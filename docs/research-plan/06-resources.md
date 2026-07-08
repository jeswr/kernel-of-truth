# P6 — Resource & infrastructure plan (provisioned up front)

**Status:** resource plan for maintainer sign-off, 2026-07-08. Component P6 of the
operational research plan (`docs/research-plan/`). Governed by
`docs/kernel-design-directives.md` (binding; esp. §3 "RESOURCES provisioned up front —
compute, model access across the scale ladder, data, budget, with concrete access routes").
Consumes P1 (`01-hypotheses-experiments.md` — experiments, rungs, costs, kill-tree), P2
(registry/budget-ledger shapes), P3 (`03-operational-dag.md` — harness, GR-1 caps, D-* data
nodes, gates O-1…O-6), and `docs/design-efficiency-track.md` (F0 accounting standard, §5
scale ladder). **Author:** Fable planning agent (P6), for @jeswr. Coordination:
sparq-org/sparq#1683.

**Native-formalism note (directives §1).** Nothing below provisions any RDF/OWL/SHACL
tooling. The only semantic-web-adjacent artifact in the entire resource plan is G1's
KGE/OWL2Vec\*-style *statistical-baseline arm* (a comparison lens per P1 HS1) — it is an
embedding trained in-house over the concept graph, not an export target, and no triple-store
or reasoner is provisioned anywhere.

**Two principles this plan enforces:**

1. **Nothing blocks silently.** Every resource has (a) a primary access route that exists
   today, (b) a named fallback, and (c) — where a human must act — a `GATE-H` entry in §5
   with the estimated human-minutes. A resource that turns out to need an unplanned human
   action is a plan defect and gets a bead.
2. **Spend unlocks stagewise with the kill-tree.** Money is provisioned as *capacity with
   caps* (Modal per-second billing + the GR-1 ledger), never as pre-paid bulk. The budget
   tiers (§4) are exactly P1 §5's decision tiers; a tier's funds are unlocked only by the
   gate that P3 already defines (GATE-T1, GNG-1, GNG-2, GATE-T4, GATE-T5). No experiment
   can spend ahead of its evidence.

---

## 1. Compute

### 1.1 Providers and access routes

| Provider | Role | Access route (concrete) | Status today |
|---|---|---|---|
| **This box** ("R0") | All Tier-0 experiments (F1, G2–G9, M0b), data authoring, analysis, report-gen | Already running. Constraint honesty: **2 cores shared with a live server** — all heavy work `nice -n 10`'d + checkpointed (house rule); the box is **ephemeral**, so every artifact persists to `jeswr/kernel-of-truth` same-session | READY |
| **Modal** (primary GPU) | All Tier-1–4 GPU runs; Tier-5 default | Profile `jmwright-045`, token in `~/.modal.toml` (outside repo); harness `poc/modal/` (validated: E2/E5/E9 full runs + E1/E4 scaffold landed under this profile); pinned image from `requirements-image.txt` (py 3.11); HF weights cached in Volume `kot-hf-cache`; per-campaign Volumes `kot-<exp>-work` | READY pending I-MODAL re-verify (token liveness check; CRED-GATE = `modal token new`, ~3 min, if expired) |
| **AWS EC2** (secondary GPU) | Fallback if Modal is down; optionally cheaper spot for long serial training grids (F5/F6/F7) | `poc/gpu/` Option B pull path (no standing credentials; launcher + collector scripted, SG scoped to this box's /32). **Blocker:** GPU vCPU quota currently 0 (`VcpuLimitExceeded`, bead `kernel-of-truth-wve`) — needs a quota escalation for G-type (8 vCPU ⇒ g5.xlarge) and, only if Tier 5 goes AWS, P-type | BLOCKED on quota (non-critical: Modal needs no quota) |
| **No other providers.** | — | Adding one (Lambda, RunPod, …) would need new credential handling, image work, and provenance plumbing for at best marginal $ savings at this programme's scale. Rejected. | — |

**Two transports, one analysis** (established discipline): both run the SAME committed
runners on the SAME committed inputs into the same `results-incoming/` review flow; nothing
in a runner may branch on transport. A Modal outage reroutes to AWS at ~2–3 days' notice
(quota permitting) with zero analysis changes.

### 1.2 Planning rates (pinned per run, planned here)

Per-second Modal billing; the **actual** $/hr is read from the Modal pricing page at
I-BUDGET time and pinned into `registry/budget.json` and every RunSpec (`worst_case_usd` is
computed from the pinned rate — F0 §3.5 rule). Planning rates used for the tables below
(2026-07 list-price ballpark; conservative side):

| GPU | Modal planning rate | AWS fallback (on-demand) | Used for |
|---|---|---|---|
| T4 (16 GB) | ~$0.6/h | g4dn.xlarge $0.53/h | inference ≤360M (F2 small rungs, E9) |
| A10G (24 GB) | ~$1.1/h | g5.xlarge $1.01/h | default: 1.7B inference; adapter/SAE/toy training (F3/F4/F6-toy/E8) |
| A100-40GB | ~$2.1–2.8/h | p4d spot (quota-gated) | controlled training T1/T2 (F5, F6-T2), E7/F7 training rungs |
| H100 (80 GB) | ~$4/h | — | Tier-5 only, and only if the sized `--dry-plan` shows it beats A100 on $/run |

Rule inherited from F0 §3.5: latency/$ numbers quoted in verdicts come from **pinned
hardware configs**, not from whatever GPU happened to be free; the T4 and A10G configs are
the pinned reference hardware for inference claims.

### 1.3 GPU type, hours and $ per experiment (the compute table)

Estimates are sized from validated priors: E1-class 15–35-way Modal fan-out ≈ 5–6 h wall;
E5 adapter training ≈ single-digit A10G-hours; F5 arithmetic from 6·N·tokens (160M × 2B
tokens ≈ 1.9e18 FLOPs ≈ 4–5 A100-h/run at ~40% MFU; ×6 arms ×5 seeds ⇒ low-hundreds of
A100-h worst case — matches the track's own sizing). Every campaign additionally pays one
`--mock` transport smoke (~pennies; GR-13 mandatory).

| Exp (hypotheses) | Rungs | GPU | Est. GPU-h | Est. $ | Tier / cap it draws on |
|---|---|---|---|---|---|
| M0b coverage; F1; G2/G3/G5/G6/G7 | R0 | none (CPU, this box) | — | ~$0 | Tier 0 (≤$15 total, API only) |
| G4 decode-legibility; G8 Lean location; G9 authoring | R0 + API | none | — | $0–20 API | Tier 0 |
| **F2 + PRM arm** (HE1, HE2, HC3, HS12) | (R1,R2) T4; R3 A10G | T4 + A10G | 15–40 | **$10–60** | Tier 1 (cap $80) |
| E9-full + E9-C (HC1, HC2, HS11-part) | R1, R2 | T4 | 25–80 | $20–100 | Tier 2 (cap $320) |
| F4 + G1 (HE4, HS1) — incl. second-family adapter train | R1–R3, 2 families | A10G | 30–90 | $40–140 | Tier 2 |
| E8-R → E8-D (HC4) — SAE fitting dominates if no public dict | 125M–160M fams (+1 ≥1B pair cond.) | A10G | 25–100 | $30–120 | Tier 2 |
| F3 + M2-output rider (HE3, HS10) | R1–R3 hosts | A10G | 45–150 | $50–170 (rider ≤$20 inside) | Tier 3 (cap $400) |
| F6 toy/T1 (HE6) — E1-pipeline reuse + text-scaffold arm | T0, T1 | A10G (toy), A100 (T1) | 30–80 | $50–150 | Tier 3 |
| F5 (HE5-full, HS9, HS11) — from-scratch controlled training | T1, T2 (T3 cond.) | A100-40GB | 100–350 | **$200–800** | Tier 4 (cap $900; GATE-T4) |
| F7 ≡ E7 (HE7, HC5, HS13) — survivor slopes; R5/T3 rungs | R1–R4/R5; T0/T2/T3 | A100/H100 + A10G | sized at GATE-T5 via `--dry-plan` | **$2–10k** | Tier 5 (approved envelope; GATE-T5) |

Cross-check: Tiers 0–3 sum to ≈ **$180–650**, matching P1 §5's pre-gate budget line; the
GR-1 cumulative cap for Tiers 0–3 is $700. Storage rider: Modal Volume storage (HF cache
~20–60 GB + per-campaign work volumes) is a ledger line, estimated <$10/month, volumes
deleted at campaign close-out (P3 §3.5).

### 1.4 Provisioning steps (compute)

Executed as P3 nodes I-MODAL / I-BUDGET during Phase P-0 (Jul 09–15):

1. **Modal (AUTO unless token dead):** `bash poc/modal/validate.sh` (recreates the pinned
   client venv) → confirm `~/.modal.toml` has a live token for `jmwright-045` (if not:
   CRED-GATE, maintainer runs `.venv/bin/modal token new`, ~3 min) → rebuild/confirm the
   pinned image from `poc/modal/requirements-image.txt`, record hydrated image id →
   inventory Volumes (`kot-hf-cache` present; create `kot-<exp>-work` lazily per campaign)
   → one `--mock` ping end-to-end (staged-manifest assertion + provenance sidecar checked)
   → write transport-ready record.
2. **Modal spend controls (GATE-H, one dashboard visit):** set the account-level spend
   limit/alert to the Tiers-0–3 envelope (≤$700) so the platform-side cap agrees with the
   GR-1 ledger; raised only at GATE-T4/GATE-T5 alongside the ledger cap.
3. **Budget ledger (I-BUDGET):** initialise `registry/budget.json` with the GR-1 cap table
   (maintainer confirms values = open decision O-1); deploy the hourly cost-monitor
   (polls Modal spend + ledger; breach ⇒ kill switch per GR-1/GR-14); smoke-test the kill
   switch against a dummy ledger breach.
4. **AWS (optional, non-blocking; O-4):** re-poke the quota escalation on bead
   `kernel-of-truth-wve` (Service Quotas: "Running On-Demand G and VT instances" ≥ 8 vCPU;
   spot G quota likewise). No standing credentials are minted either way (Option B pull
   path only; Option A deploy-key path stays retired per GR-11).
5. **R0 discipline check:** confirm `nice` + checkpoint conventions in every Tier-0 runner;
   confirm no Tier-0 job holds the box's cores un-niced (CSS box constraint).

---

## 2. Model access

### 2.1 Scale-ladder models (open-weight, revision-pinned)

All models are open-weight HF checkpoints. **Pinning rule:** at each campaign's `X.inputs`
stage the exact HF **revision (commit sha)** is resolved, recorded in the campaign manifest
and the registry entry, and downloaded into `kot-hf-cache`; runs assert the revision
in-container (same fail-closed pattern as staged bytes). Planning table:

| Rung | Model (HF repo id) | Params | License / gating | Used by |
|---|---|---|---|---|
| R1 | `HuggingFaceTB/SmolLM2-135M-Instruct` (+base for E8-family-C) | 135M | Apache-2.0, ungated | F2, E9, F3, F4, G1, E5-adapter reuse |
| R2 | `HuggingFaceTB/SmolLM2-360M-Instruct` | 360M | Apache-2.0 | F2, E9, F3, F4 |
| R3 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 1.7B | Apache-2.0 | F2 (incl. cascade target), F3, F4, F7 |
| R4 (replication family) | `Qwen/Qwen2.5-0.5B-Instruct`, `-1.5B-Instruct`, `-3B-Instruct` | 0.5/1.5/3B | 0.5B & 1.5B Apache-2.0; **3B under the Qwen Research License** (research use OK; noted in the registry entry so no verdict implies unrestricted redistribution) | G1 second family; F7 family replication; HC5 |
| R5 (gate-kept) | default `Qwen/Qwen2.5-7B-Instruct` (Apache-2.0, ungated); alt `meta-llama/Llama-3.1-8B-Instruct` (gated — needs HF license click-through, a GATE-H) | 7B-class | default choice avoids any gate | F7 only |
| T1/T2/T3 | `EleutherAI/pythia-70m(-deduped)`, `pythia-160m(-deduped)`, `pythia-410m(-deduped)`; T3 alt `pythia-1b/-1.4b` configs | 70M–1.4B | Apache-2.0; revision-pinned suite with public data order (the point of choosing Pythia) | F5, F6, E7/HS13 (configs trained from scratch on controlled corpora — we pin the *configs and suite revision*, weights only where continued-pretraining arms need them) |
| E8 families | `openai-community/gpt2` (124M), `EleutherAI/pythia-160m`, `HuggingFaceTB/SmolLM2-135M` (already pinned in `poc/e8/inputs/e8-manifest.json`) + one **third family** for E8-R (candidates in §3 D-SAE) | 124–160M | all ungated | HC4 |

Default posture: **every default model on the ladder is ungated** — no license
click-through sits on the critical path. The two exceptions (Llama-3.1 alt for R5;
Gemma if Gemma Scope SAEs are chosen for E8-R) are alternatives that trigger an explicit
GATE-H if selected.

### 2.2 API / multi-LLM needs (metered, small, capped)

Agent labor (Kern coordinator + Fable runner/auditor subagents) rides on the existing
Claude accounts (main + backup for auditor identity separation, O-5) and is **not** on the
$ ledger. Metered API calls inside experiment pipelines are, and they are small:

| Need | What for | Models/providers | Route | Est. $ |
|---|---|---|---|---|
| Authoring (G9 / HS-A) | N≥50 machine-authored explications through the validator loop | Fable-5-class (Anthropic) — the "our best author" arm; model id + params recorded per explication | In-session agent authoring with recorded model id (default), or `ANTHROPIC_API_KEY` for scripted reproducibility (either is acceptable; the registry records which) | $0–10 |
| **DeepNSM comparison metrics** (G9) | Legality / substitutability / cross-translatability scoring per Baartmans et al., reused as-is | DeepNSM-8B artifacts if published on HF (checked at G9.inputs; else compare against **published point estimates only** — exactly what HS-A pre-registers, Wilson-bound vs published number) | HF download (free) or literature numbers | $0 |
| **Proposer-invariance check** | Guard that authoring/decode-legibility results aren't one-provider artifacts: G4's decode-legibility probe and G9's authoring get one **second-provider** replication arm (descriptive secondary, not a new primary endpoint) | One non-Anthropic API: OpenAI (gpt-4o-mini-class) or Google (gemini-flash-class) — maintainer picks at O-7 | New API key, monthly hard cap $25 at the provider dashboard | $5–25 |
| G8 Lean location probe | top-5 concept-location over 1,000 Mathlib declarations | small frontier model via API | existing Anthropic route | $0–10 |
| haiku-tier authoring (bulk kernel, feeds M0b/D-DOM if drawn on) | already-established pipeline | claude-haiku (existing) | existing | inside Tier-0 API cap |
| Leak-checked judge fallback | E5-discipline scorers are non-LLM rubrics first; judge only where pre-registered | small model, leak-checked per E5 discipline | existing | inside campaign caps |

Total API budget across the programme: **≤ $50–75**, inside the Tier-0/Tier-2 caps it is
billed against. No fine-tuning APIs, no hosted-training services — all training is
open-weight on our own metered GPUs (auditability requirement).

### 2.3 Other model artifacts

- **PRM arm (HC3/F2+PRM):** one off-the-shelf small process/outcome reward model, e.g. a
  math-shepherd-class or Qwen-PRM-class ≤1.5B open checkpoint — selected and revision-pinned
  at F2.inputs with its selection rationale in the registry (choice is itself an arm
  definition; GR-10 parity applies). Ungated candidates exist; no gate expected.
- **Embedding/retrieval for RAG arms (F2 arm 6, F5 arm 3):** BM25 (pure CPU) primary;
  if an embedding retriever is pre-registered, a small ungated open embedder (e.g.
  BGE-small-class), revision-pinned. No hosted retrieval services.
- **xRAG-style trained compressor (F3 arm 5):** trained in-house at the matched adapter
  budget — no external artifact needed.
- **int4 quantization (F2 arm 9, F5 arm 4):** GPTQ/AWQ tooling inside the pinned image;
  quantized artifacts hashed and cached per campaign.

---

## 3. Data

### 3.1 Already in-repo (hash-pinned, ready)

| Corpus | Path | Feeds |
|---|---|---|
| Kernel v0 (54 records) + minted URNs | `data/kernel-v0/` | G2/G5, D-QA, F2, encoder pins |
| WordNet 3.1 extraction (117,791 records + alignment + reachability) | `data/lexical-wn31/` | F1 (byte ledger — 2.90 B/rec measured), D-QA, D-ST, F5 knowledge corpus |
| Molecule tier v0 | `data/molecules-v0/` | D-AX axiom set, HC2 litmus family |
| Metamath sector (definitions/axioms/syntax + alignment) | `data/math-mm/` | HS8 identity baseline, math-v0 |
| Lean sample + math-v0 | `data/math-lean-sample/`, `data/math-v0/` | G8/D-ML seed (the 1,000-declaration crawl extends this) |
| Physics sector (QUDT-derived + v0) | `data/physics-qudt/`, `data/physics-v0/` | coverage (M0b), sector regression |
| Ontology comparison sets (FrameNet, OBO, SUMO) | `data/onto-*/` | M0b coverage denominators; G1 concept-graph baseline material |
| haiku-tier (modelAuthored inventory + fetch pipeline, Wiktionary/Wikipedia pinned) | `data/haiku-tier/` | D-DOM candidate source; bulk-authoring cost priors for HS-A framing |
| E8 inputs (3 families, SAE manifests) | `poc/e8/inputs/` | E8-R baseline |
| TinyStories concept pipeline (E1) | `poc/e1/` + `poc/dist-corpus` | D-TS rebuild |

### 3.2 To build (P3 D-* nodes — the new eval sets), with sources

All builds are AUTO, deterministic where possible (seeded generators), and land as
hash-pinned packs referenced from registry entries. Anything an arm consumes is built
*before* the registry entry freezes (P2 P-1).

| Pack | Contents | Source / method | Consumed by |
|---|---|---|---|
| **D-QA — kernel-covered definitional QA** | E5-style slot-filling + forced-choice usage items on kernel-covered concepts, plus a **non-covered control slice**; gloss corpus + RAG index for the text/RAG arms; leak-checked | Generated from `data/kernel-v0` + `data/lexical-wn31` records (glosses = the text arms' corpus); leak checks per E5 discipline; M0b coverage number computed first (D-QA depends on M0b.run) | F2, HC3, F7 slices |
| **D-IR — factual-correctness / violation corpus** | ≥300 seeded instance records with **planted** cardinality/disjointness/domain violations at known rates over the litmus family (human/parent/sex, bookmark/maker, promise/parties) + molecule-tier axioms; clean-record control set for the FP bound | Seeded generator (seed + rates in registry); axioms from D-AX | E9-C (HC2), HS11 |
| **D-GL — long-glossary sets** | QA/consistency items needing d∈{4,16,64} in-context definitions; matched-token compressed + truncated text variants | kernel-v0 concepts first, wn31-backed second; compression variants built with a pinned summarizer | F3 (HE3) |
| **D-DOM — onboarding domain** | ≥50 held-out new concepts: validated explications, minted URNs, vectors under pinned encoder `40e8c8ba…`, JL-projected per X4 pins | Authored via the validator loop (haiku-tier pipeline reusable); disjoint from adapter training data | F4 (HE4), G1 |
| **D-CB — G1 arm artifacts** | (a) random-atom-codebook encoder fork (own ALGORITHM_VERSION label + own goldens, never mutating mainline); (b) **ConceptNet Numberbatch** vectors (public download, ~2 GB, en subset) mapped through the same adapter protocol; (c) KGE/OWL2Vec\*-style embedding trained in-house over the same concept graph (comparison lens only) | Numberbatch: github.com/commonsense/conceptnet-numberbatch (version pinned + sha'd at download); KGE trained on A10G inside G1's cap | G1 (HS1) |
| **D-SAE — E8-R third family** | Residual-stream, **site-matched** SAE dictionaries + seed-stability stratification (Paulo–Belrose) | Preference order: (1) public residual-stream SAEs for an ungated family — EleutherAI Pythia SAE suites / SAELens-published GPT-2-residual dictionaries; (2) Gemma Scope (gemma-2-2b residual) — **triggers HF license click-through GATE-H if chosen**; (3) fit our own on an ungated family (cost inside E8's $30–120 cap; the cap was sized for this) | E8-R (HC4) |
| **D-ML — Mathlib sample** | 1,000 random declarations, pinned to one mathlib4 commit | Crawl of `leanprover-community/mathlib4` at a recorded commit sha (extends `data/math-lean-sample/`) | G8 (HS8) |
| **D-TS — scaffold corpus** | Concept-heavy TinyStories + concept augmentation (E1 AMENDMENT A1 pipeline, parity-gated mapper port) + the **explication-text-interleaved** data-arm corpus | HF `roneneldan/TinyStories` (CDLA-Sharing-1.0, ungated) + kernel explications | F6 (HE6), E7 |
| **D-ST — store corpora** | 10³/10⁵/10⁶-record stores + byte-matched compressed text stores (zstd-JCS discipline from F1) | Built from `data/lexical-wn31` (+haiku-tier records if coverage requires); gated on F1.verdict | F5 (HE5) |
| **D-AX / D-AXN — axiom corpora** | ~20-axiom working set in kot-axiom/1 and (after G2's residue list) the same set in NSM-native syntax by two independent author-agents | Authored in-repo; effort logs kept for G4 | HC2, G4/G6/G7 |
| **DeepNSM eval (G9)** | N≥50 machine-authored explications + validator scores + blinded human review sheet; DeepNSM published metric definitions reused as-is | Baartmans et al. (DeepNSM) paper metrics; HF artifacts if released; annotation sheets contain no credentials (GR-11) | G9 (HS-A) |

**External-download ledger:** the only third-party downloads in the whole plan are
Numberbatch (~2 GB), TinyStories (~1 GB), mathlib4 (git, shallow), public SAE packs
(1–20 GB), and HF model weights (all cached once in `kot-hf-cache`). Each is
version/sha-pinned at fetch (existing `data/*/manifest.json` discipline) — no live-service
dependency at run time.

---

## 4. Budget tiers mapped to the go/no-go tree

Structure: three headline tiers for the maintainer's mental model, implemented as the five
GR-1 ledger tiers. **Spend never runs ahead of the tree:** each block of money is unlocked
by a machine-checked or human gate that already exists in P3, and a kill upstream *prunes*
downstream spend automatically (e.g. F1-kill makes GATE-T4 unsatisfiable ⇒ the $200–800
never leaves the wallet).

### Tier CHEAPEST-DECISIVE (~$40 spend; caps $95) — "is the best-supported mechanism real?"

- **Contents:** all of Tier 0 (R0: F1, G2–G9, M0b; ≤$15 API) + **Tier 1: F2 + PRM arm**
  ($10–60, cap $80).
- **Unlock:** GNG-0 (registry freeze signed) then GATE-T1 (machine-checked: M0b published ∧
  F0 tests green ∧ Modal ready ∧ ledger headroom).
- **What the money decides:** the pivot readout GNG-1. F2 PASS ⇒ H0-YES is reachable and
  Tier 2 is funded aggressively. F2 clean-kill at both rung pairs ⇒ M1+M5 (the
  best-supported efficiency mechanisms) are dead and the efficiency thesis shrinks to
  M6+M4-verifiability — the maintainer learns this for ~$40. Structure forks HS2–HS8
  resolve here for ~$0 either way.

### Tier MID (~$200–800 spend; caps $720 cumulative Tiers 0–3, +$900 Tier 4) — "resolve H0 and the mechanism map"

- **Contents:** Tier 2 (E9-full+E9-C, F4+G1, E8-R→E8-D; $90–360, cap $320) + Tier 3
  (F3 incl. M2-output rider, F6 toy/T1; $100–320, cap $400). Conditionally Tier 4
  (F5; $200–800, cap $900) if and only if F1 passed AND F3 settled the injection route
  AND the maintainer approves GATE-T4 (~Sep 25 with the GNG-2 dossier).
- **Unlock:** Tier 2/3 open after GNG-0 regardless of F2 (the correctness track is not
  blocked by the efficiency pivot — GNG-1 is informational for it); Tier 4 is double-gated
  as above.
- **What the money decides:** every input to the **global decision tree (P1 §6)** at GNG-2:
  TAKE-TO-FRONTIER-LAB / NARROW-AND-CONTINUE / PIVOT / KILL. A decisive H0-**NO** — every
  mechanism TOST-killed against its text null — costs ≈ **$180–650 all-in**, and per the
  directives that negative is written up at full prominence (P9), not buried.

### Tier FRONTIER (~$2–10k, hard-gated) — "the only tier that licenses scale adjectives"

- **Contents:** Tier 5: F7 ≡ E7 (HE7 efficiency slopes, HC5 correctness slope, HS13 A1-at-
  scale iff F6 showed a vector-arm signal). R5/T3 rungs each get a sized `--dry-plan` and
  their own ledger line before launch.
- **Unlock:** GATE-T5 — explicit maintainer budget sign-off, never started without it;
  requires survivors from Tiers 0–3 (P1 hard ordering: {F2, E9, F4, F6} readouts ≺ any F7
  spend).
- **What the money decides:** the ≥3-rung slopes that P1 §4b requires before ANY scale
  adjective or frontier pitch; GNG-3 final disposition. If GNG-2 routed to PIVOT or KILL,
  this tier is never funded — the $2–10k is contingent capacity, not a commitment.

**Worst-case total exposure by route:** kill-at-GNG-1 ≈ $55–95; kill-at-GNG-2 ≈ $180–650;
full run to GNG-3 ≈ $2.4–11.7k. All spend on per-second billing — there is no sunk
pre-purchase at any point.

---

## 5. Human & credential gates + the Phase-1 provisioning checklist

### 5.1 What only the maintainer can supply (the GATE-H inventory)

| # | Gate (P3 ref) | What @jeswr does | Effort | When |
|---|---|---|---|---|
| H-1 | **Budget caps (O-1, I-BUDGET)** | Confirm/adjust the GR-1 cap table (Tier 0 ≤$15 · T1 ≤$80 · T2 ≤$320 · T3 ≤$400 · cumulative ≤$700 · T4 ≤$900 · T5 = approved envelope) + set the Modal dashboard spend limit to match | one message + one dashboard visit | before GNG-0 (target Jul 15) |
| H-2 | **Modal credential (CRED-GATE)** | Only if the `jmwright-045` token is dead: `modal token new` pairing; confirm a billing method is attached to the account | ~3 min | P-0, only on failure of I-MODAL |
| H-3 | **Registry freeze signature (GNG-0)** | Sign the registry root sha (all 26 entries + caps) | ~30–60 min review | Jul 15 |
| H-4 | **Annotator sourcing (O-3)** | Decide who annotates: G3 needs 2 independent annotators ~8–10 h; G2 gold ~3 h; G9 blinded review ~4 h; M0b slice ~2–4 h (≈ 20 h total). Options: (a) maintainer + one colleague, $0; (b) paid platform (Prolific-class), ≈ $300–600 incl. platform fees — if (b), that line is added to Tier 0's cap | decision + either ~20 h of human time or ~$300–600 | P-1 (annotation starts ~Jul 13) |
| H-5 | **Second-provider API key (O-7, new)** | Pick OpenAI or Google for the proposer-invariance arm; mint one key; set a $25 hard cap at the provider | ~10 min | before G4/G9 run (Jul) |
| H-6 | **Auditor identity (O-5)** | Confirm the backup Fable account is used for Tier ≥2 positive audits (hard run-vs-audit separation) and that its credentials are live | ~5 min | before first Tier-2 audit (Aug) |
| H-7 | **GATE-T4 approval (O-6)** | $200–800 for F5, decided on the GNG-2 dossier | one decision | ~Sep 25 |
| H-8 | **GATE-T5 approval** | $2–10k envelope for F7/E7, on the GNG-2/M4 evidence | one decision | ~Oct 26 |
| H-9 | **AWS quota (O-4, optional)** | Re-poke the vCPU quota escalation (bead `kernel-of-truth-wve`) if spot savings on F5/F6/F7 are wanted; otherwise skip — Modal suffices | ~10 min (console request) | any time; non-blocking |
| H-10 | **Gated-model licenses (conditional)** | Only if E8-R selects Gemma Scope (accept Gemma license on HF) or R5 selects Llama-3.1 (accept Llama license). Defaults avoid both | ~5 min each, only if chosen | at D-SAE / GATE-T5 |

Everything else in the programme — data builds, encoder forks, eval-set generation, Modal
runs, logging, audits, verdicts, reports — is agent-executable within these gates and the
standing GR-1…GR-14 guardrails.

### 5.2 Provisioning checklist — must be all-green before Phase-1 (first annotator hour / first data-pack freeze), and items 1–12 before the first GPU dollar (GATE-T1)

```
COMPUTE
[ ] 1.  poc/modal/validate.sh green (client venv pinned, rebuilt if needed)
[ ] 2.  Modal token live for profile jmwright-045 (~/.modal.toml; CRED-GATE if not)
[ ] 3.  Pinned image rebuilt from requirements-image.txt; hydrated image id recorded
[ ] 4.  Volume inventory: kot-hf-cache present; per-campaign volume naming confirmed
[ ] 5.  --mock transport smoke green same-week (staged-manifest assertion observed)
[ ] 6.  Modal dashboard spend limit set = Tiers-0-3 envelope (<=$700)   [H-1]
[ ] 7.  registry/budget.json initialised with confirmed GR-1 caps        [H-1]
[ ] 8.  Hourly cost-monitor deployed; kill switch smoke-tested against a dummy breach
[ ] 9.  Kill-switch inventory documented + tested (modal app stop; gpu/terminate.sh)
[ ] 10. Planning $/hr rates read from Modal pricing and pinned into the ledger
MODELS
[ ] 11. HF revisions resolved + recorded for SmolLM2 135M/360M/1.7B (instruct+base),
        Qwen2.5 0.5B/1.5B/3B, Pythia 70M/160M/410M(-deduped), gpt2, pythia-160m
[ ] 12. Weights pre-warmed into kot-hf-cache (first-run download paid once, off the clock)
[ ] 13. PRM checkpoint candidate list drafted for F2.inputs (selection rationale template)
[ ] 14. Second-provider API key minted, $25-capped                       [H-5]
[ ] 15. DeepNSM artifact availability checked (HF) — else published-numbers route noted
DATA
[ ] 16. All data/*/manifest.json shas verified against the repo (validate.mjs green)
[ ] 17. External-download pins recorded: Numberbatch version, TinyStories revision,
        mathlib4 commit, SAE pack source decision (D-SAE preference order walked)
[ ] 18. M0b coverage run scheduled (blocks D-QA/D-GL; required before any verdict quote)
[ ] 19. Encoder pin confirmed: 40e8c8ba... unchanged; X0 goldens green on this box
GOVERNANCE
[ ] 20. Registry (I-REG) seeded: 26 entries, verbatim kill text, cost caps per entry
[ ] 21. F0 harness (poc/f0/) tests green (flop-meter, byte ledger, latency, $/query)
[ ] 22. Audit kit (I-AUDIT) ready; auditor identity confirmed             [H-6]
[ ] 23. Annotator plan settled (who, hours, blinding materials)           [H-4]
[ ] 24. GNG-0 signed: registry root sha + caps                            [H-3]
[ ] 25. This plan (P6) committed + pushed; beads mirror updated (work isn't done
        until pushed - box is ephemeral)
```

### 5.3 Standing failure modes and their provisioned answers

| Risk | Provisioned answer |
|---|---|
| Modal outage / account issue mid-campaign | AWS pull path (`poc/gpu/`) runs the same committed runners; quota re-poke is H-9; 2–3 day reroute, analysis unchanged |
| Token/credential leak | GR-11 hygiene (token outside repo, redact_env, no deploy keys); nuclear option `modal token revoke` (GATE-H) in the kill-switch inventory |
| Cost overrun / runaway job | Per-RunSpec `worst_case_usd` refused above headroom (ERR_BUDGET); hourly monitor + platform spend limit + per-container hard timeouts; GR-14 kill switches |
| Annotators unavailable (the main P-1 schedule risk) | G3/G2/G9 materials are build-complete before annotators start (zero idle annotator time); paid-platform fallback pre-costed in H-4; annotation-dependent nodes carry float in the P3 timeline |
| Gated model/SAE needed unexpectedly | Preference orders in §2.1/§3.2 keep ungated defaults on the critical path; any gate escalates as a named H-10 with a same-day maintainer action |
| Rate-limit fleet kill (happened twice) | ≤5 concurrent agents (GR-3); parallelism inside Modal `starmap` containers, not agents |
| This box dies | Everything of value is in `jeswr/kernel-of-truth` (GR-12); Modal volumes hold only re-derivable caches + checkpoints |

---

*Cross-references: P1 §5 (tier costs this plan funds), P2 §1 (budget ledger schema), P3 §§3–4
(harness + GR guardrails this plan provisions for), `design-efficiency-track.md` §3.5 (pinned
hardware/$ discipline). Open decisions for the maintainer are consolidated in §5.1; the
Phase-1 gate is checklist §5.2.*
