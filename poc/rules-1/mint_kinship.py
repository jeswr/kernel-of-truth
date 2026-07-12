#!/usr/bin/env python3
# RULES-1 — mint data/axioms-kinship-v1/ (WMRE-1 C1 gap-fill).
#
# Design anchor: docs/next/arch/world-model-rules-engine.md §2.1 (C1), §4.1,
# PROPOSED-ASM-1126 (minting the parent relation + person class as
# data/axioms-kinship-v1, endorsed, never auto NL->OWL), PROPOSED-ASM-1121
# (coveredBy), maintainer approval issue #19 (MD-1: world-v0 + axioms-v0 +
# minted-kinship).
#
# What is minted:
#   concepts/  five AUTHORED molecule-style concept records (parent, person,
#              grandparent, grandfather, grandmother) with content-addressed
#              urn:kot: URNs under the exact molecules-v0 identity algorithm
#              (profile header "kot-mol/1\n", identity payload =
#              {semanticStatus, flag, groundingNote, groundingRefs,
#               moleculeDepth, axioms, partialExplication}, JCS/NFC, sha2-256
#              multihash multibase32 — reproduced byte-exactly against the
#              committed molecules-v0 URNs before any mint; fail closed).
#   *.json     kot-axiom/1 constraint records using the RULES-1 extension
#              kinds {subPropertyOf, coveredBy, propertyChain, domain} in
#              addition to the frozen kinds {functional, range}; the frozen
#              tools/axiom/kot_axiom.py engine REFUSES these new kinds by
#              design (fail-closed, ASM-1126 notes) — only the RULES-1 engine
#              implements them.
#
# EPISTEMIC STATUS: PROVISIONAL AUTHORED CONTENT. The five concept records are
# authored here by the experiment-engineering role to unblock the CPU
# certificate; they cite molecules-v0 explications as warrant. Registered
# as PROPOSED-ASM-1190 (emitted in poc/rules-1/RESULT.md); any registered GPU
# run must re-pin these bytes after endorsement. No feasibility conclusion.
#
# EXPLICATOR PASS 2026-07-11 (rules-1 endorsement): four concept records
# endorsed unchanged; 'grandparent' groundingNote REVISED ("the parent" ->
# "a parent" — the definite article implied a false uniqueness claim; a
# person ordinarily has two parents; contrast grandfather/grandmother, where
# "the father"/"the mother" IS licensed by rel-father/rel-mother functional
# axioms) and re-minted. All 8 axiom records endorsed as sound + correctly
# scoped (UNA ASM-1120 and covering ASM-1121 disclosed, not hidden).
# Maintainer endorsement + freeze re-pin (corpus-pin.py) still pending.
#
# Deterministic: same inputs -> same bytes. No timestamps, no randomness.

import hashlib
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "axioms-kinship-v1"

# ---------------------------------------------------------------- mint core --
# Reproduction of tools/mint/src/{jcs,hash,mint-core}.ts singleton path for
# stable-ref hand-authored corpora (docs/design-hash-input.md). Verified below
# against the committed molecules-v0 mother/father/man/woman URNs; any
# mismatch aborts (ERR_MINT_SELFCHECK).

PROFILE = "kot-mol/1\n"
IDENTITY_KEYS = ("semanticStatus", "flag", "groundingNote", "groundingRefs",
                 "moleculeDepth", "axioms", "partialExplication")
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


def jcs(obj):
    # RFC 8785 for the value space used here (strings/ints/lists/objects,
    # no floats): sorted keys, minimal separators, raw UTF-8.
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def mint_urn(record):
    payload = {k: record.get(k) if k != "partialExplication"
               else record.get(k, None) for k in IDENTITY_KEYS}
    s = unicodedata.normalize("NFC", jcs(payload))
    digest = hashlib.sha256((PROFILE + s).encode("utf-8")).digest()
    return "urn:kot:b" + _b32(bytes([0x12, 0x20]) + digest)


def selfcheck():
    expected = {
        "mother": "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua",
        "father": "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi",
        "man":    "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy",
        "woman":  "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq",
    }
    for name, want in expected.items():
        rec = json.loads((ROOT / "data" / "molecules-v0" / "molecules" /
                          f"{name}.json").read_text())
        got = mint_urn(rec)
        if got != want:
            raise SystemExit(f"ERR_MINT_SELFCHECK: {name}: {got} != {want}")


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ----------------------------------------------------------- authored content
# Molecule-style concept records. Prose follows the molecules-v0 grounding-
# note register; intra-corpus refs use stable urn:kinship-v1:* placeholders,
# cross-corpus refs stay stable urn:molecule-v0:* (molecules-v0 convention).

