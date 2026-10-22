"""Lead-Wall-Seiten fuer die Intelligenz-Welt-Tagesausgabe (DOI -> PDF-Gate).
Seiten: /tagesbericht-anmelden/, /tagesbericht-bestaetigt/, /abmelden/ (alle noindex).
JS: out/assets/leadwall.js (Formular-POST ans dhn-Backend, Token nur nach aktivem Klick im localStorage).
Aufruf aus build.py: from leadwall import build_leadwall; build_leadwall(page, OUT, BASE)"""

CONSENT = ('Ja, ich melde mich zum kostenlosen täglichen Tagesbericht von Intelligenz Welt als PDF an. '
 'Nach der Bestätigung meiner E-Mail-Adresse (Double-Opt-In) kann ich die aktuelle Ausgabe als PDF laden. '
 'Ein Newsletter-Abonnement ist damit nicht verbunden. Ich kann meine Einwilligung jederzeit mit Wirkung für die Zukunft widerrufen, '
 'z. B. per E-Mail an <a href="mailto:philipp.l.paulik@gmail.com">philipp.l.paulik@gmail.com</a>. '
 'Der Versand der E-Mails erfolgt über den Dienstleister Resend (PLUS FIVE FIVE, Inc., USA) als Auftragsverarbeiter; '
 'Details in der <a href="/datenschutz/#tagesbericht-anmeldung">Datenschutzerklärung</a>.')

CSS = ('<style>.lw{max-width:560px}.lw label{display:block;font-weight:600;margin:18px 0 6px}.lw input[type=email]{box-sizing:border-box;width:100%;min-height:46px;'
 'padding:10px 12px;font:inherit;border:1px solid var(--line,#cbd5e1);border-radius:8px;background:var(--bg,#fff);color:var(--fg,#0f172a)}'
 '.lw .lw-c{display:flex;gap:10px;align-items:flex-start;margin:16px 0;font-size:14px;line-height:1.55;font-weight:400}'
 '.lw .lw-c input{margin:3px 0 0;padding:0;min-height:20px;width:20px;height:20px;flex:none;accent-color:#1d6bc0}'
 '.lw button.lw-go,.lw a.lw-go{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:12px 20px;border:0;border-radius:8px;'
 'background:#1d6bc0;color:#fff;font:600 15px system-ui,sans-serif;cursor:pointer;text-decoration:none}'
 '.lw button:disabled{opacity:.6}.lw .lw-hp{position:absolute;left:-9999px;height:0;overflow:hidden}'
 '.lw .lw-msg{margin-top:16px;padding:12px 14px;border:1px solid var(--line,#cbd5e1);border-radius:8px}.lw .lw-err{border-color:#c0392b}'
 '.lw small{display:block;margin-top:14px;color:var(--mut,#64748b)}</style>')

FORM = ('<form class="lw" id="lw-form" data-ep="iwsub" method="post" novalidate><label for="lw-email">E-Mail-Adresse</label>'
 '<input id="lw-email" name="email" type="email" autocomplete="email" inputmode="email" required>'
 '<div class="lw-hp" aria-hidden="true"><label>Nicht ausfüllen<input name="website" tabindex="-1" autocomplete="off"></label></div>'
 '<label class="lw-c" for="lw-consent"><input id="lw-consent" name="consent" type="checkbox" required><span>' + CONSENT + '</span></label>'
 '<button class="lw-go" type="submit">Kostenlos anmelden</button><div class="lw-msg" id="lw-msg" hidden></div>'
 '<small>Nur die E-Mail-Adresse ist Pflicht. Kein Kauf, kein Preis. Keine Tracking-Pixel in unseren E-Mails. '
 'Anmeldezeitpunkt, Bestätigungszeitpunkt, Textversion und IP-Adresse werden als Einwilligungsnachweis gespeichert.</small></form>')

PAGES = {
 'tagesbericht-anmelden': ('Tagesausgabe gratis erhalten', 'Anmeldung zur kostenlosen Intelligenz-Welt-Tagesausgabe als PDF. Double-Opt-In, jederzeit abbestellbar.',
  '<div class="w"><article class="art"><h1>Tagesausgabe gratis erhalten</h1>'
  '<p>Trage deine E-Mail-Adresse ein. Du bekommst eine Bestätigungsmail. Erst nach dem Klick auf den Link in dieser Mail bist du angemeldet und kannst die aktuelle Tagesausgabe als PDF laden.</p>'
  + FORM + '</article></div>'),
 'tagesbericht-bestaetigt': ('Anmeldung bestätigt', 'Bestätigung der Anmeldung zur Intelligenz-Welt-Tagesausgabe.',
  '<div class="w"><article class="art"><h1 id="lw-h">Anmeldung bestätigt</h1><div class="lw" id="lw-ok" hidden>'
  '<p>Danke. Du bist angemeldet. Hier ist die aktuelle Tagesausgabe:</p><p><a class="lw-go" id="lw-dl" href="/tagesbericht-anmelden/">PDF herunterladen</a></p>'
  '<p><button class="lw-go" type="button" id="lw-keep">PDF herunterladen und auf diesem Gerät eingetragen bleiben</button></p>'
  '<small>Mit „eingetragen bleiben“ speichern wir auf diesem Gerät einen Eintrag (Anmeldestatus, 12 Monate), damit du die Anmeldung nicht erneut eintippen musst. '
  'Löschbar über die Browserdaten.</small></div>'
  '<div class="lw" id="lw-bad" hidden><p>Der Bestätigungslink ist abgelaufen oder ungültig. <a href="/tagesbericht-anmelden/">Bitte melde dich erneut an.</a></p></div></article></div>'),
 'abmelden': ('Abgemeldet', 'Abmeldung von der Intelligenz-Welt-Tagesausgabe.',
  '<div class="w"><article class="art"><h1>Abmeldung</h1><div class="lw">'
  '<p id="lw-u">Du bist abgemeldet. Die Adresse wird nach 30 Tagen gelöscht, der Einwilligungsnachweis bleibt getrennt gespeichert.</p></div></article></div>')}

