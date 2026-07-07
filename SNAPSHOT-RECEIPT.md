# SNAPSHOT-RECEIPT — kernel-snapshot-2026-07-07 (generation 1)

The snapshot pack is the primary kernel distribution (design-review change 4,
bead `kernel-of-truth-6j5`): ONE self-verifying artifact a consumer downloads,
like a tokenizer file. Built by `tools/pack/build-pack.mjs` from the minting
pass recorded in each corpus manifest's `minting` block
(bead `kernel-of-truth-mud`; spec: `docs/design-hash-input.md`).

## Artifact

| | |
|---|---|
| file | `dist/kernel-snapshot-2026-07-07.tar.zst` (committed — 26.9 MB < 50 MB threshold; box is ephemeral) |
| sha256 | `1955cea145a13927d2216d41ac2de142d150ddfaa1cb7073b9efb325e3d8ab39` |
| size | 28,254,137 bytes (26.9 MiB compressed; 243 MiB unpacked) |
| records | **185,776** across 11 corpora (JCS canonical identity bytes + full records + minted-urns + manifests) |
| mintToolHash | `e07bc2acf525ab0dad61e40bf97f30353ff9a0e820b74d85a2c3fc42d9190fef` (sha256 over tools/mint/src/*.ts) |
| packToolHash | see `SNAPSHOT.json` inside the pack (sha256 over build-pack.mjs + verify.mjs) |
| reproducibility | deterministic tar (`--sort=name`, pinned `--mtime=2026-07-07`, owner 0:0, POSIX format) + zstd level 12 single-threaded: **two builds byte-identical** (same sha256) |

## Per-corpus contents

| corpus | records | profile header | ref mode | identityRoot (Merkle, sha256-hex) |
|---|---:|---|---|---|
| kernel-v0 | 54 | `kot-ast/1` | substitute | `bb321a780a045ebb8b62eb646f673b156bb0e43149840b0055da1f90ef1288e4` |
| math-v0 | 39 | `kot-pm-ast/1` | substitute | `a8dba2af30668d90d60dd27bb7f99bc46a0e4573b777f807028f746c480fca5c` |
| math-mm | 2,998 | `kot-pm-mm/1` | substitute (1 cyclic SCC: df-cleq/df-clel) | `465c638fe52b706c3e921e59754d9ceeb630699094872b48e27f95e12ebf7deb` |
| molecules-v0 | 54 | `kot-mol/1` | stable | `7de9cb9326d0bccf2a7fd125b893aa76daee5c9de0382e3476c29d268951a155` |
| physics-v0 | 83 | `kot-phys/1` | substitute (25 qk-unit 2-cycles) | `2b5852fa43a2c5210268bc339cd699733ddf04d376b47076e8c51c0248bde116` |
| physics-qudt | 3,070 | `kot-phys/1` | substitute | `d2273f986eafd63ac63061edb0271540e08377fd3993f038e5929a3760e3d842` |
| lexical-wn31 | 117,791 | `kot-lex/1` | stable (non-DAG) | `e68610ac8602b12df88beb5eefacaa574c41818d5e408f6e5475b2f582e62fe1` |
| onto-obo | 39,012 | `kot-obo/1` | substitute (49 SCCs, max 11) | `f8fb3edde8bfe348a204306128b7fe8ce7a0feb948e60443cf9aade1ac9ee3b0` |
| onto-sumo | 19,300 | `kot-sumo/1` | stable (KIF strings) | `4bda1149f63f203c1fb029d67f8a6149247686c5bc252eb5281bdb236be66d2d` |
| onto-framenet | 3,291 | `kot-framenet/1` | substitute | `fb06d17be6be4e85c0e6feaa7b954cb82709156717d91d40456fac0908d905d9` |
| haiku-tier | 84 | `kot-haiku/1` | stable (live-stream snapshot) | `cacb2a494195a4cf11bd93fe3abeaf17f86673418fe2a4ec21e7b9025be93085` |

Note (haiku-tier): minted from a frozen 2026-07-07 snapshot of a LIVE stream —
the volume runner was still writing `data/haiku-tier/records/` while this pack
was built, so the corpus will grow past 84 records. Incremental re-mint
tooling is bead `kernel-of-truth-lik`.

Unminted by signed design: `math-lean-sample` (70 lean-ref/1 records are
annotation-layer formal references; `docs/design-lean-route.md` decision 1
mints no concept ids for them).

## Verification performed (2026-07-07)

1. **RFC 8785 conformance**: mint-tool JCS core passes the RFC's own Appendix B
   number table (24 IEEE-754 vectors), the s3.2.3 property-sorting test object,
   and the s3.2.4 worked example's expected UTF-8 bytes (13/13 unit tests).
2. **Mint determinism**: two full mint runs over all corpora byte-identical
   (minted-urns, manifests, canonical JCS bytes).
3. **Independent recomputation**: 4 URNs recomputed in Python (separate
   implementation), including both members of the df-cleq/df-clel cyclic
   component — all match.
4. **Pack reproducibility**: two `build-pack.mjs` runs → identical sha256.
5. **End-to-end**: pack unpacked in a clean temp dir; `node verify.mjs` (full,
   not sampled) re-canonicalised all 185,776 records, recomputed every URN and
   all 11 Merkle roots — `VERIFIED generation=1 totalRecords=185776`.
6. **Fail-closed**: single-byte payload mutation → verifier exits 1 with the
   mismatching URN reported.

## Consume

```sh
tar --zstd -xf kernel-snapshot-2026-07-07.tar.zst
cd kernel-snapshot-2026-07-07
node verify.mjs                 # full self-verification (Node >= 18, zero deps)
node verify.mjs --sample 1000   # quick per-corpus sample
```

## Rebuild from repo

```sh
cd tools/mint && npm install && npm run build && cd ../..
node tools/mint/dist/src/cli.js --data data --out dist/canonical --haiku-records <frozen-records-dir>
node tools/pack/build-pack.mjs --date 2026-07-07
```

Hosting as a GitHub release asset: bead `kernel-of-truth-74r`.
