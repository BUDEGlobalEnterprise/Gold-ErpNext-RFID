<template>
	<div
		class="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider transition-all duration-300 cursor-pointer"
		:class="indicatorClass"
		@click="handleClick"
	>
		<!-- Status dot -->
		<span class="relative flex h-2 w-2">
			<span
				v-if="offline.statusColor === 'green'"
				class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
			></span>
			<span
				class="relative inline-flex rounded-full h-2 w-2"
				:class="{
					'bg-green-500': offline.statusColor === 'green',
					'bg-amber-500': offline.statusColor === 'amber',
					'bg-red-500': offline.statusColor === 'red',
				}"
			></span>
		</span>

		{{ offline.statusLabel }}

		<!-- Pending badge -->
		<span
			v-if="offline.pendingCount > 0"
			class="ml-0.5 w-4 h-4 flex items-center justify-center rounded-full bg-amber-500 text-white text-[9px] font-black"
		>
			{{ offline.pendingCount }}
		</span>

		<!-- Conflict badge -->
		<span
			v-if="offline.conflictCount > 0"
			class="ml-0.5 w-4 h-4 flex items-center justify-center rounded-full bg-red-500 text-white text-[9px] font-black"
		>
			{{ offline.conflictCount }}
		</span>

		<!-- Sync button (visible when pending + online) -->
		<button
			v-if="offline.pendingCount > 0 && offline.isOnline && !offline.syncing"
			@click.stop="offline.syncPendingOrders()"
			class="ml-1 p-0.5 rounded hover:bg-white/20 transition"
			title="Sync now"
		>
			<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
				/>
			</svg>
		</button>

		<!-- Syncing spinner -->
		<svg
			v-if="offline.syncing"
			class="w-3 h-3 animate-spin ml-1"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<circle cx="12" cy="12" r="10" stroke-width="3" class="opacity-25"></circle>
			<path
				stroke-width="3"
				class="opacity-75"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
			/>
		</svg>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { computed } from 'vue'
import { useOfflineStore } from '@/stores/offline.js'

const offline = useOfflineStore()
const emit = defineEmits(['show-sync-logs'])

const indicatorClass = computed(() => {
	switch (offline.statusColor) {
		case 'red':
			return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800/30'
		case 'amber':
			return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border border-amber-200 dark:border-amber-800/30'
		default:
			return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800/30'
	}
})

function handleClick() {
	emit('show-sync-logs')
}
</script>
