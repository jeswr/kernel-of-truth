# Programme 2 — the self-maintaining neurosymbolic research engine (overview & bootstrap)

**Kernel of Truth programme — next-direction synthesis, node 00 (integrates N0
`arch-survey.md`, N1-A `architecture-ladder.md`, N-B `research-engine.md`, N-C
`literature-kb.md`).**
Author: Kern (Fable design/synthesis agent). Date: 2026-07-08.
Status: **DESIGN/PLANNING document. Nothing here is pre-registered; nothing here spends
GPU money; no registry entry is amended.** Everything proposed becomes real only through
the existing rails (`prereg-freeze` for anything that runs; maintainer sign-off for
anything touching the honesty machinery). Binding constraints:
`docs/kernel-design-directives.md` (§1 no-semantic-web-legacy, §2 two value theses,
§3 operationalisable method, §4 don't-guess-test, §6 honest stats, §7 write-up
first-class, §8 cross-vendor auditor). Nothing in this document competes with or delays
the currently-running F2 pivot.

---

## 0. The vision, in plain language

The kernel gives concepts **canonical, deterministic, training-free vectors** built from
a closed basis of ~65 semantic primes: symbolic relationships, vectorised. Programme 1
asked *whether that object is useful to a language model at all*, and built an unusually
strict honesty system (pre-registration, frozen kill criteria, append-only logs,
cross-vendor audit) to keep itself from lying about the answer.

Programme 2 is the generalisation. Instead of one architecture question run through
bespoke planning, we build a **self-maintaining research engine for neurosymbolic
architectures**: a fixed, repeatable loop that

1. takes candidate architectures in which the kernel is **increasingly central to
   inference** — from normalising what enters the model, through living inside the
   model's layers, to *replacing* neural computation with deterministic symbolic
   computation for the content the kernel covers;
2. tests each candidate for **both value theses at once — correctness AND efficiency**
   (accuracy, parameters, memory, inference and training compute, authoring cost;
   Pareto reporting, never a single flattering number; directives §2);
3. turns every verdict — pass, fail, or null — **mechanically into the next prioritised
   questions**, so the programme never again needs an eleven-document planning build to
   ask what to do next; and
4. keeps itself honest and current with a maintained knowledge base of both the external
   literature and our own results, so no agent re-runs a literature search from scratch
   or proposes something our own ledger already killed.

The honest one-line status underneath the ambition (N0 §1.3): the kernel today has one
supported in-network injection cell (A2/E5, one model rung, content-transfer only), one
deployable external verifier seam under active paid test (F2, running now), two audited
Tier-0 passes (coverage m0b; store-bytes f1 at 6.7×), **and zero demonstrated end-task
wins over the kernel-as-text null**. Programme 2 is designed so that whichever way F2
lands, the next question is already queued, costed, and pre-registerable.

---

## 1. The three pillars and how they fit

**Pillar A is the fuel. Pillar B is the engine. Pillar C is the fuel supply.**

```
   C  literature-KB (N-C)            A  architecture ladder (N0 + N1-A)
   ─ external SOTA + our own          ─ candidate architectures, L0→L3,
     verdicts, indexed twice            each a pre-registerable experiment
     (vector recall + structured        with kill criteria and cost tier
     queries); kb novelty = the
     prior-art step, mechanised                │  candidates
              │ feeds                          ▼
              └────────────►  B  research engine (N-B)
                              ─ candidate template → prereg-freeze → run →
                                verdict → ASSESSMENT → backlog re-score →
                                next generation; cross-vendor audit;
                                known-results ledger; generations as clock
```

- **Pillar A — the architecture ladder (what to test).** N0 surveys the mechanism space
  (neurosymbolic engines, in-network injection/memory, concept-level I/O and
  normalisation, rules-engine inference) and N1-A arranges the kernel-relevant rungs
  into a centrality ladder: L0 (current seams: F2 verifier + A2 adapter) → L1
  (tokenisation/normalisation at the model's boundary) → L2 (kernel-labelled or
  kernel-addressed layers *inside* the network) → L3 (a deterministic rules engine that
  *answers* covered queries itself, with the LLM reserved for everything else). Each
  rung is phrased as a falsifiable hypothesis with pre-declared kill criteria and two
  mandatory nulls (text-only, and the kernel's own content rendered as text at matched
  budget — Law 2). The ladder is climbed or cut by evidence, not preference.
  **Cross-cutting the L1b/L2a/L2b rungs is the maintainer-mandated semantic-fixedness
  sweep (L2c, N1-A §4.3):** the LCM scaling penalty the programme keeps citing was
  measured at one confounded corner (a sentence-level, reconstruction-shaped,
  comprehensively-fixed space — the kernel is definitional, content-addressed, and
  explicitly partial), so L2c de-confounds it by sweeping the fraction φ of the
  representation pinned to kernel vectors (φ ∈ {0…1}, including the mandatory φ=1
  everything-fixed LCM-analog), crossed with model scale and in-kernel vs
  out-of-kernel domains. Its deliverable is a dose–response surface over
  (φ × scale × domain) with the full metric vector V — reframing the efficiency
  thesis as "find the optimal fixed fraction φ\*" — and its φ=1 in-domain cell
  doubles as the hard-scoping/confinement measurement.
