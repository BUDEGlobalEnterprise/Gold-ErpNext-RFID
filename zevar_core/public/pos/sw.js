/**
 * Service Worker for Zevar POS - Offline Support
 *
 * Caches assets and API responses for offline functionality.
 * Uses IndexedDB for reliable offline order queuing with:
 * - Idempotency keys (prevents duplicate invoices)
 * - Exponential backoff retry
 * - Conflict detection
 * - Status tracking (pending/synced/failed/conflict/dead_letter)
 */

const CACHE_NAME = 'zevar-pos-v9'
const API_CACHE = 'zevar-api-v9'

// Assets to cache immediately on install
const STATIC_ASSETS = ['/pos/', '/pos/index.html', '/pos/manifest.json']

// API routes that should be cached for offline catalog browsing
const CACHEABLE_API_ROUTES = [
	'zevar_core.api.pos.get_pos_items',
	'zevar_core.api.get_pos_settings',
	'zevar_core.api.pos.get_pos_profile',
]

const MAX_RETRY_ATTEMPTS = 5

// Install event - cache static assets
self.addEventListener('install', (event) => {
	console.log('[SW] Installing service worker v9...')
	event.waitUntil(
		caches
			.open(CACHE_NAME)
			.then((cache) => {
				console.log('[SW] Caching static assets')
				return cache.addAll(STATIC_ASSETS)
			})
			.then(() => self.skipWaiting())
	)
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
	console.log('[SW] Activating service worker v9...')
	event.waitUntil(
		caches
			.keys()
			.then((cacheNames) => {
				return Promise.all(
					cacheNames.map((cacheName) => {
						if (cacheName !== CACHE_NAME && cacheName !== API_CACHE) {
							console.log('[SW] Deleting old cache:', cacheName)
							return caches.delete(cacheName)
						}
					})
				)
			})
			.then(() => self.clients.claim())
	)
})

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
	const { request } = event
	const url = new URL(request.url)

	if (request.mode === 'navigate' || request.destination === 'document') {
		event.respondWith(handleNavigationRequest(request))
		return
	}

	// Handle API calls separately
	if (url.pathname.includes('/api/method/')) {
		// Do not cache sensitive auth methods
		const sensitiveMethods = ['get_user_info', 'get_logged_user', 'logout', 'login']
		if (sensitiveMethods.some((m) => url.pathname.includes(m))) {
			event.respondWith(fetch(request))
			return
		}

		event.respondWith(handleAPIRequest(request))
		return
	}

	// Handle static assets with cache-first strategy
	event.respondWith(
		caches
			.match(request)
			.then((response) => {
				if (response) {
					return response
				}

				return fetch(request).then((response) => {
					// Cache successful responses
					if (!response || response.status !== 200 || response.type === 'error') {
						return response
					}

					const responseToCache = response.clone()
					caches.open(CACHE_NAME).then((cache) => {
						cache.put(request, responseToCache)
					})

					return response
				})
			})
			.catch(() => {
				// Fallback for offline navigation
				if (request.destination === 'document') {
					return caches.match('/pos/index.html')
				}
			})
	)
})

async function handleNavigationRequest(request) {
	try {
		const response = await fetch(request)
		if (response && response.status === 200) {
			const cache = await caches.open(CACHE_NAME)
			cache.put('/pos/index.html', response.clone())
		}
		return response
	} catch (error) {
		return caches.match('/pos/index.html')
	}
}

