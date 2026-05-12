<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Metals Inventory</h2>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': stock.metalsResource.loading }"
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
			<div
				v-if="ratesList.length"
				class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0"
			>
				<div
					v-for="rate in ratesList.slice(0, 4)"
					:key="rate.label"
					class="premium-card !p-4"
				>
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						{{ rate.label }}
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						${{ Number(rate.price || 0).toFixed(2) }}/g
					</div>
					<div
						v-if="rate.trend"
						class="text-[10px] mt-1"
						:class="
							rate.trend === 'up'
								? 'text-emerald-500'
								: rate.trend === 'down'
								? 'text-red-500'
								: 'text-gray-500'
						"
					>
						{{ rate.trend === 'up' ? '▲' : rate.trend === 'down' ? '▼' : '—' }}
						{{ rate.change_pct || '' }}
					</div>
				</div>
			</div>
			<div class="premium-card !p-4 mb-4 flex-shrink-0">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-[10px] font-bold text-gray-500 uppercase">
							Total Metal Items
						</div>
						<div class="text-xl font-bold text-gray-900 dark:text-white">
							{{ stock.metalsTotal }}
						</div>
					</div>
					<div>
						<div class="text-[10px] font-bold text-gray-500 uppercase">
							Total Stock Value
						</div>
						<div class="text-xl font-bold text-[#D4AF37]">
							${{ totalMetalValue.toFixed(2) }}
						</div>
					</div>
				</div>
			</div>
			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.metalsResource.loading && !stock.metals.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.metals.length"
					class="text-center py-20 text-gray-400 text-sm"
				>
					No metal items found
				</div>
				<div v-else class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead>
							<tr
								class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50"
							>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Item
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden sm:table-cell"
								>
									Metal
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell"
								>
									Purity
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell"
								>
									Weight
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Stock
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Value
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="item in stock.metals"
								:key="item.item_code"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors"
							>
								<td class="px-4 py-3">
									<div class="text-xs font-bold text-gray-900 dark:text-white">
										{{ item.item_name }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ item.item_code }}
									</div>
								</td>
								<td class="px-4 py-3 hidden sm:table-cell">
									<span
										class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
										>{{ item.custom_metal_type || item.item_group }}</span
									>
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ item.custom_purity || '-' }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-mono text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ item.custom_gross_weight || '-' }}g
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold"
									:class="
										item.stock_qty > 0 ? 'text-emerald-500' : 'text-red-500'
									"
								>
									{{ item.stock_qty }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-[#D4AF37]"
								>
									${{ Number(item.current_value || 0).toFixed(2) }}
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</AppLayout>
</template>
<script setup>
import { computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'
import { useGoldStore } from '@/stores/gold.js'
const stock = useStockStore()
const goldStore = useGoldStore()
const totalMetalValue = computed(() =>
	stock.metals.reduce((s, i) => s + (i.current_value || 0) * Math.max(i.stock_qty, 0), 0)
)
const ratesList = computed(() => {
	const r = goldStore.rates || {}
	return Object.entries(r).map(([key, val]) => ({
		label: key,
		price: typeof val === 'object' ? val.rate_per_gram : val,
		trend: typeof val === 'object' ? val.trend : null,
		change_pct: typeof val === 'object' ? val.change_pct : null,
	}))
})
function loadData() {
	stock.loadMetals()
	goldStore.startPolling()
}
onMounted(loadData)
</script>
