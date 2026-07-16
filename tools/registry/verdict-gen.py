#!/usr/bin/env python3
"""verdict-gen — the verdict as a pure function of (frozen record, chained log).

    python3 tools/registry/verdict-gen.py --experiment <id> --agent-id coordinator-1
        [--root <repo>] [--computed-at 2026-07-12T18:00:00Z]

Implements P2 §3.1 (minimal spine — the F1-critical path):
  1. Load registry/experiments/<id>.json; recompute the frozen hash; require
     equality with registry/frozen-index.json (ERR_P2_FROZEN_DRIFT — no verdict
     of any kind is producible from a drifted record).
  2. Amendment overlay (P2 §1.4 / §3.1 step 2): apply kot-amend/1 records from
     registry/amendments/<id>/ in seq order as an overlay on the frozen record
     BEFORE readout. kind "ops" / "pre-authorized-fallback" amendments may ONLY
     fill a PINNED-AT-INPUTS placeholder or add a new runtime pin under /pins/;
     a patch touching design scope (endpoints, thresholds, verdict_rules, kill
     text, baselines, scale rungs, the pinned analysis script) aborts with
     ERR_P2_DESIGN_AMEND. kind "design" amendments are REFUSED once the RT-5
     cutoff has passed — the experiment is GNG-0-signed or its log contains a
     phase:"final" run record — with ERR_P2_BAD_AMENDMENT (the only lawful path
     is a new experiment id with `supersedes`). An invalid amendment always
     aborts; it is never silently skipped. The frozen record file and its
     frozen_sha256 anchor are untouched; the deterministic overlay result is
     logged in the verdict object as inputs.amended_record_sha256 alongside
     inputs.amendments_applied, so the amended record is independently
     re-derivable and verifiable from (frozen record, amendment files).
  3. Select eligible run records from results-log/<id>.jsonl (chain-verified):
     event=="run", phase=="final", exit=="ok", not superseded,
     prereg_hash == frozen_sha256, config.seed in design.seeds (when seeds are
     registered), config values within declared IV level sets. Exclusions are
     listed with the failed test named — never silent.
  3b. D9 reused-row eligibility (resource-optimization-plan.md §3 revision-1):
     rows of ANOTHER record's log enter the analysis only via a frozen
     kot-reg/2 reused_from block that re-verifies at consumption time
     (RC-1..RC-8, maintainer-ratified ruling, filled pins, producer chain +
     row hashes intact) AND an in-chain event:"reuse" witness restating the
     exact row set. A reuse witness without a frozen declaration refuses
     (ERR_P2_REUSE_UNDECLARED); >=1 fresh eligible run row is still required.
  4. Completeness gate (minimal): an empty eligible set => INCOMPLETE-DATA.
  5. Run the pinned analysis script (sha256 re-verified at execution;
     ERR_P2_FROZEN_DRIFT on mismatch) with the eligible records as JSONL on
     stdin; its stdout JSON is written to reports/auto/<id>/analysis-output.json.
     ALL derived statistics live there and nowhere else (G-4).
  5a. D10 rows-artifacts expansion (maintainer-ratified GENERAL fix,
     2026-07-15 — the 4th occurrence of the step-5 input-acquisition defect:
     knull-v2, rules-1-c, truthstyle-2x2, nsk1-r3): a ROW-HEAVY eligible
     record — one whose frozen analysis consumes bare per-item rows that
     kot-log/1 (additionalProperties:false) cannot carry at the record top
     level — declares its rows via EXACTLY ONE artifacts entry
     {path, sha256, role:"rows"}. For such a record, step 5 loads the pinned
     rows JSONL, RE-VERIFIES its sha256 against the chained log's pin
     (ERR_P2_ROWS_DRIFT — fail closed, no verdict producible from drifted
     rows), and places the EXPANDED ROWS on stdin IN PLACE OF the record
     line. Records without a role:"rows" entry keep the pre-D10 behaviour
     BYTE-IDENTICALLY (the canonical record line itself); the marked entry's
     presence is the sole, unambiguous discriminator — nothing is inferred
     from filenames or metrics. Expansions are disclosed in the verdict
     object as inputs.rows_expanded (added only when the path is taken, so
     pre-D10 verdict objects keep their exact shape). Robustness hardening
     (cross-vendor review 2026-07-15): (1) a rows artifact may back AT MOST
     ONE eligible run's expansion — two eligible marked records sharing a
     {path or sha256} fail closed (ERR_P2_ROWS_DUP; duplicated rows inflate
     n and could force a PASS with every sha check green); (2) role:"rows"
     is schema-lawful on event:"run" records only (kot-log-1.json if/else
     scope guard); (3) every expanded row must be a STRICT finite JSON
     OBJECT — NaN/Infinity/overflow literals and top-level scalars/arrays
     fail closed (ERR_P2_ROWS_MALFORMED).
  6. Write the `unblind` log line (first time only) via log-append — the single
     write path.
  7. Evaluate the frozen verdict_rules top-down with the minimal expression
     grammar (kot_common.eval_expr). A missing/null metric pointer => verdict
     INCOMPLETE-DATA (fail closed — an analysis bug cannot default to a verdict).
  8. A fired PASS is emitted as PASS-PENDING-AUDIT unless a CONFIRMED audit
     record by a non-runner identity exists under registry/audits/<id>/ (G-6).
  9. Emit registry/verdicts/<id>.json (canonical JSON; RT-14-linted).

The rendered markdown report (P2 §3.3) is S7 report-gen's job — not built here.
"""

import argparse
import datetime
import glob
import hashlib
import json
import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

# P2 §1.4 design scope — JSON-pointer prefixes that an "ops" /
# "pre-authorized-fallback" amendment may NEVER touch (endpoints and
# verdict_rules carry the thresholds; design carries baselines, scale rungs,
# seeds, IV levels; the kill/envelope text and the pinned analysis script are
# the frozen contract). Touching any of these is a design change and fails
# closed with ERR_P2_DESIGN_AMEND.
DESIGN_SCOPE_PREFIXES = (
    "/endpoints",
    "/verdict_rules",
    "/design",
    "/kill_criterion_verbatim",
    "/extrapolation_envelope_verbatim",
    "/pins/analysis_script",
    "/hypotheses",
    "/analysis_plan_ref",
    "/prereg_doc",
    "/coverage_requirement",
    "/efficiency_relevant",
    # D9: the reuse declaration is design scope — which rows a record consumes,
    # under which RC basis, may never move post-freeze by ops amendment.
    "/reused_from",
    "/reuse_overrides",
)

