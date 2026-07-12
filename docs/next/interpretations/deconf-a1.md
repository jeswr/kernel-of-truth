# FABLE INTERPRETATION — DECONF Stage A1 (mechanical: C_dec = 1.0 EXACTLY over all three components of the rev-B certificate denominator — 40,576/40,576 distinct decision cells concordant across grid ∪ replay ∪ init-order, the replay component a disclosed answer-superset SUBSTITUTE for the prescribed transcript replay — zero discordances, §3.2 triage NO-OBJECT; the certificate establishes EXTENSIONAL DECISION equivalence at the pinned scope (KERNEL-RUNTIME-STRUCTURE-INERT as §3.2 defines it), NOT a read-set proof; R-1/135M only; execution status remains EXPLORATORY pre-freeze; neither programme thesis moves)

- **Author:** Fable (interpretation agent), 2026-07-11; **rev-4 — the
  calibration pass.** Rev-4 applies every finding of the GPT-5.6 review of the
  complete-certificate interpretation
  (`poc/gpt56-review/rev-deconfi-20260711/last-message.json`, binding on this
  document): every extensional-equivalence claim is now stated as EXTENSIONAL
  DECISION equivalence (never as a read-set or literal-runtime claim); §3's
  replay-soundness argument is corrected (rev-3's "only state mutator" premise
  was FALSE as written) and restated as an explicit, unmeasured code-level
  decision-state-confluence argument; "complete" is everywhere qualified as
  complete-with-the-§3.1(c)-substitution, never literal-transcript-complete;
  and denominator entries are counted as distinct decision cells with the
  diagnostic repeats excluded. No number changed. Rev-3 was the
  complete-certificate update. Rev-2 of this document was scoped to GRID-ONLY
  because only DECONF §3.1(a) had executed, and flagged §3.1(b)
  dual-initialization and §3.1(c) trajectory replay as PENDING. Those components
  have now RUN (same day, same pins, local CPU, ~$0, zero model calls), and this
  revision updates the interpretation to the complete certificate. It preserves
  every scope correction adopted in rev-2 from the GPT-5.6 interpretation review
  (`poc/gpt56-review/rev-deconfa1i-20260711/last-message.json`) — none of those
  corrections is voided by completion; they are re-applied at the wider
  denominator. This document interprets; it changes NO frozen record, NO verdict
  object, NO results-log line, NO registered assumption, and performs no
  git/bd/kb operation. The coordinator commits.
- **Sources (read at source, in full):** `poc/deconf-a1/a1-complete-result.json`
  + `poc/deconf-a1/RESULT.md` (the COMPLETE run — authoritative for every number
  below; `a1-result.json`, the grid-scope artifact, is reproduced
  byte-identically by this execution and is subsumed), `poc/deconf-a1/audit_a1.py`
  (what was actually computed — now implementing §3.1(a)+(b)+(c), read against
  the design), `build_gsa.py` + `gsa-manifest.json` (the projection),
  `docs/next/design/DECONF.md` rev-B (the BINDING interpretive frame, esp.
  §3.0's certificate semantics, §3.1's certificate denominator — grid ∪
  trajectory replay ∪ dual-initialization — §3.2's C_dec reading + triage
  ladder, §1's scoped invariance lemma, §9.1's honest limits), and the three
  GPT-5.6 reviews (`rev-deconfb-20260711`, which set the certificate framing;
  `rev-deconfa1i-20260711`, binding on this document's scope discipline;
  `rev-deconfi-20260711`, binding on this revision's calibration). For §3's
  corrected state-mutation account, `poc/f2b/runner/f2b_runner.py` at the
  verified sha, read directly. For
  §5, `docs/next/interpretations/f2b-transfer-stage1.md` (post-judge-3 FINAL
  figures).
- **Epistemic discipline:** every load-bearing line carries its `[TAG]`.
  **MEASURED** restates a counted/computed fact strictly from a cited artifact
  (never recomputed); **STIPULATED** marks design rulings and framing adopted
  verbatim (including the entire rev-B licence structure —
  PROPOSED-ASM-1010/1011, coordinator registration pending); **DERIVED** marks
  an analytic observation made in THIS document from MEASURED facts or from
  direct code reading, disclosed as absent from the cited artifacts; **ASSUMED**
  marks a direction-only forward note, never load-bearing; **EXTRAPOLATION**
  marks a registered forward projection under DECONF's binding taxonomy (here
  ASM-0966).
