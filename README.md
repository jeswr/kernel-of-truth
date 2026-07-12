# A Kernel of Truth

**Research programme: an authoritative, training-free "kernel" of formalised concepts with canonical vector representations, as a component of future LLM/LCM architectures.**

Status: active research, launched 2026-07-07. Lead agent: **Kern** (Claude Fable 5), on behalf of [@jeswr](https://github.com/jeswr).
Coordination thread: [sparq-org/sparq#1683](https://github.com/sparq-org/sparq/issues/1683).

## The hypothesis

If concepts are formalised as structured explications over a small closed basis (NSM's ~65 semantic primes, per the [content-addressed concepts design](https://gist.github.com/jeswr/7499faa6fcbfe8ee1e3192d05e82e9ad)), then the same formal structure that yields a canonical **content-hash** for each concept can also yield a canonical, **deterministically computable vector representation** — a function of the concept's prime-decomposition, requiring no training.

A well-built kernel of such concepts could become central to the architecture of future LLMs, LCMs, and their descendants:

1. **Accuracy** — kernel concepts are built in, not learned; the model can never misunderstand them and their representation can never drift.
2. **Training efficiency** — the model never spends capacity or data learning what the kernel already fixes.
3. **Train/inference efficiency** — dense concept-level I/O: a single concept vector carries what many tokens carry today, both on input and output.
4. **Longer term** — GNN-style non-linear concept input/output, and cheap rules-based inference over kernel concepts inside the architecture as a shortcut past heavy weight evaluation.

Adjacent artefacts: a **phrase→concept mapping layer** (from tokens / token-space regions to fixed kernel concepts), and a **world layer** above the kernel — formally described facts about the state of the world expressed *in terms of* kernel concepts (the kernel holds "a person"; the world layer holds "Jesse as a person").

The near-term goal is a proof-of-concept on small local models rigorous enough to take to a frontier lab.

## Experiment summary (as of 2026-07-12)

The programme puts two theses under pre-registered test. **CORRECTNESS**: that a training-free, meaning-grounded *kernel* — machine-readable concept definitions plus a deterministic checking engine — can supply correct answers and inferences a language model cannot be trusted to produce alone. **EFFICIENCY**: that such a kernel lets a small model offload verification to cheap deterministic machinery, or lets a model be shrunk without retraining. Every claim below is capped at its registered verdict or licensed interpretation; **neither thesis has a verdict — both remain inconclusive-pending** ([synthesis v5](docs/next/feasibility-synthesis-v5.md), ASM-1380).

### Experiments run

- **f2b-transfer** — does a kernel-authored answer key, checked through a thin verify-retry interface, help a small (135M) model on independently adjudicated questions? **PASS, audit-confirmed.** The key lifted the model **+0.25** accuracy, with 96% of rendered content externally endorsed; the boosted 135M was *not* shown to match a 1.7B model.
- **DECONF-B** — what carries that lift? **PASS, audit-confirmed.** The item-aligned answer-bearing *content* carries it: a generic aligned store reproduced the kernel arm exactly, so **no kernel-specific runtime structure** is measured at this seam — a deflationary result, reported with equal weight.
- **CASC-0′** — does kernel-style structured prompting disproportionately help a smaller reasoner at matched compute? **INSTRUMENT-INVALID** (compute-matching gate missed its band). The raw interactions showed no positive sign and kernel-style gloss was equivalent to a plain typed dialect — but no overall verdict, neither "works" nor "null", is licensed.
- **g2** — are the kernel's hand-authored *hard* type constraints sound by ordinary-meaning standards? **INSTRUMENT-INVALID** (84 items < the registered 500), with a strongly adverse signal: only ~39% judged sound. LLM-proxy labels; human reconciliation pending.
- **g2-import** — does importing *soft*, non-binding typing from published ontologies (BFO/SUMO/FrameNet) repair that? **INSTRUMENT-INVALID**: soundness nearly doubled (57/84 vs 33/84) — a GO-*shaped* signal, not a licensed GO — because the judge pair went unstable on exactly the adoption arm (κ = 0.29). Caveat: follow-up analysis confirms part of the low κ is the known kappa paradox (high-prevalence penalty), yet also shows the judge pair genuinely shares little signal — the invalidation stands, while the soundness gradient itself is bracket-robust. A breadth-only control also lifted, so the ontologies' *specific* content is not yet shown to carry the effect. All numbers LLM-proxy-provisional.
- **RULES-1 CPU certificate** — can a deterministic rules engine over kernel-expressed worlds compute correct conclusions that flat lookup of stated facts cannot? **PASSED (registered certificate).** Entailed decisions were reproducible from no stated-bytes projection (0/3,680) while stated-fact behaviour was exact (1,716/1,716); the engine matched third-party CLUTRR gold 858/858 and refused correctly on missing premises, in <2 s at ~$0. This licenses *machinery non-inertness only* — not host lift, not kernel-specific value.
- **RULES-1 host-lift, GPU runs 1–3** — do those derivations help a small model answer? **The instrument has never validated — three consecutive failures.** Run 1 (rules-1) VOIDED (direction-ambiguous cue); rules-1-b refused pre-launch (host prompt-frame diverged, host models at 0); rules-1-c ran the full 4-way campaign but graded **INSTRUMENT-INVALID** — the entity-form fix restored host-validity (A5 0.94, A7 1.00) yet a 2-option surface made the verify-retry channel *vacuous* (A3 ≡ control, every retry `attempts=1`). The surface that elicits the gold and the surface that engages the verifier pull against each other; the slot's next move is a maintainer decision ([issue #24](https://github.com/jeswr/kernel-of-truth/issues/24)).
- **Built / in progress:** g2-import-v2 (authoritative GPT-5.6 + Haiku judging in progress on the AC1-gated instrument), DDC (training-free kernel-guided compression — harness complete + mock-green + LAW-1 verified, T0 corpora-pinning underway toward the first *efficiency* datum), the large-kernel scale track (10k first rung measured — see below), and the sparq upstream PRs.

### Key findings so far

- Kernel-authored content can be externally useful: an aligned answer key plus cheap deterministic verify-retry lifted a 135M model +0.25 on external gold *(measured, verdict-grade; f2b-transfer, DECONF-B)*.
- The measured value sits in the content, not in kernel-specific runtime structure — and static kernel-style prompting showed no positive sign at its (invalidated) test *(measured, deflationary; DECONF-B, CASC-0′)*.
- Deterministic rules machinery is genuinely non-inert: it computes correct entailed answers that lookup cannot, exactly and at ~$0 *(measured certificate; RULES-1)*. Whether that helps a *model* remains **unmeasured after three instrument failures** (void → host-frame → verify-retry-vacuous); the host-integration question has proven hard to instrument at this scale, not hard to answer.
- Hard hand-authored typing looks unsound (~0.39) and soft imported typing is the leading candidate repair — a GO-shaped, unlicensed signal; both readings are LLM-proxy-provisional pending human gold *(g2, g2-import)*.
- Plainly: **both theses remain open.** Nothing yet shows a kernel-equipped small model matching a larger one, kernel-*specific* necessity, natural-language input reach, or favourable end-to-end economics. CORRECTNESS and EFFICIENCY are each INCONCLUSIVE-PENDING.

### Outstanding work

- **RULES-1 host-lift — closed as INSTRUMENT-INVALID (verdict registered).** Three instrument iterations (void → host-frame → verify-retry-vacuous) failed to validate a host-integration instrument; rules-1-c's mechanical verdict is registered INSTRUMENT-INVALID. Per maintainer decision [#24](https://github.com/jeswr/kernel-of-truth/issues/24) = C: the slot pivots to RULES-2 (below) while rules-1-d is designed as paper-only (a non-vacuous verifier is a design-research project, not a cheap repair).
- **RULES-2 — PASS, audit-confirmed (the rules carrier).** A train-time internalisation variant (does fine-tuning a small model on engine-derived *entailments* beat training on stated facts?): reworked onto the rules-1-c entity-form frame, blocking-pilot passed, frozen, GPU campaign complete, verdict registered PASS, and its cross-vendor Gate-A audit **CONFIRMED** (codex/GPT-5.6 recomputed the primary endpoint to an exact match, 0.31585 LB95). So train-time internalisation on engine-derived entailments **does help at all** — the programme's first cross-vendor-confirmed affirmative on the rules/host-integration line. Honest ceiling registered up front and binding: the `knull` analog proved kernel vs plain-dictionary rule sources derive a **byte-identical** training corpus, so this licenses *train-time internalisation helps* — **not** *kernel-specific* value (content-attributed, the fourth content-not-structure result); the s4' deployment side-effect cap also applied.
- **g2-import-v2 → sense-splitting.** The judge instrument sat one item short of its AC1 reliability gate; diagnosis ([#25](https://github.com/jeswr/kernel-of-truth/issues/25)) found the splits are deterministic *construal* differences, and a provenance trace found the underlying defect is **un-sense-split kernel concepts** (one word-level concept per surface word, so a single type can't be sound across senses). The soft typing being judged is also non-binding/rank-only with no consumers — low stakes. Effort is redirecting to **sense-split-first construction** (one concept per word-sense) and the *binding* typing's soundness, with the judge upgraded from Haiku to Opus for any further pilot.
- **DDC — efficiency's first datum, in flight.** Training-free kernel-guided compression (does kernel-chosen structure preserve more ability than magnitude/random pruning at equal size?); harness complete + mock-green + LAW-1 verified, the **t0** calibration tier is running on GPU now → power-sim → **ddc0**, the efficiency thesis's first live measurement (~$5).
- **Large-kernel scale track** — the 10k first rung is measured: the deterministic vectoriser's crosstalk model holds at scale, but WordNet-only typing cannot reach the UFO-typing gate (needs OBO/SUMO/Wikidata) and exact nearest-neighbour cleanup will not scale past ~100k without an ANN index. A concrete 100k-rung plan (multi-source typing portfolio + ANN recall gate + duplicate policy) is drafted; 1M+ remains the goal.
- **sparq upstream PRs** — quoted-triple visibility in embeddings, ontology-prior readers, and quoted-triple inference in the engine (handed to the sparq agent to land, issue #2149).
- **Human-gold reconciliation** — two-human blind panels on the frozen g2/g2-import packages; all proxy-labelled conclusions remain provisional until then.

## Repository layout

| Path | Contents |
|---|---|
| `reports/` | Literature and estate-survey reports (wave 1: sparq estate, deterministic concept vectors, fixed-vectors-in-LLMs evidence, computational NSM + knowledge injection, architecture/PoC harness options) |
| `docs/` | Architecture proposals, the experiment-programme design, the prospectus |
| `poc/` | Proof-of-concept implementations and experiment results |
| `notes/` | Working notes, coordination log |

## Method

Multi-agent research under an empirical-honesty mandate: every load-bearing claim cited; `[established]` / `[claimed]` / `[speculative]` tags kept distinct; negative results reported; the programme is explicitly designed to find out whether the hypothesis is *seriously* right, partially right, or wrong.

## Related work in the estate

- [Content-addressed concepts design](https://gist.github.com/jeswr/7499faa6fcbfe8ee1e3192d05e82e9ad) (PSS agent) — the concept-hash formalism this builds on; prototype `@jeswr/concept-hash`.
- [sparq](https://github.com/sparq-org/sparq) — `sparq-vectors` (structure-aware vectorisation, grounding), RDFC canonicalisation, ZK-over-SPARQL; the `(concept-hash → embedding)` table seam.
