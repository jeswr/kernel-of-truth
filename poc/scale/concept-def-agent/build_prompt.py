#!/usr/bin/env python3
"""
build_prompt.py -- deterministically (re)generate concept-def-prompt.md, the
stateless system prompt of the single-concept kernel-v1 definition agent.

Sources (nothing is hand-copied, so the prompt cannot drift):
  * the encoder's CLOSED grammar inventories, dumped live from
    encoder/dist/src/index.js (65 primes, predicate valency frames, operators,
    SP sub-inventories, referent kinds, frames, caps);
  * the 6 BEST pilot records (pilot-review.md: bar 'meets'; the maintainer's
    named exemplar set lover/appearance/peer/exit/fidelity/throw), reshaped to
    the kernel-v1 output schema and embedded as few-shot examples with their
    explications byte-identical to data/kernel-v1-pilot/concepts/*.json.

Governance: benchmark-blind (reads only pilot records + encoder inventories;
no eval items, no model outcomes). $0. No git, no registry, no freeze.
Author: designer-34.
"""
import hashlib
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PILOT = ROOT / "data/kernel-v1-pilot/concepts"
OUT = HERE / "concept-def-prompt.md"

# The maintainer's exemplar set (pilot-review.md; all bar='meets').
FEWSHOT = ["lover", "appearance", "peer", "exit", "fidelity", "throw"]


def slugify(label: str) -> str:
    """The frozen slug rule (stated verbatim in the prompt): drop apostrophes,
    then map every run of non-[a-z0-9] to '-', trim '-'."""
    s = label.lower().replace("'", "").replace("’", "")
    out, dash = [], False
    for ch in s:
        if ch.isascii() and (ch.isalnum()):
            out.append(ch)
            dash = False
        elif not dash:
            out.append("-")
            dash = True
    return "".join(out).strip("-")


# ---- dump the closed inventories from the encoder (single source of truth) --
NODE_DUMP = r"""
import('%s').then(m => {
  const primes = m.PRIMES.map(p => ({name: p.name, category: p.category}));
  console.log(JSON.stringify({
    primes,
    frames: m.PREDICATE_FRAMES,
    operators: m.OPERATORS,
    arity: m.OPERATOR_ARITY,
    opClass: m.OPERATOR_CLASS,
    dets: m.SP_DETERMINERS,
    quants: m.SP_QUANTIFIERS,
    mods: m.SP_MODS,
    intens: m.INTENSIFIERS,
    substHeads: m.SUBSTANTIVE_HEADS,
    durations: m.DURATION_FILLERS,
    refKinds: m.REF_KINDS,
    explFrames: m.EXPLICATION_FRAMES,
    caps: m.CAPS,
    schema: m.AST_SCHEMA,
  }));
});
""" % (ROOT / "encoder/dist/src/index.js").as_posix()

INV = json.loads(subprocess.run(
    ["node", "-e", NODE_DUMP], capture_output=True, text=True, check=True,
    cwd=ROOT / "encoder").stdout)
assert len(INV["primes"]) == 65, "prime lexicon drift"
assert INV["schema"] == "kot-ast/1", "AST schema drift"

# ---- render inventory sections ----------------------------------------------
by_cat = {}
for p in INV["primes"]:
    by_cat.setdefault(p["category"], []).append(p["name"])
primes_md = "\n".join(
    f"- {cat}: " + ", ".join(f"`{n}`" for n in names)
    for cat, names in by_cat.items())

frame_rows = []
for f in INV["frames"]:
    req = [s for s in f["slots"] if s["required"]]
    opt = [s for s in f["slots"] if not s["required"]]
    fmt = lambda ss: ", ".join(f"`{s['role']}` ({s['kind']})" for s in ss) or "—"
    frame_rows.append(f"| `{f['pred']}` | {fmt(req)} | {fmt(opt)} |")
frames_md = ("| predicate | REQUIRED roles (slot kind) | optional roles |\n"
             "|---|---|---|\n" + "\n".join(frame_rows))

OP_DESC = {
    "clause1": "1 arg: a clause",
    "clause2": "2 args: clause, clause",
    "compare2": "2 args: each an SP, a ref, or a clause",
    "temporal2": "2 args: anchor (time SP / ref / `NOW` prime filler), then a clause",
    "overMod1": "1 arg: a mod prime filler (`GOOD`/`BAD`/`BIG`/`SMALL`)",
    "overModOrQuant1": "1 arg: a mod or quantifier prime filler",
}
ops_md = "\n".join(
    f"- `{op}` — {OP_DESC[INV['opClass'][op]]}" for op in INV["operators"])

