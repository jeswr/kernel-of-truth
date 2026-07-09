#!/usr/bin/env python3
"""reuse-check.py — artifact ledger builder + BINDING pre-spend reuse gate +
reuse-chain audit traversal + structured L-score validation.

Mechanism defined in docs/next/resource-optimization-plan.md §3 (bead
kernel-of-truth-utq; Fable design deliverable, 2026-07-09; REVISION-1
post-Codex-audit hardening 2026-07-09). Delta D9 wires the same machinery
into prereg-freeze / log-append / verdict-gen / registry-check via
kot_common.check_record_reuse — this tool and those gates share ONE
implementation, so the pre-spend answer and the freeze/verdict answer cannot
diverge.

Subcommands
-----------
build
    Regenerate registry/artifact-ledger.jsonl (schema kot-artifact/2) as a
    pure function of results-log/*.jsonl + registry/verdicts/. One line per
    logged final-phase run row carrying the RC-2 identity axes: config cell,
    config_sha256, impl pins (config keys ending _sha256), observed pins,
    per-item metric fields, unblinded status, and row_sha256 (the exact line
    bytes — the RC-1 row-hash pin a consumer freezes). The committed ledger is
    the browsing/L-score inventory; every GATE below derives rows LIVE from
    results-log so a stale ledger can never weaken a check.

check
    The PRE-SPEND GATE — BINDING for paid launches (experiment-runner MUST /
    opus-execution-practices practice 5): the documented launch command is

        check --record registry/experiments/<id>.json --gate

    Record mode classifies every declared arm x rung cell against the live
    inventory by PIN IDENTITY (kot_common.pin_axis_compare):
      IDENTICAL      logged at provably identical pins
      INDETERMINATE  logged, identity unproven (placeholder/absent pins) —
                     fail-closed: treated as a potential duplicate spend
      DIFFERENT      logged only at provably different pins — NOT a collision
                     (the false-positive fix: same-name cells on a different
                     corpus/model do not block)
    Cells covered by the record's own frozen/draft reused_from or
    reuse_overrides declarations are reported COVERED and do not gate. With
    --gate the exit code is 3 iff any IDENTICAL/INDETERMINATE cell is
    UNCOVERED — the same predicate prereg-freeze refuses on
    (ERR_P2_REUSE_COLLISION), so a run-script fails closed exactly where a
    freeze would. Renamed-identical arm implementations are surfaced
    heuristically (impl-pin / config-hash cross-match across arm names);
    the EXACT check is RC-2 at freeze/verdict (declared-cell config matching
    + row hashes), which does not depend on arm names.
    Ad-hoc mode (--arm/--rung/--corpus/--impl-sha256/... --gate) keeps the
    conservative behaviour: ANY match gates.

audit
    RC-6 producer-chain traversal for the cross-vendor auditor:

        audit --experiment <id>

    walks the record's reused_from blocks recursively (chained reuse A<-B<-C:
    every link must satisfy the RC conditions independently), re-verifying at
    each link: frozen-index integrity, producer record drift, log chain, row
    hashes, and the RC-1..RC-8 machine checks (recheck mode). Prints the
    provenance tree; exit 1 on any failed link.

lscore
    ASM-0011 validation: derive the backlog L component from STRUCTURED
    registry edges (non-CLOSED registry/experiments/*.json depends_on +
    pins.corpus_hashes names, and ideas.jsonl requires/dependencies), compare
    against the free-text consumers list in registry/components.jsonl, and
    flag discrepancies. Report-only (GZ-4: a scorer override needs a written
    justification committed with the stub).

Conventions: stdlib only; fail closed with ERR_* codes; no silent fallbacks.
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER_RELPATH = os.path.join("registry", "artifact-ledger.jsonl")

# config keys that identify a cell (order matters for display only)
CELL_KEYS = ("arm", "rung", "seed", "retry_budget", "escalation_budget")


def _die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(2)


def _root(args):
    return os.path.abspath(args.root) if getattr(args, "root", None) else ROOT


def build(args):
    root = _root(args)
    if not os.path.isdir(os.path.join(root, "results-log")):
        _die("ERR_NO_RESULTS_LOG", os.path.join(root, "results-log"))
    try:
        rows = kc.derive_artifact_rows(root, include_all=args.all)
    except kc.KotError as e:
        _die(e.code, str(e).split(": ", 1)[1])
    ledger_path = os.path.join(root, LEDGER_RELPATH)
    with open(ledger_path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    print(
        "artifact-ledger: wrote %d rows from %d experiments -> %s"
        % (len(rows), len({r["experiment"] for r in rows}), LEDGER_RELPATH)
    )
    return 0


def _cell_str(cfg):
    return " ".join(
        "%s=%s" % (k, cfg[k]) for k in CELL_KEYS if k in cfg and cfg[k] is not None
    )


def _match(entry, args):
    cfg = entry.get("config") or {}
    if args.arm and cfg.get("arm") != args.arm:
        return False
    if args.rung and cfg.get("rung") != args.rung:
        return False
    if args.seed is not None and cfg.get("seed") != args.seed:
        return False
    if args.producer and entry.get("experiment") != args.producer:
        return False
    if args.metric and args.metric not in entry.get("metrics_logged", []):
        return False
    if args.config_sha256 and entry.get("config_sha256") != args.config_sha256:
        return False
    if args.impl_sha256 and args.impl_sha256 not in (entry.get("impl_pins") or {}).values():
        return False
    if args.unblinded_only and not entry.get("unblinded"):
        return False
    if args.corpus:
        ch = (entry.get("pins") or {}).get("corpus_hashes") or {}
        if args.corpus not in ch and args.corpus not in ch.values():
            return False
    if args.model_revision:
        mr = (entry.get("pins") or {}).get("model_revisions") or {}
        if args.model_revision not in mr and args.model_revision not in [
            str(v) for v in mr.values()
        ]:
            return False
    return True


def _report_matches(matches):
    by_cell = {}
    for m in matches:
        key = (m["experiment"], _cell_str(m.get("config") or {}))
        by_cell.setdefault(key, []).append(m)
    for (exp, cell), ms in sorted(by_cell.items()):
        m0 = ms[0]
        print(
            "  MATCH producer=%s cell[%s] rows=%d n_items=%s per_item=%s unblinded=%s log=%s"
            % (
                exp,
                cell,
                len(ms),
                m0.get("n_items"),
                ",".join(m0.get("per_item_fields") or []) or "-",
                m0.get("unblinded"),
                m0.get("log_path"),
            )
        )


def _check_record_mode(args, root, rows):
    """Record mode: pin-identity-tiered per-cell classification + the frozen
    collision predicate (shared with prereg-freeze). Returns exit code."""
    with open(args.record, "r", encoding="utf-8") as fh:
        rec = json.load(fh)
    rec_pins = rec.get("pins") or {}
    declared = [b.get("cells", []) for b in rec.get("reused_from", []) or []]
    overridden = [o.get("cells", []) for o in rec.get("reuse_overrides", []) or []]
    grid = kc.record_grid_cells(rec)
    deps = rec.get("depends_on", [])
    print(
        "pre-spend reuse check for record %s (%d grid cells; depends_on=%s)"
        % (args.record, len(grid), ",".join(deps))
    )
    n_covered_decl, n_blocking, n_different, n_free = 0, 0, 0, 0
    blocking_cells = []
    for arm, rung in grid:
        # rung-less logged rows match any rung cell (same fail-closed rule as
        # kot_common.reuse_collisions — the two surfaces must agree)
        hits = [r for r in rows
                if r["experiment"] != rec.get("id")
                and (r.get("config") or {}).get("arm") == arm
                and (rung is None or "rung" not in (r.get("config") or {})
                     or (r.get("config") or {}).get("rung") == rung)]
        if not hits:
            n_free += 1
            continue
        classes = {}
        for r in hits:
            cls = kc.pin_axis_compare(rec_pins, r.get("pins"))["overall"]
            classes.setdefault(cls, []).append(r)
        colliding = classes.get("identical", []) + classes.get("indeterminate", [])
        covered = (kc._covered(arm, rung, declared) or kc._covered(arm, rung, overridden))
        if colliding and covered:
            n_covered_decl += 1
            label = "COVERED "
        elif colliding:
            n_blocking += 1
            label = ("IDENTICAL" if classes.get("identical") else "INDETERM.")
            blocking_cells.append((arm, rung, sorted({r["experiment"] for r in colliding})))
        else:
            n_different += 1
            label = "DIFFERENT"
        producers = sorted({r["experiment"] for r in hits})
        unblinded = any(r.get("unblinded") for r in hits)
        print("  %-9s arm=%-42s rung=%-4s rows=%3d unblinded=%-5s producers=%s"
              % (label, arm, rung, len(hits), unblinded, ",".join(producers)))
    # renamed-identical heuristic: same impl pin or config hash under another arm name
    named_arms = {a for a, _ in grid}
    impl_vals = {v for r in rows for v in (r.get("impl_pins") or {}).values()
                 if (r.get("config") or {}).get("arm") in named_arms}
    renamed = [r for r in rows
               if (r.get("config") or {}).get("arm") not in named_arms
               and impl_vals & set((r.get("impl_pins") or {}).values())]
    for r in renamed[:10]:
        print("  RENAMED-CANDIDATE producer=%s cell[%s] shares impl pins with a declared arm "
              "under another name — verify RC-2 config identity before treating as distinct"
              % (r["experiment"], _cell_str(r.get("config") or {})))
    print("cells: %d blocking (identical/indeterminate pins, no frozen reuse decision); "
          "%d covered by reused_from/reuse_overrides; %d provably-different pins (no gate); "
          "%d unlogged" % (n_blocking, n_covered_decl, n_different, n_free))
    if n_blocking:
        print(
            "NOTE: consuming logged rows is lawful ONLY through a frozen kot-reg/2 reused_from"
            " block satisfying RC-1..RC-8 (docs/next/resource-optimization-plan.md §3.3,"
            " revision-1); a deliberate fresh re-run of ledger-held cells needs a"
            " reuse_overrides entry (machine-recorded reason). prereg-freeze refuses these"
            " cells with ERR_P2_REUSE_COLLISION until one of those is declared."
        )
        if args.gate:
            print("GATE: %d uncovered cell(s) with identical/unproven-different pins — STOP; "
                  "no spend before a frozen reuse decision (exit 3)." % n_blocking)
            return 3
        print("WARNING: run WITHOUT --gate — this output is DISCOVERY ONLY and licenses "
              "nothing; paid launches must use --gate (binding, exit 3).")
    return 0


def check(args):
    root = _root(args)
    try:
        rows = kc.derive_artifact_rows(root)
    except kc.KotError as e:
        _die(e.code, str(e).split(": ", 1)[1])

    if args.record:
        return _check_record_mode(args, root, rows)

    matches = [e for e in rows if _match(e, args)]
    if matches:
        print("pre-spend reuse check: %d matching logged rows" % len(matches))
        _report_matches(matches)
    else:
        print("pre-spend reuse check: no matching logged cells")
    if matches and args.gate:
        print(
            "GATE: matching logged results exist — STOP; consuming them requires a frozen"
            " kot-reg/2 reused_from block (RC-1..RC-8), a deliberate re-run requires a"
            " reuse_overrides entry (exit 3)."
        )
        return 3
    if matches and not args.gate:
        print("WARNING: run WITHOUT --gate — discovery only; paid launches must use --gate.")
    return 0


def audit(args):
    """RC-6 traversal: re-verify the full producer chain behind a record's
    reused_from blocks, recursively. Exit 1 on any failed link."""
    root = _root(args)
    failures = []

    def walk(exp_id, depth, seen):
        indent = "  " * depth
        if exp_id in seen:
            print("%s%s: CYCLE — already on this chain" % (indent, exp_id))
            failures.append((exp_id, "reuse chain cycle"))
            return
        rec_path = os.path.join(root, "registry", "experiments", "%s.json" % exp_id)
        if not os.path.isfile(rec_path):
            print("%s%s: MISSING record file" % (indent, exp_id))
            failures.append((exp_id, "record file missing"))
            return
        with open(rec_path, "r", encoding="utf-8") as fh:
            record = json.load(fh)
        blocks = record.get("reused_from") or []
        if not blocks:
            print("%s%s: no reuse (leaf)" % (indent, exp_id))
            return
        try:
            results = kc.check_record_reuse(record, root, mode="recheck")
        except kc.KotError as e:
            print("%s%s: FAIL %s" % (indent, exp_id, e))
            failures.append((exp_id, str(e)))
            return
        for res in results:
            b = res["block"]
            print("%s%s <- %s [%s] cells=%d rows=%d seqs=%s unblinded=%s outcome_selected=%s"
                  % (indent, exp_id, b["producer"], b["role"], len(b.get("cells", [])),
                     len(res["rows"]), res["seqs"], b.get("producer_unblinded"),
                     b.get("outcome_selected_arms")))
            walk(b["producer"], depth + 1, seen | {exp_id})

    walk(args.experiment, 0, frozenset())
    if failures:
        print("reuse-audit: %d failed link(s)" % len(failures))
        return 1
    print("reuse-audit: chain verifies")
    return 0


def _last_line_wins(path):
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("id"), str):
                out[obj["id"]] = obj
    return out


def lscore(args):
    """ASM-0011: derive L from structured edges; flag free-text mismatches."""
    root = _root(args)
    components = _last_line_wins(os.path.join(root, "registry", "components.jsonl"))
    ideas = _last_line_wins(os.path.join(root, "registry", "ideas.jsonl"))
    pending = {}
    for path in sorted(glob.glob(os.path.join(root, "registry", "experiments", "*.json"))):
        with open(path, "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        if rec.get("status") == "CLOSED":
            continue
        if os.path.isfile(os.path.join(root, "registry", "verdicts", "%s.json" % rec.get("id"))):
            continue  # already unblinded — not a pending consumer
        pending[rec["id"]] = rec

    def structured_consumers(comp):
        cid = comp["id"]
        names = {cid}
        if cid.startswith("corpus-"):
            names.add(cid[len("corpus-"):])
        consumers = set()
        for rid, rec in pending.items():
            deps = set(rec.get("depends_on", []))
            corpora = set((rec.get("pins") or {}).get("corpus_hashes") or {})
            if names & deps or names & corpora:
                consumers.add(rid)
        for iid, idea in ideas.items():
            edges = set(idea.get("requires", []) or []) | set(idea.get("dependencies", []) or [])
            if names & edges:
                consumers.add(iid)
        return sorted(consumers)

    def to_l(n):
        return 3 if n >= 2 else (2 if n == 1 else 1)

    ids = [args.component] if args.component else sorted(components)
    mismatches = 0
    for cid in ids:
        comp = components.get(cid)
        if comp is None:
            _die("ERR_NO_COMPONENT", "%s not in registry/components.jsonl" % cid)
        structured = structured_consumers(comp)
        freetext_n = len(comp.get("consumers") or [])
        dl, fl = to_l(len(structured)), to_l(freetext_n)
        flag = ""
        if dl != fl:
            mismatches += 1
            flag = "  MISMATCH (free-text implies L=%d — a scorer override needs a written justification, GZ-4)" % fl
        print("%-38s derived_L=%d structured=%s free_text_consumers=%d%s"
              % (cid, dl, ",".join(structured) or "-", freetext_n, flag))
    print("lscore: %d component(s), %d free-text/structured mismatch(es); derived L is the "
          "binding input to the research-engine §2.7 score" % (len(ids), mismatches))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None, help="repo root (default: inferred)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="regenerate registry/artifact-ledger.jsonl")
    b.add_argument(
        "--all",
        action="store_true",
        help="include non-final phases (exploratory rows are quarantined/uncitable; "
        "listed only so re-analysis work is visible)",
    )
    b.set_defaults(func=build)

    c = sub.add_parser("check", help="the pre-spend gate (BINDING with --gate)")
    c.add_argument("--record", help="a registry/experiments/<id>.json to expand and check")
    c.add_argument("--arm")
    c.add_argument("--rung")
    c.add_argument("--seed", type=int)
    c.add_argument("--corpus", help="corpus name or sha256 pin")
    c.add_argument("--model-revision", help="model name or revision pin")
    c.add_argument("--producer", help="restrict to one producer experiment id")
    c.add_argument("--metric", help="require this metric key to be logged")
    c.add_argument("--config-sha256", help="exact canonical config hash")
    c.add_argument("--impl-sha256", help="an implementation pin (config *_sha256 value) — "
                                         "finds renamed-identical arm implementations")
    c.add_argument("--unblinded-only", action="store_true",
                   help="only rows whose producer already has a verdict (RC-4 surface)")
    c.add_argument(
        "--gate",
        action="store_true",
        help="BINDING: exit 3 on uncovered identical/indeterminate-pin cells "
        "(record mode) or on any match (ad-hoc mode) — REQUIRED for paid launches",
    )
    c.set_defaults(func=check)

    a = sub.add_parser("audit", help="re-verify the reused_from producer chain (RC-6)")
    a.add_argument("--experiment", required=True, help="consumer experiment id")
    a.set_defaults(func=audit)

    l = sub.add_parser("lscore", help="derive L from structured registry edges (ASM-0011)")
    l.add_argument("--component", help="one component id (default: all)")
    l.set_defaults(func=lscore)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
