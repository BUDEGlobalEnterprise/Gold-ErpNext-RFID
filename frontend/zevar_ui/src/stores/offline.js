/**
 * Offline Store — Reactive online/offline state + sync management
 *
 * Tracks connectivity, pending order count, and drives the OfflineIndicator.
 */
import { defineStore } from 'pinia'
import { ref, computed, onUnmounted } from 'vue'
import {
	cacheCatalog,
	getCachedCatalog,
	getCatalogCount,
	getPendingOrders,
	queueOfflineOrder,
	markOrderSynced,
	markOrderFailed,
	clearSyncedOrders,
	cacheSetting,
	getCachedSetting,
} from '@/services/OfflineDB.js'

export const useOfflineStore = defineStore('offline', () => {
	const isOnline = ref(navigator.onLine)
	const pendingCount = ref(0)
	const syncing = ref(false)
	const lastSyncTime = ref(null)
	const catalogCachedCount = ref(0)

	// ── Connectivity listeners ──
	function handleOnline() {
		isOnline.value = true
		// Auto-sync when coming back online
		syncPendingOrders()
	}

	function handleOffline() {
		isOnline.value = false
	}

	function init() {
		window.addEventListener('online', handleOnline)
		window.addEventListener('offline', handleOffline)
		isOnline.value = navigator.onLine
		refreshPendingCount()
		refreshCatalogCount()
	}

	function destroy() {
		window.removeEventListener('online', handleOnline)
		window.removeEventListener('offline', handleOffline)
	}

	// ── Pending Orders ──
	async function refreshPendingCount() {
		try {
			const orders = await getPendingOrders()
			pendingCount.value = orders.length
		} catch {
			pendingCount.value = 0
		}
	}

	async function addPendingOrder(orderData) {
		await queueOfflineOrder(orderData)
		await refreshPendingCount()
	}

	async function syncPendingOrders() {
		if (syncing.value || !isOnline.value) return

		syncing.value = true
		try {
			const orders = await getPendingOrders()
			if (orders.length === 0) {
				syncing.value = false
				return
			}

			for (const order of orders) {
				try {
					const response = await fetch(
						'/api/method/zevar_core.api.pos.create_pos_invoice',
						{
							method: 'POST',
							headers: {
								'Content-Type': 'application/json',
								'X-Frappe-CSRF-Token': window.csrf_token || '',
							},
							body: JSON.stringify(order.payload),
						}
					)

					if (response.ok) {
						await markOrderSynced(order.id)
					} else {
						const errData = await response.json().catch(() => ({}))
						await markOrderFailed(
							order.id,
							errData.message || `HTTP ${response.status}`
						)
					}
				} catch (e) {
					await markOrderFailed(order.id, e.message)
				}
			}

			await clearSyncedOrders()
			lastSyncTime.value = new Date().toISOString()
		} finally {
			syncing.value = false
			await refreshPendingCount()
		}
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

	// ── Settings Cache ──
	async function cacheSettingValue(key, value) {
		return cacheSetting(key, value)
	}

	async function getCachedSettingValue(key) {
		return getCachedSetting(key)
	}

	// ── Status computed ──
	const statusLabel = computed(() => {
		if (!isOnline.value) return 'Offline'
		if (syncing.value) return 'Syncing...'
		if (pendingCount.value > 0) return `${pendingCount.value} pending`
		return 'Online'
	})

	const statusColor = computed(() => {
		if (!isOnline.value) return 'red'
		if (syncing.value) return 'amber'
		if (pendingCount.value > 0) return 'amber'
		return 'green'
	})

	return {
		// State
		isOnline,
		pendingCount,
		syncing,
		lastSyncTime,
		catalogCachedCount,
		// Computed
		statusLabel,
		statusColor,
		// Actions
		init,
		destroy,
		refreshPendingCount,
		addPendingOrder,
		syncPendingOrders,
		updateCatalogCache,
		getOfflineCatalog,
		refreshCatalogCount,
		cacheSettingValue,
		getCachedSettingValue,
	}
})
