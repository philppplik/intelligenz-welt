/* Rich-Consent QA: jede HTTPS-Anfrage wird abgefangen, nie an Google gesendet.
   NODE_PATH=... node tools/monetization/test-ga4.cjs  (IW_OUT=/tmp/iwout fuer Fixture) */
const {chromium}=require('playwright'),http=require('http'),fs=require('fs'),path=require('path'),assert=require('assert');
const root=process.env.IW_OUT||path.resolve(__dirname,'../../site/out'),shots=process.env.SCREENSHOT_DIR||'/tmp/iw-ga4-screenshots';fs.mkdirSync(shots,{recursive:true});
const server=http.createServer((req,res)=>{let f=path.join(root,decodeURI(req.url.split('?')[0]));if(f.endsWith('/'))f+='index.html';try{res.setHeader('Content-Type',f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.svg')?'image/svg+xml':'text/html');res.end(fs.readFileSync(f));}catch(e){res.statusCode=404;res.end('missing')}});
const MID=process.env.GA4_EXPECTED_ID||'G-E1XCJME97G';
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));let base='http://127.0.0.1:'+server.address().port;let browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});let n=0;function ok(t,m){assert(t,m);n++}
async function ctx0(w){let c=await browser.newContext({viewport:{width:w,height:900}}),remote=[];await c.route('https://**/*',r=>{remote.push(r.request().url());return r.fulfill({contentType:'application/javascript',body:'/* mock */'});});return{c,remote}}
try{
for(const width of [1440,390]){
  let {c,remote}=await ctx0(width),p=await c.newPage();
  await p.goto(base+'/cookies/?q=private-email@example.test');ok(remote.length===0,'no remote pre-consent');
  ok(!(await p.locator('#iw-statistics').isDisabled()),'statistics selectable');ok(await p.locator('#iw-advertising').isDisabled(),'advertising locked');
  await p.screenshot({path:path.join(shots,'iw-ga4-fixture-'+width+'.png')});
  await p.locator('[data-consent="reject"]').click();await p.reload();ok(remote.length===0,'reject stays tag-free');
  await p.locator('[data-iw-consent-open]').click();await p.locator('#iw-statistics').check();await p.locator('[data-consent="save"]').click();
  await p.waitForFunction(()=>document.querySelector('script[src*="googletagmanager"]'));
  ok(remote.length===1&&remote[0].includes(MID),'exactly one gtag load with property id');
  let q=await p.evaluate(()=>dataLayer.map(x=>Array.from(x)));
  let conf=q.find(x=>x[0]==='config')[2],view=q.find(x=>x[0]==='event'&&x[1]==='page_view')[2];
  ok(conf.cookie_expires===15552000&&conf.cookie_update===false,'180d fixed cookies');ok(conf.allow_google_signals===false&&conf.allow_ad_personalization_signals===false,'no signals/ads');
  ok(conf.cookie_domain==='127.0.0.1','host-only cookie domain');ok(conf.send_page_view===false,'manual page_view');
  ok(q[0][0]==='consent'&&q[0][2].analytics_storage==='denied','default denied');ok(q[1][2].analytics_storage==='granted','granted after consent');
  ok(view.content_group==='rechtliches','content_group cookies page');ok(!view.page_location.includes('?'),'query stripped (no allowlisted utm)');
  ok(view.page_referrer==='','no referrer without consent-cleaning source');
  // utm allowlist: newsletter/email bleiben, campaign + fremde Parameter nicht
  await p.goto(base+'/news/?utm_source=newsletter&utm_medium=email&utm_campaign=nicht-freigegeben&q=geheim');
  let v2=await p.evaluate(()=>dataLayer.filter(x=>x[0]==='event'&&x[1]==='page_view').map(x=>Array.from(x)[2]).pop());
  ok(v2.content_group==='news','content_group news');ok(v2.page_location.includes('utm_source=newsletter'),'allowlisted utm_source kept');
  ok(v2.page_location.includes('utm_medium=email'),'allowlisted utm_medium kept');
  ok(!v2.page_location.includes('nicht-freigegeben')&&!v2.page_location.includes('geheim'),'campaign+q dropped');
  // content groups
  for(const [route,grp] of [['/','startseite'],['/artikel/test-artikel/','artikel'],['/modelle/','ki-modelle'],['/suche/','suche']]){
    await p.goto(base+route);let v=await p.evaluate(()=>dataLayer.filter(x=>x[0]==='event'&&x[1]==='page_view').map(x=>Array.from(x)[2]).pop());ok(v.content_group===grp,'content_group '+route);
  }
  // scroll depth
  await p.goto(base+'/artikel/test-artikel/');await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));await p.waitForTimeout(600);
  ok(await p.evaluate(()=>dataLayer.some(x=>x[0]==='event'&&x[1]==='scroll_percent')),'scroll_percent fired');
  // widerruf
  let loadsBefore=remote.filter(u=>u.includes('googletagmanager')).length;ok(loadsBefore>0,'tag loaded while consent given');
  await p.evaluate(()=>document.cookie='_ga=localtest;path=/');await p.locator('[data-iw-consent-open]').click();await p.locator('[data-consent="reject"]').click();
  await p.waitForFunction(()=>!window.dataLayer);await p.reload();await p.waitForTimeout(300);
  ok(remote.filter(u=>u.includes('googletagmanager')).length===loadsBefore,'no new load after withdrawal');ok(!(await c.cookies()).some(x=>x.name==='_ga'),'_ga removed');
  ok((await p.evaluate(()=>JSON.parse(localStorage.getItem('iw-consent-v1')))).statistics===false,'withdrawal stored');
  // rechttexte
  await p.goto(base+'/datenschutz/');let ds=await p.locator('article').textContent();
  ok((await p.locator('#iw-ga4-heading').textContent()).includes('Statistik mit Einwilligung'),'ga4 section active');
  ok(ds.includes('14 Monate'),'retention disclosed');ok(ds.includes('keine Konto-Registrierung'),'registration wording fixed');
  ok(!ds.includes('keine Analyse- oder Werbedienste'),'no contradiction left');
  await p.goto(base+'/cookies/');let ck=await p.locator('article').textContent();
  ok(ck.includes('Statistik: nur mit Einwilligung'),'cookies heading');ok(ck.includes('_ga'),'ga cookies listed');
  await c.close();
}
// excluded token route: komplett tag-frei auch nach Einwilligung
let {c:c2,remote:r2}=await ctx0(1440),p2=await c2.newPage();
await p2.goto(base+'/');await p2.locator('[data-consent="all"]').click();await p2.waitForFunction(()=>document.querySelector('script[src*="googletagmanager"]'));
await p2.goto(base+'/tagesbericht-bestaetigt/');await p2.waitForTimeout(400);
ok(r2.filter(u=>u.includes('googletagmanager')).length===1,'excluded route loads no new tag');
let cfgSeen=await p2.evaluate(()=>Array.from(document.querySelectorAll('script[src*="googletagmanager"]')).length);
ok(cfgSeen===0,'no gtag script on excluded route');
await c2.close();
console.log(n+' rich GA4 assertions passed; every Google request intercepted, none sent.')}finally{await browser.close();server.close()}})().catch(e=>{console.error(e);server.close();process.exitCode=1});
