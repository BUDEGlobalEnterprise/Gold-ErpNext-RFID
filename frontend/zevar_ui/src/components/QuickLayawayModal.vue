<template>
	<BaseModal :show="show" max-width="max-w-xl" @close="close">
		<template #header>
			<h2 class="text-lg font-bold text-gray-900 dark:text-white">Quick Layaway</h2>
		</template>

		<!-- Success State Overlay -->
		<div
			v-if="successResult"
			class="p-10 flex flex-col items-center justify-center text-center"
		>
			<div
				class="w-20 h-20 rounded-full flex items-center justify-center mb-6 bg-green-100 dark:bg-green-900/30"
			>
				<svg
					class="w-10 h-10 text-green-600 dark:text-green-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2.5"
						d="M5 13l4 4L19 7"
					/>
				</svg>
			</div>
			<h3 class="text-xl font-bold text-green-600 dark:text-green-400 mb-2">
				Layaway Created!
			</h3>
			<p class="text-gray-500 dark:text-gray-400 mb-6">
				Contract: {{ successResult.contract_name }}
			</p>

			<div
				class="bg-gray-50 dark:bg-warm-dark-700 rounded-xl p-4 w-full mb-6 border border-gray-100 dark:border-warm-border space-y-2 text-left"
			>
				<div class="flex justify-between text-sm py-2">
					<span class="text-gray-500 dark:text-gray-400">Total Amount:</span>
					<strong class="text-gray-900 dark:text-white"
						>${{ formatAmount(successResult.total_amount) }}</strong
					>
				</div>
				<div class="flex justify-between text-sm py-2">
					<span class="text-gray-500 dark:text-gray-400">Down Payment:</span>
					<strong class="text-gray-900 dark:text-white"
						>${{ formatAmount(successResult.down_payment_amount) }}</strong
					>
				</div>
				<div class="flex justify-between text-sm py-2">
					<span class="text-gray-500 dark:text-gray-400">Balance:</span>
					<strong class="text-gray-900 dark:text-white"
						>${{ formatAmount(successResult.balance_amount) }}</strong
					>
				</div>
			</div>

			<button
				class="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
				@click="close"
			>
				Done
			</button>
		</div>

		<!-- Form Content (hidden when success) -->
		<div v-else class="p-6">
			<!-- Step 1: Customer Selection -->
			<div class="mb-6">
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
					>Customer</label
				>
				<div class="flex gap-2">
					<select
						v-model="form.customer"
						required
						:disabled="loading"
						class="flex-1 px-3 py-2.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white"
					>
						<option value="">Select customer...</option>
						<option
							v-for="customer in customers"
							:key="customer.name"
							:value="customer.name"
						>
							{{ customer.customer_name }}
						</option>
					</select>
					<button
						type="button"
						class="px-3 py-2.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-white/20 transition"
						@click="searchCustomers"
						:disabled="loading"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
							/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Step 2: Cart Items Summary -->
			<div class="mb-6">
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
					>Items ({{ cartItems.length }})</label
				>
				<div class="bg-gray-50 dark:bg-warm-dark-700 rounded-lg p-3">
					<div
						v-for="item in cartItems"
						:key="item.item_code"
						class="flex items-center py-2 border-b border-gray-100 dark:border-warm-border/50 last:border-0"
					>
						<span class="flex-1 text-sm text-gray-900 dark:text-white">{{
							item.item_name || item.item_code
						}}</span>
						<span class="text-sm text-gray-500 dark:text-gray-400 mr-4"
							>x{{ item.qty }}</span
						>
						<span class="text-sm font-medium text-green-600 dark:text-green-400"
							>${{ formatAmount(item.rate * item.qty) }}</span
						>
					</div>
					<div
						class="flex justify-between pt-3 text-sm font-semibold text-gray-900 dark:text-white"
					>
						<span>Total:</span>
						<strong>${{ formatAmount(cartTotal) }}</strong>
					</div>
				</div>
			</div>

			<!-- Step 3: Layaway Terms -->
			<div class="mb-6">
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
					>Payment Terms</label
				>
				<div class="grid grid-cols-4 gap-2">
					<button
						v-for="term in validTerms"
						:key="term"
						class="p-3 rounded-lg text-center transition-all border-2"
						:class="
							form.term_months === term
								? 'bg-blue-600/20 border-blue-500'
								: 'bg-gray-50 dark:bg-warm-dark-700 border-gray-200 dark:border-warm-border hover:border-blue-400'
						"
						@click="selectTerm(term)"
						:disabled="loading"
					>
						<span class="block text-sm font-semibold text-gray-900 dark:text-white"
							>{{ term }} months</span
						>
						<span class="block text-xs text-gray-500 dark:text-gray-400 mt-1"
							>${{ formatAmount(calculateMonthlyPayment(term)) }}/mo</span
						>
					</button>
				</div>
			</div>

			<!-- Step 4: Down Payment -->
			<div class="mb-6">
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
					>Down Payment</label
				>
				<div class="grid grid-cols-4 gap-2">
					<button
						v-for="percent in downPaymentOptions"
						:key="percent"
						class="p-3 rounded-lg text-center transition-all border-2 text-sm font-semibold text-gray-900 dark:text-white"
						:class="
							form.down_payment_percent === percent
								? 'bg-blue-600/20 border-blue-500'
								: 'bg-gray-50 dark:bg-warm-dark-700 border-gray-200 dark:border-warm-border hover:border-blue-400'
						"
						@click="form.down_payment_percent = percent"
						:disabled="loading"
					>
						{{ percent }}%
						<span class="block text-xs font-normal text-gray-500 dark:text-gray-400"
							>${{ formatAmount((cartTotal * percent) / 100) }}</span
						>
					</button>
				</div>
			</div>

			<!-- Payment Schedule Preview -->
			<div v-if="preview" class="mb-6 bg-gray-50 dark:bg-warm-dark-700 rounded-lg p-4">
				<h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
					Payment Schedule
				</h4>
				<div
					class="grid grid-cols-3 gap-2 text-xs text-gray-500 dark:text-gray-400 uppercase font-medium mb-2"
				>
					<span>Installment</span>
					<span>Due Date</span>
					<span class="text-right">Amount</span>
				</div>
				<div
					v-for="payment in preview.payment_schedule"
					:key="payment.installment"
					class="grid grid-cols-3 gap-2 text-sm py-2 border-b border-gray-100 dark:border-warm-border/50 last:border-0"
				>
					<span class="text-gray-900 dark:text-white">#{{ payment.installment }}</span>
					<span class="text-gray-700 dark:text-gray-300">{{
						formatDate(payment.due_date)
					}}</span>
					<span class="text-right text-gray-900 dark:text-white"
						>${{ formatAmount(payment.amount) }}</span
					>
				</div>
				<div
					class="flex justify-between pt-3 text-sm font-semibold text-gray-900 dark:text-white"
				>
					<span>Total:</span>
					<strong>${{ formatAmount(preview.preview.total) }}</strong>
				</div>
			</div>

			<!-- Initial Payment (Optional) -->
			<div class="mb-2">
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
					>Initial Payment (Optional)</label
				>
				<div class="relative mb-2">
					<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"
						>$</span
					>
					<input
						type="number"
						v-model.number="form.initial_payment"
						step="0.01"
						min="0"
						:max="preview?.preview?.total || cartTotal"
						placeholder="0.00"
						:disabled="loading"
						class="w-full pl-7 pr-3 py-2.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white"
					/>
				</div>
				<select
					v-model="form.initial_payment_mode"
					:disabled="loading || !form.initial_payment"
					class="w-full px-3 py-2.5 bg-gray-100 dark:bg-white/10 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white"
				>
					<option value="Cash">Cash</option>
					<option value="Credit Card">Credit Card</option>
					<option value="Debit Card">Debit Card</option>
					<option value="Check">Check</option>
				</select>
			</div>
		</div>

		<template v-if="!successResult" #footer>
			<button
				class="px-4 py-2 text-sm font-semibold text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-white/10 transition"
				@click="close"
				:disabled="loading"
			>
				Cancel
			</button>
			<button
				class="px-4 py-2 text-sm font-semibold bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
				@click="submitLayaway"
				:disabled="loading || !form.customer"
			>
				<span v-if="loading">Creating...</span>
				<span v-else>Create Layaway</span>
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { createResource, call } from 'frappe-ui'
import BaseModal from './BaseModal.vue'
import { formatDate } from '@/utils/dates.js'

