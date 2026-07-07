# poc/e1 — E1 core freezing experiment harness

Prep for **E1** (docs/poc-design.md Phase E; bead `kernel-of-truth-bk0`):
TinyStories + seeded p=0.5 concept/prime substitution, GPT-2-style toy
(d_model=512, ~12.6M non-embedding params, word-level 8k vocab), **5 arms x
5 paired seeds** differing ONLY in the 54 concept-token rows:
kernel-frozen / shuffled-kernel-frozen / random-frozen / trainable /
kernel-init-trainable.

## Layout

| path | what |
|---|---|
| `harness/` (TS) | artifact generators, run NOW and committed: mapper-lexicon artifact + TS<->python parity fixture, kernel/control vector tables @D=512 (pin-verified `kot-enc-Bq/1`), cloze template-type inventory + seeded held-out split |
| `inputs/` | the committed artifacts (provenance-stamped) |
| `pipeline/` (py) | bit-exact mapper port (parity-GATED), DetStream port, `build_data.py` (annotate once -> per-seed substitution -> uint16 shards), mock tables |
| `train/train_e1.py` | single-file trainer: arms, row freezing (weight-decay exclusion + optimizer-state masking + bit-identity assertion), paired-seed batch schedule, step-0/50%/100% checkpoints, LR-sweep mode |
| `eval/` | `eval_e1.py` (cloze on held-out template types, concept-slice PPL, mid-layer probes at non-concept positions, step-0 baselines) + `stats_e1.py` (exact paired permutation, TOST d=0.5, Holm, PPL-saturation rule, verdict JSON+md quoting the pre-registered criteria verbatim) |
| `run_all.sh` | `mock` (CPU pipeline check) / `full` (the pre-registered grid; used by `poc/gpu/launch-e1.sh`) |
| `smoke/` | mock smoke driver + independent checkpoint-level assertions |
| `results/` | mock verdict + smoke evidence (committed); GPU results land here via the results branch |

```bash
cd poc/e1 && npm install && npm test          # TS artifact tests
npm run inputs                                # regenerate artifacts (deliberate only)
E1_CORPUS=<TinyStories-valid.txt> bash smoke/run_smoke.sh   # CPU mock end-to-end
# full grid: poc/gpu/launch-e1.sh (see poc/gpu/README.md, incl. cost table)
```

## Design decisions bound to the pre-registration

- **Dimension / encoder pin (Common rules 2-3, path (i)):** d_model = 512 so
  the pinned `kot-enc-Bq/1`@512 hash
  `3492799e…` applies; the vector-table generator and the TS tests verify the
  live hash against the pin and FAIL CLOSED on mismatch. No decode-dependent
  claim runs here (Bq scope).
- **Substitution scope:** stochastic p=0.5 substitution applies to BOTH
  concept- and prime-mapped tokens (M0a: 17.08% mapped mass x 0.5 ≈ 8.5%
  substituted exposure; concepts alone would give only ~1.6%). Only the 54
  concept rows are frozen/controlled (Common rule 4); the 65 prime tokens are
  ordinary trainable vocab in every arm. Abstained tokens are never
  substituted.
- **Concept-slice metrics (M0a consequence):** primary cloze + concept-token
  PPL are computed on the concept-token slice, never diluted corpus-wide.
- **Freezing (Common rule 4):** frozen = concept rows only; embeddings (tied
  with the LM head) sit in the wd=0 optimizer group in ALL arms (satisfies
  "excluded from weight decay" with no arm asymmetry); frozen-row grads are
  zeroed after every backward so Adam moments stay exactly 0; the mask is
  active from step 0 (optimizer state asserted empty at attach); frozen rows
  are asserted **bit-identical** (torch.equal) at every checkpoint — a
  violation crashes the run.
- **Paired seeds (Common rule 1):** shards, story order, substitution draws
  and batch schedule are functions of the seed index only (SHA-256 DetStream
  labels, committed); base model init is arm-independent per seed.
- **LR rule (Common rule 5):** per-condition sweep {3e-4, 6e-4, 1e-3} on
  seed 0 at half budget, best-of-3 by val loss, then fixed for all seeds
  (`lr-selection.json` committed with results).
