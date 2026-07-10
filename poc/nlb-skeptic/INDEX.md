# l3a-parse / a5-nl — §11 item-6 pre-freeze independent skeptic gate

Independent skeptic: **Codex gpt-5.6-sol** (high effort, isolated CODEX_HOME, read-only sandbox,
§4.1-adapted-for-audit — full context, no blinding). Run 2026-07-10.

**GATE VERDICT: DEFECTS FOUND — NOT freeze-clear.** 8 freeze-blocking, 3 should-fix, 0 nit.
Findings 3, 5, and part of 6 were empirically reproduced against the pinned scorers.
Arithmetic (Wilson bounds) confirmed sound; family carve-out confirmed NOT reverse-engineered.

- `skeptic-output.txt` — Codex's verbatim adversarial review (durable custody; scratchpad is ephemeral).
- `skeptic-prompt.txt` — the brief given to Codex.
- `run-skeptic.sh` — the isolated invocation wrapper (global codex-cli untouched at 0.142.5).

Freeze BLOCKED pending a Fable fix pass over all 11 findings + a re-run of this skeptic gate.
