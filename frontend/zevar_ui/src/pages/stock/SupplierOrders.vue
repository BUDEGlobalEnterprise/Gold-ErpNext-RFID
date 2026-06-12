<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Supplier Orders</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ stock.supplierOrdersTotal }} Orders
					</span>
				</div>
				<div class="flex items-center gap-2">
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': stock.supplierOrdersResource.loading }"
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
						@click="showCreateModal = true"
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
						New Order
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

			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Orders
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ stock.supplierOrdersTotal }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Pending Receipt
					</div>
					<div class="text-2xl font-bold text-amber-500">{{ pendingCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Completed
					</div>
					<div class="text-2xl font-bold text-emerald-500">{{ completedCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Value
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ formatCurrency(totalValue) }}
					</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.supplierOrdersResource.loading && !stock.supplierOrders.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>

				<div
					v-else-if="filteredOrders.length === 0"
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
					<p class="text-sm font-bold">No supplier orders found</p>
					<p class="text-xs mt-1">Create your first purchase order</p>
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
									Order
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
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell"
								>
									Delivery
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
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell"
								>
									Received
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="order in filteredOrders"
								:key="order.name"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
								@click="viewOrder(order)"
							>
								<td class="px-4 py-3">
									<div class="font-bold text-gray-900 dark:text-white text-xs">
										{{ order.name }}
									</div>
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell"
								>
									{{ order.supplier_name || order.supplier }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ formatDate(order.transaction_date) }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell"
								>
									{{ formatDate(order.schedule_date) }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white"
								>
									{{ formatCurrency(order.grand_total) }}
								</td>
								<td class="px-4 py-3 text-center">
									<span
										class="text-[9px] font-bold px-2 py-1 rounded-full"
										:class="statusClass(order.status)"
										>{{ order.status }}</span
									>
								</td>
								<td class="px-4 py-3 text-center hidden md:table-cell">
									<div
										class="w-full bg-gray-200 dark:bg-warm-dark-900 rounded-full h-1.5"
									>
										<div
											class="bg-emerald-500 h-1.5 rounded-full transition-all"
											:style="{ width: (order.per_received || 0) + '%' }"
										></div>
									</div>
									<span class="text-[9px] text-gray-500 mt-0.5"
										>{{ Math.round(order.per_received || 0) }}%</span
									>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<div
				v-if="selectedOrder"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="selectedOrder = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">
							{{ selectedOrder.name }}
						</h3>
						<button
							@click="selectedOrder = null"
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
								{{ selectedOrder.supplier_name }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Status</span>
							<p
								class="text-sm font-bold"
								:class="statusClass(selectedOrder.status)"
							>
								{{ selectedOrder.status }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Date</span>
							<p class="text-sm text-gray-700 dark:text-gray-300">
								{{ formatDate(selectedOrder.transaction_date) }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Total</span>
							<p class="text-sm font-bold text-[#D4AF37]">
								{{ formatCurrency(selectedOrder.grand_total) }}
							</p>
						</div>
					</div>
					<div
						v-if="selectedOrder.items"
						class="border-t border-gray-200 dark:border-warm-border/50 pt-4"
					>
						<h4 class="text-xs font-bold text-gray-500 uppercase mb-2">Items</h4>
						<div
							v-for="item in selectedOrder.items"
							:key="item.item_code"
							class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
						>
							<div>
								<div class="text-xs font-bold text-gray-900 dark:text-white">
									{{ item.item_name }}
								</div>
								<div class="text-[10px] text-gray-500">{{ item.item_code }}</div>
							</div>
							<div class="text-right">
								<div class="text-xs font-bold text-gray-900 dark:text-white">
									{{ item.qty }} × {{ formatCurrency(item.rate) }}
								</div>
								<div class="text-[10px] text-gray-500">
									Rcvd: {{ item.received_qty || 0 }}
								</div>
							</div>
						</div>
					</div>
					<div
						v-if="selectedOrder.docstatus === 0"
						class="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50"
					>
						<button
							@click="handleSubmit"
							class="flex-1 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition"
						>
							Submit
						</button>
						<button
							@click="handleCancel"
							class="flex-1 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg text-xs font-bold hover:bg-red-100 transition"
						>
							Cancel
						</button>
					</div>
				</div>
			</div>

			<div
				v-if="showCreateModal"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="showCreateModal = false"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">
							New Purchase Order
						</h3>
						<button
							@click="showCreateModal = false"
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
							<label class="text-[10px] font-bold text-gray-500 uppercase"
								>Supplier</label
							>
							<input
								v-model="newOrder.supplier"
								type="text"
								placeholder="Enter supplier name"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase"
								>Expected Delivery</label
							>
							<input
								v-model="newOrder.schedule_date"
								type="date"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div>
							<div class="flex items-center justify-between mb-2">
								<label class="text-[10px] font-bold text-gray-500 uppercase"
									>Items</label
								>
								<button
									@click="addNewOrderItem"
									class="text-[10px] font-bold text-[#D4AF37] hover:underline"
								>
									+ Add Item
								</button>
							</div>
							<div
								v-for="(item, idx) in newOrder.items"
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
									@click="newOrder.items.splice(idx, 1)"
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
						:disabled="stock.createPOResource.loading"
						class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50"
					>
						{{ stock.createPOResource.loading ? 'Creating...' : 'Create Order' }}
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
const selectedOrder = ref(null)
const showCreateModal = ref(false)
const newOrder = ref({
	supplier: '',
	schedule_date: '',
	items: [{ item_code: '', qty: 1, rate: 0 }],
})

const statusFilters = [
	{ label: 'All', value: '' },
	{ label: 'Draft', value: 'Draft' },
	{ label: 'To Receive', value: 'To Receive and Bill' },
	{ label: 'To Bill', value: 'To Bill' },
	{ label: 'Completed', value: 'Completed' },
	{ label: 'Cancelled', value: 'Cancelled' },
]

const filteredOrders = computed(() => {
	if (!activeStatus.value) return stock.supplierOrders
	return stock.supplierOrders.filter((o) => o.status === activeStatus.value)
})

const pendingCount = computed(
	() =>
		stock.supplierOrders.filter((o) => ['Draft', 'To Receive and Bill'].includes(o.status))
			.length
)
const completedCount = computed(
	() => stock.supplierOrders.filter((o) => o.status === 'Completed').length
)
const totalValue = computed(() =>
	stock.supplierOrders.reduce((sum, o) => sum + (o.grand_total || 0), 0)
)

function loadData() {
	stock.loadSupplierOrders({ status: activeStatus.value || undefined })
}

function viewOrder(order) {
	stock.loadOrderDetail(order.name).then(() => {
		selectedOrder.value = stock.currentOrder
	})
}

async function handleSubmit() {
	if (!selectedOrder.value) return
	await stock.submitPO(selectedOrder.value.name)
	toast({ title: 'Order submitted', icon: 'check', intent: 'success' })
	selectedOrder.value = null
	loadData()
}

async function handleCancel() {
	if (!selectedOrder.value) return
	await stock.cancelPO(selectedOrder.value.name)
	toast({ title: 'Order cancelled', icon: 'check', intent: 'success' })
	selectedOrder.value = null
	loadData()
}

function addNewOrderItem() {
	newOrder.value.items.push({ item_code: '', qty: 1, rate: 0 })
}

async function handleCreate() {
	if (!newOrder.value.supplier) {
		toast({ title: 'Supplier is required', icon: 'alert-circle', intent: 'warning' })
		return
	}
	const validItems = newOrder.value.items.filter((i) => i.item_code)
	if (!validItems.length) {
		toast({ title: 'Add at least one item', icon: 'alert-circle', intent: 'warning' })
		return
	}
	await stock.createPO(
		newOrder.value.supplier,
		JSON.stringify(validItems),
		null,
		newOrder.value.schedule_date
	)
	toast({ title: 'Purchase order created', icon: 'check', intent: 'success' })
	showCreateModal.value = false
	newOrder.value = {
		supplier: '',
		schedule_date: '',
		items: [{ item_code: '', qty: 1, rate: 0 }],
	}
	loadData()
}

function formatCurrency(val) {
	return (
		'$' +
		Number(val || 0).toLocaleString('en-US', {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2,
		})
	)
}

function formatDate(d) {
	if (!d) return '-'
	return new Date(d).toLocaleDateString('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
	})
}

function statusClass(status) {
	const map = {
		Draft: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300',
		'To Receive and Bill':
			'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
		'To Bill': 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
		Completed: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
		Cancelled: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
		Closed: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300',
	}
	return map[status] || 'bg-gray-100 text-gray-600'
}

onMounted(loadData)
</script>