# kot-reg schema selection (D9: kot-reg/2 records carry the reuse surface).
SCHEMA_FILES = {"kot-reg/1": "kot-reg-1.json", "kot-reg/2": "kot-reg-2.json"}

# Freeze bookkeeping — no amendment of ANY kind may touch these.
FREEZE_FIELD_PREFIXES = ("/status", "/frozen_sha256", "/frozen_at", "/frozen_by", "/id", "/schema_version")

# An ops pin value is a bare hex digest: 40 hex (git/HF revision sha) or
# 64 hex (sha256: corpus digest, staged-bytes manifest). Nothing else.
PIN_VALUE_RE = re.compile(r"^([0-9a-f]{40}|[0-9a-f]{64})$")


def _touches(path, prefixes):
    return any(path == p or path.startswith(p + "/") for p in prefixes)


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gng0_signed(root, exp_id):
    """True iff the experiment's frozen record is covered by the GNG-0 signoff."""
    path = os.path.join(root, "registry", "gng0-signoff.json")
    if not os.path.isfile(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        signoff = json.load(f)
    return exp_id in signoff.get("frozen_records", {})


def load_amendments(root, exp_id):
    """Load, schema-validate, and RT-14-lint registry/amendments/<id>/*.json.

    Returns [(relpath, amendment)] sorted by seq. Any malformed record aborts
    (ERR_P2_BAD_AMENDMENT) — an unreadable amendment is never skipped.
    """
    paths = sorted(glob.glob(os.path.join(root, "registry", "amendments", exp_id, "*.json")))
    if not paths:
        return []
    schema_path = os.path.join(root, "registry", "schema", "kot-amend-1.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    out, seen = [], set()
    for path in paths:
        rel = os.path.relpath(path, root)
        try:
            with open(path, "r", encoding="utf-8") as f:
                am = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise kc.KotError("ERR_P2_BAD_AMENDMENT", "%s: unparseable (%s)" % (rel, e))
        errs = kc.validate_schema(am, schema)
        if errs:
            raise kc.KotError("ERR_P2_BAD_AMENDMENT", "%s: %s" % (rel, "; ".join(errs[:5])))
        if am["experiment"] != exp_id:
            raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                              "%s: experiment %r != %r" % (rel, am["experiment"], exp_id))
        prefix = os.path.basename(path).split("-", 1)[0]
        if not prefix.isdigit() or int(prefix) != am["seq"]:
            raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                              "%s: filename seq prefix does not match seq=%r (<seq>-<slug>.json)"
                              % (rel, am["seq"]))
        if am["seq"] in seen:
            raise kc.KotError("ERR_P2_BAD_AMENDMENT", "%s: duplicate amendment seq %d" % (rel, am["seq"]))
        seen.add(am["seq"])
        kc.check_identity_fields(am)
        kc.require_no_account_strings(kc.canonical_bytes(am), rel)
        out.append((rel, am))
    out.sort(key=lambda t: t[1]["seq"])
    return out


def apply_amendment_overlay(root, exp_id, record, log_records):
    """P2 §3.1 step 2: apply valid amendments in seq order as an overlay.

    Returns (effective_record, applied_seqs, effective_sha256-or-None). The
    frozen record file is never touched; the overlay is a pure function of
    (frozen record, amendment files) so effective_sha256 is re-derivable by
    any verifier. Fails closed on the first invalid amendment.
    """
    amendments = load_amendments(root, exp_id)
    if not amendments:
        return record, [], None

    signed = gng0_signed(root, exp_id)
    has_final = any(r.get("event") == "run" and r.get("phase") == "final" for r in log_records)
    effective = record
    applied = []
    for rel, am in amendments:
        for j, op in enumerate(am["patch"]):
            if _touches(op["path"], FREEZE_FIELD_PREFIXES):
                raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                  "%s patch[%d]: freeze bookkeeping field %s may never be amended"
                                  % (rel, j, op["path"]))
        if am["kind"] == "design":
            # RT-5 cutoff: design amendments die at first raw-data exposure
            # (first phase:"final" run record) — and a GNG-0-signed record's
            # design is immutable outright. The only lawful path afterwards is
            # a new experiment id with `supersedes` and a fresh freeze.
            if signed or has_final:
                raise kc.KotError(
                    "ERR_P2_BAD_AMENDMENT",
                    "%s: design amendment after the RT-5 cutoff (GNG-0-signed=%s, final-phase run "
                    "present=%s) — the frozen design is immutable; supersede with a new experiment id"
                    % (rel, signed, has_final))
        else:  # "ops" | "pre-authorized-fallback"
            if am["kind"] == "pre-authorized-fallback":
                ptr = am.get("pre_authorized_by")
                if not ptr:
                    raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                      "%s: pre-authorized-fallback must name the frozen-record field "
                                      "that pre-authorized it (pre_authorized_by)" % rel)
                if kc.resolve_pointer(record, ptr) is kc._MISSING:
                    raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                      "%s: pre_authorized_by pointer %r is not present in the frozen record"
                                      % (rel, ptr))
            for j, op in enumerate(am["patch"]):
                where = "%s patch[%d] (%s %s)" % (rel, j, op["op"], op["path"])
                if _touches(op["path"], DESIGN_SCOPE_PREFIXES):
                    raise kc.KotError(
                        "ERR_P2_DESIGN_AMEND",
                        "%s: ops-scope amendment touches design scope (endpoints / thresholds / "
                        "verdict_rules / kill text / baselines / scale rungs / pinned analysis) — "
                        "refused; a design change needs a new experiment id" % where)
                if not op["path"].startswith("/pins/"):
                    raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                      "%s: an ops amendment may only fill a PINNED-AT-INPUTS placeholder "
                                      "or add a runtime pin under /pins/" % where)
                if op["op"] == "remove":
                    raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                      "%s: ops amendments may not remove pins" % where)
                value = op.get("value")
                if not isinstance(value, str) or not PIN_VALUE_RE.match(value):
                    raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                      "%s: pin value must be a bare 40- or 64-char lowercase hex digest, "
                                      "got %r" % (where, value))
                current = kc.resolve_pointer(effective, op["path"])
                if op["op"] == "replace":
                    if not (isinstance(current, str) and current.startswith(kc.PINNED_AT_INPUTS_PREFIX)):
                        raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                          "%s: replace target is not a PINNED-AT-INPUTS placeholder "
                                          "(current=%r) — frozen pins are immutable" % (where, current))
                else:  # add
                    if current is not kc._MISSING:
                        raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                                          "%s: add target already exists — an existing pin cannot be "
                                          "overwritten" % where)
        effective = kc.json_patch_apply(effective, am["patch"])
        applied.append(am["seq"])

    # Post-overlay integrity: the effective record must still validate against
    # ITS OWN schema version (kot-reg/1 or /2) and be RT-14-clean — an overlay
    # cannot smuggle in what a freeze would have refused.
    sv = effective.get("schema_version")
    if sv not in SCHEMA_FILES:
        raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                          "amended effective record schema_version %r is not one of %s"
                          % (sv, sorted(SCHEMA_FILES)))
    schema_path = os.path.join(root, "registry", "schema", SCHEMA_FILES[sv])
    with open(schema_path, "r", encoding="utf-8") as f:
        reg_schema = json.load(f)
    errs = kc.validate_schema(effective, reg_schema)
    if errs:
        raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                          "amended effective record no longer validates against %s: %s"
                          % (sv, "; ".join(errs[:5])))
    kc.check_identity_fields(effective)
    hashed = {k: v for k, v in effective.items() if k not in ("status", "frozen_sha256")}
    kc.require_no_account_strings(kc.canonical_bytes(hashed), "amended effective record")
    return effective, applied, kc.frozen_hash(effective)


