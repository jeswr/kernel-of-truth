# Systemic finding: CLI-only analysis pins break the verdict-gen path

Coordinator note (2026-07-13). Surfaced while verifying UFO-CHECK-0 freeze-readiness: its pinned
analysis script is CLI-only (argparse-required, reads files) so `verdict-gen` (which runs the pinned
script with **no argv, records on stdin**) fails it with `ERR_P2_ANALYSIS`. This is the **same defect
knull-v2 hit** (issue #34). A heuristic sweep of every `registry/experiments/*.json` `pins.analysis_script`
shows it is **not isolated** — many pinned analysis scripts are CLI-only or not obviously stdin-conformant.

## Method + caveat
Crude static check per experiment: does the pinned script contain `sys.stdin` (→ likely STDIN-OK) vs a
`required=True` argparse arg (→ CLI-ONLY)? **This is a heuristic** — it misses arg-required patterns that
don't use the literal `required=True` (e.g. `knull_v3.py` post-parse checks read as "no-argv?" but ARE
CLI-only), and it does not confirm which experiments actually route through verdict-gen. Treat the list as
"audit these," not "these are all broken."

## Actionable split
- **DRAFT experiments with CLI-only pins → fix PRE-FREEZE (clean, no re-freeze), before each freezes:**
  `ddc0`, `ddc1`, `nsk1`, `rules-1-knull-ablation`, `rules-1-knull-cert`, `rules-1-knull-hostlift`,
  and `ufo-check-0` (being fixed now via `analysis/ufo_check_0_stdin.py`). Each needs a stdin-adapter
  successor (template: `analysis/rules_1c_stdin.py`, `analysis/rules_2_go_stdin.py`) with byte-identical
  statistics, IF it routes through verdict-gen (confirm per experiment; some may use a certificate path).
- **FROZEN, no verdict, CLI-only → per-case audit (post-freeze fix needs a re-freeze, like #34):**
  `knull-v2` (LIVE — issue #34), `knull` (superseded by knull-v2 — likely dead), `rules-1` (result is a
  registered CPU certificate, may not need verdict-gen), `rules-1-b` (superseded by rules-1-c, CLOSED —
  dead), `f2b-errors`, `a-f0-mint-economics` (confirm whether they need a verdict-gen verdict at all).
- **Already fine:** experiments carrying a registered verdict (they ran verdict-gen through a `*_stdin.py`
  adapter — e.g. rules-1-c, rules-2, f2b-replicate, deconf-b, g3-llmproxy-v3, truthstyle-2x2).

## Recommendation (preventive)
Add a **freeze-time gate** to `tools/registry/prereg-freeze.py`: before allowing DRAFT→FROZEN, execute the
pinned `analysis_script` the way verdict-gen will (no argv, a tiny fixture on stdin) and refuse the freeze
if it exits non-zero (would-be `ERR_P2_ANALYSIS`). That converts this latent, expensive-to-repair defect
(un-amendable `/pins/analysis_script` post-freeze) into a cheap pre-freeze failure for EVERY future
experiment — catching it exactly where UFO-CHECK-0's `--dry-run` could not (prereg-freeze does not run the
script today). Tooling change → careful/reviewed; recorded here as the systemic fix, not yet implemented.
