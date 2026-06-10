<template>
	<div
		class="mb-6 p-4 bg-white dark:bg-warm-dark-900 rounded-lg border border-gray-200 dark:border-warm-border"
	>
		<h3 class="font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
			<span class="material-symbols-outlined !text-lg text-green-500">credit_card</span>
			Payment
		</h3>

		<div
			v-if="!repair.balance_due || repair.balance_due <= 0"
			class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg"
		>
			<div
				class="w-12 h-12 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center mx-auto mb-2 text-green-600 dark:text-green-400"
			>
				<span class="material-symbols-outlined">check_circle</span>
			</div>
			<p class="font-bold text-green-700 dark:text-green-300">Fully Paid</p>
			<p class="text-sm text-green-600 dark:text-green-400">Thank you for your payment!</p>
		</div>

		<div v-else>
			<div class="flex justify-between items-center mb-4">
				<span class="text-gray-600 dark:text-gray-400">Balance Due</span>
				<span class="text-xl font-bold text-gray-900 dark:text-white"
					>${{ formatNum(repair.balance_due) }}</span
				>
			</div>

			<div v-if="loading" class="flex justify-center p-4">
				<div
					class="animate-spin rounded-full h-8 w-8 border-2 border-[#D4AF37] border-t-transparent"
				></div>
			</div>

			<div v-else-if="paymentUrl" class="space-y-4">
				<p class="text-sm text-gray-600 dark:text-gray-400 text-center">
					Click below to complete your payment securely.
				</p>
				<a
					:href="paymentUrl"
					target="_blank"
					class="block w-full py-3 bg-[#D4AF37] text-black text-center rounded-lg font-bold hover:bg-[#c9a432] transition"
				>
					Pay Securely
				</a>
			</div>

			<div v-else class="space-y-3">
				<p class="text-sm text-gray-600 dark:text-gray-400">
					Pay your balance online to expedite your pickup.
				</p>
				<button
					@click="initiatePayment"
					class="w-full py-3 bg-gray-900 dark:bg-white text-white dark:text-black rounded-lg font-bold hover:bg-gray-800 dark:hover:bg-gray-200 transition flex items-center justify-center gap-2"
				>
					<span class="material-symbols-outlined">lock</span>
					Pay Online
				</button>
			</div>

			<div
				v-if="error"
				class="mt-3 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-lg text-sm"
			>
				{{ error }}
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { call } from 'frappe-ui'

const props = defineProps({
	repair: {
		type: Object,
		required: true,
	},
	authToken: {
		type: String,
		required: true,
	},
})

const loading = ref(false)
const error = ref(null)
const paymentUrl = ref(null)

async function initiatePayment() {
	loading.value = true
	error.value = null

	try {
		const res = await call('zevar_core.api.repair_customer_portal.initiate_repair_payment', {
			auth_token: props.authToken,
			repair_order: props.repair.name,
			provider: 'stripe', // Default to Stripe for now
		})

		if (res.success && res.payment_url) {
			paymentUrl.value = res.payment_url
			// Open automatically if possible
			window.open(res.payment_url, '_blank')
		} else {
			error.value = res.message || 'Failed to initiate payment'
		}
	} catch (e) {
		console.error('Payment error:', e)
		error.value = e.message || 'An error occurred while initiating payment'
	} finally {
		loading.value = false
	}
}

function formatNum(n) {
	return Number(n || 0).toLocaleString('en-US', {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	})
}
</script>
