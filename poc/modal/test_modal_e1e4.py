#!/usr/bin/env python3
"""Token-free unit tests for the E1+E4 Modal port (bead kernel-of-truth-af7).

    python3 -m unittest test_modal_e1e4 -v                  # torch-free subset
    <python-with-numpy-and-torch> -m unittest test_modal_e1e4 -v   # + mock E2E

Modal is STUBBED (no account/token/network). Coverage:

  - wiring: function registry, GPU flavours, Volume mounts, cost-table
    timeouts (+50% margin), staged-file completeness;
  - driver fidelity: the bash arrays / heredocs parsed out of the COMMITTED
    poc/e1/run_all.sh + poc/e4/runner/run_e4.sh (arm-pairing: the trainer argv
    is arm-invariant apart from --arm, seed enters only via --seed, so
    poc/e1's paired-seed batch-schedule guarantee carries over unchanged);
  - fail-closed gates: staged-manifest mismatch, GLOSS-HASH pin,
    holdout-manifest tables pin, missing-E1-checkpoint guard;
  - results plumbing: RUNNER_EXIT format, dry-plan output (no calls made);
  - [torch] the tiny-config CPU mock of BOTH stages end-to-end through the
    wrapper code path: frozen-row bit-identity through E1 training AND E4
    emission fine-tuning (poc/e1 + poc/e4's own check_smoke assertions, plus
    a negative test proving they FIRE on a corrupted checkpoint), paired-seed
    base-init identity across arms, e1's own batch()/DetStream schedule
    determinism, results-incoming byte identity, LR sweep + run_all.sh's own
    selection snippet against wrapper-produced sweep summaries.
"""

from __future__ import annotations

import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import modal_common as mc  # noqa: E402
import modal_e1e4_lib as lib  # noqa: E402

try:
    import torch  # noqa: F401
    HAS_TORCH = True
except Exception:  # pragma: no cover - environment-dependent
    HAS_TORCH = False

TORCH_NOTE = ("needs a python with numpy+torch (disposable venv: "
              "bash poc/modal/validate.sh --mock-e2e)")


# ---------------------------------------------------------------------------
# Modal stub (records wiring; .remote()/.starmap() execute locally)
# ---------------------------------------------------------------------------


class _StubImage:
    def __init__(self):
        self.calls = []

    @classmethod
    def debian_slim(cls, python_version=None):
        inst = cls()
        inst.calls.append(("debian_slim", python_version))
        return inst

    def pip_install(self, *pkgs, **_kw):
        self.calls.append(("pip_install", pkgs))
        return self

    def add_local_python_source(self, *mods, **_kw):
        self.calls.append(("add_local_python_source", mods))
        return self

    def add_local_file(self, local_path, remote_path, **_kw):
        assert os.path.isfile(str(local_path)), f"staged file missing: {local_path}"
        self.calls.append(("add_local_file", str(local_path), remote_path))
        return self


class _StubFunction:
    def __init__(self, fn, kwargs):
        self.raw = fn
        self.kwargs = kwargs
        self.calls = 0

    def remote(self, *a, **k):
        self.calls += 1
        return self.raw(*a, **k)

    def starmap(self, jobs):
        out = []
        for j in jobs:
            self.calls += 1
            out.append(self.raw(*j))
        return out

    def __call__(self, *a, **k):
        return self.raw(*a, **k)


class _StubApp:
    def __init__(self, name=None):
        self.name = name
        self.functions = {}
        self.entrypoints = {}

    def function(self, **kwargs):
        def deco(fn):
            sf = _StubFunction(fn, kwargs)
            self.functions[fn.__name__] = sf
            return sf
        return deco

    def local_entrypoint(self, **_kw):
        def deco(fn):
            self.entrypoints[fn.__name__] = fn
            return fn
        return deco


class _StubVolume:
    @classmethod
    def from_name(cls, name, create_if_missing=False):
        v = cls()
        v.name = name
        v.create_if_missing = create_if_missing
        return v

    def commit(self):
        pass

    def reload(self):
        pass


def _stub_modal():
    stub = types.ModuleType("modal")
    stub.App = _StubApp
    stub.Image = _StubImage
    stub.Volume = _StubVolume
    stub.__version__ = "0.0-stub"
    return stub


