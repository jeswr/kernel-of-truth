// Prototype KOTK/1 codec 1 (kot-lex/1) for lexical-wn31 — the measured receipt
// behind docs/design-compact-kernel-serialization.md s9(b)/s12.
//   node tools/pack/proto-kotk1-lex.mjs [--out <file>]
// encode -> decode -> rebuild JCS identity payloads -> recompute urn:kot: ->
// verify ALL records against minted-urns.jsonl. Any mismatch is a hard failure.
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const REPO = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const ROOT = join(REPO, "data", "lexical-wn31");
const OUT = (() => { const i = process.argv.indexOf("--out"); return i >= 0 ? process.argv[i + 1] : null; })();

// ---------- shared helpers ----------
function jcs(v) {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return "[" + v.map(jcs).join(",") + "]";
  return "{" + Object.keys(v).sort().map(k => JSON.stringify(k) + ":" + jcs(v[k])).join(",") + "}";
}
const B32 = "abcdefghijklmnopqrstuvwxyz234567";
function base32(bytes) {
  let out = "", bits = 0, val = 0;
  for (const b of bytes) { val = (val << 8) | b; bits += 8; while (bits >= 5) { out += B32[(val >>> (bits - 5)) & 31]; bits -= 5; } }
  if (bits > 0) out += B32[(val << (5 - bits)) & 31];
  return out;
}
function urnKot(digest) {
  const mh = Buffer.concat([Buffer.from([0x12, 0x20]), digest]);
  return "urn:kot:b" + base32(mh);
}
function mint(profileHeader, payload) {
  const d = createHash("sha256").update(Buffer.concat([Buffer.from(profileHeader, "utf8"), Buffer.from(jcs(payload), "utf8")])).digest();
  return urnKot(d);
}
class W {
  constructor() { this.chunks = []; this.len = 0; }
  byte(b) { this.chunks.push(Buffer.from([b])); this.len += 1; }
  varint(n) { const bs = []; let v = n; do { let b = v & 0x7f; v = Math.floor(v / 128); if (v > 0) b |= 0x80; bs.push(b); } while (v > 0); this.chunks.push(Buffer.from(bs)); this.len += bs.length; }
  bytes(buf) { this.chunks.push(buf); this.len += buf.length; }
  str(s) { const b = Buffer.from(s.normalize("NFC"), "utf8"); this.varint(b.length); this.bytes(b); }
  buf() { return Buffer.concat(this.chunks); }
}
class R {
  constructor(buf) { this.b = buf; this.p = 0; }
  byte() { return this.b[this.p++]; }
  varint() { let shift = 1, v = 0; for (;;) { const b = this.b[this.p++]; v += (b & 0x7f) * shift; if (!(b & 0x80)) return v; shift *= 128; } }
  str() { const n = this.varint(); const s = this.b.toString("utf8", this.p, this.p + n); this.p += n; return s; }
}

// ---------- load ----------
const RELS = ["hyponym","hypernym","similarTo","memberHolonym","memberMeronym","partMeronym","partHolonym","instanceHyponym","instanceHypernym","antonym","substanceMeronym","substanceHolonym","entailment","cause"];
const relId = new Map(RELS.map((r, i) => [r, i]));
const records = [];
for (const f of ["synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl"]) {
  for (const line of readFileSync(`${ROOT}/${f}`, "utf8").split("\n")) {
    if (!line.trim()) continue;
    const r = JSON.parse(line);
    const sid = r.id.slice("urn:lexical-wn31:".length);
    const m = /^([a-z])-(\d{8})$/.exec(sid);
    if (!m) throw new Error("bad sid " + sid);
    if (r.pos !== (r.ssType === "s" ? "a" : r.ssType)) throw new Error("pos!=f(ssType) " + sid);
    if (r.schema !== "kot-lex/1" || r.semanticStatus !== "AxiomsOnly") throw new Error("dict miss");
    records.push({ pos: m[1], off: parseInt(m[2], 10), ssType: r.ssType, axioms: r.axioms, sid });
  }
}
// pack order: pos groups in fixed order, ascending offset
const POS_ORDER = ["n", "v", "a", "r"];
records.sort((x, y) => POS_ORDER.indexOf(x.pos) - POS_ORDER.indexOf(y.pos) || x.off - y.off);
const idxOf = new Map(records.map((r, i) => [r.sid, i]));

