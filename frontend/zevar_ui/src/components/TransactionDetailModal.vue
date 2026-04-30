<template>
	<BaseModal :show="show" max-width="max-w-2xl" @close="close">
		<template #header>
			<div>
				<h2 class="text-lg font-bold text-gray-900 dark:text-white">
					Transaction Details
				</h2>
				<p class="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
					Invoice: {{ invoiceName }}
				</p>
			</div>
		</template>

		<!-- Content -->
		<div class="p-6 space-y-6">
			<!-- Loading State -->
			<div v-if="loading" class="py-12 text-center">
				<div
					class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-4"
				></div>
				<span class="text-gray-500 dark:text-gray-400 text-sm">Loading details...</span>
			</div>

			<template v-else-if="transaction">
				<!-- Customer & Date Info -->
				<div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
					<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4">
						<span
							class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
							>Customer</span
						>
						<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
							{{ transaction.invoice.customer || 'Walk-In' }}
						</p>
					</div>
					<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4">
						<span
							class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
							>Date</span
						>
						<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
							{{ formatDate(transaction.invoice.posting_date) }}
						</p>
					</div>
					<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4">
						<span
							class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
							>Status</span
						>
						<span
							class="inline-block mt-1 px-2.5 py-1 rounded-full text-xs font-bold"
							:class="getStatusClass(transaction.invoice.status)"
						>
							{{ transaction.invoice.status }}
						</span>
					</div>
				</div>

				<!-- Items -->
				<div>
					<h3
						class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
					>
						Items
					</h3>
					<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl overflow-hidden">
						<table class="w-full">
							<thead>
								<tr class="border-b border-gray-100 dark:border-warm-border/50">
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
								<tr v-for="item in transaction.items" :key="item.item_code">
									<td class="px-4 py-2 text-sm text-gray-900 dark:text-white">
										{{ item.item_name || item.item_code }}
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
							<span class="text-gray-500 dark:text-gray-400">Subtotal</span>
							<span class="text-gray-900 dark:text-white">{{
								formatCurrency(transaction.invoice.subtotal)
							}}</span>
						</div>
						<div
							v-if="transaction.invoice.discount > 0"
							class="flex justify-between text-sm"
						>
							<span class="text-gray-500 dark:text-gray-400">Discount</span>
							<span class="text-red-500"
								>-{{ formatCurrency(transaction.invoice.discount) }}</span
							>
						</div>
						<div class="flex justify-between text-sm">
							<span class="text-gray-500 dark:text-gray-400">Tax</span>
							<span class="text-gray-900 dark:text-white">{{
								formatCurrency(transaction.invoice.tax)
							}}</span>
						</div>
						<div
							class="flex justify-between text-lg font-bold pt-2 border-t border-gray-200 dark:border-warm-border"
						>
							<span class="text-gray-900 dark:text-white">Grand Total</span>
							<span class="text-green-600 dark:text-green-400">{{
								formatCurrency(transaction.invoice.grand_total)
							}}</span>
						</div>
					</div>
				</div>

				<!-- Payments -->
				<div v-if="transaction.payments && transaction.payments.length > 0">
					<h3
						class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
					>
						Payments
					</h3>
					<div class="space-y-2">
						<div
							v-for="payment in transaction.payments"
							:key="payment.mode_of_payment"
							class="flex justify-between items-center bg-gray-50 dark:bg-warm-dark-900/50 rounded-lg px-4 py-3"
						>
							<span class="text-sm text-gray-700 dark:text-gray-300">{{
								payment.mode_of_payment
							}}</span>
							<span class="text-sm font-bold text-gray-900 dark:text-white">{{
								formatCurrency(payment.amount)
							}}</span>
						</div>
					</div>
				</div>
			</template>
		</div>

		<template #footer>
			<button
				@click="printInvoice"
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
				Print Receipt
			</button>
			<button
				@click="viewInDesk"
				class="px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition flex items-center gap-2"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
					/>
				</svg>
				View in Desk
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import BaseModal from './BaseModal.vue'
import { formatDate } from '@/utils/dates.js'

const props = defineProps({
	show: { type: Boolean, default: false },
	invoiceName: { type: String, default: '' },
})

const emit = defineEmits(['close'])

const loading = ref(false)
const transaction = ref(null)

const detailsResource = createResource({
	url: 'zevar_core.api.sales_history.get_transaction_details',
	auto: false,
})

watch(
	() => props.show,
	(isOpen) => {
		if (isOpen && props.invoiceName) {
			fetchDetails()
		}
	}
)

async function fetchDetails() {
	loading.value = true
	try {
		const result = await detailsResource.submit({ invoice_name: props.invoiceName })
		transaction.value = result
	} catch (error) {
		console.error('Failed to fetch details:', error)
	} finally {
		loading.value = false
	}
}

function close() {
	emit('close')
	transaction.value = null
}

function printInvoice() {
	window.open(`/printview?doctype=Sales Invoice&name=${props.invoiceName}`, '_blank')
}

function viewInDesk() {
	window.open(`/app/sales-invoice/${props.invoiceName}`, '_blank')
}

function formatCurrency(amount) {
	if (!amount) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

function getStatusClass(status) {
	const classes = {
		Paid: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Unpaid: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
		Overdue: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
		Cancelled: 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400',
		Return: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400'
}
</script>
