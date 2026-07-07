#!/usr/bin/env python3
"""Token-free unit tests for the Modal port (bead kernel-of-truth-0oj).

    python3 -m unittest discover -s poc/modal -p 'test_*.py' -v

Runs on the SYSTEM python (numpy only — the same footprint as the e2 mock
smoke); Modal itself is STUBBED, so no account, token, or network is needed.
What is covered:

  - modal_common: manifest determinism, unpack fail-closed (traversal /
    absolute paths), byte round-trip, sidecar packaging, env redaction,
    verdict verification fail-closed;
  - modal_e2 imported against the stub: app/image/volume wiring, GPU flavours,
    AWS-failsafe-parity timeout, staged files actually exist;
  - the WHOLE wrapper end-to-end with the REAL e2_runner.py in --mock mode
    (reduced permutations): local_entrypoint -> container body -> staging
    assertion -> subprocess runner -> package -> unpack -> provenance merge ->
    OUTCOME echo — everything except Modal's transport itself;
  - cross-"transport" determinism: two independent runs produce identical
    results JSON up to the runner's own `date` field (the byte-identity
    contract vs the AWS path);
  - modal_e1e4 scaffold: imports, declares the grid resources, and every
    stage fails loudly as SCAFFOLD.
"""

from __future__ import annotations

import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
E2_DIR = REPO / "poc" / "e2"
sys.path.insert(0, str(HERE))

import modal_common as mc  # noqa: E402


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

    def add_local_dir(self, local_path, remote_path=None, **_kw):
        assert os.path.isdir(str(local_path)), f"staged dir missing: {local_path}"
        self.calls.append(("add_local_dir", str(local_path), remote_path))
        return self


class _StubFunction:
    def __init__(self, fn, kwargs):
        self.raw = fn
        self.kwargs = kwargs

    def remote(self, *a, **k):
        return self.raw(*a, **k)

    def starmap(self, jobs):
        return [self.raw(*j) for j in jobs]

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
# modal_common
# ---------------------------------------------------------------------------


