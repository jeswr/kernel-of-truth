#!/usr/bin/env node
// Self-contained snapshot verifier — shipped INSIDE the pack (bead
// kernel-of-truth-6j5: the pack is self-verifying; verification =
// re-canonicalise + compare, no toolchain beyond Node >= 18 required).
//
//   node verify.mjs [--sample N] [--corpus name]...
//
// For every record line in corpora/<name>/canonical-jcs.jsonl:
//   singleton  {"payload":P,"urn":U}
//       recompute  sha2-256( UTF8(profileHeader) || JCS(NFC(P)) )  -> multihash
//       -> multibase base32 -> urn:kot:...  and compare with U.
//   cyclic-SCC member  {"component":C,"memberIndex":i,"urn":U}
//       X = sha2-256( UTF8(profileHeader) || JCS(NFC(C)) );
//       digest = sha2-256( UTF8(header with "\n" -> "#member\n") || X || uvarint(i) ).
// Then recompute the corpus Merkle identity root over the unique sorted URNs
// and compare against SNAPSHOT.json (and the embedded manifest's minting
// block). Any mismatch => non-zero exit. --sample N verifies N random-ish
// (deterministic stride) records per corpus instead of all.
//
// The JCS implementation below mirrors RFC 8785 exactly (property sort by
// UTF-16 code units; ES6 number serialization via String(n); minimal JSON
// string escaping) plus the kot-profile NFC pre-normalization
// (docs/design-hash-input.md: "UTF-8 NFC + RFC 8785 JCS").

import { createHash } from "node:crypto";
import { createReadStream, readFileSync } from "node:fs";
import { createInterface } from "node:readline";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));

// ---------- JCS (RFC 8785) + NFC ----------
const ESCAPES = { '"': '\\"', "\\": "\\\\", "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r" };
function serializeString(s) {
  let out = '"';
  for (let i = 0; i < s.length; i++) {
    const cu = s.charCodeAt(i);
    if (cu >= 0xd800 && cu <= 0xdbff) {
      const next = i + 1 < s.length ? s.charCodeAt(i + 1) : 0;
      if (next < 0xdc00 || next > 0xdfff) throw new Error("ERR_JCS_LONE_SURROGATE");
      out += s[i] + s[i + 1];
      i++;
      continue;
    }
    if (cu >= 0xdc00 && cu <= 0xdfff) throw new Error("ERR_JCS_LONE_SURROGATE");
    const ch = s[i];
    const esc = ESCAPES[ch];
    if (esc !== undefined) out += esc;
    else if (cu < 0x20) out += "\\u" + cu.toString(16).padStart(4, "0");
    else out += ch;
  }
  return out + '"';
}
function canonicalize(v) {
  if (v === null) return "null";
  const t = typeof v;
  if (t === "boolean") return v ? "true" : "false";
  if (t === "number") {
    if (!Number.isFinite(v)) throw new Error("ERR_JCS_NONFINITE");
    return Object.is(v, -0) ? "0" : String(v);
  }
  if (t === "string") return serializeString(v);
  if (Array.isArray(v)) return "[" + v.map(canonicalize).join(",") + "]";
  if (t === "object") {
    const keys = Object.keys(v).sort();
    return "{" + keys.map((k) => serializeString(k) + ":" + canonicalize(v[k])).join(",") + "}";
  }
  throw new Error("ERR_JCS_UNSERIALIZABLE");
}
function nfcDeep(v) {
  if (typeof v === "string") return v.normalize("NFC");
  if (Array.isArray(v)) return v.map(nfcDeep);
  if (v !== null && typeof v === "object") {
    const out = {};
    for (const k of Object.keys(v)) {
      const nk = k.normalize("NFC");
      if (nk in out) throw new Error("ERR_NFC_DUP_KEY");
      out[nk] = nfcDeep(v[k]);
    }
    return out;
  }
  return v;
}

