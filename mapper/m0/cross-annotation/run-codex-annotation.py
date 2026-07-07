#!/usr/bin/env python3
"""Cross-model (OpenAI codex CLI / GPT) annotation pass over the M0a
stratified sample (mapper/m0/annotation-sample.jsonl, 300 items).

This is an INDEPENDENT second-AI-model pass. It does NOT satisfy the
pre-registered human-annotation item (poc-design.md Phase M / M0a); its
purpose is (a) cross-model-family agreement measurement against the
Claude-lineage agent judgments (mapper/m0/agent-judgments.jsonl) and
(b) a ranked disagreement list to prioritise the human pass.

Method (fail-closed):
- 15 serial batches of 20 items, each rendered into a self-contained
  judging prompt (context before/surface/after, mapped target or
  abstain/unmapped status, stratum-appropriate question mirroring the
  sample's own `instructions` field, strict JSON-array output contract).
- Invoked via `nice -n 10 codex exec --skip-git-repo-check` with the last
  agent message captured via -o. Raw stdout, prompts and last messages
  are committed under raw/.
- Parsing is strict: JSON array of {itemId, judgment} with exactly the
  batch's itemIds and judgment in {correct,incorrect,unclear}. A batch
  that fails validation is retried ONCE with a stricter instruction;
  if it still fails it is recorded as FAILED (items get no judgment)
  rather than guessed at.
- Resumable: a batch whose raw/batch-NN.parsed.json already exists is
  skipped on re-run.

Label semantics (uniform "judge the mapper's decision" polarity so one
correct|incorrect|unclear scale covers all four strata):
- concept/prime: correct iff the mapped kernel target is the contextual
  word sense of the token (same criterion as the Claude agent pass).
- abstain: correct iff abstention was the right outcome (NO listed
  candidate is the correct annotation in context); incorrect iff at
  least one candidate IS correct (a recall miss).
  Equivalence to agent labels: correct ~ no-candidate-correct,
  incorrect ~ candidate-correct.
- none: correct iff leaving the token unmapped was right (no kernel-v0
  target is its correct annotation); incorrect iff it should have
  mapped (a recall miss). correct ~ correctly-unmapped,
  incorrect ~ should-map.
"""
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
M0 = os.path.dirname(HERE)
RAW = os.path.join(HERE, 'raw')
BATCH_SIZE = 20
ANNOTATOR = 'codex-gpt'

os.makedirs(RAW, exist_ok=True)

items = [json.loads(l) for l in open(os.path.join(M0, 'annotation-sample.jsonl'))]
assert len(items) == 300, len(items)

HEADER = """You are an independent annotator judging the output of a deterministic \
word-sense mapper ("kernel mapper") over children's-story text (TinyStories). The mapper maps \
word tokens to a small fixed inventory: kernel-v0 CONCEPTS (urn:kernel-v0:<name> — everyday \
concepts named by their gloss word, e.g. urn:kernel-v0:help = the helping sense of "help") and \
NSM-style semantic PRIMES (prime:<NAME>, e.g. prime:SAY, prime:LIKE~AS~WAY = the \
similarity/manner sense "like/as/way", prime:AFTER~TIME = temporal after). For some tokens it \
ABSTAINED (recorded candidate targets but committed to none) and some tokens it left UNMAPPED.

Judge each item below ON ITS CONTEXTUAL WORD SENSE ONLY. The target's sense is the one its \
name/gloss word denotes literally. Light-verb, phrasal-verb, idiomatic and auxiliary uses whose \
sense differs from the target's literal sense are incorrect (e.g. causative "make her feel safe" \
is NOT the creation sense of make; auxiliary "do you know" is NOT the action prime DO; \
"liked to play" = enjoy is NOT similarity LIKE~AS~WAY). Use "unclear" only for genuinely \
contestable sense assignments.

Per-item question by kind:
- MAPPED (concept or prime): judgment=correct iff the mapped target is the meaning of this \
token in this context; incorrect iff it is not; unclear if genuinely contestable.
- ABSTAINED: the mapper recorded candidates but mapped nothing. judgment=correct iff \
abstention was right, i.e. NO listed candidate is the correct annotation for this token in \
context; judgment=incorrect iff at least ONE listed candidate IS the correct annotation \
(the mapper should have committed); unclear if genuinely contestable.
- UNMAPPED: the mapper mapped nothing and recorded nothing. judgment=correct iff that was \
right (no kernel-v0 concept/prime with a matching gloss would be the correct annotation for \
this token in context — grammatical function words, proper names etc.); judgment=incorrect \
iff the token clearly SHOULD have mapped to some everyday-concept or semantic-prime target; \
unclear if genuinely contestable.

OUTPUT CONTRACT (STRICT): reply with a single JSON array and NOTHING else — no prose, no \
markdown fences, no keys other than itemId and judgment. One entry per item, in order:
[{"itemId": "m0a-001", "judgment": "correct"}, ...]
judgment MUST be exactly one of: correct | incorrect | unclear.
"""

