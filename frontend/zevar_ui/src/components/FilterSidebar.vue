<template>
	<div class="select-none px-2 py-4">
		<div class="flex items-center justify-between mb-6 px-1">
			<h3 class="text-[10px] font-bold text-[#555961] uppercase tracking-widest">Filters</h3>
			<button
				v-if="hasActiveFilters"
				@click="handleReset"
				class="text-[10px] text-[#D4AF37] hover:text-yellow-300 transition-colors"
			>
				Reset All
			</button>
		</div>

		<!-- Stock Status Filter -->
		<div class="mb-6 pb-5 border-b border-white/5">
			<label class="block text-[10px] font-bold text-gray-500 mb-3 px-1">Stock Status</label>
			<div class="flex flex-col gap-2">
				<button
					@click="updateStockFilter('all')"
					:class="
						currentStockFilter === 'all'
							? 'bg-[#D4AF37] text-[#0F1115] font-bold border-[#D4AF37]'
							: 'bg-[#1C1F26] text-gray-400 border-white/5 hover:border-gray-600 hover:text-white'
					"
					class="w-full px-3 py-2.5 text-[11px] rounded-lg border transition-all text-left shadow-sm flex items-center gap-2"
				>
					<svg
						class="w-4 h-4 flex-shrink-0"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
						/>
					</svg>
					All Items
				</button>

				<button
					@click="updateStockFilter('in-stock')"
					:class="
						currentStockFilter === 'in-stock'
							? 'bg-emerald-600 text-white font-bold border-emerald-600'
							: 'bg-[#1C1F26] text-gray-400 border-white/5 hover:border-emerald-600 hover:text-emerald-400'
					"
					class="w-full px-3 py-2.5 text-[11px] rounded-lg border transition-all text-left shadow-sm flex items-center gap-2"
				>
					<svg
						class="w-4 h-4 flex-shrink-0"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					In Stock Only
				</button>

				<button
					@click="updateStockFilter('out-of-stock')"
					:class="
						currentStockFilter === 'out-of-stock'
							? 'bg-red-600 text-white font-bold border-red-600'
							: 'bg-[#1C1F26] text-gray-400 border-white/5 hover:border-red-600 hover:text-red-400'
					"
					class="w-full px-3 py-2.5 text-[11px] rounded-lg border transition-all text-left shadow-sm flex items-center gap-2"
				>
					<svg
						class="w-4 h-4 flex-shrink-0"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
					Out of Stock
				</button>
			</div>
		</div>

		<div class="mb-6">
			<label class="block text-[10px] font-bold text-gray-500 mb-3 px-1">Metal</label>
			<div class="flex flex-wrap gap-2">
				<button
					@click="updateMetal('')"
					:class="
						!currentMetal
							? 'bg-[#D4AF37] text-[#0F1115] font-bold border-[#D4AF37]'
							: 'bg-[#1C1F26] text-gray-400 border-white/5 hover:border-gray-600 hover:text-white'
					"
					class="flex-1 min-w-[45%] px-3 py-2.5 text-[11px] rounded-lg border transition-all text-center shadow-sm"
				>
					All
				</button>

				<button
					v-for="metal in Object.keys(metalPurityMap)"
					:key="metal"
					@click="updateMetal(metal)"
					:class="
						currentMetal === metal
							? 'bg-[#D4AF37] text-[#0F1115] font-bold border-[#D4AF37]'
							: 'bg-[#1C1F26] text-gray-400 border-white/5 hover:border-gray-600 hover:text-white'
					"
					class="flex-1 min-w-[45%] px-3 py-2.5 text-[11px] rounded-lg border transition-all text-center shadow-sm"
				>
					{{ metal }}
				</button>
			</div>
		</div>

		<div class="mb-6">
			<label class="block text-[10px] font-bold text-gray-500 mb-3 px-1">Gemstone</label>
			<div class="flex flex-wrap gap-2">
				<button
					@click="updateGemstone('')"
					:class="
						!currentGemstone
							? 'bg-[#D4AF37] text-[#0F1115] font-bold border-[#D4AF37]'
							: 'bg-[#1C1F26] text-gray-400 border-white/5 hover:border-gray-600 hover:text-white'
					"
					class="flex-1 min-w-[45%] px-3 py-2.5 text-[11px] rounded-lg border transition-all text-center shadow-sm"
				>
					Any
				</button>

				<button
					v-for="gem in gemstoneOptions"
					:key="gem"
					@click="updateGemstone(gem)"
					:class="
						currentGemstone === gem
							? 'bg-[#D4AF37] text-[#0F1115] font-bold border-[#D4AF37]'
							: 'bg-[#1C1F26] text-gray-400 border-white/5 hover:border-gray-600 hover:text-white'
					"
					class="flex-1 min-w-[45%] px-3 py-2.5 text-[11px] rounded-lg border transition-all text-center shadow-sm"
				>
					{{ gem }}
				</button>
			</div>
		</div>

		<div class="mb-6">
			<label class="block text-[10px] font-bold text-gray-500 mb-2 px-1">Purity</label>
			<div class="relative">
				<select
					:value="ui.activeFilters.custom_purity || ''"
					@change="ui.setFilter('custom_purity', $event.target.value)"
					class="w-full bg-[#1C1F26] text-gray-300 text-xs border border-white/10 rounded-lg p-3 focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] outline-none cursor-pointer"
				>
					<option value="">
						{{ currentMetal ? `Any ${currentMetal} Purity` : 'Any Purity' }}
					</option>
					<option v-for="p in purityOptions" :key="p" :value="p">{{ p }}</option>
				</select>
			</div>
		</div>

		<!-- Low Stock Alert -->
		<div
			v-if="lowStockCount > 0"
			class="mt-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg"
		>
			<div class="flex items-start gap-3">
				<svg
					class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
					/>
				</svg>
				<div>
					<p class="text-amber-500 font-bold text-xs mb-1">Low Stock Alert</p>
					<p class="text-gray-400 text-[10px] leading-relaxed">
						{{ lowStockCount }} item{{ lowStockCount > 1 ? 's' : '' }} need{{
							lowStockCount === 1 ? 's' : ''
						}}
						restocking
					</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useUIStore } from '@/stores/ui'
