#!/usr/bin/env python3
"""Final pass: replace the site footer by the brand-block + link-column footer.

Runs after monetization (the consent button hook must stay in the footer) and keeps
every footer link. Usage: footer.py OUT
"""
import pathlib, sys

CSS = """/* IW footer: brand block + link columns */
footer.iwf{background:var(--dark);color:#94a3b8;margin-top:80px;padding:52px 0 28px;font-size:14px}
footer.iwf a{display:block;margin:0;color:#cbd5e1}footer.iwf a:hover{color:#fff}
footer.iwf .iwf-top{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,2.75fr);gap:56px}
footer.iwf .iwf-brand a.iwf-logo{display:inline-flex;align-items:center;gap:10px;color:#fff;font-weight:700;font-size:18px;letter-spacing:-.01em}
footer.iwf .iwf-brand a.iwf-logo b{color:var(--ac);font-weight:700}
footer.iwf .iwf-brand p{margin:14px 0 0;max-width:320px;line-height:1.6}
footer.iwf .iwf-cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px}
footer.iwf h4{color:#fff;margin:0 0 14px;font-size:12px;text-transform:uppercase;letter-spacing:.08em}
footer.iwf .iwf-cols a,footer.iwf .iwf-cols .iw-consent-open{padding:5px 0;line-height:1.4}
footer.iwf .iw-consent-open{color:#cbd5e1;text-decoration:none;text-align:left;min-height:0;padding:5px 0;display:block}
footer.iwf .iw-consent-open:hover{color:#fff;text-decoration:none}
footer.iwf .iwf-rule{border-top:1px solid rgba(148,163,184,.25);margin:36px 0 18px}
footer.iwf .iwf-bottom{display:flex;justify-content:space-between;gap:12px 28px;flex-wrap:wrap;font-size:13px}
footer.iwf .iwf-bottom p{margin:0}footer.iwf .iwf-bottom a{display:inline;color:#cbd5e1;text-decoration:underline}
footer.iwf .iwf-port{margin:0 0 6px}footer.iwf .iwf-port a{display:inline}
@media(max-width:900px){footer.iwf .iwf-top{grid-template-columns:1fr;gap:36px}}
@media(max-width:560px){footer.iwf{padding:40px 0 24px}footer.iwf .iwf-cols{grid-template-columns:1fr 1fr;gap:28px 20px}footer.iwf .iwf-cols>div:last-child{grid-column:1/-1}}
"""

def main(out):
    out = pathlib.Path(out)
    (out / 'assets').mkdir(exist_ok=True)
    (out / 'assets' / 'footer.css').write_text(CSS)
    about = '<a href="/ueber-uns/">Über uns</a>' if (out / 'ueber-uns' / 'index.html').exists() else ''
    footer = ('<footer class="iwf"><div class="w"><div class="iwf-top"><div class="iwf-brand">'
        '<a class="iwf-logo" href="/"><img src="/assets/branding/logo.svg" alt="" width="28" height="28"><span>Intelligenz<b>Welt</b></span></a>'
        '<p>KI-News, Modell-Radar und Artikel auf Deutsch. News werden automatisch aus öffentlichen RSS-Feeds und APIs aggregiert.</p></div>'
        '<div class="iwf-cols">'
        '<div><h4>Magazin</h4><a href="/news/">KI-News</a><a href="/modelle/">Modell-Radar</a>%s%s<a href="/berichte/">Tagesausgabe (PDF)</a><a href="/feed.xml">RSS-Feed</a></div>'
        '<div><h4>Redaktion</h4>%s<a href="/redaktion/">Redaktion</a><a href="/transparenz/">KI-Transparenz</a><a href="/korrekturen/">Korrekturen</a><a href="/quellen/">Quellen</a></div>'
        '<div><h4>Rechtliches</h4><a href="/impressum/">Impressum</a><a href="/datenschutz/">Datenschutz</a><a href="/cookies/">Cookies &amp; Einstellungen</a>'
        '<button type="button" class="iw-consent-open" data-iw-consent-open>Datenschutzeinstellungen</button><span id="iw-consent-status" class="sr" role="status"></span>'
        '<a href="/werben/">Werben &amp; Kooperationen</a><a href="/werbung/">Werbung &amp; Affiliate</a><a href="/kontakt/">Kontakt</a></div>'
        '</div></div><div class="iwf-rule"></div><div class="iwf-bottom"><div>'
        '<p class="iwf-port"><a href="/unternehmen/">Unternehmens-Portraits</a> · <a href="/ki-modelle/">KI-Modell-Portraits</a></p>'
        '<p>© %d Intelligenz Welt</p></div></div></div></footer>')
    import datetime
    year = datetime.datetime.now().year
    n = 0
    for f in out.rglob('*.html'):
        t = f.read_text(encoding='utf-8')
        i = t.find('<footer><div class="w c">')
        if i < 0: continue
        j = t.find('</footer>', i) + 9
        old = t[i:j]
        port = '' if 'data-portrait-footer' in old else None
        has_port = 'data-portrait-footer' in old
        ft = footer % ('', '', about, year)
        if not has_port:
            ft = ft.replace('<p class="iwf-port"><a href="/unternehmen/">Unternehmens-Portraits</a> · <a href="/ki-modelle/">KI-Modell-Portraits</a></p>', '')
        t = t[:i] + ft + t[j:]
        t = t.replace('</head>', '<link rel="stylesheet" href="/assets/footer.css"></head>', 1)
        f.write_text(t, encoding='utf-8'); n += 1
    print('IW footer: %d pages' % n)

if __name__ == '__main__': main(sys.argv[1])