STRICTER = """
REMINDER — your previous reply could not be parsed. Reply with ONLY the raw JSON array \
(no code fences, no commentary before or after, no trailing commas). It must contain exactly \
one object per listed itemId, each object exactly {"itemId": "...", "judgment": \
"correct"|"incorrect"|"unclear"}.
"""


def render_item(it):
    d = it['decision']
    lines = [f"itemId: {it['itemId']}"]
    ctx = f"...{it['contextBefore']}«TOKEN: {it['surface']}»{it['contextAfter']}..."
    lines.append(f"context: {ctx}")
    if d['kind'] in ('concept', 'prime'):
        lines.append(f"mapper decision: MAPPED ({d['kind']}) -> {d['target']}")
    elif d['kind'] == 'abstain':
        lines.append(f"mapper decision: ABSTAINED; candidates: {', '.join(d['candidates'])}")
    else:
        lines.append("mapper decision: UNMAPPED (no target, no candidates)")
    return '\n'.join(lines)


def render_batch(batch):
    blocks = [render_item(it) for it in batch]
    ids = ', '.join(it['itemId'] for it in batch)
    return (HEADER + f"\nThis batch has {len(batch)} items ({ids}).\n\n"
            + '\n\n---\n\n'.join(blocks)
            + '\n\nNow output the JSON array (one entry per itemId above, same order).')


FENCE = re.compile(r'^\s*```(?:json)?\s*|\s*```\s*$', re.S)


def parse_last_message(text, want_ids):
    """Strict parse; returns list of {itemId, judgment} or raises ValueError."""
    t = FENCE.sub('', text.strip())
    # tolerate stray text around the array only if a single [...] region exists
    if not t.startswith('['):
        m = re.search(r'\[.*\]', t, re.S)
        if not m:
            raise ValueError('no JSON array found')
        t = m.group(0)
    data = json.loads(t)
    if isinstance(data, dict) and isinstance(data.get('judgments'), list):
        data = data['judgments']
    if not isinstance(data, list):
        raise ValueError('top level is not an array')
    out = {}
    for e in data:
        if not isinstance(e, dict) or set(e) - {'itemId', 'judgment'}:
            raise ValueError(f'bad entry shape: {e!r}')
        j = e.get('judgment')
        if j not in ('correct', 'incorrect', 'unclear'):
            raise ValueError(f'bad judgment: {e!r}')
        out[e['itemId']] = j
    if set(out) != set(want_ids):
        missing = sorted(set(want_ids) - set(out))
        extra = sorted(set(out) - set(want_ids))
        raise ValueError(f'id mismatch; missing={missing} extra={extra}')
    return [{'itemId': i, 'judgment': out[i]} for i in want_ids]


def extract_meta(text):
    meta = {}
    m = re.search(r'OpenAI Codex v([\w.\-]+)', text)
    if m:
        meta['codexVersion'] = m.group(1)
    m = re.search(r'^model:\s*(\S+)', text, re.M)
    if m:
        meta['model'] = m.group(1)
    return meta


