#!/usr/bin/env python3
# ENGINE-INF baseline-arm source compiler (design §1.3 [R1/R2]).
#
# Generates the MECHANICAL source modules (kot-axiom/1 record dirs) for the
# non-kernel arms into poc/engine-inference/arms/:
#   klemma-dom/    matched sense-split isolator, committed collapse
#                  (dominant minted sense's constraint set; ASM-2101 [R1])
#   klemma-union/  matched sense-split isolator, cautious collapse
#                  (agreement-or-nothing per slot; ASM-2101 [R1])
#   dword-dom/     word-level dictionary, SemCor-dominant-sense signature
#   dword-union/   word-level dictionary, union/LCS signature (untyped)
#   bwn/           WordNet-only sense-split arm (sentence-frame typing)
# plus arms/orbit-manifest.json — the C-SHUF 960-member within-lemma
# permutation ORBIT manifest (ASM-2114 [R2]; the ASM-1996 single-rotation
# kshuf/ arm is RETIRED and its directory removed).
# The kernel arm's module is AUTHORED, not generated: data/axioms-engineinf-v0/.
# No compiler here reads any gold field (PC-4 poisoned-gold canary).
#
# CUSTODY ORDER (design §2.5 custody clause 1, ASM-2104): this compiler —
# which pins the K-lemma modules and the orbit manifest, both deterministic
# functions of already-pinned bytes — runs BEFORE the SemCor holdout
# extraction ever touches the repo.

import json
import shutil
from pathlib import Path

from engineinf_lib import (WN, build_bwn_arm, build_dword_arms,
                           build_klemma_arms, kernel_inventory,
                           lemma_sense_urns, orbit_members,
                           orbit_sense_records, orbit_semantic_sha,
                           canon_sha, sha256_file, _kernel_sense_records)

HERE = Path(__file__).resolve().parent
ARMS = HERE / "arms"


def build_orbit_manifest():
    """Pin the C-SHUF orbit (ASM-2114 [R2], A_union frame per ASM-2120 [R3]):
    enumeration recipe, member count vs the build-derived factorial product,
    identity-reproduces-K, and the distinct-TBox (tie) structure."""
    import math
    inv = lemma_sense_urns()
    members = orbit_members()
    expect = 1
    for l in sorted(inv):
        expect *= math.factorial(len(inv[l]))
    senses = _kernel_sense_records()
    shas = [orbit_semantic_sha(orbit_sense_records(m, senses, inv))
            for m in members]
    pinned_sha = orbit_semantic_sha(
        [{"subject": u, "constraints": senses[u]["constraints"]}
         for u in sorted(senses)])
    return {
        "schema": "kot-engineinf-orbit/1",
        "role": ("C-SHUF control-evaluation orbit (NOT an arm; ASM-2114): "
                 "the complete within-lemma permutation orbit of the "
                 "per-sense domain/range constraint-set assignment, "
                 "identity and all fixed-point/tie members included. "
                 "Member semantics: sense at URN-order index i receives "
                 "the constraint set of sense at index perm[i]. Evaluation "
                 "frame at analysis: the orbit-invariant union A_union "
                 "(ASM-2120 [R3])."),
        "enumeration": ("per-lemma itertools.permutations lexicographic "
                        "(identity first), lemmas alphabetical, "
                        "itertools.product order; member 0 = identity = K"),
        "per_lemma_senses": {l: inv[l] for l in sorted(inv)},
        "n_members": len(members),
        "n_members_expected_factorial_product": expect,
        "members_sha256": canon_sha([{l: list(m[l]) for l in sorted(m)}
                                     for m in members]),
        "identity_semantic_sha256": shas[0],
        "pinned_kernel_semantic_sha256": pinned_sha,
        "identity_reproduces_k": shas[0] == pinned_sha,
        "n_distinct_tboxes": len(set(shas)),
        "n_tie_members": len(shas) - len(set(shas)),
    }


def main():
    ARMS.mkdir(exist_ok=True)
    # retire the ASM-1996 single-rotation kshuf arm (superseded by the orbit)
    kshuf_retired = (ARMS / "kshuf").is_dir()
    if kshuf_retired:
        shutil.rmtree(ARMS / "kshuf")
    wn = WN()
    klemma_meta = build_klemma_arms(wn, ARMS)
    dom_meta = build_dword_arms(wn, ARMS)
    bwn_meta = build_bwn_arm(wn, ARMS)
    orbit = build_orbit_manifest()
    if not orbit["identity_reproduces_k"]:
        raise RuntimeError("orbit identity member does not reproduce the "
                           "pinned kernel module (fail closed)")
    if orbit["n_members"] != orbit["n_members_expected_factorial_product"]:
        raise RuntimeError("orbit member count mismatch (fail closed)")
    (ARMS / "orbit-manifest.json").write_text(
        json.dumps(orbit, indent=1, sort_keys=True) + "\n")
    manifest = {
        "schema": "kot-engineinf-arms/2",
        "arms": ["K (data/axioms-engineinf-v0, authored)", "K-lemma-dom",
                 "K-lemma-union", "D-word-dom", "D-word-union", "B-wn"],
        "kshuf_retired": ("ASM-1996 single-rotation arm retired by "
                          "ASM-2114 [R2]; control = the 960-member orbit "
                          "(orbit-manifest.json)"),
        "klemma": klemma_meta,
        "dword_dom": dom_meta,
        "bwn_typed_relations": sum(1 for v in bwn_meta.values() if v),
        "bwn_total_relations": len(bwn_meta),
        "orbit_manifest_sha256": sha256_file(ARMS / "orbit-manifest.json"),
        "files": {str(p.relative_to(HERE)): sha256_file(p)
                  for p in sorted(ARMS.rglob("*.json"))
                  if p.name not in ("arm-manifest.json",
                                    "orbit-manifest.json")},
    }
    (ARMS / "arm-manifest.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"klemma_dominants": {l: v["concept"] for l, v in
                                           klemma_meta["dominants"].items()},
                      "klemma_union_survivors": klemma_meta["union_survivors"],
                      "dword_dom": {l: v["range"] for l, v in dom_meta.items()},
                      "bwn_typed": manifest["bwn_typed_relations"],
                      "orbit_members": orbit["n_members"],
                      "orbit_distinct_tboxes": orbit["n_distinct_tboxes"],
                      "identity_reproduces_k": orbit["identity_reproduces_k"],
                      "files": len(manifest["files"])},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
