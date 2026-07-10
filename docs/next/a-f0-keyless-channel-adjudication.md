# A-F0 — keyless claude-CLI channel adjudication (designer ruling)

**Kernel of Truth programme — run-mechanism adjudication for the frozen record
`registry/experiments/a-f0-mint-economics.json`** (kot-reg/2, FROZEN,
frozen_sha256 `fb4147ccfa6f88936effa991616927317f6aaed98eb24b38e11984b334bf5dfc`).
Author: Kern (Fable experiment-designer role, designer-1), for the maintainer.
Date: 2026-07-10. Assumption registered by this ruling: **ASM-0610** (inside the
A-F0 reserved block 0600–0619, append-only). This document changes NOTHING in
the frozen record or its prereg spec; it adjudicates a proposed change and
refuses it.

---

## 1 — The question and the verdict

The box holds no Anthropic API key, but it runs inside Claude Code, whose
headless subscription channel (`env -u ANTHROPIC_API_KEY -u
ANTHROPIC_AUTH_TOKEN claude -p --model claude-haiku-4-5-20251001
--output-format stream-json --verbose`, fresh `--no-session-persistence`
process per call — the same channel the blind judges use) reports a `usage`
object per result, including `cache_creation_input_tokens` and
`cache_read_input_tokens`. The maintainer asks whether A-F0 can be executed
through this channel now, keylessly, instead of over the direct Messages API.

DECISION: NO VALID AMENDMENT EXISTS — the API key is genuinely required. The
  headless claude-CLI subscription channel is ruled INVALID as an A-F0
  transport; the S7 hard precondition (key provisioned at run time, absent key
  ⇒ BOUNDARY STOP, no claude-CLI fallback) stands unmodified; any keyless
  study on the CLI transport would be a NEW experiment record, never an A-F0
  ops amendment [STIPULATED: ASM-0610].

The rest of this document is the reasoning, endpoint by endpoint, and the
exact statement of what provisioning a key buys.

## 2 — What the frozen mechanism requires

LOAD-BEARING: the frozen record pins the definer as `claude-haiku-4-5-20251001`
  called via the DIRECT Messages API with a pinned per-arm call configuration —
  max_tokens 2000 (arms a/b) / 3200 (arms c/d), thinking absent (a/b) /
  `{type: enabled, budget_tokens: 1024}` (c/d), sampling parameters omitted,
  `cache_control: {type: ephemeral}` on the last system block of a
  deterministically serialized definitional prefix, two byte-identical prefix
  groups {a,d} and {b,c} — and names this transport a distinct pipeline
  identity with an explicit no-CLI-fallback clause
  [MEASURED: registry/experiments/a-f0-mint-economics.json, frozen_sha256
  fb4147ccfa6f88936effa991616927317f6aaed98eb24b38e11984b334bf5dfc;
  docs/next/a-f0-mint-economics-spec.md S2/S3/S7].

The pinned call configuration is not incidental plumbing: under ASM-0600 the
pinned configuration IS the pipeline identity, and under ASM-0607 the
transport + serialization difference against the s1-G claude-CLI baseline IS
the treatment under test. Whatever channel runs A-F0 must therefore (i)
instantiate that request shape byte-controllably, (ii) let the instrument
gates verify that the cached-prefix mechanism actually engaged, and (iii)
support the price basis the decision thresholds were sized for.

## 3 — Confound analysis

### 3.1 Cache-amortization confound — the amortization endpoint is unmeasurable

Under `claude -p`, the client constructing the request is Claude Code, not the
runner. Checked on the installed CLI (2.1.201): the CLI owns request
serialization end to end — the tool block (`--tools`), its own system prompt
(`--system-prompt` replaces the text, but *dynamic system-prompt sections*
carrying per-machine cwd/env/git-status content remain in the system prompt by
default, and `--exclude-dynamic-system-prompt-sections` merely relocates them
into the first user message), context injections into the user turn, and —
decisively — the placement of `cache_control` breakpoints. None of this is
observable from outside (the rendered request bytes are not exposed), none of
it is version-stable, and none of it is pinnable in a prompt manifest.

Consequences for A-F0's cache-side deliverables:

- **Attribution is impossible.** `cache_creation_input_tokens` /
  `cache_read_input_tokens` are per-request aggregates. On this channel every
  request is CC-wrapper bytes + definitional-prefix bytes + suffix, with
  breakpoints placed by CC. A positive cache read cannot be decomposed into
  "the definitional prefix was reused" versus "CC's own wrapper prompt was
  reused." The amortization curve's estimand — marginal cost as THE
  DEFINITIONAL PREFIX amortizes over a mint batch (H-AF0-AMORT,
  sec-amortization, cum usd/concept at k ∈ {1,5,10,20,40,60}) — is therefore
  unidentifiable, not merely noisy.
