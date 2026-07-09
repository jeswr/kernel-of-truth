/**
 * Streaming / chunk-ingest primitives for the onto-obo extractor
 * (kernel-of-truth-1mv0). The whole-file path in `extract.mjs` parses an entire
 * source into an in-memory `stanzas[]` array (one object-per-stanza, each with a
 * tags[] of [tag,value] pairs). That is fine up to ~95k records but OOMs on the
 * 2-core / 7.6 GB box for the large OBO sources the coverage plan holds — ChEBI
 * (~160k terms / 270 MB) and NCBITaxon (~2.5M terms / 661 MB): the parsed object
 * graph is 10-30x the raw bytes.
 *
 * This module reads a source in fixed-size chunks off disk and assembles ONE
 * stanza at a time, invoking `onStanza` per stanza. Peak memory is O(one stanza
 * + one chunk buffer + whatever the caller retains), independent of file size —
 * so a caller that retains only lightweight per-id metadata (id, type, obsolete)
 * stays flat as term count grows.
 *
 * The line state machine here MIRRORS `parseObo` in `parse-obo.mjs` EXACTLY
 * (same \r handling, same blank/`!`-comment skip, same `^\[Word\]$` stanza-header
 * rule, same `indexOf(':')` tag/value split, same fail-closed ERR_OBO_* throws).
 * That equivalence is not asserted by construction — it is PROVEN in
 * `chunk-ingest.test.mjs` (feed identical text through `parseObo` and
 * `streamStanzas`; the stanza arrays + header must be byte-for-byte identical, on
 * synthetic fixtures AND on a real slice of a committed source). If the two ever
 * diverge that test fails. Zero external deps (node:fs + node:string_decoder,
 * both built-in); UTF-8 multibyte sequences that straddle a chunk boundary are
 * handled by StringDecoder.
 */
import { openSync, readSync, closeSync } from 'node:fs';
import { StringDecoder } from 'node:string_decoder';

const STANZA_HEADER_RE = /^\[([A-Za-z]+)\]$/;
const DEFAULT_CHUNK = 1 << 20; // 1 MiB read buffer

/**
 * Stream `path` stanza-by-stanza.
 *   onStanza(stanza)  called once per completed [..] stanza: {type, tags:[[t,v]]}
 *                     — SAME shape parseObo produces (order + multiplicity kept).
 *   onHeader(tags)    (optional) called once at EOF with the file header tags
 *                     ([tag,value] pairs before the first stanza), like parseObo.
 *   hash              (optional) a node:crypto Hash; every RAW byte read is
 *                     fed to it, so `hash.digest('hex')` equals sha256(readFileSync)
 *                     — lets the caller fail-closed on a source-hash mismatch
 *                     WITHOUT loading the whole file (ERR_SOURCE_HASH discipline).
 * Fail-closed: bad stanza header -> ERR_OBO_STANZA; a non-blank, non-comment,
 * non-stanza line with no colon -> ERR_OBO_TAG (identical to parseObo).
 */
export function streamStanzas(path, { onStanza, onHeader, hash, chunkBytes = DEFAULT_CHUNK } = {}) {
  if (typeof onStanza !== 'function') throw new Error('ERR_STREAM_USAGE: onStanza required');
  const header = [];
  let curType = null;
  let curTags = null; // null => still in header

  // Per-line handler, byte-for-byte mirroring parse-obo.mjs parseObo().
  function onLine(line) {
    if (line.endsWith('\r')) line = line.slice(0, -1);
    const trimmed = line.trim();
    if (trimmed === '') return;
    if (trimmed.startsWith('!')) return; // comment line
    if (trimmed[0] === '[') {
      if (curTags !== null) onStanza({ type: curType, tags: curTags }); // flush previous
      const m = trimmed.match(STANZA_HEADER_RE);
      if (!m) throw new Error(`ERR_OBO_STANZA: bad stanza header line: ${trimmed}`);
      curType = m[1];
      curTags = [];
      return;
    }
    const ci = line.indexOf(':');
    if (ci < 0) throw new Error(`ERR_OBO_TAG: no colon: ${line.slice(0, 80)}`);
    const tag = line.slice(0, ci).trim();
    const value = line.slice(ci + 1).trim();
    if (curTags === null) header.push([tag, value]);
    else curTags.push([tag, value]);
  }

  const fd = openSync(path, 'r');
  try {
    const buf = Buffer.allocUnsafe(chunkBytes);
    const decoder = new StringDecoder('utf8');
    let pending = '';
    let n;
    while ((n = readSync(fd, buf, 0, chunkBytes, null)) > 0) {
      if (hash) hash.update(buf.subarray(0, n));
      pending += decoder.write(buf.subarray(0, n));
      let start = 0;
      let nl;
      while ((nl = pending.indexOf('\n', start)) >= 0) {
        onLine(pending.slice(start, nl));
        start = nl + 1;
      }
      pending = start > 0 ? pending.slice(start) : pending;
    }
    pending += decoder.end();
    if (pending.length) onLine(pending); // final line with no trailing newline
    if (curTags !== null) onStanza({ type: curType, tags: curTags }); // flush last stanza
  } finally {
    closeSync(fd);
  }
  if (onHeader) onHeader(header);
  return header;
}

