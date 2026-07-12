#!/usr/bin/env python3
# RULES-1-KNULL-CERT runner — shadow-staged, byte-identical harness reuse.
# (2026-07-12 record split: the CPU certificate leg is registered as
# registry/experiments/rules-1-knull-cert.json; the conditional GPU host-lift
# leg is registered separately as rules-1-knull-hostlift.json and does NOT
# use this runner. This runner supersedes the bundled rules-1-knull-ablation
# draft's REG_SELF binding.)
#
# Design anchors: docs/next/design/rules-1-knull-ablation.md;
# PROPOSED-ASM-1400 (substitution scope), 1405 (k0 staging-identity gate),
# 1409 (role separation: arms k1/k2 refuse to run without --registered —
# they are the REGISTERED runner role's, post-freeze; only k0, --mock and
# --smoke are pre-freeze-safe: k0's outcome is already pinned in the frozen
# rules-1 record, mock payloads are synthetic, and the smoke is PARSE-ONLY —
# it never computes a closure or a decision),
# 1412 (k2_tbox_loads gate feeding discrimination_valid),
# 1413 (stage-time digest attestation; analysis rejects unattested payloads),
# 1414 (pre-freeze parse-only smoke), 1416 (engine-identity disclosure).
#
# Mechanism: for each arm a shadow tree is staged —
#   shadow/<arm>/poc/rules-1/{certificate.py, twin_engine.py}   BYTE-COPIES,
#       sha-verified against the RULES-1 pins (fail-closed ERR_PIN_MISMATCH):
#       twin_engine.py vs registry/experiments/rules-1.json
#       pins.artifact_hashes["twin-engine(...)"], certificate.py vs the
#       pinned certificate-result.json pins.certificate_py.
#   shadow/<arm>/data/{nsk1-clutrr, world-v0}                   symlinks to
#       the real corpora (read-only; per-file shas re-verified).
#   shadow/<arm>/data/axioms-v0, data/axioms-kinship-v1         THE ONLY
#       SUBSTITUTED CONTENT: k0 = the real (kernel) dirs; k1 = tbox-knull;
#       k2 = tbox-scrambled.
# Then `python3 certificate.py` runs UNMODIFIED inside the shadow tree
# (certificate.py resolves ROOT from its own path, so the substitution is
# invisible to the harness bytes). Result JSON is collected per arm.
#
# ATTESTATION (PROPOSED-ASM-1413, review fix 2): before any arm runs, the
# k1/k2 SOURCE input directories are re-digested under the kot-corpus-hash/1
# recipe and compared against the REGISTERED pins in
# registry/experiments/rules-1-knull-cert.json pins.artifact_hashes —
# post-freeze drift of the substituted TBoxes refuses fail-closed
# (ERR_PIN_MISMATCH). Every payload written by this runner carries an
# `attestation` block (record identity + frozen sha, arm identity, per-arm
# harness shas, source + staged TBox dir-digests, shared-corpus digests);
# analysis/rules_1_knull.py REJECTS unattested or drifted payloads
# (/gates/harness_pins_valid false => INSTRUMENT-INVALID).
#
# ENGINE IDENTITY (PROPOSED-ASM-1416, review fix 6): k1/k2 decisions are
# computed SOLELY by the pinned Python twin (twin_engine.py sha 399fcd8d…).
# The certificate's inherited certificate_result.engine_identity block
# ("BOTH engines … sparq-reason … EXACTLY agreed") describes the RULES-1
# conformance run over the KERNEL TBox; no sparq-reason execution occurs
# over a substituted TBox. The runner stamps that disclosure into every
# k1/k2 payload so the inherited text can never be read as a k1/k2 claim.
# Substituted-TBox differential conformance is a NAMED FOLLOW-ON.
#
# k0 staging-identity gate (ASM-1405): the k0 run must reproduce the pinned
# decision_payload_sha256 — proving the staging instrument itself is inert.
#
# NO feasibility conclusion is stated by this script. Fail-closed throughout.

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
R1 = ROOT / "poc" / "rules-1"
REG = ROOT / "registry" / "experiments" / "rules-1.json"
REG_SELF = ROOT / "registry" / "experiments" / "rules-1-knull-cert.json"
CERT_RESULT = R1 / "results" / "certificate-result.json"

