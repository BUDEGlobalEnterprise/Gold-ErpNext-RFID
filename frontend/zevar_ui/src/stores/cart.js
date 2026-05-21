/**
 * Cart Store
 *
 * Manages shopping cart state, item operations, tax calculation, and order submission.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createResource, call } from 'frappe-ui'

export const useCartStore = defineStore('cart', () => {
	// ==========================================================================
	// STATE
	// ==========================================================================

	// localStorage keys. Bumping the prefix would force a clean slate;
	// keeping each cart slice in its own key means a corrupt entry in
	// one (e.g. salespersons) cannot wipe the others.
	const LS = {
		items: 'zevar_cart_items',
		customer: 'zevar_cart_customer',
		customerType: 'zevar_cart_customer_type',
		salespersons: 'zevar_cart_salespersons',
		tradeIns: 'zevar_cart_tradeins',
	}

	function _readJson(key, fallback) {
		try {
			const raw = localStorage.getItem(key)
			return raw ? JSON.parse(raw) : fallback
		} catch (e) {
			localStorage.removeItem(key)
			return fallback
		}
	}

	function _writeJson(key, value) {
		try {
			localStorage.setItem(key, JSON.stringify(value))
		} catch (e) {
			// localStorage may be full or unavailable (private mode).
			// In-memory state stays correct; we just lose persistence.
		}
	}

	// Hydrate every cart slice from localStorage so a session-expiry
	// induced refresh keeps the cashier's full context: items, customer,
	// salespersons, and trade-ins. Before Fix #8 only `items` was hydrated
	// here — everything else was silently dropped.
	const storedItems = _readJson(LS.items, [])
	const storedCustomer = _readJson(LS.customer, null)
	const storedCustomerType = (() => {
		try {
			return localStorage.getItem(LS.customerType) || 'Individual'
		} catch (e) {
			return 'Individual'
		}
	})()
	const storedSalespersons = _readJson(LS.salespersons, [])
	const storedTradeIns = _readJson(LS.tradeIns, [])

	// Customer linked to this sale
	const customer = ref(storedCustomer)
	const customerType = ref(storedCustomerType) // 'Individual', 'Company', 'Walkin'
	const items = ref(storedItems)
	const taxRate = ref(0)
	const currency = ref('USD')

	// Salespersons attached to the current sale (up to 4)
	const salespersons = ref(storedSalespersons)

	// Self-heal old/invalid salespersons splits on load
	if (salespersons.value.length > 0) {
		const hasInvalidSplit = salespersons.value.some(
			(sp) => sp.split === null || sp.split === undefined || isNaN(sp.split)
		)
		const totalSplit = salespersons.value.reduce((sum, sp) => sum + (Number(sp.split) || 0), 0)
		if (hasInvalidSplit || Math.abs(totalSplit - 100) > 0.01) {
			// Auto distribute equally to heal the local storage state
			const count = salespersons.value.length
			const equalShare = Number((100 / count).toFixed(2))
			let sum = 0
			salespersons.value.forEach((sp, idx) => {
				if (idx === count - 1) {
					sp.split = Number((100 - sum).toFixed(2))
				} else {
					sp.split = equalShare
					sum += equalShare
				}
			})
			_writeJson(LS.salespersons, salespersons.value)
		}
	}

	// Trade-in items attached to the current sale
	const tradeIns = ref(storedTradeIns)

	// Sync state across tabs/windows. Each cart slice has its own key so
	// only the slice that actually changed in another tab gets updated
	// here — avoids racy whole-cart overwrites.
	window.addEventListener('storage', (event) => {
		if (event.key === LS.items) {
			try {
				items.value = event.newValue ? JSON.parse(event.newValue) : []
			} catch (e) {
				items.value = []
			}
		} else if (event.key === LS.customer) {
			try {
				customer.value = event.newValue ? JSON.parse(event.newValue) : null
			} catch (e) {
				customer.value = null
			}
		} else if (event.key === LS.customerType) {
			customerType.value = event.newValue || 'Individual'
		} else if (event.key === LS.salespersons) {
			try {
				salespersons.value = event.newValue ? JSON.parse(event.newValue) : []
			} catch (e) {
				salespersons.value = []
			}
		} else if (event.key === LS.tradeIns) {
			try {
				tradeIns.value = event.newValue ? JSON.parse(event.newValue) : []
			} catch (e) {
				tradeIns.value = []
			}
		}
	})

	// ==========================================================================
	// GETTERS
	// ==========================================================================

	const totalItems = computed(() => {
		return items.value.reduce((total, item) => total + (item.qty || 1), 0)
	})

	const subtotal = computed(() => {
		const sum = items.value.reduce((s, item) => {
			const qty = item.qty || 1
			const price = item.amount || 0
			return s + price * qty
		}, 0)
		return Number(sum.toFixed(2))
	})

	const tax = computed(() => Number((subtotal.value * (taxRate.value / 100)).toFixed(2)))

	const tradeInCredit = computed(() => {
		const sum = tradeIns.value.reduce((s, ti) => s + (ti.trade_in_value || 0), 0)
		return Number(sum.toFixed(2))
	})

	const grandTotal = computed(() => {
		const total = subtotal.value + tax.value - tradeInCredit.value
		return Number(Math.max(0, total).toFixed(2))
	})

	// ==========================================================================
	// ACTIONS
	// ==========================================================================

	function addItem(item) {
		// Return a structured status so callers can show a clear UI message
		// (e.g. "already in cart") without parsing magic strings or relying
		// on cart-length deltas. Existing callers that ignore the return
		// value still work because successful adds keep their old behavior.
		if (!item.item_code) {
			return { status: 'invalid', message: 'Item is missing item_code.' }
		}

		const incomingSerial = item.serial_no || null

		// Duplicate-scan guard: a serial number identifies a unique physical
		// piece. Scanning the same one twice is almost always a slip — show
		// a warning and don't double-add. The cashier can deliberately add
		// other serials of the same item_code without conflict.
		if (incomingSerial) {
			const dupe = items.value.find((i) => i.serial_no && i.serial_no === incomingSerial)
			if (dupe) {
				return {
					status: 'duplicate_serial',
					serial_no: incomingSerial,
					item_code: item.item_code,
					message: `Serial ${incomingSerial} is already in the cart.`,
				}
			}
		}

		const priceToUse = item.final_price || item.price || item.amount || 0
		// Match by item_code AND serial_no so a non-serialized line and a
		// serialized line for the same item_code stay separate.
		const existingItem = items.value.find(
			(i) => i.item_code === item.item_code && (i.serial_no || null) === incomingSerial
		)

		if (existingItem) {
			// Two cases reach here:
			//   - non-serialized item scanned again -> qty++
			//   - serialized item with matching serial -> blocked above
			// So this only ever runs for non-serialized lines.
			existingItem.qty++
		} else {
			items.value.push({
				item_code: item.item_code,
				item_name: item.item_name,
				image: item.image,
				metal: item.metal || item.custom_metal_type,
				purity: item.purity || item.custom_purity,
				amount: priceToUse,
				weight: item.gross_weight || item.custom_gross_weight_g,
				qty: 1,
				serial_no: incomingSerial,
			})
		}
		saveToStorage()
		return { status: 'added', item_code: item.item_code, serial_no: incomingSerial }
	}

	function removeItem(index) {
		items.value.splice(index, 1)
		saveToStorage()
	}

	function setCustomer(customerData) {
		customer.value = customerData
		_writeJson(LS.customer, customerData)
	}

	function clearCustomer() {
		customer.value = null
		try {
			localStorage.removeItem(LS.customer)
		} catch (e) {
			/* ignore */
		}
	}

	function setCustomerType(type) {
		customerType.value = type || 'Individual'
		try {
			localStorage.setItem(LS.customerType, customerType.value)
		} catch (e) {
			/* ignore */
		}
	}

	function _persistSalespersons() {
		_writeJson(LS.salespersons, salespersons.value)
	}

	function _persistTradeIns() {
		_writeJson(LS.tradeIns, tradeIns.value)
	}

	function autoDistributeSplits() {
		const count = salespersons.value.length
		if (count === 0) return

		const equalShare = Number((100 / count).toFixed(2))
		let sum = 0

		salespersons.value.forEach((sp, idx) => {
			if (idx === count - 1) {
				sp.split = Number((100 - sum).toFixed(2))
			} else {
				sp.split = equalShare
				sum += equalShare
			}
		})
		_persistSalespersons()
	}

	function addSalesperson(employee, split) {
		if (salespersons.value.length >= 4) return
		salespersons.value.push({ employee, split: split || 0 })
		autoDistributeSplits()
	}

	function recalculateSalespersonSplit(changedIndex) {
		const count = salespersons.value.length
		if (count <= 1) {
			autoDistributeSplits()
			return
		}

		const changed = salespersons.value[changedIndex]
		if (!changed) return

		// Clamp the entered split between 0 and 100
		let val = Number(changed.split)
		if (isNaN(val)) val = 0
		val = Math.max(0, Math.min(100, val))
		changed.split = Number(val.toFixed(2))

		const remaining = 100 - changed.split
		const otherCount = count - 1

		const equalShare = Number((remaining / otherCount).toFixed(2))
		let sum = 0

		let processedOtherCount = 0
		salespersons.value.forEach((sp, idx) => {
			if (idx === changedIndex) return
			processedOtherCount++
			if (processedOtherCount === otherCount) {
				sp.split = Number((remaining - sum).toFixed(2))
			} else {
				sp.split = equalShare
				sum += equalShare
			}
		})

		_persistSalespersons()
	}

	function removeSalesperson(index) {
		salespersons.value.splice(index, 1)
		autoDistributeSplits()
	}

	function clearSalespersons() {
		salespersons.value = []
		_persistSalespersons()
	}

	// Trade-in management
	function addTradeIn({ description, tradeInValue, newItemValue }) {
		tradeIns.value.push({
			description: description || '',
			trade_in_value: tradeInValue || 0,
			new_item_value: newItemValue || 0,
			manager_override: '',
			override_reason: '',
		})
		_persistTradeIns()
	}

	function removeTradeIn(index) {
		tradeIns.value.splice(index, 1)
		_persistTradeIns()
	}

	function clearTradeIns() {
		tradeIns.value = []
		_persistTradeIns()
	}

	function clearCart() {
		items.value = []
		customer.value = null
		customerType.value = 'Individual'
		salespersons.value = []
		tradeIns.value = []
		// Wipe every persisted slice; before Fix #8, clearCart only
		// rewrote zevar_cart_items so customer/salespersons/tradeins
		// would silently survive across sales.
		try {
			localStorage.removeItem(LS.customer)
			localStorage.removeItem(LS.customerType)
			localStorage.removeItem(LS.salespersons)
			localStorage.removeItem(LS.tradeIns)
		} catch (e) {
			/* ignore */
		}
		saveToStorage()
	}

	async function validateItems() {
		if (items.value.length === 0) return

		const itemCodes = items.value.map((i) => i.item_code)
		const resource = createResource({
			url: 'zevar_core.api.pos.validate_cart_items',
			makeParams() {
				return { item_codes: JSON.stringify(itemCodes) }
			},
		})

		try {
			const results = await resource.fetch()
			const validData = results.message || results || {}

			// Update the cart state
			const updatedItems = []
			let changed = false

			for (const item of items.value) {
				const serverItem = validData[item.item_code]
				if (!serverItem || serverItem.disabled) {
					changed = true
					continue // Item removed
				}

				if (item.amount !== serverItem.rate) {
					item.amount = serverItem.rate
					changed = true
				}
				updatedItems.push(item)
			}

			if (changed) {
				items.value = updatedItems
				saveToStorage()
			}
		} catch (e) {
			console.error('Failed to validate cart items:', e)
		}
	}

	/**
	 * Pre-submit gate. Calls zevar_core.api.pos.validate_pos_cart and
	 * returns its structured response so the caller (POS.vue / CartSidebar)
	 * can render blocking errors and price-drift warnings before the
	 * cashier presses "Submit".
	 *
	 * Shape of the resolved value:
	 *   {
	 *     ok: boolean,           // true iff there are no blocking issues
	 *     blocking: boolean,     // any issue with blocking=true
	 *     issues: Array<{
	 *       item_code: string,
	 *       type: string,        // 'out_of_stock' | 'price_drift' | ...
	 *       message: string,
	 *       blocking: boolean,
	 *       details?: object,
	 *     }>,
	 *   }
	 *
	 * On network/transport failure resolves to { ok: false, blocking: true,
	 * issues: [{ type: 'network_error', ... }] } so callers can fail
	 * closed and refuse to submit instead of guessing.
	 */
	async function validateForSubmit(warehouse) {
		if (items.value.length === 0) {
			return { ok: true, blocking: false, issues: [] }
		}

		const payload = items.value.map((i) => ({
			item_code: i.item_code,
			qty: i.qty || 1,
			rate: i.amount || 0,
			serial_no: i.serial_no || null,
		}))

		try {
			const resource = createResource({
				url: 'zevar_core.api.pos.validate_pos_cart',
				method: 'POST',
				params: {
					items: JSON.stringify(payload),
					warehouse: warehouse || '',
				},
			})
			const result = await resource.fetch()
			const data = result?.message ?? result ?? {}
			return {
				ok: !!data.ok,
				blocking: !!data.blocking,
				issues: Array.isArray(data.issues) ? data.issues : [],
			}
		} catch (e) {
			console.error('validate_pos_cart failed:', e)
			return {
				ok: false,
				blocking: true,
				issues: [
					{
						item_code: '',
						type: 'network_error',
						message:
							'Could not reach the cart validator. Please check your connection.',
						blocking: true,
					},
				],
			}
		}
	}

	function updateItemQuantity(index, qty) {
		if (qty <= 0) {
			items.value.splice(index, 1)
		} else {
			items.value[index].qty = qty
		}
		saveToStorage()
	}

	function saveToStorage() {
		_writeJson(LS.items, items.value)
	}

	/**
	 * Recognize the shape of "your session has expired" errors that
	 * frappe-ui's createResource raises when the auth cookie has been
	 * invalidated. We accept several patterns because the exact envelope
	 * varies between Frappe versions and proxies (some return 401 with
	 * html, some return 403 with the auth_error message, some bubble up
	 * a string).
	 */
	function isAuthExpiredError(err) {
		if (!err) return false
		// Network failure: treat as not-auth so the UI can retry without
		// forcing the cashier through a re-login.
		if (err.name === 'TypeError' && /network|failed to fetch/i.test(err.message || '')) {
			return false
		}
		const status = err.statusCode || err.status || err?.response?.status
		if (status === 401 || status === 403) {
			return true
		}
		const exc = err.exc_type || err?.response?.data?.exc_type
		if (
			exc &&
			/AuthenticationError|SessionExpiredError|InvalidAuthorizationToken/i.test(exc)
		) {
			return true
		}
		const msg = (err.message || err._server_messages || '').toString()
		if (/session\s*expired|please\s+log\s*in|authentication.*required/i.test(msg)) {
			return true
		}
		return false
	}

	/**
	 * Submit the order through the existing submitOrder action but trap
	 * any auth-expiry error and re-throw with a stable, machine-readable
	 * shape so the caller can render "Session expired — please log in
	 * again. Your cart is saved." without losing context.
	 *
	 * Crucially this NEVER calls clearCart on failure. The whole point
	 * of Fix #8 is that an expired session preserves the cashier's work.
	 */
	async function submitOrderSafe(payments, options = {}) {
		try {
			return await submitOrder(payments, options)
		} catch (err) {
			if (isAuthExpiredError(err)) {
				const wrapped = new Error(
					'Your session has expired. Please log in again — your cart is saved.'
				)
				wrapped.code = 'session_expired'
				wrapped.cause = err
				throw wrapped
			}
			throw err
		}
	}

	// ==========================================================================
	// RESOURCES
	// ==========================================================================

	const fetchSettings = createResource({
		url: 'zevar_core.api.pos.get_pos_settings',
		onSuccess(data) {
			if (data) {
				taxRate.value = data.tax_rate || 0
				currency.value = data.currency || 'USD'
			}
		},
	})

	function loadTaxForWarehouse(warehouse) {
		if (warehouse) {
			fetchSettings.fetch({ warehouse })
		}
	}

	// ==========================================================================
	// ORDER SUBMISSION
	// ==========================================================================

	/**
	 * Submit a POS invoice to the backend.
	 *
	 * @param {Array<{mode: string, amount: number}>} payments - Payment modes with amounts.
	 * @param {object} options - Additional options.
	 * @param {boolean} [options.taxExempt=false] - Whether to exempt tax.
	 * @param {string} [options.warehouse] - Warehouse for stock deduction.
	 * @param {string} [options.giftCardNumber] - Gift card number if paying by gift card.
	 * @param {string} [options.overrideReference] - Reference ID for tax override.
	 * @returns {Promise<object>} The API response.
	 */
	async function submitOrder(
		payments,
		{ taxExempt = false, warehouse, giftCardNumber, overrideReference } = {}
	) {
		const itemsPayload = items.value.map((i) => ({
			item_code: i.item_code,
			qty: i.qty || 1,
			rate: i.amount || 0,
			serial_no: i.serial_no || null,
		}))

		const paymentsPayload = payments.map((p) => ({
			mode_of_payment: p.mode,
			amount: p.amount,
		}))

		const customerName =
			customerType.value === 'Walkin'
				? 'Walk-In Customer'
				: customer.value?.name || 'Walk-In Customer'

		const params = {
			items: JSON.stringify(itemsPayload),
			payments: JSON.stringify(paymentsPayload),
			customer: customerName,
			warehouse: warehouse || '',
			tax_exempt: taxExempt,
		}

		// Attach gift card number if provided
		if (giftCardNumber) {
			params.gift_card_number = giftCardNumber
		}

		// Attach tax override reference if provided
		if (overrideReference) {
			params.override_reference = overrideReference
		}

		// Attach salespersons if any are assigned
		if (salespersons.value.length > 0) {
			params.salespersons = JSON.stringify(
				salespersons.value.map((sp) => ({
					employee: sp.employee,
					split: sp.split,
				}))
			)
		}

		// Attach trade-ins if any are present
		if (tradeIns.value.length > 0) {
			params.trade_ins = JSON.stringify(
				tradeIns.value.map((ti) => ({
					trade_in_value: ti.trade_in_value,
					new_item_value: ti.new_item_value,
					manager_override: ti.manager_override,
					override_reason: ti.override_reason,
				}))
			)
		}

		const r = await createResource({
			url: 'zevar_core.api.create_pos_invoice',
			method: 'POST',
			params,
		}).fetch()

		return r
	}

	/**
	 * Create a layaway contract from the current cart items.
	 *
	 * @param {number} depositAmount - Initial deposit.
	 * @param {number} durationMonths - Contract duration (6, 9, or 12).
	 * @returns {Promise<object>} The API response with layaway_id.
	 */
	async function submitLayaway(depositAmount, durationMonths, { warehouse } = {}) {
		const itemsPayload = items.value.map((i) => ({
			item_code: i.item_code,
			qty: i.qty || 1,
			rate: i.amount || 0,
			serial_no: i.serial_no || null,
		}))

		const customerName =
			customerType.value === 'Walkin'
				? 'Walk-In Customer'
				: customer.value?.name || 'Walk-In Customer'

		// Walk-in customers are not eligible for layaway
		if (customerName === 'Walk-In Customer') {
			throw new Error(
				'Walk-In customers are not eligible for layaway. Please select a registered customer with contact details.'
			)
		}

		const data = await call('zevar_core.api.layaway.create_layaway', {
			customer: customerName,
			items: JSON.stringify(itemsPayload),
			deposit_amount: depositAmount,
			duration_months: durationMonths,
			warehouse: warehouse || undefined,
		})

		return data
	}

	return {
		items,
		taxRate,
		currency,
		totalItems,
		subtotal,
		tax,
		tradeInCredit,
		grandTotal,
		fetchSettings,
		loadTaxForWarehouse,
		addItem,
		removeItem,
		updateItemQuantity,
		clearCart,
		validateItems,
		validateForSubmit,
		submitOrder,
		submitOrderSafe,
		submitLayaway,
		isAuthExpiredError,
		customer,
		customerType,
		setCustomer,
		setCustomerType,
		clearCustomer,
		salespersons,
		addSalesperson,
		recalculateSalespersonSplit,
		removeSalesperson,
		clearSalespersons,
		tradeIns,
		addTradeIn,
		removeTradeIn,
		clearTradeIns,
	}
})
