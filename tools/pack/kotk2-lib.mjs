// KOTK/2 shared codec library: canonical hashing helpers, a static order-0
// rANS entropy coder (near-entropy-floor), a Re-Pair grammar factorizer, and
// order-0 entropy analytics. Used by tools/pack/proto-kotk2-grammar.mjs.
//
// Design notes (justification):
//  - rANS over Huffman: the symbol streams here have highly skewed
//    distributions (a handful of primes / structural tags dominate). Huffman
//    pays up to ~1 bit/symbol of code-length rounding, which is material when
//    the top symbol has p>0.3 (ideal < 1.7 bits but Huffman spends >=1 whole
//    bit). Static rANS reaches within a fraction of a percent of the order-0
//    entropy H0 with a single stored frequency table, and decodes forward in a
//    single pass. We measure the achieved bytes AND report H0 so the gap to the
//    floor is visible.
//  - The frequency table is quantised to a total of M = 1<<14 and stored in the
//    container; its bytes are counted in every size we report (no free lunch).

import { createHash } from "node:crypto";

// ---------- canonical hashing (identical to the KOTK/1 prototypes) ----------
export function jcs(v) {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return "[" + v.map(jcs).join(",") + "]";
  return "{" + Object.keys(v).sort().map((k) => JSON.stringify(k) + ":" + jcs(v[k])).join(",") + "}";
}
export function nfcDeep(v) {
  if (typeof v === "string") return v.normalize("NFC");
  if (Array.isArray(v)) return v.map(nfcDeep);
  if (v !== null && typeof v === "object") { const o = {}; for (const k of Object.keys(v)) o[k.normalize("NFC")] = nfcDeep(v[k]); return o; }
  return v;
}
const B32 = "abcdefghijklmnopqrstuvwxyz234567";
function base32(bytes) { let out = "", bits = 0, val = 0; for (const b of bytes) { val = (val << 8) | b; bits += 8; while (bits >= 5) { out += B32[(val >>> (bits - 5)) & 31]; bits -= 5; } } if (bits > 0) out += B32[(val << (5 - bits)) & 31]; return out; }
export function mint(header, payload) {
  const d = createHash("sha256").update(Buffer.concat([Buffer.from(header, "utf8"), Buffer.from(jcs(payload), "utf8")])).digest();
  return "urn:kot:b" + base32(Buffer.concat([Buffer.from([0x12, 0x20]), d]));
}

// ---------- byte writer/reader with LEB128 varints ----------
export class W {
  constructor() { this.chunks = []; this.len = 0; }
  byte(b) { this.chunks.push(Buffer.from([b & 0xff])); this.len += 1; }
  varint(n) { const bs = []; let v = n; do { let b = v & 0x7f; v = Math.floor(v / 128); if (v > 0) b |= 0x80; bs.push(b); } while (v > 0); this.chunks.push(Buffer.from(bs)); this.len += bs.length; }
  bytes(buf) { this.chunks.push(buf); this.len += buf.length; }
  str(s) { const b = Buffer.from(s.normalize("NFC"), "utf8"); this.varint(b.length); this.bytes(b); }
  buf() { return Buffer.concat(this.chunks); }
}
export class R {
  constructor(buf) { this.b = buf; this.p = 0; }
  byte() { return this.b[this.p++]; }
  varint() { let m = 1, v = 0; for (;;) { const b = this.b[this.p++]; v += (b & 0x7f) * m; if (!(b & 0x80)) return v; m *= 128; } }
  str() { const n = this.varint(); const s = this.b.toString("utf8", this.p, this.p + n); this.p += n; return s; }
  bytes(n) { const s = this.b.subarray(this.p, this.p + n); this.p += n; return s; }
}

// ---------- order-0 entropy of an int symbol array (bits) ----------
export function order0Entropy(symbols) {
  const freq = new Map();
  for (const s of symbols) freq.set(s, (freq.get(s) || 0) + 1);
  const n = symbols.length; let H = 0;
  for (const c of freq.values()) { const p = c / n; H -= p * Math.log2(p); }
  return { bitsPerSymbol: H, totalBytes: Math.ceil((H * n) / 8), distinct: freq.size, n };
}

// ---------- static order-0 rANS (32-bit state, byte renorm, M = 1<<14) ----------
const RANS_SCALE_BITS = 14;
const RANS_M = 1 << RANS_SCALE_BITS;
const RANS_L = 1 << 16; // lower bound of normalised state

// Build a quantised frequency model over dense symbols 0..A-1.
// Returns {freq, cum, total:M, slot2sym}. Guarantees every observed symbol has freq>=1.
function buildModel(symbols, A) {
  const raw = new Array(A).fill(0);
  for (const s of symbols) raw[s]++;
  const n = symbols.length;
  const freq = new Array(A).fill(0);
  let used = 0;
  for (let s = 0; s < A; s++) {
    if (raw[s] === 0) continue;
    let f = Math.round((raw[s] / n) * RANS_M);
    if (f === 0) f = 1;
    freq[s] = f; used += f;
  }
  // fix rounding so sum == M, adjusting the largest bucket(s)
  let diff = RANS_M - used;
  // sort symbol indices by freq desc for stable large-bucket adjustment
  const order = [];
  for (let s = 0; s < A; s++) if (freq[s] > 0) order.push(s);
  order.sort((a, b) => freq[b] - freq[a]);
  let oi = 0;
  while (diff !== 0) {
    const s = order[oi % order.length];
    if (diff > 0) { freq[s]++; diff--; }
    else if (freq[s] > 1) { freq[s]--; diff++; }
    oi++;
  }
  const cum = new Array(A + 1).fill(0);
  for (let s = 0; s < A; s++) cum[s + 1] = cum[s] + freq[s];
  const slot2sym = new Uint16Array(RANS_M);
  for (let s = 0; s < A; s++) for (let i = cum[s]; i < cum[s + 1]; i++) slot2sym[i] = s;
  return { freq, cum, slot2sym };
}

