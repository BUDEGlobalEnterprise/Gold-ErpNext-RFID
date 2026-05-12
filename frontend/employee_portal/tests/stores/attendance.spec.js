/**
 * Attendance Store Unit Tests (Vitest)
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

describe('Attendance Store', () => {
	beforeEach(() => {
		setActivePinia(createPinia())
		localStorageMock.clear()
	})

	it('should initialize the store without errors', async () => {
		const { useAttendanceStore } = await import('../../src/stores/attendance.js')
		const attendance = useAttendanceStore()
		expect(attendance).toBeDefined()
	})
})
