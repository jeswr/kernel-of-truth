#!/usr/bin/env node
// Snapshot-pack builder (bead kernel-of-truth-6j5): ONE content-addressed
// artifact a consumer downloads, like a tokenizer file.
//
//   node tools/pack/build-pack.mjs [--date YYYY-MM-DD]
//
// Layout inside kernel-snapshot-<date>.tar.zst:
//   kernel-snapshot-<date>/
//     SNAPSHOT.json                     generation, per-corpus {count, identityRoot,
//                                       profileHeader, licence, sourcePin}, tool hashes
//     verify.mjs                        self-verification (re-canonicalise + compare)
//     corpora/<name>/canonical-jcs.jsonl   the canonical identity bytes (hash inputs)
//     corpora/<name>/minted-urns.jsonl     sourceId -> urn:kot: map
//     corpora/<name>/manifest.json         corpus manifest incl. minting block
//     corpora/<name>/records/...           full records (annotations included)
//
// Staging uses HARD LINKS (same filesystem) so the pack costs no extra disk
// beyond the compressed artifact. The pack binary is force-added to git
// (26.9 MB < the 50 MB no-commit threshold; the box is ephemeral, the repo is
// the persistence layer); its sha256 is recorded in SNAPSHOT-RECEIPT.md.
// A GitHub-release copy is the consumer-facing home (bead kernel-of-truth-74r).

import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, linkSync, copyFileSync, writeFileSync, readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, "..", "..");
const DATA = join(REPO, "data");
const DIST = join(REPO, "dist");
const CANONICAL = join(DIST, "canonical");

const dateArg = (() => {
  const i = process.argv.indexOf("--date");
  return i >= 0 ? process.argv[i + 1] : "2026-07-07";
})();
const PACKNAME = `kernel-snapshot-${dateArg}`;
const STAGE = join(DIST, PACKNAME);

// corpus -> {records: [paths...], licence, sourcePin}
function manifestOf(name, file = "manifest.json") {
  return JSON.parse(readFileSync(join(DATA, name, file), "utf8"));
}

const REPO_LICENCE = "MIT (repo LICENSE; agent-authored programme records, (c) 2026 Jesse Wright)";

