#!/usr/bin/env python3
"""E8 extraction runner — concept SAE-feature signatures for two model
families (docs/poc-design.md E8; design pin: poc/e8/README.md; bead
kernel-of-truth-u0x).

This is the ONLY thing the GPU container runs. NO statistics happen here —
signatures + diagnostics ship home; poc/e8/analyze.py does the stats on the
CPU box so they are auditable and re-runnable without spend.

    python3 e8_runner.py --e2-inputs-dir poc/e2/inputs \
        --manifest poc/e8/inputs/e8-manifest.json --out-dir OUT [--device cuda]
    python3 e8_runner.py ... --mock      # numpy-only CPU smoke (no torch/HF)

Conventions reused from E2 (imported where importable, mirrored verbatim
where the pooling order differs — see DEVIATION notes inline):
  - in-vocab rule + MAX_WORD_TOKENS: e2_runner (imported);
  - word-span token mask: same rule as e2_runner.HFExtractor.word_reps
    (tokens overlapping [cs, ce), attention==1, nonzero offset width) — but
    SAE encoding happens PER TOKEN before any pooling, because
    encode(mean(h)) != mean(encode(h)) (design pin §3), so the loop is
    mirrored here rather than reusing the span-pooled outputs;
  - layer: HF hidden_states[6] == L/2 of 12 for both families (asserted).

Fail-closed codes: ERR_MANIFEST_PIN, ERR_LAYERS, ERR_SAE_KEYS, ERR_SAE_BASIS,
ERR_DEAD_SIGNATURES, ERR_ATTRITION, ERR_SPAN.
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
# e2_runner is a sibling in-container (staged) and two hops away in-repo.
for cand in (HERE, os.path.abspath(os.path.join(HERE, "..", "..", "e2", "runner"))):
    if os.path.exists(os.path.join(cand, "e2_runner.py")):
        sys.path.insert(0, cand)
        break
import e2_runner as r  # noqa: E402  (MAX_WORD_TOKENS, cosine helpers; stats stay in analyze)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pinned_inputs(e2_inputs_dir: str, manifest_path: str) -> tuple[dict, dict, dict]:
    with open(manifest_path) as f:
        man = json.load(f)
    # Assert the staged E2 inputs the runner consumes match the manifest pins.
    for name in ("items.json", "contexts.json"):
        got = sha256_file(os.path.join(e2_inputs_dir, name))
        want = man["e2InputSha256"][name]
        if got != want:
            raise SystemExit(f"ERR_MANIFEST_PIN: {name} sha {got[:12]}… != pinned {want[:12]}…")
    with open(os.path.join(e2_inputs_dir, "items.json")) as f:
        items = json.load(f)
    with open(os.path.join(e2_inputs_dir, "contexts.json")) as f:
        contexts = json.load(f)
    if items["encoderContentHash"] != man["encoderContentHash"]:
        raise SystemExit("ERR_MANIFEST_PIN: encoderContentHash drift between items.json and manifest")
    return man, items, contexts


# ---------------------------------------------------------------------------
# SAE loading + encoding (direct safetensors slicing; design pin §1)
# ---------------------------------------------------------------------------


class SAEDict:
    """One family's dictionary. Two pinned architectures, verified key layouts."""

    def __init__(self, spec: dict, weights: dict, torch_mod):
        self.spec = spec
        self.torch = torch_mod
        want = spec["sae_keys"]
        missing = [k for k in want if k not in weights]
        if missing:
            raise SystemExit(f"ERR_SAE_KEYS: missing {missing}; file has {sorted(weights)}")
        for k, shape in want.items():
            if list(weights[k].shape) != shape:
                raise SystemExit(f"ERR_SAE_KEYS: {k} shape {list(weights[k].shape)} != pinned {shape}")
        self.w = {k: v.float() for k, v in weights.items()}
        self.arch = spec["sae_arch"]
        self.d_sae = spec["d_sae"]

    def encode(self, x):
        """x: (n, d_in) fp32 torch tensor -> (n, d_sae) feature activations."""
        t = self.torch
        if self.arch == "sae_lens_standard":
            # mats_sae_training standard arch: relu((x - b_dec) @ W_enc + b_enc)
            pre = (x - self.w["b_dec"]) @ self.w["W_enc"] + self.w["b_enc"]
            return t.relu(pre)
        if self.arch == "eleuther_topk":
            # EleutherAI sae/sparsify: relu((x - b_dec) @ enc.weight.T + enc.bias), keep top-k
            pre = t.relu((x - self.w["b_dec"]) @ self.w["encoder.weight"].T + self.w["encoder.bias"])
            k = int(self.spec["topk"])
            vals, idx = pre.topk(k, dim=-1)
            out = t.zeros_like(pre)
            out.scatter_(-1, idx, vals)
            return out
        raise SystemExit(f"ERR_SAE_KEYS: unknown arch {self.arch!r}")

    def decode(self, acts):
        return acts @ self.w["W_dec"] + self.w["b_dec"]


