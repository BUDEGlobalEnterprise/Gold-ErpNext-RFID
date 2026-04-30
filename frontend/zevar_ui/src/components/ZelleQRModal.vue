<template>
	<BaseModal :show="show" max-width="max-w-md" :show-close="true" @close="close">
		<div class="p-6 text-center">
			<h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Pay with Zelle</h2>
			<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
				Scan the QR code below with your banking app to send {{ formatCurrency(amount) }}
			</p>

			<div v-if="loading" class="py-12 flex items-center justify-center">
				<div
					class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37]"
				></div>
			</div>

			<div v-else-if="qrData" class="flex flex-col items-center">
				<div class="bg-white p-4 rounded-2xl shadow-lg mb-4">
					<img
						:src="'data:image/png;base64,' + qrData.qr_code_base64"
						alt="Zelle QR Code"
						class="w-64 h-64"
					/>
				</div>
				<p class="text-sm text-gray-500 dark:text-gray-400 mb-1">
					Send to:
					<span class="font-mono font-bold text-gray-900 dark:text-white">{{
						qrData.merchant_alias
					}}</span>
				</p>
				<p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
					Amount:
					<span class="font-bold text-gray-900 dark:text-white">{{
						formatCurrency(amount)
					}}</span>
				</p>

				<div
					v-if="checking"
					class="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400 mb-4"
				>
					<div
						class="animate-spin rounded-full h-4 w-4 border-2 border-blue-300 border-t-blue-600"
					></div>
					Checking for payment...
				</div>
				<div
					v-else-if="paymentReceived"
					class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/30 rounded-xl p-4 mb-4"
				>
					<p class="text-green-600 dark:text-green-400 font-bold">Payment Received!</p>
				</div>

				<div class="flex gap-3 w-full">
					<button
						@click="checkPayment"
						:disabled="checking || paymentReceived"
						class="flex-1 py-2.5 rounded-xl font-bold text-sm bg-gray-100 dark:bg-warm-dark-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-white/10 transition disabled:opacity-50"
					>
						Check Payment
					</button>
					<button
						@click="close"
						class="flex-1 py-2.5 rounded-xl font-bold text-sm bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black hover:bg-gray-800 dark:hover:bg-[#b5952f] transition"
					>
						{{ paymentReceived ? 'Done' : 'Cancel' }}
					</button>
				</div>
			</div>

			<div
				v-else-if="error"
				class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-xl p-4 mb-4"
			>
				<p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
			</div>
		</div>
	</BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { createResource } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	amount: { type: Number, default: 0 },
	invoiceReference: { type: String, default: null },
})
const emit = defineEmits(['close', 'paymentReceived'])

const loading = ref(false)
const checking = ref(false)
const paymentReceived = ref(false)
const qrData = ref(null)
const error = ref('')

watch(
	() => props.show,
	async (isOpen) => {
		if (isOpen) {
			paymentReceived.value = false
			qrData.value = null
			error.value = ''
			loading.value = true
			try {
				const resource = createResource({
					url: 'zevar_core.integrations.zelle.api.generate_zelle_qr',
					auto: false,
				})
				const result = await resource.submit({
					amount: props.amount,
					invoice_reference: props.invoiceReference,
				})
				qrData.value = result?.message ?? result
			} catch (e) {
				error.value = e?.message || 'Failed to generate QR code'
			} finally {
				loading.value = false
			}
		}
	}
)

async function checkPayment() {
	checking.value = true
	try {
		const resource = createResource({
			url: 'zevar_core.integrations.zelle.api.check_zelle_payment',
			auto: false,
		})
		const result = await resource.submit({
			amount: props.amount,
			reference: qrData.value?.reference,
		})
		const data = result?.message ?? result
		if (data?.received) {
			paymentReceived.value = true
			emit('paymentReceived', data)
		}
	} catch (e) {
		// Silent fail, just keep polling
	} finally {
		checking.value = false
	}
}

function close() {
	emit('close')
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}
</script>
