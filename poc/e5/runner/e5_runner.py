#!/usr/bin/env python3
"""E5 — adapter + shuffled-kernel control runner (docs/poc-design.md Phase E,
E5 rev 2, MINOR 23; poc/e5/README.md pinned operationalisations O1-O6; bead
kernel-of-truth-c24).

The ONLY thing the GPU runs. All kernel-side inputs are precomputed on the
CPU box by the TS harness (poc/e5/inputs/*, pinned + sha-verified here, fail
closed). Frozen SmolLM2-135M; a single shared affine adapter kernel-space
(JL@576) -> model embedding space is the only trainable component; 3 arms
(true-kernel / shuffled-kernel / random-vector[descriptive]) x 5 paired
seeds; Common-rule-5 LR selection; fixed non-LLM forced-choice scoring;
pre-registered statistics quoted VERBATIM from inputs/e5-manifest.json.

    python3 e5_runner.py --inputs-dir ../inputs --out-dir /tmp/e5 --device cuda
    python3 e5_runner.py --inputs-dir ../inputs --out-dir /tmp/e5 --mock   # CPU mechanics check

Mock mode swaps SmolLM2 for a tiny random-init Llama + whitespace tokenizer
(network-free), shrinks budgets/seeds and subsamples the seen-eval items —
mechanics only; every output is MOCK-labelled.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

SEED_BASE = 20260707  # published fixed base seed (matches E2's convention)

# Full-run parameters are read from inputs/e5-manifest.json (the
# pre-registration artifact); the constants here are mock-only shrinkages.
MOCK_SEEDS = [0, 1]
MOCK_STEPS = 40
MOCK_SWEEP_STEPS = 20
MOCK_BATCH = 8
MOCK_SEEN_EVAL_N = 50
MOCK_HIDDEN = 64


def utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def det_int(label: str) -> int:
    """Python-side deterministic seed from a label (documented analogue of the
    TS DetStream discipline: SHA-256 over the label, first 8 bytes)."""
    return int.from_bytes(hashlib.sha256(label.encode()).digest()[:8], "big")


# ---------------------------------------------------------------------------
# Exact statistics (numpy + stdlib only)
# ---------------------------------------------------------------------------


def binom_sf_geq(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Bin(n, p), exact via log terms."""
    if k <= 0:
        return 1.0
    lp, lq = math.log(p), math.log(1 - p)
    total = 0.0
    for i in range(k, n + 1):
        lc = math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
        total += math.exp(lc + i * lp + (n - i) * lq)
    return min(1.0, total)


def exact_signflip_p_int(diffs: list[int]) -> float:
    """One-sided exact sign-flip permutation p over INTEGER paired diffs.

    Full 2^n enumeration by integer-lattice convolution (pre-registered
    primary implementation): distribution of sum_j eps_j*d_j over all sign
    vectors, p = P(T >= T_obs) including the observed assignment. Exact in
    int64 (mass 2^n <= 2^24 << 2^63).
    """
    total_abs = int(sum(abs(d) for d in diffs))
    counts = np.zeros(2 * total_abs + 1, dtype=np.int64)
    counts[total_abs] = 1  # empty sum = 0 (index offset total_abs)
    for d in diffs:
        a = abs(int(d))
        if a == 0:
            counts *= 2
            continue
        new = np.zeros_like(counts)
        new[a:] += counts[:-a]      # +a branch
        new[:-a] += counts[a:]      # -a branch
        counts = new
    t_obs = int(sum(diffs))
    mass_geq = int(counts[t_obs + total_abs:].sum())
    return mass_geq / float(2 ** len(diffs))


def exact_signflip_p_float(diffs: list[float]) -> float:
    """One-sided exact sign-flip p over few float paired diffs (2^n enum)."""
    n = len(diffs)
    obs = sum(diffs)
    count = 0
    for mask in range(1 << n):
        s = 0.0
        for j in range(n):
            s += diffs[j] if (mask >> j) & 1 else -diffs[j]
        if s >= obs - 1e-12:
            count += 1
    return count / float(1 << n)