/**
 * A deterministic, provenance-recorded SUBSET/FILTER policy for a streamed
 * source (the plan's "chunk/filter" for NCBITaxon). Returns a predicate
 * `keep(meta)` over lightweight per-stanza metadata
 * `{ oboId, type, obsolete, parents }` (parents = is_a target oboIds, present
 * only when the policy needs them). The SAME predicate is applied at the
 * metadata pre-scan (so ownership/resolver see only kept ids) and at emit (so
 * only kept records are written) — consistency is what keeps the two passes in
 * agreement (proven in chunk-ingest.test.mjs).
 *
 * Policies implemented here (all pure functions of the id + policy params, hence
 * deterministic and re-recordable in provenance):
 *   - undefined | {policy:'all'}                 keep everything (ChEBI: whole).
 *   - {policy:'id-list', ids:[...]}              keep iff oboId in the list.
 *   - {policy:'curie-prefix', prefix:'CHEBI'}    keep iff CURIE prefix matches.
 *   - {policy:'numeric-mod', mod, eq}            keep iff numeric local-part % mod
 *                                                === eq. DEMONSTRATION-ONLY (used by
 *                                                the proof to show the filter is
 *                                                applied identically in both passes);
 *                                                NOT is_a-closed, so NOT a shippable
 *                                                subset on its own.
 *
 * NOTE (design, not implemented here — see the 1mv0 report): a shippable
 * NCBITaxon subset must be **is_a-closed** so the taxonomy backbone stays
 * complete (validate.mjs treats a dangling is_a target as FATAL). The natural
 * closed policies are `referenced-by-corpus` (seed = the taxa other shards
 * already cite — MEASURED 1,083 distinct NCBITaxon refs today — plus their is_a
 * ancestors) and `is_a-closure-of-seeds`. Both are streamable: pass A additionally
 * collects id->is_a parents (bounded by kept-id count), then the closure is
 * computed before emit. The SPECIFIC seed set is a curation decision left to the
 * maintainer/coordinator (boundary-stop), not frozen here.
 */
export function makeSubsetFilter(subset) {
  if (!subset || subset.policy === 'all') {
    const f = () => true;
    f.needsParents = false;
    return f;
  }
  // A restricting policy subsets the TERM set only; the relation vocabulary
  // (Typedefs) is ALWAYS retained, because it is shared and is required to
  // resolve the differentiae of any kept class (dropping it throws
  // ERR_OBO_REL_UNRESOLVED). `subsetFilteredSkipped` therefore counts filtered
  // Terms only.
  let termPred;
  if (subset.policy === 'id-list') {
    const set = new Set(subset.ids || []);
    termPred = (m) => set.has(m.oboId);
  } else if (subset.policy === 'curie-prefix') {
    const p = subset.prefix;
    termPred = (m) => {
      const i = m.oboId.indexOf(':');
      return (i < 0 ? '' : m.oboId.slice(0, i)) === p;
    };
  } else if (subset.policy === 'numeric-mod') {
    const { mod, eq } = subset;
    if (!Number.isInteger(mod) || mod <= 0 || !Number.isInteger(eq)) {
      throw new Error(`ERR_SUBSET_POLICY: numeric-mod needs integer mod>0 + eq`);
    }
    termPred = (m) => {
      const digits = m.oboId.replace(/^[^:]*:/, '').replace(/[^0-9]/g, '');
      if (digits === '') return false;
      return Number(digits) % mod === eq;
    };
  } else {
    throw new Error(`ERR_SUBSET_POLICY: unknown subset policy ${JSON.stringify(subset.policy)}`);
  }
  const f = (m) => m.type === 'Typedef' || termPred(m);
  f.needsParents = false;
  return f;
}
