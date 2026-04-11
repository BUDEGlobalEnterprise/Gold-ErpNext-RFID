<template>
	<div
		class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4"
	>
		<div class="max-w-lg w-full">
			<!-- Loading -->
			<div
				v-if="loading"
				class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 text-center"
			>
				<div
					class="animate-spin w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full mx-auto mb-4"
				></div>
				<p class="text-gray-600 dark:text-gray-400">Loading estimate details...</p>
			</div>

			<!-- Error -->
			<div
				v-else-if="error"
				class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 text-center"
			>
				<svg
					class="w-16 h-16 text-red-500 mx-auto mb-4"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
					Unable to Load Estimate
				</h2>
				<p class="text-gray-600 dark:text-gray-400 mb-6">{{ error }}</p>
				<p class="text-sm text-gray-500">
					Please contact our store if you believe this is an error.
				</p>
			</div>

			<!-- Estimate Details -->
			<div
				v-else-if="estimate"
				class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl overflow-hidden"
			>
				<!-- Header -->
				<div class="bg-[#D4AF37] p-6 text-center">
					<h1 class="text-2xl font-bold text-black mb-1">ZEVAR JEWELERS</h1>
					<p class="text-black/70">Repair Estimate</p>
				</div>

				<!-- Content -->
				<div class="p-6">
					<div class="text-center mb-6">
						<p class="text-gray-500 text-sm">Repair Number</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-white">
							{{ estimate.repair_number }}
						</p>
					</div>

					<!-- Customer Info -->
					<div class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
						<p class="font-medium text-gray-900 dark:text-white">
							{{ estimate.customer_name }}
						</p>
						<p class="text-sm text-gray-500">{{ estimate.repair_type_name }}</p>
					</div>

					<!-- Item Description -->
					<div class="mb-6">
						<p class="text-sm text-gray-500 mb-1">Item Description</p>
						<p class="text-gray-900 dark:text-white">
							{{ estimate.item_description || 'N/A' }}
						</p>
					</div>

					<!-- Cost Breakdown -->
					<div class="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
						<h3 class="font-bold text-gray-900 dark:text-white mb-3">
							Cost Breakdown
						</h3>
						<div class="space-y-2">
							<div class="flex justify-between text-sm">
								<span class="text-gray-500">Labor Cost</span>
								<span class="font-medium"
									>${{ formatNum(estimate.labor_cost) }}</span
								>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500">Materials Cost</span>
								<span class="font-medium"
									>${{ formatNum(estimate.material_cost) }}</span
								>
							</div>
							<div
								class="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700"
							>
								<span class="font-bold text-gray-900 dark:text-white"
									>Total Cost</span
								>
								<span class="font-bold text-lg text-[#D4AF37]"
									>${{ formatNum(estimate.total_cost) }}</span
								>
							</div>
						</div>
					</div>

					<!-- Promised Date -->
					<div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
						<div class="flex items-center gap-3">
							<svg
								class="w-5 h-5 text-blue-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
								/>
							</svg>
							<div>
								<p class="text-sm text-gray-500">Expected Completion</p>
								<p class="font-medium text-gray-900 dark:text-white">
									{{ formatDate(estimate.promised_date) || 'TBD' }}
								</p>
							</div>
						</div>
					</div>

					<!-- Valid Until -->
					<p class="text-xs text-gray-500 text-center mb-6">
						This estimate is valid until
						{{ formatDate(estimate.estimate_valid_until) }}
					</p>

					<!-- Action Form -->
					<div v-if="!actionTaken" class="space-y-3">
						<p class="text-sm text-gray-600 dark:text-gray-400 text-center mb-4">
							Please review and approve or reject this estimate
						</p>

						<!-- Approve -->
						<div
							class="border-2 border-green-200 dark:border-green-800 rounded-lg p-4"
						>
							<button
								@click="showApproveForm = true"
								class="w-full py-3 bg-green-500 text-white rounded-lg font-bold hover:bg-green-600"
							>
								Approve Estimate
							</button>

							<div v-if="showApproveForm" class="mt-4 space-y-3">
								<input
									v-model="customerName"
									type="text"
									placeholder="Your Full Name"
									class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
								/>
								<textarea
									v-model="approveNotes"
									rows="2"
									placeholder="Optional notes..."
									class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
								></textarea>
								<div class="flex gap-2">
									<button
										@click="submitApprove"
										:disabled="!customerName || submitting"
										class="flex-1 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
									>
										{{ submitting ? 'Submitting...' : 'Confirm Approval' }}
									</button>
									<button
										@click="showApproveForm = false"
										class="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg"
									>
										Cancel
									</button>
								</div>
							</div>
						</div>

						<!-- Reject -->
						<div class="border-2 border-red-200 dark:border-red-800 rounded-lg p-4">
							<button
								@click="showRejectForm = true"
								class="w-full py-3 bg-white dark:bg-gray-800 text-red-600 dark:text-red-400 border border-red-300 dark:border-red-700 rounded-lg font-bold hover:bg-red-50 dark:hover:bg-red-900/20"
							>
								Reject Estimate
							</button>

							<div v-if="showRejectForm" class="mt-4 space-y-3">
								<p class="text-sm text-gray-600 dark:text-gray-400">
									Please let us know why you're rejecting this estimate:
								</p>
								<textarea
									v-model="rejectReason"
									rows="3"
									placeholder="Reason for rejection..."
									class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
								></textarea>
								<input
									v-model="customerName"
									type="text"
									placeholder="Your Full Name"
									class="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
								/>
								<div class="flex gap-2">
									<button
										@click="submitReject"
										:disabled="!rejectReason || !customerName || submitting"
										class="flex-1 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:opacity-50"
									>
										{{ submitting ? 'Submitting...' : 'Confirm Rejection' }}
									</button>
									<button
										@click="showRejectForm = false"
										class="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg"
									>
										Cancel
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Success Message -->
					<div v-else class="text-center py-8">
						<svg
							class="w-16 h-16 text-green-500 mx-auto mb-4"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
							{{ successMessage }}
						</h3>
						<p class="text-gray-600 dark:text-gray-400">
							We'll be in touch with you soon.
						</p>
					</div>
				</div>

				<!-- Footer -->
				<div
					class="p-4 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
				>
					<p class="text-xs text-gray-500 text-center">
						Have questions? Call us at
						<a href="tel:+15551234567" class="text-[#D4AF37] font-medium"
							>(555) 123-4567</a
						>
					</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { call } from 'frappe-ui'

