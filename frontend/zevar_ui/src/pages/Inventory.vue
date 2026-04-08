<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<!-- Header -->
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Inventory</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-white/5 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-white/10"
					>
						{{ filteredItems.length }} Items
					</span>
				</div>

				<!-- Inline Filter Bar - Occupies the central "blank space" -->
				<div class="flex-1 hidden md:flex justify-center px-4">
					<FilterBar />
				</div>

				<div class="flex gap-2">
					<button
						@click="viewMode = 'grid'"
						class="p-2 rounded-lg border transition"
						:class="
							viewMode === 'grid'
								? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
								: 'border-gray-200 dark:border-gray-700 text-gray-400 hover:text-gray-600'
						"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
						</svg>
					</button>
					<button
						@click="viewMode = 'table'"
						class="p-2 rounded-lg border transition"
						:class="
							viewMode === 'table'
								? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
								: 'border-gray-200 dark:border-gray-700 text-gray-400 hover:text-gray-600'
						"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
						</svg>
					</button>
				</div>
			</div>

			<!-- Stats Cards -->
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Items</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ inventoryData.length }}</div>
					<div class="text-[10px] text-green-600 font-bold mt-1">+12 this week</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Value</div>
					<div class="text-2xl font-bold text-[#D4AF37]">{{ formatCurrency(totalValue) }}</div>
					<div class="text-[10px] text-gray-500 font-bold mt-1">Retail value</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Low Stock</div>
					<div class="text-2xl font-bold text-amber-500">{{ lowStockItems.length }}</div>
					<div class="text-[10px] text-amber-500 font-bold mt-1">Need reorder</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Out of Stock</div>
					<div class="text-2xl font-bold text-red-500">{{ outOfStockItems.length }}</div>
					<div class="text-[10px] text-red-500 font-bold mt-1">Requires action</div>
				</div>
			</div>

			<!-- Table View -->
			<div class="flex-1 overflow-auto min-h-0">
				<div v-if="viewMode === 'table'" class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead>
							<tr class="bg-gray-50 dark:bg-white/5 border-b border-gray-200 dark:border-white/5">
								<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Item</th>
								<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden sm:table-cell">Metal</th>
								<th class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell">Purity</th>
								<th class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell">Weight</th>
								<th class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Stock</th>
								<th class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider">Value</th>
								<th class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell">Status</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="item in filteredItems"
								:key="item.code"
								class="border-b border-gray-100 dark:border-white/5 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors"
							>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800 overflow-hidden shrink-0">
											<div class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600 text-[10px]">IMG</div>
										</div>
										<div class="min-w-0">
											<div class="font-bold text-gray-900 dark:text-white text-xs truncate">{{ item.name }}</div>
											<div class="text-[10px] text-gray-500 truncate">{{ item.code }}</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3 hidden sm:table-cell">
									<span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400">
										{{ item.metal }}
									</span>
								</td>
								<td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell">{{ item.purity }}</td>
								<td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 text-right font-mono hidden md:table-cell">{{ item.weight }}g</td>
								<td class="px-4 py-3 text-right">
									<span
										class="text-xs font-bold"
										:class="item.stock <= 0 ? 'text-red-500' : item.stock < 5 ? 'text-amber-500' : 'text-green-600'"
									>
										{{ item.stock }}
									</span>
								</td>
								<td class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white">
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
										{{ item.stock <= 0 ? 'OUT OF STOCK' : item.stock < 5 ? 'LOW STOCK' : 'IN STOCK' }}
									</span>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Grid View -->
				<div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
					<div
						v-for="item in filteredItems"
						:key="item.code"
						class="premium-card !p-0 overflow-hidden group cursor-pointer"
					>
						<div class="aspect-square bg-gray-100 dark:bg-gray-800 relative">
							<div class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600">
								<svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
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
							<div class="text-xs font-bold text-gray-900 dark:text-white truncate mb-1">{{ item.name }}</div>
							<div class="flex items-center gap-1 mb-2">
								<span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400">{{ item.metal }}</span>
								<span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">{{ item.purity }}</span>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-sm font-bold text-gray-900 dark:text-white font-mono">{{ formatCurrency(item.price) }}</span>
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
import { useUIStore } from '@/stores/ui.js'
import { ref, computed } from 'vue'

