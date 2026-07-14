#!/usr/bin/env python3
"""DECONTAMINATED routing analysis (v3) — successor to analyze_routing_v2.py.

WHY THIS EXISTS (bead kernel-of-truth-xafk; R4 finding, r4/r4-replay.md §1):
the committed results/stats/f000..f023.stats are SESSION-CUMULATIVE usage
dumps, not per-prompt fingerprints — per-cell counts are monotone
non-decreasing across the run (0/328,193 violations), totals grow
111,904 -> 371,336, and f000 already contains the 99,752 pre-P3 selections.
analyze_routing_v2.py (and v1) read them as per-prompt fingerprints, so the
pinned routing-analysis-v2.json magnitudes (mean-centred within 0.9119 /
across -0.0740, universal-mass 0.9392) were computed on cumulative
histograms in which within-concept prompts are ADJACENT in run order:
adjacency alone inflates within-concept similarity. Those magnitudes are
adjacency-inflated and are SUPERSEDED by this script's output.

CORRECTION (the first-difference recipe, identical to r4/r4_replay.py):
  d_N = f_N - f_{N-1}  (elementwise per (layer,expert) cell), N = 1..23,
  keeping strictly-positive cells. This recovers per-prompt fingerprints
  EXACTLY because the dumps are cumulative. f000's own fingerprint is
  UNRECOVERABLE from committed bytes (its pre-P3 per-cell baseline was not
  committed) -> f000 is DROPPED: n = 23, concept break.shatter n = 2.

Everything downstream is the v2 construction verbatim (R1 raw-cosine
within/across + 10k random-shuffle label-permutation test, R2 mean-centred
similarity, R3 per-sense-group minimal pairs; seed 20260712), run on the
differenced fingerprints. Deterministic; CPU-only; pure stdlib. ANALYSIS
ONLY: no probe run, nothing frozen, no branch classifier fired.

Cross-check: R2 raw/mean-centred values must reproduce
r4/r4-replay.json /structure_on_differenced_fingerprints (independent
numpy implementation): raw delta +0.1187, centred delta +0.3303, p 0.0001.
"""
import json, os, sys, math, random, hashlib
from collections import defaultdict

STATS = sys.argv[1] if len(sys.argv) > 1 else "poc/glm52-probe/results/stats"
SEED = 20260712          # same registered seed family as analyze_routing_v2.py
NPERM = 10000
manifest_path = os.path.join(STATS, "manifest.json")
manifest = json.load(open(manifest_path))

def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def load(path):
    v = {}
    for ln in open(path):
        p = ln.split()
        if len(p) >= 3:
            try: v[(int(p[0]), int(p[1]))] = float(p[2])
            except ValueError: pass
    return v

# ---- load CUMULATIVE dumps in manifest (run) order; record source hashes ----
stat_files = [os.path.join(STATS, os.path.basename(m["stats"])) for m in manifest]
cum = [load(fp) for fp in stat_files]
source_sha = {os.path.basename(fp): sha256(fp) for fp in stat_files}

# fail closed: the correction is only valid if the dumps really are cumulative
viol = sum(1 for i in range(1, len(cum)) for k, v in cum[i-1].items()
           if cum[i].get(k, 0) < v)
if viol != 0:
    sys.exit(f"ERR_NOT_CUMULATIVE: {viol} per-cell monotonicity violations; "
             "first-difference recipe invalid — do not use this script's output")

# ---- first-difference: d_N = f_N - f_(N-1), N = 1..23; f000 dropped ---------
raw, labels, senses, fids = [], [], [], []
for i in range(1, len(cum)):
    d = {k: cum[i][k] - cum[i-1].get(k, 0.0) for k in cum[i]
         if cum[i][k] - cum[i-1].get(k, 0.0) > 0}
    m = manifest[i]
    raw.append(d); labels.append(m["concept"])
    senses.append(m.get("sense_group", "none")); fids.append(f"f{i:03d}")
N = len(raw)
assert N == 23, f"expected 23 differenced fingerprints, got {N}"

# ---- from here on: analyze_routing_v2.py verbatim on the clean data ---------
keys = sorted(set().union(*[set(v) for v in raw]))
def vec(fp): return [fp.get(k, 0.0) for k in keys]
def l1norm(x):
    s = sum(x) or 1.0
    return [a/s for a in x]
V = [l1norm(vec(fp)) for fp in raw]

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

out = {
    "provenance": {
        "supersedes": "results/routing-analysis-v2.json (magnitudes adjacency-inflated; see CONTAMINATION-NOTE.md)",
        "superseded_sha256": sha256(os.path.join(os.path.dirname(STATS), "routing-analysis-v2.json")),
        "contamination": ("committed .stats files are SESSION-CUMULATIVE usage dumps "
                          "(per-cell monotone across f000..f023, 0/328193 violations; "
                          "totals 111904->371336; f000 contains the 99752 pre-P3 "
                          "selections). v1/v2 read them as per-prompt fingerprints; "
                          "within-concept prompts are adjacent in run order, so v2 "
                          "magnitudes confound concept structure with adjacency."),
        "correction": ("per-prompt fingerprints recovered EXACTLY by first-differencing "
                       "d_N = f_N - f_(N-1), N=1..23, keeping cells with positive "
                       "difference; cumulativity re-verified fail-closed at load"),
        "f000": "UNRECOVERABLE (pre-P3 per-cell baseline not committed) -> dropped; n=23, break.shatter n=2",
        "source_stats_sha256": source_sha,
        "manifest_sha256": sha256(manifest_path),
        "cross_check": ("raw/mean_centered must match r4/r4-replay.json "
                        "/structure_on_differenced_fingerprints (independent numpy impl)"),
        "finding": "r4/r4-replay.md §1; bead kernel-of-truth-xafk",
        "deterministic": "seed 20260712, 10k shuffles, pure stdlib; no probe re-run",
    },
    "n": N, "keyspace": len(keys), "universal_cells": nz_all,
    "universal_mass_frac": round(mass_universal, 4), "nperm": NPERM, "seed": SEED,
}

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
