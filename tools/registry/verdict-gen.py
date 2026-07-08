#!/usr/bin/env python3
"""verdict-gen — the verdict as a pure function of (frozen record, chained log).

    python3 tools/registry/verdict-gen.py --experiment <id> --agent-id coordinator-1
        [--root <repo>] [--computed-at 2026-07-12T18:00:00Z]

Implements P2 §3.1 (minimal spine — the F1-critical path):
  1. Load registry/experiments/<id>.json; recompute the frozen hash; require
     equality with registry/frozen-index.json (ERR_P2_FROZEN_DRIFT — no verdict
     of any kind is producible from a drifted record).
  2. Amendment overlay is NOT implemented in the minimal spine; the presence of
     any registry/amendments/<id>/ record aborts (ERR_P2_BAD_AMENDMENT) rather
     than being silently skipped.
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
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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

    # Step 2 — amendments (fail closed, never silently skipped).
    amendments = sorted(glob.glob(os.path.join(root, "registry", "amendments", exp_id, "*.json")))
    if amendments:
        raise kc.KotError("ERR_P2_BAD_AMENDMENT",
                          "amendment overlay is not implemented in the minimal spine; found: %s"
                          % ", ".join(os.path.relpath(a, root) for a in amendments))

    # Step 3 — chain-verified log + eligibility.
    log_path = os.path.join(root, "results-log", "%s.jsonl" % exp_id)
    records, raw_lines = kc.read_log(log_path)
    eligible, excluded = select_eligible(records, frozen_sha, record["design"])
    tail_sha = kc.log_tail_sha256(raw_lines)
    runner_ids = {r["runner"] for r in eligible}

    verdict = None
    fired_index = None
    fired_rule = None
    analysis_output_sha = None
    script_sha = record["pins"]["analysis_script"]["sha256"]
    endpoint_results = []
    coverage = None

    if not eligible:
        # Step 4 — completeness gate (minimal form).
        verdict = "INCOMPLETE-DATA"
    else:
        # Step 5 — pinned analysis script over eligible records only.
        script_path = os.path.join(root, record["pins"]["analysis_script"]["path"])
        got = file_sha256(script_path)
        if got != script_sha:
            raise kc.KotError("ERR_P2_FROZEN_DRIFT",
                              "pinned analysis script %s sha256 %s != frozen pin %s"
                              % (record["pins"]["analysis_script"]["path"], got, script_sha))
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
        if "coverage_requirement" in record:
            coverage = eligible[-1].get("metrics", {}).get("coverage")
            if not coverage:
                raise kc.KotError("ERR_P2_NO_COVERAGE",
                                  "coverage_requirement declared but eligible runs carry no metrics.coverage block")

        for ep in record["endpoints"]:
            v = kc.resolve_pointer(analysis, ep["metric"])
            endpoint_results.append({
                "id": ep["id"], "role": ep["role"], "metric": ep["metric"],
                "value": None if v is kc._MISSING else v,
            })

        # Step 7 — frozen verdict rules, first match wins; fail closed on gaps.
        try:
            for i, rule in enumerate(record["verdict_rules"]):
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
        "hypotheses": record["hypotheses"],
        "verdict": verdict,
        "fired_rule_index": fired_index,
        "fired_rule": fired_rule,
        "computed_at": computed_at or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": {
            "frozen_sha256": frozen_sha,
            "amendments_applied": [],
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
        "kill_criterion_verbatim": record["kill_criterion_verbatim"],
        "extrapolation_envelope_verbatim": record["extrapolation_envelope_verbatim"],
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
