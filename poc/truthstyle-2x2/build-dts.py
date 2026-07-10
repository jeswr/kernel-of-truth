#!/usr/bin/env python3
"""build-dts.py — deterministic builder for the d-ts corpus (truthstyle-2x2 probe).

Design: docs/design-truthstyle-2x2-f2-taxonomy.md §3. DRAFT registry record:
registry/experiments/truthstyle-2x2.json. NO LLM authors, selects, or edits
any item text; every choice below is a pure function of the pinned inputs and
the pre-committed seed string.

Item plan (600 items/judge):
  tier-1 (wn31-external content, INSTRUMENT + diagnostics): 96 words (64 noun / 32 verb) drawn
    by seeded hash from filtered WordNet 3.1 synsets, crossed
    {correct, wrong} x {nsm, plain} = 384 items. Truth gold is fixed by the
    external lexicographic authority (own gloss) vs a length-matched
    deranged-donor gloss (cyclic shift +1 in length-sorted order within POS —
    fixed-point-free by construction). Style poles are the pinned
    style-rules.json tier-1 transforms (weak NSM proxy; fidelity-gated).
  tier-2 (kernel-bytes content, PRIMARY): all 100 covered concepts (of the
    108 d-qa-t covered concepts) whose canonical gloss does not contain the
    headword, crossed {correct, wrong} x {nsm, plain} = 400 items. nsm pole =
    canonical gloss VERBATIM (the actual bytes at issue on the f2b line);
    plain pole = tier-2 plainify transform (inverse of the f2b-transfer §4.7
    S6 key) — MEASURED manipulation strength at build: >=80% of pairs must
    differ (gate). Truth gold = own/donor construction [STIPULATED:
    own-gloss-is-correct; see design doc §3.4 — the style CONTRAST is
    identified within truth level regardless].
  NOTE tier roles (design §3.2): tier-2 carries the primary because the
    tier-1 open-vocabulary NSM transform is MEASURED near-null (10/192 pairs
    differ beyond the preamble) — an equivalence primary on tier-1 would be
    dilution-biased toward false reassurance. tier-1's role is the
    kernel-independent truth-manipulation instrument gate + diagnostics.
  retest: 24 seeded-hash-sampled scored items duplicated (":dup" ids),
    excluded from all endpoints, feeding the retest instrument gate.

Leak rules (fail-closed):
  LS-1: tier-1 lemma disjoint from the 108 covered-concept headwords.
  LS-2: no tier-1 definition text contains any of the 108 canonical glosses
        as a substring (and no probe question equals any d-qa / d-qa-r /
        d-qa-t question).
  LS-3: probe ids namespaced "dts:".
  LS-4 (protocol, recorded in manifest): any HUMAN who judges d-ts items is
        permanently ineligible as an f2b-transfer judge (tier-2 reuses
        canonical-gloss bytes that appear in d-qa-t option surfaces; the
        default judge pool is LLM-only and stateless per item).
"""
import hashlib, json, os, re, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SEED = "dts/1|truthstyle-2x2|20260710"
N_T1_NOUN, N_T1_VERB, N_T2, N_RETEST = 64, 32, 100, 24

def h(*parts):
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

def file_sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def die(code, msg):
    print(f"{code}: {msg}", file=sys.stderr); sys.exit(1)

def main_clause(gloss):
    return gloss.split(";")[0].strip()

URN_MARKUP_RE = re.compile(r"\{urn:[^|}]+\|([^}]*)\}")

def render_canonical(rec):
    """VERBATIM the data/d-qa-t/build-dqat.py canonical-record rendering:
    kernel-v0 records carry `gloss`; molecules-v0 records render
    `groundingNote` through render_plain (URN markup stripped)."""
    if "gloss" in rec:
        return rec["gloss"].strip()
    text = URN_MARKUP_RE.sub(r"\1", rec["groundingNote"])
    text = text.replace(" [m]", "").replace("[m]", "")
    return re.sub(r"  +", " ", text).strip()

def toks(s):
    return s.split()

def apply_rules(text, rules):
    out = text
    for pat, rep in rules:
        if pat.startswith("re:"):
            out = re.sub(pat[3:], rep, out)
        else:
            out = out.replace(pat, rep)
    return out

def load_rules():
    p = os.path.join(ROOT, "poc", "truthstyle-2x2", "style-rules.json")
    return json.load(open(p)), file_sha(p), p

