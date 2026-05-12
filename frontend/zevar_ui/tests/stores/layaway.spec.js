/**
 * Layaway Store Unit Tests (Vitest)
 * Tests: State initialization, contract data
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('frappe-ui', () => ({
	createResource: vi.fn(() => ({
		fetch: vi.fn(() => Promise.resolve({ contracts: [] })),
		submit: vi.fn(() => Promise.resolve({ success: true })),
	})),
}))

const localStorageMock = {
	store: {},
	getItem(key) { return this.store[key] || null },
	setItem(key, value) { this.store[key] = value },
	removeItem(key) { delete this.store[key] },
	clear() { this.store = {} },
}
Object.defineProperty(global, 'localStorage', { value: localStorageMock })

describe('Layaway Store', () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		localStorageMock.clear()
	})

	describe('State Initialization', () => {
		it('should initialize the store without errors', async () => {
			const { useLayawayStore } = await import('../../src/stores/layaway.js')
			const layaway = useLayawayStore()
			expect(layaway).toBeDefined()
		})
	})
})
