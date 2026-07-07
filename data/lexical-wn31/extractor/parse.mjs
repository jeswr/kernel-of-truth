/**
 * WordNet 3.1 database-file parser (pure functions, zero deps).
 *
 * Format reference: wndb(5WN) / wninput(5WN), Princeton WordNet 3.1.
 * data.{noun,verb,adj,adv} line:
 *   synset_offset lex_filenum ss_type w_cnt word lex_id [word lex_id...]
 *   p_cnt [ptr...] [frames...] | gloss
 * where w_cnt is 2-digit hex, lex_id is 1-digit hex, p_cnt is 3-digit
 * decimal, each ptr is `pointer_symbol synset_offset pos source/target`
 * (source/target: 4 hex digits, 00xx/xx00 word numbers; 0000 = semantic),
 * and verb lines carry `f_cnt (+ f_num w_num)*` sentence frames before
 * the gloss separator.
 *
 * Fail-closed per repo convention: malformed input throws ERR_* codes,
 * never silently skips (docs/design-bulk-kernel.md verification bar).
 */

/** Lexicographer file names, lexnames(5WN). Index = lex_filenum. */
export const LEXFILE_NAMES = [
  'adj.all', 'adj.pert', 'adv.all', 'noun.Tops', 'noun.act',
  'noun.animal', 'noun.artifact', 'noun.attribute', 'noun.body',
  'noun.cognition', 'noun.communication', 'noun.event', 'noun.feeling',
  'noun.food', 'noun.group', 'noun.location', 'noun.motive',
  'noun.object', 'noun.person', 'noun.phenomenon', 'noun.plant',
  'noun.possession', 'noun.process', 'noun.quantity', 'noun.relation',
  'noun.shape', 'noun.state', 'noun.substance', 'noun.time',
  'verb.body', 'verb.change', 'verb.cognition', 'verb.communication',
  'verb.competition', 'verb.consumption', 'verb.contact',
  'verb.creation', 'verb.emotion', 'verb.motion', 'verb.perception',
  'verb.possession', 'verb.social', 'verb.stative', 'verb.weather',
  'adj.ppl',
];

/**
 * Pointer symbols extracted into axioms (bead kernel-of-truth-4m1 scope).
 * Everything else in the source (derivational `+`, verb-group `$`,
 * domain `;c ;r ;u` / `-c -r -u`, attribute `=`, see-also `^`,
 * participle `<`, pertainym `\`) is deliberately NOT extracted here and
 * is filed as follow-up work; parseDataLine still parses those pointers
 * (nothing is dropped at parse time), the record builder filters.
 */
export const AXIOM_RELS = {
  '@': 'hypernym',
  '@i': 'instanceHypernym',
  '~': 'hyponym',
  '~i': 'instanceHyponym',
  '#m': 'memberHolonym',
  '#s': 'substanceHolonym',
  '#p': 'partHolonym',
  '%m': 'memberMeronym',
  '%s': 'substanceMeronym',
  '%p': 'partMeronym',
  '!': 'antonym',
  '*': 'entailment',
  '>': 'cause',
  '&': 'similarTo',
};

const SS_TYPES = new Set(['n', 'v', 'a', 's', 'r']);
const PTR_POS = new Set(['n', 'v', 'a', 'r']);

function fail(code, msg) {
  const e = new Error(`${code}: ${msg}`);
  e.code = code;
  throw e;
}

/** True for the licence header lines at the top of every db file. */
export function isHeaderLine(line) {
  return line.startsWith('  ');
}

/**
 * Parse one data.{noun,verb,adj,adv} record line.
 * Returns { offset, lexFilenum, lexFile, ssType, words, pointers, frames, gloss }.
 * words: [{ lemma, marker|null, lexId }] — lemma keeps source case and
 *   underscores; adjective syntactic markers `(p) (a) (ip)` are split out.
 * pointers: [{ sym, offset, pos, srcWord, tgtWord }] (word numbers 0 when
 *   the pointer is semantic, i.e. source/target === "0000").
 */
