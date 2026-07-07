// Multihash / multibase identity emission, per the concept-hash design's
// conventions (concept-hash-design.md s6 step 10), adapted to the JCS hash-input
// decision (docs/design-hash-input.md).
//
//   digest      = sha2-256(hash input)
//   multihash   = 0x12 (sha2-256) || 0x20 (length 32) || digest    [34 bytes]
//   multibase   = 'b' || base32(multihash)  (RFC 4648 lower-case, no padding)
//   URN         = urn:kot:<multibase>
//
// The `urn:kot:` namespace (never `urn:concept:`) is mandated by
// docs/design-hash-input.md so no cross-scheme collision with the estate's
// RDF-native gist scheme is possible.

import { createHash } from "node:crypto";

export function sha256(bytes: Uint8Array): Uint8Array {
  const h = createHash("sha256");
  h.update(bytes);
  return new Uint8Array(h.digest());
}

// RFC 4648 base32, lower-case alphabet, no padding (multibase 'b').
const B32_ALPHABET = "abcdefghijklmnopqrstuvwxyz234567";

export function base32(bytes: Uint8Array): string {
  let out = "";
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
  if (bits > 0) {
    out += B32_ALPHABET[(value << (5 - bits)) & 31];
  }
  return out;
}

// Wrap a raw sha2-256 digest (32 bytes) as multihash multibase-base32 with the
// 'b' multibase prefix.
export function multibase32(rawDigest: Uint8Array): string {
  if (rawDigest.length !== 32) {
    throw new Error(`ERR_DIGEST_LEN: ${rawDigest.length}`);
  }
  const mh = new Uint8Array(34);
  mh[0] = 0x12; // sha2-256
  mh[1] = 0x20; // length 32
  mh.set(rawDigest, 2);
  return "b" + base32(mh);
}

// urn:kot:<multibase-multihash> from a raw digest.
export function urnKot(rawDigest: Uint8Array): string {
  return "urn:kot:" + multibase32(rawDigest);
}

// Unsigned LEB128 (multiformats uvarint), used by the cyclic-SCC member-hash
// construction (concept-hash-design.md s6 step 9).
export function uvarint(n: number): Uint8Array {
  if (n < 0 || !Number.isInteger(n)) {
    throw new Error(`ERR_UVARINT: ${n}`);
  }
  const bytes: number[] = [];
  let v = n;
  do {
    let b = v & 0x7f;
    v = Math.floor(v / 128);
    if (v > 0) b |= 0x80;
    bytes.push(b);
  } while (v > 0);
  return new Uint8Array(bytes);
}

export function concatBytes(...parts: Uint8Array[]): Uint8Array {
  const total = parts.reduce((a, p) => a + p.length, 0);
  const out = new Uint8Array(total);
  let off = 0;
  for (const p of parts) {
    out.set(p, off);
    off += p.length;
  }
  return out;
}

const UTF8 = new TextEncoder();
export function utf8(s: string): Uint8Array {
  return UTF8.encode(s);
}

export function toHex(bytes: Uint8Array): string {
  let s = "";
  for (let i = 0; i < bytes.length; i++) s += bytes[i]!.toString(16).padStart(2, "0");
  return s;
}
