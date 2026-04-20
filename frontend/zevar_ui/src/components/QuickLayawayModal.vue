<template>
	<div v-if="show" class="modal-overlay" @click.self="close">
		<div class="modal-content">
			<div class="modal-header">
				<h2>Quick Layaway</h2>
				<button class="close-btn" @click="close">&times;</button>
			</div>

			<div class="modal-body">
				<!-- Step 1: Customer Selection -->
				<div class="form-section">
					<label>Customer</label>
					<div class="customer-selector">
						<select v-model="form.customer" required :disabled="loading">
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
							class="btn-icon"
							@click="searchCustomers"
							:disabled="loading"
						>
							&#128269;
						</button>
					</div>
				</div>

				<!-- Step 2: Cart Items Summary -->
				<div class="form-section">
					<label>Items ({{ cartItems.length }})</label>
					<div class="items-summary">
						<div v-for="item in cartItems" :key="item.item_code" class="item-row">
							<span class="item-name">{{ item.item_name || item.item_code }}</span>
							<span class="item-qty">&times;{{ item.qty }}</span>
							<span class="item-price"
								>${{ formatAmount(item.rate * item.qty) }}</span
							>
						</div>
						<div class="items-total">
							<span>Total:</span>
							<strong>${{ formatAmount(cartTotal) }}</strong>
						</div>
					</div>
				</div>

				<!-- Step 3: Layaway Terms -->
				<div class="form-section">
					<label>Payment Terms</label>
					<div class="terms-grid">
						<button
							v-for="term in validTerms"
							:key="term.value"
							class="term-btn"
							:class="{ active: form.term_months === term.value, recommended: suggestedTerm === term.value }"
							@click="selectTerm(term.value)"
							:disabled="loading"
						>
							<span v-if="suggestedTerm === term.value" class="recommended-badge">Recommended</span>
							<span class="term-duration">{{ term.label }}</span>
							<span class="term-payment"
								>${{ formatAmount(calculateMonthlyPayment(term.value)) }}/mo</span
							>
						</button>
					</div>
				</div>

				<!-- Step 4: Down Payment -->
				<div class="form-section">
					<label>Down Payment</label>
					<div class="down-payment-options">
						<button
							v-for="percent in downPaymentOptions"
							:key="percent"
							class="dp-btn"
							:class="{ active: form.down_payment_percent === percent }"
							@click="form.down_payment_percent = percent"
							:disabled="loading"
						>
							{{ percent }}%<br />
							<span class="dp-amount"
								>${{ formatAmount((cartTotal * percent) / 100) }}</span
							>
						</button>
					</div>
				</div>

				<!-- Payment Timeline (Visual) -->
				<div class="timeline-preview" v-if="preview && preview.payment_schedule">
					<h4>Payment Timeline</h4>
					<div class="timeline-bar">
						<div class="timeline-track">
							<div
								v-for="(payment, idx) in preview.payment_schedule"
								:key="idx"
								class="timeline-segment"
								:style="{ width: (100 / preview.payment_schedule.length) + '%' }"
							>
								<div class="segment-fill"></div>
								<div class="segment-dot"></div>
								<span class="segment-label">${{ formatAmount(payment.amount) }}</span>
							</div>
						</div>
					</div>
					<div class="timeline-dates">
						<span v-if="preview.payment_schedule.length" class="timeline-start">
							{{ formatDate(preview.payment_schedule[0].due_date) }}
						</span>
						<span v-if="preview.payment_schedule.length" class="timeline-end">
							{{ formatDate(preview.payment_schedule[preview.payment_schedule.length - 1].due_date) }}
						</span>
					</div>
				</div>

				<!-- Initial Payment (Optional) -->
				<div class="form-section">
					<label>Initial Payment (Optional)</label>
					<div class="currency-input">
						<span class="currency-symbol">$</span>
						<input
							type="number"
							v-model.number="form.initial_payment"
							step="0.01"
							min="0"
							:max="preview?.preview?.total || cartTotal"
							placeholder="0.00"
							:disabled="loading"
						/>
					</div>
					<select
						v-model="form.initial_payment_mode"
						:disabled="loading || !form.initial_payment"
					>
						<option v-for="mode in paymentModeOptions" :key="mode" :value="mode">{{ mode }}</option>
					</select>
				</div>
			</div>

			<div class="modal-footer">
				<button class="btn btn-secondary" @click="close" :disabled="loading">
					Cancel
				</button>
				<button
					class="btn btn-primary"
					@click="submitLayaway"
					:disabled="loading || !form.customer"
				>
					<span v-if="loading">Creating...</span>
					<span v-else>Create Layaway</span>
				</button>
			</div>

			<!-- Success State -->
			<div v-if="successResult" class="success-overlay">
				<div class="success-content">
					<div class="success-icon">&#9989;</div>
					<h3>Layaway Created!</h3>
					<p>Contract: {{ successResult.contract_name }}</p>
					<div class="success-details">
						<div class="detail-row">
							<span>Total Amount:</span>
							<strong>${{ formatAmount(successResult.total_amount) }}</strong>
						</div>
						<div class="detail-row">
							<span>Down Payment:</span>
							<strong>${{ formatAmount(successResult.down_payment_amount) }}</strong>
						</div>
						<div class="detail-row">
							<span>Balance:</span>
							<strong>${{ formatAmount(successResult.balance_amount) }}</strong>
						</div>
					</div>
					<button class="btn btn-primary" @click="close">Done</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
	show: { type: Boolean, default: false },
	cartItems: { type: Array, default: () => [] },
	cartTotal: { type: Number, default: 0 },
	warehouse: { type: String, default: '' },
})

