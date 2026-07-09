# world-v0 — stratum-4 world-layer records (kot-world/1)

598 assertion records (class + relation) over urn:kotw:v0:* entities,
referencing kernel concept URNs; every record carries provenance
(directives §5: facts live in the world layer, never in concept identity).

Content: the Presley anchor family (the maintainer's worked case —
mother(elvis-presley) = gladys-presley; provenance
"public-fact-agent-recalled", see ASM-0005), 30 synthetic 3-generation
families, 43 clean + 2 planted-conflict bookmarks with makers, 25 part-of
pairs, and DELIBERATE planted violations (2 two-mother children, 2
double-maker bookmarks, 1 both-sex entity, 1 mother-range violation) that the
engine must SURFACE as ERR_CONFLICT, never resolve.

Spec: docs/design-l3a-rules-engine-oracle.md §2. Generated deterministically
by tools/axiom/gen_l3a_corpora.py (RNG-free).
