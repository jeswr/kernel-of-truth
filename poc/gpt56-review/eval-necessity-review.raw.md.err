OpenAI Codex v0.144.1
--------
workdir: /home/ec2-user/.codex-review-homes/workdir.r5NoNi
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f4a0f-e95f-7472-8878-c18eb167b18f
--------
user
# Kernel of Truth — external review: is custom eval data necessary, or should we use standard benchmarks?

> **REVIEWER FRAMING.** You are **GPT-5.6-sol**, an external methodology reviewer.
> The maintainer has one specific question and WANTS an honest answer that may
> well be "use a standard benchmark instead": for each of three newly-designed
> experiments that build BESPOKE eval data, is that custom data actually
> NECESSARY, or would an existing, off-the-shelf benchmark substitute or
> supplement it? Be candid and specific. Do not hedge toward "custom is always
> better" — the programme has a known, documented weakness (self-authored
> evals inflating results) and the maintainer's prior is that standard
> benchmarks are preferable wherever they are credible substitutes.
> This packet is self-contained: you have no access to the repository, only
> what is quoted or described below. Where you cite external benchmarks/papers,
> flag your confidence (citations get independently verified afterward).

---

## 1. Programme context (minimum needed to judge fit)

The "kernel" is a set of canonical, deterministic, training-free concept vectors
built from ~65 semantic primes in the Natural Semantic Metalanguage (NSM)
tradition (Wierzbicka/Goddard). Concepts are authored as reductive-paraphrase
explications over the primes; a deterministic encoder turns an explication into
a fixed vector; a `kot-axiom` engine is a deterministic rules engine (closed
query grammar: `unique`/`lookup`/`count`/`instance`) that answers covered
queries from explicit records and refuses (typed `ERR_*`) anything it cannot
ground. No RDF/OWL/SHACL/description-logic legacy is imported — the formalism
is native (this bars swapping in semantic-web benchmarks/ontologies as a
"standard benchmark" substitute; that is out of scope by design directive, not
an oversight).

Two value theses, always measured together: (A) correctness — does the kernel
make a model more accurate/correct at matched budget; (B) efficiency — does it
cut params/memory/compute at matched-or-better accuracy. All three experiments
below are marked `efficiency_relevant: false` in the registry — they are
correctness/instrument-validity experiments, not efficiency measurements.

**The known, documented weakness (why this review exists).** As of this
programme's own cross-experiment synthesis (2026-07-10):

> "Across the entire frozen registry there are ZERO audited end-task wins over
> the kernel-as-text null... every end-task-adjacent verdict is either R0 (no
> host model), a landed FAIL, or a PASS confined to **a self-authored
> oracle-favourable slice**."

That is: the programme's only positive end-task result (a separate experiment,
"f2b-replicate/f2b-transfer", not reviewed here directly) is adjudicated on
items and gold labels the programme itself authored, using a verifier that is
string-equality against the programme's own canonical records. The maintainer
is explicitly worried this pattern — build the eval, build the gold, build the
grader, all from the same kernel — could be repeating itself in the three NEW
experiments below, and wants to know, per experiment, whether a real
independent benchmark should replace or supplement the home-grown one.

**The coverage finding (why "just use a standard benchmark" isn't automatically
free either).** A separate measurement (`m0b`, audit-confirmed) found that the
kernel's authored vocabulary reaches only **0.3542 of content-word mass on the
single friendliest measured corpus** (a children's-story corpus, at its most
lenient matching rung), with a stricter reachable-and-checkable band far lower,
and — critically — **this number is corpus-indexed and does NOT transfer**: it
describes one corpus, one kernel snapshot, one matching rule, and licenses
nothing about any other text. In plain terms: the kernel's authored concepts
(kinship terms, a couple hundred lexical glosses, etc.) are a small, narrow,
hand-picked island inside natural language. This matters for today's question
because it means the honest failure mode is symmetric: custom evals risk
self-authoring bias, but *most* standard benchmarks are built for open-domain
natural language and may simply not touch the narrow slice of concepts the
kernel actually has authored — in which case a standard benchmark would not be
measuring the kernel at all (a null instrument), not a stronger one.

---

## 2. The three experiments and their custom eval materials

### 2.1 nsk1 — "kernel-powered neurosymbolic internals" (the flagship line)

**What it tests.** Whether patching a symbolic engine's answer INTO a
language model's hidden activations (mid-forward-pass, via cached
"steering-vector" injection) beats giving the model the identical engine
answer as ordinary appended TEXT, at a matched extra-token budget. Two small
open-weight hosts (SmolLM2-135M, 360M). The task family used to drive this
comparison is 2-hop relational-composition question answering: *"Who is the
mother of the father of X?"* over a synthetic kinship graph.

