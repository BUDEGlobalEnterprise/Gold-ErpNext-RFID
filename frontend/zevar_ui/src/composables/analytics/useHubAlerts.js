/**
 * useHubAlerts — Plan §5.2, "Alerts Strip" region.
 * Derives a list of clickable alert cards from the current hub payload.
 */
import { computed } from 'vue'

export function useHubAlerts(hero) {
	const alerts = computed(() => {
		const out = []
		if (!hero.value) return out

		if (Number(hero.value?.low_stock?.total || 0) > 0) {
			out.push({
				key: 'low_stock',
				card: 'low_stock',
				icon: 'inventory_2',
				color: 'var(--yellow)',
				label: 'Low Stock',
				detail: `${hero.value.low_stock.total} SKUs below reorder level`,
			})
		}
		const od = hero.value?.overdue_payments
		if (od && Number(od.count || 0) > 0) {
			out.push({
				key: 'overdue',
				card: 'overdue_payments',
				icon: 'error',
				color: 'var(--red)',
				label: 'Overdue',
				detail: `${od.count} items · $${Number(od.total_overdue_amount || 0).toFixed(
					0
				)} outstanding`,
			})
		}
		const holds = hero.value?.hold_queue
		if (holds && Number(holds.total_count || 0) > 0) {
			out.push({
				key: 'holds',
				card: 'hold_queue',
				icon: 'bookmark',
				color: 'var(--purple)',
				label: 'Hold Items',
				detail: `${holds.total_count} active${
					holds.expiring_soon_count ? ` · ${holds.expiring_soon_count} expiring` : ''
				}`,
			})
		}
		const cash = hero.value?.cash_variance
		if (cash && !cash.within_tolerance) {
			out.push({
				key: 'cash',
				card: 'cash_variance',
				icon: 'point_of_sale',
				color: 'var(--red)',
				label: 'Cash Variance',
				detail: `Out of tolerance: $${Number(cash.total_variance || 0).toFixed(2)}`,
			})
		}
		return out
	})

	return { alerts }
}
