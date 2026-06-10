<template>
	<div class="rounded-xl p-4 border" :class="bgClass">
		<div class="flex items-center gap-2 mb-1">
			<span class="material-symbols-outlined !text-base" :class="iconClass">{{ icon }}</span>
			<span class="text-[9px] font-bold uppercase tracking-wide" :class="labelClass">{{
				label
			}}</span>
		</div>
		<div
			v-if="loading"
			class="h-6 w-24 rounded bg-gray-200 dark:bg-gray-700 animate-pulse"
		></div>
		<p v-else class="text-lg font-black" :class="valueClass">{{ value }}</p>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	label: { type: String, required: true },
	value: { type: [String, Number], required: true },
	icon: { type: String, default: 'analytics' },
	color: { type: String, default: 'gray' },
	loading: { type: Boolean, default: false },
})

const colors = {
	emerald: {
		bg: 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-100 dark:border-emerald-800/30',
		icon: 'text-emerald-500',
		label: 'text-emerald-600 dark:text-emerald-400',
		value: 'text-emerald-700 dark:text-emerald-300',
	},
	blue: {
		bg: 'bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800/30',
		icon: 'text-blue-500',
		label: 'text-blue-600 dark:text-blue-400',
		value: 'text-blue-700 dark:text-blue-300',
	},
	purple: {
		bg: 'bg-purple-50 dark:bg-purple-900/20 border-purple-100 dark:border-purple-800/30',
		icon: 'text-purple-500',
		label: 'text-purple-600 dark:text-purple-400',
		value: 'text-purple-700 dark:text-purple-300',
	},
	amber: {
		bg: 'bg-amber-50 dark:bg-amber-900/20 border-amber-100 dark:border-amber-800/30',
		icon: 'text-amber-500',
		label: 'text-amber-600 dark:text-amber-400',
		value: 'text-amber-700 dark:text-amber-300',
	},
	red: {
		bg: 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-800/30',
		icon: 'text-red-500',
		label: 'text-red-600 dark:text-red-400',
		value: 'text-red-700 dark:text-red-300',
	},
	slate: {
		bg: 'bg-slate-50 dark:bg-slate-900/20 border-slate-100 dark:border-slate-800/30',
		icon: 'text-slate-500',
		label: 'text-slate-600 dark:text-slate-400',
		value: 'text-slate-700 dark:text-slate-300',
	},
	gray: {
		bg: 'bg-gray-50 dark:bg-gray-800 border-gray-100 dark:border-gray-700',
		icon: 'text-gray-500',
		label: 'text-gray-600 dark:text-gray-400',
		value: 'text-gray-700 dark:text-gray-300',
	},
}

const bgClass = computed(() => (colors[props.color] || colors.gray).bg)
const iconClass = computed(() => (colors[props.color] || colors.gray).icon)
const labelClass = computed(() => (colors[props.color] || colors.gray).label)
const valueClass = computed(() => (colors[props.color] || colors.gray).value)
</script>