# Scale-language license total order for the min-rule (G-12 vocabulary is the
# established one across all 17 issued verdicts: none / sign-only / slope).
SCALE_LICENSE_ORDER = {"none": 0, "sign-only": 1, "slope": 2}


def scale_language_license(design, rungs, analysis):
    """Compute scale_language_licensed as the MINIMUM of three per-record caps.

    The G-12 count map (docs/research-plan/02-data-and-reporting.md:664) is
    UNCHANGED: 1 rung -> "none", 2 -> "sign-only", >=3 -> "slope"-ELIGIBLE.
    What changed (a5-llm Gate-A re-audit REFUTE 2026-07-11, adjudicated in
    docs/next/a5-llm-refute-adjudication.md section 2.1/2.2, maintainer-approved
    2026-07-11 issue #5; correction records
    registry/corrections/a5-llm/2-scale-license-erratum.json and
    registry/corrections/f2/2-scale-license-erratum.json; residual defect fixed
    per the cross-vendor re-audit
    poc/gpt56-review/a5llm-reaudit-20260711/last-message.json point 3): the
    licensed value is min over the license total order of

      (i)   the G-12 TIER OF THE COMPARABLE-RUNG COUNT — when the frozen record
            declares design.model_scale_rungs (the list of COMPARABLE
            MODEL-SCALE rung labels, 08-stats-and-extrapolation.md section 2.1
            precondition), the tier is computed over the count of MEASURED
            rungs inside that list, NOT over raw measured labels. A baseline
            label (a5-llm's R0, or any BASE* cell) can therefore inflate
            NEITHER "sign-only"->"slope" NOR "none"->"sign-only" (the
            2026-07-11 re-audit's point-3 residual: {measured=BASE0,BASE1,R1;
            model_scale_rungs=[R1]} must license "none", one comparable rung).
            A LEGACY record that never froze the field falls back to the raw
            measured-label count — byte-identical to the pre-fix generator for
            every issued license-"none"/"sign-only" verdict (f2b-replicate et
            al.) — and "slope" stays unreachable there via caps (ii)+(iii).
      (ii)  design.scale_language_max — the machine-readable frozen PER-RECORD
            ceiling (the prose ceiling lives in extrapolation_envelope_verbatim;
            this field is its machine-readable form, validated against that
            text at freeze time by prereg-freeze). Absent field => no ceiling
            permits slope => cap "sign-only" (fail closed for slope; the
            legacy "none"/"sign-only" tiers pass through unchanged). A declared
            ceiling below the tier also caps it (a declared "none" caps a
            2-rung "sign-only"). A declared value OUTSIDE the license
            vocabulary is unintelligible and caps at "none" (fail fully
            closed; the schemas + prereg-freeze refuse it at freeze time).
      (iii) the trend-validity gate — "slope" requires every JSON pointer in
            design.scale_trend_valid_metrics to resolve to boolean true in the
            analysis output: the registered section-2 trend machinery actually
            RAN and produced a VALID result (for the a5-llm shape:
            /gates/separation_valid plus the trend Holm member; a trend member
            that left the family instrument-invalid can never license a
            slope). Absent/empty metrics, a missing pointer, or no analysis at
            all (INCOMPLETE-DATA path) => cap "sign-only".

    Explicitly NOT a blunt ">=4 rungs" rule — that would rewrite G-12 /
    08-stats section 2.1, which license a scale-trend fit at >=3 COMPARABLE
    rungs, and that stays licensable here (3 comparable rungs + slope ceiling
    + valid trend result => "slope").
    """
    model_rungs = design.get("model_scale_rungs")
    if model_rungs is None:
        # Legacy record: the field was never frozen. Raw measured-label count
        # (pre-fix basis) keeps every issued 0/1/2-rung verdict byte-identical;
        # "slope" is unreachable because caps (ii)+(iii) are also absent.
        n_comparable = len(rungs)
    else:
        # Re-audit point 3: the tier is over the COUNT OF COMPARABLE rungs.
        # A declared-empty list counts zero comparable rungs (=> "none") —
        # the conservative reading, fail closed.
        n_comparable = len([r for r in rungs if r in model_rungs])
    tier = "none" if n_comparable < 2 else ("sign-only" if n_comparable == 2 else "slope")

    ceiling = design.get("scale_language_max")
    if ceiling is None:
        ceiling_cap = "sign-only"  # absent ceiling: slope fails closed; lower tiers unaffected
    elif ceiling in SCALE_LICENSE_ORDER:
        ceiling_cap = ceiling
    else:
        ceiling_cap = "none"  # unintelligible declared ceiling: fail fully closed

    trend_ptrs = design.get("scale_trend_valid_metrics") or []
    trend_valid = (bool(trend_ptrs) and analysis is not None
                   and all(kc.resolve_pointer(analysis, p) is True for p in trend_ptrs))
    trend_cap = "slope" if trend_valid else "sign-only"

    return min((tier, ceiling_cap, trend_cap), key=SCALE_LICENSE_ORDER.__getitem__)


