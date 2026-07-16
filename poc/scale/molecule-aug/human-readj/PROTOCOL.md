# s5-human-readj — 2-human fidelity re-adjudication of the molecule-S5 re-pilot (PRE-REGISTRATION)

**Status:** designed & frozen 2026-07-16 (designer role, pseudonymous; the
coordinator builds the human spreadsheet and runs the reconciliation and the
pinned analysis). Design + freeze only: no run happens in this session, no
GPU, no LLM call, nothing regenerated, nothing committed to git.
**Registry record:** `registry/experiments/s5-human-readj.json` (kot-reg/1).
**Mandate [STIPULATED]:** the approved coordination decision **#45 option 2**
— an independent, judge-pathology-free correctness channel over the 95
EXISTING fidelity records of the molecule-S5 re-pilot, to test whether the
LLM-proxy panel's instability (F1/F2 kappa 0.3816 overall, 0.2679 on the
molecule arm — MEASURED, `stage1-repilot/results-s5-v2.json`) concealed the
sign of the E2 effect the re-pilot's PIVOT fired on.

## 1. Claim under test + hypotheses

The re-pilot (REPILOT-v2.1, FREEZE-v2.1.json) fired its pre-declared kill:
"PIVOT iff, after repair, EITHER ref-bearing molecule cells < 80% OR the E2
primary delta <= 0pp again." — ref-bearing 47/48 = 97.9% PASSED the floor;
the PIVOT fired on the delta clause alone (E2 delta −4.2pp, flat 14/24 vs
mol 13/24, McNemar p = 1.0, Tango95 [−28.0, +21.5]pp — MEASURED, proxy
panel). The panel that produced those verdicts was measurably unstable, and
worst on the treatment arm. Two disjoint hypotheses:

- **H-CONCEAL** (the reading this design can support): proxy-judge noise, not
  record content, produced the non-positive delta; on human gold the
  molecule arm's E2 exceeds the flat arm's (delta > 0).
- **H-CORROBORATE** (the reading this design can kill H-CONCEAL with): the
  sign is real; human gold reproduces a non-positive delta and the PIVOT
  stands on a channel with no LLM-judge pathology in it.

This is an adjudication-channel experiment over EXISTING artefacts. It
regenerates nothing, re-prompts nothing, and re-judges only with humans.

## 2. The records (MEASURED, pinned; do NOT regenerate)

The 95 judgeable fidelity items of
`poc/scale/molecule-aug/s5-run/stage1-repilot/judge-inputs-fidelity/` — 48
flat + 47 ref-bearing molecule cells over the same fitted n=24 concepts, one
molecule cell exhausted (`conception.mol-fable`,
`ERR_REF_UPTAKE_EXHAUSTED`) and retained as ITT NOT-FAITHFUL, never shown to
any adjudicator. Each item is the concept header (concept, synset, pos,
lemmas, sense-fixing wn31 gloss) plus ONE fully-expanded, provenance-free
candidate explication — the exact bytes the proxy panel judged. The whole
packet is re-materialized byte-identically into the corpus
`data/s5-human-readj/` by the deterministic builder
`poc/scale/molecule-aug/human-readj/build_kit.py` (fail-closed provenance
checks; refuses divergent existing content) and pinned by kot-corpus-hash/1
digest `e3cb130c2bedaa0cef1941270b47aa54b978a6560f28512958a2fc43242d399c`.

## 3. Blinding [STIPULATED, procedural + structural]

Each human sees ONLY: the item id, the item text (concept header + candidate
explication), and the rubric. Never: the arm (flat/molecule), generator or
model identity, cell identity, provenance, the LLM-proxy judgments, any
aggregate, or any project document. Presentation is arm-mixed in ONE pinned
shuffled order for both adjudicators — permutation seed
`s5-human-readj/1|order|20260716`, algorithm pinned in
`data/s5-human-readj/order.json` (max same-arm run in the realized order: 7).
The blinding key (`data/s5-human-readj/key.json`) is coordinator-only and is
not needed to build the sheets: `answers-template.csv` + `items/` are
arm-free by construction, so the spreadsheet can be assembled without ever
opening the key. The key is opened only by the pinned analysis.

**Residual, disclosed [STIPULATED, ASM-2461]:** blinding removes labels and
provenance, not structure. Molecule-arm items may carry nested
`subExplication` blocks that flat items cannot; a judge could in principle
infer condition from surface structure. This residual is IDENTICAL to the
one the frozen proxy instrument carried (its verdicts are the comparison
channel), the rubric forbids using size/nesting/style, and the mechanical
Step-3 verdict rule minimizes the leverage such an inference has. The by-arm
human agreement and by-arm proxy-vs-human disagreement outputs are the
monitoring surface for it.

