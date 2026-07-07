#!/usr/bin/env python3
"""E9-defl — deflationary control kernel on the E5 instrument (poc/e9/README.md,
NEW pre-registration 2026-07-07; bead kernel-of-truth-xj2).

The ONLY thing the GPU runs. Imports poc/e5/runner/e5_runner.py READ-ONLY
(the poc/e4-reuses-stats_e1 precedent) for the entire instrument — model,
tokenizer, sequence construction, adapter training, scoring, exact
statistics — and runs 3 arms x 5 paired seeds on it:

    true-kernel (E5 table) / shuffled-kernel (E5 derangements) /
    defl-kernel (structure-matched semantically-scrambled explications)

    python3 e9_runner.py --inputs-dir ../inputs --e5-inputs-dir ../../e5/inputs \
        --out-dir /tmp/e9 --device cuda
    python3 e9_runner.py ... --mock       # CPU mechanics check (tiny model)

Statistics and outcome labels are quoted VERBATIM from inputs/e9-manifest.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
E5_RUNNER_DIR = _HERE.parents[1] / "e5" / "runner"
sys.path.insert(0, str(E5_RUNNER_DIR))
import e5_runner as e5  # noqa: E402  READ-ONLY reuse of the E5 instrument

ARMS = ["true", "shuffled", "defl"]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def holm(pvals: dict) -> dict:
    """Holm step-down adjusted p-values."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 0.0
    for rank, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - rank) * p))
        adj[k] = running
    return adj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs-dir", required=True)
    ap.add_argument("--e5-inputs-dir", default=None,
                    help="default: <inputs-dir>/../../e5/inputs")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--max-hours", type=float, default=3.6)
    args = ap.parse_args()
    t0 = time.time()
    os.makedirs(args.out_dir, exist_ok=True)
    e5_inputs = args.e5_inputs_dir or os.path.normpath(
        os.path.join(args.inputs_dir, "..", "..", "e5", "inputs"))

    import torch
    torch.manual_seed(e5.SEED_BASE)
    if args.device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    # ---- E9 manifest + fail-closed pins over EVERY consumed file -------------
    with open(os.path.join(args.inputs_dir, "e9-manifest.json")) as f:
        e9man = json.load(f)
    pins = e9man["pins"]
    checks = {
        "e5ManifestSha256": os.path.join(e5_inputs, "e5-manifest.json"),
        "e5ItemsSha256": os.path.join(e5_inputs, "e5-items.json"),
        "e5ConceptsSha256": os.path.join(e5_inputs, "e5-concepts.json"),
        "e5VectorTablesManifestSha256": os.path.join(e5_inputs, "vector-tables-manifest.json"),
        "e5KernelF32Sha256": os.path.join(e5_inputs, "vectors", "kernel-jl576.f32"),
        "deflConceptsSha256": os.path.join(args.inputs_dir, "defl-concepts.json"),
        "deflTablesManifestSha256": os.path.join(args.inputs_dir, "defl-tables-manifest.json"),
        "deflF32Sha256": os.path.join(args.inputs_dir, "vectors", "defl-jl576.f32"),
        "e5CommittedSummarySha256": os.path.join(args.inputs_dir, "e5-committed-summary.json"),
    }
    for key, path in checks.items():
        if sha256_file(path) != pins[key]:
            raise SystemExit(f"ERR_PIN: {key}: {path} sha != e9-manifest pin")

    # ---- E5 instrument, loaded by the E5 loader (its own gates re-fire) ------
    data = e5.load_inputs(e5_inputs)
    manifest, items = data["manifest"], data["items"]
    frame = manifest["frame"]
    tr_spec = manifest["training"]
    seeds = e5.MOCK_SEEDS if args.mock else e9man["seeds"]
    steps = e5.MOCK_STEPS if args.mock else tr_spec["steps"]
    sweep_steps = e5.MOCK_SWEEP_STEPS if args.mock else tr_spec["sweepSteps"]
    sweep_lrs = tr_spec["lrSweep"][:2] if args.mock else tr_spec["lrSweep"]
    batch_size = e5.MOCK_BATCH if args.mock else tr_spec["batch"]
    warmup = 5 if args.mock else tr_spec["warmupSteps"]
    clip = tr_spec["gradClip"]
    seen_eval = items["seenEval"][:e5.MOCK_SEEN_EVAL_N] if args.mock else items["seenEval"]
    nonce_eval = items["nonceEval"]
    label = "MOCK" if args.mock else "FULL"

    with open(os.path.join(args.inputs_dir, "defl-tables-manifest.json")) as f:
        deflman = json.load(f)
    if deflman["ids"] != data["vecman"]["ids"]:
        raise SystemExit("ERR_ROWS: defl table row order != E5 ids")
    defl_np = np.fromfile(
        os.path.join(args.inputs_dir, "vectors", "defl-jl576.f32"), dtype="<f4"
    ).reshape(deflman["rows"], deflman["d"])

    def log(msg: str) -> None:
        print(f"[e9 {time.time() - t0:7.1f}s] {msg}", flush=True)

    log(f"mode={label} device={args.device} seeds={seeds} steps={steps} "
        f"sweep={sweep_lrs}@{sweep_steps} batch={batch_size} arms={ARMS}")

    # ---- model (E5 machinery verbatim) ----------------------------------------
    if args.mock:
        texts = ([frame["prefix"], frame["suffix"]]
                 + [frame["candidatePrefix"] + t["gloss"] for t in items["training"]]
                 + [frame["candidatePrefix"] + c["gloss"] for it in items["seenEval"] + nonce_eval
                    for c in it["candidates"]])
        model, tok = e5.build_mock_model(texts, args.device)
    else:
        model, tok = e5.build_model(False, args.device, manifest["model"]["dModel"])
    e5.PAD_ID = tok.pad_token_id if tok.pad_token_id is not None else tok.bos_token_id
    embed_weight = model.get_input_embeddings().weight
    param_checksum_before = float(sum(p.abs().sum().item() for p in model.parameters()))

    train_all = [(e5.build_seq(tok, frame, t["gloss"]), t["row"], t["val"])
                 for t in items["training"]]
    train_seqs = [s for s, _, v in train_all if not v]
    train_rows = [r for _, r, v in train_all if not v]
    val_seqs = [s for s, _, v in train_all if v]
    val_rows = [r for _, r, v in train_all if v]
    seen_cache = {(ii, ci): e5.build_seq(tok, frame, c["gloss"])
                  for ii, it in enumerate(seen_eval) for ci, c in enumerate(it["candidates"])}
    nonce_cache = {(ii, ci): e5.build_seq(tok, frame, c["gloss"])
                   for ii, it in enumerate(nonce_eval) for ci, c in enumerate(it["candidates"])}
    log(f"sequences: {len(train_seqs)} train / {len(val_seqs)} val / "
        f"{len(seen_eval)} seen-eval / {len(nonce_eval)} nonce-eval")

    kernel = torch.tensor(data["kernel"], dtype=torch.float32, device=args.device)
    defl = torch.tensor(defl_np, dtype=torch.float32, device=args.device)

    def table_for(arm: str, seed: int):
        if arm == "true":
            return kernel
        if arm == "shuffled":
            perm = torch.tensor(data["perms"][seed], dtype=torch.long, device=args.device)
            return kernel[perm]
        if arm == "defl":
            return defl
        raise ValueError(arm)

    results: dict = {"armSeed": {}, "lrSelection": {}}

    # ---- LR selection (Common rule 5, per arm on seed 0) ----------------------
    for arm in ARMS:
        best = None
        for lr in sweep_lrs:
            if (time.time() - t0) / 3600 > args.max_hours:
                raise SystemExit(f"ERR_TIME_BUDGET: exceeded {args.max_hours}h during sweep")
            log(f"sweep arm={arm} lr={lr}")
            table_t = table_for(arm, seeds[0])
            adapter, _, _ = e5.train_adapter(model, embed_weight, table_t, train_seqs,
                                             train_rows, seeds[0], lr, sweep_steps,
                                             batch_size, warmup, clip, args.device, log)
            vce = e5.mean_ce(model, embed_weight, adapter, table_t, val_seqs, val_rows,
                             args.device)
            log(f"  arm={arm} lr={lr} valCE={vce:.4f}")
            if best is None or vce < best[1] - 1e-12:
                best = (lr, vce)
        results["lrSelection"][arm] = {"lr": best[0], "valCE": best[1],
                                       "rule": tr_spec["lrRule"], "swept": sweep_lrs,
                                       "sweepSteps": sweep_steps}
        log(f"selected lr={best[0]} for arm={arm}")

    # ---- full runs -------------------------------------------------------------
    for arm in ARMS:
        lr = results["lrSelection"][arm]["lr"]
        for seed in seeds:
            if (time.time() - t0) / 3600 > args.max_hours:
                raise SystemExit(f"ERR_TIME_BUDGET before arm={arm} seed={seed} (partials saved)")
            log(f"train arm={arm} seed={seed} lr={lr}")
            table_t = table_for(arm, seed)
            adapter0, _sigma0 = e5.init_adapter(embed_weight, table_t.shape[1], seed, args.device)
            step0_nonce = e5.score_eval(model, embed_weight, adapter0, table_t, nonce_eval,
                                        nonce_cache, args.device)
            adapter, sigma, curve = e5.train_adapter(model, embed_weight, table_t, train_seqs,
                                                     train_rows, seed, lr, steps, batch_size,
                                                     warmup, clip, args.device, log)
            vce = e5.mean_ce(model, embed_weight, adapter, table_t, val_seqs, val_rows,
                             args.device)
            seen_res = e5.score_eval(model, embed_weight, adapter, table_t, seen_eval,
                                     seen_cache, args.device)
            nonce_res = e5.score_eval(model, embed_weight, adapter, table_t, nonce_eval,
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
                json.dump({"seen": seen_res, "nonce": nonce_res, "step0Nonce": step0_nonce}, f)
            np.savez(os.path.join(args.out_dir, f"adapter-{key}.npz"),
                     W=adapter.weight.detach().cpu().numpy().astype(np.float32),
                     b=adapter.bias.detach().cpu().numpy().astype(np.float32))
            log(f"  arm={arm} seed={seed}: seenAcc={results['armSeed'][key]['seenAcc']:.4f} "
                f"nonceAcc={results['armSeed'][key]['nonceAcc']:.4f} valCE={vce:.4f}")

    param_checksum_after = float(sum(p.abs().sum().item() for p in model.parameters()))
    if param_checksum_before != param_checksum_after:
        raise SystemExit("ERR_FROZEN: model parameter checksum changed")

    # ---- pre-registered statistics ----------------------------------------------
    stats_spec = e9man["statistics"]
    nonces = sorted({it["concept"] for it in nonce_eval})
    items_per_nonce = len(nonce_eval) // len(nonces)

    _cc: dict = {}

    def correct_counts(arm: str, seed: int) -> dict:
        if (arm, seed) not in _cc:
            with open(os.path.join(args.out_dir, f"eval-items-{arm}-seed{seed}.json")) as f:
                recs = json.load(f)["nonce"]
            out = {c: 0 for c in nonces}
            for r in recs:
                out[r["concept"]] += 1 if r["correct"] else 0
            _cc[(arm, seed)] = out
        return _cc[(arm, seed)]

    def nonce_int_diffs(arm_a: str, arm_b: str) -> list:
        diffs = []
        for c in nonces:
            dj = 0
            for s in seeds:
                dj += correct_counts(arm_a, s)[c] - correct_counts(arm_b, s)[c]
            diffs.append(dj)
        return diffs

    def seed_mean_diffs(arm_a: str, arm_b: str) -> list:
        out = []
        for s in seeds:
            ta = sum(correct_counts(arm_a, s).values())
            tb = sum(correct_counts(arm_b, s).values())
            out.append((ta - tb) / (len(nonces) * items_per_nonce))
        return out

    denom = len(seeds) * items_per_nonce
    d_true_defl = nonce_int_diffs("true", "defl")
    p_primary = e5.exact_signflip_p_int(d_true_defl)
    mean_primary = float(np.mean([d / denom for d in d_true_defl]))

    d_defl_shuf = nonce_int_diffs("defl", "shuffled")
    p_s1 = e5.exact_signflip_p_int(d_defl_shuf)
    mean_s1 = float(np.mean([d / denom for d in d_defl_shuf]))
    sm_true_defl = seed_mean_diffs("true", "defl")
    p_s2 = e5.exact_signflip_p_float(sm_true_defl)
    holm_adj = holm({"S1": p_s1, "S2": p_s2})

    gate_per_seed = []
    for seed in seeds:
        r = results["armSeed"][f"true-seed{seed}"]
        p = e5.binom_sf_geq(r["seenCorrect"], r["seenN"], manifest["scoring"]["chance"])
        gate_per_seed.append({"seed": seed, "seenCorrect": r["seenCorrect"],
                              "seenN": r["seenN"], "p": p, "pass": p < 0.05})
    n_gate_pass = sum(g["pass"] for g in gate_per_seed)
    gate_needed = max(len(seeds) - 1, 1)
    gate_ok = n_gate_pass >= gate_needed

    primary_reject = bool(p_primary < 0.05 and mean_primary > 0)
    s1_reject = bool(p_s1 < 0.05 and mean_s1 > 0)  # raw, per pinned outcome labels
    if not gate_ok:
        outcome = "INSTRUMENT-INVALID"
    elif primary_reject:
        outcome = "PASS"
    elif s1_reject:
        outcome = "DEFLATED"
    else:
        outcome = "AMBIGUOUS-NULL"
    if args.mock:
        outcome = f"MOCK-{outcome}"

    # descriptives: true-vs-shuffled (E5 replication) + recovered fraction + drift
    d_true_shuf = nonce_int_diffs("true", "shuffled")
    sm_true_shuf = seed_mean_diffs("true", "shuffled")
    sm_defl_shuf = seed_mean_diffs("defl", "shuffled")
    recovered = [ds / ts if ts != 0 else float("nan")
                 for ds, ts in zip(sm_defl_shuf, sm_true_shuf)]
    with open(os.path.join(args.inputs_dir, "e5-committed-summary.json")) as f:
        e5sum = json.load(f)
    drift = {}
    for key, v in e5sum["armSeed"].items():
        arm, seedtag = key.split("-seed")
        if int(seedtag) in seeds and f"{key}" in results["armSeed"]:
            drift[key] = {
                "e5NonceAcc": v["nonceAcc"],
                "e9NonceAcc": results["armSeed"][key]["nonceAcc"],
                "delta": results["armSeed"][key]["nonceAcc"] - v["nonceAcc"],
            }

    results.update({
        "outcome": outcome,
        "mode": label,
        "date": e5.utcnow(),
        "device": args.device,
        "torch": torch.__version__,
        "model": manifest["model"]["id"] if not args.mock else "mock-llama",
        "seeds": seeds,
        "pins": pins,
        "spec": e9man["spec"],
        "question": e9man["question"],
        "deflationPrinciple": e9man["deflationPrinciple"],
        "statisticsSpec": stats_spec,
        "primary": {
            "contrast": "true-kernel vs defl-kernel (one-sided, true > defl)",
            "nNonces": len(nonces), "itemsPerNonce": items_per_nonce,
            "intDiffs": d_true_defl, "meanDiff": mean_primary, "p": p_primary,
            "alpha": 0.05, "reject": primary_reject,
        },
        "secondaries": {
            "S1_defl_vs_shuffled": {"intDiffs": d_defl_shuf, "meanDiff": mean_s1,
                                    "p": p_s1, "pHolm": holm_adj["S1"], "reject": s1_reject},
            "S2_seedlevel_true_vs_defl": {"seedMeanDiffs": sm_true_defl, "p": p_s2,
                                          "pHolm": holm_adj["S2"],
                                          "reject": bool(p_s2 < 0.05 and np.mean(sm_true_defl) > 0)},
        },
        "instrumentValidityGate": {
            "rule": stats_spec["instrumentValidityGate"], "perSeed": gate_per_seed,
            "passed": gate_ok, "nPass": n_gate_pass, "needed": gate_needed,
        },
        "descriptive": {
            "true_vs_shuffled": {"intDiffs": d_true_shuf, "seedMeanDiffs": sm_true_shuf,
                                 "meanDiff": float(np.mean([d / denom for d in d_true_shuf]))},
            "recoveredFractionPerSeed": recovered,
            "recoveredFractionPooled":
                float(np.mean(sm_defl_shuf) / np.mean(sm_true_shuf))
                if np.mean(sm_true_shuf) != 0 else float("nan"),
            "driftVsE5Committed": drift,
        },
        "paramChecksum": {"before": param_checksum_before, "after": param_checksum_after},
        "wallClockHours": (time.time() - t0) / 3600,
    })

    suffix = "-mock" if args.mock else ""
    with open(os.path.join(args.out_dir, f"results-e9{suffix}.json"), "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)

    # ---- verdict ------------------------------------------------------------------
    def acc_table(field: str) -> str:
        lines = ["| arm | " + " | ".join(f"seed{s}" for s in seeds) + " |",
                 "|---|" + "---|" * len(seeds)]
        for arm in ARMS:
            vals = [f"{results['armSeed'][f'{arm}-seed{s}'][field]:.4f}" for s in seeds]
            lines.append(f"| {arm} | " + " | ".join(vals) + " |")
        return "\n".join(lines)

    md = [
        f"# E9-defl verdict{' (MOCK — mechanics only, tiny random model)' if args.mock else ''}",
        "",
        f"date: {results['date']}  |  mode: {label}  |  device: {args.device}  |  model: {results['model']}",
        "",
        "**What this is (poc/e9/README.md J1, verbatim):**",
        f"> {e9man['spec']}",
        "",
        f"**Question:** {e9man['question']}",
        f"**Principle:** {e9man['deflationPrinciple']}",
        "",
        "**Pre-registered primary (inputs/e9-manifest.json, verbatim):**",
        f"> {stats_spec['primaryEndpoint']}",
        "",
        "**Pre-registered outcome labels (verbatim):**",
        f"> {stats_spec['outcomes']}",
        "",
        f"## OUTCOME: **{outcome}**",
        "",
        f"- Instrument-validity gate: {n_gate_pass}/{len(seeds)} seeds (need >= {gate_needed}) "
        f"=> {'PASSED' if gate_ok else 'FAILED'}",
        f"- Primary (true vs defl): mean diff {mean_primary:+.4f}, "
        f"one-sided exact sign-flip p = {p_primary:.6g}",
        f"- S1 (defl vs shuffled): mean diff {mean_s1:+.4f}, p = {p_s1:.6g} "
        f"(Holm {holm_adj['S1']:.6g})",
        f"- S2 (seed-level true vs defl): diffs {['%+.4f' % m for m in sm_true_defl]}, "
        f"p = {p_s2:.4f} (Holm {holm_adj['S2']:.4f})",
        f"- Descriptive true vs shuffled (E5 replication): mean diff "
        f"{results['descriptive']['true_vs_shuffled']['meanDiff']:+.4f}",
        f"- Recovered fraction (defl-shuffled)/(true-shuffled), pooled: "
        f"{results['descriptive']['recoveredFractionPooled']:.4f}",
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
        "### Drift vs committed E5 run (descriptive replication datum)",
        "| arm-seed | E5 nonceAcc | E9 nonceAcc | delta |",
        "|---|---|---|---|",
    ] + [
        f"| {k} | {v['e5NonceAcc']:.4f} | {v['e9NonceAcc']:.4f} | {v['delta']:+.4f} |"
        for k, v in sorted(results["descriptive"]["driftVsE5Committed"].items())
    ] + [
        "",
        f"LR selection (Common rule 5): "
        + ", ".join(f"{a}={results['lrSelection'][a]['lr']}" for a in ARMS),
        "",
        f"Scope limits: {e9man['scopeLimits']}",
        "",
    ]
    with open(os.path.join(args.out_dir, f"verdict-e9{suffix}.md"), "w") as f:
        f.write("\n".join(md))
    log(f"OUTCOME: {outcome} (results in {args.out_dir})")


if __name__ == "__main__":
    main()
