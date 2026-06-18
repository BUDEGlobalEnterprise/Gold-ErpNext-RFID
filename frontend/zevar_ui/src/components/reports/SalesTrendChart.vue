<template>
	<div class="premium-card !p-3 sm:!p-5">
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">{{ title }}</h3>
		<div v-if="loading" class="h-48 sm:h-64 flex items-center justify-center">
			<span class="material-symbols-outlined animate-spin text-gray-300">progress_activity</span>
		</div>
		<EChart
			v-else-if="data.length"
			:option="chartOption"
			:height="height"
		/>
		<p v-else class="text-xs text-gray-400 text-center py-8">No data available</p>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import EChart from '@/components/charts/EChart.vue'

const props = defineProps({
	data: { type: Array, default: () => [] },
	title: { type: String, default: 'Sales Trend' },
	height: { type: String, default: '260px' },
	loading: { type: Boolean, default: false },
	color: { type: String, default: '#D4AF37' },
})

const chartOption = computed(() => ({
	grid: { left: 8, right: 8, top: 24, bottom: 8, containLabel: true },
	tooltip: {
		trigger: 'axis',
		backgroundColor: 'rgba(17, 24, 39, 0.95)',
		borderColor: 'rgba(255,255,255,0.1)',
		textStyle: { color: '#f3f4f6', fontSize: 11 },
		formatter: (params) => {
			const p = params[0]
			return `<div style="font-weight:bold">${p.name}</div><div>$${Number(p.value).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>`
		},
	},
	xAxis: {
		type: 'category',
		data: props.data.map((d) => d.date),
		axisLabel: { fontSize: 10, color: '#9ca3af' },
		axisLine: { lineStyle: { color: '#374151' } },
		boundaryGap: false,
	},
	yAxis: {
		type: 'value',
		splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
		axisLabel: {
			fontSize: 10,
			color: '#9ca3af',
			formatter: (v) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v),
		},
	},
	series: [
		{
			type: 'line',
			data: props.data.map((d) => d.revenue),
			smooth: true,
			lineStyle: { color: props.color, width: 2 },
			itemStyle: { color: props.color },
			areaStyle: {
				color: {
					type: 'linear',
					x: 0, y: 0, x2: 0, y2: 1,
					colorStops: [
						{ offset: 0, color: props.color + '40' },
						{ offset: 1, color: props.color + '05' },
					],
				},
			},
			symbol: 'circle',
			symbolSize: 6,
		},
	],
}))
</script>
