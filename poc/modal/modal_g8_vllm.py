#!/usr/bin/env python3
"""G8 locator LLM host: Qwen2.5-7B-Instruct behind an OpenAI-compatible endpoint
on Modal (vLLM), for the 39 g8 locator prompts (frozen record
registry/experiments/g8.json pins NO host model — R0 — so the model + revision +
decode are pinned in the RUN CONFIG, not the frozen record).

Runner helper only; not part of the frozen instrument. The LLM call is the sole
nondeterminism in g8 and every candidate it proposes is F-verified afterwards by
tools/experiments/g8_instrument.py (canonical-content equality), so the host is
untrusted: it can fail to find a name, it cannot silently mislocate.

Model  : Qwen/Qwen2.5-7B-Instruct  (Apache-2.0, ungated, real capability)
Revision (pinned): a09a35458c702b33eeacc393d103063234e8bc28
Serve  : vLLM OpenAI-compatible api_server, temperature is set to 0 by the
         instrument's --call-llm; api-key auth via the kot-g8-vllm-key Modal
         secret (VLLM_API_KEY; never committed/printed).

    poc/modal/.venv/bin/modal deploy poc/modal/modal_g8_vllm.py
    # -> prints the web endpoint URL; base-url for --call-llm is <url>/v1
    poc/modal/.venv/bin/modal app stop kot-g8-vllm     # teardown after the run
"""

import os
import subprocess

import modal

MODEL = "Qwen/Qwen2.5-7B-Instruct"
REVISION = "a09a35458c702b33eeacc393d103063234e8bc28"
VLLM_PORT = 8000
HF_CACHE = "/root/.cache/huggingface"

app = modal.App("kot-g8-vllm")

# Modal-standard vLLM image (debian_slim + pip vllm) so Modal controls/knows the
# Python; torch + CUDA runtime ride in on the vllm wheel, the GPU driver comes
# from the Modal host.
image = (
    modal.Image.debian_slim(python_version="3.12")
    # transformers pinned to the version vLLM 0.7.3 shipped against; the newer
    # transformers pip resolves by default breaks the Qwen2 tokenizer
    # (all_special_tokens_extended AttributeError).
    .pip_install(
        "vllm==0.7.3",
        "transformers==4.48.3",
        "huggingface_hub[hf_transfer]",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


@app.function(
    image=image,
    gpu="A10G",
    volumes={HF_CACHE: hf_cache},
    secrets=[modal.Secret.from_name("kot-g8-vllm-key")],
    timeout=60 * 60,
    scaledown_window=600,
    min_containers=1,
)
@modal.web_server(port=VLLM_PORT, startup_timeout=30 * 60)
def serve():
    # Auth: vLLM reads the bearer key from the VLLM_API_KEY env var (injected by
    # the kot-g8-vllm-key secret). We deliberately do NOT pass --api-key so the
    # key never lands in the server's logged args namespace.
    assert os.environ.get("VLLM_API_KEY"), "VLLM_API_KEY secret not injected"
    cmd = [
        "python3", "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL,
        "--revision", REVISION,
        "--served-model-name", MODEL,
        "--host", "0.0.0.0",
        "--port", str(VLLM_PORT),
        "--max-model-len", "8192",
        "--gpu-memory-utilization", "0.90",
        "--disable-log-requests",
    ]
    subprocess.Popen(cmd)
