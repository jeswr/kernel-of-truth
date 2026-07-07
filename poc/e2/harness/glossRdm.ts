/**
 * Baseline 3 — gloss word-overlap RDM (docs/poc-design.md E2 primary
 * criterion: "gloss word-overlap" relatedness baseline).
 *
 * HONEST DERIVATION (published; poc/e2/README.md repeats it): the "gloss" of
 * a concept is the SET of surface words a naive NSM-style rendering of its
 * explication AST would contain. We walk the kot-ast/1 tree and collect:
 *
 *   - predicate primes and prime fillers/heads: token lowercased; multi-way
 *     exponent names keep the FIRST variant ("SOMETHING~THING" -> something);
 *     hyphenated exponents split into words ("DON'T-WANT" -> don't, want);
 *   - operators (NOT, CAN, MAYBE, IF, BECAUSE, WHEN, LIKE, AFTER, BEFORE,
 *     VERY, MORE) as their lowercase surface words;
 *   - SP determiners / quantifiers / mods / intensifiers, same normalisation
 *     (THE-SAME -> the, same; OTHER~ELSE~ANOTHER -> other; MUCH~MANY -> much);
 *   - referent kinds at their declaration (SomeoneRef -> someone,
 *     SomethingRef -> something, TimeRef -> time, PlaceRef -> place,
 *     ClauseRef -> this);
 *   - KIND/PART SP frames -> "kind of" / "part of";
 *   - concept references -> the referenced kernel-v0 slug's words
 *     (urn:kernel-v0:maker-of -> maker, of) — a rendered gloss names the
 *     concept it leans on;
 *   - structural material contributes NO words: frame tags, role names,
 *     referent indices, clause order. Ref MENTIONS contribute nothing (the
 *     surface form of "ref n" is the already-counted referent kind).
 *
 * NO stopword removal: NSM explications are built almost entirely from
 * function-like words; removing them would empty the glosses. Similarity =
 * Jaccard |A∩B| / |A∪B| over these word SETS (types, not tokens).
 *
 * This is deliberately the *naive* overlap baseline the pre-registration
 * asks for: if kernel geometry explains model geometry only as well as
 * bag-of-gloss-words does, the kernel adds nothing.
 */

import { encoderContentHash } from '@jeswr/kernel-encoder';
import type {
  Clause,
  Explication,
  Filler,
  OpArg,
  SP,
  SPHead,
} from '@jeswr/kernel-encoder';
import { corpusPin, isMain, similarityMatrix, writeInput } from './common.js';
import { loadCorpus } from './corpus.js';
import { buildItems, slugOf } from './items.js';

/** "SOMETHING~THING" -> ["something"]; "DON'T-WANT" -> ["don't","want"]. */
export function surfaceWords(token: string): string[] {
  const first = token.split('~')[0]!;
  return first
    .toLowerCase()
    .split('-')
    .map((w) => w.trim())
    .filter((w) => w.length > 0);
}

const REF_KIND_WORDS: Record<string, string[]> = {
  SomeoneRef: ['someone'],
  SomethingRef: ['something'],
  TimeRef: ['time'],
  PlaceRef: ['place'],
  ClauseRef: ['this'],
};

export function deriveGlossWords(exp: Explication): Set<string> {
  const words = new Set<string>();
  const add = (token: string): void => {
    for (const w of surfaceWords(token)) words.add(w);
  };
  const addConceptId = (id: string): void => {
    for (const part of slugOf(id).split('-')) if (part.length > 0) words.add(part.toLowerCase());
  };

  const walkHead = (head: SPHead): void => {
    switch (head.kind) {
      case 'primeHead':
        add(head.prime);
        break;
      case 'kindFrame':
      case 'partFrame':
        words.add(head.kind === 'kindFrame' ? 'kind' : 'part');
        words.add('of');
        walkFiller(head.of);
        break;
      case 'refHead':
        break; // ref mention: surface form already counted at declaration
      case 'conceptHead':
        addConceptId(head.id);
        break;
    }
  };

  const walkSP = (sp: SP): void => {
    if (sp.det !== undefined) add(sp.det);
    if (sp.quant !== undefined) add(sp.quant);
    for (const m of sp.mods ?? []) {
      add(m.mod);
      if (m.intensifier !== undefined) add(m.intensifier);
    }
    walkHead(sp.head);
    if (sp.restrictedBy !== undefined) walkClause(sp.restrictedBy);
  };

  const walkFiller = (f: Filler | OpArg): void => {
    if ('type' in f) {
      walkClause(f);
      return;
    }
    switch (f.kind) {
      case 'sp':
        walkSP(f);
        break;
      case 'ref':
        break;
      case 'prime':
        add(f.prime);
        break;
      case 'concept':
        addConceptId(f.id);
        break;
      case 'clause':
        walkClause(f.clause);
        break;
      case 'quote':
        for (const c of f.clauses) walkClause(c);
        break;
      case 'temporal':
        add(f.op);
        walkFiller(f.anchor);
        break;
    }
  };

  const walkClause = (c: Clause): void => {
    if (c.type === 'pred') {
      add(c.pred);
      for (const filler of Object.values(c.roles)) {
        if (filler !== undefined) walkFiller(filler);
      }
    } else {
      add(c.op);
      for (const a of c.args) walkFiller(a);
    }
  };

  for (const r of exp.referents) {
    for (const w of REF_KIND_WORDS[r.refKind] ?? []) words.add(w);
  }
  for (const c of exp.clauses) walkClause(c);
  return words;
}

export function jaccard(a: ReadonlySet<string>, b: ReadonlySet<string>): number {
  let inter = 0;
  for (const w of a) if (b.has(w)) inter++;
  const union = a.size + b.size - inter;
  return union === 0 ? 0 : inter / union;
}

function main(): void {
  const corpus = loadCorpus();
  const byId = new Map(corpus.map((c) => [c.id, c]));
  const { probeItems } = buildItems(corpus.map((c) => c.id));
  const glosses = probeItems.map((p) => deriveGlossWords(byId.get(p.id)!.explication));
  const sim = similarityMatrix(glosses.length, (i, j) => jaccard(glosses[i]!, glosses[j]!));
  writeInput('baseline-gloss.json', {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpusPin: corpusPin(),
    derivation:
      'AST surface word sets (see poc/e2/harness/glossRdm.ts header: prime/operator/determiner exponents lowercased, first ~-variant, hyphens split; referent kinds at declaration; concept refs -> referenced slug words; structural material contributes nothing; no stopword removal). Similarity = Jaccard over word sets.',
    convention: 'similarity (Jaccard, unit diagonal); item order = ids[]',
    ids: probeItems.map((p) => p.id),
    words: probeItems.map((p) => p.word),
    glossWordSets: glosses.map((g) => [...g].sort()),
    similarity: sim,
  });
}

if (isMain(import.meta.url)) main();
