/**
 * Compositional roll-up: invented-composite identity (URN mint) and the
 * system-side invented-concept dictionary (idea B, docs/next/io-compression-ideas.md
 * §3.2–3.3; bead kernel-of-truth-5iu).
 *
 * Identity scheme — docs/design-hash-input.md, byte-compatible with
 * tools/mint/src/{jcs,hash,mint-core}.ts (singleton path):
 *
 *   payload      = the kot-ast/1 explication object (identity payload; the
 *                  same convention as data/kernel-v0/manifest.json:
 *                  "Identity = the kot-ast/1 `explication` object")
 *   hash input   = UTF8("kot-ast/1\n") || JCS(nfcDeep(payload))   (RFC 8785)
 *   digest       = sha2-256(hash input)
 *   multihash    = 0x12 || 0x20 || digest                          [34 bytes]
 *   URN          = "urn:kot:" + 'b' + base32(multihash)  (RFC 4648 lower, no pad)
 *
 * Invented composites are always SINGLETON mints: a composite AST references
 * other concepts only by already-minted URN strings (ConceptRef ids), never
 * by unminted intra-batch placeholders, so the cyclic-SCC machinery of
 * mint-core is out of scope here by construction.
 *
 * The dictionary is SYSTEM-SIDE and exact-by-id (io-compression-ideas.md §3.3):
 * URN -> canonical AST (+ pinned rendered text). It never enters an LLM
 * context, and no cosine/nearest-neighbour step exists anywhere in this path
 * (X3 ban respected structurally). Expansion failure is a hard error
 * (fail closed, ERR_DICT_UNKNOWN_URN) — there is no approximate path.
 *
 * This module is additive: it does not alter the encoder content-hash pin
 * (contentHash.ts covers {schema, algorithm, D, codebook, weighting} only).
 */

import { createHash } from 'node:crypto';
import type { Explication } from './ast.js';
import { canonicalJson } from './ast.js';
import { validateExplication } from './validate.js';
import { renderExplication } from './render.js';

/** In-band profile header (docs/design-hash-input.md; data/kernel-v0 manifest). */
export const KOT_AST_PROFILE_HEADER = 'kot-ast/1\n' as const;

// ---------------------------------------------------------------------------
// RFC 8785 (JCS) + kot-profile NFC pre-normalization — mirrors
// tools/mint/src/jcs.ts byte-for-byte on the value domain of kot-ast/1
// payloads (strings, integers, arrays, objects; `undefined` object members
// are treated as absent, matching ast.ts canonicalJson).
// ---------------------------------------------------------------------------

const ESCAPES: Record<string, string> = {
  '"': '\\"',
  '\\': '\\\\',
  '\b': '\\b',
  '\t': '\\t',
  '\n': '\\n',
  '\f': '\\f',
  '\r': '\\r',
};

/** RFC 8785 §3.2.2.2 string serialization; lone surrogates fail closed. */
function jcsString(s: string): string {
  let out = '"';
  for (let i = 0; i < s.length; i++) {
    const cu = s.charCodeAt(i);
    if (cu >= 0xd800 && cu <= 0xdbff) {
      const next = i + 1 < s.length ? s.charCodeAt(i + 1) : 0;
      if (next < 0xdc00 || next > 0xdfff) throw new Error(`ERR_JCS_LONE_SURROGATE at index ${i}`);
      out += s[i]! + s[i + 1]!;
      i++;
      continue;
    }
    if (cu >= 0xdc00 && cu <= 0xdfff) throw new Error(`ERR_JCS_LONE_SURROGATE at index ${i}`);
    const ch = s[i]!;
    const esc = ESCAPES[ch];
    if (esc !== undefined) out += esc;
    else if (cu < 0x20) out += '\\u' + cu.toString(16).padStart(4, '0');
    else out += ch;
  }
  return out + '"';
}

/** RFC 8785 §3.2.2.3 number serialization (ES Number::toString). */
function jcsNumber(n: number): string {
  if (!Number.isFinite(n)) throw new Error(`ERR_JCS_NONFINITE: ${n}`);
  if (Object.is(n, -0)) return '0';
  return String(n);
}

/**
 * NFC-normalize every string (values AND property names) then serialize per
 * RFC 8785. Composes the two steps of docs/design-hash-input.md ("UTF-8 NFC +
 * RFC 8785 JCS") in one recursive walk; post-NFC key collisions fail closed
 * (ERR_NFC_DUP_KEY), exactly as tools/mint/src/jcs.ts.
 */
