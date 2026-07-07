#!/usr/bin/env python3
"""haiku-tier stage 1 — prompt builder.

Builds the framework system prompts (static => API-prompt-cacheable across
calls) and the per-concept user prompts, and records promptVersionHash =
sha256 of each exact rendered system-prompt template.

Frameworks:
  A  molecule-first, single pass
  B  explication-first, single pass
  C  = A + a second blind self-check/repair pass (system-C.txt)
  D  = A + hardened prompt (trap list + final-audit instruction)
  E  = D + blind self-check (system-C.txt; wired in run-s1.py)
  F  = A + repair-first blind self-check (system-F.txt)
  G  = A + gate-in-the-loop repair (system-F.txt + real validator errors
      appended to the user turn; wired in run-s1.py) — the s1 winner

The molecule cheat-sheet reproduces the mechanical rules of
concept-hash-design.md §3.5 as pinned by data/molecules-v0/validate.mjs
(ALLOWED lexicon / PHRASES / punctuation / ref syntax / [m] flag / depth).
The explication cheat-sheet mirrors kot-ast/1 (encoder/src/ast.ts) and the
closed §4 inventories (encoder/src/lexicon.ts).
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DEFS = os.path.join(HERE, '..', 'cache', 'defs')
OUT = os.path.join(HERE, 'prompts')
os.makedirs(os.path.join(OUT, 'user'), exist_ok=True)

# --- ref catalog: kernel-v0 (depth 0) + molecules-v0 depth<=3 ----------------
kman = json.load(open(os.path.join(REPO, 'data', 'kernel-v0', 'manifest.json')))
mman = json.load(open(os.path.join(REPO, 'data', 'molecules-v0', 'manifest.json')))
kernel_ids = []
for c in kman['concepts']:
    slug = c['id'].rsplit(':', 1)[1]
    kernel_ids.append((c['id'], slug))
mol_ids = []
for m in mman['molecules']:
    rec = json.load(open(os.path.join(REPO, 'data', 'molecules-v0', m['file'])))
    if rec['moleculeDepth'] <= 3:
        mol_ids.append((rec['id'], rec['label'], rec['moleculeDepth']))
catalog = ('KERNEL CONCEPTS (explicated, depth 0 — usable in grounding notes '
           'as {urn|gloss} WITHOUT [m]; usable in explications as concept refs):\n')
catalog += '  ' + ', '.join(f'{i}' for i, s in kernel_ids) + '\n\n'
catalog += ('MOLECULES (usable in grounding notes as {urn|gloss} [m]; NOT usable '
            'inside explications; depth shown — your new molecule gets depth = '
            '1 + max(depth of refs; kernel refs count 0), and must stay <= 4):\n')
catalog += '  ' + ', '.join(f'{i}(d{d})' for i, l, d in mol_ids) + '\n'

# --- molecule lexicon (verbatim from data/molecules-v0/validate.mjs) ----------
src = open(os.path.join(REPO, 'data', 'molecules-v0', 'validate.mjs')).read()
STR_LIT = r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\""  # both quote styles ("someone's"!)
def grab_strings(body):
    return [a or b for a, b in re.findall(STR_LIT, body)]
def grab_set(name):
    m = re.search(name + r' = new Set\(\[(.*?)\]\)', src, re.S)
    return grab_strings(m.group(1))
ALLOWED = grab_set('ALLOWED')
m = re.search(r'const PHRASES = \[(.*?)\]', src, re.S)
PHRASES = grab_strings(m.group(1))

MOLECULE_SHEET = f"""## Molecule grounding notes — the mechanical rules (gist §3.5)

A molecule is a concept anchored by ONE grounding note written in a CLOSED
controlled lexicon. The gate rejects anything else. Rules:

1. The note is lowercase, NFC, <= 1024 bytes.
2. Every whitespace-separated token must be one of:
   (a) a word from the ALLOWED list below,
   (b) one of the allowed PHRASES below (as a whole phrase),
   (c) punctuation from: . , ; : ( )
   (d) a linked reference {{urn:...|gloss}} to a catalog concept; if the ref
       is a molecule (urn:molecule-v0:...) it MUST be followed by " [m]";
       kernel refs (urn:kernel-v0:...) must NOT carry [m].
   ANY other bare content word (e.g. "bark", "metal", "liquid") is an
   automatic gate failure ERR_GROUNDING_LEXICON.
