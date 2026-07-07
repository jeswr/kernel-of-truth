#!/usr/bin/env python3
"""E2 re-analysis input builder: deterministic explication-AST -> text renderer.

LABELLED POST-HOC RE-ANALYSIS (design-review change 1, notes/panel-kernel-
design-review.md 3.2; beads kernel-of-truth-qha + kernel-of-truth-avt).
The original pre-registered E2 verdict stands as reported
(poc/e2/results-incoming/20260707-091305-modal/verdict-e2.md); this directory
adds sentence-embedding baseline RDMs and polarity-stratified reporting
ALONGSIDE it, never in place of it.

This script emits poc/e2/reanalysis/inputs/reanalysis-texts.json:
  - ids/words: the 51 pre-registered analysis items, order-pinned to
    poc/e2/inputs/items.json (fail closed on any drift);
  - glossTexts: the kernel-v0 record `gloss` field verbatim (the dictionary-
    style definition text the design review names as the deflationary
    baseline source);
  - explicationTexts: a DETERMINISTIC plain-English rendering of each
    kot-ast/1 explication tree (renderer below; no RNG, no styles — this is
    deliberately NOT poc/e4/harness/realizer.ts, whose style/rng variation
    exists for training-data purposes; here one canonical string per tree is
    required so the RDM is a pure function of the AST);
  - notCount / hasNot: per-item count of NOT operators in the explication —
    the X3 polarity signal used for the pre-registered "interpretation
    conditioned on X3" stratification (operationalisation documented in
    README.md; X3's edit classes are per-concept mutations, so the corpus-
    level stratum is NOT-presence in the authored explication);
  - encoderContentHash / corpusPin copied from items.json so the pin-
    coherence discipline of poc/e2/inputs carries over.

RENDERER SPEC (kot-ast/1 -> text), version reanalysis-renderer/1:
  - referent i named by kind: SomeoneRef "person i", SomethingRef "thing i",
    TimeRef "time i", PlaceRef "place i", ClauseRef "fact i";
  - frames: WhenTrue -> "this is true of X when: ...";
    InstanceSchema -> "X is this: ..."; RelationalSchema ->
    "this is about X and Y: ...";
  - top-level clauses joined with "; ", quote clauses with "; ";
  - operators: NOT c -> "it is not true that C"; CAN -> "it can be that C";
    MAYBE -> "maybe C"; IF a b -> "if A, then B"; BECAUSE a b ->
    "because A, B"; WHEN a b -> "when A, B"; LIKE a b -> "A is like B";
    AFTER/BEFORE anchor scope -> "after/before ANCHOR, SCOPE";
  - predicates: fixed per-frame templates (see _render_pred), adjuncts
    appended in the fixed order time, duration, place, manner;
  - SP: "[det] [quant] [mods] head [that is a kind of/part of ...]
    [such that: CLAUSE] [(NAME)]" — bind introduces the referent name in
    parentheses; primes lowercased, first ~-variant, hyphens -> spaces;
  - fail closed (SystemExit ERR_RENDER) on any node shape outside the
    grammar actually exercised by kernel-v0 (audited 2026-07-07: all 19
    predicate frames minus WORDS, 9 operators, all filler kinds, 3 frames).

Run:  python3 poc/e2/reanalysis/build_texts.py
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ITEMS_PATH = os.path.join(REPO, "poc", "e2", "inputs", "items.json")
CONCEPTS_DIR = os.path.join(REPO, "data", "kernel-v0", "concepts")
OUT_PATH = os.path.join(HERE, "inputs", "reanalysis-texts.json")

RENDERER_VERSION = "reanalysis-renderer/1"

REF_NOUN = {
    "SomeoneRef": "person",
    "SomethingRef": "thing",
    "TimeRef": "time",
    "PlaceRef": "place",
    "ClauseRef": "fact",
}

DET_TEXT = {"THIS": "this", "THE-SAME": "the same", "OTHER~ELSE~ANOTHER": "another", "SOME": "some"}
QUANT_TEXT = {"ONE": "one", "TWO": "two", "SOME": "some", "ALL": "all", "MUCH~MANY": "many", "LITTLE~FEW": "few"}
INTENSIFIER_TEXT = {"VERY": "very", "MORE": "more"}


def die(msg: str) -> None:
    raise SystemExit(f"ERR_RENDER: {msg}")


def prime_text(prime: str) -> str:
    """Lowercase, first ~-variant, hyphens -> spaces (mirrors the convention
    of poc/e2/harness/glossRdm.ts's surface-word derivation)."""
    return prime.split("~")[0].lower().replace("-", " ")


class Renderer:
    def __init__(self, explication: dict):
        self.refs = {r["index"]: r["refKind"] for r in explication.get("referents", [])}
        self.expl = explication

    def ref_name(self, index: int) -> str:
        kind = self.refs.get(index)
        if kind is None:
            die(f"undeclared referent index {index}")
        return f"{REF_NOUN[kind]} {index}"

    # ---- fillers ----
    def filler(self, f: dict) -> str:
        k = f.get("kind")
        if k == "ref":
            return self.ref_name(f["index"])
        if k == "prime":
            return prime_text(f["prime"])
        if k == "concept":
            return f["id"].split(":")[-1].replace("-", " ")
        if k == "sp":
            return self.sp(f)
        if k == "clause":
            return self.clause(f["clause"])
        if k == "quote":
            return '"' + "; ".join(self.clause(c) for c in f["clauses"]) + '"'
        if k == "temporal":
            word = {"AFTER": "after", "BEFORE": "before"}.get(f["op"]) or die(f"temporal op {f['op']}")
            return f"{word} {self.filler(self._as_filler(f['anchor']))}"
        die(f"unknown filler kind {k!r}")

    @staticmethod
    def _as_filler(node: dict) -> dict:
        # temporal anchors are SP | RefMention | PrimeFiller — already fillers
        return node

    # ---- substantive phrases ----
    def sp_head(self, head: dict) -> str:
        hk = head.get("kind")
        if hk == "primeHead":
            return prime_text(head["prime"])
        if hk in ("kindFrame", "partFrame"):
            of = head["of"]
            of_text = self.filler(of) if of.get("kind") in ("sp", "ref", "concept") else die(
                f"kind/part 'of' filler {of.get('kind')!r}")
            rel = "a kind of" if hk == "kindFrame" else "a part of"
            return f"{rel} {of_text}"
        if hk == "refHead":
            return self.ref_name(head["index"])
        if hk == "conceptHead":
            return head["id"].split(":")[-1].replace("-", " ")
        die(f"unknown SP head kind {hk!r}")

    def sp(self, sp: dict) -> str:
        parts: list[str] = []
        if "det" in sp:
            parts.append(DET_TEXT.get(sp["det"]) or die(f"det {sp['det']}"))
        if "quant" in sp:
            parts.append(QUANT_TEXT.get(sp["quant"]) or die(f"quant {sp['quant']}"))
        for m in sp.get("mods", []):
            word = m["mod"].lower()
            if "intensifier" in m:
                word = f"{INTENSIFIER_TEXT[m['intensifier']]} {word}"
            parts.append(word)
        parts.append(self.sp_head(sp["head"]))
        text = " ".join(parts)
        if "restrictedBy" in sp:
            text += f" such that: {self.clause(sp['restrictedBy'])}"
        if "bind" in sp:
            text += f" ({self.ref_name(sp['bind'])})"
        return text

    # ---- clauses ----
    def clause(self, c: dict) -> str:
        t = c.get("type")
        if t == "pred":
            return self.pred(c)
        if t == "op":
            return self.op(c)
        die(f"unknown clause type {t!r}")

    def op(self, c: dict) -> str:
        op, args = c["op"], c["args"]

        def arg(i: int) -> str:
            a = args[i]
            if isinstance(a, dict) and a.get("type") in ("pred", "op"):
                return self.clause(a)
            return self.filler(a)

        if op == "NOT":
            return f"it is not true that {arg(0)}"
        if op == "CAN":
            return f"it can be that {arg(0)}"
        if op == "MAYBE":
            return f"maybe {arg(0)}"
        if op == "IF":
            return f"if {arg(0)}, then {arg(1)}"
        if op == "BECAUSE":
            return f"because {arg(0)}, {arg(1)}"
        if op == "WHEN":
            return f"when {arg(0)}, {arg(1)}"
        if op == "LIKE":
            return f"{arg(0)} is like {arg(1)}"
        if op == "AFTER":
            return f"after {arg(0)}, {arg(1)}"
        if op == "BEFORE":
            return f"before {arg(0)}, {arg(1)}"
        die(f"unhandled operator {op!r}")

    def pred(self, c: dict) -> str:
        pred, roles = c["pred"], dict(c["roles"])

        def take(role: str) -> str | None:
            f = roles.pop(role, None)
            return None if f is None else self.filler(f)

        # core rendering per predicate frame (gist §4.4 inventory)
        if pred == "DO":
            out = f"{take('agent')} does {take('undergoer') or 'something'}"
            inst, com = take("instrument"), take("comitative")
            if inst:
                out += f" with {inst}"
            if com:
                out += f" together with {com}"
        elif pred == "HAPPEN":
            u = take("undergoer")
            out = f"{u} happens" if u else "something happens"
        elif pred == "MOVE":
            out = f"{take('undergoer')} moves"
        elif pred == "THINK":
            out = f"{take('experiencer')} thinks"
            topic, quote = take("topic"), take("quote")
            if topic:
                out += f" about {topic}"
            if quote:
                out += f" like this: {quote}"
        elif pred == "KNOW":
            out = f"{take('experiencer')} knows"
            topic, comp = take("topic"), take("complement")
            if topic:
                out += f" about {topic}"
            if comp:
                out += f" that {comp}"
        elif pred == "WANT":
            out = f"{take('experiencer')} wants this: {take('complement')}"
        elif pred == "DON'T-WANT":
            out = f"{take('experiencer')} does not want this: {take('complement')}"
        elif pred == "FEEL":
            out = f"{take('experiencer')} feels"
            attr = take("attribute")
            out += f" something {attr}" if attr else " something"
        elif pred in ("SEE", "HEAR"):
            out = f"{take('experiencer')} {'sees' if pred == 'SEE' else 'hears'} {take('stimulus')}"
        elif pred == "SAY":
            out = f"{take('agent')} says"
            addr, topic, quote = take("addressee"), take("topic"), take("quote")
            if addr:
                out += f" to {addr}"
            if topic:
                out += f" about {topic}"
            if quote:
                out += f" {quote}"
        elif pred == "TRUE":
            out = f"{take('undergoer')} is true"
        elif pred == "BE-SOMEWHERE":
            out = f"{take('undergoer')} is somewhere at {take('locus')}"
        elif pred == "THERE-IS":
            out = f"there is {take('undergoer')}"
        elif pred == "BE-SPEC":
            out = f"{take('undergoer')} is {take('attribute')}"
        elif pred == "IS-MINE":
            out = f"{take('undergoer')} is mine ({take('possessor')})"
        elif pred == "LIVE":
            out = f"{take('undergoer')} lives"
        elif pred == "DIE":
            out = f"{take('undergoer')} dies"
        else:
            die(f"unhandled predicate {pred!r}")

        # adjuncts, fixed order
        for role, joiner in (("time", "at {}"), ("duration", "for {}"), ("place", "in {}"), ("manner", "in this way: {}")):
            f = take(role)
            if f:
                out += " " + joiner.format(f)
        if roles:
            die(f"unrendered roles {sorted(roles)} on {pred}")
        return out

    def render(self, label: str) -> str:
        e = self.expl
        if e.get("schema") != "kot-ast/1":
            die(f"schema {e.get('schema')!r}")
        body = "; ".join(self.clause(c) for c in e["clauses"])
        frame = e["frame"]
        if frame == "WhenTrue":
            return f"this is true of {self.ref_name(1)} when: {body}"
        if frame == "InstanceSchema":
            return f"{self.ref_name(1)} is this: {body}"
        if frame == "RelationalSchema":
            return f"this is about {self.ref_name(1)} and {self.ref_name(2)}: {body}"
        die(f"unknown frame {frame!r}")


def count_not(node) -> int:
    if isinstance(node, dict):
        n = 1 if (node.get("type") == "op" and node.get("op") == "NOT") else 0
        return n + sum(count_not(v) for v in node.values())
    if isinstance(node, list):
        return sum(count_not(v) for v in node)
    return 0


def main() -> None:
    with open(ITEMS_PATH) as f:
        items_doc = json.load(f)
    items = items_doc["items"]
    ids, words, glosses, texts, not_counts = [], [], [], [], []
    for it in items:
        slug = it["id"].split(":")[-1]
        with open(os.path.join(CONCEPTS_DIR, f"{slug}.json")) as f:
            rec = json.load(f)
        if rec["id"] != it["id"]:
            die(f"id mismatch for {slug}: {rec['id']} != {it['id']}")
        gloss = rec.get("gloss", "").strip()
        if not gloss:
            die(f"empty gloss for {slug}")
        ids.append(it["id"])
        words.append(it["word"])
        glosses.append(gloss)
        texts.append(Renderer(rec["explication"]).render(slug))
        not_counts.append(count_not(rec["explication"]))

    out = {
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "posture": "POST-HOC RE-ANALYSIS input (design-review change 1); the original pre-registered E2 verdict stands as reported",
        "rendererVersion": RENDERER_VERSION,
        "rendererSpec": "see module docstring of poc/e2/reanalysis/build_texts.py",
        "encoderContentHash": items_doc["encoderContentHash"],
        "corpusPin": items_doc["corpusPin"],
        "ids": ids,
        "words": words,
        "glossTexts": glosses,
        "explicationTexts": texts,
        "notCounts": not_counts,
        "hasNot": [c > 0 for c in not_counts],
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    digest = hashlib.sha256(open(OUT_PATH, "rb").read()).hexdigest()
    print(f"wrote {OUT_PATH} ({len(ids)} items, {sum(out['hasNot'])} with NOT) sha256={digest}")


if __name__ == "__main__":
    sys.exit(main())
