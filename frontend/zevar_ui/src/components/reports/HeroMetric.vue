<template>
	<div class="rounded-xl p-4 border bg-white dark:bg-gray-800/50 border-gray-100 dark:border-gray-700/50">
		<div class="flex items-center gap-2 mb-2">
			<div
				class="w-8 h-8 rounded-lg flex items-center justify-center"
				:class="iconBgClass"
			>
				<span class="material-symbols-outlined !text-base" :class="iconClass">{{ icon }}</span>
			</div>
			<span class="text-[9px] font-bold uppercase tracking-wide text-gray-400">{{ label }}</span>
		</div>
		<div v-if="loading" class="space-y-2">
			<div class="h-7 w-28 rounded bg-gray-100 dark:bg-gray-700 animate-pulse"></div>
			<div v-if="comparisonLabel" class="h-4 w-20 rounded bg-gray-100 dark:bg-gray-700 animate-pulse"></div>
		</div>
		<template v-else>
			<p class="text-xl font-black text-gray-900 dark:text-white">{{ formattedValue }}</p>
			<div
				v-if="comparisonLabel && previousValue != null"
				class="flex items-center gap-1.5 mt-1.5"
			>
				<span
					class="inline-flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full"
					:class="popBadgeClass"
				>
					<span class="material-symbols-outlined !text-[10px]">{{ popIcon }}</span>
					{{ popText }}
				</span>
				<span class="text-[9px] text-gray-400">{{ comparisonLabel }}</span>
			</div>
		</template>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	label: { type: String, required: true },
	value: { type: [String, Number], required: true },
	icon: { type: String, default: 'analytics' },
	color: { type: String, default: 'emerald' },
	loading: { type: Boolean, default: false },
	previousValue: { type: [String, Number, null], default: null },
	comparisonLabel: { type: String, default: '' },
	trend: { type: String, default: null },
	currency: { type: Boolean, default: false },
	percent: { type: Boolean, default: false },
})

const formattedValue = computed(() => {
	const v = props.value
	if (v == null) return '--'
	if (props.currency) {
		const num = parseFloat(String(v).replace(/[^0-9.\-]/g, ''))
		return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
	}
	if (props.percent) {
		const num = parseFloat(String(v).replace(/[^0-9.\-]/g, ''))
		return num.toFixed(1) + '%'
	}
	return v
})

const popDelta = computed(() => {
	if (props.previousValue == null || !props.previousValue) return null
	const current = parseFloat(String(props.value).replace(/[^0-9.\-]/g, ''))
	const previous = parseFloat(String(props.previousValue).replace(/[^0-9.\-]/g, ''))
	if (!previous) return null
	return ((current - previous) / Math.abs(previous)) * 100
})

const popText = computed(() => {
	if (popDelta.value == null) return ''
	const sign = popDelta.value >= 0 ? '+' : ''
	return `${sign}${popDelta.value.toFixed(1)}%`
})

const popIcon = computed(() => {
	if (props.trend === 'up' || (popDelta.value != null && popDelta.value > 0)) return 'trending_up'
	if (props.trend === 'down' || (popDelta.value != null && popDelta.value < 0)) return 'trending_down'
	return 'trending_flat'
})

const popBadgeClass = computed(() => {
	if (props.trend === 'up' || (popDelta.value != null && popDelta.value > 0))
		return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
	if (props.trend === 'down' || (popDelta.value != null && popDelta.value < 0))
		return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
	return 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
})

const colorMap = {
	emerald: { iconBg: 'bg-emerald-500/10', icon: 'text-emerald-500' },
	blue: { iconBg: 'bg-blue-500/10', icon: 'text-blue-500' },
	purple: { iconBg: 'bg-purple-500/10', icon: 'text-purple-500' },
	amber: { iconBg: 'bg-amber-500/10', icon: 'text-amber-500' },
	red: { iconBg: 'bg-red-500/10', icon: 'text-red-500' },
	indigo: { iconBg: 'bg-indigo-500/10', icon: 'text-indigo-500' },
	rose: { iconBg: 'bg-rose-500/10', icon: 'text-rose-500' },
}

const iconBgClass = computed(() => (colorMap[props.color] || colorMap.emerald).iconBg)
const iconClass = computed(() => (colorMap[props.color] || colorMap.emerald).icon)
</script>
