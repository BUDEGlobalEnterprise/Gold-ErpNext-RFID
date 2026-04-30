<template>
	<div class="pos-closing-page">
		<div class="page-header">
			<h1>POS Closing Entry</h1>
			<p>Close your cash register and reconcile</p>
		</div>

		<!-- No Active Session -->
		<div v-if="!sessionStatus.has_active_session && !loading" class="no-session-warning">
			<div class="warning-icon">ℹ️</div>
			<div class="warning-content">
				<h3>No Active Session</h3>
				<p>You don't have an open POS session. Please open one first.</p>
			</div>
			<router-link to="/pos/opening" class="btn btn-primary">
				Open Cash Register
			</router-link>
		</div>

		<!-- Closing Form -->
		<div v-else class="closing-form-container">
			<!-- Session Summary -->
			<div class="session-summary">
				<h3>Session Summary</h3>
				<div class="summary-grid">
					<div class="summary-item">
						<span class="label">Session ID</span>
						<span class="value">{{ sessionStatus.session?.name }}</span>
					</div>
					<div class="summary-item">
						<span class="label">Opening Balance</span>
						<span class="value"
							>${{ formatAmount(sessionStatus.session?.opening_balance) }}</span
						>
					</div>
					<div class="summary-item">
						<span class="label">Total Sales</span>
						<span class="value"
							>${{ formatAmount(sessionStatus.session?.sales_total) }}</span
						>
					</div>
					<div class="summary-item">
						<span class="label">Sales Count</span>
						<span class="value">{{ sessionStatus.session?.sales_count }}</span>
					</div>
					<div class="summary-item">
						<span class="label">Duration</span>
						<span class="value">{{ sessionStatus.session?.duration_hours }}h</span>
					</div>
					<div class="summary-item expected">
						<span class="label">Expected Balance</span>
						<span class="value">${{ formatAmount(expectedBalance) }}</span>
					</div>
				</div>
			</div>

			<form @submit.prevent="submitClosing" class="closing-form">
				<!-- Closing Balance -->
				<div class="form-group">
					<label>Actual Closing Balance</label>
					<div class="currency-input">
						<span class="currency-symbol">$</span>
						<input
							type="number"
							v-model.number="form.closing_balance"
							step="0.01"
							min="0"
							placeholder="0.00"
							required
							:disabled="loading"
							@input="calculateVariance"
						/>
					</div>
				</div>

				<!-- Cash Breakdown (Optional) -->
				<div class="form-group">
					<label>Cash Breakdown (Optional)</label>
					<div class="breakdown-grid">
						<div
							v-for="denom in denominations"
							:key="denom.value"
							class="breakdown-item"
						>
							<label>${{ denom.value }}</label>
							<input
								type="number"
								v-model.number="form.cash_breakdown[denom.value]"
								min="0"
								placeholder="0"
								@change="calculateFromBreakdown"
								:disabled="loading"
							/>
							<span class="subtotal">${{ getSubtotal(denom.value) }}</span>
						</div>
					</div>
					<div class="breakdown-total">
						<span>Calculated Total:</span>
						<strong>${{ calculatedTotal.toFixed(2) }}</strong>
					</div>
				</div>

				<!-- Variance Display -->
				<div class="variance-display" :class="varianceClass">
					<div class="variance-label">Variance</div>
					<div class="variance-amount">
						<span v-if="variance > 0">+</span>${{ formatAmount(Math.abs(variance)) }}
					</div>
					<div class="variance-status">
						{{ varianceStatus }}
					</div>
				</div>

				<!-- Notes -->
				<div class="form-group">
					<label>Closing Notes</label>
					<textarea
						v-model="form.notes"
						placeholder="Any notes about discrepancies or issues..."
						rows="3"
						:disabled="loading"
					></textarea>
				</div>

				<!-- Submit Button -->
				<div class="form-actions">
					<button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
						<span v-if="loading">Closing Session...</span>
						<span v-else>Close Cash Register</span>
					</button>
				</div>
			</form>
		</div>

		<!-- Success Message -->
		<div v-if="closingResult" class="success-overlay">
			<div class="success-card">
				<div class="success-icon">✅</div>
				<h2>Session Closed!</h2>
				<div class="closing-summary">
					<div class="summary-row">
						<span>Opening Balance:</span>
						<strong>${{ formatAmount(closingResult.opening_balance) }}</strong>
					</div>
					<div class="summary-row">
						<span>Total Sales:</span>
						<strong>${{ formatAmount(closingResult.total_sales) }}</strong>
					</div>
					<div class="summary-row">
						<span>Closing Balance:</span>
						<strong>${{ formatAmount(closingResult.closing_balance) }}</strong>
					</div>
					<div class="summary-row" :class="closingResult.variance_status">
						<span>Variance:</span>
						<strong>${{ formatAmount(Math.abs(closingResult.variance)) }}</strong>
					</div>
				</div>
				<router-link to="/pos" class="btn btn-primary"> Done </router-link>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'

