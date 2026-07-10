#!/usr/bin/env python3
"""build-deranged-probe — the judge-level content-scramble control for
f2b-transfer-llmproxy (registry/experiments/f2b-transfer-llmproxy.json;
design note poc/f2b-transfer/llmproxy-design.md §5).

WHAT THIS BUILDS. 60 def-match MCQ probe items in which the item's own
membership-gold gloss text is DERANGED OUT (replaced by the gold gloss of a
different probe item via a seed-pinned Sattolo cycle — the house shuffled-
kernel idiom applied at the judge level). After the swap no option correctly
gives the meaning of the asked word, so a judge answering from CONCEPT
COMPETENCE must answer NONE. The probe measures the judge instrument's
false-endorsement propensity (style/familiarity-driven endorsement of
NSM-shaped text when the content is provably wrong) and verifies the escape
hatch actually fires — the exact channel that would fabricate a proxy-PASS
under H-CIRC. Probe items NEVER enter labels, A_1p, or any endorsement
statistic; they feed only the pre-registered /gates/probe_valid instrument
gate (false-endorsement point-rate >= 0.30 => INSTRUMENT-INVALID).

DETERMINISM. Single-draw: one build from the seeds below, committed and
sha-pinned in the DRAFT record before freeze. Re-running reproduces the same
bytes; any seed change is a design change (new record or pre-freeze
correction). Fail-closed: the builder refuses to run if the d-qa-t corpus
digest does not match the frozen f2b-transfer pin (ERR_PROBE_REFPIN) — the
probe must derive from exactly the adjudicated item bytes.

Seeds (pre-committed verbatim, llmproxy-design.md §5):
  selection   dqatprobe/1|f2b-transfer-llmproxy|select|20260711
  derangement dqatprobe/1|f2b-transfer-llmproxy|derange|20260711
  run order   dadjt/1|judge-1p-probe|20260711

Residual disclosed (design note §5): a swapped-in gloss may, rarely, genuinely
fit the asked word (near-synonym / shared-genus surface, the design.md §4.7
"rabbit <- tree" class, expected order ~1%); the 0.30 gate bar sits far above
that floor. Collisions (swapped text byte-equal to an option already present,
or to the item's own gold text) advance deterministically along the Sattolo
cycle and are recorded per item in the manifest.
"""
import hashlib
import json
import os
import random
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "registry"))
import kot_common as kc  # noqa: E402  (corpus_hash — the kot-corpus-hash/1 reference impl)

# the frozen f2b-transfer d-qa-t pin (registry/experiments/f2b-transfer.json)
DQAT_PIN = "7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27"
SEED_SELECT = "dqatprobe/1|f2b-transfer-llmproxy|select|20260711"
SEED_DERANGE = "dqatprobe/1|f2b-transfer-llmproxy|derange|20260711"
SEED_RUNORDER = "dadjt/1|judge-1p-probe|20260711"
N_PROBE = 60
ITEMS = os.path.join(REPO, "data", "d-qa-t", "items", "covered.jsonl")
OUT_DIR = os.path.join(REPO, "data", "d-adj-t-llmproxy")
OUT_PROBE = os.path.join(OUT_DIR, "deranged-probe.jsonl")
OUT_MANIFEST = os.path.join(OUT_DIR, "deranged-probe-manifest.json")


def hsort_key(seed, s):
    return hashlib.sha256((seed + "|" + s).encode("utf-8")).hexdigest()


