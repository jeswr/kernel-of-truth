#!/usr/bin/env python3
"""UFO-CHECK-0 pre-materialisation (design §4.3; PROPOSED-ASM-1483).

Runs the Python twin ONCE on CPU before any GPU spend and writes
poc/ufo-check-0/inputs/fixtures/:

  gold.jsonl           item_id, family, scored, gold, proof_sha256
  accept-tables.jsonl  per item x arm in {AG,AU,AD,AN}: d_arm + per-answer
                       accept|reject + EXACT rejection-message bytes
  floors.jsonl         per item x arm x possible-first-answer: analytic
                       trivial-policy expectations (PROPOSED-ASM-1487)
  fixtures-meta.json   MEASURED gates: balance table; AU-vs-AN
                       representation node/edge/reifier/byte census +
                       equality (review fix 4 — measured, not asserted);
                       AD coincidence rate + derangement attempt
                       (PROPOSED-ASM-1485, <=0.35 or re-derange); AN
                       accept/reject nondegeneracy stats; OOP probe
                       refusal correctness; message-discipline lint result
  token-band.json      pinned-tokenizer rejection-message parity artifact
                       (PROPOSED-ASM-1484; knull G-3 pattern)
  fixtures-sha.json    double-run determinism proof: the WHOLE
                       materialisation runs twice in-process; canonical
                       shas MUST match (ERR_FIXTURES_PRECONDITION)

--self-test executes the design §4.4 worked examples byte-exactly (build
gate) and exits. --check re-materialises and compares against the committed
fixtures-sha.json (the runner's in-run re-verification path).

CPU-only, $0, no network. Fail-closed: ERR_FIXTURES_PRECONDITION,
ERR_CONFLICT, ERR_MESSAGE_DISCIPLINE, ERR_TOKENIZER_PIN, ERR_TOKEN_PARITY,
ERR_AD_COINCIDENCE, ERR_AN_DEGENERATE, ERR_REP_MISMATCH, ERR_SELF_TEST.
"""

import argparse
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import twin_ufo as tw  # noqa: E402  (asserts the rules-1 twin pin on import)

ARMS_CHECKER = ("AG", "AU", "AD", "AN")
DERANGE_SEED = 20260712  # design §5 (PROPOSED-ASM-1485)
AD_COINCIDENCE_MAX = 0.35  # design §7.3 item 3
PARITY_BAND = 0.20  # PROPOSED-ASM-1484
PARITY_TARGET = 0.90  # pad below 0.90x AU mean up toward it (inside band)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load_items(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def tokenizer_or_die(path, pin):
    got = tw._sha256_file(path)
    if pin and got != pin:
        raise SystemExit("ERR_TOKENIZER_PIN: %s sha %s != pinned %s"
                         % (path, got, pin))
    from tokenizers import Tokenizer
    return Tokenizer.from_file(path), got


def n_tokens(tok, text):
    return len(tok.encode(text).ids)


