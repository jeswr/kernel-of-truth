#!/usr/bin/env python3
"""A-E2 — cross-lingual phrase-coverage savings census (Tier-0, r0-local-cpu, $0).

Implements the K-A2 gate metric per docs/next/io-compression-signoff.md §3
(ASM-0461 input pins, ASM-0462 bracketing convention) and N-IOC §2.1/§2.7.

Objective:  value(c) = Σ_ℓ w_ℓ · f_ℓ(s) · (bpe_ℓ(s) − 1) · m̂(s,ℓ)
Deliverable: achievable prefill-token-savings FRACTION vs number of concepts
             minted, per-language + blended (lower & upper brackets), for two
             weight arms (uniform primary + usage-share sensitivity) and two
             host tokenizers (SmolLM2-135M mandatory R1 + Qwen2.5-0.5B R4-family).

Every number emitted is MEASURED-exploratory. NO verdict, NO freeze, NO
interpretation (Fable's lane). Fail-closed on input provenance.

Bracketing (ASM-0462), reported not adjudicated:
  - per-language unaligned curves  = LOWER bracket of aligned value
  - blended pooled-unaligned curve = a tighter LOWER bracket at fixed budget
  - blended cross-language SUM      = UPPER bracket
  K-A2 may fire only off the upper bracket; a go may rest only on the lower.

m̂ (ASM-0461: "sampled with the English-only a1-hybrid mapper on English
cells; membership-only (m̂=1) on non-English cells, K-A4 unpriced there"):
  - non-English: m̂=1 (DISCLOSED upper bound).
  - English: m̂ ∈ {0,1} from the isolated-surface a1-hybrid mapper decision
    (compute-mhat.mjs): m̂=0 iff the mapper abstains on the surface. This is a
    disclosed, mechanical instantiation and is itself an UPPER bound (only
    intrinsic-surface collisions are discounted; context-dependent polysemy
    invisible to the 119-entry lexicon is not). See RUN-LOG for the flagged
    sub-method choice.
"""
import os, sys, json, hashlib, subprocess, time, importlib.metadata as im
from tokenizers import Tokenizer
import wordfreq
from wordfreq import get_frequency_dict, available_languages

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
INPUTS = os.path.join(HERE, "inputs")
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)

LANGS = ["en", "es", "fi", "ja"]
LATIN = {"en", "es", "fi"}  # space-prefixed running-text tokenization
# ja tokenized bare (no inter-word spaces in Japanese script).

TOKENIZERS = {
    "smollm2-135m-instruct": {
        "file": os.path.join(INPUTS, "tokenizers", "smollm2-135m-instruct.tokenizer.json"),
        "hf_repo": "HuggingFaceTB/SmolLM2-135M-Instruct",
        "revision": "12fd25f77366fa6b3b4b768ec3050bf629380bac",
        "url": "https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct/resolve/12fd25f77366fa6b3b4b768ec3050bf629380bac/tokenizer.json",
        "role": "R1 mandatory host tokenizer",
        "sha256_expected": "9ca9acddb6525a194ec8ac7a87f24fbba7232a9a15ffa1af0c1224fcd888e47c",
    },
    "qwen2.5-0.5b-instruct": {
        "file": os.path.join(INPUTS, "tokenizers", "qwen2.5-0.5b-instruct.tokenizer.json"),
        "hf_repo": "Qwen/Qwen2.5-0.5B-Instruct",
        "revision": "7ae557604adf67be50417f59c2c2f167def9a775",
        "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/7ae557604adf67be50417f59c2c2f167def9a775/tokenizer.json",
        "role": "R4-family tokenizer (extension predicate); shared across Qwen2.5 family",
        "sha256_expected": "c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539",
    },
}

WORDFREQ_VER_EXPECTED = "3.1.1"
WF_SHA_EXPECTED = {
    "en": "dffae8066b78dce0a6667cf5f58e567054f902674667090a7ac8a8a44628b05c",
    "es": "14f326b4f68d517f9b8b99c1e26ef56a508d2dc8d0ee7a9e6e8732ddab1aa65e",
    "fi": "98fb498142d5cb4ff47df65d6c4784dff4fa2fc6d191a0b26cf6341101922151",
    "ja": "e6ab743b939c1802fc03791f1d58dee2861e822ceecdcdee3f0e05b863ef26d8",
}
KERNEL_MANIFEST = os.path.join(REPO, "data", "kernel-v0", "manifest.json")
A1_POLICY_SHA256 = "e13dc838ac7df709588604f7eb445082ac6776bbc83ae0415456318db504d696"

