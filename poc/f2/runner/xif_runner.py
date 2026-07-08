#!/usr/bin/env python3
"""d-xif builder + IF-1 fork pilot runner (P10 sections 3-4; pre-final-phase).

This is NOT the F2 experiment harness. It is the deterministic builder of the
P10 held-out labelled extraction set (d-xif) and the pre-registered IF-1
fork-pilot measurement, run ONCE on a small Modal GPU job BEFORE the F2
final phase (operational DAG: d-xif < f2.iface < f2.run).

It deliberately imports the FROZEN harness's own machinery from
f2_runner.py — extract_record, KernelVerifier, HFLM (the IF-C constrained
surface), build_prompt, the pinned prompt frames — so the instrument being
measured is byte-identical to the instrument the final phase will deploy.

Per rung (R1 = SmolLM2-135M-Instruct, R2 = SmolLM2-360M-Instruct, pinned
revisions from inputs/f2-manifest.json), for EVERY d-qa item (500 covered +
150 control, pinned order):

  1. IF-C output: the constrained-decoding answer (sequence-logprob selection
     over the pinned option set, greedy attempt 0 — the deployed shared
     affordance), then the P10 extraction into a kernel-checkable record via
     the harness's extract_record + KernelVerifier (per-item record_sha256
     pin, fail closed). Extraction SUCCESS/FAILURE is recorded MECHANICALLY:
     success = a well-formed record was produced AND (for kernel-covered
     items) the deterministic verifier could decide it. No human labelling.
  2. Unconstrained output: greedy free decode (max_new_tokens pinned below)
     from the IDENTICAL prompt — the "without the format constraint" arm of
     the IF-1 tax measurement.
  3. IF-A strict extraction of (2): the deterministic parser IFA-PARSE/1
     (pinned rules in ifa_parse below).
  4. Mechanical reference annotation GOLD-ANN/1 of (2) (pinned rules in
     gold_annotate below) — the no-human-in-the-loop stand-in for the P10
     gold-record annotation; blind to arm identity (there is only the
     model-alone arm here). The IF-A F1 measured against it is
     parser-vs-reference agreement and is flagged as such: if the IF-1 fork
     condition ever fires on this number, human audit of the annotation is
     required before adopting IF-A.

Gate arithmetic (P10 section 4, frozen thresholds from the f2 registry
record): extraction-failure rate over the >=300 (here 500) labelled
kernel-covered outputs per rung; one-sided 95% Wilson lower bound
(z = 1.645, the pinned analysis/f2.py formula, copied verbatim);
Wilson-LB > 0.10 => the consuming correctness arms are INSTRUMENT-INVALID.

IF-1 fork (P10 section 3, deciding measurement pre-declared): on the first
200 covered items per rung, constrained-format tax = accuracy delta with vs
without the constraint; IF-A replaces IF-C ONLY IF the tax is a degradation
of Cohen's h >= 0.2 established by paired item bootstrap at alpha = 0.05
(one-sided 95% lower bound of h_degradation >= 0.2; B = 10000, seed
20260708 — the pinned f2 SAP PRNG) AND IF-A extraction F1 >= 0.95 on the
labelled set. Otherwise IF-C stands. Decided once, before the final phase.

  python3 xif_runner.py --out-dir /tmp/xif --mock          # $0 local check
  (real path runs on Modal via poc/modal/modal_f2_xif.py)

HARD RULES: --mock spends $0, touches no GPU or network, and labels every
number MOCK; the real path fails closed on any missing pin (ERR_*); no
measurement is ever fabricated — every rate below is computed from the
per-output records shipped alongside it.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import f2_runner as f2  # the FROZEN harness machinery (see module docstring)

# ---------------------------------------------------------------------------
# Pinned pilot constants (builder identity — recorded into d-xif/manifest.json)
# ---------------------------------------------------------------------------
XIF_SPEC = "kot-dxif/1"
GEN_MAX_NEW_TOKENS = 24          # free-decode budget (short-answer items)
IF1_N = 200                      # P10 section 3: n = 200 outputs per rung
BOOT_B = 10000                   # pinned f2 SAP bootstrap size
BOOT_SEED = 20260708             # pinned f2 SAP PRNG seed
Z_ONE_SIDED = 1.645              # analysis/f2.py Z_ONE_SIDED (one-sided 95%)
IFACE_FAIL_BOUND = 0.10          # P10: failure Wilson-LB > 10% => INVALID
IFA_F1_BAR = 0.95                # P10 section 3 fork threshold
TAX_H_BAR = 0.2                  # P10 section 3 fork threshold (Cohen's h)
RUNGS = ("R1", "R2")


def wilson_lb(p, n, z=Z_ONE_SIDED):
    """Verbatim from the pinned analysis/f2.py (sha 068f68b8...)."""
    if n <= 0:
        return 0.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n)


def cohens_h(p1, p2):
    clamp = lambda p: min(max(p, 0.0), 1.0)  # noqa: E731
    return 2 * math.asin(math.sqrt(clamp(p1))) - 2 * math.asin(math.sqrt(clamp(p2)))


# ---------------------------------------------------------------------------
# IFA-PARSE/1 — the strict deterministic IF-A parser (the deployable
# candidate; pinned rules, applied to the raw free-decode text).
# ---------------------------------------------------------------------------
MCQ_KEY_RE = re.compile(r"^\s*[\(\[]?([A-Da-d])[\)\]]?(?:[.:,;]|\s|$)")
YESNO_RE = re.compile(r"^\s*[\(\[]?(yes|no)\b", re.IGNORECASE)


def ifa_parse(item, text):
    """text -> option key / 'yes'/'no', or None (parse failure). Rules:
    (a) MCQ: the text must BEGIN with a single option key A-D (optionally
        parenthesised / punctuated); else (b) the text, normalised, must
        begin with exactly one option's full normalised text.
    (c) claims: the text must BEGIN with yes/no (case-insensitive).
    Anything else is a parse failure — strict on purpose: IF-A's risk is
    exactly that free text does not surrender a record."""
    if item.get("options"):
        m = MCQ_KEY_RE.match(text)
        if m:
            return m.group(1).upper()
        norm = f2.norm_text(text)
        hits = [o["key"] for o in item["options"]
                if norm.startswith(f2.norm_text(o["text"]))]
        return hits[0] if len(hits) == 1 else None
    m = YESNO_RE.match(text)
    return m.group(1).lower() if m else None


# ---------------------------------------------------------------------------
# GOLD-ANN/1 — the mechanical reference annotation of a free-decode output
# (what answer, if any, does the output assert?). Deliberately MORE lenient
# than IFA-PARSE/1: whole-text search, cue phrases, option-text containment.
# Returns a key / 'yes'/'no', or None = "no unambiguous assertion".
# ---------------------------------------------------------------------------
CUE_RE = re.compile(
    r"\b(?:answer(?:\s+is)?|option|choose|choice|select)\s*[:\-]?\s*"
    r"[\(\[]?([A-Da-d])\b", re.IGNORECASE)
LONE_KEY_RE = re.compile(r"(?<![A-Za-z])([A-D])(?:[.:,;)\]]|\s|$)")
YESNO_ANY_RE = re.compile(r"\b(yes|no)\b", re.IGNORECASE)


def gold_annotate(item, text):
    if item.get("options"):
        cands = set()
        m = MCQ_KEY_RE.match(text)
        if m:
            cands.add(m.group(1).upper())
        for m in CUE_RE.finditer(text):
            cands.add(m.group(1).upper())
        if not cands:
            for m in LONE_KEY_RE.finditer(text):
                cands.add(m.group(1))
        norm = f2.norm_text(text)
        text_hits = {o["key"] for o in item["options"]
                     if f2.norm_text(o["text"]) and f2.norm_text(o["text"]) in norm}
        if not cands and text_hits:
            cands = text_hits
        return cands.pop() if len(cands) == 1 else None
    hits = {m.group(1).lower() for m in YESNO_ANY_RE.finditer(text)}
    return hits.pop() if len(hits) == 1 else None


# ---------------------------------------------------------------------------
# Free-decode generation (real + mock)
# ---------------------------------------------------------------------------
def hf_generate(lm, prompt):
    """Greedy free decode from the identical shared-affordance prompt."""
    torch = lm.torch
    ids = lm.tok.encode(prompt, add_special_tokens=False)
    x = torch.tensor([ids], device=lm.device)
    with torch.no_grad():
        out = lm.model.generate(
            x, max_new_tokens=GEN_MAX_NEW_TOKENS, do_sample=False,
            num_beams=1, pad_token_id=(lm.tok.pad_token_id
                                       if lm.tok.pad_token_id is not None
                                       else lm.tok.eos_token_id))
    return lm.tok.decode(out[0][len(ids):], skip_special_tokens=True)


def mock_generate(lm, item, keys, gold, seed):
    """SYNTHETIC free-decode stand-in (mock only; labelled MOCK end-to-end).
    Mixes in-format answers, cue-phrase answers, and garbage so every parser
    branch is exercised."""
    u = f2.det_u("gen", lm.name, item["id"], seed)
    v = f2.det_u("genpick", lm.name, item["id"], seed)
    ans = gold if v < lm.skill else keys[int(v * 31) % len(keys)]
    if u < 0.70:
        return "%s." % ans
    if u < 0.80:
        return "The answer is %s because of the definition." % ans
    if u < 0.90:
        return " %s) I think." % ans
    if u < 0.96:
        return "Well, it could be %s or maybe %s." % (keys[0], keys[-1])
    return "the meaning of a word is a thing people say"


# ---------------------------------------------------------------------------
# Per-rung labelled-set generation
# ---------------------------------------------------------------------------
def run_rung(lm, frames, covered, control, verifier, mock, log):
    outputs = []
    for slice_name, items in (("covered", covered), ("control", control)):
        for it in items:
            keys, gold = f2.item_keys_gold(it)
            prompt = f2.build_prompt(frames, it)
            # (1) IF-C constrained output (the deployed surface, greedy)
            if mock:
                ans_c, conf = lm.choose(it, keys, gold, 0, 0)
            else:
                ans_c, conf = lm.choose(it, keys, gold, 0, 0, prompt=prompt)
            # (2) P10 extraction + kernel-checkability, MECHANICAL
            ok_ext, decidable, consistent, _cpu = f2.verify_answer(
                verifier, it, ans_c)
            checkable = bool(ok_ext and (slice_name != "covered" or decidable))
            # P10's second rate (extraction ERROR = well-formed but wrong
            # record vs what the output asserts): mechanical round-trip
            # identity check of the extracted record against the asserted
            # option/claim (under IF-C the record is a deterministic copy of
            # pinned item fields, so this SHOULD always hold — measured, not
            # assumed)
            rec = f2.extract_record(it, ans_c)
            roundtrip = False
            if rec is not None:
                if rec["kind"] == "definition":
                    opt = {o["key"]: o["text"] for o in it["options"]}
                    roundtrip = rec["text"] == opt.get(ans_c)
                elif rec["kind"] == "term-for-definition":
                    opt = {o["key"]: o["text"] for o in it["options"]}
                    roundtrip = rec["term"] == opt.get(ans_c)
                else:
                    roundtrip = (rec["claim"] == it["claim"]
                                 and rec["verdict"] == ans_c)
            # (3) unconstrained free decode from the IDENTICAL prompt
            gen = (mock_generate(lm, it, keys, gold, 0) if mock
                   else hf_generate(lm, prompt))
            # (4) IF-A strict parse + (5) mechanical reference annotation
            parsed = ifa_parse(it, gen)
            gold_ann = gold_annotate(it, gen)
            outputs.append({
                "id": it["id"], "slice": slice_name, "type": it["type"],
                "answer_gold_item": it["answer"],
                "ifc_answer": ans_c, "ifc_margin": float(conf),
                "ifc_extract_ok": bool(ok_ext),
                "ifc_roundtrip_ok": bool(roundtrip),
                "ifc_checkable_record": checkable,
                "ifc_verifier_decidable": bool(decidable),
                "ifc_verifier_consistent": bool(consistent),
                "gen_text": gen,
                "ifa_parsed": parsed,
                "gold_annotation": gold_ann,
                "gold_method": "GOLD-ANN/1 (mechanical reference annotation; "
                               "see xif_runner.py docstring caveat)",
            })
        log("  %s slice done (%d outputs)" % (slice_name, len(items)))
    return outputs


# ---------------------------------------------------------------------------
# Gate + IF-1 arithmetic (computed FROM the shipped per-output records)
# ---------------------------------------------------------------------------
def gate_stats(outputs):
    cov = [o for o in outputs if o["slice"] == "covered"]
    n = len(cov)
    fails = sum(1 for o in cov if not o["ifc_checkable_record"])
    # P10's second rate: well-formed but WRONG record vs the asserted
    # content — the mechanical round-trip identity check from run_rung
    # (measured, not assumed; expected 0 by IF-C construction)
    errs = sum(1 for o in cov
               if o["ifc_checkable_record"] and not o["ifc_roundtrip_ok"])
    p_fail = fails / n if n else 0.0
    lb_fail = wilson_lb(p_fail, n)
    ctl = [o for o in outputs if o["slice"] == "control"]
    return {
        "n_labelled": n,
        "n_extraction_failures": fails,
        "n_extraction_errors": errs,
        "failure_rate": p_fail,
        "failure_wilson_lb_one_sided_95": lb_fail,
        "success_wilson_lb_one_sided_95": wilson_lb(1.0 - p_fail, n)
        if n else 0.0,
        "gate_pass": bool(n >= 300 and lb_fail <= IFACE_FAIL_BOUND),
        "gate_rule": "P10 section 4 / f2.reg iface_gate: n>=300 per rung AND "
                     "failure Wilson-LB (z=1.645) <= 0.10",
        "control_descriptive": {
            "n": len(ctl),
            "n_record_parse_failures": sum(
                1 for o in ctl if not o["ifc_extract_ok"]),
            "note": "control items are NOT kernel-checkable by design "
                    "(verifier abstains); descriptive only, outside the gate",
        },
    }


def paired_bootstrap_h(pairs, b=BOOT_B, seed=BOOT_SEED):
    """pairs = [(unconstrained_correct, constrained_correct)] per item.
    h_degradation = cohens_h(p_unconstrained, p_constrained): positive when
    the format constraint COSTS accuracy (constrained worse). Paired item
    bootstrap; returns the point estimate, one-sided 95% lower/upper bounds
    and p(h_deg <= 0)."""
    n = len(pairs)
    rng = random.Random(seed)
    point = cohens_h(sum(u for u, _ in pairs) / n, sum(c for _, c in pairs) / n)
    hs = []
    for _ in range(b):
        s_u = s_c = 0
        for _ in range(n):
            u, c = pairs[rng.randrange(n)]
            s_u += u
            s_c += c
        hs.append(cohens_h(s_u / n, s_c / n))
    hs.sort()
    lb = hs[int(math.floor(0.05 * b))]
    ub = hs[min(b - 1, int(math.floor(0.95 * b)))]
    p_le0 = sum(1 for h in hs if h <= 0.0) / float(b)
    return {"h_degradation_point": point, "h_lb_95_one_sided": lb,
            "h_ub_95_one_sided": ub, "p_boot_h_le_0": p_le0,
            "B": b, "seed": seed, "n_items": n}


def if1_stats(outputs):
    cov = [o for o in outputs if o["slice"] == "covered"][:IF1_N]
    pairs = []
    n_unparseable_ann = 0
    for o in cov:
        con = 1 if o["ifc_answer"] == o["answer_gold_item"] else 0
        unc = 1 if (o["gold_annotation"] is not None
                    and o["gold_annotation"] == o["answer_gold_item"]) else 0
        if o["gold_annotation"] is None:
            n_unparseable_ann += 1
        pairs.append((unc, con))
    acc_c = sum(c for _, c in pairs) / len(pairs)
    acc_u = sum(u for u, _ in pairs) / len(pairs)
    boot = paired_bootstrap_h(pairs)
    # IF-A F1 vs GOLD-ANN/1 over ALL labelled covered outputs (the full set)
    allcov = [o for o in outputs if o["slice"] == "covered"]
    tp = sum(1 for o in allcov if o["ifa_parsed"] is not None
             and o["ifa_parsed"] == o["gold_annotation"])
    n_parsed = sum(1 for o in allcov if o["ifa_parsed"] is not None)
    n_gold = sum(1 for o in allcov if o["gold_annotation"] is not None)
    prec = tp / n_parsed if n_parsed else 0.0
    rec = tp / n_gold if n_gold else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "n_if1_slice": len(pairs),
        "acc_constrained_ifc": acc_c,
        "acc_unconstrained_gold_ann": acc_u,
        "n_unconstrained_no_assertion": n_unparseable_ann,
        "format_tax_bootstrap": boot,
        "ifa_precision": prec, "ifa_recall": rec, "ifa_f1": f1,
        "ifa_f1_n_outputs": len(allcov), "ifa_n_parsed": n_parsed,
        "ifa_n_gold_assertions": n_gold,
        "ifa_f1_caveat": "F1 is parser-vs-mechanical-reference agreement "
                         "(GOLD-ANN/1), not parser-vs-human gold; if the fork "
                         "condition fires on it, human audit is required "
                         "before adopting IF-A (see docstring)",
    }


def fork_decision(per_rung):
    """P10 section 3, applied per rung then conjunctively: IF-A replaces IF-C
    only if AT EVERY MEASURED RUNG the constrained format is a degradation of
    Cohen's h >= 0.2 (one-sided 95% bootstrap lower bound >= 0.2) AND IF-A F1
    >= 0.95. The conjunction over rungs is the conservative reading (the
    default only yields to consistent evidence); recorded here explicitly."""
    per = {}
    for rung, s in per_rung.items():
        b = s["format_tax_bootstrap"]
        tax_fires = b["h_lb_95_one_sided"] >= TAX_H_BAR
        f1_ok = s["ifa_f1"] >= IFA_F1_BAR
        per[rung] = {"tax_degradation_h_lb": b["h_lb_95_one_sided"],
                     "tax_condition_h_lb_ge_0.2": bool(tax_fires),
                     "ifa_f1": s["ifa_f1"],
                     "f1_condition_ge_0.95": bool(f1_ok),
                     "both": bool(tax_fires and f1_ok)}
    replace = all(v["both"] for v in per.values()) and bool(per)
    return {"rule": fork_decision.__doc__.strip(),
            "per_rung": per,
            "choice": "IF-A" if replace else "IF-C",
            "if_c_stands": not replace}


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--inputs-dir", default=os.path.join(here, "..", "inputs"))
    ap.add_argument("--dqa-dir", default=os.path.join(here, "..", "..", "..",
                                                      "data", "d-qa"))
    ap.add_argument("--records-root", default=os.path.join(here, "..", "..", ".."))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--mock", action="store_true",
                    help="StubLM mechanics check on CPU; $0; labelled MOCK")
    args = ap.parse_args()
    t0 = time.time()

    man, covered, control, _gloss, _rag = f2.load_inputs(
        args.inputs_dir, args.dqa_dir)
    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[xif %6.1fs] %s" % (time.time() - t0, msg), flush=True)

    if args.mock:
        mk = man["mock"]
        covered = covered[:mk["n_covered_items"]]
        control = control[:mk["n_control_items"]]
    label = "MOCK" if args.mock else "REAL"
    log("mode=%s device=%s items=%d covered / %d control rungs=%s"
        % (label, args.device, len(covered), len(control), ",".join(RUNGS)))

    verifier = f2.KernelVerifier(args.records_root)
    verifier.index_labels(covered)
    frames = man["prompt_frames"]

    per_rung_gate, per_rung_if1, model_names = {}, {}, {}
    for rung in RUNGS:
        if args.mock:
            lm = f2.StubLM(rung, man["mock"])
        else:
            spec = man["models"][rung]
            lm = f2.HFLM(spec["repo"], spec["revision"], args.device)
        model_names[rung] = lm.name
        log("rung %s: model %s" % (rung, lm.name))
        outputs = run_rung(lm, frames, covered, control, verifier,
                           args.mock, log)
        opath = os.path.join(args.out_dir,
                             "xif-outputs-%s%s.jsonl"
                             % (rung.lower(), "-mock" if args.mock else ""))
        with open(opath, "w", encoding="utf-8") as fh:
            for o in outputs:
                fh.write(json.dumps(o, sort_keys=True, ensure_ascii=False) + "\n")
        per_rung_gate[rung] = gate_stats(outputs)
        per_rung_if1[rung] = if1_stats(outputs)
        g = per_rung_gate[rung]
        log("rung %s gate: %d/%d failures rate=%.4f wilson_lb=%.4f -> %s"
            % (rung, g["n_extraction_failures"], g["n_labelled"],
               g["failure_rate"], g["failure_wilson_lb_one_sided_95"],
               "PASS" if g["gate_pass"] else "GATE-FAIL"))

    fork = fork_decision(per_rung_if1)
    suffix = "-mock" if args.mock else ""
    results = {
        "spec": XIF_SPEC,
        "outcome": ("MOCK-XIF-PILOT-COMPLETE" if args.mock
                    else "XIF-PILOT-COMPLETE"),
        "mode": label,
        "date": f2.utcnow(),
        "device": args.device,
        "models": ({"note": "MOCK — synthetic stub LM, no models loaded"}
                   if args.mock else
                   {r: {"repo": man["models"][r]["repo"],
                        "revision": man["models"][r]["revision"],
                        "loaded_as": model_names[r]} for r in RUNGS}),
        "pins": man["pins"],
        "constants": {"gen_max_new_tokens": GEN_MAX_NEW_TOKENS,
                      "if1_n": IF1_N, "boot_B": BOOT_B,
                      "boot_seed": BOOT_SEED, "z_one_sided": Z_ONE_SIDED,
                      "iface_fail_bound": IFACE_FAIL_BOUND,
                      "ifa_f1_bar": IFA_F1_BAR, "tax_h_bar": TAX_H_BAR},
        "gate": per_rung_gate,
        "if1": per_rung_if1,
        "if1_fork": fork,
        "instrument_valid_precondition": bool(
            all(g["gate_pass"] for g in per_rung_gate.values())),
        "wallClockHours": (time.time() - t0) / 3600.0,
    }
    with open(os.path.join(args.out_dir, "results-xif%s.json" % suffix),
              "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)
    log("OUTCOME: %s (fork choice: %s; instrument precondition: %s)"
        % (results["outcome"], fork["choice"],
           results["instrument_valid_precondition"]))


if __name__ == "__main__":
    main()