- **Governance status, stated first because it bounds everything:** the executed
  A1 is **EXPLORATORY — a pre-freeze execution** [MEASURED: RESULT.md status
  line]. The DECONF design routes through external review → prereg freeze → a
  registered runner-role re-run before any registered ruling. Every step of this
  execution is deterministic and pin-gated (all five corpus hashes, the runner
  sha `b62c3a72…`, the GS-A sha `4a28f7fa…`, the replayed shuffle map
  `05af8f50…`, and the replay-log pins `dd98cceb…`/`133abf1f…` byte-verified
  against the frozen registry and manifest pins) [MEASURED: RESULT.md +
  a1-complete-result.json `pins`]; that the registered re-run reproduces these
  bytes for ~$0 marginal compute is the registered forward projection
  [EXTRAPOLATION: ASM-0966 — forward-looking, not measured]. What has CHANGED
  since rev-2 is the MEASUREMENT status, not the governance status: the rev-B
  certificate denominator is now fully executed — the §3.1(c) component as the
  disclosed answer-superset substitute for the prescribed transcript replay
  (§3). What remains pending is registration, not measurement.

---

## 0. The mechanical facts, restated at the complete-certificate scope

- PREMISE: [MEASURED: a1-complete-result.json `C_dec_complete`,
  `C_dec_complete_exact`] **C_dec = 1.0 exactly — 40,576/40,576** distinct
  decision cells concordant over the full rev-B denominator (each cell counted
  ONCE; the replay component's diagnostic repeat consultations are NOT
  denominator entries — see the §3.1(c) bullet), grid ∪ replay ∪
  init-order, kernel store vs GS-A (the mechanical four-column projection of
  the kernel's own 108 covered-concept records onto the pinned checker's
  read-set). This is an exhaustive count over the enumerated decision closure —
  no sampling error, no CI. Discordance list: empty (`n_discordant` = 0). The
  three components:
  - **§3.1(a) grid (eager init): 11,848/11,848** [MEASURED] — three pinned
    corpora (d-qa 650 incl. 150 controls: 3,704 cells; d-qa-r 1000: 5,840
    cells; d-qa-t 360: 2,304 cells) × every admissible answer in the closed
    IF-C surface × both verifier variants (true; seed-pinned Sattolo
    derangement). Byte-identical reproduction of the first execution's
    `a1-result.json`.
  - **§3.1(b) dual-initialization: 11,848/11,848** [MEASURED] — the FULL grid
    re-run under lazy (per-item `_load`) initialization, kernel↔GS-A
    concordant under BOTH orders; **0 label collisions** over 108 lowercased
    store labels and 108 item labels (the later-load-wins overwrite path
    counted unreachable, emptiness asserted by count, not assumed);
    **108/108 unique** normalized canonical texts; **0 eager-vs-lazy decision
    divergence within either store** (the lazy term-for-definition path can
    miss a not-yet-loaded concept, but a missing `_by_label` entry and a
    non-matching entry both decide ok=False — so DECISIONS are
    init-order-invariant even though internal lookup state is not).
  - **§3.1(c) trajectory replay: 16,880/16,880** [MEASURED] — all 7
    verifier-consulting run-cells of the audited f2b-replicate final run
    (kernel-verify-retry k=4 × seeds {0,1,2}; shuffled-kernel-verify-retry
    k=4 × seeds {0,1,2}: 6 × 2,730 = 16,380 distinct (position, answer)
    decision cells by answer-superset enumeration at the realized evolving
    state, replayed IN SEQUENCE with the runner's exact realized
    initialization and consultation order; each cell was additionally
    consulted 5 times as a diagnostic same-answer repeat probe —
    repeat-consultation violations: 0 — with the repeats EXCLUDED from the
    denominator, which counts each cell once) plus the
    extraction-instrument cell's
    **500 REAL logged d-xif R1 answers replayed answer-for-answer** in file
    order (500/500 concordant; stored per-output `ifc_*` flags match the
    kernel replay 500/500; both stores reproduce the audited cell's logged
    aggregates exactly). Log pins byte-verified (`run-records-f2b.jsonl`
    `dd98cceb…`; `d-xif/outputs/r1.jsonl` `133abf1f…` == the f2b-manifest
    pin). See §3 for the coverage-substitution disclosure this component
    carries (it is NOT the literally-prescribed transcript replay).
- PREMISE: [MEASURED: a1-complete-result.json `triage_3_2`] the §3.2 four-cause
  triage ladder (projection/adapter bug; incomplete read-set;
  initialization-order difference; schema mismatch) is **NO-OBJECT**: zero
  discordant triples on grid, init-order, and replay — nothing to triage, and
  **no KERNEL-RUNTIME-CHANNEL-CANDIDATE exists** on the measured closure (the
  candidate label is assigned by the stipulated classification rule, so its
  absence is a rule-consequence of the measured zeros [STIPULATED/DERIVED],
  the zeros themselves MEASURED).
- PREMISE (vacuity guard — the certificate does real work): [MEASURED:
  RESULT.md grid-scope detail, unchanged] the kernel-side true-variant triples
  split 1,860 accepts / 3,644 rejects / 420 abstentions (exactly the 150
  non-checkable d-qa controls × their answer spaces); true and shuffled
  variants diverge on 1,673/5,924 item–answer pairs; the replayed verify cells
  span materially different decision mixes across true and shuffled arms
  [MEASURED: `kernel_triples` per cell]. Concordance was measured across
  accepts, rejects, abstentions, shuffled-composition divergence, AND evolving
  trajectory state — it is not a trivially-constant comparison.
