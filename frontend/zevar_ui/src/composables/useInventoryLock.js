import { ref, onUnmounted } from 'vue'
import { useInventoryV2Store } from '../stores/inventoryV2'

/**
 * Composable for pessimistic inventory locking.
 *
 * Usage:
 *   const { lock, release, isLocked, lockInfo } = useInventoryLock()
 *   await lock('SN-001')
 *   // ... do work ...
 *   await release()
 */
export function useInventoryLock() {
	const store = useInventoryV2Store()

	const isLocked = ref(false)
	const lockInfo = ref(null)
	const lockError = ref(null)
	const currentSerial = ref(null)
	const currentToken = ref(null)

	let releaseTimer = null

	async function lock(serialNo, owner) {
		lockError.value = null
		try {
			const result = await store.acquireLock(serialNo, owner)
			if (result?.success) {
				isLocked.value = true
				currentSerial.value = serialNo
				currentToken.value = result.lock_token
				lockInfo.value = { serial_no: serialNo, token: result.lock_token }
				// Auto-release after 5 minutes as safety net
				releaseTimer = setTimeout(() => release(), 5 * 60 * 1000)
			}
			return result
		} catch (e) {
			lockError.value = e.message || String(e)
			isLocked.value = false
			throw e
		}
	}

	async function release() {
		if (releaseTimer) {
			clearTimeout(releaseTimer)
			releaseTimer = null
		}
		if (!currentSerial.value) return { success: true }

		try {
			const result = await store.releaseLock(currentSerial.value, currentToken.value)
			isLocked.value = false
			currentSerial.value = null
			currentToken.value = null
			lockInfo.value = null
			return result
		} catch (e) {
			lockError.value = e.message || String(e)
			throw e
		}
	}

	async function check(serialNo) {
		const result = await store.checkLock(serialNo)
		return result
	}

	// Cleanup on unmount
	onUnmounted(() => {
		if (isLocked.value && currentSerial.value) {
			release()
		}
	})

	return {
		isLocked,
		lockInfo,
		lockError,
		currentSerial,
		lock,
		release,
		check,
	}
}
