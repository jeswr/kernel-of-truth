# Programme-3 — Round-2 subjective steering note (coordinator synthesis)

**What this is:** a synthesis of the two independent subjective analyses run at the post-batch-2
milestone — Fable (`scratchpad/subj-fable.out`, archived under `poc/gpt56-review/subj-fable-20260711/`
at commit) and GPT-5.6 (`poc/gpt56-review/subj-gpt56-20260711/`). OPINION/steering only, labelled as
such per [[subjective-dual-model-analysis]]; it never overrides a mechanical verdict or a frozen
envelope. Both theses remain INCONCLUSIVE-PENDING and nothing here moves them. The two reads are
unusually convergent.

## Convergent signals (high-confidence steering)

1. **Healthy epistemically, poor experimentally.** The measurement discipline is the best this class of
   work has had (four cheap measurements landed since round-1; two kills declined honestly). But the
   decisive *quantities* remain unmeasured: Python extraction coverage, NLB retention under S2,
   clarification rate/utility, real resource costs, and a matched strong-generic baseline.
2. **Run f2b stage-2 — the EV question is nearly a category error at ~$1.** Broad information EV is
   modest (self-authored, kernel-covered, kernel-rendered, ≤1.7B, k=4 slice; with A=0.961 a large
   lift_mem≫lift_ext gap is arithmetically unlikely), but the marginal cost is ~$1/$15-cap and it is the
   only near-term registered adjudication that can put a PASS or a scoped kill on the efficiency line.
   Run it, **report it prominently, and refuse to treat a PASS as broad validation.** (Note: the runner
   must be BUILT first — dispatched.)
3. **CODEVERT G0 is the single highest-value substantive next experiment (both, independently).** ~$0,
   authorized; converts the biggest UNMEASURED block ("Python is a friendlier extraction domain" —
   pure EXTRAPOLATION vs the measured g8 0/1000 / m0b 0.3542 walls) into facts. A bad κ_q result stops
   the vertical *before* any annotation spend; a good one defines a defensible G1 universe. Dispatched.
4. **Complete DECONF-A1** (replay + dual-init, ~$0 CPU) before its grid conclusions get consumed. Dispatched.
5. **STOP further design/review cycles.** Design has converged ("enough designs to occupy several
   years; it lacks results"); the CASK-PY/1 arch round was ~85% re-derivation. Marginal review cycles now
   burn the scarce resource to produce convergence certificates. → No arch-synthesis round this wave.
6. **Drop / dormant:** general-index oracle census (human hours into a functionally-dead index — the
   census *raised* the ceiling to 0.986), H-DD, broad general-NL GNN fusion, deep-internal placements,
   proof-search on the v0 engine (no proof states to expose). Retire proof-state consumers from planning.

## Two material strategic decisions (surfaced to the maintainer)

Both models converged, nearly verbatim, on two calls that the programme is currently making **by
default via cost gradients** rather than deciding. These are maintainer-gated (issues opened):

- **A. The annotation portfolio (the #1 risk).** Every *deflationary* leg is cheap and keeps landing;
  every *affirmative decisive* leg (g2 Π-soundness, g3 necessity, GATE-H authoring, CODEVERT G1/G4 gold,
  knull-v2 plain-arm ruling) is human-annotation-gated and unrun. On the current trajectory the verdict
  degrades into **FAIL-by-attrition** — precise measured deflation against never-run affirmative legs.
  Mitigation both endorse: a pre-registered, maintainer-ratified ranking of human-gated decisive legs by
  verdict-movement-per-annotator-hour + a bounded budget. Coordinator's ranking (from Fable): (1)
  CODEVERT G1 census 70–130h, (2) g2 Π-soundness gold, (3) knull-v2 plain-arm ruling.
- **B. Is the kernel becoming optional to its own programme?** Composed measured record: the F2 lift
  survives at grid scope as an aligned-answer-key property (DECONF-A1); the a5 world is
  structural-not-NSM; a full CODEVERT win is kernel-free (ASM-1000); the NSM-semantics core (g2/g3) is
  unrun. Every live, funded line either doesn't consume NSM semantics or is agnostic to them. The likely
  emerging success story is narrower and more conventional: *a small model + an aligned typed
  store/checker*. If that's the right call it should be **made, not drifted into**; if wrong, only
  g2/g3/knull-v2 spending reverses it.

## Secondary: single-vendor epistemics
GPT-5.6 is simultaneously the sole external design-review gate, the rival architecture proposer, and the
same model family as judge-2/3. Cheap mitigation: route one review per major design (and any future judge
fallback) through a third vendor family. The stage-1 *result* survives its same-family caveat because the
human anchors every resolved label; the design-review pipeline has no such anchor.

## Next wave (dispatched this milestone) — results, not designs
f2b stage-2 runner build (→ reuse-check/dry-plan/mock/run) · CODEVERT G0 (extractor spike +
extractor-independent census) · DECONF-A1 completion (replay + init-order). Then: the annotation-portfolio
decision (issue) gates the affirmative legs; cross-experiment feasibility-synthesis refresh once G0 +
stage-2 land.
