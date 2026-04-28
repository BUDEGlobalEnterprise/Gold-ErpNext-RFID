<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<!-- Header -->
			<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Reports</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ visibleReports.length }} Available
					</span>
					<span
						v-if="roleContext.primary_role"
						class="hidden sm:inline-flex px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider"
						:class="scopeBadgeClass"
					>
						{{ roleContext.scope_label }}
					</span>
				</div>

				<div class="flex flex-col sm:flex-row gap-2 sm:items-center">
					<div class="relative">
						<span
							class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 !text-base text-gray-400"
						>
							search
						</span>
						<input
							v-model="search"
							type="search"
							placeholder="Search reports..."
							class="h-10 w-full sm:w-64 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] pl-9 pr-3 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] outline-none"
						/>
					</div>
					<button
						@click="refreshCatalog"
						:disabled="catalogResource.loading"
						class="h-10 px-4 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs font-bold text-gray-700 dark:text-gray-200 hover:border-[#D4AF37] disabled:opacity-50 flex items-center gap-2"
					>
						<span
							class="material-symbols-outlined !text-base"
							:class="{ 'animate-spin': catalogResource.loading }"
						>
							refresh
						</span>
						Refresh
					</button>
				</div>
			</div>

			<!-- Loading State -->
			<div v-if="catalogResource.loading" class="flex-1 flex items-center justify-center">
				<div class="text-center text-gray-500 dark:text-gray-400">
					<div
						class="animate-spin rounded-full h-7 w-7 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
					></div>
					Loading report catalog...
				</div>
			</div>

			<!-- Error State -->
			<div v-else-if="loadError" class="flex-1 flex items-center justify-center">
				<div class="premium-card max-w-md text-center">
					<div
						class="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-300 flex items-center justify-center mx-auto mb-4"
					>
						<span class="material-symbols-outlined">lock</span>
					</div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
						Reports Unavailable
					</h3>
					<p class="text-sm text-gray-500 dark:text-gray-400">{{ loadError }}</p>
				</div>
			</div>

			<!-- Main Content -->
			<div v-else class="flex-1 overflow-auto min-h-0 pr-1">
				<!-- Summary Stats -->
				<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
					<div class="premium-card !p-4">
						<div
							class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
						>
							Report Groups
						</div>
						<div class="text-2xl font-bold text-gray-900 dark:text-white">
							{{ groups.length }}
						</div>
					</div>
					<div class="premium-card !p-4">
						<div
							class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
						>
							Core Reports
						</div>
						<div class="text-2xl font-bold text-[#D4AF37]">
							{{ featuredReports.length }}
						</div>
					</div>
					<div class="premium-card !p-4">
						<div
							class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
						>
							Role
						</div>
						<div class="text-base font-bold text-gray-900 dark:text-white truncate">
							{{ roleContext.primary_role || 'User' }}
						</div>
					</div>
					<div class="premium-card !p-4">
						<div
							class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
						>
							Scope
						</div>
						<div class="text-base font-bold text-gray-900 dark:text-white">
							{{ roleContext.scope_label || 'Store' }}
						</div>
					</div>
				</div>

				<!-- Group Tabs -->
				<div class="flex gap-2 overflow-x-auto pb-3 mb-2">
					<button
						v-for="group in tabGroups"
						:key="group.id"
						@click="activeGroup = group.id"
						class="h-9 px-4 rounded-full border text-xs font-bold whitespace-nowrap flex items-center gap-2"
						:class="
							activeGroup === group.id
								? 'bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black border-gray-900 dark:border-[#D4AF37]'
								: 'bg-white dark:bg-[#1C1F26] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-[#D4AF37]'
						"
					>
						<span class="material-symbols-outlined !text-base">{{ group.icon }}</span>
						{{ group.label }}
						<span class="text-[10px] opacity-70">{{ group.count }}</span>
					</button>
				</div>

				<!-- Empty State -->
				<div v-if="visibleReports.length === 0" class="premium-card text-center py-12">
					<div
						class="w-12 h-12 rounded-full bg-gray-100 dark:bg-warm-dark-700 flex items-center justify-center mx-auto mb-4"
					>
						<span class="material-symbols-outlined text-gray-400">search_off</span>
					</div>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
						No Reports Found
					</h3>
					<p class="text-sm text-gray-500 dark:text-gray-400">
						Try a different search or report group.
					</p>
				</div>

				<!-- Report Cards Grid -->
				<div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 pb-4">
					<button
						v-for="report in visibleReports"
						:key="report.id"
						@click="openReport(report)"
						class="premium-card !rounded-xl !p-5 text-left hover:!border-[#D4AF37] focus:outline-none focus:ring-2 focus:ring-[#D4AF37] transition-all"
					>
						<div class="flex items-start justify-between gap-3 mb-4">
							<div
								class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
								:class="groupAccent(report.group).bg"
							>
								<span
									class="material-symbols-outlined !text-xl"
									:class="groupAccent(report.group).text"
								>
									{{ groupIcon(report.group) }}
								</span>
							</div>
							<div class="flex flex-wrap justify-end gap-1">
								<span
									v-if="report.featured"
									class="px-2 py-1 rounded-full bg-[#D4AF37]/15 text-[#9A6B00] dark:text-[#F2D675] text-[10px] font-bold uppercase"
								>
									Core
								</span>
								<span
									class="px-2 py-1 rounded-full bg-gray-100 dark:bg-warm-dark-700 text-gray-500 dark:text-gray-300 text-[10px] font-bold uppercase"
								>
									{{ formatScope(report.scope) }}
								</span>
							</div>
						</div>

						<h3 class="text-sm font-black text-gray-900 dark:text-white mb-2">
							{{ report.title }}
						</h3>
						<p class="text-xs leading-5 text-gray-500 dark:text-gray-400 min-h-[3.75rem]">
							{{ report.description }}
						</p>

						<div
							class="mt-4 pt-4 border-t border-gray-100 dark:border-warm-border/50 flex items-center justify-between"
						>
							<span
								class="text-[10px] font-bold uppercase tracking-wider"
								:class="sensitivityClass(report.sensitivity)"
							>
								{{ formatSensitivity(report.sensitivity) }}
							</span>
							<span class="inline-flex items-center gap-1 text-xs font-bold text-gray-900 dark:text-white">
								Open
								<span class="material-symbols-outlined !text-base">open_in_new</span>
							</span>
						</div>
					</button>
				</div>

				<!-- Own Sales Notice -->
				<div
					v-if="roleContext.own_sales_only"
					class="mt-2 mb-4 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/50"
				>
					<div class="flex items-start gap-2">
						<span class="material-symbols-outlined !text-base text-blue-500 mt-0.5">info</span>
						<p class="text-xs text-blue-700 dark:text-blue-300">
							You are viewing reports scoped to <strong>your own sales</strong>. Company totals,
							margins, and cross-store data are restricted to managers.
						</p>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { createResource } from 'frappe-ui'
