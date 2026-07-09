# N-G — The assumption/claim register and the literature-backing gate

**Kernel of Truth programme — honesty-machinery extension, node N-G.**
Author: Kern (Fable design agent, writer-1). Date: 2026-07-09.
Status: **DESIGN + implementation; governance wirings RULED ON.** The register file
(`registry/assumptions.jsonl`) and the standalone lint
(`tools/registry/claims-check.py`) exist as of this document. The §6 wirings were
maintainer-gated (P2 §7 item 3) and the maintainer decided them on 2026-07-09:
items 1 (claims-check in the pre-push run-all set) and 4 (full-scope coverage
footer) are **ENABLED**; item 2 is **reframed to PAUSE-and-reassess** (non-fatal;
§6 states the governing philosophy); item 3 stays **deferred** pending the lit-KB
(Pillar C). Binding constraints: `docs/kernel-design-directives.md` §§3, 4, 6;
the maintainer's epistemic-discipline directive (2026-07-08): *every load-bearing
claim carries a status tag; a claim is treated as established only when MEASURED or
LIT-BACKED; an extrapolation is never stated as fact and never used as a premise for
a decision.*

**The failure this machinery exists to prevent (the motivating incident).** The m0b
census measured coverage_fraction **0.3542** — a deterministic count on **one pinned
corpus** (the TinyStories task family) at **one rung** (molecules-v0) of **one
incomplete kernel instance** (kernel-v0 + molecules-v0 as they existed 2026-07-08).
The verdict object's own extrapolation envelope says, verbatim, that the number
*"extrapolates to NO other corpus or rung"* — and yet programme narration drifted
into treating 0.3542 as the kernel's "natural coverage", a general property. That is
a MEASURED claim silently promoted into an EXTRAPOLATION stated as fact. The register
makes that promotion mechanically visible and lintable; the worked correction is
§7 and `registry/assumptions.jsonl` entries ASM-0001/ASM-0002.

---

## 1. The four epistemic tags

Every load-bearing claim in a programme document, candidate record, assessment, or
report carries exactly one tag. "Load-bearing" = a decision, design choice, prereg
premise, or paper claim would change if the claim were false.

| Tag | Definition | How it is backed (mandatory) | May premise a decision? |
|---|---|---|---|
| **MEASURED** | The claim restates a quantity or outcome that was actually measured under this programme's rails, within the scope (corpus, rung, kernel state, model, seeds) it was measured on — never wider. | A verdict-object reference: `registry/verdicts/<id>.json` (+ its sha256 or the analysis-output sha), or for tooling-level measurements the exact command + committed output. The claim text must carry the measured scope. | **Yes** — within its measured scope only. Citing a MEASURED number outside its extrapolation envelope re-classifies the statement as EXTRAPOLATION. |
| **LIT-BACKED** | The claim restates a published result, verified at source (not from a KB record alone — N-C §0: KB records are recall infrastructure, not evidence). | A `kot-lit/1` record id once Pillar C lands, or a paper id + year (arXiv:XXXX.XXXXX, DOI). Replication status stated where known ([established] / [claimed — unreplicated], the L3-report convention). | **Yes** — with the paper's own scope and the directives-§6 scale caveats. |
| **STIPULATED** | An explicit assumption the programme chooses to proceed on — not evidenced, but named, owned, and revisitable (e.g. "TinyStories content-word mass is an adequate Tier-0 proxy for eval-relevant content"). | A register entry with an **owner** (pseudonym or `maintainer`) + a **rationale** + the condition under which it must be revisited. | **Only as a named, registered assumption** — the decision record must cite the ASM-id, so the stipulation is visible in the decision's premise list and falls when the stipulation falls. It never counts as *established*. |
| **EXTRAPOLATION** | A projection beyond measured/published scope (other corpora, rungs, scales, kernel states). Directives §6 licenses extrapolation only as an explicit, literature-anchored *trend statement* with uncertainty attached. | A register entry flagged `load_bearing: false` with a **resolution_path**: the measurement or literature search that would convert it. | **NEVER.** A decision/premise citing an EXTRAPOLATION is a lint violation (`ERR_ASM_EXTRAPOLATION_PREMISE`). It may motivate *queueing* an experiment; it may not decide one. |

