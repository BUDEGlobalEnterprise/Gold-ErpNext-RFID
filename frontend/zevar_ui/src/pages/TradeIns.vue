<template>
	<AppLayout>
		<div class="flex flex-col">
			<div
				class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 flex-shrink-0"
			>
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Trade-Ins</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ filteredRecords.length }} Records
					</span>
				</div>
				<div class="flex items-center gap-2 self-end sm:self-auto">
					<ViewToggle v-model="viewMode" storage-key="zevar_tradeins_view" />
					<button
						class="px-4 py-2 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black text-xs font-bold rounded-lg hover:bg-gray-800 dark:hover:bg-[#b5952f] transition-all shadow-sm whitespace-nowrap"
					>
						+ New Trade-In
					</button>
				</div>
			</div>

			<div
				class="flex gap-1 bg-gray-100 dark:bg-[#1C1F26] p-1 rounded-xl mb-6 flex-shrink-0 overflow-x-auto"
			>
				<button
					v-for="tab in statusTabs"
					:key="tab.value"
					@click="activeStatus = tab.value"
					class="flex-1 min-w-fit px-4 py-2 text-xs font-bold rounded-lg transition-all whitespace-nowrap"
					:class="
						activeStatus === tab.value
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
						Pending
					</div>
					<div class="text-2xl font-bold text-amber-500">
						{{ tradeInData.filter((t) => t.status === 'Pending Review').length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Accepted
					</div>
					<div class="text-2xl font-bold text-green-600">
						{{ tradeInData.filter((t) => t.status === 'Accepted').length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Credit Issued
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ formatCurrency(totalCredit) }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Avg Value
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ formatCurrency(avgValue) }}
					</div>
				</div>
			</div>

			<div class="flex-1 overflow-auto min-h-0">
				<div
					v-if="viewMode === 'grid'"
					class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3.5"
				>
					<div
						v-for="record in filteredRecords"
						:key="record.id"
						class="bg-white dark:bg-warm-dark-800 rounded-xl border border-gray-100 dark:border-warm-border/50 p-3.5 hover:shadow-md hover:border-[#D4AF37]/40 dark:hover:border-[#D4AF37]/30 transition-all duration-200 cursor-pointer flex flex-col group min-w-0"
					>
						<!-- Header -->
						<div class="flex items-start justify-between gap-1 mb-2.5 min-w-0">
							<div class="flex items-start gap-2 min-w-0">
								<div
									class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400"
								>
									<svg
										class="w-4 h-4"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
										></path>
									</svg>
								</div>
								<div class="min-w-0">
									<div
										class="font-bold text-gray-900 dark:text-white text-xs truncate leading-tight"
									>
										{{ record.description }}
									</div>
									<div class="text-[10px] text-gray-500 mt-0.5 truncate">
										{{ record.customer }} · {{ record.date }}
									</div>
								</div>
							</div>
							<span
								class="text-[9px] font-bold px-1.5 py-0.5 rounded-full shrink-0 ml-1"
								:class="
									record.status === 'Pending Review'
										? 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
										: record.status === 'Accepted'
										? 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400'
										: record.status === 'Rejected'
										? 'bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400'
										: 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
								"
							>
								{{ record.status }}
							</span>
						</div>

						<!-- Details Block -->
						<div
							class="grid grid-cols-2 gap-2 p-2 bg-gray-50 dark:bg-warm-dark-900 rounded-lg border border-gray-100 dark:border-warm-border/30 mt-auto min-w-0"
						>
							<div>
								<div
									class="text-[8px] text-gray-400 dark:text-gray-500 uppercase font-bold mb-0.5"
								>
									Metal
								</div>
								<span
									class="text-[9px] font-bold px-1 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400 inline-block truncate max-w-full"
									>{{ record.metal }} {{ record.purity }}</span
								>
							</div>
							<div>
								<div
									class="text-[8px] text-gray-400 dark:text-gray-500 uppercase font-bold mb-0.5"
								>
									Weight
								</div>
								<div
									class="text-[11px] font-bold text-gray-900 dark:text-white font-mono"
								>
									{{ record.weight }}g
								</div>
							</div>
							<div>
								<div
									class="text-[8px] text-gray-400 dark:text-gray-500 uppercase font-bold mb-0.5"
								>
									Appraised
								</div>
								<div class="text-[11px] font-bold text-[#D4AF37] font-mono">
									{{ formatCurrency(record.appraisedValue) }}
								</div>
							</div>
							<div>
								<div
									class="text-[8px] text-gray-400 dark:text-gray-500 uppercase font-bold mb-0.5"
								>
									Min Purc. (2×)
								</div>
								<div
									class="text-[11px] font-bold font-mono truncate"
									:class="
										record.newPurchase >= record.appraisedValue * 2
											? 'text-green-600'
											: 'text-red-500'
									"
								>
									{{ formatCurrency(record.appraisedValue * 2) }}
								</div>
							</div>
						</div>
					</div>
				</div>
				<div v-if="viewMode === 'list'" class="space-y-2">
					<div
						v-for="record in filteredRecords"
						:key="record.id"
						class="flex items-center justify-between bg-white dark:bg-warm-dark-900/50 rounded-lg px-4 py-3 border border-gray-100 dark:border-warm-border/50 hover:border-[#D4AF37]/30 transition cursor-pointer"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div
								class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
									></path>
								</svg>
							</div>
							<div class="min-w-0">
								<div
									class="font-bold text-gray-900 dark:text-white text-sm truncate"
								>
									{{ record.description }}
								</div>
								<div class="text-[10px] text-gray-500">
									{{ record.customer }} &middot; {{ record.date }}
								</div>
							</div>
						</div>
						<div class="flex items-center gap-4 shrink-0">
							<div class="hidden sm:flex items-center gap-1.5">
								<span
									class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>{{ record.metal }}</span
								>
								<span class="text-[10px] font-mono text-gray-500"
									>{{ record.weight }}g</span
								>
							</div>
							<div class="text-right">
								<div class="text-[9px] text-gray-500 uppercase font-bold">
									Value
								</div>
								<div class="text-sm font-bold text-[#D4AF37] font-mono">
									{{ formatCurrency(record.appraisedValue) }}
								</div>
							</div>
							<span
								class="text-[9px] font-bold px-2 py-1 rounded-full shrink-0"
								:class="
									record.status === 'Pending Review'
										? 'bg-amber-100 text-amber-700'
										: record.status === 'Accepted'
										? 'bg-green-100 text-green-700'
										: record.status === 'Rejected'
										? 'bg-red-100 text-red-700'
										: 'bg-blue-100 text-blue-700'
								"
							>
								{{ record.status }}
							</span>
						</div>
					</div>
				</div>
				<div v-if="filteredRecords.length === 0" class="py-20 text-center">
					<p class="text-gray-400 text-sm">No trade-in records found.</p>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import ViewToggle from '@/components/ViewToggle.vue'
import { useUIStore } from '@/stores/ui.js'
import { ref, computed } from 'vue'

const ui = useUIStore()
const viewMode = ref(localStorage.getItem('zevar_tradeins_view') || 'grid')
const activeStatus = ref('all')
const statusTabs = [
	{ value: 'all', label: 'All' },
	{ value: 'Pending Review', label: 'Pending' },
	{ value: 'Accepted', label: 'Accepted' },
	{ value: 'Rejected', label: 'Rejected' },
	{ value: 'Completed', label: 'Completed' },
]

import { createResource } from 'frappe-ui'
import { formatDate } from '@/utils/dates.js'

const tradeInData = ref([])

const tradeInResource = createResource({
	type: 'list',
	doctype: 'Trade In Record',
	fields: ['*'],
	limit: 100,
	onSuccess(data) {
		tradeInData.value = data.map((t) => ({
			id: t.name,
			description: t.description || t.item_description || t.name,
			customer: t.customer || t.customer_name || 'Unknown',
			date: t.creation ? formatDate(t.creation) : 'Unknown',
			metal: t.metal || '-',
			purity: t.purity || '-',
			weight: t.weight || t.gross_weight || 0,
			appraisedValue: t.appraised_value || t.total_offer_amount || 0,
			newPurchase: t.new_purchase_amount || 0, // Fallback, could be matched to Sales Invoice
			status: t.status || 'Pending Review',
		}))
	},
})

tradeInResource.fetch()

const totalCredit = computed(() =>
	tradeInData.value
		.filter((t) => t.status === 'Accepted' || t.status === 'Completed')
		.reduce((s, t) => s + t.appraisedValue, 0)
)
const avgValue = computed(() => {
	const v = tradeInData.value
	return v.length > 0 ? v.reduce((s, t) => s + t.appraisedValue, 0) / v.length : 0
})

const filteredRecords = computed(() => {
	let records = [...tradeInData.value]
	if (activeStatus.value !== 'all')
		records = records.filter((r) => r.status === activeStatus.value)
	if (ui.activeFilters.custom_metal_type)
		records = records.filter((r) => r.metal === ui.activeFilters.custom_metal_type)
	if (ui.searchQuery) {
		const q = ui.searchQuery.toLowerCase()
		records = records.filter(
			(r) => r.description.toLowerCase().includes(q) || r.customer.toLowerCase().includes(q)
		)
	}
	return records
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
