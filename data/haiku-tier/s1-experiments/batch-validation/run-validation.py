#!/usr/bin/env python3
"""haiku-tier batch-validation — single-lemma framework G vs batch-of-4 A/B.

Motivation (maintainer directive 2026-07-07): raise API spend/throughput per
local CPU-second. Every `claude -p` call is a full Node CLI process on a
2-core box; packing 4 lemmas into one call ≈ 4x tokens per process spawn.
This harness measures whether the batched pipeline
(runner/run-volume.py --batch-size 4; prompts system-A-batch/system-F-batch;
sentinel-delimited per-lemma blocks; ONE batched gate-error-fed repair call
per batch) matches the measured single-lemma framework G pipeline on QUALITY,
on the SAME lemmas, before the live volume runner is switched (that switch is
coordinator-gated on this report).

Design:
  - 80 lemmas at inventory rank >= 30000 (the live volume runner processes
    ranks <= ~15000 concurrently with this harness — no collision possible),
    evenly spaced over the remaining rank span, skipping the done-set and
    lemmas with no fetchable definitional text (skip rule: step to the next
    rank; deterministic). Frozen into lemmas.json on first run.
  - Arm S: the exact single-lemma framework G path (system-A draft ->
    gates.mjs --one --normalized -> system-F + real gate errors repair ->
    re-gate), byte-identical prompts and call config to run-volume.py.
  - Arm B: chunks of 4 in list order through the batched path (reusing
    run-volume.py's build_batch_user / extract_blocks / build_batch_repair_user
    / gate_one so the harness measures the very code the runner will execute).
  - Concurrency 3 FIXED (the volume runner owns the box's headroom; this
    harness measures quality, not speed). All outputs land in this directory,
    never in records/ or volume/ (the live runner's outputs).
  - Checkpointed per lemma (arm S) / per chunk (arm B): re-running resumes.
    A usage-limit error checkpoints and exits 2 (finish with what you have).

PRE-DECLARED GO/NO-GO criteria (fixed before any results were seen):
  G1  net ok-yield(B) >= 0.8 x net ok-yield(S) on the same 80 lemmas
  G2  zero cross-lemma contamination in B's ok records (a record referencing
      or quoting a batch sibling)
  G3  API-equiv $ per ok record (B, shared-cost attribution) <= 1.5 x S
  G4  |CF-rate(B) - CF-rate(S)| <= 15 percentage points (guard against
      batch-induced abstention inflation, the s1 framework-C pathology)
GO requires all four.

Usage (each phase is resumable; default runs select+both arms+analyze):
  nice -n 10 python3 run-validation.py [--arm single|batch] [--analyze-only]
      [--budget-seconds N]   # stop submitting new work after N s, exit 0
"""
import argparse, importlib.util, json, os, re, sys, threading, time, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))            # .../batch-validation
S1 = os.path.abspath(os.path.join(HERE, '..'))
TIER = os.path.abspath(os.path.join(S1, '..'))

spec = importlib.util.spec_from_file_location(
    'runvolume', os.path.join(TIER, 'runner', 'run-volume.py'))
rv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rv)

N_LEMMAS = 80
BATCH = 4
CONCURRENCY = 3            # directive: <= 3; the volume runner owns headroom
CALL_TIMEOUT_S = 420       # box runs 2 volume runners at ~30 in-flight calls on
                           # 2 cores: per-call wall is 2-5 min, not the ~5 s of s1
MIN_RANK = 30000           # live volume runner is at ranks <= ~15000
SYS_A = os.path.join(S1, 'prompts', 'system-A.txt')
SYS_F = os.path.join(S1, 'prompts', 'system-F.txt')
SYS_AB = os.path.join(S1, 'prompts', 'system-A-batch.txt')
SYS_FB = os.path.join(S1, 'prompts', 'system-F-batch.txt')
OUT = os.path.join(HERE, 'outputs')
TMP = os.path.join(OUT, 'tmp')
LEMMAS_JSON = os.path.join(HERE, 'lemmas.json')
META_JSON = os.path.join(HERE, 'meta.json')
_write_lock = threading.Lock()


def meta_load():
    return json.load(open(META_JSON)) if os.path.exists(META_JSON) else {}


def meta_update(**kv):
    m = meta_load(); m.update(kv)
    with open(META_JSON, 'w') as f:
        json.dump(m, f, indent=1)