import { computed, ref, watch } from 'vue'

const groups = ref([])
const reports = ref([])
const defaults = ref({})
const roleContext = ref({})
const search = ref('')
const activeGroup = ref('all')
const loadError = ref('')

const catalogResource = createResource({
	url: 'zevar_core.api.reports.get_report_catalog',
	onSuccess(data) {
		groups.value = data.groups || []
		reports.value = data.reports || []
		defaults.value = data.defaults || {}
		roleContext.value = data.role_context || {}
		loadError.value = ''
		if (!tabGroups.value.some((g) => g.id === activeGroup.value)) {
			activeGroup.value = 'all'
		}
	},
	onError(error) {
		loadError.value =
			error?.messages?.[0] || error?.message || 'You do not have access to reports.'
	},
})

catalogResource.fetch()

// ── Computed ────────────────────────────────────────────────────────────

const tabGroups = computed(() => [
	{ id: 'all', label: 'All', icon: 'apps', count: reports.value.length },
	...groups.value,
])

const featuredReports = computed(() => reports.value.filter((r) => r.featured))

const visibleReports = computed(() => {
	const needle = search.value.trim().toLowerCase()
	return reports.value.filter((report) => {
		const matchesGroup = activeGroup.value === 'all' || report.group === activeGroup.value
		const matchesSearch =
			!needle ||
			report.title.toLowerCase().includes(needle) ||
			report.description.toLowerCase().includes(needle)
		return matchesGroup && matchesSearch
	})
})

const scopeBadgeClass = computed(() => {
	const label = roleContext.value.scope_label
	if (label === 'All Stores') return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800'
	if (label === 'Current Store') return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
	return 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-warm-border'
})

// ── Watchers ────────────────────────────────────────────────────────────

watch(search, () => {
	if (activeGroup.value !== 'all' && visibleReports.value.length === 0) {
		activeGroup.value = 'all'
	}
})

// ── Methods ─────────────────────────────────────────────────────────────

function refreshCatalog() {
	catalogResource.fetch()
}

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
		window.open(
			`/app/query-report/${encodeURIComponent(report.report_name)}`,
			'_blank',
			'noopener'
		)
	}
}

function groupIcon(groupId) {
	return groups.value.find((g) => g.id === groupId)?.icon || 'analytics'
}

function groupAccent(groupId) {
	const accents = {
		daily_closeout: { bg: 'bg-blue-500/10', text: 'text-blue-500' },
		sales: { bg: 'bg-green-500/10', text: 'text-green-500' },
		inventory: { bg: 'bg-slate-500/10', text: 'text-slate-500' },
		layaway: { bg: 'bg-purple-500/10', text: 'text-purple-500' },
		repairs: { bg: 'bg-orange-500/10', text: 'text-orange-500' },
		accounting: { bg: 'bg-rose-500/10', text: 'text-rose-500' },
		employee: { bg: 'bg-cyan-500/10', text: 'text-cyan-500' },
	}
	return accents[groupId] || { bg: 'bg-gray-500/10', text: 'text-gray-500' }
}

function sensitivityClass(sensitivity) {
	const classes = {
		financial: 'text-rose-600 dark:text-rose-300',
		manager: 'text-blue-600 dark:text-blue-300',
		operational: 'text-green-600 dark:text-green-300',
		customer: 'text-purple-600 dark:text-purple-300',
		payroll: 'text-cyan-600 dark:text-cyan-300',
		hr: 'text-cyan-600 dark:text-cyan-300',
		public_internal: 'text-gray-500 dark:text-gray-300',
	}
	return classes[sensitivity] || classes.operational
}

function formatScope(scope) {
	const labels = {
		store: 'Store',
		role_based: 'Role',
		all: 'All',
		own: 'Own',
		customer: 'Customer',
		department: 'Dept',
	}
	return labels[scope] || scope
}

function formatSensitivity(sensitivity) {
	const labels = {
		financial: 'Financial',
		manager: 'Manager',
		operational: 'Operational',
		customer: 'Customer',
		payroll: 'Payroll',
		hr: 'HR',
		public_internal: 'Internal',
	}
	return labels[sensitivity] || sensitivity
}
</script>
