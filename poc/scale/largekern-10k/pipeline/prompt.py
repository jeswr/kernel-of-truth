#!/usr/bin/env python3
"""prompt.py — component 2: REQUEST BUILDER (spec §2.2 authoring blindness,
§3 cache-breakpoint structure, §5.3 gen settings).

Builds, per synset, the deterministic GPT-5.6 Batch drafting request:

* STABLE PREFIX (§3, unchanged-in-substance ASM-2428): four invariant blocks —
  (1) NSM grammar contract, (2) profile-1 lexicon + pinned ref catalog,
  (3) few-shot exemplars, (4) lint contract — deterministically serialized and
  content-hashed (cachePrefixHash). MOCK note: block (3) is an explicitly
  labelled PLACEHOLDER pending the P2 exemplar review (§9.4 — the g9 50 are
  BANNED as exemplars; no g9 bytes appear here). The prefix is re-frozen with
  the k<=8 reviewed passers before prereg-freeze; that changes cachePrefixHash
  deliberately (a contract bump). [STIPULATED ASM-2496]
* VARIABLE SUFFIX: headword + synset id + aligned WN gloss (pinned source
  extracts; the pilot's only extract IS the WN gloss row). Repair suffix =
  previous draft + the real ERR_* list (§2.3).
* Request bytes: canonical JSON (sorted keys, compact) — byte-deterministic.
  custom_id = the row's idempotencyKey (correlation within one job's input
  file ONLY, never cross-submission dedup — §6.1).

Blindness (§2.2, binding): the prompt contains ONLY headword + synset id +
WN gloss + the cached contract blocks. It never contains benchmark items,
other kernel explications beyond the pinned ref catalog, coverage rank, or
model-performance data.
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

POS_NAME = {"n": "noun", "v": "verb", "a": "adjective", "r": "adverb"}

# ---------------------------------------------------------------- ref catalog


def load_catalog():
    """Pinned ref catalog = kernel-v0 + molecules-v0 ids at their committed
    manifest state (§4.1 catalog-closure lint). Returns (ids, labels, defs)
    where defs maps kernel-v0 ids -> explication AST (for shard-encode
    injection via opts.concepts, §7.1)."""
    ids, labels, defs = [], {}, {}
    kdir = os.path.join(common.REPO_ROOT, "data", "kernel-v0", "concepts")
    for fn in sorted(os.listdir(kdir)):
        if not fn.endswith(".json"):
            continue
        d = common.read_json(os.path.join(kdir, fn))
        ids.append(d["id"])
        labels[d["id"]] = d.get("label", "")
        if isinstance(d.get("explication"), dict):
            defs[d["id"]] = d["explication"]
    mdir = os.path.join(common.REPO_ROOT, "data", "molecules-v0", "molecules")
    for fn in sorted(os.listdir(mdir)):
        if not fn.endswith(".json"):
            continue
        d = common.read_json(os.path.join(mdir, fn))
        ids.append(d["id"])
        labels[d["id"]] = d.get("label", "")
        if isinstance(d.get("explication"), dict):
            defs[d["id"]] = d["explication"]
    return ids, labels, defs


# ------------------------------------------------------------ prefix blocks

_GRAMMAR_BLOCK = """\
## BLOCK 1 — NSM grammar contract (kot-ast/1, profile-1; fail-closed)

You draft candidate NSM explications as kot-ast/1 JSON. The validator is a
pure function and REJECTS anything outside this grammar; a rejection returns
the real ERR_* codes to you for at most 2 repairs, then the draft is
quarantined. Rules:
- explication = {"schema":"kot-ast/1","frame":F,"referents":[...],"clauses":[...]}
  with F one of InstanceSchema (thing-like), WhenTrue (situation/predication),
  RelationalSchema (two-place relation).
- Referent 1 (and 2 for RelationalSchema) is the definiendum, introduced by
  the frame itself: refer to it with {"kind":"ref","index":1}; NEVER bind it.
  Further referents are introduced exactly once via "bind" on a substantive
  phrase, then referenced by index. Indices are dense from 1; max 32.
- Clauses are predicate clauses {"type":"pred","pred":P,"roles":{...}} over
  the profile-1 predicate valency frames, or operator clauses
  {"type":"op","op":OP,"args":[...]} (NOT, CAN, MAYBE, BECAUSE, IF, ...).
  Caps: 32 clauses (quotes included), depth 12.
- Every prime must be in the 65-prime profile-1 lexicon (BLOCK 2). Concept
  references use {"kind":"conceptHead","id":URN} and MUST come from the
  pinned ref catalog (BLOCK 2) — any other id is ERR_REF_OUTSIDE_CATALOG.
  Drafts are leaf nodes: never reference another draft.
"""

_LINT_BLOCK = """\
## BLOCK 4 — lint contract + output protocol (gloss standard 1-9; fail-closed)

Alongside the AST you write a scholarly GLOSS. The standard is the
programme's first-rate-scholar bar — a candidate explication that reads as if
written by a careful lexicographer-semanticist, NOT templated or mechanical
prose:
1. 15-100 words, at most 128 tokens; a single self-contained paragraph.
2. NON-CIRCULAR: never use the headword (or a trivial morphological variant)
   inside the gloss.
