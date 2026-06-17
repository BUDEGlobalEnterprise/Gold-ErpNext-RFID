<template>
	<AppLayout>
		<div class="max-w-3xl mx-auto">
			<div class="text-center mb-8">
				<h1 class="premium-title !text-2xl">POS Opening Entry</h1>
				<p class="premium-subtitle mt-2">Start your cash register session</p>
			</div>

			<div
				v-if="posSession.hasActiveSession"
				class="flex items-center gap-4 p-5 bg-amber-500/10 border border-amber-500/30 rounded-xl mb-6"
			>
				<span class="text-3xl shrink-0">&#9888;&#65039;</span>
				<div class="flex-1 min-w-0">
					<h3 class="text-amber-400 font-bold mb-1">Active Session Detected</h3>
					<p class="text-gray-400 text-sm">
						You already have an open session: {{ posSession.status.session?.name }}
					</p>
					<p class="text-gray-500 text-xs mt-1">
						Opened: {{ posSession.status.session?.opening_date }} at
						{{ posSession.status.session?.opening_time }} | Duration:
						{{ posSession.status.session?.duration_hours }}h | Sales:
						{{ posSession.status.session?.today_sales_count || 0 }} today /
						{{ posSession.status.session?.sales_count }} total
					</p>
				</div>
				<router-link
					to="/closing"
					class="px-5 py-2.5 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition text-sm shrink-0"
				>
					Go to Closing
				</router-link>
			</div>

			<div v-else class="premium-card p-6">
				<div
					v-if="profileError"
					class="p-4 mb-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-500 text-sm"
				>
					{{ profileError }}
				</div>
				<div
					v-if="!profileError && profiles.length === 0"
					class="p-4 mb-4 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-500 text-sm"
				>
					No POS profiles found. Please create a POS Profile in ERPNext first.
				</div>
				<form v-if="profiles.length > 0" @submit.prevent="submitOpening" class="space-y-6">
					<div>
						<label
							class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
							>POS Profile</label
						>
						<select
							v-model="form.pos_profile"
							required
							:disabled="loading"
							class="w-full px-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none"
						>
							<option value="">Select a profile...</option>
							<option
								v-for="profile in profiles"
								:key="profile.name"
								:value="profile.name"
							>
								{{ profile.name }} - {{ profile.warehouse }}
							</option>
						</select>
					</div>

					<div>
						<label
							class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
							>Opening Cash Balance</label
						>
						<div
							v-if="enforceFixedFloat"
							class="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg text-sm text-blue-500 mb-2"
						>
							Fixed float policy: opening balance must be ${{
								fixedFloatAmount.toFixed(2)
							}}
						</div>
						<div class="relative">
							<span
								class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-medium"
								>$</span
							>
							<input
								type="number"
								v-model.number="form.opening_balance"
								step="0.01"
								min="0"
								placeholder="0.00"
								required
								:disabled="loading || enforceFixedFloat"
								class="w-full pl-8 pr-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none font-mono disabled:opacity-60 disabled:cursor-not-allowed"
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
								<span class="text-xs font-medium text-gray-500 dark:text-gray-500"
									>${{ denom.value }}</span
								>
								<input
									type="number"
									v-model.number="form.cash_breakdown[denom.value]"
									min="0"
									placeholder="0"
									@change="calculateTotal"
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
							<strong class="font-mono">${{ calculatedTotal.toFixed(2) }}</strong>
						</div>
						<div
							v-if="breakdownMismatch"
							class="p-3 mt-2 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-500"
						>
							Breakdown total (${{ calculatedTotal.toFixed(2) }}) does not match
							required float (${{ fixedFloatAmount.toFixed(2) }}). Please adjust.
						</div>
						<div
							v-if="!breakdownMismatch && calculatedTotal > 0 && enforceFixedFloat"
							class="p-3 mt-2 bg-green-500/10 border border-green-500/30 rounded-lg text-sm text-green-500"
						>
							Breakdown matches required float.
						</div>
					</div>

					<div>
						<label
							class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
							>Opening Notes (Optional)</label
						>
						<textarea
							v-model="form.notes"
							placeholder="Any notes for this session..."
							rows="3"
							:disabled="loading"
							class="w-full px-4 py-3 bg-white dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] outline-none resize-none"
						></textarea>
					</div>

					<div class="text-center pt-2">
						<button
							type="submit"
							:disabled="loading || !form.pos_profile || breakdownMismatch"
							class="px-12 py-4 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition text-base disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
						>
							<span v-if="loading">Opening Session...</span>
							<span v-else>Open Cash Register</span>
						</button>
					</div>
				</form>
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
						v-if="successMessage"
						class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[1000]"
					>
						<div
							class="bg-white dark:bg-warm-card p-12 rounded-2xl text-center max-w-md mx-4"
						>
							<div class="text-6xl mb-4">&#9989;</div>
							<h2 class="premium-title !text-xl mb-2">Session Opened!</h2>
							<p class="text-gray-500 dark:text-gray-400 mb-8">
								{{ successMessage }}
							</p>
							<div class="flex gap-3 justify-center">
								<router-link
									to="/terminal"
									class="px-8 py-3 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition text-sm flex-1 text-center"
								>
									Start Selling
								</router-link>
							</div>

							<!-- Dual Count Verification Form -->
							<div
								v-if="!verificationData"
								class="mt-6 border-t border-gray-100 dark:border-warm-border/50 pt-6 text-left"
							>
								<h3
									class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2"
								>
									Dual Count Verification
								</h3>
								<p class="text-xs text-gray-400 mb-4 leading-relaxed">
									An authorized manager can verify and log the initial cash
									register float count now.
								</p>
								<div class="space-y-3">
									<div>
										<label
											class="block text-[10px] font-bold uppercase text-gray-500 mb-1"
											>Verifier User/Email</label
										>
										<input
											type="text"
											v-model="verifyForm.verified_by"
											placeholder="manager@example.com"
											class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-xs"
										/>
									</div>
									<div>
										<label
											class="block text-[10px] font-bold uppercase text-gray-500 mb-1"
											>Counted Amount ($)</label
										>
										<input
											type="number"
											v-model.number="verifyForm.counted_amount"
											step="0.01"
											placeholder="0.00"
											class="w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-xs font-mono"
										/>
									</div>
									<button
										@click="submitVerification"
										:disabled="verifying"
										type="button"
										class="w-full py-2 bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 border border-[#D4AF37]/30 text-[#D4AF37] font-bold rounded-lg text-xs transition"
									>
										<span v-if="verifying">Verifying...</span>
										<span v-else>Log Verification Count</span>
									</button>
								</div>
							</div>
							<div
								v-else
								class="mt-6 border-t border-gray-100 dark:border-warm-border/50 pt-6 text-center text-xs"
							>
								<div
									class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 font-bold mb-2"
								>
									✓ Count Verified
								</div>
								<p class="text-gray-400">
									Verified by <strong>{{ verificationData.verified_by }}</strong>
									<span
										v-if="verificationData.match"
										class="text-emerald-500 font-bold"
									>
										(Exact Match)</span
									>
									<span v-else class="text-red-500 font-bold">
										(Mismatch: expected ${{
											Number(verificationData.recorded_amount || 0).toFixed(
												2
											)
										}})</span
									>
								</p>
							</div>
						</div>
					</div>
				</Transition>
			</Teleport>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { usePosSessionStore } from '@/stores/posSession.js'
