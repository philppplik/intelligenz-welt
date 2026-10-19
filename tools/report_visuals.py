"""Visual blocks for the Intelligenz Welt PDF and the KI-News / Modell-Radar pages.
Own inline SVG/CSS from real data (data/ai_archive.json headlines, data/models.json Hugging Face counters).
Logos only from content/portrait-logos/manifest.json, SHA256-verified, monogram fallback. Stdlib only, no network."""
import base64, collections, datetime, hashlib, json, math, os, re
from report_core import esc, lnk

AC, DK = '#1d6bc0', '#093A6A'
PALETTE = ['#1d6bc0', '#12a594', '#e08a1e', '#7040cd', '#d1457a', '#2fa4d9', '#6b7080', '#5b8c2a']
TASKS = {'text-generation': 'Textgenerierung', 'image-text-to-text': 'Bild+Text zu Text', 'any-to-any': 'Multimodal', 'text-to-image': 'Text zu Bild',
         'text-to-speech': 'Sprachsynthese', 'automatic-speech-recognition': 'Spracherkennung', 'image-to-image': 'Bild zu Bild', 'text-to-video': 'Text zu Video',
         'image-to-text': 'Bild zu Text', 'feature-extraction': 'Embeddings', 'image-to-video': 'Bild zu Video', 'mask-generation': 'Masken-Generierung',
         'text-ranking': 'Ranking', 'robotics': 'Robotik', 'unknown': 'Ohne Angabe'}
de = lambda v: '{:,}'.format(int(round(v))).replace(',', '.')

def short(n):
    n = float(n)
    if n >= 1e6: return ('%.1f' % (n / 1e6)).replace('.', ',') + ' Mio.'
    if n >= 1e3: return ('%.1f' % (n / 1e3)).replace('.', ',') + ' Tsd.'
    return str(int(n))

def task_label(t): return TASKS.get(t or 'unknown', t or 'Ohne Angabe')
def org(m): return m['id'].split('/')[0] if '/' in m['id'] else '–'
def name(m): return m['id'].split('/', 1)[-1]

# --- Logos: only manifest assets, hash-verified. Company logos only mark companies, never models. ---
LOGOS, USED = {}, set()
HF_ORG_LOGO = {'nvidia': 'nvidia', 'mistralai': 'mistral-ai', 'openai': 'openai', 'anthropic': 'anthropic'}  # unambiguous orgs only
DARK = {'nvidia'}

def load_logos(root):
    LOGOS.clear(); USED.clear()
    d = os.path.join(root, 'content', 'portrait-logos')
    try: man = json.load(open(os.path.join(d, 'manifest.json'), encoding='utf-8'))
    except (OSError, ValueError): return
    for k, e in man.items():
        try: raw = open(os.path.join(d, e['file']), 'rb').read()
        except (OSError, KeyError): continue
        if hashlib.sha256(raw).hexdigest() != e.get('sha256'): continue
        mime = 'image/svg+xml' if e['file'].endswith('.svg') else 'image/png'
        LOGOS[k] = {'uri': 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode()), 'source': e.get('source', ''), 'license': e.get('license', '')}

def logo_box(key, w, h, u='mm'):
    L = LOGOS.get(key)
    if not L: return ''
    USED.add(key)
    return '<span class="lgbox%s" style="width:%s%s;height:%s%s"><img src="%s" alt=""></span>' % (' dk' if key in DARK else '', w, u, h, u, L['uri'])

def monogram(text, size=22, color=AC):
    t = ''.join(c for c in text if c.isalnum())[:2].upper() or '?'
    return '<span class="mono" style="width:%dpx;height:%dpx;font-size:%.1fpt;background:%s1a;color:%s;border-color:%s55">%s</span>' % (size, size, size / 3.1, color, color, color, esc(t))

def badge(key, label, color, w=13, h=6, u='mm'):
    inner = logo_box(key, w, h, u) if key in LOGOS else monogram(label, 20, color)
    return '<span class="slot">%s</span>' % inner

