<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Appraisals</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ filteredAppraisals.length }} Records
					</span>
				</div>
				<button
					class="px-4 py-2 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black text-xs font-bold rounded-lg hover:bg-gray-800 dark:hover:bg-[#b5952f] transition-all shadow-sm"
				>
					+ New Appraisal
				</button>
			</div>

			<div
				class="flex gap-1 bg-gray-100 dark:bg-[#1C1F26] p-1 rounded-xl mb-6 flex-shrink-0 overflow-x-auto"
			>
				<button
					v-for="tab in statusTabs"
					:key="tab.value"
					@click="activeTab = tab.value"
					class="flex-1 min-w-fit px-4 py-2 text-xs font-bold rounded-lg transition-all whitespace-nowrap"
					:class="
						activeTab === tab.value
							? 'bg-white dark:bg-[#2a2d37] text-gray-900 dark:text-white shadow-sm'
							: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
					"
				>
					{{ tab.label }}
				</button>
			</div>

			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Queue
					</div>
					<div class="text-2xl font-bold text-amber-500">
						{{ appraisalData.filter((a) => a.status === 'Pending').length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						In Progress
					</div>
					<div class="text-2xl font-bold text-blue-500">
						{{ appraisalData.filter((a) => a.status === 'In Progress').length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Completed
					</div>
					<div class="text-2xl font-bold text-green-600">
						{{ appraisalData.filter((a) => a.status === 'Completed').length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Total Value
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ formatCurrency(totalAppraised) }}
					</div>
				</div>
			</div>

			<div class="flex-1 overflow-auto min-h-0">
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
					<div
						v-for="item in filteredAppraisals"
						:key="item.id"
						class="premium-card !p-0 overflow-hidden cursor-pointer group"
					>
						<div class="aspect-[4/3] bg-gray-100 dark:bg-warm-dark-900 relative">
							<div
								class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600"
							>
								<svg
									class="w-12 h-12"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="1"
										d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
									></path>
								</svg>
							</div>
							<div class="absolute top-2 left-2">
								<span
									class="text-[9px] font-bold px-2 py-1 rounded-full"
									:class="
										item.status === 'Pending'
											? 'bg-amber-100 text-amber-700'
											: item.status === 'In Progress'
											? 'bg-blue-100 text-blue-700'
											: 'bg-green-100 text-green-700'
									"
								>
									{{ item.status }}
								</span>
							</div>
							<div v-if="item.certification" class="absolute top-2 right-2">
								<span
									class="text-[9px] font-bold px-2 py-1 rounded-full bg-white/90 dark:bg-warm-dark-950/80 text-gray-800 dark:text-white border border-gray-200 dark:border-warm-border"
								>
									{{ item.certification }}
								</span>
							</div>
						</div>
						<div class="p-4">
							<div
								class="font-bold text-gray-900 dark:text-white text-sm mb-1 truncate"
							>
								{{ item.description }}
							</div>
							<div class="text-[10px] text-gray-500 mb-3">
								{{ item.customer }} · {{ item.date }}
							</div>
							<div class="flex items-center gap-1.5 mb-3">
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>{{ item.metal }}</span
								>
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400"
									>{{ item.purity }}</span
								>
								<span class="text-[9px] text-gray-500 ml-auto font-mono"
									>{{ item.weight }}g</span
								>
							</div>
							<div
								class="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-warm-border/50"
							>
								<div>
									<div class="text-[9px] text-gray-500 uppercase font-bold">
										Estimated Value
									</div>
									<div class="text-lg font-bold text-[#D4AF37] font-mono">
										{{ formatCurrency(item.estimatedValue) }}
									</div>
								</div>
								<div v-if="item.certification" class="text-right">
									<div class="text-[9px] text-gray-500 uppercase font-bold">
										Cert #
									</div>
									<div
										class="text-xs font-mono text-gray-700 dark:text-gray-300"
									>
										{{ item.certNumber }}
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
				<div v-if="filteredAppraisals.length === 0" class="py-20 text-center">
					<p class="text-gray-400 text-sm">No appraisals found.</p>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { useUIStore } from '@/stores/ui.js'
import { ref, computed } from 'vue'

const ui = useUIStore()
const activeTab = ref('all')
const statusTabs = [
	{ value: 'all', label: 'All' },
	{ value: 'Pending', label: 'Queue' },
	{ value: 'In Progress', label: 'In Progress' },
	{ value: 'Completed', label: 'Completed' },
]

import { createResource } from 'frappe-ui'
	import { formatDate } from '@/utils/dates.js'

const appraisalData = ref([])

const appraisalResource = createResource({
	type: 'list',
	doctype: 'Jewelry Appraisal',
	fields: ['*'],
	limit: 100,
	onSuccess(data) {
		appraisalData.value = data.map(a => ({
			id: a.name,
			description: a.description || a.item_description || a.name,
			customer: a.customer || a.customer_name || 'Unknown',
			date: a.creation ? formatDate(a.creation) : 'Unknown',
			metal: a.metal || '-',
			purity: a.purity || '-',
			weight: a.weight || a.gross_weight || 0,
			estimatedValue: a.estimated_value || a.appraised_value || 0,
			certification: a.certification || null,
			certNumber: a.certification_number || '',
			status: a.status || 'Pending'
		}))
	}
})

appraisalResource.fetch()


const totalAppraised = computed(() =>
	appraisalData.value
		.filter((a) => a.status === 'Completed')
		.reduce((s, a) => s + a.estimatedValue, 0)
)

const filteredAppraisals = computed(() => {
	let items = [...appraisalData.value]
	if (activeTab.value !== 'all') items = items.filter((a) => a.status === activeTab.value)
	if (ui.activeFilters.custom_metal_type)
		items = items.filter((a) => a.metal === ui.activeFilters.custom_metal_type)
	if (ui.activeFilters.certification)
		items = items.filter((a) => a.certification === ui.activeFilters.certification)
	if (ui.searchQuery) {
		const q = ui.searchQuery.toLowerCase()
		items = items.filter(
			(a) => a.description.toLowerCase().includes(q) || a.customer.toLowerCase().includes(q)
		)
	}
	return items
})

function formatCurrency(val) {
	return val
		? new Intl.NumberFormat('en-US', {
				style: 'currency',
				currency: 'USD',
				maximumFractionDigits: 0,
		  }).format(val)
		: '$0'
}
</script>
