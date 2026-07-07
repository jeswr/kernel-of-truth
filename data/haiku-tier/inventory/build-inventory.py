#!/usr/bin/env python3
"""haiku-tier stage 0 — prioritised concept inventory builder.

Merges three pinned sources into a ranked, deduped, filtered inventory of
concept candidates for the modelAuthored (claude-haiku) tier:

  band A — M0b measured gaps: top-500 TinyStories content lemmas classified
           (post-molecules-v0) as still-molecule-gated / explicable /
           explicable-with-molecules-* — the lemmas the coverage measurement
           says the kernel needs next (mapper/m0/results-molecules-v0/).
  band B — Princeton WordNet "core" list (~5k most frequent+salient senses;
           standoff file, pinned by sha256) not already in band A.
  band C — frequency-ranked content lemmas from the pinned OpenSubtitles-2018
           en_50k list (hermitdave/FrequencyWords @ 072bbed) that are WordNet
           lemmas, until the content-lemma pool reaches TOP_N (~10k).

EXCLUSIONS (each recorded with a reason in inventory-excluded.jsonl):
  covered        — kernel-v0 labels/slugs, molecules-v0 slugs+corpusLemmas,
                   M0b kernel-lexicon/kernel-synonym/molecule-v0-* lemmas.
  prime          — the 65-prime exponent/allolex surfaces (ground layer).
  function       — the pinned M0b FUNCTION_STOPLIST (function words are
                   mapper/M0a territory, not concepts).
  entity         — proper-noun/named-entity rule (below).
  sector         — fixed-source-covered: exact single-word label match against
                   physics-v0 (units/quantitykinds/dimensions/constants) or
                   math-v0 labels, OR all noun senses under WordNet 3.1
                   unit_of_measurement (13604927) with no other POS.
                   These are flagged with the target sector, not silently
                   dropped: the sectors own them.
  junk           — <2 chars, non-alphabetic, or an inflected form whose base
                   (per WordNet .exc tables) is itself in the inventory pool.

ENTITY RULE (documented, mechanical; entities are world-layer, not kernel):
  a lemma is an entity iff it has WordNet noun senses, has NO verb/adj/adv
  senses, and EITHER (a) every surface form of it in data.noun is
  capitalised (e.g. London, Bible), OR (b) every one of its noun synsets is
  an instance synset (has an `@i` instance-hypernym pointer).
  Mixed-case lemmas (china/China) are kept: the lowercase sense is a concept.
  Band-A lemmas are exempt (TinyStories mid-sentence-capitalisation screening
  already classified names as oos; remaining band-A items are concepts).

Deterministic: same pinned inputs => same output bytes (sorting is total).
Usage: nice -n 10 python3 build-inventory.py   (from anywhere; paths are repo-relative)
Outputs: inventory.jsonl, inventory-excluded.jsonl, sizing.md, pins.json checked.
"""
import json, os, re, sys, hashlib
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CACHE = os.path.join(HERE, '..', 'cache')
TOP_N = 10000          # band-C content-lemma pool size (directive: top ~10k)
CUT_TARGET = 9000      # where the ~$70 / 8-10k cut nominally lands

# --- pins ------------------------------------------------------------------
PINS = json.load(open(os.path.join(HERE, 'pins.json')))
def check_pin(name):
    p = PINS['sources'][name]
    path = os.path.join(CACHE, p['file'])
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if h != p['sha256']:
        sys.exit(f'ERR_PIN_MISMATCH: {name}: {h} != {p["sha256"]}')
    return path
CORE = check_pin('core-wordnet')
FREQ = check_pin('freq-en50k')
# wn3.1 tarball pinned; extracted dict/ files are derived from it
check_pin('wn31-dict')

# --- pinned FUNCTION_STOPLIST (verbatim copy of mapper/m0/run-m0b-vocab.mjs) —
STOP = set('''the a an this that these those some any no every each all both
either neither such another other others own same few many much more most
several lot lots i me my mine myself you your yours yourself he him his
himself she her hers herself it its itself we us our ours ourselves they
them their theirs themselves who whom whose which what someone somebody
something anything everything nothing anyone anybody everyone everybody
somewhere anywhere everywhere nowhere whoever whatever to of in on at by
with from for as into onto about over under up down out off through between
behind after before during without within along around across upon near
against toward towards past until till above below beside inside outside
underneath among and or but so because if when while than then where why how
whether unless although though be is are am was were been being have has had
having do does did done doing will would can could shall should may might
must cannot let lets not too very quite really just only also again always
never ever soon now here there still even yet almost maybe perhaps together
away back else once twice instead anymore ok okay'''.split())

# --- 65-prime exponent surfaces (encoder/src/lexicon.ts chart names, split on ~ and -) —
PRIMES = set('''i you someone something thing people body kind part this same
other else another one two some all much many little few good bad big small
think know want feel see hear say words true do happen move live die when
time now before after moment where place here above below far near side
inside touch not maybe can because if very more like as way'''.split())

