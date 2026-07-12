#!/usr/bin/env python3
"""rules-1-c pre-registered analysis — STDIN-CONFORMANT successor of
analysis/rules_1c.py (identical statistics, verdict-gen-compatible input).

WHY THIS FILE EXISTS (interface-defect fix, NOT a design change): the
original pinned script analysis/rules_1c.py (sha bf4e6476aa72a060100df468
1341d78f3f2ea598e7e640a1131153e4f004627c) took argparse-REQUIRED flags
(--run-records/--certificate), while tools/registry/verdict-gen.py step 5
invokes the pinned analysis with the ELIGIBLE results-log run records as
JSONL on STDIN and NO argv — so the automated verdict path could never
execute the pin (argparse exits 2 => ERR_P2_ANALYSIS). This successor is
swapped in by a lawful pre-final reset-refreeze (docs/next/
opus-execution-practices.md 'Scope note'; registry/corrections/rules-1-c/
2-prefreeze-correction.json): rules-1-c has NO final-phase run in its
results-log at correction time and is NOT GNG-0-signed. Every statistic,
constant, gate expression and the output serialization below is carried
BYTE-IDENTICAL from rules_1c.py; only input acquisition changed. Parity
was proven by running both scripts over the same 13,470 merged campaign
rows and diffing stdout bytes (see the correction record).

INPUT CONTRACT (verdict-gen P2 §3.1 step 5): eligible run records as JSONL
on stdin — event=="run", phase=="final", exit=="ok", chain-verified,
prereg-hash-matched by verdict-gen. Each eligible record's `artifacts`
must pin the campaign per-item row file (ROWS_PATH/ROWS_SHA256 below);
this script loads the per-item rows from that PINNED path (sha256
re-verified, fail closed) and consumes ONLY rows whose (arm, rung, seed)
cell is witnessed by an eligible stdin record — the analysis stays a pure
function of the eligible set. The certificate precondition is read from
its PINNED path (the frozen record's pins.artifact_hashes carrier),
sha256 re-verified. Any mismatch/absence fails closed (exit 1 => verdict-
gen ERR_P2_ANALYSIS); nothing falls back.

Everything below this docstring other than main()'s input acquisition is
verbatim from analysis/rules_1c.py — see that file's docstring for the
design record (host-validity gate rationale, s3 conditioning, floors).

Statistics: paired item BCa bootstrap B=10000, PRNG seed 20260711, one-sided
alpha=0.05; Holm over the secondary family {s1, s2, s3, s4}; Wilson 95%
bounds for rate gates. Entailed-cell rows only for every endpoint; stated
cells are sanity descriptives; control cells feed refusal correctness.
"""

import hashlib
import json
import math
import random
import sys

# Pinned inputs (pinned transitively via THIS script's sha256 in
# pins.analysis_script — a byte change here is an encoder-of-record change
# and requires a new freeze). The certificate sha equals the frozen record's
# pins.artifact_hashes["certificate-result(...)"] carrier e0071e9e...; the
# rows sha equals merged/merge-manifest-rules1b.json merged_records_sha256.
ROWS_PATH = ("poc/rules-1/results-incoming/20260712-142704-rules1b-parallel/"
             "merged/run-records-rules1b.jsonl")
ROWS_SHA256 = "c1f5bea8241bed557e74535af3726c8384462bc69e8e8952918725f976f463be"
CERT_PATH = "poc/rules-1/results/certificate-result.json"
CERT_SHA256 = "e0071e9e4952f915c461206d514afa555d683bc22985fad2273821f37176d379"

