import { ref, computed, watch, onUnmounted } from 'vue'
import { call } from 'frappe-ui'
import { useTimeStore } from '@/stores/time'

const CACHE_TTL_MS = 110_000 // 110s
const inflight = new Map()

/**
 * useReportData - Aggregates reporting data with inflight deduplication,
 * caching, and automatic refetching based on the global time store.
 */
export function useReportData(methodName, options = { respectTime: true }) {
	const data = ref(null)
	const asOf = ref(null)
	const loading = ref(false)
	const error = ref(null)
	const lastFetched = ref(0)
	
	const timeStore = options.respectTime ? useTimeStore() : null

	const isStale = computed(() => {
		if (!lastFetched.value) return true
		return Date.now() - lastFetched.value > CACHE_TTL_MS
	})

	function key(store) {
		const base = [methodName, store || 'all', window.frappe?.boot?.user || 'guest']
		if (timeStore) {
			base.push(timeStore.range.from, timeStore.range.to)
		}
		return base.join('|')
	}

	async function fetchData(store = null, { force = false } = {}) {
		if (!force && !isStale.value && data.value) return data.value

		const k = key(store)
		const existing = inflight.get(k)
		if (existing) {
			loading.value = true
			try {
				const res = await existing
				data.value = res
				asOf.value = res?.as_of || null
				lastFetched.value = Date.now()
				error.value = null
				return res
			} catch (e) {
				error.value = e?.message || 'Failed to load report data'
				throw e
			} finally {
				loading.value = false
			}
		}

		loading.value = true
		error.value = null

		const args = { store }
		if (timeStore) {
			args.start_date = timeStore.range.from
			args.end_date = timeStore.range.to
		}

		// methodName is already the full dotted path (e.g.
		// zevar_core.api.report_center.get_executive_overview), so call it as-is —
		// prepending the module again would 404 every request (this was why the
		// report pages rendered empty).
		const p = call(methodName, args)
			.then((res) => {
				data.value = res
				asOf.value = res?.as_of || null
				lastFetched.value = Date.now()
				return res
			})
			.catch((e) => {
				error.value = e?.message || 'Failed to load report data'
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

	function refresh() {
		invalidate()
		return fetchData(null, { force: true })
	}

	let unwatch = null
	if (timeStore) {
		unwatch = watch(
			() => timeStore.range,
			() => {
				refresh().catch(() => {})
			},
			{ deep: true, immediate: true }
		)
	} else {
		refresh().catch(() => {})
	}

	onUnmounted(() => {
		if (unwatch) unwatch()
	})

	return {
		data,
		asOf,
		loading,
		error,
		isStale,
		lastFetched,
		fetchData,
		invalidate,
		refresh,
	}
}
