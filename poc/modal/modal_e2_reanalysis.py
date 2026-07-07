#!/usr/bin/env python3
"""E2 re-analysis extraction on Modal (beads kernel-of-truth-qha / -avt).

POST-HOC RE-ANALYSIS TRANSPORT (design-review change 1): re-extracts the three
model RDMs with the UNCHANGED poc/e2/runner/e2_runner.py extraction code (same
pinned image, same T4 class, byte-asserted inputs) and adds sentence-embedding
baseline RDMs over the same 51 items:

  - gloss text (kernel-v0 `gloss` field) and deterministic explication-text
    rendering (poc/e2/reanalysis/build_texts.py), each embedded with
    sentence-transformers/all-MiniLM-L6-v2 (mean-pool+L2) and
    BAAI/bge-small-en-v1.5 (CLS-pool+L2); bare probe words as descriptive extra.

NO statistics happen here — the container ships RDMs + provenance only; the
analysis (partial Spearman both ways, Mantel permutations, polarity strata)
runs on the CPU box via poc/e2/reanalysis/analyze.py, so it can be audited and
re-run without GPU spend. modal_e2.py is deliberately untouched.

    .venv/bin/modal run poc/modal/modal_e2_reanalysis.py        # T4, ~minutes

Results land in poc/e2/results-incoming/<UTC stamp>-reanalysis/ — NOT
auto-committed; review and commit deliberately, exactly like the E2 paths.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import modal_common as mc  # noqa: E402  (stdlib-only; shipped into the image below)

# ---- local (coordinator-side) paths ----------------------------------------
try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local-path constants are never dereferenced
E2_DIR = REPO_ROOT / "poc" / "e2"
RUNNER = E2_DIR / "runner" / "e2_runner.py"
RUNNER_REQS = E2_DIR / "runner" / "requirements.txt"
INPUTS_DIR = E2_DIR / "inputs"
TEXTS_JSON = E2_DIR / "reanalysis" / "inputs" / "reanalysis-texts.json"
INCOMING_ROOT = E2_DIR / "results-incoming"

# ---- container-side layout ---------------------------------------------------
REMOTE_E2 = "/root/kot/poc/e2"
REMOTE_TEXTS = f"{REMOTE_E2}/reanalysis/inputs/reanalysis-texts.json"
REMOTE_OUT = "/tmp/e2-reanalysis"
HF_CACHE_MOUNT = "/root/.cache/huggingface"
TIMEOUT_S = 3600  # extraction is minutes; 1 h failsafe

MODELS = [  # identical to e2_runner.DEFAULT_MODELS (asserted in-container)
    "roneneldan/TinyStories-33M",
    "HuggingFaceTB/SmolLM2-135M",
    "Qwen/Qwen2.5-0.5B",
]
EMBEDDERS = {  # pooling per model card; resolved commit hashes recorded in output
    "minilm": {"hf_id": "sentence-transformers/all-MiniLM-L6-v2", "pooling": "mean"},
    "bge": {"hf_id": "BAAI/bge-small-en-v1.5", "pooling": "cls"},
}


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():  # container-side re-import: image already built
        return []
    return [ln.strip() for ln in p.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


app = modal.App("kot-e2-reanalysis")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(*_image_pins())
    .add_local_python_source("modal_common")
    .add_local_file(RUNNER, f"{REMOTE_E2}/runner/e2_runner.py")
    .add_local_file(RUNNER_REQS, f"{REMOTE_E2}/runner/requirements.txt")
    .add_local_dir(INPUTS_DIR, remote_path=f"{REMOTE_E2}/inputs")
    .add_local_file(TEXTS_JSON, REMOTE_TEXTS)
)

hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _embed(texts: list, hf_id: str, pooling: str, device: str) -> tuple:
    """Sentence embeddings via plain transformers (no sentence-transformers dep).

    mean: attention-masked mean over last_hidden_state (all-MiniLM-L6-v2 card);
    cls:  last_hidden_state[:, 0] (bge-small-en-v1.5 card, symmetric task — no
    query instruction). L2-normalised either way. Returns (matrix, commit_hash).
    """
    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(hf_id)
    model = AutoModel.from_pretrained(hf_id).to(device).eval()
    out = []
    with torch.no_grad():
        for start in range(0, len(texts), 32):
            chunk = texts[start:start + 32]
            enc = tok(chunk, padding=True, truncation=True, max_length=512, return_tensors="pt")
            enc = {k: v.to(device) for k, v in enc.items()}
            hs = model(**enc).last_hidden_state
            if pooling == "mean":
                mask = enc["attention_mask"].unsqueeze(-1).float()
                vec = (hs * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
            elif pooling == "cls":
                vec = hs[:, 0]
            else:
                raise SystemExit(f"ERR_POOLING: {pooling!r}")
            vec = torch.nn.functional.normalize(vec, p=2, dim=1)
            out.append(vec.float().cpu().numpy())
    reps = np.vstack(out)
    commit = getattr(model.config, "_commit_hash", None)
    return reps, commit


def _run_in_container(local_manifest: dict) -> dict:
    import modal_common as cmc

    started = cmc.utcnow_iso()
    staged = cmc.input_manifest(
        f"{REMOTE_E2}/runner/e2_runner.py",
        f"{REMOTE_E2}/runner/requirements.txt",
        f"{REMOTE_E2}/inputs",
    )
    staged["reanalysis/inputs/reanalysis-texts.json"] = cmc.sha256_file(REMOTE_TEXTS)
    if staged != local_manifest:
        diff = sorted(k for k in set(staged) | set(local_manifest)
                      if staged.get(k) != local_manifest.get(k))
        raise SystemExit(f"ERR_STAGING_MISMATCH: staged bytes differ from coordinator: {diff}")

    sys.path.insert(0, f"{REMOTE_E2}/runner")
    import numpy as np

    import e2_runner as r  # the unchanged runner: extraction + in-vocab logic reused verbatim

    if r.DEFAULT_MODELS != MODELS:
        raise SystemExit("ERR_MODEL_DRIFT: e2_runner.DEFAULT_MODELS changed under the re-analysis")

    with open(f"{REMOTE_E2}/inputs/items.json") as f:
        items = json.load(f)["items"]
    with open(f"{REMOTE_E2}/inputs/contexts.json") as f:
        contexts = json.load(f)
    with open(REMOTE_TEXTS) as f:
        texts_doc = json.load(f)
    if texts_doc["ids"] != [it["id"] for it in items]:
        raise SystemExit("ERR_ITEM_ORDER: reanalysis-texts ids differ from items.json")

    log_lines = []

    def log(msg: str) -> None:
        print(msg, flush=True)
        log_lines.append(msg + "\n")

    # ---- model RDMs, identical extraction path to the original run ----
    models_out = {}
    for model_id in MODELS:
        log(f"=== extract {model_id} ===")
        ext = r.HFExtractor(model_id, "cuda", 64)
        in_vocab_mask = [ext.in_vocab(it["word"]) for it in items]
        dropped = [it["word"] for it, ok in zip(items, in_vocab_mask) if not ok]
        surviving = [it for it, ok in zip(items, in_vocab_mask) if ok]
        reps = r.pooled_reps_for_words(ext, [(it["word"], it["bank"]) for it in surviving], contexts)
        models_out[model_id] = {
            "mid_layer_index": int(ext.mid_layer),
            "n_layers_total": int(ext.n_layers),
            "in_vocab_dropped_words": dropped,
            "in_vocab_surviving_words": [it["word"] for it in surviving],
            "similarity_by_layer": {
                str(layer): r.cosine_sim_matrix(mat).tolist() for layer, mat in reps.items()
            },
        }
        log(f"  layers={sorted(reps)} dropped={dropped or 'none'}")
        del ext

    # ---- sentence-embedding baseline RDMs ----
    text_sets = {
        "gloss": texts_doc["glossTexts"],
        "explication": texts_doc["explicationTexts"],
        "word": texts_doc["words"],  # descriptive extra
    }
    embedders_out = {}
    for name, spec in EMBEDDERS.items():
        log(f"=== embed {name} ({spec['hf_id']}, {spec['pooling']}-pool) ===")
        sets = {}
        commit = None
        for set_name, texts in text_sets.items():
            reps, commit = _embed(texts, spec["hf_id"], spec["pooling"], "cuda")
            sets[set_name] = r.cosine_sim_matrix(np.asarray(reps, dtype=np.float64)).tolist()
        embedders_out[name] = {
            "hf_id": spec["hf_id"],
            "pooling": spec["pooling"] + "+l2norm",
            "resolved_commit_hash": commit,
            "similarity_by_textset": sets,
        }
        log(f"  commit={commit}")

    packages = {}
    for pkg in ("numpy", "torch", "transformers"):
        try:
            packages[pkg] = __import__(pkg).__version__
        except Exception as e:  # provenance must never kill a finished run
            packages[pkg] = f"unavailable: {e}"

    rdms = {
        "posture": "POST-HOC RE-ANALYSIS extraction (design-review change 1); "
                   "original pre-registered E2 verdict stands as reported",
        "date": cmc.utcnow_iso(),
        "encoderContentHash": texts_doc["encoderContentHash"],
        "corpusPin": texts_doc["corpusPin"],
        "rendererVersion": texts_doc["rendererVersion"],
        "ids": texts_doc["ids"],
        "words": texts_doc["words"],
        "notCounts": texts_doc["notCounts"],
        "models": models_out,
        "embedders": embedders_out,
        "extraction_note": "model reps via e2_runner.HFExtractor/pooled_reps_for_words "
                           "(unchanged bytes, sha256-asserted); embeddings via plain "
                           "transformers, pooling per model card",
    }
    os.makedirs(REMOTE_OUT, exist_ok=True)
    with open(os.path.join(REMOTE_OUT, "rdms-reanalysis.json"), "w") as f:
        json.dump(rdms, f)

    prov = cmc.build_provenance(
        transport="modal",
        gpu_requested="T4",
        gpu_seen=cmc.gpu_info(),
        staged_manifest=staged,
        runner_exit=0,
        started_utc=started,
        finished_utc=cmc.utcnow_iso(),
        packages=packages,
        environment=cmc.redact_env(dict(os.environ)),
        notes="re-analysis extraction only; statistics run on the CPU box "
              "(poc/e2/reanalysis/analyze.py); embedder commit hashes inside "
              "rdms-reanalysis.json",
    )
    files = cmc.package_results(REMOTE_OUT, run_log="".join(log_lines), rc=0, provenance=prov)
    try:
        hf_cache.commit()
    except Exception:
        pass
    return files


@app.function(image=image, gpu="T4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=TIMEOUT_S)
def run_reanalysis_t4(local_manifest: dict = None) -> dict:  # noqa: RUF013
    return _run_in_container(local_manifest or {})


@app.local_entrypoint()
def main(out_root: str = "") -> None:
    local_manifest = mc.input_manifest(str(RUNNER), str(RUNNER_REQS), str(INPUTS_DIR))
    local_manifest["reanalysis/inputs/reanalysis-texts.json"] = mc.sha256_file(str(TEXTS_JSON))
    print(f"kot-e2-reanalysis via Modal: T4, {len(local_manifest)} staged files, "
          f"texts {local_manifest['reanalysis/inputs/reanalysis-texts.json'][:12]}…")

    files = run_reanalysis_t4.remote(local_manifest=local_manifest)

    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-reanalysis"
    dest = Path(out_root) / stamp if out_root else INCOMING_ROOT / stamp
    mc.unpack_files(files, str(dest))

    prov_path = dest / mc.PROVENANCE_NAME
    prov = json.loads(prov_path.read_text())
    try:
        image_id = image.object_id
    except Exception:
        image_id = None
    prov["coordinator"] = {
        "modal_client": modal.__version__,
        "image_object_id": image_id,
        "local_manifest_matched": True,  # container failed closed otherwise
        "collected_utc": mc.utcnow_iso(),
    }
    prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {len(files)} files to {dest}")
    print("next: python3 poc/e2/reanalysis/analyze.py " + str(dest))
