<template>
	<BaseModal
		:show="show"
		max-width="max-w-4xl"
		:no-max-height="true"
		:show-close="false"
		@close="close"
	>
		<div class="flex flex-col md:flex-row">
			<!-- Left: Luxury Vector Placeholder -->
			<div
				class="w-full md:w-1/2 relative overflow-hidden flex items-center justify-center border-r border-gray-100 dark:border-warm-border/50 bg-[#F3F1ED] dark:bg-warm-dark-900 min-h-[300px] md:min-h-[500px]"
			>
				<img
					:src="`${baseUrl}placeholders/${getJewelryCategory(details)}.png`"
					:alt="details.item_name"
					class="w-full h-full object-cover"
					@error="(e) => e.target.src = `${baseUrl}placeholders/jewel.png`"
				/>
			</div>

			<!-- Right: Details -->
			<div class="w-full md:w-1/2 p-8 overflow-y-auto bg-white dark:bg-[#1a1c23]">
				<div v-if="loading" class="h-full flex items-center justify-center">
					<div
						class="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 dark:border-[#D4AF37] border-t-transparent"
					></div>
				</div>

				<div v-else>
					<div class="mb-6">
						<h2
							class="text-2xl font-sans font-bold text-gray-900 dark:text-white leading-tight"
						>
							{{ details.item_name }}
						</h2>
						<p
							class="text-sm text-gray-500 dark:text-gray-400 mt-1 font-mono tracking-wide"
						>
							{{ details.item_code }}
						</p>
					</div>

					<div class="flex gap-2 mb-8">
						<span
							v-if="details.metal"
							class="px-3 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500 rounded text-xs font-bold uppercase tracking-wider border border-yellow-200 dark:border-yellow-700/50"
						>
							{{ details.metal }}
						</span>
						<span
							v-if="details.purity"
							class="px-3 py-1 bg-gray-100 text-gray-800 dark:bg-warm-dark-900 dark:text-gray-300 rounded text-xs font-bold uppercase tracking-wider border border-gray-200 dark:border-warm-border"
						>
							{{ details.purity }}
						</span>
					</div>

					<div
						class="bg-gray-50 dark:bg-[#15171e] rounded-lg p-5 mb-6 text-sm border border-gray-100 dark:border-warm-border/50"
					>
						<div class="flex justify-between mb-2 text-gray-600 dark:text-gray-400">
							<span>Gross Weight</span>
							<span class="font-medium text-gray-900 dark:text-gray-200"
								>{{ formatWeight(details.gross_weight) }} g</span
							>
						</div>
						<div class="flex justify-between mb-2 text-red-400 dark:text-red-400/80">
							<span>- Stone Weight</span>
							<span>{{ formatWeight(details.stone_weight) }} g</span>
						</div>
						<div
							class="flex justify-between pt-3 border-t border-gray-200 dark:border-warm-border mt-1"
						>
							<span class="font-bold text-gray-700 dark:text-white">Net Weight</span>
							<span class="font-bold text-gray-900 dark:text-[#D4AF37] text-base"
								>{{ formatWeight(calculatedNetWeight) }} g</span
							>
						</div>
					</div>

					<div v-if="details.gemstones && details.gemstones.length > 0" class="mb-6">
						<h4
							class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-3"
						>
							Gemstone Details
						</h4>
						<div
							class="bg-white dark:bg-[#0F1115] rounded-lg border border-gray-100 dark:border-warm-border overflow-hidden"
						>
							<table class="w-full text-sm text-left">
								<thead class="bg-gray-50 dark:bg-warm-dark-700">
									<tr class="text-xs text-gray-500 dark:text-gray-400 uppercase">
										<th class="px-4 py-2 font-medium">Stone</th>
										<th class="px-4 py-2 font-medium text-right">Carat</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-100 dark:divide-white/5">
									<tr v-for="(gem, i) in details.gemstones" :key="i">
										<td class="px-4 py-2.5">
											<div
												class="font-medium text-gray-900 dark:text-gray-200"
											>
												{{ gem.gem_type }}
											</div>
											<div
												class="text-[10px] text-gray-500 dark:text-gray-500"
											>
												{{ gem.cut }} &bull; {{ gem.color }} &bull;
												{{ gem.clarity }}
											</div>
										</td>
										<td
											class="px-4 py-2.5 text-right font-mono text-gray-700 dark:text-gray-300"
										>
											{{ gem.carat }}
										</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>

					<div class="space-y-3 mb-8 pt-2">
						<template v-if="details.net_weight > 0 && details.gold_rate > 0">
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400"
									>Gold Rate (Live)</span
								>
								<span class="text-gray-900 dark:text-gray-300 font-medium"
									>{{ formatCurrency(details.gold_rate) }} /g</span
								>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">Gold Value</span>
								<span class="text-gray-900 dark:text-gray-300 font-medium">{{
									formatCurrency(details.gold_value)
								}}</span>
							</div>
						</template>
						<div
							v-if="details.gemstone_value > 0"
							class="flex justify-between text-sm"
						>
							<span class="text-purple-600 dark:text-purple-400 font-medium"
								>Gemstone Value</span
							>
							<span class="text-purple-700 dark:text-purple-300 font-bold">{{
								formatCurrency(details.gemstone_value)
							}}</span>
						</div>

						<div
							class="flex justify-between items-end pt-4 border-t border-gray-100 dark:border-warm-border mt-2"
						>
							<div>
								<span class="text-lg font-bold text-gray-900 dark:text-white"
									>Total Price</span
								>
								<span
									v-if="details.price_source"
									class="ml-2 text-xs text-gray-400"
									>({{ details.price_source }})</span
								>
							</div>
							<span
								class="text-3xl font-sans font-bold text-gray-900 dark:text-white tracking-tight"
								>{{ formatCurrency(details.final_price) }}</span
							>
						</div>
					</div>

					<button
						@click="addToCart"
						class="w-full bg-gray-900 text-white dark:bg-[#D4AF37] dark:text-black py-4 rounded-lg font-bold text-lg hover:bg-gray-800 dark:hover:bg-[#b5952f] transition-all shadow-lg hover:shadow-xl transform active:scale-95 flex items-center justify-center gap-2"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