// Props
const props = defineProps({
	show: { type: Boolean, default: false },
	cartItems: { type: Array, default: () => [] },
	cartTotal: { type: Number, default: 0 },
	warehouse: { type: String, default: '' },
})

const emit = defineEmits(['close', 'created'])

// State
const loading = ref(false)
const customers = ref([])
const preview = ref(null)
const successResult = ref(null)

const form = ref({
	customer: '',
	term_months: 3,
	down_payment_percent: 20,
	initial_payment: 0,
	initial_payment_mode: 'Cash',
	notes: '',
})

const validTerms = [3, 6, 9, 12]
const downPaymentOptions = [10, 20, 30, 50]

// Resources
const customersResource = createResource({
	url: 'zevar_core.api.customer.search_customers',
	auto: false,
})

const previewResource = createResource({
	url: 'zevar_core.api.quick_layaway.get_layaway_preview',
	auto: false,
})

const createLayawayFn = 'zevar_core.api.quick_layaway.create_quick_layaway'

// Computed
const cartItemsJson = computed(() =>
	JSON.stringify(
		props.cartItems.map((item) => ({
			item_code: item.item_code,
			qty: item.qty || 1,
			rate: item.rate || item.price || 0,
		}))
	)
)

// Methods
function formatAmount(amount) {
	if (!amount) return '0.00'
	return Number(amount).toFixed(2)
}

