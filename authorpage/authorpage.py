#!/usr/bin/env python3
"""Generate the semantic author page for Philipp Paulik and link articles to it.

Usage: python3 authorpage.py <site-key> <output-dir> [--assets <dir>]
Reuses the header/footer of an existing page of the site as template.
Idempotent: safe to run on every build.
"""
import sys, os, re, json, glob, html, shutil, datetime

PID = 'https://philipp-paulik.de/#person'
PORTFOLIO = 'https://philipp-paulik.de/'
IMG = 'philipp-paulik-portrait-bibliothek-gruene-lampen'
SAMEAS = [
    ('GitHub', 'https://github.com/philppplik'),
    ('X', 'https://x.com/philppplik'),
    ('Instagram', 'https://instagram.com/philpplik'),
    ('YouTube', 'https://www.youtube.com/@philppplik'),
    ('LinkedIn', 'https://de.linkedin.com/in/philipp-paulik-7967753aa'),
    ('npm', 'https://www.npmjs.com/~philppplik'),
    ('paulikreisch.de', 'https://paulikreisch.de'),
    ('Daily Hob', 'https://hob.philipp-paulik.de'),
    ('Wikidata', 'https://www.wikidata.org/wiki/Q137996883'),
]
AUTHOR_PAGES = {
    'iw': ('Intelligenz Welt', 'https://intelligenz-welt.de/redakteur/philipp-paulik/'),
    'kfb': ('KI Fachblatt', 'https://kifachblatt.de/redakteur/philipp-paulik'),
    'fa': ('finanz adjust', 'https://finanz-adjust.de/redakteur/philipp-paulik/'),
    'hob': ('Daily Hob', 'https://hob.philipp-paulik.de/redakteur/'),
    'somnia': ('Somnia', 'https://somnia.philipp-paulik.de/entwickler/philipp-paulik/'),
}
DE = dict(
    lang='de', kicker='Redakteur bei {site}', role_h='Rolle auf dieser Seite', role='Betreiber und Redakteur',
    h_bio='Kurzprofil', h_facts='Fakten', h_proj='Projekte', h_web='Profile im Web', h_also='Auch auf', home='Start',
    facts=[('Name', 'Philipp Paulik (Handle: philppplik)'), ('Schwerpunkte', 'KI-Strategie und Agents, Webdesign, UI/UX, Software Engineering'),
           ('Code', 'TypeScript, Rust, Python'), ('Sprachen', 'Deutsch, Englisch'), ('Persönliche Website', 'philipp-paulik.de')],
    bio1=('Philipp Paulik ist KI-Pionier und KI-Stratege, Webdesigner, UI/UX-Designer, Software Engineer und Autor. '
          'Er entwickelt KI-Strategien und baut eigene Agents und Tools, die er als Open Source und als npm-Pakete veröffentlicht, '
          'darunter true-code, ZWEP, Flower und das Webdesign-Studio Somnia.'),
    jobtitle='KI-Pionier und KI-Stratege, Webdesigner, UI/UX-Designer, Software Engineer, Autor',
    alt='Philipp Paulik, Porträt: lächelnder Mann mit kurzem braunem Haar, Bart und Tweed-Sakko über schwarzem Pullover vor Bücherregalen mit grünen Leselampen',
    cap='Philipp Paulik', byline='Von', projects=[
        ('true-code', 'https://github.com/philppplik/true-code', 'Agentic Coding Harness in Rust'),
        ('ZWEP', 'https://zwep.philipp-paulik.de/', 'Self-hosted Suchmaschine mit MCP für KI-Agents'),
        ('Flower', 'https://flower.philipp-paulik.de/', 'ASCII Image Studio im Browser'),
        ('Somnia', 'https://somnia.philipp-paulik.de/', 'Open-Source-Webdesign-Studio'),
        ('Daily Hob', 'https://hob.philipp-paulik.de/', 'tägliches Briefing zu KI, Open Source und Design'),
        ('paulikreisch.de', 'https://paulikreisch.de', 'satirische Bücher'),
    ])
