/**
 * OfflineDB — IndexedDB wrapper for Zevar POS offline support
 *
 * Stores:
 *  - catalog: Cached item catalog for offline browsing
 *  - pendingOrders: Orders created while offline, queued for sync
 *  - settings: POS settings cache (tax rate, warehouse, etc.)
 */

const DB_NAME = 'zevar_pos'
const DB_VERSION = 2

let dbPromise = null

function openDB() {
	if (dbPromise) return dbPromise

	dbPromise = new Promise((resolve, reject) => {
		const request = indexedDB.open(DB_NAME, DB_VERSION)

		request.onupgradeneeded = (event) => {
			const db = event.target.result

			// Item catalog cache
			if (!db.objectStoreNames.contains('catalog')) {
				const catalog = db.createObjectStore('catalog', { keyPath: 'item_code' })
				catalog.createIndex('item_group', 'item_group', { unique: false })
				catalog.createIndex('item_name', 'item_name', { unique: false })
			}

			// Pending orders queued while offline
			if (!db.objectStoreNames.contains('pendingOrders')) {
				const orders = db.createObjectStore('pendingOrders', {
					keyPath: 'id',
					autoIncrement: true,
				})
				orders.createIndex('created_at', 'created_at', { unique: false })
				orders.createIndex('status', 'status', { unique: false })
				orders.createIndex('idempotency_key', 'idempotency_key', { unique: false })
			} else if (event.oldVersion < 2) {
				// v1→v2 migration: add idempotency_key index to existing store
				const orders = event.target.transaction.objectStore('pendingOrders')
				if (!orders.indexNames.contains('idempotency_key')) {
					orders.createIndex('idempotency_key', 'idempotency_key', { unique: false })
				}
			}

			// Key-value settings cache
			if (!db.objectStoreNames.contains('settings')) {
				db.createObjectStore('settings', { keyPath: 'key' })
			}

			// Cart snapshot for service worker access
			if (!db.objectStoreNames.contains('cartSnapshot')) {
				db.createObjectStore('cartSnapshot', { keyPath: 'id' })
			}
		}

		request.onsuccess = () => resolve(request.result)
		request.onerror = () => reject(request.error)
	})

	return dbPromise
}

// ── Catalog ──

export async function cacheCatalog(items) {
	const db = await openDB()
	const tx = db.transaction('catalog', 'readwrite')
	const store = tx.objectStore('catalog')

	// Clear stale data
	store.clear()

	for (const item of items) {
		store.put({
			item_code: item.item_code,
			item_name: item.item_name,
			item_group: item.item_group || '',
			description: item.description || '',
			rate: item.rate || item.standard_rate || 0,
			image: item.image || null,
			stock_qty: item.actual_qty || 0,
			uom: item.stock_uom || 'Nos',
			has_serial_no: item.has_serial_no || 0,
			barcode: item.barcode || null,
			cached_at: Date.now(),
		})
	}

	return new Promise((resolve, reject) => {
		tx.oncomplete = () => resolve(items.length)
		tx.onerror = () => reject(tx.error)
	})
}

export async function getCachedCatalog(searchTerm = '') {
	const db = await openDB()
	const tx = db.transaction('catalog', 'readonly')
	const store = tx.objectStore('catalog')
	const request = store.getAll()

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			let items = request.result
			if (searchTerm) {
				const term = searchTerm.toLowerCase()
				items = items.filter(
					(i) =>
						i.item_name.toLowerCase().includes(term) ||
						i.item_code.toLowerCase().includes(term) ||
						(i.barcode && i.barcode.toLowerCase().includes(term))
				)
			}
			resolve(items)
		}
		request.onerror = () => reject(request.error)
	})
}

export async function getCatalogCount() {
	const db = await openDB()
	const tx = db.transaction('catalog', 'readonly')
	const request = tx.objectStore('catalog').count()
	return new Promise((resolve, reject) => {
		request.onsuccess = () => resolve(request.result)
		request.onerror = () => reject(request.error)
	})
}

// ── Pending Orders ──

export async function queueOfflineOrder(orderData) {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readwrite')
	const store = tx.objectStore('pendingOrders')

	const idempotency_key = crypto.randomUUID()
	const record = {
		...orderData,
		idempotency_key,
		status: 'pending',
		mode: orderData.mode || 'sale',
		created_at: Date.now(),
		last_attempt: null,
		next_retry: Date.now(),
		attempts: 0,
		max_attempts: 5,
	}

	store.add(record)

	return new Promise((resolve, reject) => {
		tx.oncomplete = () => resolve(record)
		tx.onerror = () => reject(tx.error)
	})
}

export async function getPendingOrders() {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readonly')
	const request = tx.objectStore('pendingOrders').getAll()
	return new Promise((resolve, reject) => {
		request.onsuccess = () => resolve(request.result.filter((o) => o.status === 'pending'))
		request.onerror = () => reject(request.error)
	})
}

export async function markOrderSynced(id) {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readwrite')
	const store = tx.objectStore('pendingOrders')
	const request = store.get(id)

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			const record = request.result
			if (record) {
				record.status = 'synced'
				record.synced_at = Date.now()
				store.put(record)
			}
			tx.oncomplete = () => resolve(true)
		}
		tx.onerror = () => reject(tx.error)
	})
}

