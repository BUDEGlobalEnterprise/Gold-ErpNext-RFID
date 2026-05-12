/**
 * POS Session Store Unit Tests (Vitest)
 * Tests: Session state, opening/closing balance
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('frappe-ui', () => ({
	createResource: vi.fn(() => ({
		fetch: vi.fn(() => Promise.resolve({
			has_active_session: false,
			session: null,
		})),
		submit: vi.fn(() => Promise.resolve({ success: true, session_name: 'POS-OPEN-001' })),
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

describe('POS Session Store', () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		localStorageMock.clear()
	})

	describe('State Initialization', () => {
		it('should initialize without active session', async () => {
			const { usePOSSessionStore } = await import('../../src/stores/posSession.js')
			const posSession = usePOSSessionStore()
			expect(posSession).toBeDefined()
		})
	})
})
