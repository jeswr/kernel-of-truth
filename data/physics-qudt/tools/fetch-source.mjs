#!/usr/bin/env node
/**
 * Fetch + pin-verify the QUDT source vocabularies for physics-qudt.
 *
 * Downloads the pinned release zip from GitHub, verifies its sha256, extracts
 * the four vocabulary TTL files into ../source/ (flat), verifies each file's
 * sha256 against the pins, then deletes the zip (disk discipline: <= 1 GB
 * working set; the zip is ~11 MB, the TTLs ~6 MB).
 *
 * Usage: node tools/fetch-source.mjs [--dest <dir>]
 * Requires: network access + `unzip` on PATH.
 */
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, rmSync, existsSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const argOf = (k, dflt) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : dflt; };
const dest = argOf('--dest', join(here, '..', 'source'));

// pins — MUST match tools/extract.mjs SOURCE (single source of truth is the manifest)
const manifest = JSON.parse(readFileSync(join(here, '..', 'manifest.json'), 'utf8'));
const SRC = manifest.source;
const url = `https://github.com/qudt/qudt-public-repo/releases/download/${SRC.release}/${SRC.zip}`;

mkdirSync(dest, { recursive: true });
const zipPath = join(dest, SRC.zip);
if (!existsSync(zipPath)) {
  console.error(`fetching ${url}`);
  execFileSync('curl', ['-fsSL', '-o', zipPath, url], { stdio: 'inherit' });
}
const sha = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');
if (sha(zipPath) !== SRC.zipSha256) {
  console.error(`ERR_SOURCE_PIN: ${SRC.zip} sha256 ${sha(zipPath)} != pinned ${SRC.zipSha256}`);
  process.exit(1);
}
const members = Object.values(SRC.files).map((f) => f.path);
execFileSync('unzip', ['-o', '-j', zipPath, ...members, '-d', dest], { stdio: 'inherit' });
let ok = true;
for (const f of Object.values(SRC.files)) {
  const p = join(dest, basename(f.path));
  const got = sha(p);
  if (got !== f.sha256) { console.error(`ERR_SOURCE_PIN: ${p} sha256 ${got} != pinned ${f.sha256}`); ok = false; }
  else console.error(`ok ${basename(f.path)} ${got.slice(0, 12)}…`);
}
rmSync(zipPath); // clean intermediates
if (!ok) process.exit(1);
console.error(`source ready in ${dest} (release ${SRC.release}, commit ${SRC.commit.slice(0, 12)})`);
