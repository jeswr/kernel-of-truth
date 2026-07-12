#!/usr/bin/env python3
"""DIAGNOSTIC probe (never a measurement): rank the gold option among the 23
menu words under frame variants, using the runner's OWN prompt builder and
the f2bt _option_logprobs scorer bytes, on the PINNED models.

ROOT-parameterised via KOT_ROOT (defaults to the EC2 checkout) so the same
bytes run locally and inside the Modal container layout (/root/kot).

Variants:
  asbuilt   - the exact A1/A5 alone-arm prompt (padding between Question and cue)
  nopad     - same prompt, padding omitted (A7 shape minus injection)
  padabove  - padding block moved ABOVE the Question (inside the facts region)
  chat      - nopad prompt wrapped in the tokenizer chat template (user turn),
              cue rendered as the start of the assistant turn (nsk1/g2 channel)
  chatpad   - padabove + chat template (candidate fixed A1/A5 frame)
"""
import json, os, sys, argparse

ROOT = os.environ.get("KOT_ROOT", "/home/ec2-user/css/kernel/kernel-of-truth")
HERE = os.path.join(ROOT, "poc", "rules-1")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "poc", "f2b-transfer", "runner"))
os.chdir(HERE)
import rules1_runner as R

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--revision", required=True)
ap.add_argument("--dtype", default="fp32")
ap.add_argument("--device", default="cpu")
ap.add_argument("--n", type=int, default=6)
ap.add_argument("--variants", default="asbuilt,nopad,padabove,chat,chatpad")
args = ap.parse_args()

class A: pass
a = A(); a.inputs_dir = "inputs"; a.data_root = os.path.join(ROOT, "data")
man = json.load(open("inputs/rules1-manifest.json"))
items, ctx = R.build_context(a, man)
covered = [i for i in items if i["stratum"] == "covered"][:args.n]
frames = man["prompt_frames"]

lm = R.Rules1HFLM(args.repo, args.revision, args.device, dtype=args.dtype)
menu = ctx["menu"]

def alone_prompt(it, pad=True):
    iid = it["item_id"]
    pay = ctx["payload_true"][iid]
    names, stated = ctx["names"][iid], ctx["stated"][iid]
    aq, bq = ctx["pair"][iid]
    pn = (names.get(aq, aq), names.get(bq, bq))
    inj = R.a2_shaped_injection(pay, names, ctx["urn2word"])
    if not pad:
        return R.build_prompt(frames, it, stated, names, ctx["urn2word"],
                              menu, pair_names=pn), pn
    target = lm.count_tokens(R.build_prompt(
        frames, it, stated, names, ctx["urn2word"], menu,
        derived_lines=inj, pair_names=pn))
    return R.build_prompt(frames, it, stated, names, ctx["urn2word"], menu,
                          pad_to_tokens=target, lm=lm, pair_names=pn), pn

def move_pad_above_question(p):
    """String surgery: relocate the padding block from between Question and
    cue to just above the Question line."""
    qmark = "\nQuestion: "
    lines = p.split("\n")
    padline = frames["padding_sentence"]
    padblock = [l for l in lines if padline in l]
    rest = [l for l in lines if padline not in l]
    p2 = "\n".join(rest)
    if not padblock:
        return p2
    return p2.replace(qmark, "\n" + "\n".join(padblock) + qmark, 1)

def chat_ids(prompt_body, cue):
    """nsk1/g2 channel: prompt body as the user turn, cue starts the
    assistant turn."""
    msgs = [{"role": "user", "content": prompt_body}]
    pre = lm.tok.apply_chat_template(msgs, add_generation_prompt=True)
    cue_ids = lm.tok.encode(cue.lstrip("\n"), add_special_tokens=False)
    return list(pre) + cue_ids

def score_ids(pre_ids, options):
    torch = lm.torch
    outs = []
    with torch.no_grad():
        for opt in options:
            oids = lm.tok.encode(opt, add_special_tokens=False)
            ids = torch.tensor([pre_ids + oids], device=lm.device)
            logits = lm.model(ids).logits[0]
            lp = torch.log_softmax(logits[:-1].float(), dim=-1)
            tgt = ids[0, 1:]
            start = len(pre_ids) - 1
            outs.append(float(lp[start:, :].gather(1, tgt[start:, None]).sum()))
    return outs

def story_prompt(it, cue):
    """nsk1 premise channel content: the ORIGINAL CLUTRR story replaces the
    verbalised stated-fact lines; menu header, question and infill cue
    unchanged (f2bt forced-choice scorer unchanged)."""
    story = "\n".join(it["context"])
    parts = [frames["task_prefix"].format(menu=", ".join(menu))]
    parts.append(story + "\n")
    parts.append(frames["question_prefix"] + it["question"])
    return "".join(parts) + cue

def facts_story_prompt(it, cue, names, stated):
    """Both surfaces: story first, then the verbalised stated facts."""
    story = "\n".join(it["context"])
    parts = [frames["task_prefix"].format(menu=", ".join(menu))]
    parts.append(story + "\n\nFacts:\n")
    for line in R.stated_lines(stated, names, ctx["urn2word"]):
        parts.append(frames["fact_line"].format(line=line))
    parts.append(frames["una_line"])
    parts.append(frames["question_prefix"] + it["question"])
    return "".join(parts) + cue

