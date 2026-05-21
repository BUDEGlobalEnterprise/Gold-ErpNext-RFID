<template>
	<BaseModal :show="true" max-width="max-w-4xl" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
					<svg
						class="w-6 h-6 text-amber-600"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">
						Gold Scrap Purchase
					</h3>
					<p class="text-xs text-gray-500">
						Buy scrap gold from customers at live rates
					</p>
				</div>
			</div>
		</template>

		<div class="p-6 pt-0 space-y-4">
			<!-- Customer & Store -->
			<div class="grid grid-cols-2 gap-4">
				<div>
					<label class="block text-sm font-medium mb-1">Customer / Seller *</label>
					<customer-selector v-model="form.customer" @select="onCustomerSelect" />
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Store Location *</label>
					<select
						v-model="form.store_location"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option v-for="loc in storeLocations" :key="loc.name" :value="loc.name">
							{{ loc.store_name }}
						</option>
					</select>
				</div>
			</div>

			<!-- Seller ID -->
			<div class="grid grid-cols-3 gap-4">
				<div>
					<label class="block text-sm font-medium mb-1">ID Type</label>
					<select
						v-model="form.id_type"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="">Not Required</option>
						<option>Drivers License</option>
						<option>Passport</option>
						<option>State ID</option>
						<option>Military ID</option>
					</select>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">ID Number</label>
					<input
						v-model="form.id_number"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="Required for cash >= $10,000"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Payment Method</label>
					<select
						v-model="form.payment_method"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option>Cash</option>
						<option>Check</option>
						<option>Wire Transfer</option>
						<option>Zelle</option>
					</select>
				</div>
			</div>

			<!-- Scrap Items Table -->
			<div class="border rounded-lg overflow-hidden">
				<table class="w-full text-sm">
					<thead class="bg-gray-50 dark:bg-warm-dark-700">
						<tr>
							<th class="px-3 py-2 text-left">Metal</th>
							<th class="px-3 py-2 text-left">Purity</th>
							<th class="px-3 py-2 text-right">Gross (g)</th>
							<th class="px-3 py-2 text-right">Stone (g)</th>
							<th class="px-3 py-2 text-right">Net (g)</th>
							<th class="px-3 py-2 text-right">Rate/g</th>
							<th class="px-3 py-2 text-right">Calc Value</th>
							<th class="px-3 py-2 text-right">Agreed *</th>
							<th class="px-3 py-2 text-center">Test</th>
							<th class="px-3 py-2"></th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="(item, idx) in scrapItems"
							:key="idx"
							class="border-t dark:border-warm-dark-600"
						>
							<td class="px-3 py-2">
								<select
									v-model="item.metal_type"
									@change="recalcItem(idx)"
									class="w-full px-1 py-1 border rounded text-xs bg-white dark:bg-warm-dark-900"
								>
									<option>Yellow Gold</option>
									<option>White Gold</option>
									<option>Rose Gold</option>
									<option>Silver</option>
									<option>Platinum</option>
								</select>
							</td>
							<td class="px-3 py-2">
								<select
									v-model="item.purity"
									@change="recalcItem(idx)"
									class="w-full px-1 py-1 border rounded text-xs bg-white dark:bg-warm-dark-900"
								>
									<option>24Kt</option>
									<option>22Kt</option>
									<option>18Kt</option>
									<option>14Kt</option>
									<option>10Kt</option>
									<option>999 Fine</option>
									<option>925 Sterling</option>
								</select>
							</td>
							<td class="px-3 py-2">
								<input
									v-model.number="item.gross_weight_g"
									@input="recalcItem(idx)"
									type="number"
									step="0.01"
									min="0"
									class="w-20 px-1 py-1 border rounded text-right text-xs bg-white dark:bg-warm-dark-900"
								/>
							</td>
							<td class="px-3 py-2">
								<input
									v-model.number="item.stone_weight_g"
									@input="recalcItem(idx)"
									type="number"
									step="0.01"
									min="0"
									class="w-20 px-1 py-1 border rounded text-right text-xs bg-white dark:bg-warm-dark-900"
								/>
							</td>
							<td class="px-3 py-2 text-right font-mono text-xs">
								{{ item.net_weight_g?.toFixed(2) || '0.00' }}
							</td>
							<td class="px-3 py-2 text-right font-mono text-xs">
								{{ fmtCurrency(item.rate_per_gram) }}
							</td>
							<td class="px-3 py-2 text-right font-mono text-xs">
								{{ fmtCurrency(item.calculated_value) }}
							</td>
							<td class="px-3 py-2">
								<input
									v-model.number="item.agreed_value"
									type="number"
									step="0.01"
									min="0"
									class="w-24 px-1 py-1 border rounded text-right text-xs bg-amber-50 dark:bg-warm-dark-800 font-semibold"
								/>
							</td>
							<td class="px-3 py-2">
								<select
									v-model="item.test_method"
									class="w-full px-1 py-1 border rounded text-xs bg-white dark:bg-warm-dark-900"
								>
									<option value="">--</option>
									<option>XRF</option>
									<option>Acid Test</option>
									<option>Fire Assay</option>
									<option>Electronic Tester</option>
								</select>
							</td>
							<td class="px-3 py-2">
								<button
									@click="scrapItems.splice(idx, 1)"
									class="text-red-400 hover:text-red-600 text-xs"
								>
									Remove
								</button>
							</td>
						</tr>
					</tbody>
				</table>
				<button
					@click="addItem"
					class="w-full py-2 text-sm text-amber-600 hover:bg-amber-50 dark:hover:bg-warm-dark-700 font-medium"
				>
					+ Add Scrap Item
				</button>
			</div>

			<!-- Totals -->
			<div class="flex justify-end">
				<div class="bg-gray-50 dark:bg-warm-dark-700 rounded-lg p-4 w-72 space-y-2">
					<div class="flex justify-between text-sm">
						<span class="text-gray-500">Total Net Weight:</span>
						<span class="font-mono">{{ totalNetWeight.toFixed(2) }} g</span>
					</div>
					<div class="flex justify-between text-sm">
						<span class="text-gray-500">Calculated Value:</span>
						<span class="font-mono">{{ fmtCurrency(totalCalculatedValue) }}</span>
					</div>
					<div class="flex justify-between text-base font-bold border-t pt-2">
						<span>Purchase Amount:</span>
						<span class="text-amber-600 font-mono">{{
							fmtCurrency(totalAgreedValue)
						}}</span>
					</div>
				</div>
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
				@click="submit"
				:disabled="submitting || !canSubmit"
				class="flex-1 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 disabled:opacity-50"
			>
				{{
					submitting
						? 'Processing...'
						: `Purchase Gold — ${fmtCurrency(totalAgreedValue)}`
				}}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'
