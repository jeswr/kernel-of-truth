# S5 offline selftest

No model calls; codex not required.

```json
[
  {
    "check": "compose: base prompt embedded",
    "ok": true,
    "detail": ""
  },
  {
    "check": "compose: ref-addendum embedded",
    "ok": true,
    "detail": ""
  },
  {
    "check": "compose: 85-line lexicon listing embedded",
    "ok": true,
    "detail": ""
  },
  {
    "check": "compose: judge addendum embedded",
    "ok": true,
    "detail": ""
  },
  {
    "check": "gate: ref-bearing record resolves (kernel + bridge), unit-norm D=8192",
    "ok": true,
    "detail": "{'ok': True, 'stats': {'clauseCount': 2, 'maxDepth': 2, 'referentCount': 1}, 'D': 8192, 'norm': 1.0000000000000018, 'references': ['urn:kernel-v0:teacher', 'urn:molaug-v0:money'], 'lexiconSize': 85}"
  },
  {
    "check": "gate: flat record still passes (R3 superset)",
    "ok": true,
    "detail": "{'ok': True, 'stats': {'clauseCount': 1, 'maxDepth': 1, 'referentCount': 1}, 'D': 8192, 'norm': 0.999999999999988, 'references': [], 'lexiconSize': 85}"
  },
  {
    "check": "gate: unknown id -> ERR_REF_NOT_IN_LEXICON",
    "ok": true,
    "detail": "{'ok': False, 'code': 'ERR_REF_NOT_IN_LEXICON', 'error': \"'urn:molaug-v0:nonexistent' is not in the referenceable lexicon\"}"
  },
  {
    "check": "gate: field/AST mismatch -> ERR_REF_MISMATCH",
    "ok": true,
    "detail": "{'ok': False, 'code': 'ERR_REF_MISMATCH', 'error': 'references [] != AST concept ids [urn:kernel-v0:teacher]'}"
  },
  {
    "check": "gate: self-reference -> ERR_SELF_REF",
    "ok": true,
    "detail": "{'ok': False, 'code': 'ERR_SELF_REF', 'error': 'record references itself'}"
  },
  {
    "check": "gate: 9 distinct refs -> ERR_REF_CAP",
    "ok": true,
    "detail": "{'ok': False, 'code': 'ERR_REF_CAP', 'error': '9 distinct references exceeds cap 8'}"
  },
  {
    "check": "gate: real consensus-100 flat record passes unchanged (access.fable5.json)",
    "ok": true,
    "detail": "{'ok': True, 'stats': {'clauseCount': 6, 'maxDepth': 4, 'referentCount': 3}, 'D': 8192, 'norm': 1.0000000000000002, 'references': [], 'lexiconSize': 85}"
  },
  {
    "check": "prep plumbing: judge-inputs built from mixed pool",
    "ok": true,
    "detail": "8 candidates over 2 concepts"
  },
  {
    "check": "prep plumbing: s5gate written & ok for synthetic flat-shaped records",
    "ok": true,
    "detail": ""
  },
  {
    "check": "stats: McNemar exact b=1,c=9 -> p=0.0215",
    "ok": true,
    "detail": ""
  },
  {
    "check": "stats: McNemar exact b=0,c=0 -> p=1",
    "ok": true,
    "detail": ""
  },
  {
    "check": "stats: Wilson 9/10 CI sane",
    "ok": true,
    "detail": "(0.5958499732047615, 0.9821237869049271)"
  }
]
```

**VERDICT: PASS**
