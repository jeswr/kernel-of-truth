#!/usr/bin/env python3
"""knull-v2 — G-3 tokenizer-level FLOPs-band re-check over the V2 inputs.

V2 DELTA (the ONLY changes from the pinned v1 checker poc/knull/
check_token_band.py): every input/output path reads poc/knull/inputs-v2/
instead of poc/knull/inputs/. Tokenizer pin, prompt rendering, PASS
criteria and artifact schema are byte-carried. Original docstring follows.

knull — G-3 tokenizer-level FLOPs-band re-check
(docs/design-knull-content-injection-ablation.md section 6.2 gate G-3).

The build-time word band is a PROXY for the quantity the FLOPs-parity
instrument gate actually meters (per-query mean FLOPs, dominated by prompt
tokens: F0 section 3.3, FLOPs ~ 2*N_active*T_total). This check re-computes
the band at TOKEN level with the pinned SmolLM2-135M-Instruct tokenizer over
the BUILT item files (the exact f2b build_prompt rendering, verbatim frames),
and writes the committed artifact inputs/g3-token-band.json.

PASS criteria (pre-declared here, stricter than the run-time gate):
  - per-arm mean prompt tokens within +/-10% of the kernel arm (the run-time
    instrument gate allows +/-20%; passing at half the width leaves headroom
    for decode-side and per-item variation);
  - n stays 1000 per arm => fork F-KN-C margin call: TOST margin 0.05 stands.

The tokenizer file is NOT committed (3.5 MB, third-party); this check pins it
by (repo, revision, sha256) and refuses any other bytes. Re-fetch:
  curl -sL -o tokenizer.json https://huggingface.co/<TOKENIZER_REPO>/resolve/<TOKENIZER_REVISION>/tokenizer.json

Usage:
  python3 poc/knull/check_token_band.py --tokenizer-json <path>
"""

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POC = os.path.dirname(HERE)
ROOT = os.path.dirname(POC)
F2B_RUNNER_DIR = os.path.join(POC, "f2b", "runner")
for p in (POC, F2B_RUNNER_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from f2b_runner import build_prompt  # noqa: E402  (pinned; sha checked below)

# The f2b-pinned verifier-host tokenizer (registry/experiments/
# f2b-replicate.json pins.model_revisions, R1).
TOKENIZER_REPO = "HuggingFaceTB/SmolLM2-135M-Instruct"
TOKENIZER_REVISION = "12fd25f77366fa6b3b4b768ec3050bf629380bac"
TOKENIZER_SHA256 = "9ca9acddb6525a194ec8ac7a87f24fbba7232a9a15ffa1af0c1224fcd888e47c"

ARMS = ("kernel", "plain", "opaque")
MEAN_BAND = 0.10          # pre-declared pre-freeze bound (run-time gate: 0.20)


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def file_sha256(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer-json", required=True)
    args = ap.parse_args()

    got = file_sha256(args.tokenizer_json)
    if got != TOKENIZER_SHA256:
        die("KNULL_ERR_G3_TOKENIZER_PIN",
            "tokenizer.json sha256 %s != pinned %s (%s@%s)"
            % (got[:12], TOKENIZER_SHA256[:12], TOKENIZER_REPO,
               TOKENIZER_REVISION))
    try:
        from tokenizers import Tokenizer
    except ImportError:
        die("KNULL_ERR_G3_DEPS", "pip install tokenizers")
    tok = Tokenizer.from_file(args.tokenizer_json)

    man_path = os.path.join(HERE, "inputs-v2", "manifest.json")
    man = json.load(open(man_path, encoding="utf-8"))
    f2b_man = json.load(open(os.path.join(POC, "f2b", "inputs",
                                          "f2b-manifest.json"),
                             encoding="utf-8"))
    frames = f2b_man["prompt_frames"]

    def ntok(s):
        return len(tok.encode(s).ids)

    out = {"schema": "kot-knull-g3/1",
           "gate": "G-3 tokenizer-level FLOPs band re-check",
           "tokenizer": {"repo": TOKENIZER_REPO,
                         "revision": TOKENIZER_REVISION,
                         "tokenizer_json_sha256": TOKENIZER_SHA256},
           "inputs_manifest_sha256": file_sha256(man_path),
           "opaque_token_calibration_factor":
               man["opaque_token_calibration"]["factor"],
           "mean_band_declared": MEAN_BAND,
           "runtime_gate_band": 0.20,
           "arms": {}}

    stats = {}
    for a in ARMS:
        path = os.path.join(HERE, "inputs-v2", "items", "%s.jsonl" % a)
        items = [json.loads(l) for l in open(path, encoding="utf-8")
                 if l.strip()]
        prompt_toks = [ntok(build_prompt(frames, it)) for it in items]
        gloss_toks = {}
        roots = {"kernel": ROOT,
                 "plain": os.path.join(HERE, "inputs-v2", "stores", "plain"),
                 "opaque": os.path.join(HERE, "inputs-v2", "stores", "opaque")}
        seen = set()
        for it in items:
            if it["label"] in seen:
                continue
            seen.add(it["label"])
            rec = json.load(open(os.path.join(roots[a], it["record_path"]),
                                 encoding="utf-8"))
            text = rec.get("gloss") or rec.get("groundingNote", "")
            gloss_toks[it["label"]] = ntok(text)
        n = len(prompt_toks)
        stats[a] = {
            "n_items": n,
            "mean_prompt_tokens": sum(prompt_toks) / n,
            "max_prompt_tokens": max(prompt_toks),
            "total_gloss_tokens": sum(gloss_toks.values()),
        }

    kmean = stats["kernel"]["mean_prompt_tokens"]
    violations = []
    for a in ARMS:
        ratio = stats[a]["mean_prompt_tokens"] / kmean
        stats[a]["mean_prompt_token_ratio_vs_kernel"] = round(ratio, 4)
        stats[a]["within_declared_band"] = bool(abs(ratio - 1.0) <= MEAN_BAND)
        if not stats[a]["within_declared_band"]:
            violations.append((a, ratio))
        out["arms"][a] = {k: (round(v, 2) if isinstance(v, float) else v)
                          for k, v in stats[a].items()}

    n_planned = man["n_items_planned_per_arm"]
    out["margin_call_f_kn_c"] = {
        "n_planned_per_arm": n_planned,
        "n_floor_for_margin_005": 900,
        "decision": ("margin 0.05 STANDS (n_planned %d >= 900; fork F-KN-C "
                     "fallback 0.075 not triggered)" % n_planned)
        if n_planned >= 900 else
        ("margin 0.075 (fork F-KN-C fallback: n_planned %d < 900)" % n_planned),
    }
    out["result"] = "PASS" if not violations else "FAIL"

    opath = os.path.join(HERE, "inputs-v2", "g3-token-band.json")
    with open(opath, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")

    for a in ARMS:
        print("%-7s mean prompt tokens %7.1f  ratio vs kernel %.3f  %s"
              % (a, stats[a]["mean_prompt_tokens"],
                 stats[a]["mean_prompt_token_ratio_vs_kernel"],
                 "OK" if stats[a]["within_declared_band"] else "OUT OF BAND"))
    print(out["margin_call_f_kn_c"]["decision"])
    print("G-3: %s -> %s" % (out["result"], opath))
    if violations:
        die("KNULL_ERR_G3_BAND",
            "arm(s) out of the +/-%.0f%% mean-token band: %s"
            % (MEAN_BAND * 100,
               ", ".join("%s(%.3f)" % v for v in violations)))


if __name__ == "__main__":
    main()
