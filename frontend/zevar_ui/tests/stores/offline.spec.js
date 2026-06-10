/**
 * Offline store tests (Commit B: feat(offline))
 *
 * Verifies the Pinia store wraps OfflineDB correctly and reacts to
 * connectivity events. OfflineDB is mocked at the module boundary so
 * these tests don't need a real IndexedDB implementation.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// vi.mock is hoisted; use vi.hoisted to share state with the factory.
const mocks = vi.hoisted(() => {
	const dbState = { pending: [], catalog: [], settings: {} }
	return {
		dbState,
		queueOfflineOrder: vi.fn(async (order) => {
			const id = dbState.pending.length + 1
			dbState.pending.push({
				id,
				...order,
				status: 'pending',
				idempotency_key: 'test-key-' + id,
			})
		}),
		getPendingOrders: vi.fn(async () => dbState.pending.filter((o) => o.status === 'pending')),
		getOrdersByStatus: vi.fn(async (status) =>
			dbState.pending.filter((o) => o.status === status)
		),
		markOrderSynced: vi.fn(async (id) => {
			const o = dbState.pending.find((x) => x.id === id)
			if (o) o.status = 'synced'
		}),
		markOrderFailed: vi.fn(async (id, err) => {
			const o = dbState.pending.find((x) => x.id === id)
			if (o) {
				o.status = 'failed'
				o.error = err
			}
		}),
		markOrderConflict: vi.fn(async (id, type, msg) => {
			const o = dbState.pending.find((x) => x.id === id)
			if (o) {
				o.status = 'conflict'
				o.conflict_type = type
				o.error = msg
			}
		}),
		updateOrderForRetry: vi.fn(async (id) => {
			const o = dbState.pending.find((x) => x.id === id)
			if (o) {
				o.status = 'pending'
				o.attempts = (o.attempts || 0) + 1
			}
		}),
		markOrderDead: vi.fn(async (id) => {
			const o = dbState.pending.find((x) => x.id === id)
			if (o) o.status = 'dead_letter'
		}),
		clearSyncedOrders: vi.fn(async () => {
			dbState.pending = dbState.pending.filter((o) => o.status !== 'synced')
		}),
		cacheCatalog: vi.fn(async (items) => {
			dbState.catalog = items
			return items.length
		}),
		getCachedCatalog: vi.fn(async () => dbState.catalog),
		getCatalogCount: vi.fn(async () => dbState.catalog.length),
		cacheSetting: vi.fn(async (k, v) => {
			dbState.settings[k] = v
		}),
		getCachedSetting: vi.fn(async (k) => dbState.settings[k] ?? null),
		isCatalogStale: vi.fn(async () => false),
	}
})

vi.mock('@/services/OfflineDB.js', () => ({
	queueOfflineOrder: mocks.queueOfflineOrder,
	getPendingOrders: mocks.getPendingOrders,
	getOrdersByStatus: mocks.getOrdersByStatus,
	markOrderSynced: mocks.markOrderSynced,
	markOrderFailed: mocks.markOrderFailed,
	markOrderConflict: mocks.markOrderConflict,
	updateOrderForRetry: mocks.updateOrderForRetry,
	markOrderDead: mocks.markOrderDead,
	clearSyncedOrders: mocks.clearSyncedOrders,
	cacheCatalog: mocks.cacheCatalog,
	getCachedCatalog: mocks.getCachedCatalog,
	getCatalogCount: mocks.getCatalogCount,
	cacheSetting: mocks.cacheSetting,
	getCachedSetting: mocks.getCachedSetting,
	isCatalogStale: mocks.isCatalogStale,
}))

// Mock fetch globally — each test can override.
let lastFetchUrl = null

global.fetch = vi.fn(async (url) => {
	lastFetchUrl = url
	return {
		ok: true,
		status: 200,
		json: async () => ({ message: { invoice_name: 'INV-1' } }),
	}
})

import { useOfflineStore } from '../../src/stores/offline.js'

beforeEach(() => {
	setActivePinia(createPinia())
	mocks.dbState.pending = []
	mocks.dbState.catalog = []
	mocks.dbState.settings = {}
	lastFetchUrl = null
	vi.clearAllMocks()
})

// ---------------------------------------------------------------------------
// Pending orders
// ---------------------------------------------------------------------------

describe('offline store — pending orders', () => {
	it('addPendingOrder queues to IndexedDB and updates count', async () => {
		const store = useOfflineStore()
		await store.addPendingOrder({ payload: { items: '[]' } })
		expect(mocks.queueOfflineOrder).toHaveBeenCalledOnce()
		expect(store.pendingCount).toBe(1)
	})

	it('refreshPendingCount counts pending only', async () => {
		const store = useOfflineStore()
		mocks.dbState.pending = [
			{ id: 1, status: 'pending' },
			{ id: 2, status: 'synced' },
			{ id: 3, status: 'pending' },
		]
		await store.refreshPendingCount()
		expect(store.pendingCount).toBe(2)
	})
})

// ---------------------------------------------------------------------------
// Sync — Bug Fix 2 specifically: URL must be create_pos_invoice
// ---------------------------------------------------------------------------

describe('offline store — syncPendingOrders', () => {
	it('posts to zevar_core.api.pos.create_pos_invoice (NOT submit_invoice)', async () => {
		// Bug Fix 2 regression test.
		mocks.dbState.pending = [{ id: 1, status: 'pending', payload: { items: '[]' } }]
		const store = useOfflineStore()
		await store.syncPendingOrders()
		expect(lastFetchUrl).toBe('/api/method/zevar_core.api.pos.create_pos_invoice')
		expect(mocks.markOrderSynced).toHaveBeenCalledWith(1)
	})

	it('retries server errors and marks client errors as failed without aborting the rest', async () => {
		mocks.dbState.pending = [
			{ id: 1, status: 'pending', payload: { items: '[]' } },
			{ id: 2, status: 'pending', payload: { items: '[]' } },
		]
		// First call succeeds, second returns a client error (422).
		let calls = 0
		global.fetch = vi.fn(async () => {
			calls++
			return {
				ok: calls === 1,
				status: calls === 1 ? 200 : 422,
				json: async () =>
					calls === 1
						? { message: { invoice_name: 'INV-1' } }
						: { message: 'validation error' },
			}
		})

		const store = useOfflineStore()
		await store.syncPendingOrders()

		expect(mocks.markOrderSynced).toHaveBeenCalledWith(1)
		// Client errors (4xx) mark the order as failed
		expect(mocks.markOrderFailed).toHaveBeenCalledWith(2, expect.any(String))
	})

	it('retries server errors with exponential backoff', async () => {
		mocks.dbState.pending = [
			{ id: 1, status: 'pending', payload: { items: '[]' }, attempts: 0 },
		]
		global.fetch = vi.fn(async () => ({
			ok: false,
			status: 500,
			json: async () => ({ message: 'server error' }),
		}))

		const store = useOfflineStore()
		await store.syncPendingOrders()

		// Server errors (5xx) trigger retry with backoff, not immediate failure
		expect(mocks.updateOrderForRetry).toHaveBeenCalledWith(1)
		expect(mocks.markOrderFailed).not.toHaveBeenCalled()
	})

	it('is a no-op when offline', async () => {
		const store = useOfflineStore()
		store.isOnline = false
		await store.syncPendingOrders()
		expect(global.fetch).not.toHaveBeenCalled()
	})

	it('skips when already syncing (re-entrancy guard)', async () => {
		const store = useOfflineStore()
		store.syncing = true
		await store.syncPendingOrders()
		expect(global.fetch).not.toHaveBeenCalled()
	})
})

// ---------------------------------------------------------------------------
// Catalog cache
// ---------------------------------------------------------------------------

describe('offline store — catalog cache', () => {
	it('updateCatalogCache writes through OfflineDB and updates count', async () => {
		const store = useOfflineStore()
		const items = [{ item_code: 'A1' }, { item_code: 'A2' }]
		const count = await store.updateCatalogCache(items)
		expect(count).toBe(2)
		expect(store.catalogCachedCount).toBe(2)
		expect(mocks.cacheCatalog).toHaveBeenCalledWith(items)
	})

	it('getOfflineCatalog forwards search term', async () => {
		const store = useOfflineStore()
		mocks.dbState.catalog = [{ item_code: 'X1' }]
		await store.getOfflineCatalog('foo')
		expect(mocks.getCachedCatalog).toHaveBeenCalledWith('foo')
	})
})

// ---------------------------------------------------------------------------
// Status computeds
// ---------------------------------------------------------------------------

describe('offline store — status computeds', () => {
	it('shows red Offline when not online', () => {
		const store = useOfflineStore()
		store.isOnline = false
		expect(store.statusLabel).toBe('Offline')
		expect(store.statusColor).toBe('red')
	})

	it('shows amber pending count when online with queued orders', () => {
		const store = useOfflineStore()
		store.isOnline = true
		store.pendingCount = 3
		expect(store.statusLabel).toContain('3')
		expect(store.statusColor).toBe('amber')
	})

	it('shows green Online when idle', () => {
		const store = useOfflineStore()
		store.isOnline = true
		store.pendingCount = 0
		store.syncing = false
		expect(store.statusLabel).toBe('Online')
		expect(store.statusColor).toBe('green')
	})
})
