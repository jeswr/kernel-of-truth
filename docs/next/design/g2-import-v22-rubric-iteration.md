# g2-import-v2 → v2.2 rubric iteration (DRAFT; nothing frozen, nothing spent)

**Role: Fable BUILD agent, 2026-07-12. This is the ONE bounded proxy-instrument
repair the correctness-track instrument assessment
(`docs/next/analysis/correctness-track-instrument-assessment.md` §2.1, §4 item 2)
recommends before conceding g2's adoption authority to the human panel. This
document (i) diagnoses the located judge-pB hedge-strictness channel from the
two authoritative Stage-P pilots, (ii) designs the v2.2 adoption-arm rubric
refinement, (iii) closes the dangling §11.8 documentation gap (MCP-leak
calibration artifact + harness pin drift), (iv) records the retirement
PRE-COMMITMENT, (v) recommends the successor-record mechanism, and — second
build pass, same day, maintainer directive (issue #25) — (vi) upgrades the
v2.2 judge-pB from Haiku-4.5 to **Opus-4.8** (`--pb-model opus`,
v2.2-scoped; §2b). It changes NO frozen object:
`docs/next/design/g2-import-v2-repair.md` (pinned sha 5829fad9…) and every
frozen v2 instrument file stay byte-identical; all v2.2 artifacts are NEW
files plus flag-guarded harness paths that are inert without `--rubric v22`
(and `--pb-model opus`). $0 spent: mock only, zero judge calls. Companion
ASM blocks: `poc/ontology-import-g2-v2/asm-v22-1820-1828.json` and
`poc/ontology-import-g2-v2/asm-opusjudge-1870-1879.json` (both ranges
verified free).**

Epistemic tags as in the instrument assessment: [MEASURED] read from committed
bytes this tick; [DERIVED] stated arithmetic/code-reading; [STIPULATED] design
decision; [ASSESSMENT] this agent's judgment.

---

## 1. Diagnosis — the pB hedge-strictness channel, item-precise [MEASURED]

Sources: `runs/pilot-20260712-ac1/judge-p{A,B}-a3-pilot-responses.jsonl`
(pilot #1, DRAFT-era, AC1_A3 0.6909 PASS on the AC1 channel; failed only the
calibration channel 11/12 on the MCP infra leak, §3) and
`runs/real-20260712-auth/judge-p{A,B}-a3-pilot-responses.jsonl` (pilot #2,
sanctioned post-freeze, AC1_A3 0.6222 < 0.65, table 28/1/7/4, κ = 0.0000,
AC1 = its own independence ceiling to machine precision).

**1.1 The disagreement structure is a fixed 9-item core, and it is pB-stable.**

- Persistent disagreements in BOTH pilots (9/40): pA-yes/pB-no on
  `g2:pi:016` (cause), `021` (change), `025` (condolence), `033` (end),
  `064` (lie), `089` (reminder) — six items; pA-no/pB-yes on `036`/`037`
  (find), `070` (make) — three items.
- **judge-pB flipped 0/40 items between the two pilots; judge-pA flipped
  2/40** (`068` no→yes, `071` yes→no — exactly the two items that moved the
  table from 31/40 agreements to 29/40 and AC1 from 0.6909 to 0.6222). The
  run-to-run AC1 movement is pA sampling noise; the CHANNEL is the stable
  9-item core, and its one-sided component (6 v 3, 7 v 4 with pA's flips) is
  pB strictness. One converted disagreement passes the gate (AC1 ≥ 0.65 ⇔
  ≥ 30/40 at pilot-#2 marginals) [DERIVED].

**1.2 Which A3 items flip on hedge interpretation — the composite signature.**

All 9 core-disagreement items carry hedged sentences; none of the hedge-FREE
calibration behaviour disagrees (both judges 12/12 semantically correct on the
repaired 6-item set in both pilots, including "Normally a chair has legs" —
world-typicality, not meaning-guaranteed — so pB is NOT strict on SIMPLE
hedges). The discriminator is structural [MEASURED, crude link census over the
40 pilot items: agreed-yes items average 0.96 linked details per hedged
sentence (n=28); disagreement items average ~1.7 (n=11)]:

- **Multi-claim bundles**: "Normally Y is a happening that would not have come
  about, or not in that way, without X" (016); "Normally that something is
  there both before and after — it lasts through the change" (021).
- **Tacked-on contrasts read at ALL-cases force**: "Typically Y comes after X,
  or while X is going on — not before" (016).
- **Elliptical hedged sentences (no subject)**: "Normally a person speaking or
  writing." (064); "Normally by someone — a person — often through a tool or
  device…" (089, with an embedded second-order "often").
- The three pA-no/pB-yes items are the mirror image: hedged sentences whose
  MAIN clause is contestable but whose concessive widenings ("or at least
  comes to know where Y is", "But Y can also be words, a plan, or a
  happening") make the whole-sentence picture right (036/037/070).

**1.3 The ambiguity is genuine, and it is in the v2 rubric text.** The v2
hedge bullet says a hedged sentence "is true if ordinary meaning makes IT the
usual or characteristic case" — with "it" undefined over multi-claim
sentences. Three reads are genuinely open: (a) does the hedge distribute over
each linked detail (pB's strict read: every detail must be usual, jointly) or
scope over the clause as a whole (pA's read on the 6; standard
sentence-adverb semantics)? (b) what force does a tacked-on contrast inside a
hedged sentence carry ("— not before": hedged or absolute)? (c) what does an
elliptical hedged fragment assert? The two judges resolve (a)–(c) differently
in OPPOSITE directions on different items — 6 one way, 3 the other — which is
why this is an instrument ambiguity, not a pB defect alone, and why the
repair must be symmetric [ASSESSMENT anchored on the measured 6v3 core].

This is the channel PROPOSED-ASM-1690 named ("one-sided pB hedge-strictness
on real multi-hedge composites") made item-precise.

---

## 2. The v2.2 rubric refinement (SYMMETRIC; not agreement-tuned) [STIPULATED]

New file `prompt-template-v2.2.txt` (sha
`60d3403721135410b51177545e637f8c12e44e5f18f4ccf8c2ade867dc4cfde1`). The v2
template's two strength bullets, question, and answer contract are byte-carried;
ONE bullet and ONE clause are added. Verbatim additions:

Third bullet, after the v2 hedge bullet:

> - A hedged sentence may link several details together — with dashes, commas,
>   "or", "but", or a tacked-on contrast (like "— not before"). The hedge
>   covers the WHOLE sentence: judge it as ONE picture of the usual case, true
>   if that picture, taken as a whole, is right about the usual run of cases,
>   and false if the picture as a whole misdescribes the usual case. Do NOT
>   split a hedged sentence into parts and demand that each detail hold
>   separately or hold always; and do NOT read any part of a hedged sentence
>   (including a tacked-on contrast) as an unhedged ALL-cases claim. A hedged
>   sentence written without its own subject (for example "Normally with a
>   key.") continues the topic of the sentence before it, still at hedged
>   strength.

And the "no" instruction gains the mirroring clause:

> …but never answer "no" merely because a "Normally"/"Typically" sentence has
> exceptions, **and never merely because one linked detail inside a hedged
> sentence is not, on its own, the usual case, when the sentence's whole
> picture of the usual case is right.**

**Rationale and symmetry.** "Normally"/"Typically" are sentence adverbs:
clausal scope is the ordinary-English semantics, so the clarification fixes
the rubric to what the sentences already meant, rather than inventing a
convention. It is symmetric by construction: the SAME whole-sentence standard
tells a splitting judge (the pB channel, 6 items) not to fail a true picture
on one linked detail, AND keeps "false if the whole picture misdescribes the
usual case" fully in force — a bundle with a wrong core stays "no"
(exercised by the new cal:hedge-8 anchor). It also bears on the 3-item
pA-no/pB-yes mirror channel, so it addresses both directions of the measured
disagreement, not just the direction that raises agreement with pA.
**Not-tuned disclosure:** no gate, threshold, item, seed, or judge changes;
the AC1 ≥ 0.65 gate, the 40 pinned pilot items, decisive ≥ 36/40, and
hedge-flip ≤ 2/8 stand exactly as pre-registered in the v2 record. The
clarification was derived from the ambiguity classes (a)–(c), not fitted to
convert specific items, and it can move labels in BOTH directions.
**Risk disclosure (v1→v2 lesson):** the last rubric edit moved the operating
point more than it stabilised the pair; the whole-sentence reading may shift
prevalence further yes-ward (π ≈ 0.84 → higher), where every pair coefficient
discriminates weakly. That is exactly why the burden-shifted known-answer
channels (§11.4) stay load-bearing and why the pre-commitment (§4) bounds
this to ONE iteration [ASSESSMENT].

**Calibration extension** (`calibration-hedge-v22.jsonl`, sha
`63c247a9e7e7edc8769739753ef3b4c33b502f1b93dd01e12e6a948a4f97f57f`): the 6
repaired v2 items byte-carried + 2 new COMPOSITE-hedge known-answer anchors
exercising the new bullet at the operating point, one per failure direction
(the mandatory exercised-not-argued lesson):

- `cal:hedge-7` (expected **yes** — whole picture right though details vary;
  elliptical + dashes + tacked-on contrast): *"Concept: “umbrella” — In every
  case of an umbrella, it is made to keep something off — rain, or sun.
  Normally carried by a person — held up by hand when the rain comes, or
  tucked away until it is needed — not left open all the time."*
- `cal:hedge-8` (expected **no** — whole picture misdescribes the usual case
  though some linked details are true; guards against gestalt-leniency):
  *"Concept: “bicycle” — Every bicycle is made to be ridden. Normally ridden
  indoors — on a smooth hall floor, away from any rain — by the one who owns
  it."*

Cal gates become 10/10 per judge at preflight (2 v1 + 8 hedge) and **16/16**
across judges at the pilot. The hedge-flip probe families are untouched — the
whole-sentence reading rejects their absurd flips ("done by a place far
away") as decisively as the per-part reading, so the false-satisfaction
channel is not weakened [ASSESSMENT, probe text read].

---

## 2b. The v2.2 judge-pB upgrade — Haiku-4.5 → Opus-4.8 (maintainer directive, issue #25) [STIPULATED]

**Directive.** The maintainer (issue #25, informed by
`docs/next/analysis/g2-panel-vs-assessment.md`) directs that the v2.2
successor's judge-pB be **claude-opus-4-8** (`judge-pB-opus48`), replacing
Haiku-4.5, via the SAME headless-claude machinery, pinned system prompt, and
template. **The v2.2 pair is therefore pA = GPT-5.6-Sol + pB = Opus-4.8**,
and the hedge-scope rubric fix (§2) and the judge upgrade ship TOGETHER: the
one funded Stage-P pilot tests the combined instrument.

**Grounds [MEASURED, from the panel-vs-assessment analysis].** 7 of the 11
sanctioned-pilot A3 disagreements are the pB hedge-scope channel (Haiku
reading hedged multi-clause composites at per-part/unhedged strength); the
independent Fable third-read sided against pB on all 7 (6 "sound" + 1
"sound (lean)"). The remaining 4 are the pA verb-sense channel (below).
Judge-substitution risk is disclosed: the rubric fix alone might have
sufficed; replacing the judge AND the rubric in one iteration means a PASS
cannot attribute credit between them. The maintainer accepts this — the
pre-commitment (§4) bounds the family to this one iteration either way.

**Harness mechanics [MEASURED, this build].** New flag `--pb-model opus`,
v2.2-SCOPED: it dies (`ERR_ONTG2V2_PBMODEL`) unless `--rubric v22` is
active, so the FROZEN g2-import-v2 record's pB = `claude-haiku-4-5-20251001`
path (config, exact-single-key modelUsage identity check, canonical BASE
output locations) is byte-untouched without the flag. Opus-pB runs keep ALL
response files inside their run_dir (pA-proxy discipline); `pb_model` is
recorded in preflight-status and pilot-status with fail-closed mix guards in
both directions. The CLI's background haiku helper key is tolerated in
modelUsage alongside the requested opus model — EXTRAPOLATED from the
2026-07-12 fable-proxy probe (ASM-1873); the fail-closed identity check
aborts the run if the first live call disagrees. Vendor-family overlap
disclosure carries verbatim (Opus-4.8 is the same vendor family as Haiku-4.5
and the Fable design/assessment agents; pB is a SENSITIVITY judge, never
sole gold).

**The pA verb-sense channel is NOT addressed by this change [ASSESSMENT,
noted per issue #25].** The 4 remaining disagreements (g2:pi:036/037
"find", 070/071 "make") are pA over-admitting non-central senses under BARE
parentheticals — deterministic (0 flips across three same-day runs), so
they should recur in the v2.2 pilot. Per #25, the render should ALSO pin
verb sense where the parenthetical is bare — make "as described above"
point at an actual sense description (e.g. "find (X finds Y — comes upon or
locates Y)"), not a bare "(X finds Y)". **This is an open pre-pilot
coordinator/maintainer decision, not implemented here**, because re-rendered
A3 items conflict with the successor's verbatim-inheritance clause (§5:
byte-identical arm renderings, the SAME 40 pinned pilot items) and would
need a fresh estimand-identity + gold pass of their own. Options: (a) fund
that render build BEFORE the pilot (a further design pass; the AC1 gate's
"same 40 items" pin must be consciously re-based), or (b) run the pilot
with the disclosed ~4-item residual pA channel — at pilot-#2 marginals the
7-item pB channel alone straddles the gate (fixing it counterfactually gives
AC1 ≈ 0.88), so (b) is viable but spends the family's LAST iteration with a
known deterministic residual. ASM-1877 records the recurrence expectation
and its resolution path.

---

## 3. The MCP-leak calibration artifact — fixed, now documented (closes the dangling §11.8) [MEASURED]

What broke pilot #1 (`pilot-20260712-ac1`): a claude.ai MCP connector
nondeterministically attached to 1/62 pB headless sessions despite
`--tools '' --setting-sources ''`, tripping the fail-closed `tools==[]`
contract on a semantically CORRECT answer (cal:hedge-6, raw
`{"answer": "no"}`; 5/5 diagnostic repeats clean — infrastructure, not
judgment). Two-part repair, already implemented in the working harness
(commit `bf75ff84`) but never documented in any pinned design doc — the
harness comments cite a "design section 11.8" that does not exist; THIS
section is that documentation:

1. **Transport hardening:** `--strict-mcp-config` added to every headless
   claude invocation — only MCP servers from an explicit `--mcp-config` (none
   given) may load. The validator's fail-closed `tools==[]` check is
   unchanged.
2. **Calibration retry symmetry:** the cal block now goes through the SAME
   `process_item` retry ladder as real/probe items (transport backoff +
   cap-stop + ≤ 3 content attempts). It was the only single-attempt channel
   in the harness, so one 1/62-rate process artifact could fail the 12/12
   gate. The judged CONTENT contract is unchanged: first valid answer final.

**Pin-drift disclosure, mandatory:** the frozen record pins `run-ontg2v2.py`
at `ce2ab5a6…`, but the hardened harness that ran sanctioned pilot #2 is
`cd8e2f89…` (committed 13:56Z, post-freeze 13:20:02Z, pre-run 15:24Z) — the
sanctioned pilot ran OFF-PIN with the fix in place and no ops amendment
recording it. This is a second, independent reason the frozen record cannot
simply be re-entered (§5). The v2.2 harness (first v22 build pass
`efe134ad…`: `--rubric v22` flag, v22 pins, rubric-mix guards; second pass,
issue #25: `--pb-model opus` judge-pB upgrade, pb_model status stamps + mix
guards, opus modelUsage allowance, run_dir output routing) is now
`16d71d8ffbaa09d0ec1dcd86770edf97a555b00571ca2b6e7b581637dda77c5b`; the
successor record must pin THIS sha and fill both judge CLI banners at its ops
amendment. Without the flags the harness's v2 behaviour is unchanged
(regression-mocked, §6).

---

## 4. PRE-COMMITMENT (recorded here and in ASM-1825, BEFORE any v2.2 judge call) [STIPULATED]

> **If the v2.2 Stage-P pilot's Gwet AC1_A3 on the 40 pinned items is
> < 0.65 — a SECOND sanctioned AC1 pilot failure for this record family —
> the v2.2 proxy pair (GPT-5.6-Sol + Opus-4.8) is RETIRED as an
> adoption-arm (A3) instrument for the g2-import family, AND no further
> LLM proxy pair may be substituted or funded for A3 in this family — the
> judge upgrade (§2b) does NOT reset the one-iteration bound. The adoption
> decision passes to the two-human adjudicated panel on the 84 slots —
> which the frozen envelope has always named as the sole authority for
> permanent adoption, and under which the v1 primary signal holds on every
> label bracket including the maximally conservative pair-concordant
> 42/84 ≥ 34/84. Retirement binds the proxy pair's ADOPTION-ARM authority
> only: it licenses no conclusion about H-SOFT/H-SRC/H-SEP in either
> direction, does not retire the judges for unhedged arms or other record
> families, and does not bind the human panel. A v2.2 pilot PASS licenses
> exactly the pre-registered next step: the ~$5–6 full 796-call run under
> the successor record, nothing else.**

Either branch terminates the proxy iteration loop, exactly as the instrument
assessment's §2.1 closeability call requires ("fund exactly one v2.2
iteration… with a pre-commitment that a second AC1 failure retires the
proxy-pair instrument for this record family"). Note vs ASM-1825, which
named the GPT-5.6-Sol + **Haiku-4.5** pair: under the §2b directive
Haiku-4.5's pB role is retired NOW, by maintainer decision rather than by a
second AC1 failure, and the restated clause above (ASM-1876) is STRICTLY
STRONGER — it closes the judge-substitution loophole a literal reading of
ASM-1825 would have opened (swap a judge, claim a fresh pair, iterate
again). Anti-shopping intent carries forward intact.

---

## 5. Amendment vs successor record — RECOMMENDATION: successor record `g2-import-v2.2` [ASSESSMENT]

The case for a pre-final amendment was considered and fails. For amendment:
no final-phase (full-arm) call was ever made; pilot labels are instrument
evidence only; the record family already admits scoped post-freeze amendment
(the ops `harness_manifest` fill). Against, decisively:

1. **The rubric is constitutive, not ops.** `frozen_sha256` covers
   `pins.artifact_hashes` including `prompt-template-v2.txt`; the record's
   own estimand-identity ASM stipulates the v2 sentence-force rubric as part
   of the frozen instrument. The only amendment channel the record sanctions
   is the harness_manifest banner fill.
2. **The Stage-P gate has FIRED.** The sanctioned pilot mechanically returned
   INSTRUMENT-INVALID (pilot AC1 channel, `real-20260712-auth/result.json`
   assembled, pilot-only). Re-entering Stage-P under the same frozen id would
   put two authoritative pilot outcomes under one record — a gate-shopping
   surface the pilot-stop discipline exists to prevent.
3. **The record prescribes its own exit.** The pinned verdict-name mapping
   reads INSTRUMENT-INVALID as "no conclusion, repair and mint a new frozen
   run"; §11.7's disjunction ("v2.2 under this same DRAFT record before
   freeze, or a NEW RECORD after") resolves to the successor branch now that
   freeze (2026-07-12T13:20:02Z) precedes the fail.
4. **Precedent:** v1 → v2 was exactly this mechanism — same estimand, new
   record — and the successor lawfully absorbs the two standing off-record
   facts (harness pin drift §3; the §11.8 documentation gap).

**Successor shape (recommended, NOT frozen here — coordinator action):**
`registry/experiments/g2-import-v2.2.json`, kot-reg/2, inheriting VERBATIM the
estimand identity chain (same 84 slots, byte-identical arm renderings, A0
frozen 33/84, primary ≥ 34/84, sep gates, judge-pA, rider, envelope incl.
human-panel-sole-authority), all v2 instrument gates unchanged (pilot AC1_A3
≥ 0.65 on the SAME 40 pinned items + OC block, decisive ≥ 36/40, hedge-flip
≤ 2/8, full-run AC1 ≥ 0.65/arm etc.), both prior pilots quarantined as
instrument evidence. **Judge-pB is pinned as `judge-pB-opus48`,
`claude-opus-4-8`, via the same headless-claude protocol (§2b)** — the ONE
inherited-protocol departure, maintainer-directed (issue #25). New pins:
`prompt-template-v2.2.txt` 60d34037…, `calibration-hedge-v22.jsonl`
63c247a9…, `run-ontg2v2.py` 16d71d8f… (invoked `--rubric v22 --pb-model
opus`), cal gates 10/10 preflight per judge / 16/16 pilot, call ceiling 788
→ **796** (796 × $0.012 = $9.552 ≤ $10; the pinned per-call bound covers
Opus-4.8 at the measured prompt envelope, ASM-1874, and pB draws no API
dollars on the OAuth path), §4's pre-commitment as a verdict-bearing clause,
ASM-1820..1828 + ASM-1870..1879 registered at freeze. The §2b verb-sense
render question must be DECIDED (option a or b) before freeze. Disclosure
carried on every readout: this is the family's LAST proxy-pair iteration for
A3 under the pre-commitment.

---

## 6. Mock validation ($0) + launch [MEASURED]

Zero judge calls were made this build. Mocks executed 2026-07-12:

- `--rubric v22`, all five verdict paths GREEN
  (`runs/mockcheck-v22-20260712/`): go→PASS, nogo→FAIL,
  instrument→INSTRUMENT-INVALID, pilotfail→INSTRUMENT-INVALID
  (pilot_valid=False), breadth→FAIL (breadth_confound=True); pilot-status
  records `rubric: v22`, cal 16/16 gate active, 8 cal rows per judge.
- Default-path regression GREEN (`runs/mockcheck-v2default-20260712/`):
  go + pilotfail with NO flag → `rubric: v2`, cal 12/12 — frozen v2
  behaviour untouched.
- Rubric-mix guard exercised directly: a pilot-status minted under v2
  ABORTS a v22 invocation (`ERR_ONTG2V2_RUBRIC`), and vice versa by
  symmetry; `verify_pins` green over the v22 pin set.

Second build pass (issue #25, `--pb-model opus`), mocks executed 2026-07-12:

- `--rubric v22 --pb-model opus`, all five verdict paths GREEN
  (`runs/mockcheck-v22opus-20260712/`): go→PASS, nogo→FAIL,
  instrument→INSTRUMENT-INVALID, pilotfail→INSTRUMENT-INVALID
  (pilot_valid=False), breadth→FAIL (breadth_confound=True); pilot-status
  records `rubric: v22, pb_model: opus`, cal 16/16; flag order
  independence verified (`--pb-model` before `--rubric` in argv, same
  GREEN).
- Default-path regression GREEN after the pB edit
  (`runs/mockcheck-v2default-opusbuild-20260712/`): go + pilotfail with NO
  flags → `rubric: v2, pb_model: null`, cal 12/12 — the frozen pB=Haiku
  path is untouched; all 25 frozen-record `artifact_hashes` re-verified
  byte-identical except the already-disclosed `run-ontg2v2.py` drift (§3).
- Guards exercised directly: `--pb-model opus` WITHOUT `--rubric v22` dies
  (`ERR_ONTG2V2_PBMODEL`); `--pb-model haiku` dies; pb-model mix guard
  fires in BOTH directions (v22-no-opus pilot-status vs v22+opus
  invocation, and the reverse).
- Anchor model-agnosticism check: zero model/vendor/judge-name tokens in
  the 2 v1-cal + 8 hedge-cal items, `prompt-template-v2.2.txt`, and the
  pinned pB system prompt (the only "judge" hits are the generic role word
  in the template). Opus faces the same pinned bytes as Haiku did and must
  clear the same mechanical gates: 10/10 preflight anchors per judge,
  16/16 pilot cal across judges.

**Pilot cost:** preflight (2+8)×2 = 20 + pilot (8+40+8)×2 = 112 → **132
calls ≈ $1.06 at the v1-measured ≤ $0.008/call, ≤ $1.58 at the pinned
$0.012 bound** (the ~$1.4 shape preserved). Under pB=Opus the pB half (66
calls) draws NO API dollars (OAuth path, `apiKeySource == "none"`
enforced); its API-equivalent worst case at the measured prompt envelope is
~≤ $0.009/call, inside the pinned bound (ASM-1874). Stage-P discipline
unchanged: any pilot-gate failure stops before any full-arm call.

**Exact coordinator launch command** (after the coordinator freezes the
successor record and runs reuse-check; concurrency 1, this box; pair =
pA GPT-5.6-Sol + pB Opus-4.8):

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth/poc/ontology-import-g2-v2 \
&& RUN=runs/pilot-v22-$(date -u +%Y%m%d) \
&& nice -n 10 python3 run-ontg2v2.py preflight pA "$RUN" --rubric v22 --pb-model opus \
&& nice -n 10 python3 run-ontg2v2.py preflight pB "$RUN" --rubric v22 --pb-model opus \
&& nice -n 10 python3 run-ontg2v2.py pilot     pA "$RUN" --rubric v22 --pb-model opus \
&& nice -n 10 python3 run-ontg2v2.py pilot     pB "$RUN" --rubric v22 --pb-model opus \
&& nice -n 10 python3 run-ontg2v2.py pilotgate    "$RUN" --rubric v22 --pb-model opus
```

PILOTGATE GREEN ⇒ the full run may proceed under the successor record;
PILOTGATE FAIL ⇒ INSTRUMENT-INVALID (pilot channel named) AND §4's
pre-commitment fires: the proxy pair is retired for A3 and the human panel
is the instrument.

---

*No feasibility conclusion is drawn or implied. Every sentence about a future
verdict carries the rider verbatim: PROVISIONAL-ON-LLM-PROXY; same 84
self-authored kernel-v0 slots; point-estimate engineering gate, not
statistical superiority; soft non-binding typing only — never hard laws; no
feasibility conclusion.*
