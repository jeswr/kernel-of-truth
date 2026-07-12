#!/usr/bin/env python3
"""knull v3-vs-v4 sample responses on Modal CPU (maintainer issue 17,
deliverable 2) — PROVISIONAL, ILLUSTRATIVE, NOT verdict-bearing.

WHY MODAL: the coordinator box has no local torch (ModuleNotFoundError), so
the actual-model generations the maintainer asked for — the SAME 8 prompts
answered by the SAME small model under the v3 store vs the re-authored v4
store — run in a Modal container built from the SAME pinned image
requirements as the f2b/f2b-transfer/casc-0 line (poc/modal/
requirements-image.txt; reuse pin im-6uXR6RyVQV15h2B3gtpOG2 — compare the
digest in the provenance sidecar at collection). CPU-only function (no GPU):
16 greedy generations of a 360M model, ~pennies.

SINGLE-SOURCING (nothing re-authored here):
  prompts + context   poc/knull/run_sample_responses.py (staged into the
                      container and IMPORTED: PROMPTS, build_messages,
                      load_store, MODEL_ID, MAX_NEW_TOKENS)
  markdown            poc/knull/render_sample_responses.py (run locally by
                      this wrapper's entrypoint on the returned JSON)
  model pin           HuggingFaceTB/SmolLM2-360M-Instruct at the
                      programme-wide pinned revision (casc-0/a5-llm/f2 pin)
                      a10cc1512eabd3dde888204e902eca88bddb4951
  decode              GREEDY (do_sample=False), max_new_tokens=200, CPU,
                      float32, torch.manual_seed(0) — verbatim the settings
                      documented in run_sample_responses.py; disclosed in
                      both output artifacts

COORDINATOR RUN (this box; agents have no modal tokens):
  source ~/.config/kot/modal.env; export MODAL_TOKEN_ID
  poc/modal/.venv/bin/modal run poc/knull/modal/modal_knull_samples.py --mock  # transport smoke, no model, ~$0
  poc/modal/.venv/bin/modal run poc/knull/modal/modal_knull_samples.py         # the real 16 generations

WHAT IT WRITES (directly, on the coordinator box):
  real:  poc/knull/sample-responses.json  + poc/knull/sample-responses.md
  mock:  poc/knull/sample-responses-mock.json + ...-mock.md (stub outputs,
         loudly labelled MOCK — never overwrites the real artifacts)
plus a full sidecar bundle (provenance-modal.json, run log, RUNNER_EXIT)
under poc/knull/results-incoming/<UTC stamp>-modal/. Nothing is
auto-committed.

Token-free sanity path: python3 poc/knull/modal/modal_knull_samples.py
--print-manifest (staged-bytes sha only, no modal import, $0).

Standing memory: if the local client is killed, `modal app stop ap-<id>` —
the remote task outlives the client.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    import modal
except ImportError:  # --print-manifest works without a modal install
    modal = None

_HERE = Path(__file__).resolve().parent
try:
    REPO_ROOT = _HERE.parents[2]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
_MODAL_TOOLS = REPO_ROOT / "poc" / "modal"
sys.path.insert(0, str(_MODAL_TOOLS))
import modal_common as mc  # noqa: E402  (stdlib-only helper, poc/modal)

KNULL_DIR = REPO_ROOT / "poc" / "knull"
HARNESS = KNULL_DIR / "run_sample_responses.py"
RENDERER = KNULL_DIR / "render_sample_responses.py"
STORE_V3 = KNULL_DIR / "inputs-v3" / "plain-authored.json"
STORE_V4 = KNULL_DIR / "inputs-v4" / "plain-authored.json"
IMAGE_REQS = _MODAL_TOOLS / "requirements-image.txt"
INCOMING_ROOT = KNULL_DIR / "results-incoming"

REMOTE_KNULL = "/root/kot/poc/knull"
REMOTE_OUT = "/tmp/knull-samples"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 2 * 3600

# Programme-wide R2 pin (casc-0 record, a5-llm + f2 manifests): the harness's
# MODEL_ID plus this revision names one exact set of weights.
MODEL_REVISION = "a10cc1512eabd3dde888204e902eca88bddb4951"


def _image_pins() -> list:
    p = IMAGE_REQS
    if not p.exists():
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def _manifest(harness: str, store_v3: str, store_v4: str, image_reqs: str) -> dict:
    """sha256 manifest over the EXACT bytes the run consumes (fail-closed
    staging check, same pattern as modal_casc0.py / modal_common contract)."""
    return {
        "run_sample_responses.py": mc.sha256_file(harness),
        "inputs-v3/plain-authored.json": mc.sha256_file(store_v3),
        "inputs-v4/plain-authored.json": mc.sha256_file(store_v4),
        "modal/requirements-image.txt": mc.sha256_file(image_reqs),
    }


def _local_manifest() -> dict:
    return _manifest(str(HARNESS), str(STORE_V3), str(STORE_V4), str(IMAGE_REQS))


def _run_in_container(mock: bool, local_manifest: dict) -> dict:
    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = _manifest(
        f"{REMOTE_KNULL}/run_sample_responses.py",
        f"{REMOTE_KNULL}/inputs-v3/plain-authored.json",
        f"{REMOTE_KNULL}/inputs-v4/plain-authored.json",
        "/root/kot/poc/modal/requirements-image.txt",
    )
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    # Import the staged harness — prompts, context design, and stores are
    # single-sourced from run_sample_responses.py, never re-declared here.
    sys.path.insert(0, REMOTE_KNULL)
    import run_sample_responses as rs

    log_lines = []

    def _log(msg):
        log_lines.append(msg + "\n")
        print(msg, flush=True)

    arms = {}
    for tag in ("v3", "v4"):
        path, sha, defs = rs.load_store(tag)
        arms[tag] = {"path": f"poc/knull/inputs-{tag}/plain-authored.json",
                     "sha256": sha, "defs": defs}
        for item in rs.PROMPTS:
            for lab in item["labels"]:
                if lab not in defs:
                    raise SystemExit(
                        f"ERR_MISSING_LABEL: {lab!r} not in {tag} store")
    _log(f"stores validated: v3 {arms['v3']['sha256'][:12]}… / "
         f"v4 {arms['v4']['sha256'][:12]}… ({len(rs.PROMPTS)} prompts, "
         f"all labels present in both arms)")

    if mock:
        _log("MOCK transport smoke: no model loaded, outputs are stubs")
        gen = None
    else:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        # HFLM pattern carried from poc/casc-0/runner/casc0_runner.py: pinned
        # revision, eval mode, no grads. dtype/device/decoding are verbatim
        # run_sample_responses.py (CPU float32 greedy).
        torch.manual_seed(0)
        torch.set_num_threads(max(1, os.cpu_count()))
        tok = AutoTokenizer.from_pretrained(rs.MODEL_ID, revision=MODEL_REVISION)
        model = AutoModelForCausalLM.from_pretrained(
            rs.MODEL_ID, revision=MODEL_REVISION, torch_dtype=torch.float32)
        model.eval()
        for p in model.parameters():
            p.requires_grad_(False)
        _log(f"loaded {rs.MODEL_ID}@{MODEL_REVISION[:12]}… (cpu, float32)")

        def gen(msgs):
            ids = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                          return_tensors="pt")
            t0 = time.time()
            with torch.no_grad():
                out = model.generate(ids, max_new_tokens=rs.MAX_NEW_TOKENS,
                                     do_sample=False,
                                     pad_token_id=tok.eos_token_id)
            text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
            return text.strip(), ids.shape[1], out.shape[1] - ids.shape[1], time.time() - t0

    results = []
    for item in rs.PROMPTS:
        row = {"id": item["id"], "question": item["q"],
               "labels": item["labels"], "outputs": {}}
        for tag in ("v3", "v4"):
            msgs = rs.build_messages(arms[tag]["defs"], item)
            if mock:
                row["outputs"][tag] = (
                    "[MOCK transport smoke - NOT a model generation; context "
                    "was built from the real %s store (%d chars) but no model "
                    "was loaded]" % (tag, len(msgs[0]["content"])))
                _log(f"[{item['id']}/{tag}] MOCK stub")
            else:
                text, n_in, n_out, dt = gen(msgs)
                row["outputs"][tag] = text
                _log(f"[{item['id']}/{tag}] {n_in} prompt toks -> "
                     f"{n_out} new toks in {dt:.1f}s")
        results.append(row)

    artifact = {
        "schema": "kot-knull-sample-responses/1",
        "status": ("MOCK TRANSPORT SMOKE - stub outputs, no model loaded, "
                   "NOT generations" if mock else
                   "PROVISIONAL illustrative generations - actual raw "
                   "small-model outputs, not verdict-bearing, not a "
                   "pre-registered Phase-X harness"),
        "model": rs.MODEL_ID,
        "model_revision": MODEL_REVISION,
        "decode": {"strategy": ("MOCK (no decoding performed)" if mock else
                                "greedy (do_sample=False)"),
                   "max_new_tokens": rs.MAX_NEW_TOKENS,
                   "dtype": "float32", "device": "cpu",
                   "torch_manual_seed": 0,
                   "seed": "torch_manual_seed=0 (greedy: seed inert)"},
        "context_design": "per-prompt fixed label set, identical across arms;"
                          " store entries rendered as a reference list in the"
                          " system message; headwords shown (usage"
                          " illustration, not the blind gate)",
        "stores": {t: {k: v for k, v in arms[t].items() if k != "defs"}
                   for t in arms},
        "harness": "poc/knull/modal/modal_knull_samples.py via Modal CPU "
                   "(prompt set + context design single-sourced from "
                   "run_sample_responses.py; image from the pinned f2b "
                   "requirements, reuse pin im-6uXR6RyVQV15h2B3gtpOG2)",
        "date": time.strftime("%Y-%m-%d", time.gmtime()),
        "results": results,
    }

    os.makedirs(REMOTE_OUT, exist_ok=True)
    name = "sample-responses-mock.json" if mock else "sample-responses.json"
    with open(os.path.join(REMOTE_OUT, name), "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=1, sort_keys=False)
        f.write("\n")
    _log(f"wrote {name} ({len(results)} prompts x 2 arms)")

    packages = {}
    for pkg in ("numpy", "torch", "transformers"):
        try:
            packages[pkg] = __import__(pkg).__version__
        except Exception as e:  # noqa: BLE001
            packages[pkg] = f"unavailable: {e}"

    prov = cmc.build_provenance(
        transport="modal",
        gpu_requested="none (CPU function)",
        gpu_seen=cmc.gpu_info(),
        staged_manifest=staged,
        runner_exit=0,
        started_utc=started,
        finished_utc=cmc.utcnow_iso(),
        packages=packages,
        environment=cmc.redact_env(dict(os.environ)),
        notes="illustrative knull v3-vs-v4 sample generations (maintainer "
              "issue 17); image built from the pinned f2b requirements "
              "(reuse pin im-6uXR6RyVQV15h2B3gtpOG2 — compare at collection);"
              " model pinned at the programme-wide R2 revision",
    )
    files = cmc.package_results(REMOTE_OUT, run_log="".join(log_lines),
                                rc=0, provenance=prov)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return files


if modal is not None:
    app = modal.App("kot-knull-samples")

    image = (
        modal.Image.debian_slim(python_version="3.11")
        .pip_install(*_image_pins())
        .add_local_python_source("modal_common")
        .add_local_file(HARNESS, f"{REMOTE_KNULL}/run_sample_responses.py")
        .add_local_file(STORE_V3, f"{REMOTE_KNULL}/inputs-v3/plain-authored.json")
        .add_local_file(STORE_V4, f"{REMOTE_KNULL}/inputs-v4/plain-authored.json")
        .add_local_file(IMAGE_REQS, "/root/kot/poc/modal/requirements-image.txt")
    )

    hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)

    @app.function(image=image, cpu=8.0, memory=8192,
                  volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
    def run_samples(mock: bool = False, local_manifest: dict = None) -> dict:  # noqa: RUF013
        return _run_in_container(mock, local_manifest or {})

    @app.local_entrypoint()
    def main(mock: bool = False) -> None:
        local_manifest = _local_manifest()
        base = "sample-responses-mock" if mock else "sample-responses"
        print(f"kot-knull-samples via Modal (CPU): mock={mock} "
              f"({len(local_manifest)} staged files, harness "
              f"{local_manifest['run_sample_responses.py'][:12]}…)")

        files = run_samples.remote(mock=mock, local_manifest=local_manifest)

        # Full sidecar bundle -> results-incoming (provenance discipline).
        stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-modal"
        dest = INCOMING_ROOT / stamp
        mc.unpack_files(files, str(dest))

        prov_path = dest / mc.PROVENANCE_NAME
        prov = json.loads(prov_path.read_text())
        try:
            image_id = image.object_id
        except Exception:  # noqa: BLE001
            image_id = None
        prov["coordinator"] = {
            "modal_client": modal.__version__,
            "image_object_id": image_id,
            "image_reuse_pin": "im-6uXR6RyVQV15h2B3gtpOG2",
            "local_manifest_matched": True,
            "collected_utc": mc.utcnow_iso(),
        }
        prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

        # The two deliverables, written DIRECTLY where issue 17 expects them.
        json_name = base + ".json"
        if json_name not in files:
            raise SystemExit(f"ERR_NO_ARTIFACT: container returned no {json_name}")
        (KNULL_DIR / json_name).write_bytes(files[json_name])
        rc = subprocess.call([sys.executable, str(RENDERER), base],
                             cwd=str(KNULL_DIR))
        if rc != 0:
            raise SystemExit(f"ERR_RENDER: render_sample_responses.py exited rc={rc}")

        print(f"\nwrote {len(files)} sidecar files to {dest}")
        print(f"wrote {KNULL_DIR / json_name}")
        print(f"wrote {KNULL_DIR / (base + '.md')}")
        if mock:
            print("MOCK smoke complete - stub outputs only; rerun without "
                  "--mock for the real generations")
        else:
            print("done - review and commit deliberately (results are NOT "
                  "auto-committed)")


if __name__ == "__main__":
    # sha-only path: works with NO modal install, NO network, $0.
    if "--print-manifest" in sys.argv:
        man = _local_manifest()
        print(f"staged files: {len(man)}")
        for k, v in sorted(man.items()):
            print(f"  {k}  {v}")
        sys.exit(0)
    raise SystemExit("run via `modal run poc/knull/modal/modal_knull_samples.py"
                     " [--mock]` or use --print-manifest")
