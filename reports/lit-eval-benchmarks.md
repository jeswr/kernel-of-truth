# Lit-Eval Benchmarks — Fact Sheet (G3 freeze prerequisite)

**Kernel of Truth programme — evaluation-benchmark fact sheet.**
Author: Kern (source-verification role). Date: 2026-07-10.
**Purpose:** the freeze-prerequisite (gate G3) reference for every evaluation benchmark the
nsk1 freeze and the benchmark-strategy experiments premise on. Each benchmark's canonical
source, dataset size, licence, metric, and (where relevant) published SmolLM2-135M/360M/1.7B
card scores are verified at source this session and recorded as LIT-BACKED facts, so a
downstream prereg/decision may cite them without re-deriving them.

**Scope.** This is a FACT SHEET, not a design. It records only published/source facts; it
takes no design decision and stipulates nothing. It does not amend the assumption register.

## 0. How to read this sheet — tag convention

Each fact is an indented hyphen bullet that opens with the LOAD-BEARING marker and carries an
inline `[LIT-BACKED: <source>]` tag on the same logical line, so `tools/registry/claims-check.py`
validates every recorded fact against a citation (arXiv id / DOI / dated URL). Sources were
verified at source on 2026-07-10 via WebSearch/WebFetch. Where a canonical page blocked direct
fetch (openai.com returned HTTP 403 to WebFetch), the page was read via WebSearch and the fact
corroborated against an independently-fetchable secondary source; those cases are called out
inline. Nothing here is STIPULATED or EXTRAPOLATION — a benchmark whose fact could not be
verified at source is flagged UNVERIFIED in §5 rather than recorded as a fact.

---

## 1. Relational reasoning

### 1.1 CLUTRR

- LOAD-BEARING: canonical source — Sinha, Sodhani, Dong, Pineau & Hamilton, "CLUTRR: A Diagnostic Benchmark for Inductive Reasoning from Text", EMNLP 2019. [LIT-BACKED: arXiv:1908.06177, 2019; github.com/facebookresearch/clutrr]
- LOAD-BEARING: licence is CC-BY-NC-4.0 (Attribution-NonCommercial 4.0 International) — the README states verbatim "CLUTRR is CC-BY-NC 4.0 (Attr Non-Commercial Inter.) licensed, as found in the LICENSE file". [LIT-BACKED: github.com/facebookresearch/clutrr LICENSE, 2019]
- LOAD-BEARING: NonCommercial term means CLUTRR is usable for research/eval but not for commercial redistribution — a constraint the programme must honour if it ships eval artefacts. [LIT-BACKED: CC-BY-NC-4.0, github.com/facebookresearch/clutrr, 2019]
- LOAD-BEARING: dataset "size" is configuration-dependent — CLUTRR is a procedural story generator plus pre-generated splits, parameterised by the number of reasoning hops k (systematic-generalisation and robustness splits); there is no single canonical row count in the paper. [LIT-BACKED: arXiv:1908.06177, 2019; github.com/facebookresearch/clutrr]
- LOAD-BEARING: metric is accuracy on predicting the queried kinship/family relation from a narrative requiring k inference steps. [LIT-BACKED: arXiv:1908.06177, 2019]

---

## 2. SmolLM2 pretraining-suite benchmarks

The nine benchmarks below appear on the SmolLM2 base model cards. The SmolLM2 family
(135M / 360M / 1.7B, ~11T training tokens) is documented in Allal et al., "SmolLM2: When Smol
Goes Big — Data-Centric Training of a Small Language Model" (arXiv:2502.02737, 2025). Card
scores were read from the three HuggingFaceTB base model cards on 2026-07-10.

**SmolLM2 base-model card scores (verbatim from the model cards):**