OUTPUT_FIELDS = [
    "/gates/certificate_precondition_valid",
    "/gates/twin_agreement_valid",
    "/gates/headroom_valid",
    "/gates/separation_valid",
    "/gates/engagement_valid",
    "/gates/host_validity_valid",
    "/gates/repeat_byte_identical",
    "/analysis/primary_lift_lb95",
    "/analysis/primary_pass",
    "/analysis/kill_b_fired",
    "/analysis/a2_minus_a1_lb95_systems",
    "/analysis/s1_shuffled_recovery_ub95",
    "/analysis/s1_pass",
    "/analysis/s2_a3_minus_a1_lb95",
    "/analysis/s2_pass",
    "/analysis/s3_efficiency_diff_lb95",
    "/analysis/s3_pass",
    "/analysis/s4_a7_minus_c6_lb95",
    "/analysis/s4_pass",
    "/analysis/holm_order",
    "/analysis/acc_a1", "/analysis/acc_a2", "/analysis/acc_a3",
    "/analysis/acc_a4", "/analysis/acc_a5_r3", "/analysis/acc_a7",
    "/analysis/acc_c1_shuffled", "/analysis/acc_c6_axioms_text",
    "/analysis/refusal_correctness_e5",
    "/analysis/proof_depth_strata",
    "/analysis/engine_us_per_query",
    "/analysis/default_world_cost_ledger",
    "/analysis/accuracy", "/analysis/params", "/analysis/memory",
    "/analysis/inference_compute", "/analysis/training_compute",
]

