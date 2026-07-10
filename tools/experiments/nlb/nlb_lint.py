#!/usr/bin/env python3
"""nlb_lint — mechanical lints on the NLB phrasing corpora (instrument gate
G3, design doc docs/design-nl-boundary-l3a-parse-a5-nl.md sections 5.4 / 6.3).

    python3 tools/experiments/nlb/nlb_lint.py --vertical l3a \
        --arms-profile deterministic-r0 [--receipt]

ARMS PROFILE (FK-NLB-11 / ASM-0423, fail-closed — design doc section 14.8):
the EVAL-NO-ANSWER forced-substring exemption is lawful ONLY for records
whose every arm is deterministic and surface-blind (the l3a-parse / a5-nl
R0 arms). The DEFAULT profile is `model`: under it a NONEMPTY
waived_forced_substring list is itself a blocking finding (green=False),
because a model-based arm can read the answer off the question surface.
A record with no model arm must EXPLICITLY attest that by passing
`--arms-profile deterministic-r0` (the pinned invocation for l3a-parse /
a5-nl); under that profile waived qids stay exempt-and-disclosed. Reusing
this lint for any successor with a model arm therefore fails closed instead
of relying on prose.

Checks (each a named finding; ALL must pass for green):

  DEV corpus (always):
    DEV-COUNT        exactly 60 items, unique qids
    DEV-FRESH        every dev-entity URN absent from the world store AND
                     from every eval query (disjoint-from-scored, ASM-0145);
                     every dev phrasing references only dev entities (no
                     scored-eval entity surface occurs in any dev phrasing)
    DEV-FORM         UTF-8, single line, <= 200 chars, no urn: substring,
                     no grammar keyword leakage

  EVAL corpus (when eval.jsonl exists — the Opus input build):
    EVAL-COUNT       exactly one phrasing per included eval qid (600+270 l3a;
                     855+106 a5), no extras
    EVAL-FORM        UTF-8, single line, <= 200 chars
    EVAL-NO-URN      no 'urn:' substring
    EVAL-NO-GRAMMAR  no closed-grammar keyword leakage: 'op', 'direction',
                     'unique(', 'lookup(', 'instance(', JSON braces, or the
                     scaffold token 'inverse'
    EVAL-NO-ANSWER   no covered phrasing contains its own expected answer's
                     surface form (value slug/string) AFTER masking all
                     occurrences of the item's entity surfaces (longest-first,
                     the mask_template discipline). An answer surface that
                     leaks ONLY as a forced substring of the mandatory
                     verbatim entity identifier (ASM-0142) is EXEMPT and its
                     qid is DISCLOSED in the receipt field
                     waived_forced_substring — never silent (FK-NLB-11 /
                     ASM-0423, design doc section 14.4). Only answer surfaces
                     that SURVIVE the entity mask are flagged.
    EVAL-NO-MOCK     no phrasing byte-identical to a mock template
                     instantiation (poc/nlb-mock quarantine, section 10.6)
    EVAL-DIVERSITY   per covered family: >= min(6, n) distinct masked
                     templates AND no single masked template > 50% of the
                     family (FK-NLB-8 syntactic-diversity quota)
    EVAL-SCAFFOLD    per covered family: <= 50% of phrasings match the
                     canonical scaffold 'wh… the <label> of <entity>'
                     (FK-NLB-8)

  PROBE corpus (when probe.jsonl exists):
    PROBE-COUNT      exactly 60 items; every qid is a covered eval qid
    PROBE-NO-LABEL   no probe phrasing contains its item's relation/concept
                     label (verbatim, spaced or raw) — the no-label
                     constraint that defines the synonym probe
    PROBE-FORM       same form lints as EVAL

Raw findings only; the receipt (lint-receipt.json) is embedded in the run
bodies by nlb_instrument and gated by the pinned analysis scripts (G3).
"""

import argparse
import hashlib
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "axiom"))
sys.path.insert(0, _HERE)

import kot_axiom  # noqa: E402
import kot_code  # noqa: E402
import nlb_frontend  # noqa: E402
import gen_mock_phrasings  # noqa: E402

_ENT_PREFIX = "urn:kotw:v0:"
GRAMMAR_TOKENS = ("{", "}", '"op"', "direction", "unique(", "lookup(",
                  "instance(", " inverse ")


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def form_lint(findings, key, items):
    for r in items:
        t = r["text"]
        if "\n" in t or "\r" in t:
            findings.append("%s: %s multi-line" % (key, r["qid"]))
        if len(t) > 200:
            findings.append("%s: %s > 200 chars" % (key, r["qid"]))
        if "urn:" in t.lower():
            findings.append("%s: %s contains urn:" % (key, r["qid"]))
        low = " %s " % t.lower()
        for tok in GRAMMAR_TOKENS:
            if tok in low:
                findings.append("%s: %s grammar-token %r" % (key, r["qid"], tok))


