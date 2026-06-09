<template>
	<BaseModal
		:show="show"
		:max-width="step === 'success' ? 'max-w-md' : 'max-w-5xl'"
		:no-max-height="step !== 'success'"
		:show-close="true"
		@close="close"
		data-testid="checkout-modal"
	>
		<!-- ============ PAYMENT FORM ============ -->
		<template v-if="step === 'review'">
			<div
				class="flex flex-col md:flex-row"
				style="height: 80vh; min-height: 500px; max-height: 820px"
			>
				<!-- LEFT COLUMN — context-sensitive -->
				<div
					class="w-full md:w-[45%] bg-gray-50 dark:bg-[#15171e] p-6 border-r border-gray-100 dark:border-warm-border/50 flex flex-col overflow-y-auto"
				>
					<div class="flex items-center justify-between mb-4">
						<h3
							class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider"
						>
							{{ leftPanelTitle }}
						</h3>
					</div>

					<!-- SALE MODE: Items + Tax + Trade-Ins -->
					<template v-if="mode === 'sale'">
						<div class="flex-1 overflow-y-auto space-y-2 pr-1 mb-4">
							<div
								v-for="item in cart.items"
								:key="item.item_code"
								class="flex justify-between items-center bg-white dark:bg-[#0F1115] p-3 rounded-lg border border-gray-100 dark:border-warm-border/50"
							>
								<div class="flex items-center gap-3 min-w-0">
									<div
										class="w-10 h-10 bg-gray-100 dark:bg-warm-dark-900 rounded-md overflow-hidden flex-shrink-0"
									>
										<img
											v-if="item.image"
											:src="item.image"
											class="w-full h-full object-cover"
										/>
									</div>
									<div class="min-w-0">
										<div
											class="font-bold text-gray-900 dark:text-white text-sm truncate"
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
								<div class="text-right flex-shrink-0 pl-2">
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
						<div class="pt-3 border-t border-gray-200 dark:border-warm-border">
							<label class="flex items-center justify-between cursor-pointer group">
								<div>
									<span
										class="font-medium text-gray-700 dark:text-gray-300 text-sm"
										>Tax Exempt</span
									>
									<span class="text-xs text-gray-400 block"
										>For resellers or tax-free sales</span
									>
								</div>
								<input
									v-model="taxExempt"
									type="checkbox"
									class="sr-only peer"
									data-testid="tax-exempt-checkbox"
								/>
								<div
									class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#D4AF37]/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#D4AF37]"
								></div>
							</label>
						</div>

						<!-- Totals -->
						<div
							class="mt-4 space-y-2 pt-4 border-t border-gray-200 dark:border-warm-border"
						>
							<div
								class="flex justify-between text-sm text-gray-500 dark:text-gray-400"
							>
								<span>Subtotal</span
								><span>{{ formatCurrency(cart.subtotal) }}</span>
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
							<div
								v-if="tradeInTotal > 0"
								class="flex justify-between text-sm font-bold text-orange-600 dark:text-orange-400"
							>
								<span>Trade-In Credit</span
								><span>-{{ formatCurrency(tradeInTotal) }}</span>
							</div>
							<div
								class="flex justify-between text-2xl font-bold text-gray-900 dark:text-white pt-2 border-t border-gray-200 dark:border-warm-border mt-2"
							>
								<span>Total</span><span>{{ formatCurrency(totalAmount) }}</span>
							</div>
						</div>
					</template>

					<!-- LAYAWAY / REPAIR MODE: Balance card -->
					<template v-else>
						<div
							class="bg-gradient-to-br from-orange-50 to-orange-100/50 dark:from-orange-900/20 dark:to-orange-800/10 rounded-xl p-5 border border-orange-200 dark:border-orange-800/30 mb-5"
						>
							<div class="flex items-center justify-between">
								<span
									class="text-sm text-orange-700 dark:text-orange-300 font-medium"
									>Outstanding Balance</span
								>
								<span
									class="text-2xl font-bold text-orange-700 dark:text-orange-300"
									>{{ formatCurrency(totalAmount) }}</span
								>
							</div>
							<p
								v-if="referenceId"
								class="text-xs text-orange-600/70 dark:text-orange-400/70 mt-2"
							>
								{{ mode === 'layaway' ? 'Layaway' : 'Repair' }}: {{ referenceId }}
							</p>
							<p
								v-if="itemDetails?.description"
								class="text-sm font-medium text-orange-800 dark:text-orange-200 mt-2 border-t border-orange-200/50 dark:border-orange-800/50 pt-2"
							>
								{{ itemDetails.description }}
							</p>
						</div>

						<div
							v-if="selectedPayments.length > 0"
							class="flex-1 overflow-y-auto pr-1"
						>
							<h4
								class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3"
							>
								Payment Breakdown
							</h4>
							<div class="space-y-2">
								<div
									v-for="payment in selectedPayments"
									:key="payment.mode"
									class="flex items-center justify-between bg-white dark:bg-[#0F1115] p-3.5 rounded-lg border border-gray-100 dark:border-warm-border/50"
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
											class="w-28 px-2 py-1.5 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded text-right font-mono text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
											min="0"
											:max="totalAmount"
										/>
									</div>
								</div>
							</div>
							<div
								class="flex justify-between text-sm pt-3 mt-3 border-t border-gray-200 dark:border-warm-border"
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
						<div
							v-else
							class="flex-1 flex items-center justify-center text-gray-400 dark:text-gray-600 text-sm"
							data-testid="payment-error"
						>
							Select a payment method to begin
						</div>
					</template>

					<!-- Error -->
					<div
						v-if="error"
						class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-3 mt-3"
						data-testid="payment-error"
					>
						<p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
					</div>
				</div>

				<!-- RIGHT COLUMN — Payment Methods (shared) -->
				<div
					class="w-full md:w-[55%] p-6 flex flex-col bg-white dark:bg-[#1a1c23] overflow-y-auto"
				>
					<div class="flex items-center justify-between mb-1">
						<h2 class="text-xl font-bold text-gray-900 dark:text-white">
							{{ rightPanelHeading }}
						</h2>
					</div>
					<p class="text-sm text-gray-500 dark:text-gray-400 mb-5">
						{{ rightPanelSubtext }}
					</p>

					<!-- SALE MODE: Sales Associates -->
					<div v-if="mode === 'sale'" class="mb-4">
						<button
							@click="showSalespersons = !showSalespersons"
							class="w-full flex items-center justify-between p-3 border rounded-xl transition-all"
							:class="
								cart.salespersons.length > 0
									? 'border-[#D4AF37] bg-[#D4AF37]/10'
									: 'border-gray-200 hover:border-gray-400 dark:border-warm-border dark:hover:border-white/30'
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
									<span class="font-medium text-gray-900 dark:text-white text-sm"
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
							class="mt-2 bg-gray-50 dark:bg-warm-dark-700 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50 space-y-3"
						>
							<div
								v-for="(sp, idx) in cart.salespersons"
								:key="idx"
								class="flex items-center gap-2"
							>
								<select
									v-model="sp.employee"
									class="flex-1 px-3 py-2 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-sm"
								>
									<option value="" disabled>Select Associate</option>
									<option
										v-for="emp in salesAssociates.data"
										:key="emp.name"
										:value="emp.name"
									>
										{{ emp.employee_name }} ({{ emp.designation || 'Sales' }})
									</option>
								</select>
								<div class="flex items-center gap-1">
									<input
										v-model.number="sp.split"
										@input="cart.recalculateSalespersonSplit(idx)"
										type="number"
										min="0"
										max="100"
										class="w-16 px-2 py-2 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-right font-mono"
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
								v-if="cart.salespersons.length < cart.maxSalespersons"
								@click="cart.addSalesperson('', null)"
								class="w-full py-2 text-sm font-medium text-[#D4AF37] border border-dashed border-[#D4AF37]/40 rounded-lg hover:bg-[#D4AF37]/10 transition"
							>
								+ Add Associate
							</button>
							<div
								v-if="
									cart.salespersons.length > 0 &&
									Math.abs(salespersonSplitTotal - 100) > 0.01
								"
								class="text-xs text-red-500 font-medium"
							>
								Splits must total 100% (currently {{ salespersonSplitTotal }}%)
							</div>
						</div>
					</div>

					<!-- Payment Methods (filtered per mode, grouped by category) -->
					<div class="flex-1 overflow-y-auto mb-5 pr-1">
						<!-- Standard Payment Methods -->
						<h4
							v-if="mode === 'sale'"
							class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2"
						>
							Standard
						</h4>
						<div class="space-y-2 mb-4">
							<button
								type="button"
								v-for="pm in standardModes"
								:key="pm.value"
								@click="togglePaymentMode(pm.value)"
								class="w-full flex items-center justify-between p-3.5 border rounded-xl transition-all"
								:class="
									isPaymentSelected(pm.value)
										? 'border-[#D4AF37] bg-[#D4AF37]/10 ring-1 ring-[#D4AF37]'
										: 'border-gray-200 hover:border-gray-400 dark:border-warm-border dark:hover:border-white/30'
								"
							>
								<div class="flex items-center gap-3">
									<div
										class="w-8 h-8 rounded-full flex items-center justify-center"
										:class="
											pm.value === 'Cash'
												? 'bg-green-100 text-green-600'
												: 'bg-blue-100 text-blue-600'
										"
									>
										<svg
											v-if="pm.value === 'Cash'"
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
										>{{ pm.label }}</span
									>
								</div>
								<div
									v-if="isPaymentSelected(pm.value)"
									class="w-2.5 h-2.5 rounded-full bg-green-500"
								></div>
							</button>
						</div>

						<!-- Show More Toggle -->
						<button
							v-if="mode === 'sale'"
							@click="showMoreModes = !showMoreModes"
							class="w-full py-2 text-xs font-bold text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition flex items-center justify-center gap-1"
						>
							<svg
								class="w-3 h-3 transition-transform"
								:class="showMoreModes ? 'rotate-180' : ''"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M19 9l-7 7-7-7"
								/>
							</svg>
							{{ showMoreModes ? 'Show fewer options' : 'More payment options' }}
						</button>

						<!-- Digital Wallets (collapsible) -->
						<template v-if="showMoreModes">
							<h4
								v-if="mode === 'sale'"
								class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2"
							>
								Digital Wallets
							</h4>
							<div class="space-y-2 mb-4">
								<button
									type="button"
									v-for="pm in digitalWalletModes"
									:key="pm.value"
									@click="togglePaymentMode(pm.value)"
									class="w-full flex items-center justify-between p-3.5 border rounded-xl transition-all"
									:class="
										isPaymentSelected(pm.value)
											? 'border-[#D4AF37] bg-[#D4AF37]/10 ring-1 ring-[#D4AF37]'
											: 'border-gray-200 hover:border-gray-400 dark:border-warm-border dark:hover:border-white/30'
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
													d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
												></path>
											</svg>
										</div>
										<span
											class="font-medium text-gray-900 dark:text-white text-sm"
											>{{ pm.label }}</span
										>
									</div>
									<div
										v-if="isPaymentSelected(pm.value)"
										class="w-2.5 h-2.5 rounded-full bg-green-500"
									></div>
								</button>
							</div>

							<h4
								v-if="mode === 'sale'"
								class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2"
							>
								Stored Value
							</h4>
							<div class="space-y-2 mb-4">
								<button
									type="button"
									v-for="pm in storedValueModes"
									:key="pm.value"
									@click="togglePaymentMode(pm.value)"
									class="w-full flex items-center justify-between p-3.5 border rounded-xl transition-all"
									:class="
										isPaymentSelected(pm.value)
											? 'border-[#D4AF37] bg-[#D4AF37]/10 ring-1 ring-[#D4AF37]'
											: 'border-gray-200 hover:border-gray-400 dark:border-warm-border dark:hover:border-white/30'
									"
								>
									<div class="flex items-center gap-3">
										<div
											class="w-8 h-8 rounded-full flex items-center justify-center bg-orange-100 text-orange-600"
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
												></path>
											</svg>
										</div>
										<span
											class="font-medium text-gray-900 dark:text-white text-sm"
											>{{ pm.label }}</span
										>
									</div>
									<div
										v-if="isPaymentSelected(pm.value)"
										class="w-2.5 h-2.5 rounded-full bg-green-500"
									></div>
								</button>
							</div>

							<!-- Financing Options -->
							<h4
								v-if="mode === 'sale'"
								class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2"
							>
								Financing
							</h4>
							<div class="space-y-2 mb-4">
								<button
									type="button"
									v-for="pm in financingModes"
									:key="pm.value"
									@click="togglePaymentMode(pm.value)"
									class="w-full flex items-center justify-between p-3.5 border rounded-xl transition-all"
									:class="
										isPaymentSelected(pm.value)
											? 'border-[#D4AF37] bg-[#D4AF37]/10 ring-1 ring-[#D4AF37]'
											: 'border-gray-200 hover:border-gray-400 dark:border-warm-border dark:hover:border-white/30'
									"
								>
									<div class="flex items-center gap-3">
										<div
											class="w-8 h-8 rounded-full flex items-center justify-center bg-indigo-100 text-indigo-600"
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
													d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
												></path>
											</svg>
										</div>
										<div class="text-left">
											<span
												class="font-medium text-gray-900 dark:text-white text-sm"
												>{{ pm.label }}</span
											>
											<span
												v-if="pm.value !== 'In-House Finance'"
												class="text-xs text-gray-400 block"
												>Apply for financing</span
											>
										</div>
									</div>
									<div
										v-if="isPaymentSelected(pm.value)"
										class="w-2.5 h-2.5 rounded-full bg-green-500"
									></div>
								</button>
								<button
									@click="showFinancingWaterfall = true"
									class="w-full flex items-center justify-center gap-2 p-3 border-2 border-dashed border-indigo-300 dark:border-indigo-700 rounded-xl text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all"
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
											d="M13 10V3L4 14h7v7l9-11h-7z"
										></path>
									</svg>
									<span class="font-medium text-sm"
										>Quick Apply (Waterfall)</span
									>
								</button>
							</div>
						</template>
					</div>

					<!-- Gift Card Number Input (sale mode only) -->
					<div
						v-if="mode === 'sale' && isPaymentSelected('Gift Card')"
						class="bg-gray-50 dark:bg-warm-dark-700 rounded-xl p-4 mb-4 border border-gray-100 dark:border-warm-border/50"
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
								class="flex-1 px-3 py-2 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-sm font-mono"
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
							<span v-if="giftCardInfo.valid"
								>Balance: {{ formatCurrency(giftCardInfo.balance) }}</span
							>
							<span v-else>{{ giftCardInfo.message }}</span>
						</div>
					</div>

					<!-- Split Amounts (sale mode, multiple payments) -->
					<div
						v-if="mode === 'sale' && selectedPayments.length > 1"
						class="bg-gray-50 dark:bg-warm-dark-700 rounded-xl p-4 mb-4 border border-gray-100 dark:border-warm-border/50"
					>
						<h4 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
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
									class="w-24 px-2 py-1 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded text-right font-mono text-sm"
									min="0"
									:max="totalAmount"
								/>
							</div>
						</div>
						<div
							class="flex justify-between text-sm pt-2 border-t border-gray-200 dark:border-warm-border mt-2"
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

					<!-- Terminal Device Selector (shown when card payment is selected) -->
					<div
						v-if="hasCardPaymentSelected && !cardPaymentActive"
						class="bg-blue-50 dark:bg-blue-900/10 rounded-xl p-4 mb-4 border border-blue-200 dark:border-blue-800/30"
						data-testid="terminal-device-selector"
					>
						<div class="flex items-center justify-between mb-2">
							<div class="flex items-center gap-2">
								<div class="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center">
									<svg class="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
									</svg>
								</div>
								<span class="text-sm font-medium text-blue-700 dark:text-blue-300">Card Reader</span>
							</div>
							<button
								v-if="!gateway.isTerminalReady.value"
								@click="discoverTerminalDevices"
								:disabled="deviceLoading"
								class="text-xs font-bold px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
							>
								{{ deviceLoading ? 'Searching...' : 'Find Readers' }}
							</button>
							<span v-else class="text-xs font-bold text-green-600 dark:text-green-400 flex items-center gap-1">
								<span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
								Connected
							</span>
						</div>

						<!-- Device List -->
						<div v-if="terminalDevices.length > 0 && !gateway.isTerminalReady.value" class="space-y-1 mt-2">
							<button
								v-for="device in terminalDevices"
								:key="device.id"
								@click="connectToDevice(device)"
								class="w-full flex items-center justify-between p-2 rounded-lg text-left transition"
								:class="device.is_online
									? 'bg-white dark:bg-[#0F1115] border border-blue-200 dark:border-blue-800/30 hover:border-blue-400'
									: 'bg-gray-100 dark:bg-gray-800 opacity-50 cursor-not-allowed'"
								:disabled="!device.is_online"
							>
								<div>
									<span class="text-sm font-medium text-gray-900 dark:text-white">{{ device.label || device.name }}</span>
									<span class="text-xs text-gray-400 block">{{ device.device_type || device.type || 'Terminal' }}</span>
								</div>
								<span
									class="w-2 h-2 rounded-full"
									:class="device.is_online ? 'bg-green-500' : 'bg-gray-400'"
								></span>
							</button>
						</div>

						<!-- No gateway message -->
						<p v-if="gateway.error.value && !gateway.isTerminalReady.value" class="text-xs text-red-500 mt-1">
							{{ gateway.error.value }}
						</p>

						<p v-if="!gateway.isTerminalReady.value && terminalDevices.length === 0 && !deviceLoading" class="text-xs text-blue-500 dark:text-blue-400 mt-1">
							Click "Find Readers" to discover available card readers, or proceed without to record a manual card payment.
						</p>
					</div>

					<!-- Card Payment Status Overlay (during terminal payment) -->
					<div
						v-if="cardPaymentActive"
						class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 mb-4 border border-blue-200 dark:border-blue-800/30 text-center"
						data-testid="card-payment-status"
					>
						<div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
							:class="gateway.status.value === 'succeeded'
								? 'bg-green-100 dark:bg-green-900/30'
								: gateway.status.value === 'failed'
								? 'bg-red-100 dark:bg-red-900/30'
								: 'bg-blue-100 dark:bg-blue-900/30'"
						>
							<div v-if="!['succeeded', 'failed', 'canceled'].includes(gateway.status.value)"
								class="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"
							></div>
							<svg v-else-if="gateway.status.value === 'succeeded'" class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
							</svg>
							<svg v-else class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</div>
						<h3 class="font-bold text-gray-900 dark:text-white mb-1">
							{{ terminalStatusTitle }}
						</h3>
						<p class="text-sm text-gray-500 dark:text-gray-400">
							{{ gateway.statusMessage.value || 'Processing...' }}
						</p>
						<button
							v-if="gateway.isProcessing.value"
							@click="cancelTerminalPayment"
							class="mt-4 px-4 py-2 text-sm font-medium text-red-600 border border-red-200 dark:border-red-800/30 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/10 transition"
						>
							Cancel
						</button>
					</div>

					<!-- Confirm Button -->
					<div class="flex-shrink-0 mt-6">
						<button
							type="button"
							@click="handlePayment"
							:disabled="!canSubmit || processing"
							class="w-full flex items-center justify-center gap-2 py-4 rounded-xl font-bold transition-all shadow-md"
							:class="
								canSubmit && !processing
									? 'bg-[#D4AF37] text-black hover:bg-[#b5952f] cursor-pointer'
									: 'bg-gray-100 text-gray-400 dark:bg-warm-dark-700 dark:text-gray-500 cursor-not-allowed'
							"
							data-testid="confirm-payment-btn"
						>
							<span
								v-if="processing"
								class="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-white"
							></span>
							<span v-else>{{ confirmButtonLabel }}</span>
						</button>
					</div>
				</div>
			</div>
		</template>

		<!-- ============ IRS 8300 COMPLIANCE FORM ============ -->
		<template v-if="step === 'irs_8300_form'">
			<div class="p-8 max-w-3xl mx-auto min-h-[500px]">
				<div class="mb-6 flex items-center justify-between">
					<div class="flex items-center gap-3">
						<div class="w-12 h-12 bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-500 rounded-full flex items-center justify-center flex-shrink-0">
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
							</svg>
						</div>
						<div>
							<h2 class="text-xl font-bold text-gray-900 dark:text-white">IRS Form 8300 Required</h2>
							<p class="text-sm text-gray-500 dark:text-gray-400">
								This transaction involves more than $10,000 in cash. Compliance requires we record the customer's identity before completing the transaction.
							</p>
						</div>
					</div>
					<button
						type="button"
						@click="showIdScanner = !showIdScanner"
						class="flex items-center gap-2 px-4 py-2 bg-[#D4AF37]/10 text-[#D4AF37] hover:bg-[#D4AF37]/20 rounded-lg text-sm font-bold transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
						</svg>
						Scan ID
					</button>
				</div>

				<IDScannerPanel
					:show="showIdScanner"
					v-model="scannedIdData"
					@close="showIdScanner = false"
					@apply-data="applyScannedIdData"
				/>

				<div class="bg-white dark:bg-[#15171e] p-6 border border-gray-200 dark:border-warm-border rounded-xl shadow-sm space-y-4">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div class="space-y-1">
							<label class="block text-xs font-medium text-gray-700 dark:text-gray-300">Recipient Full Name</label>
							<input v-model="irs8300Details.recipient_name" type="text" class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]" placeholder="John Doe">
						</div>
						<div class="space-y-1">
							<label class="block text-xs font-medium text-gray-700 dark:text-gray-300">TIN / SSN</label>
							<input v-model="irs8300Details.recipient_tin" type="text" class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]" placeholder="XXX-XX-XXXX">
						</div>
						<div class="space-y-1">
							<label class="block text-xs font-medium text-gray-700 dark:text-gray-300">Date of Birth</label>
							<input v-model="irs8300Details.recipient_dob" type="date" class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]">
						</div>
						<div class="space-y-1">
							<label class="block text-xs font-medium text-gray-700 dark:text-gray-300">Address</label>
							<input v-model="irs8300Details.recipient_address" type="text" class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]" placeholder="123 Main St, City, State, Zip">
						</div>
						<div class="space-y-1">
							<label class="block text-xs font-medium text-gray-700 dark:text-gray-300">ID Type</label>
							<select v-model="irs8300Details.recipient_id_type" class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]">
								<option value="">Select ID Type</option>
								<option value="Driver's License">Driver's License</option>
								<option value="Passport">Passport</option>
								<option value="State ID">State ID</option>
								<option value="National ID">National ID</option>
								<option value="Other">Other</option>
							</select>
						</div>
						<div class="space-y-1">
							<label class="block text-xs font-medium text-gray-700 dark:text-gray-300">ID Number</label>
							<input v-model="irs8300Details.recipient_id_number" type="text" class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]" placeholder="ID Number">
						</div>
					</div>
					
					<!-- Bypass Section -->
					<div class="mt-8 p-4 bg-gray-50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border/50 rounded-lg">
						<h4 class="text-sm font-bold text-gray-900 dark:text-gray-200 mb-2 flex items-center gap-2">
							Manager Bypass
							<span class="text-xs font-normal text-gray-500">(Optional - Protects Cashier)</span>
						</h4>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div class="space-y-1">
								<label class="block text-xs font-medium text-gray-700 dark:text-gray-400">Bypass Authorized By</label>
								<input v-model="irs8300Details.bypassed_by" type="text" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]" placeholder="Manager Name or PIN">
							</div>
							<div class="space-y-1">
								<label class="block text-xs font-medium text-gray-700 dark:text-gray-400">Bypass Reason</label>
								<input v-model="irs8300Details.bypass_reason" type="text" class="w-full px-3 py-2 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#D4AF37]" placeholder="e.g. Customer in rush, fill later">
							</div>
						</div>
					</div>
				</div>

				<div class="mt-6 flex flex-col sm:flex-row gap-3 justify-end">
					<button
						type="button"
						@click="step = 'review'"
						class="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-warm-dark-800 transition"
					>
						Back
					</button>
					<button
						type="button"
						@click="processFinalPayment"
						:disabled="processing"
						class="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-warm-dark-700 dark:hover:bg-warm-dark-600 text-gray-800 dark:text-gray-200 rounded-lg text-sm font-medium transition flex items-center justify-center min-w-[120px]"
					>
						<span v-if="processing" class="animate-spin rounded-full h-4 w-4 border-2 border-gray-400 border-t-transparent"></span>
						<span v-else>Skip & Pay</span>
					</button>
					<button
						type="button"
						@click="processFinalPayment"
						:disabled="processing"
						class="px-6 py-2 bg-[#D4AF37] hover:bg-[#b5952f] text-black rounded-lg text-sm font-bold transition flex items-center justify-center min-w-[160px]"
					>
						<span v-if="processing" class="animate-spin rounded-full h-4 w-4 border-2 border-black border-t-transparent"></span>
						<span v-else>Submit & Pay</span>
					</button>
				</div>
			</div>
		</template>

		<!-- ============ SUCCESS STATE ============ -->
		<template v-if="step === 'success'">
			<div
				class="p-12 flex flex-col items-center justify-center text-center w-full"
				style="min-height: 400px"
				data-testid="success-message"
			>
				<div
					class="w-20 h-20 rounded-full flex items-center justify-center mb-6"
					:class="
						isOfflineOrder
							? 'bg-amber-100 dark:bg-amber-900/30'
							: 'bg-green-100 dark:bg-green-900/30'
					"
				>
					<svg
						:class="
							isOfflineOrder
								? 'w-10 h-10 text-amber-600 dark:text-amber-400'
								: 'w-10 h-10 text-green-600 dark:text-green-400'
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
						/>
					</svg>
				</div>
				<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
					{{ successTitle }}
				</h2>
				<p class="text-gray-500 dark:text-gray-400 mb-6">{{ successSubtext }}</p>

				<div
					v-if="form8300Triggered"
					class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-4 mb-6 w-full max-w-sm text-left"
				>
					<div class="flex items-start gap-3">
						<svg class="w-6 h-6 text-red-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
						</svg>
						<div>
							<h4 class="text-sm font-bold text-red-800 dark:text-red-400">IRS Form 8300 Required</h4>
							<p class="text-xs text-red-600 dark:text-red-300 mt-1">
								Cash payments exceed $10,000. An IRS Form 8300 record has been generated. Please ensure the customer's identity is verified.
							</p>
						</div>
					</div>
				</div>

				<div
					class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-5 w-full max-w-sm mb-6 border border-gray-100 dark:border-warm-border/50 space-y-2"
				>
					<div
						v-for="(p, idx) in successBreakdown"
						:key="idx"
						class="flex justify-between text-sm py-2"
						:class="{ 'border-t border-gray-200 dark:border-warm-border': idx > 0 }"
					>
						<span class="text-gray-500 dark:text-gray-400">{{
							p.mode_of_payment
						}}</span>
						<span class="font-bold text-gray-900 dark:text-white">{{
							formatCurrency(p.amount)
						}}</span>
					</div>
					<div
						class="flex justify-between text-sm pt-3 mt-2 border-t border-gray-200 dark:border-warm-border"
					>
						<span class="font-bold text-gray-900 dark:text-white">{{
							mode === 'sale' ? 'Total Paid' : 'Total Paid'
						}}</span>
						<span class="font-bold text-[#D4AF37]">{{
							formatCurrency(successBreakdown.reduce((s, p) => s + p.amount, 0))
						}}</span>
					</div>
					<div
						v-if="successInvoiceId"
						class="flex justify-between text-sm pt-3 mt-2 border-t border-gray-200 dark:border-warm-border"
						data-testid="invoice-id"
					>
						<span class="text-gray-500 dark:text-gray-400">Transaction ID</span>
						<span class="font-mono font-bold text-gray-900 dark:text-white">{{
							successInvoiceId
						}}</span>
					</div>
				</div>

				<div class="flex gap-3 w-full max-w-sm">
					<button
						type="button"
						@click="close"
						class="flex-1 py-3 rounded-xl font-bold bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black hover:bg-gray-800 dark:hover:bg-[#b5952f] transition"
					>
						{{ mode === 'sale' ? 'New Order' : 'Done' }}
					</button>
					<button
						type="button"
						v-if="mode === 'sale'"
						@click="printReceipt"
						class="flex-1 py-3 rounded-xl font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-warm-dark-700 dark:text-gray-300 dark:hover:bg-white/10 transition flex items-center justify-center gap-2"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
							></path>
						</svg>
						Print Receipt
					</button>
				</div>
			</div>
		</template>
	</BaseModal>

	<!-- Financing Waterfall Modal -->
	<FinancingApplicationModal
		:show="showFinancingWaterfall"
		:customer="cart.customerId"
		:amount="totalAmount"
		@close="showFinancingWaterfall = false"
		@approved="onFinancingApproved"
	/>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { createResource, call } from 'frappe-ui'
