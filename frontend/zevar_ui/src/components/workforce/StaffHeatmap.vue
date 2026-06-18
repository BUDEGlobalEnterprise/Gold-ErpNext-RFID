<template>
	<div class="premium-card !p-3 sm:!p-5">
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">{{ title }}</h3>
		<div v-if="loading" class="h-64 flex items-center justify-center">
			<span class="material-symbols-outlined animate-spin text-gray-300">progress_activity</span>
		</div>
		<EChart
			v-else-if="data.length"
			:option="chartOption"
			:height="height"
		/>
		<p v-else class="text-xs text-gray-400 text-center py-8">No staffing data</p>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import EChart from '@/components/charts/EChart.vue'

const props = defineProps({
	data: { type: Array, default: () => [] },
	title: { type: String, default: 'Sales vs Staffing Heatmap' },
	height: { type: String, default: '260px' },
	loading: { type: Boolean, default: false },
})

const chartOption = computed(() => {
	const hours = props.data.map((d) => `${d.hour}:00`)
	const salesValues = props.data.map((d) => d.sales || 0)
	const staffValues = props.data.map((d) => d.staff_count || 0)

	return {
		grid: { left: 8, right: 8, top: 24, bottom: 8, containLabel: true },
		tooltip: {
			trigger: 'axis',
			backgroundColor: 'rgba(17, 24, 39, 0.95)',
			borderColor: 'rgba(255,255,255,0.1)',
			textStyle: { color: '#f3f4f6', fontSize: 11 },
		},
		legend: {
			data: ['Sales', 'Staff Count'],
			textStyle: { fontSize: 10, color: '#9ca3af' },
			top: 0,
		},
		xAxis: {
			type: 'category',
			data: hours,
			axisLabel: { fontSize: 10, color: '#9ca3af' },
			axisLine: { lineStyle: { color: '#374151' } },
		},
		yAxis: [
			{
				type: 'value',
				name: 'Sales ($)',
				splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
				axisLabel: {
					fontSize: 10,
					color: '#9ca3af',
					formatter: (v) => '$' + (v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v),
				},
			},
			{
				type: 'value',
				name: 'Staff',
				splitLine: { show: false },
				axisLabel: { fontSize: 10, color: '#9ca3af' },
			},
		],
		series: [
			{
				name: 'Sales',
				type: 'bar',
				data: salesValues,
				itemStyle: { color: '#D4AF37', borderRadius: [4, 4, 0, 0] },
				barMaxWidth: 24,
			},
			{
				name: 'Staff Count',
				type: 'line',
				yAxisIndex: 1,
				data: staffValues,
				smooth: true,
				lineStyle: { color: '#6366f1', width: 2 },
				itemStyle: { color: '#6366f1' },
				symbol: 'circle',
				symbolSize: 6,
			},
		],
	}
})
</script>