class SAEFamilyExtractor:
    """Base model + SAE for one family; per-token feature acts over word spans."""

    def __init__(self, name: str, spec: dict, device: str, batch_size: int):
        import torch
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        from transformers import AutoModel, AutoTokenizer

        self.name, self.spec, self.device, self.batch_size = name, spec, device, batch_size
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(
            spec["model_id"], revision=spec["model_revision"], use_fast=True)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        # fp32 on purpose (models are small; SAE dictionaries are fp32 — no
        # reason to inject fp16 activation noise into the signatures).
        self.model = AutoModel.from_pretrained(
            spec["model_id"], revision=spec["model_revision"], torch_dtype=torch.float32
        ).to(device).eval()
        n_layers = self.model.config.num_hidden_layers
        self.site = spec.get("site", "hidden_state")
        if self.site == "hidden_state":
            if n_layers != spec["n_layers_expected"] or spec["hidden_state_index"] != n_layers // 2:
                raise SystemExit(
                    f"ERR_LAYERS: {name} has {n_layers} layers; pinned hidden_state_index "
                    f"{spec['hidden_state_index']} must equal L//2 of {spec['n_layers_expected']}")
            self.hs_index = spec["hidden_state_index"]
        elif self.site == "mlp_output":
            # extension 1 (README §Extension 1): EleutherAI MLP-output SAEs;
            # hookpoint = named-module output, block_index pinned to L//2
            if n_layers != spec["n_layers_expected"] or spec["block_index"] != n_layers // 2:
                raise SystemExit(
                    f"ERR_LAYERS: {name} has {n_layers} layers; pinned block_index "
                    f"{spec['block_index']} must equal L//2 of {spec['n_layers_expected']}")
            try:
                self.hook_module = self.model.get_submodule(spec["module_path"])
            except AttributeError as e:
                raise SystemExit(f"ERR_LAYERS: {name}: module {spec['module_path']!r} not found: {e}")
        else:
            raise SystemExit(f"ERR_LAYERS: unknown site {self.site!r}")
        sae_path = hf_hub_download(
            spec["sae_repo"], spec["sae_file"], revision=spec["sae_revision"])
        self.sae = SAEDict(spec, load_file(sae_path), torch)
        for t in self.sae.w.values():
            t.data = t.data.to(device)
        self.resolved = {
            "model_commit": getattr(self.model.config, "_commit_hash", None),
            "sae_path": sae_path,
            "sae_sha256": sha256_file(sae_path),
        }
        # BOS handling (design pin §1): prepend the token STRING so char
        # offsets stay consistent; word spans are shifted by the caller.
        self.bos_prefix = self.tok.bos_token if spec["prepend_bos"] else ""

    def in_vocab(self, word: str) -> bool:
        # E2 rule verbatim (e2_runner.HFExtractor.in_vocab), same constant.
        ids = self.tok(" " + word, add_special_tokens=False)["input_ids"]
        unk = self.tok.unk_token_id
        return 1 <= len(ids) <= r.MAX_WORD_TOKENS and (unk is None or unk not in ids)

    def _hidden(self, enc: dict):
        torch = self.torch
        if self.site == "mlp_output":
            cap = {}

            def hook(_mod, _args, output):
                cap["h"] = output[0] if isinstance(output, tuple) else output

            handle = self.hook_module.register_forward_hook(hook)
            try:
                with torch.no_grad():
                    self.model(**enc)
            finally:
                handle.remove()
            if "h" not in cap:
                raise SystemExit("ERR_LAYERS: forward hook never fired")
            h = cap["h"]
        else:
            with torch.no_grad():
                hs = self.model(**enc, output_hidden_states=True).hidden_states
            h = hs[self.hs_index]
        if self.spec["basis"] == "subtract_hidden_mean":
            # transformer_lens center_writing_weights equivalence (README §1).
            h = h - h.mean(dim=-1, keepdim=True)
        elif self.spec["basis"] != "none":
            raise SystemExit(f"ERR_SAE_BASIS: unknown basis {self.spec['basis']!r}")
        return h

    def word_feature_signatures(self, jobs: list) -> tuple:
        """jobs: (text, cs, ce). Returns (per-job feature matrix, diagnostics).

        Mirrors e2_runner.HFExtractor.word_reps' span rule EXACTLY, but
        SAE-encodes per token BEFORE pooling (design pin §3).
        """
        n_feat = self.sae.d_sae
        out = np.zeros((len(jobs), n_feat), dtype=np.float32)
        # FVU accumulators over ALL span tokens (dataset-level variance — a
        # per-span baseline would divide by ~0 on single-token spans).
        l0s, sse, n_tok = [], 0.0, 0
        x_sum = np.zeros(self.spec["d_in"], dtype=np.float64)
        x_sq = 0.0
        shift = len(self.bos_prefix)
        for start in range(0, len(jobs), self.batch_size):
            chunk = jobs[start:start + self.batch_size]
            enc = self.tok(
                [self.bos_prefix + t for t, _, _ in chunk],
                return_tensors="pt", padding=True,
                return_offsets_mapping=True, add_special_tokens=False)
            offsets = enc.pop("offset_mapping")
            enc = {k: v.to(self.device) for k, v in enc.items()}
            h = self._hidden(enc)
            for bi, (_, cs, ce) in enumerate(chunk):
                cs2, ce2 = cs + shift, ce + shift
                mask = [
                    ti for ti, (a, b) in enumerate(offsets[bi].tolist())
                    if enc["attention_mask"][bi, ti].item() == 1 and not (b <= cs2 or a >= ce2) and a != b
                ]
                if not mask:
                    raise SystemExit(f"ERR_SPAN: no tokens overlap word span in: {chunk[bi][0]!r}")
                x = h[bi, mask, :]                       # (span, d_in) fp32
                acts = self.sae.encode(x)                # (span, d_sae)
                out[start + bi] = acts.mean(dim=0).cpu().numpy()
                # diagnostics over exactly the tokens the signatures use
                recon = self.sae.decode(acts)
                sse += float(((x - recon) ** 2).sum())
                xf = x.double().cpu().numpy()
                x_sum += xf.sum(axis=0)
                x_sq += float((xf ** 2).sum())
                n_tok += len(mask)
                l0s += (acts > 0).sum(dim=-1).float().cpu().numpy().tolist()
        mean = x_sum / max(n_tok, 1)
        svar = x_sq - n_tok * float(mean @ mean)  # sum ||x - mean||^2
        fvu = sse / max(svar, 1e-12)
        return out, {"fvu": fvu, "mean_l0": float(np.mean(l0s)), "n_span_tokens": n_tok}


