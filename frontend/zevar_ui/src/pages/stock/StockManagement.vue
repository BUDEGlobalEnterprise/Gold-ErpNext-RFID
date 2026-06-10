<template>
	<AppLayout>
		<div class="p-4 lg:p-6 max-w-5xl mx-auto">
			<!-- Header -->
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
						Stock Management
					</h1>
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
						Restock, adjust, and transfer inventory
					</p>
				</div>
			</div>

			<!-- Tab Selector -->
			<div class="flex gap-1 bg-gray-100 dark:bg-warm-dark-800 rounded-xl p-1 mb-6">
				<button
					v-for="tab in tabs"
					:key="tab.id"
					@click="activeTab = tab.id"
					class="flex-1 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all"
					:class="
						activeTab === tab.id
							? 'bg-white dark:bg-warm-dark-700 text-[#D4AF37] shadow-sm'
							: 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
					"
				>
					{{ tab.label }}
				</button>
			</div>

			<!-- Success Message -->
			<div
				v-if="successMsg"
				class="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/30 rounded-xl flex items-center gap-3"
			>
				<svg
					class="w-5 h-5 text-green-600 shrink-0"
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
				<span class="text-sm text-green-800 dark:text-green-200">{{ successMsg }}</span>
				<button
					@click="successMsg = ''"
					class="ml-auto text-green-600 hover:text-green-800"
				>
					✕
				</button>
			</div>

			<!-- Error Message -->
			<div
				v-if="errorMsg"
				class="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl flex items-center gap-3"
			>
				<svg
					class="w-5 h-5 text-red-600 shrink-0"
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
				<span class="text-sm text-red-800 dark:text-red-200">{{ errorMsg }}</span>
				<button @click="errorMsg = ''" class="ml-auto text-red-600 hover:text-red-800">
					✕
				</button>
			</div>

			<!-- ═══ ADD STOCK TAB ═══ -->
			<div
				v-if="activeTab === 'add'"
				class="bg-white dark:bg-warm-dark-800 rounded-2xl border border-gray-200 dark:border-warm-border/50 p-6"
			>
				<h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
					Add Stock / Restock
				</h2>

				<!-- Item Search -->
				<div class="mb-4">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Item *</label
					>
					<div class="relative">
						<input
							v-model="itemSearch"
							@input="searchItems"
							placeholder="Search by item code, name, vendor SKU, or barcode..."
							class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
						/>
						<div
							v-if="itemResults.length > 0 && showItemDropdown"
							class="absolute z-50 w-full mt-1 bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border/50 rounded-xl shadow-xl max-h-60 overflow-y-auto"
						>
							<button
								v-for="item in itemResults"
								:key="item.name"
								@click="selectItem(item)"
								class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
							>
								<div class="flex justify-between items-start">
									<div>
										<span
											class="font-medium text-sm text-gray-900 dark:text-white"
											>{{ item.item_name }}</span
										>
										<span class="text-xs text-gray-500 ml-2">{{
											item.name
										}}</span>
									</div>
									<span
										v-if="item.custom_vendor"
										class="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full"
										>{{ item.custom_vendor }}</span
									>
								</div>
								<div class="text-xs text-gray-400 mt-0.5">
									<span v-if="item.custom_vendor_sku"
										>SKU: {{ item.custom_vendor_sku }}</span
									>
									<span v-if="item.custom_barcode" class="ml-3"
										>Barcode: {{ item.custom_barcode }}</span
									>
									<span v-if="item.has_serial_no" class="ml-3 text-amber-600"
										>● Serial Tracked</span
									>
								</div>
							</button>
						</div>
					</div>
					<div
						v-if="selectedItem"
						class="mt-2 p-3 bg-[#D4AF37]/5 border border-[#D4AF37]/20 rounded-lg"
					>
						<div class="flex justify-between">
							<span class="font-medium text-sm">{{ selectedItem.item_name }}</span>
							<button
								@click="
									selectedItem = null
									itemSearch = ''
								"
								class="text-xs text-red-500 hover:text-red-700"
							>
								Clear
							</button>
						</div>
						<div class="text-xs text-gray-500 mt-1">
							{{ selectedItem.name }} • {{ selectedItem.item_group || 'No Group' }}
							<span v-if="selectedItem.custom_vendor">
								• Vendor: {{ selectedItem.custom_vendor }}</span
							>
							<span v-if="selectedItem.custom_vendor_sku">
								• SKU: {{ selectedItem.custom_vendor_sku }}</span
							>
						</div>
					</div>
				</div>

				<!-- Warehouse -->
				<div class="mb-4">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Warehouse *</label
					>
					<select
						v-model="addForm.warehouse"
						class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
					>
						<option value="">Select warehouse...</option>
						<option v-for="wh in storeWarehouses" :key="wh" :value="wh">
							{{ wh }}
						</option>
					</select>
				</div>

				<div class="grid grid-cols-2 gap-4 mb-4">
					<!-- Quantity -->
					<div>
						<label
							class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>Quantity *</label
						>
						<input
							v-model.number="addForm.qty"
							type="number"
							min="1"
							class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
						/>
					</div>
					<!-- Valuation Rate -->
					<div>
						<label
							class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
							>Cost Price ($)</label
						>
						<input
							v-model.number="addForm.valuation_rate"
							type="number"
							step="0.01"
							placeholder="Optional"
							class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
						/>
					</div>
				</div>

				<!-- Serial No (if serial tracked) -->
				<div v-if="selectedItem?.has_serial_no" class="mb-4">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Serial Number(s)</label
					>
					<textarea
						v-model="addForm.serial_no"
						rows="3"
						placeholder="Enter serial numbers, one per line..."
						class="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none resize-none"
					></textarea>
					<p class="text-xs text-gray-400 mt-1">
						One serial number per line. Count must match quantity.
					</p>
				</div>

				<!-- Reason -->
				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Reason</label
					>
					<select
						v-model="addForm.reason"
						class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
					>
						<option value="Vendor Restock">Vendor Restock</option>
						<option value="Return to Stock">Return to Stock</option>
						<option value="Found Item">Found Item</option>
						<option value="Inventory Correction">Inventory Correction</option>
						<option value="Transfer In">Transfer In</option>
					</select>
				</div>

				<button
					@click="submitAddStock"
					:disabled="processing || !canSubmitAdd"
					class="w-full h-12 rounded-xl font-bold text-sm transition-all"
					:class="
						canSubmitAdd && !processing
							? 'bg-[#D4AF37] text-black hover:bg-[#b5952f]'
							: 'bg-gray-200 dark:bg-warm-dark-700 text-gray-400 cursor-not-allowed'
					"
				>
					{{ processing ? 'Processing...' : 'Add Stock' }}
				</button>
			</div>

			<!-- ═══ REMOVE / ADJUST TAB ═══ -->
			<div
				v-if="activeTab === 'remove'"
				class="bg-white dark:bg-warm-dark-800 rounded-2xl border border-gray-200 dark:border-warm-border/50 p-6"
			>
				<h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Remove Stock</h2>

				<div class="mb-4">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Serial Number *</label
					>
					<input
						v-model="removeForm.serial_no"
						placeholder="Enter or scan serial number..."
						class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
					/>
				</div>

				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Reason *</label
					>
					<select
						v-model="removeForm.reason"
						class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
					>
						<option value="Damaged">Damaged</option>
						<option value="Lost">Lost</option>
						<option value="Vendor Return">Vendor Return</option>
						<option value="Inventory Correction">Inventory Correction</option>
						<option value="Stolen">Stolen</option>
					</select>
				</div>

				<button
					@click="submitRemoveStock"
					:disabled="processing || !removeForm.serial_no"
					class="w-full h-12 rounded-xl font-bold text-sm transition-all"
					:class="
						removeForm.serial_no && !processing
							? 'bg-red-600 text-white hover:bg-red-700'
							: 'bg-gray-200 dark:bg-warm-dark-700 text-gray-400 cursor-not-allowed'
					"
				>
					{{ processing ? 'Processing...' : 'Remove Stock' }}
				</button>
			</div>

			<!-- ═══ TRANSFER TAB ═══ -->
			<div
				v-if="activeTab === 'transfer'"
				class="bg-white dark:bg-warm-dark-800 rounded-2xl border border-gray-200 dark:border-warm-border/50 p-6"
			>
				<h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
					Transfer Between Stores
				</h2>

				<div class="mb-4">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Serial Number *</label
					>
					<input
						v-model="transferForm.serial_no"
						placeholder="Enter or scan serial number..."
						class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
					/>
				</div>

				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
						>Transfer To *</label
					>
					<select
						v-model="transferForm.target_warehouse"
						class="w-full h-11 px-4 rounded-xl border border-gray-200 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none"
					>
						<option value="">Select destination...</option>
						<option v-for="wh in storeWarehouses" :key="wh" :value="wh">
							{{ wh }}
						</option>
					</select>
				</div>

				<button
					@click="submitTransfer"
					:disabled="
						processing || !transferForm.serial_no || !transferForm.target_warehouse
					"
					class="w-full h-12 rounded-xl font-bold text-sm transition-all"
					:class="
						transferForm.serial_no && transferForm.target_warehouse && !processing
							? 'bg-blue-600 text-white hover:bg-blue-700'
							: 'bg-gray-200 dark:bg-warm-dark-700 text-gray-400 cursor-not-allowed'
					"
				>
					{{ processing ? 'Processing...' : 'Transfer' }}
				</button>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import { useSessionStore } from '@/stores/session.js'

