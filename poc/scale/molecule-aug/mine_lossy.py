#!/usr/bin/env python3
import json, glob, re, collections, os

GEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../consensus-100/gen')
files = sorted(f for f in glob.glob(os.path.join(GEN, '*.json')) if not f.endswith('.report.json'))

STOP = set('''a an the and or but of to in on at for with without from by as is are was were be been being
this that these those it its they them their there here he she his her him we you your i me my our us
not no nor so if then than when while where which who whom whose what how why can could would should shall
will may might must do does did done doing have has had having get gets got go goes went only just also very
more most much many some any all both each every either neither one two three several few less least own same
such other another into onto over under between among through during before after above below up down out off
again further once because until unless about against like via per etc rather instead thus hence therefore
however although though even still yet already'''.split())

META = set('''ast adequacy lossy faithful prime primes profile render renders rendered rendering
differentia differentiae cannot explication explications skeleton skeletons reads read reading readings
sense senses word words concept concepts meaning meanings term terms definition gloss synset wn wordnet
noun verb adjective adverb metalanguage nsm lexicon inventory carry carried carries carrying express
expressed expresses expressing expressible inexpressible capture captured captures capturing collapse
collapsed collapses collapsing lost lose loses losing loss drop dropped drops dropping unreachable
unavailable available lack lacks lacking lacked missing miss misses require requires required requiring
molecule molecules primitive primitives semantic semantically content notion notions idea ideas
distinction distinctions component components structure structures structural paraphrase paraphrased
represent represented represents representing representation reduce reduced reduces reducing reduction
irreducible encode encoded encodes encoding gesture gestures gestured proxy proxied proxies generic
vague vaguely weaker weakly weak strongly strong full fully exact exactly precise precisely core kind
kinds part parts something someone people thing things type types level mid-level flavor flavour
character preserved preserve preserves preserving retained retain remains remain remaining left leaves
leaving omitted omit omits omitting absent absence beyond within version versions form forms case cases
way ways underspecified unspecified target close closest near nearest best merely mere simply roughly
broadly narrow narrower broader itself themselves oneself cf note notes needs need needed used use uses
using usable placeholder placeholders schematic schema attempt attempts attempted specific specifically
approximate approximated approximates approximating approximation approximations
person persons person's good bad big small think thinking thinks thought know knowing knows known
want wanting wants wanted feel feeling feelings feels felt see seeing sees seen saw hear hearing hears
heard say saying says said true truly happen happening happens happened move moves moving moved touch
touching touches touched live living lives lived die dies died dying time times place places moment
moments body inside now maybe
act acts action actions acting actor mark marks marked marker markers criterial criterially
distinguish distinguished distinguishing distinguishes cause causes causing caused causal causation
agent agents agentive event events purpose purposes resulting result results resultant relation
relations relational condition conditions state states stative alternative alternatives disjunct
disjuncts disjunction disjunctive degree degrees bearer bearers specify specified specifies specifying
genus entail entails entailed entailment clause clauses predicate predicates argument arguments scope
negation negated iterated iteration habitual habitually sustained spatially spatial toward towards
afterward afterwards become becoming becomes became exist exists existing existence come comes coming
came make makes making made able ability long plus via especially explicit explicitly implicit
implicitly directly indirect indirectly particular particularly rendered. lossy. faithful. does doing
happening. specified. others another's specifics specification'''.split())

emdash_re = re.compile(r'^AST adequacy:\s*(lossy|faithful)\s*[—–-]+\s*', re.U)

records = []
for f in files:
    base = os.path.basename(f)[:-5]
    slug, model = base.rsplit('.', 1)
    d = json.load(open(f))
    note = (d.get('notes') or '').strip()
    m = emdash_re.match(note)
    if not m:
        continue
    records.append((slug, model, m.group(1), note[m.end():]))

lossy = [(s, mo, t) for s, mo, v, t in records if v == 'lossy']

# ---------- pass 1: content-word frequency (distinct notes containing word) ----------
tok_re = re.compile(r"[a-zA-Z][a-zA-Z\-']+")
word_notes = collections.defaultdict(set)
for slug, model, tail in lossy:
    for w in set(tok_re.findall(tail.lower())):
        w = w.strip("-'")
        if len(w) < 3 or w in STOP or w in META:
            continue
        word_notes[w].add((slug, model))