| Benchmark | 135M | 360M | 1.7B | Metric / setting |
|-----------|------|------|------|------------------|
| HellaSwag | 42.1 | 54.5 | 68.7 | zero-shot |
| ARC (Average of Easy+Challenge) | 43.9 | 53.0 | 60.5 | zero-shot |
| PIQA | 68.4 | 71.7 | 77.6 | zero-shot |
| MMLU | 31.5 (cloze) | 35.8 (cloze) | 19.4 (MMLU-Pro MCF) | zero-shot |
| CommonsenseQA | 33.9 | 38.0 | 43.6 | zero-shot |
| TriviaQA | 4.1 | 16.9 | 36.7 | zero-shot |
| WinoGrande | 51.3 | 52.5 | 59.4 | zero-shot |
| OpenBookQA | 34.6 | 37.4 | 42.2 | zero-shot |
| GSM8K | 1.4 | 3.2 | 31.0 | 5-shot |

- LOAD-BEARING: the score table above is transcribed from the three SmolLM2 base model cards; all evals were run with `lighteval`, zero-shot except GSM8K (5-shot). [LIT-BACKED: HuggingFaceTB/SmolLM2-135M, -360M, -1.7B model cards; arXiv:2502.02737, 2025]
- LOAD-BEARING: the MMLU cell is NOT comparable across the three cards — the 135M and 360M cards report MMLU cloze (31.5 / 35.8), whereas the 1.7B card reports MMLU-Pro MCF (19.4), a different, harder benchmark; do not read a 360M→1.7B "drop" as a regression. [LIT-BACKED: HuggingFaceTB/SmolLM2-360M and -1.7B model cards, 2025]

### 2.1 ARC (AI2 Reasoning Challenge — Easy + Challenge)

- LOAD-BEARING: canonical source — Clark, Cowhey, Etzioni, Khot, Sabharwal, Schoenick & Tafjord, "Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge", 2018. [LIT-BACKED: arXiv:1803.05457, 2018]
- LOAD-BEARING: licence is CC-BY-SA-4.0. [LIT-BACKED: huggingface.co/datasets/allenai/ai2_arc, 2018]
- LOAD-BEARING: size is 7,787 natural grade-school science questions, split into ARC-Challenge (2,590) and ARC-Easy (5,197); SmolLM2 reports the average over the two. [LIT-BACKED: arXiv:1803.05457, 2018; huggingface.co/datasets/allenai/ai2_arc]
- LOAD-BEARING: metric is multiple-choice accuracy. [LIT-BACKED: arXiv:1803.05457, 2018]
- LOAD-BEARING: SmolLM2 base ARC (avg) zero-shot — 135M 43.9, 360M 53.0, 1.7B 60.5. [LIT-BACKED: HuggingFaceTB/SmolLM2-135M/-360M/-1.7B cards, 2025]

### 2.2 OpenBookQA

- LOAD-BEARING: canonical source — Mihaylov, Clark, Khot & Sabharwal, "Can a Suit of Armor Conduct Electricity? A New Dataset for Open Book Question Answering", EMNLP 2018. [LIT-BACKED: arXiv:1809.02789, 2018]
- LOAD-BEARING: licence is Apache-2.0. [LIT-BACKED: github.com/allenai/OpenBookQA LICENSE, 2018]
- LOAD-BEARING: size is 5,957 multiple-choice elementary-science questions (4,957 train / 500 dev / 500 test) probing a book of 1,326 core science facts. [LIT-BACKED: arXiv:1809.02789, 2018]
- LOAD-BEARING: metric is multiple-choice accuracy. [LIT-BACKED: arXiv:1809.02789, 2018]
- LOAD-BEARING: SmolLM2 base OpenBookQA zero-shot — 135M 34.6, 360M 37.4, 1.7B 42.2. [LIT-BACKED: HuggingFaceTB/SmolLM2 cards, 2025]

### 2.3 HellaSwag

