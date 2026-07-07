/**
 * FrameNet 1.7 XML reader (kernel-of-truth onto-framenet tier). Zero deps.
 *
 * FrameNet ships regular, machine-generated XML. We parse ONLY the freely
 * licensed frame metadata (frame definitions, frame elements, lexical-unit
 * names, frame-to-frame relations) — NOT the annotated corpus (lu/ fulltext/).
 * The files are attribute-simple (no quotes inside attribute values, no CDATA
 * in attributes), so a targeted tag scanner suffices; fail closed on surprises.
 */

const ENT = { lt: '<', gt: '>', amp: '&', quot: '"', apos: "'", nbsp: ' ' };
export function decodeEntities(s) {
  return s.replace(/&(#x?[0-9a-fA-F]+|[a-zA-Z]+);/g, (m, e) => {
    if (e[0] === '#') {
      const code = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : m;
    }
    return ENT[e] !== undefined ? ENT[e] : m;
  });
}

/** Parse an XML start-tag's attribute string into an object. */
export function attrs(inner) {
  const out = {};
  for (const m of inner.matchAll(/([\w:.-]+)="([^"]*)"/g)) out[m[1]] = decodeEntities(m[2]);
  return out;
}

/**
 * Clean a FrameNet <definition> body to plain prose: decode entities, cut at
 * the first <ex> example, drop <def-root>/<fen>/<fex>/<t> inline markup,
 * collapse whitespace.
 */
export function cleanDefinition(rawInner) {
  let s = decodeEntities(rawInner);
  const ex = s.indexOf('<ex>');
  if (ex >= 0) s = s.slice(0, ex);
  s = s.replace(/<\/?def-root>/g, '').replace(/<[^>]*>/g, '');
  return s.replace(/\s+/g, ' ').trim();
}

/** All top-level (non-nested-FE) <definition>…</definition> not inside <FE>. */
export function frameLevelDefinition(xml) {
  // The frame's own definition is the FIRST <definition> in the file.
  const m = xml.match(/<definition>([\s\S]*?)<\/definition>/);
  return m ? cleanDefinition(m[1]) : '';
}

/** Parse a single frame/*.xml file. */
export function parseFrameFile(xml) {
  const rootM = xml.match(/<frame\b([^>]*)>/);
  if (!rootM) throw new Error('ERR_FN_FRAME: no <frame> root');
  const root = attrs(rootM[1]);
  if (!root.name || !root.ID) throw new Error('ERR_FN_FRAME: frame missing name/ID');

  const definition = frameLevelDefinition(xml);

  // Frame elements: each <FE ...> start tag, with its own following <definition>.
  const fes = [];
  const feDefs = {};
  // Self-closing alternative FIRST so a childless <FE .../> is not mistaken for
  // an open tag that greedily swallows the next </FE>.
  const feRe = /<FE\b([^>]*?)\/>|<FE\b([^>]*?)>([\s\S]*?)<\/FE>/g;
  let fm;
  while ((fm = feRe.exec(xml)) !== null) {
    const selfClose = fm[1] !== undefined;
    const a = attrs(selfClose ? fm[1] : fm[2]);
    if (!a.name || !a.coreType) throw new Error(`ERR_FN_FE: FE missing name/coreType in ${root.name}`);
    fes.push({ name: a.name, abbrev: a.abbrev || '', coreType: a.coreType, feId: Number(a.ID) });
    const body = selfClose ? '' : (fm[3] || '');
    const dm = body.match(/<definition>([\s\S]*?)<\/definition>/);
    if (dm) { const d = cleanDefinition(dm[1]); if (d) feDefs[a.name] = d; }
  }

  // Lexical units: <lexUnit ...> start tags (names only; NO annotated sentences).
  const lus = [];
  const luRe = /<lexUnit\b([^>]*?)>/g;
  let lm;
  while ((lm = luRe.exec(xml)) !== null) {
    const a = attrs(lm[1]);
    if (a.name) lus.push({ name: a.name, pos: a.POS || '', luId: Number(a.ID) });
  }

  return { name: root.name, id: Number(root.ID), definition, fes, feDefs, lus };
}

/**
 * Parse frRelation.xml -> array of typed frame-relation edges with FE mappings.
 * Structure: <frameRelationType name=..> <frameRelation ..> <FERelation ../> ...
 */
export function parseFrameRelations(xml) {
  const tagRe = /<(\/?)([\w:.-]+)([^>]*?)(\/?)>/g;
  const out = [];
  let curType = null;
  let curRel = null;
  let m;
  while ((m = tagRe.exec(xml)) !== null) {
    const closing = m[1] === '/';
    const name = m[2];
    const selfClose = m[4] === '/';
    if (name === 'frameRelationType') {
      if (closing) { curType = null; }
      else { curType = attrs(m[3]).name || null; }
      continue;
    }
    if (name === 'frameRelation') {
      if (closing) { if (curRel) { out.push(curRel); curRel = null; } continue; }
      const a = attrs(m[3]);
      curRel = {
        relationType: curType,
        subFrame: a.subFrameName, subFrameId: Number(a.subID),
        superFrame: a.superFrameName, superFrameId: Number(a.supID),
        relId: Number(a.ID), feMappings: [],
      };
      if (selfClose) { out.push(curRel); curRel = null; }
      continue;
    }
    if (name === 'FERelation' && curRel) {
      const a = attrs(m[3]);
      curRel.feMappings.push({ subFE: a.subFEName, superFE: a.superFEName });
    }
  }
  return out;
}
