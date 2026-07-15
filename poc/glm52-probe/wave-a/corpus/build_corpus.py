#!/usr/bin/env python3
"""build_corpus.py — deterministic 480-item Wave-A profiling corpus.

Stage-2 spec (docs/next/design/glm52-expert-profiling-plan-sol-20260715.md
"Probe corpus"): 12 macrodomains x 4 subdomains/ops x 5 base items = 240 base,
+ 1 controlled counterpart per base = 480. Every item carries the orthogonal
labels  semantic_domain / operation / language / surface_format / answer_type /
template_family  (prompt_or_target + token_role are per-token, derived from the
trace `io` field + position, so are not stored here). Items are fixed
teacher-forced (text_prompt -> text_target). Controlled counterparts vary ONE
axis at a time (recorded in `counterpart_axis`). Split is by TEMPLATE FAMILY
(never by token): within each macrodomain the 4 families are stratified
2 discovery / 1 dev / 1 held-out, so every domain appears in every split (needed
for the discovery-vs-held-out Spearman gate).

EXPLORATORY infra — rigor relaxed vs a frozen experiment. Content fills are
STIPULATED (deterministic templates); item semantic correctness is best-effort,
not measured. $0, no network, fully deterministic.

Emits (next to this file):
  wave_a_corpus.json     the 480 labelled teacher-forced items
  corpus_manifest.json   label vocab, family->split map, counts, repeat ids
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

# tiny-oracle pseudo-token ids (dry-run only): deterministic small ids that
# exercise routing on the toy GlmMoeDsa oracle (needs valid ids <256, not text).
def tiny_ids_for(item_id: int, prompt: str, target: str) -> tuple[list[int], int]:
    def toks(s):
        # split into word-ish chunks; hash each -> id in [10,239]
        chunks = [c for c in s.replace("\n", " ").split(" ") if c] or [s[:4]]
        return [10 + (int(hashlib.sha256((str(item_id)+c).encode()).hexdigest(), 16) % 230) for c in chunks[:6]]
    p = toks(prompt); t = toks(target)[:2] or [200]
    ids = [3] + p + t                       # 3 = BOS-ish
    n_prompt = 1 + len(p)
    return ids, n_prompt


# ---------------------------------------------------------------------------
# Corpus definition. Each subdomain = a template family:
#   (sub, operation, language, surface_format, answer_type, base[5], cp_axis, cp[5])
# base/cp are (prompt, target) pairs. cp[i] is the controlled counterpart of
# base[i], differing from it in exactly the `cp_axis` labelled dimension.
# ---------------------------------------------------------------------------
def M(sub, op, lang, fmt, ans, base, cp_axis, cp, cp_over=None):
    return dict(sub=sub, op=op, lang=lang, fmt=fmt, ans=ans,
                base=base, cp_axis=cp_axis, cp=cp, cp_over=cp_over or {})

CORPUS = {
 # 1. CODE ------------------------------------------------------------------
 "code": [
  M("py_return","complete","code","code","code_token",
    [("def add(a, b):\n    return ","a + b\n"),
     ("def sub(a, b):\n    return ","a - b\n"),
     ("def mul(x, y):\n    return ","x * y\n"),
     ("def neg(n):\n    return ","-n\n"),
     ("def ident(v):\n    return ","v\n")],
    "surface_format",   # code -> prose description (same semantics)
    [("In words, the add function returns the ","sum of a and b"),
     ("In words, the sub function returns the ","difference of a and b"),
     ("In words, the mul function returns the ","product of x and y"),
     ("In words, the neg function returns the ","negation of n"),
     ("In words, the ident function returns the ","value v")],
    {"surface_format":"plain","language":"en"}),
  M("py_loop","complete","code","code","code_token",
    [("for i in range(10):\n    print(","i)\n"),
     ("for j in range(5):\n    print(","j)\n"),
     ("for k in items:\n    print(","k)\n"),
     ("for x in data:\n    print(","x)\n"),
     ("for n in nums:\n    print(","n)\n")],
    "surface_format",
    [("A loop over range(10) prints each ","index i"),
     ("A loop over range(5) prints each ","index j"),
     ("A loop over items prints each ","element k"),
     ("A loop over data prints each ","element x"),
     ("A loop over nums prints each ","number n")],
    {"surface_format":"plain","language":"en"}),
  M("js_console","transform","code","code","code_token",
    [("# Python\nprint('hi')\n# JavaScript\nconsole.","log('hi')"),
     ("# Python\nprint('ok')\n# JavaScript\nconsole.","log('ok')"),
     ("# Python\nprint(x)\n# JavaScript\nconsole.","log(x)"),
     ("# Python\nprint(1)\n# JavaScript\nconsole.","log(1)"),
     ("# Python\nprint(a)\n# JavaScript\nconsole.","log(a)")],
    "operation",        # transform -> complete (same surface, different op sense)
    [("The JavaScript console method for printing is console.","log"),
     ("To print in JavaScript you call console.","log"),
     ("JavaScript logs output with console.","log"),
     ("The standard JS logging call is console.","log"),
     ("In Node.js you print via console.","log")],
    {"operation":"complete"}),
  M("fix_syntax","transform","code","code","code_token",
    [("Fix: print 'hi'\nFixed: print(","'hi')"),
     ("Fix: print 5\nFixed: print(","5)"),
     ("Fix: print x\nFixed: print(","x)"),
     ("Fix: print a, b\nFixed: print(","a, b)"),
     ("Fix: print(1\nFixed: print(","1)")],
    "answer_type",      # produce a natural-language answer instead of a code token
    [("The Python 3 print statement requires ","parentheses"),
     ("Python 2 print became a ","function"),
     ("Missing parentheses cause a syntax ","error"),
     ("The fix adds a closing ","paren"),
     ("Print in Python 3 needs round ","brackets")],
    {"answer_type":"word"}),
 ],
 # 2. MATH ------------------------------------------------------------------
 "math": [
  M("int_mul","arithmetic","symbolic","plain","numeric",
    [("12 * 8 = ","96"),("7 * 6 = ","42"),("9 * 9 = ","81"),
     ("15 * 3 = ","45"),("11 * 11 = ","121")],
    "numeric_value",    # changed numbers, same wording
    [("13 * 8 = ","104"),("7 * 8 = ","56"),("9 * 8 = ","72"),
     ("15 * 4 = ","60"),("12 * 11 = ","132")], {}),
  M("int_add","arithmetic","symbolic","plain","numeric",
    [("34 + 58 = ","92"),("19 + 6 = ","25"),("100 + 250 = ","350"),
     ("7 + 8 = ","15"),("45 + 55 = ","100")],
    "numeric_value",
    [("35 + 58 = ","93"),("19 + 7 = ","26"),("100 + 251 = ","351"),
     ("7 + 9 = ","16"),("46 + 55 = ","101")], {}),
  M("derivative","transform","symbolic","plain","symbolic",
    [("The derivative of x^2 is ","2x"),
     ("The derivative of x^3 is ","3x^2"),
     ("The derivative of x^4 is ","4x^3"),
     ("The derivative of x^5 is ","5x^4"),
     ("The derivative of x^6 is ","6x^5")],
    "operation",        # transform (differentiate) -> lookup a rule
    [("The power rule differentiates x^n to ","n x^(n-1)"),
     ("Differentiating a power multiplies by the ","exponent"),
     ("The derivative of a constant is ","0"),
     ("The derivative of x is ","1"),
     ("The integral of 1 dx is ","x")],
    {"operation":"lookup"}),
  M("probability","arithmetic","symbolic","plain","symbolic",
    [("P(heads) for a fair coin = ","1/2"),
     ("P(6) for a fair die = ","1/6"),
     ("P(red) from a deck (26/52) = ","1/2"),
     ("P(two heads) = 1/2 * 1/2 = ","1/4"),
     ("P(ace) from a deck = 4/52 = ","1/13")],
    "numeric_value",
    [("P(tails) for a fair coin = ","1/2"),
     ("P(1) for a fair die = ","1/6"),
     ("P(black) from a deck (26/52) = ","1/2"),
     ("P(three heads) = (1/2)^3 = ","1/8"),
     ("P(king) from a deck = 4/52 = ","1/13")], {}),
 ],
 # 3. LOGIC -----------------------------------------------------------------
 "logic": [
  M("modus_ponens","complete","symbolic","plain","symbolic",
    [("If P then Q. P. Therefore ","Q"),
     ("If A then B. A. Therefore ","B"),
     ("If rain then wet. Rain. Therefore ","wet"),
     ("If X then Y. X holds. So ","Y"),
     ("If p implies q, and p, then ","q")],
    "operation",        # modus ponens -> modus tollens (different inference sense)
    [("If P then Q. Not Q. Therefore ","not P"),
     ("If A then B. Not B. Therefore ","not A"),
     ("If rain then wet. Not wet. Therefore ","no rain"),
     ("If X then Y. Not Y. So ","not X"),
     ("If p implies q, and not q, then ","not p")],
    {"sub_note":"modus_tollens"}),
  M("demorgan","transform","symbolic","plain","symbolic",
    [("not (A and B) = not A or ","not B"),
     ("not (A or B) = not A and ","not B"),
     ("not (P and Q) = not P or ","not Q"),
     ("not (X or Y) = not X and ","not Y"),
     ("not (a and b) = not a or ","not b")],
    "sense",            # flip the connective (same surface form, opposite law)
    [("not (A or B) = not A and ","not B"),
     ("not (A and B) = not A or ","not B"),
     ("not (P or Q) = not P and ","not Q"),
     ("not (X and Y) = not X or ","not Y"),
     ("not (a or b) = not a and ","not b")], {}),
  M("truth_table","lookup","symbolic","plain","boolean",
    [("true AND false = ","false"),
     ("true OR false = ","true"),
     ("false AND false = ","false"),
     ("true XOR true = ","false"),
     ("NOT true = ","false")],
    "sense",            # change the truth values / operator result
    [("true AND true = ","true"),
     ("false OR false = ","false"),
     ("true AND false = ","false"),
     ("true XOR false = ","true"),
     ("NOT false = ","true")], {}),
  M("quantifier","transform","symbolic","plain","symbolic",
    [("Negation of 'all x P(x)' is 'exists x ","not P(x)'"),
     ("Negation of 'exists x P(x)' is 'all x ","not P(x)'"),
     ("Negation of 'all x Q(x)' is 'exists x ","not Q(x)'"),
     ("Negation of 'some A' is 'no ","A'"),
     ("Negation of 'every dog barks' is 'some dog ","does not bark'")],
    "operation",        # transform -> plain lookup of the dual quantifier
    [("The dual of the universal quantifier is the ","existential"),
     ("The dual of the existential quantifier is the ","universal"),
     ("'For all' is written with the symbol ","forall"),
     ("'There exists' is written with the symbol ","exists"),
     ("The negation of 'always' is ","sometimes not")],
    {"operation":"lookup"}),
 ],
 # 4. FACTUAL ---------------------------------------------------------------
 "factual": [
  M("capital","lookup","en","plain","entity",
    [("The capital of France is ","Paris"),
     ("The capital of Japan is ","Tokyo"),
     ("The capital of Italy is ","Rome"),
     ("The capital of Egypt is ","Cairo"),
     ("The capital of Canada is ","Ottawa")],
    "sense",            # different entity, identical wording
    [("The capital of Germany is ","Berlin"),
     ("The capital of China is ","Beijing"),
     ("The capital of Spain is ","Madrid"),
     ("The capital of Kenya is ","Nairobi"),
     ("The capital of Brazil is ","Brasilia")], {}),
  M("author","lookup","en","plain","entity",
    [("Romeo and Juliet was written by ","Shakespeare"),
     ("The Odyssey was written by ","Homer"),
     ("Hamlet was written by ","Shakespeare"),
     ("The Iliad was written by ","Homer"),
     ("Pride and Prejudice was written by ","Austen")],
    "sense",
    [("War and Peace was written by ","Tolstoy"),
     ("Don Quixote was written by ","Cervantes"),
     ("Macbeth was written by ","Shakespeare"),
     ("The Aeneid was written by ","Virgil"),
     ("Emma was written by ","Austen")], {}),
  M("element","lookup","en","plain","entity",
    [("The chemical symbol for gold is ","Au"),
     ("The chemical symbol for iron is ","Fe"),
     ("The chemical symbol for oxygen is ","O"),
     ("The chemical symbol for sodium is ","Na"),
     ("The chemical symbol for carbon is ","C")],
    "sense",
    [("The chemical symbol for silver is ","Ag"),
     ("The chemical symbol for lead is ","Pb"),
     ("The chemical symbol for hydrogen is ","H"),
     ("The chemical symbol for potassium is ","K"),
     ("The chemical symbol for nitrogen is ","N")], {}),
  M("relation","complete","en","plain","entity",
    [("Paris is the capital of ","France"),
     ("Tokyo is the capital of ","Japan"),
     ("The Nile flows through ","Egypt"),
     ("The Eiffel Tower is in ","Paris"),
     ("Mount Everest is in ","Nepal")],
    "sense",
    [("Berlin is the capital of ","Germany"),
     ("Beijing is the capital of ","China"),
     ("The Amazon flows through ","Brazil"),
     ("The Colosseum is in ","Rome"),
     ("Mount Fuji is in ","Japan")], {}),
 ],
 # 5. SCIENCE ---------------------------------------------------------------
 "science": [
  M("definition","complete","en","plain","word",
    [("Photosynthesis converts sunlight into ","energy"),
     ("Evaporation turns liquid water into ","vapor"),
     ("Gravity pulls objects toward the ","ground"),
     ("Combustion releases heat and ","light"),
     ("Digestion breaks food into ","nutrients")],
    "sense",
    [("Respiration converts glucose into ","energy"),
     ("Condensation turns vapor into ","liquid"),
     ("Friction resists sliding ","motion"),
     ("Fermentation releases gas and ","alcohol"),
     ("Filtration separates solids from ","liquid")], {}),
  M("unit","lookup","en","plain","word",
    [("The SI unit of force is the ","newton"),
     ("The SI unit of energy is the ","joule"),
     ("The SI unit of power is the ","watt"),
     ("The SI unit of frequency is the ","hertz"),
     ("The SI unit of pressure is the ","pascal")],
    "sense",
    [("The SI unit of electric charge is the ","coulomb"),
     ("The SI unit of resistance is the ","ohm"),
     ("The SI unit of temperature is the ","kelvin"),
     ("The SI unit of length is the ","meter"),
     ("The SI unit of mass is the ","kilogram")], {}),
  M("formula","complete","en","plain","word",
    [("Force equals mass times ","acceleration"),
     ("Speed equals distance over ","time"),
     ("Density equals mass over ","volume"),
     ("Work equals force times ","distance"),
     ("Power equals work over ","time")],
    "surface_format",   # prose formula -> symbolic form (same semantics)
    [("F = m * ","a"),
     ("v = d / ","t"),
     ("rho = m / ","V"),
     ("W = F * ","d"),
     ("P = W / ","t")],
    {"surface_format":"plain","language":"symbolic","answer_type":"symbolic"}),
  M("value","lookup","en","plain","numeric",
    [("Water boils at 100 degrees ","Celsius"),
     ("Water freezes at 0 degrees ","Celsius"),
     ("A right angle is 90 ","degrees"),
     ("Sound travels about 343 meters per ","second"),
     ("There are 24 hours in a ","day")],
    "numeric_value",
    [("Water boils at 212 degrees ","Fahrenheit"),
     ("Water freezes at 32 degrees ","Fahrenheit"),
     ("A straight angle is 180 ","degrees"),
     ("Light travels 300000 kilometers per ","second"),
     ("There are 60 minutes in an ","hour")], {}),
 ],
 # 6. LEGAL / FINANCIAL -----------------------------------------------------
 "legal_fin": [
  M("contract","complete","en","plain","word",
    [("The parties hereby agree to the terms and ","conditions"),
     ("This agreement is governed by the laws of the ","state"),
     ("The undersigned parties enter into this ","contract"),
     ("Neither party shall be liable for indirect ","damages"),
     ("This clause shall survive the termination of the ","agreement")],
    "sense",
    [("The tenant hereby agrees to pay the monthly ","rent"),
     ("This deed is executed in the presence of a ","witness"),
     ("The employee agrees to maintain strict ","confidentiality"),
     ("The seller warrants that the goods are free of ","defects"),
     ("The borrower shall repay the outstanding ","loan")], {}),
  M("finance_calc","arithmetic","en","plain","numeric",
    [("10% of $200 is $","20"),
     ("5% of $100 is $","5"),
     ("A 20% tip on $50 is $","10"),
     ("$1000 at 3% interest earns $","30"),
     ("25% of $400 is $","100")],
    "numeric_value",
    [("10% of $300 is $","30"),
     ("5% of $200 is $","10"),
     ("A 20% tip on $80 is $","16"),
     ("$1000 at 5% interest earns $","50"),
     ("25% of $800 is $","200")], {}),
  M("legal_term","complete","en","plain","word",
    [("The plaintiff filed a ","lawsuit"),
     ("The defendant pleaded not ","guilty"),
     ("The judge issued a final ","ruling"),
     ("The witness took an ","oath"),
     ("The jury reached a unanimous ","verdict")],
    "sense",
    [("The tenant filed a formal ","complaint"),
     ("The suspect requested a defense ","attorney"),
     ("The court granted an ","injunction"),
     ("The notary certified the ","signature"),
     ("The appellate court affirmed the ","judgment")], {}),
  M("accounting","complete","en","plain","word",
    [("Assets minus liabilities equals ","equity"),
     ("Revenue minus expenses equals ","profit"),
     ("Debits must equal ","credits"),
     ("Gross profit minus operating costs equals ","net profit"),
     ("The balance sheet lists assets and ","liabilities")],
    "surface_format",   # prose -> ledger/table style (same semantics)
    [("Assets = Liabilities + ","Equity"),
     ("Net Income = Revenue - ","Expenses"),
     ("Ledger rule: Debit = ","Credit"),
     ("Net = Gross - ","Costs"),
     ("Balance: Assets | ","Liabilities")],
    {"surface_format":"table","answer_type":"structural_token"}),
 ],
 # 7. PROSE -----------------------------------------------------------------
 "prose": [
  M("pangram","complete","en","plain","word",
    [("The quick brown fox jumps over the lazy ","dog"),
     ("Pack my box with five dozen liquor ","jugs"),
     ("The five boxing wizards jump ","quickly"),
     ("Sphinx of black quartz, judge my ","vow"),
     ("How vexingly quick daft zebras ","jump")],
    "sense",            # different final content word, same structure
    [("The quick brown fox jumps over the sleeping ","cat"),
     ("Pack my bag with five dozen liquor ","bottles"),
     ("The five boxing wizards move ","quickly"),
     ("Sphinx of black granite, judge my ","vow"),
     ("How vexingly quick daft zebras ","run")], {}),
  M("opening","complete","en","plain","word",
    [("It was a dark and stormy ","night"),
     ("Once upon a time in a distant ","land"),
     ("In the beginning there was ","light"),
     ("It was the best of ","times"),
     ("Call me ","Ishmael")],
    "sense",
    [("It was a bright and sunny ","morning"),
     ("Once upon a time in a nearby ","village"),
     ("In the end there was only ","silence"),
     ("It was the worst of ","times"),
     ("They called him ","Ishmael")], {}),
  M("idiom","complete","en","plain","word",
    [("A picture is worth a thousand ","words"),
     ("The early bird catches the ","worm"),
     ("Actions speak louder than ","words"),
     ("When in Rome, do as the Romans ","do"),
     ("Better late than ","never")],
    "sense",
    [("A stitch in time saves ","nine"),
     ("The squeaky wheel gets the ","grease"),
     ("Practice makes ","perfect"),
     ("Don't count your chickens before they ","hatch"),
     ("Every cloud has a silver ","lining")], {}),
  M("narrative","complete","en","plain","word",
    [("Once upon a time, there was a ","princess"),
     ("The hero drew his sword and ","charged"),
     ("She opened the door and saw a ","dragon"),
     ("The old wizard cast a powerful ","spell"),
     ("They lived happily ever ","after")],
    "sense",
    [("Once upon a time, there was a ","dragon"),
     ("The knight raised his shield and ","waited"),
     ("She opened the box and found a ","letter"),
     ("The young witch brewed a bitter ","potion"),
     ("They journeyed on for many ","days")], {}),
 ],
 # 8. MULTILINGUAL (en + zh mandatory) --------------------------------------
 "multiling": [
  M("zh_capital","lookup","zh","chinese","entity",
    [("北京是中国的","首都"),
     ("东京是日本的","首都"),
     ("巴黎是法国的","首都"),
     ("罗马是意大利的","首都"),
     ("开罗是埃及的","首都")],
    "language",         # translate to English (same semantics, language axis)
    [("Beijing is the capital of ","China"),
     ("Tokyo is the capital of ","Japan"),
     ("Paris is the capital of ","France"),
     ("Rome is the capital of ","Italy"),
     ("Cairo is the capital of ","Egypt")],
    {"language":"en","surface_format":"plain"}),
  M("zh_weather","complete","zh","chinese","word",
    [("今天天气很","好"),
     ("外面下","雨"),
     ("冬天很","冷"),
     ("夏天很","热"),
     ("这个菜很好","吃")],
    "language",
    [("The weather today is very ","good"),
     ("It is raining ","outside"),
     ("Winter is very ","cold"),
     ("Summer is very ","hot"),
     ("This dish is very ","tasty")],
    {"language":"en","surface_format":"plain"}),
  M("translate","translate","en","plain","word",
    [("English: hello\nChinese: ","你好"),
     ("English: thank you\nChinese: ","谢谢"),
     ("English: goodbye\nChinese: ","再见"),
     ("English: water\nChinese: ","水"),
     ("English: friend\nChinese: ","朋友")],
    "language",         # reverse direction zh->en (language/direction axis)
    [("Chinese: 你好\nEnglish: ","hello"),
     ("Chinese: 谢谢\nEnglish: ","thank you"),
     ("Chinese: 再见\nEnglish: ","goodbye"),
     ("Chinese: 水\nEnglish: ","water"),
     ("Chinese: 朋友\nEnglish: ","friend")],
    {"language":"mixed"}),
  M("zh_number","complete","zh","chinese","word",
    [("一 二 三 四 ","五"),
     ("十 二十 三十 ","四十"),
     ("星期一 星期二 星期","三"),
     ("春 夏 秋 ","冬"),
     ("金 木 水 火 ","土")],
    "language",
    [("one two three four ","five"),
     ("ten twenty thirty ","forty"),
     ("Monday Tuesday ","Wednesday"),
     ("spring summer autumn ","winter"),
     ("metal wood water fire ","earth")],
    {"language":"en","surface_format":"plain"}),
 ],
 # 9. STRUCTURED (json/xml/csv/markdown) ------------------------------------
 "structured": [
  M("json_obj","complete","en","json","structural_token",
    [("{\"name\": \"Alice\", \"age\": ","30}"),
     ("{\"city\": \"Paris\", \"pop\": ","2000000}"),
     ("{\"ok\": true, \"code\": ","200}"),
     ("{\"x\": 1, \"y\": ","2}"),
     ("{\"id\": 7, \"active\": ","true}")],
    "validity",         # near-valid / malformed (same surface, invalid)
    [("Invalid JSON (missing quote): {name: \"Alice\", age: ","30}"),
     ("Invalid JSON (trailing comma): {\"city\": \"Paris\", ","}"),
     ("Invalid JSON (single quotes): {'ok': true, 'code': ","200}"),
     ("Invalid JSON (no braces): \"x\": 1, \"y\": ","2"),
     ("Invalid JSON (bare word): {id: 7, active: ","true}")],
    {"answer_type":"structural_token"}),
  M("xml_tag","complete","en","xml","structural_token",
    [("<user><name>Bob</name><age>","25</age></user>"),
     ("<book><title>X</title><year>","2020</year></book>"),
     ("<item><id>1</id><qty>","3</qty></item>"),
     ("<tag><k>a</k><v>","b</v></tag>"),
     ("<row><c1>x</c1><c2>","y</c2></row>")],
    "surface_format",   # same record as JSON (semantics same, format axis)
    [("{\"name\": \"Bob\", \"age\": ","25}"),
     ("{\"title\": \"X\", \"year\": ","2020}"),
     ("{\"id\": 1, \"qty\": ","3}"),
     ("{\"k\": \"a\", \"v\": ","\"b\"}"),
     ("{\"c1\": \"x\", \"c2\": ","\"y\"}")],
    {"surface_format":"json"}),
  M("csv_row","complete","en","csv","structural_token",
    [("name,age\nAlice,30\nBob,","25"),
     ("x,y\n1,2\n3,","4"),
     ("id,qty\n1,10\n2,","20"),
     ("a,b,c\n1,2,3\n4,5,","6"),
     ("day,temp\nMon,20\nTue,","22")],
    "surface_format",   # csv -> table (markdown), same data
    [("| name | age |\n| Alice | 30 |\n| Bob | ","25 |"),
     ("| x | y |\n| 1 | 2 |\n| 3 | ","4 |"),
     ("| id | qty |\n| 1 | 10 |\n| 2 | ","20 |"),
     ("| a | b | c |\n| 1 | 2 | 3 |\n| 4 | 5 | ","6 |"),
     ("| day | temp |\n| Mon | 20 |\n| Tue | ","22 |")],
    {"surface_format":"markdown"}),
  M("markdown","complete","en","markdown","structural_token",
    [("# Title\n\n- item one\n- item ","two"),
     ("## Heading\n\n1. first\n2. ","second"),
     ("**bold** and *italic* and `","code`"),
     ("- [x] done\n- [ ] ","todo"),
     ("> a quote\n>\n> another ","line")],
    "surface_format",   # markdown -> plain prose
    [("Title\n\nThe list has item one and item ","two"),
     ("Heading\n\nThe steps are first and ","second"),
     ("This text is bold and italic and ","code"),
     ("One task is done and one is ","todo"),
     ("This is a quote with another ","line")],
    {"surface_format":"plain"}),
 ],
 # 10. COPY / INDUCTION -----------------------------------------------------
 "copy": [
  M("word_repeat","copy","en","whitespace","span",
    [("abc abc abc abc ","abc"),
     ("cat cat cat cat ","cat"),
     ("go go go go ","go"),
     ("red red red red ","red"),
     ("one one one one ","one")],
    "vocabulary",       # different tokens, identical copy structure
    [("xyz xyz xyz xyz ","xyz"),
     ("dog dog dog dog ","dog"),
     ("no no no no ","no"),
     ("blue blue blue blue ","blue"),
     ("two two two two ","two")], {}),
  M("ngram_induction","copy","symbolic","whitespace","span",
    [("1 2 3 1 2 3 1 2 3 ","1 2 3"),
     ("a b a b a b ","a b"),
     ("x y z x y z ","x y z"),
     ("7 8 7 8 7 8 ","7 8"),
     ("p q r p q r ","p q r")],
    "vocabulary",
    [("4 5 6 4 5 6 4 5 6 ","4 5 6"),
     ("m n m n m n ","m n"),
     ("i j k i j k ","i j k"),
     ("2 9 2 9 2 9 ","2 9"),
     ("s t u s t u ","s t u")], {}),
  M("long_range","copy","en","plain","span",
    [("The code is Z7Q. Remember it. The code is ","Z7Q"),
     ("The name is Mira. Note it. The name is ","Mira"),
     ("Key = 42. Store it. Key = ","42"),
     ("Token: AB9. Keep it. Token: ","AB9"),
     ("Word: apple. Recall it. Word: ","apple")],
    "vocabulary",
    [("The code is X3K. Remember it. The code is ","X3K"),
     ("The name is Otto. Note it. The name is ","Otto"),
     ("Key = 99. Store it. Key = ","99"),
     ("Token: QR2. Keep it. Token: ","QR2"),
     ("Word: melon. Recall it. Word: ","melon")], {}),
  M("char_repeat","copy","en","whitespace","char",
    [("a a a a a ","a"),
     ("z z z z z ","z"),
     ("* * * * * ","*"),
     ("1 1 1 1 1 ","1"),
     ("- - - - - ","-")],
    "vocabulary",
    [("b b b b b ","b"),
     ("q q q q q ","q"),
     ("# # # # # ","#"),
     ("9 9 9 9 9 ","9"),
     ("+ + + + + ","+")], {}),
 ],
 # 11. TOOL / SCHEMA (closed-class) -----------------------------------------
 "tool_schema": [
  M("func_schema","complete","en","json","structural_token",
    [("{\"function\": \"get_weather\", \"parameters\": {\"city\": ","\"string\"}}"),
     ("{\"function\": \"add\", \"parameters\": {\"a\": ","\"number\"}}"),
     ("{\"function\": \"send\", \"parameters\": {\"to\": ","\"string\"}}"),
     ("{\"function\": \"lookup\", \"parameters\": {\"id\": ","\"integer\"}}"),
     ("{\"function\": \"toggle\", \"parameters\": {\"on\": ","\"boolean\"}}")],
    "surface_format",   # schema -> prose spec of same tool
    [("The get_weather tool takes a city, whose type is ","string"),
     ("The add tool takes an argument a of type ","number"),
     ("The send tool takes a recipient of type ","string"),
     ("The lookup tool takes an id of type ","integer"),
     ("The toggle tool takes a flag of type ","boolean")],
    {"surface_format":"plain","answer_type":"word"}),
  M("enum_choice","classify","en","plain","word",
    [("status must be one of active, inactive, ","pending"),
     ("size is one of small, medium, ","large"),
     ("priority is low, medium, ","high"),
     ("color is red, green, ","blue"),
     ("role is admin, editor, ","viewer")],
    "sense",            # a different member of the closed class
    [("status must be one of active, inactive, ","suspended"),
     ("size is one of small, medium, ","xlarge"),
     ("priority is low, medium, ","urgent"),
     ("color is red, green, ","yellow"),
     ("role is admin, editor, ","guest")], {}),
  M("tool_name","lookup","en","plain","word",
    [("To search the web, call the tool named ","search"),
     ("To read a file, call the tool named ","read"),
     ("To send an email, call the tool named ","email"),
     ("To run a shell command, call the tool named ","bash"),
     ("To fetch a URL, call the tool named ","fetch")],
    "sense",
    [("To write a file, call the tool named ","write"),
     ("To delete a file, call the tool named ","delete"),
     ("To list a directory, call the tool named ","list"),
     ("To edit a file, call the tool named ","edit"),
     ("To grep a pattern, call the tool named ","grep")], {}),
  M("bool_field","complete","en","json","boolean",
    [("{\"enabled\": ","true}"),
     ("{\"active\": ","true}"),
     ("{\"deleted\": ","false}"),
     ("{\"visible\": ","true}"),
     ("{\"archived\": ","false}")],
    "sense",            # flip the boolean value
    [("{\"enabled\": ","false}"),
     ("{\"active\": ","false}"),
     ("{\"deleted\": ","true}"),
     ("{\"visible\": ","false}"),
     ("{\"archived\": ","true}")], {}),
 ],
 # 12. DIALOGUE / INSTRUCTION / CLASSIFY ------------------------------------
 "dialogue": [
  M("qa","complete","en","plain","numeric",
    [("Q: What is 2+2?\nA: ","4"),
     ("Q: What is the capital of France?\nA: ","Paris"),
     ("Q: How many days in a week?\nA: ","7"),
     ("Q: What color is the sky?\nA: ","blue"),
     ("Q: What is the opposite of hot?\nA: ","cold")],
    "answer_type",      # same Q&A frame, different answer type
    [("Q: Is 4 even?\nA: ","yes"),
     ("Q: Name a fruit.\nA: ","apple"),
     ("Q: Spell cat.\nA: ","c a t"),
     ("Q: Give a synonym for happy.\nA: ","glad"),
     ("Q: Translate 'yes' to Spanish.\nA: ","si")], {}),
  M("sentiment","classify","en","plain","word",
    [("Review: I loved it! Sentiment: ","positive"),
     ("Review: Best purchase ever. Sentiment: ","positive"),
     ("Review: Absolutely wonderful. Sentiment: ","positive"),
     ("Review: Highly recommend. Sentiment: ","positive"),
     ("Review: A delightful experience. Sentiment: ","positive")],
    "label",            # flip the class (same frame, opposite label)
    [("Review: I hated it. Sentiment: ","negative"),
     ("Review: Worst purchase ever. Sentiment: ","negative"),
     ("Review: Absolutely terrible. Sentiment: ","negative"),
     ("Review: Do not recommend. Sentiment: ","negative"),
     ("Review: A dreadful experience. Sentiment: ","negative")], {}),
  M("instruction","complete","en","plain","word",
    [("Translate 'cat' to French: ","chat"),
     ("Translate 'dog' to French: ","chien"),
     ("Uppercase 'abc': ","ABC"),
     ("Reverse 'ab': ","ba"),
     ("The plural of 'cat' is ","cats")],
    "operation",        # follow-instruction -> plain lookup
    [("The French word for cat is ","chat"),
     ("The French word for dog is ","chien"),
     ("The uppercase form of abc is ","ABC"),
     ("The reverse of ab is ","ba"),
     ("More than one cat are ","cats")],
    {"operation":"lookup"}),
  M("yesno","classify","en","plain","boolean",
    [("Is the sky blue? Answer: ","yes"),
     ("Is fire cold? Answer: ","no"),
     ("Is 10 greater than 5? Answer: ","yes"),
     ("Is a whale a fish? Answer: ","no"),
     ("Do birds fly? Answer: ","yes")],
    "label",            # flip so the answer flips
    [("Is the sky green? Answer: ","no"),
     ("Is fire hot? Answer: ","yes"),
     ("Is 5 greater than 10? Answer: ","no"),
     ("Is a whale a mammal? Answer: ","yes"),
     ("Do fish fly? Answer: ","no")], {}),
 ],
}

# ---------------------------------------------------------------------------
# Materialise
# ---------------------------------------------------------------------------
def build():
    macros = list(CORPUS.keys())
    assert len(macros) == 12, len(macros)
    # TWO family granularities:
    #  - template_family  = macro.sub          (48) — reporting label.
    #  - prompt_family    = macro.sub.f{fill}   (240) — the "prompt family" unit the
    #    Stage-2 gate/bootstrap/split use. Each holds a base+counterpart minimal pair
    #    (2 items) so pairs never leak across the split. Split is assigned per fill
    #    WITHIN each subdomain (fills 0,1,2 discovery / 3 dev / 4 held_out) so every
    #    domain AND every template_family appears in every split (needed for the
    #    discovery-vs-held-out Spearman gate). A genuine narrow domain specialist can
    #    now reach >=20 prompt families (a whole domain = 4 subs x 5 fills = 20).
    fill_split = {0: "discovery", 1: "discovery", 2: "discovery", 3: "dev", 4: "held_out"}
    items = []
    prompt_families = {}
    template_families = {}
    item_id = 0
    for macro in macros:
        subs = CORPUS[macro]
        assert len(subs) == 4, (macro, len(subs))
        for sd in subs:
            tfam = f"{macro}.{sd['sub']}"
            template_families[tfam] = {"macro": macro, "sub": sd["sub"],
                                       "operation": sd["op"], "counterpart_axis": sd["cp_axis"]}
            assert len(sd["base"]) == 5 and len(sd["cp"]) == 5, tfam
            for fi in range(5):
                pfam = f"{macro}.{sd['sub']}.f{fi}"
                split = fill_split[fi]
                prompt_families[pfam] = {"macro": macro, "sub": sd["sub"], "fill": fi,
                                         "template_family": tfam, "split": split,
                                         "operation": sd["op"], "counterpart_axis": sd["cp_axis"]}
                bp, bt = sd["base"][fi]
                items.append(_mk(item_id, macro, sd, tfam, pfam, split, bp, bt,
                                 is_cp=False, cp_axis=None)); item_id += 1
                cpp, cpt = sd["cp"][fi]
                items.append(_mk(item_id, macro, sd, tfam, pfam, split, cpp, cpt,
                                 is_cp=True, cp_axis=sd["cp_axis"],
                                 overrides=dict(sd["cp_over"]))); item_id += 1
    return items, prompt_families, template_families


def _mk(iid, macro, sd, tfam, pfam, split, prompt, target, is_cp, cp_axis, overrides=None):
    lang = sd["lang"]; fmt = sd["fmt"]; ans = sd["ans"]; op = sd["op"]
    ov = overrides or {}
    lang = ov.get("language", lang); fmt = ov.get("surface_format", fmt)
    ans = ov.get("answer_type", ans); op = ov.get("operation", op)
    tiny_ids, tiny_np = tiny_ids_for(iid, prompt, target)
    return {
        "id": iid,
        "domain": macro,               # kept for smoke_driver compatibility
        "semantic_domain": macro,
        "operation": op,
        "language": lang,
        "surface_format": fmt,
        "answer_type": ans,
        "template_family": tfam,       # macro.sub (48) — reporting label
        "prompt_family": pfam,         # macro.sub.fill (240) — gate/bootstrap/split unit
        "split": split,
        "is_counterpart": is_cp,
        "counterpart_axis": cp_axis,
        "label": f"{pfam}{'_cp' if is_cp else ''}",
        "text_prompt": prompt,
        "text_target": target,
        "tiny_ids": tiny_ids,
        "tiny_n_prompt": tiny_np,
    }


def main():
    items, prompt_families, template_families = build()
    assert len(items) == 480, len(items)
    assert len(prompt_families) == 240, len(prompt_families)
    assert len(template_families) == 48, len(template_families)
    # repeat ids for the determinism gate: one discovery + one held_out item,
    # re-run with id+10000 (byte-identical routing check on Wave-A scale).
    disc = next(it["id"] for it in items if it["split"] == "discovery")
    held = next(it["id"] for it in items if it["split"] == "held_out")
    repeat_ids = [disc, held]
    corpus = {
        "_about": "GLM-5.2 Wave-A 480-item expert-profiling corpus. 12 macrodomains "
                  "x 4 template_families x 5 fills x (base + 1 controlled counterpart) = 480. "
                  "Fixed teacher-forced (text_prompt -> text_target). Orthogonal labels "
                  "per item; token_role/prompt_or_target derived per-token from the trace io "
                  "field. prompt_family (macro.sub.fill, 240) is the gate/bootstrap/split "
                  "unit; template_family (macro.sub, 48) is a reporting label. Split per fill "
                  "(3 discovery/1 dev/1 held_out) so every domain+template_family is in every "
                  "split. EXPLORATORY infra; content STIPULATED, not measured.",
        "_schema": "id, domain, semantic_domain, operation, language, surface_format, "
                   "answer_type, template_family, prompt_family, split, is_counterpart, "
                   "counterpart_axis, label, text_prompt, text_target, tiny_ids, tiny_n_prompt",
        "repeat_probe_ids": repeat_ids,
        "repeat_id_offset": 10000,
        "probes": items,
    }
    (HERE / "wave_a_corpus.json").write_text(json.dumps(corpus, ensure_ascii=False, indent=1))
    # manifest: label vocab + family/split map + counts
    def vocab(key):
        return sorted({it[key] for it in items})
    counts_split = {}
    for it in items:
        counts_split[it["split"]] = counts_split.get(it["split"], 0) + 1
    manifest = {
        "n_items": len(items),
        "n_base": sum(1 for it in items if not it["is_counterpart"]),
        "n_counterpart": sum(1 for it in items if it["is_counterpart"]),
        "n_prompt_families": len(prompt_families),
        "n_template_families": len(template_families),
        "macrodomains": list(CORPUS.keys()),
        "splits": counts_split,
        "families": prompt_families,          # keyed by prompt_family (gate/bootstrap/split unit)
        "template_families": template_families,
        "label_vocab": {
            "semantic_domain": vocab("semantic_domain"),
            "operation": vocab("operation"),
            "language": vocab("language"),
            "surface_format": vocab("surface_format"),
            "answer_type": vocab("answer_type"),
        },
        "repeat_probe_ids": repeat_ids,
        "repeat_id_offset": 10000,
    }
    (HERE / "corpus_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    # sanity: per-template-family split coverage (every domain+template_family in every split)
    per_tf_splits = {}
    for pf, meta in prompt_families.items():
        per_tf_splits.setdefault(meta["template_family"], set()).add(meta["split"])
    for tf, sp in per_tf_splits.items():
        assert {"discovery", "dev", "held_out"} <= sp, (tf, sp)
    print(f"OK: {len(items)} items, {len(prompt_families)} prompt_families, "
          f"{len(template_families)} template_families, splits={counts_split}")
    print(f"repeat ids={repeat_ids} (offset {manifest['repeat_id_offset']})")
    print("label vocab:")
    for k, v in manifest["label_vocab"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
