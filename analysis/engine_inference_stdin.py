#!/usr/bin/env python3
# ENGINE-INF pre-registered analysis (stdin-conformant; verdict-gen P2 §3.1
# step 5 invokes this with the eligible results-log run records as JSONL on
# STDIN and no argv).
#
# Design: docs/next/design/engine-inference-under-typing.md §2.2-§2.3
# (scoring, divergence certificate, decision rule verbatim); build-level
# operationalisations ASM-1990..2009 (poc/engine-inference/asm-1990-2009.json):
#   ASM-1994 divergence signature (verdict + refusal + G2-side projection)
#   ASM-1997 G4 scoring rule (REFUSE or vacuous-CONSISTENT correct;
#            ANOMALOUS = confident wrong assertion)
#   ASM-1999 PRIMARY frame = decision-level Div(K, b) restricted to
#            G1/G3 (decisive third-party/constructed-rule gold) cells;
#            G4 cells feed the honesty-weighted secondary only
#   ASM-2000 delta lower bound: conservative exact-binomial (Clopper-
#            Pearson, one-sided alpha=0.05) on the discordant-pair win rate,
#            mapped to the delta scale conditional on the discordant count m:
#            delta_lb = (2*CP_LB(wins, m) - 1) * m / n_pri (0 when m = 0)
#
# INPUT CONTRACT: each eligible stdin record's `artifacts` must pin the
# runner outputs: rows_path/rows_sha256 (+ optional run_result_path/_sha256).
# Rows are loaded from the PINNED path, sha256 re-verified, fail closed.
# The analysis is a pure function of those bytes: divergence, scores and
# bands are RECOMPUTED from rows here — the committed certificate artifact
# is provenance, not an input.
#
# Statistics: deterministic engine => per-item outcomes are 0/1 census
# quantities over the finite item frame (design §2.3); Wilson-LB95
# (z=1.959963984540054) reported for the pre-registered generalization to
# Stage-B lemmas, tagged EXTRAPOLATION in any readout.

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Pre-registered constants (design §2.3 verbatim; changing any is a design
# change requiring a new freeze).
KILL_E1_MIN_DIV_DWORDDOM_FULL = 25
KILL_E1_MIN_OPS = 3
KILL_E1_MIN_LEMMAS = 3
KILL_E2_MIN_DIV_BWN_PRI = 10
PASS_K_WILSON_LB = 0.80
PASS_MIN_DELTA_BWN = 0.20
NO_NET_HARM_TOL = 0.02
Z95 = 1.959963984540054
CP_ALPHA = 0.05

ARMS = ("K", "K-shuf", "D-word-dom", "D-word-union", "B-wn")
BASELINES = ("D-word-dom", "D-word-union", "B-wn")


def fail(msg):
    print("ERR_P2_ANALYSIS: %s" % msg, file=sys.stderr)
    sys.exit(1)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wilson_lb(k, n, z=Z95):
    if n == 0:
        return 0.0
    ph = k / n
    d = 1 + z * z / n
    c = ph + z * z / (2 * n)
    e = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5)
    return (c - e) / d


def binom_tail_ge(k, n, p):
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    q = 1.0 - p
    if q <= 0:
        return 1.0
    term = q ** n
    cdf = 0.0
    for i in range(0, k):
        cdf += term
        term = term * (n - i) / (i + 1) * (p / q)
    return max(0.0, 1.0 - cdf)


def clopper_pearson_lb(k, n, alpha=CP_ALPHA):
    if n == 0 or k == 0:
        return 0.0
    lo, hi = 0.0, k / n
    for _ in range(60):
        mid = (lo + hi) / 2
        if binom_tail_ge(k, n, mid) >= alpha:
            hi = mid
        else:
            lo = mid
    return lo