export function parseDataLine(line) {
  const bar = line.indexOf(' | ');
  if (bar < 0) fail('ERR_WN_NO_GLOSS', `no gloss separator: ${line.slice(0, 60)}`);
  const gloss = line.slice(bar + 3).replace(/\s+$/, '');
  const tokens = line.slice(0, bar).trim().split(/\s+/);
  let i = 0;
  const next = (what) => {
    if (i >= tokens.length) fail('ERR_WN_TRUNCATED', `expected ${what}`);
    return tokens[i++];
  };

  const offset = next('synset_offset');
  if (!/^\d{8}$/.test(offset)) fail('ERR_WN_OFFSET', offset);
  const lexFilenum = parseInt(next('lex_filenum'), 10);
  if (!(lexFilenum >= 0 && lexFilenum < LEXFILE_NAMES.length)) {
    fail('ERR_WN_LEXFILE', String(lexFilenum));
  }
  const ssType = next('ss_type');
  if (!SS_TYPES.has(ssType)) fail('ERR_WN_SSTYPE', ssType);

  const wCntTok = next('w_cnt');
  if (!/^[0-9a-f]{2}$/.test(wCntTok)) fail('ERR_WN_WCNT', wCntTok);
  const wCnt = parseInt(wCntTok, 16);
  if (wCnt < 1) fail('ERR_WN_WCNT', wCntTok);
  const words = [];
  for (let w = 0; w < wCnt; w++) {
    const raw = next('word');
    const m = raw.match(/^(.*?)(\((p|a|ip)\))?$/);
    const lexIdTok = next('lex_id');
    if (!/^[0-9a-f]{1,2}$/.test(lexIdTok)) fail('ERR_WN_LEXID', lexIdTok);
    words.push({
      lemma: m[1],
      marker: m[3] ?? null,
      lexId: parseInt(lexIdTok, 16),
    });
  }

  const pCntTok = next('p_cnt');
  if (!/^\d{3}$/.test(pCntTok)) fail('ERR_WN_PCNT', pCntTok);
  const pCnt = parseInt(pCntTok, 10);
  const pointers = [];
  for (let p = 0; p < pCnt; p++) {
    const sym = next('pointer_symbol');
    const pOffset = next('ptr_offset');
    if (!/^\d{8}$/.test(pOffset)) fail('ERR_WN_PTR_OFFSET', pOffset);
    const pos = next('ptr_pos');
    if (!PTR_POS.has(pos)) fail('ERR_WN_PTR_POS', pos);
    const st = next('source/target');
    if (!/^[0-9a-f]{4}$/.test(st)) fail('ERR_WN_PTR_ST', st);
    pointers.push({
      sym,
      offset: pOffset,
      pos,
      srcWord: parseInt(st.slice(0, 2), 16),
      tgtWord: parseInt(st.slice(2), 16),
    });
  }

  // Verb sentence frames: f_cnt (+ f_num w_num)*
  const frames = [];
  if (i < tokens.length && ssType === 'v') {
    const fCntTok = next('f_cnt');
    if (!/^\d{2}$/.test(fCntTok)) fail('ERR_WN_FCNT', fCntTok);
    const fCnt = parseInt(fCntTok, 10);
    for (let f = 0; f < fCnt; f++) {
      if (next('+') !== '+') fail('ERR_WN_FRAME', 'missing +');
      frames.push({
        frame: parseInt(next('f_num'), 10),
        word: parseInt(next('w_num'), 16),
      });
    }
  }
  if (i !== tokens.length) {
    fail('ERR_WN_TRAILING', `${tokens.length - i} unconsumed tokens at ${offset}`);
  }

  return {
    offset,
    lexFilenum,
    lexFile: LEXFILE_NAMES[lexFilenum],
    ssType,
    words,
    pointers,
    frames,
    gloss,
  };
}

/**
 * Parse one index.{noun,verb,adj,adv} line:
 *   lemma pos synset_cnt p_cnt [ptr_symbol...] sense_cnt tagsense_cnt synset_offset [...]
 * Returns { lemma, pos, offsets } (offsets in sense order: most frequent first).
 */
export function parseIndexLine(line) {
  const tokens = line.trim().split(/\s+/);
  let i = 0;
  const lemma = tokens[i++];
  const pos = tokens[i++];
  if (!PTR_POS.has(pos)) fail('ERR_WN_IDX_POS', `${lemma} ${pos}`);
  const synsetCnt = parseInt(tokens[i++], 10);
  const pCnt = parseInt(tokens[i++], 10);
  i += pCnt; // pointer symbols this lemma has in this pos — not needed
  i += 2; // sense_cnt (== synset_cnt), tagsense_cnt
  const offsets = tokens.slice(i);
  if (offsets.length !== synsetCnt || offsets.some((o) => !/^\d{8}$/.test(o))) {
    fail('ERR_WN_IDX_OFFSETS', lemma);
  }
  return { lemma, pos, offsets };
}

/**
 * Synset record id. Uses the DATA-FILE pos (n/v/a/r) — satellite synsets
 * (ss_type "s") live in data.adj and are referenced by pointers with pos
 * "a", so the id space must be the file's, with ssType kept as a field.
 */
export function synsetId(filePos, offset) {
  return `urn:lexical-wn31:${filePos}-${offset}`;
}
