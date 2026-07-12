# g2-import-v2 — INSTRUMENT REPAIR + re-mint design (DRAFT; nothing frozen, nothing run)

- **Author:** Fable (experiment-design role), 2026-07-12. This document DESIGNS the
  repair-and-re-mint the g2-import INSTRUMENT-INVALID verdict mandates ("no conclusion;
  repair and mint a new frozen run" — plan §7.7 row 5) and the steering read
  (docs/next/analysis/steering-read-2026-07-12.md §3.2, §4) ranks as the best
  evidence-per-dollar move on the board. It changes NO frozen record, NO verdict, NO
  label file, and writes NOTHING to `registry/assumptions.jsonl` (PROPOSED-ASM only, §10).
- **Companion draft record:** `registry/experiments/g2-import-v2.json` (status DRAFT;
  freeze is a coordinator action, §9).
- **Sources read at source:** `registry/experiments/g2-import.json` (FROZEN, sha
  862e374a…), `registry/verdicts/g2-import.json` (INSTRUMENT-INVALID, fired rule 0),
  `poc/ontology-import-g2/` (analysis-output.json, result.json, all six per-judge
  response files, materials/), `poc/g2/materials/` (rubric, items, probes, calibration),
  `docs/next/interpretations/g2-import.md`, `docs/next/analysis/steering-read-2026-07-12.md`
  §2.2/§3.2/§4, `docs/next/design/ontology-import-plan.md` §§7.1–7.8.
- **Rider, verbatim, binding on every verdict-adjacent sentence in this design:**
  *"PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots; point-estimate
  engineering gate, not statistical superiority; soft non-binding typing only — never
  hard laws; no feasibility conclusion."*
- **This document draws NO feasibility conclusion and NO conclusion about H-SOFT.** The
  v1 primary "pass" (0.68 vs 0.39, McNemar p=7.0e-5) is a GO-SHAPED signal under an
  invalid instrument — it licenses nothing and is used below ONLY to size the repair.

---

## 1. Diagnosis — where κ_A3 actually died (all MEASURED from v1 artifacts)

The v1 instrument gate failed on exactly one channel: **κ_A3 = 0.2859 < 0.40**
(κ_A1 = 0.5273, κ_A2 = 0.4296; decisive 84/84 every judge×arm; deranged-probe
false-satisfaction 0/20 everywhere; pins ok; zero blinding hits).

Anatomy of the A3 judge-pair disagreement (from the per-judge response files, labels sha
ed0c000e…):

| quantity | value |
|---|---|
| A3 agreement table (pA,pB) | yes-yes 42, yes-no 16, no-yes 11, no-no 15 → raw agreement 57/84 = 0.679 |
| disagreements by rule | R3 15/42, R4 9/34, R1 3/8 |
| disagreements by form | existential 9, range 8, domain 7, subClassOf 3 |
| hedge markers per arm | A1 **0/84**; A2 83/84 "Normally", 0 "Typically"; A3 83/84 "Normally" **+ 63/84 "Typically"** (FrameNet valency tails; mean item length 245→305 chars A2→A3) |
| hedges among the 27 A3 disagreements | 26/27 contain "Normally", **24/27 contain "Typically"** (vs 63/84 = 0.75 base rate) |
| κ vs hedge gradient | 0 hedges → κ 0.527; one hedge layer → κ 0.430; two stacked hedge layers → κ 0.286 |

**Mechanism (EXTRAPOLATION, load-bearing only for the repair design, not for any
result):** the v1 judge question — *"does it hold in ALL normal cases the concept
applies to?"* — is well-defined for unhedged sentences and UNDEFINED for hedged ones. An
A3 item is a composite of one unhedged head ("In every case …") plus one "Normally …"
sentence plus (usually) one "Typically …" sentence. The rubric never says how to score
the hedged sentences: judge-pA tends to read "Normally P" as the hedged claim it
literally makes (true if P is the usual case), judge-pB intermittently applies the
ALL-normal-cases standard to the hedged tail (false if any ordinary exception exists) —
and vice versa item-by-item, which is why the disagreement is two-sided (16 vs 11). The
predecessor g2 baseline items and the A1 arm are 100% unhedged, which is exactly why
they were stable under the same rubric. The instrument, not the content, is what varies
across the arm ladder's κ collapse.

The repair therefore targets the RUBRIC's modality semantics, plus the two process
failures the steering read names: the gate channel was never exercised at the operating
point before freeze (no pilot), and the breadth control was reported-only (no A1-vs-A3
separation endpoint), letting A1's 55/84 lift eat the interpretation.

---

## 2. Repair 1 — rubric tightening for hedged modality (the κ fix)

**Principle (estimand-preserving):** the estimand is unchanged — per-slot BLIND
ordinary-meaning soundness of the rendered statement, judge-pA construction,
vacuity-zeroed, fixed denominator 84, on the SAME 84 kernel-v0 slots and the SAME
byte-identical arm renderings (all four `arm-*.jsonl` files re-pinned at their v1
hashes; no regeneration). What changes is only the ADJUDICATION RULE for compound
statements: each sentence is scored at its own stated force. For a fully unhedged
statement the new rule is extensionally identical to the old one — and the A0 baseline
(g2 items.jsonl) and A1 arm contain ZERO hedge markers (measured, §1), so the frozen
33/84 baseline constant and the breadth control are read under an unchanged standard.
This is a disambiguation of what "the statement is true" means for hedged text, not a
new quantity; it is checked mechanically at freeze (§9 step 4b).

**New prompt template `prompt-template-v2.txt` (draft text, to be pinned at freeze;
identical for every arm and both judges — no arm-identity leak; hedge instructions are
generic):**

```text
You are an independent judge of short statements about the meaning of everyday English
words. Judge ONLY by the ordinary meaning of the quoted concept (the parenthetical, if
any, tells you which sense of the word is meant). Do not use any tools. This is a single
standalone question.

{{ITEM}}

A statement may contain several sentences of different strengths. Read each sentence at
its own stated strength:
- A sentence with no hedge ("Every ...", "In every case ...", "Whenever ...") claims
  that the concept's ordinary meaning guarantees it in ALL normal cases. It is true only
  if that guarantee holds.
- A sentence hedged with "Normally" or "Typically" claims only how things usually or
  characteristically are for this concept. It is true if ordinary meaning makes it the
  usual or characteristic case; the existence of exceptions does NOT make it false. It
  is false if it misdescribes even the usual case.

Question: Is the whole statement true of the concept's ordinary meaning, with every
sentence read at its own stated strength?
Answer "yes" only if EVERY sentence is true at its stated strength.
Answer "no" if ANY sentence is false at its stated strength — but never answer "no"
merely because a "Normally"/"Typically" sentence has exceptions.
Answer with a single raw JSON object and nothing else — no markdown fence, no prose:
{"answer": "yes"} — every sentence is true at its stated strength
{"answer": "no"} — some sentence is false at its stated strength
{"answer": "cannot-say"} — only if the statement is genuinely undecidable for this concept
```

Judge invocations, output schema, `{yes,no,cannot-say}` vocabulary, statelessness,
blinding scans, first-valid-answer-final: all unchanged from the v1/directive-#11
protocol. Judges unchanged: pA = GPT-5.6-Sol via the pinned codex CLI family (primary
stand-in), pB = claude-haiku-4-5 via headless claude CLI (sensitivity; vendor-family
overlap with the materials' authoring agents DISCLOSED, never sole gold).

**Comparability disclosure (mandatory in the readout):** v2 labels are minted under a
different rubric than v1; no v2 number may be row-merged or trend-compared with the
quarantined v1 labels except as "instrument-repair before/after" instrument evidence.
The A0-vs-A3 comparison is rubric-heterogeneous ONLY on hedged sentences, which the A0
statements do not contain (measured 0/84).

## 3. Repair 2 — instrument exercises that hit the failure channel

**3a. Hedge-calibration items** (`calibration-hedge.jsonl`, 6 items, NOT scored, gate
12/12 across both judges — any miss aborts before real items). Draft set (expected
answers must survive the pre-freeze skeptic pass for uncontroversiality):

| id | item (Concept / Statement) | expected | exercises |
|---|---|---|---|
| cal:hedge-1 | "bird" / Every bird hatches from an egg. Normally a bird can fly. | yes | hedged-true despite exceptions (penguins) |
| cal:hedge-2 | "triangle" / Every triangle has exactly three sides. Normally a triangle has four corners. | no | hedged sentence misdescribes the usual case |
| cal:hedge-3 | "chair" / In every case of a chair, it is made to be sat on. Normally a chair has legs. | yes | exceptions-don't-falsify-the-hedge |
| cal:hedge-4 | "knife" / Every knife is made of metal. Normally a knife can cut. | no | unhedged head false, hedged tail true → no |
| cal:hedge-5 | "letter (written message)" / In every case of a letter, someone wrote it. Typically it is meant for someone to read. | yes | "Typically" variant, true |
| cal:hedge-6 | "gift" / In every case of a gift, someone gives it. Typically the one who receives it must pay the giver for it. | no | "Typically" variant, false |

The two v1 calibration items (triangle-yes / fish-furniture-no) are retained unchanged.

**3b. Hedge-flip probes** (`probes-hedgeflip-a2.jsonl`, `probes-hedgeflip-a3.jsonl`; 10
per hedged arm; A1 has no hedges so gets none). Construction: take a real arm item, keep
the unhedged head INTACT and TRUE, replace the hedged tail with a wrong-usual-case hedge
(same register as the existing deranged probes, e.g. "… Normally this is done by a place
far away."). Expected "no". This isolates exactly the v1 failure channel: a judge that
stops reading at the true unhedged head, or that treats hedges as unscoreable padding,
false-satisfies. Gate: hedge-flip false-satisfaction ≤ 0.30 per judge per hedged arm.
The v1 deranged-sort probe family (20/arm, expected "no", ≤ 0.30) is kept unchanged.

## 4. Repair 3 — the instrument PILOT (the steering-read process fix)

The steering read's diagnosis (§2.2): three of four recent runs died at instrument gates
that were never exercised at the operating point before freeze. v2 therefore stages the
spend: a cheap pilot that exercises the exact failing channel — judge-pair stability on
the v2 rubric over real soft-hedged A3 renderings — BEFORE the full re-run.

> **RE-REVISED 2026-07-12 (§11, κ-paradox redesign): the gate quantities below are
> SUPERSEDED — the gated pair statistic is now Gwet AC1 ≥ 0.65 (κ co-reported,
> never gated), the pilot hedge-flip block is 8 probes per judge, and cal:hedge-1
> is repaired. §11 is authoritative; this section is kept for the design record.**

**Pilot design (Stage P, runs after freeze, before any full-arm call —
REVISED 2026-07-12 per the cross-vendor FIX-THEN-FREEZE review, fix 1: the gated
quantity is the REAL pilot κ, not a raw-agreement surrogate, on a doubled sample):**
- Items: **40** real A3 items, stratified **R3=20, R4=16, R1=4** (proportional to
  42/34/8, and weighted to where v1 disagreement concentrated), selected
  deterministically by sorting ids on sha256(id + "|ontg2v2/pilot") within each rule
  stratum; the resulting id list — plus the 4 pilot hedge-flip probe ids, sha-sorted on
  sha256(id + "|ontg2v2/pilotflip") — is pinned in `pilot-manifest.json` at freeze.
- Calls per judge: 6 hedge-calibration + 40 real A3 (fresh order seed
  `ontg2v2/pilot|judge-<pk>|a3|2026-07-12`) + 4 hedge-flip probes = 50; **100 calls
  total, ≈ $1.0–1.3** at the measured v1 per-call cost band.
- **Pilot gate (all must hold, else STOP — the full run is never launched):**
  1. hedge-calibration 12/12 (6/6 per judge);
  2. **pilot κ_A3 ≥ 0.40** on the 40 real items — Cohen κ over the both-decisive
     yes/no pair table, the SAME κ function as the full-run arm gate (§6), with the
     full agreement table (both-yes / both-no / discordant cells) co-reported;
     the table is reporting, never a gate substitute;
  3. decisive ≥ 36/40 per judge (0.90, the full-run bar);
  4. hedge-flip false-satisfaction ≤ 1/4 per judge.
- n=40 makes the κ point estimate honestly gateable (the review's objection to κ at
  n=20 no longer applies at half the full-arm sample with the marginals pinned by the
  same judges); κ degenerate-table convention identical to §6 (p_e = 1 is reachable
  only with p_o = 1 → κ := 1).
- **Operating characteristics (pinned Monte Carlo, 200 000 reps, seed 20260712,
  per-item iid model at the v1 pA marginal 58/84; pinned in `pilot-manifest.json`):**
  P(κ₄₀ ≥ 0.40) = **0.29** if the true agreement rate is the v1-broken 0.679; 0.54 at
  the κ=0.40 boundary rate 0.729; 0.87 at 0.80; **0.97 at 0.85; ~1.00 at 0.90**. The
  pilot catches a still-broken instrument ~71% of the time for ~$1.3, at a priced ~3%
  false-stop risk if the repair is merely good (0.85) — versus the withdrawn
  raw-agreement surrogate's 82%/17%: the κ gate trades some broken-catch probability
  for a 5× lower false-stop rate, gates the registered quantity itself, and sits at
  ~0.5 pass probability exactly at the κ = 0.40 boundary, as a point-estimate gate
  should. A false stop costs the pilot spend only and reads INSTRUMENT-INVALID
  (pilot), never FAIL/PASS.
- Pilot labels are instrument evidence ONLY: discarded from all scoring; the full run
  re-adjudicates all 84 items with fresh calls and fresh order seeds (stateless judges,
  no session persistence — the v1 statelessness stipulation carries over; re-exposure of
  40 item texts to the same judge families is disclosed and stipulated negligible).
- If the pilot fails: STOP at ~$1.3, mechanical verdict INSTRUMENT-INVALID with the
  pilot channel named; rubric iteration happens under a NEW record (v3) — no
  post-freeze rubric edits, ever (pin discipline).

## 5. New endpoint — A1-vs-A3 separation (the breadth control gets teeth)

v1's honest embarrassment (interpretation §2): the BFO-only breadth control A1 scored
55/84, within noise of A3's 57/84 — so at n=84 the bulk of the lift over A0 is
attributable to SOFT routing + broad anchoring, not to source-specific SUMO/FrameNet
content. In v1 this was reported-only; in v2 it becomes verdict-bearing, else the
breadth caveat eats any PASS.

**Separation gates (point-estimate engineering gates, judge-pA construction,
vacuity-zeroed, same denominator conventions; NOT statistical-superiority claims):**

```text
sep_A3 :=  (a3_yes >= a1_yes)  AND  (a3_r3_yes >= a1_r3_yes + 5)
sep_A2 :=  (a2_yes >= a1_yes)  AND  (a2_r3_yes >= a1_r3_yes + 5)
```

- The R3 slice (domain/range, 42 slots) is where source-specific content lives by
  construction (A1 R3 non-vacuous 26/42 vs A2/A3 42/42; v1 measured a3_r3_yes − a1_r3_yes
  = 27 − 17 = +10). The +5 margin (≈ +0.119 on the slice) is half the v1-measured edge:
  a real content contribution should clear it; pair noise alone should not reliably do so.
- The overall term is non-inferiority (equality allowed): the content arms must not buy
  their R3 edge by regressing overall.
- Paired exact McNemar A3-vs-A1 (overall and R3 slice) is co-reported, never
  verdict-bearing (house style, plan §7.5 discipline).
- **Verdict wiring:** PASS now requires primary + separation:
  `go_combined := primary_pass AND sep_A3`; fallback
  `go_bfo_sumo_only := a2_pass AND sep_A2 AND NOT go_combined`. If A3 (or A2) clears
  34/84 but its separation gate fails, the verdict is **FAIL read as
  NO-GO-BREADTH-CONFOUND**: the measured lift is not attributable to the imported
  source-specific content at this n, and the source-specific shard is not licensed.
  (Scope note: NO-GO-BREADTH-CONFOUND does not kill soft routing as a direction, and it
  does NOT make A1 adoptable — A1 remains the breadth control, can never authorize
  adoption, and independently flunks the R3 informativeness guard by construction,
  26/42 < 34.)
- H-SEP is added as an explicit hypothesis with equal prominence for its deflationary
  outcome.

## 6. A realistic κ target — the arithmetic, pinned

> **RE-REVISED 2026-07-12 (§11, κ-paradox redesign): the κ ≥ 0.40 full-run gate
> below is SUPERSEDED by Gwet AC1 ≥ 0.65 per arm (κ co-reported, never gated) —
> the exploratory pilot measured κ = −0.021 at 70% raw agreement because the v2
> rubric shifts the operating prevalence to π ≈ 0.83, where κ collapses for
> accurate judges with independent errors. §11 is authoritative; the
> stringency-continuity arithmetic below (κ 0.40 ⇔ p_o 0.7299 ⇔ AC1 0.51 at the
> v1 A3 marginals) is one input to the new threshold's justification.**

The full-run stability gate **stays κ ≥ 0.40 per arm** — unchanged from v1/g2 for
cross-record comparability, and now sized against measured reality instead of hope:

- At the v1 A3 marginals (pA-yes 58/84, pB-yes 53/84), chance agreement p_e = 0.5499, so
  κ ≥ 0.40 ⇔ raw agreement ≥ 0.7299 ⇔ **≥ 62/84 agreements (≤ 22 disagreements)**. v1
  measured 27 disagreements; the rubric repair must convert **≥ 5 of the 27** — of which
  24 sit on "Typically"-bearing composites, the exact channel §2–§3 instrument. This is
  a modest, mechanism-targeted ask, not a 2× improvement demand.
- The pilot (§4) checks the same channel — the same κ quantity, at n=40 — at the
  operating point for ~$1.3 before the ~$5 full spend commits.
- Raw agreement and the full agreement table are added to mandatory reporting per arm,
  so the κ number can never again float free of its base rates.
- Decisiveness bar: **0.90 per judge per arm** (unchanged, RT-4-decidable rationale from
  the v1 record); the v1 record's kill-criterion text discrepancy ("decisive < 95%" vs
  the 0.90 endpoint — flagged moot in the interpretation) is FIXED in v2: 0.90 appears
  verbatim everywhere.

## 7. What does NOT change (estimand identity, pinned)

| invariant | v2 status |
|---|---|
| Estimand | blind ordinary-meaning soundness, per-slot, vacuity-zeroed, fixed denominator 84 |
| Slots / items | the SAME 84 kernel-v0 slots; `poc/g2/materials/items.jsonl` derivation untouched |
| Arm renderings | byte-identical: all four v1 `arm-*.jsonl` + `generation-report.json` + `soft-type-candidates.jsonl` re-pinned at their v1 sha256 values; **no regeneration** (regeneration would be a new experiment, not a repair) |
| A0 baseline | frozen constant 33/84 (pA labels sha 93a12447…), no new calls; estimation-only caveat inherited and restated |
| Primary gate | `sound_A3 ≥ 34/84`, judge-pA construction (plan §7.5 verbatim) |
| Informativeness guard | ≥67/84 A3 non-vacuous, ≥34/42 R3, zero hard operational rules (plan §7.6) |
| Judges | pA GPT-5.6-Sol (codex CLI family), pB claude-haiku-4-5 (headless claude CLI) — pinned invocation families as v1 |
| Rider | PROVISIONAL-ON-LLM-PROXY etc., verbatim on every verdict sentence |
| Envelope | v1 `extrapolation_envelope_verbatim` inherited in full (never W1/G4, no host model, no feasibility conclusion, human panel sole adoption authority, proxy-GO-then-human-FAIL governed by human result) |
| Deranged probes | 20/arm, ≤0.30 false-sat per judge per arm |
| Blinding | arm identity/sources/vacuity flags hidden; any blinding hit aborts pre-assembly |

Changed, exhaustively: prompt template (§2), +6 hedge-calibration items (§3a), +20
hedge-flip probes (§3b), +pilot stage and gate (§4), +separation endpoint and
NO-GO-BREADTH-CONFOUND mapping (§5), raw-agreement reporting + decisive-text fix (§6),
fresh order seeds (`ontg2v2/1|judge-<pk>|<arm>|<phase>|<date>`), new harness
`run-ontg2v2.py` + analysis `analysis/ontg2v2.py` (ports of the audited v1 machinery;
v1 files stay byte-identical).

## 8. Cost and call arithmetic (≤ $10 hard stop) — REVISED per §11.4 (pilot flips 4 → 8)

| block | calls |
|---|---|
| Stage P pilot: (6 cal + 40 real A3 + 8 hedge-flip) × 2 judges | 108 |
| Full preflight calibration: (2 v1-cal + 6 hedge-cal) × 2 | 16 |
| A1: (84 real + 20 deranged) × 2 | 208 |
| A2: (84 + 20 + 10 hedge-flip) × 2 | 228 |
| A3: (84 + 20 + 10 hedge-flip) × 2 | 228 |
| **n_calls_max** | **788** |

v1 landed 624 calls inside its $1–5 target band; 788 calls ≈ 1.26× → expected
**$1.4–6.3 cash**, hard stop **$10** (`budget.usd_cap`), wall-clock ~2.5–7.5 h at
measured v1 latency, CPU-only build on this box, concurrency 1.

**Live dollar/call abort (review fix 5 — the parent ledger records calls, not
cross-provider cash, so the harness enforces a PINNED CONSERVATIVE PRICE BOUND rather
than trusting an estimate):** `run-ontg2v2.py` pins
`PRICE_BOUND_USD_PER_CALL = 0.012` — 1.5× the v1-measured worst case (≤ $5 / 624
calls ≈ $0.008/call) — and before EVERY block aborts unless both (i) total recorded
calls ≤ 788 and (ii) bound-implied dollars = calls × $0.012 ≤ $10. Since
788 × $0.012 = $9.456 ≤ $10, the bound-implied worst case can never cross the registry
cap. Budget kill: hitting either ceiling before complete labels stops WITHOUT partial
scoring (pilot-stage stop is the one designed early exit and is a verdict, not a
partial score).

## 9. Coordinator freeze + run steps (ORDER, enforced — none executed in this session)

1. **Coordinator:** review this design + the DRAFT record; register PROPOSED-ASM-1550..1569
   (§10) into `registry/assumptions.jsonl` (append-only; coordinator action, not done here).
2. **experiment-designer role (build pass):** create `poc/ontology-import-g2-v2/` —
   `prompt-template-v2.txt`, `calibration-hedge.jsonl`, `probes-hedgeflip-a2.jsonl`,
   `probes-hedgeflip-a3.jsonl`, `pilot-manifest.json` (pinned pilot id list, §4),
   `run-ontg2v2.py`, `analysis/ontg2v2.py`, `materials/manifest.json` (fresh order
   seeds). Arm/generation files consumed BY v1 HASH from `poc/ontology-import-g2/materials/`
   — byte-identical, never regenerated.
3. **Mock pass:** `run-ontg2v2.py mock <dir> go | nogo | instrument | pilotfail | breadth`
   — all FIVE mock verdict paths GREEN before freeze (v1 had three; `pilotfail` and
   `breadth`/NO-GO-BREADTH-CONFOUND are new).
4. **Pre-freeze skeptic attack**, including at minimum: (a) adversarial pass on the 6
   hedge-calibration expected answers (uncontroversial or replaced); (b) mechanical
   check: zero hedge markers in `poc/g2/materials/items.jsonl` and `arm-a1-bfo.jsonl`
   (the §2 rubric-no-op claim); (c) sep-gate arithmetic reproduced independently;
   (d) blinding scan of the new template and probe files (no arm identity, no source
   names); (e) the v1 ASM-1366-style bridge-not-tuned check carries over unchanged
   (materials unchanged).
5. **Freeze:** fill every TO-PIN-AT-FREEZE hash in `registry/experiments/g2-import-v2.json`;
   `tools/registry/reuse-check.py check --record registry/experiments/g2-import-v2.json
   --gate` recorded pre-spend; `tools/registry/prereg-freeze.py` mints frozen_sha256.
6. **Ops amendment:** record both judge CLI version banners into `pins.harness_manifest`
   before any final-phase call.
7. **experiment-runner role:** preflight pA+pB → **Stage P pilot** (gate §4; any failure
   = STOP, assemble pilot-only result, verdict INSTRUMENT-INVALID-pilot) → per judge ×
   arm real + probe blocks (any cap pattern = STOP no retry; any blinding hit = ABORT)
   → assemble.
8. **analyst role:** mechanical verdict-gen + report (full metric vector §7.8 + raw
   agreement tables + pilot block + separation block, coverage disclosure, kill
   criterion verbatim, envelope verbatim).
9. **Cross-vendor Codex audit.** Designer never runs/grades; runner never
   designs/concludes; the identity that authored the bridge table never judges.

## 10. PROPOSED-ASM — coordinator to register (NOT written to assumptions.jsonl here)

```json
{"id":"PROPOSED-ASM-1550","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 estimand identity: v2 is an INSTRUMENT repair + re-mint of g2-import, not a new experiment on new content — same estimand (per-slot blind ordinary-meaning soundness, vacuity-zeroed, fixed denominator 84), same 84 kernel-v0 slots, byte-identical arm renderings re-pinned at the v1 sha256 values (no regeneration), same frozen A0 constant 33/84 (estimation-only caveat inherited), same primary gate sound_A3 >= 34/84 on the judge-pA construction, same judges (pA GPT-5.6-Sol codex-CLI family primary stand-in; pB claude-haiku-4-5 sensitivity, vendor overlap disclosed, never sole gold), same PROVISIONAL-ON-LLM-PROXY rider and extrapolation envelope verbatim. Changed exhaustively: adjudication rubric modality semantics, hedge-calibration items, hedge-flip probes, a staged instrument pilot, the A1-vs-A3/A2 separation endpoints with NO-GO-BREADTH-CONFOUND mapping, raw-agreement reporting, fresh order seeds, new pinned harness/analysis ports. v1 labels (sha ed0c000e...) are quarantined INSTRUMENT-INVALID evidence: never merged, never row-compared except as instrument before/after."}
{"id":"PROPOSED-ASM-1551","class":"MEASURED","load_bearing":true,"text":"g2-import v1 kappa-collapse localization (from the per-judge response files and arm materials): A3 pair disagreement 27/84 (pA-yes/pB-no 16, pA-no/pB-yes 11), concentrated R3 15/42 and R4 9/34; hedge-marker census A1 0/84, A2 83/84 'Normally' only, A3 83/84 'Normally' + 63/84 'Typically' (FrameNet valency tails); 24/27 A3 disagreements carry a 'Typically' clause (base rate 63/84); kappa tracks the hedge-stacking gradient 0.527 -> 0.430 -> 0.286 while the unhedged baseline and A1 stayed stable under the identical rubric. The v1 judge question ('true in ALL normal cases?') is undefined over hedged sentences; this is the designated repair target."}
{"id":"PROPOSED-ASM-1552","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 rubric repair semantics: each sentence of a rendered statement is scored at its own stated force — unhedged sentences ('Every/In every case/Whenever') require the ordinary-meaning guarantee in ALL normal cases (unchanged standard); 'Normally'/'Typically' sentences assert the usual/characteristic case and are true despite exceptions, false if they misdescribe even the usual case; 'yes' iff every sentence is true at its stated force. For fully-unhedged statements this is extensionally identical to the v1 standard, and the A0 baseline items and A1 arm contain zero hedge markers (measured 0/84 each; re-checked mechanically at freeze) — so the frozen 33/84 baseline constant and the breadth control are read under an unchanged standard and the estimand is preserved. The rubric text is identical across arms and judges (no arm-identity leak)."}
{"id":"PROPOSED-ASM-1553","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 instrument exercises: (i) 6 hedge-calibration items (unscored) gating 12/12 across both judges before any real item, covering hedged-true-despite-exceptions, hedged-false-at-usual-case, unhedged-false-with-hedged-true, and both hedge markers; (ii) 10 hedge-flip probes per hedged arm (A2, A3; A1 has no hedges) — true unhedged head + deranged hedged tail, expected 'no', false-satisfaction <= 0.30 per judge per hedged arm — isolating the exact v1 failure channel; (iii) the v1 deranged-sort probe family kept unchanged (20/arm, <= 0.30). Any calibration miss aborts before real spend."}
{"id":"PROPOSED-ASM-1554","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 pilot stage (the steering-read process fix — exercise the gate channel at the operating point BEFORE the full spend; REVISED per the 2026-07-12 cross-vendor FIX-THEN-FREEZE review fix 1: the gated quantity is the REAL pilot kappa, not a raw-agreement surrogate): Stage P adjudicates 40 real A3 items (stratified R3=20/R4=16/R1=4, deterministic sha-sorted selection pinned in pilot-manifest.json) + 6 hedge-calibration + 4 hedge-flip probes per judge, 100 calls ~ $1.0-1.3. Gate: calibration 12/12 AND pilot kappa_A3 >= 0.40 (Cohen kappa over the both-decisive pair table of the 40 items, SAME kappa function as the full-run arm gate, full agreement table co-reported — reporting, never a gate substitute) AND decisive >= 36/40 per judge AND hedge-flip false-sat <= 1/4 per judge; any failure = STOP, full run never launched, mechanical verdict INSTRUMENT-INVALID (pilot channel named). Operating characteristics (pinned Monte Carlo, 2e5 reps, seed 20260712, per-item iid model at the v1 pA marginal 58/84; pinned in pilot-manifest.json): P(kappa40 >= 0.40) = 0.29 at the v1-broken 0.679 agreement rate, 0.54 at the kappa-0.40 boundary 0.729, 0.87 at 0.80, 0.97 at 0.85, ~1.00 at 0.90 — catches a still-broken instrument ~71% for ~$1.3 at a priced ~3% false-stop on a merely-good (0.85) repair, and sits at ~0.5 pass probability exactly at the gate boundary as a point-estimate gate should. Pilot labels are instrument evidence only, discarded from scoring; the full run re-adjudicates all 84 items with fresh stateless calls and fresh order seeds; re-exposure of 40 item texts to the same stateless judge families is disclosed and stipulated negligible."}
{"id":"PROPOSED-ASM-1555","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 realistic kappa target: the full-run stability gate stays kappa >= 0.40 per arm (comparability with g2/g2-import). Sizing against measured v1 reality: at the v1 A3 marginals (pA-yes 58/84, pB-yes 53/84) chance agreement is 0.5499, so kappa >= 0.40 iff raw agreement >= 62/84 (<= 22 disagreements) — the rubric repair must convert >= 5 of the 27 v1 disagreements, 24 of which sit on the 'Typically' composites the repair directly instruments. Raw agreement tables are added to mandatory per-arm reporting. Decisiveness bar 0.90 per judge per arm (RT-4-decidable rationale unchanged); the v1 kill-text '95%' discrepancy is fixed to 0.90 verbatim everywhere in v2."}
{"id":"PROPOSED-ASM-1556","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 separation endpoint (the breadth control gets teeth): sep_A3 := (a3_yes >= a1_yes) AND (a3_r3_yes >= a1_r3_yes + 5); sep_A2 analogous; point-estimate engineering gates on the judge-pA construction, never statistical superiority; paired McNemar A3-vs-A1 (overall and R3) co-reported, never verdict-bearing. PASS now requires primary AND separation (go_combined := primary_pass AND sep_A3; fallback go_bfo_sumo_only := a2_pass AND sep_A2 AND NOT go_combined). A 34/84-clearing arm whose separation gate fails reads FAIL as NO-GO-BREADTH-CONFOUND: the lift is attributable to soft routing + broad categorial anchoring, and the source-specific import shard is not licensed. NO-GO-BREADTH-CONFOUND does not kill soft routing as a direction and does not make A1 adoptable (breadth control, can never authorize; independently flunks the R3 informativeness guard 26/42 < 34 by construction). Margin rationale: R3 (42 domain/range slots) is where source-specific content lives (A1 R3 non-vacuous 26/42 vs 42/42); v1 measured +10 there; +5 is half the measured edge and ~+0.119 on the slice."}
{"id":"PROPOSED-ASM-1557","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 hypothesis set: H-SOFT, H-SRC, H-BREADTH-NULL, H-INSTRUMENT carry over from g2-import with the same riders; added H-SEP (equal prominence for its deflationary reading): the imported source-specific SUMO/FrameNet content contributes measurable soundness beyond soft routing + broad BFO anchoring, read from sep_A3/sep_A2; its deflationary outcome NO-GO-BREADTH-CONFOUND is a first-class result, not a caveat. H-INSTRUMENT is restated as: the directive-#11 proxy pair is stable on soft-hedged modality UNDER THE v2 SENTENCE-FORCE RUBRIC — kappa >= 0.40 per arm, decisive >= 0.90, deranged and hedge-flip probe false-sat <= 0.30, pilot gate passed; failure at either stage => INSTRUMENT-INVALID, never FAIL/PASS."}
{"id":"PROPOSED-ASM-1558","class":"EXTRAPOLATION","load_bearing":false,"resolution_path":"the run ledger replaces these estimates; budget kill at 780 calls, at the $10 hard stop, or at the live price-bound abort stops without partial scoring","text":"g2-import-v2 cost band: <= 780 stateless proxy calls (pilot 100 + calibration 16 + A1 208 + A2 228 + A3 228), CPU-only build, expected cash $1.3-6.3 (1.25x the v1 624-call spend, which landed in its $1-5 band), hard stop $10, wall-clock ~2.5-7.5 h at measured v1 per-call latency, concurrency 1 on this box. The dollar figure is NOT trusted as an estimate: the harness enforces the ASM-1564 pinned conservative price bound live."}
{"id":"PROPOSED-ASM-1559","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 inherits verbatim: the g2-import extrapolation envelope (G2-class diagnostic over the same 84 self-authored slots; never W1, never G4, no host model, no competitiveness sentence; proxy gold with the two-human panel as sole adoption authority; proxy-GO-then-human-FAIL governed by the human result; PASS licenses only bounded promotion of the winning non-binding soft-preference shard; no feasibility conclusion in any direction), the PROVISIONAL-ON-LLM-PROXY rider on every verdict sentence, the informativeness guard (>= 67/84 A3 non-vacuous, >= 34/42 R3, zero hard operational rules), the soft-only routing invariants (binding:false, rank-only, five forbidden_effects, validator fail-closed), and the source-closure stipulations. Nothing in v2 weakens any v1 constraint."}
{"id":"PROPOSED-ASM-1560","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 fresh-runs/reuse discipline: A0 remains a pinned constant of the frozen g2 readout (no new calls); no logged proxy row of g2, g2-import v1, or the v2 pilot is consumed as a scored v2 output (pilot rows are instrument evidence only); tools/registry/reuse-check.py runs pre-spend with the v2 record as the recorded decision; v1 harness and materials files stay byte-identical (new files only: prompt-template-v2, hedge calibration/probes, pilot manifest, run-ontg2v2.py, analysis/ontg2v2.py); regenerating any pinned v1 material is a pin break and voids the run."}
{"id":"PROPOSED-ASM-1561","class":"EXTRAPOLATION","load_bearing":false,"resolution_path":"the Stage P pilot decides this for ~$1.3 before the full spend; a pilot fail stops the record and sends the rubric to a v3 under a new frozen record (no post-freeze rubric edits)","text":"g2-import-v2 repair expectation (directional, load-bearing for nothing): the sentence-force rubric plus hedge calibration should lift A3 raw pair agreement from the v1 0.679 toward the 0.80-0.90 band, clearing kappa 0.40, because the disagreement is concentrated exactly on the modality ambiguity the rubric removes (24/27 on 'Typically' composites) rather than on genuine content difficulty; if instead the instability reflects irreducible judge disagreement about soft-hedged ordinary-meaning content, the pilot fails cheaply and that is itself an informative instrument result for the whole soft-rendering programme line."}
{"id":"PROPOSED-ASM-1562","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 verdict-name mapping (pinned): PASS == GO-BFO-SUMO-FRAMENET (go_combined) or GO-BFO-SUMO + NO-GO-FRAMENET-pending-redesign (go_bfo_sumo_only); FAIL == NO-GO-VACUOUS (informative_valid false) or NO-GO-BREADTH-CONFOUND ((primary_pass or a2_pass) true but the corresponding separation gate false; /analysis/breadth_confound) or NO-GO-ONTOLOGY-IMPORT (neither A2 nor A3 reaches 34/84; /analysis/no_go); INSTRUMENT-INVALID == pilot-stage failure (named channel, ~$1.3 spend, full run never launched) or full-run instrument failure — no conclusion, repair and mint a new record. A1 passing anything alone changes NOTHING. Deflationary outcomes get equal prominence. Every verdict sentence names its licensing arm and carries the rider verbatim: PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots; point-estimate engineering gate, not statistical superiority; soft non-binding typing only — never hard laws; no feasibility conclusion."}
{"id":"PROPOSED-ASM-1563","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 pilot kappa operating-characteristics model (pinned): per-item iid, pA ~ Bernoulli(58/84) (the v1 A3 pA-yes marginal), pB equals pA with probability a and is flipped otherwise; kappa computed over the resulting n=40 table; Monte Carlo 200000 reps, seed 20260712 (python random.Random), computed at design time and pinned in pilot-manifest.json. The model treats all 40 items as decisive (cannot-say shrinks the table and is separately gated at decisive >= 36/40); its numbers size the tripwire only and license nothing about any hypothesis. Degenerate-table convention pinned: the kappa function is byte-identical to the full-run arm kappa (analysis/ontg2v2.py); p_e = 1 is reachable only with p_o = 1, in which case kappa := 1.0."}
{"id":"PROPOSED-ASM-1564","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 budget enforcement (review fix 5 — the parent ledger records 624 calls, not total cross-provider cash, so no dollar ESTIMATE is trusted): run-ontg2v2.py pins PRICE_BOUND_USD_PER_CALL = 0.012 (1.5x the v1-measured worst case <= $5/624 ~ $0.008/call) and enforces a LIVE dollar/call abort before every block: total recorded calls <= 780 AND bound-implied dollars (calls x 0.012) <= the $10 usd_cap; 780 x 0.012 = $9.36, so the bound-implied worst case can never cross the registry cap. Hitting either ceiling before complete labels stops WITHOUT partial scoring; the run ledger records actual calls and the bound-implied dollars alongside."}
{"id":"PROPOSED-ASM-1565","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 verdict-rule exhaustiveness repair (review fix 3): the draft's unreachable double catch-all (FAIL const:true shadowing INCONCLUSIVE const:true) is deleted. Exactly ONE terminal catch-all remains. Because P2 freeze constraint 3 (tools/registry/prereg-freeze.py) hard-mandates {INCONCLUSIVE, const:true} as the LAST rule, the retained catch-all is INCONCLUSIVE and the FAIL default is a fully NAMED rule: FAIL when (/analysis/no_go OR /analysis/breadth_confound). Given the pinned analysis definitions (no_go := not(primary_pass or a2_pass); breadth_confound := (primary_pass or a2_pass) and not(go_combined or go_bfo_sumo_only)), rules 0-3 are provably exhaustive over every consistent analysis document; the INCONCLUSIVE catch-all is reachable only on an inconsistent document — a fail-closed guard, never dead code behind another catch-all. Semantics are identical to the reviewer's FAIL-catch-all reading on every consistent output."}
{"id":"PROPOSED-ASM-1566","class":"MEASURED","load_bearing":true,"text":"g2-import-v2 registry-record schema repair (review fix 2), verified by prereg-freeze --dry-run 2026-07-12: scale_language_max:'none' moved into /design (kot-reg/2 declares it there; the envelope licenses nothing, coherent with 'none'), prereg_doc moved from /pins to the record root (root-required by kot-reg/2; pins.additionalProperties=false), and the forbidden /draft_note removed (the DRAFT provenance lives in this design doc and the stage discipline, not inside the hashed record bytes)."}
{"id":"PROPOSED-ASM-1567","class":"MEASURED","load_bearing":true,"text":"g2-import-v2 build pass complete (design section 9 steps 2-3), 2026-07-12: poc/ontology-import-g2-v2/ authored deterministically by build-v2-materials.py (no RNG, no clock; selections and orders sha256-derived) — prompt-template-v2.txt, calibration-hedge.jsonl (6), probes-hedgeflip-a2.jsonl (10), probes-hedgeflip-a3.jsonl (10, wrong-usual-case hedged tails on intact true heads, deranged-probe register, zero blinding tokens), pilot-manifest.json (40 stratified ids + 4 pilot flip ids + gate + OC), materials/manifest.json (fresh v2 order seeds), run-ontg2v2.py, analysis/ontg2v2.py (selftest green); ALL FIVE mock verdict paths ran GREEN against the repaired DRAFT record: go->PASS, nogo->FAIL, instrument->INSTRUMENT-INVALID, pilotfail->INSTRUMENT-INVALID (pilot_valid=false, pilot-only assembly, kappa channel named), breadth->FAIL (breadth_confound=true); every pin in the record and the harness is a real sha256 over the committed bytes."}
{"id":"PROPOSED-ASM-1568","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 pilot-stop semantics, mechanical: run-ontg2v2.py refuses every real/probe/hedgeflip/assemble invocation unless pilot-status.json exists with pass=true (written only by the pilotgate mode from the six pilot response files); a failed gate immediately assembles the pilot-only result via the pinned analysis (pilot_only mode, accepted ONLY with a failing pilot gate — a passing pilot with missing full-run metrics is refused as an incomplete run), whose document drives verdict rule 0 to INSTRUMENT-INVALID. The pilot block enters the analysis solely through /gates/pilot_valid and the pilot_* reporting fields; no pilot label is ever scored."}
{"id":"PROPOSED-ASM-1569","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 harness port faithfulness: run-ontg2v2.py is a fork of the audited poc/ontology-import-g2/run-ontg2.py with byte-identical judge invocation forms (codex exec / headless claude flags verbatim), identical validity/retry/no-label/cap-stop/blinding/checkpoint contracts, and identical assemble counting (vacuity-zeroing upstream, kappa on raw labels); the v2 deltas are exactly: the v2 sentence-force template, the 6+2 preflight calibration, the Stage-P pilot block, the hedgeflip phase, the A3-vs-A1 McNemar cells, the pilot block metrics, and the ASM-1564 budget abort. All v1 inputs are consumed byte-identical at their v1-frozen sha256 pins; the v1 harness and its response files are untouched."}
```

---

## 11. κ-PARADOX DIAGNOSIS + INSTRUMENT-GATE REDESIGN (v2.1, 2026-07-12 — Fable, statistical-methodology pass)

**Trigger:** the sanctioned Stage-P pilot ABORTED at preflight-pB (hedge-calibration
11/12, cal:hedge-1, §11.5); a coordinator-directed EXPLORATORY diagnostic run
(`runs/pilot-20260712-EXPLORATORY-kappa/`, quarantined, instrument evidence only)
then measured κ_A3 = **−0.021** on the 40 pilot items DESPITE raw agreement
28/40 = 0.70 (table both-yes 27 / both-no 1 / pA-yes-pB-no 8 / pA-no-pB-yes 4).
This section diagnoses that result, re-reads the v1 evidence under
prevalence-robust metrics, and REDESIGNS the §4/§6 instrument gates. It changes
no frozen record and no verdict; the record is still DRAFT.

### 11.1 Diagnosis — the paradox is real, but it does NOT exonerate the instrument (all MEASURED)

| table (n) | raw p_o | marginals pA/pB yes | κ | PABAK | **AC1** | p_pos | p_neg | independence-ceiling AC1 |
|---|---|---|---|---|---|---|---|---|
| v2 EXPLORATORY pilot (40) | 0.700 | 0.875 / 0.775 | **−0.021** | 0.400 | **0.578** | 0.818 | **0.143** | **0.587** |
| v1 A3 restricted to the same 40 ids | 0.750 | 0.575 / 0.675 | 0.472 | 0.500 | 0.529 | 0.800 | 0.667 | 0.108 |
| v1 A3 (84) | 0.679 | 0.690 / 0.631 | 0.286 | 0.357 | 0.417 | 0.757 | 0.526 | 0.184 |
| v1 A2 (84) | 0.738 | 0.643 / 0.643 | 0.430 | 0.476 | 0.516 | 0.796 | 0.633 | 0.151 |
| v1 A1 (84) | 0.833 | 0.810 / 0.738 | 0.527 | 0.667 | 0.744 | 0.892 | 0.632 | 0.457 |

- **κ-paradox confirmed at the pilot operating point** (Feinstein–Cicchetti 1990;
  Gwet 2008): at marginals 0.875/0.775, Cohen p_e = 0.706 ≥ p_o = 0.700 → κ ≈ 0
  at 70% raw agreement; the maximum attainable κ at those marginals is 0.66, and a
  marginal-matched pair of ACCURATE judges with INDEPENDENT errors passes κ ≥ 0.40
  only 0.7% of the time at n=40 while a genuinely good pair (true agreement 0.85)
  passes only 70% — a 30% false-stop on a good repair. κ punishes the v2 rubric
  for doing its job (hedges become satisfiable → both judges shift yes-ward →
  prevalence π rises 0.66 → 0.83). **κ is the wrong gate statistic here.**
- **But the paradox does not certify the instrument either.** The pilot pair's
  AC1 (0.578) sits BELOW its own marginal-matched independence ceiling (0.587) —
  conditional on marginals, the two judges share ≈ zero pairwise signal on these
  40 items, which is exactly what κ ≈ 0 says. Item-matched before/after: v1
  agreed 30/40 on these same ids; v2 agrees 28/40 — the rubric repaired 6 old
  discordances but minted 8 new ones, and concordant-no collapsed 10 → 1 (p_neg
  0.667 → 0.143). The v2 rubric moved the operating point more than it
  stabilized the pair. The residual disagreement is one-sided (8 pA-yes/pB-no vs
  4) — judge-pB retains residual hedge-strictness (consistent with its
  cal:hedge-1 behaviour, §11.5).
- **The v1 verdict survives the re-read.** On the original 84-item tables the
  arm gradient is metric-independent: raw 0.833→0.738→0.679, AC1
  0.744→0.516→0.417, PABAK 0.667→0.476→0.357 down the hedge-stacking ladder.
  g2-import's INSTRUMENT-INVALID was substantively right, not a κ artifact.

### 11.2 Does the g2-import 0.68-vs-0.39 signal survive a proper agreement metric? YES (bracket-robust), with the breadth caveat intact (MEASURED)

The soundness signal never depended on κ; the honest question is whether judge
instability could overturn it. It cannot, at this n:

- **Primary:** a3 ≥ 34/84 passes under EVERY label construction — judge-pA 57,
  judge-pB 53, and the maximally conservative pair-CONCORDANT bracket **42/84 =
  0.50** (i.e. even scoring all 27 discordant items "no", A3 beats the 33/84
  baseline gate).
- **R3 separation (where source-specific content lives):** a3−a1 = +10 (pA), +11
  (pB), **+6 (concordant)** — all ≥ the +5 margin.
- **Overall separation term:** a3 ≥ a1 holds on pA (57 v 55) and pB (53 v 51)
  but FAILS on the concordant bracket (42 v 47) — the v1 breadth caveat is real
  and stays first-class (that is exactly what the §5 sep-gate re-tests).
- These reads remain GO-SHAPED signals under an invalid instrument: they license
  nothing; they establish only that the signal is worth the re-mint. [rider
  verbatim: PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots;
  point-estimate engineering gate, not statistical superiority; soft non-binding
  typing only — never hard laws; no feasibility conclusion]

### 11.3 Redesigned gates (SUPERSEDES the κ≥0.40 gates of §4 and §6)

**Gated pair statistic: Gwet AC1 ≥ 0.65** — pilot (n=40, A3) AND full run (per
arm, n=84). κ is DEMOTED to a mandatory co-report (cross-record continuity with
g2/g2-import), never gated. Also mandatory co-reports wherever any AC1 is
gated: PABAK, p_pos/p_neg specific agreement, the raw 2×2 table, both
yes-marginals, and the marginal-matched independence-ceiling AC1.

Threshold justification (quadrangle, all derivable without the exploratory κ
number):
1. **Above the independence ceiling** at the measured v2 operating marginals
   (0.587): marginal-matched independent judges pass AC1 ≥ 0.55 64% and
   AC1 ≥ 0.60 46% of the time at n=40; AC1 ≥ 0.65 passes them 30%. A gate below
   the ceiling gates nothing.
2. **Tighter than the retired gate's own carried-over stringency:** κ ≥ 0.40 at
   the v1 A3 marginals ⇔ p_o ≥ 0.7299 ⇔ AC1 = 0.51 (§6's sizing, translated).
3. **Between measured-broken and measured-healthy:** v1 A3 0.417 (84) / 0.529
   (matched 40) vs unhedged A1 0.744.
4. **Item-matched meaning at the pilot marginals:** AC1 0.65 ⇔ raw ≥ 31/40 —
   strictly beating the item-matched v1 subset's 30/40. The repair must repair.

Operating characteristics (pinned in `pilot-manifest.json`; Monte Carlo 2×10⁵
reps, numpy default_rng(20260712), flip model; both m = 58/84 continuity and
m = 0.875 measured-operating rows): at m = 0.875, P(pass) = 0.116 at the
v1-broken 0.679 agreement rate, 0.404 at 0.75, 0.691 at 0.80, **0.911 at 0.85**,
0.992 at 0.90. The tripwire catches a still-broken instrument ~88% for ~$1.4 at
a ~9% false-stop on a merely-good (0.85) repair — versus the retired κ gate's
7%-pass-at-broken / **30% false-stop at 0.85** at the same operating point.

**Honesty pins (mandatory disclosures):** (a) the quarantined exploratory pilot
measured AC1 0.578 and **fails** this gate — the threshold was not shopped to
pass known data; (b) at π ≈ 0.83 ANY pair coefficient discriminates weakly (the
pairwise signal lives in rare no-items), so the prevalence-FREE known-answer
channels (§11.4) are load-bearing instrument evidence on an equal footing with
AC1; (c) every readout table reporting an AC1 must print the raw table and the
independence ceiling next to it; (d) the full-run readout re-computes primary
and separation under the pA, pB, and pair-concordant brackets and discloses any
flip with equal prominence (§11.2 shows none flips at v1 values except the
overall sep term, already gated).

### 11.4 Burden shift — the known-answer channels get real n

The pilot hedge-flip block is DOUBLED, 4 → 8 probes per judge (ids: the first 8
of the same pinned sha-sort; gate unchanged at ≤ 0.25, i.e. ≤ 2/8): at n=4 the
≤1/4 gate passes a coin-flipping judge 31% of the time; at n=8, 15%, while a
well-behaved judge (true false-sat 0.1) still passes 96%. Full-run probe
families unchanged (deranged 20/arm ≤ 0.30; hedge-flip 10/hedged-arm ≤ 0.30);
hedge-calibration 12/12 unchanged (repaired set, §11.5). Call arithmetic:
pilot (6 cal + 40 real + 8 flip) × 2 = **108**; total **788** ≤ the same $10
hard stop (788 × $0.012 = $9.456; §8 updated).

### 11.5 Calibration repair — the miss was the ITEM, not (only) the judge

The sanctioned pilot abort channel: judge-pB answered "no" on cal:hedge-1
(*"Every bird hatches from an egg. Normally a bird can fly."*, expected yes) —
and 4/4 fresh stateless repeats reproduced it (not flakiness). Audit verdict:
the unhedged HEAD is a **biological universal, not an ordinary-meaning
guarantee** — under the rubric's own standard ("the concept's ordinary meaning
guarantees it in ALL normal cases") a strict "no" is defensible; the item is
unsound as a calibration anchor. The other five items' heads are analytic
(triangle/sides, chair/sat-on, knife-head false BY DESIGN, letter/written,
gift/given) and judge behaviour on them was correct 10/10. **Repair:** head
replaced with the analytic *"Every bird is an animal."* (hedged tail and the
exercised channel — hedged-true-despite-exceptions, penguins — unchanged);
`calibration-hedge.jsonl` regenerated deterministically, re-pinned.

### 11.6 What changed on disk (all pre-freeze; record still DRAFT)

`analysis/ontg2v2.py` (AC1 gate + agreement panel + null-field set + selftest,
sha cc5806fe…), `run-ontg2v2.py` (pilotgate on AC1, κ co-reported;
N_PILOTFLIP 8; budget 788; pins; sha ce2ab5a6…), `build-v2-materials.py` +
regenerated `calibration-hedge.jsonl` (f8d4e03b…), `pilot-manifest.json`
(e4ac7c95…; new gate + OC blocks), `materials/manifest.json` (8b7ba712…;
8-probe pilotflip order). Arm/probe/template files byte-identical (template
6ba9a6f4… unchanged — the RUBRIC is not edited by this redesign; only the
instrument-validity statistics, the probe count, and one unsound calibration
item). All five mock verdict paths re-run GREEN; `prereg-freeze --dry-run`
clean. The exploratory pilot directory stays quarantined; the frozen record
must run a FRESH Stage-P pilot from scratch.

### 11.7 Honest expectation (EXTRAPOLATION, load-bearing for nothing)

If the fresh pilot's true agreement rate matches the exploratory measurement
(~0.70 at the new operating point), P(pilot pass) ≈ 0.12–0.15: the record most
likely stops at INSTRUMENT-INVALID (pilot) for ~$1.4. That is the tripwire
working, not a defect — but the cheaper path is to iterate the rubric FIRST
(v2.2/v3 under this same DRAFT record before freeze, or a new record after):
the residual failure channel is now precisely located (one-sided pB
hedge-strictness on real composite items; p_neg collapse). A targeted rubric
clarification for multi-hedge composites + the repaired calibration set is the
next design move; the redesigned gate stays as pre-registered here either way.

## 12. PROPOSED-ASM (κ-paradox redesign wave) — coordinator to register (NOT written to assumptions.jsonl here)

```json
{"id":"PROPOSED-ASM-1680","class":"MEASURED","load_bearing":true,"text":"g2-import-v2 kappa-paradox, exploratory pilot 2026-07-12 (quarantined run pilot-20260712-EXPLORATORY-kappa, instrument evidence only): 40 pinned A3 items, table both_yes 27 / both_no 1 / pA_yes_pB_no 8 / pA_no_pB_yes 4 -> raw agreement 0.700, marginals pA 35/40 = 0.875, pB 31/40 = 0.775, Cohen p_e = 0.7062 >= p_o -> kappa = -0.0213 at 70% agreement; max attainable kappa at these marginals 0.66; Gwet AC1 0.578, PABAK 0.400, p_pos 0.818, p_neg 0.143; marginal-matched independence-ceiling AC1 0.5873 EXCEEDS the measured AC1: conditional on marginals the pair shares ~zero signal on these items. The Feinstein-Cicchetti prevalence paradox is confirmed for kappa AND the instrument is not thereby exonerated."}
{"id":"PROPOSED-ASM-1681","class":"MEASURED","load_bearing":true,"text":"g2-import v1 prevalence-robust re-read (from labels-ontg2.jsonl, kappa values reproduced exactly): A1 raw 0.833 kappa 0.527 PABAK 0.667 AC1 0.744; A2 raw 0.738 kappa 0.430 PABAK 0.476 AC1 0.516; A3 raw 0.679 kappa 0.286 PABAK 0.357 AC1 0.417. The hedge-ladder instrument degradation is metric-independent; the v1 INSTRUMENT-INVALID verdict was substantively correct, not a kappa artifact. Cohen p_e at the v1 A3 marginals was only 0.55 (mild paradox); the paradox is acute only at the v2 operating point (p_e 0.71)."}
{"id":"PROPOSED-ASM-1682","class":"MEASURED","load_bearing":true,"text":"g2-import-v2 item-matched rubric before/after on the 40 pinned pilot ids: v1 agreed 30/40 (kappa 0.472, AC1 0.529, p_neg 0.667); the v2 exploratory pilot agreed 28/40 (AC1 0.578, p_neg 0.143). Transitions v1->v2: 6 of v1's 10 discordances repaired; 8 new discordances minted (3 from concordant-yes, 5 from concordant-no); concordant-no collapsed 10 -> 1; both judges shifted yes-ward (prevalence pi 0.625 -> 0.825). Residual disagreement is one-sided (8 pA-yes/pB-no vs 4): judge-pB retains hedge-strictness on real composites. The v2 rubric moved the operating point more than it stabilized the pair."}
{"id":"PROPOSED-ASM-1683","class":"MEASURED","load_bearing":true,"text":"g2-import signal bracket-robustness (v1 labels, reported as GO-SHAPED-under-invalid-instrument, licensing nothing): the primary a3 >= 34/84 holds under every label construction - judge-pA 57/84, judge-pB 53/84, pair-concordant 42/84 (even scoring all 27 discordant items 'no', A3 = 0.50 > baseline 0.393); the R3 separation edge a3-a1 holds under all brackets (+10 pA, +11 pB, +6 concordant, all >= +5); the OVERALL separation term a3 >= a1 fails on the concordant bracket only (42 vs 47) - the breadth confound stays live and is exactly what the verdict-bearing sep-gate re-tests. Rider verbatim: PROVISIONAL-ON-LLM-PROXY; same 84 self-authored kernel-v0 slots; point-estimate engineering gate, not statistical superiority; soft non-binding typing only - never hard laws; no feasibility conclusion."}
{"id":"PROPOSED-ASM-1684","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 instrument-gate redesign (design section 11.3, supersedes the kappa >= 0.40 gates in ASM-1554/1555 semantics): the gated pair statistic is Gwet AC1 >= 0.65 - Stage-P pilot (A3, n=40) and full run (per arm, n=84). Cohen kappa is DEMOTED to a mandatory co-report (cross-record continuity), never gated. Threshold justification quadrangle: (i) above the marginal-matched independence-ceiling AC1 at the measured v2 operating marginals (0.587; thresholds <= 0.60 are passable by independent judges >= 46% at n=40, 0.65 -> 30%); (ii) strictly tighter than the retired gate's carried-over stringency (kappa 0.40 at v1 A3 marginals <=> p_o 0.7299 <=> AC1 0.51); (iii) between measured-broken v1 A3 (0.417; matched-40 0.529) and measured-healthy unhedged A1 (0.744); (iv) at the pilot marginals AC1 0.65 <=> raw >= 31/40, strictly beating the item-matched v1 subset's 30/40. All other gate channels unchanged (cal 12/12, decisive >= 36/40 pilot / >= 0.90 full, probe families per ASM-1553)."}
{"id":"PROPOSED-ASM-1685","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 agreement-reporting convention (design section 11.3): wherever an AC1 is gated or reported, the readout MUST co-print Cohen kappa, PABAK, p_pos/p_neg specific agreement, the raw 2x2 table, both yes-marginals, and the marginal-matched independence-ceiling AC1; no agreement coefficient ever floats free of its base rates. The full-run readout additionally re-computes primary and separation under the judge-pA, judge-pB, and pair-concordant brackets and discloses any conclusion flip with equal prominence."}
{"id":"PROPOSED-ASM-1686","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 burden shift (design section 11.4): at prevalence pi ~ 0.83 ANY pair-agreement coefficient discriminates weakly (the pairwise signal lives in rare no-items), so the prevalence-FREE known-answer channels are load-bearing instrument evidence on an equal footing with AC1: hedge-calibration 12/12 (repaired set), pilot hedge-flip DOUBLED to 8 probes per judge at <= 0.25 (= 2/8; a coin-flipping judge passes 15% vs 31% at n=4; a 0.1-false-sat judge passes 96%), full-run deranged 20/arm and hedge-flip 10/hedged-arm at <= 0.30 per judge unchanged. Call arithmetic: pilot (6+40+8) x 2 = 108; total 788 calls; bound-implied worst case 788 x $0.012 = $9.456 <= the $10 hard stop."}
{"id":"PROPOSED-ASM-1687","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 pilot operating characteristics re-pin (design section 11.3/11.6, replaces the ASM-1563 kappa OC): per-item iid flip model, Monte Carlo 200000 reps, numpy default_rng(20260712) multinomial, pinned in pilot-manifest.json at BOTH m = 58/84 (v1 continuity) and m = 0.875 (measured exploratory v2 operating marginal, provenance disclosed). At m = 0.875: P(AC1_40 >= 0.65) = 0.116 at the v1-broken 0.679 true-agreement rate, 0.404 at 0.75, 0.691 at 0.80, 0.911 at 0.85, 0.992 at 0.90; marginal-matched independent-judge false-pass 0.300 (vs 0.638 at a 0.55 threshold). Comparison pinned for the retired gate at the same operating point: kappa >= 0.40 passes independent judges 0.007 but a genuinely-good 0.85 pair only 0.700 - a 30% false-stop; the kappa gate punishes the rubric for raising prevalence. These numbers size the tripwire only and license nothing."}
{"id":"PROPOSED-ASM-1688","class":"MEASURED","load_bearing":true,"text":"g2-import-v2 calibration repair (design section 11.5): the sanctioned Stage-P pilot aborted at preflight-pB on cal:hedge-1 ('Every bird hatches from an egg. Normally a bird can fly.', expected yes, pB answered no; 4/4 fresh stateless repeats reproduce it - systematic, not flaky). Audit: the unhedged head is a biological universal, not an ordinary-meaning guarantee; under the rubric's own 'ordinary meaning guarantees it' standard a strict no is defensible; the ITEM was unsound as a calibration anchor. The remaining five items' heads are analytic and were answered correctly 10/10. Repair: head replaced with the analytic 'Every bird is an animal.' (hedged tail and exercised channel unchanged); calibration-hedge.jsonl regenerated deterministically and re-pinned (f8d4e03b...). The 11/12 preflight result stands as the sanctioned pilot's mechanical outcome."}
{"id":"PROPOSED-ASM-1689","class":"STIPULATED","load_bearing":true,"text":"g2-import-v2 threshold-not-shopped disclosure (design section 11.3): the quarantined exploratory pilot's AC1 0.578 was KNOWN at redesign time and FAILS the pre-registered AC1 >= 0.65 gate; the threshold derives from the independence-ceiling and v1-stringency-continuity arguments, not from the observed value. The exploratory labels remain quarantined instrument evidence; the frozen record must run a fresh Stage-P pilot from scratch (fresh calls, pinned seeds); no exploratory label is ever scored or gate-consumed."}
{"id":"PROPOSED-ASM-1690","class":"EXTRAPOLATION","load_bearing":false,"resolution_path":"the fresh Stage-P pilot decides this for ~$1.4; a pilot stop reads INSTRUMENT-INVALID (pilot), never FAIL/PASS, and sends the rubric to a v2.2/v3 iteration","text":"g2-import-v2 honest expectation under the redesigned gate: if the fresh pilot's true agreement matches the exploratory measurement (~0.70 at the new operating point), P(pass) ~ 0.12-0.15 - the record most likely stops cheaply at the pilot. The residual failure channel is precisely located (one-sided judge-pB hedge-strictness on real multi-hedge composites; p_neg collapse 0.667 -> 0.143 item-matched): the recommended next design move is a targeted rubric clarification for multi-hedge composites (v2.2 pre-freeze or v3) with the repaired calibration set, under the redesigned AC1 gate unchanged."}
{"id":"PROPOSED-ASM-1691","class":"MEASURED","load_bearing":true,"text":"g2-import-v2 redesign build pass 2026-07-12 (design section 11.6): analysis/ontg2v2.py re-pinned sha cc5806fe... (AC1 gate, agreement panel incl. independence ceiling, selftest extended with the measured paradox tables); run-ontg2v2.py re-pinned sha ce2ab5a6... (pilotgate on AC1 with kappa co-reported, N_PILOTFLIP 8, budget ceiling 788, updated pins); calibration-hedge.jsonl f8d4e03b...; pilot-manifest.json e4ac7c95... (AC1 gate + OC + justification blocks); materials/manifest.json 8b7ba712... (8-probe pilotflip orders). Prompt template and all arm/probe files byte-identical (the rubric text is NOT edited by this redesign). All five mock verdict paths GREEN against the updated DRAFT record; prereg-freeze --dry-run clean; registry/assumptions.jsonl untouched."}
```

---

*No feasibility conclusion is drawn or implied anywhere in this design. The v1 primary
signal remains a GO-SHAPED signal under an invalid instrument until this record (or a
successor) is frozen, piloted, run, graded, and audited — and even a clean v2 PASS
licenses only the bounded soft-preference shard, PROVISIONAL-ON-LLM-PROXY, with the
two-human panel as sole adoption authority.*
