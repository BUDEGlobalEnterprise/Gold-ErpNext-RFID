<template>
	<AppLayout>
		<div class="max-w-3xl mx-auto">
			<div class="text-center mb-8">
				<h1 class="premium-title !text-2xl">POS Closing Entry</h1>
				<p class="premium-subtitle mt-2">Close your cash register and reconcile</p>
			</div>

			<div
				v-if="!posSession.hasActiveSession && !loading"
				class="flex items-center gap-4 p-5 bg-blue-500/10 border border-blue-500/30 rounded-xl"
			>
				<span class="text-3xl shrink-0">&#8505;&#65039;</span>
				<div class="flex-1 min-w-0">
					<h3 class="text-blue-400 font-bold mb-1">No Active Session</h3>
					<p class="text-gray-400 text-sm">
						You don't have an open POS session. Please open one first.
					</p>
				</div>
				<router-link
					to="/opening"
					class="px-5 py-2.5 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition text-sm shrink-0"
				>
					Open Cash Register
				</router-link>
			</div>

			<div
				v-else-if="posSession.activeSession?.status === 'Suspended'"
				class="flex flex-col items-center justify-center text-center p-12 bg-amber-500/10 border border-amber-500/20 rounded-2xl"
			>
				<div
					class="w-16 h-16 bg-amber-500/10 border border-amber-500/30 rounded-full flex items-center justify-center mb-4 text-amber-500 text-3xl animate-pulse"
				>
					🔒
				</div>
				<h3 class="premium-title !text-xl mb-2">Register Suspended</h3>
				<p class="premium-subtitle max-w-md mb-6">
					This register session is suspended. To reconcile cash and close the till,
					please resume the session first.
				</p>
				<button
					@click="handleResume"
					:disabled="sessionLoading"
					class="px-8 py-3 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition active:scale-95 disabled:opacity-50"
				>
					<span v-if="sessionLoading">Resuming...</span>
					<span v-else>Resume POS Session</span>
				</button>
			</div>

			<div v-else class="space-y-6">
				<div class="premium-card p-5">
					<h3 class="premium-title !text-base mb-4">Session Summary</h3>
					<div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
						<div class="flex flex-col gap-1">
							<span class="text-xs text-gray-500 dark:text-gray-500"
								>Session ID</span
							>
							<span
								class="text-sm font-bold text-gray-900 dark:text-white font-mono"
							>
								{{ posSession.status.session?.name }}
							</span>
						</div>
						<div class="flex flex-col gap-1">
							<span class="text-xs text-gray-500 dark:text-gray-500"
								>Opening Balance</span
							>
							<span
								class="text-sm font-bold text-gray-900 dark:text-white font-mono"
							>
								${{ formatAmount(posSession.status.session?.opening_balance) }}
							</span>
						</div>
						<div class="flex flex-col gap-1">
							<span class="text-xs text-gray-500 dark:text-gray-500"
								>Today's Sales</span
							>
							<span
								class="text-sm font-bold text-emerald-600 dark:text-emerald-400 font-mono"
							>
								${{ formatAmount(posSession.status.session?.today_sales_total) }}
							</span>
						</div>
						<div class="flex flex-col gap-1">
							<span class="text-xs text-gray-500 dark:text-gray-500"
								>Today's Count</span
							>
							<span class="text-sm font-bold text-emerald-600 dark:text-emerald-400">
								{{ posSession.status.session?.today_sales_count || 0 }}
							</span>
						</div>
						<div class="flex flex-col gap-1">
							<span class="text-xs text-gray-500 dark:text-gray-500"
								>Session Total</span
							>
							<span
								class="text-sm font-bold text-gray-900 dark:text-white font-mono"
							>
								${{ formatAmount(posSession.status.session?.sales_total) }}
							</span>
						</div>
						<div class="flex flex-col gap-1">
							<span class="text-xs text-gray-500 dark:text-gray-500"
								>Session Count</span
							>
							<span class="text-sm font-bold text-gray-900 dark:text-white">
								{{ posSession.status.session?.sales_count }}
							</span>
						</div>
						<div class="flex flex-col gap-1">
							<span class="text-xs text-gray-500 dark:text-gray-500">Duration</span>
							<span class="text-sm font-bold text-gray-900 dark:text-white">
								{{ posSession.status.session?.duration_hours }}h
							</span>
						</div>
						<template v-if="!isBlindClose">
							<div
								class="col-span-2 sm:col-span-1 bg-green-500/10 p-3 rounded-lg flex flex-col gap-1"
							>
								<span class="text-xs text-green-400"
									>Expected Balance (Today)</span
								>
								<span class="text-lg font-bold text-green-500 font-mono">
									${{ formatAmount(todayExpectedBalance) }}
								</span>
							</div>
							<div
								class="col-span-2 sm:col-span-1 bg-blue-500/10 p-3 rounded-lg flex flex-col gap-1"
							>
								<span class="text-xs text-blue-400"
									>Expected Balance (Session)</span
								>
								<span class="text-sm font-bold text-blue-500 font-mono">
									${{ formatAmount(sessionExpectedBalance) }}
								</span>
							</div>
						</template>
					</div>
				</div>

				<!-- Cash Movements -->
				<div v-if="!isBlindClose && cashMovements.length > 0" class="premium-card p-5">
					<div class="flex items-center justify-between mb-4">
						<h3 class="premium-title !text-base">Cash Movements</h3>
						<span class="text-xs text-gray-500">Mid-shift adjustments</span>
					</div>
					<div class="space-y-2 mb-4">
						<div
							v-for="m in cashMovements"
							:key="m.name"
							class="flex items-center justify-between p-3 rounded-lg text-sm"
							:class="{
								'bg-emerald-500/10': m.movement_type === 'Cash In',
								'bg-red-500/10': m.movement_type === 'Cash Out',
							}"
						>
							<div class="flex items-center gap-3">
								<span
									class="font-bold text-xs px-2 py-0.5 rounded-full"
									:class="{
										'bg-emerald-500 text-white': m.movement_type === 'Cash In',
										'bg-red-500 text-white': m.movement_type === 'Cash Out',
									}"
								>
									{{ m.movement_type === 'Cash In' ? '+ IN' : '- OUT' }}
								</span>
								<div>
									<p class="font-medium text-gray-900 dark:text-white">
										{{ m.reason }}
									</p>
									<p class="text-xs text-gray-500">
										{{ formatTime(m.creation) }}
										<span v-if="m.notes"> · {{ m.notes }}</span>
									</p>
								</div>
							</div>
							<span
								class="font-mono font-bold"
								:class="{
									'text-emerald-600': m.movement_type === 'Cash In',
									'text-red-500': m.movement_type === 'Cash Out',
								}"
							>
								{{ m.movement_type === 'Cash In' ? '+' : '-' }}${{
									formatAmount(m.amount)
								}}
							</span>
						</div>
					</div>
					<div
						class="grid grid-cols-3 gap-4 pt-3 border-t border-gray-200 dark:border-warm-border/50"
					>
						<div class="text-center">
							<p class="text-xs text-gray-500">Total In</p>
							<p class="text-sm font-bold text-emerald-600 font-mono">
								+${{ formatAmount(cashMovementsTotal.in) }}
							</p>
						</div>
						<div class="text-center">
							<p class="text-xs text-gray-500">Total Out</p>
							<p class="text-sm font-bold text-red-500 font-mono">
								-${{ formatAmount(cashMovementsTotal.out) }}
							</p>
						</div>
						<div class="text-center">
							<p class="text-xs text-gray-500">Net</p>
							<p
								class="text-sm font-bold font-mono"
								:class="
									cashMovementsTotal.net >= 0
										? 'text-emerald-600'
										: 'text-red-500'
								"
							>
								{{ cashMovementsTotal.net >= 0 ? '+' : '' }}${{
									formatAmount(Math.abs(cashMovementsTotal.net))
								}}
							</p>
						</div>
					</div>
				</div>

				<div class="premium-card p-6">
					<!-- Step Indicator Header -->
					<div
						class="flex items-center justify-between mb-6 pb-6 border-b border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex items-center gap-2">
							<span
								class="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-all duration-300"
								:class="
									currentStep === 1
										? 'bg-[#D4AF37] text-black font-extrabold ring-4 ring-[#D4AF37]/20'
										: 'bg-green-500 text-white'
								"
							>
								<span v-if="currentStep === 1">1</span>
								<span v-else>✓</span>
							</span>
							<span
								class="text-xs font-bold uppercase tracking-wider text-gray-900 dark:text-white"
								>Count Entry</span
							>
						</div>
						<div
							class="h-0.5 flex-1 bg-gray-200 dark:bg-warm-border mx-4 max-w-[80px]"
						></div>
						<div class="flex items-center gap-2">
							<span
								class="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-all duration-300"
								:class="
									currentStep === 2
										? 'bg-[#D4AF37] text-black font-extrabold ring-4 ring-[#D4AF37]/20'
										: 'bg-gray-200 dark:bg-warm-dark-700 text-gray-500'
								"
							>
								2
							</span>
							<span
								class="text-xs font-bold uppercase tracking-wider"
								:class="
									currentStep === 2
										? 'text-gray-900 dark:text-white'
										: 'text-gray-400'
								"
								>Reconcile & Close</span
							>
						</div>
					</div>

					<form @submit.prevent="submitClosing" class="space-y-6">
						<!-- STEP 1: COUNT ENTRY -->
						<div v-if="currentStep === 1" class="space-y-6">
							<div>
								<label
									class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
									>Actual Closing Balance</label
								>
								<div class="relative">
									<span
										class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-medium"
										>$</span
									>
									<input
										type="number"
										v-model.number="form.closing_balance"
										step="0.01"
										min="0"
										placeholder="0.00"
										required
										:disabled="loading"
										@input="calculateVariance"
										class="w-full pl-8 pr-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none font-mono"
									/>
								</div>
							</div>

							<div>
								<label
									class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
									>Cash Breakdown (Optional)</label
								>
								<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
									<div
										v-for="denom in denominations"
										:key="denom.value"
										class="flex flex-col gap-1"
									>
										<span
											class="text-xs font-medium text-gray-500 dark:text-gray-500"
											>${{ denom.value }}</span
										>
										<input
											type="number"
											v-model.number="form.cash_breakdown[denom.value]"
											min="0"
											placeholder="0"
											@change="calculateFromBreakdown"
											:disabled="loading"
											class="w-full px-3 py-2 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none font-mono"
										/>
										<span class="text-xs text-gray-500"
											>${{ getSubtotal(denom.value) }}</span
										>
									</div>
								</div>
								<div
									class="flex justify-between items-center p-3 bg-gray-50 dark:bg-warm-dark-700/50 rounded-lg mt-3 text-sm text-gray-700 dark:text-gray-300"
								>
									<span>Calculated Total:</span>
									<strong class="font-mono"
										>${{ calculatedTotal.toFixed(2) }}</strong
									>
								</div>
							</div>

							<!-- Live Variance Preview (Only shown if NOT in blind close mode) -->
							<div
								v-if="!isBlindClose"
								class="text-center p-5 rounded-xl"
								:class="{
									'bg-green-500/10 border border-green-500/30':
										varianceClass === 'balanced',
									'bg-blue-500/10 border border-blue-500/30':
										varianceClass === 'excess',
									'bg-red-500/10 border border-red-500/30':
										varianceClass === 'shortage',
								}"
							>
								<div class="text-xs text-gray-500 dark:text-gray-500 mb-1">
									Variance (Today)
								</div>
								<div
									class="text-3xl font-bold font-mono"
									:class="{
										'text-green-500': varianceClass === 'balanced',
										'text-blue-500': varianceClass === 'excess',
										'text-red-500': varianceClass === 'shortage',
									}"
								>
									<span v-if="variance > 0">+</span>${{
										formatAmount(Math.abs(variance))
									}}
								</div>
								<div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
									{{ varianceStatus }}
								</div>
							</div>
							<div
								v-else
								class="text-center p-5 rounded-xl bg-amber-500/5 border border-amber-500/20"
							>
								<div
									class="text-xs text-amber-500 font-bold uppercase tracking-wider mb-1"
								>
									🔒 Blind Reconcile Mode
								</div>
								<p class="text-xs text-gray-400 max-w-xs mx-auto leading-relaxed">
									Cashier variance and expectations are hidden. The server will
									calculate and record discrepancies securely upon closing.
								</p>
							</div>

							<div>
								<label
									class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
									>Closing Notes</label
								>
								<textarea
									v-model="form.notes"
									placeholder="Any notes about discrepancies or issues..."
									rows="3"
									:disabled="loading"
									class="w-full px-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none resize-none"
								></textarea>
							</div>

							<div class="text-center pt-2">
								<button
									type="submit"
									:disabled="loading"
									class="px-12 py-4 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition text-base disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
								>
									<span v-if="loading">Sealing Count...</span>
									<span v-else>Submit & Seal Count (Step 1)</span>
								</button>
							</div>
						</div>

						<!-- STEP 2: RECONCILE & CLOSE -->
						<div v-else class="space-y-6">
							<div
								class="bg-gray-50 dark:bg-warm-dark-700/30 border border-gray-100 dark:border-warm-border rounded-xl p-5 space-y-4"
							>
								<h4
									class="text-xs font-bold text-gray-900 dark:text-white uppercase tracking-wider"
								>
									🔒 Count Sealed Successfully
								</h4>
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div class="flex flex-col">
										<span class="text-xs text-gray-500"
											>Your Counted Cash</span
										>
										<span
											class="text-lg font-bold text-gray-900 dark:text-white font-mono"
											>${{ formatAmount(form.closing_balance) }}</span
										>
									</div>
									<div class="flex flex-col">
										<span class="text-xs text-gray-500"
											>Expected Cash Balance</span
										>
										<span
											class="text-lg font-bold text-gray-900 dark:text-white font-mono"
											>${{ formatAmount(sessionExpectedBalance) }}</span
										>
									</div>
								</div>

								<div
									class="text-center p-4 rounded-lg mt-2"
									:class="{
										'bg-green-500/10 border border-green-500/20':
											varianceClass === 'balanced',
										'bg-blue-500/10 border border-blue-500/20':
											varianceClass === 'excess',
										'bg-red-500/10 border border-red-500/20':
											varianceClass === 'shortage',
									}"
								>
									<div class="text-xs text-gray-500 mb-1">
										Variance (Difference)
									</div>
									<div
										class="text-2xl font-bold font-mono"
										:class="{
											'text-green-500': varianceClass === 'balanced',
											'text-blue-500': varianceClass === 'excess',
											'text-red-500': varianceClass === 'shortage',
										}"
									>
										<span v-if="variance > 0">+</span>${{
											formatAmount(variance)
										}}
									</div>
									<div class="text-xs text-gray-500 mt-1">
										{{ varianceStatus }}
									</div>
								</div>
							</div>

							<!-- Variance Reason Code Dropdown (Required if variance exists) -->
							<div v-if="Math.abs(variance) > 0.01">
								<label
									class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2"
								>
									Variance Reason Code <span class="text-red-500">*</span>
								</label>
								<select
									v-model="varianceReasonCode"
									required
									:disabled="loading"
									class="w-full px-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none"
								>
									<option value="" disabled>-- Select a Reason Code --</option>
									<option value="Counting Error">
										Counting Error (Cashier mistake)
									</option>
									<option value="System Error">
										System Error (POS reconciliation mismatch)
									</option>
									<option value="Suspected Theft">Suspected Theft</option>
								</select>
								<p class="text-[11px] text-gray-400 mt-1">
									Structured reason code is mandatory for all overages/shortages.
								</p>
							</div>

							<!-- Manager Override Banner if variance exceeds threshold -->
							<div
								v-if="overrideRequired"
								class="p-4 bg-red-500/10 border border-red-500/20 rounded-xl space-y-2"
							>
								<div class="flex items-start gap-2.5">
									<span class="text-lg leading-none">⚠️</span>
									<div>
										<h5
											class="text-xs font-bold text-red-500 uppercase tracking-wider"
										>
											Manager Authorization Required
										</h5>
										<p class="text-xs text-gray-400 mt-0.5">
											The variance of ${{
												formatAmount(Math.abs(variance))
											}}
											exceeds your profile's alert threshold of ${{
												formatAmount(alertThreshold)
											}}.
										</p>
									</div>
								</div>
								<div
									v-if="managerOverride"
									class="text-xs text-green-500 font-bold flex items-center gap-1.5 pt-1"
								>
									<span
										>✓ Approved by:
										{{
											managerOverride.manager_email ||
											managerOverride.approved_by
										}}</span
									>
								</div>
							</div>

							<div>
								<label
									class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
									>Closing Notes</label
								>
								<textarea
									v-model="form.notes"
									placeholder="Any additional closing notes or comments..."
									rows="3"
									:disabled="loading"
									class="w-full px-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none resize-none"
								></textarea>
							</div>

							<div class="text-center pt-2">
								<button
									type="submit"
									:disabled="loading"
									class="px-12 py-4 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition text-base disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
								>
									<span v-if="loading">Finalizing Closing...</span>
									<span v-else-if="overrideRequired && !managerOverride"
										>Request Manager Approval</span
									>
									<span v-else>Confirm & Finalize Closing (Step 2)</span>
								</button>
							</div>
						</div>
					</form>
				</div>
			</div>

			<Teleport to="body">
				<Transition
					enter-active-class="transition-opacity duration-300"
					enter-from-class="opacity-0"
					enter-to-class="opacity-100"
					leave-active-class="transition-opacity duration-200"
					leave-from-class="opacity-100"
					leave-to-class="opacity-0"
				>
					<div
						v-if="closingResult"
						class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[1000] p-4"
					>
						<div
							class="bg-white dark:bg-warm-card p-10 rounded-2xl text-center max-w-md w-full"
						>
							<div class="text-6xl mb-4">&#9989;</div>
							<h2 class="premium-title !text-xl mb-6">Session Closed!</h2>
							<div class="text-left space-y-3 mb-8">
								<div
									class="flex justify-between text-sm text-gray-600 dark:text-gray-400 pb-3 border-b border-gray-100 dark:border-warm-border/50"
								>
									<span>Opening Balance:</span>
									<strong class="font-mono text-gray-900 dark:text-white">
										${{ formatAmount(closingResult.opening_balance) }}
									</strong>
								</div>
								<div
									class="flex justify-between text-sm text-gray-600 dark:text-gray-400 pb-3 border-b border-gray-100 dark:border-warm-border/50"
								>
									<span>Total Sales:</span>
									<strong class="font-mono text-gray-900 dark:text-white">
										${{ formatAmount(closingResult.total_sales) }}
									</strong>
								</div>
								<div
									class="flex justify-between text-sm text-gray-600 dark:text-gray-400 pb-3 border-b border-gray-100 dark:border-warm-border/50"
								>
									<span>Closing Balance:</span>
									<strong class="font-mono text-gray-900 dark:text-white">
										${{ formatAmount(closingResult.closing_balance) }}
									</strong>
								</div>
								<div
									class="flex justify-between text-sm pb-3"
									:class="{
										'text-red-500':
											closingResult.variance_status === 'shortage',
										'text-blue-500':
											closingResult.variance_status === 'excess',
										'text-green-500':
											closingResult.variance_status === 'balanced',
									}"
								>
									<span>Variance:</span>
									<strong class="font-mono">
										${{ formatAmount(Math.abs(closingResult.variance)) }}
									</strong>
								</div>
							</div>
							<div class="flex gap-3 justify-center">
								<button
									@click="printReceipt"
									class="px-6 py-3 border border-gray-200 dark:border-warm-border rounded-lg font-medium text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition"
								>
									Print Receipt
								</button>
								<router-link
									:to="{ path: '/reports/eod', query: { date: 'today' } }"
									class="px-6 py-3 border border-[#D4AF37] text-[#D4AF37] rounded-lg font-bold text-sm hover:bg-[#D4AF37] hover:text-black transition"
								>
									View EOD Report
								</router-link>
								<router-link
									to="/terminal"
									class="px-8 py-3 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition"
								>
									Done
								</router-link>
							</div>
						</div>
					</div>
				</Transition>
			</Teleport>

			<ManagerOverrideModal
				:show="showOverrideModal"
				:variance="previewData?.variance ?? todayVariance"
				:threshold="alertThreshold"
				@approved="handleOverrideApproved"
				@cancel="showOverrideModal = false"
			/>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { usePosSessionStore } from '@/stores/posSession.js'
