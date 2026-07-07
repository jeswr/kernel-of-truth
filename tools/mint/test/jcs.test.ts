// RFC 8785's own test vectors (fetched from rfc-editor.org/rfc/rfc8785.txt,
// 2026-07-07): Appendix B number-serialization table, the s3.2.3 property-
// sorting test object, and the s3.2.4 full worked example with its expected
// UTF-8 bytes. Plus kot-profile layering tests (nfcDeep separate from strict
// JCS, per the RFC's "preserve string data as is" note).

import { test } from "node:test";
import assert from "node:assert/strict";
import { canonicalize, serializeNumber, nfcDeep, canonicalBytes, JsonValue } from "../src/jcs.js";

function doubleFromHex(hex: string): number {
  const buf = new ArrayBuffer(8);
  const dv = new DataView(buf);
  dv.setBigUint64(0, BigInt("0x" + hex));
  return dv.getFloat64(0);
}

test("RFC 8785 Appendix B: ES6 number serialization table", () => {
  const vectors: Array<[string, string]> = [
    ["0000000000000000", "0"], // Zero
    ["8000000000000000", "0"], // Minus zero
    ["0000000000000001", "5e-324"], // Min pos number
    ["8000000000000001", "-5e-324"], // Min neg number
    ["7fefffffffffffff", "1.7976931348623157e+308"], // Max pos number
    ["ffefffffffffffff", "-1.7976931348623157e+308"], // Max neg number
    ["4340000000000000", "9007199254740992"], // Max pos int
    ["c340000000000000", "-9007199254740992"], // Max neg int
    ["4430000000000000", "295147905179352830000"], // ~2**68
    ["44b52d02c7e14af5", "9.999999999999997e+22"],
    ["44b52d02c7e14af6", "1e+23"],
    ["44b52d02c7e14af7", "1.0000000000000001e+23"],
    ["444b1ae4d6e2ef4e", "999999999999999700000"],
    ["444b1ae4d6e2ef4f", "999999999999999900000"],
    ["444b1ae4d6e2ef50", "1e+21"],
    ["3eb0c6f7a0b5ed8c", "9.999999999999997e-7"],
    ["3eb0c6f7a0b5ed8d", "0.000001"],
    ["41b3de4355555553", "333333333.3333332"],
    ["41b3de4355555554", "333333333.33333325"],
    ["41b3de4355555555", "333333333.3333333"],
    ["41b3de4355555556", "333333333.3333334"],
    ["41b3de4355555557", "333333333.33333343"],
    ["becbf647612f3696", "-0.0000033333333333333333"],
    ["43143ff3c1cb0959", "1424953923781206.2"], // Round to even
  ];
  for (const [hex, expected] of vectors) {
    assert.equal(serializeNumber(doubleFromHex(hex)), expected, `IEEE754 ${hex}`);
  }
  // NaN / Infinity MUST error
  assert.throws(() => serializeNumber(doubleFromHex("7fffffffffffffff")), /ERR_JCS_NONFINITE/);
  assert.throws(() => serializeNumber(doubleFromHex("7ff0000000000000")), /ERR_JCS_NONFINITE/);
});

test("RFC 8785 s3.2.3: property sorting test data", () => {
  const input: JsonValue = {
    "€": "Euro Sign",
    "\r": "Carriage Return",
    "דּ": "Hebrew Letter Dalet With Dagesh",
    "1": "One",
    "😀": "Emoji: Grinning Face",
    "": "Control",
    "ö": "Latin Small Letter O With Diaeresis",
  };
  const out = canonicalize(input);
  const order = [
    "Carriage Return",
    "One",
    "Control",
    "Latin Small Letter O With Diaeresis",
    "Euro Sign",
    "Emoji: Grinning Face",
    "Hebrew Letter Dalet With Dagesh",
  ];
  const found = [...out.matchAll(/:"([^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(found, order);
});

test("RFC 8785 s3.2.2/s3.2.4: full worked example, expected UTF-8 bytes", () => {
  // Input as parsed from the RFC's sample JSON text.
  const input = JSON.parse(
    '{"numbers": [333333333.33333329, 1E30, 4.50, 2e-3, 0.000000000000000000000000001],' +
      '"string": "\\u20ac$\\u000F\\u000aA\'\\u0042\\u0022\\u005c\\\\\\"\\/",' +
      '"literals": [null, true, false]}',
  );
  const expectedHex = (
    "7b 22 6c 69 74 65 72 61 6c 73 22 3a 5b 6e 75 6c 6c 2c 74 72" +
    " 75 65 2c 66 61 6c 73 65 5d 2c 22 6e 75 6d 62 65 72 73 22 3a" +
    " 5b 33 33 33 33 33 33 33 33 33 2e 33 33 33 33 33 33 33 2c 31" +
    " 65 2b 33 30 2c 34 2e 35 2c 30 2e 30 30 32 2c 31 65 2d 32 37" +
    " 5d 2c 22 73 74 72 69 6e 67 22 3a 22 e2 82 ac 24 5c 75 30 30" +
    " 30 66 5c 6e 41 27 42 5c 22 5c 5c 5c 5c 5c 22 2f 22 7d"
  )
    .split(/\s+/)
    .join("");
  const got = Buffer.from(new TextEncoder().encode(canonicalize(input))).toString("hex");
  assert.equal(got, expectedHex);
});

test("RFC 8785 Appendix A style: arrays keep order, nested objects sorted", () => {
  const input: JsonValue = [56, { d: true, "10": null, "1": [] }];
  assert.equal(canonicalize(input), '[56,{"1":[],"10":null,"d":true}]');
});

test("lone surrogates are rejected", () => {
  assert.throws(() => canonicalize("\ud800"), /ERR_JCS_LONE_SURROGATE/);
  assert.throws(() => canonicalize({ "\udead": 1 }), /ERR_JCS_LONE_SURROGATE/);
});

test("kot-profile layering: strict JCS preserves non-NFC; nfcDeep normalizes", () => {
  const decomposed = "é"; // 'e' + COMBINING ACUTE
  const composed = "é"; // U+00E9
  // strict JCS: as-is
  assert.equal(canonicalize(decomposed), `"${decomposed}"`);
  // profile bytes: NFC first
  assert.equal(new TextDecoder().decode(canonicalBytes(decomposed)), `"${composed}"`);
  // keys normalize too; a post-NFC collision fails closed
  assert.throws(() => nfcDeep({ [decomposed]: 1, [composed]: 2 }), /ERR_NFC_DUP_KEY/);
});
