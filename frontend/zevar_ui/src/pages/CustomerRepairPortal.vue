<template>
	<div
		class="min-h-[100dvh] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800"
	>
		<!-- Header -->
		<header class="bg-white dark:bg-warm-dark-900 shadow-sm sticky top-0 z-50">
			<div class="max-w-6xl mx-auto px-4 py-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<h1 class="text-xl font-bold text-[#D4AF37]">ZEVAR JEWELERS</h1>
						<span class="text-gray-400">|</span>
						<span class="text-gray-600 dark:text-gray-400 hidden sm:inline"
							>Customer Portal</span
						>
					</div>
					<div v-if="authenticated" class="flex items-center gap-3">
						<span class="text-sm text-gray-600 dark:text-gray-400">{{
							customer?.customer_name
						}}</span>
						<button
							@click="logout"
							class="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400"
						>
							Sign Out
						</button>
					</div>
				</div>
			</div>
		</header>

		<!-- Main Content -->
		<main class="max-w-6xl mx-auto px-4 py-8">
			<!-- Authentication View -->
			<div v-if="!authenticated" class="max-w-md mx-auto">
				<div class="bg-white dark:bg-warm-dark-900 rounded-2xl shadow-xl p-8">
					<div class="text-center mb-8">
						<div
							class="w-16 h-16 bg-[#D4AF37]/10 rounded-full flex items-center justify-center mx-auto mb-4"
						>
							<svg
								class="w-8 h-8 text-[#D4AF37]"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
								/>
							</svg>
						</div>
						<h2 class="text-2xl font-bold text-gray-900 dark:text-white">
							Welcome to the Customer Portal
						</h2>
						<p class="text-gray-600 dark:text-gray-400 mt-2">
							Enter your phone number or email to access your repairs
						</p>
					</div>

					<!-- Step 1: Lookup -->
					<div v-if="authStep === 'lookup'">
						<form @submit.prevent="lookupCustomer">
							<div class="space-y-4">
								<div>
									<label
										class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
										>Phone Number or Email</label
									>
									<input
										v-model="lookupIdentifier"
										type="text"
										placeholder="(555) 123-4567 or email@example.com"
										class="w-full px-4 py-3 border border-gray-200 dark:border-warm-border rounded-lg bg-gray-50 dark:bg-warm-dark-900 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
									/>
								</div>
								<button
									type="submit"
									:disabled="lookingUp || !lookupIdentifier"
									class="w-full py-3 bg-[#D4AF37] text-black rounded-lg font-bold hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed"
								>
									{{ lookingUp ? 'Looking up...' : 'Continue' }}
								</button>
							</div>
						</form>
					</div>

					<!-- Step 2: Verification -->
					<div v-if="authStep === 'verify'">
						<form @submit.prevent="verifyCode">
							<div class="space-y-4">
								<div
									class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-100 dark:border-blue-800"
								>
									<p
										class="text-sm text-blue-800 dark:text-blue-300 text-center"
									>
										We've sent a verification code to your phone/email. Enter
										it below to continue.
									</p>
								</div>
								<div>
									<label
										class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
										>Verification Code</label
									>
									<input
										v-model="verificationCode"
										type="text"
										maxlength="6"
										placeholder="123456"
										class="w-full px-4 py-3 text-center text-2xl tracking-widest border border-gray-200 dark:border-warm-border rounded-lg bg-gray-50 dark:bg-warm-dark-900 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent uppercase"
									/>
								</div>
								<button
									type="submit"
									:disabled="verifying || !verificationCode"
									class="w-full py-3 bg-[#D4AF37] text-black rounded-lg font-bold hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed"
								>
									{{ verifying ? 'Verifying...' : 'Verify & Continue' }}
								</button>
								<button
									type="button"
									@click="returnToLookup"
									class="w-full py-2 text-gray-500 hover:text-gray-700 text-sm"
								>
									Back
								</button>
							</div>
						</form>
					</div>

					<!-- Error -->
					<div
						v-if="authError"
						class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-100 dark:border-red-800"
					>
						<p class="text-sm text-red-800 dark:text-red-300 text-center">
							{{ authError }}
						</p>
					</div>
				</div>
			</div>

			<!-- Authenticated View -->
			<div v-else>
				<!-- Tabs -->
				<div class="bg-white dark:bg-warm-dark-900 rounded-t-2xl shadow-lg px-4 pt-4">
					<div class="flex gap-2">
						<button
							v-for="tab in tabs"
							:key="tab.key"
							@click="activeTab = tab.key"
							:class="[
								'px-4 py-2 rounded-lg font-medium transition-colors',
								activeTab === tab.key
									? 'bg-[#D4AF37] text-black'
									: 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800',
							]"
						>
							{{ tab.label }}
							<span
								v-if="tab.badge"
								class="ml-1 px-2 py-0.5 text-xs rounded-full"
								:class="tab.badgeClass"
								>{{ tab.badge }}</span
							>
						</button>
					</div>
				</div>

				<!-- Tab Content -->
				<div class="bg-white dark:bg-warm-dark-900 rounded-b-2xl shadow-lg p-6">
					<!-- Active Repairs Tab -->
					<div v-if="activeTab === 'repairs'">
						<div v-if="loadingRepairs" class="text-center py-8">
							<div
								class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full mx-auto"
							></div>
							<p class="text-gray-500 mt-4">Loading your repairs...</p>
						</div>

						<div v-else-if="repairs.length === 0" class="text-center py-8">
							<svg
								class="w-16 h-16 text-gray-300 mx-auto mb-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
								/>
							</svg>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
								No Active Repairs
							</h3>
							<p class="text-gray-600 dark:text-gray-400">
								You don't have any active repairs at the moment.
							</p>
						</div>

						<div v-else class="space-y-4">
							<div
								v-for="repair in repairs"
								:key="repair.name"
								@click="openRepairDetail(repair)"
								class="p-4 border border-gray-200 dark:border-warm-border rounded-lg hover:border-[#D4AF37] cursor-pointer transition-colors"
							>
								<div class="flex items-start justify-between">
									<div>
										<p class="font-bold text-gray-900 dark:text-white">
											{{ repair.name }}
										</p>
										<p class="text-sm text-gray-500">
											{{ repair.repair_type_name || repair.repair_type }}
										</p>
									</div>
									<span
										:class="getStatusBadgeClass(repair.status)"
										class="px-3 py-1 rounded-full text-xs font-medium"
									>
										{{ repair.status }}
									</span>
								</div>
								<div class="mt-3 grid grid-cols-2 gap-2 text-sm">
									<div>
										<span class="text-gray-500">Promised:</span>
										<span class="ml-1 font-medium">{{
											formatDate(repair.promised_date)
										}}</span>
									</div>
									<div>
										<span class="text-gray-500">Balance:</span>
										<span class="ml-1 font-medium"
											>${{ formatNum(repair.balance_due) }}</span
										>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- History Tab -->
					<div v-if="activeTab === 'history'">
						<div v-if="loadingHistory" class="text-center py-8">
							<div
								class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full mx-auto"
							></div>
							<p class="text-gray-500 mt-4">Loading repair history...</p>
						</div>

						<div v-else-if="history.length === 0" class="text-center py-8">
							<p class="text-gray-500">No repair history available.</p>
						</div>

						<div v-else class="space-y-3">
							<div
								v-for="item in history"
								:key="item.repair_number"
								class="p-4 bg-gray-50 dark:bg-warm-dark-900 rounded-lg"
							>
								<div class="flex items-center justify-between">
									<div>
										<p class="font-medium text-gray-900 dark:text-white">
											{{ item.repair_number }}
										</p>
										<p class="text-sm text-gray-500">
											{{ item.repair_type_name || 'Repair' }}
										</p>
									</div>
									<div class="text-right">
										<p class="font-medium">
											${{ formatNum(item.total_cost) }}
										</p>
										<p class="text-sm text-gray-500">
											{{ formatDate(item.delivered_date) }}
										</p>
									</div>
								</div>
								<div
									v-if="item.warranty?.has_warranty"
									class="mt-2 pt-2 border-t border-gray-200 dark:border-warm-border"
								>
									<p
										class="text-xs"
										:class="
											item.warranty.is_valid
												? 'text-green-600'
												: 'text-red-600'
										"
									>
										<span class="font-medium">Warranty:</span>
										{{
											item.warranty.is_valid
												? `Valid for ${item.warranty.days_remaining} days`
												: 'Expired'
										}}
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Messages Tab -->
					<div v-if="activeTab === 'messages'">
						<div class="text-center py-8">
							<svg
								class="w-16 h-16 text-gray-300 mx-auto mb-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
								/>
							</svg>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
								Contact Us
							</h3>
							<p class="text-gray-600 dark:text-gray-400 mb-6">
								Have questions about your repair? Send us a message.
							</p>

							<form @submit.prevent="sendMessage" class="max-w-md mx-auto text-left">
								<div class="space-y-4">
									<div>
										<label
											class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
											>Select Repair</label
										>
										<select
											v-model="messageRepairId"
											class="w-full px-4 py-2 border border-gray-200 dark:border-warm-border rounded-lg bg-white dark:bg-warm-dark-900"
										>
											<option value="">General Inquiry</option>
											<option
												v-for="r in repairs.filter(
													(r) => r.status !== 'Delivered'
												)"
												:key="r.name"
												:value="r.name"
											>
												{{ r.name }} - {{ r.repair_type_name }}
											</option>
										</select>
									</div>
									<div>
										<label
											class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
											>Message</label
										>
										<textarea
											v-model="messageText"
											rows="4"
											placeholder="Type your message..."
											class="w-full px-4 py-2 border border-gray-200 dark:border-warm-border rounded-lg bg-white dark:bg-warm-dark-900"
										></textarea>
									</div>
									<button
										type="submit"
										:disabled="sendingMessage || !messageText"
										class="w-full py-2 bg-[#D4AF37] text-black rounded-lg font-medium hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed"
									>
										{{ sendingMessage ? 'Sending...' : 'Send Message' }}
									</button>
								</div>
							</form>
						</div>
					</div>
				</div>
			</div>
		</main>

		<!-- Repair Detail Modal -->
		<div
			v-if="showRepairDetail && selectedRepair"
			class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
			@click.self="showRepairDetail = false"
		>
			<div
				class="bg-white dark:bg-warm-dark-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
			>
				<div class="p-6">
					<div class="flex items-start justify-between mb-6">
						<div>
							<h2 class="text-2xl font-bold text-gray-900 dark:text-white">
								{{ selectedRepair.name }}
							</h2>
							<p class="text-gray-500">{{ selectedRepair.repair_type_name }}</p>
						</div>
						<button
							@click="showRepairDetail = false"
							class="text-gray-400 hover:text-gray-600"
						>
							<svg
								class="w-6 h-6"
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

					<!-- Visual Repair Timeline -->
					<div class="mb-6 p-4 bg-gray-50 dark:bg-warm-dark-900 rounded-xl">
						<h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
							Repair Progress
						</h4>
						<RepairTimeline
							:currentStatus="selectedRepair.status"
							orientation="horizontal"
							variant="full"
						/>
						<div v-if="selectedRepair.promised_date" class="mt-3 text-center">
							<span class="text-sm text-gray-500">Estimated ready by:</span>
							<span class="ml-1 font-bold text-[#D4AF37]">{{
								formatDate(selectedRepair.promised_date)
							}}</span>
						</div>
					</div>

					<!-- Details Grid -->
					<div class="grid grid-cols-2 gap-4 mb-6">
						<div>
							<p class="text-xs text-gray-500 uppercase">Item</p>
							<p class="font-medium">{{ selectedRepair.item_type || 'N/A' }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500 uppercase">Brand</p>
							<p class="font-medium">{{ selectedRepair.item_brand || 'N/A' }}</p>
						</div>
						<div>
							<p class="text-xs text-gray-500 uppercase">Received</p>
							<p class="font-medium">
								{{ formatDate(selectedRepair.received_date) }}
							</p>
						</div>
						<div>
							<p class="text-xs text-gray-500 uppercase">Warehouse</p>
							<p class="font-medium">
								{{
									selectedRepair.warehouse_name ||
									selectedRepair.warehouse ||
									'N/A'
								}}
							</p>
						</div>
					</div>

					<!-- Financial -->
					<div class="mb-6 p-4 bg-gray-50 dark:bg-warm-dark-900 rounded-lg">
						<h3 class="font-bold text-gray-900 dark:text-white mb-3">
							Financial Summary
						</h3>
						<div class="space-y-2 text-sm">
							<div class="flex justify-between">
								<span class="text-gray-500">Estimated Cost:</span>
								<span class="font-medium"
									>${{ formatNum(selectedRepair.estimated_cost) }}</span
								>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-500">Total Cost:</span>
								<span class="font-medium"
									>${{ formatNum(selectedRepair.total_cost) }}</span
								>
							</div>
							<div class="flex justify-between">
								<span class="text-gray-500">Deposit Paid:</span>
								<span class="font-medium text-green-600"
									>-${{ formatNum(selectedRepair.deposit_amount) }}</span
								>
							</div>
							<div
								class="flex justify-between pt-2 border-t border-gray-200 dark:border-warm-border"
							>
								<span class="font-bold">Balance Due:</span>
								<span
									class="font-bold"
									:class="
										selectedRepair.balance_due > 0
											? 'text-red-600'
											: 'text-green-600'
									"
								>
									${{ formatNum(selectedRepair.balance_due) }}
								</span>
							</div>
						</div>
					</div>

					<!-- Online Payment -->
					<RepairPayment
						v-if="selectedRepair && authToken"
						:repair="selectedRepair"
						:authToken="authToken"
					/>

					<!-- Post-Repair Review -->
					<RepairReview
						v-if="selectedRepair && selectedRepair.status === 'Delivered' && authToken"
						:repair="selectedRepair"
						:authToken="authToken"
					/>

					<!-- Estimate Approval -->
					<div
						v-if="selectedRepair.estimate_status === 'Sent'"
						class="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-100 dark:border-yellow-800"
					>
						<h3 class="font-bold text-yellow-800 dark:text-yellow-300 mb-2">
							Estimate Pending Approval
						</h3>
						<p class="text-sm text-yellow-700 dark:text-yellow-400 mb-4">
							Please review and approve the estimate for us to begin work.
						</p>
						<div class="flex gap-2">
							<button
								@click="approveEstimate"
								:disabled="approving"
								class="flex-1 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:opacity-50"
							>
								{{ approving ? 'Approving...' : 'Approve' }}
							</button>
							<button
								@click="rejecting = true"
								:disabled="approving"
								class="flex-1 py-2 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg font-medium hover:bg-red-200 dark:hover:bg-red-800"
							>
								Reject
							</button>
						</div>
					</div>

					<!-- Photo Upload -->
					<div v-if="selectedRepair.status !== 'Delivered'" class="mb-6">
						<h3 class="font-bold text-gray-900 dark:text-white mb-3">
							Upload Reference Photo
						</h3>
						<div
							class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center"
						>
							<input
								ref="photoInput"
								type="file"
								accept="image/*"
								class="hidden"
								@change="handlePhotoUpload"
							/>
							<button
								@click="$refs.photoInput?.click()"
								class="px-4 py-2 bg-gray-100 dark:bg-warm-dark-900 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-warm-dark-800"
							>
								Choose Photo
							</button>
							<p class="text-sm text-gray-500 mt-2">
								Upload reference photos to help with your repair
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Reject Estimate Modal -->
		<div
			v-if="rejecting"
			class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
		>
			<div class="bg-white dark:bg-warm-dark-900 rounded-2xl shadow-2xl max-w-md w-full p-6">
				<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
					Reject Estimate
				</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
					Please let us know why you're rejecting this estimate so we can help you
					better.
				</p>
				<textarea
					v-model="rejectReason"
					rows="3"
					placeholder="Reason for rejection..."
					class="w-full px-4 py-2 border border-gray-200 dark:border-warm-border rounded-lg bg-white dark:bg-warm-dark-900 mb-4"
				></textarea>
				<div class="flex gap-2">
					<button
						@click="cancelEstimateRejection"
						class="flex-1 py-2 bg-gray-100 dark:bg-warm-dark-900 rounded-lg font-medium"
					>
						Cancel
					</button>
					<button
						@click="rejectEstimate"
						:disabled="!rejectReason || rejecting"
						class="flex-1 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 disabled:opacity-50"
					>
						{{ rejecting ? 'Submitting...' : 'Reject' }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import RepairTimeline from '@/components/RepairTimeline.vue'
import RepairPayment from '@/components/RepairPayment.vue'
import RepairReview from '@/components/RepairReview.vue'

// State
const authStep = ref('lookup') // lookup, verify
const authenticated = ref(false)
const customer = ref(null)
const authToken = ref(null)

const lookupIdentifier = ref('')
const lookingUp = ref(false)
const verificationCode = ref('')
const verifying = ref(false)
const sessionToken = ref(null)
const authError = ref('')

const activeTab = ref('repairs')
const repairs = ref([])
const loadingRepairs = ref(false)
const history = ref([])
const loadingHistory = ref(false)

const selectedRepair = ref(null)
const showRepairDetail = ref(false)

const messageRepairId = ref('')
const messageText = ref('')
const sendingMessage = ref(false)

const rejectReason = ref('')
const rejecting = ref(false)
const approving = ref(false)

// Computed
const tabs = computed(() => [
	{
		key: 'repairs',
		label: 'Active Repairs',
		badge: repairs.value.length || null,
		badgeClass: 'bg-gray-200 text-gray-700',
	},
	{ key: 'history', label: 'History', badge: null },
	{ key: 'messages', label: 'Contact', badge: null },
])

// Methods
function returnToLookup() {
	authStep.value = 'lookup'
	verificationCode.value = ''
}

function openRepairDetail(repair) {
	selectedRepair.value = repair
	showRepairDetail.value = true
}

function cancelEstimateRejection() {
	rejecting.value = false
	rejectReason.value = ''
}

async function lookupCustomer() {
	if (!lookupIdentifier.value.trim()) return

	lookingUp.value = true
	authError.value = ''

	try {
		const result = await call('zevar_core.api.repair_customer_portal.customer_lookup', {
			identifier: lookupIdentifier.value,
			identifier_type: lookupIdentifier.value.includes('@') ? 'email' : 'phone',
		})

		if (result.success) {
			sessionToken.value = result.session_token
			customer.value = result.customer
			authStep.value = 'verify'
			// In development, show the verification code
			if (result.verification_code) {
				console.log('Verification code:', result.verification_code)
			}
		} else {
			authError.value = result.message
		}
	} catch (e) {
		authError.value = e.message || 'Lookup failed'
	} finally {
		lookingUp.value = false
	}
}

async function verifyCode() {
	if (!verificationCode.value.trim()) return

	verifying.value = true
	authError.value = ''

	try {
		const result = await call('zevar_core.api.repair_customer_portal.verify_session', {
			session_token: sessionToken.value,
			verification_code: verificationCode.value,
		})

		if (result.success) {
			authToken.value = result.auth_token
			authenticated.value = true
			await loadRepairs()
		} else {
			authError.value = result.message
		}
	} catch (e) {
		authError.value = e.message || 'Verification failed'
	} finally {
		verifying.value = false
	}
}

async function loadRepairs() {
	loadingRepairs.value = true
	try {
		const result = await call('zevar_core.api.repair_customer_portal.get_customer_repairs', {
			auth_token: authToken.value,
		})
		if (result.success) {
			customer.value = result.customer
			repairs.value = result.repairs.filter(
				(r) => r.status !== 'Delivered' && r.status !== 'Cancelled'
			)
		}
	} catch (e) {
		console.error('Failed to load repairs:', e)
	} finally {
		loadingRepairs.value = false
	}
}

async function loadHistory() {
	loadingHistory.value = true
	try {
		const result = await call('zevar_core.api.repair_customer_portal.get_repair_history', {
			auth_token: authToken.value,
		})
		if (result.success) {
			history.value = result.history
		}
	} catch (e) {
		console.error('Failed to load history:', e)
	} finally {
		loadingHistory.value = false
	}
}

async function approveEstimate() {
	if (!selectedRepair.value) return

	approving.value = true
	try {
		const result = await call(
			'zevar_core.api.repair_customer_portal.customer_approve_estimate',
			{
				auth_token: authToken.value,
				repair_order: selectedRepair.value.name,
				customer_name: customer.value?.customer_name || 'Customer',
			}
		)

		if (result.success) {
			await loadRepairs()
			showRepairDetail.value = false
		}
	} catch (e) {
		console.error('Failed to approve estimate:', e)
	} finally {
		approving.value = false
	}
}

async function rejectEstimate() {
	if (!selectedRepair.value || !rejectReason.value) return

	rejecting.value = true
	try {
		const result = await call(
			'zevar_core.api.repair_customer_portal.customer_reject_estimate',
			{
				auth_token: authToken.value,
				repair_order: selectedRepair.value.name,
				customer_name: customer.value?.customer_name || 'Customer',
				reason: rejectReason.value,
			}
		)

		if (result.success) {
			rejecting.value = false
			rejectReason.value = ''
			showRepairDetail.value = false
			await loadRepairs()
		}
	} catch (e) {
		console.error('Failed to reject estimate:', e)
	} finally {
		rejecting.value = false
	}
}

async function sendMessage() {
	if (!messageText.value.trim()) return

	sendingMessage.value = true
	try {
		const result = await call('zevar_core.api.repair_customer_portal.request_repair_update', {
			auth_token: authToken.value,
			repair_order: messageRepairId.value || repairs.value[0]?.name,
			message: messageText.value,
		})

		if (result.success) {
			messageText.value = ''
			messageRepairId.value = ''
			alert('Message sent successfully!')
		}
	} catch (e) {
		alert('Failed to send message: ' + e.message)
	} finally {
		sendingMessage.value = false
	}
}

function logout() {
	authenticated.value = false
	authToken.value = null
	customer.value = null
	repairs.value = []
	history.value = []
	authStep.value = 'lookup'
	lookupIdentifier.value = ''
	verificationCode.value = ''
	sessionToken.value = null
}

function handlePhotoUpload(event) {
	const file = event.target.files?.[0]
	if (!file) return

	const reader = new FileReader()
	reader.onload = async () => {
		try {
			const result = await call(
				'zevar_core.api.repair_customer_portal.upload_reference_photo',
				{
					auth_token: authToken.value,
					repair_order: selectedRepair.value.name,
					photo_data: reader.result,
					filename: file.name,
				}
			)

			if (result.success) {
				alert('Photo uploaded successfully!')
			}
		} catch (e) {
			alert('Failed to upload photo: ' + e.message)
		}
	}
	reader.readAsDataURL(file)
}

// Utility functions
function formatNum(n) {
	return n ? Number(n).toFixed(2) : '0.00'
}
function formatDate(d) {
	return d
		? new Date(d).toLocaleDateString('en-US', {
				month: 'short',
				day: 'numeric',
				year: 'numeric',
		  })
		: ''
}

function getStatusBadgeClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-700',
		Estimated: 'bg-yellow-100 text-yellow-700',
		Approved: 'bg-indigo-100 text-indigo-700',
		'In Progress': 'bg-orange-100 text-orange-700',
		'Waiting for Parts': 'bg-purple-100 text-purple-700',
		'Quality Check': 'bg-cyan-100 text-cyan-700',
		'Ready for Pickup': 'bg-green-100 text-green-700',
		Delivered: 'bg-gray-100 text-gray-700',
		Cancelled: 'bg-red-100 text-red-700',
	}
	return classes[status] || 'bg-gray-100 text-gray-700'
}

function getStatusHeaderClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-900',
		Estimated: 'bg-yellow-100 text-yellow-900',
		Approved: 'bg-indigo-100 text-indigo-900',
		'In Progress': 'bg-orange-100 text-orange-900',
		'Waiting for Parts': 'bg-purple-100 text-purple-900',
		'Quality Check': 'bg-cyan-100 text-cyan-900',
		'Ready for Pickup': 'bg-green-100 text-green-900',
		Delivered: 'bg-gray-100 text-gray-900',
		Cancelled: 'bg-red-100 text-red-900',
	}
	return classes[status] || 'bg-gray-100 text-gray-900'
}

// Watch for tab changes to load history
import { watch } from 'vue'
watch(activeTab, async (newTab) => {
	if (newTab === 'history' && history.value.length === 0) {
		await loadHistory()
	}
})
</script>
