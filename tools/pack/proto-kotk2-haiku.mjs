// Prototype KOTK/2 entropy-coded columnar codec for haiku-tier (kot-ast/1).
//   node tools/pack/proto-kotk2-haiku.mjs [<recordsDir>] [--out <kernelFile>] [--text <textFile>]
//
// KOTK/2 design points implemented here (see also proto-kotk2-entropy.mjs):
//   1. UNIFIED PRIMES-FIRST ID SPACE, NO STRING DICTIONARY FOR PRIMES. Every
//      prime-valued slot (PrimeFiller, det, quant, mod, intensifier,
//      primeHead) is coded as the prime's pinned chart id 0..64
//      (encoder/src/lexicon.ts PRIMES order) in ONE unified prime stream —
//      no prime string table is stored, only the 65-entry frequency tables
//      the entropy coder needs. Structural operators/preds/frames/roles use
//      the reserved small code ranges (also pinned conventions). Concept
//      references: haiku-tier is STABLE-ref-mode (the mint hashed cross-corpus
//      URN *strings*, not concept ids), so external URNs are identity bytes
//      and must ride in a front-coded table; a future substitute-mode re-mint
//      would let them collapse to global concept ids per design point 1.
//   2. BIT-LEVEL ENTROPY CODING: columnar per-slot symbol streams, each rANS
//      coded with contexts (tag: ctx=prev tag; roleMask: ctx=pred; prime:
//      ctx=slot-kind; argCount: ctx=op; lemma chars: ctx=prev char; ...).
//   3. NATURAL-LANGUAGE TEXT SIDECARRED: groundingNote prose (and the 4.4%
//      verbatim-JCS grammar-drift escapes) go to a separate TEXT segment
//      file. HONEST CAVEAT: for this snapshot the prose is *inside* the
//      identity payloads (stable-mode decision), so the text segment is
//      identity-BEARING — re-minting requires kernel+text together. Moving
//      prose out of identity is an authoring/re-mint decision, not a codec
//      one; the split here isolates the symbolic kernel (near-incompressible)
//      from the prose (where generic compression legitimately wins).
//
// INV-1 proof: encode -> decode(kernel+text) -> rebuild JCS identity payloads
// -> byte-compare against nfcDeep(original) for EVERY record + re-mint
// urn:kot: for every record present in minted-urns.jsonl. Mismatch = exit 1.
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const REPO = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const dirArg = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : null;
const DIR = dirArg ?? join(REPO, "data", "haiku-tier", "records");
const arg = n => { const i = process.argv.indexOf(n); return i >= 0 ? process.argv[i + 1] : null; };
const OUT = arg("--out"), TEXTOUT = arg("--text");
const MINTED = join(REPO, "data", "haiku-tier", "minted-urns.jsonl");

// ---------- closed inventories (encoder/src/lexicon.ts, kot-ast/1 — pinned conventions) ----------
const PRIMES = ["I","YOU","SOMEONE","SOMETHING~THING","PEOPLE","BODY","KIND","PART","THIS","THE-SAME","OTHER~ELSE~ANOTHER","ONE","TWO","SOME","ALL","MUCH~MANY","LITTLE~FEW","GOOD","BAD","BIG","SMALL","THINK","KNOW","WANT","DON'T-WANT","FEEL","SEE","HEAR","SAY","WORDS","TRUE","DO","HAPPEN","MOVE","BE-SOMEWHERE","THERE-IS","BE-SPEC","IS-MINE","LIVE","DIE","WHEN~TIME","NOW","BEFORE","AFTER","A-LONG-TIME","A-SHORT-TIME","FOR-SOME-TIME","MOMENT","WHERE~PLACE","HERE","ABOVE","BELOW","FAR","NEAR","SIDE","INSIDE","TOUCH","NOT","MAYBE","CAN","BECAUSE","IF","VERY","MORE","LIKE~AS~WAY"];
const ROLES = ["agent","undergoer","experiencer","stimulus","addressee","topic","quote","complement","attribute","locus","possessor","instrument","comitative","time","duration","place","manner"];
const PREDS = ["DO","HAPPEN","MOVE","THINK","KNOW","WANT","DON'T-WANT","FEEL","SEE","HEAR","SAY","WORDS","TRUE","BE-SOMEWHERE","THERE-IS","BE-SPEC","IS-MINE","LIVE","DIE"];
const OPS = ["NOT","CAN","MAYBE","IF","BECAUSE","WHEN","LIKE","AFTER","BEFORE","VERY","MORE"];
const FRAMES = ["InstanceSchema","WhenTrue","RelationalSchema"];
const REFKINDS = ["SomeoneRef","SomethingRef","TimeRef","PlaceRef","ClauseRef"];
const primeId = new Map(PRIMES.map((p,i)=>[p,i]));
const predId = new Map(PREDS.map((p,i)=>[p,i]));
const opId = new Map(OPS.map((p,i)=>[p,i]));

