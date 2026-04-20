<template>
	<Transition name="fade">
		<div class="fixed inset-0 z-[110] flex items-center justify-center p-4 sm:p-6">
			<div class="absolute inset-0 bg-gray-900/70 backdrop-blur-sm" @click="close"></div>

			<div
				class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden border border-transparent dark:border-white/10"
			>
				<!-- Header -->
				<div
					class="flex items-center justify-between p-6 border-b border-gray-100 dark:border-white/5"
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
				<div class="p-6 space-y-4">
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

					<!-- Single vs Split toggle -->
					<div class="flex rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
						<button
							@click="paymentMode = 'single'"
							class="flex-1 py-2 text-sm font-bold transition"
							:class="paymentMode === 'single'
								? 'bg-[#D4AF37]/10 text-[#D4AF37] border-b-2 border-[#D4AF37]'
								: 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'"
						>
							Single Payment
						</button>
						<button
							@click="paymentMode = 'split'"
							class="flex-1 py-2 text-sm font-bold transition"
							:class="paymentMode === 'split'
								? 'bg-[#D4AF37]/10 text-[#D4AF37] border-b-2 border-[#D4AF37]'
								: 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'"
						>
							Split Payment
						</button>
					</div>

					<!-- SINGLE PAYMENT MODE -->
					<template v-if="paymentMode === 'single'">
						<!-- Payment Amount -->
						<div>
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Payment Amount</label
							>
							<div class="relative">
								<span
									class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 font-medium"
									>$</span
								>
								<input
									type="number"
									v-model.number="paymentAmount"
									step="0.01"
									min="0.01"
									:max="balanceAmount"
									:disabled="processing"
									class="w-full pl-8 pr-4 py-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-lg font-bold text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
									placeholder="0.00"
								/>
							</div>
							<div class="flex items-center gap-2 mt-2">
								<button
									@click="paymentAmount = balanceAmount"
									:disabled="processing"
									class="flex-1 px-2 py-1.5 text-xs font-bold bg-[#D4AF37]/10 text-[#D4AF37] rounded-lg hover:bg-[#D4AF37]/20 transition disabled:opacity-50"
								>
									Pay Full Balance
								</button>
								<button
									v-for="percent in [25, 50, 75]"
									:key="percent"
									@click="setPaymentPercent(percent)"
									:disabled="processing"
									class="flex-1 px-2 py-1.5 text-xs font-bold bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition disabled:opacity-50"
								>
									{{ percent }}%
								</button>
							</div>
						</div>

						<!-- Mode of Payment -->
						<div>
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Mode of Payment</label
							>
							<div class="grid grid-cols-2 gap-2">
								<button
									v-for="mode in allPaymentModes"
									:key="mode.value"
									@click="selectedMode = mode.value"
									:disabled="processing"
									class="px-4 py-3 rounded-xl text-sm font-bold border transition flex items-center justify-center gap-2"
									:class="
										selectedMode === mode.value
											? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
											: 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300'
									"
								>
									{{ mode.label }}
								</button>
							</div>
						</div>
					</template>

					<!-- SPLIT PAYMENT MODE -->
					<template v-if="paymentMode === 'split'">
						<div>
							<div class="flex items-center justify-between mb-2">
								<label class="text-xs font-medium text-gray-700 dark:text-gray-300">Payment Methods</label>
								<button
									@click="addSplitPayment"
									:disabled="processing || splitPayments.length >= allPaymentModes.length"
									class="text-xs font-bold text-[#D4AF37] hover:underline disabled:opacity-50"
								>
									+ Add Method
								</button>
							</div>

							<div class="space-y-3">
								<div
									v-for="(sp, idx) in splitPayments"
									:key="idx"
									class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 border border-gray-100 dark:border-gray-700/50"
								>
									<div class="flex items-center gap-2 mb-2">
										<select
											v-model="sp.mode"
											:disabled="processing"
											class="flex-1 px-3 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37]"
										>
											<option v-for="mode in availableModesForSplit(idx)" :key="mode.value" :value="mode.value">
												{{ mode.label }}
											</option>
										</select>
										<button
											v-if="splitPayments.length > 1"
											@click="removeSplitPayment(idx)"
											class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
										>
											<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
											</svg>
										</button>
									</div>
									<div class="relative">
										<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
										<input
											type="number"
											v-model.number="sp.amount"
											step="0.01"
											min="0.01"
											:disabled="processing"
											class="w-full pl-7 pr-3 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-bold text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37]"
											placeholder="0.00"
										/>
									</div>
								</div>
							</div>

							<!-- Split Summary -->
							<div class="mt-3 flex items-center justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">Split Total:</span>
								<span
									class="font-bold"
									:class="splitTotal === balanceAmount ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'"
								>
									{{ formatCurrency(splitTotal) }} / {{ formatCurrency(balanceAmount) }}
								</span>
							</div>
							<div
								v-if="splitTotal !== balanceAmount"
								class="mt-1 text-xs text-red-500 dark:text-red-400"
							>
								Split total must equal the outstanding balance ({{ formatCurrency(balanceAmount) }})
							</div>
						</div>
					</template>

					<!-- Payment Summary -->
					<div
						v-if="effectivePaymentAmount > 0"
						class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-700/50"
					>
						<div class="space-y-2">
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400"
									>Payment Amount</span
								>
								<span class="text-gray-900 dark:text-white font-bold">{{
									formatCurrency(effectivePaymentAmount)
								}}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400"
									>Remaining Balance</span
								>
								<span class="text-green-600 dark:text-green-400 font-bold">{{
									formatCurrency(balanceAmount - effectivePaymentAmount)
								}}</span>
							</div>
							<div
								v-if="balanceAmount - effectivePaymentAmount <= 0"
								class="flex justify-between text-sm pt-2 border-t border-gray-200 dark:border-gray-700"
							>
								<span class="text-blue-600 dark:text-blue-400 font-medium"
									>Contract Status</span
								>
								<span class="text-blue-600 dark:text-blue-400 font-bold"
									>Will be Completed</span
								>
							</div>
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
		</div>
	</Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
	layawayId: { type: String, required: true },
	balanceAmount: { type: Number, default: 0 },
})

