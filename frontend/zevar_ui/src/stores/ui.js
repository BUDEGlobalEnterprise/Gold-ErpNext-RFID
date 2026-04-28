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

	const layawayPayment = ref({
		show: false,
		layawayId: null,
		balance: 0,
		draftPayload: null,
	})

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
		activeFilterCount,
		toggleTheme,
		setFilter,
		setSort,
		resetFilters,
		layawayPayment,
		openLayawayPayment,
		closeLayawayPayment,
	}
})
