<template>
	<div class="relative">
		<div
			class="flex items-center gap-4 overflow-x-auto no-scrollbar transition-colors duration-300"
		>
			<div
				class="flex items-center gap-2 pr-4 border-r border-gray-200 dark:border-warm-border flex-shrink-0"
			>
				<svg
					class="w-4 h-4 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
					/>
				</svg>
				<span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest"
					>Filters</span
				>
				<span
					v-if="ui.activeFilterCount > 0"
					class="flex items-center justify-center bg-[#D4AF37] text-white text-[9px] font-bold rounded-full h-4 min-w-[16px] px-1"
				>
					{{ ui.activeFilterCount }}
				</span>
			</div>

			<!-- Filter Group: Price -->
			<div ref="priceDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('price')"
					:class="
						hasActivePrice
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Price
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'price' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>

			<!-- Filter Group: Category -->
			<div ref="categoryDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('category')"
					:class="
						ui.activeFilters.custom_jewelry_type
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Category
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'category' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>

			<!-- Filter Group: Metal -->
			<div ref="metalDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('metal')"
					:class="
						ui.activeFilters.custom_metal_type
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Metal
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'metal' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>

			<!-- Filter Group: Gemstone -->
			<div ref="gemstoneDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('gemstone')"
					:class="
						ui.activeFilters.custom_gemstone
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					Gemstone
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'gemstone' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>

			<!-- Sort -->
			<div
				ref="sortDropdownRef"
				class="relative flex-shrink-0 border-l border-gray-200 dark:border-warm-border pl-4 ml-auto"
			>
				<button
					@click.stop="toggleDropdown('sort')"
					:class="ui.sortBy ? 'text-[#D4AF37]' : 'text-gray-500'"
					class="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest transition-colors"
				>
					Sort
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'sort' }"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M19 9l-7 7-7-7"
						/>
					</svg>
				</button>
			</div>

			<!-- Reset All -->
			<button
				v-if="ui.activeFilterCount > 0"
				@click="ui.resetFilters()"
				class="text-[10px] font-black uppercase tracking-widest text-red-500 hover:text-red-600 transition-colors whitespace-nowrap"
			>
				Reset
			</button>
		</div>
	</div>

	<!-- Teleported Dropdowns - escape overflow-hidden parents -->
	<Teleport to="body">
		<!-- Price Dropdown -->
		<div
			v-if="openDropdown === 'price'"
			ref="priceDropdown"
			class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-4 z-[99999] text-gray-700 dark:text-white"
			:style="dropdownStyle.price"
		>
			<div class="flex gap-2 items-center mb-3">
				<div class="flex-1 relative">
					<span
						class="absolute left-2 top-1/2 -translate-y-1/2 text-gray-400 text-[10px] font-bold"
						>$</span
					>
					<input
						type="number"
						:value="ui.activeFilters.price_min ?? ''"
						@input="updatePriceFilter('price_min', $event.target.value)"
						@blur="finalizePriceFilter('price_min')"
						placeholder="Min"
						class="w-full bg-gray-50 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border/50 rounded-lg py-1.5 pl-5 pr-2 text-xs text-gray-700 dark:text-white outline-none focus:ring-1 focus:ring-[#D4AF37]"
					/>
				</div>
				<span class="text-gray-400 font-bold">–</span>
				<div class="flex-1 relative">
					<span
						class="absolute left-2 top-1/2 -translate-y-1/2 text-gray-400 text-[10px] font-bold"
						>$</span
					>
					<input
						type="number"
						:value="ui.activeFilters.price_max ?? ''"
						@input="updatePriceFilter('price_max', $event.target.value)"
						@blur="finalizePriceFilter('price_max')"
						placeholder="Max"
						class="w-full bg-gray-50 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border/50 rounded-lg py-1.5 pl-5 pr-2 text-xs text-gray-700 dark:text-white outline-none focus:ring-1 focus:ring-[#D4AF37]"
					/>
				</div>
			</div>
			<div class="flex flex-wrap gap-1">
				<button
					@click="clearPriceFilter"
					:class="
						!hasActivePrice
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-500 hover:bg-gray-100'
					"
					class="px-2 py-1 rounded text-[9px] font-bold transition-colors"
				>
					All Prices
				</button>
				<button
					v-for="preset in pricePresets"
					:key="preset.label"
					@click="togglePricePreset(preset)"
					:class="
						isPricePresetActive(preset)
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-500 hover:bg-gray-100'
					"
					class="px-2 py-1 rounded text-[9px] font-bold transition-colors"
				>
					{{ preset.label }}
				</button>
			</div>
		</div>

		<!-- Category Dropdown -->
		<div
			v-if="openDropdown === 'category'"
			ref="categoryDropdown"
			class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-3 z-[99999] grid grid-cols-2 gap-1.5 text-gray-700 dark:text-white"
			:style="dropdownStyle.category"
		>
			<button
				@click="toggleJewelryType('')"
				:class="
					!ui.activeFilters.custom_jewelry_type
						? 'bg-[#D4AF37] text-white font-bold'
						: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
				"
				class="px-3 py-2 text-[10px] rounded-lg text-left transition-colors"
			>
				All Categories
			</button>
			<button
				v-for="cat in categoryOptions"
				:key="cat"
				@click="toggleJewelryType(cat)"
				:class="
					ui.activeFilters.custom_jewelry_type === cat
						? 'bg-[#D4AF37] text-white font-bold'
						: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
				"
				class="px-3 py-2 text-[10px] rounded-lg text-left transition-colors"
			>
				{{ cat }}
			</button>
		</div>

		<!-- Metal Dropdown -->
		<div
			v-if="openDropdown === 'metal'"
			ref="metalDropdown"
			class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
			:style="dropdownStyle.metal"
		>
			<button
				@click="toggleMetal('')"
				:class="
					!ui.activeFilters.custom_metal_type
						? 'bg-[#D4AF37] text-white font-bold'
						: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
				"
				class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
			>
				All Metals
			</button>
			<button
				v-for="metal in Object.keys(metalPurityMap)"
				:key="metal"
				@click="toggleMetal(metal)"
				:class="
					ui.activeFilters.custom_metal_type === metal
						? 'bg-[#D4AF37] text-white font-bold'
						: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
				"
				class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
			>
				{{ metal }}
			</button>
		</div>

		<!-- Gemstone Dropdown -->
		<div
			v-if="openDropdown === 'gemstone'"
			ref="gemstoneDropdown"
			class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
			:style="dropdownStyle.gemstone"
		>
			<button
				@click="toggleGemstone('')"
				:class="
					!ui.activeFilters.custom_gemstone
						? 'bg-[#D4AF37] text-white font-bold'
						: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
				"
				class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
			>
				Any Stone
			</button>
			<button
				v-for="gem in gemstoneOptions"
				:key="gem"
				@click="toggleGemstone(gem)"
				:class="
					ui.activeFilters.custom_gemstone === gem
						? 'bg-[#D4AF37] text-white font-bold'
						: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
				"
				class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
			>
				{{ gem }}
			</button>
		</div>

		<!-- Sort Dropdown -->
		<div
			v-if="openDropdown === 'sort'"
			ref="sortDropdown"
			class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white"
			:style="dropdownStyle.sort"
		>
			<button
				v-for="opt in sortOptions"
				:key="opt.value"
				@click="toggleSort(opt.value)"
				:class="
					ui.sortBy === opt.value
						? 'bg-[#D4AF37] text-white font-bold'
						: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
				"
				class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
			>
				{{ opt.label }}
			</button>
		</div>
	</Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'
