# M0a — mapper measurement (pre-registered, poc-design.md Phase M)

**Date:** 2026-07-07 · **Mapper:** @jeswr/kernel-mapper v0.1.0 (deterministic lexicon,
abstain-and-record ambiguity policy) · **Kernel:** kernel-v0 (54 concepts) + 65 primes.
**Corpus:** TinyStories validation split (`roneneldan/TinyStories/TinyStories-valid.txt`,
HuggingFace, 19.4 MB, 21,990 stories, 3.79M expanded word tokens). TinyStories'
semantically clean ~1.5k-word domain is a deliberate **favourable-case** design choice
(pre-registered): every number below is a best case, not an estimate for real text.

## Headline numbers (% of token mass; 1 unit = 1 contraction-expanded word token)

| outcome | % of token mass |
|---|---|
| mapped to a kernel-v0 **concept** | **3.11%** |
| mapped to a **prime** | **13.97%** |
| mapped total | **17.08%** |
| **abstained** (ambiguous, recorded, never resolved) | **4.79%** |
| unmapped | 78.13% |

## Provisional precision/recall — **AGENT-JUDGED, PENDING HUMAN ANNOTATION**

The pre-registration names human annotation; a 300-item stratified sample
(100 concept / 100 prime / 50 abstain / 50 none, seeded reservoir) is formatted for
human annotators in `../annotation-sample.jsonl`. Until that pass exists, the numbers
below come from single-annotator agent judgments (`../agent-judgments.jsonl`,
criteria in `../make-agent-judgments.py`) and carry that caveat wherever quoted.

| metric | strict (unclear=incorrect) | lenient (unclear=correct) |
|---|---|---|
| precision (population-weighted over mapped strata) | **0.82** | 0.90 |
| recall (tokens whose true annotation is a kernel target) | **0.89** | 0.90 |
| recall lower bound (95% CP on the thin 0/50 unmapped stratum) | **0.68** | — |

- Per-stratum strict precision: concepts 82/100, primes 82/100.
- Dominant concept errors: causative/light-verb **make** (6 of 18 sampled uses), sense
  collisions (**lie** = recline, **right** = correct/suitable, **take** = transport,
  **find** = realize, phrasal **give up**). Dominant prime errors: **like** = enjoy
  (the single biggest precision hole: LIKE~AS~WAY got 24,783 mappings and the verb
  sense dominates the corpus), auxiliary **do**, spatial "ran **after**", **way** = route.
- 36% of abstained tokens had a correct candidate (mostly copula BE-SOMEWHERE/BE-SPEC
  and "little"→SMALL); 64% were correctly abstained (attributive/auxiliary copulas —
  grammatical glue with no kernel target).
- Unmapped mass is dominated by function words with no kernel target by design
  (the, a, and, to, pronouns) plus proper names (lily: 30.7k) — 0/50 sampled unmapped
  tokens should have mapped, but n=50 over a 2.96M-token stratum is why the recall
  lower bound above is honest.

## Hit distributions

- **11 of 54 concepts never fire**: archived, bookmark, broken, condolence, grieving,
  has-part, inside, kind, lost, maker-of, near. Four (broken, lost, inside, near, kind)
  are *permanently shadowed by the abstention policy* — every occurrence collides with
  a prime or an inflection of another concept (broken/break, lost/lose, near/NEAR,
  inside/INSIDE, kind/KIND). This is the ontology problem in miniature: adding concepts
  whose surface forms collide with existing exponents removes them from deterministic reach.
- Top concepts: happy 18.0k, make 15.8k, friend 15.2k, find 11.3k, take 10.1k, help 10.1k.
- Top primes: SAY 43.6k, THERE-IS 34.1k, YOU 30.8k, WHEN~TIME 29.3k, NOT 29.2k, SEE 26.4k.
- Top abstention sources: was 84.3k, is 22.0k, little 19.4k, were 13.7k, are 13.1k
  (copula polysemy + little/SMALL — 4.3 of the 4.79 abstention points are copulas).

Full numbers: `m0a-report.json`. Reproduce:
`node mapper/m0/run-m0a.mjs <TinyStories-valid.txt> mapper/m0 && python3 mapper/m0/make-agent-judgments.py && python3 mapper/m0/compute-pr.py`
