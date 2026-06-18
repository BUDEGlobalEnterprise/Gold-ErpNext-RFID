const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', msg => console.log(`[Browser Console ${msg.type()}] ${msg.text()}`));
  page.on('pageerror', error => console.error(`[Browser Error] ${error.message}`));
  page.on('requestfailed', request => console.error(`[Request Failed] ${request.url()} - ${request.failure().errorText}`));

  console.log('Navigating to http://zevar.localhost:8000/pos/terminal ...');
  try {
    await page.goto('http://zevar.localhost:8000/pos/terminal', { waitUntil: 'networkidle', timeout: 10000 });
  } catch (e) {
    console.error('Goto error:', e);
  }

  // wait a bit for any late errors
  await page.waitForTimeout(2000);

  await browser.close();
})();