B = 10000
SEED = 20260711
ALPHA = 0.05


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def wilson_lb(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0
    ph = k / n
    return ((ph + z * z / (2 * n)) - z * math.sqrt(
        ph * (1 - ph) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def paired_diffs(rows, arm_a, arm_b, key="item_correct_ext"):
    """Per-item seed-mean difference arm_a - arm_b on entailed cells."""
    acc = {}
    for r in rows:
        if r["cell"] != "entailed" or r["arm"] not in (arm_a, arm_b):
            continue
        acc.setdefault(r["item_id"], {}).setdefault(r["arm"], []).append(
            r[key])
    diffs = []
    for item, byarm in sorted(acc.items()):
        if arm_a in byarm and arm_b in byarm:
            diffs.append(sum(byarm[arm_a]) / len(byarm[arm_a]) -
                         sum(byarm[arm_b]) / len(byarm[arm_b]))
    return diffs


def bca_lb(diffs, one_sided_alpha=ALPHA, b=B, seed=SEED):
    """One-sided BCa lower bound for the mean of paired diffs."""
    n = len(diffs)
    if n == 0:
        return None
    rng = random.Random(seed)
    theta = sum(diffs) / n
    boots = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(b))
    prop = sum(1 for x in boots if x < theta) / b
    z0 = _norm_ppf(min(max(prop, 1e-9), 1 - 1e-9))
    jack = [(sum(diffs) - d) / (n - 1) for d in diffs] if n > 1 else [theta]
    jm = sum(jack) / len(jack)
    num = sum((jm - j) ** 3 for j in jack)
    den = 6 * (sum((jm - j) ** 2 for j in jack) ** 1.5) or 1e-12
    a = num / den
    zq = _norm_ppf(one_sided_alpha)
    adj = _norm_cdf(z0 + (z0 + zq) / (1 - a * (z0 + zq)))
    idx = min(max(int(adj * b), 0), b - 1)
    return boots[idx]


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _norm_ppf(p, lo=-10.0, hi=10.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        if _norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def acc(rows, arm, cell="entailed"):
    xs = [r["item_correct_ext"] for r in rows
          if r["arm"] == arm and r["cell"] == cell]
    return sum(xs) / len(xs) if xs else None


def read_pinned(path, want_sha, what):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as e:
        fail("ERR_RULES1C_PIN_IO", "%s: cannot read pinned %s: %s"
             % (what, path, e))
    got = hashlib.sha256(raw).hexdigest()
    if got != want_sha:
        fail("ERR_RULES1C_PIN_DRIFT", "%s: %s sha256 %s != pinned %s"
             % (what, path, got, want_sha))
    return raw


def main():
    # ---- input acquisition (the ONLY departure from rules_1c.py) ----
    stdin_raw = sys.stdin.buffer.read().decode("utf-8")
    try:
        records = [json.loads(x) for x in stdin_raw.splitlines() if x.strip()]
    except json.JSONDecodeError as e:
        fail("ERR_RULES1C_STDIN", "stdin is not JSONL: %s" % e)
    # Defensive re-filter of verdict-gen's own eligibility (P2 §3.1 step 3);
    # reuse-provenance rows (D9) are refused — rules-1-c declares no
    # reused_from block, so any such row is a contract violation.
    eligible = [r for r in records
                if r.get("event") == "run" and r.get("phase") == "final"
                and r.get("exit") == "ok"]
    if not eligible:
        fail("ERR_RULES1C_NO_ELIGIBLE",
             "no eligible run records on stdin (verdict-gen pipes eligible "
             "rows; the completeness gate should have fired upstream)")
    if any(r.get("reuse_provenance") for r in records):
        fail("ERR_RULES1C_REUSE",
             "reused producer rows on stdin but rules-1-c freezes no "
             "reused_from block — refusing (fail closed)")
    cells = set()
    for r in eligible:
        arts = r.get("artifacts") or []
        if not any(a.get("path") == ROWS_PATH and a.get("sha256") == ROWS_SHA256
                   for a in arts):
            fail("ERR_RULES1C_ARTIFACT",
                 "eligible run record seq=%r does not pin the campaign row "
                 "artifact %s@%s…" % (r.get("seq"), ROWS_PATH, ROWS_SHA256[:12]))
        cfg = r.get("config") or {}
        missing = [k for k in ("arm", "rung", "seed") if k not in cfg]
        if missing:
            fail("ERR_RULES1C_CONFIG",
                 "eligible run record seq=%r config missing %s"
                 % (r.get("seq"), ", ".join(missing)))
        cells.add((cfg["arm"], cfg["rung"], cfg["seed"]))

    rows_raw = read_pinned(ROWS_PATH, ROWS_SHA256, "campaign rows")
    rows_all = [json.loads(x) for x in rows_raw.decode("utf-8").splitlines()
                if x.strip()]
    # Only rows whose (arm, rung, seed) cell is witnessed by an eligible
    # stdin record enter the analysis — excluded log rows drop their cells.
    rows = [r for r in rows_all if (r["arm"], r["rung"], r["seed"]) in cells]
    if not rows:
        fail("ERR_RULES1C_NO_ROWS",
             "no pinned campaign rows match the eligible cells %s"
             % sorted(cells))
    cert = json.loads(read_pinned(CERT_PATH, CERT_SHA256,
                                  "certificate precondition"))
    # ---- everything below is verbatim from analysis/rules_1c.py ----
    # (repeat_byte_identical: the pinned CLI reported False whenever no
    # repeat-sha pair was supplied; the campaign registered no repeat pair,
    # so the carried value is the constant False — same fail-closed reading.)

    gates = {
        # pinned CPU precondition (PROPOSED-ASM-1131 + 1163): the frozen
        # certificate bytes must carry SUCCESS + gates + no KILL-a.
        "certificate_precondition_valid": bool(
            cert["certificate_result"]["success_asm_1131"] and
            cert["certificate_result"]["gates_asm_1163_all_pass"] and
            not cert["certificate_result"]["kill_a_fired"]),
        # differential twin exact agreement carried with the certificate
        "twin_agreement_valid": "EXACTLY agreed" in
            cert["engine_identity"]["ran"],
        "headroom_valid": (acc(rows, "A1") is not None and
                           acc(rows, "A1") <= 0.85),
        "separation_valid": (acc(rows, "A5") is not None and
                             acc(rows, "A1") is not None and
                             acc(rows, "A5") - acc(rows, "A1") >= 0.05),
        # A3 verifier decidably engaged: >=1 rejection-resample observed and
        # rejection rate not degenerate (RT-7a shape)
        "engagement_valid": any(r["arm"] == "A3" and r.get("attempts", 1) > 1
                                for r in rows),
        # HOST-VALIDITY INSTRUMENT GATE (rules-1-c, entity-form floors): a
        # degenerate host scorer can NEVER read as a substantive verdict.
        # Floors: A7 >= 0.85 (render-only bare derived fact; pinned-R1 pilot
        # 24/24) AND A5 >= 0.75 (nsk1 R3 entity-form datum 0.7912; pinned-R3
        # pilot 24/24) — both far above the 2-option chance floor 0.5
        # (n=2574 one-sided 95% binomial UB ~0.516). Wired into
        # verdict_rules rule 0: failure => INSTRUMENT-INVALID before FAIL.
        "host_validity_valid": (acc(rows, "A7") is not None and
                                acc(rows, "A5") is not None and
                                acc(rows, "A7") >= 0.85 and
                                acc(rows, "A5") >= 0.75),
        "repeat_byte_identical": False,
    }

    primary = bca_lb(paired_diffs(rows, "A3", "A1"))
    s2 = primary  # s2 is the Holm-corrected confirmation of the same contrast
    s1_rec = None
    d_c1 = paired_diffs(rows, "c1", "A1")
    d_a3 = paired_diffs(rows, "A3", "A1")
    if d_c1 and d_a3 and sum(d_a3):
        # recovery = shuffled lift / real lift; UB95 via BCa on the ratio's
        # components (conservative: UB of c1 lift over LB of A3 lift)
        ub_c1 = -bca_lb([-d for d in d_c1])
        lb_a3 = bca_lb(d_a3)
        s1_rec = (ub_c1 / lb_a3) if lb_a3 and lb_a3 > 0 else None
    # s3 CONDITIONED on the separation gate (frozen endpoint text; fixes the
    # rules_1.py unconditional-compute defect disclosed at the rules-1 grade):
    # separation false => s3 unevaluable (null), never a pass, never a fail.
    s3 = (bca_lb(paired_diffs(rows, "A3", "A5"))  # NI margin 0, sign-only
          if gates["separation_valid"] else None)
    s4 = bca_lb(paired_diffs(rows, "A7", "c6"))
    a2 = bca_lb(paired_diffs(rows, "A2", "A1"))

    out = {"gates": gates, "analysis": {
        "primary_lift_lb95": primary,
        "primary_pass": primary is not None and primary > 0,
        "kill_b_fired": primary is not None and primary <= 0,
        "a2_minus_a1_lb95_systems": a2,
        "s1_shuffled_recovery_ub95": s1_rec,
        "s1_pass": s1_rec is not None and s1_rec < 0.30,
        "s2_a3_minus_a1_lb95": s2,
        "s2_pass": s2 is not None and s2 > 0,
        "s3_efficiency_diff_lb95": s3,
        "s3_pass": s3 is not None and s3 >= 0,
        "s4_a7_minus_c6_lb95": s4,
        "s4_pass": s4 is not None and s4 > 0,
        "holm_order": ["s1", "s2", "s3", "s4"],
        "acc_a1": acc(rows, "A1"), "acc_a2": acc(rows, "A2"),
        "acc_a3": acc(rows, "A3"), "acc_a4": acc(rows, "A4"),
        "acc_a5_r3": acc(rows, "A5"), "acc_a7": acc(rows, "A7"),
        "acc_c1_shuffled": acc(rows, "c1"),
        "acc_c6_axioms_text": acc(rows, "c6"),
        "refusal_correctness_e5": (lambda xs: sum(xs) / len(xs)
                                   if xs else None)(
            [r["refused"] for r in rows if r["cell"] == "control"
             and r["arm"] in ("A3", "A7")]),
        "proof_depth_strata": "per PROPOSED-ASM-1160: reported by depth<=4",
        "engine_us_per_query": (lambda xs: sum(xs) / len(xs)
                                if xs else None)(
            [r["engine_us"] for r in rows if "engine_us" in r]),
        "default_world_cost_ledger": {
            "note": "A4 one-off materialisation vs per-prompt delta closure "
                    "(PROPOSED-ASM-1139: cost ledger only, no non-inertness "
                    "claim)"},
        "accuracy": acc(rows, "A3"),
        "params": 135_000_000,
        "memory": None,
        "inference_compute": (lambda xs: sum(xs) if xs else None)(
            [r.get("flops_formula", 0) for r in rows]),
        "training_compute": 0,
    }}
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
