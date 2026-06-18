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
	title: { type: String, default: 'Category Breakdown' },
	height: { type: String, default: '260px' },
	loading: { type: Boolean, default: false },
})

const chartOption = computed(() => {
	const total = props.data.reduce((sum, d) => sum + (d.revenue || 0), 0) || 1
	return {
		tooltip: {
			trigger: 'item',
			backgroundColor: 'rgba(17, 24, 39, 0.95)',
			borderColor: 'rgba(255,255,255,0.1)',
			textStyle: { color: '#f3f4f6', fontSize: 11 },
			formatter: (p) =>
				`<div style="font-weight:bold">${p.name}</div><div>$${Number(p.value).toLocaleString('en-US', { minimumFractionDigits: 2 })} (${p.percent}%)</div>`,
		},
		legend: {
			orient: 'vertical',
			right: 0,
			top: 'center',
			textStyle: { fontSize: 10, color: '#9ca3af' },
			itemWidth: 10,
			itemHeight: 10,
			itemGap: 8,
		},
		series: [
			{
				type: 'pie',
				radius: ['45%', '70%'],
				center: ['40%', '50%'],
				data: props.data.map((d) => ({
					name: d.dimension || d.category || 'Other',
					value: d.revenue || 0,
				})),
				label: { show: false },
				itemStyle: {
					borderRadius: 6,
					borderColor: 'transparent',
					borderWidth: 2,
				},
				emphasis: {
					itemStyle: {
						shadowBlur: 10,
						shadowOffsetX: 0,
						shadowColor: 'rgba(0, 0, 0, 0.3)',
					},
				},
			},
		],
		color: ['#D4AF37', '#10b981', '#6366f1', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'],
	}
})
</script>
