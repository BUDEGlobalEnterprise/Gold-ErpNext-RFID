<template>
	<Teleport to="body">
		<Transition name="fade">
			<div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
				<div
					@click="close"
					class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm transition-opacity"
				></div>

				<div
					class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full overflow-hidden flex flex-col md:flex-row transition-all duration-500 ease-in-out border border-transparent dark:border-white/10"
					:class="step === 'success' ? 'max-w-md' : 'max-w-4xl h-[650px]'"
				>
					<template v-if="step === 'review'">
					<div
						class="w-full md:w-1/2 bg-gray-50 dark:bg-[#15171e] p-6 border-r border-gray-100 dark:border-white/5 flex flex-col"
					>
						<h3
							class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-4"
						>
							Items in Bag
						</h3>

						<div class="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
							<div
								v-for="item in cart.items"
								:key="item.item_code"
								class="flex justify-between items-center bg-white dark:bg-[#0F1115] p-3 rounded-lg border border-gray-100 dark:border-white/5 shadow-sm"
							>
								<div class="flex items-center gap-3">
									<div
										class="w-10 h-10 bg-gray-100 dark:bg-gray-800 rounded-md overflow-hidden flex-shrink-0"
									>
										<img
											v-if="item.image"
											:src="item.image"
											class="w-full h-full object-cover"
										/>
									</div>
									<div class="min-w-0">
										<div
											class="font-bold text-gray-900 dark:text-white text-sm line-clamp-1"
										>
											{{ item.item_name }}
										</div>
										<div
											class="text-xs text-gray-500 dark:text-gray-400 truncate"
										>
											{{ item.item_code }}
										</div>
									</div>
								</div>
								<div class="text-right flex-shrink-0">
									<div
										class="font-mono font-bold text-sm text-gray-900 dark:text-gray-200"
									>
										{{ formatCurrency(item.amount * item.qty) }}
									</div>
									<div class="text-[10px] text-gray-400">
										Qty: {{ item.qty }}
									</div>
								</div>
							</div>
						</div>

						<!-- Tax Exempt Toggle -->
						<div class="mt-4 pt-4 border-t border-gray-200 dark:border-white/10">
							<label class="flex items-center justify-between cursor-pointer group">
								<div>
									<span class="font-medium text-gray-700 dark:text-gray-300"
										>Tax Exempt</span
									>
									<span class="text-xs text-gray-400 block"
										>For resellers or tax-free sales</span
									>
								</div>
								<button
									@click="taxExempt = !taxExempt"
									class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
									:class="
										taxExempt ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
									"
								>
									<span
										class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
										:class="taxExempt ? 'translate-x-6' : 'translate-x-1'"
									></span>
								</button>
							</label>
						</div>

						<div
							class="mt-4 space-y-2 pt-4 border-t border-gray-200 dark:border-white/10"
						>
							<div
								class="flex justify-between text-sm text-gray-500 dark:text-gray-400"
							>
								<span>Subtotal</span>
								<span>{{ formatCurrency(cart.subtotal) }}</span>
							</div>
							<div
								class="flex justify-between text-sm"
								:class="
									taxExempt
										? 'text-green-500 line-through'
										: 'text-gray-500 dark:text-gray-400'
								"
							>
								<span>Tax ({{ taxExempt ? '0' : cart.taxRate }}%)</span>
								<span>{{ formatCurrency(taxExempt ? 0 : cart.tax) }}</span>
							</div>

							<!-- Trade-In Credit -->
							<div
								v-if="cart.tradeIns.length > 0"
								class="mt-2 pt-2 border-t border-orange-200 dark:border-orange-800/30"
							>
								<div
									class="text-xs font-bold text-orange-500 uppercase tracking-wider mb-1"
								>
									Trade-Ins
								</div>
								<div
									v-for="(ti, idx) in cart.tradeIns"
									:key="idx"
									class="flex justify-between text-xs text-orange-600 dark:text-orange-400 mb-0.5"
								>
									<span class="truncate">{{
										ti.description || 'Trade-In'
									}}</span>
									<span class="font-mono"
										>-{{ formatCurrency(ti.trade_in_value) }}</span
									>
								</div>
								<div
									class="flex justify-between text-sm font-bold text-orange-600 dark:text-orange-400 mt-1"
								>
									<span>Trade-In Credit</span>
									<span>-{{ formatCurrency(tradeInTotal) }}</span>
								</div>
							</div>

							<div
								class="flex justify-between text-2xl font-bold text-gray-900 dark:text-white pt-2 border-t border-gray-200 dark:border-white/10 mt-2"
							>
								<span>Total</span>
								<span>{{ formatCurrency(grandTotalWithTaxExempt) }}</span>
							</div>
						</div>
					</div>

					<div
						class="w-full md:w-1/2 p-6 flex flex-col bg-white dark:bg-[#1a1c23] relative overflow-y-auto"
					>
						<button
							@click="close"
							class="absolute top-4 right-4 p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full transition"
						>
							<svg
								class="w-5 h-5 text-gray-400"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>

						<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-1">
							Payment
						</h2>
						<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
							Select payment method(s). Split payments allowed.
						</p>

						<!-- Sales Associates -->
						<div class="mb-4">
							<button
								@click="showSalespersons = !showSalespersons"
								class="w-full flex items-center justify-between p-3 border rounded-xl transition-all"
								:class="
									cart.salespersons.length > 0
										? 'border-[#D4AF37] bg-[#D4AF37]/10'
										: 'border-gray-200 hover:border-gray-400 dark:border-white/10 dark:hover:border-white/30'
								"
							>
								<div class="flex items-center gap-3">
									<div
										class="w-8 h-8 rounded-full flex items-center justify-center bg-purple-100 text-purple-600"
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
												d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
											></path>
										</svg>
									</div>
									<div class="text-left">
										<span
											class="font-medium text-gray-900 dark:text-white text-sm"
											>Sales Associates</span
										>
										<span
											v-if="cart.salespersons.length > 0"
											class="text-xs text-gray-500 dark:text-gray-400 block"
											>{{ cart.salespersons.length }} assigned</span
										>
									</div>
								</div>
								<svg
									class="w-4 h-4 text-gray-400 transition-transform"
									:class="showSalespersons ? 'rotate-180' : ''"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 9l-7 7-7-7"
									></path>
								</svg>
							</button>

							<div
								v-if="showSalespersons"
								class="mt-2 bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 border border-gray-100 dark:border-white/5 space-y-3"
							>
								<div
									v-for="(sp, idx) in cart.salespersons"
									:key="idx"
									class="flex items-center gap-2"
								>
									<select
										v-model="sp.employee"
										class="flex-1 px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm"
									>
										<option value="" disabled>Select Associate</option>
										<option
											v-for="emp in salesAssociates.data"
											:key="emp.name"
											:value="emp.name"
										>
											{{ emp.employee_name }} ({{
												emp.designation || 'Sales'
											}})
										</option>
									</select>
									<div class="flex items-center gap-1">
										<input
											v-model.number="sp.split"
											@input="cart.recalculateSalespersonSplit(idx)"
											type="number"
											min="0"
											max="100"
											class="w-16 px-2 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm text-right font-mono"
										/>
										<span class="text-xs text-gray-400">%</span>
									</div>
									<button
										@click="cart.removeSalesperson(idx)"
										class="p-1 text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
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
											></path>
										</svg>
									</button>
								</div>

								<button
									v-if="cart.salespersons.length < 4"
									@click="cart.addSalesperson('', null)"
									class="w-full py-2 text-sm font-medium text-[#D4AF37] border border-dashed border-[#D4AF37]/40 rounded-lg hover:bg-[#D4AF37]/10 transition"
								>
									+ Add Associate
								</button>

								<div
									v-if="
										cart.salespersons.length > 0 &&
										salespersonSplitTotal !== 100
									"
									class="text-xs text-red-500 font-medium"
								>
									Splits must total 100% (currently {{ salespersonSplitTotal }}%)
								</div>
							</div>
						</div>

						<!-- Payment Methods -->
						<div class="space-y-2 mb-4">
							<button
								v-for="mode in paymentModes"
								:key="mode.mode"
								@click="togglePaymentMode(mode.mode)"
								class="w-full flex items-center justify-between p-3 border rounded-xl transition-all"
								:class="
									isPaymentSelected(mode.mode)
										? 'border-[#D4AF37] bg-[#D4AF37]/10 ring-1 ring-[#D4AF37]'
										: 'border-gray-200 hover:border-gray-400 dark:border-white/10 dark:hover:border-white/30'
								"
							>
								<div class="flex items-center gap-3">
									<div
										class="w-8 h-8 rounded-full flex items-center justify-center"
										:class="
											mode.type === 'Cash'
												? 'bg-green-100 text-green-600'
												: 'bg-blue-100 text-blue-600'
										"
									>
										<svg
											v-if="mode.type === 'Cash'"
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
												d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
											></path>
										</svg>
									</div>
									<span
										class="font-medium text-gray-900 dark:text-white text-sm"
										>{{ mode.mode }}</span
									>
								</div>
								<div
									v-if="isPaymentSelected(mode.mode)"
									class="w-2 h-2 rounded-full bg-green-500"
								></div>
							</button>
						</div>

						<!-- Gift Card Number Input -->
						<div
							v-if="isPaymentSelected('Gift Card')"
							class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 mb-4 border border-gray-100 dark:border-white/5"
						>
							<label
								class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block"
								>Gift Card Number</label
							>
							<div class="flex items-center gap-2">
								<input
									v-model="giftCardNumber"
									type="text"
									placeholder="Enter card number"
									@blur="lookupGiftCard"
									@keyup.enter="lookupGiftCard"
									class="flex-1 px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm font-mono"
								/>
								<button
									@click="lookupGiftCard"
									:disabled="!giftCardNumber || giftCardLoading"
									class="px-3 py-2 text-sm font-medium bg-[#D4AF37] text-black rounded-lg hover:bg-[#b5952f] disabled:opacity-50 transition"
								>
									{{ giftCardLoading ? '...' : 'Check' }}
								</button>
							</div>
							<div
								v-if="giftCardInfo"
								class="mt-2 text-sm"
								:class="giftCardInfo.valid ? 'text-green-600' : 'text-red-500'"
							>
								<span v-if="giftCardInfo.valid">
									✓ Balance: {{ formatCurrency(giftCardInfo.balance) }}
								</span>
								<span v-else>✗ {{ giftCardInfo.message }}</span>
							</div>
						</div>

						<!-- Split Payment Amounts (if multiple selected) -->
						<div
							v-if="selectedPayments.length > 1"
							class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 mb-4 border border-gray-100 dark:border-white/5"
						>
							<h4
								class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3"
							>
								Split Amounts
							</h4>
							<div
								v-for="payment in selectedPayments"
								:key="payment.mode"
								class="flex items-center justify-between mb-2"
							>
								<span class="text-sm text-gray-600 dark:text-gray-300">{{
									payment.mode
								}}</span>
								<div class="flex items-center gap-2">
									<span class="text-gray-400">$</span>
									<input
										type="number"
										v-model.number="payment.amount"
										@input="recalculateSplit(payment.mode)"
										class="w-24 px-2 py-1 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded text-right font-mono text-sm"
										min="0"
										:max="grandTotalWithTaxExempt"
									/>
								</div>
							</div>
							<div
								class="flex justify-between text-sm pt-2 border-t border-gray-200 dark:border-white/10 mt-2"
							>
								<span class="text-gray-500">{{
									remainingAmount < 0 ? 'Change Due' : 'Remaining'
								}}</span>
								<span
									:class="
										remainingAmount === 0
											? 'text-green-500 font-bold'
											: remainingAmount < 0
											? 'text-orange-500 font-bold'
											: 'text-red-500 font-bold'
									"
								>
									{{
										remainingAmount < 0
											? formatCurrency(Math.abs(remainingAmount))
											: formatCurrency(remainingAmount)
									}}
								</span>
							</div>
						</div>

						<div class="mt-auto">
							<button
								@click="handlePayment"
								:disabled="!canSubmit || processing"
								class="w-full py-4 rounded-xl font-bold text-lg shadow-xl transition-all flex items-center justify-center gap-2 transform active:scale-95"
								:class="
									!canSubmit || processing
										? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-white/5 dark:text-gray-600'
										: 'bg-gray-900 text-white hover:bg-black dark:bg-[#D4AF37] dark:text-black dark:hover:bg-[#b5952f]'
								"
							>
								<span
									v-if="processing"
									class="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-white"
								></span>
								<span v-else-if="!canSubmit">{{
									selectedPayments.length === 0
										? 'Select Payment'
										: 'Enter Amounts'
								}}</span>
								<span v-else
									>Confirm {{ formatCurrency(grandTotalWithTaxExempt) }}</span
								>
							</button>
							<button
								@click="step = 'layaway'"
								class="w-full py-2 mt-2 rounded-lg text-sm font-medium text-[#D4AF37] border border-[#D4AF37]/30 hover:bg-[#D4AF37]/10 transition"
							>
								Start Layaway Instead
							</button>
						</div>
					</div>
				</template>

				<template v-else-if="step === 'layaway'">
					<div
						class="w-full flex flex-col bg-white dark:bg-[#1a1c23] relative overflow-hidden"
					>
						<div class="flex items-center justify-between p-6 pb-0 flex-shrink-0">
							<button
								@click="step = 'review'"
								class="p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full transition text-gray-400"
							>
								<svg
									class="w-5 h-5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 19l-7-7 7-7"
									></path>
								</svg>
							</button>
							<div>
								<h2 class="text-xl font-bold text-gray-900 dark:text-white">
									Layaway Plan
								</h2>
								<p class="text-sm text-gray-500 dark:text-gray-400">
									Reserve items with a deposit and pay over time.
								</p>
							</div>
							<button
								@click="close"
								class="p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full transition text-gray-400"
							>
								<svg
									class="w-5 h-5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M6 18L18 6M6 6l12 12"
									></path>
								</svg>
							</button>
						</div>

						<div class="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
							<!-- Customer (required for layaway) -->
							<div>
								<label
									class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block"
									>Customer *</label
								>
								<CustomerSelector />
							</div>

							<!-- Items Summary -->
							<div
								class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 border border-gray-100 dark:border-white/5"
							>
								<div class="flex justify-between text-sm mb-1">
									<span class="text-gray-500">Items Total</span>
									<span class="font-bold text-gray-900 dark:text-white">{{
										formatCurrency(cart.subtotal)
									}}</span>
								</div>
								<div class="flex justify-between text-sm">
									<span class="text-gray-500"
										>{{ cart.items.length }} item(s)</span
									>
								</div>
							</div>

							<!-- Duration -->
							<div>
								<label
									class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block"
									>Duration</label
								>
								<div class="flex gap-2">
									<button
										v-for="m in [3, 6, 9, 12]"
										:key="m"
										@click="layawayDuration = m"
										class="flex-1 py-3 rounded-xl font-bold text-sm border transition-all"
										:class="
											layawayDuration === m
												? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37] ring-1 ring-[#D4AF37]'
												: 'border-gray-200 dark:border-white/10 text-gray-600 dark:text-gray-400 hover:border-gray-400'
										"
									>
										{{ m }} mo
									</button>
								</div>
							</div>

							<!-- Deposit -->
							<div>
								<label
									class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 block"
								>
									Deposit Amount
									<span
										class="text-[10px] text-gray-400 font-normal normal-case tracking-normal ml-2"
										>(Min 10%: {{ formatCurrency(minimumDeposit) }})</span
									>
								</label>
								<div class="flex items-center gap-2">
									<span class="text-gray-400 text-lg">$</span>
									<input
										v-model.number="layawayDeposit"
										type="number"
										min="1"
										:max="cart.subtotal - 1"
										class="flex-1 px-3 py-3 bg-white dark:bg-[#0F1115] border rounded-xl text-lg font-mono font-bold transition-colors"
										:class="
											layawayDeposit && layawayDeposit < minimumDeposit
												? 'border-red-400 dark:border-red-500 text-red-600'
												: 'border-gray-200 dark:border-white/10'
										"
										placeholder="Enter deposit..."
									/>
								</div>
								<p
									v-if="layawayDeposit && layawayDeposit < minimumDeposit"
									class="text-xs text-red-500 mt-1.5"
								>
									Deposit must be at least 10% of total ({{
										formatCurrency(minimumDeposit)
									}})
								</p>
							</div>

							<!-- Auto-calculated Preview Panel -->
							<div
								v-if="layawayDeposit >= minimumDeposit && layawayDuration > 0"
								class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-100 dark:border-blue-800/30 space-y-2"
							>
								<h4
									class="text-xs font-bold text-blue-500 dark:text-blue-400 uppercase tracking-wider mb-2"
								>
									Payment Schedule Preview
								</h4>
								<div class="flex justify-between text-sm">
									<span class="text-blue-600 dark:text-blue-400"
										>Today's Deposit</span
									>
									<span class="font-bold text-blue-700 dark:text-blue-300">{{
										formatCurrency(layawayDeposit)
									}}</span>
								</div>
								<div class="flex justify-between text-sm">
									<span class="text-blue-600 dark:text-blue-400"
										>Remaining Balance</span
									>
									<span class="font-bold text-blue-700 dark:text-blue-300">{{
										formatCurrency(cart.subtotal - layawayDeposit)
									}}</span>
								</div>
								<div class="flex justify-between text-sm">
									<span class="text-blue-600 dark:text-blue-400"
										>Monthly Payment</span
									>
									<span class="font-bold text-blue-700 dark:text-blue-300">
										{{ formatCurrency(layawayMonthlyPayment) }} ×
										{{ layawayDuration - 1 }} mo
									</span>
								</div>
								<div
									class="flex justify-between text-sm pt-2 border-t border-blue-200 dark:border-blue-700/30"
								>
									<span class="text-blue-600 dark:text-blue-400"
										>Target Completion</span
									>
									<span class="font-bold text-blue-700 dark:text-blue-300">{{
										layawayTargetDate
									}}</span>
								</div>
							</div>
						</div>

						<div class="p-6 pt-0 flex-shrink-0">
							<button
								@click="handleLayaway"
								:disabled="!canSubmitLayaway || processing"
								class="w-full py-4 rounded-xl font-bold text-lg shadow-xl transition-all flex items-center justify-center gap-2 transform active:scale-95"
								:class="
									!canSubmitLayaway || processing
										? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-white/5 dark:text-gray-600'
										: 'bg-gray-900 text-white hover:bg-black dark:bg-[#D4AF37] dark:text-black dark:hover:bg-[#b5952f]'
								"
							>
								<span
									v-if="processing"
									class="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-white"
								></span>
								<span v-else-if="!canSubmitLayaway">
									{{
										!cart.customer
											? 'Select Customer'
											: layawayDeposit < minimumDeposit
											? 'Deposit Too Low'
											: 'Complete Fields'
									}}
								</span>
								<span v-else
									>Confirm Layaway —
									{{ formatCurrency(layawayDeposit) }} Deposit</span
								>
							</button>
						</div>
					</div>
				</template>

				<template v-else-if="step === 'success'">
					<div
						class="p-10 flex flex-col items-center justify-center text-center w-full bg-white dark:bg-[#1a1c23]"
					>
						<div
							class="w-20 h-20 rounded-full flex items-center justify-center mb-6 animate-bounce-short"
							:class="
								isLayawaySuccess
									? 'bg-[#D4AF37]/20'
									: 'bg-green-100 dark:bg-green-900/30'
							"
						>
							<svg
								class="w-10 h-10"
								:class="
									isLayawaySuccess
										? 'text-[#D4AF37]'
										: 'text-green-600 dark:text-green-400'
								"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2.5"
									d="M5 13l4 4L19 7"
								></path>
							</svg>
						</div>
						<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
							{{ isLayawaySuccess ? 'Layaway Created!' : 'Payment Successful!' }}
						</h2>
						<p class="text-gray-500 dark:text-gray-400 mb-8">
							{{
								isLayawaySuccess
									? 'Contract has been generated and submitted.'
									: 'Invoice has been generated in ERPNext.'
							}}
						</p>

						<div
							class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-4 w-full mb-6 border border-gray-100 dark:border-white/5 space-y-2"
						>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">{{
									isLayawaySuccess ? 'Contract ID' : 'Transaction ID'
								}}</span>
								<span class="font-mono font-bold text-gray-900 dark:text-white">{{
									lastOrderId || '—'
								}}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">{{
									isLayawaySuccess ? 'Deposit Paid' : 'Amount Paid'
								}}</span>
								<span
									class="font-mono font-bold"
									:class="
										isLayawaySuccess
											? 'text-[#D4AF37]'
											: 'text-green-600 dark:text-green-400'
									"
									>{{
										formatCurrency(
											isLayawaySuccess
												? layawayDeposit
												: grandTotalWithTaxExempt
										)
									}}</span
								>
							</div>
							<!-- Layaway-specific details -->
							<template v-if="isLayawaySuccess">
								<div class="flex justify-between text-sm">
									<span class="text-gray-500 dark:text-gray-400"
										>Total Amount</span
									>
									<span
										class="font-mono font-bold text-gray-900 dark:text-white"
										>{{ formatCurrency(cart.subtotal) }}</span
									>
								</div>
								<div class="flex justify-between text-sm">
									<span class="text-gray-500 dark:text-gray-400"
										>Remaining Balance</span
									>
									<span
										class="font-mono font-bold text-gray-900 dark:text-white"
										>{{
											formatCurrency(cart.subtotal - (layawayDeposit || 0))
										}}</span
									>
								</div>
								<div
									class="flex justify-between text-sm pt-2 border-t border-gray-200 dark:border-white/10"
								>
									<span class="text-gray-500 dark:text-gray-400"
										>Monthly Payment</span
									>
									<span class="font-mono font-bold text-gray-900 dark:text-white"
										>{{ formatCurrency(layawayMonthlyPayment) }} ×
										{{ (layawayDuration || 6) - 1 }} mo</span
									>
								</div>
								<div class="flex justify-between text-sm">
									<span class="text-gray-500 dark:text-gray-400"
										>Target Completion</span
									>
									<span
										class="font-mono font-bold text-gray-900 dark:text-white"
										>{{ layawayTargetDate }}</span
									>
								</div>
							</template>
							<div
								v-else-if="taxExempt"
								class="flex justify-between text-sm pt-2 border-t border-gray-200 dark:border-white/10"
							>
								<span class="text-gray-500 dark:text-gray-400">Tax Status</span>
								<span class="text-green-500 font-medium">Exempt</span>
							</div>
						</div>

						<div class="flex gap-3 w-full">
							<button
								@click="close"
								class="flex-1 py-3 rounded-lg font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-white/5 dark:text-gray-300 dark:hover:bg-white/10 transition"
							>
								New Order
							</button>
							<button
								v-if="isLayawaySuccess"
								@click="openLayawayInDesk"
								class="flex-1 py-3 rounded-lg font-bold text-white bg-gray-900 hover:bg-black dark:bg-[#D4AF37] dark:text-black dark:hover:bg-[#b5952f] transition flex items-center justify-center gap-2"
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
										d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
									></path>
								</svg>
								View Contract
							</button>
							<button
								v-else
								class="flex-1 py-3 rounded-lg font-bold text-white bg-gray-900 hover:bg-black dark:bg-[#D4AF37] dark:text-black dark:hover:bg-[#b5952f] transition flex items-center justify-center gap-2"
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
										d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2-4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
									></path>
								</svg>
								Print Receipt
							</button>
						</div>
					</div>
				</template>
			</div>
		</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useCartStore } from '@/stores/cart.js'
