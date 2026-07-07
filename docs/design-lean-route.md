# Mathlib/Lean extraction route — feasibility, sample, decision (rev 1)

**Status:** design record, 2026-07-07. Deliverable of bead `kernel-of-truth-vn8` (bulk-kernel wave A, "feasibility + sample only on this box").
**Author:** Mathlib-route agent (Claude Fable 5), for @jeswr.
**Companions:** docs/design-bulk-kernel.md (honesty architecture, provenance rule), docs/design-math-sector.md §1.2/§2.4 (why CIC/Lean was rejected as the profile-M *identity* substrate — this document takes that rejection as settled and asks what is honestly extractable anyway), data/math-lean-sample/ (the sample + extractor).
**Honesty contract:** [established] / [claimed] / [open]. All sizes/counts marked [measured] were taken empirically on 2026-07-07 from this box.

---

## 0. Summary of decisions

1. **Ingestion layer: formal reference records, not concept records.** Lean gives no canonical finite byte string stable under its own identity notion (§2); we therefore ingest at the **annotation layer** — `lean-ref/1` records anchored on `(mathlibCommit, fullyQualifiedName)`, minting **no** `urn:concept:` ids. Pretty-printed signatures and docstrings ride along as annotations only.
2. **Relation to profile-M: complementary bridge, not competing profile.** Metamath remains the identity-layer grounding (canonical token strings); Lean supplies breadth (315k+ declarations [measured]) as bridge targets and mapper/annotation material. A CIC competing profile stays mintable by anyone per gist §8; this programme does not need one and could not gate one honestly.
3. **Bulk route (future, rented box): ntp-toolkit `declarations` + `premises` + `imports` at a pinned Mathlib release.** JSON-native, richest field set, premise-level dependency edges. Est. ≤ half a day and single-digit dollars on a 16-vCPU/32 GB spot instance (§5).
4. **Toolchain-free fallback: streaming doc-gen4 crawl** (what the sample used) — works from any box including this one, but signature-layer only, HTML-fragile, and byte-archival of sources is the re-derivability cost (§5.2).
5. **Sample delivered:** 70 records from `Mathlib.Data.Nat.Basic` + `Mathlib.Data.Nat.GCD.Basic` at mathlib@`5c206a85`, deterministic extractor, 0/70 parse errors on manual review, six extraction issues documented (§4).

---

## 1. Route survey

All routes surveyed 2026-07-07. "No-toolchain?" = can extraction run on this box (2 cores, 3.5 GB free disk, no Lean) over plain HTTP.

