#!/usr/bin/env python3
"""g3-llmproxy-v3 pinned analysis — STAND-IN semantics-pin annotation read
(registry/experiments/g3-llmproxy-v3.json; design note
poc/g3-llmproxy-v3/design.md; SUPERSEDES g3-llmproxy-v2 after its section-6
blinding FALSE-POSITIVE abort). Statistics, gates, brackets, verdict path AND
the section-5 extraction reference implementation (fence normalization +
token normalization; ASM-0650) are BYTE-CARRIED from the superseded
analysis/g3_llmproxy_v2.py; the ONLY addition is the section-6 BLINDING-SCAN
reference implementation (the ratified truthstyle-2x2 Amendment-A1 vendor-id-
tail exclusion, reused in its exact rule form; ASM-0740) and its selftest
fixtures. Same output_fields.

Eligible run records (kot-log/1 JSON lines) on stdin; analysis-output JSON on
stdout. Stdlib only; fully deterministic (counting + Wilson bounds + the
analysis/g3.py kappa closed form — no bootstrap, no PRNG).

WHAT THIS IS (and is not): the two independent blinded HUMAN annotators the
FROZEN g3 record requires (GATE-H) are unsourced; a pinned cross-family LLM
pair (judge-pA GPT-5.6-Sol; judge-pB Claude Haiku 4.5) fills the g3.annotate
role over the SAME 200 pinned instances under the frozen two-pass protocol.
The violation rates here ARE two LLMs' blind judgments — NOT native-speaker
human competence (the HS3 estimand). g3 remains FROZEN, unconsumed, solely
adjudicating; only the human g3 can trigger HS2 auto-resolution / g5 pruning
/ Pi demotion. The record's extrapolation envelope binds every reading.

SECTION-6 BLINDING-SCAN CONTRACT (v3; the reference implementation the runner
MUST scan through — import blinding_scan / answer_blinding_hit from this
pinned file, never reimplement; poc/g3-llmproxy-v3/judge-invocation.md
section 6; ASM-0740): per call, the three surfaces user-prompt.txt,
events.jsonl and stderr.log are scanned case-insensitively for the five blind
tokens kernel / nsm / necessity / sufficiency / hypothesis. On the two
HARNESS-CAPTURED surfaces events.jsonl and stderr.log — and NEVER on
user-prompt.txt — a token match is excluded from being a HIT iff, in the
ORIGINAL (pre-lowercasing) bytes, it lies wholly inside the base62 TAIL of a
maximal Anthropic-format vendor identifier literal matching
(req|msg)_[0-9A-Za-z]{20,48} with (i) the 4-byte prefix lowercase-exact,
(ii) non-word-adjacent boundaries on both sides (a run longer than 48 fails
the maximality byte-check and is NOT excluded — fail-closed), and (iii) the
token match wholly within the tail. Every byte outside qualifying tails is
scanned byte-identically to the superseded v2 contract. ADDITIONALLY the
section-5 raw answer string (the judge-emitted answer bytes, pre-fence-
normalization) is re-scanned with ZERO exclusions (answer-surface
strictness): a real leak in item bytes or judge-emitted answer text ABORTS
exactly as before. Any non-excluded hit anywhere => ABORT to Fable (boundary
stop). This is the ratified truthstyle-2x2 A1 rule (ASM-0660,
registry/corrections/truthstyle-2x2/4-blinding-audit-amendment-a1.json;
poc/truthstyle-2x2/blinding-audit-clarification.md section 9) reused
verbatim in form; g3's five tokens all contain letters outside [a-f], so the
truthstyle hex-run branch has no g3 analogue and is not carried.

Why (measured motivation): the v2 run 20260710T204828Z ABORTED on pass-A
item g3-friend-07 when the pinned v2 section-6 whole-file grep hit 'nsM'
inside the harness-stamped identifier req_011Ccu3G1KQZ8ciX3SvEfnsM at offset
2242 of events.jsonl — user-prompt.txt clean, stderr clean, answer text
clean, the judge never saw the token. Every captured judge-pB attempt
carries exactly TWO such base62 ids (24-char tails; judge-pA/codex captures
carry none), so a perfectly blind 430-call judge-pB run expects ~0.6
coincidental 'nsm' hits (22 windows x (2/62)^3 x 2 ids x 430 calls) and the
unamended scan aborts a clean run with probability ~0.5 under the null — a
control that fires on machinery metadata under the null detects nothing.

SECTION-5 EXTRACTION CONTRACT (carried v2 fix, byte-identical semantics; the
reference implementation the runner MUST label through — import
extract_answer_object / normalize_token from this pinned file, never
reimplement; poc/g3-llmproxy-v3/judge-invocation.md section 5; ASM-0650):
the raw answer string (judge-pA last-message.json bytes; judge-pB the result
field of the single success event) is first put through FENCE NORMALIZATION
— strip ASCII whitespace; if the string now both starts and ends with ```
remove exactly ONE fence layer (the opening ``` plus an optional language
tag matching [A-Za-z0-9_-]{0,16} plus optional spaces or tabs plus, when
present, the first newline; and the closing ```), then strip again; a string
still starting with ``` after one removal is INVALID (single layer only).
The result must json.loads over its ENTIRE length to exactly one JSON
object. Fence normalization is content-blind FORMAT normalization in the
same class as the token normalization below: deterministic, applied before
any answer field is read, unable to change which label is extracted — never
answer repair. First-valid-answer-final and the <=3-content-attempt/no-label
accounting are unchanged from the superseded records.

TOKEN NORMALIZATION (unchanged contract): strip ASCII whitespace, drop at
most one trailing '.', ASCII-lowercase, map 'cannot say' -> 'cannot-say';
VALID iff the result is byte-exactly one of yes / no / cannot-say.

DERIVED VIOLATIONS (frozen rule verbatim, annotation-protocol.md): necessity
violation iff q1 = yes AND q2 = no; sufficiency violation iff q1 = no AND
q2 = yes. An instance is DECISIVE for a judge iff its q1 AND q2 are both in
{yes, no}; DUAL-DECISIVE iff decisive for both judges. cannot-say is neither
violation nor satisfaction (ASM-0533/ASM-0554); no-label leaves denominators.

TWO-SIDED BRACKET (prereg S4/S6, ASM-0531 — the human record's combination
rule stays unconsumed): over dual-decisive instances,
  concordant rate = both judges derive the violation (the FAIL-analog side);
  union rate      = either judge derives it        (the PASS-analog side).
Wilson bounds z = 1.645 (the analysis/g3.py closed form verbatim) over
n_dual_decisive. Verdict path (record rules, first match wins):
INSTRUMENT-INVALID on either gate -> FAIL-analog iff concordant necessity
Wilson LB > 0.10 (/analysis/proxy_fail) -> PASS-analog iff union necessity
Wilson UB <= 0.10 (/analysis/proxy_pass; the envelope caps ANY PASS at 'weak
feasibility proxy') -> INCONCLUSIVE catch-all (missing record => fields
unset => fail closed). Each verdict direction clears under the combination
rule LEAST favourable to it.

GATES (prereg S4/S5; INSTRUMENT-INVALID, never FAIL/PASS):
  adjudication_valid: preflight_pass AND n_dual_decisive >= 170/200 AND
                      per judge per pass cannot-say <= 5% AND no-label <= 5%
                      AND kappa_pair >= 0.4 (the frozen g3 kappa rule carried
                      over as judge-pair instability, never FAIL).
  probe_valid:        probe-B (mismatched-conditions control), PER JUDGE:
                      coverage >= 27/30 AND false-satisfaction (q2=yes where
                      'no' is correct by construction) point-rate < 0.30.

SECONDARY: same bracket on sufficiency (union UB <= 0.10 =>
sufficiency_equivalence_survives_proxy); per-judge rates; escape rates; the
pass-B failing-cid histogram (diagnostic only — the beginnings of the failure
taxonomy the human round will need).

Fixture: --selftest (constructed records; HAND-COMPUTED values in comments —
the 12/200 and 30/200 Wilson constants are the analysis/g3.py fixture values
verbatim; kappa cross-checked by hand at staging, 2026-07-10) PLUS the
carried v2 extraction-contract fixtures (the EXACT fenced pass-B defect
bytes from the aborted v1 run) PLUS the v3 blinding-scan fixtures: the EXACT
v2-abort bytes (the g3-friend-07 request_id containing 'nsM') proven
EXCLUDED on the captured surface, and real-leak shapes (item bytes,
judge-emitted answer text, delimited stderr spellings, malformed/oversized/
embedded id lookalikes) proven to still ABORT. The spec's section-8
preflight requires this selftest to pass BEFORE any judge call.
"""
import json
import os
import re
import sys