**The custom eval — `data/nsk1-eval/`** (newly built for this experiment,
digest-pinned, zero prior use):

- `items.jsonl` — 1,100 items (1,000 "covered" 2-hop questions + 100
  "uncovered" control questions). Generated by a seeded, deterministic Python
  script (`poc/nsk1/gen_nsk1_corpus.py`) from 140 synthetic 3-generation
  families using invented surname-pair names (e.g. "Voss-Voss", "Galt-Harrow").
  Sample covered item:
  ```
  context: ["The mother of Sten Voss-Voss is Xena Voss-Voss.",
            "The father of Rurik Voss-Voss is Sten Voss-Voss.", ...12 more distractor facts...]
  question: "Who is the mother of the father of Rurik Voss-Voss?"
  gold_surface: "Xena Voss-Voss"
  hop1_bridge: "Sten Voss-Voss" (the engine resolves only this hop; gold is hop-2, held out of the engine's view)
  ```
  Sample uncovered/control item (relation "teacher" is out of kernel scope, or
  entity is unknown):
  ```
  question: "Who is the teacher of the father of Sanna Jasper-Norwin?"
  gold_entity: null   (correct behaviour is abstention)
  ```
- `world.jsonl` — 2,240 flat fact records (`kot-world/1` schema) backing the
  contexts: entity `n00001` `is-a` "man"/"woman" class, etc.
- `lexicon.json` — ~68 KB closed exact-match surface-form table (every
  entity's one canonical printed name, e.g. `"urn:kotw:v0:nsk1-alvar-brant-brant": "Alvar Brant-Brant"`) — the model's hidden-state decode is exact-string-matched against this closed list (no similarity search allowed anywhere in this design: "X3 cosine ban").
- `axioms/` — three tiny hand-authored axiom files: `class-man.json` (man/woman
  disjointness), `rel-father.json`, `rel-mother.json` (each: functional +
  range constraint). This is the ENTIRE domain theory: two relations, two
  classes, no other content.

  In short: this is a **synthetic family-tree, 2-hop kinship-relation
  composition QA corpus with a closed lexicon**, built with invented names and
  a generator script, structurally the classic "compositional relational
  reasoning over a synthetic family graph" task shape — note explicitly that
  the domain (mother/father/man/woman, k=2 hops, distractor facts in context)
  is essentially the same task shape as **CLUTRR** (Compositional Language
  Understanding and Text-based Relational Reasoning, Sinha et al. 2019), which
  is exactly a synthetic-kinship-graph, k-hop relation-composition benchmark
  with distractor facts, publicly available, with an established k-hop
  difficulty ladder and existing baseline numbers in the literature.

- Reused across both design docs and eval: `mother-of`, `father-of`, `man`,
  `woman` are the SAME already-minted kernel concepts used elsewhere in the
  programme (not new authoring for this experiment) — the corpus is new, the
  concept vocabulary is not.

### 2.2 truthstyle-2x2 — truth × style adjudication probe

**What it tests.** Whether an NSM-shaped (kernel-style) definition surface,
versus a plain-English paraphrase of THE SAME content, biases an LLM judge's
accept/reject decision independent of whether the definition is actually
correct. This exists to sanity-check a DIFFERENT experiment's (f2b-transfer's)
judge-based scoring — i.e. it is itself a validity-of-instrument probe, not a
kernel-capability claim.

**The custom eval — `data/d-ts/items.jsonl`** (808 items, deterministically
built, zero LLM authorship anywhere in the corpus):

