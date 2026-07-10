#!/usr/bin/env python3
"""build-deranged-probe — the judge-level content-scramble control for
g9-llmproxy (registry/experiments/g9-llmproxy.json; design note
poc/g9-llmproxy/design.md S4).

WHAT THIS BUILDS. 50 probe items in which sheet i's word / dictionary def /
examples / ambiguous examples are paired with sheet sigma(i)'s proposed
paraphrase, sigma a seed-pinned Sattolo cycle over the 50 review sheets (the
house shuffled-kernel idiom at the judge level; no sheet keeps its own
paraphrase). The correct Q-SUB answer is 'no' by construction (50 distinct
DeepNSM test-split words; near-synonym collision risk disclosed as
negligible-but-nonzero) [STIPULATED: ASM-0523]. Probe Q-XT is REPORTED-ONLY:
cross-translatability is text-intrinsic, so the probe cannot control it — the
Q-XT leg has NO content-scramble control by construction (disclosed binding
weakening, ASM-0523). Probe items NEVER enter labels or the composite rate;
they feed only the pre-registered /gates/probe_valid instrument gate
(Q-SUB false-endorsement point-rate >= 0.30, or probe coverage < 45/50 =>
INSTRUMENT-INVALID).

ALSO EMITTED (single manifest, so the runner's pipeline is fully mechanical):
the seed-pinned real-item order (g9lp/1|judge-r1p|20260710), the probe run
order (g9lp/1|probe-order|20260710), and the 10 retest sheet ids
(g9lp/1|retest|20260710, first 10) in their ask order.

DETERMINISM. Single-draw: one build from the seeds below, committed and
sha-pinned in the DRAFT record before freeze. Re-running reproduces the same
bytes; any seed change is a design change. Fail-closed: refuses to run if the
blinded sheets file does not match the record's pinned sha (ERR_G9P_REFPIN).

Seeds (pre-committed verbatim; design S3/S4 + record n_planned):
  real order  g9lp/1|judge-r1p|20260710
  derangement g9lp/1|probe|20260710
  probe order g9lp/1|probe-order|20260710
  retest      g9lp/1|retest|20260710
"""
import hashlib
import json
import os
import random
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SHEETS = os.path.join(REPO, "data", "authored-explication-set", "review",
                      "sheets.json")
# the record's pinned sha (registry/experiments/g9-llmproxy.json artifact_hashes)
SHEETS_PIN = "55082b1588c1c4f55b15fd07c6fbbc1b941d8fcb948de94e69b3f0e1d05b8c7c"
SEED_REAL = "g9lp/1|judge-r1p|20260710"
SEED_DERANGE = "g9lp/1|probe|20260710"
SEED_PROBE_ORDER = "g9lp/1|probe-order|20260710"
SEED_RETEST = "g9lp/1|retest|20260710"
N = 50
N_RETEST = 10
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PROBE = os.path.join(OUT_DIR, "deranged-probe.jsonl")
OUT_MANIFEST = os.path.join(OUT_DIR, "deranged-probe-manifest.json")


def hsort_key(seed, s):
    return hashlib.sha256((seed + "|" + s).encode("utf-8")).hexdigest()


