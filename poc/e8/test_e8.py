#!/usr/bin/env python3
"""Token-free unit suite for the E8 harness (bead kernel-of-truth-u0x).

    nice -n 10 python3 -m unittest discover -s poc/e8 -p 'test_e8.py' -v

Runs on the SYSTEM python (numpy only); Modal is STUBBED; no torch, no
account, no network. What is covered:

  - masked-profile correspondence: self-cell exclusion actually excludes
    (diagonal poison invariance), symmetry when both families coincide;
  - the pre-registered CONTROLS (design pin §Layout):
      * planted-correspondence POSITIVE — two synthetic families whose
        signatures are lifted from the same kernel vectors: the battery MUST
        return PASS (gate + P1 + P2);
      * structured NULL — the families correspond with each other through a
        latent geometry unrelated to the kernel: gate MUST pass, P1 MUST fail
        (correspondence exists; the kernel does not predict it);
      * pure-noise NULL — independent families: the gate MUST fail
        (PRECONDITION FAIL, kernel claim untested);
  - mock end-to-end: e8_runner.py --mock -> analyze.py on the stamp dir, all
    fail-closed pins live, verdict marked MOCK;
  - modal_e8.py wiring against a Modal stub: staged files exist, manifest
    matches build_inputs output, dry-plan prints a $ estimate.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import analyze as e8  # noqa: E402  (imports e2_runner + reanalysis machinery)

r = e8.r


def _cos(mat: np.ndarray) -> np.ndarray:
    return r.cosine_sim_matrix(np.asarray(mat, dtype=np.float64))


def _synthetic(kind: str, n: int = 40, d_lat: int = 24, d_sae: int = 300, seed: int = 7):
    """Returns (kernels, SA, SB, orig3_ods) for the three control regimes."""
    rng = np.random.default_rng(seed)
    V = rng.standard_normal((n, d_lat))          # "kernel" latents
    K = _cos(V)
    W = rng.standard_normal((n, d_lat))          # kernel-UNRELATED shared latents

    def family(latents, fam_seed):
        frng = np.random.default_rng(fam_seed)
        M = frng.standard_normal((d_sae, d_lat)) / np.sqrt(d_lat)
        sig = latents @ M.T + 0.3 * frng.standard_normal((n, d_sae))
        return _cos(np.maximum(sig, 0.0))        # ReLU: non-negative like real SAE acts

    if kind == "planted":
        SA, SB = family(V, 101), family(V, 202)
    elif kind == "structured-null":
        SA, SB = family(W, 101), family(W, 202)
    elif kind == "pure-noise":
        nrng = np.random.default_rng(303)
        SA = _cos(np.maximum(nrng.standard_normal((n, d_sae)), 0.0))
        SB = _cos(np.maximum(nrng.standard_normal((n, d_sae)), 0.0))
    else:
        raise ValueError(kind)

    # relatedness-baseline stand-ins: two independent RDMs + one mildly
    # kernel-mixed one (so P2's partial machinery has real work to do)
    b1 = _cos(rng.standard_normal((n, d_lat)))
    b2 = _cos(rng.standard_normal((n, d_lat)))
    b3 = _cos(0.4 * V + rng.standard_normal((n, d_lat)))
    orig3 = [r.offdiag(b) for b in (b1, b2, b3)]
    return {"jl512": K}, SA, SB, orig3


def _brute_masked_profile(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Reference implementation: literal masked Spearman per cell."""
    n = A.shape[0]
    idx = np.arange(n)
    out = np.empty((n, n))
    for c in range(n):
        for d in range(n):
            m = (idx != c) & (idx != d)
            out[c, d] = r.spearman(A[c, m], B[d, m])
    return out


