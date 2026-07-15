# Bridge adjudication summary (proxy panel; DESIGN-v2 §4)

closure: 39 records; verdicts: {'REPAIR': 15, 'ACCEPT': 21, 'UNRESOLVED': 3}

| bridge | final | self-flag | chain-lossy | lossy members |
|---|---|---|---|---|
| animal | ACCEPT | faithful | no | - |
| art | ACCEPT | lossy | YES | art |
| authority | ACCEPT | lossy | YES | authority, group |
| country | REPAIR | lossy | YES | authority, country, group |
| duty | REPAIR | lossy | YES | take, duty, money, work |
| eat | REPAIR | lossy | YES | eat |
| fight | REPAIR | lossy | YES | fight |
| food | ACCEPT | faithful | YES | eat |
| game | REPAIR | lossy | YES | game |
| group | ACCEPT | lossy | YES | group |
| grow | ACCEPT | faithful | no | - |
| hot | REPAIR | lossy | YES | hot |
| ill | REPAIR | faithful | YES | ill |
| institution | ACCEPT | faithful | YES | authority, group, law |
| kill | ACCEPT | faithful | no | - |
| law | REPAIR | lossy | YES | authority, group, law |
| machine | ACCEPT | faithful | no | - |
| man | UNRESOLVED | lossy | YES | birth, man |
| material | UNRESOLVED | lossy | YES | material |
| measure | REPAIR | lossy | YES | measure |
| money | REPAIR | lossy | YES | take, money |
| name | REPAIR | faithful | YES | name |
| own | ACCEPT | faithful | YES | take |
| sex | ACCEPT | lossy | YES | birth, man, sex |
| status | REPAIR | lossy | YES | group, status |
| surface | ACCEPT | faithful | no | - |
| tool | ACCEPT | faithful | no | - |
| woman | UNRESOLVED | faithful | YES | birth |
| work | ACCEPT | lossy | YES | take, money, work |
| worth | ACCEPT | lossy | YES | take, money, worth |
| write | REPAIR | faithful | YES | write |

**PENDING (REPAIR/REJECT/UNRESOLVED -- explicator loop, then re-run judges + summarize):** urn:kernel-v0:birth, urn:kernel-v0:take, urn:molaug-v0:country, urn:molaug-v0:duty, urn:molaug-v0:eat, urn:molaug-v0:fight, urn:molaug-v0:game, urn:molaug-v0:hot, urn:molaug-v0:ill, urn:molaug-v0:law, urn:molaug-v0:man, urn:molaug-v0:material, urn:molaug-v0:measure, urn:molaug-v0:money, urn:molaug-v0:name, urn:molaug-v0:status, urn:molaug-v0:woman, urn:molaug-v0:write

relabelled now -> 'provisional/model-authored (proxy-adjudicated)': 15 records. RE-RUN `node lexicon/build_manifest.mjs` then `run_s5.py compose --v2` (lexiconSetHash changed).
