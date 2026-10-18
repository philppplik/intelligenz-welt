#!/usr/bin/env python3
"""Intelligenz Welt editorial article renderer (post-build step, called at the end of site/build.py).

Input : content/articles/<slug>.json + content/images/<slug>.jpg (1600x900, optional <slug>-800.jpg). Format: docs/EDITORIAL.md
Output: <out>/artikel/<slug>/index.html, <out>/artikel/index.html, <out>/thema/<section>/index.html, <out>/redaktion/index.html,
        <out>/assets/editorial/*, patched sitemap.xml (image entries), news-sitemap.xml (last 48 h), feed.xml, home page, nav.
Invalid articles fail the build with a clear message. Articles with a future "published" are skipped (scheduled).
Usage: python3 tools/articles.py <out-dir>      (stdlib only)"""
import sys, os, re, json, glob, html, shutil, struct, datetime, email.utils

BASE = 'https://intelligenz-welt.de'
PID = 'https://philipp-paulik.de/#person'
AUTHOR_URL = BASE + '/redakteur/philipp-paulik/'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
E = lambda s: html.escape(s or '', quote=True)
SECTIONS = {'news': 'News', 'trends': 'Trends', 'tools': 'Tools', 'modelle': 'Modelle', 'analyse': 'Analyse', 'praxis': 'Praxis'}
TYPES = {'news': 'NewsArticle', 'analysis': 'NewsArticle', 'explainer': 'Article'}
NEWS_TYPES = {'news', 'analysis'}
REQ = ['slug', 'title', 'dek', 'section', 'type', 'published', 'modified', 'author', 'tags', 'key_takeaways', 'hero', 'body', 'sources']
MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
DISCLOSURE = ('Transparenzhinweis: Dieser Artikel ist ein redaktioneller Beitrag von Philipp Paulik und entstand mit KI-Unterstützung '
              '(Recherche und Textentwurf). Alle Quellen sind unten verlinkt; Zahlen und Aussagen stammen aus diesen Quellen. '
              'Das Titelbild ist KI-generiert und im Bild entsprechend gekennzeichnet. Die News-Übersicht auf dieser Seite wird dagegen automatisch aus öffentlichen Feeds aggregiert. '
              '<a href="/redaktion/">So arbeiten wir</a>.')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from share import share_block, SHARE_CSS
CSS = ('<style>.ed .crumbs{font-size:14px;color:var(--mut);margin:0 0 14px}.ed .crumbs a,.ed .byline a,.ed .src a,.ed .more a,.ed .body a,.ed .note a{text-decoration:underline;text-underline-offset:3px}'
       '.ed .byline{color:var(--mut);font-size:14px;margin:6px 0 18px}.ed .byline a{color:var(--fg)}'
       '.ed figure{margin:0 0 22px}.ed figure img{width:100%;height:auto;border-radius:14px;display:block}.ed figcaption{font-size:13px;color:var(--mut);margin-top:8px}'
       '.ed .answer{background:var(--soft);border-left:4px solid var(--ac);border-radius:10px;padding:16px 18px;margin:0 0 20px}.ed .answer p{margin:0}'
       '.ed .facts{border:1px solid var(--line);border-radius:12px;padding:14px 18px 6px;margin:0 0 24px}.ed .facts h2{font-size:15px;margin:0 0 8px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut)}.ed .facts li{margin:6px 0}'
       '.ed .src li,.ed .more li,.ed .body li{margin:6px 0}.ed .note{font-size:13px;color:var(--mut);border-top:1px solid var(--line);margin-top:28px;padding-top:14px}'
       '.ed details{border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:8px 0}.ed summary{cursor:pointer;font-weight:600}'
       '.ed table.data{margin:18px 0}.ed .callout{border:1px solid var(--line);background:var(--soft);border-radius:10px;padding:14px 18px;margin:20px 0}.ed pre{overflow:auto;background:#0b1220;color:#e2e8f0;padding:14px;border-radius:10px;font-size:13px}'
       '.ed .fig img{width:100%;height:auto;border-radius:12px}</style>')

