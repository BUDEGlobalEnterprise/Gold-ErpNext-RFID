<template>
	<MetricCard
		:label="label"
		:value="data.total_count"
		format="number"
		icon="bookmark"
		icon-color="var(--purple)"
		:badge="data.expiring_soon_count"
		:badge-severity="data.expiring_soon_count > 0 ? 'high' : 'low'"
		:aria-label="`Hold queue: ${data.total_count} active, ${data.expiring_soon_count} expiring soon`"
		@click="$emit('open')"
	>
		<template #footer>
			<span class="font-mono">
				{{ data.total_count || 0 }} active
				<span v-if="data.expiring_soon_count" class="ml-1 text-amber-500">
					· {{ data.expiring_soon_count }} expiring
				</span>
			</span>
		</template>
	</MetricCard>
</template>

<script setup>
/**
 * HoldQueueHeroCard — Plan §6.6.
 */
import MetricCard from './MetricCard.vue'
defineProps({
	data: { type: Object, required: true },
	label: { type: String, default: 'Hold Items' },
})
defineEmits(['open'])
</script>
