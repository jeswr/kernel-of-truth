# The `modelAuthored` record tier — schema (haiku-tier/1)

**Status:** stage-1 deliverable (kernel-of-truth-b96), 2026-07-07. This is the
record shape the volume runner emits for gate-passing model outputs. It slots
into the honesty architecture of `docs/design-bulk-kernel.md`: model
authorship is a **provenance fact carried inside the record**, and the tier
sits **below Explicated and below hand-authored Molecule** on the status
ladder — a modelAuthored record is a *candidate* that mechanical gates have
accepted and **no human or federation has endorsed**. Nothing counts it in
Explicated/Molecule coverage statistics until it is individually reviewed and
upgraded (which mints a new record under the concept-hash pipeline anyway;
gist §8 semantics).

## Record shape (one JSON file per concept, `data/haiku-tier/records/<lemma>.json`)

```json
{
  "schema": "haiku-tier/1",
  "id": "urn:haiku-tier:<lemma>",
  "label": "<lemma>",
  "semanticStatus": "ModelAuthored",
  "candidateStatus": "Molecule" | "Explicated",
  "kind": "molecule" | "explication",
  "gloss": "<model's one-line plain gloss>",

  "groundingNote": "...",          // kind=molecule only — §3.5-gated
  "groundingRefs": ["urn:..."],    // kind=molecule only
  "moleculeDepth": 1..4,           // kind=molecule only, computed by the gate

  "record": { ...kot-ast/1... },   // kind=explication only — encoder-gated

  "gatesPassed": true,             // only gate-passing outputs become records
  "researchGrade": true,
  "provenance": {
    "model": "claude-haiku-4-5-20251001",
    "framework": "A+gate-loop-repair",   // s1 winner: draft + gate-error-fed repair
    "promptVersionHash": "sha256:<hash of the exact draft system-prompt file>",
    "repairPromptVersionHash": "sha256:<hash of the repair system-prompt file>",
    "pipelineVersionHash": "sha256:<hash over the pinned pipeline files>",
    "sources": [
      {"source": "wiktionary", "url": "https://en.wiktionary.org/api/rest_v1/page/definition/<lemma>", "revision": "<rev/tid from ETag>", "fetched": "<ISO date>"},
      {"source": "wikipedia",  "url": "https://en.wikipedia.org/api/rest_v1/page/summary/<lemma>", "revision": <rev>, "tid": "<tid>", "fetched": "<ISO date>"}
    ],
    "date": "<ISO date of the model call(s)>",
    "usage": [ /* one entry per call: draft, then repair if it ran */
      {"inputTokens": n, "outputTokens": n, "cacheReadInputTokens": n,
       "cacheCreationInputTokens": n, "costUSD": x} ]
  }
}
```

## Semantics and constraints

- **`semanticStatus: "ModelAuthored"`** is the tier marker. It is deliberately
  NOT one of the gist's endorsed statuses (`Explicated`/`Molecule`/
  `AxiomsOnly`): renderings must surface it, coverage measurements must bucket
  it separately (an "modelAuthored-reachable" band, exactly as
  design-bulk-kernel.md prescribes for AxiomsOnly), and federation admission
  per gist §8 requires per-record human endorsement, which upgrades
  `candidateStatus` into the real status by minting a proper record.
- **`candidateStatus`** says which endorsed status the record is a candidate
  for; the mechanical gates for that status have all passed (encoder
  grammar/valency/referent gates for `Explicated`; the §3.5 rule-1/3/4/5 gate,
  ref catalog, self-ref ban and depth <= 4 for `Molecule`). What has NOT been
  judged is semantic adequacy — the gist is explicit that adequacy is social
  (§1 claim 3), and for molecules there is deliberately no mechanical
  decomposability test (§3.5 rule 6).
- **Provenance is mandatory and sufficient for re-derivation**: model id,
  prompt hash, pipeline hash, source revisions, date. A modelAuthored record
  is an assertion by a pinned pipeline about pinned sources; anyone can re-run
  the pipeline at those pins and diff.
- **Batched pipeline provenance** (`--batch-size N` in the volume runner;
  framework string e.g. `"A-batch4+gate-loop-repair"`, prompt hashes are of
  the `system-A-batch.txt`/`system-F-batch.txt` files): when one draft (or
  repair) call covered several lemmas, each affected record additionally
  carries `provenance.batch = {"size": N, "lemmas": [...]}` and its
  `usage[]` entries carry `"sharedAcrossLemmas": k` — the entry holds the
  FULL usage/cost of the shared call (honest, re-derivable); divide by
  `sharedAcrossLemmas` for a per-lemma cost attribution. Each lemma's output
  block is extracted by its own sentinels and gated independently, so
  record legality remains independent of every other model output in the
  batch, exactly as in single mode.
- **Refs** may point only at kernel-v0 / molecules-v0 ids (the frozen catalog
  in the prompt). haiku-tier records never reference each other in v0 —
  grounding cycles are impossible by construction and each record's legality
  is independent of every other model output.
- **Failures are data**: gate-failing outputs and `cannot-formalise`
  abstentions are logged (volume/failures.jsonl, volume/cannot-formalise.jsonl)
  with the same provenance, not discarded.
- Ids are placeholder URNs like kernel-v0's; minting content-addressed
  `urn:concept:` identities remains the concept-hash pipeline's job.
