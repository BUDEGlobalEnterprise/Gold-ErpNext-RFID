<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<!-- Header -->
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Inventory</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ filteredItems.length }} Items
					</span>
				</div>

				<!-- Inline Filter Bar - Occupies the central "blank space" -->
				<div class="flex-1 hidden md:flex justify-center px-4">
					<FilterBar />
				</div>

				<ViewToggle v-model="viewMode" storage-key="zevar_inventory_view" />
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6 flex-shrink-0">
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Items
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ inventoryData.length }}
					</div>
					<div class="text-[10px] text-green-600 font-bold mt-1">+12 this week</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Value
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ formatCurrency(totalValue) }}
					</div>
					<div class="text-[10px] text-gray-500 font-bold mt-1">Retail value</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Low Stock
					</div>
					<div class="text-2xl font-bold text-amber-500">{{ lowStockItems.length }}</div>
					<div class="text-[10px] text-amber-500 font-bold mt-1">Need reorder</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Out of Stock
					</div>
					<div class="text-2xl font-bold text-red-500">{{ outOfStockItems.length }}</div>
					<div class="text-[10px] text-red-500 font-bold mt-1">Requires action</div>
				</div>
			</div>

			<!-- Table View -->
			<div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
				<div v-if="viewMode === 'list'" class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead>
							<tr
								class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50"
							>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Item
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden sm:table-cell"
								>
									Metal
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell"
								>
									Purity
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell"
								>
									Weight
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Stock
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Value
								</th>
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell"
								>
									Status
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="item in filteredItems"
								:key="item.code"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors"
							>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div
											class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-warm-dark-900 overflow-hidden shrink-0"
										>
											<div
												class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600 text-[10px]"
											>
												IMG
											</div>
										</div>
										<div class="min-w-0">
											<div
												class="font-bold text-gray-900 dark:text-white text-xs truncate"
											>
												{{ item.name }}
											</div>
											<div class="text-[10px] text-gray-500 truncate">
												{{ item.code }}
											</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3 hidden sm:table-cell">
									<span
										class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>
										{{ item.metal }}
									</span>
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ item.purity }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 text-right font-mono hidden md:table-cell"
								>
									{{ item.weight }}g
								</td>
								<td class="px-4 py-3 text-right">
									<span
										class="text-xs font-bold"
										:class="
											item.stock <= 0
												? 'text-red-500'
												: item.stock < 5
												? 'text-amber-500'
												: 'text-green-600'
										"
									>
										{{ item.stock }}
									</span>
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white"
								>
									{{ formatCurrency(item.price) }}
								</td>
								<td class="px-4 py-3 text-center hidden lg:table-cell">
									<span
										class="text-[9px] font-bold px-2 py-1 rounded-full"
										:class="
											item.stock <= 0
												? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
												: item.stock < 5
												? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
												: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
										"
									>
										{{
											item.stock <= 0
												? 'OUT OF STOCK'
												: item.stock < 5
												? 'LOW STOCK'
												: 'IN STOCK'
										}}
									</span>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Grid View -->
				<div
					v-else
					class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3"
				>
					<div
						v-for="item in filteredItems"
						:key="item.code"
						class="premium-card !p-0 overflow-hidden group cursor-pointer"
					>
						<div class="aspect-square bg-gray-100 dark:bg-warm-dark-900 relative">
							<div
								class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600"
							>
								<svg
									class="w-10 h-10"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="1"
										d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
									/>
								</svg>
							</div>
							<div class="absolute top-2 right-2">
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
									:class="
										item.stock <= 0
											? 'bg-red-100 text-red-700'
											: item.stock < 5
											? 'bg-amber-100 text-amber-700'
											: 'bg-green-100 text-green-700'
									"
								>
									{{ item.stock }} pcs
								</span>
							</div>
						</div>
						<div class="p-3">
							<div
								class="text-xs font-bold text-gray-900 dark:text-white truncate mb-1"
							>
								{{ item.name }}
							</div>
							<div class="flex items-center gap-1 mb-2">
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>{{ item.metal }}</span
								>
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400"
									>{{ item.purity }}</span
								>
							</div>
							<div class="flex items-center justify-between">
								<span
									class="text-sm font-bold text-gray-900 dark:text-white font-mono"
									>{{ formatCurrency(item.price) }}</span
								>
								<span class="text-[10px] text-gray-500">{{ item.weight }}g</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import FilterBar from '@/components/FilterBar.vue'
import ViewToggle from '@/components/ViewToggle.vue'
import { useUIStore } from '@/stores/ui.js'
import { ref, computed } from 'vue'

import { createResource } from 'frappe-ui'
import { useSessionStore } from '@/stores/session.js'

const ui = useUIStore()
const session = useSessionStore()
const viewMode = ref(localStorage.getItem('zevar_inventory_view') || 'list')

const inventoryData = ref([])

const inventoryResource = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		return { 
			warehouse: session.currentWarehouse,
			page_length: 500, // Fetch up to 500 for local grid filtering, alternatively implement server-side pagination
		}
	},
	onSuccess(data) {
		inventoryData.value = data.map(i => ({
			code: i.item_code,
			name: i.item_name,
			metal: i.metal || '-',
			purity: i.purity || '-',
			weight: i.gross_weight || 0,
			stock: i.stock_qty || 0,
			price: i.price || i.msrp || 0,
			category: i.jewelry_type || i.item_group || 'Other'
		}))
	}
})

// Fetch on mount
inventoryResource.fetch()


const totalValue = computed(() =>
	inventoryData.value.reduce((sum, i) => sum + i.price * Math.max(i.stock, 0), 0)
)
const lowStockItems = computed(() => inventoryData.value.filter((i) => i.stock > 0 && i.stock < 5))
const outOfStockItems = computed(() => inventoryData.value.filter((i) => i.stock <= 0))

const filteredItems = computed(() => {
	let items = [...inventoryData.value]
	const f = ui.activeFilters

	if (f.custom_metal_type) {
		items = items.filter((i) => i.metal === f.custom_metal_type)
	}
	if (f.custom_jewelry_type) {
		items = items.filter((i) => i.category === f.custom_jewelry_type)
	}
	if (f.in_stock_only) {
		items = items.filter((i) => i.stock > 0)
	}
	if (f.out_of_stock_only) {
		items = items.filter((i) => i.stock <= 0)
	}
	if (f.low_stock_only) {
		items = items.filter((i) => i.stock > 0 && i.stock < 5)
	}
	if (f.price_min) {
		items = items.filter((i) => i.price >= f.price_min)
	}
	if (f.price_max) {
		items = items.filter((i) => i.price <= f.price_max)
	}
	if (f.custom_purity) {
		items = items.filter((i) => i.purity === f.custom_purity)
	}
	if (ui.searchQuery) {
		const q = ui.searchQuery.toLowerCase()
		items = items.filter(
			(i) => i.name.toLowerCase().includes(q) || i.code.toLowerCase().includes(q)
		)
	}

	// Sorting
	if (ui.sortBy === 'price_asc') items.sort((a, b) => a.price - b.price)
	else if (ui.sortBy === 'price_desc') items.sort((a, b) => b.price - a.price)
	else if (ui.sortBy === 'weight_asc') items.sort((a, b) => a.weight - b.weight)
	else if (ui.sortBy === 'weight_desc') items.sort((a, b) => b.weight - a.weight)
	else if (ui.sortBy === 'name_asc') items.sort((a, b) => a.name.localeCompare(b.name))

	return items
})

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		maximumFractionDigits: 0,
	}).format(val)
}
</script>
