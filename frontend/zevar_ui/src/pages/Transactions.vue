<template>
	<AppLayout>
		<div class="h-full flex flex-col">
			<!-- Page Header -->
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="premium-title !text-2xl">Transaction History</h1>
					<p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
						View and manage past POS transactions
					</p>
				</div>
				<button
					@click="exportHistory"
					:disabled="exporting"
					class="px-4 py-2 bg-gray-100 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-warm-dark-800 transition flex items-center gap-2"
				>
					<svg
						v-if="exporting"
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
					<svg
						v-else
						class="w-4 h-4"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
						/>
					</svg>
					{{ exporting ? 'Exporting...' : 'Export CSV' }}
				</button>
			</div>

			<!-- Filters Bar -->
			<div
				class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 mb-6 border border-gray-100 dark:border-warm-border/50"
			>
				<div class="flex flex-wrap gap-3 items-end">
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>From Date</label
						>
						<input
							type="date"
							v-model="filters.from_date"
							@change="fetchSales"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
						/>
					</div>
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>To Date</label
						>
						<input
							type="date"
							v-model="filters.to_date"
							@change="fetchSales"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
						/>
					</div>
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>Customer</label
						>
						<input
							type="text"
							v-model="filters.customer"
							placeholder="Search customer..."
							@keyup.enter="fetchSales"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent w-40"
						/>
					</div>
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>Status</label
						>
						<select
							v-model="filters.status"
							@change="fetchSales"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
						>
							<option value="">All</option>
							<option value="Paid">Paid</option>
							<option value="Unpaid">Unpaid</option>
							<option value="Overdue">Overdue</option>
							<option value="Cancelled">Cancelled</option>
						</select>
					</div>
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>Search</label
						>
						<input
							type="text"
							v-model="filters.search"
							placeholder="Invoice #..."
							@keyup.enter="fetchSales"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent w-36"
						/>
					</div>
					<button
						@click="fetchSales"
						:disabled="loading"
						class="px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition disabled:opacity-50"
					>
						Search
					</button>
				</div>
			</div>

			<!-- Summary Cards -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6" v-if="summary">
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
				>
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Transactions</span
					>
					<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
						{{ summary.transaction_count }}
					</p>
				</div>
				<div
					class="bg-gradient-to-br from-[#D4AF37]/20 to-[#D4AF37]/5 rounded-xl p-4 border border-[#D4AF37]/30"
				>
					<span class="text-xs text-[#D4AF37] uppercase tracking-wider font-medium"
						>Total Sales</span
					>
					<p class="text-2xl font-bold text-[#D4AF37] mt-1">
						{{ formatCurrency(summary.total_sales) }}
					</p>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
				>
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Average Sale</span
					>
					<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
						{{ formatCurrency(summary.average_sale) }}
					</p>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
				>
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Customers</span
					>
					<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
						{{ summary.unique_customers }}
					</p>
				</div>
			</div>

			<!-- Transactions Table -->
			<div
				class="flex-1 bg-white dark:bg-warm-dark-900/50 rounded-xl border border-gray-100 dark:border-warm-border/50 overflow-hidden"
			>
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr
								class="bg-gray-50 dark:bg-warm-dark-900/50 border-b border-gray-100 dark:border-warm-border/50"
							>
								<th
									class="px-4 py-3 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Invoice #
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Date
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Customer
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Items
								</th>
								<th
									class="px-4 py-3 text-right text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Total
								</th>
								<th
									class="px-4 py-3 text-center text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Status
								</th>
								<th
									class="px-4 py-3 text-center text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Actions
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-100 dark:divide-gray-700/50">
							<tr v-if="loading">
								<td colspan="7" class="px-4 py-12 text-center">
									<div class="flex flex-col items-center gap-3">
										<div
											class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37]"
										></div>
										<span class="text-gray-500 dark:text-gray-400 text-sm"
											>Loading transactions...</span
										>
									</div>
								</td>
							</tr>
							<tr v-else-if="sales.length === 0">
								<td colspan="7" class="px-4 py-12 text-center">
									<div class="flex flex-col items-center gap-3">
										<svg
											class="w-12 h-12 text-gray-300 dark:text-gray-600"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="1.5"
												d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
											/>
										</svg>
										<span class="text-gray-500 dark:text-gray-400 text-sm"
											>No transactions found</span
										>
									</div>
								</td>
							</tr>
							<tr
								v-else
								v-for="sale in sales"
								:key="sale.name"
								@click="viewDetails(sale.name)"
								class="hover:bg-gray-50 dark:hover:bg-warm-dark-800/30 cursor-pointer transition"
							>
								<td class="px-4 py-3">
									<span class="font-mono font-bold text-[#D4AF37] text-sm">{{
										sale.name
									}}</span>
								</td>
								<td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
									{{ formatDate(sale.posting_date) }}
								</td>
								<td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
									{{ sale.customer || 'Walk-In' }}
								</td>
								<td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
									{{ sale.item_count || 1 }}
								</td>
								<td class="px-4 py-3 text-right">
									<span class="font-bold text-green-600 dark:text-green-400">{{
										formatCurrency(sale.grand_total)
									}}</span>
								</td>
								<td class="px-4 py-3 text-center">
									<span
										class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold"
										:class="getStatusClass(sale.status)"
									>
										{{ sale.status }}
									</span>
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center justify-center gap-2">
										<button
											@click.stop="viewDetails(sale.name)"
											class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-warm-dark-800 rounded-lg transition"
											title="View Details"
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
													d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
												/>
											</svg>
										</button>
										<button
											@click.stop="printInvoice(sale.name)"
											class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-warm-dark-800 rounded-lg transition"
											title="Print Receipt"
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
										</button>
									</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Pagination -->
				<div
					v-if="pagination.total_pages > 1"
					class="px-4 py-3 border-t border-gray-100 dark:border-warm-border/50 flex items-center justify-between"
				>
					<span class="text-sm text-gray-500 dark:text-gray-400">
						Showing {{ (pagination.page - 1) * 20 + 1 }} to
						{{ Math.min(pagination.page * 20, pagination.total_count) }} of
						{{ pagination.total_count }}
					</span>
					<div class="flex items-center gap-2">
						<button
							@click="goToPage(pagination.page - 1)"
							:disabled="pagination.page === 1"
							class="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 dark:border-warm-border text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
						>
							Previous
						</button>
						<button
							@click="goToPage(pagination.page + 1)"
							:disabled="pagination.page === pagination.total_pages"
							class="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 dark:border-warm-border text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
						>
							Next
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Transaction Details Modal -->
		<TransactionDetailModal
			:show="showDetailModal"
			:invoiceName="selectedInvoice"
			@close="showDetailModal = false"
		/>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import TransactionDetailModal from '@/components/TransactionDetailModal.vue'
	import { formatDate } from '@/utils/dates.js'

