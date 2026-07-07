#!/usr/bin/env python3
"""E1+E4 Modal-port helpers (bead kernel-of-truth-af7) — stdlib only, NO modal
import. Shipped verbatim into the container via Image.add_local_python_source
and unit-tested token-free (poc/modal/test_modal_e1e4.py).

TRANSPORT, NOT SCIENCE: nothing here reimplements poc/e1 / poc/e4 logic. The
per-run CLI argv, the LR-selection rule, the E4 pin gate and the mock corpus
are all taken FROM the committed drivers (poc/e1/run_all.sh,
poc/e4/runner/run_e4.sh) — bash arrays are parsed out of the staged script
bytes and the embedded python heredocs are extracted and executed verbatim —
so any drift between this wrapper and the AWS path is a parse failure or a
manifest mismatch, never a silent fork. Paired-seed batch-schedule fidelity
follows: the wrapper passes run_all.sh's exact argv (asserted in tests
against the script bytes), and poc/e1/train/train_e1.py derives the schedule
from (seed, shard, batch size, steps) alone.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shlex

# ---------------------------------------------------------------------------
# Staged bytes: every file the E1 grid + E4 chain consume at run time.
# Keys/paths are repo-relative; the coordinator computes a sha-256 manifest
# over them and every container call re-computes + asserts it (fail closed).
# poc/e4/inputs/synthetic-concepts.json + gloss-report.json are PREP artifacts
# (not consumed by build_emission/finetune/eval/stats) and are not staged.
# ---------------------------------------------------------------------------

STAGE_FILES = (
    "poc/e1/run_all.sh",                       # argv + LR-rule source of truth
    "poc/e1/pipeline/build_data.py",
    "poc/e1/pipeline/detstream.py",
    "poc/e1/pipeline/kernel_mapper.py",
    "poc/e1/pipeline/mock_tables.py",
    "poc/e1/train/train_e1.py",
    "poc/e1/eval/eval_e1.py",
    "poc/e1/eval/stats_e1.py",
    "poc/e1/smoke/check_smoke.py",             # independent mock assertions
    "poc/e1/inputs/cloze-templates.json",
    "poc/e1/inputs/mapper-lexicon.json",
    "poc/e1/inputs/mapper-parity-fixture.json",
    "poc/e1/inputs/vector-tables-d512.json",
    "poc/e4/runner/run_e4.sh",                 # argv + pin-gate source of truth
    "poc/e4/runner/finetune_e4.py",
    "poc/e4/runner/eval_e4.py",
    "poc/e4/runner/stats_e4.py",
    "poc/e4/runner/mock_tables_e4.py",
    "poc/e4/runner/check_smoke.py",
    "poc/e4/pipeline/build_emission.py",
    "poc/e4/GLOSS-HASH.txt",
    "poc/e4/inputs/glosses.jsonl",
    "poc/e4/inputs/holdout-manifest.json",
    "poc/e4/inputs/vector-tables-manifest.json",
    "poc/e4/inputs/vectors/kernel-d512.f32",
    "poc/e4/inputs/vectors/random-d512-seed0.f32",
    "poc/e4/inputs/vectors/random-d512-seed1.f32",
    "poc/e4/inputs/vectors/random-d512-seed2.f32",
    "poc/e4/inputs/vectors/random-d512-seed3.f32",
    "poc/e4/inputs/vectors/random-d512-seed4.f32",
)

CORPUS_URL = ("https://huggingface.co/datasets/roneneldan/TinyStories/resolve/"
              "main/TinyStories-train.txt")   # verbatim from user-data-e1-pull.sh.tpl


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_manifest(root: str, rel_paths=STAGE_FILES) -> dict:
    """{repo-relative path: sha256} over the exact bytes staged into the image.
    Computed on the coordinator AND inside every container call; any drift
    fails the run closed (ERR_STAGING_MISMATCH in modal_e1e4.py)."""
    return {rel: sha256_file(os.path.join(root, rel)) for rel in sorted(rel_paths)}


def manifest_digest(manifest: dict) -> str:
    return hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode()).hexdigest()


# ---------------------------------------------------------------------------
# Parsing the committed drivers (fail closed on any shape change)
# ---------------------------------------------------------------------------


def _read(root: str, rel: str) -> str:
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def script_branch(text: str, mode: str) -> str:
    """The mock|full branch body of run_all.sh / run_e4.sh ($MODE dispatch)."""
    i_mock = text.index('if [ "$MODE" = mock ]; then')
    i_full = text.index('elif [ "$MODE" = full ]; then')
    i_else = text.index("\nelse", i_full)
    if mode == "mock":
        return text[i_mock:i_full]
    if mode == "full":
        return text[i_full:i_else]
    raise SystemExit(f"ERR_PARSE: unknown mode {mode!r}")


def bash_array(branch: str, name: str, subst: dict | None = None) -> list:
    """Tokens of NAME=( ... ) in a branch (no nested parens in the drivers).
    $VAR tokens are substituted from `subst` (fail closed on unknown $vars)."""
    m = re.search(rf"^\s*{re.escape(name)}=\(", branch, flags=re.M)
    if not m:
        raise SystemExit(f"ERR_PARSE: bash array {name} not found")
    end = branch.index(")", m.end())
    toks = shlex.split(branch[m.end():end])
    out = []
    for t in toks:
        if t.startswith("$"):
            key = t[1:].strip("{}")
            if not subst or key not in subst:
                raise SystemExit(f"ERR_PARSE: unsubstituted ${key} in {name}")
            t = subst[key]
        elif "$" in t:
            raise SystemExit(f"ERR_PARSE: embedded $var in {name} token {t!r}")
        out.append(t)
    return out


def bash_var(branch: str, name: str) -> str:
    m = re.search(rf'^\s*{re.escape(name)}="([^"]*)"', branch, flags=re.M)
    if not m:
        raise SystemExit(f"ERR_PARSE: bash var {name} not found")
    return m.group(1)


def bash_array_toplevel(text: str, name: str) -> list:
    """A top-level NAME=( ... ) array (e.g. ARMS in both drivers)."""
    m = re.search(rf"^{re.escape(name)}=\(", text, flags=re.M)
    if not m:
        raise SystemExit(f"ERR_PARSE: top-level array {name} not found")
    end = text.index(")", m.end())
    return shlex.split(text[m.end():end])


def heredocs(text: str, marker: str) -> list:
    """Embedded heredoc bodies (<<'MARKER' ... MARKER), in file order."""
    blocks, cur = [], None
    for line in text.splitlines():
        if cur is not None:
            if line.strip() == marker:
                blocks.append("\n".join(cur) + "\n")
                cur = None
            else:
                cur.append(line)
        elif f"<<'{marker}'" in line:
            cur = []
    if cur is not None:
        raise SystemExit(f"ERR_PARSE: unterminated heredoc {marker}")
    return blocks


def lr_selection_code(root: str) -> str:
    """run_all.sh's OWN best-of-sweep-by-val-loss snippet (Common rule 5).
    Executed verbatim: python -c CODE <sweep_dir> <out_json>."""
    code = heredocs(_read(root, "poc/e1/run_all.sh"), "PYEOF")[0]
    if "Common rule 5" not in code:
        raise SystemExit("ERR_PARSE: run_all.sh LR-selection heredoc not recognised")
    return code


def fixed_lr_code(root: str) -> str:
    """run_all.sh's OWN mock fixed-LR snippet: python -c CODE <out_json> <lr>."""
    code = heredocs(_read(root, "poc/e1/run_all.sh"), "PYEOF")[1]
    if "mock mode" not in code:
        raise SystemExit("ERR_PARSE: run_all.sh fixed-LR heredoc not recognised")
    return code


