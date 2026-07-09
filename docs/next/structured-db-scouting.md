# Structured-DB scouting — candidate ingestion sources for the KERNEL + WORLD layers

**Kernel of Truth programme — reconnaissance catalogue.**
Author: Kern (Opus scouting loop). Date: 2026-07-09.

> ## ⚠️ SPECULATIVE / PENDING FABLE SIGN-OFF — this is NOT a decision or a commitment
>
> **This whole document is reconnaissance only.** Opus scouted the landscape and
> catalogued what *exists*; it BUILDS NOTHING and DECIDES NOTHING. **Fable designs and
> signs off any ingestion pipeline.** Nothing here is authorised, prioritised, or
> committed. No source below is "chosen"; the "quick-win" and "priority" labels are
> *scouting estimates of cheapness/value*, not instructions to act. Every field
> (licence, size, format, access) is a **best-effort scout finding that Fable must
> re-verify before any ingest** — several licences are explicitly flagged unknown or
> contested. No GPU/no-spend implication; no registry entry is touched here. An ingest
> becomes real only through the normal rails (Fable design → maintainer sign-off →
> `prereg-freeze` where applicable).

---

## 0. How to read this

**Two layers, kept distinct throughout** (per programme scope):
- **KERNEL / definitional** — *what a thing IS* (canonical, definitional; genus/differentia,
  identity, classification, formal definitions). Marked **`K`**.
- **WORLD / fact** — *uncontroversial facts about instances* (measurements, positions,
  associations, registries of specific entities). Marked **`W`**.
- **`B`** = the source carries both a definitional taxonomy and instance facts.

**Extractor fit** (the programme already has a generic OBO-1.4 extractor + OWL/RDF/SKOS
tooling, so those formats are CHEAP; everything else needs a new parser):
- **`obo`** = ingestible by the existing generic OBO extractor (near-zero cost).
- **`rdf`** = native OWL/RDF/SKOS → existing OWL/RDF tooling (near-zero cost).
- **`new`** = needs a new bespoke extractor → **Fable-design item** (see §5).

**Other column codes:** Lic (licence openness) = `open` / `restr` (restricted) / `?` (unknown,
must verify). C (controversy) = `L`/`M`/`H`. P (scout priority) = `H`/`M`/`L`.

**Dedup:** each unique source is catalogued **once**, under a primary domain; the *Spans*
note lists other domains it also serves. Cross-domain conflicts in the raw scouting
(e.g. an extractor_fit that differs between domains) are reconciled and flagged in *Notes*.

**Counts (approximate hand-tally, verify if load-bearing):** ~385 raw candidate rows across
12 domains → **~318 unique sources** after dedup. Of these, **~90 are existing-extractor
compatible** (obo/rdf) and **~228 would need a new extractor**.

---

## 1. (a) QUICK-WIN SHORTLIST — cheapest for Opus to ingest *once Fable signs off*

Criteria (ALL must hold): **open-licensed** AND **existing-extractor compatible** (`obo`/`rdf`)
AND **low-controversy** AND **high kernel/programme value**. These are the near-zero-cost
targets. *They are still gated on Fable's sign-off — listing here is not a decision.*

### 1.1 KERNEL-definitional quick-wins

