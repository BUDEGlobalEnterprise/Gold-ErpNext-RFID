/**
 * Expense Store Unit Tests (Vitest)
 * Employee Portal - Tests: State initialization
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('frappe-ui', () => ({
	createResource: vi.fn(() => ({
		fetch: vi.fn(() => Promise.resolve({})),
		submit: vi.fn(() => Promise.resolve({})),
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

describe('Expense Store', () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		localStorageMock.clear()
	})

	it('should initialize the store without errors', async () => {
		const { useExpenseStore } = await import('../../src/stores/expense.js')
		const expense = useExpenseStore()
		expect(expense).toBeDefined()
	})
})
