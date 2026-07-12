# g2 gold re-scoring handoff — pinned item set + rubric (PROVISIONAL-ON-LLM-PROXY)

**Purpose.** The g2 LLM-proxy run (maintainer directive #11) scored the Π read-out
against a two-LLM stand-in for the frozen two-human `g2.gold` (GATE-H). This file
pins EVERYTHING a later re-scorer needs to judge the SAME items under the SAME
rubric, so that (a) any additional independent LLM proxy pass and (b) the human
gold panel produce byte-comparable label sets for reconciliation. It designs
nothing and changes no frozen object.

## Already-run proxy annotators (do NOT re-run these two as "new" annotators)

- `judge-pA-gpt56sol` — GPT-5.6-Sol via npx-pinned `@openai/codex@0.144.1`,
  reasoning effort low, `-s read-only --ignore-user-config --ephemeral`,
  server-side output schema. **The GPT-5.6 proxy pass is therefore already inside
  the run** (it is annotator A, executed via the cross-vendor codex CLI).
- `judge-pB-haiku45` — `claude-haiku-4-5-20251001` via headless `claude -p`,
  tools disabled, no session persistence, thinking off. Vendor-family overlap
  with the materials' authoring agents DISCLOSED; never sole gold.

Both: stateless per-item calls, pinned prompt bytes, first-valid-answer-final,
randomized per-judge item order (seeds in `materials/manifest.json`), blinding
scan on every call surface. Harness: `poc/g2/run-g2lp.py` (pins in-file).

## Pinned re-scoring package (hand these bytes to any new annotator, LLM or human)

| file | sha256 | role |
|---|---|---|
| `poc/g2/materials/items.jsonl` | `7a4728840550227703338880a79f61491a3c93e5022f07215631f6caa7077008` | the n=84 real items. Give the annotator ONLY the `item` field text per `id`. The `rule`/`form`/`subject` fields are provenance metadata — do NOT show them (they reveal the Π derivation rule). |
| `poc/g2/materials/prompt-template.txt` | `d8724154a740e8c0e7174f9a083f6a8411dfb5fda17c87d6d52acfb4da31dcac` | the rubric. `{{ITEM}}` is replaced by the item text. Human panel: use the same wording as written instructions; the answer vocabulary is {yes, no, cannot-say}. |
| `poc/g2/materials/output-schema.json` | `c43725989beb58f8e65f952e00dea9c0d2896148d732277bd50402708ed4b13f` | machine answer contract (LLM annotators). |
| `poc/g2/materials/calibration-items.jsonl` | `a2ba97735a437f704f0dcc79af8a5efdc7cc4c549f394da4d973691f9afb9d59` | 2 preflight sanity items with known answers (annotator must get both right before the real block). |
| `poc/g2/materials/probes.jsonl` | `bc181daf5b77925c882d4c3edea92635ce054ab10c5d76879646953d78158962` | 20 deranged-sort probe items (false-satisfaction instrument check; interleave or run as a block, expected answer "no" by construction). |
| `poc/g2/materials/manifest.json` | `81c15ef582b338e53bd0e66bf7a41a3806f04ca11e02cbcba49e1b9eebdbccdc` | order seeds + derangement map + dump sha. New annotators get a FRESH order seed (`g2lp/1|<annotator-id>|<date>`, same sort-by-sha rule as `run-g2lp.py::_run_block`). |

**Blinding rules (binding).** The annotator must never see: `poc/g2/pi-derived.jsonl`,
the Π projector, the other annotators' labels, `poc/g2/result.json`, or any
statement that these items came from a derivation system. Items are phrased as
ordinary-meaning questions about English concepts; keep it that way.

**Output contract per annotator.** One JSONL line per item:
`{"id": "<g2:pi:NNN>", "answer": "yes|no|cannot-say"}` — file name
`judge-<annotator-id>-real-responses.jsonl` shape as produced by the harness.

**Reconciliation protocol (human gold, when it arrives).** Per the frozen g2
record: 2 independent human annotators, disagreements adjudicated blind BEFORE
scoring; then re-run `poc/g2/run-g2lp.py assemble`-equivalent scoring with the
adjudicated labels as gold and the pinned `analysis/g2.py`
(sha `04deddcf9f1496df2da72e7965a9b2ceca69a1d87e8086f209d9045231a6f5ce`).
All LLM-proxy labels are quarantined from human annotators (ASM-0553 pattern).

**Known frozen-design gap (disclosed, not fixable by any annotator).** The FULL
Π dump over pinned kernel-v0 yields 84 judgeable subsumption/read-out items;
the frozen `n_planned` = 500 and the pinned instrument gate `n_gold >= 500`
are unattainable on this corpus for ANY annotator, human or LLM. The mechanical
verdict on this corpus is therefore INSTRUMENT-INVALID by the n-gate regardless
of precision; the precision numbers are estimation-only until the maintainer
either amends the record (ops amendment path named in the pin:
`PINNED-AT-INPUTS:g2.gold ... ops amendment before any final-phase run`) or the
kernel grows enough records to make n=500 reachable.
