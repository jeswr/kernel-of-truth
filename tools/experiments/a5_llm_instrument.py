#!/usr/bin/env python3
"""a5_llm_instrument — the a5-llm engine-vs-LLM head-to-head instrument
(registry id `a5-llm`, DRAFT kot-reg/2; prereg anchor docs/design-a5-llm.md
sections 2-3 and 5; successor of the frozen a5 engine-leg record).

RAW OUTPUT ONLY (P2 section 2.4): every run mode emits one complete kot-log/1
record BODY (counts, item vectors, pins, config) on stdout for log-append; it
renders NO verdict, computes NO derived statistic, and knows nothing about the
pre-registered thresholds (those live in registry/experiments/a5-llm.json and
are applied by verdict-gen through the pinned analysis/a5_llm.py).

Modes
  --emit-prompts --out PATH [--root R]
      Deterministic prompt-pack emitter (design section 3.1-3.3): builds the
      full two-arm pack (llm-direct + llm-rag x 977 pinned a5-eval queries)
      from the pinned corpora and pinned templates, runs the build-time
      retrieval-completeness lint (design section 3.3; FK-A5L-2), writes the
      pack JSONL, prints {pack_sha256, stats} JSON to stdout. Byte-identical
      on every invocation over unchanged pinned inputs; the digest is
      recorded in every run record (pins.artifact_hashes.a5-llm-prompt-pack).
  --emit-toy --out DIR [--root R]
      Emits the SYNTHETIC toy world (urn:kotw:v0:*-toy-* identifiers,
      mechanically disjoint from every code-world-v0 entity), the 30-query
      toy probe set (design n_planned.pilot_rule: the ONLY items any
      pre-freeze prompt/extraction iteration may touch; zero a5-eval items),
      and the toy prompt pack. Expected answers are computed by running the
      real kot-axiom engine (real code-axioms-v0) over the toy world.
  --arm engine|abstain-all|answer-all [--phase mock|final] [--root R]
      The $0 CPU cells (fresh deliberate re-runs; reuse_overrides declared in
      the record). Engine scoring is byte-equivalent to the frozen a5 rules
      (STRICT: value + provenance-subset-of-world-ids + license + exact
      ERR_* codes); the engine record embeds metrics.a5_reference (the
      comparable raw subset of the LAST final engine row of
      results-log/a5.jsonl) so the pinned analysis can compute the
      engine-regression instrument gate (/analysis/engine_matches_a5) as a
      pure function of its stdin.
  --score --arm llm-direct|llm-rag --rung R1|R2|R3 --raw PATH
          [--phase mock|final] [--pack PATH] [--toy DIR] [--root R]
      Consumes one cell's raw LLM generations (a5-llm-raw/1 JSONL: header +
      977 lines {qid, output_text, latency_ms, truncated, tokens_*}),
      re-emits the pack in memory and REFUSES on any pack-digest mismatch
      with the raw header (prompt identity is load-bearing), applies the
      pinned LENIENT extractor + scorer (design section 3.4; FK-A5L-1
      option (b), the pre-registered default), recomputes the retrieval
      completeness lint, and emits the cell's kot-log/1 record body.

The LLM-lenient instrument (STIPULATED: ASM-0012/ASM-0013 — every asymmetry
below runs in the LLM's favour, making the engine-superiority primary
conservative; changing ANY pinned string/regex/template after freeze is an
instrument version change):
  * covered queries: normalised set/boolean match — order-insensitive,
    case-insensitive, whitespace/backtick/quote-trimmed, full URN OR terminal
    slug accepted, booleans accept true/false/yes/no; no provenance required.
  * control queries: ANY well-formed refusal counts (JSON "refuse" field or
    the pinned refusal-marker regex list below — the record's five markers
    plus refusal-shaped variants, each extra marker pro-LLM on controls).
  * extractor is label-blind (returns ALL signals); the scorer applies the
    charitable class-aware precedence: covered -> answer-signals first;
    control -> refusal-signals first. Outputs with no signal are extraction
    FAILURES: instrument events (P10-analogue gate), never hypothesis events.
  * the RAG context is oracle-strong (design section 2.2): exact, complete,
    deterministic retrieval + the rendered 5-record axiom block with the
    concept-URN glossary (the engine resolves those URNs through the same
    exact-match minted tables — withholding the mapping would be an
    anti-LLM asymmetry, violating ASM-0013 faithfulness).

X3 TRAP (binding): concept/entity identity everywhere is EXACT URN string
equality — retrieval, glossary, scoring. No embedding, similarity or
nearest-neighbour step exists anywhere in this file.

House rules: stdlib only; no silent fallbacks (fail closed, named errors);
deterministic (the only RNG-bearing path is none — greedy decode upstream;
seed 0 is the registered placeholder). Engine/trivial-arm code is copied
from tools/experiments/a5_instrument.py (kept logic-identical so the fresh
engine pass reproduces a5's logged outcomes; the smoke check verifies this
against results-log/a5.jsonl).
"""

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "axiom"))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "registry"))
import kot_axiom  # noqa: E402
import kot_code  # noqa: E402
import kot_common  # noqa: E402

EXPERIMENT = "a5-llm"
CPU_ARMS = ("engine", "abstain-all", "answer-all")
LLM_ARMS = ("llm-direct", "llm-rag")
RUNGS = ("R1", "R2", "R3")
PACK_SCHEMA = "a5-llm-prompt-pack/1"
RAW_SCHEMA = "a5-llm-raw/1"
CORPORA = ("code-v0", "code-corpus-v0", "code-axioms-v0", "code-world-v0",
           "a5-eval", "kernel-v0")
GLOBAL_DEFAULT_GUESS = None  # answer-all's guess when it has nothing (a5 copy)

# Model pins (registry record pins.model_revisions, pinned directly).
MODEL_REVISIONS = {
    "R1": "HuggingFaceTB/SmolLM2-135M-Instruct@12fd25f77366fa6b3b4b768ec3050bf629380bac",
    "R2": "HuggingFaceTB/SmolLM2-360M-Instruct@a10cc1512eabd3dde888204e902eca88bddb4951",
    "R3": "HuggingFaceTB/SmolLM2-1.7B-Instruct@31b70e2e869a7173562077fd711b654946d38674",
}

# Decode pins (design section 2.1; echoed by the runner, verified at --score).
DECODE_PINS = {
    "do_sample": False,
    "temperature": 0.0,
    "max_new_tokens": 512,
    "context_window": 8192,
    "chat_template": "as shipped with the pinned revision",
}

TRUNCATION_RULE = (
    "if tokenised(messages, pinned chat template) + max_new_tokens exceeds the "
    "8192 context window, drop record lines from the TAIL of the longest "
    "CONTEXT block (final user turn) one line at a time until it fits; mark "
    "the query truncated=true; per-cell counts are reported (expected 0)")

NO_RECORDS_LINE = "CONTEXT: no records found for the entities in this question."