3. Refs must come from the catalog only, never the concept being defined
   itself. New-molecule depth = 1 + max(ref depths) must be <= 4.
4. Say what the thing IS using kind-statements, what people do with it, what
   it does, where it is — all in ALLOWED words + refs. No synonyms, no
   examples-in-English, no quotation marks.

ALLOWED = {' '.join(ALLOWED)}

PHRASES = {' | '.join(PHRASES)}
"""

EXPLICATION_SHEET = """## Explications — kot-ast/1 strict JSON (profile-1 grammar, gist §4)

An explication is: {"schema":"kot-ast/1","frame":F,"referents":[...],"clauses":[...]}

FRAMES (F): "InstanceSchema" (class concepts; referent 1 = an arbitrary
instance, frame-implicit), "WhenTrue" (property concepts; referent 1 = the
thing the property holds of), "RelationalSchema" (relations; referents 1,2 =
subject and object, both frame-implicit).

REFERENTS: [{"index":n,"refKind":K}], K in {"SomeoneRef","SomethingRef",
"TimeRef","PlaceRef","ClauseRef"}; indices dense from 1; <= 32. Frame-implicit
referents (1; also 2 for RelationalSchema) are introduced by the frame. Every
OTHER referent needs exactly one introducing occurrence: an SP carrying
"bind":n. Later mentions are {"kind":"ref","index":n}.

CLAUSES (ordered list; <= 32 total incl. embedded):
  pred clause: {"type":"pred","pred":P,"roles":{role:filler,...}}
  op clause:   {"type":"op","op":O,"args":[...]}

PREDICATES P with valency (req*, opt; all also allow adjuncts
time/duration/place/manner):
  DO agent*, undergoer, instrument, comitative | HAPPEN undergoer |
  MOVE undergoer* | THINK experiencer*, topic, quote |
  KNOW experiencer*, topic, complement(clause) |
  WANT experiencer*, complement*(clause or SP) | DON'T-WANT same |
  FEEL experiencer*, attribute(GOOD/BAD prime filler) |
  SEE experiencer*, stimulus* | HEAR experiencer*, stimulus* |
  SAY agent*, addressee, topic, quote | TRUE undergoer*(ref to ClauseRef or quote) |
  BE-SOMEWHERE undergoer*, locus* | THERE-IS undergoer* |
  BE-SPEC undergoer*, attribute*(SP or KIND-frame) |
  IS-MINE undergoer*, possessor*(I only) | LIVE undergoer* | DIE undergoer*

OPERATORS O (args are clauses unless said):
  NOT(clause) CAN(clause) MAYBE(clause) IF(antecedent,consequent)
  BECAUSE(cause,effect) WHEN(time-clause,main) LIKE(comparandum,target: SP or
  clause) AFTER(anchor: time SP/ref/NOW-prime, scope-clause) BEFORE(same)

FILLERS:
  SP: {"kind":"sp","det"?,"quant"?,"mods"?,"head":H,"restrictedBy"?:clause,"bind"?:n}
    det in {"THIS","THE-SAME","OTHER~ELSE~ANOTHER","SOME"};
    quant in {"ONE","TWO","SOME","ALL","MUCH~MANY","LITTLE~FEW"};
    mods: [{"mod":M,"intensifier"?:"VERY"|"MORE"}], M in {"GOOD","BAD","BIG","SMALL"};
    head H: {"kind":"primeHead","prime":S} with S a substantive prime from
      {"I","YOU","SOMEONE","SOMETHING~THING","PEOPLE","BODY","WORDS",
       "WHEN~TIME","WHERE~PLACE","MOMENT","SIDE"}
      | {"kind":"kindFrame","of":SP-or-conceptref-or-ref}   ("X of one kind")
      | {"kind":"partFrame","of":...}
      | {"kind":"refHead","index":n}
      | {"kind":"conceptHead","id":"urn:kernel-v0:..."}  (catalog kernel ids only)
  ref mention: {"kind":"ref","index":n}
  prime filler: {"kind":"prime","prime":"NOW"|"HERE"|"I"|"YOU"|"GOOD"|"BAD"|
    "A-LONG-TIME"|"A-SHORT-TIME"|"FOR-SOME-TIME"|"MOMENT"}
  concept ref: {"kind":"concept","id":"urn:kernel-v0:..."} (catalog only; never
    molecules, never the concept being defined)
  embedded clause: {"kind":"clause","clause":C}
  quote: {"kind":"quote","clauses":[...]} (I/NOW re-anchor to the quoted person/moment)
  temporal anchor (as time adjunct): {"kind":"temporal","op":"AFTER"|"BEFORE",
    "anchor":SP-or-ref-or-NOW-prime}

