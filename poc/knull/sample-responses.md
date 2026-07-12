# knull plain-store sample responses - ACTUAL small-model outputs, v3 vs v4

> STATUS: **PROVISIONAL, illustrative**. Every response below is the
> RAW, UNEDITED output of an actual model generation - nothing is
> paraphrased, cherry-picked among samples, or re-rolled (greedy
> decoding admits exactly one output per input). These are
> small-model generations for illustration of how the two control
> stores read in use; they are NOT verdict-bearing and NOT part of
> any pre-registered Phase-X harness.
>
> **Model:** `HuggingFaceTB/SmolLM2-360M-Instruct` | **Decoding:** greedy (do_sample=False), max_new_tokens=200, dtype=float32,
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
You can say something like, "I'm so sorry to hear that your father has passed away. I'm here for you, and I'm going to be with you in this difficult time." This acknowledges her loss and lets her know you're there to support her.
```

### with the v4 store (frame-variation retry)

```text
You can say something like:

"I'm so sorry to hear that your friend's father has passed away. I'm here for you, and I'm sure you'll be okay. Please know that I'm here for you, and I'll do everything I can to support you through this difficult time."
```

---

## 2. What is the difference between a lie and a promise?

*Injected store entries (same labels, both arms):* `lie (the words)`, `promise (the words)`, `liar`, `trustworthy`, `believe (X believes Y)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
A lie and a promise are both false statements, but they differ in their intent and the circumstances under which they are made.

A lie is a false statement made with the intention of deceiving or misleading someone. It is a deliberate act of deception, often with the goal of getting something from the person or gaining an advantage. Lies can be made with the intention of hurting someone, damaging their reputation, or gaining power.

A promise, on the other hand, is a binding assurance that one will do, or refrain from doing, a stated thing. It is a commitment or agreement to perform a certain action, and it is often made with the intention of helping someone or achieving a shared goal. Promises are typically made with the intention of building trust, establishing a relationship, or achieving a common objective.

To illustrate the difference, consider the following example:

- A person lies to get a job offer because they want to get the job. They make a
```

### with the v4 store (frame-variation retry)

```text
A lie and a promise are both assertions known by their speaker to be false, but they differ in their intent and the way they are delivered.

A lie is an assertion known by its speaker to be false and meant to deceive others. It is a deliberate attempt to mislead or mislead others into believing something that is not true. Lies are often used to manipulate or deceive others, and they can be damaging to relationships and reputations.

A promise, on the other hand, is an assurance, binding on the giver, to do or forbear some stated thing. It is an assurance that is not meant to deceive others, but rather to bind them to a particular action or commitment. Promises are often made with the intention of helping others, and they can be a way of building trust and strengthening relationships.

In other words, a lie is a form of deception, while a promise is a form of trust. A promise is a promise to do or not
```

---

## 3. Is a fish an animal? Explain briefly.

*Injected store entries (same labels, both arms):* `fish`, `animal`, `alive`, `water`

### with the v3 store (Option-B concise, gate-FAILED)

```text
Yes, a fish is an animal. Fish are cold-blooded, water-dwelling animals that breathe through gills and swim with fins. They are a part of the animal kingdom and are classified as vertebrates.
```

### with the v4 store (frame-variation retry)

```text
Yes, a fish is an animal. Fish are cold-blooded animals that live in water and have gills for breathing and fins for swimming. They are also considered to be a part of the animal kingdom.
```

---

## 4. I archived a bookmark by accident. Is it gone forever?

*Injected store entries (same labels, both arms):* `archived (bookmark boolean property)`, `bookmark`, `lost`, `find (X finds Y)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
Yes, it is gone forever.
```

### with the v4 store (frame-variation retry)

```text
Yes, it is gone forever.
```

---

## 5. Could my cat have been a dog instead? What kind of thing is a cat?

*Injected store entries (same labels, both arms):* `kind (gufo:Kind, sortal type)`, `cat`, `dog`, `animal`, `change (the event)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
Yes, your cat could have been a dog instead. The kind of thing that could be a cat is a cat. A cat is a kind of animal, specifically a domestic animal that belongs to the species Felis catus. It is a small, domesticated carnivorous mammal with soft fur, retractile claws, and whiskers.
```

### with the v4 store (frame-variation retry)

```text
Yes, your cat could have been a dog instead. The kind of thing that could be a cat is a cat. A cat is a kind of animal, specifically a domestic carnivore, which belongs to the category of animals that feed on organic matter and move under their own power.
```

---

## 6. How is running different from walking?

*Injected store entries (same labels, both arms):* `run`, `walk`, `jump`, `ground`

### with the v3 store (Option-B concise, gate-FAILED)

```text
Running is a faster pace than walking, and it involves using your legs to propel yourself forward. When you run, you are constantly moving your legs forward, and your body is in a state of continuous motion. This is in contrast to walking, where you are moving your legs in a more relaxed manner, with your body moving in a more fluid and continuous way.

