// Deterministic binary Merkle root over a set of minted URNs — the
// `corpusIdentityRoot` recorded in each manifest and re-checked by the pack
// verifier.
//
// Definition (pinned; verifier recomputes byte-identically):
//   1. De-duplicate URNs, sort ascending by UTF-16 code unit (default JS sort).
//   2. leaf_i   = sha2-256( UTF8(urn_i) )
//   3. Build a binary tree bottom-up: pair (2i, 2i+1); an odd trailing node is
//      promoted to the next level unchanged (no duplication).
//      parent = sha2-256( left || right )
//   4. Root of a single leaf is that leaf. Root of an empty set is
//      sha2-256("") (the empty-input digest), so the field is always defined.
//   Output: lower-case hex of the 32-byte root.

import { sha256, concatBytes, utf8, toHex } from "./hash.js";

export function merkleRoot(urns: readonly string[]): string {
  const uniqueSorted = Array.from(new Set(urns)).sort();
  if (uniqueSorted.length === 0) {
    return toHex(sha256(new Uint8Array(0)));
  }
  let level: Uint8Array[] = uniqueSorted.map((u) => sha256(utf8(u)));
  while (level.length > 1) {
    const next: Uint8Array[] = [];
    for (let i = 0; i < level.length; i += 2) {
      if (i + 1 < level.length) {
        next.push(sha256(concatBytes(level[i]!, level[i + 1]!)));
      } else {
        next.push(level[i]!); // promote odd trailing node unchanged
      }
    }
    level = next;
  }
  return toHex(level[0]!);
}