// Handle API requests with network-first strategy
async function handleAPIRequest(request) {
	const url = new URL(request.url)
	const isCacheableRoute = CACHEABLE_API_ROUTES.some((route) => url.pathname.includes(route))

	try {
		const response = await fetch(request)

		// Cache successful API responses for cacheable routes
		if (response.ok && (isCacheableRoute || request.method === 'GET')) {
			const cache = await caches.open(API_CACHE)
			cache.put(request, response.clone())
		}

		return response
	} catch (error) {
		console.log('[SW] API request failed, trying cache:', request.url)

		// Try to serve from cache
		const cachedResponse = await caches.match(request)
		if (cachedResponse) {
			console.log('[SW] Serving API from cache:', request.url)
			return cachedResponse
		}

		// If GET request (read-only), return offline error
		if (request.method === 'GET') {
			return new Response(JSON.stringify({ error: 'Offline - cached data not available' }), {
				status: 503,
				headers: { 'Content-Type': 'application/json' },
			})
		}

		// For POST requests (mutations), queue in IndexedDB
		if (request.method === 'POST') {
			console.log('[SW] Queuing POST request for offline sync')
			const body = await request.clone().text()
			const idempotency_key = crypto.randomUUID()

			await queueRequestInIDB({
				url: request.url,
				method: request.method,
				headers: Object.fromEntries(request.headers.entries()),
				body: body,
				idempotency_key: idempotency_key,
				timestamp: Date.now(),
				status: 'pending',
				attempts: 0,
				max_attempts: MAX_RETRY_ATTEMPTS,
				next_retry: Date.now(),
			})

			// Register background sync if available
			if ('sync' in self.registration) {
				await self.registration.sync.register('sync-pos-transactions')
			}

			return new Response(
				JSON.stringify({
					message: 'Order queued for sync when online',
					queued: true,
					idempotency_key: idempotency_key,
				}),
				{
					status: 202,
					headers: { 'Content-Type': 'application/json' },
				}
			)
		}

		throw error
	}
}

// ── IndexedDB helpers for the service worker context ──

const SW_DB_NAME = 'zevar_pos_sw'
const SW_DB_VERSION = 2

function openSWDB() {
	return new Promise((resolve, reject) => {
		const request = indexedDB.open(SW_DB_NAME, SW_DB_VERSION)
		request.onupgradeneeded = (event) => {
			const db = event.target.result
			if (!db.objectStoreNames.contains('requestQueue')) {
				const store = db.createObjectStore('requestQueue', { keyPath: 'id', autoIncrement: true })
				store.createIndex('status', 'status', { unique: false })
				store.createIndex('idempotency_key', 'idempotency_key', { unique: false })
			} else if (event.oldVersion < 2) {
				// v1→v2 migration
				const store = event.target.transaction.objectStore('requestQueue')
				if (!store.indexNames.contains('status')) {
					store.createIndex('status', 'status', { unique: false })
				}
				if (!store.indexNames.contains('idempotency_key')) {
					store.createIndex('idempotency_key', 'idempotency_key', { unique: false })
				}
			}
		}
		request.onsuccess = () => resolve(request.result)
		request.onerror = () => reject(request.error)
	})
}

async function queueRequestInIDB(requestData) {
	const db = await openSWDB()
	const tx = db.transaction('requestQueue', 'readwrite')
	tx.objectStore('requestQueue').add(requestData)
	return new Promise((resolve, reject) => {
		tx.oncomplete = () => resolve()
		tx.onerror = () => reject(tx.error)
	})
}

async function getQueuedRequests() {
	const db = await openSWDB()
	const tx = db.transaction('requestQueue', 'readonly')
	const index = tx.objectStore('requestQueue').index('status')
	const request = index.getAll('pending')
	return new Promise((resolve, reject) => {
		request.onsuccess = () => resolve(request.result)
		request.onerror = () => reject(request.error)
	})
}

async function updateQueuedRequest(id, updates) {
	const db = await openSWDB()
	const tx = db.transaction('requestQueue', 'readwrite')
	const store = tx.objectStore('requestQueue')
	const getRequest = store.get(id)

	return new Promise((resolve, reject) => {
		getRequest.onsuccess = () => {
			const record = getRequest.result
			if (record) {
				Object.assign(record, updates)
				store.put(record)
			}
			tx.oncomplete = () => resolve(record)
		}
		tx.onerror = () => reject(tx.error)
	})
}

async function removeQueuedRequest(id) {
	const db = await openSWDB()
	const tx = db.transaction('requestQueue', 'readwrite')
	tx.objectStore('requestQueue').delete(id)
	return new Promise((resolve, reject) => {
		tx.oncomplete = () => resolve()
		tx.onerror = () => reject(tx.error)
	})
}

async function cleanupSyncedRequests() {
	const db = await openSWDB()
	const tx = db.transaction('requestQueue', 'readwrite')
	const store = tx.objectStore('requestQueue')
	const request = store.getAll()

	return new Promise((resolve, reject) => {
		request.onsuccess = () => {
			for (const record of request.result) {
				if (record.status === 'synced') {
					store.delete(record.id)
				}
			}
			tx.oncomplete = () => resolve()
		}
		request.onerror = () => reject(request.error)
	})
}

