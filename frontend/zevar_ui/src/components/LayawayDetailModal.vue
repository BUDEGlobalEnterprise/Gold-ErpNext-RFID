<template>
	<BaseModal :show="show" max-width="max-w-3xl" @close="close">
		<template #header>
			<div class="flex items-center gap-3">
				<div>
					<h2 class="text-lg font-bold text-gray-900 dark:text-white">
						Layaway Contract
					</h2>
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
						{{ layawayId }}
					</p>
				</div>
				<span
					v-if="layaway?.extension_count > 0"
					class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400"
				>
					{{ layaway.extension_count }}x Extended
				</span>
				<span
					v-if="layaway?.inventory_reserved"
					class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
				>
					Inventory Reserved
				</span>
			</div>
			<span
				class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold"
				:class="getStatusClass(layaway?.status, layaway?.is_overdue)"
			>
				{{ layaway?.is_overdue ? 'Overdue' : layaway?.status }}
			</span>
		</template>

		<!-- Content - wrapped in relative container for inner overlays -->
		<div class="relative">
			<div class="p-6 space-y-6">
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
					<!-- Visual Payment Timeline -->
					<div
						v-if="layaway.payment_schedule && layaway.payment_schedule.length > 0"
						class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex items-center justify-between mb-3">
							<span
								class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>Payment Progress</span
							>
							<span class="text-xs font-medium text-gray-500 dark:text-gray-400">
								{{ paidPaymentsCount }} /
								{{ layaway.payment_schedule.length }} payments
							</span>
						</div>
						<div
							class="flex gap-1 h-3 rounded-full overflow-hidden bg-gray-200 dark:bg-warm-dark-800"
						>
							<div
								v-for="(payment, idx) in layaway.payment_schedule"
								:key="idx"
								class="h-full transition-all duration-300"
								:style="{ width: 100 / layaway.payment_schedule.length + '%' }"
								:class="{
									'bg-green-500': payment.status === 'Paid',
									'bg-yellow-400': payment.status === 'Pending',
									'bg-red-500': payment.status === 'Overdue',
									'bg-gray-300 dark:bg-gray-600': ![
										'Paid',
										'Pending',
										'Overdue',
									].includes(payment.status),
								}"
							></div>
						</div>
						<div
							class="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400"
						>
							<span class="flex items-center gap-1">
								<span class="w-2 h-2 rounded-full bg-green-500"></span> Paid
							</span>
							<span class="flex items-center gap-1">
								<span class="w-2 h-2 rounded-full bg-yellow-400"></span> Pending
							</span>
							<span class="flex items-center gap-1">
								<span class="w-2 h-2 rounded-full bg-red-500"></span> Overdue
							</span>
						</div>
					</div>

					<!-- Customer & Contract Info -->
					<div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
						<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4">
							<span
								class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
								>Customer</span
							>
							<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
								{{ layaway.customer || 'N/A' }}
							</p>
						</div>
						<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4">
							<span
								class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
								>Contract Date</span
							>
							<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
								{{ formatDate(layaway.contract_date) }}
							</p>
						</div>
						<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4">
							<span
								class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
								>Duration</span
							>
							<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
								{{ layaway.duration_months }} months
							</p>
						</div>
						<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4">
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
						<div
							class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl overflow-hidden"
						>
							<table class="w-full">
								<thead>
									<tr
										class="border-b border-gray-100 dark:border-warm-border/50"
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
								<tbody class="divide-y divide-gray-100 dark:divide-gray-700/50">
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
						class="bg-gradient-to-br from-gray-50 to-white dark:from-gray-800/50 dark:to-gray-800/30 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
					>
						<div class="space-y-2">
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">Total Amount</span>
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
								class="flex justify-between text-lg font-bold pt-2 border-t border-gray-200 dark:border-warm-border"
							>
								<span class="text-gray-900 dark:text-white">Balance</span>
								<span class="text-orange-600 dark:text-orange-400">{{
									formatCurrency(layaway.balance_amount)
								}}</span>
							</div>
						</div>
					</div>

					<!-- Payment Schedule -->
					<div v-if="layaway.payment_schedule && layaway.payment_schedule.length > 0">
						<h3
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
						>
							Payment Schedule
						</h3>
						<div
							class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl overflow-hidden"
						>
							<table class="w-full">
								<thead>
									<tr
										class="border-b border-gray-100 dark:border-warm-border/50"
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
								<tbody class="divide-y divide-gray-100 dark:divide-gray-700/50">
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

			<!-- Cancel Confirmation Dialog (inner overlay) -->
			<div
				v-if="showCancelConfirm"
				class="absolute inset-0 bg-gray-900/80 flex items-center justify-center p-4 z-10"
			>
				<div class="bg-white dark:bg-[#1a1c23] rounded-xl p-6 max-w-md w-full">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
						Cancel Layaway?
					</h3>
					<div class="space-y-2 mb-4">
						<p class="text-sm text-gray-500 dark:text-gray-400">
							This will cancel the layaway contract. A cancellation fee will be
							deducted before issuing store credit.
						</p>
						<div
							class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-lg p-3 space-y-1.5"
						>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">Paid Amount</span>
								<span class="text-gray-900 dark:text-white font-bold">{{
									formatCurrency(layaway?.deposit_amount)
								}}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400"
									>Cancellation Fee ({{
										layaway?.cancellation_fee_percent || 10
									}}%)</span
								>
								<span class="text-red-600 dark:text-red-400 font-bold"
									>-{{ formatCurrency(cancellationFee) }}</span
								>
							</div>
							<div
								class="flex justify-between text-sm pt-1.5 border-t border-gray-200 dark:border-warm-border"
							>
								<span class="text-gray-900 dark:text-white font-medium"
									>Store Credit Issued</span
								>
								<span class="text-[#D4AF37] font-bold">{{
									formatCurrency(netRefund)
								}}</span>
							</div>
						</div>
					</div>
					<div class="flex items-center justify-end gap-3">
						<button
							@click="showCancelConfirm = false"
							class="px-4 py-2 bg-gray-100 dark:bg-warm-dark-900 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-warm-dark-800 transition"
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

			<!-- Extend Plan Dialog (inner overlay) -->
			<div
				v-if="showExtendDialog"
				class="absolute inset-0 bg-gray-900/80 flex items-center justify-center p-4 z-10"
			>
				<div class="bg-white dark:bg-[#1a1c23] rounded-xl p-6 max-w-md w-full">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
						Extend Layaway Plan
					</h3>
					<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
						Extend the payment timeline. Max 2 extensions allowed.
					</p>

					<div class="space-y-4">
						<div
							class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-200 dark:border-purple-800/30"
						>
							<div class="flex justify-between text-sm">
								<span class="text-purple-700 dark:text-purple-300"
									>Extensions Used</span
								>
								<span class="font-bold text-purple-700 dark:text-purple-300"
									>{{ layaway?.extension_count || 0 }} / 2</span
								>
							</div>
							<div
								v-if="extensionsRemaining <= 0"
								class="text-xs text-red-500 dark:text-red-400 mt-1"
							>
								No extensions remaining.
							</div>
						</div>

						<div v-if="extensionsRemaining > 0">
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Additional Months</label
							>
							<div class="grid grid-cols-3 gap-2">
								<button
									v-for="m in [1, 2, 3]"
									:key="m"
									@click="extendForm.months = m"
									class="py-3 rounded-xl text-sm font-bold border transition"
									:class="
										extendForm.months === m
											? 'border-purple-400 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300'
											: 'border-gray-200 dark:border-warm-border text-gray-600 dark:text-gray-400 hover:border-gray-300'
									"
								>
									{{ m }} Month{{ m > 1 ? 's' : '' }}
								</button>
							</div>
						</div>

						<div v-if="extensionsRemaining > 0">
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Reason</label
							>
							<textarea
								v-model="extendForm.reason"
								rows="2"
								placeholder="Reason for extension..."
								class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] resize-none"
							></textarea>
						</div>
					</div>

					<div class="flex items-center justify-end gap-3 mt-4">
						<button
							@click="showExtendDialog = false"
							class="px-4 py-2 bg-gray-100 dark:bg-warm-dark-900 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-warm-dark-800 transition"
						>
							Cancel
						</button>
						<button
							v-if="extensionsRemaining > 0"
							@click="extendLayaway"
							:disabled="extending || !extendForm.months"
							class="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-bold hover:bg-purple-700 transition disabled:opacity-50"
						>
							{{ extending ? 'Extending...' : 'Extend Plan' }}
						</button>
					</div>
				</div>
			</div>
		</div>

		<template #footer>
			<div class="flex items-center gap-2">
				<button
					v-if="layaway?.status === 'Active' || layaway?.is_overdue"
					@click="showExtendDialog = true"
					class="px-4 py-2 bg-white dark:bg-warm-dark-900 border border-purple-200 dark:border-purple-800/30 rounded-lg text-sm font-medium text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition flex items-center gap-2"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					Extend Plan
				</button>
				<button
					v-if="layaway?.status === 'Active'"
					@click="showCancelConfirm = true"
					class="px-4 py-2 bg-white dark:bg-warm-dark-900 border border-red-200 dark:border-red-800/30 rounded-lg text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition flex items-center gap-2"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
					class="px-4 py-2 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-800 transition flex items-center gap-2"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
		</template>
	</BaseModal>

	<!-- Payment Modal (rendered outside BaseModal, as its own independent modal) -->
	<CheckoutModal
		v-if="showPaymentModal"
		:show="showPaymentModal"
		mode="layaway"
		:referenceId="layawayId"
		:balanceAmount="layaway?.balance_amount || 0"
		@close="showPaymentModal = false"
		@success="handlePaymentSuccess"
	/>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { formatDate, formatDateTime } from '@/utils/dates.js'
