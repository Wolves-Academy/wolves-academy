// Asks Chrome itself whether the app is installable (node tests/pwa_check.cjs [baseUrl])
const path = require('path');
const { execSync } = require('child_process');
const gRoot = execSync('npm root -g').toString().trim();
let pw;
for (const p of ['playwright-core', '@playwright/cli/node_modules/playwright-core']) {
  try { pw = require(path.join(gRoot, p)); break; } catch (e) {}
}
const B = process.argv[2] || 'http://127.0.0.1:8766';
(async () => {
  // a persistent (non-incognito) profile: Chrome never offers install in incognito
  const dir = require('fs').mkdtempSync(path.join(require('os').tmpdir(), 'pwa-'));
  const ctx = await pw.chromium.launchPersistentContext(dir, { channel: 'chrome', headless: true, viewport: { width: 390, height: 844 } });
  const browser = ctx;
  const page = await ctx.newPage();
  await page.goto(B + '/login', { waitUntil: 'networkidle' });
  const sw = await page.evaluate(async () => !!(await navigator.serviceWorker.ready));
  const cdp = await ctx.newCDPSession(page);
  const { installabilityErrors } = await cdp.send('Page.getInstallabilityErrors');
  const man = await (await page.request.get(B + '/manifest.webmanifest')).json();
  console.log('service worker ready:', sw);
  console.log('manifest:', man.name, '|', man.display, '|', man.icons.length, 'icons');
  console.log('installability errors:', JSON.stringify(installabilityErrors));
  console.log(installabilityErrors.length === 0 && sw ? 'PWA_INSTALLABLE_OK' : 'PWA_NOT_INSTALLABLE');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