- **Tier 2 (PRIMARY, 100 concepts × 4 cells = 400 items):** the kernel's own
  100 covered concepts. "nsm" pole = the literal canonical NSM gloss bytes the
  kernel already uses; "plain" pole = a rule-based lexical substitution of the
  same gloss into more ordinary wording. "Wrong" cells swap in a
  length-matched, non-corresponding gloss from a different concept (a cyclic
  shift, so it's a real, if wrong, definition, not gibberish).
  Sample item (truth=correct, style=plain, concept="condolence"):
  ```
  definition: "the thing is words; a person says them to another a person who
  is grieving; the person says them because the person doesn't want the other
  a person to feel something bad for a long time."
  question: "Does this definition correctly give the meaning of the word
  'condolence (the words)' as ordinarily understood? ... Answer: yes/no/cannot-say."
  ```
- **Tier 1 (INSTRUMENT/diagnostic only, 96 words × 4 cells = 384 items):**
  ordinary WordNet 3.1 dictionary glosses (`data/lexical-wn31/`), same 2×2
  truth/style crossing, used ONLY to check that judges can tell own-gloss from
  swapped-gloss on kernel-FREE ground (a sanity floor), not as an endpoint.
- Judge pool: 3 pinned LLMs (GPT-5.6-Sol, GPT-5.5, Claude Haiku 4.5),
  stateless, blind to truth/style/tier labels, 2,424 total invocations,
  budget cap $40, no GPU.

  In short: this is a **binary-acceptance judgment task over paired
  correct/incorrect, two-register (formal-metalanguage vs plain) definitions
  of a word/concept**, i.e. structurally: (a) a WORD-SENSE / DEFINITION
  correctness-judgment task (adjacent to WiC — Word-in-Context — and to
  dictionary-definition/lexical-entailment tasks built from WordNet glosses),
  and (b) — arguably the closer match — an **LLM-judge robustness-to-surface-
  form probe** (adjacent to the "LLM-as-judge" bias literature: position bias,
  verbosity/fluency bias, style-over-substance bias in automatic evaluators;
  e.g. instruction-following judge-robustness benchmarks that construct
  outputs which "look" high quality but are substantively wrong, to test
  whether a judge can be fooled by surface polish).

### 2.3 f2b-errors — pre-frozen failure-cause taxonomy

**What it is.** NOT new eval items. It is a CLOSED six-category failure
taxonomy (`X-EXTRACT`, `X-NONENGAGE`, `X-GOLDCONFLICT`, `X-EXHAUST-STABLE`,
`X-EXHAUST-WANDER`, `X-OTHER≤2%`) plus a deterministic assignment tree, applied
retrospectively to failure cells from a DIFFERENT already-existing experiment's
run logs (`f2b-transfer` Stage-2: SmolLM2-135M, a verify-and-retry loop, k=4
attempts, existing `data/d-qa-t` items, ~250 eval items over ~108 concepts).
It also declares a concept-cluster bootstrap re-analysis (resampling by concept
to price pseudo-replication: 250 items over 108 concepts × 4 templates are not
250 independent statistical units). No model is run, no GPU is spent
($0, CPU, minutes); its only "custom" artifact is the **category schema**
(`poc/f2b-errors/taxonomy.json`) — a hand-authored ontology of what can go
wrong in THIS pipeline (a string-equality verifier with an abstain option and
bounded retries), tailored explicitly to this pipeline's own mechanics (the
design doc is explicit that generic mapper/axiom/ambiguity categories from a
prior GPT-5.6 proposal were REJECTED as not describing this pipeline, which
has no mapper or axiom-resolution stage).

