# Cross-experiment feasibility synthesis — both value theses

- **Author:** Fable analyst role (`kern/fable-analyst`), 2026-07-10. This is FABLE's
  authoritative cross-experiment conclusion (the programme-completion goal's capstone;
  Opus never writes it — `docs/next/programme-completion-loop.md` GOAL). Opus reports
  mechanical facts; the feasibility read is decided here and only here.
- **Status: INTERIM.** The frozen set is NOT complete. Four correctness-thesis-critical
  experiments (g2, g3, g8, g9) are frozen-but-UNRUN, blocked on input materials; g4/g5 are
  DRAFT; the canonical circularity test (f2b-transfer, human judge-1) is human-pending. This
  synthesis is the honest CURRENT-evidence picture, not a final verdict, and every bottom
  line below is explicitly conditioned on what is still unmeasured.
- **Inputs (all read at source):** `registry/assessments/{g-series, f-efficiency,
  oracle-coverage, f2b-replicate, compression-census, define-op-census}.json`; the GPT-5.6
  external review `poc/gpt56-review/SYNTHESIS.md`; the honest tracker (`python3
  tools/registry/audit-status.py`); `registry/verdicts/f2b-transfer-llmproxy.json` and
  `registry/verdicts/a5-llm.json`. No registry record, verdict, correction, audit, or review
  file is modified by this document — it interprets, it changes nothing.
- **Epistemic discipline:** every load-bearing claim is tagged MEASURED / LIT-BACKED /
  STIPULATED / EXTRAPOLATION per `.claude/agents/analyst.md` and the honesty-guard. A
  MEASURED number cited outside its envelope re-classifies as EXTRAPOLATION; negatives and
  nulls carry equal prominence with positives. Authority order: verdict objects + auto-reports
  > frozen prereg > design docs > survey prose.
- **One ruling is explicitly NOT re-adjudicated here:** a5-llm. It is owned by a separate
  Fable ruling (in flight). This synthesis treats it verbatim as **REFUTE-on-pins, science
  reproduces, ruling in flight** and premises nothing on it in either direction.

---

## 0. The one sentence that governs everything below

LOAD-BEARING: Across the entire frozen registry there are ZERO audited end-task wins over the kernel-as-text null, and the question the whole programme exists to answer — *does grounding a model in the kernel make that model measurably more correct or more efficient at matched budget?* — is, as of 2026-07-10, **fully UNMEASURED** [MEASURED: the null-bound ledger entries in registry/assessments/oracle-coverage.json and registry/assessments/f-efficiency.json; every end-task-adjacent verdict is either R0 (no host model), a landed FAIL, or a PASS confined to a self-authored oracle-favourable slice].

