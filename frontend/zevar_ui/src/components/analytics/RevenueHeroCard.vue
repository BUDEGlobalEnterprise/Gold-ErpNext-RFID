<template>
	<MetricCard
		:label="label"
		:value="data.sales_revenue"
		format="currency"
		icon="payments"
		icon-color="var(--green)"
		:sparkline="sparkPoints"
		:trend="trendPct"
		:trend-label="trendLabel"
		:aria-label="`Daily sales: ${formatCurrency(data.sales_revenue)}`"
		@click="$emit('open')"
	>
		<template #footer>
			<span class="font-mono">{{ data.sales_count || 0 }} txns</span>
		</template>
	</MetricCard>
</template>

<script setup>
/**
 * RevenueHeroCard — Plan §6.1, 100 LOC budget.
 */
import { computed } from 'vue'
import MetricCard from './MetricCard.vue'
import { useFormatters } from '@/composables/useFormatters'

const props = defineProps({
	data: { type: Object, required: true },
	label: { type: String, default: 'Daily Sales' },
	yesterday: { type: Number, default: 0 },
})
defineEmits(['open'])

const { formatCurrency } = useFormatters()

const sparkPoints = computed(() => {
	const arr = props.data?.sparkline_30d || []
	return arr.map((p) => ({ date: p.date, value: Number(p.sales || 0) }))
})

const trendPct = computed(() => {
	const today = Number(props.data?.sales_revenue || 0)
	const y = Number(props.yesterday || 0)
	if (y <= 0) return null
	return Number((((today - y) / y) * 100).toFixed(1))
})

const trendLabel = computed(() => {
	if (trendPct.value == null) return ''
	const sign = trendPct.value >= 0 ? '+' : ''
	return `${sign}${trendPct.value}% vs yesterday`
})
</script>