# merge plurals
merged = collections.defaultdict(set)
keys = set(word_notes)
for w, s in word_notes.items():
    base = w
    if w.endswith('ies') and w[:-3] + 'y' in keys: base = w[:-3] + 'y'
    elif w.endswith('es') and w[:-2] in keys: base = w[:-2]
    elif w.endswith('s') and not w.endswith('ss') and w[:-1] in keys: base = w[:-1]
    merged[base] |= s
wc = collections.Counter({w: len(s) for w, s in merged.items()})

print('=== TOTALS ===')
print('records_scanned:', len(records))
print('lossy_notes:', len(lossy))
print('faithful_notes:', len(records) - len(lossy))
print()
print('=== TOP 70 CONTENT WORDS (n distinct lossy notes) ===')
for w, c in wc.most_common(70):
    print(f'{w}: {c}')

# ---------- quoted-term extraction ----------
q_re = re.compile(r"'([a-zA-Z][a-zA-Z \-/]{1,30})'")
qc = collections.Counter()
for slug, model, tail in lossy:
    for q in set(m.group(1).lower() for m in q_re.finditer(tail)):
        qc[q] += 1
print()
print('=== TOP 50 QUOTED TERMS in lossy notes (n notes) ===')
for q, c in qc.most_common(50):
    print(f'{q}: {c}')

