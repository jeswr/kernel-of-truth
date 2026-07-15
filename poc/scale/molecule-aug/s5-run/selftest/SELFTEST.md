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
  },
  {
    "check": "compose v2: fidelity prompt embeds judge-addendum-v2",
    "ok": true,
    "detail": ""
  },
  {
    "check": "compose v2: conditional prompt = v1 addendum + single-candidate note",
    "ok": true,
    "detail": ""
  },
  {
    "check": "expand: teacher-ref -> subExplication inlined, deterministic, no concept nodes left",
    "ok": true,
    "detail": "{\n \"schema\": \"kot-ast/1\",\n \"frame\": \"InstanceSchema\",\n \"referents\": [\n  {\n   \"index\": 1,\n   \"refKind\": \"SomeoneRef\"\n  }\n ],\n \"clauses\": [\n  {\n   \"type\": \"pred\","
  },
  {
    "check": "expand: flat record passes through byte-identically",
    "ok": true,
    "detail": ""
  },
  {
    "check": "expand: bridge record (kill->death) expands recursively",
    "ok": true,
    "detail": ""
  },
  {
    "check": "expand: synthetic cycle fails closed",
    "ok": true,
    "detail": "ERR_CYCLIC_CONCEPT_REF"
  },
  {
    "check": "expand: unresolved id fails closed",
    "ok": true,
    "detail": "ERR_CONCEPT_UNRESOLVED"
  },
  {
    "check": "expand: depth > 6 fails closed",
    "ok": true,
    "detail": "ERR_EXPAND_DEPTH"
  },
  {
    "check": "stats: Tango score stat at delta=0 == McNemar z (b=1,c=9,n=24)",
    "ok": true,
    "detail": ""
  },
  {
    "check": "stats: Tango CI b=c=0,n=20 == analytic +-z^2/(n+z^2)",
    "ok": true,
    "detail": "(-0.1611251580528194, 0.16112515805281935, 0.16112515805281938)"
  },
  {
    "check": "stats: Tango CI golden (1,9,24) + score self-consistency at endpoints",
    "ok": true,
    "detail": "(0.11694770833431872, 0.5419758897765519)"
  },
  {
    "check": "stats: Tango CI (150,86,1600) sane vs Wald",
    "ok": true,
    "detail": "(-0.05858192806708333, -0.02149254161291215)"
  },
  {
    "check": "stats: kappa/AC1 unit (po=.5, .5 marginals -> 0/0)",
    "ok": true,
    "detail": "{'n': 4, 'raw': 0.5, 'kappa': 0.0, 'ac1': 0.0}"
  },
  {
    "check": "score: ITT/E2 truth table + paired counts",
    "ok": true,
    "detail": "[(True, False), (False, True), (False, False), (True, True)]"
  },
  {
    "check": "score: cascade S1-mirror selector",
    "ok": true,
    "detail": ""
  },
  {
    "check": "expand v2: gate-fail cells recorded for ITT (fake row flat cells + mol-fable)",
    "ok": true,
    "detail": "9 ok / 3 gate-fail"
  },
  {
    "check": "prep v2: ONE blind 6-hex input per candidate",
    "ok": true,
    "detail": ""
  },
  {
    "check": "prep v2: blind ids deterministic (seeded)",
    "ok": true,
    "detail": ""
  },
  {
    "check": "prep v2: single-candidate shape (one CANDIDATE A, no REFERENCED CONCEPTS)",
    "ok": true,
    "detail": ""
  },
  {
    "check": "prep v2: pool-of-one input validates under rp.validate_verdicts",
    "ok": true,
    "detail": ""
  },
  {
    "check": "prep v2: mol candidate is judged on its EXPANDED rendering",
    "ok": true,
    "detail": ""
  },
  {
    "check": "prep v2: conditional instrument = ref-bearing mol cells only",
    "ok": true,
    "detail": ""
  },
  {
    "check": "prep v2: conditional input carries raw AST + REFERENCED CONCEPTS gloss block",
    "ok": true,
    "detail": ""
  },
  {
    "check": "prep v2: seeded global queue order covers all candidates",
    "ok": true,
    "detail": ""
  },
  {
    "check": "adjudicate: closure = 31 bridges + their kernel-v0 reference closure",
    "ok": true,
    "detail": "closure=39"
  },
  {
    "check": "adjudicate: review validator accepts good / rejects bad JSON",
    "ok": true,
    "detail": ""
  },
  {
    "check": "adjudicate: review input renders the record's OWN expanded rendering, offline",
    "ok": true,
    "detail": ""
  },
  {
    "check": "freeze: live pins verify (only not-yet-built artefacts may be open)",
    "ok": true,
    "detail": "['fresh_sample_sha256']"
  },
  {
    "check": "freeze: tampered pin detected",
    "ok": true,
    "detail": ""
  },
  {
    "check": "freeze: pin mismatch DIES (fail closed)",
    "ok": true,
    "detail": ""
  }
]
```

**VERDICT: PASS**
