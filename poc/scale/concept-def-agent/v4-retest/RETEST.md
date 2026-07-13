# concept-def-agent — v4 concision-discipline re-test (2026-07-13)

Validation of the lexicographic-concision discipline added in
`concept-def-prompt-v4.md`. Same 5 test concepts, same synsets
(`test-concepts.json`, positions 16–20), same runner, same model, same
mechanical gate as the v3 smoke (`TEST-RESULTS.md`).

**Setup (identical to v3 except the prompt).**

| item | value |
|---|---|
| model | `claude-opus-4-8`, `MAX_THINKING_TOKENS=0`, subscription auth (temp-0 = first valid answer) |
| v3 prompt sha256 | `fa2f80998bc4…` |
| v4 prompt sha256 | `bd4423998c0e…` |
| delta | new subsection **§1A Lexicographic concision discipline** inserted after §1, *before* §2; all §1 sense-correctness / non-circularity / self-containment rules and all §3 AST rules UNCHANGED. §1A opens by declaring itself SUBORDINATE to §1/§3 (tighten a correct definition, never trim into a wrong/circular one). Includes the draft's 7 concision bullets, its 3 before/after exemplars, and accept-gate leg 1 as an internal (non-emitting) self-check. |
| gate | strict-JSON → mechanical record checks → `validate-record.mjs` (`validateExplication` + single-concept `encodeConceptSet`), fail-closed — same gate as v3 |
| runner change | added a minimal `--prompt <path>` flag (default = canonical v3 file); v3 prompt path untouched |
| outputs | `v4-retest/*.opus48.json` (+ `.report.json`, `provenance/`) |

## Result — all 5 pass strict-JSON + mechanical gate, first attempt, no re-queue

| concept | v3 gloss (words) | v4 gloss (words) | concision verdict | sense preserved | non-circular preserved | mech. gate | AST adequacy v3→v4 | v4 latency / cost |
|---|---|---|---|---|---|---|---|---|
| **builder** (empire sense) | "A person who brings a large enterprise or country into being and makes it grow, so that through their work something great comes to exist and becomes bigger and stronger than before." (32) | "A person who founds and develops something large such as a business or a country, through whose sustained effort it comes into being and grows." (25) | **tighter** — drops the redundant "so that … bigger and stronger than before" tail | ✓ empire/business-builder, label self-disambiguates "builder (of a business or nation)" | ✓ no "build*" cognate ("founds and develops") | ✓ PASS (7 cl, d2) | lossy → lossy | 14.0 s / $0.159 (cold cache) |
| **pull** | "The act of applying force to something so that it moves toward oneself or in the direction of one's own movement." (21) | "The act of applying force to something so that it moves toward the agent or along with the agent's own motion." (21) | **same** — equal length; "the agent … along with the agent's own motion" marginally crisper, not shorter. NB: did *not* adopt the draft's shorter after-exemplar | ✓ both WN disjuncts (toward / with you) | ✓ no "pull" cognate | ✓ PASS (5 cl, d2) | faithful → faithful | 10.9 s / $0.030 |
| **expensiveness** | "The quality of costing a great deal, such that one must give much in exchange to obtain the thing." (19) | "The quality of costing a great deal; the property of a thing whose acquisition requires giving much in exchange." (19) | **same** — equal length; swapped one appositive clause for another. The draft's ideal 7-word after-exemplar ("The quality of costing a great deal.") was **not** reached — model kept a second explanatory clause | ✓ high-priced quality | ✓ no "expensive*" cognate ("costing a great deal") | ✓ PASS (4 cl, d3) | lossy → lossy | 12.1 s / $0.029 |
| **candidate** | canonical v3 = **gpt-5.6-sol** (opus v3 gate-FAILED): "A person under active consideration as a possible choice for a position, award, honor, or other role or benefit." (19) | "A person who is being considered as a possible recipient of a position, prize, or honour, so that others weigh whether it should be given to them." (27) | **same** (concision); see caveat — headline is the **gate recovery** | ✓ under-consideration-for-office/prize/honour | ✓ no "candidate" cognate | ✓ PASS (6 cl, d3) — **opus first attempt** (v3 opus needed re-queue to gpt-5.6-sol) | lossy → lossy | 15.3 s / $0.034 |
| **dig** (poke sense) | "The act of touching someone abruptly and sharply with a finger or elbow, pressing into their body for a brief moment." (21) | "A sudden, sharp prod given to someone with a finger or elbow." (12) | **tighter** — clearest win; adopts the one-exact-noun rule ("prod"), drops the "pressing into their body for a brief moment" gloss-of-a-gloss | ✓ poke-in-the-ribs, label "dig (a poke)" | ✓ no "dig/jab" lemma reused ("prod" is a distinct genus verb) | ✓ PASS (2 cl, d3) | lossy → lossy | 11.5 s / $0.029 |