def run_codex(prompt, tag):
    prompt_path = os.path.join(RAW, f'{tag}.prompt.txt')
    last_path = os.path.join(RAW, f'{tag}.last.txt')
    stdout_path = os.path.join(RAW, f'{tag}.stdout.txt')
    with open(prompt_path, 'w') as f:
        f.write(prompt)
    cmd = ['nice', '-n', '10', 'codex', 'exec', '--skip-git-repo-check',
           '--color', 'never', '-o', last_path, prompt]
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True,
                       text=True, timeout=900)
    with open(stdout_path, 'w') as f:
        f.write(r.stdout)
        if r.stderr:
            f.write('\n--- STDERR ---\n' + r.stderr)
    meta = extract_meta(r.stdout + '\n' + r.stderr)  # codex banner goes to stderr
    if r.returncode != 0:
        raise RuntimeError(f'codex exec exit {r.returncode}: {r.stderr[-500:]}')
    last = open(last_path).read() if os.path.exists(last_path) else ''
    return last, meta


def main():
    batches = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]
    failed = []
    metas = {}
    for bi, batch in enumerate(batches, 1):
        tag = f'batch-{bi:02d}'
        parsed_path = os.path.join(RAW, f'{tag}.parsed.json')
        if os.path.exists(parsed_path):
            print(f'{tag}: already parsed, skipping', flush=True)
            continue
        want_ids = [it['itemId'] for it in batch]
        prompt = render_batch(batch)
        t0 = time.time()
        try:
            last, meta = run_codex(prompt, tag)
        except Exception as e:
            print(f'{tag}: codex invocation FAILED ({e}); retrying once', flush=True)
            last, meta = '', {}
        parsed = None
        err = None
        if last:
            try:
                parsed = parse_last_message(last, want_ids)
            except ValueError as e:
                err = str(e)
        if parsed is None:
            print(f'{tag}: parse failed ({err}); retry with stricter instruction', flush=True)
            try:
                last, meta2 = run_codex(prompt + STRICTER, tag + '.retry')
                meta = meta or meta2
                parsed = parse_last_message(last, want_ids)
            except (ValueError, RuntimeError, Exception) as e:
                print(f'{tag}: retry FAILED ({e}); recording batch as failed', flush=True)
                failed.append({'batch': bi, 'itemIds': want_ids, 'error': str(e)})
                with open(os.path.join(RAW, f'{tag}.FAILED.json'), 'w') as f:
                    json.dump({'batch': bi, 'itemIds': want_ids, 'error': str(e)}, f, indent=2)
                continue
        metas[bi] = meta
        with open(parsed_path, 'w') as f:
            json.dump({'batch': bi, 'meta': meta, 'judgments': parsed}, f, indent=2)
        dt = time.time() - t0
        print(f'{tag}: OK ({len(parsed)} judgments, {dt:.0f}s, meta={meta})', flush=True)

    # assemble codex-judgments.jsonl from all parsed batches
    by_id = {it['itemId']: it for it in items}
    out_path = os.path.join(HERE, 'codex-judgments.jsonl')
    n = 0
    with open(out_path, 'w') as f:
        for bi in range(1, len(batches) + 1):
            parsed_path = os.path.join(RAW, f'batch-{bi:02d}.parsed.json')
            if not os.path.exists(parsed_path):
                continue
            rec = json.load(open(parsed_path))
            meta = rec.get('meta') or {}
            if not meta:  # earlier runs looked for the banner on stdout only
                stdout_path = os.path.join(RAW, f'batch-{bi:02d}.stdout.txt')
                if os.path.exists(stdout_path):
                    meta = extract_meta(open(stdout_path).read())
            for e in rec['judgments']:
                it = by_id[e['itemId']]
                f.write(json.dumps({
                    'itemId': e['itemId'], 'stratum': it['stratum'],
                    'surface': it['surface'], 'norm': it['norm'],
                    'decision': it['decision'], 'judgment': e['judgment'],
                    'annotator': ANNOTATOR,
                    'model': meta.get('model', 'unknown'),
                    'codexVersion': meta.get('codexVersion', 'unknown'),
                    'batch': bi, 'date': '2026-07-07',
                    'labelSemantics': 'judge-the-mapper-decision; abstain: correct~no-candidate-correct, incorrect~candidate-correct; none: correct~correctly-unmapped, incorrect~should-map',
                }) + '\n')
                n += 1
    print(f'wrote {n} judgments to {out_path}; failed batches: {len(failed)}')
    if failed:
        print(json.dumps(failed, indent=2))
        sys.exit(2)


if __name__ == '__main__':
    main()
