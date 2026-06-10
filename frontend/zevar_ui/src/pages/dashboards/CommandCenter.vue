<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<!-- Header -->
			<div class="flex items-center justify-between mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<button
						@click="$router.push('/reports')"
						class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 hover:text-[#D4AF37] transition"
					>
						<span class="material-symbols-outlined !text-lg">arrow_back</span>
					</button>
					<div
						class="w-10 h-10 rounded-xl flex items-center justify-center bg-blue-500/10"
					>
						<span class="material-symbols-outlined !text-xl text-blue-500"
							>cell_tower</span
						>
					</div>
					<div>
						<h2 class="premium-title !text-xl">Command Center</h2>
						<p class="text-[10px] text-gray-400">
							Multi-store repair operations · Real-time
						</p>
					</div>
					<span
						class="flex items-center gap-1 text-xs"
						:class="isConnected ? 'text-green-500' : 'text-red-500'"
					>
						<span
							class="w-2 h-2 rounded-full animate-pulse"
							:class="isConnected ? 'bg-green-500' : 'bg-red-500'"
						></span>
						{{ isConnected ? 'Live' : 'Connecting...' }}
					</span>
				</div>
				<div class="flex items-center gap-2">
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

			<div v-if="loading && !data" class="flex-1 flex items-center justify-center">
				<div class="text-center">
					<div
						class="animate-spin rounded-full h-10 w-10 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
					></div>
					<p class="text-sm text-gray-400">Loading command center...</p>
				</div>
			</div>

			<div v-else class="flex-1 overflow-auto space-y-4 pr-1">
				<!-- System-Wide KPIs -->
				<div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
					<div
						class="p-3 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
					>
						<p class="text-[9px] text-gray-400 uppercase mb-1">Active Repairs</p>
						<p class="text-xl font-black text-gray-900 dark:text-white">
							{{ sys.total_active }}
						</p>
					</div>
					<div
						class="p-3 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
					>
						<p class="text-[9px] text-gray-400 uppercase mb-1">Overdue</p>
						<p
							class="text-xl font-black"
							:class="sys.total_overdue > 0 ? 'text-red-500' : 'text-green-500'"
						>
							{{ sys.total_overdue }}
						</p>
					</div>
					<div
						class="p-3 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
					>
						<p class="text-[9px] text-gray-400 uppercase mb-1">Completed Today</p>
						<p class="text-xl font-black text-green-600">{{ sys.completed_today }}</p>
					</div>
					<div
						class="p-3 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
					>
						<p class="text-[9px] text-gray-400 uppercase mb-1">Received Today</p>
						<p class="text-xl font-black text-blue-600">{{ sys.received_today }}</p>
					</div>
					<div
						class="p-3 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
					>
						<p class="text-[9px] text-gray-400 uppercase mb-1">Revenue Today</p>
						<p class="text-xl font-black text-emerald-600">
							${{ fmt(sys.revenue_today) }}
						</p>
					</div>
				</div>

				<!-- Alerts Banner -->
				<div v-if="alerts.length" class="space-y-2">
					<div
						v-for="(alert, i) in alerts.slice(0, 5)"
						:key="i"
						class="flex items-center gap-3 px-4 py-2.5 rounded-lg border text-sm"
						:class="alertClass(alert.severity)"
					>
						<span class="text-base">{{ alertIcon(alert.severity) }}</span>
						<div class="flex-1 min-w-0">
							<span class="font-bold">{{ alert.title }}</span>
							<span class="text-xs opacity-75 ml-2">{{ alert.message }}</span>
						</div>
						<button
							v-if="alert.repair"
							@click="openRepair(alert.repair)"
							class="text-[10px] font-bold underline shrink-0"
						>
							View
						</button>
					</div>
				</div>

				<!-- Store Cards Grid -->
				<div>
					<h3
						class="text-sm font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2"
					>
						<span class="material-symbols-outlined !text-lg text-[#D4AF37]"
							>store</span
						>
						Store Overview
						<span
							class="text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-100 dark:bg-white/5 text-gray-500"
							>{{ stores.length }} stores</span
						>
					</h3>
					<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
						<div
							v-for="store in stores"
							:key="store.warehouse"
							class="premium-card !p-4 hover:!border-[#D4AF37] transition-all group"
						>
							<!-- Store Header -->
							<div class="flex items-center justify-between mb-3">
								<div class="flex items-center gap-2">
									<div
										class="w-2.5 h-2.5 rounded-full"
										:class="healthDot(store.health)"
									></div>
									<h4
										class="text-sm font-bold text-gray-900 dark:text-white truncate"
									>
										{{ store.name }}
									</h4>
								</div>
								<span
									class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full"
									:class="healthBadge(store.health)"
									>{{ store.health }}</span
								>
							</div>
							<!-- Metrics Row -->
							<div class="grid grid-cols-4 gap-2 mb-3 text-center">
								<div>
									<p class="text-lg font-black text-gray-900 dark:text-white">
										{{ store.active }}
									</p>
									<p class="text-[8px] text-gray-400 uppercase">Active</p>
								</div>
								<div>
									<p
										class="text-lg font-black"
										:class="
											store.overdue > 0 ? 'text-red-500' : 'text-gray-400'
										"
									>
										{{ store.overdue }}
									</p>
									<p class="text-[8px] text-gray-400 uppercase">Overdue</p>
								</div>
								<div>
									<p class="text-lg font-black text-green-600">
										{{ store.completed_today }}
									</p>
									<p class="text-[8px] text-gray-400 uppercase">Done</p>
								</div>
								<div>
									<p class="text-lg font-black text-blue-600">
										{{ store.received_today }}
									</p>
									<p class="text-[8px] text-gray-400 uppercase">New</p>
								</div>
							</div>
							<!-- Status Breakdown Bar -->
							<div
								class="flex h-2 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 mb-2"
							>
								<div
									v-for="(count, status) in store.status_breakdown"
									:key="status"
									class="h-full transition-all"
									:class="statusBarColor(status)"
									:style="{
										width: (count / Math.max(store.active, 1)) * 100 + '%',
									}"
									:title="status + ': ' + count"
								></div>
							</div>
							<!-- Revenue -->
							<div
								class="flex items-center justify-between text-xs pt-2 border-t border-gray-100 dark:border-warm-border/30"
							>
								<span class="text-gray-400">Today's Revenue</span>
								<span class="font-black text-emerald-600"
									>${{ fmt(store.revenue_today) }}</span
								>
							</div>
						</div>
					</div>
				</div>

				<!-- Live Activity Feed -->
				<div class="premium-card !p-5">
					<div class="flex items-center justify-between mb-3">
						<h3
							class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2"
						>
							<span class="material-symbols-outlined !text-lg text-blue-500"
								>rss_feed</span
							>
							Live Activity Feed
						</h3>
						<select
							v-model="feedHours"
							@change="loadFeed"
							class="text-xs px-2 py-1 border border-gray-200 dark:border-warm-border rounded-lg bg-white dark:bg-[#1C1F26]"
						>
							<option :value="4">4 hours</option>
							<option :value="8">8 hours</option>
							<option :value="24">24 hours</option>
						</select>
					</div>
					<div class="space-y-1.5 max-h-72 overflow-y-auto">
						<div
							v-for="(ev, i) in feedEvents"
							:key="i"
							class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-warm-dark-900 transition text-xs"
						>
							<div
								class="w-2 h-2 rounded-full shrink-0"
								:class="statusDotColor(ev.status)"
							></div>
							<span class="text-gray-400 shrink-0 w-16 font-mono">{{
								formatTime(ev.timestamp)
							}}</span>
							<span class="font-bold text-[#D4AF37] shrink-0">{{ ev.repair }}</span>
							<span class="text-gray-600 dark:text-gray-300 truncate flex-1">
								→ {{ ev.status }}
								<span class="text-gray-400 ml-1">· {{ ev.customer }}</span>
							</span>
							<span class="text-gray-400 shrink-0">{{ ev.user_name }}</span>
						</div>
						<p
							v-if="!feedEvents.length"
							class="text-center text-gray-400 py-4 text-xs"
						>
							No recent activity
						</p>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { call } from 'frappe-ui'

