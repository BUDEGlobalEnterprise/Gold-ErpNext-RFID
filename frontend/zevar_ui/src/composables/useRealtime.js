import { onBeforeUnmount } from 'vue'

/**
 * useRealtime — the single realtime abstraction for the dashboards.
 *
 * Wraps frappe.realtime.on/off for a set of { event: handler } subscriptions,
 * drops events while the tab is hidden (resume on visibilitychange), and cleans
 * up on unmount. Migrate the per-dashboard subscriptions (CommandCenter,
 * EmployeeLiveMonitor, session) to this so they share one subscription model.
 *
 * @param {Object<string, Function>} handlers event name -> handler(data)
 * @param {Object} opts { pausedWhenHidden=true }
 *
 * Example:
 *   useRealtime({
 *     repair_live_event: onRepair,
 *     repair_anomaly_alert: onAlert,
 *   })
 */
export function useRealtime(handlers = {}, opts = {}) {
	const { pausedWhenHidden = true } = opts
	const rt = typeof window !== 'undefined' && window.frappe && window.frappe.realtime ? window.frappe.realtime : null

	function wrap(fn) {
		return (data) => {
			if (pausedWhenHidden && typeof document !== 'undefined' && document.hidden) return
			fn(data)
		}
	}

	const wrapped = {}
	for (const [event, fn] of Object.entries(handlers)) {
		wrapped[event] = wrap(fn)
		if (rt) rt.on(event, wrapped[event])
	}

	function onVisibilityChange() {
		// no-op while hidden (the wraps already drop events); nothing extra needed
	}
	if (pausedWhenHidden && typeof document !== 'undefined') {
		document.addEventListener('visibilitychange', onVisibilityChange)
	}

	onBeforeUnmount(() => {
		if (rt) {
			for (const [event, fn] of Object.entries(wrapped)) rt.off(event, fn)
		}
		if (typeof document !== 'undefined') {
			document.removeEventListener('visibilitychange', onVisibilityChange)
		}
	})
}