# ---------- domain buckets (anchored regexes) ----------
BUCKETS = {
 'money/payment/economic': r'\bmoney\b|\bmonetar|\bpayment|\bpay(?:s|ing)?\b|\bpaid\b|econom|financial|\bprice|\bcost(?:s|ly)?\b|\bdebt|\bowe(?:s|d)?\b|\bbuy(?:s|ing)?\b|\bsell(?:s|ing)?\b|\bsold\b|purchas|\bwage|\bsalar|currenc|commerc|\bmarket|\bwealth|\bincome|\bfund(?:s)?\b|\btax(?:es|ation|payer)?\b|\brefund|\bspend|\bearn',
 'law/legal/rule/government': r'\blaw(?:s|ful|fully)?\b|\blegal(?:ly|ity)?\b|\brule(?:s)?\b|regulat|\bcourt(?:s)?\b|\bcrime|\bcriminal|\bjustice\b|\bgovern|\bauthorit|\bofficial(?:s|ly)?\b|\bpolic(?:y|ies)\b|legislat|jurisdict|\bpermit(?:s|ted)?\b|prohibit|\bobligat|\bentitle|\bright(?:s)?\b|\bcontract(?:s|ual)?\b|\bjudicial|\btestimony\b|\bsworn\b|\boath\b|\bpunish',
 'institution/social-role/organization': r'\binstitution|\borgani[sz]ation|\bsocial(?:ly)?\b|\bconvention(?:s|al|ally)?\b|\bcommunit|\bmember(?:ship|s)?\b|\bclub(?:s)?\b|\bcollective|\bstatus\b|\bformal(?:ly|ized|ised)?\b|\brole(?:s)?\b|\bsociet',
 'art/aesthetic': r'\bart\b|\bartist|aesthetic|\bbeaut|\bpaint|\bsculpt|\bliterar|\bpoem|\bpoetr|\bnovel\b|\bfiction|\bcreative|\bcultural\b|\bculture\b',
 'tool/instrument/artifact/device': r'\btool(?:s)?\b|\bartifact|\bartefact|\bdevice(?:s)?\b|\bimplement(?:s)?\b|\bapparatus\b|\bequipment\b|\butensil|\binstrument(?:s)?\b|\bknife\b|\bblade\b|\bmachine(?:s|ry)?\b|\bappliance',
 'technology/energy/physics-domain': r'technolog|electr|\bheat(?:s|ed|ing)?\b|\bthermal\b|\benergy\b|\btemperature\b|\bburn(?:s|ed|ing|t)?\b|\bfire\b|\bcurrent\b|\bmechanism|\bmechanical',
 'material/substance': r'\bmaterial(?:s)?\b|\bsubstance(?:s)?\b|\bmetal(?:s|lic)?\b|\bwood(?:en)?\b|\bstone\b|\bglass\b|\bplastic\b|\bfabric\b|\bchemical(?:s)?\b|\bmineral|\bliquid(?:s)?\b|\bstuff\b',
 'language/writing/naming': r'\blanguage(?:s)?\b|linguistic|\bwrit(?:e|es|ing|ten)\b|\btext(?:s)?\b|\bletter(?:s)?\b|alphabet|\bgrammar|\bspeech\b|\bspoken\b|\butterance|\bname(?:s|d|less)?\b|\bnaming\b|\bsymbol(?:s|ic|ically)?\b|\blabel(?:s|ed|led)?\b|\bsign(?:s)?\b',
 'profession/occupation/work': r'\bprofession(?:al|s)?\b|\boccupation(?:al|s)?\b|\bjob(?:s)?\b|\bwork(?:s|er|ers)?\b|\blabor\b|\blabour\b|\bemploy|\btrade(?:sman)?\b|\bcraft(?:s)?\b|\bcareer|\bskill(?:s|ed|ful)?\b|\bexpert(?:ise)?\b|\bvocation|\bhabitual occupation|\btask(?:s)?\b|\bduty\b|\bduties\b|\bservice(?:s)?\b',
 'nation/country/political-place': r'\bnation(?:s|al|ality)?\b|\bcountry\b|\bcountries\b|\bcity\b|\bcities\b|\bterritor|\bgeograph|\bpolitical|\bborder(?:s)?\b|\bregion(?:s)?\b|\bethnic|\bpublic\b',
 'game/sport/competition': r'\bgame(?:s)?\b|\bsport(?:s)?\b|\bcompetit|\bcontest(?:s)?\b|\bteam(?:s)?\b|\bscore|\bwinner|\bprize|\brace\b|\belection|\bcandidac|\bnominat',
 'food/eating/cooking': r'\bfood(?:s)?\b|\beat(?:s|ing|en)?\b|\bdrink|\bmeal(?:s)?\b|\bcook(?:s|ed|ing)?\b|\bnutri|\btaste(?:s|d)?\b|\bflavor|\bflavour|\bkitchen\b|\bbread\b|\bspice|\bseason(?:s|ed|ing)?\b|\btoast(?:s|ed|ing)?\b|\bripe|\bfruit',
 'clothing/wearing': r'\bcloth(?:es|ing)\b|\bgarment|\bwear(?:s|ing)?\b|\bworn\b|\bdress(?:es|ed)?\b|\btextile',
 'building/dwelling': r'\bbuilding(?:s)?\b|\bhouse(?:s|hold)?\b|\bdwelling|\barchitect|\broom(?:s)?\b|\bwall(?:s)?\b|\bshelter|\bconstruct(?:ed|ion)\b',
 'marriage/kinship/family': r'\bmarri(?:age|ed|es)|\bkinship\b|\bfamily\b|\bfamilies\b|\bparent(?:s|al|hood)?\b|\bchild(?:ren)?\b|\bspous|\bwife\b|\bhusband\b|\brelative(?:s)?\b|\bkin\b|\binherit|\bheir(?:s)?\b|\boffspring\b|\bancestor',
 'religion/ritual': r'\breligio|\bsacred\b|\bholy\b|\britual(?:s|ly)?\b|\bgod(?:s)?\b|\bworship|\bspiritual|\bchurch|\bpray|\bceremon',
 'number/measurement/quantity': r'\bnumber(?:s|ed)?\b|\bcount(?:s|ing|ed)?\b|\bmeasur(?:e|es|ed|ing|ement|ements|able)\b|\bquantit|\bunit(?:s)?\b|\bscale(?:s|d)?\b|\bamount(?:s)?\b|arithmetic|mathemat|\bpercent|\bratio\b|\bmagnitude|\bnumeric|\bproportion|\brate(?:s)?\b|\bthreshold(?:s)?\b|\bgradab|\bgradient\b|\bquantif',
 'time/calendar/duration': r'\bcalendar|\byear(?:s|ly)?\b|\bday(?:s)?\b|\bhour(?:s)?\b|\bclock|\bdate(?:s)?\b|\bseason(?:al)?\b|\bmonth(?:s|ly)?\b|\bweek(?:s|ly)?\b|\bschedul|\bregular(?:ly|ity)?\b|\bperiodic|\brecurr|\bfrequen',
 'color/light-visual': r'\bcolo[u]?r(?:s|ed)?\b|\bbright(?:ness)?\b|\bshade\b|\bhue\b|\bbrown(?:s|ed|ing)?\b|\bvisual(?:ly)?\b',
 'animal/plant/biological': r'\banimal(?:s)?\b|\bplant(?:s)?\b|\bbiolog|\bspecies\b|\borganism(?:s)?\b|\bcreature(?:s)?\b|\bflesh\b|\borgan(?:s)?\b|\bblood\b|\bcell(?:s)?\b|\bgrow(?:s|th|ing)?\b|\bbirth\b|\bdeath\b|\bsex(?:ual|ually)?\b|\bmale(?:ness)?\b|\bfemale(?:ness)?\b|\bgender|\breproduc|\bpregnan|\bfertili|\bmating\b|\bbreed|\bgenetic|\bphysiolog|\bmetabol|\bdigest|\banatomi',
 'mind/emotion/cognition-rich': r'\bemotion(?:s|al|ally)?\b|\bmental(?:ly)?\b|\bcognit|\bbelief(?:s)?\b|\bmemory\b|\battention\b|\bdesire(?:s|d)?\b|\bintend(?:s|ed)?\b|\bintention(?:s|al|ally)?\b|\bconscious|\bpercept|\bimagin|\battitude(?:s)?\b|\bmotiv|\bwill(?:ing|ingness)?\b|\bvolition|\bdeliberate',
 'possession/exchange/transfer': r'\bpossess(?:es|ed|ion|ions|or)?\b|\bownership\b|\bproperty\b|\bbelong(?:s|ing|ings)?\b|\bexchange(?:s|d)?\b|\btransfer(?:s|red|ring)?\b|\bgift(?:s)?\b|\bborrow|\blend|\bsteal|\bstolen\b|\btheft\b|\bacqui(?:re|res|red|sition)|\breceiv(?:e|es|ed|ing)\b|\bkeep(?:s|ing)?\b|\bretain',
 'movement/travel/vehicle': r'\bvehicle(?:s)?\b|\btravel(?:s|ing|ling)?\b|\btransport|\bjourney|\bcar(?:s)?\b|\bship(?:s)?\b|\bboat(?:s)?\b|\broad(?:s)?\b|\bpath(?:s)?\b|\bdriv(?:e|es|ing|er|en)\b|\bride|\bherd(?:s|ing|ed)?\b',
 'war/violence/coercion': r'\bwar\b|\bweapon(?:s)?\b|\bfight(?:s|ing)?\b|\bbattle|\bviolen|\battack(?:s|ed|er)?\b|\bconflict|\bkill(?:s|ing|ed)?\b|\barmy\b|\bmilitary\b|\bforce(?:s|d|ful|fully)?\b|\bcoerc|\bthreat(?:s|en|ened|ening)?\b|\bharm(?:s|ed|ful|ing)?\b',
 'medicine/health': r'\bmedic(?:al|ine|ation|ations)?\b|\bhealth(?:y)?\b|\bdisease(?:s|d)?\b|\billness(?:es)?\b|\bsick(?:ness)?\b|\bdoctor(?:s)?\b|\bcure(?:s|d|ative)?\b|\btherap|\bdrug(?:s)?\b|\btreat(?:s|ed|ment|ments)?\b|\binjur|\bpain(?:ful)?\b|\bheal(?:s|ing|ed)?\b|\bsuffer(?:s|ing|ed)?\b|\bsymptom|\bdiagnos|\bpatient(?:s)?\b|\bwound|\bpalliat',
 'education/knowledge-systems': r'\beducat|\bteach(?:es|ing|er|ers)?\b|\bschool(?:s)?\b|\blearn(?:s|ing|ed)?\b|\bstudent(?:s)?\b|\binstruct(?:s|ion|ions|ed)?\b|\btrain(?:s|ing|ed)?\b|\bscience(?:s)?\b|\bscientif|\btheor(?:y|ies|etical)\b|\bdiscipline(?:s)?\b|academ|\bresearch\b|\bknowledge\b|\bexpertise\b',
 'physical-space/shape/configuration': r'\bflat(?:ness)?\b|\bshape(?:s|d)?\b|\bsurface(?:s)?\b|\bround(?:ed|ness)?\b|\bedge(?:s)?\b|\bthin\b|\bthick(?:ness)?\b|\bvertical(?:ly)?\b|\bhorizontal(?:ly)?\b|\bangle(?:s|d)?\b|\bgeometr|\borientation\b|\bposture\b|\bcontainer(?:s)?\b|\bboundar(?:y|ies)\b|\bslice(?:s|d)?\b|\bpiece(?:s)?\b|\bcut(?:s|ting)?\b|\blayer(?:s|ed)?\b',
 'communication/information': r'\bcommunicat|\binformation(?:al)?\b|\bmessage(?:s)?\b|\bsignal(?:s|ed|ing|ling)?\b|\bmedia\b|\bnews\b|\bbroadcast|\bannounc|\bnotif|\badvertis|\bposter(?:s)?\b|\bdocument(?:s|ed|ation)?\b|\brecord(?:s|ed|ing)?\b',
}

