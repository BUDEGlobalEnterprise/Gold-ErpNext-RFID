<template>
	<BaseModal :show="true" max-width="max-w-md" @close="$emit('close')">
		<template #header>
			<h3 class="text-lg font-bold text-gray-900 dark:text-white">Create New Customer</h3>
		</template>

		<div class="p-6">
			<form @submit.prevent="submit" class="space-y-4">
				<!-- Customer Name -->
				<div>
					<label class="block text-sm font-medium mb-1">Customer Name *</label>
					<input
						v-model="form.customer_name"
						type="text"
						placeholder="Full Name"
						required
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>

				<!-- Phone -->
				<div>
					<label class="block text-sm font-medium mb-1">Phone Number *</label>
					<input
						v-model="form.phone"
						type="tel"
						placeholder="(555) 123-4567"
						required
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>

				<!-- Email -->
				<div>
					<label class="block text-sm font-medium mb-1">Email</label>
					<input
						v-model="form.email"
						type="email"
						placeholder="customer@example.com"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>

				<!-- Address -->
				<div>
					<label class="block text-sm font-medium mb-1">Address</label>
					<textarea
						v-model="form.address"
						rows="2"
						placeholder="Street address, City, State, ZIP"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none"
					></textarea>
				</div>

				<!-- Quick Notes -->
				<div>
					<label class="block text-sm font-medium mb-1">Notes</label>
					<input
						v-model="form.notes"
						type="text"
						placeholder="VIP, preferences, etc."
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>

				<!-- Actions -->
				<div class="flex gap-3 pt-2">
					<button
						type="button"
						@click="$emit('close')"
						class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800"
					>
						Cancel
					</button>
					<button
						type="submit"
						:disabled="submitting"
						class="flex-1 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] disabled:opacity-50"
					>
						{{ submitting ? 'Creating...' : 'Create Customer' }}
					</button>
				</div>
			</form>
		</div>
	</BaseModal>
</template>

<script setup>
import { ref } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const emit = defineEmits(['close', 'created'])

const form = ref({
	customer_name: '',
	phone: '',
	email: '',
	address: '',
	notes: '',
})

const submitting = ref(false)

async function submit() {
	if (!form.value.customer_name) {
		toast({
			title: 'Required',
			message: 'Please enter customer name',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	if (!form.value.phone) {
		toast({
			title: 'Required',
			message: 'Please enter phone number',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}

	submitting.value = true
	try {
		const customer = await call('frappe.client.insert', {
			doctype: 'Customer',
			customer_name: form.value.customer_name,
			phone: form.value.phone,
			mobile: form.value.phone,
			email_id: form.value.email || undefined,
			address_line1: form.value.address || undefined,
			notes: form.value.notes || undefined,
		})
		emit('created', customer)
		toast({
			title: 'Success',
			message: 'Customer created successfully',
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message,
			icon: 'alert-triangle',
			intent: 'error',
		})
	} finally {
		submitting.value = false
	}
}
</script>