def pin_check_code(root: str) -> str:
    """run_e4.sh's OWN holdout-manifest pin gate:
    python -c CODE <holdout.json> <gloss_sha> <tables_manifest_sha>."""
    code = heredocs(_read(root, "poc/e4/runner/run_e4.sh"), "PYEOF")[0]
    if "ERR_GLOSS_PIN" not in code or "ERR_TABLES_PIN" not in code:
        raise SystemExit("ERR_PARSE: run_e4.sh pin-check heredoc not recognised")
    return code


def mock_corpus_code(root: str) -> str:
    """run_e4.sh's OWN synthetic mock-corpus generator (gloss-free by
    construction): python -c CODE <corpus_path>."""
    code = heredocs(_read(root, "poc/e4/runner/run_e4.sh"), "EOF")[0]
    if "mock corpus" not in code:
        raise SystemExit("ERR_PARSE: run_e4.sh mock-corpus heredoc not recognised")
    return code


def gloss_pin(root: str) -> str:
    """The published gloss hash, parsed exactly like run_e4.sh's sed."""
    m = re.search(r"= ([0-9a-f]{64})", _read(root, "poc/e4/GLOSS-HASH.txt"))
    if not m:
        raise SystemExit("ERR_GLOSS_PIN: no sha-256 in GLOSS-HASH.txt")
    return m.group(1)