# ---------------------------------------------------------------- prompt pack
# Preamble: design-a5-llm.md section 3.1, verbatim.
PREAMBLE = (
    "You are answering questions about the static structure of a fixed Python "
    "codebase. Entities are named by exact identifiers (URNs) like "
    "`urn:kotw:v0:code-fn-example--main`. Answer ONLY from what you know or "
    "from the CONTEXT records if provided. Reply with a single JSON object on "
    "one line: {\"answer\": [\"<identifier>\", ...]} for a list answer, "
    "{\"answer\": true} or {\"answer\": false} for a yes/no question, or "
    "{\"refuse\": \"<short reason>\"} if the question cannot be answered "
    "(unknown entity, no matching record, conflicting records, or a malformed "
    "question). Output nothing else.")

# Question templates: design section 3.2, verbatim (one per op).
TEMPLATES = {
    "callers-of": "Which functions call `%s`?",
    "callees-of": "Which functions does `%s` call?",
    "where-defined": "In which single scope (module, class, or function) is `%s` defined?",
    "imports-of": "Which corpus modules does module `%s` import?",
    "imported-by": "Which corpus modules import module `%s`?",
    "contains": "Which constructs are lexically contained in `%s`?",
    "contained-in": "Which scopes lexically contain `%s`?",
    "instance-of": "Is `%s` an instance of the concept `%s`?",
}
MALFORMED_TEMPLATE = ("Answer this structural query if it is well-formed, "
                      "otherwise refuse: `%s`")

# Pinned refusal-marker regex list (design section 3.4 table row 2: the five
# named markers + refusal-shaped sentences; case-insensitive; every marker is
# pro-LLM on controls). Part of the instrument identity (ASM-0012).
REFUSAL_MARKER_PATTERNS = (
    r"\bcannot\s+(?:be\s+)?answer",       # "cannot answer" / "cannot be answered"
    r"\bcan(?:no|')t\s+answer",
    r"\bunable\s+to\s+answer",
    r"\bunknown\b",                        # "unknown"
    r"\bno\s+(?:matching\s+)?record",      # "no record"
    r"\bnot\s+sure\b",                     # "not sure"
    r"\bi\s+don'?t\s+know\b",              # "I don't know"
    r"\bnot\s+known\b",
    r"\brefus",                            # refuse / refusal / refusing
    r"\bnot\s+answerable\b",
    r"\bmalformed\b",
    r"\bnot\s+found\b",
    r"\bno\s+such\s+(?:entity|function|module|class|record|identifier)\b",
    r"\bdoes\s+not\s+exist\b",
    r"\bconflict",
)
REFUSAL_MARKERS = [re.compile(p, re.IGNORECASE) for p in REFUSAL_MARKER_PATTERNS]
URN_RE = re.compile(r"urn:[a-z0-9][a-z0-9:._-]*", re.IGNORECASE)
BOOL_TOKEN_RE = re.compile(r"\b(yes|true|no|false)\b", re.IGNORECASE)
_TRUE_WORDS = ("yes", "true")
_FALSE_WORDS = ("no", "false")


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _die(msg):
    sys.stderr.write("a5_llm_instrument: FATAL: %s\n" % msg)
    sys.exit(1)


def _dumps(obj):
    """Pinned canonical serialisation for pack/record lines (determinism)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


# ------------------------------------------------------------------ glossary
def load_glossary(root):
    """Exact minted-URN identity tables (X3: exact sourceId match, the same
    tables the engine layer consumes — kot_code.CodeOracle construction)."""
    code = kot_code._minted(root, "code-v0",
                            ["code-calls", "code-defines", "code-imports",
                             "python-function", "python-class", "python-module"])
    kernel = kot_code._minted(root, "kernel-v0", ["part-of"])
    rel_names = {
        code["code-calls"]: "calls",
        code["code-defines"]: "defines",
        code["code-imports"]: "imports",
        kernel["part-of"]: "part-of",
    }
    cls_names = {
        code["python-function"]: "python-function",
        code["python-class"]: "python-class",
        code["python-module"]: "python-module",
    }
    return {"rel": rel_names, "cls": cls_names,
            "calls": code["code-calls"], "defines": code["code-defines"],
            "imports": code["code-imports"], "partof": kernel["part-of"],
            "fn": code["python-function"], "cl": code["python-class"],
            "mod": code["python-module"]}


def axiom_block(gl):
    """Pinned verbatim rendering of the 5 code-axioms-v0 records (design
    section 3.3 axiom-block content), with the concept-URN glossary — the
    engine resolves these URNs via the same exact-match minted tables, so a
    faithful kernel-as-text form must hand the LLM the same mapping
    (STIPULATED: ASM-0013)."""
    return "\n".join([
        "AXIOMS (code-axioms-v0, rendered; complete and exact):",
        "- Licensed kind concepts: `%s` is python-function; `%s` is "
        "python-class; `%s` is python-module. No other concept identifier "
        "is licensed." % (gl["fn"], gl["cl"], gl["mod"]),
        "- python-function, python-class and python-module are pairwise "
        "disjoint kinds: no entity is more than one of them.",
        "- Every python-function and every python-class is defined in "
        "exactly one scope; python-modules are not \"defined in\" any scope.",
        "- `calls` relates python-functions to python-functions.",
        "- `imports` relates python-modules to python-modules.",
        "- Lexical containment (\"is lexically contained in\") has inverse "
        "\"has part\"; containment records are stored per pair, including "
        "transitive pairs.",
    ])


def disjoint_pairs(root):
    """Symmetric closure of disjointWith over the code-axioms-v0 records."""
    axioms, _w = kot_code.load_code_corpora(root)
    pairs = set()
    for _ref, rec in axioms:
        subj = rec["subject"]
        for c in rec.get("constraints", []):
            if c.get("kind") == "disjointWith":
                pairs.add((subj, c["target"]))
                pairs.add((c["target"], subj))
    return pairs


# ----------------------------------------------------------------- rendering
def render_record(rec, gl):
    """One pinned English line per world record (design section 3.3)."""
    if rec["kind"] == "class":
        name = gl["cls"].get(rec["concept"])
        if name is not None:
            return "- `%s` is a `%s`." % (rec["entity"], name)
        return "- `%s` is an instance of the concept `%s`." % (
            rec["entity"], rec["concept"])
    verb = gl["rel"].get(rec["relation"])
    if verb is None:
        _die("unrenderable relation URN %r in record %s" %
             (rec["relation"], rec.get("id")))
    if verb == "part-of":
        return "- `%s` is lexically contained in `%s`." % (
            rec["subject"], rec["object"])
    return "- `%s` %s `%s`." % (rec["subject"], verb, rec["object"])


def query_urns(q):
    """Entity/concept URNs mentioned in a query: every string value that is a
    urn: identifier (covers the 8 well-formed shapes AND malformed controls,
    deterministically; instance-of contributes entity + concept per design
    section 3.3)."""
    if not isinstance(q, dict):
        return []
    return sorted(v for v in q.values()
                  if isinstance(v, str) and v.startswith("urn:"))


def build_world_index(world):
    """Exact-string-equality retrieval index (X3-compliant; no similarity)."""
    idx = {}
    for rec in world:
        keys = ((rec["subject"], rec["object"]) if rec["kind"] == "relation"
                else (rec["entity"], rec["concept"]))
        for k in keys:
            idx.setdefault(k, []).append(rec)
    return idx


def retrieve(q, idx):
    """All world records whose subject/object (relation) or entity/concept
    (class) URN string-equals any URN in the query; deterministic record-id
    order; FK-A5L-2 option (a) — the build-time completeness lint decides."""
    seen, out = set(), []
    for u in query_urns(q):
        for rec in idx.get(u, ()):
            if rec["id"] not in seen:
                seen.add(rec["id"])
                out.append(rec)
    out.sort(key=lambda r: r["id"])
    return out


def is_wellformed(q):
    """Mirror of kot_code.CodeOracle.desugar's shape check (closed grammar)."""
    if not isinstance(q, dict):
        return False
    op = q.get("op")
    if op == "instance-of":
        return (set(q) == {"op", "entity", "concept"}
                and isinstance(q["entity"], str) and isinstance(q["concept"], str))
    if op in ("callers-of", "callees-of", "where-defined", "imports-of",
              "imported-by", "contains", "contained-in"):
        return set(q) == {"op", "of"} and isinstance(q["of"], str)
    return False


