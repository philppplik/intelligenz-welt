#!/usr/bin/env python3
"""Final, idempotent static postprocessor. Does not load any remote resource."""
import sys, json, pathlib, html, re, shutil
from urllib.parse import quote, urlparse
ROOT = pathlib.Path(__file__).resolve().parent.parent
E = lambda text: html.escape(str(text), quote=True)

def validate(cfg):
    if cfg['advertising']['enabled']:
        raise ValueError('AdSense is locked: integrate and test a Google-certified TCF CMP first')
    if cfg['analytics']['enabled']:
        if cfg['analytics']['provider'] != 'ga4' or not re.fullmatch(r'G-[A-Z0-9]+', cfg['analytics']['measurementId']):
            raise ValueError('An approved GA4 property ID is required')
        if not cfg['analytics'].get('privacyReviewed'):
            raise ValueError('Update privacy/cookies, processor agreement, retention and settings before activation')
    if cfg['metrics']['enabled'] and not cfg['analytics']['enabled']:
        raise ValueError('No collector selected: local events alone are not an aggregate metrics system')
    if len(cfg['spots']) > 1:
        raise ValueError('Unobtrusive v1: at most one direct campaign')
    for s in cfg['spots']:
        if not re.fullmatch(r'[a-z0-9-]{1,80}', s['id']): raise ValueError('Invalid spot ID')
        if s['kind'] not in ('sponsored', 'affiliate'): raise ValueError('Unknown campaign type')
        if not all(s.get(x) for x in ('sponsor','title','description','url')): raise ValueError('Missing campaign disclosure')
        u = urlparse(s['url'])
        if not (u.scheme == 'https' and u.netloc and not u.username) and not (s['url'].startswith('/artikel/') and not u.netloc): raise ValueError('Use verified HTTPS or local article destination')
        if s['url'].startswith('/artikel/'): raise ValueError('Paid article promotion needs article/list label integration and individual review before activation')
        if not s.get('approved'): raise ValueError('Campaign recipient, wording and destination must be approved')
    return cfg

PANEL = '''<section id="iw-consent" class="iw-consent" role="region" aria-labelledby="iw-consent-title" hidden>
<button type="button" class="iw-consent-close" data-consent="close" aria-label="Einstellungen schließen, ohne Auswahl zu ändern">Schließen</button>
<h2 id="iw-consent-title">Deine Privatsphäre.</h2>
<p>Du entscheidest über Statistik und Werbung. Ohne Zustimmung bleibt beides aus.</p>
<p><strong>Aktueller Stand:</strong> Statistik und Werbung sind noch nicht aktiviert.</p>
<fieldset><legend>Wofür dürfen Daten genutzt werden?</legend>
<label><input type="checkbox" checked disabled><span><strong>Notwendig</strong><small>Seite und Datenschutzauswahl. Kein Tracking.</small></span></label>
<label><input type="checkbox" id="iw-statistics"><span><strong>Statistik</strong><small>Seitenaufrufe und Interaktionen. Derzeit aus.</small></span></label>
<label><input type="checkbox" id="iw-advertising"><span><strong>Werbung</strong><small>AdSense und Werbedienste. Derzeit aus.</small></span></label>
</fieldset><div class="iw-consent-actions"><button type="button" data-consent="reject">Alle ablehnen</button><button type="button" data-consent="all">Alle verfügbaren erlauben</button><button type="button" data-consent="save">Auswahl speichern</button></div>
<p><a href="/datenschutz/">Datenschutz</a> · <a href="/cookies/">Cookies &amp; Einstellungen</a> · <a href="/impressum/">Impressum</a></p><p class="iw-muted">Jederzeit im Footer ändern. Schließen erteilt keine Einwilligung.</p></section>'''

def mailto(kind):
    body = 'Hallo Philipp,\n\nich interessiere mich für: '+kind+'\n\nUnternehmen / Website:\nBeworbener Artikel oder Ziel-URL:\nThema und Zielgruppe:\nGewünschter Zeitraum:\nOptionaler Budgetrahmen:\nHinweise / Kontakt:\n\nMir ist klar: Die Anfrage ist keine Buchung.\n'
    return 'mailto:philipp.l.paulik@gmail.com?subject=' + quote('Werbeanfrage Intelligenz Welt: '+kind) + '&body=' + quote(body)

