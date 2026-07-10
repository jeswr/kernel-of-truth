#!/usr/bin/env python3
"""nsk1 PATH-VERIFICATION smoke (NOT an experiment; nothing measured here is ever
recorded anywhere). De-risks the flagship nsk1 GPU run by exercising, end-to-end
on a Modal serverless GPU, the exact capabilities the nsk1 arms depend on:

  1. Modal auth + a real A10G (or L4) provisions.
  2. SmolLM2-135M-Instruct loads on cuda (weights pull once into Volume kot-hf-cache).
  3. A forward pass emits a coherent next-token distribution.
  4. A forward HOOK can READ the residual stream at a chosen decoder layer
     (patchscope-decode source) — captured hidden state, correct [batch, seq, d_model].
  5. A forward HOOK can WRITE to the residual stream (steering write-back): add a
     vector to a layer's output and confirm the next-token logits actually move.
  6. output_hidden_states cross-checks the hook-captured tensor byte-for-byte.

This is the Opus-execution "verify the transport path" smoke, sibling to
poc/modal/modal_prm_smoke.py and modal_int4_smoke.py. It defines NO science:
no kernel, no arm logic, no measurement — just a capability probe. The flagship
itself runs the Fable-frozen runner, not this file.

    .venv/bin/modal run poc/modal/modal_nsk1_hooksmoke.py               # A10G (default)
    .venv/bin/modal run poc/modal/modal_nsk1_hooksmoke.py --gpu l4     # L4 flavour
    .venv/bin/modal run poc/modal/modal_nsk1_hooksmoke.py --model HuggingFaceTB/SmolLM2-360M-Instruct
"""

from __future__ import annotations

import sys
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

HF_CACHE_MOUNT = "/root/.cache/huggingface"
GPU_CHOICES = ("A10G", "L4", "T4")
DEFAULT_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
# Probe layer for the residual-stream read/write (mid-stack; SmolLM2-135M has 30 layers).
PROBE_LAYER = 8
STEER_SCALE = 8.0  # large enough that the perturbed logits must move if write-back works


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():  # container-side re-import: image already built
        return []
    lines = p.read_text().splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


app = modal.App("kot-nsk1-hooksmoke")

image = modal.Image.debian_slim(python_version="3.11").pip_install(*_image_pins())
hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _probe(model_id: str, gpu_requested: str) -> dict:
    import json
    import traceback
    try:
        return _probe_body(model_id, gpu_requested)
    except Exception as e:  # noqa: BLE001
        # Never let a torch-typed exception object cross back to the torch-free
        # local venv (that manifests as an opaque DeserializationError). Return
        # a pure-JSON error payload and echo it in the container logs.
        tb = traceback.format_exc()
        print("PROBE ERROR:", repr(e))
        print(tb)
        return {"model_id": model_id, "gpu_requested": gpu_requested,
                "error": repr(e), "traceback": tb}


