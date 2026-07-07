#!/usr/bin/env python3
"""E8 extension-2 extraction runner — gloss-based SAE signatures for the
1,054-concept E4 vocabulary, three families (pre-registration:
poc/e8/README.md §Extension 2, fixed before this file was written).

The ONLY thing the GPU container runs for ext-2. NO statistics here; ships
within-family concept RDMs + gloss-embedding covariate RDMs + diagnostics.
Raw signatures are NOT retained at scale (1054 x d_sae x 3 families ~= 300 MB;
pre-registered: the shipped RDMs are the analysis inputs, and signatures are
reproducible from the pinned revisions + GLOSS-HASH).

    python3 e8_scale_runner.py --manifest .../e8-manifest-scale.json \
        --glosses .../glosses.jsonl --out-dir OUT [--device cuda]
    python3 e8_scale_runner.py ... --mock [--limit 80]   # numpy-only smoke

Signature (estimator change 1, pre-registered): per-token SAE encode -> mean
over ALL real tokens of the gloss -> mean over the concept's 5 glosses. This
reuses e8_runner's span machinery verbatim with span = the whole gloss text:
the span rule (offset overlap, attention==1, nonzero width) then covers every
real token and excludes padding + the prepended BOS (gpt2) automatically.

Covariates (estimator change 2): gloss-TEXT embeddings via the two committed
E2-reanalysis embedders; `_embed` mirrors poc/modal/modal_e2_reanalysis.py's
_embed (pooling per model card, L2-normalised) — copied with attribution
because that module imports `modal` at top level and is not importable here.

Fail-closed codes: ERR_MANIFEST_PIN, ERR_GLOSS_PIN, ERR_GLOSS_COVERAGE,
ERR_SAE_*, ERR_LIMIT, plus everything e8_runner raises.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e8_runner as e8r  # noqa: E402  (SAEFamilyExtractor / MockSAEFamily / sha256_file)

for cand in (HERE, os.path.abspath(os.path.join(HERE, "..", "..", "e2", "runner"))):
    if os.path.exists(os.path.join(cand, "e2_runner.py")):
        sys.path.insert(0, cand)
        break
import e2_runner as r  # noqa: E402  (cosine_sim_matrix)


def _embed(texts: list, hf_id: str, revision: str, pooling: str, device: str) -> tuple:
    """Sentence embeddings via plain transformers — mirrors
    modal_e2_reanalysis._embed (mean: attention-masked mean; cls: [:,0];
    L2-normalised). Returns (matrix, resolved_commit)."""
    import torch
    from transformers import AutoModel, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(hf_id, revision=revision)
    model = AutoModel.from_pretrained(hf_id, revision=revision).to(device).eval()
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
    commit = getattr(model.config, "_commit_hash", None)
    del model
    return np.vstack(out), commit


class MockEmbedder:
    """Deterministic numpy stand-in for the mock path."""

    @staticmethod
    def embed(texts: list, name: str) -> np.ndarray:
        out = np.zeros((len(texts), 48), dtype=np.float64)
        for i, t in enumerate(texts):
            seed = int.from_bytes(hashlib.sha256(f"{name}/{t}".encode()).digest()[:8], "big") % (2 ** 32)
            v = np.random.default_rng(seed).standard_normal(48)
            out[i] = v / np.linalg.norm(v)
        return out


def load_glosses(path: str, pinned_sha: str) -> dict:
    got = e8r.sha256_file(path)
    if got != pinned_sha:
        raise SystemExit(f"ERR_GLOSS_PIN: glosses.jsonl sha {got[:12]}… != pinned {pinned_sha[:12]}…")
    by_id: dict = {}
    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            by_id.setdefault(rec["conceptId"], []).append((rec["variant"], rec["gloss"]))
    for cid, gl in by_id.items():
        gl.sort()  # variant order — deterministic
        if len(gl) != 5:
            raise SystemExit(f"ERR_GLOSS_COVERAGE: {cid} has {len(gl)} glosses (want 5)")
    return {cid: [g for _, g in gl] for cid, gl in by_id.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description="E8 ext-2 gloss-signature extraction")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--glosses", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="MOCK ONLY: cap concept count for the smoke test")
    args = ap.parse_args()
    if args.limit and not args.mock:
        raise SystemExit("ERR_LIMIT: --limit is a mock-only convenience; the "
                         "pre-registered run uses the full 1,054")

    with open(args.manifest) as f:
        man = json.load(f)
    ids = man["ids"]
    glosses = load_glosses(args.glosses, man["glossHash"])
    missing = [i for i in ids if i not in glosses]
    if missing:
        raise SystemExit(f"ERR_GLOSS_COVERAGE: {len(missing)} ids without glosses, e.g. {missing[:3]}")
    if args.limit:
        ids = ids[: args.limit]

    texts = []  # 5 per concept, concept-major order
    for cid in ids:
        texts.extend(glosses[cid])
    n, k_gloss = len(ids), 5

    out = {
        "experiment": man["experiment"],
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "mock": bool(args.mock),
        "limit": args.limit or None,
        "encoderContentHash": man["encoderContentHash"],
        "glossHash": man["glossHash"],
        "manifest_sha256": e8r.sha256_file(args.manifest),
        "n_concepts": n,
        "ids_sha256": hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
        "families": {},
        "embedders": {},
    }
    os.makedirs(args.out_dir, exist_ok=True)

    # ---- SAE families: gloss-signature RDMs ----
    for name, spec in man["families"].items():
        print(f"=== family {name} ({'MOCK' if args.mock else spec['model_id']}) ===", flush=True)
        ext = e8r.MockSAEFamily(name, spec) if args.mock else e8r.SAEFamilyExtractor(
            name, spec, args.device, args.batch_size)
        jobs = [(t, 0, len(t)) for t in texts]  # span = whole gloss (docstring)
        mat, diags = ext.word_feature_signatures(jobs)
        sigs = mat.reshape(n, k_gloss, -1).mean(axis=1)  # mean over 5 glosses
        zero_ids = [ids[i] for i in range(n) if not np.any(sigs[i] > 0)]
        if not args.mock and diags["fvu"] > spec["fvu_gate"]:
            raise SystemExit(f"ERR_SAE_BASIS: {name} FVU {diags['fvu']:.3f} > gate {spec['fvu_gate']}")
        if len(zero_ids) > 0.10 * n:
            raise SystemExit(f"ERR_DEAD_SIGNATURES: {name}: {len(zero_ids)}/{n} all-zero")
        S = r.cosine_sim_matrix(np.asarray(sigs, dtype=np.float64)).astype(np.float32)
        npz = os.path.join(args.out_dir, f"rdm-{name}-scale.npz")
        np.savez_compressed(npz, similarity=S, ids=np.array(ids))
        out["families"][name] = {
            "spec_pins": {k: spec[k] for k in (
                "model_id", "model_revision", "sae_repo", "sae_revision", "sae_file",
                "sae_arch", "d_in", "d_sae", "topk", "hookpoint", "hidden_state_index",
                "site", "module_path", "block_index", "basis", "prepend_bos") if k in spec},
            "resolved": ext.resolved,
            "zero_signature_ids": zero_ids,
            "diagnostics": diags,
            "rdm_file": os.path.basename(npz),
            "rdm_sha256": e8r.sha256_file(npz),
            "signature_density_mean": float((sigs > 0).mean(axis=1).mean()),
            "signatures_retained": False,
        }
        print(f"  {name}: RDM {S.shape}, FVU {diags['fvu']:.4f}, mean L0 {diags['mean_l0']:.1f}, "
              f"zero-sigs {len(zero_ids)}", flush=True)
        del ext, mat, sigs

    # ---- gloss-embedding covariates (cov2) ----
    for emb_name, spec in man["embedders"].items():
        print(f"=== embedder {emb_name} ({spec['hf_id']}, {spec['pooling']}-pool) ===", flush=True)
        if args.mock:
            reps, commit = MockEmbedder.embed(texts, emb_name), "mock"
        else:
            reps, commit = _embed(texts, spec["hf_id"], spec["revision"], spec["pooling"], args.device)
        per_concept = reps.reshape(n, k_gloss, -1).mean(axis=1)
        per_concept /= np.maximum(np.linalg.norm(per_concept, axis=1, keepdims=True), 1e-12)
        C = r.cosine_sim_matrix(np.asarray(per_concept, dtype=np.float64)).astype(np.float32)
        npz = os.path.join(args.out_dir, f"rdm-cov-{emb_name}-scale.npz")
        np.savez_compressed(npz, similarity=C, ids=np.array(ids))
        out["embedders"][emb_name] = {
            "hf_id": spec["hf_id"], "revision": spec["revision"],
            "pooling": spec["pooling"] + "+l2norm(gloss)->mean(5)->l2norm",
            "resolved_commit_hash": commit,
            "rdm_file": os.path.basename(npz),
            "rdm_sha256": e8r.sha256_file(npz),
        }
        print(f"  {emb_name}: commit {commit}", flush=True)

    meta = os.path.join(args.out_dir, "e8-scale-extraction.json")
    with open(meta, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {meta}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
