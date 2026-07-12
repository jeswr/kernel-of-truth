#!/usr/bin/env python3
"""One-shot coordinator registration of the 2026-07-12 design wave's
PROPOSED-ASM blocks into registry/assumptions.jsonl.

Sources (all emitted-for-central-registration blocks, verbatim claims):
  - docs/next/feasibility-synthesis-v5.md            ASM-1380..1385
  - poc/rules-1-knull/RESULT.md                      ASM-1400..1419
  - docs/next/design/rules-2-train-time.md App. A    ASM-1420..1439
  - poc/rules-2/asm-1440-1459.json                   ASM-1440..1459
  - docs/next/interpretations/g2-import.md           ASM-1460..1462

Normalisations applied (coordinator registration duties, not content edits):
  - strip the PROPOSED- prefix from ids
  - owner pseudonyms mapped onto the RT-14 roster (synthesis-agent -> writer-1,
    fable-build-1 -> designer-1)
  - every EXTRAPOLATION row gets load_bearing:false and a resolution_path
  - g2-import rows converted from the emitting doc's {class,text} shorthand to
    the register schema, with backing_ref/rationale/owner/status/date added
  - validation replayed with claims-check rules + RT-14 account lint before append
"""
import json, re, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "registry", "assumptions.jsonl")

OWNER_MAP = {"synthesis-agent": "writer-1", "fable-build-1": "designer-1",
             # RT-14 roster has no 'reviewer' role; the independent-review
             # pseudonym maps onto the skeptic role (same independence duty).
             "reviewer-1": "skeptic-1"}

RES_PATHS = {
    "ASM-1434": ("measure the actual per-arm GPU-hours, USD and wall-clock in the registered "
                 "RULES-2 run's provenance logs (run-log + Modal provenance JSON) and compare to "
                 "these bands in the analyst readout; kill nothing on mismatch — re-tag this row "
                 "resolved with the measured values"),
    "ASM-1454": ("replace the dry-plan estimates with the measured GPU-hours/USD/wall-clock from "
                 "the registered RULES-2 run's provenance logs and re-tag this row resolved with "
                 "the measured values; the binding caps themselves are enforced fail-closed by the "
                 "$0 dry-plan gate, so no verdict ever rests on the estimate"),
}

KEY_ORDER = ["id", "tag", "claim", "backing_ref", "load_bearing", "status",
             "owner", "date", "rationale", "resolution_path", "notes"]


def fenced_json_blocks(path):
    text = open(path, encoding="utf-8").read()
    return [json.loads(m) for m in re.findall(r"```json\n(.*?)\n```", text, re.DOTALL)]


def norm(row):
    row = dict(row)
    row["id"] = row["id"].replace("PROPOSED-", "")
    row["owner"] = OWNER_MAP.get(row.get("owner"), row.get("owner"))
    if row["tag"] == "EXTRAPOLATION":
        row["load_bearing"] = False
        if not (row.get("resolution_path") or "").strip():
            row["resolution_path"] = RES_PATHS[row["id"]]
    return {k: row[k] for k in KEY_ORDER if k in row} | {
        k: v for k, v in row.items() if k not in KEY_ORDER}


rows = []

# --- feasibility-synthesis-v5: ASM-1380..1385 ------------------------------
(fs5,) = fenced_json_blocks(os.path.join(ROOT, "docs/next/feasibility-synthesis-v5.md"))
assert [r["id"] for r in fs5] == ["PROPOSED-ASM-138%d" % i for i in range(6)]
rows += [norm(r) for r in fs5]

# --- rules-1-knull: ASM-1400..1419 -----------------------------------------
(rk,) = fenced_json_blocks(os.path.join(ROOT, "poc/rules-1-knull/RESULT.md"))
assert [r["id"] for r in rk] == ["PROPOSED-ASM-14%02d" % i for i in range(20)]
rows += [norm(r) for r in rk]

# --- rules-2 design doc: ASM-1420..1439 ------------------------------------
(r2,) = fenced_json_blocks(os.path.join(ROOT, "docs/next/design/rules-2-train-time.md"))
assert [r["id"] for r in r2] == ["PROPOSED-ASM-14%d" % i for i in range(20, 40)]
rows += [norm(r) for r in r2]

# --- rules-2 build block: ASM-1440..1459 -----------------------------------
r2b = json.load(open(os.path.join(ROOT, "poc/rules-2/asm-1440-1459.json")))["rows"]
assert [r["id"] for r in r2b] == ["PROPOSED-ASM-14%d" % i for i in range(40, 60)]
rows += [norm(r) for r in r2b]

# --- g2-import interpretation: ASM-1460..1462 ------------------------------
g2_backing = {
    "PROPOSED-ASM-1460": ("results-log/g2-import.jsonl; poc/ontology-import-g2/analysis-output.json; "
                          "registry/experiments/g2-import.json (FROZEN)"),
    "PROPOSED-ASM-1461": ("docs/next/interpretations/g2-import.md section 1; "
                          "poc/ontology-import-g2/analysis-output.json"),
    "PROPOSED-ASM-1462": ("docs/next/interpretations/g2-import.md section 2; "
                          "poc/ontology-import-g2/analysis-output.json"),
}
g2_rationale = ("Pins the g2-import proxy readout numbers and the mechanical INSTRUMENT-INVALID "
                "no-conclusion status in the register so no later narration can upgrade a "
                "kappa-failed run into a PASS/GO.")
g2_text = open(os.path.join(ROOT, "docs/next/interpretations/g2-import.md"), encoding="utf-8").read()
g2_lines = re.findall(r"```json\n(.*?)\n```", g2_text, re.DOTALL)[0].splitlines()
for line in g2_lines:
    src = json.loads(line)
    row = {
        "id": src["id"], "tag": src["class"], "claim": src["text"],
        "backing_ref": g2_backing[src["id"]],
        "load_bearing": src["load_bearing"], "status": "open",
        "owner": "writer-1", "date": "2026-07-12",
    }
    if src["class"] == "STIPULATED":
        row["rationale"] = g2_rationale
    if "resolution_path" in src:
        row["resolution_path"] = src["resolution_path"]
    rows.append(norm(row))

# --- validate with the live lint rules, then append ------------------------
sys.argv = ["claims-check"]
cc = __import__("importlib").import_module("claims-check") if False else None
# replay check_entry from claims-check without invoking its CLI
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cchk", os.path.join(os.path.dirname(os.path.abspath(__file__)), "claims-check.py"))
cchk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cchk)

f = cchk.Findings()
existing = {json.loads(l)["id"] for l in open(REG, encoding="utf-8") if l.strip()}
out_lines = []
for row in rows:
    line = json.dumps(row, ensure_ascii=False)
    assert row["id"] not in existing, "duplicate id %s" % row["id"]
    kc.require_no_account_strings(line.encode("utf-8"), row["id"])
    cchk.check_entry(row, row["id"], f)
    out_lines.append(line)
if f.items:
    print("REFUSING to append: %d validation finding(s)" % len(f.items))
    sys.exit(1)

with open(REG, "a", encoding="utf-8") as fh:
    for line in out_lines:
        fh.write(line + "\n")
print("appended %d rows: %s .. %s" % (len(out_lines), rows[0]["id"], rows[-1]["id"]))