Structural nesting depth <= 12. Primes are UPPERCASE names as shown
(SOMETHING~THING, MUCH~MANY, WHEN~TIME, OTHER~ELSE~ANOTHER etc. are single
prime names with allolexes; use the full name string).
"""

# --- few-shot exemplars -------------------------------------------------------
def kernel_exemplar(slug):
    d = json.load(open(os.path.join(REPO, 'data', 'kernel-v0', 'concepts', slug + '.json')))
    return json.dumps({'kind': 'explication', 'gloss': d['gloss'],
                       'record': d['explication']}, separators=(',', ':'))
def mol_exemplar(slug):
    d = json.load(open(os.path.join(REPO, 'data', 'molecules-v0', 'molecules', slug + '.json')))
    return json.dumps({'kind': 'molecule', 'gloss': d['groundingNote'][:60] + '...',
                       'groundingNote': d['groundingNote'],
                       'groundingRefs': d['groundingRefs']}, separators=(',', ':'))

EXEMPLARS = f"""## Worked examples (exact output format)

concept "alive" ->
{kernel_exemplar('alive')}

concept "has-part" ->
{kernel_exemplar('has-part')}

concept "event" ->
{kernel_exemplar('event')}

concept "rabbit" ->
{mol_exemplar('rabbit')}

concept "walk" ->
{mol_exemplar('walk')}

concept "electron" ->
{json.dumps({'kind': 'cannot-formalise', 'why': 'a technical-physics kind: its identity conditions (charge, mass, quantum behaviour) are not expressible in the prime lexicon or as a grounding note over the available catalog concepts; it belongs to the physics sector, not this tier'}, separators=(',', ':'))}
"""

CONTRACT = """## Output contract

Reply with EXACTLY ONE raw JSON object (no markdown fences, no commentary):
  {"kind":"explication","gloss":"<one-line plain gloss>","record":{...kot-ast/1...}}
or
  {"kind":"molecule","gloss":"<one-line plain gloss>","groundingNote":"...",
   "groundingRefs":["urn:...","..."]}
or
  {"kind":"cannot-formalise","why":"<honest one-paragraph reason>"}

Honesty rules: a wrong or gate-failing record is WORSE than cannot-formalise.
If the concept is a proper name, an interjection/discourse particle, a
grammar word, culture-bound slang with no stable everyday sense, or needs
technical/scientific grounding the catalog cannot give — say cannot-formalise.
Define the single dominant everyday sense only.
"""

ROUTE_A = """## Route choice (molecule-first)

Decide in this order:
1. Concrete things, kinds of things, body parts, percepts, bodily actions,
   artefacts, places, substances, times of day, kinship => a MOLECULE
   grounding note (most concepts land here).
2. Only if the concept is fully expressible in bare primes — mental states,
   speech acts, simple relations/properties/events — write an EXPLICATION.
3. Otherwise => cannot-formalise.
"""

ROUTE_B = """## Route choice (explication-first)

Decide in this order:
1. Try hard to write a profile-1 EXPLICATION in bare primes (mental states,
   speech acts, relations, properties, simple events all belong here).
2. Only if the meaning irreducibly involves concrete kinds/percepts the primes
   cannot reach, write a MOLECULE grounding note instead.
3. Otherwise => cannot-formalise.
"""

HEAD = """You are a semantic-primitive lexicographer for the "Kernel of Truth"
programme. Given one English concept plus dictionary/encyclopedia text, you
produce a machine-gated formal definition record. Every output is checked by
fail-closed mechanical validators; only gate-legal records are useful.
"""

HARDENING = """## Common gate failures — avoid these exactly

