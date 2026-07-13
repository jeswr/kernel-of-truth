#!/usr/bin/env python3
"""judge_spotcheck.py -- validate the embedding-clustering against a gpt-5.6-sol
judge on a random ~10-concept sample.

For each sampled concept the judge sees the model glosses (identity hidden,
shuffled, labelled [1..n]) and must group those that express THE SAME definition,
and name the majority/consensus group. We then compare the judge's consensus
group to the embedding clique from consensus.json (Jaccard over the underlying
model set + whether the two agree on each model's in/out membership).

Uses the pinned codex isolated-home pattern (read-only, subscription auth => $0).
$0, no git.
"""
import argparse
import json
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CODEX_PKG = "@openai/codex@0.144.1"


def codex_call(model, prompt):
    auth = pathlib.Path.home() / ".codex/auth.json"
    base = pathlib.Path.home() / ".codex-review-homes"
    base.mkdir(parents=True, exist_ok=True)
    iso = pathlib.Path(tempfile.mkdtemp(prefix="judge.", dir=str(base)))
    try:
        shutil.copy(auth, iso / "auth.json")
        os.chmod(iso / "auth.json", 0o600)
        cfg = pathlib.Path.home() / ".codex/config.toml"
        if cfg.exists():
            shutil.copy(cfg, iso / "config.toml")
        env = dict(os.environ)
        env["CODEX_HOME"] = str(iso)
        out = iso / "last.json"
        cmd = ["npx", "-y", CODEX_PKG, "exec", "-m", model,
               "-c", "model_reasoning_effort=high", "-s", "read-only",
               "--ignore-user-config", "--skip-git-repo-check", "--ephemeral",
               "--disable", "memories", "--disable", "standalone_web_search",
               "-C", str(ROOT), "--color", "never", "--json", "-o", str(out), "-"]
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, env=env)
        if not out.exists():
            return None, "no last-message (rc=%d) %s" % (p.returncode, p.stderr[-200:])
        raw = out.read_text()
        try:
            text = json.loads(raw)
            if not isinstance(text, str):
                text = raw
        except Exception:
            text = raw
        return text, None
    finally:
        shutil.rmtree(iso, ignore_errors=True)


PROMPT = """You are grouping candidate DICTIONARY DEFINITIONS of one concept by MEANING.

Concept word: {label}

Below are {n} independently-written definitions of that concept, labelled [1]..[{n}].
Group the labels so that two definitions are in the SAME group iff they express
essentially THE SAME definition (same genus + same distinguishing conditions),
ignoring wording, length, and style. A definition that adds or drops a
truth-conditional element belongs in a different group.

Then identify the CONSENSUS group: the single largest group of definitions that
agree (the "same definition" most models converged on). If no group has >=4
members, set consensus to [].

Definitions:
{items}

Reply with EXACTLY one JSON object, no prose, no fences:
{{"groups": [[...labels...], ...], "consensus": [...labels...], "reason": "one short sentence"}}
"""


def extract_json(text):
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--seed", type=int, default=20260713)
    ap.add_argument("--model", default="gpt-5.6-sol")
    ap.add_argument("--consensus", default=str(HERE / "consensus.json"))
    ap.add_argument("--out", default=str(HERE / "judge-spotcheck.json"))
    args = ap.parse_args()

    con = json.load(open(args.consensus))
    # concepts eligible: have glosses + an embedding clique
    pcs = [pc for pc in con["per_concept"]
           if pc.get("consensus_cluster") and pc.get("n_glosses", 0) >= 4]
    rng = random.Random(args.seed)
    sample = rng.sample(pcs, min(args.k, len(pcs)))

    results = []
    for pc in sample:
        models = pc["models"]
        glosses = pc["glosses"]
        # shuffle to hide identity/order
        order = models[:]
        rng.shuffle(order)
        label_map = {i + 1: m for i, m in enumerate(order)}  # judge-label -> model
        items = "\n".join("[%d] %s" % (i + 1, glosses[order[i]]) for i in range(len(order)))
        prompt = PROMPT.format(label=pc["concept"], n=len(order), items=items)
        text, err = codex_call(args.model, prompt)
        obj = extract_json(text)
        rec = {"concept": pc["concept"], "n": len(order),
               "embed_clique_models": sorted(pc["consensus_cluster"])}
        if not obj:
            rec.update({"judge_error": err or "unparseable", "raw": (text or "")[:400]})
            results.append(rec)
            continue
        def flat_ints(x, acc):
            if isinstance(x, list):
                for y in x:
                    flat_ints(y, acc)
            else:
                try:
                    acc.append(int(x))
                except (TypeError, ValueError):
                    pass
            return acc
        labels = flat_ints(obj.get("consensus") or [], [])
        judge_cons_models = sorted(label_map[i] for i in labels if i in label_map)
        embed = set(pc["consensus_cluster"])
        judge = set(judge_cons_models)
        inter = embed & judge
        union = embed | judge
        jacc = len(inter) / len(union) if union else 1.0
        # per-model in/out agreement over all models present
        agree = sum(1 for m in models if (m in embed) == (m in judge))
        rec.update({
            "judge_consensus_models": judge_cons_models,
            "judge_groups_models": [sorted(label_map[i] for i in flat_ints(g, []) if i in label_map)
                                    for g in (obj.get("groups") or [])],
            "jaccard": round(jacc, 3),
            "per_model_agreement": round(agree / len(models), 3),
            "judge_reason": obj.get("reason"),
        })
        results.append(rec)
        print("%-16s embed=%s judge=%s jaccard=%.2f" %
              (pc["concept"][:16], sorted(embed), judge_cons_models, jacc), flush=True)

    valid = [r for r in results if "jaccard" in r]
    summ = {
        "n_sampled": len(sample), "n_judged": len(valid),
        "mean_jaccard": round(sum(r["jaccard"] for r in valid) / len(valid), 3) if valid else None,
        "mean_per_model_agreement": round(sum(r["per_model_agreement"] for r in valid) / len(valid), 3) if valid else None,
        "n_exact_member_match": sum(1 for r in valid if r["jaccard"] == 1.0),
    }
    out = {"built": "judge spot-check vs embedding clustering",
           "judge_model": args.model, "seed": args.seed,
           "summary": summ, "results": results}
    json.dump(out, open(args.out, "w"), indent=2, ensure_ascii=False)
    print("\nSUMMARY:", json.dumps(summ))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
