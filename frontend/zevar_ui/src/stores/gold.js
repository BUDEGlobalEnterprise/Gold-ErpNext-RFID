/**
 * Gold Store
 *
 * Manages live gold rate polling and caching for different metal/purity combinations.
 * Uses the server-side pricing API to bypass doctype-level permission restrictions,
 * ensuring all logged-in roles (Employee, ESS, Sales User, etc.) can see live rates.
 */

import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

export const useGoldStore = defineStore('gold', () => {
	// ==========================================================================
	// STATE
	// ==========================================================================

	// Holds rates like { "Gold-22K": 75.00, "Silver-925": 1.20 }
	const rates = ref({})
	const lastUpdated = ref(null)

	// ==========================================================================
	// RESOURCES
	// ==========================================================================

	const fetchRates = createResource({
		url: 'zevar_core.api.pricing.get_live_metal_rates',
		onSuccess(data) {
			const result = data?.message || data
			if (!result || !result.rates) return

			const newRates = {}
			// Convert grouped format: { "Yellow Gold": [{purity, rate_per_gram}] }
			// to flat map: { "Yellow Gold-24K": 95.50 }
			for (const [metal, purities] of Object.entries(result.rates)) {
				for (const p of purities) {
					const key = `${metal}-${p.purity}`
					if (!newRates[key]) {
						newRates[key] = p.rate_per_gram
					}
				}
			}
			rates.value = newRates
			lastUpdated.value = new Date()
		},
	})

	// ==========================================================================
	// ACTIONS
	// ==========================================================================

	let pollingInterval = null

	function startPolling() {
		if (pollingInterval) return
		fetchRates.fetch()
		pollingInterval = setInterval(() => {
			fetchRates.fetch()
		}, 60000)
	}

	function stopPolling() {
		if (pollingInterval) {
			clearInterval(pollingInterval)
			pollingInterval = null
		}
	}

	return {
		rates,
		lastUpdated,
		startPolling,
		stopPolling,
	}
})
