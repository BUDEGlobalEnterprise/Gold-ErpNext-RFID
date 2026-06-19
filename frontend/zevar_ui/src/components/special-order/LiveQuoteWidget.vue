<template>
	<!-- ── Sticky right-hand sidebar for live quote updates ────────────────── -->
	<div
		class="sticky top-0 h-[calc(100vh-120px)] overflow-hidden bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md border-l border-gray-200 dark:border-warm-border/50 flex flex-col shadow-xl"
		:class="className"
		:style="widthStyle"
	>
		<!-- Header ─────────────────────────────────────────────────────── -->
		<div
			class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-warm-border/50 shrink-0"
		>
			<div>
				<h3 class="premium-title tracking-tighter text-base text-gray-900 dark:text-white">
					Live Quote
				</h3>
				<p
					v-if="draftOrder.customer"
					class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mt-0.5"
				>
					{{ draftOrder.customer.name || draftOrder.customer }}
				</p>
			</div>
			<div class="flex items-center gap-1.5">
				<span v-if="isFetchingQuote" class="h-2 w-2 rounded-full bg-[#D4AF37] animate-pulse"></span>
				<span v-else-if="liveQuote" class="h-2 w-2 rounded-full bg-green-500"></span>
				<span v-else class="h-2 w-2 rounded-full bg-gray-300 dark:bg-gray-600"></span>
				<span class="text-[9px] font-black uppercase tracking-widest text-gray-400">
					{{ isFetchingQuote ? 'SYNCING' : liveQuote ? 'LIVE' : 'READY' }}
				</span>
			</div>
		</div>

		<!-- Content ────────────────────────────────────────────────────── -->
		<div class="flex-1 overflow-y-auto p-4 space-y-4">
			<!-- Error state ──────────────────────────────────────────────── -->
			<div v-if="lastQuoteError" class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-600 dark:text-red-400 text-xs font-medium">
				{{ lastQuoteError }}
			</div>

			<!-- ── Zevar: BOM Live Pricing Breakdown ────────────────── -->
			<div class="rounded-xl border border-gray-200 dark:border-warm-border/50 overflow-hidden bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md">
				<div class="px-4 py-3 bg-gray-50/50 dark:bg-warm-dark-900/50 border-b border-gray-200 dark:border-warm-border/50">
					<div class="flex items-center gap-2">
						<svg class="w-3.5 h-3.5 text-[#D4AF37]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
						</svg>
						<span class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400">
							Zevar — BOM Live Pricing
						</span>
					</div>
				</div>

				<div class="divide-y divide-gray-100 dark:divide-warm-border/30">
					<!-- Metal Cost row ───────────────────────────────────────── -->
					<div class="flex items-center justify-between px-4 py-3 text-xs">
						<div class="flex items-center gap-2">
							<div class="w-2 h-2 rounded-full bg-blue-500"></div>
							<span class="text-gray-500 dark:text-gray-400">Metal Cost</span>
						</div>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(bomMetalCost) }}
						</span>
					</div>

					<!-- Stones Cost row ──────────────────────────────────────── -->
					<div class="flex items-center justify-between px-4 py-3 text-xs">
						<div class="flex items-center gap-2">
							<div class="w-2 h-2 rounded-full bg-purple-500"></div>
							<span class="text-gray-500 dark:text-gray-400">Stones Cost</span>
						</div>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(bomStonesCost) }}
						</span>
					</div>

					<!-- Labor Cost row ───────────────────────────────────────── -->
					<div class="flex items-center justify-between px-4 py-3 text-xs">
						<div class="flex items-center gap-2">
							<div class="w-2 h-2 rounded-full bg-amber-500"></div>
							<span class="text-gray-500 dark:text-gray-400">Labor Cost</span>
						</div>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(draftOrder.laborCost) }}
						</span>
					</div>

					<!-- Overhead Cost row ────────────────────────────────────── -->
					<div class="flex items-center justify-between px-4 py-3 text-xs">
						<div class="flex items-center gap-2">
							<div class="w-2 h-2 rounded-full bg-gray-400"></div>
							<span class="text-gray-500 dark:text-gray-400">Overhead</span>
						</div>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatCurrency(draftOrder.overheadCost) }}
						</span>
					</div>
				</div>
			</div>

			<!-- Stone detail list (when stones exist) ──────────────────────── -->
			<div v-if="stones.length > 0" class="rounded-lg border border-gray-200 dark:border-warm-border/50 overflow-hidden">
				<div class="px-3 py-2 bg-gray-50/50 dark:bg-warm-dark-900/50 border-b border-gray-200 dark:border-warm-border/50 flex items-center justify-between">
					<span class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400">
						Stones ({{ stones.length }})
					</span>
					<span class="font-mono text-xs font-bold text-[#D4AF37]">
						{{ formatCurrency(bomStonesCost) }}
					</span>
				</div>
				<div class="divide-y divide-gray-100 dark:divide-warm-border/30">
					<div v-for="stone in stones.slice(0, 5)" :key="stone.id" class="flex justify-between px-3 py-1.5 text-xs">
						<span class="text-gray-600 dark:text-gray-300 truncate max-w-[60%]">
							{{ stone.stoneType }} {{ stone.caratWeight }}ct
						</span>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200 whitespace-nowrap ml-2">
							{{ formatCurrency(lineTotal(stone)) }}
						</span>
					</div>
					<div v-if="stones.length > 5" class="px-3 py-1.5 text-xs text-center text-gray-400 dark:text-gray-500">
						+{{ stones.length - 5 }} more
					</div>
				</div>
			</div>

			<!-- Backend quote response ───────────────────────────────────── -->
			<div v-if="liveQuote" class="rounded-lg border border-[#D4AF37]/30 overflow-hidden bg-[#D4AF37]/5 dark:bg-[#D4AF37]/5">
				<div class="px-3 py-2 bg-[#D4AF37]/10 dark:bg-[#D4AF37]/10 border-b border-[#D4AF37]/30">
					<span class="text-[10px] font-black uppercase tracking-widest text-[#D4AF37]">
						Server Quote
					</span>
				</div>
				<div class="p-3 space-y-2 text-xs">
					<div v-for="(val, key) in liveQuoteData" :key="key" class="flex justify-between">
						<span class="text-gray-500 dark:text-gray-400">{{ formatLabel(key) }}</span>
						<span class="font-mono font-bold text-gray-800 dark:text-gray-200">
							{{ formatLabelValue(key, val) }}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Grand Total Footer ─────────────────────────────────────────── -->
		<div
			class="border-t border-gray-200 dark:border-warm-border/50 p-4 bg-gradient-to-r from-[#D4AF37]/10 to-transparent dark:from-[#D4AF37]/5 shrink-0"
		>
			<div class="flex items-center justify-between">
				<span class="text-[10px] font-black uppercase tracking-widest text-[#D4AF37]">Total</span>
				<p v-if="isFetchingQuote" class="font-mono font-black text-[#D4AF37] text-2xl animate-pulse">CALCULATING...</p>
				<p v-else class="font-mono font-black text-[#D4AF37] text-2xl">
					{{ formatCurrency(grandTotal) }}
				</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useSpecialOrderStore } from '@/stores/specialOrder'

