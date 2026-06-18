<template>
	<div class="flex flex-col gap-6">
		<SkeletonState v-if="loading" :lines="6" />
		<ErrorState v-else-if="error" :message="error" @retry="refresh" />
		<template v-else-if="data">
			<!-- Leaderboard -->
			<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
				<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Associate Leaderboard</h3>
				<div v-if="data.leaderboard && data.leaderboard.length" class="overflow-x-auto">
					<table class="w-full text-left text-sm">
						<thead class="text-xs text-gray-500 uppercase bg-gray-50 dark:bg-gray-800">
							<tr>
								<th class="px-4 py-3">Rank</th>
								<th class="px-4 py-3">Associate</th>
								<th class="px-4 py-3 text-right">Revenue</th>
								<th class="px-4 py-3 text-right">Transactions</th>
								<th class="px-4 py-3 text-right">ATV</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="(l, i) in data.leaderboard"
								:key="l.employee"
								class="border-b border-gray-100 dark:border-gray-800"
							>
								<td class="px-4 py-3 font-semibold">{{ i + 1 }}</td>
								<td class="px-4 py-3 font-medium text-gray-900 dark:text-white">{{ l.employee_name }}</td>
								<td class="px-4 py-3 text-right font-semibold">{{ formatCurrency(l.revenue) }}</td>
								<td class="px-4 py-3 text-right">{{ l.txn_count }}</td>
								<td class="px-4 py-3 text-right">{{ formatCurrency(l.atv) }}</td>
							</tr>
						</tbody>
					</table>
				</div>
				<div v-else class="text-xs text-gray-500 py-4">No associate sales recorded for this period.</div>
			</div>

			<!-- Sales vs Staffing -->
			<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
				<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Sales vs Staffing by Hour</h3>
				<div v-if="data.heatmap && data.heatmap.length" class="h-80">
					<ChartWrapper :option="heatmapOption" autoresize />
				</div>
				<div v-else class="h-40 flex items-center justify-center text-gray-500 text-sm">
					No sales or staffing data available for selected period.
				</div>
				<p class="mt-2 text-[11px] text-gray-400">Staffing is approximated from attendance records; useful for spotting understaffed peak hours.</p>
			</div>
		</template>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useReportData } from '@/composables/useReportData'
import SkeletonState from '@/components/reports/SkeletonState.vue'
import ErrorState from '@/components/reports/ErrorState.vue'
import ChartWrapper from '@/components/reports/ChartWrapper.vue'

const { data, loading, error, refresh } = useReportData('zevar_core.api.report_center.get_workforce_data')

const formatCurrency = (val) => {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

const heatmapOption = computed(() => {
	const rows = data.value?.heatmap
	if (!rows || !rows.length) return {}
	const hours = rows.map((r) => `${r.hour}:00`)
	return {
		tooltip: { trigger: 'axis' },
		legend: { data: ['Sales', 'Staff on duty'], textStyle: { color: '#999' }, top: 0 },
		xAxis: { type: 'category', data: hours },
		yAxis: [
			{ type: 'value', name: 'Sales' },
			{ type: 'value', name: 'Staff' },
		],
		series: [
			{
				name: 'Sales',
				type: 'bar',
				data: rows.map((r) => r.sales),
				itemStyle: { color: '#D4AF37', borderRadius: [4, 4, 0, 0] },
			},
			{
				name: 'Staff on duty',
				type: 'line',
				yAxisIndex: 1,
				data: rows.map((r) => r.staff_count),
				itemStyle: { color: '#60a5fa' },
				smooth: true,
			},
		],
		grid: { left: 50, right: 50, top: 30, bottom: 30 },
	}
})
</script>