// ---------- helpers (identical semantics to proto-kotk1-haiku.mjs) ----------
function jcs(v){if(v===null||typeof v!=="object")return JSON.stringify(v);if(Array.isArray(v))return "["+v.map(jcs).join(",")+"]";return "{"+Object.keys(v).sort().map(k=>JSON.stringify(k)+":"+jcs(v[k])).join(",")+"}";}
function nfcDeep(v){if(typeof v==="string")return v.normalize("NFC");if(Array.isArray(v))return v.map(nfcDeep);if(v!==null&&typeof v==="object"){const o={};for(const k of Object.keys(v))o[k.normalize("NFC")]=nfcDeep(v[k]);return o;}return v;}
const B32="abcdefghijklmnopqrstuvwxyz234567";
function base32(bytes){let out="",bits=0,val=0;for(const b of bytes){val=(val<<8)|b;bits+=8;while(bits>=5){out+=B32[(val>>>(bits-5))&31];bits-=5;}}if(bits>0)out+=B32[(val<<(5-bits))&31];return out;}
function mint(header,payload){const d=createHash("sha256").update(Buffer.concat([Buffer.from(header,"utf8"),Buffer.from(jcs(payload),"utf8")])).digest();return "urn:kot:b"+base32(Buffer.concat([Buffer.from([0x12,0x20]),d]));}
class W{constructor(){this.chunks=[];this.len=0;}byte(b){this.chunks.push(Buffer.from([b]));this.len+=1;}varint(n){const bs=[];let v=n;do{let b=v&0x7f;v=Math.floor(v/128);if(v>0)b|=0x80;bs.push(b);}while(v>0);this.chunks.push(Buffer.from(bs));this.len+=bs.length;}bytes(buf){this.chunks.push(buf);this.len+=buf.length;}str(s){const b=Buffer.from(s.normalize("NFC"),"utf8");this.varint(b.length);this.bytes(b);}buf(){return Buffer.concat(this.chunks);}}
class R{constructor(buf){this.b=buf;this.p=0;}byte(){return this.b[this.p++];}varint(){let m=1,v=0;for(;;){const b=this.b[this.p++];v+=(b&0x7f)*m;if(!(b&0x80))return v;m*=128;}}str(){const n=this.varint();const s=this.b.toString("utf8",this.p,this.p+n);this.p+=n;return s;}raw(n){const b=this.b.subarray(this.p,this.p+n);this.p+=n;return b;}}

// ---------- rANS (static, byte-renormalized, 12-bit) — same as proto-kotk2-entropy.mjs ----------
const PB=12, MTOT=1<<PB, RANS_L=1<<23;
function normalizeFreqs(counts){const n=counts.reduce((a,b)=>a+b,0);if(n===0)return counts.map(()=>0);const freqs=counts.map(c=>c===0?0:Math.max(1,Math.round(c/n*MTOT)));let sum=freqs.reduce((a,b)=>a+b,0);while(sum!==MTOT){const dir=sum>MTOT?-1:1;let best=-1;for(let i=0;i<freqs.length;i++){if(freqs[i]===0)continue;if(dir===-1&&freqs[i]<=1)continue;if(best<0||freqs[i]>freqs[best])best=i;}freqs[best]+=dir;sum+=dir;}return freqs;}
class Table{constructor(freqs){this.freq=freqs;this.cum=new Array(freqs.length+1).fill(0);for(let i=0;i<freqs.length;i++)this.cum[i+1]=this.cum[i]+freqs[i];this.lookup=new Uint16Array(MTOT);for(let s=0;s<freqs.length;s++)for(let j=this.cum[s];j<this.cum[s+1];j++)this.lookup[j]=s;}}
function ransEncode(pairs){let x=RANS_L;const out=[];for(let i=pairs.length-1;i>=0;i--){const [t,s]=pairs[i];const f=t.freq[s];if(!f)throw new Error("zero-freq symbol "+s);const xmax=f*(1<<19);while(x>=xmax){out.push(x%256);x=Math.floor(x/256);}x=Math.floor(x/f)*MTOT+(x%f)+t.cum[s];}const head=Buffer.from([Math.floor(x/0x1000000)&0xff,(x>>>16)&0xff,(x>>>8)&0xff,x&0xff]);out.reverse();return Buffer.concat([head,Buffer.from(out)]);}
class RansDecoder{constructor(buf){this.b=buf;this.x=buf[0]*0x1000000+buf[1]*0x10000+buf[2]*0x100+buf[3];this.p=4;}decode(t){const slot=this.x%MTOT;const s=t.lookup[slot];this.x=t.freq[s]*Math.floor(this.x/MTOT)+slot-t.cum[s];while(this.x<RANS_L)this.x=this.x*256+this.b[this.p++];return s;}}

