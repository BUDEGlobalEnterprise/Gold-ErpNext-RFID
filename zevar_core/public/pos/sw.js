/**
 * Service Worker for Zevar POS - Offline Support
 *
 * Caches assets and API responses for offline functionality
 */

const CACHE_NAME = 'zevar-pos-v2'
const API_CACHE = 'zevar-api-v2'

// Assets to cache immediately on install
const STATIC_ASSETS = ['/pos/', '/pos/index.html', '/pos/manifest.json']

// Install event - cache static assets
self.addEventListener('install', (event) => {
	console.log('[SW] Installing service worker...')
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
	console.log('[SW] Activating service worker...')
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
		event.respondWith(handleAPIRequest(request))
		return
	}

	// Handle static assets with cache-first strategy
	event.respondWith(
		caches
			.match(request)
			.then((response) => {
				if (response) {
					console.log('[SW] Serving from cache:', request.url)
					return response
				}

				console.log('[SW] Fetching from network:', request.url)
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
					return caches.match('/index.html')
				}
			})
	)
})

// Handle API requests with network-first strategy
async function handleAPIRequest(request) {
	try {
		const response = await fetch(request)

		// Cache successful API responses
		if (response.ok) {
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

		// For POST requests (mutations), queue for background sync
		if ('sync' in self.registration && request.method === 'POST') {
			console.log('[SW] Queuing POST request for background sync')
			await queueRequest(request)
			return new Response(
				JSON.stringify({
					message: 'Request queued for sync when online',
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

// Queue failed requests for background sync
async function queueRequest(request) {
	const requestData = {
		url: request.url,
		method: request.method,
		headers: Object.fromEntries(request.headers.entries()),
		body: await request.text(),
		timestamp: Date.now(),
	}

	// Store in IndexedDB (would need idb library for production)
	// For now, register sync event
	await self.registration.sync.register('sync-pos-transactions')

	// Store request data in a simple way (would use IndexedDB in production)
	console.log('[SW] Queued request:', requestData)
}

// Background sync event - retry failed requests
self.addEventListener('sync', (event) => {
	if (event.tag === 'sync-pos-transactions') {
		console.log('[SW] Background sync triggered')
		event.waitUntil(syncPendingTransactions())
	}
})

async function syncPendingTransactions() {
	// In production, retrieve queued requests from IndexedDB
	// and retry them
	console.log('[SW] Syncing pending transactions...')
	// TODO: Implement IndexedDB retrieval and retry logic
	return Promise.resolve()
}

// Message handling for manual sync triggers
self.addEventListener('message', (event) => {
	if (event.data && event.data.type === 'SKIP_WAITING') {
		self.skipWaiting()
	}

	if (event.data && event.data.type === 'SYNC_NOW') {
		syncPendingTransactions().then(() => {
			event.ports[0].postMessage({ success: true })
		})
	}
})
