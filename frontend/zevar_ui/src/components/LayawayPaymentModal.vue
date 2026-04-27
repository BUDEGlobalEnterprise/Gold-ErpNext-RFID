<template>
	<BaseModal :show="show" :max-width="paymentBreakdown ? 'max-w-md' : 'max-w-4xl'" :fixed-height="paymentBreakdown ? '' : '650px'" :show-close="false" @close="close">
		<!-- Payment Form -->
		<template v-if="!paymentBreakdown">
			<div class="flex flex-col md:flex-row h-full">
				<!-- Left Column - Balance Info -->
				<div
					class="w-full md:w-1/2 bg-gray-50 dark:bg-[#15171e] p-6 border-r border-gray-100 dark:border-warm-border/50 flex flex-col"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
							Payment Details
						</h3>
						<button
							@click="close"
							class="p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full transition"
						>
							<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</div>

					<div
						class="bg-gradient-to-br from-orange-50 to-orange-100/50 dark:from-orange-900/20 dark:to-orange-800/10 rounded-xl p-4 border border-orange-200 dark:border-orange-800/30 mb-4"
					>
						<div class="flex items-center justify-between">
							<span class="text-sm text-orange-700 dark:text-orange-300 font-medium">Outstanding Balance</span>
							<span class="text-xl font-bold text-orange-700 dark:text-orange-300">{{ formatCurrency(balanceAmount) }}</span>
						</div>
						<p v-if="layawayId" class="text-xs text-orange-600/70 dark:text-orange-400/70 mt-1">
							Layaway: {{ layawayId }}
						</p>
					</div>

					<div v-if="selectedPayments.length > 0" class="flex-1 overflow-y-auto">
						<h4 class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3">
							Payment Breakdown
						</h4>
						<div class="space-y-2">
							<div
								v-for="payment in selectedPayments"
								:key="payment.mode"
								class="flex items-center justify-between bg-white dark:bg-[#0F1115] p-3 rounded-lg border border-gray-100 dark:border-warm-border/50"
							>
								<span class="text-sm text-gray-600 dark:text-gray-300">{{ payment.mode }}</span>
								<div class="flex items-center gap-2">
									<span class="text-gray-400">$</span>
									<input
										type="number"
										v-model.number="payment.amount"
										@input="recalculateSplit(payment.mode)"
										class="w-24 px-2 py-1 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded text-right font-mono text-sm"
										min="0"
										:max="balanceAmount"
									/>
								</div>
							</div>
						</div>
						<div class="flex justify-between text-sm pt-3 mt-3 border-t border-gray-200 dark:border-warm-border">
							<span class="text-gray-500">{{ remainingAmount < 0 ? 'Change Due' : 'Remaining' }}</span>
							<span
								:class="remainingAmount === 0 ? 'text-green-500 font-bold' : remainingAmount < 0 ? 'text-orange-500 font-bold' : 'text-red-500 font-bold'"
							>
								{{ remainingAmount < 0 ? formatCurrency(Math.abs(remainingAmount)) : formatCurrency(remainingAmount) }}
							</span>
						</div>
					</div>

					<div v-else class="flex-1 flex items-center justify-center text-gray-400 dark:text-gray-600 text-sm">
						Select a payment method to begin
					</div>

					<div
						v-if="error"
						class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-3 mt-3"
					>
						<p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
					</div>
				</div>

				<!-- Right Column - Payment Methods -->
				<div
					class="w-full md:w-1/2 p-6 flex flex-col bg-white dark:bg-[#1a1c23] relative overflow-y-auto"
				>
					<div class="flex items-center justify-between mb-1">
						<h2 class="text-xl font-bold text-gray-900 dark:text-white">
							Payment
						</h2>
					</div>
					<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
						Select payment method(s). Split payments allowed.
					</p>

					<div class="space-y-2 mb-4">
						<button
							v-for="mode in allPaymentModes"
							:key="mode.value"
							@click="togglePaymentMode(mode.value)"
							class="w-full flex items-center justify-between p-3 border rounded-xl transition-all"
							:class="
								isPaymentSelected(mode.value)
									? 'border-[#D4AF37] bg-[#D4AF37]/10 ring-1 ring-[#D4AF37]'
									: 'border-gray-200 hover:border-gray-400 dark:border-warm-border dark:hover:border-white/30'
							"
						>
							<div class="flex items-center gap-3">
								<div
									class="w-8 h-8 rounded-full flex items-center justify-center"
									:class="mode.value === 'Cash' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'"
								>
									<svg v-if="mode.value === 'Cash'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
									<svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
								</div>
								<span class="font-medium text-gray-900 dark:text-white text-sm">{{ mode.label }}</span>
							</div>
							<div v-if="isPaymentSelected(mode.value)" class="w-2 h-2 rounded-full bg-green-500"></div>
						</button>
					</div>

					<div class="mt-auto">
						<button
							@click="processPayment"
							:disabled="!canSubmit || processing"
							class="w-full py-4 rounded-xl font-bold text-lg shadow-xl transition-all flex items-center justify-center gap-2 transform active:scale-95"
							:class="
								!canSubmit || processing
									? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-warm-dark-700 dark:text-gray-600'
									: 'bg-gray-900 text-white hover:bg-black dark:bg-[#D4AF37] dark:text-black dark:hover:bg-[#b5952f]'
							"
						>
							<svg
								v-if="processing"
								class="w-5 h-5 animate-spin"
								fill="none"
								viewBox="0 0 24 24"
							>
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<span v-else-if="!canSubmit">{{
								selectedPayments.length === 0 ? 'Select Payment' : 'Enter Amounts'
							}}</span>
							<span v-else>Confirm {{ formatCurrency(balanceAmount) }}</span>
						</button>
					</div>
				</div>
			</div>
		</template>

		<!-- Success State -->
		<template v-if="paymentBreakdown">
			<div
				class="p-10 flex flex-col items-center justify-center text-center w-full"
			>
				<div class="w-20 h-20 rounded-full flex items-center justify-center mb-6 bg-green-100 dark:bg-green-900/30">
					<svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
					</svg>
				</div>
				<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Payment Successful!</h2>
				<p class="text-gray-500 dark:text-gray-400 mb-6">Layaway payment has been processed.</p>

				<div class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 w-full mb-6 border border-gray-100 dark:border-warm-border/50 space-y-2">
					<div
						v-for="(p, idx) in paymentBreakdown"
						:key="idx"
						class="flex justify-between text-sm py-2"
						:class="{ 'border-t border-gray-200 dark:border-warm-border': idx > 0 }"
					>
						<span class="text-gray-500 dark:text-gray-400">{{ p.mode_of_payment }}</span>
						<span class="font-bold text-gray-900 dark:text-white">{{ formatCurrency(p.amount) }}</span>
					</div>
					<div class="flex justify-between text-sm pt-3 mt-2 border-t border-gray-200 dark:border-warm-border">
						<span class="font-bold text-gray-900 dark:text-white">Total Paid</span>
						<span class="font-bold text-[#D4AF37]">{{ formatCurrency(paymentBreakdown.reduce((s, p) => s + p.amount, 0)) }}</span>
					</div>
				</div>

				<button
					@click="close"
					class="px-8 py-3 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black rounded-xl font-bold hover:bg-gray-800 dark:hover:bg-[#b5952f] transition"
				>
					Done
				</button>
			</div>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	layawayId: { type: String, default: null },
	balanceAmount: { type: Number, default: 0 },
	draftMode: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'success'])