- **Pillar B — the research engine (how to test it).** N-B generalises the honesty
  machinery Programme 1 already built and exercised (registry schemas, prereg-freeze,
  pure-function verdicts, run≠audit with Codex/GPT-5.5 cross-vendor audit, the 14
  guardrails) from "this plan's rules" into "the engine's physics". The unit of work is
  a **candidate** (one architecture with one falsifiable value claim); the procedure is
  a fixed template (claim → prior-art → hypotheses → decisive experiment → forks →
  skeptic attack → freeze); the loop closes with a mandatory post-verdict **assessment
  record** that emits scored backlog stubs, and an outer clock of **generations**
  (batches of candidates frozen, run, and closed together, each ending in a maintainer
  dossier). Five small build deltas (~3–3.5 agent-days, $0 compute) make this
  mechanical; nothing else is missing.
- **Pillar C — the literature + developments KB (what is already known).** N-C keeps the
  engine from starving or repeating itself: a repo-persisted, hash-pinned knowledge base
  indexing external papers AND our own verdicts/designs, in two forms — a local vector
  index (committed embeddings, brute-force search; no hosted service, no new recurring
  cost) and structured per-paper records extracted by batched Haiku agents with
  cross-vendor spot-audit. Its `kb novelty` query mechanises the engine's prior-art step
  (N-B delta D5), and its internal sync means a design agent sees KBLaM, GraphToken,
  *and our own E5 verdict* in one comparable query surface. Binding honesty boundary:
  **KB records are recall infrastructure, not evidence** — claims must be verified at
  source before they enter any prereg or paper.

The coupling is deliberate: A without B is a wishlist; B without A idles; A+B without C
re-runs the literature every generation and eventually re-proposes something already
killed. Together they form a loop that consumes architecture candidates and produces
audited verdicts plus the next generation's slate — with the maintainer holding the same
seven gate classes as today (budget, freezes, credentials, spend, external exposure).

---

## 2. Bootstrap — the first turn of the crank

Three tracks, deliberately independent, all startable now without touching F2.

### 2.1 First architecture rung to test: **L3a — the rules-engine oracle** (with L1a queued second)

**What it is (N1-A §5.1).** Implement `kot-axiom/1` v0 as a working engine: a closed
query grammar over the axiom sidecar's native constraint inventory (lookup, inverse,
functional-unique, count, disjointness — no recursion, no chaining) plus a seeded
world-layer fact store and the existing deterministic phrase→concept mapper as the
parser. Then measure, on a covered factual-query slice (N≥500 NL questions with held-out
phrasings): can the engine answer exactly, with provenance, and **refuse correctly when
no record exists** — at orders-of-magnitude lower cost than the smallest LLM that
matches it? Worked example: *"who gave birth to Elvis?"* → mapper detects
{mother, Elvis} → the functional-relation axiom licenses a unique-answer index lookup →
`Gladys Presley`, in microseconds on a CPU, with no hallucination surface. Arms include
engine-with-gold-parse (isolates parse loss), text-only LLMs at R1–R3, and LLM+RAG over
the same facts rendered as text (the Law-2 null).

**Why this rung first — cheapest-decisive + highest-insight:**

1. **Cheapest.** Tier 0–1, ~$0–20: the engine and eval are local-CPU; only the LLM
   comparison arms ride the already-built Modal harness. No model training, no new
   infrastructure, no dependence on the F2 verdict. It fits inside existing tier caps.
2. **Decisive.** It tests the L3 premise directly — *can the kernel compute answers at
   all on its covered slice, and at what cost ratio?* — and a kill at this rung is a
   clean, publishable negative that indicts a named stage (engine, store, or parser)
   without blocking L1/L2.
3. **Highest insight per dollar.** The build IS the `kot-axiom/1` implementation the
   constraint layer owes anyway (design-constraint-layer.md §3.3's validator + an
   index), so even a kill leaves the programme with its axiom engine built and its
   fact-coverage instrument measured. It also converts HC2's "a gloss file cannot count
   parents" from a verifier claim into a generator claim — the strongest native-axiom
   demonstration available at any price.
