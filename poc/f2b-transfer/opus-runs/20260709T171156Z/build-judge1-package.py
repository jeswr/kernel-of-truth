#!/usr/bin/env python3
"""build-judge1-package — assemble the BLIND judge-1 HUMAN adjudication package
for f2b-transfer stage-1 (design poc/f2b-transfer/design.md §4, frozen as
registry/experiments/f2b-transfer.json prereg_doc; task: Opus experiment-runner
stage-1 adjudication PREP).

WHAT THIS IS (and is NOT):
  - This is OPERATIONAL packaging of a FABLE-FROZEN protocol. It renders the 360
    d-qa-t items BLIND per §4.2 (question + kernel-rendered option texts ONLY;
    every provenance/membership/type field stripped), offers the §4.3 mandatory
    escape, presents judge-1's items in judge-1's pinned-seed order, and copies
    §4 verbatim as PROTOCOL.md. It DESIGNS NOTHING and CONCLUDES NOTHING.
  - It does NOT fabricate any judge-1 response (the human fills the template).
  - It does NOT touch judge-2 (the §4 LLM-judge prompt + codex invocation shape
    are NOT determined by the frozen protocol; that is Fable-needed, queued).

DETERMINISM: stdlib only; no wall-clock, no os.urandom, no Python hash(). Every
ordering choice is sha256 over the pinned judge seed + item id. Re-running
produces byte-identical outputs.

SHUFFLE CONSTRUCTION (flagged determinism choice): design §4.2 pins the per-judge
permutation SEED ("dadjt/1|judge-1|20260710") but does not write the permutation
ALGORITHM verbatim. This script uses the repo's CANONICAL seeded-sort idiom — the
identical construction data/d-qa-t/build-dqat.py uses for its pinned rank order
(sort by sha256(seed | key)). Presentation order is SCIENCE-NEUTRAL: the frozen
endorsement statistic A and the judge-pair agreement are computed per item id
(analysis/f2b_transfer.py reads only the order-independent summary record), and
the full position->id map is written to provenance so labels re-key regardless of
the permutation used. If Fable pins a different construction, re-order is trivial.

BLINDING (RT-14): only the pseudonym "judge-1" appears; NO names/emails/accounts.
The position->id map (which would de-anonymise the concept + item type) is written
to the OPUS-RUN provenance dir, NEVER into the human package.

Usage:  python3 poc/f2b-transfer/opus-runs/<TS>/build-judge1-package.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
ITEMS_PATH = os.path.join(ROOT, "data", "d-qa-t", "items", "covered.jsonl")
DESIGN_PATH = os.path.join(ROOT, "poc", "f2b-transfer", "design.md")
PKG_DIR = os.path.join(ROOT, "poc", "f2b-transfer", "judge-1-package")

JUDGE = "judge-1"
JUDGE_SEED = "dadjt/1|judge-1|20260710"          # design §4.2, pinned verbatim
EXPECT_N = 360                                    # frozen n_generated
# frozen pins (fail-closed cross-checks; values from registry/experiments/f2b-transfer.json)
EXPECT_DESIGN_SHA = "c4942eaf6c9914eb1392956a77c3ab24d1890678e869ea7cbe3f4e7b5db96c79"


def die(msg):
    sys.stderr.write("BUILD_JUDGE1_ERR: %s\n" % msg)
    sys.exit(1)


def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return sha256_hex(f.read())


def load_items():
    items = [json.loads(l) for l in open(ITEMS_PATH, encoding="utf-8") if l.strip()]
    if len(items) != EXPECT_N:
        die("expected %d items, got %d" % (EXPECT_N, len(items)))
    for it in items:
        if it["options"] is None:
            # claim item: yes/no question, no MCQ options
            if not it["question"].strip():
                die("empty claim question %s" % it["id"])
        else:
            keys = [o["key"] for o in it["options"]]
            if keys != ["A", "B", "C", "D"]:
                die("MCQ %s has non-ABCD keys %r" % (it["id"], keys))
    return items


def judge_order(items):
    """Canonical seeded sort (see module docstring). Stable, deterministic."""
    return sorted(items, key=lambda it: sha256_hex(("%s|%s" % (JUDGE_SEED, it["id"])).encode("utf-8")))


def blind_render(it):
    """BLIND rendering per §4.2: question text + (MCQ) option texts ONLY.
    Every other field (id, label, urn, record_path, record_sha256, gloss_doc_id,
    type, answer, claim, claim_source, source, slice, kernel_checkable, rank) is
    dropped. §4.3 escape sets are attached as `allowed`."""
    if it["options"] is None:
        return {"format": "claim-yes-no",
                "question": it["question"],
                "options": None,
                "allowed": ["yes", "no", "cannot say"]}   # §4.3 claim escape
    return {"format": "mcq",
            "question": it["question"],
            "options": [{"key": o["key"], "text": o["text"]} for o in it["options"]],
            "allowed": ["A", "B", "C", "D", "NONE"]}       # §4.3 MCQ escape ("NONE of these / cannot say")


def extract_section4(design_text):
    """Slice §4 verbatim: from the '## 4.' header up to (not incl.) '## 5.'."""
    lines = design_text.splitlines(keepends=True)
    start = end = None
    for i, ln in enumerate(lines):
        if ln.startswith("## 4. Adjudication protocol"):
            start = i
        elif start is not None and ln.startswith("## 5."):
            end = i
            break
    if start is None or end is None:
        die("could not locate §4 boundaries in design.md")
    return "".join(lines[start:end]).rstrip() + "\n"


# --------------------------------------------------------------------------- write

def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return file_sha(path)


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    return file_sha(path)


def render_items_md(ordered_blind):
    out = []
    out.append("# f2b-transfer stage-1 — items for judge-1 (BLIND)\n")
    out.append("\n")
    out.append("Answer every item from your OWN everyday understanding of the "
               "words involved. For each item, record your answer against its "
               "**position number** in `response-template.csv`.\n")
    out.append("\n")
    out.append("- **Multiple-choice items** (\"Which option gives the meaning\" / "
               "\"a word whose definition is\"): choose the single letter "
               "**A / B / C / D**, or write **NONE** if none of the four is a "
               "correct fit or you cannot say.\n")
    out.append("- **Yes/no items** (\"...is the following true of X?\"): answer "
               "**yes**, **no**, or **cannot say**.\n")
    out.append("- \"NONE\" / \"cannot say\" is a valid, expected answer — use it "
               "whenever the options do not fit or you genuinely cannot tell. It "
               "is not a mistake.\n")
    out.append("\n---\n\n")
    for pos, b in enumerate(ordered_blind, start=1):
        out.append("## %d\n\n" % pos)
        out.append("%s\n\n" % b["question"])
        if b["format"] == "mcq":
            for o in b["options"]:
                out.append("- **%s)** %s\n" % (o["key"], o["text"]))
            out.append("- **NONE)** none of these / cannot say\n")
            out.append("\n_Answer (A / B / C / D / NONE):_ ______\n\n")
        else:
            out.append("_Answer (yes / no / cannot say):_ ______\n\n")
        out.append("---\n\n")
    return "".join(out)


def render_template_csv(n):
    rows = ["position,answer,optional_note"]
    for pos in range(1, n + 1):
        rows.append("%d,," % pos)
    return "\n".join(rows) + "\n"


def render_readme(n, order_map_note):
    return (
"""# judge-1 adjudication package (f2b-transfer, stage 1) — BLIND