def render_question(q):
    if is_wellformed(q):
        op = q["op"]
        if op == "instance-of":
            return TEMPLATES[op] % (q["entity"], q["concept"])
        return TEMPLATES[op] % q["of"]
    # design section 3.2: the malformed stratum has no template by construction
    return MALFORMED_TEMPLATE % json.dumps(q, sort_keys=True)


def context_block(records, gl):
    if not records:
        return NO_RECORDS_LINE
    return ("CONTEXT (records for the entities in this question):\n"
            + "\n".join(render_record(r, gl) for r in records))


# ------------------------------------------------------------------ toy world
# Synthetic toy world (design section 3.1: few-shot examples + the 30-query
# pilot probe live here and ONLY here; every entity slug contains "-toy",
# and --emit-prompts asserts mechanical disjointness from code-world-v0).
def toy_world(gl):
    mod_a = "urn:kotw:v0:code-mod-toy-app"
    mod_u = "urn:kotw:v0:code-mod-toy-util"
    cls_c = "urn:kotw:v0:code-cls-toy-app--config"
    fn_main = "urn:kotw:v0:code-fn-toy-app--main"
    fn_run = "urn:kotw:v0:code-fn-toy-app--run"
    fn_load = "urn:kotw:v0:code-fn-toy-app--config--load"
    fn_parse = "urn:kotw:v0:code-fn-toy-util--parse"
    fn_emit = "urn:kotw:v0:code-fn-toy-util--emit"
    ents = {"mod_a": mod_a, "mod_u": mod_u, "cls_c": cls_c, "fn_main": fn_main,
            "fn_run": fn_run, "fn_load": fn_load, "fn_parse": fn_parse,
            "fn_emit": fn_emit}
    recs, n = [], [0]

    def rec(kind, **kw):
        n[0] += 1
        base = {"schema": "kot-world/1", "id": "ct%05d" % n[0], "kind": kind,
                "provenance": {"source": "a5-llm-toy/1 synthetic"}}
        base.update(kw)
        recs.append(base)

    for e, c in ((mod_a, gl["mod"]), (mod_u, gl["mod"]), (cls_c, gl["cl"]),
                 (fn_main, gl["fn"]), (fn_run, gl["fn"]), (fn_load, gl["fn"]),
                 (fn_parse, gl["fn"]), (fn_emit, gl["fn"])):
        rec("class", entity=e, concept=c)
    for s, o in ((fn_main, fn_run), (fn_run, fn_parse), (fn_run, fn_emit),
                 (fn_parse, fn_emit)):
        rec("relation", subject=s, relation=gl["calls"], object=o)
    for s, o in ((mod_a, fn_main), (mod_a, fn_run), (mod_a, cls_c),
                 (mod_u, fn_parse), (mod_u, fn_emit), (cls_c, fn_load)):
        rec("relation", subject=s, relation=gl["defines"], object=o)
    # per-pair materialised containment, incl. the transitive pair (mirrors
    # the pinned store's per-pair materialisation — FK-A5L-2 shape)
    for s, o in ((fn_main, mod_a), (fn_run, mod_a), (cls_c, mod_a),
                 (fn_load, cls_c), (fn_load, mod_a), (fn_parse, mod_u),
                 (fn_emit, mod_u)):
        rec("relation", subject=s, relation=gl["partof"], object=o)
    rec("relation", subject=mod_a, relation=gl["imports"], object=mod_u)
    return recs, ents


# Real out-of-scope concept (a licensed kernel concept NOT in the code axiom
# layer — same concept class the a5-eval out-of-scope-concept stratum uses;
# concept URNs are shared vocabulary, not eval items).
OOS_CONCEPT = "urn:kot:bciqg2htlxn4zazdgpx7onf6vwgenwzyvwr3yj7wlv5rt5lge3gcllnq"


