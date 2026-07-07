// Core minting: identity-payload -> urn:kot: URN, implementing the JCS variant
// of concept-hash-design.md s6 (the ordering-key / component algorithm is
// serialisation-agnostic; docs/design-hash-input.md adopts it unchanged, with
// JCS bytes replacing N-Quads bytes).
//
// Two paths:
//   * Singleton SCC  (the overwhelming majority): substitute every intra-corpus
//     reference with its already-minted urn:kot: URN; self-references (a record
//     referencing itself) become the `#self` sentinel; hash input =
//     UTF8(profileHeader) || JCS(NFC(payload)).
//   * Cyclic SCC (n>=2): ordering keys (own->#self, sibling members->#intra,
//     external refs->minted URNs) sort the members deterministically; the
//     component structure (member i's refs -> #member-i / #member-j) is hashed
//     once to a component digest X; member i's URN =
//     H( UTF8(profileHeader#member) || X_raw || uvarint(i) ).  Duplicate
//     ordering keys => ERR_SYMMETRIC_SCC (fail closed).

import { canonicalBytes, JsonValue } from "./jcs.js";
import { sha256, urnKot, utf8, concatBytes, uvarint } from "./hash.js";

// Sentinels — distinct from any real urn:kot: or urn:<corpus>: string.
const SELF = "urn:kot:#self";
const INTRA = "urn:kot:#intra";
const memberSentinel = (i: number): string => `urn:kot:#member-${i}`;

export type Resolver = (ref: string) => string;

// Recursively rewrite every string in a JSON value through `fn`.
export function rewriteStrings(value: JsonValue, fn: (s: string) => string): JsonValue {
  if (typeof value === "string") return fn(value);
  if (Array.isArray(value)) return value.map((v) => rewriteStrings(v, fn));
  if (value !== null && typeof value === "object") {
    const out: { [k: string]: JsonValue } = {};
    for (const k of Object.keys(value)) {
      out[k] = rewriteStrings((value as { [k: string]: JsonValue })[k]!, fn);
    }
    return out;
  }
  return value;
}

export function hashInput(profileHeader: string, payload: JsonValue): Uint8Array {
  return concatBytes(utf8(profileHeader), canonicalBytes(payload));
}

// Singleton mint. `ownId` is the record's placeholder urn (for self-ref
// detection); `resolve` maps an intra-corpus ref to its minted urn (or leaves
// external refs untouched).
export function mintSingleton(
  payload: JsonValue,
  profileHeader: string,
  ownId: string,
  resolve: Resolver,
): { urn: string; rawDigest: Uint8Array; canonicalBytes: Uint8Array } {
  const substituted = rewriteStrings(payload, (s) => {
    if (s === ownId) return SELF;
    return resolve(s);
  });
  const bytes = canonicalBytes(substituted);
  const digest = sha256(concatBytes(utf8(profileHeader), bytes));
  return { urn: urnKot(digest), rawDigest: digest, canonicalBytes: bytes };
}

export interface ComponentMember {
  sourceId: string; // placeholder urn (own id)
  payload: JsonValue;
}

export interface ComponentResult {
  // sourceId -> minted urn, plus the canonical component bytes for publication.
  urns: Map<string, string>;
  memberDigests: Map<string, Uint8Array>;
  memberIndex: Map<string, number>; // sourceId -> canonical index 0..n-1
  componentCanonicalBytes: Uint8Array;
  orderingKeysHex: string[]; // in sorted order, for the honesty ledger
}

// Cyclic SCC mint (concept-hash-design.md s6 steps 6-10, JCS variant).
export function mintComponent(
  members: ComponentMember[],
  profileHeader: string,
  resolveExternal: Resolver, // for refs outside the SCC (already minted or external)
): ComponentResult {
  const memberIds = new Set(members.map((m) => m.sourceId));

  // Step 6: ordering key per member (own -> #self, sibling -> #intra).
  const withKeys = members.map((m) => {
    const okPayload = rewriteStrings(m.payload, (s) => {
      if (s === m.sourceId) return SELF;
      if (memberIds.has(s)) return INTRA;
      return resolveExternal(s);
    });
    const digest = sha256(hashInput(profileHeader, okPayload));
    return { member: m, key: digest };
  });

  // Step 7: sort by ordering key (byte-lexicographic); duplicates fail closed.
  withKeys.sort((a, b) => cmpBytes(a.key, b.key));
  for (let i = 1; i < withKeys.length; i++) {
    if (cmpBytes(withKeys[i]!.key, withKeys[i - 1]!.key) === 0) {
      throw new Error(
        `ERR_SYMMETRIC_SCC: members ${withKeys[i - 1]!.member.sourceId} and ${
          withKeys[i]!.member.sourceId
        } have identical ordering keys; a distinguishing axiom or merge is required`,
      );
    }
  }

  // index assignment 0..n-1
  const indexOf = new Map<string, number>();
  withKeys.forEach((wk, i) => indexOf.set(wk.member.sourceId, i));

  // Step 8: component structure — member i's refs -> #member-i / #member-j.
  const membersOut: JsonValue[] = withKeys.map((wk) => {
    const i = indexOf.get(wk.member.sourceId)!;
    return rewriteStrings(wk.member.payload, (s) => {
      if (s === wk.member.sourceId) return memberSentinel(i);
      if (memberIds.has(s)) return memberSentinel(indexOf.get(s)!);
      return resolveExternal(s);
    });
  });
  const componentStruct: JsonValue = { "kot-component": profileHeader.trimEnd(), members: membersOut };
  const componentBytes = canonicalBytes(componentStruct);
  const componentDigest = sha256(concatBytes(utf8(profileHeader), componentBytes)); // X_raw (32 bytes)

  // Step 9: member i digest = H( UTF8(profileHeader#member) || X_raw || uvarint(i) )
  const memberHeader = profileHeader.replace(/\n$/, "#member\n");
  const urns = new Map<string, string>();
  const memberDigests = new Map<string, Uint8Array>();
  withKeys.forEach((wk) => {
    const i = indexOf.get(wk.member.sourceId)!;
    const d = sha256(concatBytes(utf8(memberHeader), componentDigest, uvarint(i)));
    urns.set(wk.member.sourceId, urnKot(d));
    memberDigests.set(wk.member.sourceId, d);
  });

  return {
    urns,
    memberDigests,
    memberIndex: indexOf,
    componentCanonicalBytes: componentBytes,
    orderingKeysHex: withKeys.map((wk) => Buffer.from(wk.key).toString("hex")),
  };
}

function cmpBytes(a: Uint8Array, b: Uint8Array): number {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    if (a[i]! !== b[i]!) return a[i]! - b[i]!;
  }
  return a.length - b.length;
}
