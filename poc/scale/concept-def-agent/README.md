# concept-def-agent — stateless "define ONE concept" agent for the F1-K kernel-v1 rebuild

A SPECIALISED, STATELESS agent that turns **one capable-model call** into **one
parseable kernel-v1 record**. Input: a word/concept + its WN-3.1 synset.
Output: strict JSON — `{id, label, synset, pattern, gloss, explication
(kot-ast/1), references, status, notes}` — mechanically gated through the
pilot's `validateExplication` + single-concept encode path. This is the
cheap-single-call path for generating the ~100 F1-K explications (issue #33)
without long agent sessions.

**Governance.** Benchmark-blind: the agent sees only {label, synset urn, pos,
lemmas, WN-3.1 source gloss} from the model-independent eligibility pool —
no eval items, no gold answers, no model outcomes, no coverage ranks. No git
side-effects, no registry write, no freeze. colibri naming; no handles.
Author: `designer-34`.

## Files

| file | role |
|---|---|
| `concept-def-prompt.md` | the stateless few-shot system prompt (kot-cda/1): scholarly-definition standard, exact output schema, full closed kot-ast/1 grammar, 6 few-shot exemplars |
| `build_prompt.py` | deterministically regenerates the prompt from the encoder's closed inventories (`encoder/dist`) + the 6 best pilot records (lover, appearance, peer, exit, fidelity, throw — all bar='meets' in `pilot-review.md`), explications byte-faithful |
| `define_concept.py` | the per-concept runner (see header docstring for the full contract) |
| `validate-record.mjs` | the pilot's mechanical gate, pointed at one record: encoder `validateExplication` + `encodeConceptSet` (D=8192, finite, positive-norm) |
| `select_test_concepts.py` | deterministic benchmark-blind selection of the 5 smoke-test concepts: the pilot's frozen round-robin rule continued to positions 16–20 |
| `test-concepts.json` | the 5-concept selection + provenance |
| `out/` | produced records (`<slug>.<model>.json`), per-call reports (`.report.json`), raw call provenance (`out/provenance/`) |

## The exact call

```bash
cd poc/scale/concept-def-agent
python3 define_concept.py <label> <synset> [--model M]

# examples
python3 define_concept.py "builder" n-09898025                        # claude-opus-4-8 (default)
python3 define_concept.py "builder" n-09898025 --model claude-fable-5
python3 define_concept.py "builder" n-09898025 --model gpt-5.6-sol    # codex path
```

Exit 0 ⇔ strict-JSON record produced AND all mechanical checks AND the
encoder gate pass. Everything else fail-closes with a written report — the
runner **reports, never fakes**.

- **claude-opus-4-8 / claude-fable-5** use the truthstyle §4.3 headless
  `claude -p` pattern of the pinned g3 judges
  (`poc/g3-llmproxy-v3/opus-pb-rejudge/run-opus-pb-rejudge.py`): subscription
  auth (API-key env unset, `apiKeySource=="none"` tripwired),
  `MAX_THINKING_TOKENS=0`, `--tools "" --setting-sources ""
  --no-session-persistence`, stream-json events kept as provenance, identity
  tripwire on `init.model`/`modelUsage` (Haiku CLI-sidecar keys allowed, as
  disclosed there).
- **gpt-5.6-sol** uses the codex pattern of `poc/gpt56-review/run-review.sh`:
  fresh isolated `CODEX_HOME` with `auth.json` copied in, npx-pinned
  `@openai/codex@0.144.1`, read-only sandbox, `--ephemeral`,
  `model_reasoning_effort=xhigh`; the system prompt is prepended to stdin
  (codex exec has no separate system channel).
- **"Temperature 0"** is discharged exactly as in the pinned judge spec:
  neither CLI exposes a temperature knob; the first VALID answer is final.
  Non-JSON replies get ≤3 fresh attempts (each recorded in the report); a
  parsed record that fails a check or the gate is NEVER retried — that is a
  real capability signal for the coordinator.
- **Input note.** "The synset" is passed as the synset *record* (urn + pos +
  lemmas + WN-3.1 gloss, labelled *sense-fixing only*): a bare offset cannot
  disambiguate for any model, and the WN gloss is part of the benchmark-blind
  eligibility pool, not an eval artifact. The prompt forbids copying it
  (kernel-K must differ from the corpus d2 anchor; the runner mechanically
  rejects a verbatim-WN gloss, cf. `pilot-review.md` §4 d2/K collision).

## How the coordinator generates the ~100

1. **Select** the ~96–100 concepts (issue #33 selection rule, from
   `poc/scale/f1k-eligibility/candidate-pool.json`; benchmark-blind).
2. **Loop — one call per concept**, e.g.:
   ```bash
   while read -r label synset; do
     python3 define_concept.py "$label" "$synset" --model claude-opus-4-8 \
       || echo "$label FAILED" >> failures.txt
   done < selected-concepts.tsv
   ```
   Calls are independent and stateless ⇒ trivially parallel across models
   and accounts (e.g. shard the list over claude-opus-4-8 / claude-fable-5 /
   gpt-5.6-sol, or run N shards under different subscription accounts). Keep
   per-account concurrency ≤2 on this box (2 shared cores; the work is
   API-bound, cores only matter for the encode gate).
3. **Triage by report**: `ok:true` records go to human review (the §1.1
   four-binary-question pass — same-sense / intension / scholarly /
   AST↔prose); `ok:false` reports name the exact failure (non-JSON, schema
   field, gate error code) — re-queue or hand-author those few.
4. **Never** write to `data/kernel-v1/` or the registry from this harness;
   the coordinator does that after human review.

### Per-concept cost & latency (measured — `TEST-RESULTS.md` for the full table)

- claude-opus-4-8, warm prompt cache: **≈ $0.03 API-equivalent, ~12–19 s /
  concept**; cold-cache first call ≈ $0.15; $0 marginal on subscription auth.
- gpt-5.6-sol: ~25–60 s / concept, tokens logged per report.
- Smoke-test result: 5/5 concepts got a strict-JSON, gate-passing,
  bar-meeting record (4/5 opus first-queue; 1 via gpt-5.6-sol re-queue).
- ~100 concepts ⇒ **≈ $3–4 API-equivalent total**, ~25 min serial,
  embarrassingly parallel across models/accounts.

## AST-lossy handling hook (pending the #33 ruling)

The pilot found lossy-AST is the true bottleneck (`pilot-review.md` §4): the
65-prime metalanguage renders the genus reliably but drops domain differentiae.
This agent handles it as follows:

- The prompt REQUIRES an honest self-flag: `notes` must begin
  `"AST adequacy: faithful — …"` or `"AST adequacy: lossy — …"`, with the
  dropped differentia named (the pilot's `KNOWN-WEAK`-style carried weakness
  note).
- The runner surfaces it as `ast_adequacy_self_flag` in every report, so the
  coordinator can partition output into faithful / lossy WITHOUT reading the
  records.
- When issue #33 rules: **if lossy-admissible-with-note** → keep the record,
  carry `notes` verbatim into the kernel; **if lossy-excluded** → drop flagged
  records and select replacement concepts (reach deeper into the eligible
  pool), no re-prompting needed. Either way the ruling is a pure filter over
  the reports — no regeneration.

## Regenerating / changing the prompt

`python3 build_prompt.py` rebuilds `concept-def-prompt.md` from the encoder
inventories and pilot records; the runner logs `prompt_sha256` in every
report, so any prompt change is visible in provenance. If the ENCODER grammar
changes (an ALGORITHM_VERSION bump), rebuild the prompt — it can never drift
silently because it is generated from `encoder/dist`.
