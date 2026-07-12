#!/usr/bin/env python3
"""Offline analysis of GLM-5.2 concept->routing fingerprints (MECHANICAL statistics only;
interpretation is deferred to Fable/GPT-5.6 per the coordinator-never-concludes rule).

Input: probe-out/stats/ dir (fNNN.stats = `layer expert count` lines) + manifest.json.
Output: within- vs across-concept routing-similarity, sense-group minimal-pair analysis,
and a label-permutation test p-value. Prints a JSON summary.
"""
import json, os, sys, math, itertools
from collections import defaultdict

STATS_DIR = sys.argv[1] if len(sys.argv) > 1 else "stats"
manifest = json.load(open(os.path.join(STATS_DIR, "manifest.json")))

def load_fp(path):
    v = {}
    if not os.path.exists(path): return None
    for ln in open(path):
        p = ln.split()
        if len(p) >= 3:
            try: v[(int(p[0]), int(p[1]))] = float(p[2])
            except ValueError: pass
    s = sum(v.values())
    if s <= 0: return None
    return {k: c/s for k, c in v.items()}          # L1-normalized routing distribution

def cosine(a, b):
    keys = set(a) | set(b)
    dot = sum(a.get(k,0)*b.get(k,0) for k in keys)
    na = math.sqrt(sum(x*x for x in a.values())); nb = math.sqrt(sum(x*x for x in b.values()))
    return dot/(na*nb) if na and nb else 0.0

fps, labels, senses, prompts = [], [], [], []
for m in manifest:
    fp = load_fp(os.path.join(STATS_DIR, os.path.basename(m["stats"])))
    if fp is None: continue
    fps.append(fp); labels.append(m["concept"]); senses.append(m.get("sense_group","none")); prompts.append(m["prompt"])

N = len(fps)
sim = [[cosine(fps[i], fps[j]) for j in range(N)] for i in range(N)]

def mean(xs): return sum(xs)/len(xs) if xs else float("nan")
within, across = [], []
for i in range(N):
    for j in range(i+1, N):
        (within if labels[i]==labels[j] else across).append(sim[i][j])
obs = mean(within) - mean(across)

# label-permutation test (deterministic: enumerate a fixed set of cyclic shifts of labels)
def stat_for(lbls):
    w, a = [], []
    for i in range(N):
        for j in range(i+1, N):
            (w if lbls[i]==lbls[j] else a).append(sim[i][j])
    return mean(w) - mean(a)
perms = []
for shift in range(1, N):                      # N-1 deterministic cyclic relabelings
    perms.append(stat_for(labels[shift:]+labels[:shift]))
ge = sum(1 for p in perms if p >= obs)
pval = (ge+1)/(len(perms)+1)

# sense minimal-pair analysis: within-sense-group, same-concept vs different-concept (same lexeme)
sense_report = {}
for sg in sorted(set(senses)):
    if sg == "none": continue
    idxs = [i for i in range(N) if senses[i]==sg]
    sw, sa = [], []
    for a,b in itertools.combinations(idxs,2):
        (sw if labels[a]==labels[b] else sa).append(sim[a][b])
    sense_report[sg] = {"n_prompts":len(idxs), "within_sense_concept_sim":round(mean(sw),4),
                        "across_sense_concept_sim":round(mean(sa),4),
                        "delta":round(mean(sw)-mean(sa),4)}

out = {
  "n_fingerprints": N,
  "concepts": sorted(set(labels)),
  "within_concept_mean_sim": round(mean(within),4),
  "across_concept_mean_sim": round(mean(across),4),
  "observed_delta": round(obs,4),
  "perm_test_pvalue": round(pval,4),
  "n_perms": len(perms),
  "sense_minimal_pairs": sense_report,
  "note": "MECHANICAL statistics only. within>across delta with small p => routing carries concept structure beyond chance; sense minimal-pairs isolate concept-vs-lexeme (same word, different sense). Interpretation deferred to Fable/GPT-5.6."
}
print(json.dumps(out, indent=2))
