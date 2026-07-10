# Free / Discounted Compute Recon — Kernel of Truth

**Beneficiary:** Jesse Wright, University of Oxford, Dept of Computer Science (jesse.wright@cs.ox.ac.uk), UK-based academic.
**Need:** GPU for training / batch inference / mechanistic-interpretability, plus some LLM inference-API credits. Possible future startup entity: **sparq-org**.
**Consolidated:** 2026-07-10 from 4 scout reports (A academic-HPC, B hyperscaler, C AI-compute-startups, D grants+API). Scout URLs fetched/verified 2026-07-10 unless flagged **UNVERIFIED**.

> **Honesty note:** "UNVERIFIED" labels are carried through verbatim from the scouts — do not present those items as confirmed. Dollar figures on discretionary programmes ("up to $X") are ceilings, not guarantees; pre-revenue/individual applicants usually land at the low end.

---

## 0. Context — already secured / applied (DO NOT double-apply)

| Programme | Status | Value | Note |
|---|---|---|---|
| **Anyscale** (hosted Ray credit) | **SECURED** | $100 | Already in hand — use it. |
| **Cloudrift AI grant** | **APPLIED** | $1,000 | Application in flight — do not re-apply; await decision. |

Everything below is **net-new** and stackable on top of these two.

---

## 1. TOP 5 TO PURSUE NOW

Best value-for-effort for a UK Oxford academic (credit value × eligibility fit × low effort × approval odds). This set deliberately spans all three needs: **NVIDIA GPU** (ARC, AIRR, Modal), **TPU** (TRC), and **LLM inference-API** (Anthropic).

1. **Oxford ARC (Advanced Research Computing)** — Free at-point-of-use GPU on Oxford's own cluster (A100 / H100 / GH200), no GPU-hour cap on Basic QoS. *Highest approval odds of anything here — near-certain, immediate.*
   - **How to apply:** Fill the "request a user account" form (+ new-project Microsoft Form if none exists) — Jesse qualifies directly as Oxford CS staff. Ask CS/MPLS whether the division has top-sliced Standard QoS (would make faster queue free too).
   - **URL:** https://www.arc.ox.ac.uk/arc-registration-request-forms

2. **AIRR Gateway route (Isambard-AI / Dawn)** — Up to **10,000 GPU-hours** on a real UK national AI system (GH200), usable within 3 months. Best raw GPU-hours per unit of effort. Compute-only, no cash.
   - **How to apply:** Online AIRRPortal form + short project template; individual UK PI qualifies (no company, no lecturer bar). **Do not use a Gmail/functional-ID email** — use @cs.ox.ac.uk. Fortnightly batching, ~1 month to award.
   - **URL:** https://portal-airr.isambard.ac.uk/login/

3. **TPU Research Cloud (TRC) — Google** — Free quota on Google's Cloud TPU fleet (v5e/v6e-class pods), via JAX/PyTorch/TF. Directly useful for training / batch-inference / interp on non-NVIDIA silicon.
   - **How to apply:** Short web form describing project + intended TPU use; open to individuals, no institutional gate. *Catch: needs a live GCP billing account (card on file) for surrounding VM/storage — those aren't free; publish/open-source obligation.*
   - **URL:** https://sites.research.google/trc/

4. **Anthropic External Researcher Access Program** — ~**$1,000** Claude API credits (higher case-by-case). Strong topical fit — interpretability / grounded-representations maps cleanly onto their safety/alignment priorities, and it covers the inference-API need directly.
   - **How to apply:** Single Google Form (team + topic). Evaluated first Monday of each month. *Catch: silence = rejection; API-only.*
   - **URL:** https://forms.gle/pZYC8f6qYqSKvRWn9
   - *(Higher-value sibling: **Anthropic AI for Science**, up to ~$20k but discretionary — apply to both; see table.)*

5. **Modal for Academics** — Up to **$10,000** serverless GPU credits (H100/B200), pay-per-invocation. Best serverless fit for a "training-free kernel" (batch inference / mech-interp, no idle-GPU cost). *$25k figure from aggregators is **UNVERIFIED** — direct source says $10k.*
   - **How to apply:** Online form on the academics page; UK faculty/postdoc/PhD eligible. Rolling.
   - **URL:** https://modal.com/academics

**Honorable mentions just outside the 5** (all low-friction, worth firing off same week): **Prime Intellect Fast Compute Grants** ($500–$100k, "anyone anywhere," email a pitch — fastest/least bureaucratic); **Google Cloud Research Credits** ($5k, UK confirmed eligible); and **activate the free API tiers now** (Groq, Google AI Studio, Mistral, SambaNova — zero effort supplementary inference).

