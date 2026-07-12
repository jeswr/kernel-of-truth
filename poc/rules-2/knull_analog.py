#!/usr/bin/env python3
"""RULES-2 KNULL ANALOG — leg 1 ($0 CPU, deterministic): byte-equivalence of
the ENGINE-MATERIALISED training corpus under the KERNEL rules source vs the
KNULL plain-dictionary rules source.

Sibling campaign registry/experiments/rules-2-knull.json (DRAFT; the
MANDATORY kernel-specific-attribution analog demanded by the correctness-
track assessment and by the ASM-1138/1438 claim cap — 'engine-materialised
entailments are internalisable' is NEVER 'kernel-specific value' until the
knull-sourced-closure comparison exists). Build ASM block PROPOSED-ASM-1849..
1852 (poc/rules-2/asm-go-1847-1859.json; EMITTED, not registered).

WHAT THIS MEASURES (mechanical counts only — no verdict, no conclusion):
regenerate the rules-2 training-corpus EXAMPLES twice with the PINNED RULES-1
twin engine over the IDENTICAL deterministic component set (world-v0 kept
components + the seed-20260712 synthetic expansion, byte-identical builder
code paths in poc/rules-2/materialise_closure.py):

  side A  the KERNEL TBox (certificate.TBOX_PINNED verbatim — axioms-v0
          {rel-mother, rel-father, class-man} + data/axioms-kinship-v1),
          cross-checked example-by-example against the PINNED corpus bytes
          data/rules2-train/corpus.jsonl (kot-corpus-hash c46aaa4e...);
          ANY kernel-side mismatch is ERR_KERNEL_REGEN — fail closed.
  side B  the KNULL TBox (poc/rules-1-knull/inputs/tbox-knull — the
          plain-dictionary-compiled ruleset of rules-1-knull-cert,
          PROPOSED-ASM-1400..1404: same closed constraint grammar, same
          shared ABox vocabulary URNs for mother/father/man/woman, FRESH
          knull-profile URNs for every TBox-introduced term), dir digest
          pin-verified against registry/experiments/rules-1-knull-cert.json.

COMPARISON SURFACE: the TRAINING BYTES a fine-tune actually sees — per
example id: (context, question, answer, options). proof_sidecar equality is
reported SEPARATELY (it feeds only the B3 scaffold arm). If the two sides
are surface-equivalent on 100% of family-2 (entailed) cells, then the
knull-sourced fine-tune corpus IS the kernel-sourced corpus byte-for-byte,
the GPU treatment arms would be identical by construction, and the sibling
campaign's GPU leg is CONDITIONAL-VACUOUS: the kernel-vs-plain-dictionary
train-time attribution is settled mechanically at $0 (in the deflationary
direction — no 'kernel-specific value' claim is licensed by rules-2 either
way; the ASM-1438 claim-cap language is retired only in the sense that the
comparison now EXISTS and its answer is 'the sources are equivalent on this
closed inventory'). Any divergence instead defines exactly the item set the
sibling GPU leg fine-tunes on (matched corpus, c5k-vs-B2 contrast).

Usage:
  python3 poc/rules-2/knull_analog.py            # real, ~4 min CPU, $0
  python3 poc/rules-2/knull_analog.py --mock     # tiny components, seconds

Deterministic: no timestamps, no RNG beyond the pinned builder seeds; same
inputs -> byte-identical results/knull-analog-result.json. Fail-closed
ERR_* codes; this module states NO feasibility conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_RULES1 = os.path.join(_ROOT, "poc", "rules-1")
for p in (_HERE, _RULES1):
    if p not in sys.path:
        sys.path.insert(0, p)

import materialise_closure as mc  # noqa: E402  (pinned builder, byte-reused)

KNULL_TBOX = os.path.join(_ROOT, "poc", "rules-1-knull", "inputs",
                          "tbox-knull")
KNULL_CERT_RECORD = os.path.join(_ROOT, "registry", "experiments",
                                 "rules-1-knull-cert.json")
PINNED_CORPUS = os.path.join(_ROOT, "data", "rules2-train", "corpus.jsonl")
PINNED_CORPUS_HASH = ("c46aaa4ea2ffd56ef48c5cd0f2e379417fe763a5a0c140ce"
                      "706f0bdf65545cf1")
OUT_PATH = os.path.join(_HERE, "results", "knull-analog-result.json")

SURFACE_KEYS = ("context", "question", "answer", "options")


def verify_knull_pins():
    """Fail-closed: the knull TBox dir digest must match the value pinned in
    the rules-1-knull-cert DRAFT record (single source of truth)."""
    rec = json.load(open(KNULL_CERT_RECORD))
    ah = rec["pins"]["artifact_hashes"]
    key = next((k for k in ah if k.startswith("tbox-knull")), None)
    if key is None:
        raise SystemExit("ERR_PIN: no tbox-knull pin in %s"
                         % KNULL_CERT_RECORD)
    want = ah[key]
    got = mc.corpus_kot_hash(KNULL_TBOX)
    if got != want:
        raise SystemExit("ERR_PIN: tbox-knull dir digest %s != pinned %s"
                         % (got, want))
    man = json.load(open(os.path.join(KNULL_TBOX, "axioms-kinship-v1",
                                      "manifest.json")))
    for term in ("grandfather", "grandmother", "parent", "grandparent",
                 "person"):
        if term not in man["minted_urns"]:
            raise SystemExit("ERR_PIN: knull manifest missing minted urn %r"
                             % term)
    return {"tbox_knull_dir_digest": got, "pin_source": KNULL_CERT_RECORD,
            "knull_minted_urns": man["minted_urns"]}


def side_vocab(cert_mod, kin_manifest_minted):
    u = kin_manifest_minted
    vocab4 = {"mother": cert_mod.MOTHER, "father": cert_mod.FATHER,
              "grandfather": u["grandfather"],
              "grandmother": u["grandmother"]}
    urn2word = {v: k for k, v in vocab4.items()}
    urn2word[u["parent"]] = "parent"
    urn2word[u["grandparent"]] = "grandparent"
    return vocab4, urn2word, u


def build_examples(tbox_paths, cert_mod, minted, comps, side_name):
    from twin_engine import Closure, EngineError, load_tbox  # noqa: E402
    tbox = load_tbox(tbox_paths)
    vocab4, urn2word, u = side_vocab(cert_mod, minted)
    counts = {"components_conflict_excluded": 0,
              "components_engine_error": 0, "stated_query_skipped": 0,
              "e1_cell_skipped": 0, "e2_cell_skipped": 0,
              "refusal_cell_skipped": 0,
              "entity_ambiguous_skipped": 0,
              "entity_no_distractor_skipped": 0,
              "entity_support_not3_skipped": 0,
              "entity_support_closure_skipped": 0,
              "component_builder_abort": 0,
              "component_builder_abort_ids": []}
    examples = []
    for comp in comps:
        try:
            examples.extend(mc.component_examples(
                comp, tbox, cert_mod, Closure, EngineError, vocab4,
                urn2word, u, counts))
        except SystemExit as e:
            # An internal consistency abort (e.g. ERR_SUPPORT_DRIFT /
            # ERR_E1_GOLD) on the KERNEL side contradicts the pinned corpus
            # and must kill the run; on the KNULL side it is a REAL
            # divergence finding — counted and disclosed, never silent.
            if side_name == "kernel":
                raise
            counts["component_builder_abort"] += 1
            counts["component_builder_abort_ids"].append(
                "%s: %s" % (comp["id"], str(e)[:120]))
    return examples, counts


def surface(e):
    return {k: e[k] for k in SURFACE_KEYS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--out", default=OUT_PATH)
    args = ap.parse_args()

    kernel_pins = mc.verify_pins()
    knull_pins = verify_knull_pins()
    import certificate as cert_mod  # noqa: E402

    kin = json.load(open(os.path.join(_ROOT, "data", "axioms-kinship-v1",
                                      "manifest.json")))
    kernel_minted = kin["minted_urns"]

    # identical deterministic component set for BOTH sides (builder flow
    # verbatim from materialise_closure.build)
    n_fam = mc.MOCK["n_syn_fam"] if args.mock else mc.N_SYN_FAM
    forb = mc.eval_surface_names()
    wv0_comps, wv0_excluded = mc.load_world_v0_components(cert_mod)
    wv0_kept = [c for c in wv0_comps
                if not any(mc.name_collides(n, forb)
                           for n in c["names"].values())]
    comps = wv0_kept + mc.gen_synthetic_components(n_fam, cert_mod, forb)

    kernel_paths = cert_mod.TBOX_PINNED
    knull_paths = [os.path.join(KNULL_TBOX, "axioms-v0"),
                   os.path.join(KNULL_TBOX, "axioms-kinship-v1")]

    ker_ex, ker_counts = build_examples(kernel_paths, cert_mod,
                                        kernel_minted, comps, "kernel")
    knu_ex, knu_counts = build_examples(knull_paths, cert_mod,
                                        knull_pins["knull_minted_urns"],
                                        comps, "knull")

    # kernel-side anchor: regeneration must match the PINNED corpus bytes
    pinned_anchor = None
    if not args.mock:
        got_hash = mc.corpus_kot_hash(os.path.join(_ROOT, "data",
                                                   "rules2-train"))
        if got_hash != PINNED_CORPUS_HASH:
            raise SystemExit("ERR_PIN: data/rules2-train kot-corpus-hash %s "
                             "!= pinned %s" % (got_hash, PINNED_CORPUS_HASH))
        pinned = {}
        for ln in open(PINNED_CORPUS):
            e = json.loads(ln)
            pinned[e["id"]] = surface(e)
        regen = {e["id"]: surface(e) for e in ker_ex}
        if set(pinned) != set(regen):
            raise SystemExit("ERR_KERNEL_REGEN: id set drift vs pinned "
                             "corpus (%d pinned / %d regenerated)"
                             % (len(pinned), len(regen)))
        bad = [i for i in pinned if pinned[i] != regen[i]]
        if bad:
            raise SystemExit("ERR_KERNEL_REGEN: %d/%d kernel-side surfaces "
                             "differ from the pinned corpus (first: %s)"
                             % (len(bad), len(pinned), bad[0]))
        pinned_anchor = {"pinned_corpus_kot_hash": got_hash,
                         "n_examples": len(pinned),
                         "kernel_regen_byte_equal": True}

    # equivalence comparison (per family, per kind; family 2 is the leg's
    # decision surface — those are the B2/c5k training targets)
    ker_by_id = {e["id"]: e for e in ker_ex}
    knu_by_id = {e["id"]: e for e in knu_ex}
    only_kernel = sorted(set(ker_by_id) - set(knu_by_id))
    only_knull = sorted(set(knu_by_id) - set(ker_by_id))
    shared = sorted(set(ker_by_id) & set(knu_by_id))

    def cmp_block(pred):
        ids = [i for i in shared if pred(ker_by_id[i])]
        div = [i for i in ids
               if surface(ker_by_id[i]) != surface(knu_by_id[i])]
        proof_div = [i for i in ids
                     if ker_by_id[i]["proof_sidecar"]
                     != knu_by_id[i]["proof_sidecar"]]
        n = len(ids)
        return {"n_shared_ids": n,
                "n_surface_equal": n - len(div),
                "surface_equal_fraction": ((n - len(div)) / n) if n else None,
                "divergent_ids_sample": div[:20],
                "n_divergent": len(div),
                "n_proof_sidecar_divergent": len(proof_div),
                "proof_sidecar_divergent_sample": proof_div[:10]}

    fam2 = cmp_block(lambda e: e["family"] == 2)
    per_kind = {k: cmp_block(lambda e, k=k: e["family"] == 2
                             and e["kind"] == k)
                for k in ("chain", "cover", "typing")}
    fam13 = cmp_block(lambda e: e["family"] in (1, 3))

    fully_equivalent = (fam2["n_shared_ids"] > 0
                        and fam2["n_divergent"] == 0
                        and not only_kernel and not only_knull
                        and fam13["n_divergent"] == 0)

    result = {
        "artifact": "rules-2 knull-analog leg 1 — kernel-vs-knull rules-"
                    "source training-corpus byte-equivalence ($0 CPU, "
                    "deterministic; PROPOSED-ASM-1849..1852)",
        "mode": "MOCK" if args.mock else "REAL",
        "sibling_campaign": "registry/experiments/rules-2-knull.json",
        "claim_semantics": "mechanical counts ONLY. Surface-equivalence "
                           "does NOT validate the kernel; it settles the "
                           "train-time source-attribution question in the "
                           "deflationary direction (the plain-dictionary "
                           "source derives the identical training bytes on "
                           "this closed inventory, so no 'kernel-specific "
                           "value' claim can attach to any rules-2 "
                           "outcome). Divergence instead defines the "
                           "matched item set for the sibling GPU leg "
                           "(c5k-vs-B2). NEVER a hypothesis verdict.",
        "pins": {
            "kernel": {k: v for k, v in sorted(kernel_pins.items())}
            if isinstance(kernel_pins, dict) else str(kernel_pins),
            "knull": {"tbox_knull_dir_digest":
                      knull_pins["tbox_knull_dir_digest"],
                      "pin_source": os.path.relpath(
                          knull_pins["pin_source"], _ROOT)},
        },
        "component_set": {
            "n_world_v0_kept": len(wv0_kept),
            "n_world_v0_excluded_records": wv0_excluded,
            "n_synthetic_families": n_fam,
            "builder": "poc/rules-2/materialise_closure.py functions "
                       "byte-reused (no fork)"},
        "pinned_corpus_anchor": pinned_anchor,
        "counts_kernel": ker_counts,
        "counts_knull": knu_counts,
        "id_set": {"n_shared": len(shared),
                   "only_kernel": only_kernel[:20],
                   "n_only_kernel": len(only_kernel),
                   "only_knull": only_knull[:20],
                   "n_only_knull": len(only_knull)},
        "family2_equivalence": fam2,
        "family2_by_kind": per_kind,
        "family13_equivalence": fam13,
        "surface_keys_compared": list(SURFACE_KEYS),
        "fully_surface_equivalent": fully_equivalent,
        "gpu_leg_condition": ("CONDITIONAL-VACUOUS: sides byte-identical on "
                              "every shared surface — the knull-sourced "
                              "fine-tune corpus IS the kernel-sourced "
                              "corpus; the sibling GPU leg would train "
                              "byte-identical arms and is therefore vacuous "
                              "by construction (register, do not run)"
                              if fully_equivalent else
                              "GPU LEG REQUIRED: divergent items exist — "
                              "the sibling campaign fine-tunes the matched "
                              "knull-derived corpus (c5k) against B2 on the "
                              "divergence-bearing item set"),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    sha = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
    print("knull-analog leg 1 -> %s (sha256 %s)" % (args.out, sha))
    print("family-2 surface-equal fraction: %s   fully_equivalent: %s"
          % (fam2["surface_equal_fraction"], fully_equivalent))


if __name__ == "__main__":
    main()
