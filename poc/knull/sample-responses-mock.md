# knull plain-store sample responses - ACTUAL small-model outputs, v3 vs v4

> **MOCK TRANSPORT SMOKE** - every 'output' below is a stub;
> NO model was loaded and NOTHING here is a generation. This
> file exists only to prove the transport + rendering path.

> STATUS: **PROVISIONAL, illustrative**. Every response below is the
> RAW, UNEDITED output of an actual model generation - nothing is
> paraphrased, cherry-picked among samples, or re-rolled (greedy
> decoding admits exactly one output per input). These are
> small-model generations for illustration of how the two control
> stores read in use; they are NOT verdict-bearing and NOT part of
> any pre-registered Phase-X harness.
>
> **Model:** `HuggingFaceTB/SmolLM2-360M-Instruct` | **Decoding:** MOCK (no decoding performed), max_new_tokens=200, dtype=float32,
> device=cpu, stop=eos, seed: torch_manual_seed=0 (greedy: seed inert).
>
> **Context design:** per-prompt fixed label set, identical across arms; store entries rendered as a reference list in the system message; headwords shown (usage illustration, not the blind gate)
>
> **v3 store:** `poc/knull/inputs-v3/plain-authored.json` sha256 `8812f91e708f7cd5b0905bf5c95af1affcf83504f503225dcd0d8dbc0c774b1d`
> **v4 store:** `poc/knull/inputs-v4/plain-authored.json` sha256 `97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2`
>
> Generated 2026-07-11 by the Fable agent session (maintainer issue 17).
> Harness: poc/knull/modal/modal_knull_samples.py via Modal CPU (prompt set + context design single-sourced from run_sample_responses.py; image from the pinned f2b requirements, reuse pin im-6uXR6RyVQV15h2B3gtpOG2)
> Model revision pin: `a10cc1512eabd3dde888204e902eca88bddb4951`.

The v3 store is the Option-B concise store that FAILED the ASM-0703
gate on set-level template monotony (GPT-5.6 8/10, Haiku 4/10); the
v4 store is the frame-variation re-authoring (option A). Each prompt
below is answered twice by the same model under identical settings;
the ONLY changed bytes between the two runs are the injected
definition texts (same concept labels in both arms).

---

## 1. My friend's father just died. What should I say to her?

*Injected store entries (same labels, both arms):* `condolence (the words)`, `grieving`, `death (the event)`, `friend (X is a friend of Y)`, `father`, `sad`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (549 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (562 chars) but no model was loaded]
```

---

## 2. What is the difference between a lie and a promise?

*Injected store entries (same labels, both arms):* `lie (the words)`, `promise (the words)`, `liar`, `trustworthy`, `believe (X believes Y)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (431 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (520 chars) but no model was loaded]
```

---

## 3. Is a fish an animal? Explain briefly.

*Injected store entries (same labels, both arms):* `fish`, `animal`, `alive`, `water`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (432 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (432 chars) but no model was loaded]
```

---

## 4. I archived a bookmark by accident. Is it gone forever?

*Injected store entries (same labels, both arms):* `archived (bookmark boolean property)`, `bookmark`, `lost`, `find (X finds Y)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (411 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (457 chars) but no model was loaded]
```

---

## 5. Could my cat have been a dog instead? What kind of thing is a cat?

*Injected store entries (same labels, both arms):* `kind (gufo:Kind, sortal type)`, `cat`, `dog`, `animal`, `change (the event)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (612 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (628 chars) but no model was loaded]
```

---

## 6. How is running different from walking?

*Injected store entries (same labels, both arms):* `run`, `walk`, `jump`, `ground`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (358 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (416 chars) but no model was loaded]
```

---

## 7. Why do people celebrate when a baby is born?

*Injected store entries (same labels, both arms):* `celebration`, `birth (the event)`, `happy`, `gift`, `event`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (456 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (502 chars) but no model was loaded]
```

---

## 8. What makes someone a good teacher?

*Injected store entries (same labels, both arms):* `teacher`, `learn (X learns Y)`, `help (X helps Y)`, `helpful (of a someone)`, `remember (X remembers Y)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v3 store (479 chars) but no model was loaded]
```

### with the v4 store (frame-variation retry)

```text
[MOCK transport smoke - NOT a model generation; context was built from the real v4 store (552 chars) but no model was loaded]
```

---

*End of illustrative sample set (8 prompts x 2 stores = 16 stub placeholders (MOCK)).
Raw JSON with shas: `poc/knull/sample-responses-mock.json`.*
