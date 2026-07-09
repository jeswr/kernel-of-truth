#!/usr/bin/env python3
"""claims-check — the epistemic-tag lint (docs/next/assumption-register.md §3).

    python3 tools/registry/claims-check.py [--root <repo>] [--register <path>] [paths...]

Enforces the maintainer's epistemic-discipline directive (2026-07-08): every
load-bearing claim carries a status tag (MEASURED / LIT-BACKED / STIPULATED /
EXTRAPOLATION); a decision/premise may rest only on MEASURED or LIT-BACKED
claims (plus explicitly registered STIPULATED assumptions cited by ASM-id);
a load-bearing EXTRAPOLATION is always a violation.

With no paths, validates registry/assumptions.jsonl (if present). Given paths:
  *.md / *.txt   — scanned under the marker convention: lines carrying
                   PREMISE: / DECISION: / LOAD-BEARING: must carry a tag,
                   the tag must not be EXTRAPOLATION, MEASURED/LIT-BACKED
                   need a non-empty backing ref, STIPULATED must cite a
                   registered ASM-id; every cited ASM-id must exist.
                   Markdown hanging-indent continuations of a bullet are
                   joined into one logical line first, so a wrapped premise
                   whose tag lands on the continuation line is read whole
                   (unindented wrapped prose is NOT joined — fail closed).
  *.json/*.jsonl — any top-level "assumptions" array is validated with the
                   same per-entry rules as the register.

Exit 0 only if every check passes; violations print named ERR_ASM_* findings
and exit 1.

Wiring (assumption-register.md §6, maintainer decision 2026-07-09):
  - item 1 ENABLED: registry-check's run-all set invokes this lint over the
    register + docs/**/*.md on every push (fail-closed).
  - item 2 is PAUSE-and-reassess and lives in prereg-freeze (non-fatal flag),
    NOT here: this lint stays the CONCLUSION-side hard gate — stop false
    conclusions, not experiments.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

TAGS = ("MEASURED", "LIT-BACKED", "STIPULATED", "EXTRAPOLATION")
ASM_ID_RE = re.compile(r"^ASM-\d{4}$")
ASM_CITE_RE = re.compile(r"\bASM-\d{4}\b")
# Inline tag: [MEASURED: <ref>] / [LIT-BACKED: <ref>] / [STIPULATED: ASM-0003] /
# [EXTRAPOLATION: ASM-0002]. The ref part is optional at the syntax level so the
# lint (not the regex) can name the missing-backing violation.
TAG_RE = re.compile(r"\[(MEASURED|LIT-BACKED|STIPULATED|EXTRAPOLATION)(?::\s*([^\]]*?))?\s*\]")
MARKER_RE = re.compile(r"\b(PREMISE|DECISION|LOAD-BEARING):")
# Role set = the P5 roster as carried into the engine roles table (research-engine §3):
# designer/statistician/skeptic are the Fable design-side pseudonyms (added 2026-07-09,
# bead kernel-of-truth-utq — the register previously had only run-side owners).
OWNER_OK = re.compile(r"^(?:maintainer|(?:runner|auditor|coordinator|writer|redteam|designer|statistician|skeptic)-[0-9]+)$")
# Backing shapes (spec §1 backing column):
MEASURED_REF_RE = re.compile(r"(registry/(?:verdicts|experiments|audits)/|results-log/|[0-9a-f]{8,64})")
# kot-lit[:/] = a Pillar-C KB record citation. This lint checks the backing
# SHAPE only; whether a KB citation RESOLVES to a committed kb/records file is
# kb-check's gate (assumption-register.md §6 item 3, ENABLED 2026-07-09).
# Case-insensitive so the canonical lowercase id grammar (arxiv:NNNN.NNNNN,
# kb_common.ID_RE) is accepted alongside the prose form arXiv:NNNN.NNNNN.
LIT_REF_RE = re.compile(r"(arxiv:\s*\d{4}\.\d{4,5}|doi:|10\.\d{4,}/|kot-lit[:/]|\b(?:19|20)\d{2}\b)",
                        re.IGNORECASE)

REQUIRED_FIELDS = ("id", "claim", "tag", "backing_ref", "load_bearing", "status", "owner")


class Findings:
    def __init__(self):
        self.items = []

    def err(self, code, msg):
        self.items.append((code, msg))
        print("FAIL %s: %s" % (code, msg))

    def ok(self, msg):
        print("  ok %s" % msg)


def check_entry(entry, where, f):
    """Validate one register line / assumptions[] element. Returns its id (or None)."""
    if not isinstance(entry, dict):
        f.err("ERR_ASM_SCHEMA", "%s: entry is not an object" % where)
        return None
    missing = [k for k in REQUIRED_FIELDS if k not in entry]
    if missing:
        f.err("ERR_ASM_SCHEMA", "%s: missing required field(s) %s" % (where, ", ".join(missing)))
        return entry.get("id")
    eid, tag = entry["id"], entry["tag"]
    if not (isinstance(eid, str) and ASM_ID_RE.match(eid)):
        f.err("ERR_ASM_SCHEMA", "%s: id %r is not ASM-NNNN" % (where, eid))
    if tag not in TAGS:
        f.err("ERR_ASM_SCHEMA", "%s: tag %r not in %s" % (where, tag, "/".join(TAGS)))
        return eid
    if entry["status"] not in ("open", "resolved"):
        f.err("ERR_ASM_SCHEMA", "%s: status %r not open/resolved" % (where, entry["status"]))
    if not isinstance(entry["load_bearing"], bool):
        f.err("ERR_ASM_SCHEMA", "%s: load_bearing must be boolean" % where)
    owner = entry["owner"]
    if not (isinstance(owner, str) and OWNER_OK.match(owner)):
        f.err("ERR_ASM_SCHEMA", "%s: owner %r is not a pseudonym <role>-<n> or 'maintainer' (RT-14)"
              % (where, owner))
    ref = entry.get("backing_ref") or ""
    # The RULE, mechanised: a load-bearing EXTRAPOLATION cannot exist.
    if tag == "EXTRAPOLATION" and entry.get("load_bearing") is True:
        f.err("ERR_ASM_LOADBEARING_EXTRAPOLATION",
              "%s: %s is tagged EXTRAPOLATION with load_bearing=true — resolve it "
              "(measure / cite literature) or demote the dependent decision to a fork" % (where, eid))
    # Per-tag backing requirements (spec §1).
    if tag == "MEASURED" and not MEASURED_REF_RE.search(ref):
        f.err("ERR_ASM_BACKING", "%s: %s MEASURED needs a verdict/experiment/log reference or hash, "
              "got %r" % (where, eid, ref))
    if tag == "LIT-BACKED" and not LIT_REF_RE.search(ref):
        f.err("ERR_ASM_BACKING", "%s: %s LIT-BACKED needs a paper id (arXiv/DOI/kot-lit) or year, "
              "got %r" % (where, eid, ref))
    if tag == "STIPULATED" and not (entry.get("rationale") or "").strip():
        f.err("ERR_ASM_BACKING", "%s: %s STIPULATED requires a non-empty 'rationale'" % (where, eid))
    if tag == "EXTRAPOLATION" and not (entry.get("resolution_path") or "").strip():
        f.err("ERR_ASM_BACKING", "%s: %s EXTRAPOLATION requires a non-empty 'resolution_path' "
              "(what measurement or lit-search converts it)" % (where, eid))
    return eid


def load_register(path, f):
    """Validate the register; return {id: entry} with last-line-wins semantics."""
    register = {}
    rel = path
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        return register
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        where = "%s line %d" % (rel, i + 1)
        try:
            kc.require_no_account_strings(line.encode("utf-8"), where)
        except kc.KotError as e:
            f.err(e.code, str(e))
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            f.err("ERR_P2_IO", "%s: unparseable (%s)" % (where, e))
            continue
        eid = check_entry(entry, where, f)
        if eid:
            register[eid] = entry  # append-only: the last line for an id is current
    f.ok("register: %s (%d current entr%s)" % (rel, len(register), "y" if len(register) == 1 else "ies"))
    return register


# A physical line that OPENS a new markdown block (bullet, numbered item,
# heading, table row, blockquote) is never a continuation of the line above.
BLOCK_OPEN_RE = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|\||>)")


def logical_lines(text):
    """Join markdown hanging-indent continuations into logical lines.

    A physical line continues the previous logical line iff it is non-blank,
    starts with whitespace (the hanging indent of a wrapped bullet), does not
    itself open a new block, and the previous physical line was non-blank.
    Deliberately conservative: an UNINDENTED wrapped paragraph line is not
    joined, so a bare marker line can never borrow a tag from ordinary prose
    below it (fail closed). Returns [(first_physical_lineno_1based, text)].
    """
    out = []
    prev_blank = True
    for i, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            prev_blank = True
            continue
        if (out and not prev_blank and raw[:1] in (" ", "\t")
                and not BLOCK_OPEN_RE.match(raw)):
            lineno, joined = out[-1]
            out[-1] = (lineno, joined + " " + stripped)
        else:
            out.append((i, stripped))
        prev_blank = False
    return out


def check_doc(path, register, register_available, f):
    rel = path
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as e:
        f.err("ERR_P2_IO", "%s: unreadable (%s)" % (rel, e))
        return
    n_markers = 0
    for lineno, line in logical_lines(text):
        where = "%s line %d" % (rel, lineno)
        tags = TAG_RE.findall(line)
        # Every cited ASM-id must exist in the register (when one is available).
        if register_available:
            for cited in ASM_CITE_RE.findall(line):
                if cited not in register:
                    f.err("ERR_ASM_UNKNOWN_ID", "%s: cites %s, absent from the register" % (where, cited))
        if not MARKER_RE.search(line):
            continue
        n_markers += 1
        if not tags:
            f.err("ERR_ASM_UNTAGGED_PREMISE",
                  "%s: PREMISE/DECISION/LOAD-BEARING line carries no epistemic tag" % where)
            continue
        for tag, ref in tags:
            ref = (ref or "").strip()
            if tag == "EXTRAPOLATION":
                f.err("ERR_ASM_EXTRAPOLATION_PREMISE",
                      "%s: a decision/premise may not rest on an EXTRAPOLATION (the RULE); "
                      "resolve it or register a fork" % where)
            elif tag in ("MEASURED", "LIT-BACKED") and not ref:
                f.err("ERR_ASM_BACKING", "%s: [%s] on a premise line needs a backing ref" % (where, tag))
            elif tag == "STIPULATED":
                cited = ASM_CITE_RE.search(ref or "")
                if not cited:
                    f.err("ERR_ASM_UNREGISTERED_STIPULATION",
                          "%s: [STIPULATED] on a premise line must cite a registered ASM-id" % where)
                elif register_available and cited.group(0) not in register:
                    f.err("ERR_ASM_UNKNOWN_ID", "%s: cites %s, absent from the register"
                          % (where, cited.group(0)))
    f.ok("doc: %s (%d marked premise line%s)"
         % (rel, n_markers, "" if n_markers == 1 else "s"))


def check_record(path, register, register_available, f):
    rel = path
    try:
        with open(path, "r", encoding="utf-8") as fh:
            if path.endswith(".jsonl"):
                docs = [json.loads(l) for l in fh if l.strip()]
            else:
                docs = [json.load(fh)]
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        f.err("ERR_P2_IO", "%s: unparseable (%s)" % (rel, e))
        return
    n = 0
    for d, doc in enumerate(docs):
        if not isinstance(doc, dict):
            continue
        for j, entry in enumerate(doc.get("assumptions", []) or []):
            n += 1
            eid = check_entry(entry, "%s assumptions[%d]" % (rel, j), f)
            # A record may reference the shared register instead of restating backing:
            if register_available and eid and eid in register and isinstance(entry, dict):
                pass  # existence is the requirement; register rules did the rest
    f.ok("record: %s (%d assumptions entr%s)" % (rel, n, "y" if n == 1 else "ies"))


def main():
    ap = argparse.ArgumentParser(description="Epistemic-tag lint (fail-closed).")
    ap.add_argument("--root", default=None)
    ap.add_argument("--register", default=None,
                    help="register path (default <root>/registry/assumptions.jsonl)")
    ap.add_argument("paths", nargs="*", help="docs (.md/.txt) or records (.json/.jsonl) to scan")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    reg_path = args.register or os.path.join(root, "registry", "assumptions.jsonl")

    f = Findings()
    register_available = os.path.isfile(reg_path)
    register = load_register(reg_path, f) if register_available else {}
    if not register_available:
        f.ok("register: none at %s (doc checks run without ASM-id resolution)" % reg_path)

    for path in args.paths:
        if os.path.abspath(path) == os.path.abspath(reg_path):
            continue  # already validated as the register
        if path.endswith((".json", ".jsonl")):
            check_record(path, register, register_available, f)
        else:
            check_doc(path, register, register_available, f)

    if f.items:
        print("claims-check: %d violation(s)" % len(f.items))
        sys.exit(1)
    print("claims-check: PASS")


if __name__ == "__main__":
    main()
