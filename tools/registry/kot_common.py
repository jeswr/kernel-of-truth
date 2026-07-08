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

import hashlib
import json
import re

GENESIS = "0" * 64
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

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
