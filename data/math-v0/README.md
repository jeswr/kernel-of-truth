# math-v0 — the foundational-mathematics concept corpus (profile-M v0)

39 concept records in the `pm-ast/1` JSON AST — the typed mirror of the
profile-M v0 grammar specified in `docs/design-math-sector.md` §2–§3
(many-sorted FOL over a Peano core with Set/Pair sort formers, canonical
de Bruijn binding). Profile-M is minted permissionlessly per
concept-hash-design.md §8: it is a **new content-addressed profile bundle**,
not an amendment to profile-1, and this corpus is its first exercise.

## What this is — and is not

**Research-grade, agent-authored against profile-M v0; NOT federation-endorsed;
formulation choices unreviewed.** Unlike kernel-v0, the *correctness* of each
record has a mathematical fact of the matter (the sort/scope/caps obligations
are machine-checked, and whether e.g. `less-or-equal := ∃k. x+k=y` is right is
provable relative to the pinned basis) — but the *choice* among provably
equivalent formulations is still a judgement nobody has endorsed, and the two
NSM-bridge explications are KNOWN-WEAK research attempts (design §6).

Concept ids (`urn:math-v0:<slug>`) are **placeholder URNs**, not
content-address hashes — minting real `urn:concept:` identities is the
concept-hash pipeline's job (the gist §6 machinery applies unchanged; design
§3.5). **No vectors exist for these records**: the construction B-M encoder
variant is specified in design §4 and deliberately not built (filed follow-up);
running the profile-1 encoder over pm-ast records would be a category error.

## Contents

- `concepts/*.json` — one record per file: `{id, label, status, gloss, notes?,
  references, nsmBridge, characterizes?, definition}`. `definition` is the
  pm-ast/1 tree (hash-boundary content); `label`/`gloss`/`notes`/`nsmBridge`
  are annotation-layer content.
- `manifest.json` — counts by frame/status, reference structure, NSM-bridge
  tally. No encoder content-hash is pinned (no encoder exists).
- `validate.mjs` — self-contained checker (zero deps): closed-inventory
  grammar, full sort checker, de Bruijn scope + vacuous-binder gates, caps,
  reference recomputation/DAG, manifest cross-checks; NSM-bridge prime names
  and explication legality are checked against `encoder/dist` when built
  (warn-and-skip otherwise).

## Shape

- **Frames:** 9 Primitive, 6 AxiomDef, 10 TermDef, 11 PredicateDef,
  3 RecursiveFunctionDef.
- **Coverage:** Peano core (zero/successor/naturals, axioms incl. induction
  via `Set(N)`), numerals one–three, predecessor/addition/multiplication
  (primitive recursion, guarded by construction), order (≤, <), divisibility
  (divides/even/odd/prime-number), sets over N (empty/singleton/subset/
  union/intersection), functions-as-graphs (total-functional, injective), and
  an integers-as-equivalence-classes sketch (`status: sketch`; quotient
  construction without quotient sorts — design limitation L3).
- **Reference structure:** 11 records reference others; deepest chain
  `odd → even → divides → multiplication → addition` (depth 4). DAG enforced.
- **NSM bridges:** `one`→ONE, `two`→TWO (prime bridges); `equality`→THE-SAME
  (flagged approximate); `addition` and `empty-set-nat` carry KNOWN-WEAK
  profile-1-legal explication attempts (legality machine-checked, adequacy
  not); the remaining 34 records record `nsmBridge: {"kind": "none"}` with a
  stated reason each. The high `none` rate is a finding, not a gap to hide:
  foundational mathematics is where the mandate predicted NSM would not reach.

## Validation

```sh
node data/math-v0/validate.mjs        # self-contained; exit 0 iff all pass
# optional, enables NSM-bridge deep checks:
(cd encoder && npm install && npm run build)
```
