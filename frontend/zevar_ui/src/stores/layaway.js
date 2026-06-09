/**
 * Layaway Store
 *
 * Manages layaway contracts, payments, and schedules.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

export const useLayawayStore = defineStore('layaway', () => {
	// ==========================================================================
	// STATE
	// ==========================================================================

	const layaways = ref([])
	const currentLayaway = ref(null)
	const loading = ref(false)
	const error = ref(null)

	// Filters
	const filters = ref({
		status: '',
		customer: '',
		search: '',
	})

	// ==========================================================================
	// RESOURCES
	// ==========================================================================

	const layawaysResource = createResource({
		fetcher: async (data) => {
			return await frappe.call('zevar_core.api.layaway.get_all_layaways', data)
		},
		auto: false,
	})

	const layawayDetailsResource = createResource({
		fetcher: async (data) => {
			return await frappe.call('zevar_core.api.layaway.get_layaway_details', data)
		},
		auto: false,
	})

	const customerLayawaysResource = createResource({
		fetcher: async (data) => {
			return await frappe.call('zevar_core.api.layaway.get_customer_layaways', data)
		},
		auto: false,
	})

	const processPaymentResource = createResource({
		fetcher: async (data) => {
			return await frappe.call('zevar_core.api.layaway.process_layaway_payment', data)
		},
		auto: false,
	})

	const cancelLayawayResource = createResource({
		url: 'zevar_core.api.layaway.cancel_layaway',
		auto: false,
	})

	// ==========================================================================
	// GETTERS
	// ==========================================================================

	const activeLayaways = computed(() => {
		return layaways.value.filter((l) => l.status === 'Active')
	})

	const overdueLayaways = computed(() => {
		return layaways.value.filter((l) => l.status === 'Overdue' || l.is_overdue)
	})

	const totalOutstanding = computed(() => {
		return layaways.value
			.filter((l) => l.status === 'Active')
			.reduce((sum, l) => sum + (l.balance_amount || 0), 0)
	})

	// ==========================================================================
	// ACTIONS
	// ==========================================================================

	async function fetchLayaways(filterParams = {}) {
		loading.value = true
		error.value = null
		try {
			const result = await layawaysResource.submit({
				...filters.value,
				...filterParams,
			})
			layaways.value = result.layaways || result || []
			return layaways.value
		} catch (e) {
			error.value = e.message || 'Failed to fetch layaways'
			console.error('Failed to fetch layaways:', e)
			return []
		} finally {
			loading.value = false
		}
	}

	async function fetchLayawayDetails(layawayId) {
		loading.value = true
		error.value = null
		try {
			const result = await layawayDetailsResource.submit({ layaway_id: layawayId })
			currentLayaway.value = result
			return result
		} catch (e) {
			error.value = e.message || 'Failed to fetch layaway details'
			console.error('Failed to fetch layaway details:', e)
			return null
		} finally {
			loading.value = false
		}
	}

	async function fetchCustomerLayaways(customer) {
		loading.value = true
		error.value = null
		try {
			const result = await customerLayawaysResource.submit({ customer })
			return result.layaways || result || []
		} catch (e) {
			error.value = e.message || 'Failed to fetch customer layaways'
			console.error('Failed to fetch customer layaways:', e)
			return []
		} finally {
			loading.value = false
		}
	}

	async function processPayment(layawayId, paymentAmount, modeOfPayment) {
		loading.value = true
		error.value = null
		try {
			const result = await processPaymentResource.submit({
				layaway_id: layawayId,
				payment_amount: paymentAmount,
				mode_of_payment: modeOfPayment,
			})
			// Refresh layaway details after payment
			if (result.success) {
				await fetchLayawayDetails(layawayId)
			}
			return result
		} catch (e) {
			error.value = e.message || 'Failed to process payment'
			console.error('Failed to process payment:', e)
			throw e
		} finally {
			loading.value = false
		}
	}

	async function cancelLayaway(layawayId, reason = '') {
		loading.value = true
		error.value = null
		try {
			const result = await cancelLayawayResource.submit({
				layaway_id: layawayId,
				reason,
			})
			// Refresh layaways list after cancellation
			if (result.success) {
				await fetchLayaways()
			}
			return result
		} catch (e) {
			error.value = e.message || 'Failed to cancel layaway'
			console.error('Failed to cancel layaway:', e)
			throw e
		} finally {
			loading.value = false
		}
	}

	function clearCurrentLayaway() {
		currentLayaway.value = null
	}

	function setFilters(newFilters) {
		filters.value = { ...filters.value, ...newFilters }
	}

	function clearFilters() {
		filters.value = {
			status: '',
			customer: '',
			search: '',
		}
	}

	return {
		// State
		layaways,
		currentLayaway,
		loading,
		error,
		filters,

		// Getters
		activeLayaways,
		overdueLayaways,
		totalOutstanding,

		// Actions
		fetchLayaways,
		fetchLayawayDetails,
		fetchCustomerLayaways,
		processPayment,
		cancelLayaway,
		clearCurrentLayaway,
		setFilters,
		clearFilters,
	}
})
