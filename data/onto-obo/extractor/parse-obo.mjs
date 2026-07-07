/**
 * OBO 1.2/1.4 flat-file parser (kernel-of-truth onto-obo tier).
 *
 * Line-oriented, zero deps. Parses the OBO stanza format used by BFO, RO and
 * GO into a header + a list of stanzas, each stanza a {type, tags[]} where
 * tags[] preserves order and multiplicity (many OBO tags repeat: is_a,
 * intersection_of, synonym, ...).
 *
 * We only *tokenise* here; semantic assembly (genus/differentia, axioms,
 * annotations) lives in extract.mjs. Fail closed: a malformed tag line throws
 * ERR_OBO_TAG so re-extraction cannot silently drop content.
 *
 * References for the format: OBO Flat File Format spec 1.4
 *   https://owlcollab.github.io/oboformat/doc/GO.format.obo-1_4.html
 */

/** CURIE test: PREFIX:LOCAL with the usual OBO id characters. */
const CURIE_RE = /^[A-Za-z0-9][A-Za-z0-9_.-]*:[A-Za-z0-9][A-Za-z0-9_.:-]*$/;

/** Tags whose value is a single id (optionally with " ! label" and "{mods}"). */
export const ID_TAGS = new Set([
  'is_a', 'disjoint_from', 'domain', 'range', 'inverse_of',
  'transitive_over', 'consider', 'replaced_by', 'alt_id', 'union_of',
  'equivalent_to',
]);

/** Boolean relation-characteristic tags (Typedef). */
export const BOOL_TAGS = new Set([
  'is_transitive', 'is_symmetric', 'is_reflexive', 'is_anti_symmetric',
  'is_asymmetric', 'is_functional', 'is_inverse_functional', 'is_obsolete',
  'is_cyclic', 'is_metadata_tag', 'is_class_level',
]);

/**
 * Normalise an OBO id (CURIE or bare relation name) to our URN namespace.
 * GO:0000018 -> urn:onto-obo:GO_0000018 ; regulates -> urn:onto-obo:regulates
 */
export function toUrn(id) {
  if (typeof id !== 'string' || id.length === 0) {
    throw new Error(`ERR_OBO_ID: empty id`);
  }
  const local = id.includes(':') ? id.replace(/:/g, '_') : id;
  return `urn:onto-obo:${local}`;
}

export function isCurie(id) {
  return CURIE_RE.test(id);
}

/** CURIE prefix (GO:0000018 -> "GO"); bare names -> "" (no prefix). */
export function curiePrefix(id) {
  const i = id.indexOf(':');
  return i < 0 ? '' : id.slice(0, i);
}

/**
 * Strip a trailing " ! human label" comment and a trailing "{...}" modifier
 * block from an id-bearing value, returning the bare token(s) as a string.
 */
export function stripIdValue(v) {
  let s = v;
  const bang = s.indexOf(' ! ');
  if (bang >= 0) s = s.slice(0, bang);
  s = s.replace(/\s*\{.*\}\s*$/, '');
  return s.trim();
}

/**
 * Parse a leading OBO quoted string ("...") honouring \\ , \" , \n , \t
 * escapes. Returns {text, rest} where rest is what follows the closing quote,
 * or null if v does not start with a quote.
 */
export function parseQuoted(v) {
  if (v[0] !== '"') return null;
  let out = '';
  let i = 1;
  for (; i < v.length; i++) {
    const c = v[i];
    if (c === '\\') {
      const n = v[i + 1];
      out += n === 'n' ? '\n' : n === 't' ? '\t' : n;
      i++;
      continue;
    }
    if (c === '"') break;
    out += c;
  }
  if (i >= v.length) throw new Error(`ERR_OBO_QUOTE: unterminated string: ${v.slice(0, 60)}`);
  return { text: out, rest: v.slice(i + 1).trim() };
}

/** Extract the [xref, ...] bracket list from a def/synonym remainder. */
export function parseXrefs(rest) {
  const m = rest.match(/\[(.*)\]\s*$/);
  if (!m || m[1].trim() === '') return [];
  // Split on commas not inside a URL-ish token; OBO xrefs are comma+space sep.
  return m[1].split(',').map((x) => x.trim()).filter(Boolean);
}

/**
 * Parse a def: value -> {text, xrefs}.
 */
export function parseDef(v) {
  const q = parseQuoted(v);
  if (!q) throw new Error(`ERR_OBO_DEF: def not quoted: ${v.slice(0, 60)}`);
  return { text: q.text, xrefs: parseXrefs(q.rest) };
}

/**
 * Parse a synonym: value -> {text, scope, type?}.
 * Form: "text" SCOPE [xrefs]  |  "text" SCOPE SYN_TYPE [xrefs]
 */
export function parseSynonym(v) {
  const q = parseQuoted(v);
  if (!q) throw new Error(`ERR_OBO_SYN: synonym not quoted: ${v.slice(0, 60)}`);
  const before = q.rest.replace(/\[.*\]\s*$/, '').trim();
  const toks = before.length ? before.split(/\s+/) : [];
  const out = { text: q.text };
  if (toks[0]) out.scope = toks[0];
  if (toks[1]) out.type = toks[1];
  return out;
}

/**
 * Split an OBO file's text into { header: tags[], stanzas: [{type, tags[]}] }.
 * tags is an array of [tag, value] pairs in file order.
 */
export function parseObo(text) {
  const lines = text.split('\n');
  const header = [];
  const stanzas = [];
  let cur = null; // current stanza tags array, or null (in header)
  let curType = null;

  for (let ln = 0; ln < lines.length; ln++) {
    let line = lines[ln];
    if (line.endsWith('\r')) line = line.slice(0, -1);
    const trimmed = line.trim();
    if (trimmed === '') continue;
    if (trimmed.startsWith('!')) continue; // comment line
    if (trimmed[0] === '[') {
      const m = trimmed.match(/^\[([A-Za-z]+)\]$/);
      if (!m) throw new Error(`ERR_OBO_STANZA: bad stanza header line ${ln + 1}: ${trimmed}`);
      curType = m[1];
      cur = [];
      stanzas.push({ type: curType, tags: cur });
      continue;
    }
    const ci = line.indexOf(':');
    if (ci < 0) throw new Error(`ERR_OBO_TAG: no colon on line ${ln + 1}: ${line.slice(0, 80)}`);
    const tag = line.slice(0, ci).trim();
    let value = line.slice(ci + 1).trim();
    // Drop an inline trailing " ! comment" ONLY later per-tag; keep raw here.
    if (cur === null) header.push([tag, value]);
    else cur.push([tag, value]);
  }
  return { header, stanzas };
}

/** Collect a stanza's tags into a Map<tag, string[]> preserving order. */
export function tagMap(stanza) {
  const m = new Map();
  for (const [t, v] of stanza.tags) {
    if (!m.has(t)) m.set(t, []);
    m.get(t).push(v);
  }
  return m;
}
