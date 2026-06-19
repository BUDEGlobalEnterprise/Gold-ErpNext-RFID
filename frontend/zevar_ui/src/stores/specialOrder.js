/**
 * Special Order Store
 *
 * Manages draft special-order state, stone sourcing rows, and debounced
 * live-quote requests to the Frappe backend.
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'

// ──────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────

/**
 * Simple debounce factory (no external dependency).
 * Returns a function with `.cancel()` and `.flush()` helpers.
 */
function debounce(fn, delay, opts = {}) {
	let timer = null
	const { leading = false, trailing = true } = opts

	const debounced = function (...args) {
		const callNow = leading && !timer
		if (timer) clearTimeout(timer)
		if (callNow) fn.apply(this, args)
		if (trailing) {
			timer = setTimeout(() => {
				timer = null
				fn.apply(this, args)
			}, delay)
		}
	}
	debounced.cancel = () => {
		if (timer) clearTimeout(timer)
		timer = null
	}
	debounced.flush = () => {
		if (timer) {
			clearTimeout(timer)
			timer = null
			fn.apply(this, args)
		}
	}
	return debounced
}

// ──────────────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────────────

function makeStoneId() {
	return 'stn_' + Math.random().toString(36).substring(2, 10)
}

function makeOrderId() {
	return 'SPO-' + new Date().toISOString().slice(2, 10).replace(/-/g, '') + '-' + Math.random().toString(36).substring(2, 6).toUpperCase()
}

/**
 * Build the shape the backend expects from `get_live_quote`.
 */
function buildQuotePayload(draft) {
	return {
		customer: draft.customer?.name || draft.customer || '',
		warehouse: draft.warehouse || '',
		metal_weight: Number(draft.metalWeight) || 0,
		metal_purity: draft.metalPurity || '',
		metal_type: draft.metalType || '',
		stones: draft.stones.map((s) => ({
			stone_id: s.id,
			stone_type: s.stoneType || 'Diamond',
			carat_weight: Number(s.caratWeight) || 0,
			cut: s.cut || '',
			color: s.color || '',
			clarity: s.clarity || '',
			shape: s.shape || '',
			source: s.source || '',
			sourcing_method: s.sourcingMethod || 'In-Stock',
			supplier_id: s.supplierId || null,
			unit_price: Number(s.unitPrice) || 0,
		})),
		labor_cost: Number(draft.laborCost) || 0,
		overhead_cost: Number(draft.overheadCost) || 0,
		margin_percent: Number(draft.marginPercent) || 0,
	}
}

// ──────────────────────────────────────────────────────────────────────────
// Store
// ──────────────────────────────────────────────────────────────────────────

