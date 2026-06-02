/**
 * AnalyticsHub Pinia store — central state for the unified hub.
 * Plan §7.4 / Constitution §3 — state mutation in stores, presentation in components.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useHubData } from '@/composables/analytics/useHubData'
import { useDrawerStack } from '@/composables/analytics/useDrawerStack'
import { useTabState } from '@/composables/analytics/useTabState'

export const useAnalyticsHubStore = defineStore('analyticsHub', () => {
	const hub = useHubData()
	const drawer = useDrawerStack()
	const tabs = useTabState('revenue')

	const selectedStore = ref(null)
	const refreshing = ref(false)

	const role = computed(() => hub.role.value)
	const hero = computed(() => hub.hero.value)
	const loading = computed(() => hub.loading.value)
	const aiBrief = computed(() => hub.aiBrief.value)
	const asOf = computed(() => hub.asOf.value)
	const error = computed(() => hub.error.value)

	async function refresh(force = false) {
		refreshing.value = true
		try {
			await hub.fetchHub(selectedStore.value, { force })
		} finally {
			refreshing.value = false
		}
	}

	function openCardDrawer(cardKey) {
		const drawerMap = {
			sales: { title: 'Daily Sales Detail', kind: 'sales' },
			repair: { title: 'Repair Detail', kind: 'repair' },
			layaway: { title: 'Layaway Detail', kind: 'layaway' },
			cash_variance: { title: 'Cash Variance Sessions', kind: 'cash_variance' },
			low_stock: { title: 'Low Stock Items', kind: 'low_stock' },
			overdue_payments: { title: 'Overdue Payments', kind: 'overdue_payments' },
			hold_queue: { title: 'Hold Queue', kind: 'hold_queue' },
		}
		const conf = drawerMap[cardKey] || { title: 'Detail', kind: cardKey }
		drawer.open({ title: conf.title, kind: conf.kind, payload: hero.value?.[cardKey] || null })
	}

	return {
		hub,
		drawer,
		tabs,
		selectedStore,
		refreshing,
		role,
		hero,
		loading,
		aiBrief,
		asOf,
		error,
		refresh,
		openCardDrawer,
	}
})
