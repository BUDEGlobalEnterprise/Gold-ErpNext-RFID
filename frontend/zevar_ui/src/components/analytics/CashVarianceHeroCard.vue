<template>
	<MetricCard
		:label="label"
		:value="data.total_variance"
		format="currency"
		icon="point_of_sale"
		:icon-color="iconColor"
		:variant="variant"
		:aria-label="`Cash variance: ${formatCurrency(data.total_variance)}`"
		@click="$emit('open')"
	>
		<template #footer>
			<span class="font-mono">
				{{ (data.sessions || []).length }} sessions
				<span v-if="data.within_tolerance" class="ml-1 text-emerald-500">· in tolerance</span>
				<span v-else class="ml-1 text-red-500">· out of tolerance</span>
			</span>
		</template>
	</MetricCard>
</template>

<script setup>
/**
 * CashVarianceHeroCard — Plan §6.4.
 * Green if |variance| < $5, yellow < $20, red >= $20 (REPORTS Phase 5).
 */
import { computed } from 'vue'
import MetricCard from './MetricCard.vue'
import { useFormatters } from '@/composables/useFormatters'

const props = defineProps({
	data: { type: Object, required: true },
	label: { type: String, default: 'Cash Variance' },
})
defineEmits(['open'])
const { formatCurrency } = useFormatters()

const variant = computed(() => {
	const v = Math.abs(Number(props.data?.total_variance || 0))
	if (v < 5) return 'success'
	if (v < 20) return 'warning'
	return 'danger'
})
const iconColor = computed(() => {
	const map = { success: 'var(--green)', warning: 'var(--yellow)', danger: 'var(--red)' }
	return map[variant.value] || 'var(--green)'
})
</script>