// State
const loading = ref(false)
const sessionStatus = ref({ has_active_session: false })
const closingResult = ref(null)
const calculatedTotal = ref(0)
const previewData = ref(null)
const overrideRequired = ref(false)

const form = ref({
	closing_balance: 0,
	cash_breakdown: {},
	notes: '',
})

const denominations = [
	{ value: 100 },
	{ value: 50 },
	{ value: 20 },
	{ value: 10 },
	{ value: 5 },
	{ value: 1 },
	{ value: 0.25 },
	{ value: 0.1 },
	{ value: 0.05 },
	{ value: 0.01 },
]

// Computed
const expectedBalance = computed(() => {
	if (previewData.value) {
		return previewData.value.expected_cash + previewData.value.fixed_float
	}
	const opening = sessionStatus.value.session?.opening_balance || 0
	const sales = sessionStatus.value.session?.sales_total || 0
	return opening + sales
})

const variance = computed(() => {
	if (previewData.value) {
		return previewData.value.variance
	}
	return form.value.closing_balance - expectedBalance.value
})

const varianceClass = computed(() => {
	if (variance.value === 0) return 'balanced'
	if (variance.value > 0) return 'excess'
	return 'shortage'
})

const varianceStatus = computed(() => {
	if (variance.value === 0) return 'Balanced ✓'
	if (variance.value > 0) return 'Excess (Over)'
	return 'Shortage (Under)'
})

// Resources
const sessionStatusResource = createResource({
	url: 'zevar_core.api.pos_session.get_session_status',
	auto: true,
	onSuccess(data) {
		sessionStatus.value = data
	},
})

const previewCloseResource = createResource({
	url: 'zevar_core.api.pos_session.preview_close',
	auto: false,
})

const closeSessionResource = createResource({
	url: 'zevar_core.api.pos_session.close_pos_session_v2',
	auto: false,
})

// Methods
function formatAmount(amount) {
	if (amount === null || amount === undefined) return '0.00'
	return Number(amount).toFixed(2)
}

function getSubtotal(denom) {
	const count = form.value.cash_breakdown[denom] || 0
	return (count * denom).toFixed(2)
}

function calculateFromBreakdown() {
	let total = 0
	for (const denom of denominations) {
		const count = form.value.cash_breakdown[denom.value] || 0
		total += count * denom.value
	}
	calculatedTotal.value = total
	form.value.closing_balance = total
	calculateVariance()
}

let timeoutId = null
function calculateVariance() {
	if (!sessionStatus.value.session?.name) return

	clearTimeout(timeoutId)
	timeoutId = setTimeout(async () => {
		try {
			const res = await previewCloseResource.submit({
				session_name: sessionStatus.value.session?.name,
				total_cash_counted: form.value.closing_balance,
			})
			previewData.value = res

			if (Math.abs(res.variance) > res.alert_threshold) {
				overrideRequired.value = true
			} else {
				overrideRequired.value = false
			}
		} catch (err) {
			console.error(err)
		}
	}, 500)
}

async function submitClosing() {
	if (overrideRequired.value) {
		const confirmed = confirm(
			`Variance is over threshold! A manager override is required. Are you a manager?`
		)
		if (!confirmed) return
	}

	loading.value = true
	try {
		const result = await closeSessionResource.submit({
			session_name: sessionStatus.value.session?.name,
			total_cash_counted: form.value.closing_balance,
			breakdown: Object.entries(form.value.cash_breakdown)
				.filter(([_, count]) => count > 0)
				.map(([denom, count]) => ({
					mode_of_payment: 'Cash',
					denomination: parseFloat(denom),
					count: count,
					amount: count * parseFloat(denom),
				})),
			notes: form.value.notes,
		})

		if (result.success) {
			closingResult.value = result
		}
	} catch (error) {
		console.error('Failed to close session:', error)
		alert('Failed to close session: ' + (error.message || 'Unknown error'))
	} finally {
		loading.value = false
	}
}

onMounted(() => {
	// Initialize cash breakdown object
	denominations.forEach((d) => {
		if (form.value.cash_breakdown[d.value] === undefined) {
			form.value.cash_breakdown[d.value] = 0
		}
	})
})
</script>

<style scoped>
.pos-closing-page {
	padding: 24px;
	max-width: 800px;
	margin: 0 auto;
}

.page-header {
	text-align: center;
	margin-bottom: 32px;
}

.page-header h1 {
	font-size: 28px;
	font-weight: 700;
	color: white;
	margin-bottom: 8px;
}

.page-header p {
	color: rgba(255, 255, 255, 0.6);
}

.no-session-warning {
	display: flex;
	align-items: center;
	gap: 16px;
	padding: 20px;
	background: rgba(59, 130, 246, 0.1);
	border: 1px solid rgba(59, 130, 246, 0.3);
	border-radius: 12px;
}

.warning-icon {
	font-size: 32px;
}

.warning-content {
	flex: 1;
}

