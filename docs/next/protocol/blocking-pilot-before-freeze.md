# Protocol: mandatory blocking instrument pilot before prereg-freeze

**Role: Fable GOVERNANCE-DESIGN agent, 2026-07-12. This document specifies a
programme-wide process gate — the blocking instrument pilot — commissioned by
`docs/next/analysis/correctness-track-instrument-assessment.md` §4's
meta-recommendation ("adopt the mandatory blocking instrument pilot as prereg
protocol now") and item 10 of its ranked list. It is a process-hardening
design, not an experiment: nothing here states or implies any feasibility
conclusion, grades any run, or alters any frozen object. The prereg-freeze
wiring in §5 is a PROPOSED patch for the coordinator to review and apply;
this build touches neither `tools/registry/prereg-freeze.py` nor
`registry/schema/*` nor `registry/assumptions.jsonl`. Assumption rows
PROPOSED-ASM-1830..1836 are emitted alongside
(`docs/next/protocol/asm-blocking-pilot-1830-1836.json`) for central
registration by the coordinator.**

Exemplar throughout: the rules-2 instrument pilot
(`poc/rules-2/instr_pilot.py`, gates IP-1..IP-4,
PROPOSED-ASM-1814..1819) — the first instance of this gate, built for one
experiment. This document generalises it to every freeze.

Epistemic tags follow the assessment's convention: **[MEASURED]** read from
committed bytes this tick; **[DERIVED]** follows from measured bytes by
stated code-reading; **[COUNTERFACTUAL]** a what-if under stated
assumptions, never evidence; **[STIPULATED]** a protocol rule this document
proposes.

---

## 0. Why (the evidence this rule answers)

Five instrument events, one shared process gap — **no gate channel was
exercised at the operating point before freeze** [MEASURED, assessment §0.1]:

| event | verdict | failing interface |
|---|---|---|
| rules-1 | VOID | elicitation: direction-unstated cue + menu adjacency; **all arms 0.000, including the oracle arm** |
| rules-1-b | superseded pre-final-phase | task form: relation-word surface form-dead for the unaided host (pilot A5 **0/24**) |
| rules-1-c | INSTRUMENT-INVALID | verifier engagement: URN/word type mismatch ⇒ unconditional abstention; **every A3 row attempts=1; A3 ≡ c1** on all 2,574 cells — atop a design-layer vacuity (2-option surface: a non-leaking verifier is necessarily vacuous) |
| g2-import v2 pilot #1 | pilot machinery PASS, near-miss | AC1 **0.6909** vs gate 0.65, with the pair's independence ceiling within run-to-run noise (2 items) of both the gate and the measurement |
| g2-import v2 pilot #2 | pilot-stop (gate FAIL, full run never launched) | AC1 0.6222 < 0.65; **κ = 0.0000 exactly** — measured AC1 equal to its own independence ceiling |

The g2 line is the existence proof in both directions: its Stage-P pilot
discipline caught a boundary-sitting instrument for ~$1.4 instead of a $6
campaign (the machinery *working*), and its pilot #1 shows what a generic
gate must additionally do — flag a statistic that passes with a margin
smaller than its own replicate noise, rather than passing it silently.
The rules lineage shows the cost of not having the gate at all: three
freezes, three campaigns, zero valid readings. [MEASURED/DERIVED]

The assessment's diagnosis, adopted here as the design premise: the
programme's instruments succeed when the measurement channel is
deterministic or externally adjudicated, and fail at the first interface
that was argued rather than exercised. At small scale the operating point
sits near multiple degeneracy boundaries simultaneously (form-death,
verifier vacuity, prevalence compression), so design-time argument keeps
missing what a $1–2 pilot catches mechanically. [assessment §1.1]

---

## 1. THE RULE [STIPULATED — PROPOSED-ASM-1830]

> **No experiment may prereg-freeze until a recorded blocking instrument
> pilot has PASSED at the operating point.**

Unpacked, each clause load-bearing:

- **No experiment** — programme-wide, every registry record, both kot-reg/1
  and kot-reg/2, from the adoption date forward. Not a rules-lane special.
  Already-frozen records are untouched (the gate is freeze-time only).
- **recorded** — the pilot's result is a pinned artifact (§3) whose sha256
  the DRAFT record carries in `pins.blocking_pilot` before the freeze is
  attempted. An unrecorded pilot ("we ran it, it was fine") does not exist.
- **blocking** — a PILOT-FAIL blocks the freeze pending redesign or an
  explicit coordinator override record (§4). The block is on the FREEZE
  (i.e. on the spend), never on pilot-scale exploration itself.
- **instrument pilot** — the REAL instrument (real host/judges, real
  surface, pinned harness) on a tiny deterministic slice, run under a
  fail-closed cost cap. Verdict semantics are instrument-validity ONLY:
  pilot rows are never campaign evidence, never an effect-size preview,
  and may not be quoted for or against any registered hypothesis
  (the ASM-1819 fence, generalised).
- **PASSED** — verdict `PILOT-PASS` or `PILOT-PASS-WITH-FLAGS` with every
  required check (§2) mechanically true. Flags are enumerated and travel
  with the record; they never silently convert to passes.
- **at the operating point** — the pilot exercises the exact pinned
  configuration the campaign will run: same model revisions, same prompt
  surface (sha-pinned), same item construction, same gate thresholds.
  A pilot at different pins is STALE and does not satisfy the rule (§5).
  "Tested" means exercised, not argued — the rules-1-c lesson verbatim.

Reconciliation with the governing philosophy ("stop false conclusions, not
experiments", assumption-register §6 item 2, maintainer decision
2026-07-09): this gate does not stop an experiment — an invalid instrument
cannot run the experiment in any epistemically meaningful sense; it can
only burn the budget and produce rows no verdict may consume. The pilot
gate blocks *waste*, is itself cheap (capped ~$2) and fast (hours), and
carries an explicit override escape (§4) so coordinator agency is
preserved. Open-EXTRAPOLATION premises remain PAUSE-not-refuse exactly as
today; instrument validity is a different axis and is fail-closed.

---

## 2. What the pilot must verify, generically [STIPULATED — PROPOSED-ASM-1831]

Five checks, PC-1..PC-5. Each is **mechanical** (a predicate over emitted
rows against pre-declared constants — no model judgement, no eyeballing),
**fail-closed** (absence of evidence = FAIL), and **exercised at the
operating point** (computed from real pilot rows, never argued from
design). Thresholds are pre-declared constants in the pilot runner;
changing any of them after a coordinator has read a pilot result requires
a fresh pilot (the ASM-1815 discipline).

Per-experiment operationalisation is the experiment designer's job; the
rules-2 pilot column shows the exemplar instantiation.

| # | check | generic predicate | rules-2 exemplar |
|---|---|---|---|
| **PC-1** | **No degenerate arm** | no arm is floored or saturated by construction: every measurement arm's pilot score clears an exact-binomial (or equivalent) bound above its structural floor (chance, abstention) AND the strongest arm sits below a pre-declared saturation ceiling, so the registered contrast has room to exist in both directions. Refusal/abstention rate bounded on every arm (the channel is answers, not abstention). | IP-1 (a)(b)(d): acc_B0 ≤ 0.90; acc_B2p ≥ exact one-sided binomial 95% bound vs chance 0.5; covered-refusal ≤ 0.5 both arms |
| **PC-2** | **Treatment-vs-control separation is non-vacuous** | the treatment channel demonstrably *moves* relative to its baseline at pilot scale by at least a pre-declared minimum gap — equivalently, the treatment arm is not row-identical (or statistically indistinguishable by construction) to a control arm. An arm that equals its control on every cell is the rules-1-c vacuity. | IP-1 (c): acc_B2p − acc_B0 ≥ 0.05 |
| **PC-3** | **Controls are non-degenerate** | every mandatory control arm lands where its construction predicts: it neither collapses to abstention nor collapses onto the treatment; and every *gating statistic* clears its own degeneracy floor (chance rate, independence ceiling for agreement statistics) with a pre-declared margin **greater than the statistic's observed replicate noise at pilot n**. A gate whose margin is inside its own noise band is flagged, never silently passed. | IP-3: c1p refusal ≤ 0.5 AND acc_c1p ≤ acc_B2p − 0.05. (The margin-vs-noise clause is the g2 generalisation; see §6.) |
| **PC-4** | **The instrument's validity gates have TEETH** | for every in-run validity gate (shortcut audit, engagement gate, leak guard, verifier), a PLANTED violation — injected into a copy of the pilot inputs, never the campaign bytes — must make the gate predicate FIRE, and the un-planted run must stay under the gate's ceiling. A gate that cannot fire on a genuine planted violation is itself INSTRUMENT-INVALID. Where the instrument has an engagement channel (verify-retry, judge escalation), the planted violation must produce at least one observably non-trivial engagement (e.g. attempts > 1). | IP-2: real c8 lookup ≤ 0.10 ceiling AND planted (base,rel)→gold exploiter pushes recovery > ceiling at ≥ 0.90; IP-4: b4_vacuous flag iff attempts==[1] everywhere |
| **PC-5** | **The gold is structurally elicitable** | the answer/elicitation surface, exercised end-to-end, can carry the gold: a scripted **oracle arm** (an agent/stub that knows the answer and follows only the pinned surface instructions) scores near ceiling under the pinned parser/scorer, and the pilot host produces parseable, scoreable output at a bounded failure rate. All-arms-zero-including-the-oracle is a dead surface, not a null result. | (retrofit) rules-1's oracle arm scored 0.000 — a PC-5 pilot fails in minutes; rules-2's uniform 3-option entity decode + ENTITY-form host-validity floors (A5 0.944/A7 1.000) discharge it |

A check may be recorded `not_applicable` **only** with a written
structural reason in the artifact (e.g. no engagement channel exists for
the second PC-4 clause); an N/A downgrades the verdict to
`PILOT-PASS-WITH-FLAGS` and is printed by the freeze tool — it is never a
silent pass.

---

## 3. The pilot-pass artifact contract — `kot-pilot/1` [STIPULATED — PROPOSED-ASM-1832]

The pilot's verdict is a **pinned JSON artifact** the freeze tool can check
mechanically. One file, canonical JSON, committed under the experiment's
poc directory (convention: `poc/<exp>/results/instrpilot-result.json`),
referenced from the DRAFT record as:

```jsonc
// registry/experiments/<id>.json (DRAFT), inside "pins":
"blocking_pilot": {
  "path":   "poc/rules-2/results/instrpilot-result.json",
  "sha256": "<sha256 of the artifact bytes>"
}
```

Required artifact fields (full shape; the rules-2
`instrpilot-result.json` writer already emits a superset of this and needs
only the `schema_version`/`checks` naming alignment):

```jsonc
{
  "schema_version": "kot-pilot/1",
  "experiment": "rules-2",              // MUST equal the record id
  "mode": "REAL",                        // MOCK artifacts validate pilot
                                         // mechanics only and NEVER satisfy
                                         // the freeze gate
  "verdict": "PILOT-PASS",               // | PILOT-PASS-WITH-FLAGS | PILOT-FAIL
  "verdict_semantics": "instrument-validity ONLY; never campaign evidence",
  "checks": {                            // the five generic channels, each:
    "no_degenerate_arm":      { "pass": true,  "evidence": { /* arm stats, bounds */ } },
    "separation_nonvacuous":  { "pass": true,  "evidence": { /* gap, threshold */ } },
    "controls_nondegenerate": { "pass": true,  "evidence": { /* per-control stats,
                                                  gate-statistic margin vs replicate noise */ } },
    "gate_teeth":             { "pass": true,  "evidence": { /* real-under-ceiling,
                                                  planted-fires, per validity gate */ } },
    "elicitable_gold":        { "pass": true,  "evidence": { /* oracle-arm score,
                                                  parse-failure rate */ } }
    // a check MAY instead carry {"not_applicable": true, "reason": "..."} —
    // downgrades verdict to PILOT-PASS-WITH-FLAGS, never a silent pass
  },
  "flags": [ { "name": "b4_vacuous", "detail": "attempts==[1] (ASM-1808 inherited)" } ],
  "operating_point": {
    "description": "R1 host, pinned-HP LoRA, entity surface, 3-option decode",
    "n_pilot": { "sout": 60, "control": 10 },
    "seed": 0,
    "pins": {                            // MUST agree with the record's pins
      "model_revisions": { /* repo+revision per rung, verbatim from the record */ },
      "harness_manifest": "<sha>",       // and/or corpus/input shas exercised
      "prompt_surface_sha256": "<sha>"   // the exact rendered surface piloted
    }
  },
  "thresholds_predeclared": { /* every PC constant + where it is pinned */ },
  "runner": { "path": "poc/rules-2/instr_pilot.py", "sha256": "<sha>" },
  "records_file": "run-records-instrpilot.jsonl",   // raw per-row evidence
  "records_sha256": "<sha>",
  "cost": { "usd_cap": 2.0, "worst_case_usd_planned": 0.27 },
  "asm_block": "PROPOSED-ASM-1814..1819",
  "date": "2026-07-12T00:00:00Z",
  "emitted_by": "fable-build-4"          // pseudonym discipline (RT-14)
}
```

Contract rules, fail-closed:

1. **Identity**: `experiment` must equal the record id; `mode` must be
   `"REAL"`. A pilot for a *predecessor* experiment never carries forward
   — new record id ⇒ new pilot (or an override, §4).
2. **Operating-point identity**: every pin the artifact declares under
   `operating_point.pins` must byte-equal the same-named pin in the frozen
   record. Any drift ⇒ the pilot is STALE (§5, `ERR_P2_PILOT_STALE`).
   Amending the record's pins after the pilot (new harness sha, new prompt
   surface, changed thresholds) invalidates the pilot by construction.
