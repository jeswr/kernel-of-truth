# onto-softtype: the ONT-TYPE-G2/1 imported SOFT-typing layer (mapping doc)

**Build:** `poc/ontology-import-g2/build-softtype.py` (deterministic; date constant 2026-07-12)  
**Plan:** `docs/next/design/ontology-import-plan.md` (maintainer-approved direction, issue #20)  
**Status:** EXPERIMENT-ONLY candidates. Nothing here is endorsed; `binding:false`, `effect:rank-only`, `identity_bearing:false` on every record. SOFT expectations only — never hard laws; never part of any concept hash.

## What this fixes

The g2 readout scored the hand-authored HARD 4-sort scheme (Person/Thing/Place/Time universals) at 33/84 = 0.39 soundness under the directive-#11 proxy protocol: hard universal typing over-constrains ordinary meaning (e.g. “X breaks Y ⇒ X is a person” fails on storms; “Y is a thing, not a person” fails on finding a person). This layer replaces each hard universal with (i) a broad BFO-anchored claim that ordinary meaning does guarantee, plus (ii) explicitly SOFT selectional preferences (“normally…”, SUMO-backed) and (iii) valency expectations (“typically…”, FrameNet-backed). Arms: A1 = BFO anchor only (breadth control), A2 = +SUMO, A3 = +SUMO+FrameNet (intended adoption arm).

## Vacuity rule (operationalised)

A slot is NON-vacuous in an arm iff its BFO anchor is strictly below `entity` OR a source-specific SUMO/FrameNet preference is present in that arm. Vacuous slots score 0 regardless of the judge label (plan §7.3). Counts this build: A1 67/84, A2 83/84, A3 83/84 non-vacuous (R3: 42/42 at A3).

## Per-slot mapping

| slot | concept | rule/form | family | BFO anchor | SUMO evidence | FrameNet evidence (Core FEs) | rank |
|---|---|---|---|---|---|---|---|
| g2:pi:000 | archived | R4/existential | agent-intention-goal | process | Keeping, Putting | Storing (Agent, Theme, Location) | moderate |
| g2:pi:001 | begin | R3/domain | event-action | occurrent | BeginFn, Process | — | strong |
| g2:pi:002 | begin | R3/range | event-action | temporal region | TimePosition, BeginFn | — | strong |
| g2:pi:003 | believe | R3/domain | agent-intention-goal | independent continuant | believes, CognitiveAgent | Becoming_aware (Cognizer, Phenomenon, Means, Topic) | strong |
| g2:pi:004 | believe | R3/range | agent-intention-goal | generically dependent continuant | believes, Formula | Becoming_aware (Cognizer, Phenomenon, Means, Topic) | strong |
| g2:pi:005 | birth | R1/subClassOf | event-action | process | Birth, Process | Being_born (Child) | strong |
| g2:pi:006 | birth | R4/existential | event-action | temporal region | Birth, TimePoint | Event (Place, Time) | strong |
| g2:pi:007 | bookmark | R1/subClassOf | generic-type-vs-kind | generically dependent continuant | ContentBearingObject, Icon | Records (Record) | moderate |
| g2:pi:008 | bookmark | R4/existential | agent-intention-goal | process | IntentionalProcess | Recording (Agent, Phenomenon, Attribute, Value) | moderate |
| g2:pi:009 | bookmark | R4/existential | generic-type-vs-kind | generically dependent continuant | ContentBearingObject | Records (Record) | moderate |
| g2:pi:010 | break | R3/domain | event-action | entity | Damaging, AutonomousAgent | Cause_to_fragment (Agent, Whole_patient, Pieces, Cause) | strong |
| g2:pi:011 | break | R3/range | event-action | material entity | Damaging, Object | Cause_to_fragment (Agent, Whole_patient, Pieces, Cause) | strong |
| g2:pi:012 | break | R4/existential | event-action | temporal region | Damaging, TimePoint | Event (Place, Time) | strong |
| g2:pi:014 | broken | R4/existential | quality-vs-disposition | quality | Damaging, Attribute | Render_nonfunctional (Agent, Artifact, Cause) | moderate |
| g2:pi:015 | cause | R3/domain | event-action | occurrent | causes, Process | Causation (Affected, Actor) | strong |
| g2:pi:016 | cause | R3/range | event-action | occurrent | causes, Process | Causation (Affected, Actor) | strong |
| g2:pi:017 | cause | R4/existential | event-action | temporal region | causes, TimePoint | Event (Place, Time) | strong |
| g2:pi:018 | celebration | R1/subClassOf | event-action | process | SocialInteraction, Ceremony | Social_event (Attendee) | strong |
| g2:pi:020 | celebration | R4/existential | event-action | process | IntentionalProcess, SocialInteraction | Social_event (Attendee) | strong |
| g2:pi:021 | change | R4/existential | event-action | continuant | InternalChange, Object | Undergo_change (Entity, Final_category, Initial_category) | moderate |
| g2:pi:022 | change | R4/existential | event-action | temporal region | InternalChange, TimePoint | Event (Place, Time) | strong |
| g2:pi:023 | condolence | R1/subClassOf | generic-type-vs-kind | generically dependent continuant | LinguisticCommunication | Communication (Communicator, Message, Topic, Medium) | moderate |
| g2:pi:025 | condolence | R4/existential | role-vs-phase | role | LinguisticCommunication, Human | Contacting (Communicator, Addressee, Address, Communication) | moderate |
| g2:pi:026 | condolence | R4/existential | role-vs-phase | role | LinguisticCommunication, Human | Communication (Communicator, Message, Topic, Medium) | moderate |
| g2:pi:027 | conversation | R1/subClassOf | event-action | process | Speaking, SocialInteraction | Discussion (Interlocutor_1, Interlocutor_2, Interlocutors, Topic) | strong |
| g2:pi:028 | conversation | R4/existential | role-vs-phase | role | SocialInteraction, Human | Discussion (Interlocutor_1, Interlocutor_2, Interlocutors, Topic) | strong |
| g2:pi:029 | conversation | R4/existential | role-vs-phase | role | Speaking, Human | Discussion (Interlocutor_1, Interlocutor_2, Interlocutors, Topic) | strong |
| g2:pi:030 | death | R1/subClassOf | event-action | process | Death, Process | Death (Protagonist) | strong |
| g2:pi:031 | death | R4/existential | event-action | material entity | Death, Organism | Death (Protagonist) | strong |
| g2:pi:032 | death | R4/existential | event-action | temporal region | Death, TimePoint | Event (Place, Time) | strong |
| g2:pi:033 | end | R3/domain | event-action | occurrent | EndFn, Process | Process_end (Process) | strong |
| g2:pi:034 | end | R3/range | event-action | temporal region | TimePosition, EndFn | Process_end (Process) | strong |
| g2:pi:035 | event | R4/existential | event-action | temporal region | Process, TimePoint | Event (Place, Time) | strong |
| g2:pi:036 | find | R3/domain | agent-intention-goal | independent continuant | Discovering, CognitiveAgent | Locating (Perceiver, Sought_entity, Location, Ground) | strong |
| g2:pi:037 | find | R3/range | agent-intention-goal | entity | Discovering, Object | Locating (Perceiver, Sought_entity, Location, Ground) | moderate |
| g2:pi:038 | forget | R3/domain | agent-intention-goal | independent continuant | PsychologicalProcess, CognitiveAgent | Memory (Cognizer, Content, Topic) | moderate |
| g2:pi:039 | forget | R3/range | agent-intention-goal | generically dependent continuant | PsychologicalProcess, Proposition | Memory (Cognizer, Content, Topic) | moderate |
| g2:pi:040 | friend | R3/domain | role-vs-phase | material entity | Human, SocialInteraction | Personal_relationship (Partner_1, Partner_2, Partners) | strong |
| g2:pi:041 | friend | R3/range | role-vs-phase | material entity | Human, SocialInteraction | Personal_relationship (Partner_1, Partner_2, Partners) | strong |
| g2:pi:043 | gift | R4/existential | role-vs-phase | role | UnilateralGiving, Human | Giving (Donor, Recipient, Theme) | strong |
| g2:pi:044 | gift | R4/existential | event-action | process | UnilateralGiving | Giving (Donor, Recipient, Theme) | strong |
| g2:pi:045 | give | R3/domain | agent-intention-goal | independent continuant | Giving, AutonomousAgent | Giving (Donor, Recipient, Theme) | strong |
| g2:pi:046 | give | R3/range | agent-intention-goal | entity | Giving, Object | Giving (Donor, Recipient, Theme) | strong |
| g2:pi:047 | give | R4/existential | event-action | temporal region | Giving, TimePoint | Event (Place, Time) | strong |
| g2:pi:050 | grieving | R4/existential | quality-vs-disposition | quality | EmotionalState | — | moderate |
| g2:pi:051 | has-part | R3/domain | generic-type-vs-kind | entity | part, Object | Part_whole (Part, Whole) | moderate |
| g2:pi:052 | has-part | R3/range | generic-type-vs-kind | entity | part, Object | Part_whole (Part, Whole) | moderate |
| g2:pi:053 | help | R3/domain | agent-intention-goal | entity | AutonomousAgent, IntentionalProcess | Assistance (Benefited_party, Helper, Goal, Focal_entity) | strong |
| g2:pi:054 | help | R3/range | agent-intention-goal | entity | Human, AutonomousAgent | Assistance (Benefited_party, Helper, Goal, Focal_entity) | strong |
| g2:pi:056 | inside | R3/domain | generic-type-vs-kind | independent continuant | Inside, Object | Interior_profile_relation (Figure, Ground, Profiled_region) | moderate |
| g2:pi:057 | inside | R3/range | generic-type-vs-kind | independent continuant | Inside, Object | Interior_profile_relation (Figure, Ground, Profiled_region) | moderate |
| g2:pi:058 | kind | R4/existential | generic-type-vs-kind | — (underdetermined) | — | — | underdetermined |
| g2:pi:059 | learn | R3/domain | agent-intention-goal | independent continuant | Learning, CognitiveAgent | Education_teaching (Teacher, Student, Institution, Subject) | strong |
| g2:pi:060 | learn | R3/range | agent-intention-goal | generically dependent continuant | Learning, Proposition | Education_teaching (Teacher, Student, Institution, Subject) | strong |
| g2:pi:062 | lie | R1/subClassOf | generic-type-vs-kind | generically dependent continuant | Stating, LinguisticCommunication | Prevarication (Speaker, Addressee, Topic) | strong |
| g2:pi:063 | lie | R4/existential | role-vs-phase | role | Stating, Human | Prevarication (Speaker, Addressee, Topic) | strong |
| g2:pi:064 | lie | R4/existential | role-vs-phase | role | Stating, Human | Prevarication (Speaker, Addressee, Topic) | strong |
| g2:pi:065 | lose | R3/domain | agent-intention-goal | independent continuant | ChangeOfPossession, Human | Losing (Owner, Possession) | moderate |
| g2:pi:066 | lose | R3/range | agent-intention-goal | entity | ChangeOfPossession, Object | Losing (Owner, Possession) | moderate |
| g2:pi:068 | lost | R4/existential | quality-vs-disposition | quality | ChangeOfPossession, Attribute | Losing_track_of_perceiver (Theme, Perceiver) | moderate |
| g2:pi:069 | make | R3/domain | agent-intention-goal | entity | Making, AutonomousAgent | Creating (Created_entity, Creator) | strong |
| g2:pi:070 | make | R3/range | agent-intention-goal | entity | Making, Artifact | Creating (Created_entity, Creator) | strong |
| g2:pi:071 | make | R4/existential | event-action | temporal region | Making, TimePoint | Event (Place, Time) | strong |
| g2:pi:073 | maker-of | R3/domain | role-vs-phase | entity | Making, Human | Manufacturing (Producer, Product, Factory) | moderate |
| g2:pi:074 | maker-of | R3/range | role-vs-phase | entity | Making, Artifact | Manufacturing (Producer, Product, Factory) | moderate |
| g2:pi:075 | maker-of | R4/existential | event-action | process | Making | Creating (Created_entity, Creator) | strong |
| g2:pi:077 | memory | R4/existential | generic-type-vs-kind | generically dependent continuant | Proposition, StateOfMind | Memory (Cognizer, Content, Topic) | moderate |
| g2:pi:078 | near | R3/domain | generic-type-vs-kind | independent continuant | Near, Object | Gradable_proximity (Ground, Figure) | moderate |
| g2:pi:079 | near | R3/range | generic-type-vs-kind | independent continuant | Near, Object | Gradable_proximity (Ground, Figure) | moderate |
| g2:pi:080 | part-of | R3/domain | generic-type-vs-kind | entity | part, Object | Part_whole (Part, Whole) | moderate |
| g2:pi:081 | part-of | R3/range | generic-type-vs-kind | entity | part, Object | Part_whole (Part, Whole) | moderate |
| g2:pi:082 | promise | R1/subClassOf | generic-type-vs-kind | generically dependent continuant | Committing, Promise | Commitment (Speaker, Addressee, Message, Topic) | strong |
| g2:pi:083 | promise | R4/existential | role-vs-phase | role | Committing, Human | Commitment (Speaker, Addressee, Message, Topic) | strong |
| g2:pi:084 | promise | R4/existential | role-vs-phase | role | Committing, Human | Commitment (Speaker, Addressee, Message, Topic) | strong |
| g2:pi:085 | remember | R3/domain | agent-intention-goal | independent continuant | Remembering, CognitiveAgent | Remembering_information (Cognizer, Mental_content) | strong |
| g2:pi:086 | remember | R3/range | agent-intention-goal | generically dependent continuant | Remembering, Proposition | Remembering_information (Cognizer, Mental_content) | strong |
| g2:pi:089 | reminder | R4/existential | agent-intention-goal | process | IntentionalProcess | Evoking (Cognizer, Phenomenon, Stimulus) | moderate |
| g2:pi:090 | reminder | R4/existential | generic-type-vs-kind | generically dependent continuant | Proposition | Evoking (Cognizer, Phenomenon, Stimulus) | strong |
| g2:pi:092 | repair | R3/domain | agent-intention-goal | entity | Repairing, Human | Rejuvenation (Entity, Agent, Cause) | strong |
| g2:pi:093 | repair | R3/range | agent-intention-goal | material entity | Repairing, Artifact | Rejuvenation (Entity, Agent, Cause) | strong |
| g2:pi:094 | repair | R4/existential | event-action | temporal region | Repairing, TimePoint | Event (Place, Time) | strong |
| g2:pi:095 | take | R3/domain | agent-intention-goal | independent continuant | Getting, AutonomousAgent | Taking (Agent, Theme, Source) | strong |
| g2:pi:096 | take | R3/range | agent-intention-goal | entity | Getting, Object | Taking (Agent, Theme, Source) | strong |
| g2:pi:097 | take | R4/existential | event-action | temporal region | Getting, TimePoint | Event (Place, Time) | strong |

## Forbidden directions (binding)

- ontology label → replacement definition → changed concept meaning/identity: FORBIDDEN (plan §3.1).
- any serialization as operational `rdfs:domain` / `rdfs:range` / `owl:disjointWith` / existential-generating rules over kernel or world entities: FORBIDDEN (plan §3.4); build validator fails closed.
- BFO source-internal disjointness never propagates through a soft bridge to reject a kernel concept or world instance.
- FrameNet FE names are roles, not ontological types; they supply valency evidence only.

## Files

| file | sha256 |
|---|---|
| bfo-anchor.jsonl | a36151f0afc462a654a5cead566fd328a1268c4cc8790af6830904d277cd1616 |
| bridge-candidates.jsonl | 4c8b4d1e7c40baf5c0573603f764e66ba6d6a390ffb1f6bb556e0c1184f0882b |
| conflicts.jsonl | 43f2a2fdc4b3d1cddcafb14895860aeb45e07c651991131f875dc5e2ca06b0fb |
| soft-type-candidates.jsonl | 3a377cfc73b7e8a45c3a08ac98eed0a75d3f2b113928adfc00d5efad95c9fadb |
| source-attribution.json | 53b47e6d8a2b56072dc6ec151b793e86612082eda944bd8d4071da812745b1e3 |
