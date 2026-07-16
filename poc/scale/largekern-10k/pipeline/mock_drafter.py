#!/usr/bin/env python3
"""mock_drafter.py — component 8 (half 2): the MOCK GPT-5.6 drafter.

Deterministic ($0, no network): every behaviour is a pure function of
sha256(conceptId) — reruns are byte-stable, so the Batch input/output files
are reproducible and the idempotency tests can assert byte-level facts.

Returns plausible candidate explications in the BLOCK-4 output protocol
({"gloss", "explication"} | {"cannot_draft": ...}), with DELIBERATE failure
modes at pinned rates so the acceptance stack, repair waves (R=2, §2.3),
quarantine paths, and §10.4 provider-retry policy are all exercised
[STIPULATED ASM-2496 — mock mix, designer-20]:

  bucket (per 10,000 of sha-space)      wave-0 behaviour        repair path
  [   0, 8800)  valid                   good draft              —
  [8800, 9200)  invalid AST             bad prime / undeclared  fixed at wave1
                                        ref / out-of-catalog    (70%), wave2
                                        conceptHead             (20%), never (10%)
  [9200, 9400)  gloss lint fail         too-short or circular   same schedule
  [9400, 9550)  malformed JSON          truncated output        fixed at wave1
  [9550, 9650)  abstention              {"cannot_draft": ...}   terminal (§2.3)
  [9650,10000)  provider transient      error line (500)        succeeds on
                                                                retry; 1/12 of
                                                                the bucket
                                                                fails forever
                                                                -> PROVIDER_FAILED

Usage fabrication carries the REGISTERED §5.2 planning figures (prefix ~8k
tokens cached after the first request per job, suffix ~1.2k, output ~600-900)
so κ and the settlement ledger read like the registered model — never mock
inventions (F1-K round-6 lesson).

The valid-draft ASTs use the three validated profile-1 template families
(InstanceSchema / WhenTrue / RelationalSchema — frame-implicit referent 1,
extra referents bound once); ~1 in 5 references a pinned-catalog conceptHead
to exercise catalog closure + opts.concepts injection (§7.1).
"""

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

# a few catalog ids for conceptHead references (kernel-v0; encodable defs)
CATALOG_REFS = ["urn:kernel-v0:afraid", "urn:kernel-v0:alive", "urn:kernel-v0:begin"]

OPENERS = [
    "In this sense the word picks out",
    "Under this reading the term names",
    "Here the expression designates",
    "This sense covers",
    "What falls under this concept is",
    "The concept at issue here is",
]
CLOSERS = [
    "The mark of the concept is what it does or undergoes, not how it is named.",
    "Nothing falls under it merely by resemblance; the defining condition must hold.",
    "Neighbouring senses differ in what they require, not in the word they share.",
    "A borderline case counts only when the stated condition is satisfied.",
    "The condition is intensional: it says what something must be, not which things happen to satisfy it.",
    "So understood, the concept applies independently of any particular example.",
]


def _h(concept_id, salt=""):
    return int(hashlib.sha256(("kv1d-mock|%s|%s" % (salt, concept_id)).encode("utf-8")).hexdigest(), 16)


def bucket(concept_id):
    n = _h(concept_id) % 10000
    if n < 8800:
        return "valid"
    if n < 9200:
        return "invalid_ast"
    if n < 9400:
        return "gloss_lint"
    if n < 9550:
        return "malformed"
    if n < 9650:
        return "abstain"
    return "provider"


def repair_fixed_at(concept_id):
    """For repairable buckets: wave at which the mock 'model' fixes the draft
    (1, 2, or None = never; exhausts the R=2 budget)."""
    r = _h(concept_id, "repair") % 10
    return 1 if r < 7 else (2 if r < 9 else None)


def provider_permanent(concept_id):
    return _h(concept_id, "provider") % 12 == 0


# ------------------------------------------------------------- draft content

def _clean_words(text, ban):
    ban_l = {b.lower() for b in ban}
    return [w for w in _WORD_RE.findall(text)
            if w.lower() not in ban_l and not any(w.lower().startswith(b) and len(w) - len(b) <= 2 for b in ban_l)]


