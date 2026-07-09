#!/usr/bin/env python3
"""report-gen — S7: the fixed-template markdown auto-report (P2 §3.3).

    python3 tools/registry/report-gen.py --experiment <id> [--root <repo>]

Renders reports/auto/<id>/verdict-<id>.md from EXACTLY three machine inputs:
the frozen registry record, the verdict object (registry/verdicts/<id>.json),
and the chained results-log — plus reports/auto/<id>/analysis-output.json when
verdict-gen produced one. No slot is author-editable; the OUTCOME line is
copied from the verdict object, and the kill criterion + extrapolation
envelope are printed verbatim beside it (P1 §6 anti-overselling guard,
mechanised). The only free-text section is the visually-fenced non-binding
commentary appended from reports/auto/<id>/commentary.md if present.

Fail-closed refusals:
  ERR_P2_REPORT_INPUT   verdict object or frozen record missing/unreadable
  ERR_P2_FROZEN_DRIFT   verdict.inputs.frozen_sha256 != the record's recomputed
                        frozen hash (a report must never render from a record
                        that is not the one the verdict was computed from)
  ERR_P2_REPORT_SLOT    a mandatory slot (verdict, kill criterion, envelope,
                        hypotheses) is empty

Sections, fixed order (P2 §3.3): header pins -> kill criterion (verbatim,
rendered for EVERY verdict incl. PASS) -> OUTCOME + fired rule -> endpoints
(the full pre-declared metric vector, ALL of them) -> coverage disclosure ->
scale/envelope -> eligible & excluded runs -> audit -> deviations/amendments
-> fenced commentary.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

TOOL_VERSION = "report-gen/1"


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def short(h, n=8):
    return (h or "")[:n] if h else "n/a"


def load_json(path, what):
    if not os.path.isfile(path):
        raise kc.KotError("ERR_P2_REPORT_INPUT", "%s missing (%s)" % (what, path))
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise kc.KotError("ERR_P2_REPORT_INPUT", "%s unparseable: %s" % (what, e))


def render(root, exp_id):
    verdict = load_json(os.path.join(root, "registry", "verdicts", "%s.json" % exp_id), "verdict object")
    record = load_json(os.path.join(root, "registry", "experiments", "%s.json" % exp_id), "frozen record")

    frozen_sha = verdict.get("inputs", {}).get("frozen_sha256")
    if not frozen_sha or kc.frozen_hash(record) != frozen_sha:
        raise kc.KotError("ERR_P2_FROZEN_DRIFT",
                          "%s: record's recomputed frozen hash != verdict.inputs.frozen_sha256 — "
                          "the verdict was computed from different frozen bytes" % exp_id)

    # Mandatory slots — refuse to render with any of them empty (P2 §3.3).
    for slot in ("verdict", "kill_criterion_verbatim", "extrapolation_envelope_verbatim", "hypotheses"):
        if not verdict.get(slot):
            raise kc.KotError("ERR_P2_REPORT_SLOT", "mandatory slot %r is empty in the verdict object" % slot)

    analysis_path = os.path.join(root, "reports", "auto", exp_id, "analysis-output.json")
    analysis = load_json(analysis_path, "analysis output") if os.path.isfile(analysis_path) else None

    pins = record.get("pins", {})
    corpus_pins = {k: v for k, v in pins.get("corpus_hashes", {}).items() if k != "_recipe"}
    rule_by_index = record.get("verdict_rules", [])

    L = []
    L.append("# %s verdict — %s" % (exp_id, verdict["verdict"]))
    L.append("")
    L.append("computed: %s | %s | analysis %s" % (
        verdict.get("computed_at", "n/a"), TOOL_VERSION,
        short(verdict["inputs"].get("analysis_script_sha256"))))
    L.append("frozen prereg: %s (frozen %s) | amendments applied: %s" % (
        short(frozen_sha), record.get("frozen_at", "n/a"),
        ", ".join(map(str, verdict["inputs"].get("amendments_applied", []))) or "none"))
    L.append("encoder pin: %s | corpus pins: %s | log tail: %s" % (
        short(pins.get("encoder_hash")),
        ", ".join("%s:%s" % (k, short(v) if isinstance(v, str) and kc.SHA256_RE.match(v)
                             else "(at-inputs)") for k, v in sorted(corpus_pins.items())) or "none",
        short(verdict["inputs"].get("log_tail_sha256"))))
    L.append("")
    L.append("## Pre-registered statement (from the frozen record)")
    L.append("")
    L.append("**Hypotheses:** %s — %s" % (", ".join(verdict["hypotheses"]), record.get("title", "")))
    L.append("prereg doc: %s (sha256 %s)" % (record["prereg_doc"]["path"], short(record["prereg_doc"]["sha256"])))
    L.append("")
    L.append("## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict")
    L.append("")
    L.append("> %s" % verdict["kill_criterion_verbatim"].replace("\n", "\n> "))
    L.append("")
    L.append("## OUTCOME: **%s**" % verdict["verdict"])
    L.append("")
    if verdict.get("fired_rule_index") is not None:
        i = verdict["fired_rule_index"]
        declared = rule_by_index[i]["verdict"] if 0 <= i < len(rule_by_index) else "?"
        L.append("Fired rule %d (declares `%s`): `%s`" % (
            i, declared, kc.canonical_dumps(verdict.get("fired_rule"))))
    elif verdict.get("fired_rule"):
        L.append("No rule fired cleanly; fail-closed detail: `%s`" % kc.canonical_dumps(verdict["fired_rule"]))
    else:
        L.append("No verdict rule was evaluated (completeness gate: %s)." % verdict["verdict"])
    L.append("evaluated over analysis-output.json (sha256 %s)."
             % short(verdict["inputs"].get("analysis_output_sha256")))
    if verdict["verdict"] == "PASS-PENDING-AUDIT":
        L.append("")
        L.append("**Not citable as PASS until the independent cross-vendor re-derivation "
                 "(audit role, P5 R8/R10) confirms.**")
    L.append("")
    L.append("## Endpoints (full pre-declared metric vector — all of them)")
    L.append("")
    L.append("| endpoint | role | metric | value | pre-registered test |")
    L.append("|---|---|---|---|---|")
    ep_results = {e["id"]: e for e in verdict.get("endpoint_results", [])}
    for ep in record.get("endpoints", []):
        res = ep_results.get(ep["id"], {})
        val = res.get("value")
        L.append("| %s | %s | `%s` | %s | %s |" % (
            ep["id"], ep["role"], ep["metric"],
            "—" if val is None else json.dumps(val, sort_keys=True),
            ep["test"].replace("|", "\\|")))
    if analysis is not None:
        L.append("")
        L.append("Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):")
        L.append("")
        L.append("```json")
        L.append(json.dumps(analysis, indent=2, sort_keys=True))
        L.append("```")
    L.append("")
    L.append("## Coverage disclosure (mandatory)")
    L.append("")
    cov = verdict.get("coverage")
    if cov:
        # FULL scope, mechanised (assumption-register.md §6 item 4, ENABLED
        # 2026-07-09): fraction + rung alone read as "natural coverage" — the
        # exact promotion the m0b incident showed. State corpus + kernel
        # instance + the no-extrapolation envelope, from machine inputs only:
        # the source experiment's frozen record supplies the census pins.
        src_id = (cov.get("source_experiment")
                  or record.get("coverage_requirement", {}).get("source") or "self")
        if src_id == "self":
            src_id, src_record = exp_id, record
        else:
            src_record = load_json(os.path.join(root, "registry", "experiments",
                                                "%s.json" % src_id), "coverage source record")
        src_pins = {k: v for k, v in
                    src_record.get("pins", {}).get("corpus_hashes", {}).items()
                    if k != "_recipe"}
        L.append("Kernel-expressibility coverage (M0b): **%s** at rung **%s** — a "
                 "corpus-indexed, rung-indexed, kernel-state-indexed measurement, NOT a "
                 "general (\"natural\") coverage property of the kernel." % (
                     cov.get("fraction", "?"), cov.get("rung", "?")))
        L.append("")
        L.append("Full measured scope: census by experiment `%s` (frozen %s) over exactly "
                 "its pinned inputs — %s (encoder pin %s) — i.e. that one pinned corpus "
                 "against the incomplete kernel instance as pinned at that freeze; coverage "
                 "is re-measured as the kernel grows (coverage-growth curve, P7 RT-11/§10)." % (
                     src_id, src_record.get("frozen_at", "n/a"),
                     ", ".join("%s:%s" % (k, short(v) if isinstance(v, str)
                                          and kc.SHA256_RE.match(v) else "(at-inputs)")
                               for k, v in sorted(src_pins.items())) or "none",
                     short(src_record.get("pins", {}).get("encoder_hash"))))
        L.append("")
        L.append("No-extrapolation envelope on this number (per the %s verdict envelope and "
                 "the assumption register, registry/assumptions.jsonl): it extrapolates to NO "
                 "other corpus, rung, or kernel state. Every claim above is bounded to this "
                 "covered slice, within exactly that scope." % src_id)
    elif "coverage_requirement" in record:
        L.append("DECLARED but ABSENT — coverage_requirement is frozen on this record and no "
                 "coverage block was available (verdict cannot be complete).")
    else:
        L.append("No coverage_requirement is frozen on this record (the correction note on the "
                 "record states why); the M0b NICHE-SCOPE discipline still binds any external "
                 "quotation of this verdict (P1: m0b precedes first external quotation).")
    L.append("")
    L.append("## Scale")
    L.append("")
    L.append("Rungs measured: %s. Scale language licensed: **%s** "
             "(>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing)." % (
                 ", ".join(verdict.get("rungs_measured", [])) or "none",
                 verdict.get("scale_language_licensed", "none")))
    L.append("")
    L.append("### Extrapolation envelope (verbatim — binding on every citation of this verdict)")
    L.append("")
    L.append("> %s" % verdict["extrapolation_envelope_verbatim"].replace("\n", "\n> "))
    L.append("")
    L.append("## Eligible & excluded runs")
    L.append("")
    L.append("%d eligible final run(s)." % verdict["inputs"].get("eligible_runs", 0))
    excluded = verdict["inputs"].get("excluded_runs", [])
    if excluded:
        L.append("")
        L.append("| excluded seq | reason (the failed eligibility test, named) |")
        L.append("|---|---|")
        for ex in excluded:
            L.append("| %s | %s |" % (ex.get("seq"), ex.get("reason", "").replace("|", "\\|")))
    else:
        L.append("Excluded: none.")
    L.append("")
    L.append("## Audit")
    L.append("")
    audit = verdict.get("audit", {})
    L.append("State: %s%s" % (audit.get("state", "N/A"),
                              (" (%s)" % audit["path"]) if audit.get("path") else ""))
    L.append("")
    L.append("## Deviations & amendments")
    L.append("")
    amendments = verdict["inputs"].get("amendments_applied", [])
    if amendments:
        for a in amendments:
            L.append("- amendment %s (see registry/amendments/%s/)" % (a, exp_id))
    else:
        L.append("None applied to this verdict.")
    corr_dir = os.path.join(root, "registry", "corrections", exp_id)
    if os.path.isdir(corr_dir):
        L.append("")
        L.append("Pre-freeze correction notes on this record (lawful only before sign-off + "
                 "before any final-phase run; they precede the freeze whose hash is above):")
        for name in sorted(os.listdir(corr_dir)):
            if name.endswith(".json"):
                L.append("- registry/corrections/%s/%s" % (exp_id, name))
    L.append("")
    L.append("---")
    L.append("### Non-binding commentary (does not and cannot alter the verdict above)")
    L.append("")
    commentary_path = os.path.join(root, "reports", "auto", exp_id, "commentary.md")
    if os.path.isfile(commentary_path):
        with open(commentary_path, "r", encoding="utf-8") as f:
            L.append("> " + f.read().strip().replace("\n", "\n> "))
    else:
        L.append("(none)")
    L.append("")

    out_dir = os.path.join(root, "reports", "auto", exp_id)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "verdict-%s.md" % exp_id)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(out_path)


def main():
    ap = argparse.ArgumentParser(description="Render the fixed-template verdict auto-report (fail-closed).")
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        render(root, args.experiment)
    except kc.KotError as e:
        fail(e.code, str(e).split(": ", 1)[1])


if __name__ == "__main__":
    main()