class TestMaskedProfile(unittest.TestCase):
    def test_matches_brute_force_with_ties(self):
        rng = np.random.default_rng(5)
        # quantized values force heavy ties — the mid-rank adjustment must be exact
        A = np.round(_cos(rng.standard_normal((14, 4))), 1)
        B = np.round(_cos(rng.standard_normal((14, 4))), 1)
        np.testing.assert_allclose(
            e8.masked_profile_matrix(A, B), _brute_masked_profile(A, B), atol=1e-12)

    def test_matches_brute_force_continuous(self):
        rng = np.random.default_rng(6)
        A, B = _cos(rng.standard_normal((13, 8))), _cos(rng.standard_normal((13, 8)))
        np.testing.assert_allclose(
            e8.masked_profile_matrix(A, B), _brute_masked_profile(A, B), atol=1e-12)

    def test_self_cell_exclusion(self):
        rng = np.random.default_rng(0)
        A, B = _cos(rng.standard_normal((12, 6))), _cos(rng.standard_normal((12, 6)))
        X1 = e8.masked_profile_matrix(A, B)
        A2, B2 = A.copy(), B.copy()
        np.fill_diagonal(A2, 99.0)   # poison the excluded cells
        np.fill_diagonal(B2, -99.0)
        X2 = e8.masked_profile_matrix(A2, B2)
        np.testing.assert_allclose(X1, X2, atol=1e-12)

    def test_cross_cell_exclusion(self):
        # X[c,d] must not depend on A[c,d] or B[d,c] either (mask drops both indices)
        rng = np.random.default_rng(1)
        A, B = _cos(rng.standard_normal((10, 5))), _cos(rng.standard_normal((10, 5)))
        X1 = e8.masked_profile_matrix(A, B)
        A2, B2 = A.copy(), B.copy()
        A2[3, 7], B2[7, 3] = 42.0, -42.0
        X2 = e8.masked_profile_matrix(A2, B2)
        self.assertAlmostEqual(X1[3, 7], X2[3, 7], places=12)

    def test_symmetry_when_families_equal(self):
        rng = np.random.default_rng(2)
        A = _cos(rng.standard_normal((9, 4)))
        X = e8.masked_profile_matrix(A, A)
        np.testing.assert_allclose(X, X.T, atol=1e-12)
        self.assertTrue(all(X[c, c] > 0.999 for c in range(9)))  # identical profiles


class TestControls(unittest.TestCase):
    N_PERM = 500          # min p = 1/501 < 0.01 — resolvable for the primary
    N_PERM_RETR = 50

    def _run(self, kind):
        kernels, SA, SB, orig3 = _synthetic(kind)
        return e8.full_battery(kernels, SA, SB, orig3, emb4_ods=None,
                               n_perm=self.N_PERM, n_perm_retrieval=self.N_PERM_RETR)

    def test_planted_correspondence_positive(self):
        res = self._run("planted")
        self.assertTrue(res["decision_flags"]["gate_pass"], res["gate_G"])
        self.assertLess(res["P1_spearman_vs_Xsym"]["p"], 0.01)
        self.assertLess(res["P2_partial_orig3_vs_Xsym"]["p"], 0.01)
        self.assertTrue(res["outcome"].startswith("PASS"), res["outcome"])
        # the A6 retrieval use case should also work on a planted world
        self.assertGreater(res["secondaries"]["S4_retrieval_famA"]["acc"],
                           res["secondaries"]["S4_retrieval_famA"]["chance_acc"])

    def test_structured_null(self):
        res = self._run("structured-null")
        self.assertTrue(res["decision_flags"]["gate_pass"],
                        "structured null must have real correspondence: " + str(res["gate_G"]))
        self.assertGreater(res["P1_spearman_vs_Xsym"]["p"], 0.05)
        self.assertTrue(res["outcome"].startswith("NULL"), res["outcome"])

    def test_pure_noise_gate_fails(self):
        res = self._run("pure-noise")
        self.assertFalse(res["decision_flags"]["gate_pass"], res["gate_G"])
        self.assertTrue(res["outcome"].startswith("PRECONDITION FAIL"), res["outcome"])


class TestHolm(unittest.TestCase):
    def test_holm_stepdown(self):
        out = e8.holm({"a": 0.001, "b": 0.02, "c": 0.9})
        self.assertAlmostEqual(out["a"]["p_holm"], 0.003)
        self.assertAlmostEqual(out["b"]["p_holm"], 0.04)
        self.assertAlmostEqual(out["c"]["p_holm"], 0.9)
        self.assertTrue(out["b"]["reject_at_0.05"])
        self.assertFalse(out["c"]["reject_at_0.05"])