const processing = ref(false)
const error = ref('')
const paymentBreakdown = ref(null)

const selectedPayments = ref([])

const allPaymentModes = [
	{ value: 'Cash', label: 'Cash' },
	{ value: 'Credit Card', label: 'Credit Card' },
	{ value: 'Debit Card', label: 'Debit Card' },
	{ value: 'Check', label: 'Check' },
	{ value: 'Apple Pay', label: 'Apple Pay' },
	{ value: 'Google Pay', label: 'Google Pay' },
	{ value: 'Venmo', label: 'Venmo' },
	{ value: 'Zelle', label: 'Zelle' },
	{ value: 'Cash App', label: 'Cash App' },
	{ value: 'Gift Card', label: 'Gift Card' },
	{ value: 'Wire Transfer', label: 'Wire Transfer' },
]

const totalPaid = computed(() =>
	selectedPayments.value.reduce((sum, sp) => sum + (Number(sp.amount) || 0), 0)
)

const remainingAmount = computed(() => {
	return props.balanceAmount - totalPaid.value
})

function isPaymentSelected(mode) {
	return selectedPayments.value.some((p) => p.mode === mode)
}

function togglePaymentMode(mode) {
	const index = selectedPayments.value.findIndex((p) => p.mode === mode)
	if (index >= 0) {
		selectedPayments.value.splice(index, 1)
	} else {
		if (selectedPayments.value.length === 0) {
			selectedPayments.value.push({ mode, amount: props.balanceAmount })
		} else {
			selectedPayments.value.push({ mode, amount: null })
		}
	}
}

