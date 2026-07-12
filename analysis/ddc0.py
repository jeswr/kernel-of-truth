#!/usr/bin/env python3
"""ddc0 pre-registered analysis (pure function over G0 statistics outputs).

Design: docs/next/design/DDC.md — §2.3 (A2 alignment: the joint max-stat
permutation family over directions x layers x methods, the four admission
criteria, the per-layer cap, FORK-1 method selection), §6 (stage table row
"G0 statistics (ddc0)" + record freeze-shape note: exactly one primary
endpoint n_layers_admitted, primary claim n_layers_admitted >= ceil(L/3),
no NULL verdict row), §8 (G0 routing rules: killed-by-G0 + the C4
expected-tie flag + FORK-1/FORK-2 mechanical resolution).
ASMs: PROPOSED-ASM-1700 (probe/alignment construction), PROPOSED-ASM-1701
(max-stat null family), PROPOSED-ASM-1702 (admission criteria).

Inputs (produced by the G0 harness; this script NEVER trusts precomputed
verdicts — every gate and analysis value is recomputed from raw fields):

--candidates <candidates.jsonl>: one row per candidate direction =
  {"layer": int (0..L-1), "method": "ridge-cca"|"procrustes",
   "dir_index": int, "test_score": float (signed one-sided TEST-partition
   Pearson correlation — the max-stat family statistic),
   "carrier_half_cos": float (|cos| between the two carrier-half refits,
   §2.3 criterion 2), "minimal_contrast_p": float (per-stratum permutation
   p on the SEL-housed minimal-contrast stratum, criterion 3),
   "bag_delta_ci90_low": float (lower bound of the seeded paired-bootstrap
   90% CI of s - s_bag over TEST concepts, 1e3 resamples, criterion 4)}.

--maxstat-null <maxstat-null.json>:
  {"B": 1000, "seed": 1, "family": "directions x layers x methods",
   "t_b": [1000 floats — per-replicate maximum over ALL candidates of the
   TEST score, the FULL pipeline re-run per replicate (ASM-1701)]}.

--sidecar <sidecar.json>:
  {"L": 30, "probe_fixture_sha_run1": str, "probe_fixture_sha_run2": str,
   "split": {"fit_sha256": str, "sel_sha256": str, "test_sha256": str,
             "n_fit": int, "n_sel": int, "n_test": int,
             "overlap_empty": bool},
   "expected_methods": ["ridge-cca", "procrustes"],
   "expected_layers": int (= L),
   "expected_dirs_per_layer_per_method": int (J = min(64, n_fit - 1)),
   "c4_subspace_overlap_per_layer": {"<layer>": float}
     ((1/r)||P_ker P_C4||_F^2, uncentred convention, working r; ALL L
     layers required — anything less fails closed),
   "template_variance_top_pc": {"mean-pool": float, "last-token": float}
     (top-PC variance fraction of the probe-set representation — the
     FORK-2 diagnostic),
   "k_cap": 256}.

Statistics conventions (implemented, not narrated):
- max-stat p per candidate: p = (1 + #{b : t_b >= s}) / (B + 1) with
  B = len(t_b); criterion 1 passes iff p <= 0.05 — Westfall-Young FWER
  control jointly over directions x layers x methods (ASM-1701); no
  uncorrected per-direction null appears anywhere in admission.
- reported threshold t* (§2.3 basis-assembly convention): the
  ceil(0.95*(B+1))-th order statistic of {t_b} — index
  int(math.ceil(0.95*(B+1))) - 1 of the ascending-sorted t_b, clamped to
  [0, B-1]. Under the counting convention above a score at B = 1000 is
  criterion-1 admitted iff it STRICTLY exceeds t* (ties count against).
- ADMITTED iff ALL four §2.3 criteria (ASM-1702): (1) max-stat p <= 0.05;
  (2) carrier_half_cos >= 0.8; (3) minimal_contrast_p <= 0.05 with
  positive survival; (4) bag_delta_ci90_low > 0. Criteria 1-3 passing
  with criterion 4 failing => admitted-as-LEXICAL: flagged in
  /analysis/bag_of_primes_lexical_flags, listed in max_stat_p_admitted,
  but NEVER counted toward n_layers_admitted and never basis-eligible.
- per-layer cap k <= min(d/2, k_cap) = k_cap = 256 STRUCTURAL admissions
  per layer per method (with J <= 64 in-contract the cap cannot bind;
  enforced anyway): overflow demotes the weakest — ordered by test_score
  descending, ties by lower dir_index — to non-admitted, never silently
  kept.
- FORK-1 (method selection, after correction): the method with structural
  admissions in MORE layers wins; tie -> "ridge-cca" (pre-declared v1
  default). /analysis/n_layers_admitted is the winning method's count.
- G0 routing (§8): killed_by_g0 iff n_layers_admitted < ceil(L/3)
  (L = 30 -> 10).
- FORK-2 (pooling): "mean-pool" iff its top-PC variance fraction <= 0.5
  (the pinned v1 pooling wins whenever valid); else "last-token" iff that
  fraction <= 0.5; else "template-dominated".
- expected-tie flag (§8): c4 overlap >= 0.9 at the working r for ALL L
  layers.
- admitted_directions_per_layer lists only layers with >= 1 structural
  admission for the WINNING method; carrier_half_stability and
  minimal_contrast_survival summarise ALL admitted directions
  (structural + lexical — criteria 2/3 hold for both).

Gates (computed here from raw sidecar/null/candidate fields, never copied):
- /gates/probe_fixture_deterministic: sha_run1 == sha_run2, both
  non-empty lowercase 64-hex.
- /gates/split_integrity_valid: overlap_empty AND
  n_fit + n_sel + n_test >= 100 AND all three split shas lowercase
  64-hex AND pairwise distinct.
- /gates/permutation_family_complete: B == 1000 AND len(t_b) == 1000 AND
  the candidate rows cover EXACTLY expected_layers x expected_methods
  with >= 1 and <= expected_dirs_per_layer_per_method dirs per (layer,
  method) cell — anything else means the family was not fully re-run.

Output: canonical JSON on stdout with exactly OUTPUT_FIELDS. Fail-closed
named errors (stderr + exit 1) fire ONLY for structurally unusable
inputs: ERR_DDC0_IO (unreadable file), ERR_DDC0_MALFORMED (undecodable
JSON, missing/mistyped/non-finite fields, c4 map not covering all L
layers), ERR_DDC0_DUPLICATE (the same layer/method/dir_index twice),
ERR_DDC0_FAMILY_INCOMPLETE (zero candidate rows, or absent/empty null
vector t_b). "Complete but failing" states (wrong B, missing grid cells,
sha mismatch, split too small) are gate booleans, never errors — and
never silent defaults.
"""