Grounding-note traps (each has failed real drafts):
- "and", "or", "but", "so", "often", "usually", "sometimes", "has", "have",
  "get", "use", "well" are NOT allowed. Use ";" instead of "and"/"or"; use
  "at many times" for often; re-express possession as "there is X, it is a
  part of Y" or with "of".
- Number words other than "one"/"two" (e.g. "four") are NOT allowed — use
  "some" or "many".
- If a content word names a catalog concept (water, animal, mouth, fire,
  color, hand, food, ...), you MUST write it as a linked ref like
  {urn:molecule-v0:water|water} [m] — the bare word is illegal. If a content
  word has NO catalog entry (e.g. "blood", "metal", "leg"), you cannot use it
  at all: re-express it with ALLOWED words, or reconsider the route.
- Every molecule ref needs " [m]" after the closing brace; kernel refs never
  take [m]. groundingRefs must list exactly the urns used in the note.

Explication traps:
- Only RelationalSchema gives you referent 2 implicitly. In InstanceSchema and
  WhenTrue every referent except 1 must be introduced with "bind":n on an SP
  before any {"kind":"ref","index":n} use.
- Roles must come from the predicate's valency table exactly ("cause",
  "reason", "goal" are NOT roles; use BECAUSE(cause-clause, effect-clause)).
- FEEL attribute is only a GOOD or BAD prime filler.
- Primes must be spelled exactly as listed (no WOMAN, no MAN — they are not
  primes; use {"kind":"concept","id":"urn:kernel-v0:..."} refs for kernel
  concepts like woman/man... only if present in the catalog).

MANDATORY FINAL STEP before you answer: re-read your draft token by token.
For a molecule note, check EVERY word: is it in ALLOWED, part of an allowed
PHRASE, punctuation (. , ; : ( )), or inside a {urn|gloss} ref? For an
explication, check every referent index, role name, prime spelling, operator
arity. Check the JSON braces balance. Fix everything before emitting. Output
raw JSON only.
"""

sys_A = '\n'.join([HEAD, ROUTE_A, MOLECULE_SHEET, EXPLICATION_SHEET,
                   '## Catalog of referenceable concepts\n\n' + catalog,
                   EXEMPLARS, CONTRACT])
sys_B = '\n'.join([HEAD, ROUTE_B, MOLECULE_SHEET, EXPLICATION_SHEET,
                   '## Catalog of referenceable concepts\n\n' + catalog,
                   EXEMPLARS, CONTRACT])
sys_C = '\n'.join([HEAD, """## Self-check pass

You will be given a concept and a DRAFT definition record produced earlier.
Check the draft against every rule below. If it passes, return it unchanged.
If it violates any rule, return a corrected record (you may change kind —
including downgrading to cannot-formalise if the concept cannot be made
legal). Never introduce new violations. Frequent draft errors: bare content
words in grounding notes (each must be an ALLOWED word, phrase, punctuation,
or {urn|gloss} ref); missing " [m]" after molecule refs; [m] wrongly added
to kernel refs; refs not in the catalog; self-reference; groundingRefs list
not matching the refs used in the note; uppercase letters in the note;
explication roles/args that break the valency/arity tables; undeclared or
non-dense referent indices; missing "bind" on the introducing SP.
""", MOLECULE_SHEET, EXPLICATION_SHEET,
                   '## Catalog of referenceable concepts\n\n' + catalog, CONTRACT])

sys_D = '\n'.join([HEAD, ROUTE_A, HARDENING, MOLECULE_SHEET, EXPLICATION_SHEET,
                   '## Catalog of referenceable concepts\n\n' + catalog,
                   EXEMPLARS, CONTRACT])

# F: revised self-check — targets the two behaviours measured in C:
# (1) CF-inflation: downgrading repairable concrete concepts to
#     cannot-formalise; (2) hallucinated non-catalog refs.
sys_F = '\n'.join([HEAD, """## Self-check pass (repair-first)

You will be given a concept and a DRAFT definition record produced earlier.
Repair it so it passes every rule below, then return the repaired JSON.