function recalculateSplit(changedMode) {
	const changedPayment = selectedPayments.value.find((p) => p.mode === changedMode)
	if (changedPayment) {
		changedPayment.amount = Number(Number(changedPayment.amount || 0).toFixed(2))
	}

	if (selectedPayments.value.length === 2 && changedPayment) {
		const otherPayment = selectedPayments.value.find((p) => p.mode !== changedMode)
		if (otherPayment) {
			const remaining = props.balanceAmount - changedPayment.amount
			otherPayment.amount = Number(remaining.toFixed(2))
		}
	}
}

const canSubmit = computed(() => {
	if (processing.value || selectedPayments.value.length === 0) return false
	return Math.abs(remainingAmount.value) < 0.01
})

const paymentResource = createResource({
	url: 'zevar_core.api.layaway.process_layaway_payment',
	auto: false,
})

const splitPaymentResource = createResource({
	url: 'zevar_core.api.layaway.process_split_layaway_payment',
	auto: false,
})

function setPaymentPercent(percent) {
	paymentAmount.value = Math.round(props.balanceAmount * percent) / 100
}

function formatCurrency(amount) {
	if (!amount) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

async function processPayment() {
	if (!canSubmit.value) return

	error.value = ''
	processing.value = true
	paymentBreakdown.value = null

	try {
		const payments = selectedPayments.value
			.filter((sp) => sp.amount > 0)
			.map((sp) => ({ mode_of_payment: sp.mode, amount: sp.amount }))

		if (props.draftMode) {
			emit('success', { success: true, payments })
			processing.value = false
			return
		}

		const rawResult = await splitPaymentResource.submit({
			layaway_id: props.layawayId,
			payments: JSON.stringify(payments),
		})
		const result = rawResult?.message ?? rawResult

		if (result?.success) {
			paymentBreakdown.value = result.payment_breakdown || payments
			emit('success', result)
		}
	} catch (e) {
		let errorMsg = ''
		if (e?._server_messages) {
			try {
				const msgs = JSON.parse(e._server_messages)
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
				errorMsg = String(e._server_messages)
			}
		} else {
			errorMsg = e?.message || 'Failed to process payment'
		}
		error.value = errorMsg.replace(/<[^>]+>/g, '')
		console.error('Payment failed:', e)
	} finally {
		processing.value = false
	}
}

function close() {
	emit('close')
	paymentBreakdown.value = null
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
	width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
	background: #f9fafb;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
	background: #d1d5db;
	border-radius: 4px;
}
.dark .custom-scrollbar::-webkit-scrollbar-track {
	background: #15171e;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
	background: #333;
}
</style>
