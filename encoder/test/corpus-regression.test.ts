/**
 * Regression tests for the authored kernel-v0 emotion trio (kernel-of-truth-0kn):
 * the X2-corpus run failed 51/54 because deep OPTIONAL content under quote>op
 * nesting fell below the decoder's presence gates —
 *   afraid: quote>CAN>HAPPEN lost its whole roles map (undergoer SP carrying
 *     the introducing bind:2 + time adjunct), so the decoded AST used ref 2
 *     without its introduction and failed validation (ERR_REF_NOT_INTRODUCED);
 *   angry:  quote>DO.undergoer lost quant:"SOME" and quote>WANT>complement>DO
 *     lost its whole undergoer SP (ok-but-wrong);
 *   sad:    quote>NOT>CAN>DO lost its whole undergoer SP (ok-but-wrong).
 * The fix is the decoder's residual-completion phase (decoder.ts). The shapes
 * are inlined (not read from data/kernel-v0) so the test pins the SHAPE even
 * if the corpus is ever re-authored.
 *
 * SPEC RULING (documented by the validator tests below): the afraid record is
 * LEGAL. Gist §4.2: each referent has "exactly one introducing occurrence"
 * and "a cdef:ref to an undeclared or not-yet-introduced index is a gate
 * error"; "Quote-local referents (bound inside a cdef:quoteClauses) scope to
 * that quote". afraid's ref 2 is declared, bound exactly once (quote clause
 * 0), and every mention follows the introduction inside the same quote — the
 * validator was right to accept it; the decoder was wrong to lose the bind.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { Explication } from '../src/ast.js';
import { AST_SCHEMA, canonicalJson } from '../src/ast.js';
import { encodeExplication } from '../src/encoder.js';
import { decodeExplication } from '../src/decoder.js';
import { validateExplication } from '../src/validate.js';

/** kernel-v0 `afraid` (NSM emotion schema): in-quote introduction of ref 2 under CAN. */
const AFRAID: Explication = {
  schema: AST_SCHEMA,
  frame: 'WhenTrue',
  referents: [
    { index: 1, refKind: 'SomeoneRef' },
    { index: 2, refKind: 'SomethingRef' },
  ],
  clauses: [
    {
      type: 'op',
      op: 'BECAUSE',
      args: [
        {
          type: 'pred',
          pred: 'THINK',
          roles: {
            experiencer: { kind: 'ref', index: 1 },
            quote: {
              kind: 'quote',
              clauses: [
                {
                  type: 'op',
                  op: 'CAN',
                  args: [
                    {
                      type: 'pred',
                      pred: 'HAPPEN',
                      roles: {
                        undergoer: {
                          kind: 'sp',
                          head: { kind: 'primeHead', prime: 'SOMETHING~THING' },
                          quant: 'SOME',
                          mods: [{ mod: 'BAD', intensifier: 'VERY' }],
                          bind: 2,
                        },
                        time: { kind: 'temporal', op: 'AFTER', anchor: { kind: 'prime', prime: 'NOW' } },
                      },
                    },
                  ],
                },
                {
                  type: 'pred',
                  pred: "DON'T-WANT",
                  roles: {
                    experiencer: { kind: 'prime', prime: 'I' },
                    complement: { kind: 'ref', index: 2 },
                  },
                },
                {
                  type: 'op',
                  op: 'MAYBE',
                  args: [
                    {
                      type: 'pred',
                      pred: 'HAPPEN',
                      roles: {
                        undergoer: { kind: 'ref', index: 2 },
                        time: { kind: 'temporal', op: 'AFTER', anchor: { kind: 'prime', prime: 'NOW' } },
                      },
                    },
                  ],
                },
              ],
            },
          },
        },
        {
          type: 'pred',
          pred: 'FEEL',
          roles: {
            experiencer: { kind: 'ref', index: 1 },
            attribute: { kind: 'prime', prime: 'BAD' },
          },
        },
      ],
    },
  ],
};

/** kernel-v0 `angry`: quant on a deep quote SP + a whole undergoer SP under quote>WANT>complement. */
const ANGRY: Explication = {
  schema: AST_SCHEMA,
  frame: 'WhenTrue',
  referents: [
    { index: 1, refKind: 'SomeoneRef' },
    { index: 2, refKind: 'SomeoneRef' },
    { index: 3, refKind: 'SomethingRef' },
  ],
  clauses: [
    {
      type: 'op',
      op: 'BECAUSE',
      args: [
        {
          type: 'pred',
          pred: 'THINK',
          roles: {
            experiencer: { kind: 'ref', index: 1 },
            quote: {
              kind: 'quote',
              clauses: [
                {
                  type: 'pred',
                  pred: 'DO',
                  roles: {
                    agent: { kind: 'sp', head: { kind: 'primeHead', prime: 'SOMEONE' }, bind: 2 },
                    undergoer: {
                      kind: 'sp',
                      head: { kind: 'primeHead', prime: 'SOMETHING~THING' },
                      quant: 'SOME',
                      mods: [{ mod: 'BAD' }],
                      bind: 3,
                    },
                    time: { kind: 'temporal', op: 'BEFORE', anchor: { kind: 'prime', prime: 'NOW' } },
                  },
                },
                {
                  type: 'pred',
                  pred: "DON'T-WANT",
                  roles: {
                    experiencer: { kind: 'prime', prime: 'I' },
                    complement: { kind: 'ref', index: 3 },
                  },
                },
                {
                  type: 'pred',
                  pred: 'WANT',
                  roles: {
                    experiencer: { kind: 'prime', prime: 'I' },
                    complement: {
                      kind: 'clause',
                      clause: {
                        type: 'pred',
                        pred: 'DO',
                        roles: {
                          agent: { kind: 'prime', prime: 'I' },
                          undergoer: {
                            kind: 'sp',
                            head: { kind: 'primeHead', prime: 'SOMETHING~THING' },
                            quant: 'SOME',
                          },
                        },
                      },
                    },
                  },
                },
              ],
            },
          },
        },
        {
          type: 'pred',
          pred: 'FEEL',
          roles: {
            experiencer: { kind: 'ref', index: 1 },
            attribute: { kind: 'prime', prime: 'BAD' },
          },
        },
      ],
    },
  ],
};