# --- Topics: company/product keywords counted in headline titles (not summaries). ---
TOPICS = [('OpenAI', 'openai', r'openai|chatgpt|\bgpt[-\s]?\d|sora\b'), ('Anthropic', 'anthropic', r'anthropic|\bclaude'),
          ('Google', None, r'google|gemini|deepmind|gemma'), ('Meta', 'meta', r'\bmeta\b|llama|zuckerberg'), ('Nvidia', 'nvidia', r'nvidia|\brtx\b|cuda'),
          ('Microsoft', None, r'microsoft|copilot|azure'), ('Apple', None, r'\bapple\b|\bsiri\b|iphone'), ('DeepSeek', None, r'deepseek'),
          ('Mistral', 'mistral-ai', r'mistral'), ('xAI / Grok', None, r'\bxai\b|grok|\bmusk')]

def ts_of(i): return datetime.datetime.fromtimestamp(i['ts'], datetime.timezone.utc)

def kpis(ai, models, now):
    t = now.timestamp(); d1 = sum(1 for i in ai if t - i['ts'] <= 86400); d7 = sum(1 for i in ai if t - i['ts'] <= 7 * 86400)
    p7 = sum(1 for i in ai if 7 * 86400 < t - i['ts'] <= 14 * 86400)
    delta = ('%+d%% zur Vorwoche' % round(100.0 * (d7 - p7) / p7)) if p7 else 'Vorwoche ohne Vergleich'
    dl = sum(m.get('dl') or 0 for m in models)
    cards = [('Meldungen 24 Std.', str(d1), 'Schlagzeilen aus %d Quellen' % len({i['src'] for i in ai})), ('Meldungen 7 Tage', str(d7), delta),
             ('Im Archiv', de(len(ai)), 'nur Überschriften mit Quelle'), ('Modelle im Radar', str(len(models)), 'Downloads: %s (API-Zähler)' % short(dl))]
    return '<div class="kp">%s</div>' % ''.join('<div class="k"><div class="n">%s</div><div class="v">%s</div><div class="s">%s</div></div>' % (esc(a), esc(b), esc(c)) for a, b, c in cards)

def per_day(ai, now, days=14, w=560, h=150):
    tz = now.tzinfo; today = now.date(); cnt = collections.Counter(datetime.datetime.fromtimestamp(i['ts'], tz).date() for i in ai)
    ds = [today - datetime.timedelta(days=k) for k in range(days - 1, -1, -1)]
    vals = [cnt.get(d, 0) for d in ds]; mx = max(vals) or 1
    if not any(vals): return ''
    bw = (w - 30) / days; g = ''
    for k in range(3):
        y = h - 24 - (h - 40) * k / 2
        g += '<line x1="26" y1="%.1f" x2="%d" y2="%.1f" stroke="#e3e8f0"/><text x="22" y="%.1f" font-size="6.5" text-anchor="end" fill="#64748b">%d</text>' % (y, w - 4, y, y + 2, round(mx * k / 2))
    for k, (d, v) in enumerate(zip(ds, vals)):
        x = 30 + k * bw; bh = (h - 40) * v / mx; wk = d.weekday() >= 5
        g += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s"><title>%s: %d</title></rect>' % (x + 1.5, h - 24 - bh, bw - 3, bh, '#8db6e6' if wk else AC, d.strftime('%d.%m.'), v)
        if v: g += '<text x="%.1f" y="%.1f" font-size="6.5" text-anchor="middle" fill="%s" font-weight="700">%d</text>' % (x + bw / 2, h - 27 - bh, DK, v)
        if k % 2 == (days - 1) % 2: g += '<text x="%.1f" y="%d" font-size="6.5" text-anchor="middle" fill="#64748b">%s</text>' % (x + bw / 2, h - 12, d.strftime('%d.%m.'))
    return '<svg class="chart" viewBox="0 0 %d %d" width="100%%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif" role="img" aria-label="Meldungen pro Tag, letzte %d Tage">%s</svg><div class="cap">Hellblau: Wochenende</div>' % (w, h, days, g)

