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
        if not cfg['analytics'].get('activationApproved'):
            raise ValueError('Owner activation approval required')
        if cfg['analytics'].get('eventRetentionMonths') != 2 or cfg['analytics'].get('cookieLifetimeDays') != 180 or cfg['analytics'].get('resetRetentionOnActivity') is not False:
            raise ValueError('Reviewed minimal profile: 2-month event retention, 180-day fixed cookies, no activity reset')
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
<h2 id="iw-consent-title">Deine Privatsphäre.</h2>
<p>Du entscheidest über Statistik und Werbung. Ohne Zustimmung bleibt beides aus.</p>
<fieldset><legend>Wofür dürfen Daten genutzt werden?</legend>
<label><input type="checkbox" checked disabled><span><strong>Notwendig</strong><small>Seite und Datenschutzauswahl. Kein Tracking.</small></span></label>
<label><input type="checkbox" id="iw-statistics"><span><strong>Statistik</strong><small>Seitenaufrufe und Interaktionen. Derzeit aus.</small></span></label>
<label><input type="checkbox" id="iw-advertising"><span><strong>Werbung</strong><small>AdSense und Werbedienste. Derzeit aus.</small></span></label>
</fieldset><div class="iw-consent-actions"><button type="button" data-consent="reject">Alle ablehnen</button><button type="button" data-consent="all">Alle verfügbaren akzeptieren</button><button type="button" data-consent="save">Auswahl speichern</button></div>
<p><a href="/datenschutz/">Datenschutz</a> · <a href="/cookies/">Cookies &amp; Einstellungen</a> · <a href="/impressum/">Impressum</a></p><p class="iw-muted">Ohne Auswahl bleiben Statistik und Werbung aus. Jederzeit im Footer änderbar.</p></section>'''

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


def ga4_disclosure(active):
    status = 'Google Analytics 4: Statistik mit Einwilligung' if active else 'Google Analytics 4: vorbereitet, noch nicht aktiv'
    intro = 'Die folgende Konfiguration wird nur nach Ihrer Statistik-Einwilligung eingesetzt.' if active else 'Google Analytics 4 ist ausgewählt, aber noch nicht aktiviert. Die folgenden Angaben beschreiben die vorbereitete Konfiguration, nicht eine bereits laufende Verarbeitung. Vor Aktivierung werden die tatsächlichen Kontoeinstellungen und Vertragsgrundlagen geprüft.'
    return '<section aria-labelledby="iw-ga4-heading"><h2 id="iw-ga4-heading">'+status+'</h2><p>'+intro+'</p>'+GA4_DETAILS+'</section>'

GA4_DETAILS = '''<h3>Anbieter und Zweck</h3><p>Google Analytics 4 ist ein Dienst von Google. Vertragspartner nach den deutschen Google-Analytics-Nutzungsbedingungen ist Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland; Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA, und weitere Auftragsverarbeiter können an der Verarbeitung beteiligt sein. Zweck ist die statistische Auswertung von Seitenaufrufen, Nutzung und gekennzeichneten Werbeplatzierungen. Werbung, Google Signals, User-ID, personalisierte Anzeigen und Verknüpfungen mit Google Ads sind nicht Teil dieser Konfiguration.</p>
<h3>Einwilligung und Daten</h3><p>Rechtsgrundlagen sind Ihre freiwillige Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO und für das Speichern beziehungsweise Auslesen auf Ihrem Gerät § 25 Abs. 1 TDDDG. Ohne Statistik-Einwilligung laden wir den Google-Tag nicht und senden auch keine cookielosen Ablehnungs-Pings (Basic Consent Mode). Lesen und Suche bleiben möglich. Bei Einwilligung können Seitenpfad, Seitentitel, Zeitpunkte, technische Browser-/Geräteinformationen, grobe Standortinformationen und eine pseudonyme Cookie-Kennung verarbeitet werden. Beim Verbindungsaufbau wird Ihre IP-Adresse an Google übermittelt; Google beschreibt für GA4, dass einzelne IP-Adressen nicht protokolliert oder gespeichert werden. Das ist keine Zusage vollständiger Anonymität.</p>
<p>Die ausdrücklich gesendeten Seitenereignisse enthalten keine URL-Suchparameter oder Referrer. Es werden keine Namen oder E-Mail-Adressen als Ereignisparameter gesendet. Enhanced Measurement ist in der Property ausgeschaltet, damit keine zusätzlichen Formular-, Such- oder Outbound-Link-Daten automatisch erfasst werden. Platzierungsereignisse enthalten nur Ereignisart, Spot-ID und Seitenpfad; keine vollständige Ziel-URL.</p>
<h3>Cookies und Speicherdauer</h3><p>GA4 kann die First-Party-Cookies _ga und _ga_&lt;Kennung&gt; verwenden. Wir begrenzen ihre Laufzeit auf 180 Tage und verlängern sie nicht mit jedem Besuch; Browser können sie früher löschen. Die eingestellte Property-Aufbewahrung für nutzer- und ereignisbezogene Daten beträgt zwei Monate, ohne Zurücksetzen bei neuer Aktivität. Diese Einstellung betrifft nicht automatisch alle bereits aggregierten Standardberichte. Google weist darauf hin, dass Änderungen der Aufbewahrung bis zu 24 Stunden brauchen können.</p>
<h3>Drittlandübermittlung und Auftragsverarbeitung</h3><p>Eine Verarbeitung in den USA und anderen Ländern außerhalb des EWR ist möglich. Für dieses Analytics-Konto wurden am 19. Oktober 2026 die Google Ads Data Processing Terms als Vereinbarung zur Auftragsverarbeitung nach Art. 28 DSGVO akzeptiert. Google LLC ist im offiziellen Register als aktiver Teilnehmer des EU-US Data Privacy Framework aufgeführt (geprüft am 19. Oktober 2026). Für davon erfasste Übermittlungen in die USA dient der entsprechende Angemessenheitsbeschluss als Grundlage. Soweit erforderlich, sehen Googles Datenverarbeitungsbedingungen ergänzend Standardvertragsklauseln vor. Andere Drittländer können ein anderes Datenschutzniveau haben; Statistik-Einwilligung beseitigt dieses Risiko nicht.</p>
<h3>Widerruf</h3><p>Öffnen Sie jederzeit „Datenschutzeinstellungen“ im Footer und wählen Sie „Alle ablehnen“ oder deaktivieren Sie Statistik. Der Widerruf gilt für die Zukunft. Weitere Statistik-Ereignisse werden gestoppt, bekannte GA-Cookies auf dieser Domain soweit technisch zugänglich entfernt und die Seite ohne Tag neu geladen. Bereits rechtmäßig verarbeitete Daten werden dadurch nicht automatisch rückwirkend gelöscht. Für Auskunft oder Löschung kontaktieren Sie philipp.l.paulik@gmail.com.</p>
<p>Weitere Informationen: <a href="https://policies.google.com/privacy?hl=de" rel="noopener">Google-Datenschutzerklärung</a>, <a href="https://support.google.com/analytics/answer/11397207" rel="noopener">GA4-Cookies</a>, <a href="https://support.google.com/analytics/answer/7667196" rel="noopener">Datenaufbewahrung</a>, <a href="https://privacy.google.com/businesses/processorterms/" rel="noopener">Google-Datenverarbeitungsbedingungen</a>, <a href="https://www.dataprivacyframework.gov/participant/5780" rel="noopener">DPF-Registereintrag Google LLC</a>, <a href="https://www.google.com/analytics/terms/de.html" rel="noopener">Analytics-Nutzungsbedingungen</a>.</p>'''

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
    active = cfg['analytics']['enabled']
    if active:
        panel = panel.replace('Statistik und Werbung sind noch nicht aktiviert.', 'Google Analytics 4 ist für freiwillige Statistik verfügbar. Werbung bleibt aus.').replace('Seitenaufrufe und Interaktionen. Derzeit aus.', 'Google Analytics 4 (Google Ireland / Google LLC): Seitenaufrufe und Interaktionen, Cookies bis 180 Tage; Datenübermittlung in die USA möglich. Nur nach Zustimmung.')

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
        if f.parent.name in ('datenschutz','cookies') and f.name=='index.html':
            t = t.replace('</article>', ga4_disclosure(active)+'</article>',1)
        if active:
            t = t.replace('Derzeit ist keiner dieser Dienste aktiviert.', 'Google Analytics 4 ist nur mit Statistik-Einwilligung verfügbar; externe Werbedienste bleiben aus.')
            t = t.replace('Eine spätere Auswertung kann nur tatsächlich gemessene, freigegebene Daten abdecken.', 'Die Statistik erfasst nur tatsächlich gemessene Daten nach Einwilligung und ist keine vollständige Reichweitenmessung.')
            t = t.replace('Aktuell sind keine Werbe- oder Statistikdienste aktiviert.', 'Google Analytics 4 wird nur nach Statistik-Einwilligung geladen. Externe Werbung bleibt aus.')
            t = t.replace('Aktuell sind Google AdSense, Affiliate-Netzwerke und Statistikdienste nicht aktiviert.', 'Google AdSense und Affiliate-Netzwerke sind nicht aktiviert. Google Analytics 4 wird nur mit Statistik-Einwilligung eingesetzt.')
            t = t.replace('Statistik- und Werbedienste sind derzeit ausgeschaltet.', 'Externe Werbedienste bleiben ausgeschaltet. Google Analytics 4 ist ausschließlich mit Statistik-Einwilligung verfügbar.')
            t = t.replace('Es ist noch kein Statistikdienst aktiviert. Es werden keine Analytics-Cookies und keine Analytics-Anfragen gesendet. Die vorbereitete Statistikoption ist deshalb nicht auswählbar. Vor einer Aktivierung werden Anbieter, Datenarten, Zwecke, Speicherdauer und mögliche Übermittlungen hier und in der Datenschutzerklärung konkret benannt. Optionale Statistik erfordert eine eigene freiwillige Einwilligung.', 'Google Analytics 4 wird nur nach Ihrer freiwilligen Statistik-Einwilligung geladen. Bei Ablehnung werden keine Google-Tags geladen und keine Statistik-Anfragen gesendet. Die Details stehen im Abschnitt Google Analytics 4 auf dieser Seite.')
            t = t.replace('Diese Website nutzt derzeit keine Analyse- oder Werbedienste', 'Diese Website nutzt Google Analytics 4 nur nach Ihrer Statistik-Einwilligung, aber keine externen Werbedienste')
            t = t.replace('Alle optionalen Dienste sind ausgeschaltet.', 'Ohne Einwilligung bleibt Statistik ausgeschaltet. Externe Werbung bleibt unabhängig davon aus.')
            t = t.replace('Derzeit sind Google Analytics, Google AdSense und Affiliate-Netzwerke nicht eingebunden. Es werden weder Google-Tags noch ein Tag Manager vorgeladen.', 'Google Analytics 4 wird nur nach Statistik-Einwilligung geladen. Google AdSense und Affiliate-Netzwerke sind nicht eingebunden. Vor der Einwilligung werden keine Google-Tags vorgeladen; ein Tag Manager wird nicht verwendet.')
            t = t.replace('## Statistik: derzeit aus', '## Statistik mit Einwilligung').replace('<h2 id="statistik-derzeit-aus">Statistik: derzeit aus</h2>', '<h2 id="statistik-mit-einwilligung">Statistik mit Einwilligung</h2>')
            t = t.replace('Stand: 19. Oktober 2026, Vorbereitung ohne aktive Statistik- oder Werbedienste.', 'Stand: 19. Oktober 2026. Statistik nur mit Einwilligung; Werbedienste aus.')
        t = t.replace('</body>',extra+'</body>',1); f.write_text(t)
    p = out/'sitemap.xml'; xml=p.read_text()
    if 'https://intelligenz-welt.de/werben/' not in xml: p.write_text(xml.replace('</urlset>','<url><loc>https://intelligenz-welt.de/werben/</loc></url></urlset>'))
    print('Monetization: consent-gated analytics '+('available' if active else 'off')+'; advertising off; advertiser page generated')

if __name__=='__main__': main(sys.argv[1])