**The RULE (the gate this node adds).** A decision, prereg premise, or paper claim
may cite only **MEASURED** or **LIT-BACKED** claims as established, plus explicitly
registered **STIPULATED** assumptions listed as such. A load-bearing
**EXTRAPOLATION** is a contradiction in terms: either resolve it (measure it / find
the paper) or demote the decision to a fork (directives §4 — register the
uncertainty and let an experiment decide).

---

## 2. The register: `registry/assumptions.jsonl`

Append-only JSONL, same discipline as everything else in `registry/` (a claim's
history is corrections appended, never lines edited; for a given `id` the last line
is current). One line per registered claim/assumption:

```jsonc
{
  "id": "ASM-0001",             // ASM-\d{4}, assigned sequentially, never reused
  "claim": "…",                 // the claim text, scope included
  "tag": "MEASURED",            // MEASURED | LIT-BACKED | STIPULATED | EXTRAPOLATION
  "backing_ref": "…",           // per the §1 backing column ("" only for open
                                //   EXTRAPOLATION / STIPULATED pending)
  "load_bearing": true,         // does any decision/design/paper claim rest on it?
  "status": "open",             // open | resolved
  "owner": "writer-1",          // pseudonym <role>-<n> (kot_common.PSEUDONYM_RE)
                                //   or the literal "maintainer" — never an account
  "date": "2026-07-09",
  // conditional fields:
  "rationale": "…",             // REQUIRED when tag=STIPULATED
  "resolution_path": "…",       // REQUIRED when tag=EXTRAPOLATION: the measurement
                                //   or lit-search that converts it
  "notes": "…"                  // optional; corrections cite what they correct
}
```

Lifecycle: an EXTRAPOLATION or STIPULATED entry is **resolved** by appending a new
line with the same `id`, the upgraded tag (MEASURED/LIT-BACKED), the backing ref,
and `status: "resolved"` — or by appending a line recording that the projection was
falsified (tag stays, `status: "resolved"`, notes say "falsified by <verdict>").
Account-string discipline (RT-14) applies: register lines are scanned with the same
pattern list as registry records.

### How load-bearing claims are IDENTIFIED (the honest limits)

A lint cannot find unmarked load-bearing prose — identification is a procedure plus
a convention, and the lint enforces the convention:

1. **Marker convention (machine-checkable).** In any document under the convention,
   a load-bearing statement is written on a line carrying one of the markers
   PREMISE / DECISION / LOAD-BEARING (each followed by a colon), with its tag inline —
   e.g. a premise line reading *"verifier lift on covered D-QA items is large at k=4
   [MEASURED: registry/verdicts/f2.json]"*. The lint (§3) rejects a marker line with
   no tag, an EXTRAPOLATION tag, or a tag without backing. (This spec deliberately
   never writes a bare marker-plus-colon itself: the lint has no code-span escape, by
   design — fail closed beats a quoting convention that could hide a real premise.)
2. **Candidate records (structural).** The N-B candidate template's `claim.md`
   gains a mandatory **Assumptions** section (see research-engine.md §1.3 step 1 as
   amended): every premise enumerated as a marker line, each citing a tag or an
   ASM-id. `prereg-freeze` integration (§6 item 2, as decided): a citation that
   resolves to an open EXTRAPOLATION emits a non-fatal PAUSE flag — the
   conclusion-side lints stay hard; the experiment is never blocked.
3. **The Skeptic sweep (adversarial).** Step-6 pre-freeze attack memos gain a fixed
   checklist item: *sweep the draft for unmarked load-bearing claims* — the human/
   agent half of identification, mirroring how RT-2/RT-3 classes are caught.
4. **Post-verdict resolution (closing the loop).** The `kot-assess/1` record gains
   `assumptions_resolved[]` (research-engine.md §2.1 as amended): every EXTRAPOLATION
   or STIPULATED entry the candidate relied on is either resolved by the verdict or
   explicitly re-registered as still open — an assessment that leaves a relied-on
   EXTRAPOLATION untouched is incomplete.

---

## 3. The lint: `tools/registry/claims-check.py` (implemented)