# Weight arms. Uniform is the PRIMARY (ASM-0461). usage-share is a SENSITIVITY
# arm; its numbers are STIPULATED-exploratory, illustrative web-content-language
# shares (order-of-magnitude, English-dominant), NOT a pinned measurement — the
# sign-off pins the arm's existence, not its values. FLAGGED for maintainer
# ratification at freeze (workload-mix discipline).
USAGE_SHARE_RAW = {"en": 0.520, "es": 0.055, "ja": 0.045, "fi": 0.005}  # ≈W3Techs-style web content share
_us_tot = sum(USAGE_SHARE_RAW[l] for l in LANGS)
WEIGHT_ARMS = {
    "uniform": {l: 0.25 for l in LANGS},
    "usage-share": {l: USAGE_SHARE_RAW[l] / _us_tot for l in LANGS},
}

# concept-budget grid (x-axis of the curve). K-A2 reference anchor = 10000.
N_GRID = [10, 30, 100, 300, 1000, 3000, 5000, 10000, 25000, 50000, 100000, 200000]

log = []
def L(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, file=sys.stderr)
    log.append(line)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# ------------------------------------------------------------------ fail-closed
L("A-E2 census start; fail-closed provenance check")
ver = im.version("wordfreq")
if ver != WORDFREQ_VER_EXPECTED:
    sys.exit(f"FAIL-CLOSED: wordfreq {ver} != pin {WORDFREQ_VER_EXPECTED}")
best = available_languages("best")
wf_files = {}
for lang in LANGS:
    p = best.get(lang)
    if not p or not os.path.exists(p):
        sys.exit(f"FAIL-CLOSED: wordfreq data for {lang} missing")
    got = sha256_file(p)
    if got != WF_SHA_EXPECTED[lang]:
        sys.exit(f"FAIL-CLOSED: wordfreq {lang} sha {got} != pin {WF_SHA_EXPECTED[lang]}")
    wf_files[lang] = {"path": p, "file": os.path.basename(p), "sha256": got}
    L(f"  wordfreq {lang}: {os.path.basename(p)} sha OK")
for name, t in TOKENIZERS.items():
    got = sha256_file(t["file"])
    if got != t["sha256_expected"]:
        sys.exit(f"FAIL-CLOSED: tokenizer {name} sha {got} != pin {t['sha256_expected']}")
    L(f"  tokenizer {name}: sha OK")
kernel_manifest_sha = sha256_file(KERNEL_MANIFEST)
L(f"  kernel-v0 manifest sha {kernel_manifest_sha[:16]}…")

# ------------------------------------------------------------- load frequencies
# f_ℓ(s) renormalised within-list so Σ_s f = 1 (relative frequency over the
# listed vocabulary). Raw Σ(wordfreq freq) recorded as the list's running-text
# coverage; unlisted tail (~1%) is excluded from BOTH numerator and denominator
# (DISCLOSED scoping).
freq = {}
list_coverage = {}
for lang in LANGS:
    d = get_frequency_dict(lang)
    raw_tot = sum(d.values())
    list_coverage[lang] = raw_tot
    freq[lang] = {s: v / raw_tot for s, v in d.items()}
    L(f"  freq {lang}: {len(d)} surfaces, raw Σfreq={raw_tot:.4f} (list running-text coverage)")