// multi-context stream framework (two passes: tally, then emit)
class Stream{
  constructor(name,nctx){this.name=name;this.nctx=nctx;this.counts=Array.from({length:nctx},()=>[]);this.pairs=[];this.tables=null;this.n=0;}
  push(ctx,sym){if(this.tables){const t=this.tables[ctx];this.pairs.push([t,sym]);}else{const c=this.counts[ctx];c[sym]=(c[sym]||0)+1;}this.n=this.tables?this.n:this.n+1;}
  build(){this.tables=this.counts.map(c=>{const arr=Array.from(c,x=>x||0);let m=arr.length;while(m>0&&arr[m-1]===0)m--;const t=arr.slice(0,m);return t.length?new Table(normalizeFreqs(t)):null;});}
  serialize(w){w.varint(this.nctx);for(const t of this.tables){if(!t){w.varint(0);continue;}w.varint(t.freq.length);for(const f of t.freq)w.varint(f);}}
}
function deserializeStream(r){const nctx=r.varint();const tables=[];for(let i=0;i<nctx;i++){const ab=r.varint();if(ab===0){tables.push(null);continue;}const freqs=[];for(let j=0;j<ab;j++)freqs.push(r.varint());tables.push(new Table(freqs));}return tables;}

// ---------- load corpus ----------
const files=readdirSync(DIR).filter(f=>f.endsWith(".json")).sort();
const recs=[];
const extSet=new Set();
function collectExt(node){if(Array.isArray(node)){node.forEach(collectExt);return;}if(node&&typeof node==="object"){if((node.kind==="concept"||node.kind==="conceptHead")&&typeof node.id==="string")extSet.add(node.id);for(const k of Object.keys(node))collectExt(node[k]);}}
for(const f of files){
  const r=JSON.parse(readFileSync(join(DIR,f),"utf8"));
  const sid=r.id.slice("urn:haiku-tier:".length);
  if(r.schema!=="haiku-tier/1"||r.semanticStatus!=="ModelAuthored")throw new Error("dict miss "+sid);
  const rec={sid,candidateStatus:r.candidateStatus,kind:r.kind};
  for(const k of ["groundingNote","groundingRefs","moleculeDepth","record"])if(k in r)rec[k]=r[k];
  if(rec.groundingRefs)rec.groundingRefs.forEach(u=>extSet.add(u));
  if(rec.record)collectExt(rec.record);
  recs.push(rec);
}
recs.sort((a,b)=>a.sid<b.sid?-1:a.sid>b.sid?1:0);
const EXT=[...extSet].sort();
const extId=new Map(EXT.map((u,i)=>[u,i]));
const CAND=[...new Set(recs.map(r=>r.candidateStatus))].sort();
const KINDS=[...new Set(recs.map(r=>r.kind))].sort();
const candId=new Map(CAND.map((c,i)=>[c,i]));
const kindId=new Map(KINDS.map((c,i)=>[c,i]));