# ---------------------------------------------------------------------------
# Inputs (fail-closed pins)
# ---------------------------------------------------------------------------


def load_inputs(inputs_dir: str) -> dict:
    with open(os.path.join(inputs_dir, "e5-manifest.json")) as f:
        manifest = json.load(f)
    pins = manifest["pins"]
    items_sha = sha256_file(os.path.join(inputs_dir, "e5-items.json"))
    if items_sha != pins["itemsSha256"]:
        raise SystemExit(f"ERR_ITEMS_PIN: e5-items.json sha {items_sha} != manifest pin")
    vecman_sha = sha256_file(os.path.join(inputs_dir, "vector-tables-manifest.json"))
    if vecman_sha != pins["vectorTablesManifestSha256"]:
        raise SystemExit("ERR_TABLES_PIN: vector-tables-manifest.json sha != manifest pin")
    with open(os.path.join(inputs_dir, "e5-items.json")) as f:
        items = json.load(f)
    with open(os.path.join(inputs_dir, "vector-tables-manifest.json")) as f:
        vecman = json.load(f)
    if items["glossHash"] != pins["glossHash"]:
        raise SystemExit("ERR_GLOSS_PIN: items glossHash != manifest pin")
    if vecman["encoderContentHash"] != pins["encoderContentHash"]:
        raise SystemExit("ERR_ENCODER_PIN: vector tables encoder hash != manifest pin")

    rows, d = vecman["rows"], vecman["d"]
    kfile = os.path.join(inputs_dir, vecman["kernel"]["file"])
    if sha256_file(kfile) != vecman["kernel"]["sha256"]:
        raise SystemExit("ERR_TABLES_PIN: kernel .f32 sha mismatch")
    kernel = np.fromfile(kfile, dtype="<f4").reshape(rows, d)
    randoms = {}
    for rf in vecman["randomFrozen"]:
        p = os.path.join(inputs_dir, rf["file"])
        if sha256_file(p) != rf["sha256"]:
            raise SystemExit(f"ERR_TABLES_PIN: {rf['file']} sha mismatch")
        randoms[rf["seed"]] = np.fromfile(p, dtype="<f4").reshape(rows, d)
    perms = {s["seed"]: np.asarray(s["perm"], dtype=np.int64) for s in vecman["shuffled"]}
    for s, perm in perms.items():
        if np.any(perm == np.arange(rows)):
            raise SystemExit(f"ERR_TABLES: derangement seed {s} has fixed points")

    # ---- re-assert zero exposure (README O3, pinned guard directions) --------
    nonce_rows = {it["row"] for it in items["nonceEval"]}
    nonce_glosses = {c["gloss"] for it in items["nonceEval"] for c in it["candidates"]}
    for t in items["training"]:
        if t["row"] in nonce_rows:
            raise SystemExit("ERR_LEAK: nonce row in training items")
        for g in nonce_glosses:
            if t["gloss"] == g or g in t["gloss"]:
                raise SystemExit("ERR_LEAK: nonce gloss text appears in training")

    return {"manifest": manifest, "items": items, "vecman": vecman,
            "kernel": kernel, "randoms": randoms, "perms": perms}


# ---------------------------------------------------------------------------
# Model + tokenizer (real or mock)
# ---------------------------------------------------------------------------


class MockTokenizer:
    """Deterministic whitespace tokenizer for the network-free CPU mock."""

    def __init__(self, texts: list[str]):
        vocab: set[str] = set()
        for t in texts:
            vocab.update(t.split())
        self.bos_token_id = 0
        self.pad_token_id = 1
        self.id_of = {w: i + 2 for i, w in enumerate(sorted(vocab))}
        self.vocab_size = len(self.id_of) + 2

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        return [self.id_of[w] for w in text.split()]


def build_model(mock: bool, device: str, d_model_expected: int):
    import torch

    if mock:
        return None, None  # constructed later, needs the text corpus
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_id = "HuggingFaceTB/SmolLM2-135M"
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
    if model.config.hidden_size != d_model_expected:
        raise SystemExit(
            f"ERR_DMODEL: {model_id} hidden_size {model.config.hidden_size} != {d_model_expected}")
    model.to(device).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model, tok