3. **Immutability**: once a coordinator has read the artifact (and a
   fortiori once a record pins it), the artifact and the pilot's
   pre-declared constants are frozen; iteration means a fresh pilot run
   and a fresh artifact.
4. **Evidence fence**: no number in the artifact may be cited as evidence
   for or against any registered hypothesis. The artifact licenses exactly
   one sentence: "the instrument has dynamic range at the operating
   point". (ASM-1819(a), generalised as PROPOSED-ASM-1835.)
5. **Cost**: the pilot carries its own fail-closed worst-case cap
   (default $2, per-experiment override allowed with justification in
   `thresholds_predeclared`), enforced by the runner's dry-plan exit code
   before any paid second.

---

## 4. The coordinator override path [STIPULATED — PROPOSED-ASM-1833]

A pilot can be genuinely infeasible (no cheap slice exists; the instrument
IS an external human panel whose pilot would consume the panel; a pure
re-analysis record with no new instrument surface). The escape is an
**explicit correction-record-style override**, never silence:

```jsonc
// registry/experiments/<id>.json (DRAFT), top level (NOT inside pins):
"blocking_pilot_override": {
  "correction_id": "c-2026-07-19-<slug>",   // a committed correction record
  "path": "registry/corrections/c-2026-07-19-<slug>.json",
  "sha256": "<sha of the correction record>",
  "justification_verbatim": "one paragraph: why no pilot can exist at this
      operating point, what specific degeneracy risks are being accepted
      unexercised (enumerate against PC-1..PC-5), and what post-hoc check
      substitutes for each",
  "approved_by": "coordinator-1"             // pseudonym; maintainer signoff
                                             // additionally required when the
                                             // record needs Tier-5 signoff anyway
}
```

