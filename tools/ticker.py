"""KI-Pulse ticker under the header of every page. Build-time only: headlines from
data/ai_archive.json, source icons from site/source-icons (copied to /assets/source-icons/).
No runtime requests, no tracking, no dependencies. Usage: ticker.py <out>"""
import hashlib, html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = 16
CSS = '''
.iwt{display:flex;align-items:center;height:40px;background:#f1f5f9;border-bottom:1px solid #e2e8f0;font-size:13px;line-height:1;overflow:hidden}
.iwt-in{display:flex;align-items:center;gap:10px;width:100%;max-width:1180px;margin:0 auto;padding:0 20px;min-width:0}
.iwt-lab{flex:none;font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#093A6A;background:#e3effb;padding:5px 9px;border-radius:99px}
.iwt-vp{flex:1;min-width:0;overflow:hidden;-webkit-mask-image:linear-gradient(90deg,transparent,#000 24px,#000 calc(100% - 24px),transparent);mask-image:linear-gradient(90deg,transparent,#000 24px,#000 calc(100% - 24px),transparent)}
.iwt-track{display:flex;width:max-content;margin:0;padding:0;list-style:none;animation:iwt-run var(--iwt-dur,90s) linear infinite}
.iwt-vp:hover .iwt-track,.iwt-vp:focus-within .iwt-track,.iwt.is-paused .iwt-track{animation-play-state:paused}
.iwt-track li{flex:none;margin-right:34px}
.iwt-track a{display:inline-flex;align-items:center;gap:8px;color:#0f172a;font-weight:500;white-space:nowrap;padding:10px 0}
.iwt-track a:hover{color:#1d6bc0}
.iwt-track a:focus-visible,.iwt-btn:focus-visible{outline:2px solid #1d6bc0;outline-offset:2px;border-radius:4px}
.iwt-track img,.iwt-track .iwt-mono{flex:none;width:18px;height:18px;border-radius:4px;background:#fff;object-fit:contain}
.iwt-mono{display:inline-flex;align-items:center;justify-content:center;font-size:9px;font-weight:800;color:hsl(var(--h) 55% 28%);background:hsl(var(--h) 70% 92%)!important}
.iwt-btn{flex:none;width:28px;height:28px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#64748b;cursor:pointer;padding:0;display:inline-flex;align-items:center;justify-content:center}
.iwt-btn:hover{color:#1d6bc0;border-color:#1d6bc0}
.iwt-btn svg{display:block}.iwt-btn .i-play{display:none}.iwt.is-paused .i-play{display:block}.iwt.is-paused .i-pause{display:none}
@keyframes iwt-run{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(max-width:800px){.iwt-in{padding:0 12px;gap:8px}.iwt-lab{font-size:10px;padding:4px 7px}}
@media(prefers-reduced-motion:reduce){.iwt-vp{overflow-x:auto;-webkit-mask-image:none;mask-image:none}.iwt-track{animation:none}.iwt-dup,.iwt-btn{display:none!important}}
'''
JS = ("(function(){var t=document.querySelector('.iwt');if(!t)return;var b=t.querySelector('.iwt-btn');if(!b)return;"
      "if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)return;b.hidden=false;"
      "b.addEventListener('click',function(){var p=t.classList.toggle('is-paused');b.setAttribute('aria-pressed',p?'true':'false');"
      "b.setAttribute('aria-label',p?'Ticker fortsetzen':'Ticker anhalten')})})();")

def slug(n): return re.sub(r'[^a-z0-9]+', '-', (n or '').lower()).strip('-')

def mark(src, out):
    s = slug(src)
    if s and (out / 'assets' / 'source-icons' / (s + '.png')).is_file():
        return '<img src="/assets/source-icons/%s.png" width="18" height="18" alt="" decoding="async">' % s
    w = [x for x in (src or '').split() if x]
    hue = int(hashlib.sha256(s.encode()).hexdigest()[:4], 16) % 360
    return '<span class="iwt-mono" style="--h:%d" aria-hidden="true">%s</span>' % (hue, html.escape((''.join(x[0] for x in w[:2]) or '?').upper()))

def build(out):
    items = [i for i in json.load(open(ROOT / 'data' / 'ai_archive.json', encoding='utf-8'))
             if i.get('url', '').startswith('https://') and i.get('title')]
    items.sort(key=lambda i: i.get('ts', 0), reverse=True)
    items = items[:N]
    if not items: return ''
    def li(i, dup):
        t = i['title'].strip()
        t = t if len(t) <= 95 else t[:92].rstrip() + '...'
        extra = ' tabindex="-1"' if dup else ''
        return ('<li%s><a href="%s" target="_blank" rel="noopener nofollow"%s>%s<span>%s</span></a></li>'
                % (' class="iwt-dup" aria-hidden="true"' if dup else '', html.escape(i['url'], quote=True), extra,
                   mark(i.get('src'), out), html.escape(t)))
    lis = ''.join(li(i, False) for i in items) + ''.join(li(i, True) for i in items)
    btn = ('<button type="button" class="iwt-btn" aria-label="Ticker anhalten" aria-pressed="false" hidden>'
           '<svg class="i-pause" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>'
           '<svg class="i-play" viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M7 5v14l12-7z"/></svg></button>')
    return ('<div class="iwt" role="region" aria-label="KI-Pulse: aktuelle Schlagzeilen" style="--iwt-dur:%ds"><div class="iwt-in">'
            '<span class="iwt-lab">KI-Pulse</span><div class="iwt-vp" tabindex="0" aria-label="Laufende Schlagzeilen"><ul class="iwt-track">%s</ul></div>%s</div></div>'
            '<script>%s</script>') % (len(items) * 6, lis, btn, JS)

def main(out):
    out = pathlib.Path(out)
    (out / 'assets').mkdir(exist_ok=True)
    (out / 'assets' / 'ticker.css').write_text(CSS)
    frag = build(out)
    n = 0
    for f in out.rglob('*.html'):
        t = f.read_text(encoding='utf-8')
        if 'class="iwt"' in t or '</header>' not in t: continue
        t = t.replace('</header>', '</header>' + frag, 1)
        t = t.replace('</head>', '<link rel="stylesheet" href="/assets/ticker.css"></head>', 1)
        f.write_text(t, encoding='utf-8'); n += 1
    print('IW ticker: %d pages' % n)

if __name__ == '__main__': main(sys.argv[1])