Z = 1.645                    # one-sided 95% each side, analysis/g3.py verbatim
BAR = 0.10                   # the frozen g3 10% bar verbatim
KAPPA_MIN = 0.4              # frozen g3 rule carried over (instrument only)
DUAL_DECISIVE_MIN = 170      # of 200
ESCAPE_MAX = 0.05            # per judge per pass (protocol ~5%, mechanical)
NOLABEL_MAX = 0.05           # per judge per pass
PROBE_LABELLED_MIN = 27      # of 30, per judge
PROBE_FALSE_SAT_BAR = 0.30   # point rule; >= 0.30 invalidates
ARM = "instance-annotation-instrument"
JUDGES = ("judge-pA", "judge-pB")
EXPERIMENT_ID = "g3-llmproxy-v3"

# ---------------------------------------------------------------------------
# Section-6 blinding-scan contract (v3 reference implementation; ASM-0740 —
# the truthstyle-2x2 Amendment-A1 rule, ASM-0660, reused in its exact form).
# The runner MUST import and use these — no reimplementation.

BLIND_TOKENS = (b"kernel", b"nsm", b"necessity", b"sufficiency", b"hypothesis")

# Maximal Anthropic-format vendor-id literal: lowercase-exact req_/msg_ prefix
# + a 20-48 char base62 tail (all observed tails are exactly 24 chars;
# 20-48 tolerates modest vendor drift while refusing short English-word-shaped
# runs; a run longer than 48 fails the maximality byte-check — fail-closed).
_VENDOR_ID_RE = re.compile(rb"(?:req|msg)_[0-9A-Za-z]{20,48}")
_WORD_BYTES = frozenset(b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        b"abcdefghijklmnopqrstuvwxyz_")


