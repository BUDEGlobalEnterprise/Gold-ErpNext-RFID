<template>
	<Transition name="fade">
		<div class="fixed inset-0 z-[110] flex items-center justify-center p-4 sm:p-6">
			<div class="absolute inset-0 bg-gray-900/70 backdrop-blur-sm" @click="close"></div>

			<div
				class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-md overflow-hidden border border-transparent dark:border-white/10"
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
								v-for="percent in [25, 50, 75, 100]"
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
								v-for="mode in paymentModes"
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
								<component :is="mode.icon" class="w-4 h-4" />
								{{ mode.label }}
							</button>
						</div>
					</div>

					<!-- Payment Summary -->
					<div
						v-if="paymentAmount > 0"
						class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 border border-gray-100 dark:border-gray-700/50"
					>
						<div class="space-y-2">
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400"
									>Payment Amount</span
								>
								<span class="text-gray-900 dark:text-white font-bold">{{
									formatCurrency(paymentAmount)
								}}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400"
									>Remaining Balance</span
								>
								<span class="text-green-600 dark:text-green-400 font-bold">{{
									formatCurrency(balanceAmount - paymentAmount)
								}}</span>
							</div>
							<div
								v-if="balanceAmount - paymentAmount <= 0"
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
			</div>
		</div>
	</Transition>
</template>

<script setup>
import { ref, computed, h } from 'vue'
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

const paymentModes = [
	{
		value: 'Cash',
		label: 'Cash',
		icon: () =>
			h(
				'svg',
				{ class: 'w-4 h-4', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
				[
					h('path', {
						'stroke-linecap': 'round',
						'stroke-linejoin': 'round',
						'stroke-width': '2',
						d: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
					}),
				]
			),
	},
	{
		value: 'Credit Card',
		label: 'Card',
		icon: () =>
			h(
				'svg',
				{ class: 'w-4 h-4', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
				[
					h('path', {
						'stroke-linecap': 'round',
						'stroke-linejoin': 'round',
						'stroke-width': '2',
						d: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
					}),
				]
			),
	},
	{
		value: 'Check',
		label: 'Check',
		icon: () =>
			h(
				'svg',
				{ class: 'w-4 h-4', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
				[
					h('path', {
						'stroke-linecap': 'round',
						'stroke-linejoin': 'round',
						'stroke-width': '2',
						d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
					}),
				]
			),
	},
	{
		value: 'Gift Card',
		label: 'Gift Card',
		icon: () =>
			h(
				'svg',
				{ class: 'w-4 h-4', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' },
				[
					h('path', {
						'stroke-linecap': 'round',
						'stroke-linejoin': 'round',
						'stroke-width': '2',
						d: 'M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7',
					}),
				]
			),
	},
]

const canSubmit = computed(() => {
	return (
		paymentAmount.value > 0 &&
		paymentAmount.value <= props.balanceAmount &&
		selectedMode.value &&
		!processing.value
	)
})

const paymentResource = createResource({
	url: 'zevar_core.api.layaway.process_layaway_payment',
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

	try {
		const rawResult = await paymentResource.submit({
			layaway_id: props.layawayId,
			payment_amount: paymentAmount.value,
			mode_of_payment: selectedMode.value,
		})

		// Unwrap frappe-ui response
		const result = rawResult?.message ?? rawResult

		if (result?.success) {
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
