/**
 * Cart Store Fix #8 Tests (Vitest)
 *
 * Covers the additions from Fix #8:
 *   - Full cart context (items + customer + customerType + salespersons +
 *     tradeIns) is persisted across reloads, so a session-expiry-induced
 *     refresh doesn't lose the cashier's work.
 *   - Storage events from other tabs sync each slice independently.
 *   - clearCart wipes EVERY persisted key (Fix #8 exposed a latent bug
 *     where customer/salespersons/tradeins survived clearCart).
 *   - isAuthExpiredError recognises the various Frappe auth-error shapes.
 *   - submitOrderSafe wraps auth failures with a stable {code:'session_expired'}
 *     and crucially does NOT clear the cart on failure.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// ---- Resource mock ---------------------------------------------------------
//
// submitOrder calls createResource(...).fetch() once per submission. We
// capture the call and let each test choose what fetch returns or throws.

let nextFetchResult = null
let nextFetchError = null
let resourceCalls = []

vi.mock('frappe-ui', () => ({
	createResource: vi.fn((opts) => {
		resourceCalls.push(opts)
		return {
			fetch: vi.fn(() => {
				if (nextFetchError) {
					return Promise.reject(nextFetchError)
				}
				return Promise.resolve(nextFetchResult)
			}),
		}
	}),
	call: vi.fn(() => Promise.resolve({})),
}))

import { useCartStore } from '../../src/stores/cart.js'

beforeEach(() => {
	setActivePinia(createPinia())
	resourceCalls = []
	nextFetchResult = null
	nextFetchError = null
	if (global.localStorage?.clear) {
		global.localStorage.clear()
	}
})

// ---------------------------------------------------------------------------
// Persistence: every cart slice survives a reload
// ---------------------------------------------------------------------------

describe('Fix #8 — full cart persistence', () => {
	it('persists customer through a fresh store instance', () => {
		const cart = useCartStore()
		cart.setCustomer({ name: 'CUST-1', customer_name: 'Jane Doe' })

		// A new Pinia simulates a page reload triggered by session expiry.
		setActivePinia(createPinia())
		const cart2 = useCartStore()

		expect(cart2.customer).toEqual({ name: 'CUST-1', customer_name: 'Jane Doe' })
	})

	it('persists customerType through a fresh store instance', () => {
		const cart = useCartStore()
		cart.setCustomerType('Walkin')

		setActivePinia(createPinia())
		const cart2 = useCartStore()

		expect(cart2.customerType).toBe('Walkin')
	})

	it('persists salespersons through a fresh store instance', () => {
		const cart = useCartStore()
		cart.addSalesperson('EMP-1', 60)
		cart.addSalesperson('EMP-2', 40)

		setActivePinia(createPinia())
		const cart2 = useCartStore()

		expect(cart2.salespersons).toEqual([
			{ employee: 'EMP-1', split: 60 },
			{ employee: 'EMP-2', split: 40 },
		])
	})

	it('persists trade-ins through a fresh store instance', () => {
		const cart = useCartStore()
		cart.addTradeIn({ description: 'Old chain', tradeInValue: 200, newItemValue: 500 })

		setActivePinia(createPinia())
		const cart2 = useCartStore()

		expect(cart2.tradeIns).toHaveLength(1)
		expect(cart2.tradeIns[0].trade_in_value).toBe(200)
		expect(cart2.tradeIns[0].description).toBe('Old chain')
	})

	it('persists customer + salespersons + items together (the real use-case)', () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 250 })
		cart.setCustomer({ name: 'CUST-9', customer_name: 'Tester' })
		cart.addSalesperson('EMP-9', 100)

		// Simulate session-expiry-induced page reload.
		setActivePinia(createPinia())
		const cart2 = useCartStore()

		expect(cart2.items).toHaveLength(1)
		expect(cart2.items[0].item_code).toBe('A1')
		expect(cart2.customer.name).toBe('CUST-9')
		expect(cart2.salespersons[0].employee).toBe('EMP-9')
	})

	it('clearCustomer wipes the persisted customer key too', () => {
		const cart = useCartStore()
		cart.setCustomer({ name: 'X', customer_name: 'Y' })
		cart.clearCustomer()

		setActivePinia(createPinia())
		const cart2 = useCartStore()
		expect(cart2.customer).toBeNull()
	})

	it('clearCart wipes every persisted key, not just items', () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 100 })
		cart.setCustomer({ name: 'C-1' })
		cart.setCustomerType('Walkin')
		cart.addSalesperson('EMP-1', 100)
		cart.addTradeIn({ tradeInValue: 50 })

		cart.clearCart()

		// New store: all slices must come up empty/default.
		setActivePinia(createPinia())
		const cart2 = useCartStore()
		expect(cart2.items).toEqual([])
		expect(cart2.customer).toBeNull()
		expect(cart2.customerType).toBe('Individual')
		expect(cart2.salespersons).toEqual([])
		expect(cart2.tradeIns).toEqual([])
	})
})

// ---------------------------------------------------------------------------
// Cross-tab sync
// ---------------------------------------------------------------------------

describe('Fix #8 — cross-tab sync', () => {
	it('updates customer when another tab writes the customer key', () => {
		const cart = useCartStore()
		expect(cart.customer).toBeNull()

		const event = new StorageEvent('storage', {
			key: 'zevar_cart_customer',
			newValue: JSON.stringify({ name: 'CUST-OTHERTAB', customer_name: 'X' }),
		})
		window.dispatchEvent(event)

		expect(cart.customer).toEqual({ name: 'CUST-OTHERTAB', customer_name: 'X' })
	})

	it('clears salespersons when another tab clears them', () => {
		const cart = useCartStore()
		cart.addSalesperson('EMP-A', 100)

		const event = new StorageEvent('storage', {
			key: 'zevar_cart_salespersons',
			newValue: '[]',
		})
		window.dispatchEvent(event)

		expect(cart.salespersons).toEqual([])
	})

	it('handles corrupted cross-tab payloads gracefully', () => {
		const cart = useCartStore()

		const event = new StorageEvent('storage', {
			key: 'zevar_cart_tradeins',
			newValue: 'not json',
		})
		window.dispatchEvent(event)

		expect(cart.tradeIns).toEqual([])
	})
})

// ---------------------------------------------------------------------------
// Auth-expiry recognition
// ---------------------------------------------------------------------------

describe('Fix #8 — isAuthExpiredError', () => {
	it('returns true for HTTP 401', () => {
		const cart = useCartStore()
		expect(cart.isAuthExpiredError({ status: 401 })).toBe(true)
		expect(cart.isAuthExpiredError({ statusCode: 401 })).toBe(true)
	})

	it('returns true for HTTP 403', () => {
		const cart = useCartStore()
		expect(cart.isAuthExpiredError({ status: 403 })).toBe(true)
	})

	it('returns true for AuthenticationError exc_type', () => {
		const cart = useCartStore()
		expect(cart.isAuthExpiredError({ exc_type: 'AuthenticationError' })).toBe(true)
		expect(cart.isAuthExpiredError({ exc_type: 'SessionExpiredError' })).toBe(true)
	})

	it('returns true for "session expired" message', () => {
		const cart = useCartStore()
		expect(
			cart.isAuthExpiredError({ message: 'Your session expired. Please log in again.' })
		).toBe(true)
	})

	it('returns false for ordinary validation errors', () => {
		const cart = useCartStore()
		expect(cart.isAuthExpiredError({ status: 400, message: 'Item out of stock' })).toBe(false)
	})

	it('returns false for network errors so the UI can retry', () => {
		const cart = useCartStore()
		const err = new TypeError('Failed to fetch')
		expect(cart.isAuthExpiredError(err)).toBe(false)
	})

	it('returns false for null / undefined', () => {
		const cart = useCartStore()
		expect(cart.isAuthExpiredError(null)).toBe(false)
		expect(cart.isAuthExpiredError(undefined)).toBe(false)
	})
})

// ---------------------------------------------------------------------------
// submitOrderSafe wraps auth failures and preserves the cart
// ---------------------------------------------------------------------------

describe('Fix #8 — submitOrderSafe', () => {
	it('rethrows session_expired error on 401 without clearing the cart', async () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 100 })
		cart.setCustomer({ name: 'C-1' })

		nextFetchError = { status: 401, message: 'Not authenticated' }

		await expect(cart.submitOrderSafe([{ mode: 'Cash', amount: 100 }])).rejects.toMatchObject({
			code: 'session_expired',
		})

		// Cart MUST still be intact.
		expect(cart.items).toHaveLength(1)
		expect(cart.customer.name).toBe('C-1')
	})

	it('passes through non-auth errors unchanged', async () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 100 })

		const original = new Error('Item out of stock')
		original.status = 400
		nextFetchError = original

		await expect(cart.submitOrderSafe([{ mode: 'Cash', amount: 100 }])).rejects.toBe(original)
		expect(cart.items).toHaveLength(1)
	})

	it('forwards a successful submit through unchanged', async () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 100 })

		nextFetchResult = { message: { invoice_name: 'INV-1', status: 'Paid' } }

		const r = await cart.submitOrderSafe([{ mode: 'Cash', amount: 100 }])
		expect(r).toBeDefined()
	})
})