def _vendor_id_tail_spans(raw):
    """Byte spans [s, e) of the base62 TAILS (prefix excluded) of maximal
    Anthropic-format vendor-id literals in the ORIGINAL bytes (ASM-0740,
    reusing the ASM-0660 rule form verbatim)."""
    spans = []
    for m in _VENDOR_ID_RE.finditer(raw):
        s, e = m.span()
        if s > 0 and raw[s - 1] in _WORD_BYTES:
            continue                      # embedded in a longer word: no exclusion
        if e < len(raw) and raw[e] in _WORD_BYTES:
            continue                      # run continues (>48 chars): fail closed
        spans.append((s + 4, e))          # tail only; skip the 4-byte req_/msg_
    return spans


def blinding_scan(paths):
    """Section-6 per-call file scan. Returns (basename, token) for the first
    NON-EXCLUDED case-insensitive hit, or None when the surfaces are clean.
    The ASM-0740 vendor-id-tail exclusion applies ONLY to harness-captured
    surfaces; it NEVER applies to user-prompt.txt (item contamination fires
    byte-identically to the superseded v2 scan). g3's five tokens all contain
    non-hex letters, so no hex-run logic exists or is needed here."""
    for p in paths:
        if not os.path.exists(p):
            continue
        raw = open(p, "rb").read()
        data = raw.lower()
        id_spans = ([] if os.path.basename(p) == "user-prompt.txt"
                    else _vendor_id_tail_spans(raw))
        for t in BLIND_TOKENS:
            i = data.find(t)
            while i >= 0:
                if not any(s <= i and i + len(t) <= e for s, e in id_spans):
                    return (os.path.basename(p), t.decode())
                i = data.find(t, i + 1)
    return None


def answer_blinding_hit(raw_answer):
    """Answer-surface strictness (ASM-0740): the section-5 RAW answer string
    (pre-fence-normalization judge-emitted bytes) is scanned with ZERO
    exclusions — a blind token anywhere in what the judge SAID is a real
    leak channel and ABORTS even if it is id-shaped. Returns the token str
    for the first hit, or None. Non-strings scan as their repr-free absence
    (None input => no answer bytes => nothing to scan here; section-5
    validity handles the invalid attempt)."""
    if not isinstance(raw_answer, str):
        return None
    data = raw_answer.encode("utf-8", "surrogatepass").lower()
    for t in BLIND_TOKENS:
        if t in data:
            return t.decode()
    return None


# ---------------------------------------------------------------------------
# Section-5 extraction contract (carried v2 reference implementation;
# ASM-0650). The runner MUST import and use these — no reimplementation.

VALID_TOKENS = ("yes", "no", "cannot-say")

# Opening fence: ``` + optional language tag (e.g. json) + optional spaces or
# tabs + the first newline when present (LF or CRLF). Matched at position 0 of
# an already-whitespace-stripped string that starts with ```.
_FENCE_OPEN_RE = re.compile(r"^```[A-Za-z0-9_-]{0,16}[ \t]*(?:\r?\n)?")


