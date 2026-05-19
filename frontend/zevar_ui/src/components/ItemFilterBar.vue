<template>
	<BaseFilterBar :context="context">
		<template #filters>
			<!-- Price -->
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

			<!-- Category -->
			<div ref="categoryDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('category')"
					:class="
						activeFilters.custom_jewelry_type
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

			<!-- Metal -->
			<div ref="metalDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('metal')"
					:class="
						activeFilters.custom_metal_type
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

			<!-- Gemstone -->
			<div ref="gemstoneDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('gemstone')"
					:class="
						activeFilters.custom_gemstone
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

			<!-- Display Case -->
			<div ref="displayCaseDropdownRef" class="relative flex-shrink-0">
				<button
					@click.stop="toggleDropdown('displayCase')"
					:class="
						activeFilters.display_case
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/50'
							: 'bg-gray-50 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-warm-border hover:border-gray-300 dark:hover:border-white/20'
					"
					class="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all"
				>
					<svg
						class="w-3 h-3"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
						<polyline points="9 22 9 12 15 12 15 22" />
					</svg>
					Case
					<svg
						class="w-3 h-3 transition-transform"
						:class="{ 'rotate-180': openDropdown === 'displayCase' }"
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
		</template>

		<template #sort>
			<div ref="sortDropdownRef" class="relative">
				<button
					@click.stop="toggleDropdown('sort')"
					:class="sortBy ? 'text-[#D4AF37]' : 'text-gray-500'"
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
		</template>

		<template #dropdowns>
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
								:value="activeFilters.price_min ?? ''"
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
								:value="activeFilters.price_max ?? ''"
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
							!activeFilters.custom_jewelry_type
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
							activeFilters.custom_jewelry_type === cat
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
							!activeFilters.custom_metal_type
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
							activeFilters.custom_metal_type === metal
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
							!activeFilters.custom_gemstone
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
							activeFilters.custom_gemstone === gem
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						{{ gem }}
					</button>
				</div>

				<!-- Display Case Dropdown -->
				<div
					v-if="openDropdown === 'displayCase'"
					ref="displayCaseDropdown"
					class="fixed bg-white dark:bg-warm-card border border-gray-200 dark:border-warm-border rounded-xl shadow-2xl p-2 z-[99999] flex flex-col gap-1 text-gray-700 dark:text-white max-h-[400px] overflow-y-auto"
					:style="dropdownStyle.displayCase"
				>
					<button
						@click="toggleDisplayCase('')"
						:class="
							!activeFilters.display_case
								? 'bg-[#D4AF37] text-white font-bold'
								: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
						"
						class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors"
					>
						All Cases
					</button>
					<template v-for="(cases, zone) in groupedDisplayCases" :key="zone">
						<div
							class="px-3 py-1.5 text-[9px] font-black uppercase tracking-widest text-gray-400 dark:text-gray-500 bg-gray-50/50 dark:bg-white/5 rounded-md mt-1 mb-0.5"
						>
							{{ zone }}
						</div>
						<button
							v-for="c in cases"
							:key="c.name"
							@click="toggleDisplayCase(c.name)"
							:class="
								activeFilters.display_case === c.name
									? 'bg-[#D4AF37] text-white font-bold'
									: 'hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-500 dark:text-gray-300'
							"
							class="px-3 py-2 text-[11px] rounded-lg text-left transition-colors flex items-center justify-between"
						>
							<div class="flex flex-col">
								<span class="font-bold">{{ c.case_code }}</span>
								<span class="text-[9px] opacity-70">{{ c.case_name }}</span>
							</div>
							<span
								v-if="c.item_count > 0"
								class="text-[9px] bg-gray-100 dark:bg-white/10 px-1.5 py-0.5 rounded-full"
							>
								{{ c.item_count }}
							</span>
						</button>
					</template>
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
							sortBy === opt.value
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
	</BaseFilterBar>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue'
import { useUIStore } from '@/stores/ui.js'
import { createResource } from 'frappe-ui'
import BaseFilterBar from './BaseFilterBar.vue'

const props = defineProps({
	context: {
		type: String,
		default: 'pos',
	},
})

const ui = useUIStore()
const openDropdown = ref(null)

const activeFilters = computed(() => ui.activeFilters[props.context] || {})
const sortBy = computed(() => ui.sortBy[props.context] || '')