def make_gloss(concept_id, lemma, pos, wn_gloss, broken=None):
    """Scholarly-register mock gloss: 15-100 words, non-circular (headword and
    near-variants excluded), varied openings/closings by hash — deliberately
    NOT one fixed template. broken='short'|'circular' produces lint failures."""
    h = _h(concept_id, "gloss")
    if broken == "short":
        return "too short to pass the gloss lint gate"
    core = _clean_words(wn_gloss, [lemma] + lemma.split("_"))[:40]
    opener = OPENERS[h % len(OPENERS)]
    closer = CLOSERS[(h // 7) % len(CLOSERS)]
    kind = {"n": "a kind of thing", "v": "a kind of happening or doing",
            "a": "a way something can be", "r": "a way something is done"}.get(pos, "a concept")
    body = " ".join(core) if core else "what the aligned source characterizes for this sense"
    gloss = "%s %s: %s. %s" % (opener, kind, body, closer)
    words = gloss.split()
    if len(words) > common.GLOSS_MAX_WORDS:
        gloss = " ".join(words[:common.GLOSS_MAX_WORDS - len(closer.split())]) + " " + closer
    if len(gloss.split()) < common.GLOSS_MIN_WORDS:
        gloss += " It holds of something only when the stated condition is true of it at the relevant time."
    if broken == "circular":
        gloss = gloss + " In short, it is %s in the %s way." % (lemma.replace("_", " "), lemma.replace("_", " "))
    return gloss


def _sp(prime, **kw):
    d = {"kind": "sp", "head": {"kind": "primeHead", "prime": prime}}
    d.update(kw)
    return d


def make_ast(concept_id, pos, broken=None):
    """A valid profile-1 kot-ast/1 explication varied by hash; broken variants
    produce the pinned validator failures."""
    h = _h(concept_id, "ast")
    quant = ["ONE", "TWO", "SOME", "ALL"][h % 4]
    mod = ["GOOD", "BAD", "BIG", "SMALL"][(h // 4) % 4]
    use_concept = (h % 5 == 0)
    cref = CATALOG_REFS[h % len(CATALOG_REFS)]
    if pos == "n":
        clauses = [
            {"type": "pred", "pred": "THERE-IS", "roles": {"undergoer": {"kind": "ref", "index": 1}}},
            {"type": "pred", "pred": "BE-SOMEWHERE",
             "roles": {"undergoer": {"kind": "ref", "index": 1},
                       "locus": _sp("WHERE~PLACE", det="THIS")}},
            {"type": "op", "op": "CAN", "args": [
                {"type": "pred", "pred": "SEE",
                 "roles": {"experiencer": _sp("PEOPLE"),
                           "stimulus": {"kind": "ref", "index": 1}}}]},
        ]
        if use_concept:
            clauses.append({"type": "pred", "pred": "THINK",
                            "roles": {"experiencer": _sp("SOMEONE", quant="SOME"),
                                      "topic": {"kind": "sp", "head": {"kind": "conceptHead", "id": cref}}}})
        ast = {"schema": "kot-ast/1", "frame": "InstanceSchema",
               "referents": [{"index": 1, "refKind": "SomethingRef"}], "clauses": clauses}
    elif pos == "v":
        ast = {"schema": "kot-ast/1", "frame": "WhenTrue",
               "referents": [{"index": 1, "refKind": "SomethingRef"},
                             {"index": 2, "refKind": "SomeoneRef"}],
               "clauses": [
                   {"type": "pred", "pred": "DO",
                    "roles": {"agent": _sp("SOMEONE", quant="SOME", bind=2),
                              "undergoer": {"kind": "ref", "index": 1}}},
                   {"type": "op", "op": "BECAUSE", "args": [
                       {"type": "pred", "pred": "WANT",
                        "roles": {"experiencer": {"kind": "ref", "index": 2},
                                  "complement": {"kind": "ref", "index": 1}}},
                       {"type": "pred", "pred": "FEEL",
                        "roles": {"experiencer": {"kind": "ref", "index": 2},
                                  "attribute": {"kind": "prime", "prime": mod if mod in ("GOOD", "BAD") else "GOOD"}}}]},
               ]}
    else:  # a / r — two-place relational schema
        clauses = [
            {"type": "pred", "pred": "THINK",
             "roles": {"experiencer": {"kind": "ref", "index": 1},
                       "topic": ({"kind": "sp", "head": {"kind": "conceptHead", "id": cref}}
                                 if use_concept else _sp("SOMETHING~THING", quant=quant))}},
            {"type": "pred", "pred": "SEE",
             "roles": {"experiencer": {"kind": "ref", "index": 1},
                       "stimulus": {"kind": "ref", "index": 2}}},
        ]
        ast = {"schema": "kot-ast/1", "frame": "RelationalSchema",
               "referents": [{"index": 1, "refKind": "SomeoneRef"},
                             {"index": 2, "refKind": "SomethingRef"}], "clauses": clauses}
    if broken == "bad_prime":
        ast = json.loads(json.dumps(ast))
        ast["clauses"][0] = {"type": "pred", "pred": "THERE-IS",
                             "roles": {"undergoer": _sp("ZORPLE")}}
    elif broken == "bad_ref":
        ast = json.loads(json.dumps(ast))
        ast["clauses"].append({"type": "pred", "pred": "DIE",
                               "roles": {"undergoer": {"kind": "ref", "index": 31}}})
    elif broken == "out_of_catalog":
        ast = json.loads(json.dumps(ast))
        ast["clauses"].append({"type": "pred", "pred": "THINK",
                               "roles": {"experiencer": _sp("SOMEONE", quant="SOME"),
                                         "topic": {"kind": "sp", "head": {"kind": "conceptHead",
                                                                          "id": "urn:kernel-v1-draft:not-in-catalog@v1"}}}})
    return ast


# ------------------------------------------------------------ batch response

class MockDrafter(object):
    """respond(request_line) -> Batch output line. Wave/repair awareness comes
    from the suffix text (REPAIR CONTEXT marker), not hidden state, so the
    provider mock stays stateless and restart-safe."""

    def __init__(self, worklist_by_custom_id):
        self.rows = worklist_by_custom_id   # custom_id -> worklist row

    def _usage(self, concept_id, line_no, output_tokens):
        cached = 0 if line_no == 0 else 8000      # first request per job = prefix population (§3)
        input_tokens = 8000 + 1200 + (_h(concept_id, "sufjit") % 120)
        return {"input_tokens": input_tokens,
                "input_tokens_details": {"cached_tokens": cached},
                "output_tokens": output_tokens,
                "prefix_write": line_no == 0}

    def respond(self, req, batch_id, line_no, meta=None):
        cid = req["custom_id"]
        row = self.rows.get(cid)
        if row is None:
            return {"custom_id": cid, "response": None,
                    "error": {"code": "unknown_custom_id", "message": "mock: unmatched correlation id"}}
        concept_id = row["conceptId"]
        suffix = req["body"]["input"][-1]["content"]
        if "REPAIR CONTEXT — repair wave 2" in suffix:
            wave = 2
        elif "REPAIR CONTEXT — repair wave 1" in suffix:
            wave = 1
        else:
            # provider retries ride follow-up jobs with the ORIGINAL draft
            # suffix (§10.4 — not content repairs); the job's wave ordinal
            # arrives via the batch metadata the orchestrator set at create.
            wave = int((meta or {}).get("wave", 0))
        b = bucket(concept_id)

        # provider-transient bucket: error on the first attempt; the §10.4
        # retry (re-inclusion in a follow-up job) succeeds unless permanent
        if b == "provider" and (wave == 0 or provider_permanent(concept_id)):
            return {"custom_id": cid, "response": None,
                    "error": {"code": "server_error", "message": "mock transient provider failure"}}

        broken = None
        if b == "invalid_ast":
            fixed_at = repair_fixed_at(concept_id)
            if fixed_at is None or wave < fixed_at:
                broken = ["bad_prime", "bad_ref", "out_of_catalog"][_h(concept_id, "brk") % 3]
        elif b == "gloss_lint":
            fixed_at = repair_fixed_at(concept_id)
            if fixed_at is None or wave < fixed_at:
                broken = ["short", "circular"][_h(concept_id, "brk") % 2]
        elif b == "malformed" and wave == 0:
            text = '{"gloss": "this output is deliberately trunca'
            return self._ok(cid, concept_id, line_no, text)
        elif b == "abstain":
            text = common.canonical_dumps(
                {"cannot_draft": {"reason": "mock: this synset is stipulated non-explicable in profile-1"}})
            return self._ok(cid, concept_id, line_no, text)

        gloss_broken = broken if broken in ("short", "circular") else None
        ast_broken = broken if broken in ("bad_prime", "bad_ref", "out_of_catalog") else None
        payload = {
            "gloss": make_gloss(concept_id, row["lemma"], row["pos"], row["wnGloss"], broken=gloss_broken),
            "explication": make_ast(concept_id, row["pos"], broken=ast_broken),
        }
        return self._ok(cid, concept_id, line_no, common.canonical_dumps(payload))

    def _ok(self, cid, concept_id, line_no, output_text):
        out_tokens = 550 + _h(concept_id, "otok") % 350
        return {
            "custom_id": cid,
            "response": {
                "status_code": 200,
                "request_id": "mockreq_" + hashlib.sha256(
                    ("%s|%s|%d" % (cid, concept_id, line_no)).encode()).hexdigest()[:20],
                "body": {
                    "model": common.MODEL_SNAPSHOT_ID,
                    "output_text": output_text,
                    "usage": self._usage(concept_id, line_no, out_tokens),
                },
            },
            "error": None,
        }
