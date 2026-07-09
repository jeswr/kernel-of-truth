# code-corpus-v0 — pinned Python snapshot corpus (A5)

A frozen SNAPSHOT of 15 Python files copied 2026-07-09 from this repo's own
tooling; the A5 extractor (`kot-code-extract/1`,
`tools/axiom/gen_a5_corpora.py`) reads ONLY these copies, and the kot-reg/1
corpus pin hashes them — later edits to the live originals cannot drift the
experiment inputs.

Snapshot origin (live path -> `src/<basename>`):

- tools/registry/claims-check.py, corpus-pin.py, kot_common.py,
  log-append.py, prereg-freeze.py, registry-check.py, report-gen.py,
  test_fixtures.py, verdict-gen.py
- tools/axiom/kot_axiom.py, gen_l3a_corpora.py
- tools/experiments/l3a_instrument.py, m0b_instrument.py
- analysis/l3a.py, m0b.py

The corpus is an arbitrary-but-real, small, license-clean code sample; its
representativeness of real codebases is explicitly OUT of the a5 verdict's
scope (docs/design-a5-code-worldlayer-oracle.md §8).
