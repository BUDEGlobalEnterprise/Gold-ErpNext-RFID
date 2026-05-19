<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Quotes</h2>
					<span class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border">{{ store.quotesTotal }} Quotes</span>
				</div>
				<div class="flex items-center gap-2">
					<button @click="loadData" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700" title="Refresh">
						<svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': store.quotesResource.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" /></svg>
					</button>
					<button @click="showCreate = true" class="flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
						New Quote
					</button>
				</div>
			</div>

			<!-- Status Filter Pills -->
			<div class="flex flex-wrap gap-2 mb-4 flex-shrink-0">
<<<<<<< Updated upstream
				<button v-for="s in statusFilters" :key="s.value" @click="activeStatus = s.value; loadData()" class="px-3 py-1.5 rounded-full text-xs font-bold transition" :class="activeStatus === s.value ? 'bg-[#D4AF37] text-white' : 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-warm-dark-600'">
=======
				<button
					v-for="s in statusFilters"
					:key="s.value"
					@click="
						activeStatus = s.value;
						loadData();
					"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						activeStatus === s.value
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-warm-dark-600'
					"
				>
>>>>>>> Stashed changes
					{{ s.label }}
				</button>
			</div>

			<!-- KPI Cards -->
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4"><div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Quotes</div><div class="text-2xl font-bold text-gray-900 dark:text-white">{{ store.quotesTotal }}</div></div>
				<div class="premium-card !p-4"><div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Open / Draft</div><div class="text-2xl font-bold text-amber-500">{{ openCount }}</div></div>
				<div class="premium-card !p-4"><div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Ordered</div><div class="text-2xl font-bold text-emerald-500">{{ orderedCount }}</div></div>
				<div class="premium-card !p-4"><div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Value</div><div class="text-2xl font-bold text-[#D4AF37]">{{ formatCurrency(totalValue) }}</div></div>
			</div>

			<!-- Data Table -->
			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="store.quotesResource.loading && !store.quotes.length" class="flex items-center justify-center py-20"><div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div></div>
				<div v-else-if="!store.quotes.length" class="flex flex-col items-center justify-center py-20 text-gray-400">
					<svg class="w-16 h-16 mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
					<p class="text-sm font-bold">No quotations found</p>
					<p class="text-xs mt-1">Create your first quote</p>
				</div>
				<div v-else class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead><tr class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50">
							<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Quote</th>
							<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden sm:table-cell">Customer</th>
							<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell">Date</th>
							<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell">Valid Till</th>
							<th class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Amount</th>
							<th class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Status</th>
						</tr></thead>
						<tbody>
							<tr v-for="q in store.quotes" :key="q.name" class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer" @click="viewQuote(q)">
								<td class="px-4 py-3"><div class="font-bold text-gray-900 dark:text-white text-xs">{{ q.name }}</div></td>
								<td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell">{{ q.customer_name || q.party_name }}</td>
								<td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell">{{ formatDate(q.transaction_date) }}</td>
								<td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell">{{ formatDate(q.valid_till) }}</td>
								<td class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white">{{ formatCurrency(q.grand_total) }}</td>
								<td class="px-4 py-3 text-center"><span class="text-[9px] font-bold px-2 py-1 rounded-full" :class="statusClass(q.status)">{{ q.status }}</span></td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Detail Modal -->
			<div v-if="selected" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="selected = null">
				<div class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ selected.name }}</h3>
						<button @click="selected = null" class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"><svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg></button>
					</div>
					<div class="grid grid-cols-2 gap-3 mb-4">
						<div><span class="text-[10px] text-gray-500 uppercase">Customer</span><p class="text-sm font-bold text-gray-900 dark:text-white">{{ selected.customer_name }}</p></div>
						<div><span class="text-[10px] text-gray-500 uppercase">Status</span><p class="text-sm font-bold"><span :class="statusClass(selected.status)" class="px-2 py-0.5 rounded-full text-[10px]">{{ selected.status }}</span></p></div>
						<div><span class="text-[10px] text-gray-500 uppercase">Date</span><p class="text-sm text-gray-700 dark:text-gray-300">{{ formatDate(selected.transaction_date) }}</p></div>
						<div><span class="text-[10px] text-gray-500 uppercase">Total</span><p class="text-sm font-bold text-[#D4AF37]">{{ formatCurrency(selected.grand_total) }}</p></div>
					</div>
					<div v-if="selected.items" class="border-t border-gray-200 dark:border-warm-border/50 pt-4">
						<h4 class="text-xs font-bold text-gray-500 uppercase mb-2">Items</h4>
						<div v-for="item in selected.items" :key="item.item_code" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0">
							<div><div class="text-xs font-bold text-gray-900 dark:text-white">{{ item.item_name }}</div><div class="text-[10px] text-gray-500">{{ item.item_code }}</div></div>
							<div class="text-right"><div class="text-xs font-bold text-gray-900 dark:text-white">{{ item.qty }} × {{ formatCurrency(item.rate) }}</div><div class="text-[10px] text-[#D4AF37]">{{ formatCurrency(item.amount) }}</div></div>
						</div>
					</div>
					<!-- Actions -->
					<div class="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50">
						<button v-if="selected.docstatus === 0" @click="handleSubmit" class="flex-1 min-w-[120px] py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition">Submit</button>
						<button v-if="selected.docstatus === 1 && selected.status !== 'Ordered'" @click="handleConvertOrder" :disabled="store.convertToOrderResource.loading" class="flex-1 min-w-[120px] py-2 bg-blue-600 text-white rounded-lg text-xs font-bold hover:bg-blue-700 transition disabled:opacity-50">
							{{ store.convertToOrderResource.loading ? '...' : '→ Sales Order' }}
						</button>
						<button v-if="selected.docstatus === 1 && selected.status !== 'Ordered'" @click="handleConvertInvoice" :disabled="store.convertToInvoiceResource.loading" class="flex-1 min-w-[120px] py-2 bg-purple-600 text-white rounded-lg text-xs font-bold hover:bg-purple-700 transition disabled:opacity-50">
							{{ store.convertToInvoiceResource.loading ? '...' : '→ Invoice' }}
						</button>
						<button v-if="selected.docstatus === 1 && selected.status === 'Open'" @click="handleMarkLost" class="flex-1 min-w-[120px] py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg text-xs font-bold hover:bg-red-100 transition">Mark Lost</button>
					</div>
				</div>
			</div>

			<!-- Create Modal -->
			<div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="showCreate = false">
				<div class="premium-card !rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto m-4">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">New Quotation</h3>
						<button @click="showCreate = false" class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"><svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg></button>
					</div>
					<div class="space-y-3">
						<div><label class="text-[10px] font-bold text-gray-500 uppercase">Customer</label><input v-model="form.customer" type="text" placeholder="Customer name" class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37]" /></div>
						<div><label class="text-[10px] font-bold text-gray-500 uppercase">Valid Until</label><input v-model="form.valid_till" type="date" class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37]" /></div>
						<div>
							<div class="flex items-center justify-between mb-2"><label class="text-[10px] font-bold text-gray-500 uppercase">Items</label><button @click="form.items.push({ item_code: '', qty: 1, rate: 0 })" class="text-[10px] font-bold text-[#D4AF37]">+ Add</button></div>
							<div v-for="(item, idx) in form.items" :key="idx" class="flex gap-2 mb-2">
								<input v-model="item.item_code" placeholder="Item Code" class="flex-1 px-2 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded text-xs outline-none text-gray-900 dark:text-white" />
								<input v-model.number="item.qty" type="number" min="1" class="w-16 px-2 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded text-xs outline-none text-gray-900 dark:text-white" />
								<input v-model.number="item.rate" type="number" min="0" placeholder="Rate" class="w-20 px-2 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded text-xs outline-none text-gray-900 dark:text-white" />
								<button @click="form.items.splice(idx, 1)" class="p-1 text-red-400 hover:text-red-600"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg></button>
							</div>
						</div>
					</div>
					<button @click="handleCreate" :disabled="store.createQuoteResource.loading" class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50">
						{{ store.createQuoteResource.loading ? 'Creating...' : 'Create Quotation' }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import { useQuotesStore } from '@/stores/quotes.js'

const store = useQuotesStore()
const activeStatus = ref('')
const selected = ref(null)
const showCreate = ref(false)
const form = ref({ customer: '', valid_till: '', items: [{ item_code: '', qty: 1, rate: 0 }] })

const statusFilters = [
	{ label: 'All', value: '' },
	{ label: 'Draft', value: 'Draft' },
	{ label: 'Open', value: 'Open' },
	{ label: 'Ordered', value: 'Ordered' },
	{ label: 'Lost', value: 'Lost' },
]

const openCount = computed(() => store.quotes.filter((q) => ['Draft', 'Open'].includes(q.status)).length)
const orderedCount = computed(() => store.quotes.filter((q) => q.status === 'Ordered').length)
const totalValue = computed(() => store.quotes.reduce((s, q) => s + (q.grand_total || 0), 0))

function loadData() { store.loadQuotes({ status: activeStatus.value || undefined }) }

function viewQuote(q) {
	store.loadQuoteDetail(q.name).then(() => { selected.value = store.currentQuote })
}

async function handleSubmit() {
	if (!selected.value) return
	await store.submitQuote(selected.value.name)
	toast({ title: 'Quotation submitted', icon: 'check', intent: 'success' })
	selected.value = null
	loadData()
}

async function handleConvertOrder() {
	if (!selected.value) return
	const res = await store.convertToOrder(selected.value.name)
	toast({ title: res.data?.message || 'Sales Order created', icon: 'check', intent: 'success' })
	selected.value = null
	loadData()
}

async function handleConvertInvoice() {
	if (!selected.value) return
	const res = await store.convertToInvoice(selected.value.name)
	toast({ title: res.data?.message || 'Invoice created', icon: 'check', intent: 'success' })
	selected.value = null
	loadData()
}

async function handleMarkLost() {
	if (!selected.value) return
	await store.updateStatus(selected.value.name, 'Lost')
	toast({ title: 'Marked as Lost', icon: 'check', intent: 'success' })
	selected.value = null
	loadData()
}

async function handleCreate() {
	if (!form.value.customer) { toast({ title: 'Customer required', icon: 'alert-circle', intent: 'warning' }); return }
	const validItems = form.value.items.filter((i) => i.item_code)
	if (!validItems.length) { toast({ title: 'Add items', icon: 'alert-circle', intent: 'warning' }); return }
	await store.createQuote(form.value.customer, JSON.stringify(validItems), form.value.valid_till)
	toast({ title: 'Quotation created', icon: 'check', intent: 'success' })
	showCreate.value = false
	form.value = { customer: '', valid_till: '', items: [{ item_code: '', qty: 1, rate: 0 }] }
	loadData()
}

function formatCurrency(val) { return '$' + Number(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
function formatDate(d) { if (!d) return '-'; return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }
function statusClass(status) {
	const map = {
		Draft: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300',
		Open: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
		Replied: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-400',
		Ordered: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
		Lost: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
		Cancelled: 'bg-gray-100 dark:bg-gray-800 text-gray-500',
		Expired: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
	}
	return map[status] || 'bg-gray-100 text-gray-600'
}

onMounted(loadData)
</script>
