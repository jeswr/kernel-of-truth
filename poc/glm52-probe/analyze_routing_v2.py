#!/usr/bin/env python3
"""R1+R2+R3 mechanical re-analysis of the GLM-5.2 concept->routing fingerprints, verifying
Fable's interpretation previews (poc/glm52-probe/interpretation-fable.md). Coordinator-run
mechanical verification: (R1) proper 10k RANDOM-shuffle label-permutation test on the raw-cosine
matrix (my earlier v1 used 23 cyclic shifts, which floor p by construction when labels are blocked);
(R2) mean-centered similarity removing the ~universal histogram component; (R3) per-sense-group
minimal-pair separation with the same 10k-shuffle test. Deterministic (seeded). No instance, CPU only.
Interpretation is Fable's; this only reproduces the numbers.
"""
import json, os, sys, math, random
from collections import defaultdict

STATS = sys.argv[1] if len(sys.argv) > 1 else "poc/glm52-probe/results/stats"
SEED = 20260712
NPERM = 10000
manifest = json.load(open(os.path.join(STATS, "manifest.json")))

def load(path):
    v = {}
    for ln in open(path):
        p = ln.split()
        if len(p) >= 3:
            try: v[(int(p[0]), int(p[1]))] = float(p[2])
            except ValueError: pass
    return v

raw, labels, senses = [], [], []
for m in manifest:
    fp = load(os.path.join(STATS, os.path.basename(m["stats"])))
    if not fp: continue
    raw.append(fp); labels.append(m["concept"]); senses.append(m.get("sense_group", "none"))
N = len(raw)

# universal keyspace + dense vectors
keys = sorted(set().union(*[set(v) for v in raw]))
def vec(fp): return [fp.get(k, 0.0) for k in keys]
def l1norm(x):
    s = sum(x) or 1.0
    return [a/s for a in x]
V = [l1norm(vec(fp)) for fp in raw]

# universal component = element-wise mean over all fingerprints
mean = [sum(V[i][j] for i in range(N))/N for j in range(len(keys))]
nz_all = sum(1 for j in range(len(keys)) if all(V[i][j] > 0 for i in range(N)))
mass_universal = sum(mean[j] for j in range(len(keys)) if all(V[i][j] > 0 for i in range(N)))

def cos(a, b):
    d = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    return d/(na*nb) if na and nb else 0.0

def simmat(vs):
    return [[cos(vs[i], vs[j]) for j in range(N)] for i in range(N)]

Vc = [[V[i][j]-mean[j] for j in range(len(keys))] for i in range(N)]  # mean-centered

def wa_delta(sim, lbls):
    w = [sim[i][j] for i in range(N) for j in range(i+1, N) if lbls[i] == lbls[j]]
    a = [sim[i][j] for i in range(N) for j in range(i+1, N) if lbls[i] != lbls[j]]
    mw = sum(w)/len(w) if w else 0.0; ma = sum(a)/len(a) if a else 0.0
    return mw, ma, mw-ma

def perm_p(sim, lbls, nperm=NPERM):
    _, _, obs = wa_delta(sim, lbls)
    rnd = random.Random(SEED); ge = 0; cur = list(lbls)
    for _ in range(nperm):
        rnd.shuffle(cur)
        if wa_delta(sim, cur)[2] >= obs: ge += 1
    return obs, (ge+1)/(nperm+1)

out = {"n": N, "keyspace": len(keys), "universal_cells": nz_all,
       "universal_mass_frac": round(mass_universal, 4), "nperm": NPERM, "seed": SEED}

sim_raw = simmat(V); sim_c = simmat(Vc)
w, a, obs = wa_delta(sim_raw, labels); _, praw = perm_p(sim_raw, labels)
out["raw_cosine"] = {"within": round(w,4), "across": round(a,4), "delta": round(obs,4), "perm_p_10k": round(praw,5)}
wc, ac, obsc = wa_delta(sim_c, labels); _, pc = perm_p(sim_c, labels)
out["mean_centered"] = {"within": round(wc,4), "across": round(ac,4), "delta": round(obsc,4), "perm_p_10k": round(pc,5)}

# sense minimal-pairs (mean-centered), within-group perm test over that group's members
sp = {}
for sg in sorted(set(senses)):
    if sg == "none": continue
    idx = [i for i in range(N) if senses[i] == sg]
    sub = [[sim_c[i][j] for j in idx] for i in idx]
    lb = [labels[i] for i in idx]; n = len(idx)
    def wad(order):
        w=[sub[i][j] for i in range(n) for j in range(i+1,n) if lb[order[i]]==lb[order[j]]]
        a=[sub[i][j] for i in range(n) for j in range(i+1,n) if lb[order[i]]!=lb[order[j]]]
        return (sum(w)/len(w) if w else 0)-(sum(a)/len(a) if a else 0)
    base=list(range(n)); obs2=wad(base); rnd=random.Random(SEED); ge=0
    for _ in range(NPERM):
        rnd.shuffle(base);
        if wad(base)>=obs2: ge+=1
    sp[sg] = {"n": n, "delta_centered": round(obs2,4), "perm_p": round((ge+1)/(NPERM+1),5)}
out["sense_pairs_centered"] = sp
print(json.dumps(out, indent=2))