// ---------- strict structural validation (decides bytecode vs escape) ----------
// Replicates proto-kotk1-haiku semantics: v1's per-record self-check escapes
// any record whose encode drops/alters anything; here the same set is caught
// by exact key-set + domain validation (throw => escape). The global JCS
// byte-compare at the end proves no validator gap survived.
function keysExactly(o,req,opt=[]){const ks=Object.keys(o);for(const k of ks)if(!req.includes(k)&&!opt.includes(k))throw new Error("extra key "+k);for(const k of req)if(!(k in o))throw new Error("missing key "+k);}
function reqPrime(p){const i=primeId.get(p);if(i===undefined)throw new Error("prime "+p);return i;}
function isInt(v){return typeof v==="number"&&Number.isInteger(v);}
function validateNode(node){
  if(node===null||typeof node!=="object"||Array.isArray(node))throw new Error("node shape");
  if(node.type==="pred"){
    keysExactly(node,["type","pred","roles"]);
    if(predId.get(node.pred)===undefined)throw new Error("pred");
    if(node.roles===null||typeof node.roles!=="object"||Array.isArray(node.roles))throw new Error("roles");
    for(const k of Object.keys(node.roles)){if(!ROLES.includes(k))throw new Error("role "+k);validateNode(node.roles[k]);}
    return;
  }
  if(node.type==="op"){
    keysExactly(node,["type","op","args"]);
    if(opId.get(node.op)===undefined)throw new Error("op");
    if(!Array.isArray(node.args))throw new Error("args");
    node.args.forEach(validateNode);
    return;
  }
  switch(node.kind){
    case "sp":{
      keysExactly(node,["kind","head"],["det","quant","mods","bind","restrictedBy"]);
      if("det" in node)reqPrime(node.det);
      if("quant" in node)reqPrime(node.quant);
      if("mods" in node){if(!Array.isArray(node.mods))throw new Error("mods");for(const m of node.mods){keysExactly(m,["mod"],["intensifier"]);reqPrime(m.mod);if("intensifier" in m)reqPrime(m.intensifier);}}
      if("bind" in node&&(!isInt(node.bind)||node.bind<0))throw new Error("bind");
      const h=node.head;
      if(h===null||typeof h!=="object")throw new Error("head");
      if(h.kind==="primeHead"){keysExactly(h,["kind","prime"]);reqPrime(h.prime);}
      else if(h.kind==="refHead"){keysExactly(h,["kind","index"]);if(!isInt(h.index)||h.index<1||h.index>32)throw new Error("refHead idx");}
      else if(h.kind==="conceptHead"){keysExactly(h,["kind","id"]);if(!extId.has(h.id))throw new Error("ext");}
      else if(h.kind==="kindFrame"||h.kind==="partFrame"){keysExactly(h,["kind","of"]);validateNode(h.of);}
      else throw new Error("head kind");
      if("restrictedBy" in node)validateNode(node.restrictedBy);
      return;
    }
    case "ref": keysExactly(node,["kind","index"]);if(!isInt(node.index)||node.index<1||node.index>32)throw new Error("ref idx");return;
    case "prime": keysExactly(node,["kind","prime"]);reqPrime(node.prime);return;
    case "concept": keysExactly(node,["kind","id"]);if(!extId.has(node.id))throw new Error("ext");return;
    case "clause": keysExactly(node,["kind","clause"]);validateNode(node.clause);return;
    case "quote": keysExactly(node,["kind","clauses"]);if(!Array.isArray(node.clauses))throw new Error("qc");node.clauses.forEach(validateNode);return;
    case "temporal": keysExactly(node,["kind","op","anchor"]);if(node.op!=="AFTER"&&node.op!=="BEFORE")throw new Error("top");validateNode(node.anchor);return;
    default: throw new Error("node? "+JSON.stringify(node).slice(0,60));
  }
}
function validateAst(ex){
  keysExactly(ex,["schema","frame","clauses"],["referents"]);
  if(ex.schema!=="kot-ast/1")throw new Error("ast schema");
  if(FRAMES.indexOf(ex.frame)<0)throw new Error("frame");
  const refs=ex.referents||[];
  if(!Array.isArray(refs))throw new Error("refs");
  refs.forEach((rd,i)=>{keysExactly(rd,["index","refKind"]);if(rd.index!==i+1)throw new Error("non-dense");if(REFKINDS.indexOf(rd.refKind)<0)throw new Error("refKind");});
  if(!Array.isArray(ex.clauses))throw new Error("clauses");
  ex.clauses.forEach(validateNode);
  if("referents" in ex && ex.referents.length===0){/* fine: encoded as count 0; decode must reproduce presence */}
  return true;
}

