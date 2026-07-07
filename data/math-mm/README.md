# math-mm — bulk-extracted Metamath set.mm corpus (profile-M formal sector)

**2,998 records** extracted mechanically from the pinned set.mm: every `$a`
statement of the database — 1,440 syntax formers, 1,432 definitions (`df-*`),
126 axioms (`ax-*`); zero `|-` `$a` statements fell outside that rule. This is
the *bulk kernel* math stream decided in `docs/design-bulk-kernel.md`:
formal-sector extraction where **the source is already definitional**, so the
records carry full definitional force (not AxiomsOnly's reduced claim) — a
Metamath definition IS its meaning. `docs/design-math-sector.md` §1.1 chose
Metamath grounding for exactly this pipeline.

**Not endorsed; provenance-pinned; deterministically re-derivable.** `$p`
theorems are out of scope by design (no proof layer — design-math-sector.md
L1). No subset truncation: this is the complete `$a` inventory including the
1,147 mathbox records (flagged `provenance.mathbox: true`).

## Source pin

- `https://github.com/metamath/set.mm`, file `set.mm`,
  commit `7010d9c53cbae4d47cf84ec552a29f06bad1606b` (2026-07-05),
  sha256 `c1a0052dbf8b601d6ff2d99cc5ac658d90153b179417a2e7a60c853bb04ed30a`,
  50,872,478 bytes. The source file itself is NOT vendored (50 MB); re-fetch
  by commit to reproduce.

## Files

- `syntax.jsonl` / `definitions.jsonl` / `axioms.jsonl` — one record per line,
  database order. `definition` (schema `pm-mm/1`, `form: "mm-canonical"`)
  holds the canonical token string (`typecode` + `symbols`), the mandatory
  variables with their **wff/class/setvar sorts**, mandatory `$d` pairs,
  `$e` hypotheses, and for definitions the definiendum/definiens split plus
  the owning syntax former. Where set.mm's statement is wider than profile-M
  v0's Peano grammar — always, in practice — the canonical token string IS the
  definitional payload, per the design doc's formal-sector clause; nothing is
  force-fit into the v0 grammar.
- `manifest.json` — counts, source pin, extractor content-hash, DAG stats,
  and the honesty ledger (irregular shapes, fallback assignments, SCCs,
  forward-edge list).
- `alignment-v0.json` — 27 hand-checked bridge candidates math-v0 ↔ set.mm
  (annotation layer; encoding-residue caveats per link).
- `validate.mjs` — self-contained re-checker (no source needed): shape, URN
  resolution, dependency/reference consistency, inverse df↔former links,
  SCC/depth/count recomputation vs manifest. Run: `node data/math-mm/validate.mjs`.
- `extractor/` — `parse-mm.mjs` (minimal spec-correct .mm parser; proofs
  skipped, includes rejected), `extract.mjs` (pipeline), `test-parser.mjs`
  (unit tests), `sample-review.mjs` (verification tooling).

Reproduce (byte-identical):

```bash
node data/math-mm/extractor/extract.mjs --src /path/to/set.mm \
  --commit 7010d9c53cbae4d47cf84ec552a29f06bad1606b --date 2026-07-07 \
  --out data/math-mm
```

## Dependency semantics (stated rule — read before consuming the DAG)

`introducedBy(c)` = first syntax former (database order) whose statement
contains constant `c`. A record's **syntax** deps are the introducing formers
of every constant it uses, plus (for definitions) the definiendum's own
former, found by exact pattern match (fallback for the 2 irregulars: df-bi,
df-clab). **Definitional** deps map each definiens constant to the `df-*`
defining its former. Three documented consequences — precision limits of
token-level scanning, not extraction errors:

1. **Punctuation attribution**: `(`,`)` attribute to `wi`, `,` to `wif`, `{`
   `}` to `cab` — their first users. So e.g. many records carry a `df-ifp`
   definitional dep via the comma token.
2. **Pattern-reuse invisibility**: formers that introduce no new constant
   (`csn`'s `{ A }`, `cpr`, `w3o`, `cv`, …) cannot be seen *inside* a
   definiens without a full grammar parse — e.g. `df-tp` uses `{ C }` but has
   no `df-sn` dep. Their own definitions still link them (df-sn → csn).
3. **`cv` is unreachable** from any record (its pattern is a bare variable);
   listed in the manifest with this note.

## DAG findings (the honest ledger)

- **Acyclicity: holds except one documented 2-cycle** — set.mm's class-theory
  bootstrap `{df-cleq, df-clel}` (`=` defined via `e.`, `e.` defined via `=`).
  set.mm itself documents df-clab/df-cleq/df-clel (and df-bi) as *not
  definitions in the strict sense* and exempts them from its definitional
  soundness check. The cycle is the source's real structure; reported, not
  patched. Depths are computed on the SCC condensation.
- 33,688 edges over 2,998 nodes; max depth 53 (witness chain runs through the
  NM mathbox Hilbert-lattice tower: df-hlhil → df-hgmap → … ). 18 edges point
  to *later* database positions (17 via the early-declared/late-defined
  wceq/wcel/wf clusters, 1 mathbox case walsc → df-alsi); listed in the
  manifest.
- 8 primitive syntax formers (no defining df-*): `wn wi wal cv` (logic core)
  + `cva csm csp cprvb` (axiomatic Hilbert-space / mathbox primitives).

## Verification (design-bulk-kernel.md bar, all run 2026-07-07)

1. **Parser unit tests**: 10/10 pass (`node --test extractor/test-parser.mjs`)
   — tokenizer, comments, scoping, `$d` mandatory-pair logic, compressed-proof
   skipping, fail-closed errors.
2. **Deterministic re-extraction**: two runs, `diff -r` byte-identical.
3. **Independent global cross-check**: every record's typecode+token string
   re-extracted from the raw bytes by a parser-independent text scan —
   **0/2,998 mismatches** (after making the *checker* comment-aware: its two
   initial hits were commented-out older statement versions near df-cvlat and
   df-lcdual; the parser was right).
4. **Manual sample review**: 100 records, seeded sample
   (`sample-review.mjs --seed 20260707`), reviewed against the source by the
   extracting agent — **0 errors**. The two rule-level precision limits above
   were observed and documented during this review.
5. **Structural validator**: `validate.mjs` exit 0.

## What this corpus is not

Records are *statements with dependency structure*, not verified theorems
(proofs were skipped, deliberately — over a dozen independent verifiers check
set.mm upstream). Identity here is still by set.mm label + pinned commit, not
content-hash: minting real `urn:concept:` ids for these records is the
concept-hash pipeline's job (an RDF record form for `pm-mm/1` does not exist
yet; filed as follow-up). NSM bridges: none, for every record (bulk mechanical
tier); the hand-checked math-v0 links live in `alignment-v0.json`.