# ---------------------------------------------------------------------------
# Mode tables (mock|full), parsed from the drivers at call time
# ---------------------------------------------------------------------------


def e1_mode(root: str, work: str, mock: bool) -> dict:
    text = _read(root, "poc/e1/run_all.sh")
    br = script_branch(text, "mock" if mock else "full")
    seeds = bash_var(br, "SEEDS")
    tables = (f"{work}/vector-tables-mock-d64.json" if mock
              else f"{root}/poc/e1/inputs/vector-tables-d512.json")
    return {
        "seeds": seeds,
        "seed_list": [int(s) for s in seeds.split(",")],
        "arms": tuple(bash_array_toplevel(text, "ARMS")),
        "model_args": bash_array(br, "MODEL_ARGS"),
        "data_args": bash_array(br, "DATA_ARGS"),
        "lrs": bash_array(br, "LRS"),
        "stats_extra": bash_array(br, "STATS_EXTRA"),
        "tables": tables,
        "verdict_name": bash_var(br, "OUT_PREFIX").rsplit("/", 1)[-1],
    }


def e4_mode(root: str, work: str, mock: bool) -> dict:
    text = _read(root, "poc/e4/runner/run_e4.sh")
    br = script_branch(text, "mock" if mock else "full")
    seeds = bash_var(br, "SEEDS")
    tables = (f"{work}/e4tables/vector-tables-mock-manifest.json" if mock
              else f"{root}/poc/e4/inputs/vector-tables-manifest.json")
    return {
        "seeds": seeds,
        "seed_list": [int(s) for s in seeds.split(",")],
        "arms": tuple(bash_array_toplevel(text, "ARMS")),
        "build_args": bash_array(br, "BUILD_ARGS", subst={"SEEDS": seeds}),
        "ft_args": bash_array(br, "FT_ARGS"),
        "stats_extra": bash_array(br, "STATS_EXTRA"),
        "tables": tables,
        "verdict_name": bash_var(br, "OUT_PREFIX").rsplit("/", 1)[-1],
    }


# ---------------------------------------------------------------------------
# Per-run argv builders — token-for-token the drivers' invocations
# ---------------------------------------------------------------------------


def corpus_path(work: str, mock: bool) -> str:
    return f"{work}/corpus/" + ("corpus-mock.txt" if mock else "TinyStories-train.txt")


def build_data_argv(py: str, root: str, work: str, mode: dict, mock: bool) -> list:
    # run_all.sh [1/5]: build_data.py --corpus $CORPUS --out $DATA --seeds $SEEDS ${DATA_ARGS[@]}
    return [py, f"{root}/poc/e1/pipeline/build_data.py",
            "--corpus", corpus_path(work, mock), "--out", f"{work}/data",
            "--seeds", mode["seeds"], *mode["data_args"]]


def mock_tables_argv(py: str, root: str, work: str, mode: dict) -> list:
    # run_all.sh [1b]: mock_tables.py --d 64 --out $TABLES --seeds $SEEDS
    return [py, f"{root}/poc/e1/pipeline/mock_tables.py", "--d", "64",
            "--out", mode["tables"], "--seeds", mode["seeds"]]


