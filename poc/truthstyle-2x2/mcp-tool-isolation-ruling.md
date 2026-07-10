# MCP tool-definition structural-isolation ruling — blind headless `claude -p` judges (§11 / §7.1)

> STATUS: issued 2026-07-10 by FABLE (experiment-designer role; register owner
> designer-1). SCOPE: every blind headless `claude -p` judge — the completed
> truthstyle-2x2 judge-p3 pass, g3-llmproxy judge-pB, and all future headless
> blind judges (knull and successors). Governing stipulations registered in
> this session: [STIPULATED: ASM-0644] (the ruling + mandatory hardening),
> [MEASURED: ASM-0645] (the leak evidence), [EXTRAPOLATION: ASM-0646] (the
> mechanism reading; load_bearing false). This note decides nothing beyond
> those three lines.

## 1. What was observed (MEASURED)

Run `poc/truthstyle-2x2/opus-runs/20260710T182459Z` (the judge-p3 re-run under
blinding Amendment A1; claude-code 2.1.201, `claude-haiku-4-5-20251001`,
subscription auth), 818 captured `init` events (808 items + preflight + 8
retries) [MEASURED: mechanical walk over the committed `events.jsonl` captures,
2026-07-10]:

- **8 of 818 init events (0.98%) reported a NON-EMPTY `tools` array despite
  `--tools ""` and `--setting-sources ""`** — positions 324, 402, 411, 421,
  575, 672, 715, 804; every one a FIRST content attempt (`c1_t0`). The arrays
  held 8–23 MCP tool DEFINITIONS from claude.ai account-level connectors
  (e.g. `mcp__claude_ai_Gmail__create_draft`, Google-Drive and Context7
  families) — i.e. session-connected MCP servers leaked tool definitions
  non-deterministically into fresh judge processes.
- 269 of 818 inits (32.9%) showed non-empty `init.mcp_servers` (account
  connectors attached, status `pending`/`connected`) even where `tools` was
  `[]` — the connectors attach far more often than their tool definitions
  land; the 8 leaks are the cases where a connector reached `connected`
  before init.
- **Zero `tool_use` blocks in any assistant message anywhere** (leaked
  attempts included); `permission_denials` `[]` everywhere; `num_turns == 1`
  everywhere; the model never invoked any tool.
- The spec §7.1 per-attempt tripwire marked every leaked attempt
  content-INVALID (`tool_use_detected`, `run-dts-judges.py` — the
  `init.get("tools") == []` check evaluates BEFORE the answer field is read);
  each of the 8 items recovered on its second content attempt with
  `init.tools == []`. Final accounting: 808/808 labelled, no-label 0,
  blinding sweep GREEN (`blinding-sweep.json` `clarified_hits: []`).

## 2. Ruling (a): the truthstyle-2x2 p3 verdict STANDS

The verdict (computed 2026-07-10T19:21:28Z, PASS-PENDING-AUDIT) stands. The
precise reason the frozen "judges see only the question bytes / structurally
tool-less" clause is NOT threatened:

1. **The clause is enforced per-attempt, not per-flag.** The frozen §7.1
   validity predicate makes `init.tools == []` a NECESSARY condition for an
   attempt to be VALID. Every retained label therefore comes from a call whose
   captured init event PROVES an empty tool surface — the clause holds over
   the exact set of calls that produced data, by the tripwire's construction.
2. **Exclusion is content-blind, so it cannot select on labels.** The
   invalidation predicate reads the init event and is evaluated before the
   answer field is consulted; the discarded attempt's answer value never
   influences whether it is discarded. The retry uses identical invocation
   bytes, and FIRST-VALID-ANSWER-IS-FINAL (ASM-0241) is preserved verbatim:
   the retained label IS the first attempt satisfying the pre-registered
   validity predicate — a leaked attempt was never a valid first draw.
3. **Completeness and gates are untouched.** No-label stayed 0 (808/808
   labelled), so the frozen label-coverage and pool gates consumed exactly the
   planned n; the 0.98% first-attempt invalidation rate sits far inside the
   ≤3-content-attempt and no-label budgets.
4. **Blinding is untouched.** No banned token (`kernel`/`nsm`/`truthstyle`/
   `f2b`) appears in any capture (sweep GREEN); the leaked definitions are
   generic account-connector schemas carrying no item, project, or experiment
   context — and those attempts are void regardless.
5. **No residual channel requires an independence assumption.** Even if the
   leak timing were correlated with item identity (unproven either way —
   ASM-0646 reads it as a connector-connection race), every item ends up
   labelled by a structurally tool-less call on identical prompt bytes, so the
   estimand — the blind tool-less judge's label on the item bytes — is
   measured for all 808 items. The argument does not lean on the mechanism
   reading.

