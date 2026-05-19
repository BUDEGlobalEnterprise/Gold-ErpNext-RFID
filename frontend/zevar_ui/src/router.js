import { createRouter, createWebHistory } from 'vue-router'

// Role tier definitions — must match backend reports.py constants
const ROLE_TIERS = {
	admin: ['Administrator', 'System Manager', 'Accounts Manager'],
	manager: ['Store Manager', 'Sales Manager', 'Stock Manager', 'Inventory Manager', 'HR Manager', 'HR User'],
	employee: ['Sales User', 'Employee', 'Employee Self Service'],
}

function getAccessTier(roles) {
	if (roles.some((r) => ROLE_TIERS.admin.includes(r))) return 'admin'
	if (roles.some((r) => ROLE_TIERS.manager.includes(r))) return 'manager'
	if (roles.some((r) => ROLE_TIERS.employee.includes(r))) return 'employee'
	return null
}

const TIER_LEVELS = { employee: 1, manager: 2, admin: 3 }

function canAccess(requiredTiers, userTier) {
	if (requiredTiers.includes('all')) return true
	const level = TIER_LEVELS[userTier] || 0
	return requiredTiers.some((t) => (TIER_LEVELS[t] || 0) <= level)
}

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
		path: '/inventory/add',
		name: 'InventoryAdd',
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
	// ── Reports Hub — all authenticated users can open it; content is role-filtered ──
	{
		path: '/reports',
		name: 'Reports',
		component: () => import('./pages/ReportsHub.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/reports/viewer/:reportId',
		name: 'ReportViewer',
		component: () => import('./pages/ReportViewer.vue'),
		meta: { requiresAuth: true, requiresManagement: true },
	},
	// ── Dashboards — granular RBAC by access tier ──
	{
		path: '/reports/dashboards/revenue',
		name: 'RevenueDashboard',
		component: () => import('./pages/dashboards/Revenue.vue'),
		meta: { requiresAuth: true, reportRoles: ['employee', 'manager', 'admin'] },
	},
	{
		path: '/reports/dashboards/inventory',
		name: 'InventoryDashboard',
		component: () => import('./pages/dashboards/Inventory.vue'),
		meta: { requiresAuth: true, reportRoles: ['manager', 'admin'] },
	},
	{
		path: '/reports/dashboards/customer',
		name: 'CustomerDashboard',
		component: () => import('./pages/dashboards/Customer.vue'),
		meta: { requiresAuth: true, reportRoles: ['manager', 'admin'] },
	},
	{
		path: '/reports/dashboards/admin',
		name: 'AdminMonitor',
		component: () => import('./pages/dashboards/AdminMonitor.vue'),
		meta: { requiresAuth: true, reportRoles: ['admin'] },
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
	// Phase 1: Stock
	{
		path: '/stock/supplier-orders',
		name: 'SupplierOrders',
		component: () => import('./pages/stock/SupplierOrders.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/incoming-memos',
		name: 'IncomingMemos',
		component: () => import('./pages/stock/IncomingMemos.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/assemblies',
		name: 'Assemblies',
		component: () => import('./pages/stock/Assemblies.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/metals',
		name: 'Metals',
		component: () => import('./pages/stock/Metals.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/gems',
		name: 'Gems',
		component: () => import('./pages/stock/Gems.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/storages',
		name: 'Storages',
		component: () => import('./pages/stock/Storages.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/categories',
		name: 'Categories',
		component: () => import('./pages/stock/Categories.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/brands',
		name: 'Brands',
		component: () => import('./pages/stock/Brands.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/collections',
		name: 'Collections',
		component: () => import('./pages/stock/Collections.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/stock/catalogs',
		name: 'Catalogs',
		component: () => import('./pages/stock/Catalogs.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/inventory-counts',
		name: 'InventoryCounts',
		component: () => import('./pages/InventoryAudit.vue'),
		meta: { requiresAuth: true },
	},
	// Phase 2: Accounting
	{
		path: '/accounting/transactions',
		name: 'AccountingTransactions',
		component: () => import('./pages/accounting/Transactions.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/accounting/terminals',
		name: 'Terminals',
		component: () => import('./pages/accounting/Terminals.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/accounting/invoices',
		name: 'Invoices',
		component: () => import('./pages/accounting/Invoices.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/accounting/credit-notes',
		name: 'CreditNotes',
		component: () => import('./pages/accounting/CreditNotes.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/accounting/export-ubl',
		name: 'ExportUBL',
		component: () => import('./pages/accounting/ExportUBL.vue'),
		meta: { requiresAuth: true },
	},
	// Phase 3: Core Ops
	{
		path: '/quotes',
		name: 'Quotes',
		component: () => import('./pages/Quotes.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/tasks',
		name: 'Tasks',
		component: () => import('./pages/Tasks.vue'),
		meta: { requiresAuth: true },
	},
	// Phase 4: HR
	{
		path: '/time-clock',
		name: 'TimeClock',
		component: () => import('./pages/TimeClock.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/leave',
		name: 'Leave',
		component: () => import('./pages/LeaveManagement.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/portal',
		name: 'EmployeePortal',
		component: () => import('./pages/EmployeePortal.vue'),
		meta: { requiresAuth: true },
	},
	{
		path: '/settings',
		name: 'Settings',
		component: () => import('./pages/Settings.vue'),
		meta: { requiresAuth: true },
	},
	// Profit Intelligence — Admin only (contains pricing engine, AI predictions)
	{
		path: '/reports/dashboards/profit',
		name: 'ProfitIntelligence',
		component: () => import('./pages/dashboards/ProfitIntelligence.vue'),
		meta: { requiresAuth: true, reportRoles: ['admin'] },
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

let _cachedUserInfo = null

async function getUserInfo() {
	if (_cachedUserInfo) return _cachedUserInfo
	try {
		const res = await fetch('/api/method/zevar_core.api.user_info.get_user_info', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		if (!res.ok) return null
		const data = await res.json()
		const userInfo = data?.message || data
		if (!userInfo || userInfo === 'Guest' || !Array.isArray(userInfo.roles)) return null
		_cachedUserInfo = userInfo
		return userInfo
	} catch {
		return null
	}
}

export function clearUserCache() {
	_cachedUserInfo = null
}

// Expose tier helpers for components
export { getAccessTier, canAccess, ROLE_TIERS, TIER_LEVELS }

router.beforeEach(async (to, _from, next) => {
	if (to.meta.guest) return next()

	if (to.meta.requiresAuth) {
		const userInfo = await getUserInfo()
		if (!userInfo) return next({ name: 'Login' })

		// Legacy requiresManagement check
		if (to.meta.requiresManagement) {
			const reportRoles = [
				'System Manager', 'Administrator', 'Store Manager', 'Sales Manager',
				'Accounts Manager', 'Sales User', 'Stock Manager', 'Inventory Manager',
				'HR User', 'HR Manager', 'Employee', 'Employee Self Service',
			]
			if (!userInfo.roles.some((r) => reportRoles.includes(r))) {
				return next({ name: 'Dashboard', query: { accessDenied: 'true' } })
			}
		}

		// Granular role-tier check for report routes
		if (to.meta.reportRoles) {
			const tier = getAccessTier(userInfo.roles)
			if (!tier || !canAccess(to.meta.reportRoles, tier)) {
				return next({ name: 'Dashboard', query: { accessDenied: 'true' } })
			}
		}
	}

	next()
})

export default router