def surfaces(urn):
    slug = urn[len(_ENT_PREFIX):].lower()
    return {slug, slug.replace("-", " ")}


def mask_template(text, ent_surfaces):
    low = re.sub(r"\s+", " ", text.lower().strip())
    for s in sorted(ent_surfaces, key=len, reverse=True):
        low = low.replace(s, "@")
    return low


def _has_surface(hay, s):
    """Word-boundary presence of surface s in already-lowercased hay (the
    EVAL-NO-ANSWER predicate; underscores/alphanumerics are word chars,
    hyphens and '@' are boundaries)."""
    return bool(re.search(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % re.escape(s), hay))


def run(root, vertical):
    findings = []
    waived = []  # EVAL-NO-ANSWER forced-substring exemptions (FK-NLB-11)
    base = os.path.join(root, "data", "nlb-phrasings-%s" % vertical)
    ev = load_jsonl(os.path.join(
        root, "data", "l3a-eval" if vertical == "l3a" else "a5-eval",
        "queries.jsonl"))
    included = [r for r in ev if r["family"] != "malformed"]
    if vertical == "l3a":
        axioms, world = kot_axiom.load_corpora(root)
        engine = kot_axiom.Engine(axioms, world)
    else:
        engine = kot_code.build_code_oracle(root).engine
    world_ents = set(engine.entities)
    eval_ents = set()
    for r in ev:
        q = r.get("query") or {}
        for k in ("subject", "entity", "of"):
            if isinstance(q.get(k), str):
                eval_ents.add(q[k])
    urn2label = nlb_frontend._load_labels(root)

    # ---------------- DEV
    dev = load_jsonl(os.path.join(base, "dev.jsonl"))
    dev_ents = [r["urn"] for r in
                load_jsonl(os.path.join(base, "dev-entities.jsonl"))]
    if len(dev) != 60 or len({r["qid"] for r in dev}) != 60:
        findings.append("DEV-COUNT: expected 60 unique dev items")
    for u in dev_ents:
        if u in world_ents or u in eval_ents:
            findings.append("DEV-FRESH: %s collides with a scored store/eval "
                            "identity" % u)
    scored_surf = set()
    for u in world_ents | eval_ents:
        if u.startswith(_ENT_PREFIX):
            scored_surf |= surfaces(u)
    for r in dev:
        low = " %s " % re.sub(r"\s+", " ", r["text"].lower())
        for s in scored_surf:
            if re.search(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % re.escape(s), low):
                findings.append("DEV-FRESH: %s mentions scored surface %r"
                                % (r["qid"], s))
    form_lint(findings, "DEV-FORM", dev)

    # ---------------- EVAL (input build; absent pre-build)
    eval_path = os.path.join(base, "eval.jsonl")
    checked = {"dev": True, "eval": False, "probe": False}
    if os.path.isfile(eval_path):
        checked["eval"] = True
        items = load_jsonl(eval_path)
        want = {r["qid"] for r in included}
        got = [r["qid"] for r in items]
        if sorted(got) != sorted(want) or len(got) != len(set(got)):
            findings.append("EVAL-COUNT: phrasing qids != included eval qids")
        form_lint(findings, "EVAL-FORM", items)
        by_qid = {r["qid"]: r for r in included}
        mock_texts = {p["text"] for p in
                      gen_mock_phrasings.generate(root, vertical)}
        fam_templates = {}
        for r in items:
            rec = by_qid.get(r["qid"])
            if rec is None:
                continue
            if r["text"] in mock_texts:
                findings.append("EVAL-NO-MOCK: %s equals a mock template"
                                % r["qid"])
            if rec["class"] == "covered":
                q = rec.get("query") or {}
                ent_urns = [q.get(k) for k in ("subject", "entity", "of")
                            if isinstance(q.get(k), str)]
                ent_surf = set()
                for u in ent_urns:
                    ent_surf |= surfaces(u)
                low_raw = re.sub(r"\s+", " ", r["text"].lower().strip())
                masked = mask_template(r["text"], ent_surf)
                # EVAL-NO-ANSWER masked forced-substring rule (FK-NLB-11 /
                # ASM-0423): flag an answer surface only if it SURVIVES masking
                # of the entity identifier; a leak removed entirely by the mask
                # is a forced substring of the mandatory verbatim identifier
                # (ASM-0142) -> EXEMPT and disclosed in waived_forced_substring.
                val = rec["expected"].get("value")
                vals = val if isinstance(val, list) else [val]
                ans_surf = set()
                for v in vals:
                    if isinstance(v, str) and v.startswith(_ENT_PREFIX):
                        ans_surf |= surfaces(v)
                leaked_masked = any(_has_surface(masked, s) for s in ans_surf)
                leaked_raw = any(_has_surface(low_raw, s) for s in ans_surf)
                if leaked_masked:
                    findings.append("EVAL-NO-ANSWER: %s leaks expected value"
                                    % r["qid"])
                elif leaked_raw:
                    waived.append(r["qid"])
                fam_templates.setdefault(rec["family"], []).append(
                    (masked, q, r["text"]))
        for fam, rows in fam_templates.items():
            n = len(rows)
            tpls = [t for t, _q, _x in rows]
            distinct = len(set(tpls))
            if distinct < min(6, n):
                findings.append("EVAL-DIVERSITY: family %s has %d distinct "
                                "templates over %d items" % (fam, distinct, n))
            most = max(tpls.count(t) for t in set(tpls))
            if n >= 2 and most > 0.5 * n:
                findings.append("EVAL-DIVERSITY: family %s dominant template "
                                "%d/%d > 50%%" % (fam, most, n))
            scaffold = 0
            for tpl, q, _x in rows:
                lab = urn2label.get(q.get("rel") or q.get("concept"), "")
                lab = (lab or "").replace("-", " ")
                if lab and re.search(
                        r"^(?:who|what|which|list|how many|where)\b.*\bthe %s"
                        r"(?: of)? @" % re.escape(lab.split(" of")[0]), tpl):
                    scaffold += 1
            if n >= 2 and scaffold > 0.5 * n:
                findings.append("EVAL-SCAFFOLD: family %s canonical scaffold "
                                "%d/%d > 50%%" % (fam, scaffold, n))

    # ---------------- PROBE (descriptive synonym probe; optional)
    probe_path = os.path.join(base, "probe.jsonl")
    if os.path.isfile(probe_path):
        checked["probe"] = True
        probe = load_jsonl(probe_path)
        covered_qids = {r["qid"] for r in included if r["class"] == "covered"}
        if len(probe) != 60:
            findings.append("PROBE-COUNT: expected 60, got %d" % len(probe))
        by_qid = {r["qid"]: r for r in included}
        for r in probe:
            if r["qid"] not in covered_qids:
                findings.append("PROBE-COUNT: %s is not a covered eval qid"
                                % r["qid"])
                continue
            q = by_qid[r["qid"]].get("query") or {}
            lab = urn2label.get(q.get("rel") or q.get("concept"))
            if lab:
                low = r["text"].lower()
                if lab in low or lab.replace("-", " ") in low:
                    findings.append("PROBE-NO-LABEL: %s contains label %r"
                                    % (r["qid"], lab))
        form_lint(findings, "PROBE-FORM", probe)

    return findings, checked, sorted(waived)


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", required=True, choices=("l3a", "a5"))
    ap.add_argument("--root", default=_ROOT)
    ap.add_argument("--receipt", action="store_true")
    ap.add_argument("--arms-profile", choices=("model", "deterministic-r0"),
                    default="model",
                    help="FK-NLB-11/ASM-0423 fail-closed guard (design doc "
                         "14.8): under the DEFAULT 'model' profile a "
                         "nonempty waived_forced_substring list BLOCKS "
                         "green (a model arm can read the answer off the "
                         "question); pass 'deterministic-r0' only for a "
                         "record whose every arm is deterministic and "
                         "surface-blind (the pinned l3a-parse / a5-nl "
                         "invocation)")
    args = ap.parse_args()
    findings, checked, waived = run(args.root, args.vertical)
    if args.arms_profile == "model" and waived:
        findings.append(
            "EVAL-NO-ANSWER: %d waived_forced_substring qid(s) are direct "
            "answer leaks under a model-based arm (FK-NLB-11/ASM-0423: the "
            "forced-substring exemption is lawful ONLY for deterministic "
            "surface-blind arms) — exclude or re-phrase them, or attest "
            "--arms-profile deterministic-r0" % len(waived))
    green = not findings
    out = {"schema": "nlb-lint-receipt/1", "vertical": args.vertical,
           "green": green, "checked": checked, "findings": findings,
           "waived_forced_substring": waived}
    print(json.dumps(out, indent=1, sort_keys=True))
    if args.receipt:
        base = os.path.join(args.root, "data",
                            "nlb-phrasings-%s" % args.vertical)
        pins = {}
        for name in ("dev.jsonl", "dev-entities.jsonl", "eval.jsonl",
                     "probe.jsonl"):
            p = os.path.join(base, name)
            if os.path.isfile(p):
                pins[name] = file_sha256(p)
        out["pins"] = pins
        rp = os.path.join(base, "lint-receipt.json")
        with open(rp, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
        print("receipt -> %s" % rp, file=sys.stderr)
    sys.exit(0 if green else 1)


if __name__ == "__main__":
    main()