def advertiser_page():
    cards = ''
    for label, title, desc in [
        ('Anzeige · Gesponsert','Artikel bewerben','Ein klar abgegrenzter Hinweis auf einen passenden Artikel oder ein Angebot. Bezahlte Platzierung, kein Einfluss auf redaktionelle Bewertungen.'),
        ('Anzeige · Affiliate','Affiliate-Kooperation','Passende Angebote mit transparentem Provisionshinweis direkt am Link. Keine versteckten Empfehlungen oder automatische Teilnahme an einem Netzwerk.'),
        ('Anzeige','Dezente Display-Anzeige','Eine ruhige Platzierung außerhalb des Lesetexts. Google AdSense ist erst nach gesonderter Einrichtung, Prüfung und passender Einwilligung vorgesehen.')]:
        cards += '<section class="iw-ad-card"><span class="iw-label">%s</span><h2>%s</h2><p>%s</p><a class="iw-button" href="%s">Format anfragen</a></section>' % (E(label),E(title),E(desc),E(mailto(title)))
    return '''<main class="iw-ad-page"><span class="tag">Kooperationen</span><h1>Gute Inhalte.<br>Dezent sichtbar.</h1><p class="iw-lead">Werbung auf Intelligenz Welt soll zum Thema passen, klar erkennbar sein und beim Lesen nicht stören.</p><a class="iw-button primary" href="%s">Kooperation per E-Mail anfragen</a><p class="meta">Unverbindlich an philipp.l.paulik@gmail.com. Kein Formular, keine automatische Buchung.</p>
<div class="iw-ad-grid">%s</div>
<section class="iw-commercial"><span class="iw-label">Platzierungskonzept, keine aktive Anzeige</span><h2>Raum für einen passenden Hinweis.</h2><p>Geplant: ein abgetrennter Spot nach dem redaktionellen Inhalt, höchstens eine direkte Kampagne pro Seite. Keine Pop-ups, keine Video-Autostarts, kein Sticky-Werbebanner über dem Text.</p><p>Solange kein geprüftes Angebot vorliegt, bleibt dieser Platz in Artikeln und auf der Startseite unsichtbar.</p></section>
<h2>Redaktion bleibt Redaktion.</h2><p>Eine bezahlte Platzierung kauft Sichtbarkeit, keine positive Bewertung. Werbung wird vor dem Inhalt mit „Anzeige“ gekennzeichnet. „Gesponsert“ oder „Affiliate“ ergänzt die Einordnung. Bei Affiliate-Links steht der Provisionshinweis direkt am Link.</p>
<h2>So läuft eine Anfrage ab</h2><ol><li>Schick Unternehmen, Ziel-URL, Thema und gewünschten Zeitraum per Mail. Ein Budgetrahmen ist optional.</li><li>Wir prüfen, ob das Angebot zum Magazin passt, und besprechen Format, Kennzeichnung und Konditionen.</li><li>Erst eine gesonderte Vereinbarung macht daraus eine Buchung. Es gibt keine garantierte Veröffentlichung oder positive redaktionelle Bewertung.</li></ol>
<h2>Reichweite &amp; Messung</h2><p>Wir versprechen keine erfundenen Reichweiten, Klickzahlen oder CPMs. Eine spätere Auswertung kann nur tatsächlich gemessene, freigegebene Daten abdecken. AdSense-Abrechnung und unsere eigenen Kampagnen sind getrennte Auswertungen.</p>
<p>Aktuell sind keine Werbe- oder Statistikdienste aktiviert. <a href="/werbung/">Wie wir Werbung kennzeichnen</a> · <a href="/cookies/">Datenschutzeinstellungen</a></p><p>E-Mail: <a href="mailto:philipp.l.paulik@gmail.com">philipp.l.paulik@gmail.com</a></p></main>''' % (E(mailto('Kooperation')),cards)

