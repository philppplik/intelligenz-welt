#!/usr/bin/env python3
"""Intelligenz Welt site search index (post-build step, called at the end of site/build.py after articles.py).

Writes <out>/search-index.json for the client-side search on /suche/ (no external service, no dependencies).
Sources: content/articles/*.json (editorial articles), site/src/artikel_*.html (legacy analyses, slugs/categories
from the ART list in site/build.py), data/ai_archive.json (KI-Pulse headlines, latest 300, external links)
and the main static pages. Stdlib only.
Usage: python3 tools/search.py <out-dir>"""
import sys, os, re, json, glob, html, datetime

BASE = 'https://intelligenz-welt.de'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SECTIONS = {'news': 'News', 'trends': 'Trends', 'tools': 'Tools', 'modelle': 'Modelle', 'analyse': 'Analyse', 'praxis': 'Praxis'}
MAX_BODY = 6000
NEWS_LIMIT = 300

def clean_inline(t):
    t = re.sub(r'\[\^(\d+)\]', r'[\1]', t or '')
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)', r'\1', t)
    return re.sub(r'[*_`]', '', t)

def strip_tags(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()

def de_date(iso):
    try:
        return datetime.datetime.fromisoformat(iso).strftime('%d.%m.%Y')
    except Exception:
        return iso[:10]

def epoch(iso):
    try:
        return int(datetime.datetime.fromisoformat(iso).timestamp())
    except Exception:
        return 0

def article_text(a):
    parts = list(a.get('key_takeaways', []))
    for b in a.get('body', []):
        if b.get('x'): parts.append(b['x'])
        parts.extend(b.get('items', []) or [])
        for r in b.get('rows', []) or []: parts.extend(str(c) for c in r)
    for q in a.get('faq', []) or []: parts += [q.get('q', ''), q.get('a', '')]
    return clean_inline(' '.join(parts))[:MAX_BODY]

def editorial_docs(now):
    docs = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'content/articles/*.json'))):
        try:
            a = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        pub = epoch(a.get('published', ''))
        if pub and pub > now: continue  # scheduled article, not built
        docs.append({
            't': a['title'], 'u': '/artikel/%s/' % a['slug'], 'k': SECTIONS.get(a.get('section', ''), a.get('section', '')),
            'd': a.get('dek', ''), 'g': ' '.join(a.get('tags', [])), 'x': article_text(a),
            'ts': pub, 'dt': de_date(a.get('published', ''))})
    return docs

def legacy_docs():
    # categories/dates of the legacy analyses live in the ART list of site/build.py (single source)
    src = open(os.path.join(ROOT, 'site/build.py'), encoding='utf-8').read()
    meta = {s: (c, d) for s, c, d in re.findall(r"\('([a-z0-9-]+)',\s*'([^']+)',\s*'([0-9-]+)'\)", src)}
    docs = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'site/src/artikel_*.html'))):
        slug = os.path.basename(p)[len('artikel_'):-len('.html')]
        h = open(p, encoding='utf-8').read()
        m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
        if not m: continue
        title = strip_tags(m.group(1))
        ll = re.search(r'class="lead-text">(.*?)</div>', h, re.S)
        art = re.search(r'<article>(.*?)</article>', h, re.S)
        cat, date = meta.get(slug, ('Analyse', ''))
        docs.append({
            't': title, 'u': '/artikel/%s/' % slug, 'k': cat,
            'd': strip_tags(ll.group(1))[:220] if ll else '', 'g': '',
            'x': strip_tags(art.group(1))[:MAX_BODY] if art else '',
            'ts': epoch(date + 'T09:00:00+01:00') if date else 0, 'dt': de_date(date)})
    return docs

def news_docs():
    try:
        arch = json.load(open(os.path.join(ROOT, 'data/ai_archive.json'), encoding='utf-8'))
    except Exception:
        return []
    docs = []
    for i in arch[:NEWS_LIMIT]:
        if not i.get('title') or not i.get('url'): continue
        docs.append({'t': i['title'], 'u': i['url'], 'k': i.get('src', ''), 'd': i.get('sum', ''), 'g': '',
                     'x': '', 'ts': int(i.get('ts') or 0),
                     'dt': datetime.datetime.fromtimestamp(i['ts']).strftime('%d.%m.%Y') if i.get('ts') else '', 'ext': 1})
    return docs

PAGES = [
    ('KI-News: Das Archiv', '/news/', 'Seite', 'Aktuelle Nachrichten zu KI, LLMs und Agenten, automatisch aus öffentlichen Feeds aggregiert.'),
    ('Modell-Radar', '/modelle/', 'Seite', 'Die trendendsten Modelle auf Hugging Face: Likes, Downloads, Aufgabenbereich.'),
    ('Artikel', '/artikel/', 'Seite', 'Alle redaktionellen Artikel von Philipp Paulik mit Quellen und Einordnung.'),
    ('Tagesausgabe als PDF', '/berichte/', 'Seite', 'Die tägliche Ausgabe als PDF: Meldung des Tages, neueste Artikel, KI-Pulse und Impressum.'),
    ('Über uns', '/ueber-uns/', 'Seite', 'Intelligenz Welt ist ein unabhängiges deutschsprachiges KI-Magazin von Philipp Paulik.'),
]

def main():
    out = sys.argv[1]
    now = int(datetime.datetime.now().timestamp())
    docs = editorial_docs(now) + news_docs()
    docs += [{'t': t, 'u': u, 'k': k, 'd': d, 'g': '', 'x': '', 'ts': 0, 'dt': ''} for t, u, k, d in PAGES]
    payload = {'generated': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'docs': docs}
    with open(os.path.join(out, 'search-index.json'), 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
    print('search: %d documents indexed' % len(docs))

if __name__ == '__main__':
    main()
