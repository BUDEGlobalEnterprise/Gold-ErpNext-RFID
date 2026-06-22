/**
 * Service Worker for Zevar POS v14
 *
 * Strategy: NETWORK-FIRST for everything.
 * Cache is ONLY used as offline fallback, never served when network is available.
 * This prevents stale content issues permanently.
 */
// Force cache update for Special Order Wizard fix
const CACHE_NAME = 'zevar-pos-v25'
const API_CACHE = 'zevar-api-v25'

const OFFLINE_FALLBACK_ASSETS = ['/pos/', '/pos/index.html']

const CACHEABLE_API_ROUTES = [
	'zevar_core.api.pos.get_pos_items',
	'zevar_core.api.get_pos_settings',
	'zevar_core.api.pos.get_pos_profile',
]

const SENSITIVE_METHODS = ['get_user_info', 'get_logged_user', 'logout', 'login']

// ── Install: cache shell for offline fallback only ──

self.addEventListener('install', (event) => {
	console.log('[SW v24] Installing — network-first strategy')
	event.waitUntil(
		caches
			.open(CACHE_NAME)
			.then((cache) => cache.addAll(OFFLINE_FALLBACK_ASSETS))
			.then(() => self.skipWaiting())
	)
})

// ── Activate: purge ALL old caches ──

self.addEventListener('activate', (event) => {
	console.log('[SW v24] Activating — clearing old caches')
	event.waitUntil(
		caches
			.keys()
			.then((names) =>
				Promise.all(
					names.map((n) => {
						if (n !== CACHE_NAME && n !== API_CACHE) {
							console.log('[SW v24] Purging:', n)
							return caches.delete(n)
						}
					})
				)
			)
			.then(() => self.clients.claim())
	)
})

// ── Fetch: network-first for EVERYTHING ──

self.addEventListener('fetch', (event) => {
	const { request } = event
	const url = new URL(request.url)

	// Skip non-GET (let browser handle POST/PUT/DELETE normally)
	if (request.method !== 'GET') return

	// Skip sensitive auth endpoints entirely
	if (SENSITIVE_METHODS.some((m) => url.pathname.includes(m))) return

	if (request.mode === 'navigate' || request.destination === 'document') {
		event.respondWith(networkFirst(request, CACHE_NAME, '/pos/index.html'))
		return
	}

	if (url.pathname.includes('/api/method/')) {
		const isCacheable = CACHEABLE_API_ROUTES.some((r) => url.pathname.includes(r))
		event.respondWith(networkFirst(request, isCacheable ? API_CACHE : null))
		return
	}

	// Static assets: network-first, cache as fallback
	event.respondWith(networkFirst(request, CACHE_NAME))
})

/**
 * Network-first strategy:
 * 1. Try network
 * 2. On success: update cache, return fresh response
 * 3. On failure: return cached version (offline fallback)
 */
async function networkFirst(request, cacheName, fallbackKey) {
	try {
		const response = await fetch(request)
		if (response && response.ok && cacheName) {
			const cache = await caches.open(cacheName)
			cache.put(request, response.clone())
		}
		return response
	} catch (err) {
		if (cacheName) {
			const cached = await caches.match(request)
			if (cached) return cached
		}
		if (fallbackKey) {
			return caches.match(fallbackKey)
		}
		return new Response('Offline', { status: 503 })
	}
}

// ── Background Sync ──

self.addEventListener('sync', (event) => {
	if (event.tag === 'sync-pos-transactions') {
		event.waitUntil(
			self.clients.matchAll().then((clients) => {
				clients.forEach((c) => c.postMessage({ type: 'TRIGGER_SYNC' }))
			})
		)
	}
})

// ── Message handling ──

self.addEventListener('message', (event) => {
	if (event.data?.type === 'SKIP_WAITING') {
		self.skipWaiting()
	}

	if (event.data?.type === 'GET_VERSION') {
		event.ports[0]?.postMessage({ version: 14 })
	}

	if (event.data?.type === 'CLEAR_CACHE') {
		event.waitUntil(
			caches
				.keys()
				.then((names) => Promise.all(names.map((n) => caches.delete(n))))
				.then(() => {
					event.ports[0]?.postMessage({ success: true })
					return self.clients.matchAll()
				})
				.then((clients) => {
					clients.forEach((c) => c.postMessage({ type: 'CACHE_CLEARED' }))
				})
		)
	}
})