import { useSessionStore } from '@/stores/session.js'
import CustomerSelector from '@/components/CustomerSelector.vue'

const props = defineProps(['show'])
const emit = defineEmits(['close'])
const cart = useCartStore()
const session = useSessionStore()

// State
const processing = ref(false)
const step = ref('review') // 'review' | 'layaway' | 'success'
const lastOrderId = ref(null)
const taxExempt = ref(false)
const selectedPayments = ref([]) // [{mode: 'Cash', amount: 100}, ...]
const showSalespersons = ref(false)

// Sales associates (employees) resource
const salesAssociates = createResource({
	url: 'zevar_core.api.sales_associates.get_sales_associates',
	initialData: [],
	auto: true,
})

// Layaway state
const layawayDuration = ref(6)
const layawayDeposit = ref(null)

// Computed: salesperson split total
const salespersonSplitTotal = computed(() => {
	return cart.salespersons.reduce((sum, sp) => sum + (sp.split || 0), 0)
})

// Layaway computeds
const minimumDeposit = computed(() => {
	return Number((cart.subtotal * 0.1).toFixed(2))
})

const layawayMonthlyPayment = computed(() => {
	const remaining = cart.subtotal - (layawayDeposit.value || 0)
	const months = (layawayDuration.value || 6) - 1
	if (remaining <= 0 || months <= 0) return 0
	return Number((remaining / months).toFixed(2))
})