export async function markOrderFailed(id, error) {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readwrite')
	const store = tx.objectStore('pendingOrders')
	const request = store.get(id)

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			const record = request.result
			if (record) {
				record.status = 'failed'
				record.error = error
				record.attempts = (record.attempts || 0) + 1
				store.put(record)
			}
			tx.oncomplete = () => resolve(true)
		}
		tx.onerror = () => reject(tx.error)
	})
}

export async function clearSyncedOrders() {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readwrite')
	const store = tx.objectStore('pendingOrders')
	const request = store.getAll()

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			for (const record of request.result) {
				if (record.status === 'synced') {
					store.delete(record.id)
				}
			}
			tx.oncomplete = () => resolve(true)
		}
		tx.onerror = () => reject(tx.error)
	})
}

// ── Settings Cache ──

export async function cacheSetting(key, value) {
	const db = await openDB()
	const tx = db.transaction('settings', 'readwrite')
	tx.objectStore('settings').put({ key, value, cached_at: Date.now() })
	return new Promise((resolve, reject) => {
		tx.oncomplete = () => resolve(true)
		tx.onerror = () => reject(tx.error)
	})
}

export async function getCachedSetting(key) {
	const db = await openDB()
	const tx = db.transaction('settings', 'readonly')
	const request = tx.objectStore('settings').get(key)
	return new Promise((resolve, reject) => {
		request.onsuccess = () => resolve(request.result?.value ?? null)
		request.onerror = () => reject(request.error)
	})
}

// ── Advanced Order Queries (for retry + conflict resolution) ──

export async function getOrdersByStatus(status) {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readonly')
	const store = tx.objectStore('pendingOrders')
	const index = store.index('status')
	const request = index.getAll(status)
	return new Promise((resolve, reject) => {
		request.onsuccess = () => resolve(request.result)
		request.onerror = () => reject(request.error)
	})
}

export async function markOrderConflict(id, conflictType, serverMessage) {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readwrite')
	const store = tx.objectStore('pendingOrders')
	const request = store.get(id)

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			const record = request.result
			if (record) {
				record.status = 'conflict'
				record.conflict_type = conflictType
				record.error = serverMessage
				record.last_attempt = Date.now()
				store.put(record)
			}
			tx.oncomplete = () => resolve(true)
		}
		tx.onerror = () => reject(tx.error)
	})
}

export async function updateOrderForRetry(id) {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readwrite')
	const store = tx.objectStore('pendingOrders')
	const request = store.get(id)

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			const record = request.result
			if (record) {
				record.status = 'pending'
				record.attempts = (record.attempts || 0) + 1
				// Exponential backoff: 30s, 60s, 120s, 240s, 480s
				const backoffMs = Math.pow(2, record.attempts) * 30_000
				record.next_retry = Date.now() + backoffMs
				record.last_attempt = Date.now()
				store.put(record)
			}
			tx.oncomplete = () => resolve(record)
		}
		tx.onerror = () => reject(tx.error)
	})
}

export async function markOrderDead(id) {
	const db = await openDB()
	const tx = db.transaction('pendingOrders', 'readwrite')
	const store = tx.objectStore('pendingOrders')
	const request = store.get(id)

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			const record = request.result
			if (record) {
				record.status = 'dead_letter'
				record.last_attempt = Date.now()
				store.put(record)
			}
			tx.oncomplete = () => resolve(true)
		}
		tx.onerror = () => reject(tx.error)
	})
}

// ── Cart Snapshot (for service worker access) ──

export async function saveCartSnapshot(cartState) {
	const db = await openDB()
	const tx = db.transaction('cartSnapshot', 'readwrite')
	tx.objectStore('cartSnapshot').put({
		id: 'current',
		...cartState,
		saved_at: Date.now(),
	})
	return new Promise((resolve, reject) => {
		tx.oncomplete = () => resolve(true)
		tx.onerror = () => reject(tx.error)
	})
}

export async function loadCartSnapshot() {
	const db = await openDB()
	const tx = db.transaction('cartSnapshot', 'readonly')
	const request = tx.objectStore('cartSnapshot').get('current')
	return new Promise((resolve, reject) => {
		request.onsuccess = () => resolve(request.result ?? null)
		request.onerror = () => reject(request.error)
	})
}

// ── Catalog TTL ──

const CATALOG_TTL_MS = 30 * 60 * 1000 // 30 minutes

export async function isCatalogStale() {
	const db = await openDB()
	const tx = db.transaction('catalog', 'readonly')
	const store = tx.objectStore('catalog')
	const request = store.openCursor()

	return new Promise((resolve, reject) => {
		let oldestCache = Infinity
		request.onsuccess = () => {
			const cursor = request.result
			if (cursor) {
				const cachedAt = cursor.value.cached_at || 0
				if (cachedAt < oldestCache) oldestCache = cachedAt
				cursor.continue()
			} else {
				if (oldestCache === Infinity) {
					resolve(true) // no catalog at all
				} else {
					resolve(Date.now() - oldestCache > CATALOG_TTL_MS)
				}
			}
		}
		request.onerror = () => reject(request.error)
	})
}
