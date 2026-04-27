<template>
	<div class="h-full flex flex-col min-h-0">
		<div class="flex items-center justify-between gap-2 sm:gap-4 mb-4 sm:mb-8 flex-shrink-0">
			<div class="flex items-center gap-2 sm:gap-4">
				<button
					v-if="selectedCategory"
					@click="selectedCategory = null"
					class="p-2 rounded-lg bg-white/5 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border hover:bg-white/10 transition-all text-gray-600 dark:text-gray-400 hover:text-[#D4AF37]"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					</svg>
				</button>
				<h2 class="premium-title !text-xl sm:!text-2xl">
					{{ selectedCategory || 'Catalogues' }}
				</h2>
				<span
					class="status-label !mb-0 !bg-gray-100 dark:!bg-white/5 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-white/10"
				>
					{{
						selectedCategory
							? categoryItems.length + ' Items'
							: categories.length + ' Categories'
					}}
				</span>
			</div>
		</div>

		<div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
			<!-- Loading State -->
			<div v-if="items.loading && start === 0" class="py-20 text-center">
				<div
					class="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 dark:border-white border-t-transparent mx-auto mb-4"
				></div>
				<span class="text-gray-400 text-sm font-medium">Loading items...</span>
			</div>

			<!-- Empty State -->
			<div
				v-else-if="!selectedCategory && categories.length === 0"
				class="py-20 text-center premium-card !bg-transparent !border-dashed !border-gray-200 dark:!border-white/10"
			>
				<p class="premium-subtitle">No categories found.</p>
			</div>

			<div
				v-else-if="selectedCategory && categoryItems.length === 0"
				class="py-20 text-center premium-card !bg-transparent !border-dashed !border-gray-200 dark:!border-white/10"
			>
				<p class="premium-subtitle">No items found in this category.</p>
			</div>

			<!-- Category Grid View -->
			<div
				v-else-if="!selectedCategory"
				class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4"
			>
				<div
					v-for="cat in filteredCategories"
					:key="cat.name"
					@click="selectCategory(cat)"
					class="group cursor-pointer"
				>
					<div
						class="relative overflow-hidden rounded-xl bg-[#2a2a32] dark:bg-[#2a2a32] border border-white/5 dark:border-warm-border/50 hover:border-[#D4AF37]/40 transition-all duration-300 shadow-sm hover:shadow-lg aspect-square flex flex-col items-center justify-center p-4"
					>
						<div
							class="w-16 h-16 sm:w-20 sm:h-20 rounded-xl bg-white/5 flex items-center justify-center text-[#D4AF37] mb-3 group-hover:bg-[#D4AF37]/10 transition-colors"
						>
							<svg
								class="w-8 h-8 sm:w-10 sm:h-10"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									:d="getCategoryIcon(cat.name)"
								/>
							</svg>
						</div>
						<p
							class="text-sm font-bold text-gray-200 dark:text-white text-center group-hover:text-[#D4AF37] transition-colors"
						>
							{{ cat.name }}
						</p>
						<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
							{{ cat.count }} items
						</p>
					</div>
				</div>
			</div>

			<!-- Item Grid View (POS style) -->
			<div v-else>
				<div v-if="items.loading && start === 0" class="py-20 text-center">
					<div
						class="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 dark:border-white border-t-transparent mx-auto mb-4"
					></div>
					<span class="text-gray-400 text-sm font-medium">Loading items...</span>
				</div>

				<div v-else class="smart-grid">
					<div v-for="item in categoryItems" :key="item.item_code" class="group">
						<ItemCard
							:item="item"
							@quick-add="handleQuickAdd"
							@open-details="openItemDetails"
						/>
					</div>
				</div>

				<div
					v-if="hasMore && categoryItems.length > 0"
					class="flex justify-center pt-12 pb-12"
				>
					<button
						@click="loadMore"
						:disabled="items.loading"
						class="px-8 py-3 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border text-gray-900 dark:text-white rounded-full shadow-sm hover:shadow-md hover:border-gray-900 dark:hover:border-white transition-all text-sm font-bold uppercase tracking-wider disabled:opacity-50"
					>
						{{ items.loading ? 'Loading...' : 'Load More' }}
					</button>
				</div>
			</div>
		</div>
	</div>

	<ProductModal :show="showModal" :itemCode="selectedItemCode" @close="showModal = false" />
