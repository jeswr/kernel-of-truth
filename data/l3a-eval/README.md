# l3a-eval — the pre-registered L3a query set (kot-query/1)

900 closed-grammar queries: 600 COVERED (expected exact answers, authored
against data/world-v0 records) + 300 CONTROL (expected refusals with the exact
ERR_* code). Strata are pinned in manifest.json and asserted by the
instrument. Expected answers are computed from the generator's construction
tables, not from the engine (residual single-author circularity: ASM-0006).

Spec: docs/design-l3a-rules-engine-oracle.md §5. Generated deterministically
by tools/axiom/gen_l3a_corpora.py (RNG-free).