4. **It is the efficiency thesis (directives §2B) in its most direct form** — answers at
   microjoules instead of GPU-seconds — and it composes with, rather than competes
   against, F2: the engine that answers covered queries and the engine that checks LLM
   output on covered content are the same artefact in two seats.

**Why not the tokenisation/normalisation rung first.** L1a (the kernel input
canonicaliser, N0 fork N-C3) is the other candidate and remains **queued second**, at
Tier 1–2 (~$20–60): the mapper already exists and is signed, the 2025–26 brittleness
literature freshly motivates it, and it de-risks exactly the parse stage L3a depends on.
It is second rather than first only because it needs paid model inference for every arm
while L3a's core question is answerable mostly on CPU — and because L3a additionally
discharges an existing design debt. If the maintainer prefers to start with the
model-facing rung, nothing breaks: the two rungs share the mapper and are otherwise
independent. Honest fork framing (directives §4): the *ordering* is a design opinion,
not a verdict; both rungs carry frozen kill criteria before anything runs, and the L3a
kills are pre-shaped in N1-A §5.1 (gold-parse accuracy below the pre-declared fraction ⇒
engine/store inadequate; mapper-parse losing too much of gold-parse ⇒ the NL boundary
eats the rung, wait for a better parser, not more GPU; LLM+RAG at R1 matching engine
accuracy at comparable cost ⇒ the differentiator failed).

**What must happen before it runs:** candidate record per the N-B template (claim,
`kb novelty` prior-art once the KB bootstraps — or a manual lit-scan if run before C
lands), hypotheses block, DRAFT `kot-reg` record with full SAP and the FK-L3-1/-2/-3
forks (router identity, world-layer population route, engine expressivity) registered,
skeptic attack, then `prereg-freeze`. Target: freeze-ready in ≤1 agent-day (the engine's
own ENG-1 friction fork measures this).

### 2.2 First literature-KB steps (Pillar C, week-1 sequence)

1. **Register the free keys now** (§3 table): OpenAlex (mandatory for API access since
   ~March 2026), Semantic Scholar (form, ~1 RPS), Hugging Face read token. Zero cost.
2. **B1 — skeleton** (~0.5 agent-day): `kb/` layout, `kot-lit/1` schema, `kb-check`
   validator, canonical-JSON/hash utilities borrowed from `tools/registry/`.
3. **Bootstrap corpus, internal-first**: chunk and record the ~200 works already cited
   across the five lit reports, the reports and design docs themselves, and all existing
   verdict objects. This is the highest-value content in the whole KB (verified
   synthesis) and needs no discovery pipeline.
4. **Pinned local embedder run**: `nomic-embed-text-v2` (137M, CPU-viable), niced
   overnight on this box; commit 256-dim f16 shards (~5 MB at 10k chunks) + manifest
   pins. Brute-force cosine search — no ANN index, no hosted service (fork KB-F1 keeps
   LanceDB as the measured fallback).
5. **Haiku extraction batch** for the read-tier papers (Batch API, structured outputs;
   ~$5–8 for a 500-paper bootstrap) + the Codex 5% spot-audit hook.
6. **Acceptance test**: `kb novelty` on the three N0 §4 headline forks
   (N-A1/N-B1/N-C3) must surface the L1–L3 prior art and the registry verdicts we
   already know are the right answers. Only then wire the weekly ingest cron and
   `kb-sync-internal`.

Steps 2–4 alone already make the KB useful to the L3a candidate's prior-art step;
steps 5–6 complete deltas D5/D2-feed for the engine.

### 2.3 Engine build deltas to land before F2 closes (Pillar B)

D1 (`kot-assess/1` + assess-gen), D2 (known-results ledger + backfill), D3 (candidate
template + backlog scorer) — ~1.5 agent-days total, $0 compute — so that **the F2
verdict is the first result to flow through the assessment loop** (the natural
acceptance test). D4 (dag-gen) and D5 (lit-scan, superseded by `kb novelty` when C
lands) follow; D6 (`kot-reg/2`) waits on maintainer approval since it touches the
honesty schemas.

### 2.4 Sequencing and the F2 branch

F2's verdict re-ranks but does not block the bootstrap: **HE1 PASS** promotes the
engine-seat rungs (L3a/L3b become the primary track — verifier and answerer are one
artefact); **HE1 KILL + HC2 PASS** narrows L3 to axiom-licensed content (counting,
functionality, disjointness — still exactly the `mother` example) and raises the
interpretability lane (L2a); **both KILL** leaves L2a's interpretability claim, L3a's
cost/exactness claim, and L1a's robustness endpoint as the surviving pitches — none of
which the F2 outcome touches (N1-A §6.2). In every branch, L3a and the KB bootstrap were
worth building. The L2c semantic-fixedness sweep reads the same branch (N1-A §6.2):
HE1 PASS raises the in-network φ>0 region; HE1 KILL + HC2 PASS narrows its in-kernel
domain to axiom-licensed content and leaves the φ=1 scoping endpoint carrying it;
both-KILL demotes the expensive exponent leg but keeps L2c-lite justified as the
de-confounding instrument for the LCM anchor — and either way its surface fixes the φ
design points the L2 rungs must otherwise assume.