const baseUrl = import.meta.env.BASE_URL

function getJewelryCategory(item) {
	const name = (item.item_name || '').toLowerCase();
	const group = (item.item_group || '').toLowerCase();
	const type = (item.jewelry_type || '').toLowerCase();
	const cat = (item.category || '').toLowerCase();
	
	if (name.includes('ring') || group.includes('ring') || type.includes('ring') || cat.includes('ring')) {
		return 'ring';
	}
	if (name.includes('earring') || group.includes('earring') || type.includes('earring') || cat.includes('earring')) {
		return 'earring';
	}
	if (name.includes('pendant') || name.includes('gemstone') || group.includes('pendant') || type.includes('pendant') || cat.includes('pendant')) {
		return 'pendant';
	}
	if (name.includes('watch') || name.includes('timepiece') || group.includes('watch') || type.includes('watch') || cat.includes('watch')) {
		return 'watch';
	}
	if (name.includes('bracelet') || name.includes('bangle') || group.includes('bangle') || group.includes('bracelet') || type.includes('bracelet') || cat.includes('bracelet') || name.includes('cuff')) {
		return 'bracelet';
	}
	if (name.includes('necklace') || name.includes('choker') || group.includes('necklace') || type.includes('necklace') || cat.includes('necklace')) {
		return 'necklace';
	}
	// Smart resolution for Chain, Link, Rope, Cuban
	if (name.includes('chain') || name.includes('link') || name.includes('rope') || name.includes('cuban') || group.includes('chain') || type.includes('chain')) {
		if (/7|8|9/.test(name)) {
			return 'bracelet';
		}
		return 'necklace';
	}
	return 'jewel';
}

const details = ref({})
const loading = ref(false)

const calculatedNetWeight = computed(() => {
	if (details.value.net_weight) return details.value.net_weight
	const gross = details.value.gross_weight || 0
	const stone = details.value.stone_weight || 0
	return Math.max(0, gross - stone)
})

const itemFetcher = createResource({
	url: 'zevar_core.api.pricing.get_item_price',
	makeParams() {
		return { item_code: props.itemCode }
	},
	onSuccess(data) {
		details.value = { ...data, item_code: props.itemCode }
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
	cart.addItem(details.value)
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
