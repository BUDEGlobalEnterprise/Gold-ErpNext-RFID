<template>
	<div class="tab-content">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
			<KPICard
				label="Open"
				:value="kpi.open || 0"
				icon="build"
				color="blue"
				:loading="loading"
			/>
			<KPICard
				label="Ready"
				:value="kpi.ready || 0"
				icon="check_circle"
				color="emerald"
				:loading="loading"
			/>
			<KPICard
				label="Overdue"
				:value="kpi.overdue || 0"
				icon="error"
				color="red"
				:loading="loading"
			/>
			<KPICard
				label="Avg Turnaround"
				:value="`${kpi.avg_turnaround || 0}d`"
				icon="schedule"
				color="amber"
				:loading="loading"
			/>
		</div>

		<div class="premium-card mt-4">
			<div class="flex items-center justify-between mb-3">
				<h3 class="text-sm font-bold text-gray-900 dark:text-white">Overdue Repairs</h3>
				<button class="text-[10px] font-bold text-[#D4AF37] hover:underline">
					View all
				</button>
			</div>
			<div v-if="loading" class="space-y-2">
				<div
					v-for="n in 4"
					:key="n"
					class="h-10 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
				/>
			</div>
			<div v-else-if="!rows.length" class="text-xs text-gray-400 text-center py-6">
				No overdue repairs
			</div>
			<div v-else class="overflow-x-auto">
				<!-- Desktop table -->
				<table class="w-full text-xs hidden sm:table">
					<thead>
						<tr
							class="text-left text-[10px] uppercase tracking-wider text-gray-500 border-b border-gray-200 dark:border-warm-border"
						>
							<th class="py-2">Repair</th>
							<th class="py-2">Customer</th>
							<th class="py-2">State</th>
							<th class="py-2 text-right">Overdue</th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="r in rows"
							:key="r.name"
							class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50 dark:hover:bg-[#1C1F26]"
						>
							<td class="py-2 font-mono">{{ r.name }}</td>
							<td class="py-2">{{ r.customer }}</td>
							<td class="py-2">
								<span
									class="px-1.5 py-0.5 rounded text-[10px] font-bold"
									:class="stateClass(r.status)"
									>{{ r.status }}</span
								>
							</td>
							<td class="py-2 text-right font-mono">
								{{ r.days_overdue || 0 }}d overdue
							</td>
						</tr>
					</tbody>
				</table>
				<!-- Mobile vertical cards -->
				<div class="sm:hidden space-y-2">
					<div
						v-for="r in rows"
						:key="'m-' + r.name"
						class="p-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26]"
					>
						<div class="flex items-center justify-between mb-1">
							<span class="font-mono text-xs font-bold">{{ r.name }}</span>
							<span
								class="px-1.5 py-0.5 rounded text-[10px] font-bold"
								:class="stateClass(r.status)"
								>{{ r.status }}</span
							>
						</div>
						<div class="text-[10px] text-gray-500">{{ r.customer }}</div>
						<div class="text-xs font-bold text-red-500 mt-1">
							{{ r.days_overdue || 0 }} days overdue
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
/**
 * RepairsTab — Plan §7.1, 180 LOC budget.
 * Reuses repair_dashboard + repair_analytics.
 */
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import KPICard from '@/components/reports/KPICard.vue'

const kpi = ref({})
const rows = ref([])
const loading = ref(true)

async function load() {
	loading.value = true
	try {
		const data = await call('zevar_core.api.repair_dashboard.get_repair_dashboard_stats', {})
		const breakdown = data?.status_breakdown || {}
		kpi.value = {
			open: breakdown['In Progress'] || breakdown['Received'] || 0,
			ready: breakdown['Ready for Pickup'] || data?.ready_pickup_count || 0,
			overdue: data?.overdue_count || 0,
			avg_turnaround: data?.avg_turnaround_days || 0,
		}
		rows.value = data?.recent_overdue || []
	} catch (e) {
		console.error('RepairsTab load:', e)
	} finally {
		loading.value = false
	}
}
onMounted(load)

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}
function stateClass(s) {
	const map = {
		'In Progress': 'bg-blue-500/15 text-blue-600 dark:text-blue-400',
		'Ready for Pickup': 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
		Delivered: 'bg-gray-500/15 text-gray-600 dark:text-gray-400',
		'On Hold': 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
	}
	return map[s] || 'bg-gray-500/15 text-gray-600'
}
</script>