// ---------- streams ----------
// tag alphabet: 0..18 pred, 19..29 op, 30 SP, 31 ref, 32 primeFiller, 33 concept,
// 34 clauseFiller, 35 quote, 36 tempAFTER, 37 tempBEFORE   (ctx = prev tag, START=38)
const TAG_AB=38, TAG_START=38;
// prime slot contexts: 0 filler, 1 det, 2 quant, 3 mod, 4 intensifier, 5 head
const S={
  flags:new Stream("flags",1),
  plen:new Stream("plen",1), slen:new Stream("slen",1), char:null, // built after alphabet known
  frame:new Stream("frame",1), nref:new Stream("nref",1), refkind:new Stream("refkind",1), nclause:new Stream("nclause",1),
  tag:new Stream("tag",TAG_AB+1),
  prime:new Stream("prime",6),
  mask:new Stream("mask",PREDS.length),
  nargs:new Stream("nargs",OPS.length),
  spflags:new Stream("spflags",1), nmods:new Stream("nmods",1), bind:new Stream("bind",1),
  head:new Stream("head",1), refidx:new Stream("refidx",1), ext:new Stream("ext",1),
  ngref:new Stream("ngref",1), depth:new Stream("depth",1), nquote:new Stream("nquote",1),
};
// lemma char alphabet (NFC utf8 bytes of sids)
const charSet=new Set();
const sidBufs=recs.map(r=>Buffer.from(r.sid.normalize("NFC"),"utf8"));
for(const b of sidBufs)for(const c of b)charSet.add(c);
const CHARS=[...charSet].sort((a,b)=>a-b);
const charIdx=new Map(CHARS.map((c,i)=>[c,i]));
S.char=new Stream("char",CHARS.length+1); const CHAR_START=CHARS.length;
// roleMask list (observed masks over pred clauses)
const maskSet=new Set();
(function collectMasks(n){if(Array.isArray(n)){n.forEach(collectMasks);return;}if(n&&typeof n==="object"){if(n.type==="pred"&&n.roles&&typeof n.roles==="object"&&!Array.isArray(n.roles)){let m=0;for(let i=0;i<ROLES.length;i++)if(ROLES[i] in n.roles)m|=(1<<i);maskSet.add(m);}for(const k of Object.keys(n))collectMasks(n[k]);}})(recs.map(r=>r.record).filter(Boolean));
const MASKS=[...maskSet].sort((a,b)=>a-b);
const maskIdx=new Map(MASKS.map((m,i)=>[m,i]));

// escape decision per record (v1-equivalent)
const isEsc=recs.map(r=>{if(!("record" in r))return false;try{validateAst(r.record);return false;}catch{return true;}});

