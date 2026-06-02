<template>
	<div class="tab-content">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
			<KPICard label="Total" :value="kpi.total_customers || 0" icon="group" color="blue" :loading="loading" />
			<KPICard label="New (30d)" :value="kpi.new_customers || 0" icon="person_add" color="emerald" :loading="loading" />
			<KPICard label="Active Layaways" :value="kpi.active_layaways || 0" icon="schedule" color="amber" :loading="loading" />
			<KPICard label="Repeat Rate" :value="repeatRate" icon="autorenew" color="purple" :loading="loading" />
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
			<div class="premium-card">
				<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">New vs Returning</h3>
				<div v-if="loading" class="h-32 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
				<div v-else class="space-y-2">
					<div class="flex items-center gap-3">
						<span class="text-xs w-24 text-gray-600 dark:text-gray-300">New</span>
						<div class="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-3 overflow-hidden">
							<div class="h-full bg-emerald-500 transition-all" :style="{ width: pctNew + '%' }" />
						</div>
						<span class="text-xs font-mono text-gray-900 dark:text-white">{{ split.new || 0 }}</span>
					</div>
					<div class="flex items-center gap-3">
						<span class="text-xs w-24 text-gray-600 dark:text-gray-300">Returning</span>
						<div class="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-3 overflow-hidden">
							<div class="h-full bg-blue-500 transition-all" :style="{ width: pctReturning + '%' }" />
						</div>
						<span class="text-xs font-mono text-gray-900 dark:text-white">{{ split.returning || 0 }}</span>
					</div>
				</div>
			</div>

			<div class="premium-card">
				<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Top Customers</h3>
				<div v-if="loading" class="space-y-2">
					<div v-for="n in 4" :key="n" class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
				</div>
				<div v-else-if="!top.length" class="text-xs text-gray-400 text-center py-6">No data</div>
				<div v-else class="space-y-1">
					<div v-for="(c, i) in top" :key="c.name" class="flex items-center gap-3 px-2 py-1.5 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]">
						<span class="text-[10px] font-black text-gray-400 w-4">{{ i + 1 }}</span>
						<span class="text-xs font-bold flex-1 truncate text-gray-900 dark:text-white">{{ c.customer_name || c.name }}</span>
						<span class="text-xs font-mono text-emerald-600 dark:text-emerald-400">${{ fmt(c.total) }}</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
/**
 * CustomersTab — Plan §7.1, 160 LOC budget.
 */
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import KPICard from '@/components/reports/KPICard.vue'

const kpi = ref({})
const split = ref({})
const top = ref([])
const loading = ref(true)

const total = computed(() => Number(split.value.new || 0) + Number(split.value.returning || 0))
const pctNew = computed(() => (total.value ? (Number(split.value.new || 0) / total.value) * 100 : 0))
const pctReturning = computed(() => (total.value ? (Number(split.value.returning || 0) / total.value) * 100 : 0))
const repeatRate = computed(() => {
	const t = Number(kpi.value.total_customers || 0)
	const r = Number(kpi.value.returning || split.value.returning || 0)
	return t > 0 ? ((r / t) * 100).toFixed(1) + '%' : '0%'
})

async function load() {
	loading.value = true
	try {
		const data = await call('zevar_core.api.customer_dashboard.get_dashboard_data', {})
		kpi.value = data?.kpi || {}
		split.value = data?.new_vs_returning || {}
		top.value = data?.top_customers || []
	} catch (e) {
		console.error('CustomersTab load:', e)
	} finally {
		loading.value = false
	}
}
onMounted(load)

function fmt(n) { if (n == null) return '0.00'; return Number(n).toFixed(2) }
</script>