Rules: the override must name, check by check, which of PC-1..PC-5 is
waived and why infeasible (a partial pilot covering the feasible checks is
always preferred to a full waiver and the justification must say why one
was not run); the freeze then proceeds but the tool appends a
non-fatal flag line to `registry/pause-flags.jsonl`
(`kind: "PILOT-OVERRIDE"`) so the waived gate is permanently visible in
the record's provenance and to the research-engine loop; verdict-gen and
the auditor see the flag. "The pilot costs $2 and we were in a hurry" is
not a justification the correction schema should survive review with —
the override is for *infeasible*, not *inconvenient*.

---

## 5. PROPOSED prereg-freeze wiring — a patch for the coordinator (NOT applied by this build)

Three pieces: a schema addition (necessary — both kot-reg schemas pin
`pins` with `additionalProperties: false` [MEASURED], so
`pins.blocking_pilot` cannot be smuggled in), the freeze-tool check, and
its docstring/error-code registration. Presented as a reviewable
diff-shaped proposal; the coordinator applies, tests, and commits it.

### 5.1 Schema (kot-reg-1.json and kot-reg-2.json)

Add to `properties.pins.properties` (OPTIONAL — legacy records validate
unchanged; adding an optional property changes no frozen bytes):

```jsonc
"blocking_pilot": {
  "type": "object",
  "required": ["path", "sha256"],
  "additionalProperties": false,
  "properties": {
    "path":   { "type": "string" },
    "sha256": { "type": "string", "pattern": "^[0-9a-f]{64}$" }
  }
}
```