def jdump(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def main():
    got = kc.corpus_hash(REPO, "d-qa-t")
    if got != DQAT_PIN:
        print("ERR_PROBE_REFPIN: data/d-qa-t digest %s != frozen pin %s"
              % (got, DQAT_PIN), file=sys.stderr)
        sys.exit(1)

    with open(ITEMS, "r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    defm = [r for r in rows if r.get("type") == "def-match"]
    if len(defm) != 108:
        print("ERR_PROBE_SOURCE: expected 108 def-match items, got %d"
              % len(defm), file=sys.stderr)
        sys.exit(1)

    # --- selection: seeded-hash sort (repo canonical idiom), first 60 --------
    defm.sort(key=lambda r: hsort_key(SEED_SELECT, r["id"]))
    sel = defm[:N_PROBE]

    # --- derangement: Sattolo cycle over the 60 in selection order -----------
    rng = random.Random(int.from_bytes(
        hashlib.sha256(SEED_DERANGE.encode("utf-8")).digest(), "big"))
    perm = list(range(N_PROBE))
    for i in range(N_PROBE - 1, 0, -1):     # Sattolo: j strictly below i =>
        j = rng.randrange(i)                # single cycle, zero fixed points
        perm[i], perm[j] = perm[j], perm[i]

    def gold_text(r):
        for o in r["options"]:
            if o["key"] == r["answer"]:
                return o["text"]
        print("ERR_PROBE_GOLDKEY: %s" % r["id"], file=sys.stderr)
        sys.exit(1)

    probe_rows, man_rows = [], []
    for i, src in enumerate(sel):
        own = gold_text(src)
        others = [o["text"] for o in src["options"] if o["key"] != src["answer"]]
        donor_idx, steps = perm[i], 0
        # collision rule (deterministic): advance along the cycle while the
        # candidate text is the item's own gold text, equals an option already
        # present, or the candidate is the item itself
        while (donor_idx == i or gold_text(sel[donor_idx]) == own
               or gold_text(sel[donor_idx]) in others):
            donor_idx = perm[donor_idx]
            steps += 1
            if steps > N_PROBE:
                print("ERR_PROBE_CYCLE: no valid donor for %s" % src["id"],
                      file=sys.stderr)
                sys.exit(1)
        donor = sel[donor_idx]
        pid = src["id"].replace("dqat:", "dqatprobe:", 1) + "p"
        options = [{"key": o["key"],
                    "text": gold_text(donor) if o["key"] == src["answer"]
                    else o["text"]}
                   for o in src["options"]]
        probe_rows.append({"allowed": ["A", "B", "C", "D", "NONE"],
                           "format": "mcq", "id": pid, "options": options,
                           "question": src["question"]})
        man_rows.append({"collision_steps": steps,
                         "deranged_option_key": src["answer"],
                         "donor_source_id": donor["id"],
                         "probe_id": pid, "source_id": src["id"]})

    # --- pinned run order (judges are stateless; recorded for provenance) ----
    order = sorted((r["id"] for r in probe_rows),
                   key=lambda pid: hsort_key(SEED_RUNORDER, pid))
    pos = {pid: p + 1 for p, pid in enumerate(order)}
    for m in man_rows:
        m["run_position"] = pos[m["probe_id"]]

    probe_rows.sort(key=lambda r: r["id"])           # by-id, like blind items
    man_rows.sort(key=lambda m: m["probe_id"])
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PROBE, "w", encoding="utf-8") as f:
        for r in probe_rows:
            f.write(jdump(r) + "\n")
    manifest = {"builder": "poc/f2b-transfer/llmproxy/build-deranged-probe.py",
                "correct_answer_by_construction": "NONE",
                "dqat_pin": DQAT_PIN, "n_probe": N_PROBE,
                "residual_note": "a swapped-in gloss may rarely genuinely fit "
                                 "the asked word (~1%-order, disclosed); the "
                                 "0.30 gate bar sits far above that floor",
                "rows": man_rows, "schema": "dqatprobe/1",
                "seed_derange": SEED_DERANGE, "seed_runorder": SEED_RUNORDER,
                "seed_select": SEED_SELECT}
    with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
        f.write(jdump(manifest) + "\n")
    for p in (OUT_PROBE, OUT_MANIFEST):
        with open(p, "rb") as f:
            print("%s  %s" % (hashlib.sha256(f.read()).hexdigest(),
                              os.path.relpath(p, REPO)))
    ncol = sum(1 for m in man_rows if m["collision_steps"])
    print("built %d probe rows (%d collision-advanced)" % (len(probe_rows), ncol))


if __name__ == "__main__":
    main()