Standalone, stdlib-only, fail-closed with named `ERR_ASM_*` codes; same conventions
as the rest of `tools/registry/`. Since 2026-07-09 it is also invoked by
`registry-check`'s run-all set (§6 item 1) — the standalone CLI remains the single
implementation. Markdown hanging-indent continuations of a bullet are joined into
one logical line before the marker checks, so a wrapped premise whose tag lands on
the continuation line is read whole; unindented wrapped prose is never joined
(fail closed).

```
python3 tools/registry/claims-check.py [--root <repo>] [--register <path>] [paths…]
```

- With no paths: validates `registry/assumptions.jsonl` (if present).
- With paths: additionally scans each `.md`/`.txt` for the marker convention, and
  each `.json`/`.jsonl` record for an `assumptions` block.

Checks (exit 1 on any violation):

| Code | Fires when |
|---|---|
| `ERR_ASM_SCHEMA` | register line missing a required field, bad id/tag/status, non-pseudonym owner |
| `ERR_ASM_BACKING` | MEASURED without a verdict/experiment/hash reference; LIT-BACKED without a paper id/year; STIPULATED without `rationale`; EXTRAPOLATION without `resolution_path` |
| `ERR_ASM_LOADBEARING_EXTRAPOLATION` | a register line (or record `assumptions[]` entry) with `tag: EXTRAPOLATION` and `load_bearing: true` — the RULE, mechanised |
| `ERR_ASM_UNTAGGED_PREMISE` | a marker line (PREMISE / DECISION / LOAD-BEARING + colon) with no epistemic tag |
| `ERR_ASM_EXTRAPOLATION_PREMISE` | such a line tagged `[EXTRAPOLATION: …]` |
| `ERR_ASM_UNREGISTERED_STIPULATION` | a premise line tagged `[STIPULATED: …]` that does not cite an ASM-id present in the register |
| `ERR_ASM_UNKNOWN_ID` | any cited ASM-id absent from the register |
| `ERR_P2_ACCOUNT_IN_RECORD` | account strings in register lines (RT-14, reused from `kot_common`) |

Fixtures: `TestClaimsCheck` in `tools/registry/test_fixtures.py` pins the exit codes
and every `ERR_ASM_*` path against a throwaway root.

---

## 4. Integration into the research engine (Pillar B)

Enacted as edits to `docs/next/research-engine.md` (design-stage, so editable):

1. **Candidate template** (§1.2/§1.3 step 1): `claim.md` gains a mandatory
   **Assumptions** heading — every load-bearing premise as a marker line with tag or
   ASM-id; `claims-check` runs over `candidates/<id>/` as part of the step-6 skeptic
   gate; at freeze, `prereg-freeze` runs the §6-item-2 pause scan (non-fatal).
2. **Assessment record** (§2.1): `kot-assess/1` gains `assumptions_resolved[]`;
   the assessment is incomplete while any EXTRAPOLATION the candidate relied on is
   unaddressed.
3. **Known-results ledger** (§2.6): resolutions are ledger entries
   (`kind: "assumption-resolution"`), so a resolved extrapolation is institutional
   memory, and `claim.md` linting against the ledger catches re-proposals built on
   projections already falsified.
4. **Engine-fixed law 9** (§1.4): the RULE itself, stated as engine physics.

---

## 5. Relationship to existing honesty machinery (no duplication)

- The **extrapolation envelope** (P2, verbatim in every verdict/report) already
  scopes MEASURED claims at the *verdict* surface. The register extends the same
  discipline to *prose and decisions* — the m0b incident happened in narration, not
  in the verdict object, which was correct throughout.
