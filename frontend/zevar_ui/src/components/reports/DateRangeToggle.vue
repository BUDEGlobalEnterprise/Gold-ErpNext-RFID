<template>
	<div class="flex items-center gap-1 flex-wrap">
		<button
			v-for="preset in presets"
			:key="preset.key"
			@click="timeStore.quickPreset(preset.key)"
			class="px-2.5 py-1 text-[10px] font-bold rounded-lg border transition-colors"
			:class="
				timeStore.presetKind === preset.key
					? 'bg-[#D4AF37] text-white border-[#D4AF37]'
					: 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:border-[#D4AF37]'
			"
		>
			{{ preset.label }}
		</button>
		<div class="flex items-center gap-1 ml-1">
			<input
				type="date"
				:value="timeStore.from"
				@change="timeStore.setRange($event.target.value, timeStore.to)"
				class="px-2 py-1 text-[10px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-[#D4AF37] max-w-[130px]"
			/>
			<span class="text-[10px] text-gray-400">to</span>
			<input
				type="date"
				:value="timeStore.to"
				@change="timeStore.setRange(timeStore.from, $event.target.value)"
				class="px-2 py-1 text-[10px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-[#D4AF37] max-w-[130px]"
			/>
		</div>
	</div>
</template>

<script setup>
import { useTimeStore } from '@/stores/time'

const timeStore = useTimeStore()

const presets = [
	{ key: 'today', label: 'Today' },
	{ key: 'week', label: 'This Week' },
	{ key: 'month', label: 'This Month' },
	{ key: 'ytd', label: 'YTD' },
]
</script>
