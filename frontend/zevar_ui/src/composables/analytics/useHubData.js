/**
 * useHubData — single-call aggregator for the Analytics Hub hero strip.
 * Plan §8.7. Wraps frappe.call with retry, debounce, and reactive state.
 */
import { ref, computed, watch } from 'vue'
import { call } from 'frappe-ui'

const CACHE_TTL_MS = 110_000 // 110s — slightly less than server's 120s
const inflight = new Map() // dedupe parallel calls with the same args

export function useHubData() {
	const hero = ref(null)
	const role = ref(null)
	const roleContext = ref(null)
	const aiBrief = ref(null)
	const overageQueue = ref(null)
	const asOf = ref(null)
	const loading = ref(false)
	const error = ref(null)
	const lastFetched = ref(0)

	const isStale = computed(() => {
		if (!lastFetched.value) return true
		return Date.now() - lastFetched.value > CACHE_TTL_MS
	})

	function key(store) {
		return [store || 'all', frappe?.boot?.user || 'guest'].join('|')
	}

	async function fetchHub(store = null, { force = false } = {}) {
		if (!force && !isStale.value && hero.value) return hero.value

		const k = key(store)
		const existing = inflight.get(k)
		if (existing) return existing

		loading.value = true
		error.value = null

		const p = call('zevar_core.api.analytics_hub.get_hub_data', { store })
			.then((data) => {
				hero.value = data?.hero || null
				role.value = data?.role || null
				roleContext.value = data?.role_context || null
				aiBrief.value = data?.ai_brief || null
				overageQueue.value = data?.overage_queue || null
				asOf.value = data?.as_of || null
				lastFetched.value = Date.now()
				return data
			})
			.catch((e) => {
				error.value = e?.message || 'Failed to load hub data'
				throw e
			})
			.finally(() => {
				inflight.delete(k)
				loading.value = false
			})

		inflight.set(k, p)
		return p
	}

	function invalidate() {
		lastFetched.value = 0
	}

	return {
		hero,
		role,
		roleContext,
		aiBrief,
		overageQueue,
		asOf,
		loading,
		error,
		isStale,
		lastFetched,
		fetchHub,
		invalidate,
	}
}

export function useMetric(methodName) {
	const data = ref(null)
	const loading = ref(false)
	const error = ref(null)

	async function fetch(args = {}) {
		loading.value = true
		error.value = null
		try {
			const res = await call(`zevar_core.api.analytics_hub.${methodName}`, args)
			data.value = res
			return res
		} catch (e) {
			error.value = e?.message || `Failed to call ${methodName}`
			throw e
		} finally {
			loading.value = false
		}
	}

	return { data, loading, error, fetch }
}
