/**
 * useTabState — Plan §5.3, DEC-REP-V2-003.
 * Persists the active tab and tab-local filter state in sessionStorage
 * so that the tab survives a refresh and across the same browser session.
 */
import { ref, watch } from 'vue'

const STORAGE_KEY = 'zevar.analyticsHub.tabState'

function load() {
	try {
		const raw = sessionStorage.getItem(STORAGE_KEY)
		if (!raw) return null
		return JSON.parse(raw)
	} catch {
		return null
	}
}

export function useTabState(defaultTab = 'revenue') {
	const stored = load()
	const activeTab = ref(stored?.activeTab || defaultTab)
	const filters = ref(stored?.filters || {})

	function setTab(tab) {
		activeTab.value = tab
		persist()
	}

	function setFilter(tab, key, value) {
		if (!filters.value[tab]) filters.value[tab] = {}
		filters.value[tab][key] = value
		persist()
	}

	function resetTab(tab) {
		delete filters.value[tab]
		persist()
	}

	function persist() {
		try {
			sessionStorage.setItem(
				STORAGE_KEY,
				JSON.stringify({ activeTab: activeTab.value, filters: filters.value })
			)
		} catch {
			// sessionStorage full / disabled — silently skip
		}
	}

	watch([activeTab, filters], persist, { deep: true })

	return { activeTab, filters, setTab, setFilter, resetTab }
}
