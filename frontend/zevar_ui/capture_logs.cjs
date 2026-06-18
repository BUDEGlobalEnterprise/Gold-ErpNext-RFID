const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  const logs = [];
  page.on('console', msg => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });
  page.on('pageerror', err => {
    logs.push(`[PAGE ERROR] ${err.message}`);
  });
  page.on('requestfailed', request => {
    logs.push(`[REQUEST FAILED] ${request.url()} - ${request.failure().errorText}`);
  });

  try {
    await page.goto('http://zevar.localhost:8000/pos/login', { waitUntil: 'networkidle' });
    
    // Fill login form
    await page.fill('input[type="text"], input[type="email"], input[placeholder*="ID"]', 'Administrator');
    await page.fill('input[type="password"]', 'admin'); // Assuming default admin/admin for dev
    await page.click('button[type="submit"], button:has-text("Login")');
    
    // Wait for navigation or network idle
    await page.waitForTimeout(3000);
    
    await page.goto('http://zevar.localhost:8000/pos/terminal', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    fs.writeFileSync('/workspace/development/frappe-bench/apps/zevar_core/frontend/zevar_ui/browser_logs.txt', logs.join('\n'));
    console.log("Playwright run finished. Logs written.");
  } catch (err) {
    console.error("Playwright error:", err);
  } finally {
    await browser.close();
  }
})();