def toy_probe_queries(gl, ents):
    """The 30-query toy probe (18 covered / 12 control shapes). Disjoint from
    the 3 few-shot examples (different (op, argument) pairs)."""
    e = ents
    covered = [
        ("callers-of", {"op": "callers-of", "of": e["fn_parse"]}),
        ("callers-of", {"op": "callers-of", "of": e["fn_emit"]}),
        ("callers-of", {"op": "callers-of", "of": e["fn_run"]}),
        ("callees-of", {"op": "callees-of", "of": e["fn_main"]}),
        ("callees-of", {"op": "callees-of", "of": e["fn_parse"]}),
        ("where-defined", {"op": "where-defined", "of": e["fn_main"]}),
        ("where-defined", {"op": "where-defined", "of": e["fn_load"]}),
        ("where-defined", {"op": "where-defined", "of": e["fn_parse"]}),
        ("imports-of", {"op": "imports-of", "of": e["mod_a"]}),
        ("imported-by", {"op": "imported-by", "of": e["mod_u"]}),
        ("contains", {"op": "contains", "of": e["mod_a"]}),
        ("contains", {"op": "contains", "of": e["cls_c"]}),
        ("contained-in", {"op": "contained-in", "of": e["fn_load"]}),
        ("contained-in", {"op": "contained-in", "of": e["fn_main"]}),
        ("instance-true", {"op": "instance-of", "entity": e["fn_load"], "concept": gl["fn"]}),
        ("instance-true", {"op": "instance-of", "entity": e["mod_a"], "concept": gl["mod"]}),
        ("instance-false-disjoint", {"op": "instance-of", "entity": e["mod_a"], "concept": gl["fn"]}),
        ("instance-false-disjoint", {"op": "instance-of", "entity": e["fn_parse"], "concept": gl["cl"]}),
    ]
    control = [
        ("unknown-entity", {"op": "callers-of", "of": "urn:kotw:v0:code-fn-toy-app--ghost-a"}),
        ("unknown-entity", {"op": "where-defined", "of": "urn:kotw:v0:code-fn-toy-app--ghost-b"}),
        ("no-record-imports", {"op": "imports-of", "of": e["mod_u"]}),
        ("no-record-imported-by", {"op": "imported-by", "of": e["mod_a"]}),
        ("no-record-callers", {"op": "callers-of", "of": e["fn_main"]}),
        ("no-record-callees", {"op": "callees-of", "of": e["fn_emit"]}),
        ("no-record-contains", {"op": "contains", "of": e["fn_load"]}),
        ("unlicensed-unique", {"op": "where-defined", "of": e["mod_a"]}),
        ("unlicensed-unique", {"op": "where-defined", "of": e["mod_u"]}),
        ("out-of-scope-concept", {"op": "instance-of", "entity": e["fn_main"], "concept": OOS_CONCEPT}),
        ("malformed", {"op": "type-of", "of": e["fn_main"]}),
        ("malformed", {"op": "callers-of"}),
    ]
    out = []
    for i, (fam, q) in enumerate(covered + control, 1):
        out.append({"qid": "tq%04d" % i, "family": fam,
                    "class": "covered" if fam in
                    ("callers-of", "callees-of", "where-defined", "imports-of",
                     "imported-by", "contains", "contained-in",
                     "instance-true", "instance-false-disjoint")
                    else "control", "query": q})
    return out


def build_toy_oracle(root, world):
    """Real code-axioms-v0 + real minted op table over the TOY world."""
    oracle = kot_code.CodeOracle(root)
    axioms, _w = kot_code.load_code_corpora(root)
    oracle.engine = kot_axiom.Engine(axioms, world)
    return oracle


def toy_expected(oracle, queries):
    """Expected answers = the engine's own outputs (single source of truth).
    Fails closed if a planned-covered query refuses (toy world inconsistent)."""
    out = []
    for rec in queries:
        r = oracle.query(rec["query"])
        if rec["class"] == "covered":
            if r["status"] != "answer":
                _die("toy covered query %s refused: %r" % (rec["qid"], r))
            exp = {"kind": "answer", "value": r["value"]}
        else:
            if r["status"] != "refuse":
                _die("toy control query %s answered: %r" % (rec["qid"], r))
            exp = {"kind": "refuse", "code": r["code"]}
        rec2 = dict(rec)
        rec2["expected"] = exp
        out.append(rec2)
    return out


def fewshot_examples(root, gl):
    """Three pinned few-shot examples over the toy world (design section 3.1:
    one list answer, one boolean, one refusal), answers computed by the real
    engine over the toy store. Multi-turn chat form (STIPULATED: ASM-0012 —
    the standard few-shot form for small instruct models, pro-LLM; any
    pre-freeze change decided on the toy probe re-emits the pack digest)."""
    world, ents = toy_world(gl)
    oracle = build_toy_oracle(root, world)
    idx = build_world_index(world)
    exs = []
    for q, kind in (
            ({"op": "callees-of", "of": ents["fn_run"]}, "list"),
            ({"op": "instance-of", "entity": ents["cls_c"], "concept": gl["cl"]}, "bool"),
            ({"op": "callers-of", "of": "urn:kotw:v0:code-fn-toy-app--ghost"}, "refuse")):
        r = oracle.query(q)
        if kind == "refuse":
            if r["status"] != "refuse":
                _die("few-shot refusal example did not refuse: %r" % r)
            ans = json.dumps({"refuse": "unknown entity"})
        else:
            if r["status"] != "answer":
                _die("few-shot example refused: %r" % r)
            ans = json.dumps({"answer": r["value"]})
        exs.append({"question": render_question(q),
                    "context": context_block(retrieve(q, idx), gl),
                    "answer": ans})
    return exs


# ------------------------------------------------------------- pack assembly
def build_messages(arm, question, ctx, fewshot, axioms_text):
    """Pinned multi-turn assembly. RAG: axiom block once, in the first user
    turn (design section 3.3: 'every rag prompt'); per-turn CONTEXT blocks.
    Direct: same turns without any CONTEXT (closed-book)."""
    rag = arm == "llm-rag"
    msgs = []
    first = PREAMBLE + ("\n\n" + axioms_text if rag else "")
    for i, ex in enumerate(fewshot):
        u = (ex["context"] + "\n\n" if rag else "") + "Question: " + ex["question"]
        if i == 0:
            u = first + "\n\n" + u
        msgs.append({"content": u, "role": "user"})
        msgs.append({"content": ex["answer"], "role": "assistant"})
    u = (ctx + "\n\n" if rag else "") + "Question: " + question
    msgs.append({"content": u, "role": "user"})
    return msgs


def completeness_lint(queries, idx, disj):
    """Build-time retrieval-completeness lint (design section 3.3, gate input
    /analysis/retrieval_completeness_violations): for every COVERED query the
    retrieved set must DERIVE the pre-authored expected answer. Returns the
    list of violating qids (must be empty; FK-A5L-2 (b) closure-walk activates
    pre-freeze only if this fails under exact matching)."""
    bad = []
    for rec in queries:
        if rec["class"] != "covered":
            continue
        q, exp = rec["query"], rec["expected"]["value"]
        got = retrieve(q, idx)
        ok = False
        op = q.get("op")
        if op == "instance-of":
            ent, con = q["entity"], q["concept"]
            asserted = [r for r in got if r["kind"] == "class" and r["entity"] == ent]
            if exp is True:
                ok = any(r["concept"] == con for r in asserted)
            else:
                ok = (not any(r["concept"] == con for r in asserted)
                      and any((r["concept"], con) in disj for r in asserted))
        else:
            rel_key = {"callers-of": "calls", "callees-of": "calls",
                       "where-defined": "defines", "imports-of": "imports",
                       "imported-by": "imports", "contains": "partof",
                       "contained-in": "partof"}[op]
            side = {"callers-of": "object", "callees-of": "subject",
                    "where-defined": "object", "imports-of": "subject",
                    "imported-by": "object", "contains": "object",
                    "contained-in": "subject"}[op]
            other = "subject" if side == "object" else "object"
            rel_urn = _LINT_GL[rel_key]
            derived = sorted(set(
                r[other] for r in got
                if r["kind"] == "relation" and r["relation"] == rel_urn
                and r[side] == q["of"]))
            if op == "where-defined":
                ok = len(derived) == 1 and derived[0] == exp
            else:
                ok = derived == sorted(exp)
        if not ok:
            bad.append(rec["qid"])
    return bad


