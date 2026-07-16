#!/usr/bin/env python3
"""run_e2e.py — component 8: the GREEN END-TO-END MOCK, $0.

10k mock synsets -> deterministic requests -> MOCK Batch -> MOCK GPT-5.6
drafts -> acceptance stack (encoder/validator loop + P8 family machinery) ->
immutable ModelDrafted minting / quarantine -> repair waves (R=2) ->
terminal accounting (§10.3: accepted + quarantined + provider_failed = N),
with the §6 idempotency crash-recovery, §10.2 budget reservation, kill-ladder
checkpoints, and P4a/P4b inline gates exercised and asserted in-flow.

Mid-run crash demo (window (b)): wave-0 job 2 is created at the provider but
the client 'dies' before recording the batchId; the r5 sweeper then adopts it
via exhaustive-pagination metadata.idempotency_key matching — asserted to
create ZERO duplicate batches.

Usage: nice -n 10 python3 pipeline/run_e2e.py [--n 10000] [--fresh]
"""

import argparse
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import frame_sample
import mock_batch
import mock_drafter
import accept as accept_mod
import orchestrator
from common import PipelineError

sys.path.insert(0, os.path.join(common.REPO_ROOT, "tools", "registry"))
from kot_common import wilson_lower_bound  # noqa: E402 — pinned Wilson LB impl
sys.path.insert(0, os.path.join(common.REPO_ROOT, "poc", "plainv5"))
import invoke_seat                          # noqa: E402
import check_family_disjoint as cfd         # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=common.SAMPLE_N)
    ap.add_argument("--fresh", action="store_true", help="wipe out/ mock state first")
    args = ap.parse_args()
    t_start = time.time()

    if args.fresh:
        for d in (common.STORE_DIR, common.PROVIDER_DIR,
                  os.path.join(common.OUT_DIR, "inputs")):
            if os.path.isdir(d):
                shutil.rmtree(d)
        for f in ("p4a-benchmark.json", "p4b-sizes.json", "e2e-report.json"):
            p = os.path.join(common.OUT_DIR, f)
            if os.path.exists(p):
                os.unlink(p)

    # ---- component 1: frame + sample (recomputed fail-closed every run, §1)
    if not os.path.exists(os.path.join(common.OUT_DIR, "worklist.jsonl")):
        frame_sample.build()
    else:
        # re-verify the pinned frame hash even when reusing the worklist
        frame, total, _ = frame_sample.load_frame()
        frame_sample.verify_frame(frame, total)
    print("[1] frame verified (%d, %s…) + worklist present" %
          (common.FRAME_COUNT, common.FRAME_SHA256[:12]))

    pilot = orchestrator.Pilot()
    n = pilot.load_worklist(limit=args.n)
    pilot.init_seat_ledger()
    drafter = mock_drafter.MockDrafter({ik: c["row"] for ik, c in pilot.by_idem.items()})
    print("[2] worklist loaded: %d rows claimed; seat ledger entry 0 = %s (family openai)"
          % (n, common.MODEL_SNAPSHOT_ID))

    crash_demo = {"ran": False}
    wave_jobs = []

    def run_wave(wave):
        members = pilot._members_for_wave(wave)
        if not members:
            return
        chunks = [members[i:i + common.MAX_JOB_REQUESTS]
                  for i in range(0, len(members), common.MAX_JOB_REQUESTS)]
        for idx, chunk in enumerate(chunks):
            if wave == 0 and idx == 1 and len(chunks) > 1 and not crash_demo["ran"]:
                # ---- §6 crash window (b) demo: provider accepts, client dies
                pilot.provider.crash_on_create = True
                jk_expected = common.job_key(wave, 0, chunk)
                try:
                    pilot.submit_job(wave, 0, chunk)
                    raise AssertionError("crash injection did not fire")
                except mock_batch.CrashInjected:
                    pass
                actions = pilot.reconcile()   # exhaustive pagination -> adopt
                adopted = [a for a in actions if a[0] == jk_expected and a[1].startswith("adopted:")]
                assert adopted, "sweeper failed to adopt the crashed job: %s" % actions
                assert pilot.provider.created_count(jk_expected) == 1, "duplicate paid submission!"
                for ik in chunk:
                    pilot.ledger.mark_submitted(ik, adopted[0][1].split(":", 1)[1], wave)
                jk, bid = jk_expected, adopted[0][1].split(":", 1)[1]
                crash_demo.update(ran=True, jobKey=jk, action=adopted[0][1],
                                  createdCount=pilot.provider.created_count(jk))
                print("    [crash-demo] window (b): %s -> %s; created_count=1 (no double spend)"
                      % (jk, adopted[0][1]))
            else:
                jk, bid = pilot.submit_job(wave, 0, chunk)
            pilot.poll_to_completion(drafter)
            cost = pilot.settle_and_process(jk, bid, wave)
            wave_jobs.append({"wave": wave, "jobKey": jk, "batchId": bid,
                              "members": len(chunk), "settledUSD": round(cost, 4)})
            print("    wave %d job %d/%d: %d members, settled $%.2f" %
                  (wave, idx + 1, len(chunks), len(chunk), cost))
            if wave == 0 and idx == 0:
                # ---- component 6: P4a/P4b inline on the FIRST batch (§7)
                pilot.p4b_measure()
                pilot.require_p4_gates()
                print("[6] P4a: %.0f rec/s, RSS %.0f MiB, 10k projection %.0fs (bound %ds) PASS; "
                      "P4b: record mean %.0f B, transcript mean %.0f B — PROCEED to remaining %d"
                      % (pilot.p4a["recordsPerSec"], pilot.p4a["maxRssBytes"] / 1048576.0,
                         pilot.p4a["projectedFull10kSec"], int(pilot.p4a["boundSec"]),
                         pilot.p4b["recordBytes"]["meanB"], pilot.p4b["transcriptBytes"]["meanB"],
                         n - len(chunk)))

    print("[3] wave 0 (draft) …")
    run_wave(0)
    for w in (1, 2):
        print("[3] wave %d (repair/retry) …" % w)
        run_wave(w)

    # ---- component 7: terminal accounting (§10.3 PROCEED precondition #0)
    acct = pilot.ledger.terminal_accounting(n)
    budget = pilot.ledger.budget()
    export = pilot.ledger.export_jsonl()
    manifest_path, manifest = pilot.store.write_manifest(extra={
        "cachePrefixHash": "sha256:" + pilot.builder.cache_prefix_hash,
        "validatorHash": pilot.builder._validator_hash(),
        "sampleManifest": "sample-manifest.json",
    })
    print("[7] terminal accounting: %s (accepted %d + quarantined %d + provider_failed %d = %d/%d)"
          % ("OK" if acct["ok"] else "FAIL", acct["counts"]["ACCEPTED"],
             acct["counts"]["QUARANTINED"], acct["counts"]["PROVIDER_FAILED"],
             acct["total"], n))
    if not acct["ok"]:
        raise PipelineError("ERR_TERMINAL_ACCOUNTING", json.dumps(acct))

    # ---- §10.3 endpoints (mock values; endpoint 4 = human leg, N/A in mock)
    accepted = acct["counts"]["ACCEPTED"]
    attempted = accepted + acct["counts"]["QUARANTINED"]
    alpha_lb = wilson_lower_bound(accepted / float(attempted), attempted)
    kappa = pilot.usage_totals["cached"] / float(pilot.usage_totals["input"])
    cost_per_accepted = budget["spentUSD"] / float(accepted)
    pf_frac = acct["counts"]["PROVIDER_FAILED"] / float(n)
    endpoints = {
        "1_acceptRateWilsonLB": {"value": round(alpha_lb, 4), "floor": common.ALPHA_FLOOR,
                                 "pass": alpha_lb >= common.ALPHA_FLOOR},
        "2_kappaCacheRead": {"value": round(kappa, 4), "floor": common.KAPPA_FLOOR,
                             "pass": kappa >= common.KAPPA_FLOOR},
        "3_costPerAccepted": {"value": round(cost_per_accepted, 5), "ceiling": common.COST_CEILING,
                              "pass": cost_per_accepted <= common.COST_CEILING},
        "4_humanPassRate": {"value": None, "floor": 0.60,
                            "pass": None, "note": "human leg NOT RUN — out of mock scope; blocks any real PROCEED"},
        "instrument_providerFailedFrac": {"value": round(pf_frac, 4),
                                          "bound": common.PROVIDER_FAILED_MAX_FRAC,
                                          "pass": pf_frac <= common.PROVIDER_FAILED_MAX_FRAC},
    }

    # ---- P8 machinery green run (§9.1) + consumer gate (§9.2)
    seat_findings = invoke_seat.verify(common.SEAT_LEDGER)
    fmap = invoke_seat.load_family_map(common.FAMILY_MAP)
    prov_findings, _ = cfd.check_provenance(manifest, fmap)
    shards = [os.path.join(common.RECORDS_DIR, f) for f in sorted(os.listdir(common.RECORDS_DIR))]
    gate_fail = accept_mod.check_status_eligibility_jsonl(shards, {"Explicated"})
    gate_pass = accept_mod.check_status_eligibility_jsonl(shards, {"ModelDrafted"})
    p8 = {
        "seatLedgerChain": "green" if not seat_findings else seat_findings,
        "provenanceAgreement": "green (authorFamily == resolve_family == openai)" if not prov_findings else prov_findings,
        "consumerGateExplicatedSlot": {"expected": "ERR_STATUS_INELIGIBLE fires",
                                       "fired": len(gate_fail), "pass": len(gate_fail) > 0},
        "consumerGateModelDraftedSlot": {"expected": "no findings",
                                         "findings": len(gate_pass), "pass": len(gate_pass) == 0},
    }
    ok_p8 = (not seat_findings and not prov_findings
             and p8["consumerGateExplicatedSlot"]["pass"] and p8["consumerGateModelDraftedSlot"]["pass"])
    print("[5] P8/family: seat chain %s; provenance %s; ERR_STATUS_INELIGIBLE fires on Explicated slot: %s"
          % ("green" if not seat_findings else "FAIL", "green" if not prov_findings else "FAIL",
             p8["consumerGateExplicatedSlot"]["pass"]))

    if not crash_demo["ran"] and n <= common.MAX_JOB_REQUESTS:
        crash_demo["skipped"] = "single-job smoke run; windows (a)+(b) covered by the P5 subprocess tests"
    mock_green = (acct["ok"] and (crash_demo["ran"] or "skipped" in crash_demo) and ok_p8
                  and pilot.p4a["pass"] and pilot.p4b["pass"]
                  and all(e["pass"] for k, e in endpoints.items() if e["pass"] is not None))
    report = {
        "schema": "kv1d-mock-e2e-report/1",
        "specRef": "docs/next/design/gpt56-draft-pipeline-large-kernel.md r5",
        "mode": "MOCK ($0; no network; no OpenAI call; pre-freeze artifact)",
        "n": n,
        "terminalAccounting": acct,
        "budget": budget,
        "killLadder": pilot.kill_ladder_log,
        "endpoints": endpoints,
        "p4a": pilot.p4a, "p4b": pilot.p4b,
        "crashRecoveryDemo": crash_demo,
        "jobs": wave_jobs,
        "p8": p8,
        "usageTotals": pilot.usage_totals,
        "ledgerExport": os.path.relpath(export, common.PKG_ROOT),
        "storeManifest": os.path.relpath(manifest_path, common.PKG_ROOT),
        "wallSec": round(time.time() - t_start, 1),
        "mockGreen": mock_green,
        "owner": "designer-20 (pipeline code); runner-1 (kb-pipeline-runner) operates",
    }
    common.write_json(os.path.join(common.OUT_DIR, "e2e-report.json"), report)
    print("\n=== E2E MOCK %s in %.0fs — spend $%.2f (cap $%.0f, reserved-then-settled), "
          "alpha_LB %.3f, kappa %.3f, $/accepted %.4f ===" %
          ("GREEN" if mock_green else "NOT GREEN", report["wallSec"], budget["spentUSD"],
           budget["capUSD"], alpha_lb, kappa, cost_per_accepted))
    return 0 if mock_green else 1


if __name__ == "__main__":
    sys.exit(main())
