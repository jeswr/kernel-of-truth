Verdict: **NEEDS-WORK** for the WordNet-10k pilot. The state model is closed, but the spend cap, provider idempotency, live economics, representative validator/storage evidence, and guardrail enforcement remain build-blocking.

1. **CONCERN — numeric go/no-go**

   The thresholds, repair limit, n=200 human sample, Wilson rules, abstention handling, and provider-failure bound are concrete ([spec:544](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:544), [spec:573](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:573)).

   However:

   - The claimed exact $500 maximum is not enforceable by recording actual cost after a call. Four concurrent online calls and especially a submitted ≤4,000-request Batch job can create unreserved liability beyond the remaining budget ([spec:552](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:552), [spec:559](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:559)). It needs an atomic pre-submit worst-case cost reservation, including whole Batch jobs.
   - “Worst-case spend ≡ $500 exactly” is incorrect; a sound cap is spend ≤ $500.
   - PROCEED requires only the four endpoints and never explicitly requires all 10,000 rows to reach a terminal state ([spec:582](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:582)). Add a terminal-accounting invariant such as `accepted + quarantined + provider_failed = 10,000`.

2. **CONCERN — clustering/worklist**

   The central clustering defect is closed: the pilot uses singleton synsets; future clustering is explicitly authored by the explicator and independently reviewed; the builder is benchmark/item/kernel-text blind ([spec:77](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:77), [spec:110](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:110)).

   But the sampling population is not reproducible. The spec attributes **110,049** type-level synsets to the WN manifest ([spec:91](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:91)); the manifest contains **117,791** records ([manifest:54](/home/ec2-user/css/kernel/kernel-of-truth/data/lexical-wn31/manifest.json:54)). The referenced F1K design obtains 110,049 only after excluding instance/named-individual and other records ([f1k spec:113](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/f1k-large-kernel-rebuild.md:113)), but this pilot does not specify or hash that filter.

3. **CONFIRMED — draft versus endorsed states**

   `ModelDrafted` is a separate immutable bucket; changes mint a new version, individual four-binary endorsement mints a new `Explicated` record, and sampled review never promotes unsampled drafts ([spec:145](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:145), [spec:163](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:163), [spec:172](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:172)). This matches the existing model-authored minting rule ([governance:54](/home/ec2-user/css/kernel/kernel-of-truth/data/haiku-tier/modelauthored-schema.md:54)).

4. **CONCERN — OpenAI cache/Batch economics**

   OpenAI cache keys, breakpoints, Batch limits, the input-only κ definition, the P/S/O micro-pilot, and output-dominance correction are present ([spec:216](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:216), [spec:288](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:288), [spec:336](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:336)).

   The cost model is nevertheless materially stale:

   - It uses $2/$0.20/$12 per million tokens ([spec:317](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:317)); current GPT-5.6 Sol pricing is $5/$0.50/$30.
   - GPT-5.6 cache writes cost 1.25× uncached input, but neither the economics nor cache-repopulation estimate includes that charge.

   These are current official provider semantics: [GPT-5.6 Sol pricing](https://developers.openai.com/api/docs/models/gpt-5.6-sol) and [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). At the spec’s own P/S/O assumptions, current prices multiply its principal estimates by roughly 2.5, making the $150–$290 expectation and $500 completion envelope unreliable.

5. **CONCERN — transactional idempotency**

   SQLite’s unique claim closes the two-local-worker race, but the provider crash window remains open ([spec:379](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:379), [spec:387](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:387)).

   OpenAI Batch `custom_id` is a per-input-file unique correlation identifier used to map results; it is not documented as a cross-submission deduplication key. Online response metadata is likewise not an idempotency primitive. Therefore, a crash after provider acceptance but before recording the returned ID can still lead to a duplicate paid submission. See the official [Batch guide](https://developers.openai.com/api/docs/guides/batch) and [Batch-list API](https://developers.openai.com/api/reference/resources/batches/methods/list).

   A sound design needs job-level transactional outbox rows and a verified provider idempotency/discovery mechanism for both Batch creation and online calls.

6. **CONCERN — validator and storage evidence**

   Bounded B=1,000 shards, catalog closure, vector dropping, and JSONL-gzip storage are well specified ([spec:409](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:409), [spec:430](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:430)).

   But the bounded shard has not been benchmarked: the only result is a 54-record whole-kernel run, while the representative 1,000-record benchmark remains future precondition P4 ([spec:418](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:418), [spec:423](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:423)). Likewise, record sizes come from 54 kernel-v0 records; the draft provenance increment and transcript sizes remain modeled rather than measured on `kernel-v1-draft/1` records ([spec:438](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:438)).

7. **CONCERN — mechanized guardrails**

   The provenance fields, frozen-overlap gate, status allowlist, and g9 exemplar ban are specified correctly ([spec:454](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:454), [spec:512](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:512), [spec:518](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:518), [spec:523](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:523)).

   The family-disjointness claim is not yet executable: the purported existing `poc/plainv5/invoke_seat.py`, `check_family_disjoint.py`, and `family-map.json` are absent from the workspace, although the referenced design names them as runtime machinery ([referenced design:294](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/plain-v5-register-lint-spec.md:294)). Also, provenance records `authorFamily: "gpt"` ([spec:464](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/gpt56-draft-pipeline-large-kernel.md:464)), while the referenced resolver maps GPT IDs to `"openai"` ([family-map design:275](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/plain-v5-register-lint-spec.md:275)). The pilot preconditions need explicit implementation and fail-path tests for FD-1/2/5/6 and `ERR_STATUS_INELIGIBLE`.

**Final verdict: NEEDS-WORK.** The minimum blockers to GO-TO-BUILD are: atomic pre-submit budget reservation plus full-10k terminal accounting; current GPT-5.6 pricing/cache-write economics; a real provider-safe idempotency protocol; explicit WordNet population filtering; representative shard/record-size measurements; and implementation/test preconditions for the guardrails.

Read-only review; no files were changed.