| Route | What it is | Size | Freshness | Licence | Fields | No-toolchain? |
|---|---|---|---|---|---|---|
| **(a) doc-gen4 / mathlib4_docs** (leanprover-community.github.io/mathlib4_docs) | generated HTML docs for Mathlib + all deps; machine-readable indexes: `declarations/declaration-data.bmp` = **65.8 MB JSON** [measured] (`declarations` name→{kind, docLink}, `instances`, `instancesFor`, `modules` name→{importedBy, url} — a full module import DAG); `declarations/header-data.bmp` = **1.14 GB** [measured] (name→signature HTML); ~11,154 module HTML pages (8,245 Mathlib) [measured] | index 66 MB; headers 1.14 GB; full HTML crawl est. 0.6–1 GB | **rebuilt from master daily** (last-modified 2026-07-07 09:58 UTC [measured]); URLs un-versioned, mutate in place | Apache-2.0 (derived from mathlib4) | name, kind, module, pretty signature, docstring, attributes, source link **with commit+line span**, type-level reference links, module import graph. **No values/proof terms** (equation lemmas sometimes elided "due to their size" [measured]) | **Yes** — plain HTTPS; per-module pages are 30–100 KB |
| **(b) LeanDojo Benchmark 4** (Zenodo DOI 10.5281/zenodo.12740403, concept 10.5281/zenodo.8040109) | traced-corpus benchmark from mathlib4: 122,517 theorems/proofs, 259,580 tactics, 167,779 premises; premise corpus carries source text spans + file dependency graph; ASTs available via the tracing tool, not the benchmark tar | **70 MB tar.gz** [measured via Zenodo API] | **published 2024-07-14 — ~2 years stale** [measured]; fresh tracing requires LeanDojo + toolchain + big machine | **CC-BY-2.0** [measured] | theorem statements + proofs (source text), tactic steps with states, premise names + definitions-as-source-text, file deps | **Yes** for the published tar; **no** for re-tracing |
| **(c) lean4export** (leanprover/lean4export) | official kernel-level exporter: NDJSON format 3.1.0, interned Name/Level/Expr tables, declarations (axiom/def/theorem/opaque/quot/inductive/ctor/recursor) with **types and values as full kernel terms**, universe-explicit, de-Bruijn-resolved | old text-format Mathlib export was ~213 MB and took 13.5 GB RAM to import (rocq-lean-import figure); current NDJSON of Mathlib plausibly ~0.5–2 GB [claimed]; **no maintained published dump found** [established by search — Lean4Lean etc. each re-export locally] | as fresh as your checkout | Apache-2.0 | everything the kernel sees; nothing human-readable | **No** — needs Lean toolchain + Mathlib build/cache (tens of GB) |
| **(d) ntp-toolkit** (cmu-l3/ntp-toolkit) | extraction pipeline (`lake exe <tool>`): `declarations` emits per-decl `name, kind, type, typeArgs, typeBody, doc, signature, module, line, column, isProp, scope, src, isHumanTheorem`; also `premises` (constants used by each constant — proof-level dep edges), `imports`, tactic training data | full pipeline output for Mathlib is GB-scale; declarations-only est. 1–2 GB JSONL [claimed] | run at any pinned commit; published HF dumps (`l3lab/ntp-mathlib*`) are **tactic-prediction data, not the declarations output**, last touched 2024-09 [measured] | MIT (toolkit); output inherits mathlib Apache-2.0 | richest pretty-layer field set of any route; still **no canonical identity** (types are pretty-printed) | **No** — toolchain; README: ~2 h full pipeline on 14-core M3 Max |
| (extras) third-party HF dumps | `hcju/mathlibretrieval` (CC-BY-4.0), `FrenzyMath/mathlib_informal_v4.16.0` (Apache-2.0, informalisations, pinned v4.16.0), `pkuAI4M/extract_mathlib_v4_11_0_validated` (1–10 M rows), LeanExplore local DB (BM25+FAISS index incl. Mathlib, PhysLean; size/licence not established) | varies | all pinned to 2024–2025 Mathlib versions | varies | varies; mostly retrieval/informalisation-oriented | Yes, but stale + third-party provenance — **not suitable as a primary source** [claimed] |

Two structural facts worth recording: the mathlib4_docs GitHub repo is effectively empty (28 KB [measured]) — the site deploys via CI artifacts, so there is **no git-clone shortcut** to the docs; and `declaration-data.bmp` is served with `content-type: image/bmp` purely for compression reasons — it is plain JSON.

**Scale [measured, 2026-07-07 build]:** 415,840 declarations total in the docs index; 315,365 in Mathlib-proper modules; kinds: theorem 282,055 / def 76,529 / instance 38,526 / ctor 9,429 / structure 3,584 / class 2,447 / opaque 2,215 / inductive 975 / **axiom 80**.

---

## 2. The identity question — what Lean honestly lets us hash

design-math-sector §1.2/§2.4 rejected CIC as profile-M's basis because Lean's identity is **modulo definitional equality**. This section answers the follow-on question that decision left open: given identity-modulo-conversion, which layer of a Mathlib declaration can a content-addressed kernel ingest, and with what claim?

The layers, examined:

1. **Source text** (what LeanDojo/ntp-toolkit `src` capture). Authored and auditable, but meaningless outside its elaboration context (imports, `open` scopes, `variable` blocks, notation state) — the same bytes elaborate differently in different files, and different bytes elaborate identically. A hash of source-at-a-commit is a fine *provenance fingerprint*; as *concept identity* it is dishonest [claimed, decision-grade].
2. **Pretty-printed signature** (doc-gen4, ntp-toolkit `signature`/`type`). Human-auditable but a *rendering*: notation (`∣` hides `Dvd.dvd`), dot-notation (`c.lcm b` = `Nat.lcm c b`), implicit-binder display, and elaborator-generated names (`Sort u_1`, `Nat.instLinearOrder`) all vary across Mathlib/Lean/doc-gen4 versions with no change in meaning — all observed in the 70-record sample (§4). Hashing this mints identity out of pretty-printer settings.
3. **Kernel terms** (lean4export). Alpha is solved (de Bruijn bvars) and universes are explicit — but this is *still* not canonical for Lean's own identity notion: two byte-different kernel terms can be definitionally equal, and elaboration output for the *same source* changes meaning-neutrally across Lean versions (instance resolution, unfolding choices). Byte-hashing kernel terms is simultaneously **too fine** (splits defeq-equal declarations) and **unstable** (splits versions), and canonicalising modulo defeq means running conversion checking inside the mint gate — the trusted-base expansion §2.4 rejected. Terms are also enormous after elaboration. [established properties; claimed consequence]

