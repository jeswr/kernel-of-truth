#!/usr/bin/env python3
"""build-probe-b — the mismatched-conditions control for g3-llmproxy
(registry/experiments/g3-llmproxy.json; design note poc/g3-llmproxy/design.md
S5).

WHAT THIS BUILDS. 30 probe-B items: seed-pinned instances presented in pass-B
form with the condition set of a DIFFERENT concept (a seed-pinned Sattolo
cycle over the 20 condition_set_ids at concept level), original text +
bindings verbatim. The correct pass-B answer is 'no' by construction (another
concept's conditions; roles may be unbound in the deranged set — cannot-say
on probes counts as non-endorsement, only q2=yes counts as false
satisfaction) [STIPULATED: ASM-0534]. Probe items run AFTER the real pass-B
and NEVER enter counts; they feed only the pre-registered /gates/probe_valid
instrument gate, PER JUDGE (false-satisfaction point-rate >= 0.30, or probe
coverage < 27/30 => INSTRUMENT-INVALID) — the channel that would fabricate a
low violation rate.

ALSO EMITTED (single manifest, so the runner's pipeline is fully mechanical):
the four seed-pinned real-item orders (g3lp/1|judge-<p>-<pass>|20260710 for
judge-pA/judge-pB x passA/passB) and the per-judge probe run orders.

DETERMINISM. Single-draw: one build from the seeds below, committed and
sha-pinned in the invocation spec before freeze. Re-running reproduces the
same bytes; any seed change is a design change. Fail-closed: refuses to run
if the instance-descriptions corpus digest drifts from the design-time pin
below (ERR_G3P_REFPIN; if g3's own materials pin lands on different bytes
first, this record re-pins BEFORE freeze — never after, per the record's
_pin_note — and this constant moves with it). A forbidden-string sweep
(kernel / nsm / necessity / sufficiency / hypothesis, case-insensitive) over
every prompt-facing probe field fails the build (ERR_G3P_BLIND).

Seeds (pre-committed verbatim; design S2/S5 — the single probe seed of the
design is consumed via fixed sub-purpose suffixes, pinned here):
  real orders   g3lp/1|judge-pA-passA|20260710   g3lp/1|judge-pA-passB|20260710
                g3lp/1|judge-pB-passA|20260710   g3lp/1|judge-pB-passB|20260710
  probe select  g3lp/1|probe|20260710            (rank all 200, first 30)
  probe derange g3lp/1|probe|20260710|derange-conditions
  probe orders  g3lp/1|judge-pA-probeB|20260710  g3lp/1|judge-pB-probeB|20260710
"""
import hashlib
import json
import os
import random
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "registry"))
import kot_common as kc  # noqa: E402  (corpus_hash — kot-corpus-hash/1 reference impl)

HERE = os.path.dirname(os.path.abspath(__file__))
# the record's design-time CANDIDATE-MATERIALS pin (re-verified at freeze)
IDESC_PIN = "1a55a2194f667a0f647e8cd3ce21b2c6327446b020dd24576c5263ea930d4f7d"
INSTANCES = os.path.join(REPO, "data", "instance-descriptions",
                         "instances.jsonl")
CONDITIONS = os.path.join(REPO, "data", "instance-descriptions",
                          "conditions.jsonl")
SEED_PROBE = "g3lp/1|probe|20260710"
SEEDS_REAL = {"judge-pA-passA": "g3lp/1|judge-pA-passA|20260710",
              "judge-pA-passB": "g3lp/1|judge-pA-passB|20260710",
              "judge-pB-passA": "g3lp/1|judge-pB-passA|20260710",
              "judge-pB-passB": "g3lp/1|judge-pB-passB|20260710"}
SEEDS_PROBE_ORDER = {"judge-pA": "g3lp/1|judge-pA-probeB|20260710",
                     "judge-pB": "g3lp/1|judge-pB-probeB|20260710"}
N_PROBE = 30
OUT_PROBE = os.path.join(HERE, "probe-b.jsonl")
OUT_MANIFEST = os.path.join(HERE, "probe-b-manifest.json")
FORBIDDEN = re.compile(r"kernel|nsm|necessity|sufficiency|hypothesis",
                       re.IGNORECASE)


def hsort_key(seed, s):
    return hashlib.sha256((seed + "|" + s).encode("utf-8")).hexdigest()