# --------------------------------------------------------------- tokenize (bpe)
tk = {name: Tokenizer.from_file(t["file"]) for name, t in TOKENIZERS.items()}
# bpe[lang][tokname] = dict surface -> primary bpe count (space-prefixed latin / bare ja)
# also keep bare & space variants for audit in per-concept detail.
bpe = {lang: {name: {} for name in TOKENIZERS} for lang in LANGS}
bpe_alt = {lang: {name: {} for name in TOKENIZERS} for lang in LANGS}  # the non-primary variant
for lang in LANGS:
    surfaces = list(freq[lang].keys())
    lead = " " if lang in LATIN else ""
    alt_lead = "" if lang in LATIN else " "
    for name, tok in tk.items():
        # primary
        enc = tok.encode_batch([lead + s for s in surfaces], add_special_tokens=False)
        for s, e in zip(surfaces, enc):
            bpe[lang][name][s] = len(e.ids)
        # alt variant (bare for latin / space for ja) for transparency
        enc2 = tok.encode_batch([alt_lead + s for s in surfaces], add_special_tokens=False)
        for s, e in zip(surfaces, enc2):
            bpe_alt[lang][name][s] = len(e.ids)
        L(f"  bpe {lang}/{name}: tokenized {len(surfaces)} surfaces (primary lead={lead!r})")

# ------------------------------------------------------------- English m̂ sample
L("English m̂: running isolated-surface a1-hybrid mapper (compute-mhat.mjs)")
en_surfaces_file = os.path.join(RESULTS, "en-surfaces.txt")
with open(en_surfaces_file, "w", encoding="utf-8") as f:
    f.write("\n".join(freq["en"].keys()) + "\n")
mhat_out = os.path.join(RESULTS, "en-mhat.jsonl")
node = subprocess.run(
    ["node", os.path.join(HERE, "compute-mhat.mjs"), en_surfaces_file, mhat_out],
    capture_output=True, text=True,
)
if node.returncode != 0:
    sys.exit(f"FAIL: compute-mhat.mjs rc={node.returncode}\n{node.stderr}")
