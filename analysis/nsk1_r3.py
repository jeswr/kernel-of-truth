#!/usr/bin/env python3
"""nsk1-r3 analysis — pinned, verdict-gen-compatible endpoint computation for the
CONFIRMATORY hardened re-run of the internal-write keyed-delivery finding
(registry/experiments/nsk1-r3.json; design docs/next/design/nsk1-r3-hardened.md).

DRAFT / not yet pinned. The coordinator recomputes this file's sha256 and writes
it into registry/experiments/nsk1-r3.json /pins/analysis_script BEFORE freeze;
any later byte-change is a design change (new experiment id), never an amendment.

I/O contract (P2 §3.1 step 5, verified against tools/registry/verdict-gen.py):
  * reads eligible run rows as JSONL on STDIN (one JSON object per line);
  * writes ONE analysis JSON object to STDOUT (verdict-gen captures stdout and
    writes reports/auto/nsk1-r3/analysis-output.json). No argv, no files.
Stdlib only. Every statistic is pre-declared in the design doc §6/§9; the
verdict_rules consume only the /gates/* and /analysis/* booleans emitted here
(the eval_expr grammar has NO arithmetic — all arithmetic lives in this file).

The endpoint kept from B" (poc/nsk1/out/bprime2, MEASURED-exploratory): keyed
accuracy of the source-keyed counterfactual-pair margin read-out, real > coin,
floor 0.70, co-gated by real > role (item-specificity).  m = lp_top - lp_bridge;
success bit = [m(+) > m(-)]; ties / non-finite = failure.

FAIL-CLOSED COMPLETENESS GUARD (pre-freeze integrity review 2026-07-15,
defect 4): the confirmatory endpoint is DEFINED on the complete pre-registered
input — n = 266 items per cell (the MEASURED build fact,
data/nsk1-clutrr-r3/manifest.json, carried in the record's count_gate) with
ALL THREE declared derangement seeds per cell ({20260720,21,22} on A for C1,
{20260723,24,25} on B for C2) and both signs of every real/deranged margin
plus the coin bit present for every item. Any shortfall (missing seed, wrong
seed family, truncated partition, missing sign/coin rows) sets
/gates/endpoint_complete_c{1,2} = false, which (a) forces
/gates/instrument_valid = false (verdict INSTRUMENT-INVALID fires first) and
(b) independently forces c{1,2}_pass = false, so primary_confirmed /
confirmed_replicated can NEVER be true on incomplete input even if the
verdict rules were re-ordered. Without this guard a partial run (e.g. one
seed, or 200 of 266 items — still >= the 175 n-floor) could have PASSed the
pre-registered 3-seed / full-partition endpoint. `--selftest` proves the
guard (see _selftest below); verdict-gen invokes this file with NO argv, so
the stdin/stdout contract is unchanged.

The three Gate-A hardenings this file implements:
  (a) COMPLETE FWER PLAN.  Bonferroni over the WHOLE pre-registered family of
      6 elementary tests = {2 confirmatory cells} x {floor, real>coin, real>role}
      -> per-test alpha = 0.05/6 = 0.0083333 (z_floor = 2.3940).  The paired
      control tests are corrected across cells too (the B" spec corrected only
      the Wilson floor).  Conservative: each cell PASS is an intersection-union
      conjunction, so the true FWER is < 0.05.
  (b) GENUINELY INDEPENDENT CELLS.  The two confirmatory cells are read out on
      DISJOINT fresh item partitions (C1=(16,16) on A, C2=(12,16) on B) with
      distinct derangement-seed families; this script keys strictly by cell and
      never pools across the two cells' items.
  (c) CONFIRMATORY, NOT EXPLORATORY.  No cell search; the two cells and all
      thresholds are frozen constants below; PASS is emitted only for the single
      pre-registered PRIMARY hypothesis H1 (cell C1) and, per verdict-gen step 8,
      resolves to PASS-PENDING-AUDIT until a non-runner audit CONFIRMS.
"""
import json
import math
import sys
from math import comb

