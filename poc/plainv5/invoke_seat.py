#!/usr/bin/env python3
"""invoke_seat.py — the pinned ledgered LLM-seat invoker (kot-seat-ledger/1).

Implements docs/next/design/plain-v5-register-lint-spec.md §7 (runtime seat
ledger + invoker; ASM-2452 family map, ASM-2458 ledger/invoker), consumed by
the largekern WordNet-10k pilot as precondition P8
(docs/next/design/gpt56-draft-pipeline-large-kernel.md §9.1, ASM-2472,
ASM-2478). Owner: coordinator-1, 2026-07-16.

Contract (spec §7, verbatim obligations):
  * schema kot-seat-ledger/1: append-only JSONL, entry 0 = the author seat
    (exact dated authoring model id). Entry fields: {seq, prev_sha256,
    seat_role, model_id, resolved_family, family_map_sha256, prompt_sha256,
    invocation_form, output_sha256}. prev_sha256 hash-chains each entry to
    its predecessor, so deletion, reordering, or rewrite breaks the chain.
  * every LLM invocation in ANY seat role goes through this invoker, which
    resolves the family via the pinned map, evaluates
    family(seat) != family(entry 0) AND both non-UNKNOWN BEFORE dispatch,
    REFUSES (no API call) on FD-1/FD-2, appends the entry pre-dispatch, and
    completes output_sha256 on return. Direct model calls are banned; FD-5
    catches them as orphans.
  * family resolution (spec §7 map): normalize the id, apply rules in order,
    first match wins; no match => UNKNOWN => FAIL (never inferred, never
    default-pass). Normalization is for family resolution only — manifests
    carry the exact dated model id verbatim.

Chain-byte convention: kot_common (P2 §2.1) — prev_sha256 = sha256 of the
predecessor line's exact bytes INCLUDING its terminating newline; genesis
prev_sha256 = 64 zeros. Hashed lines are canonical JSON (sorted keys, no
insignificant whitespace) + "\\n".

Completion semantics [STIPULATED: ASM-2494 — spec §7 pins "appends the entry
pre-dispatch ... completes output_sha256 on return" but not its mechanics]:
the pending entry (output_sha256 = null) is appended BEFORE dispatch; on
return, ONLY the final line is amended in place to the completed form. The
hash chain is defined over COMPLETED line bytes, so a later entry chains to
its predecessor's completed bytes; amending any non-final line breaks FD-6.
A pending FINAL line (crash mid-dispatch, dispatch failure, or an abandoned
call) is an FD-5 orphan: it is evidence, it blocks further invocations
through this invoker, and it is swept by check_family_disjoint.py /
verdict-gen before any readout.

FD-3 "exact dated form" mechanical proxy bound [STIPULATED: ASM-2495]:
a model id must be a non-empty whitespace-free string carrying >= 4
consecutive decimal digits (a date/snapshot token, e.g. gpt-5.6-sol-20260601,
claude-opus-4-20250514). Verbatim as-sent/as-returned fidelity stays a
manifest-side check (largekern spec §8).

Stdlib only (Python 3.9). Every violation fails closed with a named code:
FD-1/FD-2/FD-3/FD-5/FD-6 (spec §7) or ERR_* (this file). Exit nonzero, one
line per finding: "FAIL <CODE> <detail>".
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

GENESIS = "0" * 64
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAP_SCHEMA = "kot-family-map/1"
LEDGER_SCHEMA = "kot-seat-ledger/1"
UNKNOWN = "UNKNOWN"
AUTHOR_ROLE = "author"

# spec §7 entry field set, closed (kot-seat-ledger/1).
ENTRY_FIELDS = (
    "schema", "seq", "prev_sha256", "seat_role", "model_id",
    "resolved_family", "family_map_sha256", "prompt_sha256",
    "invocation_form", "output_sha256",
)

# FD-3 proxy bound (ASM-2495): >=4 consecutive digits = dated snapshot token.
DATED_ID_RE = re.compile(r"[0-9]{4}")
SEAT_ROLE_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

# RT-14 (spec §1): the account-string pattern list of
# tools/registry/kot_common.require_no_account_strings — imported, not
# re-typed. Ledger lines are scanned before they are written.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(_REPO_ROOT, "tools", "registry"))
try:
    from kot_common import account_lint  # noqa: E402
except Exception:  # pragma: no cover — fail closed, never run unlinted
    account_lint = None


class SeatRefusal(Exception):
    """Fail-closed refusal with a named FD-*/ERR_* code. No API call made."""

    def __init__(self, code, msg):
        self.code = code
        super().__init__("%s %s" % (code, msg))


# ------------------------------------------------------------------ family map

def load_family_map(path):
    """Load + validate the pinned kot-family-map/1 file. Fails closed."""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        fmap = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError) as e:
        raise SeatRefusal("ERR_FAMILY_MAP", "unreadable family map %s: %s" % (path, e))
    if fmap.get("schema") != MAP_SCHEMA:
        raise SeatRefusal("ERR_FAMILY_MAP", "schema != %s in %s" % (MAP_SCHEMA, path))
    # spec §7: unmatched => UNKNOWN => FAIL, never default-pass. The map must
    # itself declare that posture; a map without it is not the pinned map.
    if fmap.get("unmatched") != "UNKNOWN-FAILS-CLOSED":
        raise SeatRefusal("ERR_FAMILY_MAP", "unmatched policy is not UNKNOWN-FAILS-CLOSED")
    if not isinstance(fmap.get("normalize"), list) or not isinstance(fmap.get("rules"), list):
        raise SeatRefusal("ERR_FAMILY_MAP", "normalize/rules missing or not lists")
    for rule in fmap["rules"]:
        if not isinstance(rule, dict) or not rule.get("match") or not rule.get("family"):
            raise SeatRefusal("ERR_FAMILY_MAP", "malformed rule %r" % (rule,))
    fmap["_sha256"] = hashlib.sha256(raw).hexdigest()
    return fmap


def resolve_family(model_id, fmap):
    """spec §7: normalize the id, apply rules in order, first match wins;
    no match => UNKNOWN (the caller fails closed — never inferred)."""
    if not isinstance(model_id, str) or not model_id:
        return UNKNOWN
    s = model_id
    for step in fmap["normalize"]:
        if step == "lowercase":
            s = s.lower()
        elif isinstance(step, str) and step.startswith("strip-prefix-regex: "):
            s = re.sub(step[len("strip-prefix-regex: "):], "", s, count=1)
        else:
            raise SeatRefusal("ERR_FAMILY_MAP", "unknown normalize step %r" % (step,))
    for rule in fmap["rules"]:
        if re.search(rule["match"], s):
            return rule["family"]
    return UNKNOWN


# ------------------------------------------------------------------ ledger I/O

def entry_line(entry):
    """Canonical ledger line bytes (sorted keys, compact, newline-terminated
    — the exact byte range the chain convention hashes)."""
    return (json.dumps(entry, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def read_ledger(path):
    """Return [(entry, line_bytes), ...]. Unparseable lines are FD-6."""
    if not os.path.isfile(path):
        raise SeatRefusal("FD-6", "runtime seat ledger %s is absent" % path)
    out = []
    with open(path, "rb") as f:
        for i, line in enumerate(f.read().splitlines(True)):
            try:
                entry = json.loads(line.decode("utf-8"))
            except ValueError:
                raise SeatRefusal("FD-6", "ledger line %d is not valid JSON" % i)
            out.append((entry, line))
    if not out:
        raise SeatRefusal("FD-6", "ledger %s is empty (no author entry 0)" % path)
    return out


def chain_findings(rows):
    """FD-6 integrity findings for a parsed ledger (head-to-entry-0)."""
    findings = []
    prev_line = None
    for i, (entry, line) in enumerate(rows):
        missing = [k for k in ENTRY_FIELDS if k not in entry]
        if entry.get("schema") != LEDGER_SCHEMA or missing:
            findings.append(("FD-6", "entry %d: bad schema or missing fields %s" % (i, missing)))
            prev_line = line
            continue
        if entry["seq"] != i:
            findings.append(("FD-6", "entry %d: seq=%r (deletion/reordering breaks the chain)" % (i, entry["seq"])))
        want = GENESIS if i == 0 else hashlib.sha256(prev_line).hexdigest()
        if entry["prev_sha256"] != want:
            findings.append(("FD-6", "entry %d: prev_sha256 does not verify against its predecessor's bytes" % i))
        if i == 0 and entry["seat_role"] != AUTHOR_ROLE:
            findings.append(("FD-6", "entry 0 seat_role=%r, must be %r (spec §7)" % (entry["seat_role"], AUTHOR_ROLE)))
        prev_line = line
    return findings


def pending_findings(rows):
    """FD-5: runtime entries with no completed output_sha256."""
    return [("FD-5", "entry %d (%s) has no completed output_sha256 (orphan invocation)"
             % (i, e.get("seat_role")))
            for i, (e, _) in enumerate(rows)
            if not (isinstance(e.get("output_sha256"), str) and SHA256_RE.match(e["output_sha256"]))]


def _require_sha(value, what):
    if not (isinstance(value, str) and SHA256_RE.match(value)):
        raise SeatRefusal("ERR_LEDGER", "%s must be a full 64-hex sha256, got %r" % (what, value))


def _check_entry_hygiene(line):
    """RT-14 over the exact bytes about to enter the chain (spec §1)."""
    if account_lint is None:
        raise SeatRefusal("ERR_LEDGER", "kot_common.account_lint unavailable; refusing to write unlinted ledger bytes (RT-14)")
    findings = account_lint(line)
    if findings:
        raise SeatRefusal("ERR_LEDGER", "account-identifying material in ledger entry: %s"
                          % "; ".join(d for d, _ in findings))


def _validate_identity(seat_role, model_id):
    if not SEAT_ROLE_RE.match(seat_role or ""):
        raise SeatRefusal("ERR_LEDGER", "seat_role %r is not a lowercase hyphenated token" % (seat_role,))
    # FD-3: a seat's model id missing or not in the exact dated form.
    if not isinstance(model_id, str) or not model_id or re.search(r"\s", model_id):
        raise SeatRefusal("FD-3", "model id missing or malformed: %r" % (model_id,))
    if not DATED_ID_RE.search(model_id):
        raise SeatRefusal("FD-3", "model id %r carries no dated snapshot token (ASM-2495 proxy bound)" % (model_id,))


def _append_line(path, line):
    with open(path, "ab") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def _amend_last_line(path, old_line, new_line):
    """ASM-2494: complete output_sha256 by amending ONLY the final line."""
    with open(path, "r+b") as f:
        data = f.read()
        if not data.endswith(old_line):
            raise SeatRefusal("FD-6", "ledger tail changed under the invoker; refusing to amend")
        f.seek(len(data) - len(old_line))
        f.truncate()
        f.write(new_line)
        f.flush()
        os.fsync(f.fileno())


# ------------------------------------------------------------------ operations

def init_author(ledger_path, fmap_path, model_id, prompt_sha256, output_sha256,
                invocation_form="authoring-session"):
    """Write entry 0 = the author seat (spec §7: exact dated authoring model
    id). The author's family must itself resolve (FD-1) — an unresolvable
    author makes every later disjointness comparison undecidable."""
    if os.path.exists(ledger_path):
        raise SeatRefusal("ERR_LEDGER", "ledger %s already exists (append-only; entry 0 is written once)" % ledger_path)
    fmap = load_family_map(fmap_path)
    _validate_identity(AUTHOR_ROLE, model_id)
    family = resolve_family(model_id, fmap)
    if family == UNKNOWN:
        raise SeatRefusal("FD-1", "author model id %r resolves UNKNOWN (fails closed, never inferred)" % model_id)
    _require_sha(prompt_sha256, "entry 0 prompt_sha256")
    _require_sha(output_sha256, "entry 0 output_sha256")
    entry = {
        "schema": LEDGER_SCHEMA,
        "seq": 0,
        "prev_sha256": GENESIS,
        "seat_role": AUTHOR_ROLE,
        "model_id": model_id,
        "resolved_family": family,
        "family_map_sha256": fmap["_sha256"],
        "prompt_sha256": prompt_sha256,
        "invocation_form": invocation_form,
        "output_sha256": output_sha256,
    }
    line = entry_line(entry)
    _check_entry_hygiene(line)
    d = os.path.dirname(os.path.abspath(ledger_path))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    _append_line(ledger_path, line)
    return entry


def invoke(ledger_path, fmap_path, seat_role, model_id, prompt_bytes, dispatch,
           invocation_form="headless-one-read"):
    """The ONLY licensed path for an LLM call in any seat role (spec §7).

    Order of operations, all BEFORE any API call:
      1. verify the ledger chain head-to-entry-0 (FD-6) and refuse over a
         pending tail (FD-5 orphan — evidence, never overwritten);
      2. pin check: the map in hand must be the map entry 0 was resolved
         under (extending the map is a contract change, spec §7);
      3. resolve family(seat); refuse FD-1 on UNKNOWN (either side), refuse
         FD-2 on family(seat) == family(entry 0);
      4. append the pending entry;
    then dispatch, then complete output_sha256 on return (ASM-2494).
    Returns (output_bytes, completed_entry)."""
    fmap = load_family_map(fmap_path)
    rows = read_ledger(ledger_path)
    bad = chain_findings(rows)
    if bad:
        raise SeatRefusal(*bad[0])
    orphans = pending_findings(rows)
    if orphans:
        raise SeatRefusal("FD-5", orphans[0][1] + " — sweep/escalate before further invocations")
    author = rows[0][0]
    if author["family_map_sha256"] != fmap["_sha256"]:
        raise SeatRefusal("ERR_FAMILY_MAP",
                          "family map sha %s != entry 0 pin %s (map change = contract change, spec §7)"
                          % (fmap["_sha256"][:12], author["family_map_sha256"][:12]))
    if seat_role == AUTHOR_ROLE:
        raise SeatRefusal("ERR_LEDGER", "seat_role 'author' is entry 0 only")
    _validate_identity(seat_role, model_id)
    author_family = resolve_family(author["model_id"], fmap)
    if author_family != author["resolved_family"]:
        raise SeatRefusal("FD-6", "entry 0 resolved_family %r does not re-resolve (%r) under the pinned map"
                          % (author["resolved_family"], author_family))
    seat_family = resolve_family(model_id, fmap)
    # FD-1 pre-dispatch: any UNKNOWN resolution refuses, no API call.
    if seat_family == UNKNOWN:
        raise SeatRefusal("FD-1", "seat model id %r resolves UNKNOWN — REFUSED, no API call" % model_id)
    if author_family == UNKNOWN:
        raise SeatRefusal("FD-1", "author model id %r resolves UNKNOWN — REFUSED, no API call" % author["model_id"])
    # FD-2 pre-dispatch: family(seat) != family(entry 0), never a string
    # compare on raw ids — both sides go through the pinned resolver.
    if seat_family == author_family:
        raise SeatRefusal("FD-2", "family(%s)=%s == family(author %s) — REFUSED, no API call"
                          % (model_id, seat_family, author["model_id"]))
    if not isinstance(prompt_bytes, bytes):
        raise SeatRefusal("ERR_LEDGER", "prompt must be bytes (the sha-pinned unit)")
    pending = {
        "schema": LEDGER_SCHEMA,
        "seq": len(rows),
        "prev_sha256": hashlib.sha256(rows[-1][1]).hexdigest(),
        "seat_role": seat_role,
        "model_id": model_id,
        "resolved_family": seat_family,
        "family_map_sha256": fmap["_sha256"],
        "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "invocation_form": invocation_form,
        "output_sha256": None,
    }
    pending_line = entry_line(pending)
    completed_probe = dict(pending, output_sha256=GENESIS)  # hygiene-lint the completed shape too
    _check_entry_hygiene(pending_line)
    _check_entry_hygiene(entry_line(completed_probe))
    _append_line(ledger_path, pending_line)          # pre-dispatch append (spec §7)
    output = dispatch(prompt_bytes)                  # the one licensed API call
    if not isinstance(output, bytes):
        raise SeatRefusal("ERR_DISPATCH", "dispatch returned non-bytes; pending entry left as FD-5 evidence")
    completed = dict(pending, output_sha256=hashlib.sha256(output).hexdigest())
    _amend_last_line(ledger_path, pending_line, entry_line(completed))
    return output, completed


def verify(ledger_path):
    """FD-5/FD-6 sweep of a runtime ledger. Returns findings list."""
    rows = read_ledger(ledger_path)
    return chain_findings(rows) + pending_findings(rows)


# ------------------------------------------------------------------ CLI

def _fail(code, msg):
    print("FAIL %s %s" % (code, msg))
    sys.exit(1)


def main(argv=None):
    ap = argparse.ArgumentParser(description="kot-seat-ledger/1 pinned seat invoker (plain-v5 spec §7)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init-author", help="write entry 0 = the author seat")
    p.add_argument("--ledger", required=True)
    p.add_argument("--family-map", required=True)
    p.add_argument("--model-id", required=True, help="exact dated authoring model id, verbatim")
    p.add_argument("--prompt-sha256", required=True)
    p.add_argument("--output-sha256", required=True)
    p.add_argument("--invocation-form", default="authoring-session")

    p = sub.add_parser("invoke", help="ledgered seat invocation (the only licensed LLM-call path)")
    p.add_argument("--ledger", required=True)
    p.add_argument("--family-map", required=True)
    p.add_argument("--seat-role", required=True)
    p.add_argument("--model-id", required=True)
    p.add_argument("--prompt-file", required=True)
    p.add_argument("--output-file", required=True)
    p.add_argument("--dispatch-cmd", required=True,
                   help="argv string; receives the prompt on stdin, must emit the seat output on stdout")
    p.add_argument("--invocation-form", default="headless-one-read")

    p = sub.add_parser("verify", help="FD-5/FD-6 sweep of a runtime ledger")
    p.add_argument("--ledger", required=True)

    args = ap.parse_args(argv)
    try:
        if args.cmd == "init-author":
            entry = init_author(args.ledger, args.family_map, args.model_id,
                                args.prompt_sha256, args.output_sha256, args.invocation_form)
            print("OK entry 0 author=%s family=%s" % (entry["model_id"], entry["resolved_family"]))
        elif args.cmd == "invoke":
            with open(args.prompt_file, "rb") as f:
                prompt = f.read()
            import shlex
            cmd = shlex.split(args.dispatch_cmd)

            def dispatch(prompt_bytes):
                proc = subprocess.run(cmd, input=prompt_bytes, stdout=subprocess.PIPE)
                if proc.returncode != 0:
                    # pending entry stays in the ledger as FD-5 evidence.
                    _fail("ERR_DISPATCH", "dispatch command exited %d; pending entry left for the FD-5 sweep" % proc.returncode)
                return proc.stdout

            output, entry = invoke(args.ledger, args.family_map, args.seat_role,
                                   args.model_id, prompt, dispatch, args.invocation_form)
            with open(args.output_file, "wb") as f:
                f.write(output)
            print("OK seq=%d seat=%s family=%s output_sha256=%s"
                  % (entry["seq"], entry["seat_role"], entry["resolved_family"], entry["output_sha256"]))
        elif args.cmd == "verify":
            findings = verify(args.ledger)
            for code, msg in findings:
                print("FAIL %s %s" % (code, msg))
            if findings:
                sys.exit(1)
            print("OK ledger chain verifies head-to-entry-0; no pending entries")
    except SeatRefusal as e:
        _fail(e.code, str(e).split(" ", 1)[1] if " " in str(e) else str(e))


if __name__ == "__main__":
    main()