def train_argv(py: str, root: str, work: str, mode: dict,
               arm: str, seed: int, lr: str, sweep: bool = False) -> list:
    # run_all.sh [2/5] (sweep) / [3/5] (grid) train_e1.py invocations
    out = f"{work}/ckpts/sweep" if sweep else f"{work}/ckpts"
    argv = [py, f"{root}/poc/e1/train/train_e1.py", "--data", f"{work}/data",
            "--tables", mode["tables"], "--arm", arm, "--seed", str(seed),
            "--lr", lr, "--out", out]
    if sweep:
        argv += ["--budget-frac", "0.5", "--no-checkpoints"]
    return argv + list(mode["model_args"])


def eval_argv(py: str, root: str, work: str, arm: str, seed: int, tag: str) -> list:
    # run_all.sh [4/5] eval_one
    return [py, f"{root}/poc/e1/eval/eval_e1.py",
            "--ckpt", f"{work}/ckpts/ckpt-{arm}-seed{seed}-{tag}.pt",
            "--data", f"{work}/data",
            "--out", f"{work}/evals/eval-{arm}-seed{seed}-{tag}.json"]


def stats_argv(py: str, root: str, work: str, mode: dict) -> list:
    # run_all.sh [5/5]
    return [py, f"{root}/poc/e1/eval/stats_e1.py", "--evals", f"{work}/evals",
            "--seeds", mode["seeds"],
            "--out-prefix", f"{work}/results/{mode['verdict_name']}",
            *mode["stats_extra"]]


def eval_jobs(seed_list) -> list:
    """run_all.sh [4/5] verbatim: 7 evals per seed incl. step-0 baselines."""
    jobs = []
    for seed in seed_list:
        jobs += [("kernel-frozen", seed, "step0"),
                 ("kernel-frozen", seed, "50pct"),
                 ("kernel-frozen", seed, "100pct"),
                 ("shuffled-frozen", seed, "100pct"),
                 ("random-frozen", seed, "100pct"),
                 ("trainable", seed, "100pct"),
                 ("kernel-init", seed, "100pct")]
    return jobs


def summary_name(arm: str, seed: int, lr: str, sweep: bool) -> str:
    # train_e1.py's own naming: summary-{run_id}[-frac{f}]-lr{args.lr}.json
    return (f"summary-{arm}-seed{seed}"
            + ("-frac0.5" if sweep else "") + f"-lr{float(lr)}.json")


def e4_mock_tables_argv(py: str, root: str, work: str, mode: dict) -> list:
    # run_e4.sh [3/6] mock
    return [py, f"{root}/poc/e4/runner/mock_tables_e4.py", "--d", "64",
            "--e1-tables", f"{work}/vector-tables-mock-d64.json",
            "--out", f"{work}/e4tables", "--seeds", mode["seeds"]]


def e4_build_argv(py: str, root: str, work: str, mode: dict) -> list:
    # run_e4.sh [2/6]
    return [py, f"{root}/poc/e4/pipeline/build_emission.py",
            "--e1-vocab", f"{work}/data/vocab.json", "--out", f"{work}/e4data",
            *mode["build_args"]]


def e4_ft_argv(py: str, root: str, work: str, mode: dict, arm: str, seed: int) -> list:
    # run_e4.sh [4/6]
    return [py, f"{root}/poc/e4/runner/finetune_e4.py",
            "--e1-ckpt", f"{work}/ckpts/ckpt-kernel-frozen-seed{seed}-100pct.pt",
            "--e1-data", f"{work}/data", "--e4-data", f"{work}/e4data",
            "--tables", mode["tables"], "--arm", arm, "--seed", str(seed),
            "--out", f"{work}/e4ckpts", *mode["ft_args"]]


def e4_eval_argv(py: str, root: str, work: str, arm: str, seed: int) -> list:
    # run_e4.sh [5/6]
    return [py, f"{root}/poc/e4/runner/eval_e4.py",
            "--ckpt", f"{work}/e4ckpts/ckpt-e4-{arm}-seed{seed}-final.pt",
            "--e4-data", f"{work}/e4data",
            "--out", f"{work}/e4evals/eval-e4-{arm}-seed{seed}.json"]


