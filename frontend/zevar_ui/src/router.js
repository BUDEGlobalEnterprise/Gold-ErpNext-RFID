import { createRouter, createWebHistory } from 'vue-router'

const routes = [
	{
		path: '/login',
		name: 'Login',
		component: () => import('./pages/Login.vue'),
		meta: { guest: true },
	},
	{
		path: '/',
		name: 'POS',
		component: () => import('./pages/POS.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/transactions',
		name: 'Transactions',
		component: () => import('./pages/SalesHistory.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/inventory',
		name: 'Inventory',
		component: () => import('./pages/Inventory.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/customers',
		name: 'Customers',
		component: () => import('./pages/Customers.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/layaway',
		name: 'Layaway',
		component: () => import('./pages/Layaway.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/pos-catalogue',
		name: 'POSCatalogue',
		component: () => import('./pages/POSCatalogue.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/catalogues',
		name: 'Catalogues',
		component: () => import('./pages/CatalogueDashboard.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/catalogues/:category',
		name: 'CategoryListing',
		component: () => import('./pages/CategoryListing.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/repairs',
		name: 'Repairs',
		component: () => import('./pages/RepairTerminal.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/trade-ins',
		name: 'TradeIns',
		component: () => import('./pages/TradeIns.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/appraisals',
		name: 'Appraisals',
		component: () => import('./pages/Appraisals.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/reports',
		name: 'Reports',
		component: () => import('./pages/Reports.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/support',
		name: 'Support',
		component: () => import('./pages/Support.vue'),
		meta: { requiresAuth: true },
	},
	// Catch-all → POS
	{
		path: '/:pathMatch(.*)*',
		redirect: '/',
	},
]

const router = createRouter({
	history: createWebHistory('/pos'),
	routes,
})

// Auth guard — redirect unauthenticated users to login
router.beforeEach(async (to, _from, next) => {
	// Skip guard for guest routes
	if (to.meta.guest) {
		return next()
	}

	// Check if user is logged in via Frappe session
	if (to.meta.requiresAuth) {
		try {
			const res = await fetch('/api/method/frappe.auth.get_logged_user', {
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
			})
			if (!res.ok) throw new Error('Not authenticated')
			const data = await res.json()
			if (!data.message || data.message === 'Guest') {
				return next({ name: 'Login' })
			}
		} catch {
			return next({ name: 'Login' })
		}
	}

	next()
})

export default router
