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
		name: 'Dashboard',
		component: () => import('./pages/Dashboard.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/terminal',
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
		path: '/inventory-audit',
		name: 'InventoryAudit',
		component: () => import('./pages/InventoryAudit.vue'),
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
		path: '/pos-catalogue/:category',
		name: 'POSCategoryListing',
		component: () => import('./pages/POSCategoryListing.vue'),
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
		path: '/repair-lookup',
		name: 'RepairLookup',
		component: () => import('./pages/RepairLookup.vue'),
		meta: { guest: true },
	},
	{
		path: '/repair-estimate/:token',
		name: 'EstimateApproval',
		component: () => import('./pages/EstimateApproval.vue'),
		meta: { guest: true },
	},
	{
		path: '/repair-portal',
		name: 'CustomerRepairPortal',
		component: () => import('./pages/CustomerRepairPortal.vue'),
		meta: { guest: true },
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
		component: () => import('./pages/ReportsHub.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	{
		path: '/reports/viewer/:reportId',
		name: 'ReportViewer',
		component: () => import('./pages/ReportViewer.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	{
		path: '/reports/dashboards/revenue',
		name: 'RevenueDashboard',
		component: () => import('./pages/dashboards/Revenue.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	{
		path: '/reports/dashboards/inventory',
		name: 'InventoryDashboard',
		component: () => import('./pages/dashboards/Inventory.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	{
		path: '/reports/dashboards/customer',
		name: 'CustomerDashboard',
		component: () => import('./pages/dashboards/Customer.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	{
		path: '/reports/dashboards/admin',
		name: 'AdminMonitor',
		component: () => import('./pages/dashboards/AdminMonitor.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	{
		path: '/contacts',
		name: 'Contacts',
		component: () => import('./pages/Contacts.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/support',
		name: 'Support',
		component: () => import('./pages/Support.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/knowledge-base',
		name: 'KnowledgeBase',
		component: () => import('./pages/KnowledgeBase.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	{
		path: '/opening',
		name: 'POSOpening',
		component: () => import('./pages/POSOpening.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/closing',
		name: 'POSClosing',
		component: () => import('./pages/POSClosing.vue'),
		meta: { requiresAuth: true },
	},
	// Catch-all → Dashboard
	{
		path: '/:pathMatch(.*)*',
		redirect: '/',
	},
]

const router = createRouter({
	history: createWebHistory('/pos'),
	routes,
})

// Check if user has any role that can open the Reports hub.
async function checkUserRole() {
	try {
		const res = await fetch('/api/method/zevar_core.api.user_info.get_user_info', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		if (!res.ok) return false
		const data = await res.json()
		const userInfo = data?.message || data
		if (!userInfo || userInfo === 'Guest' || !Array.isArray(userInfo.roles)) return false

		const reportRoles = [
			'System Manager',
			'Administrator',
			'Store Manager',
			'Sales Manager',
			'Accounts Manager',
			'Sales User',
			'Stock Manager',
			'Inventory Manager',
			'HR User',
			'HR Manager',
			'Employee',
			'Employee Self Service',
		]
		return userInfo.roles.some((role) => reportRoles.includes(role))
	} catch {
		return false
	}
}

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

			// Role-based access check for Reports page
			if (to.meta.requiresManagement) {
				const hasManagementAccess = await checkUserRole()
				if (!hasManagementAccess) {
					// Redirect to dashboard with access denied message
					return next({ name: 'Dashboard', query: { accessDenied: 'true' } })
				}
			}
		} catch {
			return next({ name: 'Login' })
		}
	}

	next()
})

export default router