def build_mock_model(texts: list[str], device: str):
    import torch
    from transformers import LlamaConfig, LlamaForCausalLM

    tok = MockTokenizer(texts)
    torch.manual_seed(det_int("e5/mockmodel"))
    cfg = LlamaConfig(
        vocab_size=tok.vocab_size, hidden_size=MOCK_HIDDEN, intermediate_size=2 * MOCK_HIDDEN,
        num_hidden_layers=2, num_attention_heads=2, num_key_value_heads=2,
        max_position_embeddings=512,
    )
    model = LlamaForCausalLM(cfg).to(device).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model, tok


# ---------------------------------------------------------------------------
# Sequence construction + batching
# ---------------------------------------------------------------------------


def build_seq(tok, frame: dict, gloss: str) -> dict:
    pre = tok.encode(frame["prefix"], add_special_tokens=False)
    suf = tok.encode(frame["suffix"], add_special_tokens=False)
    cand = tok.encode(frame["candidatePrefix"] + gloss, add_special_tokens=False)
    bos = tok.bos_token_id if tok.bos_token_id is not None else tok.pad_token_id
    ids = [bos] + pre + [0] + suf + cand
    slot = 1 + len(pre)
    cand_start = slot + 1 + len(suf)
    if len(ids) > frame["tokenCap"]:
        raise SystemExit(f"ERR_TOKENCAP: sequence length {len(ids)} > cap {frame['tokenCap']}")
    return {"ids": ids, "slot": slot, "cand_start": cand_start, "cand_len": len(cand)}


def make_batch(seqs: list[dict], rows: list[int], pad_id: int, device: str):
    import torch

    maxlen = max(len(s["ids"]) for s in seqs)
    n = len(seqs)
    ids = torch.full((n, maxlen), pad_id, dtype=torch.long)
    mask = torch.zeros((n, maxlen), dtype=torch.long)
    labels = torch.full((n, maxlen), -100, dtype=torch.long)
    slots = torch.zeros(n, dtype=torch.long)
    for i, s in enumerate(seqs):
        L = len(s["ids"])
        ids[i, :L] = torch.tensor(s["ids"], dtype=torch.long)
        mask[i, :L] = 1
        cs, cl = s["cand_start"], s["cand_len"]
        labels[i, cs:cs + cl] = ids[i, cs:cs + cl]
        slots[i] = s["slot"]
    return (ids.to(device), mask.to(device), labels.to(device), slots.to(device),
            torch.tensor(rows, dtype=torch.long, device=device))


def forward_loss(model, embed_weight, adapter, table_t, batch, per_item: bool = False):
    """CE on candidate tokens; adapter output injected at each row's slot."""
    import torch
    import torch.nn.functional as F

    ids, mask, labels, slots, rows = batch
    with torch.no_grad():
        embeds = torch.nn.functional.embedding(ids, embed_weight)
    embeds = embeds.clone()
    inj = adapter(table_t[rows])  # (n, d_model), carries grad
    embeds[torch.arange(ids.shape[0], device=ids.device), slots] = inj
    out = model(inputs_embeds=embeds, attention_mask=mask)
    logits = out.logits[:, :-1]
    tgt = labels[:, 1:]
    lp = F.log_softmax(logits.float(), dim=-1)
    tokmask = (tgt != -100)
    safe_tgt = tgt.clamp(min=0)
    tok_lp = lp.gather(-1, safe_tgt.unsqueeze(-1)).squeeze(-1)
    tok_lp = tok_lp * tokmask
    per_item_lp = tok_lp.sum(1) / tokmask.sum(1).clamp(min=1)
    if per_item:
        return -per_item_lp  # per-item mean-token CE (also = -mean logprob)
    return -per_item_lp.mean()


# ---------------------------------------------------------------------------
# Adapter training + eval
# ---------------------------------------------------------------------------


