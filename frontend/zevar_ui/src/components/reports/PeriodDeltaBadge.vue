<template>
	<span
		v-if="deltaPct != null"
		class="inline-flex items-center gap-0.5 text-[11px] font-medium"
		:class="colorClass"
	>
		<span class="material-symbols-outlined !text-[14px]">
			{{ deltaPct > 0 ? 'trending_up' : deltaPct < 0 ? 'trending_down' : 'trending_flat' }}
		</span>
		{{ deltaPct > 0 ? '+' : '' }}{{ deltaPct.toFixed(1) }}%
		<span class="text-gray-400 font-normal ml-0.5">{{ label }}</span>
	</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	// Pass either an explicit percentage, or current+previous to derive it.
	current: { type: Number, default: null },
	previous: { type: Number, default: null },
	pct: { type: Number, default: null },
	label: { type: String, default: 'vs prior period' },
})

const deltaPct = computed(() => {
	if (props.pct != null) return Number(props.pct)
	const c = Number(props.current)
	const p = Number(props.previous)
	if (Number.isNaN(c) || Number.isNaN(p)) return null
	if (!p) return null // avoid divide-by-zero / wild deltas on a zero base
	return ((c - p) / Math.abs(p)) * 100
})

const colorClass = computed(() => {
	if (deltaPct.value == null || deltaPct.value === 0) {
		return 'text-gray-500 dark:text-gray-400'
	}
	return deltaPct.value > 0
		? 'text-green-600 dark:text-green-400'
		: 'text-red-600 dark:text-red-400'
})
</script>
