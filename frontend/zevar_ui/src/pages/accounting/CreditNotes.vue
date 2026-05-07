<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Credit Notes</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ store.creditNotesTotal }} Notes
					</span>
				</div>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
					title="Refresh"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': store.creditNotesResource.loading }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
					</svg>
				</button>
			</div>

			<div class="flex flex-wrap gap-2 mb-4 flex-shrink-0">
				<button
					v-for="tab in tabs"
					:key="tab.value"
					@click="activeTab = tab.value"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						activeTab === tab.value
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-warm-dark-600'
					"
				>
					{{ tab.label }}
				</button>
			</div>

			<div class="grid grid-cols-2 lg:grid-cols-3 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Notes</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ store.creditNotesTotal }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Incoming</div>
					<div class="text-2xl font-bold text-purple-500">{{ incomingCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Outgoing</div>
					<div class="text-2xl font-bold text-blue-500">{{ outgoingCount }}</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="store.creditNotesResource.loading && !store.creditNotes.length" class="flex items-center justify-center py-20">
					<div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div>
				</div>
				<div v-else-if="!store.creditNotes.length" class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500">
					<svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
					</svg>
					<p class="text-sm font-medium">No credit notes found</p>
				</div>
				<div v-else class="space-y-2">
					<div
						v-for="cn in store.creditNotes"
						:key="cn.name"
						class="premium-card !p-4 flex items-center justify-between cursor-pointer hover:ring-1 hover:ring-[#D4AF37]/30 transition"
						@click="viewNote(cn)"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div
								class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
								:class="cn.note_type === 'Incoming' ? 'bg-purple-100 dark:bg-purple-900/30' : 'bg-blue-100 dark:bg-blue-900/30'"
							>
								<svg class="w-4 h-4" :class="cn.note_type === 'Incoming' ? 'text-purple-600' : 'text-blue-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
								</svg>
							</div>
							<div class="min-w-0">
								<div class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ cn.name }}</div>
								<div class="text-[11px] text-gray-500 dark:text-gray-400 truncate">
									{{ cn.party_name || cn.party }}
									<span v-if="cn.return_against"> &middot; Ref: {{ cn.return_against }}</span>
								</div>
							</div>
						</div>
						<div class="text-right flex-shrink-0 ml-3">
							<div class="text-sm font-bold text-red-500">-{{ formatCurrency(cn.grand_total) }}</div>
							<div class="text-[10px] text-gray-400">{{ cn.posting_date }}</div>
							<span
								class="inline-block mt-1 px-2 py-0.5 rounded-full text-[9px] font-bold"
								:class="noteStatusClass(cn)"
							>
								{{ cn.note_type }}
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import { useAccountingStore } from '../../stores/accounting'

const store = useAccountingStore()

const activeTab = ref('all')

const tabs = [
	{ label: 'All', value: 'all' },
	{ label: 'Incoming', value: 'incoming' },
	{ label: 'Outgoing', value: 'outgoing' },
]

const incomingCount = computed(() => store.creditNotes.filter((c) => c.note_type === 'Incoming').length)
const outgoingCount = computed(() => store.creditNotes.filter((c) => c.note_type === 'Outgoing').length)

function formatCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

function noteStatusClass(cn) {
	if (cn.docstatus === 0) return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
	if (cn.note_type === 'Incoming') return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
	return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
}

function loadData() {
	store.loadCreditNotes({ note_type: activeTab.value })
}

function viewNote(cn) {
	const doctype = cn.note_type === 'Incoming' ? 'purchase-invoice' : 'sales-invoice'
	window.open(`/app/${doctype}/${cn.name}`, '_blank')
}

watch(activeTab, loadData)

onMounted(() => {
	loadData()
})
</script>