def mu_of(env):
    mus = list(env.get('modelUsage', {}).values())
    mu = mus[0] if mus else {}
    return {'inputTokens': mu.get('inputTokens'), 'outputTokens': mu.get('outputTokens'),
            'cacheReadInputTokens': mu.get('cacheReadInputTokens'),
            'cacheCreationInputTokens': mu.get('cacheCreationInputTokens'),
            'costUSD': mu.get('costUSD') or 0.0,
            'durationMs': env.get('duration_ms') or 0}


def call_with_retry(sysfile, user):
    """rv.call_claude + bounded transient-rate-limit patience (we run at
    concurrency 3 while the volume runner hammers the account, so 429s here
    are expected collateral). UsageLimit propagates: checkpoint-and-stop."""
    for attempt in range(5):
        try:
            return rv.call_claude(sysfile, user, timeout_s=CALL_TIMEOUT_S)
        except rv.RateLimited:
            if attempt == 4:
                raise
            time.sleep(20 * (attempt + 1))


def save_env(rel, env):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        json.dump(env, f, indent=1)


def append_row(fname, row):
    with _write_lock:
        with open(os.path.join(HERE, fname), 'a') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def load_rows(fname):
    p = os.path.join(HERE, fname)
    if not os.path.exists(p):
        return {}
    return {r['lemma']: r for r in (json.loads(l) for l in open(p))}


# --- selection ---------------------------------------------------------------

def select_lemmas():
    if os.path.exists(LEMMAS_JSON):
        return json.load(open(LEMMAS_JSON))['lemmas']
    inv = [json.loads(l) for l in open(os.path.join(TIER, 'inventory', 'inventory.jsonl'))]
    done = set(f[:-5] for f in os.listdir(os.path.join(TIER, 'records'))
               if f.endswith('.json'))
    for lf in ('failures.jsonl', 'cannot-formalise.jsonl'):
        p = os.path.join(TIER, 'volume', lf)
        if os.path.exists(p):
            done |= {json.loads(l)['lemma'] for l in open(p)}
    cands = sorted((it for it in inv if it['rank'] >= MIN_RANK
                    and it['lemma'] not in done), key=lambda x: x['rank'])
    step = len(cands) // N_LEMMAS
    chosen, used = [], set()
    for slot in range(N_LEMMAS):
        i = slot * step
        while i < len(cands):
            it = cands[i]
            if it['lemma'] not in used:
                text, _ = rv.def_text_and_sources(it['lemma'])   # serial => polite
                if text != '(no definitional text available)':
                    chosen.append({'lemma': it['lemma'], 'rank': it['rank'],
                                   'band': it['band']})
                    used.add(it['lemma'])
                    break
            i += 1
        print(f'  slot {slot + 1}/{N_LEMMAS}: {chosen[-1]["lemma"]} '
              f'(rank {chosen[-1]["rank"]})', file=sys.stderr)
    with open(LEMMAS_JSON, 'w') as f:
        json.dump({'selectedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                   'rule': f'rank>={MIN_RANK}, not in done-set (n={len(done)}), '
                           f'{N_LEMMAS} evenly spaced (step {step}), skip-forward on '
                           'no definitional text; chunks of 4 in list order',
                   'lemmas': chosen}, f, indent=1)
    return chosen


# --- arm S: single-lemma framework G ------------------------------------------

def run_single_one(lemma):
    t0 = time.time()
    text, _ = rv.def_text_and_sources(lemma)
    user = rv.build_user(lemma, text)
    env = call_with_retry(SYS_A, user)
    save_env(f'single/{lemma}-draft.json', env)
    usages = [mu_of(env)]
    gate = rv.gate_one(lemma, env.get('result', ''), tmpdir=TMP)
    if not gate['pass'] and gate['kind'] != 'cannot-formalise':
        # byte-identical repair-turn construction to run-volume.py process()
        repair_user = (user + '\n\nDRAFT (from an earlier pass; check and correct it):\n'
                       + env.get('result', '').strip()
                       + '\n\nMECHANICAL GATE ERRORS for this draft (fix every one; '
                         'the same validator will re-run):\n- '
                       + '\n- '.join(gate.get('errors', ['(unparseable JSON)'])[:25]))
        env = call_with_retry(SYS_F, repair_user)
        save_env(f'single/{lemma}-repair.json', env)
        usages.append(mu_of(env))
        gate = rv.gate_one(lemma, env.get('result', ''), tmpdir=TMP)
    return {'lemma': lemma, 'arm': 'single', 'kind': gate.get('kind'),
            'pass': gate['pass'], 'errors': (gate.get('errors') or [])[:10],
            'calls': len(usages), 'spawns': len(usages),
            'costUSD': round(sum(u['costUSD'] for u in usages), 6),
            'apiMs': sum(u['durationMs'] for u in usages),
            'tokensIn': sum(u['inputTokens'] or 0 for u in usages),
            'tokensOut': sum(u['outputTokens'] or 0 for u in usages),
            'wallS': round(time.time() - t0, 1),
            'result': env.get('result', '')}


