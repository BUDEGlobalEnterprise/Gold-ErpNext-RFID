<template>
	<div class="flex flex-col gap-6">
		<SkeletonState v-if="loading" :lines="6" />
		<ErrorState v-else-if="error" :message="error" @retry="refresh" />
		<template v-else-if="data">
			<!-- Hero Metrics -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<div class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Gross Sales (GTV)</div>
					<div class="flex items-center gap-2">
						<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatCurrency(data.gtv) }}</div>
						<PeriodDeltaBadge :current="data.gtv" :previous="data.previous_period?.gtv" />
					</div>
				</div>
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<div class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Net Sales</div>
					<div class="flex items-center gap-2">
						<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatCurrency(data.net_sales) }}</div>
						<PeriodDeltaBadge :current="data.net_sales" :previous="data.previous_period?.net_sales" />
					</div>
				</div>
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<div class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Transactions</div>
					<div class="flex items-center gap-2">
						<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ data.txn_count }}</div>
						<PeriodDeltaBadge :current="data.txn_count" :previous="data.previous_period?.txn_count" />
					</div>
				</div>
				<!-- Gross margin is admin/Accounts-only (D2). Hidden for Store Manager etc. -->
				<div
					v-if="data.gross_profit_margin_pct != null"
					class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border"
				>
					<div class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Avg Margin</div>
					<div class="flex items-center gap-2">
						<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatPct(data.gross_profit_margin_pct) }}</div>
					</div>
				</div>
			</div>

			<!-- Charts -->
			<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border h-96">
				<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Revenue Trend</h3>
				<ChartWrapper :option="trendChartOption" autoresize />
			</div>
		</template>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { useReportData } from '@/composables/useReportData'
import SkeletonState from '@/components/reports/SkeletonState.vue'
import ErrorState from '@/components/reports/ErrorState.vue'
import PeriodDeltaBadge from '@/components/reports/PeriodDeltaBadge.vue'
import ChartWrapper from '@/components/reports/ChartWrapper.vue'

const { data, loading, error, refresh } = useReportData('zevar_core.api.report_center.get_executive_overview')

const formatCurrency = (val) => {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}
const formatPct = (val) => {
	return new Intl.NumberFormat('en-US', { style: 'percent', minimumFractionDigits: 1 }).format((val || 0) / 100)
}

const trendChartOption = computed(() => {
	if (!data.value || !data.value.trend) return {}
	const dates = data.value.trend.map((t) => t.date)
	const revenues = data.value.trend.map((t) => t.revenue)

	return {
		tooltip: { trigger: 'axis' },
		xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#666' } } },
		yAxis: { type: 'value', splitLine: { lineStyle: { color: '#333' } } },
		series: [
			{
				data: revenues,
				type: 'line',
				smooth: true,
				areaStyle: {
					color: {
						type: 'linear',
						x: 0,
						y: 0,
						x2: 0,
						y2: 1,
						colorStops: [
							{ offset: 0, color: 'rgba(212, 175, 55, 0.4)' },
							{ offset: 1, color: 'rgba(212, 175, 55, 0)' },
						],
					},
				},
				itemStyle: { color: '#D4AF37' },
			},
		],
		grid: { left: 50, right: 20, top: 20, bottom: 30 },
	}
})
</script>
