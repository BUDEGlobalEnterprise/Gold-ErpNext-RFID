<template>
	<Transition name="fade">
		<div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
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
							Layaway Contract
						</h2>
						<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
							{{ layawayId }}
						</p>
					</div>
					<div class="flex items-center gap-2">
						<span
							class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold"
							:class="getStatusClass(layaway?.status, layaway?.is_overdue)"
						>
							{{ layaway?.is_overdue ? 'Overdue' : layaway?.status }}
						</span>
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
				</div>

				<!-- Content -->
				<div class="overflow-y-auto p-6 space-y-6 max-h-[calc(90vh-180px)]">
					<!-- Loading State -->
					<div v-if="loading" class="py-12 text-center">
						<div
							class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-4"
						></div>
						<span class="text-gray-500 dark:text-gray-400 text-sm"
							>Loading details...</span
						>
					</div>
					<div
						v-else-if="loadError"
						class="py-12 text-center text-sm text-red-500 dark:text-red-400"
					>
						{{ loadError }}
					</div>

					<template v-else-if="layaway">
						<!-- Customer & Contract Info -->
						<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
							<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
								<span
									class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
									>Customer</span
								>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
									{{ layaway.customer || 'N/A' }}
								</p>
							</div>
							<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
								<span
									class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
									>Contract Date</span
								>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
									{{ formatDate(layaway.contract_date) }}
								</p>
							</div>
							<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
								<span
									class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
									>Duration</span
								>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
									{{ layaway.duration_months }} months
								</p>
							</div>
							<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
								<span
									class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
									>Target Date</span
								>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
									{{ formatDate(layaway.target_completion_date) }}
								</p>
							</div>
						</div>

						<!-- Items -->
						<div>
							<h3
								class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
							>
								Items
							</h3>
							<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl overflow-hidden">
								<table class="w-full">
									<thead>
										<tr
											class="border-b border-gray-100 dark:border-gray-700/50"
										>
											<th
												class="px-4 py-2 text-left text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Item
											</th>
											<th
												class="px-4 py-2 text-center text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Qty
											</th>
											<th
												class="px-4 py-2 text-right text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Rate
											</th>
											<th
												class="px-4 py-2 text-right text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Amount
											</th>
										</tr>
									</thead>
									<tbody
										class="divide-y divide-gray-100 dark:divide-gray-700/50"
									>
										<tr v-for="item in layaway.items" :key="item.item_code">
											<td
												class="px-4 py-2 text-sm text-gray-900 dark:text-white"
											>
												{{ item.item_code }}
											</td>
											<td
												class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 text-center"
											>
												{{ item.qty }}
											</td>
											<td
												class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 text-right"
											>
												{{ formatCurrency(item.rate) }}
											</td>
											<td
												class="px-4 py-2 text-sm font-bold text-gray-900 dark:text-white text-right"
											>
												{{ formatCurrency(item.amount) }}
											</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>

						<!-- Totals -->
						<div
							class="bg-gradient-to-br from-gray-50 to-white dark:from-gray-800/50 dark:to-gray-800/30 rounded-xl p-4 border border-gray-100 dark:border-gray-700/50"
						>
							<div class="space-y-2">
								<div class="flex justify-between text-sm">
									<span class="text-gray-500 dark:text-gray-400"
										>Total Amount</span
									>
									<span class="text-gray-900 dark:text-white font-bold">{{
										formatCurrency(layaway.total_amount)
									}}</span>
								</div>
								<div class="flex justify-between text-sm">
									<span class="text-gray-500 dark:text-gray-400">Paid</span>
									<span class="text-green-600 dark:text-green-400 font-bold">{{
										formatCurrency(layaway.deposit_amount)
									}}</span>
								</div>
								<div
									class="flex justify-between text-lg font-bold pt-2 border-t border-gray-200 dark:border-gray-700"
								>
									<span class="text-gray-900 dark:text-white">Balance</span>
									<span class="text-orange-600 dark:text-orange-400">{{
										formatCurrency(layaway.balance_amount)
									}}</span>
								</div>
							</div>
						</div>

						<!-- Payment Schedule -->
						<div
							v-if="layaway.payment_schedule && layaway.payment_schedule.length > 0"
						>
							<h3
								class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
							>
								Payment Schedule
							</h3>
							<div class="bg-gray-50 dark:bg-gray-800/50 rounded-xl overflow-hidden">
								<table class="w-full">
									<thead>
										<tr
											class="border-b border-gray-100 dark:border-gray-700/50"
										>
											<th
												class="px-4 py-2 text-left text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Due Date
											</th>
											<th
												class="px-4 py-2 text-right text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Expected
											</th>
											<th
												class="px-4 py-2 text-right text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Paid
											</th>
											<th
												class="px-4 py-2 text-center text-xs font-bold text-gray-500 dark:text-gray-400"
											>
												Status
											</th>
										</tr>
									</thead>
									<tbody
										class="divide-y divide-gray-100 dark:divide-gray-700/50"
									>
										<tr
											v-for="(payment, index) in layaway.payment_schedule"
											:key="index"
										>
											<td
												class="px-4 py-2 text-sm text-gray-900 dark:text-white"
											>
												{{ formatDate(payment.payment_date) }}
											</td>
											<td
												class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 text-right"
											>
												{{ formatCurrency(payment.expected_amount) }}
											</td>
											<td
												class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 text-right"
											>
												{{ formatCurrency(payment.paid_amount) }}
											</td>
											<td class="px-4 py-2 text-center">
												<span
													class="inline-flex px-2 py-0.5 rounded-full text-xs font-bold"
													:class="getPaymentStatusClass(payment.status)"
												>
													{{ payment.status }}
												</span>
											</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>
					</template>
				</div>

				<!-- Footer Actions -->
				<div
					class="flex items-center justify-between gap-3 p-4 border-t border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-gray-900/50"
				>
					<div class="flex items-center gap-2">
						<button
							v-if="layaway?.status === 'Active'"
							@click="showCancelConfirm = true"
							class="px-4 py-2 bg-white dark:bg-gray-800 border border-red-200 dark:border-red-800/30 rounded-lg text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition flex items-center gap-2"
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
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
							Cancel Layaway
						</button>
					</div>
					<div class="flex items-center gap-2">
						<button
							@click="printContract"
							class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition flex items-center gap-2"
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
									d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
								/>
							</svg>
							Print Contract
						</button>
						<button
							v-if="layaway?.status === 'Active' && layaway?.balance_amount > 0"
							@click="showPaymentModal = true"
							class="px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition flex items-center gap-2"
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
									d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
								/>
							</svg>
							Process Payment
						</button>
					</div>
				</div>
			</div>

			<!-- Cancel Confirmation Dialog -->
			<div
				v-if="showCancelConfirm"
				class="absolute inset-0 bg-gray-900/80 flex items-center justify-center p-4 z-10"
			>
				<div class="bg-white dark:bg-[#1a1c23] rounded-xl p-6 max-w-md w-full">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
						Cancel Layaway?
					</h3>
					<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
						This will cancel the layaway contract and generate a store credit for the
						paid amount of
						<strong class="text-[#D4AF37]">{{
							formatCurrency(layaway?.deposit_amount)
						}}</strong
						>.
					</p>
					<div class="flex items-center justify-end gap-3">
						<button
							@click="showCancelConfirm = false"
							class="px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition"
						>
							Keep Active
						</button>
						<button
							@click="cancelLayaway"
							:disabled="cancelling"
							class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold hover:bg-red-700 transition disabled:opacity-50"
						>
							{{ cancelling ? 'Cancelling...' : 'Confirm Cancellation' }}
						</button>
					</div>
				</div>
			</div>

			<!-- Payment Modal -->
			<LayawayPaymentModal
				v-if="showPaymentModal"
				:layawayId="layawayId"
				:balanceAmount="layaway?.balance_amount || 0"
				@close="showPaymentModal = false"
				@success="handlePaymentSuccess"
			/>
		</div>
	</Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import LayawayPaymentModal from '@/components/LayawayPaymentModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	layawayId: { type: String, default: '' },
})