def _probe_body(model_id: str, gpu_requested: str) -> dict:
    import json
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    out: dict = {"model_id": model_id, "gpu_requested": gpu_requested}

    # ---- GPU identity --------------------------------------------------------
    out["cuda_available"] = bool(torch.cuda.is_available())
    out["gpu_name"] = str(torch.cuda.get_device_name(0)) if torch.cuda.is_available() else None
    out["torch"] = str(torch.__version__)
    print(f"[probe] gpu={out['gpu_name']} cuda={out['cuda_available']} torch={out['torch']}")

    # ---- (2) model + tokenizer load -----------------------------------------
    print(f"[probe] loading {model_id} ...")
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
    model.to("cuda").eval()
    out["n_layers"] = model.config.num_hidden_layers
    out["d_model"] = model.config.hidden_size
    layers = model.model.layers  # SmolLM2 == Llama arch: model.model.layers[i]
    assert 0 <= PROBE_LAYER < len(layers), "PROBE_LAYER out of range"

    # Use the chat template (Instruct variant) — this is the surface nsk1 uses.
    msgs = [{"role": "user", "content": "The capital of France is"}]
    try:
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt")
    except Exception:  # base checkpoints have no chat template
        ids = tok("The capital of France is", return_tensors="pt").input_ids
    ids = ids.to("cuda")

    # ---- (3) baseline forward + (4) READ hook + (6) hidden_states cross-check
    captured = {}

    def read_hook(_mod, _inp, output):
        hs = output[0] if isinstance(output, tuple) else output
        captured["resid"] = hs.detach().clone()

    h = layers[PROBE_LAYER].register_forward_hook(read_hook)
    with torch.no_grad():
        base = model(ids, output_hidden_states=True)
    h.remove()

    base_logits = base.logits[:, -1, :].float()
    base_top = tok.decode(int(base_logits.argmax(-1)[0]))
    resid = captured["resid"]
    out["read_hook_shape"] = list(resid.shape)  # [batch, seq, d_model]
    out["read_hook_ok"] = list(resid.shape) == [ids.shape[0], ids.shape[1], out["d_model"]]

    # hidden_states[PROBE_LAYER+1] is the OUTPUT of decoder layer PROBE_LAYER.
    hs_ref = base.hidden_states[PROBE_LAYER + 1]
    out["hidden_states_matches_hook"] = bool(torch.equal(hs_ref, resid))
    out["baseline_top_token"] = base_top

    # ---- (5) WRITE hook: steering write-back to the residual stream ----------
    # Add a fixed steering vector at the last position of the probe layer's output
    # and confirm the next-token distribution moves. This is the exact mechanism
    # nsk1 steering arms need (write a vector back into the residual stream).
    steer = torch.randn(out["d_model"], generator=torch.Generator().manual_seed(0))
    steer = (steer / steer.norm() * STEER_SCALE).to(resid.dtype).to("cuda")

    def write_hook(_mod, _inp, output):
        is_tuple = isinstance(output, tuple)
        hs = output[0] if is_tuple else output
        hs = hs.clone()
        hs[:, -1, :] = hs[:, -1, :] + steer  # write-back at the generation position
        if is_tuple:
            return (hs,) + tuple(output[1:])
        return hs

    h2 = layers[PROBE_LAYER].register_forward_hook(write_hook)
    with torch.no_grad():
        steered = model(ids)
    h2.remove()

    steer_logits = steered.logits[:, -1, :].float()
    delta = float((steer_logits - base_logits).abs().max().item())
    out["steer_logit_max_abs_delta"] = round(delta, 4)
    out["write_hook_moved_logits"] = bool(delta > 1e-3)
    out["steered_top_token"] = str(tok.decode(int(steer_logits.argmax(-1)[0])))
    print(f"[probe] read_hook_shape={out['read_hook_shape']} "
          f"hs_match={out['hidden_states_matches_hook']} "
          f"steer_delta={out['steer_logit_max_abs_delta']} "
          f"base_top={out['baseline_top_token']!r} steered_top={out['steered_top_token']!r}")

    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    # Guarantee a torch-free, JSON-native payload crosses back to the local
    # (torch-free) venv — coerce through json so no exotic scalar can leak.
    return json.loads(json.dumps(out, default=str))


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=1800)
def probe_a10g(model_id: str) -> dict:
    return _probe(model_id, "A10G")


@app.function(image=image, gpu="L4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=1800)
def probe_l4(model_id: str) -> dict:
    return _probe(model_id, "L4")


@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=1800)
def probe_t4(model_id: str) -> dict:
    return _probe(model_id, "T4")


FUNCS = {"A10G": probe_a10g, "L4": probe_l4, "T4": probe_t4}


@app.local_entrypoint()
def main(gpu: str = "A10G", model: str = DEFAULT_MODEL) -> None:
    gpu = gpu.upper()
    if gpu not in FUNCS:
        raise SystemExit(f"ERR_GPU: --gpu must be one of {GPU_CHOICES}, got {gpu!r}")
    r = FUNCS[gpu].remote(model)

    print("\n=== nsk1 Modal path-verification smoke ===")
    for k in (
        "model_id", "gpu_requested", "gpu_name", "cuda_available", "torch",
        "n_layers", "d_model",
        "read_hook_shape", "read_hook_ok", "hidden_states_matches_hook",
        "baseline_top_token",
        "steer_logit_max_abs_delta", "write_hook_moved_logits", "steered_top_token",
    ):
        print(f"  {k:28s} = {r.get(k)}")

    ok = (
        r.get("cuda_available")
        and r.get("read_hook_ok")
        and r.get("hidden_states_matches_hook")
        and r.get("write_hook_moved_logits")
    )
    print("\nHOOK SMOKE:", "OK — GPU + SmolLM2 load + residual READ and WRITE hooks verified"
          if ok else "BROKEN — inspect the failing capability above")
    if not ok:
        raise SystemExit(1)
