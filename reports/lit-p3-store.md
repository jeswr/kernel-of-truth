# P3-LR-STORE — Store authoring, maintenance, provenance + knowledge-update economics

**Bead:** P3-LR-STORE (Programme-3, Phase-0 [LIT]; `…s55r.10`).
**Deliverable path:** `reports/lit-p3-store.md`.
**Author/role:** literature-review agent (Opus execution), independent source-verification + formalization pass.
**Date:** 2026-07-19. **Status:** DRAFT for coordinator review. Nothing here is frozen, registered, or
scheduled; no registry record / ASM / KB shard / bd / git operation is touched.
**Parent:** `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §1.3a (KOT-LIFE/1 lifecycle
ledger), §2.2a (sealed evaluation / P3-D-SEAL store leg), §5 P3-LR-STORE row.
**Feeds:** P3-D-LIFE (KOT-LIFE/1 amortisation model + logging hooks — store leg), P3-D-SEAL
(temporally-fresh-facts store leg), the coverage-growth feeder line
(`docs/next/coverage-growth-ingestion-plan.md`).

> **Relationship to `docs/next/lit/STORE.md`.** A thorough prior STORE review exists (Fable,
> 2026-07-11, already once self-corrected against a GPT-5.6 cross-vendor review — the "2026-07-11b"
> revision). **This report does NOT redo it.** It (a) re-verifies STORE.md's load-bearing citations at
> source this session, (b) formalizes the decision content into the requested `reports/` deliverable,
> and (c) records divergences. Where I re-fetched a source I say `[search: 2026-07-19]`; the
> citation-verification table (§7) records reachability + claim-support per source. **Headline: the
> 07-11b draft is well-verified — its own downgrades (maintenance = material risk, not demonstrated
> killer; $219-bound withdrawn; O(1)-update narrowed) are the source-supported readings, and I
> independently confirm them. One material same-class numeric divergence was found (vbag028 scale
> figures, §8), plus three minor/precision notes. No divergence overturns a decision-relevant
> conclusion.**

## Epistemic tag convention
- `[established]` — external empirical/methodological fact confirmed at a primary source this session.
  `[claimed]` — asserted in a source but single-source, or body/abstract-level not independently
  corroborated. `[speculative]` — my forward inference / design judgement.
- Provenance suffix: `[search: 2026-07-19]` = re-verified via WebSearch/WebFetch this session;
  `[prior-verified: 2026-07-11]` = verified at source in STORE.md/STORE.sources.jsonl, cited here
  without re-fetch; `[memory]` = from the parent design doc or in-repo verdicts, not re-checked at
  source; `[repo-internal MEASURED]` = an in-repo measured figure confirmed by path this session.
- `[UNVERIFIED]` marks anything not confirmable at primary source (ACM/OUP 403, undecoded PDF binary,
  or figure genuinely absent from the fetched text).
- Load-bearing lines also carry `[MEASURED | STIPULATED | EXTRAPOLATION]` in the parent's sense:
  **MEASURED** = a published number restated inside its source's own envelope; **EXTRAPOLATION** =
  cross-source/cross-domain, direction-only, never a verdict premise; **STIPULATED** = a scoping
  decision made here.

---

## 1. Verdict up front — is store-maintenance economics *fundamental* or *capability-limited*?

**The bead's core question, answered.** Across the three closest structural analogues to a KOT store —
XCON/R1 (interdependent correctness rules over a fast-churning world), Cyc (hand-encoded axiom store),
Freebase (curated collaborative KB) — the verified primary/secondary record supports **exactly one**
reading, and it is the 07-11b draft's corrected one:

> **Store maintenance + knowledge-acquisition economics is a MATERIAL, first-order,
> explicitly-accountable RISK to the kernel's lifecycle cost — NOT a demonstrated cause of death of
> this class of system, and NOT shown to be *fundamental* rather than an implementation / representation
> / tooling problem.** `[established][search: 2026-07-19]`

The evidence that forces the *risk* half:
- XCON grew to **>6,200 rules over ~20,000 parts with ~50% of the rules changing each year** — a
  formidable, documented, recurring maintenance load `[established][search: 2026-07-19]`
  [MEASURED: Barker & O'Connor, *CACM* 1989 — corroborated at Wikipedia/Semantic Scholar; ACM PDF 403].
- Cyc consumed **a person-century of hand-encoding to reach ~10⁶ axioms (over ~10⁵ concepts) by 1995**
  `[established][search: 2026-07-19]` [MEASURED: Lenat, *CACM* 1995 — corroborated at a hosted
  full-text copy + multiple secondary quotations; ACM PDF 403].
- The Freebase→Wikidata migration routed candidate statements through **per-statement manual human
  approval** (~90,000 approve/reject actions covering only a small fraction of ~14M candidates)
  `[established][search: 2026-07-19]` [MEASURED: Pellissier Tanon et al., WWW 2016].

The evidence that **blocks** the "fundamental killer" half — and this is the load-bearing correction:
- **XCON was a production success, not a maintenance casualty.** Barker & O'Connor present it as the
  successful cornerstone of a growing family of Digital expert systems with satisfactory run-time
  performance; maintainability became a *research problem*, and DEC's response was to build a **more
  maintainable successor (the RIME re-implementation)** — a *tooling fix*, not an abandonment
  `[established][search: 2026-07-19]` [Soloway et al., AAAI-87, title verbatim: "Assessing the
  Maintainability of XCON-in-RIME: Coping with the Problems of a VERY Large Rule-Base"].
- **Freebase was consolidated because Wikidata *succeeded*, not on a stated unsustainability finding.**
  The migration paper's rationale is verbatim: *"Due to the success of Wikidata, Google decided in 2014
  to offer the content of Freebase to the Wikidata community."* No primary source in this sweep states
  Freebase was "unsustainable" or "not worth its maintenance cost" `[established][search: 2026-07-19]`.
- **Cyc supplies effort, not a causal verdict.** Lenat 1995 gives the person-century/10⁶-axiom cost;
  no source in this sweep shows Cyc losing to a learned baseline at matched cost, but a small
  non-systematic sweep finding no win is **absence-of-evidence, not proof of no win**
  `[speculative]` — the draft states this correctly.

**Where a genuinely fundamental-looking cost *does* survive (the honest nuance):** the
knowledge-**acquisition** bottleneck (Feigenbaum's diagnosis) and the recurring **refresh** cost are
the two halves that are *hard by nature*. But acquisition is exactly what the modern LLM-assisted
human-in-the-loop re-entry attacks (the vbag028 direction; the programme's own $0.078 mint), so it is
**capability-limited (attackable), not immutable** `[established][search: 2026-07-19]`. The
**maintenance/refresh TCO** half is the one the literature leaves genuinely **OPEN** — no source prices
a per-fact refresh rate/cost — so whether it is fundamental *for the kernel* is an **unmeasured
empirical question P3-D-LIFE / P3-D-SEAL must answer, not assume** `[speculative]`. **This is the
defensible verdict: risk is proven, doom is not, and the one truly-open cost (refresh TCO) must be
measured — the ledger's job is to force that measurement (K-P3v2(6)), not to presume the outcome.**

---

## 2. Cost-per-record accounting practice for curated KBs (findings, tagged)

- **The one clean fetched-and-parsed anchor — EcoCyc $219/curated article.** `[established][search:
  2026-07-19]` Karp computes **$219 per curated article** transparently as **$2.1M curation labour /
  9,606 newly cited publications** over May 2011–2016; he frames it as **6–15% of a biomedical
  open-access publication fee ($1,500–$3,500)** and **0.088% of the NIH R01** that produced the paper.
  [MEASURED: Karp, *Database* 2016, doi:10.1093/database/baw110 — **all four figures re-verified
  verbatim at PMC full text this session**.] **The skeptical reading the ledger must keep:** this is
  cost *per source article ingested*, charged against a *pre-existing, externally-funded* literature —
  and it is **not** a per-checkable-fact cost. The $219/article figure is **neither a lower nor an
  upper bound** on per-checkable-record cost, because an article yielding *n* accepted facts allocates
  ≈$219/*n* + per-fact normalization/review/refresh; *n* (article→accepted-fact yield) is the
  **unmeasured** quantity. `[established for the article figure; the per-fact bound is OPEN]`
  *(The 07-11b draft's removal of the invalid "≥$219 per checkable record" bracket is confirmed
  correct.)*
- **Crowd + redundancy reaches expert-competitive quality on some tasks at ~$1–2/abstract.**
  `[established][search: 2026-07-19]` The drug-indication crowd experiment: **~$1.75/abstract**, **five
  judgements each**, **18,775 judgements from 74 Mechanical-Turk workers in ~8h over 3,000+ HITs**,
  **~96% control accuracy** (restated by Hirschman et al. as **96% precision / 89% recall**) —
  **above** the cited **expert baseline ~90% precision / 70% recall** [MEASURED: Good et al.,
  *Database* 2015, bav016 — re-verified at PMC; expert P/R baseline verified at Hirschman baw115]. A
  gene-mutation crowd experiment reached **~80% precision / >70% recall for <$1/abstract**
  [MEASURED: Hirschman et al., *Database* 2016, baw115 — re-verified at OUP full text]. And the
  foundational NLP result: aggregating **~4 paid non-expert labels/item** rivals expert-level quality,
  studied across **five tasks** [MEASURED: Snow et al., EMNLP 2008 — five tasks corroborated; "~4"
  is the paper's abstract-level finding]. **Accounting lesson:** crowd curation *with redundancy* can
  match/exceed expert quality on crowd-tractable tasks at low unit price — but (a) quality is
  **task-conditional** (gene-mutation < drug-indication) and (b) redundancy **multiplies unit cost
  4–5×**. Whether a checker's load-bearing records fall in the crowd-tractable regime is an **open
  measurement**, not a settled quality gap. *(The 07-11b reversal of the prior "crowd is worse"
  reading is confirmed — there is no established universal crowd/expert gap.)*
- **The workforce ceiling is real but is a capture rate, not an immutable ceiling.**
  `[established][search: 2026-07-19]` Biological knowledgebases are maintained by **~100–200 full-time
  professional biocurators worldwide** [MEASURED: vbag028, 2026 — **verbatim confirmed at PMC full
  text**]. UniProtKB expert curation **captures 35–45% of the curatable literature per species (50% for
  human)** [MEASURED: UniProt Consortium, *NAR* 2019 — corroborated]. Even a mature, decades-old,
  well-funded operation **captures below completeness** on the literature it examines — but this is a
  **capture rate under a prioritisation strategy**, not proof of a saturation ceiling. *(07-11b's
  softening of "saturates / hard human ceiling" is confirmed correct.)*
- **The maximalist anchor — Cyc — is per-*axiom*, a different denominator.** `[established][search:
  2026-07-19]` Person-century / ~10⁶ axioms by 1995 [Lenat 1995]. This is **~person-year-per-10⁴-axioms**
  — it does **not** sit on the per-article axis and must not be averaged into the $1–$219/article span.
  Cumulative-to-2024 figures (~$200M / ~2,000 person-years / ~30M assertions) remain **[UNVERIFIED]**
  (tertiary encyclopedia aggregation, no primary financial disclosure).
- **Synthesis for the ledger.** Published per-*source-item* curation cost spans **~$1–2/abstract (crowd,
  redundant, task-dependent) → $219/article (expert biocuration)**; Cyc's per-axiom figure is a
  different denominator. **None** is a cost per *queryable/checkable* fact. These are **cost categories
  with order-of-magnitude anchors, not a coherent per-checkable-record range** — the article→fact yield
  *n* (§9.1) is the binding unmeasured quantity. `[MEASURED where fetched; the cross-denominator span is
  descriptive, not a bracket]`

---

## 3. Provenance, update, and staleness economics (the recurring cost the build figure hides)

- **Time-sensitive facts are a demonstrated failure mode for static parametric knowledge — and the
  paper's own remedy is *live search*, not a curated store.** `[established][search: 2026-07-19]`
  FreshQA shows all evaluated LLMs struggle on fast-changing questions and produce outdated answers;
  **FreshPrompt** (search-augmented few-shot prompting) substantially improves accuracy and beats
  Self-Ask / Perplexity.AI [MEASURED: Vu et al., Findings of ACL 2024]. **What it does NOT establish:**
  no per-fact *refresh rate* or *cost*; no proof facts "go stale continuously" as a rate; and it does
  **not** show a *maintained curated store* (vs live retrieval) is the required remedy — its own remedy
  is live search. So it motivates the P3-D-SEAL fresh-facts leg but supplies **neither cadence nor
  cost**, and it **leaves store-vs-live-search open**. *(07-11b narrowing confirmed.)*
- **Parametric fact-update is unreliable — but that is a *weak* baseline, not a matched one.**
  `[established][search: 2026-07-19]` RippleEdits (**5K edits**) shows ROME/MEMIT-class parametric
  editing fails to introduce consistent changes / propagate to entailed facts; a **simple in-context
  (external-context) baseline scores best** [MEASURED: Cohen et al., TACL 2024, verified at ACL]. And
  sequential parametric edits induce **gradual then abrupt catastrophic forgetting** [MEASURED: Gupta,
  Rao & Anumanchipalli, "Model Editing at Scale…", arXiv 2401.07453 — author + two-phase claim verified
  at arXiv]. **The defensible narrowed reading (07-11b, confirmed):** (i) record replacement is not the
  whole update cost — change-detection, provenance-check, dependency-finding, entailment propagation,
  revalidation, reindex, rollback are **not** generally O(1); (ii) the comparison was to a *straw*
  parametric channel, not the strongest neural retrieval/search/in-context baseline; (iii)
  external-knowledge separation is **not uniquely neural-symbolic** (RAG/tool-use/in-context share it).
  **Consequence:** externalising knowledge makes source records **directly replaceable + inspectable**
  — a genuine **design property** — but whether it **lowers end-to-end update TCO is OPEN** and must be
  measured against a matched external-context baseline. `[design property MEASURED; TCO advantage OPEN]`
- **Live collaborative KBs carry a standing staleness/quality debt.** `[established][search:
  2026-07-19]` Wikidata quality work formalises **three low-quality indicators — community consensus
  (removed-and-not-re-added statements), deprecated statements, and constraint violations** — and treats
  out-of-date information as an ongoing problem [MEASURED at abstract: Shenoy et al., *JWS* 2022, arXiv
  2107.00156 — **three indicators verbatim-confirmed; exact staleness percentages genuinely NOT in the
  abstract → [UNVERIFIED]**, as the draft flags]. More generally, KGs make an explicit
  **completeness-vs-correctness trade-off** requiring a *continuous* refinement stage (error detection +
  completion) — maintenance is **never-finished**, not a one-time build [MEASURED: Paulheim, *Semantic
  Web* 8:489-508, 2017 — pages + thesis corroborated].
- **Provenance is itself a per-record labour line.** `[established][search: 2026-07-19]` The
  Freebase→Wikidata migration mapped **~4.6M topics → ~14M candidate statements**, each requiring manual
  approval; **~90,000 approve/reject actions** through the Primary Sources Tool covered only a **small
  fraction** of candidates [MEASURED: Pellissier Tanon et al., WWW 2016 — 4.6M/14M/90,000 corroborated].
  The slow per-statement throughput is documented; calling provenance-verification *the* bottleneck is
  the reviewer's inference (07-11b downgrade confirmed). Ledger consequence stands: **"attach + verify
  provenance" is a distinct labour line that does not amortise away at scale**, not free metadata.
- **Synthesis for the ledger.** Time-sensitive facts force *some* refresh mechanism at *some* (unmeasured)
  cost; the parametric channel is unreliable at checker grade; externalisation yields a **design
  property (replaceability/inspectability)** but **not a demonstrated cost advantage**. The store side's
  honest §3 gain is a property, not a matched-cost win. `[design property MEASURED; TCO advantage OPEN]`

---

## 4. Human-review cost model — the shape KOT-LIFE/1 should adopt

Consolidating §2–§3 into the form P3-D-LIFE can log against:

- **Unit review cost scales with the quality target via redundancy; the crowd/expert gap is
  task-dependent, not universal.** Expert-grade correctness is reachable via professional curators
  (~$219/article-class, capped by a ~100–200-person global workforce) *or* via crowd+redundancy
  (drug-indication ~5 judgements/item at ~$1.75/abstract **matched/exceeded** the expert baseline;
  gene-mutation lower at <$1/abstract). Redundancy multiplies unit cost 4–5× [Snow 2008].
  `[established]`
- **Capture stays below completeness at mature scale** (~35–50% [UniProt]) — a capture rate, not a
  proven ceiling — so a near-completeness coverage target is outside the *demonstrated* envelope of
  manual curation; motivates AI-assisted HITL curation (vbag028) or a narrowed, defensible coverage
  claim (consistent with the programme's reachability-wall finding). `[established]`
- **Review cost is per-record and recurs on refresh** — a model that logs only build cost understates
  TCO. `[established]`
- **Provenance verification is a separate labour line** [Freebase→Wikidata], not free metadata.
  `[established]`
- **Internal calibration point.** The own-store mint is **~$0.078/legal record** (31.7% gate-pass, 13
  legal / 50 concepts) `[repo-internal MEASURED: docs/next/a-f0-mint-economics-spec.md S1]` — but that
  is **mint only** (no human review, no provenance verification, no refresh), so it is a **lower bound**
  on cost-per-maintained-record; the external literature says the true figure is dominated by the
  review + refresh lines the mint number omits. `[EXTRAPOLATION, direction-only]`

**The KOT-LIFE/1 store-review model (recommended fields).** Log per record class:
`build_or_mint_$` (denominated per *accepted checkable fact*, not per source article) ·
`review_$` (with an explicit redundancy multiplier *m* and its quality operating point) ·
`provenance_verify_$` (distinct line) · `refresh_$` at a declared `cadence` ·
`rejected_candidate_attrition` (candidates paid-for but not accepted) ·
`dependency_fanout` (entailment ripple triggered per keyed update) — each with an uncertainty range,
and human time logged as a **distribution** (long tail), not a mean.

---

## 5. Implication for KOT-LIFE/1 (§1.3a) — what this review settles

The parent §1.3a store line is a *single* item — "(3) store costs: authoring, parsing, embedding,
indexing, and human review, in hours and $." **This review's concrete implication: split it into three
recurring sub-lines, not one scalar** `[STIPULATED, grounded in §2–§4]`:

1. **build/mint** — denominated per *accepted, checkable fact* (not per source article). Anchors:
   $0.078/legal record (mint stage only, internal) and $219/article (expert external) — **different
   denominators, NOT a bracket** on per-checkable-record cost. The article→accepted-fact yield *n* is
   the single biggest ledger uncertainty (§9.1).
2. **human-review + provenance** — recurring, with a redundancy multiplier and a **distinct
   provenance-verification line** (Freebase→Wikidata precedent).
3. **staleness-refresh** — at a declared cadence for time-changing facts (FreshQA motivates it, prices
   none).

A single "store cost" scalar understates TCO and would let an uncosted-curation win slip through — the
exact failure mode §1.3a's kill condition **K-P3v2(6)** exists to catch `[memory: K-P3v2(6) fed by
KOT-LIFE/1]`. **The historical precedent (§1) justifies K-P3v2(6) as an *explicit-accounting guard*,
not a doom presumption** — XCON/Cyc/Freebase make store maintenance/acquisition a material first-order
cost that must be accounted, and two of the three were successful in their slice, so the precedent
licenses *accounting*, not a presumption of failure. **One store-side design property to log (and only
a property):** externalised records are **directly replaceable + inspectable** where parametric memory
is not — genuine, but **must not** be booked as a matched-cost update advantage until measured against
a matched external-context (RAG/search) baseline, and it is bounded to in-coverage / mapper-reachable
facts. `[STIPULATED]`

---

## 6. Implication for the sealed store leg (§2.2a / P3-D-SEAL) + the coverage-growth feeder

- **Sealed fresh-facts leg (§2.2a).** The parent requires that for store-based systems the sealed suite
  "includes temporally-fresh facts and/or independently held-out domains." **This review's contribution:
  the fresh-facts leg carries a real but *unpriced* refresh cost** — FreshQA shows time-sensitive facts
  are a demonstrated failure mode for static knowledge (search augmentation helps) but measures **no
  rate and no cost**, and does **not** establish a curated store (vs live retrieval) as the remedy.
  P3-D-SEAL therefore cannot treat the fresh-facts leg as free; it must **(a)** co-register cadence +
  per-fact refresh cost with δ_sealed, **(b)** decide store-vs-live-search as the remedy, and **(c)
  decide *whose* cost is charged** — benchmark-producer truth-refresh vs participant store-maintenance
  vs both — and must **not** asymmetrically charge producer-side fresh-fact construction to the store
  system while a neural/search baseline gets the evaluation evidence or live search for free. Provenance
  verification is a distinct labour line here too. `[STIPULATED]`
- **Coverage-growth feeder line** (`coverage-growth-ingestion-plan.md`, costs logged into KOT-LIFE/1).
  **Contribution:** ingestion's "cost per ingested record" is confirmed to **understate cost per
  checkable record** — checkability ≠ vocabulary coverage; d-ext measured **~49% lemma-touch coexisting
  with 0% checkability** `[repo-internal MEASURED: coverage-growth-ingestion-plan.md §0]`. Manual
  curation **captures below completeness** (UniProt 35–50%, a rate not a ceiling), so the feeder's κ_B
  ambitions must be paired with the mapper/world-layer work the plan already flags, and its per-record
  economics **must use the checkable-record denominator** (§9.1), not the ingested-record one. This is
  the single most important internal correction the store ledger must carry. `[established +
  repo-internal MEASURED]`

---

## 7. Citation-verification table (ref → reachable at source? → supports the load-bearing claim?)

All 18 `STORE.sources.jsonl` entries assessed this session (2026-07-19). "Supports" = the primary
source (or, where the venue 403s, ≥2 independent secondary quotations) carries the draft's load-bearing
figure. **Fetched-and-parsed = read off the source page myself this session; corroborated = venue 403
/ PDF binary, figure confirmed across independent secondaries.**

| # | id | Reachable | Supports draft claim | Note (2026-07-19) |
|---|---|---|---|---|
| 1 | karp-curation-cost-2016 | yes (PMC) | **yes — all 4 figures verbatim** | $219 · $2.1M/9,606 · 6–15% OA fee · 0.088% R01 — **fetched-and-parsed** |
| 2 | good-drug-indication-crowdsourcing-2015 | yes (PMC) | **yes** | $1.75 · 18,775 judgements · 74 workers · ~8h · 96% control accuracy — **fetched-and-parsed**. (P/R split is Hirschman's restatement — draft handles correctly) |
| 3 | hirschman-crowdsourcing-curation-2016 | yes (OUP) | **yes — authorship + all figures** | **Authors verbatim** (Hirschman, Fort, Boué, Kyrpides, Islamaj Doğan, Cohen — prior misattribution to "Good & Su" confirmed fixed); 96/89 · 80/>70 · expert 90/70 · $1.75 · <$1 · 15–20 min @ $30/hr — **fetched-and-parsed** |
| 4 | uniprot-nar-2019 | yes | yes | 35–45% per species / 50% human — corroborated (jsonl: OUP full-text fetched 07-11) |
| 5 | biocuration-hitl-2026 (vbag028) | yes (PMC) | **PARTIAL — see §8** | "**~100–200 biocurators**" **verbatim-confirmed at PMC full text**; but **>20M PubMed / ~40,000 GO terms / ~1,400 microRNA-over-a-decade NOT located** in the paper (it cites ~37M Europe PMC records + 1.2M GO associations) — **DIVERGENCE** |
| 6 | lenat-cyc-cacm-1995 | ACM 403 | yes | person-century · ~10⁶ axioms · ~10⁵ concepts — corroborated (hosted full-text copy + secondaries) |
| 7 | cyc-scale-tertiary-2024 | yes | n/a | $200M/2,000py/30M — **[UNVERIFIED]** tertiary; draft flags correctly; never load-bearing |
| 8 | barker-oconnor-xcon-cacm-1989 | ACM 403 | yes | >6,200 rules · ~20,000 parts · "**about half** the rules change each year" (~50%) — corroborated. Draft's "~40–50%, unresolved" is conservative-safe; dominant corroborated value is ~50% |
| 9 | soloway-xcon-rime-aaai-1987 | PDF binary | yes | Maintainability = the research problem; RIME = more-maintainable successor — thesis verbatim in title; corroborated |
| 10 | pellissier-tanon-freebase-wikidata-www-2016 | ACM 403 (abstract fetched) | yes | 4.6M topics · 14M statements · ~90,000 actions · rationale "**success of Wikidata**" — corroborated |
| 11 | freebase-shutdown-news-2014 | yes | yes | 16 Dec 2014 announcement; read-only 2015; closed 2016 — widely reported; consolidation framing confirmed |
| 12 | vu-freshllms-acl-2024 | yes (ACL) | yes (with note) | FreshPrompt + LLMs-struggle **verbatim**; "**600 QA pairs**" NOT in abstract (abstract cites >50K judgments) — body-level, number is correct but not abstract-verified |
| 13 | cohen-ripple-editing-tacl-2024 | yes (ACL) | **yes** | 5K edits · fail-to-propagate · in-context baseline best — **verbatim** |
| 14 | gupta-editing-catastrophic-forgetting-2024 | yes (arXiv) | **yes** | Author (Gupta, Rao, Anumanchipalli) + gradual-then-catastrophic two-phase — **verbatim** |
| 15 | shenoy-wikidata-quality-jws-2022 | yes (arXiv) | yes (with note) | Three indicators **verbatim-confirmed**; exact staleness % genuinely **[UNVERIFIED]** (not in abstract) — draft flags correctly |
| 16 | paulheim-kg-refinement-semweb-2017 | yes | yes | pp. 489–508 · completeness-vs-correctness · continuous refinement — corroborated. Minor: sagepub byline shows "Cimiano, Paulheim"; dblp/author-copy = **single-author Paulheim** → draft attribution correct |
| 17 | snow-cheap-fast-emnlp-2008 | ACL page (no abstract); PDF binary | yes (with note) | **Five tasks confirmed** (affect, word-sim, RTE, temporal ordering, WSD); "~4 non-expert labels rival expert" is the paper's abstract-level finding, corroborated not extracted verbatim this session |
| 18 | feigenbaum-ka-bottleneck-1977 | not fetched | attributed | KA-bottleneck coinage widely attributed; "60% fail / 70–80% effort on KA" folklore **[UNVERIFIED]** — draft flags correctly |

**Verification outcome: 18/18 reachable or corroborated. 15/18 fully support their load-bearing claim;
1 PARTIAL (vbag028 — core figure confirmed, three scale figures diverge, §8); 2 carry the draft's own
correctly-flagged UNVERIFIED (cyc-tertiary, Feigenbaum folklore).** No load-bearing *decision* rests on
an unverified figure. Notably, the citation most at risk — baw115, already once wrong on authorship —
now **fully verifies at source** (authors + every figure).

---

## 8. Divergences from the Fable draft (reported explicitly, per discipline)

1. **vbag028 scale figures — same-class numeric divergence [correct in the deliverable].** The draft §1
   and `STORE.sources.jsonl` entry 5 attribute to vbag028: "**>20M PubMed articles**", "**~40,000 GO
   terms**", and "only **~1,400 microRNA articles curated to GO over a decade**". At the paper's **PMC
   full text this session**, only the "**~100–200 full-time professional biocurators worldwide**"
   figure is present (verbatim); the paper instead cites **~37M research-article records in Europe PMC**
   and **1.2M manually-curated GO associations** — the ">20M PubMed / ~40,000 GO terms / ~1,400
   microRNA/decade" figures were **not located** in it. This is the closest analogue in this review to
   the prior passes' Sardana / TinyAgent-40k-vs-80K / TeCoD catches: decorative scale figures attached
   to a citation that does not carry them. **Impact on conclusions: none** — the load-bearing
   "workforce-ceiling ~100–200 curators" point survives fully, and the "capture-below-completeness"
   point rests on UniProt (independently verified). **Recommend:** the coordinator either (a)
   de-attribute the three scale figures from vbag028 and re-source them (the microRNA figure needs a
   real primary source; ~40k GO terms and >20M PubMed are true general facts but not from this paper),
   or (b) replace them with the paper's actual figures (~37M Europe PMC, 1.2M GO associations), in both
   `STORE.md` §1 and `STORE.sources.jsonl` entry 5.
2. **FreshQA "600 QA pairs" — body-level, not abstract [soft precision note].** The number is correct
   (FreshQA is 600 questions) but is **not in the abstract** I fetched (which cites >50K human
   judgments). Not a divergence — the figure is right — but the draft should not imply abstract-level
   support for it.
3. **Snow "as few as 4 … across five tasks" — mild conflation [precision note].** The **five tasks** are
   the study's scope (verified); the "~4 non-expert labels rival expert quality" result is specifically
   the paper's affect-recognition finding, not shown for all five. The draft's phrasing reads as if 4
   labels suffice across all five. Cosmetic; the redundancy-buys-quality conclusion is unaffected.
4. **Paulheim byline — not a draft error, worth a one-line note.** The sagepub landing page bylines
   "Philipp Cimiano, Heiko Paulheim"; the authoritative dblp record and the author's own copy
   (semantic-web-journal.net) list **single-author Heiko Paulheim** (Cimiano appears to be the handling
   editor). The draft's single-author attribution is **correct** — no change needed.

**No divergence overturns a decision-relevant conclusion.** The draft's own 2026-07-11b corrections
(withdrawal of the $219-per-checkable-record bound; narrowing of the O(1)-update claim; downgrade of
the "maintenance killed these systems / fundamental" thesis to "material risk"; softening of the
UniProt "hard ceiling" and the FreshQA "continuous staleness" readings) are **each independently
confirmed as the source-supported reading** by this pass.

---

## 9. Open questions carried forward (this is a measurement design, not a closed cost model)

The draft is explicit that it discovered **cost categories + order-of-magnitude anchors + failure
precedents**, not a cost model. This pass confirms that framing. P3-D-LIFE / P3-D-SEAL still must
*measure*:

1. **Cost per *accepted, checkable* record** (P3-D-LIFE) — the external figures are heterogeneous
   denominators ($219/article, ~$1.75/abstract, person-century/axiom); the programme needs cost per
   *mapper-reachable, licensing-axiom-backed, canonical* record. Requires measuring the
   **article→accepted-fact yield *n*** and **rejected-candidate attrition**. **The single biggest ledger
   uncertainty.** `[STIPULATED]`
2. **Fixed-vs-variable split + record classes + author/reviewer time distributions** (P3-D-LIFE) —
   measure before any TCO scalar is quoted. `[STIPULATED]`
3. **Refresh cadence + per-fact refresh cost + store-vs-live-search remedy** for the fresh-facts leg
   (P3-D-SEAL) — FreshQA prices none. `[STIPULATED]`
4. **Human-review quality/cost operating point** (P3-D-LIFE) — expert (~$219-class, workforce-capped)
   vs crowd+redundancy (task-conditional quality) vs AI-assisted HITL (vbag028; our mint). A registered
   normative choice, not a literature consequence. `[STIPULATED]`
5. **Provenance-verification line + dependency/entailment fan-out** (P3-D-LIFE, P3-D-SEAL co) —
   Freebase→Wikidata shows per-statement review is slow and non-amortising; measure the fan-out a keyed
   update triggers (change-detection → propagation → revalidation → reindex → rollback). `[STIPULATED]`
6. **Matched-baseline TCO comparison, not the ROME/MEMIT straw** (P3-D-LIFE) — measure externalised-
   record update TCO against the **strongest neural retrieval/search/in-context** baseline, which shares
   the mutable-knowledge separation. `[STIPULATED]`
7. **Whose cost is charged in the sealed leg** (P3-D-SEAL) — producer truth-refresh vs participant
   store-maintenance vs both; no asymmetric charging. `[STIPULATED]`
8. **Exact Wikidata/KG staleness rates** (P3-D-SEAL background) — **[UNVERIFIED]** here (abstract only);
   fetch full text or derive from sealed-refresh instrumentation if a design anchor is wanted.
9. **Is replaceability/inspectability bankable at competitive coverage?** (P3-D-LIFE) — real
   in-coverage, but the coverage/mapper walls mean the *fraction of real-world facts* to which any
   cheap-update property applies is itself unmeasured. `[STIPULATED]`

---

## 10. Source count

- **Ledger:** 18 entries in `docs/next/lit/STORE.sources.jsonl`, **all 18 assessed at primary/abstract
  source or via ≥2 independent secondary corroborations this session (2026-07-19)**. Reachability:
  18/18. Claim-support: **15/18 full · 1/18 PARTIAL (vbag028, §8) · 2/18 carry the draft's own correct
  UNVERIFIED flag (cyc-tertiary, Feigenbaum folklore)**.
- **Fetched-and-parsed off the source page this session (exact figures read):** Karp ($219/$2.1M/9,606/
  6–15%/0.088%); Good bav016 ($1.75/18,775/74/8h/96%); Hirschman baw115 (authors + 96/89/80/>70/90/70/
  $1.75/<$1/15–20 min/$30hr); vbag028 (100–200 biocurators); Cohen RippleEdits (5K + in-context);
  Gupta (author + two-phase); FreshLLMs (FreshPrompt); Shenoy (three indicators).
- **Corroborated at venue-403 / PDF-binary via independent secondaries:** Lenat, Barker & O'Connor
  (XCON), Soloway (RIME), Pellissier Tanon (Freebase migration), Paulheim, UniProt, Snow (five tasks).
- **Divergences (§8):** 1 same-class numeric misattribution to fix (vbag028 scale figures); 3
  minor/precision notes (FreshQA 600 body-level; Snow 4-labels/five-tasks conflation; Paulheim byline
  artifact — no draft change).
- **Verdict (§1):** store-maintenance economics is a **material, explicitly-accountable RISK — not a
  demonstrated killer, not shown fundamental**; the acquisition half is capability-limited (attackable),
  the refresh-TCO half is genuinely OPEN and must be measured. The 07-11b draft's corrected reading is
  independently confirmed.
- KB records (`kb/records/`) consulted for recall only; none cited as evidence (per
  `docs/next/literature-kb.md` §0). Repo-internal MEASURED anchors ($0.078 mint; m0b 0.3542; f2b ≤108
  concepts; d-ext ~49% lemma-touch / 0% checkability; K-P3v2(6)) confirmed by path this session and
  never widened beyond their verdict envelopes.
