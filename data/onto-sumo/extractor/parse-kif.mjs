/**
 * SUO-KIF reader (kernel-of-truth onto-sumo tier). Zero deps.
 *
 * SUMO is a set of .kif files of top-level S-expressions (SUO-KIF). We do NOT
 * attempt any semantic translation (per the directive and the mm-canonical
 * doctrine of data/math-mm): we tokenise, read balanced forms, and re-serialise
 * each to a deterministic canonical one-line string.
 *
 * Reader rules:
 *   - ";" begins a line comment (ignored), EXCEPT inside a "..." string.
 *   - "..." string with \\ and \" escapes; may span source lines.
 *   - atoms are maximal runs of non-whitespace, non-paren, non-quote,
 *     non-semicolon characters (symbols, variables ?x @row, =>, <=>, numbers).
 *
 * Nodes: { list: Node[] } | { atom: string } | { str: string }.
 * Fail closed: unbalanced parens / unterminated strings throw ERR_KIF_*.
 */

export function tokenize(text) {
  const toks = [];
  let i = 0;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    if (c === ';') { // line comment to EOL
      while (i < n && text[i] !== '\n') i++;
      continue;
    }
    if (c === ' ' || c === '\t' || c === '\r' || c === '\n') { i++; continue; }
    if (c === '(') { toks.push({ t: '(' }); i++; continue; }
    if (c === ')') { toks.push({ t: ')' }); i++; continue; }
    if (c === '"') {
      let s = '';
      i++;
      while (i < n) {
        const d = text[i];
        if (d === '\\') { s += (text[i + 1] === 'n' ? '\n' : text[i + 1] === 't' ? '\t' : text[i + 1]); i += 2; continue; }
        if (d === '"') { i++; break; }
        s += d;
        i++;
        if (i >= n) throw new Error(`ERR_KIF_STRING: unterminated string near: ${s.slice(0, 60)}`);
      }
      toks.push({ t: 'str', v: s });
      continue;
    }
    // atom
    let a = '';
    while (i < n) {
      const d = text[i];
      if (d === ' ' || d === '\t' || d === '\r' || d === '\n' || d === '(' || d === ')' || d === '"' || d === ';') break;
      a += d;
      i++;
    }
    toks.push({ t: 'atom', v: a });
  }
  return toks;
}

/** Read all top-level forms from a token stream. */
export function readForms(toks) {
  const forms = [];
  let i = 0;
  function readForm() {
    const tok = toks[i];
    if (!tok) throw new Error('ERR_KIF_EOF: unexpected end of input');
    if (tok.t === '(') {
      i++;
      const list = [];
      while (i < toks.length && toks[i].t !== ')') list.push(readForm());
      if (i >= toks.length) throw new Error('ERR_KIF_PAREN: unbalanced "("');
      i++; // consume ')'
      return { list };
    }
    if (tok.t === ')') throw new Error('ERR_KIF_PAREN: unexpected ")"');
    if (tok.t === 'str') { i++; return { str: tok.v }; }
    i++;
    return { atom: tok.v };
  }
  while (i < toks.length) forms.push(readForm());
  return forms;
}

export function parseKif(text) {
  return readForms(tokenize(text));
}

/** Deterministic canonical one-line serialisation of a node. */
export function canonical(node) {
  if (node.atom !== undefined) return node.atom;
  if (node.str !== undefined) {
    const esc = node.str.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\t/g, '\\t');
    return `"${esc}"`;
  }
  return `(${node.list.map(canonical).join(' ')})`;
}

/** Operator (head atom) of a form, or null if the head is not an atom. */
export function op(node) {
  if (!node.list || node.list.length === 0) return null;
  const h = node.list[0];
  return h.atom !== undefined ? h.atom : null;
}

/** A SUMO term = an atom that is not a variable (?x / @row) and not a number. */
export function isTerm(atom) {
  if (typeof atom !== 'string' || atom.length === 0) return false;
  if (atom[0] === '?' || atom[0] === '@') return false;
  if (/^-?[0-9]/.test(atom)) return false;
  // logical / builtin operators are not domain terms
  return true;
}

const LOGICAL_OPS = new Set(['=>', '<=>', 'and', 'or', 'not', 'forall', 'exists', 'equal']);

/** Collect all distinct SUMO terms mentioned anywhere in a node (sorted). */
export function mentionedTerms(node, out = new Set()) {
  if (node.atom !== undefined) {
    if (isTerm(node.atom) && !LOGICAL_OPS.has(node.atom)) out.add(node.atom);
  } else if (node.list) {
    for (const c of node.list) mentionedTerms(c, out);
  }
  return out;
}