const emit = defineEmits(['close', 'created'])

const loading = ref(false)
const customers = ref([])
const preview = ref(null)
const successResult = ref(null)
const suggestedTerm = ref(null)

const form = ref({
	customer: '',
	term_months: 3,
	down_payment_percent: 20,
	initial_payment: 0,
	initial_payment_mode: 'Cash',
	notes: '',
})

const validTerms = [
	{ value: 1, label: '30 Days' },
	{ value: 2, label: '60 Days' },
	{ value: 3, label: '90 Days' },
	{ value: 6, label: '6 Mo' },
	{ value: 9, label: '9 Mo' },
	{ value: 12, label: '12 Mo' },
]

const downPaymentOptions = [20, 25, 30, 50]

const paymentModeOptions = [
	'Cash',
	'Credit Card',
	'Debit Card',
	'Check',
	'Apple Pay',
	'Google Pay',
	'Venmo',
	'Zelle',
]

const customersResource = createResource({
	url: 'zevar_core.api.customer.search_customers',
	auto: false,
})

const previewResource = createResource({
	url: 'zevar_core.api.quick_layaway.get_layaway_preview',
	auto: false,
})

const createResource2 = createResource({
	url: 'zevar_core.api.quick_layaway.create_quick_layaway',
	auto: false,
})

const suggestResource = createResource({
	url: 'zevar_core.api.layaway.suggest_layaway_plan',
	auto: false,
})

const cartItemsJson = computed(() =>
	JSON.stringify(
		props.cartItems.map((item) => ({
			item_code: item.item_code,
			qty: item.qty || 1,
			rate: item.rate || item.price || 0,
		}))
	)
)

