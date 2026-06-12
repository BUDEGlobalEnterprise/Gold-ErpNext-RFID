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
						<div
							class="col-span-2 sm:col-span-1 bg-green-500/10 p-3 rounded-lg flex flex-col gap-1"
						>
							<span class="text-xs text-green-400">Expected Balance (Today)</span>
							<span class="text-lg font-bold text-green-500 font-mono">
								${{ formatAmount(todayExpectedBalance) }}
							</span>
						</div>
						<div
							class="col-span-2 sm:col-span-1 bg-blue-500/10 p-3 rounded-lg flex flex-col gap-1"
						>
							<span class="text-xs text-blue-400">Expected Balance (Session)</span>
							<span class="text-sm font-bold text-blue-500 font-mono">
								${{ formatAmount(sessionExpectedBalance) }}
							</span>
						</div>
					</div>
				</div>

				<div class="premium-card p-6">
					<form @submit.prevent="submitClosing" class="space-y-6">
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

						<div
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
							<div class="text-sm text-gray-500 dark:text-gray-400 mt-1">
								{{ varianceStatus }}
							</div>
							<div
								v-if="sessionVariance !== 0"
								class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700"
							>
								<div class="text-xs text-gray-400 mb-1">
									Variance (Session Since {{ openingDate }})
								</div>
								<div
									class="text-lg font-bold font-mono"
									:class="{
										'text-green-500': sessionVariance === 0,
										'text-blue-500': sessionVariance > 0,
										'text-red-500': sessionVariance < 0,
									}"
								>
									<span v-if="sessionVariance > 0">+</span>${{
										formatAmount(Math.abs(sessionVariance))
									}}
								</div>
							</div>
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
								<span v-if="loading">Closing Session...</span>
								<span v-else>Close Cash Register</span>
							</button>
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
const closingResult = ref(null)
const calculatedTotal = ref(0)
const previewData = ref(null)
const overrideRequired = ref(false)
const showOverrideModal = ref(false)
const alertThreshold = ref(5)
const managerOverride = ref(null)

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
		return previewData.value.total_expected
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
	if (todayVariance.value === 0) return 'balanced'
	if (todayVariance.value > 0) return 'excess'
	return 'shortage'
})

const varianceStatus = computed(() => {
	if (todayVariance.value === 0) return 'Balanced (Today)'
	if (todayVariance.value > 0) return 'Excess (Over) Today'
	return 'Shortage (Under) Today'
})

const variance = todayVariance

const openingDate = computed(() => {
	return posSession.status.session?.opening_date || ''
})

const previewCloseResource = createResource({
	url: 'zevar_core.api.pos_session.preview_close',
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

async function submitClosing() {
	if (overrideRequired.value && !managerOverride.value) {
		showOverrideModal.value = true
		return
	}
	await doClose()
}

async function doClose() {
	loading.value = true
	try {
		const result = await closeSessionResource.submit({
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
		})

		if (result.success) {
			closingResult.value = result
			posSession.fetchStatus()
		}
	} catch (error) {
		console.error('Failed to close session:', error)
	} finally {
		loading.value = false
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
})
</script>
