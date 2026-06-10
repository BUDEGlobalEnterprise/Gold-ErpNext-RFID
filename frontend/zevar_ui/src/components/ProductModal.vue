<template>
	<BaseModal :show="show" max-width="max-w-5xl" :no-max-height="true" @close="close">
		<div class="flex flex-col md:flex-row">
			<!-- Left: Luxury Vector Placeholder -->
			<div
				class="w-full md:w-5/12 relative overflow-hidden flex items-center justify-center border-r border-[#EFEAE2] dark:border-warm-border/20 bg-[#F3F1ED] dark:bg-warm-dark-900 min-h-[300px] md:min-h-[500px]"
			>
				<img
					:src="`${baseUrl}placeholders/${getJewelryCategory(details)}.png`"
					:alt="details.item_name"
					class="w-full h-full object-cover"
					@error="(e) => (e.target.src = `${baseUrl}placeholders/jewel.png`)"
				/>
			</div>

			<!-- Right: Details -->
			<div
				class="w-full md:w-7/12 p-8 overflow-y-auto bg-[#FAF7F2] dark:bg-warm-dark-800 text-gray-900 dark:text-white"
			>
				<div v-if="loading" class="h-full flex items-center justify-center">
					<div
						class="animate-spin rounded-full h-10 w-10 border-3 border-[#CBA358] border-t-transparent"
					></div>
				</div>

				<div v-else class="space-y-6">
					<!-- Title & SKU -->
					<div>
						<h2
							class="text-2xl font-sans font-bold text-gray-900 dark:text-white leading-tight mb-1"
						>
							{{ details.item_name }}
						</h2>
						<p class="text-sm text-gray-500 font-mono">{{ details.item_code }}</p>
					</div>

					<!-- Badges -->
					<div class="flex flex-wrap gap-2">
						<span
							v-if="details.metal"
							class="px-3 py-1.5 bg-[#FAF5EE] text-[#CBA358] dark:bg-warm-dark-900 dark:text-yellow-400 rounded-md text-xs font-bold uppercase tracking-wider border border-[#EFEAE2] dark:border-warm-border/30"
						>
							{{ details.metal }}
						</span>
						<span
							v-if="details.purity"
							class="px-3 py-1.5 bg-white text-gray-800 dark:bg-warm-dark-900 dark:text-gray-300 rounded-md text-xs font-bold uppercase tracking-wider border border-[#EFEAE2] dark:border-warm-border/30"
						>
							{{ details.purity }}
						</span>
					</div>

					<!-- Weight Section -->
					<div
						class="bg-white dark:bg-warm-dark-900 rounded-xl p-5 border border-[#EFEAE2] dark:border-warm-border/30 shadow-sm"
					>
						<div
							v-if="details.gross_weight"
							class="flex justify-between text-sm mb-2.5"
						>
							<span class="text-gray-600 dark:text-white/70 font-semibold"
								>Gross Weight</span
							>
							<span class="font-bold text-gray-900 dark:text-white"
								>{{ formatWeight(details.gross_weight) }} g</span
							>
						</div>
						<div
							v-if="details.stone_weight"
							class="flex justify-between text-sm mb-2.5"
						>
							<span class="text-red-500/90 font-medium">- Stone Weight</span>
							<span class="font-semibold text-red-600 dark:text-red-400"
								>{{ formatWeight(details.stone_weight) }} g</span
							>
						</div>
						<div
							v-if="details.net_weight || calculatedNetWeight > 0"
							class="flex justify-between pt-3 border-t border-[#EFEAE2] dark:border-warm-border/20 mt-3"
						>
							<span class="font-bold text-gray-900 dark:text-white">Net Weight</span>
							<span class="font-extrabold text-[#CBA358] text-xl font-mono"
								>{{ formatWeight(calculatedNetWeight) }} g</span
							>
						</div>
					</div>

					<!-- Product Details Table -->
					<div
						class="border border-[#EFEAE2] dark:border-warm-border/30 rounded-xl overflow-hidden shadow-sm bg-white dark:bg-warm-dark-900"
					>
						<div
							class="bg-[#FAF5EE] dark:bg-warm-dark-850 px-4 py-2.5 border-b border-[#EFEAE2] dark:border-warm-border/20"
						>
							<h3
								class="font-bold text-gray-900 dark:text-white text-xs uppercase tracking-wider"
							>
								Product Details
							</h3>
						</div>
						<div class="divide-y divide-[#EFEAE2] dark:divide-warm-border/20">
							<div v-if="details.product_type" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Product Type</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.product_type }}</span
								>
							</div>
							<div v-if="details.jewelry_type" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Jewelry Type</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.jewelry_type }}</span
								>
							</div>
							<div
								v-if="details.jewelry_subtype"
								class="flex py-2.5 px-4 items-center"
							>
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Sub Type</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.jewelry_subtype }}</span
								>
							</div>
							<div
								v-if="details.material_color"
								class="flex py-2.5 px-4 items-center"
							>
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Material Color</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.material_color }}</span
								>
							</div>
							<div v-if="details.finish" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Finish</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.finish }}</span
								>
							</div>
							<div v-if="details.plating" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Plating</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.plating }}</span
								>
							</div>
							<div v-if="details.length" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Length of Item</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.length }}</span
								>
							</div>
							<div v-if="details.width" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Width of Item</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.width }}</span
								>
							</div>
							<div v-if="details.size" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Size</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.size }}</span
								>
							</div>
							<div v-if="details.chain_type" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Chain Type</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.chain_type }}</span
								>
							</div>
							<div v-if="details.clasp_type" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Clasp Type</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.clasp_type }}</span
								>
							</div>
							<div v-if="details.gender" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Gender</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.gender }}</span
								>
							</div>
							<div v-if="details.completeness" class="flex py-2.5 px-4 items-center">
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Completeness</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.completeness }}</span
								>
							</div>
							<div
								v-if="details.country_of_origin"
								class="flex py-2.5 px-4 items-center"
							>
								<span
									class="w-1/2 text-xs text-gray-500 dark:text-white/60 font-semibold"
									>Country of Origin</span
								>
								<span
									class="w-1/2 text-xs text-gray-900 dark:text-white font-bold"
									>{{ details.country_of_origin || 'USA' }}</span
								>
							</div>
						</div>
					</div>

					<!-- Gemstone Details -->
					<div
						v-if="details.gemstones && details.gemstones.length > 0"
						class="border border-[#EFEAE2] dark:border-warm-border/30 rounded-xl overflow-hidden shadow-sm bg-white dark:bg-warm-dark-900"
					>
						<div
							class="bg-[#FAF5EE] dark:bg-warm-dark-850 px-4 py-2.5 border-b border-[#EFEAE2] dark:border-warm-border/20"
						>
							<h3
								class="font-bold text-[#CBA358] text-xs uppercase tracking-wider flex items-center gap-2"
							>
								<svg
									class="w-4 h-4 text-[#CBA358]"
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
							<table class="w-full text-xs">
								<thead
									class="bg-gray-50/50 dark:bg-warm-dark-850 border-b border-[#EFEAE2] dark:border-warm-border/20"
								>
									<tr
										class="text-[10px] text-gray-500 dark:text-white/60 uppercase font-semibold"
									>
										<th class="px-4 py-2 text-left font-semibold">Stone</th>
										<th class="px-4 py-2 text-left font-semibold">Cut</th>
										<th class="px-4 py-2 text-left font-semibold">Color</th>
										<th class="px-4 py-2 text-left font-semibold">Clarity</th>
										<th class="px-4 py-2 text-right font-semibold">Carat</th>
									</tr>
								</thead>
								<tbody
									class="divide-y divide-[#EFEAE2] dark:divide-warm-border/20"
								>
									<tr
										v-for="(gem, i) in details.gemstones"
										:key="i"
										class="hover:bg-gray-50/50 dark:hover:bg-warm-dark-850/50"
									>
										<td
											class="px-4 py-3 font-bold text-gray-900 dark:text-white"
										>
											{{ gem.gem_type }}
										</td>
										<td class="px-4 py-3 text-gray-600 dark:text-white/70">
											{{ gem.cut || '-' }}
										</td>
										<td class="px-4 py-3 text-gray-600 dark:text-white/70">
											{{ gem.color || '-' }}
										</td>
										<td class="px-4 py-3 text-gray-600 dark:text-white/70">
											{{ gem.clarity || '-' }}
										</td>
										<td
											class="px-4 py-3 text-right font-mono text-gray-900 dark:text-white font-bold"
										>
											{{ gem.carat || '0' }}
										</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>

					<!-- Price Section -->
					<div
						class="bg-white dark:bg-warm-dark-900 rounded-xl p-5 border border-[#CBA358]/35 shadow-md"
					>
						<div class="flex items-baseline justify-between mb-4">
							<div>
								<p
									class="text-xs uppercase tracking-wider text-gray-400 dark:text-white/40 font-bold mb-1"
								>
									Total Price
									<span
										v-if="details.price_source"
										class="text-[10px] text-gray-400 font-normal normal-case"
										>({{ details.price_source }})</span
									>
								</p>
								<p
									class="text-3xl font-black text-[#CBA358] dark:text-[#CBA358] font-mono leading-none"
								>
									{{ formatCurrency(details.final_price) }}
								</p>
							</div>
							<span
								v-if="details.msrp && details.msrp > details.final_price"
								class="text-sm text-gray-400 line-through font-mono"
								>{{ formatCurrency(details.msrp) }}</span
							>
						</div>

						<button
							@click="addToCart"
							class="w-full bg-[#1E2022] hover:bg-black dark:bg-[#CBA358] dark:hover:bg-[#d8b878] text-white dark:text-[#1E2022] py-3.5 rounded-xl font-bold text-base transition-all shadow-md hover:shadow-lg transform active:scale-95 flex items-center justify-center gap-2"
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

