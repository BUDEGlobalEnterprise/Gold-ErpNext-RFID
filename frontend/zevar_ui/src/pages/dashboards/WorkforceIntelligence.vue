<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<!-- Header -->
			<div class="flex items-center gap-3 mb-4 flex-shrink-0 flex-wrap">
				<button
					@click="$router.push('/reports')"
					class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors"
				>
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-rose-500/10">
					<span class="material-symbols-outlined !text-xl text-rose-500">groups</span>
				</div>
				<div class="flex-1 min-w-0">
					<h2 class="premium-title !text-xl">Workforce Intelligence</h2>
					<p class="text-[10px] text-gray-400">Team scoreboard, quota pace, payout projection</p>
				</div>
				<button
					@click="refresh"
					:disabled="loading"
					class="ml-auto w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-rose-500 transition-colors"
					:class="{ 'animate-spin': loading }"
				>
					<span class="material-symbols-outlined !text-base">refresh</span>
				</button>
			</div>

			<!-- Tabs -->
			<div class="border-b border-gray-200 dark:border-gray-700 mb-4 flex-shrink-0">
				<nav class="flex space-x-4 overflow-x-auto -mb-px">
					<button
						v-for="tab in tabs"
						:key="tab.key"
						@click="activeTab = tab.key"
						:class="[
							activeTab === tab.key
								? 'border-rose-500 text-rose-600 dark:text-rose-400'
								: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300',
							'whitespace-nowrap py-2.5 px-1 border-b-2 font-medium text-xs transition-colors',
						]"
					>
						{{ tab.label }}
					</button>
				</nav>
			</div>

			<div class="flex-1 overflow-auto space-y-4 pr-1">
				<!-- Scoreboard Tab -->
				<template v-if="activeTab === 'scoreboard'">
					<!-- KPI strip -->
					<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
						<KPICard label="Associates" :value="rows.length" icon="groups" color="rose" :loading="loading" />
						<KPICard
							label="Team Revenue"
							:value="'$' + fmt(teamRevenue)"
							icon="payments"
							color="emerald"
							:loading="loading"
						/>
						<KPICard
							label="Team UPT"
							:value="teamUpt.toFixed(2)"
							icon="sell"
							color="blue"
							:loading="loading"
						/>
						<KPICard
							label="Commission"
							:value="'$' + fmt(teamCommission)"
							icon="savings"
							color="amber"
							:loading="loading"
						/>
					</div>

					<!-- Team scoreboard -->
					<div class="premium-card !p-3 sm:!p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Team Scoreboard</h3>
						<div v-if="loading" class="space-y-2">
							<div v-for="n in 3" :key="n" class="h-10 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
						</div>
						<table v-else-if="rows.length" class="w-full text-xs">
							<thead>
								<tr class="text-left text-gray-400 border-b border-gray-100 dark:border-gray-800">
									<th class="py-2 font-bold">#</th>
									<th class="py-2 font-bold">Associate</th>
									<th class="py-2 font-bold text-right">Revenue</th>
									<th class="py-2 font-bold text-right">Txn</th>
									<th class="py-2 font-bold text-right">UPT</th>
									<th class="py-2 font-bold text-right">Commission</th>
									<th class="py-2 font-bold text-right">Pace</th>
								</tr>
							</thead>
							<tbody>
								<tr
									v-for="(r, i) in rows"
									:key="r.employee"
									class="border-b border-gray-50 dark:border-gray-800/50"
								>
									<td class="py-2 text-gray-400 font-bold">{{ i + 1 }}</td>
									<td class="py-2 font-bold text-gray-900 dark:text-white truncate max-w-[160px]">
										{{ r.employee_name || r.employee }}
									</td>
									<td class="py-2 text-right font-bold text-emerald-600 dark:text-emerald-400">
										${{ fmt(r.revenue) }}
									</td>
									<td class="py-2 text-right text-gray-600 dark:text-gray-300">{{ r.txn_count }}</td>
									<td class="py-2 text-right text-gray-600 dark:text-gray-300">{{ r.upt }}</td>
									<td class="py-2 text-right text-gray-900 dark:text-white">${{ fmt(r.commission) }}</td>
									<td class="py-2 text-right">
										<div class="inline-block w-20 bg-gray-100 dark:bg-gray-800 rounded-full h-1.5 overflow-hidden align-middle">
											<div
												class="h-full bg-rose-500"
												:style="{ width: Math.min(r.pace_pct || 0, 100) + '%' }"
											></div>
										</div>
										<span class="ml-1 text-[10px] text-gray-400">{{ Math.round(r.pace_pct || 0) }}%</span>
									</td>
								</tr>
							</tbody>
						</table>
						<p v-else class="text-xs text-gray-400 text-center py-8">
							No salesperson data yet.
						</p>
					</div>
				</template>

				<!-- Efficiency Tab -->
				<template v-if="activeTab === 'efficiency'">
					<EfficiencyMetrics :data="efficiencyData" :loading="loadingEfficiency" />
				</template>

				<!-- Heatmap Tab -->
				<template v-if="activeTab === 'heatmap'">
					<StaffHeatmap :data="heatmapData" :loading="loadingHeatmap" />
				</template>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import KPICard from '@/components/reports/KPICard.vue'
