#!/usr/bin/env python3
"""build-deranged-probe — the judge-level content-scramble control for
m0a-llmproxy (registry/experiments/m0a-llmproxy.json; design note
poc/m0a-llmproxy/design.md S4).

WHAT THIS BUILDS. 40 deranged-gloss probe items (20 concept + 20 prime):
same passage and marked token as the sampled item, but the proposed sense is
the gloss of a DIFFERENT sampled target — a seed-pinned per-stratum Sattolo
cycle over the distinct target ids among the selected items, so no probe item
keeps its own target's gloss. The correct answer is 'incorrect' by
construction (near-synonym collision risk disclosed) [STIPULATED: ASM-0544].
Probe items NEVER enter labels or P/R; they feed only the pre-registered
/gates/probe_valid instrument gate (false-endorsement point-rate >= 0.30, or
probe coverage < 36/40 => INSTRUMENT-INVALID) — the gloss-endorsement
leniency channel that would fabricate high proxy precision.

ALSO EMITTED (single manifest, so the runner's pipeline is fully mechanical):
the seed-pinned real-item order over all 300 items
(m0alp/1|judge-m1p|20260710), the probe run order, and the 30 retest item ids
(m0alp/1|retest|20260710, first 30) in their ask order.

DETERMINISM. Single-draw: one build from the seeds below, committed and
sha-pinned in the invocation spec before freeze. Re-running reproduces the
same bytes; any seed change is a design change. Fail-closed: refuses to run
if the annotation sample, the kernel-v0 corpus digest, or the authored prime
glosses drift from the pins below (ERR_M0AP_REFPIN). A forbidden-string sweep
(kernel / nsm / urn: / mapper, case-insensitive) over every prompt-facing
probe field fails the build (ERR_M0AP_BLIND).

Seeds (pre-committed verbatim; design S3/S4 — the single probe seed of the
design is consumed via fixed sub-purpose suffixes, pinned here):
  real order  m0alp/1|judge-m1p|20260710
  probe select    m0alp/1|probe|20260710|select|<stratum>
  probe derange   m0alp/1|probe|20260710|derange|<stratum>
  probe run order m0alp/1|probe|20260710|order
  retest      m0alp/1|retest|20260710
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
SAMPLE = os.path.join(REPO, "mapper", "m0", "annotation-sample.jsonl")
# the record's pinned shas (registry/experiments/m0a-llmproxy.json)
SAMPLE_PIN = "038604a8d7d0fa160209805374b5c89dd5a044c552d1e0dafe0d2bd028575a2c"
KERNELV0_PIN = "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809"
PRIME_GLOSSES = os.path.join(HERE, "prime-glosses.json")
PRIME_GLOSSES_PIN = "fdb004ccb495fd913c89bfe7262d3389d0d86276ff52f6657509735540cb2013"
SEED_REAL = "m0alp/1|judge-m1p|20260710"
SEED_PROBE = "m0alp/1|probe|20260710"
SEED_RETEST = "m0alp/1|retest|20260710"
N_PER_STRATUM = 20
N_RETEST = 30
OUT_PROBE = os.path.join(HERE, "deranged-probe.jsonl")
OUT_MANIFEST = os.path.join(HERE, "deranged-probe-manifest.json")
FORBIDDEN = re.compile(r"kernel|nsm|urn:|mapper", re.IGNORECASE)


def hsort_key(seed, s):
    return hashlib.sha256((seed + "|" + s).encode("utf-8")).hexdigest()


def jdump(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def gloss_of(target, prime_gloss_by_name):
    if target.startswith("urn:kernel-v0:"):
        slug = target.rsplit(":", 1)[1]
        with open(os.path.join(REPO, "data", "kernel-v0", "concepts",
                               slug + ".json"), "r", encoding="utf-8") as f:
            return json.load(f)["gloss"]
    if target.startswith("prime:"):
        return prime_gloss_by_name[target.split(":", 1)[1]]["gloss"]
    print("ERR_M0AP_TARGET: unresolvable target %s" % target, file=sys.stderr)
    sys.exit(1)


def main():
    with open(SAMPLE, "rb") as f:
        raw = f.read()
    got = hashlib.sha256(raw).hexdigest()
    if got != SAMPLE_PIN:
        print("ERR_M0AP_REFPIN: annotation-sample.jsonl sha %s != pinned %s"
              % (got, SAMPLE_PIN), file=sys.stderr)
        sys.exit(1)
    got = kc.corpus_hash(REPO, "kernel-v0")
    if got != KERNELV0_PIN:
        print("ERR_M0AP_REFPIN: kernel-v0 digest %s != pinned %s"
              % (got, KERNELV0_PIN), file=sys.stderr)
        sys.exit(1)
    with open(PRIME_GLOSSES, "rb") as f:
        praw = f.read()
    if hashlib.sha256(praw).hexdigest() != PRIME_GLOSSES_PIN:
        print("ERR_M0AP_REFPIN: prime-glosses.json sha != pinned",
              file=sys.stderr)
        sys.exit(1)
    prime_gloss_by_name = {g["name"]: g for g in
                           json.loads(praw.decode("utf-8"))["glosses"]}

    items = [json.loads(l) for l in raw.decode("utf-8").splitlines()
             if l.strip()]
    if len(items) != 300:
        print("ERR_M0AP_SOURCE: expected 300 items, got %d" % len(items),
              file=sys.stderr)
        sys.exit(1)
    by_id = {it["itemId"]: it for it in items}

    probe_rows, man_rows = [], []
    for stratum in ("concept", "prime"):
        pool = [it for it in items if it["stratum"] == stratum]
        pool.sort(key=lambda it: hsort_key(
            SEED_PROBE + "|select|" + stratum, it["itemId"]))
        sel = pool[:N_PER_STRATUM]
        # distinct target ids among the selected items, sorted; Sattolo over them
        targets = sorted({it["decision"]["target"] for it in sel})
        if len(targets) < 2:
            print("ERR_M0AP_DERANGE: <2 distinct targets in %s selection"
                  % stratum, file=sys.stderr)
            sys.exit(1)
        rng = random.Random(int.from_bytes(hashlib.sha256(
            (SEED_PROBE + "|derange|" + stratum).encode("utf-8")).digest(),
            "big"))
        perm = list(range(len(targets)))
        for i in range(len(targets) - 1, 0, -1):  # Sattolo: single cycle,
            j = rng.randrange(i)                  # zero fixed points
            perm[i], perm[j] = perm[j], perm[i]
        sigma = {targets[i]: targets[perm[i]] for i in range(len(targets))}
        for it in sel:
            own = it["decision"]["target"]
            own_gloss = gloss_of(own, prime_gloss_by_name)
            donor, steps = sigma[own], 0
            # collision rule (deterministic): advance along the cycle while
            # the donor gloss is byte-equal to the item's own gloss
            while gloss_of(donor, prime_gloss_by_name) == own_gloss:
                donor = sigma[donor]
                steps += 1
                if steps > len(targets):
                    print("ERR_M0AP_CYCLE: no valid donor for %s"
                          % it["itemId"], file=sys.stderr)
                    sys.exit(1)
            pid = it["itemId"].replace("m0a-", "m0ap-", 1)
            probe_rows.append({"contextAfter": it["contextAfter"],
                               "contextBefore": it["contextBefore"],
                               "id": pid,
                               "sense": gloss_of(donor, prime_gloss_by_name),
                               "stratum": stratum,
                               "surface": it["surface"]})
            man_rows.append({"collision_steps": steps,
                             "donor_target": donor,
                             "own_target": own,
                             "probe_id": pid,
                             "source_item": it["itemId"]})

    # blind sweep over every prompt-facing probe field (manifest is
    # provenance-only and MAY name targets; probe rows may not)
    for r in probe_rows:
        for fld in ("contextBefore", "surface", "contextAfter", "sense"):
            if FORBIDDEN.search(r[fld]):
                print("ERR_M0AP_BLIND: forbidden string in probe %s field %s"
                      % (r["id"], fld), file=sys.stderr)
                sys.exit(1)

    # --- pinned orders (judge is stateless; recorded for provenance) ---------
    real_order = sorted(by_id, key=lambda x: hsort_key(SEED_REAL, x))
    probe_order = sorted((r["id"] for r in probe_rows),
                         key=lambda x: hsort_key(SEED_PROBE + "|order", x))
    pos = {pid: p + 1 for p, pid in enumerate(probe_order)}
    for m in man_rows:
        m["run_position"] = pos[m["probe_id"]]
    retest_ids = sorted(by_id, key=lambda x: hsort_key(SEED_RETEST, x))[:N_RETEST]

    probe_rows.sort(key=lambda r: r["id"])
    man_rows.sort(key=lambda m: m["probe_id"])
    with open(OUT_PROBE, "w", encoding="utf-8") as f:
        for r in probe_rows:
            f.write(jdump(r) + "\n")
    manifest = {"builder": "poc/m0a-llmproxy/build-deranged-probe.py",
                "correct_answer_by_construction": {"answer": "incorrect"},
                "kernel_v0_pin": KERNELV0_PIN, "n_probe": len(probe_rows),
                "n_retest": N_RETEST,
                "prime_glosses_pin": PRIME_GLOSSES_PIN,
                "probe_order": probe_order,
                "real_order": real_order,
                "residual_note": "a deranged-in gloss may, rarely, genuinely "
                                 "fit the marked token (near-synonym residual,"
                                 " disclosed; ASM-0544); the 0.30 gate bar "
                                 "sits far above that floor",
                "retest_ids": retest_ids,
                "rows": man_rows, "sample_pin": SAMPLE_PIN,
                "schema": "m0alp-probe/1",
                "seed_probe": SEED_PROBE, "seed_real_order": SEED_REAL,
                "seed_retest": SEED_RETEST}
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
