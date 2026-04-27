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
	return session.isAdmin || session.isManager || session.hasAnyRole([
		'System Manager',
		'Administrator',
		'Store Manager',
		'Accounts Manager'
	])
}

/**
 * Check if user can view all sales history (vs own only)
 * @returns {boolean}
 */
export function canViewAllSalesHistory() {
	const session = useSessionStore()
	return session.isAdmin || session.isManager || session.hasAnyRole([
		'System Manager',
		'Administrator',
		'Store Manager',
		'Accounts Manager'
	])
}

/**
 * Check if user can view inventory analytics (best/worst selling, stagnant)
 * @returns {boolean}
 */
export function canViewInventoryAnalytics() {
	const session = useSessionStore()
	return session.isAdmin || session.isManager || session.hasAnyRole([
		'System Manager',
		'Administrator',
		'Store Manager',
		'Inventory Manager'
	])
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
	return session.isLoggedIn && session.hasAnyRole([
		'System Manager',
		'Administrator',
		'Store Manager',
		'Accounts Manager',
		'Sales User',
		'Employee',
		'Employee Self Service'
	])
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
	return session.isAdmin || session.isManager || session.hasAnyRole([
		'Store Manager',
		'Inventory Manager'
	])
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
	const isStandardUser = session.hasAnyRole(['Employee', 'Employee Self Service', 'Sales User']) &&
		!session.isAdmin && !session.isManager

	return {
		// Reports tile - Admin/Manager only
		reportsTile: !isStandardUser,

		// Full analytics section - Admin/Manager only
		fullAnalytics: !isStandardUser,

		// Own sales only indicator
		ownSalesOnly: isStandardUser,

		// Inventory analytics - Admin/Manager/Inventory Manager
		inventoryAnalytics: canViewInventoryAnalytics(),

		// Accounting section - Admin/Manager/Accounts Manager
		accountingSection: session.isAdmin || session.isManager ||
			session.hasRole('Accounts Manager'),
	}
}
