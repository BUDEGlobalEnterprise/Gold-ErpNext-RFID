<template>
	<BaseModal :show="true" max-width="max-w-4xl" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
					<svg
						class="w-6 h-6 text-blue-600"
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
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Edit Item</h3>
					<p class="text-xs text-gray-500 font-mono">{{ itemCode }}</p>
				</div>
			</div>
		</template>

		<div v-if="loading" class="flex items-center justify-center py-16 text-sm text-gray-400">
			Loading...
		</div>

		<div v-else class="p-6 space-y-5">
			<div class="grid grid-cols-3 gap-3">
				<div class="col-span-2">
					<label class="block text-xs font-medium mb-1">Item Name *</label>
					<input
						v-model="form.item_name"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
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

			<div>
				<label class="block text-xs font-medium mb-1">Description</label>
				<textarea
					v-model="form.description"
					rows="2"
					class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none"
				></textarea>
			</div>

			<div>
				<div class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
					Metal & Purity
				</div>
				<div class="grid grid-cols-4 gap-3">
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
						<label class="block text-xs font-medium mb-1">Material Color</label>
						<input
							v-model="form.material_color"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							placeholder="Yellow, White, Rose..."
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Gender</label>
						<select
							v-model="form.gender"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option>Unisex</option>
							<option>Women's</option>
							<option>Men's</option>
						</select>
					</div>
				</div>
			</div>

			<div>
				<div class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
					Weight
				</div>
				<div class="grid grid-cols-3 gap-3">
					<div>
						<label class="block text-xs font-medium mb-1">Gross Weight (g)</label>
						<input
							v-model="form.gross_weight"
							type="number"
							step="0.001"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Stone Weight (g)</label>
						<input
							v-model="form.stone_weight"
							type="number"
							step="0.001"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Net Weight (g)</label>
						<input
							:value="netWeight"
							type="number"
							step="0.001"
							class="w-full px-3 py-2 border rounded-lg bg-gray-50 dark:bg-warm-dark-800 text-sm text-gray-500"
							readonly
						/>
					</div>
				</div>
			</div>

			<div>
				<div class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
					Dimensions
				</div>
				<div class="grid grid-cols-5 gap-3">
					<div>
						<label class="block text-xs font-medium mb-1">Size</label>
						<input
							v-model="form.size"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							placeholder="7, M, L..."
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Length</label>
						<input
							v-model="form.length_value"
							type="number"
							step="0.01"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Length Unit</label>
						<select
							v-model="form.length_unit"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option value="">-</option>
							<option>in</option>
							<option>cm</option>
							<option>mm</option>
						</select>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Width</label>
						<input
							v-model="form.width_value"
							type="number"
							step="0.01"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Width Unit</label>
						<select
							v-model="form.width_unit"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option value="">-</option>
							<option>in</option>
							<option>cm</option>
							<option>mm</option>
						</select>
					</div>
				</div>
			</div>

			<div>
				<div class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
					Chain & Clasp
				</div>
				<div class="grid grid-cols-3 gap-3">
					<div>
						<label class="block text-xs font-medium mb-1">Chain Type</label>
						<input
							v-model="form.chain_type"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							placeholder="Cable, Box, Rope..."
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Clasp Type</label>
						<input
							v-model="form.clasp_type"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							placeholder="Lobster, Spring..."
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Finish</label>
						<input
							v-model="form.finish"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							placeholder="Polished, Matte..."
						/>
					</div>
				</div>
			</div>

			<div>
				<div class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
					Vendor & Identification
				</div>
				<div class="grid grid-cols-4 gap-3">
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
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm font-mono"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Barcode</label>
						<input
							v-model="form.barcode"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm font-mono"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">RFID EPC</label>
						<input
							v-model="form.rfid_epc"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm font-mono"
						/>
					</div>
				</div>
			</div>

			<div>
				<div class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
					Pricing
				</div>
				<div class="grid grid-cols-4 gap-3">
					<div>
						<label class="block text-xs font-medium mb-1">MSRP (Retail)</label>
						<input
							v-model="form.msrp"
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
					<div>
						<label class="block text-xs font-medium mb-1">Standard Rate</label>
						<input
							v-model="form.standard_rate"
							type="number"
							step="0.01"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-xs font-medium mb-1">Origin</label>
						<input
							v-model="form.country_of_origin"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
				</div>
			</div>

			<div>
				<div class="flex items-center justify-between mb-2">
					<div class="text-xs font-bold text-gray-500 uppercase tracking-wider">
						Gemstones
					</div>
					<button
						@click="addGemstone"
						class="text-xs font-bold text-blue-600 hover:text-blue-700"
					>
						+ Add Gemstone
					</button>
				</div>
				<div
					v-if="gemstones.length === 0"
					class="text-xs text-gray-400 py-3 text-center border border-dashed border-gray-200 rounded-lg"
				>
					No gemstones added
				</div>
				<div v-else class="space-y-2">
					<div
						v-for="(gem, idx) in gemstones"
						:key="idx"
						class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3"
					>
						<div class="flex items-center justify-between mb-2">
							<span class="text-[10px] font-bold text-gray-500"
								>GEMSTONE {{ idx + 1 }}</span
							>
							<button
								@click="gemstones.splice(idx, 1)"
								class="text-xs text-red-500 hover:text-red-700"
							>
								Remove
							</button>
						</div>
						<div class="grid grid-cols-7 gap-2">
							<div>
								<label class="block text-[10px] font-medium mb-0.5">Type</label>
								<select
									v-model="gem.gem_type"
									class="w-full px-2 py-1.5 border rounded bg-white dark:bg-warm-dark-800 text-xs"
								>
									<option value="">-</option>
									<option>Diamond</option>
									<option>Ruby</option>
									<option>Emerald</option>
									<option>Sapphire</option>
									<option>Polki</option>
									<option>Kundan</option>
								</select>
							</div>
							<div>
								<label class="block text-[10px] font-medium mb-0.5">Carat</label>
								<input
									v-model="gem.carat"
									type="number"
									step="0.001"
									class="w-full px-2 py-1.5 border rounded bg-white dark:bg-warm-dark-800 text-xs"
								/>
							</div>
							<div>
								<label class="block text-[10px] font-medium mb-0.5">Count</label>
								<input
									v-model="gem.count"
									type="number"
									class="w-full px-2 py-1.5 border rounded bg-white dark:bg-warm-dark-800 text-xs"
								/>
							</div>
							<div>
								<label class="block text-[10px] font-medium mb-0.5">Cut</label>
								<select
									v-model="gem.cut"
									class="w-full px-2 py-1.5 border rounded bg-white dark:bg-warm-dark-800 text-xs"
								>
									<option value="">-</option>
									<option>Excellent</option>
									<option>Very Good</option>
									<option>Good</option>
								</select>
							</div>
							<div>
								<label class="block text-[10px] font-medium mb-0.5">Color</label>
								<select
									v-model="gem.color"
									class="w-full px-2 py-1.5 border rounded bg-white dark:bg-warm-dark-800 text-xs"
								>
									<option value="">-</option>
									<option>D</option>
									<option>E</option>
									<option>F</option>
									<option>G</option>
									<option>H</option>
									<option>I</option>
									<option>J</option>
									<option>K</option>
								</select>
							</div>
							<div>
								<label class="block text-[10px] font-medium mb-0.5">Clarity</label>
								<select
									v-model="gem.clarity"
									class="w-full px-2 py-1.5 border rounded bg-white dark:bg-warm-dark-800 text-xs"
								>
									<option value="">-</option>
									<option>FL</option>
									<option>IF</option>
									<option>VVS1</option>
									<option>VVS2</option>
									<option>VS1</option>
									<option>VS2</option>
									<option>SI1</option>
									<option>SI2</option>
								</select>
							</div>
							<div>
								<label class="block text-[10px] font-medium mb-0.5">Rate</label>
								<input
									v-model="gem.rate"
									type="number"
									step="0.01"
									class="w-full px-2 py-1.5 border rounded bg-white dark:bg-warm-dark-800 text-xs"
								/>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div
				v-if="errorMsg"
				class="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-100"
			>
				<p class="text-xs text-red-700">{{ errorMsg }}</p>
			</div>
		</div>

		<template #footer>
			<button
				@click="$emit('close')"
				class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
			>
				Cancel
			</button>
			<button
				@click="save"
				:disabled="saving || !form.item_name"
				class="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 disabled:opacity-50"
			>
				{{ saving ? 'Saving...' : 'Save Changes' }}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({ itemCode: { type: String, required: true } })