# --- arm B: batch-of-4 ---------------------------------------------------------

def run_batch_chunk(ci, lemmas):
    t0 = time.time()
    texts = {}
    for l in lemmas:
        texts[l], _ = rv.def_text_and_sources(l)
    env = call_with_retry(SYS_AB, rv.build_batch_user([(l, texts[l]) for l in lemmas]))
    save_env(f'batch/chunk{ci:02d}-draft.json', env)
    dmu = mu_of(env)
    blocks = rv.extract_blocks(env.get('result', ''), lemmas)
    per = {l: {'gate': (rv.gate_one(l, blocks[l], tmpdir=TMP)
                        if blocks[l] is not None else rv.missing_block_gate()),
               'block': blocks[l] or '', 'draftMissing': blocks[l] is None}
           for l in lemmas}
    need = [l for l in lemmas
            if not per[l]['gate']['pass'] and per[l]['gate']['kind'] != 'cannot-formalise']
    rmu = None
    if need:
        entries = [(l, texts[l], per[l]['block'],
                    per[l]['gate'].get('errors', ['(unparseable JSON)'])[:25])
                   for l in need]
        renv = call_with_retry(SYS_FB, rv.build_batch_repair_user(entries))
        save_env(f'batch/chunk{ci:02d}-repair.json', renv)
        rmu = mu_of(renv)
        rblocks = rv.extract_blocks(renv.get('result', ''), need)
        for l in need:
            if rblocks[l] is not None:
                per[l]['block'] = rblocks[l]
                per[l]['gate'] = rv.gate_one(l, rblocks[l], tmpdir=TMP)
            else:
                per[l]['gate'] = rv.missing_block_gate()
                per[l]['gate']['errors'].append('ERR_BLOCK: no repaired block emitted either')
    wall = time.time() - t0
    rows = []
    for l in lemmas:
        # shared-cost attribution: draft call / batch size, repair call / |need|
        cost = dmu['costUSD'] / len(lemmas)
        api = dmu['durationMs'] / len(lemmas)
        tin = (dmu['inputTokens'] or 0) / len(lemmas)
        tout = (dmu['outputTokens'] or 0) / len(lemmas)
        spawns = 1.0 / len(lemmas)
        if rmu and l in need:
            cost += rmu['costUSD'] / len(need)
            api += rmu['durationMs'] / len(need)
            tin += (rmu['inputTokens'] or 0) / len(need)
            tout += (rmu['outputTokens'] or 0) / len(need)
            spawns += 1.0 / len(need)
        g = per[l]['gate']
        rows.append({'lemma': l, 'arm': 'batch', 'chunk': ci,
                     'chunkLemmas': lemmas, 'kind': g.get('kind'), 'pass': g['pass'],
                     'errors': (g.get('errors') or [])[:10],
                     'calls': 2 if (rmu and l in need) else 1,
                     'spawns': round(spawns, 4),
                     'costUSD': round(cost, 6), 'apiMs': round(api),
                     'tokensIn': round(tin), 'tokensOut': round(tout),
                     'draftMissing': per[l]['draftMissing'],
                     'repaired': bool(rmu and l in need),
                     'wallS': round(wall / len(lemmas), 1),
                     'result': per[l]['block']})
    return rows


# --- driving ------------------------------------------------------------------

