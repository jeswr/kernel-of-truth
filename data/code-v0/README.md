# code-v0 — code-construct concept corpus (stratum 1-2 extension, A5)

Six hand-authored code-construct concepts minted to `urn:kot:` content-hash
identities by the canonical mint tool (`tools/mint`), for the A5 code
world-layer experiment (registry id `a5`; idea `idea-code-worldlayer-cpg`).

| sourceId | kind | role in the A5 world layer |
|---|---|---|
| `python-module` | class | entity class: one source file |
| `python-function` | class | entity class: named callable (incl. methods, nested) |
| `python-class` | class | entity class: named type |
| `code-calls` | relation | caller -> callee (conservative static resolution) |
| `code-defines` | relation | defining scope -> directly defined construct |
| `code-imports` | relation | importing module -> corpus-internal imported module |

Lexical containment deliberately mints NOTHING new: the A5 world layer reuses
the already-minted kernel-v0 `part-of` / `has-part` pair (exact URNs) for the
transitive containment relation — the kernel's marginal value in the code
domain is canonical concept IDENTITY shared across domains.

## Profile decision (honesty note)

Identity payload = the `kot-code-construct/1` **`definition` object**
(construct kind + language + precise structural definition text + intra-corpus
refs), content-addressed exactly like every other corpus; `label` / `gloss` /
`notes` / `status` are annotation. These are **structural definitions, NOT
kot-ast/1 NSM explications** — the same corpus-specific-profile route as
math-v0 (`pm-ast/1`). The NSM-grounded explication of code constructs is the
deferred idea-A sub-programme (`idea-structured-data-parser`, general-code
slice); nothing here pre-empts it. Intra-corpus refs (e.g. `code-calls` ->
`python-function`) are substituted to minted URNs in reverse topological order
(Unison-style), so relation identities are compositional over construct
identities.

X3 trap (restated): every consumer of this corpus identifies concepts by
EXACT minted URN (content-hash), never by kernel-space nearest-neighbour or
any similarity step.

Mint run: 2026-07-09 (the manifest `minting.mintDate` string is the mint
tool's fixed constant, not the run date).