_LINT_GL = {}  # filled by emit_pack (glossary relation URNs for the lint)


def emit_pack(root, queries, world, gl, toy=False):
    """Assemble the full deterministic pack; returns (bytes, header, stats)."""
    global _LINT_GL
    _LINT_GL = {"calls": gl["calls"], "defines": gl["defines"],
                "imports": gl["imports"], "partof": gl["partof"]}
    idx = build_world_index(world)
    disj = disjoint_pairs(root)
    fewshot = fewshot_examples(root, gl)
    ax = axiom_block(gl)
    violations = completeness_lint(queries, idx, disj)

    if not toy:
        # mechanical toy/corpus disjointness assertion (pilot rule)
        toy_recs, _ents = toy_world(gl)
        world_ents = set()
        for r in world:
            world_ents.add(r["entity"] if r["kind"] == "class" else r["subject"])
            if r["kind"] == "relation":
                world_ents.add(r["object"])
        for r in toy_recs:
            for u in ((r["entity"],) if r["kind"] == "class"
                      else (r["subject"], r["object"])):
                if u in world_ents:
                    _die("toy identifier %s collides with code-world-v0" % u)

    lines, stats = [], {"n_empty_retrieval": 0, "max_prompt_chars": 0,
                        "n_context_records_max": 0}
    for arm in LLM_ARMS:
        for rec in queries:
            got = retrieve(rec["query"], idx)
            ctx = context_block(got, gl)
            if not got:
                stats["n_empty_retrieval"] += 1 if arm == "llm-rag" else 0
            msgs = build_messages(arm, render_question(rec["query"]), ctx,
                                  fewshot, ax)
            chars = sum(len(m["content"]) for m in msgs)
            stats["max_prompt_chars"] = max(stats["max_prompt_chars"], chars)
            stats["n_context_records_max"] = max(stats["n_context_records_max"],
                                                 len(got))
            lines.append(_dumps({"arm": arm, "messages": msgs,
                                 "n_context_records": len(got),
                                 "prompt_chars": chars, "qid": rec["qid"]}))
    stats["retrieval_completeness_violations"] = len(violations)
    stats["violating_qids"] = violations[:20]
    header = {
        "schema": PACK_SCHEMA, "experiment": EXPERIMENT, "toy": bool(toy),
        "arms": list(LLM_ARMS), "n_queries": len(queries),
        "n_prompts": len(lines), "decode_pins": DECODE_PINS,
        "truncation_rule": TRUNCATION_RULE, "no_records_line": NO_RECORDS_LINE,
        "retrieval_rule": ("exact subject/object URN string equality "
                           "(FK-A5L-2 option (a)); X3: no similarity anywhere"),
        "fewshot_style": "chat", "model_revisions": MODEL_REVISIONS,
        "stats": stats,
    }
    if not toy:
        header["corpus_pins"] = {c: kot_common.corpus_hash(root, c)
                                 for c in CORPORA}
    body = "\n".join([_dumps(header)] + lines) + "\n"
    return body.encode("utf-8"), header, stats


def pack_digest(pack_bytes):
    return hashlib.sha256(pack_bytes).hexdigest()


# ------------------------------------------------- lenient extractor + scorer
def extract_signals(text):
    """Label-blind extraction: return ALL recoverable signals (design section
    3.4: JSON-first, then pinned lenient regexes). The class-aware scorer
    applies the charitable precedence per query class."""
    sig = {"json_answer": None, "has_json_answer": False, "json_refuse": False,
           "regex_urns": [], "regex_bool": None, "refusal_marker": False}
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    t = text.strip()
    obj = None
    try:
        cand = json.loads(t)
        if isinstance(cand, dict):
            obj = cand
    except ValueError:
        dec = json.JSONDecoder()
        for m in re.finditer(r"\{", t):
            try:
                cand, _end = dec.raw_decode(t[m.start():])
            except ValueError:
                continue
            if isinstance(cand, dict) and ("answer" in cand or "refuse" in cand):
                obj = cand
                break
    if obj is not None:
        if "refuse" in obj:
            sig["json_refuse"] = True
        if "answer" in obj:
            sig["has_json_answer"] = True
            sig["json_answer"] = obj["answer"]
    urns = []
    for m in URN_RE.finditer(text):
        u = m.group(0).rstrip(".,;:`'\"")
        if u not in urns:
            urns.append(u)
    sig["regex_urns"] = urns
    bm = BOOL_TOKEN_RE.search(text)
    if bm:
        sig["regex_bool"] = bm.group(1).lower() in _TRUE_WORDS
    for rx in REFUSAL_MARKERS:
        if rx.search(text):
            sig["refusal_marker"] = True
            break
    return sig


def _norm(s):
    return str(s).strip().strip("`\"'").rstrip(".").strip().lower()


def _terminal(urn):
    return urn.rsplit(":", 1)[-1]


def _as_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        n = _norm(v)
        if n in _TRUE_WORDS:
            return True
        if n in _FALSE_WORDS:
            return False
    return None


def lenient_match(value, expected):
    """Design section 3.4 covered-exact rule for LLM arms: order-insensitive
    set equality; case-insensitive; whitespace-trimmed; full URN or terminal
    slug accepted; booleans accept true/false/yes/no. No provenance."""
    if isinstance(expected, bool):
        return _as_bool(value) is expected
    exp_list = expected if isinstance(expected, list) else [expected]
    if isinstance(value, (str, bool, int, float)):
        given = [value]
    elif isinstance(value, list):
        given = value
    else:
        return False
    if isinstance(expected, str) and isinstance(value, list) and len(value) != 1:
        return False
    alts = {}
    for e in exp_list:
        en = _norm(e)
        alts[en] = en
        alts[_terminal(en)] = en
    matched = set()
    for g in given:
        if isinstance(g, bool) or not isinstance(g, (str, int, float)):
            return False
        gn = _norm(g)
        hit = alts.get(gn)
        if hit is None:
            return False
        matched.add(hit)
    return matched == set(_norm(e) for e in exp_list)


def score_llm_output(rec, text):
    """One query, one raw output -> (conj 0/1, outcome tag, extracted 0/1).
    Charitable class-aware precedence (ASM-0012, disclosed in the module
    docstring); outcomes: exact, wrong, refused, fabricated, extraction-fail."""
    sig = extract_signals(text)
    exp = rec["expected"]
    boolean = is_wellformed(rec["query"]) and rec["query"]["op"] == "instance-of"
    if rec["class"] == "covered":
        if sig["has_json_answer"]:
            ok = lenient_match(sig["json_answer"], exp["value"])
            return (1 if ok else 0), ("exact" if ok else "wrong"), 1
        if sig["json_refuse"] or sig["refusal_marker"]:
            return 0, "refused", 1
        if boolean and sig["regex_bool"] is not None:
            ok = sig["regex_bool"] is exp["value"]
            return (1 if ok else 0), ("exact" if ok else "wrong"), 1
        if not boolean and sig["regex_urns"]:
            ok = lenient_match(sig["regex_urns"], exp["value"])
            return (1 if ok else 0), ("exact" if ok else "wrong"), 1
        return 0, "extraction-fail", 0
    # control: ANY well-formed refusal counts (pro-LLM)
    if sig["json_refuse"] or sig["refusal_marker"]:
        return 1, "refused", 1
    if sig["has_json_answer"] or sig["regex_urns"] or sig["regex_bool"] is not None:
        return 0, "fabricated", 1
    return 0, "extraction-fail", 0


