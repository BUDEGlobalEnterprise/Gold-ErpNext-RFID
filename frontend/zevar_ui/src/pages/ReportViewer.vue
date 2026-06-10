<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0">
				<button
					@click="$router.push('/reports')"
					class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors"
				>
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div>
					<h2 class="premium-title !text-xl">{{ reportTitle }}</h2>
					<p v-if="reportMeta.group" class="text-[10px] text-gray-400 mt-0.5">
						{{ reportMeta.group }}
					</p>
				</div>
				<div class="ml-auto flex gap-2">
					<button
						v-for="action in rowActions"
						:key="action.action"
						@click="handleAction(action)"
						class="h-8 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs font-bold text-gray-700 dark:text-gray-200 hover:border-[#D4AF37] hover:text-[#D4AF37] flex items-center gap-1.5"
					>
						<span class="material-symbols-outlined !text-sm">{{ action.icon }}</span>
						{{ action.label }}
					</button>
				</div>
			</div>

			<div class="flex-1 overflow-auto">
				<div v-if="loading" class="flex items-center justify-center h-64">
					<span class="material-symbols-outlined animate-spin text-gray-300 text-3xl"
						>progress_activity</span
					>
				</div>
				<iframe
					v-else-if="frappeReportUrl"
					:src="frappeReportUrl"
					class="w-full h-full min-h-[600px] border-0"
				></iframe>
				<div v-else class="premium-card text-center py-20">
					<span
						class="material-symbols-outlined text-4xl text-gray-300 dark:text-gray-600 mb-3"
						>report_off</span
					>
					<p class="text-sm text-gray-500 dark:text-gray-400">Report not available.</p>
					<p class="text-xs text-gray-400 mt-1">Report ID: {{ reportId }}</p>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const reportId = computed(() => route.params.reportId || '')
const reportTitle = ref('')
const reportMeta = ref({})
const rowActions = ref([])
const loading = ref(true)
const frappeReportName = ref('')

const frappeReportUrl = computed(() => {
	if (!frappeReportName.value) return ''
	return `/app/query-report/${encodeURIComponent(frappeReportName.value)}`
})

async function loadReportData(id) {
	if (!id) return
	loading.value = true
	reportTitle.value = ''
	frappeReportName.value = ''
	rowActions.value = []

	try {
		const [catalogRes, actionsRes] = await Promise.all([
			fetch('/api/method/zevar_core.api.reports.get_report_catalog', {
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
			}),
			fetch(
				`/api/method/zevar_core.api.reports.get_row_actions?report_id=${encodeURIComponent(
					id
				)}`,
				{
					headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
				}
			),
		])

		if (catalogRes.ok) {
			const catalogData = await catalogRes.json()
			const catalog = catalogData.message?.reports || catalogData.message || []
			const found = catalog.find((r) => r.id === id)
			if (found) {
				reportTitle.value = found.title || found.report_name || id
				frappeReportName.value = found.report_name || found.title || ''
				reportMeta.value = { group: found.group || '' }
			} else {
				reportTitle.value = id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
			}
		}

		if (actionsRes.ok) {
			const actionsData = await actionsRes.json()
			rowActions.value = actionsData.message || []
		}
	} catch (e) {
		console.error('Report viewer error:', e)
		reportTitle.value = id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
	} finally {
		loading.value = false
	}
}

function handleAction(action) {
	// Navigate to the report with action context, or show instruction
	const msg = `Select a row in the report above, then click "${action.label}" to ${
		action.description || 'perform this action'
	}.`
	alert(msg)
}

onMounted(() => {
	loadReportData(reportId.value)
})

watch(reportId, (newId) => {
	if (newId) loadReportData(newId)
})
</script>