def ent_inj_variant(it, iid, names, stated, gold, v):
    """Entity-form A7 injection probe: full one-line proof (as-built) vs the
    bare derived fact — isolates proof-chain bridge-capture at the R1 host."""
    aq, bq = ctx["pair"][iid]
    base, top = names[aq], names[bq]
    opts = sorted(s for u, s in it["lexicon"].items() if u != aq)
    q2 = "Who is the %s of %s?" % (gold, base)
    pay = ctx["payload_true"][iid]
    if v in ("entinj", "entinjonlyproof"):
        inj = R.a2_shaped_injection(pay, names, ctx["urn2word"])
    else:
        inj = [R.verbalise_fact(tuple(pay.why["fact"]), names,
                                ctx["urn2word"]) + "."]
    if v in ("entinjonly", "entinjonlyproof"):
        # render-only A7: the engine answered; the LM merely renders — the
        # stated-facts block is dropped so no bridge-frequency prior exists
        cue2 = frames["answer_cue"].format(rel=gold, a_name=base)
        p = (frames["task_prefix"].replace("the family facts",
                                           "the verified derivation")
             .replace("\n\nFacts:\n", "\n\n")
             + frames["derived_prefix"]
             + "".join(frames["derived_line"].format(line=l) for l in inj)
             + frames["question_prefix"] + q2 + cue2)
    else:
        p = R.build_prompt(frames, q2, stated, names, ctx["urn2word"],
                           derived_lines=inj, a_name=base, rel_word=gold)
    lps = lm._option_logprobs(p, [" %s" % s for s in opts])
    pick = opts[max(range(len(opts)), key=lambda j: lps[j])]
    return pick, top, ["%s:%.2f" % (o, l) for o, l in zip(opts, lps)]

