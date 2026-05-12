<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<!-- Header -->
			<div class="flex items-center gap-3 mb-4 flex-shrink-0">
				<button
					@click="$router.push('/reports')"
					class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors"
				>
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-indigo-500/10">
					<span class="material-symbols-outlined !text-xl text-indigo-500">monitoring</span>
				</div>
				<div class="flex-1">
					<h2 class="premium-title !text-xl">Profit Intelligence</h2>
					<p class="text-[10px] text-gray-400">Margins, cost analysis, pricing recommendations</p>
				</div>
				<div class="flex items-center gap-2">
					<input
						type="date"
						v-model="fromDate"
						class="px-2 py-1.5 text-xs border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-400"
					/>
					<span class="text-xs text-gray-400">to</span>
					<input
						type="date"
						v-model="toDate"
						class="px-2 py-1.5 text-xs border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-indigo-400"
					/>
					<button
						@click="refresh"
						:disabled="store.loading"
						class="px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
					>
						Refresh
					</button>
				</div>
			</div>

			<!-- Tabs -->
			<div class="border-b border-gray-200 dark:border-gray-700 mb-4 flex-shrink-0">
				<nav class="flex space-x-4 overflow-x-auto">
					<button
						v-for="tab in tabs"
						:key="tab.key"
						@click="activeTab = tab.key"
						:class="[
							activeTab === tab.key
								? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
								: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300',
							'whitespace-nowrap py-2.5 px-1 border-b-2 font-medium text-xs transition-colors',
						]"
					>
						{{ tab.label }}
					</button>
				</nav>
			</div>

			<!-- Content area -->
			<div class="flex-1 overflow-auto">
				<!-- Loading -->
				<div v-if="store.loading" class="flex flex-col items-center justify-center py-20 gap-3">
					<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
					<p class="text-xs text-gray-400">Loading profit data...</p>
				</div>

				<!-- Error -->
				<div
					v-else-if="store.error"
					class="mx-auto max-w-md mt-12 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
				>
					<p class="text-sm text-red-600 dark:text-red-400">{{ store.error }}</p>
					<button
						@click="refresh"
						class="mt-2 text-xs font-medium text-red-700 dark:text-red-300 underline"
					>
						Try again
					</button>
				</div>

				<!-- Tab panels -->
				<template v-else>
					<ProfitOverview v-if="activeTab === 'overview'" />
					<CostBreakdownChart v-else-if="activeTab === 'cost'" />
					<div v-else-if="activeTab === 'pricing'" class="space-y-6">
						<PricingRecommendationsPanel />
						<WhatIfSimulator />
					</div>
					<MarginHeatmap v-else-if="activeTab === 'heatmap'" />
				</template>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useProfitStore } from '@/stores/profit'
import ProfitOverview from '@/components/profit/ProfitOverview.vue'
import CostBreakdownChart from '@/components/profit/CostBreakdownChart.vue'
import PricingRecommendationsPanel from '@/components/pricing/PricingRecommendationsPanel.vue'
import WhatIfSimulator from '@/components/pricing/WhatIfSimulator.vue'
import MarginHeatmap from '@/components/profit/MarginHeatmap.vue'

const store = useProfitStore()

const activeTab = ref('overview')

const tabs = [
	{ key: 'overview', label: 'Overview' },
	{ key: 'cost', label: 'Cost Analysis' },
	{ key: 'pricing', label: 'Pricing' },
	{ key: 'heatmap', label: 'Margin Heatmap' },
]

// Default date range: last 90 days
const now = new Date()
const ninetyDaysAgo = new Date(now)
ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90)

const fromDate = ref(ninetyDaysAgo.toISOString().slice(0, 10))
const toDate = ref(now.toISOString().slice(0, 10))

function refresh() {
	store.loadAll(fromDate.value, toDate.value)
}

onMounted(() => {
	refresh()
})
</script>
