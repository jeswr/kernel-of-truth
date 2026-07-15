# Bridge adjudication summary (proxy panel; DESIGN-v2 §4)

closure: 39 records; verdicts: {'ACCEPT': 27, 'REPAIR': 12}

| bridge | final | self-flag | chain-lossy | lossy members |
|---|---|---|---|---|
| animal | ACCEPT | faithful | no | - |
| art | REPAIR | lossy | YES | make, art |
| authority | ACCEPT | lossy | YES | authority, group |
| country | ACCEPT | lossy | YES | authority, country, group |
| duty | REPAIR | lossy | YES | give, duty, money, work |
| eat | REPAIR | lossy | YES | eat |
| fight | REPAIR | lossy | YES | fight |
| food | ACCEPT | faithful | YES | eat |
| game | ACCEPT | lossy | YES | game |
| group | ACCEPT | lossy | YES | group |
| grow | ACCEPT | faithful | no | - |
| hot | ACCEPT | lossy | YES | hot |
| ill | ACCEPT | faithful | no | - |
| institution | REPAIR | faithful | YES | authority, group, institution, law |
| kill | ACCEPT | faithful | no | - |
| law | ACCEPT | lossy | YES | authority, group, law |
| machine | REPAIR | faithful | YES | make, machine |
| man | REPAIR | lossy | YES | man |
| material | ACCEPT | lossy | YES | make, material |
| measure | REPAIR | lossy | YES | measure |
| money | ACCEPT | lossy | YES | give, money |
| name | ACCEPT | faithful | no | - |
| own | ACCEPT | faithful | no | - |
| sex | ACCEPT | lossy | YES | man, sex |
| status | REPAIR | lossy | YES | group, status |
| surface | ACCEPT | faithful | no | - |
| tool | ACCEPT | faithful | YES | make |
| woman | ACCEPT | faithful | no | - |
| work | ACCEPT | lossy | YES | give, money, work |
| worth | ACCEPT | lossy | YES | give, money, worth |
| write | REPAIR | faithful | YES | make, write |

**PENDING (REPAIR/REJECT/UNRESOLVED -- explicator loop, then re-run judges + summarize):** urn:kernel-v0:give, urn:kernel-v0:make, urn:molaug-v0:art, urn:molaug-v0:duty, urn:molaug-v0:eat, urn:molaug-v0:fight, urn:molaug-v0:institution, urn:molaug-v0:machine, urn:molaug-v0:man, urn:molaug-v0:measure, urn:molaug-v0:status, urn:molaug-v0:write

relabelled now -> 'provisional/model-authored (proxy-adjudicated)': 9 records. RE-RUN `node lexicon/build_manifest.mjs` then `run_s5.py compose --v2` (lexiconSetHash changed).