const layawayTargetDate = computed(() => {
	const now = new Date()
	const target = new Date(now)
	target.setMonth(target.getMonth() + (layawayDuration.value || 6))
	return target.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
})

const canSubmitLayaway = computed(() => {
	if (!cart.customer) return false
	const dep = layawayDeposit.value || 0
	return (
		dep >= minimumDeposit.value &&
		dep < cart.subtotal &&
		[3, 6, 9, 12].includes(layawayDuration.value)
	)
})

const isLayawaySuccess = ref(false)

// Trade-in total credit
const tradeInTotal = computed(() => {
	return cart.tradeIns.reduce((sum, ti) => sum + (ti.trade_in_value || 0), 0)
})

// Available payment modes
const paymentModes = [
	{ mode: 'Cash', type: 'Cash' },
	{ mode: 'Credit Card', type: 'Bank' },
	{ mode: 'Debit Card', type: 'Bank' },
	{ mode: 'Check', type: 'Bank' },
	{ mode: 'Wire Transfer', type: 'Bank' },
	{ mode: 'Zelle', type: 'Bank' },
	{ mode: 'Gift Card', type: 'GiftCard' },
]

// Gift Card state
const giftCardNumber = ref('')
const giftCardInfo = ref(null)
const giftCardLoading = ref(false)

