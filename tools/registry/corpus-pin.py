#!/usr/bin/env python3
"""corpus-pin — reference implementation of the kot-corpus-hash/1 recipe.

    python3 tools/registry/corpus-pin.py [--root <repo>] <corpus> [<corpus> ...]
    python3 tools/registry/corpus-pin.py [--root <repo>] --record <exp-id>

Prints a JSON object {"_recipe": <the recipe string>, "<corpus>": <digest>, ...}
computed over data/<corpus>/ exactly as kot_common.CORPUS_RECIPE specifies.

With --record, recomputes every non-placeholder pin of the given registry
record's pins.corpus_hashes and reports match/mismatch per corpus (exit 1 on
any mismatch) — the auditor's one-command pin check.

History: the GNG-0-seed records carried digests that did not reproduce under
their own stated recipe (pin-generation defect, surfaced by the F1 exploratory
run seq 0, adjudicated by pre-sign-off correction c-2026-07-08). This tool IS
the recipe now; a pin that this tool cannot reproduce is wrong by definition.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kot_common as kc


def main():
    ap = argparse.ArgumentParser(description="Compute kot-corpus-hash/1 digests (fail-closed).")
    ap.add_argument("corpora", nargs="*", help="corpus directory names under data/")
    ap.add_argument("--root", default=None)
    ap.add_argument("--record", default=None, help="verify pins of registry/experiments/<id>.json instead")
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        if args.record:
            rec_path = os.path.join(root, "registry", "experiments", "%s.json" % args.record)
            with open(rec_path, "r", encoding="utf-8") as f:
                record = json.load(f)
            pins = record.get("pins", {}).get("corpus_hashes", {})
            recipe = pins.get("_recipe")
            out = {"experiment": args.record, "recipe_is_current": recipe == kc.CORPUS_RECIPE}
            bad = 0
            for name, want in sorted(pins.items()):
                if name == "_recipe":
                    continue
                if isinstance(want, str) and want.startswith(kc.PINNED_AT_INPUTS_PREFIX):
                    out[name] = {"state": "pinned-at-inputs (placeholder, ops amendment required)"}
                    continue
                got = kc.corpus_hash(root, name)
                match = got == want
                out[name] = {"pinned": want, "recomputed": got, "match": match}
                if not match:
                    bad += 1
            print(json.dumps(out, indent=2, sort_keys=True))
            sys.exit(1 if (bad or not out["recipe_is_current"]) else 0)

        if not args.corpora:
            ap.error("name at least one corpus, or use --record")
        out = {"_recipe": kc.CORPUS_RECIPE}
        for name in args.corpora:
            out[name] = kc.corpus_hash(root, name)
        print(json.dumps(out, indent=2, sort_keys=True))
    except kc.KotError as e:
        print("%s: %s" % (e.code, str(e).split(": ", 1)[1]), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