Cold-cache first call (builder) ≈ $0.16 API-equivalent; warm-cache thereafter
≈ $0.03/concept, ~11–15 s — same envelope as v3. Subscription auth ⇒ $0
marginal. Every reply was a bare JSON object (no fence-stripping needed).

## Reading

- **Gate + sense integrity: fully preserved.** 5/5 strict-JSON + mechanical-gate
  passes on `claude-opus-4-8` alone, first attempt, zero re-queues. No sense
  drift, no circularity introduced (all 5 records carry empty `warnings`,
  incl. the runner's headword/cognate heuristic), AST-adequacy self-flags
  unchanged from v3 (builder lossy, pull faithful, expensiveness lossy,
  candidate lossy, dig lossy). Concision did **not** cost correctness.

- **Concision effect: real but uneven.** 2 clear tightenings (builder 32→25,
  dig 21→12), 2 lateral (pull 21=21, expensiveness 19=19), 1 lateral-with-caveat
  (candidate). The two wins are exactly where v3 carried an explanatory tail
  ("so that … stronger than before"; "pressing into their body for a brief
  moment") — the discipline reliably removes that padding. Where v3 was already
  near-minimal (pull, expensiveness) the discipline neither helped nor hurt, and
  in expensiveness it did **not** reach its own advertised 7-word ideal — the
  model kept a second appositive clause. So the discipline trims obvious
  padding but does not force maximal compression.

- **Bonus — candidate gate recovery.** Under v3, opus repeatedly failed the gate
  on candidate (`ERR_REF_NOT_INTRODUCED`: bound a referent inside a THINK-quote,
  mentioned it outside) and only passed via re-queue to gpt-5.6-sol. Under v4,
  opus passes candidate first attempt with a quote-free 6-clause explication.
  This is plausibly a **side effect** of the concision discipline steering the
  gloss away from the nested-attitude phrasing that produced the fragile
  quote structure — an incidental robustness gain, not a targeted fix; n=1, do
  not over-read.

## Caveats (for the coordinator)

1. **Example priming.** The draft's 3 before/after exemplars are drawn verbatim
   from the v3 glosses of **pull, expensiveness, and dig** — i.e. 3 of the 5
   test concepts are effectively primed by their own answers in the prompt.
   This *inflates* the apparent effect and, more importantly, makes this a
   weak test of generalisation. Notably the model still did **not** simply copy
   the exemplars (pull/expensiveness kept fuller forms; dig paraphrased "prod …
   given to someone"), so the discipline is doing more than lookup — but a
   clean read needs held-out concepts whose glosses are NOT in the prompt.
2. **candidate is a cross-model v3 baseline.** The v3 *canonical passing* record
   for candidate is gpt-5.6-sol, because opus v3 failed the gate. The v4 opus
   gloss (27 w) is longer than that gpt-5.6 baseline (19 w) and re-introduces a
   "so that …" clause the discipline nominally discourages, though it removes the
   open-ended "or other role or benefit" tail the discipline explicitly targets.
   Same-model (opus-v3-fail vs opus-v4-pass) the length is unchanged (27=27);
   the win there is purely the gate pass.
3. **Accept-gate leg 2 not exercised.** Only leg 1 (generator self-check) is in
   the prompt; the runner still applies only the mechanical gate. The draft's
   second grader ("would a first-rate dictionary accept this?") is a downstream
   step and was NOT run here — scholarly-bar judgement in this doc is my read,
   not that gate.

## Files created (uncommitted)

- `poc/scale/concept-def-agent/concept-def-prompt-v4.md` — v3 + §1A concision block
- `poc/scale/concept-def-agent/v4-retest/{builder,pull,expensiveness,candidate,dig}.opus48.json` (+ `.report.json`, `provenance/`)
- `poc/scale/concept-def-agent/v4-retest/RETEST.md` — this file
- `poc/scale/concept-def-agent/define_concept.py` — added a minimal `--prompt` flag (default unchanged)
