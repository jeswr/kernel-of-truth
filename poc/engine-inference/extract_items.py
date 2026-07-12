#!/usr/bin/env python3
# ENGINE-INF mechanical item extractor + deterministic gold builder (G1-G4).
#
# Design: docs/next/design/engine-inference-under-typing.md §1.4-§1.5, §2.1;
# operationalisation constants ASM-1991/1992 (poc/engine-inference/
# asm-1990-2009.json). Consumes ONLY pinned third-party WN31 bytes + the
# kernel-v1 sense inventory (synset ids and excludedSenses membership — the
# G1 attachment identity, disclosed in the design §2.1). Emits:
#   results/items.json        the item bank (arm-neutral)
#   results/gold.json         the pinned gold (G1/G2/G3/G4) — NO compiler
#                             may read this file (poisoned-gold canary PC-4)
#   results/exclusions.json   every excluded candidate with a named reason
#
# $0, CPU-only, deterministic (double-run byte-identity checked by runner).

import json
from pathlib import Path

from engineinf_lib import WN, extract_items

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"


def main():
    OUT.mkdir(exist_ok=True)
    wn = WN()
    items, gold, exclusions, stats = extract_items(wn)
    kinds = {}
    for it in items:
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    payload = {"schema": "kot-engineinf-items/1", "items": items,
               "counts": {"total": len(items), **kinds},
               "extractor_stats": stats}
    (OUT / "items.json").write_text(json.dumps(payload, indent=1,
                                               sort_keys=True) + "\n")
    (OUT / "gold.json").write_text(json.dumps(
        {"schema": "kot-engineinf-gold/1",
         "gold_disclosure": ("G1 sense-by-attachment + G2 WN top-split "
                             "typing are third-party bytes; G3 anomaly "
                             "labels are CONSTRUCTED-RULE gold (design "
                             "§2.1, disclosed in every claim); G4 refusal "
                             "gold is excludedSenses membership with the "
                             "ASM-1997 scoring rule."),
         "gold": gold}, indent=1, sort_keys=True) + "\n")
    (OUT / "exclusions.json").write_text(json.dumps(
        {"schema": "kot-engineinf-exclusions/1", "exclusions": exclusions},
        indent=1, sort_keys=True) + "\n")
    print(json.dumps({"items": len(items), "kinds": kinds,
                      "extractor_stats": stats,
                      "exclusions": len(exclusions)}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
