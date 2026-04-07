<template>
	<Transition name="fade">
		<div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
			<div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="close"></div>

			<div
				class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden border border-transparent dark:border-white/10"
			>
				<!-- Header -->
				<div
					class="flex items-center justify-between p-6 border-b border-gray-100 dark:border-white/5"
				>
					<div>
						<h2 class="text-lg font-bold text-gray-900 dark:text-white">
							Create Layaway Contract
						</h2>
						<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
							Fill in all details and create the contract
						</p>
					</div>
					<button
						@click="close"
						class="p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full transition"
					>
						<svg
							class="w-5 h-5 text-gray-400"
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

				<!-- Content -->
				<div class="p-6 overflow-y-auto" style="max-height: calc(90vh - 160px)">
					<!-- Customer Selection -->
					<div class="mb-6">
						<h3
							class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
						>
							Customer
						</h3>
						<div class="relative">
							<input
								v-model="customerSearch"
								type="text"
								placeholder="Search customer by name..."
								@input="searchCustomers"
								@focus="showCustomerDropdown = true"
								class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
							/>
							<div
								v-if="showCustomerDropdown && customerResults.length > 0"
								class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto"
							>
								<button
									v-for="customer in customerResults"
									:key="customer.name"
									type="button"
									@click="selectCustomer(customer)"
									class="w-full px-4 py-3 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition border-b border-gray-100 dark:border-gray-700 last:border-0"
								>
									<span class="font-medium text-gray-900 dark:text-white">{{
										customer.customer_name
									}}</span>
									<span
										v-if="customer.mobile_no"
										class="text-gray-500 text-xs ml-2"
										>{{ customer.mobile_no }}</span
									>
								</button>
							</div>
						</div>
						<div
							v-if="selectedCustomer"
							class="mt-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/30 rounded-lg"
						>
							<p class="text-sm font-bold text-green-900 dark:text-green-200">
								{{ selectedCustomer.customer_name }}
							</p>
							<p
								v-if="selectedCustomer.mobile_no"
								class="text-xs text-green-600 dark:text-green-400"
							>
								{{ selectedCustomer.mobile_no }}
							</p>
						</div>
					</div>

					<!-- Add Items -->
					<div class="mb-6">
						<h3
							class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
						>
							Items
						</h3>
						<div class="relative mb-3">
							<input
								v-model="itemSearch"
								type="text"
								placeholder="Search items..."
								@input="searchItems"
								class="w-full px-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
							/>
						</div>
						<div
							v-if="itemResults.length > 0"
							class="grid grid-cols-2 gap-2 mb-3 max-h-32 overflow-y-auto"
						>
							<button
								v-for="item in itemResults"
								:key="item.item_code"
								type="button"
								@click="addItem(item)"
								class="p-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-[#D4AF37]/50 text-left transition"
							>
								<p
									class="text-xs font-medium text-gray-900 dark:text-white truncate"
								>
									{{ item.item_name }}
								</p>
								<p class="text-xs text-[#D4AF37] font-bold">
									${{ formatPrice(item.price) }}
								</p>
							</button>
						</div>
						<div v-if="selectedItems.length > 0" class="space-y-2">
							<div
								v-for="(item, index) in selectedItems"
								:key="item.item_code"
								class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
							>
								<div>
									<p class="text-sm font-medium text-gray-900 dark:text-white">
										{{ item.item_name }}
									</p>
									<p class="text-xs text-gray-500">{{ item.item_code }}</p>
								</div>
								<div class="flex items-center gap-3">
									<span class="text-sm font-bold text-[#D4AF37]"
										>${{ formatPrice(item.price) }}</span
									>
									<button
										@click="removeItem(index)"
										class="text-red-500 hover:text-red-600"
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
							<div class="pt-2 border-t border-gray-200 dark:border-gray-700">
								<p class="text-right font-bold text-gray-900 dark:text-white">
									Total:
									<span class="text-[#D4AF37]"
										>${{ formatPrice(totalAmount) }}</span
									>
								</p>
							</div>
						</div>
					</div>

					<!-- Terms -->
					<div class="mb-6">
						<h3
							class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
						>
							Terms
						</h3>
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>
									Initial Deposit (Min 10%)
								</label>
								<div class="relative">
									<span
										class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"
										>$</span
									>
									<input
										v-model.number="form.deposit"
										type="number"
										:min="minDeposit"
										:max="totalAmount * 0.9"
										class="w-full pl-8 pr-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
									/>
								</div>
								<p class="text-xs text-gray-500 mt-1">
									Min: ${{ formatPrice(minDeposit) }}
								</p>
							</div>
							<div>
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>
									Duration
								</label>
								<div class="grid grid-cols-4 gap-2">
									<button
										v-for="d in durations"
										:key="d.value"
										type="button"
										@click="form.duration = d.value"
										class="px-2 py-2.5 rounded-lg text-xs font-bold border transition"
										:class="
											form.duration === d.value
												? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
												: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300'
										"
									>
										{{ d.value }}mo
									</button>
								</div>
							</div>
						</div>
						<div class="mt-3">
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
							>
								Payment Method
							</label>
							<div class="grid grid-cols-3 gap-2">
								<button
									v-for="method in paymentMethods"
									:key="method.value"
									type="button"
									@click="form.paymentMethod = method.value"
									class="px-3 py-2.5 rounded-lg text-xs font-bold border transition flex flex-col items-center gap-1"
									:class="
										form.paymentMethod === method.value
											? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
											: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300'
									"
								>
									<span>{{ method.icon }}</span>
									<span>{{ method.label }}</span>
								</button>
							</div>
						</div>
					</div>

					<!-- Summary -->
					<div
						v-if="selectedCustomer && selectedItems.length > 0"
						class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-4"
					>
						<h4 class="font-bold text-gray-900 dark:text-white mb-3">Summary</h4>
						<div class="space-y-2 text-sm">
							<div class="flex justify-between">
								<span class="text-gray-500 dark:text-gray-400">Customer</span>
								<span class="font-medium text-gray-900 dark:text-white">{{
									selectedCustomer.customer_name
								}}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-500 dark:text-gray-400">Items</span>
								<span class="font-medium text-gray-900 dark:text-white"
									>{{ selectedItems.length }} items</span
								>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-500 dark:text-gray-400">Total</span>
								<span class="font-medium text-[#D4AF37]"
									>${{ formatPrice(totalAmount) }}</span
								>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-500 dark:text-gray-400">Deposit</span>
								<span class="font-medium text-green-600"
									>${{ formatPrice(form.deposit) }}</span
								>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-500 dark:text-gray-400">Balance</span>
								<span class="font-medium text-gray-900 dark:text-white"
									>${{ formatPrice(balanceAmount) }}</span
								>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-500 dark:text-gray-400">Monthly</span>
								<span class="font-medium text-gray-900 dark:text-white"
									>${{ formatPrice(monthlyPayment) }}/mo</span
								>
							</div>
						</div>
					</div>

					<label class="flex items-start gap-3 cursor-pointer">
						<input
							v-model="form.agreedToTerms"
							type="checkbox"
							class="mt-1 w-4 h-4 text-[#D4AF37] border-gray-300 rounded focus:ring-[#D4AF37]"
						/>
						<span class="text-sm text-gray-600 dark:text-gray-400">
							I confirm the customer has agreed to the layaway terms.
						</span>
					</label>
				</div>

				<!-- Footer -->
				<div
					class="flex items-center justify-end gap-3 p-6 border-t border-gray-100 dark:border-white/5 bg-gray-50 dark:bg-gray-900/30"
				>
					<button
						@click="close"
						class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
					>
						Cancel
					</button>
					<button
						@click="createLayaway"
						:disabled="submitting || !canSubmit"
						class="px-6 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
					>
						<svg
							v-if="submitting"
							class="w-4 h-4 animate-spin"
							fill="none"
							viewBox="0 0 24 24"
						>
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						{{ submitting ? 'Creating...' : 'Create Layaway' }}
					</button>
				</div>
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
	show: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'created'])

