import re

with open("src/components/CheckoutModal.vue", "r") as f:
    content = f.read()

# 1. Add QrcodeVue import
if "import QrcodeVue" not in content:
    content = content.replace(
        "import BaseModal from './BaseModal.vue'",
        "import QrcodeVue from 'qrcode.vue'\nimport BaseModal from './BaseModal.vue'"
    )

# 2. Add refs
if "const checkoutUrl" not in content:
    content = content.replace(
        "const processing = ref(false)",
        "const processing = ref(false)\nconst checkoutUrl = ref('')\nconst checkoutPaymentRequest = ref('')\nconst onlinePaymentMode = ref(null)"
    )

# 3. Add QR step template
qr_template = """
		<!-- ============ QR PAYMENT STATE ============ -->
		<template v-else-if="step === 'qr_payment'">
			<div class="p-8 flex flex-col items-center justify-center text-center w-full min-h-[400px]">
				<h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Customer Scan to Pay</h3>
				<p class="text-sm text-gray-500 mb-8">Have the customer scan this QR code with their mobile device to complete the {{ formatCurrency(onlinePaymentMode?.amount || 0) }} payment.</p>
				
				<div class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 dark:border-warm-border inline-block mb-8">
					<qrcode-vue v-if="checkoutUrl" :value="checkoutUrl" :size="250" level="H" />
				</div>
				
				<div class="flex gap-4">
					<button @click="cancelOnlinePayment" class="px-6 py-2 border border-gray-300 dark:border-warm-border text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-warm-dark-900 transition-colors">
						Cancel & Back
					</button>
					<button @click="pollPaymentStatus" class="px-6 py-2 bg-[#D4AF37] text-white rounded-lg font-medium hover:bg-[#B5952F] transition-colors flex items-center gap-2">
						<i class="w-4 h-4" data-feather="refresh-cw"></i> Refresh Status
					</button>
				</div>
			</div>
		</template>
"""
if "qr_payment" not in content:
    content = content.replace(
        "<!-- ============ SUCCESS STATE ============ -->",
        qr_template + "\n\t\t<!-- ============ SUCCESS STATE ============ -->"
    )

# 4. Modify submitOrderSafe call in processFinalPayment
old_submit = """			const result = await cart.submitOrderSafe(selectedPayments.value, {
				taxExempt: taxExempt.value,
				warehouse: session.currentWarehouse,
				giftCardNumber: gcPayment ? giftCardNumber.value : undefined,
				irs8300Details: step.value === 'irs_8300_form' ? irs8300Details.value : undefined,
			})
			const invoiceName = result?.invoice_name || result?.data?.invoice_name"""

new_submit = """			const onlinePayment = selectedPayments.value.find(p => ['Apple Pay', 'Google Pay', 'Credit Card'].includes(p.mode))
			let paymentsToSubmit = selectedPayments.value
			let onlineGateway = undefined

			if (onlinePayment && !gateway.isTerminalReady.value) {
				onlineGateway = 'Stripe' // Hardcoded to Stripe for now based on plan
				onlinePaymentMode.value = onlinePayment
				paymentsToSubmit = paymentsToSubmit.filter(p => p !== onlinePayment)
			}

			const result = await cart.submitOrderSafe(paymentsToSubmit, {
				taxExempt: taxExempt.value,
				warehouse: session.currentWarehouse,
				giftCardNumber: gcPayment ? giftCardNumber.value : undefined,
				irs8300Details: step.value === 'irs_8300_form' ? irs8300Details.value : undefined,
				online_checkout_gateway: onlineGateway,
			})
			
			const invoiceName = result?.invoice_name || result?.data?.invoice_name
			successInvoiceId.value = invoiceName || null
			
			if (result?.checkout_url) {
				checkoutUrl.value = result.checkout_url
				checkoutPaymentRequest.value = result.payment_request_name
				step.value = 'qr_payment'
				processing.value = false
				
				// Start polling or listening to socket here
				return
			}
"""

if "online_checkout_gateway: onlineGateway" not in content:
    content = content.replace(old_submit, new_submit)

# 5. Add cancelOnlinePayment and pollPaymentStatus functions
functions = """
	async function cancelOnlinePayment() {
		try {
			processing.value = true
			await call('zevar_core.api.pos.cancel_pos_invoice', { invoice_name: successInvoiceId.value })
			step.value = 'review'
			checkoutUrl.value = ''
			checkoutPaymentRequest.value = ''
		} catch (e) {
			error.value = 'Failed to cancel the invoice: ' + (e.message || String(e))
		} finally {
			processing.value = false
		}
	}

	async function pollPaymentStatus() {
		try {
			processing.value = true
			const pr = await call('frappe.client.get', { doctype: 'Payment Request', name: checkoutPaymentRequest.value })
			if (pr && pr.status === 'Paid') {
				// Payment is complete!
				step.value = 'success'
				successBreakdown.value = selectedPayments.value // include the online payment
			} else {
				error.value = 'Payment not yet received.'
				setTimeout(() => { error.value = '' }, 3000)
			}
		} catch (e) {
			error.value = 'Failed to check status'
		} finally {
			processing.value = false
		}
	}
"""
if "cancelOnlinePayment" not in content:
    content = content.replace("const formatCurrency = (val) => {", functions + "\n\tconst formatCurrency = (val) => {")

with open("src/components/CheckoutModal.vue", "w") as f:
    f.write(content)

