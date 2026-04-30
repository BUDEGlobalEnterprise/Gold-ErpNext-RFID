<template>
	<div class="space-y-4">
		<div class="flex items-center gap-2 mb-4">
			<span class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border">
				{{ visibleReports.length }} Available
			</span>
		</div>

		<div class="flex gap-2 overflow-x-auto pb-2">
			<button v-for="group in tabGroups" :key="group.id" @click="activeGroup = group.id" class="h-8 px-3 rounded-full border text-[11px] font-bold whitespace-nowrap flex items-center gap-1.5" :class="activeGroup === group.id ? 'bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black border-gray-900 dark:border-[#D4AF37]' : 'bg-white dark:bg-[#1C1F26] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-[#D4AF37]'">
				<span class="material-symbols-outlined !text-sm">{{ group.icon }}</span>
				{{ group.label }}
				<span class="text-[9px] opacity-70">{{ group.count }}</span>
			</button>
		</div>

		<div v-if="visibleReports.length === 0" class="premium-card text-center py-12">
			<span class="material-symbols-outlined text-4xl text-gray-300 dark:text-gray-600 mb-3">search_off</span>
			<p class="text-sm text-gray-500 dark:text-gray-400">No reports found for this filter.</p>
		</div>

		<div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 pb-4">
			<div v-for="report in visibleReports" :key="report.id" class="premium-card !rounded-xl !p-4 text-left hover:!border-[#D4AF37] focus:outline-none focus:ring-2 focus:ring-[#D4AF37] transition-all group relative">
				<button @click="$emit('openReport', report)" class="w-full text-left flex items-start gap-4">
					<div class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 overflow-hidden" :class="groupAccent(report.group).bg">
						<span class="material-symbols-outlined !text-xl" :class="groupAccent(report.group).text">{{ groupIcon(report.group) }}</span>
					</div>
					<div class="min-w-0 flex-1">
						<div class="flex items-start justify-between gap-2" :class="{ 'pr-8': canSubscribe }">
							<h3 class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ report.title }}</h3>
							<span v-if="report.featured" class="shrink-0 px-1.5 py-0.5 rounded-full bg-[#D4AF37]/15 text-[#9A6B00] dark:text-[#F2D675] text-[9px] font-bold uppercase">Core</span>
						</div>
						<p class="text-[11px] leading-4 text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{{ report.description }}</p>
						<div class="flex items-center gap-2 mt-2">
							<span class="text-[9px] font-bold uppercase tracking-wider" :class="sensitivityClass(report.sensitivity)">{{ formatSensitivity(report.sensitivity) }}</span>
							<span class="text-[9px] text-gray-300 dark:text-gray-600">&middot;</span>
							<span class="text-[9px] text-gray-400 dark:text-gray-500">{{ formatScope(report.scope) }}</span>
							<span class="ml-auto material-symbols-outlined !text-sm text-gray-400 group-hover:text-[#D4AF37] transition-colors">open_in_new</span>
						</div>
					</div>
				</button>
				<button v-if="canSubscribe" @click.stop="$emit('subscribe', report.id)" class="absolute top-3 right-3 w-7 h-7 rounded-lg flex items-center justify-center text-gray-400 hover:text-[#D4AF37] hover:bg-[#D4AF37]/10 transition-all" title="Schedule this report">
					<span class="material-symbols-outlined !text-base">schedule</span>
				</button>
			</div>
		</div>

		<div v-if="roleContext.own_sales_only" class="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/50">
			<div class="flex items-start gap-2">
				<span class="material-symbols-outlined !text-base text-blue-500 mt-0.5">info</span>
				<p class="text-xs text-blue-700 dark:text-blue-300">You are viewing reports scoped to <strong>your own sales</strong>.</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
	reports: { type: Array, default: () => [] },
	groups: { type: Array, default: () => [] },
	roleContext: { type: Object, default: () => ({}) },
	loadError: { type: String, default: '' },
	search: { type: String, default: '' },
})

defineEmits(['openReport', 'openById', 'subscribe'])

// search is now a prop from parent hub
const activeGroup = ref('all')

const canSubscribe = computed(() => {
	return ['System Manager', 'Store Manager', 'Sales Manager', 'Accounts Manager'].some(r => [props.roleContext.primary_role].includes(r))
})

const tabGroups = computed(() => [
	{ id: 'all', label: 'All', icon: 'apps', count: props.reports.length },
	...props.groups,
])

const visibleReports = computed(() => {
	const needle = props.search.trim().toLowerCase()
	return props.reports.filter((report) => {
		const matchesGroup = activeGroup.value === 'all' || report.group === activeGroup.value
		const matchesSearch = !needle || report.title.toLowerCase().includes(needle) || report.description.toLowerCase().includes(needle)
		return matchesGroup && matchesSearch
	})
})

function groupIcon(groupId) {
	return props.groups.find((g) => g.id === groupId)?.icon || 'analytics'
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

function sensitivityClass(s) {
	return { financial: 'text-rose-600 dark:text-rose-300', manager: 'text-blue-600 dark:text-blue-300', operational: 'text-green-600 dark:text-green-300', customer: 'text-purple-600 dark:text-purple-300', payroll: 'text-cyan-600 dark:text-cyan-300', hr: 'text-cyan-600 dark:text-cyan-300', public_internal: 'text-gray-500 dark:text-gray-300' }[s] || 'text-green-600 dark:text-green-300'
}

function formatScope(scope) {
	return { store: 'Store', role_based: 'Role', all: 'All', own: 'Own', customer: 'Customer', department: 'Dept' }[scope] || scope
}

function formatSensitivity(s) {
	return { financial: 'Financial', manager: 'Manager', operational: 'Operational', customer: 'Customer', payroll: 'Payroll', hr: 'HR', public_internal: 'Internal' }[s] || s
}
</script>