- **Primary endpoint (MAJOR 6/12):** concept cloze accuracy on the 8
  HELD-OUT definitional template types (seeded split committed in
  `inputs/cloze-templates.json`) x concepts attested in all seeds;
  single look = kernel@50% vs shuffled@100%; exact one-sided sign-flip
  permutation test (min attainable p = 1/32 at n=5).
- **Kill direction (MAJOR 11):** TOST with SESOI Cohen's d = 0.5.
- **Circularity guard (MAJOR 5):** every metric also runs on the step-0
  kernel-frozen checkpoint; probes read mid-layer states at the final word
  token (a non-concept position) only.
- **PPL rule (MAJOR 13):** if concept-token PPL agrees within 2% across all
  arms at 100%, the experiment is declared UNINFORMATIVE.

## Deviations / clarifications vs the E1 spec (flagged per the brief)

1. **Frozen-row scale.** Encoder vectors are unit-norm; trainable rows init
   at N(0, 0.02²) (E[‖row‖] ≈ 0.4525 at d=512). Kernel/shuffled/kernel-init
   rows are scaled by `frozenScale = 0.02·√512` at load so all arms' concept
   rows share the same norm scale. The spec fixes random-frozen's
   distribution but is silent on kernel-row scale; unscaled unit-norm rows
   would confound kernel-vs-random/trainable with a 2.2x norm mismatch. The
   PRIMARY contrast (kernel vs shuffled) is norm-identical under any choice.
2. **Cloze instrument.** "Concept cloze on held-out template types" is
   instantiated as 16 definitional frame types embedding each concept's
   kernel-v0 `gloss` + a `{c}` slot scored over the 54 concept-token logits
   (mechanical 16x54 grid; the held-out unit is the template TYPE, per
   MAJOR 6). Frames are machine-checked concept-leak-free; glosses are fixed
   kernel-v0 data (may mention other concepts' words — identical across arms
   and covered by the step-0 guard). Eval prompts are NOT substitution-
   augmented (plain words except the target slot), applied equally to all
   arms.
3. **Primary concept subset.** Pre-registered here: the primary averages over
   concepts with ≥1 substituted train occurrence in ALL seeds (M0a: 11 of 54
   concepts never fire in TinyStories; zero-exposure concept tokens are at
   chance for every arm and only dilute). The all-54 aggregate is reported as
   descriptive.
4. **Word-level vocab of 8000** (upper half of the pre-registered 4-8k):
   99%+ token coverage; concept rows = 54/8000 rows ≈ 0.7% of embedding
   params. Template/gloss words are force-included (eval fails closed on
   OOV).
5. **One-sided primary test.** The criterion is directional
   ("kernel > shuffled"), so the permutation test is one-sided; with 5 seeds
   min attainable p = 1/32 = 0.031 < 0.05 (a two-sided version could never
   reach 0.05 at n=5).
6. **Sweep at half budget.** Common rule 5 fixes "small sweep on seed 0,
   best of 3 by val loss" but not the sweep length; pre-registered here as
   50% of the token budget (cost table in poc/gpu/README.md).
7. **Mock smoke corpus.** The brief's "~50 MB sample slice" was not on disk;
   the canonical M0a slice (TinyStories-valid.txt, 19.4 MB, sha in
   `inputs/mapper-parity-fixture.json`) was fetched and used for the parity
   fixture and the smoke. The smoke's vector tables are random
   (`mock: true`-stamped): kot-enc-Bq/1 fails closed at d=64 by design, and
   the smoke checks MECHANICS, never content.
8. **Token budget 200M** (≈16x non-embedding params) — a design knob the
   spec leaves open; checkpoints at 50%/100% of it implement the MAJOR 12
   single look. The PPL-saturation rule guards the "budget too generous"
   failure mode.

## Mock smoke status

See `results/verdict-e1-mock.*` + `results/smoke-log.txt` (committed after a
green run): 5 arms x 2 seeds x 200 steps (d=64, 2 layers, CPU, niced) on the
sample slice, full pipeline data->train->eval->stats->verdict, with
independent checkpoint-level assertions: frozen concept rows bit-identical
step0 vs 50% vs 100% in all frozen arms, trainable arms' rows moved,
non-concept rows trained, val losses improved, verdict emitted mock-labelled.
