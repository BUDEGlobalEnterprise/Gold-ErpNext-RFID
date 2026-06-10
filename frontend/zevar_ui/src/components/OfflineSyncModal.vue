<template>
	<BaseModal :show="show" max-width="max-w-2xl" :show-close="true" @close="$emit('close')">
		<div class="p-6 font-sans">
			<!-- Header -->
			<div class="flex items-center gap-3 mb-6">
				<div
					class="w-10 h-10 rounded-full bg-[#D4AF37]/10 flex items-center justify-center border border-[#D4AF37]/30"
				>
					<svg
						class="w-5 h-5 text-[#D4AF37]"
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
				</div>
				<div>
					<h3
						class="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wider"
					>
						Offline Sync & Logs
					</h3>
					<p class="text-xs text-gray-500 dark:text-gray-400">
						Manage queued transactions and review human-readable error explanations
					</p>
				</div>
			</div>

			<!-- Status Bar -->
			<div
				class="flex items-center justify-between p-4 bg-gray-50 dark:bg-warm-dark-700/20 border border-gray-100 dark:border-warm-border rounded-xl mb-6 text-xs"
			>
				<div class="flex items-center gap-4">
					<div class="flex items-center gap-1.5 font-bold uppercase">
						<span class="relative flex h-2.5 w-2.5">
							<span
								v-if="offline.isOnline"
								class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
							></span>
							<span
								class="relative inline-flex rounded-full h-2.5 w-2.5"
								:class="offline.isOnline ? 'bg-green-500' : 'bg-red-500'"
							></span>
						</span>
						<span
							:class="
								offline.isOnline
									? 'text-green-600 dark:text-green-400'
									: 'text-red-500'
							"
						>
							{{ offline.isOnline ? 'Online' : 'Offline Mode' }}
						</span>
					</div>
					<div class="text-gray-400 dark:text-gray-500 font-mono">
						Last Sync:
						{{ offline.lastSyncTime ? formatTime(offline.lastSyncTime) : 'Never' }}
					</div>
				</div>

				<button
					v-if="offline.isOnline"
					@click="triggerManualSync"
					:disabled="syncing"
					class="px-3.5 py-1.5 bg-[#D4AF37] hover:bg-[#b5952f] text-black text-xs font-bold rounded-lg transition disabled:opacity-50 flex items-center gap-1"
				>
					<svg
						v-if="syncing"
						class="w-3.5 h-3.5 animate-spin"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<circle
							cx="12"
							cy="12"
							r="10"
							stroke-width="3"
							class="opacity-25"
						></circle>
						<path
							stroke-width="3"
							class="opacity-75"
							d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
						/>
					</svg>
					<span>{{ syncing ? 'Syncing...' : 'Sync Queue Now' }}</span>
				</button>
			</div>

			<!-- Tabs -->
			<div
				class="flex border-b border-gray-100 dark:border-warm-border/50 mb-4 text-xs font-bold uppercase tracking-wider"
			>
				<button
					@click="activeTab = 'failed'"
					class="pb-2.5 px-4 border-b-2 transition"
					:class="
						activeTab === 'failed'
							? 'border-red-500 text-red-600 dark:text-red-400'
							: 'border-transparent text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
					"
				>
					Failed ({{ failedItems.length }})
				</button>
				<button
					@click="activeTab = 'conflicts'"
					class="pb-2.5 px-4 border-b-2 transition"
					:class="
						activeTab === 'conflicts'
							? 'border-amber-500 text-amber-600 dark:text-amber-400'
							: 'border-transparent text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
					"
				>
					Conflicts ({{ conflictItems.length }})
				</button>
				<button
					@click="activeTab = 'pending'"
					class="pb-2.5 px-4 border-b-2 transition"
					:class="
						activeTab === 'pending'
							? 'border-[#D4AF37] text-[#D4AF37]'
							: 'border-transparent text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
					"
				>
					Pending ({{ pendingItems.length }})
				</button>
				<button
					@click="activeTab = 'synced'"
					class="pb-2.5 px-4 border-b-2 transition"
					:class="
						activeTab === 'synced'
							? 'border-green-500 text-green-600 dark:text-green-400'
							: 'border-transparent text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
					"
				>
					History ({{ syncedItems.length }})
				</button>
			</div>

			<!-- Content Area -->
			<div class="min-h-[250px] max-h-[400px] overflow-y-auto custom-scrollbar pr-1 text-sm">
				<!-- Loading State -->
				<div v-if="loading" class="py-12 text-center">
					<div
						class="animate-spin rounded-full h-6 w-6 border-2 border-[#D4AF37] border-t-transparent mx-auto mb-3"
					></div>
					<span class="text-xs text-gray-400">Loading queued transactions...</span>
				</div>

				<div v-else>
					<!-- Tab: Failed -->
					<div v-if="activeTab === 'failed'">
						<div
							v-if="failedItems.length === 0"
							class="py-12 text-center text-gray-400 text-xs"
						>
							🎉 No failed sync logs! Everything has processed successfully.
						</div>
						<div v-else class="space-y-4">
							<div
								v-for="item in failedItems"
								:key="item.id"
								class="p-4 bg-red-50/30 dark:bg-red-950/10 border border-red-100/50 dark:border-red-900/20 rounded-xl space-y-3"
							>
								<!-- Meta info -->
								<div class="flex items-start justify-between">
									<div>
										<span
											class="px-2 py-0.5 rounded bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 text-[10px] font-bold uppercase tracking-wider"
										>
											{{ item.mode }} Transaction
										</span>
										<span
											class="text-xs font-bold font-mono text-gray-700 dark:text-gray-300 ml-2"
										>
											ID: {{ item.id }}
										</span>
									</div>
									<span class="text-[11px] text-gray-400">
										{{ formatDateTime(item.created_at) }}
									</span>
								</div>

								<!-- Details -->
								<div
									class="grid grid-cols-2 gap-4 text-xs font-medium py-1.5 border-t border-b border-gray-100 dark:border-warm-border/30"
								>
									<div>
										<span class="text-gray-400 block">Amount:</span>
										<span
											class="font-mono text-gray-900 dark:text-white font-bold text-sm"
										>
											${{ getAmount(item).toFixed(2) }}
										</span>
									</div>
									<div>
										<span class="text-gray-400 block">Customer:</span>
										<span class="text-gray-800 dark:text-gray-200">
											{{ getCustomerName(item) }}
										</span>
									</div>
								</div>

								<!-- Human Error Message box -->
								<div
									class="p-3 bg-red-500/5 border border-red-500/20 rounded-lg text-xs leading-relaxed"
								>
									<p
										class="font-bold text-red-600 dark:text-red-400 mb-1 flex items-center gap-1"
									>
										<span>⚠️</span> Human-Readable Explanation:
									</p>
									<p class="text-gray-700 dark:text-gray-300">
										{{ translateError(item.error) }}
									</p>
								</div>

								<!-- Expandable Technical Log Details -->
								<div class="text-xs">
									<button
										@click="toggleExpand(item.id)"
										class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 font-bold flex items-center gap-1"
									>
										<span>{{ isExpanded(item.id) ? '▼' : '▶' }}</span>
										<span>Technical Log Details</span>
									</button>
									<div
										v-if="isExpanded(item.id)"
										class="mt-2 p-2.5 bg-gray-900 dark:bg-black text-gray-300 font-mono text-[10px] rounded border dark:border-warm-border overflow-x-auto whitespace-pre-wrap max-h-36"
									>
										{{ item.error || 'No traceback log details available.' }}
									</div>
								</div>

								<!-- Controls -->
								<div
									class="flex items-center justify-end gap-2 pt-2 border-t border-gray-100 dark:border-warm-border/30"
								>
									<button
										@click="deleteItem(item.id)"
										class="px-3 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition"
										title="Delete log entry"
									>
										Discard Order
									</button>
									<button
										@click="retryItem(item.id)"
										:disabled="syncing || !offline.isOnline"
										class="px-3 py-1.5 text-xs font-bold bg-[#D4AF37] hover:bg-[#b5952f] text-black rounded-lg transition disabled:opacity-40"
									>
										Retry Sync
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Tab: Conflicts -->
					<div v-if="activeTab === 'conflicts'">
						<div
							v-if="conflictItems.length === 0"
							class="py-12 text-center text-gray-400 text-xs"
						>
							✨ No current data conflicts detected in local storage.
						</div>
						<div v-else class="space-y-4">
							<div
								v-for="item in conflictItems"
								:key="item.id"
								class="p-4 bg-amber-50/30 dark:bg-amber-950/10 border border-amber-100/50 dark:border-amber-900/20 rounded-xl space-y-3"
							>
								<!-- Meta info -->
								<div class="flex items-start justify-between">
									<div>
										<span
											class="px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 text-[10px] font-bold uppercase tracking-wider"
										>
											{{ item.mode }} Conflict
										</span>
										<span
											class="text-xs font-bold font-mono text-gray-700 dark:text-gray-300 ml-2"
										>
											ID: {{ item.id }}
										</span>
									</div>
									<span class="text-[11px] text-gray-400">
										{{ formatDateTime(item.created_at) }}
									</span>
								</div>

								<!-- Details -->
								<div
									class="grid grid-cols-2 gap-4 text-xs font-medium py-1.5 border-t border-b border-gray-100 dark:border-warm-border/30"
								>
									<div>
										<span class="text-gray-400 block">Amount:</span>
										<span
											class="font-mono text-gray-900 dark:text-white font-bold text-sm"
										>
											${{ getAmount(item).toFixed(2) }}
										</span>
									</div>
									<div>
										<span class="text-gray-400 block">Conflict Type:</span>
										<span
											class="text-amber-600 dark:text-amber-400 uppercase font-black tracking-wider text-[10px]"
										>
											{{ item.conflict_type || 'Unknown' }}
										</span>
									</div>
								</div>

								<!-- Human Message -->
								<div
									class="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg text-xs leading-relaxed"
								>
									<p
										class="font-bold text-amber-600 dark:text-amber-400 mb-1 flex items-center gap-1"
									>
										<span>⚠️</span> Conflict Explanation:
									</p>
									<p class="text-gray-700 dark:text-gray-300">
										{{ translateError(item.error) }}
									</p>
								</div>

								<!-- Expandable Technical Log Details -->
								<div class="text-xs">
									<button
										@click="toggleExpand(item.id)"
										class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 font-bold flex items-center gap-1"
									>
										<span>{{ isExpanded(item.id) ? '▼' : '▶' }}</span>
										<span>Technical Log Details</span>
									</button>
									<div
										v-if="isExpanded(item.id)"
										class="mt-2 p-2.5 bg-gray-900 dark:bg-black text-gray-300 font-mono text-[10px] rounded border dark:border-warm-border overflow-x-auto whitespace-pre-wrap max-h-36"
									>
										{{ item.error || 'No server message details available.' }}
									</div>
								</div>

								<!-- Controls -->
								<div
									class="flex items-center justify-end gap-2 pt-2 border-t border-gray-100 dark:border-warm-border/30"
								>
									<button
										@click="deleteItem(item.id)"
										class="px-3 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition"
									>
										Cancel Order
									</button>
									<button
										@click="retryConflictModified(item)"
										class="px-3 py-1.5 text-xs font-bold bg-amber-500 hover:bg-amber-600 text-black rounded-lg transition"
									>
										Modify & Retry
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Tab: Pending -->
					<div v-if="activeTab === 'pending'">
						<div
							v-if="pendingItems.length === 0"
							class="py-12 text-center text-gray-400 text-xs"
						>
							💡 No pending transactions queued.
						</div>
						<div v-else class="space-y-4">
							<div
								v-for="item in pendingItems"
								:key="item.id"
								class="p-4 bg-gray-50/50 dark:bg-warm-dark-700/10 border border-gray-100 dark:border-warm-border/30 rounded-xl space-y-3"
							>
								<!-- Meta info -->
								<div class="flex items-start justify-between">
									<div>
										<span
											class="px-2 py-0.5 rounded bg-gray-200 text-gray-700 dark:bg-warm-dark-600 dark:text-gray-300 text-[10px] font-bold uppercase tracking-wider"
										>
											{{ item.mode }} Queued
										</span>
										<span
											class="text-xs font-bold font-mono text-gray-700 dark:text-gray-300 ml-2"
										>
											ID: {{ item.id }}
										</span>
									</div>
									<span class="text-[11px] text-gray-400">
										{{ formatDateTime(item.created_at) }}
									</span>
								</div>

								<!-- Details -->
								<div
									class="grid grid-cols-2 gap-4 text-xs font-medium py-1.5 border-t border-b border-gray-100 dark:border-warm-border/30"
								>
									<div>
										<span class="text-gray-400 block">Amount:</span>
										<span
											class="font-mono text-gray-900 dark:text-white font-bold text-sm"
										>
											${{ getAmount(item).toFixed(2) }}
										</span>
									</div>
									<div>
										<span class="text-gray-400 block">Customer:</span>
										<span class="text-gray-800 dark:text-gray-200">
											{{ getCustomerName(item) }}
										</span>
									</div>
								</div>

								<!-- Status Info -->
								<div
									class="text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between"
								>
									<span
										>Attempts: {{ item.attempts || 0 }}/{{
											item.max_attempts || 5
										}}</span
									>
									<span v-if="item.next_retry" class="font-mono">
										Next retry: {{ formatTime(item.next_retry) }}
									</span>
								</div>

								<!-- Controls -->
								<div
									class="flex items-center justify-end gap-2 pt-2 border-t border-gray-100 dark:border-warm-border/30"
								>
									<button
										@click="deleteItem(item.id)"
										class="px-3 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 rounded-lg transition"
									>
										Discard Queue
									</button>
									<button
										@click="retryItem(item.id)"
										:disabled="syncing || !offline.isOnline"
										class="px-3 py-1.5 text-xs font-bold bg-[#D4AF37] hover:bg-[#b5952f] text-black rounded-lg transition disabled:opacity-40"
									>
										Force Sync
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Tab: Synced (History) -->
					<div v-if="activeTab === 'synced'">
						<div
							v-if="syncedItems.length === 0"
							class="py-12 text-center text-gray-400 text-xs"
						>
							No recent offline history found on this device.
						</div>
						<div v-else class="space-y-4">
							<div
								v-for="item in syncedItems"
								:key="item.id"
								class="p-4 bg-green-50/30 dark:bg-green-950/10 border border-green-100/50 dark:border-green-900/20 rounded-xl space-y-3 opacity-80 hover:opacity-100 transition"
							>
								<!-- Meta info -->
								<div class="flex items-start justify-between">
									<div>
										<span
											class="px-2 py-0.5 rounded bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 w-fit"
										>
											<svg
												class="w-3 h-3"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M5 13l4 4L19 7"
												/>
											</svg>
											{{ item.mode }} Synced
										</span>
										<span
											class="text-xs font-bold font-mono text-gray-700 dark:text-gray-300 ml-1 mt-1 block"
										>
											ID: {{ item.id }}
										</span>
									</div>
									<div class="text-right">
										<span class="text-[11px] text-gray-400 block mb-0.5">
											Created: {{ formatDateTime(item.created_at) }}
										</span>
										<span
											class="text-[11px] text-green-600 dark:text-green-400 font-medium"
										>
											Synced:
											{{ formatTime(item.synced_at || item.created_at) }}
										</span>
									</div>
								</div>

								<!-- Details -->
								<div
									class="grid grid-cols-2 gap-4 text-xs font-medium py-1.5 border-t border-gray-100 dark:border-warm-border/30"
								>
									<div>
										<span class="text-gray-400 block">Amount:</span>
										<span
											class="font-mono text-gray-900 dark:text-white font-bold text-sm"
										>
											${{ getAmount(item).toFixed(2) }}
										</span>
									</div>
									<div>
										<span class="text-gray-400 block">Customer:</span>
										<span class="text-gray-800 dark:text-gray-200">
											{{ getCustomerName(item) }}
										</span>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import BaseModal from '@/components/BaseModal.vue'