L("  mhat: " + node.stderr.strip().splitlines()[-1])
en_mhat = {}          # surface -> m̂ (1 if not abstain else 0)
en_kind = {}          # surface -> raw decision kind (for re-derivation)
with open(mhat_out, encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        en_kind[r["s"]] = r["kind"]
        en_mhat[r["s"]] = 0.0 if r["kind"] == "abstain" else 1.0
mhat_kind_counts = {}
for k in en_kind.values():
    mhat_kind_counts[k] = mhat_kind_counts.get(k, 0) + 1

# --------------------------------------------------------------- curve machinery
def mhat_of(lang, s, mode):
    """mode: 'membership' -> 1 everywhere; 'mhat' -> en uses sampled m̂, others 1."""
    if mode == "mhat" and lang == "en":
        return en_mhat.get(s, 1.0)
    return 1.0

def is_wordlike(s):
    # DISCLOSED filter: keep surfaces with ≥1 alphabetic char (incl. accented,
    # kana, kanji — all isalpha() in Python) and NO digit; drops pure-numeric /
    # digit-bearing / punctuation-only tokens that are not sensible mint targets.
    return any(c.isalpha() for c in s) and not any(c.isdigit() for c in s)

def lang_stats(lang, name, mode, filt="all"):
    """Return (cells sorted by per-surface value desc, mean_bpe_per_word).
    cell = (value, f, bpe, surface). filt='wordlike' restricts the NUMERATOR
    (mint candidates) to word-like surfaces; the DENOMINATOR mean_bpe stays over
    ALL surfaces (we still pay for numeric tokens we choose not to mint)."""
    B = bpe[lang][name]
    F = freq[lang]
    mean_bpe = 0.0
    cells = []
    for s, f in F.items():
        b = B[s]
        mean_bpe += f * b
        if filt == "wordlike" and not is_wordlike(s):
            continue
        m = mhat_of(lang, s, mode)
        val = f * (b - 1) * m  # (b-1)=tokens saved/occurrence; 0 when b<=1
        if val > 0:
            cells.append((val, f, b, s))
    cells.sort(key=lambda c: -c[0])
    return cells, mean_bpe

def cum_curve(cells, grid):
    """cumulative Σ value over top-N, at each N in grid (+ 'all')."""
    out = {}
    csum = 0.0
    idx = 0
    gi = 0
    grid_sorted = sorted(set(grid))
    # we need cumulative at arbitrary N; precompute prefix then sample
    prefix = []
    run = 0.0
    for c in cells:
        run += c[0]
        prefix.append(run)
    total = prefix[-1] if prefix else 0.0
    for N in grid_sorted:
        if N <= len(prefix):
            out[str(N)] = prefix[N - 1] if N >= 1 else 0.0
        else:
            out[str(N)] = total  # budget exceeds candidate pool -> saturates
    out["all"] = total
    out["_pool_size"] = len(cells)
    return out

# ------------------------------------------------------------------- run curves
# FILTERS (DISCLOSED sensitivity): 'all' = every wordfreq surface (raw; includes
# numeric/degenerate tokens that float to the top of the value ranking, notably
# in English); 'wordlike' = mint candidates restricted to word-like surfaces.
FILTERS = ("all", "wordlike")
summary = {}
per_lang_cache = {}  # (lang,name,mode,filt) -> (cells, mean_bpe)
for name in TOKENIZERS:
    for mode in ("membership", "mhat"):
        for lang in LANGS:
            if mode == "mhat" and lang != "en":
                continue  # non-en identical to membership
            for filt in FILTERS:
                per_lang_cache[(lang, name, mode, filt)] = lang_stats(lang, name, mode, filt)

def get_lang(lang, name, mode, filt):
    key = (lang, name, mode if (mode == "mhat" and lang == "en") else "membership", filt)
    return per_lang_cache[key]

results = {"per_language": {}, "blended": {}}
for name in TOKENIZERS:
    results["per_language"][name] = {}
    for filt in FILTERS:
        for mode in ("membership", "mhat"):
            for lang in LANGS:
                if mode == "mhat" and lang != "en":
                    continue
                cells, mean_bpe = get_lang(lang, name, mode, filt)
                cum = cum_curve(cells, N_GRID)
                frac = {k: (v / mean_bpe if isinstance(v, float) and mean_bpe else v)
                        for k, v in cum.items() if not k.startswith("_")}
                results["per_language"][name][f"{lang}:{mode}:{filt}"] = {
                    "mean_bpe_per_word": mean_bpe,
                    "candidate_pool_size": cum["_pool_size"],
                    "n_surfaces": len(freq[lang]),
                    "surface_filter": filt,
                    "cum_tokens_saved_per_word": cum,
                    "frac_prefill_saved": frac,
                    "mhat_mode": mode,
                    "disclosed_upper_bound": (lang != "en") or (mode == "membership"),
                }

    # ---- blended: upper bracket (cross-language sum) & lower bracket (pooled) --
    results["blended"][name] = {}
    for filt in FILTERS:
        for wname, w in WEIGHT_ARMS.items():
            for mode in ("membership", "mhat"):
                # denominator: Σ_ℓ w_ℓ · mean_bpe_ℓ (mode- & filt-invariant: mean_bpe is over ALL surfaces)
                denom = 0.0
                for lang in LANGS:
                    _, mean_bpe = get_lang(lang, name, "membership", filt)
                    denom += w[lang] * mean_bpe

                # UPPER bracket: Σ_ℓ w_ℓ · cum_saved_ℓ(N)  (each concept covers all langs)
                per_lang_cum = {}
                for lang in LANGS:
                    cells, _ = get_lang(lang, name, mode, filt)
                    per_lang_cum[lang] = cum_curve(cells, N_GRID)
                upper_frac = {}
                for N in [str(n) for n in sorted(set(N_GRID))] + ["all"]:
                    num = sum(w[lang] * per_lang_cum[lang][N] for lang in LANGS)
                    upper_frac[N] = num / denom if denom else 0.0

                # LOWER bracket: pooled unaligned — rank ALL (s,ℓ) cells by weighted
                # contribution w_ℓ·f·(bpe-1)·m̂; each concept = one language surface.
                pooled = []
                for lang in LANGS:
                    cells, _ = get_lang(lang, name, mode, filt)
                    wl = w[lang]
                    for (val, f, b, s) in cells:
                        pooled.append(val * wl)  # weighted savings contribution
                pooled.sort(reverse=True)
                prefix = []
                run = 0.0
                for v in pooled:
                    run += v
                    prefix.append(run)
                total = prefix[-1] if prefix else 0.0
                lower_frac = {}
                for N in sorted(set(N_GRID)):
                    lower_frac[str(N)] = (prefix[N - 1] if N <= len(prefix) else total) / denom if denom else 0.0
                lower_frac["all"] = total / denom if denom else 0.0

                results["blended"][name][f"{wname}:{mode}:{filt}"] = {
                    "weights": w,
                    "surface_filter": filt,
                    "weighted_mean_bpe_denominator": denom,
                    "upper_bracket_frac_prefill_saved": upper_frac,
                    "lower_bracket_frac_prefill_saved": lower_frac,
                    "upper_bracket_desc": "cross-language sum; aligned upper bound (ASM-0462); K-A2 may fire only off this",
                    "lower_bracket_desc": "pooled unaligned; a go may rest only on this (ASM-0462)",
                    "pooled_pool_size": len(pooled),
                }
            L(f"  blended {name}/{wname}/{filt}: computed upper+lower brackets (membership+mhat)")

# ------------------------------------------------------------------ headline @10k
def headline(name, wname, mode, filt):
    b = results["blended"][name][f"{wname}:{mode}:{filt}"]
    return {
        "lower_bracket_@10k_pct": round(100 * b["lower_bracket_frac_prefill_saved"]["10000"], 4),
        "upper_bracket_@10k_pct": round(100 * b["upper_bracket_frac_prefill_saved"]["10000"], 4),
    }
headline_table = {}
for name in TOKENIZERS:
    for filt in FILTERS:
        for wname in WEIGHT_ARMS:
            for mode in ("membership", "mhat"):
                headline_table[f"{name} | {wname} | {mode} | {filt}"] = headline(name, wname, mode, filt)

# per-language @10k membership, both filters (primary tokenizer)
per_lang_headline = {}
for name in TOKENIZERS:
    for filt in FILTERS:
        for lang in LANGS:
            cell = results["per_language"][name].get(f"{lang}:membership:{filt}")
            if cell:
                per_lang_headline[f"{name} | {lang} | membership | {filt}"] = {
                    "mean_bpe_per_word": round(cell["mean_bpe_per_word"], 4),
                    "frac_prefill_saved_@10k_pct": round(100 * cell["frac_prefill_saved"]["10000"], 4),
                    "frac_prefill_saved_all_pct": round(100 * cell["frac_prefill_saved"]["all"], 4),
                    "disclosed_upper_bound": cell["disclosed_upper_bound"],
                }
        en_mh = results["per_language"][name].get(f"en:mhat:{filt}")
        if en_mh:
            per_lang_headline[f"{name} | en | mhat | {filt}"] = {
                "mean_bpe_per_word": round(en_mh["mean_bpe_per_word"], 4),
                "frac_prefill_saved_@10k_pct": round(100 * en_mh["frac_prefill_saved"]["10000"], 4),
                "frac_prefill_saved_all_pct": round(100 * en_mh["frac_prefill_saved"]["all"], 4),
            }

# ------------------------------------------------------------------- manifest
manifest = {
    "schema": "kot-ae2-manifest/1",
    "census": "A-E2 cross-lingual phrase-coverage savings census",
    "bead": "kernel-of-truth-5iu",
    "date": time.strftime("%Y-%m-%d"),
    "epistemic_tag": "MEASURED-exploratory",
    "spec": [
        "docs/next/io-compression-signoff.md §3 (N-IOC-S)",
        "docs/next/io-compression-ideas.md §2.1, §2.7 (N-IOC)",
        "ASM-0461 (input pins)", "ASM-0462 (bracketing convention)",
    ],
    "languages": LANGS,
    "frequency_lists": {
        lang: {
            "source": "wordfreq (rspeer/wordfreq lineage)",
            "package_version": WORDFREQ_VER_EXPECTED,
            "wordlist": "large (best)",
            "data_file": wf_files[lang]["file"],
            "sha256": wf_files[lang]["sha256"],
            "upstream": "https://github.com/rspeer/wordfreq (data), https://pypi.org/project/wordfreq/3.1.1/",
            "n_surfaces": len(freq[lang]),
            "list_running_text_coverage_raw_sum_freq": list_coverage[lang],
            "renormalised_within_list": True,
        } for lang in LANGS
    },
    "tokenizers": {
        name: {k: t[k] for k in ("hf_repo", "revision", "url", "role")}
              | {"sha256": t["sha256_expected"], "file": os.path.relpath(t["file"], REPO)}
        for name, t in TOKENIZERS.items()
    },
    "mapper_mhat": {
        "operationalisation": "isolated-surface a1-hybrid mapper decision; m̂=0 iff abstain else 1",
        "mapper_pkg": "kernel-mapper@0.1.0 (mapper/ package)",
        "policy_preset": "a1-hybrid",
        "policy_sha256": A1_POLICY_SHA256,
        "kernel_manifest": "data/kernel-v0/manifest.json",
        "kernel_manifest_sha256": kernel_manifest_sha,
        "en_decision_kind_counts": mhat_kind_counts,
        "DISCLOSED": "English m̂ is itself an UPPER bound (only intrinsic-surface collisions discounted); non-English m̂=1 upper bound, K-A4 unpriced there. Sub-method FLAGGED for Fable ratification (see RUN-LOG).",
    },
    "weight_arms": {
        "uniform": {"weights": WEIGHT_ARMS["uniform"], "tag": "PRIMARY (ASM-0461)"},
        "usage-share": {
            "weights": WEIGHT_ARMS["usage-share"],
            "raw_input": USAGE_SHARE_RAW,
            "tag": "STIPULATED-exploratory sensitivity arm; illustrative web-content share, English-dominant; NOT a pinned measurement; FLAGGED for maintainer ratification",
        },
    },
    "surface_filter_note": "DISCLOSED sensitivity dimension. filt='all' = every wordfreq surface (raw; numeric/digit-bearing tokens like '0000','00,000' float to the top of the English value ranking and inflate savings). filt='wordlike' restricts mint candidates to surfaces with ≥1 alphabetic char and NO digit (denominator stays over ALL surfaces). Neither is adjudicated as canonical — reported so Fable can judge the numeric artifact.",
    "tokenization_convention": "primary bpe = space-prefixed for {en,es,fi} (running-text realism), bare for ja (no inter-word spaces); alt variant recorded per-surface for audit; add_special_tokens=False",
    "denominator_convention": "frac_prefill_saved = cum_tokens_saved_per_word / mean_bpe_per_word (weighted avg BPE tokens per LISTED word); unlisted tail (~1%) excluded from num & denom",
}

summary = {
    "schema": "kot-ae2-summary/1",
    "census": "A-E2 cross-lingual phrase-coverage savings census",
    "epistemic_tag": "MEASURED-exploratory",
    "note": "NO verdict / NO freeze / NO interpretation (Fable's lane). Census informs but does not gate the feasibility verdict.",
    "bracketing_convention": "ASM-0462: per-language + pooled = LOWER bracket; cross-language sum = UPPER bracket; K-A2 fires only off upper, go rests only on lower.",
    "concept_budget_grid": N_GRID,
    "k_a2_reference_anchor_concepts": 10000,
    "manifest": manifest,
    "headline_blended_@10k": headline_table,
    "headline_per_language_@10k": per_lang_headline,
    "results": results,
}

with open(os.path.join(RESULTS, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
L("wrote results/summary.json")

# ---------------------------------------------------- per-concept detail (top-K)
DETAIL_K = 1000
with open(os.path.join(RESULTS, "per-concept-detail.jsonl"), "w", encoding="utf-8") as f:
    for name in TOKENIZERS:
        for lang in LANGS:
            cells, mean_bpe = get_lang(lang, name, "membership", "all")
            run = 0.0
            for rank, (val, fr, b, s) in enumerate(cells[:DETAIL_K], 1):
                run += val
                rec = {
                    "tokenizer": name, "lang": lang, "rank": rank, "surface": s,
                    "rel_freq": fr, "bpe_primary": b,
                    "bpe_alt": bpe_alt[lang][name][s],
                    "tokens_saved_per_occ": b - 1,
                    "value_membership": val,
                    "cum_frac_prefill_saved": run / mean_bpe if mean_bpe else 0.0,
                    "wordlike": is_wordlike(s),
                }
                if lang == "en":
                    rec["en_decision_kind"] = en_kind.get(s)
                    rec["en_mhat"] = en_mhat.get(s)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
L(f"wrote results/per-concept-detail.jsonl (top {DETAIL_K} per lang×tokenizer, membership rank)")

with open(os.path.join(RESULTS, "RUN-LOG.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log) + "\n")
L("done")
