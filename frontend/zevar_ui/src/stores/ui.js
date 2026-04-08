/**
 * UI Store
 *
 * Manages UI state including search, filters, sorting, and theme preferences.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore('ui', () => {
	const searchQuery = ref('')
	const activeFilters = ref({})
	const sidebarCollapsed = ref(false)
	const sortBy = ref('')

	const isDark = ref(localStorage.getItem('theme') === 'dark')

	if (isDark.value) {
		document.documentElement.classList.add('dark')
	} else {
		document.documentElement.classList.remove('dark')
	}

	const activeFilterCount = computed(() => {
		let count = 0
		const f = activeFilters.value
		if (f.in_stock_only) count++
		if (f.out_of_stock_only) count++
		if (f.custom_metal_type) count++
		if (f.custom_gemstone) count++
		if (f.custom_purity) count++
		if (f.custom_jewelry_type) count++
		if (f.price_min || f.price_max) count++
		return count
	})

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

	function setFilter(key, value) {
		if (value === null || value === undefined || value === '' || value === false) {
			delete activeFilters.value[key]
		} else {
			activeFilters.value[key] = value
		}
	}

	function setSort(value) {
		sortBy.value = value || ''
	}

	function resetFilters() {
		activeFilters.value = {}
		searchQuery.value = ''
		sortBy.value = ''
	}

	return {
		searchQuery,
		activeFilters,
		sidebarCollapsed,
		sortBy,
		isDark,
		activeFilterCount,
		toggleTheme,
		setFilter,
		setSort,
		resetFilters,
	}
})