# --- covered by existing corpora --------------------------------------------
def slug(urn): return urn.rsplit(':', 1)[1]
kman = json.load(open(os.path.join(REPO, 'data', 'kernel-v0', 'manifest.json')))
covered = {}
for c in kman['concepts']:
    covered[slug(c['id']).replace('-', ' ')] = 'kernel-v0'
    covered[slug(c['id'])] = 'kernel-v0'
mman = json.load(open(os.path.join(REPO, 'data', 'molecules-v0', 'manifest.json')))
for m in mman['molecules']:
    covered[slug(m['id'])] = 'molecules-v0'
    rec = json.load(open(os.path.join(REPO, 'data', 'molecules-v0', m['file'])))
    for lem in rec.get('corpusLemmas', []):
        covered[lem] = 'molecules-v0'

# --- band A: M0b post-molecules gap classes ---------------------------------
m0b = json.load(open(os.path.join(REPO, 'mapper', 'm0', 'results-molecules-v0',
                                  'm0b-molecules-report.json')))
GAP = {'still-molecule-gated', 'explicable', 'explicable-with-molecules-clear',
       'explicable-with-molecules-borderline'}
COVERED_M0B = {'kernel-lexicon', 'kernel-synonym', 'molecule-v0-label',
               'molecule-v0-synonym'}
bandA = OrderedDict()   # lemma -> row
for row in m0b['rows']:
    lem, cls = row['lemma'], row['class']
    if cls in COVERED_M0B:
        covered.setdefault(lem, f'm0b:{cls}')
    elif cls in GAP:
        bandA[lem] = row

# --- sector labels (physics-v0 + math-v0), single-word exact ----------------
sector_label = {}
pv = os.path.join(REPO, 'data', 'physics-v0')
for sub in ('units', 'quantitykinds', 'dimensions', 'constants'):
    d = os.path.join(pv, sub)
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json'): continue
        lab = json.load(open(os.path.join(d, f)))['label'].lower()
        if re.fullmatch(r'[a-z]+', lab):
            sector_label[lab] = 'physics-v0'
mv = os.path.join(REPO, 'data', 'math-v0', 'concepts')
for f in sorted(os.listdir(mv)):
    if not f.endswith('.json'): continue
    lab = json.load(open(os.path.join(mv, f)))['label'].lower()
    head = lab.split(' (')[0]
    if re.fullmatch(r'[a-z]+', head):
        sector_label[head] = 'math-v0'

# --- WordNet 3.1 structures --------------------------------------------------
DICT = os.path.join(CACHE, 'dict')
wn_pos_lemmas = {}   # pos -> set(lemma)  (index files are lowercase)
for pos, fn in (('n','index.noun'), ('v','index.verb'), ('a','index.adj'), ('r','index.adv')):
    s = set()
    for line in open(os.path.join(DICT, fn), encoding='latin-1'):
        if line.startswith(' '): continue
        s.add(line.split(' ', 1)[0])
    wn_pos_lemmas[pos] = s
wn_all = set().union(*wn_pos_lemmas.values())

noun_index = {}      # lemma -> [synset offsets]
for line in open(os.path.join(DICT, 'index.noun'), encoding='latin-1'):
    if line.startswith(' '): continue
    parts = line.split()
    lemma, p_cnt = parts[0], int(parts[3])
    noun_index[lemma] = parts[4 + p_cnt + 2:]

# data.noun scan: per-synset instance flag + case-preserving surface forms,
# + hypernym edges for the unit_of_measurement subtree
instance_syn = set(); surf = {}; hyper = {}
for line in open(os.path.join(DICT, 'data.noun'), encoding='latin-1'):
    if line.startswith(' '): continue
    off = line[:8]
    body = line.split('| ')[0].split()
    w_cnt = int(body[3], 16)
    words = [body[4 + 2*k] for k in range(w_cnt)]
    i = 4 + 2*w_cnt
    p_cnt = int(body[i]); i += 1
    ups = []
    for _ in range(p_cnt):
        sym, tgt, pos_, _st = body[i], body[i+1], body[i+2], body[i+3]; i += 4
        if sym == '@i': instance_syn.add(off)
        if sym in ('@', '@i') and pos_ == 'n': ups.append(tgt)
    hyper[off] = ups
    for w in words:
        w0 = w.split('(')[0]           # strip adj markers (noun file: none, safe)
        surf.setdefault(w0.lower(), set()).add(w0)

# unit_of_measurement subtree (descendants), WN3.1 offset 13604927
UNIT_OFF = '13604927'
children = {}
for off, ups in hyper.items():
    for u in ups: children.setdefault(u, []).append(off)
