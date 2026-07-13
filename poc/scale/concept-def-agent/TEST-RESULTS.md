# concept-def-agent — 5-concept smoke test (2026-07-13, designer-34)

**Selection.** Deterministic + benchmark-blind: the pilot's frozen round-robin
rule continued to positions 16–20 (`select_test_concepts.py`,
`test-concepts.json`) — zero overlap with the pilot's 15, no gloss/outcome
consulted. The set landed two sense traps by luck of the rule: *builder*
(n-09898025 = the empire-builder sense, not the construction worker) and *dig*
(n-00136131 = the poke-in-the-ribs sense, not excavation).

**Prompt versions (all sha-logged in every report; deltas purely additive
grammar-discipline bullets in §3.5, motivated ONLY by mechanical gate errors —
no benchmark data, no gloss content was consulted):**

| version | sha256 (prefix) | delta |
|---|---|---|
| v1 | `c6491fe3` | initial |
| v2 | `3999abc9` | + operators are never `pred`; + space primes (TOUCH…) are fillers, not predicates; + walk-order bind rule |
| v3 (final) | `fa2f8099` | + quote-scope rule (referent bound inside a quote is invisible outside it) |

## Final state — every concept re-run under the FINAL prompt (v3)

| concept | model | strict JSON | mechanical gate | scholarly bar (my judgment) | AST adequacy (self-flag) | latency | cost (API-equiv) |
|---|---|---|---|---|---|---|---|
| builder | claude-opus-4-8 | ✓ | ✓ PASS (7 clauses, d3) | **meets** — right sense (label self-disambiguated "of an enterprise or nation"), non-circular; minor prose redundancy in the final clause | lossy (honest: enterprise/nation not primitive) | 16.8 s | $0.033 |
| pull | claude-opus-4-8 | ✓ | ✓ PASS (5 clauses, d2) | **meets** — covers both WN disjuncts (toward / with oneself), non-circular | faithful | 12.3 s | $0.032 |
| expensiveness | claude-opus-4-8 | ✓ | ✓ PASS (7 clauses, d3) | **meets** — clean genus-differentia around cost-as-giving-much | lossy (money/price not primitive) | 14.0 s | $0.033 |
| candidate | claude-opus-4-8 | ✓ | ✗ FAIL `ERR_REF_NOT_INTRODUCED` (binds a referent inside a THINK-quote, mentions it outside — twice, v2 and v3) | (gloss itself meets) | lossy | 18.3 s | $0.151 |
| candidate (re-queue) | **gpt-5.6-sol** | ✓ | ✓ PASS (4 clauses, d4) | **meets** — "under active consideration as a possible choice" | lossy (selection/prize not primitive) | 58.1 s | tokens only (subscription) |
| dig | claude-opus-4-8 | ✓ | ✓ PASS (2 clauses, d3) | **meets** — right sense (poke, label "dig (a poke)"), non-circular | lossy (jab-quality dropped, honestly named) | 13.2 s | $0.031 |

**Bottom line: 5/5 concepts hold a strict-JSON, gate-passing, bar-meeting
record; 4/5 from claude-opus-4-8 alone, the 5th via the documented
re-queue-on-another-model path.** Adequacy split 1 faithful / 4 lossy —
consistent with the pilot's finding that lossy-AST, not mechanical validity,
is the true bottleneck (`pilot-review.md` §4).

## Full history (fail-closed behaviour, disclosed)

- Round 1 (v1, opus): builder ✓, pull ✓; expensiveness ✗ (`NOT` emitted as a
  `pred`), candidate ✗ (ref before bind), dig ✗ (`TOUCH` used as a predicate —
  it has no valency frame). All three were PROMPT gaps; v2 added the bullets.
- Round 2 (v2, opus): expensiveness ✓, dig ✓; candidate ✗ (new failure shape:
  bind inside quote #1, mention in quote #2). v3 added the quote-scope rule.
- Round 3 (v3, opus): candidate ✗ again (bind inside quote, mention after it)
  — a reproducible opus-under-`MAX_THINKING_TOKENS=0` weakness on
  quote-heavy explications; NEVER retried on gate-fail (capability signal),
  re-queued to gpt-5.6-sol → ✓ first attempt.
- claude-fable-5: transport-rejected in ~3 s with HTTP 429 "Fable 5 limit"
  (account quota exhausted THIS session — an account condition, not a harness
  defect; the runner now trips STOPCAP on cap patterns instead of retrying,
  mirroring the pinned judge runner). Path unproven today; identical
  invocation to opus, re-test when quota resets.
- gpt-5.6-sol: 2/2 first-attempt strict-JSON gate-passes (dig, candidate).
- No reply ever needed the fence-stripping tolerance; every parsed reply was
  a bare JSON object (directly parseable).

## Cost & latency (measured)

- claude-opus-4-8, warm prompt cache: **≈ $0.03 API-equivalent, ~12–19 s per
  concept** (~12.4k prompt tokens cached, ~0.8–1.2k output). Cold cache first
  call: ≈ $0.15. Subscription auth ⇒ marginal $ = 0.
- gpt-5.6-sol (xhigh reasoning): ~25–60 s, ~2k output tokens incl. reasoning;
  subscription auth, tokens logged in the report.
- Whole smoke test (13 opus calls incl. all re-runs): **≈ $0.77
  API-equivalent, $0 marginal.**
- ~100-concept projection, one opus call each, warm cache: **≈ $3–4
  API-equivalent, ~25 min serial, minutes in parallel** — vs the pilot's
  30–45 *author-minutes* per concept by long agent session.