---

## 2. Startup-angle options (route via sparq-org, NOT Jesse personally)

**All require sparq-org to be a real incorporated entity** (most need a working website; the AIRR route needs a UK Companies House number + Subsidy Control Act 2022 compliance). None are usable pre-incorporation. Ranked by value-for-effort once incorporated:

| Programme | What you get | Gate | Effort | Apply URL |
|---|---|---|---|---|
| **AIRR Rapid Access** | 20,000 GPU-hrs (3 mo), Isambard-AI/Dawn | UK-registered micro/SME + Companies House # + Subsidy Control compliance | Low | https://www.ukri.org/opportunity/isambard-ai-and-dawn-airr-supercomputers-rapid-access-route/ |
| **NVIDIA Inception** (meta / force-multiplier) | Unlocks partner credits: up to $100k DGX Cloud, up to $100k AWS Activate, up to $150k Nebius + DLI credits | Incorporated, ≥1 dev, working website, <10 yrs | Low (2–4 wk) | https://www.nvidia.com/en-us/startups/ |
| **Together AI Startup Accelerator** | up to $50,000 credits (inference/fine-tune/clusters) | AI-native product framing | Medium | https://www.together.ai/startup-accelerator |
| **Mistral Startup Program** | ~$30,000 credits, no equity (pre-seed→Series A) | Startup entity | Low-Med | https://mistral.ai/startups *(verify link at apply time)* |
| **Baseten AI Startup Program** | up to $25,000 (deploy/train) / up to $2,500 (Model APIs) | Net-new customer only; **6-month use-or-lose clock** | Low-Med | https://www.baseten.co/startup-program/ |
| **Fireworks for Startups** | up to $10,000, no equity | AI-native GenAI app; no academic track | Low | https://fireworks.ai/startups |
| **Replicate Startup Credits** | $1,000–$10,000 inference, non-dilutive | Pre-Series-B, production product on open-weight models | Low | https://replicate.com/startups |
| **Google for Startups Cloud** | Bootstrapped $2k → Standard $100k → AI-first up to $350k | <5 yrs (AI-first <10y), <Series A; no nonprofit/edu; big tiers need equity funding | Low (Bootstrapped) | https://cloud.google.com/startup/apply |
| **AWS Activate Founders** | up to $5,000 (Portfolio $200k needs a VC/accelerator "Activate Provider") | <10 yrs, pre-Series-B, new to Activate | Low | https://aws.amazon.com/startups/credits/ |
| **Microsoft for Startups Founders Hub** | $5,000 baseline ($1k instant + $4k) → up to $150k for funded co's | Startup, no equity taken | Low | https://www.microsoft.com/en-us/startups |
| **RunPod Startup — Starter tier** | $1,000, no commitment (Growth $75k needs $50k upfront spend — not free) | Deprioritizes non-VC/bootstrapped | Low | https://www.runpod.io/startup-program |
| **CoreWeave Startup Accelerator** | est. $50k–$250k value — **UNVERIFIED** (CoreWeave publishes no figure) | AI/ML startup; scale-mismatch for a micro pre-revenue team | Med-High | https://www.coreweave.com/startups |
| **Nebius for Startups** | $5k intro → up to $100k | **Gated to VC backing ≥$5M or waitlist** — not realistic yet | — | https://nebius.com/nebius-research-grants |

**Startup-track caveats:**
- **Founders-Hub OpenAI-credit benefit is UNVERIFIED / likely discontinued** — multiple secondary sources say the separate OpenAI allowance is gone; treat "+OpenAI credits" as stale. Credits also expire (1 yr baseline).
- **Vast.ai "Startup Program" is spend-matching, NOT a free grant** — dollar-for-dollar match on *verified spend*; you must already be paying. Excluded from the table as not-free.
- The headline six-figure tiers on Google/AWS/Microsoft/Nebius are gated behind equity funding sparq-org likely doesn't have — expect the low self-serve tiers ($2k–$5k) initially.
- **NVIDIA Inception gives no direct compute itself** — its value is entirely in unlocking the partner allocations (each separately reviewed).

---

## 3. Full ranked table (deduped across categories, sorted by priority)

**Priority key:** **P1** = pursue now, top value/effort · **P2** = worth a short proposal · **P3** = free tier, activate now (zero effort) · **P4** = watch / reopening / bigger prize but closed or gated · **P5** = skip / poor fit · **S** = startup-entity only (see §2).

