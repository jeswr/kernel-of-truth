#!/usr/bin/env python3
"""M0b step 2 — classify the top-500 content lemmas (results/m0b-vocab.json)
and emit the frequency-weighted kernel-expressibility estimate
(results/m0b-report.json). poc-design.md M0b: "this number bounds every
benefit claim and goes in the prospectus unvarnished."

Classifier: agent (Claude Fable 5), 2026-07-07. Judgment-based per the
pre-registration ("your judgment, criteria stated"); a human pass can reuse
this file by editing the tables.

CLASSES and criteria:

- kernel      — the lemma's DOMINANT TinyStories sense is a kernel-v0 concept
                or one of the 65 primes. Split into:
                  kernel-lexicon: surface form is in the mapper lexicon;
                  kernel-synonym: sense covered, surface NOT in the lexicon
                  (e.g. start->begin, glad->happy, fix->repair) — a mapper
                  LEXICON gap, not a kernel gap.
                Surface-in-lexicon lemmas whose dominant sense is NOT the
                kernel target's sense (like=enjoy, way=route, kind=nice,
                right=correct) are NOT counted kernel ("false friends";
                listed in the report).
- explicable  — plausibly profile-1-explicable with the 65 primes + existing
                kernel-v0 concepts in a few clauses: mental/emotional/social/
                speech-act/evaluative/abstract-relational/temporal-order
                vocabulary; politeness+greeting formulae; numerals beyond TWO
                (via ONE/TWO/MORE); no perceptual, taxonomic, artifact or
                body-part molecule required.
- molecule    — needs semantic molecules first (NSM's own position for these
                domains): concrete/taxonomic nouns (animals, plants, food,
                artifacts, places, nature, weather), body parts, bodily
                actions/postures/states (eat, sleep, run, laugh, hug),
                percepts (color, taste, temperature, texture, light, smell),
                kinship (classed molecule even though maternal terms are
                arguably explicable via kernel birth — conservative choice),
                day/night-cycle time words, social institutions (school,
                doctor, money, princess).
- oos         — out-of-scope: proper names (incl. titles), interjections/
                expressives, onomatopoeia, corpus artifacts. Numbers would be
                oos, but one/two are primes and 'three' is explicable.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
vocab = json.load(open(os.path.join(HERE, 'results', 'm0b-vocab.json')))

# kernel, surface in mapper lexicon, dominant sense matches target
KERNEL_LEXICON = {
    'say', 'see', 'one', 'want', 'time', 'little', 'happy', 'big', 'make',
    'friend', 'feel', 'find', 'good', 'take', 'help', 'know', 'thing', 'sad',
    'give', 'think', 'hear', 'learn', 'live', 'small', 'end', 'people',
    'two', 'break', 'bad', 'angry', 'place', 'happen', 'move', 'remember',
    'touch', 'forget', 'begin', 'lose', 'promise', 'wrong', 'moment', 'far',
    'word', 'believe', 'side', 'gift',
}
# kernel sense covered, surface NOT in mapper lexicon (lexicon gap)
KERNEL_SYNONYM = {
    'start': 'urn:kernel-v0:begin', 'scare': 'urn:kernel-v0:afraid',
    'stop': 'urn:kernel-v0:end', 'become': 'urn:kernel-v0:change',
    'finish': 'urn:kernel-v0:end', 'glad': 'urn:kernel-v0:happy',
    'piece': 'prime:PART', 'fix': 'urn:kernel-v0:repair',
    'happily': 'urn:kernel-v0:happy', 'able': 'prime:CAN',
    'build': 'urn:kernel-v0:make', 'later': 'prime:AFTER',
    'scary': 'urn:kernel-v0:afraid', 'party': 'urn:kernel-v0:celebration',
    'tiny': 'prime:SMALL', 'nearby': 'prime:NEAR',
    'long': 'prime:A-LONG-TIME',
}
# surface IS in mapper lexicon but dominant corpus sense is NOT the target
FALSE_FRIENDS = {
    'like': 'enjoy (kernel target: similarity prime)',
    'way': 'route (kernel target: manner allolex of LIKE~AS~WAY)',
    'kind': 'nice-to-people (kernel target: sortal kind)',
    'right': 'correct/suitable senses dominate (kernel target: right-of-a-doable-something)',
}

EXPLICABLE = {
    'go', 'play', 'look', 'love', 'get', 'name', 'come', 'ask', 'fun',
    'try', 'put', 'home', 'new', 'thank', 'excited', 'decide', 'tell',
    'old', 'keep', 'special', 'suddenly', 'show', 'sorry', 'yes', 'proud',
    'share', 'watch', 'need', 'nice', 'work', 'explore', 'call',
    'beautiful', 'wait', 'fast', 'safe', 'careful', 'stay', 'listen',
    'noise', 'loud', 'hurt', 'hard', 'brave', 'surprise', 'high', 'fall',
    'sure', 'pretty', 'idea', 'next', 'reach', 'finally', 'turn', 'worry',
    'leave', 'notice', 'adventure', 'mean', 'great', 'story', 'enjoy',
    'important', 'quickly', 'game', 'please', 'replied', 'wish', 'strong',
    'goodbye', 'sound', 'shout', 'voice', 'follow', 'different', 'talk',
    'first', 'hello', 'bring', 'three', 'tire', 'bright', 'curious',
    'realize', 'ready', 'use', 'favorite', 'understand', 'hide', 'world',
    'teach', 'fill', 'hole', 'top', 'sometimes', 'full', 'carefully',
    'dark', 'care', 'grow', 'pretend', 'meet', 'tall', 'lesson', 'arrive',
    'rest', 'friendly', 'fight', 'continued', 'wonderful', 'strange',
    'enough', 'agreed', 'race', 'join', 'deep', 'joy', 'miss', 'visit',
    'search', 'mess', 'well', 'perfect', 'amazed', 'amazing', 'moral',
    'chase', 'wonder', 'cheer', 'count', 'silly', 'alone', 'slowly',
    'magical', 'welcome', 'grateful', 'job', 'seem', 'explain', 'scream',
    'answer', 'hi', 'dangerous', 'spend', 'plan', 'save', 'young',
    'eventually', 'quiet', 'gentle', 'smart', 'upset',
    'like', 'way', 'kind', 'right',  # false friends: dominant sense explicable
}

MOLECULE = {
    'day', 'mom', 'girl', 'smile', 'run', 'toy', 'boy', 'mommy', 'bird',
    'park', 'walk', 'tree', 'hug', 'dad', 'man', 'dog', 'eat', 'car',
    'fly', 'house', 'ball', 'hand', 'pick', 'water', 'room', 'bear',
    'open', 'box', 'cry', 'close', 'animal', 'jump', 'cat', 'flower',
    'sky', 'garden', 'family', 'sun', 'red', 'clean', 'sit', 'ground',
    'hold', 'shiny', 'eye', 'doll', 'door', 'face', 'rock', 'grab',
    'wave', 'climb', 'book', 'food', 'bite', 'stick', 'slide', 'forest',
    'fish', 'picture', 'rabbit', 'catch', 'year', 'mum', 'truck', 'blue',
    'daddy', 'swing', 'bed', 'head', 'child', 'swim', 'dress', 'store',
    'boat', 'buy', 'cake', 'bunny', 'night', 'grandma', 'wear', 'dance',
    'pull', 'warm', 'block', 'kid', 'yummy', 'brother', 'kitchen',
    'grass', 'draw', 'teddy', 'cold', 'ride', 'farm', 'yellow', 'green',
    'bag', 'floor', 'wind', 'window', 'paint', 'hill', 'step', 'cream',
    'wood', 'lion', 'wet', 'mama', 'sweet', 'apple', 'cookies', 'shake',
    'clap', 'train', 'dinner', 'dream', 'pink', 'drive', 'puppy',
    'squirrel', 'table', 'sleep', 'morning', 'pet', 'stand', 'castle',
    'mother', 'hot', 'bug', 'beach', 'wall', 'hair', 'taste', 'drop',
    'drink', 'hungry', 'song', 'smell', 'write', 'arm', 'air', 'shine',
    'treat', 'today', 'balloon', 'clothes', 'white', 'point', 'carry',
    'fluffy', 'cut', 'blow', 'colorful', 'bike', 'wake', 'mouse', 'hat',
    'cool', 'pond', 'star', 'duck', 'leaf', 'soft', 'frog', 'throw',
    'ice', 'paper', 'lady', 'baby', 'push', 'read', 'delicious', 'light',
    'parent', 'butterfly', 'rain', 'color', 'set', 'sing', 'laugh',
    'tail', 'treasure', 'monster', 'river', 'fox', 'candy', 'shape',
    'roll', 'fire', 'snack', 'sister', 'music', 'field', 'princess',
    'branch', 'money', 'tight', 'heavy', 'sand', 'bush', 'wing', 'sign',
    'splash', 'carrot', 'bee', 'land', 'bark', 'lake', 'plant', 'brown',
    'cloud', 'town', 'mark', 'shoe', 'blanket', 'nap', 'mouth', 'chair',
    'tower', 'soup', 'fruit', 'dragon', 'sail', 'elephant', 'monkey',
    'dirty', 'dry', 'kiss', 'hit', 'bubble', 'mitten', 'bowl', 'doctor',
    'bucket', 'button', 'juice', 'wash', 'yard', 'school', 'street',
    'sea', 'fairy', 'nod', 'hop',
}

OOS = {
    'lily', 'tom', 'timmy', 'ben', 'tim', 'max', 'sam', 'anna', 'jack',
    'mia', 'sara', 'spot', 'lucy', 'john', 'bob', 'sue', 'sarah', 'jane',
    'benny', 'joe', 'tommy', 'billy', 'sally', 'molly', 'amy', 'lila',
    'daisy', 'emma', 'mary', 'jimmy', 'jill', 'sammy', 'mr', 'wow', 'oh',
}

NOTES = {
    'play': 'child-play; Wierzbicka-style explication long but prime-only — borderline vs molecule',
    'mom': "kinship classed molecule; maternal terms arguably explicable via kernel 'birth' (conservative choice)",
    'long': "dominant collocation 'a long time' -> A-LONG-TIME; spatial sense would be molecule",
    'set': 'highly polysemous light verb; phrasal uses dominate — weakest explicable call',
    'spot': "character name Spot dominates; common-noun 'spot'=place would be explicable",
    'teddy': "mostly 'teddy bear' (toy) -> molecule despite name-like look",
    'daisy': 'character name dominates; flower sense would be molecule',
    'hole': 'spatial configuration via INSIDE/PLACE — borderline vs molecule',
    'funny': 'tied to laughing (bodily molecule)',
    'hungry': 'wanting to eat -> food/eating molecules',
    'cool': "temperature + slang 'cool!'; classed by temperature sense",
    'three': 'TWO and ONE more — numerals explicable per NSM',
    'tire': 'FEEL/BODY/CAN primes plausibly suffice — borderline vs molecule',
}
MOLECULE.add('funny')

CLS = {}
for w in KERNEL_LEXICON:
    CLS[w] = 'kernel-lexicon'
for w in KERNEL_SYNONYM:
    CLS[w] = 'kernel-synonym'
for w in EXPLICABLE:
    if w not in CLS:
        CLS[w] = 'explicable'
for w in MOLECULE:
    if w not in CLS:
        CLS[w] = 'molecule'
for w in OOS:
    if w not in CLS:
        CLS[w] = 'oos'

rows = vocab['rows']
missing = [r['lemma'] for r in rows if r['lemma'] not in CLS]
assert not missing, f'unclassified lemmas: {missing}'

mass = {c: 0 for c in ('kernel-lexicon', 'kernel-synonym', 'explicable', 'molecule', 'oos')}
out_rows = []
top_mass = 0
for r in rows:
    c = CLS[r['lemma']]
    mass[c] += r['count']
    top_mass += r['count']
    row = {'lemma': r['lemma'], 'count': r['count'], 'class': c}
    if r['lemma'] in NOTES:
        row['note'] = NOTES[r['lemma']]
    if r['lemma'] in KERNEL_SYNONYM:
        row['kernelTarget'] = KERNEL_SYNONYM[r['lemma']]
    out_rows.append(row)

pct = {c: round(100 * m / top_mass, 2) for c, m in mass.items()}
content_mass = vocab['contentMass']

report = {
    'experiment': 'M0b',
    'date': '2026-07-07',
    'caveat': 'AGENT-JUDGED single-annotator classification (Claude Fable 5); criteria in classify-m0b.py; pre-registration allows judgment-based estimate with criteria stated; no inter-annotator agreement measured',
    'basis': {
        'corpus': vocab.get('experiment'),
        'contentMassTokens': content_mass,
        'pctContentOfAllWords': vocab['pctContentOfAllWords'],
        'topN': vocab['topN'],
        'topNMassPctOfContent': vocab['topNMassPctOfContent'],
    },
    'headlinePctOfTop500Mass': pct,
    'headline': {
        'kernelTotal': round(pct['kernel-lexicon'] + pct['kernel-synonym'], 2),
        'explicable': pct['explicable'],
        'molecule': pct['molecule'],
        'outOfScope': pct['oos'],
        'coverageCeilingNote': (
            'kernel+explicable is the profile-1 coverage ceiling over top-500 '
            'content mass; molecule-needing mass is unreachable without a '
            'molecule tier; scaled to ALL content mass, multiply by '
            f"{vocab['topNMassPctOfContent']}% top-500 share (long tail unclassified)"
        ),
    },
    'falseFriends': FALSE_FRIENDS,
    'classMassTokens': mass,
    'rows': out_rows,
}
with open(os.path.join(HERE, 'results', 'm0b-report.json'), 'w') as f:
    json.dump(report, f, indent=2)
    f.write('\n')
print(json.dumps({'pctOfTop500ContentMass': pct,
                  'kernelTotal': report['headline']['kernelTotal']}, indent=2))