errors = []
def err(slug, m): errors.append('%s: %s' % (slug, m))

def jpeg_size(path):
    d = open(path, 'rb').read()
    if d[:2] != b'\xff\xd8': raise ValueError('not a JPEG')
    i = 2
    while i < len(d):
        if d[i] != 0xFF: i += 1; continue
        m = d[i + 1]
        if m in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', d[i + 5:i + 9]); return w, h
        i += 2 + struct.unpack('>H', d[i + 2:i + 4])[0]
    raise ValueError('no SOF')

def de_date(dt, time=True):
    s = '%d. %s %d' % (dt.day, MONTHS[dt.month - 1], dt.year)
    return s + (', %02d:%02d Uhr' % (dt.hour, dt.minute) if time else '')

def inline(t):
    t = E(t)
    t = re.sub(r'\[\^(\d+)\]', r'<sup><a href="#q\1" aria-label="Quelle \1">[\1]</a></sup>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)', lambda m: '<a href="%s"%s>%s</a>' % (m.group(2), '' if m.group(2).startswith('/') else ' rel="noopener"', m.group(1)), t)
    return t

def load(now, reserved):
    arts, seen = [], set()
    for p in sorted(glob.glob(os.path.join(ROOT, 'content/articles/*.json'))):
        s0 = os.path.basename(p)[:-5]
        try: a = json.load(open(p, encoding='utf-8'))
        except Exception as e: err(s0, 'invalid JSON: %s' % e); continue
        n0 = len(errors)
        for k in REQ:
            if k not in a: err(s0, 'missing field "%s"' % k)
        if len(errors) > n0: continue
        s = a['slug']
        if s != s0: err(s, 'slug differs from filename')
        if s in seen or s in reserved: err(s, 'slug not unique / collides with an existing article')
        seen.add(s)
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', s): err(s, 'slug must be lowercase ascii kebab-case')
        if a['section'] not in SECTIONS: err(s, 'section must be one of %s' % ', '.join(SECTIONS))
        if a['type'] not in TYPES: err(s, 'type must be news|analysis|explainer')
        if len(a['title']) > 110: err(s, 'title longer than 110 chars (%d)' % len(a['title']))
        if not 60 <= len(a['dek']) <= 300: err(s, 'dek must be 60-300 chars (is %d)' % len(a['dek']))
        if len(a['key_takeaways']) < 3: err(s, 'need >=3 key_takeaways')
        if len(a['sources']) < 1: err(s, 'need >=1 source (>=3 preferred)')
        for i, so in enumerate(a['sources']):
            for k in ('title', 'publisher', 'url'):
                if not so.get(k): err(s, 'sources[%d] missing %s' % (i, k))
            if not str(so.get('url', '')).startswith('https://'): err(s, 'sources[%d].url must be https' % i)
        if a['author'] != 'philipp-paulik': err(s, 'author must be philipp-paulik')
        try: pub = datetime.datetime.fromisoformat(a['published']); mod = datetime.datetime.fromisoformat(a['modified'])
        except Exception as e: err(s, 'bad date: %s' % e); continue
        if pub.tzinfo is None or mod.tzinfo is None: err(s, 'dates need a time zone offset, e.g. +02:00'); continue
        if mod < pub: err(s, 'modified before published')
        h = a['hero']
        if not h.get('alt') or not h.get('caption'): err(s, 'hero needs alt and caption')
        ip = os.path.join(ROOT, 'content/images/%s.jpg' % s)
        if not os.path.exists(ip): err(s, 'missing content/images/%s.jpg' % s)
        else:
            try:
                wh = jpeg_size(ip)
                if wh != (1600, 900): err(s, 'hero must be 1600x900 (is %dx%d)' % wh)
                if os.path.getsize(ip) > 350 * 1024: err(s, 'hero larger than 350 KB')
            except Exception as e: err(s, 'hero unreadable: %s' % e)
        for b in a['body']:
            if b.get('t') == 'figure':
                if not os.path.exists(os.path.join(ROOT, 'content/images', b.get('file', ''))): err(s, 'missing figure file %s' % b.get('file'))
                if not b.get('alt') or not b.get('caption'): err(s, 'figure needs alt and caption')
            elif b.get('t') not in ('p', 'h2', 'h3', 'ul', 'ol', 'quote', 'table', 'callout', 'code'): err(s, 'unknown block type %r' % b.get('t'))
        if pub > now: print('articles: skip (scheduled)', s); continue
        a['_pub'], a['_mod'] = pub, mod
        arts.append(a)
    arts.sort(key=lambda a: a['_pub'], reverse=True)
    return arts

