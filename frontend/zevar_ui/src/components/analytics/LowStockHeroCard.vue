<template>
	<MetricCard
		:label="label"
		:value="total"
		format="number"
		icon="inventory_2"
		icon-color="var(--yellow)"
		:badge="stockout"
		:badge-severity="stockout > 0 ? 'critical' : total > 0 ? 'med' : 'low'"
		:aria-label="`Low stock: ${total} items, ${stockout} stockouts`"
		@click="$emit('open')"
	>
		<template #footer>
			<span class="font-mono">
				{{ total - stockout }} low
				<span v-if="stockout" class="ml-1 text-red-500">· {{ stockout }} stockout</span>
			</span>
		</template>
	</MetricCard>
</template>

<script setup>
/**
 * LowStockHeroCard — Plan §6.3.
 */
import { computed } from 'vue'
import MetricCard from './MetricCard.vue'

const props = defineProps({
	data: { type: Object, required: true },
	label: { type: String, default: 'Low Stock' },
})
defineEmits(['open'])
const total = computed(() => Number(props.data?.total || 0))
const stockout = computed(() => Number(props.data?.stockout || 0))
</script>