In addition, running requires more energy than walking, as you are constantly using your legs to propel yourself forward. This means that running can be more exhausting than walking, especially if you are not used to running.

Overall, running is a faster and more intense form of locomotion than walking, and it requires more energy and effort to maintain.
```

### with the v4 store (frame-variation retry)

```text
Running and walking are both forms of locomotion, but they differ in speed, pace, and the way the body moves. Running involves moving at a faster pace, with the feet leaving the ground in each stride, while walking involves moving at a slower pace, with the feet always touching the ground.

In running, the body moves forward with a greater acceleration, propelling itself forward with each step. This results in a faster pace, as the feet leave the ground more quickly. In contrast, walking is a more leisurely pace, with the feet always touching the ground, allowing for a more relaxed and steady movement.

Additionally, running requires more energy and can be more exhausting, as the body must generate more force to propel itself forward. Walking, on the other hand, is a more efficient form of locomotion, requiring less energy and allowing for a more relaxed pace.
```

---

## 7. Why do people celebrate when a baby is born?

*Injected store entries (same labels, both arms):* `celebration`, `birth (the event)`, `happy`, `gift`, `event`

### with the v3 store (Option-B concise, gate-FAILED)

```text
People celebrate when a baby is born because it marks the beginning of a new life, a new chapter in a person's life, and a new beginning. Birth is a significant event that signifies the arrival of a new life, and it is a time for people to come together, share in the joy, and celebrate the new addition to their family.
```

### with the v4 store (frame-variation retry)

```text
People celebrate when a baby is born because it marks the beginning of a new life, bringing joy and happiness to the family and community. Birth is a significant event that signifies the arrival of a new person into the world, and it is a time for celebration and gratitude.
```

---

## 8. What makes someone a good teacher?

*Injected store entries (same labels, both arms):* `teacher`, `learn (X learns Y)`, `help (X helps Y)`, `helpful (of a someone)`, `remember (X remembers Y)`

### with the v3 store (Option-B concise, gate-FAILED)

```text
A good teacher is someone who possesses certain qualities that enable them to effectively instruct and guide their students. Some of these qualities include:

A strong foundation in the subject matter, which allows them to provide clear and accurate information to their students. A good teacher also possesses excellent communication skills, which enables them to explain complex concepts in a way that is easy to understand.

Additionally, a good teacher is able to inspire and motivate their students, helping them to develop a love for learning and a desire to succeed. They are also able to adapt to different learning styles and needs, providing a variety of teaching methods to suit each student's individual needs.

Good teachers are also able to create a positive and supportive learning environment, where students feel encouraged and motivated to learn. They are able to foster a sense of community and camaraderie among their students, which helps to build a strong foundation for future learning.

Finally, a good teacher is able to provide ongoing feedback and support to their students
```

### with the v4 store (frame-variation retry)

```text
A good teacher is someone who possesses a combination of qualities that enable them to effectively instruct and guide their students in various subjects. Some of the key characteristics of a good teacher include:

They are knowledgeable and passionate about their subject matter, which allows them to provide engaging and relevant lessons that inspire students to learn. They are also able to communicate effectively with their students, using clear and concise language to explain complex concepts and make them accessible to all.

Good teachers are also able to create a supportive and inclusive learning environment, where students feel comfortable asking questions, sharing their thoughts, and taking risks. They are also able to adapt their teaching methods to meet the needs of their students, whether that means using different teaching styles, providing additional support, or offering different types of assessments.

Additionally, good teachers are able to help their students develop a love for learning, which can lead to a lifelong commitment to education. They are also able to foster critical thinking, problem-solving, and creativity
```

---

*End of illustrative sample set (8 prompts x 2 stores = 16 actual generations).
Raw JSON with shas: `poc/knull/sample-responses.json`.*
