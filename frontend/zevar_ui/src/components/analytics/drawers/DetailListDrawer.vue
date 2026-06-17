<template>
	<div :class="['detail-list', { 'detail-list--inline': inline }]">
		<div v-if="loading" class="space-y-2">
			<div
				v-for="n in 4"
				:key="n"
				class="h-8 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
			/>
		</div>
		<div v-else-if="!items.length" class="text-xs text-gray-400 text-center py-8">
			{{ empty }}
		</div>
		<div v-else class="space-y-1">
			<div
				v-if="!$slots.row && columns.length"
				class="grid gap-2 px-2 py-2 text-[10px] uppercase tracking-wider text-gray-500 border-b border-gray-200 dark:border-warm-border"
				:style="gridStyle"
			>
				<div v-for="c in columns" :key="c.key" :class="cellClass(c)">
					{{ c.label || c.key }}
				</div>
			</div>
			<div v-for="row in items" :key="rowKey(row)">
				<slot name="row" :row="row">
					<div
						class="grid gap-2 px-2 py-1.5 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]"
						:style="gridStyle"
					>
						<div v-for="c in columns" :key="c.key" :class="cellClass(c)">
							<span v-if="c.format === 'currency'"
								>${{ fmt(getVal(row, c.key)) }}</span
							>
							<span v-else>{{ getVal(row, c.key) }}</span>
						</div>
					</div>
				</slot>
			</div>
		</div>
	</div>
</template>

<script setup>
import { fmt } from '@/utils/format'
/**
 * DetailListDrawer — shared list renderer used by all 7 hub drawers.
 */
import { computed } from 'vue'

const props = defineProps({
	title: { type: String, default: '' },
	items: { type: Array, default: () => [] },
	columns: { type: Array, default: () => [] },
	empty: { type: String, default: 'Nothing to show.' },
	loading: { type: Boolean, default: false },
	inline: { type: Boolean, default: false },
})

const gridStyle = computed(() => ({
	gridTemplateColumns: `repeat(${Math.max(props.columns.length, 1)}, minmax(0, 1fr))`,
}))

function cellClass(c) {
	const a = c.align === 'right' ? 'text-right' : c.align === 'center' ? 'text-center' : ''
	const m = c.mono ? 'font-mono' : ''
	return [a, m].filter(Boolean).join(' ')
}
function getVal(row, key) {
	return row?.[key] ?? ''
}
function rowKey(row) {
	return row?.name || row?.reservation || row?.item_code || Math.random()
}
</script>