- **The cache-integrity gate goes vacuous.** The ASM-0605 instrument gate
  (`cache_read_input_tokens > 0` on ≥ 90% of post-first-call requests per
  prefix group) exists to catch exactly one failure: the run silently measured
  uncached economics. On this channel CC's own stable wrapper prefix can keep
  that gate green on every call while the definitional prefix re-bills as
  uncached input at $1.00/MTok every single call (e.g. if CC's last breakpoint
  lands before the injected content). The gate designed to catch the
  wrong-mechanism failure is blinded by the channel — worse than absent,
  because it would report PASS.
- **Cross-process byte-identity is not controllable.** Caching is a strict
  prefix match; each call is a fresh process, so warm reads require CC to
  re-render byte-identical prefixes across processes. With default settings
  the system prompt contains git status — and the A-F0 runner itself writes
  checkpoint files after every call, changing git status mid-run: a
  self-inflicted, invisible full-prefix invalidator. Excluding dynamic
  sections moves the volatile bytes into the first user message instead of
  removing them. Either way the standard remedy (diff the rendered prompt
  bytes between two requests) is unavailable because the channel never shows
  the rendered request.
- **The prefix-size gate cannot run at all.** `prefix_min_cacheable_valid`
  requires `/v1/messages/count_tokens` on both serialized prefixes at staging
  (≥ 4096 tokens, the Haiku 4.5 minimum). That is an API endpoint; the keyless
  channel has no equivalent, and the serialized prefix as rendered is not even
  accessible to count.

So of the two endpoints named in the question, the cache-amortization curve is
flatly unmeasurable through this channel, and two of the four instrument gates
(ASM-0605) are respectively vacuous and unexecutable.

### 3.2 Pipeline-identity collision — the treatment collapses

The s1-G baseline ($0.078/legal record) is API-equivalent accounting on the
claude-CLI transport. A headless, tool-restricted, no-session `claude -p` call
is not byte-identical to the s1-G volume-runner configuration — so this is not
a literal re-run of the baseline — but it sits inside the same claude-CLI
transport family, with the same wrapper, the same subscription accounting, and
the same unpinnable serialization. Running A-F0's arms through it produces a
*third* pipeline identity that is neither the baseline nor the mechanism under
test:

- H-AF0-ECON as frozen — "the direct Messages-API cached-prefix definer beats
  the s1-G claude-CLI baseline" — is simply not tested; what would be compared
  is CLI-variant-X vs CLI-variant-G, i.e. the transport term that ASM-0607
  registers as THE treatment drops out of the comparison entirely.
- The no-CLI-fallback clause (S7) was written against precisely this move:
  the CLI channel "silently revert[s] the pipeline identity under test." A
  fresh/tool-less/no-session invocation is *different enough* from s1-G to
  add new wrapper confounds, and *not different enough* to constitute the
  registered treatment. It inherits the worst of both.
- Even the arm structure is not instantiable. The fork A-F0 exists to resolve
  is output-form × thinking. Output form (arms a vs b) is prompt-driven and
  would survive; the thinking fork (arms c vs d at `budget_tokens: 1024`
  versus thinking-off) cannot be pinned through the CLI — there is no
  budget_tokens control on this channel (the `--effort` flag is a different
  parameter and is unsupported on Haiku 4.5 per ASM-0601), and per-call
  `max_tokens` (2000/3200) is likewise not settable. Half the design's cells
  cannot be constructed.

### 3.3 Cost basis — real counts of the wrong mechanism, on the wrong billing basis

The stream-json `usage` token counts are trustworthy *as counts*: they are the
API's own usage fields for the request CC actually sent. Two things still
break the price basis:

- **They price the wrong request.** Multiplying those counts by the ASM-0601
  table yields a valid API-equivalent projection *of the CC-wrapped pipeline*
  — wrapper tokens included, cache classes as CC's breakpoints happened to
  land. This is not analogous to the accepted Batch ×0.5 derived projection:
  the Batch multiplier rescales measured usage of the mechanism's OWN request
  shape; this channel changes the request shape itself. The number produced
  would be `usd_per_legal_record` of a pipeline nobody proposed to adopt,
  compared against thresholds (PASS ≤ $0.0585, FAIL ≥ $0.078) whose 25%
  margin was sized (ASM-0602/0607) for a different treatment's named
  comparability weaknesses. (`total_cost_usd`, where present, is CC's own
  estimate, not billing, and is irrelevant under the frozen usage×table
  basis.)
- **Subscription is not API-billed.** A-F0's registered advance over s1 is
  that it measures "real API dollars" on the adoptable transport — the
  ASM-0609 rationale states it "makes the cost side of the ledger real."
  Through the subscription channel every dollar figure regresses to
  API-EQUIVALENT accounting, the s1 basis, on both sides of the comparison.
  The kill criterion's "real API-billed usage fields" language would be
  false on its face.

