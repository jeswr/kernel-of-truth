# Referenceable-lexicon plan — molecule-aug bridge tier (Tier A-1)

DESIGN ARTEFACT of `../DESIGN.md` §3. Nothing here is authored yet; this file is
the work order for the explicator agent. STIPULATED-not-MEASURED except where a
path is cited.

## Composition of the referenceable lexicon (85 ids)

1. **54 × `data/kernel-v0/concepts/*.json` — reused AS-IS.** No copy is made; the
   S5 gate and the listing generator read them in place. Their manifest already
   pins them to the current encoder content hash.
2. **31 × bridge records** authored into `lexicon/records/<slug>.json`, namespace
   `urn:molaug-v0:<slug>`, kernel-v0 record shape
   `{id, label, status, pattern, gloss, notes, references, explication}` with
   `status: "research-grade"` and the `AST adequacy:` self-flag in `notes`.

## Selection evidence

Word list = greedy set-cover over the 470 lossy notes mined from
`poc/scale/consensus-100/gen/*.json` (599 records; method + script:
`../mine_lossy.py`), pruned by the mint-only-what-explication-cannot-reach rule
of `docs/design-molecule-tier.md` §1.2. Deliberately NOT minted because they
become explicable once the bridge exists (the pressure-flows-back-to-explication
discipline): pay, buy, sell, refund, price, tax (→ money, give, worth), medicine,
doctor (→ ill, help, substance-as-material), soldier, war (→ fight, country,
group), school (→ teacher/learn, institution), metal (→ material, hot), vehicle
(→ machine, MOVE), public (→ primes: many people can see/know), marriage (low
mined frequency, 5 notes).

Verified (this design session): none of the 31 slugs collides with the 100
consensus-100 concept slugs or with any kernel-v0 slug.

## Authoring order and per-record briefs

Topological: a record may reference kernel-v0 ids and STRICTLY EARLIER rows only.
"Seed" = molecules-v0 grounding note to formalize (never quote).