EN = dict(
    lang='en', kicker='Developer at {site}', role_h='Role on this site', role='Creator and developer',
    h_bio='Profile', h_facts='Facts', h_proj='Projects', h_web='Profiles on the web', h_also='Also on', home='Home',
    facts=[('Name', 'Philipp Paulik (handle: philppplik)'), ('Focus', 'AI strategy and agents, web design, UI/UX, software engineering'),
           ('Code', 'TypeScript, Rust, Python'), ('Languages', 'German, English'), ('Personal website', 'philipp-paulik.de')],
    bio1=('Philipp Paulik is an AI pioneer and strategist, web designer, UI/UX designer, software engineer and author. '
          'He develops AI strategies and builds his own agents and tools, which he releases as open source and as npm packages, '
          'including true-code, ZWEP, Flower and the web design studio Somnia.'),
    jobtitle='AI Pioneer and Strategist, Web Designer, UI/UX Designer, Software Engineer, Author',
    alt='Philipp Paulik, portrait: smiling man with short brown hair, stubble and a tweed jacket over a black sweater, in front of bookshelves with green reading lamps',
    cap='Philipp Paulik', byline='By', projects=[
        ('true-code', 'https://github.com/philppplik/true-code', 'agentic coding harness in Rust'),
        ('ZWEP', 'https://zwep.philipp-paulik.de/', 'self-hosted search engine with MCP for AI agents'),
        ('Flower', 'https://flower.philipp-paulik.de/', 'ASCII image studio in the browser'),
        ('Somnia', 'https://somnia.philipp-paulik.de/', 'open-source web design studio'),
        ('Daily Hob', 'https://hob.philipp-paulik.de/', 'daily briefing on AI, open source and design (German)'),
        ('paulikreisch.de', 'https://paulikreisch.de', 'satirical books (German)'),
    ])