class MockSAEFamily:
    """Deterministic numpy-only pseudo-family for the token-free smoke test.

    Sparse non-negative hash-seeded signatures; word + small context jitter.
    Words longer than 10 chars are out-of-vocabulary to exercise attrition —
    the e2_runner.MockExtractor convention. Numbers are MEANINGLESS by
    construction (the planted/null CONTROLS live in poc/e8/test_e8.py).
    """

    def __init__(self, name: str, spec: dict):
        self.name = name
        self.d_sae = 512
        self.resolved = {"mock": True}

    def in_vocab(self, word: str) -> bool:
        return len(word) <= 10

    def _sparse(self, seed_str: str) -> np.ndarray:
        seed = int.from_bytes(hashlib.sha256(seed_str.encode()).digest()[:8], "big") % (2 ** 32)
        rng = np.random.default_rng(seed)
        v = np.zeros(self.d_sae, dtype=np.float32)
        idx = rng.choice(self.d_sae, size=24, replace=False)
        v[idx] = rng.random(24).astype(np.float32)
        return v

    def word_feature_signatures(self, jobs: list) -> tuple:
        out = np.zeros((len(jobs), self.d_sae), dtype=np.float32)
        for i, (text, cs, ce) in enumerate(jobs):
            word = text[cs:ce]
            out[i] = self._sparse(f"{self.name}/word/{word}") + 0.2 * self._sparse(f"{self.name}/ctx/{text}")
        return out, {"fvu": 0.0, "mean_l0": 24.0, "n_span_tokens": len(jobs)}


# ---------------------------------------------------------------------------


def jobs_for_items(items: list, contexts: dict) -> list:
    """(text, cs, ce) jobs per item, bank order — e2_runner.pooled_reps_for_words'
    instantiation rule verbatim. Returns [(item, [jobs...]), ...]."""
    banks = contexts["banks"]
    out = []
    for it in items:
        jl = []
        for t in banks[it["bank"]]:
            at = t.index("{w}")
            w = it["word"]
            jl.append((t[:at] + w + t[at + 3:], at, at + len(w)))
        out.append((it, jl))
    return out