def load_rows():
    """Eligible stdin run records -> verified per-item rows by (arm, item)."""
    eligible = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            fail("stdin line is not JSON")
        if rec.get("event") == "run" and rec.get("phase") == "final" \
                and rec.get("exit") == "ok":
            eligible.append(rec)
    if not eligible:
        fail("no eligible run records on stdin")
    rows_pins = set()
    for rec in eligible:
        art = rec.get("artifacts") or {}
        if not art.get("rows_path") or not art.get("rows_sha256"):
            fail("eligible record lacks artifacts.rows_path/rows_sha256")
        rows_pins.add((art["rows_path"], art["rows_sha256"]))
    if len(rows_pins) != 1:
        fail("eligible records pin DIFFERENT rows artifacts: %s"
             % sorted(rows_pins))
    path, want = next(iter(rows_pins))
    full = ROOT / path
    if not full.is_file():
        fail("pinned rows artifact missing: %s" % path)
    got = sha256_file(full)
    if got != want:
        fail("rows artifact sha256 %s != pinned %s" % (got, want))
    rows = {}
    for line in open(full):
        r = json.loads(line)
        rows[(r["arm"], r["item"])] = r
    return rows


def main():
    rows = load_rows()
    item_ids = sorted({i for (a, i) in rows if a == "K"})
    for arm in ARMS + ("oracle",):
        missing = [i for i in item_ids if (arm, i) not in rows]
        if missing:
            fail("arm %s missing %d item rows" % (arm, len(missing)))

    def sig(arm, iid):
        r = rows[(arm, iid)]
        return (r["verdict"], r["refusal"] or "", tuple(r["derived_sides"]))

    def dec(arm, iid):
        r = rows[(arm, iid)]
        return (r["verdict"], r["refusal"] or "")

    def is_pri(iid):
        return rows[("K", iid)]["gold_rule"] in ("G1+G2", "G3")

    def correct(arm, iid):
        return bool(rows[(arm, iid)]["correct"])

    # ---- divergence (recomputed from rows; ASM-1994) ----
    div_full = {b: [i for i in item_ids if sig("K", i) != sig(b, i)]
                for b in BASELINES}
    div_dec = {b: [i for i in item_ids if dec("K", i) != dec(b, i)]
               for b in BASELINES}
    d_pri = {b: [i for i in div_dec[b] if is_pri(i)] for b in BASELINES}

    def ops_of(b, iid):
        k, r = rows[("K", iid)], rows[(b, iid)]
        o = []
        if tuple(k["derived_sides"]) != tuple(r["derived_sides"]):
            o.append("O1")
        if (k["verdict"] == "ANOMALOUS") != (r["verdict"] == "ANOMALOUS"):
            o.append("O2")
        if (k["verdict"] == "REFUSE") != (r["verdict"] == "REFUSE"):
            o.append("O3")
        return o

    dd_ops = sorted({o for i in div_full["D-word-dom"]
                     for o in ops_of("D-word-dom", i)})
    dd_lemmas = sorted({rows[("K", i)]["lemma"]
                        for i in div_full["D-word-dom"]})

    kill_e1 = (len(div_full["D-word-dom"]) < KILL_E1_MIN_DIV_DWORDDOM_FULL
               or len(dd_ops) < KILL_E1_MIN_OPS
               or len(dd_lemmas) < KILL_E1_MIN_LEMMAS)
    kill_e2 = len(d_pri["B-wn"]) < KILL_E2_MIN_DIV_BWN_PRI

    # ---- primary contrast (design §2.3; frame ASM-1999) ----
    def delta_on(b):
        cells = d_pri[b]
        if not cells:
            return 0.0, 0, 0, 0
        kc = sum(1 for i in cells if correct("K", i))
        bc = sum(1 for i in cells if correct(b, i))
        wins = sum(1 for i in cells if correct("K", i) and not correct(b, i))
        losses = sum(1 for i in cells if not correct("K", i) and correct(b, i))
        return (kc - bc) / len(cells), kc, wins, losses

    delta_bwn, k_pri_correct, wins, losses = delta_on("B-wn")
    n_pri = len(d_pri["B-wn"])
    m = wins + losses
    delta_bwn_lb = ((2 * clopper_pearson_lb(wins, m) - 1) * m / n_pri
                    if n_pri and m else 0.0)
    k_pri_wilson = wilson_lb(k_pri_correct, n_pri)
    delta_dd = delta_on("D-word-dom")[0]
    delta_du = delta_on("D-word-union")[0]

    # ---- no-net-harm (design §2.3 PASS clause 4) ----
    harm_ok = True
    for b in BASELINES:
        conv = [i for i in item_ids if is_pri(i) and i not in set(div_dec[b])]
        if not conv:
            continue
        kc = sum(1 for i in conv if correct("K", i)) / len(conv)
        bc = sum(1 for i in conv if correct(b, i)) / len(conv)
        if kc < bc - NO_NET_HARM_TOL:
            harm_ok = False

    # ---- FAIL-deflate second clause: K < D-word-dom on Div(K,D-word-dom) ----
    dd_cells = d_pri["D-word-dom"]
    k_on_dd = (sum(1 for i in dd_cells if correct("K", i)) / len(dd_cells)
               if dd_cells else 1.0)
    dd_on_dd = (sum(1 for i in dd_cells if correct("D-word-dom", i))
                / len(dd_cells) if dd_cells else 0.0)

    band_pass = (not kill_e1 and not kill_e2
                 and k_pri_wilson >= PASS_K_WILSON_LB
                 and delta_bwn >= PASS_MIN_DELTA_BWN and delta_bwn_lb > 0
                 and delta_dd > 0 and delta_du > 0 and harm_ok)
    band_fail = (not kill_e1 and not kill_e2
                 and (delta_bwn <= 0 or k_on_dd < dd_on_dd))

    # ---- gates ----
    oracle_score = (sum(1 for i in item_ids if correct("oracle", i))
                    / len(item_ids) if item_ids else 0.0)
    census = {}
    honesty = {}
    for arm in ARMS:
        census[arm] = sum(1 for i in item_ids if correct(arm, i)) / len(item_ids)
        honesty[arm] = round(sum(rows[(arm, i)]["honesty_penalty"]
                                 for i in item_ids), 2)
    kshuf_diff = (sum(1 for i in item_ids if sig("K", i) != sig("K-shuf", i))
                  / len(item_ids))

    out = {
        "gates": {
            "oracle_score": oracle_score,
            "oracle_valid": oracle_score == 1.0,
            "rows_complete": True,
            "instrument_valid": oracle_score == 1.0,
        },
        "analysis": {
            "n_items": len(item_ids),
            "n_pri_frame": sum(1 for i in item_ids if is_pri(i)),
            "div_full_dworddom_n": len(div_full["D-word-dom"]),
            "div_full_dworddom_ops_n": len(dd_ops),
            "div_full_dworddom_lemmas_n": len(dd_lemmas),
            "div_dec_bwn_n": len(div_dec["B-wn"]),
            "div_pri_bwn_n": n_pri,
            "kill_e1_fired": kill_e1,
            "kill_e2_fired": kill_e2,
            "k_pri_correct_n": k_pri_correct,
            "k_pri_wilson_lb95": k_pri_wilson,
            "delta_k_minus_bwn_pri": delta_bwn,
            "delta_k_minus_bwn_lb95": delta_bwn_lb,
            "delta_k_minus_dworddom_pri": delta_dd,
            "delta_k_minus_dwordunion_pri": delta_du,
            "k_on_div_dworddom": k_on_dd,
            "dworddom_on_div_dworddom": dd_on_dd,
            "no_net_harm_ok": harm_ok,
            "band_pass_affirm": band_pass,
            "band_fail_deflate": band_fail,
            "kshuf_differs_from_k_frac": kshuf_diff,
            "census_correctness": census,
            "honesty_penalty_sum": honesty,
            "per_op_divergence_dworddom": {o: sum(1 for i in div_full["D-word-dom"]
                                                  if o in ops_of("D-word-dom", i))
                                           for o in ("O1", "O2", "O3")},
        },
    }
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
