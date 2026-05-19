/**
 * Service Worker for Zevar POS - Offline Support
 *
 * Caches assets and API responses for offline functionality.
 * Uses IndexedDB for reliable offline order queuing.
 */

const CACHE_NAME = 'zevar-pos-v4'
const API_CACHE = 'zevar-api-v4'

// Assets to cache immediately on install
const STATIC_ASSETS = ['/pos/', '/pos/index.html', '/pos/manifest.json']

// API routes that should be cached for offline catalog browsing
const CACHEABLE_API_ROUTES = [
	'zevar_core.api.pos.get_pos_items',
	'zevar_core.api.get_pos_settings',
	'zevar_core.api.pos.get_pos_profile',
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
	console.log('[SW] Installing service worker v4...')
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
	console.log('[SW] Activating service worker v4...')
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
			return new Response(
				JSON.stringify({ error: 'Offline - cached data not available' }),
				{
					status: 503,
					headers: { 'Content-Type': 'application/json' },
				}
			)
		}

		// For POST requests (mutations), queue in IndexedDB
		if (request.method === 'POST') {
			console.log('[SW] Queuing POST request for offline sync')
			const body = await request.clone().text()
			await queueRequestInIDB({
				url: request.url,
				method: request.method,
				headers: Object.fromEntries(request.headers.entries()),
				body: body,
				timestamp: Date.now(),
			})

			// Register background sync if available
			if ('sync' in self.registration) {
				await self.registration.sync.register('sync-pos-transactions')
			}

			return new Response(
				JSON.stringify({
					message: 'Order queued for sync when online',
					queued: true,
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
const SW_DB_VERSION = 1

function openSWDB() {
	return new Promise((resolve, reject) => {
		const request = indexedDB.open(SW_DB_NAME, SW_DB_VERSION)
		request.onupgradeneeded = (event) => {
			const db = event.target.result
			if (!db.objectStoreNames.contains('requestQueue')) {
				db.createObjectStore('requestQueue', { keyPath: 'id', autoIncrement: true })
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
	const request = tx.objectStore('requestQueue').getAll()
	return new Promise((resolve, reject) => {
		request.onsuccess = () => resolve(request.result)
		request.onerror = () => reject(request.error)
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

	for (const reqData of requests) {
		try {
			const response = await fetch(reqData.url, {
				method: reqData.method,
				headers: reqData.headers,
				body: reqData.body,
			})

			if (response.ok) {
				await removeQueuedRequest(reqData.id)
				console.log('[SW] Synced queued request:', reqData.url)
			} else {
				console.error('[SW] Sync failed for:', reqData.url, response.status)
			}
		} catch (e) {
			console.error('[SW] Sync network error for:', reqData.url, e.message)
			// Leave in queue for next sync attempt
		}
	}

	// Notify clients of sync completion
	const clients = await self.clients.matchAll()
	const remaining = await getQueuedRequests()
	const remainingCount = remaining.length
	clients.forEach((client) => {
		client.postMessage({ type: 'SYNC_COMPLETE', remaining: remainingCount })
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
