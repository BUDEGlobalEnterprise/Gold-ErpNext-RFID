<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Storages</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.warehousesTotal }} Locations</span
					>
				</div>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': stock.warehousesResource.loading }"
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
					v-if="stock.warehousesResource.loading && !stock.warehouses.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.warehouses.length"
					class="text-center py-20 text-gray-400 text-sm"
				>
					No warehouses found
				</div>
				<div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
					<div
						v-for="wh in stock.warehouses"
						:key="wh.name"
						class="premium-card cursor-pointer"
						@click="viewWarehouse(wh)"
					>
						<div class="flex items-start gap-3">
							<div
								class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
								:class="
									wh.is_group
										? 'bg-blue-100 dark:bg-blue-900/30'
										: 'bg-gray-100 dark:bg-warm-dark-900'
								"
							>
								<svg
									class="w-5 h-5"
									:class="
										wh.is_group
											? 'text-blue-600 dark:text-blue-400'
											: 'text-gray-500'
									"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
									/>
								</svg>
							</div>
							<div class="flex-1 min-w-0">
								<div
									class="text-sm font-bold text-gray-900 dark:text-white truncate"
								>
									{{ wh.warehouse_name }}
								</div>
								<div class="text-[10px] text-gray-500 truncate">
									{{ wh.parent_warehouse || 'Root' }}
								</div>
								<div class="flex items-center gap-3 mt-2">
									<div>
										<span class="text-[10px] text-gray-500">Items</span>
										<p class="text-sm font-bold text-gray-900 dark:text-white">
											{{ wh.item_count }}
										</p>
									</div>
									<div>
										<span class="text-[10px] text-gray-500">Value</span>
										<p class="text-sm font-bold text-[#D4AF37]">
											${{
												Number(wh.total_value || 0).toLocaleString(
													'en-US',
													{ maximumFractionDigits: 0 }
												)
											}}
										</p>
									</div>
								</div>
							</div>
							<span
								v-if="wh.is_group"
								class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
								>Group</span
							>
						</div>
					</div>
				</div>
			</div>
			<div
				v-if="detailWh"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="detailWh = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">
							{{ detailWh.warehouse?.warehouse_name }}
						</h3>
						<button
							@click="detailWh = null"
							class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"
						>
							<svg
								class="w-5 h-5 text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
					<div v-if="detailWh.children?.length" class="mb-4">
						<h4 class="text-[10px] font-bold text-gray-500 uppercase mb-2">
							Sub-locations
						</h4>
						<div class="flex flex-wrap gap-2">
							<span
								v-for="c in detailWh.children"
								:key="c.name"
								class="text-[10px] font-bold px-2 py-1 rounded-full bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300"
								>{{ c.warehouse_name }}</span
							>
						</div>
					</div>
					<div v-if="detailWh.items?.length">
						<h4 class="text-[10px] font-bold text-gray-500 uppercase mb-2">
							Items ({{ detailWh.items.length }})
						</h4>
						<div class="max-h-60 overflow-y-auto">
							<div
								v-for="item in detailWh.items"
								:key="item.item_code"
								class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
							>
								<div>
									<div class="text-xs font-bold text-gray-900 dark:text-white">
										{{ item.item_name }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ item.item_code }}
									</div>
								</div>
								<div class="text-right">
									<div class="text-xs font-bold text-gray-900 dark:text-white">
										{{ item.actual_qty }} pcs
									</div>
									<div class="text-[10px] text-[#D4AF37]">
										${{ Number(item.value || 0).toFixed(2) }}
									</div>
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
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'
const stock = useStockStore()
const detailWh = ref(null)
function loadData() {
	stock.loadWarehouses()
}
function viewWarehouse(wh) {
	stock.loadWarehouseDetail(wh.name).then(() => {
		detailWh.value = stock.currentWarehouse
	})
}
onMounted(loadData)
</script>
