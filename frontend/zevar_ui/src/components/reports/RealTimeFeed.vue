<template>
	<div class="premium-card !p-3 sm:!p-5">
		<div class="flex items-center justify-between mb-3">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
				<span class="material-symbols-outlined !text-lg text-blue-500">rss_feed</span>
				{{ title }}
			</h3>
			<div class="flex items-center gap-1">
				<span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
				<span class="text-[10px] text-gray-400">Live</span>
			</div>
		</div>
		<div v-if="loading" class="space-y-2">
			<div v-for="n in 4" :key="n" class="h-12 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
		</div>
		<div v-else-if="items.length" class="space-y-1.5 max-h-64 overflow-y-auto">
			<div
				v-for="(item, i) in items"
				:key="i"
				class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition text-xs"
			>
				<div class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></div>
				<span class="font-bold text-gray-900 dark:text-white shrink-0 w-20 truncate">
					{{ item.customer || 'Walk-in' }}
				</span>
				<span class="flex-1 text-gray-500 truncate">
					{{ item.units || 0 }} unit{{ item.units !== 1 ? 's' : '' }}
				</span>
				<span class="font-black text-emerald-600 dark:text-emerald-400 shrink-0">
					${{ fmt(item.amount) }}
				</span>
				<span class="text-[10px] text-gray-400 shrink-0 w-16 text-right">
					{{ formatTime(item.timestamp) }}
				</span>
			</div>
		</div>
		<p v-else class="text-xs text-gray-400 text-center py-6">No recent transactions</p>
	</div>
</template>

<script setup>
import { fmt } from '@/utils/format'

defineProps({
	items: { type: Array, default: () => [] },
	title: { type: String, default: 'Recent Transactions' },
	loading: { type: Boolean, default: false },
})

function formatTime(ts) {
	if (!ts) return ''
	try {
		return new Date(ts).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
	} catch {
		return String(ts)
	}
}
</script>