const CORPORA = {
  "kernel-v0": {
    records: () => listDir(join(DATA, "kernel-v0", "concepts")),
    licence: REPO_LICENCE,
    sourcePin: { authored: "in-repo (git); validated against encoder content-hash in manifest" },
  },
  "math-v0": {
    records: () => listDir(join(DATA, "math-v0", "concepts")),
    licence: REPO_LICENCE,
    sourcePin: { authored: "in-repo (git); profile-M v0 per docs/design-math-sector.md" },
  },
  "math-mm": {
    records: () => ["syntax.jsonl", "definitions.jsonl", "axioms.jsonl"].map((f) => join(DATA, "math-mm", f)),
    licence: "set.mm content: public domain (CC0) per set.mm header; derived records MIT",
    sourcePin: manifestOf("math-mm").source,
  },
  "molecules-v0": {
    records: () => listDir(join(DATA, "molecules-v0", "molecules")),
    licence: REPO_LICENCE,
    sourcePin: { authored: "in-repo (git); gist s3.5 molecule rules" },
  },
  "physics-v0": {
    records: () =>
      ["dimensions", "quantitykinds", "units", "constants", "equations"].flatMap((d) => listDir(join(DATA, "physics-v0", d), d)),
    licence: REPO_LICENCE + "; definitional values re-derived from SI Brochure 9th ed. (BIPM 2019)",
    sourcePin: { authored: "in-repo (git); SI Brochure 9th ed. exact values" },
  },
  "physics-qudt": {
    records: () => ["quantitykinds.jsonl", "units.jsonl"].map((f) => join(DATA, "physics-qudt", f)),
    licence: "QUDT vocabularies CC BY 4.0 (qudt.org); derived records with attribution",
    sourcePin: manifestOf("physics-qudt").source,
  },
  "lexical-wn31": {
    records: () => ["synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl"].map((f) => join(DATA, "lexical-wn31", f)),
    licence: "WordNet 3.1, Copyright 2011 Princeton University (WordNet licence: redistribution with notice permitted, AS IS)",
    sourcePin: { archive: "wn3.1.dict.tar.gz", sha256: "3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a", files: manifestOf("lexical-wn31").sourceFiles },
  },
  "onto-obo": {
    records: () => ["bfo.jsonl", "ro.jsonl", "go.jsonl"].map((f) => join(DATA, "onto-obo", f)),
    licence: "BFO CC BY 4.0; RO CC0 1.0; GO CC BY 4.0 (attribution: Gene Ontology Consortium, geneontology.org)",
    sourcePin: { files: manifestOf("onto-obo").sourceFiles },
  },
  "onto-sumo": {
    records: () => ["axioms.jsonl", "terms.jsonl"].map((f) => join(DATA, "onto-sumo", f)),
    licence: "IEEE SUMO licence (permissive; redistribution + derivatives with IEEE attribution)",
    sourcePin: manifestOf("onto-sumo").source,
  },
  "onto-framenet": {
    records: () => ["frames.jsonl", "frame-relations.jsonl"].map((f) => join(DATA, "onto-framenet", f)),
    licence: "FrameNet 1.7 CC BY 3.0 Unported (attribution: Baker, Fillmore & Lowe 1998; Berkeley FrameNet, ICSI)",
    sourcePin: manifestOf("onto-framenet").source,
  },
  "haiku-tier": {
    // the frozen snapshot the mint pass ran over — NOT the live records/ dir
    records: () => listDir(join(DIST, "haiku-frozen")),
    licence: REPO_LICENCE + "; modelAuthored (claude-haiku) pilot records; source defs Wiktionary/Wikipedia (CC BY-SA, annotation-layer only)",
    sourcePin: { stream: "LIVE pilot snapshot 2026-07-07; records/ still being written by the volume runner; see mint-manifest.json" },
    manifestFile: "mint-manifest.json",
  },
};

function listDir(dir, subPrefix = "") {
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json") || f.endsWith(".jsonl"))
    .sort()
    .map((f) => join(dir, f))
    .map((p) => (subPrefix ? { path: p, sub: subPrefix } : p));
}

function link(src, dest) {
  mkdirSync(dirname(dest), { recursive: true });
  try {
    linkSync(src, dest);
  } catch {
    copyFileSync(src, dest); // cross-device fallback
  }
}

function sha256File(path) {
  const h = createHash("sha256");
  h.update(readFileSync(path));
  return h.digest("hex");
}

// ---- stage ----
rmSync(STAGE, { recursive: true, force: true });
mkdirSync(join(STAGE, "corpora"), { recursive: true });

const snapshotCorpora = {};
let totalRecords = 0;

for (const [name, cfg] of Object.entries(CORPORA)) {
  const cdir = join(STAGE, "corpora", name);
  mkdirSync(join(cdir, "records"), { recursive: true });

  link(join(CANONICAL, `${name}.canonical.jsonl`), join(cdir, "canonical-jcs.jsonl"));
  link(join(DATA, name, "minted-urns.jsonl"), join(cdir, "minted-urns.jsonl"));
  const manifestFile = cfg.manifestFile ?? "manifest.json";
  link(join(DATA, name, manifestFile), join(cdir, "manifest.json"));

  for (const entry of cfg.records()) {
    const p = typeof entry === "string" ? entry : entry.path;
    const sub = typeof entry === "string" ? "" : entry.sub;
    link(p, join(cdir, "records", sub ? `${sub}-${basename(p)}` : basename(p)));
  }

  const manifest = JSON.parse(readFileSync(join(cdir, "manifest.json"), "utf8"));
  const minting = manifest.minting;
  if (!minting) throw new Error(`no minting block for ${name}`);
  snapshotCorpora[name] = {
    count: minting.mintedCount,
    identityRoot: minting.corpusIdentityRoot,
    profileHeader: minting.profileHeader,
    referenceMode: minting.referenceMode,
    licence: cfg.licence,
    sourcePin: cfg.sourcePin,
  };
  totalRecords += minting.mintedCount;
}