// Encode dense-symbol array -> Buffer (model bytes NOT included; caller stores freq table).
export function ransEncode(symbols, A) {
  const model = buildModel(symbols, A);
  const { freq, cum } = model;
  const out = []; // bytes emitted during renorm (in reverse of final order)
  let x = RANS_L;
  for (let i = symbols.length - 1; i >= 0; i--) {
    const s = symbols[i];
    const f = freq[s];
    const xMax = ((RANS_L >>> RANS_SCALE_BITS) << 8) * f; // = (RANS_L/M)*256*f
    while (x >= xMax) { out.push(x & 0xff); x = Math.floor(x / 256); }
    x = Math.floor(x / f) * RANS_M + (x % f) + cum[s];
  }
  // flush state (4 bytes)
  out.push(x & 0xff); out.push((x >>> 8) & 0xff); out.push((x >>> 16) & 0xff); out.push((x >>> 24) & 0xff);
  out.reverse();
  return { bytes: Buffer.from(out), model };
}

// Decode n symbols from Buffer given the model.
export function ransDecode(buf, n, model) {
  const { freq, cum, slot2sym } = model;
  let p = 0;
  let x = (buf[p] << 24) | (buf[p + 1] << 16) | (buf[p + 2] << 8) | buf[p + 3];
  x = x >>> 0; p += 4;
  const out = new Array(n);
  for (let i = 0; i < n; i++) {
    const slot = x & (RANS_M - 1);
    const s = slot2sym[slot];
    out[i] = s;
    x = freq[s] * Math.floor(x / RANS_M) + slot - cum[s];
    while (x < RANS_L) { x = x * 256 + buf[p++]; }
  }
  return { symbols: out, bytesRead: p };
}

// Serialise a model's freq table compactly (varint run of A, then freqs).
export function writeModel(w, freq) {
  w.varint(freq.length);
  for (const f of freq) w.varint(f);
}
export function readModel(r) {
  const A = r.varint();
  const freq = new Array(A);
  for (let s = 0; s < A; s++) freq[s] = r.varint();
  const cum = new Array(A + 1).fill(0);
  for (let s = 0; s < A; s++) cum[s + 1] = cum[s] + freq[s];
  const slot2sym = new Uint16Array(RANS_M);
  for (let s = 0; s < A; s++) for (let i = cum[s]; i < cum[s + 1]; i++) slot2sym[i] = s;
  return { freq, cum, slot2sym };
}

// ---------- Re-Pair grammar factorisation ----------
// Input: array of terminal symbol ints, plus a Set of "barrier" symbol values
// across which pairs are never formed (record separators). Output: { seq
// (reduced sequence of symbols, terminals + nonterminals), rules (array of
// [a,b] indexed by nonterminal id - ntBase), ntBase }.
// Nonterminals get ids ntBase, ntBase+1, ... . Stops when the best pair occurs
// fewer than minOcc times or maxRules reached.
export function rePair(seq0, barriers, ntBase, { minOcc = 2, maxRules = 100000 } = {}) {
  let seq = seq0.slice();
  const rules = [];
  const isBar = (s) => barriers.has(s);
  for (let iter = 0; iter < maxRules; iter++) {
    // count adjacent pairs (skip pairs touching a barrier)
    const counts = new Map();
    for (let i = 0; i + 1 < seq.length; i++) {
      const a = seq[i], b = seq[i + 1];
      if (isBar(a) || isBar(b)) continue;
      const key = a * 4294967296 + b; // a,b < 2^31 assumed
      counts.set(key, (counts.get(key) || 0) + 1);
    }
    // pick best
    let bestKey = -1, bestCount = 0;
    for (const [k, c] of counts) if (c > bestCount) { bestCount = c; bestKey = k; }
    if (bestCount < minOcc) break;
    const a = Math.floor(bestKey / 4294967296);
    const b = bestKey % 4294967296;
    const nt = ntBase + rules.length;
    rules.push([a, b]);
    // replace non-overlapping occurrences left-to-right
    const next = [];
    for (let i = 0; i < seq.length; i++) {
      if (i + 1 < seq.length && seq[i] === a && seq[i + 1] === b && !isBar(a) && !isBar(b)) {
        next.push(nt); i++;
      } else next.push(seq[i]);
    }
    seq = next;
  }
  return { seq, rules, ntBase };
}

// Expand a Re-Pair reduced sequence back to terminals.
export function rePairExpand(seq, rules, ntBase) {
  const out = [];
  const stack = [];
  for (let i = seq.length - 1; i >= 0; i--) stack.push(seq[i]);
  while (stack.length) {
    const s = stack.pop();
    if (s >= ntBase && s < ntBase + rules.length) {
      const [a, b] = rules[s - ntBase];
      stack.push(b); stack.push(a);
    } else out.push(s);
  }
  return out;
}

export { RANS_M };