def donut(counts, size=120, centre='Quellen', total_label=None):
    total = sum(counts.values())
    if not total: return ''
    items = counts.most_common(7); rest = total - sum(v for _, v in items)
    if rest: items.append(('__rest', rest))
    r, c, sw = 40, 50, 16; circ = 2 * math.pi * r; off = 0; arcs = ''; leg = ''
    for i, (k, v) in enumerate(items):
        col = PALETTE[i % len(PALETTE)] if k != '__rest' else '#c3cad6'
        ln = circ * v / total
        arcs += '<circle cx="50" cy="50" r="40" fill="none" stroke="%s" stroke-width="16" stroke-dasharray="%.2f %.2f" stroke-dashoffset="%.2f" transform="rotate(-90 50 50)"/>' % (col, ln, circ - ln, -off)
        off += ln
        leg += '<li><i style="background:%s"></i>%s <b>%d</b></li>' % (col, esc('Weitere' if k == '__rest' else k), v)
    return ('<div class="dn"><svg viewBox="0 0 100 100" width="%d" height="%d" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s"><g>%s</g><text x="50" y="52" text-anchor="middle" font-size="15" font-weight="700" fill="%s" font-family="Helvetica,Arial,sans-serif">%d</text>'
            '<text x="50" y="63" text-anchor="middle" font-size="6" fill="#64748b" font-family="Helvetica,Arial,sans-serif">%s</text></svg><ul>%s</ul></div>') % (size, size, esc(centre), arcs, DK, total, esc(centre), leg)

def source_donut(ai, now, days=14):
    c = collections.Counter(i['src'] for i in ai if now.timestamp() - i['ts'] <= days * 86400)
    return donut(c, 120, 'Meldungen')

def topic_bars(ai, now, days=7):
    t = now.timestamp(); rows = []
    for n, key, rx in TOPICS:
        r = re.compile(rx, re.I)
        cur = sum(1 for i in ai if t - i['ts'] <= days * 86400 and r.search(i['title']))
        prev = sum(1 for i in ai if days * 86400 < t - i['ts'] <= 2 * days * 86400 and r.search(i['title']))
        rows.append((n, key, cur, prev))
    rows = sorted([r for r in rows if r[2] or r[3]], key=lambda r: (-r[2], r[0]))[:8]
    if not rows: return ''
    mx = max(r[2] for r in rows) or 1; out = ''
    for i, (n, key, cur, prev) in enumerate(rows):
        d = cur - prev; arrow = ('▲ +%d' % d) if d > 0 else (('▼ %d' % d) if d < 0 else '＝ 0')
        out += '<div class="br">%s<span class="bn">%s</span><span class="bt"><i style="width:%.1f%%;background:%s"></i></span><b>%d</b><em class="%s">%s</em></div>' % (
            badge(key, n, PALETTE[i % len(PALETTE)]), esc(n), 100.0 * cur / mx, PALETTE[i % len(PALETTE)], cur, 'up' if d > 0 else 'dn2' if d < 0 else 'eq', arrow)
    return '<div class="bars">%s</div><div class="cap">Treffer in Schlagzeilen (Titel) der letzten %d Tage, Pfeil = Veränderung zu den %d Tagen davor. Stichwortzählung, keine Wertung.</div>' % (out, days, days)

def trend_bars(models, n=10):
    L = sorted(models, key=lambda m: -(m.get('likes') or 0))[:n]
    if not L: return ''
    mx = max(m.get('likes') or 0 for m in L) or 1
    rows = ''.join('<div class="br"><span class="rk">%d</span>%s<span class="bn">%s<small>%s · %s</small></span><span class="bt"><i style="width:%.1f%%"></i></span><b>%s</b></div>' % (
        i + 1, badge(HF_ORG_LOGO.get(org(m).lower()), org(m), PALETTE[i % len(PALETTE)]), lnk(m['url'], name(m)), esc(org(m)), esc(task_label(m.get('tag'))),
        100.0 * (m.get('likes') or 0) / mx, de(m.get('likes') or 0)) for i, m in enumerate(L))
    return '<div class="bars">%s</div><div class="cap">Likes auf Hugging Face (Zähler der API, kein Qualitätsmaß).</div>' % rows