- `registry-check --citations`-style scanning (the assessment rule "interprets, never
  upgrades") is the same instinct; `claims-check` gives it a claim-level grammar.
- The KB honesty boundary (N-C §0: KB records ≠ evidence) is the LIT-BACKED backing
  rule seen from the KB side.

---

## 6. Governance wirings — maintainer decision record (2026-07-09)

These four items were proposed maintainer-gated; the maintainer ruled on each on
2026-07-09. The governing philosophy behind item 2 is binding programme-wide:

> **Stop false CONCLUSIONS, not experiments.** The hard, fail-closed gates guard
> what the programme *asserts* — verdicts, paper claims, premise/decision lines —
> never whether an experiment may run. An open EXTRAPOLATION is a perfectly good
> reason to *run* an experiment; it is never a licensed *premise* for concluding
> anything, and no conclusion may exceed its MEASURED / LIT-BACKED backing.

1. **ENABLED (2026-07-09).** `claims-check` is in `registry-check`'s run-all set,
   and the repo pre-push hook (`.beads/hooks/pre-push`, via `core.hooksPath`) runs
   `registry-check` run-all: every push lints `registry/assumptions.jsonl` +
   `docs/**/*.md`, fail-closed (`registry-check.py --claims`; wrapped markdown
   bullets are joined into logical lines so a hanging-indent tag counts, while
   unindented prose is never joined — fail closed). Fixtures:
   `TestRegistryCheckClaims`, `TestClaimsCheck.test_wrapped_bullet_premise_joined`.
2. **REFRAMED to PAUSE-and-reassess (2026-07-09) — NOT a freeze refusal.**
   `prereg-freeze` does not hard-block a DRAFT record whose record bytes or pinned
   prereg doc cite an ASM-id that currently resolves to an **open EXTRAPOLATION**.
   The freeze proceeds, and the tool emits a **non-fatal PAUSE flag**: a
   `kot-pause/1` line appended to `registry/pause-flags.jsonl` (plus the same flag
   on stdout and a `pause_flags` field in the freeze summary), carrying a
   `backlog-reprioritise` signal so the research-engine assess→next-step loop
   decides — resolve the cited extrapolation first (run its `resolution_path`), or
   prioritise another candidate. The HARD block stays on the CONCLUSION side:
   `claims-check` refuses an EXTRAPOLATION-tagged premise/decision line
   (`ERR_ASM_EXTRAPOLATION_PREMISE`) and a load-bearing EXTRAPOLATION register
   entry (`ERR_ASM_LOADBEARING_EXTRAPOLATION`), and `verdict-gen` remains a pure
   function of the frozen SAP + chained log — so a false conclusion cannot ship,
   while the experiment that would *test* the projection is never blocked.
   Fixtures: `TestPreregPause`.
3. **DEFERRED pending the lit-KB (Pillar C).** `kb-check` enforcing the LIT-BACKED
   backing rule on `kot-lit/1` records cited as backing — enable when Pillar C
   lands (tracked as follow-up work; N-C §0 remains the honesty boundary meanwhile).
4. **ENABLED (2026-07-09).** `report-gen`'s coverage-disclosure footer now states
   the FULL measured scope from machine inputs only — the census source experiment
   + its freeze timestamp + its pinned census inputs (corpus and kernel-instance
   pins + encoder pin, from the source's frozen record) + the no-extrapolation
   sentence ("corpus-indexed, rung-indexed, kernel-state-indexed … extrapolates to
   NO other corpus, rung, or kernel state; NOT a general ('natural') coverage
   property") — matching the m0b verdict envelope + ASM-0001, so the footer can
   never again read as "natural coverage". Affected auto-reports regenerated
   (m0b, f2, g6, g7; footer-only diffs). Fixture:
   `TestReportGen.test_report_full_scope_coverage_footer`.

---

## 7. Worked entry — the m0b correction (first register content)

**The wrong statement (as narrated):** "the kernel's natural coverage is ~0.35."
**Why it is wrong:** 0.3542 is MEASURED — but the measurement is triply indexed:
(i) corpus = the pinned TinyStories task family (1,709,765 tokens, pin b6bcc9f6);
(ii) rung = molecules-v0 (the kernel-v0 rung alone measures 0.2210);
(iii) kernel state = the **incomplete** kernel-v0 + molecules-v0 instance of
2026-07-08 (coverage is re-measured as the kernel grows — the coverage-growth curve
is a planned deliverable, P7 RT-11/§10). "Natural coverage" strips all three indices
and asserts a general property no experiment has measured. The m0b verdict's own
envelope forbids it verbatim: *"The measured coverage number extrapolates to NO
other corpus or rung."* The F2 external-slice result (zero item flips on D-EXT)
is a live warning of exactly this trap: in-house-slice numbers do not transfer.

**Register entries filed** (`registry/assumptions.jsonl`):

- **ASM-0001** (MEASURED, load-bearing, resolved): the correctly-scoped coverage
  claim, backed by `registry/verdicts/m0b.json`.
- **ASM-0002** (EXTRAPOLATION, non-load-bearing, open): "a ~0.35-level coverage
  would hold on other corpora" — resolution path: re-run the m0b census machinery on
  each new corpus before any covered-slice design cites a coverage number there.
- **ASM-0003** (STIPULATED, load-bearing, open, owner: maintainer): the Tier-0
  gate's premise that TinyStories content-word mass is an adequate proxy for
  eval-relevant content at the R0/R1 rungs (the GNG-0 ratification default X=0.20
  rides on it).

**Doc corrections applied this turn:** `docs/next/arch-survey.md` §1.2 (M4 row) and
§1.3, and `docs/next/00-programme-2-overview.md` §0 — each place that summarised m0b
as unqualified "coverage" now carries the corpus/rung/instance scope. No generated
report was edited (they are verdict-derived and already correct).

---

## 8. Honesty footer

Adoption baseline (MEASURED, on-box grep census 2026-07-09, ~$0: marker-pattern and
inline-tag counts over `docs/next/`, `docs/research-plan/`, `reports/`, `notes/`
*.md): before this node landed, **zero** marker lines and **zero** inline epistemic
tags existed anywhere in the four trees (docs/next now carries the first, added by
this node); the `reports/` tree uses the older per-citation convention
([established]/[claimed]/[search]/[memory]), which maps onto LIT-BACKED sub-statuses
and is left in place. Migration of existing docs is incremental: the convention binds
new candidate records and decisions first (research-engine.md §1.3 step 1), not a
retro-tagging sweep.

This document creates no registry *experiment* entries, freezes nothing, and amends
nothing frozen. `registry/assumptions.jsonl` is a new, additive register; the lint is
a new, additive tool; every integration that changes fail-closed behaviour of
existing machinery is recorded in §6 with its maintainer decision of 2026-07-09
(items 1 + 4 enabled; item 2 enacted as a non-fatal pause, which blocks nothing;
item 3 deferred pending Pillar C). The census numbers
quoted in §7 restate `registry/verdicts/m0b.json` (audit CONFIRMED) verbatim-in-
substance and add no new empirical claim.

---

## 9. Role-authoring note — the HONESTY-GUARD tail (convention, 2026-07-09)

Every Fable role file under `.claude/agents/` ends with a canonical **HONESTY-GUARD**
block distilled from this document (the four tags, the RULE, the marker convention +
lint + register, the conclusions-not-experiments scope of the block, verdict-time
resolution via `assumptions_resolved[]`, and the m0b worked caution). Authoring rules
for any NEW role (and any future guard revision):

1. **Append at the tail, never earlier.** File shape is: frontmatter → the shared
   programme-context block VERBATIM (byte-identical to
   `.claude/context/programme-context.md`, sha256 prefix `e1005387`) → the
   role-specific body → the HONESTY-GUARD tail. The leading block and existing body
   are never touched when the guard changes — tail-append preserves the prompt-cache
   prefix across all roles.
2. **Byte-identical across roles.** The guard is one canonical text (current sha256
   `44731dd21791eda093874a1c7fe6df9ac33ae6be2df5a2c70d96d11d22d39cc7`; reference copy =
   the tail block of `.claude/agents/analyst.md`, from the `# HONESTY-GUARD` heading and
   its preceding `---` separator to EOF). Revising it means re-appending the same new
   bytes to EVERY role file in one change.
3. **Lint-clean by construction.** The guard (and any role prose) never writes a bare
   marker-plus-colon; its one worked example line carries a valid `[MEASURED: …]`
   backing ref, so `claims-check.py` over `.claude/agents/` passes.
4. `architecture-advisor.md` predates the shared block (no `e1005387` prefix) but
   carries the same guard tail as of 2026-07-09.

---

*Cross-references:* `docs/kernel-design-directives.md` §§3/4/6 (binding);
`docs/next/research-engine.md` (Pillar B, as amended §4);
`docs/next/literature-kb.md` §0 (KB honesty boundary);
`reports/auto/m0b/verdict-m0b.md` (the envelope, verbatim);
`tools/registry/claims-check.py` (the lint); `registry/assumptions.jsonl` (the register).