import { useUIStore } from '@/stores/ui'
import { createResource } from 'frappe-ui'

const ui = useUIStore()
const openDropdown = ref(null)

// Button refs
const priceDropdownRef = ref(null)
const categoryDropdownRef = ref(null)
const metalDropdownRef = ref(null)
const gemstoneDropdownRef = ref(null)
const sortDropdownRef = ref(null)

// Panel refs (teleported)
const priceDropdown = ref(null)
const categoryDropdown = ref(null)
const metalDropdown = ref(null)
const gemstoneDropdown = ref(null)
const sortDropdown = ref(null)

const dropdownStyle = ref({
	price: { display: 'none' },
	category: { display: 'none' },
	metal: { display: 'none' },
	gemstone: { display: 'none' },
	sort: { display: 'none' },
})

const categoryOptions = ref([
	'Rings',
	'Necklaces',
	'Bracelets',
	'Earrings',
	'Pendants',
	'Bangles',
	'Chains',
	'Bridal Sets',
])
const gemstoneOptions = ref([
	'Diamond',
	'Ruby',
	'Sapphire',
	'Emerald',
	'Polki',
	'Kundan',
	'No Stone',
])

function toggleDropdown(key) {
	console.log('🔘 Toggle dropdown:', key, 'Current:', openDropdown.value)
	if (openDropdown.value === key) {
		openDropdown.value = null
	} else {
		openDropdown.value = key
		nextTick(() => {
			updateDropdownPosition(key)
		})
	}
}

