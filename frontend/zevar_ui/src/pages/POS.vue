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

					<!-- Online/Offline Indicator -->
					<OfflineIndicator />

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

				<!-- Held Carts Button -->
				<button
					v-if="posSession.hasActiveSession"
					@click="toggleHeldCarts"
					class="flex items-center gap-1 px-3 py-1.5 text-xs font-bold rounded-lg border transition-all"
					:class="heldCarts.length > 0
						? 'text-amber-600 border-amber-300 bg-amber-50 dark:bg-amber-900/20 dark:border-amber-700/50 dark:text-amber-400'
						: 'text-gray-500 border-gray-200 dark:border-warm-border dark:text-gray-400 hover:border-gray-300'"
				>
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					Held
					<span v-if="heldCarts.length > 0" class="ml-0.5 w-5 h-5 flex items-center justify-center rounded-full bg-amber-500 text-white text-[10px] font-black">
						{{ heldCarts.length }}
					</span>
				</button>

				<!-- Held Carts Dropdown -->
				<Teleport to="body">
					<Transition name="fade">
						<div v-if="showHeldDrawer" class="fixed inset-0 z-[100] flex items-start justify-center pt-20">
							<div @click="showHeldDrawer = false" class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm"></div>
							<div class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-md border dark:border-warm-border overflow-hidden">
								<div class="p-4 border-b border-gray-100 dark:border-warm-border/50 flex items-center justify-between">
									<h3 class="text-sm font-bold text-gray-900 dark:text-white">Held Carts ({{ heldCarts.length }})</h3>
									<button @click="showHeldDrawer = false" class="p-1 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full">
										<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
										</svg>
									</button>
								</div>
								<div v-if="heldCarts.length === 0" class="p-8 text-center text-gray-400 text-sm">
									No held carts
								</div>
								<div v-else class="max-h-80 overflow-y-auto">
									<div
										v-for="hc in heldCarts"
										:key="hc.id"
										class="p-4 border-b border-gray-50 dark:border-warm-border/30 hover:bg-gray-50 dark:hover:bg-white/5 transition"
									>
										<div class="flex items-center justify-between">
											<div class="min-w-0 flex-1">
												<div class="font-bold text-sm text-gray-900 dark:text-white truncate">
													{{ hc.note || hc.customer_name || 'Unnamed cart' }}
												</div>
												<div class="text-xs text-gray-400 mt-0.5">
													{{ hc.item_count }} item{{ hc.item_count !== 1 ? 's' : '' }} · ${{ Number(hc.total || 0).toFixed(2) }}
												</div>
											</div>
											<div class="flex items-center gap-2 ml-3">
												<button
													@click="recallHeldCart(hc.id)"
													class="px-3 py-1.5 text-xs font-bold bg-[#D4AF37] text-black rounded-lg hover:bg-[#b5952f] transition"
												>
													Recall
												</button>
												<button
													@click="discardHeldCart(hc.id)"
													class="px-2 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
												>
													Discard
												</button>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</Transition>
				</Teleport>

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
import OfflineIndicator from '@/components/OfflineIndicator.vue'
import { useSessionStore } from '@/stores/session.js'
import { useUIStore } from '@/stores/ui.js'
import { useCartStore } from '@/stores/cart.js'
import { usePosSessionStore } from '@/stores/posSession.js'
import { useOfflineStore } from '@/stores/offline.js'
import { useBreakpoint } from '@/composables/useBreakpoint.js'
import { createResource } from 'frappe-ui'
import { watch, ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const session = useSessionStore()
const ui = useUIStore()
const cart = useCartStore()
const posSession = usePosSessionStore()
const offlineStore = useOfflineStore()
const { isMobile: isMobileBP, productGridCols } = useBreakpoint()

// View mode toggle
const viewMode = ref('pos')
const categories = ref([])
const catalogLoading = ref(false)

// Modal State - only used on desktop
const showModal = ref(false)
const selectedItemCode = ref(null)
const showCashModal = ref(false)
const showHeldDrawer = ref(false)
const heldCarts = ref([])

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
			// Cache catalog for offline browsing
			offlineStore.updateCatalogCache(data).catch(() => {})
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

// ── Held Carts ──
async function fetchHeldCarts() {
	try {
		const res = await fetch('/api/method/zevar_core.api.pos.get_held_carts', {
			method: 'GET',
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		const data = await res.json()
		heldCarts.value = data.message?.carts || []
	} catch (e) {
		heldCarts.value = []
	}
}

function toggleHeldCarts() {
	fetchHeldCarts()
	showHeldDrawer.value = !showHeldDrawer.value
}

async function recallHeldCart(cartId) {
	try {
		const res = await fetch('/api/method/zevar_core.api.pos.recall_cart', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({ cart_id: cartId }),
		})
		const data = await res.json()
		if (data.message?.success) {
			const recalledCart = data.message.cart
			// Clear current cart and restore held items
			cart.clearCart()
			cart.clearCustomer()
			for (const item of (recalledCart.items || [])) {
				cart.addItem(item)
			}
			if (recalledCart.customer) {
				cart.setCustomer({
					name: recalledCart.customer,
					customer_name: recalledCart.customer_name,
				})
			}
			showHeldDrawer.value = false
			fetchHeldCarts()
		}
	} catch (e) {
		console.error('Recall failed:', e)
	}
}

async function discardHeldCart(cartId) {
	try {
		await fetch('/api/method/zevar_core.api.pos.discard_held_cart', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({ cart_id: cartId }),
		})
		fetchHeldCarts()
	} catch (e) {
		console.error('Discard failed:', e)
	}
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

// Debounced catalog refresh for stock updates from other terminals
let stockRefreshTimeout = null
function handleStockUpdate(data) {
	// Only refresh if the update affects our warehouse or is a broadcast
	if (data?.warehouse && session.currentWarehouse && data.warehouse !== session.currentWarehouse) {
		return
	}
	// Debounce: wait 2s to batch rapid-fire updates
	if (stockRefreshTimeout) clearTimeout(stockRefreshTimeout)
	stockRefreshTimeout = setTimeout(() => {
		start.value = 0
		hasMore.value = true
		items.fetch()
	}, 2000)
}

onMounted(() => {
	posSession.fetchStatus()
	sessionPollInterval = setInterval(() => posSession.fetchStatus(), 60000)
	fetchHeldCarts() // Load held carts count on mount
	offlineStore.init() // Start online/offline event listeners

	// Listen for real-time stock updates from other POS terminals
	if (window.frappe?.realtime) {
		window.frappe.realtime.on('stock_update', handleStockUpdate)
	} else if (window.frappe?.socketio) {
		window.frappe.socketio.socket?.on('stock_update', handleStockUpdate)
	}

	// Listen for service worker sync completion to refresh pending count
	if ('serviceWorker' in navigator) {
		navigator.serviceWorker.addEventListener('message', (event) => {
			if (event.data?.type === 'SYNC_COMPLETE') {
				offlineStore.refreshPendingCount()
			}
		})
	}
})
onUnmounted(() => {
	if (sessionPollInterval) clearInterval(sessionPollInterval)
	if (stockRefreshTimeout) clearTimeout(stockRefreshTimeout)
	offlineStore.destroy() // Remove online/offline listeners

	// Clean up realtime listener
	if (window.frappe?.realtime) {
		window.frappe.realtime.off('stock_update', handleStockUpdate)
	} else if (window.frappe?.socketio) {
		window.frappe.socketio.socket?.off('stock_update', handleStockUpdate)
	}
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