def score_llm_cell(queries, raws_by_qid):
    m = {"n_queries": len(queries), "n_covered": 0, "n_control": 0,
         "n_covered_exact": 0, "n_covered_refused": 0,
         "n_covered_answered_wrong": 0, "n_covered_extraction_failure": 0,
         "n_control_refused_any": 0, "n_control_fabricated": 0,
         "n_control_extraction_failure": 0,
         "n_extraction_success": 0, "n_extraction_failure": 0,
         "truncation_count": 0, "by_family": {}}
    item_conj, item_class, item_extracted, latency_ms = [], [], [], []
    tok_p = tok_d = 0
    tok_seen = True
    for rec in queries:
        raw = raws_by_qid[rec["qid"]]
        conj, tag, ext = score_llm_output(rec, raw.get("output_text", ""))
        fam = m["by_family"].setdefault(rec["family"], {"n": 0, "ok": 0})
        fam["n"] += 1
        fam["ok"] += conj
        covered = rec["class"] == "covered"
        m["n_covered" if covered else "n_control"] += 1
        if covered:
            if tag == "exact":
                m["n_covered_exact"] += 1
            elif tag == "wrong":
                m["n_covered_answered_wrong"] += 1
            elif tag == "refused":
                m["n_covered_refused"] += 1
            else:
                m["n_covered_extraction_failure"] += 1
        else:
            if tag == "refused":
                m["n_control_refused_any"] += 1
            elif tag == "fabricated":
                m["n_control_fabricated"] += 1
            else:
                m["n_control_extraction_failure"] += 1
        m["n_extraction_success"] += ext
        m["n_extraction_failure"] += 1 - ext
        m["truncation_count"] += 1 if raw.get("truncated") else 0
        item_conj.append(conj)
        item_class.append(1 if covered else 0)
        item_extracted.append(ext)
        latency_ms.append(float(raw.get("latency_ms", 0.0)))
        if raw.get("tokens_prompt") is None or raw.get("tokens_decode") is None:
            tok_seen = False
        else:
            tok_p += int(raw["tokens_prompt"])
            tok_d += int(raw["tokens_decode"])
    m["item_conj"] = item_conj
    m["item_class"] = item_class
    m["item_extracted"] = item_extracted
    m["latency_ms"] = latency_ms
    m["tokens_prompt_total"] = tok_p if tok_seen else None
    m["tokens_decode_total"] = tok_d if tok_seen else None
    return m


# --------------------------------------------------- engine / trivial arms
# Copied logic-identical from tools/experiments/a5_instrument.py (the frozen
# a5 rules; self-contained so this instrument's identity is its own sha +
# the pinned kot_axiom/kot_code shas — no runtime dependency on an unpinned
# sibling file). The a5-llm smoke check proves equivalence against
# results-log/a5.jsonl (the engine-regression gate input).
def policy_answer_all(oracle, query):
    r = oracle.query(query)
    if r["status"] == "answer":
        return r
    core = oracle.desugar(query)
    value = GLOBAL_DEFAULT_GUESS
    if core.get("status") != "refuse":
        try:
            if core["op"] in ("unique", "lookup"):
                edges = oracle.engine._edges(core["rel"], core["subject"], core["direction"])
                objs = sorted(set(o for (o, _ref) in edges))
                value = (objs[0] if objs else GLOBAL_DEFAULT_GUESS) \
                    if core["op"] == "unique" else objs
            elif core["op"] == "instance":
                value = core["concept"] in oracle.engine.classes.get(core["entity"], {})
        except Exception:
            value = GLOBAL_DEFAULT_GUESS
    return {"status": "answer", "value": value, "provenance": [], "license": ["fabricated"]}


def run_cpu_arm(oracle, queries, arm, timed=False):
    results, lat = [], []
    for rec in queries:
        t0 = time.perf_counter_ns() if timed else 0
        if arm == "engine":
            r = oracle.query(rec["query"])
        elif arm == "abstain-all":
            r = {"status": "refuse", "code": "ABSTAIN", "reason": "policy"}
        else:
            r = policy_answer_all(oracle, rec["query"])
        if timed:
            lat.append(time.perf_counter_ns() - t0)
        results.append(r)
    return results, lat


def score_cpu(queries, results, arm, world_ids):
    """a5 aggregate scoring, verbatim rules, extended with per-item vectors.
    Engine conj item: covered -> STRICT exact (value+provenance+license);
    control -> STRICT expected ERR code. Trivial arms: covered exact without
    the provenance conjunct (a5 rule); control conjunct uses refused-ANY for
    the descriptive brackets (record language: 'covered ~1.0 / refusal 0')."""
    m = {"n_covered": 0, "n_covered_exact": 0, "n_covered_refused": 0,
         "n_covered_answered_wrong": 0,
         "n_control": 0, "n_control_refused_correct_code": 0,
         "n_control_refused_other_code": 0, "n_control_answered": 0,
         "by_family": {}}
    item_conj, item_class = [], []
    prov_checked, prov_ok = 0, True
    for rec, r in zip(queries, results):
        fam = m["by_family"].setdefault(rec["family"], {"n": 0, "ok": 0})
        fam["n"] += 1
        exp = rec["expected"]
        conj = 0
        if rec["class"] == "covered":
            m["n_covered"] += 1
            item_class.append(1)
            if r["status"] != "answer":
                m["n_covered_refused"] += 1
            else:
                exact = r["value"] == exp["value"]
                if arm == "engine":
                    prov_checked += 1
                    good_prov = (bool(r.get("provenance")) and bool(r.get("license"))
                                 and all(p in world_ids for p in r["provenance"]))
                    prov_ok = prov_ok and good_prov
                    exact = exact and good_prov
                if exact:
                    m["n_covered_exact"] += 1
                    fam["ok"] += 1
                    conj = 1
                else:
                    m["n_covered_answered_wrong"] += 1
        else:
            m["n_control"] += 1
            item_class.append(0)
            if r["status"] == "answer":
                m["n_control_answered"] += 1
            elif r["code"] == exp["code"]:
                m["n_control_refused_correct_code"] += 1
                fam["ok"] += 1
                conj = 1
            else:
                m["n_control_refused_other_code"] += 1
                if arm != "engine":
                    conj = 1  # trivial-arm bracket: refused-any (descriptive)
        item_conj.append(conj)
    m["n_control_refused_any"] = m["n_control_refused_correct_code"] + \
        m["n_control_refused_other_code"]
    m["provenance_checked"] = prov_checked
    m["provenance_all_valid"] = bool(prov_ok)
    m["item_conj"] = item_conj
    m["item_class"] = item_class
    return m