**Conclusion [decision]:** there is no honest hash-boundary layer. What Lean *does* give us, robustly: the pair **(mathlibCommit, fullyQualifiedName)** as an unambiguous reference; kind; module; source span; docstring; pretty signature *as annotation*; type-level reference edges (from doc hyperlinks) and proof-level premise edges (ntp-toolkit); the module import DAG; alias/deprecation edges. So the ingestion class is:

> **`lean-ref/1` formal reference records** — annotation-layer, identity anchored on `(mathlibCommit, name)`, `status: "formal-reference"`, minting no `urn:concept:` ids, with every field outside any concept-hash boundary.

This is deliberately *below* AxiomsOnly on the bulk-kernel ladder: AxiomsOnly records still make a structural-axiom claim inside the concept space (WordNet's hypernym axioms fit profile shapes); a Lean type in CIC does not fit profile-M's closed FOL grammar at all, and pretending a pretty-string is an axiom would counterfeit exactly what the ladder exists to keep honest.

**Interaction with profile-M (gist §8):** complementary, not competing. Metamath grounds the identity layer (canonical, context-free token strings — the property Lean lacks by design); Lean supplies theorem-mass breadth and the names working mathematicians actually use. The bridge is `sameConceptAs`-style **signed annotations** from profile-M hashes to `(mathlibCommit, name)` anchors (e.g. `urn:math-v0:addition` ↔ `Nat.add`; the future Metamath-derived records ↔ set.mm labels ↔ Mathlib names give a three-way crosswalk, MathGloss-fashion). A CIC-based competing profile-M′ remains permissionlessly mintable by others; nothing here forecloses it — but its mint gate would have to carry a typechecker, and that is its problem, not ours.

---

## 3. Bulk-route decision

**Primary (rented box): ntp-toolkit `declarations` + `premises` + `imports` at a pinned Mathlib release tag.** Reasons: JSON-native (no HTML parsing fragility), the richest per-declaration field set (including `src`, `isProp`, `isHumanTheorem`), **proof-level premise edges** (doc-gen4 links give type-level edges only), and deterministic re-derivability from `(mathlib tag, toolkit commit, toolchain version)` — satisfying the bulk-kernel provenance rule without archiving GB of HTML.

**Fallback (any box, incl. this one): streaming doc-gen4 crawl** driven by `declaration-data.bmp` as the enumeration index — fetch each module page, parse (the sample extractor already does this), emit records, discard HTML. Transfer ~0.6–1 GB, disk footprint <100 MB streamed, CPU trivial; throttled + niced it fits this box in ~a day [claimed]. Honest weakness: full byte-archival of sources (~150–200 MB gzipped) is needed for byte-identical re-derivation, or we accept commit-pinned (not byte-pinned) provenance and record the doc-gen4 version — a documented deviation from the bulk provenance rule, mitigated by the fact that every record carries the mathlib commit from its gh_link.

**Rejected as primary:** LeanDojo Zenodo tar (70 MB, CC-BY-2.0 — cheapest structured dump, but 2 years stale and proof/tactic-oriented; reconsider only if tactic data becomes a requirement); lean4export (kernel layer — wrong identity discipline per §2, no published dump, toolchain + 13.5 GB-RAM-class import); third-party HF dumps (stale pins, third-party provenance).

---

## 4. Sample findings (data/math-lean-sample/)

**70 records** — `Mathlib.Data.Nat.Basic` (18) + `Mathlib.Data.Nat.GCD.Basic` (52) at mathlib@`5c206a857e6422127e45b8823dd256e1b69918da`, extracted by a zero-dep deterministic Node extractor from committed byte snapshots (the docs URLs are un-versioned, so snapshots are the archival source). Two consecutive runs byte-identical; all 70 reviewed manually, **0 parse errors**.

Issues found (full list with exhibits in `data/math-lean-sample/README.md`):

1. pretty types hide head constants behind notation and dot-notation (`a ∣ c.lcm b`); the hyperlinks recover them (`referencesPretty`), the string doesn't;
2. elaborator-generated names leak: auto-bound universes (`Sort u_1`), machine-named instances (`Nat.instLinearOrder`);
3. alias records duplicate meaning under different names — including a kind flip (`Nat.Coprime.symmetric`, a *theorem*, aliases `Nat.Coprime.stdSymm`, an *instance*);
4. values/proofs absent at this layer; even equation lemmas get elided "due to their size";
5. un-versioned source URLs — byte snapshots required for re-derivability;
6. HTML flattening is genuinely fiddly (inline vs block tags, entities) — a real cost the JSON-native primary route avoids.

Docstring coverage in the sample: 7/70 (10%) — consistent with Mathlib lemma files; docstrings will be sparse at bulk scale [claimed].

---

## 5. Cost/size estimate for full ingestion

### 5.1 Primary route (ntp-toolkit, rented box)

- **Machine:** 16 vCPU / 32 GB RAM / 100 GB disk cloud instance (Mathlib `lake exe cache get` pulls a multi-GB olean cache and the checkout + toolchain want tens of GB; 32 GB RAM clears the known 13.5 GB-class import peaks with slack).
- **Time:** cache download ~15–30 min; extraction ~2 h on a 14-core M3 Max per the toolkit README → est. **3–6 h wall** on x86 spot [claimed].
- **Cost:** ≈ **US$5–15** spot.
- **Output:** 315,365 Mathlib declarations (+ ~100k dependency declarations if wanted); raw declarations JSONL est. 1–2 GB; filtered `lean-ref/1` records est. **300–500 MB JSONL (~100–200 MB gzipped)** [claimed]. Premise-edge files add a comparable amount.
- **This box's role:** none for extraction; post-processing the gzipped output into records would fit if streamed, but the rented box should just emit final records.

### 5.2 Fallback route (doc-gen4 crawl)

~8,245 Mathlib module pages, ~0.6–1 GB transfer, <1 day niced on this box, <100 MB working disk streamed, plus ~150–200 MB gzipped HTML archive if byte-provenance is kept (recommended). Signature-layer fields only.

### 5.3 Refresh policy

Re-ingestions are new snapshots per bulk-kernel governance; `declaration-data.bmp` (66 MB, daily) is the cheap diff/freshness index — name-set deltas between builds identify what a re-ingestion would touch without a full crawl [claimed].

---

## 6. Follow-ups filed

1. **Bulk lean-ref ingestion via ntp-toolkit on a rented box** (blocked on machine budget): pinned Mathlib release tag, `declarations`+`premises`+`imports`, emit `lean-ref/1` records + premise-edge sidecar, deterministic re-derivation statement, ≥100-record manual sample per the bulk verification bar.
2. **Bridge annotations profile-M ↔ Mathlib** (small, unblocked): `sameConceptAs`-style annotations from the 39 `data/math-v0/` records to `(mathlibCommit, name)` anchors where honest counterparts exist (`Nat.add`, `Nat.gcd`-adjacent order/divisibility material...), with per-link confidence notes; design the annotation record shape once, reuse for the future Metamath↔Lean crosswalk.

---

*Primary sources: leanprover-community.github.io/mathlib4_docs (+ `declarations/declaration-data.bmp`, `header-data.bmp` [measured 2026-07-07]); github.com/leanprover/doc-gen4; Zenodo records 8040109/12740403 (LeanDojo Benchmark 4, CC-BY-2.0) + leandojo.org + github.com/lean-dojo/LeanDojo; github.com/leanprover/lean4export (`format_ndjson.md`, format 3.1.0) + github.com/rocq-community/rocq-lean-import (213 MB / 13.5 GB RAM figures) + arXiv:2403.14064 (Lean4Lean); github.com/cmu-l3/ntp-toolkit + huggingface.co/datasets/l3lab/ntp-mathlib*; huggingface.co dataset API [measured 2026-07-07]. Local: docs/design-bulk-kernel.md, docs/design-math-sector.md §1–§2, data/math-lean-sample/.*
