<template>
	<BaseModal :show="true" max-width="max-w-3xl" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-[#D4AF37]/10 rounded-lg">
					<svg
						class="w-6 h-6 text-[#D4AF37]"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						/>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Quick Add Item</h3>
					<p class="text-xs text-gray-500">Create item & allocate stock in one step</p>
				</div>
			</div>
		</template>

		<div class="p-6">
			<div class="mb-4">
				<ScannerInput placeholder="Scan barcode or RFID tag..." @scan="onScan" />
			</div>

			<div class="grid grid-cols-3 gap-3 mb-3">
				<div class="col-span-2">
					<label class="block text-xs font-medium mb-1">Item Name *</label>
					<input
						v-model="form.item_name"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="e.g. 14K Gold Diamond Ring"
					/>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Jewelry Type</label>
					<select
						v-model="form.jewelry_type"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="Other">Other</option>
						<option>Rings</option>
						<option>Earrings</option>
						<option>Necklaces</option>
						<option>Bracelets</option>
						<option>Chains</option>
						<option>Pendants</option>
						<option>Watches</option>
					</select>
				</div>
			</div>

			<div class="grid grid-cols-4 gap-3 mb-3">
				<div>
					<label class="block text-xs font-medium mb-1">Metal Type</label>
					<select
						v-model="form.metal_type"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="">Select...</option>
						<option>Yellow Gold</option>
						<option>White Gold</option>
						<option>Rose Gold</option>
						<option>Silver</option>
						<option>Platinum</option>
					</select>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Purity</label>
					<select
						v-model="form.purity"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="">Select...</option>
						<option>24Kt</option>
						<option>22Kt</option>
						<option>18Kt</option>
						<option>14Kt</option>
						<option>10Kt</option>
						<option>925 Sterling</option>
					</select>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Gross Wt (g)</label>
					<input
						v-model="form.gross_weight"
						type="number"
						step="0.01"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="0.00"
					/>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Stone Wt (g)</label>
					<input
						v-model="form.stone_weight"
						type="number"
						step="0.01"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="0.00"
					/>
				</div>
			</div>

			<div class="grid grid-cols-4 gap-3 mb-3">
				<div>
					<label class="block text-xs font-medium mb-1">Retail Price (MSRP) *</label>
					<input
						v-model="form.msrp"
						type="number"
						step="0.01"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="0.00"
					/>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Cost Price</label>
					<input
						v-model="form.cost_price"
						type="number"
						step="0.01"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="0.00"
					/>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Vendor</label>
					<input
						v-model="form.vendor"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="Supplier name"
					/>
				</div>
				<div>
					<label class="block text-xs font-medium mb-1">Vendor SKU</label>
					<input
						v-model="form.vendor_sku"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="Auto-generated if blank"
					/>
				</div>
			</div>

			<div class="mb-4">
				<label class="block text-xs font-medium mb-2">Allocate to Stores</label>
				<div class="grid grid-cols-5 gap-2">
					<div v-for="store in stores" :key="store.code" class="text-center">
						<div class="text-[10px] font-bold text-gray-500 mb-1">
							{{ store.code }}
						</div>
						<div class="flex items-center justify-center gap-1">
							<button
								@click="form.allocation[store.code] = Math.max( 0, (form.allocation[store.code] || 0) - 1 )"
								class="w-7 h-7 rounded bg-gray-100 dark:bg-warm-dark-700 text-xs font-bold hover:bg-gray-200"
							>
								−
							</button>
							<span class="w-8 text-center text-sm font-bold">{{
								form.allocation[store.code] || 0
							}}</span>
							<button
								@click="form.allocation[store.code] = (form.allocation[store.code] || 0) + 1"
								class="w-7 h-7 rounded bg-gray-100 dark:bg-warm-dark-700 text-xs font-bold hover:bg-gray-200"
							>
								+
							</button>
						</div>
					</div>
				</div>
				<div class="text-xs text-gray-400 mt-1 text-right">Total: {{ totalQty }} pcs</div>
			</div>

			<div
				v-if="errorMsg"
				class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-100 mb-3"
			>
				<p class="text-xs text-red-700">{{ errorMsg }}</p>
			</div>

			<div
				v-if="createdItem"
				class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-100 mb-3"
			>
				<p class="text-xs text-green-700 font-bold">
					Item created: {{ createdItem.item_code }}
				</p>
				<p class="text-xs text-green-600">SKU: {{ createdItem.vendor_sku }}</p>
				<p v-if="createdItem.stock_entry_created" class="text-xs text-green-600">
					Stock entry created
				</p>
			</div>

			<div v-if="showTags && createdItem" class="border-t pt-4 mt-4">
				<h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">Print Tags</h4>
				<div class="grid grid-cols-2 gap-3">
					<TagPrintPreview
						v-for="(tag, idx) in printTags"
						:key="idx"
						:item-data="tag"
						@printed="onTagPrinted"
					/>
				</div>
			</div>
		</div>

		<template #footer>
			<button
				@click="$emit('close')"
				class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
			>
				{{ createdItem ? 'Done' : 'Cancel' }}
			</button>
			<button
				v-if="!createdItem"
				@click="submitItem"
				:disabled="submitting || !canSubmit"
				class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] disabled:opacity-50 transition"
			>
				{{ submitting ? 'Creating...' : `Create Item & Push ${totalQty} pcs` }}
			</button>
			<button
				v-if="createdItem && !showTags"
				@click="showTags = true"
				class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition"
			>
				Print Tags
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'
import ScannerInput from './ScannerInput.vue'
import TagPrintPreview from './TagPrintPreview.vue'

