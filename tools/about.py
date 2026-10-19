#!/usr/bin/env python3
"""Expanded About page (/ueber-uns/). Stdlib only, no network. Post-build step: reuses the
site shell of the generated page and replaces its <article>. Usage: python3 tools/about.py <out>"""
import sys, json, re, html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
E = lambda s: html.escape(str(s), quote=True)
BASE = 'https://intelligenz-welt.de'
MAIL = 'philipp.l.paulik@gmail.com'

CSS = '''.ab{max-width:1080px;margin:0 auto;padding:40px 20px 56px}.ab h1{font-size:clamp(32px,5vw,52px);line-height:1.1;letter-spacing:-.03em;margin:10px 0 16px}
.ab .kick{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ac)}.ab p.ab-lead{font-size:20px;line-height:1.6;max-width:760px;color:var(--fg);margin:0 0 22px}
.ab h2{font-size:clamp(24px,3vw,32px);letter-spacing:-.02em;line-height:1.2;margin:56px 0 8px}.ab .sub{color:var(--mut);font-size:17px;line-height:1.6;max-width:720px;margin:0 0 22px}
.ab-cta{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 0}.ab-cta a{display:inline-block;padding:11px 18px;border-radius:10px;font-weight:600;font-size:15px;border:1px solid var(--line);background:#fff;color:var(--fg)}
.ab-cta a.p{background:var(--fg);color:#fff;border-color:var(--fg)}.ab-cta a:hover{border-color:var(--ac);color:var(--ac)}.ab-cta a.p:hover{background:var(--ac);color:#fff}
.ab-hero{background:linear-gradient(135deg,#f1f5f9 0%,#eaf2fb 100%);border:1px solid var(--line);border-radius:22px;padding:44px 36px}
.ab-facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:26px 0 0}.ab-fact{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.ab-fact b{display:block;font-size:28px;letter-spacing:-.02em;line-height:1.1}.ab-fact span{font-size:13px;color:var(--mut)}
.ab-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.ab-grid3{grid-template-columns:repeat(3,minmax(0,1fr))}
.ab-card{border:1px solid var(--line);border-radius:16px;padding:24px;background:#fff}.ab-card h3{margin:0 0 8px;font-size:19px;letter-spacing:-.01em;line-height:1.3}.ab-card p{margin:0;color:var(--mut);font-size:15.5px;line-height:1.65}
.ab-card .t{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ac);margin-bottom:8px}.ab-card a.more{display:inline-block;margin-top:12px;font-weight:600;font-size:14.5px}
.ab-steps{list-style:none;margin:0;padding:0;counter-reset:s;display:grid;gap:12px}.ab-steps li{counter-increment:s;position:relative;border:1px solid var(--line);border-radius:14px;padding:18px 20px 18px 66px;background:#fff;line-height:1.65;font-size:16px}
.ab-steps li:before{content:counter(s);position:absolute;left:18px;top:16px;width:34px;height:34px;border-radius:50%;background:var(--acd);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center}
.ab-steps b{display:block;font-size:17px;margin-bottom:2px}
.ab-split{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:28px;align-items:start}
.ab-list{margin:0;padding:0;list-style:none;display:grid;gap:8px}.ab-list li{padding:10px 14px;border:1px solid var(--line);border-radius:10px;background:#fff;font-size:15.5px;line-height:1.5}
.ab-note{background:var(--soft);border:1px solid var(--line);border-radius:14px;padding:18px 20px;font-size:15.5px;line-height:1.65;color:var(--fg)}.ab-note b{display:block;margin-bottom:4px}
.ab-faq details{border:1px solid var(--line);border-radius:12px;background:#fff;margin:0 0 10px;padding:0}.ab-faq summary{cursor:pointer;font-weight:600;font-size:17px;padding:16px 20px;list-style:none;display:flex;justify-content:space-between;gap:16px}
.ab-faq summary::-webkit-details-marker{display:none}.ab-faq summary:after{content:"+";color:var(--ac);font-size:22px;line-height:1}.ab-faq details[open] summary:after{content:"\\2212"}
.ab-faq details p{margin:0;padding:0 20px 18px;color:var(--mut);font-size:16px;line-height:1.7}.ab-faq summary:focus-visible,.ab-cta a:focus-visible{outline:2px solid var(--ac);outline-offset:2px}
.ab-end{margin-top:56px;background:var(--dark);color:#e2e8f0;border-radius:20px;padding:34px 32px}.ab-end h2{margin:0 0 8px;color:#fff}.ab-end p{margin:0 0 16px;color:#cbd5e1;font-size:17px;line-height:1.6;max-width:680px}
.ab-end .ab-cta a{background:transparent;color:#fff;border-color:#475569}.ab-end .ab-cta a.p{background:#fff;color:var(--dark);border-color:#fff}.ab-end .ab-cta a:hover{border-color:#fff;color:#fff;background:#1e293b}.ab-end .ab-cta a.p:hover{background:#e2e8f0;color:var(--dark)}
@media(max-width:860px){.ab-facts{grid-template-columns:repeat(2,minmax(0,1fr))}.ab-grid3{grid-template-columns:repeat(2,minmax(0,1fr))}.ab-split{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.ab{padding:24px 16px 40px}.ab-hero{padding:26px 20px;border-radius:16px}.ab p.ab-lead{font-size:18px}.ab-grid,.ab-grid3{grid-template-columns:minmax(0,1fr)}.ab-card{padding:20px}.ab-steps li{padding:16px 16px 16px 58px}.ab-end{padding:26px 20px}.ab h2{margin-top:42px}.ab-cta a{flex:1 1 100%;text-align:center}}
'''

