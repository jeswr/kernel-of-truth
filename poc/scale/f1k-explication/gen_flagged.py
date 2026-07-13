#!/usr/bin/env python3
"""
F1-K explication pilot — mechanical improvements (i) + (iii).

Implements the two mechanical recommendations from
`poc/scale/f1k-explication/pilot-review.md` §5:

  (i)   lossy-AST-suspected pre-flag — a mechanical, source-gloss-level proxy
        that marks a candidate `lossy_ast_suspected` when the *differentia*
        vocabulary of its aligned WordNet gloss falls outside a
        primes-coverable set (the profile-1 metalanguage: 65 NSM primes +
        endorsed molecules-v0 + endorsed kernel-v0 concept labels). Orders the
        human-review queue by `lossy_ast_score` so reviewers hit the hard
        AST<->prose cases deliberately (pilot §4: "lossy-AST is the true
        bottleneck ... where most rebuild attrition will occur").

  (iii) OBO/SUMO crosswalk seeding — an exact label<->lemma crosswalk of the
        OBO genus-differentia definitions (24,578) and SUMO class documentation
        onto the eligible pool's WN-3.1 synsets, gated by a mechanical
        rendering of the §1.1 scholarly-definition standard + a conservative
        sense-agreement guard. Candidates whose source definition meets (or
        nearly meets) the gate are marked `verbatim_reuse_candidate` with the
        source id + definition hash — a REVIEW CANDIDATE, not an endorsed merge
        (scale-track §3.5: label similarity may propose, not perform, merges).
        The pilot got 0 verbatim from WN-only; OBO/SUMO supply the reuse.

Governance: benchmark-blind (item-independent screen only; no model/gold
outcomes read), deterministic, $0. NO git, NO registry write, NO freeze, NO
spend. colibri naming; no handles. Author: designer-33.

Reads only:
  poc/scale/f1k-eligibility/candidate-pool.json   (committed; NOT mutated)
  data/onto-obo/*.jsonl                            (OBO genus-differentia defs)
  data/onto-sumo/terms.jsonl                       (SUMO class documentation)
  data/molecules-v0/molecules/*.json               (endorsed molecule labels)
  data/kernel-v0/concepts/*.json                   (endorsed concept labels)

Writes only (NEW files; committed pool untouched):
  poc/scale/f1k-explication/candidate-pool-flagged.json
  poc/scale/f1k-explication/improvements-report.md
"""
import json, re, glob, os, hashlib, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
POOL_PATH = ROOT / "poc/scale/f1k-eligibility/candidate-pool.json"
OUT_JSON = ROOT / "poc/scale/f1k-explication/candidate-pool-flagged.json"
OUT_MD = ROOT / "poc/scale/f1k-explication/improvements-report.md"

# Tunable, frozen constants (documented in the report).
LOSSY_THRESHOLD = 0.5          # >= half of differentia words outside coverable -> suspected
GATE_MEETS_MIN, GATE_MEETS_MAX = 15, 100    # §1.1(7) scholarly length band (words)
GATE_NEAR_MIN, GATE_NEAR_MAX = 8, 140       # "nearly meets": shorter/slightly-long defs
SENSE_AGREE_MIN = 1            # >=1 shared content token (conservative sense guard)

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ==========================================================================
#  Primes-coverable vocabulary  (the profile-1 metalanguage surface)
# ==========================================================================
# Source of truth for the 65 primes: encoder/src/lexicon.ts PRIMES (NSM chart
# v20, 2022). Reproduced here as exponent strings; the file is frozen and any
# change is an encoder version change (architecture.md §1.2). Molecule + kernel
# labels are read live from disk so the coverable set tracks the endorsed base.
PRIME_EXPONENTS = """
I YOU SOMEONE SOMETHING~THING PEOPLE BODY KIND PART THIS THE-SAME
OTHER~ELSE~ANOTHER ONE TWO SOME ALL MUCH~MANY LITTLE~FEW GOOD BAD BIG SMALL
THINK KNOW WANT DON'T-WANT FEEL SEE HEAR SAY WORDS TRUE DO HAPPEN MOVE
BE-SOMEWHERE THERE-IS BE-SPEC IS-MINE LIVE DIE WHEN~TIME NOW BEFORE AFTER
A-LONG-TIME A-SHORT-TIME FOR-SOME-TIME MOMENT WHERE~PLACE HERE ABOVE BELOW FAR
NEAR SIDE INSIDE TOUCH NOT MAYBE CAN BECAUSE IF VERY MORE LIKE~AS~WAY
""".split()

