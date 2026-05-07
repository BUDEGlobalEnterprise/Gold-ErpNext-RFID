<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Gems &amp; Stones</h2>
					<span class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border">{{ stock.gemsTotal }} Items</span>
				</div>
				<button @click="loadData" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700">
					<svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': stock.gemsResource.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" /></svg>
				</button>
			</div>
			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="stock.gemsResource.loading && !stock.gems.length" class="flex items-center justify-center py-20"><div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div></div>
				<div v-else-if="!stock.gems.length" class="text-center py-20 text-gray-400 text-sm">No gems found</div>
				<div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
					<div v-for="gem in stock.gems" :key="gem.item_code" class="premium-card !p-0 overflow-hidden group cursor-pointer">
						<div class="aspect-square bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 flex items-center justify-center relative">
							<img v-if="gem.image" :src="gem.image" class="w-full h-full object-cover" />
							<svg v-else class="w-12 h-12 text-purple-200 dark:text-purple-800" fill="none" stroke="currentColor" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2" stroke-width="1" /><polyline points="2 17 12 22 22 17" stroke-width="1" /><polyline points="2 12 12 17 22 12" stroke-width="1" /></svg>
							<div class="absolute top-2 right-2"><span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full" :class="gem.stock_qty>0?'bg-green-100 text-green-700':'bg-red-100 text-red-700'">{{ gem.stock_qty }} pcs</span></div>
						</div>
						<div class="p-3">
							<div class="text-xs font-bold text-gray-900 dark:text-white truncate mb-1">{{ gem.item_name }}</div>
							<div class="flex flex-wrap gap-1 mb-2">
								<span v-if="gem.custom_gem_type" class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400">{{ gem.custom_gem_type }}</span>
								<span v-if="gem.custom_carat_weight" class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400">{{ gem.custom_carat_weight }}ct</span>
								<span v-if="gem.custom_gem_cut" class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400">{{ gem.custom_gem_cut }}</span>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-sm font-bold text-gray-900 dark:text-white font-mono">${{ Number(gem.standard_rate||gem.valuation_rate||0).toFixed(2) }}</span>
								<span v-if="gem.custom_certification_number" class="text-[9px] text-emerald-500 font-bold">✓ Cert</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>
<script setup>
import { onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'
const stock = useStockStore()
function loadData() { stock.loadGems() }
onMounted(loadData)
</script>