FAQ = [
 ('Wer steckt hinter Intelligenz Welt?', 'Intelligenz Welt wird von Philipp Paulik betrieben und verantwortet. Anschrift und Verantwortlichkeit stehen im <a href="/impressum/">Impressum</a>, mehr zum Autor auf seinem <a href="/redakteur/philipp-paulik/">Autorenprofil</a>.'),
 ('Schreibt hier eine KI die Artikel?', 'Redaktionelle Artikel entstehen mit KI-Unterstützung (Recherche und Textentwurf) und werden vor der Veröffentlichung von einem Menschen inhaltlich geprüft und freigegeben. Jeder Artikel trägt dazu einen Hinweis. Die KI-News-Übersicht ist dagegen automatisch aggregiert und enthält keine KI-verfassten Texte. Details: <a href="/transparenz/">KI-Transparenz</a>.'),
 ('Woher kommen die News?', 'Aus öffentlichen RSS-Feeds und Schnittstellen von THE DECODER, The Verge (AI), TechCrunch (AI), dem Hugging Face Blog, Hacker News und heise online. Wir zeigen Überschrift und Kurzteaser und verlinken auf die Originalquelle. Maßgeblich ist immer der Originaltext.'),
 ('Was ist das Modell-Radar?', 'Eine Übersicht der aktuell meistbeachteten Modelle auf Hugging Face mit Likes, Downloads und Aufgabenbereich. Sie zeigt Beachtung, keine Qualität: ein Ranking nach Leistung ist das nicht.'),
 ('Was sind die Portraits?', 'Kompakte Steckbriefe zu KI-Unternehmen und KI-Modellen. Jede Angabe nennt Quelle und Abrufdatum. Wo uns ein ausreichend zugeordnetes Ergebnis fehlt, steht das so da, statt eine Zahl zu schätzen. Die Portraits wachsen schrittweise: <a href="/unternehmen/">Unternehmen</a>, <a href="/ki-modelle/">KI-Modelle</a>.'),
 ('Wie melde ich einen Fehler?', 'Per E-Mail an <a href="mailto:%s">%s</a> mit dem Betreff „Korrektur: [Titel des Artikels]". Wir prüfen jede Meldung, in der Regel innerhalb von zwei Werktagen. Inhaltliche Korrekturen werden im Artikel mit Datum vermerkt, siehe <a href="/korrekturen/">Korrekturen</a>.' % (MAIL, MAIL)),
 ('Gibt es Werbung auf der Seite?', 'Aktuell nicht. Werbung und Statistikdienste sind vorbereitet, aber ausgeschaltet und laden ohne Ihre Einwilligung nichts nach. Sollte Werbung kommen, wird sie als „Anzeige“ gekennzeichnet und beeinflusst keine redaktionelle Entscheidung. Mehr unter <a href="/werbung/">Werbung &amp; Affiliate</a> und <a href="/cookies/">Cookies &amp; Einstellungen</a>.'),
 ('Kann ich Inhalte nutzen oder verlinken?', 'Verlinken ist ausdrücklich erlaubt. Bei Bildern bitten wir um Quellenangabe (Intelligenz Welt, intelligenz-welt.de); für weitergehende Nutzung bitte vorher per E-Mail fragen. Titelbilder sind KI-generierte Symbolbilder und im Bild entsprechend gekennzeichnet.'),
 ('Gibt es einen Newsletter oder Feed?', 'Einen RSS-Feed gibt es: <a href="/feed.xml">/feed.xml</a>. Einen Newsletter bieten wir derzeit nicht an.'),
 ('Kann ich mit Intelligenz Welt zusammenarbeiten?', 'Gern. Anfragen zu Kooperationen und Werbeformaten gehen über <a href="/werben/">Werben &amp; Kooperationen</a> oder direkt per E-Mail. Eine Zusammenarbeit kauft keine Berichterstattung.'),
]