// verify.mjs ships inside the pack
copyFileSync(join(HERE, "verify.mjs"), join(STAGE, "verify.mjs"));

// tool hashes: mint tool (as recorded in manifests — assert consistency) + pack tool
const mintHashes = new Set(
  Object.keys(CORPORA).map((name) => JSON.parse(readFileSync(join(STAGE, "corpora", name, "manifest.json"), "utf8")).minting.mintToolHash),
);
if (mintHashes.size !== 1) throw new Error(`inconsistent mintToolHash across manifests: ${[...mintHashes]}`);
const packToolHash = createHash("sha256")
  .update(readFileSync(join(HERE, "build-pack.mjs")))
  .update(readFileSync(join(HERE, "verify.mjs")))
  .digest("hex");

const SNAPSHOT = {
  name: PACKNAME,
  generation: 1,
  date: dateArg,
  urnScheme: "urn:kot:<multibase 'b' base32(multihash sha2-256)>; hash input = UTF8(profileHeader) || RFC8785-JCS(NFC(identity payload)); cyclic SCCs per gist s6 component algorithm (JCS variant, #self/#intra/#member-i sentinels, member digest = H(header#member || X_raw || uvarint(i)))",
  identityRootAlgorithm:
    "binary Merkle over unique minted URNs sorted by UTF-16 code unit; leaf=sha256(utf8(urn)); parent=sha256(left||right); odd node promoted; hex root",
  designRecord: "docs/design-hash-input.md @ jeswr/kernel-of-truth",
  corpora: snapshotCorpora,
  totalRecords,
  mintToolHash: [...mintHashes][0],
  packToolHash,
  verification: "node verify.mjs           # full re-canonicalisation of all records\nnode verify.mjs --sample 1000   # per-corpus sample",
  unminted: {
    "math-lean-sample": "lean-ref/1 formal reference records mint no concept ids by signed design (docs/design-lean-route.md)",
  },
};
writeFileSync(join(STAGE, "SNAPSHOT.json"), JSON.stringify(SNAPSHOT, null, 2) + "\n");

// ---- compress (byte-reproducible) ----
// Deterministic tar: sorted member order, pinned mtime (the snapshot date),
// numeric owner 0:0, POSIX format. zstd level pinned at 12, single-threaded
// (level 19 was tried and ran ~0.5 MB/min on this contended 2-core box for a
// marginal size win; 12 keeps the artifact within a couple of MB of it).
// Given identical staged file bytes, the .tar.zst reproduces byte-identically
// — so the SNAPSHOT-RECEIPT sha256 remains checkable after a rebuild.
const tarZst = join(DIST, `${PACKNAME}.tar.zst`);
rmSync(tarZst, { force: true });
execFileSync(
  "nice",
  [
    "-n", "10",
    "tar",
    "--format=posix",
    "--sort=name",
    `--mtime=${dateArg} 00:00:00 UTC`,
    "--owner=0", "--group=0", "--numeric-owner",
    "--pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime",
    "--zstd",
    "-cf", tarZst,
    "-C", DIST, PACKNAME,
  ],
  { stdio: "inherit", env: { ...process.env, ZSTD_CLEVEL: "12" } },
);

const packSha = sha256File(tarZst);
const size = statSync(tarZst).size;
console.log(JSON.stringify({ pack: tarZst, bytes: size, mb: +(size / 1048576).toFixed(1), sha256: packSha, totalRecords }, null, 2));
