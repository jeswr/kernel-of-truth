#!/usr/bin/env python3
"""Build the DefineIndex the mapper leg (mapper/src/defineTemplates.ts,
parseDefineQuestion) consumes: an annotation-label -> urn:kot: index + the
resolved relation-shorthand table, over the CURRENTLY-ENDORSED definitional
substrate ONLY (data/axioms-definitional-v0/ = {go, so, mondo}).

Design refs: memo §5.1 (label->URN index over onto-obo annotations.label +
synonyms, abstain on >1 URN); §3.3 (relation shorthand -> minted urn:kot: URN via
the pinned alias table + mint bridge, fail-closed). Normalisation mirrors the
mapper's normalize() byte-for-byte so index keys match extracted question spans.

Scope honesty: only {go, so, mondo} are endorsed today (CL/UBERON/PO/PATO/CHEBI
are minted-on-disk but carry NO definitional endorsement), so anatomy/cell items
resolving to those shards are OUT OF the licensed set BY CONSTRUCTION. Emitted in
the index meta.
"""
import json, re, os, sys, hashlib, collections

ROOT = "."
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))
import kot_axiom as K  # noqa: E402

ENDORSED_SHARDS = ["go.jsonl", "so.jsonl", "mondo.jsonl"]
OUT = os.path.join(ROOT, "poc", "b-cov-define-lane", "define-index.json")


def normalize(text):
    """Byte-mirror of mapper/src/defineTemplates.ts normalize()."""
    t = text.lower()
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"[?.!]+$", "", t).strip()
    return t


def main():
    bridge = K.load_mint_bridge(ROOT)

    # relationUrns: shorthand -> minted urn:kot: (fail-closed; drop any that do
    # not resolve to a minted concept in the mint bridge).
    relation_urns = {}
    rel_report = {}
    for shorthand, iri in sorted(K.PINNED_RELATION_ALIASES.items()):
        urn = bridge.get(iri)
        rel_report[shorthand] = {"iri": iri, "urn": urn}
        if urn is not None:
            relation_urns[shorthand] = urn

    # labelToUrns over the endorsed shards' minted concepts (label + synonyms).
    label_to_urns = collections.defaultdict(set)
    minted_concepts = 0
    per_shard = collections.Counter()
    for shard in ENDORSED_SHARDS:
        for rec in K.load_obo_shard(ROOT, shard):
            urn = bridge.get(rec.get("id"))
            if urn is None:
                continue
            minted_concepts += 1
            per_shard[shard] += 1
            ann = rec.get("annotations", {}) or {}
            surfaces = []
            lab = ann.get("label")
            if isinstance(lab, str) and lab.strip():
                surfaces.append(lab)
            for syn in (ann.get("synonyms") or []):
                if isinstance(syn, dict) and isinstance(syn.get("text"), str):
                    surfaces.append(syn["text"])
                elif isinstance(syn, str):
                    surfaces.append(syn)
            for s in surfaces:
                key = normalize(s)
                if key:
                    label_to_urns[key].add(urn)

    label_out = {k: sorted(v) for k, v in label_to_urns.items()}
    collisions = sum(1 for v in label_out.values() if len(v) > 1)

    payload = {
        "labelToUrns": label_out,
        "relationUrns": relation_urns,
        "meta": {
            "endorsed_shards": ENDORSED_SHARDS,
            "minted_concepts_indexed": minted_concepts,
            "per_shard_minted": dict(per_shard),
            "distinct_label_keys": len(label_out),
            "colliding_label_keys": collisions,
            "relation_resolution": rel_report,
            "note": "MEASURED-exploratory; index over CURRENTLY-endorsed "
                    "substrate {go,so,mondo} only (memo §5.1/§3.3).",
        },
    }
    buf = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(buf)
    print("define-index: %d minted concepts, %d distinct label keys, %d colliding, "
          "%d/%d relations resolved" % (
              minted_concepts, len(label_out), collisions,
              len(relation_urns), len(K.PINNED_RELATION_ALIASES)))
    print("per-shard minted:", dict(per_shard))
    print("sha256:", hashlib.sha256(buf.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