def strip_code_fence(raw):
    """Fence normalization (section 5, carried from v2): content-blind,
    deterministic, at most ONE fence layer removed. Returns the normalized
    string, or None when a second fence layer remains (INVALID — single layer
    only). A string that never carried a fence passes through (minus outer
    ASCII whitespace) unchanged."""
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if s.startswith("```") and s.endswith("```"):
        m = _FENCE_OPEN_RE.match(s)
        body_end = len(s) - 3
        s = s[m.end():body_end] if m.end() <= body_end else ""
        s = s.strip()
        if s.startswith("```"):
            return None  # nested / second fence layer: not tolerated
    return s


def extract_answer_object(raw):
    """The section-5 answer-object extraction: fence normalization, then the
    ENTIRE remaining string must json.loads to exactly one JSON object.
    Returns the dict, or None (=> attempt INVALID; never repaired, never
    guessed). Field checks, token normalization and the pass-B list checks
    happen downstream, unchanged from the superseded contract."""
    s = strip_code_fence(raw)
    if s is None:
        return None
    try:
        obj = json.loads(s)
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


def normalize_token(tok):
    """Token normalization, contract order verbatim: strip ASCII whitespace,
    drop at most one trailing '.', ASCII-lowercase, map 'cannot say' ->
    'cannot-say'. Validity (membership in VALID_TOKENS) is the caller's
    check. Returns None for non-strings."""
    if not isinstance(tok, str):
        return None
    t = tok.strip(" \t\r\n\f\v")
    if t.endswith("."):
        t = t[:-1]
    t = t.lower()  # contract tokens are pure ASCII; lower() is ASCII-exact here
    if t == "cannot say":
        t = "cannot-say"
    return t


# ---------------------------------------------------------------------------


def wilson_bounds(p, n):
    if n <= 0:
        return 0.0, 1.0
    z2 = Z * Z
    centre = p + z2 / (2 * n)
    spread = Z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n), (centre + spread) / (1 + z2 / n)


def kappa_2x2(n11, n00, n10, n01):
    n = n11 + n00 + n10 + n01
    if n == 0:
        return 0.0
    po = (n11 + n00) / n
    a_yes, b_yes = (n11 + n10) / n, (n11 + n01) / n
    pe = a_yes * b_yes + (1 - a_yes) * (1 - b_yes)
    return 0.0 if pe == 1.0 else (po - pe) / (1 - pe)


