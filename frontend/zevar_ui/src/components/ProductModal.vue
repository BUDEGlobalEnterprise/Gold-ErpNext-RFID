<template>
	<BaseModal :show="show" max-width="max-w-5xl" :no-max-height="true" @close="close">
		<div class="flex flex-col md:flex-row">
			<!-- Left: Image -->
			<div
				class="w-full md:w-5/12 bg-gray-50 flex items-center justify-center p-10 border-r relative"
			>
				<img
					v-if="details.image"
					:src="details.image"
					class="max-h-[55vh] object-contain drop-shadow-2xl transform hover:scale-105 transition-transform duration-500"
				/>
				<div v-else class="text-7xl opacity-30">&#x1F48E;</div>
			</div>

			<!-- Right: Details -->
			<div class="w-full md:w-7/12 p-8 overflow-y-auto bg-white">
				<div v-if="loading" class="h-full flex items-center justify-center">
					<div
						class="animate-spin rounded-full h-10 w-10 border-3 border-[#8B6914] border-t-transparent"
					></div>
				</div>

				<div v-else class="space-y-6">
					<!-- Title & SKU -->
					<div>
						<h2 class="text-2xl font-bold text-gray-900 leading-tight mb-1">
							{{ details.item_name }}
						</h2>
						<p class="text-sm text-gray-500 font-mono">{{ details.item_code }}</p>
					</div>

					<!-- Badges -->
					<div class="flex flex-wrap gap-2">
						<span
							v-if="details.metal"
							class="px-3 py-1.5 bg-[#FDF6E3] text-[#8B6914] rounded-md text-xs font-bold uppercase tracking-wider border border-[#E5D4A1]"
						>
							{{ details.metal }}
						</span>
						<span
							v-if="details.purity"
							class="px-3 py-1.5 bg-gray-100 text-gray-800 rounded-md text-xs font-bold uppercase tracking-wider border border-gray-200"
						>
							{{ details.purity }}
						</span>
					</div>

					<!-- Weight Section -->
					<div class="bg-gray-50 rounded-lg p-5 border border-gray-200">
						<div
							v-if="details.gross_weight"
							class="flex justify-between text-sm mb-2.5"
						>
							<span class="text-gray-600">Gross Weight</span>
							<span class="font-semibold text-gray-900"
								>{{ formatWeight(details.gross_weight) }} g</span
							>
						</div>
						<div
							v-if="details.stone_weight"
							class="flex justify-between text-sm mb-2.5 text-red-600"
						>
							<span>- Stone Weight</span>
							<span class="font-medium"
								>{{ formatWeight(details.stone_weight) }} g</span
							>
						</div>
						<div
							v-if="details.net_weight || calculatedNetWeight > 0"
							class="flex justify-between pt-3 border-t border-gray-300"
						>
							<span class="font-bold text-gray-800">Net Weight</span>
							<span class="font-bold text-[#8B6914] text-lg"
								>{{ formatWeight(calculatedNetWeight) }} g</span
							>
						</div>
					</div>

					<!-- Product Details Table -->
					<div class="border border-gray-200 rounded-lg overflow-hidden">
						<div class="bg-gray-100 px-4 py-2 border-b border-gray-200">
							<h3 class="font-bold text-gray-900 text-sm uppercase tracking-wide">
								Product Details
							</h3>
						</div>
						<div class="divide-y divide-gray-200">
							<div v-if="details.product_type" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Product Type</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.product_type
								}}</span>
							</div>
							<div v-if="details.jewelry_type" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Jewelry Type</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.jewelry_type
								}}</span>
							</div>
							<div v-if="details.jewelry_subtype" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Sub Type</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.jewelry_subtype
								}}</span>
							</div>
							<div v-if="details.material_color" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Material Color</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.material_color
								}}</span>
							</div>
							<div v-if="details.finish" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Finish</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.finish
								}}</span>
							</div>
							<div v-if="details.plating" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Plating</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.plating
								}}</span>
							</div>
							<div v-if="details.length" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Length of Item</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.length
								}}</span>
							</div>
							<div v-if="details.width" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Width of Item</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.width
								}}</span>
							</div>
							<div v-if="details.size" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Size</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.size
								}}</span>
							</div>
							<div v-if="details.chain_type" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Chain Type</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.chain_type
								}}</span>
							</div>
							<div v-if="details.clasp_type" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Clasp Type</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.clasp_type
								}}</span>
							</div>
							<div v-if="details.gender" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Gender</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.gender
								}}</span>
							</div>
							<div v-if="details.completeness" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Completeness</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.completeness
								}}</span>
							</div>
							<div v-if="details.country_of_origin" class="flex py-2.5 px-4">
								<span class="w-1/2 text-sm text-gray-600">Country of Origin</span>
								<span class="w-1/2 text-sm text-gray-900 font-medium">{{
									details.country_of_origin || 'USA'
								}}</span>
							</div>
						</div>
					</div>

					<!-- Gemstone Details -->
					<div
						v-if="details.gemstones && details.gemstones.length > 0"
						class="border border-gray-200 rounded-lg overflow-hidden"
					>
						<div class="bg-purple-50 px-4 py-2 border-b border-purple-100">
							<h3
								class="font-bold text-purple-900 text-sm uppercase tracking-wide flex items-center gap-2"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 3l8 5-8 13-8-13 8-5z"
									/>
								</svg>
								Gemstone Details
							</h3>
						</div>
						<div class="overflow-x-auto">
							<table class="w-full text-sm">
								<thead class="bg-gray-50 border-b border-gray-200">
									<tr class="text-xs text-gray-600 uppercase">
										<th class="px-4 py-2 text-left font-semibold">Stone</th>
										<th class="px-4 py-2 text-left font-semibold">Cut</th>
										<th class="px-4 py-2 text-left font-semibold">Color</th>
										<th class="px-4 py-2 text-left font-semibold">Clarity</th>
										<th class="px-4 py-2 text-right font-semibold">Carat</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-100">
									<tr
										v-for="(gem, i) in details.gemstones"
										:key="i"
										class="hover:bg-gray-50"
									>
										<td class="px-4 py-3 font-medium text-gray-900">
											{{ gem.gem_type }}
										</td>
										<td class="px-4 py-3 text-gray-600">
											{{ gem.cut || '-' }}
										</td>
										<td class="px-4 py-3 text-gray-600">
											{{ gem.color || '-' }}
										</td>
										<td class="px-4 py-3 text-gray-600">
											{{ gem.clarity || '-' }}
										</td>
										<td class="px-4 py-3 text-right font-mono text-gray-900">
											{{ gem.carat || '0' }}
										</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>

					<!-- Price Section -->
					<div class="bg-[#faf5f0] rounded-lg p-5 border border-[#E5D4A1]">
						<div class="flex items-baseline justify-between mb-4">
							<div>
								<p class="text-sm text-gray-600 mb-1">
									Total Price
									<span v-if="details.price_source" class="text-xs text-gray-400"
										>({{ details.price_source }})</span
									>
								</p>
								<p class="text-3xl font-bold text-gray-900">
									{{ formatCurrency(details.final_price) }}
								</p>
							</div>
							<span
								v-if="details.msrp && details.msrp > details.final_price"
								class="text-sm text-gray-500 line-through"
								>{{ formatCurrency(details.msrp) }}</span
							>
						</div>

						<button
							@click="addToCart"
							class="w-full bg-[#8B6914] text-white py-3.5 rounded-lg font-bold text-base hover:bg-[#7a5c11] transition-all shadow-md hover:shadow-lg transform active:scale-95 flex items-center justify-center gap-2"
						>
							<svg
								class="w-5 h-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
								></path>
							</svg>
							Add to Cart
						</button>
					</div>
				</div>
			</div>
		</div>
	</BaseModal>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { watch, ref, computed } from 'vue'
