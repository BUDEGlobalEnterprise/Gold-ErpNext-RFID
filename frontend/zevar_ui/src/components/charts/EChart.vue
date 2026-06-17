<template>
	<!--
		EChart — the single registered ECharts wrapper for the monitor suite (Q9).
		All dashboards import this instead of pulling in vue-echarts + echarts/core
		themselves, so chart-module registration happens in exactly one place.

		Usage:
		  <EChart :option="myEchartsOption" height="260px" />
	-->
	<v-chart
		class="echart"
		:option="option"
		:autoresize="true"
		:loading="loading"
		:style="{ height, width }"
	/>
</template>

<script setup>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart, ScatterChart, HeatmapChart, FunnelChart } from 'echarts/charts'
import {
	DataZoomComponent,
	GridComponent,
	LegendComponent,
	MarkLineComponent,
	MarkPointComponent,
	TitleComponent,
	TooltipComponent,
	VisualMapComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'

// Register every chart type / component the suite uses, once.
use([
	CanvasRenderer,
	BarChart,
	LineChart,
	PieChart,
	ScatterChart,
	HeatmapChart,
	FunnelChart,
	GridComponent,
	TooltipComponent,
	LegendComponent,
	TitleComponent,
	DataZoomComponent,
	VisualMapComponent,
	MarkLineComponent,
	MarkPointComponent,
])

defineProps({
	option: { type: Object, required: true },
	height: { type: String, default: '260px' },
	width: { type: String, default: '100%' },
	loading: { type: Boolean, default: false },
})
</script>

<style scoped>
.echart {
	min-height: 80px;
}
</style>
