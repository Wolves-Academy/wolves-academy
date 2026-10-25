// Phone-width layout check against the demo server (tests/serve_demo.py on :8766).
// Lists pages wider than the screen and the elements sticking out. Usage: node tests/phone_check.cjs [shotDir]
const path = require('path');
const { execSync } = require('child_process');
const gRoot = execSync('npm root -g').toString().trim();
let pw;
for (const p of ['playwright-core', '@playwright/cli/node_modules/playwright-core']) {
  try { pw = require(path.join(gRoot, p)); break; } catch (e) {}
}
const B = 'http://127.0.0.1:8766';
const PAGES = ['/dashboard', '/attendance', '/players', '/players/1', '/players/new', '/payments', '/finance', '/coaches',
  '/coaches/1', '/coaches/checkin', '/groups', '/analytics', '/events', '/settings', '/reports/weekly', '/reports/month',
  '/reports/trials'];
(async () => {
  const browser = await pw.chromium.launch({ channel: 'chrome', headless: true });
  let bad = 0;
  for (const lang of ['en', 'ar']) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
      extraHTTPHeaders: { 'Cf-Ray': 'x' } });
    await ctx.addCookies([{ name: 'lang', value: lang, url: B }, { name: 'session', value: '', url: B }]);
    const page = await ctx.newPage();
    await page.goto(B + '/login'); await page.fill('#pin', '0000'); await page.click('button.btn-ink');
    for (const u of PAGES) {
      await page.goto(B + u, { waitUntil: 'networkidle' });
      const r = await page.evaluate(() => {
        const W = document.documentElement.clientWidth, out = [];
        const sw = document.documentElement.scrollWidth;
        document.querySelectorAll('body *').forEach(el => {
          const b = el.getBoundingClientRect();
          if (!b.width || getComputedStyle(el).position === 'fixed') return;
          let p = el.parentElement, clipped = false;
          while (p && p !== document.body) { const cs = getComputedStyle(p); if (cs.overflowX !== 'visible' || cs.position === 'fixed') { clipped = true; break; } p = p.parentElement; }
          if (!clipped && (b.right > W + 1 || b.left < -1)) out.push(`${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 3).join('.')} [${Math.round(b.left)}..${Math.round(b.right)}] "${(el.innerText || '').trim().slice(0, 30)}"`);
        });
        return { sw, W, out: out.slice(0, 6) };
      });
      if (r.sw > r.W || r.out.length) { bad++; console.log(`[${lang}] ${u}: page ${r.sw}px > ${r.W}px`); r.out.forEach(o => console.log('    ' + o)); }
      if (process.argv[2] && ['/players', '/analytics', '/dashboard', '/attendance'].includes(u))
        await page.screenshot({ path: path.join(process.argv[2], `${lang}${u.replace(/\//g, '_')}.png`) });
    }
    await ctx.close();
  }
  await browser.close();
  console.log(bad ? `PHONE_OVERFLOW ${bad}` : 'PHONE_OK');
})();
