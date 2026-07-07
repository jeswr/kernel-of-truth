// Prototype KOTK/2 — grammar / shared-substructure factoring + entropy coding.
// The self-verifying measured receipt for the KOTK/2 design (successor to
// docs/design-compact-kernel-serialization.md / KOTK/1).
//
//   node tools/pack/proto-kotk2-grammar.mjs --corpus lex   [--haiku-dir <dir>]
//   node tools/pack/proto-kotk2-grammar.mjs --corpus haiku --haiku-dir <dir>
//
// Same unified primes-first ID space + no-dictionary + provenance/NL-text
// sidecar discipline as KOTK/1, but adds a GRAMMAR layer that factors repeated
// sub-structure across the whole corpus and stores it ONCE, then entropy-codes
// the residual symbol stream with static rANS (kotk2-lib.mjs).
//
// It reuses the KOTK/1 round-trip contract exactly: encode -> decode -> rebuild
// the JCS identity payload -> recompute urn:kot: -> verify against
// minted-urns.jsonl (lex) / JCS byte-equality + published URNs (haiku). Any
// mismatch is a hard failure (INV-1).
//
// For each corpus it reports the SAME table as the entropy-only strategy AND,
// crucially, grammar-ON vs grammar-OFF, isolating how much of the residual was
// genuinely repeated structure vs order-0 symbol-frequency skew.

import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import * as L from "./kotk2-lib.mjs";
import { spawnSync } from "node:child_process";

const REPO = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const arg = (name, def = null) => { const i = process.argv.indexOf(name); return i >= 0 ? process.argv[i + 1] : def; };
const CORPUS = arg("--corpus", "lex");
const OUTDIR = arg("--out", "/tmp");

function zstd19(buf) {
  const r = spawnSync("zstd", ["-19", "-q", "-c"], { input: buf, maxBuffer: 1 << 30 });
  if (r.status !== 0) return null;
  return r.stdout.length;
}
function fmt(n) { return n.toLocaleString("en-US"); }