Add at the record's top level (also optional):
`blocking_pilot_override` with the §4 shape (`required`:
`["correction_id", "path", "sha256", "justification_verbatim",
"approved_by"]`).

### 5.2 prereg-freeze.py — new named refusals (docstring block)

```
ERR_P2_PILOT_MISSING   neither pins.blocking_pilot nor blocking_pilot_override
                       present — no freeze without a recorded instrument-pilot
                       PASS at the operating point or an explicit coordinator
                       override (docs/next/protocol/blocking-pilot-before-freeze.md §1)
ERR_P2_PILOT_PIN       pins.blocking_pilot.path missing on disk or sha256 mismatch
ERR_P2_PILOT_SCHEMA    pilot artifact is not a kot-pilot/1 REAL record for THIS
                       experiment id, or a required check block is malformed
ERR_P2_PILOT_FAIL      pilot verdict is PILOT-FAIL, or any required check is
                       neither pass=true nor an explicit not_applicable
ERR_P2_PILOT_STALE     an operating_point.pins entry disagrees with the record's
                       same-named pin — the pilot exercised a different instrument
```

### 5.3 prereg-freeze.py — the check (pseudocode, house style)

```python
PILOT_SCHEMA_VERSION = "kot-pilot/1"
PILOT_PASS_VERDICTS = ("PILOT-PASS", "PILOT-PASS-WITH-FLAGS")
PILOT_REQUIRED_CHECKS = (
    "no_degenerate_arm",       # PC-1
    "separation_nonvacuous",   # PC-2
    "controls_nondegenerate",  # PC-3
    "gate_teeth",              # PC-4
    "elicitable_gold",         # PC-5
)

def check_blocking_pilot(record, root):
    """Blocking-instrument-pilot gate (protocol
    docs/next/protocol/blocking-pilot-before-freeze.md; assessment §4
    meta-recommendation). Fail-closed: a DRAFT record carrying neither a
    kot-pilot/1 PASS pin nor an explicit override REFUSES to freeze. The
    override path emits a permanent non-fatal flag (never silent).
    Returns (status, flags) for main()'s summary/pause-flag plumbing."""
    bp = record["pins"].get("blocking_pilot")
    ov = record.get("blocking_pilot_override")
    if bp is None and ov is None:
        raise kc.KotError(
            "ERR_P2_PILOT_MISSING",
            "no pins.blocking_pilot and no blocking_pilot_override — run the "
            "instrument pilot at the operating point (exemplar: "
            "poc/rules-2/instr_pilot.py) and pin its PASS artifact, or record "
            "an explicit coordinator override correction (protocol §4)")
    if bp is None:
        # override: verify the correction record's bytes exist and match
        _p = os.path.join(root, ov["path"])
        if not os.path.isfile(_p) or file_sha256(_p) != ov["sha256"]:
            raise kc.KotError("ERR_P2_PILOT_PIN",
                              "blocking_pilot_override correction record "
                              "missing or sha mismatch: %s" % ov["path"])
        return ("OVERRIDE", ["pilot gate WAIVED by %s (%s) — see %s"
                             % (ov["approved_by"], ov["correction_id"],
                                ov["path"])])
    full = os.path.join(root, bp["path"])
    if not os.path.isfile(full):
        raise kc.KotError("ERR_P2_PILOT_PIN", "%s does not exist" % bp["path"])
    if file_sha256(full) != bp["sha256"]:
        raise kc.KotError("ERR_P2_PILOT_PIN",
                          "%s sha256 != pins.blocking_pilot.sha256" % bp["path"])
    with open(full, "r", encoding="utf-8") as f:
        art = json.load(f)
    if art.get("schema_version") != PILOT_SCHEMA_VERSION:
        raise kc.KotError("ERR_P2_PILOT_SCHEMA",
                          "artifact schema_version %r != %r"
                          % (art.get("schema_version"), PILOT_SCHEMA_VERSION))
    if art.get("experiment") != record["id"]:
        raise kc.KotError("ERR_P2_PILOT_SCHEMA",
                          "pilot artifact is for %r, record is %r — a pilot "
                          "never carries across experiment ids"
                          % (art.get("experiment"), record["id"]))
    if art.get("mode") != "REAL":
        raise kc.KotError("ERR_P2_PILOT_SCHEMA",
                          "mode %r — MOCK pilots validate pilot mechanics "
                          "only and never satisfy the freeze gate"
                          % art.get("mode"))
    if art.get("verdict") not in PILOT_PASS_VERDICTS:
        raise kc.KotError("ERR_P2_PILOT_FAIL",
                          "pilot verdict %r — a PILOT-FAIL blocks the freeze "
                          "pending redesign or an override record (protocol §4)"
                          % art.get("verdict"))
    flags = ["pilot flag: %s" % f for f in (art.get("flags") or [])]
    checks = art.get("checks")
    if not isinstance(checks, dict):
        raise kc.KotError("ERR_P2_PILOT_SCHEMA", "artifact has no checks block")
    for name in PILOT_REQUIRED_CHECKS:
        c = checks.get(name)
        if isinstance(c, dict) and c.get("pass") is True:
            continue
        if isinstance(c, dict) and c.get("not_applicable") is True \
                and isinstance(c.get("reason"), str) and c["reason"].strip():
            flags.append("pilot check %s N/A: %s" % (name, c["reason"]))
            continue
        raise kc.KotError("ERR_P2_PILOT_FAIL",
                          "required pilot check %r is absent or not passing "
                          "(fail closed; N/A needs an explicit reason)" % name)
    # operating-point identity: every pin the artifact exercised must equal
    # the record's same-named pin — a pilot at drifted pins gates nothing.
    op_pins = (art.get("operating_point") or {}).get("pins") or {}
    for key, want in sorted(op_pins.items()):
        got = record["pins"].get(key, record.get(key))
        if kc.canonical_dumps(got) != kc.canonical_dumps(want):
            raise kc.KotError("ERR_P2_PILOT_STALE",
                              "operating_point.pins[%r] disagrees with the "
                              "record — re-run the pilot at the frozen pins"
                              % key)
    return ("PASS-WITH-FLAGS" if flags else "PASS", flags)
```