def analyze(records):
    out = {"gates": {}, "analysis": {}}
    a = out["analysis"]
    adj = None
    for r in records:
        if r["config"]["arm"] == ARM:
            if adj is not None:
                print("g3-llmproxy-v3 analysis: duplicate %s record" % ARM,
                      file=sys.stderr)
                sys.exit(1)
            adj = r["metrics"]
    if adj is None:
        return out  # fields unset => INCONCLUSIVE (fail closed)

    n_inst = int(adj["n_instances"])
    n_dual = int(adj["n_dual_decisive"])
    preflight = bool(adj["preflight_pass"])
    a["n_instances"] = n_inst
    a["n_dual_decisive"] = n_dual

    # ---- kappa on the per-instance necessity indicator (dual-decisive 2x2) --
    nb, nn = int(adj["n_nec_both"]), int(adj["n_nec_neither"])
    na, nb2 = int(adj["n_nec_a_only"]), int(adj["n_nec_b_only"])
    if nb + nn + na + nb2 != n_dual:
        print("g3-llmproxy-v3 analysis: necessity 2x2 does not sum to "
              "n_dual_decisive", file=sys.stderr)
        sys.exit(1)
    kap = kappa_2x2(nb, nn, na, nb2)
    a["kappa_pair"] = kap

    # ---- bracket counts must be consistent with the 2x2 ---------------------
    n_conc = int(adj["n_necessity_concordant"])
    n_union = int(adj["n_necessity_union"])
    if n_conc != nb or n_union != nb + na + nb2:
        print("g3-llmproxy-v3 analysis: bracket counts inconsistent with the "
              "necessity 2x2", file=sys.stderr)
        sys.exit(1)

    # ---- escape / no-label / coverage gate ----------------------------------
    escape_ok = True
    escapes = {}
    for j, tag in (("judge-pA", "a"), ("judge-pB", "b")):
        row = {}
        for pas, ptag in (("pass_a", "1"), ("pass_b", "2")):
            cs = int(adj["n_cannot_say_%s%s" % (tag, ptag)])
            nl = int(adj["n_nolabel_%s%s" % (tag, ptag)])
            cs_rate = (cs / n_inst) if n_inst else 1.0
            nl_rate = (nl / n_inst) if n_inst else 1.0
            row["%s_cannot_say" % pas] = cs_rate
            row["%s_nolabel" % pas] = nl_rate
            if cs_rate > ESCAPE_MAX + 1e-12 or nl_rate > NOLABEL_MAX + 1e-12:
                escape_ok = False
        escapes[j] = row
    a["escape_rates"] = escapes
    out["gates"]["adjudication_valid"] = (
        preflight and n_dual >= DUAL_DECISIVE_MIN and escape_ok
        and kap >= KAPPA_MIN - 1e-12)

    # ---- probe-B gate, per judge ---------------------------------------------
    probe_rates, probe_ok = {}, True
    for j, tag in (("judge-pA", "a"), ("judge-pB", "b")):
        n_lab = int(adj["n_probe_labelled_%s" % tag])
        n_fs = int(adj["n_probe_false_sat_%s" % tag])
        rate = (n_fs / n_lab) if n_lab else 1.0  # fail closed
        probe_rates[j] = rate
        if n_lab < PROBE_LABELLED_MIN or rate >= PROBE_FALSE_SAT_BAR - 1e-12:
            probe_ok = False
    a["probe_false_satisfaction_rates"] = probe_rates
    out["gates"]["probe_valid"] = probe_ok

    # ---- the two-sided bracket on necessity and sufficiency ------------------
    for name, conc_k, union_k in (
            ("necessity", "n_necessity_concordant", "n_necessity_union"),
            ("sufficiency", "n_sufficiency_concordant", "n_sufficiency_union")):
        for rule, key in (("concordant", conc_k), ("union", union_k)):
            k = int(adj[key])
            rate = (k / n_dual) if n_dual else 0.0
            lb, ub = wilson_bounds(rate, n_dual)
            a["%s_rate_%s" % (name, rule)] = rate
            a["%s_%s_wilson_lb" % (name, rule)] = lb
            a["%s_%s_wilson_ub" % (name, rule)] = ub
    a["sufficiency_equivalence_survives_proxy"] = (
        a["sufficiency_union_wilson_ub"] <= BAR)
    a["proxy_fail"] = a["necessity_concordant_wilson_lb"] > BAR
    a["proxy_pass"] = a["necessity_union_wilson_ub"] <= BAR

    # ---- reported-only per-judge diagnostics ---------------------------------
    a["per_judge_necessity_rates"] = {
        j: (int(adj["n_necessity_%s" % t]) / n_dual) if n_dual else 0.0
        for j, t in (("judge-pA", "a"), ("judge-pB", "b"))}
    a["per_judge_sufficiency_rates"] = {
        j: (int(adj["n_sufficiency_%s" % t]) / n_dual) if n_dual else 0.0
        for j, t in (("judge-pA", "a"), ("judge-pB", "b"))}
    hist = adj["failing_cid_histogram"]
    a["failing_cid_histogram"] = {str(k): int(v) for k, v in sorted(hist.items())}
    return out


# --------------------------------------------------------------------------
def _rec(n_inst=200, n_dual=200, nec_both=5, nec_a=3, nec_b=4,
         suf_conc=2, suf_union=6, cs=(4, 6, 3, 5), nl=(2, 3, 1, 2),
         probe=(29, 3, 28, 4), nec_j=(8, 9), suf_j=(4, 5),
         hist=None, preflight=True):
    nec_neither = n_dual - nec_both - nec_a - nec_b
    m = {"n_instances": n_inst, "n_dual_decisive": n_dual,
         "n_nec_both": nec_both, "n_nec_neither": nec_neither,
         "n_nec_a_only": nec_a, "n_nec_b_only": nec_b,
         "n_necessity_concordant": nec_both,
         "n_necessity_union": nec_both + nec_a + nec_b,
         "n_sufficiency_concordant": suf_conc,
         "n_sufficiency_union": suf_union,
         "n_cannot_say_a1": cs[0], "n_cannot_say_a2": cs[1],
         "n_cannot_say_b1": cs[2], "n_cannot_say_b2": cs[3],
         "n_nolabel_a1": nl[0], "n_nolabel_a2": nl[1],
         "n_nolabel_b1": nl[2], "n_nolabel_b2": nl[3],
         "n_probe_labelled_a": probe[0], "n_probe_false_sat_a": probe[1],
         "n_probe_labelled_b": probe[2], "n_probe_false_sat_b": probe[3],
         "n_necessity_a": nec_j[0], "n_necessity_b": nec_j[1],
         "n_sufficiency_a": suf_j[0], "n_sufficiency_b": suf_j[1],
         "failing_cid_histogram": hist if hist is not None
         else {"c1": 4, "c3": 9},
         "preflight_pass": preflight, "labels_sha256": "0" * 64}
    return {"config": {"arm": ARM, "rung": "none", "retry_budget": 0,
                       "escalation_budget": 0, "seed": 0}, "metrics": m}


