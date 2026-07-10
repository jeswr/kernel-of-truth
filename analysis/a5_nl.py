#!/usr/bin/env python3
"""a5-nl pinned analysis — NL-boundary leg, code vertical (HA5 NL analog of
HL3a clause 2; DRAFT record registry/experiments/a5-nl.json).

Eligible run records on stdin (one JSON per line, kot-log/1 bodies from
tools/experiments/nlb/nlb_instrument.py); analysis-output JSON on stdout.
Derived statistics live HERE and nowhere else (P2 G-4). Self-contained by
design: no shared helper import, so the pinned sha is the complete analysis
artifact (structural twin of analysis/l3a_parse.py with per-record constants;
a5-nl is NOT re-scoped — FK-NLB-10 is l3a-only — so the gated numerators
stay run-level over the full 855, and the ASM-0480 by_family buckets are
consumed HERE as counts-integrity invariants, not as a scope cut).

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
     (engine, kot_code desugar layer, nlb_instrument/nlb_frontend/nlb_map,
     corpus digests, phrasing corpus files, lint receipt) must equal the
     frozen manifest constants below on EVERY arm body; a missing pin block
     or any drift fails closed. The pinned lint-receipt sha transitively
     enforces the receipt content, incl. the DISCLOSED 28-item
     waived_forced_substring list (FK-NLB-11 / ASM-0423 — lawful ONLY for
     this record's non-model arms; the pinned nlb_lint blocks green for
     model-arm reuse by default).
  G5 existence: a missing/empty deranged arm or absent n_covered_exact is a
     BROKEN instrument, never "perfect collapse".
  G1 full counts integrity: run-level covered partition
     (exact+wrong+refused_parse+refused_engine == 855), control partition
     (answered+acceptable+other == 106; refused_any == acceptable+other;
     acceptable == strict+parse on the mapper arm, which never emits
     ABSTAIN), family-key set equality (no unexpected families), per-family
     bucket partition + exact == ok, bucket sums == run-level twins,
     zero covered buckets on control families, CONTROL-FAMILY ACCEPTABLE
     SUMS == the run-level acceptable total (14.9 item C: a dropped
     control-family classification can no longer coexist with an intact
     run-level total), all buckets non-negative integers, run-level totals
     n_covered/n_control/dev_n and dev_parse_refused strictly non-negative
     INTEGERS with dev_parse_refused <= dev_n (no float/negative counter
     can reach a gate).
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

Endpoints (design doc section 6, verdict rules in the record):
  primary   retained covered exactness == absolute covered-exact rate
            (gold ceiling MEASURED 855/855), one-sided Wilson 95% LB
            (z=1.645) vs floor 0.90; UB feeds the FAIL rule.
  S1/S2     ONE Holm family (m=2, family alpha 0.05): control acceptable
            refusal (> 0.90 over 106 — FK-NLB-7 gate level, decidability at
            the small control n) and covered wrong-answer (UB < 0.02 over
            855). Step-down: the smaller one-sided score-test p is tested at
            alpha/2 (Wilson bound at z=1.96), the other at alpha (z=1.645)
            only if the first passed. The S2 kill leg
            (covered_wrong_answer_wilson_lb, z=1.645) is exported unadjusted.
  descriptive: stage breakdown, label-verbatim vs paraphrase strata, dev
            abstention, synonym probe (never gated), front-end cost.

Instrument gates G0-G7 (any failure => instrument_valid False):
  G0 one-row-per-arm (fail-closed supersede semantics above);
  G1 arm presence + counts + per-family strata match the frozen manifest
     (855 covered / 106 control / 60 dev) PLUS the 14.8 counts-integrity
     extensions above;
  G2 gold-replication parent-perfect (855/855 covered exact, 122/122
     strict-code control, zero wrong/answered);
  G3 phrasing-corpus lint receipt present + green + pinned corpus sha match;
  G4 dev abstention <= 0.20 (12/60);
  G5 deranged-lexicon arm EXISTS with integer counts over the full covered
     set and retained exactness < 0.10;
  G6 mapper-parse doubled pass byte-identical;
  G7 observed harness pins equal the frozen manifest on every arm.

Fixtures (--selftest) sit ON the pre-computed decision boundaries
(independently recomputed 2026-07-10; two informative values in the DRAFT
section 7 table were corrected at freeze-candidate time): 784/855 ->
LB 0.9001 > 0.90 vs 783 -> 0.8988; UB(755) 0.8999 <= 0.90 fires FAIL vs
756 -> 0.9010; S1 Holm-worst 102/106 -> LB(z=1.96) 0.9070 > 0.90 vs
101 -> 0.8943; S2 9/855 -> UB(z=1.96) 0.0199 < 0.02 vs 10 -> 0.0214; S2 kill
24/855 -> LB(z=1.645) 0.0202 >= 0.02 vs 23 -> 0.0192. The varied counts are
placed in the contained-in family so the by_family twins integrity holds by
construction; round-2 fixtures prove duplicate arms invalidate in both log
orders, an explicit supersede is honoured, an empty deranged arm fails G5,
harness-pin drift fails G7, and every counts-integrity breach fails G1
(including the reproduced n_covered_exact=855 AND n_covered_refused_parse=855
conflict). Round-2-RE-AUDIT fixtures (14.9, ASM-0624) reproduce the
skeptic's surviving attacks and assert each now fails closed: dict-valued
and bare-string `supersedes`, answer-all superseding a stale mapper row
(cross-arm), a two-step supersede chain (honoured), zeroed control-family
ok with the run-level acceptable total intact, float-valued
855.0/106.0/60.0 totals, and dev_parse_refused in {-1, 0.5, 61}. ROUND-3
fixtures (14.10, ASM-0625) reproduce the round-3 skeptic's surviving
attacks and assert each now fails closed: a superseding row with a
missing/empty/whitespace reason (both log orders), double retirement (the
newest row retires a target the middle row already retired), boolean
totals (n_covered/n_control/dev_n/... = True) returning a clean
serializable INSTRUMENT-INVALID with an EMPTY analysis block (previously
n_covered=True reached the output with complex Wilson values and
n_control=True crashed), non-dict metrics bodies, and malformed
descriptive counters (label_strata/probe/frontend_total_ns).
"""
import hashlib
import json
import re
import sys