export function jcsCanonicalize(value: unknown): string {
  if (value === null) return 'null';
  const t = typeof value;
  if (t === 'boolean') return value ? 'true' : 'false';
  if (t === 'number') return jcsNumber(value as number);
  if (t === 'string') return jcsString((value as string).normalize('NFC'));
  if (Array.isArray(value)) {
    return '[' + value.map((v) => jcsCanonicalize(v)).join(',') + ']';
  }
  if (t === 'object') {
    const obj = value as Record<string, unknown>;
    const seen = new Set<string>();
    const pairs: Array<readonly [string, unknown]> = [];
    for (const k of Object.keys(obj)) {
      if (obj[k] === undefined) continue; // absent member (ast.ts canonicalJson convention)
      const nk = k.normalize('NFC');
      if (seen.has(nk)) throw new Error(`ERR_NFC_DUP_KEY: ${nk}`);
      seen.add(nk);
      pairs.push([nk, obj[k]] as const);
    }
    // RFC 8785 §3.2.3: raw property names sorted by UTF-16 code units —
    // Array.prototype.sort()'s default comparator is exactly that.
    pairs.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
    return '{' + pairs.map(([k, v]) => jcsString(k) + ':' + jcsCanonicalize(v)).join(',') + '}';
  }
  throw new Error(`ERR_JCS_UNSERIALIZABLE: ${t}`);
}

// ---------------------------------------------------------------------------
// Multihash / multibase URN emission (tools/mint/src/hash.ts conventions).
// ---------------------------------------------------------------------------

const B32_ALPHABET = 'abcdefghijklmnopqrstuvwxyz234567';

/** RFC 4648 base32, lower-case, no padding (multibase 'b'). */
function base32(bytes: Uint8Array): string {
  let out = '';
  let bits = 0;
  let value = 0;
  for (let i = 0; i < bytes.length; i++) {
    value = (value << 8) | bytes[i]!;
    bits += 8;
    while (bits >= 5) {
      out += B32_ALPHABET[(value >>> (bits - 5)) & 31];
      bits -= 5;
    }
  }
  if (bits > 0) out += B32_ALPHABET[(value << (5 - bits)) & 31];
  return out;
}

/** urn:kot:<multibase-b-base32(multihash sha2-256)> from a raw 32-byte digest. */
function urnFromDigest(rawDigest: Uint8Array): string {
  if (rawDigest.length !== 32) throw new Error(`ERR_DIGEST_LEN: ${rawDigest.length}`);
  const mh = new Uint8Array(34);
  mh[0] = 0x12; // sha2-256
  mh[1] = 0x20; // length 32
  mh.set(rawDigest, 2);
  return 'urn:kot:b' + base32(mh);
}

/** Canonical hash-input bytes of a composite explication (header || JCS(NFC(payload))). */
export function compositeHashInput(e: Explication): Uint8Array {
  const enc = new TextEncoder();
  const header = enc.encode(KOT_AST_PROFILE_HEADER);
  const body = enc.encode(jcsCanonicalize(e));
  const out = new Uint8Array(header.length + body.length);
  out.set(header, 0);
  out.set(body, header.length);
  return out;
}

/**
 * Mint the content-addressed URN of an invented composite. Validates first
 * (fail closed — an invalid AST must never acquire an identity). Identical
 * composites recurring anywhere mint the same URN (global dedupe for free,
 * io-compression-ideas.md §3.2).
 */
export function mintCompositeUrn(e: Explication): string {
  validateExplication(e);
  const digest = createHash('sha256').update(compositeHashInput(e)).digest();
  return urnFromDigest(new Uint8Array(digest));
}

// ---------------------------------------------------------------------------
// The invented-concept dictionary (system-side, exact-by-id).
// ---------------------------------------------------------------------------

export interface DictionaryEntry {
  readonly urn: string;
  /** Canonical AST (deep-frozen clone; the dictionary owns its copy). */
  readonly ast: Explication;
  /** Pinned canonical rendering (render.ts canonical-form v0). */
  readonly renderedText: string;
  /** Occurrences observed via add() — dedupe statistics for the census. */
  occurrences: number;
}

/**
 * URN -> {AST, rendered text} store. Deliberately NOT serializable into an
 * LLM prompt by any method here: the accounting rule of
 * io-compression-ideas.md §3.3 (dictionary text never rides in the context)
 * is enforced by keeping this object system-side.
 */
export class CompositeDictionary {
  private readonly entries = new Map<string, DictionaryEntry>();

  /** Roll up a composite: validate, mint, store (dedupe), return its URN. */
  add(e: Explication): string {
    const urn = mintCompositeUrn(e);
    const existing = this.entries.get(urn);
    if (existing !== undefined) {
      existing.occurrences += 1;
      return urn;
    }
    const ast = JSON.parse(canonicalJson(e)) as Explication; // defensive canonical clone
    this.entries.set(urn, { urn, ast, renderedText: renderExplication(ast), occurrences: 1 });
    return urn;
  }

  /** Exact-by-id expansion. Unknown URN = hard error (no approximate path). */
  expand(urn: string): DictionaryEntry {
    const entry = this.entries.get(urn);
    if (entry === undefined) throw new Error(`ERR_DICT_UNKNOWN_URN: ${urn}`);
    return entry;
  }

  has(urn: string): boolean {
    return this.entries.has(urn);
  }

  get size(): number {
    return this.entries.size;
  }

  /** All entries (insertion order) — census/dedupe reporting. */
  list(): readonly DictionaryEntry[] {
    return [...this.entries.values()];
  }
}
