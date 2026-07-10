#!/usr/bin/env python3
"""verdict-gen-dts — SCOPED, corpus-direct verdict driver for truthstyle-2x2.

    python3 tools/registry/verdict-gen-dts.py --experiment truthstyle-2x2
        --agent-id coordinator-1 [--root <repo>] [--computed-at 2026-...Z]

Ratified by registry/corrections/truthstyle-2x2/2-verdict-path-reconciliation.json
(execution-path-ruling, seq 2; ASM-0362). The generic verdict spine
tools/registry/verdict-gen.py invokes the pinned analysis with the eligible log
rows on stdin and no argv, but the FROZEN pinned analysis
analysis/truthstyle_2x2.py is by its own frozen design a PURE FUNCTION of the two
pinned corpora (--items data/d-ts/items.jsonl, --labels required; stdin ignored;
exits 1 with ERR_TS_NO_LABELS), so the generic spine fails with ERR_P2_ANALYSIS.

This driver IMPORTS the shared spine (verdict-gen.py internals + kot_common) so
NO guardrail is reimplemented, and differs from verdict-gen.run() in EXACTLY ONE
step: how the sha-verified pinned analysis is invoked (Step 5). The shared
verdict-gen.py is NOT modified. Every other step — frozen-record integrity,
amendment overlay, chain-verified log read + eligibility + completeness gate,
first-time unblind via log-append, coverage gate, frozen verdict_rules over
kot_common.eval_expr, PASS -> PASS-PENDING-AUDIT audit gate, kot-verdict/1
RT-14-linting and canonical write — is the imported spine code path, byte-
identical in behaviour. The emitted verdict object additionally self-declares
the deviation via inputs.analysis_invocation.
"""
import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kot_common as kc  # noqa: E402

# The shared spine's filename carries a hyphen; load it as a module so every
# guardrail (apply_amendment_overlay, select_eligible, confirmed_audit,
# file_sha256, DESIGN_SCOPE_PREFIXES, ...) is the SAME code, not a copy.
_spec = importlib.util.spec_from_file_location(
    "verdict_gen_spine", os.path.join(HERE, "verdict-gen.py"))
vg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vg)

ONLY_EXPERIMENT = "truthstyle-2x2"
DRIVER_REL = "tools/registry/verdict-gen-dts.py"
DRIVER_PATH = os.path.abspath(__file__)
ANALYSIS_ARGV = ["--items", "data/d-ts/items.jsonl",
                 "--labels", "data/d-ts-labels/labels.jsonl"]


def main():
    ap = argparse.ArgumentParser(
        description="Compute the truthstyle-2x2 verdict via the scoped corpus-direct driver.")
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--agent-id", required=True, help="pseudonym stamped on the unblind log line")
    ap.add_argument("--root", default=None)
    ap.add_argument("--computed-at", default=None, help="UTC timestamp override (byte-determinism/tests)")
    args = ap.parse_args()

    if args.experiment != ONLY_EXPERIMENT:
        vg.fail("ERR_P2_DTS_ONLY",
                "verdict-gen-dts is scoped to %s only; refusing %r (no silent generalization — "
                "the generic spine tools/registry/verdict-gen.py handles every other record)"
                % (ONLY_EXPERIMENT, args.experiment))

    root = args.root or os.path.dirname(os.path.dirname(HERE))
    try:
        run(root, args.experiment, args.agent_id, args.computed_at)
    except kc.KotError as e:
        vg.fail(e.code, str(e).split(": ", 1)[1])
    except FileNotFoundError as e:
        vg.fail("ERR_P2_IO", str(e))