import { useCartStore } from '@/stores/cart.js'
import { useSessionStore } from '@/stores/session.js'
import { useOfflineStore } from '@/stores/offline.js'
import { hardwareService } from '@/services/HardwareService.js'
import { usePaymentGateway } from '@/composables/usePaymentGateway.js'
import BaseModal from './BaseModal.vue'
import FinancingApplicationModal from './FinancingApplicationModal.vue'
import IDScannerPanel from './IDScannerPanel.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	mode: {
		type: String,
		default: 'sale',
		validator: (v) => ['sale', 'layaway', 'repair'].includes(v),
	},
	referenceId: { type: String, default: null },
	balanceAmount: { type: Number, default: 0 },
	itemDetails: { type: Object, default: null },
	draftMode: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'success'])

const cart = useCartStore()
const session = useSessionStore()
const offlineStore = useOfflineStore()

const processing = ref(false)
const showMoreModes = ref(false)
const error = ref('')
const step = ref('review')
const selectedPayments = ref([])
const taxExempt = ref(false)
const showSalespersons = ref(false)
const successBreakdown = ref([])
const successInvoiceId = ref(null)
const form8300Triggered = ref(false)

const giftCardNumber = ref('')
const giftCardInfo = ref(null)
const giftCardLoading = ref(false)
const showFinancingWaterfall = ref(false)

