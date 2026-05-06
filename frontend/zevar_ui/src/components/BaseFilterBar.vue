<template>
	<div class="relative w-full">
		<div
			class="flex items-center gap-4 overflow-x-auto no-scrollbar transition-colors duration-300 py-1"
		>
			<!-- Icon & Label -->
			<div
				class="flex items-center gap-2 pr-4 border-r border-gray-200 dark:border-warm-border flex-shrink-0"
			>
				<svg
					class="w-4 h-4 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
					/>
				</svg>
				<span class="text-[10px] font-black text-gray-500 uppercase tracking-widest"
					>Filters</span
				>
				<span
					v-if="activeCount > 0"
					class="flex items-center justify-center bg-[#D4AF37] text-white text-[9px] font-bold rounded-full h-4 min-w-[16px] px-1"
				>
					{{ activeCount }}
				</span>
			</div>

			<!-- Dynamic Filters Slot -->
			<slot name="filters"></slot>

			<!-- Sort Slot (Optional) -->
			<div
				v-if="$slots.sort"
				class="border-l border-gray-200 dark:border-warm-border pl-4 ml-auto flex-shrink-0"
			>
				<slot name="sort"></slot>
			</div>

			<!-- Reset Button -->
			<button
				v-if="activeCount > 0"
				@click="ui.resetFilters(context)"
				class="text-[10px] font-black uppercase tracking-widest text-rose-500 hover:text-rose-600 transition-colors whitespace-nowrap ml-2"
			>
				Reset
			</button>
		</div>

		<!-- Teleport Container for Dropdowns -->
		<slot name="dropdowns"></slot>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui.js'

const props = defineProps({
	context: {
		type: String,
		required: true,
	},
})

const ui = useUIStore()

const activeCount = computed(() => {
	return ui.getActiveFilterCount(props.context)
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
</style>
