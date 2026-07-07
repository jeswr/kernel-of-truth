# Phase X on the AUTHORED kernel-v0 corpus — combined summary

date: 2026-07-07T03:55:02.315Z
corpus: kernel-v0, 54 concepts (research-grade, agent-authored, NOT federation-endorsed)
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (matches manifest pin: true)
corpus content-hash: `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`

The Phase-X pre-registered property tests (docs/poc-design.md), previously run on
seeded synthetics only, re-run on the authored corpus. Per-suite reports:
x1-kernel-v0-report.md, x2-kernel-v0-report.md, x3-kernel-v0-report.md, x4-kernel-v0-report.md.

## Headlines

| suite | headline on authored kernel-v0 | pre-registered bar | verdict |
|---|---|---|---|
| X1 | min adversarial single-edit angle 0.002342 rad over 2475 neighbours; fp16 floor 0.000213 rad; ratio 11.0x | >5x floor | **SUCCESS** |
| X2 | 51/54 exact decode (minimal lexicon; full-corpus lexicon 51/54); non-exact: afraid, angry, sad | 100% exact (depth <= 4 instantiation) | **FAIL** |
| X3 | 13/79 meaning-inverting edits sit closer than the nearest distinct pair (`afraid`<->`sad` cos 0.9933); inverting median cos 0.8976 | none (documentation) | documented |
| X4 | RDM Spearman 0.9718 (512) / 0.9706 (576); min R^d margin 0.002252 / 0.002199 rad = 10.1x / 9.9x floor | X1 criteria in R^d | **SUCCESS / SUCCESS** |

## Named minimum-margin pair (all 1431 authored pairs)

**`afraid` <-> `sad`** at 0.115560 rad (543.6x fp16 floor). Top nearest pairs:

1. afraid <-> sad: 0.115560 rad
2. happy <-> sad: 0.205097 rad
3. afraid <-> happy: 0.223819 rad
4. repair <-> take: 0.488447 rad
5. birth <-> death: 0.516249 rad

## Deltas vs the synthetic runs

- Synthetic X1 (reduced n=500, results/x1-report.md): min adversarial 0.015988 rad = 63.4x floor.
- Synthetic X2 gate passed 720/720 (full grid); the authored corpus FAILS it 51/54 —
  the quote-re-anchored emotion trio (afraid/angry/sad) drops optional SP slots or
  misorders a referent introduction under deep quote+op nesting, identically in both
  lexicon conditions (kernel-of-truth-0kn).
- The authored corpus exercises what synthetics cannot: reference-bearing concepts
  (18/18 exact decode), quote re-anchoring, the deliberately-near give/take/gift
  cluster (which is NOT the nearest pair — the emotion cluster is; kernel-of-truth-7yp),
  and authored known-weak explications (manifest.json#knownWeak).

> Adequacy of these explications is unvalidated (social, not proven); these are
> encoder property tests, not NSM-adequacy claims.