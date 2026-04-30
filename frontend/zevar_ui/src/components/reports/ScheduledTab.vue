<template>
	<div class="space-y-4">
		<div class="flex items-center justify-between">
			<div>
				<h3
					class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide"
				>
					Report Subscriptions
				</h3>
				<p class="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5">
					Scheduled reports delivered to your inbox or WhatsApp.
				</p>
			</div>
		</div>

		<div v-if="loading" class="flex justify-center py-10">
			<div
				class="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-[#D4AF37]"
			></div>
		</div>

		<div v-else-if="subscriptions.length === 0" class="premium-card text-center py-12">
			<span class="material-symbols-outlined text-4xl text-gray-300 dark:text-gray-600 mb-3"
				>schedule</span
			>
			<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-1">No Subscriptions</h3>
			<p class="text-xs text-gray-500 dark:text-gray-400">
				Go to All Reports and click the schedule icon on any report to set one up.
			</p>
		</div>

		<div v-else class="space-y-2">
			<div
				v-for="sub in subscriptions"
				:key="sub.name"
				class="premium-card !p-4 flex items-center gap-4"
			>
				<div
					class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
					:class="sub.enabled ? 'bg-emerald-500/10' : 'bg-gray-500/10'"
				>
					<span
						class="material-symbols-outlined !text-lg"
						:class="sub.enabled ? 'text-emerald-500' : 'text-gray-400'"
						>schedule</span
					>
				</div>
				<div class="flex-1 min-w-0">
					<p class="text-sm font-bold text-gray-900 dark:text-white truncate">
						{{ sub.report_title || sub.report_id }}
					</p>
					<div class="flex items-center gap-2 mt-0.5">
						<span
							class="text-[10px] font-bold uppercase tracking-wide"
							:class="
								sub.enabled
									? 'text-emerald-600 dark:text-emerald-400'
									: 'text-gray-400'
							"
							>{{ sub.schedule_label }}</span
						>
						<span class="text-[9px] text-gray-300">&middot;</span>
						<span class="text-[10px] text-gray-400">{{ sub.delivery_method }}</span>
						<span class="text-[9px] text-gray-300">&middot;</span>
						<span class="text-[10px] text-gray-400">{{ sub.export_format }}</span>
					</div>
					<p v-if="sub.next_run" class="text-[10px] text-gray-400 mt-0.5">
						Next: {{ formatDate(sub.next_run) }}
					</p>
				</div>
				<div class="flex items-center gap-1 shrink-0">
					<button
						@click="toggleSub(sub)"
						class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
						:title="sub.enabled ? 'Disable' : 'Enable'"
					>
						<span
							class="material-symbols-outlined !text-base"
							:class="sub.enabled ? 'text-emerald-500' : 'text-gray-400'"
							>{{ sub.enabled ? 'toggle_on' : 'toggle_off' }}</span
						>
					</button>
					<button
						@click="deleteSub(sub.name)"
						class="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
						title="Delete"
					>
						<span class="material-symbols-outlined !text-base">delete</span>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

defineProps({ roleContext: { type: Object, default: () => ({}) } })

const subscriptions = ref([])
const loading = ref(true)

const subsResource = createResource({
	url: 'zevar_core.api.reports.get_report_subscriptions',
	onSuccess(data) {
		subscriptions.value = data || []
		loading.value = false
	},
	onError() {
		subscriptions.value = []
		loading.value = false
	},
})

subsResource.fetch()

function toggleSub(sub) {
	createResource({
		url: 'zevar_core.api.reports.toggle_report_subscription',
		onSuccess(data) {
			sub.enabled = data.enabled
		},
	}).fetch({ name: sub.name })
}

function deleteSub(name) {
	if (!confirm('Delete this subscription?')) return
	createResource({
		url: 'zevar_core.api.reports.delete_report_subscription',
		onSuccess() {
			subscriptions.value = subscriptions.value.filter((s) => s.name !== name)
		},
	}).fetch({ name })
}

function formatDate(dt) {
	if (!dt) return ''
	return new Date(dt).toLocaleString([], {
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	})
}
</script>