- PREMISE (the counted circularity signature, unchanged): [MEASURED:
  a1-result.json `true_variant_decidable_accept_vs_gold`, reproduced
  byte-identically] on all 5,504 decidable (item, admissible-answer) pairs,
  verifier-accept ⇔ membership gold with ZERO off-diagonal cells (accept|gold
  1,860; reject|nongold 3,644; accept|nongold 0; reject|gold 0).
- PREMISE: [MEASURED-BY-INVARIANCE, i.e. DERIVED in the artifact itself and
  tagged so there: a1-complete-result.json `R_repro`, `status_tags`]
  **R_repro = lift(GS-A)/lift(kernel) ≡ 1.0 identically** — as an
  artifact-internal derivation, NOT a fresh model run, and never to be cited as
  one: it invokes the §1 determinism lemma (identical decisions on the full
  reachable decision surface ⇒ bit-identical endpoints), whose antecedent the
  completed run verifies directly on the grid and both initialization orders,
  and on the realized trajectories only via §3's answer-superset cover — i.e.
  subject to §3's unmeasured code-level confluence argument. The kernel-arm lift it applies to (+0.1507
  vs R3, BCa LB +0.1053) is restated context from the audited f2b-replicate
  record, not remeasured here [MEASURED: `measured_lift_context`, restated].
- PREMISE (sub-grids and supplement, unchanged): [MEASURED: RESULT.md] the
  run-realized f2b-replicate protocol sub-grid (d-qa-r[:250], 102-urn index)
  1,460/1,460; the run-planned f2b-transfer stage-2 sub-grid (d-qa-t[:250],
  105-urn index) 1,592/1,592; the d-ext off-coverage abstention grid
  4,000/4,000.

---

## 1. What was measured — the executed equivalence certificate, read strictly inside the rev-B frame