function updateDropdownPosition(key) {
	const refs = {
		price: { button: priceDropdownRef, panel: priceDropdown, width: 256 },
		category: { button: categoryDropdownRef, panel: categoryDropdown, width: 256 },
		metal: { button: metalDropdownRef, panel: metalDropdown, width: 192 },
		gemstone: { button: gemstoneDropdownRef, panel: gemstoneDropdown, width: 192 },
		sort: { button: sortDropdownRef, panel: sortDropdown, width: 192 },
	}

	const ref = refs[key]
	if (!ref || !ref.button.value || !ref.panel.value) {
		console.warn('Missing refs for:', key)
		return
	}

	const buttonRect = ref.button.value.getBoundingClientRect()

	dropdownStyle.value[key] = {
		top: `${buttonRect.bottom + 8}px`,
		left: `${buttonRect.left}px`,
		width: `${ref.width}px`,
		display: 'block',
	}

	console.log(`📍 Position ${key}:`, dropdownStyle.value[key])
}

function closeAllDropdowns() {
	console.log('❌ Closing all dropdowns')
	openDropdown.value = null
	Object.keys(dropdownStyle.value).forEach((key) => {
		dropdownStyle.value[key] = { display: 'none' }
	})
}

function handleGlobalClick(event) {
	const allRefs = [
		priceDropdownRef,
		categoryDropdownRef,
		metalDropdownRef,
		gemstoneDropdownRef,
		sortDropdownRef,
		priceDropdown,
		categoryDropdown,
		metalDropdown,
		gemstoneDropdown,
		sortDropdown,
	]

	const clickedInside = allRefs.some((ref) => {
		return ref.value && ref.value.contains(event.target)
	})

	if (!clickedInside) {
		closeAllDropdowns()
	}
}

function handleScroll() {
	if (openDropdown.value) {
		updateDropdownPosition(openDropdown.value)
	}
}

onMounted(() => {
	filtersResource.fetch()
	document.addEventListener('click', handleGlobalClick)
	window.addEventListener('scroll', handleScroll, true)
	window.addEventListener('resize', handleScroll)
})

onUnmounted(() => {
	document.removeEventListener('click', handleGlobalClick)
	window.removeEventListener('scroll', handleScroll, true)
	window.removeEventListener('resize', handleScroll)
})

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

const hasActivePrice = computed(
	() => ui.activeFilters.price_min != null || ui.activeFilters.price_max != null
)

const pricePresets = [
	{ label: '< $500', min: 0, max: 500 },
	{ label: '$500–$2K', min: 500, max: 2000 },
	{ label: '$2K–$5K', min: 2000, max: 5000 },
	{ label: '$5K–$15K', min: 5000, max: 15000 },
	{ label: '$15K+', min: 15000, max: null },
]