SITES = {
 'iw': dict(L=DE, name='Intelligenz Welt', base='https://intelligenz-welt.de', page='redakteur/philipp-paulik/', layout='dir', template='impressum/index.html',
    open='<article class="art ap">', close='</article>', slash=True,
    desc='Philipp Paulik, Betreiber und Redakteur von Intelligenz Welt: KI-Pionier, Webdesigner, UI/UX-Designer, Software Engineer und Autor. Biografie, Projekte und Profile.',
    p2='Er betreibt Intelligenz Welt (siehe Impressum) und ist für die Inhalte verantwortlich. KI-News, Modell-Radar und Analysen erscheinen hier auf Deutsch; die News werden automatisch aus öffentlichen RSS-Feeds und APIs aggregiert.',
    articles=['artikel/*/index.html'], sitemaps=['sitemap.xml'], crumb_root='Intelligenz Welt'),
 'fa': dict(L=DE, name='finanz adjust', base='https://finanz-adjust.de', page='redakteur/philipp-paulik/', layout='dir', template='impressum/index.html',
    open='<div class="pg ap">', close='</div>', slash=True, start=r'<div class="pg">',
    desc='Philipp Paulik, Betreiber und Redakteur von finanz adjust: KI-Pionier, Webdesigner, UI/UX-Designer, Software Engineer und Autor. Biografie, Projekte und Profile.',
    p2='Er betreibt finanz adjust (siehe Impressum) und ist für die Inhalte verantwortlich. Kurse, Finanznachrichten und Tagesberichte dienen ausschließlich der Information und sind keine Anlageberatung.',
    articles=[], sitemaps=['sitemap.xml'], crumb_root='finanz adjust'),
 'kfb': dict(L=DE, name='KI Fachblatt', base='https://kifachblatt.de', page='redakteur/philipp-paulik', layout='file', template='ueber.html',
    open='<main id="main" class="ap"><div class="wrap">', close='</div></main>', slash=False,
    desc='Philipp Paulik, Redakteur und Betreiber des KI Fachblatts: KI-Pionier, Webdesigner, UI/UX-Designer, Software Engineer und Autor. Biografie, Projekte und Profile.',
    p2='Er betreibt das KI Fachblatt, ein deutschsprachiges Fachmagazin über künstliche Intelligenz: ruhig, genau, ohne Hype. Beiträge entstehen mit KI-Unterstützung und sind bewusst allgemein gehalten.',
    articles=['*.html'], sitemaps=['sitemap.xml'], crumb_root='KI Fachblatt'),
 'hob': dict(L=DE, name='Daily Hob', base='https://hob.philipp-paulik.de', page='redakteur/', layout='dir', template='impressum.html',
    open='<main id="main"><article class="legal-page ap">', close='</article></main>', slash=True,
    desc='Philipp Paulik, Redakteur und Betreiber des Daily Hob: KI-Pionier, Webdesigner, UI/UX-Designer, Software Engineer und Autor. Biografie, Projekte und Profile.',
    p2='Er betreibt das Daily Hob, das tägliche Briefing zu KI, Open Source, Informatik und Design: mit Originalquellen, Einordnung und, wenn vorhanden, Audio.',
    articles=['briefings/*.html'], sitemaps=['sitemap.xml'], crumb_root='Daily Hob'),
 'somnia': dict(L=EN, name='Somnia', base='https://somnia.philipp-paulik.de', page='entwickler/philipp-paulik/', layout='dir', template='impressum/index.html',
    open='<main id="main"><div class="wrap prose-page"><div class="prose ap">', close='</div></div></main>', slash=True,
    desc='Philipp Paulik, creator and developer of Somnia: AI pioneer, web designer, UI/UX designer, software engineer and author. Biography, projects and profiles.',
    p2='He is the creator and developer of Somnia, a free and open-source (MIT) local-first design studio, and the provider of this site (see the legal notice).',
    articles=[], sitemaps=['sitemap.xml'], crumb_root='Somnia'),
}
E = lambda s: html.escape(s, quote=True)

def rel_prefix(delta):
    return '../' * delta

def fix_rel(chunk, delta):
    if delta <= 0: return chunk
    pre = rel_prefix(delta)
    def sub(m):
        v = m.group(2)
        if re.match(r'(/|https?:|#|mailto:|tel:|data:|//)', v) or v == '': return m.group(0)
        return f'{m.group(1)}="{pre}{v}"'
    return re.sub(r'\b(href|src)="([^"]*)"', sub, chunk)

def build_ld(S, url, img_abs):
    L = S['L']; base = S['base']
    person = {'@type': 'Person', '@id': PID, 'name': 'Philipp Paulik', 'alternateName': 'philppplik', 'url': PORTFOLIO,
              'jobTitle': L['jobtitle'], 'description': L['bio1'], 'knowsLanguage': ['de', 'en'],
              'knowsAbout': ['AI Strategy', 'Artificial Intelligence', 'AI Agents', 'Model Context Protocol', 'Web Design', 'UI/UX Design', 'Software Engineering', 'TypeScript', 'Rust', 'Authoring'],
              'image': {'@id': url + '#portrait'}, 'mainEntityOfPage': {'@id': url + '#profilepage'},
              'sameAs': [u for _, u in SAMEAS]}
    image = {'@type': 'ImageObject', '@id': url + '#portrait', 'url': img_abs, 'contentUrl': img_abs, 'width': 1024, 'height': 1024,
             'name': 'Philipp Paulik', 'caption': L['alt'], 'description': L['alt'], 'representativeOfPage': True,
             'encodingFormat': 'image/jpeg', 'inLanguage': L['lang']}
    crumbs = {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': S['crumb_root'], 'item': base + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Philipp Paulik', 'item': url}]}
    site = {'@type': 'WebSite', '@id': base + '/#website', 'url': base + '/', 'name': S['name'], 'inLanguage': L['lang']}
    prof = {'@type': 'ProfilePage', '@id': url + '#profilepage', 'url': url, 'name': title_of(S), 'description': S['desc'],
            'inLanguage': L['lang'], 'isPartOf': {'@id': base + '/#website'}, 'about': {'@id': PID}, 'mainEntity': {'@id': PID},
            'primaryImageOfPage': {'@id': url + '#portrait'}, 'breadcrumb': {'@id': url + '#breadcrumb'},
            'dateModified': datetime.date.today().isoformat()}
    return {'@context': 'https://schema.org', '@graph': [prof, person, image, crumbs, site]}

