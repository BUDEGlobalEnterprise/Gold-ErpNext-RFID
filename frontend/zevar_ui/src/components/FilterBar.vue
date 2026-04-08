<template>
	<div class="overflow-visible">
		<div
			class="flex items-center gap-4 overflow-x-auto overflow-y-visible no-scrollbar transition-colors duration-300"
		>
		<div class="flex items-center gap-2 pr-4 border-r border-gray-200 dark:border-white/10 flex-shrink-0">
			<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
			</svg>
			<span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Filters</span>
			<span v-if="ui.activeFilterCount > 0" class="flex items-center justify-center bg-[#D4AF37] text-white text-[9px] font-bold rounded-full h-4 min-w-[16px] px-1">
				{{ ui.activeFilterCount }}
			</span>
		</div>

		<!-- Filter Group: Price -->
		<div
			v-click-outside="() => closeDropdown('price')"
			class="relative flex-shrink-0"
		>
			<button
				@click.stop="toggleDropdown('price')"
					:class="hasActivePrice ? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50' : 'bg-gray-50 dark:bg-white/5 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20'"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
			>
				Price
				<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': openDropdown === 'price' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			<div
				v-if="openDropdown === 'price'"
				class="absolute top-full mt-2 left-0 w-64 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-white/10 rounded-xl shadow-2xl p-4 z-[100] text-gray-700 dark:text-white"
			>
				<div class="flex gap-2 items-center mb-3">
					<div class="flex-1 relative">
						<span class="absolute left-2 top-1/2 -translate-y-1/2 text-gray-400 text-[10px] font-bold">$</span>
						<input type="number" :value="ui.activeFilters.price_min ?? ''" @change="updatePriceFilter('price_min', $event.target.value)" placeholder="Min" class="w-full bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/5 rounded-lg py-1.5 pl-5 pr-2 text-xs text-gray-700 dark:text-white outline-none focus:ring-1 focus:ring-[#D4AF37]" />
					</div>
					<span class="text-gray-400 font-bold">–</span>
					<div class="flex-1 relative">
						<span class="absolute left-2 top-1/2 -translate-y-1/2 text-gray-400 text-[10px] font-bold">$</span>
						<input type="number" :value="ui.activeFilters.price_max ?? ''" @change="updatePriceFilter('price_max', $event.target.value)" placeholder="Max" class="w-full bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/5 rounded-lg py-1.5 pl-5 pr-2 text-xs text-gray-700 dark:text-white outline-none focus:ring-1 focus:ring-[#D4AF37]" />
					</div>
				</div>
				<div class="flex flex-wrap gap-1">
					<button v-for="preset in pricePresets" :key="preset.label" @click="applyPricePreset(preset)" 
							:class="isPricePresetActive(preset) ? 'bg-[#D4AF37] text-white' : 'bg-gray-50 dark:bg-white/5 text-gray-500 hover:bg-gray-100'"
							class="px-2 py-1 rounded text-[9px] font-bold transition-colors">
						{{ preset.label }}
					</button>
				</div>
			</div>
		</div>

		<!-- Filter Group: Category -->
		<div
			v-click-outside="() => closeDropdown('category')"
			class="relative flex-shrink-0"
		>
			<button @click.stop="toggleDropdown('category')" 
					:class="ui.activeFilters.custom_jewelry_type ? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50' : 'bg-gray-50 dark:bg-white/5 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20'"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all">
				Category
				<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': openDropdown === 'category' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			<div v-if="openDropdown === 'category'" 
				 class="absolute top-full mt-2 left-0 w-64 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-white/10 rounded-xl shadow-2xl p-3 z-[100] grid grid-cols-2 gap-1.5 text-gray-700 dark:text-white">
				<button @click="selectJewelryType('')" 
						:class="!ui.activeFilters.custom_jewelry_type ? 'bg-[#D4AF37] text-white font-bold' : 'hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-300'"
						class="px-3 py-2 text-[10px] rounded-lg text-left transition-colors">All Categories</button>
				<button v-for="cat in categoryOptions" :key="cat" @click="selectJewelryType(cat)" 
						:class="ui.activeFilters.custom_jewelry_type === cat ? 'bg-[#D4AF37] text-white font-bold' : 'hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-300'"
						class="px-3 py-2 text-[10px] rounded-lg text-left transition-colors">
					{{ cat }}
				</button>
			</div>
		</div>

		<!-- Filter Group: Metal -->
		<div
			v-click-outside="() => closeDropdown('metal')"
			class="relative flex-shrink-0"
		>
			<button @click.stop="toggleDropdown('metal')" 
					:class="ui.activeFilters.custom_metal_type ? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50' : 'bg-gray-50 dark:bg-white/5 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20'"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all">
				Metal
				<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': openDropdown === 'metal' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			<div v-if="openDropdown === 'metal'" 
				 class="absolute top-full mt-2 left-0 w-48 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-white/10 rounded-xl shadow-2xl p-2 z-[100] flex flex-col gap-1 text-gray-700 dark:text-white">
				<button @click="updateMetal('')" 
						:class="!ui.activeFilters.custom_metal_type ? 'bg-[#D4AF37] text-white font-bold' : 'hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-300'"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors">All Metals</button>
				<button v-for="metal in Object.keys(metalPurityMap)" :key="metal" @click="updateMetal(metal)" 
						:class="ui.activeFilters.custom_metal_type === metal ? 'bg-[#D4AF37] text-white font-bold' : 'hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-300'"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors">
					{{ metal }}
				</button>
			</div>
		</div>

		<!-- Filter Group: Gemstone -->
		<div
			v-click-outside="() => closeDropdown('gemstone')"
			class="relative flex-shrink-0"
		>
			<button @click.stop="toggleDropdown('gemstone')" 
					:class="ui.activeFilters.custom_gemstone ? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50' : 'bg-gray-50 dark:bg-white/5 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20'"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all">
				Gemstone
				<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': openDropdown === 'gemstone' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			<div v-if="openDropdown === 'gemstone'" 
				 class="absolute top-full mt-2 left-0 w-48 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-white/10 rounded-xl shadow-2xl p-2 z-[100] flex flex-col gap-1 text-gray-700 dark:text-white">
				<button @click="updateGemstone('')" 
						:class="!ui.activeFilters.custom_gemstone ? 'bg-[#D4AF37] text-white font-bold' : 'hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-300'"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors">Any Stone</button>
				<button v-for="gem in gemstoneOptions" :key="gem" @click="updateGemstone(gem)" 
						:class="ui.activeFilters.custom_gemstone === gem ? 'bg-[#D4AF37] text-white font-bold' : 'hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-300'"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors">
					{{ gem }}
				</button>
			</div>
		</div>

		<!-- Sort -->
		<div
			v-click-outside="() => closeDropdown('sort')"
			class="relative flex-shrink-0 border-l border-gray-200 dark:border-white/10 pl-4 ml-auto"
		>
			<button @click.stop="toggleDropdown('sort')" 
					:class="ui.sortBy ? 'text-[#D4AF37]' : 'text-gray-500'"
					class="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest transition-colors">
				Sort
				<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': openDropdown === 'sort' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
				</svg>
			</button>
			<div v-if="openDropdown === 'sort'" 
				 class="absolute top-full mt-2 right-0 w-48 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-white/10 rounded-xl shadow-2xl p-2 z-[100] flex flex-col gap-1 text-gray-700 dark:text-white">
				<button v-for="opt in sortOptions" :key="opt.value" @click="selectSort(opt.value)" 
						:class="ui.sortBy === opt.value ? 'bg-[#D4AF37] text-white font-bold' : 'hover:bg-gray-100 dark:hover:bg-white/5 text-gray-500 dark:text-gray-300'"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors">
					{{ opt.label }}
				</button>
			</div>
		</div>

		<!-- Reset All -->
		<button v-if="ui.activeFilterCount > 0" @click="ui.resetFilters()" 
				class="text-[10px] font-black uppercase tracking-widest text-red-500 hover:text-red-600 transition-colors whitespace-nowrap">
			Reset
		</button>
		</div>
	</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useUIStore } from '@/stores/ui'