unit_desc = set(); stack = [UNIT_OFF]
while stack:
    o = stack.pop()
    for c in children.get(o, []):
        if c not in unit_desc:
            unit_desc.add(c); stack.append(c)

def is_entity(lemma):
    """Documented entity rule — see module docstring."""
    if lemma not in wn_pos_lemmas['n']: return False
    if any(lemma in wn_pos_lemmas[p] for p in ('v', 'a', 'r')): return False
    forms = surf.get(lemma, set())
    all_caps = bool(forms) and all(f[0].isupper() for f in forms)
    offs = noun_index.get(lemma, [])
    all_inst = bool(offs) and all(o in instance_syn for o in offs)
    return all_caps or all_inst

def is_unit(lemma):
    if lemma not in wn_pos_lemmas['n']: return False
    if any(lemma in wn_pos_lemmas[p] for p in ('v', 'a', 'r')): return False
    offs = noun_index.get(lemma, [])
    return bool(offs) and all(o in unit_desc for o in offs)

# --- morphology fold tables (WordNet .exc) -----------------------------------
exc_base = {}
for fn in ('noun.exc', 'verb.exc', 'adj.exc', 'adv.exc'):
    for line in open(os.path.join(DICT, fn), encoding='latin-1'):
        parts = line.split()
        if len(parts) >= 2: exc_base.setdefault(parts[0], parts[1])

# morphy-style regular detachment (band C only): a frequency token whose
# detached base is itself a WordNet lemma is treated as an inflected surface
# and skipped — its base ranks on its own. Deliberate precision/recall trade:
# kills "things/wanted/going/looking"-type surface junk; genuinely distinct
# -ing/-s lemmas (morning, building, news, ...) survive via band B (core list
# is processed first). Documented limitation: non-core derived nouns like
# "shopping" fold away.
DETACH = [('ses','s'),('xes','x'),('zes','z'),('ches','ch'),('shes','sh'),
          ('men','man'),('ies','y'),('es','e'),('es',''),('s',''),
          ('ed','e'),('ed',''),('ing','e'),('ing',''),
          ('er',''),('est',''),('er','e'),('est','e')]
def regular_base(tok):
    for suf, rep in DETACH:
        if tok.endswith(suf) and len(tok) - len(suf) + len(rep) >= 2:
            cand = tok[:len(tok)-len(suf)] + rep
            if cand != tok and cand in wn_all:
                return cand
    return None

# --- band B: core WordNet ----------------------------------------------------
CORE_RE = re.compile(r'^([nvar]) \[([^\]]+)\] \[([^\]]+)\](?: (.*))?$')
bandB = OrderedDict()   # lemma -> {senseKeys, pos, glossHints, coreCapitalised}
core_total = core_multiword = core_capitalised = 0
for line in open(CORE, encoding='utf-8'):
    m = CORE_RE.match(line.strip())
    if not m: continue
    core_total += 1
    pos, sense, lemma_c, hint = m.group(1), m.group(2), m.group(3), m.group(4)
    if '_' in lemma_c or ' ' in lemma_c:
        core_multiword += 1; continue
    if lemma_c[0].isupper():
        core_capitalised += 1; continue    # capitalised core entries are proper nouns
    lemma = lemma_c.lower()
    e = bandB.setdefault(lemma, {'senseKeys': [], 'pos': set(), 'hints': []})
    e['senseKeys'].append(sense); e['pos'].add(pos)
    if hint: e['hints'].append(hint)

# --- band C: frequency list --------------------------------------------------
freq_rank = {}          # lemma -> rank in raw list (1-based, first occurrence)
bandC_pool = []         # ordered content lemmas (candidates incl. A/B members)
seen = set()
for k, line in enumerate(open(FREQ, encoding='utf-8'), 1):
    tok = line.split()[0]
    if tok in freq_rank: continue
    freq_rank.setdefault(tok, k)
    if len(bandC_pool) >= TOP_N: continue
    if not re.fullmatch(r'[a-z]{2,}', tok): continue
    if tok in STOP: continue
    base = exc_base.get(tok)
    if base and base != tok and base in wn_all:
        continue                    # irregular inflected form; base ranks on its own
    if tok not in wn_all: continue  # not a WordNet lemma => not a content lemma
    if regular_base(tok):
        continue                    # regular inflected surface (see DETACH note)
    if tok in seen: continue
    seen.add(tok); bandC_pool.append(tok)

# --- merge + exclude ---------------------------------------------------------
items, excluded = [], []
def consider(lemma, band, extra):
    reasons = None
    if lemma in PRIMES: reasons = ('prime', None)
    elif lemma in STOP: reasons = ('function', None)
    elif lemma in covered: reasons = ('covered', covered[lemma])
    elif lemma in sector_label: reasons = ('sector', sector_label[lemma])
    elif is_unit(lemma): reasons = ('sector', 'physics-v0:unit-subtree')
    elif band != 'A' and is_entity(lemma): reasons = ('entity', None)
    if reasons:
        excluded.append({'lemma': lemma, 'band': band, 'reason': reasons[0],
                         'detail': reasons[1], **extra})
        return
    items.append({'lemma': lemma, 'band': band,
                  'freqRank': freq_rank.get(lemma), **extra})

