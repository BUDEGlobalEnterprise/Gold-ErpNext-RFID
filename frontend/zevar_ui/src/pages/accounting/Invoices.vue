<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Invoices</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ store.invoicesTotal }} Invoices
					</span>
				</div>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
					title="Refresh"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': store.invoicesResource.loading }"
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

			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ store.invoicesTotal }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Draft</div>
					<div class="text-2xl font-bold text-amber-500">{{ draftCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Unpaid</div>
					<div class="text-2xl font-bold text-red-500">{{ unpaidCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Value</div>
					<div class="text-2xl font-bold text-[#D4AF37]">{{ formatCurrency(totalValue) }}</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="store.invoicesResource.loading && !store.invoices.length" class="flex items-center justify-center py-20">
					<div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div>
				</div>
				<div v-else-if="!store.invoices.length" class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500">
					<svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
					</svg>
					<p class="text-sm font-medium">No invoices found</p>
				</div>
				<div v-else class="space-y-2">
					<div
						v-for="inv in store.invoices"
						:key="inv.name"
						class="premium-card !p-4 flex items-center justify-between cursor-pointer hover:ring-1 hover:ring-[#D4AF37]/30 transition"
						@click="viewInvoice(inv)"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div
								class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
								:class="inv.invoice_type === 'Sales' ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-purple-100 dark:bg-purple-900/30'"
							>
								<span class="text-[10px] font-bold" :class="inv.invoice_type === 'Sales' ? 'text-blue-600' : 'text-purple-600'">
									{{ inv.invoice_type === 'Sales' ? 'SI' : 'PI' }}
								</span>
							</div>
							<div class="min-w-0">
								<div class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ inv.name }}</div>
								<div class="text-[11px] text-gray-500 dark:text-gray-400 truncate">
									{{ inv.customer_name }}
									<span v-if="inv.due_date"> &middot; Due: {{ inv.due_date }}</span>
								</div>
							</div>
						</div>
						<div class="text-right flex-shrink-0 ml-3">
							<div class="text-sm font-bold text-gray-900 dark:text-white">{{ formatCurrency(inv.grand_total) }}</div>
							<div v-if="inv.outstanding_amount > 0" class="text-[10px] text-red-500">
								{{ formatCurrency(inv.outstanding_amount) }} outstanding
							</div>
							<span
								class="inline-block mt-1 px-2 py-0.5 rounded-full text-[9px] font-bold"
								:class="invoiceStatusClass(inv)"
							>
								{{ inv.status || (inv.docstatus === 0 ? 'Draft' : 'Submitted') }}
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
	{ label: 'Pending', value: 'pending' },
	{ label: 'Sales', value: 'sales' },
	{ label: 'Purchase', value: 'purchase' },
]

const draftCount = computed(() => store.invoices.filter((i) => i.docstatus === 0).length)
const unpaidCount = computed(() => store.invoices.filter((i) => i.outstanding_amount > 0).length)
const totalValue = computed(() => store.invoices.reduce((s, i) => s + (i.grand_total || 0), 0))

function formatCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

function invoiceStatusClass(inv) {
	const s = inv.status || ''
	if (inv.docstatus === 0) return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
	if (s === 'Paid') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
	if (s === 'Unpaid' || s === 'Overdue') return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
	if (s === 'Return') return 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
	return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
}

function loadData() {
	store.loadInvoices({ invoice_type: activeTab.value })
}

function viewInvoice(inv) {
	const doctype = inv.invoice_type === 'Sales' ? 'sales-invoice' : 'purchase-invoice'
	window.open(`/app/${doctype}/${inv.name}`, '_blank')
}

watch(activeTab, loadData)

onMounted(() => {
	loadData()
})
</script>