def e4_stats_argv(py: str, root: str, work: str, mode: dict) -> list:
    # run_e4.sh [6/6]
    return [py, f"{root}/poc/e4/runner/stats_e4.py", "--evals", f"{work}/e4evals",
            "--meta", f"{work}/e4data/meta.json", "--seeds", mode["seeds"],
            "--out-prefix", f"{work}/e4results/{mode['verdict_name']}",
            *mode["stats_extra"]]


def e4_check_smoke_argv(py: str, root: str, work: str, mode: dict) -> list:
    # run_e4.sh mock tail: independent runner smoke assertions
    return [py, f"{root}/poc/e4/runner/check_smoke.py",
            "--e1-ckpts", f"{work}/ckpts", "--e4-ckpts", f"{work}/e4ckpts",
            "--e4-data", f"{work}/e4data", "--evals", f"{work}/e4evals",
            "--tables", mode["tables"],
            "--verdict", f"{work}/e4results/{mode['verdict_name']}.json",
            "--results", f"{work}/e4results", "--seeds", mode["seeds"]]


def e1_check_smoke_argv(py: str, root: str, work: str, mode: dict) -> list:
    # poc/e1/smoke/run_smoke.sh tail: check_smoke.py <ckpts> <results> <seeds>
    return [py, f"{root}/poc/e1/smoke/check_smoke.py",
            f"{work}/ckpts", f"{work}/results", mode["seeds"]]


# ---------------------------------------------------------------------------
# Cost guards: per-stage single-call estimates from the poc/gpu/README.md E1
# cost table (g5.xlarge = 1x A10G — the same GPU Modal serves), timeout =
# est x 1.5 (the pre-registered +50% margin) + 5 min container overhead.
# T4 flavours get x2.5: T4 is ~2-3x slower AND train_e1.py's bf16 autocast is
# not hardware-accelerated on sm_75 (see README deviation note).
# ---------------------------------------------------------------------------

EST_MIN = {
    # cost table: "corpus fetch + data build (5 seeds) ~4 h" (CPU-bound, GPU-free)
    "fetch_corpus": 20,        # ~1.9 GB download
    "build_data": 220,         # the remainder of the ~4 h row
    # cost table: "LR sweep: 5 arms x 3 LRs, half budget ~3.5 h" serial => ~14 min/run
    "lr_sweep": 14,
    "select_lrs": 2,
    # cost table: "grid: 5 arms x 5 seeds, 200M tokens ~12 h" => ~28 min/run
    "train_arm_seed": 28,
    # cost table: "evals (35) + stats ~1.5 h" => ~2.5 min/eval + 5 min stats
    "eval_ckpt": 3,
    "stats_verdict": 5,
    # cost table: "E4 chain: shards + 15 fine-tunes (10M tok) + 15 evals + stats ~1-2 h"
    "e4_build_emission": 15,
    "e4_finetune": 5,
    "e4_eval": 4,
    "e4_stats": 5,
    "salvage": 5,
}
T4_MULT = 2.5
GPU_STAGES = ("lr_sweep", "train_arm_seed", "eval_ckpt", "e4_finetune", "e4_eval")

# $ rates for the ESTIMATE ONLY (poc/modal/README.md cost section; verify at
# modal.com/pricing — Modal reprices, these are 2026-07 figures).
RATES = {"A10G": 1.10, "T4": 0.59, "cpu_core_h": 0.135, "mem_gib_h": 0.024}
CPU_RESOURCES = {  # (cores, GiB) requested per CPU-stage container
    "fetch_corpus": (2, 4), "build_data": (4, 32), "select_lrs": (2, 4),
    "stats_verdict": (4, 8), "e4_build_emission": (4, 8), "e4_stats": (4, 8),
    "salvage": (2, 4),
}


def timeout_s(stage: str, gpu: str = "A10G") -> int:
    mult = T4_MULT if (gpu == "T4" and stage in GPU_STAGES) else 1.0
    return int((EST_MIN[stage] * 1.5 * mult + 5) * 60)


