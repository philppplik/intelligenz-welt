const { chromium } = require('playwright');
const http = require('http'),fs=require('fs'),path=require('path'),assert=require('assert');
const root=process.env.IW_OUT||path.resolve(__dirname,'../../site/out');
const screenshotDir=process.env.SCREENSHOT_DIR||'/tmp/iw-monetization-screenshots';fs.mkdirSync(screenshotDir,{recursive:true});
const server=http.createServer((req,res)=>{let file=path.join(root,decodeURI(req.url.split('?')[0]));if(file.endsWith('/'))file+='index.html';try{res.setHeader('Content-Type',file.endsWith('.css')?'text/css':file.endsWith('.js')?'text/javascript':file.endsWith('.svg')?'image/svg+xml':file.endsWith('.png')?'image/png':'text/html');res.end(fs.readFileSync(file));}catch(e){res.statusCode=404;res.end('missing')}});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));let base='http://127.0.0.1:'+server.address().port;const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});let count=0;function ok(test){assert(test);count++}
try {
for(const [name,width,height] of [['desktop',1440,1100],['mobile',390,844],['narrow',320,760]]){
const context=await browser.newContext({viewport:{width,height}});await context.route('https://**/*',r=>r.fulfill({contentType:'application/javascript',body:'/* mock: kein echter Google-Traffic */'}));const page=await context.newPage(),requests=[];page.on('request',r=>requests.push(r.url()));
await page.goto(base+'/werben/');await page.waitForSelector('#iw-consent:not([hidden])');
ok(!(await page.locator('#iw-statistics').isDisabled()));ok(await page.locator('#iw-advertising').isDisabled());ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
if(name!=='narrow')await page.screenshot({path:path.join(screenshotDir,'iw-consent-'+name+'.png'),fullPage:false});
ok(await page.locator('#iw-consent [data-consent="close"]').count()===0);await page.keyboard.press('Escape');ok(await page.locator('#iw-consent').isVisible());ok(await page.evaluate(()=>localStorage.getItem('iw-consent-v1')===null));await page.locator('[data-consent="reject"]').click();ok(await page.locator('#iw-consent').isHidden());
let saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('iw-consent-v1')));ok(saved.statistics===false&&saved.advertising===false);
await page.reload();ok(await page.locator('#iw-consent').isHidden());ok(await page.evaluate(()=>document.cookie.includes('iw_consent_v1=')));await page.evaluate(()=>localStorage.clear());await page.reload();ok(await page.locator('#iw-consent').isHidden());await page.goto(base+'/');ok(await page.locator('#iw-consent').isHidden());await page.goto(base+'/werben/');
if(name!=='narrow')await page.screenshot({path:path.join(screenshotDir,'iw-werben-'+name+'.png'),fullPage:true});
await page.locator('[data-iw-consent-open]').click();ok(await page.locator('#iw-consent').isVisible());await page.locator('[data-consent="all"]').click();saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('iw-consent-v1')));ok(saved.statistics===true&&saved.advertising===false);
ok(!requests.some(u=>!u.startsWith(base)&&!u.includes('googletagmanager.com/gtag/js')));ok((await page.locator('a[href^="mailto:"]').count())>=4);
await page.goto(base+'/artikel/test-artikel/');ok(await page.locator('[data-iw-consent-open]').count()===1);ok(await page.locator('[data-iw-spot]').count()===0);
await page.goto(base+'/cookies/');ok(await page.locator('h1').innerText()==='Cookies & Einstellungen');
await page.evaluate(()=>{let x=JSON.parse(localStorage.getItem('iw-consent-v1'));x.at=0;localStorage.setItem('iw-consent-v1',JSON.stringify(x));document.cookie='iw_consent_v1='+encodeURIComponent(JSON.stringify(x))+'; Path=/; SameSite=Lax'});await page.reload();ok(await page.locator('#iw-consent').isVisible());await context.close();
}
console.log(count+' assertions passed: mobile/desktop, 320px, no external requests, denied/all unavailable, persistence, expiry, article, mailto.');
}finally{await browser.close();server.close();}})().catch(e=>{console.error(e);server.close();process.exitCode=1});
