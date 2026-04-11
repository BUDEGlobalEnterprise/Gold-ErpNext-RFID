<template>
	<Teleport to="body">
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="$emit('close')">
			<div class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-md w-full mx-4 p-6">
				<div class="flex items-center gap-3 mb-4">
					<div class="p-2 bg-green-100 rounded-lg">
						<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
					</div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Record Payment</h3>
				</div>

				<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
					<div class="flex justify-between mb-2">
						<span class="text-sm text-gray-600">Total Cost:</span>
						<span class="font-medium">${{ formatNum(order.total_cost) }}</span>
					</div>
					<div class="flex justify-between mb-2">
						<span class="text-sm text-gray-600">Previous Payments:</span>
						<span class="font-medium text-green-600">${{ formatNum(previousPayments) }}</span>
					</div>
					<div class="flex justify-between pt-2 border-t border-gray-200">
						<span class="font-medium">Remaining Balance:</span>
						<span class="font-bold text-lg">${{ formatNum(remainingBalance) }}</span>
					</div>
				</div>

				<form @submit.prevent="submitPayment" class="space-y-4">
					<div>
						<label class="block text-sm font-medium mb-1">Payment Amount *</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
							<input v-model.number="form.amount" type="number" step="0.01" min="0.01" :max="remainingBalance" required
								placeholder="0.00" class="w-full pl-7 pr-4 py-2 border rounded-lg bg-white dark:bg-gray-800">
						</div>
						<button type="button" @click="form.amount = remainingBalance" class="mt-1 text-xs text-[#D4AF37] hover:underline">
							Pay full balance ({{ formatNum(remainingBalance) }})
						</button>
					</div>

					<div>
						<label class="block text-sm font-medium mb-1">Payment Method *</label>
						<select v-model="form.payment_method" required class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800">
							<option value="Cash">Cash</option>
							<option value="Credit Card">Credit Card</option>
							<option value="Debit Card">Debit Card</option>
							<option value="Check">Check</option>
							<option value="Other">Other</option>
						</select>
					</div>

					<div v-if="form.payment_method === 'Check'">
						<label class="block text-sm font-medium mb-1">Check Number</label>
						<input v-model="form.reference" type="text" placeholder="Check #"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800">
					</div>

					<div>
						<label class="block text-sm font-medium mb-1">Reference (Optional)</label>
						<input v-model="form.reference" type="text" placeholder="Transaction ID, Receipt #, etc."
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800">
					</div>

					<div>
						<label class="block text-sm font-medium mb-1">Notes (Optional)</label>
						<textarea v-model="form.notes" rows="2" placeholder="Additional payment notes..."
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-sm resize-none"></textarea>
					</div>

					<div class="flex gap-3">
						<button type="button" @click="$emit('close')" class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
						<button type="submit" :disabled="submitting" class="flex-1 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 disabled:opacity-50">
							{{ submitting ? 'Recording...' : 'Record Payment' }}
						</button>
					</div>
				</form>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { call, toast } from 'frappe-ui'

const props = defineProps({
	order: { type: Object, required: true }
})

const emit = defineEmits(['close', 'payment-recorded'])

const form = ref({
	amount: null,
	payment_method: 'Cash',
	reference: '',
	notes: ''
})

const submitting = ref(false)

const previousPayments = computed(() => {
	return (props.order.total_cost || 0) - (props.order.balance_due || 0)
})

const remainingBalance = computed(() => {
	return props.order.balance_due || 0
})

function formatNum(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}

async function submitPayment() {
	if (!form.value.amount || form.value.amount <= 0) {
		toast({ title: 'Invalid Amount', message: 'Please enter a valid payment amount', icon: 'alert-circle', intent: 'error' })
		return
	}

	submitting.value = true
	try {
		await call('zevar_core.api.add_repair_payment', {
			repair_order: props.order.name,
			amount: form.value.amount,
			payment_method: form.value.payment_method,
			reference: form.value.reference || undefined,
			notes: form.value.notes || undefined
		})

		toast({
			title: 'Payment Recorded',
			message: `Payment of $${formatNum(form.value.amount)} recorded successfully`,
			icon: 'check',
			intent: 'success'
		})

		emit('payment-recorded')
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message || 'Failed to record payment',
			icon: 'alert-triangle',
			intent: 'error'
		})
	} finally {
		submitting.value = false
	}
}
</script>