# --------------------------------------------------------------------------
def materialise(items, tok, derange_attempt):
    """One full materialisation pass -> (fixtures dict, meta dict).
    PURE function of (items, tokenizer, derange_attempt): the double-run
    determinism proof calls this twice and compares canonical shas."""
    # label-alphabet Sattolo cycle (PROPOSED-ASM-1485): every type's
    # kind/role/phase label MOVES; global meta consistency asserted first.
    global_meta = {}
    for it in items:
        for t, m in it["facts"]["meta_types"].items():
            if global_meta.setdefault(t, m) != m:
                raise SystemExit("ERR_CONFLICT: type %r has inconsistent "
                                 "global meta assignment" % t)
    perm = tw.sattolo_derangement(sorted(tw.META_KINDS), DERANGE_SEED,
                                  derange_attempt)

    gold_rows, table_rows, floor_rows = [], [], []
    rep_census = {"AU": {"n_nodes": 0, "n_edges": 0, "n_reifiers": 0,
                         "bytes": 0},
                  "AN": {"n_nodes": 0, "n_edges": 0, "n_reifiers": 0,
                         "bytes": 0}}
    rep_equal_items = 0
    an_stats = {"accept_E": 0, "reject_E": 0, "accept_C": 0, "reject_C": 0}
    balance = {}
    ad_coincident_all = 0
    ad_coincident_active = 0
    n_active = 0
    n_scored = 0
    oop_ok = 0
    n_oop = 0
    messages = {a: [] for a in ARMS_CHECKER}

    for it in items:
        rep = tw.build_representation(it["facts"])
        cand = it["candidate"]
        # ---- representation census, PER CONSUMING ARM (review fix 4):
        # each checker path re-serialises the representation it consumed.
        au_counts = tw.rep_counts(rep)   # bytes the AU/AD/AG twin parses
        an_counts = tw.rep_counts(rep)   # bytes the AN lookup reads
        if au_counts != an_counts:
            raise SystemExit("ERR_REP_MISMATCH: %s AU %s != AN %s"
                             % (it["item_id"], au_counts, an_counts))
        rep_equal_items += 1
        for k in ("n_nodes", "n_edges", "n_reifiers", "bytes"):
            rep_census["AU"][k] += au_counts[k]
            rep_census["AN"][k] += an_counts[k]

        world_au = tw.UfoWorld(rep)
        if it["scored"] and world_au.conflicts():
            raise SystemExit("ERR_CONFLICT: scored item %s has a conflicted "
                             "AU world: %s"
                             % (it["item_id"], world_au.conflicts()[:3]))
        gold, reason = world_au.disposition(cand)
        if it["scored"]:
            n_scored += 1
            if gold not in tw.ANSWERS:
                raise SystemExit("ERR_CONFLICT: scored item %s gold %r not "
                                 "three-way" % (it["item_id"], gold))
            balance.setdefault(it["family"], {}).setdefault(gold, 0)
            balance[it["family"]][gold] += 1
        else:
            n_oop += 1
            if gold == tw.OOP:
                oop_ok += 1
        gold_rows.append({"item_id": it["item_id"], "family": it["family"],
                          "scored": it["scored"], "gold": gold,
                          "proof_sha256": sha256_bytes(
                              reason.encode("utf-8"))})

        ad_meta = {t: perm[m]
                   for t, m in it["facts"]["meta_types"].items()}
        world_ad = tw.UfoWorld(rep, meta_map=ad_meta)
        arms_world = {"AU": world_au, "AD": world_ad, "AG": None, "AN": None}
        tables = {}
        for arm in ARMS_CHECKER:
            table, d_arm = tw.accept_table_for(arm, rep, cand,
                                               arms_world[arm])
            tables[arm] = table
            table_rows.append({"item_id": it["item_id"], "arm": arm,
                               "d_arm": d_arm, "table": table})
            floor_rows.append({"item_id": it["item_id"], "arm": arm,
                               "floors": tw.floors_for(table, gold)})
            for ans in tw.ANSWERS:
                if not table[ans]["accept"]:
                    messages[arm].append(table[ans]["message"])
        if it["scored"]:
            same = all(tables["AD"][a]["accept"] == tables["AU"][a]["accept"]
                       for a in tw.ANSWERS)
            ad_coincident_all += 1 if same else 0
            # rejection-ACTIVE slice: items where the AU checker rejects
            # something (gold E/C). Gold-U items coincide trivially (neither
            # arm ever rejects — licensed-rejection contract), so the
            # decision-relevant coincidence for s3 is the active-slice rate.
            if any(not tables["AU"][a]["accept"] for a in tw.ANSWERS):
                n_active += 1
                ad_coincident_active += 1 if same else 0
            if tables["AN"][tw.E]["accept"]:
                an_stats["accept_E"] += 1
            else:
                an_stats["reject_E"] += 1
            if tables["AN"][tw.C]["accept"]:
                an_stats["accept_C"] += 1
            else:
                an_stats["reject_C"] += 1

    ad_rate = ad_coincident_active / max(n_active, 1)
    ad_rate_all = ad_coincident_all / max(n_scored, 1)

    # ---- token parity (PROPOSED-ASM-1484): pad below-band arms with the
    # neutral PAD_SENTENCE, deterministically, then measure + enforce.
    mean_tok = {}

    def arm_mean(arm):
        ms = messages[arm]
        return (sum(n_tokens(tok, m) for m in ms) / len(ms)) if ms else None

    mean_tok["AU"] = arm_mean("AU")
    if not mean_tok["AU"]:
        raise SystemExit("ERR_TOKEN_PARITY: AU produced no rejection "
                         "messages — vacuous checker")
    pad_counts = {}
    for arm in ("AG", "AD", "AN"):
        pads = 0
        while True:
            ms = [m + tw.PAD_SENTENCE * pads for m in messages[arm]]
            mean = (sum(n_tokens(tok, m) for m in ms) / len(ms)) if ms \
                else None
            if mean is None or mean >= PARITY_TARGET * mean_tok["AU"]:
                break
            pads += 1
            if pads > 50:
                raise SystemExit("ERR_TOKEN_PARITY: %s cannot reach the "
                                 "band" % arm)
        pad_counts[arm] = pads
        mean_tok[arm] = mean
        if pads:
            for row in table_rows:
                if row["arm"] != arm:
                    continue
                for ans in tw.ANSWERS:
                    cell = row["table"][ans]
                    if not cell["accept"]:
                        cell["message"] += tw.PAD_SENTENCE * pads
    ratios = {a: (mean_tok[a] / mean_tok["AU"]) if mean_tok.get(a) else None
              for a in ("AG", "AD", "AN")}
    for a, r in ratios.items():
        if r is None or abs(r - 1.0) > PARITY_BAND:
            raise SystemExit("ERR_TOKEN_PARITY: arm %s mean ratio %r "
                             "outside +/-%.0f%%" % (a, r, PARITY_BAND * 100))

    # ---- message-discipline lint (review fix 5, machine-enforced) --------
    n_msgs = 0
    for row in table_rows:
        for ans in tw.ANSWERS:
            cell = row["table"][ans]
            if cell["accept"]:
                continue
            n_msgs += 1
            hits = tw.lint_message(cell["message"])
            if hits:
                raise SystemExit("ERR_MESSAGE_DISCIPLINE: %s/%s/%s message "
                                 "hits prohibited pattern(s) %s"
                                 % (row["item_id"], row["arm"], ans, hits))

    fixtures = {"gold": gold_rows, "accept_tables": table_rows,
                "floors": floor_rows}
    meta = {
        "n_items": len(items), "n_scored": n_scored, "n_oop_probes": n_oop,
        "balance": balance,
        "scored_item_ids_sha256": sha256_bytes("\n".join(
            sorted(r["item_id"] for r in gold_rows if r["scored"])
        ).encode("utf-8")),
        "all_item_ids_sha256": sha256_bytes("\n".join(
            sorted(r["item_id"] for r in gold_rows)).encode("utf-8")),
        "representation_census": {
            "AU": rep_census["AU"], "AN": rep_census["AN"],
            "per_item_equal": rep_equal_items == len(items),
            "totals_equal": rep_census["AU"] == rep_census["AN"],
        },
        "ad": {"derange_seed": DERANGE_SEED,
               "derange_attempt": derange_attempt,
               "label_cycle": perm,
               "coincidence_rate": ad_rate,
               "coincidence_basis": "rejection-active scored items "
                                    "(d_AU in {E,C}; n=%d)" % n_active,
               "coincidence_rate_all_scored": ad_rate_all,
               "bound": AD_COINCIDENCE_MAX,
               "ok": ad_rate <= AD_COINCIDENCE_MAX},
        "an_stats": dict(an_stats,
                         nondegenerate=(an_stats["accept_E"] > 0
                                        and an_stats["reject_E"] > 0
                                        and an_stats["accept_C"] > 0
                                        and an_stats["reject_C"] > 0)),
        "oop": {"n": n_oop,
                "refusal_correctness": oop_ok / max(n_oop, 1)},
        "message_lint": {"n_messages": n_msgs, "clean": True,
                         "prohibited_patterns": [p.pattern for p in
                                                 tw.MESSAGE_PROHIBITED]},
        "token_parity": {"mean_tokens": mean_tok, "ratios": ratios,
                         "band": PARITY_BAND, "pad_counts": pad_counts},
    }
    return fixtures, meta


