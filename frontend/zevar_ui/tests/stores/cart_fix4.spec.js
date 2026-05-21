/**
 * Cart Store Fix #4 Tests (Vitest)
 *
 * Covers the additions from Fix #4:
 *   - addItem returns a structured status
 *   - duplicate serial-number scans are blocked with status 'duplicate_serial'
 *   - same item_code without a serial still increments qty
 *   - validateForSubmit calls validate_pos_cart and returns structured issues
 *   - validateForSubmit fails closed on transport error
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// ---- Resource mock ---------------------------------------------------------
//
// We capture the createResource calls so each test can decide what the next
// .fetch() returns. The cart store imports createResource from 'frappe-ui',
// so we mock the module wholesale.

let resourceCalls = []
let nextFetchResult = null
let nextFetchError = null

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
// addItem return contract
// ---------------------------------------------------------------------------

describe('addItem return value', () => {
	it('returns status="added" for a new item', () => {
		const cart = useCartStore()
		const result = cart.addItem({ item_code: 'A1', final_price: 100 })
		expect(result.status).toBe('added')
		expect(result.item_code).toBe('A1')
		expect(result.serial_no).toBeNull()
	})

	it('returns status="invalid" when item_code is missing', () => {
		const cart = useCartStore()
		const result = cart.addItem({ final_price: 100 })
		expect(result.status).toBe('invalid')
		expect(cart.items).toHaveLength(0)
	})
})

// ---------------------------------------------------------------------------
// Duplicate-serial guard
// ---------------------------------------------------------------------------

describe('addItem duplicate-serial guard', () => {
	it('rejects scanning the same serial twice', () => {
		const cart = useCartStore()
		const first = cart.addItem({ item_code: 'A1', serial_no: 'SN-1', final_price: 500 })
		const second = cart.addItem({ item_code: 'A1', serial_no: 'SN-1', final_price: 500 })

		expect(first.status).toBe('added')
		expect(second.status).toBe('duplicate_serial')
		expect(second.serial_no).toBe('SN-1')
		expect(cart.items).toHaveLength(1)
	})

	it('allows two different serials of the same item_code', () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', serial_no: 'SN-1', final_price: 500 })
		const result = cart.addItem({ item_code: 'A1', serial_no: 'SN-2', final_price: 500 })

		expect(result.status).toBe('added')
		expect(cart.items).toHaveLength(2)
		expect(cart.items.map((i) => i.serial_no)).toEqual(['SN-1', 'SN-2'])
	})

	it('still increments qty when the same non-serialized item is scanned twice', () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'B1', final_price: 50 })
		const second = cart.addItem({ item_code: 'B1', final_price: 50 })

		expect(second.status).toBe('added')
		expect(cart.items).toHaveLength(1)
		expect(cart.items[0].qty).toBe(2)
	})

	it('keeps a serialized line and a non-serialized line for the same item_code separate', () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'C1', final_price: 100 })
		cart.addItem({ item_code: 'C1', serial_no: 'SN-9', final_price: 100 })

		expect(cart.items).toHaveLength(2)
		expect(cart.items[0].serial_no).toBeNull()
		expect(cart.items[1].serial_no).toBe('SN-9')
	})
})

// ---------------------------------------------------------------------------
// validateForSubmit
// ---------------------------------------------------------------------------

describe('validateForSubmit', () => {
	it('returns ok=true / no issues for an empty cart without calling the API', async () => {
		const cart = useCartStore()
		const result = await cart.validateForSubmit('Some Warehouse')

		expect(result.ok).toBe(true)
		expect(result.blocking).toBe(false)
		expect(result.issues).toEqual([])
		// Two resource calls happen during store init (fetchSettings) but no
		// extra call should have been made for the empty validate.
		const validateCalls = resourceCalls.filter(
			(r) => r.url === 'zevar_core.api.pos.validate_pos_cart'
		)
		expect(validateCalls).toHaveLength(0)
	})

	it('forwards the structured response from validate_pos_cart', async () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 500 })

		nextFetchResult = {
			message: {
				ok: false,
				blocking: true,
				issues: [
					{
						item_code: 'A1',
						type: 'out_of_stock',
						message: 'Sold out',
						blocking: true,
					},
				],
			},
		}

		const result = await cart.validateForSubmit('WH-1')

		expect(result.ok).toBe(false)
		expect(result.blocking).toBe(true)
		expect(result.issues).toHaveLength(1)
		expect(result.issues[0].type).toBe('out_of_stock')

		const validateCall = resourceCalls.find(
			(r) => r.url === 'zevar_core.api.pos.validate_pos_cart'
		)
		expect(validateCall).toBeDefined()
		expect(validateCall.method).toBe('POST')
		expect(validateCall.params.warehouse).toBe('WH-1')
		const sentItems = JSON.parse(validateCall.params.items)
		expect(sentItems).toEqual([{ item_code: 'A1', qty: 1, rate: 500, serial_no: null }])
	})

	it('treats a price_drift issue as non-blocking even though the API may say ok=true', async () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 75 })

		nextFetchResult = {
			message: {
				ok: true,
				blocking: false,
				issues: [
					{
						item_code: 'A1',
						type: 'price_drift',
						message: 'Price changed',
						blocking: false,
						details: { cart_rate: 75, current_price: 100 },
					},
				],
			},
		}

		const result = await cart.validateForSubmit('WH-1')

		expect(result.ok).toBe(true)
		expect(result.blocking).toBe(false)
		expect(result.issues).toHaveLength(1)
		expect(result.issues[0].blocking).toBe(false)
		expect(result.issues[0].details.current_price).toBe(100)
	})

	it('fails closed on network error so the UI can refuse to submit', async () => {
		const cart = useCartStore()
		cart.addItem({ item_code: 'A1', final_price: 100 })

		nextFetchError = new Error('boom')

		const result = await cart.validateForSubmit('WH-1')

		expect(result.ok).toBe(false)
		expect(result.blocking).toBe(true)
		expect(result.issues).toHaveLength(1)
		expect(result.issues[0].type).toBe('network_error')
	})
})