/** kernel-v0 `sad`: whole undergoer SP under quote>NOT>CAN>DO. */
const SAD: Explication = {
  schema: AST_SCHEMA,
  frame: 'WhenTrue',
  referents: [
    { index: 1, refKind: 'SomeoneRef' },
    { index: 2, refKind: 'SomethingRef' },
  ],
  clauses: [
    {
      type: 'op',
      op: 'BECAUSE',
      args: [
        {
          type: 'pred',
          pred: 'THINK',
          roles: {
            experiencer: { kind: 'ref', index: 1 },
            quote: {
              kind: 'quote',
              clauses: [
                {
                  type: 'pred',
                  pred: 'HAPPEN',
                  roles: {
                    undergoer: {
                      kind: 'sp',
                      head: { kind: 'primeHead', prime: 'SOMETHING~THING' },
                      quant: 'SOME',
                      mods: [{ mod: 'BAD' }],
                      bind: 2,
                    },
                    time: { kind: 'temporal', op: 'BEFORE', anchor: { kind: 'prime', prime: 'NOW' } },
                  },
                },
                {
                  type: 'pred',
                  pred: "DON'T-WANT",
                  roles: {
                    experiencer: { kind: 'prime', prime: 'I' },
                    complement: { kind: 'ref', index: 2 },
                  },
                },
                {
                  type: 'op',
                  op: 'NOT',
                  args: [
                    {
                      type: 'op',
                      op: 'CAN',
                      args: [
                        {
                          type: 'pred',
                          pred: 'DO',
                          roles: {
                            agent: { kind: 'prime', prime: 'I' },
                            undergoer: {
                              kind: 'sp',
                              head: { kind: 'primeHead', prime: 'SOMETHING~THING' },
                              quant: 'SOME',
                            },
                          },
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          },
        },
        {
          type: 'pred',
          pred: 'FEEL',
          roles: {
            experiencer: { kind: 'ref', index: 1 },
            attribute: { kind: 'prime', prime: 'BAD' },
          },
        },
      ],
    },
  ],
};

test('spec ruling (gist §4.2): in-quote introduction preceding in-quote mentions is LEGAL', () => {
  // afraid's ref 2: declared, exactly one bind (quote clause 0), mentions in
  // quote clauses 1 and 2 — introduced in order, within the quote's scope.
  assert.doesNotThrow(() => validateExplication(AFRAID));
});

test('spec ruling (gist §4.2): in-quote mention BEFORE the introducing bind is a gate error', () => {
  // The mirror case the decoder's old output produced: swap afraid's quote
  // clauses so the ref-2 mention precedes the introducing occurrence.
  const reordered = JSON.parse(JSON.stringify(AFRAID)) as {
    clauses: [{ args: [{ roles: { quote: { clauses: unknown[] } } }, unknown] }];
  };
  const qc = reordered.clauses[0].args[0].roles.quote.clauses;
  [qc[0], qc[1]] = [qc[1], qc[0]];
  assert.throws(() => validateExplication(reordered as unknown as Explication), /ERR_REF_NOT_INTRODUCED/);
});

test('regression (kernel-of-truth-0kn): afraid — in-quote introducing SP under CAN round-trips exactly', () => {
  const v = encodeExplication(AFRAID);
  const r = decodeExplication(v);
  assert.equal(r.ok, true, r.validationError);
  assert.equal(canonicalJson(r.explication), canonicalJson(AFRAID));
});

test('regression (kernel-of-truth-0kn): angry — deep quant:SOME and quote>WANT>complement undergoer SP round-trip exactly', () => {
  const v = encodeExplication(ANGRY);
  const r = decodeExplication(v);
  assert.equal(r.ok, true, r.validationError);
  assert.equal(canonicalJson(r.explication), canonicalJson(ANGRY));
});

test('regression (kernel-of-truth-0kn): sad — undergoer SP under quote>NOT>CAN>DO round-trips exactly', () => {
  const v = encodeExplication(SAD);
  const r = decodeExplication(v);
  assert.equal(r.ok, true, r.validationError);
  assert.equal(canonicalJson(r.explication), canonicalJson(SAD));
});
