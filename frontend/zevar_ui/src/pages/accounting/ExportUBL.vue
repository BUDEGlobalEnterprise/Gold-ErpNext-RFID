<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Export UBL</h2>
				</div>
				<div class="flex items-center gap-2">
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': loading }"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
						</svg>
					</button>
					<button
						@click="exportSelected"
						class="flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
						:disabled="!selectedInvoices.length"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
						</svg>
						Export {{ selectedInvoices.length || '' }} Selected
					</button>
				</div>
			</div>

			<div class="flex flex-wrap gap-2 mb-4 flex-shrink-0">
				<button
					v-for="tab in typeFilters"
					:key="tab.value"
					@click="
						activeType = tab.value;
						loadData();
					"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						activeType === tab.value
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-warm-dark-600'
					"
				>
					{{ tab.label }}
				</button>
			</div>

			<div class="grid grid-cols-2 lg:grid-cols-3 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Available</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ invoices.length }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Selected</div>
					<div class="text-2xl font-bold text-[#D4AF37]">{{ selectedInvoices.length }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Value</div>
					<div class="text-2xl font-bold text-emerald-500">{{ formatCurrency(totalValue) }}</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="loading && !invoices.length" class="flex items-center justify-center py-20">
					<div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div>
				</div>
				<div v-else-if="!invoices.length" class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500">
					<svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
					</svg>
					<p class="text-sm font-medium">No exportable invoices found</p>
				</div>
				<div v-else class="space-y-2">
					<div
						class="premium-card !p-3 flex items-center gap-3 mb-1"
					>
						<input
							type="checkbox"
							:checked="allSelected"
							@change="toggleAll"
							class="w-4 h-4 rounded border-gray-300 text-[#D4AF37] focus:ring-[#D4AF37]"
						/>
						<span class="text-xs font-bold text-gray-500 dark:text-gray-400">Select All</span>
					</div>
					<div
						v-for="inv in invoices"
						:key="inv.name"
						class="premium-card !p-4 flex items-center gap-3 hover:ring-1 hover:ring-[#D4AF37]/30 transition"
						:class="{ 'ring-1 ring-[#D4AF37]/50': selectedInvoices.includes(inv.name) }"
						@click="toggleSelect(inv.name)"
					>
						<input
							type="checkbox"
							:checked="selectedInvoices.includes(inv.name)"
							class="w-4 h-4 rounded border-gray-300 text-[#D4AF37] focus:ring-[#D4AF37]"
							@click.stop
							@change="toggleSelect(inv.name)"
						/>
						<div class="flex-1 min-w-0">
							<div class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ inv.name }}</div>
							<div class="text-[11px] text-gray-500 dark:text-gray-400">{{ inv.party || '' }} &middot; {{ inv.posting_date }}</div>
						</div>
						<div class="text-right flex-shrink-0">
							<div class="text-sm font-bold text-gray-900 dark:text-white">{{ formatCurrency(inv.grand_total) }}</div>
							<div class="text-[10px] text-gray-400">{{ inv.currency }}</div>
						</div>
					</div>
				</div>
			</div>

			<div v-if="exportResult" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="exportResult = null">
				<div class="premium-card !p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
					<h3 class="premium-title !text-lg mb-4">Export Result ({{ exportResult.count }} invoices)</h3>
					<pre class="bg-gray-100 dark:bg-warm-dark-800 p-4 rounded-lg text-xs overflow-auto max-h-[60vh] text-gray-700 dark:text-gray-300">{{ JSON.stringify(exportResult.export_data, null, 2) }}</pre>
					<div class="flex gap-2 mt-4">
						<button @click="downloadJSON" class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-[#D4AF37] text-white hover:bg-[#C4A030]">Download JSON</button>
						<button @click="exportResult = null" class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300">Close</button>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import { useAccountingStore } from '../../stores/accounting'

const store = useAccountingStore()

const invoices = ref([])
const selectedInvoices = ref([])
const loading = ref(false)
const activeType = ref('sales')
const exportResult = ref(null)

const typeFilters = [
	{ label: 'Sales Invoices', value: 'sales' },
	{ label: 'Purchase Invoices', value: 'purchase' },
]

const allSelected = computed(() => invoices.value.length > 0 && invoices.value.every((i) => selectedInvoices.value.includes(i.name)))
const totalValue = computed(() => invoices.value.filter((i) => selectedInvoices.value.includes(i.name)).reduce((s, i) => s + (i.grand_total || 0), 0))

function formatCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

function toggleSelect(name) {
	const idx = selectedInvoices.value.indexOf(name)
	if (idx >= 0) selectedInvoices.value.splice(idx, 1)
	else selectedInvoices.value.push(name)
}

function toggleAll() {
	if (allSelected.value) {
		selectedInvoices.value = []
	} else {
		selectedInvoices.value = invoices.value.map((i) => i.name)
	}
}

async function loadData() {
	loading.value = true
	selectedInvoices.value = []
	try {
		const result = await store.loadExportableInvoices({ invoice_type: activeType.value })
		invoices.value = result?.invoices || []
	} finally {
		loading.value = false
	}
}

async function exportSelected() {
	if (!selectedInvoices.value.length) return
	const result = await store.exportUBL(JSON.stringify(selectedInvoices.value))
	exportResult.value = result
}

function downloadJSON() {
	if (!exportResult.value) return
	const blob = new Blob([JSON.stringify(exportResult.value.export_data, null, 2)], { type: 'application/json' })
	const url = URL.createObjectURL(blob)
	const a = document.createElement('a')
	a.href = url
	a.download = `ubl-export-${new Date().toISOString().slice(0, 10)}.json`
	a.click()
	URL.revokeObjectURL(url)
}

onMounted(() => {
	loadData()
})
</script>