import { createResource } from 'frappe-ui'

const ui = useUIStore()
const openDropdown = ref(null)
const categoryOptions = ref([
	'Rings', 'Necklaces', 'Bracelets', 'Earrings', 'Pendants', 'Bangles', 'Chains', 'Bridal Sets'
])
const gemstoneOptions = ref([
	'Diamond', 'Ruby', 'Sapphire', 'Emerald', 'Polki', 'Kundan', 'No Stone'
])

function toggleDropdown(key) {
	if (openDropdown.value === key) {
		openDropdown.value = null
	} else {
		openDropdown.value = key
	}
}

function closeDropdown(key) {
	if (openDropdown.value === key) {
		openDropdown.value = null
	}
}

const filtersResource = createResource({
	url: 'zevar_core.api.catalog.get_catalog_filters',
	onSuccess(data) {
		if (Array.isArray(data?.jewelry_types) && data.jewelry_types.length > 0) {
			categoryOptions.value = data.jewelry_types
		}

		if (Array.isArray(data?.gemstones) && data.gemstones.length > 0) {
			gemstoneOptions.value = data.gemstones
		}
	},
})

onMounted(() => {
	filtersResource.fetch()
})

// Click outside directive (simplified inline for this component context)
const vClickOutside = {
	mounted(el, binding) {
		el.clickOutsideEvent = function (event) {
			if (el === event.target || el.contains(event.target)) {
				return
			}

			binding.value(event)
		}
		window.setTimeout(() => {
			document.addEventListener('click', el.clickOutsideEvent)
		}, 0)
	},
	unmounted(el) {
		document.removeEventListener('click', el.clickOutsideEvent)
	}
}

