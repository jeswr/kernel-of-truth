#!/usr/bin/env python3
"""mock_e2e_carriers.py — $0 DRIVER-ACCEPTANCE proof for the carrier-
construction generator (build_carriers.py).

MOCK ONLY; regenerable evidence, never part of a real run. The driver's own
`--mock` validates the protocol wiring against D=8 STUB tables it fabricates
itself; THIS harness proves the seam the freeze-(A) completion adds: tables
built by the REAL generator (build_carriers.py `construct`, run against the
mock dump engine + mock tokenizer over the REAL (A)-time construction
manifest, at the FROZEN kaec_format geometry nc=96 / D=6144) are accepted by
the untouched f1k_driver.py end-to-end:

  gen_mock_fixtures (eval/trigger fixtures + config)
  -> SWAP the carriers dir for the generator's D=6144 tables
     (carriers/panel config from the generator's construction-report
      fragments; kot-corpus-hash recomputed for the swapped dir)
  -> load_config -> corpus pins -> phase_pilot (validate_panel: norm-match,
     derangement reconstruction, carrier identity — on the REAL tables)
  -> enforce_pretest_commits -> phase_guard -> validate_dose -> phase_test
  -> sidecar -> run record -> PINNED analysis/f1k.py ingest (exit 0).

Run:  python3 mock_e2e_carriers.py --carriers mock-out/carriers-6144 \
          --outdir mock-out/e2e-carriers
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import f1k_driver as drv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carriers", default="mock-out/carriers-6144")
    ap.add_argument("--outdir", default="mock-out/e2e-carriers")
    args = ap.parse_args()
    cdir_src = Path(args.carriers).resolve()
    report = json.loads((cdir_src / "construction-report.json")
                        .read_text("utf-8"))
    outdir = Path(args.outdir).resolve()
    shutil.rmtree(outdir, ignore_errors=True)
    outdir.mkdir(parents=True, exist_ok=True)

    print("== F1-K generator->driver acceptance mock ($0; stub engine; "
          "NOT a feasibility result) ==")
    cfg_path = drv.gen_mock_fixtures(outdir)
    cfg = json.loads(Path(cfg_path).read_text("utf-8"))

    # swap the fabricated D=8 stub carriers for the GENERATOR's tables
    cdir = outdir / "fixtures" / "data" / "f1k-carriers-v1"
    shutil.rmtree(cdir)
    cdir.mkdir(parents=True)
    for p in sorted(cdir_src.glob("*.kaec")):
        shutil.copy2(p, cdir / p.name)
    shutil.copy2(cdir_src / "norms.json", cdir / "norms.json")
    shutil.copy2(cdir_src / "construction-report.json",
                 cdir / "construction-report.json")

    def repath(p):
        return str(cdir / Path(p).name)

    carriers = report["carriers_config_fragment"]
    carriers["K"]["path"] = repath(carriers["K"]["path"])
    carriers["d0"]["path"] = repath(carriers["d0"]["path"])
    carriers["d2"]["path"] = repath(carriers["d2"]["path"])
    for s, m in carriers["d1-drng"].items():
        m["path"] = repath(m["path"])
    panel = report["pilot_panel_config_fragment"]
    for m in panel["members"].values():
        m["path"] = repath(m["path"])
    cfg["carriers"] = carriers
    cfg["pilot"]["panel"] = panel
    cfg["corpora"]["f1k-carriers-v1"]["expected_kot_corpus_hash"] = \
        drv.kot_corpus_hash(cdir)
    cfg["corpora"]["f1k-carriers-v1"]["provenance"] = \
        ("build_carriers.py `construct` output (REAL generator, mock dump "
         "engine, D=6144) — driver-acceptance fixture")
    cfg_path = outdir / "fixtures" / "mock-config.json"
    drv.write_json(cfg_path, cfg)

    cfg = drv.load_config(cfg_path)
    corpus_pins = drv.verify_corpus_pins(cfg, mock=True)
    assert len(corpus_pins) == 3
    # [R9-PROV] the generator's construction-report IS present here, so
    # the carrier-provenance gate byte-witnesses every configured table
    # against it (mode=mock disclosed) and yields the record witness pins.
    carrier_prov, carrier_pins = drv.verify_carrier_construction(
        cfg, mock=True)
    drv.write_json(outdir / "carrier-provenance.json", carrier_prov)
    assert carrier_prov["mode"] == "mock"
    assert "carrier-construction-report.mode-mock" in carrier_pins
    # the SAME mock tables must be REFUSED by the REAL-mode gate — the
    # re-review item-8 exploit (D=6144 mock carriers, 8 non-pinned
    # layers, ingested end-to-end) proven CLOSED on this very fixture
    try:
        drv.verify_carrier_construction(cfg, mock=False)
        real_ingest_refused = False
    except SystemExit as e:
        real_ingest_refused = (e.code == 2)
    print("[R9-PROV] REAL-mode ingest of these mock D=6144 carriers: %s"
          % ("REFUSED (fail-closed, as required)" if real_ingest_refused
             else "ACCEPTED — RE-REVIEW ITEM 8 REGRESSION"))
    ev = drv.load_eval_manifest(cfg["eval_manifest"])
    drv.verify_id_lists(cfg, ev)
    ledger = drv.Ledger(outdir, cfg)
    gold_dir = outdir / "mock-gold"
    gold_dir.mkdir(exist_ok=True)

    frozen = drv.phase_pilot(cfg, ev, outdir, ledger,
                             mock_gold_dir=gold_dir)
    print("pilot complete: frozen (L,g) = %s" % frozen)
    d3_deferred, replace_run, replace_gate = \
        drv.enforce_pretest_commits(cfg, outdir)
    guard_report = drv.phase_guard(cfg, ev, outdir, frozen, replace_run,
                                   ledger, mock_gold_dir=gold_dir)
    dose = drv.validate_dose(cfg["carriers"])
    passes = drv.main_arm_passes(d3_deferred, replace_run)
    rows_path, _ = drv.phase_test(cfg, ev, outdir, frozen, passes, ledger,
                                  mock_gold_dir=gold_dir)
    sidecar_path = drv.build_sidecar(cfg, outdir, guard_report, dose,
                                     ledger, d3_deferred, replace_gate,
                                     replace_run)
    rec_path = drv.emit_run_record(outdir, rows_path, sidecar_path,
                                   pins_observed=carrier_pins)  # [R9-PROV]
    proc = drv.run_analysis(rec_path)
    ok = proc.returncode == 0
    gates_all = False
    verdict = None
    if ok:
        out = json.loads(proc.stdout)
        gates_all = all(out["gates"].values())
        verdict = out.get("verdict", {}).get("verdict") \
            if isinstance(out.get("verdict"), dict) else out.get("verdict")
    side = json.loads(Path(sidecar_path).read_text("utf-8"))
    car = side["carriers"]
    K = drv.kaec_read(cfg["carriers"]["K"]["path"])
    # [ASM-2504] REGISTERED-GEOMETRY HARD GATE (layer re-freeze v3, re-review
    # pt 1): the oracle previously validated table_bytes against
    # car["layers"] self-consistently, so a STALE pre-built carriers dir
    # (76 layers, 3..78) could still pass. Bind the MASTER geometry
    # (construction report + master K table) to the registered union
    # EXACTLY (len==75, ids==3..77 — the real stale-76 guard); validate the
    # SIDECAR against the frozen-L PILOT-SELECTED subset actually spliced
    # (f1k_driver.py:2330 sets car["layers"] = km["nl"] of the
    # frozen["layers"] subset table — L1=1 / L2=4 / L3=75 are ALL
    # legitimate greens; a fixed ==75 here would be wrong).
    want_layers = list(drv.REGISTERED_SPLICE_LAYERS)
    assert want_layers == list(range(3, 78)) and len(want_layers) == 75, \
        "driver constant is not the ASM-2504 union 3..77 = 75"
    assert report["binding"]["layers"] == want_layers, \
        "STALE carriers dir: construction-report binding.layers != 3..77 (75)"
    assert K["layers"] == want_layers and K["nl"] == 75, \
        "STALE master table: .kaec layers != registered 3..77 (nl=75)"
    sel = list(frozen["layers"])   # pilot-selected splice subset (addendum 5)
    assert set(sel) <= set(want_layers) and car["layers"] == len(sel), \
        "sidecar carriers.layers != len(frozen-L pilot subset), or the " \
        "subset escapes the registered union 3..77"
    want_master_params = K["nc"] * K["nl"] * K["D"]
    summary = {
        "generator_tables_dir": str(cdir_src),
        "construction_seed": report["construction_seed"],
        "d0_algorithm": report["d0_algorithm"],
        "master_geometry": {"nc": K["nc"], "nl": K["nl"], "D": K["D"],
                            "layers": K["layers"],
                            "params": want_master_params},
        "sidecar_carriers": car,
        "sidecar_carriers_arithmetic_ok": (
            car["concepts"] == 96
            and car["params_added"] == 96 * car["layers"] * 6144
            and car["table_bytes"] == 16 + 4 * car["layers"]
            + 4 * car["params_added"]),
        "analysis_exit": proc.returncode,
        "analysis_gates_all_true": gates_all,
        "analysis_verdict": verdict,
        "carrier_provenance_mode": carrier_prov["mode"],   # [R9-PROV]
        "carrier_pins_on_record": sorted(carrier_pins),
        "real_mode_ingest_refused": real_ingest_refused,
    }
    drv.write_json(outdir / "acceptance-summary.json", summary)
    print(json.dumps(summary, indent=1, sort_keys=True))
    if not (ok and gates_all and real_ingest_refused):
        print("DRIVER-ACCEPTANCE: FAIL", file=sys.stderr)
        return 2
    print("DRIVER-ACCEPTANCE: PASS — generator tables (nc=96, D=6144) "
          "accepted by the untouched f1k_driver.py end-to-end; pinned "
          "analysis ingested the campaign (exit 0, all gates true)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