ARM_TBOX = {
    "k0": None,                                   # kernel (reference)
    "k1": HERE / "inputs" / "tbox-knull",         # knull-plain
    "k2": HERE / "inputs" / "tbox-scrambled",     # Sattolo-scrambled
}
ARM_PIN_KEY = {
    "k1": "tbox-knull(dir-digest, kot-corpus-hash/1 recipe over "
          "poc/rules-1-knull/inputs/tbox-knull)",
    "k2": "tbox-scrambled(dir-digest, kot-corpus-hash/1 recipe over "
          "poc/rules-1-knull/inputs/tbox-scrambled)",
}
ENGINE_IDENTITY_DISCLOSURE = (
    "ABLATION ARM (PROPOSED-ASM-1416): decisions in this payload were "
    "computed SOLELY by the pinned Python differential twin "
    "(poc/rules-1/twin_engine.py, sha attested below). The inherited "
    "certificate_result.engine_identity block describes the RULES-1 "
    "conformance run over the KERNEL TBox (sparq-reason vs twin, 1207/1207) "
    "and is FALSE FOR THIS SUBSTITUTED ARM: sparq-reason was NOT executed "
    "over this TBox. Substituted-TBox differential conformance is a named "
    "follow-on, not part of this record.")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def die(code, msg):
    print(json.dumps({"error": code, "msg": msg}), file=sys.stderr)
    sys.exit(1)


def dir_digest(base):
    """kot-corpus-hash/1 recipe (tools/registry/corpus-pin.py reference):
    sha256 over '<sha256-of-file-bytes>  <relpath>\\n' lines, two spaces,
    POSIX relpaths, sorted by UTF-8 byte order, regular files only."""
    base = Path(base)
    lines = []
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(base).as_posix()
        lines.append((rel.encode("utf-8"), "%s  %s\n" % (sha(p), rel)))
    lines.sort(key=lambda t: t[0])
    return hashlib.sha256("".join(t[1] for t in lines)
                          .encode("utf-8")).hexdigest()


def load_pins():
    reg = json.loads(REG.read_text())
    cert = json.loads(CERT_RESULT.read_text())
    ah = reg["pins"]["artifact_hashes"]
    return {
        "twin_engine_py": ah["twin-engine(poc/rules-1/twin_engine.py)"],
        "certificate_py": cert["pins"]["certificate_py"],
        "mint_kinship_py": cert["pins"]["mint_kinship_py"],
        "items_jsonl": cert["pins"]["items_jsonl"],
        "world_jsonl": cert["pins"]["world_jsonl"],
        "world_v0_jsonl": cert["pins"]["world_v0_jsonl"],
        "decision_payload_sha256":
            cert["determinism"]["decision_payload_sha256"],
        "certificate_result_sha256": sha(CERT_RESULT),
        "rules1_frozen_status": reg.get("status"),
        "kernel_corpus_digests": {c: reg["pins"]["corpus_hashes"][c]
                                  for c in ("axioms-v0", "axioms-kinship-v1")},
    }


def load_self_record():
    """The rules-1-knull-cert registry record — the registered digest
    source the attestation is checked against (PROPOSED-ASM-1413)."""
    if not REG_SELF.is_file():
        die("ERR_INPUT_MISSING", str(REG_SELF))
    rec = json.loads(REG_SELF.read_text())
    return rec


