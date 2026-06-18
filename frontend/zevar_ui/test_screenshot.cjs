const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('http://zevar.localhost:8000/pos/terminal', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/screenshot.png' });
  await browser.close();
})();