bucket_notes = collections.defaultdict(set)
bucket_concepts = collections.defaultdict(set)
for slug, model, tail in lossy:
    low = tail.lower()
    for b, pat in BUCKETS.items():
        if re.search(pat, low):
            bucket_notes[b].add((slug, model))
            bucket_concepts[b].add(slug)

print()
print('=== DOMAIN BUCKETS (lossy notes | distinct concepts) ===')
for b, s in sorted(bucket_notes.items(), key=lambda kv: -len(kv[1])):
    print(f'{b}: {len(s)} notes | {len(bucket_concepts[b])} concepts')

# ---------- candidate covering ENGLISH WORDS ----------
CANDIDATES = {
 'money': r'\bmoney\b|\bmonetar|\bcurrenc|\bfinancial\b',
 'pay': r'\bpay(?:s|ing|ment|ments)?\b|\bpaid\b',
 'buy/sell': r'\bbuy(?:s|ing)?\b|\bsell(?:s|ing)?\b|\bsold\b|\bpurchas|\bcommerc|\bmarket\b|\btrade\b',
 'cost/price/worth': r'\bprice(?:s|d)?\b|\bcost(?:s|ly)?\b|\bworth\b|\bvalue(?:s|d)?\b|\bvaluable\b|\bwealth\b|\bexpensive',
 'owe/debt': r'\bowe(?:s|d)?\b|\bdebt(?:s|or)?\b',
 'law': r'\blaw(?:s|ful|fully)?\b|\blegal(?:ly|ity)?\b|\bjudicial\b|\bjurisdict',
 'rule/regulation': r'\brule(?:s)?\b|\bregulat|\bnorm(?:s|ative)?\b',
 'right/entitlement': r'\bright(?:s)?\b|\bentitle(?:d|ment|ments)?\b|\bpermit(?:s|ted)?\b|\bpermission\b',
 'government/authority': r'\bgovern(?:ment|ments|ing|ed)?\b|\bauthorit(?:y|ies|ative)\b|\bofficial(?:s|ly)?\b|\bcourt(?:s)?\b|\binstitutional authority',
 'crime/punish': r'\bcrime(?:s)?\b|\bcriminal(?:s|ity)?\b|\bpunish(?:es|ed|ment|ments)?\b|\bjustice\b|\bguilt(?:y)?\b|\boffense|\boffence|\bwrongdo',
 'duty/obligation': r'\bduty\b|\bduties\b|\bobligat(?:ion|ions|ed|ory)?\b|\bresponsib|\bowe(?:s|d)? (?:a )?dut',
 'promise/agreement/contract': r'\bpromise(?:s|d)?\b|\bagree(?:ment|ments|d)?\b|\bcontract(?:s|ual)?\b|\bcommit(?:ment|ments)?\b|\boath\b|\bvow(?:s)?\b|\bsworn\b|\bpledge',
 'institution': r'\binstitution(?:s|al|ally|alized|alised)?\b',
 'organization/group(formal)': r'\borgani[sz]ation(?:s|al)?\b|\bclub(?:s)?\b|\bassociation(?:s)?\b|\bcollective(?:ly)?\b',
 'member(ship)': r'\bmember(?:s|ship|ships)?\b',
 'role/status(social)': r'\brole(?:s)?\b|\bstatus\b|\bposition(?:s)?\b|\brank(?:s)?\b|\btitle(?:s)?\b',
 'formal/official-procedure': r'\bformal(?:ly|ized|ised|ity)?\b|\bprocedure(?:s|al)?\b|\bprocess(?:es)? (?:of )?(?:law|selection|appointment)|\bappoint(?:ed|ment|ments)?\b|\bnominat|\belect(?:ion|ed|oral)?\b|\bcandidac',
 'work/job': r'\bwork(?:s|er|ers)?\b|\bjob(?:s)?\b|\boccupation(?:al|s)?\b|\bprofession(?:al|s)?\b|\bemploy(?:er|ee|ment|ed)?\b|\bvocation|\blabor\b|\blabour\b',
 'skill/craft/expert': r'\bskill(?:s|ed|ful)?\b|\bcraft(?:s)?\b|\bexpert(?:ise|s)?\b|\btrained\b|\bpractice(?:s|d)?\b|\bproficien',
 'country/nation': r'\bcountry\b|\bcountries\b|\bnation(?:s|al|ality)?\b|\bterritor|\bpolitical\b|\bethnic\b',
 'public/community': r'\bpublic(?:ly)?\b|\bcommunit(?:y|ies)\b|\bsociet(?:y|ies|al)\b|\bsocial(?:ly)?\b',
 'write': r'\bwrit(?:e|es|ing|ten)\b|\btext(?:s)?\b|\bdocument(?:s|ed|ation)?\b|\brecord(?:s|ed|ing)?\b|\binscri',
 'name/word/symbol': r'\bname(?:s|d|less)?\b|\bnaming\b|\bsymbol(?:s|ic|ically)?\b|\blabel(?:s|ed|led)?\b|\bsign(?:s)?\b|\bletter(?:s)?\b',
 'language': r'\blanguage(?:s)?\b|\blinguistic|\bspeech\b|\bspoken\b|\butterance',
 'count/number': r'\bnumber(?:s|ed)?\b|\bcount(?:s|ing|ed)?\b|\bnumeric|\barithmetic|\bmathemat|\bquantif',
 'measure/unit/scale': r'\bmeasur(?:e|es|ed|ing|ement|ements|able)\b|\bunit(?:s)?\b|\bscale(?:s|d)?\b|\bquantit|\bmagnitude|\bamount(?:s)?\b|\bdegree of\b|\bgradab|\bthreshold',
 'food': r'\bfood(?:s)?\b|\bmeal(?:s)?\b|\bnutri|\bedible\b',
 'cook/kitchen': r'\bcook(?:s|ed|ing)?\b|\bkitchen\b|\btoast(?:s|ed|ing)?\b|\bbake|\bheat(?:s|ed|ing)? (?:food|until)',
 'taste/flavor': r'\btaste(?:s|d)?\b|\bflavor|\bflavour|\bspice|\bseasoning\b|\bsalt(?:y)?\b|\bsweet\b|\bbitter\b',
 'eat/drink': r'\beat(?:s|ing|en)?\b|\bdrink(?:s|ing)?\b|\bswallow|\bingest',
 'tool/instrument': r'\btool(?:s)?\b|\binstrument(?:s)?\b|\butensil|\bimplement(?:s)?\b|\bblade\b|\bknife\b',
 'machine/device': r'\bmachine(?:s|ry)?\b|\bdevice(?:s)?\b|\bappliance(?:s)?\b|\bapparatus\b|\bequipment\b|\bmechanism(?:s)?\b|\bmechanical\b|\bautomat',
 'electricity/heat/energy': r'\belectr|\bheat(?:s|ed|ing)?\b|\bthermal\b|\benergy\b|\btemperature\b|\bcurrent\b|\bpower(?:ed)?\b',
 'material': r'\bmaterial(?:s)?\b|\bstuff\b|\bwood(?:en)?\b|\bmetal(?:s|lic)?\b|\bstone\b|\bfabric\b|\bplastic\b',
 'substance(chemical)': r'\bsubstance(?:s)?\b|\bchemical(?:s)?\b|\bliquid(?:s)?\b|\bmineral',
 'body-part/organ': r'\borgan(?:s)?\b|\bflesh\b|\bblood\b|\banatomi|\bbodily\b|\bmouth\b|\bhand(?:s)?\b|\bskin\b',
 'grow/alive(biology)': r'\bgrow(?:s|th|ing)?\b|\bbiolog|\borganism(?:s)?\b|\bspecies\b|\bgenetic|\bphysiolog|\bmetabol|\breproduc|\bbirth\b|\bpregnan|\bfertili|\bmating\b|\bbreed',
 'male/female/sex': r'\bmale(?:ness)?\b|\bfemale(?:ness)?\b|\bsex(?:ual|ually)?\b|\bgender',
 'animal': r'\banimal(?:s)?\b|\bcreature(?:s)?\b|\blivestock\b|\bcattle\b|\bherd(?:s|ing|ed)?\b',
 'plant': r'\bplant(?:s)?\b|\bcrop(?:s)?\b|\bfruit(?:s)?\b|\bripe(?:n|ness)?\b',
 'kill/death(caused)': r'\bkill(?:s|ing|ed)?\b|\bdeath\b(?!.{0,10}prime)|\beuthanasia\b|\bmurder|\bfatal',
 'illness/medicine': r'\bmedic(?:al|ine|ation|ations)?\b|\bdisease(?:s|d)?\b|\billness(?:es)?\b|\bsick(?:ness)?\b|\bdoctor(?:s)?\b|\bcure(?:s|d)?\b|\btherap|\bdrug(?:s)?\b|\bsymptom|\bdiagnos|\bpatient(?:s)?\b|\bsuffering\b|\bpain(?:ful)?\b|\bpalliat|\bheal(?:s|ing)?\b|\btreat(?:s|ed|ment|ments)?\b',
 'own/possess/property': r'\bpossess(?:es|ed|ion|ions|or)?\b|\bownership\b|\bproperty\b|\bbelong(?:s|ing|ings)?\b',
 'give/receive/transfer': r'\btransfer(?:s|red|ring)?\b|\bexchange(?:s|d)?\b|\bgift(?:s)?\b|\breceiv(?:e|es|ed|ing)\b|\bacqui(?:re|res|red|sition)|\bborrow|\blend|\binherit',
 'steal/take-wrongly': r'\bsteal(?:s|ing)?\b|\bstolen\b|\btheft\b|\bseiz(?:e|ed|ure)|\bransom\b|\babduct|\bkidnap',
 'marry/spouse': r'\bmarri(?:age|ed|es)\b|\bspous(?:e|es|al)\b|\bwife\b|\bhusband\b|\bwed(?:ding)?\b|\bdivorce',
 'family/kin/heir': r'\bfamily\b|\bfamilies\b|\bkin(?:ship)?\b|\bparent(?:s|al|hood)?\b|\bchild(?:ren)?\b|\brelative(?:s)?\b|\bheir(?:s)?\b|\bancestor|\boffspring\b|\bgeneration(?:s)?\b',
 'house/building/room': r'\bbuilding(?:s)?\b|\bhouse(?:s|hold)?\b|\bdwelling|\broom(?:s)?\b|\bwall(?:s)?\b|\bdoor(?:s|way)?\b|\bindoor|\bshelter',
 'vehicle/travel': r'\bvehicle(?:s)?\b|\btravel(?:s|ing|ling)?\b|\btransport|\bjourney|\bdriv(?:e|es|ing|er|en)\b|\bride|\bcar(?:s)?\b|\broad(?:s)?\b',
 'fight/attack/threat': r'\bfight(?:s|ing)?\b|\battack(?:s|ed|er)?\b|\bviolen|\bthreat(?:s|en|ened|ening)?\b|\bcoerc|\bforce(?:s|d)? (?:someone|a person|them)|\bweapon(?:s)?\b|\bwar\b|\bharm(?:s|ed|ful|ing)?\b',
 'game/play/compete': r'\bgame(?:s)?\b|\bsport(?:s)?\b|\bplay(?:s|ing|er|ers)?\b|\bcompetit|\bcontest(?:s|ants)?\b|\bwin(?:ner|ning)?\b|\bprize(?:s)?\b|\brace\b',
 'art/beauty': r'\bart\b|\bartist(?:s|ic|ically)?\b|\baesthetic|\bbeaut(?:y|iful)\b|\bcultural refinement|\bculture\b|\bcultural\b',
 'religion/ritual': r'\breligio|\bsacred\b|\bholy\b|\britual(?:s|ly)?\b|\bworship|\bceremon|\bpray|\bgod(?:s)?\b',
 'teach/learn/school': r'\bteach(?:es|ing|er|ers)?\b|\blearn(?:s|ing|ed)?\b|\bschool(?:s)?\b|\beducat|\bstudent(?:s)?\b|\btrain(?:s|ing|ed)?\b|\binstruct(?:s|ion|ions|ed)?\b',
 'know-how/science': r'\bscience(?:s)?\b|\bscientif|\btheor(?:y|ies|etical)\b|\bknowledge\b|\bdiscipline(?:s)?\b|\bacadem|\bresearch\b',
 'clothing/wear': r'\bcloth(?:es|ing)\b|\bgarment|\bwear(?:s|ing)?\b|\bworn\b|\bdress(?:es|ed)?\b',
 'container/hold': r'\bcontainer(?:s)?\b|\bvessel(?:s)?\b|\bbox(?:es)?\b|\bbag(?:s)?\b|\bstore(?:s|d)?\b|\bstorage\b',
 'surface/flat/shape': r'\bflat(?:ness)?\b|\bsurface(?:s)?\b|\bshape(?:s|d)?\b|\bround(?:ed)?\b|\bedge(?:s)?\b|\bthin\b|\bthick(?:ness)?\b|\bslice(?:s|d)?\b|\blayer(?:s|ed)?\b',
 'clean/dirty': r'\bclean(?:s|ing|ed|liness)?\b|\bdirt(?:y|iness)?\b|\bwash(?:es|ed|ing)?\b|\bwaste\b|\bexcre|\bsanit|\bhygien|\btoilet',
 'sound/music': r'\bsound(?:s)?\b|\bnoise\b|\bloud\b|\bacoustic|\bauditory\b|\bmusic(?:al)?\b|\bsong(?:s)?\b|\bmelod',
 'color/brown': r'\bcolo[u]?r(?:s|ed)?\b|\bbrown(?:s|ed|ing)?\b|\bhue\b|\bshade\b',
 'regular/schedule(time)': r'\bregular(?:ly|ity)?\b|\bschedul|\bperiodic|\brecurr|\bfrequen|\broutine|\bcalendar|\bdaily\b|\byear(?:s|ly)?\b|\bmonth(?:s|ly)?\b|\bweek(?:s|ly)?\b',
 'watch/guard/protect': r'\bwatch(?:es|ing|ful)?\b|\bguard(?:s|ing|ed)?\b|\bprotect(?:s|ion|ing|ed|ive)?\b|\bvigilan|\blookout\b|\bsafe(?:ty)?\b|\bdanger(?:ous)?\b|\brisk(?:s|y)?\b',
 'lead/supervise': r'\bsupervis|\boversee(?:s|ing|r)?\b|\bmanage(?:s|d|ment|r)?\b|\bdirect(?:s|ing|or)?\b|\bcontrol(?:s|led|ling)?\b|\bcommand(?:s)?\b|\blead(?:s|er|ership|ing)?\b|\bcharge of\b',
 'help/serve': r'\bhelp(?:s|ing|ed|ful)?\b|\bserve(?:s|d)?\b|\bservice(?:s)?\b|\bassist|\bbenefit(?:s)?\b|\bcare(?:s|d)? for\b|\bcaring\b|\bcaretak',
}

