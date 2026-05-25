<template>
	<div class="relative" ref="panelRef">
		<button
			@click.stop="isOpen = !isOpen"
			class="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0 touch-target"
			aria-label="Notifications"
		>
			<span class="material-symbols-outlined !text-xl text-gray-600 dark:text-gray-300">
				{{ unreadCount > 0 ? 'notifications_active' : 'notifications' }}
			</span>
			<span
				v-if="unreadCount > 0"
				class="absolute top-0.5 right-0.5 h-4 min-w-[16px] flex items-center justify-center bg-red-500 text-white text-[9px] font-bold rounded-full px-0.5 shadow-md"
			>
				{{ unreadCount > 9 ? '9+' : unreadCount }}
			</span>
		</button>

		<!-- Dropdown Panel -->
		<Transition
			enter-active-class="transition duration-200 ease-out"
			enter-from-class="transform scale-95 opacity-0"
			enter-to-class="transform scale-100 opacity-100"
			leave-active-class="transition duration-75 ease-in"
			leave-from-class="transform scale-100 opacity-100"
			leave-to-class="transform scale-95 opacity-0"
		>
			<div
				v-if="isOpen"
				class="absolute right-0 mt-2 w-80 sm:w-96 bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 overflow-hidden"
			>
				<!-- Header -->
				<div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white">Alerts</h3>
					<div class="flex items-center gap-2">
						<span v-if="summary.critical" class="text-[10px] font-bold bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 px-1.5 py-0.5 rounded-full">
							{{ summary.critical }} critical
						</span>
						<span v-if="summary.warning" class="text-[10px] font-bold bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 px-1.5 py-0.5 rounded-full">
							{{ summary.warning }} warning
						</span>
					</div>
				</div>

				<!-- Alert list -->
				<div class="max-h-80 overflow-auto custom-scrollbar">
					<div v-if="loading" class="flex items-center justify-center py-8">
						<span class="material-symbols-outlined animate-spin text-gray-300">progress_activity</span>
					</div>
					<div v-else-if="alerts.length === 0" class="py-8 text-center">
						<span class="material-symbols-outlined !text-3xl text-gray-300 mb-2 block">notifications_off</span>
						<p class="text-xs text-gray-400">No active alerts</p>
					</div>
					<template v-else>
						<button
							v-for="alert in alerts"
							:key="alert.type + alert.title"
							@click="handleAlertClick(alert)"
							class="w-full flex items-start gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors text-left border-b border-gray-50 dark:border-gray-800/50 last:border-0"
						>
							<span
								class="mt-0.5 w-2 h-2 rounded-full shrink-0"
								:class="{
									'bg-red-500': alert.severity === 'critical',
									'bg-amber-400': alert.severity === 'warning',
									'bg-blue-400': alert.severity === 'info',
								}"
							></span>
							<div class="flex-1 min-w-0">
								<p class="text-xs font-bold text-gray-900 dark:text-white truncate">{{ alert.title }}</p>
								<p class="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">{{ alert.message }}</p>
							</div>
							<span class="text-[9px] text-gray-400 shrink-0 mt-0.5">{{ formatTime(alert.timestamp) }}</span>
						</button>
					</template>
				</div>

				<!-- Footer -->
				<div v-if="alerts.length > 0" class="px-4 py-2 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
					<p class="text-[10px] text-gray-400 text-center">
						{{ alerts.length }} alert{{ alerts.length !== 1 ? 's' : '' }} &middot; Updated {{ formatTime(latestTimestamp) }}
					</p>
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const isOpen = ref(false)
const loading = ref(true)
const alerts = ref([])
const summary = ref({ critical: 0, warning: 0, info: 0, total: 0, recent: [] })
const panelRef = ref(null)

const unreadCount = computed(() => summary.value.critical + summary.value.warning)
const latestTimestamp = computed(() => {
	if (alerts.value.length) return alerts.value[0]?.timestamp
	return ''
})

async function fetchSummary() {
	try {
		const res = await fetch('/api/method/zevar_core.api.notifications.get_alert_summary', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		if (!res.ok) return
		const json = await res.json()
		const data = json.message || json
		summary.value = data
	} catch (e) {
		console.error('Alert summary error:', e)
	}
}

async function fetchAlerts() {
	loading.value = true
	try {
		const res = await fetch('/api/method/zevar_core.api.notifications.get_alerts', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		if (!res.ok) return
		const json = await res.json()
		const data = json.message || json
		alerts.value = data.alerts || []
	} catch (e) {
		console.error('Alerts error:', e)
	} finally {
		loading.value = false
	}
}

function handleAlertClick(alert) {
	isOpen.value = false
	if (alert.reference_doctype && alert.reference_name) {
		window.open(`/app/${alert.reference_doctype.toLowerCase().replace(' ', '-')}/${alert.reference_name}`, '_blank')
	}
}

function formatTime(ts) {
	if (!ts) return ''
	try {
		const d = new Date(ts)
		const now = new Date()
		const diffMs = now - d
		const diffMin = Math.floor(diffMs / 60000)
		if (diffMin < 1) return 'now'
		if (diffMin < 60) return `${diffMin}m ago`
		const diffHr = Math.floor(diffMin / 60)
		if (diffHr < 24) return `${diffHr}h ago`
		return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
	} catch {
		return ''
	}
}

// Click outside to close
function onClickOutside(e) {
	if (panelRef.value && !panelRef.value.contains(e.target)) {
		isOpen.value = false
	}
}

// WebSocket handler for real-time alerts
function onAlertEvent(data) {
	fetchSummary()
	if (isOpen.value) fetchAlerts()
}

// Refresh cycle
let intervalId = null

onMounted(() => {
	document.addEventListener('click', onClickOutside)
	fetchSummary()

	if (window.frappe?.realtime) {
		window.frappe.realtime.on('zevar_alert', onAlertEvent)
	}

	// Refresh summary every 2 minutes
	intervalId = setInterval(fetchSummary, 120000)
})

onUnmounted(() => {
	document.removeEventListener('click', onClickOutside)
	if (window.frappe?.realtime) {
		window.frappe.realtime.off('zevar_alert', onAlertEvent)
	}
	if (intervalId) clearInterval(intervalId)
})

// Fetch full list when dropdown opens
import { watch } from 'vue'
watch(isOpen, (open) => {
	if (open) fetchAlerts()
})
</script>
