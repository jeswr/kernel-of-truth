"""MECHANICAL per-cell acceptance verdict for the 99a frozen grid (OPUS).

Pure function of the frozen S6/S7 criteria + the raw grid results.  NO science,
NO interpretation: it only applies the pre-declared thresholds.

S6 FWER  : PASS iff CP-upper95(fwer_events, R) <= tau_FWER = 0.055 (every cell),
           where fwer_events is the REGISTERED realised OBSERVED count (S4.2/S9:
           the numerical guard does NOT change this statistic; the worst-case
           failures-as-events count is reported as a NON-GATING sensitivity).
           F10 also: whole-branch termination CP-upper95 <= tau_term0 = 0.055.
S7 power : floored cells PASS iff CP-lower95(path) >= 0.90 at the ESCALATED
           sample-size level (base reported alongside).  P6: termination
           CP-upper95 <= tau_term = 0.025.  (Whether the design MEETS the floors
           is a SCIENTIFIC question for the design owner — reported, not concluded.)
gate-cal : per (arm, gamma) CP-upper95 <= 1.25*gamma; SD-ratio (mechanism) >= 1.

RUN-VALIDITY (separate from S6/S7 acceptance — Rev2): the run is INVALID (its
S6/S7 verdicts are NOT an acceptance) unless ALL of: every expected cell is
present as a SUCCESSFUL result (no ERROR cells, no missing indices), every
fwer/power cell carries the fit-failure fields, and every cell's per-cell
fit-failure rate <= the S4.2 ceiling 0.1%.
"""
import sys
import os
import json
import math

SIM = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"
OUTDIR = os.path.join(SIM, "results", "frozen-run", "grid-run-v2")
sys.path.insert(0, SIM)
import grid

TAU_FWER = 0.055
TAU_TERM0 = 0.055
TAU_TERM = 0.025
POWER_FLOOR = 0.90
FIT_FAILURE_CEILING = 0.001            # S4.2 per-cell run-validity ceiling
N_EXPECTED_CELLS = 114                 # full 99a grid (S8 config table)

# floored power estimands (S7); the driver path key that carries each
FLOORED = {"P1": "CVAL_DEFNSUP", "P3": "CVAL_CONSUPH_GRAPH", "P4": "CFMTH_given_conH"}
REPORTED = {"P2": "CDEFSUP", "P5": "CCONSUP_A1"}

# EXPECTED index -> (kind, label, rho, regime, n_nat, n_nonce) from the S8
# enumeration; the SINGLE source of truth for the run scope (Rev4 item 3).
EXPECTED = {c[0]: tuple(c[1:]) for c in grid.enumerate_cells()}
# labels whose cells MUST carry a rung-0 whole-branch-termination record
_RUNG0_LABELS = {"F10", "P6"}
# the five power path estimands the driver emits (content, not just presence)
_POWER_PATHS = ("CVAL_DEFNSUP", "CVAL_CONSUPH_GRAPH", "CDEFSUP", "CCONSUP_A1",
                "CFMTH_given_conH")
_GATE_GAMMAS = ("0.02500", "0.00625")
# Pinned S4.4 gate-cal arm set (Rev5 — cross-vendor review finding 2): a
# gate-cal record is valid ONLY with EXACTLY these four arms; a one-arm
# {"H": ...} record, or any missing/extra arm, is structurally INVALID.
_PINNED_GATE_ARMS = frozenset(("H", "A2IR", "A2", "A1"))

# REQUIRED base schema per kind (Rev3/Rev4 — full-schema + content enforcement).
_FWER_POWER_REQUIRED = ("fwer_events", "fwer_hat", "fwer_cp_upper95",
                        "fwer_events_worstcase", "fwer_cp_upper95_worstcase",
                        "fit_failures", "fit_failure_rate",
                        "fit_failure_ceiling_pass", "fit_failure_detail",
                        "R", "truth_set")
_GATECAL_REQUIRED = ("arms", "R", "fit_failures", "fit_failure_rate",
                     "fit_failure_ceiling_pass")