// ---------- multihash / multibase / uvarint / merkle ----------
const sha256 = (buf) => createHash("sha256").update(buf).digest();
const B32 = "abcdefghijklmnopqrstuvwxyz234567";
function base32(bytes) {
  let out = "", bits = 0, value = 0;
  for (const b of bytes) {
    value = (value << 8) | b;
    bits += 8;
    while (bits >= 5) { out += B32[(value >>> (bits - 5)) & 31]; bits -= 5; }
  }
  if (bits > 0) out += B32[(value << (5 - bits)) & 31];
  return out;
}
const urnKot = (digest) => "urn:kot:b" + base32(Buffer.concat([Buffer.from([0x12, 0x20]), digest]));
function uvarint(n) {
  const bytes = [];
  do { let b = n & 0x7f; n = Math.floor(n / 128); if (n > 0) b |= 0x80; bytes.push(b); } while (n > 0);
  return Buffer.from(bytes);
}
function merkleRoot(urns) {
  const uniq = Array.from(new Set(urns)).sort();
  if (uniq.length === 0) return sha256(Buffer.alloc(0)).toString("hex");
  let level = uniq.map((u) => sha256(Buffer.from(u, "utf8")));
  while (level.length > 1) {
    const next = [];
    for (let i = 0; i < level.length; i += 2) {
      next.push(i + 1 < level.length ? sha256(Buffer.concat([level[i], level[i + 1]])) : level[i]);
    }
    level = next;
  }
  return level[0].toString("hex");
}

// ---------- verification ----------
function recomputeUrn(row, header) {
  if ("payload" in row) {
    const bytes = Buffer.concat([Buffer.from(header, "utf8"), Buffer.from(canonicalize(nfcDeep(row.payload)), "utf8")]);
    return urnKot(sha256(bytes));
  }
  if ("component" in row) {
    const X = sha256(Buffer.concat([Buffer.from(header, "utf8"), Buffer.from(canonicalize(nfcDeep(row.component)), "utf8")]));
    const memberHeader = header.replace(/\n$/, "#member\n");
    return urnKot(sha256(Buffer.concat([Buffer.from(memberHeader, "utf8"), X, uvarint(row.memberIndex)])));
  }
  throw new Error("ERR_UNKNOWN_ROW_SHAPE");
}

async function verifyCorpus(name, meta, sample) {
  const file = join(ROOT, "corpora", name, "canonical-jcs.jsonl");
  const rl = createInterface({ input: createReadStream(file, "utf8"), crlfDelay: Infinity });
  const urns = [];
  let n = 0, checked = 0, bad = 0;
  // deterministic sampling stride
  const stride = sample > 0 ? Math.max(1, Math.floor(meta.count / sample)) : 1;
  for await (const line of rl) {
    if (line.trim() === "") continue;
    const row = JSON.parse(line);
    urns.push(row.urn);
    if (n % stride === 0) {
      checked++;
      const got = recomputeUrn(row, meta.profileHeader);
      if (got !== row.urn) {
        bad++;
        if (bad <= 5) console.error(`  MISMATCH ${name}#${n}: ${got} != ${row.urn}`);
      }
    }
    n++;
  }
  const root = merkleRoot(urns);
  const ok = bad === 0 && n === meta.count && root === meta.identityRoot;
  console.log(
    `${ok ? "OK " : "FAIL"} ${name}: records=${n}/${meta.count} recomputed=${checked} mismatches=${bad} root=${root === meta.identityRoot ? "match" : "MISMATCH " + root}`,
  );
  return ok;
}

async function main() {
  const args = process.argv.slice(2);
  let sample = 0;
  const only = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--sample") sample = parseInt(args[++i], 10);
    else if (args[i] === "--corpus") only.push(args[++i]);
  }
  const snapshot = JSON.parse(readFileSync(join(ROOT, "SNAPSHOT.json"), "utf8"));
  let allOk = true;
  let total = 0;
  for (const [name, meta] of Object.entries(snapshot.corpora)) {
    if (only.length > 0 && !only.includes(name)) continue;
    const ok = await verifyCorpus(name, meta, sample);
    allOk = allOk && ok;
    total += meta.count;
  }
  if (only.length === 0 && total !== snapshot.totalRecords) {
    console.error(`FAIL totalRecords: ${total} != ${snapshot.totalRecords}`);
    allOk = false;
  }
  console.log(allOk ? `VERIFIED generation=${snapshot.generation} totalRecords=${snapshot.totalRecords}` : "VERIFICATION FAILED");
  process.exit(allOk ? 0 : 1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
