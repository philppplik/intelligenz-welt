#!/usr/bin/env python3
"""Exit-hint dialog promoting the free daily PDF edition (Tagesausgabe).

No tracking, no cookies, no data collection: the only storage is a
sessionStorage flag so the dialog appears at most once per browser session
(disclosed in Datenschutz and Cookies & Einstellungen). Desktop trigger:
mouse leaves the window toward the top. Mobile has no real exit intent, so
the honest fallback is a fast scroll-up after reading deep into the page
(address-bar gesture). Never fires in the first seconds, never while the
burger menu, the consent panel or another modal is open, and closes via X,
Escape or backdrop tap.

Final idempotent static postprocessor, like footer.py. Usage:
    exit_intent.py OUT
"""
import pathlib, sys

ARM_MS = 8000
STORAGE_KEY = "iw-exit-report"
REPORT_PDF = "/tagesbericht-anmelden/"
REPORT_PAGE = "/berichte/"
# Lead-Wall pages: the dialog would advertise the report on its own signup flow.
NO_DIALOG = ("/tagesbericht-anmelden/", "/tagesbericht-bestaetigt/", "/abmelden/")

SNIPPET = '''<style>
.iw-exit{position:fixed;inset:0;z-index:80;display:flex;align-items:flex-end;justify-content:center;padding:16px;background:rgba(15,23,42,.45)}
.iw-exit[hidden]{display:none}
.iw-exit .dlg{background:var(--bg,#fff);color:var(--fg,#0f172a);border:1px solid var(--line,#e2e8f0);border-radius:16px;box-shadow:0 18px 60px rgba(9,58,106,.25);max-width:430px;width:100%;padding:22px 22px 16px;position:relative}
@media(min-width:640px){.iw-exit{align-items:center}}
.iw-exit h2{margin:0 36px 8px 0;font-size:19px;letter-spacing:-.01em;color:var(--fg,#0f172a)}
.iw-exit .txt{margin:0 0 14px;font-size:13.5px;color:var(--mut,#64748b);line-height:1.55}
.iw-exit .row{display:flex;flex-direction:column;gap:9px}
@media(min-width:420px){.iw-exit .row{flex-direction:row;align-items:center}.iw-exit a.arc{padding:6px 4px}}
.iw-exit a.go{background:var(--ac,#1d6bc0);color:#fff;padding:10px 16px;border-radius:8px;font-weight:700;font-size:14px;text-align:center;box-shadow:0 1px 2px rgba(9,58,106,.3);transition:filter .15s ease}
.iw-exit a.go:hover{color:#fff;filter:brightness(1.08)}
.iw-exit a.arc{color:var(--ac,#1d6bc0);font-weight:600;font-size:14px;text-align:center;padding:6px 0}
.iw-exit a.arc:hover{text-decoration:underline;text-underline-offset:3px}
.iw-exit .x{position:absolute;top:10px;right:10px;width:34px;height:34px;border:1px solid var(--line,#e2e8f0);background:none;color:var(--mut,#64748b);border-radius:8px;font-size:16px;line-height:1;cursor:pointer;display:grid;place-items:center}
.iw-exit .x:hover{background:var(--soft,#f1f5f9);color:var(--fg,#0f172a)}
.iw-exit .no{display:block;margin:12px auto 0;background:none;border:0;color:var(--mut,#64748b);font-size:12.5px;cursor:pointer;padding:4px 8px}
.iw-exit .no:hover{color:var(--fg,#0f172a);text-decoration:underline;text-underline-offset:3px}
.iw-exit .fine{margin:12px 0 0;font-size:11.5px;color:var(--mut,#64748b)}
.iw-exit :focus-visible{outline:3px solid var(--ac,#1d6bc0);outline-offset:2px}
@media(prefers-reduced-motion:no-preference){.iw-exit .dlg{animation:iwex .22s ease}@keyframes iwex{from{transform:translateY(10px);opacity:0}}}
</style>
<div class="iw-exit" id="iw-exit" hidden>
<div class="dlg" role="dialog" aria-modal="true" aria-labelledby="iw-exit-t">
<button type="button" class="x" data-x aria-label="Hinweis schlie&szlig;en">&times;</button>
<h2 id="iw-exit-t">Geh noch nicht!</h2>
<p class="txt">Sichere dir noch schnell gratis die Tagesausgabe: die wichtigsten KI-News, Artikel und das Modell-Radar des Tages kompakt als PDF &ndash; kostenlos mit kurzer E-Mail-Anmeldung (Double-Opt-In), ohne Newsletter.</p>
<div class="row"><a class="go" href="__PDF__">Gratis-Tagesausgabe sichern (PDF)</a><a class="arc" href="__PAGE__">Alle Ausgaben ansehen</a></div>
<button type="button" class="no" data-x>Nein, danke</button>
<p class="fine">Kein Newsletter &ndash; nur eine Best&auml;tigungsmail. Dieser Hinweis erscheint h&ouml;chstens einmal pro Browsersitzung.</p>
</div>
</div>
<script>(function(){
var el=document.getElementById("iw-exit");if(!el)return;
var ARM=__ARM__,armed=false,shown=false,lastFocus=null;
try{if(sessionStorage.getItem("__KEY__"))shown=true}catch(e){}
setTimeout(function(){armed=true},ARM);
function blocked(){if(shown||!armed||!el.hidden)return true;
var mn=document.getElementById("menu");if(mn&&mn.classList.contains("open"))return true;
var cs=document.getElementById("iw-consent");if(cs&&!cs.hidden)return true;
return !!document.querySelector("body>[aria-modal=true]")}
function show(){if(blocked())return;shown=true;try{sessionStorage.setItem("__KEY__","1")}catch(e){}
lastFocus=document.activeElement;el.hidden=false;var b=el.querySelector("a.go");if(b)b.focus()}
function hide(){if(el.hidden)return;el.hidden=true;if(lastFocus&&lastFocus.focus)lastFocus.focus()}
document.addEventListener("mouseout",function(e){if(!e.relatedTarget&&e.clientY<=8)show()});
if(window.matchMedia&&matchMedia("(pointer:coarse)").matches){
var deep=0,lastY=window.scrollY,lastT=0;
addEventListener("scroll",function(){var y=window.scrollY,t=Date.now();
if(y>deep)deep=y;
if(deep>=500&&lastY-y>140&&t-lastT<300&&y<deep-300)show();
lastY=y;lastT=t},{passive:true})}
el.addEventListener("click",function(e){if(e.target===el||e.target.hasAttribute("data-x"))hide()});
document.addEventListener("keydown",function(e){if(el.hidden)return;
if(e.key==="Escape"){hide();return}
if(e.key!=="Tab")return;
var f=el.querySelectorAll("a[href],button"),first=f[0],last=f[f.length-1];
if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}
else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}});
})()</script>'''.replace('__ARM__', str(ARM_MS)).replace('__KEY__', STORAGE_KEY).replace('__PDF__', REPORT_PDF).replace('__PAGE__', REPORT_PAGE)

MARKER = 'id="iw-exit"'


def attach(html, path):
    """Inject the dialog before </body> on every page except the reports page itself."""
    if path == REPORT_PAGE or path in NO_DIALOG or MARKER in html or '</body>' not in html:
        return html
    return html.replace('</body>', SNIPPET + '</body>', 1)


def main(out):
    out = pathlib.Path(out)
    n = 0
    for f in sorted(out.rglob('*.html')):
        rel = '/' + f.relative_to(out).as_posix()
        path = rel[:-len('index.html')] if rel.endswith('index.html') else rel
        t = f.read_text(encoding='utf-8')
        # Meta-refresh stubs (removed areas) redirect instantly; no dialog there.
        if 'http-equiv="refresh"' in t:
            continue
        new = attach(t, path)
        if new != t:
            f.write_text(new, encoding='utf-8'); n += 1
    print('IW exit hint: %d pages' % n)


if __name__ == '__main__':
    main(sys.argv[1])
