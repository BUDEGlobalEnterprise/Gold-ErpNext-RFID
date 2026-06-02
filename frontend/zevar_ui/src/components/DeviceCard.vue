<template>
	<div
		class="premium-card !p-4 flex flex-col gap-2"
		:class="statusBorder"
	>
		<div class="flex items-center justify-between gap-2">
			<h4 class="text-sm font-bold text-gray-900 dark:text-white">
				{{ title }}
			</h4>
			<span
				class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded"
				:class="statusBadge"
			>
				{{ statusLabel }}
			</span>
		</div>
		<p v-if="hint" class="text-xs text-gray-500 dark:text-gray-400">
			{{ hint }}
		</p>
		<slot />
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	title: { type: String, required: true },
	status: { type: String, default: 'idle' },
	hint: { type: String, default: '' },
})

const statusLabel = computed(() => {
	switch (props.status) {
		case 'running':
			return 'Running'
		case 'success':
			return 'OK'
		case 'error':
			return 'Failed'
		default:
			return 'Ready'
	}
})

const statusBadge = computed(() => {
	switch (props.status) {
		case 'running':
			return 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'
		case 'success':
			return 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
		case 'error':
			return 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
		default:
			return 'bg-gray-100 text-gray-600 dark:bg-warm-dark-700 dark:text-gray-400'
	}
})

const statusBorder = computed(() => {
	switch (props.status) {
		case 'success':
			return 'border-green-200 dark:border-green-800'
		case 'error':
			return 'border-red-200 dark:border-red-800'
		case 'running':
			return 'border-amber-200 dark:border-amber-800'
		default:
			return ''
	}
})
</script>