## 3. Ruling (b): `--tools ""` alone is NOT a sufficient structural guarantee

`--tools ""` governs the built-in tool set; the observed leak shows it does
not deterministically exclude account-level MCP tool definitions, and
`--setting-sources ""` does not govern account connectors at all (the leak
occurred despite both flags) [MEASURED: §1]. Therefore, as a HARD INVARIANT:

- **H1 (BINDING, every blind headless `claude -p` judge, every call):** the
  per-call **`init.tools == []` gate** — together with its companions (zero
  `tool_use` blocks in any assistant message, `permission_denials == []`,
  `num_turns == 1`) — is MANDATORY. Any call whose init event shows a
  non-empty `tools` array is content-INVALID (`tool_use_detected`), retried
  under the protocol's content-attempt budget, and can never become a
  retained label. This is the load-bearing guarantee: it is observable
  per-call, fail-closed, and independent of WHICH mechanism leaks.
- **H2 (defense-in-depth, REQUIRED in every headless-judge protocol staged
  AFTER 2026-07-10):** add **`--strict-mcp-config`** (with NO `--mcp-config`
  argument) to the §4.3-form command. On the pinned claude-code 2.1.201 the
  flag is documented ("Only use MCP servers from --mcp-config, ignoring all
  other MCP configurations") and [MEASURED 2026-07-10: 3 staging probes,
  exact §4.3 form + the flag] it is accepted in `-p` mode and yields
  `init.mcp_servers == []` and `init.tools == []` — the account connectors
  are structurally not attached (vs 269/818 attached without it). Because the
  leak fires at ~1%, three probes cannot bound its residual rate — H2's
  effectiveness against the race is [EXTRAPOLATION: ASM-0646] from the
  attachment-level exclusion; **H2 never substitutes for H1**.
- **H3:** `--setting-sources ""` must never be cited as an MCP-exclusion
  mechanism; its role remains settings isolation only.

## 4. Status of affected protocols

| protocol | H1 gate | H2 flag | action required |
|---|---|---|---|
| truthstyle-2x2 judge-p3 (COMPLETE) | enforced per-attempt by the A1 runner (`run-dts-judges.py`, §7.1) | absent (pre-ruling staging) | none — verdict stands (§2) |
| g3-llmproxy judge-pB (pending run) | **already pinned**: `poc/g3-llmproxy/judge-invocation.md` §6 carries the identical gate verbatim ("init `\"tools\"` must be `[]`; zero `tool_use` blocks; `permission_denials` `[]`; `num_turns == 1` … attempt INVALID, flag `tool_use_detected`"); file sha `dd402cdd4b370823f220f1fe533334648655b0cafb9decaf5b89822939d72ce8` unchanged and matching the DRAFT record's artifact pin | absent | **none before the run** — the runner must simply EXPECT ~1% first-attempt `tool_use_detected` invalidations and handle them as ordinary content attempts under its §7. H2 is deliberately NOT retrofitted: it would alter already-pinned harness bytes for no epistemic gain (H1 is fail-closed), against the one-shot pin discipline. |
| `analysis/g3_llmproxy.py` | n/a — consumes runner-produced integer inputs; validity is runner-enforced per §6/§7 | n/a | none |
| future headless judges (knull, successors) | MUST stage H1 verbatim | MUST stage H2 | both, at staging time, inside the pinned invocation spec |

## 5. judges-invocation.md custody note (the §4.3 addendum edit)

`poc/truthstyle-2x2/judges-invocation.md` §4.3 gains a post-verdict hardening
addendum (§4.3.1) recording this ruling. Custody: the truthstyle-2x2
final-phase record and verdict consumed the STAGED bytes of that spec —
sha256 `5b543f41635f4676382952bd1f6cd75daafa6f4e2186d64ed7f34de06467543d`,
committed inside `poc/truthstyle-2x2/harness-manifest.json` and pinned via ops
amendment seq 1 — and the one-shot pin window closed with the final-phase run.
The addendum changes the working-tree file ONLY; nothing that was consumed is
re-derived from the edited bytes. Auditors recomputing the harness-manifest
pin must use the staged bytes (git history / the manifest's recorded sha), and
the addendum block in the file says so in place. Registered as ASM-0644.

## 6. Self-check gate

`python3 tools/registry/registry-check.py` and
`prereg-freeze.py --dry-run` (g3-llmproxy) were run after all edits of this
session; outputs are pasted in the session report (registry-check PASS;
g3-llmproxy DRY-RUN-OK).
