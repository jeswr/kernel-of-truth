#!/usr/bin/env python3
"""E2 — geometry-alignment probe runner (docs/poc-design.md, Phase E, E2).

Pre-registered protocol (poc-design.md rev 2, quoted verbatim in the emitted
verdict): explicated-concepts-only item set; layer L/2 per model; each word in
>=20 contexts, mean-pooled over word tokens; Mantel permutation over concept
labels, >=10^4 permutations; per-model in-vocabulary lists published.
PRIMARY criterion: kernel RDM adds explanatory power beyond baseline
relatedness RDMs (word2vec cosine, WordNet path, gloss word-overlap) via
partial Spearman, p<0.01, in >=2 of 3 model families; the frequency-matched
random word sets must fall below the kernel set (kernel rho > 95th percentile
of k=100 random sets) or the result is reported as "generic relatedness
detected".

All kernel-side inputs are precomputed on the CPU box by the TS harness
(poc/e2/inputs/*.json, stamped with encoder content-hash + corpus pin).
This file is the ONLY thing the GPU box runs:

    python3 e2_runner.py                  # full pre-registered run (3 models)
    python3 e2_runner.py --mock           # CPU smoke test, numpy only

Operationalisation choices NOT fixed by the pre-registration are flagged
here and in poc/e2/README.md (search DEVIATION / OPERATIONALISATION).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys

import numpy as np

# ---------------------------------------------------------------------------
# Constants (pre-registered or published operationalisations)
# ---------------------------------------------------------------------------

DEFAULT_MODELS = [
    "roneneldan/TinyStories-33M",
    "HuggingFaceTB/SmolLM2-135M",
    "Qwen/Qwen2.5-0.5B",
]
N_PERM = 10_000          # pre-registered: >=10^4 Mantel permutations
K_SETS = 100             # pre-registered: k=100 frequency-matched random sets
ALPHA_PARTIAL = 0.01     # pre-registered: partial Spearman p<0.01
RANDOM_PCTL = 95         # pre-registered: kernel rho > 95th pctl of random sets
SEED = 20260707          # published: fixed seed for permutations + random sets
MAX_WORD_TOKENS = 4      # OPERATIONALISATION: in-vocab = " word" -> <=4 tokens, no UNK
PRIMARY_KERNEL = "jl512" # OPERATIONALISATION (flagged): pre-registration fixes the
                         # projected path (Common rule 3) with pairs (8192->512, 8192->576)
                         # but does not name which is E2-primary; jl512 declared primary,
                         # jl576 + full-D reported as sensitivity.

CRITERION_VERBATIM = (
    "kernel RDM adds explanatory power beyond baseline relatedness RDMs (word2vec "
    "cosine, WordNet path, gloss word-overlap) via partial Spearman, p<0.01, in >=2 "
    "of 3 model families; the frequency-matched random word sets must fall below the "
    "kernel set (kernel rho > 95th percentile of k=100 random sets) or the result is "
    "reported as 'generic relatedness detected'"
)

# ---------------------------------------------------------------------------
# Stats (numpy only; ties -> average ranks, matching the TS harness)
# ---------------------------------------------------------------------------


def rankdata(x: np.ndarray) -> np.ndarray:
    """Average ranks for ties (mid-rank), 1-based — mirrors poc TS spearman.

    Vectorised (scipy-style): sort once, average ranks within tie groups.
    """
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    order = np.argsort(x, kind="mergesort")
    inv = np.empty(n, dtype=np.intp)
    inv[order] = np.arange(n)
    sx = x[order]
    boundaries = np.flatnonzero(np.r_[True, sx[1:] != sx[:-1], True])
    # tie group [b0, b1): average 1-based rank = (b0 + b1 - 1) / 2 + 1
    avg = (boundaries[:-1] + boundaries[1:] - 1) / 2.0 + 1.0
    return np.repeat(avg, np.diff(boundaries))[inv]


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return pearson(rankdata(a), rankdata(b))


def offdiag(m: np.ndarray) -> np.ndarray:
    iu = np.triu_indices(m.shape[0], k=1)
    return m[iu]


class PartialSpearman:
    """Partial Spearman of (kernel, model) controlling for baseline RDMs.

    Rank-transform all off-diagonal vectors; residualise the kernel and model
    rank vectors on [1, rank(B1), rank(B2), rank(B3)] by OLS (QR); partial
    coefficient = Pearson of the residuals.
    """

    def __init__(self, baselines: list[np.ndarray]):
        X = np.column_stack([np.ones(len(baselines[0]))] + [rankdata(b) for b in baselines])
        self.q, _ = np.linalg.qr(X)

    def resid(self, v: np.ndarray) -> np.ndarray:
        r = rankdata(v)
        return r - self.q @ (self.q.T @ r)

    def partial(self, kernel_od: np.ndarray, model_od: np.ndarray) -> float:
        return pearson(self.resid(kernel_od), self.resid(model_od))


def mantel_perm_p(
    kernel_sim: np.ndarray,
    stat_fn,
    n_perm: int,
    rng: np.random.Generator,
) -> tuple[float, float, np.ndarray]:
    """One-sided Mantel-style permutation test over concept labels.

    stat_fn(kernel_offdiag_vector) -> statistic. The null permutes the item
    labels of the KERNEL similarity matrix (simultaneous row/col permutation)
    while the model/baseline matrices stay fixed — 'Mantel permutation over
    concept labels' per the pre-registration.
    p = (1 + #{perm >= observed}) / (1 + n_perm).
    """
    n = kernel_sim.shape[0]
    obs = stat_fn(offdiag(kernel_sim))
    null = np.empty(n_perm, dtype=np.float64)
    for t in range(n_perm):
        p = rng.permutation(n)
        null[t] = stat_fn(offdiag(kernel_sim[np.ix_(p, p)]))
    pval = (1.0 + float((null >= obs).sum())) / (1.0 + n_perm)
    return obs, pval, null


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------


def load_inputs(inputs_dir: str) -> dict:
    def rd(name):
        with open(os.path.join(inputs_dir, name)) as f:
            return json.load(f)

    inp = {
        "items": rd("items.json"),
        "kernel": rd("kernel-rdm.json"),
        "gloss": rd("baseline-gloss.json"),
        "wordnet": rd("baseline-wordnet.json"),
        "word2vec": rd("baseline-word2vec.json"),
        "contexts": rd("contexts.json"),
        "pools": rd("freq-matched-pools.json"),
    }
    # Fail closed on pin mismatches between input artefacts.
    pins = {k: (v.get("encoderContentHash"), json.dumps(v.get("corpusPin"), sort_keys=True))
            for k, v in inp.items()}
    if len(set(pins.values())) != 1:
        raise SystemExit(f"ERR_PIN_MISMATCH: input artefacts disagree on encoder/corpus pins: {pins}")
    ids = inp["items"]
    analysis_ids = [it["id"] for it in ids["items"]]
    for key in ("gloss", "wordnet", "word2vec"):
        if inp[key]["ids"] != analysis_ids:
            raise SystemExit(f"ERR_ITEM_ORDER: {key} ids differ from items.json")
    if inp["kernel"]["analysisIds"] != analysis_ids:
        raise SystemExit("ERR_ITEM_ORDER: kernel-rdm analysisIds differ from items.json")
    return inp


def kernel_matrices(inp: dict) -> dict[str, np.ndarray]:
    """Kernel similarity matrices restricted to the 51 analysis items."""
    k = inp["kernel"]
    all_ids = k["ids"]
    idx = [all_ids.index(i) for i in k["analysisIds"]]
    out = {"full": np.asarray(k["full"]["similarity"], dtype=np.float64)[np.ix_(idx, idx)]}
    for name, proj in k["projections"].items():
        out[name] = np.asarray(proj["similarity"], dtype=np.float64)[np.ix_(idx, idx)]
    return out


# ---------------------------------------------------------------------------
# Representation extraction
# ---------------------------------------------------------------------------


class HFExtractor:
    """Mean-pooled word representations from a HuggingFace causal LM."""

    def __init__(self, model_id: str, device: str, batch_size: int):
        import torch  # lazy: --mock must run without torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        dtype = torch.float16 if device == "cuda" else torch.float32
        self.model = AutoModel.from_pretrained(model_id, torch_dtype=dtype).to(device).eval()
        self.device = device
        self.batch_size = batch_size
        self.n_layers = self.model.config.num_hidden_layers
        self.mid_layer = self.n_layers // 2  # pre-registered: layer L/2

    def in_vocab(self, word: str) -> bool:
        ids = self.tok(" " + word, add_special_tokens=False)["input_ids"]
        unk = self.tok.unk_token_id
        return 1 <= len(ids) <= MAX_WORD_TOKENS and (unk is None or unk not in ids)

    def word_reps(self, jobs: list[tuple[str, int, int]]) -> dict[int, np.ndarray]:
        """jobs: (text, charStart, charEnd). Returns {layer: (len(jobs), H)}.

        Mean-pools hidden states over the tokens overlapping the word span,
        at the embedding layer (hidden_states[0]) and layer L/2.
        """
        torch = self.torch
        layers = [0, self.mid_layer]
        outs = {l: np.zeros((len(jobs), self.model.config.hidden_size), dtype=np.float64) for l in layers}
        for start in range(0, len(jobs), self.batch_size):
            chunk = jobs[start : start + self.batch_size]
            enc = self.tok(
                [t for t, _, _ in chunk],
                return_tensors="pt",
                padding=True,
                return_offsets_mapping=True,
                add_special_tokens=False,
            )
            offsets = enc.pop("offset_mapping")
            enc = {k: v.to(self.device) for k, v in enc.items()}
            with torch.no_grad():
                hs = self.model(**enc, output_hidden_states=True).hidden_states
            for bi, (_, cs, ce) in enumerate(chunk):
                mask = [
                    ti
                    for ti, (a, b) in enumerate(offsets[bi].tolist())
                    if enc["attention_mask"][bi, ti].item() == 1 and not (b <= cs or a >= ce) and a != b
                ]
                if not mask:
                    raise SystemExit(f"ERR_SPAN: no tokens overlap word span in: {chunk[bi][0]!r}")
                for l in layers:
                    outs[l][start + bi] = hs[l][bi, mask, :].float().mean(dim=0).cpu().numpy()
        return outs


class MockExtractor:
    """Deterministic pseudo-model for the CPU smoke test (numpy only).

    Word representation = hash-seeded gaussian per (family, word) + small
    hash-seeded per-context jitter; 8 'layers'. Words longer than 10 chars
    are declared out-of-vocabulary to exercise the attrition path.
    """

    def __init__(self, model_id: str):
        self.model_id = model_id
        self.mid_layer = 4
        self.hidden = 64

    def in_vocab(self, word: str) -> bool:
        return len(word) <= 10

    def _vec(self, seed_str: str) -> np.ndarray:
        seed = int.from_bytes(hashlib.sha256(seed_str.encode()).digest()[:8], "big") % (2**32)
        return np.random.default_rng(seed).standard_normal(self.hidden)

    def word_reps(self, jobs: list[tuple[str, int, int]]) -> dict[int, np.ndarray]:
        outs = {0: np.zeros((len(jobs), self.hidden)), self.mid_layer: np.zeros((len(jobs), self.hidden))}
        for i, (text, cs, ce) in enumerate(jobs):
            word = text[cs:ce]
            base = self._vec(f"{self.model_id}/word/{word}")
            jitter = self._vec(f"{self.model_id}/ctx/{text}")
            outs[0][i] = base + 0.05 * jitter
            outs[self.mid_layer][i] = base + 0.3 * jitter
        return outs


def cosine_sim_matrix(reps: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(reps, axis=1, keepdims=True)
    unit = reps / np.maximum(norms, 1e-12)
    m = unit @ unit.T
    np.fill_diagonal(m, 1.0)
    return m


# ---------------------------------------------------------------------------
# Per-model E2
# ---------------------------------------------------------------------------


def pooled_reps_for_words(extractor, words_with_banks: list[tuple[str, str]], contexts: dict) -> dict[int, np.ndarray]:
    """Mean-pooled rep per (word, bank): all bank templates instantiated with the word."""
    banks = contexts["banks"]
    jobs: list[tuple[str, int, int]] = []
    spans: list[tuple[int, int]] = []  # (word_index, n_contexts) implicit by order
    for w, bank in words_with_banks:
        for t in banks[bank]:
            at = t.index("{w}")
            jobs.append((t[:at] + w + t[at + 3 :], at, at + len(w)))
    per_layer = extractor.word_reps(jobs)
    n_ctx = {bank: len(ts) for bank, ts in banks.items()}
    out: dict[int, np.ndarray] = {}
    for layer, mat in per_layer.items():
        pooled = []
        pos = 0
        for w, bank in words_with_banks:
            k = n_ctx[bank]
            pooled.append(mat[pos : pos + k].mean(axis=0))
            pos += k
        out[layer] = np.vstack(pooled)
    return out


def run_model(model_id: str, inp: dict, kernels: dict[str, np.ndarray], args, mock: bool) -> dict:
    items = inp["items"]["items"]
    contexts = inp["contexts"]
    pools = inp["pools"]["pools"]
    print(f"\n=== {model_id} ===", flush=True)
    extractor = MockExtractor(model_id) if mock else HFExtractor(model_id, args.device, args.batch_size)

    # ---- per-model in-vocabulary check (published) ----
    in_vocab_mask = [extractor.in_vocab(it["word"]) for it in items]
    surviving = [it for it, ok in zip(items, in_vocab_mask) if ok]
    dropped = [it["word"] for it, ok in zip(items, in_vocab_mask) if not ok]
    sel = [i for i, ok in enumerate(in_vocab_mask) if ok]
    n = len(sel)
    print(f"in-vocab: {n}/{len(items)} (dropped: {dropped or 'none'})", flush=True)
    if n < 20:
        raise SystemExit(f"ERR_ATTRITION: only {n} items in-vocab for {model_id}")

    def restrict(m: np.ndarray) -> np.ndarray:
        return m[np.ix_(sel, sel)]

    kernel_prim = restrict(kernels[PRIMARY_KERNEL])
    baselines_od = [
        offdiag(restrict(np.asarray(inp[k]["similarity"], dtype=np.float64)))
        for k in ("word2vec", "wordnet", "gloss")
    ]

    # ---- representations for the true label words ----
    reps = pooled_reps_for_words(extractor, [(it["word"], it["bank"]) for it in surviving], contexts)
    layers = sorted(reps.keys())
    mid = extractor.mid_layer

    rng = np.random.default_rng(SEED)
    ps = PartialSpearman(baselines_od)
    layer_results = {}
    for layer in layers:
        model_sim = cosine_sim_matrix(reps[layer])
        model_od = offdiag(model_sim)
        res = {"layer": int(layer), "role": "L/2 (primary)" if layer == mid else "embedding (secondary)"}
        for kname in kernels:
            ksub = restrict(kernels[kname])
            r_obs, p_mantel, _ = mantel_perm_p(ksub, lambda kv: spearman(kv, model_od), args.n_perm, rng)
            rp_obs, p_partial, _ = mantel_perm_p(ksub, lambda kv: ps.partial(kv, model_od), args.n_perm, rng)
            res[kname] = {
                "spearman": r_obs,
                "mantel_p": p_mantel,
                "partial_spearman": rp_obs,
                "partial_p": p_partial,
            }
        layer_results[layer] = res

    # ---- k=100 frequency-matched random word sets (primary layer) ----
    eligible = {}
    for it in surviving:
        cands = [w for w in pools[it["word"]]["candidates"] if extractor.in_vocab(w)]
        if len(cands) < 5:
            raise SystemExit(f"ERR_POOL: <5 in-vocab candidates for '{it['word']}' on {model_id}")
        eligible[it["word"]] = cands
    draws: list[list[str]] = []
    for _ in range(args.k_sets):
        used, chosen = set(), []
        for it in surviving:
            opts = [w for w in eligible[it["word"]] if w not in used]
            w = str(rng.choice(opts if opts else eligible[it["word"]]))
            used.add(w)
            chosen.append(w)
        draws.append(chosen)
    unique_jobs = sorted({(w, it["bank"]) for d in draws for w, it in zip(d, surviving)})
    print(f"random sets: {args.k_sets} sets, {len(unique_jobs)} unique (word,bank) reps", flush=True)
    rand_reps = pooled_reps_for_words(extractor, list(unique_jobs), contexts)
    rand_index = {wb: i for i, wb in enumerate(unique_jobs)}
    kernel_od_prim = offdiag(kernel_prim)
    rand_rhos = {int(l): [] for l in layers}
    for d in draws:
        rows = [rand_index[(w, it["bank"])] for w, it in zip(d, surviving)]
        for layer in layers:
            sim = cosine_sim_matrix(rand_reps[layer][rows])
            rand_rhos[int(layer)].append(spearman(kernel_od_prim, offdiag(sim)))
    rand_summary = {}
    for layer in layers:
        rhos = np.asarray(rand_rhos[int(layer)])
        kernel_rho = layer_results[layer][PRIMARY_KERNEL]["spearman"]
        rand_summary[int(layer)] = {
            "kernel_rho": kernel_rho,
            "random_pctl95": float(np.percentile(rhos, RANDOM_PCTL)),
            "random_max": float(rhos.max()),
            "random_mean": float(rhos.mean()),
            "kernel_above_pctl95": bool(kernel_rho > np.percentile(rhos, RANDOM_PCTL)),
            "rhos": [float(r) for r in rhos],
        }

    prim = layer_results[mid][PRIMARY_KERNEL]
    return {
        "model": model_id,
        "mock": mock,
        "n_layers_total": getattr(extractor, "n_layers", None),
        "mid_layer_index": int(mid),
        "hidden_states_note": "hidden_states[0] = embedding output (includes learned absolute positions for GPT-Neo-style models; pure token embedding for rotary models); hidden_states[L//2] = output of block L//2",
        "in_vocab_definition": f'tokenize " "+word, add_special_tokens=False: 1..{MAX_WORD_TOKENS} tokens, no UNK id',
        "in_vocab_surviving_words": [it["word"] for it in surviving],
        "in_vocab_dropped_words": dropped,
        "n_items_analysed": n,
        "layers": {str(k): v for k, v in layer_results.items()},
        "random_sets": rand_summary,
        "primary": {
            "kernel_variant": PRIMARY_KERNEL,
            "layer": int(mid),
            "spearman": prim["spearman"],
            "mantel_p": prim["mantel_p"],
            "partial_spearman": prim["partial_spearman"],
            "partial_p": prim["partial_p"],
            "partial_pass": prim["partial_p"] < ALPHA_PARTIAL,
            "random_set_pass": rand_summary[int(mid)]["kernel_above_pctl95"],
        },
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------


def verdict(results: list[dict], inp: dict, args, mock: bool) -> tuple[dict, str]:
    partial_passes = [r for r in results if r["primary"]["partial_pass"]]
    full_passes = [r for r in results if r["primary"]["partial_pass"] and r["primary"]["random_set_pass"]]
    if len(full_passes) >= 2:
        outcome = "PRIMARY CRITERION MET"
    elif len(partial_passes) >= 2:
        outcome = "generic relatedness detected"
    else:
        outcome = "NULL (no partial-RSA signal in >=2 families)"
    j = {
        "experiment": "E2 geometry-alignment probe (poc-design.md rev 2)",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "mock": mock,
        "criterion_verbatim": CRITERION_VERBATIM,
        "operationalisation": {
            "primary_kernel_variant": PRIMARY_KERNEL,
            "primary_layer": "L//2 (num_hidden_layers // 2), hidden_states index L//2",
            "partial_null": "permute concept labels of the kernel matrix only; baselines + model fixed; one-sided",
            "random_sets": "per family: kernel rho (Spearman of kernel RDM vs model RDM at L/2) must exceed the 95th percentile of k=100 sets where each item's label word is replaced by a frequency- and frame-class-matched random word in the same contexts",
            "verdict_rule": "PRIMARY MET iff >=2 families pass partial p<0.01 AND the random-set check; 'generic relatedness detected' iff >=2 pass partial but <2 also pass random-set; else NULL",
            "x3_conditioning": "polarity-stratified subset reporting (pre-registered interpretation condition) is deferred to the analysis write-up; see poc/results/x3-report",
        },
        "pins": {
            "encoderContentHash": inp["items"]["encoderContentHash"],
            "corpusPin": inp["items"]["corpusPin"],
        },
        "n_perm": args.n_perm,
        "k_sets": args.k_sets,
        "seed": SEED,
        "outcome": outcome,
        "families_partial_pass": [r["model"] for r in partial_passes],
        "families_full_pass": [r["model"] for r in full_passes],
        "per_model": results,
    }
    lines = [
        "# E2 — geometry-alignment probe: verdict",
        "",
        f"date: {j['date']}  |  mock: {mock}  |  seed: {SEED}  |  perms: {args.n_perm}  |  k: {args.k_sets}",
        f"encoder: `{j['pins']['encoderContentHash']}`",
        "",
        "**Pre-registered primary criterion (poc-design.md E2, verbatim):**",
        f"> {CRITERION_VERBATIM}",
        "",
        f"## OUTCOME: **{outcome}**",
        "",
        "| model | items | rho (L/2) | Mantel p | partial rho | partial p | partial<0.01 | rand 95th pctl | kernel>pctl |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        p = r["primary"]
        rs = r["random_sets"][str(r["mid_layer_index"])] if isinstance(next(iter(r["random_sets"])), str) else r["random_sets"][r["mid_layer_index"]]
        lines.append(
            f"| {r['model']} | {r['n_items_analysed']} | {p['spearman']:.4f} | {p['mantel_p']:.5f} "
            f"| {p['partial_spearman']:.4f} | {p['partial_p']:.5f} | {'PASS' if p['partial_pass'] else 'fail'} "
            f"| {rs['random_pctl95']:.4f} | {'PASS' if p['random_set_pass'] else 'fail'} |"
        )
    lines += [
        "",
        "Per-model in-vocabulary lists (pre-registered publication):",
    ]
    for r in results:
        lines.append(f"- **{r['model']}** ({r['n_items_analysed']} in-vocab): dropped = {r['in_vocab_dropped_words'] or 'none'}")
    lines += [
        "",
        "Secondary: embedding-layer and jl576/full-D kernel-variant numbers are in results-e2.json.",
        "Interpretation is conditioned on X3 (polarity); scope limits of poc-design.md Common rule 6 apply.",
    ]
    if mock:
        lines += ["", "**MOCK RUN — pipeline smoke test only; numbers are meaningless by construction.**"]
    return j, "\n".join(lines)


# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="E2 geometry-alignment probe")
    ap.add_argument("--models", nargs="*", default=DEFAULT_MODELS)
    ap.add_argument("--inputs-dir", default=os.path.join(os.path.dirname(__file__), "..", "inputs"))
    ap.add_argument("--out-dir", default=os.path.join(os.path.dirname(__file__), "..", "results"))
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    ap.add_argument("--k-sets", type=int, default=K_SETS)
    ap.add_argument("--mock", action="store_true", help="CPU smoke test with a deterministic pseudo-model (numpy only)")
    args = ap.parse_args()

    if args.mock:
        args.models = ["mock/family-a", "mock/family-b", "mock/family-c"]
        args.n_perm = min(args.n_perm, 1000)
        args.k_sets = min(args.k_sets, 25)

    inp = load_inputs(args.inputs_dir)
    kernels = kernel_matrices(inp)
    results = [run_model(m, inp, kernels, args, args.mock) for m in args.models]
    j, md = verdict(results, inp, args, args.mock)

    os.makedirs(args.out_dir, exist_ok=True)
    suffix = "-mock" if args.mock else ""
    jpath = os.path.join(args.out_dir, f"results-e2{suffix}.json")
    mpath = os.path.join(args.out_dir, f"verdict-e2{suffix}.md")
    with open(jpath, "w") as f:
        json.dump(j, f, indent=2)
    with open(mpath, "w") as f:
        f.write(md + "\n")
    print(f"\nwrote {jpath}\nwrote {mpath}\n\nOUTCOME: {j['outcome']}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
