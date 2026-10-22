// Renders docs/admin-guide.html to docs/Wolves-Admin-Guide.pdf. Usage: node tests/make_guide.cjs
const path = require('path');
const { execSync } = require('child_process');
const gRoot = execSync('npm root -g').toString().trim();
let pw;
for (const p of ['playwright-core', '@playwright/cli/node_modules/playwright-core']) {
  try { pw = require(path.join(gRoot, p)); break; } catch (e) {}
}
(async () => {
  const browser = await pw.chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage();
  await page.goto(require('url').pathToFileURL(path.join(__dirname, '..', 'docs', 'admin-guide.html')).href);
  await page.pdf({ path: path.join(__dirname, '..', 'docs', 'Wolves-Admin-Guide.pdf'), format: 'A4',
    printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#8c869a">Wolves Sports Academy · Admin guide · <span class="pageNumber"></span>/<span class="totalPages"></span></div>' });
  await browser.close();
  console.log('PDF_OK');
})();