Call site: inside `check_record(record, root)`, immediately **after** the
P-6 pin checks (so the analysis-script/doc pins are already verified) and
**before** the D9 reuse machinery — the pilot gates the instrument, and
reuse rulings should be adjudicated only on records whose instrument is
established. `main()` threads the returned flags into the summary JSON
and, on the OVERRIDE branch, appends the `kind: "PILOT-OVERRIDE"` line to
`registry/pause-flags.jsonl` next to the existing PAUSE-REASSESS plumbing.

`--dry-run` exercises the gate identically (it already runs every check).

Migration: the gate fires only on records frozen after the patch lands;
`frozen-index.json` entries are immutable and unaffected. The first
consumer is the rules-2 DRAFT record, whose pilot runner already exists —
alignment cost is renaming its gate keys to the five generic check names
(IP-1(a,b,d)→`no_degenerate_arm`, IP-1(c)→`separation_nonvacuous`,
IP-3→`controls_nondegenerate`, IP-2/IP-4→`gate_teeth`,
host-validity floors/oracle→`elicitable_gold`) or emitting a thin
`checks` alias block alongside the existing `gates` block.

### 5.4 Suggested tests (for the coordinator's patch)

Fixture-record variants, one per named error: missing pin
(`ERR_P2_PILOT_MISSING`), sha mismatch (`ERR_P2_PILOT_PIN`), MOCK artifact
(`ERR_P2_PILOT_SCHEMA`), wrong experiment id (`ERR_P2_PILOT_SCHEMA`),
PILOT-FAIL verdict (`ERR_P2_PILOT_FAIL`), missing check
(`ERR_P2_PILOT_FAIL`), drifted `model_revisions` (`ERR_P2_PILOT_STALE`),
valid override (freeze proceeds + flag line), valid PASS (freeze
proceeds). Mirrors the discipline the tool already applies to
ERR_P2_SCALE_LANGUAGE.

