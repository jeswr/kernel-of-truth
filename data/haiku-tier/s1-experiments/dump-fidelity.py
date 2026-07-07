#!/usr/bin/env python3
"""Dump Haiku outputs vs hand-authored records for the 15 fidelity concepts,
side by side, for agent judging (labelled as such in s1-report.md)."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
fw = sys.argv[1] if len(sys.argv) > 1 else 'A'

concepts = json.load(open(os.path.join(HERE, 'concepts.json')))
for c in concepts:
    if not c['group'].startswith('fidelity'): continue
    lemma = c['lemma']
    print('=' * 70)
    print(f'## {lemma} ({c["group"]})')
    if c['group'] == 'fidelity-kernel':
        h = json.load(open(os.path.join(REPO, 'data', 'kernel-v0', 'concepts', lemma + '.json')))
        print(f'HUMAN gloss: {h["gloss"]}')
        print(f'HUMAN explication: {json.dumps(h["explication"], separators=(",", ":"))[:1200]}')
    else:
        h = json.load(open(os.path.join(REPO, 'data', 'molecules-v0', 'molecules', lemma + '.json')))
        print(f'HUMAN groundingNote: {h["groundingNote"]}')
        print(f'HUMAN notes: {h.get("notes")}')
    env = json.load(open(os.path.join(HERE, 'outputs', fw, lemma + '.json')))
    print(f'HAIKU ({fw}): {env["result"].strip()[:1500]}')
    print()