def build(out):
    out = Path(out); f = out / 'ueber-uns' / 'index.html'; t = f.read_text()
    d = json.loads((ROOT / 'content/portraits.json').read_text())
    n_art = len(list((ROOT / 'content/articles').glob('*.json')))
    n_co, n_mo = len(d['companies']), len(d['models'])
    n_src = 6
    facts = [(n_art, 'eigene Artikel'), (n_src, 'Quellen in der News-Übersicht'), (n_co + n_mo, 'Portraits (Unternehmen und Modelle)'), ('0', 'Anzeigen und Tracker aktiv')]
    facts_html = ''.join('<div class="ab-fact"><b>%s</b><span>%s</span></div>' % (E(a), E(b)) for a, b in facts)
    title = 'Über uns: Wer wir sind und wie wir arbeiten | Intelligenz Welt'
    desc = 'Intelligenz Welt ist ein unabhängiges deutschsprachiges KI-Magazin von Philipp Paulik: wie Artikel, News und Portraits entstehen, woher die Quellen kommen und wie wir mit KI und Werbung umgehen.'
    cards = [
     ('KI-News', 'Die Übersicht', 'Überschriften und Kurzteaser aus sechs öffentlichen Quellen, automatisch gesammelt, alle drei Stunden aktualisiert, immer mit Link zum Original.', '/news/', 'Zu den KI-News'),
     ('Modell-Radar', 'Was gerade Beachtung findet', 'Die meistbeachteten Modelle auf Hugging Face mit Likes, Downloads und Aufgabenbereich. Ein Stimmungsbild, kein Leistungsranking.', '/modelle/', 'Zum Modell-Radar'),
     ('Artikel', 'Einordnung statt Meldung', 'Eigene Beiträge zu Modellen, Agenten, Tools, Sicherheit und Praxis, mit Kernaussagen, Quellenliste und Transparenzhinweis.', '/artikel/', 'Alle Artikel'),
     ('Portraits', 'Nachschlagen mit Beleg', 'Steckbriefe zu KI-Unternehmen und KI-Modellen. Jede Angabe mit Quelle und Abrufdatum, Lücken stehen offen da.', '/unternehmen/', 'Zu den Portraits'),
    ]
    cards_html = ''.join('<div class="ab-card"><span class="t">%s</span><h3>%s</h3><p>%s</p><a class="more" href="%s">%s →</a></div>' % (E(a), E(b), E(c), E(h), E(l)) for a, b, c, h, l in cards)
    steps = [
     ('Thema und Quellen', 'Wir wählen Themen nach Relevanz, nicht nach Klickpotenzial, und beginnen mit Primärquellen: Veröffentlichungen, Modellkarten, technische Dokumentation, offizielle Ankündigungen.'),
     ('Entwurf mit KI-Unterstützung', 'KI-Werkzeuge helfen bei Recherche und Textentwurf. Sie entscheiden nichts und veröffentlichen nichts.'),
     ('Prüfung durch einen Menschen', 'Existiert die Quelle wirklich? Stimmt die Zahl im Original? Ist das Datum aktuell? Ist eine Einordnung belegt oder Spekulation? Strittige Aussagen prüfen wir an mindestens zwei unabhängigen Quellen.'),
     ('Veröffentlichung mit Belegen', 'Der Artikel nennt seine Quellen, trägt den Hinweis „mit KI-Unterstützung erstellt, redaktionell verantwortet“ und, falls KI-generiert, ein im Bild gekennzeichnetes Titelbild.'),
     ('Korrektur, wenn nötig', 'Inhaltliche Fehler korrigieren wir im Artikel, setzen das Aktualisierungsdatum und vermerken die Korrektur mit Datum. Artikel werden nicht still gelöscht.'),
    ]
    steps_html = ''.join('<li><b>%s</b>%s</li>' % (E(a), E(b)) for a, b in steps)
    vals = [
     ('Belegt', 'Jede Zahl und jede Tatsachenbehauptung stammt aus einer genannten Quelle oder ist als eigene Einschätzung markiert. Wir erfinden keine Zitate, Zahlen oder Studien.'),
     ('Offen', 'Wir sagen, wo KI im Spiel ist, wo wir etwas nicht wissen und wo ein Ergebnis fehlt.'),
     ('Unabhängig', 'Die Redaktion entscheidet allein über Themen und Inhalte. Bezahlte Inhalte würden gekennzeichnet und nichts beeinflussen.'),
     ('Verständlich', 'Wir wollen informieren, nicht dramatisieren, und technische Dinge so erklären, dass man sie ohne Vorkenntnisse versteht.'),
    ]
    vals_html = ''.join('<div class="ab-card"><h3>%s</h3><p>%s</p></div>' % (E(a), E(b)) for a, b in vals)
    srcs = ['THE DECODER', 'The Verge (AI)', 'TechCrunch (AI)', 'Hugging Face Blog', 'Hacker News', 'heise online']
    srcs_html = ''.join('<li>%s</li>' % E(s) for s in srcs)
    faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), a) for q, a in FAQ)
    main = '''<main id="main"><div class="ab">
<section class="ab-hero"><span class="kick">Über Intelligenz Welt</span><h1>Künstliche Intelligenz verständlich einordnen.</h1>
<p class="ab-lead">Intelligenz Welt ist ein unabhängiges deutschsprachiges KI-Magazin. Wir verfolgen Modelle, Agenten, Sicherheit und die Frage, was das für Arbeit und Gesellschaft bedeutet, und sagen dabei offen, woher unsere Informationen kommen und wo KI beim Schreiben hilft.</p>
<div class="ab-cta"><a class="p" href="/artikel/">Artikel lesen</a><a href="/news/">KI-News</a><a href="/transparenz/">So arbeiten wir</a></div>
<div class="ab-facts">%(facts)s</div></section>

<h2 id="angebot">Was Sie hier finden</h2><p class="sub">Vier Bereiche mit unterschiedlicher Arbeitsweise. Wir trennen klar, was automatisch gesammelt und was redaktionell geschrieben wird.</p>
<div class="ab-grid">%(cards)s</div>

<h2 id="arbeitsweise">So entsteht ein Artikel</h2><p class="sub">KI hilft beim Entwurf, die Verantwortung bleibt bei einem Menschen. Diesen Ablauf halten wir ein.</p>
<ol class="ab-steps">%(steps)s</ol>

<h2 id="grundsaetze">Unsere Grundsätze</h2><div class="ab-grid">%(vals)s</div>

<h2 id="quellen">Woher die News kommen</h2>
<div class="ab-split"><div><p class="sub" style="margin-bottom:0">Die KI-News werden automatisch aus öffentlichen RSS-Feeds und Schnittstellen gesammelt. Wir übernehmen Überschrift und Kurzteaser, verlinken auf die Originalquelle und verfassen dazu keine KI-Texte. Der Modell-Radar nutzt die öffentliche Schnittstelle von Hugging Face.</p>
<p style="margin:16px 0 0"><a href="/quellen/">Quellen und Faktencheck →</a></p></div><ul class="ab-list">%(srcs)s</ul></div>

<h2 id="werbung">Werbung und Unabhängigkeit</h2>
<div class="ab-note"><b>Aktueller Stand: keine Werbung, keine Affiliate-Links, kein Tracking.</b>Werbung und Statistik sind vorbereitet, aber ausgeschaltet. Ohne Ihre Einwilligung wird kein Statistik- oder Werbedienst geladen. Falls das später anders wird, gilt: Bezahltes wird mit „Anzeige“ gekennzeichnet, redaktionelle Inhalte bleiben unabhängig, und Reichweite wird nicht zugesagt. <a href="/werbung/">Werbung &amp; Affiliate</a> · <a href="/cookies/">Cookies &amp; Einstellungen</a></div>

<h2 id="dahinter">Wer dahintersteht</h2>
<div class="ab-split"><div class="ab-card"><span class="t">Betreiber und Herausgeber</span><h3>Philipp Paulik</h3><p>Intelligenz Welt wird von Philipp Paulik betrieben und verantwortet, auch im Sinne des § 18 Abs. 2 MStV. Er trifft die Themenauswahl, prüft die Quellen und gibt jeden Beitrag frei.</p><a class="more" href="/redakteur/philipp-paulik/">Zum Autorenprofil →</a> <a class="more" href="/impressum/" style="margin-left:14px">Impressum →</a></div>
<div class="ab-card"><span class="t">Transparenz</span><h3>Eine Person, klare Regeln</h3><p>Es gibt hier keine große Redaktion, und wir tun nicht so. Dafür sind die Regeln öffentlich: <a href="/redaktion/">Redaktionelle Grundsätze</a>, <a href="/transparenz/">KI-Transparenz</a>, <a href="/korrekturen/">Korrekturen</a>, <a href="/quellen/">Quellen</a>.</p></div></div>

<h2 id="faq">Häufige Fragen</h2><div class="ab-faq">%(faq)s</div>

<section class="ab-end"><h2>Hinweis, Fehler oder Zusammenarbeit?</h2><p>Wir freuen uns über Korrekturen, Themenvorschläge und Anfragen. Geschrieben wird per E-Mail, eine Antwort kommt in der Regel innerhalb von zwei Werktagen.</p>
<div class="ab-cta"><a class="p" href="mailto:%(mail)s">%(mail)s</a><a href="/kontakt/">Kontakt</a><a href="/werben/">Werben &amp; Kooperationen</a></div></section>
</div></main>''' % dict(facts=facts_html, cards=cards_html, steps=steps_html, vals=vals_html, srcs=srcs_html, faq=re.sub(r'%', '%', faq_html), mail=MAIL)
    ld = [{'@context': 'https://schema.org', '@type': 'AboutPage', 'name': 'Über Intelligenz Welt', 'url': BASE + '/ueber-uns/', 'inLanguage': 'de-DE', 'description': desc,
           'about': {'@type': 'Organization', 'name': 'Intelligenz Welt', 'url': BASE + '/', 'founder': {'@type': 'Person', 'name': 'Philipp Paulik', 'url': BASE + '/redakteur/philipp-paulik/'}}},
          {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', html.unescape(a))}} for q, a in FAQ]}]
    head = t[:t.index('<body>')]
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % E(title), head, flags=re.S)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', '', head, flags=re.S)
    head = re.sub(r'<meta (?:name="description"|property="og:(?:title|description)"|name="twitter:(?:title|description)")[^>]*>', '', head)
    extra = '<meta name="description" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><link rel="stylesheet" href="/assets/about.css"><script type="application/ld+json">%s</script>' % (E(desc), E(title), E(desc), json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'))
    head = head.replace('</head>', extra + '</head>')
    i = t.index('</header>') + 9
    if t.startswith('<script>', i): i = t.index('</script>', i) + 9
    top = t[t.index('<body>'):i]
    foot = t[t.index('<footer', i):]
    (out / 'assets').mkdir(exist_ok=True); (out / 'assets/about.css').write_text(CSS)
    f.write_text(head + top + main + foot)
    print('about page ok, articles:', n_art)

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'site/out')
