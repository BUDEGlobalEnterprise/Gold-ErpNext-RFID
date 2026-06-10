/**
 * Offline Store — Reactive online/offline state + sync management
 *
 * Tracks connectivity, pending order count, and drives the OfflineIndicator.
 * Supports idempotency keys, exponential backoff retry, and conflict resolution.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
	cacheCatalog,
	getCachedCatalog,
	getCatalogCount,
	getPendingOrders,
	queueOfflineOrder,
	markOrderSynced,
	markOrderFailed,
	markOrderConflict,
	updateOrderForRetry,
	markOrderDead,
	clearSyncedOrders,
	cacheSetting,
	getCachedSetting,
	getOrdersByStatus,
	isCatalogStale,
	deleteOfflineOrder,
} from '@/services/OfflineDB.js'

const MAX_RETRY_ATTEMPTS = 5
const RETRY_CHECK_INTERVAL = 60_000 // 60 seconds

export const useOfflineStore = defineStore('offline', () => {
	const isOnline = ref(navigator.onLine)
	const pendingCount = ref(0)
	const failedCount = ref(0)
	const conflictCount = ref(0)
	const syncedCount = ref(0)
	const catalogCachedCount = ref(0)
	const syncing = ref(false)
	const lastSyncTime = ref(null)
	const lastSyncResults = ref([])

	let retryInterval = null

	// ── Connectivity listeners ──
	function handleOnline() {
		isOnline.value = true
		syncPendingOrders()
		_refreshCatalogIfStale()
	}

	function handleOffline() {
		isOnline.value = false
	}

	function init() {
		window.addEventListener('online', handleOnline)
		window.addEventListener('offline', handleOffline)
		isOnline.value = navigator.onLine
		refreshCounts()
		refreshCatalogCount()
		if (isOnline.value) _startRetryLoopIfNeeded()
	}

	function destroy() {
		window.removeEventListener('online', handleOnline)
		window.removeEventListener('offline', handleOffline)
		_stopRetryLoop()
	}

	// ── Pending Orders ──

	async function refreshCounts() {
		try {
			const [pending, failed, conflicts, synced] = await Promise.all([
				getOrdersByStatus('pending'),
				getOrdersByStatus('failed'),
				getOrdersByStatus('conflict'),
				getOrdersByStatus('synced'),
			])
			pendingCount.value = pending.length
			failedCount.value = failed.length
			conflictCount.value = conflicts.length
			syncedCount.value = synced.length
		} catch {
			pendingCount.value = 0
			failedCount.value = 0
			conflictCount.value = 0
			syncedCount.value = 0
		}
	}

	async function refreshPendingCount() {
		await refreshCounts()
	}

	async function addPendingOrder(orderData) {
		const record = await queueOfflineOrder(orderData)
		await refreshCounts()
		return record
	}

	async function syncPendingOrders(force = false) {
		if (syncing.value || !isOnline.value) return

		syncing.value = true
		lastSyncResults.value = []

		try {
			if (force) {
				const db = await import('@/services/OfflineDB.js')
				const failed = await db.getOrdersByStatus('failed')
				for (const order of failed) {
					if ((order.attempts || 0) < MAX_RETRY_ATTEMPTS) {
						await db.updateOrderForRetry(order.id)
					}
				}
			}

			const orders = await getPendingOrders()
			if (orders.length === 0) {
				syncing.value = false
				return
			}

			const results = []
			for (const order of orders) {
				const result = await _syncSingleOrder(order)
				results.push({ id: order.id, ...result })
			}

			lastSyncResults.value = results
			await clearSyncedOrders()
			lastSyncTime.value = new Date().toISOString()

			// Notify service worker about completed sync
			if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
				navigator.serviceWorker.controller.postMessage({ type: 'SYNC_COMPLETE' })
			}
		} finally {
			syncing.value = false
			await refreshCounts()
		}
	}

	async function _syncSingleOrder(order) {
		const mode = order.mode || 'sale'
		const methodPath = _getSyncMethod(mode)
		const syncPayload = _buildSyncPayload(order, mode)

		// Pre-validation to prevent junk requests
		if (mode === 'layaway' && !syncPayload.layaway_id) {
			const errMessage = 'Missing layaway contract identifier.'
			await markOrderConflict(order.id, 'missing_reference', errMessage)
			return { status: 'conflict', conflictType: 'missing_reference', message: errMessage }
		}
		if (mode === 'repair' && !syncPayload.repair_order) {
			const errMessage = 'Missing repair order reference.'
			await markOrderConflict(order.id, 'missing_reference', errMessage)
			return { status: 'conflict', conflictType: 'missing_reference', message: errMessage }
		}

		// Attach idempotency key so backend can deduplicate
		syncPayload.idempotency_key = order.idempotency_key || ''

		try {
			// Use frappe.call instead of raw fetch — it handles CSRF,
			// form-encoding, and response parsing correctly.
			await frappe.call(methodPath, syncPayload)

			await markOrderSynced(order.id)
			return { status: 'synced' }
		} catch (e) {
			const errMessage = e?.message || String(e)

			// Detect conflict errors from server messages
			if (_isConflictError({ message: errMessage })) {
				await markOrderConflict(order.id, 'stock_unavailable', errMessage)
				return {
					status: 'conflict',
					conflictType: 'stock_unavailable',
					message: errMessage,
				}
			}

			// Validation errors (4xx-equivalent from frappe.throw)
			const isValidationError =
				e?.exc_type === 'ValidationError' ||
				errMessage.toLowerCase().includes('validation') ||
				errMessage.toLowerCase().includes('not found') ||
				errMessage.toLowerCase().includes('required') ||
				errMessage.toLowerCase().includes('must be')

			if (isValidationError) {
				if ((order.attempts || 0) + 1 >= MAX_RETRY_ATTEMPTS) {
					await markOrderDead(order.id)
					return { status: 'dead_letter', message: errMessage }
				}
				await markOrderFailed(order.id, errMessage)
				return { status: 'failed', message: errMessage }
			}

			// Network / server errors — retry with backoff
			await _retryWithBackoff(order)
			return { status: 'retrying', message: errMessage }
		}
	}

	function _isConflictError(errData) {
		const msg = (errData.message || '').toLowerCase()
		return (
			!!errData._conflict_type ||
			msg.includes('not available') ||
			msg.includes('not enough stock') ||
			msg.includes('insufficient stock') ||
			msg.includes('stock unavailable') ||
			msg.includes('already been sold') ||
			msg.includes('serial no') ||
			msg.includes('reserved for another') ||
			msg.includes('item.*not found')
		)
	}

	async function _retryWithBackoff(order) {
		const attempts = (order.attempts || 0) + 1
		if (attempts >= MAX_RETRY_ATTEMPTS) {
			await markOrderDead(order.id)
		} else {
			await updateOrderForRetry(order.id)
		}
	}

	function _getSyncMethod(mode) {
		switch (mode) {
			case 'layaway':
				return 'zevar_core.api.layaway.process_split_layaway_payment'
			case 'repair':
				return 'zevar_core.api.add_repair_payment'
			default:
				return 'zevar_core.api.pos.create_pos_invoice'
		}
	}

	function _buildSyncPayload(order, mode) {
		const p = order.payload || {}

		if (mode === 'layaway') {
			return {
				layaway_id: p.layaway_id || '',
				payments: p.payments || '[]',
			}
		}

		if (mode === 'repair') {
			return {
				repair_order: p.repair_order || '',
				amount: p.amount || 0,
				payment_method: p.payment_method || 'Cash',
			}
		}

		// Sale mode — frappe.whitelist expects each param as a flat kwarg.
		// The payload already has items/payments as JSON strings, customer,
		// warehouse, tax_exempt etc. — just pass them through.
		const result = {
			items: p.items || '[]',
			payments: p.payments || '[]',
			customer: p.customer || 'Walk-In Customer',
			warehouse: p.warehouse || '',
			tax_exempt: p.tax_exempt || false,
		}
		if (p.gift_card_number) result.gift_card_number = p.gift_card_number
		if (p.salespersons) result.salespersons = p.salespersons
		if (p.trade_ins) result.trade_ins = p.trade_ins
		return result
	}

	// ── Retry Loop ──

	function _startRetryLoopIfNeeded() {
		if (retryInterval) return

		const hasWork = pendingCount.value > 0 || failedCount.value > 0
		if (!hasWork) return

		retryInterval = setInterval(async () => {
			if (!isOnline.value || syncing.value) return

			const failed = await getOrdersByStatus('failed')
			let needsRetry = false

			for (const order of failed) {
				if ((order.attempts || 0) >= MAX_RETRY_ATTEMPTS) {
					await markOrderDead(order.id)
					continue
				}

				const waitMs = Math.pow(2, order.attempts || 1) * 30_000
				const lastAttempt = order.last_attempt || order.created_at || 0
				if (Date.now() - lastAttempt >= waitMs) {
					const { updateOrderForRetry } = await import('@/services/OfflineDB.js')
					await updateOrderForRetry(order.id)
					needsRetry = true
				}
			}

			if (needsRetry) {
				await syncPendingOrders()
			}

			await refreshCounts()

			// Stop loop if nothing left to retry
			const remaining = await getOrdersByStatus('failed')
			const pending = await getOrdersByStatus('pending')
			if (remaining.length === 0 && pending.length === 0) {
				_stopRetryLoop()
			}
		}, RETRY_CHECK_INTERVAL)
	}

	function _stopRetryLoop() {
		if (retryInterval) {
			clearInterval(retryInterval)
			retryInterval = null
		}
	}

	// ── Conflict Resolution ──

	async function resolveConflict(orderId, resolution, updatedPayload) {
		const db = await import('@/services/OfflineDB.js')
		if (resolution === 'cancel') {
			await db.markOrderSynced(orderId) // treat as resolved
		} else if (resolution === 'retry_modified' && updatedPayload) {
			// Update the payload and reset for retry
			await db.updateOrderForRetry(orderId)
			// Re-queue with updated payload
			const orders = await getOrdersByStatus('pending')
			const order = orders.find((o) => o.id === orderId)
			if (order) {
				order.payload = updatedPayload
				// Save updated order back to IndexedDB
				const { openDB } = await import('@/services/OfflineDB.js')
				const dbInstance = await openDB()
				const tx = dbInstance.transaction('pendingOrders', 'readwrite')
				tx.objectStore('pendingOrders').put(order)
				await new Promise((resolve, reject) => {
					tx.oncomplete = () => resolve()
					tx.onerror = () => reject(tx.error)
				})
			}
		} else if (resolution === 'escalate') {
			// Leave in conflict status for manager
		}

		await refreshCounts()
	}

	async function getConflicts() {
		return getOrdersByStatus('conflict')
	}

	async function getFailedOrders() {
		const [failed, dead] = await Promise.all([
			getOrdersByStatus('failed'),
			getOrdersByStatus('dead_letter'),
		])
		return [...failed, ...dead]
	}

	async function getPendingOrdersList() {
		return getOrdersByStatus('pending')
	}

	async function getSyncedOrders() {
		const db = await import('@/services/OfflineDB.js')
		const all = await db.getAllOfflineOrders()
		return all
			.filter((o) => o.status === 'synced')
			.sort((a, b) => (b.synced_at || 0) - (a.synced_at || 0))
	}

	async function deleteOrder(id) {
		await deleteOfflineOrder(id)
		await refreshCounts()
	}

	async function retryOrder(orderId) {
		const db = await import('@/services/OfflineDB.js')
		const dbInstance = await db.openDB()
		const tx = dbInstance.transaction('pendingOrders', 'readwrite')
		const store = tx.objectStore('pendingOrders')
		const request = store.get(orderId)
		await new Promise((resolve, reject) => {
			request.onsuccess = () => {
				const record = request.result
				if (record) {
					record.status = 'pending'
					record.attempts = 0
					record.next_retry = Date.now()
					store.put(record)
				}
				resolve()
			}
			request.onerror = () => reject(request.error)
		})
		await new Promise((resolve, reject) => {
			tx.oncomplete = () => resolve()
			tx.onerror = () => reject(tx.error)
		})
		await refreshCounts()
		await syncPendingOrders()
	}

	// ── Catalog Cache ──

	async function refreshCatalogCount() {
		try {
			catalogCachedCount.value = await getCatalogCount()
		} catch {
			catalogCachedCount.value = 0
		}
	}

	async function updateCatalogCache(items) {
		const count = await cacheCatalog(items)
		catalogCachedCount.value = count
		return count
	}

	async function getOfflineCatalog(searchTerm = '') {
		return getCachedCatalog(searchTerm)
	}

	async function _refreshCatalogIfStale() {
		try {
			if (await isCatalogStale()) {
				// Signal to POS page that catalog needs refresh
				window.dispatchEvent(new CustomEvent('zevar:catalog-stale'))
			}
		} catch {
			// ignore
		}
	}

	// ── Settings Cache ──

	async function cacheSettingValue(key, value) {
		return cacheSetting(key, value)
	}

	async function getCachedSettingValue(key) {
		return getCachedSetting(key)
	}

	// ── Status computed ──

	const totalUnresolved = computed(
		() => pendingCount.value + failedCount.value + conflictCount.value
	)

	const statusLabel = computed(() => {
		if (!isOnline.value) return 'Offline'
		if (syncing.value) return 'Syncing...'
		if (conflictCount.value > 0)
			return `${conflictCount.value} conflict${conflictCount.value > 1 ? 's' : ''}`
		if (pendingCount.value > 0) return `${pendingCount.value} pending`
		if (failedCount.value > 0) return `${failedCount.value} failed`
		return 'Online'
	})

	const statusColor = computed(() => {
		if (!isOnline.value) return 'red'
		if (conflictCount.value > 0) return 'red'
		if (syncing.value) return 'amber'
		if (pendingCount.value > 0 || failedCount.value > 0) return 'amber'
		return 'green'
	})

	return {
		// State
		isOnline,
		pendingCount,
		failedCount,
		conflictCount,
		syncedCount,
		catalogCachedCount,
		syncing,
		lastSyncTime,
		lastSyncResults,
		totalUnresolved,
		// Computed
		statusLabel,
		statusColor,
		// Actions
		init,
		destroy,
		refreshPendingCount,
		refreshCounts,
		addPendingOrder,
		syncPendingOrders,
		resolveConflict,
		getConflicts,
		getFailedOrders,
		getPendingOrdersList,
		getSyncedOrders,
		deleteOrder,
		retryOrder,
		updateCatalogCache,
		getOfflineCatalog,
		refreshCatalogCount,
		cacheSettingValue,
		getCachedSettingValue,
	}
})
