"""kot_common — shared primitives for the P2 honesty-tooling spine.

Implements the mechanics specified in docs/research-plan/02-data-and-reporting.md
(P2): canonical JSON + frozen-record hashing (§1.1), the hash-chained log (§2),
the RT-14 account-string lint (§1.2 constraint 10), the raw-metrics-only rule
(§2.4), the minimal verdict expression grammar (§3.1), and the Wilson-bound
decidability lint (§1.2 constraint 9).

Stdlib only (Python 3.9). Every check fails closed with a named ERR_* code.

Canonicalisation note (P2 §1.1 "RFC-8785-ish"): UTF-8, sorted keys, no
insignificant whitespace, ensure_ascii=False, NaN/Infinity forbidden. Python's
float repr is used for non-integer numbers; full RFC 8785 ECMAScript number
formatting is NOT implemented — records in this repo keep numbers to integers
and short decimals, where the two coincide.

Chain-byte convention (P2 §2.1 "sha256 of the previous line's exact bytes"):
the hashed unit is the full line INCLUDING its terminating newline, i.e. the
exact byte range the line occupies in the file. Genesis prev_sha256 = 64 zeros.
"""

import copy
import hashlib
import json
import os
import re

GENESIS = "0" * 64
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# ------------------------------------------------------------ corpus-pin recipe
# kot-corpus-hash/1 (pre-sign-off correction c-2026-07-08, replacing the
# GNG-0-seed recipe string that did not reproduce the pinned digests — a
# pin-GENERATION defect surfaced by the F1 exploratory run, seq 0).
# The recipe is a single fixed string; prereg-freeze requires the exact string
# in pins.corpus_hashes._recipe and recomputes every digest at freeze time;
# registry-check --corpus-pins re-verifies frozen records that carry it.
CORPUS_RECIPE = (
    "kot-corpus-hash/1: digest = sha256 over the UTF-8 concatenation of one line "
    "per regular file under data/<corpus>/ (recursive; symlinks and directories "
    "excluded), each line '<sha256-of-file-bytes-hex>  <relpath>\\n' with exactly "
    "two spaces, relpath POSIX-style ('/'-separated) relative to data/<corpus>/, "
    "lines sorted by the UTF-8 byte order of relpath; reference implementation "
    "tools/registry/corpus-pin.py"
)

# Pre-declared placeholder pins: inputs that do not exist at freeze time and are
# completed by ops amendment before any final-phase run (P2 P-9).
PINNED_AT_INPUTS_PREFIX = "PINNED-AT-INPUTS:"