# Obvious English allolexes / inflections of the prime exponents that a
# differentia may surface with. Each maps transparently to a prime; documented
# so the coverable set is auditable, not a black box.
PRIME_ALLOLEX = """
person thing things time place places same another else other mine word words
saying said seen see sees want wanted feel felt know knew think thought move
moved moving happen happened happening live living life die died dead good bad
big small near far inside side above below touch touching true many much few
little all some one two moment long short before after now here where when
because if can maybe not very more like as way body people
""".split()

# Generic genus / structural heads — coverable because they *are* the frame
# skeleton (SOMEONE/SOMETHING/HAPPEN/BE-SPEC), not domain differentiae.
GENUS_HEADS = """
someone person people one act event state quality feeling condition process
thing something action way manner kind sort
""".split()

STOPWORDS = set("""
a an the of to in on for and or but with without by from as at is are be been
being that this these those it its their his her they them he she you i we our
your not no than then so such into over under out up down about within between
across also which who whom whose whether upon toward towards including
especially usually often typically may will would should could does do done has
have had was were etc eg ie such more most may can also
""".split())


def word_toks(s: str):
    """Lowercase alphabetic tokens, hyphen-split."""
    s = s.lower()
    s = re.sub(r"[^a-z' \-]", " ", s)
    return [re.sub(r"[^a-z]", "", w) for w in re.split(r"[\s\-]", s) if re.sub(r"[^a-z]", "", w)]


