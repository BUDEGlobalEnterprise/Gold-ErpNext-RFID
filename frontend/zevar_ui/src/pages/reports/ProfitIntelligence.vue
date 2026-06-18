<template>
	<div class="flex flex-col gap-6">
		<SkeletonState v-if="loading" :lines="6" />
		<ErrorState v-else-if="error" :message="error" @retry="refresh" />
		<template v-else-if="data">
			<!-- Profit Summary -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<div class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Gross Profit</div>
					<div class="flex items-center gap-2">
						<div class="text-2xl font-bold text-green-500">{{ formatCurrency(data.summary?.gross_profit) }}</div>
					</div>
				</div>
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<div class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Average Margin</div>
					<div class="flex items-center gap-2">
						<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatPct(data.summary?.avg_margin_pct) }}</div>
					</div>
				</div>
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<div class="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Total Cost (COGS)</div>
					<div class="flex items-center gap-2">
						<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatCurrency(data.summary?.total_cost) }}</div>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Waterfall Chart -->
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border h-80">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Margin Waterfall</h3>
					<ChartWrapper :option="waterfallOption" autoresize />
				</div>
				<!-- Margin by Category -->
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border h-80">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Margin by Category</h3>
					<ChartWrapper :option="categoryOption" autoresize />
				</div>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<!-- Payment Split -->
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Payment Method Mix</h3>
					<div v-if="data.payment_split && data.payment_split.length" class="space-y-3">
						<div v-for="p in data.payment_split" :key="p.mode_of_payment" class="flex items-center justify-between">
							<div class="text-sm font-medium text-gray-900 dark:text-white">{{ p.mode_of_payment }}</div>
							<div class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatCurrency(p.amount) }}</div>
						</div>
					</div>
					<div v-else class="text-xs text-gray-500 py-4">No payments recorded for this period.</div>
				</div>
				<!-- Leakage -->
				<div class="bg-white dark:bg-[#1C1F26] p-4 rounded-lg border border-gray-100 dark:border-warm-border">
					<h3 class="text-sm font-semibold mb-4 text-gray-900 dark:text-white">Money Lost (Revenue Leakage)</h3>
					<div class="space-y-3">
						<div class="flex items-center justify-between">
							<div class="text-sm font-medium text-gray-900 dark:text-white">Discounts Given</div>
							<div class="text-sm font-semibold text-red-500">{{ formatCurrency(data.leakage?.discounts) }}</div>
						</div>
						<div class="flex items-center justify-between">
							<div class="text-sm font-medium text-gray-900 dark:text-white">Voids / Cancellations</div>
							<div class="text-sm font-semibold text-red-500">{{ formatCurrency(data.leakage?.voids) }}</div>
						</div>
						<div class="flex items-center justify-between">
							<div class="text-sm font-medium text-gray-900 dark:text-white">Returns</div>
							<div class="text-sm font-semibold text-red-500">{{ formatCurrency(data.leakage?.returns) }}</div>
						</div>
					</div>
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

const { data, loading, error, refresh } = useReportData('zevar_core.api.report_center.get_profit_intelligence_data')

const formatCurrency = (val) => {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}
const formatPct = (val) => {
	return new Intl.NumberFormat('en-US', { style: 'percent', minimumFractionDigits: 1 }).format((val || 0) / 100)
}

const waterfallOption = computed(() => {
	const wData = data.value?.waterfall
	if (!wData) return {}
	return {
		tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
		grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
		xAxis: { type: 'category', splitLine: { show: false }, data: ['Revenue', 'COGS', 'Discounts', 'Net Profit'] },
		yAxis: { type: 'value' },
		series: [
			{
				name: 'Placeholder',
				type: 'bar',
				stack: 'Total',
				itemStyle: { borderColor: 'transparent', color: 'transparent' },
				emphasis: { itemStyle: { borderColor: 'transparent', color: 'transparent' } },
				data: [0, wData.net_profit + (wData.discounts || 0), wData.net_profit, 0],
			},
			{
				name: 'Amount',
				type: 'bar',
				stack: 'Total',
				label: { show: true, position: 'top' },
				data: [
					{ value: wData.revenue, itemStyle: { color: '#3b82f6' } },
					{ value: wData.cogs, itemStyle: { color: '#ef4444' } },
					{ value: wData.discounts, itemStyle: { color: '#f59e0b' } },
					{ value: wData.net_profit, itemStyle: { color: '#10b981' } },
				],
			},
		],
	}
})

const categoryOption = computed(() => {
	const analysis = data.value?.analysis
	if (!analysis || !analysis.data) return {}
	const rows = analysis.data
	const cats = rows.map((a) => a.group_name || 'Other')
	const margins = rows.map((a) => a.margin_pct)
	return {
		tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
		xAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
		yAxis: { type: 'category', data: cats },
		series: [
			{
				data: margins,
				type: 'bar',
				itemStyle: { color: '#10b981', borderRadius: [0, 4, 4, 0] },
			},
		],
		grid: { left: 80, right: 20, top: 20, bottom: 30 },
	}
})
</script>
