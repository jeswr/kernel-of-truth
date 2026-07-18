#!/usr/bin/env python3
"""Candidate-A Stage-0a — FALSIFIER-1 $0 routing-trace re-analysis (DESCRIPTIVE ONLY).

Spec (authoritative): docs/next/design/candidate-a-stage0-measurement.md §3
(v3, GPT-5.6 re-review: "Stage-0a is APPROVED to run as designed").

Computations (all DESCRIPTIVE — no falsifier verdict is derivable at this tier):
  A1  pin-set reconstruction + residual. Rank accum20.stats cells by count desc,
      tie-break (layer, expert) asc; top 2,696 MUST reproduce m4.json
      h_pin_by_G.G50 = 0.7628 (FAIL CLOSED otherwise — verification anchor).
      Residual 0.2372 is an in-sample, optimistically-LOW-biased point
      estimate, NOT a deterministic out-of-sample floor (§3 A1, v2 fix 3).
  A2  residual concentration / STATIC-residency GB economics over non-pin
      cells: GB for the next 5pp / 10pp of total selection traffic. Bounds
      STATIC / prompt-level residency levers ONLY (§3 A2, v2 fix 8; ASM-2511).
  A3  hot-set stability of the A1 pin across the 23 differenced D1
      fingerprints — prompt-fixed diagnostic under a DISCLOSED corpus +
      execution-config mismatch (D1: MTP-active draft=3, experts INT8,
      78 layers [MEASURED f000.out:2,9] vs target 75-layer int4 DRAFT=0);
      layer-78 (MTP-position) cells EXCLUDED both sides (§3 disclosure,
      v2 fix 4). NOT clean OOD evidence.
  A4  prompt-level oracle gap at the matched 2,696-cell budget (same
      exclusion + disclosure). Bounds prompt-conditioned residency policies
      on THIS config-mismatched prompt set only (ASM-2511).
  A5  NOT COMPUTED HERE — moved to Stage-0b (§3 A5 tombstone, v2 fix 1): the
      committed D5 parquet drops the family x counterpart conditional-mass
      maps; no predictability estimate exists in committed bytes.
  A6  verdict assembly: HARD-CODED "PROVISIONAL-NEEDS-0b" (§3 A6, v2 fix 11).
      Stage-0a CANNOT license DEAD or GREENLIGHT.

Reused VERBATIM from analyze_routing_v3.py (per §3): sha256(), the load()
stats parser, the fail-closed ERR_NOT_CUMULATIVE monotonicity check, the
first-difference recipe (d_N = f_N - f_{N-1}, N=1..23, f000 dropped), and the
seeded random.Random(SEED) permutation/bootstrap machinery pattern.

Deterministic: seed 20260712 (same registered seed family as
analyze_routing_v3.py); pure stdlib; CPU-only; no network; read-only on all
inputs. Writes results/falsifier1-stage0a.json + .md only. Fail-closed ERR_*
codes throughout; no silent fallbacks.
"""
import json, os, sys, math, random, hashlib
from statistics import NormalDist, median

SEED = 20260712        # registered seed family (analyze_routing_v3.py)
NBOOT = 10000          # bootstrap resamples for BCa CIs (n=23 -> CIs wide; reported anyway)
PIN_CELLS = 2696       # G50 pin budget in cells  [MEASURED, m4.json h_pin_by_G.G50]
PIN_BUDGET_GB = 50     # decimal GB               [MEASURED, m4.json]
H_PIN_ANCHOR = 0.7628  # verification anchor      [MEASURED, m4.json] — FAIL CLOSED if not reproduced
MTP_LAYER = 78         # D1 MTP-position layer, excluded both sides in A3/A4 (spec §3, v2 fix 4)

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# ---- inputs (spec §3 "Inputs"; sha256 of each recorded in provenance) -------
IN = {
    "poc/gcp/probe-results/accum20.stats": None,
    "poc/gcp/probe-results/m4.json": None,
    "poc/glm52-probe/results/stats/manifest.json": None,
    "poc/glm52-probe/wave-a/atlas/expert_atlas.parquet": None,       # hashed only; A5 moved to 0b
    "poc/glm52-probe/wave-a/atlas/expert_atlas_index.json": None,    # hashed only
    "poc/glm52-probe/wave-a/atlas/coverage_gates.json": None,        # caveat source (gates FAILED)
    "poc/glm52-probe/wave-a/corpus/corpus_manifest.json": None,      # hashed only
}
for i in range(24):
    IN[f"poc/glm52-probe/results/stats/f{i:03d}.stats"] = None
for rel in IN:
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        sys.exit(f"ERR_MISSING_INPUT: {rel} not found — STOP (all Stage-0a inputs must be committed bytes)")