| # | slug | label sketch | frame | may reference | seed (molecules-v0) | brief |
|---|---|---|---|---|---|---|
| 1 | money | money | InstanceSchema | give, take | money | things people give/take when one wants something another has; everyone in a place knows all want these things for this |
| 2 | surface | surface (of a thing) | InstanceSchema | part-of | — | the part of a something that other things can touch; can be seen from outside |
| 3 | hot | hot (heat) | WhenTrue | — | fire | when someone touches this something they feel something bad in the body part; being very near fire-like things does the same |
| 4 | material | material (what a thing is made of) | InstanceSchema | make, part-of | water/rock adjacents | the kind of something all parts of a thing are; when someone makes a thing they make it from this |
| 5 | group | group (organized people) | InstanceSchema | — | — | many people; these people think about these same people as one something; they do some things together |
| 6 | fight | fight (X fights Y) | RelationalSchema | — | — | two do bad things to each other's bodies with force; each wants the other to not be able to do more |
| 7 | measure | measure (determined how-much) | RelationalSchema | know | — | someone does something to a something because of this they know how big/how much it is; can say it with words |
| 8 | kill | kill (X kills Y) | RelationalSchema | death (kernel-v0) | — | X does something to Y; because of this a death happens to Y |
| 9 | animal | animal | InstanceSchema | — | animal | a kind of living something; not people; can move itself; can see/hear/feel |
| 10 | eat | eat (X eats Y) | RelationalSchema | — | eat | put a something inside the body through the mouth-part; after this the something is part of the body; living things need to do this to live |
| 11 | food | food | InstanceSchema | eat | food | a kind of something people/animals eat; because of this they can live |
| 12 | grow | grow | WhenTrue | — | — | a living something becomes bigger for some time, not because someone does something to it |
| 13 | name | name (the word for X) | InstanceSchema | — | — | the words people say when they want others to know which someone/something they are thinking about |
| 14 | write | write (X writes Y) | RelationalSchema | make, name | book | make marks on a surface-like something; people who see the marks can know the words |
| 15 | own | own (X owns Y) | RelationalSchema | take, know | — | everyone knows this thing is this someone's; if others take it that is bad/cannot |
| 16 | ill | ill (sick) | WhenTrue | — | — | something bad is happening inside this someone's body; because of this they feel bad and cannot do many things |
| 17 | man | man (adult male) | InstanceSchema | birth | man | grown someone of the kind that cannot bear children (formalize carefully; see honesty note) |
| 18 | woman | woman (adult female) | InstanceSchema | birth | woman | grown someone of the kind that can bear children |
| 19 | sex | sex (mating) | InstanceSchema | man, woman | — | two people do something with their bodies together; because of such doings births can happen |
| 20 | work | work (job) | InstanceSchema | money | — | things someone does for a long time on many days because after this someone gives them money |
| 21 | status | status (standing in a group) | RelationalSchema | group | — | where people in the group think this someone is: like above/below other people, not in a place but in people's thinking |
| 22 | authority | authority (X has authority over Ys) | RelationalSchema | group | — | when X says "do this", the Ys do it because X said it; the group thinks this is right |
| 23 | law | law | InstanceSchema | authority | — | words said by the people with authority over a place: all people in this place must do like these words say; if not, something bad happens to them |
| 24 | country | country | InstanceSchema | authority | — | a very big place; many people live in this place; the same authority is over all of them |
| 25 | institution | institution | InstanceSchema | group, law | — | a group that exists for a long time, not because of one person; does the same kinds of things; law-like words say how |
| 26 | duty | duty | InstanceSchema | work | — | something someone must do because of their work/place-in-group; if they do not do it, that is bad |
| 27 | worth | worth (value of a thing) | RelationalSchema | money, give | money | how much money-like things people will give for this something |
| 28 | tool | tool | InstanceSchema | make | — | a something people make because people can do other things with it that they cannot do with the body alone |
| 29 | machine | machine | InstanceSchema | tool, make | car | a tool-like made something with many parts; when someone does a small something to it, its parts move and it does much |
| 30 | art | art | InstanceSchema | make | picture | things people make because when other people see/hear them, these people feel something (often good); not because people can do other things with them |
| 31 | game | game | InstanceSchema | — | ball | something people do because they feel good when they do it; they do it like words-said-before say; often some want to do it better than others |

Briefs are CONTENT SKETCHES ONLY — the explicator authors real kot-ast/1 under
the full grammar, and the sketch never overrides the scholarly-gloss standard.

## Authoring bar (gates, in order, all fail-closed)

1. `node ../validate-record-ref.mjs lexicon/records/<slug>.json` green (grammar +
   reference resolution against kernel-v0 + earlier bridge records + encode).
2. Gloss meets `concept-def-prompt.md` §1 (genus–differentia, no circularity,
   self-contained); `pattern` names the device; `notes` carries an honest
   `AST adequacy:` flag — **lossy bridge records are admissible** (DESIGN.md
   §3.3.4: the point is factoring residual loss into one audited place).
3. References: kernel-v0 + earlier rows only; ≤8; `references` field equals the
   AST's concept ids (the gate enforces this).
4. Sensitive-content note: `sex`, `kill`, `fight` are dictionary-standard senses
   and must be written to the same detached scholarly register as any other
   record — WordNet-sense-fixed, no examples.
5. Maintainer spot-check of ≥5 records (STIPULATED pick: money, law, status,
   sex, art — the highest-leverage and most-contestable) before any S5
   generation runs.

## `build_manifest.mjs` (to build, ~60 lines)

Reads kernel-v0 manifest + `records/*.json`; verifies every record gates green,
namespace/topology rules, and NO slug/synset collision with
`consensus-100/concepts-100.json` nor the Stage-2 held-out sample; emits
`manifest.json` with per-record sha256, `lexiconSetHash` (sha256 of the sorted
id:hash lines), and the encoder content hash. The LEXICON LISTING block for the
S5 prompt (85 lines of `id — label: first-sentence gloss`) is emitted by the
same script to `listing.txt` so prompt and manifest can never drift apart.