def _import_with_stub(module_name):
    for m in (module_name, "modal"):
        sys.modules.pop(m, None)
    sys.modules["modal"] = _stub_modal()
    return importlib.import_module(module_name)


# ---------------------------------------------------------------------------
# Wiring (Modal stubbed)
# ---------------------------------------------------------------------------

CPU_FNS = {"fetch_corpus", "build_data", "select_lrs", "stats_verdict",
           "e4_build_emission", "e4_stats", "salvage"}
GPU_FNS = {"lr_sweep", "train_arm_seed", "eval_ckpt", "e4_finetune", "e4_eval"}


class TestWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = _import_with_stub("modal_e1e4")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("modal_e1e4", None)
        sys.modules.pop("modal", None)

    def test_registry(self):
        self.assertEqual(self.m.app.name, "kot-e1e4")
        expected = CPU_FNS | GPU_FNS | {f"{g}_t4" for g in GPU_FNS}
        self.assertEqual(set(self.m.app.functions), expected)
        for name in GPU_FNS:
            self.assertEqual(self.m.app.functions[name].kwargs["gpu"], "A10G")
            self.assertEqual(self.m.app.functions[f"{name}_t4"].kwargs["gpu"], "T4")
        for name in CPU_FNS:
            self.assertNotIn("gpu", self.m.app.functions[name].kwargs)
        for name in expected:
            self.assertIn("/vol/e1work", self.m.app.functions[name].kwargs["volumes"])

    def test_cost_table_timeouts(self):
        # timeout = cost-table estimate x1.5 (+5 min overhead); T4 x2.5.
        for name in GPU_FNS:
            a10g = self.m.app.functions[name].kwargs["timeout"]
            t4 = self.m.app.functions[f"{name}_t4"].kwargs["timeout"]
            self.assertEqual(a10g, int((lib.EST_MIN[name] * 1.5 + 5) * 60))
            self.assertEqual(t4, int((lib.EST_MIN[name] * 1.5 * lib.T4_MULT + 5) * 60))
        self.assertEqual(self.m.app.functions["build_data"].kwargs["timeout"],
                         int((lib.EST_MIN["build_data"] * 1.5 + 5) * 60))

    def test_image_staging_complete(self):
        calls = self.m.image.calls
        kinds = [c[0] for c in calls]
        self.assertEqual(kinds[0], "debian_slim")
        self.assertLess(kinds.index("pip_install"), kinds.index("add_local_file"))
        pins = [c for c in calls if c[0] == "pip_install"][0][1]
        expected = [ln.strip() for ln in (HERE / "requirements-image.txt")
                    .read_text().splitlines()
                    if ln.strip() and not ln.strip().startswith("#")]
        self.assertEqual(list(pins), expected)
        self.assertIn(("add_local_python_source", ("modal_common", "modal_e1e4_lib")),
                      calls)
        staged = {c[2] for c in calls if c[0] == "add_local_file"}
        self.assertEqual(staged, {f"/root/kot/{rel}" for rel in lib.STAGE_FILES})
        for rel in lib.STAGE_FILES:  # every staged file exists in the repo
            self.assertTrue((REPO / rel).is_file(), rel)

    def test_volume_name(self):
        self.assertEqual(self.m.work_vol.name, "kot-e1-work")
        self.assertTrue(self.m.work_vol.create_if_missing)

    def test_bad_gpu_fails_closed(self):
        with self.assertRaises(SystemExit) as cm:
            self.m.main(gpu="H100", dry_plan=True)
        self.assertIn("ERR_GPU", str(cm.exception))

    def test_function_sets_cover_both_gpus(self):
        for gpu, fset in self.m.FUNCTION_SETS.items():
            self.assertEqual(set(fset), CPU_FNS - {"salvage"} | GPU_FNS)
            for name in GPU_FNS:
                want = "A10G" if gpu == "A10G" else "T4"
                self.assertEqual(fset[name].kwargs["gpu"], want)


# ---------------------------------------------------------------------------
# Driver-fidelity: parsed bash arrays + heredocs ARE the committed drivers
# ---------------------------------------------------------------------------