- LOAD-BEARING: canonical source — Zellers, Holtzman, Bisk, Farhadi & Choi, "HellaSwag: Can a Machine Really Finish Your Sentence?", ACL 2019. [LIT-BACKED: arXiv:1905.07830, 2019]
- LOAD-BEARING: licence is MIT. [LIT-BACKED: huggingface.co/datasets/Rowan/hellaswag; github.com/rowanz/hellaswag LICENSE, 2019]
- LOAD-BEARING: size is 59,950 examples (39,905 train / 10,042 validation / 10,003 test). [LIT-BACKED: huggingface.co/datasets/Rowan/hellaswag, 2019]
- LOAD-BEARING: metric is multiple-choice accuracy on adversarially-filtered sentence-completion / commonsense-NLI. [LIT-BACKED: arXiv:1905.07830, 2019]
- LOAD-BEARING: SmolLM2 base HellaSwag zero-shot — 135M 42.1, 360M 54.5, 1.7B 68.7. [LIT-BACKED: HuggingFaceTB/SmolLM2 cards, 2025]

### 2.4 CommonSenseQA

- LOAD-BEARING: canonical source — Talmor, Herzig, Lourie & Berant, "CommonsenseQA: A Question Answering Challenge Targeting Commonsense Knowledge", NAACL 2019. [LIT-BACKED: arXiv:1811.00937, 2019]
- LOAD-BEARING: licence is MIT — the HuggingFace dataset card states verbatim "The dataset is licensed under the MIT License". [LIT-BACKED: huggingface.co/datasets/tau/commonsense_qa, 2019]
- LOAD-BEARING: size is 12,102 questions (9,741 train / 1,221 validation / 1,140 test). [LIT-BACKED: huggingface.co/datasets/tau/commonsense_qa; arXiv:1811.00937, 2019]
- LOAD-BEARING: metric is 5-way multiple-choice accuracy. [LIT-BACKED: arXiv:1811.00937, 2019]
- LOAD-BEARING: SmolLM2 base CommonsenseQA zero-shot — 135M 33.9, 360M 38.0, 1.7B 43.6. [LIT-BACKED: HuggingFaceTB/SmolLM2 cards, 2025]

### 2.5 WinoGrande

- LOAD-BEARING: canonical source — Sakaguchi, Le Bras, Bhagavatula & Choi, "WinoGrande: An Adversarial Winograd Schema Challenge at Scale", AAAI 2020 (preprint 2019). [LIT-BACKED: arXiv:1907.10641, 2019]
- LOAD-BEARING: licence — the dataset is CC-BY while the accompanying code is Apache-2.0 (split licensing in the AllenAI repo). [LIT-BACKED: github.com/allenai/winogrande, 2019]
- LOAD-BEARING: size is ~44,000 fill-in-the-blank (pronoun-resolution) problems. [LIT-BACKED: arXiv:1907.10641; github.com/allenai/winogrande, 2019]
- LOAD-BEARING: metric is binary-choice accuracy. [LIT-BACKED: arXiv:1907.10641, 2019]
- LOAD-BEARING: SmolLM2 base WinoGrande zero-shot — 135M 51.3, 360M 52.5, 1.7B 59.4. [LIT-BACKED: HuggingFaceTB/SmolLM2 cards, 2025]

### 2.6 PIQA

- LOAD-BEARING: canonical source — Bisk, Zellers, Le Bras, Gao & Choi, "PIQA: Reasoning about Physical Commonsense in Natural Language", AAAI 2020 (preprint 2019). [LIT-BACKED: arXiv:1911.11641, 2019]
- LOAD-BEARING: licence is the Academic Free License v3.0 (AFL-3.0), per the official dataset distribution; note the HuggingFace mirror ybisk/piqa lists licence as "unknown", so cite the official source. [LIT-BACKED: yonatanbisk.com/piqa; tensorflow.org/datasets/catalog/piqa, 2019]
- LOAD-BEARING: size is ~21,000 examples (16,000 train / 2,000 dev / 3,000 test). [LIT-BACKED: huggingface.co/datasets/ybisk/piqa; arXiv:1911.11641, 2019]
- LOAD-BEARING: metric is binary-choice accuracy over two candidate physical solutions. [LIT-BACKED: arXiv:1911.11641, 2019]
- LOAD-BEARING: SmolLM2 base PIQA zero-shot — 135M 68.4, 360M 71.7, 1.7B 77.6. [LIT-BACKED: HuggingFaceTB/SmolLM2 cards, 2025]