---

## 6. Failure → check mapping [COUNTERFACTUAL — PROPOSED-ASM-1836]

The claim "this gate would have caught them" is a counterfactual under the
stated assumption that each pilot would have been run honestly at the
as-frozen operating point. It is motivation, never evidence; each cell
cites the measured failure signature the check's predicate fires on.

| failure | measured signature | catching check | how it fires pre-spend |
|---|---|---|---|
| **rules-1 (VOID)** | all arms 0.000 **including the oracle arm**; direction-unstated cue + menu adjacency | **PC-5 elicitable-gold** (backstopped by PC-1) | the scripted oracle arm scores ~0 on the pilot slice under the pinned parser — a dead elicitation surface fails in minutes, before any campaign row exists. PC-1's floor bound fails simultaneously on every arm. |
| **rules-1-b (host-frame)** | relation-word surface form-dead for the unaided host: pilot A5 **0/24** | **PC-1 no-degenerate-arm** | the baseline arm cannot clear the exact-binomial floor vs chance at pilot n — the host demonstrably does not operate the surface, so the registered contrast has no floor to rise from. (rules-1-b's own A5 probe *was* this check, run ad hoc; the rule makes it mandatory and pre-freeze.) |
| **rules-1-c (verify-retry vacuous)** | verifier never engaged (URN/word type mismatch ⇒ unconditional abstention); **every A3 row attempts=1; A3 ≡ c1** on all 2,574 cells | **PC-4 gate-teeth**, corroborated by **PC-2** | a planted rule violation fails to produce a single attempts>1 row — the engagement gate provably cannot fire (exactly IP-4's `b4_vacuous` predicate, which detects this signature on the inherited arm today [MEASURED]). Independently, PC-2 sees the treatment arm row-identical to its control on the pilot slice: separation vacuous by construction. |
| **g2 AC1 near-miss** | pilot #1 AC1 **0.6909** vs gate 0.65; independence ceiling and run-to-run noise (±2 items ≈ the full gate margin); pilot #2 then measured AC1 = its own independence ceiling (κ = 0.0000) | **PC-3 controls-non-degenerate** (margin-vs-noise clause) | the gating statistic's clearance over its own degeneracy floor (0.6909 − independence ceiling) is smaller than its observed replicate movement at pilot n — PC-3 flags the pass as boundary-sitting instead of passing it silently, forcing the margin question *before* the coordinator reads a green light. (g2's pilot-stop discipline caught pilot #2 as designed; PC-3 is what upgrades pilot #1 from silent near-miss to recorded flag.) |

Coverage honesty: the five checks are a floor, not a ceiling — they encode
the failure modes the programme has *already paid for*. A sixth event of a
genuinely new shape may pass all five; when that happens the protocol's
correct response is a new PC row (a protocol amendment), not a claim that
the gate was sufficient. [STIPULATED, disclosed as PROPOSED-ASM-1835(c)]

---

## 7. Emitted assumption rows

`docs/next/protocol/asm-blocking-pilot-1830-1836.json` —
PROPOSED-ASM-1830 (the rule), -1831 (the five checks), -1832 (the
artifact contract), -1833 (the override path), -1834 (the freeze-tool
wiring proposal), -1835 (licence limits of a pilot PASS), -1836 (the §6
counterfactual mapping, EXTRAPOLATION, non-load-bearing). Range 1830–1839
verified free at emission time (register max ASM-1828; no ASM-183x
reference anywhere in the tree). The register itself is untouched by this
build; central registration is the coordinator's.
