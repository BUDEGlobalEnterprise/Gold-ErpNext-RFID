<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Assemblies</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.assembliesTotal }} Entries</span
					>
				</div>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': stock.assembliesResource.loading }"
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
			<div class="flex flex-wrap gap-2 mb-4">
				<button
					v-for="f in ['All', 'Manufacture', 'Repack']"
					:key="f"
					@click="
						purposeFilter = f === 'All' ? '' : f
						loadData()
					"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						(purposeFilter || 'All') === (f === 'All' && !purposeFilter ? 'All' : f)
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300'
					"
				>
					{{ f }}
				</button>
			</div>
			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.assembliesResource.loading && !stock.assemblies.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.assemblies.length"
					class="text-center py-20 text-gray-400 text-sm"
				>
					No assembly entries found
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
									Entry
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden sm:table-cell"
								>
									Purpose
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell"
								>
									Date
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden lg:table-cell"
								>
									From
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden lg:table-cell"
								>
									To
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Amount
								</th>
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Status
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="a in stock.assemblies"
								:key="a.name"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors"
							>
								<td
									class="px-4 py-3 text-xs font-bold text-gray-900 dark:text-white"
								>
									{{ a.name }}
								</td>
								<td class="px-4 py-3 hidden sm:table-cell">
									<span
										class="text-[9px] font-bold px-2 py-0.5 rounded-full"
										:class="
											a.purpose === 'Manufacture'
												? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400'
												: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
										"
										>{{ a.purpose }}</span
									>
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ a.posting_date }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell truncate max-w-[120px]"
								>
									{{ a.from_warehouse || '-' }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell truncate max-w-[120px]"
								>
									{{ a.to_warehouse || '-' }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white"
								>
									${{ Number(a.total_amount || 0).toFixed(2) }}
								</td>
								<td class="px-4 py-3 text-center">
									<span
										class="text-[9px] font-bold px-2 py-1 rounded-full"
										:class="
											a.docstatus === 1
												? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
												: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300'
										"
										>{{ a.docstatus === 1 ? 'Submitted' : 'Draft' }}</span
									>
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
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'
const stock = useStockStore()
const purposeFilter = ref('')
function loadData() {
	stock.loadAssemblies({ purpose: purposeFilter.value || undefined })
}
onMounted(loadData)
</script>
