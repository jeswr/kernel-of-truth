# P11 — Funding & compute-access plan

**Status:** resource-acquisition plan for maintainer sign-off, 2026-07-08. Component P11 of
the operational research plan (`docs/research-plan/`). Consumes P6 (`06-resources.md` —
providers, planning rates, canonical caps) and P1 §5 (tier costs / kill-tree). Every
external figure below was **verified against live sources on 2026-07-08**; each carries its
source URL. Prices for marketplaces are volatile — re-verify at I-BUDGET time and pin into
`registry/budget.json` per F0 §3.5.

> **Timeline note (2026-07-08, post-authorship):** gate dates in this document were written
> against the pre-recompression calendar. Under the agentic-pace re-base (P3 §5), GNG-2 /
> GATE-T4 land ≈ GNG-0 +2–3 wk (**~Aug 2026**, not ~Sep 25) and GATE-T5 stays **~Oct 2026**
> — now bound by the AIRR/ARC access lead time itself, not by evidence readiness. This makes
> the "start the free-path onboarding NOW" actions (§5 N-1…N-7) *more* urgent, not less.
> Tier-0 + Tier-1 spend is AUTHORIZED (2026-07-08); the Tiers 2–5 provider fields are
> DEFERRED/OPEN, re-frozen at each tier's spend-gate (P6 authorization block).

**Governance note.** P6 §1.1 contains a standing "**No other providers**" decision (Modal
primary, AWS fallback; Lambda/RunPod/etc. rejected for credential/image/provenance overhead).
Nothing in this document overrides that. §2 below prices the rejected options so the
decision stays evidence-based; §4 (ARC / UK national HPC) and the credit programs in §3 are
proposed as *amendments* to P6 — each needs a one-line maintainer decision (new open
decisions O-8…O-10, §5) before any harness work starts.

---

## 1. Cost decomposition: what is actually money, and whose money

Four cost classes, applied to every quoted tier figure:

