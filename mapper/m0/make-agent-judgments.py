#!/usr/bin/env python3
"""Emit mapper/m0/agent-judgments.jsonl from the per-item judgments authored
by the M0 agent (Claude Fable 5) on 2026-07-07, after reading every sampled
token in its story context.

PROVISIONAL: agent-judged, pending human annotation. The pre-registration
(poc-design.md Phase M / M0a) names HUMAN annotation as the measurement; these
judgments exist so a provisional precision/recall can be reported before that
happens, and they are superseded by the human pass over
mapper/m0/annotation-sample.jsonl.

Judgment criteria (stated):
- concept/prime strata — "correct" iff the token's contextual WORD SENSE is
  the sense the mapped kernel target denotes (checked against the concept
  gloss / NSM prime); explication ADEQUACY is out of scope (M0a measures the
  mapper, not the explications). Light-verb, phrasal-verb, idiomatic and
  auxiliary uses whose sense differs from the target are "incorrect".
  "unclear" = genuinely contestable sense assignment (e.g. indefinite
  "one day"; "big difference" degree reading); reported both ways
  (strict = unclear counted incorrect; lenient = counted correct).
- abstain stratum — "candidate-correct" iff at least one recorded candidate
  is the correct annotation in context (trueTarget names it); such tokens
  count as recall misses. "no-candidate-correct" = abstention was the right
  outcome (mostly attributive/auxiliary copulas, which are grammatical glue
  with no kernel target).
- none stratum — "should-map" iff some kernel-v0 concept/prime is the correct
  annotation (counts as a recall miss); else "correctly-unmapped".
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# stratum concept+prime: itemId -> (judgment, trueTarget, note)
J = {}
for i in range(1, 101):
    J[f'm0a-{i:03d}'] = ('correct', '', '')
for iid, note in {
    'm0a-002': "right = 'correct about facts', of a person; concept is of-a-doable-something",
    'm0a-005': "take = transport ('taken to the hospital'), not possession acquisition",
    'm0a-006': "light verb: 'took a few steps'",
    'm0a-013': "right = 'suitable' ('the right friend')",
    'm0a-020': "make = causative ('made her feel safe'), not creation",
    'm0a-039': "light verb: 'gave her a big surprise', no possession transfer",
    'm0a-042': "make = causative ('make the plane zoom')",
    'm0a-050': "idiom: 'find its way home'",
    'm0a-054': "make = causative ('made it glow')",
    'm0a-056': "make = causative ('make someone else happy')",
    'm0a-060': "find = realize ('surprised to find he was still in the car')",
    'm0a-067': "lie = recline ('lying there'); concept lie = the words. Homonym collision",
    'm0a-071': "phrasal verb: 'gave up'",
    'm0a-072': "take out = retrieve one's own object; no possession change",
    'm0a-076': "make = causative ('made the girl happy')",
    'm0a-078': "make = causative ('make his house look more amazing')",
}.items():
    J[iid] = ('incorrect', '', note)
J['m0a-022'] = ('unclear', '', "'change her mind' idiom; become-different reading defensible")
J['m0a-068'] = ('unclear', '', "physical keepsake called 'a memory'; concept requires stored-at-a-part-of-someone")
J['m0a-045'] = ('correct', '', "'made of ice blocks': creation sense present; material aspect beyond gloss")
J['m0a-047'] = ('correct', '', "remember-to (prospective); recall-of-known-something reading holds loosely")
J['m0a-058'] = ('correct', '', "anticausative 'it broke'; breaking sense correct, agent implicit (valency mismatch noted)")

for i in range(101, 201):
    J[f'm0a-{i:03d}'] = ('correct', '', '')
for iid, note in {
    'm0a-101': "like = enjoy ('liked to play'); prime is similarity",
    'm0a-104': "'after all' idiom, not temporal AFTER",
    'm0a-116': 'like = enjoy',
    'm0a-145': "'ran after it' = pursuit, not temporal",
    'm0a-150': 'like = enjoy',
    'm0a-167': "auxiliary do ('Do you know'), not the action prime",
    'm0a-173': "way = route ('find his way back home'), not manner",
    'm0a-182': 'like = enjoy',
    'm0a-200': "auxiliary do ('Where did you last see')",
}.items():
    J[iid] = ('incorrect', '', note)
for iid, note in {
    'm0a-122': "'big difference' = degree, not physical size",
    'm0a-125': "'one day' = indefinite determiner use; single-unspecified-day reading defensible",
    'm0a-126': "'couldn't wait' idiom; negation not compositional",
    'm0a-132': "'one day' indefinite (as m0a-125)",
    'm0a-144': "'one day' indefinite (as m0a-125)",
    'm0a-154': "'one day' indefinite (as m0a-125)",
    'm0a-181': "'one day' indefinite (as m0a-125)",
    'm0a-189': "see = visit ('brought Lily to see you')",
    'm0a-191': "'best friends' idiom; superlative-good reading partial",
}.items():
    J[iid] = ('unclear', '', note)
J['m0a-106'] = ('correct', '', "'once upon a time': temporal-noun sense (at some time before now)")
J['m0a-169'] = ('correct', '', "'once upon a time' (as m0a-106)")
J['m0a-171'] = ('correct', '', "'feel better': goodness sense; comparative morphology folded by lemmatizer")
J['m0a-178'] = ('correct', '', "'can I help': permission request; possibility reading available")

# abstain stratum: candidate-correct (recall miss) vs no-candidate-correct
ABSTAIN_YES = {
    'm0a-201': 'prime:INSIDE', 'm0a-202': 'prime:BE-SPEC', 'm0a-205': 'prime:BE-SOMEWHERE',
    'm0a-207': 'prime:BE-SPEC', 'm0a-209': 'prime:BE-SPEC', 'm0a-212': 'prime:BE-SPEC',
    'm0a-213': 'prime:SMALL', 'm0a-223': 'prime:SMALL', 'm0a-224': 'prime:BE-SOMEWHERE',
    'm0a-227': 'prime:BE-SPEC', 'm0a-228': 'prime:BE-SOMEWHERE', 'm0a-229': 'prime:SMALL',
    'm0a-234': 'prime:SMALL', 'm0a-239': 'prime:BE-SPEC', 'm0a-240': 'prime:BE-SPEC',
    'm0a-243': 'prime:BE-SOMEWHERE', 'm0a-248': 'prime:BE-SOMEWHERE', 'm0a-249': 'prime:SMALL',
}
for i in range(201, 251):
    iid = f'm0a-{i:03d}'
    if iid in ABSTAIN_YES:
        J[iid] = ('candidate-correct', ABSTAIN_YES[iid], 'abstained where a listed candidate was right (recall miss)')
    else:
        J[iid] = ('no-candidate-correct', '',
                  'no listed candidate correct in context (attributive/auxiliary copula or degree "little"); abstention was the right outcome')
J['m0a-247'] = ('no-candidate-correct', '',
                "corpus typo: possessive 'its' written \"it's\"; tokenizer expanded it to it+is — artifact, no correct candidate")

# none stratum: all judged correctly-unmapped (function words, proper names,
# out-of-lexicon content words with no kernel-v0 target)
for i in range(251, 301):
    J[f'm0a-{i:03d}'] = ('correctly-unmapped', '', '')

items = [json.loads(l) for l in open(os.path.join(HERE, 'annotation-sample.jsonl'))]
assert len(items) == 300
out = []
for it in items:
    j, tt, note = J[it['itemId']]
    rec = {
        'itemId': it['itemId'],
        'stratum': it['stratum'],
        'surface': it['surface'],
        'norm': it['norm'],
        'decision': it['decision'],
        'judgment': j,
        'trueTarget': tt,
        'note': note,
        'judge': 'agent (Claude Fable 5), 2026-07-07 — PROVISIONAL, pending human annotation (pre-registration names human annotation; this file does NOT satisfy it)',
    }
    out.append(json.dumps(rec))
with open(os.path.join(HERE, 'agent-judgments.jsonl'), 'w') as f:
    f.write('\n'.join(out) + '\n')

# summary counts
from collections import Counter
c = Counter((json.loads(l)['stratum'], json.loads(l)['judgment']) for l in out)
for k in sorted(c):
    print(k, c[k])