## 4 — Endpoint-by-endpoint measurability through `claude -p`

| Frozen endpoint / gate | Keyless CLI channel | Why |
|---|---|---|
| `primary` `/analysis/best_lawful_usd_per_legal_record` (H-AF0-ECON) | NOT VALIDLY MEASURABLE | prices a third pipeline identity; pinned call config not instantiable; thresholds sized for a different treatment; billing basis reverts to API-equivalent (§3.2, §3.3) |
| `sec-amortization` (H-AF0-AMORT, the curve) | UNMEASURABLE | per-request usage aggregates cannot attribute cache reads to the definitional prefix; breakpoints CC-owned (§3.1) |
| `sec-cache-integrity` gate | VACUOUS | wrapper-prefix reuse alone can satisfy it while the definitional prefix runs uncached (§3.1) |
| `sec-prefix-min` gate | UNEXECUTABLE | needs `/v1/messages/count_tokens`; no keyless equivalent; rendered prefix not accessible (§3.1) |
| `sec-completeness`, `sec-budget` | executable but moot | they gate a run whose primary and cache-side endpoints are already invalid |
| `sec-fork-diagnostics` (output-form × thinking deltas) | HALF-CONSTRUCTIBLE | a-vs-b output form survives as prompt content; c/d thinking arms cannot be pinned (no budget_tokens/max_tokens control) (§3.2) |
| Arms c/d configuration | NOT INSTANTIABLE | no thinking-budget or max_tokens control on the channel (§3.2) |

Because the primary endpoint, the amortization endpoint, two instrument gates,
and half the arm structure fail on this channel, there is no honest
restriction of A-F0 — however downgraded — that both runs keylessly and still
measures anything the frozen record promised. An "amended A-F0" here would not
be a measurement-mechanics amendment; it would be a replacement experiment
wearing the frozen record's thresholds. That is exactly what the freeze
discipline exists to prevent.

## 5 — What provisioning a key buys (the maintainer's exact question)

An Anthropic API key enables the full frozen design, unchanged:

- the pinned request shape, byte-controlled by the runner: two
  deterministically serialized prefix groups, `cache_control` on the last
  system block, per-arm thinking/max_tokens, sampling defaults;
- `count_tokens` staging preflight (prefix ≥ 4096 tokens) and a
  non-vacuous cache-integrity gate, because every token in the request is the
  runner's own;
- a valid amortization curve — the definitional prefix is the only cacheable
  prefix in the request, so cache_creation/cache_read attribute cleanly;
- real API-billed economics on the transport A-E1 would actually inherit,
  compared like-for-frozen against the $0.0585/$0.078 thresholds;
- scale: ~450 calls, expected spend ≈ $4.1, hard abort at $10.00
  (budget.usd_cap), one run window.

Minimum provisioning: any Anthropic API key with Messages API +
`count_tokens` access to `claude-haiku-4-5-20251001` and ≥ $10.00 of headroom,
present in the runner's environment for the run window only. The key is never
written to the repository or any hashed artifact (RT-14 account-lint
discipline); raw usage fields are logged so every dollar figure reconverts
under a corrected table (ASM-0601).

## 6 — The keyless option that WOULD be lawful (and is not taken)

A new, separately designed experiment record could measure the a-vs-b
output-form fork on the headless CLI transport with API-equivalent accounting
— explicitly scoped as CLI-transport-only, no cached-prefix claim, no
amortization claim, no thinking arms, thresholds derived fresh rather than
inherited from ASM-0602. That would be a legitimate but different instrument,
answering "which output form is cheaper on the transport we already have,"
not "does the cached-prefix Messages-API definer beat the baseline."

Designer recommendation: do not build it. It duplicates most of A-F0's
staging effort for a fraction of its information, cannot configure A-E1's
transport decision, and the real A-F0 remains necessary afterward regardless
of its outcome. Provision the key. Nothing in this adjudication creates such
a record, and per ASM-0610 it could never be created *as* an A-F0 amendment.

## 7 — Disposition

- The frozen record and prereg spec are untouched; frozen_sha256 unchanged.
- ASM-0610 registered (designer ruling, binding on execution; A-F0 reserved
  block, append-only after existing later entries).
- Status of A-F0 remains FROZEN awaiting the S7 staging sequence; the absent
  key remains a BOUNDARY STOP to the maintainer, exactly as frozen.

| ASM | Role |
|---|---|
| ASM-0610 | keyless-channel refusal: claude-CLI subscription transport invalid for A-F0; key precondition stands; keyless CLI study = new record, never an amendment |

*Cross-references:* `docs/next/a-f0-mint-economics-spec.md` S2/S5/S7;
`registry/experiments/a-f0-mint-economics.json`; ASM-0600/0601/0602/0605/0607
(the stipulations this ruling enforces); `docs/next/io-compression-ideas.md`
§2.2 (caching mechanics).