MOL = {"mother": "urn:molecule-v0:mother", "father": "urn:molecule-v0:father",
       "man": "urn:molecule-v0:man", "woman": "urn:molecule-v0:woman",
       "child": "urn:molecule-v0:child"}

CONCEPTS = [
    {
        "id": "urn:kinship-v1:parent",
        "label": "parent",
        "semanticStatus": "Molecule",
        "flag": "[m]",
        "groundingNote": (
            "someone of one kind: this someone is the "
            "{urn:molecule-v0:mother|mother} [m] of someone else, or this "
            "someone is the {urn:molecule-v0:father|father} [m] of someone "
            "else; there is no one of this kind who is not one of these two"),
        "groundingRefs": [MOL["mother"], MOL["father"]],
        "moleculeDepth": 4,
        "axioms": [],
        "partialExplication": None,
        "researchGrade": False,
        "notes": ("PROVISIONAL (rules-1, PROPOSED-ASM-1190): authored to fill "
                  "the named gap of docs/design-l3a-rules-engine-oracle.md §7 "
                  "successor task 3. The final clause is the covering claim "
                  "that PROPOSED-ASM-1121 registers as a stipulation. "
                  "Explicator pass 2026-07-11: ENDORSED unchanged — 'the "
                  "mother/father of someone else' is licensed by "
                  "functionality, and the covering clause is read "
                  "relation-level (to be someone's parent is to be that "
                  "someone's mother or that someone's father), the form "
                  "R-COVER-ELIM uses; it is a disclosed stipulation, not "
                  "claimed analytic. Maintainer endorsement still pending."),
        "corpusLemmas": ["parent", "parents"],
    },
    {
        "id": "urn:kinship-v1:person",
        "label": "person",
        "semanticStatus": "Molecule",
        "flag": "[m]",
        "groundingNote": (
            "someone; someone of this kind can be a "
            "{urn:molecule-v0:man|man} [m], can be a "
            "{urn:molecule-v0:woman|woman} [m], can be a "
            "{urn:molecule-v0:child|child} [m]; someone of this kind is not "
            "something of another kind (not an animal, not a thing)"),
        "groundingRefs": [MOL["man"], MOL["woman"], MOL["child"]],
        "moleculeDepth": 4,
        "axioms": [],
        "partialExplication": None,
        "researchGrade": False,
        "notes": ("PROVISIONAL (rules-1, PROPOSED-ASM-1190): authored to fill "
                  "the named 'person' gap (ASM-1126). Explicator pass "
                  "2026-07-11: ENDORSED unchanged — the can-be list states "
                  "possibility, not exhaustion (no over-constraint), and the "
                  "'not an animal, not a thing' contrast is standard NSM "
                  "folk-taxonomy prose that carries no minted axiom (the "
                  "kot-axiom/1 record is a bare classDeclaration). Maintainer "
                  "endorsement still pending."),
        "corpusLemmas": ["person", "people"],
    },
    {
        "id": "urn:kinship-v1:grandparent",
        "label": "grandparent",
        "semanticStatus": "Molecule",
        "flag": "[m]",
        "groundingNote": (
            "someone of one kind: this someone is a "
            "{urn:kinship-v1:parent|parent} [m] of someone else's "
            "{urn:kinship-v1:parent|parent} [m]"),
        "groundingRefs": ["urn:kinship-v1:parent"],
        "moleculeDepth": 5,
        "axioms": [],
        "partialExplication": None,
        "researchGrade": False,
        "notes": ("PROVISIONAL (rules-1, PROPOSED-ASM-1190): carrier of the "
                  "R-CHAIN target (WMRE-1 §3, E3). Explicator pass "
                  "2026-07-11: REVISED 'the parent' -> 'a parent' and "
                  "re-minted — the definite article implied a uniqueness "
                  "that is false under ordinary meaning (a person ordinarily "
                  "has two parents); no functionality axiom licenses it, "
                  "unlike 'the father'/'the mother' in the gendered records. "
                  "Endorsed as revised; maintainer endorsement still "
                  "pending."),
        "corpusLemmas": ["grandparent", "grandparents"],
    },
    {
        "id": "urn:kinship-v1:grandfather",
        "label": "grandfather",
        "semanticStatus": "Molecule",
        "flag": "[m]",
        "groundingNote": (
            "someone of one kind: a {urn:molecule-v0:man|man} [m]; this "
            "someone is the {urn:molecule-v0:father|father} [m] of someone "
            "else's {urn:kinship-v1:parent|parent} [m]"),
        "groundingRefs": [MOL["man"], MOL["father"], "urn:kinship-v1:parent"],
        "moleculeDepth": 5,
        "axioms": [],
        "partialExplication": None,
        "researchGrade": False,
        "notes": ("PROVISIONAL (rules-1, PROPOSED-ASM-1190): gendered E3 "
                  "target, answer-vocabulary word. Explicator pass "
                  "2026-07-11: ENDORSED unchanged — 'the father' is licensed "
                  "by rel-father (functional), and the chain "
                  "[parent, father] with range Man renders this prose "
                  "exactly. Maintainer endorsement still pending."),
        "corpusLemmas": ["grandfather", "grandpa", "granddad"],
    },
    {
        "id": "urn:kinship-v1:grandmother",
        "label": "grandmother",
        "semanticStatus": "Molecule",
        "flag": "[m]",
        "groundingNote": (
            "someone of one kind: a {urn:molecule-v0:woman|woman} [m]; this "
            "someone is the {urn:molecule-v0:mother|mother} [m] of someone "
            "else's {urn:kinship-v1:parent|parent} [m]"),
        "groundingRefs": [MOL["woman"], MOL["mother"], "urn:kinship-v1:parent"],
        "moleculeDepth": 5,
        "axioms": [],
        "partialExplication": None,
        "researchGrade": False,
        "notes": ("PROVISIONAL (rules-1, PROPOSED-ASM-1190): gendered E3 "
                  "target, answer-vocabulary word. Explicator pass "
                  "2026-07-11: ENDORSED unchanged — 'the mother' is licensed "
                  "by rel-mother (functional), and the chain "
                  "[parent, mother] with range Woman renders this prose "
                  "exactly. Maintainer endorsement still pending."),
        "corpusLemmas": ["grandmother", "grandma", "granny"],
    },
]

