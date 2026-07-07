#!/usr/bin/env python3
"""haiku-tier volume runner — session-budget-governed, checkpointed.

Processes data/haiku-tier/inventory/inventory.jsonl in rank order (highest
value first): fetch definitional text (cached), call claude-haiku with the
winning stage-1 framework prompt, gate mechanically (s1-experiments/gates.mjs
--one), and emit:
  data/haiku-tier/records/<lemma>.json            gate-passing modelAuthored records
  data/haiku-tier/volume/failures.jsonl           gate failures (with errors)
  data/haiku-tier/volume/cannot-formalise.jsonl   honest abstentions
  data/haiku-tier/volume/usage-log.jsonl          per-window consumption log

SESSION GOVERNOR (maintainer directive 2026-07-07: the work runs on a shared
Max20 subscription; Haiku gets ~half of each 5h window):
  - max MAX_CALLS_PER_WINDOW calls per 5h window (default 500, conservative);
    windows are anchored at the first call after the previous window closed
    (approximates the plan's rolling 5h session), plus a safety margin.
  - ADAPTIVE concurrency (maintainer directive 2026-07-07: "keep
    parallelising indefinitely until rate limits are hit", round budget
    ~$300 API-equiv): AIMD — ramp +2 after each target-many successes,
    halve on a transient rate-limit/overload, guarded by /proc/meminfo
    MemAvailable so the live server sharing this 2-core box is never
    OOM-squeezed. --concurrency is the STARTING target, --concurrency-max
    the ceiling. --max-cost-usd stops the round when API-equiv spend
    crosses it.
  - any usage-limit error from claude -p => stop the window immediately,
    parse a reset time from the error if present (epoch, ISO, or h:mm am/pm)
    and sleep past it + 10 min margin; else sleep 60 min.
  - full checkpointing: every lemma's outcome lands on disk before the next
    starts; reruns skip finished lemmas, so the runner resumes across
    windows/days/crashes with no state beyond the output files + state.json.

Usage:
  nice -n 10 python3 data/haiku-tier/runner/run-volume.py --dry-run           # plan only, no calls
  nice -n 10 python3 data/haiku-tier/runner/run-volume.py --limit 500         # one window's worth
  nice -n 10 python3 data/haiku-tier/runner/run-volume.py                     # run to inventory end
Options: --framework A --max-per-window 500 --window-hours 5 --concurrency 2
         --bands ABCD --start-rank N --limit N --dry-run
"""
import argparse, collections, datetime, hashlib, importlib.util, json, os, re, subprocess, sys, time, unicodedata
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

HERE = os.path.dirname(os.path.abspath(__file__))          # data/haiku-tier/runner
TIER = os.path.abspath(os.path.join(HERE, '..'))            # data/haiku-tier
REPO = os.path.abspath(os.path.join(TIER, '..', '..'))
S1 = os.path.join(TIER, 's1-experiments')
VOL = os.path.join(TIER, 'volume')
RECORDS = os.path.join(TIER, 'records')
MODEL = 'claude-haiku-4-5-20251001'

# import the fetcher module (shared def-text logic)
spec = importlib.util.spec_from_file_location(
    'fetchdefs', os.path.join(TIER, 'fetch', 'fetch-definitions.py'))
fetchdefs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetchdefs)

def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def pipeline_hash():
    files = [os.path.join(HERE, 'run-volume.py'),
             os.path.join(S1, 'gates.mjs'),
             os.path.join(TIER, 'fetch', 'fetch-definitions.py'),
             os.path.join(TIER, 'inventory', 'build-inventory.py')]
    h = hashlib.sha256()
    for f in files: h.update(sha256_file(f).encode())
    return h.hexdigest()

def def_text_and_sources(lemma):
    parts, sources = [], []
    wt, _ = fetchdefs.cached_fetch('wiktionary', lemma, fetchdefs.fetch_wiktionary)
    if wt.get('ok'):
        by_pos = {}
        for s in wt['senses']:
            by_pos.setdefault(s['pos'], []).append(s['definition'])
        lines = []
        for pos, ds in list(by_pos.items())[:4]:
            for d in ds[:4]:
                lines.append(f'({pos.lower()}) {d[:220]}')
        parts.append(f'Wiktionary (rev {wt.get("revision","?")}):\n' + '\n'.join(lines[:8]))
        sources.append({'source': 'wiktionary',
                        'url': f'https://en.wiktionary.org/api/rest_v1/page/definition/{lemma}',
                        'revision': wt.get('revision'), 'fetched': wt.get('fetched')})
    wp, _ = fetchdefs.cached_fetch('wikipedia', lemma, fetchdefs.fetch_wikipedia)
    if wp.get('ok'):
        parts.append(f'Wikipedia (rev {wp.get("revision","?")}): {wp["extract"][:600]}')
        sources.append({'source': 'wikipedia',
                        'url': f'https://en.wikipedia.org/api/rest_v1/page/summary/{lemma}',
                        'revision': wp.get('revision'), 'tid': wp.get('tid'),
                        'fetched': wp.get('fetched')})
    return ('\n'.join(parts) if parts else '(no definitional text available)'), sources