The question for this artifact is therefore narrower and different in kind
from the other two: not "should the eval items be swapped for a benchmark"
(there are no new eval items), but "should the failure-CATEGORY SCHEME be
adopted from an existing, established error/failure taxonomy instead of
hand-authored from scratch" — e.g. process-reward/step-verification literature
(ProcessBench's error-localization categories, PRM800K's step-label taxonomy),
RAG/tool-use failure-mode taxonomies, or hallucination-taxonomy literature
(HaluEval's category set), any of which might offer a validated, reusable
category scheme instead of a bespoke one.

---

## 3. What we want from you

For EACH of the three experiments (nsk1, truthstyle-2x2, f2b-errors),
answer, in order:

**(1) Is the custom eval NECESSARY, or could an existing out-of-the-box
benchmark substitute or supplement it?** Name SPECIFIC current benchmarks (not
just families) and assess the fit concretely — what would transfer cleanly,
what would need adaptation, what would be lost. Consider explicitly, where
relevant to the task shape (add others you know of that fit better; these are
starting candidates, not a required list):
   - relational/multi-hop reasoning: **CLUTRR** (note: nsk1's own
     father/mother/man/woman axioms and synthetic-family-graph shape look like
     a close structural match — assess directly whether nsk1 could run ON
     CLUTRR's public data instead of, or in addition to, the bespoke
     `nsk1-eval` corpus, and what would have to change: e.g. CLUTRR's relation
     vocabulary vs the kernel's covered {mother, father, man, woman} slice)
   - word-sense / lexical tasks: **WiC** (Word-in-Context)
   - NLI/entailment: **MNLI**
   - definitional/lexical-acceptability: **WordNet-derived gloss tasks,
     BLiMP**
   - commonsense QA: **CommonsenseQA, ARC**
   - compositional generalization: **COGS, SCAN**
   - knowledge editing: **CounterFact, zsRE**
   - factuality/hallucination: **TruthfulQA, FActScore, HaluEval**
   - process/verifier reward and step-level error taxonomies:
     **ProcessBench, PRM800K, GSM8K**
   - general leaderboard sets: **MMLU** or similar
   - (for f2b-errors specifically) any established **LLM-judge bias /
     judge-robustness benchmark** for the truthstyle-2x2 case, and any
     established **failure/error-taxonomy** for process-verification pipelines
     for the f2b-errors case.

**(2) Does each custom eval risk SELF-AUTHORING BIAS**, given the programme's
own documented confound (the ONLY positive end-task result to date is
"a PASS confined to a self-authored oracle-favourable slice" — items, gold,
AND grader all built by the same programme from the same kernel)? Be concrete
about the causal channel in EACH experiment specifically (e.g.: who wrote the
gold label, who wrote the item, who wrote the grader/verifier, and do any two
of those three share authorship/provenance in a way that could inflate a
result).

**(3) Where standard benchmarks genuinely CANNOT test the kernel's specific
covered concepts, say so explicitly** — this is the niche-coverage mismatch:
the kernel's authored vocabulary is measured at only ~0.35 of content-word
mass on the single friendliest natural corpus tested (and that number is
corpus-indexed, does not transfer, and is itself a crude vocabulary-membership
lower bound, not a semantic-coverage number). Standard benchmarks are built
for open natural language and may have near-zero overlap with the kernel's
actual covered slice (e.g. does CLUTRR's relation set — likely broader kinship
terms: uncle, cousin, grandmother, sister-in-law, etc. — even overlap with the
kernel's currently-covered {mother, father, man, woman}, or would most of
CLUTRR simply be "uncovered" by construction, making it an equally narrow
substitute rather than a broader one?). Where this mismatch is real, say
plainly that custom eval is justified BECAUSE of it — do not manufacture a
benchmark-swap recommendation where the benchmark would not actually exercise
what the experiment needs to measure.

**Per-experiment recommendation.** For each of the three, give ONE clear
verdict: **SWAP** to a named benchmark (say which, and what changes),
**SUPPLEMENT** with a named benchmark (custom eval stays primary/necessary,
benchmark adds a corroborating or generalization data point — say which
result it would strengthen and why the custom eval alone doesn't clear the
self-authoring worry), or **JUSTIFIABLY KEEP custom, no swap** (say exactly
why standard benchmarks fail here — niche-coverage mismatch, structural
mismatch, or a real methodological reason the custom design is doing something
no existing benchmark does).

Be candid and specific. The maintainer wants to use standard benchmarks where
they are credible — do not default to defending the custom design; if a real
benchmark is a better or equally good instrument for less bespoke-authoring
risk, say so plainly and recommend the swap.

**How to structure your answer:** one section per experiment (nsk1,
truthstyle-2x2, f2b-errors), each with the three numbered sub-answers above and
a one-line verdict at the top of the section. Close with a short cross-cutting
paragraph: does the SAME self-authoring risk show up differently across the
three, and is there a single common cheap step (e.g. one shared external
benchmark, or one shared disclosure practice) that would de-risk all three at
once?

warning: Codex could not find bubblewrap on PATH. Install bubblewrap with your OS package manager. See the sandbox prerequisites: https://developers.openai.com/codex/concepts/sandboxing#prerequisites. Codex will use the bundled bubblewrap in the meantime.
codex
I’ll verify the named benchmarks against primary papers or official repositories, then separate structural fit from provenance independence. My key test will be whether a benchmark can preserve each experiment’s actual intervention and estimand, not merely resemble its topic.
web search: 
web search: CLUTRR benchmark official paper relation vocabulary kinship k-hop github ...
web search: 
web search: site:arxiv.org ProcessBench identifying process errors mathematical reasoning official ...
web search: 
web search: WiC Word-in-Context benchmark official paper same meaning two contexts ...
web search: 
web search: 
web search: 
web search: 
web search: 
web search: https://raw.githubusercontent.com/facebookresearch/clutrr/main/clutrr/store/relations_store.yaml
web search: 
web search: site:github.com/facebookresearch/clutrr "relation_types" "grandfather" ...
web search: 
web search: 'SOS-Bench'
web search: 
web search: HaluEval benchmark official paper hallucination types question answering dialogue summarization ...
codex
The fit is already diverging across the three. CLUTRR is close enough to be a real replacement candidate for nsk1 if its original graph/proof provenance and labels are preserved; judge benchmarks can only calibrate truthstyle’s judges, not reproduce its NSM-specific factorial contrast; process-verification taxonomies do not describe f2b’s retry/verifier mechanics.