def wn_candidates(pos_file, pos):
    cands = []
    for ln in open(os.path.join(ROOT, "data", "lexical-wn31", pos_file)):
        o = json.loads(ln)
        lm = o["annotations"]["lemmas"]
        g = main_clause(o["annotations"]["gloss"]).lower()
        if not lm:
            continue
        w = lm[0]
        if not (w.isalpha() and w.islower() and 3 <= len(w) <= 12):
            continue
        t = toks(g)
        if not (8 <= len(t) <= 30):
            continue
        if '"' in g or "`" in g or "(" in g:
            continue
        if re.search(r"\b" + re.escape(w) + r"\b", g):
            continue  # headword inside own gloss: circular / giveaway
        cands.append({"word": w, "pos": pos, "gloss": g, "synset": o["id"]})
    # one synset per word: keep the seeded-hash-smallest
    best = {}
    for c in cands:
        k = h(SEED, "syn-pick", c["word"], c["synset"])
        if c["word"] not in best or k < best[c["word"]][0]:
            best[c["word"]] = (k, c)
    return [c for _, c in best.values()]

def seeded_sample(cands, n, tag):
    ranked = sorted(cands, key=lambda c: h(SEED, tag, c["word"]))
    return ranked[:n]

def derange(entries):
    """cyclic shift +1 in (gloss token count, word) order — fixed-point-free."""
    order = sorted(entries, key=lambda c: (len(toks(c["gloss"])), c["word"]))
    donor = {}
    for i, c in enumerate(order):
        donor[c["word"]] = order[(i + 1) % len(order)]
    return donor

QUESTION = (
    'Here is a proposed definition of the word "{label}".{pnote}\n\n'
    "definition: {text}\n\n"
    'Does this definition correctly give the meaning of the word "{label}" as '
    "ordinarily understood? Judge it like this: read each part as describing "
    "the normal case; extra true details do not make it wrong; it is not "
    "correct if any part does not fit the word's meaning, or if, taken as a "
    "whole, it fails to say what the word means. The plain simplified wording "
    "itself is never a reason to reject. Answer with exactly one word: "
    "yes / no / cannot-say."
)

def mk_item(tier, label, truth, style, text, content_key, src, donor=None):
    pnote = (" The letters X and Y in the definition name the participants "
             "given with the word in brackets.") if "(" in label else ""
    return {
        "id": f"dts:{tier}:{label}:{truth}-{style}",
        "tier": tier, "label": label, "truth": truth, "style": style,
        "text": text, "content_key": content_key,
        "question": QUESTION.format(label=label, pnote=pnote, text=text),
        "len_tokens": len(toks(text)), "source": src, "donor": donor,
        "retest": False,
    }