const route = useRoute()
const token = route.params.token

const loading = ref(true)
const error = ref(null)
const estimate = ref(null)

const showApproveForm = ref(false)
const showRejectForm = ref(false)
const customerName = ref('')
const approveNotes = ref('')
const rejectReason = ref('')
const submitting = ref(false)
const actionTaken = ref(false)
const successMessage = ref('')

onMounted(async () => {
	await loadEstimate()
})

async function loadEstimate() {
	loading.value = true
	error.value = null

	try {
		const result = await call('zevar_core.api.get_estimate_details_for_approval', {
			token: token,
		})

		if (result.success) {
			estimate.value = result
		} else {
			error.value = result.message || 'Unable to load estimate details'
		}
	} catch (e) {
		error.value = e.message || 'Failed to load estimate'
	} finally {
		loading.value = false
	}
}

async function submitApprove() {
	if (!customerName.value) return

	submitting.value = true
	try {
		const result = await call('zevar_core.api.public_estimate_approval', {
			token: token,
			action: 'approve',
			customer_name: customerName.value,
			notes: approveNotes.value || null,
		})

		if (result.success) {
			actionTaken.value = true
			successMessage.value = 'Estimate Approved!'
		} else {
			error.value = result.message
		}
	} catch (e) {
		error.value = e.message || 'Failed to approve estimate'
	} finally {
		submitting.value = false
	}
}

async function submitReject() {
	if (!customerName.value || !rejectReason.value) return

	submitting.value = true
	try {
		const result = await call('zevar_core.api.public_estimate_approval', {
			token: token,
			action: 'reject',
			customer_name: customerName.value,
			notes: rejectReason.value,
		})

		if (result.success) {
			actionTaken.value = true
			successMessage.value = 'Estimate Rejected'
		} else {
			error.value = result.message
		}
	} catch (e) {
		error.value = e.message || 'Failed to reject estimate'
	} finally {
		submitting.value = false
	}
}

function formatNum(n) {
	return n ? Number(n).toFixed(2) : '0.00'
}
function formatDate(d) {
	return d
		? new Date(d).toLocaleDateString('en-US', {
				month: 'long',
				day: 'numeric',
				year: 'numeric',
		  })
		: ''
}
</script>
