#!/usr/bin/env python3
# ENGINE-INF baseline-arm source compiler (design §1.3).
#
# Generates the MECHANICAL source modules (kot-axiom/1 record dirs) for the
# non-kernel arms into poc/engine-inference/arms/:
#   dword-dom/     word-level dictionary, SemCor-dominant-sense signature
#   dword-union/   word-level dictionary, union/LCS signature (untyped)
#   bwn/           WordNet-only sense-split arm (sentence-frame typing)
#   kshuf/         shuffled-kernel control (derangement of the authored
#                  data/axioms-engineinf-v0/kernel module, ASM-1996)
# The kernel arm's module is AUTHORED, not generated: data/axioms-engineinf-v0/.
# No compiler here reads any gold field (PC-4 poisoned-gold canary).

import json
from pathlib import Path

from engineinf_lib import (WN, build_bwn_arm, build_dword_arms,
                           build_kshuf_arm, sha256_file)

HERE = Path(__file__).resolve().parent
ARMS = HERE / "arms"


def main():
    ARMS.mkdir(exist_ok=True)
    wn = WN()
    dom_meta = build_dword_arms(wn, ARMS)
    bwn_meta = build_bwn_arm(wn, ARMS)
    build_kshuf_arm(ARMS)
    manifest = {
        "schema": "kot-engineinf-arms/1",
        "dword_dom": dom_meta,
        "bwn_typed_relations": sum(1 for v in bwn_meta.values() if v),
        "bwn_total_relations": len(bwn_meta),
        "files": {str(p.relative_to(HERE)): sha256_file(p)
                  for p in sorted(ARMS.rglob("*.json"))
                  if p.name != "arm-manifest.json"},
    }
    (ARMS / "arm-manifest.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"dword_dom": dom_meta,
                      "bwn_typed": manifest["bwn_typed_relations"],
                      "bwn_total": manifest["bwn_total_relations"],
                      "files": len(manifest["files"])},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