import AppLayout from '@/components/AppLayout.vue'
import ManagerOverrideModal from '@/components/ManagerOverrideModal.vue'

const posSession = usePosSessionStore()
posSession.fetchStatus()

const loading = ref(false)
const sessionLoading = ref(false)
const closingResult = ref(null)
const calculatedTotal = ref(0)
const previewData = ref(null)
const overrideRequired = ref(false)
const showOverrideModal = ref(false)
const alertThreshold = ref(5)
const managerOverride = ref(null)
const cashMovements = ref([])
const cashMovementsTotal = ref({ in: 0, out: 0, net: 0 })
const isBlindClose = ref(true)

const currentStep = ref(1)
const varianceReasonCode = ref('')

const step1Resource = createResource({
	url: 'zevar_core.api.pos_session.submit_blind_close_step1',
	auto: false,
})

const step2Resource = createResource({
	url: 'zevar_core.api.pos_session.submit_blind_close_step2',
	auto: false,
})

const form = ref({
	closing_balance: 0,
	cash_breakdown: {},
	notes: '',
})

const denominations = [
	{ value: 100 },
	{ value: 50 },
	{ value: 20 },
	{ value: 10 },
	{ value: 5 },
	{ value: 1 },
	{ value: 0.25 },
	{ value: 0.1 },
	{ value: 0.05 },
	{ value: 0.01 },
]

