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

	let storedItems = []
	try {
		const raw = localStorage.getItem('zevar_cart_items')
		storedItems = raw ? JSON.parse(raw) : []
	} catch (e) {
		localStorage.removeItem('zevar_cart_items')
		storedItems = []
	}

	// Customer linked to this sale
	const customer = ref(null)
	const customerType = ref('Individual') // 'Individual', 'Company', 'Walkin'
	const items = ref(storedItems)
	const taxRate = ref(0)
	const currency = ref('USD')

	// Salespersons attached to the current sale (up to 4)
	const salespersons = ref([])

	// Trade-in items attached to the current sale
	const tradeIns = ref([])

	// Sync state across tabs/windows
	window.addEventListener('storage', (event) => {
		if (event.key === 'zevar_cart_items') {
			try {
				const newVal = event.newValue ? JSON.parse(event.newValue) : []
				items.value = newVal
			} catch (e) {
				items.value = []
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
	}

	function clearCustomer() {
		customer.value = null
	}

	function addSalesperson(employee, split) {
		if (salespersons.value.length >= 4) return
		salespersons.value.push({ employee, split: split })
	}

	function recalculateSalespersonSplit(changedIndex) {
		const changed = salespersons.value[changedIndex]
		if (changed) {
			changed.split = Number(Number(changed.split || 0).toFixed(2))
		}

		if (salespersons.value.length === 2 && changed) {
			const otherIndex = changedIndex === 0 ? 1 : 0
			const other = salespersons.value[otherIndex]
			const newSplit = 100 - changed.split
			other.split = Number(newSplit.toFixed(2))
		}
	}

	function removeSalesperson(index) {
		salespersons.value.splice(index, 1)
	}

	function clearSalespersons() {
		salespersons.value = []
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
	}

	function removeTradeIn(index) {
		tradeIns.value.splice(index, 1)
	}

	function clearTradeIns() {
		tradeIns.value = []
	}

	function clearCart() {
		items.value = []
		customer.value = null
		customerType.value = 'Individual'
		salespersons.value = []
		tradeIns.value = []
		saveToStorage()
	}

	async function validateItems() {
		if (items.value.length === 0) return

		const itemCodes = items.value.map(i => i.item_code)
		const resource = createResource({
			url: 'zevar_core.api.pos.validate_cart_items',
			makeParams() {
				return { item_codes: JSON.stringify(itemCodes) }
			}
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
						message: 'Could not reach the cart validator. Please check your connection.',
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
		localStorage.setItem('zevar_cart_items', JSON.stringify(items.value))
	}

	// ==========================================================================
	// RESOURCES
	// ==========================================================================

	const fetchSettings = createResource({
		url: 'zevar_core.api.get_pos_settings',
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
		submitLayaway,
		customer,
		customerType,
		setCustomer,
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