import BaseModal from './BaseModal.vue'
import CheckoutModal from '@/components/CheckoutModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	layawayId: { type: String, default: '' },
})

const emit = defineEmits(['close', 'refresh'])

const loading = ref(false)
const layaway = ref(null)
const showCancelConfirm = ref(false)
const showPaymentModal = ref(false)
const showExtendDialog = ref(false)
const cancelling = ref(false)
const extending = ref(false)
const loadError = ref('')

const extendForm = ref({
	months: null,
	reason: '',
})

const detailsResource = createResource({
	url: 'zevar_core.api.layaway.get_layaway_details',
	auto: false,
})

const cancelResource = createResource({
	url: 'zevar_core.api.layaway.cancel_layaway',
	auto: false,
})

const extendResource = createResource({
	url: 'zevar_core.api.layaway.extend_layaway',
	auto: false,
})

const paidPaymentsCount = computed(() => {
	if (!layaway.value?.payment_schedule) return 0
	return layaway.value.payment_schedule.filter((p) => p.status === 'Paid').length
})

const extensionsRemaining = computed(() => {
	const used = layaway.value?.extension_count || 0
	return Math.max(0, 2 - used)
})

const cancellationFee = computed(() => {
	if (!layaway.value) return 0
	const percent = layaway.value.cancellation_fee_percent || 10
	return (layaway.value.deposit_amount * percent) / 100
})