JS = r'''(function(){
  // Backend-Basis optional per <meta name="iw-lw-api" content="https://..."> oder window.IW_LW_API ueberschreiben.
  var m=document.querySelector('meta[name="iw-lw-api"]'),API=(window.IW_LW_API||(m&&m.content)||'https://daily-hob-newsletter.vercel.app/lw').replace(/\/$/,'');
  var KEY='iw-lw-k',DAYS=365;
  function get(){try{var r=JSON.parse(localStorage.getItem(KEY)||'null');if(r&&r.exp>Date.now())return r.k}catch(e){}return null}
  function set(k){try{localStorage.setItem(KEY,JSON.stringify({k:k,exp:Date.now()+DAYS*864e5}))}catch(e){}}
  var path=location.pathname.replace(/\/$/,'');
  // 1) Report-Links: eingetragene Abonnenten gehen direkt zum PDF, alle anderen zur Anmeldung.
  document.querySelectorAll('a[href="/tagesbericht-anmelden/"]:not(.lw-go)').forEach(function(a){
    var k=get();a.href=(k&&API)?API+'/api/iwpdf?k='+encodeURIComponent(k):'/tagesbericht-anmelden/';
  });
  // 2) Anmeldeformular
  var f=document.getElementById('lw-form');
  if(f)f.addEventListener('submit',function(e){e.preventDefault();var msg=document.getElementById('lw-msg'),b=f.querySelector('button');
    function show(t,err){msg.hidden=false;msg.className='lw-msg'+(err?' lw-err':'');msg.textContent=t}
    var em=f.email.value.trim();
    if(!/^\S+@\S+\.\S{2,}$/.test(em))return show('Bitte gib eine gültige E-Mail-Adresse ein.',1);
    if(!f.consent.checked)return show('Bitte stimme der Anmeldung zur Tagesausgabe zu (Checkbox).',1);
    if(!API)return show('Die Anmeldung ist noch nicht freigeschaltet.',1);
    b.disabled=true;
    fetch(API+'/api/'+(f.getAttribute('data-ep')||'iwsub'),{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:em,consent:true,website:f.website.value})})
      .then(function(r){return r.json()}).then(function(j){b.disabled=false;
        if(j.ok)show('Fast geschafft: Wir haben dir eine Bestätigungsmail geschickt. Bitte klicke auf den Link darin (auch im Spam-Ordner nachsehen).');
        else show('Das hat nicht geklappt. Bitte prüfe die Eingaben.',1)})
      .catch(function(){b.disabled=false;show('Verbindungsfehler. Bitte versuche es später erneut.',1)});
  });
  // 3) Bestaetigungsseite: Token kommt im URL-Fragment; nur ein aktiver Klick speichert ihn (Option B).
  if(path==='/tagesbericht-bestaetigt'){
    var h=/[#&]k=([^&]+)/.exec(location.hash),ok=document.getElementById('lw-ok'),bad=document.getElementById('lw-bad');
    if(h&&API){var k=decodeURIComponent(h[1]);history.replaceState(null,'',location.pathname);ok.hidden=false;
      var dl=document.getElementById('lw-dl');dl.href=API+'/api/iwpdf?k='+encodeURIComponent(k);
      document.getElementById('lw-keep').addEventListener('click',function(){set(k);location.href=dl.href});
    }else bad.hidden=false;
  }
})();'''

def build_leadwall(page, OUT, BASE):
    import os, re
    for slug, (title, desc, body) in PAGES.items():
        page('/%s/' % slug, '%s | Intelligenz Welt' % title, desc, CSS + body)
        p = os.path.join(OUT, slug, 'index.html')
        h = open(p, encoding='utf-8').read()
        h = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,follow">', h, count=1)
        h = h.replace('</body>', '<script src="/assets/leadwall.js" defer></script></body>', 1)
        open(p, 'w', encoding='utf-8').write(h)
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    open(os.path.join(OUT, 'assets', 'leadwall.js'), 'w', encoding='utf-8').write(JS)
    print('leadwall pages:', ', '.join(PAGES))
