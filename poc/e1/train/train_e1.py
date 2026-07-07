#!/usr/bin/env python3
"""E1 trainer (docs/poc-design.md E1; bead kernel-of-truth-bk0). Single file.

GPT-2-style causal LM, d_model = 512 (pinned kot-enc-Bq/1@512 dimension),
word-level vocab from build_data.py. FIVE ARMS that differ ONLY in the
54 concept-token rows' initialisation + freezing mask (Common rule 4):

  kernel-frozen    kernel vectors (x frozenScale), rows FROZEN
  shuffled-frozen  seeded derangement of concept<->vector (per seed), FROZEN
  random-frozen    i.i.d. N(0, initStd^2) per-seed table, FROZEN
  trainable        standard init (N(0, initStd^2)), trainable
  kernel-init      kernel vectors (x frozenScale), TRAINABLE (MINOR 20)

FREEZING DISCIPLINE (Common rule 4, all three requirements):
  1. weight-decay exclusion: token embeddings (tied with the LM head) sit in
     the no-decay param group in ALL arms — frozen rows are never decayed,
     and no decay asymmetry between arms is introduced;
  2. optimizer-state masking: gradients of frozen rows are zeroed after
     every backward() BEFORE optimizer.step(), so Adam exp_avg/exp_avg_sq
     stay exactly 0 for those rows and the update is exactly 0;
  3. no step before the mask attaches: the mask is applied from step 0 and
     we assert the optimizer state is empty at attach time.
  VERIFICATION: frozen rows are snapshotted at init and asserted BIT-IDENTICAL
  (torch.equal) at every checkpoint and at the end; a mismatch CRASHES the run.

PAIRED SEEDS (Common rule 1): base init and the batch schedule depend on the
seed only (never the arm): all five arms of seed k see identical parameters
outside the concept rows and an identical batch sequence.

Checkpoints at step 0 (circularity baseline, MAJOR 5), 50% and 100% of the
token budget (single-look primary: kernel@50% vs shuffled@100% — MAJOR 12).

Per-condition LR (Common rule 5): run with --budget-frac 0.5 per candidate LR
on seed 0 (run_all.sh drives the sweep), select best-of-3 by val loss, then
train all seeds at the fixed per-arm LR.
"""

import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
E1_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(E1_DIR, "pipeline"))
from detstream import det_permutation  # noqa: E402

ARMS = ("kernel-frozen", "shuffled-frozen", "random-frozen", "trainable", "kernel-init")
FROZEN_ARMS = ("kernel-frozen", "shuffled-frozen", "random-frozen")


# ---------------------------------------------------------------------------
# Model (GPT-2 style, pre-LN, learned positions, tied embeddings)
# ---------------------------------------------------------------------------

class Block(nn.Module):
    def __init__(self, d, h, dff):
        super().__init__()
        self.ln1 = nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, h, batch_first=True)
        self.ln2 = nn.LayerNorm(d)
        self.fc = nn.Linear(d, dff)
        self.proj = nn.Linear(dff, d)

    def forward(self, x, attn_mask):
        h = self.ln1(x)
        a, _ = self.attn(h, h, h, attn_mask=attn_mask, need_weights=False)
        x = x + a
        x = x + self.proj(F.gelu(self.fc(self.ln2(x))))
        return x


