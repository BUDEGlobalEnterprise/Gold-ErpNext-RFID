/**
 * Router tier helpers — pure-function tests (Commit C: feat(pos))
 *
 * Verifies the role-tier RBAC matrix introduced in router.js so a
 * future role-string typo or tier-table change can't silently demote
 * (or promote) a role.
 */

import { describe, it, expect } from 'vitest'
import { getAccessTier, canAccess, ROLE_TIERS, TIER_LEVELS } from '../src/router.js'

describe('router tier helpers — getAccessTier', () => {
	it('returns "admin" for System Manager', () => {
		expect(getAccessTier(['System Manager'])).toBe('admin')
	})

	it('returns "admin" for Administrator even with manager roles', () => {
		expect(getAccessTier(['Administrator', 'Sales Manager'])).toBe('admin')
	})

	it('returns "manager" for Sales Manager', () => {
		expect(getAccessTier(['Sales Manager'])).toBe('manager')
	})

	it('returns "manager" for Stock Manager', () => {
		expect(getAccessTier(['Stock Manager'])).toBe('manager')
	})

	it('returns "employee" for Sales User', () => {
		expect(getAccessTier(['Sales User'])).toBe('employee')
	})

	it('returns "employee" for Employee Self Service', () => {
		expect(getAccessTier(['Employee Self Service'])).toBe('employee')
	})

	it('returns null for unrecognised role-only user', () => {
		expect(getAccessTier(['Customer'])).toBeNull()
	})

	it('returns null for empty role list', () => {
		expect(getAccessTier([])).toBeNull()
	})

	it('picks highest tier when multiple roles overlap tiers', () => {
		// Admin + manager + employee → admin should win.
		expect(
			getAccessTier(['System Manager', 'Sales Manager', 'Sales User'])
		).toBe('admin')
		// Manager + employee → manager wins.
		expect(getAccessTier(['Sales Manager', 'Sales User'])).toBe('manager')
	})
})

describe('router tier helpers — canAccess', () => {
	it('allows when "all" is in required tiers', () => {
		expect(canAccess(['all'], 'employee')).toBe(true)
		expect(canAccess(['all'], null)).toBe(true)
	})

	it('admin can access any tier-restricted route', () => {
		expect(canAccess(['employee'], 'admin')).toBe(true)
		expect(canAccess(['manager'], 'admin')).toBe(true)
		expect(canAccess(['admin'], 'admin')).toBe(true)
	})

	it('manager can access manager+ but not admin-only', () => {
		expect(canAccess(['employee'], 'manager')).toBe(true)
		expect(canAccess(['manager'], 'manager')).toBe(true)
		expect(canAccess(['admin'], 'manager')).toBe(false)
	})

	it('employee can access employee but not manager or admin', () => {
		expect(canAccess(['employee'], 'employee')).toBe(true)
		expect(canAccess(['manager'], 'employee')).toBe(false)
		expect(canAccess(['admin'], 'employee')).toBe(false)
	})

	it('returns false for null user tier on a tier-restricted route', () => {
		expect(canAccess(['employee'], null)).toBe(false)
	})

	it('matches when user tier meets ANY required tier', () => {
		// Route gated for ['employee', 'manager', 'admin'] — any matches.
		expect(canAccess(['employee', 'manager', 'admin'], 'employee')).toBe(true)
		expect(canAccess(['employee', 'manager', 'admin'], 'manager')).toBe(true)
		expect(canAccess(['employee', 'manager', 'admin'], 'admin')).toBe(true)
	})
})

describe('router tier helpers — invariants', () => {
	it('TIER_LEVELS is monotonic increasing', () => {
		expect(TIER_LEVELS.employee).toBeLessThan(TIER_LEVELS.manager)
		expect(TIER_LEVELS.manager).toBeLessThan(TIER_LEVELS.admin)
	})

	it('every role in ROLE_TIERS is non-empty', () => {
		for (const tier of Object.keys(ROLE_TIERS)) {
			expect(Array.isArray(ROLE_TIERS[tier])).toBe(true)
			expect(ROLE_TIERS[tier].length).toBeGreaterThan(0)
		}
	})

	it('Administrator never appears in non-admin tier', () => {
		expect(ROLE_TIERS.manager).not.toContain('Administrator')
		expect(ROLE_TIERS.employee).not.toContain('Administrator')
	})
})
