# P3-D-HON — KOT-HON/1: the honesty-first asymmetric-utility score (programme-wide evaluation principle)

> **Status: [DESIGN, rev 1] — maintainer-directed (issue #18, 2026-07-11).
> Nothing here is frozen, pre-registered, scheduled, or run; no verdict,
> audit, frozen object, floor, or registered ruling is touched or amended.
> The assumption entries in §6 are **PROPOSED-ASM ASM-1330…ASM-1339** (a
> fresh DISJOINT block; NOT in `registry/assumptions.jsonl` — this document
> performs no registry edit; the coordinator registers them; the id-space was
> checked disjoint against the ledger and all docs on 2026-07-11). Adoption
> of KOT-HON/1 into any frozen claim surface is a maintainer + review-gate
> decision; this document supplies the design and the worked application.
> Author: Fable, design agent (`kern/fable-designer`), 2026-07-11. No
> git/bd/kb operation is performed by this document.
>
> **The maintainer's directive, restated (issue #18):** treat "I don't know"
> as a MISS (not a pass), but penalise a WRONG answer far more (~−2 to −5 vs
> +1 for a correct answer), so a system is incentivised to answer only when
> sure; a system with ~0 wrong answers plus honest abstentions then reads as
> a STRENGTH that a raw answer-rate metric hides. Caveat, also the
> maintainer's: standard benchmarks and the AI index do not reward this, so
> competing there may need a SEPARATE non-penalised variant.
>
> **Inputs read at source, in full:**
> `docs/next/interpretations/codevert-g1.md` (the R_q honest-abstention
> result — §1.2 table, §3b abstention-charging flag, the rev-1 scope riders
> on "zero wrong answers"); `docs/next/programme-3-neurosymbolic-architecture.md`
> (KOT-AI-INDEX/2 / ASM-0811 vector rule, §2.0 threat model incl. the named
> "abstention gaming" channel, §2.5 house statistics, W1/G4, R3
> wrong-with-provenance-is-worse-than-refusal); `registry/assumptions.jsonl`
> (id-space check); house design-doc conventions
> (`docs/next/design/CODEVERT.md` header + tag discipline).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` restates a
> registry/analysis artifact strictly inside its envelope (every
> gold-dependent CODEVERT number below additionally carries
> **[PROVISIONAL-ON-LLM-PROXY]** and is void on human re-annotation, per
> ASM-1113); `[DERIVED]` is this document's own arithmetic/rule-application
> from MEASURED facts; `[STIPULATED]` / `[PROPOSED-ASM: id]` are design
> choices; `[ESTIMATED]` is a projection with no measurement behind it;
> nothing here is a feasibility conclusion or a verdict.

---

## 0. One-paragraph summary

KOT-HON/1 is a per-item asymmetric-utility score: **+1** for a correct
answer, **0** for an explicit fail-closed abstention (a MISS — it stays in
the denominator and forgoes value; it is never a pass), **−λ** for a wrong
answer, with the penalty pinned in the band **λ ∈ [2, 5], default λ = 3**.
The band is not arbitrary: λ fixes the rational confidence threshold
t\* = λ/(1+λ) at which answering beats abstaining (λ=2 → 2/3, λ=3 → 3/4,
λ=5 → 5/6), so pinning λ pins the abstention policy a calibrated system
should implement. Applied to CODEVERT G1's answer-quality legs
[MEASURED + PROVISIONAL-ON-LLM-PROXY inputs; recompute DERIVED,
exploratory]: on the 160 gold-answerable queries the system scored 123
correct, 37 explicit UNKNOWN-INCOMPLETE abstentions, **0 wrong** — so
S_λ = **0.7688 at every λ in the band**, numerically equal to the raw R_q
that reads as a floor FAIL, while a hypothetical always-answering system
with the *identical* raw R_q would score **0.3063 / 0.0750 / −0.3875** at
λ = 2/3/5. λ-invariance is the signature of the honest profile: the entire
shortfall is forgone value, none of it is negative value — exactly the
strength the raw metric hides and the maintainer's directive names. The
element-level precision leg (32 wrong of 474, all one AnnAssign defect)
scores S_3 = 0.7300 vs raw 0.9325 — the score correctly taxes real wrongs
harder than raw precision does. Because standard benchmarks and
KOT-AI-INDEX/2 head-to-heads reward raw accuracy and punish abstention, the
programme carries **two named system variants** — **S-HON** (honesty-first,
the programme's default identity, abstention policy tuned to λ) and
**S-BENCH** (non-penalised, forced-answer, for AI-index/W1 head-to-heads) —
never mixed, both disclosed, with the delta INDEX(S-BENCH) − INDEX(S-HON)
published as the measured **price of honesty**. Nothing retroactive: G1's
mechanical verdict on the ASM-1030 floors as written stands untouched; this
score binds FUTURE preregs and co-reports beside frozen results.

---

## 1. The score — KOT-HON/1, exact form

### 1.1 Definition [PROPOSED-ASM: ASM-1330]

For an evaluation surface with item set Q (|Q| = N) where the system's
action on each item q is either an answer or an abstention:

- **outcome(q) = CORRECT** — an answer was given and it is gold-equal under
  the surface's pinned gold semantics;
- **outcome(q) = WRONG** — an answer was given and it is not gold-equal.
  This INCLUDES a silent empty answer on a gold-answerable item: emptiness
  delivered as an answer is a wrong answer, not an abstention (the
  negative-validity leg exists to police exactly this);
- **outcome(q) = ABSTAIN** — an EXPLICIT, fail-closed abstention carrying a
  machine-readable reason code (the `UNKNOWN-INCOMPLETE(reason)` shape).
  Only explicit abstention scores 0; anything else that fails to be correct
  is WRONG. "I don't know" without a reason code is still ABSTAIN-class for
  scoring but is flagged in the co-report (reasonless abstention is a
  product defect even when it is not an honesty defect).

Per-item utility and the score:

```
u_λ(q) = +1   if CORRECT
          0   if ABSTAIN        (a MISS: in the denominator, forgoes value)
         −λ   if WRONG          λ ∈ [2, 5], pinned per surface, default 3

S_λ(Q) = (1/N) · Σ_{q∈Q} u_λ(q)          range: [−λ, +1]
```

**The denominator is all in-scope items.** Abstentions are never removed
from N. Removing them (scoring over answered-queries only) is the
option-(iii) move the G0/G1 interpretations flagged as epistemically
dangerous — it converts a miss into a non-event. Under KOT-HON/1 an
abstention costs exactly the forgone +1, no more (not an error) and no less
(not a pass).

### 1.2 Decomposition and the threshold theorem [DERIVED, elementary]

Let a = answer rate = (C+W)/N, p = precision-on-answered = C/(C+W),
r = raw recall = C/N. Then:

```
S_λ = a·(p·(1+λ) − λ) = r − λ·(W/N)
```

Two readings fall out:

1. **S_λ is the raw metric minus an honesty tax.** S_λ = raw recall minus
   λ × wrong-rate. A system with zero wrong answers has S_λ = r at every λ
   — **λ-invariance of S_λ is the machine-checkable signature of a clean
   profile**, and the sensitivity co-report (§2.2) makes it visible.
2. **The threshold theorem.** For an item where the system's calibrated
   confidence of being correct is p_q, the expected utility of answering is
   p_q·(1+λ) − λ, which is positive iff **p_q > t\* = λ/(1+λ)**. Pinning λ
   therefore pins the rational abstention policy:

   | λ | t\* (answer only if confidence >) |
   |---|---|
   | 2 | 0.667 |
   | 3 | 0.750 (default) |
   | 4 | 0.800 |
   | 5 | 0.833 |

### 1.3 Why the band is [2, 5] — justification of both ends
[PROPOSED-ASM: ASM-1331]

- **λ ≥ 2 (the floor of the band):** at λ = 1, a calibrated coin-flip
  (p = 0.5) is EV-neutral and anything above 0.5 is profitable guessing —
  the score would still reward weakly-confident volunteering. λ = 2 is the
  smallest integer penalty at which answering requires better than 2:1
  confidence (t\* = 2/3), i.e. the smallest penalty that makes
  low-confidence guessing strictly irrational. (Classical negative marking
  — e.g. −1/4 on 5-option multiple choice — is tuned to make blind guessing
  EV-*neutral*; the maintainer's directive requires guessing to be
  EV-*negative*, hence strictly above that regime.)
- **λ ≤ 5 (the ceiling of the band):** two independent reasons.
  (a) *Incentive:* t\*(5) = 5/6 ≈ 0.833; above λ = 5 the score pushes a
  system toward degenerate abstention on everything short of near-certainty
  — and a well-calibrated system operating near a 0.95-precision product
  bar should plainly still be answering, not hedging.
  (b) *Statistics:* a single wrong item moves S_λ by (1+λ)/N; at the
  programme's realistic gold sizes (n ≈ 160–500) λ > 5 makes one wrong
  answer dominate the endpoint's margin and turns the score into a noisy
  wrong-answer counter. The band keeps single-item influence bounded while
  keeping wrongs categorically more expensive than misses.
- **Why NOT λ = π/(1−π) for a precision floor π** (e.g. λ = 19 for the
  ASM-1030 0.95 precision floor): the precision floor is a bar on the
  *delivered answer set*, not the marginal-answer indifference point.
  Setting t\* equal to the product bar collapses the score into an
  abstention machine and (per (b) above) makes a single wrong item at
  n = 160 swing the score by 0.125 — larger than any margin the programme
  registers. Precision floors and S_λ are complementary instruments, not
  substitutes (§2.1).

### 1.4 Calibrating λ [PROPOSED-ASM: ASM-1332]

1. **Default:** λ = 3 (t\* = 0.75) for any surface that does not declare a
   harm ratio.
2. **Surface-declared harm ratio:** where a deployment surface can state
   the cost ratio of a delivered-wrong answer to the value of a
   delivered-correct one (rework + downstream-trust damage vs answer
   value), pin λ to that ratio, clamped to [2, 5]; the a5-nl S2 lesson —
   wrong-with-provenance is WORSE than refusal [MEASURED:
   registry/verdicts/a5-nl.json S2 kill, 5.0% wrong-with-provenance;
   restated as programme-3 risk R3] — is the programme's standing evidence
   that this ratio is materially above 1 for every provenance-carrying
   surface.
3. **Pinned at prereg-freeze, before any number exists.** λ is part of the
   endpoint. Changing λ after a readout is an endpoint change under the
   ASM-1116-class discipline — i.e. it is floor-shopping and is treated
   exactly as the G0/G1 interpretations treat denominator re-pins:
   registered before any re-scored readout, as-written numbers carried
   beside it in perpetuity.
4. **Mandatory sensitivity co-report:** every S_λ readout reports S_2 and
   S_5 beside the pinned S_λ. (For a clean profile these coincide — the
   λ-invariance signature; divergence quantifies how much of the score is
   exposure to the penalty choice.)

### 1.5 Guards [PROPOSED-ASM: ASM-1333, ASM-1334]

- **Degenerate-abstention guard [ASM-1334]:** abstain-always scores
  S_λ = 0. Every KOT-HON/1 endpoint therefore carries a pre-registered
  **answer-rate (or coverage) co-floor** — or reports the full
  risk–coverage curve — so the score cannot be gamed by abstaining on hard
  items. S_λ measures honesty of the answering behaviour; coverage remains
  its own axis (in CODEVERT terms: κ legs are untouched by this document,
  §2.1).
- **The co-report vector [ASM-1333]:** the S_λ scalar is never quoted
  without: answer rate a, precision-on-answered p, abstention rate (split:
  reasoned vs reasonless), wrong-rate W/N, raw recall r, and the S_2/S_5
  sensitivity pair. This mirrors the ASM-0811 rule that no index scalar
  travels without its vector.
- **Statistical treatment:** S_λ endpoints take CIs by bootstrap over
  items (hierarchical where item families exist), and a margin claim
  requires the LCB clearing the margin — the §2.5 house rules of
  programme-3 (ASM-0813) apply verbatim; no new statistics are invented
  here.

---

## 2. KOT-HON/1 as a PROGRAMME-WIDE principle — where it binds

### 2.1 Scope and non-retroactivity [PROPOSED-ASM: ASM-1335, ASM-1339]

- **Binds (future):** every new prereg whose surface has an item-level
  answer/abstain distinction — CODEVERT-class query answering, H-VL
  verifier-loop outputs, H-PS/NLB parse-or-abstain front-ends, any
  store-backed QA leg — SHOULD carry a KOT-HON/1 endpoint (pinned λ,
  co-floor, co-report vector) alongside whatever precision/recall floors it
  registers. Precision floors police the delivered answer set; S_λ prices
  the answer/abstain policy; coverage floors police reach. They are three
  instruments, not one.
- **Does not apply:** legs with no abstention action (pure coverage
  censuses, κ agreement legs, byte-determinism gates) — they keep their own
  endpoints [ASM-1339].
- **Non-retroactive [ASM-1335]:** no frozen floor, endpoint, or verdict is
  amended. CODEVERT G1's mechanical verdict on the ASM-1030 floors as
  written stands (the G1 interpretation's option (i) — never suppressed).
  §3 below is an **exploratory co-reading carried beside the as-written
  numbers**, not a re-scoring; whether any frozen surface is ever re-pinned
  onto KOT-HON/1 (the G1 option-(iii) route) remains a maintainer +
  review-gate decision. What KOT-HON/1 contributes to that decision is the
  registered, principled form option (iii) previously lacked: a
  pre-registrable score in which abstention is a MISS, not a pass — so a
  re-pin, if ever taken, is not an ad-hoc denominator edit.

### 2.2 Relation to the G1 §3b flag

The G1 interpretation's §3b lists four semantics for abstention-charging
and states there is no unique mechanical completion. KOT-HON/1 is a
maintainer-directed selection among them — closest to "count
UNKNOWN-INCOMPLETE as a first-class outcome with its own utility" — with
the directive supplying exactly the judgment (the harm asymmetry) that §3b
said Fable could not supply alone. The floors-as-written path and the
KOT-HON/1 path now BOTH exist as registered shapes; the review gate
arbitrates adoption per surface.

---

## 3. Applied to CODEVERT G1 — the asymmetric recompute

All inputs [MEASURED + PROVISIONAL-ON-LLM-PROXY:
docs/next/interpretations/codevert-g1.md §1.2 + §9; g1-endpoints-proxygold
via that document]; all recomputes [DERIVED, exploratory per §2.1 —
verdict-input for the maintainer's §3b/option-(iii) decision, changing no
verdict, void on human re-annotation of the 200-query proxy gold]
[PROPOSED-ASM: ASM-1336].

### 3.1 Query level — the R_q leg (160 gold-answerable queries)

Counts: C = 160 − 37 = **123 correct**, A = **37 abstentions** (100%
explicit `UNKNOWN-INCOMPLETE`, no silent empties — neg-validity 1.0),
W = **0 wrong** (zero wrong PROVED answers on this leg; the scope rider
from G1 rev-1 carries: precision is scored over proved queries only, and
the AnnAssign defect lives on the element leg below, not here).

| score | G1 as measured (honest abstainer) | counterfactual: same raw R_q, forced-answer (123 right / 37 wrong) |
|---|---|---|
| raw R_q (floor ≥ 0.90) | **0.7688** — FAIL at point | **0.7688** — identical FAIL; the raw metric cannot tell them apart |
| S_2 | **0.7688** | 0.3063 |
| S_3 (default) | **0.7688** | 0.0750 |
| S_5 | **0.7688** | −0.3875 |

Readings [DERIVED]:

- **λ-invariance:** S_2 = S_3 = S_5 = raw recall, because W = 0. The
  sensitivity co-report degenerates to a single number — the §1.2
  signature of a clean profile, achieved exactly.
- **The separation the raw floor hides:** the G1 interpretation itself
  notes the R_q floor as written "cannot distinguish this instrument from
  one that guessed and was wrong 23% of the time." Under KOT-HON/1 the
  separation is 0.46 points at λ = 2 and 1.16 points at λ = 5 — the
  guesser goes to ~0 or negative while the honest abstainer keeps its full
  recall. **This is the maintainer's directive realised in the measured
  numbers: near-0 wrong + honest abstentions reads as a strength, not a
  22%-of-floor miss.**
- **The score still charges the miss:** S_3 = 0.7688, not 1.0. The 37
  abstentions cost 0.2312 of forgone value — an honest instrument with a
  coverage problem, said honestly. Under the §1.5 guard this leg would be
  read WITH its answer-rate co-floor (a = 123/160 = 0.7688 here), so the
  profile cannot be mistaken for, or gamed into, abstention-washing.

### 3.2 Element level — the precision leg (474 proved elements)

Counts: C = 442, W = 32 (all 32 the single enumerated AnnAssign extractor
defect), A = 0 (abstentions are not element-scored on this leg).

| score | G1 as measured | post-AnnAssign-fix projection |
|---|---|---|
| raw precision (floor ≥ 0.95) | **0.9325** — FAIL at point | 1.0 **[ESTIMATED — must be re-measured on the pinned §3a re-run; adaptive/in-sample caveat carries]** |
| S_2 | 0.7975 | 1.0 [ESTIMATED] |
| S_3 (default) | **0.7300** | 1.0 [ESTIMATED] |
| S_5 | 0.5949 | 1.0 [ESTIMATED] |

Reading [DERIVED]: on real wrongs the asymmetric score is HARSHER than the
raw metric (0.7300 vs 0.9325 at λ = 3) — by design. KOT-HON/1 is not a
leniency instrument: it relocates the penalty from honest misses onto
actual wrongs. The G1 profile earns its §3.1 strength only because its
wrongs are confined to one enumerated, mechanically-specified defect; had
the 32 wrongs been diffuse, S_λ would have said so louder than precision
does. The S_2–S_5 spread (0.80 → 0.59) is the sensitivity signal §1.4
promises: this leg IS exposed to the penalty choice, exactly because it
contains real wrongs.

### 3.3 Negative-answer validity leg (6 gold-empty queries)

C = 6, W = 0, A = 0 → S_λ = **1.0** at every λ [DERIVED]. Correct empty
answers are correct answers; no silent-empty pathology exists to charge.

### 3.4 Scope note on the combined read

The 200-query adjudicated proxy gold publishes two scored legs used above
(160 gold-answerable; 6 gold-empty). An illustrative combined query-level
read over those 166: C = 129, A = 37, W = 0 → S_λ = **0.7771**,
λ-invariant [DERIVED]. The remaining 34 of the 200 are not in either
published scored leg and are excluded here — no number is invented for
them. Every figure in §3 inherits the G1 riders in full: agent-selected
pool (sensitivity bands, never generalization CIs), LLM proxy gold (void on
human re-annotation, common-mode error unbounded by the 0.915 agreement),
and the where_defined hazard bimodality disclosure.

---

## 4. The benchmark caveat — the dual-variant rule and programme-3

### 4.1 The problem, stated plainly

Standard benchmarks (and KOT-AI-INDEX/2, correctly, for W1 comparability)
score raw accuracy: an abstention is marked wrong, and no wrong answer is
penalised beyond the forgone mark. A system whose abstention policy is
tuned to t\* = 0.75 is structurally handicapped on such surfaces — it
donates every item in its (t\*, certainty) confidence band that a
forced-answer competitor would convert at better-than-chance rates. The
maintainer's caveat is accepted in full: honesty-first and
benchmark-competitive are different operating points of the same system,
and pretending one number serves both is how the strength gets hidden
(internal surfaces) or the index gets lost (external surfaces).

### 4.2 The dual-variant rule [PROPOSED-ASM: ASM-1337]

Two NAMED variants of any Programme-3 system entering external comparison:

- **S-HON (honesty-first)** — the programme's default identity and the
  variant every internal claim, product claim, and KOT-HON/1 endpoint is
  about: fail-closed, explicit reasoned abstention, abstention policy tuned
  to the surface's pinned λ. If abstention behaviour is trained (selective
  prediction, calibrated parse confidence per H-PS), it is trained here.
- **S-BENCH (non-penalised)** — the SAME architecture and store with the
  abstention policy disabled or relaxed to forced-answer (argmax under the
  benchmark's format), tuned for raw accuracy, entered in AI-index/W1/G4
  head-to-heads and any external leaderboard. S-BENCH makes NO honesty,
  fail-closedness, or provenance claim, ever; a wrong S-BENCH answer is an
  accepted cost of the comparison surface, not a product defect of S-HON.

Rules of the road:

1. **Disclosure:** every claim surface names which variant produced its
   numbers. Mixing variants in one headline is prohibited.
2. **Shared substrate:** S-HON and S-BENCH share weights/store/engine
   wherever architecturally possible, so the published delta
   **INDEX(S-BENCH) − INDEX(S-HON)** is a clean measurement of the **price
   of honesty** on that suite — itself a standing programme deliverable
   (if the price is near zero, honesty is free and S-HON can compete
   as-is; if it is large, that is a real finding about the benchmark, the
   calibration, or both).
3. **Symmetric hygiene:** decontamination, sealed-eval, threat-model, and
   frontier-builder machinery (programme-3 §2) apply to BOTH variants;
   S-BENCH gets no exemption because it is "just for the leaderboard".
4. **Training separation:** if S-HON's abstention behaviour is trained in,
   S-BENCH must not silently inherit answer-suppression (it would sandbag
   the head-to-head); conversely S-HON is never graded against
   raw-accuracy floors written for S-BENCH. Each prereg names which
   variant each endpoint binds.

### 4.3 How both factor into programme-3 [PROPOSED-ASM: ASM-1338]

- **W1/G4 head-to-heads:** fought by **S-BENCH** under KOT-AI-INDEX/2 as
  frozen — the headline index stays raw-accuracy-normalised, because W1's
  legitimacy rests on comparability with comparators that do not share our
  abstention ideology. No change to ASM-0810/0811 is proposed.
- **The index vector grows a diagnostic column:** KOT-AI-INDEX/2 already
  mandates refusal/abstention rates in the published vector (ASM-0811) and
  its threat model already names "abstention gaming" as an index-games
  channel (§2.0/ASM-0812). KOT-HON/1 supplies the missing instrument for
  both: S_λ (pinned λ = 3, with S_2/S_5) is co-reported per domain in the
  index vector for any abstention-capable arm — **diagnostic, never the
  headline scalar** — and the §1.5 answer-rate co-floor is the mechanised
  counter the threat model can now point at for abstention gaming.
  (Operationally this lands as a P3-D-INDEX freeze input, subject to that
  bead's own review path; this document does not edit the frozen framework
  spec.)
- **S-HON is where the programme's product claims live:** the
  "aligned typed store with honest incompleteness" success mode that
  feasibility-synthesis v3 §4 points at, and that G1-forward strengthened
  direction-only, is an S-HON-shaped claim. KOT-HON/1 is the score under
  which that shape is legible as a strength; the CODEVERT §3 recompute is
  its first worked instance.
- **Both ledgers travel:** an eventual product/W1 publication reports the
  S-BENCH index (comparability), the S-HON KOT-HON/1 vector (honesty), and
  the price-of-honesty delta — three numbers, three meanings, never
  collapsed into one.

---

## 5. Honest limits of this design

1. **λ is a judgment, bounded but not derived.** The band ends are
   anchored (§1.3) but the pin inside the band encodes a harm ratio no
   current experiment measures; the "product utility of abstention-heavy
   answers" gap the G1 interpretation names ([UNMEASURED], its §7.4)
   is narrowed by this design, not closed. A G2/G4-class measurement of
   real abstention cost would let λ be evidence-set rather than
   directive-set.
2. **The §3 recompute inherits every G1 rider** — LLM proxy gold (void on
   human re-annotation), agent-selected pool, hazard bimodality — and is
   exploratory beside the as-written verdict, per ASM-1335/1336.
3. **S_λ does not measure coverage** and must never be quoted as if it
   did; the co-floor guard (§1.5) is load-bearing, not decorative.
4. **The dual-variant rule creates a real maintenance cost** (two tuned
   operating points, two eval tracks) and a real communication hazard
   (variant confusion); the disclosure rule is the mitigation, not a
   solution.
5. **Nothing here is registered yet.** ASM-1330…1339 are PROPOSED; the
   coordinator registers; the maintainer + review gate own adoption into
   any frozen surface.

---

## 6. PROPOSED-ASM block (ASM-1330…ASM-1339) — for coordinator registration

Fresh disjoint block; ledger and doc-space checked free of ASM-13xx on
2026-07-11. Each row: `tag = STIPULATED` (design choices) except where
noted; `backing_ref = docs/next/design/honesty-first-scoring.md` + the
maintainer's issue-#18 directive (2026-07-11); `owner = maintainer via
kern/fable-designer`.

| id | claim (self-contained) |
|---|---|
| **ASM-1330** | KOT-HON/1 per-item utility is u_λ = +1 correct / 0 explicit fail-closed abstention (a MISS: stays in the denominator) / −λ wrong; a silent empty answer on an answerable item is WRONG, not an abstention; S_λ = mean u_λ over ALL in-scope items; abstentions are never removed from the denominator. |
| **ASM-1331** | The penalty band is λ ∈ [2, 5], default λ = 3; rationale: λ fixes the rational confidence threshold t\* = λ/(1+λ) (2/3 … 5/6), making sub-t\* guessing strictly EV-negative while bounding single-item influence (1+λ)/N at programme gold sizes; λ is NOT set to precision-floor odds π/(1−π). |
| **ASM-1332** | λ is pinned per surface at prereg-freeze, before any number exists — from a declared wrong:correct harm ratio clamped to [2, 5] where the surface declares one, else default 3; changing λ after a readout is an endpoint version change (ASM-1116-class discipline: registered before any re-scored readout, as-written numbers carried beside in perpetuity); S_2 and S_5 are mandatory sensitivity co-reports. |
| **ASM-1333** | The S_λ scalar never travels without its vector: answer rate, precision-on-answered, abstention rate (reasoned vs reasonless split), wrong-rate, raw recall, and the S_2/S_5 pair; CIs by item-level (hierarchical) bootstrap per the ASM-0813 house rules, margin claims by LCB. |
| **ASM-1334** | Degenerate-abstention guard: abstain-always scores S_λ = 0 and FAILS; every KOT-HON/1 endpoint carries a pre-registered answer-rate/coverage co-floor or a full risk–coverage curve; S_λ prices answering honesty only — coverage remains a separate axis with its own endpoints. |
| **ASM-1335** | Non-retroactivity: KOT-HON/1 amends no frozen floor, endpoint, or verdict; the CODEVERT G1 mechanical verdict on the ASM-1030 floors as written stands; applying KOT-HON/1 to any frozen result is an exploratory co-reading carried beside the as-written numbers; re-pinning any frozen surface onto KOT-HON/1 (the G1 option-(iii) route) is a maintainer + review-gate decision. |
| **ASM-1336** | The CODEVERT G1 asymmetric co-reading is [DERIVED, exploratory, PROVISIONAL-ON-LLM-PROXY, void on human re-annotation]: R_q leg (160 gold-answerable) C=123/A=37/W=0 → S_λ = 0.7688 λ-invariant vs 0.3063/0.0750/−0.3875 for a forced-answer system at identical raw R_q; precision leg (474 elements, 32 AnnAssign wrongs) S_3 = 0.7300 vs raw 0.9325; neg-validity leg 6/6 → 1.0; it licenses no verdict change. |
| **ASM-1337** | Dual-variant rule: S-HON (honesty-first, fail-closed reasoned abstention tuned to the pinned λ) is the programme's default identity and the subject of all product/honesty claims; S-BENCH (non-penalised forced-answer, same architecture/store where possible) is the ONLY variant entered in AI-index/W1/G4 head-to-heads and external leaderboards and makes no honesty/provenance claim; variant identity is disclosed on every claim surface; numbers are never mixed; each prereg names which variant each endpoint binds. |
| **ASM-1338** | Programme-3 integration: the KOT-AI-INDEX/2 headline stays raw-accuracy-normalised and W1 is fought by S-BENCH (no change to ASM-0810/0811); S_λ (λ=3, with S_2/S_5) is co-reported per domain in the index vector for abstention-capable arms as a diagnostic, never the headline; the §1.5 answer-rate co-floor is the mechanised counter for the threat model's named "abstention gaming" channel; the price-of-honesty delta INDEX(S-BENCH) − INDEX(S-HON) is a mandatory published figure wherever both variants run; landing these in the frozen framework goes through P3-D-INDEX's own review path. |
| **ASM-1339** | Scope: KOT-HON/1 applies to item-level answer/abstain/wrong surfaces (query answering, verifier-loop outputs, parse-or-abstain front-ends, store-backed QA); it does not apply to legs without an abstention action (coverage censuses, κ agreement legs, determinism gates), which retain their own endpoints. |

---

## 7. Self-check gate (per session governance)

- Every design choice carries a PROPOSED-ASM id; every empirical number is
  tagged [MEASURED (+PROVISIONAL-ON-LLM-PROXY where gold-dependent)],
  [DERIVED], or [ESTIMATED]; the one projection (post-fix precision 1.0)
  is marked ESTIMATED with the adaptive/in-sample caveat carried. ✅
- Arithmetic checks: 123/160 = 0.76875 → 0.7688 (matches the published
  R_q); (123−2·37)/160 = 0.30625; (123−3·37)/160 = 0.075;
  (123−5·37)/160 = −0.3875; 442/474 = 0.9325; (442−2·32)/474 = 0.7975;
  (442−3·32)/474 = 0.7300; (442−5·32)/474 = 0.5949; 129/166 = 0.7771. ✅
- No frozen object, verdict, floor, registry line, or bead is touched;
  ASM-1330…1339 are PROPOSED only; the id-space was checked disjoint. ✅
- No feasibility conclusion is stated; adoption decisions are reserved to
  the maintainer + review gate; the G1 option-(iii) reservation is
  restated, not resolved. ✅
- No @handle/account strings appear. ✅
