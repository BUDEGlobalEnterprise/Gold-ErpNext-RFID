/**
 * Playwright visual regression tests for Zevar UI responsive pages.
 *
 * Takes screenshots at 6 viewport widths (xs/sm/md/lg/xl/2xl)
 * for all key routes. Baselines stored in tests/visual/baselines/.
 *
 * Run: npx playwright test --config playwright.config.js
 * Update baselines: npx playwright test --config playwright.config.js --update-snapshots
 */

import { test, expect } from '@playwright/test'

// 20 key routes from the plan
const ROUTES = [
	{ path: '/', name: 'Dashboard' },
	{ path: '/terminal', name: 'POS' },
	{ path: '/inventory', name: 'Inventory' },
	{ path: '/inventory-audit', name: 'InventoryAudit' },
	{ path: '/customers', name: 'Customers' },
	{ path: '/transactions', name: 'Transactions' },
	{ path: '/pos-catalogue', name: 'POSCatalogue' },
	{ path: '/layaway', name: 'Layaway' },
	{ path: '/repairs', name: 'Repairs' },
	{ path: '/trade-ins', name: 'TradeIns' },
	{ path: '/appraisals', name: 'Appraisals' },
	{ path: '/reports', name: 'ReportsHub' },
	{ path: '/contacts', name: 'Contacts' },
	{ path: '/support', name: 'Support' },
	{ path: '/catalogues', name: 'Catalogues' },
	{ path: '/repair-lookup', name: 'RepairLookup' },
	{ path: '/login', name: 'Login' },
	// Dynamic routes need specific IDs — skip if not available
	// { path: '/pos-catalogue/rings', name: 'POSCategoryListing' },
	// { path: '/catalogues/rings', name: 'CategoryListing' },
	// { path: '/reports/viewer/daily_sales', name: 'ReportViewer' },
]

for (const route of ROUTES) {
	test(`${route.name} (${route.path}) — visual regression`, async ({ page }) => {
		// Navigate and wait for content to stabilize
		await page.goto(route.path, { waitUntil: 'networkidle' })

		// Wait for main content area to render
		await page
			.waitForSelector('main, .app-shell-main, .app-layout-main', { timeout: 5000 })
			.catch(() => {})

		// Small delay for animations
		await page.waitForTimeout(500)

		// Check no horizontal scroll
		const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth)
		const clientWidth = await page.evaluate(() => document.documentElement.clientWidth)
		expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 2) // allow 2px tolerance

		// Take full-page screenshot
		await expect(page).toHaveScreenshot(`${route.name}.png`, {
			maxDiffPixelRatio: 0.05,
			fullPage: false, // viewport-only for responsive testing
		})
	})
}