// Computed: Grand total with tax exemption
const grandTotalWithTaxExempt = computed(() => {
	const base = taxExempt.value ? cart.subtotal : cart.subtotal + cart.tax
	const total = base - tradeInTotal.value
	return Number(Math.max(0, total).toFixed(2))
})

// Computed: Remaining amount for split payments
const remainingAmount = computed(() => {
	const totalPaid = selectedPayments.value.reduce((sum, p) => sum + Number(p.amount || 0), 0)
	return Number((grandTotalWithTaxExempt.value - totalPaid).toFixed(2))
})

// Computed: Can submit the payment
const canSubmit = computed(() => {
	if (selectedPayments.value.length === 0) return false
	// Check salesperson splits if any are added
	if (cart.salespersons.length > 0 && Math.abs(salespersonSplitTotal.value - 100) > 0.01) {
		return false
	}
	if (selectedPayments.value.length === 1) return true
	// For split payments, remaining must be 0
	return Math.abs(remainingAmount.value) < 0.01
})

// Check if a payment mode is selected
function isPaymentSelected(mode) {
	return selectedPayments.value.some((p) => p.mode === mode)
}

// Toggle payment mode selection
function togglePaymentMode(mode) {
	const index = selectedPayments.value.findIndex((p) => p.mode === mode)
	if (index >= 0) {
		selectedPayments.value.splice(index, 1)
	} else {
		// Add new payment mode
		if (selectedPayments.value.length === 0) {
			// First payment gets full amount
			selectedPayments.value.push({ mode, amount: grandTotalWithTaxExempt.value })
		} else {
			// Additional payments start at null
			selectedPayments.value.push({ mode, amount: null })
		}
	}
}

