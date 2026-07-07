// Prototype KOTK/1 codec 2 (kot-haiku/1 + kot-ast/1 bytecode) — the measured
// receipt behind docs/design-compact-kernel-serialization.md s9(a)/s12.
//   node tools/pack/proto-kotk1-haiku.mjs [<recordsDir>] [--out <file>]
// The published numbers were run against the frozen 2,348-record snapshot
// (data/haiku-tier/snapshots/haiku-records-2348-20260707T201855Z.tar.zst,
// extracted); default is the live records/ dir (a moving target).
// encode -> decode -> rebuild JCS identity payloads -> byte-compare against
// nfcDeep(original) for EVERY record, and verify recomputed urn:kot: against
// minted-urns.jsonl for every record that has a published URN. Any mismatch
// is a hard failure.
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const REPO = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const dirArg = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : null;
const DIR = dirArg ?? join(REPO, "data", "haiku-tier", "records");
const OUT = (() => { const i = process.argv.indexOf("--out"); return i >= 0 ? process.argv[i + 1] : null; })();
const MINTED = join(REPO, "data", "haiku-tier", "minted-urns.jsonl");

// ---------- closed inventories (from encoder/src/lexicon.ts, kot-ast/1) ----------
const PRIMES = ["I","YOU","SOMEONE","SOMETHING~THING","PEOPLE","BODY","KIND","PART","THIS","THE-SAME","OTHER~ELSE~ANOTHER","ONE","TWO","SOME","ALL","MUCH~MANY","LITTLE~FEW","GOOD","BAD","BIG","SMALL","THINK","KNOW","WANT","DON'T-WANT","FEEL","SEE","HEAR","SAY","WORDS","TRUE","DO","HAPPEN","MOVE","BE-SOMEWHERE","THERE-IS","BE-SPEC","IS-MINE","LIVE","DIE","WHEN~TIME","NOW","BEFORE","AFTER","A-LONG-TIME","A-SHORT-TIME","FOR-SOME-TIME","MOMENT","WHERE~PLACE","HERE","ABOVE","BELOW","FAR","NEAR","SIDE","INSIDE","TOUCH","NOT","MAYBE","CAN","BECAUSE","IF","VERY","MORE","LIKE~AS~WAY"];
const ROLES = ["agent","undergoer","experiencer","stimulus","addressee","topic","quote","complement","attribute","locus","possessor","instrument","comitative","time","duration","place","manner"];
const PREDS = ["DO","HAPPEN","MOVE","THINK","KNOW","WANT","DON'T-WANT","FEEL","SEE","HEAR","SAY","WORDS","TRUE","BE-SOMEWHERE","THERE-IS","BE-SPEC","IS-MINE","LIVE","DIE"];
const OPS = ["NOT","CAN","MAYBE","IF","BECAUSE","WHEN","LIKE","AFTER","BEFORE","VERY","MORE"];
const FRAMES = ["InstanceSchema","WhenTrue","RelationalSchema"];
const REFKINDS = ["SomeoneRef","SomethingRef","TimeRef","PlaceRef","ClauseRef"];
const primeId = new Map(PRIMES.map((p,i)=>[p,i]));
const roleId = new Map(ROLES.map((p,i)=>[p,i]));
const predId = new Map(PREDS.map((p,i)=>[p,i]));
const opId = new Map(OPS.map((p,i)=>[p,i]));