class GPT(nn.Module):
    def __init__(self, vocab, d, n_layer, n_head, dff, seq_len):
        super().__init__()
        self.wte = nn.Embedding(vocab, d)
        self.wpe = nn.Embedding(seq_len, d)
        self.blocks = nn.ModuleList([Block(d, n_head, dff) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(d)
        self.seq_len = seq_len
        mask = torch.triu(torch.full((seq_len, seq_len), float("-inf")), diagonal=1)
        self.register_buffer("mask", mask, persistent=False)

    def hidden_states(self, idx):
        """Returns the list of post-block hidden states (for mid-layer probes)."""
        T = idx.shape[1]
        x = self.wte(idx) + self.wpe(torch.arange(T, device=idx.device))
        states = []
        m = self.mask[:T, :T]
        for b in self.blocks:
            x = b(x, m)
            states.append(x)
        return states

    def forward(self, idx):
        x = self.hidden_states(idx)[-1]
        x = self.ln_f(x)
        return F.linear(x, self.wte.weight)  # tied LM head

    def init_weights(self, gen, init_std, n_layer):
        for name, p in self.named_parameters():
            if p.dim() >= 2:
                std = init_std
                if name.endswith("proj.weight") or "out_proj.weight" in name:
                    std = init_std / math.sqrt(2 * n_layer)  # GPT-2 residual scaling
                with torch.no_grad():
                    p.copy_(torch.normal(0.0, std, p.shape, generator=gen))
            else:
                with torch.no_grad():
                    p.zero_()
        # LayerNorm weights back to 1 (zeroed by the dim<2 branch above)
        for m in self.modules():
            if isinstance(m, nn.LayerNorm):
                with torch.no_grad():
                    m.weight.fill_(1.0)

    def non_embedding_params(self):
        emb = self.wte.weight.numel() + self.wpe.weight.numel()
        return sum(p.numel() for p in self.parameters()) - emb


# ---------------------------------------------------------------------------
# Concept-row initialisation per arm
# ---------------------------------------------------------------------------

def load_tables(path, d_model, vocab):
    with open(path) as f:
        tables = json.load(f)
    if tables["D"] != d_model:
        raise SystemExit(f"ERR_TABLES: table D={tables['D']} != d_model={d_model}")
    slugs = [i.replace("urn:kernel-v0:", "") for i in tables["ids"]]
    if slugs != vocab["conceptSlugs"]:
        raise SystemExit("ERR_TABLES: concept order mismatch between tables and vocab")
    return tables


def concept_rows_for_arm(arm, tables, seed):
    kernel = np.asarray(tables["kernel"], dtype=np.float32)
    scale = float(tables["frozenScale"])
    if arm in ("kernel-frozen", "kernel-init"):
        return kernel * scale
    if arm == "shuffled-frozen":
        entry = next(e for e in tables["shuffled"] if e["seed"] == seed)
        perm = entry["perm"]
        return kernel[perm] * scale
    if arm == "random-frozen":
        entry = next(e for e in tables["randomFrozen"] if e["seed"] == seed)
        return np.asarray(entry["rows"], dtype=np.float32)
    if arm == "trainable":
        return None  # keep the seed-paired base init
    raise SystemExit(f"ERR_ARM: {arm}")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

class Shard:
    def __init__(self, path, seq_len):
        self.data = np.memmap(path, dtype=np.uint16, mode="r")
        self.seq_len = seq_len
        self.n_windows = (len(self.data) - 1) // seq_len
        if self.n_windows < 1:
            raise SystemExit(f"ERR_DATA: shard {path} smaller than one window")

    def window(self, w):
        s = w * self.seq_len
        chunk = torch.from_numpy(self.data[s:s + self.seq_len + 1].astype(np.int64))
        return chunk[:-1], chunk[1:]


def batches(shard, batch_size, n_steps, seed):
    """Deterministic seed-paired schedule: epoch-wise DetStream permutations."""
    step = 0
    epoch = 0
    while step < n_steps:
        perm = det_permutation(f"e1/batches/{seed}/epoch{epoch}", shard.n_windows)
        for i in range(0, shard.n_windows - batch_size + 1, batch_size):
            if step >= n_steps:
                return
            xs, ys = zip(*(shard.window(w) for w in perm[i:i + batch_size]))
            yield step, torch.stack(xs), torch.stack(ys)
            step += 1
        epoch += 1


# ---------------------------------------------------------------------------
# Eval helpers (val loss + concept-slice loss)
# ---------------------------------------------------------------------------

@torch.no_grad()
def val_losses(model, shard, batch_size, n_batches, concept_lo, concept_hi, device):
    model.eval()
    tot, ntok = 0.0, 0
    ctot, cn = 0.0, 0
    for b in range(n_batches):
        ws = range(b * batch_size, min((b + 1) * batch_size, shard.n_windows))
        if not ws:
            break
        xs, ys = zip(*(shard.window(w) for w in ws))
        x, y = torch.stack(xs).to(device), torch.stack(ys).to(device)
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1), reduction="none")
        tot += loss.sum().item()
        ntok += loss.numel()
        cmask = (y.view(-1) >= concept_lo) & (y.view(-1) < concept_hi)
        if cmask.any():
            ctot += loss[cmask].sum().item()
            cn += int(cmask.sum().item())
    model.train()
    return {
        "valLoss": tot / max(ntok, 1),
        "valPpl": math.exp(min(tot / max(ntok, 1), 30)),
        "conceptSliceLoss": (ctot / cn) if cn else None,
        "conceptSlicePpl": math.exp(min(ctot / cn, 30)) if cn else None,
        "conceptTargets": cn,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="build_data.py output dir")
    ap.add_argument("--tables", required=True, help="vector-tables json")
    ap.add_argument("--arm", required=True, choices=ARMS)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lr", type=float, required=True)
    ap.add_argument("--n-layer", type=int, default=4)
    ap.add_argument("--n-head", type=int, default=8)
    ap.add_argument("--d-model", type=int, default=512)
    ap.add_argument("--d-ff", type=int, default=2048)
    ap.add_argument("--seq-len", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--total-tokens", type=int, default=200_000_000)
    ap.add_argument("--budget-frac", type=float, default=1.0,
                    help="fraction of --total-tokens actually run (LR sweep: 0.5)")
    ap.add_argument("--weight-decay", type=float, default=0.1)
    ap.add_argument("--warmup-frac", type=float, default=0.01)
    ap.add_argument("--init-std", type=float, default=0.02)
    ap.add_argument("--val-batches", type=int, default=20)
    ap.add_argument("--log-every", type=int, default=50)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--no-checkpoints", action="store_true", help="sweep mode: summary only")
    ap.add_argument("--allow-any-size", action="store_true",
                    help="skip the 5-15M non-embedding param assertion (mock smoke only)")
    args = ap.parse_args()

    device = args.device if args.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)  # library-level; all substantive draws are labelled
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()

    with open(os.path.join(args.data, "vocab.json")) as f:
        vocab = json.load(f)
    V = vocab["vocabSize"]
    sp = vocab["specials"]
    concept_lo = sp["conceptBase"]
    concept_hi = sp["conceptBase"] + sp["conceptCount"]
    tables = load_tables(args.tables, args.d_model, vocab)

    # ---- model: seed-paired base init, then arm-specific concept rows ------
    model = GPT(V, args.d_model, args.n_layer, args.n_head, args.d_ff, args.seq_len)
    gen = torch.Generator().manual_seed(args.seed)  # arm-INDEPENDENT base init
    model.init_weights(gen, args.init_std, args.n_layer)
    nep = model.non_embedding_params()
    if not args.allow_any_size and not (5_000_000 <= nep <= 15_000_000):
        raise SystemExit(f"ERR_SIZE: {nep} non-embedding params outside pre-registered 5-15M")

    rows = concept_rows_for_arm(args.arm, tables, args.seed)
    if rows is not None:
        if rows.shape != (sp["conceptCount"], args.d_model):
            raise SystemExit(f"ERR_TABLES: rows shape {rows.shape}")
        with torch.no_grad():
            model.wte.weight[concept_lo:concept_hi] = torch.from_numpy(rows.copy())
    model.to(device)

    frozen = args.arm in FROZEN_ARMS
    frozen_snapshot = model.wte.weight[concept_lo:concept_hi].detach().clone() if frozen else None

    def assert_frozen(where):
        if not frozen:
            return True
        same = torch.equal(model.wte.weight[concept_lo:concept_hi], frozen_snapshot)
        if not same:
            raise SystemExit(f"ERR_FROZEN_ROWS_MOVED at {where} — freezing mask failed; run is INVALID")
        return True

    # ---- optimizer: decay only >=2D non-embedding weights -------------------
    decay, nodecay = [], []
    emb_params = {id(model.wte.weight), id(model.wpe.weight)}
    for p in model.parameters():
        (decay if (p.dim() >= 2 and id(p) not in emb_params) else nodecay).append(p)
    opt = torch.optim.AdamW(
        [{"params": decay, "weight_decay": args.weight_decay},
         {"params": nodecay, "weight_decay": 0.0}],
        lr=args.lr, betas=(0.9, 0.95), eps=1e-8)
    if any(len(s) for s in opt.state.values()):
        raise SystemExit("ERR_OPT_STATE: optimizer state non-empty before mask attach")

    tokens_per_step = args.batch_size * args.seq_len
    n_steps = max(1, int(args.total_tokens * args.budget_frac) // tokens_per_step)
    half_step = n_steps // 2
    warmup = max(1, int(n_steps * args.warmup_frac))

    def lr_at(step):
        if step < warmup:
            return args.lr * (step + 1) / warmup
        p = (step - warmup) / max(1, n_steps - warmup)
        return args.lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * p)))

    train_shard = Shard(os.path.join(args.data, f"seed{args.seed}", "train.bin"), args.seq_len)
    val_shard = Shard(os.path.join(args.data, f"seed{args.seed}", "val.bin"), args.seq_len)

    run_id = f"{args.arm}-seed{args.seed}"
    log = open(os.path.join(args.out, f"train-{run_id}.jsonl"), "w")

    def save_ckpt(tag, step):
        assert_frozen(f"checkpoint {tag}")
        vm = val_losses(model, val_shard, args.batch_size, args.val_batches,
                        concept_lo, concept_hi, device)
        path = os.path.join(args.out, f"ckpt-{run_id}-{tag}.pt")
        torch.save({
            "model": model.state_dict(),
            "config": {k: getattr(args, k.replace("-", "_")) for k in
                       ["n_layer", "n_head", "d_model", "d_ff", "seq_len", "init_std"]},
            "arm": args.arm, "seed": args.seed, "step": step, "tag": tag,
            "vocabSize": V, "conceptLo": concept_lo, "conceptHi": concept_hi,
            "lr": args.lr, "totalTokens": args.total_tokens, "budgetFrac": args.budget_frac,
            "frozen": frozen, "frozenRowsBitIdentical": True if frozen else None,
            "val": vm,
        }, path)
        print(f"[{time.time()-t0:.0f}s] ckpt {tag} @step {step}: val {vm['valLoss']:.4f} "
              f"conceptSlice {vm['conceptSliceLoss']}")
        return vm

    if not args.no_checkpoints:
        save_ckpt("step0", 0)  # circularity baseline BEFORE any update (MAJOR 5)

    amp = device == "cuda"
    model.train()
    for step, x, y in batches(train_shard, args.batch_size, n_steps, args.seed):
        for g in opt.param_groups:
            g["lr"] = lr_at(step)
        x, y = x.to(device), y.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=amp):
            logits = model(x)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        if frozen and model.wte.weight.grad is not None:
            # optimizer-state masking: rows never see a nonzero grad, so Adam
            # moments stay 0 and the AdamW update is exactly 0 (wd=0 group).
            model.wte.weight.grad[concept_lo:concept_hi].zero_()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % args.log_every == 0:
            log.write(json.dumps({"step": step, "loss": float(loss.item()),
                                  "lr": lr_at(step), "tokens": step * tokens_per_step,
                                  "elapsed": time.time() - t0}) + "\n")
            log.flush()
        if not args.no_checkpoints and step + 1 == half_step:
            save_ckpt("50pct", step + 1)

    final = save_ckpt("100pct", n_steps) if not args.no_checkpoints else \
        val_losses(model, val_shard, args.batch_size, args.val_batches,
                   concept_lo, concept_hi, device)
    assert_frozen("end of training")

    summary = {
        "arm": args.arm, "seed": args.seed, "lr": args.lr, "steps": n_steps,
        "tokens": n_steps * tokens_per_step, "budgetFrac": args.budget_frac,
        "nonEmbeddingParams": nep, "vocabSize": V, "device": device,
        "frozen": frozen, "frozenRowsBitIdentical": True if frozen else None,
        "final": final, "wallSeconds": time.time() - t0,
    }
    with open(os.path.join(args.out, f"summary-{run_id}"
              + ("" if args.budget_frac == 1.0 else f"-frac{args.budget_frac}")
              + f"-lr{args.lr}.json"), "w") as f:
        json.dump(summary, f, indent=2)
    log.close()
    print(json.dumps({k: summary[k] for k in
                      ["arm", "seed", "lr", "steps", "frozenRowsBitIdentical"]}))
    print(f"[{time.time()-t0:.0f}s] done: final val {final['valLoss']:.4f}")


if __name__ == "__main__":
    main()
