<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0 flex-wrap">
				<div
					class="w-10 h-10 rounded-xl flex items-center justify-center bg-blue-500/10"
				>
					<span class="material-symbols-outlined !text-xl text-blue-500"
						>person_pin</span
					>
				</div>
				<div>
					<h2 class="premium-title !text-xl">My Dashboard</h2>
					<p class="text-[10px] text-gray-400">
						{{ perf.employee_name }} &middot; {{ timeNow }}
					</p>
				</div>
				<button
					@click="refresh"
					class="ml-auto w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-blue-500 transition-colors"
					:class="{ 'animate-spin': loading }"
				>
					<span class="material-symbols-outlined !text-base">refresh</span>
				</button>
			</div>

			<div class="flex-1 overflow-auto space-y-4 pr-1">
				<!-- My Performance -->
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
					<KPICard
						label="My Sales Today"
						:value="'$' + fmt(perf.today_revenue)"
						icon="payments"
						color="emerald"
						:loading="loading"
					/>
					<KPICard
						label="Transactions"
						:value="perf.txn_count"
						icon="receipt"
						color="blue"
						:loading="loading"
					/>
					<KPICard
						label="Items Sold"
						:value="perf.items_sold"
						icon="shopping_bag"
						color="purple"
						:loading="loading"
					/>
					<KPICard
						label="vs Yesterday"
						:value="(perf.change_pct >= 0 ? '+' : '') + perf.change_pct + '%'"
						icon="trending_up"
						:color="perf.change_pct >= 0 ? 'emerald' : 'red'"
						:loading="loading"
					/>
				</div>

				<!-- POS Session Status -->
				<div v-if="!loading" class="premium-card !p-3 flex items-center gap-3">
					<span
						class="material-symbols-outlined !text-lg"
						:class="perf.has_active_session ? 'text-emerald-500' : 'text-gray-400'"
					>
						{{ perf.has_active_session ? 'point_of_sale' : 'point_of_sale' }}
					</span>
					<span class="text-xs font-bold" :class="perf.has_active_session ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-500'">
						{{ perf.has_active_session ? 'Register Open' : 'No Active Register' }}
					</span>
					<span v-if="!perf.has_active_session" class="text-[10px] text-gray-400 ml-auto">
						Open a register to start selling
					</span>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<!-- My Tasks -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
							<span class="material-symbols-outlined !text-base text-amber-500">task_alt</span>
							My Tasks
							<span v-if="tasks.pending_count" class="ml-auto text-[10px] font-bold bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 px-2 py-0.5 rounded-full">
								{{ tasks.pending_count }}
							</span>
						</h3>
						<div v-if="loading" class="space-y-2">
							<div v-for="n in 3" :key="n" class="h-8 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
						</div>
						<template v-else>
							<!-- Repairs -->
							<div v-if="tasks.repairs?.length" class="space-y-2 mb-3">
								<p class="text-[10px] font-bold text-gray-400 uppercase">Repairs</p>
								<div
									v-for="r in tasks.repairs.slice(0, 5)"
									:key="r.name"
									class="flex items-center gap-2 py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0"
								>
									<span
										class="w-2 h-2 rounded-full shrink-0"
										:class="r.days_overdue > 0 ? 'bg-red-500' : 'bg-amber-400'"
									></span>
									<span class="text-xs text-gray-900 dark:text-white flex-1 truncate">{{ r.customer_name }}</span>
									<span class="text-[10px] text-gray-400 shrink-0">{{ r.repair_type_name }}</span>
									<span v-if="r.days_overdue > 0" class="text-[10px] font-bold text-red-500 shrink-0">
										{{ r.days_overdue }}d overdue
									</span>
								</div>
							</div>
							<!-- Layaways -->
							<div v-if="tasks.layaways?.length" class="space-y-2 mb-3">
								<p class="text-[10px] font-bold text-gray-400 uppercase">Layaway Follow-ups</p>
								<div
									v-for="l in tasks.layaways.slice(0, 3)"
									:key="l.name"
									class="flex items-center gap-2 py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0"
								>
									<span class="w-2 h-2 rounded-full bg-purple-400 shrink-0"></span>
									<span class="text-xs text-gray-900 dark:text-white flex-1 truncate">{{ l.customer_name }}</span>
									<span class="text-[10px] text-gray-400 shrink-0">${{ fmt(l.outstanding_amount) }}</span>
								</div>
							</div>
							<!-- Todos -->
							<div v-if="tasks.todos?.length" class="space-y-2">
								<p class="text-[10px] font-bold text-gray-400 uppercase">To-Do</p>
								<div
									v-for="todo in tasks.todos.slice(0, 5)"
									:key="todo.name"
									class="flex items-center gap-2 py-1"
								>
									<span class="material-symbols-outlined !text-sm text-gray-300">check_box_outline_blank</span>
									<span class="text-xs text-gray-700 dark:text-gray-300 flex-1 truncate">{{ todo.description }}</span>
								</div>
							</div>
							<p
								v-if="!tasks.repairs?.length && !tasks.layaways?.length && !tasks.todos?.length"
								class="text-xs text-gray-400 text-center py-4"
							>
								All caught up!
							</p>
						</template>
					</div>

					<!-- Store Activity -->
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
							<span class="material-symbols-outlined !text-base text-blue-500">store</span>
							Store Activity
							<span class="ml-auto text-[10px] text-gray-400">
								{{ store.store_txn_count_today || 0 }} transactions today
							</span>
						</h3>
						<div v-if="loading" class="h-40 flex items-center justify-center">
							<span class="material-symbols-outlined animate-spin text-gray-300">progress_activity</span>
						</div>
						<div v-else-if="store.hourly?.length" class="h-40 flex items-end gap-1">
							<div
								v-for="(bar, i) in store.hourly"
								:key="i"
								class="flex-1 flex flex-col items-center gap-1 group cursor-default"
							>
								<span class="text-[8px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
									{{ bar.txn_count }}
								</span>
								<div
									class="w-full rounded-t bg-blue-500/60 dark:bg-blue-400/40 min-h-[2px] hover:bg-blue-500 transition-colors"
									:style="{ height: barHeight(bar.txn_count) + '%' }"
								></div>
								<span class="text-[8px] text-gray-400">{{ bar.label }}</span>
							</div>
						</div>
						<!-- Recent feed -->
						<div v-if="store.recent_feed?.length && !loading" class="mt-3 space-y-1 max-h-24 overflow-auto">
							<div
								v-for="(ev, i) in store.recent_feed.slice(0, 8)"
								:key="i"
								class="flex items-center gap-2"
							>
								<span class="text-[10px] text-gray-400 shrink-0 w-12">{{ ev.time }}</span>
								<span class="text-[10px] text-gray-600 dark:text-gray-400">{{ ev.item_count }} item{{ ev.item_count !== 1 ? 's' : '' }}</span>
								<span v-if="ev.stream !== 'Sale'" class="text-[9px] bg-gray-100 dark:bg-gray-800 text-gray-500 px-1.5 py-0.5 rounded">{{ ev.stream }}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Repair Queue Summary -->
				<div v-if="tasks.queue_summary?.length && !loading" class="premium-card !p-5">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
						<span class="material-symbols-outlined !text-base text-slate-500">format_list_numbered</span>
						My Repair Queue
					</h3>
					<div class="flex gap-2 flex-wrap">
						<div
							v-for="qs in tasks.queue_summary"
							:key="qs.status"
							class="flex-1 min-w-[80px] bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 text-center"
						>
							<p class="text-lg font-black text-gray-900 dark:text-white">{{ qs.cnt }}</p>
							<p class="text-[10px] font-bold text-gray-500 uppercase">{{ qs.status }}</p>
							<p v-if="qs.avg_age_days > 0" class="text-[9px] text-gray-400 mt-0.5">
								avg {{ Math.round(qs.avg_age_days) }}d old
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import KPICard from '@/components/reports/KPICard.vue'

