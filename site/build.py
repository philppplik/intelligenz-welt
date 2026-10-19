import json,os,re,shutil,sys
from common import *
SRC_ICON_DIR='source-icons'
OUT='out'; shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+'/artikel'); os.makedirs(OUT+'/news')
BASE='https://intelligenz-welt.de'
NOW=datetime.datetime.now().astimezone()
ai=json.load(open('../data/ai_archive.json')); models=[m for m in json.load(open('../data/models.json')) if not re.search('uncensored|nsfw|abliterat',m['id'],re.I)]
import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent.parent/'tools'))
from licensed_news import archive_body as licensed_archive_body, collect, merge_current, valid as licensed_valid, detail_path as licensed_path, body as licensed_body, noindex as licensed_noindex, write_css
licensed=collect('..','iw')
ai=merge_current(ai,licensed)

ART=[]  # legacy Briefing/Analyse essays removed; their URLs are redirect stubs (see end of file)
arts=[]
for slug,cat,date in ART:
    s=open('src/artikel_%s.html'%slug).read()
    title=strip(re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S).group(1))
    m=re.search(r'<article>(.*?)</article>',s,re.S)
    inner=m.group(1) if m else ''
    ll=re.search(r'class="lead-text">(.*?)</div>',s,re.S)
    body=[(t,strip(x)) for t,x in re.findall(r'<(h2|h3|p|blockquote)[^>]*>(.*?)</\1>',inner,re.S) if strip(x)]
    if ll: body.insert(0,('p',strip(ll.group(1))))
    lead=body[0][1] if body else ''
    arts.append(dict(slug=slug,cat=cat,date=date,title=title,body=body,lead=lead[:200]))
    print(slug,len(body),title[:60])
