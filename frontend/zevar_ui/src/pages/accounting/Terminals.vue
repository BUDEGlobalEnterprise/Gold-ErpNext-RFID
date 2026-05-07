<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Terminals</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ store.terminalsTotal }} Terminals
					</span>
				</div>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
					title="Refresh"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': store.terminalsResource.loading }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
					</svg>
				</button>
			</div>

			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ store.terminalsTotal }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Open</div>
					<div class="text-2xl font-bold text-emerald-500">{{ openCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Closed</div>
					<div class="text-2xl font-bold text-gray-400">{{ closedCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Today's Revenue</div>
					<div class="text-2xl font-bold text-[#D4AF37]">{{ formatCurrency(todayRevenue) }}</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="store.terminalsResource.loading && !store.terminals.length" class="flex items-center justify-center py-20">
					<div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div>
				</div>
				<div v-else-if="!store.terminals.length" class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500">
					<svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
					</svg>
					<p class="text-sm font-medium">No terminals found</p>
				</div>
				<div v-else class="space-y-3">
					<div
						v-for="t in store.terminals"
						:key="t.name"
						class="premium-card !p-5 cursor-pointer hover:ring-1 hover:ring-[#D4AF37]/30 transition"
						@click="viewTerminal(t)"
					>
						<div class="flex items-center justify-between mb-3">
							<div class="flex items-center gap-3">
								<div
									class="w-10 h-10 rounded-lg flex items-center justify-center"
									:class="t.status === 'Open' ? 'bg-emerald-100 dark:bg-emerald-900/30' : 'bg-gray-100 dark:bg-gray-800'"
								>
									<svg class="w-5 h-5" :class="t.status === 'Open' ? 'text-emerald-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
									</svg>
								</div>
								<div>
									<div class="text-sm font-bold text-gray-900 dark:text-white">{{ t.name }}</div>
									<div class="text-[11px] text-gray-500 dark:text-gray-400">{{ t.warehouse || 'No warehouse' }}</div>
								</div>
							</div>
							<span
								class="px-3 py-1 rounded-full text-[10px] font-bold"
								:class="t.status === 'Open' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'"
							>
								{{ t.status }}
							</span>
						</div>
						<div class="grid grid-cols-3 gap-3 text-center">
							<div>
								<div class="text-[10px] text-gray-400 uppercase font-bold">Cashier</div>
								<div class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">{{ t.current_user || '—' }}</div>
							</div>
							<div>
								<div class="text-[10px] text-gray-400 uppercase font-bold">Invoices</div>
								<div class="text-xs font-medium text-gray-700 dark:text-gray-300">{{ t.today_invoices }}</div>
							</div>
							<div>
								<div class="text-[10px] text-gray-400 uppercase font-bold">Revenue</div>
								<div class="text-xs font-bold text-[#D4AF37]">{{ formatCurrency(t.today_total) }}</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import { useAccountingStore } from '../../stores/accounting'

const store = useAccountingStore()

const openCount = computed(() => store.terminals.filter((t) => t.status === 'Open').length)
const closedCount = computed(() => store.terminals.filter((t) => t.status === 'Closed').length)
const todayRevenue = computed(() => store.terminals.reduce((s, t) => s + (t.today_total || 0), 0))

function formatCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

function loadData() {
	store.loadTerminals()
}

function viewTerminal(t) {
	window.open(`/app/pos-profile/${t.name}`, '_blank')
}

onMounted(() => {
	loadData()
})
</script>