// ── IRS Form 8300 Compliance ──
const irs8300Details = ref({
	recipient_name: '',
	recipient_tin: '',
	recipient_dob: '',
	recipient_id_type: '',
	recipient_id_number: '',
	recipient_address: '',
	bypass_reason: '',
	bypassed_by: ''
})

const showIdScanner = ref(false)
const scannedIdData = ref({ type: '', number: '', name: '', address: '', dob: '' })

function applyScannedIdData() {
	if (scannedIdData.value.name) irs8300Details.value.recipient_name = scannedIdData.value.name
	if (scannedIdData.value.address) irs8300Details.value.recipient_address = scannedIdData.value.address
	if (scannedIdData.value.number) irs8300Details.value.recipient_id_number = scannedIdData.value.number
	if (scannedIdData.value.dob) irs8300Details.value.recipient_dob = scannedIdData.value.dob
	
	if (scannedIdData.value.type === 'drivers_license') irs8300Details.value.recipient_id_type = "Driver's License"
	else if (scannedIdData.value.type === 'passport') irs8300Details.value.recipient_id_type = 'Passport'
	else if (scannedIdData.value.type === 'state_id') irs8300Details.value.recipient_id_type = 'State ID'
	else if (scannedIdData.value.type === 'national_id') irs8300Details.value.recipient_id_type = 'National ID'
	
	showIdScanner.value = false
}