# ---- frozen design constants (part of the sha-pinned contract) -------------
C1 = (16, 16)          # PRIMARY confirmatory cell (ell_h, ell_t), on partition A
C2 = (12, 16)          # co-primary INDEPENDENT-REPLICATION cell, on partition B
FLOOR = 0.70           # keyed-accuracy floor kept from B"
ALPHA_FAMILY = 0.05    # target FWER across the 6-test family
N_ELEMENTARY = 6       # 2 cells x {floor, coin, role}
ALPHA_TEST = ALPHA_FAMILY / N_ELEMENTARY          # 0.00833... per test (Bonferroni)
N_COIN_SERIES = 6      # 2 cells x 3 derangement seeds (coin-validity tripwire family)
HEADROOM_LO, HEADROOM_HI = 0.05, 0.85
HEADROOM_MIN_N = 300   # scored text-only items required for a valid headroom read
MIN_N_CELL = 175       # below this the floor test is underpowered; fail closed (INSTRUMENT-INVALID)
# Pre-registered completeness endpoint (fail-closed; integrity review defect 4):
# the full disjoint partitions (n = 266 each, data/nsk1-clutrr-r3/manifest.json)
# and the declared per-cell derangement-seed families (design §6.2 / record
# design.n_planned.partitions). An incomplete run must NOT be able to PASS.
N_CELL_FULL = 266      # complete partition size per cell (MEASURED build fact)
SEEDS_BY_CELL = {C1: (20260720, 20260721, 20260722),   # partition A family
                 C2: (20260723, 20260724, 20260725)}   # partition B family


def _phi_inv(p):
    # Acklam rational approximation (index/threshold selection only).
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


Z_FLOOR = _phi_inv(1 - ALPHA_TEST)                 # 2.3940  (one-sided /6 Bonferroni)
Z_UB = _phi_inv(1 - 0.05)                          # 1.6449  (one-sided 95% UB, refutation)
Z_COIN_TRIP = _phi_inv(1 - 0.05 / (2 * N_COIN_SERIES))   # ~2.638 (two-sided, /6 coin series)


def wilson_lb(k, n, z):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d


def wilson_ub(k, n, z):
    if n == 0:
        return 1.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c + r) / d


def sign_p(b, c):
    """Exact one-sided binomial sign test: P(X >= b | n=b+c, 0.5). b = #(real & !ctrl)."""
    n = b + c
    if n == 0:
        return 1.0
    return sum(comb(n, i) for i in range(b, n + 1)) / (2.0 ** n)


