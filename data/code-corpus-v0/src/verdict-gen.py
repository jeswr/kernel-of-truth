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
  4. Completeness gate (minimal): an empty eligible set => INCOMPLETE-DATA.
  5. Run the pinned analysis script (sha256 re-verified at execution;
     ERR_P2_FROZEN_DRIFT on mismatch) with the eligible records as JSONL on
     stdin; its stdout JSON is written to reports/auto/<id>/analysis-output.json.
     ALL derived statistics live there and nowhere else (G-4).
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
)

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

    # Post-overlay integrity: the effective record must still be a valid
    # kot-reg/1 record and RT-14-clean — an overlay cannot smuggle in what a
    # freeze would have refused.
    schema_path = os.path.join(root, "registry", "schema", "kot-reg-1.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        reg_schema = json.load(f)
    errs = kc.validate_schema(effective, reg_schema)
    if errs:
        raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                          "amended effective record no longer validates against kot-reg/1: %s"
                          % "; ".join(errs[:5]))
    kc.check_identity_fields(effective)
    hashed = {k: v for k, v in effective.items() if k not in ("status", "frozen_sha256")}
    kc.require_no_account_strings(kc.canonical_bytes(hashed), "amended effective record")
    return effective, applied, kc.frozen_hash(effective)


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

    verdict = None
    fired_index = None
    fired_rule = None
    analysis_output_sha = None
    # Ops amendments cannot touch /pins/analysis_script, so this pin is
    # byte-identical between `record` and `effective`; read it from the
    # effective record for uniformity.
    script_sha = effective["pins"]["analysis_script"]["sha256"]
    endpoint_results = []
    coverage = None

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
        stdin_payload = "".join(kc.canonical_dumps(r) + "\n" for r in eligible)
        proc = subprocess.run(
            ["nice", "-n", "10", sys.executable, script_path],
            input=stdin_payload.encode("utf-8"), capture_output=True, cwd=root,
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

    rungs = sorted({str(r["config"]["rung"]) for r in eligible
                    if isinstance(r.get("config"), dict) and "rung" in r["config"]})
    license_ = "none" if len(rungs) < 2 else ("sign-only" if len(rungs) == 2 else "slope")

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
        "kill_criterion_verbatim": effective["kill_criterion_verbatim"],
        "extrapolation_envelope_verbatim": effective["extrapolation_envelope_verbatim"],
        "audit": audit_state,
    }

    # RT-14 applies to verdict objects too (they are re-hashed by audits).
    kc.check_identity_fields(verdict_obj)
    kc.require_no_account_strings(kc.canonical_bytes(verdict_obj), "verdict object")

    verdict_dir = os.path.join(root, "registry", "verdicts")
    os.makedirs(verdict_dir, exist_ok=True)
    kc.write_canonical_json(os.path.join(verdict_dir, "%s.json" % exp_id), verdict_obj)
    print(json.dumps(verdict_obj, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
