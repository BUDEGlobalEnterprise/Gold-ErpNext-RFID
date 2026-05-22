<template>
	<div class="technician-workload-panel bg-white dark:bg-warm-dark-800 rounded-xl border border-gray-100 dark:border-warm-border p-4">
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
				<svg class="w-4 h-4 text-[#D4AF37]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
						d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
				</svg>
				Technician Workload
			</h3>
			<button
				@click="refresh"
				:disabled="loading"
				class="text-[10px] px-2 py-1 bg-gray-100 dark:bg-warm-dark-900 rounded-full hover:bg-gray-200 transition disabled:opacity-50"
			>
				{{ loading ? '...' : '↻ Refresh' }}
			</button>
		</div>

		<!-- Loading -->
		<div v-if="loading && !technicians.length" class="text-center py-6">
			<div class="animate-spin w-6 h-6 border-2 border-[#D4AF37] border-t-transparent rounded-full mx-auto"></div>
			<p class="text-xs text-gray-400 mt-2">Loading workload data...</p>
		</div>

		<!-- Empty -->
		<div v-else-if="!technicians.length" class="text-center py-6 text-gray-400">
			<p class="text-sm">No active technicians found</p>
			<p class="text-xs mt-1">Assign repairs to see workload data</p>
		</div>

		<!-- Technician Cards -->
		<div v-else class="space-y-3">
			<div
				v-for="tech in technicians"
				:key="tech.user"
				class="group border border-gray-100 dark:border-warm-border/50 rounded-lg p-3 hover:border-[#D4AF37]/30 transition-colors"
			>
				<!-- Tech Header -->
				<div class="flex items-center justify-between mb-2">
					<div class="flex items-center gap-2">
						<div class="w-7 h-7 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#B8962A] flex items-center justify-center text-[10px] font-bold text-white">
							{{ getInitials(tech.user_name) }}
						</div>
						<div>
							<p class="text-xs font-bold text-gray-900 dark:text-white leading-tight">{{ tech.user_name }}</p>
							<p class="text-[9px] text-gray-400">{{ tech.avg_turnaround_days }}d avg turnaround</p>
						</div>
					</div>
					<div class="text-right">
						<p class="text-sm font-bold text-gray-900 dark:text-white">{{ tech.active_jobs }}</p>
						<p class="text-[9px] text-gray-400">active</p>
					</div>
				</div>

				<!-- Workload Bar -->
				<div class="relative h-3 bg-gray-100 dark:bg-warm-dark-900 rounded-full overflow-hidden mb-2">
					<div
						class="h-full rounded-full transition-all duration-500"
						:class="getWorkloadBarClass(tech.active_jobs)"
						:style="{ width: getWorkloadPercent(tech.active_jobs) + '%' }"
					></div>
				</div>

				<!-- Status Breakdown Pills -->
				<div class="flex flex-wrap gap-1 mb-2">
					<span
						v-for="(count, status) in tech.status_breakdown"
						:key="status"
						v-show="count > 0"
						class="px-1.5 py-0.5 text-[8px] font-bold rounded-full"
						:class="getStatusPillClass(status)"
					>
						{{ getStatusShortLabel(status) }}: {{ count }}
					</span>
				</div>

				<!-- Stats Row -->
				<div class="flex items-center justify-between text-[9px] text-gray-400 pt-1 border-t border-gray-50 dark:border-warm-border/20">
					<span>{{ tech.completed_this_month }} completed this month</span>
					<span class="font-bold text-green-600">${{ formatNum(tech.revenue_this_month) }}</span>
				</div>
			</div>
		</div>

		<!-- AI Suggestion -->
		<div v-if="suggestion" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-100 dark:border-blue-800/30">
			<p class="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase mb-1">
				🤖 AI Recommendation
			</p>
			<p class="text-xs text-blue-700 dark:text-blue-300">
				Best match for new repairs: <strong>{{ suggestion.user_name }}</strong>
				<span class="text-[9px] opacity-70">
					({{ suggestion.active_jobs }} active, {{ suggestion.avg_days }}d avg, {{ suggestion.type_experience }} similar completed)
				</span>
			</p>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'

const props = defineProps({
	/** Repair type to suggest technician for */
	repairType: { type: String, default: '' },
})

const technicians = ref([])
const suggestion = ref(null)
const loading = ref(false)

const MAX_WORKLOAD = 10 // 10 active jobs = 100% bar

async function refresh() {
	loading.value = true
	try {
		const data = await call('zevar_core.api.repair_timeline.get_technician_workload')
		technicians.value = data || []

		// Also get suggestion if repair type provided
		if (props.repairType) {
			const sugData = await call('zevar_core.api.repair_timeline.suggest_technician', {
				repair_type: props.repairType,
			})
			suggestion.value = sugData?.suggestion || null
		}
	} catch (e) {
		console.error('Failed to load workload:', e)
	} finally {
		loading.value = false
	}
}

function getInitials(name) {
	if (!name) return '?'
	return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

function getWorkloadPercent(jobs) {
	return Math.min(100, (jobs / MAX_WORKLOAD) * 100)
}

function getWorkloadBarClass(jobs) {
	if (jobs >= 8) return 'bg-red-500'
	if (jobs >= 5) return 'bg-yellow-500'
	return 'bg-green-500'
}

function getStatusPillClass(status) {
	const classes = {
		'Received': 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
		'Estimated': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
		'Approved': 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
		'In Progress': 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
		'Waiting for Parts': 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
		'Quality Check': 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300',
	}
	return classes[status] || 'bg-gray-100 text-gray-600'
}

function getStatusShortLabel(status) {
	const labels = {
		'Received': 'RCV',
		'Estimated': 'EST',
		'Approved': 'APR',
		'In Progress': 'WIP',
		'Waiting for Parts': 'PRT',
		'Quality Check': 'QC',
	}
	return labels[status] || status.slice(0, 3).toUpperCase()
}

function formatNum(n) {
	if (!n) return '0'
	return Number(n).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

onMounted(refresh)
</script>