// AST event traversal (encode side)
function emitNode(node){
  if(node.type==="pred"){
    const pi=predId.get(node.pred);
    S.tag.push(tagCtx,pi); tagCtx=pi;
    let m=0;const present=[];
    for(let i=0;i<ROLES.length;i++)if(ROLES[i] in node.roles){m|=(1<<i);present.push(ROLES[i]);}
    S.mask.push(pi,maskIdx.get(m));
    for(const role of present)emitNode(node.roles[role]);
    return;
  }
  if(node.type==="op"){
    const oi=opId.get(node.op);
    S.tag.push(tagCtx,19+oi); tagCtx=19+oi;
    S.nargs.push(oi,node.args.length);
    for(const a of node.args)emitNode(a);
    return;
  }
  switch(node.kind){
    case "sp":{
      S.tag.push(tagCtx,30); tagCtx=30;
      let flags=0;
      if("det" in node)flags|=1; if("quant" in node)flags|=2; if("mods" in node)flags|=4;
      if("bind" in node)flags|=8; if("restrictedBy" in node)flags|=16;
      S.spflags.push(0,flags);
      if(flags&1)S.prime.push(1,reqPrime(node.det));
      if(flags&2)S.prime.push(2,reqPrime(node.quant));
      if(flags&4){S.nmods.push(0,node.mods.length);for(const m of node.mods){S.prime.push(3,reqPrime(m.mod));S.spflags.push(0,("intensifier" in m)?1:0);if("intensifier" in m)S.prime.push(4,reqPrime(m.intensifier));}}
      if(flags&8)S.bind.push(0,node.bind);
      const h=node.head;
      if(h.kind==="primeHead"){S.head.push(0,0);S.prime.push(5,reqPrime(h.prime));}
      else if(h.kind==="refHead"){S.head.push(0,1);S.refidx.push(0,h.index-1);}
      else if(h.kind==="conceptHead"){S.head.push(0,2);S.ext.push(0,extId.get(h.id));}
      else if(h.kind==="kindFrame"){S.head.push(0,3);emitNode(h.of);}
      else {S.head.push(0,4);emitNode(h.of);}
      if(flags&16)emitNode(node.restrictedBy);
      return;
    }
    case "ref": S.tag.push(tagCtx,31); tagCtx=31; S.refidx.push(0,node.index-1); return;
    case "prime": S.tag.push(tagCtx,32); tagCtx=32; S.prime.push(0,reqPrime(node.prime)); return;
    case "concept": S.tag.push(tagCtx,33); tagCtx=33; S.ext.push(0,extId.get(node.id)); return;
    case "clause": S.tag.push(tagCtx,34); tagCtx=34; emitNode(node.clause); return;
    case "quote": S.tag.push(tagCtx,35); tagCtx=35; S.nquote.push(0,node.clauses.length); node.clauses.forEach(emitNode); return;
    case "temporal": {const t=node.op==="AFTER"?36:37; S.tag.push(tagCtx,t); tagCtx=t; emitNode(node.anchor); return;}
    default: throw new Error("emit node?");
  }
}
let tagCtx=TAG_START;
// NOTE: mods symbol above pushes reqPrime(m.mod) with a no-op mask (kept simple:
// intensifier presence rides a dedicated spflags bit-symbol right after).
function emitRecord(r,esc){
  let flags=kindId.get(r.kind)|(candId.get(r.candidateStatus)<<2);
  if("groundingNote" in r)flags|=16;
  if("groundingRefs" in r)flags|=32;
  if("moleculeDepth" in r)flags|=64;
  if("record" in r)flags|=128;
  if(esc)flags|=256;
  S.flags.push(0,flags);
  if("groundingRefs" in r){S.ngref.push(0,r.groundingRefs.length);for(const u of r.groundingRefs)S.ext.push(0,extId.get(u));}
  if("moleculeDepth" in r)S.depth.push(0,r.moleculeDepth);
  if("record" in r&&!esc){
    const ex=r.record;
    S.frame.push(0,FRAMES.indexOf(ex.frame));
    const refs=ex.referents||[];
    // presence of the (possibly empty) referents key must round-trip:
    S.nref.push(0,"referents" in ex?refs.length+1:0); // 0 = absent, n+1 = present with n
    for(const rd of refs)S.refkind.push(0,REFKINDS.indexOf(rd.refKind));
    S.nclause.push(0,ex.clauses.length);
    tagCtx=TAG_START;
    ex.clauses.forEach(emitNode);
  }
}
// lemma front-coding: shared prefix with previous sid
function emitLemmas(){
  let prev=Buffer.alloc(0);
  for(const b of sidBufs){
    let p=0;while(p<b.length&&p<prev.length&&b[p]===prev[p])p++;
    S.plen.push(0,p);S.slen.push(0,b.length-p);
    let c=CHAR_START;
    for(let i=p;i<b.length;i++){const ci=charIdx.get(b[i]);S.char.push(c,ci);c=ci;}
    prev=b;
  }
}
// pass 1: tally
emitLemmas();
recs.forEach((r,i)=>emitRecord(r,isEsc[i]));
for(const k of Object.keys(S))S[k].build();
// pass 2: emit pairs (same order)
emitLemmas();
recs.forEach((r,i)=>emitRecord(r,isEsc[i]));
const STREAM_ORDER=["flags","plen","slen","char","frame","nref","refkind","nclause","tag","prime","mask","nargs","spflags","nmods","bind","head","refidx","ext","ngref","depth","nquote"];
const blobs={};for(const k of STREAM_ORDER)blobs[k]=S[k].pairs.length?ransEncode(S[k].pairs):Buffer.alloc(0);

// ---------- kernel container ----------
const w=new W();
w.bytes(Buffer.from("KOTK2H","utf8"));
w.str("kot-haiku/1\n");
w.str(JSON.stringify({schema:"haiku-tier/1",semanticStatus:"ModelAuthored",astSchema:"kot-ast/1"}));
w.varint(CAND.length);CAND.forEach(c=>w.str(c));
w.varint(KINDS.length);KINDS.forEach(c=>w.str(c));
// EXT URN table, front-coded (sorted)
w.varint(EXT.length);
{let prev="";for(const u of EXT){let p=0;while(p<u.length&&p<prev.length&&u[p]===prev[p])p++;w.varint(p);w.str(u.slice(p));prev=u;}}
w.varint(CHARS.length);CHARS.forEach(c=>w.byte(c));
w.varint(MASKS.length);MASKS.forEach(m=>w.varint(m));
w.varint(recs.length);
const tStart=w.len;
for(const k of STREAM_ORDER)S[k].serialize(w);
const tableBytes=w.len-tStart;
for(const k of STREAM_ORDER){w.varint(blobs[k].length);w.bytes(blobs[k]);}
const kernelPacked=w.buf();
if(OUT)writeFileSync(OUT,kernelPacked);