import CustomerSelector from './CustomerSelector.vue'

const emit = defineEmits(['close', 'completed'])

const form = reactive({
	customer: '',
	customer_name: '',
	store_location: '',
	id_type: '',
	id_number: '',
	payment_method: 'Cash',
})

const scrapItems = ref([newScrapItem()])
const storeLocations = ref([])
const submitting = ref(false)

const totalNetWeight = computed(() =>
	scrapItems.value.reduce((sum, i) => sum + (i.net_weight_g || 0), 0)
)
const totalCalculatedValue = computed(() =>
	scrapItems.value.reduce((sum, i) => sum + (i.calculated_value || 0), 0)
)
const totalAgreedValue = computed(() =>
	scrapItems.value.reduce((sum, i) => sum + (i.agreed_value || 0), 0)
)
const canSubmit = computed(
	() => form.customer && form.store_location && totalAgreedValue.value > 0
)

function newScrapItem() {
	return {
		metal_type: 'Yellow Gold',
		purity: '14Kt',
		gross_weight_g: null,
		stone_weight_g: 0,
		net_weight_g: 0,
		rate_per_gram: 0,
		calculated_value: 0,
		agreed_value: 0,
		test_method: 'XRF',
		test_result: '',
		description: '',
	}
}

function addItem() {
	scrapItems.value.push(newScrapItem())
}

function onCustomerSelect(customer) {
	form.customer = customer.name
	form.customer_name = customer.customer_name
}

async function recalcItem(idx) {
	const item = scrapItems.value[idx]
	const gross = parseFloat(item.gross_weight_g) || 0
	const stone = parseFloat(item.stone_weight_g) || 0
	if (gross <= 0) {
		item.net_weight_g = 0
		item.rate_per_gram = 0
		item.calculated_value = 0
		return
	}
	try {
		const result = await call('zevar_core.api.gold_purchase.calculate_scrap_value', {
			metal_type: item.metal_type,
			purity: item.purity,
			gross_weight_g: gross,
			stone_weight_g: stone,
		})
		item.net_weight_g = result.net_weight
		item.rate_per_gram = result.rate_per_gram
		item.calculated_value = result.calculated_value
		if (!item.agreed_value || item.agreed_value === 0) {
			item.agreed_value = result.calculated_value
		}
	} catch (e) {
		console.error('Rate calc failed', e)
	}
}

async function submit() {
	submitting.value = true
	try {
		const result = await call('zevar_core.api.gold_purchase.create_gold_purchase', {
			data: {
				customer: form.customer,
				store_location: form.store_location,
				payment_method: form.payment_method,
				id_type: form.id_type,
				id_number: form.id_number,
				items: scrapItems.value.map((i) => ({
					metal_type: i.metal_type,
					purity: i.purity,
					gross_weight_g: i.gross_weight_g,
					stone_weight_g: i.stone_weight_g,
					agreed_value: i.agreed_value,
					test_method: i.test_method,
					test_result: i.test_result,
				})),
			},
		})

		await call('zevar_core.api.gold_purchase.submit_gold_purchase', { name: result.name })

		toast({
			title: 'Gold Purchased',
			message: `${result.name} — ${fmtCurrency(totalAgreedValue.value)}`,
			icon: 'check',
			intent: 'success',
		})
		emit('completed')
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message || String(e),
			icon: 'alert-triangle',
			intent: 'error',
		})
	} finally {
		submitting.value = false
	}
}

function fmtCurrency(val) {
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
	}).format(val || 0)
}

onMounted(async () => {
	const locations = await call('frappe.client.get_list', {
		doctype: 'Store Location',
		fields: ['name', 'store_name'],
		limit_page_length: 50,
	})
	storeLocations.value = locations
})
</script>