class TestMockEndToEnd(unittest.TestCase):
    def test_runner_then_analyze(self):
        with tempfile.TemporaryDirectory(prefix="e8-mock-") as td:
            rc = subprocess.run(
                [sys.executable, str(HERE / "runner" / "e8_runner.py"), "--mock",
                 "--out-dir", td,
                 "--e2-inputs-dir", str(REPO / "poc" / "e2" / "inputs"),
                 "--manifest", str(HERE / "inputs" / "e8-manifest.json")],
                capture_output=True, text=True)
            self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
            with open(os.path.join(td, "e8-extraction.json")) as f:
                ext = json.load(f)
            self.assertTrue(ext["mock"])
            self.assertEqual(len(ext["families"]), 2)
            # attrition path exercised: >10-char words are OOV in the mock
            dropped = {w for fam in ext["families"].values()
                       for w in fam["in_vocab_dropped_words"]}
            self.assertTrue(all(len(w) > 10 for w in dropped))

            rc2 = subprocess.run(
                [sys.executable, str(HERE / "analyze.py"), td],
                capture_output=True, text=True)
            self.assertEqual(rc2.returncode, 0, rc2.stdout + rc2.stderr)
            with open(os.path.join(td, "results-e8.json")) as f:
                res = json.load(f)
            self.assertTrue(res["mock"])
            self.assertIn("outcome", res)
            self.assertIn("gate_G", res["results"])
            with open(os.path.join(td, "verdict-e8.md")) as f:
                verdict = f.read()
            self.assertIn("MOCK RUN", verdict)
            self.assertIn("OUTCOME", verdict)

    def test_runner_fails_closed_on_manifest_drift(self):
        with tempfile.TemporaryDirectory(prefix="e8-pin-") as td:
            man_path = os.path.join(td, "bad-manifest.json")
            with open(HERE / "inputs" / "e8-manifest.json") as f:
                man = json.load(f)
            man["e2InputSha256"]["items.json"] = "0" * 64
            with open(man_path, "w") as f:
                json.dump(man, f)
            rc = subprocess.run(
                [sys.executable, str(HERE / "runner" / "e8_runner.py"), "--mock",
                 "--out-dir", td, "--manifest", man_path,
                 "--e2-inputs-dir", str(REPO / "poc" / "e2" / "inputs")],
                capture_output=True, text=True)
            self.assertNotEqual(rc.returncode, 0)
            self.assertIn("ERR_MANIFEST_PIN", rc.stdout + rc.stderr)