def run(root, exp_id, agent_id, computed_at):
    kc.require_pseudonym(agent_id, "--agent-id")

    # Step 1 (imported behaviour) — frozen record integrity.
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

    # Step 2 (imported) — amendment overlay via the shared spine. The post-
    # adjudication ops amendment seq 4 (4-pin-d-ts-labels.json) MUST have landed:
    # it replaces the corpus_hashes.d-ts-labels PINNED-AT-INPUTS placeholder with
    # the kot-corpus-hash/1 digest of data/d-ts-labels/. Fail closed if the
    # placeholder is still unfilled after overlay.
    log_path = os.path.join(root, "results-log", "%s.jsonl" % exp_id)
    records, raw_lines = kc.read_log(log_path)
    effective, amendments_applied, amended_sha = vg.apply_amendment_overlay(root, exp_id, record, records)

    d_ts_labels_pin = effective["pins"]["corpus_hashes"].get("d-ts-labels")
    if not isinstance(d_ts_labels_pin, str) or d_ts_labels_pin.startswith(kc.PINNED_AT_INPUTS_PREFIX):
        raise kc.KotError(
            "ERR_P2_CORPUS_PIN",
            "corpus_hashes.d-ts-labels is still the PINNED-AT-INPUTS placeholder after amendment "
            "overlay (current=%r) — the post-adjudication ops amendment seq 4 must land before any "
            "readout (correction seq 2, step 2)" % d_ts_labels_pin)

    # Steps 3-4 (imported) — chain-verified log read (done), eligibility, and the
    # completeness gate. The eligible rows GATE the readout; they are NOT piped to
    # the analysis, which is corpus-direct by frozen design. select_eligible
    # enforces phase==final, exit==ok, not superseded, prereg_hash == frozen sha,
    # and config.seed in design.seeds ({20260710}).
    eligible, excluded = vg.select_eligible(records, frozen_sha, effective["design"])
    tail_sha = kc.log_tail_sha256(raw_lines)
    runner_ids = {r["runner"] for r in eligible}

    # This record is kot-reg/1 with no reused_from block; D9 reuse can never
    # apply. Mirror the spine's undeclared-witness refusal exactly (a reuse
    # witness without a frozen declaration is unlawful), then carry no reused
    # rows — byte-identical behaviour to verdict-gen for a non-reuse record.
    reuse_witnesses = [r for r in records if r.get("event") == "reuse"]
    if reuse_witnesses and not (effective.get("reused_from") or []):
        raise kc.KotError("ERR_P2_REUSE_UNDECLARED",
                          "log carries %d reuse witness line(s) but the frozen record declares no "
                          "reused_from block" % len(reuse_witnesses))

    verdict = None
    fired_index = None
    fired_rule = None
    analysis_output_sha = None
    # Ops amendments cannot touch /pins/analysis_script, so this pin is
    # byte-identical between `record` and `effective`.
    script_sha = effective["pins"]["analysis_script"]["sha256"]
    endpoint_results = []
    coverage = None
    analysis_invocation = {
        "driver": DRIVER_REL,
        "driver_sha256": vg.file_sha256(DRIVER_PATH),
        "argv": list(ANALYSIS_ARGV),
        "corpus_digests_verified": None,
    }

    if not eligible:
        # Step 4 — completeness gate (minimal form). At least one eligible
        # phase:final exit:ok row is required before any readout.
        verdict = "INCOMPLETE-DATA"
    else:
        # ---- Step 5: THE ONE DIVERGENCE from verdict-gen.run() ----
        # (a) re-verify the pinned analysis sha at execution time.
        script_path = os.path.join(root, effective["pins"]["analysis_script"]["path"])
        got = vg.file_sha256(script_path)
        if got != script_sha:
            raise kc.KotError("ERR_P2_FROZEN_DRIFT",
                              "pinned analysis script %s sha256 %s != frozen pin %s"
                              % (effective["pins"]["analysis_script"]["path"], got, script_sha))
        # (b) ADDITIONALLY re-verify BOTH corpus digests at readout time — the
        # analysis is a pure function of these two pinned corpora, so the driver
        # digest-verifies them against the (amended) effective record. STRICTER
        # than the generic spine, which never re-verifies corpora at readout.
        d_ts_want = effective["pins"]["corpus_hashes"]["d-ts"]
        d_ts_got = kc.corpus_hash(root, "d-ts")
        if d_ts_got != d_ts_want:
            raise kc.KotError("ERR_P2_CORPUS_PIN",
                              "data/d-ts/ digest %s != effective corpus_hashes.d-ts %s"
                              % (d_ts_got, d_ts_want))
        d_ts_labels_got = kc.corpus_hash(root, "d-ts-labels")
        if d_ts_labels_got != d_ts_labels_pin:
            raise kc.KotError("ERR_P2_CORPUS_PIN",
                              "data/d-ts-labels/ digest %s != amended corpus_hashes.d-ts-labels %s"
                              % (d_ts_labels_got, d_ts_labels_pin))
        analysis_invocation["corpus_digests_verified"] = {
            "d-ts": d_ts_got, "d-ts-labels": d_ts_labels_got}
        # (c) run the frozen analysis corpus-direct, from repo root, EMPTY stdin.
        proc = subprocess.run(
            ["nice", "-n", "10", sys.executable, script_path] + ANALYSIS_ARGV,
            input=b"", capture_output=True, cwd=root,
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
        analysis_output_sha = vg.file_sha256(out_path)
        # ---- end Step 5 divergence ----

        # Step 6 (imported) — unblind line, first time only, via the single write path.
        if not any(r.get("event") == "unblind" for r in records):
            unblind = {"event": "unblind", "prereg_hash": frozen_sha}
            p = subprocess.run(
                [sys.executable, os.path.join(HERE, "log-append.py"),
                 "--experiment", exp_id, "--agent-id", agent_id, "--record", "-", "--root", root],
                input=kc.canonical_dumps(unblind).encode("utf-8"), capture_output=True,
            )
            if p.returncode != 0:
                raise kc.KotError("ERR_P2_CHAIN", "could not write unblind line: %s"
                                  % p.stderr.decode("utf-8", "replace"))
            records, raw_lines = kc.read_log(log_path)
            tail_sha = kc.log_tail_sha256(raw_lines)

        # Coverage gate (imported, G-7 scoped) — the frozen record declares
        # coverage_requirement.source = "m0b"; restate that experiment's
        # published, audit-CONFIRMED coverage. Fail closed otherwise.
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

        # Step 7 (imported) — frozen verdict rules, first match wins; fail closed.
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
            verdict = "INCOMPLETE-DATA"

    # Step 8 (imported) — audit gate on PASS.
    audit_state = {"state": "N/A", "path": None}
    if verdict == "PASS":
        audit_path = vg.confirmed_audit(root, exp_id, runner_ids)
        if audit_path is None:
            verdict = "PASS-PENDING-AUDIT"
            audit_state = {"state": "PENDING", "path": None}
        else:
            audit_state = {"state": "CONFIRMED", "path": audit_path}

    rungs_fresh = sorted({str(r["config"]["rung"]) for r in eligible
                          if isinstance(r.get("config"), dict) and "rung" in r["config"]})
    rungs = sorted(set(rungs_fresh))
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
            # Step 5 divergence self-declared to the auditor (correction seq 2).
            "analysis_invocation": analysis_invocation,
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