const emit = defineEmits(['close', 'refresh'])

const loading = ref(false)
const layaway = ref(null)
const showCancelConfirm = ref(false)
const showPaymentModal = ref(false)
const cancelling = ref(false)
const loadError = ref('')

const detailsResource = createResource({
	url: 'zevar_core.api.layaway.get_layaway_details',
	auto: false,
})

const cancelResource = createResource({
	url: 'zevar_core.api.layaway.cancel_layaway',
	auto: false,
})

function unwrapResponse(result) {
	return result?.message ?? result
}

watch(
	() => [props.show, props.layawayId],
	([isOpen, layawayId]) => {
		if (isOpen && layawayId) {
			fetchDetails()
		}
	}
)

async function fetchDetails() {
	loading.value = true
	loadError.value = ''
	try {
		const result = unwrapResponse(await detailsResource.submit({ layaway_id: props.layawayId }))
		layaway.value = result
	} catch (error) {
		console.error('Failed to fetch layaway details:', error)
		layaway.value = null
		loadError.value = error?.message || 'Unable to load layaway details.'
	} finally {
		loading.value = false
	}
}

async function cancelLayaway() {
	cancelling.value = true
	try {
		const rawResult = await cancelResource.submit({ layaway_id: props.layawayId })
		const result = rawResult?.message ?? rawResult
		if (result?.success) {
			alert(
				`Layaway cancelled. Store Credit ${
					result.store_credit_id
				} generated for ${formatCurrency(result.amount_refunded)}`
			)
			showCancelConfirm.value = false
			emit('refresh')
			close()
		}
	} catch (error) {
		console.error('Failed to cancel layaway:', error)
		let errorMsg = ''
		if (error?._server_messages) {
			try {
				const msgs = JSON.parse(error._server_messages)
				errorMsg = msgs.map(m => { try { return JSON.parse(m).message } catch { return m } }).join('\n')
			} catch { errorMsg = String(error._server_messages) }
		} else {
			errorMsg = error?.message || 'Unknown error'
		}
		errorMsg = errorMsg.replace(/<[^>]+>/g, '')
		alert('Failed to cancel layaway: ' + errorMsg)
	} finally {
		cancelling.value = false
	}
}

function handlePaymentSuccess() {
	showPaymentModal.value = false
	fetchDetails()
	emit('refresh')
}

function close() {
	emit('close')
	layaway.value = null
	loadError.value = ''
}

function printContract() {
	window.open(`/printview?doctype=Layaway Contract&name=${props.layawayId}`, '_blank')
}

function formatCurrency(amount) {
	if (!amount) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function getStatusClass(status, isOverdue) {
	if (isOverdue) {
		return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
	}
	const classes = {
		Active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Completed: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
		Cancelled: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
		Defaulted: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
}

function getPaymentStatusClass(status) {
	const classes = {
		Paid: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
		Overdue: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
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
