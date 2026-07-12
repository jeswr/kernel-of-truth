#!/usr/bin/env python3
# RULES-1-KNULL-ABLATION — compile the knull-plain kinship TBox (arm k1) and
# its Sattolo-scrambled twin (arm k2).  CPU, ~$0, deterministic.
#
# Design anchors: docs/next/design/rules-1-knull-ablation.md;
# docs/next/arch/world-model-rules-engine.md MD-7 / c5 (PROPOSED-ASM-1138);
# PROPOSED-ASM-1400 (substitution scope), 1401 (definition provenance +
# contamination direction), 1402 (compilation protocol: every constraint
# carries a licensed_by quote from the plain definition text; the closed
# RULES-1 constraint inventory is the compilation TARGET GRAMMAR; filename
# mirroring against data/axioms-kinship-v1 + the three pinned axioms-v0 files
# is a HARNESS-COMPATIBILITY contract, never content copying), 1403 (knull
# URNs content-addressed under the kot-knull-def/1 profile — NOT kot-mol/1;
# no explication payload exists to mint from), 1404 (scramble construction:
# Sattolo derangement, seed 20260712, over constraint-slot fillers with
# record subjects fixed — identical topology, kinds, counts and byte-shape).
#
# SHARED-VOCABULARY BOUNDARY (ASM-1400): the ABox (nsk1-clutrr worlds,
# world-v0) states facts using the kernel URNs for mother/father/man/woman.
# Those identifiers are DATA SCHEMA shared by every arm; the ablation
# substitutes the DEFINITIONAL CONTENT (all constraints + every term the
# TBox itself introduces: parent, person, grandparent, grandfather,
# grandmother, minted fresh under the knull profile).
#
# Deterministic: same inputs -> same bytes.  No timestamps.  Randomness only
# in the seeded Sattolo derangement.  Fail-closed on any grammar violation.

import hashlib
import json
import random
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFS_PATH = HERE / "knull_kinship_defs.json"
OUT_KNULL = HERE / "inputs" / "tbox-knull"
OUT_SCRAM = HERE / "inputs" / "tbox-scrambled"
SATTOLO_SEED = 20260712  # pinned (PROPOSED-ASM-1404)

# Shared stated-vocabulary URNs (ABox data schema — kept in every arm).
MOTHER = "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua"
FATHER = "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi"
MAN = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
WOMAN = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"

B32 = "abcdefghijklmnopqrstuvwxyz234567"


def _b32(bs):
    out, bits, val = "", 0, 0
    for b in bs:
        val = (val << 8) | b
        bits += 8
        while bits >= 5:
            out += B32[(val >> (bits - 5)) & 31]
            bits -= 5
    if bits:
        out += B32[(val << (5 - bits)) & 31]
    return out


