<template>
	<div class="flex flex-col gap-6">
		<SkeletonState v-if="loading" :lines="6" />
		<ErrorState v-else-if="error" :message="error" @retry="refresh" />
		<template v-else-if="data">
			<!-- Sales Pace -->
			<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
				<h3 class="text-sm font-semibold mb-2 text-gray-900 dark:text-white">Daily Pace vs Target</h3>
				<div class="flex items-center justify-between">
					<div>
						<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatCurrency(data.pace?.revenue_so_far) }}</div>
						<div class="text-xs text-gray-500">Target: {{ formatCurrency(data.pace?.target_revenue) }}</div>
					</div>
					<div class="text-right">
						<div class="text-lg font-bold" :class="(data.pace?.run_rate || 0) >= (data.pace?.target_revenue || 0) ? 'text-green-500' : 'text-red-500'">
							{{ formatCurrency(data.pace?.run_rate) }}
						</div>
						<div class="text-xs text-gray-500">Projected Run Rate</div>
					</div>
				</div>
				<div class="mt-4 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
					<div class="h-full bg-[#D4AF37]" :style="{ width: Math.min(100, ((data.pace?.revenue_so_far || 0) / (data.pace?.target_revenue || 1)) * 100) + '%' }"></div>
				</div>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Hourly Sales -->
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border h-80">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Hourly Sales</h3>
					<ChartWrapper :option="hourlyChartOption" autoresize />
				</div>
				<!-- Category Breakdown -->
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border h-80">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Sales by Category</h3>
					<ChartWrapper :option="categoryChartOption" autoresize />
				</div>
			</div>

			<!-- Top Items and Dead Stock -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Top 5 Items</h3>
					<div class="space-y-3">
						<div v-for="(item, i) in data.top_items" :key="item.item_code" class="flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="w-6 h-6 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xs font-bold text-gray-500">{{ i + 1 }}</div>
								<div>
									<div class="text-sm font-medium text-gray-900 dark:text-white">{{ item.item_name }}</div>
									<div class="text-xs text-gray-500">{{ item.item_code }}</div>
								</div>
							</div>
							<div class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatCurrency(item.revenue) }}</div>
						</div>
					</div>
				</div>
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Dead Stock Warnings</h3>
					<div v-if="data.dead_stock && data.dead_stock.length" class="space-y-3">
						<div v-for="item in data.dead_stock" :key="item.item_code" class="flex items-center justify-between">
							<div>
								<div class="text-sm font-medium text-gray-900 dark:text-white">{{ item.item_name || item.item_code }}</div>
								<div class="text-xs text-gray-500">On hand: {{ item.stock_qty || 0 }} · 0 sold in period</div>
							</div>
							<div class="text-sm font-semibold text-red-500">{{ formatCurrency(item.revenue) }}</div>
						</div>
					</div>
					<div v-else class="text-xs text-gray-500 py-4">No dead stock for this period — every stocked item has sold.</div>
				</div>
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

const { data, loading, error, refresh } = useReportData('zevar_core.api.report_center.get_sales_monitor_data')

const formatCurrency = (val) => {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

const hourlyChartOption = computed(() => {
	if (!data.value || !data.value.hourly) return {}
	const hours = data.value.hourly.map((h) => `${h.hour}:00`)
	const revenues = data.value.hourly.map((h) => h.revenue)

	return {
		tooltip: { trigger: 'axis' },
		xAxis: { type: 'category', data: hours },
		yAxis: { type: 'value' },
		series: [
			{
				data: revenues,
				type: 'bar',
				itemStyle: { color: '#D4AF37', borderRadius: [4, 4, 0, 0] },
			},
		],
		grid: { left: 50, right: 20, top: 20, bottom: 30 },
	}
})

const categoryChartOption = computed(() => {
	if (!data.value || !data.value.breakdown) return {}
	const pieData = data.value.breakdown.map((b) => ({ name: b.dimension, value: b.revenue }))

	return {
		tooltip: { trigger: 'item' },
		legend: { orient: 'vertical', left: 'left', textStyle: { color: '#999' } },
		series: [
			{
				name: 'Sales',
				type: 'pie',
				radius: ['40%', '70%'],
				avoidLabelOverlap: false,
				itemStyle: {
					borderRadius: 4,
					borderColor: '#1C1F26',
					borderWidth: 2,
				},
				label: { show: false, position: 'center' },
				emphasis: {
					label: { show: true, fontSize: '14', fontWeight: 'bold', color: '#FFF' },
				},
				labelLine: { show: false },
				data: pieData,
			},
		],
	}
})
</script>
