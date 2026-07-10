#!/usr/bin/env python3
"""l3a-parse pinned analysis — NL-boundary leg, family/world vertical
(HL3a clause 2; DRAFT record registry/experiments/l3a-parse.json).

Eligible run records on stdin (one JSON per line, kot-log/1 bodies from
tools/experiments/nlb/nlb_instrument.py); analysis-output JSON on stdout.
Derived statistics live HERE and nowhere else (P2 G-4). Self-contained by
design: no shared helper import, so the pinned sha is the complete analysis
artifact (structural twin of analysis/a5_nl.py with per-record constants and
the FK-NLB-10 in-scope split).

SHAPE-RECOVERABLE RE-SCOPE (FK-NLB-10, ASM-0420; design doc 14.2/14.6/14.7):
the recoverability audit measured that unmarked English cannot faithfully
render the unique-maker / made-lookup shapes (0.7167 strict recovery; 8/8
genuine shape misses land in exactly those two families). The gated
primary and S2 numerators are therefore scored over the 7 shape-recoverable
IN-SCOPE families only (n_scored = 527), as per-family BUCKET SUMS over the
score_nl by_family enrichment (ASM-0480). The run still EXECUTES all 600
covered phrasings; the 2 dropped families (unique-maker 43, made-lookup 30)
are reported DESCRIPTIVELY in /analysis/shape_ambiguous_stratum, never
gated, carved out of the envelope. Full-run descriptives (parse_ok_rate over
870, label strata, stage breakdown, dev, probe, cost) stay full-run.

SKEPTIC ROUND-2 + ROUND-2-RE-AUDIT HARDENING (design doc 14.8 + 14.9,
ASM-0621/ASM-0624; all fail-closed):
  G0 one-row-per-arm: duplicate/retry rows for the same arm are NEVER
     resolved by log order. A retry row carries the kot-log/1 run-row
     channel `supersedes: [<row sha256>]` — the sha256 of the REPLACED log
     line's exact bytes incl. newline (identical to prev_sha256 /
     reuse.row_hashes identity; producible with sha256 over the line), the
     same channel log-append validates at append time (14.9 item A). Here
     the semantics are independently re-verified: the field must be a
     non-empty list of DISTINCT 64-hex row hashes; every target must be
     present among the scored records, belong to the SAME arm, and not be
     the row itself; every record needs a string config.arm (no top-level
     fallback); >1 surviving row per arm, a dangling/self target, a
     malformed field (dict/string/etc.), a cross-arm supersede, byte-
     duplicate rows, or an arm whose every row is superseded (a cycle —
     unconstructible without a SHA-256 fixed point, checked anyway)
     invalidates the instrument in EVERY log order.
  G7 harness-pin enforcement: the pins_observed emitted by the instrument
     (engine, nlb_instrument/nlb_frontend/nlb_map, corpus digests, phrasing
     corpus files, lint receipt) must equal the frozen manifest constants
     below on EVERY arm body; a missing pin block or any drift fails closed.
     The pinned lint-receipt sha transitively enforces the receipt content,
     incl. waived_forced_substring == [] for l3a (ASM-0423).
  G5 existence: a missing/empty deranged arm or absent n_covered_exact is a
     BROKEN instrument, never "perfect collapse".
  G1 full counts integrity: run-level covered partition
     (exact+wrong+refused_parse+refused_engine == 600), control partition
     (answered+acceptable+other == 270; refused_any == acceptable+other;
     acceptable == strict+parse on the mapper arm, which never emits
     ABSTAIN), family-key set equality (no unexpected families), per-family
     bucket partition + exact == ok, bucket sums == run-level twins,
     zero covered buckets on control families, CONTROL-FAMILY ACCEPTABLE
     SUMS == the run-level acceptable total (14.9 item C: a dropped
     control-family classification can no longer coexist with an intact
     run-level total), all buckets non-negative integers, run-level totals
     n_covered/n_control/dev_n and dev_parse_refused strictly non-negative
     INTEGERS with dev_parse_refused <= dev_n (no float/negative counter
     can reach a gate), in-scope n_scored == 527.
  G2/G4 typing: gold-replication counters must be exact non-negative
     integers; G4 divides only well-formed in-range dev counters.

SKEPTIC ROUND-3 HARDENING (design doc 14.10, ASM-0625; all fail-closed):
  G0 defence-in-depth made COMPLETE: the scorer re-validates the FULL
     append-time supersession semantics that are order-independently
     checkable — a superseding row must carry a non-blank string `reason`,
     and NO target may be retired twice (the order-free form of
     log-append's not-already-superseded rule: in a lawful chain every
     retired row is retired exactly once, by its direct successor) — so a
     manually constructed, schema-valid, correctly hash-chained log that
     bypasses log-append can no longer reach a nominal PASS carrying an
     unreasoned or double-retired supersession. Target event/exit/phase
     remain transitively enforced: verdict-gen's eligibility filter drops
     non-run/non-final/non-ok rows before the scorer, leaving any
     reference to them dangling (G0 invalid).
  G1 SHORT-CIRCUIT: any counts-integrity failure returns a clean,
     serializable INSTRUMENT-INVALID result (gates populated, analysis
     EMPTY) BEFORE any Wilson/Holm/descriptive arithmetic — a rejected
     denominator (boolean/float/negative/missing counter, non-dict
     metrics) is never computed over and can never crash the scorer into
     verdict-gen's ERR_P2_ANALYSIS in place of the registered
     INSTRUMENT-INVALID classification. G1 additionally types EVERY
     remaining counter the analysis divides — label_strata, synonym-probe
     counters and frontend_total_ns must be well-formed non-negative
     integers (in-range) whenever present — and non-dict metrics /
     pins_observed blocks on any arm are handled fail-closed, never as
     exceptions.

Endpoints (design doc section 6 + 14.2, verdict rules in the record):
  primary   retained covered exactness == absolute covered-exact rate over
            the 527 shape-recoverable covered queries (gold ceiling MEASURED
            600/600), one-sided Wilson 95% LB (z=1.645) vs floor 0.90; UB
            feeds the FAIL rule.
  S1/S2     ONE Holm family (m=2, family alpha 0.05): control acceptable
            refusal (> 0.95 over 270, run-level totals unchanged) and covered
            wrong-answer over the 527 in-scope slice (UB < 0.02). Step-down:
            the smaller one-sided score-test p is tested at alpha/2 (Wilson
            bound at z=1.96), the other at alpha (z=1.645) only if the first
            passed. The S2 kill leg (covered_wrong_answer_wilson_lb, z=1.645)
            is exported unadjusted.
  descriptive: shape-ambiguous stratum, stage breakdown, label-verbatim vs
            paraphrase strata, dev abstention, synonym probe (never gated),
            front-end cost, audit-r1 reference.

Instrument gates G0-G7 (any failure => instrument_valid False):
  G0 one-row-per-arm (fail-closed supersede semantics above);
  G1 arm presence + counts + per-family strata match the frozen manifest
     (600 covered / 270 control / 60 dev) PLUS the 14.7 + 14.8 counts-
     integrity extensions above;
  G2 gold-replication parent-perfect (600/600 covered exact, 300/300
     strict-code control, zero wrong/answered);
  G3 phrasing-corpus lint receipt present + green + pinned corpus sha match;
  G4 dev abstention <= 0.20 (12/60);
  G5 deranged-lexicon arm EXISTS with integer counts over the full covered
     set and retained exactness < 0.10;
  G6 mapper-parse doubled pass byte-identical;
  G7 observed harness pins equal the frozen manifest on every arm.

Fixtures (--selftest) sit ON the pre-computed decision boundaries of the
design doc section 14.2 power table (n=527; independently recomputed
2026-07-10): 486/527 -> LB 0.9008 > 0.90 vs 485 -> 0.8987; UB(462) 0.8983
<= 0.90 fires FAIL vs 463 -> 0.9001; S1 Holm-worst 264/270 -> LB(z=1.96)
0.9524 > 0.95 vs 263 -> 0.9475; S2 4/527 -> UB(z=1.96) 0.0194 < 0.02 vs
5 -> 0.0220; S2 kill 16/527 -> LB(z=1.645) 0.0203 >= 0.02 vs 15 -> 0.0187.
The gated numerators are BUCKET SUMS over the 7 in-scope families, so the
boundary fixtures place the varied counts in in-scope families; an isolation
fixture proves a wrong answer in a shape-ambiguous family moves no gate;
round-2 fixtures prove duplicate arms invalidate in both log orders, an
explicit supersede is honoured, an empty deranged arm fails G5, harness-pin
drift fails G7, and every counts-integrity breach fails G1. Round-2-RE-AUDIT
fixtures (14.9, ASM-0624) reproduce the skeptic's surviving attacks and
assert each now fails closed: dict-valued and bare-string `supersedes`,
answer-all superseding a stale mapper row (cross-arm), a two-step supersede
chain (honoured), zeroed control-family ok with the run-level acceptable
total intact, float-valued 600.0/270.0/60.0 totals, and dev_parse_refused
in {-1, 0.5, 61}. ROUND-3 fixtures (14.10, ASM-0625) reproduce the round-3
skeptic's surviving attacks and assert each now fails closed: a superseding
row with a missing/empty/whitespace reason (both log orders), double
retirement (the newest row retires a target the middle row already
retired), boolean totals (n_covered/n_control/dev_n/... = True) returning a
clean serializable INSTRUMENT-INVALID with an EMPTY analysis block (no
complex Wilson values, no TypeError), non-dict metrics bodies, and
malformed descriptive counters (label_strata/probe/frontend_total_ns).
"""
import hashlib
import json
import re
import sys