const session = useSessionStore()

const activeTab = ref('add')
const tabs = [
	{ id: 'add', label: 'Add Stock' },
	{ id: 'remove', label: 'Remove' },
	{ id: 'transfer', label: 'Transfer' },
]

const processing = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

// Item search
const itemSearch = ref('')
const itemResults = ref([])
const selectedItem = ref(null)
const showItemDropdown = ref(false)
let searchTimeout = null

// Store warehouses
const storeWarehouses = ref([])

// Forms
const addForm = ref({
	warehouse: '',
	qty: 1,
	valuation_rate: null,
	serial_no: '',
	reason: 'Vendor Restock',
})
const removeForm = ref({ serial_no: '', reason: 'Damaged' })
const transferForm = ref({ serial_no: '', target_warehouse: '' })

const canSubmitAdd = computed(
	() => selectedItem.value && addForm.value.warehouse && addForm.value.qty > 0
)

onMounted(async () => {
	// Load warehouses
	try {
		const whs = await call('frappe.client.get_list', {
			doctype: 'Warehouse',
			filters: { is_group: 0, parent_warehouse: ['like', '%Zevar US Stores%'] },
			fields: ['name'],
			limit_page_length: 50,
		})
		storeWarehouses.value = whs.map((w) => w.name)
	} catch {
		/* fallback */
	}

	// Default warehouse from session
	if (session.currentWarehouse) {
		addForm.value.warehouse = session.currentWarehouse
	}
})