import AppLayout from '@/components/AppLayout.vue'

const posSession = usePosSessionStore()
posSession.fetchStatus()

const loading = ref(false)
const profiles = ref([])
const profileError = ref('')
const successMessage = ref('')
const calculatedTotal = ref(0)
const fixedFloatAmount = ref(0)
const enforceFixedFloat = ref(false)
const breakdownMismatch = ref(false)

const posOpeningName = ref('')
const verifying = ref(false)
const verificationData = ref(null)
const verifyForm = ref({
	verified_by: '',
	counted_amount: 0,
})

const form = ref({
	pos_profile: '',
	opening_balance: 0,
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

const openSessionResource = createResource({
	url: 'zevar_core.api.pos_session.open_pos_session',
	auto: false,
})

async function loadProfiles() {
	try {
		const res = await fetch('/api/method/zevar_core.api.pos_profile.get_pos_profiles', {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		const json = await res.json()
		if (!res.ok) {
			throw new Error(json.message || 'Not authorized to access POS profiles.')
		}
		const data = json.message || json
		profiles.value = data.profiles || []
		if (profiles.value.length === 1) {
			form.value.pos_profile = profiles.value[0].name
			applyProfileSettings(profiles.value[0])
		}
	} catch (err) {
		console.error('Failed to load profiles:', err)
		profileError.value = err.message || 'Failed to load POS profiles. Check permissions.'
	}
}

function applyProfileSettings(profile) {
	if (!profile) return
	enforceFixedFloat.value = !!profile.custom_enforce_fixed_float
	fixedFloatAmount.value = parseFloat(profile.custom_fixed_opening_float || 0)
	if (enforceFixedFloat.value && fixedFloatAmount.value > 0) {
		form.value.opening_balance = fixedFloatAmount.value
		calculatedTotal.value = 0
		breakdownMismatch.value = false
	}
}

watch(
	() => form.value.pos_profile,
	(name) => {
		const profile = profiles.value.find((p) => p.name === name)
		if (profile) applyProfileSettings(profile)
	}
)

function getSubtotal(denom) {
	const count = form.value.cash_breakdown[denom] || 0
	return (count * denom).toFixed(2)
}

function calculateTotal() {
	let total = 0
	for (const denom of denominations) {
		const count = form.value.cash_breakdown[denom.value] || 0
		total += count * denom.value
	}
	calculatedTotal.value = total
	if (enforceFixedFloat.value && total > 0) {
		form.value.opening_balance = fixedFloatAmount.value
		breakdownMismatch.value = Math.abs(total - fixedFloatAmount.value) > 0.01
	} else {
		form.value.opening_balance = total
		breakdownMismatch.value = false
	}
}

async function submitOpening() {
	loading.value = true
	try {
		const result = await openSessionResource.submit({
			pos_profile: form.value.pos_profile,
			opening_balance: form.value.opening_balance,
			cash_breakdown: Object.entries(form.value.cash_breakdown)
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
			successMessage.value = result.message
			posOpeningName.value = result.name || result.session || ''
			posSession.fetchStatus()
		}
	} catch (error) {
		console.error('Failed to open session:', error)
	} finally {
		loading.value = false
	}
}

async function submitVerification() {
	if (!verifyForm.value.verified_by) {
		alert('Verifier email/user is required.')
		return
	}
	verifying.value = true
	try {
		const targetSession = posOpeningName.value || posSession.sessionName
		const res = await fetch('/api/method/zevar_core.api.pos_session.verify_opening_count', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({
				session_name: targetSession,
				counted_amount: verifyForm.value.counted_amount,
				verified_by: verifyForm.value.verified_by,
			}),
		})
		if (!res.ok) {
			const err = await res.json()
			throw new Error(err.message || 'Verification failed')
		}
		const data = await res.json()
		if (data.message?.success) {
			verificationData.value = data.message
		} else {
			throw new Error('Failed to verify count')
		}
	} catch (e) {
		alert(e.message || 'Failed to verify count')
	} finally {
		verifying.value = false
	}
}

onMounted(() => {
	loadProfiles()
	denominations.forEach((d) => {
		if (form.value.cash_breakdown[d.value] === undefined) {
			form.value.cash_breakdown[d.value] = 0
		}
	})
})
</script>