def body_html(a):
    out = []
    for b in a['body']:
        t = b['t']
        if t == 'p': out.append('<p>%s</p>' % inline(b['x']))
        elif t in ('h2', 'h3'): out.append('<%s>%s</%s>' % (t, inline(b['x']), t))
        elif t in ('ul', 'ol'): out.append('<%s>%s</%s>' % (t, ''.join('<li>%s</li>' % inline(i) for i in b['items']), t))
        elif t == 'quote':
            c = ''
            if b.get('cite'): c = '<footer>%s</footer>' % (('<a href="%s" rel="noopener">%s</a>' % (E(b['url']), E(b['cite']))) if b.get('url') else E(b['cite']))
            out.append('<blockquote><p>%s</p>%s</blockquote>' % (inline(b['x']), c))
        elif t == 'table':
            cap = '<caption>%s</caption>' % E(b['caption']) if b.get('caption') else ''
            out.append('<div class="tw"><table class="data">%s<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cap, ''.join('<th scope="col">%s</th>' % inline(c) for c in b['head']), ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in b['rows'])))
        elif t == 'callout': out.append('<aside class="callout"><b>%s</b><p>%s</p></aside>' % (E(b.get('title', 'Hinweis')), inline(b['x'])))
        elif t == 'code': out.append('<pre><code>%s</code></pre>' % E(b['x']))
        elif t == 'figure':
            w, h = jpeg_size(os.path.join(ROOT, 'content/images', b['file']))
            cap = E(b['caption']) + (' (KI-generiert)' if b.get('ai_generated') and 'KI' not in b['caption'] else '')
            out.append('<figure class="fig"><img src="/assets/editorial/%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"><figcaption>%s</figcaption></figure>' % (E(b['file']), E(b['alt']), w, h, cap))
    return '\n'.join(out)

def words(a):
    txt = ' '.join(b.get('x', '') + ' ' + ' '.join(b.get('items', [])) for b in a['body']) + ' ' + ' '.join(a['key_takeaways'])
    return len(re.sub(r'<[^>]+>|[*\[\]()]', ' ', txt).split())

def ld_script(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'
ORG = {'@type': 'NewsMediaOrganization', '@id': BASE + '/#org', 'name': 'Intelligenz Welt', 'url': BASE + '/', 'logo': {'@type': 'ImageObject', 'url': BASE + '/assets/branding/logo-512.png', 'width': 512, 'height': 512}, 'founder': {'@id': PID}}

def template(out):
    t = open(os.path.join(out, 'impressum', 'index.html'), encoding='utf-8').read()
    i = t.find('</header>') + len('</header>'); j = t.find('<footer', i)
    return t[:i], t[j:]

def head_for(head, title, desc, url, og_type, img=None, alt='', pub=None, mod=None, extra=''):
    h = re.sub(r'<title>.*?</title>', '', head, flags=re.S)
    for pat in (r'<meta name="description"[^>]*>', r'<link rel="canonical"[^>]*>', r'<meta property="og:(title|description|url|type|image[^"]*)"[^>]*>', r'<meta name="twitter:[^"]*"[^>]*>'):
        h = re.sub(pat, '', h)
    new = ('<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s">'
           '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:type" content="%s">'
           '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s">') % (E(title), E(desc), url, E(title), E(desc), url, og_type, E(title), E(desc))
    if img:
        new += ('<meta property="og:image" content="%s"><meta property="og:image:width" content="1600"><meta property="og:image:height" content="900"><meta property="og:image:alt" content="%s">'
                '<meta name="twitter:image" content="%s"><meta name="twitter:image:alt" content="%s">') % (img, E(alt), img, E(alt))
    if pub: new += '<meta property="article:published_time" content="%s"><meta property="article:modified_time" content="%s"><meta property="article:author" content="%s"><link rel="author" href="%s">' % (pub, mod or pub, AUTHOR_URL, AUTHOR_URL)
    return h.replace('</head>', new + extra + CSS + '</head>', 1)

def article_page(a, arts, head, foot):
    s, h = a['slug'], a['hero']
    url = '%s/artikel/%s/' % (BASE, s)
    img_abs = '%s/assets/editorial/%s.jpg' % (BASE, s); img_rel = '/assets/editorial/%s.jpg' % s
    has800 = os.path.exists(os.path.join(ROOT, 'content/images/%s-800.jpg' % s))
    credit = h.get('credit') or ('KI-generiert (Intelligenz Welt)' if h.get('ai_generated') else '')
    image_ld = {'@type': 'ImageObject', '@id': url + '#image', 'url': img_abs, 'contentUrl': img_abs, 'width': 1600, 'height': 900, 'caption': h['caption'], 'description': h['alt'],
                'creditText': credit, 'creator': {'@type': 'Organization', 'name': 'Intelligenz Welt'}, 'license': BASE + '/redaktion/#bildrechte', 'acquireLicensePage': BASE + '/kontakt/'}
    if h.get('ai_generated'): image_ld['digitalSourceType'] = 'http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia'
    author = {'@type': 'Person', '@id': PID, 'name': 'Philipp Paulik', 'url': AUTHOR_URL, 'sameAs': ['https://philipp-paulik.de/']}
    graph = [{'@type': TYPES[a['type']], '@id': url + '#article', 'headline': a['title'], 'description': a['dek'], 'image': [image_ld], 'datePublished': a['published'], 'dateModified': a['modified'],
              'author': author, 'publisher': ORG, 'mainEntityOfPage': {'@type': 'WebPage', '@id': url}, 'inLanguage': 'de-DE', 'articleSection': SECTIONS[a['section']], 'keywords': ', '.join(a['tags']),
              'wordCount': words(a), 'isAccessibleForFree': True,
              'citation': [{'@type': 'CreativeWork', 'name': x['title'], 'url': x['url'], 'publisher': {'@type': 'Organization', 'name': x['publisher']}} for x in a['sources']]},
             {'@type': 'BreadcrumbList', 'itemListElement': [
                 {'@type': 'ListItem', 'position': 1, 'name': 'Intelligenz Welt', 'item': BASE + '/'},
                 {'@type': 'ListItem', 'position': 2, 'name': SECTIONS[a['section']], 'item': '%s/thema/%s/' % (BASE, a['section'])},
                 {'@type': 'ListItem', 'position': 3, 'name': a['title'], 'item': url}]}]
    if a.get('faq'):
        graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': q['a']}} for q in a['faq']]})
    hh = head_for(head, '%s | Intelligenz Welt' % a['title'], meta_trunc(a['dek']), url, 'article', img_abs, h['alt'], a['published'], a['modified'], ld_script({'@context': 'https://schema.org', '@graph': graph}) + ''.join('<meta property="article:tag" content="%s">' % E(t) for t in a['tags']))
    rel = [x for x in arts if x['slug'] in a.get('related', [])] or [x for x in arts if x['slug'] != s][:4]
    faq = ('<h2>Häufige Fragen</h2>' + ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q['q']), inline(q['a'])) for q in a['faq'])) if a.get('faq') else ''
    src = ''.join('<li id="q%d"><a href="%s" rel="noopener" target="_blank">%s</a> (%s%s)</li>' % (i + 1, E(x['url']), E(x['title']), E(x['publisher']), (', abgerufen %s' % E(x['accessed'])) if x.get('accessed') else '') for i, x in enumerate(a['sources']))
    more = ('<h2>Weitere Artikel</h2><ul class="more">' + ''.join('<li><a href="/artikel/%s/">%s</a></li>' % (x['slug'], E(x['title'])) for x in rel) + '</ul>') if rel else ''
    mins = max(2, round(words(a) / 200))
    modtxt = (' · aktualisiert <time datetime="%s">%s</time>' % (a['modified'], de_date(a['_mod']))) if a['_mod'] != a['_pub'] else ''
    srcset = ' srcset="/assets/editorial/%s-800.jpg 800w, %s 1600w" sizes="(max-width:800px) 100vw, 760px"' % (s, img_rel) if has800 else ''
    facts = ''.join('<li>%s</li>' % inline(k) for k in a['key_takeaways'])
    method = ''
    if a.get('method'): method += '<h2>Methode</h2>' + ''.join('<p>%s</p>' % inline(x) for x in ([a['method']] if isinstance(a['method'], str) else a['method']))
    lim = a.get('limitations')
    if isinstance(lim, str): lim = [x for x in lim.split('\n') if x.strip()]
    if lim: method += '<h3>Grenzen</h3>' + (('<p>%s</p>' % inline(lim[0])) if isinstance(a.get('limitations'), str) and len(lim) == 1 else '<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(l) for l in lim))
    body = ('<article class="art ed"><nav class="crumbs" aria-label="Breadcrumb"><a href="/">Intelligenz Welt</a> / <a href="/thema/%s/">%s</a></nav>'
            '<span class="tag">%s</span><h1>%s</h1><p class="byline">Von <a rel="author" href="%s">Philipp Paulik</a> · <time datetime="%s">%s</time>%s · %d Min. Lesezeit</p>'
            '<figure><img src="%s"%s width="1600" height="900" alt="%s" fetchpriority="high" decoding="async"><figcaption>%s</figcaption></figure>'
            '<div class="facts"><h2>Die wichtigsten Fakten</h2><ul>%s</ul></div><div class="body">%s%s</div>%s<h2>Quellen</h2><ol class="src">%s</ol>%s%s<p class="note">%s</p></article>') % (
        a['section'], SECTIONS[a['section']], E(SECTIONS[a['section']]), E(a['title']), AUTHOR_URL, a['published'], de_date(a['_pub']), modtxt, mins,
        img_rel, srcset, E(h['alt']), E(h['caption']), facts, body_html(a), method, faq, src, more, share_block(url, a['title'], 'iw'), DISCLOSURE)
    return hh + body + foot

CSS = CSS.replace('</style>', SHARE_CSS % ('mut', 'soft', 'ac') + '</style>', 1)

def meta_trunc(t, n=157):
    if len(t) <= n: return t
    c = t[:n].rsplit(' ', 1)[0].rstrip(' ,;:.')
    return c + '…'

def card(a):
    return ('<a class="card" href="/artikel/%s/"><span class="tag">%s</span><h3>%s</h3><p>%s</p><div class="meta">%s · Philipp Paulik</div></a>' % (a['slug'], E(SECTIONS[a['section']]), E(a['title']), E(a['dek']), de_date(a['_pub'], False)))

def list_page(title, desc, url, h1, intro, arts, head, foot, crumb=None):
    ld = ld_script({'@context': 'https://schema.org', '@type': 'CollectionPage', '@id': url, 'name': title, 'url': url, 'inLanguage': 'de-DE', 'publisher': ORG,
                    'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': '%s/artikel/%s/' % (BASE, a['slug'])} for i, a in enumerate(arts)]}})
    hh = head_for(head, title, desc, url, 'website', extra=ld)
    return hh + '<div class="w ed"><div class="hero"><h1>%s</h1><p>%s</p></div><div class="cards">%s</div></div>' % (h1, intro, ''.join(card(a) for a in arts)) + foot

