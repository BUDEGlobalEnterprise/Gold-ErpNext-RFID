<template>
	<div class="h-full flex flex-col min-h-0">
		<div class="flex items-center gap-2 sm:gap-4 mb-4 sm:mb-8 flex-shrink-0">
			<h2 class="premium-title !text-xl sm:!text-2xl">Catalogue</h2>
			<span
				class="status-label !mb-0 !bg-gray-100 dark:!bg-white/5 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-white/10"
			>
				{{ categories.length }} Categories
			</span>
		</div>

		<div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
			<div v-if="loading" class="py-20 text-center">
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

		<ProductModal :show="showModal" :itemCode="selectedItemCode" @close="showModal = false" />
	</div>
</template>

<script setup>
import ItemCard from '@/components/ItemCard.vue'
import ProductModal from '@/components/POSProductModal.vue'
import { useCartStore } from '@/stores/cart.js'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const cart = useCartStore()
const categories = ref([])
const loading = ref(false)
const showModal = ref(false)
const selectedItemCode = ref(null)

const catalogResource = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		return { page_length: 50 }
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
		loading.value = false
	},
})

function loadCatalog() {
	loading.value = true
	catalogResource.fetch()
}

function handleQuickAdd(item) {
	cart.addItem(item)
}

function openItemDetails(itemCode) {
	selectedItemCode.value = itemCode
	showModal.value = true
}

function viewCategory(cat) {
	router.push(`/pos-catalogue/${encodeURIComponent(cat.name)}`)
}

defineExpose({ loadCatalog })
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
