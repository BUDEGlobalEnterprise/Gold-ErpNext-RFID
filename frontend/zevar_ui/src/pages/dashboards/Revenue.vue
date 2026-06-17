<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0 flex-wrap">
				<button
					@click="$router.push('/reports')"
					class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors"
				>
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div
					class="w-10 h-10 rounded-xl flex items-center justify-center bg-emerald-500/10"
				>
					<span class="material-symbols-outlined !text-xl text-emerald-500"
						>monitoring</span
					>
				</div>
				<div>
					<h2 class="premium-title !text-xl">Revenue Dashboard</h2>
					<p class="text-[10px] text-gray-400">
						Sales vs last year, category, hourly, salesperson
					</p>
				</div>
				<button
					@click="refresh"
					class="ml-auto w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-emerald-500 transition-colors"
					:class="{ 'animate-spin': loading }"
				>
					<span class="material-symbols-outlined !text-base">refresh</span>
				</button>
			</div>

			<div class="flex-1 overflow-auto space-y-4 pr-1">
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
					<KPICard
						label="Today's Sales"
						:value="'$' + fmt(summary.today_sales)"
						icon="payments"
						color="emerald"
						:loading="loading"
					/>
					<KPICard
						label="Transactions"
						:value="summary.txn_count"
						icon="receipt"
						color="blue"
						:loading="loading"
					/>
					<KPICard
						label="Avg Ticket"
						:value="'$' + fmt(summary.avg_ticket)"
						icon="sell"
						color="purple"
						:loading="loading"
					/>
					<KPICard
						label="vs Last Year"
						:value="(summary.yoy_pct >= 0 ? '+' : '') + summary.yoy_pct + '%'"
						icon="trending_up"
						color="amber"
						:loading="loading"
					/>
				</div>

				<!-- Hourly Chart -->
				<div class="premium-card !p-3 sm:!p-5">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
						Hourly Sales Distribution
					</h3>
					<div v-if="loading" class="h-40 sm:h-64 flex items-center justify-center">
						<span class="material-symbols-outlined animate-spin text-gray-300"
							>progress_activity</span
						>
					</div>
					<EChart
						v-else-if="hourlyData.length"
						:option="hourlyOption"
						height="256px"
					/>
					<p v-else class="text-xs text-gray-400 text-center py-8">
						No sales data for today
					</p>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<!-- Category Breakdown -->
					<div class="premium-card !p-3 sm:!p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Category Breakdown
						</h3>
						<div v-if="loading" class="space-y-2">
							<div
								v-for="n in 4"
								:key="n"
								class="h-4 bg-gray-100 dark:bg-gray-800 rounded-full animate-pulse"
							></div>
						</div>
						<div v-else-if="categoryData.length" class="space-y-2">
							<div
								v-for="cat in categoryData"
								:key="cat.category"
								class="flex items-center gap-3"
							>
								<div
									class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-4 overflow-hidden"
								>
									<div
										class="h-full rounded-full bg-[#D4AF37] transition-all"
										:style="{ width: cat.pct + '%' }"
									></div>
								</div>
								<span
									class="text-[10px] font-bold text-gray-600 dark:text-gray-300 shrink-0 w-24 text-right truncate"
									>{{ cat.category }}</span
								>
								<span
									class="text-[10px] font-bold text-gray-900 dark:text-white shrink-0"
									>${{ fmt(cat.total) }}</span
								>
							</div>
						</div>
						<p v-else class="text-xs text-gray-400 text-center py-4">
							No category data
						</p>
					</div>

					<!-- Top Salespersons -->
					<div class="premium-card !p-3 sm:!p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Top Salespersons
						</h3>
						<div v-if="loading" class="space-y-2">
							<div
								v-for="n in 3"
								:key="n"
								class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
							></div>
						</div>
						<div v-else-if="topSalespeople.length" class="space-y-2">
							<div
								v-for="(sp, i) in topSalespeople"
								:key="sp.employee_id || sp.name"
								class="flex items-center gap-3"
							>
								<span class="text-[10px] font-black text-gray-400 w-4">{{
									i + 1
								}}</span>
								<span
									class="text-xs font-bold text-gray-900 dark:text-white flex-1 truncate"
									>{{ sp.name }}</span
								>
								<span
									class="text-xs font-black text-emerald-600 dark:text-emerald-400"
									>${{ fmt(sp.total) }}</span
								>
							</div>
						</div>
						<p v-else class="text-xs text-gray-400 text-center py-4">
							No salesperson data
						</p>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import EChart from '@/components/charts/EChart.vue'
import { fmt } from '@/utils/format'
import { computed, ref } from 'vue'
import KPICard from '@/components/reports/KPICard.vue'

const summary = ref({ today_sales: 0, txn_count: 0, avg_ticket: 0, yoy_pct: 0 })
const hourlyData = ref([])

// ECharts option for the hourly bar chart (Q9 — replaces the bespoke CSS bars).
const hourlyOption = computed(() => ({
	grid: { left: 8, right: 8, top: 16, bottom: 8, containLabel: true },
	tooltip: {
		trigger: 'axis',
		formatter: (p) => `${p[0].name} → $${fmt(p[0].value)}`,
	},
	xAxis: {
		type: 'category',
		data: hourlyData.value.map((b) => b.label),
		axisLabel: { fontSize: 10, color: '#9ca3af' },
		axisLine: { lineStyle: { color: '#374151' } },
	},
	yAxis: {
		type: 'value',
		splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
		axisLabel: { fontSize: 10, color: '#9ca3af' },
	},
	series: [
		{
			type: 'bar',
			data: hourlyData.value.map((b) => Number(b.total || 0)),
			itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] },
			barMaxWidth: 28,
		},
	],
}))
const categoryData = ref([])
const topSalespeople = ref([])
const loading = ref(true)
const error = ref(null)

async function refresh() {
	loading.value = true
	error.value = null
	try {
		const res = await fetch(
			'/api/method/zevar_core.api.revenue_dashboard.get_dashboard_data',
			{
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
			}
		)
		if (!res.ok) throw new Error('Failed to load revenue data')
		const json = await res.json()
		const data = json.message || json
		summary.value = data.summary || summary.value
		hourlyData.value = data.hourly || []
		categoryData.value = data.categories || []
		topSalespeople.value = data.top_salespersons || []
	} catch (e) {
		error.value = e.message
		console.error('Revenue dashboard error:', e)
	} finally {
		loading.value = false
	}
}

refresh()
</script>