export const useSpecialOrderStore = defineStore('specialOrder', () => {
	// ── STEP STATE ────────────────────────────────────────────────────────
	const currentStep = ref(1) // 1=Intake → 2=Design → 3=Stones → 4=Quote
	const steps = [
		{ id: 1, label: 'Intake', icon: 'M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-10V4m0 10V4m-4 10h4' },
		{ id: 2, label: 'Design', icon: 'M11 4a2 2 0 1 1 4 0 2 2 0 0 1-4 0zm3.45 6.45-.45.45-3.45 3.45-1.45-1.45 3.45-3.45.45.45zm-6.9-.9L11 14.5 7.5 18H3v-4.5L6.5 10l1.05 1.05Z' },
		{ id: 3, label: 'Stones', icon: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5' },
		{ id: 4, label: 'Quote', icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M12 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2Z' },
	]

	function goToStep(step) {
		if (step >= 1 && step <= 4) currentStep.value = step
	}

	function nextStep() {
		goToStep(Math.min(4, currentStep.value + 1))
	}

	function prevStep() {
		goToStep(Math.max(1, currentStep.value - 1))
	}

	// ── DRAFT ORDER ───────────────────────────────────────────────────────
	const draftOrder = ref({
		orderId: makeOrderId(),
		customer: null,
		warehouse: '',
		metalType: '',
		metalPurity: '',
		metalWeight: 0,
		laborCost: 0,
		overheadCost: 0,
		marginPercent: 30,
		status: 'Draft',
		stones: [],
		notes: '',
	})

	// ── LIVE QUOTE ────────────────────────────────────────────────────────
	const liveQuote = ref(null)
	const isFetchingQuote = ref(false)
	const lastQuoteError = ref('')

	/** Debounced POST to get_live_quote — avoids hammering the backend on every keystroke. */
	const fetchLiveQuote = debounce(
		async () => {
			isFetchingQuote.value = true
			lastQuoteError.value = ''
			try {
				const resource = createResource({
					url: 'zevar_core.api.special_order.get_live_quote',
				})
				const result = await resource.submit(buildQuotePayload(draftOrder.value))
				liveQuote.value = result?.message || result || null
			} catch (e) {
				lastQuoteError.value = e?.message || 'Failed to fetch live quote'
				console.error('[SpecialOrder] get_live_quote error:', e)
			} finally {
				isFetchingQuote.value = false
			}
		},
		600,
		{ leading: false, trailing: true }
	)

	// Deep watch on the entire draft order so any change (metal weight,
	// stones array, costs, etc.) triggers a live-quote refresh.
	watch(
		draftOrder,
		() => {
			fetchLiveQuote()
		},
		{ deep: true }
	)

	// ── SUPPLIER LIST (Lightspeed Vendor Memos) ─────────────────────────
	const suppliers = ref([])
	const fetchSuppliersResource = createResource({
		url: 'zevar_core.api.special_order.get_memo_suppliers',
		auto: true,
		onSuccess(data) {
			suppliers.value = Array.isArray(data) ? data : (data?.message || data || [])
		},
	})

	// ── STONES ────────────────────────────────────────────────────────────
	function addStone(row) {
		draftOrder.value.stones.push({
			id: makeStoneId(),
			stoneType: row?.stoneType || 'Diamond',
			caratWeight: row?.caratWeight || 0,
			cut: row?.cut || '',
			color: row?.color || '',
			clarity: row?.clarity || '',
			shape: row?.shape || '',
			source: row?.source || '',
			sourcingMethod: row?.sourcingMethod || 'In-Stock',
			supplierId: row?.supplierId || null,
			unitPrice: row?.unitPrice || 0,
		})
	}

	function removeStone(stoneId) {
		draftOrder.value.stones = draftOrder.value.stones.filter((s) => s.id !== stoneId)
	}

	function updateStone(stoneId, field, value) {
		const stone = draftOrder.value.stones.find((s) => s.id === stoneId)
		if (stone) {
			stone[field] = value
		}
	}

	function clearStones() {
		draftOrder.value.stones = []
	}

	// ── SUMMARY COMPUTED ──────────────────────────────────────────────────
	const totalStoneCost = computed(() => {
		return draftOrder.value.stones.reduce((sum, s) => sum + (Number(s.caratWeight) || 0) * (Number(s.unitPrice) || 0), 0)
	})

	const subtotal = computed(() => {
		return (totalStoneCost.value + (Number(draftOrder.value.metalWeight) || 0) * (Number(draftOrder.value.metalPrice || 0)) + (Number(draftOrder.value.laborCost) || 0) + (Number(draftOrder.value.overheadCost) || 0))
	})

	const grandTotal = computed(() => {
		if (liveQuote.value?.total) return Number(liveQuote.value.total)
		return Number((subtotal.value * (1 + (Number(draftOrder.value.marginPercent) || 0) / 100)).toFixed(2))
	})

	// ── SUBMIT ────────────────────────────────────────────────────────────
	const submitOrderResource = createResource({
		url: 'zevar_core.api.special_order.create_special_order',
	})

	async function submitOrder() {
		const payload = {
			order_id: draftOrder.value.orderId,
			customer: draftOrder.value.customer?.name || draftOrder.value.customer || '',
			warehouse: draftOrder.value.warehouse || '',
			metal_type: draftOrder.value.metalType,
			metal_purity: draftOrder.value.metalPurity,
			metal_weight: Number(draftOrder.value.metalWeight),
			labor_cost: Number(draftOrder.value.laborCost),
			overhead_cost: Number(draftOrder.value.overheadCost),
			margin_percent: Number(draftOrder.value.marginPercent),
			stones: draftOrder.value.stones,
			notes: draftOrder.value.notes,
		}
		const result = await submitOrderResource.submit(payload)
		return result
	}

	function resetDraft() {
		draftOrder.value = {
			orderId: makeOrderId(),
			customer: null,
			warehouse: '',
			metalType: '',
			metalPurity: '',
			metalWeight: 0,
			laborCost: 0,
			overheadCost: 0,
			marginPercent: 30,
			status: 'Draft',
			stones: [],
			notes: '',
		}
		liveQuote.value = null
		lastQuoteError.value = ''
		currentStep.value = 1
		suppliers.value = []
	}

	return {
		// Step state
		currentStep,
		steps,
		goToStep,
		nextStep,
		prevStep,

		// Draft
		draftOrder,
		addStone,
		removeStone,
		updateStone,
		clearStones,

		// Suppliers (Lightspeed vendor memos)
		suppliers,
		fetchSuppliersResource,

		// Quote
		liveQuote,
		isFetchingQuote,
		lastQuoteError,
		fetchLiveQuote,

		// Summary
		totalStoneCost,
		subtotal,
		grandTotal,

		// Submit
		submitOrderResource,
		submitOrder,
		resetDraft,
	}
})
