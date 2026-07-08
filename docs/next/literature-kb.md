# N-C — The Literature + Developments Knowledge Base (Pillar C)

**Kernel of Truth programme — next-direction seed, Pillar C.**
Author: Kern (Fable design agent). Date: 2026-07-08.
Status: **DESIGN/PLANNING document.** No GPU spend; no registry entry is amended here.
Binding constraints: `docs/kernel-design-directives.md` (esp. §3 data-tracking-fixed-up-front,
§4 don't-guess-test, §6 honest stats). Companions: `docs/next/arch-survey.md` (N0),
`docs/next/research-engine.md` (N-B — this KB implements N-B's `lit-scan` skill, delta D5,
and feeds its known-results ledger, delta D2).
External facts below tagged **[search]** were web-verified 2026-07-08; untagged
operational facts are from the repo record or the model-pricing reference loaded this session.

**Purpose in one sentence.** A maintained, repo-persisted knowledge base that indexes BOTH
external SOTA literature AND our own developments (verdict objects, design docs, ledger
facts), in two complementary forms — a **vector index** for fast semantic recall and a
**structured index** in the sparq/kernel style for exact, queryable claims — so design
agents stop re-running the literature from scratch and never propose what a ledger null
already bounds.

---

## 0. Why two forms, and the honesty boundary

The two query patterns design agents actually have are different machines:

1. *"What exists on latent-space verification of LM outputs?"* — fuzzy recall over
   everything we have ever ingested. **Vector form.**
2. *"List every trained-bridge injection result at ≥1B params where the injected arm beat
   a text baseline, with effect sizes"* — exact predicates over typed fields. **Structured
   form.** (Note L3 §7's table is precisely this kind of query, hand-built once at great
   cost; the structured index makes it a one-liner, maintained.)

**The honesty boundary (binding).** KB records are **recall infrastructure, not evidence**.
The verified evidence layers remain (a) the adversarially-verified lit reports
(`reports/lit-*.md`, with their [established]/[claimed]/[speculative] tags) and (b) the
registry verdict objects. A KB record carries its extraction provenance (model, prompt
hash, date) and an `epistemics` tag, and no document may cite a KB record as if it were a
verified claim — a paper claim found via the KB must be verified against the source (or
promoted through a lit-report update) before it appears in any prereg, dossier, or paper.
For internal records the rule is mechanical: they are **generated from registry objects,
never hand-written**, and the existing `registry-check --citations` claim-regex machinery
applies to their summary text (a KB summary of a FAIL cannot say "promising").

---

## 1. Form V — the vector / semantic index

### 1.1 Local-embedded vs hosted: recommendation and reasoning

**Recommendation: local-embedded, with the canonical data committed to the repo and any
binary index treated as a deterministically-rebuildable derived artifact.** Hosted vector
services (Qdrant Cloud, Pinecone, Chroma Cloud) are rejected for this programme:

| Criterion | Local-embedded | Hosted service |
|---|---|---|
| Everything-persists rule (box is ephemeral; repo is the system of record) | ✅ index lives in-repo, survives box death, clones with the repo | ❌ state lives on a third party; repo clone is incomplete |
| Determinism / pinning (P2 discipline) | ✅ embedder revision + corpus hash pinned; rebuild is a pure function | ❌ service-side model/version drift, silent reindexing |
| Cost / credentials | ✅ $0, no key | ❌ another credential + recurring cost for a ~10⁴-chunk corpus |
| Scale we actually have | ~10³–10⁴ chunks at bootstrap, ≤10⁵ over the programme's life | overkill |

Within "local-embedded", the three named candidates plus the null option:

- **Null option (recommended default): committed embedding matrix + brute-force cosine.**
  At our scale an ANN index is decoration. Store chunks as canonical JSONL
  (`kb/chunks/*.jsonl`) and embeddings as float16 shards (`kb/embeddings/*.f16.npy`,
  Matryoshka-truncated to 256 dims → 512 B/chunk → **~5 MB at 10k chunks, ~25 MB at 50k**;
  git-lfs only if we ever exceed that). Query = matrix multiply in NumPy; <100 ms at 50k
  chunks even on this box's 2 cores. Zero dependencies beyond NumPy, byte-deterministic,
  diffable ingestion, trivially auditable. This mirrors the encoder's own ethos.
- **LanceDB** — the best of the three if/when we outgrow brute force: genuinely embedded
  (SQLite-like, no server), Lance columnar format with zero-copy versioning and 2026
  git-style branching **[search]**. But its files are opaque binaries in git; keep it as a
  *derived* index built from the committed JSONL+npy by a `make kb-index` step, never as
  the source of truth.
- **Chroma** — embedded mode is fine but SQLite-backed persistence is a mutable binary
  blob in-repo with no versioning story **[search]**; strictly dominated by LanceDB here.
- **Qdrant** — a server (even in embedded/local mode it wants to own its storage dir);
  heaviest ops footprint on a 2-core shared box; rejected.

**Fork KB-F1 (registered, §6)** decides brute-force vs LanceDB by measurement, but the
prior is strongly brute-force-first: adopt LanceDB only when a measured trigger fires.

### 1.2 Embedding source

**Recommendation: a pinned local CPU model — `nomic-embed-text-v2` (137M params,
~274 MB, 8192-token context, Matryoshka dims 768→64) [search]** — run niced on the box,
checkpointed, output shards committed. Rationale:

- **Pinnable.** HF model revision sha recorded in `kb/manifest.json` next to the corpus
  hashes — the P2 pin discipline extended to the KB. A hosted embedding API (OpenAI
  `text-embedding-3`, Voyage, Cohere, Jina) cannot be pinned against deprecation, makes
  re-embedding a paid event, and adds a key; there is also no first-party Anthropic
  embedding model that fits this need. Hosted is listed in §5 as an explicit non-purchase.
- **CPU-viable.** 137M params embeds hundreds of chunks/sec on commodity CPU **[search]**;
  even at 10× slower on this box, a 10k-chunk bootstrap is an overnight niced job, run
  once per embedder version.
- **Matryoshka** lets us commit 256-dim truncations (small in git) while keeping the
  option of 768-dim local scratch indexes for precision work.

Runner-ups, decided by **Fork KB-F3** (§6): `bge-m3` (stronger, 3× heavier — likely too
slow on 2 cores), `qwen3-embedding:0.6b` (strongest sub-1GB **[search]**, same concern),
and **SPECTER2 vectors served by the Semantic Scholar API** (paper-level, scientific-text
specialised, zero local compute — attractive as a *paper-level* complement, but external,
non-pinnable, and abstract-level only; usable as a free extra signal, not the backbone).

Embedding-model version bump = KB version change: full re-embed, new manifest hash,
recorded in the KB changelog — never a silent swap (the X0-goldens convention).

### 1.3 What gets chunked into the vector index

| Source | Unit | Notes |
|---|---|---|
| External papers | title+abstract always; full-text sections for the **read tier** (papers with structured records, §2) | arXiv LaTeX/HTML preferred over PDF-extracted text |
| Our lit reports (`reports/lit-*.md` etc.) | section-level chunks | the highest-value content in the whole KB — verified synthesis |
| Design docs (`docs/**`), notes, prospectus | section-level chunks | so agents find prior internal reasoning, not just papers |
| Verdict objects + auto-reports (`registry/verdicts/`, `reports/auto/`) | one chunk per verdict: rendered one-paragraph summary (generated, §3.3) | tagged `kind:internal-verdict` |
| Ledger facts (N-B's `registry/ledger.jsonl`, once built) | one chunk per fact | tagged `kind:ledger` |
| Grey literature (Anthropic transformer-circuits posts, GDM mech-interp updates, HF blog) | page-level chunks from a watchlist | several load-bearing L3 sources were blog posts, not papers — the GDM SAE deprioritisation lived on Medium |

Every chunk carries `{source_id, kind, sha256(source bytes), span}` so a hit always
resolves to an exact, hash-pinned location.

---

## 2. Form S — the structured index (papers as kernel-style records)

### 2.1 The idea, mirrored from how the kernel is built

The kernel turns concepts into canonical, validated, content-hashed structured objects;
the KB does the same to papers. One JSON record per read paper at
`kb/records/<id>.json` (id = arXiv id or DOI-slug), canonical JSON (sorted keys,
newline-terminated), validated against `kb/schema/kot-lit-1.json`, content-hashed,
fail-closed on schema violation — the same conventions as `registry/`.

### 2.2 Record schema `kot-lit/1` (normative field list, prose rendering)

```jsonc
{
  "schema_version": "kot-lit/1",
  "id": "arxiv:2410.10450",                  // canonical id: arxiv > doi > url-slug
  "identity": {
    "doi": "…|null", "arxiv": "2410.10450", "openalex": "W…", "s2": "…",
    "pdf_sha256": "…|null"                    // pinned bytes actually read
  },
  "biblio": { "title": "…", "authors": ["…"], "year": 2025, "venue": "ICLR 2025",
              "citation_count": {"value": 312, "as_of": "2026-07-08", "source": "s2"} },
  "architecture": {                            // what the system IS
    "summary": "one paragraph, mechanism-level",
    "seam_cell": "trained-bridge",             // closed enum from N0 §1.4 / L3 §3's
                                               // interface-locality law: text |
                                               // own-activations | trained-bridge |
                                               // external-engine | raw-foreign-coords |
                                               // none (theory/survey)
    "trained_components": ["projector"],       // what learns; [] if training-free
    "frozen_components": ["host LLM", "KB encoder"],
    "mechanism_tags": ["kv-injection", "retrieval", "adapter", "sae", "vsa",
                       "verifier-loop", "concept-io", "…"]   // open vocabulary, linted
  },
  "claims": [                                  // the load-bearing part
    {
      "claim_id": "c1",
      "type": "quantitative",                  // quantitative | qualitative | negative | theoretical
      "statement": "verbatim-or-near claim text",
      "metric": "accuracy", "value": 0.62, "unit": "fraction",
      "baseline": {"name": "text-in-context", "value": 0.85},   // null if none — flag it
      "dataset": "NQ-open",
      "scale": {"params": 7e9, "rungs_measured": 1},
      "compute_reported": false,               // did they report the §2-directive vector?
      "evidence": "claimed"                    // established | claimed | speculative —
                                               // start at "claimed"; only a lit-report
                                               // verification pass may upgrade
    }
  ],
  "relation_to_kernel": {                      // built AFTER extraction, by a Fable pass
    "hypotheses": [{"id": "HE1", "direction": "supports|contradicts|bounds|informs"}],
    "ledger_refs": ["…"],                      // ledger facts this paper touches
    "seams": ["A2", "F2-verifier", "A6"],
    "note": "one paragraph: why this matters to us, or 'peripheral'"
  },
  "reproduction": { "code_url": "…|null", "weights_url": "…|null" },  // PWC is dead; capture here
  "provenance": {                              // extraction is pinned like everything else
    "extractor_model": "claude-haiku-4-5",
    "prompt_sha256": "…", "extracted_at": "…",
    "source_scope": "fulltext|abstract-only",
    "audit": {"state": "UNAUDITED|SPOT-CONFIRMED|SPOT-REFUTED", "by": null}
  },
  "record_sha256": "…"                         // over canonical bytes minus this field
}
```

Schema hard constraints (a `kb-check` lint, same style as `registry-check`): closed enums
enforced; every `quantitative` claim needs `metric`+`value`+`dataset`; `baseline: null`
is legal but sets a `no_baseline` flag the query layer surfaces (Law-2 discipline: a
number without a baseline is a decoration); `evidence` can only be upgraded by a commit
that also cites a lit-report anchor.

### 2.3 The Haiku extraction pipeline (mirroring bulk kernel-building)

Structured records are built by **Haiku agents** (`claude-haiku-4-5`, $1/$5 per MTok) the
way the Bulk/Registrar role drafts volume kernel content in N-B: mechanical, high-volume,
never self-certifying.

1. **Triage (free/cheap).** Discovery (§4) yields candidates; a Haiku pass over
   title+abstract scores kernel-relevance 0–3 against a fixed rubric (the seam-cell
   taxonomy + programme keywords). Score ≥2 enters the **read tier**.
2. **Extraction.** For read-tier papers, fetch full text (arXiv LaTeX/HTML preferred);
   one Haiku call per paper with the pinned extraction prompt, using **structured outputs**
   (`output_config.format` json_schema mirroring `kot-lit/1`'s extractable subset) so the
   record is schema-valid by construction. Run through the **Batch API** (50% price).
   Cost: ~15k tokens in + ~2k out ≈ $0.02/paper list-price → **~$0.01/paper batched;
   a 500-paper bootstrap ≈ $5–8; ongoing ~30 papers/month ≈ well under $1/month.**
3. **Relation pass.** A Fable agent (not Haiku) fills `relation_to_kernel` for records
   touching live hypotheses — this is judgement, kept at design-agent grade, and cheap
   because it reads the record, not the paper.
4. **Validation + commit.** `kb-check` validates, canonicalises, hashes; commit.
5. **Spot-audit (honesty).** Codex/GPT-5.5 re-extracts a random 5% (min 5) of each
   batch's records from source and diffs field-level; disagreements on `claims[]` fields
   fail the batch back to re-extraction. This extends the run≠audit discipline to KB
   construction — a silently wrong extracted effect size is exactly the kind of quiet
   steering the honesty system exists to prevent.

### 2.4 Internal developments in the same structured space

A generator (`kb-sync-internal`, run in CI) maps registry objects into sibling records
`kb/records/internal/<exp-id>.json` (`schema kot-lit-internal/1`): experiment id, verdict,
kill text verbatim, coverage, scale license, endpoint values, links to the verdict object
by path+sha256. **Generated only — hand-editing fails `kb-check`** (the file must equal
the generator's output byte-for-byte). Design docs get lightweight stub records (id,
title, one-line abstract, tags) so structured queries can return "we already designed
this" alongside "someone already published this". N-B ledger facts (once D2 lands) sync
the same way. Result: one query surface where `filter --seam trained-bridge` returns
KBLaM, GraphToken, **and our own E5/A2 verdict**, in comparable shape.

---

## 3. Query interface (what a Fable design agent actually types)

One stdlib-plus-NumPy CLI at `tools/kb/kb` (Python, same conventions as
`tools/registry/`), exposed to agents via a thin `lit-scan`-adjacent skill doc. No MCP
server, no daemon — agents already live in a shell.

```
kb search "latent verification of LM outputs" [--k 12] [--kind papers|internal|all]
      # vector recall; returns chunk hits with source ids, kinds, epistemics tags
kb get arxiv:2410.10450 [--field claims]
      # pretty-print a record or field
kb filter --seam trained-bridge --claim.metric accuracy --claim.scale.params ">=1e9" \
          --evidence claimed,established [--json]
      # structured predicates over records (flat dotted-path grammar, deliberately
      # weaker than jq — same philosophy as the P2 verdict grammar: too weak to hide
      # judgement in). Internal records match the same predicates.
kb related arxiv:2410.10450 [--depth 1] [--direction citing|cited]
      # citation neighbourhood via the S2 Graph API (cached in kb/graph/)
kb novelty "canonical concept vectors injected through a trained adapter"
      # the step-2 killer: vector search over papers+ledger+verdicts, then a rendered
      # answer sheet: nearest prior art, any ledger null it collides with, any
      # internal verdict that already bounds it. This is N-B §1.3 step 2 mechanised.
kb watch --list | --add "query or arxiv-category"    # manage discovery watchlists
kb status      # corpus counts, pin hashes, staleness lints, last-ingest date
```

Two integration points with N-B: `kb novelty` output *is* the draft `prior-art.md` for a
candidate (delta D5), and every `kb filter`/`search` result footer prints the KB's
epistemics reminder (records ≠ verified evidence) so it lands in agent context every time.

---

## 4. Ingestion pipeline and discovery sources

### 4.1 Discovery (which APIs, in priority order)

| Source | Role | Key? | Notes |
|---|---|---|---|
| **OpenAlex** | primary discovery + metadata + citation counts (250M works) | **Free; API key becomes mandatory ~mid-Mar 2026** (polite-pool/mailto retired) **[search]** | 100k req/day free tier — orders of magnitude above need; register key now |
| **arXiv API + LaTeX/HTML source** | full text for extraction; category sweeps (cs.CL, cs.LG, cs.AI, cs.NE) | none (courtesy: 1 req/3 s) | full-text source is what makes Haiku extraction good; bulk via GCS requester-pays if ever needed |
| **Semantic Scholar Graph API** | citation graph (`kb related`), TLDRs, SPECTER2 paper embeddings, influential-citation counts, recommendations endpoint | **Free key, ~1 RPS** (request via form; higher on review) **[search]** | the citation-expansion engine for watchlists |
| **Crossref** | DOI resolution + non-arXiv venue metadata | none (mailto polite pool); Crossref Plus not needed | secondary |
| **Papers With Code** | ~~leaderboards/code links~~ **sunset July 2025**; domain redirects to HF **[search]** | — | historical dump archived at `paperswithcode/paperswithcode-data` (one-time grab for legacy code links); do not build on it |
| **Hugging Face Papers / Hub API** | PWC's successor for trending + paper↔code/model links **[search]** | Free token (optional but useful) | daily/weekly trending is a good freshness signal |
| **OpenReview API** | reviews + decisions for ICLR/NeurIPS submissions | none | reviewer critiques are cheap adversarial signal on [claimed] results |
| **Grey-literature watchlist** | transformer-circuits.pub, GDM safety Medium, HF/Nomic/LanceDB blogs, alignment forum | none (WebFetch/RSS) | curated URL list in `kb/sources.json`; page snapshots hashed into the corpus |

### 4.2 Pipeline stages (all runnable on this box, niced, checkpointed)

```
discover  → watchlist queries (OpenAlex + arXiv categories + HF trending)
            + citation expansion (S2: refs/citations of every read-tier paper, 1 hop)
            + manual adds (any agent/maintainer can `kb watch --add`)
dedupe    → canonical id (arxiv > doi); alias table for versions (v1/v2) and preprint↔venue
fetch     → metadata (OpenAlex/S2/Crossref) + full text (arXiv source; PDF fallback)
            → bytes hashed into kb/cache/ (gitignored) with hashes committed in manifests
triage    → Haiku relevance rubric (§2.3.1) → read tier / abstract tier / skip
extract   → Haiku batch → kot-lit/1 records (§2.3.2) → Fable relation pass → kb-check → commit
chunk+embed → §1.3 chunking; pinned nomic-embed-text-v2; f16 shards committed
index     → derived (brute-force needs none; LanceDB build only if KB-F1 flips)
audit     → Codex 5% re-extraction spot-audit per batch
```

Bootstrap corpus (week 1): the ~200 works already cited across the five lit reports +
the reports/design docs themselves + all existing verdict objects. That alone makes
`kb novelty` useful; watchlists grow it from there.

### 4.3 Maintenance cadence (how it stays current)

- **Weekly ingest run** (cron or the N-B weekly-heartbeat session): watchlist sweep,
  citation expansion of anything new in the read tier, triage, extraction batch, commit.
  Wall-clock ≈ one niced overnight job; spend ≈ pennies.
- **Event-driven internal sync**: `kb-sync-internal` runs whenever a verdict object or
  ledger line lands (hook into the N-B assessment step / session-close `registry-check`),
  so agents never see the KB lag our own results.
- **Generation-boundary refresh** (N-B §2.5): before each generation's backlog re-scoring,
  a deeper pass — re-pull citation counts, sweep for new nulls/replications touching live
  hypotheses, and file a one-screen "literature delta" into the generation dossier.
- **Staleness lints in `kb status`** (CI-advisory): every CLOSED experiment has an
  internal record; last ingest ≤ 10 days; no read-tier paper UNAUDITED for > 2 batches;
  embedder pin matches manifest.
- **Quarterly**: re-evaluate the embedding-model fork evidence; prune dead watchlists.

### 4.4 Repo layout

```
kb/
  schema/kot-lit-1.json, kot-lit-internal-1.json
  sources.json            # watchlists: queries, arXiv categories, grey-lit URLs
  manifest.json           # pins: embedder HF revision, prompt sha256s, corpus shard hashes
  records/<id>.json       # structured paper records (canonical JSON, hashed)
  records/internal/…      # generated from registry objects — never hand-edited
  chunks/*.jsonl          # chunk text + source pointers (committed)
  embeddings/*.f16.npy    # 256-dim f16 shards (committed; git-lfs if >50 MB total)
  graph/…                 # cached S2 citation edges
  eval/                   # KB-F3 retrieval eval set + results
  cache/                  # fetched PDFs/HTML — gitignored; hashes ARE committed
tools/kb/                 # kb CLI, kb-check, kb-sync-internal, ingest scripts
```

---

## 5. API keys / services shopping list (for the maintainer)

Things to obtain, in order of value. Total recurring cost of the recommended set: **$0**
beyond existing Anthropic spend.

| # | Service | Cost | Action | Why it helps |
|---|---|---|---|---|
| 1 | **OpenAlex API key** | **Free** | Register at openalex.org (keys mandatory from ~mid-Mar 2026 **[search]**) | Primary discovery/metadata backbone; 100k req/day |
| 2 | **Semantic Scholar API key** | **Free** (form; introductory 1 RPS) **[search]** | Request at semanticscholar.org/product/api | Citation graph (`kb related`, watchlist expansion), TLDRs, SPECTER2 embeddings, influential-citation signal |
| 3 | **Anthropic API** (already held) | Existing; Haiku 4.5 $1/$5 per MTok, **Batch API −50%** | Nothing new; budget ~$10 bootstrap + <$5/month | Haiku extraction agents; structured outputs make records schema-valid by construction |
| 4 | **Hugging Face account/token** | **Free** | Create token (read) | PWC successor (trending papers, paper↔code/model links) **[search]**; also the pinned embedder download |
| 5 | Crossref | Free, no key (mailto etiquette) | none | DOI/venue metadata fallback |
| 6 | OpenReview | Free | none | Reviews/decisions as adversarial signal on [claimed] results |
| — | **Not recommended:** hosted embeddings (Voyage/OpenAI/Cohere/Jina) | ~$0.02–0.13/M tok + key | skip | Unpinnable against deprecation; re-embedding becomes a paid event; local 137M model is sufficient at our scale |
| — | **Not recommended:** Scopus / Web of Science / Dimensions | Paid, institutional | skip | Nothing they add over OpenAlex+S2 for CS/ML |
| — | **Optional, defer:** Exa / Tavily web-search API | Paid | only if grey-lit discovery via manual watchlist proves too lossy (KB-F5 territory) | Semantic web search for blog-borne results |
| — | **Optional, defer:** git-lfs on the repo | Free (GitHub quota) | only if committed embeddings exceed ~50 MB | Keeps clone weight sane at 10⁵ chunks |

---

## 6. Forks (registered per directives §4 — options, why-uncertain, deciding test, kill)

- **KB-F1 — Vector backend: committed brute-force matrix vs LanceDB derived index.**
  *Why uncertain:* brute force is obviously right at 10⁴ chunks; unclear where it stops
  being right on a 2-core box. *Deciding measurement:* p95 `kb search` latency and
  recall@10 parity, measured in `kb status` as the corpus grows. *Kill (for brute-force):*
  p95 > 5 s or corpus > 5×10⁴ chunks → build the LanceDB derived index (source of truth
  unchanged). *Kill (for LanceDB):* if adopted, index rebuild must stay byte-reproducible
  from committed data or it reverts to scratch-only.
- **KB-F2 — Extractor model: Haiku 4.5 alone vs Haiku+Sonnet split.**
  *Why uncertain:* quantitative-claim fields (metric/value/baseline/scale) are exactly
  where a cheap model may misread tables. *Deciding experiment:* 30-paper gold set
  extracted by a Fable agent; field-level agreement scored mechanically. *Kill (Haiku-only):*
  <90% agreement on `claims[]` numeric fields → route `claims[]` extraction to
  `claude-sonnet-5` (still batched), keep Haiku for the rest; re-measure.
- **KB-F3 — Embedding model: nomic-embed-text-v2 vs bge-m3 vs qwen3-embedding-0.6b
  (+SPECTER2-via-S2 as a free paper-level side channel).**
  *Why uncertain:* generic MTEB rankings **[search]** may not transfer to our
  mechanism-dense ML prose. *Deciding experiment:* a small fixed retrieval eval built
  from the lit reports (query = section question, relevant set = papers that section
  cites); nDCG@10 per candidate, runtime measured on this box. *Kill:* any candidate
  >5% nDCG behind the best, or >4 h to embed 10k chunks niced, is out. Pre-commitment:
  whatever wins is pinned; changes only by re-running this eval.
- **KB-F4 — Structured query surface: dotted-path `kb filter` vs a generated SQLite
  mirror (`kb.sqlite`, derived, gitignored).**
  *Why uncertain:* agents may want joins (papers × hypotheses × verdicts) that a flat
  filter grammar makes painful. *Deciding measurement:* friction log over the first
  month of design-agent use (N-B retro input). *Kill (flat grammar):* if >25% of logged
  structured queries fall back to ad-hoc `jq`/python over the records, ship the SQLite
  mirror as a derived artifact.
- **KB-F5 — Grey-literature discovery: curated watchlist vs paid semantic search API.**
  *Why uncertain:* blog-borne results (GDM-update-class) are load-bearing but sparse.
  *Deciding measurement:* at each generation boundary, count blog-borne facts that
  reached the KB late (>30 days after publication) or via luck. *Kill (watchlist):*
  ≥2 such misses in a generation that would have changed a design decision → trial Exa.

---

## 7. Build plan and cost

| Step | What | Effort |
|---|---|---|
| B1 | `kb/` layout, `kot-lit/1` schema, `kb-check`, canonical-JSON/hash utils (borrow from `tools/registry/`) | ~0.5 agent-day |
| B2 | Ingest scripts (OpenAlex/arXiv/S2/Crossref clients, dedupe, cache) + `kb watch` | ~1 agent-day |
| B3 | Haiku triage+extraction batch pipeline + Codex spot-audit hook | ~1 agent-day |
| B4 | Embedder run + committed shards + `kb search`/`get`/`filter`/`novelty` CLI | ~1 agent-day |
| B5 | `kb-sync-internal` + staleness lints + weekly-run wiring | ~0.5 agent-day |
| B6 | KB-F2/KB-F3 mini-evals (gold set, retrieval eval) | ~0.5 agent-day |

Total ≈ **4–4.5 agent-days; ~$10–20 one-off Haiku spend (batched); ~$0 recurring** beyond
pennies/month of Haiku. R0-tier; no prereg needed (infrastructure, not an experiment),
but every pin/audit discipline above applies from day one. Natural acceptance test:
`kb novelty` on the three N0 §4 candidate forks must surface the L1–L3 prior art and the
relevant registry verdicts that we already know are the right answers.

## 8. Open decisions for the maintainer

1. Obtain keys #1, #2, #4 from §5 (all free; OpenAlex has a ~March-2026 deadline already
   passed for keyless access — register regardless of pool grandfathering).
2. Ack the **$10–20 bootstrap + <$5/month** Haiku envelope for extraction.
3. Ack committed-embeddings repo weight (~5–25 MB now; git-lfs decision deferred to the
   >50 MB trigger).
4. Confirm the honesty boundary in §0 (KB ≠ evidence; internal records generated-only;
   Codex spot-audit on extraction batches) as binding policy, so `kb-check` can enforce
   it from the first commit.