def jdump(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def main():
    with open(SHEETS, "rb") as f:
        raw = f.read()
    got = hashlib.sha256(raw).hexdigest()
    if got != SHEETS_PIN:
        print("ERR_G9P_REFPIN: sheets.json sha %s != pinned %s"
              % (got, SHEETS_PIN), file=sys.stderr)
        sys.exit(1)
    sheets = json.loads(raw.decode("utf-8"))["sheets"]
    if len(sheets) != N:
        print("ERR_G9P_SOURCE: expected %d sheets, got %d" % (N, len(sheets)),
              file=sys.stderr)
        sys.exit(1)
    sheets.sort(key=lambda s: s["sheet_id"])  # ascending sheet_id, indices 0..49

    def item_id(sheet):
        return "g9s:%02d" % sheet["sheet_id"]

    def probe_id(sheet):
        return "g9p:%02d" % sheet["sheet_id"]

    # --- derangement: Sattolo cycle over the 50 in sheet_id order ------------
    rng = random.Random(int.from_bytes(
        hashlib.sha256(SEED_DERANGE.encode("utf-8")).digest(), "big"))
    perm = list(range(N))
    for i in range(N - 1, 0, -1):       # Sattolo: j strictly below i =>
        j = rng.randrange(i)            # single cycle, zero fixed points
        perm[i], perm[j] = perm[j], perm[i]

    probe_rows, man_rows = [], []
    for i, src in enumerate(sheets):
        donor_idx, steps = perm[i], 0
        # collision rule (deterministic): advance along the cycle while the
        # donor is the sheet itself or its paraphrase text is byte-equal to
        # the sheet's own (cannot occur across 50 distinct authored texts;
        # kept for fail-closed completeness)
        while (donor_idx == i or sheets[donor_idx]["candidate_explication"]
               == src["candidate_explication"]):
            donor_idx = perm[donor_idx]
            steps += 1
            if steps > N:
                print("ERR_G9P_CYCLE: no valid donor for sheet %d"
                      % src["sheet_id"], file=sys.stderr)
                sys.exit(1)
        donor = sheets[donor_idx]
        probe_rows.append({
            "ambig_examples": src["ambig_examples"],
            "candidate_explication": donor["candidate_explication"],
            "def": src["def"], "examples": src["examples"],
            "id": probe_id(src), "word": src["word"]})
        man_rows.append({"collision_steps": steps,
                         "donor_sheet_id": donor["sheet_id"],
                         "probe_id": probe_id(src),
                         "source_sheet_id": src["sheet_id"]})

    # --- pinned orders (judge is stateless; recorded for provenance) ---------
    real_order = sorted((item_id(s) for s in sheets),
                        key=lambda x: hsort_key(SEED_REAL, x))
    probe_order = sorted((r["id"] for r in probe_rows),
                         key=lambda x: hsort_key(SEED_PROBE_ORDER, x))
    pos = {pid: p + 1 for p, pid in enumerate(probe_order)}
    for m in man_rows:
        m["run_position"] = pos[m["probe_id"]]
    retest_ids = sorted((item_id(s) for s in sheets),
                        key=lambda x: hsort_key(SEED_RETEST, x))[:N_RETEST]

    probe_rows.sort(key=lambda r: r["id"])
    man_rows.sort(key=lambda m: m["probe_id"])
    with open(OUT_PROBE, "w", encoding="utf-8") as f:
        for r in probe_rows:
            f.write(jdump(r) + "\n")
    manifest = {"builder": "poc/g9-llmproxy/build-deranged-probe.py",
                "correct_answer_by_construction": {"substitutable": "no"},
                "n_probe": N, "n_retest": N_RETEST,
                "probe_order": probe_order,
                "probe_xt_note": "Q-XT on probes is REPORTED-ONLY: "
                                 "cross-translatability is text-intrinsic, so "
                                 "the content scramble cannot control it "
                                 "(ASM-0523 disclosed weakening)",
                "real_order": real_order,
                "residual_note": "a deranged-in paraphrase may, rarely, "
                                 "genuinely substitute for the asked word "
                                 "(near-synonym residual, disclosed "
                                 "negligible-but-nonzero; ASM-0523); the 0.30 "
                                 "gate bar sits far above that floor",
                "retest_ids": retest_ids,
                "rows": man_rows, "schema": "g9lp-probe/1",
                "seed_derange": SEED_DERANGE,
                "seed_probe_order": SEED_PROBE_ORDER,
                "seed_real_order": SEED_REAL, "seed_retest": SEED_RETEST,
                "sheets_pin": SHEETS_PIN}
    with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
        f.write(jdump(manifest) + "\n")
    for p in (OUT_PROBE, OUT_MANIFEST):
        with open(p, "rb") as f:
            print("%s  %s" % (hashlib.sha256(f.read()).hexdigest(),
                              os.path.relpath(p, REPO)))
    ncol = sum(1 for m in man_rows if m["collision_steps"])
    print("built %d probe rows (%d collision-advanced), %d retest ids"
          % (len(probe_rows), ncol, len(retest_ids)))


if __name__ == "__main__":
    main()
