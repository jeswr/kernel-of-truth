// Incremental re-mint / delta detection (bead kernel-of-truth-lik).
//
//   node dist/src/incremental.js --data <repo>/data --corpus <name> [--write] [--allow-changes]
//
// The mint is a DETERMINISTIC PURE FUNCTION of the corpus (docs/design-hash-input.md):
// every URN depends only on record identity-payload bytes (stable mode) or on
// those bytes with intra-corpus refs substituted by already-minted URNs
// (substitute mode). A full re-mint therefore always yields the canonical answer;
// "incremental" here means *computing and gating the delta* against the currently
// committed `minted-urns.jsonl`, not skipping deterministic work.
//
// The delta is classified into four sets keyed by sourceId:
//   * added   — in the new mint, not in the committed set (new source records).
//   * removed — in the committed set, not in the new mint (deleted source records).
//   * changed — in both, but the URN differs. THIS IS THE RE-MINT CONE:
//       - stable mode    : the record's own identity payload changed.
//       - substitute mode: the record changed OR a dependency's URN changed
//                          (its ancestor cone in the reference DAG). A full
//                          deterministic re-mint resolves the whole cone; this
//                          set names exactly which committed URNs it moved.
//   * stable  — in both, same URN (URN-stability guarantee holds for these).
//
// Generation semantics (gist §8): `changed.length === 0` => same-generation
// growth (added/removed only) — no generation bump. `changed.length > 0` =>
// a re-ingestion changed existing identities — a new snapshot/generation is
// required, and --write refuses unless --allow-changes is passed (fail closed).

import { mkdtempSync, mkdirSync, copyFileSync, existsSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { makeSpecs, CorpusSpec } from "./corpora.js";
import { mintCorpus, main as mintMain } from "./cli.js";

interface Delta {
  corpus: string;
  refMode: string;
  committedCount: number;
  newCount: number;
  added: string[];
  removed: string[];
  changed: Array<{ sourceId: string; from: string; to: string }>;
  stableCount: number;
  duplicateGroups: number;
  cyclicComponents: number;
  generation: "same-generation-growth" | "re-ingestion-changed-identities" | "empty-corpus";
}

function readMinted(path: string): Map<string, string> {
  const m = new Map<string, string>();
  if (!existsSync(path)) return m;
  for (const line of readFileSync(path, "utf8").split("\n")) {
    const t = line.trim();
    if (!t) continue;
    const r = JSON.parse(t) as { sourceId: string; urn: string };
    m.set(r.sourceId, r.urn);
  }
  return m;
}

// Dry-run mint into a throwaway dir; returns the freshly-minted sourceId->urn map
// plus the honesty counters, WITHOUT touching any committed file.
export function computeDelta(spec: CorpusSpec, dataRoot: string): Delta {
  const committed = readMinted(join(spec.outDir, "minted-urns.jsonl"));
  const tmp = mkdtempSync(join(tmpdir(), `kot-remint-${spec.name}-`));
  try {
    const dry: CorpusSpec = { ...spec, outDir: tmp };
    const { result, rows } = mintCorpus(dry, dataRoot, tmp);
    const fresh = new Map<string, string>();
    for (const r of rows) fresh.set(r.sourceId, r.urn);

    const added: string[] = [];
    const changed: Array<{ sourceId: string; from: string; to: string }> = [];
    let stableCount = 0;
    for (const [sid, urn] of fresh) {
      const prev = committed.get(sid);
      if (prev === undefined) added.push(sid);
      else if (prev !== urn) changed.push({ sourceId: sid, from: prev, to: urn });
      else stableCount++;
    }
    const removed: string[] = [];
    for (const sid of committed.keys()) if (!fresh.has(sid)) removed.push(sid);

    added.sort();
    removed.sort();
    changed.sort((a, b) => (a.sourceId < b.sourceId ? -1 : a.sourceId > b.sourceId ? 1 : 0));

    const generation: Delta["generation"] =
      fresh.size === 0 ? "empty-corpus" : changed.length > 0 ? "re-ingestion-changed-identities" : "same-generation-growth";

    return {
      corpus: spec.name,
      refMode: spec.refMode,
      committedCount: committed.size,
      newCount: fresh.size,
      added,
      removed,
      changed,
      stableCount,
      duplicateGroups: result.duplicateGroups,
      cyclicComponents: result.cyclicComponents.length,
      generation,
    };
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

function archiveCommitted(spec: CorpusSpec): string | null {
  const minted = join(spec.outDir, "minted-urns.jsonl");
  if (!existsSync(minted)) return null;
  const ts = new Date().toISOString().replace(/[:.]/g, "").replace("T", "T").slice(0, 15) + "Z";
  const dir = join(spec.outDir, "snapshots", `mint-archive-${ts}`);
  mkdirSync(dir, { recursive: true });
  copyFileSync(minted, join(dir, "minted-urns.jsonl"));
  const mm = join(spec.outDir, "mint-manifest.json");
  if (existsSync(mm)) copyFileSync(mm, join(dir, "mint-manifest.json"));
  return dir;
}

function summary(d: Delta): void {
  const brief = {
    corpus: d.corpus,
    refMode: d.refMode,
    committed: d.committedCount,
    new: d.newCount,
    added: d.added.length,
    removed: d.removed.length,
    changedCone: d.changed.length,
    stable: d.stableCount,
    duplicateGroups: d.duplicateGroups,
    cyclicComponents: d.cyclicComponents,
    generation: d.generation,
  };
  console.log(JSON.stringify(brief));
  if (d.changed.length > 0) {
    console.log(JSON.stringify({ changedConeSample: d.changed.slice(0, 20) }));
  }
}

export function main(argv: string[]): void {
  const args = new Map<string, string[]>();
  let key = "";
  for (const a of argv) {
    if (a.startsWith("--")) {
      key = a.slice(2);
      if (!args.has(key)) args.set(key, []);
    } else if (key) args.get(key)!.push(a);
  }
  const dataRoot = args.get("data")?.[0];
  const corpus = args.get("corpus")?.[0];
  const write = args.has("write");
  const allowChanges = args.has("allow-changes");
  if (!dataRoot || !corpus) {
    console.error("usage: incremental.js --data <repo>/data --corpus <name> [--write] [--allow-changes]");
    process.exit(2);
  }
  const spec = makeSpecs(dataRoot).find((s) => s.name === corpus);
  if (!spec) {
    console.error(`ERR_UNKNOWN_CORPUS: ${corpus}`);
    process.exit(2);
  }

  const delta = computeDelta(spec, dataRoot);
  summary(delta);

  if (delta.changed.length > 0 && !allowChanges) {
    console.error(
      `ERR_IDENTITY_CHANGED: ${delta.changed.length} committed URN(s) would change (re-mint cone). ` +
        `This is a re-ingestion (gist §8 new generation), not pure growth. ` +
        `Re-run with --allow-changes once a generation bump / new snapshot pack is intended.`,
    );
    if (write) process.exit(3);
    return;
  }

  if (!write) return;

  const archived = archiveCommitted(spec);
  // Delegate the real write (minted-urns.jsonl + manifest refresh) to the pinned
  // mint CLI so byte-output and manifest semantics are identical to a full mint.
  const canonTmp = mkdtempSync(join(tmpdir(), `kot-canon-${corpus}-`));
  mintMain(["--data", dataRoot, "--out", canonTmp, "--corpus", corpus]);
  rmSync(canonTmp, { recursive: true, force: true });
  console.log(JSON.stringify({ wrote: join(spec.outDir, "minted-urns.jsonl"), archivedPrevious: archived }));
}

if (process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href) {
  main(process.argv.slice(2));
}