// ---------- helpers ----------
function jcs(v) {
  if (v === null || typeof v !== "object") return JSON.stringify(v);
  if (Array.isArray(v)) return "[" + v.map(jcs).join(",") + "]";
  return "{" + Object.keys(v).sort().map(k => JSON.stringify(k) + ":" + jcs(v[k])).join(",") + "}";
}
function nfcDeep(v) {
  if (typeof v === "string") return v.normalize("NFC");
  if (Array.isArray(v)) return v.map(nfcDeep);
  if (v !== null && typeof v === "object") { const o = {}; for (const k of Object.keys(v)) o[k.normalize("NFC")] = nfcDeep(v[k]); return o; }
  return v;
}
const B32 = "abcdefghijklmnopqrstuvwxyz234567";
function base32(bytes){let out="",bits=0,val=0;for(const b of bytes){val=(val<<8)|b;bits+=8;while(bits>=5){out+=B32[(val>>>(bits-5))&31];bits-=5;}}if(bits>0)out+=B32[(val<<(5-bits))&31];return out;}
function mint(header,payload){const d=createHash("sha256").update(Buffer.concat([Buffer.from(header,"utf8"),Buffer.from(jcs(payload),"utf8")])).digest();return "urn:kot:b"+base32(Buffer.concat([Buffer.from([0x12,0x20]),d]));}
class W{constructor(){this.chunks=[];this.len=0;}byte(b){this.chunks.push(Buffer.from([b]));this.len+=1;}varint(n){const bs=[];let v=n;do{let b=v&0x7f;v=Math.floor(v/128);if(v>0)b|=0x80;bs.push(b);}while(v>0);this.chunks.push(Buffer.from(bs));this.len+=bs.length;}bytes(buf){this.chunks.push(buf);this.len+=buf.length;}str(s){const b=Buffer.from(s.normalize("NFC"),"utf8");this.varint(b.length);this.bytes(b);}buf(){return Buffer.concat(this.chunks);}}
class R{constructor(buf){this.b=buf;this.p=0;}byte(){return this.b[this.p++];}varint(){let m=1,v=0;for(;;){const b=this.b[this.p++];v+=(b&0x7f)*m;if(!(b&0x80))return v;m*=128;}}str(){const n=this.varint();const s=this.b.toString("utf8",this.p,this.p+n);this.p+=n;return s;}}

// ---------- load ----------
const files = readdirSync(DIR).filter(f=>f.endsWith(".json")).sort();
const recs = [];
const extSet = new Set();
function collectExt(node){ // gather concept-ref URNs from an AST
  if (Array.isArray(node)) { node.forEach(collectExt); return; }
  if (node && typeof node === "object") {
    if ((node.kind === "concept" || node.kind === "conceptHead") && typeof node.id === "string") extSet.add(node.id);
    for (const k of Object.keys(node)) collectExt(node[k]);
  }
}
for (const f of files) {
  const r = JSON.parse(readFileSync(join(DIR,f),"utf8"));
  const sid = r.id.slice("urn:haiku-tier:".length);
  if (r.schema!=="haiku-tier/1"||r.semanticStatus!=="ModelAuthored") throw new Error("dict miss "+sid);
  const rec = { sid, candidateStatus:r.candidateStatus, kind:r.kind };
  for (const k of ["groundingNote","groundingRefs","moleculeDepth","record"]) if (k in r) rec[k]=r[k];
  if (rec.groundingRefs) rec.groundingRefs.forEach(u=>extSet.add(u));
  if (rec.record) collectExt(rec.record);
  recs.push(rec);
}
recs.sort((a,b)=>a.sid<b.sid?-1:a.sid>b.sid?1:0);
const EXT = [...extSet].sort();
const extId = new Map(EXT.map((u,i)=>[u,i]));
const CAND = [...new Set(recs.map(r=>r.candidateStatus))].sort();
const KINDS = [...new Set(recs.map(r=>r.kind))].sort();
const candId = new Map(CAND.map((c,i)=>[c,i]));
const kindId = new Map(KINDS.map((c,i)=>[c,i]));

