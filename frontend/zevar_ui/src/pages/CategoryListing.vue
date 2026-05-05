<template>
	<div
		class="min-h-[100dvh]"
		:class="isDark ? 'bg-[#1e1e24] text-white' : 'bg-white text-gray-900'"
	>
		<Header
			v-if="!isEmbedded"
			:isDark="isDark"
			:activeCategory="categoryId"
			@toggleTheme="toggleTheme"
			@search="performSearch"
			@selectCategory="handleCategorySelect"
		/>

		<!-- Breadcrumb -->
		<div
			class="border-b"
			:class="isDark ? 'bg-[#111] border-white/5' : 'bg-gray-50 border-gray-200'"
		>
			<div class="max-w-7xl mx-auto px-6 py-3">
				<div
					class="flex items-center gap-2 text-sm"
					:class="isDark ? 'text-gray-400' : 'text-gray-600'"
				>
					<router-link to="/pos-catalogue" class="hover:text-[#C9A962]"
						>Home</router-link
					>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 5l7 7-7 7"
						/>
					</svg>
					<span
						class="font-medium capitalize"
						:class="isDark ? 'text-white' : 'text-gray-900'"
						>{{ categoryTitle }}</span
					>
				</div>
			</div>
		</div>

		<!-- Hero Banner -->
		<div
			class="relative h-60 overflow-hidden"
			:class="
				isDark
					? 'bg-gradient-to-br from-[#111] to-[#1a1a1a]'
					: 'bg-gradient-to-br from-[#faf5f0] to-[#e8ddd0]'
			"
		>
			<div class="absolute inset-0 opacity-10">
				<img :src="categoryBanner" class="w-full h-full object-cover" />
			</div>
			<div class="relative max-w-7xl mx-auto px-6 h-full flex flex-col justify-center">
				<h1 class="premium-title !text-4xl md:!text-5xl mb-2 capitalize">
					{{ categoryTitle }}
				</h1>
				<p class="text-lg font-light" :class="isDark ? 'text-gray-400' : 'text-gray-600'">
					{{ categoryDescription }}
				</p>
			</div>
		</div>

		<!-- Filters & Grid -->
		<div class="max-w-7xl mx-auto px-6 py-10">
			<div class="flex gap-8">
				<!-- Sidebar Filters -->
				<aside class="w-64 flex-shrink-0 hidden lg:block">
					<div class="sticky top-6 space-y-6">
						<!-- Price Range -->
						<div
							class="border-b pb-5"
							:class="isDark ? 'border-white/10' : 'border-gray-200'"
						>
							<h3
								class="font-bold mb-3"
								:class="isDark ? 'text-white' : 'text-gray-900'"
							>
								Price Range
							</h3>
							<div class="space-y-2">
								<label
									class="flex items-center gap-2 text-sm cursor-pointer"
									:class="isDark ? 'text-gray-300' : 'text-gray-700'"
								>
									<input
										type="radio"
										name="price"
										value="all"
										v-model="filters.priceRange"
										@change="applyFilters"
										class="text-[#8B6914]"
									/>
									<span>All Prices</span>
								</label>
								<label
									class="flex items-center gap-2 text-sm cursor-pointer"
									:class="isDark ? 'text-gray-300' : 'text-gray-700'"
								>
									<input
										type="radio"
										name="price"
										value="0-500"
										v-model="filters.priceRange"
										@change="applyFilters"
										class="text-[#8B6914]"
									/>
									<span>Under $500</span>
								</label>
								<label
									class="flex items-center gap-2 text-sm cursor-pointer"
									:class="isDark ? 'text-gray-300' : 'text-gray-700'"
								>
									<input
										type="radio"
										name="price"
										value="500-1000"
										v-model="filters.priceRange"
										@change="applyFilters"
										class="text-[#8B6914]"
									/>
									<span>$500 - $1,000</span>
								</label>
								<label
									class="flex items-center gap-2 text-sm cursor-pointer"
									:class="isDark ? 'text-gray-300' : 'text-gray-700'"
								>
									<input
										type="radio"
										name="price"
										value="1000-2500"
										v-model="filters.priceRange"
										@change="applyFilters"
										class="text-[#8B6914]"
									/>
									<span>$1,000 - $2,500</span>
								</label>
								<label
									class="flex items-center gap-2 text-sm cursor-pointer"
									:class="isDark ? 'text-gray-300' : 'text-gray-700'"
								>
									<input
										type="radio"
										name="price"
										value="2500+"
										v-model="filters.priceRange"
										@change="applyFilters"
										class="text-[#8B6914]"
									/>
									<span>$2,500+</span>
								</label>
							</div>
						</div>

						<!-- Metal Type -->
						<div
							class="border-b pb-5"
							:class="isDark ? 'border-white/10' : 'border-gray-200'"
						>
							<h3
								class="font-bold mb-3"
								:class="isDark ? 'text-white' : 'text-gray-900'"
							>
								Metal
							</h3>
							<div class="space-y-2">
								<label
									v-for="metal in availableMetals"
									:key="metal"
									class="flex items-center gap-2 text-sm cursor-pointer"
									:class="isDark ? 'text-gray-300' : 'text-gray-700'"
								>
									<input
										type="checkbox"
										:value="metal"
										v-model="filters.metals"
										@change="applyFilters"
										class="text-[#8B6914]"
									/>
									<span>{{ metal }}</span>
								</label>
							</div>
						</div>

						<!-- Purity -->
						<div
							class="border-b pb-5"
							:class="isDark ? 'border-white/10' : 'border-gray-200'"
						>
							<h3
								class="font-bold mb-3"
								:class="isDark ? 'text-white' : 'text-gray-900'"
							>
								Purity
							</h3>
							<div class="space-y-2">
								<label
									v-for="purity in availablePurities"
									:key="purity"
									class="flex items-center gap-2 text-sm cursor-pointer"
									:class="isDark ? 'text-gray-300' : 'text-gray-700'"
								>
									<input
										type="checkbox"
										:value="purity"
										v-model="filters.purities"
										@change="applyFilters"
										class="text-[#8B6914]"
									/>
									<span>{{ purity }}</span>
								</label>
							</div>
						</div>
					</div>
				</aside>

				<!-- Products Grid -->
				<main class="flex-1">
					<div class="flex items-center justify-between mb-6">
						<p :class="isDark ? 'text-gray-400' : 'text-gray-600'">
							{{ totalItems }} products
						</p>
						<select
							v-model="sortBy"
							@change="applyFilters"
							:class="
								isDark
									? 'px-4 py-2 border border-white/10 rounded-lg text-sm bg-[#1a1a1a] text-white focus:border-[#C9A962] focus:ring-1 focus:ring-[#C9A962]'
									: 'px-4 py-2 border border-gray-200 rounded-lg text-sm focus:border-[#8B6914] focus:ring-1 focus:ring-[#8B6914]'
							"
						>
							<option value="featured">Featured</option>
							<option value="price-asc">Price: Low to High</option>
							<option value="price-desc">Price: High to Low</option>
							<option value="newest">Newest First</option>
						</select>
					</div>

					<div
						v-if="loading"
						class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
					>
						<div v-for="i in 8" :key="i" class="animate-pulse">
							<div
								class="rounded-2xl aspect-square mb-3"
								:class="isDark ? 'bg-gray-800' : 'bg-gray-200'"
							></div>
							<div
								class="h-4 rounded mb-2"
								:class="isDark ? 'bg-gray-800' : 'bg-gray-200'"
							></div>
							<div
								class="h-4 w-2/3 rounded"
								:class="isDark ? 'bg-gray-800' : 'bg-gray-200'"
							></div>
						</div>
					</div>

					<div v-else-if="products.length === 0" class="text-center py-16">
						<svg
							class="w-16 h-16 mx-auto text-gray-300 mb-4"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
							/>
						</svg>
						<p :class="isDark ? 'text-gray-400' : 'text-gray-500'">
							No products found in this category
						</p>
					</div>

					<div
						v-else
						class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
					>
						<ProductCard
							v-for="product in products"
							:key="product.item_code"
							:product="product"
							@click="openProduct(product)"
						/>
					</div>
				</main>
			</div>
		</div>

		<ProductModal :show="showModal" :item-code="selectedItem" @close="closeModal" />
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import Header from '@/components/Header.vue'
import ProductCard from '@/components/CatalogProductCard.vue'
import ProductModal from '@/components/ProductModal.vue'