const emit = defineEmits(['close', 'created'])

const submitting = ref(false)
const errorMsg = ref('')
const createdItem = ref(null)
const showTags = ref(false)
const printTags = ref([])

const stores = [
	{ code: 'NY-01', city: 'New York' },
	{ code: 'Miami-01', city: 'Miami' },
	{ code: 'LA-01', city: 'Los Angeles' },
	{ code: 'Houston-01', city: 'Houston' },
	{ code: 'Chicago-01', city: 'Chicago' },
]

const form = reactive({
	item_name: '',
	metal_type: '',
	purity: '',
	jewelry_type: 'Other',
	gross_weight: '',
	stone_weight: '',
	msrp: '',
	cost_price: '',
	vendor: '',
	vendor_sku: '',
	barcode: '',
	allocation: { 'NY-01': 1, 'Miami-01': 0, 'LA-01': 0, 'Houston-01': 0, 'Chicago-01': 0 },
})

const totalQty = computed(() => Object.values(form.allocation).reduce((s, q) => s + q, 0))

const canSubmit = computed(() => !!form.item_name && !!form.msrp && totalQty.value > 0)

function onScan(value) {
	form.barcode = value
}

function buildPrintTags(itemResult) {
	printTags.value = []
	for (let i = 0; i < totalQty.value; i++) {
		printTags.value.push({
			barcode: form.barcode || `${itemResult.item_code}-${i}`,
			serialNo: '',
			itemCode: itemResult.item_code,
			itemName: form.item_name,
			price: form.msrp,
			metal: form.metal_type,
			purity: form.purity,
			weight: form.gross_weight,
			vendorSku: itemResult.vendor_sku,
		})
	}
}

function onTagPrinted() {}

async function submitItem() {
	submitting.value = true
	errorMsg.value = ''

	try {
		const result = await call('zevar_core.api.item_entry.pos_quick_add_item', {
			item_name: form.item_name,
			metal_type: form.metal_type || undefined,
			purity: form.purity || undefined,
			jewelry_type: form.jewelry_type,
			gross_weight: form.gross_weight || 0,
			stone_weight: form.stone_weight || 0,
			msrp: form.msrp || 0,
			cost_price: form.cost_price || 0,
			vendor: form.vendor || undefined,
			vendor_sku: form.vendor_sku || undefined,
			warehouse: undefined,
			qty: 0,
		})

		if (result.success && totalQty.value > 0) {
			const alloc = Object.entries(form.allocation)
				.filter(([, q]) => q > 0)
				.map(([store_code, qty]) => ({ store_code, qty }))

			if (alloc.length > 0) {
				await call('zevar_core.api.inventory.bulk_push_to_stores', {
					item_code: result.item_code,
					allocation: alloc,
				})
			}
		}

		createdItem.value = result
		buildPrintTags(result)
		toast({
			title: 'Item Created',
			message: `${result.item_code} — ${result.vendor_sku}`,
			icon: 'check',
			intent: 'success',
		})
		emit('created')
	} catch (e) {
		errorMsg.value = e.messages?.[0] || e.message || 'Failed to create item'
		toast({ title: 'Error', message: errorMsg.value, icon: 'alert-triangle', intent: 'error' })
	} finally {
		submitting.value = false
	}
}
</script>