def drive(items, fn, deadline):
    """Run fn over items at CONCURRENCY 3; stop submitting past deadline;
    UsageLimit => checkpoint note + exit 2."""
    limit_msg = None
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {}
        it = iter(items)
        def submit_next():
            if deadline and time.time() > deadline:
                return False
            try:
                x = next(it)
            except StopIteration:
                return False
            futs[ex.submit(fn, x)] = x
            return True
        for _ in range(CONCURRENCY):
            submit_next()
        while futs:
            for fu in as_completed(list(futs)):
                x = futs.pop(fu)
                try:
                    fu.result()
                except rv.UsageLimit as e:
                    limit_msg = e.msg[:300]
                except Exception as e:
                    print(f'ERROR on {x}: {str(e)[:200]}', file=sys.stderr)
                if limit_msg is None:
                    submit_next()
                break
        if limit_msg:
            meta_update(usageLimitHit=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                        usageLimitMsg=limit_msg)
            print(f'USAGE LIMIT — checkpointed, stopping: {limit_msg[:120]}',
                  file=sys.stderr)
            sys.exit(2)


def arm_single(lemmas, deadline):
    done = load_rows('results-single.jsonl')
    todo = [l['lemma'] for l in lemmas if l['lemma'] not in done]
    print(f'arm S: {len(todo)} lemmas to run ({len(done)} done)', file=sys.stderr)
    t0 = time.time()
    def one(lemma):
        append_row('results-single.jsonl', run_single_one(lemma))
    drive(todo, one, deadline)
    m = meta_load()
    meta_update(singleWallS=round(m.get('singleWallS', 0) + time.time() - t0, 1))


