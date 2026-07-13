# Programme steering read (GPT-5.6, 2026-07-13) — coordinator-transcribed

> GPT-5.6 (codex, xhigh) candid subjective read per the dual-model-analysis directive. A Fable read
> will be added + synthesized when a lane frees. Labelled opinion, not a verdict; drives the next wave.

## Opinion, not verdict

My overall read is that the programme has established a useful engineering proposition—authoritative content plus deterministic machinery can help models—but has not established the distinctive scientific proposition that the kernel’s formal structure is what creates the benefit. That attribution gap is now the programme’s central question.

### 1. Honest status of both theses

**CORRECTNESS: positive on the weaker content thesis; genuinely open, with an adverse lean, on kernel-specific structure.**

The strongest evidence is the conjunction of f2b-transfer and DECONF-B: item-aligned authored content lifted accuracy by about 25 points, while a generic aligned store reproduced the kernel arm. RULES-2 then showed that engine-derived entailments can be internalised by a 135M host, but the kernel and plain-dictionary rules sources produced a byte-identical 21,780-example training corpus. These are real, audit-confirmed positives—and four distinct “content, not structure” readings. [README](README.md:29), [RULES-2 interpretation](docs/next/analysis/rules2-interpretation.md:204)

The adverse evidence is no longer negligible. The g3 necessity FAIL survives a full Opus Pass-B re-judge: 39/193 violations, LB95 0.1588 above the 0.10 kill bar. It remains an LLM-judged result rather than full human gold, but the Haiku-artifact explanation has been tested and refuted. That lowers my prior on the current hand-authored explications being reliably necessary descriptions of ordinary concepts. [g3 reconciliation](docs/next/analysis/g3-human-proxy-reconciliation.md:44)

nsk1 is a genuine mechanism observation, but not an accuracy result: item-specific content is readable internally at 0.81–0.85 keyed accuracy, yet the subsequent free-generation probe found no low-damage keying window and bounded the echo-proof net rescue near zero under this operator. The honest state is “delivery exists; useful integration unresolved,” not a correctness positive. [nsk1 interpretation](docs/next/interpretations/nsk1-bprime.md:100)

So my subjective label is: **CORRECTNESS is inconclusive, leaning sceptical specifically about kernel-specific structure, while the weaker content/tooling thesis is already supported.**

**EFFICIENCY: speculative, not merely incomplete.**

There is still no thesis-bearing live efficiency result. The GLM-5.2 probe establishes valuable physics: expert reads consume roughly 75% of decode time; uniform top-k reduction cut expert loads from 1,825 to 999/606 per token and produced preliminary 1.9×/2.5× throughput observations. But that is a **kernel-free** lever, so it raises the bar rather than supporting the thesis. [probe log](poc/glm52-probe/results/probe-main.log:9)

The routing signal is strong—mean-centred within-concept similarity 0.9119 versus −0.0740 across, permutation p=0.0001—but it is not yet kernel-specific. Generic embedding clusters are an entirely plausible explanation. [routing analysis](poc/glm52-probe/results/routing-analysis-v2.json:14)

My subjective label is: **EFFICIENCY remains high-risk and evidence-poor. The hardware opportunity is real; the kernel contribution is unmeasured.**

### 2. What is going well and poorly

Going well:

- The programme’s strongest results survive serious controls and cross-vendor audits. The f2b/DECONF content lift, RULES-1 certificate, and RULES-2 internalisation result are load-bearing.

- The deflator discipline is working. It has repeatedly prevented generic content, formatting, or routing structure from being misreported as kernel-specific value.

- Instrument hygiene has improved materially. The blocking pilot helped RULES-2 remove invalid interfaces before the campaign.

- The GLM probe and scale census converted vague architectural hopes into useful engineering facts: disk-bound MoE decode, measurable routing structure, 207,733 unmerged type-level candidates, and a domain-balanced 191,301-record typed core. [scale census](poc/scale/results/scale-s1-census.md:13)

Going poorly:

- The affirmative findings repeatedly dissolve at the attribution boundary: helpful content, but no demonstrated need for kernel structure.

- The cleanest structure-sensitive tests do not reach the treatment question. E0 lacked operator/inventory adequacy; frozen F1-K had only 49 realised clusters and 46 with \(m\ge8\), against 65 required. [F1-K shortfall](docs/next/design/f1k-power-shortfall-options.md:11)

- The current concept inventory is not merely an inconveniently small sample. It is too small and too thinly connected to independent evaluation items to support the programme’s intended claims. Raw imported ontology rows do not solve that: F1-K needs reviewed explications, dictionary controls, trigger surfaces, QA coverage, and balanced independent concept clusters.

- The resource bottleneck is therefore not chiefly GPU or account capacity. It is **validated experimental inventory**: concept breadth, semantic quality, test-item density, and human audit.

