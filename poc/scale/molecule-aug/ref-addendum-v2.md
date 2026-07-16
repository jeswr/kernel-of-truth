# S5 addendum v2 — MANDATORY closure-safe reference uptake (REPILOT-v2.1)

> DESIGN ARTEFACT (REPILOT-v2.1; repairs the ASM-2379 uptake failure — the v1
> addendum yielded 68.1% zero-ref molecule records and 11 non-closure-safe
> reference picks in the n=24 pilot). At generation time this addendum is
> appended to the UNMODIFIED base `concept-def-prompt.md`, followed by the
> mechanically generated REFERENCEABLE LEXICON LISTING block — which now
> contains ONLY the 20 validated (closure-safe) concepts, built from the
> adjudicated lexicon by the S5 driver, never hand-edited. The base prompt
> file itself is not touched. Everything below overrides the base prompt ONLY
> where it says so explicitly.

## 6. Reference-augmented explication (S5 v2.1 override)

Two rules of the base prompt are amended and one NEW hard requirement is
added. Everything else — the scholarly gloss standard (§1), the record shape
(§2), the kot-ast/1 grammar (§3.1–§3.3), the caps and discipline (§3.5) —
stands unchanged.

### 6.1 The vocabulary is the 65 primes PLUS the 20 listed concepts — no others

Base §3.4 says the 65 primes are the only vocabulary. For THIS task you may
additionally reference any concept in the REFERENCEABLE LEXICON LISTING
appended below — and ONLY those 20. Each listed entry is a validated,
already-defined concept with its own prime-grounded explication; referencing
it imports that meaning whole. Other lexicon concepts exist but are NOT
validated: a reference to ANY id not in the listing is mechanically rejected
(`ERR_REF_NOT_CLOSURE_SAFE`) and your record is discarded. Do not invent
urns; do not reference from memory.

Reference syntax inside the explication (both already legal kot-ast/1):

- as an entity filler in any role that takes an entity:
  `{"kind": "concept", "id": "urn:molaug-v0:woman"}`
- as the target of a kind/part head ("a kind of X" / "a part of X"):
  `{"kind": "sp", "head": {"kind": "kindFrame", "of": {"kind": "concept", "id": "urn:kernel-v0:event"}}}`
- as a manner filler or a BE-SPEC attribute, where the base grammar already
  admits a concept ref.

### 6.2 The `references` field is live and MUST NOT be empty

Base §2 says `references` is always `[]`. For THIS task, `references` MUST
list exactly the distinct listed ids your explication mentions, sorted — and
it MUST contain at least one. **A record with `"references": []` is
mechanically REJECTED (`ERR_ZERO_REFS`) exactly like a malformed record, and
the task is re-issued.** A mismatch between the field and the AST is a hard
gate error (`ERR_REF_MISMATCH`), as is any id not in the listing.

Why this is not optional: every concept in this campaign is one whose
primes-only renderings measurably dropped criterial content, and the listing
was built to carry exactly the kinds of content that were dropped. Your job
is to find which listed concept(s) carry criterial components of THIS sense
and compose them in. Writing a primes-only record is refusing the task.

### 6.3 Discipline — references are a scalpel, and at least one cut is required

1. **Decompose everything the primes can carry; import the rest.** Render in
   primes whatever primes can faithfully render; use references for the
   criterial differentia primes would drop. Expect 1–3 references; pick the
   SMALLEST set of listed concepts that carries the dropped meaning.
2. **Reference the criterial unit, not the topic.** For *widow*, the
   criterial imports are woman and death — not "law" because marriage is
   legal. Pick the smallest lexicon concepts that carry the dropped meaning.
3. **Do not pad.** The mandatory-reference rule is NOT license for topical
   decoration: a reference whose meaning is not criterial to this sense is
   asserted wrong/idle meaning, and the fidelity judge reads the fully
   expanded rendering — a padded reference shows up there verbatim and makes
   the record LOSSY. If several listed concepts are plausible, choose the one
   whose imported meaning is actually entailed by this sense.
4. **≤ 8 distinct references** per record (hard gate); good records use 1–3.
5. **No self-reference, no invented chains.** You may only cite listed ids;
   you may not coin new urns, and you may not reference the concept being
   defined (directly or by synonym).
6. **The honesty flag keeps its meaning, at the NEW bar.** `notes` must still
   begin `"AST adequacy: faithful — "` or `"AST adequacy: lossy — "`, judged
   against what the primes PLUS your references can carry. Declare `lossy`
   only for content neither the primes nor any listed concept can render
   (and name it exactly, as before). Do not declare lossy merely because a
   perfect lexicon entry is missing if a faithful composition exists.
7. **References import meaning, not spelling.** Never reference a listed
   concept just because its label appears in the gloss; reference it because
   its MEANING is a criterial component of this sense.

### 6.4 Worked delta-example (input → the reference-bearing part)

For `concept: widow` ("a woman whose spouse has died"), a primes-only
rendering loses the woman and death differentia; with the listing the
criterial clauses become:

```
{"type": "pred", "pred": "BE-SPEC", "roles": {
  "undergoer": {"kind": "ref", "index": 1},
  "attribute": {"kind": "sp", "head": {"kind": "kindFrame",
    "of": {"kind": "concept", "id": "urn:molaug-v0:woman"}}}}}
```

plus a clause locating a prior `{"kind": "concept", "id":
"urn:kernel-v0:death"}` event of the spouse, with
`"references": ["urn:kernel-v0:death", "urn:molaug-v0:woman"]`. The record
remains ONE strict-JSON object, nothing else, exactly as the base prompt
demands.

<!-- REFERENCEABLE LEXICON LISTING (closure-safe, 20 ids) is appended below this line by the S5 driver -->