class TestExt1(unittest.TestCase):
    """Extension 1 (bead fnq): manifest pins, family filter, mock e2e."""

    def test_manifest_pins_committed_signatures(self):
        with open(HERE / "inputs" / "e8-manifest-ext1.json") as f:
            man = json.load(f)
        self.assertEqual(man["extraction_families"], ["smollm2-135m"])
        self.assertEqual(man["pairs"], [["gpt2", "smollm2-135m"], ["pythia-160m", "smollm2-135m"]])
        stamp = REPO / man["reusedSignatures"]["stamp"]
        import hashlib
        for fam, pin in man["reusedSignatures"]["families"].items():
            with open(stamp / pin["file"], "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), pin["sha256"],
                                 f"{fam} committed signature drifted")
        spec = man["families"]["smollm2-135m"]
        self.assertEqual(spec["site"], "mlp_output")
        self.assertEqual(spec["block_index"], spec["n_layers_expected"] // 2)
        self.assertEqual(spec["d_sae"], 36864)

    def test_mock_ext1_end_to_end(self):
        with tempfile.TemporaryDirectory(prefix="e8-ext1-") as td:
            rc = subprocess.run(
                [sys.executable, str(HERE / "runner" / "e8_runner.py"), "--mock",
                 "--out-dir", td,
                 "--e2-inputs-dir", str(REPO / "poc" / "e2" / "inputs"),
                 "--manifest", str(HERE / "inputs" / "e8-manifest-ext1.json")],
                capture_output=True, text=True)
            self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
            with open(os.path.join(td, "e8-extraction.json")) as f:
                ext = json.load(f)
            # extraction_families filter honoured: family C only
            self.assertEqual(list(ext["families"]), ["smollm2-135m"])

            rc2 = subprocess.run(
                [sys.executable, str(HERE / "analyze_ext1.py"), td],
                capture_output=True, text=True)
            self.assertEqual(rc2.returncode, 0, rc2.stdout + rc2.stderr)
            with open(os.path.join(td, "results-e8-ext1.json")) as f:
                res = json.load(f)
            self.assertTrue(res["mock"])
            self.assertEqual(len(res["per_pair"]), 2)
            self.assertIn("replicated", res)
            for pdata in res["per_pair"].values():
                self.assertIn("gate_G", pdata["battery"])
            with open(os.path.join(td, "verdict-e8-ext1.md")) as f:
                v = f.read()
            self.assertIn("MOCK RUN", v)
            self.assertIn("Pre-registered replication rule", v)


class TestScale(unittest.TestCase):
    """Extension 2 (at-scale): manifest pins + mock e2e at --limit 80."""

    def test_scale_manifest_pins(self):
        with open(HERE / "inputs" / "e8-manifest-scale.json") as f:
            man = json.load(f)
        self.assertEqual(man["n"], 1054)
        self.assertEqual(len(man["ids"]), 1054)
        self.assertEqual(len(man["pairs"]), 3)
        self.assertEqual(man["pairs"][0], ["gpt2", "pythia-160m"])  # headline pair
        import hashlib
        for name, pin in man["kernelRdmScale"]["rdms"].items():
            with open(HERE / pin["file"], "rb") as f:
                self.assertEqual(hashlib.sha256(f.read()).hexdigest(), pin["sha256"],
                                 f"kernel RDM {name} drifted")
        # at-scale distortion measured and sane
        d = man["kernelRdmScale"]["atScaleDistortionRdmSpearman"]
        self.assertGreater(d["jl512"], 0.9)
        # GLOSS-HASH matches the pinned E4 artifact
        with open(REPO / "poc" / "e4" / "GLOSS-HASH.txt") as f:
            pinned = f.readline().split("=")[1].strip()
        self.assertEqual(man["glossHash"], pinned)

    def test_mock_scale_end_to_end(self):
        with tempfile.TemporaryDirectory(prefix="e8-scale-") as td:
            rc = subprocess.run(
                [sys.executable, str(HERE / "runner" / "e8_scale_runner.py"), "--mock",
                 "--limit", "60", "--out-dir", td,
                 "--manifest", str(HERE / "inputs" / "e8-manifest-scale.json"),
                 "--glosses", str(REPO / "poc" / "e4" / "inputs" / "glosses.jsonl")],
                capture_output=True, text=True)
            self.assertEqual(rc.returncode, 0, rc.stdout + rc.stderr)
            with open(os.path.join(td, "e8-scale-extraction.json")) as f:
                ext = json.load(f)
            self.assertTrue(ext["mock"])
            self.assertEqual(ext["n_concepts"], 60)
            self.assertEqual(len(ext["families"]), 3)
            self.assertEqual(len(ext["embedders"]), 2)

            rc2 = subprocess.run(
                [sys.executable, str(HERE / "analyze_scale.py"), td],
                capture_output=True, text=True)
            self.assertEqual(rc2.returncode, 0, rc2.stdout + rc2.stderr)
            with open(os.path.join(td, "results-e8-scale.json")) as f:
                res = json.load(f)
            self.assertTrue(res["mock"])
            self.assertEqual(len(res["per_pair"]), 3)
            self.assertIn("headline_pass", res)
            with open(os.path.join(td, "verdict-e8-scale.md")) as f:
                v = f.read()
            self.assertIn("MOCK RUN", v)
            self.assertIn("headline rule", v)

    def test_limit_rejected_without_mock(self):
        rc = subprocess.run(
            [sys.executable, str(HERE / "runner" / "e8_scale_runner.py"),
             "--limit", "10", "--out-dir", "/tmp/never",
             "--manifest", str(HERE / "inputs" / "e8-manifest-scale.json"),
             "--glosses", str(REPO / "poc" / "e4" / "inputs" / "glosses.jsonl")],
            capture_output=True, text=True)
        self.assertNotEqual(rc.returncode, 0)
        self.assertIn("ERR_LIMIT", rc.stdout + rc.stderr)


class TestModalWiring(unittest.TestCase):
    """Import poc/modal/modal_e8.py against a Modal stub; no token, no network."""

    def _stub_modal(self):
        stub = types.ModuleType("modal")

        class _Image:
            @classmethod
            def debian_slim(cls, python_version=None):
                return cls()

            def pip_install(self, *a, **k):
                return self

            def add_local_python_source(self, *a, **k):
                return self

            def add_local_file(self, src, dst):
                assert os.path.exists(str(src)), f"staged file missing: {src}"
                return self

            def add_local_dir(self, src, remote_path=None):
                assert os.path.isdir(str(src))
                return self

        class _Volume:
            @staticmethod
            def from_name(name, create_if_missing=False):
                return object()

        class _App:
            def __init__(self, name):
                self.name = name

            def function(self, **kw):
                def deco(fn):
                    fn.remote = fn
                    return fn
                return deco

            def local_entrypoint(self):
                def deco(fn):
                    return fn
                return deco

        stub.App, stub.Image, stub.Volume = _App, _Image, _Volume
        stub.__version__ = "stub"
        return stub

    def test_import_and_dry_plan(self):
        saved_modal = sys.modules.get("modal")
        saved_path = list(sys.path)
        sys.modules["modal"] = self._stub_modal()
        sys.path.insert(0, str(REPO / "poc" / "modal"))
        try:
            sys.modules.pop("modal_e8", None)
            import modal_e8  # noqa: F401  (staged-file existence asserted in stub)
            man = modal_e8._staged_manifest()
            self.assertEqual(len(man), 9)
            with open(HERE / "inputs" / "e8-manifest.json", "rb") as f:
                import hashlib
                self.assertEqual(man["e8/inputs/e8-manifest.json"],
                                 hashlib.sha256(f.read()).hexdigest())
            buf = io.StringIO()
            with redirect_stdout(buf):
                modal_e8._print_plan()
            plan = buf.getvalue()
            self.assertIn("GB", plan)
            self.assertIn("$", plan)
            self.assertIn("kot-hf-cache", plan)
        finally:
            sys.modules.pop("modal_e8", None)
            if saved_modal is not None:
                sys.modules["modal"] = saved_modal
            else:
                sys.modules.pop("modal", None)
            sys.path[:] = saved_path


if __name__ == "__main__":
    unittest.main()
