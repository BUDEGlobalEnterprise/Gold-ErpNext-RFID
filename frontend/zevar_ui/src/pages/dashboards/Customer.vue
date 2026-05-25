<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0 flex-wrap">
				<button @click="$router.push('/reports')" class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors">
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-purple-500/10">
					<span class="material-symbols-outlined !text-xl text-purple-500">group</span>
				</div>
				<div>
					<h2 class="premium-title !text-xl">Customer Dashboard</h2>
					<p class="text-[10px] text-gray-400">New vs returning, LTV, layaway cohort, repair NPS</p>
				</div>
				<button @click="refresh" class="ml-auto w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-purple-500 transition-colors" :class="{ 'animate-spin': loading }">
					<span class="material-symbols-outlined !text-base">refresh</span>
				</button>
			</div>

			<div class="flex-1 overflow-auto space-y-4 pr-1">
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
					<KPICard label="Total Customers" :value="kpi.total_customers" icon="group" color="purple" :loading="loading" />
					<KPICard label="New This Month" :value="kpi.new_customers" icon="person_add" color="blue" :loading="loading" />
					<KPICard label="Avg Lifetime Value" :value="'$' + fmt(kpi.avg_ltv)" icon="diamond" color="emerald" :loading="loading" />
					<KPICard label="Active Layaways" :value="kpi.active_layaways" icon="event_repeat" color="amber" :loading="loading" />
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<!-- New vs Returning -->
					<div class="premium-card !p-3 sm:!p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">New vs Returning</h3>
						<div v-if="loading" class="flex gap-3">
							<div class="flex-1 h-20 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse"></div>
							<div class="flex-1 h-20 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse"></div>
						</div>
						<div v-else class="flex gap-3">
							<div class="flex-1 bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 text-center">
								<p class="text-2xl font-black text-purple-700 dark:text-purple-300">{{ newVsReturning.new || 0 }}</p>
								<p class="text-[10px] font-bold text-purple-500 uppercase">New</p>
							</div>
							<div class="flex-1 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
								<p class="text-2xl font-black text-blue-700 dark:text-blue-300">{{ newVsReturning.returning || 0 }}</p>
								<p class="text-[10px] font-bold text-blue-500 uppercase">Returning</p>
							</div>
						</div>
					</div>

					<!-- Top Customers -->
					<div class="premium-card !p-3 sm:!p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Top Customers by Revenue</h3>
						<div v-if="loading" class="space-y-2">
							<div v-for="n in 3" :key="n" class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
						</div>
						<div v-else-if="topCustomers.length" class="space-y-2">
							<div v-for="(c, i) in topCustomers" :key="c.customer_id || c.name" class="flex items-center gap-3">
								<span class="text-[10px] font-black text-gray-400 w-4">{{ i + 1 }}</span>
								<span class="text-xs font-bold text-gray-900 dark:text-white flex-1 truncate">{{ c.name }}</span>
								<span class="text-xs font-black text-purple-600 dark:text-purple-400">${{ fmt(c.total) }}</span>
							</div>
						</div>
						<p v-else class="text-xs text-gray-400 text-center py-4">No customer data</p>
					</div>
				</div>

				<!-- Layaway Cohort -->
				<div class="premium-card !p-3 sm:!p-5">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Layaway Cohort Retention</h3>
					<p class="text-xs text-gray-500 dark:text-gray-400">Showing active layaway completion rate by month of origination.</p>
					<div v-if="loading" class="mt-3 h-40 flex items-center justify-center">
						<span class="material-symbols-outlined animate-spin text-gray-300">progress_activity</span>
					</div>
					<div v-else-if="cohortData.length" class="mt-3 h-32 sm:h-40 overflow-x-auto">
						<div class="flex items-end gap-2 min-w-[300px] h-full">
							<div v-for="(m, i) in cohortData" :key="i" class="flex-1 flex flex-col items-center gap-1 group cursor-default">
								<span class="text-[8px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">{{ m.rate }}%</span>
								<div class="w-full rounded-t bg-purple-500/60 dark:bg-purple-400/40 min-h-[2px] hover:bg-purple-500 transition-colors" :style="{ height: m.height + '%' }"></div>
								<span class="text-[8px] text-gray-400">{{ m.label }}</span>
							</div>
						</div>
					</div>
					<p v-else class="text-xs text-gray-400 text-center py-8 mt-2">No layaway cohort data</p>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { ref } from 'vue'
import KPICard from '@/components/reports/KPICard.vue'

const kpi = ref({ total_customers: 0, new_customers: 0, avg_ltv: 0, active_layaways: 0, returning: 0 })
const newVsReturning = ref({ new: 0, returning: 0 })
const topCustomers = ref([])
const cohortData = ref([])
const loading = ref(true)
const error = ref(null)

async function refresh() {
	loading.value = true
	error.value = null
	try {
		const res = await fetch('/api/method/zevar_core.api.customer_dashboard.get_dashboard_data', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		if (!res.ok) throw new Error('Failed to load customer data')
		const json = await res.json()
		const data = json.message || json
		kpi.value = data.kpi || kpi.value
		newVsReturning.value = data.new_vs_returning || newVsReturning.value
		topCustomers.value = data.top_customers || []
		cohortData.value = data.layaway_cohort || []
	} catch (e) {
		error.value = e.message
		console.error('Customer dashboard error:', e)
	} finally {
		loading.value = false
	}
}

refresh()

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}
</script>