// ── Payment Terminal Integration ──
const gateway = usePaymentGateway()
const showDeviceSelector = ref(false)
const terminalDevices = ref([])
const deviceLoading = ref(false)
const cardPaymentActive = ref(false)

const salesAssociates = createResource({
	url: 'zevar_core.api.sales_associates.get_sales_associates',
	initialData: [],
	auto: props.mode === 'sale',
})

const salespersonSplitTotal = computed(() =>
	cart.salespersons.reduce((sum, sp) => sum + (sp.split || 0), 0)
)
const tradeInTotal = computed(() =>
	cart.tradeIns.reduce((sum, ti) => sum + (ti.trade_in_value || 0), 0)
)

const totalAmount = computed(() => {
	if (props.mode === 'sale') {
		const base = taxExempt.value ? cart.subtotal : cart.subtotal + cart.tax
		return Number(Math.max(0, base - tradeInTotal.value).toFixed(2))
	}
	return props.balanceAmount || 0
})

const allPaymentModes = [
	{ value: 'Cash', label: 'Cash', category: 'standard' },
	{ value: 'Credit Card', label: 'Credit Card', category: 'standard' },
	{ value: 'Debit Card', label: 'Debit Card', category: 'standard' },
	{ value: 'Check', label: 'Check', category: 'standard' },
	{ value: 'Apple Pay', label: 'Apple Pay', category: 'digital' },
	{ value: 'Google Pay', label: 'Google Pay', category: 'digital' },
	{ value: 'Venmo', label: 'Venmo', category: 'digital' },
	{ value: 'Zelle', label: 'Zelle', category: 'digital' },
	{ value: 'Cash App', label: 'Cash App', category: 'digital' },
	{ value: 'Gift Card', label: 'Gift Card', category: 'stored_value' },
	{ value: 'Wire Transfer', label: 'Wire Transfer', category: 'standard' },
	{ value: 'Synchrony', label: 'Synchrony', category: 'financing' },
	{ value: 'AFF', label: 'American First Finance', category: 'financing' },
	{ value: 'Progressive', label: 'Progressive Leasing', category: 'financing' },
	{ value: 'Snap', label: 'Snap Finance', category: 'financing' },
	{ value: 'CIMA', label: 'Acima', category: 'financing' },
	{ value: 'Trade-In', label: 'Trade-In Credit', category: 'stored_value' },
	{ value: 'In-House Finance', label: 'In-House Finance', category: 'financing' },
]