import { useCartStore } from '@/stores/cart.js'
import BaseModal from './BaseModal.vue'

const props = defineProps(['show', 'itemCode'])
const emit = defineEmits(['close'])
const cart = useCartStore()

const details = ref({})
const loading = ref(false)

// Computed net weight (gross - stone) or use provided net_weight
const calculatedNetWeight = computed(() => {
	if (details.value.net_weight) return details.value.net_weight
	const gross = details.value.gross_weight || 0
	const stone = details.value.stone_weight || 0
	return Math.max(0, gross - stone)
})

const itemFetcher = createResource({
	url: 'zevar_core.api.catalog.get_item_details',
	makeParams() {
		return { item_code: props.itemCode }
	},
	onSuccess(data) {
		details.value = {
			...data,
			final_price: data.price || data.msrp || 0,
			price_source: data.price ? 'Calculated' : 'MSRP',
		}
		loading.value = false
	},
	onError(error) {
		console.error('Failed to load item:', error)
		loading.value = false
	},
})

watch(
	() => props.show,
	(isOpen) => {
		if (isOpen && props.itemCode) {
			loading.value = true
			details.value = {}
			itemFetcher.fetch()
		}
	}
)

function addToCart() {
	if (!details.value.item_code) return
	cart.addItem({
		item_code: details.value.item_code,
		item_name: details.value.item_name,
		price: details.value.final_price,
		image: details.value.image,
	})
	emit('close')
}

function close() {
	emit('close')
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

function formatWeight(val) {
	if (!val && val !== 0) return '0.000'
	return parseFloat(val).toFixed(3)
}
</script>
