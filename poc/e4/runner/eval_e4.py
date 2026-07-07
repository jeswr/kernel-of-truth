#!/usr/bin/env python3
"""E4 evaluation (docs/poc-design.md E4 rev 2; bead kernel-of-truth-hkp).

Scores ONE fine-tuned E4 checkpoint on the seed-independent eval.jsonl
emitted by poc/e4/pipeline/build_emission.py, exactly per the holdout
manifest's statistics spec (BLOCKER 3):

  - every eval item ends at the EMIT marker; the model's next-token logits
    are RESTRICTED to the 1,054 candidate concept-token ids (e4-vocab.json
    `candidateIds`); rank of the true target within that candidate set;
  - top-1 / top-10 accuracy aggregated per tier (tier2, tier1,
    seen-heldgloss) and per compositional subset (sharesStructureWithSeen
    true = "shared" / false = "novel") within the held-out tiers;
  - per-item ranks are emitted so stats_e4.py can pool exact Fisher counts.

Chance: top-1 = 1/1054, top-10 = 10/1054 (the manifest's "10/|C|").
"""

import argparse
import json
import os
import sys

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
E4_DIR = os.path.dirname(HERE)
E1_DIR = os.path.join(os.path.dirname(E4_DIR), "e1")
sys.path.insert(0, os.path.join(E1_DIR, "pipeline"))
sys.path.insert(0, os.path.join(E1_DIR, "train"))
from train_e1 import GPT  # noqa: E402  (read-only reuse)


def acc(rows, key):
    return (sum(1 for r in rows if r["rank"] < key) / len(rows)) if rows else None


def tier_aggregate(rows, with_composition):
    out = {"n": len(rows), "top1": acc(rows, 1), "top10": acc(rows, 10)}
    if with_composition:
        shared = [r for r in rows if r["sharesStructureWithSeen"] is True]
        novel = [r for r in rows if r["sharesStructureWithSeen"] is False]
        out["composition"] = {
            "shared": {"n": len(shared), "top1": acc(shared, 1), "top10": acc(shared, 10)},
            "novel": {"n": len(novel), "top1": acc(novel, 1), "top10": acc(novel, 10)},
        }
    return out


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True, help="finetune_e4.py output checkpoint")
    ap.add_argument("--e4-data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()
    device = args.device if args.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")

    ck = torch.load(args.ckpt, map_location=device, weights_only=False)
    if ck.get("experiment") != "E4":
        raise SystemExit("ERR_CKPT: not an E4 fine-tuned checkpoint")
    cfg = ck["config"]
    model = GPT(ck["vocabSize"], cfg["d_model"], cfg["n_layer"], cfg["n_head"],
                cfg["d_ff"], cfg["seq_len"])
    model.load_state_dict(ck["model"])
    model.to(device).eval()

    with open(os.path.join(args.e4_data, "e4-vocab.json")) as f:
        vocab = json.load(f)
    candidate_ids = list(vocab["candidateIds"])
    emit_id = vocab["emitId"]
    if emit_id != ck["emitId"]:
        raise SystemExit("ERR_VOCAB: eval data emit id != checkpoint emit id")
    cand = torch.tensor(candidate_ids, device=device)
    cand_pos = {tid: i for i, tid in enumerate(candidate_ids)}

    items = [json.loads(l) for l in open(os.path.join(args.e4_data, "eval.jsonl"))]
    results = []
    for it in items:
        ids = it["ids"]
        if ids[-1] != emit_id:
            raise SystemExit("ERR_EVAL: item does not end at EMIT")
        ids = ids[-cfg["seq_len"]:]
        x = torch.tensor([ids], device=device)
        logits = model(x)[0, -1]
        scores = logits[cand]
        order = torch.argsort(scores, descending=True)
        rank = int((order == cand_pos[it["target"]]).nonzero()[0].item())
        results.append({"conceptId": it["conceptId"], "slug": it["slug"],
                        "variant": it["variant"], "tier": it["tier"],
                        "sharesStructureWithSeen": it["sharesStructureWithSeen"],
                        "rank": rank})

    tiers = {}
    for tier in ("tier2", "tier1", "seen-heldgloss"):
        rows = [r for r in results if r["tier"] == tier]
        tiers[tier] = tier_aggregate(rows, with_composition=tier in ("tier1", "tier2"))

    out = {
        "experiment": "E4", "arm": ck["arm"], "seed": ck["seed"],
        "ckpt": os.path.basename(args.ckpt),
        "frozenRowsBitIdentical": ck.get("frozenRowsBitIdentical"),
        "candidateSetSize": len(candidate_ids),
        "chance": {"top1": 1.0 / len(candidate_ids), "top10": 10.0 / len(candidate_ids)},
        "tiers": tiers,
        "items": results,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({"arm": ck["arm"], "seed": ck["seed"],
                      "tier2Top1": tiers["tier2"]["top1"],
                      "tier1Top1": tiers["tier1"]["top1"],
                      "seenHeldglossTop1": tiers["seen-heldgloss"]["top1"]}))


if __name__ == "__main__":
    main()
