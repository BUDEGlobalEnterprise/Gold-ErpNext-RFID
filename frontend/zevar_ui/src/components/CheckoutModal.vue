<template>
	<BaseModal
		:show="show"
		:max-width="step === 'success' ? 'max-w-md' : 'max-w-5xl'"
		:no-max-height="step !== 'success'"
		:show-close="true"
		@close="close"
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
						>
							Select a payment method to begin
						</div>
					</template>

					<!-- Error -->
					<div
						v-if="error"
						class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-3 mt-3"
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
								v-if="cart.salespersons.length < 4"
								@click="cart.addSalesperson('', null)"
								class="w-full py-2 text-sm font-medium text-[#D4AF37] border border-dashed border-[#D4AF37]/40 rounded-lg hover:bg-[#D4AF37]/10 transition"
							>
								+ Add Associate
							</button>
							<div
								v-if="
									cart.salespersons.length > 0 && salespersonSplitTotal !== 100
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

						<!-- Digital Wallets -->
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

						<!-- Stored Value (Gift Card, Trade-In) -->
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
								<span class="font-medium text-sm">Quick Apply (Waterfall)</span>
							</button>
						</div>
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

					<!-- Confirm Button -->
					<div class="flex-shrink-0">
						<button
							type="button"
							@click="handlePayment"
							:disabled="!canSubmit || processing"
							class="w-full py-4 rounded-xl font-bold text-lg shadow-xl transition-all flex items-center justify-center gap-2 transform active:scale-95"
							:class="
								!canSubmit || processing
									? 'bg-gray-100 text-gray-400 cursor-not-allowed dark:bg-warm-dark-700 dark:text-gray-600'
									: 'bg-gray-900 text-white hover:bg-black dark:bg-[#D4AF37] dark:text-black dark:hover:bg-[#b5952f]'
							"
						>
							<span
								v-if="processing"
								class="animate-spin rounded-full h-5 w-5 border-2 border-gray-400 border-t-white"
							></span>
							<span v-else-if="!canSubmit">{{
								selectedPayments.length === 0 ? 'Select Payment' : 'Enter Amounts'
							}}</span>
							<span v-else>{{ confirmButtonLabel }}</span>
						</button>
					</div>
				</div>
			</div>
		</template>

		<!-- ============ SUCCESS STATE ============ -->
		<template v-if="step === 'success'">
			<div
				class="p-12 flex flex-col items-center justify-center text-center w-full"
				style="min-height: 400px"
			>
				<div
					class="w-20 h-20 rounded-full flex items-center justify-center mb-6 bg-green-100 dark:bg-green-900/30"
				>
					<svg
						class="w-10 h-10 text-green-600 dark:text-green-400"
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
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { createResource, call } from 'frappe-ui'
import { useCartStore } from '@/stores/cart.js'
import { useSessionStore } from '@/stores/session.js'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	mode: {
		type: String,
		default: 'sale',
		validator: (v) => ['sale', 'layaway', 'repair'].includes(v),
	},
	referenceId: { type: String, default: null },
	balanceAmount: { type: Number, default: 0 },
	draftMode: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'success'])

const cart = useCartStore()
const session = useSessionStore()

const processing = ref(false)
const error = ref('')
const step = ref('review')
const selectedPayments = ref([])
const taxExempt = ref(false)
const showSalespersons = ref(false)
const successBreakdown = ref([])
const successInvoiceId = ref(null)

const giftCardNumber = ref('')
const giftCardInfo = ref(null)
const giftCardLoading = ref(false)
const showFinancingWaterfall = ref(false)

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

const successTitle = computed(() => {
	if (props.mode === 'sale') return 'Payment Successful!'
	if (props.mode === 'layaway') return 'Layaway Payment Recorded!'
	return 'Repair Payment Recorded!'
})

const successSubtext = computed(() => {
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
			const result = await cart.submitOrder(selectedPayments.value, {
				taxExempt: taxExempt.value,
				warehouse: session.currentWarehouse,
				giftCardNumber: gcPayment ? giftCardNumber.value : undefined,
			})
			const invoiceName = result?.invoice_name || result?.data?.invoice_name
			successInvoiceId.value = invoiceName || null
			successBreakdown.value = payments
			step.value = 'success'
			emit('success', result)
		} else if (props.mode === 'layaway') {
			const splitPaymentResource = createResource({
				url: 'zevar_core.api.layaway.process_split_layaway_payment',
				auto: false,
			})
			const rawResult = await splitPaymentResource.submit({
				layaway_id: props.referenceId,
				payments: JSON.stringify(payments),
			})
			const result = rawResult?.message ?? rawResult
			if (result?.success) {
				successBreakdown.value = result.payment_breakdown || payments
				successInvoiceId.value = props.referenceId
				step.value = 'success'
				emit('success', result)
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
		let errorMsg = ''
		if (e?.exc_type === 'ValidationError' && e?.message) {
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

function printReceipt() {
	if (successInvoiceId.value) {
		window.open(`/printview?doctype=Sales Invoice&name=${successInvoiceId.value}`, '_blank')
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
		}
	}
)

function close() {
	emit('close')
	if (step.value === 'success' && props.mode === 'sale') {
		cart.clearCart()
	}
	step.value = 'review'
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}
</script>