def _finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def compute(rows):
    # text-only correctness map (for reported failure/correct substrata) -------
    text_correct = {}
    n_text_scored = 0
    n_text_correct = 0
    for r in rows:
        if r.get("probe") == "text-only":
            cid = r.get("item_id")
            ok = bool(r.get("correct"))
            text_correct[cid] = ok
            n_text_scored += 1
            n_text_correct += int(ok)
    acc_text = (n_text_correct / n_text_scored) if n_text_scored else 0.0
    headroom_ok = (HEADROOM_LO <= acc_text <= HEADROOM_HI) and n_text_scored >= HEADROOM_MIN_N

    # collect margins per (cell, item): real +/-, and per-seed drg +/- + coin bit
    def blank():
        return {"real": {}, "drg": {}, "coin_bit": {}}

    cells = {C1: {}, C2: {}}          # cell -> item_id -> {'real':{sign:m}, 'drg':{seed:{sign:m}}, 'coin_bit':{seed:bit}}
    nonfinite = 0
    for r in rows:
        if r.get("probe") != "margin":
            continue
        cell = tuple(r.get("cell") or [])
        if cell not in cells:
            continue
        item = r.get("item_id")
        arm = r.get("arm")
        sign = r.get("sign")
        lt_, lb_ = r.get("lp_top"), r.get("lp_bridge")
        if not (_finite(lt_) and _finite(lb_)):
            nonfinite += 1
            m = None
        else:
            m = lt_ - lb_
        d = cells[cell].setdefault(item, blank())
        if arm == "real":
            d["real"][sign] = m
        elif arm == "drg":
            s = r.get("seed")
            d["drg"].setdefault(s, {})[sign] = m
            d["coin_bit"][s] = int(r.get("coin"))

    def gt(a, b):
        return _finite(a) and _finite(b) and a > b

    def cell_report(cell):
        items = cells[cell]
        declared = SEEDS_BY_CELL[cell]           # the ONLY seeds the endpoint admits
        observed = sorted({s for d in items.values() for s in d["drg"].keys()})
        # ---- fail-closed completeness of the pre-registered endpoint ----
        # (defect-4 guard): full partition, exact declared seed family, both
        # real signs, both drg signs + coin bit at EVERY declared seed, for
        # EVERY item. Any shortfall => complete=False => cell can never PASS
        # and the instrument gate fails (INSTRUMENT-INVALID).
        complete = (len(items) == N_CELL_FULL) and (observed == sorted(declared))
        if complete:
            for d in items.values():
                if not (1 in d["real"] and -1 in d["real"]):
                    complete = False
                    break
                for s in declared:
                    dd = d["drg"].get(s)
                    if dd is None or 1 not in dd or -1 not in dd or s not in d["coin_bit"]:
                        complete = False
                        break
                if not complete:
                    break
        seeds = sorted(declared)                  # tests iterate the DECLARED family
        ties = 0
        real_bits = {}
        for item, d in items.items():
            mp, mm = d["real"].get(1), d["real"].get(-1)
            if _finite(mp) and _finite(mm) and mp == mm:
                ties += 1
            real_bits[item] = 1 if gt(mp, mm) else 0
        n = len(items)
        k_real = sum(real_bits.values())
        keyacc_real = (k_real / n) if n else 0.0

        # per-seed coin / role bits
        coin_pass_all = bool(seeds)
        role_pass_all = bool(seeds)
        min_coin_p, min_role_p = 1.0, 1.0
        max_keyacc_coin, max_keyacc_role = 0.0, 0.0
        for s in seeds:
            coin_bits, role_bits = {}, {}
            for item, d in items.items():
                dd = d["drg"].get(s, {})
                mp, mm = dd.get(1), dd.get(-1)
                role = 1 if gt(mp, mm) else 0
                role_bits[item] = role
                bit = d["coin_bit"].get(s, 0)
                coin_bits[item] = role if bit == 1 else (1 if gt(mm, mp) else 0)
            max_keyacc_coin = max(max_keyacc_coin, sum(coin_bits.values()) / n if n else 0.0)
            max_keyacc_role = max(max_keyacc_role, sum(role_bits.values()) / n if n else 0.0)
            # paired real vs coin_s
            b = sum(1 for it in items if real_bits[it] == 1 and coin_bits[it] == 0)
            c = sum(1 for it in items if real_bits[it] == 0 and coin_bits[it] == 1)
            p_coin = sign_p(b, c)
            min_coin_p = min(min_coin_p, p_coin)
            if not (b > c and p_coin < ALPHA_TEST):
                coin_pass_all = False
            # paired real vs role_s
            b = sum(1 for it in items if real_bits[it] == 1 and role_bits[it] == 0)
            c = sum(1 for it in items if real_bits[it] == 0 and role_bits[it] == 1)
            p_role = sign_p(b, c)
            min_role_p = min(min_role_p, p_role)
            if not (b > c and p_role < ALPHA_TEST):
                role_pass_all = False

        lb_floor = wilson_lb(k_real, n, Z_FLOOR)
        ub = wilson_ub(k_real, n, Z_UB)
        floor_pass = (n >= MIN_N_CELL) and (lb_floor >= FLOOR)
        # coin-validity tripwire: coin keyacc statistically above chance => broken plumbing
        coin_valid = wilson_lb(int(round(max_keyacc_coin * n)), n, Z_COIN_TRIP) <= 0.5

        # reported substrata (never gated)
        def sub_acc(pred):
            ks = [real_bits[it] for it in items if pred(text_correct.get(it))]
            return (sum(ks) / len(ks)) if ks else None
        return {
            "n": n, "ties": ties, "seeds": seeds, "seeds_observed": observed,
            "complete": bool(complete),
            "keyacc_real": keyacc_real,
            "wilson_lb_floor": lb_floor, "wilson_ub": ub,
            "floor_pass": floor_pass,
            "coin_pass": coin_pass_all, "role_pass": role_pass_all,
            # defect-4 guard: a cell PASS additionally requires the complete
            # pre-registered input (full 266-item partition + all 3 declared
            # seeds) — an incomplete run can never yield cell_pass=True.
            "cell_pass": bool(floor_pass and coin_pass_all and role_pass_all and complete),
            "role_generic": bool(floor_pass and coin_pass_all and not role_pass_all),
            "min_coin_p": min_coin_p, "min_role_p": min_role_p,
            "keyacc_coin_max": max_keyacc_coin, "keyacc_role_max": max_keyacc_role,
            "coin_valid": coin_valid,
            "keyacc_real_fail_sub": sub_acc(lambda ok: ok is False),
            "keyacc_real_correct_sub": sub_acc(lambda ok: ok is True),
        }

    r1 = cell_report(C1)
    r2 = cell_report(C2)

    coin_validity_ok = bool(r1["coin_valid"] and r2["coin_valid"])
    n_ok = (r1["n"] >= MIN_N_CELL) and (r2["n"] >= MIN_N_CELL)
    endpoint_complete = bool(r1["complete"] and r2["complete"])
    instrument_valid = bool(headroom_ok and coin_validity_ok and nonfinite == 0
                            and n_ok and endpoint_complete)

    # defect-4 guard, belt-and-braces: the pre-registered run is BOTH cells'
    # complete partitions; primary_confirmed (and hence a PASS verdict) can
    # never be true unless the WHOLE declared input is present — independent
    # of the verdict rules' evaluation order.
    primary_confirmed = bool(r1["cell_pass"] and endpoint_complete)
    confirmed_replicated = bool(r1["cell_pass"] and r2["cell_pass"] and endpoint_complete)
    refuted = bool((r1["wilson_ub"] < FLOOR) and (r2["wilson_ub"] < FLOOR))
    primary_role_generic = bool(r1["role_generic"])

    out = {
        "gates": {
            "instrument_valid": instrument_valid,
            "headroom_ok": bool(headroom_ok),
            "coin_validity_ok": coin_validity_ok,
            "endpoint_complete": endpoint_complete,
            "endpoint_complete_c1": r1["complete"],
            "endpoint_complete_c2": r2["complete"],
            "seeds_observed_c1": r1["seeds_observed"],
            "seeds_observed_c2": r2["seeds_observed"],
            "acc_text_only": acc_text,
            "n_text_scored": n_text_scored,
            "nonfinite_count": nonfinite,
            "n_c1": r1["n"], "n_c2": r2["n"],
            "ties_c1": r1["ties"], "ties_c2": r2["ties"],
        },
        "analysis": {
            "alpha_per_test": ALPHA_TEST, "z_floor": Z_FLOOR, "floor": FLOOR,
            "primary_confirmed": primary_confirmed,
            "confirmed_replicated": confirmed_replicated,
            "refuted": refuted,
            "primary_role_generic": primary_role_generic,
            # primary cell C1 = (16,16) on partition A
            "c1_keyacc_real": r1["keyacc_real"],
            "c1_wilson_lb_floor": r1["wilson_lb_floor"],
            "c1_wilson_ub": r1["wilson_ub"],
            "c1_floor_pass": r1["floor_pass"],
            "c1_coin_pass": r1["coin_pass"], "c1_role_pass": r1["role_pass"],
            "c1_pass": r1["cell_pass"],
            "c1_min_coin_p": r1["min_coin_p"], "c1_min_role_p": r1["min_role_p"],
            "c1_keyacc_coin_max": r1["keyacc_coin_max"], "c1_keyacc_role_max": r1["keyacc_role_max"],
            "c1_keyacc_real_fail_sub": r1["keyacc_real_fail_sub"],
            "c1_keyacc_real_correct_sub": r1["keyacc_real_correct_sub"],
            # replication cell C2 = (12,16) on partition B
            "c2_keyacc_real": r2["keyacc_real"],
            "c2_wilson_lb_floor": r2["wilson_lb_floor"],
            "c2_wilson_ub": r2["wilson_ub"],
            "c2_floor_pass": r2["floor_pass"],
            "c2_coin_pass": r2["coin_pass"], "c2_role_pass": r2["role_pass"],
            "c2_pass": r2["cell_pass"],
            "c2_min_coin_p": r2["min_coin_p"], "c2_min_role_p": r2["min_role_p"],
            "c2_keyacc_coin_max": r2["keyacc_coin_max"], "c2_keyacc_role_max": r2["keyacc_role_max"],
            "c2_keyacc_real_fail_sub": r2["keyacc_real_fail_sub"],
            "c2_keyacc_real_correct_sub": r2["keyacc_real_correct_sub"],
        },
    }
    return out