- **(A) Subscription-absorbed agent labour (~$0 marginal).** All Claude-Code-CLI work —
  orchestration (Kern + Fable subagents), NSM/kernel authoring done *in-session*, harness and
  analysis code, registry/report/paper writing, red-teaming — rides on the maintainer's
  existing **Claude Max20** subscription (plus the backup Fable account for auditor
  separation, O-5). This is the overwhelming majority of programme labour and it never
  touches the $ ledger.
  **Explicit warning:** interactive subscriptions (Claude Max, ChatGPT Plus/Pro) do **not**
  cover metered token billing at `api.anthropic.com` / `api.openai.com`. A scripted
  `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` run is real money on a separate account. Where P6
  §2.2 allows either route (G9/RT-11 authoring: "in-session agent authoring with recorded
  model id (default), or `ANTHROPIC_API_KEY` for scripted reproducibility"), **prefer the
  in-session route** — it is subscription-absorbed and the registry records the model id
  either way.
- **(B) Metered model-API (small, capped).** Only three arms genuinely need metered API:
  (1) the **proposer-invariance second-provider arm** (G4/G9 secondary; one non-Anthropic
  key, $25 hard cap at the provider dashboard — this one *cannot* shift to the CLI, its
  whole point is a non-Anthropic model); (2) any **scripted-reproducibility** authoring runs
  the maintainer opts into (shiftable to CLI, see above); (3) G8's Lean location probe if
  run scripted (shiftable to CLI). DeepNSM comparison uses published numbers or free HF
  artifacts ($0); the PRM baseline is an open checkpoint on our own GPU ($0 API). Programme
  API total ≤ **$60–100** worst case (P6 §2.2), and with the CLI-shift applied the realistic
  metered spend is **$10–50** (second-provider key + small scripted residue).
- **(C) GPU rental — the real money.** Tiers 1–5, per-second Modal billing today. This is
  the only cost class where funding/access work (this document) changes the picture.
- **(D) $0 / human-hour items.** Tier-0 CPU on this box; annotator hours (H-4: ~30–40 h at
  $0 if maintainer+colleague, else $500–900 platform); maintainer gate decisions (H-1…H-10);
  supervisor signatures for ARC/AIRR (§4).

### Tier table: {GPU $, metered API $, subscription-absorbed}

| Tier (cap) | GPU rental $ (C) | Metered API $ (B) | Subscription-absorbed (A) | $0 / human (D) |
|---|---|---|---|---|
| **0** — R0 on-box (≤$20) | $0 | $0–20 (G4/G8/G9 scripted arms; **→ ~$0 if shifted in-session**, leaving only the second-provider key $5–25 charged here) | all authoring, validator loops, analysis, M0b, report-gen | annotator 30–40 h (or $500–900); box CPU |
| **1** — F2 pivot (≤$80) | **$10–60** (T4/A10G, 15–40 h) | $0 | RunSpec authoring, arm analysis, verdict drafting | — |
| **2** — E9/F4/G1/E8 (≤$400) | **$95–360** (T4/A10G, 80–270 h) | $5–25 (RT-11 `authoring_cost` line, D-DOM ≥50 explications; **→ ~$0–10 if authored in-session**) | eval-pack builds, SAE selection, audits | D-IR-N adjudication ~2 h |
| **3** — F3/F6 (≤$400) | **$100–320** (A10G + first A100 hours) | ≤$20 (M2-output rider, inside F3 cap) | corpus builds, scaffold pipelines | — |
| **4** — F5 (≤$900, GATE-T4 ~Sep 25) | **$200–800** (A100-40GB, 100–350 GPU-h) | ~$0 | training-grid code, ledgers, GNG-2 dossier | maintainer GATE-T4 decision |
| **5** — F7/E7 (envelope $2–10k, GATE-T5 ~Oct 26) | **$2,000–10,000** (≈500–2,500 H100-h at Modal's $3.95/h, or ≈950–4,800 A100-40GB-h) | ~$0 | slope analysis, paper | maintainer GATE-T5 decision |
| **Total (worst case)** | ≈ $760 (Tiers 0–3) + $800 (T4) + $10k (T5) | ≤$60–100 (→ $10–50 with CLI-shift) | ~$0 marginal | 30–40 h annotation + gate decisions |

Reading: **(C) is >95% of all out-of-pocket money, and Tiers 4–5 are >90% of (C).** So the
funding strategy is: squeeze Tiers 0–3 toward $0 with free credits (§2), and aim Tiers 4–5
at free academic compute (§3–4) so the $2.4–11.6k worst-case exposure becomes a
contingency, not a bill.

---

## 2. Free / discounted GPU options (verified 2026-07-08)

### 2.1 Modal free credits — the zero-effort lever (KEEP)

- **What:** Starter (free) plan includes **$30/month free compute credits**, 100 containers,
  10 concurrent GPUs. Verified: [modal.com/pricing](https://modal.com/pricing).
- **Current Modal on-demand rates** (verified same page, converted from per-second):
  T4 **$0.59/h** · L4 $0.80/h · A10 **$1.10/h** · L40S $1.95/h · A100-40GB **$2.10/h** ·
  A100-80GB **$2.50/h** · H100 **$3.95/h** · H200 $4.54/h · B200 $6.25/h. These match P6
  §1.2's planning rates (T4 ~$0.6, A10G ~$1.1, A100 $2.1–2.8, H100 ~$4) — **no P6 revision
  needed**; pin exact rates at I-BUDGET.
- **Eligibility / access:** already have it — profile `jmwright-045` is on this plan class.
  Action: confirm the workspace shows the monthly credit and that runs draw it down first.
- **Arithmetic:** Jul→Oct 2026 = ~$120 of free credit across the Tiers 0–3 window if
  campaigns are paced monthly; that alone covers Tier 1 entirely and ~15% of the Tiers 0–3
  worst case.
- **Reproducibility:** perfect — status quo (pinned image digest, per-second ledger).
- **Best serves:** Tiers 0–3 (and it is already the plan of record).

### 2.2 Spot / marketplace GPU (priced for the record; adoption = P6 amendment)

| Provider | A100 80GB $/h | H100 $/h | vs Modal | Source (verified 2026-07-08) |
|---|---|---|---|---|
| **Vast.ai** (marketplace) | ~**$0.67–0.72** on-demand avg; interruptible 50%+ below | from ~**$1.47** on-demand; spot reported as low as ~$0.34–0.65 | A100 ≈ **70% cheaper**, H100 ≈ **60% cheaper** | [vast.ai/pricing](https://vast.ai/pricing), [cloudzero.com H100 cost](https://www.cloudzero.com/blog/h100-gpu-cost/), [synpixcloud comparison](https://www.synpixcloud.com/blog/cloud-gpu-pricing-comparison-2026) |
| **RunPod** | Secure $1.39 (PCIe) / $1.49 (SXM); Community ~20–40% lower | Secure $2.89 (PCIe); Community lower | A100 ≈ **40–55% cheaper**, H100 ≈ **27–45%** | [runpod.io/pricing](https://www.runpod.io/pricing), [northflank breakdown](https://northflank.com/blog/runpod-gpu-pricing) |
| **Lambda** | ~$2.49 on-demand | $2.99–3.29 (often 8× bundles) | ≈ 0–25% cheaper; **no spot tier** | [lambda.ai/pricing](https://lambda.ai/pricing), [synpixcloud](https://www.synpixcloud.com/blog/lambda-labs-gpu-pricing-2026) |

- **Eligibility/access:** credit card sign-up, minutes. **Reproducibility caveat:** all
  three run our own Docker/OCI images, so hash-pinning works; but vast.ai is heterogeneous
  host hardware (F0 §3.5 pinned-hardware discipline requires filtering to the exact GPU SKU
  and recording host fingerprint), and interruptible instances add preemption→checkpoint
  complexity to the harness.
- **Honest sizing vs P6's rejection:** on Tier 4 worst case (350 A100-h) vast.ai saves
  ≈ $2.10–0.70 = **$1.40/h ⇒ ~$490 max**; on Tiers 1–3 the saving is $100–300. Against
  that: new credential handling, provenance plumbing, preemption logic — the exact costs P6
  §1.1 cited when it rejected extra providers. **Recommendation: do not adopt for Tiers
  0–3.** Revisit *only* if (a) GATE-T4 approves F5 at the high end **and** (b) neither ARC
  (§4.1) nor credits (§3) landed in time — then a RunPod *Secure Cloud* (not vast.ai
  interruptible) adapter is the least-bad option, decided as **O-9**.

### 2.3 Colab / Kaggle — scouting only, never registry runs

- **Colab** (verified: [colab pricing/signup](https://colab.research.google.com/signup),
  CU burn rates via [mccormickml.com](http://mccormickml.com/2024/04/23/colab-gpus-features-and-pricing/),
  [thundercompute overview](https://www.thundercompute.com/blog/colab-alternatives-for-cheap-deep-learning-in-2025)):
  Pay-as-you-go **$9.99 / 100 compute units**; **Pro $9.99–11.99/mo** (~100 CU);
  **Pro+ $49.99/mo** (~500 CU, background execution). GPUs: T4, L4, A100-40/80GB —
  *not guaranteed*, availability varies. Burn: T4 ≈1.76 CU/h (≈$0.18/h effective), A100
  ≈15 CU/h (≈$1.50/h effective).
- **Kaggle** (verified: [kaggle docs](https://www.kaggle.com/docs/efficient-gpu-usage),
  [aimultiple survey](https://aimultiple.com/free-cloud-gpu)): free **~30 GPU-h/week**
  (P100 16GB or 2×T4), 12 h max session; TPU v5e-8 sessions 9 h.
- **Reproducibility caveat (disqualifying):** no user-supplied container images, VM images
  drift, sessions preempt — **cannot be hash-pinned**, so per GR discipline these are
  *never* registry-eligible transports. Legitimate uses: free interactive scouting of prompt
  formats / OOM boundaries before writing a RunSpec (Tier 1–2 prep), at $0.
- **Best serves:** pre-Tier-1 exploration only.

### 2.4 HuggingFace ZeroGPU — demos only

Free accounts: ~3.5 min/day of H200 slices; **PRO ($9/mo): 8× quota, up to ~25 min/day
H200** (~70 GB VRAM exposed), over-quota credits $1/10 min. Gradio-Spaces execution model —
not batch, not pinnable. Verified:
[huggingface.co/docs/hub/spaces-zerogpu](https://huggingface.co/docs/hub/en/spaces-zerogpu).
**Best serves:** a public demo Space for the paper/frontier pitch (P9), $0–9/mo. Not an
experiment transport.

### 2.5 Together AI & new-account trial credits

Together research-credit program is **invite-only, small grants** (~hundreds of $ of
inference credits); new accounts get ~$25–50 trial credits. Verified:
[together.ai research credits](https://www.together.ai/research-credits-program-request),
[getaiperks summary](https://www.getaiperks.com/en/ai/together-ai-free-credits-2026).
Inference-API only — irrelevant to our GPU rental, but note: a $25 trial credit at a
second, non-Anthropic provider could cover the **proposer-invariance arm at $0** if the
maintainer picks a provider with trial credits at O-7 (OpenAI/Google keys themselves do not
ship meaningful free tiers in 2026).

---

## 3. Academic / researcher credit programs (verified 2026-07-08)

| Program | Amount | Eligibility (us) | Route | Lead time | TPU/port needed? |
|---|---|---|---|---|---|
| **Google Cloud Research Credits** | **PhD student: up to $1,000/yr (may re-apply annually)**; faculty/postdoc $5,000 once | PhD students at accredited institutions in approved countries — **Jesse qualifies directly, no PI needed** | Online form + short proposal + cost estimate + GCP billing account; rolling. [edu.google.com/programs/credits/research](https://edu.google.com/intl/ALL_us/programs/credits/research/), [guidelines](https://support.google.com/google-cloud-higher-ed/answer/10724468?hl=en) | Weeks (rolling) | No — GCE A100/H100 VMs run our pinned containers |
| **AWS Cloud Credit for Research** | **Student awards up to $5,000** (faculty uncapped) | Institutional email required; **Free-Tier accounts ineligible since 2026-02-16** — apply from a standard account | Rolling application. [pages.awscloud.com](https://pages.awscloud.com/aws-cloud-credit-for-research.html), [FAQs](https://aws.amazon.com/government-education/research-and-technical-computing/cloud-credit-for-research/faqs/) | **30–60 days stated; some report 90–120** | No — and it funds our *existing* AWS fallback transport (`poc/gpu/`); still needs the vCPU quota fix (H-9) |
| **Microsoft AFMR** (Accelerate Foundation Models Research) | Azure credits (pilot awards up to ~$20k) + Azure OpenAI access | CFP-based, typically **faculty PI** — supervisor would lead | Proposal to CFP rounds. [microsoft.com/research AFMR](https://www.microsoft.com/en-us/research/blog/accelerate-foundation-models-research-supporting-a-global-academic-research-ecosystem-for-ai/) | Months (round-based) | No, but heavyweight process |
| **Google TPU Research Cloud (TRC)** | **Free TPU quota, 30 days, renewable**; VM/storage still billed (small) | Open to researchers *and students*; rolling invitations; expectation to publish + acknowledge | Sign-up form. [sites.research.google/trc](https://sites.research.google/trc/about/), [FAQ](https://sites.research.google/trc/faq/) | Days–weeks to invite | **Yes — JAX or PyTorch/XLA port.** Our stack is PyTorch/CUDA; only F5/F7 from-scratch training would benefit, and a validated port ≈ 1–2 agent-weeks + a parity gate in the registry. **Default: no.** |
| **NVIDIA Academic Grant Program** | Up to **30,000 H100-hours** or hardware, when a call is open | **Full-time faculty only** (supervisor would apply); **currently NOT accepting applications** — windows open per call | [nvidia.com academic grants](https://www.nvidia.com/en-us/industries/higher-education-research/academic-grant-program/) | Unpredictable; watch for windows via NVIDIA Developer Program | No (CUDA) |
| ~~AWS Activate~~ | startups only — not applicable to a PhD programme | — | — | — | — |

**Fit:** the two *student-direct* programs (Google $1k, AWS $5k) are cheap to apply for,
rolling, and container-clean. Together they roughly cover the **entire Tiers 0–4 worst case
(~$1.56k of $1.66k)** if awarded. AFMR and NVIDIA are supervisor-led moonshots — worth one
email to the supervisor, not worth blocking on.

---

## 4. Oxford ARC + UK national HPC (the key section)

### 4.1 Oxford ARC (Advanced Research Computing) — the Tier-4 free path

**What it is (verified 2026-07-08).** Two clusters, both **SLURM** on AlmaLinux 9.4:
`arc` (CPU capability, 272 nodes) and **`htc` (throughput + ALL GPUs: 124 nodes, 51 GPU
nodes)**. GPU inventory on htc: **16× A100-40GB, 16× H100 (80–96 GB), 92× L40S, 76× V100**,
plus RTX8000/A6000, P100, MI210, GH200 singles. Partitions: `short` (12 h max), `medium`
(48 h), `long`, plus `devel`/`interactive`. Login `htc-login.arc.ox.ac.uk`; storage $HOME
15 GB, **$DATA 5 TB/project**, **no backups** (our push-everything-to-repo discipline
already assumes this). Sources:
[ARC systems (user guide)](https://arc-user-guide.readthedocs.io/en/latest/arc-systems.html),
[general FAQ](https://github.com/oxford-arc/arc-user-guide/blob/main/docs/source/general-faq.rst).

**Cost model.** **Free at the point of use for all University of Oxford researchers**
(standard service level); each project gets standard credits under fair-share (`mybalance`
to check); a paid **priority QoS** exists (`--qos=priority`, purchasable credits) if queues
ever block a gate date. Sources:
[IT Services catalogue entry](https://services.it.ox.ac.uk/Service/research-support/advanced-research-computing),
[priority jobs doc](https://github.com/oxford-arc/arc-user-guide/blob/main/docs/source/arc-priority-jobs.rst).

**Containers.** Apptainer/Singularity **run** is supported (`--nv` for GPU); images
**cannot be built on ARC** — build the SIF elsewhere and copy in. Source:
[ARC Apptainer guide](https://arc-software-guide.readthedocs.io/en/latest/apps/arc_apptainer.html).
This is fine: we convert the *same* pinned OCI image (`requirements-image.txt` digest) to a
SIF off-cluster and record the SIF sha256 — hash-pinning preserved.

**Exact access process for a PhD student (verified against ARC FAQ / IT catalogue / forms):**

1. **Project first.** Access is per-project. Ask the supervisor whether the research group
   already has an ARC project. If yes → skip to step 3.
2. **Supervisor registers a project** (project leaders must be University staff — a PhD
   student cannot lead): the ARC project-registration form at
   [arc.ox.ac.uk/arc-project-registration](https://www.arc.ox.ac.uk/arc-project-registration)
   (a Microsoft Form behind Oxford SSO). ~10 minutes of supervisor time.
3. **Student applies for a user account** against that project via the user-registration
   form (linked from the ARC getting-started pages — note these moved to the Oxford
   intranet/SharePoint in 2025–26, SSO required; start from the
   [University ARC page](https://www.ox.ac.uk/research/support/data-computing/research-computing/advanced-research-computing)
   or the [IT catalogue](https://services.it.ox.ac.uk/Service/research-support/advanced-research-computing)).
   The **project leader approves** the application; credentials (username + temp password)
   arrive by email.
4. **Induction/training:** ARC runs getting-started training (intranet page); not verified
   as mandatory — treat as recommended, ~half a day.
5. **Connect:** SSH from the University network or VPN; external access via
   `gateway.arc.ox.ac.uk` requires registering a **static IP from an identifiable
   institution** ([FAQ](https://github.com/oxford-arc/arc-user-guide/blob/main/docs/source/general-faq.rst)).
   **Caveat for us:** our EC2 box's IP may not qualify as "identifiable institution" —
   fallback drive paths: (a) maintainer's VPN session submits; (b) a cron/agent relay on an
   Oxford-network machine; (c) ask ARC support whether the EC2 /32 is acceptable. Ask at
   step 2 (one email to **support@arc.ox.ac.uk**).
6. **Run:** `sbatch --gres=gpu:1 --constraint=<sku>` on `htc`, partitions short/medium; the
   A100-40GB nodes match our **pinned A100 hardware config** (F0 §3.5), so $/latency
   verdicts stay on pinned hardware; ARC GPU-h are ledgered at $0 actual + Modal-pinned-rate
   *shadow cost* so cross-transport $ comparisons stay honest.
7. **Acknowledge ARC in publications** (ARC policy; goes in P9's boilerplate).

**Lead time estimate:** form → approval → account ≈ **1–3 weeks** (not an official SLA —
start now, it is free). **Capacity honesty:** 16 A100 + 16 H100 shared university-wide
means multi-day queue waits are possible; F5's 100–350 GPU-h of ≤48 h single-GPU jobs fits
the `medium` partition well, but schedule float and keep Modal as the paid fallback for
gate-critical runs (two-transports-one-analysis, P6 discipline).

**What ARC serves:** **Tier 4 (F5) primary-free path; Tier 3 A100 hours; Tier-5 pilot
rungs.** It cannot absorb all of Tier 5's 500–2,500 H100-h — that is what AIRR is for.

### 4.2 UK national / Tier-2 options for the frontier tier

| System | Status & hardware (verified 2026-07-08) | Eligibility for an Oxford PhD student | Route & lead time |
|---|---|---|---|
| **Isambard-AI** (Bristol, AIRR) | UK's largest public AI system: **5,448 GH200** superchips (Hopper GPU, **aarch64** host) | Via AIRR routes; **PhD student cannot be project lead** — supervisor (staff contract outlasting the project) leads, student named as team member | **Gateway route: up to 10,000 GPU-h over 3 months, always open, fortnightly batching, ~1 month submission→access**, light-touch review, priority to first-time AIRR users. Apply via [AIRRPortal](https://portal-airr.isambard.ac.uk/login/); guidance [UKRI Gateway](https://www.ukri.org/opportunity/access-to-isambard-ai-and-dawn-airr-supercomputers-gateway-route/); bigger: [AI Open Access, 50k–1.4M GPU-h](https://www.ukri.org/opportunity/airr-compute-opportunity-ai-open-access/); contact airr@ukri.org |
| **Dawn** (Cambridge, AIRR) | **1,024 Intel Data Centre GPU Max 1550** (PVC); £36M upgrade to AMD **MI355X** landing from spring 2026 | Same AIRR routes as Isambard-AI | Same Gateway/Rapid routes — [hpc.cam.ac.uk/access-dawn](https://www.hpc.cam.ac.uk/access-dawn). **Port warning:** Intel XPU (and soon ROCm) — our CUDA/PyTorch stack needs a backend port; prefer Isambard-AI |
| **JADE2** | **DEAD — access withdrawn 6 Jan 2025, physically decommissioned** | — | Remove from any mental list. Source: [Sheffield HPC docs](https://docs.hpc.shef.ac.uk/en/latest/other-uk-hpc-resources/jade2.html) |
| **Baskerville** (Birmingham) | A100 service (208× A100) superseded; **"Baskerville NCR" (B200) commissioning now, full service early 2027**; access page: "once commissioned…" | Historically EPSRC A2HPC or consortium | **Not a near-term option**; re-check late 2026. [baskerville.ac.uk](https://www.baskerville.ac.uk/), [access](https://www.baskerville.ac.uk/compute/access/) |
| **EPSRC Access to HPC (A2HPC)** — umbrella for Tier-2 (Cirrus, CSD3, Isambard 3, NI-HPC, NICE, HPC Midlands+) + ARCHER2 | Twice-yearly calls; **no call open as of 2026-07-08** (autumn 2025 was the last confirmed; next unconfirmed); ARCHER2 service ends **21 Nov 2026** | UKRI-eligible research org; in practice **supervisor leads**, student is researcher; projects needing <1,000 GPU-h are told to use *exploratory access* at each site instead | Two-stage: technical assessment with the target service, then UKRI form; **~3–6 months end-to-end**. [Cirrus A2HPC page](https://www.cirrus.ac.uk/support-access/access/a2hpc/), [autumn 2025 call](https://www.ukri.org/opportunity/access-to-high-performance-computing-facilities-autumn-2025/), [service spec PDF](https://www.ukri.org/wp-content/uploads/2025/09/EPSRC-090925-A2HPC-2025-1-Service-Specifications-V2.pdf); contact researchinfrastructure@epsrc.ukri.org |

**Frontier-tier arithmetic.** Tier 5's $2–10k envelope ≈ 500–2,500 H100-h at Modal rates.
One **AIRR Gateway award (10,000 GPU-h, free)** covers the *entire* worst case 4× over.
The costs are non-monetary: supervisor-led application (~2–3 h), ~1-month lead, 3-month
use window (fits the GNG-2 → GNG-3 window if timed right), and an **aarch64 port** of our
container image (multi-arch build; CUDA itself is native on GH200). This is the single
highest-leverage funding action available to the programme.

**Reproducibility across backends.** The science is backend-agnostic *by construction*:
model HF revisions, data pack shas, seeds, and the OCI image spec are what's pinned — the
registry records per-transport image digests (x86 Modal, x86 SIF for ARC, arm64 for
Isambard-AI). Numerics can drift across GPU SKUs (A100 vs H100 vs GH200): keep each
experiment's *within-experiment comparisons on one backend* (already GR discipline via
pinned hardware configs) and use alternate backends per-campaign, never mid-campaign.

---

## 5. SET IN MOTION NOW — ordered checklist

Decision points bearing on this: **GATE-T4 ~Sep 25 2026** (F5, $200–800) and **GATE-T5
~Oct 26 2026** (F7/E7, $2–10k). ARC and AIRR lead times are weeks — the free paths only
exist at those gates if started **now**.

| # | Action | Owner | Effort | When | Feeds |
|---|---|---|---|---|---|
| N-1 | **Email supervisor: register an ARC project** (form: [arc-project-registration](https://www.arc.ox.ac.uk/arc-project-registration)); in the same thread ask about existing group projects + departmental GPU boxes; cc/query **support@arc.ox.ac.uk** on (a) A100/H100 queue realities, (b) whether our EC2 /32 can be registered on `gateway.arc.ox.ac.uk` | maintainer (+supervisor ~10 min) | 20 min | **Today** | Tier 3/4 free path |
| N-2 | On project creation: **submit ARC user-account application**; project leader approves; book/skim getting-started training; first SSH login + `mybalance` | maintainer | 30 min + wait | ≤1 wk after N-1 | — |
| N-3 | **Google Cloud Research Credits application** (PhD-student track, up to $1,000, rolling, re-appliable yearly): proposal para + cost estimate + billing account. [Apply](https://edu.google.com/intl/ALL_us/programs/credits/research/) | maintainer | 30–45 min | This week | Tiers 2–4 buffer |
| N-4 | **AWS Cloud Credit for Research application** (student track, ≤$5,000, rolling, 30–120-day review; use a standard non-Free-Tier account, institutional email). [Apply](https://pages.awscloud.com/aws-cloud-credit-for-research.html). Re-poke the G-type vCPU quota (H-9, bead `kernel-of-truth-wve`) in the same sitting | maintainer | 45 min | This week | Tier 4/5 buffer + existing AWS fallback |
| N-5 | Confirm **Modal $30/mo Starter credits** are live on `jmwright-045` and drawn before paid spend; note in `registry/budget.json` that ~$30/mo is pre-funded (I-BUDGET) | agent + maintainer glance | 10 min | At I-BUDGET (Jul 09–15) | Tiers 0–3 |
| N-6 | **File the SLURM/Apptainer transport-adapter bead** (see estimate below). Build AFTER N-2 lands, target green `--mock` smoke on htc `devel` by **end of Aug** | agent | 2–4 agent-days + ~1–2 h maintainer (keys/VPN) | Aug | Tier 3/4 on ARC; reused for AIRR |
| N-7 | **Draft AIRR Gateway application** (agents draft; supervisor is project lead; 10k GPU-h on Isambard-AI; motivate with Tiers 0–3 readouts). Submit **early Sep** so the ~1-month batching lands access **~Oct**, aligned with GATE-T5; 3-month window then covers the F7 campaign. [Guidance](https://www.ukri.org/opportunity/access-to-isambard-ai-and-dawn-airr-supercomputers-gateway-route/) | agent draft + supervisor ~2–3 h | 1 agent-day + 2–3 h human | Draft Aug, submit early Sep | **Tier 5 at $0** |
| N-8 | **arm64 image build** (multi-arch `requirements-image.txt` build + digest recording) — only if/when N-7 is submitted | agent | 0.5–1 agent-day | Sep | Isambard-AI |
| N-9 | Watch-list (no action now): EPSRC A2HPC next call (none open 2026-07-08); NVIDIA Academic Grant window (faculty-led, currently closed); Baskerville NCR (early 2027); AFMR CFP (supervisor-led). One line each in beads with a monthly check | agent | 10 min/mo | ongoing | Tier 5 alternates |
| N-10 | **Decline by default:** TRC/TPU (port ≈1–2 agent-weeks + registry parity gate — not worth it unless F5/F7 outgrow every GPU option), Colab/Kaggle for registry runs (not pinnable), vast.ai interruptible (preemption vs reproducibility) | — | — | — | — |

**Maintainer decisions to log (extends P6 §5.1):** **O-8** adopt ARC as third transport
(needs P6 §1.1 amendment; recommended YES) · **O-9** marketplace adapter as Tier-4
contingency (recommended NO unless ARC+credits both miss GATE-T4) · **O-10** AIRR Gateway
submission (recommended YES, early Sep).

**Harness-porting note (N-6 estimate).** Our harness is Modal-serverless
(`poc/modal/`, `starmap` fan-out, Volumes, staged-manifest assertions). ARC/AIRR are
**SLURM + Apptainer**. The adapter is a third transport under the existing
two-transports-one-analysis discipline (nothing in a runner may branch on transport):
(1) OCI→SIF conversion of the *same* pinned image + sha256 recording (~0.5 day);
(2) `sbatch` templates + job-array fan-out mapping of the RunSpec (~1 day);
(3) staging/collection: `$DATA` replaces Volumes; rsync-pull into `results-incoming/`
with the same provenance sidecars (~0.5–1 day);
(4) `--mock` smoke + one paid-vs-free parity run on a Tier-1-sized workload (~0.5–1 day).
**Total ≈ 2–4 agent-days + 1–2 human-hours.** Results remain comparable because everything
load-bearing is hash-pinned in the container and manifests — the backend only changes *who
is billed*; the ledger carries ARC/AIRR GPU-h at $0 actual with pinned-rate shadow cost.

---

## 6. Recommended strategy

1. **Tiers 0–3 (the decisive-NO band, ≤$900 cap): stay on Modal, drive toward ~$0
   out-of-pocket** with (a) the $30/mo free credits (~$120 over the window), (b) the
   CLI-shift of every shiftable API arm onto the Max20 subscription (metered API →
   $10–50 total), (c) Google's $1k PhD credits if they land (GCP becomes a credit-funded
   overflow transport). Do NOT add marketplace providers here — the $100–300 saving does
   not pay for the plumbing P6 already priced. A decisive H0-NO should cost **≲$400–600
   cash** under this plan (vs $760 worst case unassisted).
2. **Tier 4 (F5, GATE-T4 ~Sep 25): ARC free A100s primary, Modal paid fallback.** Start
   ARC onboarding today (N-1: supervisor-sponsored project — the one action with real lead
   time and zero cost). If ARC queues threaten the gate date, fall back to Modal within the
   $900 cap, or AWS credits if N-4 landed. Expected cash: **$0–800, most likely low
   hundreds**.
3. **Tier 5 (F7/E7, GATE-T5 ~Oct 26): AIRR Gateway (10k GPU-h Isambard-AI) is the plan of
   record**, supervisor-led, submitted early Sep on the back of Tiers 0–3 readouts. It
   covers the whole $2–10k envelope for free; Modal H100 remains the paid fallback (and the
   pinned-hardware reference for $/latency claims). Expected cash: **$0 if awarded; $2–10k
   only if AIRR declines AND the maintainer still wants frontier slopes.**
4. **Tradeoffs, honestly:** spot marketplaces are 40–70% cheaper but trade away
   reproducibility (heterogeneous hosts, preemption) — wrong trade at our scale; the TPU
   port is a 1–2-week detour for hardware we do not need; HPC queues and 3-month AIRR
   windows are real schedule risks — which is why paid Modal stays as the always-available
   fallback at every tier, and why every free path starts onboarding **now**, months before
   its gate.

**Worst-case exposure is unchanged** (caps still bind: $900 + $900 + envelope); this plan
changes the *expected* spend: **Tiers 0–5 ≈ $400–1,400 cash** if N-1…N-7 land, vs
$2.4–11.6k unassisted.

---

*All external figures verified 2026-07-08 against the URLs cited inline. Re-verify volatile
prices (Modal, marketplaces, Colab) at each I-BUDGET; re-check A2HPC calls and the NVIDIA
window monthly (N-9). Cross-refs: P6 §1 (providers), P6 §4 / P1 §5 (tier caps this plan
funds), P3 GR-1 (ledger the shadow costs land in), F0 §3.5 (pinned-hardware discipline that
makes free backends admissible).*
