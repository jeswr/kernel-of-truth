# judge-2 pinned prompt (f2b-transfer stage-1, design.md §4.1)

> The AUTHORITATIVE prompt bytes are `data/d-adj-t/judge-2-prompt-template.txt`
> (sha256 `65ea3c137daa9d236b9de2bc13a94ce6b2c23f9eb845427828ee526c0452e70b`).
> This file is the human-readable record: an informative copy of the template,
> the per-item assembly rule, and the design rationale mapping every operative
> line to the frozen §4 and to judge-1's package — so the two judges verifiably
> answer under ONE protocol. Invocation, ordering, validity, and recording
> rules live in `data/d-adj-t/judge-2-invocation.md`. Authored by FABLE (bead
> `kernel-of-truth-67m`), FILLING the §4.1 "pinned prompt stored in d-adj-t"
> placeholder; no frozen text is amended.

## The template (informative copy — the .txt bytes are authoritative)

```text
You are judge-2, an independent judge in a blind adjudication task.

Below is ONE item about an everyday concept (things like bird, eat, sleep, water, jump, forget). The item is either:

- a multiple-choice question -- "Which option gives the meaning of the word X?" or "A word whose definition is: ...  Which word is it?" -- with options written in a deliberately plain, simplified style; or
- a yes/no question -- "According to the definition of X, is the following true of X? ...".

Answer the item from your own competence with the everyday concepts -- pick the option that genuinely best gives the meaning, or genuinely answer the yes/no question. You are NOT trying to guess an intended answer; there is no trick, and you must not try to infer what the item's author might have wanted.

The item offers an escape answer, and using it is a normal, expected outcome:

- multiple-choice: answer NONE if none of A-D correctly gives the meaning, or if you cannot decide;
- yes/no: answer "cannot say" if you cannot judge the statement.

Do not force a choice. If the options do not describe the concept as you understand it, NONE / "cannot say" is the correct answer.

Rules of conduct:

- Do not run any commands, do not use any tools, do not read any files, and do not search or look anything up. Answer directly from your own understanding.
- Do not write out reasoning or explanation. Respond with the JSON object only.

Output contract (strict): your entire reply must be exactly one JSON object of the form

    {"answer": "<token>"}

where <token> is one of the allowed answers listed under the item -- for a multiple-choice item exactly one of "A", "B", "C", "D", "NONE"; for a yes/no item exactly one of "yes", "no", "cannot say". No other keys, no other text.

--- ITEM ---

{{ITEM}}

--- END ITEM ---

Respond now with the JSON object only.
```

Per-item assembly: the `{{ITEM}}` line is replaced by the item's blind
rendering (question + kernel-rendered option texts + the NONE escape line +
the allowed-answers line; byte-exact rule in `judge-2-invocation.md` §1).
Nothing else is ever added to the prompt.

## Rationale — line by line, against §4 and the judge-1 instrument

| prompt element | source / §4 anchor |
|---|---|
| "independent judge in a blind adjudication task", pseudonym judge-2 | §4.1 pseudonymous judges (RT-14); mirrors judge-1 README's "You are judge-1" |
| everyday-concept framing + the two format descriptions + "deliberately plain, simplified style" | mirrored from judge-1 README "Your task" section, near-verbatim — same task model for both judges; the style note prevents register-driven NONE-inflation exactly as it does for the human |
| "from your own competence ... genuinely ... NOT trying to guess an intended answer; there is no trick" | judge-1 README verbatim-in-substance; design §2 "judges ... answer each item from their own competence"; the added "must not try to infer what the item's author might have wanted" pins the same rule against an LLM's answer-the-test-writer prior — it forbids rationalising toward a kernel-intended answer without hinting one exists |
| escape block ("normal, expected outcome ... Do not force a choice ... IS the correct answer") | §4.3 mandatory escape, mirrored from judge-1 README "The mandatory escape" section near-verbatim; the escape is offered as a genuine first-class answer, biased neither for nor against |
| "Do not run any commands ... do not search or look anything up" | judge-1 README "Do not look anything up"; E5 leak-checked-judge discipline; enforced mechanically by the invocation's empty workdir + zero-tool-use gate |
| "Do not write out reasoning or explanation. Respond with the JSON object only." | the fixed minimal-reasoning contract (with `model_reasoning_effort="low"` pinned at invocation): no chain-of-thought surface on which to reverse-engineer an intended answer; also what makes the reply machine-parseable |
| output contract `{"answer": "<token>"}` | judge-2's analogue of judge-1's `response-template.csv`; same answer tokens byte-for-byte (`A/B/C/D/NONE`, `yes/no/cannot say`), so agreement is computed over one label alphabet; enforced by `--output-schema` |

## What is deliberately ABSENT (blinding — do not "fix" by adding)

No item ids/types/provenance, no "kernel", no project identity, no mention of
other judges or of how labels are used, no §4 text, no eligibility narrative
(judge-1's README names "kernel records" only to let a HUMAN self-certify
naivety; judge-2's naivety is enforced by cross-vendor choice and context
control — naming the kernel to the model could only prime codebook-inference),
no per-item hints, no examples of answered items (an example would anchor the
label distribution). The rendering arriving in `{{ITEM}}` is already blind;
this prompt adds zero bits about provenance or intended answers.

## Escape-token note

The MCQ escape token is `NONE` and the claim escape token is `cannot say` —
identical to judge-1's recording tokens. A judge-2 refusal or malformed reply
is NOT the escape and is never coerced to it; it is a judge-quality event
(`judge2_no_label`, invocation spec §6).