3. Intension first: state what makes something fall under the concept, not
   examples, not etymology, not encyclopedic trivia.
4. Distinguish the concept from its nearest neighbours where the WordNet
   gloss invites confusion; keep the synset's exact sense, never a broader or
   narrower one.
5. Plain scholarly register: no hedging boilerplate, no "refers to", no
   dictionary-ese ("of or pertaining to"), no bullet lists, varied openings —
   mechanical sameness across drafts is a defect.
6. The gloss and the AST must express the SAME analysis (a human reviewer
   checks AST/prose consistency as one of four binaries).
7. No text overlapping any evaluation item (an 8-token overlap is a hard
   reject; you never see eval items, so simply never quote long passages).
8. English only; no markdown; no quotation of the WordNet gloss verbatim
   beyond 7 consecutive tokens.
9. If the synset cannot be explicated in profile-1 (institutional trivia,
   pure proper-name residue, taxonomic placeholder), return the abstention
   object instead — abstention is honest and terminal, never penalized into
   a bad draft.

OUTPUT PROTOCOL (strict): return EXACTLY ONE JSON object, no fences, no
commentary: {"gloss": "<paragraph>", "explication": {<kot-ast/1>}} or
{"cannot_draft": {"reason": "<one sentence>"}}. Your draft is a CANDIDATE:
it lands as an immutable ModelDrafted record, validator-gated, never final;
only a later individual human endorsement can mint an Explicated record.
"""

_EXEMPLAR_BLOCK_MOCK = """\
## BLOCK 3 — few-shot exemplars [PLACEHOLDER — PENDING P2 REVIEW]

MOCK BUILD NOTE (binding): the real prefix carries k<=8 kernel-v0 exemplars
that PASSED the full 4-binary human review (spec §9.4; the g9 records are
banned — blinded_review_done=0). That review (P2) has not run yet, so this
mock prefix carries ONE schematic, clearly-synthetic exemplar to pin the
output shape only. Re-freezing the prefix with the reviewed exemplars is a
deliberate cachePrefixHash change before prereg-freeze.