variants = args.variants.split(",")
summary = {v: 0 for v in variants}
for it in covered:
    gold = it["gold_relation"]
    iid = it["item_id"]
    names, stated = ctx["names"][iid], ctx["stated"][iid]
    legacy = [v for v in variants if not v.startswith("ent")]
    if legacy:
        p_pad, pn = alone_prompt(it, pad=True)
        p_nop, _ = alone_prompt(it, pad=False)
        cue = frames["answer_cue"].format(a_name=pn[0], b_name=pn[1])
        body_nop = p_nop[: p_nop.rfind(cue)]
        p_above = move_pad_above_question(p_pad)
        body_above = p_above[: p_above.rfind(cue)]
    else:
        cue = ""
    print("== %s gold=%s cue=%r" % (it["item_id"], gold, cue.strip()), flush=True)
    for v in variants:
        if v in ("entinj", "entinjbare", "entinjonly", "entinjonlyproof"):
            pick, top, lps = ent_inj_variant(it, iid, names, stated, gold, v)
            hit = pick.lower() == top.lower()
            summary[v] += hit
            print("  %-11s pick=%r gold=%r hit=%d lps=%s"
                  % (v, pick, top, hit, lps), flush=True)
            continue
        if v == "asbuilt":
            lps = lm._option_logprobs(p_pad, [" %s" % w for w in menu])
        elif v == "nopad":
            lps = lm._option_logprobs(p_nop, [" %s" % w for w in menu])
        elif v == "padabove":
            lps = lm._option_logprobs(p_above, [" %s" % w for w in menu])
        elif v == "chat":
            lps = score_ids(chat_ids(body_nop, cue), [" %s" % w for w in menu])
        elif v == "chatpad":
            lps = score_ids(chat_ids(body_above, cue), [" %s" % w for w in menu])
        elif v == "story":
            lps = lm._option_logprobs(story_prompt(it, cue),
                                      [" %s" % w for w in menu])
        elif v == "factstory":
            lps = lm._option_logprobs(facts_story_prompt(it, cue, names, stated),
                                      [" %s" % w for w in menu])
        elif v == "storychat":
            sp = story_prompt(it, cue)
            lps = score_ids(chat_ids(sp[: sp.rfind(cue)], cue),
                            [" %s" % w for w in menu])
        elif v in ("nsk1gen", "factsgen", "factsgencue"):
            # EXACT nsk1/g2 channel (modal_nsk1_g2.py): chat template + greedy
            # generate(16) + first-vocab-word extraction. nsk1gen = original
            # story + nsk1 instruction line; factsgen = same instruction over
            # the rules-1 verbalised facts; factsgencue = facts + the
            # direction-explicit infill cue ending the user message.
            import re as _re
            torch = lm.torch
            instr = ("Answer with exactly one word naming the family "
                     "relationship, chosen from this list: %s. Answer:"
                     % ", ".join(menu))
            if v == "nsk1gen":
                body = "Story:\n%s\nQuestion: %s\n%s" % (
                    "\n".join(it["context"]), it["question"], instr)
            else:
                facts = "".join(frames["fact_line"].format(line=l)
                                for l in R.stated_lines(stated, names,
                                                        ctx["urn2word"]))
                facts += frames["una_line"]
                if v == "factsgen":
                    body = "Facts:\n%s\nQuestion: %s\n%s" % (
                        facts, it["question"], instr)
                else:
                    body = ("Facts:\n%s\nQuestion: %s\n%s %s" % (
                        facts, it["question"], instr, cue.strip()))
            msgs = [{"role": "user", "content": body}]
            ids = lm.tok.apply_chat_template(msgs, add_generation_prompt=True,
                                             return_tensors="pt").to(lm.device)
            with torch.no_grad():
                gen = lm.model.generate(ids, max_new_tokens=16,
                                        do_sample=False, num_beams=1,
                                        pad_token_id=lm.tok.eos_token_id)
            text = lm.tok.decode(gen[0][ids.shape[1]:],
                                 skip_special_tokens=True)
            low = text.lower()
            best_pos, best_word = None, None
            for w in menu:
                m = _re.search(r"(?<![a-z-])%s(?![a-z-])" % _re.escape(w.lower()), low)
                if m and (best_pos is None or m.start() < best_pos):
                    best_pos, best_word = m.start(), w
            hit = best_word == gold
            summary[v] += hit
            print("  %-11s first_word=%r hit=%d gen=%r"
                  % (v, best_word, hit, text[:60]), flush=True)
            continue
        elif v in ("entfc", "entgen", "entgenstory"):
            # ENTITY FORM (the g2/bprime capability window: 1.7B 0.76/0.7912):
            # question 'Who is the <gold_rel> of <base>?', answer = chain-top
            # NAME. entfc = rules-1 stated facts + f2bt forced choice over the
            # non-base lexicon names; entgen = same facts, nsk1 chat+generate
            # channel + anti-echo first-name scorer; entgenstory = the exact
            # g2b form-2 text-only cell (story) as positive control.
            import re as _re
            torch = lm.torch
            aq, bq = ctx["pair"][iid]
            base_surface = names[aq]           # A of the query pair
            top_surface = names[bq]            # gold: B (engine-derived)
            surfaces = list(it["lexicon"].values())
            q2 = "Who is the %s of %s?" % (gold, base_surface)
            facts = "".join(frames["fact_line"].format(line=l)
                            for l in R.stated_lines(stated, names,
                                                    ctx["urn2word"]))
            facts += frames["una_line"]
            if v == "entfc":
                opts = [s for s in surfaces
                        if s.lower() != base_surface.lower()]
                body = ("Read the family facts, then answer the question "
                        "with exactly one name.\n\nFacts:\n%s\nQuestion: %s"
                        "\nAnswer: the %s of %s is" % (facts, q2, gold,
                                                       base_surface))
                lps = lm._option_logprobs(body, [" %s" % s for s in opts])
                pick = opts[max(range(len(opts)), key=lambda j: lps[j])]
                hit = pick.lower() == top_surface.lower()
                summary[v] += hit
                print("  %-11s pick=%r gold=%r hit=%d lps=%s"
                      % (v, pick, top_surface, hit,
                         ["%s:%.2f" % (o, l) for o, l in zip(opts, lps)]),
                      flush=True)
                continue
            instr_ent = ("Answer with exactly one word: the name of the "
                         "person. Answer:")
            if v == "entgen":
                body = "Facts:\n%s\nQuestion: %s\n%s" % (facts, q2, instr_ent)
            else:
                body = "Story:\n%s\nQuestion: %s\n%s" % (
                    "\n".join(it["context"]), q2, instr_ent)
            msgs = [{"role": "user", "content": body}]
            ids = lm.tok.apply_chat_template(msgs, add_generation_prompt=True,
                                             return_tensors="pt").to(lm.device)
            with torch.no_grad():
                gen = lm.model.generate(ids, max_new_tokens=16,
                                        do_sample=False, num_beams=1,
                                        pad_token_id=lm.tok.eos_token_id)
            text = lm.tok.decode(gen[0][ids.shape[1]:],
                                 skip_special_tokens=True)
            low = text.lower()
            best_pos, best_surf = None, None
            for s in surfaces:
                if s.lower() == base_surface.lower():
                    continue
                m = _re.search(r"(?<![a-z])%s(?![a-z])" % _re.escape(s.lower()), low)
                if m and (best_pos is None or m.start() < best_pos):
                    best_pos, best_surf = m.start(), s
            hit = (best_surf is not None
                   and best_surf.lower() == top_surface.lower())
            summary[v] += hit
            print("  %-11s pick=%r gold=%r hit=%d gen=%r"
                  % (v, best_surf, top_surface, hit, text[:60]), flush=True)
            continue
        order = sorted(range(len(menu)), key=lambda j: -lps[j])
        rank = order.index(menu.index(gold)) + 1
        top3 = ["%s:%.2f" % (menu[j], lps[j]) for j in order[:3]]
        hit = rank == 1
        summary[v] += hit
        print("  %-9s rank(gold)=%2d top1hit=%d top3=%s" % (v, rank, hit, top3),
              flush=True)
print("\n== SUMMARY (top-1 hits / %d items):" % len(covered))
for v in variants:
    print("  %-9s %d/%d" % (v, summary[v], len(covered)))