def sha256(path):  # analyze_routing_v3.py verbatim
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def load(path):    # analyze_routing_v3.py verbatim
    v = {}
    for ln in open(path):
        p = ln.split()
        if len(p) >= 3:
            try: v[(int(p[0]), int(p[1]))] = float(p[2])
            except ValueError: pass
    return v

source_sha = {rel: sha256(os.path.join(ROOT, rel)) for rel in sorted(IN)}

# ---- D1: load cumulative dumps in manifest order; fail-closed cumulativity --
STATS = os.path.join(ROOT, "poc/glm52-probe/results/stats")
manifest = json.load(open(os.path.join(STATS, "manifest.json")))
stat_files = [os.path.join(STATS, os.path.basename(m["stats"])) for m in manifest]
cum = [load(fp) for fp in stat_files]

# fail closed: the correction is only valid if the dumps really are cumulative
viol = sum(1 for i in range(1, len(cum)) for k, v in cum[i-1].items()
           if cum[i].get(k, 0) < v)
if viol != 0:
    sys.exit(f"ERR_NOT_CUMULATIVE: {viol} per-cell monotonicity violations; "
             "first-difference recipe invalid — do not use this script's output")

# first-difference: d_N = f_N - f_(N-1), N = 1..23; f000 dropped (v3 verbatim)
raw, labels, fids = [], [], []
for i in range(1, len(cum)):
    d = {k: cum[i][k] - cum[i-1].get(k, 0.0) for k in cum[i]
         if cum[i][k] - cum[i-1].get(k, 0.0) > 0}
    raw.append(d); labels.append(manifest[i]["concept"]); fids.append(f"f{i:03d}")
if len(raw) != 23:
    sys.exit(f"ERR_DIFF_COUNT: expected 23 differenced fingerprints, got {len(raw)}")

# ---- A1: pin-set reconstruction + residual (verification anchor) ------------
acc = load(os.path.join(ROOT, "poc/gcp/probe-results/accum20.stats"))
m4 = json.load(open(os.path.join(ROOT, "poc/gcp/probe-results/m4.json")))
total = sum(acc.values())
if total != m4["total_selections"]:
    sys.exit(f"ERR_TOTALS_MISMATCH: accum20 sums to {total}, m4.json says {m4['total_selections']}")
per_expert_bytes = m4["per_expert_bytes"]