RESET_PATTERNS = [
    (re.compile(r'reset[s]?(?: at)?[^0-9]{0,10}(1[6-9]\d{8})'), 'epoch'),
    (re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?)'), 'iso'),
    (re.compile(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))', re.I), 'clock'),
]
def parse_reset_seconds(msg):
    """Best-effort: seconds to sleep until the reported reset (+ margin handled
    by caller). Returns None if nothing parseable."""
    now = time.time()
    for rx, kind in RESET_PATTERNS:
        m = rx.search(msg)
        if not m: continue
        try:
            if kind == 'epoch':
                return max(0, int(m.group(1)) - now)
            if kind == 'iso':
                t = datetime.datetime.fromisoformat(m.group(1)).timestamp()
                return max(0, t - now)
            if kind == 'clock':
                h, mnt = (m.group(1).lower().replace('am', ' am').replace('pm', ' pm')
                          .split()[0] + ':0').split(':')[:2]
                hh = int(h) % 12 + (12 if 'pm' in m.group(1).lower() else 0)
                cand = datetime.datetime.now().replace(hour=hh, minute=int(mnt or 0),
                                                       second=0, microsecond=0)
                if cand.timestamp() < now: cand += datetime.timedelta(days=1)
                return cand.timestamp() - now
        except Exception:
            continue
    return None

class UsageLimit(Exception):
    def __init__(self, msg): super().__init__(msg); self.msg = msg

class RateLimited(Exception):
    """Transient per-request rate limit / overload — scheduler halves the
    concurrency target and requeues the lemma; NOT a window stop."""
    def __init__(self, msg): super().__init__(msg); self.msg = msg

def mem_available_mb():
    try:
        for line in open('/proc/meminfo'):
            if line.startswith('MemAvailable:'):
                return int(line.split()[1]) // 1024
    except Exception:
        pass
    return None

