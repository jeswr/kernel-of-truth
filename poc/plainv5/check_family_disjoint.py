#!/usr/bin/env python3
"""check_family_disjoint.py — family-disjointness validator (codes FD-1..FD-6)
plus the largekern consumer gates ERR_STATUS_INELIGIBLE and the
provenance == resolve_family(author) agreement check.

Implements docs/next/design/plain-v5-register-lint-spec.md §7 (ASM-2452
family map, ASM-2458 runtime ledger; validator inputs: the map, the
disclosure/manifest, the DECLARED llm_seat_ledger, the RUNTIME seat ledger),
as required by the largekern WordNet-10k pilot precondition P8
(docs/next/design/gpt56-draft-pipeline-large-kernel.md §§8, 9.1, 9.2, 10;
ASM-2472, ASM-2478). Owner: coordinator-1, 2026-07-16.

Code numbering follows the PINNED plain-v5 §7 list (the largekern §9.1 P8
prose swaps the FD-1/FD-2 glosses; the pinned spec wins — both conditions
are enforced either way):
  FD-1  any model id resolves UNKNOWN.
  FD-2  family(seat) == family(author) for any seat.
  FD-3  a seat's model id missing or not in the exact dated form
        (mechanical proxy bound ASM-2495: >=4 consecutive digits, no
        whitespace; verbatim as-sent fidelity stays manifest-side).
  FD-4  the declared seat ledger is absent, or omits a seat role the
        record's own text names (mechanical cross-check over strings
        matching seat|judge|screen|tie-break; proxy bound ASM-2495).
  FD-5  orphan: a raw seat output file whose sha matches no runtime-ledger
        entry, or a runtime entry with no completed output_sha256.
  FD-6  integrity: the runtime ledger's hash chain does not verify
        head-to-entry-0, OR its role set mismatches the declared ledger.
  ERR_STATUS_INELIGIBLE  (largekern §9.2) a record whose status is outside
        the builder's explicit eligible-status allowlist reaches a slot
        requiring an eligible status (e.g. ModelDrafted where Explicated is
        required). Missing status fails closed.
  ERR_FAMILY_PROVENANCE  (largekern §8) the manifest's authorFamily (or a
        plain-v5 disclosure's authoring_model.family) != the pinned
        resolver's output for the author model id. Canonical family for
        ^gpt- ids is "openai", never "gpt" (ASM-2478).

Everything fails closed: any finding => exit nonzero, one line per finding,
"FAIL <CODE> <detail>". Stdlib only (Python 3.9).
"""

import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invoke_seat import (  # noqa: E402 — single pinned implementation, never re-typed
    AUTHOR_ROLE, DATED_ID_RE, SHA256_RE, UNKNOWN,
    SeatRefusal, chain_findings, load_family_map, pending_findings,
    read_ledger, resolve_family as _resolve_family,
)

DEFAULT_MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "family-map.json")
# largekern §9.1: the machinery is pointed at data/kernel-v1-draft/.
DEFAULT_RECORDS = os.path.join("data", "kernel-v1-draft")

# FD-4 mechanical cross-check (spec §7): role mentions = hyphenated tokens
# ending in seat/judge/screen, plus tie-break*. Proxy bound ASM-2495 —
# false positives are cheap (declare the role), false negatives are not.
ROLE_MENTION_RE = re.compile(r"\b([a-z][a-z0-9]*(?:-[a-z0-9]+)*-(?:seat|judge|screen))\b|\b(tie-break[a-z]*)\b")


def resolve_family(model_id, fmap=None):
    """Pinned-map family resolution; ^gpt- => "openai" (largekern authorFamily).

    fmap may be a loaded map dict or a path; default = the pinned
    poc/plainv5/family-map.json. Unmatched => "UNKNOWN" (callers fail closed)."""
    if fmap is None or isinstance(fmap, str):
        fmap = load_family_map(fmap or DEFAULT_MAP)
    return _resolve_family(model_id, fmap)


