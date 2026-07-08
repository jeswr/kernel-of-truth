#!/usr/bin/env python3
"""One-off smoke of the F2 real-path PRM backend (HFPRM in f2_runner.py):
loads Skywork-o1-Open-PRM-Qwen-2.5-1.5B at the PINNED revision on an A10G,
scores best-of-2 candidates on 3 pinned d-qa items, prints the scores.
Validates: trust_remote_code load, chat-template input, scalar sigmoid
readout, score discrimination signal. Costs pennies; NOT an experiment run —
no measurement from this smoke is ever recorded anywhere.

    .venv/bin/modal run poc/modal/modal_prm_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants never dereferenced
F2_DIR = REPO_ROOT / "poc" / "f2"

REMOTE_F2 = "/root/kot/poc/f2"
REMOTE_F0 = "/root/kot/poc/f0"
REMOTE_DATA = "/root/kot/data"
HF_CACHE_MOUNT = "/root/.cache/huggingface"


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():
        return []  # container re-import: image already built
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


app = modal.App("kot-f2-prm-smoke")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_file(F2_DIR / "runner" / "f2_runner.py",
                    f"{REMOTE_F2}/runner/f2_runner.py")
    .add_local_file(REPO_ROOT / "poc" / "f0" / "__init__.py",
                    f"{REMOTE_F0}/__init__.py")
    .add_local_file(REPO_ROOT / "poc" / "f0" / "flop_meter.py",
                    f"{REMOTE_F0}/flop_meter.py")
    .add_local_dir(F2_DIR / "inputs", remote_path=f"{REMOTE_F2}/inputs")
    .add_local_dir(REPO_ROOT / "data" / "d-qa", remote_path=f"{REMOTE_DATA}/d-qa")
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
              timeout=1800)
def smoke() -> dict:
    import json
    import os
    import sys as _sys
    _sys.path.insert(0, f"{REMOTE_F2}/runner")
    import f2_runner as f2

    with open(f"{REMOTE_F2}/inputs/f2-manifest.json") as fh:
        man = json.load(fh)
    frames = man["prompt_frames"]
    spec = man["models"]["prm"]
    print("loading PRM %s @ %s (trust_remote_code, bf16)"
          % (spec["repo"], spec["revision"][:12]))
    prm = f2.HFPRM(spec["repo"], spec["revision"], "cuda", frames)
    print("loaded: n_active=%d name=%s" % (prm.n_active, prm.name))

    items = [json.loads(l) for l in open(f"{REMOTE_DATA}/d-qa/items/covered.jsonl")
             if l.strip()][:3]
    out = {}
    for it in items:
        keys, gold = f2.item_keys_gold(it)
        scores = {k: prm.score(it, k, gold, 0, 0) for k in keys}
        out[it["id"]] = {"gold": gold, "scores": scores}
        print(it["id"], "gold=%s" % gold,
              " ".join("%s=%.4f" % kv for kv in sorted(scores.items())))
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return out


@app.local_entrypoint()
def main() -> None:
    out = smoke.remote()
    ok = all(len(set(v["scores"].values())) > 1 for v in out.values())
    print("\nPRM SMOKE:", "OK — backend loads, scores vary per candidate" if ok
          else "DEGENERATE — identical scores for all candidates, inspect")
    if not ok:
        raise SystemExit(1)
