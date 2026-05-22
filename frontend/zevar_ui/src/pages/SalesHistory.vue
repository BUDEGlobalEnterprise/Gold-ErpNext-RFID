<template>
	<AppLayout>
		<div class="flex flex-col">
			<!-- Page Header -->
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div>
					<h1 class="premium-title !text-2xl">Sales History</h1>
					<p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
						View and manage past transactions
						<span
							v-if="isOwnSalesOnly"
							class="text-xs text-amber-600 dark:text-amber-400 ml-2"
						>
							(Showing your sales only)
						</span>
					</p>
				</div>
				<div class="flex items-center gap-2 self-end sm:self-auto">
					<button
						v-if="sales.length > 0"
						@click="exportCSV"
						class="px-3 py-1.5 text-xs font-bold text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition flex items-center gap-1.5 whitespace-nowrap"
						title="Export to CSV"
					>
						<svg
							class="w-3.5 h-3.5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						Export
					</button>
					<ViewToggle v-model="viewMode" storage-key="zevar_sales_view" />
				</div>
			</div>

			<!-- Filters -->
			<div class="mb-6">
				<TransactionFilterBar />
			</div>

			<!-- Summary Cards -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 flex-shrink-0" v-if="summary">
				<div class="premium-card !p-4">
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
						${{ formatAmount(summary.total_sales) }}
					</p>
				</div>
				<div class="premium-card !p-4">
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Average Sale</span
					>
					<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
						${{ formatAmount(summary.average_sale) }}
					</p>
				</div>
				<div class="premium-card !p-4">
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Customers</span
					>
					<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
						{{ summary.unique_customers }}
					</p>
				</div>
			</div>

			<!-- Grid View -->
			<div
				v-if="viewMode === 'grid'"
				class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar"
			>
				<div v-if="loading" class="flex items-center justify-center py-20">
					<div
						class="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-[#D4AF37]"
					></div>
				</div>
				<div v-else-if="sales.length === 0" class="flex items-center justify-center py-20">
					<p class="text-gray-400 text-sm">No transactions found</p>
				</div>
				<div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3.5">
					<div
						v-for="sale in sales"
						:key="sale.name"
						class="bg-white dark:bg-warm-dark-800 rounded-xl border border-gray-100 dark:border-warm-border/50 p-3.5 hover:shadow-md hover:border-[#D4AF37]/40 dark:hover:border-[#D4AF37]/30 transition-all duration-200 cursor-pointer flex flex-col group min-w-0"
						@click="viewDetails(sale.name)"
					>
						<!-- Header -->
						<div class="flex items-start justify-between gap-1 mb-2.5 min-w-0">
							<div class="min-w-0">
								<span class="font-mono text-[10px] font-bold text-[#D4AF37]">{{
									sale.name
								}}</span>
								<p class="text-xs font-bold text-gray-900 dark:text-white mt-0.5 truncate leading-tight">
									{{ sale.customer || 'Walk-In' }}
								</p>
							</div>
							<span
								class="inline-flex px-1.5 py-0.5 rounded-full text-[9px] font-bold shrink-0"
								:class="getStatusClass(sale.status)"
							>
								{{ sale.status }}
							</span>
						</div>

						<!-- Details grid -->
						<div class="grid grid-cols-2 gap-2 mb-2.5">
							<div>
								<span class="text-[9px] uppercase font-bold text-gray-400 dark:text-gray-500"
									>Date</span
								>
								<p class="text-xs text-gray-700 dark:text-gray-300 truncate">
									{{ formatDate(sale.posting_date) }}
								</p>
							</div>
							<div>
								<span class="text-[9px] uppercase font-bold text-gray-400 dark:text-gray-500"
									>Items</span
								>
								<p class="text-xs font-mono font-bold text-gray-700 dark:text-gray-300">
									{{ sale.item_count || 1 }}
								</p>
							</div>
						</div>

						<!-- Footer -->
						<div
							class="flex items-center justify-between mt-auto pt-2 border-t border-gray-50 dark:border-warm-border/30 min-w-0"
						>
							<span class="text-base font-mono font-extrabold text-green-600 dark:text-green-400"
								>${{ formatAmount(sale.grand_total) }}</span
							>
							<button
								class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-400 hover:text-gray-600 dark:hover:text-white transition opacity-0 group-hover:opacity-100 shrink-0"
							>
								<svg
									class="w-3.5 h-3.5"
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
						</div>
					</div>
				</div>
				<div
					v-if="pagination.page < pagination.total_pages"
					class="flex items-center justify-center pt-6 pb-4"
				>
					<button
						@click="loadMore"
						:disabled="loading"
						class="px-6 py-2.5 text-sm font-bold rounded-lg border-2 border-[#D4AF37] text-[#D4AF37] hover:bg-[#D4AF37] hover:text-black disabled:opacity-50 transition"
					>
						{{ loading ? 'Loading...' : 'Load More' }}
					</button>
				</div>
			</div>

			<!-- Sales Table -->
			<div
				v-if="viewMode === 'list'"
				class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar flex flex-col"
			>
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl border border-gray-100 dark:border-warm-border/50 mb-6"
				>
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead>
								<tr
									class="bg-gray-50 dark:bg-warm-dark-900/50 border-b border-gray-100 dark:border-warm-border/50"
								>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
									>
										Invoice #
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
									>
										Date
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
									>
										Customer
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
									>
										Items
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
									>
										Total
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
									>
										Status
									</th>
									<th
										class="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
									>
										Actions
									</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-50 dark:divide-gray-700/30">
								<tr v-if="loading">
									<td
										colspan="7"
										class="px-4 py-12 text-center text-gray-500 dark:text-gray-400"
									>
										<div
											class="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
										></div>
										Loading transactions...
									</td>
								</tr>
								<tr v-else-if="sales.length === 0">
									<td
										colspan="7"
										class="px-4 py-12 text-center text-gray-500 dark:text-gray-400"
									>
										No transactions found
									</td>
								</tr>
								<tr
									v-for="sale in sales"
									:key="sale.name"
									@click="viewDetails(sale.name)"
									class="hover:bg-gray-50 dark:hover:bg-warm-dark-700 cursor-pointer transition"
								>
									<td class="px-4 py-3 text-sm font-semibold text-[#D4AF37]">
										{{ sale.name }}
									</td>
									<td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
										{{ formatDate(sale.posting_date) }}
									</td>
									<td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
										{{ sale.customer }}
									</td>
									<td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">
										{{ sale.item_count || 1 }}
									</td>
									<td
										class="px-4 py-3 text-sm font-semibold text-green-600 dark:text-green-400"
									>
										${{ formatAmount(sale.grand_total) }}
									</td>
									<td class="px-4 py-3">
										<span
											class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold"
											:class="getStatusClass(sale.status)"
										>
											{{ sale.status }}
										</span>
									</td>
									<td class="px-4 py-3">
										<div class="flex items-center gap-1">
											<button
												class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700 transition text-gray-400 hover:text-gray-600 dark:hover:text-white"
												@click.stop="viewDetails(sale.name)"
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
												class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700 transition text-gray-400 hover:text-gray-600 dark:hover:text-white"
												@click.stop="printInvoice(sale.name)"
												title="Print"
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
				</div>

				<!-- Load More Pagination -->
				<div
					v-if="pagination.page < pagination.total_pages"
					class="flex items-center justify-center pt-6 pb-8"
				>
					<button
						@click="loadMore"
						:disabled="loading"
						class="px-6 py-2.5 text-sm font-bold rounded-lg border-2 border-[#D4AF37] text-[#D4AF37] hover:bg-[#D4AF37] hover:text-black disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
					>
						<svg
							v-if="loading"
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
						{{ loading ? 'Loading...' : 'Load More' }}
					</button>
				</div>

				<div
					v-else-if="sales.length > 0"
					class="text-center pt-6 pb-8 text-sm text-gray-500 dark:text-gray-400"
				>
					Showing all {{ sales.length }} transactions
				</div>
			</div>

			<!-- Transaction Details Modal -->
			<div
				v-if="selectedTransaction"
				class="fixed inset-0 z-[100] flex items-center justify-center p-4"
			>
				<div
					class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm"
					@click="selectedTransaction = null"
				></div>
				<div
					class="relative bg-white dark:bg-warm-card rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden border border-gray-200 dark:border-warm-border"
				>
					<div
						class="flex items-center justify-between p-5 border-b border-gray-100 dark:border-warm-border/50"
					>
						<h2 class="text-lg font-bold text-gray-900 dark:text-white">
							Invoice {{ selectedTransaction.invoice.name }}
						</h2>
						<button
							@click="selectedTransaction = null"
							class="p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full transition"
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

					<div class="p-5 overflow-y-auto max-h-[calc(90vh-140px)]">
						<div class="grid grid-cols-3 gap-4 mb-6">
							<div>
								<span class="text-xs text-gray-500 dark:text-gray-400 font-medium"
									>Customer</span
								>
								<p
									class="text-sm font-semibold text-gray-900 dark:text-white mt-0.5"
								>
									{{ selectedTransaction.invoice.customer }}
								</p>
							</div>
							<div>
								<span class="text-xs text-gray-500 dark:text-gray-400 font-medium"
									>Date & Time</span
								>
								<p
									class="text-sm font-semibold text-gray-900 dark:text-white mt-0.5"
								>
									{{ formatDate(selectedTransaction.invoice.posting_date) }}
									{{ selectedTransaction.invoice.posting_time }}
								</p>
							</div>
							<div>
								<span class="text-xs text-gray-500 dark:text-gray-400 font-medium"
									>Status</span
								>
								<p class="mt-0.5">
									<span
										class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold"
										:class="getStatusClass(selectedTransaction.invoice.status)"
									>
										{{ selectedTransaction.invoice.status }}
									</span>
								</p>
							</div>
						</div>

						<h4
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2"
						>
							Items
						</h4>
						<div
							class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl overflow-hidden mb-6"
						>
							<table class="w-full text-sm">
								<thead>
									<tr
										class="border-b border-gray-200 dark:border-warm-border/50"
									>
										<th
											class="px-3 py-2 text-left text-xs text-gray-500 dark:text-gray-400"
										>
											Item
										</th>
										<th
											class="px-3 py-2 text-left text-xs text-gray-500 dark:text-gray-400"
										>
											Qty
										</th>
										<th
											class="px-3 py-2 text-left text-xs text-gray-500 dark:text-gray-400"
										>
											Rate
										</th>
										<th
											class="px-3 py-2 text-left text-xs text-gray-500 dark:text-gray-400"
										>
											Amount
										</th>
									</tr>
								</thead>
								<tbody>
									<tr
										v-for="item in selectedTransaction.items"
										:key="item.item_code"
										class="border-b border-gray-100 dark:border-gray-800/50 last:border-0"
									>
										<td class="px-3 py-2 text-gray-900 dark:text-white">
											{{ item.item_name || item.item_code }}
										</td>
										<td class="px-3 py-2 text-gray-700 dark:text-gray-300">
											{{ item.qty }}
										</td>
										<td class="px-3 py-2 text-gray-700 dark:text-gray-300">
											${{ formatAmount(item.rate) }}
										</td>
										<td
											class="px-3 py-2 font-semibold text-gray-900 dark:text-white"
										>
											${{ formatAmount(item.amount) }}
										</td>
									</tr>
								</tbody>
							</table>
						</div>

						<div
							class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-4 mb-6 space-y-2"
						>
							<div
								class="flex justify-between text-sm text-gray-600 dark:text-gray-400"
							>
								<span>Subtotal:</span>
								<span
									>${{
										formatAmount(selectedTransaction.invoice.subtotal)
									}}</span
								>
							</div>
							<div
								v-if="selectedTransaction.invoice.discount > 0"
								class="flex justify-between text-sm text-gray-600 dark:text-gray-400"
							>
								<span>Discount:</span>
								<span
									>-${{
										formatAmount(selectedTransaction.invoice.discount)
									}}</span
								>
							</div>
							<div
								class="flex justify-between text-sm text-gray-600 dark:text-gray-400"
							>
								<span>Tax:</span>
								<span>${{ formatAmount(selectedTransaction.invoice.tax) }}</span>
							</div>
							<div
								class="flex justify-between text-lg font-bold text-gray-900 dark:text-white border-t border-gray-200 dark:border-warm-border pt-3 mt-2"
							>
								<span>Grand Total:</span>
								<span
									>${{
										formatAmount(selectedTransaction.invoice.grand_total)
									}}</span
								>
							</div>
						</div>

						<h4
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2"
						>
							Payments
						</h4>
						<div class="space-y-2">
							<div
								v-for="payment in selectedTransaction.payments"
								:key="payment.mode_of_payment"
								class="flex justify-between px-3 py-2 bg-gray-50 dark:bg-warm-dark-900/50 rounded-lg text-sm"
							>
								<span class="text-gray-700 dark:text-gray-300">{{
									payment.mode_of_payment
								}}</span>
								<span class="font-semibold text-gray-900 dark:text-white"
									>${{ formatAmount(payment.amount) }}</span
								>
							</div>
						</div>
					</div>

					<div
						class="flex items-center justify-between gap-3 p-4 border-t border-gray-100 dark:border-warm-border/50"
					>
						<!-- Return/Void Actions (left side) -->
						<div
							class="flex items-center gap-2"
							v-if="selectedTransaction.invoice.status === 'Paid'"
						>
							<button
								@click="initiateReturn(selectedTransaction.invoice.name)"
								:disabled="returnProcessing"
								class="px-3 py-2 text-xs font-bold text-orange-600 dark:text-orange-400 border border-orange-200 dark:border-orange-800/30 rounded-lg hover:bg-orange-50 dark:hover:bg-orange-900/20 transition flex items-center gap-1.5 disabled:opacity-50"
							>
								<svg
									class="w-3.5 h-3.5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
									/>
								</svg>
								Return
							</button>
							<button
								@click="showVoidConfirm = true"
								:disabled="returnProcessing"
								class="px-3 py-2 text-xs font-bold text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800/30 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition flex items-center gap-1.5 disabled:opacity-50"
							>
								<svg
									class="w-3.5 h-3.5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
									/>
								</svg>
								Void
							</button>
						</div>
						<div v-else></div>

						<!-- Print/Close (right side) -->
						<div class="flex items-center gap-2">
							<button
								@click="printInvoice(selectedTransaction.invoice.name)"
								class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition flex items-center gap-2"
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
								Print
							</button>
							<button
								@click="selectedTransaction = null"
								class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition"
							>
								Close
							</button>
						</div>
					</div>

					<!-- Void Confirmation Mini-Modal -->
					<div
						v-if="showVoidConfirm"
						class="absolute inset-0 bg-white/95 dark:bg-warm-card/95 backdrop-blur-sm flex items-center justify-center z-10 rounded-2xl"
					>
						<div class="text-center p-8 max-w-sm">
							<div
								class="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mx-auto mb-4"
							>
								<svg
									class="w-6 h-6 text-red-500"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
									/>
								</svg>
							</div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
								Void Invoice?
							</h3>
							<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
								This will cancel the invoice and reverse stock. Requires manager
								PIN.
							</p>
							<input
								v-model="voidReason"
								type="text"
								placeholder="Reason for void..."
								class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-sm mb-3"
							/>
							<input
								v-model="voidPin"
								type="password"
								maxlength="6"
								placeholder="Manager PIN"
								class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-sm mb-4 font-mono"
							/>
							<p v-if="voidError" class="text-xs text-red-500 mb-3">
								{{ voidError }}
							</p>
							<div class="flex gap-3">
								<button
									@click="
										showVoidConfirm = false;
										voidReason = '';
										voidPin = '';
										voidError = '';
									"
									class="flex-1 py-2 text-sm font-medium border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-warm-dark-700"
								>
									Cancel
								</button>
								<button
									@click="executeVoid"
									:disabled="!voidReason || !voidPin || returnProcessing"
									class="flex-1 py-2 text-sm font-bold bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 transition"
								>
									{{ returnProcessing ? 'Voiding...' : 'Confirm Void' }}
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import ViewToggle from '@/components/ViewToggle.vue'
import { ref, onMounted, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import TransactionFilterBar from '@/components/TransactionFilterBar.vue'
import { useSessionStore } from '@/stores/session.js'
import { useUIStore } from '@/stores/ui.js'
import { canViewAllSalesHistory } from '@/utils/permissions.js'

const ui = useUIStore()

const session = useSessionStore()
const isOwnSalesOnly = computed(() => !canViewAllSalesHistory())

const viewMode = ref(localStorage.getItem('zevar_sales_view') || 'list')
const loading = ref(false)
const sales = ref([])
const summary = ref(null)
const selectedTransaction = ref(null)
const pagination = ref({ page: 1, total_pages: 1, total_count: 0 })

// Return/Void state
const returnProcessing = ref(false)
const showVoidConfirm = ref(false)
const voidReason = ref('')
const voidPin = ref('')
const voidError = ref('')

const filters = computed(() => ui.activeFilters.transactions || {})

// Watch filters to trigger fetch
watch(
	filters,
	() => {
		fetchSales()
	},
	{ deep: true }
)

const salesResource = createResource({
	url: 'zevar_core.api.sales_history.get_sales_history',
	auto: false,
})

const summaryResource = createResource({
	url: 'zevar_core.api.sales_history.get_sales_summary',
	auto: false,
})

const detailsResource = createResource({
	url: 'zevar_core.api.sales_history.get_transaction_details',
	auto: false,
})

function getDefaultDate() {
	return new Date().toISOString().split('T')[0]
}

function getDefaultFromDate() {
	const date = new Date()
	date.setDate(date.getDate() - 30)
	return date.toISOString().split('T')[0]
}

function formatAmount(amount) {
	if (!amount) return '0.00'
	return Number(amount).toFixed(2)
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
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

async function fetchSales(append = false) {
	if (!append) {
		pagination.value.page = 1
		loading.value = true
	} else {
		loading.value = true
	}

	try {
		// Add owner filter for non-admin users
		const requestParams = {
			...filters.value,
			page: pagination.value.page,
			page_size: 20,
		}
		if (isOwnSalesOnly.value && session.user?.email) {
			requestParams.owner = session.user.email
		}

		const summaryParams = {
			from_date: filters.value.from_date,
			to_date: filters.value.to_date,
		}
		if (isOwnSalesOnly.value && session.user?.email) {
			summaryParams.owner = session.user.email
		}

		const [salesResult, summaryResult] = await Promise.all([
			salesResource.submit(requestParams),
			summaryResource.submit(summaryParams),
		])

		if (append) {
			sales.value = [...sales.value, ...(salesResult.sales || [])]
		} else {
			sales.value = salesResult.sales || []
		}

		pagination.value = salesResult.pagination || pagination.value
		summary.value = summaryResult.summary
	} catch (error) {
		console.error('Failed to fetch sales:', error)
	} finally {
		loading.value = false
	}
}

function loadMore() {
	if (pagination.value.page < pagination.value.total_pages) {
		pagination.value.page++
		fetchSales(true)
	}
}

async function viewDetails(invoiceName) {
	try {
		const result = await detailsResource.submit({ invoice_name: invoiceName })
		selectedTransaction.value = result
	} catch (error) {
		console.error('Failed to fetch details:', error)
	}
}

function printInvoice(invoiceName) {
	window.open(`/printview?doctype=Sales Invoice&name=${invoiceName}`, '_blank')
}

function goToPage(page) {
	pagination.value.page = page
	fetchSales()
}

// Return initiation — opens Frappe's return form in a new tab
function initiateReturn(invoiceName) {
	window.open(`/app/sales-invoice/${invoiceName}?is_return=1`, '_blank')
}

// Void invoice with manager PIN
async function executeVoid() {
	if (!voidReason.value || !voidPin.value) return
	voidError.value = ''
	returnProcessing.value = true
	try {
		const res = await fetch('/api/method/zevar_core.api.returns.void_invoice', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({
				invoice_name: selectedTransaction.value.invoice.name,
				reason: voidReason.value,
				manager_pin: voidPin.value,
			}),
		})
		const data = await res.json()
		if (data.message?.success) {
			showVoidConfirm.value = false
			selectedTransaction.value = null
			voidReason.value = ''
			voidPin.value = ''
			fetchSales() // Refresh list
		} else {
			voidError.value = data.message?.message || data._server_messages || 'Void failed'
		}
	} catch (e) {
		voidError.value = 'Network error'
	} finally {
		returnProcessing.value = false
	}
}

// CSV Export
function exportCSV() {
	if (!sales.value.length) return
	const headers = ['Invoice #', 'Date', 'Customer', 'Items', 'Total', 'Status']
	const rows = sales.value.map((s) => [
		s.name,
		s.posting_date,
		s.customer || 'Walk-In',
		s.item_count || 1,
		formatAmount(s.grand_total),
		s.status,
	])
	const csv = [headers, ...rows]
		.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(','))
		.join('\n')
	const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
	const url = URL.createObjectURL(blob)
	const link = document.createElement('a')
	link.href = url
	link.download = `sales_history_${new Date().toISOString().split('T')[0]}.csv`
	link.click()
	URL.revokeObjectURL(url)
}

onMounted(() => {
	fetchSales()
})
</script>