const todayOpening = computed(() => {
	const sessionDate = posSession.status.session?.opening_date
	const today = new Date().toISOString().split('T')[0]
	if (sessionDate === today) {
		return posSession.status.session?.opening_balance || 0
	}
	return 0
})
const todaySalesTotal = computed(() => posSession.status.session?.today_sales_total || 0)
const sessionSalesTotal = computed(() => posSession.status.session?.sales_total || 0)

const todayExpectedBalance = computed(() => {
	return todayOpening.value + todaySalesTotal.value
})

const sessionExpectedBalance = computed(() => {
	if (previewData.value) {
		return previewData.value.expected_balance || previewData.value.total_expected || 0
	}
	return (posSession.status.session?.opening_balance || 0) + sessionSalesTotal.value
})

const todayVariance = computed(() => {
	return form.value.closing_balance - todayExpectedBalance.value
})

const sessionVariance = computed(() => {
	if (previewData.value) {
		return previewData.value.variance
	}
	return form.value.closing_balance - sessionExpectedBalance.value
})

const varianceClass = computed(() => {
	const v = previewData.value ? previewData.value.variance : todayVariance.value
	if (v === 0) return 'balanced'
	if (v > 0) return 'excess'
	return 'shortage'
})

const varianceStatus = computed(() => {
	const v = previewData.value ? previewData.value.variance : todayVariance.value
	if (v === 0) return 'Balanced'
	if (v > 0) return 'Excess (Over)'
	return 'Shortage (Under)'
})

