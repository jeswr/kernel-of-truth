#!/usr/bin/env python3
"""SCAFFOLD — E1 core-freezing grid + E4 emission test on Modal (NOT runnable).

Full port tracked in bead kernel-of-truth-af7. This file exists to fix the
SHAPE of the port while the E2 wrapper (modal_e2.py) is the working reference:
every stage of poc/e1/run_all.sh + poc/e4/runner/run_e4.sh maps onto a Modal
function below with the right resources, and the pre-registered 5-arms x
5-seeds grid becomes parallel Modal calls instead of a serial loop on one box.

Why this beats the AWS serial path on wall-clock (NOT on protocol — the
pre-registration is unchanged; per-run determinism is seed-keyed, so run
ORDER is immaterial):

    AWS g5.xlarge serial (poc/gpu/README.md cost table)   ~20-21 h
    Modal parallel:
      fetch + build_data (CPU fn, serial today)            ~4 h   <- bottleneck;
                                                                     bead 0r1
                                                                     parallelises it
      LR sweep: 15 jobs (5 arms x 3 LRs) via starmap       ~25 min (max of 15)
      grid: 25 jobs (5 arms x 5 seeds) via starmap         ~30 min (max of 25)
      evals: 35 jobs via starmap                           ~15 min
      stats + verdict (CPU fn)                             ~5 min
      TOTAL                                                ~4-5 h wall

Serial-vs-parallel is possible because arms/seeds are independent by
construction (Common rule 1: shards, story order, substitution draws and
batch schedule are functions of the seed index only) — the only cross-job
data flow is the Common-rule-5 LR selection barrier between sweep and grid.

Persistent state lives in Modal Volume `kot-e1-work` (corpus, uint16 shards,
checkpoints, eval JSONs — the /opt/e1work of the AWS path), mounted read-write
in every function; E4 chains off the SAME volume (reads E1's data/ + ckpts/,
exactly like run_e4.sh consumes $E1_WORK read-only). Only results/ (eval
JSONs, verdicts, lr-selection — never checkpoints) is shipped back to the
coordinator, matching the AWS results-branch discipline.

The intended orchestration once ported (all pre-registered knobs unchanged):

    sel = {}   # Common rule 5 barrier
    sweep = list(lr_sweep.starmap((a, lr) for a in ARMS for lr in LRS))
    ...best-of-3 by val loss per arm -> sel[arm]...
    list(train_arm_seed.starmap((a, s, sel[a]) for a in ARMS for s in SEEDS))
    list(eval_ckpt.starmap(EVAL_JOBS))           # incl. step-0 baselines
    stats_verdict.remote()
    e4_build_emission.remote(); list(e4_finetune.starmap(E4_JOBS)); ...
"""

from __future__ import annotations

import sys
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

_SCAFFOLD = (
    "SCAFFOLD ONLY (bead kernel-of-truth-af7): the E1/E4 Modal port is not "
    "implemented yet — this file fixes the function/volume/parallelism shape. "
    "Run E2 instead: modal run poc/modal/modal_e2.py"
)

ARMS = ("kernel-frozen", "shuffled-frozen", "random-frozen", "trainable", "kernel-init")
SEEDS = (0, 1, 2, 3, 4)
LRS = ("3e-4", "6e-4", "1e-3")   # Common rule 5 sweep grid, seed 0, half budget
E1_WORK = "/vol/e1work"          # Volume mount — the /opt/e1work of the AWS path

app = modal.App("kot-e1e4")

# One programme image (same pins as E2 — torch/numpy are what E1/E4 need; the
# unused transformers pin is the price of a single cached image). The full
# port adds poc/e1 + poc/e4 sources via add_local_dir, exactly as modal_e2.py
# stages poc/e2 (and with the same manifest fail-closed assertion).
def _pins() -> list:
    lines = (_HERE / "requirements-image.txt").read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