const loading = ref(false)
const data = ref(null)
const feedEvents = ref([])
const feedHours = ref(4)
const isConnected = ref(false)
const realtimeEvents = ref([])

const sys = computed(() => data.value?.system || {})
const stores = computed(() => data.value?.stores || [])
const alerts = computed(() => data.value?.alerts || [])

async function refresh() {
	loading.value = true
	try {
		data.value = await call('zevar_core.api.live_monitor.get_command_center_data')
		isConnected.value = true
		await loadFeed()
	} catch (e) {
		console.error('Command center load failed:', e)
		isConnected.value = false
	} finally {
		loading.value = false
	}
}

async function loadFeed() {
	try {
		feedEvents.value =
			(await call('zevar_core.api.live_monitor.get_repair_live_feed', {
				hours: feedHours.value,
			})) || []
	} catch (e) {
		console.error('Feed load failed:', e)
	}
}

function openRepair(name) {
	window.open(`/pos/repairs?open=${name}`, '_blank')
}

// WebSocket listener for real-time events
function onRealtimeEvent(eventData) {
	realtimeEvents.value.unshift(eventData)
	if (realtimeEvents.value.length > 50) realtimeEvents.value.pop()

	// Prepend to feed
	feedEvents.value.unshift({
		type: 'status_change',
		repair: eventData.repair,
		customer: eventData.customer,
		status: eventData.new_status,
		timestamp: eventData.timestamp,
		user_name: eventData.user_name,
	})

	// Refresh store metrics every 5 realtime events
	if (realtimeEvents.value.length % 5 === 0) {
		call('zevar_core.api.live_monitor.get_command_center_data')
			.then((d) => {
				if (d) data.value = d
			})
			.catch(() => {})
	}
}

