#!/usr/bin/env python3
"""E4 emission fine-tuner (docs/poc-design.md E4 rev 2; bead
kernel-of-truth-hkp). Consumes ONE E1 kernel-frozen checkpoint (poc/e1's
trainer output, read-only) + the E4 emission shards (poc/e4's
build_emission.py output) and fine-tunes under the E1 freezing discipline.

ARMS (poc/e4/inputs/holdout-manifest.json `statistics.arms`, verbatim):
  kernel    "E1 kernel-frozen model + kernel rows for the 1000 new concepts
            (frozen)"
  shuffled  "same, with the concept<->vector assignment deranged per
            vector-tables-manifest (the EMPIRICAL CHANCE FLOOR — BLOCKER 3)"
  random    "descriptive secondary arm" (random-frozen tables)

MODEL SURGERY (E1 model/code untouched — poc/e1/train/train_e1.py is imported
read-only for the GPT/Shard classes):
  - vocab extended V -> V' per e4-vocab.json (EMIT + 1000 synthetic concept
    rows appended); all non-embedding weights + positions copied bit-exact;
  - appended rows initialised N(0, init_std^2) from a SEED-paired,
    arm-independent generator (Common rule 1 analog), then the 1054 concept
    rows are set per arm from the vector-tables manifest (kernel/shuffled
    rows x frozenScale at load — manifest `scalePolicy`; random rows raw);
  - KERNEL arm: the 54 authored rows are KEPT from the E1 checkpoint
    (bit-exact continuity) and the table-derived rows are asserted equal to
    them (fail closed; --authored-row-tol relaxes to a recorded deviation).
    SHUFFLED arm note (pre-registered consequence of the manifest's 1054-row
    derangement): the 54 authored rows are ALSO deranged, so they differ
    from the rows the E1 base model was trained around — identical glosses,
    content-free assignment; that is what makes it the empirical chance
    floor.

FREEZING DISCIPLINE — reuse of poc/e1's masking assertions (Common rule 4):
  1. weight-decay exclusion: embeddings in the wd=0 group in ALL arms;
  2. optimizer-state masking: frozen-row grads zeroed after every backward()
     BEFORE optimizer.step() (index mask — the 1054 rows are non-contiguous),
     so Adam moments stay exactly 0;
  3. mask active from step 0; optimizer state asserted empty at attach.
  VERIFICATION: the 1054 frozen rows are snapshotted at init and asserted
  BIT-IDENTICAL (torch.equal) at every checkpoint and at the end; a mismatch
  CRASHES the run (ERR_FROZEN_ROWS_MOVED).

The EMIT row and all pre-existing non-concept rows stay ordinary trainable
parameters. Fixed LR, identical across arms (arms differ only in frozen row
CONTENT, so the choice is arm-symmetric — no confound; recorded in summary).
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
E4_DIR = os.path.dirname(HERE)
E1_DIR = os.path.join(os.path.dirname(E4_DIR), "e1")
sys.path.insert(0, os.path.join(E1_DIR, "pipeline"))
sys.path.insert(0, os.path.join(E1_DIR, "train"))
from detstream import det_permutation  # noqa: E402
from train_e1 import GPT, Shard  # noqa: E402  (read-only reuse)

ARMS = ("kernel", "shuffled", "random")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_tables(manifest_path, d_model, n_expected):
    """Vector-tables manifest + sha-verified kernel table (fail closed)."""
    with open(manifest_path) as f:
        man = json.load(f)
    if man.get("artifact") not in ("e4-vector-tables", "e4-vector-tables-MOCK"):
        raise SystemExit("ERR_TABLES: not an e4 vector-tables manifest")
    if man["D"] != d_model:
        raise SystemExit(f"ERR_TABLES: manifest D={man['D']} != d_model={d_model}")
    if man["rows"] != n_expected:
        raise SystemExit(f"ERR_TABLES: manifest rows={man['rows']} != {n_expected}")
    base = os.path.dirname(os.path.abspath(manifest_path))
    kpath = os.path.join(base, man["kernel"]["file"])
    if sha256_file(kpath) != man["kernel"]["sha256"]:
        raise SystemExit(f"ERR_TABLES: {kpath} sha256 != manifest pin")
    K = np.fromfile(kpath, dtype="<f4").reshape(man["rows"], man["D"])
    return man, K, base


def rows_for_arm(arm, man, K, base, seed):
    """(rows[1054, D] float32) for this arm+seed, scale policy applied."""
    scale = float(man["frozenScale"])
    if arm == "kernel":
        return K * scale
    if arm == "shuffled":
        entry = next(e for e in man["shuffled"] if e["seed"] == seed)
        return K[entry["perm"]] * scale
    if arm == "random":
        entry = next(e for e in man["randomFrozen"] if e["seed"] == seed)
        rpath = os.path.join(base, entry["file"])
        if sha256_file(rpath) != entry["sha256"]:
            raise SystemExit(f"ERR_TABLES: {rpath} sha256 != manifest pin")
        return np.fromfile(rpath, dtype="<f4").reshape(man["rows"], man["D"])
    raise SystemExit(f"ERR_ARM: {arm}")


def batches(shard, batch_size, n_steps, seed):
    """Deterministic seed-paired schedule (e1 pattern, e4 labels)."""
    if shard.n_windows < batch_size:
        raise SystemExit(f"ERR_DATA: {shard.n_windows} windows < batch size {batch_size}")
    step = 0
    epoch = 0
    while step < n_steps:
        perm = det_permutation(f"e4/batches/{seed}/epoch{epoch}", shard.n_windows)
        for i in range(0, shard.n_windows - batch_size + 1, batch_size):
            if step >= n_steps:
                return
            xs, ys = zip(*(shard.window(w) for w in perm[i:i + batch_size]))
            yield step, torch.stack(xs), torch.stack(ys)
            step += 1
        epoch += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e1-ckpt", required=True, help="poc/e1 ckpt-kernel-frozen-seedS-100pct.pt")
    ap.add_argument("--e1-data", required=True, help="poc/e1 build_data.py output dir (vocab.json)")
    ap.add_argument("--e4-data", required=True, help="build_emission.py output dir")
    ap.add_argument("--tables", required=True, help="e4 vector-tables manifest json")
    ap.add_argument("--arm", required=True, choices=ARMS)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lr", type=float, required=True)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--total-tokens", type=int, default=10_000_000)
    ap.add_argument("--weight-decay", type=float, default=0.1)
    ap.add_argument("--warmup-frac", type=float, default=0.05)
    ap.add_argument("--log-every", type=int, default=25)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--authored-row-tol", type=float, default=0.0,
                    help="0 = table-derived authored rows must equal the E1 rows "
                         "bit-exactly (default, fail closed); >0 = allow and record")
    args = ap.parse_args()
    device = args.device if args.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)  # library-level; substantive draws are labelled/seeded
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()

    # ---- artifacts + cross-pins (fail closed) -------------------------------
    with open(os.path.join(args.e4_data, "e4-vocab.json")) as f:
        vocab = json.load(f)
    if vocab.get("artifact") != "e4-vocab":
        raise SystemExit("ERR_ARTIFACT: e4-vocab.json missing/invalid")
    e1_vocab_path = os.path.join(args.e1_data, "vocab.json")
    if sha256_file(e1_vocab_path) != vocab["baseVocab"]["sha256"]:
        raise SystemExit("ERR_VOCAB_PIN: e4 shards were built against a DIFFERENT e1 vocab "
                         f"({e1_vocab_path} sha != e4-vocab baseVocab.sha256)")
    V = vocab["baseVocab"]["size"]
    V2 = vocab["vocabSize"]
    emit_id = vocab["emitId"]
    if emit_id != V:
        raise SystemExit("ERR_VOCAB: EMIT must be the first appended token")
    candidate_ids = list(vocab["candidateIds"])

    ck = torch.load(args.e1_ckpt, map_location="cpu", weights_only=False)
    if ck.get("arm") != "kernel-frozen" or ck.get("tag") != "100pct":
        raise SystemExit(f"ERR_BASE: E4 fine-tunes the E1 kernel-frozen 100pct checkpoint, "
                         f"got arm={ck.get('arm')} tag={ck.get('tag')}")
    if ck.get("seed") != args.seed:
        raise SystemExit(f"ERR_BASE: checkpoint seed {ck.get('seed')} != --seed {args.seed} "
                         "(Common rule 1 pairing)")
    if ck["vocabSize"] != V:
        raise SystemExit(f"ERR_VOCAB: e1 ckpt vocab {ck['vocabSize']} != e4 base vocab {V}")
    cfg = ck["config"]
    init_std = cfg["init_std"]

    man, K, tbase = load_tables(args.tables, cfg["d_model"], len(candidate_ids))
    # manifest row order (authored alphabetical, then synthetic) -> token ids
    tids = [vocab["conceptTokenIds"][s] for s in man["slugs"]]
    if sorted(tids) != sorted(candidate_ids):
        raise SystemExit("ERR_TABLES: manifest slugs do not cover the candidate set")
    authored_pos = [i for i, s in enumerate(man["slugs"]) if not s.startswith("e4-")]
    synth_pos = [i for i, s in enumerate(man["slugs"]) if s.startswith("e4-")]
    if len(authored_pos) != ck["conceptHi"] - ck["conceptLo"]:
        raise SystemExit("ERR_TABLES: authored count mismatch vs e1 concept rows")

    # ---- model surgery: V -> V2, copy everything else bit-exact -------------
    model = GPT(V2, cfg["d_model"], cfg["n_layer"], cfg["n_head"], cfg["d_ff"], cfg["seq_len"])
    sd = dict(ck["model"])
    old_wte = sd.pop("wte.weight")
    missing, unexpected = model.load_state_dict(sd, strict=False)
    if list(missing) != ["wte.weight"] or unexpected:
        raise SystemExit(f"ERR_SURGERY: unexpected state-dict shape (missing={missing}, "
                         f"unexpected={unexpected})")
    gen = torch.Generator().manual_seed(args.seed)  # arm-INDEPENDENT appended-row init
    with torch.no_grad():
        model.wte.weight[:V] = old_wte
        appended = torch.normal(0.0, init_std, (V2 - V, cfg["d_model"]), generator=gen)
        model.wte.weight[V:] = appended
    emit_row_init = model.wte.weight[emit_id].detach().clone()

    rows = rows_for_arm(args.arm, man, K, tbase, args.seed)
    rows_t = torch.from_numpy(np.ascontiguousarray(rows))
    tids_t = torch.tensor(tids, dtype=torch.long)

    # authored-row consistency gate (kernel arm): the table-derived rows must
    # reproduce the E1 checkpoint's frozen kernel rows; the E1 rows are KEPT.
    authored_diff = None
    if args.arm == "kernel":
        expect = rows_t[authored_pos]
        have = old_wte[torch.tensor([tids[i] for i in authored_pos], dtype=torch.long)]
        authored_diff = float((expect - have).abs().max())
        if not torch.equal(expect, have):
            if authored_diff > args.authored_row_tol:
                raise SystemExit(
                    f"ERR_AUTHORED_ROWS: e4 kernel table x frozenScale differs from the E1 "
                    f"checkpoint's frozen rows (maxAbsDiff={authored_diff:.3e} > tol "
                    f"{args.authored_row_tol}) — same encoder pin should be bit-identical")
            print(f"WARNING: authored rows differ (maxAbsDiff={authored_diff:.3e}) — "
                  "within --authored-row-tol, recorded in summary")
        with torch.no_grad():
            model.wte.weight[tids_t[synth_pos]] = rows_t[synth_pos]
    else:
        with torch.no_grad():
            model.wte.weight[tids_t] = rows_t
    model.to(device)

    # ---- freezing (e1 discipline, index-masked: rows are non-contiguous) ----
    frozen_idx = torch.tensor(sorted(tids), dtype=torch.long, device=device)
    frozen_snapshot = model.wte.weight.detach()[frozen_idx].clone()

    def assert_frozen(where):
        if not torch.equal(model.wte.weight.detach()[frozen_idx], frozen_snapshot):
            raise SystemExit(f"ERR_FROZEN_ROWS_MOVED at {where} — freezing mask failed; "
                             "run is INVALID")

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

    tokens_per_step = args.batch_size * cfg["seq_len"]
    n_steps = max(1, args.total_tokens // tokens_per_step)
    warmup = max(1, int(n_steps * args.warmup_frac))

    def lr_at(step):
        if step < warmup:
            return args.lr * (step + 1) / warmup
        p = (step - warmup) / max(1, n_steps - warmup)
        return args.lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * p)))

    shard = Shard(os.path.join(args.e4_data, f"seed{args.seed}", "train.bin"), cfg["seq_len"])
    run_id = f"e4-{args.arm}-seed{args.seed}"
    log = open(os.path.join(args.out, f"train-{run_id}.jsonl"), "w")

    amp = device == "cuda"
    model.train()
    last_loss = None
    for step, x, y in batches(shard, args.batch_size, n_steps, args.seed):
        for g in opt.param_groups:
            g["lr"] = lr_at(step)
        x, y = x.to(device), y.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=amp):
            logits = model(x)
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)), y.view(-1))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        if model.wte.weight.grad is not None:
            # optimizer-state masking: frozen rows never see a nonzero grad,
            # so Adam moments stay 0 and the AdamW update is exactly 0
            # (embeddings are in the wd=0 group).
            model.wte.weight.grad[frozen_idx] = 0.0
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        last_loss = float(loss.item())
        if step % args.log_every == 0:
            assert_frozen(f"step {step}")
            log.write(json.dumps({"step": step, "loss": last_loss, "lr": lr_at(step),
                                  "tokens": step * tokens_per_step,
                                  "elapsed": time.time() - t0}) + "\n")
            log.flush()
    assert_frozen("end of fine-tuning")
    log.close()

    ckpt_path = os.path.join(args.out, f"ckpt-{run_id}-final.pt")
    torch.save({
        "experiment": "E4", "arm": args.arm, "seed": args.seed,
        "model": model.state_dict(), "config": cfg,
        "vocabSize": V2, "baseVocabSize": V, "emitId": emit_id,
        "conceptLo": ck["conceptLo"], "conceptHi": ck["conceptHi"],
        "frozenTokenIds": sorted(tids),
        "emitRowInit": emit_row_init,
        "e1Ckpt": {"path": os.path.abspath(args.e1_ckpt),
                   "sha256": sha256_file(args.e1_ckpt)},
        "tablesManifestSha256": sha256_file(args.tables),
        "mockTables": bool(man.get("mock")),
        "lr": args.lr, "steps": n_steps, "totalTokens": n_steps * tokens_per_step,
        "frozen": True, "frozenRowsBitIdentical": True,
        "authoredRowsMaxAbsDiff": authored_diff,
    }, ckpt_path)

    summary = {
        "experiment": "E4", "arm": args.arm, "seed": args.seed, "lr": args.lr,
        "steps": n_steps, "tokens": n_steps * tokens_per_step,
        "vocabSize": V2, "device": device, "finalTrainLoss": last_loss,
        "frozen": True, "frozenRowsBitIdentical": True,
        "authoredRowsMaxAbsDiff": authored_diff,
        "mockTables": bool(man.get("mock")),
        "wallSeconds": time.time() - t0,
    }
    with open(os.path.join(args.out, f"summary-{run_id}.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: summary[k] for k in
                      ["arm", "seed", "lr", "steps", "frozenRowsBitIdentical"]}))
    print(f"[{time.time()-t0:.0f}s] done -> {ckpt_path}")


if __name__ == "__main__":
    main()
