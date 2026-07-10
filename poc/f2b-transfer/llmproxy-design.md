# f2b-transfer-llmproxy — design note + pre-registration text (prereg_doc for registry/experiments/f2b-transfer-llmproxy.json)

> STATUS: DESIGN (record DRAFT, dry-run-validated). STAND-IN, NOT THE
> ADJUDICATING EXPERIMENT. The maintainer requested (2026-07-09) that
> GPT-5.6 ("sol") fill the judge-1 role of f2b-transfer's frozen §4
> adjudication protocol as a FAST FEASIBILITY READ, because the required
> kernel-naive HUMAN judge-1 is unavailable. That change is designed here as
> a SEPARATE experiment; `registry/experiments/f2b-transfer.json`
> (frozen_sha256 b341a090…) is NOT touched — no correction, no
> reset-refreeze, no bytes changed — and its human judge-1 path stays open
> and solely adjudicating. Designed by FABLE (design owner;
> design-vs-judge separation: the judged model, GPT-5.6, contributed
> NOTHING to this protocol — it only answers blind items). Execution is
> Opus-runner work, mechanical, post-freeze (§S5).

Every load-bearing claim is tagged MEASURED / LIT-BACKED / STIPULATED /
EXTRAPOLATION per the honesty guard; STIPULATED and EXTRAPOLATION entries
are registered (ASM-0021, ASM-0022).

## S1. Separate experiment id, not a proxy-arm on a re-frozen f2b-transfer

DECISION: mint the FRESH id `f2b-transfer-llmproxy` and leave f2b-transfer
frozen and untouched [STIPULATED, this note; the three grounds below].

1. **The reset-refreeze precedent's own legitimacy test fails.**
   PREMISE: the corrections/1 reset-refreeze was lawful because at correction
   time there existed "zero adjudication data (judge-1 not started, judge-2
   not run)" [MEASURED: registry/corrections/f2b-transfer/1-prefreeze-correction.json,
   `legitimacy` field]. PREMISE: the GPT-5.5 judge-2 run is IN FLIGHT now
   under the frozen record [MEASURED: poc/f2b-transfer/opus-runs/20260709T232652Z/main-progress.log
   + preflight-status.json pass:true]. So a §4 judge-identity change to
   f2b-transfer today is NOT pre-data by the standard the programme itself
   set; re-freezing would be a post-data protocol change wearing a
   correction's clothes.
2. **Judge identity is design scope, not clarification.** Corrections/1
   changed HOW judges judge (S1–S7 standards, both judges, one protocol);
   this changes WHO judges — the gold standard itself. The frozen envelope
   scopes every claim to "THIS gold standard (blind dual-judge adjudication
   under the pinned d-adj-t protocol…)"; swapping the human for an LLM
   changes the estimand (LLM endorsement ≠ human-anchored external gold), and
   a different estimand is a different experiment.
3. **The single-draw rule would exile the definitive result.** f2b-transfer
   pre-commits "one build, one adjudication round; … after the freeze it is
   a new experiment id". Burning its adjudication round on the LLM stand-in
   would force the eventual HUMAN adjudication — the only one that
   adjudicates H-TRANSFER vs H-CIRC — into a new id, while the weaker proxy
   held the canonical name. Exactly backwards. The stand-in takes the
   suffixed id; the human experiment keeps its frozen record, its d-adj-t
   placeholder, and its name.

Rejected alternative — labelled proxy-arm on a re-frozen f2b-transfer:
fails (1) outright, and even were it pre-data it would entangle two
estimands under one kill/envelope and consume the single adjudication round.

## S2. The weakening (verbatim, binding) and the kill

The record's `extrapolation_envelope_verbatim`, reproduced byte-identically
(this is THE reduced envelope; any PASS citation must carry it):

