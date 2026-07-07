#!/usr/bin/env python3
"""Emit mapper/m0/shadowed-judgments.jsonl: per-occurrence sense judgments for
the five ambiguity-shadowed concepts (bead kernel-of-truth-30d), authored by
the mapper-policy agent (Claude Fable 5) on 2026-07-07 after reading every
sampled token in its story context (shadowed-sample.jsonl, 50 per concept,
seed 0x5EED05).

AGENT-JUDGED, PENDING HUMAN ANNOTATION — same caveat discipline as the M0a
provisional precision/recall (make-agent-judgments.py); a human pass over
shadowed-sample.jsonl supersedes this file.

trueTarget semantics (mirrors the sample's instructions):
- a target key            that candidate alone is the correct contextual mapping
- 'either'                the candidates are sense-identical in context (for
                          inside/near the prime and the concept denote the
                          same spatial relation — ontology duplication, not
                          polysemy; the tie is a modelling decision, not WSD)
- 'neither'               the contextual sense matches no candidate (for kind:
                          'nice/caring', which kernel-v0 does not carry; for
                          lost: idioms 'lose one's balance/way/grip')

Judgment criteria per concept (stated before judging):
- broken: attributive/predicative STATE ('the broken toy', 'it was broken')
  -> urn:kernel-v0:broken; perfect/eventive verb ('had broken a rib', 'the
  rope had broken') -> urn:kernel-v0:break.
- lost:   STATE (cannot find one's way / cannot be found: 'was lost', 'got
  lost', 'a lost dog') -> urn:kernel-v0:lost; transitive past of lose ('lost
  his ball') -> urn:kernel-v0:lose; idioms -> neither.
- inside/near: spatial containment/proximity (prep or adverbial with implicit
  landmark) -> 'either' (candidates sense-identical).
- kind:   'nice/caring' -> neither; sortal ('all kinds of') -> 'either'
  (prime KIND and gufo:Kind concept both taxonomic).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

BROKEN = 'urn:kernel-v0:broken'
BREAK = 'urn:kernel-v0:break'
LOST = 'urn:kernel-v0:lost'
LOSE = 'urn:kernel-v0:lose'

# ---- broken: default state; exceptions verbal-perfect (all 'had broken') ----
J = {}
for i in range(1, 51):
    J[f'shadow-broken-{i:02d}'] = (BROKEN, 'stative (attributive or predicative adjective)')
for i, note in {
    2: "pluperfect 'had broken free' (phrasal, escape event)",
    10: "pluperfect active 'They had broken the new train'",
    13: "pluperfect active 'Timmy had broken a rib'",
    33: "pluperfect active 'he had broken something'",
    34: "pluperfect intransitive 'The battery had broken and leaked'",
    47: "pluperfect intransitive 'One of the ropes had broken'",
    49: "pluperfect intransitive 'the toy had broken into two pieces'",
}.items():
    J[f'shadow-broken-{i:02d}'] = (BREAK, note)

# ---- lost: state vs lose-verb vs idiom, judged per item --------------------
LOST_STATE = [1, 3, 5, 7, 8, 10, 11, 14, 15, 19, 22, 25, 27, 28, 29,
              34, 35, 37, 39, 43, 45, 46, 48, 49]
LOST_VERB = [2, 4, 6, 9, 12, 13, 17, 18, 20, 21, 23, 24, 26, 30, 31,
             32, 36, 38, 41, 42, 44, 47, 50]
for i in LOST_STATE:
    J[f'shadow-lost-{i:02d}'] = (LOST, "state: cannot find one's way / cannot be found")
for i in LOST_VERB:
    J[f'shadow-lost-{i:02d}'] = (LOSE, 'transitive past of lose (X loses Y)')
for i, note in {
    16: "idiom 'lost his balance' — neither possession-loss nor lost-state",
    33: "idiom 'lost his way' — the following 'got lost' carries the state",
    40: "idiom 'lost her grip'",
}.items():
    J[f'shadow-lost-{i:02d}'] = ('neither', note)

# ---- inside / near: spatial in every sampled occurrence --------------------
for i in range(1, 51):
    J[f'shadow-inside-{i:02d}'] = (
        'either',
        'spatial containment; prime INSIDE and concept inside sense-identical',
    )
    J[f'shadow-near-{i:02d}'] = (
        'either',
        'spatial proximity; prime NEAR and concept near sense-identical',
    )

# ---- kind: 'nice' everywhere except one sortal plural ----------------------
for i in range(1, 51):
    J[f'shadow-kind-{i:02d}'] = (
        'neither',
        "sense 'nice/caring' — matches neither prime KIND nor gufo:Kind sortal",
    )
J['shadow-kind-25'] = ('either', "sortal: 'all kinds of shapes and colours'")

items = [json.loads(l) for l in open(os.path.join(HERE, 'shadowed-sample.jsonl'))]
assert len(items) == 250
out = []
tally = {}
for it in items:
    true_target, note = J[it['itemId']]
    rec = {
        'itemId': it['itemId'],
        'concept': it['concept'],
        'surface': it['surface'],
        'candidates': it['candidates'],
        'trueTarget': true_target,
        'note': note,
        'provenance': 'AGENT-JUDGED (Claude Fable 5, 2026-07-07); pending human annotation',
    }
    out.append(json.dumps(rec))
    short = it['concept'].replace('urn:kernel-v0:', '')
    tally.setdefault(short, {}).setdefault(true_target, 0)
    tally[short][true_target] += 1

path = os.path.join(HERE, 'shadowed-judgments.jsonl')
open(path, 'w').write('\n'.join(out) + '\n')
print(json.dumps(tally, indent=2))
print(f'{len(out)} judgments -> {path}')
