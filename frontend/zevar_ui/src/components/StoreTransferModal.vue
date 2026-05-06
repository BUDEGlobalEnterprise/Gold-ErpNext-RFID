<template>
	<BaseModal :show="true" max-width="max-w-lg" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-blue-100 rounded-lg">
					<svg
						class="w-6 h-6 text-blue-600"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
						/>
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">
						{{ mode === 'dispatch' ? 'Dispatch Transfer' : 'Receive Transfer' }}
					</h3>
					<p v-if="order" class="text-xs text-gray-500">Ref: {{ order.name }}</p>
				</div>
			</div>
		</template>

		<div class="p-6 pt-0">
			<div v-if="mode === 'dispatch'" class="space-y-4">
				<div>
					<label class="block text-sm font-medium mb-1">Source Store *</label>
					<select
						v-model="source"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="">Select source store...</option>
						<option v-for="s in storeWarehouses" :key="s.name" :value="s.name">
							{{ s.warehouse_name || s.name }}
						</option>
					</select>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Destination Store *</label>
					<select
						v-model="destination"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					>
						<option value="">Select destination store...</option>
						<option
							v-for="s in storeWarehouses.filter((w) => w.name !== source)"
							:key="s.name"
							:value="s.name"
						>
							{{ s.warehouse_name || s.name }}
						</option>
					</select>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Carrier Reference</label>
					<input
						v-model="carrierRef"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						placeholder="e.g., FedEx tracking #"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium mb-2">Scan Pieces to Transfer</label>
					<ScannerInput @scan="addSerial" />
					<div class="mt-2 space-y-1 max-h-40 overflow-y-auto">
						<div
							v-for="(sn, i) in serialNos"
							:key="i"
							class="flex items-center justify-between text-sm py-1 px-2 bg-gray-50 dark:bg-warm-dark-700 rounded"
						>
							<span class="font-mono">{{ sn }}</span>
							<button @click="serialNos.splice(i, 1)" class="text-red-500 text-xs">
								Remove
							</button>
						</div>
					</div>
				</div>
			</div>

			<div v-else class="space-y-4">
				<div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-100">
					<p class="text-xs text-blue-700">
						Scan each serial number to confirm receipt. Any missing pieces will be
						flagged as variance.
					</p>
				</div>
				<div>
					<label class="block text-sm font-medium mb-2">Scan Received Pieces</label>
					<ScannerInput @scan="addReceivedSerial" />
					<div class="mt-2 space-y-1 max-h-40 overflow-y-auto">
						<div
							v-for="(sn, i) in receivedSerials"
							:key="i"
							class="flex items-center justify-between text-sm py-1 px-2 bg-green-50 dark:bg-green-900/20 rounded"
						>
							<span class="font-mono">{{ sn }}</span>
							<span class="text-green-600 text-xs">Received</span>
						</div>
					</div>
					<div v-if="receivedSerials.length > 0" class="mt-2 text-sm text-gray-600">
						{{ receivedSerials.length }} of {{ expectedCount }} pieces received
					</div>
				</div>
			</div>
		</div>

		<template #footer>
			<button
				@click="$emit('close')"
				class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
			>
				Cancel
			</button>
			<button
				@click="submit"
				:disabled="
					submitting ||
					(mode === 'dispatch' ? serialNos.length === 0 : receivedSerials.length === 0)
				"
				class="flex-1 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
			>
				{{
					submitting
						? 'Processing...'
						: mode === 'dispatch'
						? `Dispatch ${serialNos.length} Pieces`
						: `Confirm ${receivedSerials.length} Received`
				}}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call, toast, createResource } from 'frappe-ui'
import BaseModal from './BaseModal.vue'
import ScannerInput from './ScannerInput.vue'

const props = defineProps({
	order: { type: Object, default: () => ({}) },
	mode: { type: String, default: 'dispatch' },
})

const emit = defineEmits(['close', 'completed'])

const source = ref(props.order.warehouse || '')
const destination = ref('')
const carrierRef = ref('')
const serialNos = ref([])
const receivedSerials = ref([])
const expectedCount = ref(props.order.expectedCount || 0)
const submitting = ref(false)
const storeWarehouses = ref([])

const whResource = createResource({
	url: 'frappe.client.get_list',
	makeParams: () => ({
		doctype: 'Warehouse',
		filters: { is_group: 1 },
		fields: ['name', 'warehouse_name'],
		limit_page_length: 100,
	}),
	onSuccess: (data) => {
		storeWarehouses.value = data || []
	},
})

function addSerial(value) {
	if (!serialNos.value.includes(value)) serialNos.value.push(value)
}

function addReceivedSerial(value) {
	if (!receivedSerials.value.includes(value)) receivedSerials.value.push(value)
}

async function submit() {
	submitting.value = true
	try {
		if (props.mode === 'dispatch') {
			const items = serialNos.value.map((sn) => ({ serial_no: sn }))
			await call('zevar_core.api.inventory.create_inter_store_transfer', {
				items,
				source: source.value,
				destination: destination.value,
				carrier_ref: carrierRef.value,
			})
			toast({
				title: 'Dispatched',
				message: `${serialNos.value.length} pieces sent`,
				icon: 'check',
				intent: 'success',
			})
		} else {
			await call('zevar_core.api.inventory.do_receive_inter_store_transfer', {
				transfer_name: props.order.name,
				scanned_serials: receivedSerials.value,
			})
			toast({
				title: 'Received',
				message: `${receivedSerials.value.length} pieces confirmed`,
				icon: 'check',
				intent: 'success',
			})
		}
		emit('completed')
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

onMounted(() => {
	whResource.fetch()
})
</script>