// State
const loading = ref(false)
const exporting = ref(false)
const sales = ref([])
const summary = ref(null)
const showDetailModal = ref(false)
const selectedInvoice = ref(null)
const pagination = ref({ page: 1, total_pages: 1, total_count: 0 })

const filters = ref({
	from_date: getDefaultFromDate(),
	to_date: getDefaultDate(),
	customer: '',
	status: '',
	search: '',
})

// Resources
const salesResource = createResource({
	url: 'zevar_core.api.sales_history.get_sales_history',
	auto: false,
})

const summaryResource = createResource({
	url: 'zevar_core.api.sales_history.get_sales_summary',
	auto: false,
})

// Methods
function getDefaultDate() {
	return new Date().toISOString().split('T')[0]
}

function getDefaultFromDate() {
	const date = new Date()
	date.setDate(date.getDate() - 30)
	return date.toISOString().split('T')[0]
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

async function fetchSales() {
	loading.value = true
	try {
		const [salesResult, summaryResult] = await Promise.all([
			salesResource.submit({
				...filters.value,
				page: pagination.value.page,
				page_size: 20,
			}),
			summaryResource.submit({
				from_date: filters.value.from_date,
				to_date: filters.value.to_date,
			}),
		])

		sales.value = salesResult.sales || []
		pagination.value = salesResult.pagination || pagination.value
		summary.value = summaryResult.summary
	} catch (error) {
		console.error('Failed to fetch sales:', error)
	} finally {
		loading.value = false
	}
}

function viewDetails(invoiceName) {
	selectedInvoice.value = invoiceName
	showDetailModal.value = true
}

function printInvoice(invoiceName) {
	window.open(`/printview?doctype=Sales Invoice&name=${invoiceName}`, '_blank')
}

function goToPage(page) {
	pagination.value.page = page
	fetchSales()
}

async function exportHistory() {
	exporting.value = true
	try {
		const result = await createResource({
			url: 'zevar_core.api.sales_history.export_sales_history',
			params: {
				from_date: filters.value.from_date,
				to_date: filters.value.to_date,
				format: 'csv',
			},
		}).fetch()

		if (result?.data) {
			// Create download link
			const blob = new Blob([result.data], { type: 'text/csv' })
			const url = window.URL.createObjectURL(blob)
			const a = document.createElement('a')
			a.href = url
			a.download = `transactions_${filters.value.from_date}_to_${filters.value.to_date}.csv`
			a.click()
			window.URL.revokeObjectURL(url)
		}
	} catch (error) {
		console.error('Export failed:', error)
		alert('Export failed. Please try again.')
	} finally {
		exporting.value = false
	}
}

// Lifecycle
onMounted(() => {
	fetchSales()
})
</script>