import argparse
import json
import math
import sys

OUTPUT_FIELDS = [
    "/gates/probe_fixture_deterministic",
    "/gates/split_integrity_valid",
    "/gates/permutation_family_complete",
    "/analysis/n_layers_admitted",
    "/analysis/n_layers_admitted_ge_third",
    "/analysis/killed_by_g0",
    "/analysis/winning_method",
    "/analysis/fork1_method_choice",
    "/analysis/fork2_pooling_choice",
    "/analysis/n_layers_admitted_ridge_cca",
    "/analysis/n_layers_admitted_procrustes",
    "/analysis/admitted_directions_per_layer",
    "/analysis/max_stat_threshold",
    "/analysis/max_stat_p_admitted",
    "/analysis/carrier_half_stability",
    "/analysis/minimal_contrast_survival",
    "/analysis/bag_of_primes_lexical_flags",
    "/analysis/c4_subspace_overlap_per_layer",
    "/analysis/c4_overlap_ge_09_all_layers",
    "/analysis/template_variance_top_pc",
]

ALPHA = 0.05             # criteria 1 and 3 level (§2.3, ASM-1701/1702)
CARRIER_COS_MIN = 0.8    # criterion 2 bound (§2.3, ASM-1702)
EXPECTED_B = 1000        # pinned replicate count (ASM-1701)
METHODS = ("ridge-cca", "procrustes")
FORK1_TIE = "ridge-cca"  # pre-declared v1 default (§2.3 FORK-1)
TEMPLATE_VAR_MAX = 0.5   # FORK-2 template-dominance bound (§2.3)
C4_TIE_BOUND = 0.9       # §8 expected-tie flag bound
SPLIT_MIN_TOTAL = 100    # split-integrity floor (n ~ 119 concepts, §2.3)

