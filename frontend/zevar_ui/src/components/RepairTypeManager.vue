<template>
	<Teleport to="body">
		<div
			class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm"
			@click.self="$emit('close')"
		>
			<div
				class="bg-white dark:bg-warm-dark-900 rounded-2xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto"
			>
				<div class="p-6">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
						Create Repair Type
					</h3>
					<form @submit.prevent="submit" class="space-y-4">
						<div>
							<label class="block text-sm font-medium mb-1">Repair Name *</label>
							<input
								v-model="form.repair_name"
								type="text"
								placeholder="e.g., Ring Sizing, Stone Replacement"
								class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							/>
						</div>
						<div>
							<label class="block text-sm font-medium mb-1">Category</label>
							<input
								v-model="form.category"
								type="text"
								placeholder="e.g., Sizing, Cleaning, Stone Work"
								class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
							/>
						</div>
						<div class="grid grid-cols-2 gap-3">
							<div>
								<label class="block text-sm font-medium mb-1"
									>Base Price ($)</label
								>
								<input
									v-model.number="form.base_price"
									type="number"
									step="0.01"
									min="0"
									class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
								/>
							</div>
							<div>
								<label class="block text-sm font-medium mb-1">Est. Days</label>
								<input
									v-model.number="form.estimated_days"
									type="number"
									min="1"
									class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
								/>
							</div>
						</div>
						<div>
							<label class="block text-sm font-medium mb-1">Description</label>
							<textarea
								v-model="form.description"
								rows="2"
								placeholder="Describe this repair type..."
								class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none"
							></textarea>
						</div>
						<div class="flex gap-3">
							<button
								type="button"
								@click="$emit('close')"
								class="flex-1 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50"
							>
								Cancel
							</button>
							<button
								type="submit"
								:disabled="submitting"
								class="flex-1 py-2 bg-purple-500 text-white rounded-lg text-sm font-medium hover:bg-purple-600 disabled:opacity-50"
							>
								{{ submitting ? 'Creating...' : 'Create Repair Type' }}
							</button>
						</div>
					</form>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { call, toast } from 'frappe-ui'

const emit = defineEmits(['close', 'created'])

const form = ref({
	repair_name: '',
	category: '',
	base_price: 0,
	estimated_days: 7,
	description: '',
})
const submitting = ref(false)

async function submit() {
	if (!form.value.repair_name) {
		toast({
			title: 'Required',
			message: 'Please enter repair name',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}

	submitting.value = true
	try {
		await call('frappe.client.insert', {
			doctype: 'Repair Type',
			repair_name: form.value.repair_name,
			category: form.value.category || undefined,
			base_price: form.value.base_price || 0,
			estimated_days: form.value.estimated_days || 7,
			description: form.value.description || undefined,
			is_active: 1,
		})
		emit('created')
		toast({
			title: 'Success',
			message: 'Repair type created successfully',
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
