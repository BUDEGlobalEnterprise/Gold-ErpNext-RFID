<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Categories</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.categoriesTotal }} Groups</span
					>
				</div>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': stock.categoriesResource.loading }"
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
			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.categoriesResource.loading && !stock.categories.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.categories.length"
					class="text-center py-20 text-gray-400 text-sm"
				>
					No categories found
				</div>
				<div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
					<div
						v-for="cat in stock.categories"
						:key="cat.name"
						class="premium-card cursor-pointer hover:border-[#D4AF37]/50"
					>
						<div class="flex items-center gap-3">
							<div
								class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
								:class="
									cat.is_group
										? 'bg-amber-100 dark:bg-amber-900/30'
										: 'bg-gray-100 dark:bg-warm-dark-900'
								"
							>
								<svg
									class="w-5 h-5"
									:class="cat.is_group ? 'text-amber-600' : 'text-gray-500'"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
									/>
								</svg>
							</div>
							<div class="min-w-0">
								<div
									class="text-xs font-bold text-gray-900 dark:text-white truncate"
								>
									{{ cat.item_group_name }}
								</div>
								<div class="text-[10px] text-gray-500">
									{{ cat.item_count }} items
								</div>
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
function loadData() {
	stock.loadCategories()
}
onMounted(loadData)
</script>