## 4. Adjudicators, rubric, reconciliation

- **Judges:** 2 kernel-naive HUMAN adjudicators (no prior exposure to this
  project's kernel, records, or judging; sourcing disclosed in the run log by
  pseudonym only — judge-H1, judge-H2; no real names, no account strings —
  ASM-2459). Each judges ALL 95 items independently: verdict ∈ {FAITHFUL,
  LOSSY, CANNOT-SAY(escape)} + a mandatory compact criterial-feature audit.
  No LLM or machine assistance anywhere in the channel (that is the point of
  the channel).
- **Rubric:** `data/s5-human-readj/rubric.md` — the pinned proxy instrument
  `s5-judge-fidelity-v2.1.md` (criterial-feature checklist + MECHANICAL
  verdict rule) re-addressed to a human, with exactly four deltas
  (human addressee/spreadsheet output; CANNOT-SAY escape; quality score
  dropped; F3 section replaced by the reconciliation rule). Instrument
  comparability to the proxy channel is by construction.
- **Reconciliation:** `data/s5-human-readj/reconciliation.md`, VERBATIM and
  binding (quoted in full there; summary: both sheets complete → both
  hash-pinned → discordant items revealed arm-blind → structured blind
  discussion per item resolving each disputed FEATURE against the rendered
  clauses → mechanical Step-3 verdict on the agreed classification → no
  consensus ⇒ UNRESOLVED, scores LOSSY fail-closed ITT, counted, capped;
  concordant CANNOT-SAY ⇒ LOSSY ITT, counted as escape; the exhausted cell
  scores LOSSY ITT). Human-human agreement statistics are computed on the
  PRE-reconciliation independent verdicts only.

## 5. Endpoints, statistics, and honest power (ANALYSIS PLAN)

Scoring is the registered re-pilot estimand on HUMAN gold — statistics ported
verbatim from the pinned scorer (`run_s5.py`: exact two-sided McNemar; Tango
(1998) asymptotic score CI; Cohen kappa + Gwet AC1 + seeded bootstrap;
E2/ITT), implemented in the pinned pure-function analysis
`analysis/s5_human_readj.py` (selftest 26/26 PASS, including the
proxy-reproduction oracle: feeding the pinned proxy finals through the human
channel reproduces b=5, c=4, delta −4.2pp, p=1.0, Tango95 [−28.0, +21.5]
exactly).

- **ONE PRIMARY:** the human-gold paired concept-level ensemble comparison,
  matched to the re-pilot's registered primary. Per concept (n=24, ITT,
  every concept analyzable): `Flat-E2H = 1` iff any of {flat-luna,
  flat-fable} is human-final FAITHFUL; `Mol-E2H` likewise over {mol-luna,
  mol-fable}; the exhausted cell is NOT-FAITHFUL. Effect Δ̂ = (c−b)/24 in pp
  (`/analysis/delta_pp`), exact two-sided McNemar p, Tango 95% CI.
- **TOST / interval:** equivalence at the registered MCID margin ±15pp via
  the Tango 90% CI (two one-sided 5%): pass iff the CI lies inside
  (−15, +15)pp (`/analysis/tost_equivalence_pass`).
- **Robust sign booleans (fail-closed both directions):**
  `sign_flip_confirmed` = Δ̂ > 0 AND p < 0.05 AND Δ̂ > 0 under EVERY possible
  resolution of UNRESOLVED cells (exhaustive bracket
  `/analysis/delta_pp_unresolved_min/max`); `sign_nonpositive` = Δ̂ ≤ 0 under
  the ITT primary AND under every resolution. A bracket straddling zero can
  reach neither — INCONCLUSIVE. The ITT fail-closed rule can therefore never
  manufacture a sign verdict (skeptic finding S-3, §10).
- **Secondaries (nominal, no multiplicity claim):** per-generator paired
  deltas (luna, fable); human-human agreement raw3/raw/kappa/AC1 + seeded
  boot95, overall and by arm; PROXY-vs-HUMAN disagreement analysis —
  cell-level agreement on the 93 proxy-binary cells, per-arm disagreement
  rates + arm gap (the panel-instability signature localizer), concept-level
  E2 flip counts, and `sign_flipped_vs_proxy` (human Δ̂ > 0 where the pinned
  proxy Δ̂ = −4.2 ≤ 0) — the registered answer to "does the human channel
  flip the sign the proxy panel measured?". The re-pilot's cascade and
  quality secondaries are NOT re-measured (quality is not elicited; self-flag
  is arm-side metadata, untouched by this channel) — disclosed drop.