SLOT_KIND_MD = """\
Slot kinds (what may fill a role):
- `entity` — an SP, `{"kind":"ref","index":n}`, `{"kind":"concept","id":...}`, or the indexical primes `I`/`YOU` as `{"kind":"prime","prime":"I"}`.
- `clause` — `{"kind":"clause","clause":<clause>}`.
- `entityOrClause` — either of the above (WANT / DON'T-WANT complements).
- `quote` — `{"kind":"quote","clauses":[<clause>...]}` (re-anchors `I`/`NOW` to the quoted thinker/speaker/moment).
- `attributeGoodBad` — exactly `{"kind":"prime","prime":"GOOD"}` or `"BAD"` (the only legal FEEL attribute).
- `attributeSpec` — an SP (typically a `kindFrame` head) or concept ref (BE-SPEC attribute).
- `clauseRefOrQuote` — a ref to a ClauseRef referent, a quote, or an embedded clause (TRUE undergoer).
- `firstPerson` — exactly `{"kind":"prime","prime":"I"}` (IS-MINE possessor).

Adjunct roles — EVERY predicate additionally admits:
- `time` — SP / ref / `{"kind":"prime","prime":"NOW"}` / temporal-anchor filler `{"kind":"temporal","op":"AFTER"|"BEFORE","anchor":<time SP|ref|NOW>}`.
- `duration` — one of the duration primes as `{"kind":"prime","prime":"A-LONG-TIME"|"A-SHORT-TIME"|"FOR-SOME-TIME"|"MOMENT"}`, or an SP.
- `place` — SP / ref / `{"kind":"prime","prime":"HERE"}`.
- `manner` — SP / ref / prime filler (e.g. `INSIDE`, `ABOVE`, `FAR`, `NEAR`) / concept ref.\
"""

# ---- few-shot examples from the pilot's best records -------------------------
examples = []
for slug in FEWSHOT:
    src = json.loads((PILOT / f"{slug}.json").read_text())
    prov = src["provenance"]
    concept_word = prov["wn31_lemmas"][0]
    rec = {
        "id": f"urn:kernel-v1:{slugify(concept_word)}",
        "label": src["label"],
        "synset": prov["wn31_synset"],
        "pattern": src["pattern"],
        "gloss": src["gloss"],
        "explication": src["explication"],  # byte-faithful to the pilot AST
        "references": [],
        "status": "draft",
        "notes": src["notes"],
    }
    inp = (f"concept: {concept_word}\n"
           f"synset: {prov['wn31_synset']}\n"
           f"pos: {prov['wn31_pos']}\n"
           f"lemmas: {', '.join(prov['wn31_lemmas'])}\n"
           f"wn31-gloss (sense-fixing only): {prov['source_gloss']}")
    examples.append((inp, json.dumps(rec, indent=1, ensure_ascii=False)))

examples_md = "\n\n".join(
    f"--- EXAMPLE {i} INPUT ---\n{inp}\n--- EXAMPLE {i} OUTPUT ---\n{out}"
    for i, (inp, out) in enumerate(examples, 1))

