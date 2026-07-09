# axioms-v0 — stratum-3 endorsed-axiom sidecar records (kot-axiom/1)

Six `kot-axiom/1` records (grammar: docs/design-constraint-layer.md §3.3;
engine: tools/axiom/kot_axiom.py; spec: docs/design-l3a-rules-engine-oracle.md §3):
mother/father functional + range, man/woman disjointness, bookmark
exact-one-maker cardinality, maker-of range, part-of inverseOf has-part.

Subjects are minted concept URNs from data/kernel-v0/ and data/molecules-v0/.
Relation direction/alias readings are STIPULATED (ASM-0004). Sidecar records
live OUTSIDE concept identity (directives §5; design-constraint-layer.md §3.5).
Research-grade, agent-authored; NOT federation-endorsed.

Generated deterministically by tools/axiom/gen_l3a_corpora.py (RNG-free).

## Definitional endorsements (define-op, kot-axiom/1 `definitional` kind)

Three corpus-scoped `definitional` endorsement records license the `define`-op
(docs/design-kot-query-define-op.md §3) over the onto-obo genus-differentia
`logicalDefinition` substrate — one per endorsed shard:

| file | shard | pinned `sourceVersion` |
|---|---|---|
| `defn-onto-obo-go.json` | `go.jsonl` | `sha256:9d661d25…` (post-8es) |
| `defn-onto-obo-so.json` | `so.jsonl` | `sha256:10fae0e4…` (post-8es) |
| `defn-onto-obo-mondo.json` | `mondo.jsonl` | `sha256:b9d20d63…` (post-8es) |

Each admits its shard's `logicalDefinitions` as a definitional-source by shard
name + extraction `sha256` (memo §3.1). Consumed ONLY by the define-op index,
never by the CWA store-validation pass (ASM-DEF-4). Each passes
`kot_axiom.validate_axiom_record`. The `sourceVersion` is re-pinned to the
post-`kernel-of-truth-8es` shard bytes (relation-resolved re-extraction).

### The `subject` convention (pinned here — memo §3.1 left it open)

DECISION [STIPULATED]: the `subject` of a corpus-scoped `definitional`
endorsement is a **minted onto-obo corpus-marker URN**, one per shard — NOT a
concept URN. Rationale: an endorsement is a governance act about a *shard as a
definitional-source*, not a claim about any concept, so its subject should not be
a real concept (which would falsely read as "this endorsement is about concept
X"). The marker is deliberately absent from the concept mint bridge
(`minted-urns.jsonl`) because it is a governance marker, not a concept. It is
**non-load-bearing** for the measurement: the engine licenses the define-op by
shard membership (`source.shard`), never by `subject` (verified — the census
reproduces its counts under any well-formed subject).

Marker URNs (verified to be computed by the SAME construction as `tools/mint` —
`urn:kot: = urnKot(sha256(utf8("kot-obo/1\n") || JCS(NFC(payload))))`, a
reproduction that also reproduces a known minted record URN):

| shard | marker payload (canonical) | subject URN |
|---|---|---|
| `go.jsonl` | `{schema:"kot-axiom/1", kind:"definitional-source-endorsement-subject", corpus:"onto-obo", shard:"go.jsonl"}` | `urn:kot:bciqbiesonu2nfevxdcg4ocxcy44m5doraxa4miyce4rxibgo52yoe2q` |
| `so.jsonl` | …`shard:"so.jsonl"` | `urn:kot:bciqh275lyay2amhdjfhxwkipm26oe2vdtafatl2c6oi4k62zg4nreoq` |
| `mondo.jsonl` | …`shard:"mondo.jsonl"` | `urn:kot:bciqbe67jtceyuc3hwacig5ry2tmlrpn3utqxu3idcqjbzve6wp2ouji` |

The marker payload's shape (no `sourceId`/`oboId`/`ontology`/`axioms`; `schema:
kot-axiom/1`) cannot collide with any real onto-obo record's identity payload.
