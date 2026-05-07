<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Collections</h2>
					<span class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border">{{ stock.collectionsTotal }} Collections</span>
				</div>
				<button @click="loadData" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700">
					<svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': stock.collectionsResource.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" /></svg>
				</button>
			</div>
			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="stock.collectionsResource.loading && !stock.collections.length" class="flex items-center justify-center py-20"><div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div></div>
				<div v-else-if="!stock.collections.length" class="text-center py-20 text-gray-400 text-sm">No collections found</div>
				<div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
					<div v-for="col in stock.collections" :key="col.name" class="premium-card !p-0 overflow-hidden cursor-pointer hover:border-[#D4AF37]/50 group">
						<div class="aspect-[3/2] bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/10 dark:to-orange-900/10 flex items-center justify-center">
							<img v-if="col.image" :src="col.image" class="w-full h-full object-cover" />
							<svg v-else class="w-12 h-12 text-amber-200 dark:text-amber-800" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" stroke-width="1" /><rect x="14" y="3" width="7" height="7" stroke-width="1" /><rect x="14" y="14" width="7" height="7" stroke-width="1" /><rect x="3" y="14" width="7" height="7" stroke-width="1" /></svg>
						</div>
						<div class="p-3">
							<div class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ col.item_group_name }}</div>
							<div class="text-[10px] text-gray-500 mt-0.5">{{ col.item_count }} items</div>
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
function loadData() { stock.loadCollections() }
onMounted(loadData)
</script>
