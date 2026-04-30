<template>
	<BaseModal :show="true" max-width="max-w-4xl" scrollable @close="$emit('close')">
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
					<p class="text-xs text-gray-500">Step {{ currentStep }} of 4</p>
				</div>
			</div>
		</template>

		<div class="p-6">
			<div class="flex items-center gap-2 mb-6">
				<div
					v-for="s in 4"
					:key="s"
					class="flex-1 h-1.5 rounded-full"
					:class="
						s <= currentStep ? 'bg-[#D4AF37]' : 'bg-gray-200 dark:bg-warm-dark-700'
					"
				/>
			</div>

			<div v-if="currentStep === 1">
				<h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">
					Photo / Tag Scan
				</h4>
				<ScannerInput placeholder="Scan item barcode or RFID..." @scan="onScanTag" />
				<div class="mt-4 text-center text-gray-400 text-xs">or</div>
				<button
					class="mt-3 w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-500 hover:border-[#D4AF37] hover:text-[#D4AF37] transition"
				>
					Upload Photo of Tag
				</button>
			</div>

			<div v-if="currentStep === 2">
				<h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">
					Item Details
				</h4>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-xs font-medium mb-1">Item Name *</label>
						<input
							v-model="form.item_name"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Item Code</label>
						<input
							v-model="form.item_code"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Metal Type</label>
						<select
							v-model="form.metal"
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
						<label class="block text-xs font-medium mb-1">Weight (g)</label>
						<input
							v-model="form.weight"
							type="number"
							step="0.01"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Vendor SKU</label>
						<input
							v-model="form.vendor_sku"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
				</div>
			</div>

			<div v-if="currentStep === 3">
				<h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">
					Pricing & Store Allocation
				</h4>
				<div class="grid grid-cols-2 gap-3 mb-4">
					<div>
						<label class="block text-xs font-medium mb-1">Retail Price *</label>
						<input
							v-model="form.price"
							type="number"
							step="0.01"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Cost Price</label>
						<input
							v-model="form.cost_price"
							type="number"
							step="0.01"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
				</div>
				<div>
					<label class="block text-xs font-medium mb-2">Allocate to Stores</label>
					<div
						v-for="store in stores"
						:key="store.code"
						class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
					>
						<span class="text-sm text-gray-700 dark:text-gray-300"
							>{{ store.code }} — {{ store.city }}</span
						>
						<div class="flex items-center gap-2">
							<button
								@click="
									form.allocation[store.code] = Math.max(
										0,
										(form.allocation[store.code] || 0) - 1
									)
								"
								class="w-7 h-7 rounded bg-gray-100 dark:bg-warm-dark-700 text-xs font-bold"
							>
								−
							</button>
							<span class="w-8 text-center text-sm font-bold">{{
								form.allocation[store.code] || 0
							}}</span>
							<button
								@click="
									form.allocation[store.code] =
										(form.allocation[store.code] || 0) + 1
								"
								class="w-7 h-7 rounded bg-gray-100 dark:bg-warm-dark-700 text-xs font-bold"
							>
								+
							</button>
						</div>
					</div>
				</div>
			</div>

			<div v-if="currentStep === 4">
				<h4 class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">
					Confirm & Print Tags
				</h4>
				<div class="premium-card !p-4 mb-4">
					<div class="grid grid-cols-2 gap-2 text-sm">
						<div><span class="text-gray-500">Item:</span> {{ form.item_name }}</div>
						<div>
							<span class="text-gray-500">Metal:</span> {{ form.metal }}
							{{ form.purity }}
						</div>
						<div><span class="text-gray-500">Price:</span> ${{ form.price }}</div>
						<div><span class="text-gray-500">Weight:</span> {{ form.weight }}g</div>
					</div>
					<div class="mt-2 text-sm">
						<span class="text-gray-500">Stores:</span>
						{{
							Object.entries(form.allocation)
								.filter(([, q]) => q > 0)
								.map(([s, q]) => `${s}(${q})`)
								.join(', ') || 'None'
						}}
					</div>
				</div>
				<div v-for="tag in printTags" :key="tag.serialNo" class="mb-3">
					<TagPrintPreview :item-data="tag" @printed="onTagPrinted" />
				</div>
			</div>
		</div>

		<template #footer>
			<div class="flex gap-3 w-full">
				<button
					v-if="currentStep > 1"
					@click="currentStep--"
					class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50 transition"
				>
					Back
				</button>
				<button
					v-if="currentStep < 4"
					@click="nextStep"
					:disabled="!canProceed"
					class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-sm font-medium hover:bg-[#C4A030] disabled:opacity-50 transition"
				>
					Next
				</button>
				<button
					v-if="currentStep === 4"
					@click="submitItem"
					:disabled="submitting"
					class="flex-1 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition"
				>
					{{ submitting ? 'Creating...' : 'Create Item & Push' }}
				</button>
			</div>
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

const currentStep = ref(1)
const submitting = ref(false)
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
	item_code: '',
	metal: '',
	purity: '',
	weight: '',
	vendor_sku: '',
	price: '',
	cost_price: '',
	barcode: '',
	allocation: { 'NY-01': 1, 'Miami-01': 0, 'LA-01': 0, 'Houston-01': 0, 'Chicago-01': 0 },
})

const canProceed = computed(() => {
	if (currentStep.value === 1) return true
	if (currentStep.value === 2) return !!form.item_name
	if (currentStep.value === 3)
		return !!form.price && Object.values(form.allocation).some((q) => q > 0)
	return true
})

function onScanTag(value) {
	form.barcode = value
	currentStep.value = 2
}

function nextStep() {
	if (!canProceed.value) return
	currentStep.value++
	if (currentStep.value === 4) {
		buildPrintTags()
	}
}

function buildPrintTags() {
	printTags.value = []
	const totalQty = Object.values(form.allocation).reduce((s, q) => s + q, 0)
	for (let i = 0; i < totalQty; i++) {
		printTags.value.push({
			barcode: form.barcode || `ZV-${Date.now()}-${i}`,
			serialNo: '',
			itemCode: form.item_code,
			itemName: form.item_name,
			price: form.price,
			metal: form.metal,
			purity: form.purity,
			weight: form.weight,
			vendorSku: form.vendor_sku,
		})
	}
}

function onTagPrinted() {}

async function submitItem() {
	submitting.value = true
	try {
		await call('zevar_core.api.inventory.bulk_push_to_stores', {
			item_code: form.item_code,
			allocation: Object.entries(form.allocation)
				.filter(([, q]) => q > 0)
				.map(([store_code, qty]) => ({ store_code, qty })),
		})
		toast({
			title: 'Item Created',
			message: 'Item pushed to stores',
			icon: 'check',
			intent: 'success',
		})
		emit('created')
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message || 'Failed',
			icon: 'alert-triangle',
			intent: 'error',
		})
	} finally {
		submitting.value = false
	}
}
</script>