def select_eligible(records, frozen_sha, design):
    """P2 §3.1 step 3. Returns (eligible, excluded=[{seq, reason}])."""
    superseded = {r.get("target_seq") for r in records if r.get("event") == "supersede"}
    iv_levels = {iv["name"]: iv["levels"] for iv in design.get("independent_vars", [])}
    seeds = design.get("seeds", [])
    eligible, excluded = [], []

    def exclude(rec, reason):
        excluded.append({"seq": rec["seq"], "reason": reason})

    for rec in records:
        if rec.get("event") != "run":
            continue
        if rec.get("phase") != "final":
            exclude(rec, "phase!=final (%r)" % rec.get("phase"))
            continue
        if rec.get("exit") != "ok":
            exclude(rec, "exit!=ok (%r)" % rec.get("exit"))
            continue
        if rec["seq"] in superseded:
            exclude(rec, "superseded")
            continue
        if rec.get("prereg_hash") != frozen_sha:
            exclude(rec, "prereg_hash mismatch")
            continue
        cfg = rec.get("config", {})
        if seeds and "seed" in cfg and cfg["seed"] not in seeds:
            exclude(rec, "seed %r not registered" % cfg["seed"])
            continue
        bad_level = None
        for name, levels in iv_levels.items():
            if name in cfg and cfg[name] not in levels:
                bad_level = "config.%s=%r not in declared levels" % (name, cfg[name])
                break
        if bad_level:
            exclude(rec, bad_level)
            continue
        eligible.append(rec)
    return eligible, excluded


# ---------------------------------------------------------------- D10 rows-artifacts
# The rows-artifacts convention (P2 §3.1 step 5a; kot-log-1.json description;
# maintainer-ratified 2026-07-15, bead kernel-of-truth-fh4j). Every check here
# fails closed with a named ERR_* code — an unreadable/ambiguous/drifted rows
# declaration can never silently degrade to the record-line stdin path (that
# silent degradation IS the defect this convention removes: the pinned
# row-consuming analysis would compute over n=0 and emit a spurious
# INSTRUMENT-INVALID).
ROWS_ROLE = "rows"
SIDECAR_ROLE = "sidecar"


def rows_artifact_entry(rec):
    """The record's single role:"rows" artifacts entry, or None (not row-heavy).

    More than one marked entry is unintelligible — which file carries THE
    per-item rows the frozen analysis is defined on? — and refuses
    (ERR_P2_ROWS_AMBIGUOUS) rather than guessing or concatenating.
    """
    entries = [a for a in (rec.get("artifacts") or [])
               if isinstance(a, dict) and a.get("role") == ROWS_ROLE]
    if not entries:
        return None
    if len(entries) > 1:
        raise kc.KotError("ERR_P2_ROWS_AMBIGUOUS",
                          "run record seq %s carries %d role:\"rows\" artifacts entries; the D10 "
                          "convention admits exactly one per record" % (rec.get("seq"), len(entries)))
    return entries[0]


def sidecar_artifact_entry(rec):
    """The record's single role:"sidecar" artifacts entry, or None.

    D10-PAIRED convention (F1-K seam fix, 2026-07-16): an analysis whose
    frozen input contract is (per-item rows + run sidecar) TOGETHER marks
    BOTH on the same run record; step 5a then verifies both pins and feeds
    the RECORD LINE instead of expanding the rows (a bare expansion would
    strand the sidecar and the pinned analysis would reject raw rows).
    More than one marked entry is unintelligible and refuses, exactly like
    the rows marker.
    """
    entries = [a for a in (rec.get("artifacts") or [])
               if isinstance(a, dict) and a.get("role") == SIDECAR_ROLE]
    if not entries:
        return None
    if len(entries) > 1:
        raise kc.KotError("ERR_P2_SIDECAR_AMBIGUOUS",
                          "run record seq %s carries %d role:\"sidecar\" artifacts entries; the "
                          "D10-paired convention admits exactly one per record"
                          % (rec.get("seq"), len(entries)))
    return entries[0]


def _refuse_nonstandard_constant(name):
    """json.loads parse_constant hook: NaN/Infinity/-Infinity are NOT JSON
    (RFC 8259 section 6) — Python's default acceptance is a liberal extension
    the pinned analyses must never receive (a NaN row silently poisons every
    aggregate it touches). Cross-vendor review 2026-07-15, robustness defect 3."""
    raise ValueError("non-standard JSON constant %s" % name)


def _finite_float(s):
    """json.loads parse_float hook: a numeric literal that overflows to an
    infinity (e.g. 1e999) is non-finite by the back door — refuse it exactly
    like the spelled-out constants (same review defect 3, fail closed)."""
    v = float(s)
    if not math.isfinite(v):
        raise ValueError("numeric literal %s is non-finite" % s)
    return v