def main(out):
    out = pathlib.Path(out); cfg = validate(json.loads((ROOT/'content/monetization.json').read_text()))
    asset = out/'assets/monetization'; asset.mkdir(parents=True,exist_ok=True)
    for name in ('consent.css','consent.js'): shutil.copy(ROOT/'tools/monetization'/name,asset/name)
    base = (out/'impressum/index.html').read_text()
    head = base[:base.index('</header>')+len('</header>')]
    # Preserve existing menu/search script, not the imprint body.
    tail = base[base.index('</header>')+len('</header>'):]
    if tail.startswith('<script>'): head += tail[:tail.index('</script>')+len('</script>')]
    foot = base[base.index('<footer'):]
    h = re.sub(r'<title>.*?</title>','<title>Werben &amp; Kooperationen | Intelligenz Welt</title>',head,flags=re.S)
    h = re.sub(r'<meta (?:property="og:(?:title|description|url|type)"|name="description")[^>]*>', '', h)
    h = re.sub(r'<link rel="canonical"[^>]*>','<link rel="canonical" href="https://intelligenz-welt.de/werben/">',h)
    h = h.replace('</head>','<meta name="description" content="Dezente Werbung und Kooperationen auf Intelligenz Welt. Formate, Kennzeichnung und unverbindliche Anfrage per E-Mail."><meta property="og:title" content="Werben &amp; Kooperationen | Intelligenz Welt"><meta property="og:url" content="https://intelligenz-welt.de/werben/"></head>')
    (out/'werben').mkdir(exist_ok=True); (out/'werben/index.html').write_text(h+advertiser_page()+foot)
    # Dynamic provider wording must be reviewed with the actual provider; preparation stays literal/off.
    panel = PANEL
    if cfg['analytics']['enabled'] or cfg['metrics']['enabled']:
        raise ValueError('Activation is a separate reviewed release: replace off-state privacy text and banner provider disclosure first')
    config = '<script type="application/json" id="iw-monetization-config">'+json.dumps(cfg,ensure_ascii=True).replace('<','\\u003c')+'</script>'
    extra = panel+config+'<script src="/assets/monetization/consent.js" defer></script>'
    spot = ''
    for s in cfg['spots']:
        label = 'Anzeige · '+('Affiliate' if s['kind']=='affiliate' else 'Gesponsert')
        notice = '<p>Affiliate-Link: Bei einem Kauf über diesen Link können wir eine Provision erhalten.</p>' if s['kind']=='affiliate' else ''
        spot += '<aside class="iw-commercial" aria-label="Anzeige" data-iw-spot="%s"><span class="iw-label">%s · Auftraggeber: %s</span><h2>%s</h2><p>%s</p>%s<a class="iw-button" data-iw-promotion href="%s" rel="sponsored nofollow noopener">Angebot ansehen</a></aside>' % (E(s['id']),E(label),E(s['sponsor']),E(s['title']),E(s['description']),notice,E(s['url']))
    for f in out.rglob('*.html'):
        t = f.read_text()
        if 'id="iw-monetization-config"' in t or '</body>' not in t: continue
        # Printable reports deliberately do not acquire a consent UI or commercial content.
        if f.parent.name=='berichte' and f.name!='index.html': continue
        t = t.replace('</head>','<link rel="stylesheet" href="/assets/monetization/consent.css"></head>',1)
        if '<a href="/kontakt/">Kontakt</a>' in t:
            t = t.replace('<a href="/kontakt/">Kontakt</a>','<a href="/kontakt/">Kontakt</a><a href="/werben/">Werben &amp; Kooperationen</a><a href="/werbung/">Werbung &amp; Affiliate</a><a href="/cookies/">Cookies &amp; Einstellungen</a><button type="button" class="iw-consent-open" data-iw-consent-open>Datenschutzeinstellungen</button><span id="iw-consent-status" class="sr" role="status"></span>',1)
        if spot and (f==out/'index.html' or f.parent.parent.name=='artikel'):
            at = t.find('<footer')
            t = t[:at]+'<div class="w">'+spot+'</div>'+t[at:]
        t = t.replace('</body>',extra+'</body>',1); f.write_text(t)
    p = out/'sitemap.xml'; xml=p.read_text()
    if 'https://intelligenz-welt.de/werben/' not in xml: p.write_text(xml.replace('</urlset>','<url><loc>https://intelligenz-welt.de/werben/</loc></url></urlset>'))
    print('Monetization: inert configuration, consent UI and advertiser page generated')

if __name__=='__main__': main(sys.argv[1])
