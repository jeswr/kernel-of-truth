#!/usr/bin/env python3
"""prereg-freeze — validate a DRAFT registry record and freeze it (P2 §1.1, S1 step 3).

    python3 tools/registry/prereg-freeze.py --experiment <id> --agent-id coordinator-1
        [--root <repo>] [--frozen-at 2026-07-09T00:00:00Z] [--dry-run]

Reads registry/experiments/<id>.json (status DRAFT), runs every freeze-time
check below, then sets status=FROZEN, stamps frozen_at/frozen_by, computes
frozen_sha256 over the canonical-JSON bytes of the record with `status` and
`frozen_sha256` excluded (P2 §1.1), rewrites the record canonically, and
appends id -> frozen_sha256 to registry/frozen-index.json.

Fail-closed refusals (all abort with exit 1 and a named code):
  ERR_P2_SCHEMA              record does not validate against kot-reg/1
  ERR_P2_NOT_DRAFT           status is not DRAFT
  ERR_P2_ALREADY_FROZEN      id already present in frozen-index.json
  ERR_P2_ENDPOINTS           not exactly one role:"primary" endpoint (constraint 1)
  ERR_P2_UNKNOWN_POINTER     a verdict-rule/endpoint metric pointer is not in the
                             analysis script's declared output_fields (constraint 2)
  ERR_P2_RULES_NOT_EXHAUSTIVE  last rule is not the INCONCLUSIVE catch-all (constraint 3)
  ERR_P2_NULL_WITHOUT_SESOI  NULL rule present but primary endpoint has no
                             smallest_effect_of_interest (constraint 4)
  ERR_P2_MISSING_METRIC_VECTOR efficiency_relevant without the five V DVs (constraint 5)
  ERR_P2_SEEDS               trained arms declared but <5 seeds (constraint 6)
  ERR_P2_MISSING_KILL / ERR_P2_MISSING_ENVELOPE  (constraints 7/8; also schema-enforced)
  ERR_P2_UNPOWERED_GATE      a Wilson-bound gate undecidable at planned n (constraint 9, RT-4)
  ERR_P2_ACCOUNT_IN_RECORD   account-identifying material inside hashed bytes (constraint 10, RT-14)
  ERR_P2_MISSING_BASELINE    arms_mandatory_baselines empty (G-8, minimal form)
  ERR_P2_PIN_MISMATCH        pinned analysis script / plan doc / prereg doc sha256
                             does not match the committed file bytes
  ERR_P2_CORPUS_PIN          pins.corpus_hashes._recipe is not the current
                             kot-corpus-hash/1 recipe, or a non-placeholder corpus
                             digest does not reproduce from data/<corpus>/ at
                             freeze time (correction c-2026-07-08)
  ERR_P2_SIGNOFF             budget.usd_cap > 900 without maintainer_signoff (G-11 Tier-5)

External freeze-timestamping (P2 §1.1 RT-15: publish the hash to the
coordination issue) is a POST-step for the coordinator; this tool prints the
line to post but never touches the network.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc

FIVE_V = ("accuracy", "params", "memory", "inference_compute", "training_compute")
CATCH_ALL = {"verdict": "INCONCLUSIVE", "when": {"const": True}}


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def file_sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_record(record, root):
    """All freeze-time lints. Raises kc.KotError on the first violation."""
    schema_path = os.path.join(root, "registry", "schema", "kot-reg-1.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    errs = kc.validate_schema(record, schema)
    if errs:
        raise kc.KotError("ERR_P2_SCHEMA", "; ".join(errs[:10]))

    if record["status"] != "DRAFT":
        raise kc.KotError("ERR_P2_NOT_DRAFT", "status=%r; only DRAFT records can be frozen" % record["status"])

    # Constraint 1: exactly one primary endpoint.
    primaries = [e for e in record["endpoints"] if e["role"] == "primary"]
    if len(primaries) != 1:
        raise kc.KotError("ERR_P2_ENDPOINTS", "found %d primary endpoints; exactly one required" % len(primaries))

    # Constraint 3: provably exhaustive rule list.
    if record["verdict_rules"][-1] != CATCH_ALL:
        raise kc.KotError(
            "ERR_P2_RULES_NOT_EXHAUSTIVE",
            'last verdict rule must be {"verdict":"INCONCLUSIVE","when":{"const":true}}',
        )

    # Constraint 2: every metric pointer resolves to a declared analysis-output field.
    declared = set(record["pins"]["analysis_script"]["output_fields"])
    pointers = []
    for rule in record["verdict_rules"]:
        pointers.extend(kc.collect_metric_pointers(rule["when"]))
    for ep in record["endpoints"]:
        pointers.append(ep["metric"])
    unknown = sorted(set(p for p in pointers if p not in declared))
    if unknown:
        raise kc.KotError(
            "ERR_P2_UNKNOWN_POINTER",
            "metric pointers not in pins.analysis_script.output_fields: %s" % ", ".join(unknown),
        )

    # Constraint 4: NULL requires a TOST bound on the primary endpoint.
    if any(r["verdict"] == "NULL" for r in record["verdict_rules"]):
        if "smallest_effect_of_interest" not in primaries[0]:
            raise kc.KotError(
                "ERR_P2_NULL_WITHOUT_SESOI",
                "NULL verdict declared but primary endpoint has no smallest_effect_of_interest",
            )

    # Constraint 5: efficiency_relevant => full metric vector V in the DVs.
    if record.get("efficiency_relevant"):
        dv_names = {dv["name"] for dv in record["design"]["dependent_vars"]}
        missing = [v for v in FIVE_V if v not in dv_names]
        if missing:
            raise kc.KotError(
                "ERR_P2_MISSING_METRIC_VECTOR",
                "efficiency_relevant but dependent_vars missing V components: %s" % ", ".join(missing),
            )

    # Constraint 6: >=5 seeds whenever any arm is a trained condition.
    if "seeds_per_trained_arm" in record["design"].get("n_planned", {}):
        if len(record["design"]["seeds"]) < 5:
            raise kc.KotError("ERR_P2_SEEDS", "trained arms declared but only %d seeds registered (>=5 required)"
                              % len(record["design"]["seeds"]))

    # Constraints 7/8: non-empty kill text + envelope (schema also enforces minLength).
    if not record["kill_criterion_verbatim"].strip():
        raise kc.KotError("ERR_P2_MISSING_KILL", "kill_criterion_verbatim is blank")
    if not record["extrapolation_envelope_verbatim"].strip():
        raise kc.KotError("ERR_P2_MISSING_ENVELOPE", "extrapolation_envelope_verbatim is blank")

    # Constraint 9 (RT-4): Wilson-bound gates must be powered at planned n.
    for ep in record["endpoints"]:
        if "wilson_gate" in ep:
            kc.check_wilson_gate(ep["wilson_gate"], "endpoint %r" % ep["id"])

    # G-8 (minimal form): mandatory baselines declared.
    if not record["design"]["arms_mandatory_baselines"]:
        raise kc.KotError("ERR_P2_MISSING_BASELINE", "arms_mandatory_baselines is empty")

    # G-11 Tier-5 interlock (canonical caps: anything above the $900 Tier-4 cap).
    if record["budget"]["usd_cap"] > 900 and "maintainer_signoff" not in record["budget"]:
        raise kc.KotError("ERR_P2_SIGNOFF", "usd_cap %s > 900 requires budget.maintainer_signoff"
                          % record["budget"]["usd_cap"])

    # Corpus pins (kot-corpus-hash/1; correction c-2026-07-08 closing the F1
    # pin-generation defect): the record must carry the exact current recipe
    # string, and every non-placeholder digest must reproduce from data/<corpus>/
    # at freeze time. PINNED-AT-INPUTS:* placeholders (pre-declared inputs
    # completed by ops amendment before any final-phase run, P2 P-9) are exempt.
    corpus_pins = record["pins"]["corpus_hashes"]
    if corpus_pins.get("_recipe") != kc.CORPUS_RECIPE:
        raise kc.KotError(
            "ERR_P2_CORPUS_PIN",
            "pins.corpus_hashes._recipe is not the current kot-corpus-hash/1 recipe string "
            "(kot_common.CORPUS_RECIPE) — unverifiable corpus pins cannot be frozen",
        )
    for name, want in sorted(corpus_pins.items()):
        if name == "_recipe":
            continue
        if isinstance(want, str) and want.startswith(kc.PINNED_AT_INPUTS_PREFIX):
            continue
        if not isinstance(want, str) or not kc.SHA256_RE.match(want):
            raise kc.KotError("ERR_P2_CORPUS_PIN",
                              "pins.corpus_hashes[%r] is neither a sha256 digest nor a "
                              "PINNED-AT-INPUTS placeholder" % name)
        got = kc.corpus_hash(root, name)
        if got != want:
            raise kc.KotError("ERR_P2_CORPUS_PIN",
                              "pins.corpus_hashes[%r]: recomputed %s != pinned %s "
                              "(kot-corpus-hash/1 over data/%s/)" % (name, got, want, name))

    # P-6 pins: the pinned analysis script and referenced docs must match their shas NOW.
    for what, path, want in (
        ("pins.analysis_script", record["pins"]["analysis_script"]["path"], record["pins"]["analysis_script"]["sha256"]),
        ("analysis_plan_ref", record["analysis_plan_ref"]["path"], record["analysis_plan_ref"]["sha256"]),
        ("prereg_doc", record["prereg_doc"]["path"], record["prereg_doc"]["sha256"]),
    ):
        full = os.path.join(root, path)
        if not os.path.isfile(full):
            raise kc.KotError("ERR_P2_PIN_MISMATCH", "%s: %s does not exist" % (what, path))
        got = file_sha256(full)
        if got != want:
            raise kc.KotError("ERR_P2_PIN_MISMATCH", "%s: %s sha256 %s != pinned %s" % (what, path, got, want))

    # Constraint 10 (RT-14): no account-identifying material inside hashed bytes,
    # and every identity field is a pseudonym. Scanned over exactly the byte
    # range frozen_sha256 will cover (record minus status/frozen_sha256).
    kc.check_identity_fields(record)
    hashed = {k: v for k, v in record.items() if k not in ("status", "frozen_sha256")}
    kc.require_no_account_strings(kc.canonical_bytes(hashed), "frozen-record hashed bytes")


def main():
    ap = argparse.ArgumentParser(description="Freeze a DRAFT kot-reg/1 registry record (fail-closed).")
    ap.add_argument("--experiment", required=True, help="EXP-ID (registry/experiments/<id>.json)")
    ap.add_argument("--agent-id", required=True, help="pseudonymous identity, e.g. coordinator-1")
    ap.add_argument("--root", default=None, help="repo root (default: inferred from this file)")
    ap.add_argument("--frozen-at", default=None, help="UTC timestamp override (byte-determinism/tests)")
    ap.add_argument("--dry-run", action="store_true", help="run every check, write nothing")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rec_path = os.path.join(root, "registry", "experiments", "%s.json" % args.experiment)
    index_path = os.path.join(root, "registry", "frozen-index.json")

    try:
        kc.require_pseudonym(args.agent_id, "--agent-id")
        with open(rec_path, "r", encoding="utf-8") as f:
            record = json.load(f)
        if record.get("id") != args.experiment:
            fail("ERR_P2_SCHEMA", "record id %r != --experiment %r" % (record.get("id"), args.experiment))

        index = {}
        if os.path.isfile(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
        if args.experiment in index:
            fail("ERR_P2_ALREADY_FROZEN", "%s already in frozen-index.json — frozen records are immutable; "
                 "changes are amendments or a new experiment id" % args.experiment)

        # Stamp freeze fields BEFORE hashing (they are inside the hashed bytes).
        record["frozen_by"] = args.agent_id
        record["frozen_at"] = args.frozen_at or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        check_record(record, root)

        record["status"] = "FROZEN"
        record["frozen_sha256"] = kc.frozen_hash(record)

        if not args.dry_run:
            kc.write_canonical_json(rec_path, record)
            index[args.experiment] = record["frozen_sha256"]
            kc.write_canonical_json(index_path, index)

        print(json.dumps({
            "experiment": args.experiment,
            "status": "FROZEN" if not args.dry_run else "DRY-RUN-OK",
            "frozen_sha256": record["frozen_sha256"],
            "frozen_at": record["frozen_at"],
            "frozen_by": record["frozen_by"],
            "external_timestamp_post": "prereg freeze %s frozen_sha256=%s (post hash-only to the coordination issue — RT-15)"
                                       % (args.experiment, record["frozen_sha256"]),
        }, indent=2, sort_keys=True))
    except kc.KotError as e:
        fail(e.code, str(e).split(": ", 1)[1])
    except FileNotFoundError as e:
        fail("ERR_P2_IO", str(e))


if __name__ == "__main__":
    main()
