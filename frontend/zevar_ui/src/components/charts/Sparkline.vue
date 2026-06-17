<template>
	<!-- Sparkline (Q9) — small trend line for KPI cards. -->
	<EChart :option="option" :height="height" />
</template>

<script setup>
import { computed } from 'vue'
import EChart from './EChart.vue'

const props = defineProps({
	values: { type: Array, required: true }, // [number, ...]
	height: { type: String, default: '48px' },
	color: { type: String, default: '#22c55e' },
	areaColor: { type: String, default: 'rgba(34,197,94,0.15)' },
})

const option = computed(() => ({
	grid: { left: 0, right: 0, top: 4, bottom: 0 },
	xAxis: { type: 'category', show: false, data: props.values.map((_, i) => i) },
	yAxis: { type: 'value', show: false },
	tooltip: { trigger: 'axis', formatter: (p) => Number(p[0].value).toLocaleString('en-US') },
	series: [
		{
			type: 'line',
			data: props.values,
			smooth: true,
			symbol: 'none',
			lineStyle: { color: props.color, width: 2 },
			areaStyle: { color: props.areaColor },
		},
	],
}))
</script>