// ---------- AST bytecode: encode ----------
function encNode(w, node) { // Clause | Filler | OpArg
  if (node.type === "pred") {
    const pi = predId.get(node.pred); if (pi===undefined) throw new Error("pred "+node.pred);
    w.byte(0x00|pi);
    let mask=0; const present=[];
    for (let i=0;i<ROLES.length;i++) if (ROLES[i] in node.roles && node.roles[ROLES[i]]!==undefined){mask|=(1<<i);present.push(ROLES[i]);}
    const keys=Object.keys(node.roles).filter(k=>node.roles[k]!==undefined);
    if (keys.length!==present.length) throw new Error("unknown role in "+keys);
    w.varint(mask);
    for (const role of present) encNode(w, node.roles[role]);
    return;
  }
  if (node.type === "op") {
    const oi = opId.get(node.op); if (oi===undefined) throw new Error("op "+node.op);
    w.byte(0x20|oi);
    w.varint(node.args.length);
    for (const a of node.args) encNode(w,a);
    return;
  }
  switch (node.kind) {
    case "sp": { encSP(w,node); return; }
    case "ref": { if(node.index<1||node.index>32) throw new Error("ref idx"); w.byte(0x40|(node.index-1)); return; }
    case "prime": { w.byte(0x60); w.byte(reqPrime(node.prime)); return; }
    case "concept": { w.byte(0x61); w.varint(extId.get(node.id)); return; }
    case "clause": { w.byte(0x62); encNode(w,node.clause); return; }
    case "quote": { w.byte(0x63); w.varint(node.clauses.length); node.clauses.forEach(c=>encNode(w,c)); return; }
    case "temporal": { w.byte(node.op==="AFTER"?0x64:0x65); encNode(w,node.anchor); return; }
    default: throw new Error("node? "+JSON.stringify(node).slice(0,80));
  }
}
function reqPrime(p){const i=primeId.get(p);if(i===undefined)throw new Error("prime "+p);return i;}
function encSP(w,sp){
  w.byte(0x30);
  let flags=0;
  if (sp.det!==undefined) flags|=1;
  if (sp.quant!==undefined) flags|=2;
  if (sp.mods!==undefined) flags|=4;
  if (sp.bind!==undefined) flags|=8;
  if (sp.restrictedBy!==undefined) flags|=16;
  w.byte(flags);
  if (flags&1) w.byte(reqPrime(sp.det));
  if (flags&2) w.byte(reqPrime(sp.quant));
  if (flags&4){ w.varint(sp.mods.length); for(const m of sp.mods){ w.byte(reqPrime(m.mod)|(m.intensifier!==undefined?0x80:0)); if(m.intensifier!==undefined) w.byte(reqPrime(m.intensifier)); } }
  if (flags&8) w.varint(sp.bind);
  const h=sp.head;
  if (h.kind==="primeHead"){w.byte(0x70);w.byte(reqPrime(h.prime));}
  else if (h.kind==="refHead"){w.byte(0x71);w.byte(h.index);}
  else if (h.kind==="conceptHead"){w.byte(0x72);w.varint(extId.get(h.id));}
  else if (h.kind==="kindFrame"){w.byte(0x73);encNode(w,h.of);}
  else if (h.kind==="partFrame"){w.byte(0x74);encNode(w,h.of);}
  else throw new Error("head "+h.kind);
  if (flags&16) encNode(w,sp.restrictedBy);
}