def call_claude(system_file, user_text, attempts=3):
    env = dict(os.environ, MAX_THINKING_TOKENS='0')
    cmd = ['nice', '-n', '10', 'claude', '-p', '--model', MODEL,
           '--system-prompt-file', system_file, '--tools', '',
           '--strict-mcp-config', '--exclude-dynamic-system-prompt-sections',
           '--effort', 'low', '--output-format', 'json', '--max-turns', '1']
    last = None
    for attempt in range(attempts):
        try:
            r = subprocess.run(cmd, input=user_text, capture_output=True,
                               text=True, env=env, timeout=300)
        except subprocess.TimeoutExpired:
            last = 'claude timeout after 300s'
            time.sleep(5 * 3 ** attempt)
            continue
        if r.returncode == 0:
            try:
                out = json.loads(r.stdout)
            except Exception:
                last = f'unparseable stdout: {(r.stdout or "")[:200]}'
                time.sleep(5 * 3 ** attempt)
                continue
            if not out.get('is_error'):
                # limit patterns are only scanned on ERROR paths — a lemma
                # whose generated text mentions "rate limit" must not trip them
                return out
            blob = r.stdout
        else:
            blob = (r.stdout or '') + (r.stderr or '')
        # window-level limits stop the run (the 2026-07-07 burn: "You've hit
        # your session limit" matched nothing here and 253 lemmas were logged
        # as transport errors instead of pausing — hence 'session limit')
        if re.search(r'usage limit|session limit|limit reached|'
                     r'out of.*(quota|credits)|5-hour', blob, re.I):
            raise UsageLimit(blob[:1000])
        if re.search(r'rate.?limit|overloaded|too many requests|429', blob, re.I):
            raise RateLimited(blob[:400])
        last = f'claude exit {r.returncode}: {blob[:400]}'
        time.sleep(5 * 3 ** attempt)
    raise RuntimeError(last)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--framework', default='A',
                    help='draft-pass system prompt (s1 framework id)')
    ap.add_argument('--repair', action=argparse.BooleanOptionalAction, default=True,
                    help='on gate failure, run one repair pass (system-F prompt '
                         '+ the actual gate errors) and re-gate — the measured '
                         'best pipeline from s1 (framework G)')
    ap.add_argument('--max-per-window', type=int, default=500)
    ap.add_argument('--window-hours', type=float, default=5.0)
    ap.add_argument('--concurrency', type=int, default=2,
                    help='STARTING concurrency target (adaptive AIMD)')
    ap.add_argument('--concurrency-max', type=int, default=14,
                    help='adaptive ceiling; bounded by box RAM, not the API')
    ap.add_argument('--max-cost-usd', type=float,
                    help='stop the round when cumulative API-equiv cost crosses this')
    ap.add_argument('--bands', default='ABCD')
    ap.add_argument('--start-rank', type=int, default=1)
    ap.add_argument('--limit', type=int)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    assert 1 <= args.concurrency <= args.concurrency_max <= 64, \
        'need 1 <= concurrency <= concurrency-max <= 64'

    os.makedirs(VOL, exist_ok=True); os.makedirs(RECORDS, exist_ok=True)
    sysfile = os.path.join(S1, 'prompts', f'system-{args.framework}.txt')
    repairfile = os.path.join(S1, 'prompts', 'system-F.txt')
    prov_static = {
        'model': MODEL,
        'framework': args.framework + ('+gate-loop-repair' if args.repair else ''),
        'promptVersionHash': 'sha256:' + sha256_file(sysfile),
        'repairPromptVersionHash': ('sha256:' + sha256_file(repairfile)) if args.repair else None,
        'pipelineVersionHash': 'sha256:' + pipeline_hash(),
    }
    inv = [json.loads(l) for l in open(os.path.join(TIER, 'inventory', 'inventory.jsonl'))]
    done = set(f[:-5] for f in os.listdir(RECORDS) if f.endswith('.json'))
    for logf in ('failures.jsonl', 'cannot-formalise.jsonl'):
        p = os.path.join(VOL, logf)
        if os.path.exists(p):
            done |= {json.loads(l)['lemma'] for l in open(p)}
    todo = [it for it in inv
            if it['band'] in args.bands and it['rank'] >= args.start_rank
            and it['lemma'] not in done]
    if args.limit: todo = todo[:args.limit]
    print(f'{len(todo)} to process (of {len(inv)}; {len(done)} already done); '
          f'governor: {args.max_per_window} calls / {args.window_hours}h window, '
          f'concurrency {args.concurrency}', file=sys.stderr)
    if args.dry_run:
        calls_per_concept = 1.9 if args.repair else 1.0   # s1-measured: ~90% need repair
        est_windows = int((len(todo) * calls_per_concept + args.max_per_window - 1)
                          // args.max_per_window)
        print(f'DRY RUN: would need ~{est_windows} windows '
              f'(~{est_windows/3:.1f} days at 3 windows/day). First 5: '
              f'{[t["lemma"] for t in todo[:5]]}', file=sys.stderr)
        return

    state = {'windowStart': None, 'calls': 0, 'ok': 0, 'fail': 0, 'cf': 0,
             'tokensIn': 0, 'tokensOut': 0, 'costUSD': 0.0}

    def log_window():
        with open(os.path.join(VOL, 'usage-log.jsonl'), 'a') as f:
            f.write(json.dumps({**state, 'windowEnd':
                time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}) + '\n')

    def window_gate():
        now = time.time()
        if state['windowStart'] is None:
            state.update(windowStart=now, calls=0, ok=0, fail=0, cf=0,
                         tokensIn=0, tokensOut=0, costUSD=0.0)
        if now - state['windowStart'] >= args.window_hours * 3600:
            log_window()
            state.update(windowStart=now, calls=0, ok=0, fail=0, cf=0,
                         tokensIn=0, tokensOut=0, costUSD=0.0)
        if state['calls'] >= args.max_per_window:
            wake = state['windowStart'] + args.window_hours * 3600 + 300
            slp = max(0, wake - now)
            print(f'governor: window budget spent; sleeping {slp/60:.0f} min',
                  file=sys.stderr)
            log_window(); time.sleep(slp)
            state.update(windowStart=time.time(), calls=0, ok=0, fail=0, cf=0,
                         tokensIn=0, tokensOut=0, costUSD=0.0)

    round_tot = {'calls': 0, 'costUSD': 0.0}   # whole-invocation, never reset

    def account(env):
        mu = list(env.get('modelUsage', {}).values())
        mu = mu[0] if mu else {}
        state['calls'] += 1
        state['tokensIn'] += (mu.get('inputTokens') or 0)
        state['tokensOut'] += (mu.get('outputTokens') or 0)
        state['costUSD'] = round(state['costUSD'] + (mu.get('costUSD') or 0), 5)
        round_tot['calls'] += 1
        round_tot['costUSD'] = round(round_tot['costUSD'] + (mu.get('costUSD') or 0), 5)
        return mu

    def gate_one(lemma, result_text):
        tmp = os.path.join(VOL, f'.result-{lemma}.txt')
        open(tmp, 'w').write(result_text)
        gate = json.loads(subprocess.run(
            ['node', os.path.join(S1, 'gates.mjs'), '--one', lemma, tmp, '--normalized'],
            capture_output=True, text=True, check=True).stdout)
        os.unlink(tmp)
        return gate

    def parse_result(result_text):
        m = re.search(r'```(?:json)?\s*([\s\S]*?)```', result_text)
        return json.loads((m.group(1) if m else result_text).strip())

    def process(it):
        lemma = it['lemma']
        text, sources = def_text_and_sources(lemma)
        user = (f'CONCEPT: {lemma}\n\nDefinitional text:\n{text}\n\n'
                f'Produce the JSON record for the dominant everyday sense of "{lemma}".')
        env = call_claude(sysfile, user)
        mu = account(env)
        gate = gate_one(lemma, env.get('result', ''))
        usages = [mu]
        # gate-in-the-loop repair (s1 framework G): one repair pass fed with
        # the validator's actual errors, then re-gate. Never repair a passing
        # output or an honest abstention.
        if args.repair and not gate['pass'] and gate['kind'] != 'cannot-formalise':
            repair_user = (user + '\n\nDRAFT (from an earlier pass; check and correct it):\n'
                           + env.get('result', '').strip()
                           + '\n\nMECHANICAL GATE ERRORS for this draft (fix every one; '
                             'the same validator will re-run):\n- '
                           + '\n- '.join(gate.get('errors', ['(unparseable JSON)'])[:25]))
            env = call_claude(repairfile, repair_user)
            usages.append(account(env))
            gate = gate_one(lemma, env.get('result', ''))
        prov = {**prov_static, 'sources': sources,
                'date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'usage': [{'inputTokens': u.get('inputTokens'),
                           'outputTokens': u.get('outputTokens'),
                           'cacheReadInputTokens': u.get('cacheReadInputTokens'),
                           'cacheCreationInputTokens': u.get('cacheCreationInputTokens'),
                           'costUSD': u.get('costUSD')} for u in usages]}
        try:
            parsed = parse_result(env.get('result', ''))
        except Exception:
            parsed = {}
        if gate['pass'] and gate['kind'] in ('molecule', 'explication'):
            rec = {'schema': 'haiku-tier/1', 'id': f'urn:haiku-tier:{lemma}',
                   'label': lemma, 'semanticStatus': 'ModelAuthored',
                   'candidateStatus': 'Molecule' if gate['kind'] == 'molecule' else 'Explicated',
                   'kind': gate['kind'], 'gloss': parsed.get('gloss'),
                   **({'groundingNote': unicodedata.normalize(
                           'NFC', str(parsed.get('groundingNote', ''))).lower(),
                       'groundingRefs': gate.get('normalizedRefs')
                                        or sorted(set(parsed.get('groundingRefs', []))),
                       'moleculeDepth': gate.get('depth')} if gate['kind'] == 'molecule'
                      else {'record': parsed['record']}),
                   'gatesPassed': True, 'researchGrade': True, 'provenance': prov}
            with open(os.path.join(RECORDS, f'{lemma}.json'), 'w') as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
            state['ok'] += 1
        elif gate['kind'] == 'cannot-formalise' and gate['pass']:
            with open(os.path.join(VOL, 'cannot-formalise.jsonl'), 'a') as f:
                f.write(json.dumps({'lemma': lemma, 'why': parsed.get('why'),
                                    'provenance': prov}) + '\n')
            state['cf'] += 1
        else:
            with open(os.path.join(VOL, 'failures.jsonl'), 'a') as f:
                f.write(json.dumps({'lemma': lemma, 'kind': gate.get('kind'),
                                    'errors': gate.get('errors'),
                                    'result': env.get('result', '')[:2000],
                                    'provenance': prov}) + '\n')
            state['fail'] += 1

    def log_transport_error(lemma, err):
        print(f'ERROR {lemma}: {str(err)[:200]}', file=sys.stderr)
        with open(os.path.join(VOL, 'transport-errors.jsonl'), 'a') as f:
            f.write(json.dumps({'lemma': lemma, 'error': str(err)[:500]}) + '\n')

    # sliding-window scheduler with ADAPTIVE concurrency (AIMD): keep `target`
    # lemmas in flight; +2 after target-many successes (if RAM headroom),
    # halve on a transient rate-limit. Lemmas interrupted by a limit are
    # requeued, never burned. The pool is sized at the ceiling; the effective
    # concurrency is how many futures we keep in flight.
    pending = collections.deque(todo)
    processed, last_report = 0, 0
    target, succ_since = args.concurrency, 0
    with ThreadPoolExecutor(max_workers=args.concurrency_max) as ex:
        inflight = {}
        while pending or inflight:
            if (args.max_cost_usd and pending
                    and round_tot['costUSD'] >= args.max_cost_usd):
                print(f'round budget ${args.max_cost_usd:.0f} reached '
                      f'(${round_tot["costUSD"]:.2f} API-equiv, '
                      f'{round_tot["calls"]} calls); stopping submissions',
                      file=sys.stderr)
                pending.clear()
            while pending and len(inflight) < target:
                window_gate()
                it = pending.popleft()
                inflight[ex.submit(process, it)] = it
            if not inflight:
                continue
            done_futs, _ = wait(set(inflight), return_when=FIRST_COMPLETED)
            limit_hit, rate_limited = None, False
            for fu in done_futs:
                it = inflight.pop(fu)
                try:
                    fu.result(); processed += 1; succ_since += 1
                except UsageLimit as e:
                    pending.appendleft(it); limit_hit = (e.msg, it['lemma'])
                except RateLimited as e:
                    pending.appendleft(it); rate_limited = True
                    print(f'rate-limited at {it["lemma"]}: {e.msg[:120]}',
                          file=sys.stderr)
                except Exception as e:
                    processed += 1; log_transport_error(it['lemma'], e)
            if rate_limited and not limit_hit:
                target = max(4, target // 2); succ_since = 0
                print(f'concurrency target halved -> {target}', file=sys.stderr)
                time.sleep(10)
            elif succ_since >= target and target < args.concurrency_max:
                mem = mem_available_mb()
                if mem is None or mem > 1000:
                    target = min(args.concurrency_max, target + 2); succ_since = 0
                    print(f'concurrency target raised -> {target} '
                          f'(MemAvailable {mem} MB)', file=sys.stderr)
                else:
                    succ_since = 0   # hold: box RAM is the binding constraint
            mem = mem_available_mb()
            if mem is not None and mem < 600 and target > 4:
                target = max(4, target - 2)
                print(f'RAM guard: MemAvailable {mem} MB, target -> {target}',
                      file=sys.stderr)
            if limit_hit:
                # drain in-flight work before sleeping; requeue anything that
                # also hit the limit
                for fu, it in list(inflight.items()):
                    try:
                        fu.result(); processed += 1
                    except UsageLimit:
                        pending.appendleft(it)
                    except Exception as e:
                        processed += 1; log_transport_error(it['lemma'], e)
                inflight.clear()
                msg, lemma = limit_hit
                slp = parse_reset_seconds(msg)
                slp = (slp + 600) if slp is not None else 3600
                print(f'usage limit hit at {lemma}; backing off {slp/60:.0f} min',
                      file=sys.stderr)
                log_window(); state['windowStart'] = None
                time.sleep(slp)
            if processed - last_report >= 25:
                last_report = processed
                print(f'progress: {processed}/{len(todo)} done, {len(pending)} queued, '
                      f'target {target}; window calls {state["calls"]}, ok {state["ok"]} '
                      f'fail {state["fail"]} cf {state["cf"]}; round '
                      f'${round_tot["costUSD"]:.2f} API-equiv / {round_tot["calls"]} calls',
                      file=sys.stderr)
    log_window()
    print(f'ROUND COMPLETE: {processed} lemmas, {round_tot["calls"]} calls, '
          f'${round_tot["costUSD"]:.2f} API-equiv', file=sys.stderr)

if __name__ == '__main__':
    main()
