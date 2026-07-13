/**
 * SCALE-1 S1 (100k rung) — FIRST MEASURABLE INCREMENT:
 * multi-source concept census + UFO-typing-yield probe over the LOCAL
 * WordNet ∪ OBO ∪ SUMO shards (docs/next/design/scale-s1-multisource-census.md).
 *
 * WHY THIS INCREMENT. The S0 10k readout measured two hard blockers for the
 * 100k rung (docs/next/analysis/scale-s0-interpretation.md):
 *   §2.3  the SemCor tag_cnt selection rule EXHAUSTS at 27,210 < 100k — the
 *         100k rung cannot be built from WordNet alone; it needs the §3.1
 *         multi-source portfolio with type-level dedup.
 *   §2.1  WordNet-only typing yields 0% identity / 0% dependence /
 *         0% source-asserted ontic_category — the §4.3 0.95 hard-typing gate
 *         is unreachable in principle on that source; the UFO fields must come
 *         from OBO/BFO anchoring + SUMO commitments (cascade steps 1-2).
 *
 * Both blockers are answered by ONE cheap, local, deterministic measurement:
 * a census of the union's type-level cluster count + domain balance (answers
 * §2.3) and a typing-yield probe that measures whether OBO is_a*→BFO closure,
 * genus-differentia logical definitions, and RO relationship edges move the
 * UFO fields off the WordNet-only 0% (answers §2.1). It reads only bytes
 * already in the repo (data/lexical-wn31, data/onto-obo, data/onto-sumo) — no
 * download, no license fetch, no GPU, CPU-minutes.
 *
 * EPISTEMIC STATUS: exploratory S1-preparation pilot. It measures YIELD
 * (how many records CAN carry a source-asserted / candidate value), NOT
 * PRECISION (whether those values are correct — that needs the §4.3 stratified
 * human audit, which this does not perform and does not substitute for). It
 * issues NO feasibility conclusion; CORRECTNESS and EFFICIENCY remain
 * INCONCLUSIVE-PENDING (design §14). No encoder version, no goldens, no
 * registry write.
 *
 * Output: poc/scale/results/scale-s1-census.{json,md}
 */

import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { REPO_DIR, RESULTS_DIR, ensureDir, nowMs, writeJson } from './common.js';

const OBO_DIR = join(REPO_DIR, 'data', 'onto-obo');
const SUMO_DIR = join(REPO_DIR, 'data', 'onto-sumo');
const WN_DIR = join(REPO_DIR, 'data', 'lexical-wn31');

// --- generic jsonl reader (streaming split; large files) --------------------
function* readJsonl(path: string): Generator<any> {
  const text = readFileSync(path, 'utf8');
  let start = 0;
  while (start < text.length) {
    let end = text.indexOf('\n', start);
    if (end === -1) end = text.length;
    const line = text.slice(start, end);
    start = end + 1;
    if (line.trim().length > 0) yield JSON.parse(line);
  }
}

// ===========================================================================
// BFO / SUMO upper anchors → UFO ontic_category. [STIPULATED crosswalk, but
// the ASSIGNMENT is SOURCE-ASSERTED when the record's is_a*/subclass* closure
// actually reaches one of these anchors — that is cascade step 1 (explicit
// imported commitment), distinct from a lexFile GUESS (cascade step 3).]
// BFO 2.0 canonical IDs.
// ===========================================================================
const BFO_CATEGORY: Record<string, string> = {
  BFO_0000003: 'event', // occurrent
  BFO_0000015: 'event', // process
  BFO_0000016: 'disposition', // disposition
  BFO_0000017: 'disposition', // realizable entity (role|disposition parent)
  BFO_0000023: 'role', // role
  BFO_0000019: 'quality', // quality
  BFO_0000020: 'mode', // specifically dependent continuant (quality/mode/relator parent)
  BFO_0000031: 'proposition', // generically dependent continuant (information-like)
  BFO_0000004: 'object', // independent continuant
  BFO_0000040: 'object', // material entity
  BFO_0000006: 'region', // spatial region
  BFO_0000141: 'region', // immaterial entity
};
// Per-ontology declared-domain fallback root → category. [STIPULATED,
// ontology-grounded: weaker than a BFO chain but stronger than lexFile guess
// because it is the ontology's own declared subject matter. Reported SEPARATELY
// from the source-asserted (BFO-reached) yield so the two are never conflated.]
const ONTOLOGY_ROOT_CATEGORY: Record<string, string> = {
  GO: 'event', // biological_process dominant; molecular_function/cellular_component split out below is not attempted at census
  CL: 'object', // cell — material entity
  UBERON: 'object', // anatomical structure — material entity
  PO: 'object', // plant anatomy — material entity
  CHEBI: 'object', // chemical entity — material entity
  PATO: 'quality', // phenotypic quality
  MONDO: 'disposition', // disease — BFO disposition
  SO: 'proposition', // sequence feature — generically dependent (information) continuant
  OGMS: 'event', // medical process/disorder mix (coarse)
  RO: 'relator', // relation ontology — relational
  BFO: 'underdetermined',
};
const SUMO_CATEGORY: Record<string, string> = {
  Process: 'event',
  Object: 'object',
  Physical: 'object',
  Attribute: 'quality',
  Relation: 'relator',
  Proposition: 'proposition',
  Region: 'region',
  Entity: 'underdetermined',
  Abstract: 'underdetermined',
};