CSS='''
:root{--bg:#fff;--fg:#0f172a;--mut:#64748b;--line:#e2e8f0;--ac:#1d6bc0;--acd:#093A6A;--soft:#f1f5f9;--dark:#0b1220}
.menu{display:flex;align-items:center;gap:28px}.burger{display:none}.sic{display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border:1px solid var(--line);border-radius:8px;color:var(--mut);flex:none}.sic:hover{color:var(--ac);border-color:var(--ac)}.sic svg{display:block}.sic:focus-visible{outline:2px solid var(--ac);outline-offset:2px}@media(min-width:801px){.menu a.l[href="/suche/"]{display:none}}.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}
.lead{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:28px;margin:28px 0 8px}.lead-main{display:block}.lead-main img,.th img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:12px;background:var(--soft)}.lead-main h2{font-size:34px;line-height:1.15;letter-spacing:-.025em;margin:12px 0 10px}.lead-main p{font-size:17px;color:var(--mut);margin:0 0 10px}.lead-main:hover h2{color:var(--ac)}
.lead-side{display:flex;flex-direction:column;gap:0}.lead-side a{display:grid;grid-template-columns:104px minmax(0,1fr);gap:14px;padding:14px 0;border-bottom:1px solid var(--line)}.lead-side a:first-child{padding-top:0}.lead-side a:last-child{border-bottom:0}.lead-side img{width:104px;height:70px;object-fit:cover;border-radius:8px;display:block}.lead-side h3{font-size:16px;line-height:1.3;margin:4px 0 4px;letter-spacing:-.01em}.lead-side a:hover h3{color:var(--ac)}
.tgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.th{display:block}.th h3{font-size:18px;line-height:1.3;margin:10px 0 6px;letter-spacing:-.01em}.th:hover h3{color:var(--ac)}.th .meta{margin-top:6px}.hupd{font-size:13px;color:var(--mut);margin:6px 0 0}
@media(max-width:800px){.lead{grid-template-columns:1fr;gap:18px;margin-top:16px}.lead-main h2{font-size:26px}.lead-main p{font-size:16px}.tgrid{grid-template-columns:1fr;gap:20px}.lead-side a{grid-template-columns:96px minmax(0,1fr)}.lead-side img{width:96px;height:64px}}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
a{color:inherit;text-decoration:none}a:hover{color:var(--ac)}
.w{max-width:1180px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(255,255,255,.94);backdrop-filter:blur(8px);z-index:9}
.nav{display:flex;align-items:center;gap:28px;height:60px}.logo{white-space:nowrap;flex:none;font-weight:800;font-size:19px;letter-spacing:-.02em;display:inline-flex;align-items:center;gap:9px}.logo img{display:block;width:30px;height:30px}.logo b{color:var(--ac)}
.nav a.l{font-size:14px;color:var(--mut);font-weight:500}.nav a.l:hover,.nav a.act{color:var(--fg)}.sp{flex:1}
.btn{background:var(--fg);color:#fff;padding:8px 16px;border-radius:8px;font-size:14px;font-weight:600}.btn:hover{background:var(--ac);color:#fff}
.hero{padding:56px 0 32px}.hero h1{font-size:44px;line-height:1.1;letter-spacing:-.03em;margin:0 0 14px;max-width:760px}.hero p{color:var(--mut);font-size:18px;max-width:640px;margin:0}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:28px 0}.stat{border:1px solid var(--line);border-radius:12px;padding:16px}.stat b{display:block;font-size:26px;letter-spacing:-.02em}.stat span{font-size:13px;color:var(--mut)}
h2.sec{font-size:22px;letter-spacing:-.02em;margin:40px 0 16px;display:flex;justify-content:space-between;align-items:baseline}h2.sec a{font-size:14px;color:var(--ac);font-weight:600}
.grid{display:grid;grid-template-columns:2fr 1fr;gap:32px}
.card{border:1px solid var(--line);border-radius:14px;padding:22px;background:#fff;transition:.15s}.card:hover{border-color:var(--ac);box-shadow:0 6px 24px rgba(29,107,192,.12)}
.tag{display:inline-block;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--acd);background:#e3effb;padding:2px 8px;border-radius:99px}
.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.card h3{margin:10px 0 6px;font-size:18px;line-height:1.3;letter-spacing:-.01em}.card p{margin:0;color:var(--mut);font-size:14px}.meta{font-size:12px;color:var(--mut);margin-top:10px}
.feed{list-style:none;margin:0;padding:0}.feed li{padding:14px 0;border-bottom:1px solid var(--line)}.feed a{font-weight:600;font-size:15px;line-height:1.4;display:block}.feed .m{font-size:12px;color:var(--mut);margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:14px}th{text-align:left;color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em;padding:10px;border-bottom:1px solid var(--line)}td{padding:11px 10px;border-bottom:1px solid var(--line)}tr:hover td{background:var(--soft)}
.bar{height:6px;border-radius:3px;background:#e3effb;min-width:40px}.bar i{display:block;height:100%;background:var(--ac);border-radius:3px}
.art{max-width:720px;margin:0 auto;padding:40px 20px}.art h1{font-size:38px;line-height:1.15;letter-spacing:-.03em}.art p{font-size:18px;line-height:1.75}.art h2{margin-top:36px;letter-spacing:-.02em}.art blockquote{border-left:3px solid var(--ac);margin:24px 0;padding:4px 20px;color:var(--mut);font-style:italic}
@media(max-width:800px){.nav{height:auto;min-height:56px;flex-wrap:wrap;gap:0 12px;padding:8px 20px}.logo{flex:none;white-space:nowrap;font-size:18px}.logo img{width:28px;height:28px}.btn{padding:6px 12px;font-size:13px}.burger{display:inline-flex;flex-direction:column;justify-content:center;gap:4px;width:40px;height:40px;padding:0 9px;border:1px solid var(--line);border-radius:8px;background:#fff;cursor:pointer}.burger span{display:block;height:2px;background:var(--fg);border-radius:2px}.menu{order:5;flex-basis:100%;flex-direction:column;align-items:stretch;gap:0;border-top:1px solid var(--line);margin:8px -20px 0;padding:2px 20px 8px;background:#fff}.menu a.l{padding:13px 0;font-size:16px;border-bottom:1px solid var(--line)}.menu a.l:last-child{border-bottom:0}.js .menu{display:none}.js .menu.open{display:flex}}
footer{background:var(--dark);color:#94a3b8;margin-top:80px;padding:44px 0;font-size:14px}footer a{color:#cbd5e1}footer a:hover{color:#fff}footer .c{display:flex;gap:48px;flex-wrap:wrap}footer h4{color:#fff;margin:0 0 10px;font-size:13px;text-transform:uppercase;letter-spacing:.06em}footer a{display:block;margin:6px 0}
.upd{font-size:13px;color:var(--mut)}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;margin-right:6px}
@media(max-width:800px){.grid>*,.cards>*{min-width:0}.tw{overflow-x:auto}body{overflow-x:hidden}.grid,.cards{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.hero h1{font-size:32px}.nav{gap:14px;overflow-x:auto}.nav a.l{white-space:nowrap}.art h1{font-size:28px}table{font-size:12px}}
.sform{display:flex;gap:10px;margin:4px 0 6px}.sform input{flex:1;min-width:0;font:16px Inter,system-ui,sans-serif;color:var(--fg);padding:12px 16px;border:1px solid var(--line);border-radius:10px;min-height:48px;background:#fff}.sform input:focus{outline:2px solid var(--ac);outline-offset:1px;border-color:var(--ac)}.sstatus{font-size:14px;color:var(--mut);margin:12px 0 0;min-height:22px}.sresults{list-style:none;margin:14px 0 0;padding:0}.sresults li{padding:16px 0;border-bottom:1px solid var(--line)}.sresults a.rt{font-weight:700;font-size:18px;line-height:1.35;letter-spacing:-.01em}.sresults a.rt:hover{color:var(--ac)}.sresults p{margin:6px 0 0;color:var(--mut);font-size:14px}.sresults .sm{font-size:12px;color:var(--mut);margin-top:6px}@media(max-width:800px){.sform{flex-direction:column}.sform .btn{align-self:flex-start}}
'''
CSS += '@media(max-width:800px){.nav{gap:8px;overflow:visible}.nav>.btn{display:none}.nav>.sic{width:40px;height:40px}.nav>.sp{min-width:0}.menu{order:5}}'
CSS+='.feed .m{display:flex;align-items:center;gap:8px}.si{flex:none;width:20px;height:20px;border-radius:5px;display:block;background:#fff;object-fit:contain}.si.mono{display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;letter-spacing:.02em;color:hsl(var(--h) 55% 28%);background:hsl(var(--h) 70% 92%)}'
os.makedirs(OUT+'/assets/source-icons',exist_ok=True)
for f in os.listdir(SRC_ICON_DIR):
    if f.endswith('.png'): shutil.copy(os.path.join(SRC_ICON_DIR,f),OUT+'/assets/source-icons/'+f)
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tools'))
import report_visuals as RV
RV.load_logos(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
CSS+=RV.CSS_COMMON+RV.CSS_WEB
open(OUT+'/style.css','w').write(CSS)
NAVL=[('/news/','KI-News'),('/modelle/','Modell-Radar'),('/suche/','Suche'),('/ueber-uns/','Über uns')]
def page(path,title,desc,body,ld=None,typ='website',og=None,act=''):
    url=BASE+path
    nav=''.join('<a class="l%s" href="%s">%s</a>'%(' act' if act==h else '',h,t) for h,t in NAVL)
    ldj=''
    if ld: ldj='<script type="application/ld+json">%s</script>'%json.dumps(ld,ensure_ascii=False)
    h='''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><meta name="description" content="%s"><link rel="canonical" href="%s"><meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s"><meta property="og:type" content="%s"><meta property="og:site_name" content="Intelligenz Welt"><meta property="og:locale" content="de_DE"><meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Intelligenz Welt" href="/feed.xml"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="32x32" href="/assets/branding/favicon-32.png"><link rel="icon" type="image/png" sizes="16x16" href="/assets/branding/favicon-16.png"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="stylesheet" href="/style.css">%s</head><body>
<header><div class="w nav"><a class="logo" href="/"><img src="/assets/branding/logo.svg" alt="" width="30" height="30"><span>Intelligenz<b>Welt</b></span></a><nav class="menu" id="menu" aria-label="Hauptnavigation">%s</nav><span class="sp"></span><a class="sic" href="/suche/" aria-label="Suche" title="Suche"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg></a><a class="btn" href="/feed.xml">RSS</a><button type="button" class="burger" aria-label="Menü" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button></div></header><script>document.documentElement.classList.add("js");(function(){var b=document.querySelector(".burger"),m=document.getElementById("menu");if(!b)return;b.addEventListener("click",function(){var o=m.classList.toggle("open");b.setAttribute("aria-expanded",o?"true":"false");b.setAttribute("aria-label",o?"Menü schließen":"Menü")});document.addEventListener("keydown",function(e){if(e.key==="Escape"&&m.classList.contains("open")){m.classList.remove("open");b.setAttribute("aria-expanded","false");b.focus()}})})()</script>
%s
<footer><div class="w c"><div><b style="color:#fff;font-size:17px">Intelligenz Welt</b><p style="max-width:300px">KI-News, Modell-Radar und Artikel auf Deutsch. News werden automatisch aus öffentlichen RSS-Feeds und APIs aggregiert.</p></div><div><h4>Magazin</h4><a href="/news/">KI-News</a><a href="/modelle/">Modell-Radar</a><a href="/feed.xml">RSS-Feed</a></div><div><h4>Rechtliches</h4><a href="/impressum/">Impressum</a><a href="/datenschutz/">Datenschutz</a><a href="/kontakt/">Kontakt</a></div></div><div class="w" style="margin-top:24px">© %d Intelligenz Welt</div></footer></body></html>'''%(esc(title),esc(desc),url,esc(title),esc(desc),url,typ,ldj,nav,body,NOW.year)
    p=OUT+path+('index.html' if path.endswith('/') else '')
    os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(h)
    return url
urls=[]

def src_slug(name):
    return re.sub(r'[^a-z0-9]+','-',(name or '').lower()).strip('-')
def src_mark(name):
    """Local source icon (no hotlinks) or a monogram fallback."""
    slug=src_slug(name)
    if slug and os.path.isfile(os.path.join(SRC_ICON_DIR,slug+'.png')):
        return '<img class="si" src="/assets/source-icons/%s.png" width="20" height="20" alt="" loading="lazy" decoding="async">'%slug
    words=[w for w in re.split(r'\s+',(name or '').strip()) if w]
    mono=(''.join(w[0] for w in words[:2]) or '?').upper()
    hue=int(hashlib.sha256(slug.encode()).hexdigest()[:4],16)%360
    return '<span class="si mono" style="--h:%d" aria-hidden="true">%s</span>'%(hue,esc(mono))
def newsli(items,n):
    return '<ul class="feed">'+''.join('<li><a href="%s" rel="noopener nofollow" target="_blank">%s</a><div class="m">%s<span>%s \u00b7 %s</span></div></li>'%(esc(licensed_path(i) if licensed_valid(i,'iw') else i['url']),esc(i['title']),src_mark(i['src']),esc(i['src']),fmtd(i['ts'])) for i in items[:n])+'</ul>'
def artcards(l):
    return '<div class="cards">'+''.join('<a class="card" href="/artikel/%s/"><span class="tag">%s</span><h3>%s</h3><p>%s…</p><div class="meta">%s · %d Min. Lesezeit</div></a>'%(a['slug'],a['cat'],esc(a['title']),esc(a['lead'][:150]),datetime.datetime.fromisoformat(a['date']).strftime('%d.%m.%Y'),max(3,sum(len(x) for _,x in a['body'])//900)) for a in l)+'</div>'
mx=max([m['likes'] for m in models] or [1])
def mtable(n):
    return '<div class="tw"><table><tr><th>#</th><th>Modell</th><th>Aufgabe</th><th>Likes</th><th>Downloads</th></tr>'+''.join('<tr><td>%d</td><td><a href="%s" target="_blank" rel="noopener"><b>%s</b></a></td><td>%s</td><td>%s<div class="bar"><i style="width:%d%%"></i></div></td><td>%s</td></tr>'%(i+1,m['url'],esc(m['id']),esc(m['tag'] or '–'),f"{m['likes']:,}".replace(',','.'),m['likes']*100//mx,f"{m['dl']:,}".replace(',','.')) for i,m in enumerate(models[:n]))+'</table></div>'
upd='<span class="upd"><span class="dot"></span>Aktualisiert %s · automatisch aus %d Quellen</span>'%(NOW.strftime('%d.%m.%Y %H:%M'),len({i['src'] for i in ai}))
home='''<div class="w"><div class="hero"><h1>Was in der KI-Welt gerade wirklich zählt.</h1><p>Aktuelle News zu LLMs, Agenten und Modellen, ein Live-Radar der meistdiskutierten Open-Source-Modelle und Artikel, die einordnen statt aufzuregen.</p><p style="margin-top:12px">%s</p></div>
<div class="stats"><div class="stat"><b>%d</b><span>News im Archiv</span></div><div class="stat"><b>%d</b><span>Quellen live</span></div><div class="stat"><b>%d</b><span>Trendende Modelle</span></div></div>
<div class="grid"><div><h2 class="sec">Modell-Radar: Trending auf Hugging Face <a href="/modelle/">Mehr →</a></h2>%s</div>
<aside><h2 class="sec" style="margin-top:0">KI-Pulse <a href="/news/">Archiv →</a></h2>%s</aside></div></div>'''%(upd,len(ai),len({i['src'] for i in ai}),len(models),mtable(8),newsli(ai,14))
orgld={'@context':'https://schema.org','@type':'NewsMediaOrganization','name':'Intelligenz Welt','url':BASE,'logo':{'@type':'ImageObject','url':BASE+'/assets/branding/logo-512.png','width':512,'height':512},'email':'philipp.l.paulik@gmail.com'}
siteld={'@context':'https://schema.org','@type':'WebSite','name':'Intelligenz Welt','url':BASE,'inLanguage':'de-DE','publisher':{'@type':'Organization','name':'Intelligenz Welt'}}
urls.append(page('/','Intelligenz Welt: KI-News, Modell-Radar und Artikel','Aktuelle KI- und LLM-News auf Deutsch, Live-Radar der trendenden Open-Source-Modelle und Artikel zu Agenten, Modellen und Strategie.',home,[orgld,siteld]))
urls.append(page('/news/','KI-News: Das Archiv | Intelligenz Welt','Aktuelle Nachrichten zu KI, LLMs und Agenten aus The Decoder, The Verge, TechCrunch, Hugging Face, Hacker News und heise. Automatisch aktualisiert.','<div class="w"><div class="hero"><h1>KI-News</h1><p>%s</p></div>%s%s</div>'%(upd,RV.web_news(ai,models,NOW),newsli(ai,300)),act='/news/'))
urls.append(page('/modelle/','Modell-Radar: Trending LLMs | Intelligenz Welt','Die aktuell meistbeachteten Modelle auf Hugging Face, täglich aktualisiert: Likes, Downloads und Aufgabenbereich.','<div class="w"><div class="hero"><h1>Modell-Radar</h1><p>Die 20 am stärksten trendenden Modelle auf Hugging Face. Daten live aus der öffentlichen Hugging-Face-API, täglich neu gebaut.</p></div>%s%s</div>'%(RV.web_models(ai,models,NOW),mtable(20)),act='/modelle/'))
SUCHE_BODY = '''<div class="w"><div class="hero"><h1>Suche</h1><p>Eigene Artikel durchsuchen, dazu die Schlagzeilen des KI-Pulse. Die Suche l\u00e4uft lokal in deinem Browser, ohne Tracking.</p></div>
<form class="sform" role="search" action="/suche/" method="get"><label class="sr" for="sq">Suchbegriff</label><input id="sq" name="q" type="search" placeholder="z. B. Claude, Agenten, Open Source \u2026" autocomplete="off"><button class="btn" type="submit">Suchen</button></form>
<p id="sstatus" class="sstatus" role="status"></p><ul id="sresults" class="sresults"></ul>
<noscript><p>F\u00fcr die Suche wird JavaScript ben\u00f6tigt. Alle Artikel findest du auch in der <a href="/artikel/" style="text-decoration:underline">Artikel\u00fcbersicht</a>.</p></noscript></div>
<script>''' + open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tools','search.js'),encoding='utf-8').read() + '''</script>'''
urls.append(page('/suche/','Suche | Intelligenz Welt','Artikel und News auf Intelligenz Welt durchsuchen: eigene Beitr\u00e4ge und die Schlagzeilen des KI-Pulse.',SUCHE_BODY,act='/suche/'))
for a in arts:
    b=''.join('<%s>%s</%s>'%({'h3':'h2'}.get(t,t),esc(x),{'h3':'h2'}.get(t,t)) for t,x in a['body'])
    ld={'@context':'https://schema.org','@type':'Article' if a['cat']=='Analyse' else 'NewsArticle','headline':a['title'][:110],'datePublished':a['date']+'T09:00:00+01:00','dateModified':a['date']+'T09:00:00+01:00','author':{'@type':'Person','name':'Philipp Paulik','url':BASE+'/ueber-uns/'},'publisher':orgld,'mainEntityOfPage':BASE+'/artikel/%s/'%a['slug'],'inLanguage':'de-DE','description':a['lead']}
    urls.append(page('/artikel/%s/'%a['slug'],a['title']+' | Intelligenz Welt',a['lead'][:155],'<article class="art"><span class="tag">%s</span><h1>%s</h1><div class="meta">Philipp Paulik · %s</div>%s</article>'%(a['cat'],esc(a['title']),datetime.datetime.fromisoformat(a['date']).strftime('%d.%m.%Y'),b),ld,'article'))
urls.append(page('/ueber-uns/','Über uns | Intelligenz Welt','Intelligenz Welt ist ein unabhängiges deutschsprachiges KI-Magazin von Philipp Paulik.','<article class="art"><h1>Über Intelligenz Welt</h1><p>Intelligenz Welt ordnet die Entwicklung rund um künstliche Intelligenz ein: Modelle, Agenten, Sicherheit und die Frage, was das für Arbeit und Gesellschaft bedeutet.</p><p>Die Nachrichtenübersicht entsteht automatisch aus öffentlichen RSS-Feeds und APIs. Die Artikel sind redaktionell verfasst von Philipp Paulik.</p></article>',act='/ueber-uns/'))
urls.append(page('/kontakt/','Kontakt | Intelligenz Welt','Kontakt zu Intelligenz Welt.','<article class="art"><h1>Kontakt</h1><p>E-Mail: <a href="mailto:philipp.l.paulik@gmail.com">philipp.l.paulik@gmail.com</a></p></article>'))
imp=open('src/impressum.html.txt').read()
page('/impressum/','Impressum | Intelligenz Welt','Impressum','''<article class="art"><h1>Impressum</h1><h2>Angaben gemäß § 5 DDG</h2><p>Philipp Paulik<br>Mozartstraße 1<br>53819 Neunkirchen-Seelscheid<br>Nordrhein-Westfalen</p><h2>Kontakt</h2><p>E-Mail: philipp.l.paulik@gmail.com</p><h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2><p>Philipp Paulik, Anschrift wie oben</p><h2>Haftung für Inhalte</h2><p>Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen. Bei Bekanntwerden von Rechtsverletzungen entfernen wir entsprechende Inhalte umgehend.</p><h2>Haftung für Links</h2><p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Für diese fremden Inhalte übernehmen wir keine Gewähr. Verantwortlich ist stets der jeweilige Anbieter. Die automatisch aggregierten News-Links führen zu den Originalquellen.</p><h2>Urheberrecht</h2><p>Die von den Seitenbetreibern erstellten Inhalte unterliegen dem deutschen Urheberrecht. News-Überschriften und Kurzteaser stammen von den jeweils verlinkten Quellen.</p></article>''')
page('/datenschutz/','Datenschutz | Intelligenz Welt','Datenschutzerklärung','''<article class="art"><h1>Datenschutzerklärung</h1><h2>Verantwortlicher</h2><p>Philipp Paulik, Mozartstraße 1, 53819 Neunkirchen-Seelscheid, philipp.l.paulik@gmail.com</p><h2>Hosting</h2><p>Diese Website wird als statische Seite über GitHub Pages (GitHub Inc., USA) ausgeliefert. Beim Aufruf verarbeitet der Hosting-Anbieter technisch notwendig Ihre IP-Adresse und Zugriffsdaten (Server-Logfiles). Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO (stabiler, sicherer Betrieb).</p><h2>Keine Cookies, kein Tracking</h2><p>Wir setzen keine Cookies und keine Analyse- oder Werbe-Tools ein. Schriftarten werden vom System geladen, es werden keine externen Ressourcen eingebunden.</p><h2>Externe Links</h2><p>Beim Klick auf Links zu Drittseiten gelten deren Datenschutzbestimmungen.</p><h2>Ihre Rechte</h2><p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch sowie auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde. Kontakt: philipp.l.paulik@gmail.com</p></article>''')
urls+= [BASE+'/impressum/',BASE+'/datenschutz/']
open(OUT+'/favicon.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#0d9488"/><path d="M8 22V10l8 8 8-8v12" fill="none" stroke="#fff" stroke-width="3"/></svg>')
open(OUT+'/robots.txt','w').write('User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\nSitemap: %s/news-sitemap.xml\n'%(BASE,BASE))
open(OUT+'/CNAME','w').write('intelligenz-welt.de\n')
open(OUT+'/.nojekyll','w').write('')
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>%s</loc><lastmod>%s</lastmod></url>'%(u,NOW.strftime('%Y-%m-%d')) for u in urls)+'</urlset>')
# news sitemap: only own articles within 2 days (none) -> empty valid
open(OUT+'/news-sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"></urlset>')
rss=''.join('<item><title>%s</title><link>%s</link><guid>%s</guid><description>%s</description><pubDate>%s</pubDate><source url="%s">%s</source></item>'%(esc(i['title']),esc(i['url']),esc(i['url']),esc(i['sum']),email.utils.format_datetime(datetime.datetime.fromtimestamp(i['ts']).astimezone()),esc(i['url']),esc(i['src'])) for i in ai[:60] if i['ts'])
open(OUT+'/feed.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Intelligenz Welt</title><link>%s</link><description>KI- und LLM-News</description><language>de</language>%s</channel></rss>'%(BASE,rss))
json.dump(ai[:300],open(OUT+'/news.json','w'),ensure_ascii=False)
# Stable, noindex source-info pages, deliberately not appended to urls/sitemaps/RSS.
write_css(OUT)
page('/news/quellenarchiv/','Gesicherte KI-Meldungen | Intelligenz Welt','Dauerhaft gespeicherte Quelleninfos aus erlaubten RSS-Feeds.',licensed_archive_body(licensed,'Intelligenz Welt'),act='/news/')
licensed_noindex(OUT+'/news/quellenarchiv/index.html')
_p=__import__('pathlib').Path(OUT+'/news/index.html')
_p.write_text(_p.read_text().replace('<h1>KI-News</h1>','<h1>KI-News</h1><p><a href="/news/quellenarchiv/">Alle gesicherten heise-Quelleninfos →</a></p>',1))
for item in licensed:
    path=licensed_path(item)
    page(path,item['title']+' | Quelleninfo | Intelligenz Welt','Externe KI-Meldung mit RSS-Anrisstext und Original-Link.',licensed_body(item,'Intelligenz Welt','/news/quellenarchiv/'),act='/news/')
    licensed_noindex(OUT+path+'index.html')
print('IW pages',len(urls))
# editorial articles (content/articles/*.json): rendered by tools/articles.py, see docs/EDITORIAL.md
import subprocess,sys
subprocess.check_call([sys.executable,'../tools/articles.py',OUT])
subprocess.check_call([sys.executable,'../tools/search.py',OUT])

# Curated versioned portraits, after editorial pages and the local search index.
subprocess.check_call([sys.executable,'../tools/portraits.py','iw',OUT])

# Final isolated pass: advertising, consent and activation gates (no third-party code by default).
subprocess.check_call([sys.executable,'../tools/monetization.py',OUT])

# Footer redesign: brand block + link columns (after monetization, which injects the consent button).
subprocess.check_call([sys.executable,'../tools/footer.py',OUT])

# Removed Analysen area: GitHub Pages has no server redirects or 410, so each old URL is a small
# meta-refresh stub (canonical + noindex) pointing at the article overview. Not in sitemap/search/nav.
for _p in ['/analysen/']+['/artikel/%s/'%x for x in ('kimi-k25-agentic-swarm-revolution','seedance-2-ki-video-revolution','openclaw-chaos-sicherheit-ki','claude-4-6-opus-analyse')]:
    os.makedirs(OUT+_p,exist_ok=True)
    open(OUT+_p+'index.html','w',encoding='utf-8').write('<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Seite verschoben | Intelligenz Welt</title><meta name="robots" content="noindex,follow"><link rel="canonical" href="%s/artikel/"><meta http-equiv="refresh" content="0; url=/artikel/"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><p>Diese Seite gibt es nicht mehr. Weiter zu den <a href="/artikel/">Artikeln</a>.</p></body></html>'%BASE)

# Expanded About page (replaces the short /ueber-uns/ body); keep after monetization so the final shell is reused.
subprocess.check_call([sys.executable,'../tools/about.py',OUT])

subprocess.check_call([sys.executable,'../tools/share_iconify.py',OUT])

# Static in-article daily-report CTA, after all article renderers and consent passes.
subprocess.check_call([sys.executable,'../tools/report_breaker.py',OUT])

# KI-Pulse ticker under the header (build-time data, local icons, no runtime requests).
subprocess.check_call([sys.executable,'../tools/ticker.py',OUT])
