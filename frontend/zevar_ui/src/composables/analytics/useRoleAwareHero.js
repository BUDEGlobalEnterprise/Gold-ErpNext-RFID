/**
 * useRoleAwareHero — Plan §5.5.
 * Returns the role-aware hero strip config: which cards, what size.
 * Sizes: 'lg' (default), 'md' (de-emphasized), 'sm' (compact).
 */
import { computed } from 'vue'

const CARDS = {
	sales: { key: 'sales', label: 'Daily Sales', icon: 'payments', size: 'lg' },
	repair: { key: 'repair', label: 'Repair Revenue', icon: 'build', size: 'lg' },
	layaway: { key: 'layaway', label: 'Layaways', icon: 'schedule', size: 'lg' },
	cash_variance: { key: 'cash_variance', label: 'Cash Variance', icon: 'point_of_sale', size: 'lg' },
	low_stock: { key: 'low_stock', label: 'Low Stock', icon: 'inventory_2', size: 'lg' },
	overdue_payments: { key: 'overdue_payments', label: 'Overdue', icon: 'error', size: 'md' },
	hold_queue: { key: 'hold_queue', label: 'Hold Items', icon: 'bookmark', size: 'md' },
}

const ROLE_PRESETS = {
	owner: ['sales', 'repair', 'layaway', 'cash_variance', 'low_stock', 'overdue_payments', 'hold_queue'],
	manager: ['sales', 'repair', 'layaway', 'cash_variance', 'low_stock', 'overdue_payments', 'hold_queue'],
	finance: ['cash_variance', 'overdue_payments', 'sales', 'layaway', 'low_stock', 'repair', 'hold_queue'],
	salesperson: ['sales', 'layaway', 'hold_queue'],
	bench: ['repair', 'hold_queue', 'low_stock'],
	default: ['sales', 'repair', 'layaway', 'cash_variance', 'low_stock'],
}

export function useRoleAwareHero(roleInfo) {
	const tier = computed(() => {
		if (!roleInfo?.value) return 'default'
		if (roleInfo.value.is_owner) return 'owner'
		if (roleInfo.value.is_manager) return 'manager'
		return 'default'
	})

	const cards = computed(() => {
		const order = ROLE_PRESETS[tier.value] || ROLE_PRESETS.default
		return order.map((k) => CARDS[k])
	})

	return { tier, cards, CARDS, ROLE_PRESETS }
}