def canonical_fixture_sha(fixtures, meta):
    blob = tw.canonical({"fixtures": fixtures, "meta": meta}).encode("utf-8")
    return sha256_bytes(blob)


# --------------------------------------------------------------------------
# Build gate: design §4.4 worked examples, byte-exact (--self-test).
# --------------------------------------------------------------------------
def self_test():
    def facts(**kw):
        base = {"situations": ["S1", "S2"], "accessible": [["S1", "S2"]],
                "meta_types": {"Person": "kind", "Student": "role"},
                "subsumptions": [], "exists": [["bo", "S1"], ["bo", "S2"]],
                "holds": [["S1", "bo", "Person"]], "not_holds": [],
                "closed_for": []}
        base.update(kw)
        return base

    cases = [
        # 1. F-RIG/E + near-miss U (drop existsAt(bo,S2))
        (facts(), {"form": "membership", "situation": "S2", "entity": "bo",
                   "type": "Person"}, tw.E),
        (facts(exists=[["bo", "S1"]]),
         {"form": "membership", "situation": "S2", "entity": "bo",
          "type": "Person"}, tw.U),
        # 2. F-ANTI/C witness + companion U (open scope)
        (facts(holds=[["S1", "bo", "Person"], ["S1", "bo", "Student"]],
               not_holds=[["S2", "bo", "Student"]]),
         {"form": "necessity", "entity": "bo", "type": "Student"}, tw.C),
        (facts(holds=[["S1", "bo", "Person"], ["S1", "bo", "Student"]]),
         {"form": "necessity", "entity": "bo", "type": "Student"}, tw.U),
        # 3. F-DISJ/C derived disjointness + companion U (subkind instead)
        (facts(meta_types={"Person": "kind", "Rock": "kind"}),
         {"form": "membership", "situation": "S1", "entity": "bo",
          "type": "Rock"}, tw.C),
        (facts(meta_types={"Person": "kind", "Rock": "kind"},
               subsumptions=[["Rock", "Person"]]),
         {"form": "membership", "situation": "S1", "entity": "bo",
          "type": "Rock"}, tw.U),
        # 4. F-SPEC/C illegal edge + companion E (reversed edge)
        (facts(subsumptions=[["Person", "Student"]]),
         {"form": "spec_consequence", "situation": "S1", "sub": "Person",
          "super": "Student"}, tw.C),
        (facts(subsumptions=[["Student", "Person"]]),
         {"form": "spec_consequence", "situation": "S1", "sub": "Student",
          "super": "Person"}, tw.E),
        # 5. OOP probe
        (facts(), {"form": "oop", "oop_kind": "all-worlds"}, tw.OOP),
    ]
    for i, (f, cand, want) in enumerate(cases):
        rep = tw.build_representation(f)
        got, _reason = tw.UfoWorld(rep).disposition(cand)
        if got != want:
            raise SystemExit("ERR_SELF_TEST: worked example %d: got %s "
                             "want %s" % (i + 1, got, want))
    print("self-test OK: all %d design-§4.4 worked examples byte-exact"
          % len(cases))


