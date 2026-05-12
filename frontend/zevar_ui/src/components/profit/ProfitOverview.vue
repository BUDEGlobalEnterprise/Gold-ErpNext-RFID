<template>
	<div class="space-y-6">
		<!-- KPI Cards -->
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
			<!-- Total Revenue -->
			<div class="premium-card !p-4">
				<div class="flex items-center gap-2 mb-2">
					<div class="w-8 h-8 rounded-lg flex items-center justify-center bg-emerald-500/10">
						<span class="material-symbols-outlined !text-base text-emerald-500">payments</span>
					</div>
					<span class="text-[10px] font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Revenue</span>
				</div>
				<p class="text-lg font-bold text-gray-900 dark:text-white">{{ fmtCurrency(kpi.totalRevenue) }}</p>
				<TrendIndicator :current="kpi.totalRevenue" :previous="kpi.prevRevenue" />
			</div>

			<!-- Gross Profit -->
			<div class="premium-card !p-4">
				<div class="flex items-center gap-2 mb-2">
					<div class="w-8 h-8 rounded-lg flex items-center justify-center bg-indigo-500/10">
						<span class="material-symbols-outlined !text-base text-indigo-500">trending_up</span>
					</div>
					<span class="text-[10px] font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Gross Profit</span>
				</div>
				<p class="text-lg font-bold text-gray-900 dark:text-white">{{ fmtCurrency(kpi.grossProfit) }}</p>
				<TrendIndicator :current="kpi.grossProfit" :previous="kpi.prevProfit" />
			</div>

			<!-- Avg Margin -->
			<div class="premium-card !p-4">
				<div class="flex items-center gap-2 mb-2">
					<div class="w-8 h-8 rounded-lg flex items-center justify-center bg-amber-500/10">
						<span class="material-symbols-outlined !text-base text-amber-500">percent</span>
					</div>
					<span class="text-[10px] font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Avg Margin</span>
				</div>
				<p class="text-lg font-bold text-gray-900 dark:text-white">{{ fmtPct(kpi.avgMargin) }}</p>
				<div class="flex items-center gap-1 mt-1">
					<span
						v-if="kpi.marginChange !== 0"
						:class="[
							kpi.marginChange > 0 ? 'text-emerald-500' : 'text-red-500',
							'text-[10px] font-medium',
						]"
					>
						{{ kpi.marginChange > 0 ? '+' : '' }}{{ kpi.marginChange.toFixed(1) }}pp
					</span>
					<span v-else class="text-[10px] text-gray-400">--</span>
				</div>
			</div>

			<!-- Invoice Count -->
			<div class="premium-card !p-4">
				<div class="flex items-center gap-2 mb-2">
					<div class="w-8 h-8 rounded-lg flex items-center justify-center bg-blue-500/10">
						<span class="material-symbols-outlined !text-base text-blue-500">receipt</span>
					</div>
					<span class="text-[10px] font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Invoices</span>
				</div>
				<p class="text-lg font-bold text-gray-900 dark:text-white">{{ kpi.invoiceCount }}</p>
				<span class="text-[10px] text-gray-400">period total</span>
			</div>
		</div>

		<!-- Profit Trend Chart -->
		<div class="premium-card !p-5">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4">Monthly Profit Trend</h3>
			<div v-if="trendBars.length" class="space-y-2">
				<div
					v-for="bar in trendBars"
					:key="bar.label"
					class="flex items-center gap-3"
				>
					<span class="text-[10px] text-gray-500 dark:text-gray-400 w-12 text-right shrink-0">{{ bar.label }}</span>
					<div class="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-5 overflow-hidden">
						<div
							class="h-full rounded-full transition-all duration-500"
							:style="{ width: bar.width + '%' }"
							:class="bar.profit >= 0 ? 'bg-indigo-500' : 'bg-red-400'"
						></div>
					</div>
					<span
						class="text-[10px] font-bold shrink-0 w-16 text-right"
						:class="bar.profit >= 0 ? 'text-gray-900 dark:text-white' : 'text-red-500'"
					>
						{{ fmtCurrency(bar.profit) }}
					</span>
				</div>
			</div>
			<p v-else class="text-xs text-gray-400 text-center py-6">No trend data available</p>
		</div>
	</div>
</template>

<script setup>
import { computed, h } from 'vue'
import { useProfitStore } from '@/stores/profit'
import { useFormatters } from '@/composables/useFormatters'

const store = useProfitStore()
const { formatCurrency, formatPercentage } = useFormatters()

function fmtCurrency(v) {
	if (!v && v !== 0) return '$0.00'
	return formatCurrency(v, { compact: Math.abs(v) >= 10000 })
}
function fmtPct(v) {
	if (!v && v !== 0) return '0%'
	return formatPercentage(v)
}

const kpi = computed(() => store.kpiData || {
	totalRevenue: 0,
	grossProfit: 0,
	avgMargin: 0,
	marginChange: 0,
	invoiceCount: 0,
	prevRevenue: 0,
	prevProfit: 0,
})

const trendBars = computed(() => {
	const data = store.trends
	if (!data || !Array.isArray(data) || data.length === 0) return []

	const profits = data.map((d) => d.gross_profit || d.profit || 0)
	const maxAbs = Math.max(...profits.map(Math.abs), 1)

	return data.map((d) => ({
		label: d.period || d.month || '',
		profit: d.gross_profit || d.profit || 0,
		width: Math.max(2, (Math.abs(d.gross_profit || d.profit || 0) / maxAbs) * 100),
	}))
})

// Tiny inline component for trend arrows
const TrendIndicator = {
	props: {
		current: { type: Number, default: 0 },
		previous: { type: Number, default: 0 },
	},
	setup(props) {
		return () => {
			if (!props.previous) return h('span', { class: 'text-[10px] text-gray-400' }, '--')
			const change = props.previous
				? ((props.current - props.previous) / Math.abs(props.previous)) * 100
				: 0
			const isUp = change >= 0
			return h(
				'div',
				{ class: 'flex items-center gap-0.5 mt-1' },
				[
					h('span', {
						class: `material-symbols-outlined !text-xs ${isUp ? 'text-emerald-500' : 'text-red-500'}`,
					}, isUp ? 'arrow_upward' : 'arrow_downward'),
					h(
						'span',
						{
							class: `text-[10px] font-medium ${isUp ? 'text-emerald-500' : 'text-red-500'}`,
						},
						`${isUp ? '+' : ''}${change.toFixed(1)}%`
					),
				]
			)
		}
	},
}
</script>