// Button refs
const priceDropdownRef = ref(null)
const categoryDropdownRef = ref(null)
const metalDropdownRef = ref(null)
const gemstoneDropdownRef = ref(null)
const displayCaseDropdownRef = ref(null)
const sortDropdownRef = ref(null)

// Panel refs (teleported)
const priceDropdown = ref(null)
const categoryDropdown = ref(null)
const metalDropdown = ref(null)
const gemstoneDropdown = ref(null)
const displayCaseDropdown = ref(null)
const sortDropdown = ref(null)

const dropdownStyle = ref({
	price: { display: 'none' },
	category: { display: 'none' },
	metal: { display: 'none' },
	gemstone: { display: 'none' },
	displayCase: { display: 'none' },
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
const displayCaseOptions = ref([])

const groupedDisplayCases = computed(() => {
	const groups = {}
	displayCaseOptions.value.forEach((c) => {
		const zone = c.zone_type || 'Other'
		if (!groups[zone]) groups[zone] = []
		groups[zone].push(c)
	})
	return groups
})

function toggleDropdown(key) {
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
		displayCase: { button: displayCaseDropdownRef, panel: displayCaseDropdown, width: 220 },
		sort: { button: sortDropdownRef, panel: sortDropdown, width: 192 },
	}

	const ref = refs[key]
	if (!ref || !ref.button.value || !ref.panel.value) return

	const buttonRect = ref.button.value.getBoundingClientRect()

	dropdownStyle.value[key] = {
		top: `${buttonRect.bottom + 8}px`,
		left: `${buttonRect.left}px`,
		width: `${ref.width}px`,
		display: 'block',
	}
}

function closeAllDropdowns() {
	openDropdown.value = null
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
		displayCaseDropdown,
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
		if (Array.isArray(data?.display_cases)) {
			displayCaseOptions.value = data.display_cases
		}
	},
})

const hasActivePrice = computed(
	() => activeFilters.value.price_min != null || activeFilters.value.price_max != null
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
	ui.setFilter(props.context, key, Number.isFinite(value) && value !== '' ? value : '')
}

function finalizePriceFilter(key) {
	const currentValue = activeFilters.value[key]
	if (currentValue === '' || currentValue === 0) {
		ui.setFilter(props.context, key, null)
	}
}

function togglePricePreset(preset) {
	if (isPricePresetActive(preset)) {
		ui.setFilter(props.context, 'price_min', null)
		ui.setFilter(props.context, 'price_max', null)
	} else {
		ui.setFilter(props.context, 'price_min', preset.min ?? '')
		ui.setFilter(props.context, 'price_max', preset.max ?? '')
	}
	openDropdown.value = null
}

function clearPriceFilter() {
	ui.setFilter(props.context, 'price_min', null)
	ui.setFilter(props.context, 'price_max', null)
}

function isPricePresetActive(preset) {
	return (
		(activeFilters.value.price_min ?? null) === (preset.min ?? null) &&
		(activeFilters.value.price_max ?? null) === (preset.max ?? null)
	)
}

function toggleJewelryType(value) {
	if (activeFilters.value.custom_jewelry_type === value) {
		ui.setFilter(props.context, 'custom_jewelry_type', null)
	} else {
		ui.setFilter(props.context, 'custom_jewelry_type', value || null)
	}
	openDropdown.value = null
}

function toggleMetal(val) {
	if (activeFilters.value.custom_metal_type === val) {
		ui.setFilter(props.context, 'custom_metal_type', null)
		ui.setFilter(props.context, 'custom_purity', null)
	} else {
		ui.setFilter(props.context, 'custom_metal_type', val || null)
		ui.setFilter(props.context, 'custom_purity', null)
	}
	openDropdown.value = null
}

function toggleGemstone(val) {
	if (activeFilters.value.custom_gemstone === val) {
		ui.setFilter(props.context, 'custom_gemstone', null)
	} else {
		ui.setFilter(props.context, 'custom_gemstone', val || null)
	}
	openDropdown.value = null
}

function toggleSort(value) {
	if (sortBy.value === value) {
		ui.setSort(props.context, '')
	} else {
		ui.setSort(props.context, value)
	}
	openDropdown.value = null
}

function toggleDisplayCase(val) {
	if (activeFilters.value.display_case === val) {
		ui.setFilter(props.context, 'display_case', null)
	} else {
		ui.setFilter(props.context, 'display_case', val || null)
	}
	openDropdown.value = null
}
</script>