EXPERIMENT = "l3a-parse"
Z_PRIMARY = 1.645   # one-sided 95%, matches kot_common.wilson_lower_bound
Z_HOLM_FIRST = 1.96  # alpha/2 leg of the m=2 Holm step-down
FLOOR = 0.90
S1_GATE = 0.95
S2_GATE = 0.02
DERANGED_MAX = 0.10
DEV_MAX_ABSTENTION = 0.20

PLANNED_COVERED = 600
PLANNED_CONTROL = 270
PLANNED_DEV = 60
# FK-NLB-10 / ASM-0420: the gated slice is the 7 shape-recoverable families
# (n_scored = 527); the 2 shape-ambiguous families are descriptive only.
IN_SCOPE_FAMILIES = ("children-lookup", "count-maker",
                     "instance-false-disjoint", "instance-true",
                     "part-lookup", "unique-father", "unique-mother")
SHAPE_AMBIGUOUS_FAMILIES = ("unique-maker", "made-lookup")
N_SCORED = 527
PLANNED_COVERED_STRATA = {
    "children-lookup": 100, "count-maker": 43, "instance-false-disjoint": 40,
    "instance-true": 50, "made-lookup": 30, "part-lookup": 50,
    "unique-father": 122, "unique-maker": 43, "unique-mother": 122}
PLANNED_CONTROL_STRATA = {
    "conflict": 20, "instance-no-record": 20, "no-record": 60,
    "out-of-scope-rel": 60, "unknown-entity": 40, "unlicensed-count": 30,
    "unlicensed-unique": 40}
EXPECTED_FAMILIES = frozenset(PLANNED_COVERED_STRATA) | \
    frozenset(PLANNED_CONTROL_STRATA)
BUCKET_KEYS = ("exact", "wrong", "refused_parse", "refused_engine")
GOLD_PERFECT = {"n_covered": 600, "n_covered_exact": 600,
                "n_control": 300, "n_control_refused_correct_code": 300,
                "n_covered_answered_wrong": 0, "n_control_answered": 0}
AUDIT_R1_REF = {
    "path": "data/nlb-phrasings-l3a/audit-recoverability-r1.json",
    "sha256": ("57e9d8d12826ae6ba28da4289fcc703109b2fb"
               "9994ef99eb589655874ea6da6d")}
# EVAL corpus pinned 2026-07-10 (EVAL-BUILD-SPEC step 6): sha256 of
# data/nlb-phrasings-l3a/eval.jsonl, checked against the run's observed
# phrasings_file in G3 (and again in G7). None would disable ONLY the
# G3 sha-equality sub-check.
EXPECTED_PHRASINGS_SHA256 = \
    "832828d892260ee53aff51d648998e3656a2d5dc16b26c55713b638964858d8a"

# ---- G7 frozen harness manifest (design doc 14.8, ASM-0621): the analysis
# REFUSES any run whose observed pins drift from the record's harness
# manifest / corpus pins. Values byte-copied from
# registry/experiments/l3a-parse.json (pins + harness_manifest) and the
# committed corpus files at the 2026-07-10 input pin.
CORPUS_RECIPE = (
    "kot-corpus-hash/1: digest = sha256 over the UTF-8 concatenation of one "
    "line per regular file under data/<corpus>/ (recursive; symlinks and "
    "directories excluded), each line '<sha256-of-file-bytes-hex>  "
    "<relpath>\\n' with exactly two spaces, relpath POSIX-style "
    "('/'-separated) relative to data/<corpus>/, lines sorted by the UTF-8 "
    "byte order of relpath; reference implementation "
    "tools/registry/corpus-pin.py"
)
EXPECTED_HARNESS_PINS = {
    "engine":
        "d26408815238cd9f73b50bb2c4b1f659c8a783ff6a5f16e27357eb2071bb3d08",
    "nlb_instrument.py":
        "b3cd5bc9ba6e311081a06110cee61801648601432e89faf8eb7b50b055c12e54",
    "nlb_frontend.py":
        "590377760ed5067688ddc0dd859c1a1cfa955e640b3a07c0f75e91d3bc908ea0",
    "nlb_map.mjs":
        "6256fc019cd4be8e64708565475976c90237bf25cd46908379c25ee7fa3d7084",
    "corpus_axioms-v0":
        "bfcb2f45969b9fe9beb41bcb435d66c078aab3b01d8e6ec387c1bf36b52da718",
    "corpus_world-v0":
        "dfa5145167b1365681b640f91c766f0a46da28af6941f35a56d00aff35408f9a",
    "corpus_l3a-eval":
        "53eb788b1681960b55436a4566df5d9fabe5efb3c57399e90fcfa2d13afb98e7",
    "corpus_kernel-v0":
        "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809",
    "corpus_molecules-v0":
        "69f0c8a354ce489d15e9156d611932ba548f80c41e78af4ffe597192067a59c4",
    "corpus_file_eval.jsonl": EXPECTED_PHRASINGS_SHA256,
    "corpus_file_dev.jsonl":
        "3022a6762148808f9083d412231aa6b790d6c7d1d5e44e58dc3c3134a5851230",
    "corpus_file_dev-entities.jsonl":
        "eda2721d17c712253d51d23fc10b27f9191322273043ca6667597d6e59518cd9",
    "corpus_file_probe.jsonl":
        "11c4bfee8587346bbec8bba0600fc26195b7f37d006f173328218f86c5a8aac2",
    "corpus_file_manifest.json":
        "63002038da1667985fa507a3ecc5d62d95f14b2f47a7458d8db22a3d2445e436",
    # lint receipt: green, findings [], waived_forced_substring [] — the sha
    # pin transitively enforces the EMPTY l3a waived list (ASM-0423).
    "phrasings_lint":
        "9716a8551349b0fd7d99d01e012fbce93d9f134ec80de8b55449dc2b48c56aed",
    "phrasings_file": EXPECTED_PHRASINGS_SHA256,
}