### 2.7 MMLU

- LOAD-BEARING: canonical source — Hendrycks, Burns, Basart, Zou, Mazeika, Song & Steinhardt, "Measuring Massive Multitask Language Understanding", ICLR 2021 (preprint 2020). [LIT-BACKED: arXiv:2009.03300, 2020]
- LOAD-BEARING: licence is MIT. [LIT-BACKED: huggingface.co/datasets/cais/mmlu; github.com/hendrycks/test LICENSE, 2020]
- LOAD-BEARING: size is 14,042 test questions across 57 subjects (plus 285 dev, 1,531 validation, ~99,842 auxiliary-train). [LIT-BACKED: huggingface.co/datasets/cais/mmlu, 2020]
- LOAD-BEARING: metric is multiple-choice accuracy, averaged across subjects. [LIT-BACKED: arXiv:2009.03300, 2020]
- LOAD-BEARING: SmolLM2 base MMLU zero-shot — 135M 31.5 and 360M 35.8 report MMLU cloze; the 1.7B card reports MMLU-Pro MCF 19.4 (different benchmark — see §2 caveat). [LIT-BACKED: HuggingFaceTB/SmolLM2-135M/-360M/-1.7B cards, 2025]

### 2.8 TriviaQA

- LOAD-BEARING: canonical source — Joshi, Choi, Weld & Zettlemoyer, "TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension", ACL 2017. [LIT-BACKED: arXiv:1705.03551, 2017; aclanthology.org/P17-1147]
- LOAD-BEARING: licence is Apache-2.0 — RESOLVED at source: the official repo README states "The Apache 2.0 License applies to both the code and the data", with the caveat that the University of Washington does not own the copyright of the underlying trivia questions/documents. [LIT-BACKED: github.com/mandarjoshi90/triviaqa, 2017]
- LOAD-BEARING: size is ~650,000 question-answer-evidence triples built from ~95,000 question-answer pairs, ~6 evidence documents per question on average. [LIT-BACKED: arXiv:1705.03551, 2017]
- LOAD-BEARING: metric is exact-match / F1 for reading comprehension; SmolLM2 evaluates it as closed-book QA (zero-shot exact-match accuracy). [LIT-BACKED: arXiv:1705.03551, 2017; HuggingFaceTB/SmolLM2 cards, 2025]
- LOAD-BEARING: SmolLM2 base TriviaQA zero-shot — 135M 4.1, 360M 16.9, 1.7B 36.7. [LIT-BACKED: HuggingFaceTB/SmolLM2 cards, 2025]

### 2.9 GSM8K

- LOAD-BEARING: canonical source — Cobbe, Kosaraju, Bavarian, Chen, Jun, Kaiser, Plappert, Tworek, Hilton, Nakano, Hesse & Schulman, "Training Verifiers to Solve Math Word Problems", 2021. [LIT-BACKED: arXiv:2110.14168, 2021]
- LOAD-BEARING: licence is MIT — the dataset card states verbatim "The GSM8K dataset is licensed under the MIT License". [LIT-BACKED: huggingface.co/datasets/openai/gsm8k, 2021]
- LOAD-BEARING: size is 8.5K grade-school math word problems (7,473 train / 1,319 test), each solvable in 2–8 elementary steps. [LIT-BACKED: arXiv:2110.14168; huggingface.co/datasets/openai/gsm8k, 2021]
- LOAD-BEARING: metric is final-answer accuracy (exact match on the numeric answer). [LIT-BACKED: arXiv:2110.14168, 2021]
- LOAD-BEARING: SmolLM2 base GSM8K 5-shot — 135M 1.4, 360M 3.2, 1.7B 31.0. [LIT-BACKED: HuggingFaceTB/SmolLM2 cards, 2025]

---

## 3. Coding benchmarks

### 3.1 HumanEval