def stage(arm, pins, record):
    shadow = HERE / "shadow" / arm
    if shadow.exists():
        shutil.rmtree(shadow)
    (shadow / "poc" / "rules-1").mkdir(parents=True)
    (shadow / "data").mkdir(parents=True)
    harness_shas = {}
    # 1. harness bytes — copied, then sha-verified (fail closed)
    for name, pin in (("certificate.py", pins["certificate_py"]),
                      ("twin_engine.py", pins["twin_engine_py"]),
                      # mint_kinship.py is staged ONLY because certificate.py
                      # records its sha in the result pins block; it is never
                      # executed by the certificate (provenance-inert).
                      ("mint_kinship.py", pins["mint_kinship_py"])):
        src, dst = R1 / name, shadow / "poc" / "rules-1" / name
        shutil.copyfile(src, dst)
        got = sha(dst)
        if got != pin:
            die("ERR_PIN_MISMATCH", f"{name}: {got} != pinned {pin}")
        harness_shas[name] = got
    # 2. shared read-only corpora — symlinked, key files sha-verified
    for corpus in ("nsk1-clutrr", "world-v0"):
        (shadow / "data" / corpus).symlink_to(ROOT / "data" / corpus)
    data_shas = {}
    for rel, pin in (("nsk1-clutrr/items.jsonl", pins["items_jsonl"]),
                     ("nsk1-clutrr/world.jsonl", pins["world_jsonl"]),
                     ("world-v0/world.jsonl", pins["world_v0_jsonl"])):
        got = sha(ROOT / "data" / rel)
        if got != pin:
            die("ERR_PIN_MISMATCH", f"data/{rel} drifted from rules-1 pin")
        data_shas[rel] = got
    # 3. THE SUBSTITUTION (ASM-1400): TBox dirs only — with dir-digest
    #    attestation against the REGISTERED pins (ASM-1413, review fix 2):
    #    a post-freeze edit of the substituted TBoxes refuses fail-closed.
    tbox_attest = {}
    if ARM_TBOX[arm] is None:
        for corpus in ("axioms-v0", "axioms-kinship-v1"):
            (shadow / "data" / corpus).symlink_to(ROOT / "data" / corpus)
            got = dir_digest(ROOT / "data" / corpus)
            want = pins["kernel_corpus_digests"][corpus]
            if got != want:
                die("ERR_PIN_MISMATCH",
                    f"data/{corpus} dir-digest {got} != rules-1 pin {want}")
            tbox_attest[corpus] = got
        tbox_attest["tbox"] = "kernel"
    else:
        base = ARM_TBOX[arm]
        pin_key = ARM_PIN_KEY[arm]
        want = (record.get("pins", {}).get("artifact_hashes", {})
                .get(pin_key))
        if not want:
            die("ERR_PIN_MISMATCH",
                f"registry record carries no pin {pin_key!r}")
        got_src = dir_digest(base)
        if got_src != want:
            die("ERR_PIN_MISMATCH",
                f"{base} dir-digest {got_src} != registered pin {want} "
                "(post-freeze drift of the substituted TBox, ASM-1413)")
        for corpus in ("axioms-v0", "axioms-kinship-v1"):
            src = base / corpus
            if not src.is_dir():
                die("ERR_INPUT_MISSING", f"{src} (run build_knull_tbox.py)")
            shutil.copytree(src, shadow / "data" / corpus)
        # staged copy must reproduce the source digest (copy integrity)
        staged_digest = {c: dir_digest(shadow / "data" / c)
                         for c in ("axioms-v0", "axioms-kinship-v1")}
        src_digest = {c: dir_digest(base / c)
                      for c in ("axioms-v0", "axioms-kinship-v1")}
        if staged_digest != src_digest:
            die("ERR_PIN_MISMATCH", "staged TBox bytes != source bytes")
        tbox_attest = {"tbox": base.name, "source_dir_digest": got_src,
                       "registered_pin": want,
                       "per_corpus_staged": staged_digest}
        # axioms-v0 non-kinship records are NOT pinned by certificate.py
        # (TBOX_PINNED lists 3 files) — nothing else to stage; the loader
        # refuses unknown kinds fail-closed if anything extra is passed.
    attestation = {
        "schema": "kot-knull-attest/1",
        "record_id": record.get("id"),
        "record_status": record.get("status"),
        "record_frozen_sha256": record.get("frozen_sha256"),
        "arm": arm,
        "harness_sha256": harness_shas,
        "shared_data_sha256": data_shas,
        "tbox": tbox_attest,
        "pinned_decision_payload_sha256": pins["decision_payload_sha256"],
    }
    return shadow, attestation