const emit = defineEmits(['close', 'saved'])

const loading = ref(true)
const saving = ref(false)
const errorMsg = ref('')

const form = reactive({
	item_name: '',
	jewelry_type: 'Other',
	description: '',
	metal_type: '',
	purity: '',
	material_color: '',
	gender: 'Unisex',
	gross_weight: '',
	stone_weight: '',
	size: '',
	length_value: '',
	length_unit: '',
	width_value: '',
	width_unit: '',
	chain_type: '',
	clasp_type: '',
	finish: '',
	vendor: '',
	vendor_sku: '',
	barcode: '',
	rfid_epc: '',
	msrp: '',
	cost_price: '',
	standard_rate: '',
	country_of_origin: 'USA',
	plating: '',
})

const gemstones = ref([])

const netWeight = computed(() => {
	const g = parseFloat(form.gross_weight) || 0
	const s = parseFloat(form.stone_weight) || 0
	return Math.max(0, g - s).toFixed(3)
})

function addGemstone() {
	gemstones.value.push({
		gem_type: '',
		carat: '',
		count: 1,
		cut: '',
		color: '',
		clarity: '',
		rate: '',
	})
}

onMounted(async () => {
	try {
		const data = await call('zevar_core.services.stock_reduction.ui_get_item_for_edit', {
			item_code: props.itemCode,
		})
		form.item_name = data.item_name || ''
		form.jewelry_type = data.custom_jewelry_type || 'Other'
		form.description = data.description || ''
		form.metal_type = data.custom_metal_type || ''
		form.purity = data.custom_purity || ''
		form.material_color = data.custom_material_color || ''
		form.gender = data.custom_gender || 'Unisex'
		form.gross_weight = data.custom_gross_weight_g || ''
		form.stone_weight = data.custom_stone_weight_g || ''
		form.size = data.custom_size || ''
		form.length_value = data.custom_length_value || ''
		form.length_unit = data.custom_length_unit || ''
		form.width_value = data.custom_width_value || ''
		form.width_unit = data.custom_width_unit || ''
		form.chain_type = data.custom_chain_type || ''
		form.clasp_type = data.custom_clasp_type || ''
		form.finish = data.custom_finish || ''
		form.vendor = data.custom_vendor || ''
		form.vendor_sku = data.custom_vendor_sku || ''
		form.barcode = data.custom_barcode || ''
		form.rfid_epc = data.custom_rfid_epc || ''
		form.msrp = data.custom_msrp || ''
		form.cost_price = data.custom_cost_price || ''
		form.standard_rate = data.standard_rate || ''
		form.country_of_origin = data.custom_country_of_origin || 'USA'
		gemstones.value = data.gemstones || []
	} catch (e) {
		errorMsg.value = e.messages?.[0] || e.message || 'Failed to load item'
	} finally {
		loading.value = false
	}
})

