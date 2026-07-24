# Cross-vendor re-review (GPT-5.6 gpt-5.6-sol, xhigh) — F1-K dump-patch r3 (bead 2zh8)

> Re-review of r3 (SHA e4e04177...) after the r2 gate-0 REJECT. Verdict CLEAN: all code-fixable
> findings closed fail-closed; delta surgical (moe() hook byte-identical); 3 real-engine gates
> remain documented MANDATORY-BEFORE-PAID-CONSTRUCTION obligations. Runner: run-review.sh (codex 0.144.1).

---

## Verdict: **CLEAN**

All code-fixable r2 findings are genuinely closed fail-closed. r3 SHA-256 is `e4e04177068d0d8563ecdd24a4bc1f2c25be93a97992c173207ae760f7543887`.

- **Finding 3:** `kaed_parse_int` clears `errno`, rejects no-conversion/ERANGE/out-of-range values, and bounds every manifest cast to at most `INT_MAX-1` ([kae_dump.h](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/f1k-harness/dump-patch/kae_dump.h:108)). All four engine and mock sites use it. The exact `2147483648` span now exits nonzero; pass-1 `T` and both-pass `ferror` checks are present. No unchecked manifest `long→int` cast remains. The separate layer-CSV casts are dominated by `0 <= v < n_layers`, so they are exact.
- **Finding 4:** Every f64 accumulator and its staged f32 cast is checked before any line bytes are written ([kae_dump.h](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/f1k-harness/dump-patch/kae_dump.h:239)). `run_dump` independently checks finiteness and `gc == count(span >= 0)` before mean arithmetic ([build_carriers.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/f1k-harness/build_carriers.py:676)). No NaN/Inf success path remains.
- **Finding 8.2:** The clone parser correctly captures dotted symbols and maps clones to their base names ([bringup.sh](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/f1k-harness/bringup.sh:123)). The precise historical 66→82 count was not independently replayable without its disassembly, but the implementation is correct.
- **Finding 6:** Missing, malformed, or mismatched `TOK_SHA256` exits nonzero before output ([tok_glm52.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/f1k-harness/tok_glm52.py:56)). Both wrapper and worker text require every unique construction text, zero mismatches.
- **Surgical delta:** The `moe()` hook, global arming state, phase-separation guard, arming block, and dispatch are byte-identical to r2; only dump parsing/writing and associated payload/tests changed. The load-bearing objdump signature remains 79 shared functions, only `{main, moe}` differing, none removed. The accepted newly-outlined-symbol spelling changed from `run_score` to `run_kae_score`, but this does not expand the shared-function blast radius.
- **Outstanding gates:** The real unarmed byte-identity, full-corpus tokenizer equality, independent MoE-sum cross-check, and fresh pinned-HEAD rebuild are explicitly unchecked, mandatory-before-paid-construction obligations—not claimed complete ([PATCH-NOTES.md](/home/ec2-user/css/kernel/kernel-of-truth/poc/glm52-probe/f1k-harness/dump-patch/PATCH-NOTES.md:308)).

The missing dedicated pass-2 `ferror` injection is acceptable: the check is present before finish, and the same failure primitive is exercised through pass 1. This is a minor coverage asymmetry, not a fail-open gap.

Fresh checks passed: tokenizer 10/10, carrier consumer 22/22, exact integer negatives, non-finite negatives, and the plain C suite 64/64. r3 is ready to be pinned only after the documented real-engine gates pass.