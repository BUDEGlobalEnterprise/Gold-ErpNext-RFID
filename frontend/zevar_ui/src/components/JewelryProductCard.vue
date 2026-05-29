<template>
	<div class="group relative" @click="$emit('view', product)">
		<!-- Hover Glow -->
		<div
			class="absolute -inset-2 bg-gradient-to-r from-[#D4AF37]/0 via-[#D4AF37]/10 to-[#D4AF37]/0 rounded-3xl opacity-0 group-hover:opacity-100 blur-2xl transition-all duration-500"
		></div>

		<div
			class="relative rounded-2xl overflow-hidden border transition-all duration-300 transform group-hover:-translate-y-1 group-hover:shadow-xl cursor-pointer"
			:class="
				isDark
					? 'glass-product-card border-white/5 group-hover:border-[#D4AF37]/20'
					: 'bg-white border-gray-100 shadow-sm group-hover:border-[#D4AF37]/50 group-hover:shadow-[#D4AF37]/10'
			"
		>
			<!-- Image Container -->
			<div
				class="relative aspect-square overflow-hidden"
				:class="isDark ? 'bg-gradient-to-br from-[#18181b] to-[#1e1e24]' : 'bg-gray-50'"
			>
				<!-- Placeholder/Emoji Display -->
				<div class="absolute inset-0 flex items-center justify-center">
					<span
						class="text-7xl opacity-60 group-hover:opacity-80 group-hover:scale-110 transition-all duration-500"
					>
						{{ product.emoji || categoryEmoji }}
					</span>
				</div>

				<!-- Image if available -->
				<img
					v-if="product.image"
					:src="product.image"
					:alt="product.item_name || product.name"
					class="absolute inset-0 w-full h-full object-cover opacity-0 group-hover:opacity-100 transition-opacity duration-500"
					loading="lazy"
				/>

				<!-- Gradient Overlay -->
				<div
					class="absolute inset-0 bg-gradient-to-t"
					:class="isDark ? 'from-black/80' : 'from-black/40'"
				></div>

				<!-- Top Badges -->
				<div class="absolute top-3 left-3 flex gap-2 flex-wrap">
					<span
						v-if="product.stock_qty > 0"
						class="px-2 py-1 bg-emerald-500 text-white text-[10px] font-bold uppercase tracking-wide rounded flex items-center gap-1"
					>
						<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M5 13l4 4L19 7"
							></path>
						</svg>
						In Stock
					</span>
					<span
						v-else-if="showPartnerBadge && product.custom_source"
						class="px-2 py-1 bg-purple-600 text-white text-[10px] font-bold uppercase tracking-wide rounded flex items-center gap-1"
					>
						<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
							/>
						</svg>
						{{ product.custom_source }}
					</span>
					<span
						v-if="product.is_featured"
						class="px-2 py-1 bg-[#D4AF37] text-black text-[10px] font-bold uppercase tracking-wide rounded"
						>Featured</span
					>
					<span
						v-if="product.is_trending"
						class="px-2 py-1 bg-emerald-500 text-white text-[10px] font-bold uppercase tracking-wide rounded"
						>Trending</span
					>
					<span
						v-if="product.isNew"
						class="px-2 py-1 bg-blue-500 text-white text-[10px] font-bold uppercase tracking-wide rounded"
						>New</span
					>
					<div
						v-if="product.discount"
						class="absolute top-3 right-3 px-2 py-1 bg-red-500 text-white text-[10px] font-bold uppercase tracking-wide rounded"
					>
						-{{ product.discount }}%
					</div>
				</div>

				<!-- Bottom Badges - Material, Purity, Weight -->
				<div class="absolute bottom-3 left-3 right-3 flex items-center gap-2 flex-wrap">
					<span
						v-if="product.metal"
						class="px-3 py-1.5 rounded-full backdrop-blur-sm border text-xs font-medium"
						:class="
							isDark
								? 'bg-black/60 border-[#D4AF37]/30 text-[#D4AF37]'
								: 'bg-white/90 border-gray-200 text-[#8B7355]'
						"
					>
						{{ product.metal }}
					</span>
					<span
						v-if="product.purity"
						class="px-3 py-1.5 rounded-full backdrop-blur-sm border text-xs"
						:class="
							isDark
								? 'bg-black/60 border-white/20 text-white'
								: 'bg-white/90 border-gray-200 text-gray-700'
						"
					>
						{{ product.purity }}
					</span>
					<span
						v-if="displayWeight"
						class="px-3 py-1.5 rounded-full backdrop-blur-sm border text-xs"
						:class="
							isDark
								? 'bg-black/60 border-white/20 text-gray-300'
								: 'bg-white/90 border-gray-200 text-gray-600'
						"
					>
						{{ displayWeight }}g
					</span>
				</div>
			</div>

			<!-- Content -->
			<div class="p-4 space-y-3">
				<!-- Title -->
				<h3
					class="font-medium text-sm line-clamp-2 min-h-[2.5rem] transition-colors"
					:class="
						isDark
							? 'text-white group-hover:text-[#D4AF37]'
							: 'text-gray-900 group-hover:text-[#8B7355]'
					"
				>
					{{ product.item_name || product.name }}
				</h3>

				<!-- Jewelry Type & Gender -->
				<p
					class="text-xs flex items-center gap-2"
					:class="isDark ? 'text-gray-500' : 'text-gray-500'"
				>
					<span v-if="product.jewelry_type" class="flex items-center gap-1">
						<span class="w-1.5 h-1.5 rounded-full bg-[#D4AF37]"></span>
						{{ product.jewelry_type }}
					</span>
					<span v-if="product.gender" class="text-gray-400">• {{ product.gender }}</span>
				</p>

				<!-- Price Section -->
				<div
					class="flex items-end justify-between pt-2 border-t"
					:class="isDark ? 'border-white/5' : 'border-gray-100'"
				>
					<div>
						<p class="text-xs text-gray-400 mb-0.5">Price</p>
						<div class="flex items-baseline gap-2">
							<span
								class="text-xl font-bold font-sans"
								:class="isDark ? 'text-white' : 'text-gray-900'"
								>{{ formatPrice(product.price) }}</span
							>
							<span
								v-if="product.msrp && product.msrp > product.price"
								class="text-sm text-gray-400 line-through"
								>{{ formatPrice(product.msrp) }}</span
							>
						</div>
					</div>

					<!-- Quick View -->
					<button
						@click.stop="$emit('view', product)"
						class="w-10 h-10 rounded-xl flex items-center justify-center hover:shadow-lg active:scale-95 transition-all"
						:class="
							isDark
								? 'bg-[#D4AF37] text-black hover:shadow-[#D4AF37]/30'
								: 'bg-[#1a1a1a] text-white hover:bg-black hover:shadow-xl'
						"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
							></path>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
							></path>
						</svg>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	product: {
		type: Object,
		required: true,
		default: () => ({}),
	},
	isDark: {
		type: Boolean,
		default: true,
	},
	showPartnerBadge: {
		type: Boolean,
		default: false,
	},
})

defineEmits(['view'])

// Computed: Display weight (prefer net_weight, fallback to gross_weight)
const displayWeight = computed(() => {
	const weight = props.product.net_weight || props.product.gross_weight
	if (!weight || weight <= 0) return null
	return weight.toFixed(2)
})

// Computed: Category-based emoji
const categoryEmoji = computed(() => {
	const type = (props.product.jewelry_type || '').toLowerCase()
	const emojiMap = {
		rings: '💍',
		chains: '⛓️',
		necklaces: '📿',
		earrings: '👂',
		bracelets: '📿',
		pendants: '🔮',
		watches: '⌚',
	}
	return emojiMap[type] || '💎'
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
</script>

<style scoped>
.glass-product-card {
	background: linear-gradient(180deg, rgba(20, 20, 25, 0.9) 0%, rgba(10, 10, 12, 0.95) 100%);
	backdrop-filter: blur(10px);
}

.line-clamp-2 {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}
</style>
