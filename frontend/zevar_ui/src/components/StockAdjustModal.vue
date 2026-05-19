<template>
	<BaseModal :show="true" max-width="max-w-lg" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
					<svg
						class="w-6 h-6 text-emerald-600"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">
						Quick Stock Adjust
					</h3>
					<p class="text-xs text-gray-500">Add, remove, or move stock</p>
				</div>
			</div>
		</template>

		<div class="p-6 pt-4">
			<div class="flex gap-1 mb-4 bg-gray-100 dark:bg-warm-dark-900 rounded-lg p-1">
				<button
					v-for="tab in tabs"
					:key="tab.key"
					@click="activeTab = tab.key"
					:class="[
						'flex-1 py-2 px-3 rounded-md text-xs font-bold transition',
						activeTab === tab.key
							? 'bg-white dark:bg-warm-dark-700 shadow text-emerald-600 dark:text-emerald-400'
							: 'text-gray-500 hover:text-gray-700',
					]"
				>
					{{ tab.label }}
				</button>
			</div>

			<div v-if="activeTab === 'add'" class="space-y-3">
				<div>
					<label class="block text-sm font-medium mb-1">Item Code *</label>
					<input
						v-model="addItemCode"
						type="text"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="Enter item code or scan barcode"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Warehouse *</label>
					<select
						v-model="addWarehouse"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="">Select warehouse...</option>
						<optgroup
							v-for="(store, code) in storeWarehouses"
							:key="code"
							:label="`${code} - ${store.name}`"
						>
							<option v-for="wh in store.warehouses" :key="wh.name" :value="wh.name">
								{{ wh.warehouse_name }}
							</option>
						</optgroup>
					</select>
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-sm font-medium mb-1">Qty *</label>
						<input
							v-model.number="addQty"
							type="number"
							min="1"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-sm font-medium mb-1">Valuation Rate</label>
						<input
							v-model.number="addRate"
							type="number"
							step="0.01"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							placeholder="$0.00"
						/>
					</div>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Reason</label>
					<input
						v-model="addReason"
						type="text"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="New shipment, restock, etc."
					/>
				</div>
			</div>

			<div v-if="activeTab === 'remove'" class="space-y-3">
				<div>
					<label class="block text-sm font-medium mb-1">Serial No *</label>
					<input
						v-model="removeSerial"
						type="text"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="Scan or enter serial number"
					/>
				</div>
				<div
					v-if="removeLookup && removeLookup.found"
					class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 space-y-1"
				>
					<div class="text-xs">
						<span class="text-gray-500">Item:</span>
						<span class="font-bold ml-1">{{ removeLookup.item_code }}</span>
					</div>
					<div class="text-xs">
						<span class="text-gray-500">Name:</span>
						<span class="ml-1">{{ removeLookup.item_name }}</span>
					</div>
					<div class="text-xs">
						<span class="text-gray-500">Warehouse:</span>
						<span class="ml-1">{{ removeLookup.warehouse }}</span>
					</div>
					<div class="text-xs">
						<span class="text-gray-500">Value:</span>
						<span class="font-bold ml-1"
							>${{ (removeLookup.valuation_rate || 0).toFixed(2) }}</span
						>
					</div>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Reason</label>
					<input
						v-model="removeReason"
						type="text"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="Damaged, lost, vendor return, etc."
					/>
				</div>
			</div>

			<div v-if="activeTab === 'move'" class="space-y-3">
				<div>
					<label class="block text-sm font-medium mb-1">Serial No *</label>
					<input
						v-model="moveSerial"
						type="text"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="Scan or enter serial number"
					/>
				</div>
				<div
					v-if="moveLookup && moveLookup.found"
					class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 space-y-1"
				>
					<div class="text-xs">
						<span class="text-gray-500">Current:</span>
						<span class="font-bold ml-1">{{ moveLookup.warehouse }}</span>
					</div>
					<div class="text-xs">
						<span class="text-gray-500">Item:</span>
						<span class="ml-1">{{ moveLookup.item_code }}</span>
					</div>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Target Warehouse *</label>
					<select
						v-model="moveTarget"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="">Select target warehouse...</option>
						<optgroup
							v-for="(store, code) in storeWarehouses"
							:key="code"
							:label="`${code} - ${store.name}`"
						>
							<option v-for="wh in store.warehouses" :key="wh.name" :value="wh.name">
								{{ wh.warehouse_name }}
							</option>
						</optgroup>
					</select>
				</div>
			</div>

			<div
				v-if="errorMsg"
				class="mt-3 bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-100"
			>
				<p class="text-xs text-red-700">{{ errorMsg }}</p>
			</div>
			<div
				v-if="successMsg"
				class="mt-3 bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-100"
			>
				<p class="text-xs text-green-700">{{ successMsg }}</p>
			</div>
		</div>

		<template #footer>
			<button
				@click="$emit('close')"
				class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
			>
				Close
			</button>
			<button
				@click="submit"
				:disabled="submitting || !canSubmit"
				class="flex-1 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50"
			>
				{{ submitting ? 'Processing...' : submitLabel }}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { call, createResource, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const emit = defineEmits(['close', 'completed'])

const tabs = [
	{ key: 'add', label: 'Add Stock' },
	{ key: 'remove', label: 'Remove' },
	{ key: 'move', label: 'Move' },
]

const activeTab = ref('add')
const submitting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const storeWarehouses = ref({})
const addItemCode = ref('')
const addWarehouse = ref('')
const addQty = ref(1)
const addRate = ref(null)
const addReason = ref('')

const removeSerial = ref('')
const removeReason = ref('')
const removeLookup = ref(null)

const moveSerial = ref('')
const moveTarget = ref('')
const moveLookup = ref(null)

const canSubmit = computed(() => {
	if (activeTab.value === 'add')
		return addItemCode.value && addWarehouse.value && addQty.value > 0
	if (activeTab.value === 'remove') return removeSerial.value
	if (activeTab.value === 'move') return moveSerial.value && moveTarget.value
	return false
})

const submitLabel = computed(() => {
	if (activeTab.value === 'add') return `Add ${addQty.value} pcs`
	if (activeTab.value === 'remove') return 'Remove Piece'
	if (activeTab.value === 'move') return 'Move Piece'
	return 'Submit'
})

watch(removeSerial, async (val) => {
	if (!val) {
		removeLookup.value = null
		return
	}
	try {
		const res = await call('zevar_core.services.stock_reduction.ui_lookup_piece', {
			query: val,
		})
		removeLookup.value = res
	} catch {
		removeLookup.value = null
	}
})

watch(moveSerial, async (val) => {
	if (!val) {
		moveLookup.value = null
		return
	}
	try {
		const res = await call('zevar_core.services.stock_reduction.ui_lookup_piece', {
			query: val,
		})
		moveLookup.value = res
	} catch {
		moveLookup.value = null
	}
})

onMounted(async () => {
	try {
		storeWarehouses.value = await call(
			'zevar_core.services.stock_reduction.ui_get_store_warehouses'
		)
	} catch {}
})

async function submit() {
	submitting.value = true
	errorMsg.value = ''
	successMsg.value = ''

	try {
		let result
		if (activeTab.value === 'add') {
			result = await call('zevar_core.services.stock_reduction.ui_add_stock', {
				item_code: addItemCode.value,
				warehouse: addWarehouse.value,
				qty: addQty.value,
				valuation_rate: addRate.value || undefined,
				reason: addReason.value || undefined,
			})
			successMsg.value = `Added ${addQty.value} pcs. Stock Entry: ${result.stock_entry}`
		} else if (activeTab.value === 'remove') {
			result = await call('zevar_core.services.stock_reduction.ui_remove_stock', {
				serial_no: removeSerial.value,
				reason: removeReason.value || undefined,
			})
			successMsg.value = `Removed ${removeSerial.value}. Stock Entry: ${result.stock_entry}`
		} else if (activeTab.value === 'move') {
			result = await call('zevar_core.services.stock_reduction.ui_move_stock', {
				serial_no: moveSerial.value,
				target_warehouse: moveTarget.value,
			})
			successMsg.value = `Moved ${moveSerial.value}. Stock Entry: ${result.stock_entry}`
		}

		toast({ title: 'Success', message: successMsg.value, icon: 'check', intent: 'success' })
		emit('completed')
	} catch (e) {
		errorMsg.value = e.messages?.[0] || e.message || 'An error occurred'
		toast({ title: 'Error', message: errorMsg.value, icon: 'alert-triangle', intent: 'error' })
	} finally {
		submitting.value = false
	}
}
</script>
