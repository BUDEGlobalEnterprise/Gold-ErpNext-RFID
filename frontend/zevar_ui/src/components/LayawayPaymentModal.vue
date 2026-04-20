<template>
	<Teleport to="body">
		<div class="fixed inset-0 z-[110] pointer-events-none">
			<Transition
				enter-active-class="transition-opacity duration-300"
				enter-from-class="opacity-0"
				enter-to-class="opacity-100"
				leave-active-class="transition-opacity duration-300"
				leave-from-class="opacity-100"
				leave-to-class="opacity-0"
			>
				<div v-if="show" class="absolute inset-0 bg-gray-900/70 backdrop-blur-sm pointer-events-auto" @click="close"></div>
			</Transition>

			<Transition
				enter-active-class="transform transition-transform duration-300 ease-in-out"
				enter-from-class="translate-x-full"
				enter-to-class="translate-x-0"
				leave-active-class="transform transition-transform duration-300 ease-in-out"
				leave-from-class="translate-x-0"
				leave-to-class="translate-x-full"
			>
				<div
					v-if="show"
					class="absolute top-0 right-0 h-full w-full sm:w-[400px] bg-white dark:bg-[#1a1c23] shadow-2xl flex flex-col border-l border-gray-200 dark:border-white/10 pointer-events-auto"
				>
					<!-- Header -->
					<div
						class="flex items-center justify-between p-6 border-b border-gray-100 dark:border-white/5 flex-shrink-0"
					>
						<div>
							<h2 class="text-lg font-bold text-gray-900 dark:text-white">
								Process Payment
							</h2>
							<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
								Layaway: {{ layawayId }}
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
					<div class="p-6 space-y-4 flex-1 overflow-y-auto custom-scrollbar">
					<!-- Balance Info -->
					<div
						class="bg-gradient-to-br from-orange-50 to-orange-100/50 dark:from-orange-900/20 dark:to-orange-800/10 rounded-xl p-4 border border-orange-200 dark:border-orange-800/30"
					>
						<div class="flex items-center justify-between">
							<span class="text-sm text-orange-700 dark:text-orange-300 font-medium"
								>Outstanding Balance</span
							>
							<span class="text-xl font-bold text-orange-700 dark:text-orange-300">{{
								formatCurrency(balanceAmount)
							}}</span>
						</div>
					</div>

					<!-- Payment Methods -->
					<div class="space-y-2 mb-4">
						<button
							v-for="mode in allPaymentModes"
							:key="mode.value"
							@click="togglePaymentMode(mode.value)"
							class="w-full flex items-center justify-between p-3 border rounded-xl transition-all"
							:class="
								isPaymentSelected(mode.value)
									? 'border-[#D4AF37] bg-[#D4AF37]/10 ring-1 ring-[#D4AF37]'
									: 'border-gray-200 hover:border-gray-400 dark:border-white/10 dark:hover:border-white/30'
							"
						>
							<div class="flex items-center gap-3">
								<div
									class="w-8 h-8 rounded-full flex items-center justify-center"
									:class="
										mode.value === 'Cash'
											? 'bg-green-100 text-green-600'
											: 'bg-blue-100 text-blue-600'
									"
								>
									<svg v-if="mode.value === 'Cash'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
									<svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
								</div>
								<span class="font-medium text-gray-900 dark:text-white text-sm">{{ mode.label }}</span>
							</div>
							<div v-if="isPaymentSelected(mode.value)" class="w-2 h-2 rounded-full bg-green-500"></div>
						</button>
					</div>

					<!-- Payment Amounts -->
					<div
						v-if="selectedPayments.length > 0"
						class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 mb-4 border border-gray-100 dark:border-white/5"
					>
						<h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
							Amounts
						</h4>
						<div
							v-for="payment in selectedPayments"
							:key="payment.mode"
							class="flex items-center justify-between mb-2"
						>
							<span class="text-sm text-gray-600 dark:text-gray-300">{{ payment.mode }}</span>
							<div class="flex items-center gap-2">
								<span class="text-gray-400">$</span>
								<input
									type="number"
									v-model.number="payment.amount"
									@input="recalculateSplit(payment.mode)"
									class="w-24 px-2 py-1 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded text-right font-mono text-sm"
									min="0"
									:max="balanceAmount"
								/>
							</div>
						</div>
						<div class="flex justify-between text-sm pt-2 border-t border-gray-200 dark:border-white/10 mt-2">
							<span class="text-gray-500">{{ remainingAmount < 0 ? 'Change Due' : 'Remaining' }}</span>
							<span
								:class="remainingAmount === 0 ? 'text-green-500 font-bold' : remainingAmount < 0 ? 'text-orange-500 font-bold' : 'text-red-500 font-bold'"
							>
								{{ remainingAmount < 0 ? formatCurrency(Math.abs(remainingAmount)) : formatCurrency(remainingAmount) }}
							</span>
						</div>
					</div>

					<!-- Error Message -->
					<div
						v-if="error"
						class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-3"
					>
						<p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
					</div>
				</div>

				<!-- Footer -->
				<div
					class="flex items-center justify-end gap-3 p-4 border-t border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-gray-900/50"
				>
					<button
						@click="close"
						:disabled="processing"
						class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition disabled:opacity-50"
					>
						Cancel
					</button>
					<button
						@click="processPayment"
						:disabled="!canSubmit || processing"
						class="px-6 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
					>
						<svg
							v-if="processing"
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
						{{ processing ? 'Processing...' : 'Confirm Payment' }}
					</button>
				</div>

				<!-- Payment Breakdown (shown after split payment success) -->
				<div
					v-if="paymentBreakdown"
					class="absolute inset-0 bg-white dark:bg-[#1a1c23] rounded-2xl flex items-center justify-center p-6 z-10"
				>
					<div class="text-center w-full">
						<div class="w-12 h-12 mx-auto mb-4 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
							<svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
							</svg>
						</div>
						<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Payment Successful</h3>
						<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 mb-4 text-left">
							<div
								v-for="(p, idx) in paymentBreakdown"
								:key="idx"
								class="flex justify-between text-sm py-2"
								:class="{ 'border-t border-gray-200 dark:border-gray-700': idx > 0 }"
							>
								<span class="text-gray-500 dark:text-gray-400">{{ p.mode_of_payment }}</span>
								<span class="font-bold text-gray-900 dark:text-white">{{ formatCurrency(p.amount) }}</span>
							</div>
							<div class="flex justify-between text-sm pt-3 mt-2 border-t border-gray-200 dark:border-gray-700">
								<span class="font-bold text-gray-900 dark:text-white">Total Paid</span>
								<span class="font-bold text-[#D4AF37]">{{ formatCurrency(paymentBreakdown.reduce((s, p) => s + p.amount, 0)) }}</span>
							</div>
						</div>
						<button
							@click="close"
							class="px-6 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition"
						>
							Done
						</button>
					</div>
				</div>
				</div>
			</Transition>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
	show: { type: Boolean, default: false },
	layawayId: { type: String, required: true },
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
		if (props.draftMode) {
			const payments = paymentMode.value === 'split'
				? splitPayments.value.filter((sp) => sp.amount > 0).map((sp) => ({ mode_of_payment: sp.mode, amount: sp.amount }))
				: [{ mode_of_payment: selectedMode.value, amount: paymentAmount.value }]

			emit('success', { success: true, payments })
			processing.value = false
			return
		}

		if (paymentMode.value === 'split') {
			const payments = splitPayments.value
				.filter((sp) => sp.amount > 0)
				.map((sp) => ({ mode_of_payment: sp.mode, amount: sp.amount }))

			const rawResult = await splitPaymentResource.submit({
				layaway_id: props.layawayId,
				payments: JSON.stringify(payments),
			})
			const result = rawResult?.message ?? rawResult

			if (result?.success) {
				paymentBreakdown.value = result.payment_breakdown || payments
				emit('success', result)
			}
		} else {
			const rawResult = await paymentResource.submit({
				layaway_id: props.layawayId,
				payment_amount: paymentAmount.value,
				mode_of_payment: selectedMode.value,
			})
			const result = rawResult?.message ?? rawResult

			if (result?.success) {
				emit('success', result)
			}
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
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