def _dated_ok(model_id):
    return (isinstance(model_id, str) and model_id
            and not re.search(r"\s", model_id) and DATED_ID_RE.search(model_id))


def _seat_findings(seats, author_family, fmap, where):
    """FD-1/FD-2/FD-3 over a list of {seat_role, model_id} seats."""
    findings = []
    for i, seat in enumerate(seats):
        role = seat.get("seat_role", "<missing seat_role #%d>" % i)
        mid = seat.get("model_id")
        if not _dated_ok(mid):
            findings.append(("FD-3", "%s seat %r: model id missing or not exact dated form: %r" % (where, role, mid)))
            continue
        fam = _resolve_family(mid, fmap)
        if fam == UNKNOWN:
            findings.append(("FD-1", "%s seat %r: model id %r resolves UNKNOWN" % (where, role, mid)))
        elif fam == author_family:
            findings.append(("FD-2", "%s seat %r: family(%s)=%s == family(author)" % (where, role, mid, fam)))
    return findings


def check_author(author_model_id, fmap):
    """FD-1/FD-3 on the author identity; returns (findings, family)."""
    findings = []
    if not _dated_ok(author_model_id):
        findings.append(("FD-3", "author model id missing or not exact dated form: %r" % (author_model_id,)))
        return findings, UNKNOWN
    fam = _resolve_family(author_model_id, fmap)
    if fam == UNKNOWN:
        findings.append(("FD-1", "author model id %r resolves UNKNOWN" % (author_model_id,)))
    return findings, fam


def check_declared(declared, author_family, fmap):
    """FD-4 (absence) + FD-1/2/3 over the DECLARED llm_seat_ledger."""
    if declared is None:
        return [("FD-4", "declared llm_seat_ledger is absent (every LLM seat must be declared in advance)")]
    if not isinstance(declared, list) or not all(isinstance(s, dict) for s in declared):
        return [("FD-4", "declared llm_seat_ledger malformed: expected [{seat_role, model_id}]")]
    return _seat_findings(declared, author_family, fmap, "declared")


def check_protocol_roles(record_text, declared):
    """FD-4 mechanical cross-check: every role the record's protocol text
    names must appear in the declared ledger."""
    declared_roles = set(s.get("seat_role") for s in (declared or []))
    findings = []
    for m in ROLE_MENTION_RE.finditer(record_text.lower()):
        mention = m.group(1) or m.group(2)
        if mention.startswith("tie-break"):
            mention = "tie-break"
        if mention not in declared_roles and not any(
                isinstance(r, str) and (mention in r or r in mention) for r in declared_roles):
            findings.append(("FD-4", "record text names seat role %r absent from the declared ledger" % mention))
    return findings


def check_runtime(ledger_path, declared, fmap):
    """FD-6 chain + role-set, FD-5 pending, FD-1/2/3 per runtime entry."""
    try:
        rows = read_ledger(ledger_path)
    except SeatRefusal as e:
        return [(e.code, str(e).split(" ", 1)[1])]
    findings = list(chain_findings(rows)) + list(pending_findings(rows))
    author = rows[0][0]
    a_find, author_family = check_author(author.get("model_id"), fmap)
    findings += a_find
    if author.get("family_map_sha256") != fmap["_sha256"]:
        findings.append(("FD-6", "runtime entry 0 family_map_sha256 does not match the pinned map (contract change requires a new ledger)"))
    findings += _seat_findings(
        [dict(seat_role=e.get("seat_role"), model_id=e.get("model_id")) for e, _ in rows[1:]],
        author_family, fmap, "runtime")
    for i, (e, _) in enumerate(rows):
        if e.get("resolved_family") != _resolve_family(e.get("model_id"), fmap):
            findings.append(("FD-6", "runtime entry %d resolved_family %r does not re-resolve under the pinned map" % (i, e.get("resolved_family"))))
    if declared is not None and isinstance(declared, list):
        declared_roles = set(s.get("seat_role") for s in declared)
        runtime_roles = set(e.get("seat_role") for e, _ in rows[1:])  # entry 0 = author, disclosed separately
        for role in sorted(declared_roles - runtime_roles):
            findings.append(("FD-6", "declared seat role %r never appears in the runtime ledger" % role))
        for role in sorted(runtime_roles - declared_roles):
            findings.append(("FD-6", "runtime seat role %r was never declared in advance" % role))
    return findings


