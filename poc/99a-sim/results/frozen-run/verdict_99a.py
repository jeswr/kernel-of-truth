"""MECHANICAL per-cell acceptance verdict for the 99a frozen grid (OPUS).

Pure function of the frozen S6/S7 criteria + the raw grid results.  NO science,
NO interpretation: it only applies the pre-declared thresholds.

S6 FWER  : PASS iff CP-upper95(fwer_events, R) <= tau_FWER = 0.055 (every cell).
           F10 also: whole-branch termination CP-upper95 <= tau_term0 = 0.055.
S7 power : floored cells PASS iff CP-lower95(path) >= 0.90 at the ESCALATED
           sample-size level (base reported alongside).  P6: termination
           CP-upper95 <= tau_term = 0.025.  (Whether the design MEETS the floors
           is a SCIENTIFIC question for the design owner — reported, not concluded.)
gate-cal : per (arm, gamma) CP-upper95 <= 1.25*gamma; SD-ratio (mechanism) >= 1.
"""
import sys
import os
import json

SIM = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"
OUTDIR = os.path.join(SIM, "results", "frozen-run", "grid-run")

TAU_FWER = 0.055
TAU_TERM0 = 0.055
TAU_TERM = 0.025
POWER_FLOOR = 0.90

# floored power estimands (S7); the driver path key that carries each
FLOORED = {"P1": "CVAL_DEFNSUP", "P3": "CVAL_CONSUPH_GRAPH", "P4": "CFMTH_given_conH"}
REPORTED = {"P2": "CDEFSUP", "P5": "CCONSUP_A1"}


def main():
    src = os.path.join(OUTDIR, "grid-results.json")
    data = json.load(open(src))
    rows = data["results"]
    by_idx = {r["config_index"]: r for r in rows if "config_index" in r}

    fwer_rows, power_rows, gate_rows = [], [], []
    fwer_fail, power_floor_fail, gate_fail = [], [], []
    term_rows = []

    for r in rows:
        if "ERROR" in r:
            print("ERROR CELL:", r.get("config_index"), r["ERROR"])
            continue
        kind = r.get("_kind") or r.get("kind")
        idx = r["config_index"]
        if kind == "fwer":
            cpu = r["fwer_cp_upper95"]
            passed = cpu <= TAU_FWER
            fwer_rows.append((idx, r["label"], r["rho"], r["regime"],
                              (r["n_nat"], r["n_nonce"]), len(r["truth_set"]),
                              r["fwer_events"], r["fwer_hat"], r["fwer_mcse"], cpu, passed))
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
                for g in ("0.02500", "0.00625"):
                    gg = a["gamma"][g]
                    worst[g] = max(worst[g], gg["cp_upper95"])
                    allpass = allpass and gg["pass"]
            gate_rows.append((idx, r["rho"], r["n_nonce"], min_sd,
                              worst["0.02500"], worst["0.00625"], allpass))
            if not allpass:
                gate_fail.append(idx)

    # ---- print tables ----
    print("\n================ S6 FWER ACCEPTANCE (tau_FWER=0.055) ================")
    print(f"{'idx':>3} {'label':6} {'rho':>4} {'regime':8} {'n':>9} {'|T|':>3} "
          f"{'events':>6} {'fwer':>8} {'mcse':>7} {'CPupper':>8} verdict")
    for (idx, label, rho, regime, n, tsz, ev, fh, mc, cpu, p) in sorted(fwer_rows):
        print(f"{idx:>3} {label:6} {rho:>4} {regime:8} {str(n):>9} {tsz:>3} "
              f"{ev:>6} {fh:>8.5f} {mc:>7.5f} {cpu:>8.5f} {'PASS' if p else 'FAIL *****'}")
    n_fwer = len(fwer_rows)
    n_fwer_pass = sum(1 for x in fwer_rows if x[-1])
    print(f"FWER cells: {n_fwer_pass}/{n_fwer} PASS  (max CP-upper "
          f"{max(x[9] for x in fwer_rows):.5f})")

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

    print("\n================ MECHANICAL SUMMARY ================")
    print(f"FWER (S6):     {n_fwer_pass}/{n_fwer} cells CP-upper <= {TAU_FWER}  "
          f"{'ALL PASS' if not fwer_fail else 'FAIL: '+str(fwer_fail)}")
    n_gc_pass = sum(1 for x in gate_rows if x[-1])
    print(f"Gate-cal(S4.4):{n_gc_pass}/{len(gate_rows)} cells all (arm,gamma) pass; "
          f"min SD-ratio {min(x[3] for x in gate_rows):.3f} "
          f"{'ALL PASS' if not gate_fail else 'FAIL: '+str(gate_fail)}")
    esc_floored = [x for x in power_rows if x[4] and x[5] in FLOORED.values()]
    esc_pass = [x for x in esc_floored if x[8]]
    print(f"Power floors (S7, ESCALATED floored cells): {len(esc_pass)}/{len(esc_floored)} "
          f">= {POWER_FLOOR}  {'(none below)' if not power_floor_fail else 'BELOW-FLOOR/term: '+str(power_floor_fail)}")
    print("  (power-floor status is a SCIENTIFIC read for the design owner; "
          "reported here mechanically, not concluded.)")

    # machine-readable verdict object
    verdict = {
        "tau_FWER": TAU_FWER, "tau_term0": TAU_TERM0, "tau_term": TAU_TERM,
        "power_floor": POWER_FLOOR,
        "fwer": {"n": n_fwer, "n_pass": n_fwer_pass, "fails": fwer_fail,
                 "max_cp_upper": max(x[9] for x in fwer_rows)},
        "gatecal": {"n": len(gate_rows), "n_pass": n_gc_pass, "fails": gate_fail,
                    "min_sd_ratio": min(x[3] for x in gate_rows)},
        "power": {"n_esc_floored": len(esc_floored), "n_esc_floored_meet": len(esc_pass),
                  "below_floor_or_term": power_floor_fail},
    }
    with open(os.path.join(OUTDIR, "mechanical-verdict.json"), "w") as f:
        json.dump(verdict, f, indent=2)
    print("\nwrote", os.path.join(OUTDIR, "mechanical-verdict.json"))


if __name__ == "__main__":
    main()
