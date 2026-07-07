#!/usr/bin/env python3
"""E2 post-hoc re-analysis statistics (design-review change 1; beads qha + avt).

    python3 poc/e2/reanalysis/analyze.py poc/e2/results-incoming/<stamp>-reanalysis

Consumes the Modal extraction (rdms-reanalysis.json) + the committed E2 inputs
and the committed original results (for the reproduction check), and writes
results-e2-reanalysis.json + verdict-e2-reanalysis.md into the stamp dir.

All stats primitives (rankdata / spearman / pearson / offdiag / PartialSpearman)
are IMPORTED from poc/e2/runner/e2_runner.py — no forked implementations.
Analysis plan + decision rules were fixed in poc/e2/reanalysis/README.md BEFORE
the extraction ran. Null convention: permute the concept labels of the TESTED
RDM only (kernel in forward tests, embedding RDM in reverse tests); model and
covariate RDMs stay fixed; one-sided p = (1+#{perm >= obs})/(1+N); each test
uses a fresh np.random.default_rng(SEED) so every test is independently
reproducible and all tests share one permutation sequence.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
E2_DIR = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(E2_DIR, "runner"))
import e2_runner as r  # noqa: E402

SEED = r.SEED                # 20260707, same discipline as the original run
N_PERM = r.N_PERM            # 10^4
ALPHA = r.ALPHA_PARTIAL      # 0.01
PRIMARY_KERNEL = r.PRIMARY_KERNEL  # jl512
ORIGINAL_RESULTS = os.path.join(E2_DIR, "results-incoming", "20260707-091305-modal", "results-e2.json")
ORIGINAL_VERDICT = os.path.join(E2_DIR, "results-incoming", "20260707-091305-modal", "verdict-e2.md")

EMB4 = ["glossEmb.minilm", "glossEmb.bge", "explEmb.minilm", "explEmb.bge"]
WORD2 = ["wordEmb.minilm", "wordEmb.bge"]


def offdiag_perm(sim: np.ndarray, perm: np.ndarray) -> np.ndarray:
    return r.offdiag(sim[np.ix_(perm, perm)])


def mantel(tested_sim: np.ndarray, stat_fn, n_perm: int = N_PERM) -> dict:
    """One-sided label-permutation test; permutes the TESTED matrix only."""
    rng = np.random.default_rng(SEED)
    n = tested_sim.shape[0]
    obs = stat_fn(r.offdiag(tested_sim))
    exceed = 0
    for _ in range(n_perm):
        p = rng.permutation(n)
        if stat_fn(offdiag_perm(tested_sim, p)) >= obs:
            exceed += 1
    return {"rho": float(obs), "p": (1.0 + exceed) / (1.0 + n_perm)}


class MaskedPartial:
    """Partial Spearman restricted to a fixed set of off-diagonal cells.

    mask indexes the off-diagonal vector (upper triangle order). Ranks are
    computed WITHIN the masked cells; covariates + model stay fixed to cells,
    the tested matrix's labels permute (mask follows the fixed side).
    """

    def __init__(self, cov_ods: list, model_od: np.ndarray, mask: np.ndarray):
        self.mask = mask
        cols = [np.ones(int(mask.sum()))] + [r.rankdata(c[mask]) for c in cov_ods]
        self.q, _ = np.linalg.qr(np.column_stack(cols))
        self.model_resid = self._resid(model_od[mask])

    def _resid(self, v: np.ndarray) -> np.ndarray:
        rk = r.rankdata(v)
        return rk - self.q @ (self.q.T @ rk)

    def stat(self, tested_od: np.ndarray) -> float:
        return r.pearson(self._resid(tested_od[self.mask]), self.model_resid)


class MaskedSpearman:
    def __init__(self, model_od: np.ndarray, mask: np.ndarray):
        self.mask = mask
        self.model_ranks = r.rankdata(model_od[mask])

    def stat(self, tested_od: np.ndarray) -> float:
        return r.pearson(r.rankdata(tested_od[self.mask]), self.model_ranks)


def load_all(stamp_dir: str) -> tuple:
    with open(os.path.join(stamp_dir, "rdms-reanalysis.json")) as f:
        rd = json.load(f)
    inp = r.load_inputs(os.path.join(E2_DIR, "inputs"))
    if rd["ids"] != [it["id"] for it in inp["items"]["items"]]:
        raise SystemExit("ERR_ITEM_ORDER: extraction ids differ from items.json")
    if rd["encoderContentHash"] != inp["items"]["encoderContentHash"]:
        raise SystemExit("ERR_PIN_MISMATCH: extraction encoder hash differs from inputs")
    with open(ORIGINAL_RESULTS) as f:
        orig = json.load(f)
    return rd, inp, orig


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    stamp_dir = sys.argv[1].rstrip("/")
    rd, inp, orig = load_all(stamp_dir)

    kernels = r.kernel_matrices(inp)  # full / jl512 / jl576, 51x51 (analysis ids)
    orig3_ods = {
        "word2vec": r.offdiag(np.asarray(inp["word2vec"]["similarity"], dtype=np.float64)),
        "wordnet": r.offdiag(np.asarray(inp["wordnet"]["similarity"], dtype=np.float64)),
        "gloss": r.offdiag(np.asarray(inp["gloss"]["similarity"], dtype=np.float64)),
    }
    emb_sims = {}
    for emb_name, emb in rd["embedders"].items():
        for set_name, key in (("gloss", "glossEmb"), ("explication", "explEmb"), ("word", "wordEmb")):
            emb_sims[f"{key}.{emb_name}"] = np.asarray(
                emb["similarity_by_textset"][set_name], dtype=np.float64)
    emb_ods = {k: r.offdiag(v) for k, v in emb_sims.items()}

    has_not = np.asarray(rd["notCounts"], dtype=np.int64) > 0
    iu = np.triu_indices(len(has_not), k=1)
    pair_not = has_not[iu[0]].astype(int) + has_not[iu[1]].astype(int)
    masks = {
        "both-NOT": pair_not == 2,
        "one-NOT (polarity-divergent)": pair_not == 1,
        "neither-NOT": pair_not == 0,
    }

    cov_sets = {
        "orig3": list(orig3_ods.values()),
        **{f"orig3+{e}": list(orig3_ods.values()) + [emb_ods[e]] for e in EMB4},
        "orig3+emb4": list(orig3_ods.values()) + [emb_ods[e] for e in EMB4],
        "emb4": [emb_ods[e] for e in EMB4],
        **{f"{e} alone": [emb_ods[e]] for e in EMB4},
        **{f"orig3+{e}": list(orig3_ods.values()) + [emb_ods[e]] for e in WORD2},
        "orig3+emb4+word2": list(orig3_ods.values()) + [emb_ods[e] for e in EMB4 + WORD2],
    }

    per_model = {}
    for model_id, mdata in rd["models"].items():
        mid = str(mdata["mid_layer_index"])
        if mdata["in_vocab_dropped_words"]:
            raise SystemExit(f"ERR_ATTRITION_DRIFT: {model_id} dropped words in re-extraction")
        model_sim = np.asarray(mdata["similarity_by_layer"][mid], dtype=np.float64)
        model_od = r.offdiag(model_sim)
        kernel = kernels[PRIMARY_KERNEL]
        full_mask = np.ones(model_od.shape[0], dtype=bool)
        print(f"\n=== {model_id} (layer {mid}) ===", flush=True)

        # ---- reproduction check vs the committed run ----
        sp = mantel(kernel, MaskedSpearman(model_od, full_mask).stat)
        rep_partial = mantel(kernel, MaskedPartial(cov_sets["orig3"], model_od, full_mask).stat)
        committed = next(pm for pm in orig["per_model"] if pm["model"] == model_id)["primary"]
        repro = {
            "spearman": sp, "partial_orig3": rep_partial,
            "committed": {"spearman": committed["spearman"],
                          "partial_spearman": committed["partial_spearman"],
                          "partial_p": committed["partial_p"]},
            "delta_spearman": sp["rho"] - committed["spearman"],
            "delta_partial": rep_partial["rho"] - committed["partial_spearman"],
        }
        print(f"repro: rho {sp['rho']:.4f} (committed {committed['spearman']:.4f}), "
              f"partial {rep_partial['rho']:.4f} (committed {committed['partial_spearman']:.4f})", flush=True)

        # ---- forward battery: kernel beyond baselines ----
        forward = {}
        for name, covs in cov_sets.items():
            forward[name] = mantel(kernel, MaskedPartial(covs, model_od, full_mask).stat)
            print(f"forward kernel|{name}: rho {forward[name]['rho']:.4f} p {forward[name]['p']:.5f}", flush=True)

        # sensitivity: full-D + jl576 kernels on the joint set
        sensitivity = {
            kv: mantel(kernels[kv], MaskedPartial(cov_sets["orig3+emb4"], model_od, full_mask).stat)
            for kv in ("full", "jl576")
        }

        # ---- reverse battery: embeddings beyond kernel ----
        kernel_od = r.offdiag(kernel)
        reverse = {}
        for e in EMB4:
            tested = emb_sims[e]
            reverse[e] = {
                "spearman": mantel(tested, MaskedSpearman(model_od, full_mask).stat),
                "partial_kernel": mantel(tested, MaskedPartial([kernel_od], model_od, full_mask).stat),
                "partial_kernel+orig3": mantel(
                    tested, MaskedPartial([kernel_od] + list(orig3_ods.values()), model_od, full_mask).stat),
            }
            rv = reverse[e]
            print(f"reverse {e}: rho {rv['spearman']['rho']:.4f} | kernel {rv['partial_kernel']['rho']:.4f} "
                  f"(p {rv['partial_kernel']['p']:.5f}) | kernel+orig3 {rv['partial_kernel+orig3']['rho']:.4f} "
                  f"(p {rv['partial_kernel+orig3']['p']:.5f})", flush=True)

        # ---- polarity strata (bead avt) ----
        strata = {}
        for sname, mask in masks.items():
            strata[sname] = {
                "n_pairs": int(mask.sum()),
                "spearman": mantel(kernel, MaskedSpearman(model_od, mask).stat),
                "partial_orig3": mantel(kernel, MaskedPartial(cov_sets["orig3"], model_od, mask).stat),
                "partial_orig3+emb4": mantel(kernel, MaskedPartial(cov_sets["orig3+emb4"], model_od, mask).stat),
            }
            st = strata[sname]
            print(f"stratum {sname} (n={st['n_pairs']}): rho {st['spearman']['rho']:.4f} "
                  f"| orig3 {st['partial_orig3']['rho']:.4f} (p {st['partial_orig3']['p']:.5f}) "
                  f"| +emb4 {st['partial_orig3+emb4']['rho']:.4f} (p {st['partial_orig3+emb4']['p']:.5f})", flush=True)

        # item-subset RSA (restrict matrices to NOT / non-NOT items)
        subsets = {}
        for sname, sel in (("NOT-items", np.flatnonzero(has_not)),
                           ("non-NOT-items", np.flatnonzero(~has_not))):
            ksub = kernel[np.ix_(sel, sel)]
            msub_od = r.offdiag(model_sim[np.ix_(sel, sel)])
            sub_full = np.ones(msub_od.shape[0], dtype=bool)
            covs_o3 = [r.offdiag(np.asarray(inp[k]["similarity"], dtype=np.float64)[np.ix_(sel, sel)])
                       for k in ("word2vec", "wordnet", "gloss")]
            covs_e4 = covs_o3 + [r.offdiag(emb_sims[e][np.ix_(sel, sel)]) for e in EMB4]
            subsets[sname] = {
                "n_items": int(sel.size),
                "spearman": mantel(ksub, MaskedSpearman(msub_od, sub_full).stat),
                "partial_orig3": mantel(ksub, MaskedPartial(covs_o3, msub_od, sub_full).stat),
                "partial_orig3+emb4": mantel(ksub, MaskedPartial(covs_e4, msub_od, sub_full).stat),
            }
            su = subsets[sname]
            print(f"subset {sname} (n={su['n_items']}): rho {su['spearman']['rho']:.4f} "
                  f"| orig3 {su['partial_orig3']['rho']:.4f} (p {su['partial_orig3']['p']:.5f}) "
                  f"| +emb4 {su['partial_orig3+emb4']['rho']:.4f} (p {su['partial_orig3+emb4']['p']:.5f})", flush=True)

        per_model[model_id] = {
            "layer": int(mid), "repro": repro, "forward": forward,
            "kernel_variant_sensitivity_orig3emb4": sensitivity,
            "reverse": reverse, "pair_strata": strata, "item_subsets": subsets,
        }

    # ---- decision rules (fixed in README.md before extraction) ----
    fam = list(per_model)
    kernel_pass = [m for m in fam if per_model[m]["forward"]["orig3+emb4"]["p"] < ALPHA]
    kernel_beyond = len(kernel_pass) >= 2
    reverse_pass = {
        e: [m for m in fam if per_model[m]["reverse"][e]["partial_kernel+orig3"]["p"] < ALPHA]
        for e in EMB4 if e.startswith("explEmb")
    }
    expl_beyond = any(len(v) >= 2 for v in reverse_pass.values())

    out = {
        "experiment": "E2 re-analysis: sentence-embedding baselines + polarity strata (POST-HOC; design-review change 1)",
        "posture": "The original pre-registered E2 verdict stands as reported; this re-analysis is reported alongside it.",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "beads": ["kernel-of-truth-qha", "kernel-of-truth-avt"],
        "seed": SEED, "n_perm": N_PERM, "alpha": ALPHA,
        "primary_kernel_variant": PRIMARY_KERNEL,
        "pins": {"encoderContentHash": rd["encoderContentHash"], "corpusPin": rd["corpusPin"],
                 "rendererVersion": rd["rendererVersion"],
                 "embedders": {k: {kk: v[kk] for kk in ("hf_id", "pooling", "resolved_commit_hash")}
                               for k, v in rd["embedders"].items()}},
        "decision": {
            "kernel_beyond_embeddings": kernel_beyond,
            "kernel_pass_families_orig3emb4": kernel_pass,
            "explication_embedding_beyond_kernel": expl_beyond,
            "reverse_pass_families": reverse_pass,
        },
        "per_model": per_model,
    }
    jpath = os.path.join(stamp_dir, "results-e2-reanalysis.json")
    with open(jpath, "w") as f:
        json.dump(out, f, indent=2)
    write_verdict(stamp_dir, out)
    print(f"\nwrote {jpath}")
    print(f"kernel beyond embeddings (>=2 fam, p<{ALPHA}, orig3+emb4): {kernel_beyond} {kernel_pass}")
    print(f"explication-embedding beyond kernel: {expl_beyond} {reverse_pass}")


def write_verdict(stamp_dir: str, out: dict) -> None:
    with open(ORIGINAL_VERDICT) as f:
        original_verbatim = f.read().rstrip()
    L = [
        "# E2 re-analysis — sentence-embedding baselines + polarity strata",
        "",
        "**POST-HOC RE-ANALYSIS** (notes/panel-kernel-design-review.md change 1; beads "
        "kernel-of-truth-qha, kernel-of-truth-avt). The original pre-registered verdict "
        "below stands as reported; nothing here replaces it.",
        "",
        f"date: {out['date']}  |  seed: {out['seed']}  |  perms: {out['n_perm']}  |  "
        f"kernel: {out['primary_kernel_variant']}  |  layer: L/2",
        "embedders: " + "; ".join(
            f"{v['hf_id']} ({v['pooling']}, rev {str(v['resolved_commit_hash'])[:10]})"
            for v in out["pins"]["embedders"].values()),
        "",
        "## 1. Original pre-registered verdict (verbatim)",
        "",
        "```",
        original_verbatim,
        "```",
        "",
        "## 2. Reproduction check (re-extracted reps, same runner bytes/image/GPU class)",
        "",
        "| model | rho re-run | rho committed | partial(orig3) re-run | committed | delta partial |",
        "|---|---|---|---|---|---|",
    ]
    for m, pm in out["per_model"].items():
        rp = pm["repro"]
        L.append(f"| {m} | {rp['spearman']['rho']:.4f} | {rp['committed']['spearman']:.4f} "
                 f"| {rp['partial_orig3']['rho']:.4f} | {rp['committed']['partial_spearman']:.4f} "
                 f"| {rp['delta_partial']:+.4f} |")
    L += [
        "",
        "## 3. Forward: kernel partial rho (p) by covariate set",
        "",
        "| covariates | " + " | ".join(m.split('/')[-1] for m in out["per_model"]) + " |",
        "|---|" + "---|" * len(out["per_model"]),
    ]
    for name in next(iter(out["per_model"].values()))["forward"]:
        row = [name]
        for pm in out["per_model"].values():
            t = pm["forward"][name]
            row.append(f"{t['rho']:.4f} (p={t['p']:.4g})")
        L.append("| " + " | ".join(row) + " |")
    L += [
        "",
        "## 4. Reverse: embedding-RDM partial rho (p) vs model",
        "",
        "| tested RDM | control | " + " | ".join(m.split('/')[-1] for m in out["per_model"]) + " |",
        "|---|---|" + "---|" * len(out["per_model"]),
    ]
    first = next(iter(out["per_model"].values()))
    for e in first["reverse"]:
        for ctrl in ("spearman", "partial_kernel", "partial_kernel+orig3"):
            row = [e, ctrl]
            for pm in out["per_model"].values():
                t = pm["reverse"][e][ctrl]
                row.append(f"{t['rho']:.4f} (p={t['p']:.4g})")
            L.append("| " + " | ".join(row) + " |")
    L += [
        "",
        "## 5. Polarity strata (bead avt; X3 conditioning — post-hoc operationalisation: "
        "NOT-presence in the authored explication, 26/51 items)",
        "",
        "| model | stratum | n pairs | rho (p) | partial orig3 (p) | partial orig3+emb4 (p) |",
        "|---|---|---|---|---|---|",
    ]
    for m, pm in out["per_model"].items():
        for sname, st in pm["pair_strata"].items():
            L.append(f"| {m.split('/')[-1]} | {sname} | {st['n_pairs']} "
                     f"| {st['spearman']['rho']:.4f} (p={st['spearman']['p']:.4g}) "
                     f"| {st['partial_orig3']['rho']:.4f} (p={st['partial_orig3']['p']:.4g}) "
                     f"| {st['partial_orig3+emb4']['rho']:.4f} (p={st['partial_orig3+emb4']['p']:.4g}) |")
    L += ["", "| model | item subset | n items | rho (p) | partial orig3 (p) | partial orig3+emb4 (p) |",
          "|---|---|---|---|---|---|"]
    for m, pm in out["per_model"].items():
        for sname, st in pm["item_subsets"].items():
            L.append(f"| {m.split('/')[-1]} | {sname} | {st['n_items']} "
                     f"| {st['spearman']['rho']:.4f} (p={st['spearman']['p']:.4g}) "
                     f"| {st['partial_orig3']['rho']:.4f} (p={st['partial_orig3']['p']:.4g}) "
                     f"| {st['partial_orig3+emb4']['rho']:.4f} (p={st['partial_orig3+emb4']['p']:.4g}) |")
    d = out["decision"]
    L += [
        "",
        "## 6. Decision-rule outcomes (rules fixed in poc/e2/reanalysis/README.md before extraction)",
        "",
        f"- kernel beyond text-embedding baselines (partial p<0.01, orig3+emb4, >=2/3 families): "
        f"**{d['kernel_beyond_embeddings']}** — pass: {d['kernel_pass_families_orig3emb4'] or 'none'}",
        f"- embedded explication text beyond kernel (partial p<0.01, kernel+orig3, >=2/3 families, "
        f"any embedder): **{d['explication_embedding_beyond_kernel']}** — pass: {d['reverse_pass_families']}",
        "",
        "## 7. Verdict paragraph",
        "",
        "(one honest paragraph — written by the analyst after reading the numbers; "
        "see VERDICT-PARAGRAPH marker in the committed file)",
        "",
    ]
    with open(os.path.join(stamp_dir, "verdict-e2-reanalysis.md"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
