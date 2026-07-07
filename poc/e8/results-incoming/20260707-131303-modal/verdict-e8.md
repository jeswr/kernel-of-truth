# E8 — kernel<->SAE alignment: verdict

date: 2026-07-07T13:45:30.653158+00:00  |  mock: False  |  seed: 20260707  |  perms: 10000 (retrieval 2000)  |  kernel: jl512
encoder: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`
families: famA=gpt2, famB=pythia-160m

**Pre-registered criterion (docs/poc-design.md E8, verbatim):**
> Align kernel geometry to SAE feature dictionaries across >=2 open model families (projected path, X4 distortion reported); criterion: kernel coordinates predict cross-model feature correspondence beyond shuffled-kernel and permutation nulls.

Projected path: jl512 primary; inherited X4 RDM-Spearman distortion 0.9718 (8192->512), 0.9706 (8192->576).

## OUTCOME: **PASS (kernel coordinates predict cross-model feature correspondence beyond shuffled-kernel and permutation nulls)**

- items analysed: 51 (zero-signature drops: none)
- gate G (kernel-free correspondence): acc 0.0686 (chance 0.0196; A->B 0.0980, B->A 0.0392), p 0.00130
- P1 Spearman(K_jl512, X_sym): rho 0.3857, p 0.00010 (PASS at 0.01)
- P2 partial | orig3: rho 0.3603, p 0.00010 (PASS at 0.01)

## Secondaries (Holm-corrected)

| test | stat | p | p_holm | reject@0.05 |
|---|---|---|---|---|
| S1_partial_orig3+emb4_vs_Xsym | 0.2998 | 0.00010 | 0.00050 | yes |
| S2_partial_orig3_vs_S_famA | 0.4039 | 0.00010 | 0.00050 | yes |
| S3_partial_orig3_vs_S_famB | 0.1707 | 0.00040 | 0.00120 | yes |
| S4_retrieval_famA | 0.0980 | 0.00250 | 0.00500 | yes |
| S5_retrieval_famB | 0.0588 | 0.03248 | 0.03248 | yes |

## Sensitivity (descriptive; P2 form, kernel variants)

- full: rho 0.3748, p 0.00010
- jl576: rho 0.3594, p 0.00010

## Diagnostics

- gpt2: FVU 0.1511, mean L0 49.6, span tokens 1248
- pythia-160m: FVU 0.2095, mean L0 32.0, span tokens 1344

Nulls note: shuffled-kernel == Mantel concept-label permutation at the RDM level (P K P^T); one permutation scheme implements both pre-registered nulls.
Scope: ONE family pair == ONE primary test; a PASS licenses exactly this pair. Pre-named weaknesses (poc/e8/README.md §6) apply, in particular: the SAE sees the exponent WORD in synthetic contexts, never the explication.
