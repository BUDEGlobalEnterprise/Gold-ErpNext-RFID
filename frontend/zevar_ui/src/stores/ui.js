/**
 * UI Store
 *
 * Manages UI state including search, filters, sorting, and theme preferences.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore('ui', () => {
	const searchQuery = ref('')
	const activeFilters = ref({
		pos: {},
		transactions: {
			from_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
			to_date: new Date().toISOString().split('T')[0],
			date_preset: 'Last 7 Days',
		},
		customers: {},
		inventory: {},
	})
	const sidebarCollapsed = ref(false)
	const sortBy = ref({
		pos: '',
		transactions: '',
		customers: '',
		inventory: '',
	})

	// Migrate legacy 'zevar-theme' key to 'theme'
	const legacy = localStorage.getItem('zevar-theme')
	if (legacy && !localStorage.getItem('theme')) {
		localStorage.setItem('theme', legacy)
		localStorage.removeItem('zevar-theme')
	}

	const isDark = ref(localStorage.getItem('theme') === 'dark')

	// Apply dark class synchronously — before any component mounts
	if (isDark.value) {
		document.documentElement.classList.add('dark')
	} else {
		document.documentElement.classList.remove('dark')
	}

	function getActiveFilterCount(context = 'pos') {
		let count = 0
		const f = activeFilters.value[context] || {}
		// General count for any truthy value except specific exclusions
		Object.keys(f).forEach((key) => {
			if (f[key] !== null && f[key] !== undefined && f[key] !== '' && f[key] !== false) {
				// Handle price min/max as one filter
				if (key === 'price_min' || key === 'price_max') {
					if (key === 'price_min') count++
				} else {
					count++
				}
			}
		})
		return count
	}

	function toggleTheme() {
		isDark.value = !isDark.value
		if (isDark.value) {
			document.documentElement.classList.add('dark')
			localStorage.setItem('theme', 'dark')
		} else {
			document.documentElement.classList.remove('dark')
			localStorage.setItem('theme', 'light')
		}
	}

	function setFilter(context, key, value) {
		if (!activeFilters.value[context]) {
			activeFilters.value[context] = {}
		}
		if (value === null || value === undefined || value === '' || value === false) {
			delete activeFilters.value[context][key]
		} else {
			activeFilters.value[context][key] = value
		}
	}

	function setSort(context, value) {
		if (sortBy.value[context] !== undefined) {
			sortBy.value[context] = value || ''
		}
	}

	function resetFilters(context) {
		if (activeFilters.value[context]) {
			activeFilters.value[context] = {}
		}
		if (sortBy.value[context] !== undefined) {
			sortBy.value[context] = ''
		}
		searchQuery.value = ''
	}

	const layawayPayment = ref({
		show: false,
		layawayId: null,
		balance: 0,
		draftPayload: null,
	})

	const sidebarScrollTop = ref(0)

	function openLayawayPayment(layawayId, balance, draftPayload = null) {
		layawayPayment.value = {
			show: true,
			layawayId,
			balance,
			draftPayload,
		}
	}

	function closeLayawayPayment() {
		layawayPayment.value.show = false
		layawayPayment.value.draftPayload = null
	}

	return {
		searchQuery,
		activeFilters,
		sidebarCollapsed,
		sortBy,
		isDark,
		getActiveFilterCount,
		toggleTheme,
		setFilter,
		setSort,
		resetFilters,
		layawayPayment,
		openLayawayPayment,
		closeLayawayPayment,
		sidebarScrollTop,
	}
})
