<template>
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
		@click.self="$emit('close')"
	>
		<div class="premium-card !rounded-2xl w-full max-w-md mx-4 !p-6">
			<div class="flex items-center justify-between mb-5">
				<h3 class="text-base font-bold text-gray-900 dark:text-white">Schedule Report</h3>
				<button
					@click="$emit('close')"
					class="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800"
				>
					<span class="material-symbols-outlined !text-lg">close</span>
				</button>
			</div>

			<div class="space-y-4">
				<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
					<p class="text-sm font-bold text-gray-900 dark:text-white">
						{{ reportTitle }}
					</p>
					<p class="text-[10px] text-gray-500 dark:text-gray-400">
						Report will be delivered automatically on schedule.
					</p>
				</div>

				<div>
					<label
						class="text-[10px] font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1 block"
						>Frequency</label
					>
					<select
						v-model="form.cron"
						class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-sm text-gray-900 dark:text-white"
					>
						<option value="0 22 * * *">Daily at 10 PM</option>
						<option value="0 8 * * 1">Weekly Monday 8 AM</option>
						<option value="0 8 1 * *">Monthly 1st 8 AM</option>
						<option value="0 8 1 1 *">Yearly Jan 1st 8 AM</option>
					</select>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label
							class="text-[10px] font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1 block"
							>Delivery</label
						>
						<select
							v-model="form.delivery"
							class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-sm text-gray-900 dark:text-white"
						>
							<option value="Email">Email</option>
							<option value="WhatsApp">WhatsApp</option>
							<option value="Both">Both</option>
						</select>
					</div>
					<div>
						<label
							class="text-[10px] font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1 block"
							>Format</label
						>
						<select
							v-model="form.format"
							class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-sm text-gray-900 dark:text-white"
						>
							<option value="PDF">PDF</option>
							<option value="XLSX">XLSX</option>
							<option value="CSV">CSV</option>
						</select>
					</div>
				</div>

				<div v-if="form.delivery !== 'Email'">
					<label
						class="text-[10px] font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1 block"
						>WhatsApp Phone</label
					>
					<input
						v-model="form.phone"
						type="tel"
						placeholder="+1 555 000 0000"
						class="w-full h-10 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-sm text-gray-900 dark:text-white"
					/>
				</div>

				<div
					v-if="errorMsg"
					class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
				>
					<p class="text-xs text-red-600 dark:text-red-300">{{ errorMsg }}</p>
				</div>

				<button
					@click="submit"
					:disabled="submitting"
					class="w-full h-11 rounded-lg bg-[#D4AF37] text-black text-sm font-bold hover:bg-[#c9a432] disabled:opacity-50 flex items-center justify-center gap-2"
				>
					<div
						v-if="submitting"
						class="animate-spin rounded-full h-4 w-4 border-2 border-black/20 border-t-black"
					></div>
					{{ submitting ? 'Creating...' : 'Create Subscription' }}
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { ref, reactive } from 'vue'

const props = defineProps({
	reportId: { type: String, required: true },
	reportTitle: { type: String, default: '' },
})

const emit = defineEmits(['close', 'created'])

const form = reactive({
	cron: '0 22 * * *',
	delivery: 'Email',
	format: 'PDF',
	phone: '',
})

const submitting = ref(false)
const errorMsg = ref('')

function submit() {
	submitting.value = true
	errorMsg.value = ''

	createResource({
		url: 'zevar_core.api.reports.create_report_subscription',
		onSuccess() {
			submitting.value = false
			emit('created')
		},
		onError(err) {
			submitting.value = false
			errorMsg.value = err?.messages?.[0] || err?.message || 'Failed to create subscription.'
		},
	}).fetch({
		report_id: props.reportId,
		cron_expression: form.cron,
		delivery_method: form.delivery,
		export_format: form.format,
		recipient_phone: form.phone,
	})
}
</script>
