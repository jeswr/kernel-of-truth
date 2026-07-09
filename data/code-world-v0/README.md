# code-world-v0 — extracted code world layer (stratum 4, A5)

`world.jsonl`: kot-world/1 records EXTRACTED deterministically from
`data/code-corpus-v0/src/` by `kot-code-extract/1`
(`tools/axiom/gen_a5_corpora.py`, RNG-free; regenerating is byte-identical),
plus 10 PLANTED records (provenance `planted-violation/1 ...`) realising the
3 pre-declared instrument-validity violations (1 disjoint, 1 cardinality-max,
1 range). Concept references are EXACT minted URNs (X3 trap): code-v0
constructs/relations + kernel-v0 part-of for transitive lexical containment.
Spec: docs/design-a5-code-worldlayer-oracle.md §§1-2. Counts: manifest.json.
