import { defineConfig } from '@playwright/test'

export default defineConfig({
	testDir: './tests/visual',
	timeout: 30_000,
	expect: { timeout: 10_000 },
	retries: 2,
	use: {
		baseURL: 'http://localhost:8080/pos',
		screenshot: 'on',
		trace: 'on-first-retry',
	},
	projects: [
		// 6 viewport widths per plan §4.7
		{ name: 'xs-375', use: { viewport: { width: 375, height: 667 } } },
		{ name: 'sm-640', use: { viewport: { width: 640, height: 960 } } },
		{ name: 'md-768', use: { viewport: { width: 768, height: 1024 } } },
		{ name: 'lg-1024', use: { viewport: { width: 1024, height: 768 } } },
		{ name: 'xl-1280', use: { viewport: { width: 1280, height: 800 } } },
		{ name: '2xl-1536', use: { viewport: { width: 1536, height: 900 } } },
	],
	snapshotDir: './tests/visual/baselines',
	snapshotPathTemplate: '{snapshotDir}/{testFileDir}/{arg}-{projectName}{ext}',
})