note_sets = collections.defaultdict(set)
for slug, model, tail in lossy:
    low = tail.lower()
    for c, pat in CANDIDATES.items():
        if re.search(pat, low):
            note_sets[c].add((slug, model))

print()
print('=== CANDIDATE WORDS (lossy notes addressed | concepts) ===')
for c, s in sorted(note_sets.items(), key=lambda kv: -len(kv[1]))[:60]:
    cons = len(set(x[0] for x in s))
    print(f'{c}: {len(s)} notes | {cons} concepts')

covered = set()
pool = dict(note_sets)
print()
print('=== GREEDY SET-COVER ORDER (top 40; word: +marginal, cumulative) ===')
for _ in range(40):
    best, gain = None, 0
    for c, s in pool.items():
        g = len(s - covered)
        if g > gain: best, gain = c, g
    if not best: break
    covered |= pool.pop(best)
    print(f'{best}: +{gain} (cum {len(covered)}/{len(lossy)})')

# ---------- per-concept ----------
per_concept = collections.Counter()
for slug, model, tail in lossy:
    per_concept[slug] += 1
all_slugs = sorted(set(s for s, m, v, t in records))
dist = collections.Counter(per_concept.values())
print()
print('=== PER-CONCEPT LOSSY RECURRENCE ===')
for k in sorted(dist, reverse=True):
    print(f'{k}_of_6_models_lossy: {dist[k]} concepts')
print(f'0_models_lossy: {len(all_slugs)-len(per_concept)} concepts')
print('concepts_total:', len(all_slugs))
print('unanimous_lossy_concepts:', sorted(s for s, c in per_concept.items() if c == 6))

midlevel = collections.Counter()
midwords = collections.defaultdict(collections.Counter)
for slug, model, tail in lossy:
    low = tail.lower()
    hits = [c for c, pat in CANDIDATES.items() if re.search(pat, low)]
    if hits:
        midlevel[slug] += 1
        for h in hits: midwords[slug][h] += 1
print()
print('=== TOP 30 CONCEPTS whose lossy notes most often name a missing mid-level word ===')
for slug, n in midlevel.most_common(30):
    top = ','.join(w for w, _ in midwords[slug].most_common(4))
    print(f'{slug}: {n}/{per_concept[slug]} [{top}]')
