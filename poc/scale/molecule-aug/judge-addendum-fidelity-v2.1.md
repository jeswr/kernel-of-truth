# S5 judge addendum v2.1 — checklist fidelity instrument (REPILOT-v2.1)

> DESIGN ARTEFACT (REPILOT-v2.1). Composed at judge time onto the UNMODIFIED base
> `poc/scale/ast-pipeline/judge_prompt.md` to form `s5-judge-fidelity-v2.1.md` —
> the PRIMARY instrument for the repaired S5 campaign. It supersedes
> `judge-addendum-v2.md`: the pilot measured F1/F2 kappa 0.204 under the v2
> holistic protocol; this version replaces the free FAITHFUL/LOSSY threshold with
> a mandatory criterial-feature audit and a MECHANICAL verdict rule, which is the
> component that agreement analysis indicted. Applied identically to ALL
> candidates (both arms). Verdicts under this instrument are not comparable to
> verdicts under the base pooled prompt, the v1 conditional prompt, or the v2
> fidelity prompt.

## Protocol (unchanged from v2)

1. **Exactly ONE candidate per request.** One concept header, a single candidate
   labelled `=== CANDIDATE A ===`. Your `verdicts` array contains exactly one
   entry, for "A". You will never see other candidates for this concept; do not
   try to infer or compare. Requests are independent: no comparison, no memory.

2. **Candidates are fully expanded.** Every candidate has been mechanically
   rewritten so that it contains ONLY profile-1 prime material. Where an
   explication composed in another already-defined concept, that concept's own
   explication has been inlined in place as a nested
   `{"kind": "subExplication", "frame": …, "referents": […], "clauses": […]}`
   block. Read a `subExplication` block as a self-contained sub-definition whose
   full meaning applies at that position (its `referents` indices are local to
   the block). Judge the meaning the nested material ACTUALLY renders in primes —
   you are never asked to take any gloss or label on credit; none are shown.

3. **No provenance, no comparison.** Do not penalize (or reward) size, nesting,
   or style of composition as such. Provenance is unknowable and irrelevant.

## Decision procedure (NEW — mandatory, in this order)

**Step 1 — CRITERIAL FEATURES.** From the concept header (the sense-fixing
wn31 gloss plus lemmas/pos), enumerate 2–6 criterial features of THIS sense:
the genus (what kind of thing it is) and each differentia that distinguishes
this sense from its nearest neighbours and siblings. Number them. What is NOT
criterial: encyclopedic detail, typical-but-not-defining properties, register,
connotation, and anything true of the genus generally.

**Step 2 — FEATURE AUDIT.** For each numbered feature, classify it against the
RENDERED MATERIAL ONLY (primes + inlined subExplication content):
- **PRESENT** — the rendered clauses entail the feature. An approximate
  rendering counts as PRESENT if it still separates this sense from its
  siblings; prime-level paraphrase is the norm here, not a defect.
- **MISSING** — no rendered material carries the feature.
- **CONTRADICTED** — rendered material asserts something incompatible with the
  feature (or with the sense).

**Step 3 — MECHANICAL VERDICT.** `FAITHFUL` iff every criterial feature is
PRESENT and none is CONTRADICTED; otherwise `LOSSY`. No holistic override in
either direction: do not upgrade a MISSING-feature record because it "feels
close", and do not downgrade an all-PRESENT record because it is bloated, ugly,
or nested (bloat costs `quality`, not the verdict).

**Output format is unchanged** (STRICT-JSON, single "A" entry, verdict
inventory FAITHFUL/LOSSY, quality 0–3), with these two content rules:
- `reason` MUST be the audit itself, compact, e.g.
  `"1 genus event: PRESENT (clause 1); 2 spouse died before: MISSING; 3 …"`.
- `missing` MUST list exactly the MISSING/CONTRADICTED features (empty string
  if none). Judge `quality` after the verdict, as before.

### Micro-anchors (synthetic, not from any evaluation set)

- Concept "vow (a solemn promise)"; rendering says: someone says words to
  someone; because of this, this someone has to do something after now; this
  someone wants the other someone to know it is true. Features: 1 genus
  speech-act/promise: PRESENT; 2 commitment created: PRESENT; 3 solemn/binding
  seriousness: PRESENT (has-to + truth clauses carry it approximately) →
  **FAITHFUL**, even though "solemn" is rendered only approximately.
- Concept "orphan (a child whose parents are dead)"; rendering says: this
  someone is small; this someone is not with the mother and father. Features:
  1 genus child: PRESENT; 2 parents DIED: MISSING (absence ≠ death) →
  **LOSSY**, however well-formed the rest is.

## ADJUDICATOR protocol (F3 only)

If the request additionally contains a block headed
`=== ADJUDICATION: REVIEWER VERDICTS`, you are the ADJUDICATOR for a
disagreement between two independent reviewers. Then:

1. Ignore the reviewers' verdicts at first: run Steps 1–3 yourself, from
   scratch, on the candidate.
2. Compare your audit with both reviewers' audits (given in their `reason`/
   `missing` fields). For each feature on which they differ, resolve it
   explicitly: say which reviewer's reading of the rendered material is
   correct and cite the clause(s) that decide it.
3. Output the SAME strict-JSON single-"A" format; your `reason` is your own
   audit plus the per-feature resolutions. The mechanical verdict rule (Step 3)
   applies to your final feature classification.