def init_adapter(embed_weight, d_in: int, seed: int, device: str):
    import torch

    d_model = embed_weight.shape[1]
    sigma = float(embed_weight.std().item())
    mean_row = embed_weight.mean(dim=0)
    gen = torch.Generator().manual_seed(SEED_BASE * 1000 + seed)
    adapter = torch.nn.Linear(d_in, d_model, bias=True).to(device)
    with torch.no_grad():
        adapter.weight.copy_(torch.randn((d_model, d_in), generator=gen) * sigma)
        adapter.bias.copy_(mean_row)
    return adapter, sigma


def lr_factor(step: int, steps: int, warmup: int) -> float:
    if step < warmup:
        return (step + 1) / warmup
    t = (step - warmup) / max(1, steps - warmup)
    return 0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * t))


def train_adapter(model, embed_weight, table_t, train_seqs, train_rows, seed: int,
                  lr: float, steps: int, batch_size: int, warmup: int, clip: float,
                  device: str, log) -> tuple:
    import torch

    adapter, sigma = init_adapter(embed_weight, table_t.shape[1], seed, device)
    opt = torch.optim.AdamW(adapter.parameters(), lr=lr, betas=(0.9, 0.999),
                            eps=1e-8, weight_decay=0.0)
    n = len(train_seqs)
    curve = []
    epoch, pos, order = -1, n, None
    for step in range(steps):
        if pos + batch_size > n:
            epoch += 1
            rng = np.random.Generator(np.random.PCG64(det_int(f"e5/order/{seed}/{epoch}")))
            order = rng.permutation(n)
            pos = 0
        idx = order[pos:pos + batch_size]
        pos += batch_size
        batch = make_batch([train_seqs[i] for i in idx], [train_rows[i] for i in idx],
                           PAD_ID, device)
        f = lr_factor(step, steps, warmup)
        for g in opt.param_groups:
            g["lr"] = lr * f
        loss = forward_loss(model, embed_weight, adapter, table_t, batch)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(adapter.parameters(), clip)
        opt.step()
        if step % 50 == 0 or step == steps - 1:
            curve.append({"step": step, "loss": float(loss.item()), "lr": lr * f})
            log(f"    step {step}/{steps} loss {loss.item():.4f}")
    return adapter, sigma, curve


def mean_ce(model, embed_weight, adapter, table_t, seqs, rows, device: str,
            batch_size: int = 32) -> float:
    import torch

    ces = []
    with torch.no_grad():
        for i in range(0, len(seqs), batch_size):
            batch = make_batch(seqs[i:i + batch_size], rows[i:i + batch_size], PAD_ID, device)
            ces.append(forward_loss(model, embed_weight, adapter, table_t, batch,
                                    per_item=True).cpu().numpy())
    return float(np.concatenate(ces).mean())


def score_eval(model, embed_weight, adapter, table_t, eval_items, seq_cache, device: str,
               batch_rows: int = 48) -> list[dict]:
    """Forced-choice scoring: per item, mean per-token logprob per candidate;
    correct iff strict argmax = candidate 0 (ties incorrect; README O3)."""
    import torch

    flat_seqs, flat_rows, owners = [], [], []
    for ii, it in enumerate(eval_items):
        for ci in range(len(it["candidates"])):
            flat_seqs.append(seq_cache[(ii, ci)])
            flat_rows.append(it["row"])
            owners.append((ii, ci))
    scores = np.zeros(len(flat_seqs))
    with torch.no_grad():
        for i in range(0, len(flat_seqs), batch_rows):
            batch = make_batch(flat_seqs[i:i + batch_rows], flat_rows[i:i + batch_rows],
                               PAD_ID, device)
            ce = forward_loss(model, embed_weight, adapter, table_t, batch, per_item=True)
            scores[i:i + batch_rows] = -ce.cpu().numpy()  # mean per-token logprob
    out = []
    k = 0
    for ii, it in enumerate(eval_items):
        cs = [float(scores[k + c]) for c in range(len(it["candidates"]))]
        k += len(it["candidates"])
        best = max(cs)
        correct = (cs[0] == best) and (cs.count(best) == 1)
        out.append({"concept": it["concept"], "style": it["style"], "scores": cs,
                    "correct": bool(correct), "margin": cs[0] - max(cs[1:])})
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

PAD_ID = 0  # set in main()


