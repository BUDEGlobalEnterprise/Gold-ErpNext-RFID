<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Reports</h2>
					<span
						v-if="roleContext.primary_role"
						class="hidden sm:inline-flex px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider"
						:class="scopeBadgeClass"
					>
						{{ roleContext.scope_label }}
					</span>
				</div>
				<div class="flex flex-col sm:flex-row gap-2 sm:items-center">
					<!-- Search (Only for All Reports tab) -->
					<div v-if="activeTab === 'reports'" class="relative group min-w-[200px] sm:min-w-[240px]">
						<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 !text-lg text-gray-400 group-focus-within:text-[#D4AF37] transition-colors pointer-events-none">search</span>
						<input v-model="search" type="search" placeholder="Search reports..." class="h-9 w-full rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] pl-10 pr-3 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none transition-all" />
					</div>

					<select
						v-model="selectedStore"
						class="h-9 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs text-gray-700 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] outline-none"
					>
						<option value="">All Stores</option>
						<option v-for="(label, code) in storeLocations" :key="code" :value="code">{{ label }}</option>
					</select>
					<button
						@click="refreshAll"
						:disabled="briefResource.loading"
						class="h-9 px-4 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs font-bold text-gray-700 dark:text-gray-200 hover:border-[#D4AF37] disabled:opacity-50 flex items-center gap-2 group transition-all"
						title="Refresh Data"
					>
						<span class="material-symbols-outlined !text-base group-hover:text-[#D4AF37]" :class="{ 'animate-spin': briefResource.loading }">refresh</span>
					</button>
				</div>
			</div>

			<div class="flex gap-1 sm:gap-2 overflow-x-auto pb-3 border-b border-gray-200 dark:border-warm-border mb-4 flex-shrink-0">
				<button
					v-for="tab in mainTabs"
					:key="tab.id"
					@click="activeTab = tab.id"
					class="relative h-10 px-3 sm:px-5 text-xs sm:text-sm font-bold whitespace-nowrap flex items-center gap-1.5 border-b-2 transition-colors -mb-[11px]"
					:class="activeTab === tab.id
						? 'border-[#D4AF37] text-[#D4AF37] dark:text-[#D4AF37]'
						: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'"
				>
					<span class="material-symbols-outlined !text-lg">{{ tab.icon }}</span>
					<span class="hidden sm:inline">{{ tab.label }}</span>
				</button>
			</div>

			<div v-if="loadError" class="flex-1 flex items-center justify-center">
				<div class="premium-card max-w-md text-center">
					<div class="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-300 flex items-center justify-center mx-auto mb-4">
						<span class="material-symbols-outlined">lock</span>
					</div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Reports Unavailable</h3>
					<p class="text-sm text-gray-500 dark:text-gray-400">{{ loadError }}</p>
				</div>
			</div>

			<div v-else class="flex-1 overflow-auto min-h-0 pr-1">
				<DailyBrief v-if="activeTab === 'brief'" :brief="briefData" :loading="briefResource.loading" :role-context="roleContext" @open-report="openReportById" @drill="drillToReport" />
				<AllReports v-else-if="activeTab === 'reports'" :reports="reports" :groups="groups" :role-context="roleContext" :load-error="loadError" :search="search" @open-report="openReport" @open-by-id="openReportById" @subscribe="openSubscribeModal" />
				<Dashboards v-else-if="activeTab === 'dashboards'" @open-dashboard="openDashboard" />
				<ScheduledTab v-else-if="activeTab === 'scheduled'" :role-context="roleContext" />
			</div>
		</div>

		<SubscribeModal v-if="showSubscribeModal" :report-id="subscribeReportId" :report-title="subscribeReportTitle" @close="showSubscribeModal = false" @created="onSubscriptionCreated" />
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { createResource } from 'frappe-ui'
import { computed, ref, provide } from 'vue'
import DailyBrief from '@/components/reports/DailyBrief.vue'
import AllReports from '@/components/reports/AllReports.vue'
import Dashboards from '@/components/reports/Dashboards.vue'
import ScheduledTab from '@/components/reports/ScheduledTab.vue'
import SubscribeModal from '@/components/reports/SubscribeModal.vue'

const mainTabs = [
	{ id: 'brief', label: 'Daily Brief', icon: 'today' },
	{ id: 'reports', label: 'All Reports', icon: 'analytics' },
	{ id: 'dashboards', label: 'Dashboards', icon: 'monitoring' },
	{ id: 'scheduled', label: 'Scheduled', icon: 'schedule' },
]

const storeLocations = {
	'NY-01': 'New York',
	'Miami-01': 'Miami',
	'LA-01': 'Los Angeles',
	'Houston-01': 'Houston',
	'Chicago-01': 'Chicago',
}

const activeTab = ref('brief')
const selectedStore = ref('')
const search = ref('')
const groups = ref([])
const reports = ref([])
const roleContext = ref({})
const briefData = ref(null)
const loadError = ref('')
const showSubscribeModal = ref(false)
const subscribeReportId = ref('')
const subscribeReportTitle = ref('')

const catalogResource = createResource({
	url: 'zevar_core.api.reports.get_report_catalog',
	onSuccess(data) {
		groups.value = data.groups || []
		reports.value = data.reports || []
		roleContext.value = data.role_context || {}
		loadError.value = ''
	},
	onError(error) {
		loadError.value = error?.messages?.[0] || error?.message || 'You do not have access to reports.'
	},
})

const briefResource = createResource({
	url: 'zevar_core.api.reports.get_daily_brief',
	onSuccess(data) {
		briefData.value = data
	},
	onError() {
		briefData.value = null
	},
})

function refreshAll() {
	catalogResource.fetch()
	briefResource.fetch({ store: selectedStore.value || undefined })
}

catalogResource.fetch()
briefResource.fetch({ store: selectedStore.value || undefined })

const scopeBadgeClass = computed(() => {
	const label = roleContext.value.scope_label
	if (label === 'All Stores') return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800'
	if (label === 'Current Store') return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
	return 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-warm-border'
})

function openReport(report) {
	if (report.route) {
		window.location.href = `/pos${report.route}`
		return
	}
	if (report.external_url) {
		window.location.href = report.external_url
		return
	}
	if (report.report_name) {
		window.open(`/app/query-report/${encodeURIComponent(report.report_name)}`, '_blank', 'noopener')
	}
}

function openReportById(reportId) {
	const report = reports.value.find((r) => r.id === reportId)
	if (report) return openReport(report)
	const fallbackMap = {
		eod_stream_summary: 'EOD Stream Summary',
		cash_drawer_reconciliation: 'Cash Drawer Reconciliation',
		payment_method_summary: 'Payment Method Summary',
		refunds_voids_discounts: 'Refunds Voids and Discounts',
	}
	const name = fallbackMap[reportId]
	if (name) window.open(`/app/query-report/${encodeURIComponent(name)}`, '_blank', 'noopener')
}

function drillToReport(reportId) {
	openReportById(reportId)
}

function openDashboard(name) {
	window.location.href = `/pos/reports/dashboards/${name}`
}

function openSubscribeModal(reportId) {
	const report = reports.value.find((r) => r.id === reportId)
	subscribeReportId.value = reportId
	subscribeReportTitle.value = report?.title || reportId
	showSubscribeModal.value = true
}

function onSubscriptionCreated() {
	showSubscribeModal.value = false
}

provide('reports', reports)
provide('roleContext', roleContext)
</script>
