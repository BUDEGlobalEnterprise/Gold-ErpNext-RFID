<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Brands</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.brandsTotal }} Brands</span
					>
				</div>
				<div class="flex items-center gap-2">
					<div class="relative">
						<input
							v-model="search"
							@input="debouncedSearch"
							type="text"
							placeholder="Search brands..."
							class="pl-8 pr-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37] w-40"
						/>
						<svg
							class="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<circle cx="11" cy="11" r="8" stroke-width="2" />
							<path stroke-linecap="round" stroke-width="2" d="M21 21l-4.35-4.35" />
						</svg>
					</div>
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': stock.brandsResource.loading }"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15"
							/>
						</svg>
					</button>
				</div>
			</div>
			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.brandsResource.loading && !stock.brands.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.brands.length"
					class="text-center py-20 text-gray-400 text-sm"
				>
					No brands found
				</div>
				<div
					v-else
					class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3"
				>
					<div
						v-for="brand in stock.brands"
						:key="brand.name"
						class="premium-card !p-4 cursor-pointer hover:border-[#D4AF37]/50 flex flex-col items-center text-center"
					>
						<div
							class="w-16 h-16 rounded-full bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 flex items-center justify-center mb-3 overflow-hidden"
						>
							<img
								v-if="brand.image"
								:src="brand.image"
								class="w-full h-full object-cover rounded-full"
							/>
							<span v-else class="text-2xl font-bold text-[#D4AF37]">{{
								(brand.brand_name || brand.name || '?')[0]
							}}</span>
						</div>
						<div
							class="text-sm font-bold text-gray-900 dark:text-white truncate w-full"
						>
							{{ brand.brand_name || brand.name }}
						</div>
						<div class="text-[10px] text-gray-500 mt-1">
							{{ brand.item_count }} items
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'
const stock = useStockStore()
const search = ref('')
let searchTimer = null
function loadData() {
	stock.loadBrands({ search: search.value || undefined })
}
function debouncedSearch() {
	clearTimeout(searchTimer)
	searchTimer = setTimeout(loadData, 300)
}
onMounted(loadData)
</script>
