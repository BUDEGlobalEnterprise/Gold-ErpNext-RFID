<template>
	<div class="group cursor-pointer" @click="$emit('click', product)">
		<div
			class="relative rounded-2xl overflow-hidden bg-gray-50 aspect-square mb-3 border border-gray-100 group-hover:border-[#C9A962] transition-all group-hover:shadow-lg"
		>
			<img
				v-if="product.image"
				:src="product.image"
				:alt="product.item_name"
				class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
			/>
			<div v-else class="flex items-center justify-center h-full text-6xl opacity-40">
				💎
			</div>

			<!-- Badges -->
			<div class="absolute top-2 left-2 flex flex-col gap-1.5">
				<span
					v-if="product.is_featured"
					class="px-2 py-0.5 bg-[#8B6914] text-white text-[9px] font-bold uppercase tracking-wider rounded-md"
					>Featured</span
				>
				<span
					v-if="product.is_trending"
					class="px-2 py-0.5 bg-emerald-500 text-white text-[9px] font-bold uppercase tracking-wider rounded-md"
					>Trending</span
				>
				<span
					v-if="product.stock_qty > 0"
					class="px-2 py-0.5 bg-blue-500 text-white text-[9px] font-bold uppercase tracking-wider rounded-md"
					>In Stock</span
				>
			</div>

			<!-- Quick View -->
			<button
				class="absolute bottom-3 right-3 w-10 h-10 bg-white rounded-full shadow-md flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-[#8B6914] hover:text-white"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
					/>
				</svg>
			</button>
		</div>

		<!-- Details -->
		<div class="space-y-1 mt-2">
			<h3
				class="font-medium text-xs text-gray-900 line-clamp-2 min-h-[2rem] group-hover:text-[#8B6914] transition-colors"
			>
				{{ product.item_name }}
			</h3>

			<!-- Metal & Purity -->
			<div class="flex items-center gap-1.5 text-[10px] text-gray-500">
				<span v-if="product.metal">{{ product.metal }}</span>
				<span
					v-if="product.metal && product.purity"
					class="w-1 h-1 rounded-full bg-gray-300"
				></span>
				<span v-if="product.purity">{{ product.purity }}</span>
			</div>

			<!-- Weight Info -->
			<div v-if="showWeights" class="flex items-center gap-2 text-[10px]">
				<span v-if="product.gross_weight" class="text-gray-600">
					<span class="font-medium">Gross:</span>
					{{ formatWeight(product.gross_weight) }}
				</span>
				<span v-if="product.stone_weight" class="text-red-600">
					<span class="font-medium">Stone:</span>
					{{ formatWeight(product.stone_weight) }}
				</span>
				<span v-if="product.net_weight" class="text-[#8B6914] font-medium">
					<span>Net:</span> {{ formatWeight(product.net_weight) }}
				</span>
			</div>

			<!-- Price -->
			<div class="pt-1.5 border-t border-gray-100">
				<div class="flex items-baseline gap-2">
					<span class="text-base font-bold text-gray-900 font-sans leading-tight">{{
						formatPrice(product.price)
					}}</span>
					<span
						v-if="product.msrp && product.msrp > product.price"
						class="text-xs text-gray-400 line-through"
						>{{ formatPrice(product.msrp) }}</span
					>
				</div>
				<p v-if="product.jewelry_type" class="text-[10px] text-gray-400 mt-0.5">
					{{ product.jewelry_type }}
				</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	product: { type: Object, required: true },
})

defineEmits(['click'])

const showWeights = computed(() => {
	return props.product.gross_weight || props.product.stone_weight || props.product.net_weight
})

function formatPrice(value) {
	if (!value) return '$0'
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	}).format(value)
}

function formatWeight(value) {
	if (!value) return '0g'
	return `${parseFloat(value).toFixed(2)}g`
}
</script>

<style scoped>
.line-clamp-2 {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}
</style>
