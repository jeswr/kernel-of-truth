#!/usr/bin/env python3
"""knull freeze-prep G-2 — FLOP-accounting re-check on the ACCEPTED v4 plain
store (maintainer issue-17 acceptance + blind style sign-off 10/10,
poc/knull/inputs-v3/plain-spotcheck-current-RESULT.md).

WHY THIS EXISTS: the standing pre-freeze token evidence
(poc/knull/inputs-v3/token-projection.json, ASM-1088) measures the v3 store;
the accepted store is v4 (poc/knull/inputs-v4/plain-authored.json v4.0.0,
sha256 97609abe...). Gate G-2 of kernel-of-truth-d0hq requires the
matched-FLOP accounting re-verified against the store that will actually be
frozen. This script recomputes, on the committed v4 bytes:

  1. MEASURED   gloss-level token counts (pinned SmolLM2-135M tokenizer) for
                kernel / plain-v2 / plain-v3 / plain-v4.
  2. MEASURED   feasibility of the plain-padded generator rule (ASM-1082:
                own-segment cyclic whole-segment repetition into the kernel
                word band [0.75*wc, max(1.25*wc, wc+8)], fail-closed) on all
                108 v4 definitions, + the padded arm's gloss tokens.
  3. PROJECTED  prompt-level mean tokens for a v4 plain arm and a v4
                plain-padded arm, by substituting the v4 glosses (and
                index-mapped v4 claim segments) into the byte-identical v2
                item schedule, re-rendered with the pinned f2b build_prompt
                — the identical methodology of the pinned
                poc/knull/project_tokens_optionb.py (sha
                21b217e1476e435c21bd08b350f9e92de66c4e9058fa2fb672ad0a15a4f7f62e
                on disk at recheck time); binding resolution stays the G-3
                artifact of the actual v4 build + the run-time F0 FLOPs
                ledger (ASM-1088).
  4. VERDICT    the matched-FLOP bands under the registered Option-B scope
                (ASM-1085): pre-freeze +/-10% binds plain-padded and opaque
                vs kernel; run-time gate +/-20%; the concise plain arm is
                EXEMPT BY DESIGN, its ratio measured and disclosed
                DESCRIPTIVE.

FLOP model (per the record's own accounting): in every knull cell the
verifier is the CPU string-matcher (metered at the pinned rate); LM FLOPs
per query scale with prompt tokens x attempts on the same pinned 135M host
with the same retry budget k=4 in every verify arm, so prompt-token ratio is
the pre-freeze FLOPs-parity proxy (knull-v2.json gate-flops-parity;
docs/next/design/knull-optionb-analysis.md section 2).

Usage:
  python3 poc/knull/freeze-prep/flops_recheck_v4.py --tokenizer-json <path>

$0, CPU-only, writes poc/knull/freeze-prep/flops-recheck-v4.json only.
"""