| Source | Domain | Kind | Ext | Licence | Why it's a cheap win | Caveat to verify |
|---|---|---|---|---|---|---|
| **ChEBI** | Chemistry | K | obo | CC BY 4.0 | Structure-based chemical-entity ontology; backbone for Rhea/ChEMBL/PubChem | none material |
| **Protein Ontology (PRO/PR)** | Proteins | K | obo | CC BY 4.0 | "What a protein/proteoform/complex IS"; fills gap not in mined set | none material |
| **Cell Ontology (CL)** | Anatomy | K | obo | CC BY 4.0 | Canonical cell types; companion to UBERON | none material |
| **UBERON** | Anatomy | K | obo | CC BY 4.0 | Cross-species anatomy backbone; ties species anatomies together | large |
| **Sequence Ontology (SO)** | Genetics | K | obo | CC BY 4.0 | Definitional genomics vocabulary (gene/exon/variant types) | none material |
| **HPO** | Diseases | K | obo | open (attrib.) | Human phenotype terms; central to gene–phenotype–disease linkage | verify exact licence text |
| **Mondo** | Diseases | K | obo | CC BY 4.0 | Harmonised disease identities (merges OMIM/Orphanet/DO/NCIt/ICD) | none material |
| **DOID** | Diseases | K | obo | CC0 | Cleanest-licensed disease ontology; feeds MONDO | one scout flagged M-controversy at nosology margins; largely absorbed by MONDO |
| **OGMS** | Diseases | K | obo | CC0 | Formal upper defn of "disease" itself; BFO-aligned like mined set | tiny (~200 terms) |
| **EFO** | Diseases | K | rdf | Apache-2.0 | Integration layer aligning MONDO/HPO/UBERON/CHEBI | none material |
| **NCI Thesaurus (NCIt)** | Diseases | B | rdf | CC BY 4.0 | Real textual definitions per concept; also has OBO edition (dual-fit) | none material |
| **ORDO (Orphanet)** | Diseases | K | rdf | CC BY 4.0 | Rare-disease long tail; cross-linked OMIM/MONDO/HGNC/UniProt | none material |
| **MeSH** | Diseases | B | rdf | CC0 | RDF-native NLM vocab (disease/chemical/anatomy); under-used as RDF | none material |
| **NDF-RT / MED-RT** | Drugs | K | rdf | public domain | DL terminology of drug MoA/physiologic-effect/class — very "kernel" | OWL via BioPortal (inferred edition) |
| **UAT** | Astronomy | K | rdf | CC BY-SA 4.0 | Off-the-shelf SKOS astronomy concept graph (~2.4k concepts) | none material |
| **IVOA Object-Type Ontology** | Astronomy | K | rdf | open (IVOA) | OWL-DL taxonomy of celestial object classes | status = IVOA Note, not REC |
| **OGC GeoSPARQL ontology** | Geography | K | rdf | open (OGC) | Upper defn of Feature/Geometry/spatial relations (geo's "BFO seam") | small |
| **Getty TGN** | Geography | B | rdf | ODC-By 1.0 | Place-TYPE hierarchy (kernel) + gazetteer (world) | attribution licence |
| **Getty AAT** | General | K | rdf | ODC-By 1.0 | SKOS thesaurus of art/material-culture concepts (genus/differentia) | attribution licence |
| **LCSH** | General | K | rdf | public domain | ~400k general subject concepts, SKOS, PD; broadest library vocab | none material |
| **CCO (Common Core Ontologies)** | General | K | rdf | BSD-3 | Mid-level agent/event/artifact/info concepts on BFO — extends mined set | none material |
| **CILI** | Language | K | rdf | CC0/CC BY | Language-independent concept-identity backbone for all wordnets | NSM-adjacent, small |
| **schema.org** | General | K | rdf | CC BY-SA 3.0 | Small, ubiquitous general type hierarchy (Person/Place/Event/…) | share-alike |
| **ISIC (via FAO Caliper)** | Standards | K | rdf | UN open | Global economic-activity classification; SKOS/RDF hub | Caliper also bundles CPC/SITC/BEC/COICOP/COFOG |
| **ISCO-08 / ESCO** | Standards | K | rdf | CC BY 4.0 | ~3k occupations + ~13.9k skills, already SKOS/RDF | none material |
| **CPC (patent classification)** | Standards | K | rdf | open gov | ~260k technology-domain symbols, published as Linked Open Data | none material |
| **FIBO** | Finance | K | rdf | MIT | Purpose-built OWL finance ontology (securities/loans/derivatives/…) | none material |
| **GLEIF ISO 20275 ELF** | Finance | K | rdf | CC0 | Legal-entity-FORM code list, small, CC0, RDF (LEI register is the world layer) | none material |
| **FMA** | Anatomy | K | rdf | custom open | Granular human-anatomy reference ontology | OBO PURL is a PARTIAL subset; full FMA is separate UW distribution/licence — verify |
| **NCBITaxon** | Anatomy | B | obo | CC0 | OBO/OWL rendering of NCBI Taxonomy — organism-identity backbone | very large → chunk/filter ingest |

### 1.2 WORLD-layer (and both-layer) quick-wins

| Source | Domain | Kind | Ext | Licence | Why it's a cheap win | Caveat to verify |
|---|---|---|---|---|---|---|
| **UniProt** | Proteins | B | rdf | CC BY 4.0 | Gold-standard protein identity/function; native RDF + SPARQL | TrEMBL huge/automated — prefer Swiss-Prot for kernel |
| **Reactome** | Proteins | B | rdf | CC0 (verify release) | Curated pathways/reactions; BioPAX = OWL | confirm current release licence |
| **Rhea** | Proteins | B | rdf | CC BY 4.0 | RDF-native curated biochemical reactions; built on ChEBI | none material |
| **PubChem** | Chemistry | B | rdf | public domain | Largest open chemical-identity repo; native PubChemRDF | massive → want a subset |
| **GeoNames** | Geography | B | rdf | CC BY 4.0 | Global gazetteer + feature-type taxonomy; maintained OWL ontology | none material |
| **KnowWhereGraph** | Geography | B | rdf | CC BY 4.0 | ~29B-triple geo KG (ontology + 30+ environmental/demographic layers) | very large |
| **Wikidata** | General | B | rdf | CC0 | Largest open general KG; P31/P279 taxonomy + per-entity facts | crowd-edited → needs vandalism/quality filtering (M-controversy per some scouts) |
| **DBpedia** | General | B | rdf | CC BY-SA 3.0 | Cleaner ontology layer + LOD hub over Wikipedia | Wikipedia-derived quality varies; slower cadence |
| **YAGO 4.5** | General | B | rdf | CC BY-SA 3.0 | Wikidata facts + schema.org taxonomy, engineered for logical cleanliness | smaller coverage than Wikidata |
| **DBnary** | Language | B | rdf | CC BY-SA 3.0 | Wiktionary as native OntoLex-Lemon RDF (26 editions) | **overlaps already-mined Wiktionary** — dedup/replace decision for Fable |

> **Not on the shortlist because they are already ingested:** **QUDT** (units — already mined),
> **Plant Ontology / PO** (already in the mined BFO/RO/GO/PATO/PO set). **WordNet, FrameNet,
> SUMO, Metamath, Wiktionary** are already mined — CILI/OMW/OEWN, SemLink, and DBnary/Kaikki
> below are *extensions or cleaner re-ingestion paths* for those, i.e. dedup/replace calls
> for Fable, not fresh sources.

### 1.3 Promising but NOT clean quick-wins — cross-domain conflicts to resolve first

These scored high but have a **conflict or ambiguity** across the domain scouts, so they are
deliberately kept OFF the clean shortlist until Fable resolves them:

- **ChEMBL** — extractor conflict: Proteins/Drugs scouts said `rdf`; Chemistry scout said the
  EBI RDF platform is **discontinued/unsupported** → `new` (SQL/SDF). Treat as needs-new until confirmed.
- **InterPro** — extractor conflict: Genetics scout `rdf`; Proteins scout `new` (primary dist. is
  XML/TSV). Pfam subset is CC0. Confirm whether an RDF slice is usable before treating as cheap.
- **IUPHAR/BPS GtoPdb** — extractor conflict (`rdf` in Proteins vs `new` in Drugs/Chemistry) and
  only medium scout-priority; open (ODbL + CC BY-SA).
- **ATC (WHO)** — licence conflict: Drugs scout `open`+`rdf`(via BioPortal); Diseases scout
  `?`+`new`. WHO/WHOCC redistribution terms need direct confirmation.

---

## 2. Already-mined / overlap map (avoid duplicate ingest)

| Already mined | Cheaper/cleaner or extension source found | Action for Fable |
|---|---|---|
| OBO set (BFO/RO/GO/PATO/**PO=Plant Ontology**) | CL, UBERON, PRO, SO, CARO, HPO, Mondo, DOID, OGMS, CHEBI, NCBITaxon (all obo) | complement, don't re-ingest PO |
| QUDT (units) | OM, UCUM, CODATA constants | QUDT already in; others are cross-checks |
| WordNet (EN) | Open English WordNet (cleaner CC BY), OMW (multilingual), CILI (interlingual index) | dedup/replace decision |
| Wiktionary | DBnary (RDF, 26 langs), Kaikki/wiktextract (JSONL, all langs) | cheaper re-ingestion path |
| FrameNet | SemLink (maps FrameNet↔VerbNet↔PropBank↔WordNet) | alignment layer |
| SUMO, Metamath | — (Mathlib/OEIS/ProofWiki are adjacent math sources) | complementary |

---

## 3. (b) FULL CATALOGUE by domain (deduped; all fields)

Legend recap: Kind `K/W/B` · Ext `obo/rdf/new` · Lic `open/restr/?` · C `L/M/H` · P `H/M/L`.

### 3.1 Genetics & genomics

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| HGNC | K | Approved human gene symbols/names/IDs, gene families | TSV/JSON (some RDF via BioPortal) | open | ~44.4k symbols (~19.25k protein-coding) | genenames.org GCS bucket | new | L | H | Pure naming authority; tiny, high-value gene-identity ground truth |
| NCBI Gene (Entrez) | B | Gene records all organisms: identity/location/function/xrefs | flat/ASN.1/XML/E-utils | ? | millions | FTP gene/DATA; E-utils | new | L | H/M | **Licence mixed (CC BY-NC vs US-govt PD) — re-verify** |
| Ensembl | B | Genome assemblies + gene/transcript/exon annotation | GTF/GFF3/FASTA/MySQL/REST | open | 4100+ animal genomes | ensembl.org FTP | new | L | H/M | Structural gene defns across tree of life |
| GENCODE | K | Canonical human/mouse transcript/gene models | GTF/GFF3 | open | ~20k PC + ~18k lncRNA (human) | gencodegenes.org | new | L | H | De-facto ground-truth gene models; confirm exact wording |
| RefSeq | B | Curated non-redundant reference sequences per gene | GenBank/FASTA/GFF | ? | millions | NCBI FTP | new | L | H/M | Mixed licence signals (ODbL cited vs US-govt PD) — verify |
| ClinVar | W | Variant→disease clinical-significance assertions | VCF/XML/TSV | open | >3M variants | NCBI FTP | new | M | H/M | Significance calls shift over time / vary by submitter |
| gnomAD | W | Population allele frequencies (measured) | VCF/Hail | open (CC0) | v4: 730k exomes + 76k genomes; 241M variants | broad/GCS/AWS | new | L | H | Cleanest objective genomics fact source; CC0, huge |
| OMIM | B | Genes + Mendelian disorders, gene–disease links | flat/API | restr | ~17k+ entries | omim.org (key) | new | L | M | **Restrictive licence; weekly-refresh obligation** |
| dbSNP | W | Short-variant catalogue (existence/position) | VCF | open | 100Ms of rsIDs | NCBI FTP | new | L | M | Superseded by gnomAD for freqs; still canonical rsID registry |
| 1000 Genomes / IGSR | W | Global human variation (phased genotypes) | VCF | open | 2504+ individuals | IGSR FTP/Globus | new | L | M | Foundational panel; superseded in scale by gnomAD |
| MGI | B | Mouse gene/genome/phenotype/disease-model | GFF/TSV | open | ~57k features | informatics.jax.org FTP | new | L | M | Folding into Alliance of Genome Resources |
| Alliance of Genome Resources | B | Integrated model-organism gene/disease/orthology | TSV/JSON/VCF | open (CC0) | millions, 6+ organisms | alliancegenome.org; AWS | new | L | H | Best single entry point; consolidates Fly/Worm/ZFIN/SGD/RGD/MGI |
| FlyBase | B | Drosophila gene/genome | GFF/FASTA/TSV/SQL | open | ~17.8k genes | flybase.org | new | L | L | Redundant w/ Alliance |
| WormBase | B | C. elegans gene/genome | GFF/FASTA/TSV | open | ~20k genes | wormbase.org | new | L | L | Redundant w/ Alliance |
| ZFIN | B | Zebrafish gene/genome/phenotype | TSV/JSON | open | ~26k genes | zfin.org | new | L | L | Redundant w/ Alliance |
| SGD | B | Budding-yeast functional annotation | TSV/GFF/FASTA | open | ~6.6k genes | yeastgenome.org | new | L | L | Compact "complete parts list" if fine-grained wanted |
| RGD | B | Rat gene/QTL/disease | OBO/OWL/JSON/TSV | open | 10Ks records | rgd.mcw.edu | new | L | L | Niche vs Alliance |
| TAIR | B | Arabidopsis gene/genome | GFF/FASTA/TSV | ? | ~27k genes | arabidopsis.org | new | L | L | **Historically subscription for bulk — verify** |
| PomBase | B | Fission-yeast gene/genome | GFF/FASTA/TSV | open | ~5.1k genes | pombase.org | new | L | L | Niche, small |
| GENO | K | Genotype/allele/zygosity structure | OWL2 (OBO) | ? | 100s terms | monarch GitHub | obo | L | M | Fills "what is a genotype" gap; verify CC BY |
| VariO | K | Effects/mechanisms of sequence variation | OWL/RDF-XML | ? | 100s terms | variationontology.org | rdf | L | L | Narrower than SO/GENO; verify licence |
| ClinGen | W | Evidence-graded gene–disease validity/dosage | CSV/BED/TSV/API | ? | 1000s pairs | clinicalgenome.org | new | M | M | Classifications explicitly revisable; verify licence |
| GWAS Catalog | W | Published variant–trait associations | TSV/REST | ? | 45k+ studies | ebi.ac.uk/gwas | new | M | M | Statistical/replication-prone; "documented claim" layer |
| PharmGKB | B | Gene–drug–variant pharmacogenomics | TSV/zip | restr | 1000s annotations | pharmgkb.org (acct) | new | L | L | **Research-use-only, no redistribution** |
| PharmVar | K | Star-allele nomenclature for pharmacogenes | web/files | ? | 15 genes, 100s alleles | pharmvar.org | new | L | L | Precisely definitional but tiny; licence unverified |
| CIViC | W | Expert cancer-variant clinical interpretation | TSV/REST | open (CC0) | 1000s interps | civicdb.org | new | M | M | CC0 but interpretive/evolving |
| DisGeNET | W | Gene–disease associations (curated+mined) | SQLite/TSV/RDF | ? | 100Ks assoc | disgenet.com | rdf | M | M | **Partly commercialised — re-verify licence**; also under Diseases |
| GTEx | W | Tissue expression + eQTLs | TSV/VCF | restr | 54 tissues, 900+ donors | gtexportal.org | new | L | L | NC + partial controlled-access |
| COSMIC | W | Somatic mutations in cancer | VCF/TSV | restr | >38M mutations | sanger COSMIC (reg) | new | L | L | **Commercial licence required** |
| Human Protein Atlas | W | Tissue/cell/subcellular protein expression | TSV/XML/REST | open | ~20k genes | proteinatlas.org | new | L/M | L | Expression facts, not identity; also under Proteins |
| MedGen | K | Medical-genetics concept normalisation map | XML/TSV | ? | large (aggregates) | ncbi.nlm.nih.gov/medgen | new | L | L | **UMLS-entangled licence** — prefer Mondo/HPO/Orphanet directly |
| GeneCards | K | Aggregated human-gene compendium | web/API (proprietary) | restr | ~20k genes | genecards.org | new | L | L | **⚠ ToU EXPLICITLY PROHIBITS AI-training use** — do NOT ingest; use its primary sources |
| HGVS Nomenclature | K | Grammar for naming DNA/RNA/protein variants | web spec | open (CC0) | small (a spec) | hgvs-nomenclature.org | new | L | L | Naming grammar, not an entity DB; bespoke prose extraction |

Cross-referenced (catalogued elsewhere): **UniProt, Reactome** (Proteins); **ChEBI, PubChem**
(Chemistry); **DrugBank, KEGG, IUPHAR** (Drugs/Chemistry); **NCBI Taxonomy** (Anatomy);
**HPO, Mondo, ORDO, SNOMED CT, UMLS** (Diseases). Genetics-native OBO/RDF quick-wins: **SO**.

### 3.2 Proteins & molecular biology

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| UniProt | B | Protein sequence/identity/function | flat/XML/FASTA/RDF/SPARQL | open (CC BY 4.0) | ~575k Swiss-Prot + >300M TrEMBL | uniprot.org; SPARQL | rdf | L | H | **Quick-win.** Swiss-Prot = gold kernel; TrEMBL lower-confidence |
| ChEBI | K | Chemical-entity ontology | OBO/OWL/SDF/SQL | open (CC BY 4.0) | ~200k (~60k curated) | EBI FTP; OBO | obo | L | H | **Quick-win** (home: Chemistry). Backbone for Rhea/ChEMBL |
| Protein Ontology (PRO) | K | Protein classes/proteoforms/complexes | OBO/OWL | open (CC BY 4.0) | 10Ks classes | OBO/proconsortium | obo | L | H | **Quick-win** — not in mined set; fills protein-identity gap |
| Cell Ontology (CL) | K | Natural cell types | OBO/OWL/JSON | open (CC BY 4.0) | ~2.7k classes | obophenotype GitHub | obo | L | H | **Quick-win** (home: Anatomy) |
| Rhea | B | Curated biochemical reactions | RDF/OWL/SPARQL/flat | open (CC BY 4.0) | ~15k+ reactions | rhea-db.org; SPARQL | rdf | L | H | **Quick-win.** RDF-native, built on ChEBI |
| Reactome | B | Pathways/reactions/complexes | BioPAX(OWL)/SBML/Neo4j | open (CC0*) | ~2.6k human pathways | reactome.org | rdf | L | H | **Quick-win.** BioPAX = OWL; confirm current release licence |
| PubChem | B | Chemical compound/substance identity | SDF/JSON/RDF/REST | open (PD) | >110M compounds | FTP; PubChemRDF | rdf | L | H | **Quick-win** (home: Chemistry). Massive → subset |
| ChEMBL | B | Bioactive molecules + bioactivity | SQL/SDF/FASTA/(RDF?) | open (CC BY-SA 3.0) | ~2.4M compounds | EBI FTP | new* | L | H | **Extractor CONFLICT**: RDF platform discontinued per Chemistry scout → treat `new` |
| Disease Ontology (DOID) | K | Human disease classification | OBO/OWL/JSON | open (CC0) | >11k terms | disease-ontology.org | obo | M | H | **Quick-win (caveated).** CC0; marginal nosology disputes; feeds MONDO |
| Enzyme Nomenclature (ENZYME/IntEnz) | K | EC-numbered enzyme activities | flat/SQL/XML | open (CC BY) | ~5–8k EC entries | ExPASy/EBI FTP | new | L | H | Small authoritative taxonomy under BRENDA/Rhea/CAZy/MEROPS |
| UniPathway | K | Metabolic-pathway hierarchy | OBO | open (CC BY 4.0) | ~1.2k pathways | ExPASy/UniProt FTP | obo | L | M | Clean OBO complement to Rhea/Reactome |
| InterPro | K | Protein family/domain/site classification | XML/TSV/GFF3/(RDF) | open (PD) | >85k entries | ebi.ac.uk/interpro | new* | L | H | **Extractor CONFLICT** (Genetics scout said `rdf`); primary dist. XML/TSV |
| Pfam | K | Family/domain via MSAs + profile HMMs | Stockholm/HMM | open (CC0) | ~20k families | EBI FTP | new | L | M | Custom bioinformatics formats; now in InterPro cycle |
| PROSITE | K | Domain/family patterns/profiles + ProRule | PROSITE flat | restr | ~2k docs | ExPASy FTP | new | L | M | **Free academic, paid commercial** |
| CATH | K | Structural classification of protein folds | flat | open (CC BY 4.0) | >235k domains | cathdb.info | new | L | M | Objective structural taxonomy |
| SCOP / SCOPe | K | Structural/evolutionary domain classification | flat | ? | ~41k domains | scop.berkeley.edu | new | L | L | Overlaps CATH; verify licence |
| RCSB PDB / wwPDB | W | Experimental 3D structures (instances) | PDB/mmCIF/XML | open (CC0) | ~230k structures | RCSB/FTP/Globus | new | L | M | Instance records, not category defns |
| AlphaFold DB | W | Predicted 3D structures | mmCIF/PDB + pLDDT | open (CC BY 4.0) | >200M predictions | alphafold.ebi.ac.uk | new | M | L | **Model output, not verified fact** |
| STRING | W | Protein–protein association network | TSV/API | open (CC BY 4.0) | >2B associations | string-db.org | new | M | M | Includes text-mined/predicted → threshold-filter |
| IntAct | W | Curated molecular interactions | PSI-MI/MITAB/RDF/BioPAX | open | ~1M+ interactions | ebi.ac.uk/intact | rdf | L | M | Native RDF/BioPAX; curated (lower controversy than STRING) |
| BioGRID | W | Curated protein/genetic/chemical interactions | tab/PSI-MI XML | open (MIT) | ~3M interactions | thebiogrid.org | new | L | M | Unusually permissive (MIT) |
| WikiPathways | B | Community pathway models | GPML/RDF | open (CC0) | ~3k pathways | wikipathways.org | new | M | L | Community-curated; RDF export could shift to `rdf` |
| BRENDA | B | Enzyme function/kinetics | flat; BTO in OBO | restr | ~8k EC enzymes | brenda-enzymes.org | new | L | M | **Academic free / commercial paid**; embedded BTO is OBO |
| MEROPS | K | Peptidase clans/families | web/flat | restr | >4.6k peptidases | ebi.ac.uk/merops | new | L | M | **CC BY-NC** |
| CAZy | K | Carbohydrate-active-enzyme families | HTML/flat | open (CC BY) | 100s families | cazy.org | new | L | M | Niche, cleanly definitional |
| TCDB | K | Membrane-transporter classification | web/flat | open (CC BY-SA + GFDL) | ~1.5k families | tcdb.org | new | L | L | Smaller; less mature bulk infra |
| GOA (GO Annotation) | W | Gene-product→GO evidence facts | GAF/GPAD/GPI | open (CC BY 4.0) | 100Ms records | EBI FTP | new | L | M | Complements mined GO with the evidence facts |
| PANTHER | B | Protein family/subfamily + function | HMM/flat | restr | >12k families | pantherdb.org | new | L | L | **CC BY-NC**; InterPro member |
| eggNOG | W | Orthologous groups + function | FASTA/tab/Newick | open (CC BY) | 3.18M OGs | eggnogdb.org | new | L | L | Orthology facts, not defns |
| Rfam | K | Non-coding-RNA families | Stockholm/CM | open (CC0) | >4k families | EBI FTP | new | L | L | Xfam RNA sibling of Pfam |

Cross-referenced elsewhere: **Human Protein Atlas** (Genetics table above); **NCBI Gene, RefSeq,
Ensembl, ClinVar, OMIM** (Genetics); **NCBI Taxonomy** (Anatomy); **DrugBank, KEGG, IUPHAR**
(Drugs); **HMDB** (Chemistry).

### 3.3 Chemistry & compounds

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| ChEBI | K | see §3.2 | OBO/OWL | open | ~200k | EBI FTP | obo | L | H | **Quick-win** (home domain) |
| PubChem | B | see §3.2 | SDF/RDF/REST | open (PD) | >110M | FTP; PubChemRDF | rdf | L | H | **Quick-win** (home domain) |
| Rhea | B | see §3.2 | RDF/OWL | open | 10Ks | EBI FTP; SPARQL | rdf | L | H | **Quick-win** (home: Proteins) |
| CAS Common Chemistry | K | Curated CAS-Registry subset | REST/SDF | restr | ~500k | commonchemistry.cas.org | new | L | M | **CC BY-NC**; redundant w/ PubChem/ChEBI |
| CAS Registry / SciFinder | K | Authoritative substance registry (CAS RN) | proprietary | restr | >200M | subscription only | new | L | L | **Fully paywalled** — high-value-but-inaccessible |
| ChemSpider | K | Aggregated structures (~270 sources) | web/limited API | restr | ~130M | chemspider.com | new | L | L | No bulk; mostly redundant aggregation |
| InChI / InChIKey | K | Canonical structure-identity standard | C software + strings | open (IUPAC-InChI) | N/A (algorithm) | github.com/IUPAC-InChI | new | L | M | Normalisation infra, not a corpus |
| NIST Chemistry WebBook | W | Thermochemical/spectral reference data | web (HTML) | ?/restr | ~100k species | webbook.nist.gov | new | L | M | Web-only, reuse rights ambiguous; also under Physics |
| PDB Chemical Component Dict (CCD) | K | Canonical defns of ligands/residues in PDB | mmCIF/PDBML | open (PD/CC0-equiv) | ~18.5k defns | wwPDB FTP | new | L | H | Clean rigorous open dictionary; mmCIF parser |
| UniChem | W | InChI-based xref across ~40 chem DBs | REST/RDF/SPARQL/TSV | open (CC BY) | 200M+ xrefs | EBI FTP/SPARQL | rdf | L | M | De-dup/identity-equivalence infra |
| EPA CompTox / DSSTox | B | Substances + tox/exposure/property data | CSV/SDF | open (PD) | ~1.2M | comptox.epa.gov | new | L | H | Large PD registry + tox world-facts |
| FDA GSRS / UNII | K | ISO-11238 canonical substance-identity (UNII) | flat/REST | open (PD) | ~116k (public) | precisionFDA; GSRS API | new | L | H | Gov-authored ISO-standard identity registry; also under Drugs |
| LOTUS | W | Natural-product structure–organism pairs | RDF (Wikidata)/CSV/SDF | open (CC0) | ~750k pairs | Wikidata SPARQL | rdf | L | M | Occurrence facts; RDF-native |
| COCONUT | K | Aggregated natural-product structures | SDF/CSV/DB | open (CC0 data) | ~400k–730k | coconut.naturalproducts.net | new | L | M | Check per-entry source provenance |
| IUPAC Gold Book | K | Committee-ratified chemistry terminology | web (HTML/XML) | open (CC BY-SA) | ~7k terms | goldbook.iupac.org | new | L | H | Highest-purity chemistry glossary; bespoke HTML extractor |
| MetaCyc / BioCyc | B | Pathways/reactions/enzymes/compounds | BioCyc flat | restr | MetaCyc ~2.5k pathways | biocyc.org | new | L | L | **Bulk access paywalled ($5k+/yr)** |
| RxNorm | K | Normalised clinical-drug names/codes | RRF/REST | open* | ~100k+ | NLM (UMLS acct) | new | L | H | Full release UMLS-gated; PD content; also under Drugs |
| WHO ATC/DDD | K | Drug classification by organ/therapeutic/chem | flat; OWL via BioPortal | open/? | ~6k codes | atcddd.fhi.no; BioPortal | rdf/new | L | H/M | **Licence conflict across scouts — verify WHO terms** |
| GHS | K | Chemical-hazard classification criteria | UN PDF | restr | ~22 hazard classes | unece.org | new | M | L | Unstructured legal PDF; reuse restricted |
| KEGG (COMPOUND/DRUG/…) | B | Pathway-linked compounds/genes/drugs | KEGG flat/KGML | restr | ~19k compounds | rest.kegg.jp (limited) | new | L | L | **Bulk/commercial paywalled** — Reactome/Rhea/MetaCyc are open substitutes |
| DrugBank | B | see §3.4 | XML/CSV/SDF | restr | ~11.9k | go.drugbank.com | new | L | M | **Full set NC + gated; only CC0 Open Data subset free** |
| HMDB | B | Human metabolites + drug metabolites | XML/SDF | restr | ~220k | hmdb.ca | new | L | M | **CC BY-NC**; also under Drugs |
| Wikidata (chem subset) | B | Compound identity + xrefs | RDF/SPARQL | open (CC0) | 100Ks items | WDQS | rdf | M | M | Crowd-edited; cross-linking/lay-name layer |

### 3.4 Drugs & pharmacology

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| MeSH (Chem & Drugs, PA, SCR) | B | Drug/chemical descriptors + pharmacologic actions | XML/RDF-OWL | open (PD) | ~30k D-desc + ~250k SCR | id.nlm.nih.gov/mesh | rdf | L | H | **Quick-win.** Full RDF distribution; also under Diseases |
| NDF-RT / MED-RT | K | Drug MoA/physiologic-effect/chem-class DL terminology | VA/NCI files; OWL via BioPortal | open (PD) | 10Ks concepts | NCI EVS; BioPortal | rdf | L | H | **Quick-win.** Arguably most "kernel" pharma source |
| ATC (WHO) | K | Drug classification hierarchy | flat; OWL via BioPortal | open | ~6k codes | atcddd.fhi.no; BioPortal | rdf | L | H | Small stable gold-standard; **verify WHO redistribution (Diseases scout flagged `?`)** |
| DrugCentral | B | Active ingredients: indication/MoA/class/status | PostgreSQL/SMILES | open (CC BY-SA 4.0) | ~4.7k APIs | drugcentral.org | new | L | H | Best "no-friction" open drug compendium (no account wall) |
| IUPHAR/BPS GtoPdb | B | Drug targets + ligands, MoA, quantitative data | CSV/(RDF) | open (ODbL + CC BY-SA) | ~3.1k targets, ~13.3k ligands | guidetopharmacology.org | new* | L | H/M | **Extractor conflict** (`rdf` in Proteins vs `new` here); expert-curated |
| DrugBank | B | Drug chemistry/pharmacology/targets/interactions | XML/CSV/SDF | restr | ~11.9k | go.drugbank.com | new | L | M | **Full set CC BY-NC + manual gate; CC0 Open Data subset is frictionless** |
| RxNorm | K | Normalised clinical-drug identity (RxCUI) | RRF/REST | open* | ~100k+ | NLM | new | L | H | Full release UMLS-account gated (free); prescribable subset ungated |
| WHO INN | K | Official non-proprietary substance names | PDF lists | open (PD names) | ~12.1k INNs | who.int/inn | new | L | M | PDF-only → scrape, or take from RxNorm/DrugBank fields |
| DailyMed (FDA SPL) | B | Official FDA product labelling | HL7 SPL XML | open (PD) | ~150k labels | dailymed.nlm.nih.gov | new | L | M | Bespoke SPL schema; kernel content redundant w/ cheaper sources |
| FDA NDC Directory | K | Product/package identifiers | JSON/CSV (openFDA) | open (PD) | ~100k listings | open.fda.gov | new | L | M | Cleanest FDA source to build an extractor for |
| FDA Orange Book | W | Approved products + TE codes + patents | delimited/Excel | open (PD) | ~30k products | fda.gov | new | M | L | **Patent-listing portion has real FTC-challenged controversy** |
| Drugs@FDA | W | Drug approval history | tab-delimited | open (PD) | 10Ks records | fda.gov | new | L | L | Pure regulatory-history facts |
| FDA UNII / GSRS | K | see §3.3 | flat/JSON | open (PD) | ~900k substances | precisionFDA; GSRS | new | L | M | Good identity complement for excipients/biologics |
| PharmGKB | W | Gene–drug–outcome associations | TSV/zip | restr | 100k+ annotations | pharmgkb.org | new | L | L | **No-redistribution licence** — blocker |
| SIDER | W | Drug→ADR associations from inserts | TSV | ? | 140k pairs | sideeffects.embl.de | new | L | L | Stale (~2015); depends on restricted MedDRA |
| CTD | W | Chemical–gene–disease interaction networks | CSV/TSV | restr | ~17k chemicals | ctdbase.org | new | L | L | **CC BY-NC**; also under Diseases |
| BindingDB | W | Measured binding affinities | SDF/TSV/MySQL | open (CC BY/BY-SA 3.0) | 2.9M measurements | bindingdb.org | new | L | L | Overlaps ChEMBL |
| DGIdb | W | Drug–gene interaction claims (~30 sources) | TSV/API | ? | 10Ks claims | dgidb.org | new | L | L | Per-source licence fragmentation |
| DDInter | W | Drug–drug interactions | CSV/web | ? | 10Ks pairs | ddinter.scbdd.com | new | L | L | "Open-access" but licence vague — confirm |
| HMDB | B | see §3.3 | XML/SDF | restr | ~220k | hmdb.ca | new | L | L | **CC BY-NC** |
| OHDSI Athena / OMOP | B | Cross-mapped standard vocabularies | CSV (OMOP) | restr | 10M+ concepts | athena.ohdsi.org | new | L | L | License-gated components; redundant w/ RxNorm/ATC/MeSH |
| WHO EML | W | Essential-medicines list (normative selection) | PDF/DOCX | open | 523 meds | who.int | new | M | L | Selection is a policy/value judgement; PDF-only |
| EMA Medicines DB | W | EU authorised medicines (status/substance/indication) | JSON/Excel | open (EU) | 10Ks records | ema.europa.eu | new | L | L | EU regulatory facts |
| KEGG DRUG | B | see §3.3 (KEGG) | KEGG flat | restr | ~12k D-numbers | rest.kegg.jp | new | L | M | **Bulk paywalled** |
| MedDRA | K | Adverse-event/regulatory terminology | ASCII | restr | ~90k+ terms | meddra.org (subscription) | new | L | L | **Fee-gated**; hidden dependency of SIDER/FAERS |
| SNOMED CT (drug model) | K | Clinical-drug ontology | RF2/OWL | restr | subset of ~350k | UMLS/IHTSDO | new | L | L | **Restricted** (see §6) |
| UMLS Metathesaurus | B | Cross-vocabulary hub | RRF | restr | ~4.5M concepts | UTS acct | new | L | L | **Restricted**; free parts better obtained direct |

### 3.5 Diseases, phenotypes & clinical

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| MONDO | K | Unified disease classes | OWL/OBO/JSON | open (CC BY 4.0) | ~25k+ | monarch GitHub | obo | L | H | **Quick-win.** Best single disease backbone |
| HPO | K | Human phenotypic-abnormality vocabulary | OBO/OWL/JSON | open (attrib.) | >18k terms; 156k annots | purl.obolibrary.org/obo/hp | obo | L | H | **Quick-win.** Annotation files = world-fact layer |
| DOID | K | see §3.2 | OBO/OWL | open (CC0) | >11k | disease-ontology.org | obo | L(/M) | H | **Quick-win (caveated).** Diseases scout says L; Proteins scout M |
| ORDO (Orphanet) | K | Rare-disease identities/classification | OWL/RDF | open (CC BY 4.0) | ~9k concepts | orphadata.com/ordo | rdf | L | H | **Quick-win.** Rare-disease long tail |
| NCI Thesaurus (NCIt) | B | Cancer/biomed reference terminology w/ real defns | OWL + OBO edition + flat | open (CC BY 4.0) | ~192k concepts | evs.nci.nih.gov | rdf | L | H | **Quick-win.** Dual OWL/OBO fit |
| MeSH | B | see §3.4 | XML/RDF | open (CC0) | ~30k + ~300k SCR | id.nlm.nih.gov/mesh | rdf | L | H | **Quick-win** (home: Drugs) |
| EFO | K | Cross-cutting biomed variables; imports MONDO/HPO/UBERON/CHEBI | OWL/OBO | open (Apache-2.0) | ~30k+ classes | EBISPOT/efo GitHub | rdf | L | H | **Quick-win.** Unusually permissive |
| OGMS | K | Formal upper theory of disease/diagnosis (BFO-based) | OBO/OWL | open (CC0) | ~200 terms | OGMS GitHub | obo | L | H | **Quick-win.** Defines "disease" itself |
| IDO | K | Infectious-disease process concepts | OBO/OWL | open (CC0) | few 100s core | IDO GitHub | obo | L | M | Clean OBO scaffolding |
| Symptom Ontology (SYMP) | K | Patient-facing symptoms | OBO/OWL | open (CC0) | ~1k terms | DiseaseOntology GitHub | obo | L | M | Distinct from HPO's clinician framing |
| Mammalian Phenotype (MP) | K | Mouse/mammalian phenotype terms | OBO/OWL/JSON | open (CC BY 4.0) | ~13k terms | mgijax GitHub | obo | L | L | Cross-species alignment w/ HPO |
| Vaccine Ontology (VO) | K | Vaccine/immunisation concepts | OBO/OWL | open (CC BY 4.0) | ~5k terms | vaccineontology GitHub | obo | L | M | Near-zero cost |
| CIDO | K | COVID/coronavirus disease concepts | OBO/OWL | open (CC0) | low 1000s | CIDO GitHub | obo | L | L | Narrow; covered by IDO/MONDO/VO |
| ICD-11 (WHO) | K | Global disease/disorder classification | REST/JSON/spreadsheet | restr | ~17k categories | icd.who.int | new | L | M | **CC BY-ND — NO derivatives** (real blocker for reformulating defns) |
| ICD-10-CM / ICD-9-CM | W | US clinical diagnosis codes + titles | XML/CSV/PDF | open (PD) | ~70k codes | CDC/CMS | new | L | M | Short labels, not rich defns; crosswalk use |
| LOINC | K | Lab test / clinical-observation identity | CSV/RRF | open (free, reg.) | ~96k terms | loinc.org (acct) | new | L | M | Tabular → bespoke extractor |
| RxNorm | K | see §3.4 | RRF | open* | ~300k RXCUIs | NLM | new | L | M | Drug-identity layer |
| ClinVar | W | Variant→disease significance | VCF/XML/TSV | open (PD) | millions | NCBI FTP | new | M | M | Also under Genetics |
| MedGen | K | Aggregated condition-concept dictionary | flat | restr | ~250k | ncbi.nlm.nih.gov/medgen | new | L | L | **UMLS-entangled**; prefer MONDO/OMIM/HPO |
| OncoTree | K | Clinical cancer-type hierarchy | REST/JSON | open (CC BY 4.0) | ~868 types | oncotree.mskcc.org | new | L | M | API-only → small extractor |
| ICD-O-3 | K | Tumour morphology/topography codes | PDF/web | restr | ~1.2k morph codes | who.int/IACR | new | L | L | WHO copyright; no clean bulk |
| ICF | K | Functioning/disability classification | PDF/web | restr | ~1.6k categories | who.int | new | L | L | WHO-encumbered; no clean bulk |
| GARD | W | Plain-language rare-disease summaries | web/API | ? | ~7k entries | rarediseases.info.nih.gov | new | L | L | Re-aggregation of MONDO/Orphanet/OMIM/HPO |
| SNOMED CT | B | Clinical terminology | RF2/(RDF) | restr | ~350k+ | UTS + Affiliate | new | L | M | **Restricted — see §6** |
| UMLS Metathesaurus | B | 200+ vocab cross-walk | RRF/(RDF) | restr | >4.5M | UTS acct | new | L | M | **Restricted — see §6** |
| MedDRA | K | see §3.4 | delimited | restr | ~80k+ LLTs | meddra.org | new | L | L | **Restricted** |
| OMIM | B | see §3.1 | flat/API | restr | ~26k | omim.org | new | M | M | **Restricted** |
| CTD | W | see §3.4 | TSV/XML | restr | ~94M connections | ctdbase.org | new | L | L | **CC BY-NC (commercial paid)** |
| DisGeNET | W | see §3.1 | TSV/RDF | restr | ~2M assoc | disgenet.com | rdf | L | M | **CC BY-NC-SA** |
| ATC | K | see §3.4 | flat/OWL | open/? | ~6k | atcddd.fhi.no | rdf/new | L | M | Licence to verify |

### 3.6 Anatomy, cells, organisms & taxonomy

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| UBERON | K | Cross-species anatomy | OWL/OBO/JSON | open (CC BY 4.0) | ~13–15k classes | uberon.github.io | obo | L | H | **Quick-win.** Central anatomy backbone |
| Cell Ontology (CL) | K | see §3.2 | OWL/OBO | open (CC BY 4.0) | ~2.7k | obophenotype GitHub | obo | L | H | **Quick-win** (home domain) |
| FMA | K | Granular human anatomy | OWL | open (custom UW) | ~75k classes | sig.biostr.washington.edu; BioPortal | rdf | L | H | **Quick-win (caveated).** OBO PURL is PARTIAL; full = separate distribution/licence |
| NCBITaxon | B | Taxonomic identity of organisms | OWL/OBO | open (CC0) | ~2M+ nodes | obophenotype/ncbitaxon | obo | L | H | **Quick-win.** PREFERRED route vs raw taxdump; very large → chunk |
| NCBI Taxonomy (raw taxdump) | W | Names/ranks/lineage + host/type/merge history | .dmp flat | open (PD) | ~2.6M taxa | ncbi FTP | new | L | M | Only for extra fields not in the OBO conversion |
| Plant Ontology (PO) | K | Plant anatomy + growth stages | OWL/OBO | open (CC BY 4.0) | few 1000s | Planteome GitHub | obo | L | H | **ALREADY MINED** — do not re-ingest; Planteome siblings (TO/PSO) are cheap adds |
| CARO | K | Upper-level anatomy template | OWL/OBO | open (CC BY) | ~60–100 classes | OBO PURL | obo | L | M | Tiny but structurally important under UBERON/ZFA/FBbt/MA |
| FoodOn | K | Food products + source organisms | OWL/OBO | open (CC BY 4.0) | 10Ks classes | FoodOntology GitHub | obo | L | M | Bridges taxonomy↔food identity |
| ZFA / ZFS | K | Zebrafish anatomy + stages | OWL/OBO | open (CC0) | ~2.86k classes | ZFIN GitHub | obo | L | M | CC0 |
| FBbt | K | Drosophila anatomy | OWL/OBO | open (CC BY 4.0) | few 1000s | OBO PURL | obo | L | M | CARO-aligned; verify licence |
| XAO | K | Xenopus anatomy + stages | OWL/OBO | open (CC BY) | ~couple 1000 | OBO PURL | obo | L | L | Low marginal value beyond UBERON |
| MA (adult mouse anatomy) | K | Adult mouse anatomy | OWL/OBO | open (CC BY 4.0) | ~2.7k | obophenotype GitHub | obo | L | M | Largely merged into UBERON |
| EHDAA2 | K | Human developmental anatomy (stages) | OWL/OBO | ? | few 1000 | obophenotype GitHub | obo | L | L | Unmaintained since ~2012; **licence unstated** |
| Cell Line Ontology (CLO) | B | Cell-line types + ~40k named lines | OWL/OBO | open | ~40k lines | obofoundry.org/clo | obo | L | M | Cultured lines (vs CL's in-vivo cell types) |
| Cellosaurus | B | Cell-line knowledge resource | flat/TSV/XML + RDF/OWL | open (CC BY 4.0) | >170k lines | ExPASy FTP; RDF ontology | rdf | L | M | RDF view makes it cheap |
| GBIF Backbone Taxonomy | W | Synthetic global taxonomic backbone | DwC-A (TSV)/REST | open (CC BY 4.0) | ~6M names | hosted-datasets.gbif.org | new | L | H | De-facto biodiversity backbone |
| Catalogue of Life (CoL) | W | Consensus global species checklist | ColDP/DwC-A/REST | open (CC BY 4.0) | ~2.48M species | catalogueoflife.org | new | L | H | More curated than GBIF; pick one primary |
| ITIS | W | Taxonomic names/hierarchy/synonymy | SQL/flat/WS | open (PD) | ~839k names | itis.gov | new | L | M | Subsumed by GBIF/CoL |
| WoRMS | W | Marine-species taxonomy | REST | restr | ~240k+ species | marinespecies.org | new | L | M | **Bulk redistribution restricted** — API only |
| Open Tree of Life | W | Synthetic phylogenetic tree + reference taxonomy | flat/Newick/JSON | open (mixed src) | OTT ~5M taxa | opentreeoflife.org | new | L | M | Unique value = actual evolutionary tree |
| GTDB | B | Genome-based bacterial/archaeal taxonomy | TSV/API | ? | ~136k species | gtdb.ecogenomic.org | new | M | M | **Active reclassification vs classical taxonomy**; verify licence |
| LPSN | K | Validly-published prokaryote names | web | restr | 10Ks names | lpsn.dsmz.de | new | L | L | **CC BY-NC** |
| ICTV Master Species List | K | Official virus taxonomy | Excel (MSL) | open (CC BY 4.0) | ~14.7k species | ictv.global/msl | new | L | H | **Only authoritative virus-identity source** (absent from OBO) |
| World Flora Online (WFO) | W | Vascular-plant + bryophyte checklist | DwC-A/JSON/CoLDP | open (CC0) | 100Ks species | worldfloraonline.org | new | L | H | Best-licensed plant taxonomy (CC0) |
| POWO / WCVP (Kew) | W | Vascular-plant names/synonymy/distribution | CSV/REST | ? | 100Ks species | powo.science.kew.org | new | L | L | Redundant w/ WFO; verify bulk licence |
| IPNI | W | Plant-name nomenclatural index | web/per-record RDF | ? | ~1.6M names | ipni.org | new | L | L | No bulk yet; per-record RDF scraping only |
| Index Fungorum / MycoBank | W | Fungal nomenclature | web/Excel | ? | 100Ks names each | indexfungorum.org; mycobank.org | new | L | L | **Licence unclear both** |
| AlgaeBase | W | Algae taxonomy | CSV/web | ? | ~165k+ names | algaebase.org | new | L | L | **Licence ambiguous** |
| BOLD Systems | W | DNA-barcode records + IDs | REST | ? | millions | boldsystems.org | new | L | L | Specimen data, low definitional value |
| EOL / TraitBank | W | Species pages + organism traits | REST/DwC | open (CC BY 4.0) | ~1.3M pages | eol.org; opendata.eol.org | new | L | M | TraitBank = clean organism-attribute world-facts |
| ZooBank | W | Zoological nomenclatural-act registry | web (LSID) | ? | 100Ks acts | zoobank.org | new | L | L | Nomenclatural acts, not concepts |
| Paleobiology DB (PBDB) | B | Fossil taxa + occurrences | REST (JSON/CSV) | open (CC BY/CC0) | >1.26M occurrences | paleobiodb.org | new | M | M | Unique extinct-organism coverage; opinions actively revised |
| IRMNG | W | Marine+nonmarine genus-level names (incl. fossil) | web/snapshot | open (CC BY) | 100Ks genera | irmng.org | new | L | L | Genus-level cross-check into GBIF/OToL |

### 3.7 Geography, places & Earth

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| GeoNames | B | Gazetteer + feature-code place-type taxonomy | OWL/RDF + TSV | open (CC BY 4.0) | ~13M features | download.geonames.org; geonames.org/ontology | rdf | L | H | **Quick-win.** Geo backbone for DBpedia/YAGO |
| Getty TGN | B | Place-name thesaurus + place types | RDF (Getty LOD) | open (ODC-By) | ~3.0M records | vocab.getty.edu | rdf | L | H | **Quick-win.** Curated place-TYPE hierarchy |
| OGC GeoSPARQL | K | Feature/Geometry/spatial-relation primitives | OWL | open (OGC) | small | opengeospatial GitHub | rdf | L | H | **Quick-win.** Geo's upper-ontology seam |
| KnowWhereGraph | B | Geo-KG: ontology + 30+ environmental/demographic layers | OWL-DL + SPARQL | open (CC BY 4.0) | ~29B triples | knowwheregraph.org | rdf | L | H | **Quick-win.** Richest existing geo KG |
| Wikidata (geo subset) | B | Place types + instances + coordinates | RDF/SPARQL | open (CC0) | 10Ms geo items | WDQS | rdf | M | H | Best source for place-TYPE hierarchy; filter disputed items |
| UN M49 | K | UN statistical country/region hierarchy | CSV/JSON | open (PD) | ~249 entities | unstats.un.org | new | L | H | Deliberately less politically fraught than ISO 3166 |
| ISO 3166 (+2/3, OMG LCC) | K | Country/subdivision codes + names | CSV; OWL (OMG LCC) | restr* | ~249 + ~5k subdiv | omg.org/spec/LCC; datahub mirrors | rdf/new | M | H | Official ISO text restricted; **use open community/LCC mirrors**; contested cases |
| geoBoundaries | W | Political/admin boundary polygons | GeoJSON/Shapefile | open (CC BY 4.0) | up to ADM5 | geoboundaries.org | new | M | H | Open alternative to GADM; disputed borders |
| Natural Earth | B | Cultural + physical vector features | Shapefile | open (PD) | 258 countries + features | naturalearthdata.com | new | L | H | Cleanest PD cartographic reference |
| IANA Time Zone DB | K | Region→timezone + historical rules | plain text | open (PD) | ~600 zones | iana.org/time-zones | new | L | H | Tiny, canonical place↔time link |
| Pleiades | B | Ancient/historical places + types | CSV/JSON/RDF | open (CC BY 3.0) | ~41k places | pleiades.stoa.org | rdf | L | M | Historical-geography layer |
| UN/LOCODE | W | Ports/airports/terminals codes | CSV/TXT/MDB | open (PDDL) | ~104k locations | unece.org | new | L | M | Logistics place identity; also Standards |
| OpenStreetMap | W | Crowd map of physical/built world | OSM XML/PBF | open (ODbL) | billions of features | planet.openstreetmap.org | new | M | M | **ODbL share-alike**; use LinkedGeoData for RDF slice |
| LinkedGeoData | W | RDF-ised OSM | RDF/SPARQL | open (ODbL) | ~20B triples | linkedgeodata.org | rdf | M | M | Pragmatic RDF path into OSM; check dump freshness |
| DBpedia (geo) | B | Places from Wikipedia infoboxes | RDF | open (CC BY-SA) | ~735k places (EN) | databus.dbpedia.org | rdf | M | M | Cross-link source; infobox quality varies |
| YAGO (geo) | B | Place taxonomy + instances (WordNet+GeoNames) | RDF/TSV | open (CC BY) | 1.5M+ geo entities | yago-knowledge.org | rdf | M | M | Bridges lexical↔geo |
| USGS GNIS | W | US domestic feature names | pipe-delimited | open (PD) | 1–2M+ features | usgs.gov | new | L | M | US-only complement to GeoNames |
| NGA GNS | W | Foreign geographic names (romanisation) | delimited | open (PD) | ~8M features | geonames.nga.mil | new | L | M | Foreign counterpart to GNIS |
| Who's On First | B | Multi-scale gazetteer + placetype hierarchy | GeoJSON per place | open (CC0*) | ~26M records | whosonfirst-data GitHub | new | L | M | Placetype granularity taxonomy |
| Overture Maps | B | Places (POI taxonomy) + Divisions | GeoParquet | open (CDLA/ODbL) | 100Ms records | AWS registry | new | L | M | Actively maintained; GeoParquet extractor |
| Eurostat NUTS | W | EU statistical regions | Shapefile/GeoJSON/CSV | open (EU) | 92/244/1165 regions | ec.europa.eu/eurostat | new | L | L | EU-only |
| Marine Regions | B | Marine place names + maritime boundaries | WFS/CSV/REST | open (CC BY) | 100Ks names | marineregions.org | new | M | M | Ocean/sea gap; EEZ boundaries contested |
| SimpleMaps World Cities | W | City instances + population | CSV/XLSX/SQL | open (CC BY 4.0) | ~4.4M cities | simplemaps.com | new | L | L | GeoNames covers this with better provenance |
| GADM | W | Admin boundary polygons (to ADM5) | Shapefile/GPKG | restr | 400,276 areas | gadm.org | new | M | L | **NC + no-redistribution** — prefer geoBoundaries |
| FAO GAUL | W | Admin boundary polygons | Shapefile/GEE | restr | global multi-level | fao.org | new | M | L | **2015 restricted; 2024 now CC BY 4.0** — check vintage |
| WDPA / Protected Planet | W | Protected areas + IUCN category | Shapefile/CSV/API | restr | ~312k PAs | protectedplanet.net | new | L | L | **⚠ forbids redistribution in any form w/o permission** |
| WWF Ecoregions | B | Biome/ecoregion type taxonomy + polygons | Shapefile | restr | 825 ecoregions | databasin.org | new | L | L | **CC BY-NC**; rare biome-TYPE taxonomy |
| Köppen-Geiger | K | Climate-type classification | raster/GeoTIFF | ? | 30 sub-types | multiple mirrors | new | L | L | Genuinely definitional; verify per-raster licence |
| IHO Limits of Oceans & Seas (S-23) | K | Official ocean/sea definitions & limits | PDF + coord lists | ? | few 100 regions | iho.int; Pangaea digitised | new | H | L | **⚠ CONTESTED** (Sea of Japan/East Sea, Persian/Arabian Gulf); 1953 ref ed. |
| OpenAddresses | W | Address points | CSV/GeoJSON | ? | ~470M points | results.openaddresses.io | new | L | L | Below "place" resolution; per-source licences |

### 3.8 Astronomy & space

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Unified Astronomy Thesaurus (UAT) | K | Astronomy concept graph | SKOS/RDF/JSON/CSV | open (CC BY-SA 4.0) | ~2.4k concepts | astrothesaurus GitHub | rdf | L | H | **Quick-win.** Best off-the-shelf astronomy concepts |
| IVOA Object-Type Ontology | K | Celestial object classes | OWL-DL | open (IVOA) | ~70 classes | ivoa.net | rdf | L | H | **Quick-win.** "What class of object is this" |
| IVOA Vocabularies (UCD1+) | K | Astronomical measured-quantity concepts | SKOS/RDF | open (IVOA) | 100s terms | ivoa.net/rdf | rdf | L | M | Complements QUDT for quantity grounding |
| SIMBAD | B | Named-object identity/coords/type | ASCII/VOTable/TAP | restr | ~19.5M objects | simbad.u-strasbg.fr | new | L | M | Mostly world-fact; **CDS terms (citation req.)** |
| NASA Exoplanet Archive | B | Confirmed exoplanets + parameters | REST/TAP/CSV/JSON | open (PD) | ~6.3k confirmed | exoplanetarchive.ipac | new | L | H | Authoritative, open, maintained |
| Gaia Archive (DR3/DR4) | W | Astrometry/photometry for ~1.8B sources | TAP/VOTable/CSV/Parquet | open (CC BY-SA 3.0 IGO) | ~1.8B sources | gea.esac.esa.int | new | L | M | Huge, low definitional density |
| NED | W | Extragalactic object identity/redshift | web/API/VOTable | ? | ~1.1B objects | ned.ipac.caltech.edu | new | L | M | World-fact; licence unstated |
| Minor Planet Center (MPCORB) | W | Asteroid/comet orbits + designations | fixed-width DAT/JSON | restr | ~1.4M+ bodies | cfa-ftp/minorplanetcenter | new | L | M | Free files redistributable w/ attribution |
| JPL SBDB | B | Small-body ID/orbit/physical params | REST/JSON | ? | ~1.4M bodies | ssd-api.jpl.nasa.gov | new | L | M | Cleaner API; likely PD but unconfirmed |
| ATNF Pulsar Catalogue | W | Pulsar parameters | psrcat/CSV | open (BSD data) | ~3k pulsars | atnf.csiro.au | new | L | L | Openly licensed but narrow |
| GCVS / AAVSO VSX | B | Variable-star names + variability-type taxonomy | ASCII/VOTable | ? | 58k GCVS / 400k+ VSX | sai.msu.su; vsx.aavso.org | new | L | M | The variability-TYPE scheme is the higher-value kernel bit |
| IAU Catalog of Star Names | K | Official proper star names | plain text | open | ~600 names | exopla.net/star-names | new | L | M | Tiny, maximally authoritative |
| IAU 88 constellations + boundaries | K | Official constellations + sky boundaries | text/CSV | open (PD-in-practice) | 88 | iau.org; Bill-Gray/constbnd | new | L | M | Uncontroversial canonical partition |
| USGS Gazetteer of Planetary Nomenclature | B | Planetary feature names + feature-type categories | web/CSV/shapefile | open (PD) | 16k+ names, ~150 types | usgs.gov; data.nasa.gov | new | L | M | Feature-type list = compact kernel taxonomy |
| Meteoritical Bulletin DB | B | Meteorites + classification taxonomy | web/exports | open (CC BY 4.0) | ~80k names | lpi.usra.edu/meteor | new | L | M | Classification taxonomy is definitional |
| PDS4 Information Model | K | Planetary-science data-concept ontology/dictionary | OWL/TTL/XML | ? | 100s classes | NASA-PDS GitHub | rdf | L | M | Genuine formal ontology; **confirm licence (likely Apache-2.0)** |
| VizieR | B | Meta-index of >25k astronomy catalogues | VOTable/TAP | restr | ~25.8k catalogues | vizier.cds.unistra.fr | new | L | L | Access layer, not a coherent concept set |
| Open Exoplanet Catalogue | B | Exoplanet systems | XML | open (MIT) | ~4k systems | OEC GitHub | new | L | L | Redundant w/ NASA archive |
| exoplanet.eu | B | Exoplanets + disks | VOTable/CSV | ? | ~8.25k objects | exoplanet.eu | new | L | L | Redundant; licence unstated |
| SDSS | W | Photometric/spectroscopic classifications | SQL/CSV/FITS | open | 100M+ objects | skyserver.sdss.org | new | L | L | Overlaps Gaia/NED; low defn density |
| 2MASS / AllWISE | W | IR photometry/positions | FITS/CSV/VOTable | open | 470M–750M sources | irsa.ipac.caltech.edu | new | L | L | Completeness only |
| ICRF3 | K | Celestial reference-frame definition | ASCII | open | ~4.5k radio sources | hpiers.obspm.fr | new | L | L | Defines the reference-frame convention itself |
| NAIF SPICE kernels | W | Solar-system/spacecraft ephemerides | binary SPICE | open (PD) | N/A (toolkit) | naif.jpl.nasa.gov | new | L | L | Computational infra, out of kernel scope |

### 3.9 Physics, units, materials science & mathematics

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| QUDT | B | Units/quantity-kinds/dimensions | OWL/RDF | open (CC BY 4.0) | ~1.7k units | qudt.org | rdf | L | H | **ALREADY MINED** — verify w/ Fable before any re-ingest |
| UCUM | K | Machine-readable units grammar | XML + grammar | open (Regenstrief) | ~300 base units | ucum.org | new | L | H | Bespoke parser; small/mechanical |
| OM (Ontology of units of Measure) | K | Units/quantities across ~15 domains | OWL2-DL | open (BSD) | ~600 units | HajoRijgersberg/OM | rdf | L | M | Cross-check vs QUDT |
| CODATA / NIST constants | B | ~350 fundamental physical constants | ASCII table | open (PD) | ~350 | physics.nist.gov | new | L | H | Trivially parseable; high value/byte |
| BIPM SI Brochure | K | SI base/derived unit prose defns | PDF/HTML | ? | 7 base + ~22 derived | bipm.org | new | L | M | Content already in QUDT/UCUM/OM structured |
| ISO/IEC 80000 | K | Formal quantity/unit definitions | PDF (DRM) | restr | 17 parts | iso.org (purchase) | new | L | L | **Paywalled/DRM** |
| GNU Units database | B | ~3–5k unit definitions/conversions | plain text | open (GPLv3) | ~3–5k | GNU units | new | L | M | Data reuse likely fine; check licence |
| UnitsML | K | XML schema + unit reference dictionary | XML/XSD | ? | 100s units | unitsml.nist.gov | new | L | L | Thin vs QUDT/UCUM/OM |
| Wikidata (physics/math) | B | Quantities/units/constants/particles/elements | RDF/SPARQL | open (CC0) | 10Ks (subset) | WDQS | rdf | M | H | Crowd-edited → filter; SPARQL carve-out |
| Materials Project | B | Computed inorganic-material properties | REST/JSON | open (CC BY 4.0) | ~150k+ | api.materialsproject.org; AWS | new | L | H | DFT-computed; uncontroversial as computed data |
| OQMD | B | DFT thermodynamic/structural props | SQL/OPTIMADE | open (CC BY 4.0) | ~1.4M | oqmd.org | new | L | M | Overlaps Materials Project |
| AFLOW | B | Ab-initio material properties | REST (AFLUX)/JSON | ? | 3.5M+ | aflow.org | new | L | M | **Verify licence** |
| NOMAD | B | Computed materials data (many codes) | REST/JSON | open (CC BY 4.0) | 10Ms entries | nomad-lab.eu | new | L | M | Custom Archive schema |
| JARVIS (NIST) | B | DFT/ML/FF properties 2D/3D materials | REST (OPTIMADE)/JSON | ? | 80k+ mat., 1M+ props | jarvis.nist.gov | new | L | M | NIST data licence not explicit |
| Crystallography Open DB (COD) | W | Experimental crystal structures | CIF/MySQL | open (CC0) | ~500k+ | crystallography.net/cod | new | L | H | CIF parser; large, fully open |
| Materials Data Facility | W | Aggregated materials-dataset index | REST/JSON | ? | ~30 TB | materialsdatafacility.org | new | L | L | Heterogeneous aggregator |
| EMMO | K | Physics+materials+manufacturing ontology | OWL (TTL) | open (CC BY 4.0) | ~1k+ classes | emmo-repo GitHub | rdf | M | H | **Commits to 4D perdurantism** — not theory-neutral; flag |
| IUPAC CIAAW atomic weights | K | Standard atomic weights/isotopic abundances | HTML | ? | 118 elements | ciaaw.org | new | L | M | Tiny/zero-controversy; also via PubChem |
| NIST Atomic Spectra DB (ASD) | W | Atomic energy levels/lines | web query export | ? | >300k lines | physics.nist.gov/ASD | new | L | L | No clean bulk → scraping |
| NIST Chemistry WebBook | W | Thermochemical/spectral data | web | restr | ~100k species | webbook.nist.gov | new | L | L | **Reuse restricted**; also Chemistry |
| Particle Data Group (PDG) | B | Elementary particles + measured properties | REST/Python/SQLite | restr | ~500+ states | pdgapi.lbl.gov | new | L | H | **Review of Particle Physics = CC BY-NC** — flag |
| SWEET Ontology | K | Earth/environmental + units/quantity modules | OWL | open (CC0/Apache) | ~6k concepts | ESIPFed/sweet | rdf | L | M | Only units/quantity submodules core here |
| OEIS | K | Integer sequences (formula-defined) | custom text/git | open (CC BY-SA 4.0) | ~380k+ | oeis.org GitHub | new | L | H | Simple documented text format |
| Mathlib (Lean 4) | K | Machine-checked math definitions + theorems | Lean 4 DSL/JSON | open (Apache-2.0) | 115k+ defns | leanprover-community GitHub | new | L | H | Highest-fidelity "what IS X" for math; Lean-aware tooling |
| Isabelle AFP | K | Machine-checked math/CS libraries | Isabelle .thy | open (BSD/LGPL) | 700+ entries | isa-afp.org | new | L | M | Largely redundant w/ Mathlib for pure math |
| DLMF | K | Special-function semantic definitions | web + Content-MathML | ? | 700+ functions | dlmf.nist.gov | new | L | M | Uniquely rigorous; no bulk; licence friction |
| ProofWiki | K | Math definitions + proofs | MediaWiki XML | open (CC BY-SA 3.0) | ~40k+ pages | proofwiki.org/xmldump | new | L | H | **Reuse the mined Wiktionary MediaWiki parser pattern** |
| Encyclopedia of Mathematics | K | Encyclopedic math articles | MediaWiki | open (CC BY-SA 3.0) | ~8k articles | encyclopediaofmath.org | new | L | M | Dump availability unconfirmed |
| nLab | K | Category theory / math-physics concepts | Instiki wiki/HTML | ? | ~20k+ pages | ncatlab.org | new | M | L | **No site-wide licence** — blocker despite high value |
| OpenMath Content Dictionaries | K | Formal semantics of math symbols | XML (CD schema) | open (OpenMath) | 1000s symbols | openmath.org/cd | new | L | M | Complements DLMF/Mathlib at symbol level |
| MSC2020 | K | Math subject classification | PDF/text (RDF proposed) | restr | ~6k codes | msc2020.org | new | L | L | **CC BY-NC-SA**; thin taxonomy |
| Wolfram MathWorld | K | Math encyclopedia | web (HTML) | restr | ~13k entries | mathworld.wolfram.com | new | L | L | **All rights reserved** — do not ingest |

### 3.10 Language, lexical & linguistic

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| CILI | K | Language-independent concept-identity index | RDF/CSV | open (CC0/CC BY) | ~120k IDs | globalwordnet/cili | rdf | L | H | **Quick-win.** Cross-lingual concept anchor (NSM-adjacent) |
| DBnary | B | Wiktionary lexical data as OntoLex-Lemon RDF | RDF/Turtle | open (CC BY-SA 3.0) | millions, 26 langs | kaiko.getalp.org | rdf | L | H | **Quick-win.** RDF path for already-mined Wiktionary |
| Open English WordNet (OEWN) | K | English synsets/senses/relations | RDF/JSON-LD/LMF | open (CC BY 4.0) | ~120k synsets | globalwordnet GitHub | rdf | L | M | Cleaner-licensed successor to mined WordNet — dedup/replace call |
| Open Multilingual Wordnet (OMW) | K | 40+ language wordnets on shared ILI | LMF/RDF/JSON-LD | ? | 40+ langs | globalwordnet/OMW | rdf | L | H | **Per-language licence varies — verify** before bulk redistribution |
| ConceptNet (symbolic graph) | B | Commonsense relations (IsA/PartOf/UsedFor/…) | CSV/JSON | open (CC BY-SA 4.0) | ~34M edges | commonsense GitHub | new | M | M | Distinct from mined Numberbatch vectors; crowd-quality uneven |
| VerbNet | K | Verb classes: frames/roles/event semantics | XML | ? | ~5.8k senses | uvi.colorado.edu | new | L | M | Predicate/action structure; verify redistribution |
| PropBank | K | Predicate–argument frames | XML | open | ~10k framesets | propbank GitHub | new | L | M | Frame files free (corpus is LDC) |
| NomBank | K | Nominalisation argument frames | XML | ? | ~5k framesets | nlp.cs.nyu.edu | new | L | L | Less consistently open than PropBank |
| SemLink | K | Maps VerbNet↔PropBank↔FrameNet↔WordNet | XML/TSV | ? | 5–10k senses | cu-clear/semlink | new | L | M | Alignment layer over mined FrameNet |
| Kaikki / wiktextract | B | Full Wiktionary extraction (all editions) | JSONL | open (CC BY-SA 4.0) | >10M records (EN) | kaikki.org | new | L | H | Best full-scale Wiktionary path; simple JSON extractor |
| GOLD | K | Grammatical-category ontology | OWL/RDF | open | 100s classes | linguistics-ontology.org | rdf | L | M | Linguistics' "BFO/RO" for grammar categories |
| OLiA | K | Reference model mapping POS/annotation tagsets | OWL/RDF | open | 100+ ontologies | acoli-repo GitHub | rdf | L | M | Complements GOLD |
| Glottolog | B | Languages/dialects/families + classification | CLDF (CSV+JSON-LD) | open (CC BY 4.0) | ~25k languoids | glottolog GitHub | new | M | H | Language-identity registry; some family calls contested |
| WALS | W | Typological structural features | CLDF/CSV | open (CC BY 4.0) | 2662 langs × 192 | wals.info | new | L | M | Descriptive/observational |
| PHOIBLE | B | Phoneme inventories + features | CLDF/CSV | open (CC BY-SA) | ~2186 inventories | phoible.org | new | L | M | Defines phoneme/feature categories |
| Concepticon | K | ~4k basic concepts across wordlists | CLDF/CSV | open (CC BY 4.0) | ~4k concept sets | concepticon GitHub | new | L | H | **NSM-relevant** basic-concept inventory; cheap |
| CLICS | W | Cross-linguistic colexifications | CLDF | open (CC BY 4.0) | 10Ks links | clics GitHub | new | L | L | Semantic-proximity signal |
| ASJP | W | Standardised phonetic wordlists | CLDF/CSV/TSV | open (CC BY) | ~7655 lists | asjp.clld.org | new | L | L | Lexicostatistics; limited defn value |
| Grambank | W | Grammatical typology features | CLDF/CSV | open (CC BY 4.0) | 2467 × 195 | grambank GitHub | new | L | L | Binary sibling of WALS |
| IDS | W | Comparative wordlists (1310 concepts) | CLDF/CSV | open (CC BY) | 330 langs | ids.clld.org | new | L | L | Concept↔wordform mapping |
| WOLD | W | Loanword/borrowing status | CLDF/CSV | open (CC BY) | 41 langs | wold.clld.org | new | L | L | Word-origin facts |
| UniMorph | K | Universal morphological paradigms | TSV | open (CC BY-SA) | 170+ langs | github.com/unimorph | new | L | M | Morphological feature inventory; simple TSV |
| Universal Dependencies schema | K | Universal POS + morphosyntactic features | schema/JSON; CoNLL-U | open (CC BY-SA) | ~17 POS + ~24 feats | universaldependencies.org | new | L | M | Tiny schema is the high-value cheap part |
| ISO 639-3 | K | Language identifiers/names/macrolanguages | TSV | open (SIL tables) | ~7.9k codes | iso639-3.sil.org | new | L | H | Foundational identity anchor; trivial |
| ISO 15924 | K | Script codes/names | semicolon text | open (Unicode) | ~200 scripts | unicode.org/iso15924 | new | L | M | Grounds "script" concept |
| IANA Language Subtag Registry | K | BCP-47 subtags (639+15924+3166/M49) | plain-text registry | open (IANA) | ~10k records | iana.org | new | L | M | Unifying glue layer |
| Unicode Character DB (UCD) | K | Per-code-point character properties | UCD text/XML | open (Unicode) | ~150k code points | unicode.org/Public/UCD | new | L | M | Grounds "character/symbol" |
| Unicode CLDR | W | Locale data (names/plurals/formats) | XML/JSON | open (Unicode) | ~700+ locales | unicode-org/cldr | new | L | L | Cross-language name variants |
| PanLex | W | Cross-lingual translation equivalences | CSV/JSON/SQL/SQLite | open (CC0) | ~20M lexemes, ~9k langs | panlex.org/snapshot | new | L | H | Uniquely large CC0; triangulates concept identity |
| Roget's Thesaurus (1911) | K | ~1000 concept heads grouping words | plain text/RDF ports | open (PD) | ~1k classes | Project Gutenberg | new | L | L | Superseded by WordNet; zero-friction legacy cross-check |
| SIL Ethnologue | W | Living-language reference (speakers/vitality) | web/PDF | restr | ~7k langs | ethnologue.com | new | L | L | **Paywalled**; Glottolog is the open substitute |
| OntoNotes | B | Multi-genre annotated corpus | LDC format | restr | ~1.6M words | catalog.ldc.upenn.edu | new | L | L | **LDC-restricted** |
| Merriam-Webster / Oxford APIs | K | Commercial dictionary definitions | REST/JSON | restr | 150k–450k | dictionaryapi.com | new | L | L | **Bulk redistribution prohibited**; open equivalents exist |
| JMdict/EDICT + FreeDict | K | Free bilingual/multilingual dictionaries | XML/TEI | open (CC BY-SA/GPL) | JMdict ~200k | edrdg.org; freedict.org | new | L | L | Narrower than Wiktionary/DBnary/PanLex |

### 3.11 General & cross-domain knowledge graphs

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Wikidata | B | Entities/concepts + P31/P279 taxonomy | RDF/JSON/SPARQL | open (CC0) | ~122M items | dumps.wikimedia.org; WDQS | rdf | L(/M) | H | **Quick-win (caveated).** Anchor/reconciliation layer; crowd-edited → filter |
| schema.org | K | ~800 general web types + ~1450 props | OWL/RDFS | open (CC BY-SA 3.0) | ~800 types | schema.org; GitHub | rdf | L | H | **Quick-win.** Small ubiquitous top-level scaffold |
| DBpedia | B | Wikipedia facts + curated ontology | RDF/SPARQL | open (CC BY-SA 3.0) | ~6–9M entities (EN) | databus.dbpedia.org | rdf | L(/M) | H | **Quick-win (caveated).** LOD hub; cadence slowed |
| YAGO 4.5 | B | Clean taxonomy + Wikidata facts | RDF/Turtle | open (CC BY-SA 3.0) | millions | yago-knowledge.org | rdf | L(/M) | H | **Quick-win (caveated).** Engineered for logical consistency |
| Getty AAT | K | Art/architecture/material-culture concepts | SKOS/RDF | open (ODC-By) | ~60k+ concepts | vocab.getty.edu | rdf | L | H | **Quick-win.** Clean genus/differentia thesaurus |
| LCSH | K | ~400k general subject concepts | SKOS/MADS RDF | open (PD) | ~400k | id.loc.gov/download | rdf | L | H | **Quick-win.** Broadest library vocab; PD |
| CCO (Common Core Ontologies) | K | Mid-level agent/event/artifact/info on BFO | OWL | open (BSD-3) | 1000s classes | CommonCoreOntology GitHub | rdf | L | H | **Quick-win.** Extends mined BFO/RO beyond biomed |
| Getty ULAN | W | Artist authority records | SKOS/RDF | open (ODC-By) | ~300k+ | vocab.getty.edu | rdf | L | M | Named-entity grounding (art) |
| VIAF | W | Consolidated name authority records | RDF/JSON | open (ODC-By) | 10Ms records | viaf.org | rdf | L | M | Entity reconciliation; full dump has approval gate |
| DOLCE | K | Foundational ontology (endurant/perdurant/…) | OWL2/CL | ? | dozens categories | appliedontolab GitHub | rdf | L | M | Linguistic/cognitive stance (complements BFO); **licence unstated** |
| ConceptNet | B | Commonsense semantic network | CSV/JSON | open (CC BY-SA 4.0) | 10Ms edges | commonsense GitHub | new | M | H | IsA/PartOf defn-like; crowd-noisier; bespoke edge-CSV |
| ATOMIC 2020 | W | If-then commonsense event/social inferences | TSV/JSON | open (CC BY) | ~1.33M tuples | allenai GitHub | new | M | M | Encodes social/cultural norms → review before "fact" |
| NELL | W | Web-extracted confidence-weighted beliefs | TSV | ? | ~120M beliefs | rtw.ml.cmu.edu | new | M | L | Noisy; maintenance/licence unconfirmed |
| Cyc / OpenCyc | K | Hand-built commonsense ontology + FOL rules | CycL/(OWL) | restr | OpenCyc ~239k | Cycorp / stale mirrors | new | L | L | Current Cyc gated; OpenCyc stale (2012) |
| UMBEL | K | Reference concept taxonomy bridging KGs | SKOS/OWL2 | ? | ~34k concepts | structureddynamics GitHub | rdf | L | L | Retired 2019; licence unconfirmed |
| GND | W | German national authority file (+ subjects) | RDF/Turtle/JSON-LD | open (CC0) | ~9–10M | lobid.org/gnd | rdf | L | M | CC0 LCSH/VIAF analog; cross-lingual reconciliation |
| CIA World Factbook | W | Per-country reference profiles | HTML/JSON | open (PD) | ~265 profiles | cia.gov; JSON mirrors | new | M | M | Some fields reflect US-gov POV (disputed borders) |
| Freebase (defunct) | W | Historical general KG | RDF/Turtle | open (CC BY) | ~2.9B facts | archive.org | rdf | L | L | Superseded by Wikidata — no reason to ingest |
| ISO code lists (generic) | W | Country/currency/language reference codes | CSV/JSON/XML | ? | 100s codes | iso-codes pkg; id.loc.gov | new | L | L | Tiny; check which re-release's licence |
| Commercial KGs (Google/Bing/Diffbot) | B | Proprietary entity graphs | REST only | restr | 100Bs facts (unverified) | rate-limited APIs | new | L | L | API-only; not viable for bulk |

### 3.12 Standards, law, finance & classifications

| Source | Kind | Defines | Format | Lic | Size | Access | Ext | C | P | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| ISIC (via FAO Caliper) | K | Global economic-activity classification | RDF/SKOS/CSV/JSON-LD | open (UN) | ~700+ classes | fao.org/statistics/caliper | rdf | L | H | **Quick-win.** Caliper is LOD hub for UN classifications |
| ISCO-08 / ESCO | K | Occupations + skills/competences taxonomy | SKOS/RDF/OWL/CSV | open (CC BY 4.0) | ~3k occ + ~13.9k skills | esco.ec.europa.eu | rdf | L | H | **Quick-win.** Near-zero-friction SKOS/RDF |
| CPC (patent) | K | Technology/invention-domain taxonomy | RDF/OWL (LOD)/XML | open (gov) | ~260k symbols | cooperativepatentclassification.org | rdf | L | H | **Quick-win.** Published as Linked Open Data |
| FIBO | K | Financial-industry concept ontology | OWL/RDF | open (MIT) | 1000s classes | edmcouncil GitHub | rdf | L | H | **Quick-win.** Finance's "BFO/RO" |
| GLEIF LEI + ISO 20275 ELF | B | Legal entities (LEI) + legal-form types (ELF) | CSV/XML + RDF/Turtle | open (CC0) | ~2.7M LEIs; ~500 ELF | gleif.org | rdf | L | H | **Quick-win** (ELF = kernel; LEI register = world) |
| ISO 4217 (Currency Codes) | B | Currency codes/precision | CSV/JSON | open (PDDL mirrors) | ~180 active | datahub.io/currency-codes | new | L | H | Tiny, foundational; complements QUDT with "currency" |
| ISO 3166 (+2, UN M49, OMG LCC) | B | Country/subdivision/region codes | CSV; RDF (OMG LCC) | open* | ~249 + ~5k subdiv | omg.org/spec/LCC; UNSD | rdf/new | M | H | Also under Geography; contested cases |
| ISO 639 (language codes) | B | Language codes/names | CSV/TSV | open (SIL) | ~7.9k | iso639-3.sil.org | new | L | M | Also under Language |
| NAICS / SIC | K | US/NA industry classification | XLSX/CSV | open (PD) | ~1057 NAICS | census.gov/naics | new | L | H | Clean hierarchy; bundles SIC↔NAICS concordance |
| NACE Rev.2 | K | EU economic-activity classification | RDF/CSV | open (EU) | ~996 classes | Eurostat RAMON | rdf | L | M | Redundant w/ ISIC; value = EU correspondence |
| UN/FAO Caliper family (CPC/SITC/BEC/COICOP/COFOG) | K | UN product/trade/consumption/gov-function classes | RDF/SKOS/CSV | open (UN) | CPC ~3.7k etc. | fao.org/statistics/caliper | rdf | L | M | One-stop RDF batch via existing tooling |
| HS (Harmonized System) | K | Classification of traded goods | CSV/JSON (codes); XML/PDF (notes) | restr* | ~5.3k subheadings | datasets/harmonized-system; WCO | new | L | H | **Bare codes open; WCO Explanatory Notes copyrighted/sold** |
| IPC (patent) | K | Global patent/technology taxonomy | XML | open (WIPO) | ~74k subdivisions | wipo.int | new | L | M | Superseded in granularity by CPC |
| Nice / Vienna Classification | K | Trademark goods/services + figurative taxonomy | PDF/XLSX/HTML | restr | Nice ~10k terms | nclpub.wipo.int | new | L | M | WIPO copyright on publication; no clean bulk XML |
| UNSPSC | K | Products & services classification | XLSX/CSV | ? | ~50k+ codes | ungm.org; undp.org | new | L | M | **Conflicting licence claims — verify** |
| GS1 GPC | K | Retail product classification + attributes | JSON/XML/XLSX | restr | ~40k+ bricks | gpc-browser.gs1.org | new | L | M | **GS1 IP policy (RAND, not PD)** |
| eCl@ss | K | Industrial product/service + property dictionaries | XML/CSV/API | restr | ~46k classes | eclass.eu | new | L | L | **Paid licence, no free tier** |
| XBRL US-GAAP / IFRS | K | Accounting concepts (asset/liability/revenue/…) | XBRL/XML | ? | ~20k + ~6k elements | xbrl.us; sec.gov; fasb.org | new | L | H | High defn value; **IFRS text restricted — resolve licence** |
| ISO 20022 | K | Financial-messaging business-concept dictionary | XML | ? | 1000s items | iso20022.org | new | L | M | No clean bulk RDF |
| ISO 10962 (CFI) | K | Financial-instrument TYPE classification | Excel/CSV; (JSON-LD/TTL) | ? | 100s combos | six-group.com | rdf | L | M | Genuinely definitional; confirm RDF links |
| ISO 10383 (MIC) | W | Market/trading-venue identifiers | Excel/CSV/XML | ? | ~2.7k MICs | iso20022.org | new | L | L | Venue registry (instances) |
| Securities IDs (ISIN/CUSIP/SEDOL/OpenFIGI) | W | Instrument identifiers; FIGI adds sec-type | REST/JSON; proprietary | restr | 10Ms | openfigi.com (free); others paid | new | L | L | Only OpenFIGI open; **CUSIP/SEDOL restricted** |
| FinRegOnt | K | XBRL→FIBO/GAAP bridge ontology | OWL/RDF | ? | moderate | finregont.com | rdf | L | L | Cheap RDF bridge; **verify licence** |
| LKIF-Core | K | Basic legal concepts (norm/right/obligation/…) | OWL | ? | few 100 classes | RinkeHoekstra GitHub | rdf | L | H | Legal "BFO/RO"; **confirm licence** |
| Akoma Ntoso/ALLOT + LegalRuleML + ELI | K | Legal-document structure + deontic norms + legislation metadata | OWL/RDF/XML | open (OASIS/EU) | schema-level | w3id.org/akn; OASIS; EUR-Lex | rdf | L | M | Document/norm-structure complement to LKIF |
| eCFR (US CFR) | K | US federal regulations incl. formal Definitions sections | XML/REST | open (PD) | 50 titles | ecfr.gov; govinfo | new | M | H | Definitions sections = authoritative term defns; bespoke prose extraction |
| legislation.gov.uk | K | UK legislation incl. Interpretation sections | CLML/Akoma XML/RDF | open (OGL) | 10Ks Acts/SIs | legislation.gov.uk | new | M | M | RDF metadata cheap; definitions text needs new work |
| EUR-Lex / CELLAR | K | EU legislation + FRBR RDF/OWL metadata | RDF/OWL + XML | open (EU reuse) | 100Ks docs | publications.europa.eu SPARQL | rdf | M | M | Metadata cheap; "definitions articles" need prose extraction |
| Caselaw Access Project | W | ~6.7M US court decisions + metadata | JSON/XML | open (CC0) | ~6.7M cases | case.law; HuggingFace | new | M | M | Record facts low-controversy; holdings interpretive |
| LCSH / LCC | K | see §3.11 (LCSH) + classification scheme | SKOS/MADS RDF | open (PD) | ~400k+ | id.loc.gov | rdf | L | H | Cross-domain library classification |
| UN/LOCODE | W | Trade/transport location codes | CSV/TXT/MDB | open (PDDL) | ~104k | unece.org | new | L | L | Also under Geography |

---

## 4. KERNEL vs WORLD layer — where each domain's value sits

- **Purest KERNEL sources** (definitional taxonomies/ontologies): all OBO ontologies
  (CHEBI, PRO, CL, UBERON, SO, HPO, MONDO, DOID, OGMS, CARO, …); the classification vocabularies
  (schema.org, CCO, Getty AAT/TGN, LCSH, ISIC/ISCO/CPC/NAICS/HS, FIBO, LKIF); the units/quantity
  ontologies (UCUM, OM, IVOA UCD1+); the formal-math corpora (Mathlib, OEIS, ProofWiki, OpenMath);
  the identity registries (HGNC, NCBITaxon, ISO 639-3/3166/4217, GLEIF ELF, UNII); the terminology
  glossaries (IUPAC Gold Book, eCFR/EUR-Lex definitions sections).
- **Purest WORLD sources** (uncontroversial instance facts): gnomAD, dbSNP, 1000G, ClinVar,
  GBIF/CoL/WFO/ICTV species registries, gazetteers (GeoNames instances, GNIS, GNS, Natural Earth),
  astronomy catalogues (Gaia, NED, SIMBAD, MPC, exoplanet archives), materials/crystallography
  (Materials Project, COD), CODATA constants, GLEIF LEI register, UN/LOCODE, Caselaw.
- **Both** (taxonomy + instances in one distribution): UniProt, Reactome, Rhea, PubChem, ChEMBL,
  Wikidata, DBpedia, YAGO, KnowWhereGraph, NCIt, MeSH, NCBITaxon.
- **World-fact sources flagged more contestable than they look** (curated/interpretive/evolving —
  treat as "documented claim", not settled fact): ClinVar, ClinGen, CIViC, GWAS Catalog, STRING,
  AlphaFold (model output), GTDB & PBDB (active taxonomic revision), Orange Book patents, ATOMIC/NELL
  (social/extraction noise), Human Protein Atlas prognostic annotations.

---

## 5. (c) NEEDS-A-NEW-EXTRACTOR — Fable-design items

Every source with **Ext = `new`** below needs a bespoke parser designed and signed off by Fable
(~228 unique sources total carry `new`). Most are low priority; the list below is the subset that
is **open-licensed + low-controversy + high scout-value** — i.e. the extractor builds most worth
Fable *considering* (still: no build without sign-off). Grouped by format family, since one new
extractor often unlocks several sources.

**Flat tabular / CSV / TSV (simplest new builds):**
- HGNC (CC0), Alliance of Genome Resources (CC0), gnomAD (CC0), CODATA/NIST constants (PD, tiny),
  ISO 639-3 (SIL), ISO 4217 (PDDL), NAICS/SIC (PD), Concepticon (CC BY), PanLex (CC0),
  GBIF Backbone / Catalogue of Life / WFO (CC BY/CC0), Glottolog (CC BY), FDA UNII/GSRS (PD),
  EPA CompTox (PD), DrugCentral (CC BY-SA), UN M49 (PD).

**Domain flat-file formats (one parser → a family):**
- GTF/GFF3 + FASTA → Ensembl, GENCODE, RefSeq (genomics annotation).
- CIF/mmCIF → COD, PDB CCD, RCSB PDB (crystallography/structure).
- Darwin Core Archive → GBIF, CoL, WFO, EOL (biodiversity).
- CLDF (CSV+JSON-LD) → Glottolog, WALS, PHOIBLE, Concepticon, Grambank (comparative linguistics).
- MediaWiki XML → **ProofWiki, Encyclopedia of Mathematics** (reuse the mined Wiktionary parser pattern).
- REST/TAP+ADQL → NASA Exoplanet Archive, Materials Project, OQMD, NOMAD (scientific data APIs).

**Bespoke glossary / prose extraction (higher effort, high definitional value):**
- IUPAC Gold Book (chemistry terminology), eCFR / EUR-Lex / legislation.gov.uk (statutory
  Definitions sections), HGVS Nomenclature (variant grammar), WHO INN (PDF lists).

**Custom scientific grammars/DSLs (specialist tooling):**
- UCUM (units grammar), Mathlib (Lean-aware tooling), OEIS (sequence text), OpenMath CDs,
  ICTV MSL (Excel), GNU Units.

**High-value-but-`new` that also carry a licence/quality caveat (verify first):** NCBI Gene,
RefSeq (mixed PD signals), ICD-11 (**CC BY-ND — no-derivatives**), HS Explanatory Notes (WCO
copyright), XBRL IFRS (IFRS text restricted), geoBoundaries/OSM (open but share-alike / disputed
borders), ConceptNet (crowd-quality + edge-CSV).

---

## 6. (d) LICENSING LANDMINES — do NOT ingest without explicit clearance

Fable must gate every one of these before any ingest. Grouped by failure mode.

**Explicitly forbids AI-training / derivative use (hard blockers):**
- **GeneCards** — ToU *explicitly prohibits use of data for AI model training* without a commercial
  licence. Use its primary sources (HGNC/NCBI Gene/Ensembl/UniProt/OMIM) instead.
- **ICD-11 (WHO)** — CC BY-**ND** (no derivatives). A kernel that *reformulates/vectorises* definitions
  is a derivative → real blocker. (ICD-O-3, ICF share WHO's restrictive framework.)
- **Wolfram MathWorld** — all rights reserved, no bulk/redistribution.

**Account/affiliate-gated clinical vocabularies (free within scheme, restricted to redistribute):**
- **SNOMED CT** — UMLS/IHTSDO Affiliate Licence; no substantial-portion extraction by browser users.
- **UMLS Metathesaurus** — UTS licence; per-source restrictions inherited (SNOMED, MedDRA…).
- **MedDRA** — MSSO subscription; no redistribution (hidden dependency of SIDER/FAERS).
- **OMIM** — free academic registration but restrictive redistribution + weekly-refresh obligation.

**Non-commercial (CC BY-NC / NC-SA) — blocks a redistributable/possibly-commercial kernel:**
- DrugBank (full set; **CC0 Open Data subset is fine**), PharmGKB (no-redistribution), CTD, HMDB,
  MEROPS, PANTHER, CAS Common Chemistry, GTEx, DisGeNET, Comparative Toxicogenomics DB, PDG *Review
  of Particle Physics*, MSC2020, BabelNet (research-only), WWF Ecoregions, LPSN.

**Paywalled / commercial-only bulk access:**
- KEGG (bulk/commercial), MetaCyc/BioCyc ($5k+/yr), COSMIC (commercial), BRENDA (commercial tier),
  PROSITE (commercial), CAS Registry/SciFinder, ChemSpider (no bulk), ISO/IEC 80000 & official ISO
  standard texts, eCl@ss, GS1 GPC (GS1 IP), Nice/Vienna (WIPO), CUSIP/SEDOL, SIL Ethnologue,
  OntoNotes (LDC), Merriam-Webster/Oxford, Cyc (gated), commercial KGs, NIST Chemistry WebBook
  (reserves right to charge), GADM & WDPA & FAO GAUL-2015 (no-redistribution geo).

**Licence UNKNOWN — must positively verify before ingest (do not assume open):**
- NCBI Gene, RefSeq, GENO, VariO, ClinGen, GWAS Catalog, TAIR, SCOP/SCOPe, AFLOW, JARVIS, GTDB,
  EHDAA2, POWO/WCVP, IPNI, Index Fungorum/MycoBank, AlgaeBase, BOLD, ZooBank, Köppen-Geiger, IHO
  S-23, OpenAddresses, PDS4, JPL SBDB, NED, exoplanet.eu, GCVS/VSX, DOLCE, LKIF-Core, UMBEL, NELL,
  FinRegOnt, XBRL IFRS, ISO 20022 / 10383 / 10962, UNSPSC, DDInter, SIDER, OMW (per-language),
  VerbNet/NomBank/SemLink, DLMF, nLab, ATC (WHO redistribution), UN/FAO WHO ATC.

**Content-contested (licence may be open, but the *content* is disputed — handle explicitly, not silently):**
- IHO Limits of Oceans and Seas / S-23 (**H-controversy**: sea/ocean naming disputes), ISO 3166 &
  geoBoundaries/GADM (disputed borders/sovereignty), GTDB & PBDB (active taxonomic revision),
  CIA World Factbook (US-gov POV fields), WHO EML & Orange Book (policy/patent disputes),
  ATOMIC 2020 (encoded social/cultural norms).

---

*End of catalogue. Reconnaissance only — Fable designs and signs off. Nothing here is a decision.*