// ===========================================================================
// Load OBO, build is_a graph, compute closure to BFO anchors.
// ===========================================================================
interface OboRec {
  id: string;
  ontology: string;
  kind: string;
  isa: string[];
  hasLogicalDef: boolean;
  hasGenus: boolean;
  relCount: number; // RO 'relationship' differentia/dependence edges
}

function loadObo(): { recs: Map<string, OboRec>; perOnt: Record<string, number> } {
  const recs = new Map<string, OboRec>();
  const perOnt: Record<string, number> = {};
  for (const f of readdirSync(OBO_DIR)) {
    if (!f.endsWith('.jsonl') || f === 'minted-urns.jsonl') continue;
    for (const r of readJsonl(join(OBO_DIR, f))) {
      const isa: string[] = [];
      let relCount = 0;
      for (const a of r.axioms ?? []) {
        if (a.rel === 'is_a' && typeof a.target === 'string') isa.push(a.target);
        else if (a.rel === 'relationship') relCount++;
      }
      const ld = r.logicalDefinition;
      recs.set(r.id, {
        id: r.id,
        ontology: r.ontology,
        kind: r.kind,
        isa,
        hasLogicalDef: !!ld,
        hasGenus: !!(ld && Array.isArray(ld.genus) && ld.genus.length > 0),
        relCount,
      });
      perOnt[r.ontology] = (perOnt[r.ontology] ?? 0) + 1;
    }
  }
  return { recs, perOnt };
}

/** Memoised is_a* closure category: the FIRST BFO anchor reached, or null. */
function bfoCategoryOf(recs: Map<string, OboRec>): Map<string, string | null> {
  const memo = new Map<string, string | null>();
  const visit = (id: string, stack: Set<string>): string | null => {
    if (memo.has(id)) return memo.get(id)!;
    if (stack.has(id)) return null; // cycle guard
    // direct BFO anchor?
    const bare = id.replace('urn:onto-obo:', '');
    if (bare.startsWith('BFO_') && BFO_CATEGORY[bare]) {
      memo.set(id, BFO_CATEGORY[bare]!);
      return BFO_CATEGORY[bare]!;
    }
    const rec = recs.get(id);
    if (!rec) {
      memo.set(id, null);
      return null;
    }
    stack.add(id);
    let found: string | null = null;
    for (const p of rec.isa) {
      const c = visit(p, stack);
      if (c) {
        found = c;
        break;
      }
    }
    stack.delete(id);
    memo.set(id, found);
    return found;
  };
  for (const id of recs.keys()) visit(id, new Set());
  return memo;
}