EXPERIMENT = "a5-nl"
Z_PRIMARY = 1.645   # one-sided 95%, matches kot_common.wilson_lower_bound
Z_HOLM_FIRST = 1.96  # alpha/2 leg of the m=2 Holm step-down
FLOOR = 0.90
S1_GATE = 0.90  # FK-NLB-7: 0.95 is undecidable at n=106 under Holm-worst
S2_GATE = 0.02
DERANGED_MAX = 0.10
DEV_MAX_ABSTENTION = 0.20

PLANNED_COVERED = 855
PLANNED_CONTROL = 106
PLANNED_DEV = 60
PLANNED_COVERED_STRATA = {
    "callees-of": 73, "callers-of": 74, "contained-in": 201, "contains": 41,
    "imported-by": 2, "imports-of": 9, "instance-false-disjoint": 38,
    "instance-true": 216, "where-defined": 201}
PLANNED_CONTROL_STRATA = {
    "conflict": 5, "no-record-callees": 15, "no-record-callers": 15,
    "no-record-contains": 10, "no-record-imported-by": 10,
    "no-record-imports": 6, "out-of-scope-concept": 6, "unknown-entity": 24,
    "unlicensed-unique": 15}
EXPECTED_FAMILIES = frozenset(PLANNED_COVERED_STRATA) | \
    frozenset(PLANNED_CONTROL_STRATA)
BUCKET_KEYS = ("exact", "wrong", "refused_parse", "refused_engine")
GOLD_PERFECT = {"n_covered": 855, "n_covered_exact": 855,
                "n_control": 122, "n_control_refused_correct_code": 122,
                "n_covered_answered_wrong": 0, "n_control_answered": 0}
# EVAL corpus pinned 2026-07-10 (EVAL-BUILD-SPEC step 6): sha256 of
# data/nlb-phrasings-a5/eval.jsonl, checked against the run's observed
# phrasings_file in G3 (and again in G7). None would disable ONLY the
# G3 sha-equality sub-check.
EXPECTED_PHRASINGS_SHA256 = \
    "746b202d27239cc1b49aa611696387080313a7116c48a8ce5cad2f963d3489c6"

