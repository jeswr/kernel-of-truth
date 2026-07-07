#!/usr/bin/env python3
"""E1 evaluation suite (docs/poc-design.md E1; bead kernel-of-truth-bk0).

Runs ALL pre-registered metrics for ONE checkpoint (so the identical code
path produces the step-0 circularity baselines — MAJOR 5 — and the 50%/100%
looks):

  1. CONCEPT CLOZE (primary instrument): candidate-restricted argmax over the
     54 concept-token logits at the {c} slot of each definitional template
     type x concept item (16 x 54 grid). The PRIMARY endpoint is accuracy on
     HELD-OUT template types x concepts attested in all seeds (MAJOR 6);
     dev-type and all-54 aggregates are reported as descriptive.
  2. CONCEPT-SLICE VAL LOSS/PPL + overall val PPL (M0a consequence: ~8.5% of
     tokens are substituted specials, ~1.6% concept tokens — corpus-wide
     metrics would dilute the signal; the slice is computed at positions
     whose TARGET is a concept token). Feeds the pre-registered 2%
     PPL-saturation uninformativeness rule.
  3. MID-LAYER PROBE (secondary; circularity guard): linear softmax probe on
     the hidden state after block n_layer//2, read at the pre-registered
     NON-concept position (final word token of the stimulus sentence),
     54-way concept classification; trained on probe-train template types,
     tested on probe-test types.

Fail-closed: any eval-instrument token missing from the vocab is an error
(build_data.py force-includes template+gloss tokens, so a miss means
mismatched artifacts).
"""

import argparse
import json
import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
E1_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(E1_DIR, "pipeline"))
sys.path.insert(0, os.path.join(E1_DIR, "train"))
from kernel_mapper import load_mapper  # noqa: E402
from train_e1 import GPT, Shard, val_losses  # noqa: E402


def load_model(ckpt_path, device):
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    c = ck["config"]
    model = GPT(ck["vocabSize"], c["d_model"], c["n_layer"], c["n_head"],
                c["d_ff"], c["seq_len"])
    model.load_state_dict(ck["model"])
    model.to(device).eval()
    return model, ck


def to_ids(mapper, vocab_ids, text):
    """Template/gloss text -> token ids (word norms + punct surfaces); fail closed on <unk>."""
    ids = []
    for t in mapper.tokenize(text):
        tok = t.norm if t.is_word else t.surface
        if not tok:
            continue
        i = vocab_ids.get(tok)
        if i is None or i == 0:
            raise SystemExit(f"ERR_EVAL_OOV: '{tok}' from '{text[:60]}...' not in vocab")
        ids.append(i)
    return ids


@torch.no_grad()
def cloze(model, mapper, vocab_ids, templates, concept_ids, seq_len, device):
    """Per (definitional type, concept): candidate-restricted rank of the true token."""
    results = []
    cand = torch.tensor(concept_ids, device=device)
    for ti, frame in enumerate(templates["definitional"]["types"]):
        for ci, c in enumerate(templates["concepts"]):
            text = frame.replace("{gloss}", c["gloss"])
            prefix = text[:text.index("{c}")]
            ids = to_ids(mapper, vocab_ids, prefix)
            ids = ids[-(seq_len - 1):]
            x = torch.tensor([ids], device=device)
            logits = model(x)[0, -1]
            scores = logits[cand]
            order = torch.argsort(scores, descending=True)
            rank = int((cand[order] == concept_ids[ci]).nonzero()[0].item())
            results.append({"type": ti, "concept": c["slug"], "rank": rank,
                            "correct": rank == 0})
    return results


def cloze_aggregates(results, templates, attested):
    held = set(templates["definitional"]["split"]["heldOut"])
    dev = set(templates["definitional"]["split"]["dev"])
    att = set(attested)

    def acc(rows):
        return sum(r["correct"] for r in rows) / len(rows) if rows else None

    return {
        "heldOutAccAttested": acc([r for r in results if r["type"] in held and r["concept"] in att]),
        "devAccAttested": acc([r for r in results if r["type"] in dev and r["concept"] in att]),
        "heldOutAccAll54": acc([r for r in results if r["type"] in held]),
        "devAccAll54": acc([r for r in results if r["type"] in dev]),
        "attestedCount": len(att),
        "chance": 1.0 / 54,
    }