const activePaymentModes = computed(() => allPaymentModes)
const standardModes = computed(() => allPaymentModes.filter((m) => m.category === 'standard'))
const digitalWalletModes = computed(() => allPaymentModes.filter((m) => m.category === 'digital'))
const storedValueModes = computed(() =>
	allPaymentModes.filter((m) => m.category === 'stored_value')
)
const financingModes = computed(() => allPaymentModes.filter((m) => m.category === 'financing'))

const remainingAmount = computed(() => {
	const totalPaid = selectedPayments.value.reduce((sum, p) => sum + (Number(p.amount) || 0), 0)
	return Number((totalAmount.value - totalPaid).toFixed(2))
})

const canSubmit = computed(() => {
	if (processing.value || selectedPayments.value.length === 0) return false
	if (
		props.mode === 'sale' &&
		cart.salespersons.length > 0 &&
		Math.abs(salespersonSplitTotal.value - 100) > 0.01
	)
		return false
	if (selectedPayments.value.length === 1) return true
	return Math.abs(remainingAmount.value) < 0.01
})

const leftPanelTitle = computed(() => {
	if (props.mode === 'sale') return 'Items in Bag'
	if (props.mode === 'layaway') return 'Layaway Payment'
	return 'Repair Payment'
})

const rightPanelHeading = computed(() => {
	if (props.mode === 'sale') return 'Payment'
	if (props.mode === 'layaway') return 'Layaway Payment'
	return 'Repair Payment'
})