def corpus_hash(root, corpus):
    """kot-corpus-hash/1 digest for data/<corpus>/ under repo root.

    Raises KotError(ERR_P2_CORPUS_PIN) when the corpus directory is missing or
    empty — a pin over nothing is meaningless and fails closed.
    """
    base = os.path.join(root, "data", corpus)
    if not os.path.isdir(base):
        raise KotError("ERR_P2_CORPUS_PIN", "corpus directory data/%s/ does not exist" % corpus)
    lines = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        for name in filenames:
            full = os.path.join(dirpath, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            h = hashlib.sha256()
            with open(full, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            lines.append((rel.encode("utf-8"), h.hexdigest()))
    if not lines:
        raise KotError("ERR_P2_CORPUS_PIN", "corpus directory data/%s/ contains no regular files" % corpus)
    lines.sort(key=lambda t: t[0])
    payload = b"".join(digest.encode("ascii") + b"  " + rel + b"\n" for rel, digest in lines)
    return hashlib.sha256(payload).hexdigest()

# P2 §4 identities / §1.2 constraint 10 (RT-14): in-record identities are
# stable pseudonyms <role>-<n>. Anything else in an identity field is refused.
PSEUDONYM_RE = re.compile(r"^(runner|auditor|coordinator|writer|redteam)-[0-9]+$")
IDENTITY_FIELDS = ("runner", "author", "auditor", "frozen_by", "agent")

# RT-14 fixed account-pattern list. Scanned over the exact bytes that enter
# frozen_sha256 / prev_sha256 ranges. Deliberately blunt: false positives are
# cheap (rewrite the record), false negatives are not.
ACCOUNT_PATTERNS = (
    (re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email address"),
    (re.compile(rb"jeswr", re.IGNORECASE), "maintainer account string"),
    (re.compile(rb"github\.com/[A-Za-z0-9_.-]+"), "account-bearing github URL"),
    (re.compile(rb"sparq-org[/#]"), "account-bearing org issue/repo reference"),
)

# P2 §2.4: a run record's metrics block is RAW only. Fixed forbidden-key list
# (matched case-insensitively against every key at any depth under "metrics").
FORBIDDEN_METRIC_KEYS = frozenset(
    {
        "p", "p_value", "pvalue", "p_holm", "q_value",
        "effect_size", "cohens_d", "cohen_d", "cohens_h",
        "ci", "ci_low", "ci_high", "ci95", "confidence_interval",
        "tost", "tost_pass", "tost_equivalence_pass",
        "holm", "fdr", "reject", "primary_reject",
        "verdict", "pareto", "hull", "wilson_lb", "wilson_bound",
        "significance", "significant", "z_stat", "t_stat",
    }
)

# P2 §3.1 closed verdict vocabulary. Rules in a record may only *declare* the
# first subset; the tooling-only values are emitted by verdict-gen itself.
RULE_VERDICTS = ("PASS", "FAIL", "NULL", "INCONCLUSIVE", "INSTRUMENT-INVALID", "CONSTRUCTION-ANOMALY")
TOOL_VERDICTS = RULE_VERDICTS + ("PASS-PENDING-AUDIT", "INCOMPLETE-DATA", "BUDGET-HALT")


class KotError(Exception):
    """Fail-closed error with a named ERR_* code."""

    def __init__(self, code, msg):
        self.code = code
        super().__init__("%s: %s" % (code, msg))


# ---------------------------------------------------------------- canonical JSON

def canonical_dumps(obj):
    """Canonical JSON string: sorted keys, no whitespace, UTF-8-ready."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def canonical_bytes(obj):
    return canonical_dumps(obj).encode("utf-8")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(obj):
    return sha256_hex(canonical_bytes(obj))


def frozen_hash(record):
    """P2 §1.1: sha256 over canonical bytes with status + frozen_sha256 excluded."""
    stripped = {k: v for k, v in record.items() if k not in ("status", "frozen_sha256")}
    return canonical_sha256(stripped)


def write_canonical_json(path, obj):
    """Committed-file convention: canonical JSON, newline-terminated."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(canonical_dumps(obj) + "\n")


# ---------------------------------------------------------------- RT-14 lint

def account_lint(data):
    """Return [(pattern-description, matched-text), ...] found in `data` bytes."""
    findings = []
    for pattern, desc in ACCOUNT_PATTERNS:
        m = pattern.search(data)
        if m:
            findings.append((desc, m.group(0).decode("utf-8", "replace")))
    return findings


def require_no_account_strings(data, where):
    findings = account_lint(data)
    if findings:
        detail = "; ".join("%s (%r)" % (d, t) for d, t in findings)
        raise KotError("ERR_P2_ACCOUNT_IN_RECORD", "account-identifying material in %s: %s" % (where, detail))


def require_pseudonym(value, field):
    if not isinstance(value, str) or not PSEUDONYM_RE.match(value):
        raise KotError(
            "ERR_P2_ACCOUNT_IN_RECORD",
            "%s=%r is not a pseudonym of the form <role>-<n> (RT-14)" % (field, value),
        )


def check_identity_fields(obj, path=""):
    """Recursively require every identity-bearing field to be a pseudonym."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = "%s/%s" % (path, k)
            if k in IDENTITY_FIELDS and isinstance(v, str):
                require_pseudonym(v, p)
            check_identity_fields(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_identity_fields(v, "%s/%d" % (path, i))


# ---------------------------------------------------------------- raw-metrics rule

def find_forbidden_metric_keys(metrics, path="/metrics"):
    """P2 §2.4: derived/verdict-adjacent statistics may not appear in raw metrics."""
    found = []
    if isinstance(metrics, dict):
        for k, v in metrics.items():
            p = "%s/%s" % (path, k)
            if isinstance(k, str) and k.lower() in FORBIDDEN_METRIC_KEYS:
                found.append(p)
            found.extend(find_forbidden_metric_keys(v, p))
    elif isinstance(metrics, list):
        for i, v in enumerate(metrics):
            found.extend(find_forbidden_metric_keys(v, "%s/%d" % (path, i)))
    return found


# ---------------------------------------------------------------- minimal JSON Schema validator

_SUPPORTED_KEYWORDS = {
    "$schema", "$id", "title", "description",  # annotations, ignored
    "type", "const", "enum", "pattern", "minLength",
    "minItems", "maxItems", "minimum", "maximum",
    "required", "properties", "additionalProperties", "items",
}

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value, tname):
    py = _TYPES[tname]
    if tname in ("number", "integer") and isinstance(value, bool):
        return False  # bool is not a JSON number
    return isinstance(value, py)


def validate_schema(instance, schema, path=""):
    """Minimal JSON-Schema (draft-2020-12 subset) validator.

    Fails closed: an unsupported keyword in the schema is an error, so a schema
    cannot silently promise more than this validator checks.
    Returns a list of violation strings (empty = valid).
    """
    errs = []
    for kw in schema:
        if kw not in _SUPPORTED_KEYWORDS:
            raise KotError("ERR_P2_SCHEMA_KEYWORD", "unsupported schema keyword %r at %s" % (kw, path or "/"))

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(instance, t) for t in types):
            errs.append("%s: expected type %s, got %s" % (path or "/", types, type(instance).__name__))
            return errs
    if "const" in schema and instance != schema["const"]:
        errs.append("%s: expected const %r" % (path or "/", schema["const"]))
    if "enum" in schema and instance not in schema["enum"]:
        errs.append("%s: %r not in enum %s" % (path or "/", instance, schema["enum"]))
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errs.append("%s: %r does not match pattern %r" % (path or "/", instance, schema["pattern"]))
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errs.append("%s: shorter than minLength %d" % (path or "/", schema["minLength"]))
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errs.append("%s: %s < minimum %s" % (path or "/", instance, schema["minimum"]))
        if "maximum" in schema and instance > schema["maximum"]:
            errs.append("%s: %s > maximum %s" % (path or "/", instance, schema["maximum"]))
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errs.append("%s: fewer than minItems %d" % (path or "/", schema["minItems"]))
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errs.append("%s: more than maxItems %d" % (path or "/", schema["maxItems"]))
        if "items" in schema:
            for i, item in enumerate(instance):
                errs.extend(validate_schema(item, schema["items"], "%s/%d" % (path, i)))
    if isinstance(instance, dict):
        for req in schema.get("required", ()):
            if req not in instance:
                errs.append("%s: missing required field %r" % (path or "/", req))
        props = schema.get("properties", {})
        for k, v in instance.items():
            if k in props:
                errs.extend(validate_schema(v, props[k], "%s/%s" % (path, k)))
            elif schema.get("additionalProperties", True) is False:
                errs.append("%s: additional property %r not allowed" % (path or "/", k))
    return errs


# ---------------------------------------------------------------- hash-chained log

class ChainError(KotError):
    def __init__(self, msg):
        super().__init__("ERR_P2_CHAIN", msg)


def read_log(path):
    """Read and chain-verify a results-log JSONL file.

    Returns (records, raw_lines) where raw_lines are the exact byte lines
    (including trailing newline). Raises ChainError on any violation.
    """
    try:
        with open(path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        return [], []
    if not data:
        return [], []
    if not data.endswith(b"\n"):
        raise ChainError("%s: file is not newline-terminated" % path)
    raw_lines = [line + b"\n" for line in data[:-1].split(b"\n")]
    records = []
    prev = GENESIS
    for i, raw in enumerate(raw_lines):
        try:
            rec = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ChainError("%s line %d: unparseable (%s)" % (path, i, e))
        if rec.get("seq") != i:
            raise ChainError("%s line %d: seq=%r, expected %d" % (path, i, rec.get("seq"), i))
        if rec.get("prev_sha256") != prev:
            raise ChainError(
                "%s line %d (seq %d): prev_sha256 mismatch — chain broken (edit or deletion upstream)"
                % (path, i, i)
            )
        records.append(rec)
        prev = sha256_hex(raw)
    return records, raw_lines


def log_tail_sha256(raw_lines):
    return sha256_hex(raw_lines[-1]) if raw_lines else GENESIS


# ---------------------------------------------------------------- JSON pointer + verdict grammar

class MissingMetric(KotError):
    def __init__(self, pointer):
        self.pointer = pointer
        super().__init__("ERR_P2_MISSING_METRIC", "pointer %r missing/null in analysis output" % pointer)


_MISSING = object()


def resolve_pointer(doc, pointer):
    """RFC-6901 JSON pointer; returns _MISSING sentinel when absent."""
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        return _MISSING
    node = doc
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if token not in node:
                return _MISSING
            node = node[token]
        elif isinstance(node, list):
            if not re.match(r"^(0|[1-9][0-9]*)$", token) or int(token) >= len(node):
                return _MISSING
            node = node[int(token)]
        else:
            return _MISSING
    return node


def _eval_val(val, doc):
    if isinstance(val, dict) and "metric" in val:
        v = resolve_pointer(doc, val["metric"])
        if v is _MISSING or v is None:
            raise MissingMetric(val["metric"])
        return v
    if isinstance(val, dict) and "const" in val:
        return val["const"]
    raise KotError("ERR_P2_GRAMMAR", "invalid value node %r (must be {metric} or {const})" % (val,))


def eval_expr(expr, doc):
    """Evaluate a P2 §3.1 verdict expression over an analysis-output document.

    Grammar (the entirety of it — no arithmetic, no strings, no quantifiers):
      expr := {"op":"and"|"or","a":expr,"b":expr} | {"op":"not","a":expr}
            | {"op":"gt"|"gte"|"lt"|"lte"|"eq","a":val,"b":val} | val
      val  := {"metric": <json-pointer>} | {"const": number|boolean}
    """
    if not isinstance(expr, dict):
        raise KotError("ERR_P2_GRAMMAR", "expression must be an object, got %r" % (expr,))
    op = expr.get("op")
    if op is None:
        v = _eval_val(expr, doc)
        if not isinstance(v, bool):
            raise KotError("ERR_P2_GRAMMAR", "non-boolean value %r used as a bare expression" % (v,))
        return v
    if op in ("and", "or"):
        a = eval_expr(expr["a"], doc)
        b = eval_expr(expr["b"], doc)
        return (a and b) if op == "and" else (a or b)
    if op == "not":
        return not eval_expr(expr["a"], doc)
    if op in ("gt", "gte", "lt", "lte", "eq"):
        a = _eval_val(expr["a"], doc)
        b = _eval_val(expr["b"], doc)
        if op == "eq":
            return a == b
        for side, v in (("a", a), ("b", b)):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise KotError("ERR_P2_GRAMMAR", "comparison operand %r (%r) is not a number" % (side, v))
        return {"gt": a > b, "gte": a >= b, "lt": a < b, "lte": a <= b}[op]
    raise KotError("ERR_P2_GRAMMAR", "unknown op %r" % op)


# ---------------------------------------------------------------- RFC-6902 patch (amendment overlay mechanics)

_ARRAY_INDEX_RE = re.compile(r"^(0|[1-9][0-9]*)$")


def _pointer_tokens(pointer, op_index):
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise KotError("ERR_P2_BAD_AMENDMENT",
                       "patch op %d: path %r is not a JSON pointer starting with '/'" % (op_index, pointer))
    return [t.replace("~1", "/").replace("~0", "~") for t in pointer[1:].split("/")]


def _patch_step(node, token, pointer, op_index):
    if isinstance(node, dict):
        if token not in node:
            raise KotError("ERR_P2_BAD_AMENDMENT",
                           "patch op %d: path %r: member %r does not exist" % (op_index, pointer, token))
        return node[token]
    if isinstance(node, list):
        if not _ARRAY_INDEX_RE.match(token) or int(token) >= len(node):
            raise KotError("ERR_P2_BAD_AMENDMENT",
                           "patch op %d: path %r: bad array index %r" % (op_index, pointer, token))
        return node[int(token)]
    raise KotError("ERR_P2_BAD_AMENDMENT",
                   "patch op %d: path %r traverses a non-container" % (op_index, pointer))


def json_patch_apply(doc, patch):
    """Minimal RFC-6902 JSON Patch — the P2 §1.4 amendment-overlay mechanics.

    Supports add / replace / remove only (kot-amend/1 forbids the rest by
    schema). Returns a NEW document (the input is never mutated), so the
    overlay is a pure function of (frozen record, amendment list) and its
    result is deterministic. Fails closed with ERR_P2_BAD_AMENDMENT on any
    unsupported op, unresolvable path, or replace/remove of a nonexistent
    member — never a silent no-op. Per RFC 6902 §4.1 an `add` on an existing
    object member replaces it; POLICY restrictions (ops amendments may only
    fill placeholders / add new pins) live in verdict-gen, not here.
    """
    out = copy.deepcopy(doc)
    for i, op in enumerate(patch):
        if not isinstance(op, dict) or "op" not in op or "path" not in op:
            raise KotError("ERR_P2_BAD_AMENDMENT", "patch op %d is not an {op, path, ...} object" % i)
        action = op["op"]
        if action not in ("add", "replace", "remove"):
            raise KotError("ERR_P2_BAD_AMENDMENT",
                           "patch op %d: unsupported op %r (add/replace/remove only)" % (i, action))
        if action in ("add", "replace") and "value" not in op:
            raise KotError("ERR_P2_BAD_AMENDMENT", "patch op %d (%s): missing value" % (i, action))
        tokens = _pointer_tokens(op["path"], i)
        parent = out
        for token in tokens[:-1]:
            parent = _patch_step(parent, token, op["path"], i)
        last = tokens[-1]
        if isinstance(parent, dict):
            if action == "replace" and last not in parent:
                raise KotError("ERR_P2_BAD_AMENDMENT",
                               "patch op %d: replace target %r does not exist" % (i, op["path"]))
            if action == "remove":
                if last not in parent:
                    raise KotError("ERR_P2_BAD_AMENDMENT",
                                   "patch op %d: remove target %r does not exist" % (i, op["path"]))
                del parent[last]
            else:
                parent[last] = op["value"]
        elif isinstance(parent, list):
            if action == "add" and last == "-":
                parent.append(op["value"])
                continue
            if not _ARRAY_INDEX_RE.match(last):
                raise KotError("ERR_P2_BAD_AMENDMENT",
                               "patch op %d: path %r: bad array index %r" % (i, op["path"], last))
            idx = int(last)
            if action == "add":
                if idx > len(parent):
                    raise KotError("ERR_P2_BAD_AMENDMENT",
                                   "patch op %d: add index %d out of range" % (i, idx))
                parent.insert(idx, op["value"])
            else:
                if idx >= len(parent):
                    raise KotError("ERR_P2_BAD_AMENDMENT",
                                   "patch op %d: %s index %d out of range" % (i, action, idx))
                if action == "remove":
                    del parent[idx]
                else:
                    parent[idx] = op["value"]
        else:
            raise KotError("ERR_P2_BAD_AMENDMENT",
                           "patch op %d: path %r targets inside a non-container" % (i, op["path"]))
    return out


def collect_metric_pointers(expr, out=None):
    """Every {"metric": ptr} leaf in an expression (freeze-time constraint 2)."""
    if out is None:
        out = []
    if isinstance(expr, dict):
        if "metric" in expr and isinstance(expr["metric"], str):
            out.append(expr["metric"])
        for v in expr.values():
            collect_metric_pointers(v, out)
    return out


# ---------------------------------------------------------------- Wilson decidability (constraint 9)

def wilson_lower_bound(p, n, z=1.645):
    """One-sided Wilson score lower bound at the given z (default z=1.645, alpha=0.05)."""
    if n <= 0:
        return 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n)


def check_wilson_gate(gate, where):
    """P2 §1.2 constraint 9: a Wilson-bound gate must be powered for its
    threshold at the planned n under the EXPECTED rate — else the gate is
    undecidable and the freeze is refused."""
    for field in ("threshold", "n_planned", "expected_rate"):
        if field not in gate:
            raise KotError("ERR_P2_UNPOWERED_GATE", "%s: wilson_gate missing %r" % (where, field))
    lb = wilson_lower_bound(float(gate["expected_rate"]), int(gate["n_planned"]))
    if lb <= float(gate["threshold"]):
        raise KotError(
            "ERR_P2_UNPOWERED_GATE",
            "%s: Wilson lower bound at expected_rate=%s, n=%s is %.5f <= threshold %s — "
            "gate undecidable at the planned n (RT-4)"
            % (where, gate["expected_rate"], gate["n_planned"], lb, gate["threshold"]),
        )
    return lb


# ================================================================ REUSE machinery
# Delta D9 (docs/next/resource-optimization-plan.md §3, revision-1 post-audit;
# docs/next/research-engine.md §5.1). One implementation, four call sites:
# prereg-freeze (freeze-time RC checks + cell-collision refusal), log-append
# (event:"reuse" witness lines), verdict-gen (consumption eligibility), and
# registry-check / reuse-check audit (re-verification + producer-chain
# traversal). The RC conditions are defined in the plan §3.3 (RC-1..RC-8);
# every check here cites its RC number. Fail closed with named ERR_* codes.
#
# RATIFICATION INTERLOCK: nothing reuse-PERMISSIVE operates until the
# maintainer commits registry/reuse-ratification.json pinning the sha256 of
# the CURRENT ruling text (editing the ruling voids the ratification). The
# reuse-RESTRICTIVE side (collision refusal, the binding pre-spend gate) is
# live unconditionally.

REUSE_RATIFICATION_RELPATH = os.path.join("registry", "reuse-ratification.json")
REUSE_PLAN_RELPATH = os.path.join("docs", "next", "resource-optimization-plan.md")
# RC-1: the ONLY lawful selection rule — cell-complete, never row/seed-picked.
REUSE_SELECTION_RULE = "all-final-rows-matching-declared-cells"
# RC-7: the closed set of DATA-BLIND comparator-selection bases (Case B).
RC7_BASES = ("mandatory-baseline-law", "exhaustive-declared-family", "prior-frozen-rule")
REUSE_ROLES = ("prospective", "comparator")
RC5_KINDS = ("overlap-rerun", "deterministic-cpu-recompute")
_MAINTAINER_RE = re.compile(r"^maintainer(-[0-9]+)?$")
_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_REV_PIN_RE = re.compile(r"@([0-9a-f]{40}|[0-9a-f]{64})$")


def _file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def reuse_ratified(root):
    """(ok, detail). True iff registry/reuse-ratification.json exists, names the
    maintainer, and pins the sha256 of the CURRENT ruling doc bytes."""
    path = os.path.join(root, REUSE_RATIFICATION_RELPATH)
    if not os.path.isfile(path):
        return False, "%s does not exist — the reuse ruling is not ratified" % REUSE_RATIFICATION_RELPATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            r = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return False, "%s unparseable: %s" % (REUSE_RATIFICATION_RELPATH, e)
    if r.get("schema_version") != "kot-reuse-ratify/1":
        return False, "ratification schema_version %r != kot-reuse-ratify/1" % r.get("schema_version")
    if not (isinstance(r.get("by"), str) and _MAINTAINER_RE.match(r["by"])):
        return False, "ratification 'by'=%r is not maintainer[-N]" % r.get("by")
    plan_path = os.path.join(root, r.get("plan_path", REUSE_PLAN_RELPATH))
    if not os.path.isfile(plan_path):
        return False, "ratified plan path %r missing" % r.get("plan_path")
    got = _file_sha256(plan_path)
    if got != r.get("plan_sha256"):
        return False, ("ratification pins plan sha %r but current %s bytes hash %s — the ruling "
                       "changed since ratification; re-ratify" % (r.get("plan_sha256"),
                                                                  r.get("plan_path", REUSE_PLAN_RELPATH), got))
    return True, "ratified by %s on %s" % (r["by"], r.get("date"))


def require_reuse_ratified(root, what):
    ok, detail = reuse_ratified(root)
    if not ok:
        raise KotError("ERR_P2_REUSE_UNRATIFIED",
                       "%s requires maintainer ratification of the reuse ruling: %s" % (what, detail))


def is_real_pin(value):
    """A pin value that PROVES identity: bare 40/64-hex, or <name>@<40/64-hex>.
    Placeholders (PINNED-AT-INPUTS:*, POST-F2-INFRA-OPEN, anything else) are
    indeterminate — fail-closed for identity comparisons."""
    if not isinstance(value, str):
        return False
    return bool(SHA256_RE.match(value) or _HEX40_RE.match(value) or _REV_PIN_RE.search(value))


def derive_artifact_rows(root, include_all=False):
    """The artifact inventory as a PURE FUNCTION of results-log/*.jsonl +
    registry/verdicts/ — derived LIVE (never from the committed ledger file, so
    staleness cannot weaken a gate). One row per logged run row (final-phase
    unless include_all), carrying the identity axes RC-2 compares: pins, seed,
    config_sha256, impl pins (config keys ending _sha256), and row_sha256 (the
    exact line bytes incl. newline — the RC-1 row-hash pin a consumer freezes).
    Chain integrity is enforced by read_log (fail closed)."""
    import glob as _glob
    results_dir = os.path.join(root, "results-log")
    verdicts_dir = os.path.join(root, "registry", "verdicts")
    if not os.path.isdir(results_dir):
        return []  # nothing logged yet — an empty inventory, not an error
    verdicts = {
        os.path.splitext(os.path.basename(p))[0]
        for p in _glob.glob(os.path.join(verdicts_dir, "*.json"))
    }
    rows = []
    for path in sorted(_glob.glob(os.path.join(results_dir, "*.jsonl"))):
        exp = os.path.splitext(os.path.basename(path))[0]
        records, raw_lines = read_log(path)
        for rec, raw in zip(records, raw_lines):
            if rec.get("event") != "run" and not include_all:
                continue
            phase = rec.get("phase")
            if phase != "final" and not include_all:
                continue
            metrics = rec.get("metrics") or {}
            config = rec.get("config") or {}
            per_item = sorted(k for k, v in metrics.items() if isinstance(v, list))
            n_items = None
            for k in ("item_correct", "record_caught"):
                if isinstance(metrics.get(k), list):
                    n_items = len(metrics[k])
                    break
            pins = rec.get("pins_observed") or {}
            rows.append({
                "schema_version": "kot-artifact/2",
                "experiment": exp,
                "log_path": os.path.relpath(path, root),
                "seq": rec.get("seq"),
                "phase": phase,
                "event": rec.get("event"),
                "exit": rec.get("exit"),
                "config": config,
                "config_sha256": rec.get("config_sha256") or canonical_sha256(config),
                "impl_pins": {k: v for k, v in config.items()
                              if isinstance(k, str) and k.endswith("_sha256")},
                "seed": config.get("seed"),
                "n_items": n_items,
                "metrics_logged": sorted(metrics.keys()),
                "per_item_fields": per_item,
                "pins": {
                    "encoder_hash": pins.get("encoder_hash"),
                    "corpus_hashes": pins.get("corpus_hashes"),
                    "model_revisions": pins.get("model_revisions"),
                    "other_pins": sorted(
                        k for k in pins
                        if k not in ("encoder_hash", "corpus_hashes", "model_revisions")
                    ),
                },
                "prereg_hash": rec.get("prereg_hash"),
                "row_sha256": sha256_hex(raw),
                "unblinded": exp in verdicts,
                "ts": rec.get("ts"),
            })
    rows.sort(key=lambda r: (r["experiment"], r["seq"] if r["seq"] is not None else -1))
    return rows


def pin_axis_compare(record_pins, row_pins):
    """RC-2 identity classification between a record's pins block and a logged
    row's observed pins, per axis (corpus, model, encoder). Returns
    {"corpus": s, "model": s, "encoder": s, "overall": s} with each state in
    {"identical", "different", "indeterminate"}.

    Fail-closed semantics: an axis is "different" ONLY when both sides carry
    real (hash-proving) pins on shared names, none match, and the record side
    has NO placeholder that could later resolve to the row's identity.
    Anything unprovable is "indeterminate". overall = "different" iff ANY axis
    is provably different (a proven mismatch on one identity axis means the
    cell is a different experiment, not reuse — the audit's false-positive
    fix); else "identical" iff at least one axis proves identity and none is
    indeterminate-with-no-evidence... conservatively: "identical" iff >=1 axis
    identical and no axis different; else "indeterminate"."""
    rec_pins = record_pins or {}
    r_pins = row_pins or {}

    def axis(rec_map, row_map):
        rec_map = rec_map if isinstance(rec_map, dict) else {}
        row_map = row_map if isinstance(row_map, dict) else {}
        shared = [n for n in rec_map if n in row_map and not n.startswith("_")]
        rec_has_placeholder = any(
            not is_real_pin(v) for k, v in rec_map.items() if not k.startswith("_"))
        if not shared:
            return "indeterminate" if (rec_map or row_map) else "indeterminate"
        any_match, any_real_mismatch = False, False
        for n in shared:
            a, b = rec_map[n], row_map[n]
            if is_real_pin(a) and is_real_pin(b):
                if a == b:
                    any_match = True
                else:
                    any_real_mismatch = True
        if any_real_mismatch:
            return "different" if not rec_has_placeholder else "indeterminate"
        if any_match:
            return "identical"
        return "indeterminate"

    corpus = axis(rec_pins.get("corpus_hashes"), r_pins.get("corpus_hashes"))
    model = axis(rec_pins.get("model_revisions"), r_pins.get("model_revisions"))
    enc_a, enc_b = rec_pins.get("encoder_hash"), r_pins.get("encoder_hash")
    if is_real_pin(enc_a) and is_real_pin(enc_b):
        encoder = "identical" if enc_a == enc_b else "different"
    else:
        encoder = "indeterminate"
    # overall: "different" iff ANY axis provably differs (a proven mismatch on
    # one identity axis means a different experiment, not reuse); "identical"
    # only when BOTH the item-universe axis (corpus) and the checkpoint axis
    # (model) prove identity — the shared encoder pin alone proves nothing
    # (every record pins it); anything else is "indeterminate" (fail closed).
    states = (corpus, model, encoder)
    if "different" in states:
        overall = "different"
    elif corpus == "identical" and model == "identical":
        overall = "identical"
    else:
        overall = "indeterminate"
    return {"corpus": corpus, "model": model, "encoder": encoder, "overall": overall}


def _cell_matches_config(cell, config):
    """A declared cell matches a row config iff EVERY key the cell names equals
    the config's value (the cell is a config selector; omitted keys are free)."""
    return all(config.get(k) == v for k, v in cell.items())


def record_grid_cells(record):
    """The record's declared arm x rung grid (freeze-collision surface)."""
    design = record.get("design") or {}
    ivs = {iv.get("name"): iv.get("levels", []) for iv in design.get("independent_vars", [])}
    arms = ivs.get("arm", [])
    rungs = ivs.get("rung", design.get("scale_rungs", [])) or [None]
    return [(a, r) for a in arms for r in rungs]


def _covered(arm, rung, cell_lists):
    for cells in cell_lists:
        for c in cells:
            if c.get("arm") != arm:
                continue
            if "rung" not in c or c.get("rung") == rung:
                return True
    return False


def reuse_collisions(record, root):
    """Freeze-time COLLISION surface (D9): every (arm, rung) cell of the record
    that the live results-log inventory already holds at identical or
    unproven-different pins, and that is NOT covered by a reused_from block or
    a reuse_overrides entry. Derived LIVE from results-log (never the committed
    ledger). Cells whose pin identity is PROVABLY different are not collisions
    (the audit's false-positive fix). The record's own log rows never collide
    with itself. Returns [{arm, rung, producers, identity}]."""
    rows = derive_artifact_rows(root)
    rec_id = record.get("id")
    rec_pins = record.get("pins") or {}
    declared = [b.get("cells", []) for b in record.get("reused_from", []) or []]
    overridden = [o.get("cells", []) for o in record.get("reuse_overrides", []) or []]
    out = []
    for arm, rung in record_grid_cells(record):
        # a logged row with NO rung in its config matches ANY rung cell
        # (identity indeterminate on the rung axis — fail closed)
        hits = [r for r in rows
                if r["experiment"] != rec_id
                and (r.get("config") or {}).get("arm") == arm
                and (rung is None or "rung" not in (r.get("config") or {})
                     or (r.get("config") or {}).get("rung") == rung)]
        if not hits:
            continue
        classes = {}
        for r in hits:
            cls = pin_axis_compare(rec_pins, r.get("pins"))["overall"]
            classes.setdefault(cls, set()).add(r["experiment"])
        colliding = sorted(classes.get("identical", set()) | classes.get("indeterminate", set()))
        if not colliding:
            continue
        if _covered(arm, rung, declared) or _covered(arm, rung, overridden):
            continue
        identity = "identical" if classes.get("identical") else "indeterminate"
        out.append({"arm": arm, "rung": rung, "producers": colliding, "identity": identity})
    return out


def _producer_integrity(root, block):
    """RC-6 link integrity: producer is frozen, index sha equals the declared
    producer_frozen_sha256, the producer record's bytes have not drifted, and
    its chained log verifies. Returns (producer_record, log_records, raw_lines)."""
    producer = block.get("producer")
    where = "reused_from[producer=%s]" % producer
    index_path = os.path.join(root, "registry", "frozen-index.json")
    if not os.path.isfile(index_path):
        raise KotError("ERR_P2_REUSE_PRODUCER", "%s: no frozen-index.json" % where)
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    if producer not in index:
        raise KotError("ERR_P2_REUSE_PRODUCER",
                       "%s: producer is not FROZEN — only frozen producers' logs are consumable" % where)
    if index[producer] != block.get("producer_frozen_sha256"):
        raise KotError("ERR_P2_REUSE_PRODUCER",
                       "%s: declared producer_frozen_sha256 %r != frozen-index %s"
                       % (where, block.get("producer_frozen_sha256"), index[producer]))
    prod_path = os.path.join(root, "registry", "experiments", "%s.json" % producer)
    if not os.path.isfile(prod_path):
        raise KotError("ERR_P2_REUSE_PRODUCER", "%s: producer record file missing" % where)
    with open(prod_path, "r", encoding="utf-8") as f:
        prod = json.load(f)
    if frozen_hash(prod) != index[producer]:
        raise KotError("ERR_P2_REUSE_PRODUCER",
                       "%s: producer record bytes drifted from frozen-index" % where)
    expected_log = "results-log/%s.jsonl" % producer
    if block.get("producer_log_path") != expected_log:
        raise KotError("ERR_P2_REUSE_BLOCK",
                       "%s: producer_log_path %r != %s" % (where, block.get("producer_log_path"), expected_log))
    log_records, raw_lines = read_log(os.path.join(root, expected_log))  # ERR_P2_CHAIN on tamper
    return prod, log_records, raw_lines


def _matching_final_rows(log_records, raw_lines, frozen_sha, cells):
    out = []
    for rec, raw in zip(log_records, raw_lines):
        if rec.get("event") != "run" or rec.get("phase") != "final" or rec.get("exit") != "ok":
            continue
        if rec.get("prereg_hash") != frozen_sha:
            continue
        cfg = rec.get("config") or {}
        if any(_cell_matches_config(c, cfg) for c in cells):
            out.append((rec, raw))
    return out


def _rc2_pin_identity(where, consumer_pins, producer_pins, at_freeze):
    """RC-2: exact-pin identity on every SHARED name. A real-vs-real mismatch
    is a hard refusal at any time (not reuse — a different experiment). A
    consumer-side placeholder on a shared name is tolerated at freeze (P-9
    pre-declared inputs, completed by ops amendment) and REFUSED at
    consumption time (verdict) — identity must be proven before rows flow.
    At consumption time the check is AFFIRMATIVE: at least one shared corpus
    name must prove identity real-vs-real (a row carrying no provable corpus
    identity, or corpora under disjoint names, cannot be consumed)."""
    c = consumer_pins or {}
    p = producer_pins or {}

    def check_map(axis, cmap, pmap):
        cmap = cmap if isinstance(cmap, dict) else {}
        pmap = pmap if isinstance(pmap, dict) else {}
        proven = 0
        for name in sorted(set(cmap) & set(pmap)):
            if name.startswith("_"):
                continue
            a, b = cmap[name], pmap[name]
            if is_real_pin(a) and is_real_pin(b):
                if a != b:
                    raise KotError("ERR_P2_REUSE_RC2",
                                   "%s: %s pin %r differs (consumer %s != producer %s) — not reuse; "
                                   "a fresh run or a different declared experiment is required"
                                   % (where, axis, name, a, b))
                proven += 1
            elif not at_freeze:
                raise KotError("ERR_P2_REUSE_RC2",
                               "%s: %s pin %r is not identity-proving on both sides at consumption "
                               "time (consumer %r / producer %r) — fill placeholders by ops "
                               "amendment before the verdict" % (where, axis, name, a, b))
        return proven

    corpus_proven = check_map("corpus", c.get("corpus_hashes"), p.get("corpus_hashes"))
    check_map("model", c.get("model_revisions"), p.get("model_revisions"))
    if not at_freeze and corpus_proven == 0:
        raise KotError("ERR_P2_REUSE_RC2",
                       "%s: no shared corpus name proves identity real-vs-real at consumption "
                       "time — RC-2 identity must be AFFIRMATIVELY established, not merely "
                       "un-contradicted" % where)
    ce, pe = c.get("encoder_hash"), p.get("encoder_hash")
    if ce is not None and pe is not None:
        if is_real_pin(ce) and is_real_pin(pe):
            if ce != pe:
                raise KotError("ERR_P2_REUSE_RC2", "%s: encoder_hash differs" % where)
        elif not at_freeze:
            raise KotError("ERR_P2_REUSE_RC2", "%s: encoder_hash not identity-proving at consumption" % where)


def _stratum(cell):
    return "%s|%s" % (cell.get("arm"), cell.get("rung", "-"))


def _check_rc5(where, block, record, matched_rows, root, mode):
    """RC-5 (tightened, revision-1): the batch-effect gate must cover EACH
    material (arm x rung) stratum of the consumed cells for THIS producer, or
    carry an explicit representativeness justification per uncovered stratum,
    frozen in the record. The CPU waiver requires a committed recompute of the
    EXACT consumed outputs with matching content hashes — citing
    deterministic_repeat_identical alone licenses nothing."""
    rc5 = block.get("rc5")
    if not isinstance(rc5, dict):
        raise KotError("ERR_P2_REUSE_RC5", "%s: rc5 block missing (overlap-rerun or "
                                           "deterministic-cpu-recompute)" % where)
    kind = rc5.get("kind")
    if kind not in RC5_KINDS:
        raise KotError("ERR_P2_REUSE_RC5", "%s: rc5.kind %r not in %s" % (where, kind, RC5_KINDS))
    output_fields = set(((record.get("pins") or {}).get("analysis_script") or {}).get("output_fields", []))
    if kind == "overlap-rerun":
        cells = rc5.get("cells") or []
        if not cells:
            raise KotError("ERR_P2_REUSE_RC5", "%s: overlap-rerun declares no overlap cells" % where)
        n = rc5.get("n_items")
        if not isinstance(n, int) or n < 50:
            raise KotError("ERR_P2_REUSE_RC5", "%s: overlap n_items %r < 50" % (where, n))
        ptr = rc5.get("agreement_metric_pointer")
        if not (isinstance(ptr, str) and ptr.startswith("/")):
            raise KotError("ERR_P2_REUSE_RC5", "%s: agreement_metric_pointer %r is not a JSON pointer"
                           % (where, ptr))
        if ptr not in output_fields:
            raise KotError("ERR_P2_REUSE_RC5",
                           "%s: agreement_metric_pointer %s not in pins.analysis_script.output_fields"
                           % (where, ptr))
        if not isinstance(rc5.get("agreement_bound"), (int, float)) or isinstance(rc5.get("agreement_bound"), bool):
            raise KotError("ERR_P2_REUSE_RC5", "%s: agreement_bound must be a number" % where)
        # a miss must be able to fire INSTRUMENT-INVALID, never hypothesis evidence
        fires = any(r.get("verdict") == "INSTRUMENT-INVALID" and ptr in canonical_dumps(r.get("when", {}))
                    for r in record.get("verdict_rules", []))
        if not fires:
            raise KotError("ERR_P2_REUSE_RC5",
                           "%s: no INSTRUMENT-INVALID verdict rule references %s — an RC-5 miss "
                           "must score INSTRUMENT-INVALID for the reused arms" % (where, ptr))
        consumed_strata = {_stratum(c) for c in block.get("cells", [])}
        overlap_strata = {_stratum(c) for c in cells}
        justified = rc5.get("representativeness_justification") or {}
        for s in sorted(consumed_strata):
            if s in overlap_strata:
                continue
            j = justified.get(s)
            if not (isinstance(j, str) and j.strip()):
                raise KotError("ERR_P2_REUSE_RC5",
                               "%s: consumed stratum %r has no overlap cell and no representativeness "
                               "justification (RC-5 tightened: per producer AND per arm/rung stratum)"
                               % (where, s))
    else:  # deterministic-cpu-recompute
        for field in ("recompute_command", "recompute_run_log"):
            if not (isinstance(rc5.get(field), str) and rc5[field].strip()):
                raise KotError("ERR_P2_REUSE_RC5", "%s: waiver missing %s" % (where, field))
        coh = rc5.get("consumed_output_hashes")
        if not (isinstance(coh, dict) and isinstance(coh.get("path"), str)
                and isinstance(coh.get("sha256"), str)):
            raise KotError("ERR_P2_REUSE_RC5",
                           "%s: waiver missing consumed_output_hashes {path, sha256}" % where)
        full = os.path.join(root, coh["path"])
        if not os.path.isfile(full):
            raise KotError("ERR_P2_REUSE_RC5", "%s: %s does not exist" % (where, coh["path"]))
        got = _file_sha256(full)
        if got != coh["sha256"]:
            raise KotError("ERR_P2_REUSE_RC5", "%s: %s sha256 %s != pinned %s"
                           % (where, coh["path"], got, coh["sha256"]))
        with open(full, "r", encoding="utf-8") as f:
            try:
                recomputed = json.load(f)
            except json.JSONDecodeError as e:
                raise KotError("ERR_P2_REUSE_RC5", "%s: %s unparseable: %s" % (where, coh["path"], e))
        fields = block.get("per_item_fields", [])
        for rec, _raw in matched_rows:
            seq = str(rec.get("seq"))
            metrics = rec.get("metrics") or {}
            if metrics.get("deterministic_repeat_identical") is not True:
                raise KotError("ERR_P2_REUSE_RC5",
                               "%s: seq %s does not log deterministic_repeat_identical=true — the CPU "
                               "waiver applies only to determinism-witnessing producers" % (where, seq))
            want = canonical_sha256({f_: metrics.get(f_) for f_ in fields})
            if recomputed.get(seq) != want:
                raise KotError("ERR_P2_REUSE_RC5",
                               "%s: recomputed consumed-output hash for seq %s (%r) != hash of the exact "
                               "consumed fields in the log (%s) — bit-identity NOT proven; the waiver "
                               "requires recomputing the exact consumed outputs" % (where, seq,
                                                                                    recomputed.get(seq), want))


def verify_reuse_block(root, record, block, mode):
    """Verify ONE reused_from block. mode: 'freeze' | 'verdict' | 'append' |
    'recheck'. Returns (matched_rows, seqs) where matched_rows = [(record, raw)].
    Raises KotError (fail closed) on any RC violation this mode can check."""
    if mode not in ("freeze", "verdict", "append", "recheck"):
        raise KotError("ERR_P2_REUSE_BLOCK", "unknown reuse verification mode %r" % mode)
    producer = block.get("producer")
    where = "reused_from[producer=%s]" % producer
    if producer == record.get("id"):
        raise KotError("ERR_P2_REUSE_BLOCK", "%s: a record cannot reuse its own log" % where)
    role = block.get("role")
    if role not in REUSE_ROLES:
        raise KotError("ERR_P2_REUSE_BLOCK", "%s: role %r not in %s" % (where, role, REUSE_ROLES))
    if block.get("selection_rule") != REUSE_SELECTION_RULE:
        raise KotError("ERR_P2_REUSE_BLOCK",
                       "%s: selection_rule must be %r (RC-1: cell-complete, never row/seed-picked)"
                       % (where, REUSE_SELECTION_RULE))
    cells = block.get("cells") or []
    if not cells or not all(isinstance(c, dict) and isinstance(c.get("arm"), str) for c in cells):
        raise KotError("ERR_P2_REUSE_BLOCK", "%s: cells must be non-empty objects each naming an arm" % where)
    fields = block.get("per_item_fields") or []
    if not fields:
        raise KotError("ERR_P2_REUSE_RC3", "%s: per_item_fields is empty — a consumer DV must be a "
                                           "pure function of declared producer fields" % where)
    if not isinstance(block.get("outcome_selected_arms"), bool):
        raise KotError("ERR_P2_REUSE_SURVIVOR",
                       "%s: outcome_selected_arms must be declared true/false (RC-8)" % where)

    prod, log_records, raw_lines = _producer_integrity(root, block)
    frozen_sha = block["producer_frozen_sha256"]
    matched = _matching_final_rows(log_records, raw_lines, frozen_sha, cells)
    matched_seqs = [rec["seq"] for rec, _ in matched]
    unblinded_now = os.path.isfile(os.path.join(root, "registry", "verdicts", "%s.json" % producer))

    if role == "prospective":
        if "rows" in block:
            raise KotError("ERR_P2_REUSE_BLOCK",
                           "%s: prospective (Case A) blocks pin no rows — the row set is derived as "
                           "all matching final rows once the producer lands" % where)
        if block.get("producer_unblinded") is not False:
            raise KotError("ERR_P2_REUSE_RC4",
                           "%s: prospective block must declare producer_unblinded:false" % where)
        if mode == "freeze":
            has_final = any(r.get("event") == "run" and r.get("phase") == "final" for r in log_records)
            if has_final or unblinded_now:
                raise KotError("ERR_P2_REUSE_BLOCK",
                               "%s: producer already has final-phase data (final rows=%s, unblinded=%s) — "
                               "this is retrospective consumption; declare role:comparator under "
                               "RC-4/RC-7 or run fresh" % (where, has_final, unblinded_now))
        if mode == "verdict":
            if not matched:
                raise KotError("ERR_P2_REUSE_ROWS",
                               "%s: prospective block has no matching producer rows at consumption time"
                               % where)
    else:  # comparator (Case B)
        rows_pin = block.get("rows")
        if not (isinstance(rows_pin, dict) and isinstance(rows_pin.get("seqs"), list)
                and isinstance(rows_pin.get("row_hashes"), list)
                and len(rows_pin["seqs"]) == len(rows_pin["row_hashes"])
                and rows_pin["seqs"]):
            raise KotError("ERR_P2_REUSE_BLOCK",
                           "%s: comparator block must pin rows {seqs, row_hashes} of equal non-zero "
                           "length (RC-1)" % where)
        if block.get("producer_unblinded") is not True:
            raise KotError("ERR_P2_REUSE_RC4",
                           "%s: comparator blocks exist for already-unblinded producers; declare "
                           "producer_unblinded:true (disclosure, RC-4) — for not-yet-run producers "
                           "use role:prospective" % where)
        if mode == "freeze" and not unblinded_now:
            raise KotError("ERR_P2_REUSE_RC4",
                           "%s: declared producer_unblinded:true but no verdict exists — the "
                           "disclosure must be accurate at freeze" % where)
        declared = sorted(rows_pin["seqs"])
        if declared != sorted(matched_seqs):
            raise KotError("ERR_P2_REUSE_ROWS",
                           "%s: declared seqs %s != all matching final rows %s — RC-1 requires the "
                           "COMPLETE cell (no subset, no superset)" % (where, declared, sorted(matched_seqs)))
        by_seq = {rec["seq"]: raw for rec, raw in matched}
        for seq, want in zip(rows_pin["seqs"], rows_pin["row_hashes"]):
            got = sha256_hex(by_seq[seq])
            if got != want:
                raise KotError("ERR_P2_REUSE_ROWS",
                               "%s: seq %d line-bytes sha %s != pinned %s" % (where, seq, got, want))
        # RC-7: data-blind comparator/config selection basis (Case B, critical fix)
        sel = block.get("comparator_selection")
        if not isinstance(sel, dict):
            raise KotError("ERR_P2_REUSE_RC7",
                           "%s: comparator_selection missing — the comparator family AND its "
                           "config-selection rule must be fixed by a data-blind rule (RC-7)" % where)
        if sel.get("basis") not in RC7_BASES:
            raise KotError("ERR_P2_REUSE_RC7",
                           "%s: comparator_selection.basis %r not in %s — a basis selected after "
                           "unblinding makes the primary exploratory unless freshly replicated"
                           % (where, sel.get("basis"), RC7_BASES))
        ref = sel.get("ref") or {}
        if not (isinstance(ref.get("path"), str) and isinstance(ref.get("sha256"), str)):
            raise KotError("ERR_P2_REUSE_RC7", "%s: comparator_selection.ref {path, sha256} required" % where)
        full = os.path.join(root, ref["path"])
        if not os.path.isfile(full):
            raise KotError("ERR_P2_REUSE_RC7", "%s: comparator_selection.ref path %r missing"
                           % (where, ref["path"]))
        if _file_sha256(full) != ref["sha256"]:
            raise KotError("ERR_P2_REUSE_RC7", "%s: comparator_selection.ref %s sha mismatch — the "
                                               "data-blind rule's bytes must be pinned" % (where, ref["path"]))
        if not (isinstance(sel.get("rule_verbatim"), str) and sel["rule_verbatim"].strip()):
            raise KotError("ERR_P2_REUSE_RC7", "%s: comparator_selection.rule_verbatim required" % where)

    # RC-8: survivor/slope rule (critical fix — f7 loophole)
    if block.get("outcome_selected_arms") is True:
        sai = block.get("selection_adjusted_inference")
        if not (isinstance(sai, dict) and isinstance(sai.get("method"), str) and sai["method"].strip()
                and isinstance(sai.get("analysis_anchor"), str) and sai["analysis_anchor"].startswith("/")):
            raise KotError("ERR_P2_REUSE_SURVIVOR",
                           "%s: outcome_selected_arms:true requires pre-specified "
                           "selection_adjusted_inference {method, analysis_anchor} (RC-8) — otherwise "
                           "rerun the lower rungs fresh, or keep the slope component exploratory "
                           "(outside reused_from entirely)" % where)
        anchors = set(((record.get("pins") or {}).get("analysis_script") or {}).get("output_fields", []))
        if sai["analysis_anchor"] not in anchors:
            raise KotError("ERR_P2_REUSE_SURVIVOR",
                           "%s: selection_adjusted_inference.analysis_anchor %s not in "
                           "pins.analysis_script.output_fields — the adjustment must live in the "
                           "pinned analysis" % (where, sai["analysis_anchor"]))

    # RC-2 pin identity (freeze: real-vs-real must match, placeholders deferred;
    # verdict: identity must be proven) + RC-3 field computability over rows.
    check_rows = matched if role == "comparator" or mode in ("verdict", "recheck") else []
    at_freeze = mode in ("freeze", "append", "recheck")
    if role == "prospective" and mode == "freeze":
        _rc2_pin_identity(where, record.get("pins"), prod.get("pins"), at_freeze=True)
    for rec, _raw in check_rows:
        _rc2_pin_identity(where + "[seq=%s]" % rec.get("seq"), record.get("pins"),
                          rec.get("pins_observed"), at_freeze=at_freeze)
        metrics = rec.get("metrics") or {}
        for f_ in fields:
            if not isinstance(metrics.get(f_), list):
                raise KotError("ERR_P2_REUSE_RC3",
                               "%s: seq %s does not log per-item field %r as a list — the consumer DV "
                               "is not computable from this row (RC-3)" % (where, rec.get("seq"), f_))

    # RC-5 batch-effect gate / CPU waiver (skipped for prospective-at-freeze
    # only when no rows exist yet to hash; shape checks still run).
    if role == "comparator" or (mode in ("verdict", "recheck") and matched):
        _check_rc5(where, block, record, matched, root, mode)
    elif mode == "freeze":
        _check_rc5(where, block, record, [], root, mode)

    return matched, sorted(matched_seqs)


def check_record_reuse(record, root, mode):
    """Record-level RC checks over ALL reused_from blocks + the RATIFICATION
    interlock. Returns [{'block': b, 'rows': [(rec, raw)], 'seqs': [...]}].
    mode as in verify_reuse_block."""
    blocks = record.get("reused_from") or []
    if not blocks:
        return []
    if record.get("schema_version") != "kot-reg/2":
        raise KotError("ERR_P2_REUSE_BLOCK",
                       "reused_from requires schema kot-reg/2 (the machine-enforced wire format); "
                       "kot-reg/1 has no lawful reuse surface")
    if mode in ("freeze", "verdict", "append"):
        require_reuse_ratified(root, "consuming logged rows (reused_from)")
    results = []
    for block in blocks:
        rows, seqs = verify_reuse_block(root, record, block, mode)
        results.append({"block": block, "rows": rows, "seqs": seqs})
    # RC-4 record-level: when ANY block consumes already-unblinded rows, at
    # least one declared arm must be fresh (no block covers it at any rung).
    if any(b.get("producer_unblinded") for b in blocks):
        arms = set()
        for iv in (record.get("design") or {}).get("independent_vars", []):
            if iv.get("name") == "arm":
                arms = set(iv.get("levels", []))
        reused_arms = {c.get("arm") for b in blocks for c in b.get("cells", [])}
        unknown = reused_arms - arms
        if unknown:
            raise KotError("ERR_P2_REUSE_RC4",
                           "reused cells name arms not in the design: %s" % sorted(unknown))
        if arms and not (arms - reused_arms):
            raise KotError("ERR_P2_REUSE_RC4",
                           "every declared arm is covered by reused rows — RC-4 requires >=1 "
                           "freshly-run arm in the primary contrast when consuming already-"
                           "unblinded data")
    # reuse_overrides shape (proceed-with-reason, machine-recorded)
    for i, o in enumerate(record.get("reuse_overrides") or []):
        if not (isinstance(o, dict) and o.get("cells") and isinstance(o.get("reason"), str)
                and o["reason"].strip()):
            raise KotError("ERR_P2_REUSE_BLOCK",
                           "reuse_overrides[%d] must carry cells + a non-empty reason" % i)
    return results
