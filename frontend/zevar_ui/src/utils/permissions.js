/**
 * Permissions Utility
 *
 * Centralized role-based access control (RBAC) for POS Dashboard and Terminal.
 *
 * Role Hierarchy:
 * - System Manager / Administrator: Full access
 * - Store Manager: Full access to store operations, reports, analytics
 * - Accounts Manager: Accounting, financial reports
 * - Sales User: POS Terminal, own sales history only
 * - Employee / Employee Self Service: Limited POS access, own sales only
 */

import { useSessionStore } from '@/stores/session'

/**
 * Check if user can access Reports page
 * @returns {boolean}
 */
export function canAccessReports() {
	const session = useSessionStore()
	return (
		session.isAdmin ||
		session.isManager ||
		session.hasAnyRole([
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
		])
	)
}

/**
 * Check if user can view all sales history (vs own only)
 * @returns {boolean}
 */
export function canViewAllSalesHistory() {
	const session = useSessionStore()
	return (
		session.isAdmin ||
		session.isManager ||
		session.hasAnyRole([
			'System Manager',
			'Administrator',
			'Store Manager',
			'Accounts Manager',
		])
	)
}

/**
 * Check if user can view inventory analytics (best/worst selling, stagnant)
 * @returns {boolean}
 */
export function canViewInventoryAnalytics() {
	const session = useSessionStore()
	return (
		session.isAdmin ||
		session.isManager ||
		session.hasAnyRole([
			'System Manager',
			'Administrator',
			'Store Manager',
			'Inventory Manager',
		])
	)
}

/**
 * Check if user can access POS Terminal
 * @returns {boolean}
 */
export function canAccessPOSTerminal() {
	const session = useSessionStore()
	// All authenticated users can access POS
	return session.isLoggedIn
}

/**
 * Check if user can access POS Dashboard
 * @returns {boolean}
 */
export function canAccessPOSDashboard() {
	const session = useSessionStore()
	// Employee, ESS, Sales User, and all management roles
	return (
		session.isLoggedIn &&
		session.hasAnyRole([
			'System Manager',
			'Administrator',
			'Store Manager',
			'Accounts Manager',
			'Sales User',
			'Employee',
			'Employee Self Service',
		])
	)
}

/**
 * Check if user can access Management section
 * @returns {boolean}
 */
export function canAccessManagementSection() {
	const session = useSessionStore()
	return session.isAdmin || session.isManager
}

/**
 * Check if user can access Inventory Management section
 * @returns {boolean}
 */
export function canAccessInventoryManagement() {
	const session = useSessionStore()
	return (
		session.isAdmin ||
		session.isManager ||
		session.hasAnyRole(['Store Manager', 'Inventory Manager'])
	)
}

/**
 * Get the owner filter for sales queries (for non-admin users)
 * @returns {object|null} Filter object or null if no restriction
 */
export function getSalesOwnerFilter() {
	if (!canViewAllSalesHistory()) {
		const session = useSessionStore()
		// Filter by logged-in user's email
		return { owner: session.user?.email }
	}
	return null
}

/**
 * Role-based visibility configuration for dashboard tiles
 * Returns an object with boolean flags for each section/tile
 */
export function getDashboardVisibility() {
	const session = useSessionStore()
	const isStandardUser =
		session.hasAnyRole(['Employee', 'Employee Self Service', 'Sales User']) &&
		!session.isAdmin &&
		!session.isManager

	return {
		// Reports tile - server-side catalog still controls the visible reports
		reportsTile: canAccessReports(),

		// Full analytics section - Admin/Manager only
		fullAnalytics: !isStandardUser,

		// Own sales only indicator
		ownSalesOnly: isStandardUser,

		// Inventory analytics - Admin/Manager/Inventory Manager
		inventoryAnalytics: canViewInventoryAnalytics(),

		// Accounting section - Admin/Manager/Accounts Manager
		accountingSection:
			session.isAdmin || session.isManager || session.hasRole('Accounts Manager'),
	}
}

/**
 * Check if user can access Daily Closeout reports
 * @returns {boolean}
 */
export function canAccessDailyCloseout() {
	const session = useSessionStore()
	return (
		session.isAdmin ||
		session.isManager ||
		session.hasAnyRole(['Store Manager', 'Sales Manager', 'Accounts Manager'])
	)
}

/**
 * Check if user can access Sales Performance reports
 * @returns {boolean}
 */
export function canAccessSalesPerformance() {
	const session = useSessionStore()
	return session.hasAnyRole([
		'System Manager',
		'Administrator',
		'Store Manager',
		'Sales Manager',
		'Sales User',
	])
}

/**
 * Check if user can access Inventory reports
 * @returns {boolean}
 */
export function canAccessInventoryReports() {
	const session = useSessionStore()
	return (
		session.isAdmin ||
		session.isManager ||
		session.hasAnyRole([
			'Stock Manager',
			'Inventory Manager',
			'Store Manager',
			'Sales Manager',
		])
	)
}

/**
 * Check if user can access Accounting reports
 * @returns {boolean}
 */
export function canAccessAccountingReports() {
	const session = useSessionStore()
	return session.isAdmin || session.isManager || session.hasRole('Accounts Manager')
}

/**
 * Check if user can access HR/Employee reports
 * @returns {boolean}
 */
export function canAccessHRReports() {
	const session = useSessionStore()
	return (
		session.isAdmin ||
		session.hasAnyRole(['HR User', 'HR Manager', 'Employee', 'Employee Self Service'])
	)
}

/**
 * Check if user is limited to own sales only (Sales User without manager roles)
 * @returns {boolean}
 */
export function isOwnSalesOnly() {
	const session = useSessionStore()
	const isSalesUser = session.hasRole('Sales User')
	const isEmployee = session.hasAnyRole(['Employee', 'Employee Self Service'])
	const hasElevatedRoles =
		session.isAdmin ||
		session.isManager ||
		session.hasAnyRole([
			'Accounts Manager',
			'Stock Manager',
			'Inventory Manager',
			'HR User',
			'HR Manager',
		])
	return (isSalesUser || isEmployee) && !hasElevatedRoles
}

/**
 * Get report scope label for the current user
 * @returns {string}
 */
export function getReportScopeLabel() {
	if (isOwnSalesOnly()) return 'Own Sales'
	const session = useSessionStore()
	if (session.isAdmin) return 'All Stores'
	if (
		session.isManager ||
		session.hasAnyRole([
			'Accounts Manager',
			'Stock Manager',
			'Inventory Manager',
			'HR User',
			'HR Manager',
		])
	)
		return 'Current Store'
	return 'Own Sales'
}

/**
 * Get primary role label for the current user
 * @returns {string}
 */
export function getPrimaryRoleLabel() {
	const session = useSessionStore()
	if (session.hasRole('System Manager')) return 'System Manager'
	if (session.hasRole('Store Manager')) return 'Store Manager'
	if (session.hasRole('Accounts Manager')) return 'Accounts Manager'
	if (session.hasRole('Sales Manager')) return 'Sales Manager'
	if (session.hasRole('Stock Manager') || session.hasRole('Inventory Manager'))
		return 'Stock Manager'
	if (session.hasRole('HR Manager')) return 'HR Manager'
	if (session.hasRole('HR User')) return 'HR User'
	if (session.hasRole('Sales User')) return 'Sales User'
	if (session.hasAnyRole(['Employee', 'Employee Self Service'])) return 'Employee'
	return 'User'
}
