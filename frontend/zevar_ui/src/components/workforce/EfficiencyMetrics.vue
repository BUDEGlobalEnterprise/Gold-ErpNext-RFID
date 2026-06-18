<template>
	<div class="premium-card !p-3 sm:!p-5">
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">{{ title }}</h3>
		<div v-if="loading" class="space-y-2">
			<div v-for="n in 3" :key="n" class="h-12 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
		</div>
		<table v-else-if="data.length" class="w-full text-xs">
			<thead>
				<tr class="text-left text-gray-400 border-b border-gray-100 dark:border-gray-800">
					<th class="py-2 font-bold">Associate</th>
					<th class="py-2 font-bold text-right">Revenue</th>
					<th class="py-2 font-bold text-right">Txn</th>
					<th class="py-2 font-bold text-right">AOV</th>
					<th class="py-2 font-bold text-right">Commission</th>
				</tr>
			</thead>
			<tbody>
				<tr
					v-for="row in data"
					:key="row.employee"
					class="border-b border-gray-50 dark:border-gray-800/50"
				>
					<td class="py-2 font-bold text-gray-900 dark:text-white truncate max-w-[140px]">
						{{ row.employee_name || row.employee }}
					</td>
					<td class="py-2 text-right font-bold text-emerald-600 dark:text-emerald-400">
						${{ fmt(row.revenue) }}
					</td>
					<td class="py-2 text-right text-gray-600 dark:text-gray-300">{{ row.txn_count }}</td>
					<td class="py-2 text-right text-gray-600 dark:text-gray-300">${{ fmt(row.aov) }}</td>
					<td class="py-2 text-right text-gray-900 dark:text-white">${{ fmt(row.commission) }}</td>
				</tr>
			</tbody>
		</table>
		<p v-else class="text-xs text-gray-400 text-center py-6">No efficiency data</p>
	</div>
</template>

<script setup>
import { fmt } from '@/utils/format'

defineProps({
	data: { type: Array, default: () => [] },
	title: { type: String, default: 'Employee Efficiency' },
	loading: { type: Boolean, default: false },
})
</script>
