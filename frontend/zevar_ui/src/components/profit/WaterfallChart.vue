<template>
	<div class="premium-card !p-3 sm:!p-5">
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">{{ title }}</h3>
		<div v-if="loading" class="h-64 flex items-center justify-center">
			<span class="material-symbols-outlined animate-spin text-gray-300">progress_activity</span>
		</div>
		<EChart
			v-else-if="steps.length"
			:option="chartOption"
			:height="height"
		/>
		<p v-else class="text-xs text-gray-400 text-center py-8">No waterfall data</p>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import EChart from '@/components/charts/EChart.vue'

const props = defineProps({
	steps: { type: Array, default: () => [] },
	title: { type: String, default: 'Profit Waterfall' },
	height: { type: String, default: '300px' },
	loading: { type: Boolean, default: false },
})

const chartOption = computed(() => {
	const labels = props.steps.map((s) => s.label)
	const values = props.steps.map((s) => s.value)

	// Build waterfall: transparent base + colored bar
	const base = []
	const positives = []
	const negatives = []
	let running = 0

	for (const step of props.steps) {
		const v = step.value
		if (step.type === 'start' || step.type === 'end') {
			base.push(0)
			if (v >= 0) {
				positives.push(v)
				negatives.push('-')
			} else {
				positives.push('-')
				negatives.push(Math.abs(v))
			}
			running = v
		} else if (v <= 0) {
			base.push(running + v)
			positives.push('-')
			negatives.push(Math.abs(v))
			running += v
		} else {
			base.push(running)
			positives.push(v)
			negatives.push('-')
			running += v
		}
	}

	return {
		grid: { left: 8, right: 8, top: 16, bottom: 8, containLabel: true },
		tooltip: {
			trigger: 'axis',
			backgroundColor: 'rgba(17, 24, 39, 0.95)',
			borderColor: 'rgba(255,255,255,0.1)',
			textStyle: { color: '#f3f4f6', fontSize: 11 },
			formatter: (params) => {
				const p = params[0]
				const idx = p.dataIndex
				const step = props.steps[idx]
				return `<div style="font-weight:bold">${step.label}</div><div>$${Math.abs(step.value).toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>`
			},
		},
		xAxis: {
			type: 'category',
			data: labels,
			axisLabel: { fontSize: 9, color: '#9ca3af', rotate: 30 },
			axisLine: { lineStyle: { color: '#374151' } },
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
				type: 'bar',
				stack: 'waterfall',
				data: base,
				itemStyle: { color: 'transparent' },
				emphasis: { itemStyle: { color: 'transparent' } },
			},
			{
				type: 'bar',
				stack: 'waterfall',
				data: positives,
				itemStyle: {
					color: (params) => {
						const step = props.steps[params.dataIndex]
						return step.type === 'start' || step.type === 'end' ? '#6366f1' : '#10b981'
					},
					borderRadius: [4, 4, 0, 0],
				},
				barMaxWidth: 40,
			},
			{
				type: 'bar',
				stack: 'waterfall',
				data: negatives,
				itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] },
				barMaxWidth: 40,
			},
		],
	}
})
</script>
