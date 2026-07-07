// KOTK/2 haiku-tier path: AST subtree factoring (Re-Pair over a pre-order token
// stream) + rANS, with provenance + all natural-language text held in sidecars.
// Imported by proto-kotk2-grammar.mjs. Reuses the KOTK/1 kot-ast/1 tag semantics.
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import * as L from "./kotk2-lib.mjs";

const PRIMES = ["I","YOU","SOMEONE","SOMETHING~THING","PEOPLE","BODY","KIND","PART","THIS","THE-SAME","OTHER~ELSE~ANOTHER","ONE","TWO","SOME","ALL","MUCH~MANY","LITTLE~FEW","GOOD","BAD","BIG","SMALL","THINK","KNOW","WANT","DON'T-WANT","FEEL","SEE","HEAR","SAY","WORDS","TRUE","DO","HAPPEN","MOVE","BE-SOMEWHERE","THERE-IS","BE-SPEC","IS-MINE","LIVE","DIE","WHEN~TIME","NOW","BEFORE","AFTER","A-LONG-TIME","A-SHORT-TIME","FOR-SOME-TIME","MOMENT","WHERE~PLACE","HERE","ABOVE","BELOW","FAR","NEAR","SIDE","INSIDE","TOUCH","NOT","MAYBE","CAN","BECAUSE","IF","VERY","MORE","LIKE~AS~WAY"];
const ROLES = ["agent","undergoer","experiencer","stimulus","addressee","topic","quote","complement","attribute","locus","possessor","instrument","comitative","time","duration","place","manner"];
const PREDS = ["DO","HAPPEN","MOVE","THINK","KNOW","WANT","DON'T-WANT","FEEL","SEE","HEAR","SAY","WORDS","TRUE","BE-SOMEWHERE","THERE-IS","BE-SPEC","IS-MINE","LIVE","DIE"];
const OPS = ["NOT","CAN","MAYBE","IF","BECAUSE","WHEN","LIKE","AFTER","BEFORE","VERY","MORE"];
const FRAMES = ["InstanceSchema","WhenTrue","RelationalSchema"];
const REFKINDS = ["SomeoneRef","SomethingRef","TimeRef","PlaceRef","ClauseRef"];
const primeId = new Map(PRIMES.map((p, i) => [p, i]));
const predId = new Map(PREDS.map((p, i) => [p, i]));
const opId = new Map(OPS.map((p, i) => [p, i]));

// ---- unified token alphabet (primes-first) ----
const OPC = 65;                       // opcode base
const FRAME0 = OPC, PRED0 = OPC + 3, OP0 = OPC + 22, SP = OPC + 33;  // 65,68,87,98
const REFNODE = 99, PRIMEFILL = 100, CONCEPTFILL = 101, CLAUSEFILL = 102, QUOTE = 103,
      TEMP_AF = 104, TEMP_BE = 105, HEAD_PRIME = 106, HEAD_REF = 107, HEAD_CONC = 108,
      HEAD_KIND = 109, HEAD_PART = 110, REC_END = 111, INT_ESC = 127;
const INTCAP = 1024, INT0 = 128, EXT0 = INT0 + INTCAP;  // ext refs at 1152+
const NTBASE = 100000;