def task_donut(models):
    return donut(collections.Counter(task_label(m.get('tag')) for m in models), 120, 'Modelle')

def scatter(models, w=560, h=190):
    P = [m for m in models if (m.get('likes') or 0) > 0 and (m.get('dl') or 0) > 0]
    if len(P) < 3: return ''
    lx = [math.log10(m['dl']) for m in P]; ly = [math.log10(m['likes']) for m in P]
    x0, x1 = math.floor(min(lx)), math.ceil(max(lx)); y0, y1 = math.floor(min(ly)), math.ceil(max(ly)); x1 = max(x1, x0 + 1); y1 = max(y1, y0 + 1)
    px = lambda v: 34 + (v - x0) / (x1 - x0) * (w - 44); py = lambda v: h - 22 - (v - y0) / (y1 - y0) * (h - 34)
    g = ''
    for v in range(x0, x1 + 1): g += '<line x1="%.1f" y1="8" x2="%.1f" y2="%d" stroke="#e3e8f0"/><text x="%.1f" y="%d" font-size="6.5" text-anchor="middle" fill="#64748b">%s</text>' % (px(v), px(v), h - 22, px(v), h - 11, short(10 ** v))
    for v in range(y0, y1 + 1): g += '<line x1="34" y1="%.1f" x2="%d" y2="%.1f" stroke="#e3e8f0"/><text x="30" y="%.1f" font-size="6.5" text-anchor="end" fill="#64748b">%s</text>' % (py(v), w - 10, py(v), py(v) + 2, short(10 ** v))
    top = set(id(m) for m in sorted(P, key=lambda m: -m['likes'])[:3]); dots = ''
    for m in P:
        x, y = px(math.log10(m['dl'])), py(math.log10(m['likes']))
        dots += '<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" fill-opacity=".55" stroke="%s"><title>%s</title></circle>' % (x, y, AC, DK, esc(m['id']))
        if id(m) in top: dots += '<text x="%.1f" y="%.1f" font-size="6.5" fill="%s">%s</text>' % (min(x + 5, w - 70), y - 5, DK, esc(name(m)[:18]))
    return ('<svg class="chart" viewBox="0 0 %d %d" width="100%%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif" role="img" aria-label="Likes gegen Downloads">%s%s<text x="%d" y="%d" font-size="6.5" text-anchor="middle" fill="#334155">Downloads (log)</text>'
            '<text x="36" y="6" font-size="6.5" fill="#334155">Likes (log)</text></svg>') % (w, h, g, dots, (34 + w - 10) // 2, h - 1)

def org_bars(models, n=5):
    L = collections.Counter(org(m) for m in models).most_common(n)
    if not L: return ''
    mx = L[0][1]
    return '<div class="bars sm">%s</div>' % ''.join('<div class="br">%s<span class="bn">%s</span><span class="bt"><i style="width:%.0f%%;background:%s"></i></span><b>%d</b></div>' % (
        badge(HF_ORG_LOGO.get(o.lower()), o, PALETTE[i % len(PALETTE)]), esc(o), 100.0 * v / mx, PALETTE[i % len(PALETTE)], v) for i, (o, v) in enumerate(L))

def logo_credits():
    if not USED: return ''
    li = ''.join('<li><b>%s</b>: <a href="%s">%s</a> · %s</li>' % (esc(k), esc(LOGOS[k]['source']), esc(LOGOS[k]['source']), esc(LOGOS[k]['license'])) for k in sorted(USED))
    return ('<h3>Logos und Marken</h3><p>Logos stammen aus dem lokalen Bestand von Intelligenz Welt (content/portrait-logos), unverändert und eingebettet, mit Quelle und Rechtehinweis je Datei. Marken gehören ihren Inhabern. '
            'Die Logos kennzeichnen redaktionell Unternehmen und Organisationen, sie deuten keine Partnerschaft, Freigabe oder Empfehlung an. Wo kein eindeutig zugeordnetes Logo vorliegt, steht ein Kürzel. Unternehmens- und Modelllogos werden nicht vermischt.</p><ul class="lc">%s</ul>' % li)

# Shared look (PDF in mm, page in px via .vz wrapper)
CSS_COMMON = '''
.lgbox{display:inline-flex;align-items:center;justify-content:center;background:#fff;border:1px solid #dbe3ee;border-radius:3px;padding:2px 3px;flex:none}.lgbox img{max-width:100%;max-height:100%;display:block;object-fit:contain}.lgbox.dk{background:#111827;border-color:#111827}
.slot{display:inline-flex;justify-content:center;flex:none}
.mono{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;border:1px solid;font-weight:800;flex:none;letter-spacing:-.03em}
.k .v{font-weight:800;color:#093A6A}.k{border:1px solid #cfe0f3;border-top:3px solid #1d6bc0;background:#eef5fc}
.bars .bt{flex:1;background:#e3effb;overflow:hidden}.bars .bt i{display:block;height:100%;background:linear-gradient(90deg,#1d6bc0,#2fa4d9)}
.bars em{font-style:normal;font-weight:700;font-size:.82em;white-space:nowrap}.bars em.up{color:#0f8a5f}.bars em.dn2{color:#c0392b}.bars em.eq{color:#64748b}
.dn{display:flex;align-items:center}.dn ul{list-style:none;margin:0;padding:0}.dn li{display:flex;align-items:center}.dn li i{display:inline-block;border-radius:50%;flex:none}
.cap{color:#64748b}.lc{list-style:none;padding:0}.lc li{overflow-wrap:anywhere}
'''
CSS = CSS_COMMON + '''
.kp{display:flex;gap:3mm;margin:0 0 5mm}.k{flex:1 1 0;min-width:0;border-radius:4px;padding:3mm 3.5mm}.k .n{font-size:7.6pt;color:#64748b;text-transform:uppercase;letter-spacing:.05em}.k .v{font-size:17pt;margin:1px 0}.k .s{font-size:7.8pt;color:#475569}
.lgbox{border-radius:2mm}.slot{width:13mm}
.bars .br{display:flex;align-items:center;gap:2.6mm;margin:1.1mm 0;font-size:8.8pt}.bars .rk{width:4mm;color:#64748b;font-weight:700;text-align:right}
.bars .bn{width:32mm;flex:none;min-width:0;overflow:hidden;font-weight:600;white-space:nowrap;text-overflow:ellipsis}.bars .bn a{font-weight:700;color:#14151b;text-decoration:none;display:block;overflow:hidden;text-overflow:ellipsis}.bars .bn small{display:block;color:#64748b;font-size:7.4pt;font-weight:400}
.bars .bt{height:3.2mm;border-radius:2mm;min-width:10mm}.bars b{width:13mm;text-align:right;font-variant-numeric:tabular-nums}.bars em{width:13mm}
.two{display:flex;gap:6mm}.two>div{flex:1;min-width:0}.two h3{font-size:9.5pt;margin:0 0 1.5mm;color:#093A6A}
.dn{gap:4mm}.dn ul{font-size:8.4pt}.dn li{margin:.9mm 0;gap:1.6mm}.dn li i{width:2.6mm;height:2.6mm}
.cap{font-size:7.4pt;margin:1mm 0 2mm}.chart{max-height:55mm}
.lc{font-size:7.6pt;margin:1mm 0}.lc li{margin:.6mm 0}
'''
CSS_WEB = '''
.vz{margin:8px 0 28px}.vz h3{font-size:16px;margin:22px 0 8px;letter-spacing:-.01em}.vz .two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}
.vz .kp{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0 0 8px}.vz .k{border-radius:12px;padding:14px 16px}.vz .k .n{font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:.05em}.vz .k .v{font-size:28px;margin:2px 0;letter-spacing:-.02em}.vz .k .s{font-size:13px;color:#475569}
.vz .slot{width:44px}.vz .lgbox{border-radius:6px}
.vz .bars .br{display:flex;align-items:center;gap:10px;margin:8px 0;font-size:14px}.vz .bars .rk{width:16px;color:#64748b;font-weight:700;text-align:right}
.vz .bars .bn{flex:0 0 150px;min-width:0;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.vz .bars .bn a{display:block;overflow:hidden;text-overflow:ellipsis}.vz .bars .bn small{display:block;color:#64748b;font-size:11px;font-weight:400}
.vz .bars .bt{height:10px;border-radius:5px;min-width:30px}.vz .bars b{min-width:48px;text-align:right}.vz .bars em{min-width:46px}
.vz .dn{gap:16px;flex-wrap:wrap}.vz .dn ul{font-size:13px}.vz .dn li{margin:4px 0;gap:6px}.vz .dn li i{width:10px;height:10px}
.vz .cap{font-size:12px;margin:6px 0}.vz .chart{display:block;max-width:100%;height:auto}
@media(max-width:800px){.vz .kp{grid-template-columns:repeat(2,minmax(0,1fr))}.vz .two{grid-template-columns:1fr}.vz .bars .bn{flex-basis:96px}.vz .bars .rk{display:none}.vz .k .v{font-size:24px}.vz .slot{width:36px}.vz .bars em{display:none}}
'''

def web_news(ai, models, now):
    """Visual strip for /news/ (page body, before the list)."""
    p = per_day(ai, now); d = source_donut(ai, now); t = topic_bars(ai, now)
    if not p: return ''
    return '<div class="vz">%s<h3>Meldungen pro Tag</h3>%s<div class="two"><div><h3>Wer meldet</h3>%s</div><div><h3>Themen der Woche</h3>%s</div></div>%s</div>' % (kpis(ai, models, now), p, d, t, logo_credits_web())

def web_models(ai, models, now):
    if not models: return ''
    return '<div class="vz">%s<div class="two"><div><h3>Beliebteste Modelle (Likes)</h3>%s</div><div><h3>Aufgabenbereiche</h3>%s<h3>Nach Organisation</h3>%s</div></div><h3>Likes gegen Downloads</h3>%s%s</div>' % (
        kpis(ai, models, now), trend_bars(models, 8), task_donut(models), org_bars(models), scatter(models), logo_credits_web())

def logo_credits_web():
    if not USED: return ''
    return '<p class="cap">Logos: Quellen und Rechte je Datei in <a href="https://github.com/philppplik/intelligenz-welt/blob/main/docs/PORTRAIT-LOGO-RIGHTS.md">PORTRAIT-LOGO-RIGHTS</a>. Marken gehören ihren Inhabern, keine Partnerschaft oder Empfehlung.</p>'

def pdf_overview(ai, models, now):
    return '<h2>KI-Lage in Zahlen <small>aus dem Archiv der Schlagzeilen</small></h2>%s<h3 class="h3">Meldungen pro Tag, letzte 14 Tage</h3>%s<div class="two"><div><h3 class="h3">Themen der Woche</h3>%s</div><div><h3 class="h3">Wer meldet</h3>%s</div></div>' % (
        kpis(ai, models, now), per_day(ai, now), topic_bars(ai, now), source_donut(ai, now))

def pdf_radar(models):
    if not models: return ''
    return '<h2 style="break-before:page">Modell-Radar <small>Trending auf Hugging Face · Likes und Downloads aus der öffentlichen API</small></h2><div class="two"><div><h3 class="h3">Top nach Likes</h3>%s</div><div><h3 class="h3">Aufgabenbereiche</h3>%s<h3 class="h3">Organisationen</h3>%s</div></div><h3 class="h3">Likes gegen Downloads</h3>%s' % (
        trend_bars(models, 8), task_donut(models), org_bars(models), scatter(models))