const hasActivePrice = computed(() => ui.activeFilters.price_min != null || ui.activeFilters.price_max != null)

const pricePresets = [
	{ label: '< $500', min: 0, max: 500 },
	{ label: '$500–$2K', min: 500, max: 2000 },
	{ label: '$2K–$5K', min: 2000, max: 5000 },
	{ label: '$5K–$15K', min: 5000, max: 15000 },
	{ label: '$15K+', min: 15000, max: null },
]

const metalPurityMap = {
	'Yellow Gold': ['24K', '22K', '18K', '14K'],
	'White Gold': ['18K', '14K'],
	'Rose Gold': ['18K', '14K'],
	Platinum: ['950'],
	Silver: ['925 Sterling']
}

const sortOptions = [
	{ label: 'Default Order', value: '' },
	{ label: 'Price: Low → High', value: 'price_asc' },
	{ label: 'Price: High → Low', value: 'price_desc' },
	{ label: 'Weight: Light → Heavy', value: 'weight_asc' },
	{ label: 'Weight: Heavy → Light', value: 'weight_desc' },
	{ label: 'Newest First', value: 'newest' },
	{ label: 'Name: A → Z', value: 'name_asc' },
]

function updatePriceFilter(key, rawValue) {
	const value = rawValue === '' ? '' : Number(rawValue)
	ui.setFilter(key, Number.isFinite(value) ? value : '')
}

function applyPricePreset(preset) {
	ui.setFilter('price_min', preset.min ?? '')
	ui.setFilter('price_max', preset.max ?? '')
	openDropdown.value = null
}

function isPricePresetActive(preset) {
	return (ui.activeFilters.price_min ?? null) === (preset.min ?? null) &&
		   (ui.activeFilters.price_max ?? null) === (preset.max ?? null)
}

function selectJewelryType(value) {
	ui.setFilter('custom_jewelry_type', value)
	openDropdown.value = null
}

function updateMetal(val) {
	ui.setFilter('custom_metal_type', val)
	ui.setFilter('custom_purity', '')
	openDropdown.value = null
}

function updateGemstone(val) {
	ui.setFilter('custom_gemstone', val)
	openDropdown.value = null
}

function selectSort(value) {
	ui.setSort(value)
	openDropdown.value = null
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}

/* Tooltip/Dropdown arrow effect */
.absolute::after {
	content: '';
	position: absolute;
	top: -6px;
	left: 20px;
	width: 12px;
	height: 12px;
	background: inherit;
	border-left: 1px solid rgba(0,0,0,0.05);
	border-top: 1px solid rgba(0,0,0,0.05);
	transform: rotate(45deg);
}

.right-0::after {
	left: auto;
	right: 20px;
}
</style>