const submitting = ref(false)
const customerSearch = ref('')
const itemSearch = ref('')
const customerResults = ref([])
const itemResults = ref([])
const selectedCustomer = ref(null)
const selectedItems = ref([])
const showCustomerDropdown = ref(false)

const durations = [
	{ value: 3, label: '3 Months' },
	{ value: 6, label: '6 Months' },
	{ value: 9, label: '9 Months' },
	{ value: 12, label: '12 Months' },
]

const paymentMethods = [
	{ value: 'Cash', label: 'Cash', icon: '💵' },
	{ value: 'Card', label: 'Card', icon: '💳' },
	{ value: 'Skip', label: 'Pay Later', icon: '⏳' },
]

const form = ref({
	customer: '',
	deposit: 0,
	duration: 3,
	paymentMethod: 'Cash',
	agreedToTerms: false,
})

const totalAmount = computed(() => {
	return selectedItems.value.reduce((sum, item) => sum + (item.price || 0), 0)
})

const minDeposit = computed(() => {
	return Math.ceil(totalAmount.value * 0.1)
})

const balanceAmount = computed(() => {
	return Math.max(0, totalAmount.value - (form.value.deposit || 0))
})

const monthlyPayment = computed(() => {
	if (!form.value.duration || form.value.duration === 0) return 0
	return Math.ceil(balanceAmount.value / form.value.duration)
})