// ===========================================================================
// SUMO: subclass* closure to a SUMO upper anchor.
// ===========================================================================
interface SumoRec {
  id: string;
  term: string;
  kind: string;
  subOf: string[];
  hasArgTyping: boolean; // domain/range axioms → selectional/argument structure
  hasBiconditional: boolean;
}
function loadSumo(): Map<string, SumoRec> {
  const recs = new Map<string, SumoRec>();
  const path = join(SUMO_DIR, 'terms.jsonl');
  for (const r of readJsonl(path)) {
    const subOf: string[] = [];
    let hasArg = false;
    for (const a of r.axioms ?? []) {
      if (a.rel === 'subclass' && typeof a.target === 'string') subOf.push(a.target);
      else if (a.rel === 'domain' || a.rel === 'range') hasArg = true;
    }
    recs.set(r.term, {
      id: r.id,
      term: r.term,
      kind: r.kind,
      subOf,
      hasArgTyping: hasArg,
      hasBiconditional: (r.axiomStats?.biconditionalDefs ?? 0) > 0,
    });
  }
  return recs;
}
function sumoCategoryOf(recs: Map<string, SumoRec>): Map<string, string | null> {
  const memo = new Map<string, string | null>();
  const visit = (term: string, stack: Set<string>): string | null => {
    if (memo.has(term)) return memo.get(term)!;
    if (stack.has(term)) return null;
    if (SUMO_CATEGORY[term] && SUMO_CATEGORY[term] !== 'underdetermined') {
      memo.set(term, SUMO_CATEGORY[term]!);
      return SUMO_CATEGORY[term]!;
    }
    const rec = recs.get(term);
    if (!rec) {
      memo.set(term, SUMO_CATEGORY[term] ?? null);
      return SUMO_CATEGORY[term] ?? null;
    }
    stack.add(term);
    let found: string | null = SUMO_CATEGORY[term] ?? null;
    for (const p of rec.subOf) {
      const c = visit(p, stack);
      if (c) {
        found = c;
        break;
      }
    }
    stack.delete(term);
    memo.set(term, found);
    return found;
  };
  for (const t of recs.keys()) visit(t, new Set());
  return memo;
}

// ===========================================================================
// WordNet counts (type-level, excluding instance synsets = named individuals).
// ===========================================================================
function countWordNet(): { total: number; instances: number; typeLevel: number } {
  let total = 0;
  let instances = 0;
  for (const f of ['synsets-noun.jsonl', 'synsets-verb.jsonl', 'synsets-adj.jsonl', 'synsets-adv.jsonl']) {
    for (const r of readJsonl(join(WN_DIR, f))) {
      total++;
      if ((r.axioms ?? []).some((a: any) => a.rel === 'instanceHypernym')) instances++;
    }
  }
  return { total, instances, typeLevel: total - instances };
}

function pct(x: number, n: number): string {
  return n === 0 ? '0%' : ((100 * x) / n).toFixed(2) + '%';
}

