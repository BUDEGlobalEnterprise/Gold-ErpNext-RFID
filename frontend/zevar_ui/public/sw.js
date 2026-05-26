/**
 * Service Worker for Zevar POS - Offline Support v13
 *
 * Cache strategy:
 * - Navigation: network-first, cache fallback
 * - API:        network-first, cache fallback (catalog routes cached for offline)
 * - Static:     stale-while-revalidate (instant load + background update)
 *   - Assets older than MAX_ASSET_AGE_MS bypass cache and fetch from network first
 *
 * Offline sync:
 * - The SW relays SYNC_NOW messages from the app to trigger syncPendingOrders()
 * - POST queuing is handled by the app layer (OfflineDB.js), not the SW
 * - Background Sync API is used only as a connectivity signal to the app
 */

const CACHE_NAME = 'zevar-pos-v13'
const API_CACHE = 'zevar-api-v13'

const STATIC_ASSETS = ['/pos/', '/pos/index.html']

const CACHEABLE_API_ROUTES = [
  'zevar_core.api.pos.get_pos_items',
  'zevar_core.api.get_pos_settings',
  'zevar_core.api.pos.get_pos_profile',
]

const SENSITIVE_METHODS = ['get_user_info', 'get_logged_user', 'logout', 'login']

const MAX_ASSET_AGE_MS = 24 * 60 * 60 * 1000

self.addEventListener('install', (event) => {
  console.log('[SW v13] Installing...')
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', (event) => {
  console.log('[SW v13] Activating...')
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(
          names.map((n) => {
            if (n !== CACHE_NAME && n !== API_CACHE) {
              console.log('[SW v13] Deleting old cache:', n)
              return caches.delete(n)
            }
          })
        )
      )
      .then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(handleNavigationRequest(request))
    return
  }

  if (url.pathname.includes('/api/method/')) {
    if (SENSITIVE_METHODS.some((m) => url.pathname.includes(m))) {
      event.respondWith(fetch(request))
      return
    }
    event.respondWith(handleAPIRequest(request))
    return
  }

  event.respondWith(handleStaticAssetRequest(request))
})

// ── Navigation: network-first ──

async function handleNavigationRequest(request) {
  try {
    const response = await fetch(request)
    if (response && response.status === 200) {
      const cache = await caches.open(CACHE_NAME)
      cache.put('/pos/index.html', response.clone())
    }
    return response
  } catch {
    return caches.match('/pos/index.html')
  }
}

// ── API: network-first with cache fallback ──

async function handleAPIRequest(request) {
  const url = new URL(request.url)
  const isCacheableRoute = CACHEABLE_API_ROUTES.some((route) =>
    url.pathname.includes(route)
  )

  try {
    const response = await fetch(request)

    if (response.ok && (isCacheableRoute || request.method === 'GET')) {
      const cache = await caches.open(API_CACHE)
      cache.put(request, response.clone())
    }

    return response
  } catch {
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }

    if (request.method === 'GET') {
      return new Response(
        JSON.stringify({ error: 'Offline - cached data not available' }),
        { status: 503, headers: { 'Content-Type': 'application/json' } }
      )
    }

    return new Response(
      JSON.stringify({ error: 'Offline - request will be retried by app sync' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    )
  }
}

// ── Static assets: stale-while-revalidate with max-age ──

async function handleStaticAssetRequest(request) {
  const cachedResponse = await caches.match(request)

  if (!cachedResponse) {
    return fetchAndCacheStatic(request)
  }

  const dateHeader = cachedResponse.headers.get('sw-cache-time')
  const cachedTime = dateHeader ? new Date(dateHeader).getTime() : 0
  const isStale = Date.now() - cachedTime > MAX_ASSET_AGE_MS

  if (isStale) {
    try {
      return await fetchAndCacheStatic(request)
    } catch {
      return cachedResponse
    }
  }

  const fetchPromise = fetchAndCacheStatic(request).catch(() => {})

  return cachedResponse
}

async function fetchAndCacheStatic(request) {
  const response = await fetch(request)

  if (!response || response.status !== 200 || response.type === 'error') {
    return response
  }

  const headers = new Headers(response.headers)
  headers.set('sw-cache-time', new Date().toISOString())

  const body = await response.blob()
  const cacheableResponse = new Response(body, {
    status: response.status,
    statusText: response.statusText,
    headers: headers,
  })

  const cache = await caches.open(CACHE_NAME)
  cache.put(request, cacheableResponse.clone())

  return cacheableResponse
}

// ── Background Sync: relay to app, SW does not queue POSTs itself ──

self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-pos-transactions') {
    console.log('[SW v13] Background sync fired — notifying app')
    event.waitUntil(notifyAppToSync())
  }
})

async function notifyAppToSync() {
  const clients = await self.clients.matchAll()
  clients.forEach((client) => {
    client.postMessage({ type: 'TRIGGER_SYNC' })
  })
}

// ── Message handling ──

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }

  if (event.data?.type === 'GET_QUEUE_COUNT') {
    event.ports[0]?.postMessage({ count: 0 })
  }

  if (event.data?.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((names) =>
        Promise.all(names.map((n) => caches.delete(n)))
      ).then(() => {
        event.ports[0]?.postMessage({ success: true })
        return self.clients.matchAll()
      }).then((clients) => {
        clients.forEach((c) => c.postMessage({ type: 'CACHE_CLEARED' }))
      })
    )
  }
})