REPAIR, DON'T ABSTAIN: downgrade to cannot-formalise ONLY if the concept is a
proper name, an interjection/discourse particle, a grammar word, or needs
technical/scientific grounding (physics/maths). For EVERY everyday thing,
kind, action, or property, the ALLOWED vocabulary plus the catalog IS enough
— a simpler, shorter, gate-legal note that says less is better than
abstaining or than a rich note that fails the gate. (The hand-authored corpus
proves dogs, colours, food, sleep, houses are all expressible.)

Repair procedure for a molecule note:
1. Go word by word. Keep a word only if it is in ALLOWED, inside one of the
   PHRASES, punctuation (. , ; : ( )), or inside a {urn|gloss} ref.
2. "and"/"or" become ";". Number words other than one/two become "some" or
   "many". Verbs must be the exact ALLOWED forms (moves, touches, says...).
3. A bare content word that names a CATALOG concept becomes a ref:
   {urn:molecule-v0:X|X} [m] for molecules, {urn:kernel-v0:X|X} for kernel.
   NEVER invent a urn: if it is not in the catalog list below, IT DOES NOT
   EXIST (there is no blood, moon, wind, instrument, plant, leg, ...). A
   non-catalog content word must be re-expressed with ALLOWED words or the
   clause dropped.
4. groundingRefs must list exactly the urns that appear in the note.
5. The whole note is lowercase; every molecule ref is followed by " [m]".

Repair procedure for an explication: check frame choice (RelationalSchema
only for two-argument relations; it gives referents 1 and 2 implicitly; in
other frames every referent except 1 needs "bind":n on its introducing SP
before use), role names against the valency tables, operator arity, prime
spellings, JSON brace balance. If a clause cannot be made legal, drop it —
a shorter legal explication beats a broken rich one.
""", MOLECULE_SHEET, EXPLICATION_SHEET,
                   '## Catalog of referenceable concepts\n\n' + catalog, CONTRACT])

hashes = {}
for name, txt in (('A', sys_A), ('B', sys_B), ('C', sys_C), ('D', sys_D), ('F', sys_F)):
    p = os.path.join(OUT, f'system-{name}.txt')
    open(p, 'w').write(txt)
    hashes[name] = hashlib.sha256(txt.encode()).hexdigest()

# --- per-concept user prompts --------------------------------------------------
concepts = json.load(open(os.path.join(HERE, 'concepts.json')))
def def_text(lemma):
    parts = []
    wt = os.path.join(DEFS, 'wiktionary', lemma + '.json')
    if os.path.exists(wt):
        w = json.load(open(wt))
        if w.get('ok'):
            by_pos = {}
            for s in w['senses']:
                by_pos.setdefault(s['pos'], []).append(s['definition'])
            for pos, ds in list(by_pos.items())[:4]:
                for d in ds[:4]:
                    parts.append(f'({pos.lower()}) {d[:220]}')
            parts = parts[:8]
            parts.insert(0, f'Wiktionary (rev {w.get("revision","?")}):')
    wp = os.path.join(DEFS, 'wikipedia', lemma + '.json')
    if os.path.exists(wp):
        p = json.load(open(wp))
        if p.get('ok'):
            parts.append(f'Wikipedia (rev {p.get("revision","?")}): {p["extract"][:600]}')
    return '\n'.join(parts) if parts else '(no definitional text available)'

for c in concepts:
    lemma = c['lemma']
    user = (f'CONCEPT: {lemma}\n\nDefinitional text:\n{def_text(lemma)}\n\n'
            f'Produce the JSON record for the dominant everyday sense of "{lemma}".')
    open(os.path.join(OUT, 'user', lemma + '.txt'), 'w').write(user)

meta = {'promptVersionHash': {k: 'sha256:' + v for k, v in hashes.items()},
        'systemPromptBytes': {k: len(t.encode()) for k, t in
                              (('A', sys_A), ('B', sys_B), ('C', sys_C), ('D', sys_D), ('F', sys_F))},
        'conceptCount': len(concepts)}
json.dump(meta, open(os.path.join(OUT, 'prompt-meta.json'), 'w'), indent=1)
print(json.dumps(meta, indent=1))