| Programme | What you get | Eligibility fit (UK academic) | Effort | Deadline | Apply URL | Priority |
|---|---|---|---|---|---|---|
| Oxford ARC | Free GPU (A100/H100/GH200), no Basic-QoS cap | Trivial — Oxford staff | Low | Rolling | arc.ox.ac.uk/arc-registration-request-forms | **P1** |
| AIRR Gateway | up to 10,000 GPU-hrs (GH200), 3-mo | Strong — individual UK PI | Low-Med | Rolling (fortnightly) | portal-airr.isambard.ac.uk | **P1** |
| TPU Research Cloud (TRC) | Free Cloud TPU quota (v5e/v6e) | Strong — individuals OK | Low | Rolling | sites.research.google/trc | **P1** |
| Anthropic External Researcher Access | ~$1k Claude API credits (higher case-by-case) | Strong — interp/safety fit | Low | Rolling (1st Mon) | forms.gle/pZYC8f6qYqSKvRWn9 | **P1** |
| Modal for Academics | up to $10k serverless GPU ($25k UNVERIFIED) | Strong — UK academic | Low-Med | Rolling | modal.com/academics | **P1** |
| Prime Intellect Fast Compute Grants | $500–$100k credits (cluster low) | Strong — anyone anywhere | Low | Rolling | primeintellect.ai (/iclr URL 404 UNVERIFIED — email contact@primeintellect.ai) | **P2** |
| Anthropic AI for Science | up to ~$20k Claude credits (discretionary) | Good — frame as AI-for-research | Low-Med | Rolling | anthropic.com/news/ai-for-science-program | **P2** |
| Google Cloud Research Credits | up to $5k (faculty/postdoc), one-time | Strong — UK confirmed eligible | Medium | Rolling | cloud.google.com/edu/researchers | **P2** |
| EuroHPC Development Access | Small dev-scale alloc (LUMI/Leonardo/MN5/JUPITER) | Eligible — UK now EuroHPC state | Low | Monthly cut-off (1st, 10:00 CET) | access.eurohpc-ju.europa.eu/calls/42 | **P2** |
| AWS Cloud Credit for Research | Faculty uncapped (proposal-scoped) | Good — needs PAID AWS acct (Free Tier ineligible from 16 Feb 2026) | Med-High | Rolling | pages.awscloud.com/aws-cloud-credit-for-research | **P2** |
| Cohere Labs Catalyst Grants | Cohere API credits (amount undisclosed) | Good — interp/efficiency fit | Low-Med | Rolling | cohere.com/research/grants | **P2** |
| OpenAI Researcher Access | up to $1k API credits, 12-mo expiry | Good — UK eligible (not priority tier) | Low | Quarterly — next ~Sept 2026 | openai.com/form/researcher-access-program | **P2** |
| Nebius Research Credits/Grants | up to 8 GPUs/yr OR 10M tokens | UK eligibility **UNVERIFIED** | Medium | 2026–27 cycle; notify Q3–Q4 2026 | nebius.com/nebius-research-credits-program | **P2** |
| Lambda AI Research Grant | up to $5k credits + mentoring | non-US eligibility **UNVERIFIED** | Medium | Rolling/cohort | lambda.ai/research | **P2** |
| Oracle for Research | Starter $1k / Project variable OCI | Good — no country excl. (exc. China) | Medium | Rolling | go.oracle.com/research-cloud-starter-award | **P2** |
| Groq free API tier | Free rate-limited LPU inference (no card) | Open to anyone | Low | Standing | console.groq.com | **P3** |
| Google AI Studio / Gemini free tier | Free Flash models, ~1,500 req/day (Pro now paid) | Open | Low | Standing | aistudio.google.com | **P3** |
| Mistral La Plateforme free tier | ~1B tokens/mo (eval only); €150/mo credit UNVERIFIED | Open | Low | Standing | console.mistral.ai | **P3** |
| SambaNova Cloud free tier | $5 credit + rate-limited free tier | Open | Low | Standing | cloud.sambanova.ai | **P3** |
| HF Community GPU Grant (Spaces) | Free GPU upgrade for a public demo | Only if shipping an interactive demo | Low | Rolling | huggingface.co/docs/hub/spaces-gpus | **P3** |
| Lightning AI base free tier | 1 always-on Studio + ~80 GPU-hrs/mo | Open (NAIRR 1M-H100 pool is US-gated, **UNVERIFIED** excl.) | Low | Standing | lightning.ai/docs/team-management/academia | **P3** |
| AIRR Innovator route | 50k–150k GPU-hrs (6 mo) | Lecturer-level bar **UNVERIFIED** for Jesse; peer-review duty | Med-High | Round 1 CLOSED (Jan 2026); watch R2 | ukri.org/opportunity/…innovator-route | **P4** |
| AIRR AI for Science | 200k–1M GPU-hrs (6 mo) | Narrow scope — Kernel of Truth a stretch | High | Last round closed Dec 2025; watch | ukri.org/opportunity/airr-compute-opportunity-ai-for-science | **P4** |
| UK Tier-2 Access to HPC | Baskerville/Sulis/Bede/Isambard-3 A100s | Good — UKRI-eligible, no grant needed | Med (2-stage) | Biannual; **no window confirmed open** (~mid-2026?) | ukri.org/opportunity/access-to-high-performance-computing-facilities-autumn-2025/ | **P4** |
| Amazon Research Awards | $40k–$100k + $50k–$250k AWS credits | Faculty; competitive; UK unis have won | High | Spring 2026 closed; Fall 2026 expected ~Aug–Sep (not posted) | amazon.science/research-awards/call-for-proposals | **P4** |
| NVIDIA Academic Hardware Grant / ARAP | up to 30,000 H100-hrs OR 8× RTX PRO 6000 | **Full-time faculty PI gate** — may need faculty co-PI | High | **CLOSED now**; quarterly windows | academicgrants.nvidia.com | **P4** |
| Cerebras Inference Research Grant | up to $50k inference credits | Faculty-PI gate | High | 2026 CFP **UNVERIFIED** (last Jan 2025 passed) | cerebras.ai/inference-research-grant | **P4** |
| EuroHPC Regular / Extreme Scale | Large allocations | Eligible — needs Dev-Access results first | High | Periodic calls | eurohpc-ju.europa.eu | **P4** |
| Microsoft Azure Research Credits | "Large" alloc, amount opaque | UK eligibility **UNVERIFIED** | Medium | Varies by cycle | microsoft.com/en-us/azure-academic-research | **P4** |
| Together AI Research Credits | "a few hundred $", **invite-only** | Low odds on cold apply | Low | Rolling | together.ai/research-credits-program-request | **P4** |
| RunPod academic research | Terms opaque (no public figures) | Labs/universities, case-by-case | Med (email) | Rolling | runpod.io/research-credits | **P4** |
| DiRAC Seedcorn (STFC) | up to 1,000 GPU-hrs (fast) | Poor — STFC physics scope only | Low | Rolling | dirac.ac.uk/getting-access | **P5** |
| ARCHER2 GPU Pump Priming | up to 4,000 CU on 16× AMD MI210 | Tiny; ROCm-only; service winding down | Low | Rolling | archer2.ac.uk/support-access/access.html | **P5** |
| Schmidt Sciences AI2050 | $300k–$500k / 3 yrs | **Nomination-gated**; 2026 effectively closed | High | 2026 closed; watch 2027 | ai2050.schmidtsciences.org | **P5** |
| Mozilla Democracy x AI | $50k (+$250k finalists) | Off-topic (democratic-governance); routes via US 501(c)(3) | Med-High | Closed Mar 2026 | mozillafoundation.org/…/incubator | **P5** |
| ML Collective compute | Informal free GPU (GCP) | Good fit but **currently PAUSED** | Low (email) | Paused since ~Jul 2025 | mlcollective.org/wiki/ask-mlc-compute-assistance | **P5** |
| EleutherAI SOAR / community | Mentorship (not a compute grant) | SOAR skews newcomers; 2026 closed | Low | SOAR closed Jun 2026 | eleuther.ai/soar | **P5** |
| AI Grant (aigrant.org) | $5k–$50k compute or cash (OSS) | Plausible OSS fit — **UNVERIFIED** current cycle | Medium | **UNVERIFIED** — verify live link | aigrant.org | **P5** |
| a16z Open Source AI Grant | Unrestricted OSS funding (amount undisclosed) | Plausible OSS fit — **UNVERIFIED / possibly dormant** | Unknown | **UNVERIFIED** — no live form found | a16z.com/supporting-the-open-source-ai-community | **P5** |
| AIRR Rapid Access | 20,000 GPU-hrs (3 mo) | **sparq-org only** (Companies House # + Subsidy Control) | Low | Rolling | ukri.org/opportunity/…rapid-access-route | **S** |
| NVIDIA Inception | Unlocks up to $100k DGX / $100k AWS / $150k Nebius | **sparq-org only** (incorporated + website) | Low | Rolling | nvidia.com/en-us/startups | **S** |
| Together AI Startup Accelerator | up to $50k credits | **sparq-org only** — product framing | Medium | Rolling | together.ai/startup-accelerator | **S** |
| Mistral Startup Program | ~$30k, no equity | **sparq-org only** | Low-Med | Rolling | mistral.ai/startups | **S** |
| Baseten AI Startup Program | up to $25k / $2.5k; 6-mo clock | **sparq-org only** — net-new only | Low-Med | Rolling | baseten.co/startup-program | **S** |
| Fireworks for Startups | up to $10k | **sparq-org only** | Low | Rolling | fireworks.ai/startups | **S** |
| Replicate Startup Credits | $1k–$10k inference, non-dilutive | **sparq-org only** — production product | Low | Rolling | replicate.com/startups | **S** |
| Google for Startups Cloud | $2k → $100k → $350k (AI-first) | **sparq-org only** — big tiers need equity | Low (Bootstrapped) | Rolling | cloud.google.com/startup/apply | **S** |
| AWS Activate Founders | up to $5k ($200k needs VC provider) | **sparq-org only** | Low | Rolling | aws.amazon.com/startups/credits | **S** |
| MS for Startups Founders Hub | $5k baseline (up to $150k funded); OpenAI credit UNVERIFIED/likely gone | **sparq-org only** | Low | Rolling | microsoft.com/en-us/startups | **S** |
| RunPod Startup — Starter | $1k, no commitment | **sparq-org only** — non-VC deprioritized | Low | Rolling | runpod.io/startup-program | **S** |
| CoreWeave Accelerator | $50k–$250k value **UNVERIFIED** | **sparq-org only** — scale mismatch | Med-High | Rolling | coreweave.com/startups | **S** |
| Nebius for Startups | $5k → $100k | **sparq-org only** — gated VC ≥$5M | — | Waitlist | nebius.com/nebius-research-grants | **S** |

**Explicitly excluded (checked, not viable / not free):**
- **Microsoft AI for Good Lab** — restricted to Washington-State-based/benefiting projects. Not usable from Oxford.
- **Vast.ai Startup Program** — spend-matching (match on *verified spend*), not a no-strings grant.
- **JADE2** — decommissioned since 1 Sept 2024; dead, do not chase.
- **Hyperbolic / SF Compute / Crusoe / DataCrunch-Verda** — no confirmed academic or startup grant programme found (DataCrunch/Verda expanding into UK — worth a re-check later).

---

## 4. Recommended sequence (bottom line)

- **This week, parallel, near-zero risk:** Oxford ARC account · AIRR Gateway form · TRC form · Anthropic External Researcher form · Modal for Academics · and just switch on the free API tiers (Groq / Google AI Studio / Mistral / SambaNova). Fire a one-paragraph pitch at Prime Intellect too — it's the cheapest shot at a large number.
- **Next 2–4 weeks, short proposals:** Google Cloud Research Credits ($5k) · Anthropic AI for Science (up to ~$20k) · EuroHPC Development Access (next monthly cut-off) · AWS Cloud Credit for Research (open the paid AWS account *first*) · Cohere Catalyst.
- **Watch-and-reapply (bigger prizes, currently closed/gated):** AIRR Innovator R2 · Amazon Research Awards Fall 2026 · NVIDIA Academic/ARAP + Cerebras — the last two are **faculty-PI-gated**, so flag them to Jesse's PI/supervisor as named applicant when windows reopen.
- **Only once sparq-org is incorporated:** AIRR Rapid Access (needs Companies House #) and NVIDIA Inception (unlocks the six-figure partner pools) are the two highest-leverage entity plays; the rest are modest self-serve top-ups.

**Reality check on approval odds:** the P1 five are all high-probability, low-effort, and cover GPU + TPU + inference-API between them — ARC is effectively guaranteed and AIRR Gateway is a light-touch pilot route, so Jesse can realistically have working GPU access within ~4 weeks without spending a penny. The eye-catching six-figure numbers (NVIDIA/Cerebras/Amazon/AIRR-Innovator, and the startup tiers) are either closed, faculty-PI-gated, competitive, or need an incorporated funded company — treat them as second-wave targets to pursue *after* the P1 pilots generate citable results, not near-term wins.
