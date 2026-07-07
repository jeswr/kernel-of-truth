// RFC 8785 (JSON Canonicalization Scheme) — canonical serialization, plus the
// kot-profile NFC pre-normalization.
//
// LAYERING (load-bearing): RFC 8785 s3.2 note says JCS itself "does not take
// [Unicode Normalization] into consideration — all components ... MUST
// preserve Unicode string data as is". The programme decision
// (docs/design-hash-input.md: "UTF-8 NFC + RFC 8785 JCS") therefore composes
// TWO steps:
//     hash input bytes = JCS( nfcDeep( identity payload ) )
// `canonicalize` below is strict, vector-testable RFC 8785; `nfcDeep` is the
// kot-profile pre-normalization applied by the minter before canonicalizing.
//
// The three JCS requirements, and how we meet them:
//   1. No insignificant whitespace (s3.2.1)     -> none emitted.
//   2. Property sorting (s3.2.3): raw property  -> Array.prototype.sort()'s
//      name strings compared as arrays of          default comparator compares
//      UTF-16 code units, ascending.               by UTF-16 code unit, exactly
//                                                  as specified.
//   3. Primitive serialization per ECMAScript (s3.2.2): strings via JSON
//      minimal escaping (lowercase \u00xx for controls, \b \t \n \f \r \" \\
//      two-char forms, everything else verbatim); numbers via the ES6
//      Number::toString shortest-round-trip algorithm — String(n) in a
//      conforming engine IS that algorithm (V8 is the RFC's own reference,
//      s3.2.2.3). NaN/Infinity and lone surrogates are hard errors per spec.

export type JsonValue =
  | null
  | boolean
  | number
  | string
  | JsonValue[]
  | { [k: string]: JsonValue };

const ESCAPES: Record<string, string> = {
  '"': '\\"',
  "\\": "\\\\",
  "\b": "\\b",
  "\t": "\\t",
  "\n": "\\n",
  "\f": "\\f",
  "\r": "\\r",
};

// RFC 8785 s3.2.2.2 string serialization. Operates on the string AS IS (no
// normalization). Lone surrogates are rejected (the RFC: "occurrences of such
// data MUST cause a compliant JCS implementation to terminate").
export function serializeString(s: string): string {
  let out = '"';
  for (let i = 0; i < s.length; i++) {
    const cu = s.charCodeAt(i);
    if (cu >= 0xd800 && cu <= 0xdbff) {
      // high surrogate: must be followed by a low surrogate
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
    else if (cu < 0x20) out += "\\u" + cu.toString(16).padStart(4, "0");
    else out += ch;
  }
  return out + '"';
}

// RFC 8785 s3.2.2.3: ECMAScript Number::toString. String(n) is that algorithm.
export function serializeNumber(n: number): string {
  if (!Number.isFinite(n)) throw new Error(`ERR_JCS_NONFINITE: ${n}`);
  if (Object.is(n, -0)) return "0";
  return String(n);
}

// Strict RFC 8785 canonicalization (no Unicode normalization).
export function canonicalize(value: JsonValue): string {
  if (value === null) return "null";
  const t = typeof value;
  if (t === "boolean") return value ? "true" : "false";
  if (t === "number") return serializeNumber(value as number);
  if (t === "string") return serializeString(value as string);
  if (Array.isArray(value)) {
    return "[" + value.map((v) => canonicalize(v)).join(",") + "]";
  }
  if (t === "object") {
    const obj = value as { [k: string]: JsonValue };
    // raw (unescaped) property names, sorted by UTF-16 code units (s3.2.3)
    const keys = Object.keys(obj).sort();
    const parts: string[] = [];
    for (const k of keys) {
      parts.push(serializeString(k) + ":" + canonicalize(obj[k]!));
    }
    return "{" + parts.join(",") + "}";
  }
  throw new Error(`ERR_JCS_UNSERIALIZABLE: ${t}`);
}

// kot-profile pre-normalization (docs/design-hash-input.md): NFC-normalize
// every string, including property names, recursively. Two distinct keys
// collapsing to one post-NFC is a hard error (fail closed, never silently
// merge fields).
export function nfcDeep(value: JsonValue): JsonValue {
  if (typeof value === "string") return value.normalize("NFC");
  if (Array.isArray(value)) return value.map(nfcDeep);
  if (value !== null && typeof value === "object") {
    const out: { [k: string]: JsonValue } = {};
    for (const k of Object.keys(value)) {
      const nk = k.normalize("NFC");
      if (nk in out) throw new Error(`ERR_NFC_DUP_KEY: ${nk}`);
      out[nk] = nfcDeep(value[k]!);
    }
    return out;
  }
  return value;
}

// Canonical UTF-8 hash-input bytes of an identity payload (NFC + JCS).
export function canonicalBytes(value: JsonValue): Uint8Array {
  return new TextEncoder().encode(canonicalize(nfcDeep(value)));
}
