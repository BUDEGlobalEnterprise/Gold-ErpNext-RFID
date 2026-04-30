<template>
	<span v-if="delta" class="inline-flex items-center gap-0.5 text-[9px] font-bold" :class="badgeClass">
		<span class="material-symbols-outlined !text-xs">{{ delta.pct >= 0 ? 'trending_up' : 'trending_down' }}</span>
		{{ delta.pct >= 0 ? '+' : '' }}{{ delta.pct }}% vs LY
	</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ delta: { type: Object, default: null } })

const badgeClass = computed(() => {
	if (!props.delta) return ''
	if (props.delta.pct >= 0) return 'text-emerald-600 dark:text-emerald-400'
	return 'text-red-600 dark:text-red-400'
})
</script>
