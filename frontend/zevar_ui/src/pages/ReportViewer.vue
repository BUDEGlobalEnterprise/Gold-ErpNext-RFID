<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0">
				<button @click="$router.push('/reports')" class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors">
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div>
					<h2 class="premium-title !text-xl">{{ reportTitle }}</h2>
				</div>
				<div class="ml-auto flex gap-2">
					<button v-if="rowActions.length > 0" class="h-9 px-3 rounded-lg bg-[#D4AF37] text-black text-xs font-bold hover:bg-[#c9a432] flex items-center gap-1.5">
						<span class="material-symbols-outlined !text-sm">bolt</span>
						Actions Available
					</button>
				</div>
			</div>

			<div class="flex-1 overflow-auto">
				<iframe
					v-if="frappeReportUrl"
					:src="frappeReportUrl"
					class="w-full h-full min-h-[600px] border-0"
					@load="onIframeLoad"
				></iframe>
				<div v-else class="premium-card text-center py-20">
					<span class="material-symbols-outlined text-4xl text-gray-300 dark:text-gray-600 mb-3">report_off</span>
					<p class="text-sm text-gray-500 dark:text-gray-400">Report not available.</p>
				</div>
			</div>

			<div v-if="rowActions.length > 0" class="flex-shrink-0 border-t border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] p-3">
				<p class="text-[10px] font-bold text-gray-400 uppercase tracking-wide mb-2">Row Actions</p>
				<div class="flex gap-2 flex-wrap">
					<button v-for="action in rowActions" :key="action.action" @click="handleAction(action)" class="h-8 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs font-bold text-gray-700 dark:text-gray-200 hover:border-[#D4AF37] hover:text-[#D4AF37] flex items-center gap-1.5">
						<span class="material-symbols-outlined !text-sm">{{ action.icon }}</span>
						{{ action.label }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { createResource } from 'frappe-ui'
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const reportId = computed(() => route.params.reportId || '')
const reportTitle = ref('')
const rowActions = ref([])

const frappeReportUrl = computed(() => {
	if (!reportTitle.value) return ''
	return `/app/query-report/${encodeURIComponent(reportTitle.value)}`
})

const actionsResource = createResource({
	url: 'zevar_core.api.reports.get_row_actions',
	onSuccess(data) {
		rowActions.value = data || []
	},
})

onMounted(() => {
	if (reportId.value) {
		actionsResource.fetch({ report_id: reportId.value })
		const titleMap = {
			reorder_suggestions: 'Reorder Suggestions',
			overdue_layaway_payments: 'Overdue Layaway Payments',
			overdue_repairs: 'Overdue Repairs Report',
			low_stock_alert: 'Low Stock Alert',
			reservation_aging: 'Reservation Aging',
		}
		reportTitle.value = titleMap[reportId.value] || reportId.value
	}
})

function onIframeLoad() {}

function handleAction(action) {
	alert(`Action: ${action.label} — select a row in the report above first.`)
}
</script>