def load_rows_payload(root, rec, entry):
    """Load + fail-closed-verify a row-heavy record's pinned rows JSONL.

    Returns (payload_bytes, n_rows): the file's exact bytes (newline-
    terminated) ready for the analysis stdin, and the parsed row count for
    the verdict object's inputs.rows_expanded disclosure. The sha256 is
    re-verified against the chained log's artifacts pin at THIS consumption
    time (the same at-consumption discipline as the analysis-script pin and
    the D9 reuse checks); every line must parse as a STRICT JSON OBJECT —
    RFC 8259 JSON only (NaN/Infinity/-Infinity and overflow-to-infinity
    literals refused via the two hooks above) and a top-level object, never
    a scalar or array (a bare-scalar/array line is not a row of the frozen
    analysis's input contract and would be consumed as one) — so a
    truncated, corrupted, or nonstandard rows file can never feed a partial
    or poisoned row set to the analysis (ERR_P2_ROWS_MALFORMED).
    """
    seq = rec.get("seq")
    path = os.path.join(root, entry["path"])
    if not os.path.isfile(path):
        raise kc.KotError("ERR_P2_ROWS_MISSING",
                          "run record seq %s: pinned rows file %s does not exist" % (seq, entry["path"]))
    with open(path, "rb") as f:
        data = f.read()
    got = kc.sha256_hex(data)
    if got != entry["sha256"]:
        raise kc.KotError("ERR_P2_ROWS_DRIFT",
                          "run record seq %s: rows file %s sha256 %s != pinned %s — no verdict is "
                          "producible from drifted rows" % (seq, entry["path"], got, entry["sha256"]))
    n_rows = 0
    for i, line in enumerate(data.split(b"\n")):
        if not line.strip():
            continue
        try:
            # json.JSONDecodeError is a ValueError subclass, so the two
            # strictness hooks' refusals land in the same fail-closed branch.
            row = json.loads(line.decode("utf-8"),
                             parse_constant=_refuse_nonstandard_constant,
                             parse_float=_finite_float)
        except (ValueError, UnicodeDecodeError) as e:
            raise kc.KotError("ERR_P2_ROWS_MALFORMED",
                              "run record seq %s: rows file %s line %d is not strict JSON (%s)"
                              % (seq, entry["path"], i, e))
        if not isinstance(row, dict):
            raise kc.KotError("ERR_P2_ROWS_MALFORMED",
                              "run record seq %s: rows file %s line %d is a top-level %s, not the "
                              "JSON OBJECT the row contract requires"
                              % (seq, entry["path"], i, type(row).__name__))
        n_rows += 1
    if n_rows == 0:
        raise kc.KotError("ERR_P2_ROWS_MISSING",
                          "run record seq %s: rows file %s contains no rows" % (seq, entry["path"]))
    if not data.endswith(b"\n"):
        data += b"\n"
    return data, n_rows


def verify_sidecar_pin(root, rec, entry):
    """Fail-closed verification of a paired record's pinned sidecar JSON.

    Same at-consumption discipline as load_rows_payload: existence
    (ERR_P2_SIDECAR_MISSING), sha256 against the chained log's pin
    (ERR_P2_SIDECAR_DRIFT — no verdict is producible from a drifted
    sidecar), and a strict RFC 8259 parse to a top-level JSON OBJECT via
    the same two non-finite-refusing hooks (ERR_P2_SIDECAR_MALFORMED).
    The pinned analysis re-verifies the same sha before reading a byte —
    two independent enforcements of one pin.
    """
    seq = rec.get("seq")
    path = os.path.join(root, entry["path"])
    if not os.path.isfile(path):
        raise kc.KotError("ERR_P2_SIDECAR_MISSING",
                          "run record seq %s: pinned sidecar file %s does not exist"
                          % (seq, entry["path"]))
    with open(path, "rb") as f:
        data = f.read()
    got = kc.sha256_hex(data)
    if got != entry["sha256"]:
        raise kc.KotError("ERR_P2_SIDECAR_DRIFT",
                          "run record seq %s: sidecar file %s sha256 %s != pinned %s — no verdict "
                          "is producible from a drifted sidecar" % (seq, entry["path"], got, entry["sha256"]))
    try:
        side = json.loads(data.decode("utf-8"),
                          parse_constant=_refuse_nonstandard_constant,
                          parse_float=_finite_float)
    except (ValueError, UnicodeDecodeError) as e:
        raise kc.KotError("ERR_P2_SIDECAR_MALFORMED",
                          "run record seq %s: sidecar file %s is not strict JSON (%s)"
                          % (seq, entry["path"], e))
    if not isinstance(side, dict):
        raise kc.KotError("ERR_P2_SIDECAR_MALFORMED",
                          "run record seq %s: sidecar file %s is a top-level %s, not the JSON "
                          "OBJECT the sidecar contract requires"
                          % (seq, entry["path"], type(side).__name__))