// ---------- encode ----------
const w = new W();
w.bytes(Buffer.from("KOTK1", "utf8"));
w.str("kot-lex/1\n");                    // profile header
w.str("urn:lexical-wn31:");              // placeholder prefix (stable ref mode)
w.str(JSON.stringify({ schema: "kot-lex/1", semanticStatus: "AxiomsOnly" })); // record-constant dict
w.varint(RELS.length); for (const r of RELS) w.str(r);
w.varint(POS_ORDER.length);
for (const p of POS_ORDER) {
  w.str(p);
  w.varint(records.filter(r => r.pos === p).length);
}
for (const p of POS_ORDER) {
  let prev = 0;
  for (const r of records) {
    if (r.pos !== p) continue;
    w.varint(r.off - prev); prev = r.off;
    if (p === "a") w.byte(r.ssType === "s" ? 1 : 0);
    w.varint(r.axioms.length);
    for (const a of r.axioms) {
      const extra = "srcWord" in a;
      w.byte(relId.get(a.rel) | (extra ? 0x80 : 0));
      const tsid = a.target.slice("urn:lexical-wn31:".length);
      const ti = idxOf.get(tsid);
      if (ti === undefined) throw new Error("dangling target " + a.target);
      w.varint(ti);
      if (extra) { w.varint(a.srcWord); w.varint(a.tgtWord); }
    }
  }
}
const packed = w.buf();
if (OUT) writeFileSync(OUT, packed);
console.log("packed bytes:", packed.length, "(", (packed.length / records.length).toFixed(1), "B/record )");

// ---------- decode ----------
const r0 = new R(packed);
r0.p += 5;
const profile = r0.str();
const prefix = r0.str();
const consts = JSON.parse(r0.str());
const nRels = r0.varint(); const rels = []; for (let i = 0; i < nRels; i++) rels.push(r0.str());
const nPos = r0.varint(); const groups = [];
for (let i = 0; i < nPos; i++) { const p = r0.str(); const c = r0.varint(); groups.push([p, c]); }
// first pass builds the sid table implicitly while reading; we must read
// sequentially, so decode raw rows first, then resolve targets.
const rows = []; const sids = [];
for (const [p, count] of groups) {
  let prev = 0;
  for (let i = 0; i < count; i++) {
    prev += r0.varint();
    let ssType = p;
    if (p === "a") ssType = r0.byte() === 1 ? "s" : "a";
    const na = r0.varint();
    const axioms = [];
    for (let j = 0; j < na; j++) {
      const t = r0.byte();
      const rel = rels[t & 0x7f];
      const ti = r0.varint();
      if (t & 0x80) { const srcWord = r0.varint(); const tgtWord = r0.varint(); axioms.push({ rel, ti, srcWord, tgtWord }); }
      else axioms.push({ rel, ti });
    }
    const sid = `${p}-${String(prev).padStart(8, "0")}`;
    sids.push(sid);
    rows.push({ sid, ssType, pos: p, axioms });
  }
}
if (r0.p !== packed.length) throw new Error("trailing bytes");

// ---------- rebuild payloads + verify ----------
const minted = new Map();
for (const line of readFileSync(`${ROOT}/minted-urns.jsonl`, "utf8").split("\n")) {
  if (!line.trim()) continue;
  const o = JSON.parse(line);
  minted.set(o.sourceId, o.urn);
}
let ok = 0, bad = 0;
const digests = [];
for (const row of rows) {
  const payload = {
    sourceId: row.sid, schema: consts.schema, semanticStatus: consts.semanticStatus,
    pos: row.pos, ssType: row.ssType,
    axioms: row.axioms.map(a => {
      const o = { rel: a.rel, target: prefix + sids[a.ti] };
      if ("srcWord" in a) { o.srcWord = a.srcWord; o.tgtWord = a.tgtWord; }
      return o;
    }),
  };
  const urn = mint(profile, payload);
  if (minted.get(row.sid) === urn) ok++; else { bad++; if (bad < 4) console.log("MISMATCH", row.sid, urn, minted.get(row.sid)); }
  digests.push(urn);
}
console.log("hash verify: ok", ok, "bad", bad, "of", rows.length);
if (bad > 0) { console.error("ERR_KOTK1_ROUNDTRIP: URN mismatches"); process.exit(1); }
// Merkle-ish root over the urns in pack order (spec: root over raw digests)
const root = createHash("sha256");
for (const u of digests) root.update(u);
console.log("identityRoot(sha256 over urns, pack order):", root.digest("hex"));
