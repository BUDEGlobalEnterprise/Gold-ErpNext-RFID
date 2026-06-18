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
		<p v-else class="text-xs text-gray-400 text-center py-8">No payment data</p>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import EChart from '@/components/charts/EChart.vue'

const props = defineProps({
	data: { type: Array, default: () => [] },
	title: { type: String, default: 'Payment Methods' },
	height: { type: String, default: '260px' },
	loading: { type: Boolean, default: false },
})

const chartOption = computed(() => ({
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
	},
	series: [
		{
			type: 'pie',
			radius: ['40%', '65%'],
			center: ['35%', '50%'],
			data: props.data.map((d) => ({
				name: d.method || 'Other',
				value: d.total || 0,
			})),
			label: { show: false },
			itemStyle: {
				borderRadius: 4,
				borderColor: 'transparent',
				borderWidth: 2,
			},
		},
	],
	color: ['#10b981', '#6366f1', '#D4AF37', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'],
}))
</script>
