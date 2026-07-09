// Per-corpus minting configuration: the identity-payload split, reference mode,
// and profile header. Every decision here is documented in the corpus manifest
// (`identityNote`) and in reports; the split is the load-bearing choice
// (docs/design-hash-input.md: identity payload = record minus annotation /
// provenance-of-extraction).
//
// Two identity philosophies, applied by corpus `kind`:
//   * hand-authored  : content-addressed by MEANING. The identity payload is the
//                      definitional object itself, with NO source-id anchor — two
//                      records with an identical explication ARE the same concept.
//                      (kernel-v0, math-v0, molecules-v0.)
//   * bulk-extracted : a record is "an extractor's assertion ABOUT a source
//                      entity" (design-bulk-kernel.md). The stable source id is
//                      therefore INSIDE identity (as `sourceId`) — without it,
//                      structurally-identical AxiomsOnly records (e.g. 3,620
//                      WordNet adjectives with empty axioms) would collapse to a
//                      single URN, an unsound merge of distinct concepts. This is
//                      the task's sanctioned "reference by stable source id"
//                      route, made explicit and uniform.
//
// Reference mode:
//   * substitute : intra-corpus references resolved to minted urn:kot: URNs in
//                  reverse topological order (Unison-style); cyclic SCCs handled
//                  by the gist s6 component algorithm. Requires refs to sit at
//                  clean whole-string JSON positions.
//   * stable     : references kept as their placeholder urn:<corpus>: (stable
//                  source id). Chosen where refs are embedded in literal content
//                  (a KIF/token string, a prose grounding note) so substitution
//                  would alter source bytes, or where the graph is not a DAG
//                  (WordNet antonymy) so no reverse-topo order exists.

import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { JsonValue } from "./jcs.js";

export interface RawRecord {
  id: string; // placeholder urn:<corpus>:<sid>
  raw: { [k: string]: JsonValue };
}

export interface CorpusSpec {
  name: string;
  prefix: string; // e.g. "urn:kernel-v0:"
  profileHeader: string; // includes trailing "\n"
  refMode: "substitute" | "stable";
  kind: "hand-authored" | "bulk-extracted";
  identityNote: string;
  // manifest path to update (or null when the corpus emits a separate mint manifest)
  manifestPath: string | null;
  outDir: string; // where minted-urns.jsonl / mint-manifest.json land
  load(dataRoot: string): RawRecord[];
  // Build the identity payload from a raw record. For bulk corpora this MUST
  // include the stable `sourceId`. It must NOT include the placeholder `id`.
  idPayload(raw: { [k: string]: JsonValue }, sid: string): JsonValue;
}

function readJson(path: string): { [k: string]: JsonValue } {
  return JSON.parse(readFileSync(path, "utf8"));
}
function readJsonl(path: string): Array<{ [k: string]: JsonValue }> {
  return readFileSync(path, "utf8")
    .split("\n")
    .filter((l) => l.trim().length > 0)
    .map((l) => JSON.parse(l));
}
function globJson(dir: string): string[] {
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .sort()
    .map((f) => join(dir, f));
}
function omit(o: { [k: string]: JsonValue }, keys: string[]): { [k: string]: JsonValue } {
  const out: { [k: string]: JsonValue } = {};
  for (const k of Object.keys(o)) if (!keys.includes(k)) out[k] = o[k]!;
  return out;
}
function sid(id: string, prefix: string): string {
  return id.startsWith(prefix) ? id.slice(prefix.length) : id;
}

export interface SpecOptions {
  // Freeze the haiku-tier live stream: read records from this directory
  // (a caller-made snapshot copy) instead of data/haiku-tier/records, so the
  // determinism double-run compares like with like.
  haikuRecordsDir?: string;
}

