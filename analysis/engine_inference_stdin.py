#!/usr/bin/env python3
# ENGINE-INF pre-registered analysis (stdin-conformant; verdict-gen P2 §3.1
# step 5 invokes this with the eligible results-log run records as JSONL on
# STDIN and no argv). REVISION-1/2/3 build.
#
# Design: docs/next/design/engine-inference-under-typing.md §2.2-§2.3 as
# amended through REVISION-3 (exact finite-census gates, co-primary EP-A/
# EP-B, C-SHUF orbit randomization over the orbit-invariant A_union frame);
# operationalisations:
#   ASM-1994  divergence signature (verdict + refusal + G2-side projection)
#   ASM-1997/2116  G4 scoring rule (REFUSE or truly-vacuous CONSISTENT
#             correct; a confident derived assertion is incorrect) — G4
#             cells feed the honesty secondary only, never the co-primary
#             frames
#   ASM-2101/2102  co-primary endpoints: EP-A = K vs K-lemma-{dom,union} on
#             Div_dec ∩ (G1∪G3)_H* (sense-splitting per se); EP-B = K vs
#             B-wn on Div_dec ∩ (G1∪G3)_H* (kernel-authored content given
#             splitting); D-word arms descriptive only
#   ASM-2105  KILL-e1 (holdout adequacy) / KILL-e2a (sense-split idle) /
#             KILL-e2b (kernel-vs-mechanical unaskable)
#   ASM-2106  the outcome-equivalence CELL is the inference unit
#   ASM-2115  EXACT census gates over the fixed cell frame (all bootstrap/
#             LB95 gates REMOVED): delta >= +0.20, strict win>loss sign,
#             K correctness floor >= 0.80, binding DIST-SPAN (net winning
#             cells span >= 2 lemmas), no-net-harm tolerance 0.02
#   ASM-2114/2120  C-SHUF: the 960-member within-lemma permutation orbit;
#             evaluation frame = the orbit-INVARIANT union A_union of
#             per-member activated cells (non-empty derived_sides OR
#             ANOMALOUS); T(pi) = correctness over A_union (constant
#             denominator); calibrated one-sided p = #{T(pi)>=T(K)}/960;
#             PASS gate p <= 0.05
#
# INPUT CONTRACT: each eligible stdin record's `artifacts` must pin the
# runner outputs: rows_path/rows_sha256 AND orbit_rows_path/
# orbit_rows_sha256. Rows are loaded from the PINNED paths, sha256
# re-verified, fail closed. The analysis is a pure function of those bytes:
# cells, divergence, exact censuses, C-SHUF and bands are RECOMPUTED here —
# committed certificate artifacts are provenance, not inputs.
#
# FRAME SEMANTICS: rows carry frame ("H" = registered holdout run, "seen" =
# exploratory) and h_star. The BINDING frame is (G1∪G3)_H* — G1∪G3 cells
# whose h_star is true. On a seen-frame input every h_star is false; the
# analysis then evaluates the identical machinery over the seen G1∪G3
# cells and stamps exploratory_nonbinding=true (the seen frames are
# exploratory-forever, ASM-2104 — such output is mechanics validation and
# never a registered verdict).

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Pre-registered constants (design §2.3 [R2] verbatim; changing any is a
# design change requiring a new freeze).
PASS_MIN_DELTA = 0.20
PASS_K_FLOOR = 0.80
NO_NET_HARM_TOL = 0.02
CSHUF_P_MAX = 0.05
DIST_SPAN_MIN_LEMMAS = 2
KILL_E1_MIN_ITEMS = 30
KILL_E1_MIN_CELLS = 12
KILL_E1_MIN_OPS = 2
KILL_E1_MIN_LEMMAS = 2
KILL_E2A_MIN_CELLS = 6
KILL_E2B_MIN_CELLS = 6
KILL_E2B_MIN_ITEMS = 10
ORBIT_N = 960

ARMS = ("K", "K-lemma-dom", "K-lemma-union", "D-word-dom", "D-word-union",
        "B-wn")
EP_A_ARMS = ("K-lemma-dom", "K-lemma-union")
EP_B_ARM = "B-wn"


def fail(msg):
    print("ERR_P2_ANALYSIS: %s" % msg, file=sys.stderr)
    sys.exit(1)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pinned():
    """Eligible stdin run records -> verified rows + orbit rows."""
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
    pins = set()
    for rec in eligible:
        art = rec.get("artifacts") or {}
        for k in ("rows_path", "rows_sha256", "orbit_rows_path",
                  "orbit_rows_sha256"):
            if not art.get(k):
                fail("eligible record lacks artifacts.%s" % k)
        pins.add((art["rows_path"], art["rows_sha256"],
                  art["orbit_rows_path"], art["orbit_rows_sha256"]))
    if len(pins) != 1:
        fail("eligible records pin DIFFERENT artifacts: %s" % sorted(pins))
    rows_path, rows_sha, orows_path, orows_sha = next(iter(pins))
    out = []
    for path, want in ((rows_path, rows_sha), (orows_path, orows_sha)):
        full = ROOT / path
        if not full.is_file():
            fail("pinned artifact missing: %s" % path)
        got = sha256_file(full)
        if got != want:
            fail("artifact %s sha256 %s != pinned %s" % (path, got, want))
        out.append([json.loads(l) for l in open(full)])
    rows_list, orbit_list = out
    rows = {}
    for r in rows_list:
        rows[(r["arm"], r["item"])] = r
    return rows, orbit_list


def main():
    rows, orbit_list = load_pinned()
    item_ids = sorted({i for (a, i) in rows if a == "K"})
    for arm in ARMS + ("oracle",):
        missing = [i for i in item_ids if (arm, i) not in rows]
        if missing:
            fail("arm %s missing %d item rows" % (arm, len(missing)))

    frames = {rows[("K", i)].get("frame", "seen") for i in item_ids}
    if len(frames) != 1:
        fail("mixed row frames: %s" % sorted(frames))
    frame = next(iter(frames))
    binding = frame == "H"

    def dec(arm, iid):
        r = rows[(arm, iid)]
        return (r["verdict"], r["refusal"] or "")

    def correct(arm, iid):
        return bool(rows[(arm, iid)]["correct"])

    def is_g1g3(iid):
        return rows[("K", iid)]["gold_rule"] in ("G1+G2", "G3")

    def in_frame(iid):
        if not is_g1g3(iid):
            return False
        return rows[("K", iid)].get("h_star", False) if binding else True

    # ---- cells (ASM-2106): one observation per outcome-equivalence cell;
    # within-cell determinism asserted, fail closed ----
    cells = {}
    for iid in item_ids:
        if not in_frame(iid):
            continue
        ck = rows[("K", iid)].get("cell")
        if not ck:
            fail("row lacks the cell key (item %s)" % iid)
        cells.setdefault(ck, []).append(iid)
    for ck, iids in sorted(cells.items()):
        for arm in ARMS:
            sigs = {(rows[(arm, i)]["verdict"], rows[(arm, i)]["refusal"] or "",
                     tuple(rows[(arm, i)]["derived_sides"]),
                     correct(arm, i)) for i in iids}
            if len(sigs) != 1:
                fail("cell %s not outcome-equivalent in arm %s" % (ck, arm))

    def cell_dec(arm, ck):
        return dec(arm, cells[ck][0])

    def cell_correct(arm, ck):
        return correct(arm, cells[ck][0])

    def cell_lemma(ck):
        return rows[("K", cells[ck][0])]["lemma"]

    def cell_kind(ck):
        return rows[("K", cells[ck][0])]["kind"]

    frame_cells = sorted(cells)
    n_frame_items = sum(len(cells[c]) for c in frame_cells)

    # ---- KILL-e1 (holdout adequacy; ASM-2105 — the pre-freeze count,
    # re-verified here from the pinned rows) ----
    ops = sorted({"O1" if cell_kind(c) == "attested" else "O2"
                  for c in frame_cells})
    lemmas = sorted({cell_lemma(c) for c in frame_cells})
    kill_e1 = (n_frame_items < KILL_E1_MIN_ITEMS
               or len(frame_cells) < KILL_E1_MIN_CELLS
               or len(ops) < KILL_E1_MIN_OPS
               or len(lemmas) < KILL_E1_MIN_LEMMAS)

    # ---- co-primary frames (ASM-2102): decision-level divergence cells ----
    div_cells = {b: [c for c in frame_cells
                     if cell_dec("K", c) != cell_dec(b, c)]
                 for b in ARMS if b != "K"}
    f_a = {x: div_cells[x] for x in EP_A_ARMS}
    f_a_union = sorted(set(f_a["K-lemma-dom"]) | set(f_a["K-lemma-union"]))
    f_b = div_cells[EP_B_ARM]

    kill_e2a = len(f_a_union) < KILL_E2A_MIN_CELLS
    kill_e2b = (len(f_b) < KILL_E2B_MIN_CELLS
                or sum(len(cells[c]) for c in f_b) < KILL_E2B_MIN_ITEMS)

    # ---- exact census per endpoint (ASM-2115) ----
    def census(b, frame_c):
        wins = [c for c in frame_c if cell_correct("K", c)
                and not cell_correct(b, c)]
        losses = [c for c in frame_c if not cell_correct("K", c)
                  and cell_correct(b, c)]
        ties = len(frame_c) - len(wins) - len(losses)
        delta = ((sum(cell_correct("K", c) for c in frame_c)
                  - sum(cell_correct(b, c) for c in frame_c)) / len(frame_c)
                 if frame_c else 0.0)
        # DIST-SPAN (binding, ASM-2115): net winning cells (win-cells minus
        # same-lemma loss-cells) must span >= 2 distinct lemmas
        net = {}
        for c in wins:
            net[cell_lemma(c)] = net.get(cell_lemma(c), 0) + 1
        for c in losses:
            net[cell_lemma(c)] = net.get(cell_lemma(c), 0) - 1
        span = sorted(l for l, v in net.items() if v > 0)
        return {"n_cells": len(frame_c), "n_items": sum(len(cells[c])
                                                        for c in frame_c),
                "delta": delta, "wins": len(wins), "losses": len(losses),
                "ties": ties, "net_win_lemma_span": span,
                "dist_span_ok": len(span) >= DIST_SPAN_MIN_LEMMAS}

    ep_a = {x: census(x, f_a[x]) for x in EP_A_ARMS}
    ep_b = census(EP_B_ARM, f_b)
    k_corr_a = (sum(cell_correct("K", c) for c in f_a_union) / len(f_a_union)
                if f_a_union else None)
    k_corr_b = (sum(cell_correct("K", c) for c in f_b) / len(f_b)
                if f_b else None)

    pass_a = (not kill_e2a and all(
        ep_a[x]["delta"] >= PASS_MIN_DELTA
        and ep_a[x]["wins"] > ep_a[x]["losses"]
        and ep_a[x]["dist_span_ok"] for x in EP_A_ARMS)
        and k_corr_a is not None and k_corr_a >= PASS_K_FLOOR)
    pass_b = (not kill_e2b and ep_b["delta"] >= PASS_MIN_DELTA
              and ep_b["wins"] > ep_b["losses"] and ep_b["dist_span_ok"]
              and k_corr_b is not None and k_corr_b >= PASS_K_FLOOR)
    fail_a = (not kill_e2a and min(ep_a[x]["delta"] for x in EP_A_ARMS) <= 0)
    fail_b = (not kill_e2b and ep_b["delta"] <= 0)

    # ---- no-net-harm (binding for PASS-affirm; ASM-2115) ----
    harm = {}
    harm_ok = True
    for b in ARMS:
        if b == "K":
            continue
        conv = [c for c in frame_cells if c not in set(div_cells[b])]
        if not conv:
            harm[b] = None
            continue
        kc = sum(cell_correct("K", c) for c in conv) / len(conv)
        bc = sum(cell_correct(b, c) for c in conv) / len(conv)
        harm[b] = kc - bc
        if kc < bc - NO_NET_HARM_TOL:
            harm_ok = False

    # ---- C-SHUF (ASM-2114 mechanics + ASM-2120 A_union frame) ----
    orbit = {}
    for r in orbit_list:
        orbit.setdefault(r["m"], {})[r["cell"]] = r
    members = sorted(orbit)
    if len(members) != ORBIT_N:
        fail("orbit has %d members, expected %d" % (len(members), ORBIT_N))
    cand = set(frame_cells)
    for m in members:
        if set(orbit[m]) - cand or cand - set(orbit[m]):
            # orbit rows must cover exactly the frame cells
            fail("orbit member %d cell set differs from the frame" % m)
    # identity member must reproduce the K arm on the frame (consistency)
    for c in frame_cells:
        r0, rk = orbit[0][c], rows[("K", cells[c][0])]
        if (r0["verdict"], tuple(r0["derived_sides"])) != \
                (rk["verdict"], tuple(rk["derived_sides"])):
            fail("orbit identity member != K arm on cell %s" % c)
    a_union = sorted({c for m in members for c, r in orbit[m].items()
                      if r["derived_sides"] or r["verdict"] == "ANOMALOUS"})
    if a_union:
        gold_of = {c: rows[("K", cells[c][0])]["gold_verdict"]
                   for c in a_union}
        t = {m: sum(1 for c in a_union
                    if orbit[m][c]["verdict"] == gold_of[c]) / len(a_union)
             for m in members}
        t_k = t[0]
        cshuf_p = sum(1 for m in members if t[m] >= t_k) / len(members)
        cshuf_rank = sum(1 for m in members if t[m] > t_k) + 1
        cshuf_ok = cshuf_p <= CSHUF_P_MAX
    else:
        t_k, cshuf_p, cshuf_rank, cshuf_ok = None, None, None, False

    # ---- bands (§2.3 [R2] decision rule; §3 ladder) ----
    band_pass_affirm = (not kill_e1 and pass_a and pass_b and cshuf_ok
                        and harm_ok)
    content_inert = (a_union != [] and not cshuf_ok)

    # ---- gates + descriptive secondaries ----
    oracle_score = (sum(1 for i in item_ids if correct("oracle", i))
                    / len(item_ids) if item_ids else 0.0)
    census_all, honesty = {}, {}
    for arm in ARMS:
        census_all[arm] = sum(1 for i in item_ids if correct(arm, i)) / len(item_ids)
        honesty[arm] = round(sum(rows[(arm, i)]["honesty_penalty"]
                                 for i in item_ids), 2)
    dword_desc = {b: census(b, div_cells[b])
                  for b in ("D-word-dom", "D-word-union")}

    out = {
        "gates": {
            "oracle_score": oracle_score,
            "oracle_valid": oracle_score == 1.0,
            "rows_complete": True,
            "cells_outcome_equivalent": True,
            "orbit_identity_matches_k": True,
            "instrument_valid": oracle_score == 1.0,
        },
        "analysis": {
            "frame": frame,
            "binding": binding,
            "exploratory_nonbinding": not binding,
            "n_items": len(item_ids),
            "n_frame_items": n_frame_items,
            "n_cells_confirmatory": len(frame_cells),
            "frame_ops_spanned": ops,
            "frame_lemmas_spanned": lemmas,
            "kill_e1_fired": kill_e1,
            "kill_e2a_fired": kill_e2a,
            "kill_e2b_fired": kill_e2b,
            "ep_a_delta_dom": ep_a["K-lemma-dom"]["delta"],
            "ep_a_delta_union": ep_a["K-lemma-union"]["delta"],
            "ep_a_dom": ep_a["K-lemma-dom"],
            "ep_a_union": ep_a["K-lemma-union"],
            "ep_b_delta": ep_b["delta"],
            "ep_b": ep_b,
            "k_corr_ep_a_frame": k_corr_a,
            "k_corr_ep_b_frame": k_corr_b,
            "pass_a": pass_a,
            "pass_b": pass_b,
            "fail_a": fail_a,
            "fail_b": fail_b,
            "cshuf_orbit_p": cshuf_p,
            "cshuf_rank": cshuf_rank,
            "cshuf_active_n": len(a_union),
            "cshuf_t_identity": t_k,
            "cshuf_pass": cshuf_ok,
            "content_inert_flag": content_inert,
            "no_net_harm_ok": harm_ok,
            "no_net_harm_margins": harm,
            "band_pass_affirm": band_pass_affirm,
            "band_fail_deflate": fail_a or fail_b,
            "census_correctness": census_all,
            "honesty_penalty_sum": honesty,
            "dword_descriptive": dword_desc,
        },
    }
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
