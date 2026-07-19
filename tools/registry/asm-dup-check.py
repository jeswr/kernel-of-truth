#!/usr/bin/env python3
"""asm-dup-check — duplicate-ASM-id guard for registry/assumptions.jsonl.

Implements the recurrence-prevention recommendation of bead
kernel-of-truth-ybok: "Recommend a dup-id guard in the ASM-register tooling to
prevent recurrence." The root pattern the bead identified: retired
molecule-S5's ASM ids (2401-2403, 2455) were REUSED by later experiments
(stage-4, F1-K round-10) after the pivot freed them -> unrelated claims silently
share an id, and JSON last-line-wins masks the collision (live gates resolve to
the later line, so a frozen record asserting these are uniquely-registered
anchors is quietly false).

STANDALONE by design (2026-07-19): this is NOT yet wired into the pre-push
registry-check gate, because 9 known duplicates currently exist and some of
their fixes require refreezing frozen records (2401-2403 via bead euva; 2455 via
the F1-K round-10 carrier record) that are gated on maintainer/experiment
decisions. Arming a hard gate now would strand every push. Instead this script
exits 0 while only the 9 TRIAGED dups are present, and exits nonzero the moment
a NEW (untriaged) duplicate id appears — so it can be run in CI or by hand today,
and promoted into registry-check.py's check list (as check_asm_unique) once the
allowlist is emptied by the pending refreezes.

Usage:
    python3 tools/registry/asm-dup-check.py [--root <repo>]
Exit 0: no duplicates, or every duplicate id is in the triaged allowlist.
Exit 1: a duplicate id NOT in the allowlist (a new, untriaged collision).
Exit 2: file/parse error (fail closed).
"""
import argparse
import collections
import json
import os
import sys

# The 9 duplicate ids triaged 2026-07-19 under bead kernel-of-truth-ybok.
# Each is either a BENIGN in-place revision (intentional last-line-wins, the
# second line explicitly supersedes the first -> schema-hygiene only) or a REAL
# COLLISION (two unrelated claims sharing an id -> genuine defect whose fix is a
# renumber + refreeze of the affected record, tracked in the noted bead).
# An entry here says "this dup is known and accounted for"; it is NOT a claim the
# defect is fixed. Remove an id from this dict once its fix lands, so the guard
# starts enforcing uniqueness for it too.
TRIAGED_DUP_ALLOWLIST = {
    "ASM-0010": "benign: REVISION-1 rewrite post-Codex-audit (last-line-wins supersession)",
    "ASM-0011": "benign: REVISION-1 rewrite post-Codex-audit (last-line-wins supersession)",
    "ASM-0023": "likely-benign: nsk1-eval 3-gen-family same-topic revision (verify exact-dup vs revision)",
    "ASM-2389": "benign: SUPERSEDED by re-review 5c (last-line-wins supersession)",
    "ASM-2399": "benign: Stage-4 decision-boundary revision D1/D2 (last-line-wins supersession)",
    "ASM-2401": "REAL COLLISION: molecule-S5 REPILOT vs stage-4 io_match/residuals -> renumber+refreeze in bead euva",
    "ASM-2402": "REAL COLLISION: molecule-S5 REPILOT vs stage-4 io_match/residuals -> renumber+refreeze in bead euva",
    "ASM-2403": "REAL COLLISION: molecule-S5 REPILOT vs stage-4 io_match/residuals -> renumber+refreeze in bead euva",
    "ASM-2455": "REAL COLLISION: molecule-S5 RE-PILOT attribution vs F1-K round-10 carrier content-auth floors -> renumber+refreeze the F1-K round-10 carrier record",
}


def scan(path):
    """Return (total, dict id->[line numbers]) or raise on parse/IO failure."""
    ids = collections.defaultdict(list)
    total = 0
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            # Fail closed: a malformed line in the provenance ledger is itself a
            # defect, not something to skip silently.
            obj = json.loads(line)
            _id = obj.get("id")
            if _id is None:
                raise ValueError(f"line {lineno}: record has no 'id' field")
            ids[_id].append(lineno)
    return total, ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    args = ap.parse_args()
    path = os.path.join(args.root, "registry", "assumptions.jsonl")
    if not os.path.exists(path):
        print(f"ERR_ASM_DUP_IO: {path} not found", file=sys.stderr)
        return 2
    try:
        total, ids = scan(path)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"ERR_ASM_DUP_IO: {e}", file=sys.stderr)
        return 2

    dups = {k: v for k, v in ids.items() if len(v) > 1}
    untriaged = sorted(k for k in dups if k not in TRIAGED_DUP_ALLOWLIST)
    stale_allow = sorted(k for k in TRIAGED_DUP_ALLOWLIST if k not in dups)

    print(f"scanned {total} ASM records, {len(ids)} unique ids, "
          f"{len(dups)} duplicate id(s)")
    for k in sorted(dups):
        tag = "ALLOWED" if k in TRIAGED_DUP_ALLOWLIST else "UNTRIAGED"
        note = TRIAGED_DUP_ALLOWLIST.get(k, "*** NEW COLLISION — renumber the later claim to a fresh id ***")
        print(f"  [{tag}] {k}: lines {ids[k]} — {note}")

    # A stale allowlist entry (an id that is no longer duplicated) is a hint that
    # a fix landed; surface it as a warning so the allowlist gets pruned, but do
    # not fail on it.
    for k in stale_allow:
        print(f"  [STALE-ALLOWLIST] {k}: no longer duplicated — remove from "
              f"TRIAGED_DUP_ALLOWLIST so uniqueness is enforced for it")

    if untriaged:
        print(f"ERR_ASM_DUP: {len(untriaged)} untriaged duplicate id(s): "
              f"{', '.join(untriaged)}", file=sys.stderr)
        return 1
    print("OK: no untriaged duplicate ASM ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