export function makeSpecs(dataRoot: string, opts: SpecOptions = {}): CorpusSpec[] {
  const specs: CorpusSpec[] = [];

  // ---- kernel-v0 (hand-authored explications; substitute) ----
  specs.push({
    name: "kernel-v0",
    prefix: "urn:kernel-v0:",
    profileHeader: "kot-ast/1\n",
    refMode: "substitute",
    kind: "hand-authored",
    identityNote:
      "Identity = the kot-ast/1 `explication` object (content-addressed by meaning). " +
      "label/gloss/notes/pattern/status/references are annotation. Intra-corpus conceptRefs " +
      "substituted to minted urn:kot: URNs in reverse topological order (DAG, no cycles).",
    manifestPath: join(dataRoot, "kernel-v0", "manifest.json"),
    outDir: join(dataRoot, "kernel-v0"),
    load: (root) =>
      globJson(join(root, "kernel-v0", "concepts")).map((p) => {
        const r = readJson(p);
        return { id: r["id"] as string, raw: r };
      }),
    idPayload: (raw) => raw["explication"]!,
  });

  // ---- math-v0 (hand-authored profile-M AST; substitute) ----
  specs.push({
    name: "math-v0",
    prefix: "urn:math-v0:",
    profileHeader: "kot-pm-ast/1\n",
    refMode: "substitute",
    kind: "hand-authored",
    identityNote:
      "Identity = the pm-ast/1 `definition` tree (content-addressed by meaning). " +
      "label/gloss/notes/nsmBridge/characterizes/status/references are annotation. " +
      "Intra-corpus refs substituted in reverse topological order (DAG).",
    manifestPath: join(dataRoot, "math-v0", "manifest.json"),
    outDir: join(dataRoot, "math-v0"),
    load: (root) =>
      globJson(join(root, "math-v0", "concepts")).map((p) => {
        const r = readJson(p);
        return { id: r["id"] as string, raw: r };
      }),
    idPayload: (raw) => raw["definition"]!,
  });

  // ---- code-v0 (hand-authored structural code-construct definitions; substitute) ----
  // A5 code world-layer vocabulary (data/code-v0/README.md profile decision):
  // NOT kot-ast/1 NSM explications — the same corpus-specific-profile route as
  // math-v0. Containment reuses kernel-v0 part-of/has-part (nothing minted).
  specs.push({
    name: "code-v0",
    prefix: "urn:code-v0:",
    profileHeader: "kot-code-construct/1\n",
    refMode: "substitute",
    kind: "hand-authored",
    identityNote:
      "Identity = the kot-code-construct/1 `definition` object (content-addressed structural " +
      "definition: construct kind + language + definition text + intra-corpus refs). " +
      "label/gloss/notes/status/references are annotation. Intra-corpus refs substituted " +
      "to minted urn:kot: URNs in reverse topological order (DAG, no cycles).",
    manifestPath: join(dataRoot, "code-v0", "manifest.json"),
    outDir: join(dataRoot, "code-v0"),
    load: (root) =>
      globJson(join(root, "code-v0", "concepts")).map((p) => {
        const r = readJson(p);
        return { id: r["id"] as string, raw: r };
      }),
    idPayload: (raw) => raw["definition"]!,
  });

  // ---- math-mm (bulk profile-M metamath; substitute; the df-cleq/df-clel 2-cycle) ----
  specs.push({
    name: "math-mm",
    prefix: "urn:math-mm:",
    profileHeader: "kot-pm-mm/1\n",
    refMode: "substitute",
    kind: "bulk-extracted",
    identityNote:
      "Identity = {sourceId (set.mm label), status, references (the curated forward " +
      "dependency vector, substituted to minted URNs), definition (mm-canonical token " +
      "string verbatim; syntaxFormer substituted; the DERIVED `definedBy` inverse pointer " +
      "EXCLUDED — it is the inverse of syntaxFormer and would manufacture 1,431 spurious " +
      "2-cycles)}. Over `references` the only non-trivial SCC is {df-cleq, df-clel} " +
      "(set.mm's class-theory bootstrap), minted via the gist s6 component algorithm. " +
      "sourceComment/dependencies/provenance/label excluded.",
    manifestPath: join(dataRoot, "math-mm", "manifest.json"),
    outDir: join(dataRoot, "math-mm"),
    load: (root) => {
      const out: RawRecord[] = [];
      for (const f of ["syntax.jsonl", "definitions.jsonl", "axioms.jsonl"]) {
        for (const r of readJsonl(join(root, "math-mm", f))) out.push({ id: r["id"] as string, raw: r });
      }
      return out;
    },
    idPayload: (raw, s) => {
      const def = raw["definition"] as { [k: string]: JsonValue };
      return {
        sourceId: s,
        status: raw["status"]!,
        references: raw["references"]!,
        definition: omit(def, ["definedBy"]),
      };
    },
  });

  // ---- molecules-v0 (hand-authored molecules; stable — prose grounding note) ----
  specs.push({
    name: "molecules-v0",
    prefix: "urn:molecule-v0:",
    profileHeader: "kot-mol/1\n",
    refMode: "stable",
    kind: "hand-authored",
    identityNote:
      "Identity = {semanticStatus, flag, groundingNote, groundingRefs, moleculeDepth, axioms, " +
      "partialExplication} per gist s3.5 (the authored grounding note IS the payload). " +
      "STABLE ids: refs are embedded inside the prose groundingNote as {urn:...|gloss} — " +
      "substituting would alter authored source bytes. label/researchGrade/notes/corpusLemmas " +
      "are annotation. groundingRefs to kernel-v0 are cross-corpus and stay stable.",
    manifestPath: join(dataRoot, "molecules-v0", "manifest.json"),
    outDir: join(dataRoot, "molecules-v0"),
    load: (root) =>
      globJson(join(root, "molecules-v0", "molecules")).map((p) => {
        const r = readJson(p);
        return { id: r["id"] as string, raw: r };
      }),
    idPayload: (raw) => ({
      semanticStatus: raw["semanticStatus"]!,
      flag: raw["flag"]!,
      groundingNote: raw["groundingNote"]!,
      groundingRefs: raw["groundingRefs"]!,
      moleculeDepth: raw["moleculeDepth"]!,
      axioms: raw["axioms"]!,
      partialExplication: raw["partialExplication"] ?? null,
    }),
  });

  // ---- physics-v0 (bulk exact dimensional corpus; substitute; qk<->unit 2-cycles) ----
  const physExclude = [
    "id", "label", "symbol", "source", "status", "notes",
    "nsmGloss", "nsmGlossStatus", "bridgesTo", "bridgeStatus", "boundary",
    "statement", "semantics",
  ];
  specs.push({
    name: "physics-v0",
    prefix: "urn:physics-v0:",
    profileHeader: "kot-phys/1\n",
    refMode: "substitute",
    kind: "bulk-extracted",
    identityNote:
      "Identity = {sourceId, schema, type, and exact structural content (dim vector, " +
      "index/siBaseUnit for dimensions, dim/coherentSIUnit for kinds, quantityKind/scale/" +
      "offset/coherentSI for units, value/quantityKind for constants, lhs/rhs for relations)}. " +
      "label/symbol/source/status/nsmGloss/bridgesTo/statement/semantics/notes are annotation. " +
      "Intra-corpus refs substituted; the 25 quantity-kind<->coherent-unit 2-cycles are minted " +
      "via the gist s6 component algorithm.",
    manifestPath: join(dataRoot, "physics-v0", "manifest.json"),
    outDir: join(dataRoot, "physics-v0"),
    load: (root) => {
      const out: RawRecord[] = [];
      for (const sub of ["dimensions", "quantitykinds", "units", "constants", "equations"]) {
        for (const p of globJson(join(root, "physics-v0", sub))) {
          const r = readJson(p);
          out.push({ id: r["id"] as string, raw: r });
        }
      }
      return out;
    },
    idPayload: (raw, s) => ({ sourceId: s, ...omit(raw, physExclude) }),
  });

  // ---- physics-qudt (bulk QUDT tier; substitute; DAG) ----
  const qudtExclude = ["id", "label", "symbol", "status", "derivation", "provenance", "bridgesTo", "bridgeStatus"];
  specs.push({
    name: "physics-qudt",
    prefix: "urn:physics-qudt:",
    profileHeader: "kot-phys/1\n",
    refMode: "substitute",
    kind: "bulk-extracted",
    identityNote:
      "Identity = {sourceId, schema, type, semanticStatus, dim, dimOrder, broader (kinds), " +
      "quantityKind/otherQuantityKinds/scale/offset/coherentSI/piExponent (units)}. " +
      "label/symbol/status/derivation/provenance/bridgesTo are annotation. Intra-corpus refs " +
      "substituted in reverse topological order (DAG — no qk<->unit backref in QUDT). Shares the " +
      "kot-phys/1 profile with physics-v0 (same grammar); sourceIds keep the corpora disjoint.",
    manifestPath: join(dataRoot, "physics-qudt", "manifest.json"),
    outDir: join(dataRoot, "physics-qudt"),
    load: (root) => {
      const out: RawRecord[] = [];
      for (const f of ["quantitykinds.jsonl", "units.jsonl"]) {
        for (const r of readJsonl(join(root, "physics-qudt", f))) out.push({ id: r["id"] as string, raw: r });
      }
      return out;
    },
    idPayload: (raw, s) => ({ sourceId: s, ...omit(raw, qudtExclude) }),
  });

  // ---- lexical-wn31 (bulk AxiomsOnly WordNet; stable — non-DAG antonymy) ----
  specs.push({
    name: "lexical-wn31",
    prefix: "urn:lexical-wn31:",
    profileHeader: "kot-lex/1\n",
    refMode: "stable",
    kind: "bulk-extracted",
    identityNote:
      "Identity = {sourceId (synset offset), schema, semanticStatus, pos, ssType, axioms}. " +
      "STABLE ids: the axiom graph is NOT a DAG (antonymy/similarTo cycles) so no reverse-topo " +
      "order exists. lemmas/gloss/lexFile/markers are annotation. NOTE: the README's 'inside " +
      "identity' list omitted the synset offset; including it (as sourceId) is REQUIRED — without " +
      "it 66,569 records (incl. 3,620 axiom-less adjectives) collapse to shared URNs, an unsound " +
      "merge of distinct concepts. Deviation filed as a follow-up bead.",
    manifestPath: join(dataRoot, "lexical-wn31", "manifest.json"),
    outDir: join(dataRoot, "lexical-wn31"),
    load: (root) => {
      const out: RawRecord[] = [];
      for (const f of ["synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl"]) {
        for (const r of readJsonl(join(root, "lexical-wn31", f))) out.push({ id: r["id"] as string, raw: r });
      }
      return out;
    },
    idPayload: (raw, s) => ({
      sourceId: s,
      schema: raw["schema"]!,
      semanticStatus: raw["semanticStatus"]!,
      pos: raw["pos"]!,
      ssType: raw["ssType"]!,
      axioms: raw["axioms"]!,
    }),
  });

  // ---- onto-obo (bulk logical-definition tier; substitute; SCCs up to size 11) ----
  specs.push({
    name: "onto-obo",
    prefix: "urn:onto-obo:",
    profileHeader: "kot-obo/1\n",
    refMode: "substitute",
    kind: "bulk-extracted",
    identityNote:
      "Identity = {sourceId (OBO id), schema, semanticStatus, ontology, kind, oboId, axioms, " +
      "logicalDefinition?, characteristics?, upgradeCandidate?}. label/definition(prose)/synonyms/" +
      "xrefs/comment/namespace/subsets are annotation. Intra-corpus refs substituted; the 49 " +
      "GO/RO SCCs (max size 11: e.g. cell-communication cluster) minted via the gist s6 component " +
      "algorithm. 5 external/cross-ontology refs (NCBITaxon, foaf, COB, BFO_0000060) are unresolved " +
      "in-corpus and kept as stable placeholder ids.",
    manifestPath: join(dataRoot, "onto-obo", "manifest.json"),
    outDir: join(dataRoot, "onto-obo"),
    load: (root) => {
      const out: RawRecord[] = [];
      for (const f of ["bfo.jsonl", "ro.jsonl", "go.jsonl"]) {
        for (const r of readJsonl(join(root, "onto-obo", f))) out.push({ id: r["id"] as string, raw: r });
      }
      return out;
    },
    idPayload: (raw) => {
      const keep = ["schema", "semanticStatus", "ontology", "kind", "oboId", "axioms", "logicalDefinition", "characteristics", "upgradeCandidate"];
      const out: { [k: string]: JsonValue } = { sourceId: raw["oboId"]! };
      for (const k of keep) if (k in raw) out[k] = raw[k]!;
      return out;
    },
  });

  // ---- onto-sumo (bulk SUO-KIF axiom tier; stable — literal KIF strings, bare-name refs) ----
  specs.push({
    name: "onto-sumo",
    prefix: "urn:onto-sumo:",
    profileHeader: "kot-sumo/1\n",
    refMode: "stable",
    kind: "bulk-extracted",
    identityNote:
      "Two record types. Axiom identity = {sourceId, schema, semanticStatus, form, operator, kif, " +
      "terms, subject?, definienda?}; term identity = {sourceId, schema, semanticStatus, term, kind, " +
      "axioms, definitionalAxiomRefs}. STABLE ids: the canonical KIF string embeds term references " +
      "literally and term axioms reference by BARE name — substitution would alter source bytes. " +
      "documentation/label are annotation; sourceFile/ordinal/axiomStats are derived (excluded).",
    manifestPath: join(dataRoot, "onto-sumo", "manifest.json"),
    outDir: join(dataRoot, "onto-sumo"),
    load: (root) => {
      const out: RawRecord[] = [];
      for (const f of ["axioms.jsonl", "terms.jsonl"]) {
        for (const r of readJsonl(join(root, "onto-sumo", f))) out.push({ id: r["id"] as string, raw: r });
      }
      return out;
    },
    idPayload: (raw, s) => {
      if ("kif" in raw) {
        const out: { [k: string]: JsonValue } = {
          sourceId: s, schema: raw["schema"]!, semanticStatus: raw["semanticStatus"]!,
          form: raw["form"]!, operator: raw["operator"]!, kif: raw["kif"]!, terms: raw["terms"]!,
        };
        if ("subject" in raw && raw["subject"] !== null) out["subject"] = raw["subject"]!;
        if ("definienda" in raw && raw["definienda"] !== null) out["definienda"] = raw["definienda"]!;
        return out;
      }
      const out: { [k: string]: JsonValue } = {
        sourceId: s, schema: raw["schema"]!, semanticStatus: raw["semanticStatus"]!,
        term: raw["term"]!, kind: raw["kind"]!, axioms: raw["axioms"]!,
      };
      if ("definitionalAxiomRefs" in raw) out["definitionalAxiomRefs"] = raw["definitionalAxiomRefs"]!;
      return out;
    },
  });

  // ---- onto-framenet (bulk valency scaffold; substitute; DAG) ----
  specs.push({
    name: "onto-framenet",
    prefix: "urn:onto-framenet:",
    profileHeader: "kot-framenet/1\n",
    refMode: "substitute",
    kind: "bulk-extracted",
    identityNote:
      "Frame identity = {sourceId, schema, semanticStatus, form, frame, frameId, frameElements}; " +
      "relation identity = {sourceId, schema, semanticStatus, form, relationType, sub, super, feMappings}. " +
      "definition/frameElementDefinitions/lexicalUnits are annotation; subFrame/superFrame labels and " +
      "the redundant *FrameId ints are dropped. Relation sub/super substituted to minted frame URNs " +
      "in reverse topological order (DAG).",
    manifestPath: join(dataRoot, "onto-framenet", "manifest.json"),
    outDir: join(dataRoot, "onto-framenet"),
    load: (root) => {
      const out: RawRecord[] = [];
      for (const f of ["frames.jsonl", "frame-relations.jsonl"]) {
        for (const r of readJsonl(join(root, "onto-framenet", f))) out.push({ id: r["id"] as string, raw: r });
      }
      return out;
    },
    idPayload: (raw, s) => {
      if ("frameElements" in raw) {
        return {
          sourceId: s, schema: raw["schema"]!, semanticStatus: raw["semanticStatus"]!,
          form: raw["form"]!, frame: raw["frame"]!, frameId: raw["frameId"]!, frameElements: raw["frameElements"]!,
        };
      }
      return {
        sourceId: s, schema: raw["schema"]!, semanticStatus: raw["semanticStatus"]!,
        form: raw["form"]!, relationType: raw["relationType"]!, sub: raw["sub"]!, super: raw["super"]!,
        feMappings: raw["feMappings"]!,
      };
    },
  });

  // ---- haiku-tier (modelAuthored pilot records; stable; LIVE stream — snapshot semantics) ----
  // The volume runner writes data/haiku-tier/records/ concurrently; the mint
  // pass snapshots whatever .json records exist at load time and the mint
  // manifest records that count + snapshot time. Incremental re-mint is a
  // filed follow-up.
  specs.push({
    name: "haiku-tier",
    prefix: "urn:haiku-tier:",
    profileHeader: "kot-haiku/1\n",
    refMode: "stable",
    kind: "bulk-extracted",
    identityNote:
      "Identity = {sourceId (lemma), schema, semanticStatus, candidateStatus, kind, and the " +
      "definitional content: groundingNote/groundingRefs/moleculeDepth (molecule-kind) or the " +
      "kot-ast/1 `record` (explication-kind)}. label/gloss/gatesPassed/researchGrade/provenance " +
      "are annotation. STABLE ids: grounding refs are cross-corpus (kernel-v0/molecules-v0) and " +
      "embedded in prose {urn:...|gloss} tokens — never rewritten (same rule as molecules-v0). " +
      "LIVE-STREAM SNAPSHOT: records/ is being written concurrently by the volume runner; " +
      "mintedCount reflects the snapshot at mint time, not a closed corpus.",
    manifestPath: null, // live stream: emit mint-manifest.json instead of touching the stream's files
    outDir: join(dataRoot, "haiku-tier"),
    load: (root) => {
      const dir = opts.haikuRecordsDir ?? join(root, "haiku-tier", "records");
      let files: string[];
      try {
        files = globJson(dir);
      } catch {
        return [];
      }
      return files.map((p) => {
        const r = readJson(p);
        return { id: r["id"] as string, raw: r };
      });
    },
    idPayload: (raw, s) => {
      const out: { [k: string]: JsonValue } = {
        sourceId: s, schema: raw["schema"]!, semanticStatus: raw["semanticStatus"]!,
        candidateStatus: raw["candidateStatus"]!, kind: raw["kind"]!,
      };
      for (const k of ["groundingNote", "groundingRefs", "moleculeDepth", "record"]) {
        if (k in raw) out[k] = raw[k]!;
      }
      return out;
    },
  });

  return specs;
}

// Corpora surveyed but deliberately NOT minted:
//   * math-lean-sample — lean-ref/1 records are annotation-layer formal
//     references, identity-anchored on (mathlibCommit, name); the signed route
//     decision (docs/design-lean-route.md decision 1) says they mint NO concept
//     ids. Minting them here would override a signed design decision.
export const UNMINTED: Array<{ name: string; reason: string }> = [
  {
    name: "math-lean-sample",
    reason:
      "lean-ref/1 formal reference records mint no concept URNs by signed design " +
      "(docs/design-lean-route.md): identity anchored on (mathlibCommit, name); " +
      "every field is outside any concept-hash boundary.",
  },
];