import argparse
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KNULL = os.path.dirname(HERE)
POC = os.path.dirname(KNULL)
F2B_RUNNER_DIR = os.path.join(POC, "f2b", "runner")
for p in (KNULL, POC, F2B_RUNNER_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from f2b_runner import build_prompt          # noqa: E402 (pinned sha; G-3 pattern)
import build_inputs                          # noqa: E402 (pinned v1 builder, lib use)
import lint_plain_store as lps               # noqa: E402 (pinned; segments())

TOKENIZER_SHA256 = "9ca9acddb6525a194ec8ac7a87f24fbba7232a9a15ffa1af0c1224fcd888e47c"
V4_SHA256 = "97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2"
WORDBAND_FRAC = 0.25
PREFREEZE_BAND = 0.10   # G-3 pre-freeze band (record gate-flops-parity note)
RUNTIME_BAND = 0.20     # run-time instrument gate


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def wc(text):
    return len(text.split())


def pad_gloss(base, kernel_gloss):
    """ASM-1082 generator rule, byte-identical logic to the pinned
    project_tokens_optionb.py pad_gloss."""
    segs = lps.segments(base)
    if not segs:
        return None, "NO_SEGMENTS"
    k = wc(kernel_gloss)
    lo, hi = k * (1 - WORDBAND_FRAC), max(k * (1 + WORDBAND_FRAC), k + 8)
    g = base
    if wc(g) > hi:
        return None, "OVER_BAND_UNPADDED"
    i = 0
    while wc(g) < lo:
        nxt = segs[i % len(segs)]
        if wc(g) + wc(nxt) > hi:
            landing = [s for s in segs if lo <= wc(g) + wc(s) <= hi]
            if not landing:
                return None, "GAP_NO_LANDING_SEGMENT"
            nxt = landing[0]
            g = g + "; " + nxt
            break
        g = g + "; " + nxt
        i += 1
    if not (lo <= wc(g) <= hi):
        return None, "OUT_OF_BAND_AFTER_PAD"
    if lps.segments(g) != segs:
        return None, "SEGMENT_SET_CHANGED"
    return g, ("DEGENERATE_NO_PAD" if g == base else "PADDED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer-json", required=True)
    args = ap.parse_args()
    if file_sha256(args.tokenizer_json) != TOKENIZER_SHA256:
        die("KNULL_ERR_TOKENIZER_PIN", "tokenizer.json sha256 mismatch")
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(args.tokenizer_json)

    def ntok(s):
        return len(tok.encode(s).ids)

    concepts = build_inputs.load_covered()
    kern = {c["label"]: c["gloss"] for c in concepts}
    v2 = json.load(open(os.path.join(KNULL, "inputs-v2", "plain-authored.json"),
                        encoding="utf-8"))["definitions"]
    v3 = json.load(open(os.path.join(KNULL, "inputs-v3", "plain-authored.json"),
                        encoding="utf-8"))["definitions"]
    v4_path = os.path.join(KNULL, "inputs-v4", "plain-authored.json")
    if file_sha256(v4_path) != V4_SHA256:
        die("KNULL_ERR_STORE_PIN", "v4 store sha256 mismatch vs accepted pin")
    v4 = json.load(open(v4_path, encoding="utf-8"))["definitions"]
    if sorted(v4) != sorted(kern):
        die("KNULL_ERR_COVERAGE", "v4 store labels != covered concept labels")

    # ---- 1. MEASURED gloss-level tokens
    def stats(d):
        t = [ntok(d[lab]) for lab in sorted(d)]
        return {"mean_tokens": round(sum(t) / len(t), 2),
                "min_tokens": min(t), "max_tokens": max(t)}

    gloss = {"kernel": stats(kern), "plain_v2": stats(v2),
             "plain_v3": stats(v3), "plain_v4": stats(v4)}
    for a in ("plain_v2", "plain_v3", "plain_v4"):
        gloss[a]["ratio_vs_kernel"] = round(
            gloss[a]["mean_tokens"] / gloss["kernel"]["mean_tokens"], 4)

    # ---- 2. MEASURED padded feasibility on v4 (ASM-1082)
    seg_v2 = {lab: lps.segments(v2[lab]) for lab in v2}
    seg_v4 = {lab: lps.segments(v4[lab]) for lab in v4}
    single_segment = sum(1 for lab in seg_v4 if len(seg_v4[lab]) == 1)
    padded, pad_rows, statuses = {}, [], {}
    for lab in sorted(v4):
        g, status = pad_gloss(v4[lab], kern[lab])
        statuses[status] = statuses.get(status, 0) + 1
        if g is None:
            pad_rows.append({"label": lab, "status": status})
            continue
        padded[lab] = g
        pad_rows.append({"label": lab, "status": status,
                         "words": wc(g), "kernel_words": wc(kern[lab]),
                         "tokens": ntok(g)})
    feasible = len(padded) == len(v4)
    gloss["plain_padded_v4_projected"] = (stats(padded) if feasible else None)
    if feasible:
        gloss["plain_padded_v4_projected"]["ratio_vs_kernel"] = round(
            gloss["plain_padded_v4_projected"]["mean_tokens"]
            / gloss["kernel"]["mean_tokens"], 4)

    # ---- 3. PROJECTED prompt-level tokens on the v2 item schedule
    frames = json.load(open(os.path.join(POC, "f2b", "inputs",
                                         "f2b-manifest.json"),
                            encoding="utf-8"))["prompt_frames"]
    items = [json.loads(l) for l in
             open(os.path.join(KNULL, "inputs-v2", "items", "plain.jsonl"),
                  encoding="utf-8") if l.strip()]

    def substitute(item, defs, segmap):
        it = copy.deepcopy(item)
        claim = it.get("claim")
        new_claim = None
        if claim:
            src = it.get("claim_source", it["label"])
            if claim in seg_v2.get(src, ()):
                idx = seg_v2[src].index(claim)
                new_claim = segmap[src][idx % len(segmap[src])]
        for field in ("question",):
            s = it[field]
            if new_claim:
                s = s.replace(claim, new_claim)
            for lab, old in v2.items():
                if old in s:
                    s = s.replace(old, defs[lab])
            it[field] = s
        if it.get("options"):
            for o in it["options"]:
                for lab, old in v2.items():
                    if old in o["text"]:
                        o["text"] = o["text"].replace(old, defs[lab])
        if new_claim:
            it["claim"] = new_claim
        return it

    def mean_prompt(defs, segmap):
        toks = [ntok(build_prompt(frames, substitute(it, defs, segmap)))
                for it in items]
        return round(sum(toks) / len(toks), 2)

    v2_g3 = json.load(open(os.path.join(KNULL, "inputs-v2",
                                        "g3-token-band.json"),
                           encoding="utf-8"))
    kernel_mean = v2_g3["arms"]["kernel"]["mean_prompt_tokens"]
    opaque_mean = v2_g3["arms"]["opaque"]["mean_prompt_tokens"]
    prompt = {
        "_method": ("substitution of v4 glosses (and index-mapped v4 claim "
                    "segments) into the byte-identical v2 plain item "
                    "schedule, re-rendered with the pinned f2b build_prompt; "
                    "kernel/opaque arms carried from the MEASURED v2 G-3 "
                    "artifact (their logic is byte-identical across "
                    "versions)"),
        "_epistemic": ("PROJECTED pre-freeze evidence only; binding "
                       "resolution = the G-3 artifact of the actual v4 "
                       "four-arm build + the run-time F0 FLOPs ledger "
                       "(ASM-1088)"),
        "kernel_measured_v2": kernel_mean,
        "opaque_measured_v2": opaque_mean,
        "opaque_ratio_vs_kernel_measured": round(opaque_mean / kernel_mean, 4),
        "plain_v4_projected": mean_prompt(v4, seg_v4),
    }
    prompt["plain_v4_projected_ratio_vs_kernel"] = round(
        prompt["plain_v4_projected"] / kernel_mean, 4)
    if feasible:
        prompt["plain_padded_v4_projected"] = mean_prompt(padded, seg_v4)
        prompt["plain_padded_v4_projected_ratio_vs_kernel"] = round(
            prompt["plain_padded_v4_projected"] / kernel_mean, 4)

    # ---- 4. Band verdicts under the ASM-1085 scope
    def band(ratio, frac):
        return ratio is not None and abs(ratio - 1.0) <= frac

    pp = prompt.get("plain_padded_v4_projected_ratio_vs_kernel")
    op = prompt["opaque_ratio_vs_kernel_measured"]
    pl = prompt["plain_v4_projected_ratio_vs_kernel"]
    verdict = {
        "scope": ("ASM-1085: parity binds the TOKEN-MATCHED arms "
                  "(plain-padded, opaque) vs kernel; the concise plain arm "
                  "is exempt by design, DESCRIPTIVE only"),
        "plain_padded_projected_in_prefreeze_band_10pct": band(pp, PREFREEZE_BAND),
        "plain_padded_projected_in_runtime_band_20pct": band(pp, RUNTIME_BAND),
        "opaque_measured_in_prefreeze_band_10pct": band(op, PREFREEZE_BAND),
        "opaque_measured_in_runtime_band_20pct": band(op, RUNTIME_BAND),
        "plain_v4_descriptive_ratio": pl,
        "plain_v4_outside_20pct_band_as_designed": not band(pl, RUNTIME_BAND),
        "padded_feasible_108_of_108": feasible,
        "retry_topology_note": ("matched by construction, not recomputed "
                                "here: every verify arm runs the identical "
                                "imported f2b verify-retry machinery at "
                                "k=4 on the same pinned 135M host; the "
                                "verifier is the CPU string-matcher metered "
                                "at the pinned rate (knull_runner.py "
                                "imports poc/f2b/runner/f2b_runner.py "
                                "read-only at the pinned sha)"),
    }

    out = {
        "schema": "kot-knull-freezeprep-flopsrecheck/1",
        "gate": "d0hq G-2 (FLOPs re-check on the accepted v4 store)",
        "store_v4": {"path": "poc/knull/inputs-v4/plain-authored.json",
                     "sha256": V4_SHA256},
        "tokenizer_json_sha256": TOKENIZER_SHA256,
        "gloss_level_measured": gloss,
        "prompt_level": prompt,
        "padded_feasibility_v4": {
            "rule": ("ASM-1082 own-segment cyclic whole-segment repetition "
                     "into the kernel word band [0.75*wc, max(1.25*wc, "
                     "wc+8)]; fail-closed"),
            "n_feasible": len(padded), "n_total": len(v4),
            "n_single_segment_definitions": single_segment,
            "status_counts": statuses,
            "all_feasible": feasible,
            "failures": [r for r in pad_rows if "words" not in r],
        },
        "band_verdicts": verdict,
    }
    opath = os.path.join(HERE, "flops-recheck-v4.json")
    with open(opath, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"gloss_level_measured": gloss, "prompt_level": prompt,
                      "padded_feasibility_v4": out["padded_feasibility_v4"],
                      "band_verdicts": verdict}, indent=1, sort_keys=True))
    print("artifact -> %s" % opath)


if __name__ == "__main__":
    main()