def run(args) -> dict:
    man, items_doc, contexts = load_pinned_inputs(args.e2_inputs_dir, args.manifest)
    items = items_doc["items"]

    extract_names = man.get("extraction_families") or list(man["families"])
    families = {}
    for name in extract_names:
        spec = man["families"][name]
        print(f"=== family {name} ({'MOCK' if args.mock else spec['model_id']}) ===", flush=True)
        ext = MockSAEFamily(name, spec) if args.mock else SAEFamilyExtractor(
            name, spec, args.device, args.batch_size)
        in_vocab = {it["id"]: ext.in_vocab(it["word"]) for it in items}
        families[name] = {"ext": ext, "in_vocab": in_vocab, "spec": spec}
        dropped = [it["word"] for it in items if not in_vocab[it["id"]]]
        print(f"  in-vocab {len(items) - len(dropped)}/{len(items)} (dropped: {dropped or 'none'})", flush=True)

    # Pre-registered analysed set: intersection of the families' survivors.
    surviving = [it for it in items if all(f["in_vocab"][it["id"]] for f in families.values())]
    if len(surviving) < 20:
        raise SystemExit(f"ERR_ATTRITION: only {len(surviving)} items in-vocab in both families")

    out = {
        "experiment": man["experiment"],
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "mock": bool(args.mock),
        "encoderContentHash": man["encoderContentHash"],
        "corpusPin": man["corpusPin"],
        "manifest_sha256": sha256_file(args.manifest),
        "ids": [it["id"] for it in surviving],
        "words": [it["word"] for it in surviving],
        "families": {},
    }
    os.makedirs(args.out_dir, exist_ok=True)

    for name, fam in families.items():
        ext = fam["ext"]
        sigs, zero_ids = [], []
        item_jobs = jobs_for_items(surviving, contexts)
        all_jobs = [j for _, jl in item_jobs for j in jl]
        mat, diags = ext.word_feature_signatures(all_jobs)
        pos = 0
        for it, jl in item_jobs:
            sig = mat[pos:pos + len(jl)].mean(axis=0)  # mean over the 24 bank contexts
            pos += len(jl)
            if not np.any(sig > 0):
                zero_ids.append(it["id"])
            sigs.append(sig)
        sig_mat = np.vstack(sigs).astype(np.float32)

        if not args.mock:
            gate = fam["spec"]["fvu_gate"]
            if diags["fvu"] > gate:
                raise SystemExit(
                    f"ERR_SAE_BASIS: {name} FVU {diags['fvu']:.3f} > gate {gate} — activation-basis "
                    "convention is wrong; this must be a crash, not a quietly null result")
        if len(zero_ids) > 0.10 * len(surviving):
            raise SystemExit(f"ERR_DEAD_SIGNATURES: {name}: {len(zero_ids)}/{len(surviving)} all-zero: {zero_ids}")

        npz = os.path.join(args.out_dir, f"signatures-{name}.npz")
        np.savez_compressed(npz, signatures=sig_mat, ids=np.array(out["ids"]))
        out["families"][name] = {
            "spec_pins": {k: fam["spec"][k] for k in (
                "model_id", "model_revision", "sae_repo", "sae_revision", "sae_file",
                "sae_arch", "d_in", "d_sae", "topk", "hookpoint", "hidden_state_index",
                "site", "module_path", "block_index", "basis", "prepend_bos")
                if k in fam["spec"]},
            "resolved": ext.resolved,
            "in_vocab_dropped_words": [it["word"] for it in items if not fam["in_vocab"][it["id"]]],
            "zero_signature_ids": zero_ids,
            "diagnostics": diags,
            "signature_file": os.path.basename(npz),
            "signature_sha256": sha256_file(npz),
            "signature_density_mean": float((sig_mat > 0).mean(axis=1).mean()),
        }
        print(f"  {name}: signatures {sig_mat.shape}, FVU {diags['fvu']:.4f}, "
              f"mean L0 {diags['mean_l0']:.1f}, zero-sigs {len(zero_ids)}", flush=True)

    meta = os.path.join(args.out_dir, "e8-extraction.json")
    with open(meta, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {meta}", flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="E8 SAE-signature extraction")
    ap.add_argument("--e2-inputs-dir", default=os.path.join(HERE, "..", "..", "e2", "inputs"))
    ap.add_argument("--manifest", default=os.path.join(HERE, "..", "inputs", "e8-manifest.json"))
    ap.add_argument("--out-dir", default=os.path.join(HERE, "..", "results"))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--mock", action="store_true", help="numpy-only deterministic pseudo-SAEs (CPU)")
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    sys.exit(main())
