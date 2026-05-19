<template>
	<AppLayout>
		<div
			v-if="!session.currentWarehouse"
			class="min-h-[50vh] flex flex-col items-center justify-center text-center opacity-50"
		>
			<div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
				<svg
					class="w-8 h-8 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
					></path>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
					></path>
				</svg>
			</div>
			<h3 class="premium-title !text-xl mb-2">Select Store Location</h3>
			<p class="premium-subtitle">Choose a location from the top menu to view inventory.</p>
		</div>

		<div v-else class="flex flex-col">
			<div
				class="flex items-center justify-between gap-4 mb-6 flex-shrink-0"
			>
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">
						{{ viewMode === 'catalog' ? 'Catalogue' : 'Collection' }}
					</h2>

					<router-link
						v-if="posSession.hasActiveSession"
						to="/closing"
						class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/30 hover:bg-green-500/20 transition"
					>
						<span class="relative flex h-1.5 w-1.5"
							><span
								class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"
							></span
							><span
								class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"
							></span
						></span>
						Session Open
					</router-link>
					<router-link
						v-else
						to="/opening"
						class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-500/10 text-red-500 border border-red-500/30 hover:bg-red-500/20 transition"
					>
						<span class="relative flex h-1.5 w-1.5"
							><span
								class="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500"
							></span
						></span>
						No Register Session
					</router-link>

					<div
						v-if="ui.activeFilters.pos?.display_case"
						class="flex items-center gap-1.5 px-3 py-1 bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30 rounded-full text-[10px] font-bold animate-in fade-in slide-in-from-left-2"
					>
						<svg
							class="w-3 h-3"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
						</svg>
						Case-Based View
					</div>
				</div>

				<!-- Cash In/Out - only when session is active -->
				<button
					v-if="posSession.hasActiveSession"
					@click="showCashModal = true"
					class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition"
				>
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
					</svg>
					Cash In/Out
				</button>

				<!-- Inline Filter Bar -->
				<div class="flex-1 hidden md:flex justify-center px-4">
					<ItemFilterBar context="pos" />
				</div>

			</div>

			<!-- Cash In/Out Modal -->
			<CashMovementModal
				v-if="showCashModal"
				:session-name="posSession.sessionName"
				@close="showCashModal = false"
				@recorded="onCashMovementSaved"
			/>

			<div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
				<!-- POS View -->
				<div v-if="viewMode === 'pos'">
					<div v-if="items.loading && start === 0" class="py-20 text-center">
						<div
							class="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 dark:border-white border-t-transparent mx-auto mb-4"
						></div>
						<span class="text-gray-400 text-sm font-medium"
							>Curating Collection...</span
						>
					</div>

					<div
						v-else-if="catalog.length === 0"
						class="py-20 text-center premium-card !bg-transparent !border-dashed !border-gray-200 dark:!border-white/10"
					>
						<p class="premium-subtitle">No pieces found matching your criteria.</p>
					</div>

					<div v-else class="smart-grid">
						<div v-for="item in catalog" :key="item.item_code" class="group">
							<ItemCard
								:item="item"
								@quick-add="handleQuickAdd"
								@open-details="openItemDetails"
							/>
						</div>
					</div>

					<div
						v-if="hasMore && catalog.length > 0"
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

				<!-- Catalogue View -->
				<div v-else>
					<div v-if="catalogLoading" class="py-20 text-center">
						<div
							class="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 dark:border-white border-t-transparent mx-auto mb-4"
						></div>
						<span class="text-gray-400 text-sm font-medium">Loading catalogue...</span>
					</div>

					<div v-else-if="categories.length === 0" class="py-20 text-center">
						<p class="text-gray-400 text-sm">No categories found.</p>
					</div>

					<div v-else class="space-y-8">
						<div v-for="cat in categories" :key="cat.name" class="mb-6">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-lg font-bold text-gray-900 dark:text-white">
									{{ cat.name }}
								</h3>
								<button
									@click="viewCategory(cat)"
									class="text-sm text-[#D4AF37] hover:underline font-medium"
								>
									View All
								</button>
							</div>
							<div class="smart-grid">
								<div v-for="item in cat.items" :key="item.item_code" class="group">
									<ItemCard
										:item="item"
										@quick-add="handleQuickAdd"
										@open-details="openItemDetails(item.item_code)"
									/>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Product Modal - Only on desktop (lg+) -->
		<ProductModal :show="showModal" :itemCode="selectedItemCode" @close="showModal = false" />
	</AppLayout>
