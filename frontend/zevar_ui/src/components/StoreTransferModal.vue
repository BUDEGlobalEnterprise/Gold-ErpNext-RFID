<template>
	<Teleport to="body">
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" @click.self="$emit('close')">
			<div class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-md w-full mx-4 p-6">
				<div class="flex items-center gap-3 mb-4">
					<div class="p-2 bg-blue-100 rounded-lg">
						<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>
					</div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Store Transfer</h3>
				</div>

				<div class="mb-4">
					<p class="text-sm text-gray-600">Initiating transfer for <span class="font-bold">{{ order.name }}</span></p>
					<p class="text-xs text-gray-500 mt-1">From: {{ order.warehouse || order.receiving_store }}</p>
				</div>

				<form @submit.prevent="submitTransfer" class="space-y-4">
					<div>
						<label class="block text-sm font-medium mb-1">Destination Store *</label>
						<select v-model="destinationStore" required class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800">
							<option value="">Select destination store...</option>
							<option v-for="store in availableStores" :key="store.name" :value="store.name">
								{{ store.warehouse_name || store.name }}
							</option>
						</select>
					</div>

					<div>
						<label class="block text-sm font-medium mb-1">Reason</label>
						<textarea v-model="reason" rows="2" placeholder="Why is this being transferred?"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 text-sm resize-none"></textarea>
					</div>

					<div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-100">
						<p class="text-xs text-yellow-700">
							<svg class="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
							This will create a material transfer and update the repair status. The destination store will be notified.
						</p>
					</div>

					<div class="flex gap-3">
						<button type="button" @click="$emit('close')" class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
						<button type="submit" :disabled="submitting || !destinationStore" class="flex-1 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 disabled:opacity-50">
							{{ submitting ? 'Processing...' : 'Initiate Transfer' }}
						</button>
					</div>
				</form>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import { call, toast, createResource } from 'frappe-ui'

const props = defineProps({
	order: { type: Object, required: true }
})

const emit = defineEmits(['close', 'transferred'])

const destinationStore = ref('')
const reason = ref('')
const submitting = ref(false)
const availableStores = ref([])

const storesResource = createResource({
	url: 'frappe.client.get_list',
	makeParams: () => ({
		doctype: 'Warehouse',
		filters: { is_group: 0 },
		fields: ['name', 'warehouse_name'],
		limit_page_length: 100
	}),
	onSuccess: (data) => {
		// Filter out current store
		const currentStore = props.order.warehouse || props.order.receiving_store
		availableStores.value = (data || []).filter(s => s.name !== currentStore)
	}
})

async function submitTransfer() {
	if (!destinationStore.value) return

	submitting.value = true
	try {
		await call('zevar_core.api.initiate_store_transfer', { repair_order: props.order.name })

		toast({
			title: 'Transfer Initiated',
			message: `Transfer to ${destinationStore.value} has been initiated`,
			icon: 'check',
			intent: 'success'
		})

		emit('transferred')
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message || 'Failed to initiate transfer',
			icon: 'alert-triangle',
			intent: 'error'
		})
	} finally {
		submitting.value = false
	}
}

onMounted(() => {
	storesResource.fetch()
})
</script>
