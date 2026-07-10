# Programme-completion loop + goal (Kern self-driver)

Status: BINDING self-operating loop. Authorised by Jesse 2026-07-10 — "create a
loop and goal that will see you get our research programme done as fast and to as
high a quality as possible without creating extra / duplicate work." Complements
`docs/next/opus-execution-practices.md` (which governs HOW Opus runs each
experiment); this doc governs WHAT to drive toward and the self-loop that drives
it. It changes no design law: the honesty discipline, role separation
(Fable designs+interprets / Opus executes+coordinates / Codex+GPT audit), and
`tools/registry` law all still bind.

## GOAL

Bring the Kernel of Truth programme to a defensible, evidence-backed **feasibility
verdict on both value theses** — CORRECTNESS (training-free grounded / deterministic
canonical concept vectors + an engine that grounds and checks claims) and EFFICIENCY
(verifier-offload, dense-concept I/O, compression) — **as fast and as high-quality as
possible, without extra or duplicate work.**

"Done" = every frozen experiment has a mechanical verdict + cross-vendor audit +
**Fable interpretation**; the highest-information roadmap items are executed; and
Fable has produced a **cross-experiment feasibility synthesis** the maintainer can
act on. Kern (Opus) never writes the conclusion — it drives the machine that produces
the evidence and reports only mechanical facts.

## CRITICAL PATH (live read — refresh each iteration)

As of 2026-07-10 the bottleneck is NOT more runs — it is **Fable interpretation**:
`tools/registry/audit-status.py` shows **13/14** frozen experiments run + audited but
PENDING a Fable interpretive assessment (only f2b-replicate is done). Fastest route
to the feasibility verdict:

1. **Clear the Fable-interpretation backlog, BATCHED by family** — G-series semantics
   (g2–g9) as one coherent assessment; f1/f2 efficiency; m0b/l3a/a5 oracle+coverage.
   Batching is the dedup lever the maintainer asked for.
2. **Land the just-completed results' interpretation:** a5-llm audit REJECT (pin
   defect → Fable rules re-freeze vs correction-record); f2b-transfer-llmproxy Stage-1
   (PASS-PENDING-AUDIT, A₁ₚ=0.95, weak-proxy stand-in); define-op census (0.803);
   compression censuses.
3. **Fable cross-experiment feasibility synthesis** across both theses.
4. In parallel, Opus feeds the cheapest-decisive remaining runs + audits + commits,
   never blocking on 1–3.

## THE LOOP (run on EVERY re-invocation — task-notification OR scheduled wake)

1. **ASSESS** — in-flight agents/jobs; newly-completed results awaiting reconciliation;
   usage/quota posture; items blocked on the human or on Fable quota.
2. **RECONCILE** — land mechanical verdicts; commit+push verified artifacts (TARGETED
   paths only); route interpretations→Fable, audits→Codex/GPT; update
   audit-status/beads/registry via central custody. Opus NEVER concludes.
3. **SELECT** — the highest information-per-cost, NON-DUPLICATE next action toward the
   goal. Dedup FIRST (in-flight? `bd`? git? prior assessment/idea registry?).
   Cheapest-decisive-first. Respect roles: Opus executes run-scripts/collection/
   mechanical + commits; Fable owns design/interpretation (dispatch in measured,
   BATCHED waves within quota); Codex/GPT audits.
4. **DISPATCH** — within concurrency ≤ ~10 + usage-gating (back off only on a real
   429); disjoint files, or central-custody serial append for shared files; `nice`
   heavy CPU; foreground gates; no child-spawning coordinators; isolated CODEX_HOME
   for any codex call concurrent with a live judge run.
5. **GUARDRAILS** — no duplicate/overlapping work; no unauthorised outward-facing
   actions (external posts need per-post maintainer auth; GPU spend only on a
   Fable-designed target within authorised budget — Anyscale $100 authorised but
   blocked on the hosted-cloud console step, Modal is the working path); never
   print/commit secrets; targeted `git add` only, never `-A`.
6. **SCHEDULE next wake** — rely on task-notifications for event wakes; set a LONG
   fallback (~20–30 min) via ScheduleWakeup(`<<autonomous-loop-dynamic>>`) so the loop
   survives lulls/hangs. Shorten only when actively polling external state (a live GPU
   job, a CI run).
7. **ESCALATE / PAUSE** — surface to the maintainer only when: a decision is genuinely
   theirs; everything is blocked on the human or Fable-quota with no Opus-executable
   work left; usage is exhausted; or a feasibility verdict is reached. Keep heartbeat
   status to one paragraph. End the loop only on maintainer instruction or goal
   completion.

## Standing human / Fable-blocked items (do NOT re-dispatch; surface when relevant)

- Human judge-1 annotation of the f2b-transfer CSV (the canonical content-vs-
  circularity test; the llmproxy stand-in only proxies feasibility).
- M0a human annotation (bead `r7i`) — gates E1 precision/recall claims.
- Anyscale hosted-cloud console step — once a cloud exists, Opus runs GPU jobs on the
  $100 credit (target chosen with Fable, bead `utq`).
- Fable design/interpretation queue: a5-llm pin-defect ruling; the 13 pending
  interpretive assessments; define-op / compression census interpretations; HGNC
  gene-track extractor; large-OBO chunk-ingest; the maintainer-raised
  leaderboard-benchmark-eval + kernel-precision-linter directions.