def confirmed_audit(root, exp_id, runner_ids):
    """Return the path of a CONFIRMED audit by a non-runner identity, or None."""
    for path in sorted(glob.glob(os.path.join(root, "registry", "audits", exp_id, "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            audit = json.load(f)
        if audit.get("outcome") != "CONFIRMED":
            continue
        auditor = audit.get("auditor")
        if auditor in runner_ids:
            raise kc.KotError("ERR_P2_SELF_AUDIT",
                              "%s: auditor %r also appears as a runner in the eligible log" % (path, auditor))
        return os.path.relpath(path, root)
    return None


def main():
    ap = argparse.ArgumentParser(description="Compute an experiment verdict purely from frozen record + log.")
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--agent-id", required=True, help="pseudonym stamped on the unblind log line")
    ap.add_argument("--root", default=None)
    ap.add_argument("--computed-at", default=None, help="UTC timestamp override (byte-determinism/tests)")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    exp_id = args.experiment
    try:
        run(root, exp_id, args.agent_id, args.computed_at)
    except kc.KotError as e:
        fail(e.code, str(e).split(": ", 1)[1])
    except FileNotFoundError as e:
        fail("ERR_P2_IO", str(e))


def run(root, exp_id, agent_id, computed_at):
    kc.require_pseudonym(agent_id, "--agent-id")

    # Step 1 — frozen record integrity.
    rec_path = os.path.join(root, "registry", "experiments", "%s.json" % exp_id)
    index_path = os.path.join(root, "registry", "frozen-index.json")
    with open(rec_path, "r", encoding="utf-8") as f:
        record = json.load(f)
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    if exp_id not in index:
        raise kc.KotError("ERR_P2_NOT_FROZEN", "%s absent from frozen-index.json" % exp_id)
    frozen_sha = index[exp_id]
    if kc.frozen_hash(record) != frozen_sha or record.get("frozen_sha256") != frozen_sha:
        raise kc.KotError("ERR_P2_FROZEN_DRIFT",
                          "%s: frozen record bytes drifted from frozen-index — no verdict is producible" % exp_id)

    # Step 2 — amendment overlay (fail closed, never silently skipped). The
    # chain-verified log is read first: it is the RT-5 cutoff witness. The
    # overlay never touches the frozen file; `record` stays the frozen anchor
    # (prereg_hash eligibility is checked against frozen_sha), `effective` is
    # what readout runs against.
    log_path = os.path.join(root, "results-log", "%s.jsonl" % exp_id)
    records, raw_lines = kc.read_log(log_path)
    effective, amendments_applied, amended_sha = apply_amendment_overlay(root, exp_id, record, records)

    # Step 3 — eligibility.
    eligible, excluded = select_eligible(records, frozen_sha, effective["design"])
    tail_sha = kc.log_tail_sha256(raw_lines)
    runner_ids = {r["runner"] for r in eligible}

    # Step 3b — D9 reused-row eligibility (resource-optimization-plan.md §3
    # revision-1). Reused producer rows enter the analysis ONLY when ALL hold:
    #   - the frozen (effective) record is kot-reg/2 with a reused_from block
    #     (an in-log reuse witness without a frozen declaration is refused);
    #   - the ruling is maintainer-ratified (kc.check_record_reuse enforces);
    #   - every RC-1..RC-8 machine check re-verifies at consumption time,
    #     including RC-2 identity with placeholders now FILLED (no
    #     indeterminate pins may license consumption);
    #   - an in-chain RC-6 witness (event:"reuse") restates the exact verified
    #     row set {seqs, row_hashes} for each block.
    # Reused rows NEVER substitute for fresh evidence: the completeness gate
    # below still requires >=1 fresh eligible run row.
    reuse_witnesses = [r for r in records if r.get("event") == "reuse"]
    reused_rows, reused_summary = [], []
    if reuse_witnesses and not (effective.get("reused_from") or []):
        raise kc.KotError("ERR_P2_REUSE_UNDECLARED",
                          "log carries %d reuse witness line(s) but the frozen record declares no "
                          "reused_from block" % len(reuse_witnesses))
    if effective.get("reused_from") and eligible:
        for res in kc.check_record_reuse(effective, root, mode="verdict"):
            block, rows, seqs = res["block"], res["rows"], res["seqs"]
            verified = {rec_p["seq"]: kc.sha256_hex(raw_p) for rec_p, raw_p in rows}
            witness_ok = False
            for w in reuse_witnesses:
                wr = w.get("reuse") or {}
                if (wr.get("producer") == block["producer"]
                        and wr.get("producer_frozen_sha256") == block["producer_frozen_sha256"]
                        and dict(zip(wr.get("seqs", []), wr.get("row_hashes", []))) == verified):
                    witness_ok = True
                    break
            if not witness_ok:
                raise kc.KotError("ERR_P2_REUSE_NO_WITNESS",
                                  "no event:\"reuse\" line in the consumer log restates the verified "
                                  "row set for producer %s (RC-6 in-chain witness; append it via "
                                  "log-append before the verdict)" % block["producer"])
            for rec_p, raw_p in rows:
                aug = dict(rec_p)
                aug["reuse_provenance"] = {
                    "producer": block["producer"],
                    "producer_frozen_sha256": block["producer_frozen_sha256"],
                    "row_sha256": verified[rec_p["seq"]],
                    "role": block["role"],
                }
                reused_rows.append(aug)
            reused_summary.append({
                "producer": block["producer"],
                "producer_frozen_sha256": block["producer_frozen_sha256"],
                "role": block["role"],
                "seqs": seqs,
                "rows_sha256": kc.canonical_sha256([verified[s] for s in seqs]),
            })

    verdict = None
    fired_index = None
    fired_rule = None
    analysis = None
    analysis_output_sha = None
    # Ops amendments cannot touch /pins/analysis_script, so this pin is
    # byte-identical between `record` and `effective`; read it from the
    # effective record for uniformity.
    script_sha = effective["pins"]["analysis_script"]["sha256"]
    endpoint_results = []
    coverage = None
    rows_expanded = []
    paired_verified = []

    if not eligible:
        # Step 4 — completeness gate (minimal form).
        verdict = "INCOMPLETE-DATA"
    else:
        # Step 5 — pinned analysis script over eligible records only.
        script_path = os.path.join(root, effective["pins"]["analysis_script"]["path"])
        got = file_sha256(script_path)
        if got != script_sha:
            raise kc.KotError("ERR_P2_FROZEN_DRIFT",
                              "pinned analysis script %s sha256 %s != frozen pin %s"
                              % (effective["pins"]["analysis_script"]["path"], got, script_sha))
        # Step 5a (D10): assemble stdin in eligible-log order — a row-heavy
        # record (exactly one role:"rows" artifacts entry) contributes its
        # sha-re-verified per-item rows IN PLACE OF its record line; every
        # other record contributes its canonical record line, byte-identical
        # to the pre-D10 payload. Reused rows (verified above) follow the
        # fresh eligible rows, each carrying reuse_provenance so the pinned
        # analysis can distinguish fresh from reused (and apply the frozen
        # selection-adjusted inference where RC-8 requires it). Reused rows
        # are ALWAYS record lines: a role:"rows" marker on a PRODUCER row has
        # no ratified consumption semantics (the D9 witness restates record
        # row hashes, not rows-file bytes), so it refuses rather than feeding
        # the record line silently — the exact degradation D10 removes.
        #
        # DUP GUARD (cross-vendor review 2026-07-15, robustness defect 1): a
        # rows artifact may back AT MOST ONE eligible run's expansion. Two
        # ELIGIBLE marked records referencing the same rows file — same
        # pinned sha256 (the content identity: a byte-identical copy under a
        # second path is the same evidence) or same path — would place the
        # SAME per-item rows on stdin twice: inflated n / precision that
        # could FORCE a PASS while every sha check verifies. Fail closed
        # (ERR_P2_ROWS_DUP). Only ELIGIBLE marked records count: a
        # superseded or excluded duplicate is lawful (its rows never reach
        # stdin), an UNMARKED record citing the same file as a plain
        # artifact is lawful (it contributes its record line, no expansion),
        # and script-baked pinned rows paths (rules-1-c) are invisible here
        # — they are not D10 rows-artifacts at all.
        # D10-PAIRED extension (F1-K seam fix, 2026-07-16): a record marking
        # BOTH role:"rows" AND role:"sidecar" declares the paired input
        # contract — its analysis consumes (rows + sidecar) via the record
        # line's pins, so step 5a verifies BOTH artifacts fail-closed here
        # and contributes the RECORD LINE (an expansion would strand the
        # sidecar; the pinned analysis re-verifies both pins again). A
        # sidecar marker without its rows partner is unintelligible
        # (ERR_P2_SIDECAR_ORPHAN). Rows-only and unmarked records keep
        # their pre-existing behaviour byte-identically, and the
        # ERR_P2_ROWS_DUP guard covers paired rows entries unchanged.
        marked = [(r, rows_artifact_entry(r), sidecar_artifact_entry(r))
                  for r in eligible]
        seen_rows = {}
        for r, entry, _side in marked:
            if entry is None:
                continue
            for dim in ("sha256", "path"):
                key = (dim, entry[dim])
                if key in seen_rows:
                    raise kc.KotError(
                        "ERR_P2_ROWS_DUP",
                        "run records seq %s and seq %s both declare the same rows artifact "
                        "(%s %s) for expansion — a rows artifact may back at most one "
                        "eligible run's expansion; duplicated rows would inflate n and "
                        "could force a verdict" % (seen_rows[key], r.get("seq"), dim, entry[dim]))
                seen_rows[key] = r.get("seq")
        payload = []
        for r, entry, side_entry in marked:
            if entry is None and side_entry is None:
                payload.append((kc.canonical_dumps(r) + "\n").encode("utf-8"))
            elif entry is not None and side_entry is not None:
                _rows_bytes, n_rows = load_rows_payload(root, r, entry)
                verify_sidecar_pin(root, r, side_entry)
                payload.append((kc.canonical_dumps(r) + "\n").encode("utf-8"))
                paired_verified.append({
                    "seq": r["seq"],
                    "rows": {"path": entry["path"],
                             "sha256": entry["sha256"], "rows": n_rows},
                    "sidecar": {"path": side_entry["path"],
                                "sha256": side_entry["sha256"]}})
            elif entry is not None:
                rows_bytes, n_rows = load_rows_payload(root, r, entry)
                payload.append(rows_bytes)
                rows_expanded.append({"seq": r["seq"], "path": entry["path"],
                                      "sha256": entry["sha256"], "rows": n_rows})
            else:
                raise kc.KotError(
                    "ERR_P2_SIDECAR_ORPHAN",
                    "run record seq %s carries a role:\"sidecar\" artifacts entry without its "
                    "role:\"rows\" partner — the D10-paired convention requires both; refusing "
                    "rather than guessing which stdin shape the frozen analysis expects"
                    % r.get("seq"))
        for r in reused_rows:
            if rows_artifact_entry(r) is not None or sidecar_artifact_entry(r) is not None:
                raise kc.KotError("ERR_P2_ROWS_REUSE",
                                  "reused producer row seq %s (producer %s) carries a role:\"rows\" "
                                  "or role:\"sidecar\" artifacts entry — row-heavy/paired reuse has "
                                  "no ratified D9/D10 consumption semantics; extend the convention "
                                  "deliberately"
                                  % (r.get("seq"), r["reuse_provenance"]["producer"]))
            payload.append((kc.canonical_dumps(r) + "\n").encode("utf-8"))
        stdin_payload = b"".join(payload)
        proc = subprocess.run(
            ["nice", "-n", "10", sys.executable, script_path],
            input=stdin_payload, capture_output=True, cwd=root,
        )
        if proc.returncode != 0:
            raise kc.KotError("ERR_P2_ANALYSIS",
                              "pinned analysis script exited %d: %s"
                              % (proc.returncode, proc.stderr.decode("utf-8", "replace")[-2000:]))
        try:
            analysis = json.loads(proc.stdout.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise kc.KotError("ERR_P2_ANALYSIS", "analysis output is not JSON: %s" % e)
        out_dir = os.path.join(root, "reports", "auto", exp_id)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "analysis-output.json")
        kc.write_canonical_json(out_path, analysis)
        analysis_output_sha = file_sha256(out_path)

        # Step 6 — unblind line, first time only, via the single write path.
        if not any(r.get("event") == "unblind" for r in records):
            unblind = {"event": "unblind", "prereg_hash": frozen_sha}
            p = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "log-append.py"),
                 "--experiment", exp_id, "--agent-id", agent_id, "--record", "-", "--root", root],
                input=kc.canonical_dumps(unblind).encode("utf-8"), capture_output=True,
            )
            if p.returncode != 0:
                raise kc.KotError("ERR_P2_CHAIN", "could not write unblind line: %s"
                                  % p.stderr.decode("utf-8", "replace"))
            records, raw_lines = kc.read_log(log_path)
            tail_sha = kc.log_tail_sha256(raw_lines)

        # G-7 (scoped): coverage is required only when the frozen record declares it.
        # coverage_requirement.source names WHERE the coverage block comes from
        # (P2 §2 G-7: "absent from eligible runs' metrics or the verdict object"):
        #   - "self" / this experiment's id: the experiment measures its own
        #     coverage and every eligible run carries metrics.coverage (m0b).
        #   - any other experiment id: the published coverage from that
        #     experiment's verdict object is RESTATED here (P3 m0b.close:
        #     "publish coverage + rung; restated in every later verdict").
        #     Fail closed unless that verdict exists, carries a coverage
        #     block, and is itself audit-CONFIRMED (G-6 — an unaudited
        #     coverage number must not silently license downstream verdicts).
        if "coverage_requirement" in effective:
            cov_source = effective["coverage_requirement"].get("source", "self")
            if cov_source in ("self", exp_id):
                coverage = eligible[-1].get("metrics", {}).get("coverage")
                if not coverage:
                    raise kc.KotError("ERR_P2_NO_COVERAGE",
                                      "coverage_requirement declared but eligible runs carry no metrics.coverage block")
            else:
                src_path = os.path.join(root, "registry", "verdicts", "%s.json" % cov_source)
                if not os.path.exists(src_path):
                    raise kc.KotError("ERR_P2_NO_COVERAGE",
                                      "coverage_requirement.source=%r but registry/verdicts/%s.json does not exist"
                                      % (cov_source, cov_source))
                with open(src_path, encoding="utf-8") as f:
                    src_verdict = json.load(f)
                coverage = src_verdict.get("coverage")
                if not coverage:
                    raise kc.KotError("ERR_P2_NO_COVERAGE",
                                      "coverage_requirement.source=%r but that verdict object carries no coverage block"
                                      % cov_source)
                if src_verdict.get("audit", {}).get("state") != "CONFIRMED":
                    raise kc.KotError("ERR_P2_NO_COVERAGE",
                                      "coverage_requirement.source=%r but that verdict's audit state is %r, not CONFIRMED"
                                      % (cov_source, src_verdict.get("audit", {}).get("state")))

        for ep in effective["endpoints"]:
            v = kc.resolve_pointer(analysis, ep["metric"])
            endpoint_results.append({
                "id": ep["id"], "role": ep["role"], "metric": ep["metric"],
                "value": None if v is kc._MISSING else v,
            })

        # Step 7 — frozen verdict rules, first match wins; fail closed on gaps.
        try:
            for i, rule in enumerate(effective["verdict_rules"]):
                if kc.eval_expr(rule["when"], analysis):
                    verdict = rule["verdict"]
                    fired_index = i
                    fired_rule = rule["when"]
                    break
        except kc.MissingMetric as e:
            verdict = "INCOMPLETE-DATA"
            fired_rule = {"missing_metric": e.pointer}
        if verdict is None:
            # unreachable when the freeze-time catch-all lint held; fail closed anyway
            verdict = "INCOMPLETE-DATA"

    # Step 8 — audit gate on PASS.
    audit_state = {"state": "N/A", "path": None}
    if verdict == "PASS":
        audit_path = confirmed_audit(root, exp_id, runner_ids)
        if audit_path is None:
            verdict = "PASS-PENDING-AUDIT"
            audit_state = {"state": "PENDING", "path": None}
        else:
            audit_state = {"state": "CONFIRMED", "path": audit_path}

    rungs_fresh = sorted({str(r["config"]["rung"]) for r in eligible
                          if isinstance(r.get("config"), dict) and "rung" in r["config"]})
    rungs_reused = sorted({str(r["config"]["rung"]) for r in reused_rows
                           if isinstance(r.get("config"), dict) and "rung" in r["config"]})
    rungs = sorted(set(rungs_fresh) | set(rungs_reused))
    # Per-record min-rule licensing (a5-llm REFUTE remediation) — see
    # scale_language_license's docstring for the three caps and their sources.
    license_ = scale_language_license(effective["design"], rungs, analysis)

    verdict_obj = {
        "schema_version": "kot-verdict/1",
        "experiment": exp_id,
        "hypotheses": effective["hypotheses"],
        "verdict": verdict,
        "fired_rule_index": fired_index,
        "fired_rule": fired_rule,
        "computed_at": computed_at or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": {
            "frozen_sha256": frozen_sha,
            "amendments_applied": amendments_applied,
            "amended_record_sha256": amended_sha,
            "log_tail_sha256": tail_sha,
            "eligible_runs": len(eligible),
            "excluded_runs": excluded,
            "analysis_output_sha256": analysis_output_sha,
            "analysis_script_sha256": script_sha,
        },
        "endpoint_results": endpoint_results,
        "coverage": coverage,
        "rungs_measured": rungs,
        "scale_language_licensed": license_,
        # (fields below added only for reuse-consuming records, so pre-D9
        # verdict objects keep their exact shape)
        "kill_criterion_verbatim": effective["kill_criterion_verbatim"],
        "extrapolation_envelope_verbatim": effective["extrapolation_envelope_verbatim"],
        "audit": audit_state,
    }
    if reused_summary:
        # Transparency for the auditor (RC-6): what was consumed, from where,
        # and which rungs the record measured fresh vs inherited via reuse —
        # any scale-language license that leans on reused rungs is visible.
        verdict_obj["inputs"]["reused"] = reused_summary
        verdict_obj["rungs_fresh"] = rungs_fresh
        verdict_obj["rungs_reused_only"] = sorted(set(rungs_reused) - set(rungs_fresh))
    if rows_expanded:
        # D10 transparency (step 5a): which eligible records' rows-artifacts
        # were expanded onto the analysis stdin, with the re-verified pins and
        # parsed row counts. Added only when the row-heavy path was taken, so
        # every pre-D10 verdict object keeps its exact byte shape.
        verdict_obj["inputs"]["rows_expanded"] = rows_expanded
    if paired_verified:
        # D10-paired transparency (F1-K seam fix): which eligible records'
        # rows+sidecar artifact PAIRS were verified at consumption time (the
        # record line itself fed the analysis, which re-verified the same
        # pins). Added only when the paired path was taken, so every earlier
        # verdict object keeps its exact byte shape.
        verdict_obj["inputs"]["paired_artifacts_verified"] = paired_verified

    # RT-14 applies to verdict objects too (they are re-hashed by audits).
    kc.check_identity_fields(verdict_obj)
    kc.require_no_account_strings(kc.canonical_bytes(verdict_obj), "verdict object")

    verdict_dir = os.path.join(root, "registry", "verdicts")
    os.makedirs(verdict_dir, exist_ok=True)
    kc.write_canonical_json(os.path.join(verdict_dir, "%s.json" % exp_id), verdict_obj)
    print(json.dumps(verdict_obj, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