image = modal.Image.debian_slim(python_version="3.11").pip_install(*_pins())
work = modal.Volume.from_name("kot-e1-work", create_if_missing=True)
_VOL = {E1_WORK: work}


@app.function(image=image, volumes=_VOL, timeout=2 * 3600, cpu=4, memory=16384)
def fetch_corpus() -> str:
    """TinyStories-train fetch -> {E1_WORK}/corpus/ (idempotent, sha-verified).
    AWS equivalent: the fetch stage of user-data-e1-pull.sh.tpl."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, timeout=8 * 3600, cpu=8, memory=32768)
def build_data(seeds: str = "0,1,2,3,4") -> str:
    """poc/e1/pipeline/build_data.py -> {E1_WORK}/data (annotate once, per-seed
    p=0.5 substitution, uint16 shards). CPU-bound, GPU-free — on Modal it runs
    on a cheap CPU-only container instead of idling a GPU for ~4 h like the
    AWS path does. Serial today; bead kernel-of-truth-0r1 parallelises pass
    A/B, which would drop the programme's wall-clock bottleneck."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=4 * 3600)
def lr_sweep(arm: str, lr: str) -> dict:
    """One (arm, lr) half-budget run on seed 0 (train_e1.py --budget-frac 0.5
    --no-checkpoints); returns the summary dict for LR selection. 15 of these
    run CONCURRENTLY via lr_sweep.starmap(...) — the AWS path loops them."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, timeout=1800)
def select_lrs(summaries: list) -> dict:
    """Common rule 5: best-of-3 by val loss per arm, then FIXED for all seeds;
    writes lr-selection.json to the volume (committed with results)."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=6 * 3600)
def train_arm_seed(arm: str, seed: int, lr: str) -> str:
    """One full-budget train_e1.py run: checkpoints at step-0/50%/100% into
    {E1_WORK}/ckpts, frozen-row bit-identity asserted by the trainer itself.
    THE parallel-arms pattern: 25 of these via train_arm_seed.starmap(...) —
    no quota, so the grid's wall-clock is max(single run) ~30 min, not 12 h."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=2 * 3600)
def eval_ckpt(arm: str, seed: int, tag: str) -> dict:
    """poc/e1/eval/eval_e1.py on one checkpoint (7 evals/seed incl. the step-0
    circularity baselines = 35 jobs, all parallel)."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, timeout=3600, cpu=4)
def stats_verdict() -> dict:
    """poc/e1/eval/stats_e1.py: pre-registered statistics + verdict JSON/md;
    returns {rel path: bytes} of results/ for the coordinator (modal_e2.py's
    unpack + provenance-sidecar treatment applies unchanged)."""
    raise NotImplementedError(_SCAFFOLD)


# ---- E4 (chained off the same volume, run_e4.sh stages; bead hkp lineage) ----

@app.function(image=image, volumes=_VOL, timeout=3600, cpu=4)
def e4_build_emission() -> str:
    """Fail-closed gloss/vector pins, then poc/e4/pipeline/build_emission.py
    against E1's real vocab.json on the volume (leakage gates fail closed)."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=4 * 3600)
def e4_finetune(arm: str, seed: int) -> str:
    """Emission fine-tune of one (arm, seed) E1 checkpoint with E1's freezing
    discipline (3 arms x 5 paired seeds = 15 parallel jobs)."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, gpu="A10G", timeout=2 * 3600)
def e4_eval(arm: str, seed: int) -> dict:
    """1,054-way candidate-restricted eval (tier-1/tier-2 holdouts)."""
    raise NotImplementedError(_SCAFFOLD)


@app.function(image=image, volumes=_VOL, timeout=3600, cpu=4)
def e4_stats() -> dict:
    """Pre-registered E4 stats + verdict (stats_e4.py), shipped like E1's."""
    raise NotImplementedError(_SCAFFOLD)


@app.local_entrypoint()
def main() -> None:
    print(__doc__)
    raise SystemExit(2)