// Background sync event - retry queued requests
self.addEventListener('sync', (event) => {
	if (event.tag === 'sync-pos-transactions') {
		console.log('[SW] Background sync triggered')
		event.waitUntil(syncPendingTransactions())
	}
})

async function syncPendingTransactions() {
	const requests = await getQueuedRequests()
	console.log(`[SW] Syncing ${requests.length} pending transactions...`)

	if (requests.length === 0) return

	for (const reqData of requests) {
		try {
			// Exponential backoff check
			if (reqData.next_retry && Date.now() < reqData.next_retry) {
				continue
			}

			const headers = { ...reqData.headers }
			if (reqData.idempotency_key) {
				headers['X-Idempotency-Key'] = reqData.idempotency_key
			}

			const response = await fetch(reqData.url, {
				method: reqData.method,
				headers: headers,
				body: reqData.body,
			})

			if (response.ok) {
				await updateQueuedRequest(reqData.id, {
					status: 'synced',
					synced_at: Date.now(),
				})
				console.log('[SW] Synced queued request:', reqData.url)
			} else if (response.status === 409) {
				// Conflict — server already processed or stock issue
				const errData = await response.json().catch(() => ({}))
				await updateQueuedRequest(reqData.id, {
					status: 'conflict',
					error: errData.message || `Conflict: HTTP ${response.status}`,
					conflict_type: errData._conflict_type || 'unknown',
					last_attempt: Date.now(),
				})
				console.warn('[SW] Conflict for:', reqData.url, errData.message)
			} else if (response.status >= 400 && response.status < 500) {
				// Client error — retry won't help, mark dead
				const errData = await response.json().catch(() => ({}))
				await updateQueuedRequest(reqData.id, {
					status: 'dead_letter',
					error: errData.message || `Client error: HTTP ${response.status}`,
					last_attempt: Date.now(),
				})
				console.error('[SW] Dead letter:', reqData.url, response.status)
			} else {
				// Server error — retry with backoff
				const attempts = (reqData.attempts || 0) + 1
				if (attempts >= MAX_RETRY_ATTEMPTS) {
					await updateQueuedRequest(reqData.id, {
						status: 'dead_letter',
						attempts: attempts,
						error: `Max retries reached`,
						last_attempt: Date.now(),
					})
				} else {
					const backoffMs = Math.pow(2, attempts) * 1000 // 1s, 2s, 4s, 8s
					await updateQueuedRequest(reqData.id, {
						status: 'pending',
						attempts: attempts,
						next_retry: Date.now() + backoffMs,
						last_attempt: Date.now(),
					})
					// Re-throw to signal sync manager to retry
					throw new Error(`Server error ${response.status}, will retry`)
				}
			}
		} catch (e) {
			console.error('[SW] Sync network error for:', reqData.url, e.message)
			// Leave in queue with incremented attempts
			const attempts = (reqData.attempts || 0) + 1
			if (attempts < MAX_RETRY_ATTEMPTS) {
				const backoffMs = Math.pow(2, attempts) * 1000
				await updateQueuedRequest(reqData.id, {
					attempts: attempts,
					next_retry: Date.now() + backoffMs,
					last_attempt: Date.now(),
				}).catch(() => {})
			} else {
				await updateQueuedRequest(reqData.id, {
					status: 'dead_letter',
					error: `Max retries: ${e.message}`,
					last_attempt: Date.now(),
				}).catch(() => {})
			}
			// Re-throw so the sync manager retries the event
			throw e
		}
	}

	// Cleanup synced records
	await cleanupSyncedRequests()

	// Notify clients of sync completion
	const clients = await self.clients.matchAll()
	const remaining = await getQueuedRequests()
	clients.forEach((client) => {
		client.postMessage({
			type: 'SYNC_COMPLETE',
			remaining: remaining.length,
		})
	})
}

// Message handling for manual sync triggers
self.addEventListener('message', (event) => {
	if (event.data && event.data.type === 'SKIP_WAITING') {
		self.skipWaiting()
	}

	if (event.data && event.data.type === 'SYNC_NOW') {
		syncPendingTransactions().then(async () => {
			const remaining = await getQueuedRequests()
			event.ports[0]?.postMessage({ success: true, remaining: remaining.length })
		})
	}

	if (event.data && event.data.type === 'GET_QUEUE_COUNT') {
		getQueuedRequests().then((requests) => {
			event.ports[0]?.postMessage({ count: requests.length })
		})
	}
})
