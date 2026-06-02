import { ref } from 'vue'
import { useInventoryLock } from './useInventoryLock'

/**
 * Composable for pessimistic submit pattern:
 * 1. Acquire lock on serial
 * 2. Execute submit action
 * 3. Release lock
 *
 * Usage:
 *   const { submitting, error, pessimisticSubmit } = usePessimisticSubmit()
 *   await pessimisticSubmit('SN-001', () => store.createInvoice(...))
 */
export function usePessimisticSubmit() {
	const { lock, release, isLocked } = useInventoryLock()
	const submitting = ref(false)
	const error = ref(null)

	async function pessimisticSubmit(serialNo, action) {
		submitting.value = true
		error.value = null

		try {
			// Acquire lock
			await lock(serialNo)

			// Execute the action
			const result = await action()

			return result
		} catch (e) {
			error.value = e.message || String(e)
			throw e
		} finally {
			// Always release lock
			await release()
			submitting.value = false
		}
	}

	async function batchSubmit(serialNos, action) {
		submitting.value = true
		error.value = null

		try {
			// Lock all serials
			for (const sn of serialNos) {
				await lock(sn)
			}

			const result = await action()
			return result
		} catch (e) {
			error.value = e.message || String(e)
			throw e
		} finally {
			await release()
			submitting.value = false
		}
	}

	return {
		submitting,
		error,
		isLocked,
		pessimisticSubmit,
		batchSubmit,
	}
}
