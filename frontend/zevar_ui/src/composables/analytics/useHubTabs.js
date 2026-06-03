/**
 * useHubTabs — central config for the 6 module tabs and the 7 drawers.
 * Filters tabs based on role_context.visible_tabs from the backend.
 */
import { defineAsyncComponent, computed } from 'vue'

const ALL_TABS = [
	{ key: 'revenue', label: 'Revenue', icon: 'monitoring' },
	{ key: 'inventory', label: 'Inventory', icon: 'inventory_2' },
	{ key: 'customers', label: 'Customers', icon: 'group' },
	{ key: 'repairs', label: 'Repairs', icon: 'build' },
	{ key: 'finance', label: 'Finance', icon: 'account_balance' },
	{ key: 'ai', label: 'AI Insights', icon: 'auto_awesome' },
]

export const TAB_COMPONENT_MAP = {
	revenue: defineAsyncComponent(() => import('@/pages/reports/RevenueTab.vue')),
	inventory: defineAsyncComponent(() => import('@/pages/reports/InventoryTab.vue')),
	customers: defineAsyncComponent(() => import('@/pages/reports/CustomersTab.vue')),
	repairs: defineAsyncComponent(() => import('@/pages/reports/RepairsTab.vue')),
	finance: defineAsyncComponent(() => import('@/pages/reports/FinanceTab.vue')),
	ai: defineAsyncComponent(() => import('@/pages/reports/AIInsightsTab.vue')),
}

export const DRAWER_COMPONENT_MAP = {
	sales: defineAsyncComponent(() => import('@/components/analytics/drawers/SalesDetailDrawer.vue')),
	repair: defineAsyncComponent(() => import('@/components/analytics/drawers/RepairDetailDrawer.vue')),
	layaway: defineAsyncComponent(() => import('@/components/analytics/drawers/LayawayDetailDrawer.vue')),
	cash_variance: defineAsyncComponent(() => import('@/components/analytics/drawers/CashVarianceDrawer.vue')),
	low_stock: defineAsyncComponent(() => import('@/components/analytics/drawers/LowStockDrawer.vue')),
	overdue_payments: defineAsyncComponent(() => import('@/components/analytics/drawers/OverdueDrawer.vue')),
	hold_queue: defineAsyncComponent(() => import('@/components/analytics/drawers/HoldQueueDrawer.vue')),
}

export function useFilteredTabs(roleContext) {
	const HUB_TABS = computed(() => {
		const visible = roleContext?.value?.visible_tabs
		if (!visible || !Array.isArray(visible)) return ALL_TABS
		const set = new Set(visible)
		return ALL_TABS.filter((t) => set.has(t.key))
	})
	return { HUB_TABS, ALL_TABS }
}