const netRefund = computed(() => {
	if (!layaway.value) return 0
	return Math.max(0, (layaway.value.deposit_amount || 0) - cancellationFee.value)
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
		const result = unwrapResponse(
			await detailsResource.submit({ layaway_id: props.layawayId })
		)
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
				} generated for ${formatCurrency(
					result.amount_refunded
				)}. Cancellation fee: ${formatCurrency(result.cancellation_fee)}`
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
			errorMsg = error?.message || 'Unknown error'
		}
		errorMsg = errorMsg.replace(/<[^>]+>/g, '')
		alert('Failed to cancel layaway: ' + errorMsg)
	} finally {
		cancelling.value = false
	}
}

async function extendLayaway() {
	if (!extendForm.value.months) return
	extending.value = true
	try {
		const rawResult = await extendResource.submit({
			layaway_id: props.layawayId,
			additional_months: extendForm.value.months,
			reason: extendForm.value.reason || undefined,
		})
		const result = rawResult?.message ?? rawResult
		if (result?.success) {
			showExtendDialog.value = false
			extendForm.value = { months: null, reason: '' }
			fetchDetails()
			emit('refresh')
		}
	} catch (error) {
		console.error('Failed to extend layaway:', error)
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
			errorMsg = error?.message || 'Unknown error'
		}
		errorMsg = errorMsg.replace(/<[^>]+>/g, '')
		alert('Failed to extend layaway: ' + errorMsg)
	} finally {
		extending.value = false
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
	showExtendDialog.value = false
	extendForm.value = { months: null, reason: '' }
}

function printContract() {
	window.open(`/printview?doctype=Layaway Contract&name=${props.layawayId}`, '_blank')
}

function formatCurrency(amount) {
	if (!amount) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

function getStatusClass(status, isOverdue) {
	if (isOverdue) {
		return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
	}
	const classes = {
		Active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Completed: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
		Cancelled: 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400',
		Defaulted: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400'
}

function getPaymentStatusClass(status) {
	const classes = {
		Paid: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
		Overdue: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400'
}
</script>