A5_REFERENCE_KEYS = (
    "n_covered", "n_covered_exact", "n_covered_refused",
    "n_covered_answered_wrong", "n_control", "n_control_refused_correct_code",
    "n_control_refused_other_code", "n_control_answered",
    "n_control_refused_any", "provenance_checked", "provenance_all_valid",
    "by_family", "store")


def a5_reference(root):
    """Comparable raw subset of the LAST final engine row in
    results-log/a5.jsonl (a5's log carries per-FAMILY aggregate outcomes —
    its finest logged granularity; the fresh record additionally logs
    item_conj + a per-query outcome digest for future regressions)."""
    path = os.path.join(root, "results-log", "a5.jsonl")
    ref = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if (r.get("event") == "run" and r.get("phase") == "final"
                    and r.get("config", {}).get("arm") == "engine"):
                ref = r
    if ref is None:
        _die("no final engine row found in results-log/a5.jsonl")
    sub = {k: ref["metrics"][k] for k in A5_REFERENCE_KEYS}
    return {"source": "results-log/a5.jsonl", "source_seq": ref["seq"],
            "metrics": sub}


# --------------------------------------------------------------- record body
def common_pins(root, inst_sha, pack_sha):
    pins = {"_recipe": kot_common.CORPUS_RECIPE}
    for corpus in CORPORA:
        pins["corpus_%s" % corpus] = {
            "observed": kot_common.corpus_hash(root, corpus),
            "recipe": "kot-corpus-hash/1"}
    pins["instrument"] = {"observed": inst_sha}
    pins["engine"] = {"observed": file_sha256(
        os.path.join(root, "tools", "axiom", "kot_axiom.py"))}
    pins["code_layer"] = {"observed": file_sha256(
        os.path.join(root, "tools", "axiom", "kot_code.py"))}
    pins["analysis_script"] = {"observed": file_sha256(
        os.path.join(root, "analysis", "a5_llm.py"))}
    pins["prompt_pack"] = {"observed": pack_sha}
    return pins


