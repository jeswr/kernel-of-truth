#!/usr/bin/env python3
"""haiku-tier stage 0 — definitional-text fetcher (Wiktionary + Wikipedia).

For each inventory lemma, fetches:
  wiktionary — en.wiktionary.org/api/rest_v1/page/definition/{lemma}
               (English section only; HTML stripped; revision from the ETag)
  wikipedia  — en.wikipedia.org/api/rest_v1/page/summary/{lemma}
               (lead extract; revision+tid from the body; disambiguation pages
               recorded as such, NOT counted as definitional text)

Politeness: single-threaded, >= MIN_INTERVAL s between requests, identifying
User-Agent with contact address, honours 429/503 with backoff. Responses are
cached to data/haiku-tier/cache/defs/{source}/{lemma}.json (gitignored);
a cached entry (success OR terminal failure) is never re-fetched.

Usage:
  nice -n 10 python3 fetch-definitions.py --sample 100      # stratified test
  nice -n 10 python3 fetch-definitions.py --lemmas a,b,c    # explicit list
  nice -n 10 python3 fetch-definitions.py --all             # full inventory (stage 2 only)
Writes fetch-report.md for --sample runs.
"""
import argparse, html, json, os, re, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
INV = os.path.join(HERE, '..', 'inventory', 'inventory.jsonl')
CACHE = os.path.join(HERE, '..', 'cache', 'defs')
UA = 'kernel-of-truth-haiku-tier/0.1 (research; contact: jesu4460@ox.ac.uk)'
MIN_INTERVAL = 0.6            # seconds between HTTP requests (both sources)
_last = [0.0]

TAG_RE = re.compile(r'<[^>]+>')

def strip_html(s):
    return html.unescape(TAG_RE.sub('', s)).strip()

def _get(url):
    wait = MIN_INTERVAL - (time.monotonic() - _last[0])
    if wait > 0: time.sleep(wait)
    req = urllib.request.Request(url, headers={'User-Agent': UA,
                                               'Accept': 'application/json'})
    for attempt in range(4):
        _last[0] = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, dict(r.headers), r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 1)); continue
            return e.code, dict(e.headers or {}), ''
        except Exception as e:               # network blip: one retry
            if attempt < 3: time.sleep(2 ** (attempt + 1)); continue
            return -1, {'error': str(e)}, ''
    return -1, {}, ''

