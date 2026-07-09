# Archived haiku-tier mint snapshot — 84 URNs (2026-07-07)

**Superseded. Preserved for provenance; do not use as the live minted set.**

These two files are the *exact bytes* of the former authoritative
`data/haiku-tier/minted-urns.jsonl` + `mint-manifest.json` as committed on
2026-07-07:

- `minted-urns.jsonl` — 84 URNs.
- `mint-manifest.json` — `mintedCount: 84`, `corpusIdentityRoot: cacb2a49…`.

## Why it was superseded

The haiku-tier mint is a **stable-mode, per-record pure function** of the
corpus (each record's `urn:kot:` URN depends only on its own identity payload;
there is no intra-corpus substitution — see `tools/mint/src/corpora.ts`
`haiku-tier` and `docs/design-hash-input.md`). The 84-URN file was a mint taken
mid-stream on 2026-07-07 while the volume runner was still writing
`records/`; only 84 record files were visible to that pass. The corpus has
since settled at **2,673 authored records**.

Re-minting the full 2,673-record corpus with the same pinned tool
(`mintToolHash 4b65ee17…`) reproduces:

- all **84** of these URNs **byte-identically** (0 changed, verified), plus
- **2,589** additional URNs for the records that were being written when this
  snapshot was taken.

Because no existing URN changed, promoting the 2,673-URN set is **same-generation
pure growth**, not a re-ingestion — no generation bump (gist §8). The
authoritative set now lives at `data/haiku-tier/minted-urns.jsonl` (2,673 URNs,
`corpusIdentityRoot b219cbf4…`). See `docs/design-incremental-remint.md` and
bead `kernel-of-truth-lik`.