- LOAD-BEARING: canonical source — Chen et al., "Evaluating Large Language Models Trained on Code", 2021. [LIT-BACKED: arXiv:2107.03374, 2021]
- LOAD-BEARING: licence is MIT. [LIT-BACKED: huggingface.co/datasets/openai/openai_humaneval; github.com/openai/human-eval, 2021]
- LOAD-BEARING: size is 164 hand-written Python programming problems (single test split). [LIT-BACKED: huggingface.co/datasets/openai/openai_humaneval; arXiv:2107.03374, 2021]
- LOAD-BEARING: metric is pass@k functional correctness (unit-test pass rate), most commonly pass@1. [LIT-BACKED: arXiv:2107.03374, 2021]

### 3.2 MBPP (Mostly Basic Python Problems)

- LOAD-BEARING: canonical source — Austin et al., "Program Synthesis with Large Language Models", 2021. [LIT-BACKED: arXiv:2108.07732, 2021]
- LOAD-BEARING: licence is CC-BY-4.0. [LIT-BACKED: huggingface.co/datasets/google-research-datasets/mbpp, 2021]
- LOAD-BEARING: size is ~974 crowd-sourced Python problems (full split); a hand-verified "sanitized" subset of 427 problems. [LIT-BACKED: huggingface.co/datasets/google-research-datasets/mbpp; arXiv:2108.07732, 2021]
- LOAD-BEARING: metric is pass@1 functional correctness (unit-test pass rate). [LIT-BACKED: arXiv:2108.07732, 2021]

### 3.3 SWE-bench (original, for lineage)

- LOAD-BEARING: canonical source — Jimenez, Yang, Wettig, Yao, Pei, Press & Narasimhan, "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", ICLR 2024. [LIT-BACKED: arXiv:2310.06770, 2024]
- LOAD-BEARING: licence is MIT (the SWE-bench harness/repo). [LIT-BACKED: github.com/SWE-bench/SWE-bench LICENSE, 2024]
- LOAD-BEARING: size is 2,294 task instances drawn from 12 popular Python repositories. [LIT-BACKED: arXiv:2310.06770, 2024]
- LOAD-BEARING: metric is percent of issues resolved (generated patch makes fail-to-pass and pass-to-pass tests pass). [LIT-BACKED: arXiv:2310.06770, 2024]

### 3.4 SWE-bench Verified

- LOAD-BEARING: canonical source — OpenAI, "Introducing SWE-bench Verified", 2024-08-13; a human-validated subset of the SWE-bench test set built with the SWE-bench authors. [LIT-BACKED: openai.com/index/introducing-swe-bench-verified, 2024]
- LOAD-BEARING: size is 500 instances human-validated to be non-problematic (clear problem statement, correct test patch, solvable). [LIT-BACKED: openai.com/index/introducing-swe-bench-verified, 2024]
- LOAD-BEARING: metric is percent of issues resolved (same harness as SWE-bench); GPT-4o resolved 33.2% at release. [LIT-BACKED: openai.com/index/introducing-swe-bench-verified, 2024]
- LOAD-BEARING: DEPRECATED — RESOLVED at source: OpenAI, "Why SWE-bench Verified no longer measures frontier coding capabilities" (~2026-02-23), states SWE-bench Verified no longer measures frontier coding capability. [LIT-BACKED: openai.com/index/why-we-no-longer-evaluate-swe-bench-verified, 2026]
- LOAD-BEARING: deprecation reason 1 — CONTAMINATION: frontier models reproduce the original human-written gold patch (and verbatim problem-statement specifics) on Verified tasks, indicating training exposure, so gains reflect exposure rather than software-engineering ability. [LIT-BACKED: openai.com/index/why-we-no-longer-evaluate-swe-bench-verified, 2026]
- LOAD-BEARING: deprecation reason 2 — FLAWED TESTS: OpenAI audited a 27.6% subset of the problems models often fail and found at least 59.4% of the audited problems have flawed test cases that reject functionally-correct submissions. [LIT-BACKED: openai.com/index/why-we-no-longer-evaluate-swe-bench-verified, 2026]
- LOAD-BEARING: OpenAI recommends SWE-bench Pro as the replacement, reporting it suffers less from contamination (no model produced a complete verbatim gold patch). [LIT-BACKED: openai.com/index/why-we-no-longer-evaluate-swe-bench-verified, 2026]
- LOAD-BEARING: SOURCING NOTE — the canonical openai.com announcement returns HTTP 403 to direct WebFetch from this box; its content was read via WebSearch and the date/percentages (2026-02-23; 27.6% audited; 59.4% flawed; ~138 hard problems audited; frontier models GPT-5.2 / Claude Opus 4.5 / Gemini 3 Flash reproducing gold patches) corroborated against an independently-fetchable secondary write-up. [LIT-BACKED: buildmvpfast.com/blog/benchmark-contamination-ai-coding-leaderboard-swe-bench-2026; codingfleet.com/blog/swe-bench-pro-explained-the-new-standard-for-ai-coding-benchmarks-2026, 2026]