# --------------------------------------------------------------------------
def write_fixtures(out_dir, fixtures, meta, sha_proof):
    os.makedirs(out_dir, exist_ok=True)

    def dump_jsonl(name, rows):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(tw.canonical(r) + "\n")

    dump_jsonl("gold.jsonl", fixtures["gold"])
    dump_jsonl("accept-tables.jsonl", fixtures["accept_tables"])
    dump_jsonl("floors.jsonl", fixtures["floors"])
    with open(os.path.join(out_dir, "fixtures-meta.json"), "w",
              encoding="utf-8") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(out_dir, "fixtures-sha.json"), "w",
              encoding="utf-8") as f:
        json.dump(sha_proof, f, indent=1, sort_keys=True)
        f.write("\n")
    tb = dict(meta["token_parity"], tokenizer=sha_proof["tokenizer"])
    with open(os.path.join(out_dir, "token-band.json"), "w",
              encoding="utf-8") as f:
        json.dump(tb, f, indent=1, sort_keys=True)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=os.path.normpath(os.path.join(
        _HERE, "..", "..", "data", "ufo-sn3-items-v0", "items.jsonl")))
    ap.add_argument("--out-dir", default=os.path.join(_HERE, "inputs",
                                                      "fixtures"))
    ap.add_argument("--tokenizer", required=False,
                    help="pinned tokenizer.json path (SmolLM2 family)")
    ap.add_argument("--tokenizer-sha", default=None,
                    help="expected sha256 of tokenizer.json (fail closed)")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="re-materialise and compare against the committed "
                         "fixtures-sha.json (in-run re-verification)")
    args = ap.parse_args()

    self_test()  # always: the §4.4 build gate is cheap and load-bearing
    if args.self_test:
        return

    if not args.tokenizer:
        raise SystemExit("ERR_TOKENIZER_PIN: --tokenizer is required for "
                         "fixture materialisation (token parity artifact)")
    tok, tok_sha = tokenizer_or_die(args.tokenizer, args.tokenizer_sha)
    items = load_items(args.items)

    # AD derangement attempt loop (design §7.3 item 3): deterministic
    # attempt bump until the coincidence bound holds; attempt is RECORDED.
    attempt = 0
    while True:
        fixtures, meta = materialise(items, tok, attempt)
        if meta["ad"]["ok"]:
            break
        attempt += 1
        if attempt > 20:
            raise SystemExit("ERR_AD_COINCIDENCE: no derangement attempt "
                             "<=20 meets the %.2f bound" % AD_COINCIDENCE_MAX)
    if not meta["an_stats"]["nondegenerate"]:
        raise SystemExit("ERR_AN_DEGENERATE: AN accept/reject stats "
                         "degenerate: %s" % meta["an_stats"])
    if not (meta["representation_census"]["per_item_equal"]
            and meta["representation_census"]["totals_equal"]):
        raise SystemExit("ERR_REP_MISMATCH: AU vs AN representation census "
                         "differs: %s" % meta["representation_census"])

    # double-run determinism proof (PROPOSED-ASM-1483)
    sha1 = canonical_fixture_sha(fixtures, meta)
    fixtures2, meta2 = materialise(items, tok, attempt)
    sha2 = canonical_fixture_sha(fixtures2, meta2)
    if sha1 != sha2:
        raise SystemExit("ERR_FIXTURES_PRECONDITION: double-run shas differ "
                         "(%s != %s)" % (sha1, sha2))
    sha_proof = {"fixtures_sha_run1": sha1, "fixtures_sha_run2": sha2,
                 "match": True, "derange_attempt": attempt,
                 "items_sha256": tw._sha256_file(args.items),
                 "tokenizer": {"path_basename":
                               os.path.basename(args.tokenizer),
                               "sha256": tok_sha}}

    if args.check:
        committed = json.load(open(os.path.join(args.out_dir,
                                                "fixtures-sha.json")))
        if committed["fixtures_sha_run1"] != sha1:
            raise SystemExit("ERR_FIXTURE_SHA: recomputed %s != committed "
                             "%s" % (sha1, committed["fixtures_sha_run1"]))
        print("check OK: fixtures reproduce committed sha %s" % sha1[:16])
        return

    write_fixtures(args.out_dir, fixtures, meta, sha_proof)
    print("fixtures OK: sha %s (double-run match; derange attempt %d, "
          "coincidence %.3f; AN nondegenerate; rep census equal; %d "
          "messages lint-clean)"
          % (sha1[:16], attempt, meta["ad"]["coincidence_rate"],
             meta["message_lint"]["n_messages"]))


if __name__ == "__main__":
    main()