function calculateMonthlyPayment(term) {
	const downPayment = (props.cartTotal * form.value.down_payment_percent) / 100
	const balance = props.cartTotal - downPayment
	return balance / term
}

function selectTerm(term) {
	form.value.term_months = term
	fetchPreview()
}

async function searchCustomers() {
	try {
		const result = await customersResource.submit({
			query: '',
		})
		const list = result || []
		customers.value = list.map((c) => ({
			...c,
			name: c.name || c.customer_name,
			customer_name: c.display_name || c.customer_name,
		}))
	} catch (error) {
		console.error('Failed to search customers:', error)
	}
}
async function fetchPreview() {
	if (!props.cartItems.length) return

	try {
		const result = await previewResource.submit({
			items: cartItemsJson.value,
			customer: form.value.customer || 'Walk-In Customer',
			down_payment_percent: form.value.down_payment_percent,
			term_months: form.value.term_months,
		})
		preview.value = result
	} catch (error) {
		console.error('Failed to fetch preview:', error)
	}
}

async function submitLayaway() {
	if (!form.value.customer || form.value.customer === 'Walk-In Customer') {
		alert(
			'Walk-In customers are not eligible for layaway. Please select a registered customer with contact details.'
		)
		return
	}
	loading.value = true
	try {
		const rawResult = await call(createLayawayFn, {
			items: cartItemsJson.value,
			customer: form.value.customer,
			down_payment_percent: form.value.down_payment_percent,
			term_months: form.value.term_months,
			initial_payment: form.value.initial_payment,
			initial_payment_mode: form.value.initial_payment_mode,
			warehouse: props.warehouse || undefined,
			notes: form.value.notes,
		})

		const result = rawResult?.message ?? rawResult

		if (result?.success || result?.layaway_id || result?.contract_name) {
			successResult.value = result
			emit('created', result)
		}
	} catch (error) {
		console.error('Failed to create layaway:', error)
		let errorMsg = ''
		const data = error?.data || error?.response?.data || error
		if (data?._server_messages) {
			try {
				const msgs = JSON.parse(data._server_messages)
				errorMsg = msgs
					.map((m) => {
						try {
							return JSON.parse(m).message
						} catch {
							return m
						}
					})
					.join('\n')
			} catch {
				errorMsg = String(data._server_messages)
			}
		} else if (data?.exception) {
			errorMsg = data.exception
		} else if (data?.message) {
			errorMsg = data.message
		} else if (error?.message) {
			errorMsg = error.message
		} else if (typeof error === 'string') {
			errorMsg = error
		}

		if (errorMsg === 'frappe.exceptions.ValidationError' || errorMsg === 'ValidationError') {
			if (data?.exc_type === 'ValidationError') {
				errorMsg = data.exception || 'Validation Error: Please check your inputs.'
			}
		}

		alert('Failed to create layaway: ' + String(errorMsg).replace(/<[^>]+>/g, ''))
	} finally {
		loading.value = false
	}
}

function close() {
	emit('close')
	// Reset form
	form.value = {
		customer: '',
		term_months: 3,
		down_payment_percent: 20,
		initial_payment: 0,
		initial_payment_mode: 'Cash',
		notes: '',
	}
	preview.value = null
	successResult.value = null
}

// Watchers
watch(
	() => props.show,
	(newVal) => {
		if (newVal) {
			searchCustomers()
			fetchPreview()
		}
	}
)

watch(
	() => form.value.down_payment_percent,
	() => {
		fetchPreview()
	}
)

onMounted(() => {
	if (props.show) {
		searchCustomers()
		fetchPreview()
	}
})
</script>