def redaktion_page(head, foot):
    url = BASE + '/redaktion/'
    hh = head_for(head, 'Redaktionelle Grundsätze | Intelligenz Welt', 'KI-Einsatz, Quellen, Bildrechte, Korrekturen und Unabhängigkeit bei Intelligenz Welt.', url, 'website')
    b = ('<article class="art ed"><h1>Redaktionelle Grundsätze</h1>'
         '<p>Intelligenz Welt wird von Philipp Paulik betrieben und verantwortet (<a href="/impressum/">Impressum</a>, <a href="/redakteur/philipp-paulik/">Autorenprofil</a>, <a href="/kontakt/">Kontakt</a>).</p>'
         '<h2>Zwei Bereiche</h2><p>Die <a href="/news/">KI-News</a> und das Modell-Radar werden automatisch aus öffentlichen Feeds und APIs aggregiert und führen zu den Originalquellen. Die <a href="/artikel/">Artikel</a> sind eigene redaktionelle Beiträge.</p>'
         '<h2 id="ki-einsatz">Einsatz von KI</h2><p>Artikel entstehen mit KI-Unterstützung (Recherche und Textentwurf). Themenauswahl, Quellenprüfung und Veröffentlichung verantwortet Philipp Paulik. Jeder Artikel nennt seine Quellen; Zahlen und Aussagen stammen aus diesen Quellen. Wir erfinden keine Zitate, Zahlen oder Studien und kennzeichnen Unsicherheit im Text.</p>'
         '<h2 id="bildrechte">Bilder</h2><p>Titelbilder sind KI-generiert und im Bild mit „KI-generiert“ gekennzeichnet. Sie sind Symbolbilder und kein offizielles Material der genannten Unternehmen. Alle Bilder haben einen Alternativtext. Eine Verlinkung mit Quellenangabe (Intelligenz Welt, intelligenz-welt.de) ist erlaubt; für weitere Nutzung bitte per E-Mail anfragen.</p>'
         '<h2>Korrekturen</h2><p>Fehler werden im Artikel korrigiert. Bei inhaltlichen Änderungen setzen wir das Aktualisierungsdatum und vermerken die Korrektur im Text. Hinweise bitte per E-Mail an die Adresse im <a href="/kontakt/">Kontakt</a>.</p>'
         '<h2>Werbung und Unabhängigkeit</h2><p>Intelligenz Welt verkauft derzeit keine Anzeigen und nimmt keine bezahlten Beiträge an. Sollte sich das ändern, wird bezahlter Inhalt klar gekennzeichnet. Wir nehmen keine Stellung zu parteipolitischen Themen.</p></article>')
    return hh + b + foot

