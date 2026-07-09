# axioms-definitional-v0 — stratum-3 definitional-endorsement corpus (kot-axiom/1)

The home for the define-op's corpus-scoped `definitional` endorsements
(grammar: docs/design-constraint-layer.md §3.3; spec: the FROZEN memo
docs/design-kot-query-define-op.md; engine: tools/axiom/kot_axiom.py).

One `kot-axiom/1` record per endorsed onto-obo shard. Each admits that shard's
`logicalDefinition`s as a definitional-source, pinning the shard's exact bytes
via `source.sourceVersion` (sha256):

| record | shard | pinned shard sha256 |
| --- | --- | --- |
| defn-onto-obo-go.json | go.jsonl | 9d661d25…2930f8 |
| defn-onto-obo-so.json | so.jsonl | 10fae0e4…30c8bf |
| defn-onto-obo-mondo.json | mondo.jsonl | b9d20d63…9bab5e |

A `definitional` endorsement is an ENDORSEMENT, not an extension-constraint
(memo §3, ASM-DEF-4): it is consumed ONLY by the define-op index and NEVER
enters the CWA store-validation pass over world-layer facts. `subject` is a
minted onto-obo corpus-marker URN (§3.1); the subject value does not affect any
coverage count (the index is keyed off shard membership, not the subject).

## Why a separate corpus (NOT data/axioms-v0/)

`data/axioms-v0/` is l3a's FROZEN pinned test corpus (registry/experiments/l3a.json
pins its `axioms-v0` corpus-hash). Adding endorsement files there would change
that corpus digest and break l3a's pin. This corpus is instead a GROWING corpus
pinned by NO frozen experiment — endorsing another shard here appends a file
without re-freezing any registry record. `tools/axiom/kot_axiom.build_engine`
loads its definitional endorsements from here (via `load_definitional_endorsements`);
the l3a store path (`load_corpora`) is untouched and still reads only axioms-v0.

Research-grade, agent-authored; NOT federation-endorsed.