# The EXACT byte neighbourhood of the v2 abort (poc/g3-llmproxy-v2/opus-runs/
# 20260710T204828Z/judge-pB-haiku45/passA/g3-friend-07/c1_t0/events.jsonl,
# bytes 2202..2302 verbatim; the 'nsM' the v2 scan hit is the tail-final
# trigram of the harness-stamped request_id):
V2_ABORT_BYTES = (b'a-4d0d-95ea-7536f45f30c0","request_id":'
                  b'"req_011Ccu3G1KQZ8ciX3SvEfnsM"}\n'
                  b'{"type":"result","subtype":"s')


def selftest_blinding():
    """The v3 section-6 blinding-scan fixtures (ASM-0740). Fixture 1 is the
    EXACT v2-abort bytes: the false positive this record exists to fix must
    now be EXCLUDED on the captured surface. Every other fixture proves the
    scan is NOT relaxed anywhere a real leak could live: item bytes,
    judge-emitted answer text, delimited spellings, malformed / embedded /
    oversized id lookalikes. The section-8 preflight requires this selftest
    before any judge call."""
    import shutil
    import tempfile
    d = tempfile.mkdtemp(prefix="g3lp3-blind-selftest.")
    try:
        def w(name, data):
            p = os.path.join(d, name)
            with open(p, "wb") as fh:
                fh.write(data)
            return p

        # 1. THE v2 FALSE POSITIVE, verbatim bytes: 'nsM' wholly inside the
        #    24-char base62 tail of req_011Ccu3G1KQZ8ciX3SvEfnsM on the
        #    captured surface => EXCLUDED, scan clean.
        ev = w("events.jsonl", V2_ABORT_BYTES)
        assert blinding_scan([ev]) is None
        # ... and a realistic full per-attempt surface trio stays clean:
        up = w("user-prompt.txt", b"Read the text and answer the question.")
        se = w("stderr.log", b"")
        assert blinding_scan([up, ev, se]) is None

        # 2. The SAME bytes as ITEM bytes still ABORT: the exclusion NEVER
        #    applies to user-prompt.txt (a leak into the rendered item fires
        #    byte-identically to the v2 scan, id-shaped or not).
        up_leak = w("user-prompt.txt", V2_ABORT_BYTES)
        assert blinding_scan([up_leak]) == ("user-prompt.txt", "nsm")

        # 3. A real leak in JUDGE-EMITTED ANSWER TEXT still aborts: a token in
        #    a result/content block is not inside any qualifying id tail.
        ev_echo = w("events.jsonl",
                    b'{"type":"result","subtype":"success",'
                    b'"result":"the nsm condition list fails"}')
        assert blinding_scan([ev_echo]) == ("events.jsonl", "nsm")
        #    ... and the strict answer-surface scan (zero exclusions) catches
        #    a token in the answer string even when it is id-shaped:
        assert answer_blinding_hit('{"q1": "yes"}') is None
        assert answer_blinding_hit(
            '{"q2": "no", "note": "nsm"}') == "nsm"
        assert answer_blinding_hit(
            'req_011Ccu3G1KQZ8ciX3SvEfnsM') == "nsm"
        assert answer_blinding_hit(None) is None

        # 4. stderr.log: a qualifying vendor id is excluded; a delimited real
        #    spelling still trips.
        assert blinding_scan(
            [w("stderr.log", b'retry req_011Ccu3G1KQZ8ciX3SvEfnsM ok')]) is None
        assert blinding_scan(
            [w("stderr.log", b"error: nsm lexicon missing")]) == ("stderr.log",
                                                                  "nsm")

        # 5. Rule-shape boundaries (all still ABORT — fail-closed):
        #    uppercase prefix (not lowercase-exact):
        assert blinding_scan(
            [w("events.jsonl", b'"REQ_011Ccu3G1KQZ8ciX3SvEfnsM"')]) is not None
        #    tail too short (< 20 chars):
        assert blinding_scan(
            [w("events.jsonl", b'"req_0aXnsMb12"')]) is not None
        #    run longer than 48 chars fails maximality (not excluded):
        assert blinding_scan(
            [w("events.jsonl",
               b'"req_' + b"A" * 30 + b"nsM" + b"B" * 30 + b'"')]) is not None
        #    prefix embedded in a longer word (leading word byte):
        assert blinding_scan(
            [w("events.jsonl", b'"Xreq_011Ccu3G1KQZ8ciX3SvEfnsM"')]) is not None
        #    token NOT wholly inside a tail (plain prose next to an id):
        assert blinding_scan(
            [w("events.jsonl",
               b'nsm near "req_011Ccu3G1KQZ8ciX3SvEfabcd"')]) == (
                   "events.jsonl", "nsm")

        # 6. Uniform over all five tokens: 'kernel' inside a qualifying
        #    msg_ tail is excluded; delimited 'kernel' still trips.
        assert blinding_scan(
            [w("events.jsonl", b'"msg_01AbkernelXYZ0123456789"')]) is None
        assert blinding_scan(
            [w("events.jsonl", b'"text":"the kernel says"')]) == (
                "events.jsonl", "kernel")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("g3-llmproxy-v3 blinding fixtures OK "
          "(v2-abort request_id excluded; real leaks still abort)")


