import { ref, watch, onBeforeUnmount } from 'vue'
import { createResource } from 'frappe-ui'
import { usePolling } from './usePolling'
import { useTimeStore } from '@/stores/time'

/**
 * useDashboardData — the standard dashboard fetch wrapper.
 *
 * Wraps a frappe-ui resource with shared loading/error/refresh, optional
 * exponential-backoff polling (usePolling), and auto-refetch when the global
 * time store range changes (respectTime). Use this instead of raw fetch()+CSRF
 * so the dashboards share one HTTP client and one time context.
 *
 * @param {string} method dotted frappe whitelisted method, e.g.
 *   'zevar_core.api.command_center.get_wall_state'
 * @param {Object} opts { params={}, auto=true, poll=0, respectTime=true }
 * @returns {{ data, loading, error, refresh }}
 *
 * Example:
 *   const { data, loading, refresh } = useDashboardData(
 *     'zevar_core.api.sales_monitor.get_summary',
 *     { params: { store: 'NY-01' }, poll: 30000 }
 *   )
 */
export function useDashboardData(method, opts = {}) {
	const { params = {}, auto = true, poll = 0, respectTime = true } = opts

	const loading = ref(false)
	const error = ref(null)

	const resource = createResource({
		url: method,
		auto,
		onError: (e) => {
			error.value = e
		},
	})

	const data = resource?.data ?? ref(null)

	async function refresh(extraParams = {}) {
		loading.value = true
		error.value = null
		try {
			await resource.submit({ ...params, ...extraParams })
		} catch (e) {
			error.value = e
		} finally {
			loading.value = false
		}
	}

	// Polling fallback (exponential backoff, paused-when-hidden).
	let poller = null
	if (poll && poll > 0) {
		poller = usePolling(() => refresh(), { baseDelay: poll })
	}

	// Re-fetch when the global time range changes.
	let unwatch = null
	if (respectTime) {
		try {
			const time = useTimeStore()
			unwatch = watch(
				() => time.range,
				() => refresh(),
				{ deep: true }
			)
		} catch {
			// pinia not active in this context (e.g. outside a component) -> skip
		}
	}

	onBeforeUnmount(() => {
		if (poller) poller.pause()
		if (unwatch) unwatch()
	})

	return { data, loading, error, refresh }
}