I do think the repeated inventory stops tell us something substantive about present scope: **kernel-v0 is a useful hand-built demonstration object, not yet a general semantic substrate.** They do not refute a larger kernel, but they refute treating the present one as representative enough to answer the programme’s flagship questions.

### 3. Path ranking

| Rank | Path | Expected payoff versus cost/risk |
|---|---|---|
| 1 | **Targeted large-kernel powered F1-K successor** | Highest correctness payoff. It can test whether a grounded carrier works at a frontier-model seam and whether correct concept alignment beats dose-exact derangement. High preparation cost, but it addresses the actual inventory failure. |
| 2 | **GLM expert-drop—only after expanding trace clusters** | Best efficiency route, because it directly compares kernel guidance with uniform, frequency, embedding, and deranged controls. As written at \(C=8\), however, its simulated 80% MDE is about **16 points** and power at a true +3 is 0.119; I would not spend the main campaign on that geometry. [power analysis](docs/next/design/glm52-expert-drop.md:862) |
| 3 | **nsk1 R3/new operator** | Cheap, and the channel-existence result is real. But Stage-1 already found keying and damage co-attenuate, with no demonstrated end-task integration. Worth only a tightly capped deconfounded-operator pilot, not flagship weight. |
| 4 | **Full large-kernel scale track as a standalone programme** | Important infrastructure, poor near-term verdict return. S0/S1 explicitly cannot produce a thesis verdict; the full 100k work is estimated at weeks of crosswalk/audit engineering. Use a targeted subset for F1-K and GLM-DROP rather than completing the entire scale programme first. [S0 interpretation](docs/next/analysis/scale-s0-interpretation.md:251) |

One important qualification: registered F1-K PASS requires K-1 and K-2, while the hard kernel-vs-plain-dictionary K-3 comparison is only secondary. A PASS can therefore still leave kernel-specific structure unresolved. If the rebuild is meant to settle that question, **make K-3 verdict-bearing or co-primary in the successor**. [F1-K ladder](registry/experiments/f1k.json:135)

### 4. What I would change and prioritise

1. **Build one targeted experimental inventory, not a general 100k kernel.** Select perhaps 80–100 benchmark-blind concepts from the large typed core, with reviewed explications, dictionary controls, trigger surfaces, and demonstrated QA density. Target substantial headroom over 65 clusters, not exactly 65.

2. **Add a pre-spend “is the structure question actually askable?” gate.** On dev-only data, require:

   - kernel and dictionary carriers to be materially distinct;
   - kernel and deranged carriers to induce distinct logits at the selected splice;
   - for GLM-DROP, kernel masks to differ materially from embedding, frequency, and deranged masks;
   - adequate cluster count under exact re-powering.

   If kernel and knull artifacts are behaviourally identical—as in RULES-2—stop before the main campaign.

3. **Collect more GLM routing fingerprints while the instance is available.** More items cannot overcome GLM-DROP’s eight-cluster floor; more independent trace clusters can. The existing probe suggests this is relatively cheap compared with the 68–279 instance-hour campaign.

4. **Freeze F1-K and GLM-DROP together, then run them serially on one spot instance.** F1-K first; GLM-DROP second under the existing isolation firewall. This maximises reuse without mixing outcomes.

5. **Do not fund a broad nsk1 R3 campaign.** Permit only a small pilot of a genuinely new operator that demonstrates all three simultaneously: preserved keying, low correct-answer breakage, and an echo-proof generation effect. Otherwise record-and-redirect.

6. **Make efficiency measurable as efficiency.** GLM-DROP currently treats loads/token as its only systems endpoint and declines causal throughput measurement. Add a balanced, replicated latency/throughput protocol plus an end-to-end cost ledger. Without that, even D1∧D2 is a correctness-preservation result at matched load—not a full efficiency verdict. [GLM-DROP regimes](docs/next/design/glm52-expert-drop.md:723)

### 5. Honest feasibility outlook

These are subjective probabilities, not statistical posteriors:

- **CORRECTNESS:** about **30%** probability of a defensible kernel-specific positive within the present resource envelope; perhaps **60–70%** for another positive showing that kernel-authored or engine-derived content helps. The latter is no longer the disputed question. A real positive needs a powered F1-K successor, K-3 promoted into the verdict, adequate concept diversity, and no repeat of g3-style semantic-quality failures.

- **EFFICIENCY:** about **15%** probability of a defensible positive under the current GLM-DROP design, perhaps **25–30%** after expanding trace clusters and adding causal throughput/economics endpoints. A thesis-level claim about favourable end-to-end economics is presently below **10%**, because mapping, authoring, storage, update, and serving costs remain unpriced.

The most likely failure mode for both theses is not a clean negative verdict. It is another scoped positive or non-demonstration that still cannot cross the kernel-specificity or economics boundary. The next wave should be designed explicitly to prevent that outcome.
