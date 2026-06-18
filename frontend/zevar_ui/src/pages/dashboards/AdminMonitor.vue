<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<!-- Header -->
			<div class="flex items-center justify-between mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<div
						class="w-10 h-10 rounded-xl flex items-center justify-center bg-blue-500/10"
					>
						<svg
							class="w-5 h-5 text-blue-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
							/>
						</svg>
					</div>
					<div>
						<h2 class="text-lg font-bold text-gray-900 dark:text-white">
							Live Monitor
						</h2>
						<p class="text-xs text-gray-400">
							Real-time sales, sessions, and employee activity
						</p>
					</div>
					<span
						v-if="latestSaleEvent || latestSessionEvent"
						class="ml-3 flex items-center gap-1 text-xs text-green-500"
					>
						<span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> Live
					</span>
				</div>
				<div class="flex items-center gap-2">
					<select
						v-model="feedHours"
						@change="fetchFeed"
						class="px-3 py-2 text-xs bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-gray-700 dark:text-gray-300"
					>
						<option :value="4">Last 4 hours</option>
						<option :value="8">Last 8 hours</option>
						<option :value="24">Last 24 hours</option>
						<option :value="72">Last 3 days</option>
					</select>
					<button
						@click="fetchFeed"
						class="p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-lg transition"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
					</button>
				</div>
			</div>

			<!-- KPI Cards -->
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0">
				<div
					class="p-4 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
				>
					<p class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">
						Today's Sales
					</p>
					<p class="text-xl font-bold text-gray-900 dark:text-white">
						${{ fmt(feed.summary?.total_sales || 0) }}
					</p>
					<p class="text-xs text-gray-400 mt-1">
						{{ feed.summary?.invoice_count || 0 }} invoices
					</p>
				</div>
				<div
					class="p-4 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
				>
					<p class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">
						Open Registers
					</p>
					<p class="text-xl font-bold text-blue-600">
						{{ feed.summary?.open_session_count || 0 }}
					</p>
					<p class="text-xs text-gray-400 mt-1">active sessions</p>
				</div>
				<div
					class="p-4 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
				>
					<p class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">
						Pending Overrides
					</p>
					<p class="text-xl font-bold text-amber-500">{{ overrides.count || 0 }}</p>
					<p class="text-xs text-gray-400 mt-1">tax exemption requests</p>
				</div>
				<div
					class="p-4 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border"
				>
					<p class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">
						Audit Events Today
					</p>
					<p class="text-xl font-bold text-gray-900 dark:text-white">
						{{ auditSummary.total_events || 0 }}
					</p>
					<p class="text-xs text-amber-500 mt-1">
						{{ auditSummary.warning_events || 0 }} warnings
					</p>
				</div>
			</div>

			<!-- Main Content: Tabs -->
			<div class="flex-1 overflow-hidden flex flex-col">
				<div
					class="flex gap-1 mb-3 flex-shrink-0 bg-gray-100 dark:bg-white/5 p-1 rounded-lg w-fit"
				>
					<button
						v-for="tab in tabs"
						:key="tab.key"
						@click="activeTab = tab.key"
						class="px-4 py-2 text-xs font-semibold rounded-md transition"
						:class="
							activeTab === tab.key
								? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm'
								: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
						"
					>
						{{ tab.label }}
					</button>
				</div>

				<div class="flex-1 overflow-y-auto">
					<!-- Active Sessions Tab -->
					<div v-if="activeTab === 'sessions'" class="space-y-3">
						<div
							v-if="sessions.length === 0"
							class="text-center py-12 text-gray-400 text-sm"
						>
							No open sessions
						</div>
						<div
							v-for="s in sessions"
							:key="s.name"
							@click="openUserDetail(s)"
							class="p-4 bg-white dark:bg-[#1a1c23] rounded-xl border border-gray-100 dark:border-warm-border flex items-center justify-between cursor-pointer hover:border-blue-300 dark:hover:border-blue-700 transition"
						>
							<div class="flex items-center gap-3">
								<div
									class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center"
								>
									<span
										class="text-sm font-bold text-blue-600 dark:text-blue-400"
										>{{
											(s.user_full_name || s.user || '?')[0].toUpperCase()
										}}</span
									>
								</div>
								<div>
									<p class="text-sm font-semibold text-gray-900 dark:text-white">
										{{ s.user_full_name || s.user }}
									</p>
									<p class="text-xs text-gray-400">
										{{ s.pos_profile }} | {{ s.warehouse || 'N/A' }}
									</p>
								</div>
							</div>
							<div class="text-right">
								<p class="text-sm font-medium text-gray-900 dark:text-white">
									{{ s.today_sales_count || 0 }} today |
									{{ s.sales_count || 0 }} total | ${{
										fmt(s.today_sales_total || 0)
									}}
								</p>
								<p class="text-xs text-gray-400">
									Opened {{ s.duration_hours || 0 }}h ago (${{
										fmt(s.opening_amount || 0)
									}}
									float)
								</p>
							</div>
							<button
								@click.stop="confirmForceClose(s)"
								class="ml-4 px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition"
							>
								Force Close
							</button>
						</div>
					</div>

					<!-- Recent Sales Tab -->
					<div v-if="activeTab === 'sales'" class="space-y-2">
						<div
							v-if="feed.recent_invoices?.length === 0"
							class="text-center py-12 text-gray-400 text-sm"
						>
							No recent sales
						</div>
						<div
							v-for="inv in feed.recent_invoices"
							:key="inv.name"
							class="p-3 bg-white dark:bg-[#1a1c23] rounded-lg border border-gray-100 dark:border-warm-border flex items-center justify-between"
						>
							<div>
								<p class="text-sm font-medium text-gray-900 dark:text-white">
									{{ inv.name }}
								</p>
								<p class="text-xs text-gray-400">
									{{ inv.salesperson_name || inv.owner }} | {{ inv.customer }}
								</p>
							</div>
							<div class="text-right">
								<p class="text-sm font-bold text-[#D4AF37]">
									${{ fmt(inv.grand_total) }}
								</p>
								<p class="text-xs text-gray-400">{{ formatTime(inv.creation) }}</p>
							</div>
						</div>
					</div>

					<!-- Tax Overrides Tab -->
					<div v-if="activeTab === 'overrides'" class="space-y-3">
						<div
							v-if="overrides.overrides?.length === 0"
							class="text-center py-12 text-gray-400 text-sm"
						>
							No pending tax exemption overrides
						</div>
						<div
							v-for="o in overrides.overrides || []"
							:key="o.name"
							class="p-4 bg-amber-50 dark:bg-amber-900/10 rounded-xl border border-amber-200 dark:border-amber-800/30"
						>
							<div class="flex items-center justify-between mb-2">
								<div>
									<p class="text-sm font-semibold text-gray-900 dark:text-white">
										Tax Exemption Request
									</p>
									<p class="text-xs text-gray-500">
										Requested by {{ o.requester_name }} at
										{{ formatTime(o.request_time) }}
									</p>
								</div>
								<span
									class="px-2 py-1 text-[10px] font-bold uppercase bg-amber-200 dark:bg-amber-800/40 text-amber-800 dark:text-amber-300 rounded"
									>Pending</span
								>
							</div>
							<div class="grid grid-cols-2 gap-2 text-sm mb-3">
								<div>
									<span class="text-gray-500">Customer:</span>
									<span class="font-medium">{{ o.customer_name }}</span>
								</div>
								<div>
									<span class="text-gray-500">Override #:</span>
									<span class="font-mono text-xs">{{ o.name }}</span>
								</div>
							</div>
							<p
								class="text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-white/5 p-2 rounded mb-3"
							>
								{{ o.reason }}
							</p>
							<div class="flex gap-2">
								<button
									@click="approveOverride(o.name)"
									class="flex-1 px-4 py-2 text-xs font-semibold bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
								>
									Approve
								</button>
								<button
									@click="rejectOverride(o.name)"
									class="flex-1 px-4 py-2 text-xs font-semibold bg-red-100 text-red-700 border border-red-200 rounded-lg hover:bg-red-200 transition"
								>
									Reject
								</button>
							</div>
						</div>
					</div>

					<!-- Audit Log Tab -->
					<div v-if="activeTab === 'audit'" class="space-y-2">
						<div
							v-if="auditLogs.logs?.length === 0"
							class="text-center py-12 text-gray-400 text-sm"
						>
							No audit events found
						</div>
						<div
							v-for="log in auditLogs.logs || []"
							:key="log.name"
							class="p-3 bg-white dark:bg-[#1a1c23] rounded-lg border border-gray-100 dark:border-warm-border flex items-center justify-between"
						>
							<div class="flex items-center gap-3">
								<span
									class="w-2 h-2 rounded-full flex-shrink-0"
									:class="
										log.severity === 'Warning' ? 'bg-amber-500' : 'bg-blue-500'
									"
								></span>
								<div>
									<p class="text-sm font-medium text-gray-900 dark:text-white">
										{{ formatEventType(log.event_type) }}
									</p>
									<p class="text-xs text-gray-400">
										{{ log.user_full_name || log.user }} |
										{{ log.reference_document || '-' }}
									</p>
								</div>
							</div>
							<div class="text-right">
								<span
									class="px-2 py-0.5 text-[10px] font-medium rounded"
									:class="
										log.category === 'Security'
											? 'bg-red-100 text-red-700'
											: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
									"
									>{{ log.category }}</span
								>
								<p class="text-xs text-gray-400 mt-1">
									{{ formatTime(log.timestamp) }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
		<!-- User detail drawer (click a session to open) -->
		<Teleport to="body">
			<div v-if="selectedUser" class="fixed inset-0 z-50 flex justify-end" @click.self="closeUserDetail">
				<div class="absolute inset-0 bg-black/40"></div>
				<div class="relative w-full max-w-md h-full bg-white dark:bg-[#1a1c23] shadow-2xl overflow-y-auto">
					<!-- header -->
					<div class="sticky top-0 bg-white dark:bg-[#1a1c23] border-b border-gray-100 dark:border-warm-border p-4 flex items-center justify-between z-10">
						<div class="flex items-center gap-3">
							<div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
								<span class="text-sm font-bold text-blue-600 dark:text-blue-400">{{
									(userDetail?.user_full_name || selectedUser.user || '?')[0].toUpperCase()
								}}</span>
							</div>
							<div>
								<p class="text-sm font-bold text-gray-900 dark:text-white">
									{{ userDetail?.user_full_name || selectedUser.user_full_name || selectedUser.user }}
								</p>
								<p class="text-[10px] flex items-center gap-1">
									<span
										class="px-1.5 py-0.5 rounded text-[9px] font-bold"
										:class="userDetail?.status === 'Open'
											? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
											: userDetail?.status === 'Logged In'
												? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
												: 'bg-gray-100 text-gray-500'"
										>{{ userDetail?.status || '...' }}</span>
									<span class="text-gray-400">{{ userDetail?.employee_name || '' }}</span>
								</p>
							</div>
						</div>
						<button @click="closeUserDetail" class="text-gray-400 hover:text-gray-700">
							<span class="material-symbols-outlined">close</span>
						</button>
					</div>

					<div v-if="detailLoading" class="flex justify-center py-16">
						<span class="material-symbols-outlined animate-spin text-gray-300">progress_activity</span>
					</div>

					<div v-else-if="userDetail" class="p-4 space-y-4">
						<!-- KPI grid -->
						<div class="grid grid-cols-3 gap-2">
							<div class="premium-card !p-2 text-center">
								<p class="text-[9px] text-gray-400 uppercase">Revenue</p>
								<p class="text-sm font-bold text-emerald-600">${{ fmt(userDetail.kpi.revenue) }}</p>
							</div>
							<div class="premium-card !p-2 text-center">
								<p class="text-[9px] text-gray-400 uppercase">Txn</p>
								<p class="text-sm font-bold text-gray-900 dark:text-white">{{ userDetail.kpi.txn_count }}</p>
							</div>
							<div class="premium-card !p-2 text-center">
								<p class="text-[9px] text-gray-400 uppercase">AOV</p>
								<p class="text-sm font-bold text-amber-600">${{ fmt(userDetail.kpi.aov) }}</p>
							</div>
							<div class="premium-card !p-2 text-center">
								<p class="text-[9px] text-gray-400 uppercase">Units</p>
								<p class="text-sm font-bold text-gray-900 dark:text-white">{{ userDetail.kpi.units }}</p>
							</div>
							<div class="premium-card !p-2 text-center">
								<p class="text-[9px] text-gray-400 uppercase">UPT</p>
								<p class="text-sm font-bold text-amber-600">{{ userDetail.kpi.upt }}</p>
							</div>
							<div class="premium-card !p-2 text-center">
								<p class="text-[9px] text-gray-400 uppercase">Items/hr</p>
								<p class="text-sm font-bold text-purple-600">{{ userDetail.kpi.items_per_hour }}</p>
							</div>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div class="premium-card !p-2">
								<p class="text-[9px] text-gray-400 uppercase">Commission today</p>
								<p class="text-base font-bold text-emerald-600">${{ fmt(userDetail.kpi.commission) }}</p>
							</div>
							<div class="premium-card !p-2">
								<p class="text-[9px] text-gray-400 uppercase">Last sale</p>
								<p class="text-xs font-bold text-gray-900 dark:text-white">
									{{ userDetail.last_sale_time ? formatTime(userDetail.last_sale_time) : '—' }}
								</p>
							</div>
						</div>

						<!-- Session -->
						<div v-if="userDetail.session" class="premium-card !p-3">
							<div class="flex items-center justify-between">
								<p class="text-xs font-bold text-gray-900 dark:text-white">Open Register</p>
								<button
									@click="endSession"
									:disabled="endingSession"
									class="px-2.5 py-1 text-[10px] font-bold text-red-600 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50"
								>
									{{ endingSession ? 'Closing…' : 'End Session' }}
								</button>
							</div>
							<p class="text-[10px] text-gray-400 mt-1">
								{{ userDetail.session.pos_profile }} · {{ userDetail.session.warehouse || 'N/A' }} ·
								{{ userDetail.session.duration_hours }}h · ${{ fmt(userDetail.session.opening_amount) }} float
							</p>
						</div>
						<div v-else class="premium-card !p-3 text-center">
							<p class="text-[11px] text-gray-400">
								No open register<span v-if="userDetail.status === 'Logged In'"> — logged in but no cash drawer open.</span>
							</p>
						</div>

						<!-- Recent sales feed -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<p class="text-xs font-bold text-gray-900 dark:text-white">Recent Sales (today)</p>
								<button @click="reloadDetail" class="text-[10px] text-blue-500 hover:underline">refresh</button>
							</div>
							<div v-if="userDetail.recent_sales.length === 0" class="text-[11px] text-gray-400 text-center py-4">
								No sales yet today.
							</div>
							<div
								v-for="r in userDetail.recent_sales"
								:key="r.name"
								class="flex items-center justify-between py-2 border-b border-gray-50 dark:border-gray-800/50"
							>
								<div>
									<p class="text-xs font-medium text-gray-900 dark:text-white">{{ r.customer || 'Walk-in' }}</p>
									<p class="text-[10px] text-gray-400">{{ r.items }} item(s) · {{ formatTime(r.time) }}</p>
								</div>
								<span class="text-xs font-bold text-emerald-600">${{ fmt(r.total) }}</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</Teleport>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { createResource, call } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import { fmt } from '@/utils/format'
import { useSessionStore } from '@/stores/session.js'

const session = useSessionStore()

const feedHours = ref(24)
const activeTab = ref('sessions')
const tabs = [
	{ key: 'sessions', label: 'Active Sessions' },
	{ key: 'sales', label: 'Recent Sales' },
	{ key: 'overrides', label: 'Tax Overrides' },
	{ key: 'audit', label: 'Audit Log' },
]

const feed = ref({ recent_invoices: [], open_sessions: [], summary: {} })
const sessions = ref([])
const overrides = ref({ overrides: [], count: 0 })
const auditLogs = ref({ logs: [] })
const auditSummary = ref({ total_events: 0, warning_events: 0 })

const latestSaleEvent = ref(null)
const latestSessionEvent = ref(null)

// User detail drawer
const selectedUser = ref(null)
const userDetail = ref(null)
const detailLoading = ref(false)
const endingSession = ref(false)

// Resources
const liveFeedResource = createResource({
	url: 'zevar_core.api.pos_session.get_live_sales_feed',
	auto: false,
	onSuccess(data) {
		if (data) feed.value = data
	},
	onError(err) {
		console.warn('[LiveMonitor] Sales feed failed:', err?.messages || err)
	},
})

const sessionsResource = createResource({
	url: 'zevar_core.api.pos_session.get_all_active_sessions',
	auto: false,
	onSuccess(data) {
		if (data) sessions.value = data.sessions || []
	},
	onError(err) {
		console.warn('[LiveMonitor] Sessions failed:', err?.messages || err)
	},
})

const overridesResource = createResource({
	url: 'zevar_core.api.pos.get_pending_overrides',
	auto: false,
	onSuccess(data) {
		if (data) overrides.value = data
	},
	onError(err) {
		console.warn('[LiveMonitor] Overrides failed:', err?.messages || err)
	},
})

const auditResource = createResource({
	url: 'zevar_core.api.audit_log.get_audit_logs',
	auto: false,
	onSuccess(data) {
		if (data) auditLogs.value = data
	},
	onError(err) {
		console.warn('[LiveMonitor] Audit logs failed:', err?.messages || err)
	},
})

const auditSummaryResource = createResource({
	url: 'zevar_core.api.audit_log.get_audit_summary',
	auto: false,
	onSuccess(data) {
		if (data) auditSummary.value = data
	},
	onError(err) {
		console.warn('[LiveMonitor] Audit summary failed:', err?.messages || err)
	},
})

async function fetchFeed() {
	await Promise.allSettled([
		liveFeedResource.submit({ hours: feedHours.value }),
		sessionsResource.submit(),
		overridesResource.submit(),
		auditResource.submit({ page_size: 50 }),
		auditSummaryResource.submit(),
	])
}

async function approveOverride(name) {
	try {
		await call('zevar_core.api.pos.approve_tax_exemption_override', { override_name: name })
		overridesResource.submit()
	} catch (e) {
		console.error('Approve failed:', e)
	}
}

async function rejectOverride(name) {
	try {
		await call('zevar_core.api.pos.reject_tax_exemption_override', { override_name: name })
		overridesResource.submit()
	} catch (e) {
		console.error('Reject failed:', e)
	}
}

async function confirmForceClose(session) {
	if (!confirm(`Force close session ${session.name} (${session.user_full_name})?`)) return
	try {
		await call('zevar_core.api.pos_session.force_close_session', {
			session_name: session.name,
			reason: 'Force closed by admin from Live Monitor',
		})
		sessionsResource.submit()
		liveFeedResource.submit({ hours: feedHours.value })
	} catch (e) {
		console.error('Force close failed:', e)
	}
}

async function openUserDetail(s) {
	selectedUser.value = s
	userDetail.value = null
	detailLoading.value = true
	try {
		userDetail.value = await call('zevar_core.api.pos_session.get_live_user_detail', { user: s.user })
	} catch (e) {
		console.error('User detail failed:', e)
	} finally {
		detailLoading.value = false
	}
}

function closeUserDetail() {
	selectedUser.value = null
	userDetail.value = null
}

async function reloadDetail() {
	if (!selectedUser.value) return
	detailLoading.value = true
	try {
		userDetail.value = await call('zevar_core.api.pos_session.get_live_user_detail', {
			user: selectedUser.value.user,
		})
	} catch (e) {
		console.error('Reload detail failed:', e)
	} finally {
		detailLoading.value = false
	}
}

async function endSession() {
	if (!userDetail.value?.session?.name) return
	if (!confirm(`End ${userDetail.value.user_full_name}'s register session?`)) return
	endingSession.value = true
	try {
		await call('zevar_core.api.pos_session.force_close_session', {
			session_name: userDetail.value.session.name,
			reason: 'Closed from Live Monitor detail',
		})
		await reloadDetail()
		sessionsResource.submit()
		liveFeedResource.submit({ hours: feedHours.value })
	} catch (e) {
		console.error('End session failed:', e)
	} finally {
		endingSession.value = false
	}
}

function formatTime(ts) {
	if (!ts) return ''
	try {
		const d = new Date(ts)
		return d.toLocaleString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
		})
	} catch {
		return String(ts)
	}
}

function formatEventType(type) {
	return String(type || '')
		.replace(/_/g, ' ')
		.replace(/\b\w/g, (c) => c.toUpperCase())
}

// Auto-refresh every 30 seconds
let refreshInterval = null

onMounted(() => {
	fetchFeed()
	refreshInterval = setInterval(fetchFeed, 30000)

	// Start realtime monitoring
	session.startSalesMonitoring()
})

onBeforeUnmount(() => {
	if (refreshInterval) clearInterval(refreshInterval)
	session.stopSalesMonitoring()
})
</script>
