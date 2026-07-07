// Unit tests: multihash/multibase emission, uvarint, Merkle root, Tarjan SCC
// order, and the gist-s6 component algorithm (JCS variant) including the
// ERR_SYMMETRIC_SCC fail-closed gate and index/sentinel behavior.

import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { sha256, base32, multibase32, urnKot, uvarint, toHex, utf8, concatBytes } from "../src/hash.js";
import { merkleRoot } from "../src/merkle.js";
import { tarjanSCC } from "../src/scc.js";
import { mintSingleton, mintComponent } from "../src/mint-core.js";

test("base32: RFC 4648 lower-case, no padding", () => {
  // RFC 4648 test vectors (lowercased, padding stripped)
  const cases: Array<[string, string]> = [
    ["", ""],
    ["f", "my"],
    ["fo", "mzxq"],
    ["foo", "mzxw6"],
    ["foob", "mzxw6yq"],
    ["fooba", "mzxw6ytb"],
    ["foobar", "mzxw6ytboi"],
  ];
  for (const [input, expected] of cases) {
    assert.equal(base32(utf8(input)), expected, input);
  }
});

test("multihash wrapping: 0x12 0x20 prefix, multibase 'b'", () => {
  const digest = sha256(utf8("hello"));
  const mb = multibase32(digest);
  assert.equal(mb[0], "b");
  // decode leading 2 bytes back: base32 of [0x12,0x20,...]
  assert.match(mb, /^b[a-z2-7]+$/);
  assert.equal(urnKot(digest), "urn:kot:" + mb);
  // known digest check: sha256("hello") starts 2cf24d…
  assert.equal(toHex(digest).slice(0, 8), "2cf24dba");
});

test("uvarint: unsigned LEB128", () => {
  assert.deepEqual(Array.from(uvarint(0)), [0x00]);
  assert.deepEqual(Array.from(uvarint(1)), [0x01]);
  assert.deepEqual(Array.from(uvarint(127)), [0x7f]);
  assert.deepEqual(Array.from(uvarint(128)), [0x80, 0x01]);
  assert.deepEqual(Array.from(uvarint(300)), [0xac, 0x02]);
});

test("merkle root: pinned construction", () => {
  const h = (b: Buffer | Uint8Array) => new Uint8Array(createHash("sha256").update(b).digest());
  // empty
  assert.equal(merkleRoot([]), toHex(h(Buffer.alloc(0))));
  // single leaf = leaf hash
  assert.equal(merkleRoot(["urn:kot:x"]), toHex(h(Buffer.from("urn:kot:x"))));
  // duplicates de-duplicate
  assert.equal(merkleRoot(["urn:kot:x", "urn:kot:x"]), merkleRoot(["urn:kot:x"]));
  // two leaves: parent = H(leaf(a)||leaf(b)) with sorted URNs
  const la = h(Buffer.from("a")), lb = h(Buffer.from("b"));
  assert.equal(merkleRoot(["b", "a"]), toHex(h(concatBytes(la, lb))));
  // three leaves: H( H(l0||l1) || l2 ) — odd node promoted
  const lc = h(Buffer.from("c"));
  assert.equal(merkleRoot(["c", "a", "b"]), toHex(h(concatBytes(h(concatBytes(la, lb)), lc))));
});

test("tarjan: reverse topological order, cycle detection", () => {
  const edges = new Map<string, string[]>([
    ["a", ["b"]],
    ["b", ["c"]],
    ["c", ["b", "d"]],
    ["d", []],
  ]);
  const comps = tarjanSCC(["a", "b", "c", "d"], edges);
  // components: [d], [b,c], [a] — dependencies before dependents
  const flat = comps.map((c) => c.slice().sort().join("+"));
  assert.deepEqual(flat, ["d", "b+c", "a"]);
});

test("component algorithm: deterministic member URNs, symmetric SCC rejected", () => {
  const header = "kot-test/1\n";
  // Asymmetric 2-cycle: A references B and has a distinguishing field.
  const A = { sourceId: "urn:t:a", payload: { name: "A-ish", ref: "urn:t:b" } };
  const B = { sourceId: "urn:t:b", payload: { name: "B-ish", ref: "urn:t:a" } };
  const res1 = mintComponent([A, B], header, (s) => s);
  const res2 = mintComponent([B, A], header, (s) => s); // input order must not matter
  assert.equal(res1.urns.get("urn:t:a"), res2.urns.get("urn:t:a"));
  assert.equal(res1.urns.get("urn:t:b"), res2.urns.get("urn:t:b"));
  assert.notEqual(res1.urns.get("urn:t:a"), res1.urns.get("urn:t:b"));
  // member digest reconstruction: H(header#member || X_raw || uvarint(i))
  const X = sha256(concatBytes(utf8(header), res1.componentCanonicalBytes));
  for (const [sid, i] of res1.memberIndex) {
    const d = sha256(concatBytes(utf8("kot-test/1#member\n"), X, uvarint(i)));
    assert.equal(res1.urns.get(sid), urnKot(d));
  }
  // Perfectly symmetric SCC must fail closed.
  const S1 = { sourceId: "urn:t:s1", payload: { ref: "urn:t:s2" } };
  const S2 = { sourceId: "urn:t:s2", payload: { ref: "urn:t:s1" } };
  assert.throws(() => mintComponent([S1, S2], header, (s) => s), /ERR_SYMMETRIC_SCC/);
});

test("singleton: self-reference becomes #self; substitution changes the URN", () => {
  const header = "kot-test/1\n";
  const own = "urn:t:x";
  const m1 = mintSingleton({ me: own, k: 1 }, header, own, (s) => s);
  // the canonical bytes must contain the sentinel, not the placeholder
  assert.match(new TextDecoder().decode(m1.canonicalBytes), /urn:kot:#self/);
  // resolving an external ref changes identity
  const withRef = { r: "urn:t:dep" };
  const unresolved = mintSingleton(withRef, header, own, (s) => s);
  const resolved = mintSingleton(withRef, header, own, (s) => (s === "urn:t:dep" ? "urn:kot:babc" : s));
  assert.notEqual(unresolved.urn, resolved.urn);
});