@torch.no_grad()
def probe_reps(model, mapper, vocab_ids, templates, concept_ids, device):
    """Mid-layer reps at the final WORD token of each probe stimulus."""
    mid = max(0, len(model.blocks) // 2 - 1)  # state after block n_layer//2
    xs = {"train": [], "test": []}
    ys = {"train": [], "test": []}
    for ci, c in enumerate(templates["concepts"]):
        bank = c["bank"]
        frames = templates["probe"]["types"][bank]
        split = templates["probe"]["split"][bank]
        for part in ("train", "test"):
            for ti in split[part]:
                frame = frames[ti]
                before, after = frame.split("{c}")
                ids = to_ids(mapper, vocab_ids, before) + [concept_ids[ci]] \
                    + to_ids(mapper, vocab_ids, after)
                # pre-registered position: last WORD token (skip trailing punct)
                after_toks = [t.norm if t.is_word else t.surface for t in mapper.tokenize(after)]
                n_trailing_punct = 0
                for tk in reversed(after_toks):
                    if tk and not tk.isalpha():
                        n_trailing_punct += 1
                    else:
                        break
                pos = len(ids) - 1 - n_trailing_punct
                x = torch.tensor([ids], device=device)
                h = model.hidden_states(x)[mid][0, pos]
                xs[part].append(h)
                ys[part].append(ci)
    return ({p: torch.stack(xs[p]) for p in xs}, {p: torch.tensor(ys[p]) for p in ys}, mid)


def probe_fit(xs, ys, n_classes, device, steps=300, lr=0.05, seed=0):
    """Full-batch softmax regression (standardised inputs), fixed seed."""
    g = torch.Generator().manual_seed(seed)
    mu, sd = xs["train"].mean(0), xs["train"].std(0) + 1e-6
    xtr = ((xs["train"] - mu) / sd).to(device)
    xte = ((xs["test"] - mu) / sd).to(device)
    ytr, yte = ys["train"].to(device), ys["test"].to(device)
    W = torch.zeros(xtr.shape[1], n_classes, device=device, requires_grad=True)
    b = torch.zeros(n_classes, device=device, requires_grad=True)
    with torch.no_grad():
        W.copy_(torch.normal(0, 0.01, W.shape, generator=g).to(device))
    opt = torch.optim.Adam([W, b], lr=lr)
    for _ in range(steps):
        loss = torch.nn.functional.cross_entropy(xtr @ W + b, ytr) + 1e-3 * W.pow(2).sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        tr = float(((xtr @ W + b).argmax(1) == ytr).float().mean())
        te = float(((xte @ W + b).argmax(1) == yte).float().mean())
    return {"trainAcc": tr, "testAcc": te, "chance": 1.0 / n_classes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--artifact-dir", default=os.path.join(E1_DIR, "inputs"))
    ap.add_argument("--device", default="auto")
    ap.add_argument("--val-batches", type=int, default=20)
    ap.add_argument("--per-item", action="store_true", help="include the per-item cloze table")
    args = ap.parse_args()
    device = args.device if args.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")

    model, ck = load_model(args.ckpt, device)
    mapper = load_mapper(os.path.join(args.artifact_dir, "mapper-lexicon.json"))
    with open(os.path.join(args.artifact_dir, "cloze-templates.json")) as f:
        templates = json.load(f)
    with open(os.path.join(args.data, "vocab.json")) as f:
        vocab = json.load(f)
    with open(os.path.join(args.data, "meta.json")) as f:
        meta = json.load(f)
    vocab_ids = {t: i for i, t in enumerate(vocab["tokens"])}
    sp = vocab["specials"]
    concept_ids = list(range(sp["conceptBase"], sp["conceptBase"] + sp["conceptCount"]))
    attested = meta["attestedInAllSeeds"]

    results = cloze(model, mapper, vocab_ids, templates, concept_ids,
                    ck["config"]["seq_len"], device)
    agg = cloze_aggregates(results, templates, attested)

    val_shard = Shard(os.path.join(args.data, f"seed{ck['seed']}", "val.bin"),
                      ck["config"]["seq_len"])
    ppl = val_losses(model, val_shard, 32, args.val_batches,
                     ck["conceptLo"], ck["conceptHi"], device)

    xs, ys, mid = probe_reps(model, mapper, vocab_ids, templates, concept_ids, device)
    probe = probe_fit(xs, ys, len(concept_ids), device)
    probe["midLayerStateIndex"] = mid
    probe["positionRule"] = "final word token of the stimulus (non-concept position)"

    out = {
        "arm": ck["arm"], "seed": ck["seed"], "tag": ck["tag"], "step": ck["step"],
        "ckpt": os.path.basename(args.ckpt),
        "frozenRowsBitIdentical": ck.get("frozenRowsBitIdentical"),
        "cloze": agg,
        "ppl": ppl,
        "probe": probe,
    }
    if args.per_item:
        out["clozePerItem"] = results
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"arm": ck["arm"], "seed": ck["seed"], "tag": ck["tag"],
                      "heldOutAccAttested": agg["heldOutAccAttested"],
                      "probeTestAcc": probe["testAcc"],
                      "conceptSlicePpl": ppl["conceptSlicePpl"]}))


if __name__ == "__main__":
    main()