# ---- G7 frozen harness manifest (design doc 14.8, ASM-0621): the analysis
# REFUSES any run whose observed pins drift from the record's harness
# manifest / corpus pins. Values byte-copied from
# registry/experiments/a5-nl.json (pins + harness_manifest) and the
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
    "code_layer":
        "9fbe2a50dcd80e100a8a32ffb5d455e9ce993424fbf0bd293b8143aef96bb99a",
    "nlb_instrument.py":
        "b3cd5bc9ba6e311081a06110cee61801648601432e89faf8eb7b50b055c12e54",
    "nlb_frontend.py":
        "590377760ed5067688ddc0dd859c1a1cfa955e640b3a07c0f75e91d3bc908ea0",
    "nlb_map.mjs":
        "6256fc019cd4be8e64708565475976c90237bf25cd46908379c25ee7fa3d7084",
    "corpus_code-axioms-v0":
        "dc930b4fdeb95994828d8b7b0a184e5d96714a3b7f51269f7d46cba5b14e39e3",
    "corpus_code-world-v0":
        "b8a8a50a3111425685cb2041061f72e4d0d89da17cb073fdffe11b338f26aef9",
    "corpus_a5-eval":
        "3676d689277660f80f7cfac9823ecb7b9b40a73777ad538623405c5c1e903843",
    "corpus_kernel-v0":
        "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809",
    "corpus_molecules-v0":
        "69f0c8a354ce489d15e9156d611932ba548f80c41e78af4ffe597192067a59c4",
    "corpus_code-v0":
        "01009b1fc0c6e34b0c49b294e0cb159695831070fbe6808957694f46d03abd83",
    "corpus_code-corpus-v0":
        "1063ad50ff694d8548296f42c17f296027768a87dba98f534e9f2ea7f7c5fea3",
    "corpus_file_eval.jsonl": EXPECTED_PHRASINGS_SHA256,
    "corpus_file_dev.jsonl":
        "09bc68f012245eb96ca745ffeeef45a9a062bb08a2b79ffebd24ceba11fba1a3",
    "corpus_file_dev-entities.jsonl":
        "f95517ff2b47f299ecbffce9f7ef6b029b7fb6ddb213a719735e539a738737d1",
    "corpus_file_probe.jsonl":
        "8ca0458c7f45e79f7a7886089b1bb6446cb386453c901e7886e4a13d62acbdf1",
    "corpus_file_manifest.json":
        "38120781d93521e60898572f0bbe1f93e26f9afbf89e0120ea1231c5f1a45107",
    # lint receipt: green, findings [], waived_forced_substring = the 28
    # DISCLOSED forced-substring qids (FK-NLB-11 / ASM-0423) — the sha pin
    # transitively enforces exactly that list, no more, no less.
    "phrasings_lint":
        "cc8a286e4165cfa949b8c679990b65cc6ff5f8723aeaf581dd9ef525be4c8c83",
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

    # ---- G1 counts integrity (14.8 extensions; any failure =>
    # instrument-invalid). Well-formedness first, so nothing below can
    # arithmetic over a malformed bucket. a5-nl is NOT re-scoped: the gated
    # numerators are the RUN-LEVEL totals; the by_family buckets are
    # consumed as integrity invariants only.
    fam_keys_ok = isinstance(fam, dict) and set(fam) == EXPECTED_FAMILIES
    buckets_wellformed = fam_keys_ok and all(
        isinstance(fam[k], dict) and
        all(_count(fam[k].get(b)) for b in ("n", "ok") + BUCKET_KEYS)
        for k in EXPECTED_FAMILIES)
    if buckets_wellformed:
        strata_ok = all(fam[k]["n"] == v for k, v in
                        list(PLANNED_COVERED_STRATA.items()) +
                        list(PLANNED_CONTROL_STRATA.items()))
        # (i) per covered family the bucket partition holds and exact == ok
        partition_ok = all(
            sum(buck(k, b) for b in BUCKET_KEYS) == buck(k, "n") and
            buck(k, "exact") == buck(k, "ok")
            for k in PLANNED_COVERED_STRATA)
        # (ii) covered-family bucket sums equal the run-level twins
        twins_ok = (
            sum(buck(k, "exact") for k in PLANNED_COVERED_STRATA) == n_exact
            and sum(buck(k, "wrong") for k in PLANNED_COVERED_STRATA)
            == n_wrong and
            sum(buck(k, "refused_parse") for k in PLANNED_COVERED_STRATA)
            == n_rparse and
            sum(buck(k, "refused_engine") for k in PLANNED_COVERED_STRATA)
            == n_rengine)
        # (iii) control families hold zero covered buckets; ok <= n
        control_zero_ok = all(
            all(buck(k, b) == 0 for b in BUCKET_KEYS) and
            buck(k, "ok") <= buck(k, "n")
            for k in PLANNED_CONTROL_STRATA)
        # (iii-b) 14.9 item C: the control-family acceptable ('ok') sums
        # must equal the run-level acceptable total — a zeroed/dropped
        # control-family classification can no longer coexist with an
        # intact run-level n_control_refused_acceptable (reproduced attack)
        control_sum_ok = (sum(buck(k, "ok") for k in PLANNED_CONTROL_STRATA)
                          == n_ctl_acc)
    else:
        strata_ok = partition_ok = twins_ok = control_zero_ok = False
        control_sum_ok = False
    # (iv) run-level covered outcome partition over 855 (the reproduced
    # finding-6 conflict — e.g. exact=855 AND refused_parse=855 — dies here)
    run_counts = (n_exact, n_wrong, n_rparse, n_rengine)
    run_partition_ok = (all(_count(x) for x in run_counts) and
                        sum(run_counts) == nc)
    # (v) run-level control outcome partition over 106 (mapper arm: the
    # acceptable set is strict-engine-code + ERR_PARSE — FK-NLB-6; the
    # ABSTAIN branch exists only on the abstain-all arm, never here)
    ctl_counts = (n_ctl_acc, n_ctl_ans, n_ctl_other, n_ctl_any,
                  n_ctl_strict, n_ctl_parse)
    ctl_partition_ok = (all(_count(x) for x in ctl_counts) and
                        n_ctl_ans + n_ctl_acc + n_ctl_other == ng and
                        n_ctl_any == n_ctl_acc + n_ctl_other and
                        n_ctl_acc == n_ctl_strict + n_ctl_parse)
    # (vi) 14.9 item C: run-level totals and dev counters must be strict
    # non-negative INTEGERS (855.0/106.0/60.0 are not lawful counts — the
    # == comparisons above would accept them) and dev_parse_refused must be
    # a count within [0, dev_n]
    totals_int_ok = (_count(nc) and _count(ng) and _count(dev_n) and
                     _count(dev_ref) and dev_ref <= dev_n)
    # (vii) 14.10 item B (ASM-0625): every REMAINING counter the analysis
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
          buckets_wellformed and strata_ok and partition_ok and twins_ok and
          control_zero_ok and control_sum_ok and run_partition_ok and
          ctl_partition_ok and totals_int_ok and descr_ok)
    gm = gold.get("metrics") if gold else {}
    if not isinstance(gm, dict):
        gm = {}
    # G2 typed (14.9 item C): a float 855.0 must not satisfy parent-perfect
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
        # populated, analysis EMPTY) — never complex Wilson values in the
        # output or a crash that verdict-gen would surface as
        # ERR_P2_ANALYSIS in place of the registered INSTRUMENT-INVALID
        # classification.
        return out

    # ---- primary (retained == absolute: measured gold ceiling 855/855)
    a = out["analysis"]
    cov = n_exact / float(nc) if nc else 0.0
    a["n_covered"], a["n_control"], a["n_dev"] = nc, ng, dev_n
    a["retained_covered_exact_rate"] = cov
    a["retained_covered_exact_wilson_lb"] = wilson(cov, nc, Z_PRIMARY)
    a["retained_covered_exact_wilson_ub"] = wilson(cov, nc, Z_PRIMARY, True)

    # ---- secondaries (one Holm family, m=2)
    ctl = n_ctl_acc / float(ng) if ng else 0.0
    wrong = n_wrong / float(nc) if nc else 1.0
    a["control_refusal_acceptable_rate"] = ctl
    a["control_refusal_acceptable_wilson_lb"] = wilson(ctl, ng, Z_PRIMARY)
    a["control_refusal_strict_engine_code_rate"] = (
        m.get("n_control_refused_strict_engine_code", 0) / float(ng)
        if ng else 0.0)
    a["covered_wrong_answer_rate"] = wrong
    a["covered_wrong_answer_wilson_ub"] = wilson(wrong, nc, Z_PRIMARY, True)
    a["covered_wrong_answer_wilson_lb"] = wilson(wrong, nc, Z_PRIMARY)

    def s1_pass_at(z):
        return wilson(ctl, ng, z) > S1_GATE

    def s2_pass_at(z):
        return wilson(wrong, nc, z, upper=True) < S2_GATE

    z_s1 = score_z(ctl, S1_GATE, ng, "gt")
    z_s2 = score_z(wrong, S2_GATE, nc, "lt")
    if z_s1 >= z_s2:  # S1 has the smaller p -> tested at alpha/2
        s1 = s1_pass_at(Z_HOLM_FIRST)
        s2 = s1 and s2_pass_at(Z_PRIMARY)
    else:
        s2 = s2_pass_at(Z_HOLM_FIRST)
        s1 = s2 and s1_pass_at(Z_PRIMARY)
    a["holm_s1_pass"] = bool(s1)
    a["holm_s2_pass"] = bool(s2)

    # ---- baselines / instruments (descriptive)
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


