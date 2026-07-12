# CODEVERT G1-FORWARD — design pin (written and hashed BEFORE the G1 pool is cloned)

> **Status: [PINNED DESIGN, PROVISIONAL-ON-LLM-PROXY instrument].** Per the
> maintainer decision on issue 16 (2026-07-11): CODEVERT is re-scoped to the
> forward/lexical subset that clears the G1 floor; G1 gold annotation runs
> with Fable + GPT-5.6 as the two annotators (LLM stand-ins, NOT human — every
> gold-dependent number is PROVISIONAL-ON-LLM-PROXY); the coordinator performs
> the mechanical verdict. This file is authored and sha256-hashed BEFORE any
> G1 repo is cloned or looked at (ordering is filesystem-time-consistent only —
> the G0 auditability caveat 1 applies verbatim: no git object exists at pin
> time because this agent performs no git operation; the coordinator commits).
> Author: Fable experiment agent, 2026-07-11. No git/bd/kb operation performed.
> New assumptions are PROPOSED-ASM block **ASM-1110…ASM-1119** (disjoint; doc
> note only — the coordinator registers them; nothing here edits any registry).

## 1. The re-scoped vertical: CODEVERT-FL/1 [PROPOSED-ASM: ASM-1110]

Primary family set FL-4 (the maintainer's named list "defines-where / imports
/ contains / lexical", mapped onto G0's measured family inventory):

| family | G0 pooled κ (agent-selected pool, non-scored) | class |
|---|---|---|
| contains | 1.0000 | lexical [ASM-1053] |
| contained_in | 1.0000 | lexical [ASM-1053] |
| imports_of | 0.6466 | forward |
| where_defined | 0.3994 pooled; bimodal 0/1 per repo (hazard-driven) | exhaustive-over-names, maintainer-included |

FL-4 aggregate on the G0 pool [MEASURED, G0, non-scored]: query-pooled
6392/8520 = 0.7502, family-macro 0.7615 — both above the 0.5 floor.
DISCLOSED AMBIGUITY: the maintainer's brief quoted "κ≈0.72", which is G0's
*forward-4* macro (contains, contained_in, imports_of, **callees_of**;
0.7198) — a set that omits where_defined and includes callees_of (0.2326,
which does NOT clear the floor and is not in the maintainer's family list).
Resolution pinned here, not invented post-hoc: **FL-4 as tabled above is the
primary scored universe; callees_of is carried as a disclosed SENSITIVITY
SLICE** (annotated and reported identically, never in the primary aggregate).
The excluded families (callers_of, imported_by, instance_of) are the G0
structural collapse; they are PY-STAT/2 territory (the parallel spike).

## 2. G1 pool pin — pinned BEFORE looking [PROPOSED-ASM: ASM-1111]

Rule (ASM-1030 repo rule, instantiated): 20 primary + 5 backup repositories,
pinned by NAME AND ORDER in §2.1 below at design-pin time, from agent memory
of widely-used permissively-licensed (MIT/BSD/Apache/PSF) predominantly-
pure-Python libraries, DISJOINT from the G0 six (six, toml, python-tabulate,
bottle, more-itertools, click). Size band: analyzed `*.py` LOC in
[300, 120000] per repo, checked AFTER clone; a repo failing clone, license,
or band is replaced by the next unused backup in pinned order (mechanical,
logged in repos.lock.json). Clone = shallow at default branch HEAD; exact SHA
recorded. HONESTY: this is an agent-selected list, not a sample from a
defined population — every cross-repo band downstream is a resampling
sensitivity band, NEVER a generalization CI (the G0 discipline verbatim).
Analyzed scope: all `*.py` incl. tests, fail-closed [ASM-1051]; a
package-source-only slice is co-reported (where_defined dropped there, as in
G0, disclosed).

### 2.1 The pinned list (order = priority; no repo content seen at pin time)

Primary (1–20): psf/requests; pallets/jinja; pallets/markupsafe;
pallets/itsdangerous; python-attrs/attrs; GrahamDumpleton/wrapt;
dateutil/dateutil; pytest-dev/pluggy; pypa/packaging;
jawah/charset_normalizer; kjd/idna; pallets-eco/blinker; hukkin/tomli;
python-humanize/humanize; jd/tenacity; tkem/cachetools; micheles/decorator;
grantjenks/python-sortedcontainers; mahmoud/boltons; arrow-py/arrow.
Backups (21–25): marshmallow-code/marshmallow; jmespath/jmespath.py;
jquast/wcwidth; Suor/funcy; keleshev/schema.

## 3. Census + extraction [PROPOSED-ASM: ASM-1112]

- Census generator: the G0 `census.py` logic REUSED (extractor-independent,
  raw-bytes syntactic, ast.parse-as-tokenizer per ASM-1052), adapted ONLY in
  paths + seed. **G1 seed: 20260716** (fresh, pinned here). The census is
  generated and hashed BEFORE the extractor runs on the G1 pool (run
  ordering recorded in freeze-manifest.json; same filesystem-time-consistency
  limitation as G0, disclosed).
- Extractor: PY-STAT/1 **unchanged** — byte-identical
  `poc/codevert-g0/extractor.py` (sha pinned in the freeze manifest) +
  `engine.py` + `inventory.json`. No extractor edit of any kind (an edit
  would be an extractor version change per ASM-1031 and would void this run).
- κ_q^indep: computed over the FULL frozen census, per family × repo;
  primary aggregate = FL-4 (query-pooled + family-macro); callees_of and the
  three excluded families co-reported for disclosure. Repo-cluster bootstrap
  (seed 20260716, 10k resamples) = sensitivity band only.

## 4. Proxy-gold annotation [PROPOSED-ASM: ASM-1113/1114/1115/1116]

- **Sample [ASM-1114]:** 2 queries per (family × repo) cell over the 5
  measured families (FL-4 + callees_of slice) × 20 repos = **200 queries**,
  drawn seed-pinned (seed 20260716) from the frozen census universes; cells
  smaller than 2 take all and log the shortfall. A query whose context bundle
  exceeds the 120 KB cap is REPLACED by the next sampled index in that cell's
  pinned shuffle order (logged; never silently dropped).
- **Annotator A = "fable-a":** Claude-family subagents (one per repo),
  receiving ONLY: the pinned instruction doc (§4.1), the query list for that
  repo, and the mechanical context bundles. BLIND to all extractor/engine
  output (auditable: prompts are saved verbatim under annotation/prompts/).
- **Annotator B = "gpt56-b":** `gpt-5.6-sol` via pinned
  `npx -y @openai/codex@0.144.1 exec`, isolated per-call CODEX_HOME (auth
  copied, memories + web search disabled, `--ephemeral`, `-s read-only`),
  workdir = an out-of-repo temp dir containing ONLY that batch's context
  bundle. Reasoning effort **medium** — a pinned, DISCLOSED deviation from
  the judge-1p recipe's `low` (this is free-form code reading with set-valued
  output, not MCQ). One call per (repo × family) batch (2 queries/call).
  Output = JSON per the instruction doc; validity = parses + required keys;
  ≤2 content retries, then no-label (query leaves the gold denominator,
  counted; >10% no-label ⇒ instrument-invalid for that endpoint).
- **Blindness/independence:** neither annotator sees the other's answers or
  any extractor output; both receive byte-identical instruction docs and
  context bundles.
- **Agreement (reported RAW, pre-adjudication):** per-family exact-set
  agreement rate; element-level Jaccard; answerability agreement + Cohen's
  kappa. This is the inter-annotator agreement the maintainer asked for.
- **Adjudication [ASM-1113]:** disagreements adjudicated by the Fable main
  agent reading the same context (rationale logged per item in
  annotation/adjudication.jsonl). Adjudicated set = **PROXY GOLD**, tagged
  PROVISIONAL-ON-LLM-PROXY everywhere; it is void as evidence the moment a
  human Pass-B annotation of the same sample lands (the g3-humangold
  pattern).
- **Element normalization [ASM-1115]:** engine answers and gold are compared
  after pinned normalization — contains/contained_in and repo-internal
  callees: `relpath::qualpath` symbols (module target = `relpath`);
  imports_of: `repo:relpath` for repo-internal (WITH parent-package closure
  + self-edges per ASM-1058, stated in the instructions) and `ext:<base>`
  for external per the PY-STAT/1 emission rule (`import a.b`→`ext:a.b`,
  `from X import y` with X external→`ext:X`); where_defined: (relpath,
  lineno) sites, engine spans mapped to lines mechanically. callees_of
  precision/R_q are computed on REPO-INTERNAL elements only (external-callee
  naming is not reliably normalizable; disclosed).
- **Answerability + endpoints [ASM-1116]:** each annotator marks each query
  answerable-static yes/no + gold set (possibly empty) + conditional/lazy
  flags. On the adjudicated proxy gold: **precision** = element-level
  correctness of `proved` listings; **R_q** = fraction of gold-answerable
  queries returned `proved` with the FULL gold set; **negative-answer
  validity** = fraction of gold-EMPTY queries answered `proved`-empty.
  Floors quoted from ASM-1030 (κ_q^indep ≥ 0.5, R_q ≥ 0.90, precision
  ≥ 0.95, neg-validity ≥ 0.90) — the mechanical verdict is the
  COORDINATOR'S step; this run produces the verdict-INPUT only.

## 5. PY-STAT/2 spike (parallel, option C) [PROPOSED-ASM: ASM-1117/1118]

Scope pinned in poc/codevert-g1/pystat2-spike/ (D1 local-alias, D2
parametrized-decorator return analysis, D3 call-result return analysis;
candidates-only, NO proved upgrades; NON-SCORED; measured on the pinned G0
corpus against the FROZEN G0 census; probe re-check against saved traces as
the candidate-narrowing soundness guard). Any full PY-STAT/2 build is an
extractor version change per ASM-1031: new inventory, new census freeze, new
spike — the spike output is a build/no-build verdict-INPUT only.

## 6. PROPOSED-ASM block ASM-1110…ASM-1119 (doc note; coordinator registers)

| id | scope |
|---|---|
| ASM-1110 | CODEVERT-FL/1 = primary families {contains, contained_in, imports_of, where_defined}; callees_of = disclosed sensitivity slice; callers_of/imported_by/instance_of excluded from the re-scoped product claim (PY-STAT/2 territory); the maintainer-gloss vs G0-option-(a) family ambiguity resolved as pinned in §1 |
| ASM-1111 | G1 pool: the §2.1 pinned-before-looking 20+5 list, size band [300,120000] LOC, mechanical backup substitution, shallow-HEAD SHAs recorded; agent-selected disclosure; all-*.py analyzed scope + srconly co-report |
| ASM-1112 | G1 census = G0 census.py generator logic (content-hash-pinned) with seed 20260716; PY-STAT/1 byte-identical; FL-4 primary aggregate, all-8 co-report |
| ASM-1113 | Proxy gold: two LLM annotators (fable-a Claude-family, gpt56-b gpt-5.6-sol pinned invocation, effort medium disclosed), blind + independent, identical instructions; Fable adjudication with logged rationale; ALL gold-dependent endpoints PROVISIONAL-ON-LLM-PROXY, void on human re-annotation |
| ASM-1114 | Sample: 2 per (family × repo) cell, 5 families × 20 repos = 200, seed 20260716; 120 KB bundle cap with pinned replacement rule; no-label >10% per endpoint ⇒ instrument-invalid |
| ASM-1115 | Element normalization rules of §4 (symbols, import closure per ASM-1058, span→line mapping, repo-internal-only callee scoring) |
| ASM-1116 | Answerability protocol + endpoint definitions (precision / R_q / negative-answer validity) and the quoted ASM-1030 floors; verdict is the coordinator's mechanical step |
| ASM-1117 | PY-STAT/2-SPIKE scope: D1/D2/D3 bounded local dataflow, candidates-only, non-scored, G0 corpus + frozen census reuse |
| ASM-1118 | Spike metrics: '*'-mass conversion by mechanism, per-family κ recovery vs the G0 ablation ceiling, probe-trace candidate-narrowing exclusion count as soundness guard |
| ASM-1119 | Session governance: no git/bd/kb ops; no @-handle strings in artifacts; every measured number [MEASURED]; every gold-dependent number additionally PROVISIONAL-ON-LLM-PROXY; nothing here is a scored verdict — coordinator runs the mechanical verdict against the pinned floors |

## 7. Run ordering (recorded in freeze-manifest.json as executed)

1. hash this file + annotation-instructions.md (pre-clone manifest);
2. clone pool → repos.lock.json;
3. census_g1.py (seed 20260716) → results/census-g1.json + hash;
4. run_g1.py (PY-STAT/1 unchanged) → results/g1-metrics.json;
5. sample_builder.py → annotation sample + context bundles + prompts (no
   extractor output enters any bundle);
6. annotators A and B in parallel; raw agreement computed;
7. adjudication → proxy gold → endpoints; analysis JSON + report.