class TestCommon(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="kot-modal-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _tree(self):
        d = Path(self.tmp)
        (d / "runner").mkdir(exist_ok=True)
        (d / "inputs").mkdir(exist_ok=True)
        (d / "runner" / "r.py").write_text("print('x')\n")
        (d / "runner" / "req.txt").write_text("numpy\n")
        (d / "inputs" / "b.json").write_text("{}")
        (d / "inputs" / "a.json").write_text("[1]")
        return d

    def test_manifest_deterministic_and_complete(self):
        d = self._tree()
        m1 = mc.input_manifest(str(d / "runner/r.py"), str(d / "runner/req.txt"), str(d / "inputs"))
        m2 = mc.input_manifest(str(d / "runner/r.py"), str(d / "runner/req.txt"), str(d / "inputs"))
        self.assertEqual(m1, m2)
        self.assertEqual(
            sorted(m1),
            ["inputs/a.json", "inputs/b.json", "runner/e2_runner.py", "runner/requirements.txt"],
        )
        for v in m1.values():
            self.assertRegex(v, r"^[0-9a-f]{64}$")
        (d / "inputs" / "a.json").write_text("[2]")
        self.assertNotEqual(m1, mc.input_manifest(
            str(d / "runner/r.py"), str(d / "runner/req.txt"), str(d / "inputs")))

    def test_unpack_byte_roundtrip(self):
        d = self._tree()
        files = mc.collect_dir(str(d))
        dest = os.path.join(self.tmp, "out")
        mc.unpack_files(files, dest)
        self.assertEqual(mc.collect_dir(dest), files)

    def test_unpack_rejects_traversal_and_absolute(self):
        for bad in ("../evil", "a/../../evil", "/etc/evil"):
            with self.assertRaises(SystemExit) as cm:
                mc.unpack_files({bad: b"x"}, os.path.join(self.tmp, "out"))
            self.assertIn("ERR_UNPACK_PATH", str(cm.exception))

    def test_package_results_sidecars_and_no_mutation(self):
        d = self._tree()
        prov = {"transport": "modal"}
        files = mc.package_results(str(d), run_log="log line\n", rc=3, provenance=prov)
        self.assertEqual(files[mc.RUNNER_EXIT_NAME], b"rc=3\n")
        self.assertEqual(json.loads(files[mc.PROVENANCE_NAME]), prov)
        self.assertIn(b"log line", files[mc.RUN_LOG_NAME])
        # runner-emitted bytes are shipped untouched
        self.assertEqual(files["inputs/a.json"], (d / "inputs" / "a.json").read_bytes())

    def test_package_results_reserved_collision_fails_closed(self):
        d = self._tree()
        (d / mc.RUNNER_EXIT_NAME).write_text("rc=0\n")
        with self.assertRaises(SystemExit) as cm:
            mc.package_results(str(d), run_log="", rc=0, provenance={})
        self.assertIn("ERR_SIDECAR_COLLISION", str(cm.exception))

    def test_redact_env(self):
        env = {
            "MODAL_TASK_ID": "ta-123",
            "MODAL_TOKEN_ID": "ak-nope",
            "MODAL_TOKEN_SECRET": "as-nope",
            "MODAL_AUTH_THING": "nope",
            "NVIDIA_VISIBLE_DEVICES": "all",
            "CUDA_VERSION": "12.4",
            "AWS_SECRET_ACCESS_KEY": "nope",
            "HOME": "/root",
        }
        red = mc.redact_env(env)
        self.assertEqual(
            red,
            {"MODAL_TASK_ID": "ta-123", "NVIDIA_VISIBLE_DEVICES": "all", "CUDA_VERSION": "12.4"},
        )
        self.assertNotIn("nope", json.dumps(red))

    def test_verdict_outcome_fail_closed(self):
        with self.assertRaises(SystemExit) as cm:
            mc.verdict_outcome(self.tmp)
        self.assertIn("ERR_NO_RESULTS", str(cm.exception))
        Path(self.tmp, "results-e2-mock.json").write_text(json.dumps({"no_outcome": 1}))
        with self.assertRaises(SystemExit) as cm:
            mc.verdict_outcome(self.tmp)
        self.assertIn("ERR_NO_OUTCOME", str(cm.exception))
        Path(self.tmp, "results-e2-mock.json").write_text(json.dumps({"outcome": "NULL (x)"}))
        self.assertEqual(mc.verdict_outcome(self.tmp), "NULL (x)")

    def test_provenance_required_keys(self):
        prov = mc.build_provenance(
            transport="modal", gpu_requested="T4", gpu_seen={"available": False},
            staged_manifest={"runner/e2_runner.py": "0" * 64}, runner_exit=0,
            started_utc="s", finished_utc="f",
        )
        for key in ("transport", "gpu_requested", "gpu_seen", "staged_sha256",
                    "runner_exit", "started_utc", "finished_utc", "python", "packages"):
            self.assertIn(key, prov)


# ---------------------------------------------------------------------------
# modal_e2 wiring (Modal stubbed)
# ---------------------------------------------------------------------------


class TestModalE2Wiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = _import_with_stub("modal_e2")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("modal_e2", None)
        sys.modules.pop("modal", None)

    def test_app_and_gpu_flavours(self):
        self.assertEqual(self.m.app.name, "kot-e2")
        self.assertEqual(set(self.m.GPU_FUNCTIONS), {"T4", "A10G"})
        for flavour, fname in (("T4", "run_e2_t4"), ("A10G", "run_e2_a10g")):
            kw = self.m.app.functions[fname].kwargs
            self.assertEqual(kw["gpu"], flavour)
            self.assertEqual(kw["timeout"], 4 * 3600)  # AWS 4 h failsafe parity
            self.assertIn("/root/.cache/huggingface", kw["volumes"])

    def test_image_staging(self):
        calls = self.m.image.calls
        kinds = [c[0] for c in calls]
        self.assertEqual(kinds[0], "debian_slim")
        self.assertLess(kinds.index("pip_install"), kinds.index("add_local_file"))
        pins = [c for c in calls if c[0] == "pip_install"][0][1]
        expected = [ln.strip() for ln in (HERE / "requirements-image.txt").read_text().splitlines()
                    if ln.strip() and not ln.strip().startswith("#")]
        self.assertEqual(list(pins), expected)
        staged_files = {c[2] for c in calls if c[0] == "add_local_file"}
        self.assertIn("/root/kot/poc/e2/runner/e2_runner.py", staged_files)
        self.assertIn("/root/kot/poc/e2/runner/requirements.txt", staged_files)
        staged_dirs = {c[2] for c in calls if c[0] == "add_local_dir"}
        self.assertIn("/root/kot/poc/e2/inputs", staged_dirs)
        self.assertIn(("add_local_python_source", ("modal_common",)), calls)

    def test_volume_name(self):
        self.assertEqual(self.m.hf_cache.name, "kot-hf-cache")
        self.assertTrue(self.m.hf_cache.create_if_missing)

    def test_bad_gpu_fails_closed(self):
        with self.assertRaises(SystemExit) as cm:
            self.m.main(gpu="H100")
        self.assertIn("ERR_GPU", str(cm.exception))


# ---------------------------------------------------------------------------
# End-to-end with the REAL runner (mock mode, reduced perms), Modal stubbed
# ---------------------------------------------------------------------------


class TestEndToEndMock(unittest.TestCase):
    """Everything except Modal's transport: entrypoint -> container body ->
    staging assertion -> real e2_runner.py subprocess -> package -> unpack."""

    @classmethod
    def setUpClass(cls):
        cls.m = _import_with_stub("modal_e2")
        cls.tmp = tempfile.mkdtemp(prefix="kot-modal-e2e-")
        # Repoint the "container" at the real local poc/e2 + a temp out dir.
        cls.m.REMOTE_E2 = str(E2_DIR)
        cls.m.REMOTE_OUT = os.path.join(cls.tmp, "container-out")
        cls.m.INCOMING_ROOT = Path(cls.tmp) / "results-incoming"
        # Reduced permutations for test speed; the entrypoint itself exposes
        # no such knob (pre-registered defaults only), so patch run_runner.
        # (staticmethod: keep the stashed plain function unbound on the class)
        cls._orig_run_runner = staticmethod(mc.run_runner)
        orig = mc.run_runner
        mc.run_runner = lambda *a, **kw: orig(
            *a, **{**kw, "n_perm": 60, "k_sets": 5, "echo": False})

    @classmethod
    def tearDownClass(cls):
        mc.run_runner = cls._orig_run_runner
        shutil.rmtree(cls.tmp, ignore_errors=True)
        sys.modules.pop("modal_e2", None)
        sys.modules.pop("modal", None)

    def test_staging_mismatch_fails_closed(self):
        with self.assertRaises(SystemExit) as cm:
            self.m.run_e2_t4.remote(mock=True, local_manifest={"bogus": "0" * 64})
        self.assertIn("ERR_STAGING_MISMATCH", str(cm.exception))

    def test_full_wrapper_roundtrip(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.m.main(gpu="T4", mock=True)
        out = buf.getvalue()
        self.assertIn("OUTCOME:", out)

        runs = sorted(self.m.INCOMING_ROOT.iterdir())
        self.assertEqual(len(runs), 1)
        dest = runs[0]
        self.assertTrue(dest.name.endswith("-modal"))
        names = {p.name for p in dest.iterdir()}
        self.assertLessEqual(
            {"results-e2-mock.json", "verdict-e2-mock.md",
             mc.RUN_LOG_NAME, mc.RUNNER_EXIT_NAME, mc.PROVENANCE_NAME},
            names,
        )
        self.assertEqual((dest / mc.RUNNER_EXIT_NAME).read_text(), "rc=0\n")

        # byte-identity: unpacked runner outputs == what the runner wrote
        for f in ("results-e2-mock.json", "verdict-e2-mock.md"):
            self.assertEqual(
                (dest / f).read_bytes(),
                Path(self.m.REMOTE_OUT, f).read_bytes(),
            )

        prov = json.loads((dest / mc.PROVENANCE_NAME).read_text())
        self.assertEqual(prov["transport"], "modal")
        self.assertEqual(prov["gpu_requested"], "T4")
        self.assertEqual(prov["runner_exit"], 0)
        self.assertEqual(
            prov["staged_sha256"]["runner/e2_runner.py"],
            mc.sha256_file(str(E2_DIR / "runner" / "e2_runner.py")),
        )
        self.assertIn("coordinator", prov)  # local-side merge happened
        self.assertEqual(prov["coordinator"]["modal_client"], "0.0-stub")
        self.assertNotIn("TOKEN", json.dumps(prov).upper())

        j = json.loads((dest / "results-e2-mock.json").read_text())
        self.assertTrue(j["mock"])
        self.assertEqual(len(j["per_model"]), 3)

    def test_cross_transport_determinism(self):
        """Same runner + same inputs => identical results JSON up to the
        runner's own `date` stamp — the byte-identity contract vs AWS."""
        outs = []
        for i in range(2):
            out = os.path.join(self.tmp, f"det-{i}")
            rc, _ = self._orig_run_runner(
                sys.executable, str(E2_DIR / "runner" / "e2_runner.py"),
                str(E2_DIR / "inputs"), out, mock=True,
                n_perm=60, k_sets=5, echo=False)
            self.assertEqual(rc, 0)
            j = json.loads(Path(out, "results-e2-mock.json").read_text())
            j.pop("date")
            outs.append(j)
        self.assertEqual(outs[0], outs[1])


# ---------------------------------------------------------------------------
# modal_e1e4 scaffold (Modal stubbed)
# ---------------------------------------------------------------------------


class TestScaffold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = _import_with_stub("modal_e1e4")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("modal_e1e4", None)
        sys.modules.pop("modal", None)

    def test_shape(self):
        self.assertEqual(self.m.app.name, "kot-e1e4")
        expected = {"fetch_corpus", "build_data", "lr_sweep", "select_lrs",
                    "train_arm_seed", "eval_ckpt", "stats_verdict",
                    "e4_build_emission", "e4_finetune", "e4_eval", "e4_stats"}
        self.assertEqual(set(self.m.app.functions), expected)
        for gpu_fn in ("lr_sweep", "train_arm_seed", "eval_ckpt", "e4_finetune", "e4_eval"):
            self.assertEqual(self.m.app.functions[gpu_fn].kwargs["gpu"], "A10G")
        for fn in expected:
            self.assertIn("/vol/e1work", self.m.app.functions[fn].kwargs["volumes"])
        self.assertEqual(len(self.m.ARMS), 5)
        self.assertEqual(len(self.m.SEEDS), 5)
        self.assertEqual(len(self.m.LRS), 3)

    def test_every_stage_is_loudly_scaffold(self):
        jobs = [("kernel-frozen", 0, "3e-4")]
        with self.assertRaises(NotImplementedError) as cm:
            self.m.train_arm_seed.starmap(jobs)
        self.assertIn("SCAFFOLD", str(cm.exception))
        self.assertIn("kernel-of-truth-af7", str(cm.exception))
        with self.assertRaises(SystemExit):
            with redirect_stdout(io.StringIO()):
                self.m.main()


if __name__ == "__main__":
    unittest.main()
