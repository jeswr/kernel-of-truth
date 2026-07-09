#!/usr/bin/env python3
"""Re-render the judge-1 package after the §4.7 pre-data clarification (correction 1,
registry/corrections/f2b-transfer/1-prefreeze-correction.json; refrozen record
b341a0901e12023d3c56bdc196be0b9c492c7d348f988416d7e9c43aade20879).

Produces two files into poc/f2b-transfer/judge-1-package/:
  * PROTOCOL.md            — verbatim copy of the NEW design.md §4 (now incl. §4.7),
                             with a wrapper header noting the new prereg_doc sha.
  * judge-1-adjudication.csv — the SINGLE self-contained answer file: Fable's exact
                             13-line INSTRUCTIONS block (§A of judge-instructions-
                             wording.md) as a preamble, then a header
                             position,question,allowed_answers,your_answer,comment
                             and 360 item rows (question+options inline, answer/comment
                             blank), keyed by position.

The INSTRUCTIONS text is SOURCED (not transcribed) from judge-instructions-wording.md
§A so it is byte-identical to Fable's authored replacement. The §4 body is SOURCED from
design.md so PROTOCOL.md is a byte-exact copy. Item text/positions/options/allowed
tokens are copied byte-for-byte from the frozen items — nothing adjudicated changes.
Deterministic (stdlib only; sorted by position).

README.md (§B deltas) and items-judge-1.md (§D preamble delta) are surgical single-
target edits applied outside this script (they preserve every untouched byte, in
particular items-judge-1.md item sections 1-360); see run-log.md.
"""
import json, csv, hashlib, pathlib, re, sys

ROOT = pathlib.Path(".").resolve()
PKG = ROOT / "poc/f2b-transfer/judge-1-package"
DESIGN = ROOT / "poc/f2b-transfer/design.md"
WORDING = ROOT / "poc/f2b-transfer/judge-instructions-wording.md"

EXPECT_DESIGN_SHA = "4d0f7a70f3ecce6aa55665bd74f74e6ca24994b4e4e7ff795c70564a55ab9d0f"
EXPECT_ITEMS_SHA = "57070307f85a0137157143c2b3706ebb2b88e2cfd00706f8f4946c773487add5"
NEW_PREREG_SHA = EXPECT_DESIGN_SHA  # prereg_doc.sha256 of the refrozen record


def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---- 0. fail-closed pin checks -------------------------------------------------
got = sha256_file(DESIGN)
assert got == EXPECT_DESIGN_SHA, "design.md sha %s != expected %s" % (got, EXPECT_DESIGN_SHA)
items_sha = sha256_file(PKG / "items-judge-1.jsonl")
assert items_sha == EXPECT_ITEMS_SHA, "items-judge-1.jsonl sha %s != expected %s (corpus MUST be byte-identical)" % (items_sha, EXPECT_ITEMS_SHA)

# ---- 1. Fable's exact 13-line INSTRUCTIONS block, sourced from §A ---------------
wtext = WORDING.read_text(encoding="utf-8").splitlines()
a_idx = next(i for i, l in enumerate(wtext) if l.startswith("## A."))
b_idx = next(i for i, l in enumerate(wtext) if l.startswith("## B."))
num_re = re.compile(r"^(\d+)\.\s(.*)$")
INSTRUCTIONS = []
for l in wtext[a_idx + 1:b_idx]:
    m = num_re.match(l)
    if m:
        INSTRUCTIONS.append((int(m.group(1)), m.group(2)))
assert [n for n, _ in INSTRUCTIONS] == list(range(1, 14)), \
    "expected numbered lines 1..13 in §A, got %s" % [n for n, _ in INSTRUCTIONS]
INSTRUCTIONS = [t for _, t in INSTRUCTIONS]
# the superseded 'close but not quite -> NONE' line must be gone
assert not any("close but not quite right" in s for s in INSTRUCTIONS), \
    "superseded 'close but not quite right' line must not appear"
assert any("EXTRA TRUE DETAILS ARE FINE" in s for s in INSTRUCTIONS)