const rightPanelSubtext = computed(() => {
	if (props.mode === 'sale') return 'Select payment method(s). Split payments allowed.'
	if (props.mode === 'layaway') return 'Make a payment toward the layaway balance.'
	return 'Record a payment toward the repair balance.'
})

const confirmButtonLabel = computed(() => {
	if (props.mode === 'sale') return `Confirm ${formatCurrency(totalAmount.value)}`
	if (props.mode === 'layaway') return `Pay ${formatCurrency(totalAmount.value)}`
	return `Record ${formatCurrency(totalAmount.value)}`
})

const isOfflineOrder = computed(() => successInvoiceId.value === 'QUEUED-OFFLINE')

const successTitle = computed(() => {
	if (isOfflineOrder.value) return 'Order Saved Offline'
	if (props.mode === 'sale') return 'Payment Successful!'
	if (props.mode === 'layaway') return 'Layaway Payment Recorded!'
	return 'Repair Payment Recorded!'
})

const successSubtext = computed(() => {
	if (isOfflineOrder.value)
		return "This order will be synced automatically when you're back online."
	if (props.mode === 'sale') return 'Invoice has been generated successfully.'
	if (props.mode === 'layaway') return 'Layaway payment has been processed.'
	return 'Repair payment has been recorded.'
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
			selectedPayments.value.push({ mode, amount: totalAmount.value })
		} else {
			selectedPayments.value.push({ mode, amount: null })
		}
	}
}

function recalculateSplit(changedMode) {
	const changed = selectedPayments.value.find((p) => p.mode === changedMode)
	if (changed) changed.amount = Number(Number(changed.amount || 0).toFixed(2))
	if (props.mode === 'sale' && changedMode === 'Gift Card' && giftCardInfo.value?.valid) {
		if (changed && changed.amount > giftCardInfo.value.balance)
			changed.amount = Number(giftCardInfo.value.balance.toFixed(2))
	}
	if (selectedPayments.value.length === 2 && changed) {
		const other = selectedPayments.value.find((p) => p.mode !== changedMode)
		if (other) other.amount = Number((totalAmount.value - changed.amount).toFixed(2))
	}
}

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
		if (data.valid) {
			const gc = selectedPayments.value.find((p) => p.mode === 'Gift Card')
			if (gc && gc.amount > data.balance) gc.amount = data.balance
		}
	} catch {
		giftCardInfo.value = { valid: false, message: 'Failed to lookup card' }
	} finally {
		giftCardLoading.value = false
	}
}