def run_arm(arm, pins, record):
    shadow, attestation = stage(arm, pins, record)
    cwd = shadow / "poc" / "rules-1"
    r = subprocess.run([sys.executable, "certificate.py"], cwd=cwd,
                       capture_output=True, text=True)
    out_json = cwd / "results" / "certificate-result.json"
    if r.returncode != 0 or not out_json.exists():
        # fail-closed: a crash is captured as a named load/run failure,
        # NEVER silently treated as collapse (ASM-1408); for k2 a parse/load
        # failure resolves INSTRUMENT-INVALID via /gates/k2_tbox_loads
        # (ASM-1412), never "successful discrimination".
        payload = {"arm": arm, "run_failed": True,
                   "returncode": r.returncode,
                   "stderr_tail": r.stderr[-2000:]}
    else:
        payload = json.loads(out_json.read_text())
        payload["arm"] = arm
        payload["run_failed"] = False
    payload["attestation"] = attestation
    if arm in ("k1", "k2"):
        payload["engine_identity_ablation_disclosure"] = \
            ENGINE_IDENTITY_DISCLOSURE
    dst = HERE / "results-incoming" / f"{arm}-certificate-result.json"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    return payload, dst


def k0_identity(payload, pins):
    got = (payload.get("determinism") or {}).get("decision_payload_sha256")
    ok = (not payload.get("run_failed") and
          got == pins["decision_payload_sha256"])
    rep = {
        "gate": "k0 staging-identity (PROPOSED-ASM-1405)",
        "pinned_decision_payload_sha256": pins["decision_payload_sha256"],
        "shadow_decision_payload_sha256": got,
        "certificate_result_pinned_sha256": pins["certificate_result_sha256"],
        "success_asm_1131_match": (payload.get("certificate_result", {})
                                   .get("success_asm_1131") is True),
        "attestation": payload.get("attestation"),
        "pass": bool(ok),
        "note": ("PASS => the shadow-staging instrument is inert: the "
                 "byte-identical harness over the byte-identical kernel "
                 "TBox reproduces the pinned RULES-1 decision payload "
                 "exactly. Pre-freeze-safe: this outcome is already pinned "
                 "in the frozen rules-1 record (no unblinding)."),
    }
    out = HERE / "results-incoming" / "k0-staging-identity.json"
    out.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    return rep


def parse_smoke(pins, record):
    """PARSE-ONLY smoke (PROPOSED-ASM-1414, review fix 4): load each
    substituted TBox through the PINNED twin_engine.load_tbox() and report
    load success + compiled-rule counts. NO closure is computed, NO item is
    evaluated, NO decision exists — the survival predicate stays blind
    (ASM-1409). Pre-freeze mandatory: a trivially-unparseable comparator
    must be caught BEFORE freeze, where it is an authoring bug, not after,
    where it could masquerade as an outcome."""
    report = {"schema": "kot-knull-parse-smoke/1",
              "note": ("parse-only: twin_engine.load_tbox over the staged "
                       "TBOX_PINNED set; no closure, no decisions, no "
                       "unblinding"),
              "arms": {}}
    for arm in ("k0", "k1", "k2"):
        shadow, attestation = stage(arm, pins, record)
        te_path = shadow / "poc" / "rules-1" / "twin_engine.py"
        spec = importlib.util.spec_from_file_location(
            f"twin_engine_smoke_{arm}", te_path)
        te = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(te)
        tbox_paths = [shadow / "data/axioms-v0/rel-mother.json",
                      shadow / "data/axioms-v0/rel-father.json",
                      shadow / "data/axioms-v0/class-man.json",
                      shadow / "data/axioms-kinship-v1"]
        entry = {"tbox": attestation["tbox"].get("tbox")
                 if isinstance(attestation["tbox"], dict) else None}
        try:
            tbox = te.load_tbox(tbox_paths)
            entry.update({
                "loaded": True,
                "n_known_urns": len(tbox.known),
                "n_rules": {"subPropertyOf": sum(len(v) for v in
                                                 tbox.subprop.values()),
                            "domain": len(tbox.domain),
                            "range": len(tbox.range),
                            "inverseOf": len(tbox.inverse),
                            "propertyChain": len(tbox.chains),
                            "coveredBy": len(tbox.covers),
                            "disjointWith": len(tbox.disjoint),
                            "functional": len(tbox.functional)},
                "error": None})
        except Exception as e:  # named, fail-closed, disclosed
            entry.update({"loaded": False, "n_known_urns": None,
                          "n_rules": None,
                          "error": "%s: %s" % (type(e).__name__, e)})
        report["arms"][arm] = entry
    report["pass"] = all(a["loaded"] for a in report["arms"].values())
    out = HERE / "inputs" / "parse-smoke.json"
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps(report, indent=1, sort_keys=True))
    if not report["pass"]:
        sys.exit(2)
    return report


