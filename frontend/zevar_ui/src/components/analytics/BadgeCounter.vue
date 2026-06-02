<template>
	<span
		class="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1.5 rounded-full text-[10px] font-black leading-none"
		:class="cls"
	>
		{{ formatted }}
	</span>
</template>

<script setup>
/**
 * BadgeCounter — Plan §7.6, 40 LOC budget.
 * Severity badge: low / med / high / critical.
 */
import { computed } from 'vue'

const props = defineProps({
	value: { type: [Number, String], default: 0 },
	severity: { type: String, default: 'low' },
})

const formatted = computed(() => {
	const n = Number(props.value) || 0
	if (n > 99) return '99+'
	return n
})

const cls = computed(() => {
	const map = {
		low: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
		med: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
		high: 'bg-orange-500/15 text-orange-600 dark:text-orange-400',
		critical: 'bg-red-500/15 text-red-600 dark:text-red-400',
	}
	return map[props.severity] || map.low
})
</script>