function formatAmount(amount) {
	if (!amount) return '0.00'
	return Number(amount).toFixed(2)
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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

async function fetchSuggestion() {
	if (!props.cartTotal) return
	try {
		const raw = await suggestResource.submit({ total_amount: props.cartTotal })
		const result = raw?.message ?? raw
		if (result?.suggested_duration) {
			suggestedTerm.value = result.suggested_duration
			form.value.term_months = result.suggested_duration
			if (result.suggested_down_percent) {
				form.value.down_payment_percent = result.suggested_down_percent
			}
		}
	} catch (e) {
		console.error('Failed to fetch suggestion:', e)
	}
}

async function searchCustomers() {
	try {
		const result = await customersResource.submit({ search: '' })
		customers.value = result.customers || result || []
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
	loading.value = true
	try {
		const rawResult = await createResource2.submit({
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
		if (error?._server_messages) {
			try {
				const msgs = JSON.parse(error._server_messages)
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
				errorMsg = String(error._server_messages)
			}
		} else {
			errorMsg = error?.message || error?.exc || 'Unknown error'
		}
		errorMsg = errorMsg.replace(/<[^>]+>/g, '')
		alert('Failed to create layaway: ' + errorMsg)
	} finally {
		loading.value = false
	}
}

function close() {
	emit('close')
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
	suggestedTerm.value = null
}

watch(
	() => props.show,
	(newVal) => {
		if (newVal) {
			searchCustomers()
			fetchSuggestion()
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
		fetchSuggestion()
		fetchPreview()
	}
})
</script>

<style scoped>
.modal-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.7);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal-content {
	background: #1e293b;
	border-radius: 16px;
	width: 90%;
	max-width: 600px;
	max-height: 90vh;
	overflow-y: auto;
	position: relative;
}

.modal-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20px 24px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
	color: white;
	font-size: 20px;
	margin: 0;
}

.close-btn {
	background: transparent;
	border: none;
	color: rgba(255, 255, 255, 0.6);
	font-size: 24px;
	cursor: pointer;
	padding: 4px 8px;
}

.close-btn:hover {
	color: white;
}

.modal-body {
	padding: 24px;
}

.form-section {
	margin-bottom: 24px;
}

.form-section > label {
	display: block;
	color: rgba(255, 255, 255, 0.8);
	font-size: 14px;
	font-weight: 500;
	margin-bottom: 8px;
}

.customer-selector {
	display: flex;
	gap: 8px;
}

.customer-selector select {
	flex: 1;
	padding: 12px;
	background: rgba(255, 255, 255, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.2);
	border-radius: 8px;
	color: white;
}

.btn-icon {
	padding: 8px 12px;
	background: rgba(255, 255, 255, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.2);
	border-radius: 8px;
	cursor: pointer;
}

.items-summary {
	background: rgba(255, 255, 255, 0.05);
	border-radius: 8px;
	padding: 12px;
}

.item-row {
	display: flex;
	align-items: center;
	padding: 8px 0;
	border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.item-name {
	flex: 1;
	color: white;
}

.item-qty {
	color: rgba(255, 255, 255, 0.6);
	margin-right: 16px;
}

.item-price {
	color: #22c55e;
	font-weight: 500;
}

.items-total {
	display: flex;
	justify-content: space-between;
	padding-top: 12px;
	color: white;
	font-weight: 600;
}

.terms-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 8px;
}

.term-btn {
	padding: 12px;
	background: rgba(255, 255, 255, 0.05);
	border: 2px solid rgba(255, 255, 255, 0.1);
	border-radius: 8px;
	cursor: pointer;
	text-align: center;
	transition: all 0.2s;
	position: relative;
}

.term-btn:hover {
	border-color: rgba(59, 130, 246, 0.5);
}

.term-btn.active {
	background: rgba(59, 130, 246, 0.2);
	border-color: #3b82f6;
}

.term-btn.recommended {
	border-color: #D4AF37;
	background: rgba(212, 175, 55, 0.1);
}

.term-btn.recommended.active {
	background: rgba(212, 175, 55, 0.2);
	border-color: #D4AF37;
}

.recommended-badge {
	display: inline-block;
	position: absolute;
	top: -8px;
	right: -4px;
	background: #D4AF37;
	color: #000;
	font-size: 9px;
	font-weight: 700;
	padding: 1px 6px;
	border-radius: 4px;
	letter-spacing: 0.5px;
	text-transform: uppercase;
}

.term-duration {
	display: block;
	color: white;
	font-weight: 600;
	font-size: 14px;
}

.term-payment {
	display: block;
	color: rgba(255, 255, 255, 0.6);
	font-size: 12px;
	margin-top: 4px;
}

.down-payment-options {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 8px;
}

.dp-btn {
	padding: 12px;
	background: rgba(255, 255, 255, 0.05);
	border: 2px solid rgba(255, 255, 255, 0.1);
	border-radius: 8px;
	cursor: pointer;
	color: white;
	font-weight: 600;
	transition: all 0.2s;
}

.dp-btn:hover {
	border-color: rgba(59, 130, 246, 0.5);
}

.dp-btn.active {
	background: rgba(59, 130, 246, 0.2);
	border-color: #3b82f6;
}

.dp-amount {
	display: block;
	font-size: 11px;
	color: rgba(255, 255, 255, 0.6);
	font-weight: normal;
}

.timeline-preview {
	background: rgba(255, 255, 255, 0.05);
	border-radius: 8px;
	padding: 16px;
	margin-bottom: 24px;
}

.timeline-preview h4 {
	color: white;
	margin-bottom: 12px;
}

.timeline-bar {
	padding: 0 8px;
}

.timeline-track {
	display: flex;
	gap: 4px;
	position: relative;
}

.timeline-segment {
	display: flex;
	flex-direction: column;
	align-items: center;
	position: relative;
}

.segment-fill {
	width: 100%;
	height: 8px;
	background: rgba(212, 175, 55, 0.3);
	border-radius: 4px;
	position: relative;
}

.segment-dot {
	width: 12px;
	height: 12px;
	border-radius: 50%;
	background: #D4AF37;
	border: 2px solid rgba(255, 255, 255, 0.3);
	margin-top: -10px;
	position: relative;
	z-index: 1;
}

.segment-label {
	font-size: 10px;
	color: rgba(255, 255, 255, 0.6);
	margin-top: 4px;
	white-space: nowrap;
}

.timeline-dates {
	display: flex;
	justify-content: space-between;
	margin-top: 8px;
	font-size: 11px;
	color: rgba(255, 255, 255, 0.5);
}

.currency-input {
	position: relative;
	margin-bottom: 8px;
}

.currency-symbol {
	position: absolute;
	left: 12px;
	top: 50%;
	transform: translateY(-50%);
	color: rgba(255, 255, 255, 0.5);
}

.currency-input input {
	width: 100%;
	padding: 12px 12px 12px 28px;
	background: rgba(255, 255, 255, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.2);
	border-radius: 8px;
	color: white;
}

select {
	width: 100%;
	padding: 12px;
	background: rgba(255, 255, 255, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.2);
	border-radius: 8px;
	color: white;
}

.modal-footer {
	display: flex;
	justify-content: flex-end;
	gap: 12px;
	padding: 20px 24px;
	border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn {
	padding: 12px 24px;
	border-radius: 8px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.2s;
}

.btn-primary {
	background: #3b82f6;
	color: white;
	border: none;
}

.btn-primary:hover:not(:disabled) {
	background: #2563eb;
}

.btn-secondary {
	background: transparent;
	color: rgba(255, 255, 255, 0.8);
	border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.success-overlay {
	position: absolute;
	inset: 0;
	background: rgba(30, 41, 59, 0.98);
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 16px;
}

.success-content {
	text-align: center;
	padding: 24px;
}

.success-icon {
	font-size: 48px;
	margin-bottom: 16px;
}

.success-content h3 {
	color: #22c55e;
	font-size: 20px;
	margin-bottom: 8px;
}

.success-content p {
	color: rgba(255, 255, 255, 0.7);
	margin-bottom: 24px;
}

.success-details {
	text-align: left;
	background: rgba(255, 255, 255, 0.05);
	border-radius: 8px;
	padding: 16px;
	margin-bottom: 24px;
}

.detail-row {
	display: flex;
	justify-content: space-between;
	padding: 8px 0;
	color: rgba(255, 255, 255, 0.8);
}
</style>
