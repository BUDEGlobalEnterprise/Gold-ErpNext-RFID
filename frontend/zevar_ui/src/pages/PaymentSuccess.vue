<template>
	<div class="min-h-screen bg-gray-50 dark:bg-[#0F1115] flex items-center justify-center p-4">
		<div class="max-w-md w-full">
			<!-- Loading State -->
			<div v-if="loading" class="text-center py-20">
				<div class="w-16 h-16 mx-auto mb-6 rounded-full bg-[#D4AF37]/10 flex items-center justify-center">
					<div class="animate-spin rounded-full h-8 w-8 border-2 border-[#D4AF37] border-t-transparent"></div>
				</div>
				<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Verifying Payment</h2>
				<p class="text-gray-500 dark:text-gray-400">Please wait while we confirm your payment...</p>
			</div>

			<!-- Success State -->
			<div v-else-if="paymentVerified" class="text-center" data-testid="payment-success-view">
				<div class="bg-white dark:bg-[#1a1c23] rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 p-8 mb-6">
					<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
						<svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
						</svg>
					</div>

					<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Payment Successful!</h1>
					<p class="text-gray-500 dark:text-gray-400 mb-6">Your payment has been processed securely.</p>

					<div class="bg-gray-50 dark:bg-[#15171e] rounded-xl p-5 border border-gray-100 dark:border-gray-800 space-y-3 text-left">
						<div v-if="sessionData.repair_order" class="flex justify-between text-sm">
							<span class="text-gray-500 dark:text-gray-400">Repair Order</span>
							<span class="font-bold text-gray-900 dark:text-white font-mono">{{ sessionData.repair_order }}</span>
						</div>
						<div class="flex justify-between text-sm">
							<span class="text-gray-500 dark:text-gray-400">Amount Paid</span>
							<span class="font-bold text-[#D4AF37] text-lg">{{ formatCurrency(sessionData.amount_total) }}</span>
						</div>
						<div v-if="sessionData.customer_email" class="flex justify-between text-sm">
							<span class="text-gray-500 dark:text-gray-400">Receipt Email</span>
							<span class="text-gray-700 dark:text-gray-300">{{ sessionData.customer_email }}</span>
						</div>
						<div class="flex justify-between text-sm">
							<span class="text-gray-500 dark:text-gray-400">Payment Status</span>
							<span class="inline-flex items-center gap-1 text-green-600 dark:text-green-400 font-medium">
								<span class="w-2 h-2 rounded-full bg-green-500"></span>
								Paid
							</span>
						</div>
					</div>
				</div>

				<router-link
					to="/repair-portal"
					class="block w-full py-3 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black text-center rounded-xl font-bold hover:opacity-90 transition"
					data-testid="return-to-portal-btn"
				>
					Return to Repair Portal
				</router-link>

				<p class="text-xs text-gray-400 dark:text-gray-600 mt-4">
					You can safely close this window.
					A confirmation email will be sent to your registered email address.
				</p>
			</div>

			<!-- Error State -->
			<div v-else class="text-center" data-testid="payment-error-view">
				<div class="bg-white dark:bg-[#1a1c23] rounded-2xl shadow-xl border border-gray-100 dark:border-gray-800 p-8 mb-6">
					<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
						<svg class="w-10 h-10 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
						</svg>
					</div>

					<h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Payment Verification Failed</h1>
					<p class="text-gray-500 dark:text-gray-400 mb-2">{{ errorMessage }}</p>
					<p class="text-sm text-gray-400 dark:text-gray-500">
						If you believe this is an error, please contact the store.
					</p>
				</div>

				<router-link
					to="/repair-portal"
					class="block w-full py-3 bg-gray-900 dark:bg-gray-700 text-white text-center rounded-xl font-bold hover:opacity-90 transition"
				>
					Return to Portal
				</router-link>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { call } from 'frappe-ui'

const route = useRoute()

const loading = ref(true)
const paymentVerified = ref(false)
const errorMessage = ref('Unable to verify your payment. Please check with the store.')
const sessionData = ref({})

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

onMounted(async () => {
	const sessionId = route.query.session_id

	if (!sessionId) {
		loading.value = false
		errorMessage.value = 'No payment session found.'
		return
	}

	try {
		const result = await call('zevar_core.api.repair_customer_portal.verify_checkout_session', {
			session_id: sessionId,
		})

		if (result?.success && result.payment_status === 'paid') {
			sessionData.value = result
			paymentVerified.value = true
		} else {
			errorMessage.value = result?.message || 'Payment was not completed.'
		}
	} catch (e) {
		errorMessage.value = 'Failed to verify payment. Please contact the store.'
	} finally {
		loading.value = false
	}
})
</script>
