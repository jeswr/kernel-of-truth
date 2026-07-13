#!/usr/bin/env python3
"""knull-v2 Option-B — BINDING G-3 tokenizer-level FLOPs-band check over the
FOUR-ARM v4 inputs (pre-freeze blocker B-2 of poc/knull/freeze-prep/
README.md; band scope per docs/next/design/knull-optionb-analysis.md
section 4.4, ASM-1085).

V4 DELTA (the ONLY changes from the pinned v2 checker poc/knull/
check_token_band_v2.py; custody pattern — the pinned v1/v2 checker bytes
stay untouched):
  - every input/output path reads poc/knull/inputs-v4/;
  - FOUR arms (kernel, plain, plain-padded, opaque);
  - BAND SCOPE RE-SCOPED (ASM-1085): the pre-freeze +/-10% mean-prompt-token
    band BINDS the TOKEN-MATCHED arms only — plain-padded and opaque vs
    kernel. The concise plain arm is EXEMPT BY DESIGN (the Option-B ruling's
    point): its ratio is MEASURED and DISCLOSED here, descriptive only,
    never a PASS/FAIL input;
  - additionally writes inputs-v4/prompt-tokens.json — per-arm, per-item
    prompt token counts in item-file (rank-sorted) order. This sidecar is
    the MEASURED source for the SAP's descriptive length reads
    (analysis/knull_v3.py /analysis/length_sensitivity item_meta contract)
    and resolves the ASM-1088 pre-freeze projections at build level (the
    run-time F0 FLOPs ledger remains the final binding resolution).

Tokenizer pin, prompt rendering (pinned f2b build_prompt over the built item
files), PASS criteria width and artifact schema are byte-carried from v2.
Original rationale: see check_token_band.py / check_token_band_v2.py
docstrings (the word band is a PROXY; this check meters the TOKEN quantity
the FLOPs-parity gate actually binds).

The tokenizer file is NOT committed (3.5 MB, third-party); this check pins
it by (repo, revision, sha256) and refuses any other bytes. Re-fetch:
  curl -sL -o tokenizer.json https://huggingface.co/<TOKENIZER_REPO>/resolve/<TOKENIZER_REVISION>/tokenizer.json

Usage:
  python3 poc/knull/check_token_band_v4.py --tokenizer-json <path>
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

ARMS = ("kernel", "plain", "plain-padded", "opaque")
# ASM-1085 scope: the band BINDS the token-matched arms only.
BOUND_ARMS = ("plain-padded", "opaque")
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

    man_path = os.path.join(HERE, "inputs-v4", "manifest.json")
    man = json.load(open(man_path, encoding="utf-8"))
    f2b_man = json.load(open(os.path.join(POC, "f2b", "inputs",
                                          "f2b-manifest.json"),
                             encoding="utf-8"))
    frames = f2b_man["prompt_frames"]

    def ntok(s):
        return len(tok.encode(s).ids)

    out = {"schema": "kot-knull-g3/2",
           "gate": ("G-3 tokenizer-level FLOPs band re-check, four-arm "
                    "Option-B scope"),
           "band_scope": ("ASM-1085: the band BINDS the token-matched arms "
                          "(plain-padded, opaque) vs kernel; the concise "
                          "plain arm is EXEMPT BY DESIGN — its ratio is "
                          "measured and disclosed DESCRIPTIVE below, never "
                          "a PASS/FAIL input. Run-time binding resolution "
                          "of parity = the F0 FLOPs ledger (ASM-1088)."),
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
    per_item = {}
    roots = {"kernel": ROOT,
             "plain": os.path.join(HERE, "inputs-v4", "stores", "plain"),
             "plain-padded": os.path.join(HERE, "inputs-v4", "stores",
                                          "plain-padded"),
             "opaque": os.path.join(HERE, "inputs-v4", "stores", "opaque")}
    skeleton_order = None
    for a in ARMS:
        path = os.path.join(HERE, "inputs-v4", "items", "%s.jsonl" % a)
        items = [json.loads(l) for l in open(path, encoding="utf-8")
                 if l.strip()]
        order = [it["skeleton_uid"] for it in items]
        if skeleton_order is None:
            skeleton_order = order
        elif order != skeleton_order:
            die("KNULL_ERR_G3_PAIRING",
                "%s item order differs from kernel (pairing broken)" % a)
        prompt_toks = [ntok(build_prompt(frames, it)) for it in items]
        per_item[a] = prompt_toks
        gloss_toks = {}
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
        stats[a]["band_binding"] = a in BOUND_ARMS
        if a in BOUND_ARMS:
            stats[a]["within_declared_band"] = bool(abs(ratio - 1.0) <= MEAN_BAND)
            if not stats[a]["within_declared_band"]:
                violations.append((a, ratio))
        elif a == "plain":
            stats[a]["within_declared_band"] = None
            stats[a]["descriptive_disclosure"] = (
                "measured ratio %.4f — outside the parity band AS THE "
                "OPTION-B RULING INTENDS (natural concise length; the "
                "token-matched comparison lives in the plain-padded arm); "
                "reported at run time as /gates/flops_ratio_plain, "
                "DESCRIPTIVE (ASM-1085)" % ratio)
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

    # MEASURED per-item prompt-token sidecar (feeds the knull_v3 item_meta
    # length reads; see this file's docstring)
    sidecar = {
        "schema": "kot-knull-prompt-tokens/1",
        "note": ("per-item prompt token counts under the pinned tokenizer, "
                 "in item-file (rank-sorted) order — identical "
                 "skeleton_uid order across arms (checked fail-closed at "
                 "this build); MEASURED source for the "
                 "analysis/knull_v3.py item_meta prompt_tokens contract "
                 "(/analysis/length_sensitivity, descriptive)"),
        "tokenizer_json_sha256": TOKENIZER_SHA256,
        "inputs_manifest_sha256": out["inputs_manifest_sha256"],
        "skeleton_order_sha256": hashlib.sha256(
            "|".join(skeleton_order).encode("utf-8")).hexdigest(),
        "arms": {a: per_item[a] for a in ARMS},
    }
    spath = os.path.join(HERE, "inputs-v4", "prompt-tokens.json")
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=1, sort_keys=True)
        f.write("\n")
    out["prompt_tokens_sidecar"] = {
        "path": "poc/knull/inputs-v4/prompt-tokens.json",
        "sha256": file_sha256(spath),
    }

    opath = os.path.join(HERE, "inputs-v4", "g3-token-band.json")
    with open(opath, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")

    for a in ARMS:
        band = ("REFERENCE" if a == "kernel"
                else "OK" if stats[a].get("within_declared_band")
                else "OUT OF BAND" if stats[a].get("within_declared_band")
                is False else "DESCRIPTIVE (not bound)")
        print("%-12s mean prompt tokens %7.1f  ratio vs kernel %.3f  %s"
              % (a, stats[a]["mean_prompt_tokens"],
                 stats[a]["mean_prompt_token_ratio_vs_kernel"], band))
    print(out["margin_call_f_kn_c"]["decision"])
    print("G-3 (band binds %s): %s -> %s"
          % ("+".join(BOUND_ARMS), out["result"], opath))
    print("prompt-token sidecar -> %s" % spath)
    if violations:
        die("KNULL_ERR_G3_BAND",
            "bound arm(s) out of the +/-%.0f%% mean-token band: %s"
            % (MEAN_BAND * 100,
               ", ".join("%s(%.3f)" % v for v in violations)))


if __name__ == "__main__":
    main()