def patch_sitemaps(out, arts, sections, now):
    p = os.path.join(out, 'sitemap.xml'); x = open(p, encoding='utf-8').read()
    x = x.replace('http://www.google.com/schemas/image/1.1', 'http://www.google.com/schemas/sitemap-image/1.1')
    if 'xmlns:image=' not in x: x = x.replace('<urlset ', '<urlset xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" ', 1)
    entries = [(BASE + '/artikel/', now.strftime('%Y-%m-%d'), ''), (BASE + '/redaktion/', now.strftime('%Y-%m-%d'), '')]
    for k in sections: entries.append(('%s/thema/%s/' % (BASE, k), max(a['modified'] for a in arts if a['section'] == k)[:10], ''))
    for a in arts:
        im = '<image:image><image:loc>%s/assets/editorial/%s.jpg</image:loc><image:title>%s</image:title><image:caption>%s</image:caption></image:image>' % (BASE, a['slug'], E(a['title']), E(a['hero']['alt']))
        entries.append(('%s/artikel/%s/' % (BASE, a['slug']), a['modified'], im))
    add = ''
    for u, lm, im in entries:
        x = re.sub(r'<url><loc>' + re.escape(u) + r'</loc>.*?</url>', '', x, flags=re.S)
        add += '<url><loc>%s</loc><lastmod>%s</lastmod>%s</url>' % (u, lm, im)
    open(p, 'w', encoding='utf-8').write(x.replace('</urlset>', add + '</urlset>'))
    items = ''
    for a in arts:
        if a['type'] in NEWS_TYPES and now - a['_pub'] <= datetime.timedelta(hours=48):
            items += ('<url><loc>%s/artikel/%s/</loc><news:news><news:publication><news:name>Intelligenz Welt</news:name><news:language>de</news:language></news:publication>'
                      '<news:publication_date>%s</news:publication_date><news:title>%s</news:title></news:news><image:image><image:loc>%s/assets/editorial/%s.jpg</image:loc></image:image></url>') % (BASE, a['slug'], a['published'], E(a['title']), BASE, a['slug'])
    open(os.path.join(out, 'news-sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + items + '</urlset>')
    return items.count('<url>')

def patch_feed(out, arts):
    p = os.path.join(out, 'feed.xml')
    if not os.path.exists(p): return
    x = open(p, encoding='utf-8').read(); items = ''
    for a in arts:
        u = '%s/artikel/%s/' % (BASE, a['slug'])
        if '<guid>%s</guid>' % u in x: continue
        items += '<item><title>%s</title><link>%s</link><guid>%s</guid><description>%s</description><pubDate>%s</pubDate><author>Philipp Paulik</author></item>' % (E(a['title']), u, u, E(a['dek']), email.utils.format_datetime(a['_pub']))
    x = x.replace('</description><language>de</language>', '</description><language>de</language>' + items, 1)
    open(p, 'w', encoding='utf-8').write(x)

def patch_site(out, arts):
    link = '<a class="l" href="/artikel/">Artikel</a>'
    for f in glob.glob(os.path.join(out, '**', '*.html'), recursive=True):
        t = open(f, encoding='utf-8').read(); o = t
        if 'href="/artikel/">Artikel</a>' not in t and '<a class="l" href="/analysen/">' in t:
            t = re.sub(r'(<a class="l[^"]*" href="/analysen/">Analysen</a>)', link + r'\1', t, count=1)
        if 'href="/redaktion/"' not in t and '<a href="/kontakt/">Kontakt</a>' in t:
            t = t.replace('<a href="/kontakt/">Kontakt</a>', '<a href="/kontakt/">Kontakt</a><a href="/redaktion/">Redaktion</a>', 1)
        if f == os.path.join(out, 'index.html') and 'id="neueste-artikel"' not in t and arts:
            sec = '<h2 class="sec" id="neueste-artikel">Neueste Artikel <a href="/artikel/">Alle →</a></h2><div class="cards">' + ''.join(card(a) for a in arts[:6]) + '</div>'
            t = t.replace('<h2 class="sec">Analysen &amp; Briefings', sec + '<h2 class="sec">Analysen &amp; Briefings', 1)
        if t != o: open(f, 'w', encoding='utf-8').write(t)

def main():
    out = sys.argv[1]
    now = datetime.datetime.now().astimezone()
    reserved = set(os.listdir(os.path.join(out, 'artikel'))) if os.path.isdir(os.path.join(out, 'artikel')) else set()
    arts = load(now, {r for r in reserved if not os.path.exists(os.path.join(ROOT, 'content/articles', r + '.json'))})
    if errors:
        print('ARTICLES FAILED:'); [print(' -', e) for e in errors]; sys.exit(1)
    head, foot = template(out)
    ad = os.path.join(out, 'assets', 'editorial'); os.makedirs(ad, exist_ok=True)
    for a in arts:
        s = a['slug']
        for fn in [s + '.jpg', s + '-800.jpg'] + [b['file'] for b in a['body'] if b['t'] == 'figure']:
            src = os.path.join(ROOT, 'content/images', fn)
            if os.path.exists(src): shutil.copy(src, os.path.join(ad, fn))
        d = os.path.join(out, 'artikel', s); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(article_page(a, arts, head, foot))
    sections = sorted({a['section'] for a in arts})
    if arts:
        os.makedirs(os.path.join(out, 'artikel'), exist_ok=True)
        open(os.path.join(out, 'artikel', 'index.html'), 'w', encoding='utf-8').write(list_page('Artikel: KI-Einordnung von Philipp Paulik | Intelligenz Welt', 'Redaktionelle KI-Artikel von Philipp Paulik: Modelle, Tools, Trends und Praxis. Mit Quellen, kurz und einordnend.', BASE + '/artikel/', 'Artikel', 'Eigene redaktionelle Beiträge zu KI mit Quellen und Einordnung, von <a rel="author" href="%s" style="text-decoration:underline">Philipp Paulik</a>.' % AUTHOR_URL, arts, head, foot))
        for k in sections:
            d = os.path.join(out, 'thema', k); os.makedirs(d, exist_ok=True)
            open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(list_page('%s | Intelligenz Welt' % SECTIONS[k], 'KI-Artikel zum Thema %s auf Intelligenz Welt.' % SECTIONS[k], '%s/thema/%s/' % (BASE, k), SECTIONS[k], 'Artikel zum Thema %s.' % SECTIONS[k], [a for a in arts if a['section'] == k], head, foot))
    os.makedirs(os.path.join(out, 'redaktion'), exist_ok=True)
    open(os.path.join(out, 'redaktion', 'index.html'), 'w', encoding='utf-8').write(redaktion_page(head, foot))
    n = patch_sitemaps(out, arts, sections, now) if arts else 0
    patch_feed(out, arts); patch_site(out, arts)
    branding(out); og_fallback(out)
    print('articles: %d rendered, %d in news-sitemap' % (len(arts), n))

def branding(out):
    bd = os.path.join(ROOT, 'content/branding')
    if not os.path.isdir(bd): return
    dst = os.path.join(out, 'assets', 'branding'); os.makedirs(dst, exist_ok=True)
    for f in os.listdir(bd):
        shutil.copy(os.path.join(bd, f), dst)
        if f in ('favicon.ico', 'favicon.svg', 'apple-touch-icon.png'): shutil.copy(os.path.join(bd, f), os.path.join(out, f))

def og_fallback(out):
    src = os.path.join(ROOT, 'content/images/og-default.jpg')
    if not os.path.exists(src): return
    os.makedirs(os.path.join(out, 'assets'), exist_ok=True); shutil.copy(src, os.path.join(out, 'assets', 'og-default.jpg'))
    img = BASE + '/assets/og-default.jpg'
    tags = ('<meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            '<meta property="og:image:alt" content="Intelligenz Welt: KI-News, Modell-Radar und Analysen auf Deutsch">'
            '<meta name="twitter:image" content="%s">' % (img, img))
    for dp, _, fs in os.walk(out):
        for f in fs:
            if not f.endswith('.html'): continue
            fp = os.path.join(dp, f); t = open(fp, encoding='utf-8').read()
            if 'property="og:image"' in t or 'noindex' in t or '</head>' not in t: continue
            if 'name="twitter:card"' not in t: tags_ = '<meta name="twitter:card" content="summary_large_image">' + tags
            else: tags_ = tags
            open(fp, 'w', encoding='utf-8').write(t.replace('</head>', tags_ + '</head>', 1))

if __name__ == '__main__': main()