def title_of(S):
    return f"Philipp Paulik, {'Redakteur' if S['L']['lang']=='de' else 'Developer'} · {S['name']}"

def body_html(S, url, img_rel):
    L = S['L']; name = S['name']
    srcset = f"{img_rel}-400.jpg 400w, {img_rel}-800.jpg 800w, {img_rel}.jpg 1024w"
    others = [(n, u) for k, (n, u) in AUTHOR_PAGES.items() if n != name]
    css = ('<style>.ap .ap-grid{display:grid;grid-template-columns:minmax(0,240px) minmax(0,1fr);gap:28px;align-items:start;margin:18px 0 8px}'
           '.ap a{text-decoration:underline;text-underline-offset:3px}.ap figure{margin:0}.ap figure img{width:100%;height:auto;border-radius:16px;display:block}.ap figcaption{font-size:13px;opacity:.7;margin-top:8px}'
           '.ap .ap-kicker{font-size:13px;letter-spacing:.06em;text-transform:uppercase;opacity:.7;margin:0 0 6px}'
           '.ap dl{display:grid;grid-template-columns:max-content 1fr;gap:6px 18px;margin:0}.ap dt{opacity:.7}.ap dd{margin:0}'
           '.ap ul.ap-links{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px 16px}.ap .ap-crumbs{font-size:14px;opacity:.8;margin:20px 0 14px}'
           '@media(max-width:640px){.ap .ap-grid{grid-template-columns:1fr}.ap figure{max-width:260px}}</style>')
    crumbs = f'<nav class="ap-crumbs" aria-label="Breadcrumb"><a href="{S["base"]}/">{E(S["crumb_root"])}</a> / <span aria-current="page">Philipp Paulik</span></nav>'
    img = (f'<figure><img src="{img_rel}.jpg" srcset="{srcset}" sizes="(max-width:640px) 260px, 240px" width="1024" height="1024" '
           f'alt="{E(L["alt"])}" fetchpriority="high" decoding="async"><figcaption>{E(L["cap"])}</figcaption></figure>')
    me = ' '.join(f'<a rel="me noopener" href="{u}">{E(n)}</a>' for n, u in SAMEAS)
    web = '<ul class="ap-links">' + ''.join(f'<li><a rel="me noopener" href="{u}">{E(n)}</a></li>' for n, u in SAMEAS) + '</ul>'
    def fv(k, v):
        if k in ("Persönliche Website", "Personal website"):
            return '<a rel="me" href="%s">%s</a>' % (PORTFOLIO, E(v))
        return E(v)
    facts = ''.join('<dt>%s</dt><dd>%s</dd>' % (E(k), fv(k, v)) for k, v in L['facts'])
    facts += f'<dt>{E(L["role_h"])}</dt><dd>{E(L["role"])}, {E(name)}</dd>'
    proj = '<ul>' + ''.join(f'<li><a href="{u}">{E(n)}</a>: {E(d)}</li>' for n, u, d in L['projects']) + '</ul>'
    also = '<ul class="ap-links">' + ''.join(f'<li><a href="{u}">{E(n)}</a></li>' for n, u in others) + '</ul>'
    return (f'{S["open"]}{css}{crumbs}<p class="ap-kicker">{E(L["kicker"].format(site=name))}</p><h1>Philipp Paulik</h1>'
            f'<div class="ap-grid">{img}<div><p>{E(L["bio1"])}</p><p>{E(S["p2"])}</p>'
            f'<p><a rel="me" href="{PORTFOLIO}">philipp-paulik.de</a></p></div></div>'
            f'<h2>{E(L["h_facts"])}</h2><dl>{facts}</dl><h2>{E(L["h_proj"])}</h2>{proj}'
            f'<h2>{E(L["h_web"])}</h2>{web}<h2>{E(L["h_also"])}</h2>{also}{S["close"]}')

