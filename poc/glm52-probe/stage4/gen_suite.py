#!/usr/bin/env python3
"""gen_suite.py — deterministic Stage-4 held-out quality suite (glm-s4drop-0).

Generates the 300-item teacher-forced quality suite pinned by the Stage-4
registry record (data/glm-s4drop-quality-suite-v1/): 10 macrodomains x 3
template families x 10 items, every item a (text_prompt -> short text_target)
pair scoreable by mean NLL/target-token under the pinned single-prefill path
(the same instrument Stage-3 validated end-to-end; design doc SS5.1).

DISJOINTNESS IS A FREEZE GATE (design doc SS2.3, GPT-5.6 review item 4): the
suite must share ZERO items with the 244 Stage-3 selection items AND zero
items with the full 480-item Wave-A probe corpus (the atlas that feeds the
SEM-D tier-2 ranking was built by routing the 480 — reusing any of them
would hand the semantic arm routing-level foreknowledge of the eval items).
This generator refuses to emit if any generated text_prompt matches (exact
string, or either-direction prefix >= 24 chars) any prompt in either corpus.

Determinism: all content fills are drawn from SHA-256 over (SEED, domain,
family, index) — no RNG state, no time, byte-identical across runs. Content
fills are STIPULATED template instantiations (ASM-2391); item semantic
correctness is template-guaranteed for arithmetic/format/copy and
best-effort factual for science/general (targets are fixed strings; the
paired PRIMARY contrast never scores truth, only NLL of the same target
under two arms, so a factually-imperfect target biases NO arm).

Usage:
    python3 poc/glm52-probe/stage4/gen_suite.py [--root <repo>] [--check-only]

Writes data/glm-s4drop-quality-suite-v1/{items.json,manifest.json} and prints
the kot-corpus-hash/1-relevant file sha256s. Exits nonzero on any
disjointness hit or count mismatch (fail closed, ERR_S4_*).
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys

SEED = "glm-s4drop-0:quality-suite-v1:20260801"
N_PER_FAMILY = 10


def h(*parts: object) -> int:
    return int(hashlib.sha256(":".join(str(p) for p in [SEED, *parts]).encode()).hexdigest(), 16)


def pick(seq, *key):
    return seq[h(*key) % len(seq)]


# ---------------------------------------------------------------- fill pools
NAMES = ["Lena", "Marco", "Priya", "Tomas", "Aiko", "Farid", "Nadia", "Oskar", "Yusuf", "Greta",
         "Ines", "Pavel", "Mei", "Dario", "Zofia"]
CITIES = [("France", "Paris"), ("Japan", "Tokyo"), ("Canada", "Ottawa"), ("Egypt", "Cairo"),
          ("Norway", "Oslo"), ("Peru", "Lima"), ("Kenya", "Nairobi"), ("Portugal", "Lisbon"),
          ("Thailand", "Bangkok"), ("Poland", "Warsaw"), ("Chile", "Santiago"), ("Greece", "Athens")]
ELEMENTS = [("hydrogen", "H"), ("oxygen", "O"), ("carbon", "C"), ("nitrogen", "N"),
            ("iron", "Fe"), ("gold", "Au"), ("sodium", "Na"), ("helium", "He"),
            ("calcium", "Ca"), ("potassium", "K"), ("silver", "Ag"), ("zinc", "Zn")]
PLANETS = [("closest planet to the Sun", "Mercury"), ("largest planet in the Solar System", "Jupiter"),
           ("planet known as the Red Planet", "Mars"), ("planet with prominent rings", "Saturn"),
           ("planet we live on", "Earth"), ("hottest planet in the Solar System", "Venus")]
ORGANS = [("pumps blood through the body", "heart"), ("primary organ of gas exchange", "lungs"),
          ("filters blood and produces urine", "kidneys"), ("largest internal organ, detoxifies blood", "liver"),
          ("controls the nervous system", "brain")]
DE_WORDS = [("house", "Haus"), ("water", "Wasser"), ("book", "Buch"), ("dog", "Hund"),
            ("bread", "Brot"), ("night", "Nacht"), ("hand", "Hand"), ("milk", "Milch")]
FR_WORDS = [("house", "maison"), ("water", "eau"), ("book", "livre"), ("dog", "chien"),
            ("bread", "pain"), ("night", "nuit"), ("cheese", "fromage"), ("milk", "lait")]
ES_WORDS = [("house", "casa"), ("water", "agua"), ("book", "libro"), ("dog", "perro"),
            ("bread", "pan"), ("night", "noche"), ("cheese", "queso"), ("milk", "leche")]
ZH_SPANS = ["春天的花园里有很多花", "他每天早上七点起床", "这本书放在桌子上", "我们下午去公园散步",
            "今天的天气非常好", "她喜欢喝绿茶", "火车八点钟出发", "图书馆星期天关门",
            "山上的风景很美", "孩子们在教室里读书", "这条河流向大海", "冬天的夜晚很长"]
ZH_EN = [("水", "water"), ("书", "book"), ("狗", "dog"), ("山", "mountain"),
         ("茶", "tea"), ("花", "flower"), ("月", "moon"), ("火", "fire")]
IDIOMS = [("Actions speak louder than", "words"), ("The early bird catches the", "worm"),
          ("Don't judge a book by its", "cover"), ("Every cloud has a silver", "lining"),
          ("Practice makes", "perfect"), ("Better late than", "never"),
          ("A picture is worth a thousand", "words"), ("When in Rome, do as the Romans", "do")]
FRUITS = ["apples", "pears", "plums", "melons", "grapes", "cherries", "lemons", "oranges"]
LEGAL_TERMS = [("a formal written agreement enforceable by law", "contract"),
               ("the party who initiates a lawsuit", "plaintiff"),
               ("the party being sued in a lawsuit", "defendant"),
               ("a legally binding court decision", "judgment"),
               ("intentional deception for unlawful gain", "fraud"),
               ("a right to keep possession of property belonging to another until a debt is paid", "lien")]


def rot(seq, fam, i):
    """Deterministic rotation through a fixed pool: distinct entry for
    i < len(seq); beyond that, callers add a phrasing variant (v)."""
    off = h(fam, "off") % len(seq)
    return seq[(off + i) % len(seq)], i // len(seq)


def items_for(domain: str, family: str, builder):
    out = []
    for i in range(N_PER_FAMILY):
        prompt, target = builder(i)
        out.append({"domain": domain, "family": family,
                    "text_prompt": prompt, "text_target": target})
    return out


def build_all():
    fams = []

    # 1. arithmetic --------------------------------------------------------
    def ar_add(i):
        a = 137 + (h("ar_add", i, "a") % 8600); b = 214 + (h("ar_add", i, "b") % 7300)
        return f"Compute the sum. {a} + {b} = ", str(a + b)

    def ar_mul(i):
        a = 12 + (h("ar_mul", i, "a") % 86); b = 13 + (h("ar_mul", i, "b") % 85)
        return f"Compute the product. {a} * {b} = ", str(a * b)

    def ar_word(i):
        n1 = 12 + (h("ar_word", i, 1) % 38); n2 = 5 + (h("ar_word", i, 2) % 30)
        who = pick(NAMES, "ar_word", i, "n"); fruit = pick(FRUITS, "ar_word", i, "f")
        return (f"{who} had {n1} {fruit} and gave away {n2}. "
                f"How many {fruit} does {who} have left? Answer: "), str(n1 - n2)
    fams += [("arithmetic", "add4", ar_add), ("arithmetic", "mul2x2", ar_mul),
             ("arithmetic", "word_sub", ar_word)]

    # 2. code --------------------------------------------------------------
    def code_ret(i):
        a = 2 + (h("code_ret", i, "a") % 9); b = 2 + (h("code_ret", i, "b") % 9)
        return (f"def scale(x):\n    return x * {a} + {b}\n\nprint(scale({i + 3}))\n"
                f"# output: "), str((i + 3) * a + b)

    def code_len(i):
        word, _ = rot(["kernel", "expert", "router", "matrix", "tensor", "decode",
                       "stream", "buffer", "signal", "vector"], "code_len", i)
        return f">>> len(\"{word}\")\n", str(len(word))

    def code_idx(i):
        xs = [(h("code_idx", i, j) % 90) + 10 for j in range(5)]
        k = h("code_idx", i, "k") % 5
        return f">>> xs = {xs}\n>>> xs[{k}]\n", str(xs[k])
    fams += [("code", "fn_eval", code_ret), ("code", "str_len", code_len),
             ("code", "list_index", code_idx)]

    # 3. format_csv --------------------------------------------------------
    def csv_sum(i):
        v = [(h("csv_sum", i, j) % 400) + 25 for j in range(3)]
        rows = "\n".join(f"r{j + 1},{v[j]}" for j in range(3))
        return f"item,cost\n{rows}\nThe total of the cost column is ", str(sum(v))

    def csv_get(i):
        who = pick(NAMES, "csv_get", i); age = 21 + (h("csv_get", i, "a") % 40)
        city = pick(CITIES, "csv_get", i, "c")[1]
        return (f"name,age,city\n{who},{age},{city}\n"
                f"In the row above, the value of the city column is "), city

    def tsv2csv(i):
        a = pick(FRUITS, "tsv", i, 1); b = (h("tsv", i, 2) % 50) + 3
        return (f"Convert this TSV line to CSV.\nTSV: {a}\t{b}\tcrate\nCSV: "), f"{a},{b},crate"
    fams += [("format_csv", "col_sum", csv_sum), ("format_csv", "col_get", csv_get),
             ("format_csv", "tsv_to_csv", tsv2csv)]

    # 4. format_xml_json ---------------------------------------------------
    def json_get(i):
        who = pick(NAMES, "json_get", i); n = (h("json_get", i) % 900) + 40
        return (f'Given the JSON {{"user": "{who}", "credits": {n}}}, '
                f'the value of the "credits" key is '), str(n)

    def xml_get(i):
        city = pick(CITIES, "xml_get", i)[1]; qty = (h("xml_get", i, "q") % 70) + 4
        return (f"<order><city>{city}</city><qty>{qty}</qty></order>\n"
                f"The text inside the <city> tag is "), city

    def json_keys(i):
        who = pick(NAMES, "json_keys", i)
        return (f'{{"id": {i + 11}, "name": "{who}", "active": true}}\n'
                f'The first key in this JSON object is '), '"id"'
    fams += [("format_xml_json", "json_value", json_get), ("format_xml_json", "xml_value", xml_get),
             ("format_xml_json", "json_first_key", json_keys)]

    # 5. copy_zh -----------------------------------------------------------
    def zh_copy(i):
        s, _ = rot(ZH_SPANS, "zh_copy", i)
        return f"请一字不差地重复下面这句话。\n句子：{s}\n重复：", s

    def zh_en(i):
        (zh, en), v = rot(ZH_EN, "zh_en", i)
        lead = ["The English translation of the Chinese word",
                "Translated into English, the Chinese word"][v % 2]
        tail = [" is \"", " becomes \""][v % 2]
        return f"{lead} \"{zh}\"{tail}", en + '"'

    def en_copy(i):
        who = NAMES[(h("en_copy", "off") + i) % len(NAMES)]
        n = (h("en_copy", i) % 400) + 37 + i
        s = f"ticket {n} assigned to {who}"
        return f"Repeat the following line exactly.\nLine: {s}\nRepeat: ", s
    fams += [("copy_zh", "zh_verbatim", zh_copy), ("copy_zh", "zh_to_en", zh_en),
             ("copy_zh", "en_verbatim", en_copy)]

    # 6. science -----------------------------------------------------------
    def sci_elem(i):
        (name, sym), v = rot(ELEMENTS, "sci_elem", i)
        lead = ["In chemistry class we write the element",
                "On the periodic-table wall chart, the element"][v % 2]
        return f"{lead} {name} with the symbol ", sym

    def sci_planet(i):
        (q, a), v = rot(PLANETS, "sci_planet", i)
        lead = ["The", "In astronomy, the"][v % 2]
        return f"{lead} {q} is ", a

    def sci_organ(i):
        (q, a), v = rot(ORGANS, "sci_organ", i)
        lead = ["The organ that", "In human anatomy, the organ that"][v % 2]
        return f"{lead} {q} is the ", a
    fams += [("science", "element_symbol", sci_elem), ("science", "planet_fact", sci_planet),
             ("science", "organ_fact", sci_organ)]

    # 7. legal_fin ---------------------------------------------------------
    def fin_interest(i):
        p = ((h("fin_int", i, "p") % 80) + 10) * 100; r = (h("fin_int", i, "r") % 9) + 2
        return (f"A deposit of {p} dollars earns {r}% simple interest per year. "
                f"The interest after one year is, in dollars, "), str(p * r // 100)

    def fin_fx(i):
        amt = (h("fin_fx", i, "a") % 90) + 10; rate = (h("fin_fx", i, "r") % 4) + 2
        return (f"At an exchange rate of {rate} florins per crown, "
                f"{amt} crowns equal, in florins, "), str(amt * rate)

    def legal_term(i):
        (q, a), v = rot(LEGAL_TERMS, "legal_term", i)
        lead = ["The legal term for", "In law, the usual term for"][v % 2]
        return f"{lead} {q} is ", a
    fams += [("legal_fin", "simple_interest", fin_interest), ("legal_fin", "fx_convert", fin_fx),
             ("legal_fin", "term_recall", legal_term)]

    # 8. multiling ---------------------------------------------------------
    def de_w(i):
        (en, de), v = rot(DE_WORDS, "de_w", i)
        lead = ["Das englische Wort", "Uebersetzung: das englische Wort"][v % 2]
        return f"{lead} \"{en}\" heisst auf Deutsch \"", de + '"'

    def fr_w(i):
        (en, fr), v = rot(FR_WORDS, "fr_w", i)
        lead = ["Le mot anglais", "Traduction : le mot anglais"][v % 2]
        return f"{lead} \"{en}\" se dit en francais \"", fr + '"'

    def es_w(i):
        (en, es), v = rot(ES_WORDS, "es_w", i)
        lead = ["La palabra inglesa", "Traduccion: la palabra inglesa"][v % 2]
        return f"{lead} \"{en}\" se dice en espanol \"", es + '"'
    fams += [("multiling", "de_word", de_w), ("multiling", "fr_word", fr_w),
             ("multiling", "es_word", es_w)]

    # 9. general -----------------------------------------------------------
    def gen_cap(i):
        (country, cap), _ = rot(CITIES, "gen_cap", i)
        return f"The capital city of {country} is ", cap

    def gen_day(i):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        k = (h("gen_day", "off") + i) % 7
        lead = ["The day that comes immediately after",
                "In the week, the day right after"][(i // 7) % 2]
        return f"{lead} {days[k]} is ", days[(k + 1) % 7]

    def gen_month(i):
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
        k = (h("gen_month", "off") + i) % 12
        return f"The month that comes immediately after {months[k]} is ", months[(k + 1) % 12]
    fams += [("general", "capital", gen_cap), ("general", "next_day", gen_day),
             ("general", "next_month", gen_month)]

    # 10. prose ------------------------------------------------------------
    def prose_idiom(i):
        (q, a), v = rot(IDIOMS, "prose_idiom", i)
        lead = ["Complete the saying:", "Finish the proverb:"][v % 2]
        return f"{lead} {q} ", a

    def prose_opp(i):
        pairs = [("hot", "cold"), ("big", "small"), ("fast", "slow"), ("light", "dark"),
                 ("open", "closed"), ("early", "late"), ("wet", "dry"), ("loud", "quiet")]
        (a, b), v = rot(pairs, "prose_opp", i)
        lead = ["The opposite of", "An antonym of"][v % 2]
        return f"{lead} \"{a}\" is \"", b + '"'

    def prose_seq(i):
        who = pick(NAMES, "prose_seq", i); fruit = pick(FRUITS, "prose_seq", i, "f")
        return (f"{who} walked to the market, bought some {fruit}, and then walked back "
                f"home. The person who bought the {fruit} was "), who
    fams += [("prose", "idiom", prose_idiom), ("prose", "opposite", prose_opp),
             ("prose", "coref", prose_seq)]

    items = []
    for domain, family, builder in fams:
        items += items_for(domain, family, builder)
    for k, it in enumerate(items):
        it["id"] = "s4q-%04d" % k
    return items


def load_existing_prompts(root):
    """Every prompt text the suite must be disjoint from: the 244 Stage-3
    selection items AND the full 480-item Wave-A probe corpus."""
    prompts = set()
    s3 = json.load(open(os.path.join(root, "poc/glm52-probe/stage3/corpus/stage3_corpus.json")))
    for it in s3["items"].values():
        prompts.add(it["text_prompt"])
    wa = json.load(open(os.path.join(root, "poc/glm52-probe/wave-a/corpus/wave_a_corpus.json")))
    for p in wa["probes"]:
        if isinstance(p, dict) and "text_prompt" in p:
            prompts.add(p["text_prompt"])
    return prompts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    root = args.root or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    items = build_all()
    if len(items) != 300:
        print("ERR_S4_SUITE_COUNT: generated %d items, expected 300" % len(items)); sys.exit(1)
    if len({it["text_prompt"] for it in items}) != 300:
        print("ERR_S4_SUITE_DUP: duplicate prompts inside the suite"); sys.exit(1)

    existing = load_existing_prompts(root)
    hits = []
    for it in items:
        p = it["text_prompt"]
        if p in existing:
            hits.append((it["id"], "exact"))
            continue
        for e in existing:
            if len(p) >= 24 and (e.startswith(p[:24]) or p.startswith(e[:24])):
                hits.append((it["id"], "prefix24")); break
    if hits:
        print("ERR_S4_SUITE_LEAK: %d suite items collide with stage-3/wave-A prompts: %s"
              % (len(hits), hits[:10])); sys.exit(1)

    n_existing = len(existing)
    payload = {"_schema": "kot-s4suite/1", "_seed": SEED,
               "_disjoint_from": {"stage3_corpus_items": 244, "wave_a_prompts_seen": n_existing},
               "items": items}
    blob = json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    manifest = {"_schema": "kot-s4suite-manifest/1", "n_items": 300,
                "domains": sorted({it["domain"] for it in items}),
                "families_per_domain": 3, "items_per_family": N_PER_FAMILY,
                "disjointness": {"rule": "exact prompt match + either-direction 24-char prefix vs "
                                          "stage3_corpus.json (244) and wave_a_corpus.json probes",
                                 "collisions": 0, "prompts_checked_against": n_existing},
                "generator": "poc/glm52-probe/stage4/gen_suite.py",
                "generator_seed": SEED}
    mblob = json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

    outdir = os.path.join(root, "data", "glm-s4drop-quality-suite-v1")
    if not args.check_only:
        os.makedirs(outdir, exist_ok=True)
        open(os.path.join(outdir, "items.json"), "w", encoding="utf-8").write(blob)
        open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8").write(mblob)
    print("items.json  sha256", hashlib.sha256(blob.encode("utf-8")).hexdigest())
    print("manifest.json sha256", hashlib.sha256(mblob.encode("utf-8")).hexdigest())
    print("suite: 300 items, disjoint vs %d existing prompts — OK" % n_existing)


if __name__ == "__main__":
    main()
