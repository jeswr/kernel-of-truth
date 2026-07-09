# Lit-KB triage rubric — kernel-relevance 0–3 (N-C §2.3 step 1)

**Status.** FIXED rubric text for the (next-phase) Haiku triage pass over
title+abstract; its sha256 is recorded in `kb/manifest.json` (`triage_rubric_sha256`)
and becomes part of the extraction provenance pin. Changing this file changes the
pin — re-triage is then a deliberate, recorded event.

**This phase (no metered spend):** the ingest scripts compute a *mechanical
keyword prescore* (`prescore` on queue entries) using the §3 term lists below.
The prescore is a HEURISTIC ORDERING SIGNAL ONLY — it is not the triage score,
it decides nothing, and no record or document may cite it. Haiku triage assigns
the real `triage_score` next phase.

## 1. The score

| Score | Meaning | Fate |
|---|---|---|
| 3 | Directly on a live seam: injects/verifies fixed or structured representations at an LM boundary; trains a bridge into a frozen model; SAE/feature-label instrumentation; latent/concept-level reasoning loop | READ TIER (full-text extraction) |
| 2 | Same mechanism family but different goal, or same goal with a neighbouring mechanism (retrieval-augmented latents, constrained decoding, program-aided reasoning, process verification) | READ TIER |
| 1 | Background: embeddings/VSA theory, NSM/primitives linguistics, general interpretability, scaling analyses that bound our claims | ABSTRACT TIER (title+abstract chunk only, no structured record) |
| 0 | Off-programme | SKIP |

## 2. Scoring questions (answer from title+abstract only)

1. Does the paper move ANYTHING other than text across a model boundary
   (activations, vectors, KV entries, adapters, external-engine calls)?
   If yes → at least 2.
2. Is the moved thing FIXED/canonical/deterministic (not learned end-to-end)?
   If yes → 3.
3. Does it verify, score, or constrain LM outputs stepwise (verifier, PRM,
   constrained decoding, symbolic checker)? If yes → at least 2.
4. Does it operate at concept/sentence granularity in latent space (LCM, CALM,
   Coconut class)? If yes → at least 2.
5. Does it label, align, or canonicalise learned feature spaces (SAEs,
   dictionary features, representation alignment)? If yes → at least 2.
6. Is it a negative/correction result touching any of the above? Negative
   results score as the positive mechanism would — nulls are load-bearing.
7. None of the above but supplies theory/data our claims lean on → 1.

## 3. Programme term lists (mechanical prescore; heuristic only)

- **seam terms (weight 2):** inject, injection, knowledge editing, kv cache,
  soft prompt, prefix tuning, adapter, frozen language model, frozen LLM,
  bridge, projector, cross-attention knowledge, activation steering,
  representation engineering, embedding surgery
- **verify terms (weight 2):** process reward, verifier, self-verification,
  stepwise verification, constrained decoding, grammar-constrained, symbolic
  checker, proof checking, program-aided
- **canonical terms (weight 2):** tensor product representation, vector
  symbolic, hyperdimensional, holographic reduced, canonical vector,
  deterministic embedding, training-free, hand-set
- **concept terms (weight 1):** large concept model, sentence embedding
  reasoning, latent reasoning, continuous thought, concept bottleneck,
  semantic primitives, natural semantic metalanguage
- **interp terms (weight 1):** sparse autoencoder, dictionary learning,
  feature absorption, residual stream, mechanistic interpretability
- **anti terms (weight −2):** medical imaging, protein, molecular dynamics,
  recommender, autonomous driving, speech enhancement, wireless

`prescore = Σ weights over matched terms in title+abstract (case-insensitive,
substring match), floor 0`. Ties keep queue order (queued_at, then id).
