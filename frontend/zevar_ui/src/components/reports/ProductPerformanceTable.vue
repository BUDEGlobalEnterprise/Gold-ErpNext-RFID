<template>
	<div class="premium-card !p-3 sm:!p-5">
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">{{ title }}</h3>
		<div v-if="loading" class="space-y-2">
			<div v-for="n in 3" :key="n" class="h-10 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
		</div>
		<table v-else-if="items.length" class="w-full text-xs">
			<thead>
				<tr class="text-left text-gray-400 border-b border-gray-100 dark:border-gray-800">
					<th class="py-2 font-bold">#</th>
					<th class="py-2 font-bold">Item</th>
					<th class="py-2 font-bold text-right">Units</th>
					<th class="py-2 font-bold text-right">Revenue</th>
					<th v-if="showStock" class="py-2 font-bold text-right">Stock</th>
				</tr>
			</thead>
			<tbody>
				<tr
					v-for="(item, i) in items"
					:key="item.item_code"
					class="border-b border-gray-50 dark:border-gray-800/50"
				>
					<td class="py-2 text-gray-400 font-bold">{{ i + 1 }}</td>
					<td class="py-2 font-bold text-gray-900 dark:text-white truncate max-w-[180px]">
						{{ item.item_name || item.item_code }}
					</td>
					<td class="py-2 text-right text-gray-600 dark:text-gray-300">{{ item.units_sold }}</td>
					<td
						class="py-2 text-right font-bold"
						:class="
							variant === 'top'
								? 'text-emerald-600 dark:text-emerald-400'
								: 'text-gray-600 dark:text-gray-300'
						"
					>
						${{ fmt(item.revenue) }}
					</td>
					<td v-if="showStock" class="py-2 text-right text-gray-600 dark:text-gray-300">
						{{ item.stock_qty ?? '--' }}
					</td>
				</tr>
			</tbody>
		</table>
		<p v-else class="text-xs text-gray-400 text-center py-6">{{ emptyMessage }}</p>
	</div>
</template>

<script setup>
import { fmt } from '@/utils/format'

defineProps({
	items: { type: Array, default: () => [] },
	title: { type: String, default: 'Product Performance' },
	variant: { type: String, default: 'top' },
	showStock: { type: Boolean, default: false },
	loading: { type: Boolean, default: false },
	emptyMessage: { type: String, default: 'No data available' },
})
</script>