class TestDriverFidelity(unittest.TestCase):
    def test_manifest_deterministic_and_complete(self):
        m1 = lib.tree_manifest(str(REPO))
        m2 = lib.tree_manifest(str(REPO))
        self.assertEqual(m1, m2)
        self.assertEqual(sorted(m1), sorted(lib.STAGE_FILES))
        for v in m1.values():
            self.assertRegex(v, r"^[0-9a-f]{64}$")

    def test_e1_full_mode_matches_run_all_sh(self):
        m = lib.e1_mode(str(REPO), "/W", mock=False)
        self.assertEqual(m["seeds"], "0,1,2,3,4")
        self.assertEqual(m["arms"], ("kernel-frozen", "shuffled-frozen",
                                     "random-frozen", "trainable", "kernel-init"))
        self.assertEqual(m["model_args"], [
            "--n-layer", "4", "--n-head", "8", "--d-model", "512", "--d-ff", "2048",
            "--seq-len", "256", "--batch-size", "64", "--total-tokens", "200000000"])
        self.assertEqual(m["data_args"],
                         ["--vocab-size", "8000", "--max-train-tokens", "210000000"])
        self.assertEqual(m["lrs"], ["3e-4", "6e-4", "1e-3"])
        self.assertEqual(m["stats_extra"], [])
        self.assertEqual(m["verdict_name"], "verdict-e1")
        self.assertTrue(m["tables"].endswith("poc/e1/inputs/vector-tables-d512.json"))

    def test_e1_mock_mode_matches_run_all_sh(self):
        m = lib.e1_mode(str(REPO), "/W", mock=True)
        self.assertEqual(m["seeds"], "0,1")
        self.assertEqual(m["model_args"], [
            "--n-layer", "2", "--n-head", "2", "--d-model", "64", "--d-ff", "128",
            "--seq-len", "128", "--batch-size", "16", "--total-tokens", "409600",
            "--allow-any-size", "--device", "cpu"])
        self.assertEqual(m["lrs"], ["1e-3"])
        self.assertEqual(m["stats_extra"], ["--mock"])
        self.assertEqual(m["verdict_name"], "verdict-e1-mock")
        self.assertEqual(m["tables"], "/W/vector-tables-mock-d64.json")

    def test_e4_modes_match_run_e4_sh(self):
        f = lib.e4_mode(str(REPO), "/W", mock=False)
        self.assertEqual(f["arms"], ("kernel", "shuffled", "random"))
        self.assertEqual(f["build_args"], ["--seeds", "0,1,2,3,4"])
        self.assertEqual(f["ft_args"], ["--batch-size", "64", "--total-tokens",
                                        "10000000", "--lr", "1e-4"])
        self.assertEqual(f["verdict_name"], "verdict-e4")
        m = lib.e4_mode(str(REPO), "/W", mock=True)
        self.assertEqual(m["build_args"], ["--seeds", "0,1",
                                           "--exposure-per-concept", "2", "--smoke", "30"])
        self.assertEqual(m["ft_args"], ["--batch-size", "8", "--total-tokens",
                                        "200000", "--lr", "1e-3", "--device", "cpu"])
        self.assertEqual(m["tables"], "/W/e4tables/vector-tables-mock-manifest.json")

    def test_train_argv_is_arm_invariant_apart_from_arm(self):
        """Common-rule-1 fidelity at the transport layer: for a fixed seed the
        wrapper hands train_e1.py IDENTICAL argv across arms except the --arm
        value itself, and the seed enters only via --seed — so the paired-seed
        batch schedule (a function of seed/shard/batch/steps inside poc/e1's
        OWN trainer) cannot differ between arms."""
        mode = lib.e1_mode(str(REPO), "/W", mock=False)
        a = lib.train_argv("py", "/R", "/W", mode, "kernel-frozen", 3, "3e-4")
        b = lib.train_argv("py", "/R", "/W", mode, "trainable", 3, "3e-4")
        ia, ib = a.index("--arm"), b.index("--arm")
        self.assertEqual(ia, ib)
        self.assertEqual(a[:ia + 1] + a[ia + 2:], b[:ib + 1] + b[ib + 2:])
        c = lib.train_argv("py", "/R", "/W", mode, "kernel-frozen", 4, "3e-4")
        diff = [i for i, (x, y) in enumerate(zip(a, c)) if x != y]
        self.assertEqual(diff, [a.index("--seed") + 1])

    def test_train_argv_matches_run_all_sh_shape(self):
        mode = lib.e1_mode(str(REPO), "/W", mock=False)
        argv = lib.train_argv("py", "/R", "/W", mode, "kernel-frozen", 0, "3e-4",
                              sweep=True)
        # run_all.sh [2/5]: ... --out $CKPTS/sweep --budget-frac 0.5
        # --no-checkpoints "${MODEL_ARGS[@]}"
        i = argv.index("--out")
        self.assertEqual(argv[i + 1], "/W/ckpts/sweep")
        self.assertEqual(argv[i + 2:i + 5], ["--budget-frac", "0.5", "--no-checkpoints"])
        self.assertEqual(argv[i + 5:], mode["model_args"])
        grid = lib.train_argv("py", "/R", "/W", mode, "kernel-frozen", 0, "3e-4")
        self.assertEqual(grid[grid.index("--out") + 2:], mode["model_args"])

    def test_eval_jobs_match_run_all_sh(self):
        jobs = lib.eval_jobs([0, 1, 2, 3, 4])
        self.assertEqual(len(jobs), 35)
        per_seed = [j for j in jobs if j[1] == 2]
        self.assertEqual(per_seed, [
            ("kernel-frozen", 2, "step0"), ("kernel-frozen", 2, "50pct"),
            ("kernel-frozen", 2, "100pct"), ("shuffled-frozen", 2, "100pct"),
            ("random-frozen", 2, "100pct"), ("trainable", 2, "100pct"),
            ("kernel-init", 2, "100pct")])
        self.assertEqual(len(lib.eval_jobs([0, 1])), 14)

    def test_summary_name_matches_trainer_formula(self):
        self.assertEqual(lib.summary_name("kernel-frozen", 0, "3e-4", True),
                         "summary-kernel-frozen-seed0-frac0.5-lr0.0003.json")
        self.assertEqual(lib.summary_name("trainable", 4, "1e-3", False),
                         "summary-trainable-seed4-lr0.001.json")

    def test_heredocs_extracted_and_recognisable(self):
        self.assertIn("Common rule 5", lib.lr_selection_code(str(REPO)))
        self.assertIn("mock mode", lib.fixed_lr_code(str(REPO)))
        self.assertIn("ERR_TABLES_PIN", lib.pin_check_code(str(REPO)))
        self.assertIn("mock corpus", lib.mock_corpus_code(str(REPO)))

    def test_lr_selection_snippet_is_run_all_shs_own(self):
        """Execute run_all.sh's OWN selection heredoc on synthetic sweep
        summaries: best of sweep by val loss, per arm."""
        tmp = tempfile.mkdtemp(prefix="kot-lrsel-")
        try:
            rows = [("kernel-frozen", 0.0003, 2.0), ("kernel-frozen", 0.001, 1.5),
                    ("trainable", 0.0003, 1.1), ("trainable", 0.001, 1.9)]
            for arm, lr, vl in rows:
                with open(os.path.join(tmp, f"summary-{arm}-seed0-frac0.5-lr{lr}.json"),
                          "w") as f:
                    json.dump({"arm": arm, "lr": lr, "final": {"valLoss": vl}}, f)
            out = os.path.join(tmp, "sel.json")
            r = subprocess.run([sys.executable, "-c", lib.lr_selection_code(str(REPO)),
                                tmp, out], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            with open(out) as f:
                sel = json.load(f)
            self.assertIn("Common rule 5", sel["rule"])
            self.assertEqual(sel["selected"]["kernel-frozen"]["lr"], 0.001)
            self.assertEqual(sel["selected"]["trainable"]["lr"], 0.0003)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_pin_check_snippet_pass_and_fail(self):
        holdout = str(REPO / "poc/e4/inputs/holdout-manifest.json")
        gloss = mc.sha256_file(str(REPO / "poc/e4/inputs/glosses.jsonl"))
        vsha = mc.sha256_file(str(REPO / "poc/e4/inputs/vector-tables-manifest.json"))
        code = lib.pin_check_code(str(REPO))
        ok = subprocess.run([sys.executable, "-c", code, holdout, gloss, vsha],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertIn("pins OK", ok.stdout)
        bad = subprocess.run([sys.executable, "-c", code, holdout, "0" * 64, vsha],
                             capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("ERR_GLOSS_PIN", bad.stdout + bad.stderr)

    def test_gloss_pin_matches_committed_bytes(self):
        self.assertEqual(lib.gloss_pin(str(REPO)),
                         mc.sha256_file(str(REPO / "poc/e4/inputs/glosses.jsonl")))

    def test_runner_exit_format(self):
        self.assertEqual(lib.runner_exit_text(0, 0), "rc=0 e4_rc=0\n")
        self.assertEqual(lib.runner_exit_text(0, "skipped"), "rc=0 e4_rc=skipped\n")


# ---------------------------------------------------------------------------
# Fail-closed gates through the wrapper bodies (Modal stubbed, no torch)
# ---------------------------------------------------------------------------


def _tamper_tree(tamper: dict) -> str:
    """A parallel repo root: symlinks to the real staged files, with `tamper`
    entries replaced by modified copies."""
    root = tempfile.mkdtemp(prefix="kot-tamper-")
    for rel in lib.STAGE_FILES:
        dst = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel in tamper:
            with open(REPO / rel, "rb") as f:
                data = f.read()
            with open(dst, "wb") as f:
                f.write(tamper[rel](data))
        else:
            os.symlink(REPO / rel, dst)
    return root


class TestFailClosedGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = _import_with_stub("modal_e1e4")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("modal_e1e4", None)
        sys.modules.pop("modal", None)

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="kot-e1e4-gate-")
        self._root, self._work = self.m.REMOTE_ROOT, self.m.WORK
        self.m.REMOTE_ROOT = str(REPO)
        self.m.WORK = os.path.join(self.tmp, "work")
        os.makedirs(self.m.WORK)

    def tearDown(self):
        self.m.REMOTE_ROOT, self.m.WORK = self._root, self._work
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_staging_mismatch_fails_closed(self):
        with self.assertRaises(SystemExit) as cm:
            self.m.fetch_corpus.remote({"bogus": "0" * 64}, True)
        self.assertIn("ERR_STAGING_MISMATCH", str(cm.exception))

    def test_gloss_pin_gate_fires(self):
        root = _tamper_tree({"poc/e4/inputs/glosses.jsonl": lambda b: b + b"tamper\n"})
        try:
            self.m.REMOTE_ROOT = root
            manifest = lib.tree_manifest(root)  # staging itself matches
            with self.assertRaises(SystemExit) as cm, \
                    redirect_stdout(io.StringIO()):
                self.m.e4_build_emission.remote(manifest, False)
            self.assertIn("ERR_GLOSS_PIN", str(cm.exception))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_tables_pin_gate_fires(self):
        root = _tamper_tree({"poc/e4/inputs/vector-tables-manifest.json":
                             lambda b: b + b"\n"})
        try:
            self.m.REMOTE_ROOT = root
            manifest = lib.tree_manifest(root)
            with self.assertRaises(SystemExit) as cm, \
                    redirect_stdout(io.StringIO()):
                self.m.e4_build_emission.remote(manifest, False)
            self.assertIn("ERR_TABLES_PIN", str(cm.exception))
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_missing_e1_checkpoints_fail_closed(self):
        manifest = lib.tree_manifest(str(REPO))
        with self.assertRaises(SystemExit) as cm, redirect_stdout(io.StringIO()):
            self.m.e4_build_emission.remote(manifest, False)
        self.assertIn("ERR_MISSING_E1_CKPT", str(cm.exception))

    def test_missing_grid_checkpoint_fails_eval(self):
        manifest = lib.tree_manifest(str(REPO))
        with self.assertRaises(SystemExit) as cm:
            self.m.eval_ckpt.remote("kernel-frozen", 0, "step0", manifest, False)
        self.assertIn("ERR_MISSING_CKPT", str(cm.exception))


# ---------------------------------------------------------------------------
# --dry-plan: full call graph + GPU-h + $ estimate, ZERO calls
# ---------------------------------------------------------------------------


class TestDryPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = _import_with_stub("modal_e1e4")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("modal_e1e4", None)
        sys.modules.pop("modal", None)

    def test_plan_counts_and_costs(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.m.main(gpu="A10G", dry_plan=True)
        out = buf.getvalue()
        self.assertIn("lr_sweep", out)
        self.assertIn("train_arm_seed", out)
        for stage, n in (("lr_sweep", 15), ("train_arm_seed", 25),
                         ("eval_ckpt", 35), ("e4_finetune", 15), ("e4_eval", 15)):
            row = next(ln for ln in out.splitlines() if ln.startswith(stage))
            self.assertIn(f"{n:>6}", row)
        self.assertIn("A10G-h", out)
        self.assertIn("estimate: ~$", out)
        self.assertIn("worst case", out)
        self.assertIn("NO authenticated Modal call", out)
        for fn in self.m.app.functions.values():  # nothing was invoked
            self.assertEqual(fn.calls, 0)

    def test_plan_totals_sane(self):
        plan = lib.build_plan(str(REPO), "A10G", False, False)
        tot = lib.plan_totals(plan, "A10G", False)
        self.assertAlmostEqual(tot["gpu_h"], 1150 / 60, places=2)  # 19.2 A10G-h
        self.assertTrue(20 <= tot["total_cost"] <= 40, tot)
        self.assertTrue(tot["worst_case_gpu_cost"] <= 50, tot)
        skip = lib.plan_totals(lib.build_plan(str(REPO), "A10G", False, True),
                               "A10G", False)
        self.assertLess(skip["gpu_h"], tot["gpu_h"])

    def test_direct_execution_dry_plan(self):
        # python3 modal_e1e4.py --dry-plan must never need a token; the real
        # client is absent here, so run __main__ under the stub via runpy.
        app_py = str(HERE / "modal_e1e4.py")
        code = (
            "import sys, runpy\n"
            f"sys.path.insert(0, {str(HERE)!r})\n"
            "import test_modal_e1e4 as t\n"
            "sys.modules['modal'] = t._stub_modal()\n"
            f"sys.argv = [{app_py!r}, '--dry-plan']\n"
            f"runpy.run_path({app_py!r}, run_name='__main__')\n")
        r = subprocess.run([sys.executable, "-c", code],
                           capture_output=True, text=True, cwd=str(HERE))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("estimate: ~$", r.stdout)


# ---------------------------------------------------------------------------
# Tiny-config CPU mock of BOTH stages end-to-end through the wrapper
# ---------------------------------------------------------------------------


@unittest.skipUnless(HAS_TORCH, TORCH_NOTE)
class TestMockE2E(unittest.TestCase):
    """main(mock=True): fetch(mock corpus) -> build_data -> fixed-LR selection
    (run_all.sh's own snippet) -> 5 arms x 2 seeds grid -> 14 evals -> stats +
    e1 check_smoke -> E4 pin gates -> emission build -> 3x2 fine-tunes ->
    evals -> stats + e4 check_smoke -> results-incoming bundle. Everything
    except Modal's transport itself."""

    @classmethod
    def setUpClass(cls):
        cls.m = _import_with_stub("modal_e1e4")
        cls.tmp = tempfile.mkdtemp(prefix="kot-e1e4-e2e-")
        cls.m.REMOTE_ROOT = str(REPO)
        cls.m.WORK = os.path.join(cls.tmp, "work")
        cls.m.INCOMING_ROOT = Path(cls.tmp) / "results-incoming"
        os.makedirs(cls.m.WORK)
        cls.m.main(gpu="A10G", mock=True)
        runs = sorted(cls.m.INCOMING_ROOT.iterdir())
        assert len(runs) == 1
        cls.dest = runs[0]
        cls.work = Path(cls.m.WORK)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)
        sys.modules.pop("modal_e1e4", None)
        sys.modules.pop("modal", None)

    def test_incoming_layout_aws_parity(self):
        names = {p.name for p in self.dest.iterdir()}
        self.assertLessEqual(
            {"verdict-e1-mock.json", "verdict-e1-mock.md", "lr-selection.json",
             "lr-selection-mock.json", "data-meta-mock.json", "kot-e1-run.log",
             "RUNNER_EXIT", "provenance-modal.json", "provenance", "summaries",
             "e4"}, names)
        self.assertEqual(len(list(self.dest.glob("mock-eval-*.json"))), 14)
        e4names = {p.name for p in (self.dest / "e4").iterdir()}
        self.assertLessEqual(
            {"verdict-e4-mock.json", "verdict-e4-mock.md", "e4-data-meta-mock.json",
             "runner-smoke-log.txt", "kot-e4-run.log", "provenance"}, e4names)
        self.assertEqual(len(list((self.dest / "e4").glob("mock-eval-e4-*.json"))), 6)
        self.assertEqual((self.dest / "RUNNER_EXIT").read_text(), "rc=0 e4_rc=0\n")

    def test_verdicts_mock_labelled(self):
        v1 = json.loads((self.dest / "verdict-e1-mock.json").read_text())
        self.assertTrue(v1["mock"])
        self.assertIn("MOCK", v1["verdict"])
        self.assertIn("kernel-frozen > shuffled-kernel-frozen",
                      v1["preRegisteredCriteria"]["primary"])
        v4 = json.loads((self.dest / "e4" / "verdict-e4-mock.json").read_text())
        self.assertTrue(v4["mock"])
        self.assertIn("MOCK", v4["verdict"])

    def test_frozen_row_bit_identity_through_wrapper(self):
        import torch as T
        for arm in ("kernel-frozen", "shuffled-frozen", "random-frozen"):
            ck0 = T.load(self.work / "ckpts" / f"ckpt-{arm}-seed0-step0.pt",
                         map_location="cpu", weights_only=False)
            lo, hi = ck0["conceptLo"], ck0["conceptHi"]
            for tag in ("50pct", "100pct"):
                ck = T.load(self.work / "ckpts" / f"ckpt-{arm}-seed0-{tag}.pt",
                            map_location="cpu", weights_only=False)
                self.assertTrue(T.equal(ck0["model"]["wte.weight"][lo:hi],
                                        ck["model"]["wte.weight"][lo:hi]),
                                f"{arm} {tag}: frozen rows moved")
        # poc/e1's own independent assertions ran in-wrapper and passed:
        self.assertIn("SMOKE PASS", (self.dest / "kot-e1-run.log").read_text())
        # ...and poc/e4's, through emission fine-tuning:
        self.assertIn("PASS", (self.dest / "e4" / "runner-smoke-log.txt").read_text())

    def test_paired_seed_base_init_across_arms(self):
        """Common rule 1 through the wrapper: outside the 54 concept rows,
        the step-0 model of every arm of a seed is bit-identical."""
        import torch as T
        ref = T.load(self.work / "ckpts" / "ckpt-kernel-frozen-seed0-step0.pt",
                     map_location="cpu", weights_only=False)
        lo, hi = ref["conceptLo"], ref["conceptHi"]
        for arm in ("shuffled-frozen", "random-frozen", "trainable", "kernel-init"):
            ck = T.load(self.work / "ckpts" / f"ckpt-{arm}-seed0-step0.pt",
                        map_location="cpu", weights_only=False)
            for key, w in ck["model"].items():
                r = ref["model"][key]
                if key == "wte.weight":
                    self.assertTrue(T.equal(w[:lo], r[:lo]), arm)
                    self.assertTrue(T.equal(w[hi:], r[hi:]), arm)
                else:
                    self.assertTrue(T.equal(w, r), f"{arm} {key}")

    def test_batch_schedule_is_e1s_own_and_seed_keyed(self):
        """Assert against poc/e1's OWN scheduling code (train_e1.batches +
        detstream.det_permutation), not a reimplementation: the schedule the
        wrapper-run trainer consumed is a pure function of the seed."""
        import torch as T
        sys.path.insert(0, str(REPO / "poc" / "e1" / "train"))
        sys.path.insert(0, str(REPO / "poc" / "e1" / "pipeline"))
        import detstream
        import train_e1
        shard = train_e1.Shard(str(self.work / "data" / "seed0" / "train.bin"), 128)
        seqs = []
        for _ in range(2):
            xs = [x for _step, x, _y in train_e1.batches(shard, 16, 5, seed=0)]
            seqs.append(T.cat([t.reshape(-1) for t in xs]))
        self.assertTrue(T.equal(seqs[0], seqs[1]))
        perm = detstream.det_permutation("e1/batches/0/epoch0", shard.n_windows)
        x0, y0 = shard.window(perm[0])
        first = next(iter(train_e1.batches(shard, 16, 1, seed=0)))
        self.assertTrue(T.equal(first[1][0], x0))
        seed1 = [x for _s, x, _y in train_e1.batches(shard, 16, 5, seed=1)]
        self.assertFalse(T.equal(seqs[0], T.cat([t.reshape(-1) for t in seed1])))

    def test_assertions_fire_on_corrupted_checkpoint(self):
        """Negative control: perturb one frozen concept row on a COPY of the
        wrapper-produced grid and prove poc/e1's own check_smoke FIRES."""
        import torch as T
        cp = Path(self.tmp) / "ckpts-corrupt"
        if cp.exists():
            shutil.rmtree(cp)
        shutil.copytree(self.work / "ckpts", cp)
        p = cp / "ckpt-kernel-frozen-seed0-50pct.pt"
        ck = T.load(p, map_location="cpu", weights_only=False)
        ck["model"]["wte.weight"][ck["conceptLo"]] += 1.0
        T.save(ck, p)
        r = subprocess.run([sys.executable,
                            str(REPO / "poc" / "e1" / "smoke" / "check_smoke.py"),
                            str(cp), str(self.work / "results"), "0,1"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FROZEN concept rows moved", r.stdout)

    def test_results_bytes_identical_to_volume(self):
        """Unpack fidelity: script outputs ship as opaque bytes."""
        for name in ("verdict-e1-mock.json", "verdict-e1-mock.md",
                     "data-meta-mock.json"):
            self.assertEqual((self.dest / name).read_bytes(),
                             (self.work / "results" / name).read_bytes())
        self.assertEqual(
            (self.dest / "e4" / "verdict-e4-mock.json").read_bytes(),
            (self.work / "e4results" / "verdict-e4-mock.json").read_bytes())

    def test_provenance_sidecars(self):
        prov = json.loads((self.dest / "provenance-modal.json").read_text())
        self.assertEqual(prov["transport"], "modal")
        self.assertEqual(prov["staged_sha256"], lib.tree_manifest(str(REPO)))
        self.assertTrue(prov["coordinator"]["local_manifest_matched"])
        per_run = list((self.dest / "provenance").glob("*.json"))
        self.assertGreaterEqual(len(per_run), 20)  # every stage stamped one
        one = json.loads(per_run[0].read_text())
        for key in ("stage", "runId", "argv", "staged_sha256", "runner_exit",
                    "gpu_requested", "started_utc", "finished_utc"):
            self.assertIn(key, one)
        blob = "".join(p.read_text() for p in per_run).upper()
        for needle in ("TOKEN_ID", "TOKEN_SECRET", "AWS_SECRET"):
            self.assertNotIn(needle, blob)

    def test_idempotent_stamps_skip_completed_work(self):
        before = (self.work / "ckpts" / "ckpt-kernel-frozen-seed0-100pct.pt").stat().st_mtime
        manifest = lib.tree_manifest(str(REPO))
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.m.build_data.remote(manifest, True)
            self.m.train_arm_seed.remote("kernel-frozen", 0, "0.001", manifest, True)
        self.assertIn("skipping", buf.getvalue())
        after = (self.work / "ckpts" / "ckpt-kernel-frozen-seed0-100pct.pt").stat().st_mtime
        self.assertEqual(before, after)

    def test_salvage_returns_trace_bytes(self):
        files = self.m.salvage.remote()
        self.assertTrue(any(k.startswith("logs/") for k in files))
        self.assertTrue(any(k.startswith("prov/") for k in files))
        self.assertTrue(all(isinstance(v, bytes) for v in files.values()))

    def test_z_sweep_path_with_run_all_shs_own_selector(self):
        """Exercise the full-mode sweep machinery (not used by the faithful
        mock, which mirrors run_all.sh's fixed-LR shortcut): two arms x two
        LRs of tiny half-budget sweeps through the wrapper, then run_all.sh's
        OWN Common-rule-5 snippet over the wrapper-produced summaries."""
        manifest = lib.tree_manifest(str(REPO))
        sweep_dir = self.work / "ckpts" / "sweep"
        results = {}
        for arm in ("kernel-frozen", "trainable"):
            for lr in ("1e-3", "3e-3"):
                results[(arm, lr)] = self.m.lr_sweep.remote(arm, lr, manifest, True)
        out = Path(self.tmp) / "lr-selection-sweeptest.json"
        r = subprocess.run([sys.executable, "-c", lib.lr_selection_code(str(REPO)),
                            str(sweep_dir), str(out)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(out) as f:
            sel = json.load(f)["selected"]
        for arm in ("kernel-frozen", "trainable"):
            best_lr = min(("1e-3", "3e-3"),
                          key=lambda lr: results[(arm, lr)]["final"]["valLoss"])
            self.assertEqual(sel[arm]["lr"], float(best_lr))
            self.assertEqual(sel[arm]["valLoss"],
                             results[(arm, best_lr)]["final"]["valLoss"])


if __name__ == "__main__":
    unittest.main()