async function handlePayment() {
	if (!canSubmit.value) return

	if (props.mode === 'sale') {
		await session.posSessionResource.fetch()
		const canBypassSession = session.hasAnyRole([
			'Sales Manager',
			'Store Manager',
			'System Manager',
		])
		if (!session.hasActiveSession && !canBypassSession) {
			error.value =
				'You must open a POS session before making sales. Please open a register first.'
			return
		}

		const gc = selectedPayments.value.find((p) => p.mode === 'Gift Card')
		if (gc && (!giftCardInfo.value?.valid || !giftCardNumber.value)) {
			error.value = 'Please enter and verify a valid Gift Card number.'
			return
		}
		if (gc && gc.amount > (giftCardInfo.value?.balance || 0)) {
			error.value = 'Gift Card amount exceeds available balance.'
			return
		}
	}

	// ── PRE-CHECK: IRS Form 8300 ──
	// If it's a cash transaction, check if it pushes them over $10,000 before proceeding
	const cashPayment = selectedPayments.value.find(p => p.mode === 'Cash')
	if (cashPayment && cashPayment.amount > 0 && (props.mode === 'sale' || props.mode === 'layaway')) {
		try {
			processing.value = true
			const customerId = props.mode === 'sale' ? (cart.customer?.name || 'Walk-In Customer') : cart.customerId
			
			// Only check for registered customers (Walk-ins might just pass 'Walk-In Customer' which we handle in backend)
			if (customerId && customerId !== 'Walk-In Customer') {
				const res = await call('zevar_core.api.compliance.check_pre_8300_status', {
					customer: customerId,
					cash_amount: cashPayment.amount
				})
				if (res?.triggered) {
					step.value = 'irs_8300_form'
					processing.value = false
					return // Stop payment flow and show form
				}
			}
		} catch (e) {
			console.error('Failed to pre-check IRS 8300 status', e)
		} finally {
			processing.value = false
		}
	}

	// If no 8300 triggered, proceed to final payment
	await processFinalPayment()
}