# Frozen concept URNs already in the estate (molecules-v0 minted table).
MOTHER = "urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua"
FATHER = "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi"
MAN = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
WOMAN = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"


def main():
    selfcheck()
    (OUT / "concepts").mkdir(parents=True, exist_ok=True)

    # 1. mint concepts
    urns = {}
    concept_files = {}
    for rec in CONCEPTS:
        urn = mint_urn(rec)
        urns[rec["label"]] = urn
        p = OUT / "concepts" / f"{rec['label']}.json"
        p.write_text(json.dumps(rec, indent=1, ensure_ascii=False,
                                sort_keys=True) + "\n")
        concept_files[rec["label"]] = p

    P, GP, GF, GM = (urns["parent"], urns["grandparent"],
                     urns["grandfather"], urns["grandmother"])
    PERSON = urns["person"]

    endorse_mol = {n: sha256_file(ROOT / "data" / "molecules-v0" /
                                  "molecules" / f"{n}.json")
                   for n in ("mother", "father", "man", "woman", "child")}
    endorse_new = {lbl: sha256_file(p) for lbl, p in concept_files.items()}

    # 2. kot-axiom/1 records (RULES-1 extension kinds; each cites the
    #    endorsing explication sha per the axioms-definitional-v0 precedent).
    def ax(name, subject, constraints, endorsement):
        rec = {"schema": "kot-axiom/1", "subject": subject,
               "constraints": constraints,
               "endorsement": endorsement,
               "provenance": {
                   "module": "axioms-kinship-v1",
                   "status": "PROVISIONAL-EXPLICATOR-ENDORSED-2026-07-11-PENDING-MAINTAINER-REPIN",
                   "design": "docs/next/arch/world-model-rules-engine.md §2.1 C1 / §4.1",
                   "asm": ["PROPOSED-ASM-1126", "PROPOSED-ASM-1190"]}}
        (OUT / f"{name}.json").write_text(
            json.dumps(rec, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
        return name

    files = []
    files.append(ax("rel-parent", P,
        [{"kind": "domain", "target": PERSON},
         {"kind": "range", "target": PERSON}],
        {"explication": "axioms-kinship-v1/concepts/parent.json",
         "sha256": endorse_new["parent"]}))
    files.append(ax("class-person", PERSON,
        [{"kind": "classDeclaration"}],
        {"explication": "axioms-kinship-v1/concepts/person.json",
         "sha256": endorse_new["person"]}))
    files.append(ax("sub-mother-parent", MOTHER,
        [{"kind": "subPropertyOf", "target": P}],
        {"explication": "molecules-v0/molecules/mother.json",
         "sha256": endorse_mol["mother"]}))
    files.append(ax("sub-father-parent", FATHER,
        [{"kind": "subPropertyOf", "target": P}],
        {"explication": "molecules-v0/molecules/father.json",
         "sha256": endorse_mol["father"]}))
    files.append(ax("cover-parent", P,
        [{"kind": "coveredBy", "members": [MOTHER, FATHER]}],
        {"explication": "axioms-kinship-v1/concepts/parent.json",
         "sha256": endorse_new["parent"],
         "asm": ["PROPOSED-ASM-1121"]}))
    files.append(ax("chain-grandparent", GP,
        [{"kind": "propertyChain", "chain": [P, P]},
         {"kind": "domain", "target": PERSON},
         {"kind": "range", "target": PERSON}],
        {"explication": "axioms-kinship-v1/concepts/grandparent.json",
         "sha256": endorse_new["grandparent"]}))
    files.append(ax("chain-grandfather", GF,
        [{"kind": "propertyChain", "chain": [P, FATHER]},
         {"kind": "subPropertyOf", "target": GP},
         {"kind": "range", "target": MAN}],
        {"explication": "axioms-kinship-v1/concepts/grandfather.json",
         "sha256": endorse_new["grandfather"]}))
    files.append(ax("chain-grandmother", GM,
        [{"kind": "propertyChain", "chain": [P, MOTHER]},
         {"kind": "subPropertyOf", "target": GP},
         {"kind": "range", "target": WOMAN}],
        {"explication": "axioms-kinship-v1/concepts/grandmother.json",
         "sha256": endorse_new["grandmother"]}))

    # 3. manifest
    manifest = {
        "corpus": "axioms-kinship-v1",
        "epistemic_status": ("PROVISIONAL AUTHORED CONTENT — explicator loop "
                             "COMPLETED 2026-07-11: parent, person, "
                             "grandfather, grandmother endorsed unchanged; "
                             "grandparent groundingNote revised ('the "
                             "parent' -> 'a parent', removing a false "
                             "uniqueness implicature) and re-minted, with "
                             "the dependent axiom records regenerated. All "
                             "8 kot-axiom/1 records endorsed sound and "
                             "correctly scoped (UNA PROPOSED-ASM-1120 and "
                             "covering PROPOSED-ASM-1121 disclosed "
                             "stipulations). Pending maintainer endorsement "
                             "+ freeze re-pin (PROPOSED-ASM-1190; re-run "
                             "corpus-pin.py). Deterministic re-mint: "
                             "poc/rules-1/mint_kinship.py."),
        "identityNote": ("Concept URNs content-addressed by MEANING under the "
                         "molecules-v0 algorithm: profile 'kot-mol/1', "
                         "identity payload {semanticStatus, flag, "
                         "groundingNote, groundingRefs, moleculeDepth, "
                         "axioms, partialExplication}, JCS/NFC, sha2-256 "
                         "multihash multibase32. Mint self-check reproduced "
                         "the committed mother/father/man/woman URNs "
                         "byte-exactly before minting."),
        "minted_urns": urns,
        "axiom_records": {f: sha256_file(OUT / f"{f}.json") for f in files},
        "concept_records": {lbl: {"file": f"concepts/{lbl}.json",
                                  "sha256": endorse_new[lbl],
                                  "urn": urns[lbl]} for lbl in urns},
        "extension_kinds": ["subPropertyOf", "coveredBy", "propertyChain",
                            "domain", "classDeclaration"],
        "extension_note": ("These kinds extend kot-axiom/1 per "
                           "PROPOSED-ASM-1126; the frozen "
                           "tools/axiom/kot_axiom.py refuses them "
                           "(ERR_AXIOM_UNIMPLEMENTED) — only the RULES-1 "
                           "engine (poc/rules-1/twin_engine.py) implements "
                           "them. Frozen kinds functional/range/disjointWith "
                           "continue to come from data/axioms-v0 unchanged."),
        "design_anchor": "docs/next/arch/world-model-rules-engine.md §2.1/§4.1",
        "asm": ["PROPOSED-ASM-1120", "PROPOSED-ASM-1121", "PROPOSED-ASM-1126",
                "PROPOSED-ASM-1190"],
    }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(urns, indent=1))
    print("OK: minted", len(CONCEPTS), "concepts,", len(files),
          "axiom records ->", OUT)


if __name__ == "__main__":
    sys.exit(main())