function searchItems() {
	showItemDropdown.value = true
	clearTimeout(searchTimeout)
	if (!itemSearch.value || itemSearch.value.length < 2) {
		itemResults.value = []
		return
	}
	searchTimeout = setTimeout(async () => {
		try {
			const results = await call('zevar_core.services.stock_reduction.ui_get_stock_items', {
				search: itemSearch.value,
				limit: 15,
			})
			itemResults.value = results || []
		} catch {
			itemResults.value = []
		}
	}, 300)
}

function selectItem(item) {
	selectedItem.value = item
	itemSearch.value = item.item_name
	showItemDropdown.value = false
	itemResults.value = []
}

async function submitAddStock() {
	if (!canSubmitAdd.value) return
	processing.value = true
	errorMsg.value = ''
	successMsg.value = ''
	try {
		const params = {
			item_code: selectedItem.value.name,
			warehouse: addForm.value.warehouse,
			qty: addForm.value.qty,
			reason: addForm.value.reason,
		}
		if (addForm.value.valuation_rate) params.valuation_rate = addForm.value.valuation_rate
		if (addForm.value.serial_no) params.serial_no = addForm.value.serial_no.trim()

		const result = await call('zevar_core.services.stock_reduction.ui_add_stock', params)
		successMsg.value = `Added ${addForm.value.qty} × ${selectedItem.value.item_name} to ${addForm.value.warehouse}. Entry: ${result.stock_entry}`
		// Reset
		selectedItem.value = null
		itemSearch.value = ''
		addForm.value.qty = 1
		addForm.value.valuation_rate = null
		addForm.value.serial_no = ''
	} catch (e) {
		errorMsg.value = e?.messages?.[0] || e?.message || 'Failed to add stock'
	} finally {
		processing.value = false
	}
}

async function submitRemoveStock() {
	if (!removeForm.value.serial_no) return
	processing.value = true
	errorMsg.value = ''
	successMsg.value = ''
	try {
		const result = await call('zevar_core.services.stock_reduction.ui_remove_stock', {
			serial_no: removeForm.value.serial_no.trim(),
			reason: removeForm.value.reason,
		})
		successMsg.value = `Removed ${removeForm.value.serial_no}. Entry: ${result.stock_entry}`
		removeForm.value.serial_no = ''
	} catch (e) {
		errorMsg.value = e?.messages?.[0] || e?.message || 'Failed to remove stock'
	} finally {
		processing.value = false
	}
}

async function submitTransfer() {
	if (!transferForm.value.serial_no || !transferForm.value.target_warehouse) return
	processing.value = true
	errorMsg.value = ''
	successMsg.value = ''
	try {
		const result = await call('zevar_core.services.stock_reduction.ui_move_stock', {
			serial_no: transferForm.value.serial_no.trim(),
			target_warehouse: transferForm.value.target_warehouse,
		})
		successMsg.value = `Transferred ${transferForm.value.serial_no} to ${transferForm.value.target_warehouse}. Entry: ${result.stock_entry}`
		transferForm.value.serial_no = ''
	} catch (e) {
		errorMsg.value = e?.messages?.[0] || e?.message || 'Failed to transfer'
	} finally {
		processing.value = false
	}
}
</script>
