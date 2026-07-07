#!/usr/bin/env python3
"""E8 inputs builder — writes poc/e8/inputs/e8-manifest.json (bead kernel-of-truth-u0x).

Stdlib only for the original + ext1 manifests (--scale additionally uses
numpy + e2_runner.rankdata to measure at-scale JL distortion), offline,
deterministic (idempotent given unchanged inputs; the
`date` field is refreshed on regeneration and is the only volatile field —
compare with `diff -I '"date"'`). The manifest is THE pin: the Modal container
asserts every reused artifact and every HF revision against it, fail closed.

    python3 poc/e8/build_inputs.py          # original two-family manifest
    python3 poc/e8/build_inputs.py --ext1    # extension-1 manifest (family C
                                             # + pairs vs committed signatures)
    python3 poc/e8/build_inputs.py --scale   # extension-2 manifest (1,054-concept
                                             # gloss-based variant; needs scale/out)

All SAE-source facts below (revisions, file names, sizes, weight-key layouts)
were surveyed 2026-07-07 via the HF API + ranged safetensors-header reads and
are HARD-CODED here on purpose: regeneration must never silently re-resolve
`main` to a different revision. Survey record: poc/e8/README.md §Design-pin 1.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
E2_INPUTS = os.path.join(REPO, "poc", "e2", "inputs")
REANALYSIS_RDMS = os.path.join(
    REPO, "poc", "e2", "results-incoming", "20260707-112247-reanalysis", "rdms-reanalysis.json"
)
OUT = os.path.join(HERE, "inputs", "e8-manifest.json")
OUT_EXT1 = os.path.join(HERE, "inputs", "e8-manifest-ext1.json")
OUT_SCALE = os.path.join(HERE, "inputs", "e8-manifest-scale.json")
SCALE_OUT = os.path.join(HERE, "scale", "out")
GLOSSES = os.path.join(REPO, "poc", "e4", "inputs", "glosses.jsonl")
GLOSS_HASH_TXT = os.path.join(REPO, "poc", "e4", "GLOSS-HASH.txt")
COMMITTED_STAMP = os.path.join(HERE, "results-incoming", "20260707-131303-modal")

# Reused E2 artifacts (byte-pinned; container stages items+contexts only,
# analyze.py additionally consumes the kernel + baseline RDMs on this box).
E2_FILES = [
    "items.json",
    "contexts.json",
    "kernel-rdm.json",
    "baseline-word2vec.json",
    "baseline-wordnet.json",
    "baseline-gloss.json",
]

FAMILIES = {
    "gpt2": {
        "model_id": "openai-community/gpt2",
        "model_revision": "607a30d783dfa663caf39e06633721c8d4cfcd7e",
        "sae_repo": "jbloom/GPT2-Small-SAEs-Reformatted",
        "sae_revision": "57d08a4fd333fbf18caf3fbea63ceeb88e2f50d9",
        "sae_file": "blocks.6.hook_resid_pre/sae_weights.safetensors",
        "sae_cfg_file": "blocks.6.hook_resid_pre/cfg.json",
        "sae_file_bytes": 151096640,
        "sae_arch": "sae_lens_standard",  # encode = relu((x - b_dec) @ W_enc + b_enc)
        "sae_keys": {"W_enc": [768, 24576], "b_enc": [24576], "W_dec": [24576, 768], "b_dec": [768]},
        "d_in": 768,
        "d_sae": 24576,
        "topk": None,
        "hookpoint": "blocks.6.hook_resid_pre",
        # HF hidden_states index for the SAME site: resid entering block 6
        # (0-based) = output of block 5 = hidden_states[6] = L/2 of 12.
        "hidden_state_index": 6,
        "n_layers_expected": 12,
        # transformer_lens center_writing_weights equivalence: TL resid equals
        # HF resid minus its per-position mean over d_model (derivation:
        # poc/e8/README.md §Design-pin 1).
        "basis": "subtract_hidden_mean",
        "prepend_bos": True,
        "fvu_gate": 0.5,
        "training": {"dataset": "Skylion007/openwebtext", "tokens": 300_000_000, "l1_coefficient": 8e-05},
        "model_bytes_approx": 548_000_000,
    },
    "pythia-160m": {
        "model_id": "EleutherAI/pythia-160m",
        "model_revision": "50f5173d932e8e61f858120bcb800b97af589f46",
        "sae_repo": "EleutherAI/sae-pythia-160m-32k",
        "sae_revision": "2046768ae0c8cb69a2e8ed64f2eafb9f8c5fa294",
        "sae_file": "layers.5/sae.safetensors",
        "sae_cfg_file": "layers.5/cfg.json",
        "sae_file_bytes": 201461072,
        "sae_arch": "eleuther_topk",  # encode = topk_k(relu((x - b_dec) @ enc.weight.T + enc.bias))
        "sae_keys": {"encoder.weight": [32768, 768], "encoder.bias": [32768], "W_dec": [32768, 768], "b_dec": [768]},
        "d_in": 768,
        "d_sae": 32768,
        "topk": 32,
        "hookpoint": "layers.5",  # module-path convention of EleutherAI/sae;
        # output of gpt_neox.layers[5] = the same between-blocks-5-and-6 site.
        "hidden_state_index": 6,
        "n_layers_expected": 12,
        "basis": "none",  # sparsify trains on raw HF module outputs
        "prepend_bos": False,
        "fvu_gate": 0.75,  # TopK k=32 is lossier by construction
        "training": {"dataset": "EleutherAI/pile", "tokens": 8_200_000_000, "k": 32},
        "model_bytes_approx": 375_000_000,
    },
}

# Extension 1 (bead kernel-of-truth-fnq; README §Extension 1): third family,
# MLP-output site (no ungated residual suites exist for a third architecture
# — survey 2026-07-07, recorded in the README).
FAMILY_C = {
    "smollm2-135m": {
        "model_id": "HuggingFaceTB/SmolLM2-135M",
        "model_revision": "93efa2f097d58c2a74874c7e644dbc9b0cee75a2",
        "sae_repo": "EleutherAI/sae-SmolLM2-135M-64x",
        "sae_revision": "57ea2cb986e2545844cdd4a5bb2eb39523243494",
        "sae_file": "layers.15.mlp/sae.safetensors",
        "sae_cfg_file": "layers.15.mlp/cfg.json",
        "sae_file_bytes": 170019400,
        "sae_arch": "eleuther_topk",
        "sae_keys": {"encoder.weight": [36864, 576], "encoder.bias": [36864],
                     "W_dec": [36864, 576], "b_dec": [576]},
        "d_in": 576,
        "d_sae": 36864,  # 64x of 576; repo cfg.json says expansion_factor 32 —
        # num_latents/d_in/k are the authoritative fields (README ext-1 note)
        "topk": 32,
        "hookpoint": "layers.15.mlp",
        "site": "mlp_output",            # named-module output via forward hook
        "module_path": "layers.15.mlp",  # AutoModel (LlamaModel) submodule path
        "block_index": 15,               # == 30 // 2, the L/2 discipline
        "n_layers_expected": 30,
        "basis": "none",                 # sparsify trains on raw HF module outputs
        "prepend_bos": False,
        "fvu_gate": 0.75,
        "training": {"dataset": "EleutherAI/fineweb-edu-dedup-10b", "k": 32},
        "model_bytes_approx": 270_000_000,
    },
}


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_ext1() -> None:
    """Extension-1 manifest: family C pins + committed-signature reuse pins +
    the two pre-registered pairs (README §Extension 1, fixed before build)."""
    with open(os.path.join(E2_INPUTS, "items.json")) as f:
        items = json.load(f)
    e2_pins = {name: sha256_file(os.path.join(E2_INPUTS, name)) for name in E2_FILES}
    reused = {}
    for fam, npz in (("gpt2", "signatures-gpt2.npz"), ("pythia-160m", "signatures-pythia-160m.npz")):
        path = os.path.join(COMMITTED_STAMP, npz)
        if not os.path.exists(path):
            raise SystemExit(f"ERR_MISSING_INPUT: committed signatures not found: {path}")
        reused[fam] = {"file": npz, "sha256": sha256_file(path)}
    manifest = {
        "experiment": "E8 extension 1: third-family replication (bead kernel-of-truth-fnq)",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "designPin": "poc/e8/README.md §Extension 1 (fixed before any ext-1 code or download)",
        "encoderContentHash": items["encoderContentHash"],
        "corpusPin": items["corpusPin"],
        "itemSource": "poc/e2/inputs/items.json — the 51 E2 analysis items, reused byte-identically",
        "itemCountAnalysis": items["itemCountAnalysis"],
        "e2InputSha256": e2_pins,
        "reanalysisRdms": {
            "path": os.path.relpath(REANALYSIS_RDMS, REPO),
            "sha256": sha256_file(REANALYSIS_RDMS),
            "use": "emb4 sentence-embedding RDMs as S1 covariates (unchanged from the original run)",
        },
        "families": {**FAMILIES, **FAMILY_C},
        "extraction_families": ["smollm2-135m"],  # runner extracts ONLY family C
        "reusedSignatures": {
            "stamp": os.path.relpath(COMMITTED_STAMP, REPO),
            "extraction_json_sha256": sha256_file(os.path.join(COMMITTED_STAMP, "e8-extraction.json")),
            "families": reused,
        },
        "pairs": [["gpt2", "smollm2-135m"], ["pythia-160m", "smollm2-135m"]],
        "replicationRule": "the extension REPLICATES iff BOTH new pairs pass P1 AND P2 "
                           "(p<0.01) with gates passed; anything weaker is reported "
                           "per-pair, verbatim, no cherry-picking",
        "signature": {
            "definition": "per-token SAE encode -> mean over word-span tokens -> mean over the 24 bank contexts; fp32",
            "siteNote": "family C dictionary lives on the MLP OUTPUT of block 15 (L/2 of 30), "
                        "named-module output per the EleutherAI sae convention — a site mismatch "
                        "vs families A/B (residual stream), named as a confound (conservative direction)",
        },
        "stats": {
            "seed": 20260707,
            "nPerm": 10000,
            "nPermRetrieval": 2000,
            "alphaPrimary": 0.01,
            "primaryKernelVariant": "jl512",
            "x4DistortionRdmSpearman": {"jl512": 0.9717634748044783, "jl576": 0.9705671745304928},
        },
        "downloadPlanBytes": {
            "models": FAMILY_C["smollm2-135m"]["model_bytes_approx"],
            "saes": FAMILY_C["smollm2-135m"]["sae_file_bytes"],
            "destination": "Modal volume kot-hf-cache (families A/B already cached; signatures reused)",
        },
    }
    with open(OUT_EXT1, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print(f"wrote {OUT_EXT1}")
    print(f"  pairs: {manifest['pairs']}")
    print(f"  reused: " + ", ".join(f"{k} {v['sha256'][:12]}…" for k, v in reused.items()))


def build_scale() -> None:
    """Extension-2 manifest (README §Extension 2, pre-registered before build):
    1,054-concept gloss-based variant. Pins the TS-built kernel RDM binaries
    (scale/out), measures the at-scale JL distortion (X4 was kernel-v0-only),
    asserts GLOSS-HASH, and pins the cov2 embedders at the revisions the
    committed E2 re-analysis resolved."""
    import sys as _sys

    import numpy as _np
    _sys.path.insert(0, os.path.join(REPO, "poc", "e2", "runner"))
    import e2_runner as _r

    with open(os.path.join(SCALE_OUT, "kernel-rdm-scale-meta.json")) as f:
        meta = json.load(f)
    n = meta["n"]
    rdms = {}
    mats = {}
    for name, pin in meta["rdms"].items():
        path = os.path.join(SCALE_OUT, pin["file"])
        got = sha256_file(path)
        if got != pin["sha256"]:
            raise SystemExit(f"ERR_MISSING_INPUT: {pin['file']} sha drifted")
        rdms[name] = {"file": os.path.join("scale", "out", pin["file"]), "sha256": got}
        mats[name] = _np.fromfile(path, dtype=_np.float32).reshape(n, n)

    # at-scale JL distortion (pre-registered re-measurement; X4 measured v0 only)
    iu = _np.triu_indices(n, k=1)
    full_od = mats["full"][iu].astype(_np.float64)
    distortion = {}
    for d in ("jl512", "jl576"):
        distortion[d] = float(_r.pearson(_r.rankdata(full_od), _r.rankdata(mats[d][iu].astype(_np.float64))))
        print(f"  at-scale RDM Spearman full vs {d}: {distortion[d]:.4f}")

    gloss_sha = sha256_file(GLOSSES)
    with open(GLOSS_HASH_TXT) as f:
        pinned = f.readline().split("=")[1].strip()
    if gloss_sha != pinned:
        raise SystemExit(f"ERR_MISSING_INPUT: glosses.jsonl sha {gloss_sha[:12]}… != GLOSS-HASH.txt {pinned[:12]}…")

    # cov2 embedders at the revisions the committed re-analysis resolved
    with open(REANALYSIS_RDMS) as f:
        rean = json.load(f)
    embedders = {}
    for name, pooling in (("minilm", "mean"), ("bge", "cls")):
        e = rean["embedders"][name]
        embedders[name] = {"hf_id": e["hf_id"], "revision": e["resolved_commit_hash"],
                           "pooling": pooling}

    manifest = {
        "experiment": "E8 extension 2: at-scale geometry, 1,054 concepts (gloss-based)",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "designPin": "poc/e8/README.md §Extension 2 (pre-registered before any ext-2 code, encode, or download)",
        "encoderContentHash": meta["encoderContentHash"],
        "glossHash": gloss_sha,
        "ids": meta["ids"],
        "n": n,
        "kernelRdmScale": {
            "metaFile": os.path.join("scale", "out", "kernel-rdm-scale-meta.json"),
            "metaSha256": sha256_file(os.path.join(SCALE_OUT, "kernel-rdm-scale-meta.json")),
            "rdms": rdms,
            "atScaleDistortionRdmSpearman": distortion,
            "x4KernelV0DistortionRdmSpearman": {"jl512": 0.9717634748044783, "jl576": 0.9705671745304928},
            "pathNote": "projected path (Common rule 3): re-encoded at D=8192 with pinned kot-enc-B/1, "
                        "jl/8192/512 + jl/8192/576 streams; the E4 Bq@512 tables are NOT used",
        },
        "families": {**FAMILIES, **FAMILY_C},
        "embedders": embedders,
        "pairs": [["gpt2", "pythia-160m"], ["gpt2", "smollm2-135m"], ["pythia-160m", "smollm2-135m"]],
        "headlineRule": "the at-scale claim holds iff the (gpt2, pythia-160m) pair — the pair that "
                        "PASSED at n=51 — passes gate + P1 + P2' at n~1054",
        "stats": {
            "seed": 20260707,
            "nPermMantel": 2000,
            "nPermGate": 10000,
            "retrieval": "descriptive only (top-1 acc vs 1/n chance; permutation null dropped — "
                         "each draw would rebuild a 1054^2 masked-profile matrix)",
            "alphaPrimary": 0.01,
            "primaryKernelVariant": "jl512",
            "holmSecondaries": ["S2p_partial_cov2_vs_S_famA", "S3p_partial_cov2_vs_S_famB"],
        },
        "downloadPlanBytes": {"models": 0, "saes": 0,
                              "destination": "all five models + three SAEs already in kot-hf-cache"},
    }
    with open(OUT_SCALE, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print(f"wrote {OUT_SCALE} (n={n}, pairs={len(manifest['pairs'])})")


def main() -> None:
    with open(os.path.join(E2_INPUTS, "items.json")) as f:
        items = json.load(f)
    e2_pins = {name: sha256_file(os.path.join(E2_INPUTS, name)) for name in E2_FILES}
    if not os.path.exists(REANALYSIS_RDMS):
        raise SystemExit(f"ERR_MISSING_INPUT: committed re-analysis RDMs not found: {REANALYSIS_RDMS}")

    manifest = {
        "experiment": "E8 kernel<->SAE alignment (docs/poc-design.md E8; bead kernel-of-truth-u0x)",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "designPin": "poc/e8/README.md (fixed before build; amendments would be listed there)",
        "encoderContentHash": items["encoderContentHash"],
        "corpusPin": items["corpusPin"],
        "itemSource": "poc/e2/inputs/items.json — the 51 E2 analysis items, reused byte-identically",
        "itemCountAnalysis": items["itemCountAnalysis"],
        "moleculeTier": {
            "included": False,
            "reason": "molecules-v0 records have no explications, hence no derived kernel vectors; "
                      "molecule-vector derivation is a pinned encoder version change "
                      "(docs/design-molecule-tier.md) => new pre-registration. Follow-up bead filed.",
            "moleculeCount": 54,
        },
        "e2InputSha256": e2_pins,
        "reanalysisRdms": {
            "path": os.path.relpath(REANALYSIS_RDMS, REPO),
            "sha256": sha256_file(REANALYSIS_RDMS),
            "use": "emb4 sentence-embedding RDMs as S1 covariates (committed extraction reused; no new GPU work)",
        },
        "families": FAMILIES,
        "signature": {
            "definition": "per-token SAE encode -> mean over word-span tokens -> mean over the 24 bank contexts; fp32",
            "rejectedAlternative": "direct feature-max (single top feature) — brittle under feature "
                                   "splitting, discards the profile, near-degenerate under TopK k=32",
            "spanRule": "E2 verbatim: tokens overlapping [charStart, charEnd), attention==1, nonzero offset width",
            "inVocabRule": "E2 verbatim: ' '+word tokenizes to 1..4 tokens, no UNK; analysed set = intersection of both families",
        },
        "stats": {
            "seed": 20260707,
            "nPerm": 10000,
            "alphaPrimary": 0.01,
            "primaryKernelVariant": "jl512",
            "x4DistortionRdmSpearman": {"jl512": 0.9717634748044783, "jl576": 0.9705671745304928},
            "nullsNote": "shuffled-kernel == Mantel concept-label permutation at the RDM level (P K P^T); "
                         "one permutation scheme implements both pre-registered nulls",
        },
        "downloadPlanBytes": {
            "models": sum(f["model_bytes_approx"] for f in FAMILIES.values()),
            "saes": sum(f["sae_file_bytes"] for f in FAMILIES.values()),
            "destination": "Modal volume kot-hf-cache (NOT the CPU box)",
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print(f"wrote {OUT}")
    print(f"  encoder {manifest['encoderContentHash'][:16]}…  items {manifest['itemCountAnalysis']}")
    print(f"  downloads: {(manifest['downloadPlanBytes']['models'] + manifest['downloadPlanBytes']['saes']) / 1e9:.2f} GB (volume)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ext1", action="store_true",
                    help="write the extension-1 manifest instead of the original")
    ap.add_argument("--scale", action="store_true",
                    help="write the extension-2 (1,054-concept) manifest")
    _args = ap.parse_args()
    if _args.ext1:
        build_ext1()
    elif _args.scale:
        build_scale()
    else:
        main()