export function runHaiku(REPO, arg, zstd19, fmt) {
  const DIR = arg("--haiku-dir", join(REPO, "data", "haiku-tier", "records"));
  const OUTDIR = arg("--out", "/tmp");
  const MINTED = join(REPO, "data", "haiku-tier", "minted-urns.jsonl");

  const files = readdirSync(DIR).filter((f) => f.endsWith(".json")).sort();
  const recs = [];
  const extSet = new Set();
  const collectExt = (node) => { if (Array.isArray(node)) return node.forEach(collectExt); if (node && typeof node === "object") { if ((node.kind === "concept" || node.kind === "conceptHead") && typeof node.id === "string") extSet.add(node.id); for (const k of Object.keys(node)) collectExt(node[k]); } };
  for (const f of files) {
    const r = JSON.parse(readFileSync(join(DIR, f), "utf8"));
    const sid = r.id.slice("urn:haiku-tier:".length);
    const rec = { sid, candidateStatus: r.candidateStatus, kind: r.kind };
    for (const k of ["groundingNote", "groundingRefs", "moleculeDepth", "record"]) if (k in r) rec[k] = r[k];
    if (rec.groundingRefs) rec.groundingRefs.forEach((u) => extSet.add(u));
    if (rec.record) collectExt(rec.record);
    recs.push(rec);
  }
  recs.sort((a, b) => (a.sid < b.sid ? -1 : a.sid > b.sid ? 1 : 0));
  const EXT = [...extSet].sort();
  const extId = new Map(EXT.map((u, i) => [u, i]));
  const CAND = [...new Set(recs.map((r) => r.candidateStatus))].sort();
  const KINDS = [...new Set(recs.map((r) => r.kind))].sort();
  const candId = new Map(CAND.map((c, i) => [c, i]));
  const kindId = new Map(KINDS.map((c, i) => [c, i]));

  // ---- AST -> token stream (mirrors KOTK/1 encNode; ints, not bytes) ----
  const pushInt = (toks, esc, n) => { if (n < INTCAP) toks.push(INT0 + n); else { toks.push(INT_ESC); esc.varint(n); } };
  function encNode(toks, esc, node) {
    if (node.type === "pred") {
      const pi = predId.get(node.pred); if (pi === undefined) throw new Error("pred");
      toks.push(PRED0 + pi);
      let mask = 0; const present = [];
      for (let i = 0; i < ROLES.length; i++) if (ROLES[i] in node.roles && node.roles[ROLES[i]] !== undefined) { mask |= (1 << i); present.push(ROLES[i]); }
      if (Object.keys(node.roles).filter((k) => node.roles[k] !== undefined).length !== present.length) throw new Error("unknown role");
      pushInt(toks, esc, mask);
      for (const role of present) encNode(toks, esc, node.roles[role]);
      return;
    }
    if (node.type === "op") {
      const oi = opId.get(node.op); if (oi === undefined) throw new Error("op");
      toks.push(OP0 + oi); pushInt(toks, esc, node.args.length);
      for (const a of node.args) encNode(toks, esc, a); return;
    }
    switch (node.kind) {
      case "sp": return encSP(toks, esc, node);
      case "ref": { if (node.index < 1 || node.index > 32) throw new Error("refidx"); toks.push(REFNODE); pushInt(toks, esc, node.index); return; }
      case "prime": { toks.push(PRIMEFILL); toks.push(reqPrime(node.prime)); return; }
      case "concept": { toks.push(CONCEPTFILL); toks.push(EXT0 + extId.get(node.id)); return; }
      case "clause": { toks.push(CLAUSEFILL); encNode(toks, esc, node.clause); return; }
      case "quote": { toks.push(QUOTE); pushInt(toks, esc, node.clauses.length); node.clauses.forEach((c) => encNode(toks, esc, c)); return; }
      case "temporal": { toks.push(node.op === "AFTER" ? TEMP_AF : TEMP_BE); encNode(toks, esc, node.anchor); return; }
      default: throw new Error("node?");
    }
  }
  const reqPrime = (p) => { const i = primeId.get(p); if (i === undefined) throw new Error("prime"); return i; };
  function encSP(toks, esc, sp) {
    toks.push(SP);
    let flags = 0;
    if (sp.det !== undefined) flags |= 1;
    if (sp.quant !== undefined) flags |= 2;
    if (sp.mods !== undefined) flags |= 4;
    if (sp.bind !== undefined) flags |= 8;
    if (sp.restrictedBy !== undefined) flags |= 16;
    pushInt(toks, esc, flags);
    if (flags & 1) toks.push(reqPrime(sp.det));
    if (flags & 2) toks.push(reqPrime(sp.quant));
    if (flags & 4) { pushInt(toks, esc, sp.mods.length); for (const m of sp.mods) { toks.push(reqPrime(m.mod)); toks.push(m.intensifier !== undefined ? INT0 + 1 : INT0); if (m.intensifier !== undefined) toks.push(reqPrime(m.intensifier)); } }
    if (flags & 8) pushInt(toks, esc, sp.bind);
    const h = sp.head;
    if (h.kind === "primeHead") { toks.push(HEAD_PRIME); toks.push(reqPrime(h.prime)); }
    else if (h.kind === "refHead") { toks.push(HEAD_REF); pushInt(toks, esc, h.index); }
    else if (h.kind === "conceptHead") { toks.push(HEAD_CONC); toks.push(EXT0 + extId.get(h.id)); }
    else if (h.kind === "kindFrame") { toks.push(HEAD_KIND); encNode(toks, esc, h.of); }
    else if (h.kind === "partFrame") { toks.push(HEAD_PART); encNode(toks, esc, h.of); }
    else throw new Error("head");
    if (flags & 16) encNode(toks, esc, sp.restrictedBy);
  }

  // token cursor decode (mirrors encode)
  function makeCursor(toks, esc) { return { toks, esc, i: 0, next() { return this.toks[this.i++]; } }; }
  const popInt = (c) => { const t = c.next(); return t === INT_ESC ? c.esc.varint() : t - INT0; };
  function decNode(c) {
    const t = c.next();
    if (t >= PRED0 && t < OP0) { const pred = PREDS[t - PRED0]; const mask = popInt(c); const roles = {}; for (let i = 0; i < ROLES.length; i++) if (mask & (1 << i)) roles[ROLES[i]] = decNode(c); return { type: "pred", pred, roles }; }
    if (t >= OP0 && t < SP) { const op = OPS[t - OP0]; const n = popInt(c); const args = []; for (let i = 0; i < n; i++) args.push(decNode(c)); return { type: "op", op, args }; }
    if (t === SP) return decSP(c);
    if (t === REFNODE) return { kind: "ref", index: popInt(c) };
    if (t === PRIMEFILL) return { kind: "prime", prime: PRIMES[c.next()] };
    if (t === CONCEPTFILL) return { kind: "concept", id: EXT[c.next() - EXT0] };
    if (t === CLAUSEFILL) return { kind: "clause", clause: decNode(c) };
    if (t === QUOTE) { const n = popInt(c); const clauses = []; for (let i = 0; i < n; i++) clauses.push(decNode(c)); return { kind: "quote", clauses }; }
    if (t === TEMP_AF || t === TEMP_BE) return { kind: "temporal", op: t === TEMP_AF ? "AFTER" : "BEFORE", anchor: decNode(c) };
    throw new Error("tok " + t);
  }
  function decSP(c) {
    const flags = popInt(c); const sp = { kind: "sp" };
    if (flags & 1) sp.det = PRIMES[c.next()];
    if (flags & 2) sp.quant = PRIMES[c.next()];
    if (flags & 4) { const n = popInt(c); sp.mods = []; for (let i = 0; i < n; i++) { const mod = PRIMES[c.next()]; const inten = popInt(c); const m = { mod }; if (inten) m.intensifier = PRIMES[c.next()]; sp.mods.push(m); } }
    if (flags & 8) sp.bind = popInt(c);
    const ht = c.next();
    if (ht === HEAD_PRIME) sp.head = { kind: "primeHead", prime: PRIMES[c.next()] };
    else if (ht === HEAD_REF) sp.head = { kind: "refHead", index: popInt(c) };
    else if (ht === HEAD_CONC) sp.head = { kind: "conceptHead", id: EXT[c.next() - EXT0] };
    else if (ht === HEAD_KIND) sp.head = { kind: "kindFrame", of: decNode(c) };
    else if (ht === HEAD_PART) sp.head = { kind: "partFrame", of: decNode(c) };
    else throw new Error("head tok " + ht);
    if (flags & 16) sp.restrictedBy = decNode(c);
    return sp;
  }

  // encode one AST record to tokens (returns null if it doesn't conform -> escape)
  function astToTokens(ex) {
    if (ex.schema !== "kot-ast/1") return null;
    const fi = FRAMES.indexOf(ex.frame); if (fi < 0) return null;
    const toks = [FRAME0 + fi]; const esc = new L.W();
    try {
      const refs = ex.referents || [];
      for (let i = 0; i < refs.length; i++) { const rd = refs[i]; if (rd.index !== i + 1) return null; if (Object.keys(rd).some((k) => k !== "index" && k !== "refKind")) return null; }
      pushInt(toks, esc, refs.length);
      for (const rd of refs) { const ki = REFKINDS.indexOf(rd.refKind); if (ki < 0) return null; pushInt(toks, esc, ki); }
      pushInt(toks, esc, ex.clauses.length);
      for (const cl of ex.clauses) encNode(toks, esc, cl);
    } catch { return null; }
    // self-check: decode and JCS-compare
    const c = makeCursor(toks.slice(), new L.R(esc.buf()));
    const frame = FRAMES[c.next() - FRAME0]; const nrf = popInt(c); const referents = []; for (let j = 0; j < nrf; j++) referents.push({ index: j + 1, refKind: REFKINDS[popInt(c)] });
    const ncl = popInt(c); const clauses = []; for (let j = 0; j < ncl; j++) clauses.push(decNode(c));
    if (c.i !== toks.length) return null;
    const round = { schema: ex.schema, frame, referents, clauses };
    if (L.jcs(round) !== L.jcs(L.nfcDeep(ex))) return null;
    return { toks, esc: esc.buf() };
  }

  // ---- build streams ----
  // structural token stream (all conforming ASTs concatenated, REC_END separated),
  // a per-record escaped-int side stream, and sidecars: scalars, groundingNote text,
  // groundingRefs, escaped-JCS records.
  const allToks = [];
  const escW = new L.W();          // escaped ints, concatenated in record order (conforming records only)
  const scalarW = new L.W();       // sourceId + flags + enums + moleculeDepth + groundingRefs (identity scalars)
  const textW = new L.W();         // groundingNote NL prose  (SIDECAR: natural language)
  const escJcsW = new L.W();       // verbatim-JCS escape records (non-conforming ASTs)
  const recMeta = [];              // per record: has-tokens flag etc for decode
  let nConform = 0, nEscape = 0, nNoRecord = 0;
  let astTokenBytesApprox = 0;

  for (const r of recs) {
    scalarW.str(r.sid);
    let flags = kindId.get(r.kind) | (candId.get(r.candidateStatus) << 1);
    if ("groundingNote" in r) flags |= 4;
    if ("groundingRefs" in r) flags |= 8;
    if ("moleculeDepth" in r) flags |= 16;
    if ("record" in r) flags |= 32;
    let tokens = null;
    if (flags & 32) { tokens = astToTokens(r.record); if (tokens) nConform++; else { flags |= 64; nEscape++; } }
    else nNoRecord++;
    scalarW.byte(flags);
    if (flags & 4) textW.str(r.groundingNote);
    if (flags & 8) { scalarW.varint(r.groundingRefs.length); r.groundingRefs.forEach((u) => scalarW.varint(extId.get(u))); }
    if (flags & 16) scalarW.varint(r.moleculeDepth);
    if (flags & 32) {
      if (flags & 64) { escJcsW.str(L.jcs(L.nfcDeep(r.record))); recMeta.push({ tokens: false }); }
      else { for (const t of tokens.toks) allToks.push(t); allToks.push(REC_END); escW.bytes(tokens.esc); recMeta.push({ tokens: true, escLen: tokens.esc.length }); }
    } else recMeta.push({ tokens: false });
  }

  // ---- entropy-only vs grammar on the AST token stream ----
  const H = L.order0Entropy(allToks);
  // dense-remap for plain rANS (grammar OFF)
  function denseRans(arr, extraSyms = []) {
    const seen = new Map(); const d2o = [];
    for (const s of arr) if (!seen.has(s)) { seen.set(s, d2o.length); d2o.push(s); }
    for (const s of extraSyms) if (!seen.has(s)) { seen.set(s, d2o.length); d2o.push(s); }
    const dense = arr.map((s) => seen.get(s));
    const { bytes, model } = dense.length ? L.ransEncode(dense, d2o.length) : { bytes: Buffer.alloc(0), model: { freq: [] } };
    return { bytes, model, d2o, seen };
  }
  const flat = denseRans(allToks);
  const flatModelBytes = (() => { const w = new L.W(); L.writeModel(w, flat.model.freq); return w.len; })();

  // grammar ON: Re-Pair over the token stream (factors repeated AST subtrees + record templates)
  const rp = L.rePair(allToks, new Set(), NTBASE, { minOcc: 3, maxRules: 6000 });
  const rpDense = denseRans(rp.seq, rp.rules.flat());
  const rpSeqModelBytes = (() => { const w = new L.W(); L.writeModel(w, rpDense.model.freq); return w.len; })();
  const rpRuleW = new L.W(); rpRuleW.varint(rp.rules.length); for (const [a, b] of rp.rules) { rpRuleW.varint(rpDense.seen.get(a)); rpRuleW.varint(rpDense.seen.get(b)); }
  const rpMapW = new L.W(); rpMapW.varint(rpDense.d2o.length); for (const s of rpDense.d2o) rpMapW.varint(s);

  // ---- assemble the SMALLEST packed file and prove round-trip ----
  const pw = new L.W();
  pw.bytes(Buffer.from("KOTK2H", "utf8"));
  pw.str("kot-haiku/1\n");
  pw.str(JSON.stringify({ schema: "haiku-tier/1", semanticStatus: "ModelAuthored", astSchema: "kot-ast/1" }));
  pw.varint(CAND.length); CAND.forEach((c) => pw.str(c));
  pw.varint(KINDS.length); KINDS.forEach((c) => pw.str(c));
  pw.varint(EXT.length); EXT.forEach((u) => pw.str(u));
  pw.varint(recs.length);
  // scalars block (identity scalars)
  const scalarBuf = scalarW.buf(); pw.varint(scalarBuf.length); pw.bytes(scalarBuf);
  // NL-text sidecar (groundingNote) — kept in-file here for the honest INV-1 re-mint,
  // but flagged as sidecar-eligible; measured separately below.
  const textBuf = textW.buf(); pw.varint(textBuf.length); pw.bytes(textBuf);
  // escaped-JCS records
  const escJcsBuf = escJcsW.buf(); pw.varint(escJcsBuf.length); pw.bytes(escJcsBuf);
  // escaped-ints side stream
  const escBuf = escW.buf(); pw.varint(escBuf.length); pw.bytes(escBuf);
  // grammar: NTBASE, rules, dense map, seq model + rANS
  pw.varint(NTBASE);
  pw.bytes(rpRuleW.buf());
  pw.bytes(rpMapW.buf());
  { const w = new L.W(); L.writeModel(w, rpDense.model.freq); pw.bytes(w.buf()); }
  pw.varint(rp.seq.length); pw.varint(rpDense.bytes.length); pw.bytes(rpDense.bytes);
  const packed = pw.buf();
  writeFileSync(join(OUTDIR, "kotk2-haiku.bin"), packed);

  // ---- DECODE packed -> rebuild payloads -> re-mint ----
  const pr = new L.R(packed); pr.p += 6;
  const profile = pr.str();
  const consts = JSON.parse(pr.str());
  const nc = pr.varint(); const cand = []; for (let i = 0; i < nc; i++) cand.push(pr.str());
  const nk = pr.varint(); const kinds = []; for (let i = 0; i < nk; i++) kinds.push(pr.str());
  const ne = pr.varint(); const ext = []; for (let i = 0; i < ne; i++) ext.push(pr.str());
  const nr = pr.varint();
  const scLen = pr.varint(); const scR = new L.R(pr.bytes(scLen));
  const txLen = pr.varint(); const txR = new L.R(pr.bytes(txLen));
  const ejLen = pr.varint(); const ejR = new L.R(pr.bytes(ejLen));
  const esLen = pr.varint(); const esR = new L.R(pr.bytes(esLen));
  const ntb = pr.varint();
  const nRules = pr.varint(); const rules = []; for (let i = 0; i < nRules; i++) rules.push([pr.varint(), pr.varint()]);
  const dCount = pr.varint(); const d2o = []; for (let i = 0; i < dCount; i++) d2o.push(pr.varint());
  const seqModel = L.readModel(pr);
  const seqLen = pr.varint(); const seqRansLen = pr.varint(); const seqBytes = pr.bytes(seqRansLen);
  const denseSeq = L.ransDecode(seqBytes, seqLen, seqModel).symbols;
  // map rules back to original ids
  const rulesO = rules.map(([a, b]) => [d2o[a], d2o[b]]);
  const reduced = denseSeq.map((d) => d2o[d]);
  const tokStream = L.rePairExpand(reduced, rulesO, ntb);
  if (pr.p !== packed.length) throw new Error("trailing bytes (haiku)");

  // split tokStream by REC_END into per-conforming-record token arrays
  const perRec = []; let cur = [];
  for (const t of tokStream) { if (t === REC_END) { perRec.push(cur); cur = []; } else cur.push(t); }

  const minted = new Map();
  try { for (const line of readFileSync(MINTED, "utf8").split("\n")) { if (!line.trim()) continue; const o = JSON.parse(line); minted.set(o.sourceId, o.urn); } } catch {}
  let eq = 0, neq = 0, urnOk = 0, urnBad = 0, urnChecked = 0; let ci = 0; const neqSamples = [];
  for (let i = 0; i < nr; i++) {
    const sid = scR.str();
    const flags = scR.byte();
    const pay = { sourceId: sid, schema: consts.schema, semanticStatus: consts.semanticStatus, candidateStatus: cand[(flags >> 1) & 1], kind: kinds[flags & 1] };
    if (flags & 4) pay.groundingNote = txR.str();
    if (flags & 8) { const n = scR.varint(); pay.groundingRefs = []; for (let j = 0; j < n; j++) pay.groundingRefs.push(ext[scR.varint()]); }
    if (flags & 16) pay.moleculeDepth = scR.varint();
    if (flags & 32) {
      if (flags & 64) { pay.record = JSON.parse(ejR.str()); }
      else {
        const toks = perRec[ci++];
        const c = makeCursor(toks, esR);
        const frame = FRAMES[c.next() - FRAME0]; const nrf = popInt(c); const referents = []; for (let j = 0; j < nrf; j++) referents.push({ index: j + 1, refKind: REFKINDS[popInt(c)] });
        const ncl = popInt(c); const clauses = []; for (let j = 0; j < ncl; j++) clauses.push(decNode(c));
        pay.record = { schema: consts.astSchema, frame, referents, clauses };
      }
    }
    // compare against original identity JCS
    const r = recs[i];
    const orig = { sourceId: r.sid, schema: "haiku-tier/1", semanticStatus: "ModelAuthored", candidateStatus: r.candidateStatus, kind: r.kind };
    for (const k of ["groundingNote", "groundingRefs", "moleculeDepth", "record"]) if (k in r) orig[k] = r[k];
    const a = L.jcs(L.nfcDeep(orig)), b = L.jcs(pay);
    if (a === b) eq++; else { neq++; if (neqSamples.length < 3) neqSamples.push({ sid: r.sid, a: a.slice(0, 160), b: b.slice(0, 160) }); }
    if (minted.has(r.sid)) { urnChecked++; const u = L.mint(profile, pay); if (u === minted.get(r.sid)) urnOk++; else urnBad++; }
  }

  // ---- structural-kernel vs sidecar accounting ----
  const scalarBytes = scalarBuf.length;
  const structGrammarBytes = packed.length - textBuf.length - escJcsBuf.length; // structural kernel (excl NL text + escapes)
  const z = zstd19(packed);
  const zStructOnly = zstd19(Buffer.concat([rpDense.bytes, rpRuleW.buf(), rpMapW.buf()]));
  console.log("\n==================== KOTK/2  haiku-tier ====================");
  console.log(`records: ${fmt(recs.length)}   conforming ASTs: ${fmt(nConform)}   escaped(grammar-drift): ${fmt(nEscape)}   no-record: ${fmt(nNoRecord)}`);
  console.log("\n AST token stream (the structural kernel; primes-first unified ids):");
  console.log(`   tokens: ${fmt(allToks.length)}   distinct: ${fmt(H.distinct)}   H0 floor: ${fmt(H.totalBytes)} B (${H.bitsPerSymbol.toFixed(2)} b/tok)`);
  console.log("\n grammar OFF (entropy-only, rANS over tokens):");
  console.log(`   rANS ${fmt(flat.bytes.length)} B (+model ${fmt(flatModelBytes)} B) + escaped-ints ${fmt(escBuf.length)} B  = ${fmt(flat.bytes.length + flatModelBytes + escBuf.length)} B`);
  console.log("\n grammar ON (Re-Pair subtree factoring + rANS):");
  console.log(`   ${fmt(rp.rules.length)} rules, token stream ${fmt(allToks.length)} -> ${fmt(rp.seq.length)} syms`);
  console.log(`   reduced rANS ${fmt(rpDense.bytes.length)} B (+seq-model ${fmt(rpSeqModelBytes)} + rules ${fmt(rpRuleW.len)} + map ${fmt(rpMapW.len)}) + escaped-ints ${fmt(escBuf.length)} B`);
  const grammarStruct = rpDense.bytes.length + rpSeqModelBytes + rpRuleW.len + rpMapW.len + escBuf.length;
  const flatStruct = flat.bytes.length + flatModelBytes + escBuf.length;
  console.log(`   structural-kernel total: ${fmt(grammarStruct)} B   (grammar removed ${fmt(flatStruct - grammarStruct)} B = ${(100 * (flatStruct - grammarStruct) / flatStruct).toFixed(1)}% beyond entropy coding)`);
  console.log("\n sidecars (measured separately; not needed to verify identity in a re-mint corpus):");
  console.log(`   NL-text (groundingNote): ${fmt(textBuf.length)} B  (+zstd ${fmt(zstd19(textBuf))} B)`);
  console.log(`   verbatim-JCS escapes (${fmt(nEscape)} grammar-drift ASTs): ${fmt(escJcsBuf.length)} B`);
  console.log(`   identity scalars (sourceId/enums/refs/depth): ${fmt(scalarBytes)} B`);
  console.log(`\n round-trip (decoded from packed file): JCS byte-equality ${fmt(eq)}/${fmt(recs.length)} (mismatch ${neq}); published-URN ${fmt(urnOk)} ok / ${fmt(urnBad)} bad of ${fmt(urnChecked)}`);
  if (neq) console.log("   SAMPLES", JSON.stringify(neqSamples, null, 1));
  console.log(`\n WHOLE packed file (structural kernel + scalars + NL-text + escapes, self-contained): ${fmt(packed.length)} B  +zstd-19 ${fmt(z)} B  residual ${(packed.length / z).toFixed(3)}`);
  console.log(`   of which structural-kernel-only +zstd: ${fmt(zStructOnly)} B (residual ${(grammarStruct / zStructOnly === Infinity ? 0 : (grammarStruct / zStructOnly)).toFixed(3)})`);
  console.log(` vs KOTK/1: 307,142 B raw / 61,958 B zstd (which INCLUDES 171,223 B of grounding-note prose in the kernel)`);

  if (neq > 0 || urnBad > 0) { console.error("ERR_KOTK2_ROUNDTRIP"); process.exit(1); }
  return { eq, neq, urnOk, urnBad, packed: packed.length };
}
