# Archived onto-obo mint — substitute mode, 5 ontologies, 42,565 URNs (superseded)

**Provenance only. Not the live minted set.**

These are the exact bytes of the former `data/onto-obo/minted-urns.jsonl` +
`manifest.json` as committed before CL + UBERON were added:

- `minted-urns.jsonl` — 42,565 URNs, **`referenceMode: substitute`**,
  `corpusIdentityRoot 0c892f94…`, `mintToolHash 4b65ee17…`.
- `manifest.json` — the 5-ontology (BFO/RO/GO/PATO/PO) extractor + minting
  manifest.

## Why superseded

Adding the anatomy ontologies **CL** and **UBERON** (extraction 3, 2026-07-09)
made the onto-obo axiom reference graph **not a DAG** (662 SCCs, largest 1,142
UBERON/CL terms, from symmetric `disjoint_from` + lateral `relationship`/
`part_of`/`develops_from` assertions). Substitute-mode content-addressing cannot
represent that soundly — it exceeds the gist-s6 component cap (32) and would
otherwise mint a 1,142-term monster component that spuriously entangles those
identities. onto-obo was therefore switched to **stable mode** (the same
resolution as `lexical-wn31`'s non-DAG axiom graph): refs kept as stable
placeholder `urn:onto-obo:` ids, identity anchored on the globally-unique
`sourceId`.

This re-schemes **every** onto-obo URN (a generation bump, gist §8): 42,497 of
the 42,565 prior URNs changed value, 53 ref-free records kept the same URN, 15
were removed (RO foreign stubs), and 18,499 CL/UBERON records were added. The
live set now lives at `data/onto-obo/minted-urns.jsonl` (61,049 URNs, stable
mode, `corpusIdentityRoot 42bc0781…`).

Downstream consumer to re-point on adoption: `tools/pack/build-pack.mjs` (the
snapshot pack). Bead `kernel-of-truth-4im`.