# ---- the prompt ---------------------------------------------------------------
PROMPT = f"""# kernel-v1 single-concept definition agent (kot-cda/1)

You are a definition author for the Kernel-of-Truth kernel-v1 lexicon: a
first-rate English scholar-lexicographer who also writes machine-checkable
semantic explications in a closed 65-prime metalanguage.

You are STATELESS and handle EXACTLY ONE concept per call. The user message is
a small block of this exact shape:

concept: <the word or phrase to define>
synset: urn:lexical-wn31:<pos>-<8-digit offset>   (the ONE WordNet-3.1 sense meant)
pos: <n|v|a|r>
lemmas: <the synset's lemmas, comma-separated>
wn31-gloss (sense-fixing only): <the WordNet gloss of that synset>

Your ENTIRE reply must be EXACTLY ONE JSON object — the kernel-v1 record —
and NOTHING else: no prose, no markdown fences, no preamble, no trailing
commentary. The reply must parse as a single strict-JSON object.

## 1. The definition (`gloss`) — the scholarly standard

Write the definition as a first-rate English scholar would:

1. **Genus–differentia.** Open with the most apt genus word for the concept
   (person, act, quality, state, event, movement, disposition, ...), then give
   the differentia that picks out exactly this sense and no other.
2. **Most-apt words.** Choose each word for precision, not decoration. Plain,
   exact, unhurried scholarly English. One or two sentences; roughly 15–45
   words.
3. **No circularity.** Never use the headword, its cognates, or a trivial
   derivational variant (define *appearance* without "appear(ing)", *fidelity*
   without "faithful").
4. **Self-contained.** No examples, no quotation fragments, no domain tags in
   parentheses, no cross-references. A reader with no context must grasp the
   full intension.
5. **No unnecessary information and no templated prose.** Include exactly what
   is criterial for the sense; write natural definitional prose, not a
   fill-in-the-blank formula.
6. **This sense only.** The `wn31-gloss` line tells you WHICH sense is meant —
   and nothing more. WordNet glosses are routinely circular, terse, or
   under-specified: do NOT copy one; author the true intension of that sense.
   If the WordNet gloss's genuinely definitional core survives, a light edit
   to the standard above is acceptable. Never widen or narrow the sense, and
   never drift to a more common sense of the same word.

## 2. The output record — kernel-v1 schema (strict JSON)

Emit an object with EXACTLY these nine fields, in this order:

- `id` — `"urn:kernel-v1:<slug>"`. Slug rule (mechanical, from the `concept:`
  input line): lowercase; delete apostrophes; replace every run of other
  non-alphanumeric characters with `-`; trim leading/trailing `-`
  (e.g. `artist's model` → `artists-model`).
- `label` — the concept word exactly as given, optionally followed by a short
  disambiguating parenthetical ONLY when the bare word would suggest the wrong
  sense (e.g. `"wealth (profuse abundance)"`) or the relation needs its
  arguments shown (e.g. `"peer (X is a peer of Y)"`). The label MUST begin
  with the concept word exactly as given.
- `synset` — the input synset URN, verbatim.
- `pattern` — one line naming the structural shape of the explication
  (frame + the key device used).
- `gloss` — the scholarly definition (§1).
- `explication` — the `kot-ast/1` rendering of the gloss (§3).
- `references` — `[]` (always the empty list).
- `status` — `"draft"` (always).
- `notes` — MUST begin `"AST adequacy: faithful — "` or
  `"AST adequacy: lossy — "`, followed by one honest sentence. *Faithful*
  means the explication carries the gloss's genus AND differentia; *lossy*
  means the 65-prime metalanguage cannot carry some criterial part of the
  differentia (say exactly which part, and what the AST renders instead).
  Judge this severely: a merely-plausible skeleton is lossy, not faithful.

## 3. The explication — `kot-ast/1` grammar (closed; validated fail-closed)

The explication is a JSON object:

```
{{"schema": "kot-ast/1", "frame": <frame>, "referents": [...], "clauses": [...]}}
```

It is checked by a mechanical validator (grammar, valency, referent
discipline, caps). Anything outside the closed inventories below is a hard
gate error — there is no other vocabulary, and no way to add any.

### 3.1 Frames and referents

Frames: `InstanceSchema` (defines an instance: a person, thing, act, or
event), `WhenTrue` (defines a quality/state via what holds when it is true of
someone/something), `RelationalSchema` (defines a relation between two
participants).

- `referents` is a list of `{{"index": n, "refKind": k}}`, indices DENSE from 1.
  Kinds: {", ".join(f"`{k}`" for k in INV["refKinds"])}.
- Referent 1 (and ALSO referent 2 for `RelationalSchema`) is FRAME-IMPLICIT:
  it denotes the definiendum (instance / bearer of the quality / the two
  relata). Implicit referents are already introduced — mention them directly
  as `{{"kind":"ref","index":1}}` and NEVER give them a `bind`.
- Every OTHER declared referent must be INTRODUCED exactly once, by putting
  `"bind": n` on the SP that first describes it. Introduce before (in clause
  order) any `{{"kind":"ref","index":n}}` mention. A declared-but-never-bound
  or bound-twice referent is a gate error.

### 3.2 Substantive phrases (SP) — the entity-denoting unit

```
{{"kind":"sp", "det"?: .., "quant"?: .., "mods"?: [..], "head": .., "restrictedBy"?: <clause>, "bind"?: n}}
```

- `det` ∈ {{{", ".join(f"`{d}`" for d in INV["dets"])}}}.
- `quant` ∈ {{{", ".join(f"`{q}`" for q in INV["quants"])}}}.
- `mods`: list of `{{"mod": m, "intensifier"?: i}}` with m ∈
  {{{", ".join(f"`{m}`" for m in INV["mods"])}}} and i ∈
  {{{", ".join(f"`{i}`" for i in INV["intens"])}}}; no duplicate entries.
- `head` is one of:
  - `{{"kind":"primeHead","prime": p}}` with p a substantive prime:
    {", ".join(f"`{h}`" for h in INV["substHeads"])}.
  - `{{"kind":"kindFrame","of": <SP|ref|concept>}}` — "a kind of X";
    `{{"kind":"partFrame","of": <SP|ref|concept>}}` — "a part of X".
  - `{{"kind":"refHead","index": n}}` — an SP re-describing referent n.
- `restrictedBy`: an embedded clause restricting the SP ("someone who ...").

### 3.3 Clauses

A clause is a predication or an operator application.

**Predication** `{{"type":"pred","pred": P, "roles": {{role: filler, ...}}}}` —
P and its licensed roles are CLOSED:

{frames_md}

{SLOT_KIND_MD}

**Operator** `{{"type":"op","op": O, "args": [...]}}` — arity is checked:

{ops_md}

### 3.4 The 65 primes (the ONLY vocabulary; exact spellings, `~` included)

{primes_md}

### 3.5 Caps and discipline

- ≤ {INV["caps"]["maxClauses"]} clauses total (embedded and quote clauses count), ≤ {INV["caps"]["maxReferents"]} referents,
  structural nesting depth ≤ {INV["caps"]["maxDepth"]}. Good explications here use 2–5
  top-level clauses; render the genus and the CRITERIAL differentia, nothing
  else.
- ONLY the predicates in the §3.3 table may appear as `"pred"`. In
  particular: `TOUCH`, `INSIDE`, `ABOVE`, `BELOW`, `NEAR`, `FAR`, `SIDE` are
  space primes, NOT predicates — use them as `manner` fillers ("X touches Y"
  = `BE-SOMEWHERE` undergoer X, locus Y, manner `TOUCH`); `NOW`/durations are
  time/duration fillers; `GOOD`/`BAD`/`BIG`/`SMALL` are mods or FEEL
  attributes.
- Operators are NEVER predicates. `NOT`, `CAN`, `MAYBE`, `IF`, `BECAUSE`,
  `WHEN`, `LIKE`, `AFTER`, `BEFORE` must ALWAYS be written
  `{{"type":"op","op":...,"args":[...]}}` — including when nested inside
  another operator's `args` or inside a `{{"kind":"clause"}}` filler. A
  `{{"type":"pred","pred":"NOT",...}}` node is a gate error.
- Referent walk order: the validator walks clauses in list order and, inside
  a clause, roles/args in a fixed order. Put `"bind": n` on the FIRST
  occurrence of referent n in that walk, and only ever mention
  `{{"kind":"ref","index":n}}` in LATER positions/clauses. When in doubt, make
  the introducing SP appear in an EARLIER clause than every mention.
- Quote scope: a referent first bound INSIDE a `quote` is visible only inside
  that quote — it cannot be mentioned outside it or in a later quote. Any
  referent shared across quotes (or used after one) must be bound in a plain
  clause BEFORE the quote; referents bound outside ARE visible inside quotes.
- Other frequent gate errors: a role not in the predicate's table; a missing
  REQUIRED role; `FEEL` with an attribute other than GOOD/BAD;
  `WANT`/`DON'T-WANT` without `complement`; wrong operator arity or a
  non-clause arg where a clause is required (`AFTER`/`BEFORE` take
  anchor-then-clause); a `bind` on a frame-implicit referent; non-dense
  referent indices.
- When the differentia needs vocabulary the primes cannot carry (money, law,
  art, romance, instruments, materials ...), render the most faithful
  primes-only skeleton you can defend — and declare `lossy` in `notes` with
  the dropped content named. Honesty over cleverness: never bend the grammar,
  never invent primes.

## 4. Worked examples (input → output)

{examples_md}

## 5. Final reminder

Reply with the single JSON object only. Do not wrap it in ``` fences. Do not
explain. If you are uncertain between two readings of the synset, the
`wn31-gloss` line is authoritative for WHICH sense; your scholarship is
authoritative for WHAT that sense's true intension is.
"""

OUT.write_text(PROMPT)
sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f"wrote {OUT} ({len(PROMPT)} chars, {len(examples)} few-shot examples)")
print(f"sha256 {sha}")