</template>

<script setup>
import ItemCard from '@/components/ItemCard.vue'
import ProductModal from '@/components/POSProductModal.vue'
import { useSessionStore } from '@/stores/session.js'
import { useUIStore } from '@/stores/ui.js'
import { useCartStore } from '@/stores/cart.js'
import { createResource } from 'frappe-ui'
import { watch, ref, computed } from 'vue'

const session = useSessionStore()
const ui = useUIStore()
const cart = useCartStore()

const selectedCategory = ref(null)
const categories = ref([])

const showModal = ref(false)
const selectedItemCode = ref(null)

const isMobile = computed(() => {
	if (typeof window === 'undefined') return false
	return window.innerWidth < 1024
})

const catalog = ref([])
const start = ref(0)
const PAGE_LENGTH = 20
const hasMore = ref(true)

const categoryItems = computed(() => {
	if (!selectedCategory.value) return []
	return catalog.value.filter(
		(item) => (item.item_group || item.category || 'Other') === selectedCategory.value
	)
})

const filteredCategories = computed(() => {
	const query = ui.searchQuery?.toLowerCase() || ''
	if (!query) return categories.value
	return categories.value.filter((cat) => cat.name.toLowerCase().includes(query))
})

// Fetch Items Resource
const items = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		const {
			in_stock_only,
			out_of_stock_only,
			price_min,
			price_max,
			custom_jewelry_type,
			custom_metal_type,
			custom_purity,
			custom_gemstone,
			...otherFilters
		} = ui.activeFilters

		return {
			warehouse: session.currentWarehouse,
			page_length: PAGE_LENGTH,
			start: start.value,
			search_term: ui.searchQuery || undefined,
			filters: JSON.stringify({
				custom_jewelry_type: custom_jewelry_type || undefined,
				custom_metal_type: custom_metal_type || undefined,
				custom_purity: custom_purity || undefined,
				custom_gemstone: custom_gemstone || undefined,
				...otherFilters,
			}),
			in_stock_only: in_stock_only || false,
			out_of_stock_only: out_of_stock_only || false,
			min_price: price_min || undefined,
			max_price: price_max || undefined,
			sort_by: ui.sortBy || undefined,
		}
	},
	onSuccess(data) {
		if (data.length < PAGE_LENGTH) {
			hasMore.value = false
		}
		if (start.value === 0) {
			catalog.value = data
			// Build categories from catalog
			const grouped = {}
			data.forEach((item) => {
				const cat = item.item_group || item.category || 'Other'
				if (!grouped[cat]) {
					grouped[cat] = { name: cat, items: [], count: 0 }
				}
				grouped[cat].count++
				if (grouped[cat].items.length < 8) {
					grouped[cat].items.push(item)
				}
			})
			categories.value = Object.values(grouped)
		} else {
			catalog.value.push(...data)
		}
	},
})

function selectCategory(cat) {
	selectedCategory.value = cat.name
}

function getCategoryIcon(categoryName) {
	// Return SVG path based on category
	return 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
}

function loadMore() {
	if (!hasMore.value || items.loading) return
	start.value += PAGE_LENGTH
	items.fetch()
}

function openItemDetails(itemCode) {
	if (isMobile.value) return
	selectedItemCode.value = itemCode
	showModal.value = true
}

function handleQuickAdd(item) {
	cart.addItem(item)
}

// Watchers
let searchTimeout = null

watch(
	() => ({
		search: ui.searchQuery,
		filters: JSON.stringify(ui.activeFilters),
		sort: ui.sortBy,
	}),
	() => {
		if (searchTimeout) clearTimeout(searchTimeout)
		searchTimeout = setTimeout(() => {
			start.value = 0
			hasMore.value = true
			items.fetch()
		}, 400)
	},
	{ deep: true }
)

watch(
	() => session.currentWarehouse,
	(newVal) => {
		if (newVal) {
			start.value = 0
			hasMore.value = true
			items.fetch()
		} else {
			catalog.value = []
			categories.value = []
			selectedCategory.value = null
		}
	},
	{ immediate: true }
)
</script>

<style scoped>
.smart-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 0.5rem;
}

@media (min-width: 640px) {
	.smart-grid {
		grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
		gap: 0.75rem;
	}
}

@media (min-width: 1024px) {
	.smart-grid {
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: 1rem;
	}
}
</style>
