<template>
	<div class="space-y-4">
		<!-- Toggle -->
		<div class="flex items-center justify-between">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white">
				Cost Component Breakdown
			</h3>
			<div
				class="flex rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
			>
				<button
					@click="mode = 'absolute'"
					:class="[
						mode === 'absolute'
							? 'bg-indigo-600 text-white'
							: 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400',
						'px-3 py-1 text-[10px] font-medium transition-colors',
					]"
				>
					Absolute
				</button>
				<button
					@click="mode = 'percent'"
					:class="[
						mode === 'percent'
							? 'bg-indigo-600 text-white'
							: 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400',
						'px-3 py-1 text-[10px] font-medium transition-colors',
					]"
				>
					Percentage
				</button>
			</div>
		</div>

		<!-- Chart -->
		<div v-if="periods.length" class="premium-card !p-5 space-y-3">
			<div v-for="period in periods" :key="period.label" class="space-y-1">
				<div class="flex items-center justify-between">
					<span class="text-[10px] font-medium text-gray-500 dark:text-gray-400">{{
						period.label
					}}</span>
					<span
						v-if="mode === 'absolute'"
						class="text-[10px] font-bold text-gray-900 dark:text-white"
					>
						{{ fmtCurrency(period.total) }}
					</span>
					<span v-else class="text-[10px] font-bold text-gray-900 dark:text-white"
						>100%</span
					>
				</div>
				<div class="flex w-full h-6 rounded overflow-hidden bg-gray-100 dark:bg-gray-800">
					<div
						v-for="seg in period.segments"
						:key="seg.key"
						:style="{ width: seg.width + '%' }"
						:class="segmentColor(seg.key)"
						class="h-full transition-all duration-300 flex items-center justify-center"
					>
						<span
							v-if="seg.width > 8"
							class="text-[8px] font-bold text-white truncate px-0.5"
						>
							{{ mode === 'percent' ? seg.pctLabel : fmtCompact(seg.value) }}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Empty state -->
		<div v-else class="premium-card !p-8 text-center">
			<p class="text-xs text-gray-400">
				No cost trend data available for the selected period.
			</p>
		</div>

		<!-- Legend -->
		<div class="premium-card !p-4">
			<div class="flex flex-wrap gap-x-4 gap-y-2">
				<div v-for="comp in legendItems" :key="comp.key" class="flex items-center gap-1.5">
					<div :class="[comp.colorClass, 'w-3 h-3 rounded-sm']"></div>
					<span class="text-[10px] text-gray-600 dark:text-gray-400">{{
						comp.label
					}}</span>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useProfitStore } from '@/stores/profit'
import { useFormatters } from '@/composables/useFormatters'

const store = useProfitStore()
const { formatCurrency } = useFormatters()

const mode = ref('absolute') // 'absolute' | 'percent'

const COST_KEYS = [
	{ key: 'metal_cogs', label: 'Metal COGS', colorClass: 'bg-amber-500' },
	{ key: 'gemstone_cogs', label: 'Gemstone COGS', colorClass: 'bg-purple-500' },
	{ key: 'labor', label: 'Labor', colorClass: 'bg-blue-500' },
	{ key: 'commission', label: 'Commission', colorClass: 'bg-emerald-500' },
	{ key: 'payment_cost', label: 'Payment', colorClass: 'bg-orange-500' },
	{ key: 'overhead', label: 'Overhead', colorClass: 'bg-gray-400' },
]

const legendItems = COST_KEYS

function segmentColor(key) {
	const match = COST_KEYS.find((c) => c.key === key)
	return match ? match.colorClass : 'bg-gray-300'
}

const periods = computed(() => {
	const data = store.costTrends
	if (!data || !Array.isArray(data) || data.length === 0) return []

	return data.map((period) => {
		const segments = COST_KEYS.map((comp) => {
			const value = period[comp.key] || 0
			return { key: comp.key, value }
		})

		const total = segments.reduce((sum, s) => sum + s.value, 0) || 1

		return {
			label: period.period || period.week || '',
			total,
			segments: segments.map((s) => ({
				...s,
				width: (s.value / total) * 100,
				pctLabel: ((s.value / total) * 100).toFixed(0) + '%',
			})),
		}
	})
})

function fmtCurrency(v) {
	if (!v && v !== 0) return '$0.00'
	return formatCurrency(v, { compact: Math.abs(v) >= 10000 })
}

function fmtCompact(v) {
	if (!v && v !== 0) return '$0'
	if (Math.abs(v) >= 1000) return '$' + (v / 1000).toFixed(1) + 'k'
	return '$' + v.toFixed(0)
}
</script>