// Recalculate split when user edits an amount
function recalculateSplit(changedMode) {
	const changedPayment = selectedPayments.value.find((p) => p.mode === changedMode)
	if (changedPayment) {
		changedPayment.amount = Number(Number(changedPayment.amount || 0).toFixed(2))
	}

	// For Gift Card, cap amount at available balance
	if (changedMode === 'Gift Card' && giftCardInfo.value?.valid) {
		if (changedPayment && changedPayment.amount > giftCardInfo.value.balance) {
			changedPayment.amount = Number(Number(giftCardInfo.value.balance).toFixed(2))
		}
	}

	// Auto balance if exactly 2 payment methods are selected
	if (selectedPayments.value.length === 2 && changedPayment) {
		const otherPayment = selectedPayments.value.find((p) => p.mode !== changedMode)
		if (otherPayment) {
			const remaining = grandTotalWithTaxExempt.value - changedPayment.amount
			otherPayment.amount = Number(remaining.toFixed(2))
		}
	}
}

// Gift Card balance lookup
async function lookupGiftCard() {
	if (!giftCardNumber.value) return
	giftCardLoading.value = true
	giftCardInfo.value = null
	try {
		const r = await createResource({
			url: 'zevar_core.api.gift_card.get_gift_card_balance',
			params: { gift_card_number: giftCardNumber.value },
		}).fetch()
		const data = r?.data || r
		giftCardInfo.value = data
		// Cap the Gift Card payment at available balance
		if (data.valid) {
			const gcPayment = selectedPayments.value.find((p) => p.mode === 'Gift Card')
			if (gcPayment && gcPayment.amount > data.balance) {
				gcPayment.amount = data.balance
			}
		}
	} catch (e) {
		giftCardInfo.value = { valid: false, message: 'Failed to lookup card' }
	} finally {
		giftCardLoading.value = false
	}
}