# ---- 2. verbatim §4 slice (now incl. §4.7) from design.md ----------------------
dlines = DESIGN.read_text(encoding="utf-8").split("\n")
i4 = next(i for i, l in enumerate(dlines) if l.startswith("## 4. Adjudication protocol"))
i5 = next(i for i, l in enumerate(dlines) if l.startswith("## 5. Arms"))
sec4 = dlines[i4:i5]
while sec4 and sec4[-1].strip() == "":
    sec4.pop()
sec4_body = "\n".join(sec4) + "\n"
assert "S1 — MCQ correctness" in sec4_body and "S7 — item independence" in sec4_body, \
    "§4.7 S1..S7 must be present in the §4 slice"
assert "A-direction disclosure" in sec4_body

protocol = (
    "# f2b-transfer adjudication protocol (§4) — VERBATIM, FROZEN\n"
    "\n"
    "> Verbatim copy of section 4 of `poc/f2b-transfer/design.md`\n"
    "> (frozen prereg_doc, sha256 %s).\n"
    "> This copy is authoritative for judge-1's task; the wrapper lines above\n"
    "> this rule are not part of §4.\n"
    "\n"
    "---\n"
    "\n"
    "%s" % (NEW_PREREG_SHA, sec4_body)
)
(PKG / "PROTOCOL.md").write_text(protocol, encoding="utf-8")
# assert the §4 body inside PROTOCOL.md is byte-identical to the design.md slice
assert (PKG / "PROTOCOL.md").read_text(encoding="utf-8").endswith(sec4_body)

# ---- 3. the single self-contained judge-1-adjudication.csv ---------------------
items = [json.loads(l) for l in (PKG / "items-judge-1.jsonl").open() if l.strip()]
items.sort(key=lambda d: d["position"])
assert [d["position"] for d in items] == list(range(1, len(items) + 1)), "positions must be 1..N contiguous"


def render_item(d):
    q = d["question"].strip()
    if d.get("format") == "mcq":
        lines = [q, ""]
        for opt in d["options"]:
            lines.append("%s) %s" % (opt["key"], opt["text"].strip()))
        lines.append("NONE) none of these / cannot say")
        return "\n".join(lines)
    return q  # claim yes/no: question already self-contained


def allowed(d):
    a = d["allowed"]
    if d.get("format") == "mcq":
        return "A, B, C, D, or NONE"
    return ", ".join(a[:-1]) + ", or " + a[-1] if len(a) > 1 else a[0]


out = PKG / "judge-1-adjudication.csv"
with out.open("w", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    w.writerow(["INSTRUCTIONS — please read every line before you start", "", "", ""])
    for i, line in enumerate(INSTRUCTIONS, 1):
        w.writerow(["%d. %s" % (i, line), "", "", ""])
    w.writerow(["", "", "", ""])
    w.writerow(["(the 360 items to answer are below — fill 'your_answer' for every position)", "", "", ""])
    w.writerow(["", "", "", ""])
    w.writerow(["position", "question", "allowed_answers", "your_answer", "comment"])
    for d in items:
        w.writerow([d["position"], render_item(d), allowed(d), "", ""])

# ---- 4. verify: re-read, count item rows, positions 1..N, answers blank ---------
rows = list(csv.reader(out.open(newline="")))
data = [r for r in rows if r and r[0].isdigit()]
positions = [int(r[0]) for r in data]
assert positions == list(range(1, len(items) + 1)), "position keying broke"
assert all(r[3] == "" and r[4] == "" for r in data), "answer/comment must start blank"

print("OK PROTOCOL.md sha256   =", sha256_file(PKG / "PROTOCOL.md"))
print("OK judge-1-adjudication.csv sha256 =", sha256_file(out))
print("OK csv item rows=%d positions 1..%d, %d MCQ / %d claim, answers+comments blank" % (
    len(data), len(items),
    sum(1 for d in items if d.get("format") == "mcq"),
    sum(1 for d in items if d.get("format") != "mcq")))
print("OK items-judge-1.jsonl byte-identical, sha256 =", items_sha)
print("OK §4 slice incl §4.7 (S1..S7 + A-direction disclosure)")