def selftest_extraction():
    """The carried v2 section-5 extraction-contract fixtures (ASM-0650). The
    first fixture is the EXACT defect shape from the aborted v1 run (run-log
    parse_fail captures, poc/g3-llmproxy/opus-runs/20260710T194903Z/): a
    ```json fence around a well-formed two-field pass-B object. The section-8
    preflight requires this selftest before any judge call (extraction
    self-check cal:g3lp-x1, runner-local, no judge call)."""
    want_yes = {"q2": "yes", "q2_failing_conditions": []}
    want_no = {"q2": "no", "q2_failing_conditions": ["c2"]}
    # The aborted-run defect bytes, verbatim shape:
    assert extract_answer_object(
        '```json\n{"q2": "yes", "q2_failing_conditions": []}\n```') == want_yes
    assert extract_answer_object(
        '```json\n{"q2": "no", "q2_failing_conditions": ["c2"]}\n```') == want_no
    # Bare (compliant) answers pass through untouched:
    assert extract_answer_object(
        '{"q2": "yes", "q2_failing_conditions": []}') == want_yes
    assert extract_answer_object(' {"q1": "cannot-say"} \n') == {"q1": "cannot-say"}
    # Fence variants tolerated (one layer): bare ```, tag+spaces, CRLF,
    # no-newline, outer whitespace:
    assert extract_answer_object(
        '```\n{"q2": "yes", "q2_failing_conditions": []}\n```') == want_yes
    assert extract_answer_object(
        '  ```json \n{"q2": "yes", "q2_failing_conditions": []}\n```  \n') == want_yes
    assert extract_answer_object(
        '```json\r\n{"q2": "no", "q2_failing_conditions": ["c2"]}\r\n```') == want_no
    assert extract_answer_object(
        '```json{"q2": "yes", "q2_failing_conditions": []}```') == want_yes
    # Pass-A single-field object through the same uniform path:
    assert extract_answer_object('```json\n{"q1": "no"}\n```') == {"q1": "no"}
    # Still INVALID (None), exactly as the contract demands:
    assert extract_answer_object(
        '```json\n```json\n{"q2": "yes"}\n```\n```') is None      # nested fence
    assert extract_answer_object(
        'Here it is:\n```json\n{"q2": "yes"}\n```') is None       # leading prose
    assert extract_answer_object('```json\n[1, 2]\n```') is None  # not an object
    assert extract_answer_object(
        '```json\n{"q2": "yes"} trailing\n```') is None           # trailing bytes
    assert extract_answer_object('not json at all') is None
    assert extract_answer_object('```') is None
    assert extract_answer_object(None) is None
    # Token normalization (contract order: strip, one trailing '.', lowercase,
    # map 'cannot say'):
    assert normalize_token(" Yes.\n") == "yes"
    assert normalize_token("No") == "no"
    assert normalize_token("Cannot Say.") == "cannot-say"
    assert normalize_token("cannot-say") == "cannot-say"
    assert normalize_token("yes..") == "yes."   # stays invalid downstream
    assert normalize_token(3) is None
    assert normalize_token("maybe") == "maybe"  # membership check is the caller's
    print("g3-llmproxy-v3 extraction fixtures OK (fenced pass-B answer handled)")