async function save() {
	saving.value = true
	errorMsg.value = ''
	try {
		await call('zevar_core.api.item_entry.update_item', {
			item_code: props.itemCode,
			item_name: form.item_name || undefined,
			jewelry_type: form.jewelry_type || undefined,
			description: form.description || undefined,
			metal_type: form.metal_type || undefined,
			purity: form.purity || undefined,
			material_color: form.material_color || undefined,
			gender: form.gender || undefined,
			gross_weight: form.gross_weight || undefined,
			stone_weight: form.stone_weight || undefined,
			size: form.size || undefined,
			length_value: form.length_value || undefined,
			length_unit: form.length_unit || undefined,
			width_value: form.width_value || undefined,
			width_unit: form.width_unit || undefined,
			chain_type: form.chain_type || undefined,
			clasp_type: form.clasp_type || undefined,
			finish: form.finish || undefined,
			vendor: form.vendor || undefined,
			vendor_sku: form.vendor_sku || undefined,
			barcode: form.barcode || undefined,
			rfid_epc: form.rfid_epc || undefined,
			msrp: form.msrp || undefined,
			cost_price: form.cost_price || undefined,
			standard_rate: form.standard_rate || undefined,
			country_of_origin: form.country_of_origin || undefined,
			gemstones: gemstones.value.length > 0 ? JSON.stringify(gemstones.value) : undefined,
		})
		toast({
			title: 'Saved',
			message: `${form.item_name} updated`,
			icon: 'check',
			intent: 'success',
		})
		emit('saved')
	} catch (e) {
		errorMsg.value = e.messages?.[0] || e.message || 'Failed to save'
	} finally {
		saving.value = false
	}
}
</script>