// Reset state when modal opens
watch(
	() => props.show,
	(isOpen) => {
		if (isOpen) {
			step.value = 'review'
			selectedPayments.value = []
			processing.value = false
			taxExempt.value = false
			showSalespersons.value = false
			giftCardNumber.value = ''
			giftCardInfo.value = null
			layawayDuration.value = 6
			layawayDeposit.value = null
			isLayawaySuccess.value = false
		}
	}
)

async function handlePayment() {
	if (!canSubmit.value) return

	// Validate gift card if selected
	const gcPayment = selectedPayments.value.find((p) => p.mode === 'Gift Card')
	if (gcPayment && (!giftCardInfo.value?.valid || !giftCardNumber.value)) {
		alert('Please enter and verify a valid Gift Card number.')
		return
	}
	if (gcPayment && gcPayment.amount > (giftCardInfo.value?.balance || 0)) {
		alert('Gift Card amount exceeds available balance.')
		return
	}

	processing.value = true
	try {
		const result = await cart.submitOrder(selectedPayments.value, {
			taxExempt: taxExempt.value,
			warehouse: session.currentWarehouse,
			giftCardNumber: gcPayment ? giftCardNumber.value : undefined,
		})

		if (result && result.invoice_name) {
			lastOrderId.value = result.invoice_name
		} else if (result && result.data && result.data.invoice_name) {
			lastOrderId.value = result.data.invoice_name
		}
		isLayawaySuccess.value = false
		step.value = 'success'
	} catch (e) {
		// Extract meaningful error from Frappe's response structure
		let errorMsg = ''
		if (e?.exc_type === 'ValidationError' && e?.message) {
			errorMsg = e.message
		} else if (e?.exception?.message) {
			errorMsg = e.exception.message
		} else if (e?._server_messages) {
			try {
				const msgs = JSON.parse(e._server_messages)
				errorMsg = msgs
					.map((m) => {
						try {
							const parsed = JSON.parse(m)
							return parsed.message || parsed.error || m
						} catch {
							return m
						}
					})
					.filter(Boolean)
					.join('\n')
			} catch {
				errorMsg = String(e._server_messages)
			}
		} else if (e?.response?.data?.message) {
			errorMsg = e.response.data.message
		} else if (e?.response?.data?._server_messages) {
			try {
				const msgs = JSON.parse(e.response.data._server_messages)
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
				errorMsg = String(e.response.data._server_messages)
			}
		} else {
			errorMsg = e?.message || e?.error_message || String(e)
		}

		// Strip HTML tags for clean display
		errorMsg = errorMsg.replace(/<[^>]+>/g, '')

		// Clean up common error message patterns
		if (errorMsg.includes('ValidationError') && errorMsg.length < 50) {
			errorMsg = 'Validation error: Please check the form data and try again.'
		}

		// Detect trade-in 2x rule failure → prompt for manager override
		if (errorMsg.includes('Manager Override') && cart.tradeIns.length > 0) {
			const managerUser = prompt(
				'Trade-In 2x rule violation detected.\nEnter Manager User ID to override:'
			)
			if (managerUser) {
				const reason = prompt('Enter override reason:')
				if (reason) {
					// Set manager override on all trade-in rows and retry
					for (const ti of cart.tradeIns) {
						ti.manager_override = managerUser
						ti.override_reason = reason
					}
					// Retry submission with override data
					try {
						const result = await cart.submitOrder(selectedPayments.value, {
							taxExempt: taxExempt.value,
							warehouse: session.currentWarehouse,
						})
						if (result && result.invoice_name) {
							lastOrderId.value = result.invoice_name
						} else if (result && result.data && result.data.invoice_name) {
							lastOrderId.value = result.data.invoice_name
						}
						step.value = 'success'
						return
					} catch (retryErr) {
						alert('Override failed: ' + (retryErr.message || retryErr))
						return
					}
				}
			}
		}
		alert('Order failed: ' + errorMsg)
	} finally {
		processing.value = false
	}
}

