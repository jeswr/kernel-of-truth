# d-qa — F2 definitional-QA eval inputs

**Role.** Pinned input corpus for the frozen F2 experiment (`registry/experiments/f2.json`):
resolves the two `PINNED-AT-INPUTS:d-qa` placeholders — `definitional-qa-eval-set` and
`gloss-corpus-and-rag-index` — via ops amendments under `registry/amendments/f2/`
(kot-corpus-hash/1 digest over this directory). Also consumed by E9-full (`gloss-corpus` pin)
when that record freezes.

**Contents.**

| File | What |
|---|---|
| `items/covered.jsonl` | 500 kernel-covered definitional-QA items (= F2 `n_planned.per_arm_items`), pinned order (`rank`); every item carries its concept `urn` + `record_sha256` so the kernel verifier can score it against the canonical record |
| `items/control.jsonl` | 150 NOT-kernel-covered control items, same item types and pinned order; `kernel_checkable: false` (measures off-coverage verifier behaviour / false positives) |
| `gloss-corpus.jsonl` | hash-pinned gloss dictionary + RAG corpus for the text arms (kernel-as-text, RAG-over-text, gloss-text self-verify+retry): 108 covered + 30 control + 239 filler WordNet-3.1 gloss docs |
| `rag-index.json` | deterministic BM25 statistics (k1=1.2, b=0.75) over `gloss-corpus.jsonl` |
| `leak-check.json` | leak-check evidence (LC1–LC7); the build fails closed on any violation |
| `manifest.json` | build manifest: source pins, counts, split, authorship |
| `build-dqa.py` | the deterministic builder — re-running it reproduces every generated file byte-identically |

**Item types.** `def-match` (4-way forced choice: label → definition), `term-match`
(4-way: definition → label; dropped+substituted if the definition leaks the headword),
`claim-true` / `claim-false` (yes/no: a definitional segment from the concept's own record
vs a non-entailed segment from a different record, Jaccard-screened).

**Sources.** Covered slice: `data/kernel-v0` (54 concepts, `gloss` field) +
`data/molecules-v0` (54 molecules, `groundingNote` field) — exactly the corpora pinned in
the frozen F2 record. Control slice: M0b top-500 content-mass lemmas (classes
explicable/molecule/oos) that no kernel/molecule record covers, glossed from
`data/lexical-wn31`. All source digests are in `manifest.json`.

**Authorship.** Deterministically generated from the pinned records by `build-dqa.py`
(fixed templates; sha256-seeded selections; no wall-clock, no PRNG state). **No LLM
authored, selected, or edited any item text.** Built by runner-2, 2026-07-08.

**Leak check.** Fail-closed at build time; see `leak-check.json`. LC1 headword not in any
shown definition; LC2 answer text never in the question; LC3 false claims non-entailed
(substring + token-Jaccard < 0.5 screens); LC4 options distinct, answer present; LC5 no
duplicate ids/questions; LC6 true claims verbatim from the record; LC7 answer-key balance
(no majority letter; yes/no 172/202).

**Reproduce / verify.**

```bash
python3 data/d-qa/build-dqa.py                 # regenerates byte-identical outputs
python3 tools/registry/corpus-pin.py d-qa      # kot-corpus-hash/1 digest
```
