#!/usr/bin/env python3
"""Benchmark adapters for poc/pubeval — openly-licensed HUMAN-built public
benchmarks (docs/next/analysis/existing-benchmarks-survey.md §4 top picks).

Adopted set (survey recommendation order; gold-provenance taxonomy per
PROPOSED-ASM-1590):

  folio           FOLIO validation split      HUMAN-AUTHORED   MIT
  arc_easy        ARC-Easy test split         HUMAN-SOURCED    CC BY-SA 4.0
  arc_challenge   ARC-Challenge test split    HUMAN-SOURCED    CC BY-SA 4.0
  gsm8k           GSM8K test split            HUMAN-AUTHORED   MIT

EntailmentBank (survey adoption #2 package) is deliberately NOT wired here:
it is a store-projection/attribution instrument, not a plain LM benchmark
surface; its ARC end-task carrier IS wired. No LLM-PROXY gold anywhere.

Normalised item schemas (fail-closed on any missing field, ERR_BENCH_SCHEMA):
  MC  : {"id", "context", "options": [str], "gold": int}
        context ends with "Answer:"; each option is scored as the
        continuation " <option>" (f2bt HFLM forced-choice convention).
  GEN : {"id", "context", "gold_answer": str, "gold_solution": str}

Every adapter also carries MOCK fixtures (SYNTHETIC, mechanics-only — never a
measurement; f2bt StubLM discipline) so --mock runs offline with zero deps.

Stdlib only. Python 3.9 compatible (the coordinator box).
"""

from __future__ import annotations

import json
import os
import re

ERR_SCHEMA = "ERR_BENCH_SCHEMA"
ERR_DATA = "ERR_BENCH_DATA"

# Data files written by fetch_data.py (raw released rows, one JSON per line).
DATA_FILES = {
    "folio": {"eval": "folio_validation.jsonl", "fewshot": "folio_train.jsonl"},
    "arc_easy": {"eval": "arc_easy_test.jsonl", "fewshot": "arc_easy_train.jsonl"},
    "arc_challenge": {"eval": "arc_challenge_test.jsonl",
                      "fewshot": "arc_challenge_train.jsonl"},
    "gsm8k": {"eval": "gsm8k_test.jsonl", "fewshot": "gsm8k_train.jsonl"},
}

LICENSES = {
    # [search 2026-07-12] tags per the survey; re-verify at any freeze.
    "folio": {"license": "MIT", "provenance": "HUMAN-AUTHORED",
              "source": "yale-nlp/FOLIO (arXiv:2209.00840)"},
    "arc_easy": {"license": "CC BY-SA 4.0", "provenance": "HUMAN-SOURCED (EXAM)",
                 "source": "allenai/ai2_arc ARC-Easy"},
    "arc_challenge": {"license": "CC BY-SA 4.0",
                      "provenance": "HUMAN-SOURCED (EXAM)",
                      "source": "allenai/ai2_arc ARC-Challenge"},
    "gsm8k": {"license": "MIT", "provenance": "HUMAN-AUTHORED",
              "source": "openai/grade-school-math"},
}


def _load_jsonl(path):
    if not os.path.exists(path):
        raise SystemExit(
            "%s: missing %s — run poc/pubeval/fetch_data.py first "
            "(or use --mock)" % (ERR_DATA, path))
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise SystemExit("%s: %s line %d: %s"
                                     % (ERR_DATA, path, i + 1, e))
    if not rows:
        raise SystemExit("%s: %s is empty" % (ERR_DATA, path))
    return rows


def _need(row, key, bench):
    if key not in row or row[key] in (None, ""):
        raise SystemExit("%s: %s row missing %r (keys: %s)"
                         % (ERR_SCHEMA, bench, key, sorted(row)[:20]))
    return row[key]


# ---------------------------------------------------------------------------
# FOLIO — 3-way forced choice (True/False/Uncertain) over human premises.
# Frame mirrors the paper's NL task; scored at the f2bt host seam
# (survey §2.2 FOLIO seam (i), LOW effort).
# ---------------------------------------------------------------------------
_FOLIO_OPTIONS = ["True", "False", "Uncertain"]
_FOLIO_LABELS = {"True": 0, "False": 1, "Uncertain": 2, "Unknown": 2}


def _folio_norm(row, idx):
    prem = _need(row, "premises", "folio")
    if isinstance(prem, list):
        prem = "\n".join(str(p) for p in prem)
    concl = _need(row, "conclusion", "folio")
    label = str(_need(row, "label", "folio")).strip()
    if label not in _FOLIO_LABELS:
        raise SystemExit("%s: folio unknown label %r" % (ERR_SCHEMA, label))
    rid = row.get("example_id", row.get("story_id", idx))
    ctx = ("Premises:\n%s\nConclusion: %s\n"
           "Question: Based on the premises alone, is the conclusion true, "
           "false, or uncertain?\nAnswer:" % (prem, concl))
    return {"id": "folio-%s" % rid, "context": ctx,
            "options": list(_FOLIO_OPTIONS), "gold": _FOLIO_LABELS[label]}


# ---------------------------------------------------------------------------
# ARC — N-way multiple choice; continuation is the raw choice text
# (EleutherAI lm-evaluation-harness ARC convention: acc + acc_norm).
# ---------------------------------------------------------------------------
def _arc_norm(row, idx, bench):
    q = _need(row, "question", bench)
    choices = _need(row, "choices", bench)
    texts = _need(choices, "text", bench)
    labels = _need(choices, "label", bench)
    key = str(_need(row, "answerKey", bench))
    labels = [str(x) for x in labels]
    if key not in labels:
        raise SystemExit("%s: %s answerKey %r not in labels %s"
                         % (ERR_SCHEMA, bench, key, labels))
    ctx = "Question: %s\nAnswer:" % q
    return {"id": "%s-%s" % (bench, row.get("id", idx)), "context": ctx,
            "options": [str(t) for t in texts], "gold": labels.index(key)}