function onAnomalyAlert(alertData) {
	if (data.value) {
		data.value.alerts = [alertData, ...(data.value.alerts || [])].slice(0, 20)
	}
}

// Auto-refresh interval
let refreshTimer = null

onMounted(() => {
	refresh()
	refreshTimer = setInterval(refresh, 30000)

	// Subscribe to WebSocket events
	if (typeof frappe !== 'undefined' && frappe.realtime) {
		frappe.realtime.on('repair_live_event', onRealtimeEvent)
		frappe.realtime.on('repair_anomaly_alert', onAnomalyAlert)
	}
})

onBeforeUnmount(() => {
	if (refreshTimer) clearInterval(refreshTimer)
	if (typeof frappe !== 'undefined' && frappe.realtime) {
		frappe.realtime.off('repair_live_event', onRealtimeEvent)
		frappe.realtime.off('repair_anomaly_alert', onAnomalyAlert)
	}
})

// Helpers
function fmt(n) {
	return Number(n || 0).toLocaleString('en-US', {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	})
}
function formatTime(ts) {
	if (!ts) return ''
	try {
		return new Date(ts).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
	} catch {
		return String(ts)
	}
}
function alertClass(sev) {
	const c = {
		critical:
			'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800/30 text-red-700 dark:text-red-300',
		warning:
			'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/30 text-amber-700 dark:text-amber-300',
		info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800/30 text-blue-700 dark:text-blue-300',
	}
	return c[sev] || c.info
}
function alertIcon(sev) {
	return { critical: '🔴', warning: '🟡', info: 'ℹ️' }[sev] || 'ℹ️'
}
function healthDot(h) {
	return (
		{ healthy: 'bg-green-500', warning: 'bg-amber-500', critical: 'bg-red-500 animate-pulse' }[
			h
		] || 'bg-gray-400'
	)
}
function healthBadge(h) {
	return (
		{
			healthy: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
			warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
			critical: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
		}[h] || ''
	)
}
function statusBarColor(s) {
	return (
		{
			Received: 'bg-blue-400',
			Estimated: 'bg-yellow-400',
			Approved: 'bg-indigo-400',
			'In Progress': 'bg-orange-400',
			'Waiting for Parts': 'bg-purple-400',
			'Quality Check': 'bg-cyan-400',
			'Ready for Pickup': 'bg-green-400',
		}[s] || 'bg-gray-400'
	)
}
function statusDotColor(s) {
	return (
		{
			Received: 'bg-blue-500',
			Estimated: 'bg-yellow-500',
			Approved: 'bg-indigo-500',
			'In Progress': 'bg-orange-500',
			'Waiting for Parts': 'bg-purple-500',
			'Quality Check': 'bg-cyan-500',
			'Ready for Pickup': 'bg-green-500',
			Delivered: 'bg-gray-500',
		}[s] || 'bg-gray-400'
	)
}
</script>