const ui = useUIStore()
const viewMode = ref('table')

// Mock inventory data - jewelry themed
const inventoryData = ref([
	{ code: 'ZV-RG-001', name: 'Royal Solitaire Diamond Ring', metal: 'Yellow Gold', purity: '18K', weight: 4.2, stock: 3, price: 8500, category: 'Rings' },
	{ code: 'ZV-RG-002', name: 'Emerald Cut Platinum Band', metal: 'Platinum', purity: '950', weight: 6.8, stock: 1, price: 12400, category: 'Rings' },
	{ code: 'ZV-NK-001', name: 'Heritage Polki Necklace Set', metal: 'Yellow Gold', purity: '22K', weight: 48.5, stock: 2, price: 24800, category: 'Necklaces' },
	{ code: 'ZV-NK-002', name: 'Riviera Diamond Tennis Necklace', metal: 'White Gold', purity: '18K', weight: 22.3, stock: 0, price: 18500, category: 'Necklaces' },
	{ code: 'ZV-BR-001', name: 'Kundan Bridal Bangle Set (4pc)', metal: 'Yellow Gold', purity: '22K', weight: 65.0, stock: 4, price: 32000, category: 'Bangles' },
	{ code: 'ZV-ER-001', name: 'Ruby Halo Drop Earrings', metal: 'Rose Gold', purity: '18K', weight: 5.6, stock: 7, price: 4200, category: 'Earrings' },
	{ code: 'ZV-ER-002', name: 'Diamond Studs - Round Brilliant', metal: 'White Gold', purity: '14K', weight: 2.1, stock: 12, price: 3800, category: 'Earrings' },
	{ code: 'ZV-PD-001', name: 'Sapphire Pendant with Chain', metal: 'Yellow Gold', purity: '18K', weight: 8.4, stock: 0, price: 6200, category: 'Pendants' },
	{ code: 'ZV-CH-001', name: 'Cuban Link Chain 24"', metal: 'Yellow Gold', purity: '14K', weight: 32.0, stock: 6, price: 9800, category: 'Chains' },
	{ code: 'ZV-BR-002', name: 'Diamond Tennis Bracelet', metal: 'White Gold', purity: '18K', weight: 12.5, stock: 2, price: 14200, category: 'Bracelets' },
	{ code: 'ZV-RG-003', name: 'Vintage Art Deco Ring', metal: 'Platinum', purity: '950', weight: 5.3, stock: 1, price: 9800, category: 'Rings' },
	{ code: 'ZV-BS-001', name: 'Maharani Bridal Set', metal: 'Yellow Gold', purity: '22K', weight: 120.0, stock: 1, price: 58000, category: 'Bridal Sets' },
	{ code: 'ZV-SV-001', name: 'Sterling Silver Charm Bracelet', metal: 'Silver', purity: '925 Sterling', weight: 18.0, stock: 15, price: 450, category: 'Bracelets' },
	{ code: 'ZV-NK-003', name: 'Rose Gold Choker Necklace', metal: 'Rose Gold', purity: '18K', weight: 15.2, stock: 3, price: 7200, category: 'Necklaces' },
	{ code: 'ZV-ER-003', name: 'Emerald Chandelier Earrings', metal: 'Yellow Gold', purity: '18K', weight: 9.8, stock: 0, price: 11500, category: 'Earrings' },
])

const totalValue = computed(() => inventoryData.value.reduce((sum, i) => sum + i.price * Math.max(i.stock, 0), 0))
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
		items = items.filter((i) => i.name.toLowerCase().includes(q) || i.code.toLowerCase().includes(q))
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
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
}
</script>
})

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val)
}
</script>
