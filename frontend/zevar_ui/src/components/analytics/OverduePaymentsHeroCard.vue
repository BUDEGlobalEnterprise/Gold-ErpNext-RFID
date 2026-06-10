<template>
	<MetricCard
		:label="label"
		:value="data.total_overdue_amount"
		format="currency"
		icon="error"
		icon-color="var(--red)"
		:badge="data.count"
		:badge-severity="data.count > 0 ? 'critical' : 'low'"
		:aria-label="`Overdue payments: ${formatCurrency(data.total_overdue_amount)} across ${
			data.count
		} items`"
		@click="$emit('open')"
	>
		<template #footer>
			<span class="font-mono">
				{{ (data.repairs || []).length }} repairs ·
				{{ (data.layaways || []).length }} layaways
			</span>
		</template>
	</MetricCard>
</template>

<script setup>
/**
 * OverduePaymentsHeroCard — Plan §6.5.
 * Unifies repair + layaway overdue into one card.
 */
import MetricCard from './MetricCard.vue'
import { useFormatters } from '@/composables/useFormatters'
defineProps({
	data: { type: Object, required: true },
	label: { type: String, default: 'Overdue' },
})
defineEmits(['open'])
const { formatCurrency } = useFormatters()
</script>
