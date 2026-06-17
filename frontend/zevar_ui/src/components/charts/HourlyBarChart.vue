<template>
	<!-- HourlyBarChart (Q9) — replaces the bespoke CSS/SVG hourly bars in
	     Revenue / EmployeeLiveMonitor / Command Center. -->
	<EChart :option="option" :height="height" />
</template>

<script setup>
import { computed } from 'vue'
import EChart from './EChart.vue'

const props = defineProps({
	// [{ hour: 0..23, count, revenue }, ...] (sales_monitor.get_hourly shape)
	data: { type: Array, required: true },
	metric: { type: String, default: 'revenue' }, // 'revenue' | 'count'
	height: { type: String, default: '240px' },
	color: { type: String, default: '#6366f1' },
})

const fmtMoney = (v) => Number(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const option = computed(() => {
	const labels = props.data.map((d) => `${String(d.hour).padStart(2, '0')}`)
	const values = props.data.map((d) => Number(d[props.metric] || 0))
	return {
		grid: { left: 8, right: 8, top: 16, bottom: 8, containLabel: true },
		tooltip: {
			trigger: 'axis',
			formatter: (params) =>
				`${params[0].name}:00 → ${props.metric === 'revenue' ? fmtMoney(params[0].value) : params[0].value}`,
		},
		xAxis: {
			type: 'category',
			data: labels,
			axisLabel: { fontSize: 10, color: '#9ca3af' },
			axisLine: { lineStyle: { color: '#374151' } },
		},
		yAxis: {
			type: 'value',
			splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
			axisLabel: { fontSize: 10, color: '#9ca3af' },
		},
		series: [
			{
				type: 'bar',
				data: values,
				itemStyle: { color: props.color, borderRadius: [4, 4, 0, 0] },
				barMaxWidth: 22,
			},
		],
	}
})
</script>
