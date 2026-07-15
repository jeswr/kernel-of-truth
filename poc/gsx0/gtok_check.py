#!/usr/bin/env python3
"""gtok_check — the gsx0 G-TOK token-band gate (design section 4.1).

Re-runs the knull G-3 token-band check ON THE ACTUAL gsx0 surfaces at the
pinned SmolLM2-135M tokenizer: the mean prompt-surface token count of each
token-matched generic corpus (d-qa-t-plain = plain-padded store, d-qa-t-opaque
= opaque store) must lie within +/-10% of the kernel d-qa-t surface mean
(pre-freeze bar; the run-time FLOPs gate re-checks at +/-20% via the F0
ledger). FAIL-CLOSED: any pin mismatch or band violation exits 1 and writes
nothing.

Surface rendering for counting (identical rule for all three corpora, so the
ratio is invariant to the runner's fixed prompt-frame constants):
    question + "\n" + "<KEY>. <text>" per option (MCQ) — claims have no options.

Tokenizer: poc/gsx0/smollm2-135m-12fd25f7-tokenizer.json, byte-pinned below —
the tokenizer.json of HuggingFaceTB/SmolLM2-135M-Instruct at the model
revision frozen in f2b-transfer/knull-v2 (12fd25f7...). Requires the
`tokenizers` wheel (measured with 0.22.2); the corpora themselves build
stdlib-only.

Writes poc/gsx0/g3-token-band-gsx0.json (pinned in the gsx0 registry record
under pins.artifact_hashes) on PASS.

Usage:  python3 poc/gsx0/gtok_check.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOKENIZER_PATH = os.path.join(HERE, "smollm2-135m-12fd25f7-tokenizer.json")
TOKENIZER_SHA = "9ca9acddb6525a194ec8ac7a87f24fbba7232a9a15ffa1af0c1224fcd888e47c"
BAND = 0.10                      # pre-freeze band (run-time FLOPs gate: 0.20)
CORPORA = {"kernel": "d-qa-t", "plain": "d-qa-t-plain", "opaque": "d-qa-t-opaque"}
BAND_BINDING = ("plain", "opaque")
OUT = os.path.join(HERE, "g3-token-band-gsx0.json")


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def surface(item):
    parts = [item["question"]]
    for o in (item["options"] or []):
        parts.append("%s. %s" % (o["key"], o["text"]))
    return "\n".join(parts)


def main():
    got = file_sha256(TOKENIZER_PATH)
    if got != TOKENIZER_SHA:
        die("GSX0_ERR_TOKPIN", "tokenizer sha256 %s != pinned %s" % (got, TOKENIZER_SHA))
    try:
        from tokenizers import Tokenizer
        import tokenizers as _tk
    except ImportError:
        die("GSX0_ERR_TOKDEP", "the `tokenizers` wheel is required for G-TOK")
    tok = Tokenizer.from_file(TOKENIZER_PATH)

    stats = {}
    for arm, corpus in sorted(CORPORA.items()):
        path = os.path.join(ROOT, "data", corpus, "items", "covered.jsonl")
        counts = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    counts.append(len(tok.encode(surface(json.loads(line))).ids))
        if len(counts) != 360:
            die("GSX0_ERR_TOKSRC", "%s: expected 360 items, got %d" % (corpus, len(counts)))
        stats[arm] = {"corpus": corpus, "n_items": len(counts),
                      "mean_prompt_tokens": round(sum(counts) / len(counts), 2),
                      "max_prompt_tokens": max(counts)}

    kmean = stats["kernel"]["mean_prompt_tokens"]
    result = "PASS"
    for arm in BAND_BINDING:
        ratio = stats[arm]["mean_prompt_tokens"] / kmean
        stats[arm]["mean_prompt_token_ratio_vs_kernel"] = round(ratio, 4)
        stats[arm]["within_declared_band"] = abs(ratio - 1.0) <= BAND
        if not stats[arm]["within_declared_band"]:
            result = "FAIL"
    stats["kernel"]["mean_prompt_token_ratio_vs_kernel"] = 1.0

    report = {
        "artifact": "gsx0-g3-token-band",
        "gate": "G-TOK (design section 4.1): token-matched generic surfaces within "
                "+/-%d%% of the kernel d-qa-t surface mean at the pinned "
                "SmolLM2-135M tokenizer; fail-closed" % int(BAND * 100),
        "tokenizer": {"path": "poc/gsx0/smollm2-135m-12fd25f7-tokenizer.json",
                      "sha256": TOKENIZER_SHA,
                      "model_revision": "HuggingFaceTB/SmolLM2-135M-Instruct@"
                                        "12fd25f77366fa6b3b4b768ec3050bf629380bac",
                      "tokenizers_version": _tk.__version__},
        "surface_rule": "question + newline + '<KEY>. <text>' per option; identical "
                        "for all corpora (runner frame constants cancel in the ratio)",
        "arms": stats,
        "result": result,
    }
    if result != "PASS":
        sys.stderr.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
        die("GSX0_ERR_TOKBAND", "a token-matched arm is outside the +/-10%% band")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, sort_keys=True)
        f.write("\n")
    print("G-TOK PASS: kernel %.2f / plain %.2f (%.2fx) / opaque %.2f (%.2fx)"
          % (kmean, stats["plain"]["mean_prompt_tokens"],
             stats["plain"]["mean_prompt_token_ratio_vs_kernel"],
             stats["opaque"]["mean_prompt_tokens"],
             stats["opaque"]["mean_prompt_token_ratio_vs_kernel"]))


if __name__ == "__main__":
    main()