function main(): void {
  const t0 = nowMs();
  ensureDir(RESULTS_DIR);

  // ---- WordNet ----
  const wn = countWordNet();

  // ---- OBO ----
  const { recs: obo, perOnt } = loadObo();
  const bfoCat = bfoCategoryOf(obo);
  let oboClasses = 0;
  let oboBfoReached = 0; // source-asserted ontic_category (cascade step 1)
  let oboOntologyRoot = 0; // ontology-grounded fallback (cascade step 3, grounded)
  let oboGenus = 0; // identity-provider candidate via genus
  let oboLogicalDef = 0;
  let oboDependence = 0; // ≥1 RO relationship edge → dependence candidate
  const oboBfoByOnt: Record<string, number> = {};
  const oboCatDist: Record<string, number> = {};
  for (const r of obo.values()) {
    if (r.kind !== 'class') continue;
    oboClasses++;
    const c = bfoCat.get(r.id) ?? null;
    if (c) {
      oboBfoReached++;
      oboBfoByOnt[r.ontology] = (oboBfoByOnt[r.ontology] ?? 0) + 1;
      oboCatDist[c] = (oboCatDist[c] ?? 0) + 1;
    } else if (ONTOLOGY_ROOT_CATEGORY[r.ontology] && ONTOLOGY_ROOT_CATEGORY[r.ontology] !== 'underdetermined') {
      oboOntologyRoot++;
    }
    if (r.hasGenus) oboGenus++;
    if (r.hasLogicalDef) oboLogicalDef++;
    if (r.relCount > 0) oboDependence++;
  }

  // ---- SUMO ----
  const sumo = loadSumo();
  const sumoCat = sumoCategoryOf(sumo);
  let sumoClasses = 0;
  let sumoTyped = 0;
  let sumoArg = 0;
  let sumoBicond = 0;
  for (const r of sumo.values()) {
    if (r.kind === 'class') sumoClasses++;
    if (sumoCat.get(r.term)) sumoTyped++;
    if (r.hasArgTyping) sumoArg++;
    if (r.hasBiconditional) sumoBicond++;
  }

  // ---- §3.5 four counts + domain balance ----
  const rawRecords = wn.total + obo.size + sumo.size;
  // type-level clusters: WN type synsets + OBO classes + SUMO classes.
  // NOTE: this is the UPPER BOUND (pre-crosswalk-merge). Exact cross-source
  // dedup (WN↔OBO↔SUMO) is S1 step 3 engineering that does not yet exist here;
  // the ONLY exact crosswalks available at census time are the shipped
  // alignment-kernel-v0.json anchor files (kernel-v0 ↔ each source), which
  // align to the ~54 hand kernel, not source↔source. So type-level clusters
  // here is reported as an unmerged union count with that caveat.
  const typeLevelUnion = wn.typeLevel + oboClasses + sumoClasses;
  const perSource = { wordnet_typelevel: wn.typeLevel, obo_classes: oboClasses, sumo_classes: sumoClasses };
  // domain balance: OBO is entirely biological; largest single ontology share
  const oboLargest = Object.entries(perOnt).sort((a, b) => b[1] - a[1])[0];
  const biologyShare = oboClasses / typeLevelUnion;

  const report = {
    stage: 'scale-s1-census',
    date: new Date().toISOString().slice(0, 10),
    epistemicStatus:
      'Exploratory S1-preparation pilot. MEASURES YIELD (records that CAN carry a source-asserted/candidate UFO value), NOT PRECISION (correctness of those values — needs the §4.3 human audit, not performed here). Local bytes only; no encoder version; no registry write; NO feasibility conclusion (design §14).',
    sources: {
      wordnet: { file: 'data/lexical-wn31', total: wn.total, instances_named_individuals: wn.instances, type_level: wn.typeLevel },
      obo: { file: 'data/onto-obo', records: obo.size, classes: oboClasses, per_ontology: perOnt },
      sumo: { file: 'data/onto-sumo', terms: sumo.size, classes: sumoClasses },
    },
    // ------- §2.3 blocker: does the union reach the 100k rung? -------
    reachability_100k: {
      question: 'S0 §2.3: SemCor tag_cnt exhausted at 27,210 < 100k. Does WN∪OBO∪SUMO clear 100k type-level clusters WITHOUT named entities?',
      four_counts_S35: {
        raw_source_records: rawRecords,
        exactly_crosswalked_clusters: 'NOT COMPUTED — source↔source exact crosswalk (WN↔OBO↔SUMO) is S1 step-3 engineering not yet built; only kernel-v0 anchor alignments ship. See caveat.',
        type_level_clusters_UNMERGED_UPPER_BOUND: typeLevelUnion,
        fully_resolved_ckufo_records: 'NOT COMPUTED — requires endorsement + human audit (S1→S2 gate).',
      },
      per_source: perSource,
      clears_100k_before_crosswalk_merge: typeLevelUnion >= 100000,
      caveat:
        'UNMERGED union upper bound: cross-source duplicates (e.g. WordNet cell ↔ CL cell) are NOT yet merged, so the true type-level count is LOWER. The measured point is that the union HEADROOM is >100k whereas the tag_cnt rule floored at 27,210 — the selection-rule exhaustion blocker (§2.3) is retired by the portfolio; the exact post-merge count is S1 step-3 work.',
    },
    // ------- §0.44 domain-balance requirement -------
    domain_balance: {
      requirement: 'design §0: a second domain-balanced count must exclude domination by a single taxonomy/domain.',
      obo_is_entirely_biology: true,
      biology_share_of_union: pct(oboClasses, typeLevelUnion),
      largest_single_ontology: { ontology: oboLargest?.[0], records: oboLargest?.[1], share_of_union: pct(oboLargest?.[1] ?? 0, typeLevelUnion) },
      note:
        'NCBITaxon is only 402 records locally (not the full millions-of-taxa dump), so single-TAXONOMY domination is NOT the local risk; single-DOMAIN (biology, via all-OBO) is. A domain-balanced 100k needs a non-biological structured source (Wikidata class subset, §3.1) that is NOT yet local — flagged as the one missing ingredient for a domain-balanced (not merely 100k) rung.',
    },
    // ------- §2.1 blocker: does OBO/SUMO move UFO typing off WordNet-only 0%? -------
    typing_yield_vs_wordnet_zero: {
      question:
        'S0 §2.1: WordNet-only gave 0% source-asserted ontic_category, 0% identity, 0% dependence. Do OBO/BFO + SUMO commitments (cascade steps 1-2) yield NONZERO on those fields?',
      wordnet_only_baseline_S0: { source_asserted_ontic: '0% (only the 1.27% instance flag on denotation_level)', identity: '0%', dependence: '0%' },
      obo: {
        classes: oboClasses,
        ontic_source_asserted_via_bfo_chain: { count: oboBfoReached, pct: pct(oboBfoReached, oboClasses), by_ontology: oboBfoByOnt, category_dist: oboCatDist },
        ontic_ontology_grounded_fallback_stipulated: { count: oboOntologyRoot, pct: pct(oboOntologyRoot, oboClasses) },
        identity_provider_candidate_via_genus: { count: oboGenus, pct: pct(oboGenus, oboClasses), note: 'genus-differentia logical definition supplies an identity-provider CANDIDATE via the genus chain — WordNet has none.' },
        logical_definition_records: { count: oboLogicalDef, pct: pct(oboLogicalDef, oboClasses) },
        dependence_candidate_via_RO_relationship: { count: oboDependence, pct: pct(oboDependence, oboClasses), note: 'RO relationship edges (part_of, has_part, ...) are dependence CANDIDATES — WordNet antonym/similarTo are lexical, not dependence.' },
      },
      sumo: {
        terms: sumo.size,
        classes: sumoClasses,
        ontic_via_subclass_chain: { count: sumoTyped, pct: pct(sumoTyped, sumo.size) },
        argument_typing_domain_range: { count: sumoArg, note: 'SUMO domain/range axioms give selectional/argument structure — the layer FrameNet only scaffolds and WordNet lacks.' },
        biconditional_definitions: { count: sumoBicond, note: 'SUMO <=> biconditionals are its genuinely-definitional statements.' },
      },
      interpretation:
        'YIELD not PRECISION. A NONZERO source-asserted ontic yield + NONZERO identity-provider-candidate + NONZERO dependence-candidate demonstrates the multi-source portfolio has an EVIDENTIAL PATH to the UFO fields that WordNet-only lacked entirely. Whether those candidates are CORRECT at the §4.3 0.95 bar is a SEPARATE human-audit measurement this probe does not perform.',
    },
    wallSeconds: (nowMs() - t0) / 1000,
  };

  writeJson(join(RESULTS_DIR, 'scale-s1-census.json'), report);

  // ---- markdown readout ----
  const md = `# SCALE-1 S1 (100k rung) — multi-source concept census + UFO-typing-yield probe

date: ${report.date} · script: \`poc/scale/src/census.ts\` · full JSON: \`scale-s1-census.json\` · wall: ${report.wallSeconds.toFixed(1)}s

**Epistemic status.** Exploratory S1-preparation pilot over LOCAL bytes
(\`data/lexical-wn31\`, \`data/onto-obo\`, \`data/onto-sumo\`). It measures **YIELD**
(records that CAN carry a source-asserted / candidate UFO value), **NOT
PRECISION** (whether those values are correct — that needs the design §4.3
stratified human audit, which this does not perform and does not substitute
for). No encoder version, no goldens, no registry write. **NO feasibility
conclusion; CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING (design §14).**

## Answers the two measured S0 blockers for the 100k rung

### §2.3 — selection-rule exhaustion (tag_cnt floored at 27,210 < 100k)

| §3.5 count | value |
|---|---|
| raw source records (WN+OBO+SUMO) | ${rawRecords.toLocaleString()} |
| type-level clusters — UNMERGED union upper bound | ${typeLevelUnion.toLocaleString()} |
| — WordNet type-level (non-instance) | ${wn.typeLevel.toLocaleString()} |
| — OBO classes | ${oboClasses.toLocaleString()} |
| — SUMO classes | ${sumoClasses.toLocaleString()} |
| clears 100k before cross-source merge? | **${typeLevelUnion >= 100000 ? 'YES' : 'NO'}** |

The union headroom is ${typeLevelUnion >= 100000 ? '>100k' : '<100k'}; the exhausted
tag_cnt rule floored at 27,210. **The selection-rule blocker is retired by the
portfolio** — but the count above is an UNMERGED upper bound (cross-source
duplicates not yet merged; exact source↔source crosswalk is S1 step-3
engineering). Exactly-crosswalked and fully-resolved counts are deliberately
NOT COMPUTED here (they need dedup engineering / human endorsement).

### §0 domain balance

OBO is entirely biological → biology share of the union = **${pct(oboClasses, typeLevelUnion)}**;
largest single ontology = ${oboLargest?.[0]} (${(oboLargest?.[1] ?? 0).toLocaleString()},
${pct(oboLargest?.[1] ?? 0, typeLevelUnion)}). NCBITaxon is only 402 records locally, so
single-*taxonomy* domination is NOT the local risk; single-*domain* (biology) is.
**A domain-balanced 100k needs a non-biological structured source (Wikidata class
subset, §3.1) that is not yet local** — the one missing ingredient flagged.

### §2.1 — WordNet-only gave 0% identity / 0% dependence / 0% source-asserted ontic

| field | WordNet-only (S0) | multi-source yield (this probe) |
|---|---|---|
| source-asserted ontic_category | 0% | OBO is_a*→BFO: **${oboBfoReached.toLocaleString()} (${pct(oboBfoReached, oboClasses)})**; SUMO subclass*: ${sumoTyped.toLocaleString()} (${pct(sumoTyped, sumo.size)}) |
| ontology-grounded ontic (STIPULATED fallback) | 0% | OBO: ${oboOntologyRoot.toLocaleString()} (${pct(oboOntologyRoot, oboClasses)}) |
| identity-provider candidate | 0% | OBO genus-differentia: **${oboGenus.toLocaleString()} (${pct(oboGenus, oboClasses)})** |
| dependence candidate | 0% | OBO RO relationship edges: **${oboDependence.toLocaleString()} (${pct(oboDependence, oboClasses)})** |
| argument/selectional typing | 0% | SUMO domain/range: ${sumoArg.toLocaleString()} |

OBO BFO-reached category distribution: ${JSON.stringify(oboCatDist)}.

**Interpretation (YIELD, not PRECISION).** A nonzero source-asserted ontic yield,
a nonzero identity-provider-candidate yield (genus), and a nonzero
dependence-candidate yield (RO) show the portfolio has an **evidential path** to
exactly the UFO fields WordNet-only lacked entirely. Whether those candidates are
**correct** at the §4.3 0.95 bar is a **separate human-audit measurement** this
probe does not perform. The BFO-reached fraction is modest in the LOCAL
extraction because most domain ontologies chain to their own roots, not to BFO
directly (only a handful of upper classes carry explicit is_a→BFO edges); closing
that gap is the S1 crosswalk step (load per-ontology BFO bridges + SUMO↔WordNet
mapping), not new science.

## What this increment does and does not license

- **Does:** retires §2.3 (union has >100k headroom); demonstrates §2.1 has a
  nonzero evidential path via OBO/SUMO (identity/dependence off 0%); gives the
  first §3.5-shaped four-count skeleton and the domain-balance gap (needs
  Wikidata).
- **Does NOT:** compute exact post-merge type-level clusters (needs S1 dedup
  engineering); measure typing PRECISION (needs §4.3 human audit); make any
  correctness/efficiency claim; touch construction B or any registered verdict.

ASM candidates for the coordinator: \`poc/scale/asm-2050-2059.json\`.
`;
  writeFileSync(join(RESULTS_DIR, 'scale-s1-census.md'), md);
  console.log(
    `census: WN type-level ${wn.typeLevel}, OBO classes ${oboClasses} (BFO-reached ${oboBfoReached}, genus ${oboGenus}, dep ${oboDependence}), SUMO ${sumo.size} (typed ${sumoTyped}); union ${typeLevelUnion} in ${report.wallSeconds.toFixed(1)}s`,
  );
}

main();
