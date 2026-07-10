# m0a-llmproxy — design note + pre-registration text (prereg_doc for registry/experiments/m0a-llmproxy.json)

> STATUS: DESIGN (record DRAFT). STAND-IN, NOT THE PRE-REGISTERED HUMAN PASS.
> The M0a pre-registration (docs/poc-design.md, Phase M: "mapper
> precision/recall against human annotation") names HUMAN annotation; the
> current provisional numbers (strict P 0.82 / strict R 0.8865) were produced
> by a NON-BLIND, project-contexted Claude-family agent on 2026-07-07 and are
> stamped PROVISIONAL in every artifact. This record replaces that stopgap
> with a BLIND, kernel-instance-naive, cross-vendor LLM judge over the same
> 300 items — a strictly better-controlled stand-in that is STILL NOT the
> human pass and discharges nothing [STIPULATED: ASM-0550, ASM-0540]. The
> human pass over `mapper/m0/annotation-sample.jsonl` remains the sole gold
> standard. Designed by FABLE (designer-1); execution is Opus-runner work,
> mechanical, post-freeze; undecided situations are BOUNDARY STOPS to Fable.

## S1. Why a fresh registry record

M0a predates the registry (it is pre-registered in prose in docs/poc-design.md
and published in `mapper/m0/results/m0a-report.json`), so there is no frozen
human record to protect — but the same discipline applies: this proxy gets its
own id and envelope, the human pass keeps the M0a name and the
pre-registration, and the proxy's P/R numbers carry a quarantine label
everywhere they appear [STIPULATED: ASM-0540].

## S2. Items and per-stratum task (blind rendering)

Items: all 300 of `mapper/m0/annotation-sample.jsonl` (sha256 038604a8…;
strata concept 100 / prime 100 / abstain 50 / none 50; per-stratum reservoir,
seed 0xC0FFEE, populations pinned in `mapper/m0/results/m0a-report.json`
sha256 c424be2d…). Rendering (mechanical builder, staged at run time as
`poc/m0a-llmproxy/judge-invocation.md` + templates + schemas, pinned by ops
amendment before any real call) [STIPULATED: ASM-0541]:

- concept/prime (200): the passage (contextBefore + the marked token +
  contextAfter), plus ONE proposed sense = the mapped target's gloss rendered
  WITHOUT any urn/id (concept: the record gloss from
  `data/kernel-v0/concepts/<slug>.json`; prime: the profile-1 lexicon's
  canonical one-line exponent gloss). Question: "In this passage, does the
  marked word, as used here, have this meaning?" with the pinned judging
  criteria carried on the sheet verbatim from the stated M0a criteria
  (sense-in-context only; adequacy of the definition out of scope; light-verb
  / phrasal / idiomatic / auxiliary uses whose sense differs = incorrect;
  unclear = genuinely contestable). Answer ∈ {correct, incorrect, unclear}.
- abstain (50): the passage + the recorded candidate senses as a numbered
  gloss list (no ids). Question: "would ANY single one of these senses be the
  correct reading of the marked token here?" Answer: the number, or `none`.
  Mapped to candidate-correct / no-candidate-correct.
- none (50): the passage + the full pinned kernel-v0 surface inventory (54
  concept lemmas + 65 prime exponents, each with a one-line sense; byte-identical
  rendering across all 50 items). Question: "should the marked token, as used
  here, be annotated with one of the listed senses?" Answer: the entry, or
  `none`. Mapped to should-map / correctly-unmapped.

Blinding: the judge never sees urns, stratum labels, the words "kernel",
"NSM", "mapper", the project name, or that a mapping system produced the
proposed sense ("a proposed sense", never "the mapper's decision"). Grep audit
per call over prompt + captured events: `kernel`, `nsm`, `urn:`, `mapper` —
any hit ⇒ ABORT to Fable.

## S3. Judge mechanism and why

judge-m1p-gpt56sol: `gpt-5.6-sol`, effort `low`, npx-pinned
`@openai/codex@0.144.1`, invocation form byte-derived from
`poc/truthstyle-2x2/judges-invocation.md` §4.1 (stateless per-item calls,
empty out-of-repo workdir, ignore-user-config, memories/web-search disabled,
read-only sandbox, server-side per-stratum output schemas, zero-tool tripwire,
first-valid-answer-final, ≤ 3 content attempts then no-label). CROSS-VENDOR is
load-bearing twice over: (a) the judgments being replaced were produced by a
Claude-family agent, so a Claude judge would correlate with the very
comparator the diagnostic below measures against; (b) the mapper, the kernel
glosses and the prior judging are all Claude-family work-products
(author-family separation) [STIPULATED: ASM-0540]. The in-session Agent-tool
sub-agent form is FORBIDDEN (ASM-0240 finding, carried over). Item order:
seed-pinned shuffle `m0alp/1|judge-m1p|20260710`. Preflight: 2 pinned
calibration items (one plainly-correct sense pairing expected `correct`, one
plainly-wrong expected `incorrect`) first-attempt pass required.

## S4. Instrument controls

- Deranged-gloss probe: 40 items (20 concept + 20 prime, seed-pinned
  `m0alp/1|probe|20260710`), same passage/token, proposed sense = the gloss of
  a DIFFERENT sampled target (per-stratum Sattolo cycle over distinct target
  ids). Correct answer `incorrect` by construction (near-synonym collision
  risk disclosed). Gate: probe coverage ≥ 36/40 AND false-endorsement
  (`correct`) rate < 0.30, else INSTRUMENT-INVALID [STIPULATED: ASM-0544].
- Retest stability floor: 30 seed-pinned duplicates
  (`m0alp/1|retest|20260710`) re-asked after the probe pass; raw agreement
  ≥ 0.80 required, else INSTRUMENT-INVALID (FAIL direction only).
- Coverage: n_labelled ≥ 285/300 overall AND ≥ 90/100 per 100-item stratum
  AND ≥ 45/50 per 50-item stratum, else INSTRUMENT-INVALID.

## S5. Metrics — the pinned M0a estimator, proxy-labelled

`analysis/m0a_llmproxy.py` (PINNED-AT-FREEZE) recomputes the published M0a
estimator EXACTLY as `mapper/m0/compute-pr.py` (sha256 5858b116…), with proxy
labels in place of agent labels and denominators restricted to labelled items
[STIPULATED: ASM-0542]:

- precision strict/lenient = stratum-population-weighted share of
  correct-mapped tokens (strict: unclear counted incorrect; lenient: correct),
  concept + prime strata, populations 117563 + 504500;
- recall strict/lenient = correct-mapped mass / (correct-mapped mass +
  abstain-miss mass + none-miss mass), populations abstain 181388 / none
  2958417; recall lowerBound95 = the none-miss rate at its Clopper-Pearson
  95% upper bound over the observed none-stratum sample (the pre-existing
  thin-coverage discipline: ~50 items over 2.96M tokens = 78% of token mass —
  carried over UNCHANGED, not fixed by this proxy);
- REPORTED-ONLY diagnostic, never gated, never validation: per-stratum raw
  agreement between the proxy labels and the 2026-07-07 non-blind agent
  labels (`mapper/m0/agent-judgments.jsonl` sha256 6f291b69…). Divergence
  measures blindness + judge-family effects JOINTLY and attributes nothing
  [EXTRAPOLATION: ASM-0543 — resolved by the human pass on the same items].

## S6. Verdict semantics and licensing

The M0a pre-registration is a MEASUREMENT with no kill bar; the proxy cannot
invent one. Verdict rules: INSTRUMENT-INVALID (gates); PASS iff all instrument
gates hold — PASS means EXACTLY "a valid blind-LLM proxy measurement of the
M0a quantities exists", never a mapper-quality endorsement; INCONCLUSIVE
otherwise. The proxy P/R REPLACE the agent-judged provisional numbers as the
programme's provisional numbers (upgrading blindness and author-family
independence only, never species-of-judge); every citation carries the
WEAK-PROXY label and the human pass remains the only discharger of the M0a
pre-registration. Proxy per-item labels are pinned so the eventual human pass
yields a free human-vs-proxy bias measurement (ASM-0553); proxy outputs must
never be shown to the human annotator beforehand. Asymmetric reading:
familiarity/leniency channels plausibly inflate `correct` judgments, so LOW
proxy precision (or a nonzero none-miss) is the more informative outcome — an
early warning on the mapper line; high proxy P/R licenses only continued
investment. Budget: ≈ 372 calls, Tier 0, usd_cap 10, zero GPU.