const baseUrl = import.meta.env.BASE_URL

const props = defineProps(['show', 'itemCode'])
const emit = defineEmits(['close'])
const cart = useCartStore()

function getJewelryCategory(item) {
	const name = (item.item_name || '').toLowerCase()
	const group = (item.item_group || '').toLowerCase()
	const type = (item.jewelry_type || '').toLowerCase()
	const cat = (item.category || '').toLowerCase()

	if (
		name.includes('ring') ||
		group.includes('ring') ||
		type.includes('ring') ||
		cat.includes('ring')
	) {
		return 'ring'
	}
	if (
		name.includes('earring') ||
		group.includes('earring') ||
		type.includes('earring') ||
		cat.includes('earring')
	) {
		return 'earring'
	}
	if (
		name.includes('pendant') ||
		name.includes('gemstone') ||
		group.includes('pendant') ||
		type.includes('pendant') ||
		cat.includes('pendant')
	) {
		return 'pendant'
	}
	if (
		name.includes('watch') ||
		name.includes('timepiece') ||
		group.includes('watch') ||
		type.includes('watch') ||
		cat.includes('watch')
	) {
		return 'watch'
	}
	if (
		name.includes('bracelet') ||
		name.includes('bangle') ||
		group.includes('bangle') ||
		group.includes('bracelet') ||
		type.includes('bracelet') ||
		cat.includes('bracelet') ||
		name.includes('cuff')
	) {
		return 'bracelet'
	}
	if (
		name.includes('necklace') ||
		name.includes('choker') ||
		group.includes('necklace') ||
		type.includes('necklace') ||
		cat.includes('necklace')
	) {
		return 'necklace'
	}
	// Smart resolution for Chain, Link, Rope, Cuban
	if (
		name.includes('chain') ||
		name.includes('link') ||
		name.includes('rope') ||
		name.includes('cuban') ||
		group.includes('chain') ||
		type.includes('chain')
	) {
		if (/7|8|9/.test(name)) {
			return 'bracelet'
		}
		return 'necklace'
	}
	return 'jewel'
}

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
