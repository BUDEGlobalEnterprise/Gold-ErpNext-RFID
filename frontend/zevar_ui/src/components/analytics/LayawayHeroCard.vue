<template>
	<MetricCard
		:label="label"
		:value="data.total_outstanding"
		format="currency"
		icon="schedule"
		icon-color="var(--color-gold)"
		:badge="data.overdue || 0"
		:badge-severity="data.overdue > 0 ? 'high' : 'low'"
		:aria-label="`Layaway outstanding: ${formatCurrency(data.total_outstanding)}; ${data.overdue || 0} overdue`"
		@click="$emit('open')"
	>
		<template #footer>
			<span class="font-mono">
				{{ data.active || 0 }} active
				<span v-if="data.due_this_week" class="ml-1 text-amber-500">
					· {{ data.due_this_week }} due 7d
				</span>
			</span>
		</template>
	</MetricCard>
</template>

<script setup>
/**
 * LayawayHeroCard — Plan §6.2.
 */
import MetricCard from './MetricCard.vue'
import { useFormatters } from '@/composables/useFormatters'
defineProps({
	data: { type: Object, required: true },
	label: { type: String, default: 'Layaways' },
})
defineEmits(['open'])
const { formatCurrency } = useFormatters()
</script>
