<template>
	<MetricCard
		:label="label"
		:value="data.repair_revenue"
		format="currency"
		icon="build"
		icon-color="var(--blue)"
		:sparkline="sparkPoints"
		:aria-label="`Repair revenue: ${formatCurrency(data.repair_revenue)}`"
		@click="$emit('open')"
	>
		<template #footer>
			<span class="font-mono">{{ data.repair_count || 0 }} delivered</span>
		</template>
	</MetricCard>
</template>

<script setup>
/**
 * RepairHeroCard — Plan §6.1.
 */
import { computed } from 'vue'
import MetricCard from './MetricCard.vue'
import { useFormatters } from '@/composables/useFormatters'

const props = defineProps({
	data: { type: Object, required: true },
	label: { type: String, default: 'Repair Revenue' },
})
defineEmits(['open'])
const { formatCurrency } = useFormatters()
const sparkPoints = computed(() => (props.data?.sparkline_30d || []).map((p) => ({ date: p.date, value: Number(p.repair || 0) })))
</script>
