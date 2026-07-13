> **COORDINATOR RECONCILIATION (2026-07-13).** This diagnosis (from a fresh investigative
> agent) is correct on ROOT CAUSE: rules-1-b's A5=0.0 is a frozen-design floor-mis-attribution
> defect (the 0.7912 "headroom" was the ENTITY form, not the relation-word form the design
> scores), NOT a runner bug; the entity-form successor `rules-1-c` remediates it and is FROZEN.
> ONE CORRECTION: the report's "what remains is launching the frozen rules-1-c campaign" is
> **superseded** — `registry/verdicts/rules-1-c.json` shows rules-1-c **already ran and was
> graded INSTRUMENT-INVALID** (interpreted; #24 closed; double-run already avoided). So there
> is **NO rules-1-c relaunch to do**; the A5=0.944 numbers cited in §4 are the pre-freeze
> (14:27) validation run, not a new outstanding campaign. Net effect: rules-1-b is
> superseded + concluded, and bug beads **482y and a4b5 are stale → closed** on this basis.
> Any follow-up to the rules-1-c INSTRUMENT-INVALID result is a separate, new question.

# rules-1-b A5/A1 = 0.0 — host-frame diagnosis (beads 482y, a4b5)

**TL;DR.** The defect is **NOT** a malformed-prompt / answer-extraction bug. It is the
**answer FORM itself**: rules-1-b scored a **23-way forced choice over the kinship
*relation-word* vocabulary** ("...is A's ___" → `grandfather`), a form that is genuinely
at/below floor for SmolLM2-1.7B/135M on multi-hop CLUTRR when the host must *derive* the
relation. The A5 floor (0.15, live via the `acc(A5)-acc(A1)>=0.05` separation gate) was
justified by a **0.7912 headroom datum that was measured on the *entity* form**, not the
relation-word form — a form mis-attribution baked into the frozen design. Switching the
host surface to the **entity form** ("Who is the <rel> of <base>?" → a *name*, 2-option)
recovers A5 to **0.944–1.0**. This is a **FROZEN-DESIGN defect**, and the remediation is
**already complete and validated**: `rules-1-c` (entity form) is FROZEN and supersedes
rules-1-b. The two beads are **stale** — what remains is running the frozen rules-1-c
campaign, not any further diagnosis or a rules-1-b fix.

---

## 1. Root cause — the exact rendering/form difference

### The failing rules-1-b surface (RELATION-WORD form)
From the frozen rules-1-b record and the runner as it stood at commit `d07b55e9`
("rules-1-b: freeze artifacts + A5 GPU host-validity pilot (FAILED floor)"):

- **Frozen dependent variable** — `registry/experiments/rules-1-b.json`
  `/design/dependent_vars[0]/definition`:
  > "exact match against the pinned third-party CLUTRR gold **relation word**
  > (closed **23-word vocabulary**; predates the kernel)"
- **Task header** — `rules1-manifest.json` @ d07b55e9 `prompt_frames.task_prefix`:
  > "Read the family facts, then answer the question with **exactly one relationship
  > word from: {menu}**.\n\nFacts:\n"
- **Answer cue** — `prompt_frames.answer_cue` @ d07b55e9:
  > `"\nAnswer: {b_name} is {a_name}'s"`  (a possessive infill whose continuation must
  > be the composed relation word)
- **Scored option set** — `rules1_runner.py` @ d07b55e9: `menu = list(lex["relations_answer_vocab"])`
  (the **23-word** surface, :662); `gold = item["gold_relation"]` (:526); `choose_word(...,
  ctx["menu"], ...)` scores per-option logprobs over **all 23 relation words** (:477–485).
- `render_answer_cue` @ d07b55e9:385–400 — the ASM-1630 "direction-explicit possessive
  infill" fix (`{b} is {a}'s`); the menu was also moved into the header (ASM-1630 fix 2)
  to stop menu-prior swamping. **Neither fix cleared the floor.**

### The known-working reference surfaces
- **knull-v2 / f2b (1.7B-alone WORKS)** — `poc/knull/runner/knull_runner_v2.py:577`
  uses `frames = f2b_man["prompt_frames"]` and calls `run_alone` from the pinned
  `f2b_runner.py` (`:420–436`). Those frames (`poc/f2b/inputs/f2b-manifest.json`) are a
  **letter-key MCQ**: `option_line: "{key}. {text}"`, `answer_cue: "\nAnswer: "`, gold = a
  **letter key** over a definitions-QA task. Answer token is a single easy letter.
- **rules-1-c entity form (the fix)** — current `rules1_runner.py`: `render_answer_cue`
  (:388–407) emits cue `"\nAnswer: the {rel} of {a_name} is"`; `build_context` (:734–741)
  sets `q_entity = "Who is the <rel> of <base>?"`, `opts` = the **2** non-base lexicon
  **names**, `gold = names[b]` (the chain-top NAME). Answer token is a **name**, 2-option.

### Why the relation-word form yields exactly 0/24 (not ~chance)
The discriminating evidence rules out a broken scorer/extractor and points at the form:

| arm (rules-1-b relation-word form, merged pilot) | acc |
|---|---|
| A1 (135M alone, must derive) | **0/24 = 0.000** |
| A5 (1.7B alone, must derive) | **0/24 = 0.000** |
| A7 (derivation injected, same scorer+cue) | **20/24 = 0.833** |

A7 uses the **same** 23-way scorer and the **same** possessive-infill cue and reaches
0.833 — so the extraction/scoring path is **not degenerate**. The alone arms sit at
*exactly* 0 (below the ~1/24≈0.043 chance floor), i.e. a **systematic** miss: the
possessive-infill cue reliably elicits *a* relation word, but the small host emits a
**wrong-but-plausible** one (the bridge/direct relation, e.g. `father`/`mother`, or a
menu-prior high-frequency word) instead of the **composed 2-hop** gold (`grandfather`).
The runner's ASM-1630 note records the measured mechanism directly: `' grandfather'` was
top-1 at −1.14 with no adjacent menu but fell to rank ~9 with the menu adjacent; moving
the menu to the header helped but did not make the composed relation word top-1 on the
alone R3. The rules-1-c docstring cites the corroborating `nsk1-g2d` calibration:
relation-word form 1.7B = **0.00–0.10** ("dead-at-floor at every tested host"), entity
form 1.7B = **0.76 / 0.7912 (n=958)**; and 8 frame variants (incl. the exact nsk1
chat+generation channel) measured 2026-07-12 on the pinned R3 **never** put the gold
relation word top-1, while the entity form on the *same* stated-facts world with the
*same* f2bt scorer scored **11/12**. Probe artifacts: `poc/rules-1/results-incoming/diag-20260712-formprobe/`.

**The floor mis-attribution.** `rules-1-b.json` `/design/arms_mandatory_baselines[4]`
sets the A5 comparator "headroom datum 0.7912, nsk1 R3 run", and `/endpoints[7]` makes the
`acc(A5)-acc(A1)>=0.05` separation gate "live" on that 0.7912. But 0.7912 is the **entity
(bprime) form** datum, applied to a design whose dependent variable is the **relation-word**
form. The frozen floor therefore assumes a capability the frozen answer-form cannot exhibit.

### The knull cross-check (the requested diff)
The task's premise — "diff the working knull 1.7B-alone frame against rules-1-b" — resolves
cleanly: knull's working 1.7B-alone frame answers with a **letter key over a
different task**; it proves the **f2b harness plumbing** (HFLM `_option_logprobs` /
`choose`, `run_alone`, per-option scoring) is sound, but it is **not** the relation-word
CLUTRR form, so it does not license the relation-word form. The apples-to-apples
comparison is nsk1-g2d on the *same* CLUTRR items (relation-word 0.00–0.10 vs entity 0.76),
which is exactly what the frozen record got wrong. Confirmed numbers this session:
knull kernel 1.7B-alone = **0.691**, plain = 0.948, opaque = 0.512
(`poc/knull/results-incoming/knull-v2-20260713/slice-kernel.on-modal2.log`).

---

## 2. Proposed fix (already implemented as rules-1-c)

Minimal change = **replace the relation-word answer form with the entity (name) form**:
- host surface `"Who is the <gold_rel> of <base>?"`; per-item **2-option forced choice
  over the two non-base lexicon names** (bridge + chain-top; chance 0.5, DISCLOSED);
  gold = the chain-top NAME (third-party CLUTRR proof_state, predates the kernel);
- answer cue `"\nAnswer: the {rel} of {a_name} is"` (direction-explicit; no menu line in
  the prompt — the closed option set lives only in the per-option logprob scorer);
- reset the A5 floor to be justified by an **entity-form** datum (or chance 0.5).

This is already in `poc/rules-1/rules1_runner.py` (`render_answer_cue` :388–407;
`build_context` :720–741) and `poc/rules-1/inputs/rules1-manifest.json`
(`prompt_frames.answer_cue`, `task_prefix "...exactly one name."`), and is captured by
the FROZEN record `registry/experiments/rules-1-c.json`. **No further code change is
required.** (A companion A7 render-only fix — bare derived fact, no stated-facts block,
`build_render_prompt` :447–461 — is also already in place; it lifted A7 from 4/12 to 12/12
at the 135M in the probe.)

---

## 3. Scope ruling — FROZEN-DESIGN defect (successor + re-freeze), **already done**

This is **not** a runner-side rendering bug fixable without touching the frozen record:

- The broken thing is the **answer form**, which is a **frozen dependent variable**:
  `rules-1-b.json` `/design/dependent_vars[0]` pins "exact match against the ... **relation
  word** (closed 23-word vocabulary)". Changing it to a name/2-option choice changes the
  measured quantity.
- The **floor premise** (0.7912) and the **separation gate** (`/endpoints[7]`) are frozen
  and depend on the form.
- The runner bytes were themselves pinned (bead 482y: "rules1_runner.py bytes are pinned by
  amendment seq 1 sha 357a8796").

So the fix necessarily needed a **successor record + re-freeze**. That has **already
happened**: `registry/experiments/rules-1-c.json` is `status=FROZEN`
(`frozen_at 2026-07-12T19:36`, in `registry/frozen-index.json`), `supersedes = rules-1-b`,
new entity-form dependent variable and floor. rules-1-b remains FROZEN and superseded.

**Bead status: both 482y and a4b5 are STALE.** a4b5's own remedy ("if frozen bytes change,
produce rules-1-c DRAFT successor") is complete. The remaining work is **runner/coordinator
work** — launch the frozen rules-1-c campaign — **not** a diagnosis or a rules-1-b fix.
Recommend: update 482y/a4b5 to cite rules-1-c as the resolution and close them once the
frozen rules-1-c campaign has run.

---

## 4. Cheap validation plan (already substantially satisfied)

The fix has already cleared the floor cheaply, **before** any new Modal spend:

- **CPU/A10G entity-form pilots** (`--pilot-n 24`, seed 0):
  `poc/rules-1/results-incoming/pilot-20260712-rules1c` → **A5 = 1.0 (24/24)**, A1 = 0.542;
  `…-rules1c-v2` → A5 = 1.0, A1 = 0.542, A7 = 1.0.
- **Full entity-form run** (rules-1-c, mode=FULL, n=2574 = 858×3):
  `poc/rules-1/results-incoming/20260712-142704-rules1b-parallel` (results JSON
  `experiment: rules-1-c`) → **A5 = 0.944**, **A1 = 0.703**, A7 = 1.0, A3/c1 = 0.531.
  A5 clears the 0.15 floor and the A5−A1 separation gate holds.

To confirm on THIS box with $0 before any relaunch (no GPU/Modal):
1. `python3 poc/rules-1/rules1_runner.py --out-dir /tmp/r1c-mock --mock` — mechanics
   self-check (pins verify, frames render, rows emit).
2. `python3 poc/rules-1/rules1_runner.py --out-dir /tmp/r1c-pilot --pilot-n 24
   --pilot-dtype bf16 --device cpu` — real-model host-validity smoke on the entity form;
   expect A5 well above 0.5 (pilots above show 24/24). This is the same instrument smoke
   that fail-closed on rules-1-b, so it is the correct gate before any Modal launch.
3. Only then launch the frozen rules-1-c campaign on Modal (coordinator/runner scope,
   outside this diagnosis).

---

### File:line index
- Failing form (frozen): `registry/experiments/rules-1-b.json` `/design/dependent_vars[0]`,
  `/design/arms_mandatory_baselines[4]`, `/endpoints[7]`.
- Failing frame (bytes): `poc/rules-1/rules1_runner.py` @ git `d07b55e9` :385–400
  (`render_answer_cue`), :526 (`gold_relation`), :662 (23-word `menu`), :477–485
  (`choose_word` scores 23 options); `rules1-manifest.json` @ d07b55e9 `prompt_frames`
  (`task_prefix`, `answer_cue "{b_name} is {a_name}'s"`).
- Fix (frozen + bytes): `registry/experiments/rules-1-c.json`; current
  `poc/rules-1/rules1_runner.py:388–407, 720–741, 447–461`; current
  `poc/rules-1/inputs/rules1-manifest.json` `prompt_frames`.
- Working reference: `poc/knull/runner/knull_runner_v2.py:577, 420–436`;
  `poc/f2b/inputs/f2b-manifest.json` `prompt_frames`.
- Evidence: `poc/rules-1/results-incoming/pilot-20260712-merged/` (A1/A5=0, A7=0.833);
  `…/pilot-20260712-rules1c[-v2]/` (A5=1.0); `…/20260712-142704-rules1b-parallel/`
  (rules-1-c FULL, A5=0.944); `…/diag-20260712-formprobe/` (8-variant probe);
  `poc/knull/results-incoming/knull-v2-20260713/slice-kernel.on-modal2.log` (1.7B-alone=0.691).