ARMS = ("mapper-parse", "gold-replication", "deranged-lexicon",
        "abstain-all", "answer-all")


def wilson(p, n, z, upper=False):
    if n <= 0:
        return 1.0 if upper else 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre + spread if upper else centre - spread) / (1 + z2 / n)


def score_z(p_hat, p0, n, direction):
    """One-sided score-test statistic used ONLY to order the two Holm
    hypotheses (larger z == smaller p). direction 'gt': H1 p > p0;
    'lt': H1 p < p0."""
    se = (p0 * (1 - p0) / n) ** 0.5 if n > 0 else 1.0
    z = (p_hat - p0) / se if se > 0 else 0.0
    return z if direction == "gt" else -z


def _count(v):
    """A well-formed counter: non-negative int (bool excluded)."""
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _canonical(r):
    """Byte-identical twin of tools/registry/kot_common.canonical_dumps —
    the exact serialization the single log writer (log-append) emits.
    Re-implemented here so the pinned sha stays the complete analysis
    artifact (self-contained by design, no shared import)."""
    return json.dumps(r, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def _row_sha(r):
    """kot-log/1 row identity for G0 (14.9 item A, ASM-0624): sha256 over
    the row's exact log line bytes (canonical JSON + trailing newline) —
    the SAME identity prev_sha256 and reuse.row_hashes use, so a runner
    computes a supersede target directly from the results-log line."""
    return hashlib.sha256((_canonical(r) + "\n").encode("utf-8")).hexdigest()


def _one_row_per_arm(records):
    """G0 (fail-closed; design doc 14.8 item 3 as re-based by 14.9 item A
    and completed by 14.10 item A, ASM-0621/ASM-0624/ASM-0625):
    duplicate/retry rows are never resolved by log order; the ONLY lawful
    resolution is the kot-log/1 run-row `supersedes` channel, re-verified
    here independently of log-append — INCLUDING the append-time rules that
    are order-independently checkable at read time: a superseding row must
    state a non-blank string `reason`, and no target may be retired twice
    (the order-free form of not-already-superseded).
    Returns (by_arm, ok, detail)."""
    eligible = [r for r in records if r.get("experiment") == EXPERIMENT]
    shas = [_row_sha(r) for r in eligible]
    detail = {"duplicate_arms": [], "dangling_supersedes": [],
              "malformed_supersedes": [], "cross_arm_supersedes": [],
              "self_supersedes": [], "malformed_arm": [],
              "duplicate_row_bytes": [], "arms_fully_superseded": [],
              "missing_reason": [], "retired_twice": []}
    if len(set(shas)) != len(shas):
        detail["duplicate_row_bytes"] = sorted(
            s for s in set(shas) if shas.count(s) > 1)
    arms = []
    for i, r in enumerate(eligible):
        arm = (r.get("config") or {}).get("arm")
        if not isinstance(arm, str) or not arm:
            detail["malformed_arm"].append(i)
            arm = None
        arms.append(arm)
    by_sha = {s: i for i, s in enumerate(shas)}
    superseded = set()
    for i, r in enumerate(eligible):
        sup = r.get("supersedes")
        if sup is None:
            continue
        if not (isinstance(sup, list) and sup and
                all(isinstance(t, str) and _SHA256_RE.match(t) for t in sup)
                and len(set(sup)) == len(sup)):
            # dict/string/empty/duplicate/non-hex forms all die here — a
            # malformed field never resolves anything.
            detail["malformed_supersedes"].append(i)
            continue
        # 14.10 item A (ASM-0625): re-validate log-append's mandatory
        # non-blank reason — an unreasoned retirement never resolves.
        reason = r.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            detail["missing_reason"].append(i)
        for t in sup:
            if t == shas[i]:
                detail["self_supersedes"].append(t)
            elif t not in by_sha:
                detail["dangling_supersedes"].append(t)
            elif arms[by_sha[t]] != arms[i]:
                detail["cross_arm_supersedes"].append(t)
            # 14.10 item A (ASM-0625): re-validate log-append's
            # not-already-superseded rule in its order-free form — in a
            # lawful chain every retired row is retired EXACTLY ONCE, by
            # its direct successor; a target named by two superseding rows
            # is a double retirement and never resolves.
            if t in superseded:
                detail["retired_twice"].append(t)
            superseded.add(t)
    detail["retired_twice"] = sorted(set(detail["retired_twice"]))
    by_arm, dup = {}, []
    for i, r in enumerate(eligible):
        if shas[i] in superseded or arms[i] is None:
            continue
        if arms[i] in by_arm:
            dup.append(arms[i])
        by_arm[arms[i]] = r
    # An arm with rows but zero survivors is a supersede cycle / dead chain
    # (unconstructible through log-append, which forbids forward targets;
    # checked anyway — fail closed on any input).
    detail["arms_fully_superseded"] = sorted(
        set(a for a in arms if a) - set(by_arm))
    detail["duplicate_arms"] = sorted(set(dup))
    detail["dangling_supersedes"] = sorted(set(detail["dangling_supersedes"]))
    ok = not any(detail.values())
    return by_arm, ok, {k: v for k, v in detail.items() if v}


def _pins_ok(body):
    """G7: observed harness pins on one arm body equal the frozen manifest
    (fail-closed on a missing pins block or any missing/drifted key)."""
    po = body.get("pins_observed")
    if not isinstance(po, dict) or po.get("_recipe") != CORPUS_RECIPE:
        return False
    for key, want in EXPECTED_HARNESS_PINS.items():
        v = po.get(key)
        if not isinstance(v, dict) or v.get("observed") != want:
            return False
    return True


def analyze(records):
    out = {"gates": {"instrument_valid": False}, "analysis": {}}
    by_arm, g0, g0_detail = _one_row_per_arm(records)
    out["gates"]["g0_one_row_per_arm"] = bool(g0)
    if not g0:
        out["gates"]["g0_detail"] = g0_detail
        return out
    mp = by_arm.get("mapper-parse")
    gold = by_arm.get("gold-replication")
    der = by_arm.get("deranged-lexicon")
    if mp is None:
        return out
    # 14.10 item B (ASM-0625): a non-dict metrics body is a counts-integrity
    # failure, never an exception — every read below stays total.
    m = mp.get("metrics")
    if not isinstance(m, dict):
        m = {}
    nc, ng = m.get("n_covered", 0), m.get("n_control", 0)
    n_exact = m.get("n_covered_exact", 0)
    n_wrong = m.get("n_covered_answered_wrong", 0)
    n_rparse = m.get("n_covered_refused_parse", 0)
    n_rengine = m.get("n_covered_refused_engine", 0)
    n_ctl_acc = m.get("n_control_refused_acceptable", 0)
    n_ctl_ans = m.get("n_control_answered", 0)
    n_ctl_other = m.get("n_control_refused_other", 0)
    n_ctl_any = m.get("n_control_refused_any", 0)
    n_ctl_strict = m.get("n_control_refused_strict_engine_code", 0)
    n_ctl_parse = m.get("n_control_refused_parse", 0)
    dev_n = m.get("dev_n", 0)
    dev_ref = m.get("dev_parse_refused", 0)
    fam = m.get("by_family", {})

    def buck(k, key):
        return fam.get(k, {}).get(key, 0)

    # ---- G1 counts integrity (14.7 + 14.8 extensions; any failure =>
    # instrument-invalid). Well-formedness first, so nothing below can
    # arithmetic over a malformed bucket.
    fam_keys_ok = isinstance(fam, dict) and set(fam) == EXPECTED_FAMILIES
    buckets_wellformed = fam_keys_ok and all(
        isinstance(fam[k], dict) and
        all(_count(fam[k].get(b)) for b in ("n", "ok") + BUCKET_KEYS)
        for k in EXPECTED_FAMILIES)
    if buckets_wellformed:
        strata_ok = all(fam[k]["n"] == v for k, v in
                        list(PLANNED_COVERED_STRATA.items()) +
                        list(PLANNED_CONTROL_STRATA.items()))
        # (i) in-scope n_scored == 527 (gated numerators are bucket sums over
        # the 7 in-scope families only — FK-NLB-10, ASM-0420; the two dropped
        # families' outcomes never enter a gate)
        n_scored = sum(buck(k, "n") for k in IN_SCOPE_FAMILIES)
        exact_in = sum(buck(k, "exact") for k in IN_SCOPE_FAMILIES)
        wrong_in = sum(buck(k, "wrong") for k in IN_SCOPE_FAMILIES)
        scored_ok = (n_scored == N_SCORED)
        # (ii) per covered family the bucket partition holds and exact == ok
        partition_ok = all(
            sum(buck(k, b) for b in BUCKET_KEYS) == buck(k, "n") and
            buck(k, "exact") == buck(k, "ok")
            for k in PLANNED_COVERED_STRATA)
        # (iii) covered-family bucket sums equal the run-level twins
        twins_ok = (
            sum(buck(k, "exact") for k in PLANNED_COVERED_STRATA) == n_exact
            and sum(buck(k, "wrong") for k in PLANNED_COVERED_STRATA)
            == n_wrong and
            sum(buck(k, "refused_parse") for k in PLANNED_COVERED_STRATA)
            == n_rparse and
            sum(buck(k, "refused_engine") for k in PLANNED_COVERED_STRATA)
            == n_rengine)
        # (iv) control families hold zero covered buckets; ok <= n
        control_zero_ok = all(
            all(buck(k, b) == 0 for b in BUCKET_KEYS) and
            buck(k, "ok") <= buck(k, "n")
            for k in PLANNED_CONTROL_STRATA)
        # (iv-b) 14.9 item C: the control-family acceptable ('ok') sums must
        # equal the run-level acceptable total — a zeroed/dropped control-
        # family classification can no longer coexist with an intact
        # run-level n_control_refused_acceptable (reproduced round-2 attack)
        control_sum_ok = (sum(buck(k, "ok") for k in PLANNED_CONTROL_STRATA)
                          == n_ctl_acc)
    else:
        strata_ok = scored_ok = partition_ok = twins_ok = False
        control_zero_ok = control_sum_ok = False
        n_scored = exact_in = wrong_in = 0
    # (v) run-level covered outcome partition over 600
    run_counts = (n_exact, n_wrong, n_rparse, n_rengine)
    run_partition_ok = (all(_count(x) for x in run_counts) and
                        sum(run_counts) == nc)
    # (vi) run-level control outcome partition over 270 (mapper arm: the
    # acceptable set is strict-engine-code + ERR_PARSE — FK-NLB-6; the
    # ABSTAIN branch exists only on the abstain-all arm, never here)
    ctl_counts = (n_ctl_acc, n_ctl_ans, n_ctl_other, n_ctl_any,
                  n_ctl_strict, n_ctl_parse)
    ctl_partition_ok = (all(_count(x) for x in ctl_counts) and
                        n_ctl_ans + n_ctl_acc + n_ctl_other == ng and
                        n_ctl_any == n_ctl_acc + n_ctl_other and
                        n_ctl_acc == n_ctl_strict + n_ctl_parse)
    # (vii) 14.9 item C: run-level totals and dev counters must be strict
    # non-negative INTEGERS (600.0/270.0/60.0 are not lawful counts — the
    # == comparisons above would accept them) and dev_parse_refused must be
    # a count within [0, dev_n]
    totals_int_ok = (_count(nc) and _count(ng) and _count(dev_n) and
                     _count(dev_ref) and dev_ref <= dev_n)
    # (viii) 14.10 item B (ASM-0625): every REMAINING counter the analysis
    # divides — the descriptive label_strata, synonym-probe and
    # frontend_total_ns counters — must be well-formed whenever present, so
    # once G1 is green NO malformed metric of any kind reaches arithmetic.
    ls = m.get("label_strata")
    ls_ok = ls is None or (isinstance(ls, dict) and all(
        isinstance(v, dict) and _count(v.get("n")) and _count(v.get("exact"))
        and v["exact"] <= v["n"] for v in ls.values()))
    if m.get("probe_n"):
        probe_ok = (_count(m.get("probe_n")) and
                    _count(m.get("probe_parse_ok")) and
                    _count(m.get("probe_exact")) and
                    m["probe_parse_ok"] <= m["probe_n"] and
                    m["probe_exact"] <= m["probe_n"])
    else:
        probe_ok = True
    descr_ok = ls_ok and probe_ok and _count(m.get("frontend_total_ns", 0))
    g1 = (all(a in by_arm for a in ARMS) and nc == PLANNED_COVERED and
          ng == PLANNED_CONTROL and dev_n == PLANNED_DEV and fam_keys_ok and
          buckets_wellformed and strata_ok and scored_ok and partition_ok and
          twins_ok and control_zero_ok and control_sum_ok and
          run_partition_ok and ctl_partition_ok and totals_int_ok and
          descr_ok)
    gm = gold.get("metrics") if gold else {}
    if not isinstance(gm, dict):
        gm = {}
    # G2 typed (14.9 item C): a float 600.0 must not satisfy parent-perfect
    g2 = all(_count(gm.get(k)) and gm.get(k) == v
             for k, v in GOLD_PERFECT.items())
    po_mp = mp.get("pins_observed")
    if not isinstance(po_mp, dict):
        po_mp = {}
    lint = po_mp.get("phrasings_lint")
    if not isinstance(lint, dict):
        lint = {}
    g3 = bool(lint.get("green"))
    if EXPECTED_PHRASINGS_SHA256 is not None:
        pf = po_mp.get("phrasings_file")
        if not isinstance(pf, dict):
            pf = {}
        g3 = g3 and pf.get("observed") == EXPECTED_PHRASINGS_SHA256
    # G4 hardened (14.9 item C): the division runs only over well-formed
    # in-range integer counters — dev_parse_refused in {-1, 0.5, 61} or a
    # float dev_n fails closed here (and in G1's totals_int_ok).
    g4 = (_count(dev_n) and dev_n > 0 and _count(dev_ref) and
          dev_ref <= dev_n and (dev_ref / float(dev_n)) <= DEV_MAX_ABSTENTION)
    # G5 (14.8 hardening): the deranged arm must EXIST, cover the full
    # planned covered set, and report an explicit integer exact count —
    # a missing arm or missing metric is a broken instrument, NEVER
    # "perfect collapse".
    dm = der.get("metrics") if der else {}
    if not isinstance(dm, dict):
        dm = {}
    if der is not None and dm.get("n_covered") == PLANNED_COVERED and \
            _count(dm.get("n_covered")) and _count(dm.get("n_covered_exact")):
        der_rate = dm["n_covered_exact"] / float(dm["n_covered"])
        g5 = der_rate < DERANGED_MAX
    else:
        der_rate = None
        g5 = False
    g6 = m.get("deterministic_repeat_identical") is True
    g7 = all(a in by_arm and _pins_ok(by_arm[a]) for a in ARMS)
    out["gates"].update({"g1_counts": g1, "g2_gold_replication": g2,
                         "g3_phrasing_lints": g3, "g4_dev_abstention": g4,
                         "g5_deranged_collapse": g5, "g6_determinism": g6,
                         "g7_harness_pins": g7})
    out["gates"]["instrument_valid"] = all((g0, g1, g2, g3, g4, g5, g6, g7))
    if not g1:
        # 14.10 item B (ASM-0625, round-3 freeze-blocker): a counts-
        # integrity failure SHORT-CIRCUITS the scorer BEFORE any Wilson/
        # Holm/descriptive arithmetic. A rejected denominator (boolean/
        # float/negative/missing counter) is never computed over: the
        # result is a clean, serializable INSTRUMENT-INVALID (gates
        # populated, analysis EMPTY) — never a crash that verdict-gen
        # would surface as ERR_P2_ANALYSIS in place of the registered
        # INSTRUMENT-INVALID classification.
        return out

    # ---- primary (retained == absolute over the 527 in-scope slice;
    # measured gold ceiling 600/600)
    a = out["analysis"]
    cov = exact_in / float(N_SCORED) if N_SCORED else 0.0
    a["n_covered_run"] = nc          # 600 executed (replaces n_covered)
    a["n_covered_scored"] = N_SCORED  # 527 gated (FK-NLB-10)
    a["n_control"], a["n_dev"] = ng, dev_n
    a["retained_covered_exact_rate"] = cov
    a["retained_covered_exact_wilson_lb"] = wilson(cov, N_SCORED, Z_PRIMARY)
    a["retained_covered_exact_wilson_ub"] = wilson(cov, N_SCORED, Z_PRIMARY,
                                                   True)

    # ---- secondaries (one Holm family, m=2): S1 run-level over 270,
    # S2 over the 527 in-scope slice
    ctl = n_ctl_acc / float(ng) if ng else 0.0
    wrong = wrong_in / float(N_SCORED) if N_SCORED else 1.0
    a["control_refusal_acceptable_rate"] = ctl
    a["control_refusal_acceptable_wilson_lb"] = wilson(ctl, ng, Z_PRIMARY)
    a["control_refusal_strict_engine_code_rate"] = (
        m.get("n_control_refused_strict_engine_code", 0) / float(ng)
        if ng else 0.0)
    a["covered_wrong_answer_rate"] = wrong
    a["covered_wrong_answer_wilson_ub"] = wilson(wrong, N_SCORED, Z_PRIMARY,
                                                 True)
    a["covered_wrong_answer_wilson_lb"] = wilson(wrong, N_SCORED, Z_PRIMARY)

    def s1_pass_at(z):
        return wilson(ctl, ng, z) > S1_GATE

    def s2_pass_at(z):
        return wilson(wrong, N_SCORED, z, upper=True) < S2_GATE

    z_s1 = score_z(ctl, S1_GATE, ng, "gt")
    z_s2 = score_z(wrong, S2_GATE, N_SCORED, "lt")
    if z_s1 >= z_s2:  # S1 has the smaller p -> tested at alpha/2
        s1 = s1_pass_at(Z_HOLM_FIRST)
        s2 = s1 and s2_pass_at(Z_PRIMARY)
    else:
        s2 = s2_pass_at(Z_HOLM_FIRST)
        s1 = s2 and s1_pass_at(Z_PRIMARY)
    a["holm_s1_pass"] = bool(s1)
    a["holm_s2_pass"] = bool(s2)

    # ---- shape-ambiguous stratum (FK-NLB-10, ASM-0420): DESCRIPTIVE ONLY,
    # never gated, carved out of the envelope.
    sa = {k: {"n": buck(k, "n"), "exact": buck(k, "exact"),
              "wrong": buck(k, "wrong"),
              "refused_parse": buck(k, "refused_parse"),
              "refused_engine": buck(k, "refused_engine"),
              "exact_rate": (buck(k, "exact") / float(buck(k, "n")))
              if buck(k, "n") else None}
          for k in SHAPE_AMBIGUOUS_FAMILIES}
    sa["note"] = ("descriptive only; never gated; carved out of the "
                  "envelope (FK-NLB-10, ASM-0420)")
    a["shape_ambiguous_stratum"] = sa
    a["audit_r1_ref"] = dict(AUDIT_R1_REF)

    # ---- baselines / instruments (descriptive; full-run unless noted)
    a["gold_replication_identical"] = bool(g2)
    a["deranged_retained_exact_rate"] = der_rate
    a["dev_abstention_rate"] = (dev_ref / float(dev_n)) if dev_n else 1.0
    n_parse_ref = (m.get("n_covered_refused_parse", 0) +
                   m.get("n_control_refused_parse", 0))
    a["parse_ok_rate"] = (1.0 - n_parse_ref / float(nc + ng)) \
        if (nc + ng) else 0.0
    a["parse_stage_breakdown"] = m.get("parse_stage_breakdown", {})
    ls = m.get("label_strata")
    if ls:
        a["label_verbatim_vs_paraphrase"] = {
            k: {"n": v["n"], "exact": v["exact"],
                "exact_rate": (v["exact"] / float(v["n"])) if v["n"] else None}
            for k, v in ls.items()}
    else:
        a["label_verbatim_vs_paraphrase"] = None
    if m.get("probe_n"):
        a["synonym_probe"] = {
            "probe_n": m["probe_n"], "probe_parse_ok": m["probe_parse_ok"],
            "probe_exact": m["probe_exact"],
            "parse_ok_rate": m["probe_parse_ok"] / float(m["probe_n"]),
            "exact_rate": m["probe_exact"] / float(m["probe_n"]),
            "note": "descriptive only; never gated (FK-NLB-8)"}
    else:
        a["synonym_probe"] = None
    a["frontend_mean_us_per_query"] = (
        m.get("frontend_total_ns", 0) / float(nc + ng) / 1000.0
        if (nc + ng) else 0.0)
    return out


def _fam(n, exact=None, wrong=0, rparse=0, rengine=0):
    """One covered family's enriched bucket record; exact defaults to the
    residual so the partition exact+wrong+refused_parse+refused_engine == n
    holds and exact == ok."""
    if exact is None:
        exact = n - wrong - rparse - rengine
    return {"n": n, "ok": exact, "exact": exact, "wrong": wrong,
            "refused_parse": rparse, "refused_engine": rengine}


def _pins():
    """Fixture pins_observed matching the frozen manifest (G7)."""
    po = {"_recipe": CORPUS_RECIPE}
    for k, v in EXPECTED_HARNESS_PINS.items():
        po[k] = {"observed": v}
    po["phrasings_lint"]["green"] = True
    return po


def _rec(arm, covered=None, control_accept=270, control_parse=40, **kw):
    # Covered families default to all-exact; `covered` overrides named
    # families with explicit buckets (run-level covered twins are DERIVED
    # from by_family so G1 twins-integrity holds by construction). Control
    # counters keep the score_nl identities: acceptable = strict + parse,
    # other = n_control - acceptable (answered 0), any = acceptable + other.
    cov = {k: _fam(v) for k, v in PLANNED_COVERED_STRATA.items()}
    for k, b in (covered or {}).items():
        assert b["n"] == PLANNED_COVERED_STRATA[k], (k, b)
        cov[k] = b
    fam = dict(cov)
    # 14.10: fixtures model an INTERNALLY CONSISTENT instrument — the
    # non-acceptable control remainder (PLANNED_CONTROL - control_accept)
    # is deducted from the by_family 'ok' counts so the 14.9 item-C
    # control-sum invariant holds by construction (G1 now short-circuits,
    # so a Holm-boundary fixture may no longer ride on an inconsistent
    # control split).
    deficit = PLANNED_CONTROL - control_accept
    for k, v in sorted(PLANNED_CONTROL_STRATA.items()):
        take = min(deficit, v)
        deficit -= take
        fam[k] = {"n": v, "ok": v - take, "exact": 0, "wrong": 0,
                  "refused_parse": 0, "refused_engine": 0}
    ce = sum(cov[k]["exact"] for k in cov)
    cw = sum(cov[k]["wrong"] for k in cov)
    cp = sum(cov[k]["refused_parse"] for k in cov)
    cg = sum(cov[k]["refused_engine"] for k in cov)
    ctl_other = PLANNED_CONTROL - control_accept
    m = {"n_covered": 600, "n_covered_exact": ce,
         "n_covered_refused_parse": cp, "n_covered_refused_engine": cg,
         "n_covered_answered_wrong": cw, "n_control": 270,
         "n_control_refused_acceptable": control_accept,
         "n_control_refused_strict_engine_code":
             control_accept - control_parse,
         "n_control_refused_parse": control_parse,
         "n_control_refused_other": ctl_other,
         "n_control_answered": 0,
         "n_control_refused_any": control_accept + ctl_other,
         "by_family": fam, "parse_stage_breakdown": {},
         "label_strata": {"verbatim": {"n": 300, "exact": 300},
                          "paraphrase": {"n": 300, "exact": 300}},
         "dev_n": 60, "dev_parse_refused": 7,
         "deterministic_repeat_identical": True,
         "frontend_total_ns": 600000000}
    m.update(kw)
    # Fixture bodies mirror REAL eligible log rows (verdict-gen passes the
    # stamped kot-log/1 rows through): run event, final phase, ok exit.
    body = {"experiment": EXPERIMENT, "event": "run", "phase": "final",
            "exit": "ok", "config": {"arm": arm}, "metrics": m,
            "pins_observed": _pins()}
    if arm == "gold-replication":
        body["metrics"] = dict(GOLD_PERFECT)
        body["metrics"]["deterministic_repeat_identical"] = True
    if arm == "deranged-lexicon":
        m2 = dict(m)
        m2.update({"n_covered_exact": 0, "n_covered_answered_wrong": 20})
        body["metrics"] = m2
    return body


def _suite(**mp_kw):
    return [_rec("mapper-parse", **mp_kw), _rec("gold-replication"),
            _rec("deranged-lexicon"), _rec("abstain-all"),
            _rec("answer-all")]


def selftest():
    base = analyze(_suite())
    assert base["gates"]["instrument_valid"] is True, base["gates"]
    a = base["analysis"]
    assert a["n_covered_run"] == 600 and a["n_covered_scored"] == 527, a
    assert a["retained_covered_exact_rate"] == 1.0
    assert a["holm_s1_pass"] and a["holm_s2_pass"]
    assert a["synonym_probe"] is None
    # shape-ambiguous stratum present, descriptive, all-exact in the base
    assert a["shape_ambiguous_stratum"]["unique-maker"]["n"] == 43
    assert a["shape_ambiguous_stratum"]["made-lookup"]["n"] == 30
    assert a["audit_r1_ref"]["sha256"].startswith("57e9d8d1")
    # primary decision boundary (section 14.2 table, n=527): the varied
    # counts sit in an IN-SCOPE family (unique-father) as refusals.
    hi = analyze(_suite(covered={"unique-father": _fam(122, exact=81,
                                                       rparse=41)}))["analysis"]
    lo = analyze(_suite(covered={"unique-father": _fam(122, exact=80,
                                                       rparse=42)}))["analysis"]
    assert hi["retained_covered_exact_wilson_lb"] > FLOOR, hi
    assert lo["retained_covered_exact_wilson_lb"] <= FLOOR, lo
    kill = analyze(_suite(covered={"unique-father": _fam(122, exact=57,
                                                         rparse=65)}))
    nokill = analyze(_suite(covered={"unique-father": _fam(122, exact=58,
                                                           rparse=64)}))
    assert kill["analysis"]["retained_covered_exact_wilson_ub"] <= FLOOR, kill
    assert nokill["analysis"]["retained_covered_exact_wilson_ub"] > FLOOR, \
        nokill
    # S1 boundary at the HOLM-WORST level: with S2 at 5/527 (z ~1.72), S1
    # wins the ordering at both 264/270 (z ~2.09) and 263/270 (z ~1.81) and
    # is therefore tested at alpha/2 (z=1.96) — 264 passes, 263 fails (and
    # blocks S2). w=5 is the unique in-scope wrong count that keeps S1 first
    # AND lets S2 pass at nominal when S1 passes (UB(5/527,1.645)=0.0194).
    s1hi = analyze(_suite(control_accept=264,
                          covered={"unique-father": _fam(122, exact=117,
                                                         wrong=5)}))["analysis"]
    s1lo = analyze(_suite(control_accept=263,
                          covered={"unique-father": _fam(122, exact=117,
                                                         wrong=5)}))["analysis"]
    assert s1hi["holm_s1_pass"] is True and s1hi["holm_s2_pass"] is True, s1hi
    assert s1lo["holm_s1_pass"] is False and s1lo["holm_s2_pass"] is False, \
        s1lo
    # S1 at the nominal-alpha leg (S2 dominant at 0/527): 263/270 passes
    s1nom = analyze(_suite(control_accept=263))["analysis"]
    assert s1nom["holm_s1_pass"] is True, s1nom
    # S2 Holm-worst boundary (4 vs 5 wrong at z=1.96), asserted directly
    assert wilson(4 / 527.0, 527, Z_HOLM_FIRST, True) < S2_GATE
    assert wilson(5 / 527.0, 527, Z_HOLM_FIRST, True) > S2_GATE
    s2a = analyze(_suite(covered={"unique-father": _fam(122, exact=118,
                                                        wrong=4)}))["analysis"]
    assert s2a["holm_s2_pass"] is True, s2a
    # S2 kill boundary, unadjusted z=1.645 (fires from 16/527)
    s2c = analyze(_suite(covered={"unique-father": _fam(122, exact=106,
                                                        wrong=16)}))["analysis"]
    s2d = analyze(_suite(covered={"unique-father": _fam(122, exact=107,
                                                        wrong=15)}))["analysis"]
    assert s2c["covered_wrong_answer_wilson_lb"] >= S2_GATE, s2c
    assert s2d["covered_wrong_answer_wilson_lb"] < S2_GATE, s2d
    # Holm step-down: a failed first hypothesis blocks the second
    both = analyze(_suite(control_accept=200))["analysis"]
    assert both["holm_s1_pass"] is False and both["holm_s2_pass"] is True, both
    # ISOLATION (14.7 step 5): a wrong answer in a SHAPE-AMBIGUOUS family
    # moves NO gate and NO gated numerator; it appears ONLY in the
    # shape_ambiguous_stratum descriptive.
    iso = analyze(_suite(covered={"unique-maker": _fam(43, exact=33,
                                                       wrong=10)}))
    ia = iso["analysis"]
    assert iso["gates"]["instrument_valid"] is True, iso["gates"]
    assert ia["retained_covered_exact_rate"] == 1.0, ia
    assert ia["covered_wrong_answer_rate"] == 0.0, ia
    assert ia["holm_s2_pass"] is True, ia
    assert ia["shape_ambiguous_stratum"]["unique-maker"]["wrong"] == 10, ia
    assert ia["shape_ambiguous_stratum"]["made-lookup"]["wrong"] == 0, ia
    # G1 counts-integrity: a broken bucket partition => instrument-invalid
    broken = analyze(_suite(covered={"unique-father": {
        "n": 122, "ok": 122, "exact": 100, "wrong": 0,
        "refused_parse": 0, "refused_engine": 0}}))
    assert broken["gates"]["instrument_valid"] is False, broken["gates"]
    assert broken["gates"]["g1_counts"] is False, broken["gates"]
    # G1 (14.8): mutually inconsistent RUN-LEVEL counters => invalid
    recs = _suite()
    recs[0]["metrics"]["n_covered_exact"] = 600
    recs[0]["metrics"]["n_covered_refused_parse"] = 600
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.8): an unexpected family => invalid
    recs = _suite()
    recs[0]["metrics"]["by_family"]["mystery-family"] = _fam(1)
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.8): nonzero covered bucket on a CONTROL family => invalid
    recs = _suite()
    recs[0]["metrics"]["by_family"]["no-record"]["exact"] = 1
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.8): negative / non-integer buckets => invalid
    recs = _suite()
    recs[0]["metrics"]["by_family"]["children-lookup"]["wrong"] = -1
    assert analyze(recs)["gates"]["g1_counts"] is False
    recs = _suite()
    recs[0]["metrics"]["by_family"]["children-lookup"]["exact"] = 99.0
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.8): broken control partition (acceptable != strict + parse)
    recs = _suite()
    recs[0]["metrics"]["n_control_refused_strict_engine_code"] = 220
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.9, reproduced round-2 attack): ZEROED control-family ok with
    # the run-level acceptable total left intact — previously g1_counts was
    # True with S1 PASS and acceptable-refusal rate 1.0; now invalid
    recs = _suite()
    for k in PLANNED_CONTROL_STRATA:
        recs[0]["metrics"]["by_family"][k]["ok"] = 0
    o = analyze(recs)
    assert o["gates"]["g1_counts"] is False, o["gates"]
    assert o["gates"]["instrument_valid"] is False, o["gates"]
    # G1 (14.9, reproduced): float-valued run totals 600.0 / 270.0 / 60.0
    for key, val in (("n_covered", 600.0), ("n_control", 270.0),
                     ("dev_n", 60.0)):
        recs = _suite()
        recs[0]["metrics"][key] = val
        o = analyze(recs)
        assert o["gates"]["g1_counts"] is False, (key, o["gates"])
        assert o["gates"]["instrument_valid"] is False, (key, o["gates"])
    # G2 typed (14.9): a float gold counter is not parent-perfect
    recs = _suite()
    recs[1]["metrics"]["n_covered_exact"] = 600.0
    assert analyze(recs)["gates"]["g2_gold_replication"] is False
    # G4 hardened (14.9, reproduced): dev_parse_refused in {-1, 0.5, 61}
    for bad in (-1, 0.5, 61):
        recs = _suite()
        recs[0]["metrics"]["dev_parse_refused"] = bad
        o = analyze(recs)
        assert o["gates"]["g4_dev_abstention"] is False, (bad, o["gates"])
        assert o["gates"]["instrument_valid"] is False, (bad, o["gates"])
    # G1 SHORT-CIRCUIT (14.10, reproduced round-3 attack): BOOLEAN totals
    # and counters return a CLEAN INSTRUMENT-INVALID — no Wilson/Holm
    # arithmetic runs over the rejected denominator (previously
    # n_control=True crashed with a complex-vs-float TypeError), the output
    # is JSON-serializable, and the analysis block is EMPTY
    for key in ("n_covered", "n_control", "dev_n", "n_covered_exact",
                "n_control_refused_acceptable", "dev_parse_refused"):
        recs = _suite()
        recs[0]["metrics"][key] = True
        o = analyze(recs)
        json.dumps(o)  # must not raise: serializable, no complex values
        assert o["gates"]["g1_counts"] is False, (key, o["gates"])
        assert o["gates"]["instrument_valid"] is False, (key, o["gates"])
        assert o["analysis"] == {}, (key, o)
    # G1 SHORT-CIRCUIT (14.10): every counts-integrity failure — including
    # the reproduced float/negative forms — now stops before arithmetic
    for key, val in (("n_covered", 599), ("n_control", -1),
                     ("n_covered_exact", 0.5)):
        recs = _suite()
        recs[0]["metrics"][key] = val
        o = analyze(recs)
        json.dumps(o)
        assert o["gates"]["g1_counts"] is False, (key, o["gates"])
        assert o["analysis"] == {}, (key, o)
    # 14.10: non-dict metrics bodies are counts-integrity failures, never
    # exceptions (mapper arm => G1 short-circuit; gold arm => G2 false)
    recs = _suite()
    recs[0]["metrics"] = "bogus"
    o = analyze(recs)
    json.dumps(o)
    assert o["gates"]["g1_counts"] is False, o["gates"]
    assert o["analysis"] == {}, o
    recs = _suite()
    recs[1]["metrics"] = None
    o = analyze(recs)
    json.dumps(o)
    assert o["gates"]["g2_gold_replication"] is False, o["gates"]
    assert o["gates"]["instrument_valid"] is False, o["gates"]
    # 14.10: malformed DESCRIPTIVE counters (label_strata / probe /
    # frontend_total_ns) fail G1 instead of crashing the divisions
    recs = _suite()
    recs[0]["metrics"]["label_strata"] = {"verbatim": {"n": "x", "exact": 1}}
    o = analyze(recs)
    json.dumps(o)
    assert o["gates"]["g1_counts"] is False, o["gates"]
    assert o["analysis"] == {}, o
    recs = _suite()
    recs[0]["metrics"]["probe_n"] = True
    o = analyze(recs)
    json.dumps(o)
    assert o["gates"]["g1_counts"] is False, o["gates"]
    recs = _suite()
    recs[0]["metrics"]["frontend_total_ns"] = "1e9"
    o = analyze(recs)
    json.dumps(o)
    assert o["gates"]["g1_counts"] is False, o["gates"]
    # G0 (14.8): duplicate mapper-parse rows are INVALID in BOTH log orders
    stale = _rec("mapper-parse", covered={"unique-father": _fam(122, exact=0,
                                                                rparse=122)})
    good = _suite()
    for order in ([stale] + good, good + [stale]):
        o = analyze(order)
        assert o["gates"]["g0_one_row_per_arm"] is False, o["gates"]
        assert o["gates"]["instrument_valid"] is False, o["gates"]
    # G0: an EXPLICIT supersede (kot-log/1 row-hash channel, 14.9 item A)
    # is honoured (order-independent) and the surviving row feeds the
    # analysis
    recs = _suite()
    recs[0]["supersedes"] = [_row_sha(stale)]
    recs[0]["reason"] = "retry after simulated crash-after-append"
    for order in ([stale] + recs, recs + [stale]):
        o = analyze(order)
        assert o["gates"]["instrument_valid"] is True, o["gates"]
        assert o["analysis"]["retained_covered_exact_rate"] == 1.0, o
    # G0 (14.9): a two-step retry CHAIN is honoured — the newest row wins,
    # each step explicitly superseding its predecessor
    stale2 = _rec("mapper-parse", covered={"unique-father": _fam(122, exact=1,
                                                                 rparse=121)})
    stale2["supersedes"] = [_row_sha(stale)]
    stale2["reason"] = "first retry"
    recs = _suite()
    recs[0]["supersedes"] = [_row_sha(stale2)]
    recs[0]["reason"] = "second retry"
    o = analyze([stale, stale2] + recs)
    assert o["gates"]["instrument_valid"] is True, o["gates"]
    assert o["analysis"]["retained_covered_exact_rate"] == 1.0, o
    # G0 (14.10, reproduced round-3 attack): a superseding row with a
    # MISSING / empty / whitespace reason fails closed in BOTH log orders —
    # log-append refuses these at append time; the scorer now re-validates
    # them independently, so the defence-in-depth claim is executable
    for bad in (None, "", "   "):
        recs = _suite()
        recs[0]["supersedes"] = [_row_sha(stale)]
        if bad is not None:
            recs[0]["reason"] = bad
        for order in ([stale] + recs, recs + [stale]):
            o = analyze(order)
            assert o["gates"]["g0_one_row_per_arm"] is False, (bad, o["gates"])
            assert o["gates"]["instrument_valid"] is False, (bad, o["gates"])
            assert "missing_reason" in o["gates"]["g0_detail"], (bad, o)
    # G0 (14.10, reproduced round-3 attack): DOUBLE RETIREMENT — the newest
    # row retires BOTH prior rows although the middle row already retired
    # the first (log-append's not-already-superseded rule, re-validated
    # order-independently: no target may be retired twice)
    recs = _suite()
    recs[0]["supersedes"] = [_row_sha(stale), _row_sha(stale2)]
    recs[0]["reason"] = "over-broad retirement"
    for order in ([stale, stale2] + recs, recs + [stale2, stale]):
        o = analyze(order)
        assert o["gates"]["g0_one_row_per_arm"] is False, o["gates"]
        assert o["gates"]["instrument_valid"] is False, o["gates"]
        assert o["gates"]["g0_detail"]["retired_twice"] == \
            [_row_sha(stale)], o
    # G0: a dangling supersede target fails closed
    recs = _suite()
    recs[0]["supersedes"] = ["0" * 64]
    assert analyze(recs)["gates"]["g0_one_row_per_arm"] is False
    # G0 (14.9, reproduced round-2 attack): a DICT-valued supersedes must
    # not resolve anything — under the old scorer a dict of hash keys (and
    # a bare 64-char string, iterated char-wise) counted as supersession
    recs = _suite()
    recs[0]["supersedes"] = {_row_sha(stale): 1}
    o = analyze([stale] + recs)
    assert o["gates"]["g0_one_row_per_arm"] is False, o["gates"]
    assert o["gates"]["instrument_valid"] is False, o["gates"]
    recs = _suite()
    recs[0]["supersedes"] = _row_sha(stale)  # bare string
    assert analyze([stale] + recs)["gates"]["g0_one_row_per_arm"] is False
    # G0 (14.9, reproduced round-2 attack): CROSS-ARM supersession —
    # answer-all superseding a stale mapper-parse row — fails closed in
    # both log orders (the old scorer accepted it)
    recs = _suite()
    recs[4]["supersedes"] = [_row_sha(stale)]
    recs[4]["reason"] = "cross-arm attack"
    for order in ([stale] + recs, recs + [stale]):
        o = analyze(order)
        assert o["gates"]["g0_one_row_per_arm"] is False, o["gates"]
        assert o["gates"]["instrument_valid"] is False, o["gates"]
    # G0 (14.9): a record without a string config.arm fails closed (the
    # top-level "arm" fallback is gone — kot-log/1 forbids that key)
    recs = _suite()
    del recs[0]["config"]["arm"]
    assert analyze(recs)["gates"]["g0_one_row_per_arm"] is False
    # G5 (14.8): an EMPTY deranged arm is a broken instrument, not collapse
    recs = _suite()
    recs[2]["metrics"] = {}
    o = analyze(recs)
    assert o["gates"]["g5_deranged_collapse"] is False, o["gates"]
    assert o["gates"]["instrument_valid"] is False, o["gates"]
    assert o["analysis"]["deranged_retained_exact_rate"] is None, o
    recs = _suite()
    del recs[2]["metrics"]["n_covered_exact"]
    assert analyze(recs)["gates"]["g5_deranged_collapse"] is False
    # G7 (14.8): harness-pin drift / missing pins block => invalid
    recs = _suite()
    recs[0]["pins_observed"]["engine"] = {"observed": "f" * 64}
    o = analyze(recs)
    assert o["gates"]["g7_harness_pins"] is False, o["gates"]
    assert o["gates"]["instrument_valid"] is False, o["gates"]
    recs = _suite()
    recs[3].pop("pins_observed")
    assert analyze(recs)["gates"]["g7_harness_pins"] is False
    # gates: broken determinism / deranged leak / missing lint / dev gate
    bad = analyze(_suite(deterministic_repeat_identical=False))
    assert bad["gates"]["instrument_valid"] is False
    recs = _suite()
    recs[2]["metrics"]["n_covered_exact"] = 100
    assert analyze(recs)["gates"]["g5_deranged_collapse"] is False
    recs = _suite()
    recs[0]["pins_observed"] = {}
    assert analyze(recs)["gates"]["g3_phrasing_lints"] is False
    recs = _suite()
    recs[0]["metrics"]["dev_parse_refused"] = 13
    assert analyze(recs)["gates"]["g4_dev_abstention"] is False
    print("l3a-parse selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