import { useOfflineStore } from '@/stores/offline.js'

const props = defineProps({
	show: { type: Boolean, required: true },
})

const emit = defineEmits(['close'])

const offline = useOfflineStore()

const activeTab = ref('failed')
const loading = ref(false)
const syncing = ref(false)
const expandedItems = ref({})

const failedItems = ref([])
const conflictItems = ref([])
const pendingItems = ref([])
const syncedItems = ref([])

async function loadData() {
	loading.value = true
	try {
		const [failed, conflicts, pending, synced] = await Promise.all([
			offline.getFailedOrders(),
			offline.getConflicts(),
			offline.getPendingOrdersList(),
			offline.getSyncedOrders(),
		])
		failedItems.value = failed || []
		conflictItems.value = conflicts || []
		pendingItems.value = pending || []
		syncedItems.value = synced || []
	} catch (e) {
		console.error('Failed to load offline data lists:', e)
	} finally {
		loading.value = false
	}
}

// Watchers
watch(
	() => props.show,
	(newVal) => {
		if (newVal) {
			loadData()
		}
	}
)

onMounted(() => {
	if (props.show) {
		loadData()
	}
})

// Formatting Helpers
function formatTime(isoOrTimestamp) {
	if (!isoOrTimestamp) return ''
	const d = new Date(isoOrTimestamp)
	return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function formatDateTime(isoOrTimestamp) {
	if (!isoOrTimestamp) return ''
	const d = new Date(isoOrTimestamp)
	return d.toLocaleString([], {
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	})
}

function getAmount(item) {
	const p = item.payload || {}
	if (item.mode === 'layaway') {
		const payments =
			typeof p.payments === 'string' ? JSON.parse(p.payments || '[]') : p.payments || []
		return payments.reduce((acc, curr) => acc + (curr.amount || 0), 0)
	}
	if (item.mode === 'repair') {
		return Number(p.amount || 0)
	}
	// Sale mode
	let amt = Number(p.grand_total || p.total || 0)
	if (!amt && p.payments) {
		try {
			const payments =
				typeof p.payments === 'string' ? JSON.parse(p.payments || '[]') : p.payments || []
			amt = payments.reduce((acc, curr) => acc + (curr.amount || 0), 0)
		} catch (e) {
			// ignore
		}
	}
	return amt
}

function getCustomerName(item) {
	const p = item.payload || {}
	if (item.mode === 'layaway') {
		return p.customer_name || 'Layaway Account'
	}
	if (item.mode === 'repair') {
		return p.customer_name || 'Repair Customer'
	}
	return p.customer_name || p.customer || 'Walk-in Customer'
}

// Error Translator
function translateError(errorStr) {
	if (!errorStr)
		return 'An unknown server or network error occurred during transaction synchronization.'
	const err = String(errorStr).toLowerCase()

	if (
		err.includes('not available') ||
		err.includes('out of stock') ||
		err.includes('insufficient') ||
		err.includes('reserved for another') ||
		err.includes('already been sold') ||
		err.includes('serial no')
	) {
		return 'Stock Availability Conflict: One or more selected jewelry items (or exact serial numbers) are no longer in stock at this store. Another register or cashier sold them while you were offline, or the inventory status changed on the server. You must cancel this order or modify the items to resolve this.'
	}
	if (
		err.includes('csrf') ||
		err.includes('session expired') ||
		err.includes('login') ||
		err.includes('not permitted') ||
		err.includes('guest') ||
		err.includes('authenticated') ||
		err.includes('verification failed')
	) {
		return 'Security Session Timeout: Your register security token has expired. Your credentials are no longer valid on the server. Please close this modal, refresh your web browser to re-login, and then trigger the sync cycle again.'
	}
	if (
		err.includes('failed to fetch') ||
		err.includes('network') ||
		err.includes('timeout') ||
		err.includes('dns') ||
		err.includes('502') ||
		err.includes('503') ||
		err.includes('504')
	) {
		return 'Network Timeout: The transaction could not be transmitted to the server because the connection was lost or timed out. Make sure your local internet connection is active. It will automatically try syncing again shortly.'
	}
	if (
		err.includes('duplicate') ||
		err.includes('already exists') ||
		err.includes('primary key') ||
		err.includes('integrity')
	) {
		return 'Duplicate Synced Entry: This transaction appears to have already been synced and processed successfully on the server. It is safe to discard this duplicate log entry.'
	}
	if (
		err.includes('tax') ||
		err.includes('pricing') ||
		err.includes('rate') ||
		err.includes('rounding')
	) {
		return 'Pricing / Tax System Mismatch: The tax profile or standard rates for one of the products on the server has changed since you generated this transaction offline. Please check pricing definitions.'
	}

	// Try extracting standard JSON message from Frappe if available
	try {
		const parsed = JSON.parse(errorStr)
		if (parsed.message) return parsed.message
		if (parsed._server_messages) {
			const msgs = JSON.parse(parsed._server_messages)
			if (msgs.length > 0) {
				const nested = JSON.parse(msgs[0])
				if (nested.message) return nested.message
			}
		}
	} catch (e) {
		// Ignore parsing failures
	}

	return `Validation Alert: ${errorStr}`
}

// Expander Helpers
function toggleExpand(id) {
	expandedItems.value[id] = !expandedItems.value[id]
}

function isExpanded(id) {
	return !!expandedItems.value[id]
}

// Sync Actions
async function triggerManualSync() {
	if (syncing.value || !offline.isOnline) return
	syncing.value = true
	try {
		await offline.syncPendingOrders(true)
		await loadData()
	} finally {
		syncing.value = false
	}
}

async function retryItem(id) {
	syncing.value = true
	try {
		await offline.retryOrder(id)
		await loadData()
	} finally {
		syncing.value = false
	}
}

async function deleteItem(id) {
	if (
		confirm(
			'Are you sure you want to discard this transaction? It will be deleted from your offline queue permanently.'
		)
	) {
		await offline.deleteOrder(id)
		await loadData()
	}
}

function retryConflictModified(item) {
	alert(
		'To modify and resolve this conflict, please recall the item or checkout modified quantities.'
	)
}
</script>