> Binding on ANY verdict of this record and on every citation of its numbers. STAND-IN, NOT THE ADJUDICATING EXPERIMENT: the judge-1 role is filled by a pinned LLM (GPT-5.6-Sol via codex-cli 0.144.1, reasoning effort low, pinned invocation data/d-adj-t-llmproxy/judge-1p-invocation.md) because the kernel-naive HUMAN judge-1 that the frozen f2b-transfer section-4 protocol requires is unavailable at run time; f2b-transfer (frozen_sha256 b341a0901e12023d3c56bdc196be0b9c492c7d348f988416d7e9c43aade20879) remains FROZEN, unconsumed, and is the ONLY experiment on this line whose Stage-1 adjudicates H-TRANSFER vs H-CIRC. External gold here IS one LLM's endorsement under blind rendering -- NOT blind human concept competence. Binding weakenings: (1) SINGLE JUDGE FAMILY -- judge-1p (GPT-5.6) and the diagnostic judge-2 (GPT-5.5) are same-vendor, adjacent-generation models and may correlate through shared training data, shared preference tuning, and shared style priors; they are NOT a two-judge panel in the section-4 sense; their raw agreement is reported as a CORRELATION DIAGNOSTIC and is NEVER evidence of independent validation; A_1p estimates 'GPT-5.x-family endorsement of the kernel's content', an estimand that family-level bias can inflate or deflate independent of real kernel content. (2) KERNEL-TRADITION FAMILIARITY -- the judge is kernel-INSTANCE-naive by context control (E5: empty out-of-repo workdir, user config ignored, memories and web search disabled) but NOT kernel-tradition-naive: NSM literature and NSM-style explications are plausibly in GPT-5.x training data (ASM-0021), so the judge may endorse a familiar explication STYLE rather than judge content from concept competence -- a channel that inflates A_1p under BOTH hypotheses; the deranged-probe gate bounds only its crudest form. (3) PARTIAL CIRCULARITY BREAK ONLY -- the LLM's label is a genuinely different function from the kernel verifier's string-equality, so the d-qa/d-qa-r gold-definition circularity is broken in the letter, but with WEAKER independence than a human judge. (4) LICENSE OF A PASS -- a PASS means exactly: 'an independent, kernel-instance-naive LLM, under blind rendering with a demonstrated working escape, endorses the kernel's record content at the pre-declared bar on the 360 d-qa-t items'. It is a WEAK FEASIBILITY PROXY (ASM-0022). It does NOT adjudicate H-TRANSFER vs H-CIRC, does NOT substitute for f2b-transfer Stage-1, does NOT license f2b-transfer Stage-2 GPU cells or promotion of any f2b claim, and does NOT extend to human judges, public-benchmark surfaces, other corpora, other rungs, or any coverage-general claim (kernel-expressibility coverage 0.3542 at rung molecules-v0, MEASURED by m0b on one incomplete kernel-v0 instance, restated mandatorily). (5) ASYMMETRIC READING -- the named channels plausibly push A_1p UP (direction unproven, ASM-0021), so FAIL is the more informative outcome: a FAIL warrants the same programme response as f2b-transfer's kill (d) -- pause the verifier-content line and escalate to the maintainer -- while remaining formally scoped to this proxy id; a PASS licenses only continued investment (human judge-1 recruitment, Stage-2 harness build-out) and never upgrades any claim. (6) Item bytes, blind rendering, and the S1-S7 judging standards are byte-identical to f2b-transfer's; nothing else carries over.

The record's `kill_criterion_verbatim`, byte-identical:

