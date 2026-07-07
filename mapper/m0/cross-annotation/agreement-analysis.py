#!/usr/bin/env python3
"""Agreement analysis: codex-gpt judgments vs the Claude-lineage agent
judgments over the M0a annotation sample, plus a precision/recall
sensitivity check (recompute compute-pr.py's numbers with the codex
judgments substituted). Writes agreement.json, disagreements.jsonl and
agreement-report.md in this directory. Reads (never writes) the m0a
report for stratum populations.

Label normalisation onto one correct|incorrect|unclear scale ("was the
mapper's decision right?"):
- concept/prime: both annotators already use correct|incorrect|unclear.
- abstain: agent no-candidate-correct -> correct, candidate-correct -> incorrect.
- none: agent correctly-unmapped -> correct, should-map -> incorrect.
codex judgments were elicited directly on this scale (see
run-codex-annotation.py header).

Cohen's kappa over the 3-label space; reported as None when undefined
(expected agreement = 1, i.e. no label variance in either annotator).
"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
M0 = os.path.dirname(HERE)

sample = {json.loads(l)['itemId']: json.loads(l)
          for l in open(os.path.join(M0, 'annotation-sample.jsonl'))}
agent = {j['itemId']: j for j in
         (json.loads(l) for l in open(os.path.join(M0, 'agent-judgments.jsonl')))}
codex = {j['itemId']: j for j in
         (json.loads(l) for l in open(os.path.join(HERE, 'codex-judgments.jsonl')))}

AGENT_NORM = {
    'correct': 'correct', 'incorrect': 'incorrect', 'unclear': 'unclear',
    'no-candidate-correct': 'correct', 'candidate-correct': 'incorrect',
    'correctly-unmapped': 'correct', 'should-map': 'incorrect',
}
LABELS = ('correct', 'incorrect', 'unclear')
STRATA = ('concept', 'prime', 'abstain', 'none')


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for a, b in pairs if a == b) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[l] * cb[l] for l in LABELS) / (n * n)
    if pe >= 1.0:
        return None  # no variance; kappa undefined
    return (po - pe) / (1 - pe)


pairs_by_stratum = {s: [] for s in STRATA}
disagreements = []
for iid in sorted(sample):
    if iid not in codex:
        continue  # failed batch
    it = sample[iid]
    a = AGENT_NORM[agent[iid]['judgment']]
    c = codex[iid]['judgment']
    pairs_by_stratum[it['stratum']].append((a, c))
    if a != c:
        d = it['decision']
        disagreements.append({
            'itemId': iid, 'stratum': it['stratum'], 'surface': it['surface'],
            'target': d.get('target') or (', '.join(d.get('candidates', [])) or 'UNMAPPED'),
            'claudeAgent': agent[iid]['judgment'], 'claudeAgentNormalized': a,
            'codexGpt': c, 'agentNote': agent[iid].get('note', ''),
            'contextBefore': it['contextBefore'], 'contextAfter': it['contextAfter'],
        })

# rank: concept first (headline precision stratum), then prime, abstain, none
order = {s: i for i, s in enumerate(STRATA)}
disagreements.sort(key=lambda d: (order[d['stratum']], d['itemId']))

all_pairs = [p for s in STRATA for p in pairs_by_stratum[s]]


def agree_block(pairs):
    n = len(pairs)
    return {
        'n': n,
        'rawAgreement': round(sum(1 for a, b in pairs if a == b) / n, 4) if n else None,
        'cohensKappa': (lambda k: round(k, 4) if k is not None else None)(kappa(pairs)),
        'confusion': {f'{a}|{c}': sum(1 for x, y in pairs if (x, y) == (a, c))
                      for a in LABELS for c in LABELS
                      if sum(1 for x, y in pairs if (x, y) == (a, c))},
    }


# ---- P/R sensitivity: compute-pr.py logic with either annotator's judgments
report = json.load(open(os.path.join(M0, 'results', 'm0a-report.json')))
pop = {k: v['population'] for k, v in report['sampling']['strata'].items()}
mapped_pop = pop['concept'] + pop['prime']


def pr(judg_by_stratum):
    """judg_by_stratum: stratum -> list of normalized labels."""
    def frac(s, pred):
        xs = judg_by_stratum[s]
        return sum(1 for x in xs if pred(x)) / len(xs)
    p_strict = {s: frac(s, lambda x: x == 'correct') for s in ('concept', 'prime')}
    p_lenient = {s: frac(s, lambda x: x in ('correct', 'unclear')) for s in ('concept', 'prime')}

    def wprec(p):
        return (p['concept'] * pop['concept'] + p['prime'] * pop['prime']) / mapped_pop
    # miss = mapper's non-decision was wrong (normalized 'incorrect');
    # strict counts 'unclear' as a miss too, lenient does not.
    miss_strict = {s: frac(s, lambda x: x in ('incorrect', 'unclear')) for s in ('abstain', 'none')}
    miss_lenient = {s: frac(s, lambda x: x == 'incorrect') for s in ('abstain', 'none')}

    def recall(prec, miss):
        tp = prec * mapped_pop
        missed = miss['abstain'] * pop['abstain'] + miss['none'] * pop['none']
        return tp / (tp + missed)
    return {
        'precisionStrict': round(wprec(p_strict), 4),
        'precisionLenient': round(wprec(p_lenient), 4),
        'perStratumPrecisionStrict': {s: round(v, 4) for s, v in p_strict.items()},
        'recallStrict': round(recall(wprec(p_strict), miss_strict), 4),
        'recallLenient': round(recall(wprec(p_lenient), miss_lenient), 4),
        'abstainMissRateStrict': round(miss_strict['abstain'], 4),
        'noneMissRateStrict': round(miss_strict['none'], 4),
    }


agent_labels = {s: [AGENT_NORM[agent[i]['judgment']] for i in sorted(agent)
                    if agent[i]['stratum'] == s] for s in STRATA}
codex_labels = {s: [codex[i]['judgment'] for i in sorted(codex)
                    if codex[i]['stratum'] == s] for s in STRATA}

meta = next(iter(codex.values()))
out = {
    'date': '2026-07-07',
    'annotators': {
        'A': 'agent (Claude Fable 5), mapper/m0/agent-judgments.jsonl',
        'B': f"codex-gpt (OpenAI Codex v{meta.get('codexVersion')}, model {meta.get('model')}), codex-judgments.jsonl",
    },
    'itemsCompared': len(all_pairs),
    'itemsMissing': sorted(set(sample) - set(codex)),
    'overall': agree_block(all_pairs),
    'perStratum': {s: agree_block(pairs_by_stratum[s]) for s in STRATA},
    'disagreementCount': len(disagreements),
    'disagreementsByStratum': dict(Counter(d['stratum'] for d in disagreements)),
    'prSensitivity': {
        'claudeAgent': pr(agent_labels),
        'codexGpt': pr(codex_labels),
        'decomposition': {
            'codexMappedAndAbstain_agentNone': pr({**codex_labels, 'none': agent_labels['none']}),
            'codexMappedAndNone_agentAbstain': pr({**codex_labels, 'abstain': agent_labels['abstain']}),
            'note': 'isolates which non-mapped stratum drives the recall gap between annotators',
        },
        'note': 'compute-pr.py logic; strict counts unclear as incorrect (mapped strata) / as a miss (abstain+none strata). Claude-agent row differs from results/m0a-report.json recall only in that the original had zero unclear judgments in abstain/none so strict==original there.',
        'codexNoneCaveat': 'codex was not shown the kernel-v0 inventory (54 concepts + 65 prime exponent lists); its none-stratum should-map judgments are semantic coverage claims that may name targets the inventory does not contain. By mapper construction every none-stratum token has NO lexicon entry for its surface or lemma.',
    },
}
with open(os.path.join(HERE, 'agreement.json'), 'w') as f:
    json.dump(out, f, indent=2)
    f.write('\n')
with open(os.path.join(HERE, 'disagreements.jsonl'), 'w') as f:
    for d in disagreements:
        f.write(json.dumps(d) + '\n')
print(json.dumps({k: out[k] for k in ('overall', 'perStratum', 'disagreementCount',
                                      'disagreementsByStratum', 'prSensitivity')}, indent=2))