def main() -> None:
    global PAD_ID
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--max-hours", type=float, default=3.6,
                    help="soft wall-clock budget; exceeded => fail loudly with partials")
    args = ap.parse_args()
    t0 = time.time()
    os.makedirs(args.out_dir, exist_ok=True)

    import torch
    torch.manual_seed(SEED_BASE)
    if args.device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    data = load_inputs(args.inputs_dir)
    manifest, items = data["manifest"], data["items"]
    frame = manifest["frame"]
    tr_spec = manifest["training"]
    seeds = MOCK_SEEDS if args.mock else manifest["seeds"]
    steps = MOCK_STEPS if args.mock else tr_spec["steps"]
    sweep_steps = MOCK_SWEEP_STEPS if args.mock else tr_spec["sweepSteps"]
    sweep_lrs = tr_spec["lrSweep"][:2] if args.mock else tr_spec["lrSweep"]
    batch_size = MOCK_BATCH if args.mock else tr_spec["batch"]
    warmup = 5 if args.mock else tr_spec["warmupSteps"]
    clip = tr_spec["gradClip"]
    seen_eval = items["seenEval"][:MOCK_SEEN_EVAL_N] if args.mock else items["seenEval"]
    nonce_eval = items["nonceEval"]
    label = "MOCK" if args.mock else "FULL"

    def log(msg: str) -> None:
        print(f"[e5 {time.time() - t0:7.1f}s] {msg}", flush=True)

    log(f"mode={label} device={args.device} seeds={seeds} steps={steps} "
        f"sweep={sweep_lrs}@{sweep_steps} batch={batch_size}")

    # ---- model ----------------------------------------------------------------
    if args.mock:
        texts = ([frame["prefix"], frame["suffix"]]
                 + [frame["candidatePrefix"] + t["gloss"] for t in items["training"]]
                 + [frame["candidatePrefix"] + c["gloss"] for it in items["seenEval"] + nonce_eval
                    for c in it["candidates"]])
        model, tok = build_mock_model(texts, args.device)
    else:
        model, tok = build_model(False, args.device, manifest["model"]["dModel"])
    PAD_ID = tok.pad_token_id if tok.pad_token_id is not None else tok.bos_token_id
    embed_weight = model.get_input_embeddings().weight  # frozen
    param_checksum_before = float(sum(p.abs().sum().item() for p in model.parameters()))

    # ---- sequences (built once; identical across arms/seeds) -------------------
    train_items = items["training"]
    train_all = [(build_seq(tok, frame, t["gloss"]), t["row"], t["val"]) for t in train_items]
    train_seqs = [s for s, _, v in train_all if not v]
    train_rows = [r for _, r, v in train_all if not v]
    val_seqs = [s for s, _, v in train_all if v]
    val_rows = [r for _, r, v in train_all if v]
    seen_cache = {(ii, ci): build_seq(tok, frame, c["gloss"])
                  for ii, it in enumerate(seen_eval) for ci, c in enumerate(it["candidates"])}
    nonce_cache = {(ii, ci): build_seq(tok, frame, c["gloss"])
                   for ii, it in enumerate(nonce_eval) for ci, c in enumerate(it["candidates"])}
    log(f"sequences: {len(train_seqs)} train / {len(val_seqs)} val / "
        f"{len(seen_eval)} seen-eval / {len(nonce_eval)} nonce-eval")

    kernel = torch.tensor(data["kernel"], dtype=torch.float32, device=args.device)

    def table_for(arm: str, seed: int):
        if arm == "true":
            return kernel
        if arm == "shuffled":
            perm = torch.tensor(data["perms"][seed], dtype=torch.long, device=args.device)
            return kernel[perm]
        if arm == "random":
            return torch.tensor(data["randoms"][seed], dtype=torch.float32, device=args.device)
        raise ValueError(arm)

    arms = ["true", "shuffled", "random"]
    results: dict = {"armSeed": {}, "lrSelection": {}}

    # ---- LR selection (Common rule 5): per-arm sweep on seed 0, half budget ----
    for arm in arms:
        best = None
        for lr in sweep_lrs:
            if (time.time() - t0) / 3600 > args.max_hours:
                raise SystemExit(f"ERR_TIME_BUDGET: exceeded {args.max_hours}h during sweep")
            log(f"sweep arm={arm} lr={lr}")
            table_t = table_for(arm, seeds[0])
            adapter, _, _ = train_adapter(model, embed_weight, table_t, train_seqs,
                                          train_rows, seeds[0], lr, sweep_steps,
                                          batch_size, warmup, clip, args.device, log)
            vce = mean_ce(model, embed_weight, adapter, table_t, val_seqs, val_rows,
                          args.device)
            log(f"  arm={arm} lr={lr} valCE={vce:.4f}")
            if best is None or vce < best[1] - 1e-12:
                best = (lr, vce)
        results["lrSelection"][arm] = {"lr": best[0], "valCE": best[1],
                                       "rule": tr_spec["lrRule"], "swept": sweep_lrs,
                                       "sweepSteps": sweep_steps}
        log(f"selected lr={best[0]} for arm={arm}")

    # ---- full runs --------------------------------------------------------------
    for arm in arms:
        lr = results["lrSelection"][arm]["lr"]
        for seed in seeds:
            elapsed_h = (time.time() - t0) / 3600
            if elapsed_h > args.max_hours:
                raise SystemExit(f"ERR_TIME_BUDGET: {elapsed_h:.2f}h > {args.max_hours}h "
                                 f"before arm={arm} seed={seed} (partials saved)")
            log(f"train arm={arm} seed={seed} lr={lr}")
            table_t = table_for(arm, seed)
            # step-0 (untrained adapter, same init as training start) — descriptive
            adapter0, _sigma0 = init_adapter(embed_weight, table_t.shape[1], seed, args.device)
            step0_nonce = score_eval(model, embed_weight, adapter0, table_t, nonce_eval,
                                     nonce_cache, args.device)
            adapter, sigma, curve = train_adapter(model, embed_weight, table_t, train_seqs,
                                                  train_rows, seed, lr, steps, batch_size,
                                                  warmup, clip, args.device, log)
            vce = mean_ce(model, embed_weight, adapter, table_t, val_seqs, val_rows,
                          args.device)
            seen_res = score_eval(model, embed_weight, adapter, table_t, seen_eval,
                                  seen_cache, args.device)
            nonce_res = score_eval(model, embed_weight, adapter, table_t, nonce_eval,
                                   nonce_cache, args.device)
            key = f"{arm}-seed{seed}"
            results["armSeed"][key] = {
                "arm": arm, "seed": seed, "lr": lr, "valCE": vce,
                "adapterInitSigma": sigma, "curve": curve,
                "seenAcc": float(np.mean([r["correct"] for r in seen_res])),
                "seenCorrect": int(sum(r["correct"] for r in seen_res)),
                "seenN": len(seen_res),
                "nonceAcc": float(np.mean([r["correct"] for r in nonce_res])),
                "step0NonceAcc": float(np.mean([r["correct"] for r in step0_nonce])),
                "meanNonceMargin": float(np.mean([r["margin"] for r in nonce_res])),
            }
            with open(os.path.join(args.out_dir, f"eval-items-{key}.json"), "w") as f:
                json.dump({"seen": seen_res, "nonce": nonce_res,
                           "step0Nonce": step0_nonce}, f)
            W = adapter.weight.detach().cpu().numpy().astype(np.float32)
            b = adapter.bias.detach().cpu().numpy().astype(np.float32)
            np.savez(os.path.join(args.out_dir, f"adapter-{key}.npz"), W=W, b=b)
            log(f"  arm={arm} seed={seed}: seenAcc={results['armSeed'][key]['seenAcc']:.4f} "
                f"nonceAcc={results['armSeed'][key]['nonceAcc']:.4f} valCE={vce:.4f}")

    param_checksum_after = float(sum(p.abs().sum().item() for p in model.parameters()))
    if param_checksum_before != param_checksum_after:
        raise SystemExit("ERR_FROZEN: model parameter checksum changed — the model was not frozen")

    # ---- pre-registered statistics ---------------------------------------------
    stats_spec = manifest["statistics"]
    nonces = sorted({it["concept"] for it in nonce_eval})
    items_per_nonce = len(nonce_eval) // len(nonces)

    _cc_cache: dict = {}

    def correct_counts(arm: str, seed: int) -> dict:
        key = (arm, seed)
        if key not in _cc_cache:
            with open(os.path.join(args.out_dir, f"eval-items-{arm}-seed{seed}.json")) as f:
                recs = json.load(f)["nonce"]
            out = {c: 0 for c in nonces}
            for r in recs:
                out[r["concept"]] += 1 if r["correct"] else 0
            _cc_cache[key] = out
        return _cc_cache[key]

    int_diffs, per_nonce = [], {}
    for c in nonces:
        dj = 0
        for seed in seeds:
            dj += correct_counts("true", seed)[c] - correct_counts("shuffled", seed)[c]
        int_diffs.append(dj)
        per_nonce[c] = {"intDiff": dj,
                        "meanDiff": dj / (len(seeds) * items_per_nonce),
                        "composition": None}
    # attach compositional split (descriptive) if present in concepts artifact
    try:
        with open(os.path.join(args.inputs_dir, "e5-concepts.json")) as f:
            comp = json.load(f)["composition"]
        for c in nonces:
            per_nonce[c]["composition"] = comp.get(c)
    except Exception:
        pass

    p_primary = exact_signflip_p_int(int_diffs)
    mean_diff = float(np.mean([d / (len(seeds) * items_per_nonce) for d in int_diffs]))

    seed_means = []
    for seed in seeds:
        tsum = sum(correct_counts("true", seed).values())
        ssum = sum(correct_counts("shuffled", seed).values())
        seed_means.append((tsum - ssum) / (len(nonces) * items_per_nonce))
    p_secondary = exact_signflip_p_float(seed_means)

    gate_per_seed = []
    for seed in seeds:
        r = results["armSeed"][f"true-seed{seed}"]
        p = binom_sf_geq(r["seenCorrect"], r["seenN"], manifest["scoring"]["chance"])
        gate_per_seed.append({"seed": seed, "seenCorrect": r["seenCorrect"],
                              "seenN": r["seenN"], "p": p, "pass": p < 0.05})
    n_gate_pass = sum(g["pass"] for g in gate_per_seed)
    gate_needed = max(len(seeds) - 1, 1)
    gate_ok = n_gate_pass >= gate_needed

    if not gate_ok:
        outcome = "INSTRUMENT-INVALID"
    elif p_primary < 0.05 and mean_diff > 0:
        outcome = "PASS"
    else:
        outcome = "FAIL"
    if args.mock:
        outcome = f"MOCK-{outcome}"

    results.update({
        "outcome": outcome,
        "mode": label,
        "date": utcnow(),
        "device": args.device,
        "torch": torch.__version__,
        "tf32": bool(args.device == "cuda"),
        "model": manifest["model"]["id"] if not args.mock else f"mock-llama-{MOCK_HIDDEN}",
        "seeds": seeds,
        "pins": manifest["pins"],
        "specVerbatim": manifest["specVerbatim"],
        "statisticsSpec": stats_spec,
        "primary": {
            "test": "one-sided exact sign-flip permutation over nonce-level paired differences (integer-lattice convolution, full 2^n enumeration)",
            "nNonces": len(nonces), "itemsPerNonce": items_per_nonce,
            "intDiffs": int_diffs, "meanDiff": mean_diff, "p": p_primary,
            "alpha": 0.05, "reject": bool(p_primary < 0.05 and mean_diff > 0),
        },
        "instrumentValidityGate": {
            "rule": stats_spec["instrumentValidityGate"], "perSeed": gate_per_seed,
            "passed": gate_ok, "nPass": n_gate_pass, "needed": gate_needed,
        },
        "secondary": {
            "test": "one-sided exact paired sign-flip over per-seed mean nonce accuracy diffs (true - shuffled), Holm m=1",
            "seedMeanDiffs": seed_means, "p": p_secondary, "pHolm": p_secondary,
            "reject": bool(p_secondary < 0.05 and np.mean(seed_means) > 0),
        },
        "perNonce": per_nonce,
        "paramChecksum": {"before": param_checksum_before, "after": param_checksum_after},
        "wallClockHours": (time.time() - t0) / 3600,
    })

    suffix = "-mock" if args.mock else ""
    with open(os.path.join(args.out_dir, f"results-e5{suffix}.json"), "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)

    # ---- verdict ----------------------------------------------------------------
    def acc_table(field: str) -> str:
        lines = ["| arm | " + " | ".join(f"seed{s}" for s in seeds) + " |",
                 "|---|" + "---|" * len(seeds)]
        for arm in arms:
            vals = [f"{results['armSeed'][f'{arm}-seed{s}'][field]:.4f}" for s in seeds]
            lines.append(f"| {arm} | " + " | ".join(vals) + " |")
        return "\n".join(lines)

    shared = [c for c in nonces if (per_nonce[c]["composition"] or {}).get("sharesStructureWithSeen")]
    md = [
        f"# E5 verdict{' (MOCK — mechanics only, tiny random model)' if args.mock else ''}",
        "",
        f"date: {results['date']}  |  mode: {label}  |  device: {args.device}  |  model: {results['model']}",
        f"encoder pin: `{manifest['pins']['encoderContentHash'][:12]}…`  |  gloss pin: `{manifest['pins']['glossHash'][:12]}…`",
        "",
        "**Pre-registered spec (docs/poc-design.md E5 rev 2, verbatim):**",
        f"> {manifest['specVerbatim']}",
        "",
        "**Pre-registered primary (poc/e5/inputs/e5-manifest.json, verbatim):**",
        f"> {stats_spec['primaryEndpoint']}",
        "",
        "**Pre-registered success criterion (verbatim):**",
        f"> {stats_spec['successCriterion']}",
        "",
        f"## OUTCOME: **{outcome}**",
        "",
        f"- Instrument-validity gate: {n_gate_pass}/{len(seeds)} seeds beat chance on seen items "
        f"(need >= {gate_needed}) => {'PASSED' if gate_ok else 'FAILED'}",
        f"  - rule: {stats_spec['instrumentValidityGate']}",
        f"- Primary: mean nonce accuracy diff (true - shuffled) = {mean_diff:+.4f}, "
        f"one-sided exact sign-flip p = {p_primary:.6f} (alpha 0.05, n = {len(nonces)} nonces)",
        f"- Secondary (Holm m=1): per-seed mean diffs {['%+.4f' % m for m in seed_means]}, "
        f"p = {p_secondary:.4f}",
        "",
        "### Nonce accuracy (5-way forced choice, chance 0.2)",
        acc_table("nonceAcc"),
        "",
        "### Seen validity accuracy (chance 0.2)",
        acc_table("seenAcc"),
        "",
        "### Step-0 (untrained adapter) nonce accuracy — descriptive",
        acc_table("step0NonceAcc"),
        "",
        f"### Compositional split (descriptive): {len(shared)}/{len(nonces)} nonces share structure with seen set",
        f"- shared: mean diff {np.mean([per_nonce[c]['meanDiff'] for c in shared]) if shared else float('nan'):+.4f}",
        f"- novel: mean diff {np.mean([per_nonce[c]['meanDiff'] for c in nonces if c not in shared]) if len(shared) < len(nonces) else float('nan'):+.4f}",
        "",
        f"LR selection (Common rule 5): "
        + ", ".join(f"{a}={results['lrSelection'][a]['lr']}" for a in arms),
        "",
        "Scope limits (README O6 / Common rule 6) apply; the random arm is descriptive only.",
        f"Random-arm nonce accuracies (descriptive): "
        + ", ".join(f"seed{s}={results['armSeed'][f'random-seed{s}']['nonceAcc']:.4f}" for s in seeds),
        "",
    ]
    with open(os.path.join(args.out_dir, f"verdict-e5{suffix}.md"), "w") as f:
        f.write("\n".join(md))
    log(f"OUTCOME: {outcome} (results in {args.out_dir})")


if __name__ == "__main__":
    main()
