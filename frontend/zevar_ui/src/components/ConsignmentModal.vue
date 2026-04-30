<template>
	<BaseModal :show="true" max-width="max-w-2xl" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
					<svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
					</svg>
				</div>
				<div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ mode === 'out' ? 'Consignment Out' : 'Consignment Return' }}</h3>
				</div>
			</div>
		</template>

		<div class="p-6 pt-0">
			<div v-if="mode === 'out'" class="space-y-3">
				<div>
					<label class="block text-sm font-medium mb-1">Event Name *</label>
					<input v-model="eventName" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm" placeholder="e.g., Bridal Show 2026" />
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Return By</label>
					<input v-model="returnBy" type="date" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm" />
				</div>
				<div>
					<label class="block text-sm font-medium mb-2">Scan Pieces</label>
					<ScannerInput @scan="addSerial" />
					<div class="mt-2 space-y-1 max-h-40 overflow-y-auto">
						<div v-for="(sn, i) in serialNos" :key="i" class="flex items-center justify-between text-sm py-1 px-2 bg-gray-50 dark:bg-warm-dark-700 rounded">
							<span class="font-mono">{{ sn }}</span>
							<button @click="serialNos.splice(i, 1)" class="text-red-500 text-xs">Remove</button>
						</div>
					</div>
				</div>
			</div>

			<div v-else class="space-y-3">
				<div>
					<label class="block text-sm font-medium mb-1">Event Name *</label>
					<input v-model="eventName" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm" />
				</div>
				<div>
					<label class="block text-sm font-medium mb-2">Scan Returned Pieces</label>
					<ScannerInput @scan="addSerial" />
					<div class="mt-2 space-y-1 max-h-40 overflow-y-auto">
						<div v-for="(sn, i) in serialNos" :key="i" class="flex items-center justify-between text-sm py-1 px-2 bg-gray-50 dark:bg-warm-dark-700 rounded">
							<span class="font-mono">{{ sn }}</span>
							<button @click="serialNos.splice(i, 1)" class="text-red-500 text-xs">Remove</button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<template #footer>
			<button @click="$emit('close')" class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
			<button @click="submit" :disabled="submitting || serialNos.length === 0 || !eventName" class="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50">
				{{ submitting ? 'Processing...' : (mode === 'out' ? `Consign ${serialNos.length} Pieces` : `Return ${serialNos.length} Pieces`) }}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'
import ScannerInput from './ScannerInput.vue'

const props = defineProps({
	mode: { type: String, default: 'out' },
	items: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'completed'])

const eventName = ref('')
const returnBy = ref('')
const serialNos = ref(props.items.map(i => i.serial_no).filter(Boolean))
const submitting = ref(false)

function addSerial(value) {
	if (!serialNos.value.includes(value)) {
		serialNos.value.push(value)
	}
}

async function submit() {
	submitting.value = true
	try {
		const endpoint = props.mode === 'out'
			? 'zevar_core.api.inventory.do_consign_out'
			: 'zevar_core.api.inventory.do_consign_in'

		const payload = props.mode === 'out'
			? { items: serialNos.value.map(sn => ({ serial_no: sn })), event_name: eventName.value, return_by: returnBy.value }
			: { event_name: eventName.value, scanned_serials: serialNos.value }

		await call(endpoint, payload)
		toast({ title: 'Done', message: 'Consignment processed', icon: 'check', intent: 'success' })
		emit('completed')
	} catch (e) {
		toast({ title: 'Error', message: e.messages?.[0] || e.message, icon: 'alert-triangle', intent: 'error' })
	} finally {
		submitting.value = false
	}
}
</script>