const variance = computed(() => {
	return previewData.value ? previewData.value.variance : todayVariance.value
})

const openingDate = computed(() => {
	return posSession.status.session?.opening_date || ''
})

const previewCloseResource = createResource({
	url: 'zevar_core.api.pos_session.preview_close',
	auto: false,
})

const cashMovementsResource = createResource({
	url: 'zevar_core.api.pos_session.get_cash_movements',
	auto: false,
})

const closeSessionResource = createResource({
	url: 'zevar_core.api.pos_session.close_pos_session_v2',
	auto: false,
})

function formatAmount(amount) {
	if (amount === null || amount === undefined) return '0.00'
	return Number(amount).toFixed(2)
}

function formatTime(timestamp) {
	if (!timestamp) return ''
	const d = new Date(timestamp)
	return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

async function fetchCashMovements() {
	if (!posSession.status.session?.name) return
	try {
		const res = await cashMovementsResource.submit({
			session_name: posSession.status.session.name,
		})
		cashMovements.value = res.movements || []
		cashMovementsTotal.value = {
			in: res.total_in || 0,
			out: res.total_out || 0,
			net: res.net || 0,
		}
	} catch (err) {
		console.error('Failed to fetch cash movements:', err)
	}
}

function getSubtotal(denom) {
	const count = form.value.cash_breakdown[denom] || 0
	return (count * denom).toFixed(2)
}

function calculateFromBreakdown() {
	let total = 0
	for (const denom of denominations) {
		const count = form.value.cash_breakdown[denom.value] || 0
		total += count * denom.value
	}
	calculatedTotal.value = total
	form.value.closing_balance = total
	calculateVariance()
}

let timeoutId = null
function calculateVariance() {
	if (!posSession.status.session?.name) return
	if (isBlindClose.value) return // NETWORK LOCKDOWN: Hides requests/payloads from network tab!

	clearTimeout(timeoutId)
	timeoutId = setTimeout(async () => {
		try {
			const res = await previewCloseResource.submit({
				session_name: posSession.status.session?.name,
				total_cash_counted: form.value.closing_balance,
			})
			previewData.value = res
			alertThreshold.value = res.alert_threshold || 5

			if (Math.abs(res.variance) > res.alert_threshold) {
				overrideRequired.value = true
			} else {
				overrideRequired.value = false
				managerOverride.value = null
			}
		} catch (err) {
			console.error(err)
		}
	}, 500)
}

function handleOverrideApproved(data) {
	managerOverride.value = data
	showOverrideModal.value = false
	overrideRequired.value = false
	doClose()
}

async function handleResume() {
	sessionLoading.value = true
	try {
		const success = await posSession.resumeSession()
		if (success) {
			console.log('Session resumed')
		} else {
			alert(posSession.error || 'Failed to resume session')
		}
	} catch (e) {
		console.error(e)
	} finally {
		sessionLoading.value = false
	}
}

async function submitStep1() {
	loading.value = true
	try {
		const payload = {
			session_name: posSession.status.session?.name,
			total_cash_counted: form.value.closing_balance,
			breakdown: Object.entries(form.value.cash_breakdown)
				.filter(([_, count]) => count > 0)
				.map(([denom, count]) => ({
					mode_of_payment: 'Cash',
					denomination: parseFloat(denom),
					count: count,
					amount: count * parseFloat(denom),
				})),
			notes: form.value.notes,
		}

		const res = await step1Resource.submit(payload)
		if (res.success) {
			previewData.value = res
			alertThreshold.value = res.alert_threshold || 5

			if (Math.abs(res.variance) > alertThreshold.value) {
				overrideRequired.value = true
			} else {
				overrideRequired.value = false
				managerOverride.value = null
			}
			currentStep.value = 2
		}
	} catch (error) {
		console.error('Failed to submit physical count:', error)
		alert(error.message || 'Failed to submit physical count')
	} finally {
		loading.value = false
	}
}

async function submitStep2() {
	if (Math.abs(previewData.value?.variance || 0) > 0.01 && !varianceReasonCode.value) {
		alert('Please select a Variance Reason Code.')
		return
	}
	if (overrideRequired.value && !managerOverride.value) {
		showOverrideModal.value = true
		return
	}
	await doClose()
}

async function doClose() {
	loading.value = true
	try {
		const res = await step2Resource.submit({
			session_name: posSession.status.session?.name,
			variance_reason_code: varianceReasonCode.value,
			notes: form.value.notes,
		})

		if (res.success) {
			closingResult.value = res
			posSession.fetchStatus()
		}
	} catch (error) {
		console.error('Failed to close session:', error)
		alert(error.message || 'Failed to close session')
	} finally {
		loading.value = false
	}
}

async function submitClosing() {
	if (currentStep.value === 1) {
		await submitStep1()
	} else {
		await submitStep2()
	}
}

function printReceipt() {
	if (closingResult.value?.closing_entry) {
		window.open(
			`/api/method/frappe.utils.print_format.download_pdf?doctype=POS+Closing+Entry&name=${closingResult.value.closing_entry}&format=Standard`,
			'_blank'
		)
	}
}

onMounted(() => {
	denominations.forEach((d) => {
		if (form.value.cash_breakdown[d.value] === undefined) {
			form.value.cash_breakdown[d.value] = 0
		}
	})
	fetchCashMovements()
})
</script>