Everything that IS measured is either (a) instrument-adequacy and perimeter facts about the
deterministic substrate, obtained *inside the fortress wall* (evals authored against the
engine's own stores), or (b) one narrow model-free storage-byte ratio, or (c) one end-task
PASS whose causal attribution is confounded and whose canonical de-confounding test has not
been run. The programme is further along on *building a defensible checker* than on
*showing the checker helps anyone*.

---

## 1. MEASURED + confirmed (cross-vendor CONFIRMED unless noted)

These are the solid facts. All are cross-vendor Gate-A CONFIRMED except where marked, and all
carry their scope indices verbatim.

### 1a. The correctness SUBSTRATE: a sound, cheap, portable, byte-identical deterministic checker exists

LOAD-BEARING: The kot-axiom/1 v0 rules engine is exact and fail-closed on its covered slice, at microsecond cost, and ports across a domain vertical with a byte-identical engine binary [MEASURED: registry/verdicts/l3a.json + registry/verdicts/a5.json, both audit CONFIRMED; registry/assessments/oracle-coverage.json].

The two measurements that establish it:

- **l3a (family/world vertical, R0):** 600/600 covered queries answered exactly with
  provenance + non-empty axiom license (one-sided Wilson 95% LB **0.9955** > 0.98); 300/300
  control queries refused with the exact pre-authored ERR_* code (strict, Wilson LB **0.9911**
  > 0.95); **6/6** planted store violations surfaced at load; mean **5.29 µs/query** on the
  shared 2-core box. Trivial policies bracket the conjunction (abstain-all: covered 0.0;
  answer-all: refused 0.0) — neither can pass, which is what makes the conjunctive primary
  non-degenerate. Audit independently re-derived 34 expectations across all 17 families.
- **a5 (code vertical, R0):** the engine `kot_axiom.py` **BYTE-IDENTICAL** to the l3a pin,
  extended only by data + a pure desugaring grammar over a deterministically-extracted code
  world layer: 855/855 covered-exact (Wilson LB **0.9968**); 122/122 strict refusals (LB
  **0.9783**); **3/3** planted violations; mean **7.82 µs/query**. A no-LLM extraction route
  (kot-code-extract/1) populated the stratum-4 world layer end-to-end. Audit re-derived 38
  expectations + X3 exact-hash and generator-separation checks.

LOAD-BEARING: This is the strongest, cleanest evidence in the whole registry — and it is evidence about the INSTRUMENT, not about usefulness to any model [MEASURED: both l3a/a5 evals were authored against the engines' own stores ("coverage by construction"), so exactness is a consistency-and-licensing property, never world-accuracy; both verdicts are R0 with scale_language_licensed = none].

What this banks: Law-3's deterministic-engine seat (formal language + engine that owns
correctness) demonstrably *exists*, is sound where covered, refuses with named codes off its
slice, carries provenance/license on every answer, costs ~10¹ µs/query, and generalises as a
*formalism* (not a hand-fit artifact) across two verticals. E9's constraint-violation arm and
every downstream verifier design can consume this. What it explicitly does NOT contain: a
model, natural language, a non-trivial baseline, or any real-world fact coverage.

Two scope stipulations bound the semantic reach (not the engine-correctness reach): a5's
construct→concept map is **STRUCTURAL definitions, NOT NSM explications** [STIPULATED:
ASM-0007, load-bearing — a5 exercises the machinery, not the semantic-prime thesis]; l3a's
relation directions are stipulated readings [STIPULATED: ASM-0004]. Until natively-relational
and NSM-explicated concepts are minted, these results support *the formalism*, not *the NSM
semantics*.

### 1b. The f1 compression win — narrow, byte-ratio only, model-free

LOAD-BEARING: KOTK/2 entropy-columnar storage beats the compressed glosses-only text of the SAME records by 6.7369× bytes, cross-vendor CONFIRMED, on ONE corpus at ONE store rung, byte-ratio ONLY [MEASURED: registry/verdicts/f1.json, audit CONFIRMED (Codex independently recomputed 2,300,224/341,435 = 6.736930894606587 and re-ran the lossless packer self-check, 117,791/117,791 URNs re-minted)].

Scope, binding: lexical-wn31 (117,791 records), 2.8987 vs 19.528 B/record, single store rung
S1e5, zstd-19 comparator. Against the more conservative identity-JCS text form the ratio is
~3.3× (decision-record measurement), so the PASS is robust to comparator choice. Law-2
discipline honoured — the comparator is the kernel's own content rendered as compressed text,
not a strawman.

LOAD-BEARING: f1 is a premise-RETAINER, not an efficiency win — bytes alone were pre-declared unable to carry the M4 claim, the latency half of the premise is UNDECIDED (deferred to F5), and there is no accuracy, model, or task anywhere in f1 [MEASURED: registry/verdicts/f1.json envelope + registry/assessments/f-efficiency.json; the design's own kill text: "text-store parity ⇒ the kernel's efficiency contribution is a compression format, not an architecture"]. The byte-ratio extrapolates UPWARD on store size only (table overhead amortises); DOWNWARD it is contradicted at the 2.3k-record haiku tier (~25% table overhead) — size-independence is scale-conditional [MEASURED counter-evidence in design-compact-kernel-serialization-v2.md §4]. Quoting 6.74× on any other record tier or corpus re-classifies it as EXTRAPOLATION.

### 1c. Two substrate-maturity censuses (tooling-measured, no verdict object)

- **define-op census: 0.7710 internal define-checkability** [MEASURED: poc/define-op-census/
  RUN-LOG.md; GO 1.0, SO 1.0, MONDO 0.4871; the 3,941 misses are all un-ingested foreign
  fillers with a named ingestion route]. This is Axis-A substrate readiness — NOT κ_B, NOT an
  end-task claim: it measures checkability legs 1–2 (record present + define-op resolves) on
  the SELF-AUTHORED substrate; the binding third leg (mapper parse of an external benchmark
  item) is untouched. d-ext's ~49% lemma-touch coexisting with 0% checkability is the standing
  warning that substrate coverage ≠ item checkability.
- **B-RT round-trip: 100% (1,786/1,786)** [MEASURED: poc/compression-census/results/
  b-rt-roundtrip.json; parse→roll-up→URN→expand→re-parse is an exact identity, D=8192 vectors
  byte-identical]. The roll-up machinery is sound; what fails is engagement, not correctness
  (§2d).

---

## 2. NOT measured / confound-exposed (equal prominence with §1)

### 2a. "Does grounding help a model?" — the central question, fully UNMEASURED

The measured evidence reaches exactly to the fortress wall and stops. Every step that would
make the substrate matter to a model is an open successor or a landed negative:

- NL must reach the closed grammar (l3a-parse / a5-nl): UNRUN. Every prior programme lesson
  says the NL boundary is where mechanisms die; nothing tests it.
- A model must be measurably better off with the engine than with the kernel-as-text null and
  strong baselines (l3a-cost / a5-llm): UNRUN or under separate contested-audit ruling.
- No correctness experiment scores an unfiltered externally-authored population.

LOAD-BEARING: "a sound, licensed, fail-closed deterministic checker over kernel-governed records exists, extends across domains, and costs microseconds" is MEASURED and CONFIRMED; "that checker, or the kernel it serves, makes any model more correct on any task at matched budget" is UNMEASURED [MEASURED: registry/assessments/oracle-coverage.json null-bound].

### 2b. The SOLE positive end-task signal (f2b verifier-offload) is CONFOUNDED — internal and external reviews converged independently

The one end-task PASS in the registry:

LOAD-BEARING: SmolLM2-135M + kernel-verify-retry (k=4) beats SmolLM2-1.7B-alone by +0.1507 absolute (one-sided 95% BCa LB +0.1053) at cost_ratio_vs_R3 = 0.103, cross-vendor CONFIRMED, and a seed-pinned derangement of the record→item map recovers ~0 of the lift (point −0.021) [MEASURED: registry/verdicts/f2b-replicate.json, audit CONFIRMED].

But this result cannot yet be attributed to the kernel's semantics, and the confound was
flagged from **two fully independent directions that reached the same place**:

- **INTERNAL (the f2b-replicate + f-efficiency assessments, Fable):** the derangement control
  separates CONTENT from STRUCTURE, "not real semantics from definitional circularity" — the
  verifier accepts iff the answer string-equals the canonical record, and d-qa-r gold is still
  DEFINED by that same equality, so under BOTH the real-content reading and the
  self-consistent-circularity reading a derangement destroys the lift; the shuffled control
  provably cannot adjudicate between them [MEASURED: registry/assessments/f2b-replicate.json
  does_not_license, "content-specificity is not ground-truth independence"].
- **EXTERNAL (GPT-5.6 review, all four lenses, sharpest in A and C):** the derangement null
  destroys record↔item *alignment*, not NSM *content* — any aligned deterministic answer table
  (opaque IDs, a plain typed schema) would produce the same lift and die under the same
  derangement, so the measured +0.1507 supports "an aligned deterministic acceptance rule plus
  retry beats these arms on this authored task", not "kernel semantics caused the lift"
  [poc/gpt56-review/SYNTHESIS.md G1].

DECISION: adopt GPT-5.6's language correction — the f2b lift is **correct-alignment-specific**, not "kernel-content-specific", and the f2b-transfer confound is honestly named **gold-label independence**, not "ground-truth independence" [MEASURED: registry/assessments/f2b-replicate.json does_not_license + registry/verdicts/f2b-replicate.json — the derangement null recovers ~0 of the lift under BOTH the real-content and the definitional-circularity readings, so it provably cannot discriminate NSM content from correct record↔item alignment; the wider phrasing exceeds what the control measures, and internal and external reviews converged on the narrower one]. It is a $0 relabel that blocks a false-conclusion class.

The convergence itself is the signal worth recording: an internal honesty-rail assessment and
an out-of-house adversarial review, run independently, identified the *same* single weakest
inferential link in the programme's only positive end-task result. That raises confidence the
confound is real, not an artifact of one reviewer's framing.

*Where GPT-5.6 itself overstated (flagged, not adopted):* its lens-A claim that a stage-2
f2b-transfer PASS "removes exactly one confound" is itself an overclaim (the designer
synthesis corrects this in-house); its family-h0 "prospectivity" critique and its
Construction-B commutativity worry are both wrong (family members are fixed in the frozen P1
master plan; Construction B uses fixed permutations by design) [poc/gpt56-review/SYNTHESIS.md
§Bottom line]. Adopt the language corrections; do not inherit the overstatements.

### 2c. f2 verifier-offload FAIL landed as a FAIL

LOAD-BEARING: F2's frozen HE1 (R1,R2) gap-closure primary FAILED as pre-registered (gap_closed_fraction = −40.13, one-sided CI −135.6 to −23.1); the FAIL stands unmodified, and is MEASURED-UNAUDITED because the audit gate fires on PASS only [MEASURED: registry/verdicts/f2.json, fired_rule_index 1].

No softening. The diagnostic read — which does not change the verdict — is that the estimand's
denominator was degenerate: R2-alone (360M) scored ≤ R1-alone (135M) on D-QA (0.388 vs 0.394),
so there was no s→S gap to close, and that attribution is itself the MEASURED finding of the
audited f2b-replicate separation gate. Un-contaminated by the denominator and carried at full
prominence: **HE2 cascade-dominance is DEAD at this scope** — the verifier-gated cascade was
not strictly dominant over the model's own free calibration baselines (logprob gate + gloss-text
self-check) at every escalation budget (Holm family fail, worst-budget p 0.0471). The model's
own free signal was not beaten under the pre-registered dominance standard. Also NOT a
measurement: f2's external-slice "zero transfer" reading was an **instrument artifact**
(ext_vector ran model-alone in every arm) — off-slice transfer after f2 is UNMEASURED, not
negative [MEASURED: bead kernel-of-truth-97r; a live discrepancy D3, the uncorrected reading
still sits in the bead description].

### 2d. Coverage is the narrow, non-transferring perimeter

LOAD-BEARING: Kernel-vocabulary coverage is 0.3542 of content-word mass on the FRIENDLIEST measured corpus at the molecules-v0 rung (kernel-v0 0.2210; wn31-aligned reachable band 0.7841), clearing the 0.20 niche-scope gate but leaving ~2/3 of even this corpus unreachable [MEASURED: registry/verdicts/m0b.json, audit CONFIRMED; corpus/rung/kernel-state-indexed; extrapolates to NO other corpus — ASM-0002 open, with one live non-transfer warning].

This is the hard ceiling on every covered-slice claim. Two censuses show USABLE coverage is
thinner still: proposition-level roll-up **engagement is ~0.6%** (idea-B compression, ~5×
below its 2% floor — PARKED behind coverage growth, not a mechanism kill) and the maintainer's
flagship "a AND b" pattern engages ~0 on real text (1 fragment / 405,523 sentences)
[MEASURED: registry/assessments/compression-census.json]. m0b's 0.3542 must never be read as
"fraction of the corpus the kernel can do something with"; it is surface-form vocabulary
membership, a crude LOWER bound on expressibility.

---

## 3. OPEN decisive tests (what is still in flight or unrun)

### 3a. The canonical circularity test (f2b-transfer) — human-pending, with a WEAK proxy in flight

- **Canonical path: OPEN, human-blocked.** f2b-transfer (frozen) Stage-1 with a kernel-naive
  HUMAN judge-1 is the ONLY experiment on this line that adjudicates H-TRANSFER vs H-CIRC — the
  real content-vs-circularity question. The CSV awaits human annotation
  [docs/next/programme-completion-loop.md standing human-blocked items].
- **Proxy stand-in: PASS-PENDING-AUDIT, A₁ₚ = 0.95, but a WEAK FEASIBILITY PROXY only.**
  f2b-transfer-llmproxy fills judge-1 with a pinned LLM (GPT-5.6-Sol) because the human is
  unavailable; the one-sided 95% Wilson LB of A₁ₚ cleared 0.70 [MEASURED-PENDING-AUDIT:
  registry/verdicts/f2b-transfer-llmproxy.json, verdict PASS-PENDING-AUDIT]. Its own binding
  envelope is emphatic and I adopt it verbatim: single judge FAMILY (GPT-5.6/5.5 same-vendor,
  may correlate), kernel-TRADITION familiarity (NSM style plausibly in training data,
  ASM-0021), PARTIAL circularity break only, and — decisively — **a PASS does NOT adjudicate
  H-TRANSFER vs H-CIRC, does NOT substitute for the human Stage-1, and does NOT license Stage-2
  or any f2b promotion** [STIPULATED: ASM-0022, weak-proxy status]. Read asymmetrically: the
  named channels plausibly push A₁ₚ up, so a FAIL would have been the informative outcome; the
  PASS licenses only continued investment, never a claim upgrade.

LOAD-BEARING: the sole positive end-task result remains attribution-confounded, and NO experiment that could de-confound it (human f2b-transfer; the K-NULL aligned-non-NSM-store ablation) has read out [MEASURED: registry/assessments/f2b-replicate.json; the A₁ₚ=0.95 proxy is explicitly not that experiment].

### 3b. Successor legs that decide usefulness (designed/unrun or ruling-in-flight)

- **l3a-parse / a5-nl (the NL boundary): UNRUN.** The highest-mortality unmeasured leg —
  mapper-parse vs gold-parse loss on the same frozen evals. Everything §1a banked is reachable
  only through a closed grammar; if NL cannot reach it cheaply, the oracle stays an internal
  instrument. Tier-0-ish, no GPU.
- **l3a-cost / a5-llm (the LLM differentiator): UNRUN / ruling-in-flight.** l3a-cost converts
  the 5.29 µs/query V-ledger line into (or kills) an engine-vs-LLM correctness argument.
  a5-llm is the code-vertical head-to-head: I treat it verbatim as **REFUTE-on-pins, science
  reproduces, ruling in flight** — its mechanical endpoints (effect_size 0.6601, cost_ratio
  ~2.3×10⁴) are not premised on here in either direction, and the separate ruling owns whether
  the science stands on corrected pins [not adjudicated here per tasking; registry/verdicts/
  a5-llm.json audit REFUTE]. GPT-5.6 separately flags that a5-llm's lenient pro-LLM extractor
  is *anti-conservative for the differentiator kill* — a pre-freeze repair worth landing before
  any re-freeze [poc/gpt56-review/SYNTHESIS.md G5], but that is a design action, not a claim.

### 3c. The correctness SEMANTICS core (g2/g3/g8/g9) — FROZEN but UNRUN, input-blocked

LOAD-BEARING: The correctness thesis's load-bearing semantics measurements are UNMEASURED: g2 (Π read-out soundness vs n=500 human gold), g3 (semantics-pin necessity), g8 (Lean minting), g9 (authoring capability) are FROZEN-but-UNRUN and g4/g5 are DRAFT — blocked on INPUT MATERIALS (human gold + adjudication, instance descriptions, a Mathlib crawl, an authored explication set), not on compute or design [MEASURED: registry/experiments/g2.json frozen with verdict absent; registry/assessments/g-series.json status_census — six of eight G-rows carry verdict:null].

Only g6 and g7 produced results, and both are **container-shape (formalism-capacity) facts,
not semantics facts**: g7 FAIL selected apply-clauses (kot-ast/2) as the bulk representation —
a design selection, verbatim "not a programme kill" (inline rendering breaches on 91.3% of
committed bulk records); g6 INCONCLUSIVE left the ∃-conjunctive-only fragment open (AND-demand
rare at 0.0505%, but the closed sidecar inventory absorbs only 2/142 of it). *Tracker-vs-reality
discrepancy, corrected here:* the "13/14 frozen experiments run + audited" framing is FALSE for
these six rows — they are NOT-RUN, and `audit-status.py` renders them indistinguishably from
run-awaiting-assessment (a flagged tooling defect).

### 3d. The cheap $0–250 confound-sharpening probes (GPT-5.6, adopted as design targets)

These are the cheapest decisive money in the programme and several are timing-critical (must be
frozen before f2b-transfer Stage-2 unblinds, or they lose confirmatory standing forever):

- **Truth×style 2×2 adjudication probe** — crosses semantic correctness with NSM-shaped vs
  plain surface, length/fluency-matched, order-rotated, blind-adjudicated. Protects the
  interpretation of f2b-transfer against style/familiarity leakage. CPU + bounded adjudication.
- **K-NULL ablation, preceded by a content-injection map** — vector-free / opaque-ID /
  conventional-store nulls of the f2b verifier at identical retry topology and FLOPs; the
  content-injection map (enumerate exactly where kernel-derived bytes touch the model) must come
  first, or the ablation "passes" trivially against arms that were never different. $0–250. This
  is the single experiment that decides what the +0.1507 *is evidence of*.
- **Pre-frozen failure-cause taxonomy for the F2 line + exploratory item-cluster bootstrap
  re-analysis** — ~$0, must be declared into Stage-2's consumer design before unblinding.

---

## 4. BOTTOM LINE per thesis

### CORRECTNESS thesis — UNDETERMINED, pending the NL boundary and the semantics core

**Verdict: ALIVE but UNDETERMINED — its instrument half is MEASURED-and-CONFIRMED, its
usefulness half is entirely UNMEASURED, and its semantics core has not been run at all.** The
programme has proven, cross-vendor, that a sound, fail-closed, provenance-carrying, microsecond
deterministic checker exists and ports across verticals with a byte-identical engine (l3a
600/600, a5 855/855, strict refusals, planted-violation capture). That is real and it is the
strongest evidence in the registry — but it is instrument-adequacy obtained inside the fortress
(evals authored against the engine's own stores), it exercises the *formalism* rather than the
*NSM semantics* (ASM-0004/0007), and it says nothing about whether grounding helps a model.
The four experiments that would test the semantics (g2/g3/g8/g9) are frozen-but-unrun and
input-blocked; the NL boundary that would make the checker reachable (l3a-parse/a5-nl) is unrun.

*Single result that would settle it* (in truth two, in order): **(1) l3a-parse/a5-nl** —
whether natural language reaches the closed grammar cheaply; if it does not, the checker is a
permanent internal instrument regardless of everything else. **(2) g2** (Π read-out soundness
vs blind human gold) — whether the kernel's semantics are sound at all, which g3 gates (a g3
necessity-kill auto-resolves HS2 to sidecar-only). g2's gold-annotation budget is protected by
generating g3 materials first.

### EFFICIENCY thesis — ALIVE-NARROW, pending de-confounding of its one positive

**Verdict: ALIVE-NARROW — one audited model-free storage-byte premise retained, one end-task
PASS that is real but attribution-confounded, one mechanism variant DEAD at scope, everything
else unrun.** f1 retains the M4 byte premise (6.74×, audited, one corpus, one rung, latency
undecided) but a byte ratio is a compression format, not an architecture, until an accuracy leg
(F5) exists. The verifier-offload line has exactly one PASS (f2b-replicate, +0.1507 at
cost_ratio 0.103, audited) — but it is correct-alignment-specific, not kernel-content-specific,
and its canonical de-confounding test is human-pending with only a weak A₁ₚ=0.95 proxy in
flight. f2's own frozen primary FAILED; HE2 cascade-dominance died against free calibration
baselines; and no audited end-task efficiency win exists over the kernel-as-text null outside
the self-authored oracle-favourable slice.

*Single result that would settle it:* **f2b-transfer with a human judge-1** (the canonical
content-vs-circularity adjudication), OR, as the cheapest decisive proxy for it, **the K-NULL
aligned-non-NSM-store ablation** — either one decides whether the +0.1507 is a kernel-semantics
result or a generic "aligned deterministic answer key + retry" result. Under the deflationary
reading the *efficiency* economics still survive in narrowed form ("135M + an authored
deterministic answer key beats 1.7B-alone at ~10% FLOPs"), but the open question then becomes
authoring cost (Law 1), not semantics.

### Neither thesis is dead; neither is established. Both hinge on measurements that are cheap and already designed, and the binding constraint is not compute — it is human annotation (f2b-transfer, g2 gold) and input-material generation (g3/g8/g9), plus a handful of $0–250 attribution probes.

---

## 5. Highest-information next steps (cheapest-decisive-first)

Ranked by information-per-dollar toward the feasibility verdict. Each is labelled with its
executor gate. "Adopt" = carry into the named design / propose to the maintainer; nothing here
is committed by this document.

| # | Next step | Why it is decisive | Cost | Executor gate |
|---|---|---|---|---|
| **1** | **Claims-language + envelope corrections bundle** — relabel f2b "correct-alignment-specific", rename the f2b-transfer confound "gold-label independence", narrow HC3 to the named PRM checkpoint (not "the 1.5B class"), plus the GPT-5.6 G7 envelope table (f1 store-size, f4/f5 licensing width, g9 EXTRAPOLATION). | Restores the programme's only positive result to its measured scope; every downstream doc inherits these phrases; the honesty rail IS the product. | $0 | **Fable-design** (forward language + successor records only; frozen objects untouched). Opus-executable for the mechanical tracker/prose edits once Fable specifies them. |
| **2** | **Truth×style 2×2 adjudication probe + pre-frozen F2 failure-cause taxonomy** — frozen BEFORE f2b-transfer Stage-2 unblinds. | Protects the interpretation of the single most important record in flight; after unblinding they lose confirmatory standing forever (R-2 logging rule). | ~$0 (CPU + bounded adjudication) | **Fable-design** to freeze; **Opus-executable** to run. Timing-critical. |
| **3** | **K-NULL ablation, content-injection map FIRST** — aligned-non-NSM-store / opaque-ID / vector-free nulls at matched topology+FLOPs. | Decides what the +0.1507 IS evidence of (kernel semantics vs generic aligned answer key) — the cheapest attribution money available, ahead of any further F2-line spend. | $0–250 | **Fable-design** (map + arms), then **GPU-gated** (small; matched-FLOP retry). |
| **4** | **f2b-transfer with human judge-1** (canonical) — recruit/annotate the frozen CSV. | The ONLY experiment that adjudicates H-TRANSFER vs H-CIRC; the A₁ₚ=0.95 proxy explicitly cannot. Settles the efficiency thesis's one live positive. | Human annotation time | **Human-blocked** (maintainer/annotator). Standing item; do not re-dispatch, surface for scheduling. |
| **5** | **l3a-parse / a5-nl (the NL boundary leg)** — mapper-parse vs gold-parse loss on the existing frozen evals. | The highest-mortality unmeasured correctness leg; decides whether the microsecond checker is reachable from NL or is a permanent internal instrument. | ~$10, no GPU (mapper + existing evals) | **Fable-design** to freeze; **Opus-executable** to run (Tier-0). |

**Held with reasons (next tier):** g3-then-g2 materials generation (the correctness semantics
critical path — cheap Tier-0 but human-annotation-gated on g2 gold; g3-first protects the g2
budget) → **human-blocked / Fable-design**; l3a-cost differentiator (~$40 Modal) → **GPU-gated**,
sequence after l3a-parse shows NL is reachable; f2b-family-replicate (the cheapest ecology buy,
decides two-family sign) → **GPU-gated**, only after f2b-transfer reads out; a5-llm pre-freeze
extractor/ledger repairs → **Fable-design**, but the a5-llm *ruling itself* is a separate Fable
task not touched here. Deprioritised until attribution is settled: M5 cascade re-entry, TIMEPACK/
versioned-contradiction (GPT-5.6's best new value surface, but design it only after the
circularity chain reads out).

---

## Epistemic register (assumptions this synthesis relied on)

- **STIPULATED, adopted from convergent internal+external review:** the f2b lift is
  correct-alignment-specific, not kernel-content-specific (blocks a false-conclusion class; $0).
  The f2b-transfer confound is gold-label independence, not ground-truth independence.
- **STIPULATED (ASM-0022):** f2b-transfer-llmproxy A₁ₚ=0.95 is a WEAK feasibility proxy; it does
  not adjudicate H-TRANSFER vs H-CIRC. Load-bearing on the efficiency bottom line's "still
  confounded" framing; resolution path = human f2b-transfer OR K-NULL.
- **EXTRAPOLATION (not premised):** that coverage ~0.35 or the +0.1507 lift would hold on other
  corpora, hosts >1.7B, non-templated items, or externally-authored items. ASM-0002, the f2b
  envelope catch-room shrinkage, and the m0b scope are all open; none premises a conclusion here.
- **MEASURED, fully indexed and never widened:** every number in §1 carries its corpus/rung/
  kernel-state/model indices verbatim; m0b 0.3542 is restated only as corpus-indexed gate, never
  as "natural coverage" (the worked caution ASM-0001/0002).
- **NOT adjudicated here:** a5-llm (separate ruling; treated verbatim as REFUTE-on-pins, science
  reproduces, ruling in flight). No conclusion depends on it in either direction.

This synthesis is INTERIM: it will change when the frozen-unrun set (g2/g3/g8/g9), the human
f2b-transfer, the NL-boundary legs, and the K-NULL ablation read out. Nothing above is a final
feasibility verdict; it is the honest current-evidence picture the maintainer can act on now.
