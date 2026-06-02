/**
 * useRAGQuery — wraps the AI insights API with loading/error/retry.
 * Plan §8.8. Used by AIInsightsTab.
 */
import { ref } from 'vue'
import { call } from 'frappe-ui'

export function useRAGQuery() {
	const data = ref(null)
	const loading = ref(false)
	const error = ref(null)
	const lastFetched = ref(0)
	const CACHE_MS = 55_000  // 55s, slightly less than server's 60min but with shorter client cache

	async function fetchInsights({ scope = 'today', focus = null, force = false } = {}) {
		if (!force && data.value && Date.now() - lastFetched.value < CACHE_MS) {
			return data.value
		}
		loading.value = true
		error.value = null
		try {
			const res = await call('zevar_core.api.analytics_hub.get_rag_insights', { scope, focus })
			data.value = res
			lastFetched.value = Date.now()
			return res
		} catch (e) {
			error.value = e?.message || 'Failed to fetch AI insights'
			throw e
		} finally {
			loading.value = false
		}
	}

	async function submitFeedback(insightId, rating, note = '') {
		return call('zevar_core.api.analytics_hub.submit_insight_feedback', { insight_id: insightId, rating, note })
	}

	return { data, loading, error, lastFetched, fetchInsights, submitFeedback }
}
