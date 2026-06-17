import { ref } from 'vue'

/**
 * usePolling — exponential-backoff refresh that pauses when the tab is hidden.
 *
 * @param {Function} fn async function to run on each tick
 * @param {Object} opts { baseDelay=10000, maxDelay=60000, multiplier=1.5, pausedWhenHidden=true }
 * @returns {{ currentDelay, pause, resume }}
 *
 * On success the interval resets to baseDelay; on error it backs off
 * (baseDelay * multiplier, capped at maxDelay) so a struggling server isn't
 * hammered. When the tab is hidden the next tick is deferred 1s until visible.
 */
export function usePolling(fn, opts = {}) {
	const { baseDelay = 10000, maxDelay = 60000, multiplier = 1.5, pausedWhenHidden = true } = opts

	let timer = null
	let nextDelay = baseDelay
	const currentDelay = ref(baseDelay)

	function clear() {
		if (timer) {
			clearTimeout(timer)
			timer = null
		}
	}

	function schedule(delay) {
		clear()
		currentDelay.value = delay
		timer = setTimeout(async () => {
			if (pausedWhenHidden && typeof document !== 'undefined' && document.hidden) {
				schedule(1000)
				return
			}
			try {
				await fn()
				nextDelay = baseDelay // success -> reset
			} catch {
				nextDelay = Math.min(nextDelay * multiplier, maxDelay) // error -> backoff
			}
			schedule(nextDelay)
		}, delay)
	}

	function pause() {
		clear()
	}
	function resume() {
		schedule(nextDelay)
	}

	return { currentDelay, pause, resume }
}