const emit = defineEmits(['close', 'success'])

const paymentAmount = ref(0)
const selectedMode = ref('Cash')
const processing = ref(false)
const error = ref('')
const paymentMode = ref('single')
const paymentBreakdown = ref(null)

const splitPayments = ref([
	{ mode: 'Cash', amount: 0 },
	{ mode: 'Credit Card', amount: 0 },
])

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

const splitTotal = computed(() =>
	splitPayments.value.reduce((sum, sp) => sum + (sp.amount || 0), 0)
)

const effectivePaymentAmount = computed(() =>
	paymentMode.value === 'split' ? splitTotal.value : paymentAmount.value
)

function availableModesForSplit(idx) {
	const usedModes = splitPayments.value
		.filter((_, i) => i !== idx)
		.map((sp) => sp.mode)
	return allPaymentModes.filter((m) => !usedModes.includes(m.value))
}

function addSplitPayment() {
	const unused = allPaymentModes.find(
		(m) => !splitPayments.value.some((sp) => sp.mode === m.value)
	)
	if (unused) {
		splitPayments.value.push({ mode: unused.value, amount: 0 })
	}
}

function removeSplitPayment(idx) {
	splitPayments.value.splice(idx, 1)
}

const canSubmit = computed(() => {
	if (processing.value) return false
	if (paymentMode.value === 'single') {
		return paymentAmount.value > 0 && paymentAmount.value <= props.balanceAmount && selectedMode.value
	}
	return (
		splitTotal.value === props.balanceAmount &&
		splitPayments.value.every((sp) => sp.amount > 0 && sp.mode)
	)
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
