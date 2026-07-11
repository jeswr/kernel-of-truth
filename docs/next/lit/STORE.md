# P3-LR-STORE — Store authoring, maintenance, provenance + knowledge-update economics

- **Bead:** kernel-of-truth-s55r.10 (P3-LR-STORE; Phase-0 [LIT], Programme-3 revision 2,
  `docs/next/programme-3-neurosymbolic-architecture.md` §5 table row P3-LR-STORE).
- **Author:** Fable (chief architect), 2026-07-11.
- **Deliverable pair:** this review + `docs/next/lit/STORE.sources.jsonl` (one JSON per source).
- **Purpose (decision-oriented):** de-risk the **store leg of the lifecycle ledger (KOT-LIFE/1)**
  and the **temporally-fresh-facts store leg of the sealed benchmark (P3-D-SEAL)** by pricing what
  it historically costs to *author, review, provenance, and keep current* a curated knowledge store,
  and by judging what store-maintenance economics did to the closest comparable prior systems
  (expert systems, knowledge graphs) — **capability-limited vs fundamental**. This review supplies
  the **cost categories** (the buckets a store ledger must carry) and the **failure precedents as
  material risk**, not a completed cost model and not a demonstrated "maintenance is the usual killer"
  verdict; it does **not** freeze the ledger or the sealed protocol (§7–§8 state the — still large —
  empirical measurement design that stays open for P3-D-LIFE and P3-D-SEAL).
