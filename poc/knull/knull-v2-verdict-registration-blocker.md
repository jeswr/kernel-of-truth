# knull-v2 formal verdict registration — blocked by a pinned-script interface defect

Coordinator custody note (2026-07-13). The knull-v2 **mechanical verdict is settled and NOT in
question**: the pinned SAP `analysis/knull_v3.py` (sha `54528cd4…`, matches `/pins/analysis_script`)
on the complete 36-cell merged campaign gives `tost_equivalent=True`, superior/inferior `False`, all
instrument gates `True` → by the frozen `verdict_rules` (rule 2) the verdict is **NULL**. This is
committed (`fb9deb91`) and interpreted (`docs/next/analysis/knull-v2-interpretation.md`).

What is blocked is only the **formal chain-verified registration** into
`registry/verdicts/knull-v2.json` via the canonical `verdict-gen` path. A guardrailed registry-mechanic
agent investigated and STOPPED (writing nothing) with a rigorous diagnosis:

## The defect
`verdict-gen` runs the pinned analysis script as `[python, <script>]` with eligible run records on
**stdin, no argv**. But `knull_v3.py` is the designer's **CLI tool**, not a stdin adapter, so it fails
verdict-gen three independent, structural ways:
1. **argparse-required flags → exits 2** (`--records/--item-meta/--out` required) ⇒ verdict-gen raises
   `ERR_P2_ANALYSIS`. No verdict producible.
2. **Needs `--item-meta`**, which verdict-gen has no channel to supply (stdin only).
3. **Reads top-level fields the log schema forbids** (`arm/cell/rung/seed/cov/flops_per_query` at record
   top level; `kot-log-1.json` is `additionalProperties:false`). No lawful `log-append` record can carry
   them at top level.

## This is the EXACT defect rules-1-c already hit and fixed
The canonical pattern (proven by `analysis/f2b_replicate.py`, `analysis/rules_1c_stdin.py`,
`analysis/rules_2_go_stdin.py`, `analysis/engine_inference_stdin.py`) is a **stdin adapter**: reads
eligible runs as JSONL from stdin (no argv), takes cell coords from each record's `config`, loads heavy
per-item rows from an `artifacts`-pinned campaign file (sha re-verified). **No `knull_*_stdin.py`
exists.** `registry/corrections/rules-1-c/2-prefreeze-correction.json` documents rules-1-c hitting the
identical "CLI pin argparse-exits-2 ⇒ ERR_P2_ANALYSIS" and fixing it via a **pre-final reset-refreeze**
swapping in the stdin successor (which rewrote `pins.analysis_script` path+sha and the record's
`frozen_sha256`).

## Window status
knull-v2 is **NOT GNG-0-signed** and has **no final-phase (results-log) run** yet, so by the programme's
formal definition it is still *pre-final* — the rules-1-c-style pre-final reset-refreeze window is
lawfully open. The one subtlety: knull-v2's **RT-15 external timestamp was already posted** against the
current `frozen_sha256` (`d04e7364…`); a reset-refreeze mints a NEW hash the external post does not cover.

## Options (maintainer decision — see the issue)
- **(A) Hand-author the verdict file** with the direct-SAP result + provenance, noting the verdict-gen
  path is blocked by the interface gap; file a separate infra bead for the adapter. Fast; bypasses the
  canonical chain-verified path.
- **(B) rules-1-c-style fix (recommended, precedented):** author `analysis/knull_v3_stdin.py` (stdin-
  conformant; item-meta + merged rows pinned as `artifacts`; **prove byte-identical statistics** to
  `knull_v3.py`), register a correction, do a lawful **pre-final reset-refreeze**, then run the
  canonical ingest → `verdict-gen` → NULL. Statistics — and therefore the NULL verdict — cannot change
  (parity-proven); only the pinned interface changes. Requires re-posting the RT-15 hash.
- **(C) Defer:** leave the mechanical NULL (committed + interpreted) as the working result; register
  formally later. Zero integrity risk; the formal verdict file stays absent for now.

The mechanical verdict is unaffected by the choice; this is purely *how* to formally record an
already-determined NULL, plus whether to re-freeze post-RT-15.