const canSubmit = computed(() => {
	return (
		selectedCustomer.value &&
		selectedItems.value.length > 0 &&
		form.value.deposit >= minDeposit.value &&
		form.value.deposit < totalAmount.value &&
		form.value.duration > 0 &&
		form.value.paymentMethod &&
		form.value.agreedToTerms
	)
})

const searchCustomersResource = createResource({
	url: 'frappe.client.get_list',
	auto: false,
})

const searchItemsResource = createResource({
	url: 'zevar_core.api.get_pos_items',
	auto: false,
})

const createLayawayResource = createResource({
	url: 'zevar_core.api.layaway.create_layaway',
	auto: false,
})

function formatPrice(price) {
	if (price == null) return '0.00'
	return Number(price).toFixed(2)
}

let customerSearchTimer
async function searchCustomers() {
	if (!customerSearch.value || customerSearch.value.length < 2) {
		customerResults.value = []
		return
	}
	clearTimeout(customerSearchTimer)
	customerSearchTimer = setTimeout(async () => {
		try {
			const result = await searchCustomersResource.submit({
				doctype: 'Customer',
				fields: ['name', 'customer_name', 'mobile_no', 'email_id'],
				filters: {
					customer_name: ['like', `%${customerSearch.value}%`],
				},
				limit_page_length: 10,
			})
			customerResults.value = result || []
		} catch (error) {
			console.error('Customer search failed:', error)
		}
	}, 300)
}

function selectCustomer(customer) {
	selectedCustomer.value = customer
	form.value.customer = customer.name
	customerSearch.value = customer.customer_name
	showCustomerDropdown.value = false
}

let itemSearchTimer
async function searchItems() {
	if (!itemSearch.value || itemSearch.value.length < 2) {
		itemResults.value = []
		return
	}
	clearTimeout(itemSearchTimer)
	itemSearchTimer = setTimeout(async () => {
		try {
			const result = await searchItemsResource.submit({
				search: itemSearch.value,
				page_length: 20,
			})
			itemResults.value = (result || []).map((item) => ({
				item_code: item.item_code,
				item_name: item.item_name,
				price: item.price || item.standard_rate || 0,
			}))
		} catch (error) {
			console.error('Item search failed:', error)
		}
	}, 300)
}

function addItem(item) {
	if (selectedItems.value.find((i) => i.item_code === item.item_code)) return
	selectedItems.value.push(item)
	form.value.deposit = Math.ceil(totalAmount.value * 0.1)
}

function removeItem(index) {
	selectedItems.value.splice(index, 1)
	form.value.deposit = Math.ceil(totalAmount.value * 0.1)
}

async function createLayaway() {
	if (!canSubmit.value) return

	submitting.value = true

	try {
		const result = await createLayawayResource.submit({
			customer: form.value.customer,
			items: JSON.stringify(
				selectedItems.value.map((item) => ({
					item_code: item.item_code,
					item_name: item.item_name,
					qty: 1,
					rate: item.price,
				}))
			),
			deposit_amount: form.value.deposit,
			duration_months: form.value.duration,
		})

		if (result?.success || result?.layaway_id) {
			emit('created', result)
			close()
		}
	} catch (error) {
		console.error('Failed to create layaway:', error)
		alert('Failed to create layaway: ' + (error.message || error?.exc || 'Unknown error'))
	} finally {
		submitting.value = false
	}
}

function close() {
	customerSearch.value = ''
	itemSearch.value = ''
	selectedCustomer.value = null
	selectedItems.value = []
	form.value = {
		customer: '',
		deposit: 0,
		duration: 3,
		paymentMethod: 'Cash',
		agreedToTerms: false,
	}
	customerResults.value = []
	itemResults.value = []
	emit('close')
}

watch(
	() => props.show,
	(isOpen) => {
		if (isOpen) {
			showCustomerDropdown.value = false
		}
	}
)

document.addEventListener('click', (e) => {
	if (!e.target.closest('.relative')) {
		showCustomerDropdown.value = false
	}
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
