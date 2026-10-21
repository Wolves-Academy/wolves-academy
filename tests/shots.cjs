// Full-page captures of the demo server (tests/serve_demo.py) into review/.
// Usage: node tests/shots.cjs
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');
const gRoot = execSync('npm root -g').toString().trim();
let pw;
for (const p of ['playwright-core', '@playwright/cli/node_modules/playwright-core']) {
  try { pw = require(path.join(gRoot, p)); break; } catch (e) {}
}
const OUT = path.join(__dirname, '..', 'review');
fs.mkdirSync(OUT, { recursive: true });
const B = 'http://127.0.0.1:8766';
const jobs = [
  ['desktop.png', '/dashboard', 1440, 'en', 'light'],
  ['mobile.png', '/dashboard', 390, 'en', 'light'],
  ['mobile-dark.png', '/dashboard', 390, 'en', 'dark'],
  ['mobile-coaches.png', '/coaches', 390, 'en', 'light'],
  ['desktop-coach.png', '/coaches/1', 1440, 'en', 'light'],
  ['mobile-players-school.png', '/players?sort=school', 390, 'en', 'light'],
  ['mobile-player.png', '/players/1', 390, 'en', 'light'],
  ['mobile-form.png', '/players/1/edit', 390, 'en', 'light'],
  ['mobile-weekly.png', '/reports/weekly', 390, 'en', 'light'],
  ['mobile-trials.png', '/reports/trials', 390, 'ar', 'light'],
  ['mobile-coach-portal.png', 'COACH:/attendance?group=1', 390, 'en', 'light'],
  ['mobile-login.png', 'ANON:/login', 390, 'en', 'dark'],
];
(async () => {
  const browser = await pw.chromium.launch({ channel: 'chrome', headless: true });
  for (const [file, spec, w, lang, theme] of jobs) {
    const mobile = w < 600;
    const ctx = await browser.newContext({ viewport: { width: w, height: mobile ? 844 : 900 },
      deviceScaleFactor: mobile ? 2 : 1, reducedMotion: 'reduce', colorScheme: theme, hasTouch: mobile, isMobile: mobile,
      // a tunnel header makes the app treat this visitor as remote (not the laptop admin)
      extraHTTPHeaders: /^(COACH|ANON):/.test(spec) ? { 'Cf-Ray': 'demo' } : {} });
    await ctx.addCookies([{ name: 'lang', value: lang, url: B }]);
    await ctx.addInitScript(t => { try { localStorage.setItem('theme', t); } catch (e) {} }, theme);
    const page = await ctx.newPage();
    let url = spec;
    if (spec.startsWith('COACH:') || spec.startsWith('ANON:')) {
      const base = B;
      url = spec.split(':').slice(1).join(':');
      await ctx.addCookies([{ name: 'lang', value: lang, url: base }]);
      if (spec.startsWith('COACH:')) {
        await page.goto(base + '/login');
        await page.fill('input[name=pin]', '482913');
        await page.click('button[type=submit], form button');
        await page.waitForLoadState('networkidle');
      }
      await page.goto(base + url, { waitUntil: 'networkidle' });
    } else {
      await page.goto(B + url, { waitUntil: 'networkidle' });
    }
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(OUT, file), fullPage: true });
    console.log('saved', file);
    await ctx.close();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