const route = useRoute()
const router = useRouter()

const props = defineProps({
	isEmbedded: {
		type: Boolean,
		default: false,
	},
})

// Check if embedded inside AppLayout
const isEmbedded = computed(() => props.isEmbedded || route.meta?.fullPage === true)

// Dark mode
import { useUIStore } from '@/stores/ui.js'
const uiStore = useUIStore()
const isDark = ref(uiStore.isDark)
function toggleTheme() {
	uiStore.toggleTheme()
	isDark.value = uiStore.isDark
}

const categoryId = computed(() => route.params.category?.toLowerCase() || 'all')
const categoryTitle = computed(() => route.params.category || 'All Jewelry')
const loading = ref(true)
const products = ref([])
const totalItems = ref(0)
const showModal = ref(false)
const selectedItem = ref(null)
const sortBy = ref('featured')

const filters = ref({
	priceRange: 'all',
	metals: [],
	purities: [],
})

const availableMetals = ref(['Yellow Gold', 'White Gold', 'Rose Gold', 'Platinum', 'Silver'])
const availablePurities = ref(['10K', '14K', '18K', '22K', '24K'])

const categoryBanner = computed(() => {
	const banners = {
		rings: 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=1200&q=80',
		earrings: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=1200&q=80',
		necklaces: 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=1200&q=80',
		chains: 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=1200&q=80',
		bracelets: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=1200&q=80',
		pendants: 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=1200&q=80',
		gold: 'https://images.unsplash.com/photo-1610375461246-83df859d849d?w=1200&q=80',
		diamond: 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=1200&q=80',
	}
	return (
		banners[categoryId.value] ||
		'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=1200&q=80'
	)
})