import EfficiencyMetrics from '@/components/workforce/EfficiencyMetrics.vue'
import StaffHeatmap from '@/components/workforce/StaffHeatmap.vue'
import { fmt } from '@/utils/format'
import { ref, computed, onMounted, watch } from 'vue'
import { call } from 'frappe-ui'

const loading = ref(false)
const rows = ref([])
const activeTab = ref('scoreboard')
const efficiencyData = ref([])
const heatmapData = ref([])
const loadingEfficiency = ref(false)
const loadingHeatmap = ref(false)

const tabs = [
	{ key: 'scoreboard', label: 'Scoreboard' },
	{ key: 'efficiency', label: 'Efficiency' },
	{ key: 'heatmap', label: 'Heatmap' },
]

const teamRevenue = computed(() => rows.value.reduce((s, r) => s + (r.revenue || 0), 0))
const teamCommission = computed(() => rows.value.reduce((s, r) => s + (r.commission || 0), 0))
const teamUpt = computed(() => {
	const t = rows.value.reduce((s, r) => s + (r.txn_count || 0), 0)
	const u = rows.value.reduce((s, r) => s + (r.units || 0), 0)
	return t ? u / t : 0
})

async function loadScoreboard() {
	loading.value = true
	try {
		const leaderboard = (await call('zevar_core.api.sales_monitor.get_leaderboard')) || []
		const enriched = await Promise.all(
			(leaderboard || []).map(async (r) => {
				let pace = 0
				try {
					const qp = await call('zevar_core.api.workforce.get_quota_progress', { employee: r.employee })
					pace = qp?.attainment_pct || 0
				} catch {
					pace = 0
				}
				return { ...r, pace_pct: pace }
			})
		)
		rows.value = enriched
	} catch (e) {
		console.error('Workforce load failed:', e)
	} finally {
		loading.value = false
	}
}

async function loadEfficiency() {
	loadingEfficiency.value = true
	try {
		efficiencyData.value = (await call('zevar_core.api.workforce.get_employee_efficiency')) || []
	} catch (e) {
		console.error('Efficiency load failed:', e)
	} finally {
		loadingEfficiency.value = false
	}
}

async function loadHeatmap() {
	loadingHeatmap.value = true
	try {
		heatmapData.value = (await call('zevar_core.api.workforce.get_staffing_heatmap')) || []
	} catch (e) {
		console.error('Heatmap load failed:', e)
	} finally {
		loadingHeatmap.value = false
	}
}

async function refresh() {
	await loadScoreboard()
	if (activeTab.value === 'efficiency') await loadEfficiency()
	if (activeTab.value === 'heatmap') await loadHeatmap()
}

watch(activeTab, (tab) => {
	if (tab === 'efficiency' && !efficiencyData.value.length) loadEfficiency()
	if (tab === 'heatmap' && !heatmapData.value.length) loadHeatmap()
})

onMounted(refresh)
</script>
