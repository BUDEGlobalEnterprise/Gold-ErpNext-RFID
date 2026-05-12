/**
 * Settings Store Unit Tests (Vitest)
 * Tests: State initialization, settings data
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('frappe-ui', () => ({
	createResource: vi.fn(() => ({
		fetch: vi.fn(() =>
			Promise.resolve({
				pos_profiles: [],
				warehouses: [],
				customers: [],
			})
		),
	})),
}))

const localStorageMock = {
	store: {},
	getItem(key) {
		return this.store[key] || null
	},
	setItem(key, value) {
		this.store[key] = value
	},
	removeItem(key) {
		delete this.store[key]
	},
	clear() {
		this.store = {}
	},
}
Object.defineProperty(global, 'localStorage', { value: localStorageMock })

describe('Settings Store', () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		localStorageMock.clear()
	})

	describe('State Initialization', () => {
		it('should initialize the store without errors', async () => {
			const { useSettingsStore } = await import('../../src/stores/settings.js')
			const settings = useSettingsStore()
			expect(settings).toBeDefined()
		})
	})
})
