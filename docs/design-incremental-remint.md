# Incremental re-mint: URN-stability guarantee vs re-mint cone (bead kernel-of-truth-lik)

**Status:** decided + implemented 2026-07-09 (Fable, kernel-data). Motivating
case: `data/haiku-tier` (minted 2026-07-07 as an 84-record mid-stream snapshot
while the volume runner was writing `records/`; corpus has since settled at
2,673 authored records).

## The invariant the mint already gives us

The mint (`tools/mint`) is a **deterministic pure function of the corpus**
(`docs/design-hash-input.md`): a record's `urn:kot:` URN is
`H(profileHeader ‖ JCS(NFC(identityPayload')))`, where `identityPayload'` is the
identity payload with intra-corpus references handled per the corpus reference
mode:

- **stable mode** (haiku-tier, molecules-v0, lexical-wn31, onto-sumo): no
  substitution. A URN depends **only on that record's own identity-payload
  bytes**. Adding/removing/editing record *X* affects **only** *X*'s URN. The
  re-mint cone of a change is exactly `{X}`. There is no dependency graph and no
  topological order to compute.

- **substitute mode** (kernel-v0, math-v0, code-v0, math-mm, physics-\*,
  onto-obo, onto-framenet): intra-corpus refs are substituted by the referent's
  already-minted URN in reverse-topological order. Editing *X* changes *X*'s
  URN, which changes the URN of every record that (transitively) references *X* —
  *X*'s **ancestor cone** in the reference DAG (cyclic SCCs move as a unit). A
  full deterministic re-mint resolves the whole cone in one pass.

Because the mint is a pure function, a **full re-mint always produces the
canonical answer**. "Incremental" therefore does **not** mean skipping
deterministic work (which would only trade a few milliseconds of CPU for a
divergence risk). It means: **compute the delta against the committed set and
gate on it**, so that (a) the stability guarantee is proven per re-mint, and (b)
re-ingestions that would move existing identities are surfaced, never silent.

## Decision

1. **The authoritative minted set of a corpus is the full mint of its current
   records.** A partial/mid-stream mint is a snapshot, never authoritative once
   superseded. (haiku-tier: the 84-URN 2026-07-07 file is archived under
   `data/haiku-tier/snapshots/mint-20260707-84urn/`; the authoritative set is now
   the 2,673-URN full mint, `corpusIdentityRoot b219cbf4…`.)

2. **URN-stability guarantee.** Re-minting a corpus MUST NOT change the URN of an
   unchanged record. This is automatic in stable mode and holds in substitute
   mode for any record outside a changed record's cone. It is *verified* per
   re-mint by the delta's `changed` set being empty for records whose identity
   payload did not change.

3. **Re-mint cone = the delta's `changed` set.** The set of committed URNs whose
   value moves under a re-mint is exactly the affected cone. The tool names it;
   in substitute mode it is `{directly-edited records} ∪ {their dependents}`.

4. **Generation semantics (gist §8).** `changed.length === 0` ⇒
   *same-generation growth* (only `added`/`removed`); adopt in place, no
   generation bump. `changed.length > 0` ⇒ a *re-ingestion* changed existing
   identities ⇒ a new generation/snapshot pack is required; the writer refuses
   unless `--allow-changes` is explicitly passed (fail closed).

## Tooling

`tools/mint/src/incremental.ts` (compiled to `dist/src/incremental.js`), a
standalone driver that **reuses the pinned mint** (`mintCorpus` / `main` from
`cli.ts`) and is deliberately **not** part of the `mintToolHash` file set, so it
never perturbs mint identity:

```
node dist/src/incremental.js --data <repo>/data --corpus <name> [--write] [--allow-changes]
```

- Dry-runs the full mint into a throwaway temp dir (never touches committed
  files), diffs the fresh `sourceId → urn` map against the committed
  `minted-urns.jsonl`, and prints `{added, removed, changedCone, stable,
  duplicateGroups, cyclicComponents, generation}`.
- Exits non-zero (`ERR_IDENTITY_CHANGED`) if any committed URN would change and
  `--allow-changes` was not given.
- `--write` archives the current `minted-urns.jsonl` (+ `mint-manifest.json`)
  under `<corpus>/snapshots/mint-archive-<ts>/`, then delegates the real write
  (minted-urns + manifest refresh) to the pinned mint CLI, so the adopted bytes
  and manifest block are identical to a full mint.

### haiku-tier migration (executed)

- Old 84-URN authoritative files preserved byte-for-byte at
  `data/haiku-tier/snapshots/mint-20260707-84urn/`.
- Full 2,673-URN mint (byte-reproduced by the current pinned tool,
  `mintToolHash 4b65ee17…`) promoted to `data/haiku-tier/minted-urns.jsonl` +
  `mint-manifest.json`.
- Verified: all 84 prior URNs reproduced identically (0 changed), 2,589 added,
  0 duplicate-identity groups ⇒ **same-generation growth**. Post-migration
  `incremental --corpus haiku-tier` reports `added:0 removed:0 changedCone:0
  stable:2673`.