LOAD-BEARING: [STIPULATED: DECONF §3.0 (PROPOSED-ASM-1010), adopted as binding]
A1 is an **executable EQUIVALENCE/REGRESSION CERTIFICATE over an exact
projection of kernel-authored answer strings** — and, as of this execution,
all three components of its pre-registered denominator — grid ∪
trajectory-replay ∪ dual-initialization — have run, with ONE disclosed
substitution: the §3.1(c) component is NOT the literally-prescribed replay of
logged (item, attempt, answer) trajectories (no per-attempt log exists) but a
coverage-equivalent answer-superset SUBSTITUTE, sound subject to §3's
code-level decision-state-confluence argument. Wherever this document says the
certificate is "complete", it means complete-with-this-substitution, never
literal-transcript-complete [MEASURED: §0; STIPULATED: §3.1's denominator;
DERIVED: the substitution framing]. GS-A copies
the kernel's own answer-bearing bytes (gloss.strip / render_plain(groundingNote),
claims = segments(canonical_text) — the pinned `KernelVerifier._load` derivation
itself, imported from the verified runner bytes) [MEASURED: build_gsa.py +
gsa-manifest.json]. Concordance was therefore *nearly true by construction*,
and the design says so in advance (§9.1: "a certificate, not a discovery
instrument"; the expected outcome was registered as non-load-bearing
EXTRAPOLATION ASM-0966, now resolved in its expected direction across all
three components — the replay component via the §3 substitute). The stage's
value is exactly the conversion the design pre-registered: an analytic claim
("a generic aligned answer-key WOULD reproduce it") is now a measured, riding,
re-checkable fact over the measured certificate closure ("the answer-key
projection DOES reproduce every enumerated grid decision, every decision in
the answer-superset cover of the realized trajectories — plus all 500
genuinely logged d-xif answers, answer-for-answer — and every decision under
both initialization orders, bit-for-bit") [STIPULATED: §3.3; MEASURED: §0].

The single narrow proposition the certificate targets is §3.0's, quoted in
the design's own words [STIPULATED: §3.0 wording]: *"the pinned F2 runtime
checker uses no information beyond the projected urn-keyed label/gloss/claim
answer key."* What the measurement actually establishes is the EXTENSIONAL
form of that proposition, and only that form [MEASURED: C_dec = 1.0; DERIVED:
the calibration, per the residue paragraph below]:

> **At the pinned harness/checker/output-space/init/store hashes, every
> decision the pinned F2 runtime checker takes on the measured closure — the
> exhaustive decision grid, the answer-superset cover of the audited run's
> trajectories, and both initialization orders — is extensionally computable
> from the projected urn-keyed label/gloss/claim answer key alone: the
> structural fields change no decision.**

The literal read-set form of the §3.0 wording ("uses no information beyond")
is NOT something mirror-concordance can prove: the evidence does not exclude
extra reads, caching, pin checks, timing bookkeeping (`last_cpu_s`), or other
decision-inert runtime activity, and stipulating the stronger wording does not
make it empirically proved. The extensional form governs every claim in this
document; §6 recommends the frozen record adopt it (or carry this gloss
verbatim).

Equivalently, in the §3.2 vocabulary: the kernel's structural fields
(explication trees, primes, vectors, types, provenance frames, engine hooks)
are **runtime-inert under the pinned topology** — this is the pre-registered
reading of C_dec = 1.0, and it is now available at the scope §3.2 defined it
for, not a grid-restricted fragment of it [STIPULATED: §3.2 (PROPOSED-ASM-1010);
MEASURED: §0]. Stated precisely, what C_dec = 1 licenses: **extensional
decision equivalence on the measured closure — the structural fields change
no decision, and no decision-semantic contribution beyond the projected
answer key was detected.** It does NOT license the literal-runtime claim that
the checker reads or does nothing else (the residue paragraph below). The
consequence for the F2 line, said exactly and no
wider: **the measured F2 verify-retry lift (+0.1507, BCa LB +0.1053) survives
as an ALIGNED-ANSWER-KEY property — a property of verify-retry against an
item-aligned deterministic answer key — and NOT as distinctive kernel runtime
semantics. The kernel is measured to be ONE WAY TO AUTHOR such a key; no
kernel-specific decision-semantic contribution was detected anywhere on the
measured closure**
[MEASURED: §0; STIPULATED: the §3.2 reading + §5.2's ALIGNMENT-SPECIFIC licence
sentence, whose runtime half the completed certificate supplies; the alignment
half — aligned vs generic retrieval — awaits Stage B's Δ_align contrast].

That sentence — and NOT "kernel-authored content is generic" — is the whole
positive content of the result. GS-A is not independently-generic content; its
strings ARE the kernel's strings; nothing about the value of AUTHORING those
strings is tested here [STIPULATED: §2.1/§3.0; the rev-B review's ranked
concern #2, carried forward verbatim].

DERIVED (a bounded robustness observation of this document, from reading
audit_a1.py; the rev-2 weakening retained — completion widens its domain, not
its strength): the GS-A-side checker (`GSAVerifier`/`GSAShuffledVerifier`) is a
mirror class that *physically has access only to the four projected columns* —
no record file, no derivation function, no engine is reachable at check time.
Concordance of every evaluated cell therefore establishes **extensional
decision equivalence on the measured closure**: each decision is computable
from the projection alone. It does NOT establish that the kernel-side checker
performed no extra store reads — an extra field may be read yet remain
decision-inert on every measured cell — and mirror-agreement is not a read-set
proof. The residual falsification surface the design named — the
term-for-definition path, claim-polarity membership, the shuffled-map
composition, the order-dependent label map, engine consultation inside
`check()` — is now CONSTRAINED across grid, trajectory, and init-order states
(any such channel decision-relevant on any measured cell would have produced
discordance and did not [MEASURED: §0]), with the remaining residue exactly
two-fold: decision-inert runtime activity — extra reads, caching, pin checks,
timing bookkeeping such as `last_cpu_s` — extensionally invisible in
principle, and unrealized trajectory states outside the answer-superset
closure of §3 (argued-closed by §3's code-level confluence argument, disclosed
there as unmeasured) [STIPULATED: §3.2 falsifiability note; DERIVED: this
residue statement].

## 2. The triage ladder: NO-OBJECT on the complete denominator

[STIPULATED: DECONF §3.2 — the four-cause triage (projection/adapter bug,
incomplete read-set, initialization-order difference, schema mismatch) is
defined FOR the C_dec < 1 branch.] With zero discordant triples across all
three components, the ladder has nothing to triage: **NO-OBJECT** [MEASURED:
`triage_3_2`], and no KERNEL-RUNTIME-CHANNEL-CANDIDATE exists on the measured
closure [MEASURED: the zeros; STIPULATED/DERIVED: the label semantics]. Unlike
rev-2, this exclusion is no longer qualified by unexecuted components: the
init-order cause is directly probed by the full dual-order grid re-run
(cause 3's own named test, run unconditionally rather than on-discordance),
and the trajectory-state channel that grid enumeration structurally cannot
reach is probed by the §3.1(c) replay-substitute, subject to §3's
coverage-and-confluence disclosure [MEASURED: §0]. Causes 1 and 4 remain
constrained by construction as before [DERIVED, from the code]: the projection
uses the checker's own pinned load-time derivation functions and fails closed
on every record/label/count pin (ERR_RECORD_PIN, ERR_LABEL_DRIFT,
ERR_LABEL_COLLISION — the collision list asserted empty by count, and now also
published: 0/108 store, 0/108 item [MEASURED: §0]).

## 3. The replay-coverage disclosure — carried in full, not papered over

The §3.1(c) design text PRESCRIBES a transcript replay: "replay every logged
(item, attempt, answer) trajectory" [STIPULATED: §3.1(c)]. The audited
campaign's pinned runner did NOT persist per-attempt answers — it persisted
per-item `item_correct` vectors only [MEASURED at source:
a1-complete-result.json `per_attempt_answer_logs`; RESULT.md coverage
disclosure]. What executed is therefore a SUBSTITUTE, not the prescribed
replay: coverage of the realized trajectories by **ANSWER-SUPERSET enumeration
at the realized state** — at each item position of each cell's realized
consultation sequence (the runner's exact realized initialization — eager
`index_labels` over the rank-prefix-250 scored items — and consultation order,
250 covered + 500 d-ext items), EVERY admissible answer is consulted at the
realized evolving checker state and additionally repeated k+1 = 5 times (the
realized max attempts; the repeats are a diagnostic probe, not denominator
entries) [MEASURED: `trajectory_replay_3_1c_coverage`].

Why the substitute covers every realizable logged (item, attempt, answer)
decision — the argument, with its epistemic status per link. The cover is
sound IFF the checker's DECISION-RELEVANT state at each consultation position
is invariant across answer/attempt histories (decision-state confluence): the
enumeration consults each answer at ITS realized state — the state induced by
enumerating all answers in one fixed order, not the state any particular
logged trajectory induced — so identifying the two is exactly the confluence
claim, and it must be argued, not assumed:

- CORRECTION (rev-3 asserted here that `_load(item)` is "the ONLY
  checker-state mutator"; that is FALSE as written, as the rev-deconfi review
  found, and the claim is withdrawn): the pinned runner has THREE
  state-mutation channels — (i) `check()` writes `last_cpu_s` on every call
  (f2b_runner.py:306); (ii) item-keyed record loads (`_load(item)` inside
  `check`, `index_labels`, `shown_definition`) mutate the `_by_urn` memo and
  the `_by_label` map; and (iii) in the SHUFFLED arm only, ANSWER-dependent
  loads occur: the term-for-definition path derives `u` from the attempted
  answer's term and calls `_entry(self.perm[u])` (f2b_runner.py:377–379), so
  WHICH records enter the base cache/label map can depend on the answer
  history [DERIVED-FROM-CODE at the verified sha `b62c3a72…`].
- The confluence argument — each mutation channel is DECISION-INERT
  [DERIVED-FROM-CODE, all three links; NOT measured]: (i) `last_cpu_s` is
  never read by any decision path and sits outside the compared decision
  triple (the audit's `triple()` discards the cpu component); (ii) `_by_urn`
  is a pure memo of a deterministic, sha-pinned derivation — an entry,
  whenever present, is byte-identical regardless of load history, so cache
  state affects only WHETHER a load occurs, never what a lookup returns; and
  given the measured 0/108 label collisions, the same holds for each
  `_by_label` entry's VALUE; (iii) the only decision path that reads the
  EVOLVING `_by_label` map is the TRUE arm's term-for-definition lookup
  (f2b_runner.py:297) — and in the true arm every load is item-keyed (no
  answer-keyed load exists on any true-arm code path), so the true arm's
  `_by_label` presence-state is a function of the item/consultation sequence
  alone, which the replay reproduces exactly; the shuffled arm's decisions
  read only construction-time-fixed structures (`label_to_urn`, `perm`,
  `meta`) plus memo-idempotent `_load`, never the evolving `_by_label` — so
  its answer-dependent mutations land only in state its own decisions never
  consult (the GS-A mirror classes share this structure over the projected
  columns). Jointly: the decision triple at every (position, answer) is
  invariant across answer and attempt histories. This is a code-reading
  argument, falsifiable by code inspection; it is NOT a measurement.
- What the measurements contribute — strictly less than confluence, said
  plainly: repeat-consultation invariance is **MEASURED** (0 violations over
  all 16,380 verify-cell decision cells × 5 same-answer repeats), but it
  probes SAME-ANSWER idempotence at each realized enumeration state in ONE
  fixed enumeration order (audit_a1.py:401–407); by itself it does NOT
  exclude cross-answer history effects (answer A changing how a later answer
  B is decided) — only the code-level argument above excludes those. And
  where real logged answers DO exist, the replay is answer-for-answer: the
  500 d-xif R1 `ifc_answer` records replayed in file order, 500/500
  concordant, stored flags matching 500/500, and both stores reproducing the
  audited cell's logged aggregates exactly [MEASURED] — but this anchors ONLY
  the extraction-instrument path; it does not anchor the unlogged attempt
  histories of the six verify-retry cells.

Honest bottom line [DERIVED]: the trajectory component is a
**coverage-equivalent SUBSTITUTE for the prescribed transcript replay — a
superset cover of the realized trajectories anchored by one genuine
answer-for-answer replay** — because no per-attempt transcript exists. Its
soundness rests on the UNMEASURED code-level confluence argument above plus
the measured same-answer repeat-invariance; a reader who rejects code-reading
as evidence should discount the §3.1(c) component to exactly that extent and
no further. The disclosure — including the confluence argument's unmeasured
status — rides every citation of the certificate. (Forward notes [ASSUMED,
direction-only]: future campaigns should persist per-attempt (item, attempt,
answer) logs so the next A1-class replay needs no substitute; and if review
wants the confluence link measured rather than code-derived, a cheap
permuted-answer-order re-enumeration diff would convert it into a measured
invariance.)

## 4. What complete C_dec = 1.0 licenses — and what it does not

**Licensed NOW, at the measured (exploratory, pre-registration) level**
[MEASURED: §0; STIPULATED: the rev-B reading vocabulary]:

- The reading of §1: kernel-runtime-STRUCTURE is INERT under the pinned
  topology — in the extensional-decision sense and no other — measured over
  the pre-registered closure (grid ∪ replay-substitute ∪ init-order). On the
  measured closure every decision is extensionally reproduced by the aligned
  deterministic answer key alone; no decision-semantic contribution beyond the
  key was detected. (Not a claim that the checker reads or does nothing else
  at runtime — §1.)
- The invariance-lemma rider at §1's stated scope [STIPULATED:
  `invariance_lemma_scope` in the artifact, licensed_iff C_dec == 1.0, now
  satisfied]: every pinned-scope F2-line endpoint — the audited +0.1507 lift,
  its CIs, the shuffled-control readings, and f2b-transfer stage-2's
  external-gold endpoints IF stage 2 runs at the identical pins — is
  bit-for-bit invariant under replacement of the kernel store by GS-A
  [MEASURED-BY-INVARIANCE, per §0's R_repro caveat: a lemma-derivation whose
  antecedent is measured directly on grid + init-order and covered on the
  trajectories via §3's substitute (contingent on §3's unmeasured confluence
  argument), not a model run]. "Future"
  runs are covered ONLY under identical re-pins; any checker/harness/schema/
  output-space/init/store change voids the lemma and requires an A1 re-run
  [STIPULATED: §7.1 note in the artifact].
- The counted circularity signature (§0): verifier-accept ⇔ membership gold
  with zero off-diagonals on all 5,504 decidable pairs — the "gold is defined
  by check()" note is a count, not an argument.
- Stage B's arm-sharing economy becomes AVAILABLE at the measured level: the
  conditional kernel-verify-retry arm may be omitted because the GS-A arm is
  bit-identical to it under the pins [STIPULATED: §5.1 conditional-arm rule,
  whose condition — the executed certificate, complete-with-§3's-substitution
  — is now measured; the REGISTERED
  form of this economy still awaits the freeze + registered re-run, §6].

**Pending REGISTRATION, not measurement** [STIPULATED: DECONF status line +
§11; DERIVED: the governance/measurement split of the header]:

- The verdict-input **KERNEL-RUNTIME-STRUCTURE-INERT** is defined by §3.2 over
  exactly what has now been measured; its registered assignment routes through
  external review → prereg freeze → the registered runner-role re-run →
  verdict-gen. This document supports the label at the measured level and
  assigns nothing.
- The §6 row-1 headline re-scoping of the F2 line (see the implication below)
  is the maintainer's to route on the registered result.

**NOT licensed at ANY scope — each clause within the binding frame, restated
without widening** [STIPULATED: §3.0/§6/§9.1, clause by clause]:

- It does NOT show kernel-authored content is generic, replaceable, or
  valueless. GS-A's strings are the kernel's strings; whether
  independently-authored plain/nonce content reproduces anything is knull-v2's
  authored-content channel, untouched and still blocked on the plain-arm
  quality-gate ruling.
- It does NOT bear on authoring economics (A-F0), consumption channels (A-E2),
  or any architecture whose store coupling is not answer→check→resample.
- It does NOT extend beyond the pinned model context: **R-1/SmolLM2-135M only;
  no extrapolation to the 100M–2B rung band is licensed by anything here** —
  the lemma quantifies over the checker, not over model scale.
- It does NOT retire the item-generation or store-addressing circularities:
  the items are rendered from the kernel's own records and every item pins the
  record that answers it; the self-authored/kernel-covered/oracle-addressed
  rider rides on [STIPULATED: PROPOSED-ASM-1017].
- It does NOT move either programme thesis. **The correctness thesis and the
  efficiency thesis both remain INCONCLUSIVE-PENDING.** A1 is a pre-ladder CPU
  attribution diagnostic: it occupies no gate rung and unlocks none (it is NOT
  G1); it bears on the ATTRIBUTION of the already-measured F2 lift — the lift
  is real and stands byte-identical in its frozen record; its runtime mechanism
  is now measured, on the complete closure, to be answer-key-structural rather
  than kernel-structural. What the lift is worth to either thesis turns on the
  still-unrun legs: alignment-vs-generic-retrieval (Stage B's Δ_align TOST/LCB
  contrast), authored-content value (knull-v2), authoring cost (A-F0), and the
  stage-2 external-gold system lift (f2b-transfer).

**The deflationary implication, labelled as implication and not conclusion**
[DERIVED, from MEASURED §0 within the STIPULATED frame; ASSUMED where marked]:
this is a **deflationary result on the correctness/efficiency question** — it
sharpens, materially, the "kernel becoming optional" question (issue #12).
On the completed evidence, the F2 line survives as: *"verify-retry against an
item-aligned deterministic answer key lifts a 135M host on this self-authored,
kernel-covered, oracle-addressed slice"* — with the kernel measured as one way
to author such a key and no kernel-specific runtime contribution detected
anywhere on the measured closure. IF this stands through registration and
Stage B does not surface an alignment-specific residue attributable to
kernel-side structure, the F2 runtime story SHOULD be renamed from
"kernel-verify-retry" to **"aligned-answer-key verify-retry"** in programme
prose [ASSUMED — a recommendation-shaped implication for the maintainer, not a
ruling; the frozen verdict objects are untouched either way]. What would
REINFLATE the kernel's runtime role is now sharply enumerable: an
alignment-specific Δ_align that only kernel-grade authoring achieves (Stage B
+ knull-v2's channel), or value on the authoring/consumption/economics axes A1
deliberately does not measure.

## 5. Relation to the f2b-transfer stage-1 endorsement — different confounds, not conflated

The two results are orthogonal probes of the SAME assessment ceiling and must
not be summed into one sentence:

- **f2b-transfer stage 1** broke the **gold-definition circularity**: it asked
  whether the membership gold — defined by the kernel's own string-equality —
  is *externally endorsable*, and blind human-anchored adjudication endorsed it
  at A = 320/333 = 0.9610 (one-sided 95% Wilson LB 0.9395, post-judge-3 FINAL)
  [MEASURED: interpretations/f2b-transfer-stage1.md §0, restated]. That is a
  claim about the gold's CONTENT contacting external understanding.
- **DECONF A1** measured the **runtime decision-equivalence question at the
  pre-registered certificate scope** (it did NOT close a read-set question —
  no read-set claim is available, §1): concordant decisions on every cell of
  grid ∪ replay-substitute ∪ init-order [MEASURED: §0]; the calibrated
  reading — every runtime decision is extensionally computable from the
  projected answer key alone — is the interpretation of that concordance on
  the measured closure, and per §1 it does not exclude decision-inert reads
  or other decision-inert runtime activity [STIPULATED/DERIVED: §1]. This
  line of inquiry concerns what the mechanism's DECISIONS depend on,
  extensionally, and is deliberately silent on whether the key's content is
  true, endorsable, or worth authoring.
- The bonus contingency links them precisely and no further: A1 count-verified
  (off-diagonals zero on all 5,504 decidable pairs) that verifier-accept ≡
  membership gold on the enumerated cells [MEASURED: §0]; f2b-t stage 1
  measured that this same membership gold agrees with an external
  human-anchored gold at 0.961 on the resolved slice. Chaining the two ("the
  runtime accept signal coincides with an externally-endorsed gold") is a
  direction-only composition — the frozen f2b-transfer design forbids inferring
  the stage-2 primary from A, and retry dynamics on the judge–kernel
  disagreement set are not a pure function of either number [ASSUMED —
  direction-only, non-load-bearing; STIPULATED: f2b-transfer design.md §2
  layer 2]. Stage 2 measures it; nothing here does.
- One economy now transfers at the measured level: the d-qa-t[:250] planned
  sub-grid is fully concordant AND the certificate holds
  (complete-with-substitution, §1/§3), so IF stage
  2 runs at the identical pins, its endpoints are covered by the invariance
  lemma and Stage B's kernel arm and a GS-A arm would be bit-identical
  [MEASURED: §0; STIPULATED: lemma scope]. The registered form of the
  arm-omission awaits the freeze + registered re-run (§4, §6).

## 6. What follows (recommendations to the coordinator/maintainer; no action taken here)

1. **Register the certificate**: external review of the completed-A1 artifact +
   prereg freeze, then the registered runner-role re-run (minutes, ~$0,
   deterministic) + verdict-gen + results-log append under runner-role
   separation [STIPULATED: DECONF status line]. The §3.1(c)
   coverage-substitution disclosure AND its code-level confluence argument
   (§3, including that argument's unmeasured status) must ride into the
   frozen record verbatim; the freeze should also adopt the extensional
   wording of the §3.0 proposition (§1's gloss) or carry that gloss verbatim,
   since mirror-concordance cannot support the literal "uses no information
   beyond" read-set wording.
2. Coordinator: register PROPOSED-ASM-1010–1017 and create P3-E-DECONF-0 /
   P3-E-DECONF-B per design §11 (no bd operation was performed by the run or by
   this document).
3. Maintainer: the §6 row-1 invariance-lemma rider wording, the
   aligned-answer-key renaming question (issue #12; §4's labelled implication),
   and Stage B's arm-omission are now unblocked at the measured level and
   should be routed on the registered result.
4. ASM-0966 (the expected-outcome extrapolation) is **resolved in its
   registered direction across all three components** (the replay component
   via the §3 substitute). The expected-direction
   disclosure should ride any citation — the value is the completed
   certificate, not surprise [STIPULATED: §3.3/§9.2].
5. Forward instrumentation note (§3): persist per-attempt (item, attempt,
   answer) logs in future campaigns so replay-class audits need no substitute
   argument; and if review wants §3's confluence link measured rather than
   code-derived, a cheap permuted-answer-order re-enumeration diff would
   convert it into a measured invariance [ASSUMED, direction-only].

---

## Epistemic register (what this interpretation relied on)

- **MEASURED:** every number in §0 (complete C_dec 40,576/40,576 and its three
  components 11,848 + 11,848 + 16,880; 0 label collisions / 108 + 108 labels;
  108/108 unique canonical texts; 0 eager-vs-lazy divergence; 0
  repeat-consultation violations; 500/500 answer-for-answer d-xif replay with
  500/500 flag matches and exact logged-aggregate reproduction; triage
  NO-OBJECT with n_discordant 0; sub-grids 1,460/1,460 and 1,592/1,592; d-ext
  4,000/4,000; the 1,860/3,644/420 decision mix; 1,673/5,924 divergence; the
  zero off-diagonal accept⇔gold contingency; all pins), restated from
  a1-complete-result.json/RESULT.md without recomputation; the f2b-replicate
  lift context and the f2b-transfer stage-1 FINAL endorsement figures,
  restated from their own artifacts. Scope discipline retained from rev-2:
  "runtime-inert" and "no runtime channel candidate" are NOT purely MEASURED —
  the measurements are the concordant decisions and the empty discordance
  list; the inertness/no-candidate readings are their stipulated/derived
  interpretation, extensional-decision only, now at the full-denominator scope
  (with §3's substitution). The measured repeat-invariance is NOT the §3
  confluence claim, which remains code-derived and unmeasured.
- **STIPULATED:** the entire interpretive frame — certificate-not-content-test,
  the §3.1 denominator (grid ∪ replay ∪ init-order), the §3.2 reading of
  complete C_dec = 1.0 as KERNEL-RUNTIME-STRUCTURE-INERT at the pinned scope,
  the four-cause triage semantics, the scoped invariance lemma and its
  identical-re-pins condition, the R-1-only scope bar, the riders — adopted
  verbatim from DECONF.md rev-B (ASM-0960–0966 + PROPOSED-ASM-1010–1017,
  registration pending) and the two GPT-5.6 reviews.
- **DERIVED (this document's own, disclosed):** the §1 extensional-equivalence
  observation and its two-fold residue (decision-inert runtime activity; the
  superset qualification), still not a read-set proof; the §3 soundness
  assessment of the answer-superset replay substitute (resting on the
  disclosed — and unmeasured — code-level decision-state-confluence argument,
  which corrects rev-3's false "only mutator" claim, plus the measured
  same-answer repeat-invariance); the §2 by-construction
  triage mapping; the §4 deflationary-implication paragraph's derivation; the
  governance/measurement split in the header.
- **ASSUMED (direction-only, never load-bearing):** the §5 chained
  accept↔external-gold composition; the §4 aligned-answer-key renaming
  recommendation; the §3/§6 per-attempt-logging instrumentation note.
- **EXTRAPOLATION (ASM-0966, registered forward projection):** that the
  registered re-run reproduces these bytes — the certificate components
  themselves are resolved in the registered direction; the byte-reproduction
  projection remains forward-looking until the registered re-run lands.
- **R_repro ≡ 1.0** is cited only as MEASURED-BY-INVARIANCE — a derivation
  inside the artifact whose lemma-antecedent is measured directly on grid +
  init-order and covered on the trajectories via §3's substitute (contingent
  on §3's unmeasured confluence argument) — never as a model run, and only
  under identical re-pins.

Neither the correctness thesis nor the efficiency thesis moves off
INCONCLUSIVE-PENDING on this result. The certificate is executed over all
three pre-registered components (C_dec = 1.0 exactly, 40,576/40,576 distinct
decision cells, grid ∪ replay ∪ init-order, triage NO-OBJECT), with the
§3.1(c) component a disclosed coverage-equivalent substitute for the
prescribed transcript replay; it carries the §3 substitution-and-confluence
disclosure wherever it is cited, remains EXPLORATORY pending the registered
freeze + re-run, and reads — at its pinned R-1/135M scope and nowhere wider —
as EXTENSIONAL DECISION equivalence: the kernel's structural fields change no
runtime decision on the measured closure, with no decision-semantic
contribution beyond the projected answer key detected (not a read-set or
literal-runtime claim); the F2 verify-retry lift stands as an
aligned-answer-key property, with the kernel as one way to author such a key.