def write_page(S, out, assets_src):
    L = S['L']; base = S['base']
    url = base + '/' + S['page']
    tpl_path = os.path.join(out, S['template'])
    t = open(tpl_path, encoding='utf-8').read()
    target_rel = S['page'] + ('index.html' if S['layout'] == 'dir' and not S['page'].endswith('.html') else '')
    if S['layout'] == 'file': target_rel = S['page'] + '.html'
    elif not target_rel.endswith('index.html'): target_rel += 'index.html'
    tdepth = S['template'].count('/'); gdepth = target_rel.count('/')
    delta = gdepth - tdepth
    i = t.find('</header>')
    m = re.search(S.get('start', r'<(main|article)\b'), t[i:]); start = i + m.start()
    j = t.find('<footer', start)
    head, mid, foot = t[:start], t[start:j], t[j:]
    head = fix_rel(head, delta); foot = fix_rel(foot, delta)
    img_abs = f'{base}/assets/{IMG}.jpg'
    img_rel = '/assets/' + IMG
    # head rewrite
    head = re.sub(r'<title>.*?</title>', '', head, flags=re.S)
    head = re.sub(r'<meta name="description"[^>]*>', '', head)
    head = re.sub(r'<link rel="canonical"[^>]*>', '', head)
    head = re.sub(r'<meta property="og:(title|description|url|type|image[^"]*)"[^>]*>', '', head)
    head = re.sub(r'<meta name="twitter:(title|description|image[^"]*)"[^>]*>', '', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    title = title_of(S)
    ldjson = json.dumps(build_ld(S, url, img_abs), ensure_ascii=False).replace('</', '<\\/')
    # Hob appends " · Daily Hob" via its own wrap; here the title already holds the site name
    new = (f'<title>{E(title)}</title><meta name="description" content="{E(S["desc"])}"><link rel="canonical" href="{url}">'
           f'<meta property="og:type" content="profile"><meta property="profile:first_name" content="Philipp"><meta property="profile:last_name" content="Paulik">'
           f'<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(S["desc"])}"><meta property="og:url" content="{url}">'
           f'<meta property="og:image" content="{img_abs}"><meta property="og:image:width" content="1024"><meta property="og:image:height" content="1024">'
           f'<meta property="og:image:alt" content="{E(L["alt"])}"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(S["desc"])}">'
           f'<meta name="twitter:image" content="{img_abs}"><meta name="twitter:image:alt" content="{E(L["alt"])}">'
           f'<script type="application/ld+json">{ldjson}</script>')
    head = head.replace('</head>', new + '</head>', 1)
    head = re.sub(r'<meta name="twitter:card"[^>]*>', '<meta name="twitter:card" content="summary">', head)
    if 'twitter:card' not in head: head = head.replace('</head>', '<meta name="twitter:card" content="summary"></head>', 1)
    page = head + body_html(S, url, img_rel) + foot
    dest = os.path.join(out, target_rel); os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(page)
    # assets
    ad = os.path.join(out, 'assets'); os.makedirs(ad, exist_ok=True)
    for f in glob.glob(os.path.join(assets_src, IMG + '*.jpg')): shutil.copy(f, ad)
    return url, img_abs, title, target_rel

def patch_ld(node, author):
    n = 0
    if isinstance(node, list):
        for x in node: n += patch_ld(x, author)
    elif isinstance(node, dict):
        if '@graph' in node: n += patch_ld(node['@graph'], author)
        t = node.get('@type'); ts = t if isinstance(t, list) else [t]
        if any(x in ('Article', 'NewsArticle', 'BlogPosting', 'TechArticle') for x in ts):
            a = node.get('author')
            al = a if isinstance(a, list) else ([a] if a else [])
            keep = [x for x in al if isinstance(x, dict) and x.get('@type') == 'Person' and x.get('name') != 'Philipp Paulik']
            node['author'] = author if not keep else keep + [author]
            n += 1
    return n

def patch_articles(S, out, author_url, target_rel):
    L = S['L']; seen = set(); linked = 0
    author = {'@type': 'Person', '@id': PID, 'name': 'Philipp Paulik', 'url': author_url, 'sameAs': [PORTFOLIO]}
    for g in S['articles']:
        for f in sorted(glob.glob(os.path.join(out, g))):
            if f in seen or f.endswith(target_rel) or '/redakteur/' in f: continue
            seen.add(f)
            h = open(f, encoding='utf-8').read(); orig = h
            ok = False
            def sub(m):
                nonlocal ok
                try: data = json.loads(m.group(1))
                except Exception: return m.group(0)
                if patch_ld(data, author): ok = True
                return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'
            h = re.sub(r'<script type="application/ld\+json">(.*?)</script>', sub, h, flags=re.S)
            if not ok: continue
            if 'rel="author"' not in h:
                h = h.replace('</head>', f'<link rel="author" href="{author_url}"></head>', 1)
                link = f'<a rel="author" href="{author_url}">Philipp Paulik</a>'
                if 'class="byline"' in h and ('Redaktion ' + S['name']) in h:
                    h = h.replace('Redaktion ' + S['name'], link + ', Redaktion ' + S['name'], 1)
                elif 'class="byline"' not in h:
                    h = re.sub(r'(</h1>)', r'\1<p class="byline">' + L['byline'] + ' ' + link + '</p>', h, count=1)
            if h != orig:
                open(f, 'w', encoding='utf-8').write(h); linked += 1
    return linked

def patch_sitemaps(S, out, url, img_abs, title):
    today = datetime.date.today().isoformat()
    for sm in S['sitemaps']:
        p = os.path.join(out, sm)
        if not os.path.exists(p): print('no sitemap', p); continue
        x = open(p, encoding='utf-8').read()
        if f'<loc>{url}</loc>' in x: continue
        if 'xmlns:image=' not in x:
            x = x.replace('<urlset ', '<urlset xmlns:image="http://www.google.com/schemas/image/1.1" ', 1)
        entry = (f'<url><loc>{url}</loc><lastmod>{today}</lastmod><image:image><image:loc>{img_abs}</image:loc>'
                 f'<image:title>{E(title)}</image:title><image:caption>{E(S["L"]["alt"])}</image:caption></image:image></url>')
        x = x.replace('</urlset>', entry + '</urlset>')
        open(p, 'w', encoding='utf-8').write(x)

def main():
    key, out = sys.argv[1], sys.argv[2]
    assets = sys.argv[sys.argv.index('--assets') + 1] if '--assets' in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authorpage-assets')
    S = SITES[key]
    url, img_abs, title, target_rel = write_page(S, out, assets)
    n = patch_articles(S, out, url, target_rel)
    patch_sitemaps(S, out, url, img_abs, title)
    lt = os.path.join(out, 'llms.txt')
    if os.path.exists(lt):
        x = open(lt, encoding='utf-8').read()
        if url not in x:
            open(lt, 'a', encoding='utf-8').write(f'\n- Autor / author: Philipp Paulik, {url}\n')
    print('author page:', os.path.join(out, target_rel), '| articles linked:', n)

if __name__ == '__main__': main()