def build_plan(root: str, gpu: str, mock: bool, skip_e4: bool) -> list:
    """Ordered stage list: (stage, kind, n_calls, est_min_per_call, calls)."""
    work = "<volume:kot-e1-work>"
    m1 = e1_mode(root, work, mock)
    plan = [("fetch_corpus", "cpu", 1, EST_MIN["fetch_corpus"], [()]),
            ("build_data", "cpu", 1, EST_MIN["build_data"], [()])]
    gm = T4_MULT if gpu == "T4" else 1.0
    if len(m1["lrs"]) > 1:
        sweep = [(a, lr) for a in m1["arms"] for lr in m1["lrs"]]
        plan.append(("lr_sweep", "gpu", len(sweep), EST_MIN["lr_sweep"] * gm, sweep))
    plan.append(("select_lrs", "cpu", 1, EST_MIN["select_lrs"], [()]))
    grid = [(a, s, "<selected-lr>") for a in m1["arms"] for s in m1["seed_list"]]
    plan.append(("train_arm_seed", "gpu", len(grid),
                 EST_MIN["train_arm_seed"] * gm, grid))
    ev = eval_jobs(m1["seed_list"])
    plan.append(("eval_ckpt", "gpu", len(ev), EST_MIN["eval_ckpt"] * gm, ev))
    plan.append(("stats_verdict", "cpu", 1, EST_MIN["stats_verdict"], [()]))
    if not skip_e4:
        m4 = e4_mode(root, work, mock)
        plan.append(("e4_build_emission", "cpu", 1, EST_MIN["e4_build_emission"], [()]))
        ft = [(a, s) for a in m4["arms"] for s in m4["seed_list"]]
        plan.append(("e4_finetune", "gpu", len(ft), EST_MIN["e4_finetune"] * gm, ft))
        plan.append(("e4_eval", "gpu", len(ft), EST_MIN["e4_eval"] * gm, ft))
        plan.append(("e4_stats", "cpu", 1, EST_MIN["e4_stats"], [()]))
    if mock:  # tiny-config CPU-device runs; estimates above are FULL-mode
        plan = [(n, k, c, 2.0, calls) for (n, k, c, _e, calls) in plan]
    return plan


def plan_totals(plan: list, gpu: str, mock: bool) -> dict:
    gpu_min = sum(n * est for (stage, kind, n, est, _c) in plan if kind == "gpu")
    cpu_min = sum(n * est for (stage, kind, n, est, _c) in plan if kind == "cpu")
    wall_min = sum(est for (_s, _k, _n, est, _c) in plan)  # starmaps ~ max(1 call)
    gpu_rate = RATES[gpu]
    cpu_cost = 0.0
    for stage, kind, n, est, _c in plan:
        if kind == "cpu":
            cores, gib = CPU_RESOURCES[stage]
            cpu_cost += n * est / 60 * (cores * RATES["cpu_core_h"]
                                        + gib * RATES["mem_gib_h"])
    # GPU containers also bill their (default) CPU/mem; fold in ~15% overhead.
    gpu_cost = gpu_min / 60 * gpu_rate * 1.15
    # Worst case = every call runs to its sized timeout (the failsafe cap).
    cap_min = sum(n * timeout_s(stage, gpu if kind == "gpu" else "A10G") / 60
                  for (stage, kind, n, _e, _c) in plan if kind == "gpu")
    return {
        "gpu_h": gpu_min / 60, "cpu_h": cpu_min / 60, "wall_h": wall_min / 60,
        "gpu_cost": gpu_cost, "cpu_cost": cpu_cost,
        "total_cost": gpu_cost + cpu_cost,
        "worst_case_gpu_cost": cap_min / 60 * gpu_rate,
    }


# ---------------------------------------------------------------------------
# Results-bundle helpers (coordinator side)
# ---------------------------------------------------------------------------


def runner_exit_text(rc: int, e4_rc) -> str:
    """user-data-e1-pull.sh.tpl parity: 'rc=$RC e4_rc=$E4_RC' (e4_rc may be
    'skipped')."""
    return f"rc={rc} e4_rc={e4_rc}\n"


def ceil_min(seconds: float) -> int:
    return int(math.ceil(seconds / 60))