// ---------- text segment (sidecar): notes + verbatim-JCS escapes, record order ----------
const tw=new W();
tw.bytes(Buffer.from("KOTK2T","utf8"));
let noteBytes=0,escBytes=0,nEsc=0;
recs.forEach((r,i)=>{
  if("groundingNote" in r){const b0=tw.len;tw.str(r.groundingNote);noteBytes+=tw.len-b0;}
  if(isEsc[i]){const b0=tw.len;tw.str(jcs(nfcDeep(r.record)));escBytes+=tw.len-b0;nEsc++;}
});
const textPacked=tw.buf();
if(TEXTOUT)writeFileSync(TEXTOUT,textPacked);

// ---------- decode (kernel + text) ----------
const rr=new R(kernelPacked);
rr.p+=6;
const profile=rr.str();
const consts=JSON.parse(rr.str());
const nc=rr.varint();const cand=[];for(let i=0;i<nc;i++)cand.push(rr.str());
const nk=rr.varint();const kinds=[];for(let i=0;i<nk;i++)kinds.push(rr.str());
const ne=rr.varint();const ext=[];{let prev="";for(let i=0;i<ne;i++){const p=rr.varint();const s=prev.slice(0,p)+rr.str();ext.push(s);prev=s;}}
const nch=rr.varint();const chars=[];for(let i=0;i<nch;i++)chars.push(rr.byte());
const nma=rr.varint();const masks=[];for(let i=0;i<nma;i++)masks.push(rr.varint());
const nrec=rr.varint();
const dT={};for(const k of STREAM_ORDER)dT[k]=deserializeStream(rr);
const dB={};for(const k of STREAM_ORDER){const n=rr.varint();dB[k]=n?new RansDecoder(rr.raw(n)):null;}
if(rr.p!==kernelPacked.length)throw new Error("trailing kernel bytes");
const tr=new R(textPacked);tr.p+=6;
const dec=(k,ctx=0)=>dB[k].decode(dT[k][ctx]);
// lemmas
const dSids=[];{let prev=Buffer.alloc(0);
  for(let i=0;i<nrec;i++){
    const p=dec("plen"),sl=dec("slen");
    const out=Buffer.alloc(p+sl);prev.copy(out,0,0,p);
    let c=chars.length; // CHAR_START
    for(let j=0;j<sl;j++){const ci=dB.char.decode(dT.char[c]);out[p+j]=chars[ci];c=ci;}
    dSids.push(out.toString("utf8"));prev=out;
  }}
let dTagCtx=TAG_AB;
function decNode(){
  const t=dB.tag.decode(dT.tag[dTagCtx]);dTagCtx=t;
  if(t<19){const pred=PREDS[t];const m=masks[dB.mask.decode(dT.mask[t])];const roles={};const savedOrder=[];for(let i=0;i<ROLES.length;i++)if(m&(1<<i))savedOrder.push(ROLES[i]);for(const role of savedOrder)roles[role]=decNode();return {type:"pred",pred,roles};}
  if(t<30){const oi=t-19;const op=OPS[oi];const n=dB.nargs.decode(dT.nargs[oi]);const args=[];for(let i=0;i<n;i++)args.push(decNode());return {type:"op",op,args};}
  if(t===30){
    const flags=dec("spflags");const sp={kind:"sp"};
    if(flags&1)sp.det=PRIMES[dB.prime.decode(dT.prime[1])];
    if(flags&2)sp.quant=PRIMES[dB.prime.decode(dT.prime[2])];
    if(flags&4){const n=dec("nmods");sp.mods=[];for(let i=0;i<n;i++){const m={mod:PRIMES[dB.prime.decode(dT.prime[3])]};const hasInt=dec("spflags");if(hasInt===1)m.intensifier=PRIMES[dB.prime.decode(dT.prime[4])];sp.mods.push(m);}}
    if(flags&8)sp.bind=dec("bind");
    const ht=dec("head");
    if(ht===0)sp.head={kind:"primeHead",prime:PRIMES[dB.prime.decode(dT.prime[5])]};
    else if(ht===1)sp.head={kind:"refHead",index:dec("refidx")+1};
    else if(ht===2)sp.head={kind:"conceptHead",id:ext[dec("ext")]};
    else if(ht===3)sp.head={kind:"kindFrame",of:decNode()};
    else sp.head={kind:"partFrame",of:decNode()};
    if(flags&16)sp.restrictedBy=decNode();
    return sp;
  }
  if(t===31)return {kind:"ref",index:dec("refidx")+1};
  if(t===32)return {kind:"prime",prime:PRIMES[dB.prime.decode(dT.prime[0])]};
  if(t===33)return {kind:"concept",id:ext[dec("ext")]};
  if(t===34)return {kind:"clause",clause:decNode()};
  if(t===35){const n=dec("nquote");const clauses=[];for(let i=0;i<n;i++)clauses.push(decNode());return {kind:"quote",clauses};}
  if(t===36||t===37)return {kind:"temporal",op:t===36?"AFTER":"BEFORE",anchor:decNode()};
  throw new Error("tag "+t);
}
const decoded=[];
for(let i=0;i<nrec;i++){
  const flags=dec("flags");
  const pay={sourceId:dSids[i],schema:consts.schema,semanticStatus:consts.semanticStatus,candidateStatus:cand[(flags>>2)&3],kind:kinds[flags&3]};
  if(flags&16)pay.groundingNote=tr.str();
  if(flags&32){const n=dec("ngref");pay.groundingRefs=[];for(let j=0;j<n;j++)pay.groundingRefs.push(ext[dec("ext")]);}
  if(flags&64)pay.moleculeDepth=dec("depth");
  if(flags&128){
    if(flags&256){pay.record=JSON.parse(tr.str());}
    else{
      const frame=FRAMES[dec("frame")];
      const nr=dec("nref");
      const rec={schema:consts.astSchema,frame,clauses:null};
      if(nr>0){rec.referents=[];for(let j=0;j<nr-1;j++)rec.referents.push({index:j+1,refKind:REFKINDS[dec("refkind")]});}
      const ncl=dec("nclause");const clauses=[];dTagCtx=TAG_AB;
      for(let j=0;j<ncl;j++)clauses.push(decNode());
      rec.clauses=clauses;
      if(!("referents" in rec))delete rec.referents;
      pay.record=rec;
    }
  }
  decoded.push(pay);
}
if(tr.p!==textPacked.length)throw new Error("trailing text bytes");