.warning-content h3 {
	color: #3b82f6;
	margin-bottom: 4px;
}

.warning-content p {
	color: rgba(255, 255, 255, 0.7);
}

.session-summary {
	background: rgba(255, 255, 255, 0.05);
	border: 1px solid rgba(255, 255, 255, 0.1);
	border-radius: 12px;
	padding: 20px;
	margin-bottom: 24px;
}

.session-summary h3 {
	color: white;
	margin-bottom: 16px;
	font-size: 16px;
}

.summary-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
	gap: 16px;
}

.summary-item {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.summary-item .label {
	font-size: 12px;
	color: rgba(255, 255, 255, 0.6);
}

.summary-item .value {
	font-size: 18px;
	font-weight: 600;
	color: white;
}

.summary-item.expected {
	background: rgba(59, 130, 246, 0.1);
	padding: 12px;
	border-radius: 8px;
	grid-column: span 2;
}

.closing-form-container {
	background: rgba(255, 255, 255, 0.05);
	border: 1px solid rgba(255, 255, 255, 0.1);
	border-radius: 16px;
	padding: 24px;
}

.form-group {
	margin-bottom: 24px;
}

.form-group label {
	display: block;
	color: rgba(255, 255, 255, 0.8);
	font-size: 14px;
	font-weight: 500;
	margin-bottom: 8px;
}

.form-group select,
.form-group input[type='number'],
.form-group textarea {
	width: 100%;
	padding: 12px 16px;
	background: rgba(255, 255, 255, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.2);
	border-radius: 8px;
	color: white;
	font-size: 16px;
}

.form-group select:focus,
.form-group input:focus,
.form-group textarea:focus {
	outline: none;
	border-color: #3b82f6;
}

.currency-input {
	position: relative;
}

.currency-symbol {
	position: absolute;
	left: 16px;
	top: 50%;
	transform: translateY(-50%);
	color: rgba(255, 255, 255, 0.5);
}

.currency-input input {
	padding-left: 32px;
}

.breakdown-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
	gap: 12px;
}

.breakdown-item {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.breakdown-item label {
	font-size: 12px;
	color: rgba(255, 255, 255, 0.6);
}

.breakdown-item input {
	padding: 8px 12px;
}

.subtotal {
	font-size: 12px;
	color: rgba(255, 255, 255, 0.5);
}

.breakdown-total {
	display: flex;
	justify-content: space-between;
	padding: 12px;
	background: rgba(255, 255, 255, 0.05);
	border-radius: 8px;
	margin-top: 12px;
	color: white;
}

.variance-display {
	text-align: center;
	padding: 20px;
	border-radius: 12px;
	margin-bottom: 24px;
}

.variance-display.balanced {
	background: rgba(34, 197, 94, 0.1);
	border: 1px solid rgba(34, 197, 94, 0.3);
}

.variance-display.excess {
	background: rgba(59, 130, 246, 0.1);
	border: 1px solid rgba(59, 130, 246, 0.3);
}

.variance-display.shortage {
	background: rgba(239, 68, 68, 0.1);
	border: 1px solid rgba(239, 68, 68, 0.3);
}

.variance-label {
	font-size: 12px;
	color: rgba(255, 255, 255, 0.6);
	margin-bottom: 4px;
}

.variance-amount {
	font-size: 32px;
	font-weight: 700;
	color: white;
}

.variance-display.balanced .variance-amount {
	color: #22c55e;
}
.variance-display.excess .variance-amount {
	color: #3b82f6;
}
.variance-display.shortage .variance-amount {
	color: #ef4444;
}

.variance-status {
	font-size: 14px;
	color: rgba(255, 255, 255, 0.7);
	margin-top: 4px;
}

.form-actions {
	text-align: center;
	padding-top: 16px;
}

.btn {
	padding: 12px 24px;
	border-radius: 8px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.2s;
	text-decoration: none;
	display: inline-block;
}

.btn-primary {
	background: #3b82f6;
	color: white;
	border: none;
}

.btn-primary:hover:not(:disabled) {
	background: #2563eb;
}

.btn:disabled {
	opacity: 0.6;
	cursor: not-allowed;
}

.btn-lg {
	padding: 16px 48px;
	font-size: 18px;
}

.success-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.8);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.success-card {
	background: #1e293b;
	padding: 48px;
	border-radius: 16px;
	text-align: center;
	max-width: 450px;
}

.success-icon {
	font-size: 64px;
	margin-bottom: 16px;
}

.success-card h2 {
	color: white;
	margin-bottom: 24px;
}

.closing-summary {
	text-align: left;
	margin-bottom: 24px;
}

.summary-row {
	display: flex;
	justify-content: space-between;
	padding: 12px 0;
	border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	color: rgba(255, 255, 255, 0.8);
}

.summary-row:last-child {
	border-bottom: none;
}

.summary-row.shortage {
	color: #ef4444;
}

.summary-row.excess {
	color: #3b82f6;
}
</style>