def finish_body(body, root):
    idx_path = os.path.join(root, "registry", "frozen-index.json")
    if os.path.isfile(idx_path):
        with open(idx_path, "r", encoding="utf-8") as f:
            ph = json.load(f).get(EXPERIMENT)
        if ph:
            body["prereg_hash"] = ph
    body["config_sha256"] = hashlib.sha256(
        json.dumps(body["config"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print(json.dumps(body, sort_keys=True))


def load_eval(root):
    with open(os.path.join(root, "data", "a5-eval", "queries.jsonl"), "r",
              encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def run_cpu(root, arm, phase):
    oracle = kot_code.build_code_oracle(root)
    queries = load_eval(root)
    t0 = time.perf_counter_ns()
    results, lat = run_cpu_arm(oracle, queries, arm, timed=True)
    t1 = time.perf_counter_ns()
    results2, _ = run_cpu_arm(oracle, queries, arm)
    deterministic = json.dumps(results, sort_keys=True) == \
        json.dumps(results2, sort_keys=True)

    eng = oracle.engine
    metrics = score_cpu(queries, results, arm, eng.world_ids)
    from collections import Counter
    vio = Counter(v["code"] for v in eng.violations)
    with open(os.path.join(root, "data", "code-world-v0", "world.jsonl"),
              "r", encoding="utf-8") as f:
        n_world = sum(1 for l in f if l.strip())
    metrics["store"] = {
        "n_axiom_records": len(eng.axioms),
        "n_world_records": n_world,
        "n_entities": len(eng.entities),
        "n_violations": len(eng.violations),
        "violations_by_code": dict(sorted(vio.items())),
        "n_incomplete_pairs": len(eng.incomplete),
    }
    metrics["engine_total_ns"] = t1 - t0
    metrics["latency_ns"] = lat
    metrics["n_queries"] = len(queries)
    metrics["deterministic_repeat_identical"] = bool(deterministic)
    metrics["per_query_outcome_sha256"] = hashlib.sha256(
        json.dumps(results, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if arm == "engine":
        metrics["a5_reference"] = a5_reference(root)
    metrics["coverage_note"] = (
        "eval authored against the deterministically-extracted code-world-v0 "
        "records - coverage is by construction (design doc section 5.1); "
        "every accuracy statement is bounded to this slice")

    gl = load_glossary(root)
    world = [r for _n, r in _iter_world(root)]
    pack_bytes, _h, _s = emit_pack(root, queries, world, gl)
    inst_sha = file_sha256(os.path.join(_HERE, "a5_llm_instrument.py"))
    pins = common_pins(root, inst_sha, pack_digest(pack_bytes))

    body = {
        "event": "run", "experiment": EXPERIMENT, "phase": phase,
        "config": {
            "arm": arm, "rung": "R0", "seed": 0,
            "instrument": "tools/experiments/a5_llm_instrument.py",
            "instrument_sha256": inst_sha,
            "engine_sha256": pins["engine"]["observed"],
            "code_layer_sha256": pins["code_layer"]["observed"],
            "pack_sha256": pins["prompt_pack"]["observed"],
            "python_version": platform.python_version(),
            "hardware": "r0-local-cpu shared 2-core box, nice -n 10, foreground",
            "scope_note": ("fresh deliberate re-run of the a5-logged cell "
                           "(reuse_overrides declared; reuse DEFERRED "
                           "programme-wide); the engine cell doubles as the "
                           "engine-regression instrument gate input"),
        },
        "metrics": metrics,
        "pins_observed": pins,
        "cost": {"usd": 0},
        "exit": "ok",
        "error": None,
    }
    finish_body(body, root)


def _iter_world(root):
    with open(os.path.join(root, "data", "code-world-v0", "world.jsonl"),
              "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.strip():
                yield i, json.loads(line)


def run_score(root, arm, rung, raw_path, phase, toy_dir=None):
    if arm not in LLM_ARMS:
        _die("--score arm must be one of %s" % (LLM_ARMS,))
    if rung not in RUNGS:
        _die("--score rung must be one of %s" % (RUNGS,))
    with open(raw_path, "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    if not lines:
        _die("empty raw file %s" % raw_path)
    header, rows = lines[0], lines[1:]

    # fail-closed header verification (prompt identity is load-bearing)
    if header.get("schema") != RAW_SCHEMA:
        _die("raw header schema %r != %s" % (header.get("schema"), RAW_SCHEMA))
    if header.get("arm") != arm or header.get("rung") != rung:
        _die("raw header arm/rung %r/%r != requested %s/%s"
             % (header.get("arm"), header.get("rung"), arm, rung))
    if header.get("model_revision") != MODEL_REVISIONS[rung]:
        _die("model revision %r != pinned %s"
             % (header.get("model_revision"), MODEL_REVISIONS[rung]))
    if header.get("decode_pins") != _json_roundtrip(DECODE_PINS):
        _die("decode pins in raw header do not match the pinned decode pins")

    gl = load_glossary(root)
    if toy_dir:
        with open(os.path.join(toy_dir, "toy-world.jsonl"), encoding="utf-8") as f:
            world = [json.loads(l) for l in f if l.strip()]
        with open(os.path.join(toy_dir, "toy-queries.jsonl"), encoding="utf-8") as f:
            queries = [json.loads(l) for l in f if l.strip()]
        pack_bytes, _h, stats = emit_pack(root, queries, world, gl, toy=True)
    else:
        queries = load_eval(root)
        world = [r for _n, r in _iter_world(root)]
        pack_bytes, _h, stats = emit_pack(root, queries, world, gl)
    psha = pack_digest(pack_bytes)
    if header.get("pack_sha256") != psha:
        _die("raw header pack_sha256 %r != re-emitted pack digest %s"
             % (header.get("pack_sha256"), psha))

    raws_by_qid = {}
    for r in rows:
        q = r.get("qid")
        if q in raws_by_qid:
            _die("duplicate qid %r in raw file" % q)
        raws_by_qid[q] = r
    missing = [q["qid"] for q in queries if q["qid"] not in raws_by_qid]
    extra = set(raws_by_qid) - set(q["qid"] for q in queries)
    if missing or extra:
        _die("raw/eval qid mismatch: %d missing (%s...), %d extra"
             % (len(missing), missing[:3], len(extra)))

    metrics = score_llm_cell(queries, raws_by_qid)
    metrics["retrieval_completeness_violations"] = \
        stats["retrieval_completeness_violations"]
    metrics["gpu_wall_seconds"] = float(header.get("gpu_wall_seconds", 0.0))
    metrics["deterministic_repeat_identical"] = bool(
        header.get("deterministic_repeat_identical", True))

    inst_sha = file_sha256(os.path.join(_HERE, "a5_llm_instrument.py"))
    pins = common_pins(root, inst_sha, psha) if not toy_dir else {
        "instrument": {"observed": inst_sha}, "prompt_pack": {"observed": psha}}
    body = {
        "event": "run", "experiment": EXPERIMENT, "phase": phase,
        "config": {
            "arm": arm, "rung": rung, "seed": 0,
            "model_revision": MODEL_REVISIONS[rung],
            "decode_pins": DECODE_PINS,
            "gpu_class": header.get("gpu_class"),
            "batch_size": header.get("batch_size"),
            "instrument": "tools/experiments/a5_llm_instrument.py",
            "instrument_sha256": inst_sha,
            "pack_sha256": psha,
            "python_version": platform.python_version(),
            "hardware": "modal cloud GPU (class pinned in harness_manifest); "
                        "batched greedy decode (batching disclosed)",
            "scope_note": ("LLM cell of the a5-llm head-to-head; lenient "
                           "pro-LLM extraction instrument (ASM-0012); "
                           "results are indexed to this instrument identity"),
            "toy": bool(toy_dir),
        },
        "metrics": metrics,
        "pins_observed": pins,
        "cost": {"usd": float(header.get("usd", 0.0))},
        "exit": "ok",
        "error": None,
    }
    finish_body(body, root)


def _json_roundtrip(obj):
    return json.loads(json.dumps(obj))


def run_emit_prompts(root, out_path):
    gl = load_glossary(root)
    queries = load_eval(root)
    world = [r for _n, r in _iter_world(root)]
    pack_bytes, header, stats = emit_pack(root, queries, world, gl)
    with open(out_path, "wb") as f:
        f.write(pack_bytes)
    print(json.dumps({"pack_sha256": pack_digest(pack_bytes),
                      "path": out_path, "n_prompts": header["n_prompts"],
                      "stats": stats}, sort_keys=True))
    if stats["retrieval_completeness_violations"]:
        sys.stderr.write("a5_llm_instrument: completeness lint FAILED "
                         "(%d violations) — FK-A5L-2 option (b) must be "
                         "resolved before freeze\n"
                         % stats["retrieval_completeness_violations"])
        sys.exit(2)


def run_emit_toy(root, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    gl = load_glossary(root)
    world, ents = toy_world(gl)
    oracle = build_toy_oracle(root, world)
    queries = toy_expected(oracle, toy_probe_queries(gl, ents))
    wp = os.path.join(out_dir, "toy-world.jsonl")
    qp = os.path.join(out_dir, "toy-queries.jsonl")
    pp = os.path.join(out_dir, "toy-pack.jsonl")
    with open(wp, "w", encoding="utf-8") as f:
        for r in world:
            f.write(_dumps(r) + "\n")
    with open(qp, "w", encoding="utf-8") as f:
        for r in queries:
            f.write(_dumps(r) + "\n")
    pack_bytes, header, stats = emit_pack(root, queries, world, gl, toy=True)
    with open(pp, "wb") as f:
        f.write(pack_bytes)
    n_cov = sum(1 for q in queries if q["class"] == "covered")
    print(json.dumps({"toy_pack_sha256": pack_digest(pack_bytes),
                      "dir": out_dir, "n_queries": len(queries),
                      "n_covered": n_cov, "n_control": len(queries) - n_cov,
                      "stats": stats}, sort_keys=True))
    if stats["retrieval_completeness_violations"]:
        _die("toy completeness lint failed: %s" % stats["violating_qids"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=CPU_ARMS + LLM_ARMS)
    ap.add_argument("--rung", choices=RUNGS)
    ap.add_argument("--phase", default="final",
                    choices=("smoke", "mock", "exploratory", "final"))
    ap.add_argument("--root", default=None)
    ap.add_argument("--emit-prompts", action="store_true")
    ap.add_argument("--emit-toy", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--raw", default=None)
    ap.add_argument("--toy", default=None,
                    help="toy directory (score toy raws against the toy pack)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(_HERE))

    if args.emit_prompts:
        if not args.out:
            _die("--emit-prompts requires --out")
        run_emit_prompts(root, args.out)
    elif args.emit_toy:
        if not args.out:
            _die("--emit-toy requires --out")
        run_emit_toy(root, args.out)
    elif args.score:
        if not (args.arm and args.rung and args.raw):
            _die("--score requires --arm, --rung and --raw")
        run_score(root, args.arm, args.rung, args.raw, args.phase, args.toy)
    elif args.arm in CPU_ARMS:
        run_cpu(root, args.arm, args.phase)
    else:
        _die("nothing to do: pass --emit-prompts / --emit-toy / --score / "
             "--arm engine|abstain-all|answer-all")


if __name__ == "__main__":
    main()
