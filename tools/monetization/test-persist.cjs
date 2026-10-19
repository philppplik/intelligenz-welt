// Developer-only: consent persistence (reject/accept/withdraw), no close/Escape dismissal, cookie fallback.
// NODE_PATH=/path/to/node_modules node tools/monetization/test-persist.cjs  (uses site/out)
const { chromium } = require('playwright-core'), http = require('http'), fs = require('fs'), path = require('path'), assert = require('assert');
const root = path.resolve(__dirname, '../../site/out'), P = 'iw';
const server = http.createServer((q, s) => { let f = path.join(root, decodeURI(q.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html'; try { s.setHeader('Content-Type', f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'text/javascript' : f.endsWith('.svg') ? 'image/svg+xml' : 'text/html'); s.end(fs.readFileSync(f)); } catch (e) { s.statusCode = 404; s.end('x'); } });
let n = 0; const ok = (v, m) => { assert(v, m); n++; };
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r)); const base = 'http://127.0.0.1:' + server.address().port;
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  for (const choice of ['reject', 'all']) for (const [w, h] of [[1440, 900], [390, 844]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h } }); await ctx.route('https://**/*', r => r.fulfill({ contentType: 'application/javascript', body: '' }));
    const p = await ctx.newPage(); await p.goto(base + '/');
    const panel = p.locator('#' + P + '-consent'); await panel.waitFor({ state: 'visible' });
    ok(await p.locator('[data-consent="close"]').count() === 0, 'no close button');
    await p.keyboard.press('Escape'); ok(await panel.isVisible(), 'escape does not dismiss');
    await p.reload(); ok(await panel.isVisible(), 'no decision = banner stays');
    await p.locator('[data-consent="' + choice + '"]').click(); ok(await panel.isHidden());
    await p.reload(); ok(await panel.isHidden(), choice + ' persists on reload');
    ok(await p.evaluate(() => document.cookie.includes('iw_consent_v1=')), 'cookie');
    await p.evaluate(() => localStorage.clear()); await p.reload(); ok(await panel.isHidden(), 'cookie fallback');
    await p.goto(base + '/cookies/'); ok(await panel.isHidden(), 'follow-up page');
    await p.locator('[data-iw-consent-open]').first().click(); ok(await panel.isVisible(), 'footer reopen');
    await p.locator('[data-consent="reject"]').click(); await p.reload(); ok(await panel.isHidden());
    const st = await p.evaluate(() => JSON.parse(localStorage.getItem('iw-consent-v1'))); ok(st.statistics === false, 'withdrawal stored');
    await ctx.close();
  }
  console.log(n + ' persistence assertions passed'); await b.close(); server.close();
})().catch(e => { console.error(e); process.exitCode = 1; server.close(); });