> f2b-transfer-llmproxy kill (STAGE-1-ONLY, zero GPU, judge-1 role filled by the pinned GPT-5.6 STAND-IN): FAIL fires iff the one-sided 95% Wilson lower bound of A_1p < 0.70, where A_1p = n_agree_j1p / n_labelled_j1p over the 360 blind d-qa-t items, computed from judge-1p's labels ALONE (GPT-5.6-Sol, pinned invocation data/d-adj-t-llmproxy/judge-1p-invocation.md); agreement = judge-1p label equals membership gold; escape tokens (NONE / 'cannot say') count as DISAGREEMENT; no-label items leave the denominator (instrument events, capped by gate). This mirrors f2b-transfer kill (d) in FORM ONLY; it can neither fire nor discharge f2b-transfer's own kill (d), whose judge-1 is a kernel-naive HUMAN. Degeneracy discipline (INSTRUMENT-INVALID, never FAIL/PASS): preflight failure; n_labelled_j1p < 300 of 360; n_nolabel_j1p > 18 (5%); raw judge-1p/judge-2 agreement < 0.80 over both-labelled items (single-family stability check -- only its FAIL direction is informative; its pass direction validates nothing, judges being one model family); deranged-probe false-endorsement point-rate >= 0.30 or probe coverage < 54/60 (every probe item's own-gloss is deranged out by a seed-pinned Sattolo cycle, so a content-competent judge must answer NONE; a judge endorsing wrong glosses at >= 0.30 is answering from style/familiarity, and its endorsement of the real items cannot be read as content endorsement -- exactly the channel that would fabricate a proxy-PASS under H-CIRC).

Reading guide (informative): a PASS here means "an independent kernel-naive
LLM endorses the kernel content" — a weak feasibility proxy that sequences
programme investment and nothing else. It is NOT the adjudicating
content-vs-circularity result; only the human-judged f2b-transfer Stage-1 is.
A FAIL is the more informative outcome (envelope clause 5) and warrants the
same programme response as kill (d): pause the verifier-content line,
escalate.

## S3. Independence treatment: one judge family, one gold source, one new control

**Is GPT-5.6 + GPT-5.5 a valid two-judge panel?** No. The §4 concordance
machinery buys validity from INDEPENDENT raters: two humans err mostly
independently, so concordance certifies labels. Same-vendor,
adjacent-generation models share training corpora, preference tuning, and
style priors; their concordance is expected under correlation and certifies
nothing [STIPULATED, standard measurement reasoning; the run MEASURES their
raw agreement rather than assuming its value]. Treating them as a panel
would launder one family's bias through a two-vote formality — the precise
way the endorsement statistic A could be inflated "independent of real
kernel content". Honest treatment, all pre-registered in the record:

1. **Sole gold source.** A_1p is computed from judge-1p (GPT-5.6) ALONE:
   escapes count as disagreement, no-labels leave the denominator (gated).
   No concordance step touches the primary.
2. **Judge-2 kept, demoted.** Its in-flight run is f2b-transfer's instrument
   and is reused here read-only (same 360 blind bytes — reuse costs nothing
   and re-running a second GPT-5.5 round would create a second adjudication
   of the same items for no validity gain). Roles: (a) STABILITY GATE, fail
   direction only — raw agreement < 0.80 ⇒ INSTRUMENT-INVALID (if one family
   cannot even agree with itself, single-judge labels are noise); its pass
   direction validates nothing and is envelope-flagged; (b) reported-only
   diagnostics: raw agreement (the correlation diagnostic), A_j2, and the
   concordant-panel analog A_panel (FORM-comparable to the human pipeline's
   A, carried for the eventual side-by-side).
3. **No judge-3.** Discordant pairs stay unresolved-proxy (diagnostic). The
   maintainer tie-break instrument is deliberately left uncontaminated (no
   item exposure) for the human f2b-transfer round.
4. **The different independence check — the deranged-gloss probe.** 60
   def-match probes (`data/d-adj-t-llmproxy/deranged-probe.jsonl`, built
   pre-freeze, seed-pinned, byte-verified: gold slot holds a Sattolo-cycle
   donor gloss, distractors and question untouched, all options distinct).
   Correct answer is NONE by construction, so the probe measures the judge's
   false-endorsement propensity on NSM-SHAPED text whose content is provably
   wrong — the exact channel (kernel-tradition familiarity, ASM-0021) that
   would fabricate a proxy-PASS under H-CIRC — and simultaneously verifies
   the escape hatch actually fires in an LLM. Gate: point rate ≥ 0.30 or
   probe coverage < 54/60 ⇒ INSTRUMENT-INVALID. Residual disclosed: a
   swapped-in gloss may rarely genuinely fit (order ~1%, the design.md §4.7
   "rabbit ← tree" class); the 0.30 bar sits far above that floor.
   Probe items never enter labels or A_1p.

**How A is computed and flagged:** A_1p = n_agree_j1p / n_labelled_j1p,
one-sided 95% Wilson LB, bar 0.70 — the same FORM as kill (d) so the proxy
rehearses the real gate, with envelope clauses (1), (2) and (5) binding every
citation to the correlated-family, familiarity-channel, and
asymmetric-reading caveats.

## S4. Mechanism: blind §4 rendering, judge-1's pinned shuffle, verified invocation

Everything the judge sees is identical to the frozen protocol's judge-2
mechanics: the pinned prompt template (ONE line differs from judge-2's —
the panel-position pseudonym is removed; every other byte identical, so all
judges answer under the same S1–S7 standards), the same per-item blind
rendering (question + options only; no gloss, no ids, no provenance, no
"kernel", no panel), the same output-schema enum, the same E5 context
controls (empty out-of-repo workdir, --ignore-user-config, memories and web
search force-disabled, read-only sandbox, zero-tool-use tripwire,
--ephemeral), the same first-valid-answer-final no-selection rule, ≤3
content attempts, no-label discipline (never mapped to the escape). Real
items run in the judge-1 ROLE's frozen shuffle order
`dadjt/1|judge-1|20260710` (§4.2; stateless per-item calls make order
science-neutral; the role's order is honoured and recorded; the identity is
recorded as pseudonym judge-1p, never judge-1). Probes run after, in
`dadjt/1|judge-1p-probe|20260711` order. Full spec:
`data/d-adj-t-llmproxy/judge-1p-invocation.md` (sha-pinned in the record).

PREMISE: the pinned invocation is EXECUTABLE — `npx -y @openai/codex@0.144.1
exec -m gpt-5.6-sol -c model_reasoning_effort="low" …` with the full
hardened flag set returned exit 0 and a schema-constrained answer with zero
tool events; the global codex-cli 0.142.5 REJECTS gpt-5.6 (HTTP 400, no
catalog entry), and under 0.144.1 the catalog lists gpt-5.6-sol with efforts
low…ultra, default low [MEASURED: designer capability check 2026-07-09,
single trivial call; artifacts in the session scratchpad `gpt56-check/`].
Operational constraint carried into the record: the GLOBAL codex install
stays at 0.142.5 until the in-flight judge-2 run completes; judge-1p uses
the npx-pinned 0.144.1 in isolation (verified to leave the global binary
untouched). Temperature-0 is discharged exactly as judge-2's spec §4
(reasoning models expose no temperature; pinned bytes + effort low — also
the catalog default for this model — + enum output + first-valid-final).

## S5. Governance path (exact, in order; Opus-runner work)

Nothing below touches f2b-transfer's record, log, or d-adj-t placeholder.

1. Let the in-flight judge-2 run COMPLETE under its own spec; commit
   `data/d-adj-t/judge-2-responses.jsonl` per that spec (it remains
   f2b-transfer's instrument; this record only reads it).
2. Post the stand-in decision + this note's path and sha to the coordination
   issue (RT-15) and record the maintainer's ack line (the stand-in was
   maintainer-requested; the record's budget.maintainer_signoff cites it).
3. `prereg-freeze --experiment f2b-transfer-llmproxy` (record is DRAFT and
   passes `--dry-run` as committed); post the frozen_sha256 (RT-15).
4. Ops amendment: fill `pins.artifact_hashes["data/d-adj-t/judge-2-responses.jsonl"]`
   with the committed file's sha256 (declared PINNED-AT-INPUTS placeholder).
5. Run judge-1p per the pinned spec: preflight (2 calibration items,
   first-attempt-valid + expected) → 360 real items → 60 probes. Abort
   bounds: >18 real no-labels or >6 probe no-labels.
6. Assemble `data/d-adj-t-llmproxy/` (judge-1p-responses.jsonl,
   judge-1p-probe-responses.jsonl, labels-proxy.jsonl, summary.json with the
   analysis-input integers + sourcing disclosure), RT-14 scrub, `corpus-pin`,
   ops amendment fills the `d-adj-t-llmproxy` corpus placeholder.
7. `log-append` the single stage-1 final-phase record (phase:"final",
   arm "adjudication-instrument", the summary integers as raw metrics);
   `verdict-gen` (pure function of the frozen SAP + chained log).
8. Cross-vendor audit via the standing Codex/GPT-5.5 auditor, with the
   FAMILY-OVERLAP DISCLOSURE required in the audit note: the auditor shares
   a model family with both judges; the audit certifies mechanical integrity
   (recomputation from pinned bytes, log-chain, gate arithmetic) and does
   NOT validate judge quality — no audit of this record may be cited as
   evidence that the LLM judge is unbiased.
9. Fable interpretive assessment; beads update; targeted `git add` of the
   paths in §S7 + commit + push (central custody: the designer session
   committed nothing).

If the maintainer instead insists the stand-in replace f2b-transfer's own
judge-1: that path requires (a) a correction record acknowledging it is NOT
pre-data (judge-2 data exists), (b) reset→refreeze of f2b-transfer with the
weakened envelope, and (c) accepting that the human round then needs a new
id. This note recommends AGAINST it for the S1 reasons; the fresh-id design
delivers the same feasibility read without those costs.

## S6. Pre-freeze skeptic attack memo (freeze is blocked without this)

- **Oracle-leakage class (does the eval's gold coincide with the mechanism's
  accept test?).** The judged items' membership gold IS kernel-derived — that
  is inherited from f2b-transfer's design and is exactly what endorsement
  measures (does an outsider agree with the kernel's own labels?). The
  stand-in's new leak surface is the judge KNOWING the kernel: closed by E5
  context control for the instance (memories/web disabled, empty workdir,
  blind rendering) and BOUNDED-NOT-CLOSED for the tradition (NSM in training
  data) — named in envelope clause (2), probed by the deranged-gloss gate,
  registered as ASM-0021. No claim of full closure is made anywhere.
- **Endpoint gameability.** A_1p is a deterministic count over pinned items
  with a pinned bar; the judge cannot be re-rolled (first-valid-final), items
  cannot be re-drawn (single build, sha-pinned), no-labels cannot be mapped
  to escapes (spec §6), and the analysis is a pure function with a green
  selftest. The one discretionary surface — WHICH judge fills the role — is
  pinned by model slug + CLI version + template sha before freeze.
- **Baseline asymmetry.** No host arms exist; the mandatory-control slot is
  filled by the probe (content-scramble at the judge level) and the
  single-family stability gate. The kernel-as-text/Law-2 obligations are
  explicitly out of scope (no model-lift claim is possible from this record;
  the envelope forbids reading one in).
- **Undecidable/underpowered gates.** Endorsement gate powered (expected
  0.85 → Wilson LB ≈ 0.816 at n=360; ≈ 0.813 at the 300 floor — both > 0.70);
  agreement gate powered (expected 0.92 → LB ≈ 0.896 > 0.80); probe gate is
  a point rule at n≥54 with the bar 0.30 far from both the expected escape
  behaviour (~0.05–0.10) and the ~1% construction residual. All three
  verified by `prereg-freeze --dry-run`.
- **Correlated-judges laundering.** The design's central threat, treated by
  construction: no concordance in the primary, agreement gate one-directional,
  panel analog reported-only, envelope clauses (1) and (5). What this design
  CANNOT do — and says so — is convert LLM endorsement into human-anchored
  external gold; that conversion is f2b-transfer's job.
- **Contamination of the future human round.** The human judge-1 must never
  see this record's outputs; the recruitment package's kernel-naivety
  self-certification already covers "never read kernel records"; judge-3
  exposure is zero by design (no tie-breaks here). The item bytes are
  unchanged, so the human round's blinding is exactly as frozen.
- **Cost/right-size.** 422 sequential low-effort calls ≈ the judge-2 run's
  measured per-item cost envelope [STIPULATED estimate, anchor: the
  in-flight run's progress log ~4 s/item]; usd_cap 10, zero GPU. The
  experiment can FAIL at ~$0 GPU and ~1 judge-day of wall clock.

## S7. Files of this design (created by the designer session; committed by Opus)

- `registry/experiments/f2b-transfer-llmproxy.json` (DRAFT, dry-run-validated)
- `poc/f2b-transfer/llmproxy-design.md` (this note; prereg_doc)
- `data/d-adj-t-llmproxy/judge-1p-prompt-template.txt` (1-line diff from judge-2's; sha-pinned)
- `data/d-adj-t-llmproxy/judge-1p-invocation.md` (pinned, verified invocation)
- `data/d-adj-t-llmproxy/deranged-probe.jsonl` + `deranged-probe-manifest.json` (built, byte-verified)
- `data/d-adj-t-llmproxy/README.md`
- `poc/f2b-transfer/llmproxy/build-deranged-probe.py` (deterministic; d-qa-t pin fail-closed)
- `analysis/f2b_transfer_llmproxy.py` (pure function; selftest green)
- `registry/assumptions.jsonl` (+ASM-0021 EXTRAPOLATION, +ASM-0022 STIPULATED)
