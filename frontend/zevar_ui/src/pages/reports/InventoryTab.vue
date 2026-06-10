<template>
	<div class="tab-content">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
			<KPICard
				label="Total SKUs"
				:value="kpi.total_items || 0"
				icon="category"
				color="blue"
				:loading="loading"
			/>
			<KPICard
				label="Inventory Value"
				:value="`$${fmt(kpi.total_value)}`"
				icon="payments"
				color="emerald"
				:loading="loading"
			/>
			<KPICard
				label="Low Stock"
				:value="kpi.low_stock || 0"
				icon="warning"
				color="amber"
				:loading="loading"
			/>
			<KPICard
				label="Aging 90+"
				:value="kpi.aging_90 || 0"
				icon="schedule"
				color="orange"
				:loading="loading"
			/>
		</div>

		<div class="premium-card mt-4">
			<div class="flex items-center justify-between mb-3">
				<h3 class="text-sm font-bold text-gray-900 dark:text-white">Aging Buckets</h3>
				<button class="text-[10px] font-bold text-[#D4AF37] hover:underline">
					View all
				</button>
			</div>
			<div v-if="loading" class="space-y-2">
				<div
					v-for="n in 4"
					:key="n"
					class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
				/>
			</div>
			<div v-else-if="!buckets.length" class="text-xs text-gray-400 text-center py-6">
				No aging data
			</div>
			<div v-else class="space-y-1.5">
				<div v-for="b in buckets" :key="b.label" class="flex items-center gap-3">
					<span class="text-xs font-mono w-24 text-gray-600 dark:text-gray-300"
						>{{ b.label }}d</span
					>
					<div
						class="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-3 overflow-hidden"
					>
						<div
							class="h-full rounded-full transition-all"
							:class="bucketColor(b.label)"
							:style="{ width: b.pct + '%' }"
						/>
					</div>
					<span
						class="text-[10px] font-bold font-mono w-12 text-right text-gray-900 dark:text-white"
						>{{ b.count }} items</span
					>
					<span class="text-[10px] font-mono w-14 text-right text-gray-500"
						>{{ b.pct.toFixed(0) }}%</span
					>
				</div>
			</div>
		</div>

		<div class="premium-card mt-4">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
				Stock by Warehouse
			</h3>
			<div v-if="loading" class="space-y-2">
				<div
					v-for="n in 3"
					:key="n"
					class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
				/>
			</div>
			<div v-else-if="!warehouses.length" class="text-xs text-gray-400 text-center py-6">
				No data
			</div>
			<div v-else class="space-y-1">
				<div
					v-for="w in warehouses"
					:key="w.warehouse"
					class="flex items-center gap-3 px-2 py-1.5 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]"
				>
					<span class="material-symbols-outlined !text-base text-gray-400"
						>warehouse</span
					>
					<span
						class="text-xs font-bold flex-1 truncate text-gray-900 dark:text-white"
						>{{ w.warehouse }}</span
					>
					<span class="text-xs font-mono text-gray-700 dark:text-gray-300"
						>${{ fmt(w.value) }}</span
					>
					<span class="text-[10px] font-mono text-gray-500 w-12 text-right"></span>
				</div>
			</div>
		</div>

		<OveragePanel />
	</div>
</template>

<script setup>
/**
 * InventoryTab — Plan §7.1, 180 LOC budget.
 * Reuses inventory_dashboard.get_dashboard_data + get_aging_buckets + get_stock_by_warehouse.
 * Overage sub-panel comes from the overage store (Phase 9) once mounted.
 */
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import KPICard from '@/components/reports/KPICard.vue'
import OveragePanel from '@/components/analytics/OveragePanel.vue'

const kpi = ref({})
const buckets = ref([])
const warehouses = ref([])
const loading = ref(true)

async function load() {
	loading.value = true
	try {
		const [data, ag, wh] = await Promise.all([
			call('zevar_core.api.inventory_dashboard.get_dashboard_data', {}),
			call('zevar_core.api.inventory_dashboard.get_aging_buckets', {}).catch(() => []),
			call('zevar_core.api.inventory_dashboard.get_stock_by_warehouse', {}).catch(() => []),
		])
		const kpiData = data?.kpi || {}
		// Compute aging_90+ from aging buckets (min_days >= 90)
		const agingBuckets = ag || []
		let aging90 = 0
		for (const b of agingBuckets) {
			if ((b.min_days || 0) >= 90) aging90 += b.count || 0
		}
		kpiData.aging_90 = aging90
		kpi.value = kpiData

		// Compute bar percentages from counts
		const maxCount = Math.max(1, ...agingBuckets.map((b) => b.count || 0))
		buckets.value = agingBuckets.map((b) => ({
			...b,
			pct: Math.min(100, ((b.count || 0) / maxCount) * 100),
		}))

		warehouses.value = wh || []
	} catch (e) {
		console.error('InventoryTab load:', e)
	} finally {
		loading.value = false
	}
}
onMounted(load)

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}
function bucketColor(bucket) {
	const b = String(bucket)
	if (b.includes('90') || b.includes('120') || b.includes('180')) return 'bg-red-500'
	if (b.includes('60') || b.includes('30')) return 'bg-amber-500'
	return 'bg-emerald-500'
}
</script>