You are **judge-1**. Please record NOTHING that identifies you anywhere in this
package (use only the label "judge-1"). Do not write your name or email.

## Eligibility (required)

You may serve as judge-1 ONLY if you have **never read any of the project's
concept/"kernel" records**. This task measures whether ordinary understanding of
everyday concepts agrees with those records; having seen them would invalidate
your labels. If you have seen them, stop and hand this to someone who has not.

## Your task

`items-judge-1.md` contains **%d numbered items** about everyday concepts
(things like *bird, eat, sleep, water, jump, forget*). Each item is either:

- a **multiple-choice** question — "Which option gives the meaning of the word
  X?" or "A word whose definition is: ...  Which word is it?" — with options
  written in a deliberately plain, simplified style; or
- a **yes/no** question — "According to the definition of X, is the following
  true of X? ...".

Answer **each item from your own competence** with the everyday concepts — pick
the option that genuinely best gives the meaning, or genuinely answer the yes/no
question. You are NOT trying to guess an intended answer; there is no trick.

## The mandatory escape ("cannot say")

Every item offers an escape, and using it is a normal, expected outcome:

- multiple-choice: answer **NONE** if none of A–D correctly gives the meaning,
  or if you cannot decide;
- yes/no: answer **cannot say** if you cannot judge the statement.

Do not force a choice. If the options do not describe the concept as you
understand it, "NONE" / "cannot say" is the correct answer.

## How to record your answers

Fill in `response-template.csv` — one row per item, keyed by the **position
number** shown in `items-judge-1.md`:

- multiple-choice → write `A`, `B`, `C`, `D`, or `NONE` in the `answer` column;
- yes/no → write `yes`, `no`, or `cannot say`.

`optional_note` is free-text and optional. Please answer every position.

## Practical guidance

- Roughly 20 seconds per item (~2 hours total); one sitting if you can.
- Work top to bottom; please don't go back and "correct" earlier answers to fit
  a pattern you think you see — first-read judgement is what we want.
- Do not look anything up about the project or any "kernel".

## Authoritative rules

`PROTOCOL.md` is a **verbatim copy of the frozen adjudication protocol (§4)**;
it is the authority if anything here is unclear.

## Note on item order

%s
""" % (n, order_map_note))


def main():
    # fail-closed pin cross-check on the frozen design doc
    got = file_sha(DESIGN_PATH)
    if got != EXPECT_DESIGN_SHA:
        die("design.md sha %s != frozen prereg_doc.sha256 %s" % (got, EXPECT_DESIGN_SHA))

    items = load_items()
    ordered = judge_order(items)
    ordered_blind = [blind_render(it) for it in ordered]

    os.makedirs(PKG_DIR, exist_ok=True)

    # ---- human package (BLIND; no ids, no provenance) ----
    design_text = open(DESIGN_PATH, encoding="utf-8").read()
    section4 = extract_section4(design_text)
    protocol_md = (
        "# f2b-transfer adjudication protocol (§4) — VERBATIM, FROZEN\n\n"
        "> Verbatim copy of section 4 of `poc/f2b-transfer/design.md`\n"
        "> (frozen prereg_doc, sha256 c4942eaf6c9914eb1392956a77c3ab24d1890678e869ea7cbe3f4e7b5db96c79).\n"
        "> This copy is authoritative for judge-1's task; the wrapper lines above\n"
        "> this rule are not part of §4.\n\n"
        "---\n\n" + section4)
    order_note = (
        "Items are presented in judge-1's pinned-seed order (seed "
        "`dadjt/1|judge-1|20260710`, §4.2). The order carries no information "
        "about the answers; just work through the positions in sequence.")

    shas = {}
    shas["judge-1-package/PROTOCOL.md"] = write_text(os.path.join(PKG_DIR, "PROTOCOL.md"), protocol_md)
    shas["judge-1-package/items-judge-1.md"] = write_text(
        os.path.join(PKG_DIR, "items-judge-1.md"), render_items_md(ordered_blind))
    shas["judge-1-package/response-template.csv"] = write_text(
        os.path.join(PKG_DIR, "response-template.csv"), render_template_csv(len(ordered)))
    shas["judge-1-package/README.md"] = write_text(
        os.path.join(PKG_DIR, "README.md"), render_readme(len(ordered), order_note))
    # blind machine-readable items for judge-1 (position-keyed; still no id/provenance)
    blind_rows = [dict(position=pos, **b) for pos, b in enumerate(ordered_blind, start=1)]
    shas["judge-1-package/items-judge-1.jsonl"] = write_jsonl(
        os.path.join(PKG_DIR, "items-judge-1.jsonl"), blind_rows)

    # ---- provenance (NOT in the human package) ----
    # private re-keying map: position -> dqat id (+ frozen rank), for re-keying
    # judge-1's returned labels back to item ids. Contains ids => provenance only.
    map_rows = [{"position": pos, "id": it["id"], "rank": it["rank"]}
                for pos, it in enumerate(ordered, start=1)]
    shas["opus-run/judge-1-position-map.jsonl"] = write_jsonl(
        os.path.join(HERE, "judge-1-position-map.jsonl"), map_rows)
    # order-neutral canonical BLIND rendering keyed by id (helper for whoever
    # later assembles judge-2 under a Fable-frozen prompt; strips the same fields).
    byid = [dict(id=it["id"], **blind_render(it)) for it in items]
    byid.sort(key=lambda r: r["id"])
    shas["opus-run/blind-items-by-id.jsonl"] = write_jsonl(
        os.path.join(HERE, "blind-items-by-id.jsonl"), byid)

    # ---- report ----
    n_mcq = sum(1 for b in ordered_blind if b["format"] == "mcq")
    n_claim = len(ordered_blind) - n_mcq
    print(json.dumps({
        "judge": JUDGE,
        "judge_seed": JUDGE_SEED,
        "n_items": len(ordered),
        "n_mcq": n_mcq,
        "n_claim_yes_no": n_claim,
        "design_sha256_verified": got,
        "artifact_sha256": shas,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
