# E8 extension 1 — third-family replication: verdict

date: 2026-07-07T15:36:30.152786+00:00  |  mock: False  |  seed: 20260707  |  perms: 10000 (retrieval 2000)  |  kernel: jl512
encoder: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`

**Pre-registered criterion (docs/poc-design.md E8, verbatim):**
> Align kernel geometry to SAE feature dictionaries across >=2 open model families (projected path, X4 distortion reported); criterion: kernel coordinates predict cross-model feature correspondence beyond shuffled-kernel and permutation nulls.

**Pre-registered replication rule (README §Extension 1, verbatim):**
> the extension REPLICATES iff BOTH new pairs pass P1 AND P2 (p<0.01) with gates passed; anything weaker is reported per-pair, verbatim, no cherry-picking

Family C: HuggingFaceTB/SmolLM2-135M + EleutherAI/sae-SmolLM2-135M-64x (layers.15.mlp, eleuther_topk, d_sae 36864) — MLP-output site; the site mismatch vs the residual-stream families A/B is a named confound (conservative direction).
Family C diagnostics: FVU 0.3274, mean L0 32.0; in-vocab drops: none; zero signatures: none.
Families A/B signatures reused byte-identically from `poc/e8/results-incoming/20260707-131303-modal` (sha-asserted).

## OUTCOME: **NOT REPLICATED (per-pair outcomes reported verbatim)**

| pair | items | gate acc (p) | P1 rho (p) | P2 rho (p) | pair outcome |
|---|---|---|---|---|---|
| gpt2|smollm2-135m | 51 | 0.0980 (0.00010) | 0.0089 (0.39056) | 0.0198 (0.29577) | NULL (no kernel signal on the correspondence structure) |
| pythia-160m|smollm2-135m | 51 | 0.0882 (0.00010) | 0.0614 (0.08659) | 0.0740 (0.05569) | NULL (no kernel signal on the correspondence structure) |

## Holm secondaries per pair

**gpt2|smollm2-135m**

| test | stat | p | p_holm | reject@0.05 |
|---|---|---|---|---|
| S1_partial_orig3+emb4_vs_Xsym | -0.0652 | 0.95180 | 1.00000 | no |
| S2_partial_orig3_vs_S_famA | 0.4039 | 0.00010 | 0.00050 | yes |
| S3_partial_orig3_vs_S_famB | -0.0148 | 0.59834 | 1.00000 | no |
| S4_retrieval_famA | 0.0980 | 0.00250 | 0.01000 | yes |
| S5_retrieval_famB | 0.0196 | 0.56122 | 1.00000 | no |

**pythia-160m|smollm2-135m**

| test | stat | p | p_holm | reject@0.05 |
|---|---|---|---|---|
| S1_partial_orig3+emb4_vs_Xsym | -0.0183 | 0.64094 | 1.00000 | no |
| S2_partial_orig3_vs_S_famA | 0.1707 | 0.00040 | 0.00200 | yes |
| S3_partial_orig3_vs_S_famB | -0.0148 | 0.59834 | 1.00000 | no |
| S4_retrieval_famA | 0.0588 | 0.03248 | 0.12994 | no |
| S5_retrieval_famB | 0.0196 | 0.56122 | 1.00000 | no |

Scope: these are pairs 2 and 3 of three, all at toy/small-model scale; family C is an MLP-site dictionary. Pre-named weaknesses (poc/e8/README.md §6 + §Extension 1) apply unchanged.