Exemplar (schematic shape only, not a reviewed record):
{"gloss": "Something of this kind is a bounded, self-standing object in the world; people can see it and touch it, it stays the same thing for a long time, and when something happens to one part of it, people think of the whole as involved.", "explication": {"schema": "kot-ast/1", "frame": "InstanceSchema", "referents": [{"index": 1, "refKind": "SomethingRef"}], "clauses": [{"type": "pred", "pred": "THERE-IS", "roles": {"undergoer": {"kind": "ref", "index": 1}}}, {"type": "op", "op": "CAN", "args": [{"type": "pred", "pred": "SEE", "roles": {"experiencer": {"kind": "sp", "head": {"kind": "primeHead", "prime": "PEOPLE"}}, "stimulus": {"kind": "ref", "index": 1}}}]}]}}
"""


def build_prefix(catalog_ids, catalog_labels, primes):
    """The four invariant blocks, deterministically serialized (§3)."""
    lex_lines = ["## BLOCK 2 — profile-1 lexicon (65 primes) + pinned ref catalog", "",
                 "PRIMES (closed; anything else is ERR_PRIME_UNKNOWN):",
                 " ".join(primes), "",
                 "REF CATALOG (closed; conceptHead ids MUST come from this list):"]
    lex_lines += ["  %s  (%s)" % (cid, catalog_labels.get(cid, "")) for cid in catalog_ids]
    blocks = [
        "# GPT-5.6 drafting contract — kernel-v1 WordNet-10k pilot (kernel-v1-draft/1)",
        _GRAMMAR_BLOCK,
        "\n".join(lex_lines) + "\n",
        _EXEMPLAR_BLOCK_MOCK,
        _LINT_BLOCK,
    ]
    text = "\n".join(blocks)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def draft_suffix(row):
    """Variable suffix (§2.2: headword + synset id + WN gloss ONLY)."""
    return (
        "DRAFT TASK\n"
        "headword: %s\n"
        "synset: %s (%s)\n"
        "wordnet gloss (aligned; annotation only, do not quote verbatim): %s\n"
        "Write the scholarly gloss and the kot-ast/1 explication for exactly "
        "this sense. Return the single JSON object per the output protocol."
        % (row["lemma"], row["conceptId"], POS_NAME.get(row["pos"], row["pos"]), row["wnGloss"])
    )


def repair_suffix(row, previous_output_text, err_codes, wave=1):
    """§2.3: the repair call carries the previous draft + the REAL ERR_* list.
    The wave ordinal is stated in-band (repair waves are follow-up Batch jobs,
    §6.0)."""
    return (
        draft_suffix(row)
        + "\n\nREPAIR CONTEXT — repair wave %d of R=%d (attempt under the R=2 repair budget)\n" % (wave, common.R_REPAIR)
        + "your previous output:\n" + previous_output_text
        + "\nvalidator/lint failures (fail-closed, fix ALL):\n"
        + "\n".join("  - %s" % c for c in err_codes)
    )


class RequestBuilder(object):
    def __init__(self):
        self.catalog_ids, self.catalog_labels, self.catalog_defs = load_catalog()
        self.primes = self._load_primes()
        self.prefix_text, self.cache_prefix_hash = build_prefix(
            self.catalog_ids, self.catalog_labels, self.primes)
        self.gen_settings = dict(common.GEN_SETTINGS)
        self.gen_settings_hash = common.canonical_sha256(self.gen_settings)
        self.lint_contract = {
            "glossWords": [common.GLOSS_MIN_WORDS, common.GLOSS_MAX_WORDS],
            "glossMaxTokensProxy": common.GLOSS_MAX_TOKENS,
            "leakageShingle": common.LEAKAGE_SHINGLE,
            "nonCircular": True, "catalogClosed": True,
        }
        self.lint_hash = common.canonical_sha256(self.lint_contract)

    @staticmethod
    def _load_primes():
        """The 65-prime profile-1 lexicon, read from the committed encoder
        lexicon data (encoder/ is the single source; never re-typed)."""
        lex = os.path.join(common.REPO_ROOT, "encoder", "dist", "src", "lexicon.js")
        import subprocess
        out = subprocess.check_output(
            ["node", "-e",
             "const l=require(%s);console.log(JSON.stringify(l.PRIMES.map(p=>p.name||p)))"
             % json.dumps(lex)])
        primes = json.loads(out.decode("utf-8"))
        if len(primes) != 65:
            raise common.PipelineError("ERR_LEXICON", "expected 65 primes, got %d" % len(primes))
        return primes

    def request_body(self, suffix_text):
        """OpenAI Batch line body for /v1/responses (§3: prompt_cache_key
        routes the shared prefix; the full prefix BYTES ride every line —
        no cross-request dedup in the input file)."""
        return {
            "model": common.MODEL_SNAPSHOT_ID,
            "input": [
                {"role": "developer", "content": self.prefix_text},
                {"role": "user", "content": suffix_text},
            ],
            "max_output_tokens": self.gen_settings["max_output_tokens"],
            "prompt_cache_key": "kv1d-" + self.cache_prefix_hash[:32],
        }

    def build_line(self, row, custom_id, wave=0, previous_output=None, err_codes=None):
        """One deterministic Batch input line. Returns (line_bytes, promptHash)."""
        suffix = (draft_suffix(row) if wave == 0 or not err_codes
                  else repair_suffix(row, previous_output or "", err_codes, wave=wave))
        body = self.request_body(suffix)
        prompt_hash = hashlib.sha256(
            (self.prefix_text + "\x1e" + suffix).encode("utf-8")).hexdigest()
        line = common.canonical_dumps({
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/responses",
            "body": body,
        }) + "\n"
        return line.encode("utf-8"), prompt_hash

    def version_ids(self, row):
        """(versionHash, idempotencyKey) for a worklist row at conceptVersion 1
        (§6.1). promptHash here is the DRAFT-call prompt hash — repairs share
        the row identity (same (conceptId, conceptVersion))."""
        _, prompt_hash = self.build_line(row, "probe", wave=0)
        vh = common.version_hash(
            row["sourceRowSha256"], prompt_hash, self.cache_prefix_hash,
            common.MODEL_SNAPSHOT_ID, self.gen_settings_hash,
            self._validator_hash(), self.lint_hash)
        return vh, common.idempotency_key(vh)

    _VALIDATOR_HASH = None

    @classmethod
    def _validator_hash(cls):
        """The encoder content-hash pin (encoder/'s own encoderPin), §8
        validatorHash. Read once from the committed encoder dist."""
        if cls._VALIDATOR_HASH is None:
            import subprocess
            out = subprocess.check_output(
                ["node", "-e",
                 "const e=require(%s);console.log(JSON.stringify(e.encoderPin()))"
                 % json.dumps(os.path.join(common.REPO_ROOT, "encoder", "dist", "src", "index.js"))])
            pin = json.loads(out.decode("utf-8"))
            cls._VALIDATOR_HASH = pin.get("contentHash") or common.canonical_sha256(pin)
        return cls._VALIDATOR_HASH


if __name__ == "__main__":
    rb = RequestBuilder()
    print("cachePrefixHash", rb.cache_prefix_hash)
    print("genSettingsHash", rb.gen_settings_hash)
    print("lintHash       ", rb.lint_hash)
    print("validatorHash  ", rb._validator_hash())
    print("catalog ids    ", len(rb.catalog_ids), "prefix bytes", len(rb.prefix_text))
    row = {"conceptId": "urn:lexical-wn31:n-00001740", "lemma": "entity", "pos": "n",
           "wnGloss": "that which is perceived...", "sourceRowSha256": "0" * 64}
    b1, p1 = rb.build_line(row, "kv1d-test")
    b2, p2 = rb.build_line(row, "kv1d-test")
    assert b1 == b2 and p1 == p2, "request bytes must be deterministic"
    print("deterministic  OK (%d bytes/line)" % len(b1))