- **Power, honestly [STIPULATED, ASM-2462]:** n is FIXED at 24 concepts / 95
  cells; nothing here can cure it. Simulated at the re-pilot's observed
  discordance (~9/24): power of the significance clause ≈ 0.13 at the
  originally predicted +15pp, ≈ 0.41 at +25pp, ≈ 0.61 at +30pp, ≈ 0.84 at
  +35pp; MDE₈₀ ≈ +33pp. TOST at ±15pp is essentially unreachable at this n
  (pass probability ≤ 0.05 at true Δ=0 and that discordance) — a NULL
  verdict is therefore expected to be unreachable and its absence carries no
  information. What the experiment DOES resolve at n=24: the SIGN of the
  human-gold point estimate under a full sensitivity bracket, the interval,
  and a well-powered per-cell disagreement analysis (93 paired binary
  verdicts) between proxy and human channels. It is an independent-channel
  sign-check, not a confirmation instrument.

## 6. Instrument gates (G-HRA → INSTRUMENT-INVALID, never a hypothesis event)

All-of, evaluated mechanically by the pinned analysis:
1. `pins_valid` — every corpus file matches `manifest.json`; the pinned
   proxy finals reproduce the frozen re-pilot primary (else the analysis
   REFUSES outright: integrity, not instrument, ERR_HRA_*).
2. `completion_valid` — both sheets cover exactly the 95 ids with valid
   verdict tokens (fail-closed parse).
3. `escape_valid` — CANNOT-SAY share ≤ 10% of the 190 elicitations.
4. `unresolved_valid` — post-reconciliation UNRESOLVED ≤ 4 of 95.
5. `agreement_valid` — pre-reconciliation 3-category raw agreement ≥ 0.70
   (the proxy panel measured 0.6774; a human channel that cannot beat the
   pathology it adjudicates cannot adjudicate it).
Disclosure (not a gate): human binary kappa < 0.40 sets
`instrument_unreliable_disclosure` (mirrors the re-pilot's ASM-2402
discipline).

## 7. Kill + envelope (VERBATIM, binding)

**KILL:** "s5-human-readj is an independent-channel SIGN-CHECK over the 95
existing re-pilot fidelity records, PROXY-PROVISIONAL-replacing on exactly
one axis (judge pathology): H-CONCEAL is DEAD iff sign_nonpositive — the
human-gold E2 delta is <= 0pp under the ITT primary AND under every
resolution of unresolved cells — and the molecule-S5 PIVOT then stands
corroborated by a channel with no LLM judge in it; no further human
re-adjudication of these 95 records may be proposed. A verdict of PASS
(sign_flip_confirmed) licenses exactly ONE action: registering a fresh,
properly powered human-gold molecule-S5 successor before any re-opening of
the molecule-S5 line. This experiment CANNOT move the programme CORRECTNESS
verdict-word alone, in either direction, at any outcome; it cannot un-fire
the re-pilot PIVOT retroactively; gate failure is INSTRUMENT-INVALID, never
evidence about the records."

**ENVELOPE:** "Binding on any outcome: claims are scoped to THESE 95 frozen
records — 24 fitted WordNet-stride concepts, 2 generators, the v2.1 expanded
rendering, this rubric, these two pseudonymous kernel-naive adjudicators —
and to the E2 best-of-two oracle ensemble, which is a ceiling, not a
deployable yield. n=24 licenses a SIGN and an interval, never a magnitude
claim, never confirmation (MDE80 ~ +33pp; the TOST NULL is disclosed as
essentially unreachable at this n). Nothing here validates the molaug-v0
inventory, licenses any deployable-yield or coverage-general claim, or
speaks to any concept distribution beyond the pinned sample. The
proxy-vs-human disagreement analysis characterizes THIS proxy panel on THESE
items only — it licenses no general claim about LLM judges. No scale
language of any kind is licensed."

## 8. What this experiment is NOT

- Not a re-run: generation, gating, expansion, proxy judgments all stay
  byte-frozen; only NEW human verdicts are created.
- Not a controls-bearing capability experiment: kernel-as-text and
  shuffled-kernel controls are N/A — there is no model-under-test and no
  kernel-in-context arm anywhere in this design; the matched FLAT arm
  re-adjudicated under the identical blind protocol is the baseline, and the
  frozen proxy verdicts are the comparison channel (never re-run). This is
  the same dropped-arms discipline as f2b-transfer's right-size note.
- Not a power cure: see §5.
- Not a verdict-word mover: see §7 KILL.

