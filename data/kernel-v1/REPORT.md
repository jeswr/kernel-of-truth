# F1-K kernel-v1 — first-100 concept set

Assembled from the `consensus-100` first-100 F1-K selection
(`poc/scale/consensus-100/concepts-100.json`). Luna explications with a sol
backstop for the six concepts Luna scored `<2` on. Nothing regenerated: the 94
Luna records are the committed `poc/scale/consensus-100/gen/<slug>.gpt56luna.json`
files (quality `>=2`); the 6 sol records are the escalations written under
`/tmp/kv1-escalate/`. Records copied verbatim into `concepts/<slug>.json` using
the pilot's slug naming (`artist's model -> artists-model.json`).

## Totals

| metric | value |
|---|---|
| total concepts | **100** |
| Luna (reused, quality >= 2) | **94** |
| sol (escalated, Luna < 2) | **6** |

Escalated to sol: `lover`, `appearance`, `fidelity`, `dig`, `poisoning`,
`boring`.

## AST adequacy (kot-ast/1 vs the gloss)

Tag taken from **each record's own AST-adequacy self-flag** (the `notes` field —
all 100 records carried one, so the pilot `lossy_ast` heuristic backstop was not
needed).

| | faithful | lossy | total |
|---|---|---|---|
| Luna | 7 | 87 | 94 |
| sol | 2 | 4 | 6 |
| **all** | **9** | **91** | **100** |

Faithful (9): `appearance` (sol), `fidelity` (sol), `exit`, `deposition`,
`equality`, `service`, `contamination`, `combustion`, `cognitive-state`
(the last seven are Luna). The 91 lossy explications are admitted under the
maintainer's issue-#33 *admit-lossy-to-top-up* policy; `manifest.json` orders
the set **prefer-faithful** (all 9 faithful first, 91 lossy last).

## Realized cluster coverage vs the power gate

Computed by rerunning the frozen `poc/scale/f1k-eligibility/screen_candidates.py`
operationalisation **restricted to the 100 selected synsets** (`coverage_kv1.py`;
artifact `coverage-kv1.json`). The screener as shipped screens the whole 110,049
WN31 type-level pool and has no concept-subset flag, so the restriction was done
by reusing its own functions — `parse_wn_dict` / `build_pool` / `Matcher` /
`load_items` — building the trigger index over only the 100 synsets and running
the identical SOP-4 eligibility + SOP-5 greedy scarcest-first disjoint
assignment over just those concepts. This is exact, not an estimate: per-concept
`m` is pool-independent (OP-4 presence-only matching), and a cross-check of the
recomputed `m_total` against the `m_test_screen` recorded in `concepts-100.json`
showed **0 / 100 mismatches**.

Eval supply: the five sha256-pinned snapshots (MMLU / ARC-Easy / ARC-Challenge /
OpenBookQA / CSQA), 19,311 admitted items.

| bound (m >= 8 on mutually disjoint items) | C | >= 65 gate |
|---|---|---|
| **raw disjoint** | **100** | **PASS** |
| header/cue-collision-free disjoint | 100 | PASS |
| conservative (unambiguous-lemma evidence only) | 7 | fail |

- All 100 concepts individually reach `m_total >= 8`; all 100 are
  header/cue-collision-free; and all 100 **simultaneously** secure 8 mutually
  disjoint eval items (contention among 100 concepts drawing 800 items from
  19,311 is negligible). Realized **C = 100**.
- The conservative bound (each of the 8 disjoint items matched via a
  *monosemous direct lemma*) is 7. This is the same strict adequacy statement
  the screener reports pool-wide (1,475 there); restricted to 100 hand-selected
  concepts it is naturally small and is **not** the metric ASM-2271 gates on.
  The gate arithmetic in `coverage-report.json` treats the raw / header-clean
  disjoint bound as the operative `C`.

## Verdict

**Clears the power gate.** Realized `C = 100 >= 65` (ASM-2271), with 35 clusters
of headroom. The kernel-v1 first-100 set is powered.

## Files

- `concepts/<slug>.json` — 100 concept records (94 Luna + 6 sol), pilot naming.
- `manifest.json` — per-concept `{label, synset, source, ast_adequacy}`, ordered
  prefer-faithful.
- `coverage-kv1.json` — realized-coverage computation output (C bounds,
  per-concept eligibility, m-crosscheck).

Uncommitted — left under `data/kernel-v1/` for the coordinator.
