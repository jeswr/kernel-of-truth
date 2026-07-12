#!/usr/bin/env python3
"""knull Option-B -- pre-freeze token-delta measurement + plain-padded
feasibility check (design note docs/next/design/knull-optionb-analysis.md,
PROPOSED-ASM-1082/ASM-1088).

Three questions, three epistemic grades, one artifact
(poc/knull/inputs-v3/token-projection.json):

  1. MEASURED   gloss-level token counts under the pinned SmolLM2-135M
                tokenizer for the kernel store, the v2 plain store, and the
                v3 (Option-B concise) plain store -- exact, on committed
                bytes.
  2. PROJECTED  prompt-level mean token count for a v3 plain arm, obtained
                by substituting the v3 glosses (and, for claim items, the
                index-mapped v3 segments) into the BYTE-IDENTICAL v2 item
                schedule and re-rendering with the pinned f2b build_prompt.
                A projection, never a premise: the binding number is the
                G-3 artifact of the actual v3 build.
  3. MEASURED   feasibility of the plain-padded generator rule (own-segment
                cyclic repetition into the kernel word band) on all 108
                committed v3 definitions, plus the projected padded-arm
                token ratios.

Usage:
  python3 poc/knull/project_tokens_optionb.py --tokenizer-json <path>
"""

import argparse
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POC = os.path.dirname(HERE)
F2B_RUNNER_DIR = os.path.join(POC, "f2b", "runner")
for p in (HERE, POC, F2B_RUNNER_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from f2b_runner import build_prompt          # noqa: E402 (pinned sha; G-3 pattern)
import build_inputs                          # noqa: E402 (pinned v1 builder, lib use)
import lint_plain_store as lps               # noqa: E402 (pinned; segments())

TOKENIZER_SHA256 = "9ca9acddb6525a194ec8ac7a87f24fbba7232a9a15ffa1af0c1224fcd888e47c"
WORDBAND_FRAC = 0.25


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
    """The plain-padded generator rule (PROPOSED-ASM-1082): append the
    definition's own admissible segments, cyclically and whole, until the
    word count enters the kernel-gloss word band; never cut inside a
    segment. Returns (padded, status)."""
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
            # final step: scan for any own segment that lands in the band
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
    v2 = json.load(open(os.path.join(HERE, "inputs-v2", "plain-authored.json"),
                        encoding="utf-8"))["definitions"]
    v3_path = os.path.join(HERE, "inputs-v3", "plain-authored.json")
    v3 = json.load(open(v3_path, encoding="utf-8"))["definitions"]

    # ---- 1. MEASURED gloss-level tokens
    def stats(d):
        t = [ntok(d[lab]) for lab in sorted(d)]
        return {"mean_tokens": round(sum(t) / len(t), 2),
                "min_tokens": min(t), "max_tokens": max(t)}

    gloss = {"kernel": stats(kern), "plain_v2": stats(v2), "plain_v3": stats(v3)}
    for a in ("plain_v2", "plain_v3"):
        gloss[a]["ratio_vs_kernel"] = round(
            gloss[a]["mean_tokens"] / gloss["kernel"]["mean_tokens"], 4)

    # ---- 3. MEASURED padded feasibility (+ gloss tokens of padded arm)
    seg_v2 = {lab: lps.segments(v2[lab]) for lab in v2}
    seg_v3 = {lab: lps.segments(v3[lab]) for lab in v3}
    padded, pad_rows, statuses = {}, [], {}
    for lab in sorted(v3):
        g, status = pad_gloss(v3[lab], kern[lab])
        statuses[status] = statuses.get(status, 0) + 1
        if g is None:
            pad_rows.append({"label": lab, "status": status})
            continue
        padded[lab] = g
        pad_rows.append({"label": lab, "status": status,
                         "words": wc(g), "kernel_words": wc(kern[lab]),
                         "tokens": ntok(g)})
    feasible = len(padded) == len(v3)
    gloss["plain_padded_projected"] = (stats(padded) if feasible else None)
    if feasible:
        gloss["plain_padded_projected"]["ratio_vs_kernel"] = round(
            gloss["plain_padded_projected"]["mean_tokens"]
            / gloss["kernel"]["mean_tokens"], 4)

    # ---- 2. PROJECTED prompt-level tokens on the v2 item schedule
    frames = json.load(open(os.path.join(POC, "f2b", "inputs",
                                         "f2b-manifest.json"),
                            encoding="utf-8"))["prompt_frames"]
    items = [json.loads(l) for l in
             open(os.path.join(HERE, "inputs-v2", "items", "plain.jsonl"),
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
                o["text"] = defs_sub(o["text"], defs)
        if new_claim:
            it["claim"] = new_claim
        return it

    def defs_sub(s, defs):
        for lab, old in v2.items():
            if old in s:
                s = s.replace(old, defs[lab])
        return s

    def mean_prompt(defs, segmap):
        toks = [ntok(build_prompt(frames, substitute(it, defs, segmap)))
                for it in items]
        return round(sum(toks) / len(toks), 2)

    v2_g3 = json.load(open(os.path.join(HERE, "inputs-v2",
                                        "g3-token-band.json"),
                           encoding="utf-8"))
    kernel_mean = v2_g3["arms"]["kernel"]["mean_prompt_tokens"]
    prompt = {
        "_method": ("substitution of v3 glosses (and index-mapped v3 claim "
                    "segments) into the byte-identical v2 plain item "
                    "schedule, re-rendered with the pinned f2b build_prompt; "
                    "kernel/opaque arms unchanged from the v2 G-3 artifact"),
        "_epistemic": ("PROJECTED pre-freeze evidence only; the binding "
                       "number is the G-3 artifact of the actual v3 build"),
        "kernel_measured_v2": kernel_mean,
        "plain_v2_measured": v2_g3["arms"]["plain"]["mean_prompt_tokens"],
        "opaque_measured_v2": v2_g3["arms"]["opaque"]["mean_prompt_tokens"],
        "plain_v3_projected": mean_prompt(v3, seg_v3),
    }
    prompt["plain_v3_projected_ratio_vs_kernel"] = round(
        prompt["plain_v3_projected"] / kernel_mean, 4)
    if feasible:
        prompt["plain_padded_projected"] = mean_prompt(padded, seg_v3)
        prompt["plain_padded_projected_ratio_vs_kernel"] = round(
            prompt["plain_padded_projected"] / kernel_mean, 4)

    out = {
        "schema": "kot-knull-optionb-tokenproj/1",
        "store_v3": {"path": "poc/knull/inputs-v3/plain-authored.json",
                     "sha256": file_sha256(v3_path)},
        "tokenizer_json_sha256": TOKENIZER_SHA256,
        "gloss_level_measured": gloss,
        "prompt_level": prompt,
        "padded_feasibility": {
            "rule": ("own-segment cyclic whole-segment repetition into the "
                     "kernel word band [0.75*wc, max(1.25*wc, wc+8)]; "
                     "fail-closed"),
            "n_feasible": len(padded), "n_total": len(v3),
            "status_counts": statuses,
            "all_feasible": feasible,
            "failures": [r for r in pad_rows if "words" not in r],
        },
    }
    opath = os.path.join(HERE, "inputs-v3", "token-projection.json")
    with open(opath, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"gloss_level_measured": gloss, "prompt_level": prompt,
                      "padded_feasibility": out["padded_feasibility"]},
                     indent=1, sort_keys=True))
    print("artifact -> %s" % opath)


if __name__ == "__main__":
    main()