for lemma, row in bandA.items():
    consider(lemma, 'A', {'sources': ['m0b'], 'm0bClass': row['class'],
                          'tsCount': row['count']})
inA = {it['lemma'] for it in items}
for lemma, e in bandB.items():
    if lemma in inA or lemma in bandA: continue
    consider(lemma, 'B', {'sources': ['core-wn'],
                          'pos': sorted(e['pos']), 'senseKeys': e['senseKeys'][:5],
                          'glossHint': (e['hints'][0] if e['hints'] else None)})
inAB = {it['lemma'] for it in items}
for lemma in bandC_pool:
    if lemma in inAB or lemma in bandA or lemma in bandB: continue
    pos = sorted(p for p in 'nvar' if lemma in wn_pos_lemmas[p])
    consider(lemma, 'C', {'sources': ['freq'], 'pos': pos})

# rank: band A by TinyStories count desc, then B and C by frequency rank
BIG = 10**9
items.sort(key=lambda it: (
    {'A': 0, 'B': 1, 'C': 2}[it['band']],
    -(it.get('tsCount') or 0),
    it['freqRank'] if it['freqRank'] is not None else BIG,
    it['lemma']))
for r, it in enumerate(items, 1): it['rank'] = r

with open(os.path.join(HERE, 'inventory.jsonl'), 'w') as f:
    for it in items:
        f.write(json.dumps(it, sort_keys=True) + '\n')
with open(os.path.join(HERE, 'inventory-excluded.jsonl'), 'w') as f:
    for e in sorted(excluded, key=lambda x: (x['band'], x['lemma'])):
        f.write(json.dumps(e, sort_keys=True) + '\n')

# --- sizing table ------------------------------------------------------------
from collections import Counter
bc = Counter(it['band'] for it in items)
xc = Counter((e['band'], e['reason']) for e in excluded)
cum, cut_band = 0, None
band_cum = {}
for b in 'ABC':
    cum += bc[b]; band_cum[b] = cum
    if cut_band is None and cum >= CUT_TARGET: cut_band = b
n_at_cut = min(CUT_TARGET, len(items))
sizing = f"""# haiku-tier inventory — sizing (stage 0)

Generated deterministically by `build-inventory.py` from the pinned sources in
`pins.json` (sha256-verified at run time). {len(items)} ranked items;
{len(excluded)} exclusions (audit trail: `inventory-excluded.jsonl`).

| band | source | items | cumulative |
|---|---|---|---|
| A | M0b measured gaps (post-molecules-v0 top-500) | {bc['A']} | {band_cum['A']} |
| B | WordNet core (~5k senses -> single-word, non-proper lemmas) | {bc['B']} | {band_cum['B']} |
| C | OpenSubtitles-2018 frequency top-{TOP_N} content lemmas | {bc['C']} | {band_cum['C']} |

**The ~{CUT_TARGET} cut lands in band {cut_band}** — every measured-gap and
core-WordNet concept is inside the budget; the cut point trims only the
frequency tail. At the cut: rank {n_at_cut} = lemma
`{items[n_at_cut-1]['lemma']}` (freq rank {items[n_at_cut-1].get('freqRank')}).

## Exclusions by band and reason

| band | covered | prime | function | entity | sector | total |
|---|---|---|---|---|---|---|
""" + '\n'.join(
    f"| {b} | {xc[(b,'covered')]} | {xc[(b,'prime')]} | {xc[(b,'function')]} | "
    f"{xc[(b,'entity')]} | {xc[(b,'sector')]} | {sum(v for k,v in xc.items() if k[0]==b)} |"
    for b in 'ABC') + f"""

Core-list preprocessing: {core_total} entries -> {core_multiword} multiword
dropped (v0 targets single-token lemmas; multiword lexemes are a filed
follow-up), {core_capitalised} capitalised (proper-noun) dropped,
{len(bandB)} distinct lemmas considered.

Sector-routed lemmas (flagged to physics-v0/math-v0, not Haiku-authored):
{sorted(set(e['lemma'] for e in excluded if e['reason']=='sector'))}

Entity rule and every other exclusion rule: see the module docstring of
`build-inventory.py` (the documented, mechanical rules).
"""
open(os.path.join(HERE, 'sizing.md'), 'w').write(sizing)
print(f"OK inventory={len(items)} (A={bc['A']} B={bc['B']} C={bc['C']}) "
      f"excluded={len(excluded)} cut@{CUT_TARGET} in band {cut_band}")
