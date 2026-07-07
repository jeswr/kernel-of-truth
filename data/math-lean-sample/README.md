# math-lean-sample — 70 Mathlib formal-reference records (feasibility sample)

Deliverable of bead `kernel-of-truth-vn8`. Companion design record:
**`docs/design-lean-route.md`** (route survey + decision — read that first).
Sector context: `docs/design-math-sector.md` §1.2/§2.4 (why Lean/Mathlib was
rejected as an *identity* substrate); `docs/design-bulk-kernel.md` (bulk-tier
honesty architecture and provenance rules).

## What these records ARE — and are not

Each record is a **formal reference record** (`"record": "lean-ref/1"`,
`"status": "formal-reference"`): an annotation-layer pointer to a declaration
in Mathlib, identity-anchored on **(source.mathlibCommit, name)**. That pair is
the only stable thing here.

**No field of these records is concept-hash-boundary content.** In particular
`signaturePretty` is the doc-gen4 pretty-printed signature: it depends on
notation, dot-notation heuristics, implicit-binder display, auto-generated
universe names (`Sort u_1`), and pretty-printer settings — the same kernel
declaration admits many such strings, and the string changes across Mathlib /
Lean / doc-gen4 versions with no change in meaning. Hashing it would mint
identity out of rendering. These records are therefore *not* profile-M records
and are not even AxiomsOnly records: they mint no `urn:concept:` ids at all.
They exist to be **bridge targets** (`sameConceptAs`-style annotations from
profile-M hashes to Mathlib names) and mapper/annotation material.

## Files

| File | Role |
|---|---|
| `extract.mjs` | deterministic extractor (zero-dep Node): `source-snapshot/*.html` → `records.jsonl` + `manifest.json`, byte-identical on re-run |
| `source-snapshot/*.html` | the exact doc-gen4 bytes the records derive from (the docs site is un-versioned, so these snapshots are the only archival source copy) |
| `fetch-log.json` | one-off fetch provenance (URLs, sha256, timestamps) — the only place timestamps live |
| `records.jsonl` | 70 records: `Mathlib.Data.Nat.Basic` (18) + `Mathlib.Data.Nat.GCD.Basic` (52), mathlib@`5c206a85` |
| `manifest.json` | generated: counts, snapshot hashes, commit, identity note |

Regenerate: `node extract.mjs` (no network, no deps). Verification performed:
two consecutive runs byte-identical; all 70 records manually reviewed against
the rendered docs pages — **0 parse errors** (one automated flag was the
literal `<` in `0 < n`, a false positive).

## Record fields

`name`, `kind` (theorem/instance/def/…), `module`, `attributes` (e.g.
`@[simp]`), `signaturePretty` (annotation only, see above), `docstring` (often
empty: 63/70 here), `referencesPretty` (declarations hyperlinked from the
signature — *type-level* dependency edges; proof/value dependencies are NOT
visible at this layer), `hasEquations` / `equationsUnrendered` (definition
values are not extractable from doc-gen4 output; sometimes even the equation
lemmas are elided "due to their size"), `source` (mathlib commit + file + line
span from the gh_link).

## Extraction issues found (the honest list)

1. **Pretty-printed types are not canonical.** `a ∣ c.lcm b` hides head
   constants behind notation (`∣` = `Dvd.dvd`) and dot-notation (`c.lcm b` =
   `Nat.lcm c b`); the hyperlink structure recovers the referenced constants,
   the string does not.
2. **Elaborator-generated names leak into signatures.** Auto-bound universe
   variables render as `Sort u_1` (`Nat.leRecOn_injective`); instance names
   are machine-generated (`Nat.instLinearOrder`) and churn across refactors.
3. **Aliases duplicate meaning under different names.** `Nat.Dvd.dvd.nat_lcm_right`
   is "Alias of `Nat.dvd_lcm_of_dvd_left`" (note the left/right naming cross);
   `Nat.Coprime.symmetric` (kind *theorem*) aliases `Nat.Coprime.stdSymm`
   (kind *instance*) — even the kind is not stable across an alias.
4. **Values/proofs absent.** doc-gen4 emits signatures + docstrings only;
   `Nat.instLinearOrder`'s equations are literally "not rendered due to their
   size". Anything value-level needs a toolchain route (see design doc).
5. **Un-versioned source URL.** The docs site mutates in place daily; without
   the committed snapshots the extraction would not be re-derivable. The
   mathlib commit inside gh_links is the content pin.
6. **HTML flattening subtleties.** Inline tags must vanish (`Nat.succ` spans),
   block tags must become whitespace, entities must decode (`&lt;` in `0 < n`)
   — all handled in `extract.mjs`, but this fragility is a real cost of the
   doc-gen4 route vs a JSON-native dump.
