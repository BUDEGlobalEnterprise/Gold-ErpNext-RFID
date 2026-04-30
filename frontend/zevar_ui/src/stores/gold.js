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

/**
 * Normalize purity strings to canonical Kt form.
 * Handles common variants: "18K" → "18Kt", "10k" → "10Kt", etc.
 */
function normalizePurity(purity) {
	if (!purity) return purity
	const map = {
		'24k': '24Kt',
		'24kt': '24Kt',
		'22k': '22Kt',
		'22kt': '22Kt',
		'18k': '18Kt',
		'18kt': '18Kt',
		'14k': '14Kt',
		'14kt': '14Kt',
		'10k': '10Kt',
		'10kt': '10Kt',
		'999 sterling': '999 Fine',
		925: '925 Sterling',
		sterling: '925 Sterling',
	}
	return map[purity.toLowerCase().trim()] || purity
}

export const useGoldStore = defineStore('gold', () => {
	// ==========================================================================
	// STATE
	// ==========================================================================

	// Holds rates like { "Yellow Gold-18Kt": 75.00, "Silver-925 Sterling": 1.20 }
	const rates = ref({})
	const lastUpdated = ref(null)

	// ==========================================================================
	// RESOURCES
	// ==========================================================================

	const fetchRates = createResource({
		url: 'zevar_core.api.pricing.get_live_metal_rates',
		method: 'GET',
		onSuccess(data) {
			const result = data?.message || data
			if (!result || !result.rates) return

			const newRates = {}
			for (const [metal, purities] of Object.entries(result.rates)) {
				for (const p of purities) {
					const normalizedPurity = normalizePurity(p.purity)
					const key = `${metal}-${normalizedPurity}`
					if (!newRates[key] || p.rate_per_gram > newRates[key]) {
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
