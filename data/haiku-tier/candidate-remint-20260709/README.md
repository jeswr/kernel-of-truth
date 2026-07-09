# haiku-tier candidate re-mint (2026-07-09) — NON-AUTHORITATIVE

Produced by an Opus data-pipeline execution run (`tools/mint --corpus haiku-tier`) on
2026-07-09 to reconcile the haiku-tier mint gap: ~2,673 authored record files on disk vs
only 84 minted URNs in the committed `data/haiku-tier/minted-urns.jsonl`.

**This is NOT the authoritative minted set.** Per maintainer instruction (2026-07-09), the
existing committed `data/haiku-tier/minted-urns.jsonl` (84 URNs) is left BYTE-UNCHANGED
(`git diff` on it is empty); this full re-mint is saved to a separate location so that
**Fable** can make the architectural call on which minted set to adopt and how to migrate
(bead `kernel-of-truth-lik` — incremental re-mint tooling). Opus made no architectural
decision here; it ran the existing pinned mint and redirected the output.

Contents:
- `minted-urns.jsonl` — 2,673 candidate minted URNs.
- `haiku-tier.canonical.jsonl` — the canonical records the mint consumed.
- `mint-manifest.json` — mint provenance.

Do not treat as authoritative until Fable reviews.