def mint_knull_urn(term, definition):
    """Content-addressed knull URN. Profile kot-knull-def/1 (ASM-1403):
    payload = JCS({definition, term}), NFC, sha2-256 multihash multibase32.
    Deliberately NOT kot-mol/1 — there is no explication identity payload."""
    payload = json.dumps({"definition": definition, "term": term},
                         sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"))
    s = unicodedata.normalize("NFC", payload)
    digest = hashlib.sha256(("kot-knull-def/1\n" + s).encode("utf-8")).digest()
    return "urn:kot:b" + _b32(bytes([0x12, 0x20]) + digest)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    defs_doc = json.loads(DEFS_PATH.read_text())
    d = defs_doc["definitions"]

    # knull-minted URNs for every term the TBox itself introduces
    u = {t: mint_knull_urn(t, d[t]) for t in
         ("parent", "person", "grandparent", "grandfather", "grandmother")}

    prov = {
        "module": "rules-1-knull-ablation tbox-knull (arm k1)",
        "design": "docs/next/design/rules-1-knull-ablation.md",
        "asm": ["PROPOSED-ASM-1400", "PROPOSED-ASM-1401",
                "PROPOSED-ASM-1402", "PROPOSED-ASM-1403"],
        "status": ("KNULL-PLAIN-SOURCED — compiled from plain-dictionary "
                   "definitions (knull register); NO NSM explication, NO "
                   "explicator/endorsement chain; every constraint carries "
                   "licensed_by quoting the definition span that licenses "
                   "it"),
    }

    def lic(term, span, reading):
        return {"term": term, "definition": d[term], "span": span,
                "reading": reading}

    # ---- the compiled records (filename contract mirrors the RULES-1
    #      TBOX_PINNED set; constraint CONTENT is licensed per span) ----
    records = {}

    # axioms-v0 substitutes (the three pinned files)
    records["axioms-v0/rel-mother.json"] = {
        "schema": "kot-axiom/1", "subject": MOTHER,
        "constraints": [
            {"kind": "functional",
             "licensed_by": lic("mother", "THE woman who has borne a child",
                                "definite article: at most one mother per "
                                "child (under stated differentFrom)")},
            {"kind": "range", "target": WOMAN,
             "licensed_by": lic("mother", "the WOMAN who has borne a child",
                                "a mother is a woman")}],
        "provenance": prov}
    records["axioms-v0/rel-father.json"] = {
        "schema": "kot-axiom/1", "subject": FATHER,
        "constraints": [
            {"kind": "functional",
             "licensed_by": lic("father", "THE male parent of a child",
                                "definite article: at most one father per "
                                "child (under stated differentFrom)")},
            {"kind": "range", "target": MAN,
             "licensed_by": lic("father", "the MALE parent",
                                "a father is male; the only male-sex-typed "
                                "class in the shared stated vocabulary is "
                                "man ('a human being of the male sex, fully "
                                "grown') — the adultness component is an "
                                "over-restriction risk carried by the "
                                "dictionary register, disclosed")}],
        "provenance": prov}
    records["axioms-v0/class-man.json"] = {
        "schema": "kot-axiom/1", "subject": MAN,
        "constraints": [
            {"kind": "disjointWith", "target": WOMAN,
             "licensed_by": {"term": "man/woman",
                             "definition": d["man"] + " || " + d["woman"],
                             "span": "of the MALE sex / of the FEMALE sex",
                             "reading": "male-sex and female-sex read as "
                                        "exclusive (disclosed stipulation, "
                                        "same class as the kernel's)"}}],
        "provenance": prov}

    # axioms-kinship-v1 substitutes
    records["axioms-kinship-v1/rel-parent.json"] = {
        "schema": "kot-axiom/1", "subject": u["parent"],
        "constraints": [
            {"kind": "domain", "target": u["person"],
             "licensed_by": lic("parent", "a PERSON'S father or mother",
                                "the one who has the parent is a person")},
            {"kind": "range", "target": u["person"],
             "licensed_by": lic("parent", "a person's FATHER OR MOTHER",
                                "a father/mother is a male/female parent of "
                                "a child; man and woman are defined as "
                                "human beings; person = 'a human being' => "
                                "the parent is a person")}],
        "provenance": prov}
    records["axioms-kinship-v1/class-person.json"] = {
        "schema": "kot-axiom/1", "subject": u["person"],
        "constraints": [
            {"kind": "classDeclaration",
             "licensed_by": lic("person", "a human being, whether man, "
                                "woman, or child", "class declaration")}],
        "provenance": prov}
    records["axioms-kinship-v1/sub-mother-parent.json"] = {
        "schema": "kot-axiom/1", "subject": MOTHER,
        "constraints": [
            {"kind": "subPropertyOf", "target": u["parent"],
             "licensed_by": lic("mother", "its female PARENT",
                                "a mother is a parent")}],
        "provenance": prov}
    records["axioms-kinship-v1/sub-father-parent.json"] = {
        "schema": "kot-axiom/1", "subject": FATHER,
        "constraints": [
            {"kind": "subPropertyOf", "target": u["parent"],
             "licensed_by": lic("father", "the male PARENT of a child",
                                "a father is a parent")}],
        "provenance": prov}
    records["axioms-kinship-v1/cover-parent.json"] = {
        "schema": "kot-axiom/1", "subject": u["parent"],
        "constraints": [
            {"kind": "coveredBy", "members": [MOTHER, FATHER],
             "licensed_by": lic("parent", "a person's father OR mother",
                                "the disjunction read as EXHAUSTIVE: every "
                                "parent is a father or a mother (disclosed "
                                "stipulation, same class as the kernel's "
                                "ASM-1121 covering premise)")}],
        "provenance": prov}
    records["axioms-kinship-v1/chain-grandparent.json"] = {
        "schema": "kot-axiom/1", "subject": u["grandparent"],
        "constraints": [
            {"kind": "propertyChain", "chain": [u["parent"], u["parent"]],
             "licensed_by": lic("grandparent",
                                "a PARENT of one's FATHER OR MOTHER",
                                "one's father-or-mother = one's parent "
                                "(parent def), so: x's parent's parent is "
                                "x's grandparent")},
            {"kind": "domain", "target": u["person"],
             "licensed_by": lic("grandparent", "of ONE'S father or mother",
                                "'one' = a person")},
            {"kind": "range", "target": u["person"],
             "licensed_by": lic("grandparent", "A PARENT of one's ...",
                                "a parent is a person (parent def range "
                                "reading)")}],
        "provenance": prov}
    records["axioms-kinship-v1/chain-grandfather.json"] = {
        "schema": "kot-axiom/1", "subject": u["grandfather"],
        "constraints": [
            {"kind": "propertyChain", "chain": [u["parent"], FATHER],
             "licensed_by": lic("grandfather",
                                "the FATHER of one's FATHER OR MOTHER",
                                "one's father-or-mother = one's parent "
                                "(parent def), so: the father of x's parent "
                                "is x's grandfather")},
            {"kind": "subPropertyOf", "target": u["grandparent"],
             "licensed_by": lic("grandfather",
                                "the FATHER of one's father or mother",
                                "a father is a parent (father def), and a "
                                "parent of one's father-or-mother is a "
                                "grandparent (grandparent def) => every "
                                "grandfather is a grandparent")},
            {"kind": "range", "target": MAN,
             "licensed_by": lic("grandfather", "the FATHER of ...",
                                "a grandfather is a father, and a father is "
                                "male (father def; man-class mapping as in "
                                "rel-father, disclosed)")}],
        "provenance": prov}
    records["axioms-kinship-v1/chain-grandmother.json"] = {
        "schema": "kot-axiom/1", "subject": u["grandmother"],
        "constraints": [
            {"kind": "propertyChain", "chain": [u["parent"], MOTHER],
             "licensed_by": lic("grandmother",
                                "the MOTHER of one's FATHER OR MOTHER",
                                "one's father-or-mother = one's parent "
                                "(parent def), so: the mother of x's parent "
                                "is x's grandmother")},
            {"kind": "subPropertyOf", "target": u["grandparent"],
             "licensed_by": lic("grandmother",
                                "the MOTHER of one's father or mother",
                                "a mother is a parent (mother def), and a "
                                "parent of one's father-or-mother is a "
                                "grandparent (grandparent def) => every "
                                "grandmother is a grandparent")},
            {"kind": "range", "target": WOMAN,
             "licensed_by": lic("grandmother", "the MOTHER of ...",
                                "a grandmother is a mother, and a mother is "
                                "a woman (mother def)")}],
        "provenance": prov}

    # ---- write k1 ----
    for rel, rec in sorted(records.items()):
        p = OUT_KNULL / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    manifest = {
        "schema": "kot-knull-tbox/1",
        "arm": "k1 knull-plain",
        "minted_urns": u,
        "mint_profile": "kot-knull-def/1 (PROPOSED-ASM-1403)",
        "definitions_source": {
            "path": "poc/rules-1-knull/knull_kinship_defs.json",
            "sha256": sha(DEFS_PATH)},
        "shared_vocabulary_urns": {"mother": MOTHER, "father": FATHER,
                                   "man": MAN, "woman": WOMAN},
        "asm": ["PROPOSED-ASM-1400", "PROPOSED-ASM-1401",
                "PROPOSED-ASM-1402", "PROPOSED-ASM-1403"],
    }
    (OUT_KNULL / "axioms-kinship-v1" / "manifest.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n")

    # ---- k2: Sattolo-scrambled twin (ASM-1404) ----
    # Derangement over constraint-slot FILLERS only; subjects fixed;
    # relation pool and class pool deranged separately.
    rel_pool = sorted([MOTHER, FATHER, u["parent"], u["grandparent"],
                       u["grandfather"], u["grandmother"]])
    cls_pool = sorted([MAN, WOMAN, u["person"]])
    rng = random.Random(SATTOLO_SEED)

    def sattolo(xs):
        xs = list(xs)
        for i in range(len(xs) - 1, 0, -1):
            j = rng.randrange(i)
            xs[i], xs[j] = xs[j], xs[i]
        return xs

    rel_map = dict(zip(rel_pool, sattolo(rel_pool)))
    cls_map = dict(zip(cls_pool, sattolo(cls_pool)))

    def scramble_slot(urn):
        return rel_map.get(urn) or cls_map.get(urn) or urn

    scram_prov = dict(prov)
    scram_prov["module"] = "rules-1-knull-ablation tbox-scrambled (arm k2)"
    scram_prov["status"] = (
        "SATTOLO-SCRAMBLED CONTENT-DESTRUCTION CONTROL (seed %d): the k1 "
        "records with every constraint-slot filler deranged (relation and "
        "class pools separately, subjects fixed) — identical topology, "
        "kinds, counts and token cost; licensed_by spans retained verbatim "
        "and now FALSE by construction (that is the point)" % SATTOLO_SEED)
    for rel, rec in sorted(records.items()):
        rec2 = json.loads(json.dumps(rec))  # deep copy
        rec2["provenance"] = scram_prov
        for c in rec2["constraints"]:
            if "target" in c:
                c["target"] = scramble_slot(c["target"])
            if "chain" in c:
                c["chain"] = [scramble_slot(x) for x in c["chain"]]
            if "members" in c:
                c["members"] = [scramble_slot(x) for x in c["members"]]
        p = OUT_SCRAM / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec2, indent=1, sort_keys=True) + "\n")
    scram_manifest = dict(manifest)
    scram_manifest["arm"] = "k2 scrambled"
    scram_manifest["sattolo_seed"] = SATTOLO_SEED
    scram_manifest["derangement_map"] = {
        "relations": {k: rel_map[k] for k in rel_pool},
        "classes": {k: cls_map[k] for k in cls_pool}}
    scram_manifest["asm"] = manifest["asm"] + ["PROPOSED-ASM-1404"]
    (OUT_SCRAM / "axioms-kinship-v1" / "manifest.json").write_text(
        json.dumps(scram_manifest, indent=1, sort_keys=True) + "\n")

    # ---- lint (compilation-fidelity gate input, ASM-1402) ----
    problems = []
    n_constraints = 0
    known = set(rel_pool) | set(cls_pool)
    for rel, rec in sorted(records.items()):
        for c in rec["constraints"]:
            n_constraints += 1
            if "licensed_by" not in c:
                problems.append(f"{rel}: constraint without licensed_by")
            else:
                span = c["licensed_by"]["span"].lower().replace("'", "")
                defn = c["licensed_by"]["definition"].lower()
                for w in [w for w in span.replace("/", " ").split()
                          if w not in ("...", "||", "the", "a", "of",
                                       "or", "one's", "ones")]:
                    if w not in defn.replace("'", ""):
                        problems.append(
                            f"{rel}: span word {w!r} not in definition")
            for slot in ([c.get("target")] + list(c.get("chain", [])) +
                         list(c.get("members", []))):
                if slot is not None and slot not in known:
                    problems.append(f"{rel}: unknown slot urn {slot}")
    lint = {
        "schema": "kot-knull-tbox-lint/1",
        "n_records": len(records),
        "n_constraints": n_constraints,
        "every_constraint_licensed": not any("licensed_by" in p
                                             for p in problems),
        "problems": problems,
        "pass": not problems,
        "kernel_slot_isomorphism_note": (
            "the compiled record/constraint topology is expected to land "
            "isomorphic to the kernel's — convergence of two authoring "
            "channels on the same closed target grammar is itself a datum, "
            "not copying; content licensing is carried per-constraint by "
            "licensed_by (ASM-1402)"),
    }
    (HERE / "inputs" / "lint-report.json").write_text(
        json.dumps(lint, indent=1, sort_keys=True) + "\n")

    # ---- inputs manifest with per-file shas ----
    files = {}
    for base in (OUT_KNULL, OUT_SCRAM):
        for p in sorted(base.rglob("*.json")):
            files[str(p.relative_to(HERE))] = sha(p)
    files["knull_kinship_defs.json"] = sha(DEFS_PATH)
    files["inputs/lint-report.json"] = sha(HERE / "inputs/lint-report.json")
    inputs_manifest = {
        "schema": "kot-knull-ablation-inputs/1",
        "builder": "poc/rules-1-knull/build_knull_tbox.py",
        "builder_sha256": sha(Path(__file__)),
        "sattolo_seed": SATTOLO_SEED,
        "minted_urns": u,
        "files": files,
        "lint_pass": lint["pass"],
    }
    (HERE / "inputs" / "manifest.json").write_text(
        json.dumps(inputs_manifest, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"minted_urns": u, "lint_pass": lint["pass"],
                      "n_problems": len(problems),
                      "n_files": len(files)}, indent=1))


if __name__ == "__main__":
    main()
