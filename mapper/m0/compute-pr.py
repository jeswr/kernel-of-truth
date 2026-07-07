#!/usr/bin/env python3
"""Compute provisional precision/recall for M0a from agent-judgments.jsonl,
reweighted by stratum populations, and append them to results/m0a-report.json.

CAVEAT stamped into every output: agent-judged, pending human annotation.

Definitions:
- precision = P(mapped target is the correct contextual sense | mapper mapped),
  weighted over the concept/prime strata by their token populations.
  strict: 'unclear' counted incorrect; lenient: counted correct.
- recall = correct-mapped mass / (correct-mapped mass + missed mass), where
  missed = abstained tokens with a correct candidate + unmapped tokens that
  should have mapped, each scaled by stratum population. Tokens mapped to a
  WRONG target whose true sense is outside kernel-v0 are excluded from the
  denominator (measured: all incorrect items in the sample had no kernel
  target for their contextual sense).
- The none stratum sampled 0/50 misses; the 95% Clopper-Pearson upper bound
  (1 - 0.05^(1/50) = 5.8%) over its 2.96M-token population gives the reported
  recall LOWER bound — n=50 is thin coverage of 78% of the token mass.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
report_path = os.path.join(HERE, 'results', 'm0a-report.json')
report = json.load(open(report_path))
pop = {k: v['population'] for k, v in report['sampling']['strata'].items()}

js = [json.loads(l) for l in open(os.path.join(HERE, 'agent-judgments.jsonl'))]
by = {}
for j in js:
    by.setdefault(j['stratum'], []).append(j['judgment'])

def frac(stratum, pred):
    xs = by[stratum]
    return sum(1 for x in xs if pred(x)) / len(xs)

p_strict = {s: frac(s, lambda x: x == 'correct') for s in ('concept', 'prime')}
p_lenient = {s: frac(s, lambda x: x in ('correct', 'unclear')) for s in ('concept', 'prime')}
mapped_pop = pop['concept'] + pop['prime']

def wprec(p):
    return (p['concept'] * pop['concept'] + p['prime'] * pop['prime']) / mapped_pop

abstain_miss = frac('abstain', lambda x: x == 'candidate-correct')
none_miss = frac('none', lambda x: x == 'should-map')
none_miss_upper95 = 1 - 0.05 ** (1 / len(by['none']))  # Clopper-Pearson upper, 0 observed

def recall(prec, none_rate):
    tp = prec * mapped_pop
    missed = abstain_miss * pop['abstain'] + none_rate * pop['none']
    return tp / (tp + missed)

prov = {
    'caveat': 'AGENT-JUDGED, PENDING HUMAN ANNOTATION — the pre-registration (poc-design.md M0a) names human annotation; these numbers are provisional and superseded by the human pass over annotation-sample.jsonl',
    'judge': 'Claude Fable 5, 2026-07-07; criteria in make-agent-judgments.py',
    'sampleCounts': {s: dict((j, by[s].count(j)) for j in sorted(set(by[s]))) for s in by},
    'precision': {
        'strict': round(wprec(p_strict), 4),
        'lenient': round(wprec(p_lenient), 4),
        'perStratumStrict': {s: round(v, 4) for s, v in p_strict.items()},
        'note': 'strict counts unclear as incorrect; lenient as correct; weighted by stratum token populations',
    },
    'recall': {
        'strict': round(recall(wprec(p_strict), none_miss), 4),
        'lenient': round(recall(wprec(p_lenient), none_miss), 4),
        'lowerBound95': round(recall(wprec(p_strict), none_miss_upper95), 4),
        'abstainMissRate': round(abstain_miss, 4),
        'noneMissRate': none_miss,
        'noneMissUpper95': round(none_miss_upper95, 4),
        'note': 'recall over tokens whose true annotation is a kernel-v0 target; lowerBound95 assumes the none-stratum miss rate at its 95% Clopper-Pearson upper bound (0/50 observed over a 2.96M-token stratum)',
    },
}
report['provisionalPrecisionRecall'] = prov
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)
    f.write('\n')
print(json.dumps(prov['precision'], indent=2))
print(json.dumps(prov['recall'], indent=2))