def _rec(arm, covered=None, control_accept=106, control_parse=24, **kw):
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
    m = {"n_covered": 855, "n_covered_exact": ce,
         "n_covered_refused_parse": cp, "n_covered_refused_engine": cg,
         "n_covered_answered_wrong": cw, "n_control": 106,
         "n_control_refused_acceptable": control_accept,
         "n_control_refused_strict_engine_code":
             control_accept - control_parse,
         "n_control_refused_parse": control_parse,
         "n_control_refused_other": ctl_other,
         "n_control_answered": 0,
         "n_control_refused_any": control_accept + ctl_other,
         "by_family": fam, "parse_stage_breakdown": {},
         "label_strata": {"verbatim": {"n": 455, "exact": 455},
                          "paraphrase": {"n": 400, "exact": 400}},
         "dev_n": 60, "dev_parse_refused": 4,
         "deterministic_repeat_identical": True,
         "frontend_total_ns": 960000000}
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
        m2.update({"n_covered_exact": 0, "n_covered_answered_wrong": 38})
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
    assert a["retained_covered_exact_rate"] == 1.0
    assert abs(a["retained_covered_exact_wilson_lb"] - 0.996845) < 1e-4
    assert a["holm_s1_pass"] and a["holm_s2_pass"]
    assert a["synonym_probe"] is None
    # primary decision boundary (recomputed table): the varied counts sit in
    # the contained-in family so by_family twins integrity holds.
    hi = analyze(_suite(covered={"contained-in": _fam(201, exact=130,
                                                      rparse=71)}))["analysis"]
    lo = analyze(_suite(covered={"contained-in": _fam(201, exact=129,
                                                      rparse=72)}))["analysis"]
    assert hi["retained_covered_exact_rate"] == 784 / 855.0, hi
    assert hi["retained_covered_exact_wilson_lb"] > FLOOR, hi
    assert lo["retained_covered_exact_wilson_lb"] <= FLOOR, lo
    kill = analyze(_suite(covered={"contained-in": _fam(201, exact=101,
                                                        rparse=100)}))["analysis"]
    nokill = analyze(_suite(covered={"contained-in": _fam(201, exact=102,
                                                          rparse=99)}))["analysis"]
    assert kill["retained_covered_exact_wilson_ub"] <= FLOOR, kill
    assert nokill["retained_covered_exact_wilson_ub"] > FLOOR, nokill
    # S1 boundary at the HOLM-WORST level: with S2 at 10/855 (z ~1.73), S1
    # wins the ordering at both 102/106 (z ~2.14) and 101/106 (z ~1.81) and
    # is tested at alpha/2 (z=1.96): 102 passes, 101 fails (and blocks S2).
    s1hi = analyze(_suite(control_accept=102,
                          covered={"contained-in": _fam(201, exact=191,
                                                        wrong=10)}))["analysis"]
    s1lo = analyze(_suite(control_accept=101,
                          covered={"contained-in": _fam(201, exact=191,
                                                        wrong=10)}))["analysis"]
    assert s1hi["holm_s1_pass"] is True and s1hi["holm_s2_pass"] is True, s1hi
    assert s1lo["holm_s1_pass"] is False and s1lo["holm_s2_pass"] is False, \
        s1lo
    # S1 at the nominal-alpha leg (S2 dominant at 0/855): 101/106 passes
    s1nom = analyze(_suite(control_accept=101))["analysis"]
    assert s1nom["holm_s1_pass"] is True, s1nom
    # S2 Holm-worst boundary (9 vs 10 wrong at z=1.96), asserted directly
    assert wilson(9 / 855.0, 855, Z_HOLM_FIRST, True) < S2_GATE
    assert wilson(10 / 855.0, 855, Z_HOLM_FIRST, True) > S2_GATE
    # S2 kill boundary, unadjusted z=1.645 (corrected: fires from 24/855)
    s2c = analyze(_suite(covered={"contained-in": _fam(201, exact=177,
                                                       wrong=24)}))["analysis"]
    s2d = analyze(_suite(covered={"contained-in": _fam(201, exact=178,
                                                       wrong=23)}))["analysis"]
    assert s2c["covered_wrong_answer_wilson_lb"] >= S2_GATE, s2c
    assert s2d["covered_wrong_answer_wilson_lb"] < S2_GATE, s2d
    # Holm step-down: a failed first hypothesis blocks the second
    both = analyze(_suite(control_accept=80))["analysis"]
    assert both["holm_s1_pass"] is False and both["holm_s2_pass"] is True, both
    # G1 (14.8): the REPRODUCED finding-6 conflict — exact and refused_parse
    # both claiming the full 855 — must be instrument-invalid.
    recs = _suite()
    recs[0]["metrics"]["n_covered_exact"] = 855
    recs[0]["metrics"]["n_covered_refused_parse"] = 855
    o = analyze(recs)
    assert o["gates"]["g1_counts"] is False, o["gates"]
    assert o["gates"]["instrument_valid"] is False, o["gates"]
    # G1 (14.8): a broken per-family bucket partition => invalid
    broken = analyze(_suite(covered={"contained-in": {
        "n": 201, "ok": 201, "exact": 150, "wrong": 0,
        "refused_parse": 0, "refused_engine": 0}}))
    assert broken["gates"]["g1_counts"] is False, broken["gates"]
    # G1 (14.8): an unexpected family => invalid
    recs = _suite()
    recs[0]["metrics"]["by_family"]["mystery-family"] = _fam(1)
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.8): nonzero covered bucket on a CONTROL family => invalid
    recs = _suite()
    recs[0]["metrics"]["by_family"]["unknown-entity"]["exact"] = 1
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.8): negative / non-integer buckets => invalid
    recs = _suite()
    recs[0]["metrics"]["by_family"]["callees-of"]["wrong"] = -1
    assert analyze(recs)["gates"]["g1_counts"] is False
    recs = _suite()
    recs[0]["metrics"]["by_family"]["callees-of"]["exact"] = 72.0
    assert analyze(recs)["gates"]["g1_counts"] is False
    # G1 (14.8): broken control partition (acceptable != strict + parse)
    recs = _suite()
    recs[0]["metrics"]["n_control_refused_strict_engine_code"] = 70
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
    # G1 (14.9, reproduced): float-valued run totals 855.0 / 106.0 / 60.0
    for key, val in (("n_covered", 855.0), ("n_control", 106.0),
                     ("dev_n", 60.0)):
        recs = _suite()
        recs[0]["metrics"][key] = val
        o = analyze(recs)
        assert o["gates"]["g1_counts"] is False, (key, o["gates"])
        assert o["gates"]["instrument_valid"] is False, (key, o["gates"])
    # G2 typed (14.9): a float gold counter is not parent-perfect
    recs = _suite()
    recs[1]["metrics"]["n_covered_exact"] = 855.0
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
    # n_covered=True reached the output with complex Wilson values and
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
    for key, val in (("n_covered", 854), ("n_control", -1),
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
    stale = _rec("mapper-parse", covered={"contained-in": _fam(201, exact=0,
                                                               rparse=201)})
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
    stale2 = _rec("mapper-parse", covered={"contained-in": _fam(201, exact=1,
                                                                rparse=200)})
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
    print("a5-nl selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