</template>

<script setup>
/**
 * POS Page Component
 *
 * Main Point of Sale page displaying item catalog with filtering and search.
 * Refactored for mobile-first with 1-tap quick add.
 */

import AppLayout from '@/components/AppLayout.vue'
import ItemFilterBar from '@/components/ItemFilterBar.vue'
import ItemCard from '@/components/ItemCard.vue'
import ProductModal from '@/components/POSProductModal.vue'
import CashMovementModal from '@/components/CashMovementModal.vue'
import { useSessionStore } from '@/stores/session.js'
import { useUIStore } from '@/stores/ui.js'
import { useCartStore } from '@/stores/cart.js'
import { usePosSessionStore } from '@/stores/posSession.js'
import { useBreakpoint } from '@/composables/useBreakpoint.js'
import { createResource } from 'frappe-ui'
import { watch, ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const session = useSessionStore()
const ui = useUIStore()
const cart = useCartStore()
const posSession = usePosSessionStore()
const { isMobile: isMobileBP, productGridCols } = useBreakpoint()

// View mode toggle
const viewMode = ref('pos')
const categories = ref([])
const catalogLoading = ref(false)

// Modal State - only used on desktop
const showModal = ref(false)
const selectedItemCode = ref(null)
const showCashModal = ref(false)

// Detect mobile/tablet viewport via shared composable
const isMobile = computed(() => isMobileBP.value)

// Data State
const catalog = ref([])
const start = ref(0)
const PAGE_LENGTH = 20
const hasMore = ref(true)
const filteredItems = computed(() => {
	let items = [...(catalog.value || [])]
	const filters = ui.activeFilters.pos || {}
	return items
})

// Fetch Items Resource
const items = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		const f = ui.activeFilters.pos || {}
		const {
			in_stock_only,
			out_of_stock_only,
			price_min,
			price_max,
			custom_jewelry_type,
			custom_metal_type,
			custom_purity,
			custom_gemstone,
			display_case,
			...otherFilters
		} = f

		const params = {
			warehouse: session.currentWarehouse,
			display_case: display_case || undefined,
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
			sort_by: ui.sortBy.pos || undefined,
		}

		console.log('🔍 POS Items API Params:', params)
		console.log('🎯 Active Filters:', ui.activeFilters)

		return params
	},
	onSuccess(data) {
		console.log('✅ POS Items API Response:', data.length, 'items')
		if (data.length < PAGE_LENGTH) {
			hasMore.value = false
		}
		if (start.value === 0) {
			catalog.value = data
		} else {
			catalog.value.push(...data)
		}
	},
	onError(error) {
		console.error('❌ POS Items API Error:', error)
	},
})

// Fetch Catalogue Resource
const catalogResource = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		return { page_length: 100, warehouse: session.currentWarehouse }
	},
	onSuccess(data) {
		const items = data.items || data || []
		const grouped = {}
		items.forEach((item) => {
			const cat = item.item_group || item.category || 'Other'
			if (!grouped[cat]) {
				grouped[cat] = { name: cat, items: [] }
			}
			if (grouped[cat].items.length < 8) {
				grouped[cat].items.push(item)
			}
		})
		categories.value = Object.values(grouped).slice(0, 6)
		catalogLoading.value = false
	},
})

function loadCatalog() {
	catalogLoading.value = true
	catalogResource.fetch()
}

function showCatalogView() {
	viewMode.value = 'catalog'
	loadCatalog()
}

// Actions
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

function onCashMovementSaved() {
	showCashModal.value = false
	posSession.fetchStatus()
}

function viewCategory(cat) {
	router.push(`/pos-catalogue/${encodeURIComponent(cat.name)}`)
}

// Watchers
let searchTimeout = null

watch(
	() => ({
		search: ui.searchQuery,
		filters: JSON.stringify(ui.activeFilters.pos),
		sort: ui.sortBy.pos,
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
			items.fetch()
		} else {
			catalog.value = []
		}
	},
	{ immediate: true }
)

let sessionPollInterval = null
onMounted(() => {
	posSession.fetchStatus()
	sessionPollInterval = setInterval(() => posSession.fetchStatus(), 60000)
})
onUnmounted(() => {
	if (sessionPollInterval) clearInterval(sessionPollInterval)
})
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