# Rev6 (review finding 1): the six-field config identity a VALID gate-cal
# record MUST carry, required PRESENT and matched WITHOUT substitution.
_GATECAL_IDENTITY = ("label", "rho", "regime", "n_nat", "n_nonce")


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _rate_ok(rec, R):
    """fit_failure_rate must be FINITE, nonnegative, fit_failures a valid count,
    and rate CONSISTENT with fit_failures/R (Rev4 item 3c)."""
    ff = rec.get("fit_failures"); rate = rec.get("fit_failure_rate")
    if not (isinstance(ff, int) and not isinstance(ff, bool) and 0 <= ff <= R):
        return False
    if not (_num(rate) and math.isfinite(rate) and rate >= 0.0):
        return False
    return abs(rate - ff / R) <= 1e-9


def _valid_success(rec, exp):
    """Structural + CONTENT + mapping validity of ONE successful cell record
    against its EXPECTED (kind, label, rho, regime, n_nat, n_nonce) — Rev4
    item 3.  Returns (ok, reason).  Fail-closed on any mismatch: wrong kind,
    wrong config, missing schema, missing content (power paths / rung-0 / gate
    arms+gammas), or a fit-failure rate that is non-finite / negative /
    inconsistent with fit_failures/R.  The CEILING is recomputed separately."""
    if "ERROR" in rec:
        return False, "error"
    exp_kind, exp_label, exp_rho, exp_regime, exp_nnat, exp_nnonce = exp
    kind = rec.get("_kind") or rec.get("kind")
    if kind != exp_kind:
        return False, "kind %r != expected %r" % (kind, exp_kind)
    if kind in ("fwer", "power"):
        miss = [k for k in _FWER_POWER_REQUIRED if k not in rec]
        if miss:
            return False, "missing:" + ",".join(miss)
        if (rec.get("label") != exp_label or rec.get("rho") != exp_rho
                or rec.get("regime") != exp_regime or rec.get("n_nat") != exp_nnat
                or rec.get("n_nonce") != exp_nnonce):
            return False, "config-mismatch"
        R = rec.get("R")
        if not (isinstance(R, int) and R > 0):
            return False, "bad-R"
        ev = rec.get("fwer_events")
        if not (isinstance(ev, int) and 0 <= ev <= R):
            return False, "bad-fwer_events"
        if not _rate_ok(rec, R):
            return False, "rate-inconsistent"
        if not isinstance(rec.get("fit_failure_detail"), list):
            return False, "bad-detail"
        if kind == "power":
            paths = rec.get("paths")
            if not isinstance(paths, dict) or any(k not in paths for k in _POWER_PATHS):
                return False, "missing-power-paths"
        if exp_label in _RUNG0_LABELS:
            rung0 = rec.get("rung0")
            if not (isinstance(rung0, dict) and "cp_upper95" in rung0
                    and "termination_rate" in rung0):
                return False, "missing-rung0"
        return True, "ok"
    elif kind == "gatecal":
        miss = [k for k in _GATECAL_REQUIRED if k not in rec]
        if miss:
            return False, "missing:" + ",".join(miss)
        # FULL SIX-FIELD config identity (Rev6 finding 1): label, rho, regime,
        # n_nat, n_nonce ALL PRESENT and MATCHING — a MISSING regime / n_nat is
        # REJECTED, NEVER substituted with the expected value (the Rev5
        # `.get(fld, expected)` default let a beta / wrong-n_nat payload with
        # the fields absent tabulate as the required Gaussian/48 cell).
        id_miss = [k for k in _GATECAL_IDENTITY if k not in rec]
        if id_miss:
            return False, "missing-identity:" + ",".join(id_miss)
        if (rec["label"] != exp_label or rec["rho"] != exp_rho
                or rec["regime"] != exp_regime or rec["n_nat"] != exp_nnat
                or rec["n_nonce"] != exp_nnonce):
            return False, "config-mismatch"
        R = rec.get("R")
        if not (isinstance(R, int) and R > 0):
            return False, "bad-R"
        if not _rate_ok(rec, R):
            return False, "rate-inconsistent"
        arms = rec.get("arms")
        # EXACT pinned arm set (Rev5 finding 2): a missing OR extra arm is
        # invalid — a one-arm {"H": ...} record must be refused.
        if not (isinstance(arms, dict)
                and set(arms.keys()) == set(_PINNED_GATE_ARMS)):
            return False, "gate-arms!=pinned{H,A2IR,A2,A1}"
        for a in arms.values():
            if not isinstance(a, dict):
                return False, "bad-gate-arm"
            sd = a.get("sd_ratio")
            # numeric, non-NaN (the battery emits +inf on a degenerate zero
            # empirical SD; NaN is fail-closed invalid)
            if not (_num(sd) and not math.isnan(sd)):
                return False, "bad-gate-arm"
            g = a.get("gamma")
            if not (isinstance(g, dict) and all(k in g for k in _GATE_GAMMAS)):
                return False, "bad-gate-arm"
            for k in _GATE_GAMMAS:
                gg = g[k]
                cpu = gg.get("cp_upper95") if isinstance(gg, dict) else None
                # the RAW value the verdict recomputes PASS from must be a
                # finite number (Rev5 finding 3 depends on it)
                if not (_num(cpu) and math.isfinite(cpu)):
                    return False, "bad-gate-arm"
        return True, "ok"
    return False, "unknown-kind %r" % kind


