// Minting pass driver (bead kernel-of-truth-mud).
//
//   node dist/src/cli.js --data <repo>/data --out <canonical-out-dir> [--corpus name]...
//
// Per corpus:
//   1. load records; identity payload per corpora.ts (the documented split);
//   2. build the intra-corpus reference graph over identity payloads
//      (substitute mode) or skip graph work (stable mode);
//   3. Tarjan SCC -> reverse topological order -> mint (singleton or gist-s6
//      component algorithm for cyclic SCCs);
//   4. emit  <corpus>/minted-urns.jsonl   {sourceId, id, urn}   (committed)
//            <out>/<corpus>.canonical.jsonl  one JCS line per record:
//              {"payload":<canonical identity payload>,"urn":"..."}
//              — the line itself is JCS-canonical (keys pre-sorted), so the
//              payload substring IS the hashed bytes (after header prefix).
//   5. update the corpus manifest with the minting block;
//   6. honesty ledger: URN collisions (identical identity payloads), cyclic
//      components, unresolved refs — counted, never silent.

import { mkdirSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { canonicalize, JsonValue } from "./jcs.js";
import { sha256, utf8, toHex } from "./hash.js";
import { tarjanSCC } from "./scc.js";
import { merkleRoot } from "./merkle.js";
import { mintSingleton, mintComponent, rewriteStrings, ComponentMember } from "./mint-core.js";
import { makeSpecs, CorpusSpec, RawRecord, SpecOptions } from "./corpora.js";

interface MintedRow {
  sourceId: string;
  id: string; // placeholder urn
  urn: string; // minted urn:kot:
}

interface CorpusResult {
  name: string;
  profileHeader: string;
  mintedCount: number;
  uniqueUrnCount: number;
  corpusIdentityRoot: string;
  duplicateGroups: number;
  cyclicComponents: Array<{ members: string[]; orderingKeys: string[] }>;
  refMode: string;
  identityNote: string;
  unresolvedRefs: Record<string, number>;
}

// Collect intra-corpus references appearing in an identity payload: any string
// exactly equal to a known placeholder id, or embedded as {urn:...|gloss}.
function collectRefs(payload: JsonValue, prefix: string, ownId: string, known: Set<string>, unresolved: Map<string, number>): string[] {
  const acc = new Set<string>();
  walk(payload);
  acc.delete(ownId);
  return Array.from(acc).sort();

  function walk(v: JsonValue): void {
    if (typeof v === "string") {
      if (v.startsWith(prefix)) {
        if (known.has(v)) acc.add(v);
        else unresolved.set(v, (unresolved.get(v) ?? 0) + 1);
      }
      // inline {urn:...|gloss} tokens are reported but only substituted in
      // substitute-mode corpora that use them (none today; molecules/haiku are stable)
      const m = v.matchAll(/\{(urn:[^|}]+)\|/g);
      for (const g of m) {
        const u = g[1]!;
        if (u.startsWith(prefix)) {
          if (known.has(u)) acc.add(u);
          else unresolved.set(u, (unresolved.get(u) ?? 0) + 1);
        }
      }
    } else if (Array.isArray(v)) {
      for (const x of v) walk(x);
    } else if (v !== null && typeof v === "object") {
      for (const k of Object.keys(v)) walk((v as { [k: string]: JsonValue })[k]!);
    }
  }
}

export function mintCorpus(spec: CorpusSpec, dataRoot: string, outDir: string): { result: CorpusResult; rows: MintedRow[] } {
  const records = spec.load(dataRoot);
  const byId = new Map<string, RawRecord>();
  for (const r of records) {
    if (byId.has(r.id)) throw new Error(`ERR_DUP_SOURCE_ID: ${spec.name} ${r.id}`);
    byId.set(r.id, r);
  }
  const known = new Set(byId.keys());
  const sidOf = (id: string): string => (id.startsWith(spec.prefix) ? id.slice(spec.prefix.length) : id);

  const payloads = new Map<string, JsonValue>();
  for (const r of records) payloads.set(r.id, spec.idPayload(r.raw, sidOf(r.id)));

  const minted = new Map<string, string>(); // placeholder id -> urn:kot:
  const canonical = new Map<string, string>(); // placeholder id -> canonical JCS string of substituted payload
  const memberInfo = new Map<string, number>(); // placeholder id -> component member index (cyclic only)
  const unresolved = new Map<string, number>();
  const cyclicComponents: Array<{ members: string[]; orderingKeys: string[] }> = [];

  const resolve = (s: string): string => minted.get(s) ?? s;

  if (spec.refMode === "substitute") {
    const edges = new Map<string, readonly string[]>();
    for (const r of records) {
      edges.set(r.id, collectRefs(payloads.get(r.id)!, spec.prefix, r.id, known, unresolved));
    }
    // Tarjan emits SCCs in reverse topological order: dependencies first.
    const comps = tarjanSCC(Array.from(known).sort(), edges);
    for (const comp of comps) {
      if (comp.length === 1) {
        const id = comp[0]!;
        // self-loop check: a singleton with a self-edge is handled by #self in mintSingleton
        const m = mintSingleton(payloads.get(id)!, spec.profileHeader, id, resolve);
        minted.set(id, m.urn);
        canonical.set(id, new TextDecoder().decode(m.canonicalBytes));
      } else {
        if (comp.length > 32) {
          throw new Error(`ERR_SCC_TOO_LARGE: ${spec.name} scc size ${comp.length} > 32`);
        }
        const members: ComponentMember[] = comp
          .slice()
          .sort()
          .map((id) => ({ sourceId: id, payload: payloads.get(id)! }));
        const res = mintComponent(members, spec.profileHeader, resolve);
        for (const [id, urn] of res.urns) minted.set(id, urn);
        // Members of a cyclic SCC verify through the component record + their
        // canonical index (gist s6 steps 8-9): store the component JSON once
        // per member together with its index.
        const componentJson = new TextDecoder().decode(res.componentCanonicalBytes);
        for (const id of comp) {
          canonical.set(id, componentJson);
          memberInfo.set(id, res.memberIndex.get(id)!);
        }
        cyclicComponents.push({
          members: members.map((m) => m.sourceId),
          orderingKeys: res.orderingKeysHex,
        });
      }
    }
  } else {
    // stable mode: no substitution; payload hashed as-is (placeholder refs are
    // stable source ids under a pinned source version).
    for (const r of records) {
      collectRefs(payloads.get(r.id)!, spec.prefix, r.id, known, unresolved); // ledger only
      const m = mintSingleton(payloads.get(r.id)!, spec.profileHeader, r.id, (s) => s);
      minted.set(r.id, m.urn);
      canonical.set(r.id, new TextDecoder().decode(m.canonicalBytes));
    }
  }

  // Duplicate-identity ledger.
  const urnCounts = new Map<string, number>();
  for (const u of minted.values()) urnCounts.set(u, (urnCounts.get(u) ?? 0) + 1);
  const duplicateGroups = Array.from(urnCounts.values()).filter((c) => c > 1).length;

  // Emit minted-urns.jsonl sorted by source id for byte-determinism.
  const rows: MintedRow[] = records
    .map((r) => ({ sourceId: sidOf(r.id), id: r.id, urn: minted.get(r.id)! }))
    .sort((a, b) => (a.sourceId < b.sourceId ? -1 : a.sourceId > b.sourceId ? 1 : 0));

  const urns = rows.map((r) => r.urn);
  const root = merkleRoot(urns);

  mkdirSync(spec.outDir, { recursive: true });
  writeFileSync(
    join(spec.outDir, "minted-urns.jsonl"),
    rows.map((r) => canonicalize({ id: r.id, sourceId: r.sourceId, urn: r.urn })).join("\n") + "\n",
  );

  // canonical identity bytes for the snapshot pack (NOT committed; regenerable).
  mkdirSync(outDir, { recursive: true });
  const lines: string[] = [];
  for (const r of rows) {
    // Construct each line so the canonical payload substring appears verbatim
    // and the line itself is JCS-canonical (keys pre-sorted):
    //   singleton:  {"payload":<canonical>,"urn":"..."}
    //   SCC member: {"component":<canonical component>,"memberIndex":i,"urn":"..."}
    const idx = memberInfo.get(r.id);
    if (idx === undefined) {
      lines.push(`{"payload":${canonical.get(r.id)!},"urn":"${r.urn}"}`);
    } else {
      lines.push(`{"component":${canonical.get(r.id)!},"memberIndex":${idx},"urn":"${r.urn}"}`);
    }
  }
  writeFileSync(join(outDir, `${spec.name}.canonical.jsonl`), lines.join("\n") + "\n");

  const result: CorpusResult = {
    name: spec.name,
    profileHeader: spec.profileHeader,
    mintedCount: rows.length,
    uniqueUrnCount: urnCounts.size,
    corpusIdentityRoot: root,
    duplicateGroups,
    cyclicComponents,
    refMode: spec.refMode,
    identityNote: spec.identityNote,
    unresolvedRefs: Object.fromEntries(Array.from(unresolved.entries()).sort()),
  };
  return { result, rows };
}

// Content-hash of the mint tool itself: sha256 over sorted (path, bytes) of src/*.ts.
export function mintToolHash(): string {
  const here = dirname(fileURLToPath(import.meta.url));
  // dist/src -> tool root is two levels up; hash the TypeScript sources.
  const srcDir = join(here, "..", "..", "src");
  const files = ["cli.ts", "corpora.ts", "hash.ts", "jcs.ts", "merkle.ts", "mint-core.ts", "scc.ts"];
  const parts: Uint8Array[] = [];
  for (const f of files) {
    parts.push(utf8(f + "\n"));
    parts.push(new Uint8Array(readFileSync(join(srcDir, f))));
  }
  const total = parts.reduce((a, p) => a + p.length, 0);
  const buf = new Uint8Array(total);
  let off = 0;
  for (const p of parts) {
    buf.set(p, off);
    off += p.length;
  }
  return toHex(sha256(buf));
}

function updateManifest(spec: CorpusSpec, result: CorpusResult, toolHash: string): void {
  const block = {
    profileHeader: result.profileHeader,
    mintedCount: result.mintedCount,
    uniqueUrnCount: result.uniqueUrnCount,
    mintToolHash: toolHash,
    corpusIdentityRoot: result.corpusIdentityRoot,
    identityRootAlgorithm:
      "binary Merkle over unique minted URNs sorted by UTF-16 code unit; leaf=sha256(utf8(urn)); parent=sha256(left||right); odd node promoted; hex root",
    urnScheme: "urn:kot:<multibase-b-base32(multihash sha2-256)> per docs/design-hash-input.md",
    referenceMode: result.refMode,
    identityPayload: result.identityNote,
    duplicateIdentityGroups: result.duplicateGroups,
    cyclicComponents: result.cyclicComponents.map((c) => c.members),
    mintDate: "2026-07-07",
  };
  if (spec.manifestPath !== null && existsSync(spec.manifestPath)) {
    const manifest = JSON.parse(readFileSync(spec.manifestPath, "utf8"));
    manifest["minting"] = block;
    writeFileSync(spec.manifestPath, JSON.stringify(manifest, null, 2) + "\n");
  } else {
    // live streams (haiku-tier): separate mint manifest, do not touch stream files
    writeFileSync(
      join(spec.outDir, "mint-manifest.json"),
      JSON.stringify({ corpus: spec.name, snapshotNote: "live stream snapshot; see identityPayload", minting: block }, null, 2) + "\n",
    );
  }
}

export function main(argv: string[]): void {
  const args = new Map<string, string[]>();
  let key = "";
  for (const a of argv) {
    if (a.startsWith("--")) {
      key = a.slice(2);
      if (!args.has(key)) args.set(key, []);
    } else if (key) {
      args.get(key)!.push(a);
    }
  }
  const dataRoot = args.get("data")?.[0];
  const outDir = args.get("out")?.[0];
  if (!dataRoot || !outDir) {
    console.error("usage: cli.js --data <repo>/data --out <canonical-out> [--corpus name ...] [--no-manifest] [--haiku-records <frozen-dir>]");
    process.exit(2);
  }
  const only = new Set(args.get("corpus") ?? []);
  const writeManifests = !args.has("no-manifest");
  const opts: SpecOptions = {};
  const haikuDir = args.get("haiku-records")?.[0];
  if (haikuDir) opts.haikuRecordsDir = haikuDir;

  const specs = makeSpecs(dataRoot, opts).filter((s) => only.size === 0 || only.has(s.name));
  const toolHash = mintToolHash();
  const summary: Record<string, unknown>[] = [];
  for (const spec of specs) {
    const t0 = Date.now();
    const { result } = mintCorpus(spec, dataRoot, outDir);
    if (writeManifests) updateManifest(spec, result, toolHash);
    summary.push({
      corpus: result.name,
      minted: result.mintedCount,
      uniqueUrns: result.uniqueUrnCount,
      duplicateGroups: result.duplicateGroups,
      cyclicComponents: result.cyclicComponents.length,
      unresolvedRefTargets: Object.keys(result.unresolvedRefs).length,
      identityRoot: result.corpusIdentityRoot,
      ms: Date.now() - t0,
    });
    console.log(JSON.stringify(summary[summary.length - 1]));
  }
  console.log(JSON.stringify({ mintToolHash: toolHash, totalMinted: summary.reduce((a, s) => a + (s["minted"] as number), 0) }));
}

// ESM entrypoint check
if (process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href) {
  main(process.argv.slice(2));
}