const perf = ref({
	employee_name: '',
	today_revenue: 0,
	txn_count: 0,
	items_sold: 0,
	change_pct: 0,
	has_active_session: false,
})
const store = ref({ hourly: [], recent_feed: [], store_txn_count_today: 0 })
const tasks = ref({ repairs: [], layaways: [], todos: [], queue_summary: [], pending_count: 0 })
const loading = ref(true)
const timeNow = ref('')

function updateTime() {
	timeNow.value = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

async function refresh() {
	loading.value = true
	updateTime()
	try {
		const res = await fetch('/api/method/zevar_core.api.employee_live_monitor.get_employee_dashboard', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		if (!res.ok) throw new Error('Failed to load employee dashboard')
		const json = await res.json()
		const data = json.message || json
		if (data.performance) perf.value = data.performance
		if (data.store) store.value = data.store
		if (data.tasks) tasks.value = data.tasks
	} catch (e) {
		console.error('Employee monitor error:', e)
	} finally {
		loading.value = false
	}
}

function barHeight(count) {
	const maxVal = Math.max(...(store.value.hourly?.map(h => h.txn_count) || [1]), 1)
	return (count / maxVal) * 100
}

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}

// WebSocket subscription
function onEmployeeEvent(data) {
	if (data.event_type === 'sale_completed' || data.event_type === 'repair_updated') {
		refresh()
	}
}

onMounted(() => {
	refresh()
	if (window.frappe?.realtime) {
		window.frappe.realtime.on('employee_event', onEmployeeEvent)
	}
})

onUnmounted(() => {
	if (window.frappe?.realtime) {
		window.frappe.realtime.off('employee_event', onEmployeeEvent)
	}
})
</script>