# rank by count desc, tie-break (layer, expert) asc (spec §3 A1)
order = sorted(acc.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
pin = set(k for k, _ in order[:PIN_CELLS])
h_pin = sum(acc[k] for k in pin) / total
if round(h_pin, 4) != H_PIN_ANCHOR:
    sys.exit(f"ERR_PIN_MISMATCH: reconstructed h_pin {h_pin:.6f} (rounds to {round(h_pin,4)}) "
             f"!= anchor {H_PIN_ANCHOR} — FAIL CLOSED (spec §3 A1); STOP, do not use any output")
if any(k[0] == MTP_LAYER for k in pin):
    sys.exit("ERR_PIN_LAYER: pin set contains MTP-layer cells — accum20 layer range violated")
# secondary (non-fail-closed) anchors: G40 / G100 from the same ranking
repro = {}
for gname, spec in m4["h_pin_by_G"].items():
    h = sum(v for _, v in order[:spec["experts_pinned"]]) / total
    repro[gname] = {"cells": spec["experts_pinned"], "h_pin_reconstructed": round(h, 4),
                    "h_pin_m4": spec["h_pin"], "match": round(h, 4) == spec["h_pin"]}
residual = 1.0 - h_pin

# ---- A2: residual concentration / STATIC-residency GB economics -------------
gb_per_cell = per_expert_bytes / 1e9
nonpin = order[PIN_CELLS:]

def cells_for_extra_pp(extra_frac):
    """Non-pin cells (rank order) to capture extra_frac of TOTAL selections."""
    need = extra_frac * total
    got, n = 0.0, 0
    for _, v in nonpin:
        got += v; n += 1
        if got >= need:
            return n, got
    return None, got  # not reachable within observed tail

a2 = {"scope": "static/prompt-level residency only",  # spec §3 A2 / ASM-2511 (v2 fix 8)
      "note": ("bounds STATIC and prompt-level residency levers only; a token/layer-"
               "conditioned swapping policy can reuse capacity across the diffuse tail "
               "(ASM-2511); dynamic levers are addressed only at 0b/Stage-1")}
for pp, key in ((0.05, "gb_for_next_5pp"), (0.10, "gb_for_next_10pp")):
    n, got = cells_for_extra_pp(pp)
    if n is None:
        sys.exit(f"ERR_TAIL_EXHAUSTED: observed tail cannot supply +{pp:.0%} of total")
    a2[key] = {"extra_cells": n, "extra_gb": round(n * gb_per_cell, 2),
               "total_gb": round(PIN_BUDGET_GB + n * gb_per_cell, 2),
               "cum_hit_frac_total": round((h_pin * total + got) / total, 4)}
# fine-grain curve extending m4's below the pin line: one point per +1pp of total hit
# (targets stop at 0.99; the 1.0 full-tail point is appended once, with its note)
curve, got, n = [], 0.0, 0
targets = [t / 100.0 for t in range(int(math.ceil(h_pin * 100)), 100)]
ti = 0
for _, v in nonpin:
    got += v; n += 1
    frac = (h_pin * total + got) / total
    while ti < len(targets) and frac >= targets[ti]:
        curve.append({"cum_hit_frac_total": targets[ti], "extra_cells": n,
                      "extra_gb": round(n * gb_per_cell, 2),
                      "total_gb": round(PIN_BUDGET_GB + n * gb_per_cell, 2)})
        ti += 1
curve.append({"cum_hit_frac_total": 1.0, "extra_cells": len(nonpin),
              "extra_gb": round(len(nonpin) * gb_per_cell, 2),
              "total_gb": round(PIN_BUDGET_GB + len(nonpin) * gb_per_cell, 2),
              "note": "full observed tail (16,184 active cells of 19,200)"})
a2["curve"] = curve

# ---- BCa bootstrap CI (seeded; machinery pattern per analyze_routing_v3.py) -
def bca_ci95(vals, stat):
    nd = NormalDist(); n = len(vals); obs = stat(vals)
    rnd = random.Random(SEED)  # fresh SEED per test, as v3 does for each perm test
    boots = sorted(stat([vals[rnd.randrange(n)] for _ in range(n)]) for _ in range(NBOOT))
    below = sum(1 for b in boots if b < obs)
    p0 = min(max(below / NBOOT, 1.0 / (NBOOT + 1)), 1.0 - 1.0 / (NBOOT + 1))
    z0 = nd.inv_cdf(p0)
    jack = [stat(vals[:i] + vals[i+1:]) for i in range(n)]
    jm = sum(jack) / n
    den = 6.0 * (sum((jm - j) ** 2 for j in jack)) ** 1.5
    a = (sum((jm - j) ** 3 for j in jack) / den) if den else 0.0
    def q(al):
        z = nd.inv_cdf(al)
        adj = nd.cdf(z0 + (z0 + z) / (1.0 - a * (z0 + z)))
        return boots[min(max(int(adj * NBOOT), 0), NBOOT - 1)]
    return [round(q(0.025), 4), round(q(0.975), 4)]

CONFIG_MISMATCH = ("D1 MTP-active (draft=3) int8 78L vs target int4 DRAFT=0 75L; "
                   "layer-78 cells excluded both sides; corpus AND execution config "
                   "differ -> prompt-fixed diagnostic, NOT clean OOD evidence")

# ---- A3: hot-set stability across the 23 differenced fingerprints -----------
a3_hits, a4_rows, l78_mass = [], [], []
for fid, lab, d in zip(fids, labels, raw):
    tot_all = sum(d.values())
    d75 = {k: v for k, v in d.items() if k[0] != MTP_LAYER}
    tot = sum(d75.values())
    if tot <= 0:
        sys.exit(f"ERR_EMPTY_FINGERPRINT: {fid} has no non-MTP mass")
    l78_mass.append(1.0 - tot / tot_all)
    static_hit = sum(v for k, v in d75.items() if k in pin) / tot
    a3_hits.append(static_hit)
    # A4: oracle per-prompt pin at the matched 2,696-cell budget (same ranking rule)
    op = sorted(d75.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
    oracle = sum(v for _, v in op[:PIN_CELLS]) / tot
    a4_rows.append({"fid": fid, "concept": lab, "oracle_hit": round(oracle, 4),
                    "static_hit": round(static_hit, 4),
                    "delta_oracle": round(oracle - static_hit, 4),
                    "positive_cells": len(d75)})

a3 = {"per_prompt_hit": [{"fid": f, "concept": c, "hit": round(h, 4)}
                         for f, c, h in zip(fids, labels, a3_hits)],
      "median": round(median(a3_hits), 4), "min": round(min(a3_hits), 4),
      "mean": round(sum(a3_hits) / len(a3_hits), 4),
      "ci95_median_bca": bca_ci95(a3_hits, lambda v: median(v)),
      "layer78_mass_excluded_mean": round(sum(l78_mass) / len(l78_mass), 4),
      "config_mismatch": CONFIG_MISMATCH}

# ---- A4: prompt-level oracle gap --------------------------------------------
deltas = [r["delta_oracle"] for r in a4_rows]
a4 = {"delta_oracle_mean": round(sum(deltas) / len(deltas), 4),
      "delta_oracle_median": round(median(deltas), 4),
      "ci95_mean_bca": bca_ci95(deltas, lambda v: sum(v) / len(v)),
      "per_prompt": a4_rows,
      "note": ("oracle = top-2,696 cells of the prompt's OWN fingerprint (same ranking "
               "rule); bounds prompt-conditioned residency policies on this "
               "config-mismatched prompt set only; NOT a bound on within-sequence "
               "token-level swapping (ASM-2511)"),
      "config_mismatch": CONFIG_MISMATCH}

# ---- A6: verdict assembly + output (schema kot-falsifier1/0a, spec §3) ------
cov = json.load(open(os.path.join(ROOT, "poc/glm52-probe/wave-a/atlas/coverage_gates.json")))
out = {
    "schema": "kot-falsifier1/0a",
    "provenance": {
        "spec": "docs/next/design/candidate-a-stage0-measurement.md §3 (v3; Stage-0a approved to run as designed)",
        "source_sha256": source_sha,
        "seed": SEED,
        "script": "poc/glm52-probe/analyze_residual_v1.py",
        "script_sha256": sha256(os.path.abspath(__file__)),
        "tier": "committed-bytes-only",
        "d3_commit": "d594844070b02e1234b095e14942a8405dacffee",
        "reused_from_analyze_routing_v3": ["load() stats parser", "ERR_NOT_CUMULATIVE fail-closed check",
                                          "first-difference recipe (f000 dropped, n=23)",
                                          "seeded Random(SEED) resampling machinery pattern"],
        "deterministic": f"seed {SEED}, {NBOOT} bootstrap resamples, pure stdlib, no network",
    },
    "config": {"pin_budget_gb": PIN_BUDGET_GB, "pin_cells": PIN_CELLS,
               "per_expert_bytes": per_expert_bytes, "layer78_excluded": True,
               "thresholds": {"kill_pp": 5, "green_pp": 10,
                              "note": "ASM-2505 applies at 0b/Stage-1 ONLY, not at 0a"},
               "nboot": NBOOT, "seed": SEED, "n_prompts": len(raw)},
    "A1": {"h_pin_insample": round(h_pin, 6),
           "residual_mass_insample_biased": round(residual, 6),
           "anchor_reproduced": True, "anchor": H_PIN_ANCHOR,
           "secondary_anchors": repro,
           "bias": ("IN-SAMPLE: pin ranked and scored on the same histogram; residual "
                    "is an optimistically-LOW-biased point estimate, NOT an "
                    "out-of-sample floor (true OOS residual likely higher)")},
    "A2": a2,
    "A3": a3,
    "A4": a4,
    "verdict": "PROVISIONAL-NEEDS-0b",  # HARD-CODED at this tier (spec §3 A6); DEAD/GREENLIGHT unreachable
    "caveats": [
        "descriptive only — Stage-0a licenses no falsifier verdict; ASM-2505 applies at 0b/Stage-1",
        "in-sample pin: residual 0.2372 biased low, NOT a deterministic out-of-sample floor",
        "A3/A4 config-confounded: D1 MTP-active int8 78L vs target int4 DRAFT=0 75L "
        "(layer 78 excluded both sides); corpus AND execution config differ",
        "no predictability estimate exists at this tier: committed D5 parquet drops the "
        "family x counterpart conditional-mass maps (6 biased top-activation exemplars per cell only)",
        "A2 bounds STATIC/prompt-level residency only; token/layer-conditioned swapping not bounded (ASM-2511)",
        f"wave-a atlas coverage gates FAILED (mass_on_ge100_event_experts "
        f"{cov['mass_on_ge100_event_experts']} < 0.95 gate; Spearman median "
        f"{cov['discovery_heldout_spearman_median']}, 0% layers >= 0.8 gate; "
        f"{cov['label_class_counts']['rare']}/19200 cells rare) — the undersampled region is "
        "exactly the non-resident residual",
        "n=23 differenced prompt fingerprints (f000 unrecoverable, dropped); BCa CIs wide",
        "D1 .stats are SESSION-CUMULATIVE; per-prompt fingerprints recovered by first-differencing "
        "(cumulativity re-verified fail-closed at load)",
    ],
}

res_path = os.path.join(ROOT, "poc/glm52-probe/results/falsifier1-stage0a.json")
with open(res_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"wrote {res_path}")
print(json.dumps({"A1_h_pin": out["A1"]["h_pin_insample"],
                  "A1_residual": out["A1"]["residual_mass_insample_biased"],
                  "A2_next5pp": a2["gb_for_next_5pp"], "A2_next10pp": a2["gb_for_next_10pp"],
                  "A3_median": a3["median"], "A3_min": a3["min"], "A3_ci95": a3["ci95_median_bca"],
                  "A4_delta_mean": a4["delta_oracle_mean"], "A4_ci95": a4["ci95_mean_bca"],
                  "verdict": out["verdict"]}, indent=2))