def jdump(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def main():
    got = kc.corpus_hash(REPO, "instance-descriptions")
    if got != IDESC_PIN:
        print("ERR_G3P_REFPIN: instance-descriptions digest %s != pinned %s"
              % (got, IDESC_PIN), file=sys.stderr)
        sys.exit(1)
    with open(INSTANCES, "r", encoding="utf-8") as f:
        inst = [json.loads(l) for l in f if l.strip()]
    inst = [r for r in inst if "instance_id" in r]
    if len(inst) != 200:
        print("ERR_G3P_SOURCE: expected 200 instances, got %d" % len(inst),
              file=sys.stderr)
        sys.exit(1)
    with open(CONDITIONS, "r", encoding="utf-8") as f:
        csets = [json.loads(l) for l in f if l.strip()]
    csets = {c["condition_set_id"]: c for c in csets if "condition_set_id" in c}
    if len(csets) != 20:
        print("ERR_G3P_SOURCE: expected 20 condition sets, got %d"
              % len(csets), file=sys.stderr)
        sys.exit(1)

    # --- selection: rank all 200 instance ids, first 30 ----------------------
    sel = sorted(inst, key=lambda r: hsort_key(SEED_PROBE, r["instance_id"]))
    sel = sel[:N_PROBE]

    # --- derangement: Sattolo over the 20 condition_set_ids ------------------
    kids = sorted(csets)
    rng = random.Random(int.from_bytes(hashlib.sha256(
        (SEED_PROBE + "|derange-conditions").encode("utf-8")).digest(), "big"))
    perm = list(range(len(kids)))
    for i in range(len(kids) - 1, 0, -1):   # Sattolo: single cycle,
        j = rng.randrange(i)                # zero fixed points
        perm[i], perm[j] = perm[j], perm[i]
    sigma = {kids[i]: kids[perm[i]] for i in range(len(kids))}

    def cond_texts(kid):
        return [c["text"] for c in csets[kid]["conditions"]]

    probe_rows, man_rows = [], []
    for r in sel:
        own = r["condition_set_id"]
        donor, steps = sigma[own], 0
        # collision rule (deterministic, fail-closed completeness): advance
        # along the cycle while the donor's condition texts are byte-equal to
        # the instance's own set's texts (cannot occur across the 20 distinct
        # authored sets)
        while cond_texts(donor) == cond_texts(own):
            donor = sigma[donor]
            steps += 1
            if steps > len(kids):
                print("ERR_G3P_CYCLE: no valid donor for %s"
                      % r["instance_id"], file=sys.stderr)
                sys.exit(1)
        pid = r["instance_id"] + "-pb"
        probe_rows.append({"bindings": r["bindings"],
                           "conditions": [{"cid": c["cid"], "text": c["text"]}
                                          for c in csets[donor]["conditions"]],
                           "id": pid, "text": r["text"]})
        man_rows.append({"collision_steps": steps,
                         "donor_condition_set": donor,
                         "own_condition_set": own,
                         "probe_id": pid,
                         "source_instance": r["instance_id"]})

    # blind sweep over every prompt-facing probe field (the manifest is
    # provenance-only and never enters any prompt)
    for r in probe_rows:
        surfaces = [r["text"]]
        surfaces += ["%s = %s" % (k, v) for k, v in r["bindings"].items()]
        surfaces += ["%s: %s" % (c["cid"], c["text"]) for c in r["conditions"]]
        for s in surfaces:
            if FORBIDDEN.search(s):
                print("ERR_G3P_BLIND: forbidden string in probe %s" % r["id"],
                      file=sys.stderr)
                sys.exit(1)

    # --- pinned orders (judges are stateless; recorded for provenance) -------
    ids = [r["instance_id"] for r in inst]
    real_orders = {k: sorted(ids, key=lambda x: hsort_key(seed, x))
                   for k, seed in sorted(SEEDS_REAL.items())}
    probe_orders = {}
    for judge, seed in sorted(SEEDS_PROBE_ORDER.items()):
        order = sorted((r["id"] for r in probe_rows),
                       key=lambda x: hsort_key(seed, x))
        probe_orders[judge] = order
        pos = {pid: p + 1 for p, pid in enumerate(order)}
        for m in man_rows:
            m["run_position_%s" % judge.replace("-", "_")] = pos[m["probe_id"]]

    probe_rows.sort(key=lambda r: r["id"])
    man_rows.sort(key=lambda m: m["probe_id"])
    with open(OUT_PROBE, "w", encoding="utf-8") as f:
        for r in probe_rows:
            f.write(jdump(r) + "\n")
    manifest = {"builder": "poc/g3-llmproxy/build-probe-b.py",
                "correct_answer_by_construction": {"q2": "no"},
                "escape_note": "cannot-say on probes counts as "
                               "non-endorsement; only q2=yes is false "
                               "satisfaction (ASM-0534)",
                "instance_descriptions_pin": IDESC_PIN,
                "n_probe": N_PROBE,
                "probe_orders": probe_orders,
                "real_orders": real_orders,
                "residual_note": "roles may be unbound under the deranged "
                                 "condition set; a content-competent judge "
                                 "must not mark every-condition satisfaction "
                                 "(ASM-0534)",
                "rows": man_rows, "schema": "g3lp-probe/1",
                "seed_derange": SEED_PROBE + "|derange-conditions",
                "seed_probe_orders": SEEDS_PROBE_ORDER,
                "seed_real_orders": SEEDS_REAL,
                "seed_select": SEED_PROBE}
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
