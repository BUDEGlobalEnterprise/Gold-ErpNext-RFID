/**
 * Auth Store Unit Tests (Vitest)
 * Employee Portal - Tests: State initialization, auth flow
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('frappe-ui', () => ({
	createResource: vi.fn(() => ({
		fetch: vi.fn(() => Promise.resolve({
			user: 'test@example.com',
			full_name: 'Test Employee',
			roles: ['Employee'],
		})),
		submit: vi.fn(() => Promise.resolve({})),
		auto: false,
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

describe('Auth Store', () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		localStorageMock.clear()
	})

	describe('State Initialization', () => {
		it('should initialize with no user', async () => {
			const { useAuthStore } = await import('../../src/stores/auth.js')
			const auth = useAuthStore()
			expect(auth.user).toBeNull()
			expect(auth.isLoggedIn).toBe(false)
		})

		it('should not be ready initially', async () => {
			const { useAuthStore } = await import('../../src/stores/auth.js')
			const auth = useAuthStore()
			expect(auth.ready).toBe(false)
		})
	})

	describe('Methods', () => {
		it('should have logout method', async () => {
			const { useAuthStore } = await import('../../src/stores/auth.js')
			const auth = useAuthStore()
			expect(typeof auth.logout).toBe('function')
		})

		it('should have init method', async () => {
			const { useAuthStore } = await import('../../src/stores/auth.js')
			const auth = useAuthStore()
			expect(typeof auth.init).toBe('function')
		})
	})
})