def fetch_wiktionary(lemma):
    st, hdr, body = _get('https://en.wiktionary.org/api/rest_v1/page/definition/'
                         f'{urllib.parse.quote(lemma)}?redirect=true')
    out = {'source': 'wiktionary', 'lemma': lemma, 'status': st,
           'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    # RESTBase ETag = "<revision>/<tid>"
    etag = (hdr.get('ETag') or hdr.get('etag') or '').strip('W/"')
    if etag: out['revision'] = etag
    if st == 200:
        data = json.loads(body)
        senses = []
        for entry in data.get('en', []):
            pos = entry.get('partOfSpeech')
            for d in entry.get('definitions', []):
                txt = strip_html(d.get('definition', ''))
                if txt:
                    ex = [strip_html(e) for e in (d.get('parsedExamples') and
                          [pe.get('example','') for pe in d['parsedExamples']] or [])][:2]
                    senses.append({'pos': pos, 'definition': txt,
                                   **({'examples': ex} if ex else {})})
        out['senses'] = senses
        out['ok'] = len(senses) > 0
    else:
        out['ok'] = False
    return out

def fetch_wikipedia(lemma):
    st, hdr, body = _get('https://en.wikipedia.org/api/rest_v1/page/summary/'
                         f'{urllib.parse.quote(lemma)}?redirect=true')
    out = {'source': 'wikipedia', 'lemma': lemma, 'status': st,
           'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    if st == 200:
        data = json.loads(body)
        out['title'] = data.get('title')
        out['type'] = data.get('type')            # 'standard' | 'disambiguation'
        out['revision'] = data.get('revision')
        out['tid'] = data.get('tid')
        out['description'] = data.get('description')
        out['extract'] = data.get('extract')
        out['ok'] = (data.get('type') == 'standard'
                     and bool((data.get('extract') or '').strip()))
    else:
        out['ok'] = False
    return out

def cached_fetch(source, lemma, fn):
    d = os.path.join(CACHE, source)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{lemma}.json')
    if os.path.exists(path):
        return json.load(open(path)), True
    rec = fn(lemma)
    if rec['status'] == -1:      # transport failure: don't cache
        return rec, False
    with open(path, 'w') as f: json.dump(rec, f, ensure_ascii=False, indent=1)
    return rec, False

def load_inventory():
    return [json.loads(l) for l in open(INV)]

def stratified_sample(items, n):
    """Deterministic: n/3 per band, evenly spaced by rank within the band."""
    out = []
    per = n // 3
    for band in 'ABC':
        rows = [it for it in items if it['band'] == band]
        step = max(1, len(rows) // per)
        out.extend(rows[::step][:per])
    return out[:n]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int)
    ap.add_argument('--lemmas')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--report', default=os.path.join(HERE, 'fetch-report.md'))
    args = ap.parse_args()
    items = load_inventory()
    if args.lemmas:
        want = set(args.lemmas.split(','))
        rows = [it for it in items if it['lemma'] in want]
        rows += [{'lemma': w, 'band': '?', 'rank': None}
                 for w in want - {r['lemma'] for r in rows}]
    elif args.sample:
        rows = stratified_sample(items, args.sample)
    elif args.all:
        rows = items
    else:
        ap.error('one of --sample/--lemmas/--all required')

    stats = {'wiktionary': [], 'wikipedia': []}
    for i, it in enumerate(rows):
        lem = it['lemma']
        wt, _ = cached_fetch('wiktionary', lem, fetch_wiktionary)
        wp, _ = cached_fetch('wikipedia', lem, fetch_wikipedia)
        stats['wiktionary'].append((it, wt))
        stats['wikipedia'].append((it, wp))
        if (i + 1) % 25 == 0:
            print(f'  {i+1}/{len(rows)} fetched', file=sys.stderr)

    # report
    def rate(src, band=None):
        xs = [(it, r) for it, r in stats[src] if band is None or it['band'] == band]
        ok = sum(1 for _, r in xs if r.get('ok'))
        return ok, len(xs)
    lines = [f'# fetch test — {len(rows)} lemmas, {time.strftime("%Y-%m-%d")}', '',
             '| source | band A | band B | band C | overall |', '|---|---|---|---|---|']
    for src in ('wiktionary', 'wikipedia'):
        cells = []
        for b in ('A', 'B', 'C', None):
            ok, n = rate(src, b)
            cells.append(f'{ok}/{n} ({100*ok/max(n,1):.0f}%)')
        lines.append(f'| {src} | ' + ' | '.join(cells) + ' |')
    wp_dab = sum(1 for _, r in stats['wikipedia'] if r.get('type') == 'disambiguation')
    wp_404 = sum(1 for _, r in stats['wikipedia'] if r.get('status') == 404)
    wt_404 = sum(1 for _, r in stats['wiktionary'] if r.get('status') == 404)
    lines += ['', f'wikipedia: {wp_dab} disambiguation pages (not counted as ok), '
                  f'{wp_404} 404s. wiktionary: {wt_404} 404s.',
              '', 'Failures:', '']
    for src in ('wiktionary', 'wikipedia'):
        bad = [f"{it['lemma']}({it['band']}:{r.get('type') or r.get('status')})"
               for it, r in stats[src] if not r.get('ok')]
        lines.append(f'- {src}: ' + (', '.join(bad) if bad else 'none'))
    lines += ['', 'Revisions recorded per record in cache/defs/ (wiktionary: ETag '
              'revision/tid; wikipedia: body revision+tid). Cache is gitignored; '
              'the fetcher is deterministic modulo upstream edits — the pinned '
              'revision ids in each provenance block are what stage-2 records cite.']
    if args.sample:
        open(args.report, 'w').write('\n'.join(lines) + '\n')
        print(f'report -> {args.report}')
    print('\n'.join(lines[2:8]))

if __name__ == '__main__':
    main()