## 9. Pins

| what | where / value |
|---|---|
| input corpus (95 items + key + order + rubric + reconciliation + template) | `data/s5-human-readj/` kot-corpus-hash/1 `e3cb130c2bedaa0cef1941270b47aa54b978a6560f28512958a2fc43242d399c` |
| per-file shas incl. every item | `data/s5-human-readj/manifest.json` (inside the corpus digest) |
| shuffle seed | `s5-human-readj/1\|order\|20260716` (order.json, inside the corpus) |
| rubric | `data/s5-human-readj/rubric.md` (inside the corpus; derived from frozen `s5_judge_fidelity_v21_sha256 6fa6da2e…2ec4`) |
| reconciliation rule | `data/s5-human-readj/reconciliation.md` (inside the corpus, verbatim) |
| proxy finals + re-pilot aggregates | `data/s5-human-readj/key.json` `proxy_pins` (sha-pins results-s5-v2.json, judge-key-v2.json, FREEZE-v2.1.json) |
| analysis script | `analysis/s5_human_readj.py` (sha in the registry record; selftest 26/26) |
| builder (provenance) | `poc/scale/molecule-aug/human-readj/build_kit.py` (sha in registry `pins.harness_manifest`) |
| human sheets | PINNED-AT-INPUTS: both raw CSVs + the consensus CSV are sha256-pinned in the run log, raw sheets BEFORE any discordant item is revealed |

Any post-freeze change to a pinned input ⇒ the run is exploratory, full stop.

## 10. Pre-freeze skeptic attack record

- **S-1 structural unblinding** (nesting reveals arm) → cannot be removed
  without re-rendering (which would break comparability with the proxy
  channel); disclosed as ASM-2461, monitored via by-arm agreement +
  disagreement outputs, leverage bounded by the mechanical verdict rule.
  ACCEPTED-DISCLOSED.
- **S-2 consensus contamination** (dominant judge steers reconciliation) →
  agreement statistics restricted to pre-reconciliation verdicts; discussion
  is feature-anchored with clause citations; UNRESOLVED escape exists and is
  fail-closed. FIXED-BY-DESIGN.
- **S-3 ITT manufactures the sign** (UNRESOLVED→LOSSY could flip Δ̂ ≤ 0) →
  sign booleans made robust over the exhaustive unresolved-resolution
  bracket; a straddling bracket yields INCONCLUSIVE. FIXED (analysis
  hardened before freeze; selftest case added).
- **S-4 coordinator-side leak** (key open while building sheets) → sheets
  are buildable from arm-free files only; key needed only at analysis;
  procedural rule in coordinator README. FIXED-PROCEDURAL.
- **S-5 escape abuse** (CANNOT-SAY as a soft middle grade guts n) → rubric
  narrows the escape to procedure-failure; 10% gate; concordant escapes
  scored ITT. FIXED-BY-GATE.
- **S-6 verdict overreach** (a PASS read as un-PIVOTing molecule-S5, or a
  FAIL read as moving CORRECTNESS) → kill text forecloses both directions
  verbatim; PASS licenses only registering a successor. FIXED-BY-KILL-TEXT.
- **S-7 unreachable NULL quietly read as evidence** → §5 pre-declares the
  TOST NULL essentially unreachable at n=24; envelope repeats it.
  FIXED-BY-DISCLOSURE.

## 11. Changed-file list + self-check

Added by this line (working tree; git custody stays with the maintainer —
NOTHING COMMITTED, per the single-shot mandate):

- `poc/scale/molecule-aug/human-readj/` — `PROTOCOL.md` (this doc),
  `rubric.md`, `reconciliation.md`, `coordinator-readme.md`, `build_kit.py`
- `data/s5-human-readj/` — the built, pinned input corpus (95 items,
  key.json, order.json, manifest.json, rubric, reconciliation rule, answer
  template, coordinator README)
- `analysis/s5_human_readj.py` — pinned analysis (selftest 26/26 PASS)
- `registry/experiments/s5-human-readj.json` — kot-reg/1, frozen
- `registry/assumptions.jsonl` — append-only: ASM-2459..ASM-2463
- `registry/frozen-index.json` — appended by prereg-freeze

Self-check gate: `python3 analysis/s5_human_readj.py --selftest` → 26/26
PASS; `python3 poc/scale/molecule-aug/human-readj/build_kit.py` →
byte-idempotent, corpus digest reproduced; `tools/registry/prereg-freeze.py
--dry-run` then freeze → frozen_sha256 recorded below by the freeze tool;
`tools/registry/registry-check.py` → PASS (pasted in the session report).