const props = defineProps({
	className: { type: String, default: 'w-80' },
})

const store = useSpecialOrderStore()

const draftOrder = computed(() => store.draftOrder)
const stones = computed(() => store.draftOrder.stones)
const liveQuote = computed(() => store.liveQuote)
const isFetchingQuote = computed(() => store.isFetchingQuote)
const lastQuoteError = computed(() => store.lastQuoteError)
const grandTotal = computed(() => store.grandTotal)
const totalStoneCost = computed(() => store.totalStoneCost)

// BOM cost breakdowns (Zevar)
const bomMetalCost = computed(() => {
	if (liveQuote.value?.metal_cost !== undefined) {
		return liveQuote.value.metal_cost
	}
	const weight = Number(draftOrder.value?.metalWeight) || 0
	const pricePerGram = draftOrder.value?.metalPricePerGram || 0
	return Number((weight * pricePerGram).toFixed(2))
})

const bomStonesCost = computed(() => store.totalStoneCost)

const liveQuoteData = computed(() => {
	const data = liveQuote.value
	if (!data) return {}
	const flat = {}
	for (const [key, val] of Object.entries(data)) {
		if (typeof val !== 'object' || val === null) flat[key] = val
	}
	return flat
})

const widthStyle = computed(() => {
	if (props.className.startsWith('w-')) {
		const w = parseInt(props.className.replace('w-', ''), 10)
		return { width: `${w * 0.25}rem`, minWidth: `${w * 0.25}rem`, maxWidth: `${w * 0.25}rem` }
	}
	return {}
})

function lineTotal(stone) {
	return Number(((stone.caratWeight || 0) * (stone.unitPrice || 0)).toFixed(2))
}

function formatCurrency(value) {
	return '$' + Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatLabel(key) {
	const labels = {
		metal_cost: 'Metal Cost', labor_cost: 'Labor Cost', stone_cost: 'Stone Cost',
		overhead_cost: 'Overhead', total: 'Total', estimated_weight: 'Est. Weight',
		estimated_price: 'Est. Price', margin: 'Margin',
	}
	return labels[key] || key.replace(/_/g, ' ')
}

function formatLabelValue(key, val) {
	if (key === 'total' || key.includes('cost') || key.includes('price') || key.includes('margin')) {
		return formatCurrency(val)
	}
	return val
}
</script>