async function handleLayaway() {
	if (!canSubmitLayaway.value) return

	processing.value = true
	try {
		const result = await cart.submitLayaway(layawayDeposit.value, layawayDuration.value, {
			warehouse: session.currentWarehouse,
		})
		// Handle all possible response shapes from frappe-ui
		const data = result?.message || result?.data || result
		if (data?.layaway_id) {
			lastOrderId.value = data.layaway_id
		} else if (data?.contract_name) {
			lastOrderId.value = data.contract_name
		} else if (typeof data === 'string') {
			lastOrderId.value = data
		}
		isLayawaySuccess.value = true
		step.value = 'success'
	} catch (e) {
		// Extract meaningful error from Frappe's response structure
		let errorMsg = ''
		if (e?._server_messages) {
			try {
				const msgs = JSON.parse(e._server_messages)
				errorMsg = msgs
					.map((m) => {
						try {
							const parsed = JSON.parse(m)
							return parsed.message || parsed.error || m
						} catch {
							return m
						}
					})
					.filter(Boolean)
					.join('\n')
			} catch {
				errorMsg = String(e._server_messages)
			}
		} else if (e?.response?.data?._server_messages) {
			try {
				const msgs = JSON.parse(e.response.data._server_messages)
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
				errorMsg = String(e.response.data._server_messages)
			}
		} else if (e?.response?.data?.message) {
			errorMsg = e.response.data.message
		} else {
			errorMsg = e?.message || e?.error_message || String(e)
		}
		errorMsg = errorMsg.replace(/<[^>]+>/g, '')
		alert('Layaway failed: ' + errorMsg)
	} finally {
		processing.value = false
	}
}

function close() {
	emit('close')
	if (step.value === 'success') {
		cart.clearCart()
	}
}

function openLayawayInDesk() {
	if (lastOrderId.value) {
		window.open(`/app/layaway-contract/${lastOrderId.value}`, '_blank')
	}
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
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

.animate-bounce-short {
	animation: bounce 0.5s ease-in-out 1;
}
@keyframes bounce {
	0%,
	100% {
		transform: translateY(0);
	}
	50% {
		transform: translateY(-10px);
	}
}

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
/* Dark Mode Scrollbar */
.dark .custom-scrollbar::-webkit-scrollbar-track {
	background: #15171e;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
	background: #333;
}
</style>