// ---------- encode document ----------
const w = new W();
w.bytes(Buffer.from("KOTK1","utf8"));
w.str("kot-haiku/1\n");
w.str(JSON.stringify({schema:"haiku-tier/1",semanticStatus:"ModelAuthored",astSchema:"kot-ast/1"}));
w.varint(CAND.length); CAND.forEach(c=>w.str(c));
w.varint(KINDS.length); KINDS.forEach(c=>w.str(c));
w.varint(EXT.length); EXT.forEach(u=>w.str(u));
// Try strict bytecode; verify by immediate decode+JCS self-check; else escape.
function tryEncodeAst(ex){
  const tw=new W();
  if (ex.schema!=="kot-ast/1") throw new Error("ast schema");
  const frameIdx=FRAMES.indexOf(ex.frame);
  if (frameIdx<0) throw new Error("frame");
  tw.byte(frameIdx);
  const refs=ex.referents||[];
  refs.forEach((rd,i)=>{if(rd.index!==i+1)throw new Error("non-dense referent");
    const extra=Object.keys(rd).filter(k=>k!=="index"&&k!=="refKind"); if(extra.length)throw new Error("referent extras");});
  tw.varint(refs.length);
  refs.forEach(rd=>{const ki=REFKINDS.indexOf(rd.refKind); if(ki<0)throw new Error("refKind"); tw.byte(ki);});
  tw.varint(ex.clauses.length);
  ex.clauses.forEach(c=>encNode(tw,c));
  const buf=tw.buf();
  // pack-time self-check: decode and compare JCS bytes (normative in the spec)
  const rr=new R(buf);
  const frame=FRAMES[rr.byte()];
  const nrf=rr.varint(); const referents=[]; for(let j=0;j<nrf;j++)referents.push({index:j+1,refKind:REFKINDS[rr.byte()]});
  const ncl=rr.varint(); const clauses=[]; for(let j=0;j<ncl;j++)clauses.push(decNode(rr));
  if (rr.p!==buf.length) throw new Error("selfcheck trailing");
  const round={schema:ex.schema,frame,referents,clauses};
  if (jcs(round)!==jcs(nfcDeep(ex))) throw new Error("selfcheck jcs mismatch");
  return buf;
}
w.varint(recs.length);
let astBytes=0, noteBytes=0, nBytecode=0, nEscape=0, escBytes=0;
for (const r of recs) {
  w.str(r.sid);
  let flags = kindId.get(r.kind) | (candId.get(r.candidateStatus)<<1);
  if ("groundingNote" in r) flags|=4;
  if ("groundingRefs" in r) flags|=8;
  if ("moleculeDepth" in r) flags|=16;
  if ("record" in r) flags|=32;
  let astBuf=null;
  if (flags&32){
    try { astBuf=tryEncodeAst(r.record); nBytecode++; }
    catch { flags|=64; nEscape++; } // bit6: verbatim-JCS escape
  }
  w.byte(flags);
  if (flags&4){const before=w.len; w.str(r.groundingNote); noteBytes+=w.len-before;}
  if (flags&8){w.varint(r.groundingRefs.length); r.groundingRefs.forEach(u=>w.varint(extId.get(u)));}
  if (flags&16) w.varint(r.moleculeDepth);
  if (flags&32){
    const before=w.len;
    if (flags&64){ const s=jcs(nfcDeep(r.record)); w.str(s); escBytes+=w.len-before; }
    else w.bytes(astBuf);
    astBytes+=w.len-before;
  }
}
const packed = w.buf();
if (OUT) writeFileSync(OUT, packed);
console.log("packed bytes:", packed.length, "avg/record:", (packed.length/recs.length).toFixed(1));
console.log("  AST bodies:", astBytes, "avg/explication:", (astBytes/recs.filter(r=>r.record).length).toFixed(1),
  "| bytecode:", nBytecode, "escape:", nEscape, "escape bytes:", escBytes);
console.log("  groundingNotes:", noteBytes);

