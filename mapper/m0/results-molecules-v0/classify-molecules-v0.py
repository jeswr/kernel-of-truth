#!/usr/bin/env python3
"""Molecule-tier coverage delta — re-run of the M0b classification with
data/molecules-v0 counted as covered. Reads the COMMITTED m0b report
(../results/m0b-report.json — never modified) and reclassifies only the
rows m0b classed `molecule`; all other classes are carried over unchanged.

Classifier: agent (Claude Fable 5), 2026-07-07, single-annotator, criteria
stated below — the same caveat as m0b itself (judgment-based estimate,
class boundaries ±few points).

NEW CLASSES over the m0b `molecule` rows:

- molecule-v0-label     — the lemma IS a molecules-v0 label; the mapper
                          would cover it by adding the label to its lexicon.
- molecule-v0-synonym   — dominant sense is a minted molecule, surface
                          differs (mom->mother, bunny->rabbit, hop->jump,
                          kid->child, lady->woman) — a mapper LEXICON gap,
                          exactly parallel to m0b's kernel-synonym class.
- explicable-with-molecules (CLEAR) — plausibly profile-1-explicable in a
                          few clauses GIVEN molecules-v0 + kernel-v0 +
                          primes, with closure over other lemmas in this
                          class (the same closure m0b's `explicable` class
                          already used, e.g. adventure over other
                          explicables). This is the TRANSITIVE expressibility
                          the molecule tier buys: molecules become referable
                          building blocks for future explications.
- explicable-with-molecules (BORDERLINE) — an explication sketch exists but
                          leans on an unminted molecule (teeth, legs, sand,
                          air, sharp...) or an under-determined artifact/
                          story/percept kind. Counted separately and
                          reported as a sensitivity band, never silently
                          merged into the clear class.
- still-molecule-gated  — needs molecules not in v0 (animal kinds, food
                          kinds, remaining colors, calendar units, royalty,
                          sensory kinds, highly polysemous light verbs).

Refs notation: m:<slug> = molecules-v0, k:<slug> = kernel-v0, p:<PRIME>,
ew:<lemma> = closure over another explicable-with lemma. All refs are
validated against the molecules-v0 manifest / kernel-v0 manifest / the
tables themselves — a typo fails the run.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))

m0b = json.load(open(os.path.join(HERE, '..', 'results', 'm0b-report.json')))
mol_manifest = json.load(open(os.path.join(REPO, 'data', 'molecules-v0', 'manifest.json')))
kernel_manifest = json.load(open(os.path.join(REPO, 'data', 'kernel-v0', 'manifest.json')))

MOL_LABELS = {m['label']: m['id'] for m in mol_manifest['molecules']}
KERNEL_SLUGS = {c['id'].split(':')[-1] for c in kernel_manifest['concepts']}

# lemma -> molecule id, derived from the manifest's own corpusLemmas claims.
DIRECT = {}
for mrec in mol_manifest['molecules']:
    for lemma in mrec['corpusLemmas']:
        assert lemma not in DIRECT, f'lemma {lemma} claimed by two molecules'
        DIRECT[lemma] = mrec['id']

SYNONYM_NOTES = {
    'hop': "counted as jump-synonym: dominant TinyStories use is rabbit/child hopping (small jumps); weakest synonym call",
    'lady': "polite/adult-register surface of woman",
    'bunny': "child-register surface of rabbit",
}

# --- explicable-with-molecules, CLEAR ---------------------------------------
EW_CLEAR = {
    'girl': ['m:child', 'm:woman'], 'boy': ['m:child', 'm:man'],
    'toy': ['m:child', 'k:make'], 'doll': ['m:child', 'k:make'],
    'teddy': ['m:child', 'k:make', 'm:bear'],
    'block': ['m:child', 'k:make'],
    'park': ['m:tree', 'm:grass', 'm:child'],
    'garden': ['m:house', 'm:flower', 'm:grass'],
    'fly': ['m:bird', 'm:sky', 'm:ground'],
    'swim': ['m:water'], 'splash': ['m:water'],
    'pick': ['m:hand', 'k:take'], 'hold': ['m:hand'], 'grab': ['m:hand', 'k:take'],
    'wave': ['m:hand'], 'clap': ['m:hand'], 'point': ['m:hand'],
    'throw': ['m:hand'], 'catch': ['m:hand'], 'pull': ['m:hand'],
    'push': ['m:hand'], 'shake': ['m:hand'], 'hit': ['m:hand'],
    'drop': ['m:hand', 'm:ground'], 'carry': ['m:hand', 'm:walk'],
    'climb': ['m:hand', 'm:tree'],
    'arm': ['m:hand'],
    'room': ['m:house'], 'door': ['m:house', 'm:open', 'm:close'],
    'window': ['m:house'], 'wall': ['m:house'], 'floor': ['m:house', 'm:ground'],
    'kitchen': ['m:house', 'm:food', 'm:eat'], 'yard': ['m:house'],
    'town': ['m:house'], 'street': ['ew:town', 'm:car', 'm:walk'],
    'tower': ['m:house', 'k:make', 'm:ground'],
    'family': ['m:mother', 'm:father', 'm:child'],
    'parent': ['m:mother', 'm:father'], 'grandma': ['m:mother', 'm:father'],
    'brother': ['m:mother', 'm:father', 'ew:boy'],
    'sister': ['m:mother', 'm:father', 'ew:girl'],
    'baby': ['m:child', 'k:birth'],
    'nod': ['m:head'], 'face': ['m:head', 'm:eye', 'm:mouth'],
    'kiss': ['m:mouth'],
    'clean': ['m:water'], 'dirty': ['ew:clean'],
    'shiny': ['m:light'], 'shine': ['m:light'],
    'star': ['m:sky', 'm:night', 'm:light'],
    'funny': ['m:laugh'],
    'stick': ['m:tree'], 'forest': ['m:tree'], 'leaf': ['m:tree'],
    'branch': ['m:tree'], 'bush': ['m:tree'],
    'wood': ['m:tree', 'm:fire', 'k:make'],
    'plant': ['m:tree', 'm:grass', 'm:flower'],
    'slide': ['m:child', 'k:make'], 'swing': ['m:child', 'm:sit', 'k:make'],
    'truck': ['m:car'], 'train': ['m:car'], 'drive': ['m:car'],
    'ride': ['m:car', 'm:animal'],
    'dress': ['m:clothes', 'm:woman'], 'wear': ['m:clothes'],
    'hat': ['m:clothes', 'm:head'], 'shoe': ['m:clothes', 'm:walk', 'm:ground'],
    'mitten': ['m:clothes', 'm:hand', 'm:cold'],
    'store': ['m:money', 'm:house'], 'buy': ['m:money', 'k:give', 'k:take'],
    'boat': ['m:water', 'k:make'],
    'warm': ['m:fire', 'm:cold'], 'hot': ['m:fire'], 'cool': ['m:cold'],
    'ice': ['m:water', 'm:cold'], 'wet': ['m:water'], 'dry': ['m:water'],
    'rain': ['m:water', 'm:sky'], 'cloud': ['m:sky'],
    'pond': ['m:water'], 'lake': ['m:water'], 'river': ['m:water'],
    'sea': ['m:water'],
    'hill': ['m:ground'], 'land': ['m:ground'],
    'field': ['m:grass'],
    'yummy': ['m:eat', 'm:food'], 'delicious': ['m:eat', 'm:food'],
    'hungry': ['m:eat'], 'snack': ['m:food', 'm:eat'],
    'dinner': ['m:eat', 'm:food', 'm:day', 'm:night'],
    'treat': ['m:food', 'k:give', 'm:child'],
    'drink': ['m:water', 'm:mouth'],
    'read': ['m:book'], 'write': ['m:hand', 'p:WORDS'],
    'draw': ['m:picture', 'm:hand'],
    'paint': ['m:picture', 'm:color', 'm:hand'],
    'sign': ['k:make', 'p:WORDS'],
    'colorful': ['m:color'],
    'sing': ['m:music', 'm:mouth'], 'song': ['m:music', 'ew:sing'],
    'dance': ['m:music'],
    'sleep-derived-wake': [],  # placeholder removed below
    'wake': ['m:sleep'], 'dream': ['m:sleep'], 'nap': ['m:sleep', 'm:day'],
    'bed': ['m:sleep', 'm:house', 'k:make'],
    'blanket': ['m:sleep', 'm:cold', 'k:make'],
    'chair': ['m:sit', 'k:make'],
    'morning': ['m:day', 'm:night', 'm:sleep'], 'today': ['m:day'],
    'pet': ['m:animal', 'm:house'], 'puppy': ['m:dog', 'k:birth'],
    'tail': ['m:animal'], 'wing': ['m:bird'], 'bug': ['m:animal'],
    'bark': ['m:dog'],
    'farm': ['m:animal', 'm:food', 'm:house'],
    'school': ['m:child', 'k:teacher', 'k:learn'],
    'bag': ['k:make', 'm:hand'], 'bucket': ['m:water', 'm:hand', 'k:make'],
    'bowl': ['m:food', 'm:eat', 'k:make'],
    'roll': ['m:ball', 'm:ground'],
    'step': ['m:walk', 'm:ground'],
    'wash': ['m:water', 'm:hand'],
}
del EW_CLEAR['sleep-derived-wake']

EW_CLEAR_NOTES = {
    'girl': "a child that can be a woman after a long time — NSM's own derivation over the child/woman molecules",
    'boy': "mirror of girl over child/man",
    'toy': "functional kind: a thing people make for children to do things with for pleasure; function IS the identity, so explication (not minting) is the honest tier",
    'park': "functional-relational place kind over tree/grass/child",
    'fly': "move far above the ground, in the sky, like a bird moves",
    'school': "place where children are so that someone (kernel teacher) can teach them — kernel-v0 already carries teacher/learn",
    'hop': "see synonym table",
    'carry': "hold in the hands while moving",
    'morning': "the part of the day a short time after night ends",
    'sing': "make music with the mouth/say words like music — NSM might well molecule this; kept clear because the differentia is fully functional",
    'swing': "playground artifact: a thing children sit on that moves one way then the other; motion verb sense explicable with MOVE",
    'slide': "playground artifact + motion-on-surface verb sense",
    'clean': "arguably never needed a molecule ('nothing bad on it'); m0b classed it molecule via the scrubbing-activity sense",
    'bed': "same functional-artifact logic as chair-via-sit; consistency with chair/table calls",
    'land': "verb sense dominates in TinyStories (landed on the ground) — end-of-flight schema",
    'bark': "dog-sound sense dominates in TinyStories; tree-bark minority sense would be still-gated",
}

# --- explicable-with-molecules, BORDERLINE ----------------------------------
EW_BORDERLINE = {
    'bite': (['m:mouth', 'm:eat'], "teeth [m] unminted; NSM bites with teeth"),
    'stand': (['m:sit', 'm:ground'], "posture differentia from sit is coarse without legs [m]"),
    'table': (['k:make', 'm:eat', 'm:food'], "under-determined artifact kind (flat-top essence needs shape molecules)"),
    'castle': (['m:house', 'k:make'], "very big old house of rock — rock ref fine but royalty/fortification content lost"),
    'beach': (['m:water', 'm:ground'], "sand [m] unminted"),
    'hair': (['m:head'], "body-covering kind; 'very many small long things on the head' strains the lexicon"),
    'air': ([], "invisible material kind; prime-only sketch exists ('something in all places, people cannot see it') but NSM molecules it"),
    'wind': ([], "prime-only sketch ('it moves, people feel it on the body, small things move because of it'); m0b classed it weather-molecule"),
    'blow': (['m:mouth'], "needs air/wind"),
    'monster': (['m:animal', 'k:afraid'], "story-kind; 'big bad animal-like thing in stories' is a stretch of KIND"),
    'dragon': (['m:animal', 'm:fire'], "story-kind, same caveat as monster"),
    'treasure': (['m:money'], "value-kind; hidden-precious content under-determined"),
    'cut': (['m:hand'], "instrument (sharp [m]) unminted; 'after this it is two things' captures result only"),
    'bike': (['k:make', 'm:ground'], "mechanism (wheels, pedalling) unminted; functional sketch only"),
    'balloon': (['m:child', 'k:make', 'm:sky'], "needs air [m]"),
    'soft': ([], "touch-percept quality; prime-only sketch ('parts of it move when the body touches it')"),
    'heavy': ([], "effort-based prime-only sketch; NSM treats weight words as molecule-backed"),
    'paper': (['m:book', 'k:make'], "material kind; NSM molecules materials"),
    'sand': (['m:ground', 'm:water', 'm:rock'], "granular material kind"),
    'taste': (['m:mouth', 'm:food', 'm:eat'], "percept kind; the quality space (sweet/sour) stays gated"),
    'doctor': (['k:help'], "institution; sick [m] unminted"),
    'sail': (['ew:boat', 'k:make'], "wind [m] unminted"),
    'mark': (['k:make'], "highly schematic; visible-trace reading only"),
    'bubble': (['m:water'], "needs air [m]; round-shape content lost"),
    'button': (['m:clothes'], "small artifact kind; fastening mechanism under-determined"),
}

# --- still molecule-gated -----------------------------------------------------
GATED = {
    'year': "calendar unit; 'very many days' would be dishonest",
    'cake': "food kind", 'cookies': "food kind", 'candy': "food kind",
    'apple': "food kind", 'carrot': "food kind", 'soup': "food kind",
    'juice': "food kind", 'fruit': "food kind", 'cream': "ice-cream sense dominates; food kind",
    'sweet': "taste quality; needs sugar/honey-style prototype molecule",
    'butterfly': "animal kind", 'mouse': "animal kind", 'duck': "animal kind",
    'frog': "animal kind", 'lion': "animal kind", 'elephant': "animal kind",
    'monkey': "animal kind", 'squirrel': "animal kind", 'bee': "animal kind",
    'fox': "animal kind",
    'yellow': "color kind (sun prototype available but unminted in v0 — next-100 candidate)",
    'green': "color kind (grass/tree prototype available but unminted in v0 — next-100 candidate)",
    'white': "color kind", 'pink': "color kind", 'brown': "color kind",
    'smell': "sensory kind; nose [m] unminted",
    'fluffy': "texture kind; fur/hair [m] unminted",
    'shape': "percept determinable; determinates (round, flat) all unminted",
    'set': "highly polysemous light verb; phrasal uses dominate (m0b's own note)",
    'princess': "royalty institution", 'fairy': "story-kind institution",
    'tight': "force/fit percept",
}

rows = m0b['rows']
mol_rows = [r for r in rows if r['class'] == 'molecule']
mol_lemmas = {r['lemma'] for r in mol_rows}

# ---- table hygiene: full cover, no overlap, refs resolve --------------------
for lemma in DIRECT:
    assert lemma in mol_lemmas, f'direct lemma {lemma} not in m0b molecule class'
buckets = [set(DIRECT), set(EW_CLEAR), set(EW_BORDERLINE), set(GATED)]
for i, a in enumerate(buckets):
    for b in buckets[i + 1:]:
        assert not (a & b), f'overlap: {a & b}'
covered = set().union(*buckets)
missing = mol_lemmas - covered
extra = covered - mol_lemmas
assert not missing, f'unclassified molecule lemmas: {sorted(missing)}'
assert not extra, f'classified but not molecule-class: {sorted(extra)}'

def check_refs(refs, owner):
    for ref in refs:
        ns, _, slug = ref.partition(':')
        if ns == 'm':
            assert slug in MOL_LABELS, f'{owner}: unknown molecule ref {ref}'
        elif ns == 'k':
            assert slug in KERNEL_SLUGS, f'{owner}: unknown kernel ref {ref}'
        elif ns == 'ew':
            assert slug.split('-')[0] in EW_CLEAR or slug in EW_CLEAR, \
                f'{owner}: unknown closure ref {ref}'
        elif ns == 'p':
            pass  # prime name; encoder lexicon is source of truth
        else:
            raise AssertionError(f'{owner}: bad ref namespace {ref}')

for lemma, refs in EW_CLEAR.items():
    check_refs(refs, lemma)
for lemma, (refs, _) in EW_BORDERLINE.items():
    check_refs(refs, lemma)

# ---- mass accounting ---------------------------------------------------------
top_mass = sum(r['count'] for r in rows)
mass = {
    'kernel-lexicon': 0, 'kernel-synonym': 0, 'explicable': 0, 'oos': 0,
    'molecule-v0-label': 0, 'molecule-v0-synonym': 0,
    'explicable-with-molecules-clear': 0,
    'explicable-with-molecules-borderline': 0,
    'still-molecule-gated': 0,
}
out_rows = []
for r in rows:
    lemma, count, cls = r['lemma'], r['count'], r['class']
    row = {'lemma': lemma, 'count': count}
    if cls != 'molecule':
        row['class'] = cls
    elif lemma in DIRECT:
        mol_id = DIRECT[lemma]
        label = mol_id.split(':')[-1]
        row['class'] = 'molecule-v0-label' if lemma == label else 'molecule-v0-synonym'
        row['moleculeTarget'] = mol_id
        if lemma in SYNONYM_NOTES:
            row['note'] = SYNONYM_NOTES[lemma]
    elif lemma in EW_CLEAR:
        row['class'] = 'explicable-with-molecules-clear'
        row['refs'] = EW_CLEAR[lemma]
        if lemma in EW_CLEAR_NOTES:
            row['note'] = EW_CLEAR_NOTES[lemma]
    elif lemma in EW_BORDERLINE:
        refs, note = EW_BORDERLINE[lemma]
        row['class'] = 'explicable-with-molecules-borderline'
        row['refs'] = refs
        row['note'] = note
    else:
        row['class'] = 'still-molecule-gated'
        row['note'] = GATED[lemma]
    mass[row['class']] += count
    out_rows.append(row)

pct = {c: round(100 * v / top_mass, 2) for c, v in mass.items()}
content_share = m0b['basis']['pctContentOfAllWords'] / 100.0

old_ceiling = m0b['headline']['kernelTotal'] + m0b['headline']['explicable']
direct = pct['molecule-v0-label'] + pct['molecule-v0-synonym']
clear = pct['explicable-with-molecules-clear']
borderline = pct['explicable-with-molecules-borderline']
ceil_direct = old_ceiling + direct
ceil_clear = ceil_direct + clear
ceil_border = ceil_clear + borderline

mol_total_pct = m0b['headlinePctOfTop500Mass']['molecule']  # 33.0

def all_tok(x):
    return round(x * content_share, 1)

report = {
    'experiment': 'M0b-molecules-v0 (coverage delta)',
    'date': '2026-07-07',
    'caveat': ('AGENT-JUDGED single-annotator reclassification of the m0b '
               'molecule class (Claude Fable 5); criteria in this file; same '
               'epistemic status as m0b itself (±few points). Committed m0b '
               'results untouched; only class=molecule rows reclassified.'),
    'inputs': {
        'm0bReport': 'mapper/m0/results/m0b-report.json',
        'molecules': 'data/molecules-v0/manifest.json (54 molecules, all pass validate.mjs)',
    },
    'basis': m0b['basis'],
    'headlinePctOfTop500Mass': pct,
    'moleculeMassSplit': {
        'moleculeClassTotalPct': mol_total_pct,
        'directPct': round(direct, 2),
        'transitiveClearPct': round(clear, 2),
        'transitiveBorderlinePct': round(borderline, 2),
        'stillGatedPct': pct['still-molecule-gated'],
        'shareOfMoleculeMassUnlocked': {
            'directOnly': round(100 * direct / mol_total_pct, 1),
            'plusClear': round(100 * (direct + clear) / mol_total_pct, 1),
            'plusBorderline': round(100 * (direct + clear + borderline) / mol_total_pct, 1),
        },
    },
    'ceilings': {
        'convention': ('content-mass ceilings are % of top-500 content mass '
                       '(80.35% of content mass classified; long tail skews '
                       'concrete/named => generous, same as m0b); all-token '
                       'ceilings apply the 45.55% content share, same '
                       'convention as the m0b ~26% number'),
        'old': {'contentPct': round(old_ceiling, 1), 'allTokenPct': all_tok(old_ceiling)},
        'newDirectOnly': {'contentPct': round(ceil_direct, 1), 'allTokenPct': all_tok(ceil_direct)},
        'newPlusTransitiveClear': {'contentPct': round(ceil_clear, 1), 'allTokenPct': all_tok(ceil_clear)},
        'newPlusBorderline': {'contentPct': round(ceil_border, 1), 'allTokenPct': all_tok(ceil_border)},
    },
    'classMassTokens': mass,
    'rows': out_rows,
}
with open(os.path.join(HERE, 'm0b-molecules-report.json'), 'w') as f:
    json.dump(report, f, indent=2)
    f.write('\n')
print(json.dumps({k: v for k, v in report.items() if k in ('headlinePctOfTop500Mass', 'moleculeMassSplit', 'ceilings')}, indent=2))
