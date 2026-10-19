"""Intelligenz Welt Tagesausgabe (A4 PDF + print page). Called from articles.py after the build. Data: own articles, aggregated headlines (news.json)."""
import json, os, re, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report_core import esc, DAYS, render, to_pdf, logo_inline, lnk, dom, srclist
import report_visuals as V

def domain(u):
    m = re.match(r'https?://(?:www\.)?([^/]+)', u or ''); return m.group(1) if m else ''

def build(arts, now, out, root, base):
    day = DAYS[now.weekday()] + ', ' + now.strftime('%d.%m.%Y'); stamp = now.strftime('%d.%m.%Y, %H:%M') + ' Uhr'
    top = sorted(arts, key=lambda a: a['_pub'], reverse=True)
    lead, rest = (top[0] if top else None), top[1:10]
    p1 = ''
    if lead:
        img = os.path.join(out, 'assets', 'editorial', lead['slug'] + '-800.jpg')
        im = '<img src="../assets/editorial/%s-800.jpg" alt="" style="width:100%%;height:62mm;object-fit:cover;border-radius:6px;margin:0 0 3mm">' % esc(lead['slug']) if os.path.exists(img) else ''
        facts = ''.join('<li>%s</li>' % esc(re.sub(r'\s*\[\d+(?:[,–-]\s*\d+)*\]', '', t)) for t in lead.get('key_takeaways', [])[:4])
        p1 += '<h2>Die Meldung des Tages</h2><div class="art lead">%s<div class="m">%s · %s · %d Quellen</div><div class="t">%s</div><div class="d">%s</div>%s<div class="u">%s</div>%s</div>' % (
            im, esc(lead['section'].capitalize()), lead['_pub'].strftime('%d.%m.%Y, %H:%M'), len(lead['sources']), lnk(base + '/artikel/' + lead['slug'] + '/', lead['title']), esc(lead['dek']), ('<ul>%s</ul>' % facts) if facts else '', lnk(base + '/artikel/' + lead['slug'] + '/'), srclist(lead['sources']))
    p2 = '<h2>Weitere Artikel <small>neueste zuerst</small></h2>'
    for a in rest:
        p2 += '<div class="art"><div class="m">%s · %s</div><div class="t">%s</div><div class="d">%s</div><div class="u">%s</div>%s</div>' % (
            esc(a['section'].capitalize()), a['_pub'].strftime('%d.%m.%Y, %H:%M'), lnk(base + '/artikel/' + a['slug'] + '/', a['title']), esc(a['dek']), lnk(base + '/artikel/' + a['slug'] + '/'), srclist(a['sources'], 3))
    p2 = p2 if rest else '<h2>Weitere Artikel</h2><p class="mut">Keine weiteren Artikel.</p>'
    try: news = json.load(open(os.path.join(out, 'news.json'), encoding='utf-8'))[:12]
    except Exception: news = []
    nl = ''.join('<li style="padding:4px 0;border-bottom:1px solid #eceef4;break-inside:avoid">%s<br><span class="mut" style="font-size:8pt">%s · %s</span></li>' % (lnk(n['url'], n['title']) if n.get('url') else esc(n['title']), esc(n.get('src', '')), lnk(n['url'], dom(n['url'])) if n.get('url') else '') for n in news)
    p3 = '<h2>KI-Pulse <small>aktuelle Schlagzeilen aus öffentlichen Feeds · nur Überschriften, Rechte bei den Quellen</small></h2><ul style="list-style:none;margin:0;padding:0">%s</ul>' % (nl or '<li class="mut">Aktuell keine Schlagzeilen.</li>')
    def _load(rel):
        try: return json.load(open(os.path.join(root, 'data', rel), encoding='utf-8'))
        except (OSError, ValueError): return []
    ai = _load('ai_archive.json'); models = [m for m in _load('models.json') if not re.search('uncensored|nsfw|abliterat', m['id'], re.I)]
    V.load_logos(root)
    pv = '<style>%s.h3{font-size:9.5pt;margin:3mm 0 1.5mm;color:#093A6A}</style>' % V.CSS
    pv += (V.pdf_overview(ai, models, now) if ai else '') + V.pdf_radar(models)
    last = '''<h2>Impressum &amp; Redaktionsschluss</h2>
<div class="imp"><div><h3>Anbieter nach § 5 DDG</h3><p>Philipp Paulik<br>Mozartstraße 1<br>53819 Neunkirchen-Seelscheid<br>Nordrhein-Westfalen</p><h3>Kontakt</h3><p>E-Mail: philipp.l.paulik@gmail.com<br>Web: intelligenz-welt.de</p></div>
<div><h3>Verantwortlich nach § 18 Abs. 2 MStV</h3><p>Philipp Paulik, Anschrift wie links</p><h3>Redaktion</h3><p>Intelligenz Welt, Redaktion Philipp Paulik</p></div></div>
<h3>Redaktionsschluss</h3><p>Diese Ausgabe wurde am %s automatisch erstellt. Später veröffentlichte Beiträge und Meldungen sind nicht berücksichtigt.</p>
<h3>Hinweis zu KI</h3><p>Redaktionelle Beiträge von Intelligenz Welt werden mit Unterstützung von KI erstellt und vor Veröffentlichung redaktionell geprüft (siehe intelligenz-welt.de/transparenz/). Titelbilder sind KI-generiert und gekennzeichnet. Die Schlagzeilen im KI-Pulse werden automatisch aus öffentlichen Feeds aggregiert. Trotz Prüfung können Fehler nicht ausgeschlossen werden.</p>
<h3>Datenquellen</h3><p>Eigene Artikel von Intelligenz Welt mit Quellenangaben im jeweiligen Beitrag. Schlagzeilen: öffentliche RSS-Feeds und APIs der genannten Medien (nur Überschriften mit Quellenangabe).</p>
<p class="foot">© %d Intelligenz Welt · Philipp Paulik · Stand %s</p>''' % (esc(stamp), now.year, esc(stamp))
    logo = logo_inline(os.path.join(root, 'content', 'branding', 'logo.svg'), '0 0 637 641')
    htm = render('Intelligenz Welt', 'Tagesausgabe', now.strftime('%d.%m.%Y'), '#1d6bc0', '#093A6A', '#eef5fc', '#cfe0f3', logo,
                 'Tagesausgabe', day + ' · Meldung des Tages, neueste Artikel und KI-Pulse', ([p1 + p2, pv, p3] if (ai or models) else [p1 + p2, p3]), last.replace('<h3>Datenquellen</h3>', V.logo_credits() + '<h3>Datenquellen</h3>', 1))
    d = os.path.join(out, 'berichte'); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'tagesausgabe.html'), 'w', encoding='utf-8').write(htm)
    dated = os.path.join(d, 'intelligenz-welt-tagesausgabe-%s.pdf' % now.strftime('%Y-%m-%d'))
    ok = to_pdf(os.path.join(d, 'tagesausgabe.html'), dated)
    if ok: shutil.copy(dated, os.path.join(d, 'intelligenz-welt-tagesausgabe.pdf'))
    return ok
