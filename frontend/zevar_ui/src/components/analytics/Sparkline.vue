<template>
	<svg
		:width="width"
		:height="height"
		:viewBox="`0 0 ${width} ${height}`"
		preserveAspectRatio="none"
		class="block"
		aria-hidden="true"
	>
		<defs>
			<linearGradient :id="`spark-grad-${uid}`" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" :stop-color="strokeColor" stop-opacity="0.35" />
				<stop offset="100%" :stop-color="strokeColor" stop-opacity="0" />
			</linearGradient>
		</defs>
		<path v-if="areaPath" :d="areaPath" :fill="`url(#spark-grad-${uid})`" />
		<path
			v-if="linePath"
			:d="linePath"
			fill="none"
			:stroke="strokeColor"
			stroke-width="1.5"
			stroke-linecap="round"
			stroke-linejoin="round"
		/>
		<text
			v-if="showAxis && points.length"
			:x="2"
			:y="height - 2"
			:fill="axisColor"
			font-size="8"
			font-family="var(--font-mono)"
		>
			{{ minLabel }}–{{ maxLabel }}
		</text>
	</svg>
</template>

<script setup>
/**
 * Sparkline — Plan §7.6, 70 LOC budget.
 * Inline 30-day sparkline, SVG-only, no chart library.
 */
import { computed } from 'vue'

const props = defineProps({
	points: { type: Array, default: () => [] },
	width: { type: Number, default: 96 },
	height: { type: Number, default: 24 },
	strokeColor: { type: String, default: 'var(--color-gold)' },
	axisColor: { type: String, default: 'rgba(255,255,255,0.4)' },
	showAxis: { type: Boolean, default: false },
})

const uid = Math.random().toString(36).slice(2, 9)

const values = computed(() =>
	props.points.map((p) => Number(p.value ?? p.total ?? p.sales ?? 0) || 0)
)
const min = computed(() => (values.value.length ? Math.min(...values.value) : 0))
const max = computed(() => (values.value.length ? Math.max(...values.value) : 1))
const range = computed(() => Math.max(1, max.value - min.value))

const linePath = computed(() => {
	if (values.value.length < 2) return ''
	const stepX = props.width / (values.value.length - 1)
	return values.value
		.map((v, i) => {
			const x = i * stepX
			const y = props.height - ((v - min.value) / range.value) * (props.height - 4) - 2
			return `${i === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
		})
		.join(' ')
})

const areaPath = computed(() => {
	if (!linePath.value) return ''
	return `${linePath.value} L ${props.width} ${props.height} L 0 ${props.height} Z`
})

const minLabel = computed(() => min.value.toFixed(0))
const maxLabel = computed(() => max.value.toFixed(0))
</script>