def stem_variants(w: str):
    """Cheap deterministic morphological closure (no external stemmer)."""
    v = {w}
    for suf in ("s", "es", "ed", "ing", "ly", "er", "ion", "tion", "al",
                "ness", "ity", "ous", "ic", "ical", "ment"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            v.add(w[: -len(suf)])
    v.add(w + "e")
    return v


def build_coverable():
    words = set()
    for p in PRIME_EXPONENTS:
        for tok in re.split(r"[~\-']", p.lower()):
            tok = re.sub(r"[^a-z]", "", tok)
            if tok:
                words.add(tok)
    words |= set(PRIME_ALLOLEX) | set(GENUS_HEADS)
    n_prime = len(words)
    # endorsed molecules-v0 labels
    mol = sorted(glob.glob(str(ROOT / "data/molecules-v0/molecules/*.json")))
    mol_labels = [re.sub(r"[^a-z]", "", os.path.basename(f)[:-5].lower()) for f in mol]
    words |= set(w for w in mol_labels if w)
    # endorsed kernel-v0 concept labels
    kv0 = sorted(glob.glob(str(ROOT / "data/kernel-v0/concepts/*.json")))
    kv0_labels = [re.sub(r"[^a-z]", "", os.path.basename(f)[:-5].lower()) for f in kv0]
    words |= set(w for w in kv0_labels if w)
    return words, dict(prime_surface=n_prime, molecules=len(mol_labels), kernel_v0=len(kv0_labels), total=len(words))


COVERABLE, COVERABLE_STATS = build_coverable()


def coverable_word(w: str) -> bool:
    return any(v in COVERABLE for v in stem_variants(w))


def strip_examples(gloss: str) -> str:
    """Isolate the DEFINITIONAL core: drop WN example clauses (after ';'),
    quoted usage examples, and parenthetical domain tags (§1.1(4): defining
    conditions must be separated from examples/usage)."""
    core = gloss.split(";")[0]
    core = re.sub(r'"[^"]*"', " ", core)
    core = re.sub(r"\([^)]*\)", " ", core)
    return core


def lossy_metrics(gloss: str, lemmas):
    """Return (score, n_out, n_diff, out_sample). score = fraction of
    differentia content words whose vocabulary is outside the primes-coverable
    set. Differentia = definitional-core content words minus stopwords minus
    the concept's own lemma variants (the circular/genus-name part)."""
    core = strip_examples(gloss)
    lem_variants = set()
    for lem in lemmas:
        for w in word_toks(lem):
            lem_variants |= stem_variants(w)
    diff = [w for w in word_toks(core)
            if w not in STOPWORDS and len(w) >= 3
            and not (stem_variants(w) & lem_variants)]
    if not diff:
        return 0.0, 0, 0, []
    out = [w for w in diff if not coverable_word(w)]
    # deterministic, de-duplicated sample of the offending vocabulary
    seen, sample = set(), []
    for w in out:
        if w not in seen:
            seen.add(w); sample.append(w)
    return round(len(out) / len(diff), 4), len(out), len(diff), sample[:8]


# ==========================================================================
#  OBO / SUMO crosswalk seeding
# ==========================================================================
def norm_name(s: str) -> str:
    s = s.lower().strip().replace("_", " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def content_set(s: str):
    return set(t for t in norm_name(s).split() if t not in STOPWORDS and len(t) >= 3)


def scholarly_tier(defn: str, matched_name: str):
    """Mechanical rendering of the §1.1 scholarly-definition standard.
    Returns 'meets' | 'nearly-meets' | None."""
    words = norm_name(defn).split()
    wc = len(words)
    nm = norm_name(matched_name).split()
    # §1.1(3) non-circular: definition must not simply open with the lemma
    circular = wc >= len(nm) and words[: len(nm)] == nm
    if circular:
        return None
    if GATE_MEETS_MIN <= wc <= GATE_MEETS_MAX:
        return "meets"
    if GATE_NEAR_MIN <= wc <= GATE_NEAR_MAX:
        return "nearly-meets"
    return None


def sense_agreement(wn_gloss: str, defn: str, matched_name: str) -> int:
    lem = content_set(matched_name)
    return len((content_set(wn_gloss) - lem) & (content_set(defn) - lem))


# source priority for deterministic tie-break (lower = preferred). OBO
# genus-differentia definitions first (formal source axioms), then SUMO docs.
SOURCE_PRIORITY = {
    "OBO:BFO": 0, "OBO:CHEBI": 1, "OBO:CL": 2, "OBO:GO": 3, "OBO:MONDO": 4,
    "OBO:NCBITAXON": 5, "OBO:OGMS": 6, "OBO:PATO": 7, "OBO:PO": 8, "OBO:RO": 9,
    "OBO:SO": 10, "OBO:UBERON": 11, "SUMO": 12,
}
TIER_RANK = {"meets": 0, "nearly-meets": 1}


def split_camel(s: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)


def build_crosswalk(eligible):
    """Map eligible-pool WN lemmas -> list of eligible candidates; scan
    OBO+SUMO defs for exact-normalized-name matches; keep scholarly-gated,
    sense-agreeing candidates."""
    lem2c = {}
    for c in eligible:
        for lem in c["lemmas"]:
            nn = norm_name(lem)
            if len(nn) >= 3:                       # drop 1-2 char abbreviation coincidences
                lem2c.setdefault(nn, []).append(c)

    cand_by_urn = {}   # urn -> list of candidate dicts

    def consider(cands, source, sid, matched_name, license_, defn):
        tier = scholarly_tier(defn, matched_name)
        if not tier:
            return
        for c in cands:
            agree = sense_agreement(c["gloss"], defn, matched_name)
            if agree < SENSE_AGREE_MIN:
                continue
            cand_by_urn.setdefault(c["urn"], []).append(dict(
                source=source, source_id=sid, matched_name=matched_name,
                tier=tier, sense_agreement=agree,
                definition_word_count=len(norm_name(defn).split()),
                definition=defn.strip(),
                definition_sha256=sha256(defn.strip()),
                license=license_,
            ))

    # ---- OBO (sorted files -> deterministic) ----
    obo_files = sorted(f for f in glob.glob(str(ROOT / "data/onto-obo/*.jsonl"))
                       if os.path.basename(f) != "minted-urns.jsonl")
    for f in obo_files:
        ont = os.path.basename(f).split(".")[0].upper()
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            ann = r.get("annotations", {})
            label = ann.get("label")
            defn = ann.get("definition")
            if not label or not defn:
                continue
            lic = r.get("provenance", {}).get("license", "")
            names = [label] + [s["text"] for s in ann.get("synonyms", [])
                               if s.get("scope") == "EXACT"]
            seen = set()
            for nm in names:
                nn = norm_name(nm)
                if nn in lem2c and nn not in seen:
                    seen.add(nn)
                    consider(lem2c[nn], "OBO:" + ont, r["id"], nm, lic, defn)

    # ---- SUMO ----
    for line in open(ROOT / "data/onto-sumo/terms.jsonl"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("kind") != "class":
            continue
        term = r.get("term")
        doc = r.get("annotations", {}).get("documentation")
        if not term or not doc:
            continue
        doc_clean = re.sub(r"&%", "", doc).strip()
        lic = r.get("provenance", {}).get("license", "")
        seen = set()
        for nm in (term, split_camel(term)):
            nn = norm_name(nm)
            if nn in lem2c and nn not in seen:
                seen.add(nn)
                consider(lem2c[nn], "SUMO", r["id"], nm, lic, doc_clean)

    # ---- pick the single best candidate per urn (deterministic) ----
    best = {}
    for urn, cl in cand_by_urn.items():
        cl_sorted = sorted(cl, key=lambda d: (
            TIER_RANK[d["tier"]],
            -d["sense_agreement"],
            SOURCE_PRIORITY.get(d["source"], 99),
            d["source_id"],
        ))
        best[urn] = dict(chosen=cl_sorted[0], n_candidates=len(cl_sorted),
                         all_sources=sorted({d["source"] for d in cl_sorted}))
    return best


# ==========================================================================
#  Main
# ==========================================================================
def main():
    pool = json.load(open(POOL_PATH))
    cands = pool["candidates"]
    eligible = [c for c in cands if c.get("greedy_disjoint_m8")]
    elig_urns = set(c["urn"] for c in eligible)

    crosswalk = build_crosswalk(eligible)

    # ---- annotate every candidate record ----
    out_records = []
    lossy_count = 0
    lossy_scores = []
    verbatim_by_source = {}
    verbatim_by_tier = {"meets": 0, "nearly-meets": 0}
    n_verbatim = 0

    for c in cands:
        rec = dict(c)  # shallow copy; never mutate the input object
        score, n_out, n_diff, sample = lossy_metrics(c["gloss"], c["lemmas"])
        is_elig = c["urn"] in elig_urns
        suspected = bool(is_elig and score >= LOSSY_THRESHOLD)
        rec["lossy_ast_suspected"] = suspected
        rec["lossy_ast_score"] = score
        rec["lossy_ast_detail"] = {
            "differentia_words": n_diff,
            "out_of_primes_coverable": n_out,
            "out_sample": sample,
            "scoped": is_elig,      # boolean flag only computed for eligible pool
        }
        if suspected:
            lossy_count += 1
        if is_elig:
            lossy_scores.append(score)

        vc = crosswalk.get(c["urn"])
        if vc and is_elig:
            ch = vc["chosen"]
            rec["verbatim_reuse_candidate"] = {
                "source": ch["source"],
                "source_id": ch["source_id"],
                "matched_lemma": ch["matched_name"],
                "scholarly_tier": ch["tier"],
                "sense_agreement": ch["sense_agreement"],
                "definition_word_count": ch["definition_word_count"],
                "definition": ch["definition"],
                "definition_sha256": ch["definition_sha256"],
                "license": ch["license"],
                "n_crosswalk_candidates": vc["n_candidates"],
                "all_candidate_sources": vc["all_sources"],
                "status": "review-candidate",  # scale-track §3.5: NOT an endorsed merge
            }
            n_verbatim += 1
            top = ch["source"].split(":")[0]
            verbatim_by_source[top] = verbatim_by_source.get(top, 0) + 1
            verbatim_by_tier[ch["tier"]] += 1
        else:
            rec["verbatim_reuse_candidate"] = None
        out_records.append(rec)

    # projected authoring-load reduction for the ~100 scale
    N_SCALE = 100
    elig_n = len(eligible)
    verbatim_rate = n_verbatim / elig_n
    projected_verbatim = round(verbatim_rate * N_SCALE, 1)

    summary = {
        "built": "designer-33 F1-K explication mechanical improvements (i)+(iii) ($0, benchmark-blind)",
        "reads": {
            "candidate_pool": str(POOL_PATH.relative_to(ROOT)),
            "obo": "data/onto-obo/*.jsonl",
            "sumo": "data/onto-sumo/terms.jsonl",
        },
        "eligible_pool_size": elig_n,
        "total_candidate_records": len(cands),
        "primes_coverable_vocabulary": COVERABLE_STATS,
        "improvement_i_lossy_ast_preflag": {
            "threshold": LOSSY_THRESHOLD,
            "n_lossy_ast_suspected": lossy_count,
            "pct_of_eligible": round(100 * lossy_count / elig_n, 1),
            "median_score": round(sorted(lossy_scores)[len(lossy_scores) // 2], 4),
            "note": ("boolean scoped to eligible pool; lossy_ast_score is the "
                     "primary queue-ordering key (ascending = likely-faithful first)"),
        },
        "improvement_iii_verbatim_reuse": {
            "n_verbatim_reuse_candidates": n_verbatim,
            "by_source": verbatim_by_source,
            "by_scholarly_tier": verbatim_by_tier,
            "verbatim_rate_in_eligible": round(verbatim_rate, 4),
            "projected_for_100_scale": projected_verbatim,
            "wn_only_pilot_verbatim": 0,
        },
    }

    out = {
        "schema": "f1k-candidate-pool-flagged/1",
        "provenance": summary,
        "benchmark_blind": "item-independent screen only; no model/gold outcomes read",
        "governance": "$0; no git; no registry write; no freeze; no spend; colibri naming; no handles",
        "derived_fields": ["lossy_ast_suspected", "lossy_ast_score",
                           "lossy_ast_detail", "verbatim_reuse_candidate"],
        "candidates": out_records,
    }
    OUT_JSON.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")

    write_report(summary)
    # self-check
    print("=== SELF-CHECK (F1-K improvements (i)+(iii)) ===")
    print(f"eligible pool (greedy_disjoint_m8):         {elig_n}")
    print(f"(i)   lossy_ast_suspected (score>={LOSSY_THRESHOLD}):        "
          f"{lossy_count}/{elig_n} ({round(100*lossy_count/elig_n,1)}%)")
    print(f"(iii) verbatim_reuse_candidate (eligible):  {n_verbatim}"
          f"  [meets {verbatim_by_tier['meets']} / nearly {verbatim_by_tier['nearly-meets']}]")
    print(f"      by source: {verbatim_by_source}")
    print(f"      pilot WN-only verbatim was 0; OBO/SUMO supply {n_verbatim}")
    print(f"projected authoring-load reduction for ~{N_SCALE} scale:")
    print(f"      ~{projected_verbatim} verbatim-reuse (rate {round(100*verbatim_rate,1)}%) "
          f"-> {round(100*verbatim_rate,1)}% fewer fresh authorings")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    return summary


def write_report(s):
    i = s["improvement_i_lossy_ast_preflag"]
    v = s["improvement_iii_verbatim_reuse"]
    elig = s["eligible_pool_size"]
    proj = v["projected_for_100_scale"]
    rate = v["verbatim_rate_in_eligible"]
    md = f"""# F1-K explication — mechanical improvements (i) + (iii): report

**Author:** designer-33 · **Governance:** benchmark-blind · deterministic · `$0` ·
no git · no registry write · no freeze · no spend · colibri naming · no handles.

Implements the two mechanical recommendations in
`poc/scale/f1k-explication/pilot-review.md` §5 that reduce the ~{100}-concept
authoring load and order the human-review queue, and that do **not** depend on
the pending AST-lossy maintainer ruling (§5(ii)). Output:
`candidate-pool-flagged.json` (the committed `candidate-pool.json` is **not**
mutated; two new derived fields are added to a fresh copy).

Eligible pool = the **{elig}** `greedy_disjoint_m8` disjoint-eligible WN-aligned
concepts. Both fields are written on every one of the
{s['total_candidate_records']} candidate records; the boolean flag and the
crosswalk are *scoped to the eligible pool* (`lossy_ast_detail.scoped`).

---

## (i) `lossy-AST-suspected` pre-flag

**Mechanism.** For each candidate, isolate the *definitional core* of the aligned
WN-3.1 gloss (drop example clauses after `;`, quoted usage, and parenthetical
domain tags — §1.1(4)), remove stopwords and the concept's own lemma variants
(the circular / genus-name part), and score the remaining **differentia**
vocabulary against a **primes-coverable set**:

> primes-coverable = 65 NSM prime exponents + documented allolexes/genus heads
> ({s['primes_coverable_vocabulary']['prime_surface']} surface forms) ∪ endorsed
> molecules-v0 labels ({s['primes_coverable_vocabulary']['molecules']}) ∪ endorsed
> kernel-v0 concept labels ({s['primes_coverable_vocabulary']['kernel_v0']})
> = **{s['primes_coverable_vocabulary']['total']}** coverable stems.

`lossy_ast_score` = fraction of differentia content words whose vocabulary lies
**outside** the primes-coverable set. This operationalises the pilot's
semantic-adequacy finding (§4): profile-1 "renders the genus/skeleton reliably
while dropping domain differentiae (painter, walls, money, moral law,
romantic)". A high score means the differentia leans on vocabulary the 65-prime
metalanguage cannot carry, so the `kot-ast/1` rendering will likely be *lossy*.

**Result.** `lossy_ast_suspected = (score ≥ {i['threshold']})` marks
**{i['n_lossy_ast_suspected']} / {elig} ({i['pct_of_eligible']}%)** of the
eligible pool; the eligible-pool median score is **{i['median_score']}**. That
near-total flag rate is itself the finding the pilot predicted — the QA-derived
WN long tail is dominated by domain/technical differentiae, so **lossy-AST, not
mechanical validity, is the binding constraint**. The *ordering* value therefore
lives in the continuous `lossy_ast_score`, not the boolean: sorting the review
queue by `lossy_ast_score` **ascending** puts the primes-coverable-differentia
concepts (fast, likely-faithful, low weakness-note risk) first and the
domain-heavy ones (need a carried weakness note, à la kernel-v0 `KNOWN-WEAK`)
last — reviewers hit the hard AST↔prose cases (question 4) deliberately.

**Nature of the proxy (honest).** This is a *source-gloss* proxy computed
*before* authoring; the pilot's 7/15 lossy verdict was a *post-authoring*
judgment on enriched glosses. The two correlate but are not identical: e.g.
`lover`'s WN gloss ("a person who loves someone or is loved by someone") is
fully primes-coverable at the source level (score 0) yet was judged lossy only
after the *romantic/sexual* differentia was authored in. Such residual cases are
exactly what the human gate exists to catch; the pre-flag orders the queue, it
does not replace the reviewer.

---

## (iii) OBO/SUMO crosswalk seeding → `verbatim-reuse-candidate`

**Mechanism.** Exact-normalized crosswalk of OBO class labels + EXACT synonyms
(genus-differentia `definition`) and SUMO class `documentation` onto the
eligible pool's WN-3.1 lemmas, then gate each match by a mechanical rendering of
the §1.1 scholarly-definition standard (non-circular; length band
{GATE_MEETS_MIN}–{GATE_MEETS_MAX} words = *meets*, {GATE_NEAR_MIN}–{GATE_NEAR_MAX}
= *nearly-meets*) plus a conservative **sense-agreement guard** (≥
{SENSE_AGREE_MIN} shared content token between the WN gloss and the source
definition, so a coincidental homograph label match is dropped). The surviving
match is written as `verbatim_reuse_candidate` with `source`, `source_id`, the
matched lemma, tier, `definition`, and `definition_sha256`.

Per scale-track §3.5 this is a **review candidate**, not an endorsed merge
(`status: "review-candidate"`): label similarity may *propose* a reuse but a
human must confirm same-referent alignment (§1.2) before it enters F1-K.

**Result.** **{v['n_verbatim_reuse_candidates']}** eligible concepts gain a
verbatim-reuse candidate — vs the pilot's **{v['wn_only_pilot_verbatim']}** from
the WN-only screen, confirming the pilot's §5(iii) prediction that OBO/SUMO would
supply the reuse the WN glosses cannot.

| Split | Count |
|---|---:|
| **Total eligible with a candidate** | **{v['n_verbatim_reuse_candidates']}** |
| by source — OBO | {v['by_source'].get('OBO', 0)} |
| by source — SUMO | {v['by_source'].get('SUMO', 0)} |
| by tier — meets (15–100 w) | {v['by_scholarly_tier']['meets']} |
| by tier — nearly-meets (8–14 w) | {v['by_scholarly_tier']['nearly-meets']} |

The reuse is concentrated in the biology/chemistry (OBO) and upper-ontology
(SUMO) verticals of the tail, exactly where fresh NSM authoring is least
tractable and a reviewed formal definition is most valuable.

---

## Projected authoring-load reduction for the ~100 scale

The verbatim-reuse rate in the eligible pool is **{round(100*rate,1)}%**
({v['n_verbatim_reuse_candidates']}/{elig}). Applied to the ~100-concept rebuild
that is a projected **~{proj} concepts** with a ready OBO/SUMO source definition
to reuse or lightly edit instead of authoring fresh.

- Pilot blended author-side effort ≈ **30–45 min/concept** (§4), dominated by the
  lossy `kot-ast/1` iterate-to-validate loop.
- A verbatim/near-verbatim source definition removes the *prose-authoring* leg
  (~5–15 min) and shrinks the sense-fixing leg for those ~{proj} concepts; on the
  design's `~60–90 fresh + 0–5 verbatim` projection this lifts the verbatim leg
  from ≈0 to **~{proj}**, i.e. a **~{round(100*rate,1)}% reduction in fresh
  prose-authoring** across the scale (the `kot-ast/1` leg is unchanged — reuse
  helps the gloss, not the lossy-AST bottleneck, which is what improvement (i)
  triages).
- The two improvements compose: sort the queue by `lossy_ast_score` ascending,
  and within that surface the `verbatim_reuse_candidate` rows first — reviewers
  clear the fast, high-confidence, source-backed concepts before spending
  question-4 budget on the domain-heavy lossy tail.

---

## Self-check

- **(i) lossy_ast_suspected:** {i['n_lossy_ast_suspected']} / {elig} eligible
  ({i['pct_of_eligible']}%) at threshold {i['threshold']}; median score
  {i['median_score']}; queue ordered by continuous `lossy_ast_score`.
- **(iii) verbatim_reuse_candidate:** {v['n_verbatim_reuse_candidates']} eligible
  concepts — OBO {v['by_source'].get('OBO', 0)}, SUMO {v['by_source'].get('SUMO', 0)}
  (meets {v['by_scholarly_tier']['meets']}, nearly-meets
  {v['by_scholarly_tier']['nearly-meets']}); pilot WN-only was 0.
- **Projected reduction:** ~{proj}/100 concepts reuse-seeded
  (~{round(100*rate,1)}% fewer fresh prose authorings).
- **Constraints honoured:** benchmark-blind · deterministic · `$0` · no git · no
  registry write · no freeze · no spend · colibri naming · no handles ·
  committed `candidate-pool.json` **not** mutated.
"""
    OUT_MD.write_text(md)


if __name__ == "__main__":
    main()
