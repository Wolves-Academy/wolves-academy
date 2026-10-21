// Renders the PWA icons from static/logo-mark.png (run once: node tests/make_icons.cjs)
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');
const gRoot = execSync('npm root -g').toString().trim();
let pw;
for (const p of ['playwright-core', '@playwright/cli/node_modules/playwright-core']) {
  try { pw = require(path.join(gRoot, p)); break; } catch (e) {}
}
const STATIC = path.join(__dirname, '..', 'static');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(STATIC, 'logo-mark.png')).toString('base64');
// "any" icons: mark on deep purple-black; "maskable": extra safe-zone padding (Android crops to a circle)
const jobs = [['icon-192.png', 192, 0.74], ['icon-512.png', 512, 0.74], ['icon-maskable-512.png', 512, 0.56],
              ['apple-touch-icon.png', 180, 0.72]];
(async () => {
  const browser = await pw.chromium.launch({ channel: 'chrome', headless: true });
  for (const [file, size, scale] of jobs) {
    const page = await browser.newPage({ viewport: { width: size, height: size } });
    await page.setContent(`<html><body style="margin:0;width:${size}px;height:${size}px;display:grid;place-items:center;
      background:radial-gradient(120% 120% at 30% 20%, #2A1450 0%, #150A27 60%, #0E061B 100%)">
      <img src="${logo}" style="width:${Math.round(size * scale)}px;height:auto"></body></html>`);
    await page.waitForTimeout(150);
    await page.screenshot({ path: path.join(STATIC, file), omitBackground: false });
    console.log('icon', file);
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
