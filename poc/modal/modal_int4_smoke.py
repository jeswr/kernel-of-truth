#!/usr/bin/env python3
"""One-off smoke of the F2 int4-quantized arm backend (HFLM int4 path in
f2_runner.py) + the bitsandbytes/accelerate image pins: loads SmolLM2-360M at
the PINNED revision in 4-bit on an A10G and scores one pinned d-qa item
through the IF-C constrained surface. Costs pennies; NOT an experiment run —
no measurement from this smoke is ever recorded anywhere.

    .venv/bin/modal run poc/modal/modal_int4_smoke.py
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


app = modal.App("kot-f2-int4-smoke")

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
              timeout=1200)
def smoke() -> dict:
    import json
    import sys as _sys
    _sys.path.insert(0, f"{REMOTE_F2}/runner")
    import f2_runner as f2

    import bitsandbytes
    import accelerate
    print("bitsandbytes", bitsandbytes.__version__,
          "accelerate", accelerate.__version__)

    with open(f"{REMOTE_F2}/inputs/f2-manifest.json") as fh:
        man = json.load(fh)
    spec = man["models"]["R2"]
    print("loading %s @ %s int4" % (spec["repo"], spec["revision"][:12]))
    lm = f2.HFLM(spec["repo"], spec["revision"], "cuda", int4=True)
    print("loaded: n_active=%d weight_bytes=%d" % (lm.n_active, lm.weight_bytes))

    it = [json.loads(l) for l in open(f"{REMOTE_DATA}/d-qa/items/covered.jsonl")
          if l.strip()][0]
    keys, gold = f2.item_keys_gold(it)
    prompt = f2.build_prompt(man["prompt_frames"], it)
    ans, conf = lm.choose(it, keys, gold, 0, 0, prompt=prompt)
    print("constrained choice:", ans, "margin %.4f" % conf, "(gold %s)" % gold)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return {"answer": ans, "margin": float(conf), "keys": keys}


@app.local_entrypoint()
def main() -> None:
    out = smoke.remote()
    ok = out["answer"] in out["keys"]
    print("\nINT4 SMOKE:", "OK — int4 backend loads and answers in-format"
          if ok else "BROKEN — answer outside the option set")
    if not ok:
        raise SystemExit(1)
