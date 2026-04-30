<template>
	<BaseModal :show="true" max-width="max-w-md" scrollable @close="$emit('close')">
		<template #header>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
					<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
					</svg>
				</div>
				<h3 class="text-lg font-bold text-gray-900 dark:text-white">Damage Report</h3>
			</div>
		</template>

		<div class="p-6 pt-0">
			<div class="mb-3 text-sm text-gray-600 dark:text-gray-400">
				Serial: <span class="font-mono font-bold">{{ serialNo }}</span>
			</div>
			<div class="space-y-3">
				<div>
					<label class="block text-sm font-medium mb-1">Reason *</label>
					<select v-model="reason" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm">
						<option value="">Select reason...</option>
						<option>Scratched</option><option>Broken</option><option>Tarnished</option>
						<option>Defective</option><option>Other</option>
					</select>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Notes</label>
					<textarea v-model="notes" rows="3" class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none" placeholder="Describe the damage..."></textarea>
				</div>
				<div>
					<label class="block text-sm font-medium mb-1">Evidence Photo</label>
					<input type="file" accept="image/*" @change="onFileChange" class="w-full text-sm" />
				</div>
			</div>
			<div class="mt-4 bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-100">
				<p class="text-xs text-red-700">This will write off the piece and move it to the Shrinkage warehouse. This action cannot be undone.</p>
			</div>
		</div>

		<template #footer>
			<button @click="$emit('close')" class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">Cancel</button>
			<button @click="submit" :disabled="submitting || !reason" class="flex-1 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50">
				{{ submitting ? 'Processing...' : 'Write Off' }}
			</button>
		</template>
	</BaseModal>
</template>

<script setup>
import { ref } from 'vue'
import { call, toast } from 'frappe-ui'
import BaseModal from './BaseModal.vue'

const props = defineProps({
	serialNo: { type: String, required: true },
})

const emit = defineEmits(['close', 'completed'])

const reason = ref('')
const notes = ref('')
const evidenceFile = ref(null)
const submitting = ref(false)

function onFileChange(e) {
	evidenceFile.value = e.target.files?.[0] || null
}

async function submit() {
	submitting.value = true
	try {
		await call('zevar_core.api.inventory.do_damage_write_off', {
			serial_no: props.serialNo,
			reason: `${reason.value}${notes.value ? ': ' + notes.value : ''}`,
		})
		toast({ title: 'Written Off', message: 'Piece moved to shrinkage', icon: 'check', intent: 'success' })
		emit('completed')
	} catch (e) {
		toast({ title: 'Error', message: e.messages?.[0] || e.message, icon: 'alert-triangle', intent: 'error' })
	} finally {
		submitting.value = false
	}
}
</script>