def main():
    src = os.path.join(OUTDIR, "grid-results.json")
    data = json.load(open(src))
    rows = data["results"]
    from collections import defaultdict
    idx_rows = defaultdict(list)
    for r in rows:
        if "config_index" in r:
            idx_rows[r["config_index"]].append(r)
    by_idx = {i: l[0] for i, l in idx_rows.items()}

    fwer_rows, power_rows, gate_rows = [], [], []
    fwer_fail, power_floor_fail, gate_fail = [], [], []
    term_rows = []
    # RUN-VALIDITY accumulators (Rev2/Rev3 — separate from S6/S7 acceptance)
    error_cells = []          # cells that raised (durable ERROR record)
    ceiling_fail = []         # cells whose INDEPENDENTLY-recomputed rate > ceiling
    invalid_cells = []        # (idx, reason): schema/duplicate/unknown-kind breaches
    wc_max_cp_upper = 0.0     # worst-case (failures-as-events) CP-upper, disclosed

    # ---- INDEPENDENT run-validity pass over EVERY expected index (Rev3) ----
    # Requires exactly ONE structurally-valid successful record per index in
    # 0..N-1, the full schema on each, and recomputes the ceiling from the
    # numeric rate (never the stored boolean).
    missing_cells = [i for i in range(N_EXPECTED_CELLS) if i not in idx_rows]
    unexpected_idx = sorted(i for i in idx_rows if i not in EXPECTED)
    for u in unexpected_idx:
        invalid_cells.append((u, "unexpected-index"))
    valid_idx = set()
    for i in range(N_EXPECTED_CELLS):
        recs = idx_rows.get(i, [])
        if len(recs) == 0:
            continue                          # counted in missing_cells
        if len(recs) != 1:
            invalid_cells.append((i, "duplicate x%d" % len(recs)))
            continue
        rec = recs[0]
        if "ERROR" in rec:
            error_cells.append(i)
            print("ERROR CELL (run-invalidating):", i, rec.get("ERROR"))
            continue
        ok, why = _valid_success(rec, EXPECTED[i])
        if not ok:
            invalid_cells.append((i, why))
            continue
        valid_idx.add(i)
        # INDEPENDENT ceiling recompute (do NOT trust fit_failure_ceiling_pass)
        if float(rec["fit_failure_rate"]) > FIT_FAILURE_CEILING:
            ceiling_fail.append(i)

    for r in rows:
        idx = r.get("config_index")
        # Only tabulate STRUCTURALLY-VALID cells; ERROR/invalid/malformed records
        # are recorded in the validity pass above and must NOT reach the
        # (structure-trusting) table code below (Rev4 — fail-closed, no crash).
        if idx not in valid_idx:
            continue
        kind = r.get("_kind") or r.get("kind")
        if kind == "fwer":
            cpu = r["fwer_cp_upper95"]                 # REGISTERED gate (observed)
            passed = cpu <= TAU_FWER
            cpu_wc = r.get("fwer_cp_upper95_worstcase", cpu)  # NON-GATING sensitivity
            wc_max_cp_upper = max(wc_max_cp_upper, cpu_wc)
            fwer_rows.append((idx, r["label"], r["rho"], r["regime"],
                              (r["n_nat"], r["n_nonce"]), len(r["truth_set"]),
                              r["fwer_events"], r["fwer_hat"], r["fwer_mcse"], cpu,
                              passed, r.get("fit_failures", 0), cpu_wc))
            if not passed:
                fwer_fail.append(idx)
            if "rung0" in r:  # F10 termination
                t = r["rung0"]
                tp = t["cp_upper95"] <= TAU_TERM0
                term_rows.append((idx, r["label"], r["rho"], "F10/tau_term0=0.055",
                                  t["termination_rate"], t["cp_upper95"], tp))
                if not tp:
                    fwer_fail.append(f"{idx}-term")
        elif kind == "power":
            label = r["label"]
            n = (r["n_nat"], r["n_nonce"])
            esc = (n == (96, 160))
            paths = r.get("paths", {})
            # floored estimand
            floored_key = FLOORED.get(label)
            floored_rate = floored_cpl = None
            floored_pass = None
            if floored_key and floored_key in paths:
                pd = paths[floored_key]
                if floored_key == "CFMTH_given_conH":
                    ch = pd.get("n_cond") or 0
                    rate = pd.get("rate")
                    if rate is not None and ch:
                        from math import isclose
                        k = round(rate * ch)
                        # exact CP-lower on the conditional
                        from scipy import stats
                        floored_cpl = float(stats.beta.ppf(0.05, k, ch - k + 1)) if k > 0 else 0.0
                        floored_rate = rate
                else:
                    floored_rate = pd.get("rate")
                    floored_cpl = pd.get("cp_lower95")
                if esc and floored_cpl is not None:
                    floored_pass = floored_cpl >= POWER_FLOOR
                    if not floored_pass:
                        power_floor_fail.append(idx)
            power_rows.append((idx, label, r["rho"], n, esc, floored_key,
                               floored_rate, floored_cpl, floored_pass, paths))
            if "rung0" in r:  # P6 termination
                t = r["rung0"]
                tp = t["cp_upper95"] <= TAU_TERM
                term_rows.append((idx, label, r["rho"], "P6/tau_term=0.025",
                                  t["termination_rate"], t["cp_upper95"], tp))
                if not tp:
                    power_floor_fail.append(f"{idx}-term")
        elif kind == "gatecal":
            arms = r["arms"]
            min_sd = min(a["sd_ratio"] for a in arms.values())
            worst = {"0.02500": 0.0, "0.00625": 0.0}
            allpass = True
            for a in arms.values():
                # Rev5 (review finding 3): PASS is RECOMPUTED from the stored
                # RAW values — (cp_upper95 <= 1.25*gamma) AND (sd_ratio >= 1)
                # — the stored `pass` boolean is NEVER trusted (a lying
                # pass=True with cp_upper95=1.0 / sd_ratio=0.5 must tabulate
                # FAIL), and the R9a SD-ratio mechanism check is part of
                # allpass, not a side column.
                allpass = allpass and (a["sd_ratio"] >= 1.0)
                for g in ("0.02500", "0.00625"):
                    gg = a["gamma"][g]
                    cpu = gg["cp_upper95"]
                    worst[g] = max(worst[g], cpu)
                    allpass = allpass and (cpu <= 1.25 * float(g))
            gate_rows.append((idx, r["rho"], r["n_nonce"], min_sd,
                              worst["0.02500"], worst["0.00625"], allpass))
            if not allpass:
                gate_fail.append(idx)

    # ---- print tables ----
    print("\n================ S6 FWER ACCEPTANCE (tau_FWER=0.055; gate=OBSERVED) ======")
    print(f"{'idx':>3} {'label':6} {'rho':>4} {'regime':8} {'n':>9} {'|T|':>3} "
          f"{'events':>6} {'fwer':>8} {'mcse':>7} {'CPupper':>8} verdict "
          f"{'ff':>3} {'CPu_wc':>8}")
    for (idx, label, rho, regime, n, tsz, ev, fh, mc, cpu, p, ff, cpu_wc) in sorted(fwer_rows):
        print(f"{idx:>3} {label:6} {rho:>4} {regime:8} {str(n):>9} {tsz:>3} "
              f"{ev:>6} {fh:>8.5f} {mc:>7.5f} {cpu:>8.5f} "
              f"{'PASS' if p else 'FAIL *****'} {ff:>3} {cpu_wc:>8.5f}")
    n_fwer = len(fwer_rows)
    n_fwer_pass = sum(1 for x in fwer_rows if x[10])
    max_cpu = max((x[9] for x in fwer_rows), default=float("nan"))
    print(f"FWER cells: {n_fwer_pass}/{n_fwer} PASS  (max CP-upper "
          f"{max_cpu:.5f}; worst-case sensitivity max "
          f"CP-upper {wc_max_cp_upper:.5f} [NON-GATING])")

    print("\n================ S7 POWER (floor 0.90 at ESCALATED n) ================")
    print(f"{'idx':>3} {'label':6} {'rho':>4} {'n':>9} {'esc':>4} {'floored':22} "
          f"{'rate':>7} {'CPlower':>8} verdict")
    for (idx, label, rho, n, esc, fk, fr, fcpl, fp, paths) in sorted(power_rows):
        fr_s = f"{fr:.4f}" if fr is not None else "  -  "
        fcpl_s = f"{fcpl:.4f}" if fcpl is not None else "  -  "
        vd = ("PASS" if fp else "FAIL") if (esc and fp is not None) else ("base" if not esc else "n/a")
        print(f"{idx:>3} {label:6} {rho:>4} {str(n):>9} {str(esc):>4} {str(fk):22} "
              f"{fr_s:>7} {fcpl_s:>8} {vd}")
    # per-cell all reported paths
    print("\n  -- all reported path estimands per power cell --")
    for (idx, label, rho, n, esc, fk, fr, fcpl, fp, paths) in sorted(power_rows):
        ps = []
        for k, v in paths.items():
            if isinstance(v, dict):
                if "rate" in v and v["rate"] is not None:
                    cl = v.get("cp_lower95")
                    ps.append(f"{k}={v['rate']:.4f}" + (f"(CPl {cl:.4f})" if cl is not None else ""))
        print(f"  idx{idx:>3} {label} rho={rho} n={n}: " + "  ".join(ps))

    print("\n================ RUNG-0 TERMINATION (F10/P6) ================")
    for (idx, label, rho, tag, rate, cpu, p) in sorted(term_rows):
        print(f"  idx{idx:>3} {label:5} rho={rho} {tag}: term_rate={rate:.5f} "
              f"CPupper={cpu:.5f} {'PASS' if p else 'FAIL *****'}")

    print("\n================ S4.4 GATE-CAL BATTERY (R9a) ================")
    print(f"{'idx':>3} {'rho':>4} {'n_nonce':>7} {'minSDratio':>10} "
          f"{'worstCPu@.025':>13} {'worstCPu@.00625':>15} verdict")
    for (idx, rho, nn, msd, w25, w06, p) in sorted(gate_rows):
        print(f"{idx:>3} {rho:>4} {nn:>7} {msd:>10.3f} {w25:>13.5f} {w06:>15.5f} "
              f"{'PASS' if p else 'FAIL *****'}  (bars 0.03125 / 0.0078)")

    # ---- RUN VALIDITY (Rev2/Rev3 — gates whether S6/S7 verdicts are an acceptance) ----
    present = set(idx_rows.keys())
    n_valid_success = len(valid_idx & set(range(N_EXPECTED_CELLS)))
    run_valid = (not error_cells and not missing_cells
                 and not invalid_cells and not ceiling_fail
                 and n_valid_success == N_EXPECTED_CELLS)

    print("\n================ RUN VALIDITY (S4.2 / Rev3) ================")
    print(f"cells present: {len(present)}/{N_EXPECTED_CELLS}"
          + ("" if not missing_cells else f"  MISSING: {missing_cells}"))
    print(f"exactly-one-valid-success per index: {n_valid_success}/{N_EXPECTED_CELLS}")
    print(f"ERROR (unevaluable) cells: {len(error_cells)}"
          + ("" if not error_cells else f"  {sorted(x for x in error_cells if x is not None)}"))
    print(f"structurally-invalid (schema/duplicate) cells: {len(invalid_cells)}"
          + ("" if not invalid_cells else f"  {invalid_cells}"))
    print(f"fit-failure ceiling ({FIT_FAILURE_CEILING:g}) breaches "
          f"[INDEPENDENTLY recomputed from fit_failure_rate]: {len(ceiling_fail)}"
          + ("" if not ceiling_fail else f"  {ceiling_fail}"))
    print(f"RUN VALID: {run_valid}"
          + ("" if run_valid else "  -> S6/S7 verdicts below are NOT an acceptance"))

    print("\n================ MECHANICAL SUMMARY ================")
    print(f"FWER (S6, OBSERVED gate): {n_fwer_pass}/{n_fwer} cells CP-upper <= {TAU_FWER}  "
          f"{'ALL PASS' if not fwer_fail else 'FAIL: '+str(fwer_fail)}")
    print(f"  worst-case FWER sensitivity (failures-as-events, NON-GATING): "
          f"max CP-upper {wc_max_cp_upper:.5f}")
    n_gc_pass = sum(1 for x in gate_rows if x[-1])
    _min_sd = min((x[3] for x in gate_rows), default=float("nan"))
    print(f"Gate-cal(S4.4):{n_gc_pass}/{len(gate_rows)} cells all (arm,gamma) pass; "
          f"min SD-ratio {_min_sd:.3f} "
          f"{'ALL PASS' if not gate_fail else 'FAIL: '+str(gate_fail)}")
    esc_floored = [x for x in power_rows if x[4] and x[5] in FLOORED.values()]
    esc_pass = [x for x in esc_floored if x[8]]
    print(f"Power floors (S7, ESCALATED floored cells): {len(esc_pass)}/{len(esc_floored)} "
          f">= {POWER_FLOOR}  {'(none below)' if not power_floor_fail else 'BELOW-FLOOR/term: '+str(power_floor_fail)}")
    print("  (power-floor status is a SCIENTIFIC read for the design owner; "
          "reported here mechanically, not concluded.)")
    print(f"\n*** RUN {'VALID — S6/S7 verdicts stand' if run_valid else 'INVALID — NOT AN ACCEPTANCE'} ***")

    # machine-readable verdict object
    verdict = {
        "tau_FWER": TAU_FWER, "tau_term0": TAU_TERM0, "tau_term": TAU_TERM,
        "power_floor": POWER_FLOOR, "fit_failure_ceiling": FIT_FAILURE_CEILING,
        "run_valid": run_valid,
        "run_validity": {
            "cells_present": len(present), "n_expected": N_EXPECTED_CELLS,
            "n_valid_success": n_valid_success,
            "missing_cells": missing_cells,
            "error_cells": sorted(x for x in error_cells if x is not None),
            "invalid_cells": invalid_cells,
            "ceiling_fail": ceiling_fail,
        },
        "fwer": {"n": n_fwer, "n_pass": n_fwer_pass, "fails": fwer_fail,
                 "max_cp_upper": max((x[9] for x in fwer_rows), default=None),
                 "max_cp_upper_worstcase_sensitivity": wc_max_cp_upper},
        "gatecal": {"n": len(gate_rows), "n_pass": n_gc_pass, "fails": gate_fail,
                    "min_sd_ratio": min((x[3] for x in gate_rows), default=None)},
        "power": {"n_esc_floored": len(esc_floored), "n_esc_floored_meet": len(esc_pass),
                  "below_floor_or_term": power_floor_fail},
    }
    with open(os.path.join(OUTDIR, "mechanical-verdict.json"), "w") as f:
        json.dump(verdict, f, indent=2)
    print("\nwrote", os.path.join(OUTDIR, "mechanical-verdict.json"))


if __name__ == "__main__":
    main()