// ---------- verify: JCS byte-equality + URNs ----------
const minted=new Map();
try{for(const line of readFileSync(MINTED,"utf8").split("\n")){if(!line.trim())continue;const o=JSON.parse(line);minted.set(o.sourceId,o.urn);}}catch{}
let eq=0,neq=0,urnOk=0,urnBad=0,urnChecked=0;
for(let i=0;i<recs.length;i++){
  const r=recs[i];
  const orig={sourceId:r.sid,schema:"haiku-tier/1",semanticStatus:"ModelAuthored",candidateStatus:r.candidateStatus,kind:r.kind};
  for(const k of ["groundingNote","groundingRefs","moleculeDepth","record"])if(k in r)orig[k]=r[k];
  const a=jcs(nfcDeep(orig)),b=jcs(decoded[i]);
  if(a===b)eq++;else{neq++;if(neq<3){console.log("JCS MISMATCH",r.sid);console.log(" orig:",a.slice(0,200));console.log(" dec :",b.slice(0,200));}}
  if(minted.has(r.sid)){urnChecked++;const u=mint(profile,decoded[i]);if(u===minted.get(r.sid))urnOk++;else{urnBad++;if(urnBad<3)console.log("URN MISMATCH",r.sid);}}
}
console.log("kernel bytes:",kernelPacked.length,"(",(kernelPacked.length/recs.length).toFixed(1),"B/rec ) | text sidecar:",textPacked.length,"B ( notes",noteBytes,", escapes",escBytes,"in",nEsc,"records )");
console.log("total (kernel+text):",kernelPacked.length+textPacked.length);
console.log("JCS byte-equality:",eq,"of",recs.length,"(mismatches:",neq+")");
console.log("published-URN verify:",urnOk,"ok /",urnBad,"bad of",urnChecked,"checked");
if(neq>0||urnBad>0){console.error("ERR_KOTK2_ROUNDTRIP");process.exit(1);}
// per-stream report
console.log("\nper-stream (rANS blob incl 4B state; naive = fixed-width):");
let blobTotal=0;
for(const k of STREAM_ORDER){
  const st=S[k];if(!st.pairs.length)continue;
  const ab=Math.max(...st.tables.filter(Boolean).map(t=>t.freq.length));
  const naive=Math.ceil(Math.log2(Math.max(2,ab)));
  console.log(`  ${k.padEnd(8)} n=${String(st.pairs.length).padStart(6)}  ${(blobs[k].length*8/st.pairs.length).toFixed(3)} b/sym (naive ${naive}, alphabet ${ab})  blob ${blobs[k].length} B`);
  blobTotal+=blobs[k].length;
}
console.log(`  tables ${tableBytes} B; header ${tStart} B; blobs ${blobTotal} B`);