def write_mocks(pins, record):
    """Synthetic k1/k2 payloads for BOTH branches — analysis validation
    only. Clearly labelled MOCK; never consumable as run results. Each mock
    carries a structurally-valid attestation block (built from the SAME
    registered pins a real run attests against) so the analysis attestation
    path is exercised; /analysis/mock stays true on any MOCK input."""
    def attest(arm):
        pin_key = ARM_PIN_KEY[arm]
        want = record["pins"]["artifact_hashes"][pin_key]
        return {"schema": "kot-knull-attest/1", "MOCK": True,
                "record_id": record.get("id"),
                "record_status": record.get("status"),
                "record_frozen_sha256": record.get("frozen_sha256"),
                "arm": arm,
                "harness_sha256": {
                    "certificate.py": pins["certificate_py"],
                    "twin_engine.py": pins["twin_engine_py"],
                    "mint_kinship.py": pins["mint_kinship_py"]},
                "shared_data_sha256": {
                    "nsk1-clutrr/items.jsonl": pins["items_jsonl"],
                    "nsk1-clutrr/world.jsonl": pins["world_jsonl"],
                    "world-v0/world.jsonl": pins["world_v0_jsonl"]},
                "tbox": {"tbox": ARM_TBOX[arm].name,
                         "source_dir_digest": want,
                         "registered_pin": want},
                "pinned_decision_payload_sha256":
                    pins["decision_payload_sha256"]}

    def cert(arm, success, gates, kill_a, stated, entailed, wl):
        return {"MOCK": True, "run_failed": False,
                "arm": arm, "attestation": attest(arm),
                "engine_identity_ablation_disclosure":
                    ENGINE_IDENTITY_DISCLOSURE,
                "certificate_result": {"success_asm_1131": success,
                                       "gates_asm_1163_all_pass": gates,
                                       "kill_a_fired": kill_a},
                "grid": {"C_dec_stated": stated, "C_dec_entailed": entailed,
                         "C_dec_entailed_counts": [0, 3680],
                         "C_dec_stated_counts": [1716, 1716]},
                "engine_soundness": {
                    "e3_vs_third_party_clutrr_gold": {
                        "correct": int(858 * min(1.0, wl + 0.01)), "n": 858,
                        "wilson_lb95": wl, "bar": 0.98,
                        "meets_bar": wl >= 0.98},
                    "e1_vs_held_out_world_v0_edge": {
                        "correct": 248, "n": 248, "wilson_lb95": 0.9847},
                    "e5_control_refusal": {"refused": 100, "n": 100,
                                           "wilson_lb95": 0.963}},
                "determinism": {"double_run_sha_match": True,
                                "decision_payload_sha256": "mock"}}
    mocks = {
        "survives": {"k1": cert("k1", True, True, False, 1.0, 0.0, 0.9955),
                     "k2": cert("k2", False, False, False, 0.4, 0.7, 0.02)},
        "collapses": {"k1": cert("k1", False, False, False, 1.0, 0.0, 0.61),
                      "k2": cert("k2", False, False, False, 0.4, 0.7, 0.02)},
    }
    # k2 load-failure branch (ASM-1412): must resolve INSTRUMENT-INVALID,
    # never "successful discrimination" — validated by the analysis mock run.
    k2_loadfail = {"MOCK": True, "run_failed": True, "arm": "k2",
                   "returncode": 1, "stderr_tail":
                   "EngineError ERR_AXIOM_GRAMMAR (synthetic mock)",
                   "attestation": attest("k2"),
                   "engine_identity_ablation_disclosure":
                       ENGINE_IDENTITY_DISCLOSURE}
    mocks["k2loadfail"] = {"k1": cert("k1", True, True, False,
                                      1.0, 0.0, 0.9955),
                           "k2": k2_loadfail}
    (HERE / "mock").mkdir(exist_ok=True)
    for branch, arms in mocks.items():
        for arm, payload in arms.items():
            p = HERE / "mock" / f"{branch}-{arm}-certificate-result.json"
            p.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    # phase-2b hostlift mock: EXACT registered shape — 858 paired items x
    # 3 seeds x all four (host_tbox x host_arm) cells = 10296 rows
    # (review fix: hostlift() rejects duplicates/missing rows), plus a
    # parent-analysis mock with /analysis/primary_pass true (activation
    # condition) and a deliberately-incomplete rows mock (must be rejected).
    rows = []
    for i in range(858):
        item = "mock-item-%04d" % i
        for seed in (0, 1, 2):
            for tbox in ("kernel", "knull"):
                for a in ("A1", "A3"):
                    base = 0.55 if a == "A1" else 0.72
                    correct = 1 if ((i * 7 + seed * 13 +
                                     (3 if a == "A3" else 0) +
                                     (1 if tbox == "kernel" else 0)) % 100
                                    < base * 100) else 0
                    rows.append({"item_id": item, "tbox": tbox, "arm": a,
                                 "seed": seed, "correct": correct})
    (HERE / "mock" / "hostlift-mock.json").write_text(
        json.dumps({"MOCK": True, "rows": rows}) + "\n")
    (HERE / "mock" / "hostlift-mock-incomplete.json").write_text(
        json.dumps({"MOCK": True, "rows": rows[:-5]}) + "\n")
    (HERE / "mock" / "parent-analysis-mock.json").write_text(
        json.dumps({"MOCK": True, "/analysis/primary_pass": True},
                   indent=1) + "\n")
    (HERE / "mock" / "parent-analysis-mock-fail.json").write_text(
        json.dumps({"MOCK": True, "/analysis/primary_pass": False},
                   indent=1) + "\n")
    print("mock payloads ->", HERE / "mock")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["k0", "k1", "k2"])
    ap.add_argument("--mock", action="store_true",
                    help="write synthetic k1/k2 payloads for analysis "
                         "validation (both branches + k2 load-failure)")
    ap.add_argument("--smoke", action="store_true",
                    help="PARSE-ONLY pre-freeze smoke (ASM-1414): "
                         "twin_engine.load_tbox over every arm's staged "
                         "TBox; no closure, no decisions, no unblinding")
    ap.add_argument("--registered", action="store_true",
                    help="REQUIRED for k1/k2: acknowledges the record "
                         "rules-1-knull-cert is FROZEN and this is the "
                         "registered runner role (ASM-1409)")
    args = ap.parse_args()
    if args.mock:
        write_mocks(load_pins(), load_self_record())
        return
    if args.smoke:
        parse_smoke(load_pins(), load_self_record())
        return
    if not args.arm:
        ap.error("--arm, --mock or --smoke required")
    pins = load_pins()
    record = load_self_record()
    if args.arm in ("k1", "k2") and not args.registered:
        die("ERR_NOT_REGISTERED",
            "arms k1/k2 are the registered runner role's (post-freeze); "
            "pre-freeze execution would unblind the primary endpoint "
            "(PROPOSED-ASM-1409). Use --registered only under the frozen "
            "record.")
    if args.arm in ("k1", "k2") and args.registered:
        if record.get("status") != "FROZEN":
            die("ERR_NOT_FROZEN",
                "rules-1-knull-cert.json status != FROZEN; refusing "
                "(fail-closed, ASM-1409)")
    payload, dst = run_arm(args.arm, pins, record)
    print("->", dst)
    if args.arm == "k0":
        rep = k0_identity(payload, pins)
        print(json.dumps(rep, indent=1))
        if not rep["pass"]:
            sys.exit(2)


if __name__ == "__main__":
    main()
