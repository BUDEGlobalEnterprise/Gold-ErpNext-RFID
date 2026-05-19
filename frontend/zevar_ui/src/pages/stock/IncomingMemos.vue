<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Incoming Memos</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.memosTotal }} Memos</span
					>
				</div>
				<button
					@click="loadData"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': stock.memosResource.loading }"
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
			<div class="grid grid-cols-3 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Total
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ stock.memosTotal }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Draft
					</div>
					<div class="text-2xl font-bold text-amber-500">
						{{ stock.memos.filter((m) => m.docstatus === 0).length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
						Received
					</div>
					<div class="text-2xl font-bold text-emerald-500">
						{{ stock.memos.filter((m) => m.docstatus === 1).length }}
					</div>
				</div>
			</div>
			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.memosResource.loading && !stock.memos.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.memos.length"
					class="text-center py-20 text-gray-400 text-sm"
				>
					No memos found
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
									Memo
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden sm:table-cell"
								>
									Supplier
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell"
								>
									Date
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
								v-for="m in stock.memos"
								:key="m.name"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors"
							>
								<td
									class="px-4 py-3 text-xs font-bold text-gray-900 dark:text-white"
								>
									{{ m.name }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell"
								>
									{{ m.supplier_name }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ m.posting_date }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white"
								>
									${{ Number(m.grand_total || 0).toFixed(2) }}
								</td>
								<td class="px-4 py-3 text-center">
									<span
										class="text-[9px] font-bold px-2 py-1 rounded-full"
										:class="
											m.docstatus === 1
												? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
												: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
										"
										>{{ m.docstatus === 1 ? 'Received' : 'Draft' }}</span
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
import { onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'
const stock = useStockStore()
function loadData() {
	stock.loadMemos()
}
onMounted(loadData)
</script>
