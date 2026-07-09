# f2b-transfer — Opus-runner execution log (BOUNDARY STOP at §11 step 1)

- run-ts (UTC): 20260709T164008Z
- runner_agent_id: kern/opus-runner-3
- role: experiment-runner (Opus execution) — EXECUTE a Fable-frozen design; never design, never conclude
- experiment: f2b-transfer (registry/experiments/f2b-transfer.json, status DRAFT)
- authorization scope (per task): §11 steps 1–2, judge-2, judge-1 human package; STOP before Stage-1 verdict
- outcome: **BOUNDARY STOP** — the §11.1 d-qa-t build is NOT executable as a
  seed-and-count change; it requires a design decision (the per-concept item
  plan) that is not frozen by Fable. No d-qa-t built, no freeze, no
  adjudication run. Nothing spent. Nothing about the programme is concluded here.

## Pin verification (fail-closed, PASS)

- prereg_doc: `poc/f2b-transfer/design.md`
  sha256 = `4cb5dcaf3e0767b272e1a300cf4729e79e3e919d07cf996c8475cc5122ea812e`
  == record `prereg_doc.sha256` → **MATCH**. The design read here is exactly the
  one the DRAFT record pins.

## §11.1 build attempt — BOUNDARY CHECK

Task: port `data/d-qa-t/build-dqat.py` from the committed
`data/d-qa-r/build-dqar.py` as a **seed-and-count change ONLY**
(seed `dqat/1|f2b-transfer|20260710`, count 360, LC8-t = prompt-surface
disjointness from d-qa ∪ d-qa-r), per design §3.1.

### What IS a pure, determined change (not the blocker)

- Generator seed → `dqat/1|f2b-transfer|20260710`: pure constant swap.
- ID namespace `dqar:` → `dqat:`: pure constant swap.
- LC8-t reference set: `load_dqa_prompt_hashes()` currently loads the 650 d-qa
  prompt hashes; extending it to ALSO load the 1000 d-qa-r prompt hashes
  (same unsalted `qhash(question, options)` construction) is a mechanical,
  fully-determined extension. **LC8-t is NOT the blocker** (the task named it
  as a candidate; it is pure).

### What is NOT determined by the frozen design — the blocker: the COUNT (360)

build-dqar's `build_items()` emits, per concept, r1..r9 unconditionally (9
items) plus r10 for a seeded subset. Therefore its output is **hardcoded to the
range [972, 1080]** for the 108 covered concepts. The count is not a free
parameter of a fixed plan; `N_ITEMS` only sizes the r10 subset via
`N_TENTH = N_ITEMS - 9*108`, guarded by `0 <= N_TENTH <= 108`.

Reproduced arithmetic (constants read from the committed script):

```
build-dqar build_items output range: [972, 1080]
N_ITEMS=1000 -> N_TENTH = 28   ; guard(0<=N_TENTH<=108) = True
N_ITEMS= 360 -> N_TENTH = -612 ; guard = False  => DQAR_ERR_SOURCE abort
360/108 = 3.3333 items/concept (non-uniform; 108*3 + 36 = 360)
```

Consequences (both hold):

1. A naive `N_ITEMS = 360` makes `N_TENTH = -612`, so the committed guard
   `if not 0 <= N_TENTH <= len(covered): die("DQAR_ERR_SOURCE", ...)` fires and
   the build aborts fail-closed. The script literally cannot run at 360.
2. Even ignoring the guard, `build_items()` structurally emits ≥ 9 items/concept
   = ≥ 972 items. 360 is far below the 972 floor and unreachable without
   **re-authoring `build_items` to a different per-concept plan** (≈ 3.33
   items/concept: e.g. 3 base templates for all 108 + a seeded 36-concept 4th).

Choosing that per-concept plan is a **design decision**, not a seed-and-count
edit:
- WHICH templates each concept receives (from the def-match / term-match /
  claim-true / claim-false vocabulary) and in what proportion;
- the type-balance needed to pass the fail-closed leak machinery — in
  particular LC7 (answer-position balance and yes/no ≤ 0.75). A truncation to
  the first three build-dqar templates (r1 def-match, r2 term-match, r3
  claim-true) yields all-"yes" claim items and would trip LC7's yes/no
  imbalance abort; so the "obvious" truncation is itself inadmissible. The
  design §3.1 lists all four types as expected but does not specify a plan that
  hits exactly 360 while passing the leak checks.

The design §3.1 instruction ("a seed-and-count change of build-dqar.py") is
therefore inconsistent with the frozen count (360 < 972 floor). Resolving it
requires Fable to freeze the d-qa-t per-concept item plan (and confirm the
resulting four-type / answer-position balance passes the leak machinery).

### Search performed before declaring the STOP (no plan found anywhere)

- `data/d-qa-t/` — does not exist (no prior build output).
- `data/d-qa-t/build-dqat.py` — does not exist.
- `registry/corrections/f2b-transfer/` — does not exist.
- repo-wide grep for `dqat` / `d-qa-t` (md/py/json/jsonl) — only
  `poc/f2b-transfer/design.md` and `registry/experiments/f2b-transfer.json`
  reference it (plus unrelated `data/*/minted-urns.jsonl`).
- `git log` — the design was committed in `5d1a5f7` ("f2b-transfer:
  frozen-ready design"); no build-dqat.py has ever existed.
- `bd list` — no bead specifies a d-qa-t per-concept plan or item count.

## Downstream steps — all blocked by the same STOP

- §11.2 freeze: NOT run. The design/task wants the real d-qa-t corpus pin
  written into the record before freeze; it cannot be produced. The DRAFT
  record is left untouched (d-qa-t pin remains its PINNED-AT-INPUTS placeholder).
- judge-2 (GPT-5.5) adjudication: NOT run. It adjudicates d-qa-t items, which
  do not exist.
- judge-1 human package: NOT assembled. Same dependency.
- No GPU, no `codex` spend, no API keys touched. $0.

## Artifacts written by this run

- this run-log (`poc/f2b-transfer/opus-runs/20260709T164008Z/run-log.md`)
- bead `kernel-of-truth-voc` (P1) queuing the Fable design decision.

No registry record was frozen or edited. No `data/d-qa-t/` was created (writing
a build-dqat.py would require inventing the per-concept plan — out of role).