def selftest():
    # PASS-analog branch — HAND (the analysis/g3.py fixture constants
    # verbatim): union = 5+3+4 = 12 of 200 -> rate .06, Wilson UB = .09393
    # <= .10 => proxy_pass; concordant 5/200 -> LB .01222 (not > .10).
    # kappa 2x2 (5,188,3,4): po = 193/200 = .965; a_yes = 8/200 = .04;
    # b_yes = 9/200 = .045; pe = .04*.045 + .96*.955 = .9186;
    # kappa = (.965-.9186)/(1-.9186) = .0464/.0814 = .57003 >= .4.
    # escapes max 6/200 = .03 <= .05; probes 3/29 = .1034, 4/28 = .1429 < .30
    out = analyze([_rec()])
    assert out["gates"]["adjudication_valid"] is True
    assert out["gates"]["probe_valid"] is True
    a = out["analysis"]
    assert a["n_dual_decisive"] == 200
    assert abs(a["necessity_rate_union"] - 0.06) < 1e-12
    assert abs(a["necessity_union_wilson_ub"] - 0.09393) < 5e-5
    assert a["proxy_pass"] is True and a["proxy_fail"] is False
    assert abs(a["necessity_concordant_wilson_lb"] - 0.01222) < 5e-5
    assert abs(a["kappa_pair"] - 0.57003) < 5e-5
    assert abs(a["per_judge_necessity_rates"]["judge-pA"] - 0.04) < 1e-12
    assert abs(a["escape_rates"]["judge-pB"]["pass_b_cannot_say"] - 0.025) < 1e-12
    assert a["failing_cid_histogram"] == {"c1": 4, "c3": 9}
    # sufficiency secondary — HAND: union 6/200 -> UB (rate .03) < .10
    assert a["sufficiency_equivalence_survives_proxy"] is True

    # FAIL-analog branch — HAND (g3.py fixture verbatim): concordant 30/200
    # -> rate .15, Wilson LB = .11315 > .10 => proxy_fail. union 45/200 ->
    # rate .225. 2x2 (30, 155, 7, 8): po = .925; a_yes = .185; b_yes = .19;
    # pe = .185*.19 + .815*.81 = .69530; kappa = .22970/.30470 = .75386
    out = analyze([_rec(nec_both=30, nec_a=7, nec_b=8,
                        nec_j=(37, 38), suf_conc=2, suf_union=8)])
    a = out["analysis"]
    assert out["gates"]["adjudication_valid"] is True
    assert abs(a["necessity_concordant_wilson_lb"] - 0.11315) < 5e-5
    assert a["proxy_fail"] is True and a["proxy_pass"] is False
    assert abs(a["necessity_rate_union"] - 0.225) < 1e-12
    assert abs(a["kappa_pair"] - 0.75386) < 5e-5

    # INSTRUMENT branches (each single-cause)
    out = analyze([_rec(n_dual=169, nec_both=4, nec_a=3, nec_b=4)])
    assert out["gates"]["adjudication_valid"] is False   # dual 169 < 170
    out = analyze([_rec(cs=(11, 6, 3, 5))])              # 11/200 = .055 > .05
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(nl=(2, 11, 1, 2))])              # no-label 11 > 10
    assert out["gates"]["adjudication_valid"] is False
    out = analyze([_rec(preflight=False)])
    assert out["gates"]["adjudication_valid"] is False
    # kappa floor: 2x2 (1,183,8,8): po = .92; a_yes = .045; b_yes = .045;
    # pe = .045^2 + .955^2 = .914050; kappa = .00595/.085950 = .06923 < .4
    out = analyze([_rec(nec_both=1, nec_a=8, nec_b=8)])
    assert abs(out["analysis"]["kappa_pair"] - 0.06923) < 5e-5
    assert out["gates"]["adjudication_valid"] is False
    # probe: judge-pB 9/30 = .30 exactly => invalid (point rule boundary IN)
    out = analyze([_rec(probe=(29, 3, 30, 9))])
    assert out["gates"]["probe_valid"] is False
    out = analyze([_rec(probe=(26, 0, 28, 4))])          # coverage 26 < 27
    assert out["gates"]["probe_valid"] is False

    # cannot-say boundary IN: 10/200 = .05 exactly is allowed
    out = analyze([_rec(cs=(10, 6, 3, 5))])
    assert out["gates"]["adjudication_valid"] is True

    # missing record => everything unset => INCONCLUSIVE downstream
    out = analyze([])
    assert out == {"gates": {}, "analysis": {}}

    # carried v2 section-5 extraction contract (the fence fix)
    selftest_extraction()
    # v3 section-6 blinding-scan contract (the fix this record exists for)
    selftest_blinding()
    print("g3-llmproxy-v3 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    records = [json.loads(line) for line in sys.stdin if line.strip()]
    final = [r for r in records if r.get("phase") == "final"
             and r.get("experiment") == EXPERIMENT_ID]
    print(json.dumps(analyze(final), sort_keys=True))
