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
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-[#D4AF37]/10">
					<span class="material-symbols-outlined !text-xl text-[#D4AF37]">build</span>
				</div>
				<div class="flex-1 min-w-0">
					<h2 class="premium-title !text-xl">Repair Analytics</h2>
					<p class="text-[10px] text-gray-400">
						Volume, revenue, SLA, technician performance, AI insights
					</p>
				</div>
				<div class="flex items-center gap-2">
					<select
						v-model="period"
						@change="refresh"
						class="h-9 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs"
					>
						<option :value="7">7 Days</option>
						<option :value="30">30 Days</option>
						<option :value="90">90 Days</option>
					</select>
					<button
						@click="refresh"
						:disabled="loading"
						class="h-9 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs font-bold hover:border-[#D4AF37] disabled:opacity-50 flex items-center gap-1 transition"
					>
						<span
							class="material-symbols-outlined !text-base"
							:class="{ 'animate-spin': loading }"
							>refresh</span
						>
					</button>
				</div>
			</div>

			<!-- Loading -->
			<div v-if="loading && !data" class="flex-1 flex items-center justify-center">
				<div class="text-center">
					<div
						class="animate-spin rounded-full h-10 w-10 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
					></div>
					<p class="text-sm text-gray-400">Loading analytics...</p>
				</div>
			</div>

			<!-- Dashboard Content -->
			<div v-else class="flex-1 overflow-auto space-y-4 pr-1">
				<!-- KPI Row -->
				<div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
					<KPICard
						label="Total Repairs"
						:value="kpis.total_repairs"
						icon="build"
						color="blue"
					>
						<template #badge>
							<span
								:class="
									kpis.total_change_pct >= 0 ? 'text-green-500' : 'text-red-500'
								"
								class="text-[9px] font-bold"
							>
								{{ kpis.total_change_pct >= 0 ? '↑' : '↓'
								}}{{ Math.abs(kpis.total_change_pct) }}%
							</span>
						</template>
					</KPICard>
					<KPICard
						label="Revenue"
						:value="'$' + fmt(kpis.revenue)"
						icon="payments"
						color="emerald"
					>
						<template #badge>
							<span
								:class="
									kpis.revenue_change_pct >= 0
										? 'text-green-500'
										: 'text-red-500'
								"
								class="text-[9px] font-bold"
							>
								{{ kpis.revenue_change_pct >= 0 ? '↑' : '↓'
								}}{{ Math.abs(kpis.revenue_change_pct) }}%
							</span>
						</template>
					</KPICard>
					<KPICard
						label="Avg Turnaround"
						:value="kpis.avg_turnaround_days + 'd'"
						icon="schedule"
						color="purple"
					/>
					<KPICard
						label="Active Now"
						:value="kpis.active_repairs"
						icon="pending"
						color="amber"
					/>
					<KPICard
						label="On-Time SLA"
						:value="sla.on_time_pct + '%'"
						icon="verified"
						:color="
							sla.on_time_pct >= 90
								? 'emerald'
								: sla.on_time_pct >= 75
								? 'amber'
								: 'red'
						"
					/>
				</div>

				<!-- AI Insights Banner -->
				<div
					v-if="aiInsights.length"
					class="premium-card !p-4 !border-[#D4AF37]/20 bg-gradient-to-r from-[#D4AF37]/5 to-transparent"
				>
					<div class="flex items-center gap-2 mb-3">
						<span class="material-symbols-outlined !text-lg text-[#D4AF37]"
							>psychology</span
						>
						<h3 class="text-sm font-bold text-gray-900 dark:text-white">
							AI Insights
						</h3>
						<span
							class="text-[9px] px-2 py-0.5 rounded-full bg-[#D4AF37]/10 text-[#D4AF37] font-bold uppercase"
						>
							{{ aiSource === 'qwen' ? 'Qwen 3.6' : 'Rule Engine' }}
						</span>
					</div>
					<div class="space-y-2">
						<div
							v-for="(insight, idx) in aiInsights"
							:key="idx"
							class="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300"
						>
							<span
								class="w-5 h-5 rounded-full bg-[#D4AF37]/10 text-[#D4AF37] flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5"
							>
								{{ idx + 1 }}
							</span>
							<p>{{ insight }}</p>
						</div>
					</div>
				</div>

				<!-- Charts Row -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<!-- Daily Volume Chart -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Daily Volume
						</h3>
						<div class="h-48 flex items-end gap-[2px]">
							<div
								v-for="(val, i) in dailyTrend.counts"
								:key="'vol-' + i"
								class="flex-1 flex flex-col items-center justify-end gap-0.5 group relative"
							>
								<div
									class="w-full rounded-t bg-blue-500/70 dark:bg-blue-400/50 transition-all min-h-[2px] hover:bg-blue-600"
									:style="{ height: barHeight(val, maxDailyCount) }"
								></div>
								<span
									v-if="i % 5 === 0"
									class="text-[7px] text-gray-400 truncate w-full text-center"
									>{{ dailyTrend.labels[i] }}</span
								>
								<!-- Tooltip -->
								<div
									class="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[9px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-10"
								>
									{{ dailyTrend.labels[i] }}: {{ val }} repairs
								</div>
							</div>
						</div>
					</div>

					<!-- Revenue Trend Chart -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Revenue Trend
						</h3>
						<div class="h-48 flex items-end gap-[2px]">
							<div
								v-for="(val, i) in dailyTrend.revenues"
								:key="'rev-' + i"
								class="flex-1 flex flex-col items-center justify-end gap-0.5 group relative"
							>
								<div
									class="w-full rounded-t bg-emerald-500/70 dark:bg-emerald-400/50 transition-all min-h-[2px] hover:bg-emerald-600"
									:style="{ height: barHeight(val, maxDailyRevenue) }"
								></div>
								<span
									v-if="i % 5 === 0"
									class="text-[7px] text-gray-400 truncate w-full text-center"
									>{{ dailyTrend.labels[i] }}</span
								>
								<div
									class="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[9px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-10"
								>
									{{ dailyTrend.labels[i] }}: ${{ fmt(val) }}
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Type Breakdown + SLA -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<!-- Repair Type Breakdown -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Repair Types
						</h3>
						<div class="space-y-2.5">
							<div v-for="t in typeBreakdown" :key="t.type" class="group">
								<div class="flex items-center justify-between mb-1">
									<span
										class="text-xs font-bold text-gray-700 dark:text-gray-300 truncate"
										>{{ t.type }}</span
									>
									<div class="flex items-center gap-3 shrink-0">
										<span class="text-[10px] text-gray-400"
											>{{ t.count }} · {{ t.avg_days }}d</span
										>
										<span
											class="text-xs font-black text-gray-900 dark:text-white"
											>${{ fmt(t.revenue) }}</span
										>
									</div>
								</div>
								<div
									class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2.5 overflow-hidden"
								>
									<div
										class="h-full rounded-full bg-[#D4AF37] transition-all duration-500"
										:style="{ width: t.pct + '%' }"
									></div>
								</div>
							</div>
							<p
								v-if="!typeBreakdown.length"
								class="text-xs text-gray-400 text-center py-3"
							>
								No data
							</p>
						</div>
					</div>

					<!-- SLA Compliance -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							SLA Compliance
						</h3>
						<!-- Gauge visualization -->
						<div class="flex items-center justify-center mb-4">
							<div class="relative w-40 h-20">
								<!-- Background arc -->
								<svg class="w-full h-full" viewBox="0 0 160 80">
									<path
										d="M10 75 A65 65 0 0 1 150 75"
										fill="none"
										stroke="currentColor"
										stroke-width="10"
										class="text-gray-200 dark:text-gray-700"
										stroke-linecap="round"
									/>
									<path
										d="M10 75 A65 65 0 0 1 150 75"
										fill="none"
										:stroke="slaColor"
										stroke-width="10"
										stroke-linecap="round"
										:stroke-dasharray="slaArc + ' 999'"
									/>
								</svg>
								<div class="absolute inset-0 flex items-end justify-center pb-1">
									<span
										class="text-2xl font-black"
										:class="
											sla.on_time_pct >= 90
												? 'text-green-600'
												: sla.on_time_pct >= 75
												? 'text-amber-500'
												: 'text-red-500'
										"
									>
										{{ sla.on_time_pct }}%
									</span>
								</div>
							</div>
						</div>
						<div class="grid grid-cols-3 gap-3 text-center">
							<div>
								<p class="text-lg font-black text-gray-900 dark:text-white">
									{{ sla.total_delivered }}
								</p>
								<p class="text-[9px] text-gray-400 uppercase">Delivered</p>
							</div>
							<div>
								<p class="text-lg font-black text-green-600">{{ sla.on_time }}</p>
								<p class="text-[9px] text-gray-400 uppercase">On Time</p>
							</div>
							<div>
								<p
									class="text-lg font-black"
									:class="sla.overdue_now > 0 ? 'text-red-500' : 'text-gray-400'"
								>
									{{ sla.overdue_now }}
								</p>
								<p class="text-[9px] text-gray-400 uppercase">Overdue</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Technician Leaderboard + Monthly Revenue -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<!-- Technician Leaderboard -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Technician Leaderboard
						</h3>
						<div class="space-y-2">
							<div
								v-for="(tech, i) in techLeaderboard"
								:key="tech.user"
								class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-warm-dark-900 transition"
							>
								<span
									class="text-[10px] font-black w-5 text-center"
									:class="i < 3 ? 'text-[#D4AF37]' : 'text-gray-400'"
								>
									{{ i < 3 ? ['🥇', '🥈', '🥉'][i] : i + 1 }}
								</span>
								<div
									class="w-7 h-7 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#B8962A] flex items-center justify-center text-[10px] font-bold text-white shrink-0"
								>
									{{
										tech.name
											.split(' ')
											.map((w) => w[0])
											.join('')
											.slice(0, 2)
									}}
								</div>
								<div class="flex-1 min-w-0">
									<p
										class="text-xs font-bold text-gray-900 dark:text-white truncate"
									>
										{{ tech.name }}
									</p>
									<p class="text-[9px] text-gray-400">
										{{ tech.completed }}/{{ tech.total }} ·
										{{ tech.avg_days }}d avg
									</p>
								</div>
								<div class="text-right shrink-0">
									<p class="text-xs font-black text-emerald-600">
										${{ fmt(tech.revenue) }}
									</p>
									<p class="text-[9px] text-gray-400">
										{{ tech.completion_rate }}% rate
									</p>
								</div>
							</div>
							<p
								v-if="!techLeaderboard.length"
								class="text-xs text-gray-400 text-center py-3"
							>
								No data
							</p>
						</div>
					</div>

					<!-- Monthly Revenue -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Monthly Revenue (6mo)
						</h3>
						<div class="h-48 flex items-end gap-2">
							<div
								v-for="(val, i) in monthlyRevenue.revenues"
								:key="'mo-' + i"
								class="flex-1 flex flex-col items-center justify-end gap-1 group relative"
							>
								<div
									class="w-full rounded-t bg-gradient-to-t from-[#D4AF37] to-[#D4AF37]/60 transition-all min-h-[4px]"
									:style="{ height: barHeight(val, maxMonthlyRevenue) }"
								></div>
								<span class="text-[8px] text-gray-400">{{
									monthlyRevenue.labels[i]?.slice(5) || ''
								}}</span>
								<div
									class="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[9px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition pointer-events-none whitespace-nowrap z-10"
								>
									{{ monthlyRevenue.labels[i] }}: ${{ fmt(val) }}
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Customer Insights -->
				<div class="premium-card !p-5">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
						Customer Insights
					</h3>
					<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
						<div class="text-center">
							<p class="text-2xl font-black text-gray-900 dark:text-white">
								{{ customerInsights.total_customers }}
							</p>
							<p class="text-[10px] text-gray-400 uppercase">Unique Customers</p>
						</div>
						<div class="text-center">
							<p class="text-2xl font-black text-purple-600">
								{{ customerInsights.repeat_customers }}
							</p>
							<p class="text-[10px] text-gray-400 uppercase">Repeat Customers</p>
						</div>
						<div class="text-center">
							<p class="text-2xl font-black text-[#D4AF37]">
								{{ customerInsights.repeat_pct }}%
							</p>
							<p class="text-[10px] text-gray-400 uppercase">Repeat Rate</p>
						</div>
						<div>
							<p class="text-[10px] text-gray-400 uppercase mb-1">Top Repeat</p>
							<div
								v-for="c in customerInsights.top_repeat?.slice(0, 3)"
								:key="c.customer"
								class="flex items-center justify-between text-xs py-0.5"
							>
								<span class="truncate text-gray-700 dark:text-gray-300">{{
									c.name
								}}</span>
								<span class="font-bold text-gray-900 dark:text-white shrink-0 ml-2"
									>{{ c.count }}×</span
								>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { fmt } from '@/utils/format'
import KPICard from '@/components/reports/KPICard.vue'
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'

const period = ref(30)
const loading = ref(false)
const data = ref(null)
const aiInsights = ref([])
const aiSource = ref('rules')

const kpis = computed(() => data.value?.kpis || {})
const sla = computed(() => data.value?.sla || {})
const dailyTrend = computed(
	() => data.value?.daily_trend || { labels: [], counts: [], revenues: [] }
)
const typeBreakdown = computed(() => data.value?.type_breakdown || [])
const techLeaderboard = computed(() => data.value?.tech_leaderboard || [])
const monthlyRevenue = computed(() => data.value?.monthly_revenue || { labels: [], revenues: [] })
const customerInsights = computed(() => data.value?.customer_insights || {})

const maxDailyCount = computed(() => Math.max(1, ...dailyTrend.value.counts))
const maxDailyRevenue = computed(() => Math.max(1, ...dailyTrend.value.revenues))
const maxMonthlyRevenue = computed(() => Math.max(1, ...(monthlyRevenue.value.revenues || [1])))

const slaColor = computed(() => {
	const pct = sla.value.on_time_pct || 0
	if (pct >= 90) return '#22c55e'
	if (pct >= 75) return '#f59e0b'
	return '#ef4444'
})
const slaArc = computed(() => {
	const pct = Math.min(100, sla.value.on_time_pct || 0)
	return Math.round((pct / 100) * 204)
})

function barHeight(val, max) {
	if (!max || !val) return '2px'
	return Math.max(2, (val / max) * 100) + '%'
}

async function refresh() {
	loading.value = true
	try {
		const [analytics, ai] = await Promise.all([
			call('zevar_core.api.repair_analytics.get_repair_analytics', { period: period.value }),
			call('zevar_core.api.repair_analytics.get_ai_insights').catch(() => null),
		])
		data.value = analytics
		if (ai) {
			aiInsights.value = ai.insights || []
			aiSource.value = ai.source || 'rules'
		}
	} catch (e) {
		console.error('Failed to load repair analytics:', e)
	} finally {
		loading.value = false
	}
}

onMounted(refresh)
</script>
