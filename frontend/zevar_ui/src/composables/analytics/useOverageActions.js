/**
 * useOverageActions — wraps the 5 clearance action endpoints.
 * Plan §8.9 / §10.4.
 */
import { ref } from 'vue'
import { call } from 'frappe-ui'

export function useOverageActions() {
	const loading = ref(false)
	const error = ref(null)
	const lastResult = ref(null)

	async function submitAction(actionType, items, params = {}) {
		loading.value = true
		error.value = null
		try {
			const res = await call('zevar_core.api.analytics_hub.submit_overage_action', {
				action_type: actionType,
				items: Array.isArray(items) ? items : [items],
				params,
			})
			lastResult.value = res
			return res
		} catch (e) {
			error.value = e?.message || `Action ${actionType} failed`
			throw e
		} finally {
			loading.value = false
		}
	}

	async function score({ days_threshold = 90, min_score = 50, limit = 100, offset = 0 } = {}) {
		loading.value = true
		error.value = null
		try {
			return await call('zevar_core.api.analytics_hub.score_overage', {
				days_threshold,
				min_score,
				limit,
				offset,
			})
		} catch (e) {
			error.value = e?.message || 'Failed to score overage'
			throw e
		} finally {
			loading.value = false
		}
	}

	return { loading, error, lastResult, submitAction, score }
}
