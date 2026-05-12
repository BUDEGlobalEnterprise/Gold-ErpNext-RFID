<template>
	<div class="space-y-4">
		<div class="flex items-center justify-between">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white">Margin Heatmap by Category &amp; Metal</h3>
		</div>

		<div v-if="rows.length && columns.length" class="premium-card !p-4 overflow-x-auto">
			<table class="w-full text-[10px] border-collapse min-w-[500px]">
				<thead>
					<tr>
						<th class="text-left p-2 font-bold text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
							Category
						</th>
						<th
							v-for="col in columns"
							:key="col"
							class="text-center p-2 font-bold text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700"
						>
							{{ col }}
						</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="row in rows" :key="row">
						<td class="p-2 font-medium text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-800 whitespace-nowrap">
							{{ row }}
						</td>
						<td
							v-for="col in columns"
							:key="col"
							class="text-center p-2 border-b border-gray-100 dark:border-gray-800"
						>
							<span
								class="inline-block px-2 py-1 rounded text-[10px] font-bold"
								:style="cellStyle(getCellValue(row, col))"
							>
								{{ getCellValue(row, col) !== null ? getCellValue(row, col).toFixed(1) + '%' : '--' }}
							</span>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Empty state -->
		<div v-else class="premium-card !p-8 text-center">
			<p class="text-xs text-gray-400">No heatmap data available. Ensure items have category and metal type assignments.</p>
		</div>

		<!-- Legend -->
		<div class="premium-card !p-4">
			<p class="text-[10px] font-medium text-gray-500 dark:text-gray-400 mb-2">Margin Ranges</p>
			<div class="flex flex-wrap gap-3">
				<div v-for="legend in colorLegend" :key="legend.label" class="flex items-center gap-1.5">
					<div class="w-3 h-3 rounded-sm" :style="{ backgroundColor: legend.bg }"></div>
					<span class="text-[10px] text-gray-600 dark:text-gray-400">{{ legend.label }}</span>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useProfitStore } from '@/stores/profit'

const store = useProfitStore()

const colorLegend = [
	{ label: '> 45%', bg: '#10b981' },
	{ label: '35 - 45%', bg: '#84cc16' },
	{ label: '25 - 35%', bg: '#eab308' },
	{ label: '15 - 25%', bg: '#f97316' },
	{ label: '< 15%', bg: '#ef4444' },
]

const rows = computed(() => {
	const data = store.heatmap
	if (!data || !Array.isArray(data)) return []
	return data.map((r) => r.jewelry_type || r.category || '').filter(Boolean)
})

const columns = computed(() => {
	const data = store.heatmap
	if (!data || !Array.isArray(data) || data.length === 0) return []
	// Collect all unique metal keys from the first row's margins object
	const keys = new Set()
	data.forEach((row) => {
		if (row.margins && typeof row.margins === 'object') {
			Object.keys(row.margins).forEach((k) => keys.add(k))
		}
	})
	return Array.from(keys)
})

function getCellValue(rowLabel, metalType) {
	const data = store.heatmap
	if (!data || !Array.isArray(data)) return null
	const row = data.find(
		(r) => (r.jewelry_type || r.category || '') === rowLabel
	)
	if (!row || !row.margins || !row.margins[metalType]) return null
	return row.margins[metalType].margin_pct ?? row.margins[metalType]
}

function cellStyle(value) {
	if (value === null || value === undefined) {
		return { backgroundColor: '#f3f4f6', color: '#9ca3af' }
	}
	if (value > 45) return { backgroundColor: '#10b981', color: '#fff' }
	if (value > 35) return { backgroundColor: '#84cc16', color: '#fff' }
	if (value > 25) return { backgroundColor: '#eab308', color: '#1f2937' }
	if (value > 15) return { backgroundColor: '#f97316', color: '#fff' }
	return { backgroundColor: '#ef4444', color: '#fff' }
}
</script>