### 3.5 SWE-bench Pro

- LOAD-BEARING: canonical source — Scale AI, "SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?", 2025. [LIT-BACKED: arXiv:2509.16941, 2025]
- LOAD-BEARING: size is 1,865 total tasks across 41 repositories — a Public set of 731 instances (11 repos, open on HuggingFace ScaleAI/SWE-bench_Pro), a Commercial set of 276 (18 private startup codebases), and a Held-out set of 858 (12 repos). [LIT-BACKED: arXiv:2509.16941; huggingface.co/datasets/ScaleAI/SWE-bench_Pro, 2025]
- LOAD-BEARING: the Public and Held-out sets are drawn exclusively from strong-copyleft (GPL-family) repositories as a deliberate contamination-resistance measure — the copyleft terms deter inclusion in proprietary training corpora, so benchmark instances inherit their source repositories' GPL-family licences. [LIT-BACKED: arXiv:2509.16941; scale.com/blog/swe-bench-pro, 2025]
- LOAD-BEARING: tasks exclude trivial 1–10-line edits; reference solutions average 107.4 lines of code across 4.1 files. [LIT-BACKED: arXiv:2509.16941, 2025]
- LOAD-BEARING: metric is percent of tasks resolved; frontier models score ~23% on SWE-bench Pro versus ~70%+ on SWE-bench Verified, the gap OpenAI cites as evidence of Verified's contamination. [LIT-BACKED: arXiv:2509.16941, 2025; openai.com/index/why-we-no-longer-evaluate-swe-bench-verified, 2026]

---

## 4. The two flagged open items — resolved

- LOAD-BEARING: SWE-bench Verified DEPRECATION resolved — OpenAI, "Why SWE-bench Verified no longer measures frontier coding capabilities" (~2026-02-23), gives two reasons: training-data contamination (frontier models reproduce the gold patch) and flawed tests (59.4% of a 27.6%-audited hard subset reject correct solutions); OpenAI recommends SWE-bench Pro. [LIT-BACKED: openai.com/index/why-we-no-longer-evaluate-swe-bench-verified, 2026]
- LOAD-BEARING: TriviaQA LICENCE resolved — Apache-2.0, applying to both code and data per the official repository README, with the caveat that the underlying trivia questions/documents are third-party copyright. [LIT-BACKED: github.com/mandarjoshi90/triviaqa, 2017]

---

## 5. UNVERIFIED / caveats

- The exact CLUTRR pre-generated split row counts are not asserted here: CLUTRR is a generator and the paper fixes no single size, so any specific N depends on the generation config chosen at experiment time (verify the pinned split at freeze).
- PIQA's licence is AFL-3.0 per the official distribution; the HuggingFace mirror (ybisk/piqa) records licence as "unknown", so downstream tooling that reads HF metadata should not treat PIQA as unlicensed — cite the official source.
- The SWE-bench Verified deprecation percentages/date were read from the canonical openai.com page via WebSearch (direct WebFetch returned HTTP 403) and corroborated against two independently-fetchable secondary write-ups; treat the exact 2026-02-23 date as "on/around" pending a direct fetch of the openai.com page.
- No benchmark in the required set was left wholly unverifiable at source; all canonical sources, licences, sizes, and metrics above were confirmed on 2026-07-10.