- **What this revision corrects (GPT-5.6 review, 2026-07-11b).** An independent cross-vendor review
  found three overreaches in the prior draft, all fixed here: (i) the historical causal thesis
  ("maintenance *killed* XCON/Freebase; the bottleneck was *fundamental*") is **downgraded to
  "maintenance is a material, explicitly-accountable risk"** — the primary sources show serious
  maintenance problems but do **not** establish maintenance as the demonstrated cause of death, and
  XCON/Freebase were materially mischaracterised (XCON ran successfully in production and DEC built a
  *more* maintainable successor; Freebase was consolidated into Wikidata *because Wikidata succeeded*,
  not on a stated unsustainability finding); (ii) the "cost per checkable record ≥ $219" bracket is
  **mathematically invalid and removed** — an article yielding *n* accepted facts allocates ≈ $219/*n*
  (plus normalization/review/refresh), which can fall either side of $219; the article→accepted-record
  yield is the unmeasured quantity; (iii) the "O(1) external-update = defensible matched advantage"
  claim is **narrowed** — record replacement is only part of update lifecycle cost, the comparison was
  against a *weak* parametric-editing baseline (ROME/MEMIT) not a matched RAG/search/in-context
  baseline, and external-knowledge separation is **not** uniquely neural-symbolic. Two citations were
  also materially misstated (baw115 authorship + conflated crowd experiments; Freebase rationale) and
  are corrected in the sources JSONL.
- **Epistemic discipline:** every empirical claim carries a primary citation (venue + year + URL,
  fetch-state recorded in the sources JSONL's `verification` field); anything I could not verify at
  its primary venue this session is marked **UNVERIFIED**. Load-bearing lines carry
  **[MEASURED | STIPULATED | EXTRAPOLATION]**. In this document **MEASURED** = a published number
  restated strictly inside its source's own envelope (the *authors'* measurement, not ours);
  **EXTRAPOLATION** = a cross-source or cross-domain reading, direction-only, never a premise for a
  verdict; **STIPULATED** = a scoping/design decision made here. Where a primary PDF was
  identifiable at its venue (DOI/anthology-ID unambiguous) but not machine-parseable this session
  (ACM 403s, undecoded PDF binaries), the JSONL records `verified:true` with a `verification` note
  that the **full text was not parsed** and the figure rests on multiply-corroborated secondary
  quotation — I flag those inline as **[venue-verified, full-text-not-parsed]** so no reader mistakes
  them for figures I read off the source page myself. Fetched-and-parsed figures (EcoCyc $219,
  UniProt capture rate) carry no such flag.
- **Governance:** writes only this file + the sources JSONL; no KB ingest/embed/sync, no shared-index
  mutation, no registry or assumption-register mutation, no bd/git operations, no child agents.

---

## 0. Dedup — what already exists (surveyed first, built on, not duplicated)

- **Sibling P3 lit reviews (`docs/next/lit/`):** `SYS.md` (P3-LR-SYS) owns *inference-side* lifecycle
  economics — MLPerf power methodology, Sardana inference-volume sizing, and the KOT-LIFE/1
  amortisation vector at 10³/10⁶/10⁹ queries — and **explicitly cedes store-authoring economics to
  this review** (`SYS.md` §11: "no store authoring economics (P3-LR-STORE)"). `EVAL.md` (P3-LR-EVAL)
  owns sealed-benchmark *production and contamination* (its §4: three verified sealing recipes,
  LiveBench refresh discipline, GSM1k frozen→sealed drops) and hands P3-D-SEAL the δ_sealed and
  producer-independence questions; **this review adds only the store leg** — the cost of authoring and
  keeping *fresh* the temporally-changing facts a sealed release draws on. `RAG.md` (P3-LR-RAG) owns
  the retrieval-*index* cost axis (datastore scaling, deployment-bytes accounting). **No sibling
  prices curated-record authoring, human-review cost, provenance/staleness, or the expert-system/KG
  maintenance-death precedent — that gap is this bead.** [STIPULATED: dedup protocol]
- **Lit-KB (`kb/records/`, 552 records):** a scan over `biblio.title` + `architecture.*` finds the
  retrieval-LM lineage (kNN-LM, REALM, RETRO, Atlas) and KG/graph-RAG entries (KG-RAG, KBLaM,
  graph-RAG survey) already extracted — but these are *consumers* of stores, not studies of store
  *authoring/maintenance economics*. Per the KB honesty boundary (`docs/next/literature-kb.md` §0)
  those records are **recall infrastructure, not evidence**; every load-bearing claim below was
  re-verified at its primary venue today. No KB record covers biocuration cost, Cyc/XCON maintenance
  economics, or the Freebase shutdown. [STIPULATED: dedup protocol]
- **Prior lit reports (`reports/lit-*.md`):** `nsm-and-knowledge-injection.md` touches KEPLER/ERNIE
  (Wikidata-backed embeddings) but as an *injection* mechanism, not a maintenance-cost study; none
  covers store economics. **This is the first dedicated store-authoring/maintenance-economics review
  in the repo.**
- **Internal store-economics evidence this review must stay consistent with** (repo-internal, MEASURED
  within its own envelope):
  - **Mint cost of the *own* store:** the s1-G Haiku definer pipeline mints legal `modelAuthored`
    records at **~$0.078 per legal record** (13 legal / 50 concepts, 31.7% gate-pass), the frozen
    baseline for the key-gated A-F0 experiment [MEASURED: `docs/next/a-f0-mint-economics-spec.md` S1,
    sha-pinned]. This is a *mint* figure only; **review, provenance, and staleness costs are
    unpriced** — exactly the gap the external literature below fills.
  - **The store is currently tiny:** f2b's covered store is **108 concepts**; coverage census m0b
    reads **0.3542** on the friendliest corpus; structured-DB ingestion measured **~49% lemma-touch
    coexisting with 0% checkability** (`docs/next/coverage-growth-ingestion-plan.md` §0)
    [MEASURED, repo-internal]. Any competitive-coverage store is *orders of magnitude* larger than
    what has been priced, so the per-record and per-refresh economics below are the binding scaling
    question, not the current $0.078.
  - **Checkability ≠ vocabulary coverage** (`coverage-growth-ingestion-plan.md` §0): ingestion supplies
    records + sometimes licensing axioms, never the mapper parse — so "cost per *ingested* record"
    understates "cost per *checkable* record." [MEASURED, repo-internal] This is the single most
    important internal correction the ledger must carry.

---

## 1. Cost-per-record for curated knowledge bases — state of the art, and under what accounting

**The one clean, fetched-and-parsed number.** The best-documented per-record curation cost in the
literature is EcoCyc's: **$219 per curated article** over 2011–2016, computed transparently as $2.1M
of curation labour / 9,606 newly cited publications [MEASURED: Karp, *Database* 2016,
doi:10.1093/database/baw110 — full text fetched]. Karp's framing is deliberately *reassuring*: that
$219 is 6–15% of a biomedical open-access publication fee and 0.088% of the NIH R01 that produced the
paper. **The skeptical reading the ledger must adopt:** this is cost *per source article ingested*,
not per queryable fact, and it is charged against a *pre-existing, externally-funded* literature —
the curator reads a paper someone else paid millions to produce and spends $219 distilling it. A
programme that must *generate* the facts (not distil published ones) has no such subsidy.
**The denominator is unresolved, and it does NOT bound below at $219** [correction, 2026-07-11b]: an
article yielding *n* accepted, checkable facts allocates ≈ **$219/*n*** of curation labour per fact,
*plus* per-fact normalization, review, provenance, and refresh lines. Because *n* is typically > 1
(one paper yields many assertions), the per-*fact* build cost can fall **either side** of $219 — the
$219/article figure is neither a lower nor an upper bound on per-checkable-record cost. **The
article→accepted-record yield *n* (and the rejected-candidate attrition around it) is precisely the
unmeasured quantity P3-D-LIFE must measure.** [EXTRAPOLATION removed; this is now stated as an open
measurement, not a direction-only inference]

**The workforce ceiling.** Manually curated biological knowledgebases worldwide are sustained by only
**~100–200 full-time professional biocurators** against **>20M PubMed articles** and **~40,000 GO
terms**; e.g. microRNA curation reached only **~1,400 articles in a decade**
[venue-verified, full-text-not-parsed: Bioinformatics Advances 6(1) vbag028, 2026]. UniProtKB expert
curation **captures only 35–45% of the curatable literature per species (50% for human)**
[MEASURED: UniProt Consortium, *NAR* 47(D1):D506, 2019 — fetched]. The decision-relevant fact: even a
mature, well-funded, decades-old curation operation **captures well below completeness** on the
literature examined, and does so while *prioritising* particular high-value, hard-to-predict data.
Curation throughput is a real, low ceiling — but the UniProt number is a **capture rate under a
prioritisation strategy**, not a proof of an immutable saturation ceiling [correction, 2026-07-11b:
"saturates / fixed corpus / hard human ceiling" softened — the paper reports the rate, not the
permanence].

**Crowdsourcing lowers unit cost and, with redundancy, can reach expert-competitive quality.**
The primary drug-indication crowdsourcing experiment reached **~$1.75 per abstract** (five judgements
each, 8h elapsed) at **~96% precision / ~89% recall** [MEASURED: Good, Nanis, Wu & Su, *Database*
2015, doi:10.1093/database/bav016; restated by Hirschman et al. 2016] — **above** the cited
**expert-curator baseline of ~90% precision / ~70% recall** on that task. A separate gene-mutation
crowd experiment reached **~80% precision / >70% recall for <$1/abstract**
[MEASURED: Hirschman, Fort, Boué, Kyrpides, Islamaj Doğan & Cohen, *Database* 2016,
doi:10.1093/database/baw115 — full text fetched]. And the foundational NLP result: aggregating
**as few as 4** paid non-expert Mechanical-Turk annotations per item reaches expert-level agreement
across five tasks [MEASURED: Snow et al., EMNLP 2008, D08-1027]. **The accounting lesson for
KOT-LIFE/1 [correction, 2026-07-11b — this reverses the prior draft's "crowd is worse" reading]:**
crowd curation *with redundancy* can match or exceed expert quality on some extraction tasks at
~$1–2/abstract — but (a) recall/precision vary by task (the gene-mutation task sat below the
drug-indication task), and (b) redundancy *multiplies* per-item cost (4–5× the single-annotation
price). So the crowd's low unit price is bankable only where the task is crowd-tractable *and* the
redundancy multiplier is paid; whether a checker's load-bearing records fall in that regime is an
open measurement, not a settled quality gap. [MEASURED across sources; the regime question is open]

**The maximalist end — Cyc — is the cautionary anchor.** By 1995 roughly **a person-century** of
hand-encoding had produced **~10⁶ commonsense axioms** [venue-verified, full-text-not-parsed: Lenat,
*CACM* 38(11), 1995, doi:10.1145/219717.219745]. Cumulative-to-2024 figures (~$200M, ~2,000
person-years, ~30M assertions) are **UNVERIFIED** — tertiary encyclopedia aggregation, no primary
financial disclosure located [UNVERIFIED: `cyc-scale-tertiary-2024`]. Even taking only the
venue-verified person-century/10⁶-axiom figure, the per-axiom labour cost is enormous. Whether Cyc
"never demonstrated a matched-cost win" is an **absence-of-evidence reading from this review's small,
non-systematic sweep**, not a result in Lenat 1995 (which supplies effort, not that causal verdict)
— see §4 [correction, 2026-07-11b: downgraded from a stated verdict to a bounded absence-of-evidence].

**Synthesis of §1 for the ledger.** Published per-*source-item* curation cost spans roughly
**~$1–2/abstract (crowd, redundant, task-dependent quality) → $219/article (expert biocuration)**;
Cyc's **~person-year-per-10⁴-axioms** is a *per-axiom* figure, a different denominator that does **not**
belong on the per-article axis [correction, 2026-07-11b: prior draft wrongly called "every figure a
per-source-item cost" — Cyc's is per-axiom]. None of these is a cost **per queryable/checkable fact**
(that requires the unmeasured article→fact yield *n*, §7.1), and none includes the recurring refresh
cost priced in §2. These are **cost categories with order-of-magnitude anchors, not a coherent
per-record range.** [MEASURED where fetched; the cross-denominator span is descriptive, not a bracket]

---

## 2. Provenance, update, and staleness economics — the recurring cost the build figure hides

The §1 numbers are *build-once* costs. The literature's sharper finding is that **the recurring cost
of keeping a store current is first-order, and for the update mechanisms available to a
neural-symbolic system it is either expensive-and-manual or cheap-and-unreliable.**

- **Time-sensitive facts are a demonstrated failure mode for static parametric knowledge — and
  search augmentation helps.** FreshQA (600 QA pairs requiring fast-changing world knowledge) shows
  *all* evaluated LLMs struggle on rapidly-changing questions and produce outdated answers; a
  search-augmented prompting method (FreshPrompt) substantially improves accuracy [MEASURED: Vu et al.,
  Findings of ACL 2024, 2024.findings-acl.813]. **What it does NOT show [correction, 2026-07-11b]:**
  it does not measure a per-fact *refresh rate* or *cost*, does not prove facts "go stale continuously"
  as a rate, and does not establish that a *curated persistent store* (rather than *live search*) is
  the required remedy — indeed its own remedy is live search. So it motivates the
  **temporally-fresh-facts store leg** P3-D-SEAL must design (time-changing facts force *some* refresh
  mechanism with *some* cost) but supplies **neither the cadence nor the cost**, and it leaves open
  whether the remedy should be a maintained store at all versus live retrieval (§7.2, §3-SEAL).
- **Parametric fact-update is not a cheap maintenance channel — but that is a weak baseline, not a
  matched one.** RippleEdits (5K edits) shows prominent *parametric* knowledge-editing methods
  (ROME/MEMIT-class) **fail to propagate** an edit to logically entailed facts while perturbing
  unrelated ones; a simple *in-context* (external-context) baseline scores best [MEASURED: Cohen et al.,
  TACL 2024, doi:10.1162/tacl_a_00644]. Sequential parametric edits at scale induce **gradual then
  catastrophic forgetting** [MEASURED: Findings of ACL 2024, arXiv 2401.07453]. **The narrower,
  defensible reading [correction, 2026-07-11b — the prior "O(1), local, auditable, defensible matched
  advantage" claim overstated on three counts]:**
  1. *Record replacement is not the whole update cost.* Replacing a keyed store record may be
     average-case O(1), but **detecting** the change, **checking** provenance, **finding** dependent
     assertions, **propagating** entailments, **revalidating** consistency, **rebuilding** indices, and
     **rolling back** are not generally O(1) or local — RippleEdits is itself evidence that *entailment
     ripple* is real and non-trivial, and it does not measure symbolic-store lifecycle cost.
  2. *The comparison was to a weak baseline.* ROME/MEMIT parametric editing is a *straw* update
     channel; the matched comparison the GPT-5.6 review requires is against the **strongest neural
     retrieval / search / in-context** system, which gets the *same* separation of mutable knowledge
     from model weights.
  3. *External-knowledge separation is not uniquely neural-symbolic.* Conventional RAG, tool-use, and
     in-context systems already externalise mutable facts; directly-replaceable, inspectable source
     records are a property of *any* externalized-knowledge design, not a KOT-specific win.
  **Decision consequence (narrowed):** externalising knowledge makes individual source records
  **directly replaceable and inspectable** — a genuine design property worth naming — but whether it
  **lowers end-to-end update TCO** is *unproven* and must be measured against matched external-context
  baselines, not asserted from the parametric-editing contrast. [design property MEASURED; the TCO
  advantage is OPEN, not a verdict]
- **Live collaborative KBs carry a standing staleness/quality debt.** Wikidata quality work formalises
  three low-quality indicators — community consensus (removed-and-not-re-added statements), deprecated
  statements, and constraint violations — and treats out-of-date information as a recognised, ongoing
  problem [MEASURED at abstract level: Shenoy et al., *JWS* 2022, arXiv 2107.00156; **exact staleness
  percentages UNVERIFIED — not in the fetched abstract**]. More generally, automatically-built KGs make
  an explicit **completeness-vs-correctness trade-off** requiring a *continuous* refinement stage —
  maintenance is never-finished, not a one-time build [MEASURED: Paulheim, *Semantic Web* 8:489-508,
  2017, doi:10.3233/SW-160218].
- **Provenance is itself a per-record labour cost.** The Freebase→Wikidata migration routed **every
  migrated statement through manual human approval** — by Jan 2016, 100+ users had performed **~90,000
  approval/rejection actions** through the Primary Sources Tool, covering only a **small fraction** of
  the ~14M candidate statements mapped from ~4.6M topics [venue-verified, full-text-not-parsed:
  Pellissier Tanon et al., WWW 2016, doi:10.1145/2872427.2874809]. The slow, per-statement throughput
  is documented; calling provenance verification *the* bottleneck is **this review's inference, not a
  stated paper result**, and the ~90,000 actions are **not a measured labour cost** [correction,
  2026-07-11b]. The defensible ledger consequence stands: "attach + verify provenance" is a **distinct
  labour line** whose per-statement human review does **not** amortise away at migration scale, not
  free metadata.

**Synthesis of §2 for the ledger.** Time-sensitive facts are a demonstrated failure mode requiring
*some* refresh mechanism at *some* cost (cadence and cost both **unmeasured** here); the parametric
editing channel is unreliable at the correctness grade a checker needs; and externalising knowledge
makes source records **directly replaceable and inspectable** — but whether that *lowers update TCO*
is unproven against matched external-context (RAG/search/in-context) baselines and is bankable only
for facts *in* coverage and *addressable* by the mapper (§0). The store side's honest §2 gain is a
**design property (replaceability/inspectability)**, not a demonstrated cost advantage. [design
property MEASURED; TCO advantage OPEN]

---

## 3. Human-review cost models — the shape KOT-LIFE/1 should adopt

Consolidating §1–§2 into a model form P3-D-LIFE can log against:

- **Unit review cost scales with quality target via redundancy — and the crowd/expert gap is
  task-dependent, not universal [correction, 2026-07-11b].** Expert-grade correctness is reachable via
  professional curators (~$219/article-class, capped by a ~100–200-person global workforce
  [Karp 2016; vbag028 2026]) *or* via crowd + redundancy: on drug-indication, ~5 judgements/item at
  ~$1.75/abstract **matched/exceeded** the expert baseline (crowd 96/89 vs expert 90/70)
  [Good et al. 2015; Hirschman et al. 2016]; on gene-mutation the crowd sat lower (~80/>70 at
  <$1/abstract). So there **is** a measured regime where redundant crowd curation reaches
  expert-competitive quality at low unit price — but it is *task-conditional*, and redundancy still
  multiplies unit cost 4–5× [Snow 2008]. Whether a KOT checker's load-bearing records fall in a
  crowd-tractable regime is an **open measurement**, not a settled quality deficit.
- **Capture stays below completeness at mature scale.** Even mature operations capture only ~35–50%
  of the literature they examine [UniProt 2019] — a *capture rate under a prioritisation strategy*, not
  proof of an immutable ceiling [correction, 2026-07-11b] — so a coverage target near completeness is
  expensive and outside the *demonstrated* envelope of manual curation, motivating either AI-assisted
  human-in-the-loop curation (the vbag028 direction) or a *narrowed, defensible* coverage claim
  (consistent with the programme's reachability-wall-on-coverage-wall finding,
  `feasibility-synthesis.md` §0).
- **Review cost is per-record and recurs on refresh.** The build cost (§1) is paid once; the review
  cost recurs every time a fact is refreshed (§2). A model that logs only build cost understates TCO.
- **Provenance verification is a separate labour line** [Freebase→Wikidata, WWW 2016], not free
  metadata.
- **Internal calibration point:** the own-store mint is ~$0.078/legal record [MEASURED: A-F0 spec S1],
  but that is *mint only* — no human review, no provenance verification, no refresh — so it is a
  **lower bound** on true cost-per-maintained-record, and the external literature says the true figure
  is dominated by the review + refresh lines the mint number omits. [EXTRAPOLATION, direction-only]

---

## 4. What maintenance economics did to comparable past systems — capability-limited vs fundamental

The bead asks for a *capability-limited vs fundamental* judgement on comparable systems. **The
prior draft over-read the primary sources into a "maintenance killed these systems, fundamentally"
thesis; the GPT-5.6 review is right that the sources do not support it. Corrected reading: maintenance
is a documented, material, first-order RISK in each case — not a demonstrated cause of death, and
not shown to be fundamental rather than an implementation/representation problem** [correction,
2026-07-11b, applies to all three below].

- **XCON/R1 (DEC, rule-based configurer) — a *successful* production system whose maintenance was a
  large, documented, first-order cost. NOT shown to be killed by maintenance; fundamental-vs-
  implementation UNRESOLVED.** XCON grew to **~6,200 rules** over **~20,000 parts**, with a **large
  annual rule-churn rate** (figures of ~40–50% appear across the literature; the exact value and its
  attribution between Barker & O'Connor and Soloway et al. are **unresolved from the primary texts I
  could parse** — the GPT-5.6 review reports Barker & O'Connor give ~40% and the 50% is in the
  XCON-in-RIME paper) [venue-verified, full-text-not-parsed: Barker & O'Connor, *CACM* 32(3):298-318,
  1989]. Crucially, that paper presents XCON as the **successful cornerstone of a growing production
  family** of Digital expert systems with **satisfactory run-time performance**; maintainability
  became a *research problem*, and DEC's response was to build a **more maintainable successor** (the
  RIME re-implementation), not to abandon the capability [venue-verified: Soloway et al., AAAI-87].
  So XCON is the **closest structural analogue to a KOT store** — a large set of interdependent
  correctness rules over a fast-churning world with real, recurring maintenance cost — and that is why
  it belongs in the ledger; but it is a precedent that **maintenance is a material risk to account
  for**, not evidence that maintenance *kills* such systems or that the cost is *fundamental* rather
  than a representation/tooling problem (RIME was precisely a tooling fix). [precedent = material
  risk; the causal "killed / fundamental" claim is withdrawn]
- **Cyc — a decades-long hand-encoding investment; no matched-cost win is *in evidence here*, but that
  is absence-of-evidence, not a demonstrated failure.** A person-century / ~10⁶ axioms by 1995
  [venue-verified: Lenat, *CACM* 1995]. This review's small, non-systematic sweep located **no**
  benchmark result establishing Cyc beating a learned baseline at matched cost — but Lenat 1995
  supplies *effort*, not that causal verdict, and a null sweep is not proof of no win [correction,
  2026-07-11b: prior "FUNDAMENTAL bottleneck / no matched-cost win exists" downgraded]. The general
  diagnosis — the **knowledge-acquisition bottleneck** (elicitation + hand-encoding cost as the
  binding constraint) — is attributed to Feigenbaum [attributed, primary IJCAI-77 text not fetched:
  `feigenbaum-ka-bottleneck-1977`; the "60% of projects fail / 70–80% of effort on KA" figures are
  **UNVERIFIED folklore**]. The decision-relevant, defensible point: hand-encoding at Cyc scale is
  *demonstrably expensive*, and the modern re-entry (LLM-assisted authoring, the vbag028
  human-in-the-loop direction, our own $0.078 mint) targets exactly that *acquisition* cost — while
  §2 shows the *maintenance* cost is a separate, also-hard half.
- **Freebase — consolidated into Wikidata *because Wikidata succeeded*; NOT a stated economic-
  unsustainability finding.** Google announced on 16 Dec 2014 that Freebase would be wound down and its
  data transferred to Wikidata (read-only 31 Mar 2015, closed 2 May 2016) [venue-verified secondary:
  Search Engine Land 2014]. The migration paper states the rationale plainly: *"Due to the success of
  Wikidata, Google decided in 2014 to offer the content of Freebase to the Wikidata community"*
  [venue-verified: Pellissier Tanon et al., WWW 2016]. **There is no primary source in this sweep
  stating Freebase was "unsustainable" or "not worth its maintenance cost"** — that framing was
  invented in the prior draft and is **withdrawn** [correction, 2026-07-11b]. What Freebase *does*
  contribute is the migration's per-statement manual-review labour (§2): consolidating even a
  well-resourced collaborative KB carried a large, human-in-the-loop provenance cost. That is a
  maintenance-cost data point, not a maintenance-death verdict.

**The cross-cutting reading [corrected 2026-07-11b — was "maintenance, not capability, is the
historical killer"; now a material-risk claim]:** across XCON, Cyc, and Freebase, maintenance and
acquisition economics were **serious, first-order, and explicitly documented** — large annual rule
churn, person-century encoding effort, per-statement migration review. The literature supports
**"store maintenance is a material risk that must be explicitly accounted for,"** *not* "maintenance
is the usual demonstrated cause of failure of this class of system." Two of the three systems were, in
fact, *successful in their covered slice* (XCON ran production for years; Freebase's data was valuable
enough to migrate wholesale), and none of the three is shown by its primary sources to have *died of
maintenance* or to face a *fundamental* rather than implementation-level cost. This is still exactly
why the store leg belongs in the ledger **with a kill condition that forces explicit accounting** —
but the precedent justifies *accounting*, not a presumption of doom (see §6 on K-P3v2(6)).

---

## 5. What "beat matched baselines" here — and under what accounting (the skeptical read)

The bead asks, per sub-question, what beat matched baselines and under what accounting, skeptical of
unmatched-compute/uncosted-curation wins. **For the store/maintenance axis the honest answer is
stark:**

- **No curated-KB system in this sweep is *shown here* to win over a learned baseline at matched
  total lifecycle cost** (absence-of-evidence from a small sweep, not a proof of no win). XCON's
  celebrated "$25M/year savings" figure is (a) secondary/UNVERIFIED at primary here and (b) an
  *operational-savings* claim against manual configuration, never a matched-cost comparison against an
  alternative automated system. Cyc has no such win *in this sweep*. Freebase was consolidated into
  Wikidata (because Wikidata succeeded), neither shown superior nor shown inferior on a benchmark.
  [EXTRAPOLATION, direction-only]
- **The "small store beats big model" retrieval wins (RAG.md) all under-charge the store.** RAG.md
  already established that kNN-LM/RETRO/Atlas/MassiveDS charge *parameters* but not the *index bytes or
  its construction/refresh* — and this review adds the missing line: they also do not charge
  **authoring, human-review, provenance, or staleness-refresh**. A deployment-bytes-*and*-lifecycle-
  inclusive ledger is *stronger accounting than the field's own norm*, and on the store axis it will
  tend to *erase* uncosted-curation wins. [EXTRAPOLATION, direction-only; consistent with RAG.md §1]
- **The one internal end-task positive is store-agnostic on this axis.** f2b-replicate's +0.1507
  (135M+verify-retry vs 1.7B) is **correct-alignment-specific, not store-content-specific** — a
  derangement kills it — and it inherits the NL-boundary FAIL [MEASURED: `feasibility-synthesis.md`
  §2]. It is *not* evidence that curated-store authoring pays; its de-confound (knull) is unrun.
- **The store side's honest §2 property is replaceability/inspectability, NOT a demonstrated cost
  win [correction, 2026-07-11b].** Externalising knowledge makes individual source records **directly
  replaceable and inspectable**, which parametric memory is not — but (a) that property is shared by
  *any* external-knowledge system (RAG, tool-use, in-context), not unique to neural-symbolic; (b) the
  favourable RippleEdits/forgetting contrast is against a *weak parametric-editing baseline*
  (ROME/MEMIT), not the matched RAG/search/in-context baseline the GPT-5.6 review requires; and (c)
  record replacement is not the whole update lifecycle (change-detection, dependency/entailment
  propagation, revalidation, reindex, rollback — §2). So whether externalisation **lowers end-to-end
  update TCO** is **unproven** and must be *measured against matched external-context baselines*, not
  asserted. The ledger should claim the **design property**, flag the **TCO question as open**, and
  claim no matched-accounting advantage yet. [design property MEASURED; TCO advantage OPEN]

**Methods to adopt** (what the literature offers the programme): (i) **transparent per-source-item
cost accounting** exactly as Karp 2016 does it (labour-$ / items over a fixed window) — adopt this
denominator discipline for KOT-LIFE/1's store line, *and extend it to a per-accepted-checkable-fact
denominator* (the article→fact yield, §7.1); (ii) **AI-assisted human-in-the-loop curation**
(vbag028 direction; our $0.078 mint is the mint stage of this) to attack the acquisition cost;
(iii) **redundancy-with-bias-correction** (Snow 2008) as the human-review quality model, priced with
its redundancy multiplier and *task-conditional* quality (some tasks reach expert grade, §1/§3);
(iv) **external-context update over parametric editing** (Cohen 2024) as *a* maintenance mechanism,
benchmarked against a matched neural-retrieval baseline before any TCO advantage is booked;
(v) **explicit refinement/refresh stage** (Paulheim 2017) budgeted as recurring, not one-off;
(vi) **provenance-verification as a distinct labour line** (Freebase→Wikidata).

---

## 6. What this review settles for the lifecycle ledger (KOT-LIFE/1) and the sealed store leg

- **The store line of KOT-LIFE/1 must have three sub-lines, not one:** (a) **build/mint** cost —
  denominated per *accepted, checkable fact*, not per source article; the internal mint anchor is
  $0.078/legal record (mint stage only) and the external expert anchor is $219/*article*, but these
  are **different denominators** and do **not** form a bracket on per-checkable-record cost (§1
  correction; the article→fact yield *n* is unmeasured); (b) **human-review + provenance** cost,
  recurring, priced with a redundancy multiplier and a distinct provenance-verification line;
  (c) **staleness-refresh** cost at a declared cadence for time-changing facts. A single "store cost"
  scalar understates TCO and would let an uncosted-curation win slip through. [STIPULATED, grounded in
  §1–§3]
- **The historical precedent justifies K-P3v2(6) as an explicit-accounting guard, not a doom
  presumption [correction, 2026-07-11b]:** XCON/Cyc/Freebase show store maintenance/acquisition is a
  **material, first-order cost that must be explicitly accounted** — *not* that maintenance is the
  usual demonstrated killer of this class (§4; two of the three were successful in their slice). The
  ledger's kill condition — TCO dominated by a frontier baseline at all three amortisation volumes —
  is the programme's structural guard that *forces* this accounting; the precedent makes the accounting
  load-bearing, and that is the defensible claim. [STIPULATED]
- **The temporally-fresh-facts store leg (P3-D-SEAL) carries a real but unpriced refresh cost:**
  FreshQA shows time-sensitive facts are a demonstrated failure mode for static knowledge and that
  search augmentation helps (§2) — it does **not** measure a per-fact refresh *rate* or *cost*, nor
  prove a *curated store* (vs live search) is the required remedy [correction, 2026-07-11b]. A sealed
  release drawing on time-changing facts forces *some* refresh mechanism at *some* cost; P3-D-SEAL
  cannot treat the fresh-facts leg as free, must co-register cadence and per-fact refresh cost with
  δ_sealed, **and must decide whether the remedy is a maintained store or live retrieval**. [STIPULATED]
- **One store-side design property to claim (and only a property, not a cost win):** externalised
  knowledge makes source records **directly replaceable and inspectable** where parametric memory is
  not — the ledger should log this as a genuine design property, but **must not** book it as a
  matched-cost update advantage until measured against a matched external-context (RAG/search) baseline,
  and it is bounded to in-coverage/mapper-reachable facts. [STIPULATED, from §2/§5]

---

## 7. Open questions Phase-1 must resolve — this is a measurement design, not a closed cost model

**Framing [corrected 2026-07-11b].** This review discovered the store ledger's **cost categories** and
supplied order-of-magnitude anchors and failure precedents; it did **not** produce a cost model. Per
the GPT-5.6 review, P3-D-LIFE still needs to *measure* a **quality-adjusted denominator**, separate
**fixed vs variable** costs, define **record classes**, characterise **author/reviewer time
distributions**, account for **rejected-candidate attrition**, quantify **dependency fan-out** on
update, and price **refresh/reindex/rollback** — each with **uncertainty ranges**. The list below is
the measurement protocol, not a residue of a mostly-finished model.

1. **Cost per *accepted, checkable* record, not per source item** (P3-D-LIFE): the external figures are
   heterogeneous denominators ($219 *per article*, ~$1.75 *per abstract*, person-century *per axiom*);
   the programme needs cost per *mapper-reachable, licensing-axiom-backed, canonical* record. This
   requires measuring the **article→accepted-fact yield *n*** and the **rejected-candidate attrition**
   around it (multi-fact articles, duplicate facts, record-type complexity all enter the denominator).
   The A-F0 mint figure prices only the mint stage. **The single biggest uncertainty in the ledger.**
2. **Fixed vs variable cost split + record classes + author/reviewer time distributions** (P3-D-LIFE):
   a single scalar hides that some cost is one-time infrastructure and some scales per record, that
   record classes differ in cost, and that human time is a *distribution* (with a long tail), not a
   mean. Measure these before any TCO number is quoted.
3. **Refresh cadence + per-fact refresh cost for the fresh-facts leg** (P3-D-SEAL): FreshQA motivates
   *some* refresh but prices none; measure *our* per-fact refresh labour and cadence, and decide
   **store-vs-live-search** as the remedy, before the sealed leg is frozen.
4. **Human-review quality/cost operating point** (P3-D-LIFE): expert (~$219-class, workforce-capped) vs
   crowd+redundancy (task-conditional quality — expert-competitive on drug-indication, lower on
   gene-mutation — at ~$1–2/abstract × redundancy) vs AI-assisted HITL (vbag028; our mint). Which
   operating point clears the checker's correctness grade, at what unit cost, is a normative registered
   choice, not a literature consequence.
5. **Provenance-verification labour line + dependency fan-out** (P3-D-LIFE, P3-D-SEAL co):
   Freebase→Wikidata shows per-statement human review is slow and non-amortising at scale; decide how
   provenance is verified and priced, and **measure the dependency/entailment fan-out** that a keyed
   update triggers (change-detection, propagation, revalidation, reindex, rollback — §2), since these
   determine whether "external update is cheap" survives contact with the lifecycle.
6. **Matched-baseline TCO comparison, not the ROME/MEMIT straw** (P3-D-LIFE): whether externalised
   records lower end-to-end update TCO must be measured against the **strongest neural
   retrieval/search/in-context** baseline, which shares the mutable-knowledge separation — not against
   parametric editing.
7. **Whose cost is charged in the sealed leg** (P3-D-SEAL): decide explicitly whether the priced cost
   is **benchmark-producer truth refresh**, **participant-authored store maintenance**, or **both**.
   Producer-side fresh-fact construction must **not** be charged asymmetrically to the store system
   while a neural/search baseline receives the evaluation evidence or live search for free.
8. **Exact Wikidata/KG staleness rates** (P3-D-SEAL background): UNVERIFIED here (abstract only; the
   Shenoy et al. abstract supports three quality *indicators*, not a staleness *economics*); if a
   staleness constant is wanted as a design anchor, fetch full text or derive from sealed-refresh
   instrumentation.
9. **Is the replaceability/inspectability property bankable at competitive coverage?** (P3-D-LIFE): it
   is real in-coverage, but the coverage/mapper walls (§0, `feasibility-synthesis.md` §0) mean the
   *fraction of real-world facts* to which any cheap-update property applies is itself unmeasured.

---

## 8. Phase-1 hand-off — design beads this review feeds, and what it settled

**Design beads to create (per the §5 table; coordinator to `bd create` — this review does not create
them, per governance):**

- **P3-D-LIFE** (co-blocked on P3-LR-SYS + **P3-LR-STORE**) — KOT-LIFE/1 amortisation model + logging
  hooks. *Category discovery contributed here (not a de-risked model):* the **store line is specified
  as three recurring sub-lines** (build/mint, review+provenance, staleness-refresh) with adopted
  accounting discipline (Karp 2016 denominator; Snow 2008 redundancy model; Paulheim 2017
  recurring-refinement framing); order-of-magnitude anchors are pinned ($0.078/legal record mint-stage
  internal; $219/article expert external — **different denominators, not a bracket**); the historical
  precedent (XCON large annual churn, Cyc person-century, Freebase migration) is supplied to justify
  kill condition K-P3v2(6) as an **explicit-accounting guard**; the store-side **design property**
  (replaceable/inspectable records) is identified and bounded. *Still open (the measurement, §7):* the
  quality-adjusted per-checkable-record denominator (§7.1–7.2), review operating point (§7.4),
  provenance + dependency fan-out (§7.5), the matched-baseline TCO comparison (§7.6), and
  property-fraction at coverage (§7.9). **This is the larger part of the work.**
- **P3-D-SEAL** (store-leg co-input; blocked by P3-LR-EVAL + **P3-LR-STORE** co) — sealed benchmark
  incl. temporally-fresh-facts store leg. *Contributed here:* the fresh-facts leg is shown to carry a
  **real but unpriced refresh cost** (FreshQA motivates refresh but measures no rate/cost), which must
  be co-registered with δ_sealed and a declared cadence; provenance verification is a distinct labour
  line (Freebase→Wikidata). *Still open:* §7.3 (cadence + per-fact refresh cost + store-vs-live-search
  remedy), §7.7 (**whose cost is charged** — producer refresh vs participant maintenance vs both,
  no asymmetric charging), §7.8 (staleness rate anchor). (Contamination/production/δ_sealed remain
  owned by P3-D-SEAL via EVAL.md §4.)
- **Coverage-growth feeder line** (`docs/next/coverage-growth-ingestion-plan.md`, costs logged into
  KOT-LIFE/1) — *Contributed here:* ingestion's "cost per ingested record" is confirmed to
  **understate cost per checkable record** (checkability ≠ vocabulary coverage, §0), and manual
  curation is shown to **capture below completeness** (UniProt 35–50%, a capture rate not a proven
  ceiling), so the feeder's κ_B ambitions must be paired with the mapper/world-layer work the plan
  already flags, and its per-record economics must use the checkable-record denominator (§7.1).

**What this review settled (the defensible decision content):**
1. Crowd curation *with redundancy* can reach **expert-competitive quality on some extraction tasks**
   at ~$1–2/abstract (drug-indication crowd 96/89 vs expert 90/70) but is **task-conditional** and
   pays a 4–5× redundancy multiplier; even mature expert operations capture below completeness on the
   literature examined [MEASURED: Karp 2016, UniProt 2019, Snow 2008, Good et al. 2015, Hirschman et
   al. 2016]. There is **no established universal crowd/expert quality gap** — that prior claim was
   corrected.
2. **Time-sensitive facts are a demonstrated failure mode** for static parametric knowledge (search
   augmentation helps); the parametric-editing channel is unreliable at checker grade; and externalised
   records are **directly replaceable and inspectable** — a genuine **design property**, but **not a
   demonstrated matched-cost update advantage** (unproven vs matched RAG/search baselines) [MEASURED:
   Vu 2024, Cohen 2024, arXiv 2401.07453; corrected 2026-07-11b].
3. **Store maintenance/acquisition is a material, first-order, explicitly-accountable RISK** across the
   closest comparable systems (XCON large churn but successful in production; Cyc expensive
   hand-encoding; Freebase consolidated into Wikidata *because Wikidata succeeded*) — this justifies
   KOT-LIFE/1's kill condition K-P3v2(6) as an accounting guard. It does **not** establish that
   maintenance is the usual demonstrated *cause of death* of this class, nor that the cost is
   *fundamental* rather than implementation-level [corrected 2026-07-11b; two of the three systems were
   successful in their slice].
4. The KOT store's **build cost is priced only at the mint stage** ($0.078/legal record); review,
   provenance, refresh, the per-*checkable*-record conversion, and the whole §7 measurement protocol
   are **unmeasured** and are the store ledger's binding uncertainties. **This deliverable is category
   discovery + measurement design, not a de-risked implementation hand-off** (§7).

---

## 9. Proposed assumptions-register entries (in-doc; not written to the registry — governance)

*Governance forbids this review from mutating `registry/assumptions.jsonl`; these are proposed here for
the coordinator to register. Each replaces or corrects a prior-draft framing per the GPT-5.6 review.*

- **A-STORE-1 (corrected):** "$219/curated article (Karp 2016) is a per-*source-article* cost and does
  **not** bound per-checkable-record cost either above or below; the article→accepted-fact yield *n* is
  unmeasured." (Was: "per-checkable-record cost ≥ $219." **Withdrawn.**)
- **A-STORE-2 (corrected):** "Externalised knowledge gives directly replaceable/inspectable records — a
  design property shared with RAG/search — but a **matched-cost update-TCO advantage is unproven** and
  must be measured against the strongest neural-retrieval baseline, not ROME/MEMIT." (Was: "O(1)
  external update is a real, defensible, matched-accounting advantage." **Narrowed.**)
- **A-STORE-3 (corrected):** "Store maintenance/acquisition is a **material, explicitly-accountable
  risk**; the historical record (XCON, Cyc, Freebase) does **not** establish maintenance as the usual
  cause of death or as fundamental." (Was: "maintenance economics, not capability, is the historical
  killer; FUNDAMENTAL." **Downgraded.**)
- **A-STORE-4 (corrected):** "FreshQA shows time-sensitive facts fail static knowledge and that search
  augmentation helps; it does **not** measure a per-fact refresh rate/cost or establish that a curated
  store (vs live search) is required." (Was: "FreshQA proves facts go stale continuously." **Narrowed.**)
- **A-STORE-5 (new):** "P3-D-SEAL must decide whose cost is charged (producer truth-refresh vs
  participant store-maintenance vs both) and must not asymmetrically charge producer-side fresh-fact
  construction to the store system while a neural/search baseline gets evaluation evidence or live
  search free."

---

*Epistemic register: 18 external sources cited (one added this revision — Good et al. 2015 bav016 — to
de-conflate the drug-indication experiment from the Hirschman et al. 2016 perspectives paper). Two
sources were fetched-and-parsed with exact figures read off the source page (Karp/EcoCyc $219; UniProt
35–50% capture); the Hirschman et al. 2016 crowd/expert figures and the Freebase-migration rationale
were fetched-and-parsed this revision. The remainder are **venue-verified** (DOI/anthology/journal
listing confirmed) — which is **bibliographic** verification, not claim-level verification: several
figures rest on multiply-corroborated secondary quotation of an unparsed primary PDF and are flagged
inline as [venue-verified, full-text-not-parsed]. Two items remain UNVERIFIED at primary (Cyc
cumulative $/person-year totals; Feigenbaum IJCAI-77 primary text + KA-failure-rate folklore).
**Corrections applied this revision (2026-07-11b):** baw115 authorship (Hirschman et al., not Good &
Su) and its conflated crowd/expert figures; the Freebase shutdown rationale (Wikidata's success, not a
stated unsustainability finding); the XCON churn attribution (~40–50%, unresolved) and the withdrawal
of the "killed by maintenance / fundamental" causal verdict; the removal of the invalid $219
per-checkable-record bound; and the narrowing of the O(1)-update and FreshQA claims. Internal MEASURED
anchors (A-F0 mint $0.078, f2b 108-concept store, m0b 0.3542, coverage-growth checkability≠coverage)
are repo-internal, cited by path, and never widened beyond their verdict envelopes.*
