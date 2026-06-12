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
	if (purity === null || purity === undefined) return purity
	const purityStr = String(purity).toLowerCase().trim()
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
		'925': '925 Sterling',
		'sterling': '925 Sterling',
	}
	return map[purityStr] || purity
}

export const useGoldStore = defineStore('gold', () => {
	// ==========================================================================
	// STATE
	// ==========================================================================

	// Holds rates like { "Yellow Gold-18Kt": 75.00, "Silver-925 Sterling": 1.20 }
	const rates = ref({})
	// Holds trends like { "Yellow Gold-18Kt": { trend: "up", change_pct: 0.25 } }
	const trends = ref({})
	const lastUpdated = ref(null)
	const isStale = ref(false)
	const rateSource = ref('unknown')
	const lastError = ref(null)

	// ==========================================================================
	// RESOURCES
	// ==========================================================================

	const fetchRates = createResource({
		url: 'zevar_core.api.pricing.get_live_metal_rates',
		onSuccess(data) {
			const result = data
			if (!result || !result.rates) return

			const newRates = {}
			const newTrends = {}
			for (const [metal, purities] of Object.entries(result.rates)) {
				if (!metal || metal === 'null' || !Array.isArray(purities)) continue

				for (const p of purities) {
					const normalizedPurity = normalizePurity(p.purity)
					const rate = Number(p.rate_per_gram || 0)
					if (!normalizedPurity || rate <= 0) continue

					const key = `${metal}-${normalizedPurity}`

					const rateObj = {
						rate_per_gram: rate,
						change_pct: p.change_pct || 0,
						change_amount: p.change_amount || 0,
						trend: p.trend || 'none',
					}
					const trendObj = {
						trend: p.trend || 'flat',
						change_pct: p.change_pct || 0,
						change_amount: p.change_amount || 0,
					}

					// Store the full object instead of just rate_per_gram
					if (!newRates[key]) {
						newRates[key] = rateObj
					} else {
						const current = newRates[key]
						const currentHasTrend =
							current.trend && current.trend !== 'none' && current.trend !== 'flat'
						const newHasTrend = p.trend && p.trend !== 'none' && p.trend !== 'flat'

						if (newHasTrend && !currentHasTrend) {
							newRates[key] = rateObj
						} else if (!newHasTrend && currentHasTrend) {
							// Keep current
						} else {
							// Prefer higher rate, or if rates are equal, prefer the one with a non-zero change_pct
							if (rate > current.rate_per_gram) {
								newRates[key] = rateObj
							} else if (
								rate === current.rate_per_gram &&
								Math.abs(rateObj.change_pct) > Math.abs(current.change_pct)
							) {
								newRates[key] = rateObj
							}
						}
					}

					// Capture trend data from server
					if (!newTrends[key]) {
						newTrends[key] = trendObj
					} else {
						const current = newTrends[key]
						const currentHasTrend =
							current.trend && current.trend !== 'none' && current.trend !== 'flat'
						const newHasTrend = p.trend && p.trend !== 'none' && p.trend !== 'flat'

						if (newHasTrend && !currentHasTrend) {
							newTrends[key] = trendObj
						} else if (!newHasTrend && currentHasTrend) {
							// Keep current
						} else {
							if (Math.abs(trendObj.change_pct) > Math.abs(current.change_pct)) {
								newTrends[key] = trendObj
							}
						}
					}
				}
			}
			rates.value = newRates
			trends.value = newTrends
			lastUpdated.value = result.last_updated ? new Date(result.last_updated) : new Date()
			isStale.value = result.is_stale || false
			rateSource.value = result.source || 'unknown'
			lastError.value = null
		},
		onError() {
			lastError.value = 'Failed to fetch live rates'
			isStale.value = true
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

	function refreshRates() {
		return fetchRates.fetch()
	}

	function stopPolling() {
		if (pollingInterval) {
			clearInterval(pollingInterval)
			pollingInterval = null
		}
	}

	return {
		rates,
		trends,
		lastUpdated,
		isStale,
		rateSource,
		lastError,
		refreshRates,
		startPolling,
		stopPolling,
	}
})
