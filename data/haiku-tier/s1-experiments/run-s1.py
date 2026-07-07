#!/usr/bin/env python3
"""haiku-tier stage 1 — experiment runner.

Runs the 50 stage-1 concepts through claude-haiku via `claude -p` for a given
framework (A: molecule-first, B: explication-first, C: self-check pass over
framework A's drafts). Saves the full CLI JSON envelope (usage + cost + result)
to outputs/<FW>/<lemma>.json. Skips lemmas already present (resumable).

Pinned call configuration (any change = pipeline version change):
  env MAX_THINKING_TOKENS=0
  claude -p --model claude-haiku-4-5-20251001 --system-prompt-file <fw file>
    --tools "" --strict-mcp-config --exclude-dynamic-system-prompt-sections
    --effort low --output-format json --max-turns 1
Concurrency 2 (box has 2 shared cores; calls are network-bound; directive <=4).
First call runs alone to warm the prompt cache.

Usage: nice -n 10 python3 run-s1.py A [B C ...]
"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = 'claude-haiku-4-5-20251001'
CONCURRENCY = 2

def call_claude(system_file, user_text, timeout=300):
    env = dict(os.environ, MAX_THINKING_TOKENS='0')
    cmd = ['nice', '-n', '10', 'claude', '-p', '--model', MODEL,
           '--system-prompt-file', system_file, '--tools', '',
           '--strict-mcp-config', '--exclude-dynamic-system-prompt-sections',
           '--effort', 'low', '--output-format', 'json', '--max-turns', '1']
    r = subprocess.run(cmd, input=user_text, capture_output=True, text=True,
                       env=env, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f'claude exit {r.returncode}: {r.stderr[:400] or r.stdout[:400]}')
    return json.loads(r.stdout)

def run_framework(fw):
    outdir = os.path.join(HERE, 'outputs', fw)
    os.makedirs(outdir, exist_ok=True)
    concepts = json.load(open(os.path.join(HERE, 'concepts.json')))
    SELFCHECK = {'C': 'A', 'E': 'D', 'F': 'A', 'G': 'A'}  # self-check: fw -> draft source
    # G = gate-in-the-loop: repair prompt (system-F) + the REAL validator
    # errors for the draft appended to the user turn.
    gate_errors = {}
    if fw == 'G':
        gr = json.load(open(os.path.join(HERE, 'gate-results-A.json')))
        gate_errors = {r['lemma']: r.get('errors', []) for r in gr['rows']}
    sysfile = os.path.join(HERE, 'prompts',
                           'system-' + ('F' if fw in ('F', 'G') else ('C' if fw in SELFCHECK else fw)) + '.txt')

    def user_prompt(lemma):
        base = open(os.path.join(HERE, 'prompts', 'user', lemma + '.txt')).read()
        if fw not in SELFCHECK:
            return base
        draft_env = json.load(open(os.path.join(HERE, 'outputs', SELFCHECK[fw], lemma + '.json')))
        out = base + '\n\nDRAFT (from an earlier pass; check and correct it):\n' + \
              draft_env['result'].strip()
        if fw == 'G':
            errs = gate_errors.get(lemma, [])
            if errs:
                out += ('\n\nMECHANICAL GATE ERRORS for this draft (fix every one; '
                        'the same validator will re-run):\n- ' + '\n- '.join(errs[:25]))
            else:
                out += '\n\nMECHANICAL GATE ERRORS for this draft: none — the draft passed; return it unchanged.'
        return out

    todo = [c['lemma'] for c in concepts
            if not os.path.exists(os.path.join(outdir, c['lemma'] + '.json'))]
    print(f'[{fw}] {len(todo)} to run', file=sys.stderr)

    def one(lemma):
        for attempt in (1, 2):
            try:
                env = call_claude(sysfile, user_prompt(lemma))
                with open(os.path.join(outdir, lemma + '.json'), 'w') as f:
                    json.dump(env, f, indent=1)
                return lemma, env.get('total_cost_usd'), None
            except Exception as e:
                if attempt == 2: return lemma, None, str(e)[:200]
                time.sleep(10)

    results = []
    if todo:                      # warm the prompt cache with one solo call
        results.append(one(todo[0]))
        print(f'[{fw}] warm: {results[0]}', file=sys.stderr)
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        for res in ex.map(one, todo[1:]):
            results.append(res)
            print(f'[{fw}] {res}', file=sys.stderr)
    errs = [r for r in results if r[2]]
    print(f'[{fw}] done: {len(results)-len(errs)} ok, {len(errs)} failed'
          + (f' -> {errs}' if errs else ''), file=sys.stderr)

if __name__ == '__main__':
    for fw in sys.argv[1:]:
        run_framework(fw)