def main():
    """verdict-gen entrypoint: JSONL rows on STDIN -> one JSON object on STDOUT."""
    rows = [json.loads(l) for l in sys.stdin if l.strip()]
    out = compute(rows)
    sys.stdout.write(json.dumps(out, sort_keys=True, separators=(",", ":")))
    sys.stdout.write("\n")
    return 0


# ------------------------------------------------------------------ selftest
def _st_rows(keyacc_c1=0.86, keyacc_c2=0.83, n_c1=N_CELL_FULL, n_c2=N_CELL_FULL,
             seeds_c1=None, seeds_c2=None, text_acc=0.79):
    """Deterministic synthetic row world for --selftest (never evidence).

    real success bits: the first round(keyacc*n) items; role bits ~0.5
    ((i+seed)%2); coin bits ~0.5 (independent hash-free pattern). At
    keyacc >= ~0.8 the floor / real>coin / real>role conjuncts all clear the
    /6 plan; at 0.50 both cells' Wilson UB < 0.70 (refuted)."""
    seeds_c1 = list(SEEDS_BY_CELL[C1]) if seeds_c1 is None else seeds_c1
    seeds_c2 = list(SEEDS_BY_CELL[C2]) if seeds_c2 is None else seeds_c2
    rows = []
    for cell, n, ka, seeds, tag in ((C1, n_c1, keyacc_c1, seeds_c1, "a"),
                                    (C2, n_c2, keyacc_c2, seeds_c2, "b")):
        k = int(round(ka * n))
        for i in range(n):
            iid = "st-%s%04d" % (tag, i)
            rows.append({"probe": "text-only", "item_id": iid,
                         "correct": (i % 100) < int(round(text_acc * 100))})
            succ = i < k
            rows.append({"probe": "margin", "cell": list(cell), "item_id": iid,
                         "arm": "real", "sign": 1,
                         "lp_top": -1.0 if succ else -2.0, "lp_bridge": -2.0})
            rows.append({"probe": "margin", "cell": list(cell), "item_id": iid,
                         "arm": "real", "sign": -1,
                         "lp_top": -2.0 if succ else -1.0, "lp_bridge": -2.0})
            for s in seeds:
                role = (i + s) % 2                      # ~0.5 role band
                coin_bit = ((i // 2) + s) % 2           # ~0.5 coin band
                rows.append({"probe": "margin", "cell": list(cell), "item_id": iid,
                             "arm": "drg", "sign": 1, "seed": s, "coin": coin_bit,
                             "lp_top": -1.0 if role else -2.0, "lp_bridge": -2.0})
                rows.append({"probe": "margin", "cell": list(cell), "item_id": iid,
                             "arm": "drg", "sign": -1, "seed": s, "coin": coin_bit,
                             "lp_top": -2.0 if role else -1.0, "lp_bridge": -2.0})
    return rows


def _selftest():
    """Prove both endpoint branches AND the defect-4 fail-closed guard: every
    incomplete-input world must be REJECTED (endpoint_complete=false,
    instrument_valid=false, primary_confirmed=false) even when its partial
    data would otherwise clear floor/coin/role."""
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))
        print("  %-52s %s" % (name + ":", "PASS" if cond else "FAIL"))

    print("=== nsk1_r3 --selftest (synthetic rows; never evidence) ===")
    # (1) complete PASS world
    o = compute(_st_rows())
    ck("complete world -> endpoint_complete", o["gates"]["endpoint_complete"])
    ck("complete world -> instrument_valid", o["gates"]["instrument_valid"])
    ck("complete world -> primary_confirmed", o["analysis"]["primary_confirmed"])
    ck("complete world -> confirmed_replicated", o["analysis"]["confirmed_replicated"])
    # (2) null world -> refuted (completeness intact)
    o = compute(_st_rows(keyacc_c1=0.50, keyacc_c2=0.50))
    ck("null world -> refuted", o["analysis"]["refuted"])
    ck("null world -> NOT primary_confirmed", not o["analysis"]["primary_confirmed"])
    ck("null world -> instrument_valid (complete input)", o["gates"]["instrument_valid"])

    def rejected(o):
        return (not o["gates"]["endpoint_complete"]
                and not o["gates"]["instrument_valid"]
                and not o["analysis"]["primary_confirmed"]
                and not o["analysis"]["confirmed_replicated"])
    # (3) missing seed: drop the third declared C1 seed entirely
    o = compute(_st_rows(seeds_c1=[20260720, 20260721]))
    ck("missing C1 seed (2 of 3) -> REJECTED fail-closed", rejected(o))
    # (4) truncated partition: 200 items (>= the 175 n-floor — the exact
    #     pre-guard hole: floor/coin/role would clear on this partial world)
    o = compute(_st_rows(n_c1=200))
    ck("truncated C1 partition (200<266) -> REJECTED", rejected(o))
    ck("truncated world clears floor+coin+role yet c1_pass=false (guard binds)",
       o["analysis"]["c1_floor_pass"] and o["analysis"]["c1_coin_pass"]
       and o["analysis"]["c1_role_pass"] and not o["analysis"]["c1_pass"])
    # (5) wrong seed family: burned B\" seed substituted for a declared one
    o = compute(_st_rows(seeds_c1=[20260720, 20260721, 20260712]))
    ck("wrong C1 seed family (burned 20260712) -> REJECTED", rejected(o))
    # (6) missing sign rows: strip every real sign=-1 row at C2
    rows = [r for r in _st_rows()
            if not (r.get("arm") == "real" and r.get("sign") == -1
                    and tuple(r.get("cell") or []) == C2)]
    o = compute(rows)
    ck("missing real(-) rows at C2 -> REJECTED", rejected(o))
    # (7) missing coin bits: drop one seed's drg rows for a single C1 item
    rows = [r for r in _st_rows()
            if not (r.get("item_id") == "st-a0000" and r.get("arm") == "drg"
                    and r.get("seed") == 20260722)]
    o = compute(rows)
    ck("one item missing one seed's drg rows -> REJECTED", rejected(o))

    ok = all(c for _, c in checks)
    print("SELFTEST_%s (%d/%d)" % ("PASS" if ok else "FAIL",
                                   sum(c for _, c in checks), len(checks)))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(_selftest())
    sys.exit(main())