---

## 3. Consolidated maintainer supply list

Everything the maintainer must provide or decide for the bootstrap, in one place.
Recommended-set recurring cost: **$0 beyond existing Anthropic spend**; one-off spend
asks total **≈ $30–40** (KB extraction + L3a's LLM arms), all inside existing tier caps.

### 3.1 Keys & accounts (all free)

| # | Item | Cost | Action | Used by |
|---|---|---|---|---|
| 1 | OpenAlex API key | Free | Register at openalex.org (keys mandatory since ~Mar 2026) | KB discovery/metadata backbone |
| 2 | Semantic Scholar API key | Free (request form; ~1 RPS) | semanticscholar.org/product/api | Citation graph, `kb related`, SPECTER2 side channel |
| 3 | Hugging Face token (read) | Free | Create token | Trending-papers signal (PWC successor); pinned embedder download |
| — | Anthropic API | already held | none | Haiku extraction agents (Batch API, −50%) |
| — | Explicit non-purchases | — | none | Hosted vector DBs, hosted embeddings, Scopus/WoS — rejected in N-C §§1.1/5; Exa/Tavily deferred behind fork KB-F5 |

### 3.2 Spend acks (one-off / trickle)

| # | Item | Envelope |
|---|---|---|
| 1 | KB bootstrap Haiku extraction | **$10–20 one-off**, then **<$5/month** |
| 2 | L3a engine-oracle (first rung) | **~$0–20** (Tier 0–1; engine+eval local CPU, LLM arms on the F2 Modal harness) |
| 3 | L1a canonicaliser (second rung, after L3a freeze) | ~$20–60 (Tier 1–2, inference-only) |
| 4 | Committed-embeddings repo weight | ~5–25 MB now; git-lfs decision deferred to a >50 MB trigger |
| — | Engine build deltas D1–D5 | ~$0 (agent time only, ≈3–3.5 agent-days) |

### 3.3 Decisions to ratify (each is a recorded decision; none is assumed)

1. **Ratify the engine spec** (N-B) as standing procedure — it then freezes and changes
   only by dated, signed amendment.
2. **Approve `kot-reg/2`** (N-B delta D6) — the only change touching the honesty
   schemas (open pins map + declared instrument gates + candidate/generation fields).
3. **Generation budget pattern**: each generation dossier carries its own spend ask,
   with standing tier caps as per-candidate defaults.
4. **Codex strongest-rival duty**: the cross-vendor red-team proposes one candidate per
   generation designed to *beat* our best mechanism (separation preserved: it never
   runs, grades, or audits what it proposed).
5. **Cadence ack**: generations of 2–4 weeks; weekly one-screen generated heartbeat.
6. **KB honesty boundary** (N-C §0) as binding policy: KB records ≠ evidence; internal
   records generated-only; Codex spot-audit on every extraction batch.
7. **Bootstrap ordering**: confirm L3a as the first architecture rung (or swap to L1a —
   §2.1 records both the recommendation and the swap's cost).

---

## 4. What this document does NOT do (honesty footer)

It creates no registry entries, freezes nothing, amends nothing frozen, and asserts no
empirical result beyond what the registry and audited verdicts already hold (N0 §1.3's
one-screen ledger is the authoritative status: two audited Tier-0 passes, one narrow
in-network transfer result, one paid pivot running, zero end-task wins over text). Every
recommendation above — including the choice of first rung — is a design opinion phrased
so that a pre-registered experiment, not this document, decides it. The programme's two
top questions remain the directives' (§4): is the kernel principle useful to LLMs at
all, and if so, which kernel structure is most useful? Programme 2 is the machine for
answering them — and for being told *no* cheaply, honestly, and in public.

---

*Cross-references:* `docs/next/arch-survey.md` (N0); `docs/next/architecture-ladder.md`
(N1-A); `docs/next/research-engine.md` (N-B); `docs/next/literature-kb.md` (N-C);
`docs/kernel-design-directives.md` (binding); `reports/lit-llm-injection-priorart.md`
(L3 laws); `registry/status.json` (freeze state, tier caps);
`docs/design-constraint-layer.md` §3 (`kot-axiom/1`); `mapper/README.md` (Phase M).
