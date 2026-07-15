#!/usr/bin/env python3
"""power_n1573.py — F1-K frozen-geometry exact-power confirmation ($0, blind).

Re-runs the pre-registered §R-REV5 exact cluster sign-flip joint-power sim
(the IDENTICAL procedure, constants and seed as poc/f1k-askability/screen.py
Part 3 — seed 20260713, N_sim=10000, b=10000 add-one-corrected flips,
delta=rho_U=0.10, fire iff p<0.05 AND T>=+3 pts, R=(1,3,1)) at the
MAINTAINER-APPROVED geometry (2026-07-15):

    C = 96 concepts, n_test = 1573 (the prior 1440 cap RAISED to 1573),
    mu* = +4.09 pts, R-vector = (1, 3, 1) for K-1 / K-2 / K-3.

The ONLY change vs the screen's Part-3 run is N_TEST 1440 -> 1573; the
allocation rule ([BC] OP-6: dev-96 round-robin, test breadth-first to m=8,
round-robin to the cap) and the power procedure are byte-identical reuse of
screen.py's frozen functions. Selection + contrast passes are joined from the
committed screen reports (poc/f1k-askability/reports/, deterministic outputs
of the same pipeline; the redacted-input hash is re-verified below).

Output: reports/power-report-n1573.json — the pre-spend MEASURED power
artifact the F1-K freeze pins (expected per the maintainer approval:
K-1 0.804 / K-2 0.806 / K-3 0.800, all >= 0.80).

$0, no GPU, no network, no model call, gold-label/model-outcome blind
(same governance as screen.py). Deterministic: byte-identical on re-run.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import screen as sc  # frozen machinery: loaders, allocate, power_curve
import numpy as np

N_TEST_APPROVED = 1573      # maintainer-approved raise of the 1440 cap (2026-07-15)
C_APPROVED = 96             # maintainer-approved operating C
EXPECTED = {"K-1": 0.804, "K-2": 0.806, "K-3": 0.800}  # approval memo figures

STAMP = "2026-07-15 designer-32 frozen-geometry power confirmation ($0, blind)"


def main():
    import build_corpora as bc

    # --- rebuild the deterministic Part-1 state (identical pipeline) --------
    wn = bc.parse_wn_dict()
    recs, n_raw, n_dup = sc.load_kernel_records()
    bc.build_triggers(recs, wn)
    pool = []
    for r in recs:
        ok, ast_bytes = sc.ast_parseable(r["explication"])
        if not (r["gloss"] and r["gloss"].strip()) or not ok:
            continue
        if not (r.get("d2_gloss") and r["d2_gloss"].strip()) or not r["triggers"]:
            continue
        r["ast_bytes"] = ast_bytes
        pool.append(r)
    for i, r in enumerate(pool):
        r["index"] = i
    matchers = bc.compile_matchers(pool)
    hdr_cids = set()
    for text in (bc.HEADER, bc.CUE, " ".join(bc.LABEL_ALPHABET)):
        for (_s, _e, cidx) in sc.raw_candidates(text, matchers):
            hdr_cids.add(cidx)
    items = sc.load_items_redacted()

    # re-verify the frozen redacted-input hash (the pre-spend askability pin)
    import kot_common as kc
    redacted_view = [{"item_id": it["item_id"], "source": it["source"],
                      "question": it["question"], "options": it["options"]}
                     for it in sorted(items, key=lambda x: x["item_id"])]
    redacted_hash = sc.sha256_bytes(kc.canonical_bytes(redacted_view))
    want = json.load(open(HERE / "reports" / "hash-report.json",
                          encoding="utf-8"))[
        "redacted_input_hash_frozen_before_screen"]
    if redacted_hash != want:
        sc.fail("redacted-input hash %s != frozen %s" % (redacted_hash, want))
    print("redacted-input hash re-verified: %s" % redacted_hash[:12])

    item_cands = {}
    q_end = {}
    for ii, it in enumerate(items):
        tpl = bc.render_template(it["question"], it["options"])
        q_end[ii] = len(bc.HEADER) + len(it["question"])
        cands = sc.raw_candidates(tpl, matchers)
        if cands:
            item_cands[ii] = cands
    allowed_all = set(range(len(pool)))
    raw_match = [0] * len(pool)
    excl = [0] * len(pool)
    excl_stem = [0] * len(pool)
    for ii, cands in item_cands.items():
        for (_s, _e, cidx) in cands:
            raw_match[cidx] += 1
        spans = sc.resolve(cands, allowed_all)
        if spans:
            win = spans[0][2]
            excl[win] += 1
            if spans[0][0] < q_end[ii]:
                excl_stem[win] += 1
    for r in pool:
        i = r["index"]
        r["raw_match"] = raw_match[i]
        r["excl_total"] = excl[i]
        r["excl_stem"] = excl_stem[i]
        r["collision_fraction"] = (round((raw_match[i] - excl[i]) /
                                         raw_match[i], 6)
                                   if raw_match[i] else 0.0)
        r["projected_m_test"] = excl[i]
        r["header_cue_collision"] = i in hdr_cids
    survivors = [r for r in pool
                 if r["projected_m_test"] >= sc.POWER_GATE_MIN_M
                 and not r["header_cue_collision"]]
    survivors.sort(key=lambda r: (-r["projected_m_test"], -r["excl_stem"],
                                  -r["excl_total"], r["collision_fraction"],
                                  r["synset"].encode("utf-8")))
    for i, r in enumerate(survivors):
        r["rank"] = i + 1
    selected = survivors[:sc.SELECT_N]

    # cross-check the selection against the committed candidate report
    cand = json.load(open(HERE / "reports" / "candidate-report.json",
                          encoding="utf-8"))
    want_sel = [(c["rank"], c["urn"]) for c in cand["selected"]]
    got_sel = [(r["rank"], r["urn"]) for r in selected]
    if want_sel != got_sel:
        sc.fail("re-derived selection differs from the committed "
                "candidate-report.json — pipeline drift, STOP")
    print("selection re-derived identically: 96 concepts, ranks 1..96")

    # contrast passes from the committed certification (all 96 pass)
    dis = json.load(open(HERE / "reports" / "distinctness-report.json",
                         encoding="utf-8"))
    passed_urns = {c["urn"] for c in dis["concepts"]
                   if c["in_selected"] and c["contrast_pass"]}
    pass_selected = [r for r in selected if r["urn"] in passed_urns]
    if len(pass_selected) != C_APPROVED:
        sc.fail("contrast-passing selected = %d != approved C = %d"
                % (len(pass_selected), C_APPROVED))

    # --- allocation at the APPROVED cap n=1573 ------------------------------
    sc.N_TEST = N_TEST_APPROVED           # the ONLY departure from the screen
    prefix = [r["index"] for r in pass_selected]
    test, dev, ntest, ndev = sc.allocate(prefix, item_cands, items, q_end)
    m_list = [test[c] for c in prefix]
    m_min, m_max = min(m_list), max(m_list)
    m_mean = sum(m_list) / len(m_list)
    print("allocation at C=%d, n=%d: realized n_test=%d n_dev=%d "
          "m_min=%d m_mean=%.4f m_max=%d"
          % (C_APPROVED, N_TEST_APPROVED, ntest, ndev, m_min, m_mean, m_max))
    if ntest != N_TEST_APPROVED:
        sc.fail("allocation could not fill n=%d (got %d) — supply short"
                % (N_TEST_APPROVED, ntest))
    if m_min < sc.POWER_GATE_MIN_M:
        sc.fail("m_min=%d < 8 — power gate unsatisfied" % m_min)

    # --- the §R-REV5 exact-power sim at the frozen geometry -----------------
    mu_grid = sorted(set([round(x, 5)
                          for x in np.arange(0.030, 0.05201, 0.002)]
                         + [sc.MU_STAR]))
    out_contrasts = {}
    all3 = True
    for name, R in sc.CONTRASTS:
        curve = sc.power_curve(m_list, name, mu_grid)
        p_star = curve[sc.MU_STAR]
        mc_se = round((p_star * (1 - p_star) / sc.N_SIM) ** 0.5, 5)
        mde = sc.mde_from_curve(mu_grid, curve)
        ok = p_star >= sc.POWER_MIN
        all3 = all3 and ok
        out_contrasts[name] = {
            "R": R, "power_at_mu_star": round(p_star, 4), "mc_se": mc_se,
            "mde_80pct_power": round(mde, 5) if mde is not None else None,
            "power_ge_0.80": ok,
            "approval_memo_figure": EXPECTED[name],
        }
        print("  %s (R=%d): power at mu*=+4.09 pts -> %.4f (MC-SE %.5f, "
              "MDE %.5f)  %s" % (name, R, p_star, mc_se, mde or -1,
                                 "PASS" if ok else "FAIL"))

    report = {
        "part": "frozen-geometry exact-power confirmation",
        "built": STAMP,
        "procedure": "IDENTICAL to screen.py Part 3 ([DES] SSR-REV5 exact "
                      "cluster sign-flip joint-power sim; fire iff perm "
                      "p<0.05 AND observed lift >= +3 pts); the ONLY change "
                      "is N_TEST 1440 -> 1573 (maintainer-approved raise, "
                      "2026-07-15)",
        "geometry": {"C": C_APPROVED, "n_test": N_TEST_APPROVED,
                     "n_dev": ndev, "m_min": m_min,
                     "m_mean": round(m_mean, 4), "m_max": m_max,
                     "every_m_ge_8": m_min >= sc.POWER_GATE_MIN_M,
                     "m_list_by_rank": m_list},
        "params": {"seed": sc.POWER_SEED, "n_sim": sc.N_SIM,
                   "b_flip": sc.B_FLIP, "delta": sc.DELTA,
                   "rho_u": sc.RHO_U, "mu_star": sc.MU_STAR,
                   "t_fire_pts": 3.0, "power_min": sc.POWER_MIN,
                   "R_per_contrast": {c: r for c, r in sc.CONTRASTS}},
        "redacted_input_hash_reverified": redacted_hash,
        "contrasts": out_contrasts,
        "all_three_power_ge_0.80": all3,
        "MEASURED": "Monte-Carlo joint power; MC-SE = sqrt(p(1-p)/N_sim); "
                    "selection + allocation exact over the pinned corpora",
        "STIPULATED": "geometry (C=96, n=1573, mu*=+4.09 pts, R=(1,3,1)) is "
                      "the maintainer-approved powered geometry (2026-07-15); "
                      "delta=0.10 shared across rungs (conservative for K-2, "
                      "see screen.py power-report note)",
    }
    sc.write_json(HERE / "reports" / "power-report-n1573.json", report)
    print("\nALL THREE >= 0.80: %s   -> reports/power-report-n1573.json"
          % all3)
    sys.exit(0 if all3 else 3)


if __name__ == "__main__":
    main()