async function processFinalPayment() {
	// Check if any card-based payment is selected
	const cardModes = ['Credit Card', 'Debit Card', 'Apple Pay', 'Google Pay']
	const cardPayment = selectedPayments.value.find(p => cardModes.includes(p.mode))

	// If card payment and we have a terminal connected, use the terminal flow
	if (cardPayment && gateway.isTerminalReady.value && cardPayment.amount > 0) {
		try {
			cardPaymentActive.value = true
			processing.value = true
			error.value = ''

			const terminalResult = await gateway.collectPayment({
				amount: cardPayment.amount,
				invoiceName: props.mode === 'sale' ? null : props.referenceId,
				description: props.mode === 'sale'
					? `POS Sale - ${cart.items.length} items`
					: `${props.mode} payment - ${props.referenceId}`,
			})

			if (!terminalResult.success) {
				if (terminalResult.canceled) {
					error.value = 'Card payment was canceled.'
				} else {
					error.value = terminalResult.error || 'Card payment failed.'
				}
				processing.value = false
				cardPaymentActive.value = false
				return
			}

			// Terminal payment succeeded — attach reference to the payment
			cardPayment.reference_no = terminalResult.paymentIntentId || terminalResult.paymentId || ''
			cardPaymentActive.value = false
			// Fall through to the normal submission flow below
		} catch (e) {
			error.value = e.message || 'Card payment failed unexpectedly.'
			processing.value = false
			cardPaymentActive.value = false
			return
		}
	}

	error.value = ''
	processing.value = true

	try {
		const payments = selectedPayments.value
			.filter((sp) => sp.amount > 0)
			.map((sp) => ({ mode_of_payment: sp.mode, amount: sp.amount }))

		if (props.draftMode) {
			emit('success', { success: true, payments })
			processing.value = false
			return
		}

		if (props.mode === 'sale') {
			const gcPayment = selectedPayments.value.find((p) => p.mode === 'Gift Card')
			// Use submitOrderSafe so auth-expiry errors come back with a
			// stable {code: 'session_expired'} shape and DON'T fall through
			// to the offline-queue branch (which would mask the real issue).
			const result = await cart.submitOrderSafe(selectedPayments.value, {
				taxExempt: taxExempt.value,
				warehouse: session.currentWarehouse,
				giftCardNumber: gcPayment ? giftCardNumber.value : undefined,
				irs8300Details: step.value === 'irs_8300_form' ? irs8300Details.value : undefined
			})
			const invoiceName = result?.invoice_name || result?.data?.invoice_name
			successInvoiceId.value = invoiceName || null
			successBreakdown.value = payments
			step.value = 'success'
			form8300Triggered.value = !!(result?.form_8300_triggered || result?.data?.form_8300_triggered)
			emit('success', result)
		} else if (props.mode === 'layaway') {
			const splitPaymentResource = createResource({
				url: 'zevar_core.api.layaway.process_split_layaway_payment',
				auto: false,
			})
			const rawResult = await splitPaymentResource.submit({
				layaway_id: props.referenceId,
				payments: JSON.stringify(payments),
				irs_8300_details: step.value === 'irs_8300_form' ? JSON.stringify(irs8300Details.value) : undefined
			})
			const result = rawResult?.message ?? rawResult
			if (result?.success) {
				successBreakdown.value = result.payment_breakdown || payments
				successInvoiceId.value = props.referenceId
				step.value = 'success'
				form8300Triggered.value = !!(result?.form_8300_triggered || result?.data?.form_8300_triggered)
				emit('success', result)
			} else {
				throw new Error(result?.message || 'Layaway payment failed')
			}
		} else if (props.mode === 'repair') {
			const primary = payments[0]
			const result = await call('zevar_core.api.add_repair_payment', {
				repair_order: props.referenceId,
				amount: primary.amount,
				payment_method: primary.mode_of_payment,
			})
			successBreakdown.value = payments
			successInvoiceId.value = props.referenceId
			step.value = 'success'
			emit('success', result)
		}
	} catch (e) {
		// Detect network failures and offer offline queuing
		const errMessage = (e?.message || '').toLowerCase()
		const isNetworkError =
			!navigator.onLine ||
			(e instanceof TypeError && (
				errMessage.includes('fetch') ||
				errMessage.includes('network') ||
				errMessage.includes('load failed')
			)) ||
			errMessage.includes('err_internet') ||
			errMessage.includes('networkerror') ||
			errMessage.includes('failed to fetch') ||
			errMessage.includes('net::err_')

		// Auth-expired error from submitOrderSafe (Fix #8): bubble a clear
		// message and DO NOT fall through to the offline-queue branch —
		// queueing here would silently retry on reconnect against an
		// already-expired session and surface as a confusing failure later.
		// The cart is preserved either way (Fix #8 never clears it on
		// failure).
		if (e?.code === 'session_expired') {
			error.value = 'Your session has expired. Please log in again — your cart is saved.'
			return
		}

		if (isNetworkError && (props.mode === 'sale' || props.mode === 'layaway' || props.mode === 'repair')) {
			// Queue for offline sync — all payment modes supported
			try {
				const payments = selectedPayments.value
					.filter((sp) => sp.amount > 0)
					.map((sp) => ({ mode_of_payment: sp.mode, amount: sp.amount }))

				const payload = {
					payments: JSON.stringify(payments),
					customer: cart.customer?.name || 'Walk-In Customer',
					warehouse: session.currentWarehouse || '',
					tax_exempt: taxExempt.value,
				}

				// Mode-specific payload
				if (props.mode === 'sale') {
					payload.items = JSON.stringify(
						cart.items.map((i) => ({
							item_code: i.item_code,
							qty: i.qty || 1,
							rate: i.amount || 0,
							serial_no: i.serial_no || null,
						}))
					)

					// Include salespersons so commission is tracked after sync
					if (cart.salespersons.length > 0) {
						payload.salespersons = JSON.stringify(
							cart.salespersons.map((sp) => ({
								employee: sp.employee,
								split: sp.split,
							}))
						)
					}

					// Include trade-ins so credit is applied after sync
					if (cart.tradeIns.length > 0) {
						payload.trade_ins = JSON.stringify(
							cart.tradeIns.map((ti) => ({
								trade_in_value: ti.trade_in_value,
								new_item_value: ti.new_item_value,
								manager_override: ti.manager_override || '',
								override_reason: ti.override_reason || '',
							}))
						)
					}

					// Include gift card number if gift card payment is present
					const gcPayment = selectedPayments.value.find((p) => p.mode === 'Gift Card')
					if (gcPayment && giftCardNumber.value) {
						payload.gift_card_number = giftCardNumber.value
					}
				} else if (props.mode === 'layaway') {
					payload.layaway_id = props.referenceId
				} else if (props.mode === 'repair') {
					payload.repair_order = props.referenceId
					payload.amount = payments[0]?.amount || 0
					payload.payment_method = payments[0]?.mode_of_payment || 'Cash'
				}

				await offlineStore.addPendingOrder({
					mode: props.mode,
					payload,
				})

				successBreakdown.value = payments
				successInvoiceId.value = 'QUEUED-OFFLINE'
				step.value = 'success'
				emit('success', { success: true, offline: true })
				return
			} catch (queueError) {
				error.value = 'Network unavailable and failed to save offline. Please try again.'
				return
			}
		}

		let errorMsg = ''
		if (isNetworkError) {
			errorMsg = 'Network connection lost. Please check your internet and try again.'
		} else if (e?.exc_type === 'ValidationError' && e?.message) {
			errorMsg = e.message
		} else if (e?._server_messages) {
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
	} finally {
		processing.value = false
	}
}

function onFinancingApproved(result) {
	showFinancingWaterfall.value = false
	// Add financing as a payment mode
	const mode = result.provider
	const amount = result.approval_amount || totalAmount.value

	const existing = selectedPayments.value.findIndex((p) => p.mode === mode)
	if (existing >= 0) {
		selectedPayments.value[existing].amount = amount
	} else {
		selectedPayments.value.push({ mode, amount })
	}
	recalculateSplit(mode)
}

function printReceipt() {
	if (successInvoiceId.value) {
		hardwareService.printReceipt(successInvoiceId.value)
	}
}

watch(
	() => props.show,
	(isOpen) => {
		if (isOpen) {
			step.value = 'review'
			selectedPayments.value = []
			processing.value = false
			error.value = ''
			taxExempt.value = false
			showSalespersons.value = false
			giftCardNumber.value = ''
			giftCardInfo.value = null
			successBreakdown.value = []
			successInvoiceId.value = null
			form8300Triggered.value = false
		}
	}
)

function close() {
	emit('close')
	if (step.value === 'success' && props.mode === 'sale') {
		cart.clearCart()
	}
	step.value = 'review'
	gateway.reset()
	cardPaymentActive.value = false
}

// ── Terminal Integration Helpers ──

const hasCardPaymentSelected = computed(() => {
	const cardModes = ['Credit Card', 'Debit Card', 'Apple Pay', 'Google Pay']
	return selectedPayments.value.some(p => cardModes.includes(p.mode))
})

const terminalStatusTitle = computed(() => {
	const s = gateway.status.value
	const titles = {
		loading_sdk: 'Loading Terminal',
		discovering: 'Finding Readers',
		connecting: 'Connecting',
		creating_intent: 'Creating Payment',
		creating_checkout: 'Creating Payment',
		waiting_for_card: 'Waiting for Card',
		processing: 'Processing Payment',
		confirming: 'Confirming',
		succeeded: 'Payment Approved',
		failed: 'Payment Failed',
		canceled: 'Payment Canceled',
	}
	return titles[s] || 'Processing'
})

async function discoverTerminalDevices() {
	deviceLoading.value = true
	try {
		await gateway.detectGateway()
		const found = await gateway.loadDevices()
		terminalDevices.value = found || []
	} catch {
		// Error is displayed via gateway.error
	} finally {
		deviceLoading.value = false
	}
}

async function connectToDevice(device) {
	try {
		deviceLoading.value = true
		await gateway.selectDevice(device)
	} catch {
		// Error displayed via gateway.error
	} finally {
		deviceLoading.value = false
	}
}

async function cancelTerminalPayment() {
	await gateway.cancelPayment()
	cardPaymentActive.value = false
	processing.value = false
}

// Auto-detect gateway on mount (best-effort, non-blocking)
onMounted(() => {
	gateway.detectGateway().catch(() => {})
})

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}
</script>