// ---------- decode ----------
function decNode(r){
  const t=r.byte();
  if (t<0x20){ const pred=PREDS[t]; const mask=r.varint(); const roles={}; for(let i=0;i<ROLES.length;i++) if(mask&(1<<i)) roles[ROLES[i]]=decNode(r); return {type:"pred",pred,roles}; }
  if (t<0x30){ const op=OPS[t-0x20]; const n=r.varint(); const args=[]; for(let i=0;i<n;i++) args.push(decNode(r)); return {type:"op",op,args}; }
  if (t===0x30) return decSP(r);
  if (t>=0x40&&t<0x60) return {kind:"ref",index:(t&0x1f)+1};
  if (t===0x60) return {kind:"prime",prime:PRIMES[r.byte()]};
  if (t===0x61) return {kind:"concept",id:EXT[r.varint()]};
  if (t===0x62) return {kind:"clause",clause:decNode(r)};
  if (t===0x63){const n=r.varint();const clauses=[];for(let i=0;i<n;i++)clauses.push(decNode(r));return {kind:"quote",clauses};}
  if (t===0x64||t===0x65) return {kind:"temporal",op:t===0x64?"AFTER":"BEFORE",anchor:decNode(r)};
  throw new Error("tag "+t);
}
function decSP(r){
  const flags=r.byte(); const sp={kind:"sp"};
  if (flags&1) sp.det=PRIMES[r.byte()];
  if (flags&2) sp.quant=PRIMES[r.byte()];
  if (flags&4){const n=r.varint();sp.mods=[];for(let i=0;i<n;i++){const b=r.byte();const m={mod:PRIMES[b&0x7f]};if(b&0x80)m.intensifier=PRIMES[r.byte()];sp.mods.push(m);}}
  if (flags&8) sp.bind=r.varint();
  const ht=r.byte();
  if (ht===0x70) sp.head={kind:"primeHead",prime:PRIMES[r.byte()]};
  else if (ht===0x71) sp.head={kind:"refHead",index:r.byte()};
  else if (ht===0x72) sp.head={kind:"conceptHead",id:EXT[r.varint()]};
  else if (ht===0x73) sp.head={kind:"kindFrame",of:decNode(r)};
  else if (ht===0x74) sp.head={kind:"partFrame",of:decNode(r)};
  else throw new Error("head tag "+ht);
  if (flags&16) sp.restrictedBy=decNode(r);
  return sp;
}
const rd=new R(packed); rd.p+=5;
const profile=rd.str();
const consts=JSON.parse(rd.str());
const nc=rd.varint(); const cand=[]; for(let i=0;i<nc;i++)cand.push(rd.str());
const nk=rd.varint(); const kinds=[]; for(let i=0;i<nk;i++)kinds.push(rd.str());
const ne=rd.varint(); const ext=[]; for(let i=0;i<ne;i++)ext.push(rd.str());
if (JSON.stringify(ext)!==JSON.stringify(EXT)) throw new Error("ext table mismatch");
const nr=rd.varint();
const decoded=[];
for (let i=0;i<nr;i++){
  const sid=rd.str();
  const flags=rd.byte();
  const pay={sourceId:sid,schema:consts.schema,semanticStatus:consts.semanticStatus,candidateStatus:cand[(flags>>1)&1],kind:kinds[flags&1]};
  if (flags&4) pay.groundingNote=rd.str();
  if (flags&8){const n=rd.varint();pay.groundingRefs=[];for(let j=0;j<n;j++)pay.groundingRefs.push(ext[rd.varint()]);}
  if (flags&16) pay.moleculeDepth=rd.varint();
  if (flags&32){
    if (flags&64){ pay.record=JSON.parse(rd.str()); }
    else {
      const frame=FRAMES[rd.byte()];
      const nrf=rd.varint(); const referents=[]; for(let j=0;j<nrf;j++)referents.push({index:j+1,refKind:REFKINDS[rd.byte()]});
      const ncl=rd.varint(); const clauses=[]; for(let j=0;j<ncl;j++)clauses.push(decNode(rd));
      pay.record={schema:consts.astSchema,frame,referents,clauses};
    }
  }
  decoded.push(pay);
}
if (rd.p!==packed.length) throw new Error("trailing bytes");

// ---------- verify: JCS byte-equality + published URNs ----------
const minted=new Map();
try{for(const line of readFileSync(MINTED,"utf8").split("\n")){if(!line.trim())continue;const o=JSON.parse(line);minted.set(o.sourceId,o.urn);}}catch{}
let eq=0,neq=0,urnOk=0,urnBad=0,urnChecked=0;
for (let i=0;i<recs.length;i++){
  const r=recs[i];
  const orig={sourceId:r.sid,schema:"haiku-tier/1",semanticStatus:"ModelAuthored",candidateStatus:r.candidateStatus,kind:r.kind};
  for (const k of ["groundingNote","groundingRefs","moleculeDepth","record"]) if (k in r) orig[k]=r[k];
  const a=jcs(nfcDeep(orig)), b=jcs(decoded[i]);
  if (a===b) eq++; else { neq++; if(neq<3){console.log("JCS MISMATCH",r.sid);console.log(" orig:",a.slice(0,200));console.log(" dec :",b.slice(0,200));} }
  if (minted.has(r.sid)){urnChecked++;const u=mint(profile,decoded[i]);if(u===minted.get(r.sid))urnOk++;else{urnBad++;if(urnBad<3)console.log("URN MISMATCH",r.sid);}}
}
console.log("JCS byte-equality:",eq,"of",recs.length,"(mismatches:",neq+")");
console.log("published-URN verify:",urnOk,"ok /",urnBad,"bad of",urnChecked,"checked");
if (neq>0||urnBad>0){console.error("ERR_KOTK1_ROUNDTRIP");process.exit(1);}
// canonical-kernel-only JCS size for reference
let jcsTotal=0; for(const d of decoded) jcsTotal+=Buffer.byteLength(jcs(d));
console.log("reconstructed identity JCS total:",jcsTotal);
