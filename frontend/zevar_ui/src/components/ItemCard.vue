<template>
	<div
		class="bg-white dark:bg-warm-dark-800 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer flex flex-col h-full group relative overflow-hidden border border-[#EFEAE2] dark:border-warm-border/30 hover:border-[#CBA358]/50"
		@click="emit('open-details', item.item_code)"
		data-testid="item-card"
	>
		<div
			class="aspect-[16/10] relative overflow-hidden flex items-center justify-center shrink-0 bg-[#F3F1ED] dark:bg-warm-dark-900"
		>
			<img
				:src="`${baseUrl}placeholders/${getJewelryCategory(item)}.png`"
				:alt="item.item_name"
				class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700 ease-out"
				@error="(e) => (e.target.src = `${baseUrl}placeholders/jewel.png`)"
			/>

			<div class="absolute top-2 right-2 flex flex-col gap-1 items-end z-10">
				<span
					v-if="item.stock_qty <= 0"
					class="bg-red-500/10 text-red-600 dark:text-red-400 text-[8px] font-extrabold px-1.5 py-0.5 rounded-full border border-red-500/20 shadow-sm backdrop-blur-md"
				>
					Out of Stock
				</span>
				<span
					v-else-if="item.stock_qty < 5"
					class="bg-orange-500/10 text-orange-600 dark:text-orange-400 text-[8px] font-extrabold px-1.5 py-0.5 rounded-full border border-orange-500/20 shadow-sm backdrop-blur-md"
				>
					Only {{ item.stock_qty }} left
				</span>
			</div>
		</div>

		<div class="p-2.5 flex-1 flex flex-col justify-between">
			<div>
				<div class="flex items-start justify-between mb-1">
					<h3
						class="font-sans font-bold text-xs tracking-tight text-gray-900 dark:text-white line-clamp-2 leading-tight group-hover:text-[#CBA358] transition-colors duration-200 min-h-[2rem]"
					>
						{{ item.item_name }}
					</h3>
				</div>

				<div class="flex flex-wrap gap-1 mb-1.5">
					<span
						class="inline-flex items-center px-1.5 py-0.5 rounded text-[8px] font-bold bg-yellow-100/60 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border border-yellow-200/30"
					>
						{{ item.metal || 'Gold' }}
					</span>
					<span
						class="inline-flex items-center px-1.5 py-0.5 rounded text-[8px] font-semibold bg-gray-100/80 text-gray-800 dark:bg-warm-dark-900 dark:text-gray-300 border border-gray-200/20"
					>
						{{ item.purity || 'Standard' }}
					</span>
				</div>

				<!-- Sleek Horizontal Weight Breakdown -->
				<div
					v-if="item.net_weight > 0 || item.gross_weight > 0 || item.stone_weight > 0"
					class="hidden lg:flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[8.5px] mt-1 border-t border-gray-200 dark:border-warm-border/30 pt-1.5"
				>
					<span
						v-if="item.net_weight > 0"
						class="font-bold text-gray-900 dark:text-white"
					>
						Net: {{ item.net_weight }}g
					</span>
					<span
						v-if="item.gross_weight > 0"
						class="font-semibold text-gray-700 dark:text-white/90"
					>
						Gross: {{ item.gross_weight }}g
					</span>
					<span
						v-if="item.stone_weight > 0"
						class="font-semibold text-red-600 dark:text-red-400"
					>
						Stn: -{{ item.stone_weight }}g
					</span>
				</div>
			</div>

			<div
				class="mt-auto pt-2 border-t border-gray-100 dark:border-warm-border/30 flex flex-col gap-1.5"
			>
				<div class="flex justify-between items-baseline">
					<span
						class="text-[8px] uppercase tracking-wider text-gray-400 dark:text-gray-500 font-bold"
						>Price</span
					>
					<span class="text-xs font-black text-[#D4AF37] font-mono leading-none">
						{{ formatCurrency(item.price) }}
					</span>
				</div>

				<button
					@click.stop="quickAdd"
					class="w-full py-1.5 border border-[#CBA358] hover:bg-[#CBA358] text-[#CBA358] hover:text-[#1E2022] font-bold text-[10px] rounded-md transition-all duration-200 flex items-center justify-center gap-1 active:scale-95 shadow-sm"
					title="Add to Cart"
					data-testid="add-to-cart-btn"
				>
					+ Add to Cart
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, watch } from 'vue'

const baseUrl = import.meta.env.BASE_URL

const props = defineProps({
	item: {
		type: Object,
		required: true,
		default: () => ({}),
	},
})

const emit = defineEmits(['quick-add', 'open-details'])

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

const imageFailed = ref(false)
watch(
	() => props.item.image,
	() => {
		imageFailed.value = false
	}
)

function quickAdd() {
	emit('quick-add', props.item)
}

function formatCurrency(value) {
	if (!value) return '$0.00'
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
	}).format(value)
}
</script>
