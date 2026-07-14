# S5 addendum — referenceable-lexicon (molecule-augmented) generation

> DESIGN ARTEFACT (poc/scale/molecule-aug/DESIGN.md §4). At generation time this
> addendum is appended to the UNMODIFIED base `concept-def-prompt.md`, followed by
> the mechanically generated `LEXICON LISTING` block (ids + one-line glosses,
> built from the lexicon record files by the S5 driver — never hand-edited).
> The base prompt file itself is not touched. Everything below overrides the
> base prompt ONLY where it says so explicitly.

## 6. Reference-augmented explication (S5 override)

Two rules of the base prompt are amended. Everything else — the scholarly
gloss standard (§1), the record shape (§2), the kot-ast/1 grammar (§3.1–§3.3),
the caps and discipline (§3.5) — stands unchanged.

### 6.1 The vocabulary is now the 65 primes PLUS the referenceable lexicon

Base §3.4 says the 65 primes are the only vocabulary. For THIS task you may
additionally reference any concept in the LEXICON LISTING appended below —
and ONLY those. Each listed entry is an already-defined concept with its own
prime-grounded explication; referencing it imports that meaning whole.

Reference syntax inside the explication (both already legal kot-ast/1):

- as an entity filler in any role that takes an entity:
  `{"kind": "concept", "id": "urn:kernel-v0:teacher"}`
- as the target of a kind/part head ("a kind of X" / "a part of X"):
  `{"kind": "sp", "head": {"kind": "kindFrame", "of": {"kind": "concept", "id": "urn:kernel-v0:event"}}}`
- as a manner filler or a BE-SPEC attribute, where the base grammar already
  admits a concept ref.

### 6.2 The `references` field is now live

Base §2 says `references` is always `[]`. For THIS task, `references` MUST
list exactly the distinct lexicon ids your explication mentions, sorted,
e.g. `"references": ["urn:kernel-v0:learn", "urn:kernel-v0:teacher"]` —
and `[]` only when you used no reference. A mismatch between the field and
the AST is a hard gate error, as is any id not in the LEXICON LISTING.

### 6.3 Discipline — references are a scalpel, not a thesaurus

1. **Decompose first.** Use a reference ONLY where the base-prompt primes-only
   rendering would drop CRITERIAL differentia. If the primes carry the
   meaning in a few clauses, write the primes; a reference you could have
   decomposed is a fault, not a convenience.
2. **Reference the criterial unit, not the topic.** For *tuition fee*, the
   criterial imports are money-like payment and teaching — not "school" at
   large. Pick the smallest lexicon concepts that carry the dropped meaning.
3. **≤ 8 distinct references** per record (hard gate). Good records here are
   expected to use 0–3.
4. **No self-reference, no chains you invent.** You may only cite listed ids;
   you may not coin new urns, and you may not reference the concept being
   defined (directly or by synonym).
5. **The honesty flag keeps its meaning, at the NEW bar.** `notes` must still
   begin `"AST adequacy: faithful — "` or `"AST adequacy: lossy — "`, judged
   against what the primes PLUS your references can carry. Declare `lossy`
   only for content neither the primes nor any listed concept can render
   (and name it exactly, as before). Do not declare lossy merely because a
   perfect lexicon entry is missing if a faithful composition exists.
6. **References import meaning, not spelling.** Never reference a lexicon
   concept just because its label appears in the gloss; reference it because
   its MEANING is a criterial component of this sense.

### 6.4 Worked delta-example (input → the reference-bearing part)

For `concept: mentor` ("a wise and trusted guide"), a primes-only rendering
loses the teaching differentia; with the lexicon the criterial clause becomes:

```
{"type": "pred", "pred": "BE-SPEC", "roles": {
  "undergoer": {"kind": "ref", "index": 1},
  "attribute": {"kind": "sp", "head": {"kind": "kindFrame",
    "of": {"kind": "concept", "id": "urn:kernel-v0:teacher"}}}}}
```

with `"references": ["urn:kernel-v0:teacher"]`, plus further primes-only
clauses for the trusted-guide differentia (`urn:kernel-v0:trustworthy` is
also listed and may serve). The record remains ONE strict-JSON object,
nothing else, exactly as the base prompt demands.

<!-- LEXICON LISTING is appended below this line by the S5 driver -->