const metalPurityMap = {
	'Yellow Gold': ['24K', '22K', '18K', '14K', '10K'],
	'White Gold': ['18K', '14K'],
	'Rose Gold': ['18K', '14K'],
	Platinum: ['950'],
	Silver: ['999 Fine', '925 Sterling'],
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
	ui.setFilter(key, Number.isFinite(value) && value !== '' ? value : '')
}

function finalizePriceFilter(key) {
	const currentValue = ui.activeFilters[key]
	if (currentValue === '' || currentValue === 0) {
		ui.setFilter(key, null)
	}
}

function applyPricePreset(preset) {
	ui.setFilter('price_min', preset.min ?? '')
	ui.setFilter('price_max', preset.max ?? '')
	openDropdown.value = null
}

function togglePricePreset(preset) {
	// If clicking the same preset, clear the filter (toggle off)
	if (isPricePresetActive(preset)) {
		ui.setFilter('price_min', null)
		ui.setFilter('price_max', null)
	} else {
		ui.setFilter('price_min', preset.min ?? '')
		ui.setFilter('price_max', preset.max ?? '')
	}
	openDropdown.value = null
}

function clearPriceFilter() {
	ui.setFilter('price_min', null)
	ui.setFilter('price_max', null)
}

function isPricePresetActive(preset) {
	return (
		(ui.activeFilters.price_min ?? null) === (preset.min ?? null) &&
		(ui.activeFilters.price_max ?? null) === (preset.max ?? null)
	)
}

function selectJewelryType(value) {
	console.log('📂 Category:', value)
	ui.setFilter('custom_jewelry_type', value)
	openDropdown.value = null
}

function toggleJewelryType(value) {
	// Toggle: if same value selected, clear it; otherwise set it
	if (ui.activeFilters.custom_jewelry_type === value) {
		ui.setFilter('custom_jewelry_type', null)
	} else {
		ui.setFilter('custom_jewelry_type', value || null)
	}
	console.log('📂 Category toggle:', value, '→', ui.activeFilters.custom_jewelry_type)
	openDropdown.value = null
}

function updateMetal(val) {
	console.log('🔩 Metal:', val)
	ui.setFilter('custom_metal_type', val)
	ui.setFilter('custom_purity', '')
	openDropdown.value = null
}

function toggleMetal(val) {
	// Toggle: if same value selected, clear it; otherwise set it
	if (ui.activeFilters.custom_metal_type === val) {
		ui.setFilter('custom_metal_type', null)
		ui.setFilter('custom_purity', null)
	} else {
		ui.setFilter('custom_metal_type', val || null)
		ui.setFilter('custom_purity', null)
	}
	console.log('🔩 Metal toggle:', val, '→', ui.activeFilters.custom_metal_type)
	openDropdown.value = null
}

function updateGemstone(val) {
	console.log('💎 Gemstone:', val)
	ui.setFilter('custom_gemstone', val)
	openDropdown.value = null
}

function toggleGemstone(val) {
	// Toggle: if same value selected, clear it; otherwise set it
	if (ui.activeFilters.custom_gemstone === val) {
		ui.setFilter('custom_gemstone', null)
	} else {
		ui.setFilter('custom_gemstone', val || null)
	}
	console.log('💎 Gemstone toggle:', val, '→', ui.activeFilters.custom_gemstone)
	openDropdown.value = null
}

function selectSort(value) {
	console.log('📊 Sort:', value)
	ui.setSort(value)
	openDropdown.value = null
}

function toggleSort(value) {
	// Toggle: if same sort selected, clear it (reset to default); otherwise set it
	if (ui.sortBy === value) {
		ui.setSort('')
	} else {
		ui.setSort(value)
	}
	console.log('📊 Sort toggle:', value, '→', ui.sortBy)
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
</style>
