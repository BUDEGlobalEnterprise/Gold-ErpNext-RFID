<template>
	<BaseModal :show="true" max-width="max-w-md" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
					<svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<h3 class="text-lg font-bold text-gray-900 dark:text-white">Reserve Piece</h3>
			</div>
		</template>

		<div class="p-6 pt-0">
			<div class="mb-3 text-sm text-gray-600 dark:text-gray-400">
				Serial: <span class="font-mono font-bold">{{ serialNo }}</span>
			</div>
			<div class="space-y-3">
				<div>
					<label class="block text-sm font-medium mb-1">Customer *</label>
					<select v-model="customerId" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm">
						<option value="">Select customer...</option>
						<option v-for="c in customers" :key="c.name" :value="c.name">{{ c.customer_name }}</option>
					</select>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Hold Until</label>
					<input v-model="holdUntil" type="datetime-local" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm" />
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Deposit Amount ($)</label>
					<input v-model="depositAmount" type="number" step="0.01" min="0" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm" />
				</div>
			</div>
		</div>

		<template #footer>
			<button @click="$emit('close')" class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
			<button @click="reserve" :disabled="submitting || !customerId" class="flex-1 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 disabled:opacity-50">
				{{ submitting ? 'Reserving...' : 'Reserve' }}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call, toast, createResource } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	serialNo: { type: String, required: true },
})

const emit = defineEmits(['close', 'reserved'])

const customerId = ref('')
const holdUntil = ref('')
const depositAmount = ref(0)
const submitting = ref(false)
const customers = ref([])

const defaultHold = new Date()
defaultHold.setHours(defaultHold.getHours() + 48)
holdUntil.value = defaultHold.toISOString().slice(0, 16)

const custResource = createResource({
	url: 'frappe.client.get_list',
	makeParams: () => ({ doctype: 'Customer', fields: ['name', 'customer_name'], limit_page_length: 200 }),
	onSuccess: (data) => { customers.value = data || [] },
})

async function reserve() {
	submitting.value = true
	try {
		await call('zevar_core.api.inventory.reserve_for_customer', {
			serial_no: props.serialNo,
			customer: customerId.value,
			hold_until: holdUntil.value,
			deposit_amount: depositAmount.value,
		})
		toast({ title: 'Reserved', message: 'Piece reserved successfully', icon: 'check', intent: 'success' })
		emit('reserved')
	} catch (e) {
		toast({ title: 'Error', message: e.messages?.[0] || e.message, icon: 'alert-triangle', intent: 'error' })
	} finally {
		submitting.value = false
	}
}

onMounted(() => { custResource.fetch() })
</script>
