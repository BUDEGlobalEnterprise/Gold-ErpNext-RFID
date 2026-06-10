<template>
	<div class="tab-content">
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
			<div class="premium-card">
				<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Hourly Sales</h3>
				<div v-if="loading" class="h-40 flex items-center justify-center">
					<span class="material-symbols-outlined animate-spin text-gray-300"
						>progress_activity</span
					>
				</div>
				<div v-else-if="!hourly.length" class="text-xs text-gray-400 text-center py-8">
					No hourly data
				</div>
				<div v-else class="h-40 flex items-end gap-1">
					<div
						v-for="(b, i) in hourly"
						:key="i"
						class="flex-1 rounded-t bg-emerald-500/70 dark:bg-emerald-400/50 min-h-[2px] hover:bg-emerald-500 transition-all"
						:style="{ height: b.height + '%' }"
						:title="`${b.label}: $${fmt(b.total)}`"
					/>
				</div>
			</div>

			<div class="premium-card">
				<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
					Category Breakdown
				</h3>
				<div v-if="loading" class="space-y-2">
					<div
						v-for="n in 4"
						:key="n"
						class="h-3 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
					/>
				</div>
				<div v-else-if="!categories.length" class="text-xs text-gray-400 text-center py-8">
					No data
				</div>
				<div v-else class="space-y-2">
					<div v-for="c in categories" :key="c.category" class="flex items-center gap-3">
						<div
							class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-3 overflow-hidden"
						>
							<div
								class="h-full rounded-full bg-[#D4AF37] transition-all"
								:style="{ width: c.pct + '%' }"
							/>
						</div>
						<span
							class="text-[10px] font-bold w-20 truncate text-right text-gray-700 dark:text-gray-300"
							>{{ c.category }}</span
						>
						<span class="text-[10px] font-bold font-mono text-gray-900 dark:text-white"
							>${{ fmt(c.total) }}</span
						>
					</div>
				</div>
			</div>
		</div>

		<div class="premium-card mt-4">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Top Salespeople</h3>
			<div v-if="loading" class="space-y-2">
				<div
					v-for="n in 3"
					:key="n"
					class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
				/>
			</div>
			<div v-else-if="!salespeople.length" class="text-xs text-gray-400 text-center py-6">
				No data
			</div>
			<div v-else class="space-y-1">
				<div
					v-for="(sp, i) in salespeople"
					:key="sp.name"
					class="flex items-center gap-3 px-2 py-1.5 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]"
				>
					<span class="text-[10px] font-black text-gray-400 w-4">{{ i + 1 }}</span>
					<span
						class="text-xs font-bold flex-1 truncate text-gray-900 dark:text-white"
						>{{ sp.name }}</span
					>
					<span
						class="text-xs font-black font-mono text-emerald-600 dark:text-emerald-400"
						>${{ fmt(sp.total) }}</span
					>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
/**
 * RevenueTab — Plan §7.1, 180 LOC budget.
 * Reuses the existing revenue_dashboard.get_dashboard_data API.
 */
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'

const hourly = ref([])
const categories = ref([])
const salespeople = ref([])
const loading = ref(true)

async function load() {
	loading.value = true
	try {
		const data = await call('zevar_core.api.revenue_dashboard.get_dashboard_data', {})
		hourly.value = data?.hourly || []
		categories.value = data?.categories || []
		salespeople.value = data?.top_salespersons || []
	} catch (e) {
		console.error('RevenueTab load:', e)
	} finally {
		loading.value = false
	}
}
onMounted(load)

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}
</script>
