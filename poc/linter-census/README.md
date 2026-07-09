# poc/linter-census — LNT-E0: proposition-coverage census + false-alarm floor

Tier-0 ($0, r0-local-cpu) feasibility instruments for the kernel precision
linter (`docs/next/kernel-precision-linter.md` §5 LNT-E0), run over the
Stage-0 `kot-lint` core (`tools/lint/`).

**EPISTEMIC STATUS — read first.** This is an EXPLORATORY feasibility run:
NOT pre-registered, no frozen `kot-reg/1` record, and per the tooling law it
can never flip any verdict. Its numbers are tooling-level MEASUREMENTS
(deterministic census, no sampling, no RNG; exact command in the report)
whose scope is exactly the three pinned corpus slices — they extrapolate to
NO other corpus (the m0b envelope discipline verbatim). If the linter idea
proceeds, LNT-E0 gets a proper prereg (experiment-designer role) and these
instruments become its harness; margins/kill bars are fixed at freeze, not
here.

## Reproduce

```sh
# corpus (not committed; 19.4 MB): the m0a/m0b-pinned TinyStories validation split
curl -L https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStories-valid.txt -o /tmp/TinyStories-valid.txt
bash poc/linter-census/prep-clean-human.sh     # renders the committed man-page slice
nice -n 10 node poc/linter-census/run-lnt-e0.mjs --tinystories=/tmp/TinyStories-valid.txt
```

Outputs: `results/lnt-e0-report.json` (full numbers, stable JSON) and
`results/lnt-e0-report.md` (render-only summary). The committed results were
produced 2026-07-09 over the full 21,990-story corpus (sha256 in the report's
`corpusPins`; 15.6 s runtime).

## Slices (corpus choices for the LLM-output and clean-text classes)

- **llm-tinystories** — the m0b-pinned corpus: LLM-generated (GPT-3.5/4)
  stories, so it serves N-PL's "real LLM outputs" class AND makes the
  proposition-level number directly comparable to the MEASURED token-mass
  0.3542 @ molecules-v0 (`registry/verdicts/m0b.json`).
- **llm-programme-docs** — six pinned programme design docs (LLM/agent-
  authored technical prose; the N-PL Stage-0 "dogfood on the programme's own
  generated docs").
- **clean-human** — rendered man pages (bash/grep/tar; 62k words of
  human-authored precise technical documentation). STIPULATED corpus choice
  for this feasibility run within N-PL's declared class ("clean,
  human-authored precise text — good technical documentation"); it is OFF
  the covered TinyStories domain, which is fine for the coverage-INDEPENDENT
  V/A false-alarm floor (U is info-only and never an alarm in mode P) but
  means the U columns for this slice say nothing about the linter's covered-
  domain behaviour. The prereg-time corpus choice remains open.

## Headline numbers (MEASURED, this run's scope only — see the report for all)

- **(i) Census.** Proposition-level conjunctive coverage on llm-tinystories
  (443,008 clause-propositions): **6.83% @ molecules-v0** and **3.87%
  kernel-v0-strict** (the operational "linter can fully map it today"
  ceiling) — vs 35.42% token-mass on the same corpus. Single-digit, exactly
  the N-PL §9.3 expectation; and these are UPPER BOUNDS (no frame conjunct;
  clause proxy). On technical prose (docs / man pages) it is ~0.3–0.5%.
- **(ii) False-alarm floor.** clean-human: **0.080 warn flags / 1000 words**
  (V 0.064, A 0.016); **0.136% of sentences** carry a warn flag.
  llm-programme-docs: 0.62 warn/1000w (all A-class; zero V).
  llm-tinystories: 6.15 warn/1000w, dominated by A on the single ambiguity
  shadow "little" (19,383 of 22,974 A flags).
- **(iii) V split.** Only the V-rhetorical half is measurable at Stage 0
  (V-tautology needs the explication normaliser); per-pattern counts are in
  the JSON — notable measured pattern hazard: "at the end of the day" fires
  240× on TinyStories where it is mostly LITERAL narrative time, the
  idiom-vs-literal failure mode to price at prereg time.
- **Instrument gates.** G1 rung monotonicity holds on every slice; G2: the
  harness's flagless decision fractions reproduce the published M0a headline
  to 4 decimal places (deltas 0.0000 pp across all five numbers).

## Files

- `run-lnt-e0.mjs` — the census + false-alarm harness (aggregation over
  `tools/lint/lib/lint.mjs`; G1/G2 instrument gates; render-only .md)
- `prep-clean-human.sh` — clean-human slice prep (pinned rendering)
- `corpora/clean-human/*.txt` — committed clean-human slice
- `results/lnt-e0-report.{json,md}` — committed run outputs