CAND_FIELDS = ("layer", "method", "dir_index", "test_score",
               "carrier_half_cos", "minimal_contrast_p",
               "bag_delta_ci90_low")


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    raise SystemExit(1)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_num(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v))


def _is_hex64(s):
    return (isinstance(s, str) and len(s) == 64
            and all(c in "0123456789abcdef" for c in s))


def _read(path, what):
    try:
        with open(path) as fh:
            return fh.read()
    except OSError as e:
        die("ERR_DDC0_IO", "cannot read %s %r: %s" % (what, path, e))


def _load_json(path, what):
    txt = _read(path, what)
    try:
        obj = json.loads(txt)
    except ValueError as e:
        die("ERR_DDC0_MALFORMED", "%s %r is not valid JSON: %s"
            % (what, path, e))
    if not isinstance(obj, dict):
        die("ERR_DDC0_MALFORMED", "%s %r: top level must be an object"
            % (what, path))
    return obj


def _load_jsonl(path, what):
    rows = []
    for ln, line in enumerate(_read(path, what).splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as e:
            die("ERR_DDC0_MALFORMED", "%s %r line %d: %s"
                % (what, path, ln, e))
        if not isinstance(row, dict):
            die("ERR_DDC0_MALFORMED", "%s %r line %d: row must be an object"
                % (what, path, ln))
        rows.append(row)
    return rows


def _require(obj, key, what, pred, desc):
    if key not in obj:
        die("ERR_DDC0_MALFORMED", "%s missing key %r" % (what, key))
    if not pred(obj[key]):
        die("ERR_DDC0_MALFORMED", "%s key %r must be %s (got %r)"
            % (what, key, desc, obj[key]))
    return obj[key]


def load_sidecar(path):
    side = _load_json(path, "sidecar")
    what = "sidecar"
    L = _require(side, "L", what, lambda v: _is_int(v) and v >= 1,
                 "int >= 1")
    _require(side, "probe_fixture_sha_run1", what,
             lambda v: isinstance(v, str), "str")
    _require(side, "probe_fixture_sha_run2", what,
             lambda v: isinstance(v, str), "str")
    split = _require(side, "split", what,
                     lambda v: isinstance(v, dict), "object")
    for k in ("fit_sha256", "sel_sha256", "test_sha256"):
        _require(split, k, "sidecar.split", lambda v: isinstance(v, str),
                 "str")
    for k in ("n_fit", "n_sel", "n_test"):
        _require(split, k, "sidecar.split",
                 lambda v: _is_int(v) and v >= 0, "int >= 0")
    _require(split, "overlap_empty", "sidecar.split",
             lambda v: isinstance(v, bool), "bool")
    methods = _require(side, "expected_methods", what,
                       lambda v: isinstance(v, list)
                       and set(v) == set(METHODS) and len(v) == 2,
                       "exactly the two pinned methods %r" % (METHODS,))
    exp_layers = _require(side, "expected_layers", what,
                          lambda v: _is_int(v) and v >= 1, "int >= 1")
    if exp_layers != L:
        die("ERR_DDC0_MALFORMED",
            "sidecar expected_layers=%r disagrees with L=%r"
            % (exp_layers, L))
    _require(side, "expected_dirs_per_layer_per_method", what,
             lambda v: _is_int(v) and v >= 1, "int >= 1")
    c4 = _require(side, "c4_subspace_overlap_per_layer", what,
                  lambda v: isinstance(v, dict), "object")
    want = set(str(l) for l in range(L))
    if set(c4) != want:
        die("ERR_DDC0_MALFORMED",
            "c4_subspace_overlap_per_layer must carry ALL %d layers "
            "0..%d exactly (got keys %r)" % (L, L - 1, sorted(c4)))
    for k, v in c4.items():
        if not _is_num(v):
            die("ERR_DDC0_MALFORMED",
                "c4_subspace_overlap_per_layer[%r] must be a finite "
                "number (got %r)" % (k, v))
    tmpl = _require(side, "template_variance_top_pc", what,
                    lambda v: isinstance(v, dict), "object")
    for k in ("mean-pool", "last-token"):
        _require(tmpl, k, "sidecar.template_variance_top_pc", _is_num,
                 "finite number")
    _require(side, "k_cap", what, lambda v: _is_int(v) and v >= 1,
             "int >= 1")
    return side


def load_null(path):
    null = _load_json(path, "maxstat-null")
    what = "maxstat-null"
    for k in ("B", "seed", "family"):
        if k not in null:
            die("ERR_DDC0_MALFORMED", "%s missing key %r" % (what, k))
    if not _is_int(null["B"]):
        die("ERR_DDC0_MALFORMED", "%s key 'B' must be int (got %r)"
            % (what, null["B"]))
    tb = null.get("t_b")
    if not isinstance(tb, list) or not tb:
        # structurally unusable: no null vector at all -> the family was
        # never run; distinct from the "ran but wrong size" gate case.
        die("ERR_DDC0_FAMILY_INCOMPLETE",
            "%s key 't_b' absent or empty — no permutation family to "
            "score against" % what)
    for i, t in enumerate(tb):
        if not _is_num(t):
            die("ERR_DDC0_MALFORMED",
                "%s t_b[%d] must be a finite number (got %r)"
                % (what, i, t))
    return null


def load_candidates(path):
    rows = _load_jsonl(path, "candidates")
    if not rows:
        die("ERR_DDC0_FAMILY_INCOMPLETE",
            "candidates file carries zero rows — nothing was scored")
    seen = {}
    for ln, r in enumerate(rows, 1):
        what = "candidates row %d" % ln
        for k in CAND_FIELDS:
            if k not in r:
                die("ERR_DDC0_MALFORMED", "%s missing key %r" % (what, k))
        if not (_is_int(r["layer"]) and r["layer"] >= 0):
            die("ERR_DDC0_MALFORMED", "%s 'layer' must be int >= 0 "
                "(got %r)" % (what, r["layer"]))
        if r["method"] not in METHODS:
            die("ERR_DDC0_MALFORMED", "%s 'method' must be one of %r "
                "(got %r)" % (what, METHODS, r["method"]))
        if not (_is_int(r["dir_index"]) and r["dir_index"] >= 0):
            die("ERR_DDC0_MALFORMED", "%s 'dir_index' must be int >= 0 "
                "(got %r)" % (what, r["dir_index"]))
        for k in ("test_score", "carrier_half_cos", "minimal_contrast_p",
                  "bag_delta_ci90_low"):
            if not _is_num(r[k]):
                die("ERR_DDC0_MALFORMED", "%s %r must be a finite number "
                    "(got %r)" % (what, k, r[k]))
        key = (r["layer"], r["method"], r["dir_index"])
        if key in seen:
            die("ERR_DDC0_DUPLICATE",
                "candidate %d:%s:%d appears twice (rows %d and %d)"
                % (key[0], key[1], key[2], seen[key], ln))
        seen[key] = ln
    return rows


def _count_ge(sorted_tb, s):
    """#{b : t_b >= s} by binary search over the ascending-sorted null."""
    lo, hi = 0, len(sorted_tb)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_tb[mid] < s:
            lo = mid + 1
        else:
            hi = mid
    return len(sorted_tb) - lo


def _median(xs):
    ys = sorted(xs)
    n = len(ys)
    if n == 0:
        return None
    m = n // 2
    return ys[m] if n % 2 else (ys[m - 1] + ys[m]) / 2.0


def main():
    ap = argparse.ArgumentParser(
        description="ddc0 pre-registered analysis (DDC.md §2.3/§6/§8)")
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--maxstat-null", required=True)
    ap.add_argument("--sidecar", required=True)
    args = ap.parse_args()

    side = load_sidecar(args.sidecar)
    null = load_null(args.maxstat_null)
    rows = load_candidates(args.candidates)

    L = side["L"]
    k_cap = side["k_cap"]  # per-layer cap = min(d/2, 256) = k_cap (§2.3)
    j_cap = side["expected_dirs_per_layer_per_method"]
    tb_sorted = sorted(null["t_b"])
    n_tb = len(tb_sorted)

    # --- max-stat threshold t*: ceil(0.95*(B+1))-th order statistic of
    # {t_b} (§2.3 basis-assembly convention), index clamped to [0, B-1].
    # Consistent with the counting p below: at B=1000 a score is
    # criterion-1 admitted iff it STRICTLY exceeds t*.
    idx = min(max(int(math.ceil(0.95 * (n_tb + 1))) - 1, 0), n_tb - 1)
    t_star = tb_sorted[idx]

    # --- admission (ASM-1702; verdicts recomputed, never trusted) ---
    structural = {}   # (layer, method) -> [candidate dict + p]
    lexical = []      # criteria 1-3 pass, criterion 4 fails
    for r in rows:
        p = (1 + _count_ge(tb_sorted, r["test_score"])) / (n_tb + 1.0)
        c1 = p <= ALPHA                                  # max-stat
        c2 = r["carrier_half_cos"] >= CARRIER_COS_MIN    # carrier halves
        c3 = r["minimal_contrast_p"] <= ALPHA            # minimal contrast
        c4 = r["bag_delta_ci90_low"] > 0                 # bag-of-primes
        if c1 and c2 and c3:
            entry = dict(r, p=p)
            if c4:
                structural.setdefault((r["layer"], r["method"]),
                                      []).append(entry)
            else:
                lexical.append(entry)

    # per-layer cap (§2.3): keep the strongest k_cap structural admissions
    # per (layer, method) — test_score descending, ties -> lower
    # dir_index; overflow is demoted to non-admitted, never silently kept.
    for cell, lst in structural.items():
        lst.sort(key=lambda e: (-e["test_score"], e["dir_index"]))
        del lst[k_cap:]

    admitted = [e for lst in structural.values() for e in lst] + lexical

    # --- FORK-1 method selection + G0 routing (§2.3, §8) ---
    layers_by_method = {m: set() for m in METHODS}
    for (layer, method), lst in structural.items():
        if lst:
            layers_by_method[method].add(layer)
    n_ridge = len(layers_by_method["ridge-cca"])
    n_proc = len(layers_by_method["procrustes"])
    if n_ridge > n_proc:
        winning = "ridge-cca"
    elif n_proc > n_ridge:
        winning = "procrustes"
    else:
        winning = FORK1_TIE  # tie -> ridge-cca (pre-declared v1 default)
    n_layers_admitted = {"ridge-cca": n_ridge,
                         "procrustes": n_proc}[winning]
    ceil_third = int(math.ceil(L / 3.0))
    ge_third = n_layers_admitted >= ceil_third
    killed_by_g0 = not ge_third  # §8 G0 routing: A2 dropped below ceil(L/3)

    admitted_per_layer = {
        str(layer): len(lst)
        for (layer, method), lst in structural.items()
        if method == winning and lst}

    # --- FORK-2 pooling choice (§2.3 template-variance diagnostic) ---
    tmpl = side["template_variance_top_pc"]
    if tmpl["mean-pool"] <= TEMPLATE_VAR_MAX:
        fork2 = "mean-pool"       # pinned v1 pooling wins whenever valid
    elif tmpl["last-token"] <= TEMPLATE_VAR_MAX:
        fork2 = "last-token"
    else:
        fork2 = "template-dominated"

    # --- C4 expected-tie flag (§8) ---
    c4 = side["c4_subspace_overlap_per_layer"]  # all L layers (verified)
    c4_all = all(v >= C4_TIE_BOUND for v in c4.values())

    # --- gates (computed from raw fields; failure = gate false, not ERR)
    sha1 = side["probe_fixture_sha_run1"]
    sha2 = side["probe_fixture_sha_run2"]
    split = side["split"]
    split_shas = (split["fit_sha256"], split["sel_sha256"],
                  split["test_sha256"])
    counts = {}
    for r in rows:
        counts[(r["layer"], r["method"])] = \
            counts.get((r["layer"], r["method"]), 0) + 1
    expected_cells = set((layer, m) for layer in range(L) for m in METHODS)
    family_complete = (
        null["B"] == EXPECTED_B
        and n_tb == EXPECTED_B
        and set(counts) == expected_cells
        and all(1 <= c <= j_cap for c in counts.values()))
    gates = {
        "probe_fixture_deterministic": (
            _is_hex64(sha1) and _is_hex64(sha2) and sha1 == sha2),
        "split_integrity_valid": (
            split["overlap_empty"]
            and split["n_fit"] + split["n_sel"] + split["n_test"]
            >= SPLIT_MIN_TOTAL
            and all(_is_hex64(s) for s in split_shas)
            and len(set(split_shas)) == 3),
        "permutation_family_complete": family_complete,
    }

    analysis = {
        "n_layers_admitted": n_layers_admitted,
        "n_layers_admitted_ge_third": ge_third,
        "killed_by_g0": killed_by_g0,
        "winning_method": winning,
        "fork1_method_choice": winning,
        "fork2_pooling_choice": fork2,
        "n_layers_admitted_ridge_cca": n_ridge,
        "n_layers_admitted_procrustes": n_proc,
        "admitted_directions_per_layer": admitted_per_layer,
        "max_stat_threshold": t_star,
        "max_stat_p_admitted": {
            "%d:%s:%d" % (e["layer"], e["method"], e["dir_index"]): e["p"]
            for e in admitted},
        "carrier_half_stability": {
            "n_admitted": len(admitted),
            "min": (min(e["carrier_half_cos"] for e in admitted)
                    if admitted else None),
            "median": _median([e["carrier_half_cos"] for e in admitted]),
        },
        "minimal_contrast_survival": {
            "n_admitted": len(admitted),
            "max_p": (max(e["minimal_contrast_p"] for e in admitted)
                      if admitted else None),
        },
        "bag_of_primes_lexical_flags": sorted(
            ("%d:%s:%d" % (e["layer"], e["method"], e["dir_index"])
             for e in lexical),
            key=lambda s: (int(s.split(":")[0]), s.split(":")[1],
                           int(s.split(":")[2]))),
        "c4_subspace_overlap_per_layer": {str(int(k)): float(v)
                                          for k, v in c4.items()},
        "c4_overlap_ge_09_all_layers": c4_all,
        "template_variance_top_pc": {"mean-pool": tmpl["mean-pool"],
                                     "last-token": tmpl["last-token"]},
    }

    out = {"gates": gates, "analysis": analysis}
    # constraint-2 discipline: the emitted paths must be exactly
    # OUTPUT_FIELDS — an internal-invariant check, fail closed.
    paths = (["/gates/%s" % k for k in gates]
             + ["/analysis/%s" % k for k in analysis])
    if sorted(paths) != sorted(OUTPUT_FIELDS):
        die("ERR_DDC0_MALFORMED",
            "internal invariant violated: emitted fields != OUTPUT_FIELDS")
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