# ---------------------------------------------------------------------------
# GSM8K — generative, exact match on the final number ("#### N" convention,
# github.com/openai/grade-school-math). Calculator annotations <<...>> are
# stripped from few-shot solutions, as in the original repo's evaluation.
# ---------------------------------------------------------------------------
_GSM_CALC = re.compile(r"<<[^>]*>>")
_GSM_GOLD = re.compile(r"####\s*(-?[\d,\.]+)")


def normalize_number(s):
    """Canonical final-number form: strip commas/space/trailing dot/$."""
    s = str(s).strip().replace(",", "").replace("$", "").rstrip(".")
    try:
        f = float(s)
    except ValueError:
        return s
    return str(int(f)) if f == int(f) else str(f)


def extract_final_number(text):
    """Prediction extraction: prefer '#### N', else the LAST number."""
    m = _GSM_GOLD.search(text)
    if m:
        return normalize_number(m.group(1))
    nums = re.findall(r"-?\d[\d,]*\.?\d*", text)
    return normalize_number(nums[-1]) if nums else ""


def _gsm_norm(row, idx):
    q = _need(row, "question", "gsm8k")
    ans = _need(row, "answer", "gsm8k")
    m = _GSM_GOLD.search(ans)
    if not m:
        raise SystemExit("%s: gsm8k row %s has no '#### N' gold" % (ERR_SCHEMA, idx))
    sol = _GSM_CALC.sub("", ans).strip()
    return {"id": "gsm8k-%s" % idx, "context": "Question: %s\nAnswer:" % q,
            "gold_answer": normalize_number(m.group(1)), "gold_solution": sol}


# ---------------------------------------------------------------------------
# Few-shot rendering (shared frames; identical for every model/variant so
# weight-transform comparisons are like-for-like by construction).
# ---------------------------------------------------------------------------
def render_shot(bench, item):
    if bench == "gsm8k":
        return "%s %s" % (item["context"], item["gold_solution"])
    return "%s %s" % (item["context"], item["options"][item["gold"]])


def build_fewshot_prefix(bench, pool, shots, seed, det_u):
    """Deterministic k-shot prefix: pool ranked by det_u (f2bt det_u
    convention — sha256, no RNG state), first `shots` taken. Few-shot pool is
    the TRAIN split, eval is validation/test: disjoint by construction."""
    if shots <= 0:
        return ""
    ranked = sorted(pool, key=lambda it: det_u("fewshot", bench, seed, it["id"]))
    return "\n\n".join(render_shot(bench, it) for it in ranked[:shots]) + "\n\n"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
class Benchmark:
    def __init__(self, name, kind, norm):
        self.name = name
        self.kind = kind  # "mc" | "gen"
        self._norm = norm

    def load(self, data_dir, which="eval"):
        rows = _load_jsonl(os.path.join(data_dir, DATA_FILES[self.name][which]))
        return [self._norm(r, i) for i, r in enumerate(rows)]

    def mock_items(self, which="eval"):
        return [self._norm(r, i) for i, r in
                enumerate(MOCK_FIXTURES[self.name][which])]


BENCHMARKS = {
    "folio": Benchmark("folio", "mc", _folio_norm),
    "arc_easy": Benchmark("arc_easy", "mc",
                          lambda r, i: _arc_norm(r, i, "arc_easy")),
    "arc_challenge": Benchmark("arc_challenge", "mc",
                               lambda r, i: _arc_norm(r, i, "arc_challenge")),
    "gsm8k": Benchmark("gsm8k", "gen", _gsm_norm),
}

DEFAULT_BENCHMARKS = "folio,arc_easy,arc_challenge,gsm8k"


# ---------------------------------------------------------------------------
# MOCK fixtures — SYNTHETIC, mechanics-only. Shapes mirror the released raw
# schemas exactly so the SAME normalisers run in mock and real paths.
# ---------------------------------------------------------------------------
def _mk_folio(i, label):
    return {"example_id": "m%d" % i,
            "premises": "All blints are cromed.\nTuk is a blint.",
            "conclusion": "Tuk is cromed. (variant %d)" % i, "label": label}


def _mk_arc(i):
    return {"id": "m%d" % i,
            "question": "Which mock option is correct in case %d?" % i,
            "choices": {"text": ["alpha", "beta", "gamma", "delta"],
                        "label": ["A", "B", "C", "D"]},
            "answerKey": "ABCD"[i % 4]}


def _mk_gsm(i):
    a, b = 3 + i, 4 + i
    return {"question": "Mock case %d: Pat has %d pens and buys %d more. "
                        "How many pens now?" % (i, a, b),
            "answer": "Pat has %d+%d=<<%d+%d=%d>>%d pens.\n#### %d"
                      % (a, b, a, b, a + b, a + b, a + b)}


MOCK_FIXTURES = {
    "folio": {
        "eval": [_mk_folio(i, ["True", "False", "Uncertain"][i % 3])
                 for i in range(8)],
        "fewshot": [_mk_folio(100 + i, ["True", "False", "Uncertain"][i % 3])
                    for i in range(5)],
    },
    "arc_easy": {"eval": [_mk_arc(i) for i in range(8)],
                 "fewshot": [_mk_arc(100 + i) for i in range(5)]},
    "arc_challenge": {"eval": [_mk_arc(i) for i in range(8)],
                      "fewshot": [_mk_arc(100 + i) for i in range(5)]},
    "gsm8k": {"eval": [_mk_gsm(i) for i in range(8)],
              "fewshot": [_mk_gsm(100 + i) for i in range(5)]},
}