def arm_batch(lemmas, deadline):
    done = load_rows('results-batch.jsonl')
    names = [l['lemma'] for l in lemmas]
    chunks = [(i // BATCH, names[i:i + BATCH]) for i in range(0, len(names), BATCH)]
    todo = [c for c in chunks if any(l not in done for l in c[1])]
    print(f'arm B: {len(todo)} chunks to run ({len(chunks) - len(todo)} done)',
          file=sys.stderr)
    t0 = time.time()
    def one(c):
        ci, ls = c
        for row in run_batch_chunk(ci, ls):
            append_row('results-batch.jsonl', row)
    drive(todo, one, deadline)
    m = meta_load()
    meta_update(batchWallS=round(m.get('batchWallS', 0) + time.time() - t0, 1))


# --- analysis -----------------------------------------------------------------

def norm_note(s):
    return unicodedata.normalize('NFC', str(s or '')).lower().strip()


def outcome(row):
    if row['pass'] and row['kind'] in ('molecule', 'explication'):
        return 'ok'
    if row['pass'] and row['kind'] == 'cannot-formalise':
        return 'cf'
    return 'fail'


def analyze(lemmas):
    S = load_rows('results-single.jsonl')
    B = load_rows('results-batch.jsonl')
    names = [l['lemma'] for l in lemmas]
    both = [l for l in names if l in S and l in B]
    meta = meta_load()

    def arm_stats(rows, wall):
        xs = [rows[l] for l in both]
        ok = [r for r in xs if outcome(r) == 'ok']
        cf = [r for r in xs if outcome(r) == 'cf']
        fail = [r for r in xs if outcome(r) == 'fail']
        cost = sum(r['costUSD'] for r in xs)
        return {'n': len(xs), 'ok': len(ok), 'cf': len(cf), 'fail': len(fail),
                'okMol': sum(1 for r in ok if r['kind'] == 'molecule'),
                'okExp': sum(1 for r in ok if r['kind'] == 'explication'),
                'parseFail': sum(1 for r in fail if r['kind'] == 'parse-failure'),
                'calls': sum(r['calls'] for r in xs),
                'spawnsPerLemma': sum(r['spawns'] for r in xs) / max(len(xs), 1),
                'costUSD': cost,
                'costPerLemma': cost / max(len(xs), 1),
                'costPerOk': cost / len(ok) if ok else None,
                'apiSPerLemma': sum(r['apiMs'] for r in xs) / 1000 / max(len(xs), 1),
                'wallSPerLemma': (wall or 0) / max(len(xs), 1)}

    st = {'single': arm_stats(S, meta.get('singleWallS')),
          'batch': arm_stats(B, meta.get('batchWallS'))}

    agree = {}
    for l in both:
        key = outcome(S[l]) + '/' + outcome(B[l])
        agree[key] = agree.get(key, 0) + 1
    cf_either = [l for l in both if 'cf' in (outcome(S[l]), outcome(B[l]))]
    cf_both = [l for l in both if outcome(S[l]) == outcome(B[l]) == 'cf']

    # record-level comparison where BOTH arms passed the same lemma
    eq = {'n': 0, 'kindAgree': 0, 'exact': 0, 'refsEqual': 0,
          'refsJaccard': [], 'noteJaccard': [], 'pairs': []}
    contamination = []
    for l in both:
        if outcome(S[l]) != 'ok' or outcome(B[l]) != 'ok':
            continue
        eq['n'] += 1
        try:
            ps, pb = rv.parse_result(S[l]['result']), rv.parse_result(B[l]['result'])
        except Exception:
            eq['pairs'].append({'lemma': l, 'note': 'reparse failed'})
            continue
        same_kind = ps.get('kind') == pb.get('kind')
        eq['kindAgree'] += same_kind
        detail = {'lemma': l, 'kindS': ps.get('kind'), 'kindB': pb.get('kind')}
        if same_kind and ps.get('kind') == 'molecule':
            ns, nb = norm_note(ps.get('groundingNote')), norm_note(pb.get('groundingNote'))
            rs = set(re.findall(r'urn:[a-z0-9:-]+', ns))
            rb = set(re.findall(r'urn:[a-z0-9:-]+', nb))
            ts, tb = set(ns.split()), set(nb.split())
            exact = ns == nb
            eq['exact'] += exact
            eq['refsEqual'] += rs == rb
            eq['refsJaccard'].append(len(rs & rb) / len(rs | rb) if rs | rb else 1.0)
            eq['noteJaccard'].append(len(ts & tb) / len(ts | tb) if ts | tb else 1.0)
            detail.update(exact=exact, refsEqual=rs == rb,
                          noteJaccard=round(len(ts & tb) / len(ts | tb), 3) if ts | tb else 1.0)
        elif same_kind and ps.get('kind') == 'explication':
            exact = (json.dumps(ps.get('record'), sort_keys=True)
                     == json.dumps(pb.get('record'), sort_keys=True))
            eq['exact'] += exact
            detail.update(exact=exact)
        eq['pairs'].append(detail)
    # cross-lemma contamination scan over ALL batch outputs (ok or not):
    # does any lemma's final text mention a batch sibling?
    for l in both:
        r = B[l]
        low = (r.get('result') or '').lower()
        for sib in r.get('chunkLemmas', []):
            if sib != l and len(sib) >= 4 and re.search(r'\b' + re.escape(sib) + r'\b', low):
                contamination.append({'lemma': l, 'sibling': sib,
                                      'ok': outcome(r) == 'ok'})

    res = {'nBoth': len(both), 'stats': st, 'agreement': agree,
           'cfBoth': len(cf_both), 'cfEither': len(cf_either),
           'equality': {k: v for k, v in eq.items() if k != 'pairs'},
           'equalityPairs': eq['pairs'], 'contamination': contamination}

    # pre-declared gates
    s, b = st['single'], st['batch']
    g1 = b['ok'] >= 0.8 * s['ok']
    g2 = not [c for c in contamination if c['ok']]
    g3 = (b['costPerOk'] is not None and s['costPerOk'] is not None
          and b['costPerOk'] <= 1.5 * s['costPerOk'])
    g4 = abs(b['cf'] - s['cf']) / max(len(both), 1) <= 0.15
    res['gates'] = {'G1_yield': g1, 'G2_contamination': g2, 'G3_cost': g3, 'G4_cf': g4}
    res['verdict'] = 'GO' if all(res['gates'].values()) else 'NO-GO'
    with open(os.path.join(HERE, 'analysis.json'), 'w') as f:
        json.dump(res, f, indent=1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', choices=['single', 'batch'])
    ap.add_argument('--analyze-only', action='store_true')
    ap.add_argument('--budget-seconds', type=int)
    args = ap.parse_args()
    os.makedirs(TMP, exist_ok=True)
    lemmas = select_lemmas()
    deadline = time.time() + args.budget_seconds if args.budget_seconds else None
    if not args.analyze_only:
        if args.arm in (None, 'single'):
            arm_single(lemmas, deadline)
        if args.arm in (None, 'batch'):
            arm_batch(lemmas, deadline)
    res = analyze(lemmas)
    print(json.dumps({k: res[k] for k in ('nBoth', 'stats', 'agreement',
                                          'gates', 'verdict')}, indent=1))


if __name__ == '__main__':
    main()
