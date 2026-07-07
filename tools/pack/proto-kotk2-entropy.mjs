// Prototype KOTK/2 entropy-coded columnar codec for lexical-wn31 (kot-lex/1).
//   node tools/pack/proto-kotk2-entropy.mjs [--out <file>]
//
// KOTK/2 design points implemented here (vs KOTK/1, docs/design-compact-kernel-serialization.md):
//   1. UNIFIED ID SPACE, NO DICTIONARY. Concept ids are pack positions in the
//      pinned record order (pos groups n,v,a,r; ascending offset). The 65 NSM
//      primes own ids 0..64 by convention and 65..127 is reserved for
//      operators/frames/roles (see proto-kotk2-haiku.mjs); wn31 concepts start
//      at GLOBAL_BASE=128. References are stored as RELATIVE distances, so the
//      base costs zero bytes. NOTE on topological order: the wn31 axiom graph
//      is symmetric BY CONSTRUCTION (every hyponym edge has a mirror hypernym
//      edge, 269,326/269,331 mirrored) so a topological "all refs point down"
//      order cannot exist; the codec instead EXPLOITS the symmetry — see
//      mirror queue below — which recovers strictly more than topological
//      locality would.
//   2. BIT-LEVEL ENTROPY CODING. Columnar symbol streams, each coded with a
//      static rANS coder (12-bit normalized tables stored in the header).
//      rANS over canonical Huffman because several streams carry symbols with
//      p >~ 0.5 (mirror hits, ssType, chained-distance buckets) where
//      Huffman's 1-bit/symbol floor forfeits ~0.3-0.6 bits/symbol; rANS
//      reaches the fractional-bit floor with the same table overhead and
//      table-driven O(1) decode. Wide values (offset deltas, reference
//      distances) are split DEFLATE-style: entropy-coded bit-length bucket
//      symbol + raw extra bits (the low bits are ~uniform, so entropy coding
//      them buys nothing — measured).
//   3. SIDECAR DISCIPLINE unchanged from KOTK/1: wn31 identity payloads carry
//      NO natural-language text (gloss/lemmas are annotation-layer already),
//      so this pack is 100% symbolic. KOTK/1's residual zstd compressibility
//      on wn31 was therefore 100% STRUCTURAL redundancy, now removed here.
//
// Columnar streams (each an independent rANS blob + optional raw-bit blob):
//   off   : sourceId offset deltas, bucketed; table ctx = pos group (4 tables)
//   ss    : ssType flag for the 'a' group (2 symbols)
//   nax   : axioms-per-record count (direct alphabet)
//   rel   : per-axiom symbol relIdx*2+wordFlag, plus MIRROR; ctx = previous
//           symbol in the record (order-1 within record, START context)
//   dist  : reference distance bucket; value = target - prev explicit target
//           in record (chained; init = own index), zigzag; ctx = rel
//   word  : antonym srcWord/tgtWord values (direct alphabet)
//   raw   : two bit-packed extras blobs (off extras, dist extras)
//
// MIRROR QUEUE (derive-don't-store, exact + self-checking): when an explicit
// axiom (rel t>i) with a symmetric rel is coded at record i, push the implied
// inverse (invRel, src=i, words swapped) onto record t's FIFO. At record t, an
// axiom equal to the queue FRONT is coded as the 1-symbol MIRROR (~1 bit)
// instead of rel+distance(+words); front mismatch falls back to explicit
// coding, so losslessness never depends on the mirror property. Encoder and
// decoder maintain identical queues (push only on explicit forward symmetric
// axioms, pop only on MIRROR). Measured: 122,251/134,666 second-direction
// edges elided (91%).
//
// INV-1 proof, same as the v1 prototypes: encode -> decode -> rebuild JCS
// identity payloads -> recompute urn:kot: -> verify ALL records against
// minted-urns.jsonl. Any mismatch is a hard failure (exit 1).
import { readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const REPO = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const ROOT = join(REPO, "data", "lexical-wn31");
const OUT = (() => { const i = process.argv.indexOf("--out"); return i >= 0 ? process.argv[i + 1] : null; })();

// ---------- shared helpers (identical semantics to proto-kotk1-lex.mjs) ----------
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
function mint(profileHeader, payload) {
  const d = createHash("sha256").update(Buffer.concat([Buffer.from(profileHeader, "utf8"), Buffer.from(jcs(payload), "utf8")])).digest();
  return "urn:kot:b" + base32(Buffer.concat([Buffer.from([0x12, 0x20]), d]));
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
  varint() { let m = 1, v = 0; for (;;) { const b = this.b[this.p++]; v += (b & 0x7f) * m; if (!(b & 0x80)) return v; m *= 128; } }
  str() { const n = this.varint(); const s = this.b.toString("utf8", this.p, this.p + n); this.p += n; return s; }
  raw(n) { const b = this.b.subarray(this.p, this.p + n); this.p += n; return b; }
}

// ---------- rANS (static, byte-renormalized, 12-bit precision) ----------
const PB = 12, MTOT = 1 << PB, RANS_L = 1 << 23;
function normalizeFreqs(counts) { // counts: array (0 = absent) -> freqs summing to MTOT, present >= 1
  const n = counts.reduce((a, b) => a + b, 0);
  if (n === 0) return counts.map(() => 0);
  const freqs = counts.map(c => c === 0 ? 0 : Math.max(1, Math.round(c / n * MTOT)));
  let sum = freqs.reduce((a, b) => a + b, 0);
  // fix rounding drift against the largest bins (never dropping a present symbol to 0)
  while (sum !== MTOT) {
    const dir = sum > MTOT ? -1 : 1;
    let best = -1;
    for (let i = 0; i < freqs.length; i++) {
      if (freqs[i] === 0) continue;
      if (dir === -1 && freqs[i] <= 1) continue;
      if (best < 0 || freqs[i] > freqs[best]) best = i;
    }
    freqs[best] += dir; sum += dir;
  }
  return freqs;
}
class Table {
  constructor(freqs) {
    this.freq = freqs;
    this.cum = new Array(freqs.length + 1).fill(0);
    for (let i = 0; i < freqs.length; i++) this.cum[i + 1] = this.cum[i] + freqs[i];
    this.lookup = new Uint16Array(MTOT);
    for (let s = 0; s < freqs.length; s++) for (let j = this.cum[s]; j < this.cum[s + 1]; j++) this.lookup[j] = s;
  }
}
function ransEncode(pairs) { // pairs: [table, symbol][] in DECODE order; returns Buffer
  let x = RANS_L;
  const out = [];
  for (let i = pairs.length - 1; i >= 0; i--) {
    const [t, s] = pairs[i];
    const f = t.freq[s];
    if (!f) throw new Error("zero-freq symbol " + s);
    const xmax = f * (1 << 19); // ((L>>PB)<<8)*f with L=2^23, PB=12
    while (x >= xmax) { out.push(x % 256); x = Math.floor(x / 256); }
    x = Math.floor(x / f) * MTOT + (x % f) + t.cum[s];
  }
  const head = Buffer.from([Math.floor(x / 0x1000000) & 0xff, (x >>> 16) & 0xff, (x >>> 8) & 0xff, x & 0xff]);
  out.reverse();
  return Buffer.concat([head, Buffer.from(out)]);
}
class RansDecoder {
  constructor(buf) {
    this.b = buf;
    this.x = buf[0] * 0x1000000 + buf[1] * 0x10000 + buf[2] * 0x100 + buf[3];
    this.p = 4;
  }
  decode(t) {
    const slot = this.x % MTOT;
    const s = t.lookup[slot];
    this.x = t.freq[s] * Math.floor(this.x / MTOT) + slot - t.cum[s];
    while (this.x < RANS_L) this.x = this.x * 256 + this.b[this.p++];
    return s;
  }
}
// raw-bit blobs (MSB-first)
class BitW {
  constructor() { this.bytes = []; this.cur = 0; this.n = 0; this.total = 0; }
  put(v, nbits) { for (let i = nbits - 1; i >= 0; i--) { this.cur = (this.cur << 1) | ((v >>> i) & 1); if (++this.n === 8) { this.bytes.push(this.cur); this.cur = 0; this.n = 0; } } this.total += nbits; }
  buf() { const bs = this.bytes.slice(); if (this.n) bs.push(this.cur << (8 - this.n)); return Buffer.from(bs); }
}
class BitR {
  constructor(buf) { this.b = buf; this.p = 0; this.n = 0; this.cur = 0; }
  get(nbits) { let v = 0; for (let i = 0; i < nbits; i++) { if (this.n === 0) { this.cur = this.b[this.p++]; this.n = 8; } v = (v << 1) | ((this.cur >>> 7) & 1); this.cur = (this.cur << 1) & 0xff; this.n--; } return v; }
}
const zig = d => d >= 0 ? 2 * d : -2 * d - 1;
const unzig = z => (z % 2 === 0) ? z / 2 : -(z + 1) / 2;
const blen = v => v === 0 ? 0 : 32 - Math.clz32(v);
// bucket split: value v>=0 -> (symbol b=blen(v), extras = v - 2^(b-1) in b-1 bits for b>=2)
function bucketExtras(v, b) { return b >= 2 ? v - (1 << (b - 1)) : 0; }
function unbucket(b, extras) { return b === 0 ? 0 : b === 1 ? 1 : (1 << (b - 1)) + extras; }

// ---------- load corpus (identical to v1) ----------
const RELS = ["hyponym","hypernym","similarTo","memberHolonym","memberMeronym","partMeronym","partHolonym","instanceHyponym","instanceHypernym","antonym","substanceMeronym","substanceHolonym","entailment","cause"];
const relId = new Map(RELS.map((r, i) => [r, i]));
const INV_REL = [1,0,2,4,3,6,5,8,7,9,11,10,-1,-1]; // index-mapped inverse; -1 = not symmetric (entailment, cause)
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
const POS_ORDER = ["n", "v", "a", "r"];
records.sort((x, y) => POS_ORDER.indexOf(x.pos) - POS_ORDER.indexOf(y.pos) || x.off - y.off);
const idxOf = new Map(records.map((r, i) => [r.sid, i]));
const N = records.length;

// ---------- forward pass: emit symbol streams ----------
// rel-stream alphabet: relIdx*2 + wordFlag (0..27), MIRROR = 28; contexts = prev symbol (29) + START
const MIRROR = 28, REL_AB = 29, REL_CTX = 30, START_CTX = 29;
const relCounts = Array.from({ length: REL_CTX }, () => new Array(REL_AB).fill(0));
const distCounts = Array.from({ length: RELS.length }, () => new Array(40).fill(0));
const offCounts = Array.from({ length: 4 }, () => new Array(40).fill(0));
const ssCounts = [new Array(2).fill(0)];
let maxNax = 0; for (const r of records) maxNax = Math.max(maxNax, r.axioms.length);
const naxCounts = [new Array(maxNax + 1).fill(0)];
let maxWord = 0; for (const r of records) for (const a of r.axioms) if ("srcWord" in a) maxWord = Math.max(maxWord, a.srcWord, a.tgtWord);
const wordCounts = [new Array(maxWord + 1).fill(0)];

// two passes over identical emission logic: pass 1 tallies, pass 2 codes
function emitAll(sink) {
  // sink: {off(pos,sym,extras,nbits), ss(sym), nax(sym), rel(ctx,sym), dist(rel,sym,extras,nbits), word(sym)}
  const pending = new Map(); // target idx -> FIFO [{rel, src, hasW, srcWord, tgtWord}], qi pointer
  const prevOff = { n: 0, v: 0, a: 0, r: 0 };
  for (let i = 0; i < N; i++) {
    const r = records[i];
    const d = r.off - prevOff[r.pos]; prevOff[r.pos] = r.off;
    { const b = blen(d); sink.off(POS_ORDER.indexOf(r.pos), b, bucketExtras(d, b), Math.max(0, b - 1)); }
    if (r.pos === "a") sink.ss(r.ssType === "s" ? 1 : 0);
    sink.nax(r.axioms.length);
    const q = pending.get(i); let qi = q ? q.qi : 0;
    let prevT = i, ctx = START_CTX;
    for (const a of r.axioms) {
      const hasW = "srcWord" in a;
      const t = idxOf.get(a.target.slice("urn:lexical-wn31:".length));
      if (t === undefined) throw new Error("dangling " + a.target);
      const front = q && qi < q.list.length ? q.list[qi] : null;
      if (front && front.rel === a.rel && front.src === t && front.hasW === hasW &&
          (!hasW || (front.srcWord === a.srcWord && front.tgtWord === a.tgtWord))) {
        sink.rel(ctx, MIRROR); qi++; ctx = MIRROR;
        continue;
      }
      const ri = relId.get(a.rel);
      const sym = ri * 2 + (hasW ? 1 : 0);
      sink.rel(ctx, sym); ctx = sym;
      const z = zig(t - prevT); prevT = t;
      const b = blen(z);
      sink.dist(ri, b, bucketExtras(z, b), Math.max(0, b - 1));
      if (hasW) { sink.word(a.srcWord); sink.word(a.tgtWord); }
      const inv = INV_REL[ri];
      if (inv >= 0 && t > i) {
        if (!pending.has(t)) pending.set(t, { list: [], qi: 0 });
        pending.get(t).list.push({ rel: RELS[inv], src: i, hasW, srcWord: hasW ? a.tgtWord : undefined, tgtWord: hasW ? a.srcWord : undefined });
      }
    }
  }
}
emitAll({
  off: (p, s) => offCounts[p][s]++,
  ss: s => ssCounts[0][s]++,
  nax: s => naxCounts[0][s]++,
  rel: (c, s) => relCounts[c][s]++,
  dist: (rel, s) => distCounts[rel][s]++,
  word: s => wordCounts[0][s]++,
});
function trim(arr) { let n = arr.length; while (n > 0 && arr[n - 1] === 0) n--; return arr.slice(0, n); }
const tablesSpec = { off: offCounts.map(trim), ss: ssCounts.map(trim), nax: naxCounts.map(trim), rel: relCounts.map(trim), dist: distCounts.map(trim), word: wordCounts.map(trim) };
const tables = {};
for (const k of Object.keys(tablesSpec)) tables[k] = tablesSpec[k].map(counts => counts.length ? new Table(normalizeFreqs(counts)) : null);

// pass 2: collect (table, symbol) pair lists per stream + raw bits
const pairs = { off: [], ss: [], nax: [], rel: [], dist: [], word: [] };
const offBits = new BitW(), distBits = new BitW();
emitAll({
  off: (p, s, extras, nb) => { pairs.off.push([tables.off[p], s]); if (nb) offBits.put(extras, nb); },
  ss: s => pairs.ss.push([tables.ss[0], s]),
  nax: s => pairs.nax.push([tables.nax[0], s]),
  rel: (c, s) => pairs.rel.push([tables.rel[c], s]),
  dist: (rel, s, extras, nb) => { pairs.dist.push([tables.dist[rel], s]); if (nb) distBits.put(extras, nb); },
  word: s => pairs.word.push([tables.word[0], s]),
});
const blobs = {};
for (const k of Object.keys(pairs)) blobs[k] = ransEncode(pairs[k]);
const rawOff = offBits.buf(), rawDist = distBits.buf();

// ---------- container ----------
const w = new W();
w.bytes(Buffer.from("KOTK2", "utf8"));
w.str("kot-lex/1\n");
w.str("urn:lexical-wn31:");
w.str(JSON.stringify({ schema: "kot-lex/1", semanticStatus: "AxiomsOnly" }));
w.varint(RELS.length); for (const r of RELS) w.str(r);
w.varint(POS_ORDER.length);
for (const p of POS_ORDER) { w.str(p); w.varint(records.filter(r => r.pos === p).length); }
let tableBytesStart = w.len;
const STREAMS = ["off", "ss", "nax", "rel", "dist", "word"];
for (const k of STREAMS) {
  w.varint(tables[k].length);
  for (const t of tables[k]) {
    if (!t) { w.varint(0); continue; }
    w.varint(t.freq.length);
    for (const f of t.freq) w.varint(f);
  }
}
const tableBytes = w.len - tableBytesStart;
for (const k of STREAMS) { w.varint(blobs[k].length); w.bytes(blobs[k]); }
w.varint(offBits.total); w.bytes(rawOff);
w.varint(distBits.total); w.bytes(rawDist);
const packed = w.buf();
if (OUT) writeFileSync(OUT, packed);

// ---------- decode (from packed bytes alone) ----------
const rr = new R(packed);
rr.p += 5;
const profile = rr.str();
const prefix = rr.str();
const consts = JSON.parse(rr.str());
const nRels = rr.varint(); const rels = []; for (let i = 0; i < nRels; i++) rels.push(rr.str());
const dInv = rels.map(r => { const m = { hyponym:"hypernym",hypernym:"hyponym",memberHolonym:"memberMeronym",memberMeronym:"memberHolonym",partMeronym:"partHolonym",partHolonym:"partMeronym",instanceHyponym:"instanceHypernym",instanceHypernym:"instanceHyponym",substanceMeronym:"substanceHolonym",substanceHolonym:"substanceMeronym",similarTo:"similarTo",antonym:"antonym" }[r]; return m ? rels.indexOf(m) : -1; });
const nPos = rr.varint(); const groups = [];
for (let i = 0; i < nPos; i++) { const p = rr.str(); const c = rr.varint(); groups.push([p, c]); }
const dTables = {};
for (const k of STREAMS) {
  const nt = rr.varint(); dTables[k] = [];
  for (let i = 0; i < nt; i++) {
    const ab = rr.varint();
    if (ab === 0) { dTables[k].push(null); continue; }
    const freqs = []; for (let j = 0; j < ab; j++) freqs.push(rr.varint());
    dTables[k].push(new Table(freqs));
  }
}
const dBlobs = {};
for (const k of STREAMS) { const n = rr.varint(); dBlobs[k] = new RansDecoder(rr.raw(n)); }
const nOffBits = rr.varint(); const dRawOff = new BitR(rr.raw(Math.ceil(nOffBits / 8)));
const nDistBits = rr.varint(); const dRawDist = new BitR(rr.raw(Math.ceil(nDistBits / 8)));
if (rr.p !== packed.length) throw new Error("trailing bytes");

// grammar-driven decode: mirrors the emit logic exactly
const total = groups.reduce((a, [, c]) => a + c, 0);
const rows = []; const sids = new Array(total);
{
  const pending = new Map();
  let gi = 0, left = 0, pos = null, prevOff = 0, posIdx = -1;
  for (let i = 0; i < total; i++) {
    while (left === 0) { [pos, left] = groups[gi]; posIdx = gi; gi++; prevOff = 0; }
    left--;
    const b = dBlobs.off.decode(dTables.off[posIdx]);
    const extras = b >= 2 ? dRawOff.get(b - 1) : 0;
    prevOff += unbucket(b, extras);
    const sid = `${pos}-${String(prevOff).padStart(8, "0")}`;
    sids[i] = sid;
    let ssType = pos;
    if (pos === "a") ssType = dBlobs.ss.decode(dTables.ss[0]) === 1 ? "s" : "a";
    const nax = dBlobs.nax.decode(dTables.nax[0]);
    const q = pending.get(i); let qi = 0;
    let prevT = i, ctx = START_CTX;
    const axioms = [];
    for (let j = 0; j < nax; j++) {
      const sym = dBlobs.rel.decode(dTables.rel[ctx]);
      ctx = sym;
      if (sym === MIRROR) {
        const front = q.list[qi++];
        const ax = { rel: front.rel, ti: front.src };
        if (front.hasW) { ax.srcWord = front.srcWord; ax.tgtWord = front.tgtWord; }
        axioms.push(ax);
        continue;
      }
      const ri = sym >> 1, hasW = (sym & 1) === 1;
      const db = dBlobs.dist.decode(dTables.dist[ri]);
      const dext = db >= 2 ? dRawDist.get(db - 1) : 0;
      const t = prevT + unzig(unbucket(db, dext)); prevT = t;
      const ax = { rel: rels[ri], ti: t };
      if (hasW) { ax.srcWord = dBlobs.word.decode(dTables.word[0]); ax.tgtWord = dBlobs.word.decode(dTables.word[0]); }
      axioms.push(ax);
      const inv = dInv[ri];
      if (inv >= 0 && t > i) {
        if (!pending.has(t)) pending.set(t, { list: [] });
        pending.get(t).list.push({ rel: rels[inv], src: i, hasW, srcWord: hasW ? ax.tgtWord : undefined, tgtWord: hasW ? ax.srcWord : undefined });
      }
    }
    rows.push({ sid, ssType, pos, axioms });
  }
}

// ---------- rebuild payloads + verify against minted URNs ----------
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
console.log("packed bytes:", packed.length, "(", (packed.length / N).toFixed(2), "B/record )");
console.log("hash verify: ok", ok, "bad", bad, "of", rows.length);
if (bad > 0) { console.error("ERR_KOTK2_ROUNDTRIP: URN mismatches"); process.exit(1); }
const root = createHash("sha256");
for (const u of digests) root.update(u);
console.log("identityRoot(sha256 over urns, pack order):", root.digest("hex"));

// ---------- per-stream report ----------
console.log("\nper-stream report (rANS blob incl 4B state; naive = fixed-width symbols):");
const symCount = { off: pairs.off.length, ss: pairs.ss.length, nax: pairs.nax.length, rel: pairs.rel.length, dist: pairs.dist.length, word: pairs.word.length };
let blobTotal = 0;
for (const k of STREAMS) {
  const n = symCount[k]; if (!n) continue;
  const bits = blobs[k].length * 8;
  const ab = Math.max(...tables[k].filter(Boolean).map(t => t.freq.length));
  const naive = Math.ceil(Math.log2(Math.max(2, ab)));
  console.log(`  ${k.padEnd(5)} n=${String(n).padStart(7)}  ${(bits / n).toFixed(3)} b/sym (naive ${naive} b/sym, alphabet ${ab})  blob ${blobs[k].length} B`);
  blobTotal += blobs[k].length;
}
console.log(`  raw extras: off ${rawOff.length} B (${(offBits.total / symCount.off).toFixed(2)} b/rec), dist ${rawDist.length} B (${(distBits.total / symCount.dist).toFixed(2)} b/explicit-ref)`);
console.log(`  entropy tables: ${tableBytes} B; header+dicts: ${tableBytesStart} B; blobs ${blobTotal} B; raws ${rawOff.length + rawDist.length} B`);
const mirrorN = pairs.rel.filter(([, s]) => s === MIRROR).length;
console.log(`  mirror-elided axioms: ${mirrorN} of ${pairs.rel.length} (explicit refs: ${symCount.dist})`);