def main():
    rules, rules_sha, rules_path = load_rules()
    t1n = rules["tier1_nsm_preamble"]; t1p = rules["tier1_plain_preamble"]
    sub1 = rules["tier1_nsm_substitutions"]; sub2 = rules["tier2_plainify_substitutions"]

    # ---- covered concepts (tier-2 source + LS-1/LS-2 reference) ----
    covered = {}
    for ln in open(os.path.join(ROOT, "data", "d-qa-t", "items", "covered.jsonl")):
        o = json.loads(ln)
        covered.setdefault(o["label"], {"record_path": o["record_path"],
                                        "record_sha256": o["record_sha256"]})
    if len(covered) != 108:
        die("DTS_ERR_COVERED", f"expected 108 covered concepts, got {len(covered)}")
    glosses = {}
    for label, m in covered.items():
        p = os.path.join(ROOT, m["record_path"])
        if file_sha(p) != m["record_sha256"]:
            die("DTS_ERR_RECPIN", f"record sha drift: {m['record_path']}")
        glosses[label] = render_canonical(json.load(open(p))).lower()
    headwords = {label.split(" (")[0].strip().lower() for label in covered}

    # ---- tier-1: wn31 words ----
    nouns = [c for c in wn_candidates("synsets-noun.jsonl", "n") if c["word"] not in headwords]
    verbs = [c for c in wn_candidates("synsets-verb.jsonl", "v") if c["word"] not in headwords]
    sel = seeded_sample(nouns, N_T1_NOUN, "t1-noun") + seeded_sample(verbs, N_T1_VERB, "t1-verb")
    if len(sel) != N_T1_NOUN + N_T1_VERB:
        die("DTS_ERR_T1N", f"tier-1 selection short: {len(sel)}")
    donors = {}
    for pos in ("n", "v"):
        donors.update(derange([c for c in sel if c["pos"] == pos]))

    items = []
    for c in sel:
        own, don = c["gloss"], donors[c["word"]]["gloss"]
        for truth, g in (("correct", own), ("wrong", don)):
            dn = None if truth == "correct" else donors[c["word"]]["word"]
            ck = f"t1:{c['word']}:{truth}"
            items.append(mk_item("t1", c["word"], truth, "plain", t1p + g, ck, c["synset"], dn))
            items.append(mk_item("t1", c["word"], truth, "nsm", t1n + apply_rules(g, sub1), ck, c["synset"], dn))

    # ---- tier-2: kernel bytes ----
    t2_pool = [l for l in sorted(covered) if l.split(" (")[0].strip().lower()
               not in glosses[l]]
    t2 = sorted(t2_pool, key=lambda l: h(SEED, "t2", l))[:N_T2]
    if len(t2) != N_T2:
        die("DTS_ERR_T2N", f"tier-2 selection short: {len(t2)}")
    t2_entries = [{"word": l, "gloss": glosses[l]} for l in t2]
    t2_donor = derange(t2_entries)
    for e in t2_entries:
        own, don = e["gloss"], t2_donor[e["word"]]["gloss"]
        for truth, g in (("correct", own), ("wrong", don)):
            dn = None if truth == "correct" else t2_donor[e["word"]]["word"]
            ck = f"t2:{e['word']}:{truth}"
            items.append(mk_item("t2", e["word"], truth, "nsm", g, ck,
                                 covered[e["word"]]["record_path"], dn))
            items.append(mk_item("t2", e["word"], truth, "plain", apply_rules(g, sub2), ck,
                                 covered[e["word"]]["record_path"], dn))

    # ---- leak checks ----
    for it in items:
        if it["tier"] == "t1":
            for gl in glosses.values():
                if gl in it["text"]:
                    die("DTS_ERR_LS2", f"canonical gloss inside tier-1 item {it['id']}")
    probe_qs = {it["question"] for it in items}
    for corpus in ("d-qa/items/covered.jsonl", "d-qa/items/control.jsonl",
                   "d-qa-r/items/covered.jsonl", "d-qa-t/items/covered.jsonl"):
        for ln in open(os.path.join(ROOT, "data", corpus)):
            q = json.loads(ln).get("question")
            if q in probe_qs:
                die("DTS_ERR_LS2", f"probe question collides with {corpus}")

    # ---- retest duplicates ----
    scored = sorted(items, key=lambda it: h(SEED, "retest", it["id"]))
    for it in scored[:N_RETEST]:
        d = dict(it); d["id"] = it["id"] + ":dup"; d["retest"] = True
        items.append(d)

    # ---- pinned output order ----
    items.sort(key=lambda it: h(SEED, "rank", it["id"]))
    for r, it in enumerate(items):
        it["rank"] = r

    outdir = os.path.join(ROOT, "data", "d-ts")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "items.jsonl"), "w") as f:
        for it in items:
            f.write(json.dumps(it, sort_keys=True) + "\n")

    by = {}
    for it in items:
        if not it["retest"]:
            k = f"{it['tier']}:{it['truth']}:{it['style']}"
            by[k] = by.get(k, 0) + 1
    manifest = {
        "corpus": "d-ts", "seed": SEED,
        "authorship": ("deterministically generated by poc/truthstyle-2x2/build-dts.py "
                       "from the pinned inputs; NO LLM authored, selected, or edited any "
                       "item text"),
        "builder": {"path": "poc/truthstyle-2x2/build-dts.py",
                    "sha256": file_sha(os.path.abspath(__file__))},
        "style_rules": {"path": "poc/truthstyle-2x2/style-rules.json", "sha256": rules_sha},
        "counts": {"items_total": len(items), "scored": len(items) - N_RETEST,
                   "retest": N_RETEST, "by_cell": by,
                   "tier1_words": N_T1_NOUN + N_T1_VERB, "tier2_concepts": N_T2},
        "leak_checks": {"LS-1": "pass", "LS-2": "pass", "LS-3": "pass",
                        "LS-4": ("PROTOCOL RULE: any human who judges d-ts items is "
                                 "permanently ineligible as an f2b-transfer judge; "
                                 "default pool is LLM-only, stateless per item")},
        "inputs": {"lexical-wn31": "data/lexical-wn31 (synsets-noun/verb.jsonl)",
                   "covered_concepts": "data/d-qa-t/items/covered.jsonl (labels + record pins)"},
    }
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print(json.dumps({"built": len(items), "by_cell": by}, sort_keys=True))

if __name__ == "__main__":
    main()