const categoryDescription = computed(() => {
	const desc = {
		rings: 'Discover our exquisite collection of engagement rings, wedding bands, and fashion rings',
		earrings: 'Elegant studs, hoops, and drop earrings for every occasion',
		necklaces: 'From delicate chains to statement pieces that capture attention',
		chains: 'Classic gold and diamond chains crafted to perfection',
		bracelets: 'Timeless bracelets and bangles to adorn your wrists',
		pendants: 'Beautiful pendants that tell your unique story',
		gold: 'Premium gold jewelry in various purities and designs',
		diamond: 'Brilliant diamonds set in exquisite designs',
	}
	return desc[categoryId.value] || 'Explore our premium jewelry collection'
})

// Build query filters based on category and user selections
function buildQueryFilters() {
	const queryFilters = {}
	const categoryMap = {
		rings: 'Rings',
		earrings: 'Earrings',
		necklaces: 'Necklaces',
		chains: 'Chains',
		bracelets: 'Bracelets',
		pendants: 'Pendants',
		gold: null,
		diamond: null,
	}
	const catKey = categoryId.value.toLowerCase()
	if (catKey === 'gold') {
		queryFilters.custom_metal_type = ['like', '%Gold%']
	} else if (catKey === 'diamond') {
		queryFilters.custom_product_type = ['like', '%Diamond%']
	} else if (categoryMap[catKey]) {
		queryFilters.custom_jewelry_type = categoryMap[catKey]
	}
	if (filters.value.metals.length > 0) {
		queryFilters.custom_metal_type = filters.value.metals
	}
	if (filters.value.purities.length > 0) {
		queryFilters.custom_purity = filters.value.purities
	}
	return queryFilters
}

const itemsResource = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		const queryFilters = buildQueryFilters()
		let minPrice = null
		let maxPrice = null
		const priceRange = filters.value.priceRange
		if (priceRange === '0-500') {
			maxPrice = 500
		} else if (priceRange === '500-1000') {
			minPrice = 500
			maxPrice = 1000
		} else if (priceRange === '1000-2500') {
			minPrice = 1000
			maxPrice = 2500
		} else if (priceRange === '2500+') {
			minPrice = 2500
		}

		const params = {
			start: 0,
			page_length: 100,
			filters: JSON.stringify(queryFilters),
		}
		if (minPrice) params.min_price = minPrice
		if (maxPrice) params.max_price = maxPrice
		return params
	},
	onSuccess(data) {
		products.value = data || []
		totalItems.value = data?.length || 0
		loading.value = false
	},
	onError(error) {
		console.error('Failed to load items:', error)
		loading.value = false
	},
})

function loadProducts() {
	loading.value = true
	itemsResource.fetch()
}

function applyFilters() {
	loadProducts()
}

function handleCategorySelect(cat) {
	router.push(`/pos-catalogue/${cat}`)
}

function openProduct(product) {
	selectedItem.value = product.item_code
	showModal.value = true
}

function closeModal() {
	showModal.value = false
	selectedItem.value = null
}

function performSearch(q) {
	// Add search logic if needed
}

watch(categoryId, () => {
	loadProducts()
})

onMounted(() => {
	loadProducts()
})
</script>