import { createResource } from 'frappe-ui'

const ui = useUIStore()

// Data Options
const gemstoneOptions = ref([
	'Diamond',
	'Ruby',
	'Sapphire',
	'Emerald',
	'Polki',
	'Kundan',
	'No Stone',
])

const filtersResource = createResource({
	url: 'zevar_core.api.catalog.get_catalog_filters',
	onSuccess(data) {
		if (data && data.gemstones) {
			gemstoneOptions.value = data.gemstones
		}
	},
})

onMounted(() => {
	filtersResource.fetch()
})

const metalPurityMap = {
	'Yellow Gold': ['24K', '22K', '18K', '14K'],
	'White Gold': ['18K', '14K'],
	'Rose Gold': ['18K', '14K'],
	Platinum: ['950'],
	Silver: ['925 Sterling', '999 Fine'],
}

const lowStockCount = ref(0) // This would be fetched from API in production

// Helpers
const currentMetal = computed(() => ui.activeFilters.custom_metal_type || '')
const currentGemstone = computed(() => ui.activeFilters.custom_gemstone || '')
const currentStockFilter = computed(() => {
	if (ui.activeFilters.out_of_stock_only) {
		return 'out-of-stock'
	}

	if (ui.activeFilters.in_stock_only) {
		return 'in-stock'
	}

	return 'all'
})
const hasActiveFilters = computed(() => {
	const f = ui.activeFilters
	let count = 0

	// Check stock filters
	if (f.in_stock_only) count++
	if (f.out_of_stock_only) count++

	// Check custom filters
	if (f.custom_metal_type) count++
	if (f.custom_gemstone) count++
	if (f.custom_purity) count++
	if (f.custom_jewelry_type) count++
	if (f.price_min || f.price_max) count++

	return count > 0 || Boolean(ui.searchQuery)
})

// Smart Purity Logic
const purityOptions = computed(() => {
	if (currentMetal.value && metalPurityMap[currentMetal.value]) {
		return metalPurityMap[currentMetal.value]
	}
	return [...new Set(Object.values(metalPurityMap).flat())]
})

// Actions
function updateStockFilter(status) {
	if (status === 'in-stock') {
		ui.setFilter('in_stock_only', true)
		ui.setFilter('out_of_stock_only', false)
	} else if (status === 'out-of-stock') {
		ui.setFilter('out_of_stock_only', true)
		ui.setFilter('in_stock_only', false)
	} else {
		ui.setFilter('in_stock_only', false)
		ui.setFilter('out_of_stock_only', false)
	}
}

function updateMetal(val) {
	if (ui.activeFilters.custom_purity) {
		ui.setFilter('custom_purity', '')
	}
	ui.setFilter('custom_metal_type', val)
}

function updateGemstone(val) {
	ui.setFilter('custom_gemstone', val)
}

function handleReset() {
	ui.resetFilters()
}
</script>