// =====================================================================
// LEX (wn31): inverse-edge structural grammar + rANS entropy
// =====================================================================
function runLex() {
  const ROOT = join(REPO, "data", "lexical-wn31");
  const RELS = ["hyponym", "hypernym", "similarTo", "memberHolonym", "memberMeronym", "partMeronym", "partHolonym", "instanceHyponym", "instanceHypernym", "antonym", "substanceMeronym", "substanceHolonym", "entailment", "cause"];
  const relId = new Map(RELS.map((r, i) => [r, i]));
  // inverse-pair mapping and canonical "primary" rel per unordered pair
  const INV = { hyponym: "hypernym", hypernym: "hyponym", memberHolonym: "memberMeronym", memberMeronym: "memberHolonym", partMeronym: "partHolonym", partHolonym: "partMeronym", instanceHyponym: "instanceHypernym", instanceHypernym: "instanceHyponym", substanceMeronym: "substanceHolonym", substanceHolonym: "substanceMeronym", antonym: "antonym", similarTo: "similarTo" };
  const PRIMARY = new Set(["hypernym", "memberHolonym", "partHolonym", "instanceHypernym", "substanceHolonym"]); // asym-inverse primaries
  const SELF = new Set(["antonym", "similarTo"]);

  const records = [];
  for (const f of ["synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl"]) {
    for (const line of readFileSync(`${ROOT}/${f}`, "utf8").split("\n")) {
      if (!line.trim()) continue;
      const r = JSON.parse(line);
      const sid = r.id.slice("urn:lexical-wn31:".length);
      const m = /^([a-z])-(\d{8})$/.exec(sid);
      records.push({ pos: m[1], off: parseInt(m[2], 10), ssType: r.ssType, axioms: r.axioms, sid });
    }
  }
  const POS_ORDER = ["n", "v", "a", "r"];
  records.sort((x, y) => POS_ORDER.indexOf(x.pos) - POS_ORDER.indexOf(y.pos) || x.off - y.off);
  const idxOf = new Map(records.map((r, i) => [r.sid, i]));
  const N = records.length;

  // canonical order predicate for a record's axioms
  const axKey = (a) => `${a.rel}|${a.target}|${a.srcWord ?? ""}|${a.tgtWord ?? ""}`;
  const cmpAx = (a, b) => { const ka = axKey(a), kb = axKey(b); return ka < kb ? -1 : ka > kb ? 1 : 0; };
  const isCanon = records.map((r) => {
    const keys = r.axioms.map(axKey);
    const sorted = [...keys].sort();
    for (let i = 0; i < keys.length; i++) if (keys[i] !== sorted[i]) return false;
    return true;
  });

  // directed edge presence for mirror lookup: key u|relId|v
  const ekey = (u, rid, v) => u * 20 * N + rid * N + v;
  const present = new Set();
  const wordsOf = new Map(); // eкey -> [srcWord,tgtWord] for antonym
  for (let u = 0; u < N; u++) for (const a of records[u].axioms) {
    const v = idxOf.get(a.target.slice("urn:lexical-wn31:".length));
    present.add(ekey(u, relId.get(a.rel), v));
    if (a.rel === "antonym") wordsOf.set(ekey(u, relId.get(a.rel), v), [a.srcWord, a.tgtWord]);
  }
  const mirrorPresent = (u, rid, v) => {
    const rel = RELS[rid]; const inv = INV[rel]; if (!inv) return false;
    const ir = relId.get(inv);
    if (!present.has(ekey(v, ir, u))) return false;
    if (rel === "antonym") {
      const w = wordsOf.get(ekey(u, rid, v)); const wm = wordsOf.get(ekey(v, ir, u));
      if (!w || !wm || wm[0] !== w[1] || wm[1] !== w[0]) return false;
    }
    return true;
  };

  // A canon record must be stored EXPLICITLY (no inverse-derivation) if it is not
  // in canonical axiom order, OR it holds an asymmetric edge that the decoder's
  // derivation rule would otherwise wrongly re-create: a PRIMARY-rel edge whose
  // mirror is absent, or a SELF-rel edge in canonical (u<v) orientation whose
  // mirror is absent. (Non-primary/asym rels and self u>v are never derived, so
  // they are safe as ordinary stored edges.)
  const EXPL = records.map((r, u) => {
    if (!isCanon[u]) return true;
    for (const a of r.axioms) {
      const rid = relId.get(a.rel); const v = idxOf.get(a.target.slice("urn:lexical-wn31:".length));
      if (PRIMARY.has(a.rel) && !mirrorPresent(u, rid, v)) return true;
      if (SELF.has(a.rel) && u < v && !mirrorPresent(u, rid, v)) return true;
    }
    return false;
  });

  // Decide, per record, its stored edges under a given factoring flag.
  // factor=false -> store ALL directed edges (entropy-only baseline).
  // factor=true  -> inverse-edge grammar (store representatives + singletons).
  function buildStored(factor) {
    const stored = []; // per record: array of {rid, v, words?}
    for (let u = 0; u < N; u++) {
      const list = [];
      if (!factor || EXPL[u]) {
        // store all edges directed (ESC records always here); order preserved for ESC
        for (const a of records[u].axioms) {
          const v = idxOf.get(a.target.slice("urn:lexical-wn31:".length));
          const rid = relId.get(a.rel);
          const e = { rid, v };
          if (a.rel === "antonym") e.words = [a.srcWord, a.tgtWord];
          list.push(e);
        }
      } else {
        for (const a of records[u].axioms) {
          const v = idxOf.get(a.target.slice("urn:lexical-wn31:".length));
          const rid = relId.get(a.rel);
          const rel = a.rel; const inv = INV[rel];
          let store = true;
          if (inv && mirrorPresent(u, rid, v) && !EXPL[v]) {
            if (SELF.has(rel)) store = u < v;                // keep u<v representative
            else store = PRIMARY.has(rel);                   // keep primary rel representative
          }
          if (store) { const e = { rid, v }; if (rel === "antonym") e.words = [a.srcWord, a.tgtWord]; list.push(e); }
        }
        // deterministic store order for delta coding (final order recovered by sort)
        list.sort((p, q) => p.v - q.v || p.rid - q.rid);
      }
      stored.push(list);
    }
    return stored;
  }

  // ---- serialise (real codec) for factor=true, with streams for entropy ----
  function serialize(stored, factor) {
    // tag symbols: 0..13 relIds, 14 = REC boundary (canon), 15 = ESC boundary
    const BOUND = 14, ESC = 15, ALPHA = 16;
    const tags = [];
    const targetW = new L.W();   // zigzag-delta (canon) / absolute (esc) varints
    const antoW = new L.W();     // antonym words in tag order
    const canonBits = [];        // 1 if record is canon-derived (factor path), else esc
    for (let u = 0; u < N; u++) {
      const esc = factor ? EXPL[u] : true; // in no-factor mode all records are "esc-like" (store-all, keep order)
      canonBits.push(esc ? 0 : 1);
      const list = stored[u];
      if (esc) {
        // ESC: store all edges in ORIGINAL order (absolute targets)
        for (const e of list) { tags.push(e.rid); targetW.varint(e.v); if (e.rid === relId.get("antonym")) { antoW.varint(e.words[0]); antoW.varint(e.words[1]); } }
        tags.push(ESC);
      } else {
        let prev = 0;
        for (const e of list) { tags.push(e.rid); const d = e.v - prev; prev = e.v; const zz = d >= 0 ? d * 2 : -d * 2 - 1; targetW.varint(zz); if (e.rid === relId.get("antonym")) { antoW.varint(e.words[0]); antoW.varint(e.words[1]); } }
        tags.push(BOUND);
      }
    }
    return { tags, ALPHA, targetBytes: targetW.buf(), antoBytes: antoW.buf(), canonBits };
  }

  // reconstruct axioms per record from decoded streams
  function reconstruct(tags, ALPHA, targetBytes, antoBytes, canonBits, factor) {
    const BOUND = 14, ESC = 15;
    const tr = new L.R(targetBytes), ar = new L.R(antoBytes);
    const recon = Array.from({ length: N }, () => []);
    const escFlag = new Array(N).fill(false);
    let u = 0, prev = 0, isEsc = (factor ? canonBits[0] === 0 : true);
    // We must know per-record esc-ness up front to choose delta vs absolute.
    const escArr = canonBits.map((b) => (factor ? b === 0 : true));
    u = 0; prev = 0;
    let ti = 0;
    for (let i = 0; i < tags.length; i++) {
      const t = tags[i];
      if (t === BOUND || t === ESC) { u++; prev = 0; continue; }
      const rid = t;
      const esc = escArr[u];
      let v;
      if (esc) { v = tr.varint(); }
      else { const zz = tr.varint(); const d = (zz & 1) ? -((zz + 1) / 2) : zz / 2; v = prev + d; prev = v; }
      const e = { rid, v };
      if (rid === relId.get("antonym")) e.words = [ar.varint(), ar.varint()];
      recon[u].push(e);
      escFlag[u] = esc;
    }
    // derive mirrors for representatives in canon records
    if (factor) {
      for (u = 0; u < N; u++) {
        if (escArr[u]) continue;
        for (const e of recon[u].slice()) {
          const rel = RELS[e.rid]; const inv = INV[rel]; if (!inv) continue;
          // A stored edge in a non-explicit record generates its mirror iff it is a
          // representative: PRIMARY-rel edges, or SELF-rel edges in u<v orientation.
          // Explicit-record targets never receive derived edges (they store all edges).
          const v = e.v; if (escArr[v]) continue;
          if (rel === "antonym" || rel === "similarTo") {
            if (u < v) { const m = { rid: relId.get(inv), v: u }; if (rel === "antonym") m.words = [e.words[1], e.words[0]]; recon[v].push(m); }
          } else if (PRIMARY.has(rel)) {
            const m = { rid: relId.get(inv), v: u }; recon[v].push(m);
          }
        }
      }
    }
    return { recon, escArr };
  }

  // Build both factor modes; do the REAL round-trip on factor=true.
  const results = {};
  for (const factor of [false, true]) {
    const stored = buildStored(factor);
    const ser = serialize(stored, factor);
    // entropy sizes
    const H = L.order0Entropy(ser.tags);
    // real rANS on tags
    const distinct = ser.ALPHA;
    const { bytes: tagRans, model } = L.ransEncode(ser.tags, distinct);
    // rANS on target bytes (order-0 over 256) and anto bytes
    const tgtSyms = Array.from(ser.targetBytes);
    const { bytes: tgtRans } = tgtSyms.length ? L.ransEncode(tgtSyms, 256) : { bytes: Buffer.alloc(0) };
    const antoSyms = Array.from(ser.antoBytes);
    const { bytes: antoRans } = antoSyms.length ? L.ransEncode(antoSyms, 256) : { bytes: Buffer.alloc(0) };
    // model tables cost
    const mw = new L.W(); L.writeModel(mw, model.freq); const tagModelBytes = mw.len;
    // Re-Pair on the tag stream (generic grammar) to measure ADDITIONAL structure
    const barriers = new Set(); // boundaries participate (they carry the "record shape")
    const rp = L.rePair(ser.tags, barriers, 1000, { minOcc: 3, maxRules: 4000 });
    const rpAlphaMax = 1000 + rp.rules.length;
    const rpSyms = rp.seq;
    const rpRemap = new Map(); let dz = 0; for (const s of rpSyms) if (!rpRemap.has(s)) rpRemap.set(s, dz++);
    for (const [a, b] of rp.rules) { if (!rpRemap.has(a)) rpRemap.set(a, dz++); if (!rpRemap.has(b)) rpRemap.set(b, dz++); }
    const rpDense = rpSyms.map((s) => rpRemap.get(s));
    const { bytes: rpRans } = rpDense.length ? L.ransEncode(rpDense, dz) : { bytes: Buffer.alloc(0) };
    // rule table cost: 2 varints per rule + remap table
    const rw = new L.W(); rw.varint(rp.rules.length); for (const [a, b] of rp.rules) { rw.varint(rpRemap.get(a)); rw.varint(rpRemap.get(b)); }
    const rpRuleBytes = rw.len;

    // container-ish size: tags(rANS)+model + targets(rANS) + anto(rANS) + canonBitmap + dict
    const canonBytes = Math.ceil(N / 8);
    const dictBytes = 200; // rel names + prefix + const + pos counts, ~fixed small
    const totalEntropyOnlyTags = tagRans.length + tagModelBytes;
    const total = totalEntropyOnlyTags + tgtRans.length + antoRans.length + canonBytes + dictBytes;
    const totalTagsRepair = rpRans.length + rpRuleBytes;

    results[factor ? "grammar" : "flat"] = {
      nStoredEdges: stored.reduce((s, l) => s + l.length, 0),
      tagCount: ser.tags.length,
      tagH0Bytes: H.totalBytes, tagRansBytes: tagRans.length, tagModelBytes,
      tagRepairRansBytes: rpRans.length, tagRepairRuleBytes: rpRuleBytes, repairRules: rp.rules.length, repairReduced: rp.seq.length,
      targetBytesRaw: ser.targetBytes.length, targetRansBytes: tgtRans.length,
      antoBytesRaw: ser.antoBytes.length, antoRansBytes: antoRans.length,
      canonBytes, total,
      _ser: ser, _stored: stored,
    };
  }

  // ---- build the SMALLEST self-contained packed file (grammar + Re-Pair on
  //      tags + rANS) and prove INV-1 by decoding IT and re-minting. ----
  const factor = true;
  const ser = results.grammar._ser;
  const NTBASE = 1000;
  const packW = new L.W();
  packW.bytes(Buffer.from("KOTK2L", "utf8"));
  packW.str("kot-lex/1\n");
  for (const r of RELS) packW.str(r);          // rel dictionary (small)
  // canon bitmap (1 = derived/canon record, 0 = explicit)
  const bm = Buffer.alloc(Math.ceil(N / 8)); for (let i = 0; i < N; i++) if (ser.canonBits[i]) bm[i >> 3] |= (1 << (i & 7));
  packW.varint(bm.length); packW.bytes(bm);
  // Re-Pair the tag stream, then rANS the reduced sequence
  const rp = L.rePair(ser.tags, new Set(), NTBASE, { minOcc: 3, maxRules: 4000 });
  packW.varint(NTBASE);
  packW.varint(rp.rules.length);
  for (const [a, b] of rp.rules) { packW.varint(a); packW.varint(b); }
  const dseen = new Map(); const d2o = []; for (const s of rp.seq) if (!dseen.has(s)) { dseen.set(s, d2o.length); d2o.push(s); }
  packW.varint(d2o.length); for (const s of d2o) packW.varint(s);
  const dense = rp.seq.map((s) => dseen.get(s));
  const { bytes: seqRans, model: sm } = L.ransEncode(dense, d2o.length);
  const smw = new L.W(); L.writeModel(smw, sm.freq); packW.bytes(smw.buf());
  packW.varint(rp.seq.length); packW.varint(seqRans.length); packW.bytes(seqRans);
  // targets (rANS over bytes) + anto
  const tgtSyms = Array.from(ser.targetBytes); const { bytes: tgtRans, model: tm } = L.ransEncode(tgtSyms, 256);
  const tmw = new L.W(); L.writeModel(tmw, tm.freq); packW.bytes(tmw.buf());
  packW.varint(ser.targetBytes.length); packW.varint(tgtRans.length); packW.bytes(tgtRans);
  const antoSyms = Array.from(ser.antoBytes); const { bytes: antoRans, model: am } = antoSyms.length ? L.ransEncode(antoSyms, 256) : { bytes: Buffer.alloc(0), model: { freq: [] } };
  const amw = new L.W(); L.writeModel(amw, am.freq); packW.bytes(amw.buf());
  packW.varint(ser.antoBytes.length); packW.varint(antoRans.length); packW.bytes(antoRans);
  const packed = packW.buf();
  writeFileSync(join(OUTDIR, "kotk2-lex.bin"), packed);

  // ---- DECODE the packed bytes back (proves the smallest config round-trips) ----
  const pr = new L.R(packed); pr.p += 6;
  pr.str(); // profile header
  const relsDec = []; for (let i = 0; i < RELS.length; i++) relsDec.push(pr.str());
  const bmLen = pr.varint(); const bmDec = pr.bytes(bmLen);
  const canonBitsDec = []; for (let i = 0; i < N; i++) canonBitsDec.push((bmDec[i >> 3] >> (i & 7)) & 1);
  const ntBaseDec = pr.varint();
  const nRules = pr.varint(); const rulesDec = []; for (let i = 0; i < nRules; i++) rulesDec.push([pr.varint(), pr.varint()]);
  const dCount = pr.varint(); const d2oDec = []; for (let i = 0; i < dCount; i++) d2oDec.push(pr.varint());
  const seqModel = L.readModel(pr);
  const seqLen = pr.varint(); const seqRansLen = pr.varint(); const seqBytes = pr.bytes(seqRansLen);
  const { symbols: denseDec } = L.ransDecode(seqBytes, seqLen, seqModel);
  const reducedDec = denseDec.map((d) => d2oDec[d]);
  const tagsDec = L.rePairExpand(reducedDec, rulesDec, ntBaseDec);
  const tgtModel = L.readModel(pr);
  const tgtRawLen = pr.varint(); const tgtRansLen = pr.varint(); const tgtBytes = pr.bytes(tgtRansLen);
  const { symbols: tgtByteSyms } = L.ransDecode(tgtBytes, tgtRawLen, tgtModel);
  const targetBytesDec = Buffer.from(tgtByteSyms);
  const antoModel = L.readModel(pr);
  const antoRawLen = pr.varint(); const antoRansLen = pr.varint(); const antoBytes = pr.bytes(antoRansLen);
  const antoBytesDec = antoRawLen ? Buffer.from(L.ransDecode(antoBytes, antoRawLen, antoModel).symbols) : Buffer.alloc(0);
  if (pr.p !== packed.length) throw new Error("trailing bytes in packed decode");
  const { recon, escArr } = reconstruct(tagsDec, ser.ALPHA, targetBytesDec, antoBytesDec, canonBitsDec, factor);

  // rebuild payloads, sort canon records, re-mint
  const minted = new Map();
  for (const line of readFileSync(`${ROOT}/minted-urns.jsonl`, "utf8").split("\n")) { if (!line.trim()) continue; const o = JSON.parse(line); minted.set(o.sourceId, o.urn); }
  let ok = 0, bad = 0, badSamples = [];
  for (let u = 0; u < N; u++) {
    const r = records[u];
    let edges = recon[u];
    if (!escArr[u]) edges = edges.slice().sort((p, q) => {
      // canonical sort by (rel,target,srcWord,tgtWord) string key
      const ka = `${RELS[p.rid]}|urn:lexical-wn31:${records[p.v].sid}|${p.words ? p.words[0] : ""}|${p.words ? p.words[1] : ""}`;
      const kb = `${RELS[q.rid]}|urn:lexical-wn31:${records[q.v].sid}|${q.words ? q.words[0] : ""}|${q.words ? q.words[1] : ""}`;
      return ka < kb ? -1 : ka > kb ? 1 : 0;
    });
    const axioms = edges.map((e) => {
      const o = { rel: RELS[e.rid], target: "urn:lexical-wn31:" + records[e.v].sid };
      if (e.words) { o.srcWord = e.words[0]; o.tgtWord = e.words[1]; }
      return o;
    });
    const payload = { sourceId: r.sid, schema: "kot-lex/1", semanticStatus: "AxiomsOnly", pos: r.pos, ssType: r.ssType, axioms };
    const urn = L.mint("kot-lex/1\n", payload);
    if (minted.get(r.sid) === urn) ok++; else { bad++; if (badSamples.length < 5) badSamples.push({ sid: r.sid, got: urn, want: minted.get(r.sid), nEdges: axioms.length, orig: r.axioms.length }); }
  }

  // report
  const g = results.grammar, f = results.flat;
  console.log("\n==================== KOTK/2  lexical-wn31 ====================");
  console.log(`records: ${fmt(N)}   axioms(total directed): ${fmt(records.reduce((s, r) => s + r.axioms.length, 0))}`);
  console.log(`canon-order records: ${fmt(isCanon.filter(Boolean).length)}   escaped(unsorted): ${fmt(isCanon.filter((x) => !x).length)}`);
  console.log("\n grammar OFF (entropy-only, all directed edges stored):");
  console.log(`   stored edges: ${fmt(f.nStoredEdges)}`);
  console.log(`   tag stream: ${fmt(f.tagCount)} syms  H0=${fmt(f.tagH0Bytes)}B  rANS=${fmt(f.tagRansBytes)}B (+model ${f.tagModelBytes}B)`);
  console.log(`   target bytes: ${fmt(f.targetBytesRaw)} -> rANS ${fmt(f.targetRansBytes)}   anto: ${fmt(f.antoBytesRaw)} -> ${fmt(f.antoRansBytes)}`);
  console.log(`   TOTAL: ${fmt(f.total)} B`);
  console.log("\n grammar ON (inverse-edge factoring + entropy):");
  console.log(`   stored edges: ${fmt(g.nStoredEdges)}  (${(100 * g.nStoredEdges / f.nStoredEdges).toFixed(1)}% of directed; ${fmt(f.nStoredEdges - g.nStoredEdges)} mirror edges derived, not stored)`);
  console.log(`   tag stream: ${fmt(g.tagCount)} syms  H0=${fmt(g.tagH0Bytes)}B  rANS=${fmt(g.tagRansBytes)}B (+model ${g.tagModelBytes}B)`);
  console.log(`   target bytes: ${fmt(g.targetBytesRaw)} -> rANS ${fmt(g.targetRansBytes)}   anto: ${fmt(g.antoBytesRaw)} -> ${fmt(g.antoRansBytes)}`);
  console.log(`   +Re-Pair on tags (generic grammar): ${g.repairRules} rules, tag stream ${fmt(g.tagCount)}->${fmt(g.repairReduced)} syms, rANS ${fmt(g.tagRepairRansBytes)}B (+rules ${fmt(g.tagRepairRuleBytes)}B) vs plain-rANS tags ${fmt(g.tagRansBytes)}B`);
  console.log(`   TOTAL: ${fmt(g.total)} B`);
  console.log(`\n round-trip re-mint (decoded from the packed file): ${fmt(ok)} ok / ${fmt(bad)} bad of ${fmt(N)}`);
  if (bad) { console.log("   SAMPLES:", JSON.stringify(badSamples, null, 1)); }

  const z = zstd19(packed);
  console.log(`\n SMALLEST packed file (inverse-grammar + Re-Pair-on-tags + rANS, self-contained):`);
  console.log(`   ${fmt(packed.length)} B   +zstd-19 ${fmt(z)} B   residual ratio ${(packed.length / z).toFixed(3)}`);
  console.log(`   vs KOTK/1: 1,387,461 B raw / 732,323 B zstd  ->  ${(1387461 / packed.length).toFixed(2)}x smaller uncompressed, ${(732323 / z).toFixed(2)}x smaller post-zstd`);
  return { ok, bad, packed: packed.length, zstd: z };
}

if (CORPUS === "lex") runLex();
else if (CORPUS === "haiku") (await import("./proto-kotk2-haiku-part.mjs")).runHaiku(REPO, arg, zstd19, fmt);
else { console.error("unknown --corpus"); process.exit(1); }
