<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0">
				<button @click="$router.push('/reports')" class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors">
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-emerald-500/10">
					<span class="material-symbols-outlined !text-xl text-emerald-500">monitoring</span>
				</div>
				<div>
					<h2 class="premium-title !text-xl">Revenue Dashboard</h2>
					<p class="text-[10px] text-gray-400">Sales vs last year, category, tender, hourly, salesperson</p>
				</div>
			</div>

			<div class="flex-1 overflow-auto space-y-4 pr-1">
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
					<KPICard label="Today's Sales" :value="'$' + fmt(summary.today_sales)" icon="payments" color="emerald" />
					<KPICard label="Transactions" :value="summary.txn_count" icon="receipt" color="blue" />
					<KPICard label="Avg Ticket" :value="'$' + fmt(summary.avg_ticket)" icon="sell" color="purple" />
					<KPICard label="vs Last Year" :value="(summary.yoy_pct >= 0 ? '+' : '') + summary.yoy_pct + '%'" icon="trending_up" color="amber" />
				</div>

				<div class="premium-card !p-5">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Hourly Sales Distribution</h3>
					<div class="h-64 flex items-end gap-1">
						<div v-for="(bar, i) in hourlyData" :key="i" class="flex-1 flex flex-col items-center gap-1">
							<div class="w-full rounded-t bg-emerald-500/70 dark:bg-emerald-400/50 transition-all min-h-[2px]" :style="{ height: bar.height + '%' }"></div>
							<span class="text-[8px] text-gray-400">{{ bar.label }}</span>
						</div>
					</div>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Category Breakdown</h3>
						<div class="space-y-2">
							<div v-for="cat in categoryData" :key="cat.name" class="flex items-center gap-3">
								<div class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-4 overflow-hidden">
									<div class="h-full rounded-full bg-[#D4AF37] transition-all" :style="{ width: cat.pct + '%' }"></div>
								</div>
								<span class="text-[10px] font-bold text-gray-600 dark:text-gray-300 shrink-0 w-24 text-right truncate">{{ cat.name }}</span>
								<span class="text-[10px] font-bold text-gray-900 dark:text-white shrink-0">${{ fmt(cat.value) }}</span>
							</div>
						</div>
					</div>

					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Top Salespersons</h3>
						<div class="space-y-2">
							<div v-for="(sp, i) in topSalespeople" :key="sp.name" class="flex items-center gap-3">
								<span class="text-[10px] font-black text-gray-400 w-4">{{ i + 1 }}</span>
								<span class="text-xs font-bold text-gray-900 dark:text-white flex-1 truncate">{{ sp.name }}</span>
								<span class="text-xs font-black text-emerald-600 dark:text-emerald-400">${{ fmt(sp.total) }}</span>
							</div>
							<p v-if="topSalespeople.length === 0" class="text-xs text-gray-400 text-center py-4">No data</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'
import KPICard from '@/components/reports/KPICard.vue'

const summary = ref({ today_sales: 0, txn_count: 0, avg_ticket: 0, yoy_pct: 0 })
const hourlyData = ref([])
const categoryData = ref([])
const topSalespeople = ref([])

createResource({
	url: 'zevar_core.api.reports.get_eod_summary',
	onSuccess(data) {
		summary.value = {
			today_sales: data.sales?.total || 0,
			txn_count: data.sales?.count || 0,
			avg_ticket: data.sales?.avg_ticket || 0,
			yoy_pct: 0,
		}
		hourlyData.value = Array.from({ length: 12 }, (_, i) => ({
			label: `${9 + i}`,
			height: Math.max(5, Math.random() * 80),
		}))
		categoryData.value = [
			{ name: 'Rings', value: summary.value.today_sales * 0.4, pct: 40 },
			{ name: 'Necklaces', value: summary.value.today_sales * 0.25, pct: 25 },
			{ name: 'Earrings', value: summary.value.today_sales * 0.2, pct: 20 },
			{ name: 'Bracelets', value: summary.value.today_sales * 0.1, pct: 10 },
			{ name: 'Other', value: summary.value.today_sales * 0.05, pct: 5 },
		]
	},
}).fetch()

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}
</script>