def check_orphan_outputs(outputs_dir, ledger_path):
    """FD-5: every raw seat output file must match a runtime-ledger
    output_sha256 — a direct (un-ledgered) model call shows up here."""
    try:
        rows = read_ledger(ledger_path)
    except SeatRefusal as e:
        return [(e.code, str(e).split(" ", 1)[1])]
    ledgered = set(e.get("output_sha256") for e, _ in rows
                   if isinstance(e.get("output_sha256"), str) and SHA256_RE.match(e.get("output_sha256")))
    findings = []
    if not os.path.isdir(outputs_dir):
        return [("FD-5", "outputs dir %s is absent; cannot sweep for orphans" % outputs_dir)]
    for name in sorted(os.listdir(outputs_dir)):
        full = os.path.join(outputs_dir, name)
        if not os.path.isfile(full):
            continue
        with open(full, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        if sha not in ledgered:
            findings.append(("FD-5", "orphan seat output %s (sha %s…) matches no runtime-ledger entry — direct model calls are banned" % (name, sha[:12])))
    return findings


def check_provenance(manifest, fmap):
    """largekern §8 / plain-v5 PV5-10: the recorded family field MUST equal
    resolve_family(author id) — the resolver's vocabulary wins, never a
    string compare, never a default-pass ("gpt" is not a family)."""
    findings = []
    if "draftAuthor" in manifest or "authorFamily" in manifest:
        author_id, recorded = manifest.get("draftAuthor"), manifest.get("authorFamily")
    elif isinstance(manifest.get("authoring_model"), dict):
        am = manifest["authoring_model"]
        author_id, recorded = am.get("model"), am.get("family")
    else:
        return [("ERR_FAMILY_PROVENANCE", "manifest carries neither draftAuthor/authorFamily nor authoring_model{family,model}")], None
    a_find, fam = check_author(author_id, fmap)
    findings += a_find
    if fam == UNKNOWN:
        return findings, None
    if recorded != fam:
        findings.append(("ERR_FAMILY_PROVENANCE",
                         "recorded family %r != resolve_family(%r) == %r (canonical vocabulary is the resolver's; ASM-2478)"
                         % (recorded, author_id, fam)))
    return findings, author_id


def check_status_eligibility(records_path, allowlist):
    """largekern §9.2 consumer gate: builders take an explicit
    eligible-status allowlist and fail closed if an ineligible record (e.g.
    ModelDrafted) reaches a slot requiring an eligible status (Explicated)."""
    if not allowlist:
        return [("ERR_STATUS_INELIGIBLE", "no eligible-status allowlist supplied — the gate never default-passes")]
    paths = []
    if os.path.isdir(records_path):
        for root, _, names in os.walk(records_path):
            paths += [os.path.join(root, n) for n in sorted(names) if n.endswith(".json")]
    elif os.path.isfile(records_path):
        paths = [records_path]
    else:
        return [("ERR_STATUS_INELIGIBLE", "records path %s is absent; cannot certify eligibility" % records_path)]
    findings = []
    for p in sorted(paths):
        try:
            with open(p, "r", encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError) as e:
            findings.append(("ERR_STATUS_INELIGIBLE", "%s unreadable (%s); fails closed" % (p, e)))
            continue
        status = rec.get("status")
        if status not in allowlist:
            findings.append(("ERR_STATUS_INELIGIBLE",
                             "%s: status %r reaches a slot requiring one of %s" % (p, status, sorted(allowlist))))
    return findings


def run_checks(map_path, manifest_path=None, declared_path=None, runtime_ledger=None,
               outputs_dir=None, record_text_path=None, records_path=None, eligible=None):
    findings = []
    try:
        fmap = load_family_map(map_path)
    except SeatRefusal as e:
        return [(e.code, str(e).split(" ", 1)[1])]

    manifest = None
    author_family = None
    if manifest_path:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, ValueError) as e:
            findings.append(("ERR_FAMILY_PROVENANCE", "manifest %s unreadable: %s" % (manifest_path, e)))
        else:
            prov, author_id = check_provenance(manifest, fmap)
            findings += prov
            if author_id:
                author_family = _resolve_family(author_id, fmap)

    declared = None
    if declared_path:
        try:
            with open(declared_path, "r", encoding="utf-8") as f:
                declared = json.load(f)
            if isinstance(declared, dict):
                declared = declared.get("llm_seat_ledger")
        except (OSError, ValueError) as e:
            findings.append(("FD-4", "declared ledger %s unreadable: %s" % (declared_path, e)))

    if runtime_ledger:
        findings += check_runtime(runtime_ledger, declared, fmap)
        if author_family is None:
            try:
                author_family = _resolve_family(read_ledger(runtime_ledger)[0][0].get("model_id"), fmap)
            except SeatRefusal:
                pass
        if outputs_dir:
            findings += check_orphan_outputs(outputs_dir, runtime_ledger)
    elif outputs_dir:
        findings.append(("FD-5", "outputs dir given without a runtime ledger; nothing to certify against"))

    if declared_path:
        findings += check_declared(declared, author_family if author_family else UNKNOWN, fmap)
        if author_family is None:
            findings.append(("FD-1", "no author identity available (manifest or runtime entry 0) to compare seat families against"))

    if record_text_path:
        try:
            with open(record_text_path, "r", encoding="utf-8") as f:
                findings += check_protocol_roles(f.read(), declared)
        except OSError as e:
            findings.append(("FD-4", "record text %s unreadable: %s" % (record_text_path, e)))

    if records_path or eligible:
        findings += check_status_eligibility(records_path or DEFAULT_RECORDS, set(eligible or []))

    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description="family-disjointness validator (plain-v5 spec §7; largekern P8)")
    ap.add_argument("--family-map", default=DEFAULT_MAP)
    ap.add_argument("--manifest", help="record manifest / store disclosure JSON (draftAuthor+authorFamily, or authoring_model{family,model})")
    ap.add_argument("--declared", help="declared llm_seat_ledger JSON: [{seat_role, model_id}] or {llm_seat_ledger: [...]}")
    ap.add_argument("--runtime-ledger", help="kot-seat-ledger/1 JSONL (entry 0 = author seat)")
    ap.add_argument("--outputs-dir", help="raw seat output files to sweep for FD-5 orphans")
    ap.add_argument("--record-text", help="record/protocol text for the FD-4 role cross-check")
    ap.add_argument("--records", help="record file or directory for the status-eligibility gate (default %s when --eligible-status is given)" % DEFAULT_RECORDS)
    ap.add_argument("--eligible-status", action="append", default=[],
                    help="explicit eligible-status allowlist entry (repeatable; e.g. Explicated)")
    ap.add_argument("--resolve", metavar="MODEL_ID", help="print resolve_family(MODEL_ID) and exit (UNKNOWN exits nonzero)")
    args = ap.parse_args(argv)

    if args.resolve is not None:
        fam = resolve_family(args.resolve, args.family_map)
        print(fam)
        sys.exit(0 if fam != UNKNOWN else 1)

    findings = run_checks(args.family_map, args.manifest, args.declared, args.runtime_ledger,
                          args.outputs_dir, args.record_text, args.records, args.eligible_status)
    for code, msg in findings:
        print("FAIL %s %s" % (code, msg))
    if findings:
        sys.exit(1)
    print("OK family-disjointness checks green (FD-1..FD-6, provenance, status-eligibility as invoked)")


if __name__ == "__main__":
    main()
