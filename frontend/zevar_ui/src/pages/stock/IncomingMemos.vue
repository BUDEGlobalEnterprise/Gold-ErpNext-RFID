<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Incoming Memos</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.memosTotal }} Memos</span
					>
				</div>
				<div class="flex items-center gap-2">
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': stock.memosResource.loading }"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15"
							/>
						</svg>
					</button>
					<button
						@click="openCreate"
						class="flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						New Memo
					</button>
				</div>
			</div>

			<div class="flex flex-wrap gap-2 mb-4 flex-shrink-0">
				<button
					v-for="s in statusFilters"
					:key="s.value"
					@click="activeStatus = s.value"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						activeStatus === s.value
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-warm-dark-600'
					"
				>
					{{ s.label }}
				</button>
			</div>

			<div class="grid grid-cols-3 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Total
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ stock.memosTotal }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Draft
					</div>
					<div class="text-2xl font-bold text-amber-500">
						{{ stock.memos.filter((m) => m.docstatus === 0).length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Received
					</div>
					<div class="text-2xl font-bold text-emerald-500">
						{{ stock.memos.filter((m) => m.docstatus === 1).length }}
					</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.memosResource.loading && !stock.memos.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!filteredMemos.length"
					class="flex flex-col items-center justify-center py-20 text-gray-400"
				>
					<svg
						class="w-16 h-16 mb-4 opacity-30"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1"
							d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						/>
					</svg>
					<p class="text-sm font-bold">No memos found</p>
					<p class="text-xs mt-1">Create a new memo to receive supplier goods</p>
				</div>
				<div v-else class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead>
							<tr
								class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50"
							>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Memo
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden sm:table-cell"
								>
									Supplier
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell"
								>
									Date
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Amount
								</th>
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Status
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="m in filteredMemos"
								:key="m.name"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
								@click="viewMemo(m)"
							>
								<td
									class="px-4 py-3 text-xs font-bold text-gray-900 dark:text-white"
								>
									{{ m.name }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell"
								>
									{{ m.supplier_name || m.supplier }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ m.posting_date }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white"
								>
									${{ Number(m.grand_total || 0).toFixed(2) }}
								</td>
								<td class="px-4 py-3 text-center">
									<span
										class="text-[9px] font-bold px-2 py-1 rounded-full"
										:class="statusClass(m)"
									>
										{{ m.docstatus === 1 ? 'Received' : 'Draft' }}
									</span>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Detail / View Modal -->
			<div
				v-if="selectedMemo"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="selectedMemo = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">
							{{ selectedMemo.name }}
						</h3>
						<button
							@click="selectedMemo = null"
							class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"
						>
							<svg
								class="w-5 h-5 text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
					<div class="grid grid-cols-2 gap-3 mb-4">
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Supplier</span>
							<p class="text-sm font-bold text-gray-900 dark:text-white">
								{{ selectedMemo.supplier_name || selectedMemo.supplier }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Status</span>
							<p class="text-sm font-bold">
								<span
									class="text-[9px] font-bold px-2 py-1 rounded-full"
									:class="statusClass(selectedMemo)"
								>
									{{ selectedMemo.docstatus === 1 ? 'Received' : 'Draft' }}
								</span>
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Date</span>
							<p class="text-sm text-gray-700 dark:text-gray-300">
								{{ selectedMemo.posting_date }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Total</span>
							<p class="text-sm font-bold text-[#D4AF37]">
								${{ Number(selectedMemo.grand_total || 0).toFixed(2) }}
							</p>
						</div>
					</div>
					<div
						v-if="selectedMemo.docstatus === 0"
						class="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50"
					>
						<button
							@click="handleReceive"
							class="flex-1 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition"
						>
							Receive
						</button>
					</div>
				</div>
			</div>

			<!-- Create Modal -->
			<div
				v-if="showCreate"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="showCreate = false"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">New Memo</h3>
						<button
							@click="showCreate = false"
							class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"
						>
							<svg
								class="w-5 h-5 text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
					<div class="space-y-3">
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Supplier</label>
							<input
								v-model="newMemo.supplier"
								type="text"
								placeholder="Enter supplier name"
								list="memo-supplier-suggestions"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
							<datalist id="memo-supplier-suggestions">
								<option v-for="s in stock.suppliers" :key="s.name" :value="s.name">
									{{ s.supplier_name }}
								</option>
							</datalist>
						</div>
						<div>
							<div class="flex items-center justify-between mb-2">
								<label class="text-[10px] font-bold text-gray-500 uppercase">Items</label>
								<button
									@click="addMemoItem"
									class="text-[10px] font-bold text-[#D4AF37] hover:underline"
								>
									+ Add Item
								</button>
							</div>
							<div
								v-for="(item, idx) in newMemo.items"
								:key="idx"
								class="flex gap-2 mb-2"
							>
								<input
									v-model="item.item_code"
									placeholder="Item Code"
									class="flex-1 px-2 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded text-xs text-gray-900 dark:text-white outline-none"
								/>
								<input
									v-model.number="item.qty"
									type="number"
									min="1"
									placeholder="Qty"
									class="w-16 px-2 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded text-xs text-gray-900 dark:text-white outline-none"
								/>
								<input
									v-model.number="item.rate"
									type="number"
									min="0"
									placeholder="Rate"
									class="w-20 px-2 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded text-xs text-gray-900 dark:text-white outline-none"
								/>
								<button
									@click="newMemo.items.splice(idx, 1)"
									class="p-1 text-red-400 hover:text-red-600"
								>
									<svg
										class="w-4 h-4"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
										/>
									</svg>
								</button>
							</div>
						</div>
					</div>
					<button
						@click="handleCreate"
						:disabled="stock.createMemoResource.loading"
						class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50"
					>
						{{ stock.createMemoResource.loading ? 'Creating...' : 'Create Memo' }}
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
import { useStockStore } from '@/stores/stock.js'

const stock = useStockStore()
const activeStatus = ref('')
const selectedMemo = ref(null)
const showCreate = ref(false)
const newMemo = ref({ supplier: '', items: [{ item_code: '', qty: 1, rate: 0 }] })

const statusFilters = [
	{ label: 'All', value: '' },
	{ label: 'Draft', value: 'Draft' },
	{ label: 'Received', value: 'Received' },
]

const filteredMemos = computed(() => {
	if (!activeStatus.value) return stock.memos
	if (activeStatus.value === 'Draft')
		return stock.memos.filter((m) => m.docstatus === 0)
	if (activeStatus.value === 'Received')
		return stock.memos.filter((m) => m.docstatus === 1)
	return stock.memos
})

function statusClass(m) {
	return m.docstatus === 1
		? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
		: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
}

function loadData() {
	stock.loadMemos({ status: activeStatus.value === 'Received' ? 'Completed' : activeStatus.value || undefined })
	if (!stock.suppliers.length) stock.loadSuppliers()
}

function viewMemo(m) {
	selectedMemo.value = m
}

async function handleReceive() {
	if (!selectedMemo.value) return
	await stock.receiveMemo(selectedMemo.value.name)
	toast({ title: 'Memo received', icon: 'check', intent: 'success' })
	selectedMemo.value = null
	loadData()
}

function addMemoItem() {
	newMemo.value.items.push({ item_code: '', qty: 1, rate: 0 })
}

function openCreate() {
	newMemo.value = { supplier: '', items: [{ item_code: '', qty: 1, rate: 0 }] }
	showCreate.value = true
}

async function handleCreate() {
	if (!newMemo.value.supplier) {
		toast({ title: 'Supplier is required', icon: 'alert-circle', intent: 'warning' })
		return
	}
	const validItems = newMemo.value.items.filter((i) => i.item_code)
	if (!validItems.length) {
		toast({ title: 'Add at least one item', icon: 'alert-circle', intent: 'warning' })
		return
	}
	await stock.createMemo(newMemo.value.supplier, JSON.stringify(validItems), null)
	toast({ title: 'Memo created', icon: 'check', intent: 'success' })
	showCreate.value = false
	loadData()
}

onMounted(loadData)
</script>
