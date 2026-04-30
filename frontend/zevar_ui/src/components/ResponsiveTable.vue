<template>
	<div class="responsive-table-wrapper">
		<!-- Desktop: real table (>= md) -->
		<div v-if="!bp.isMobile.value" class="hidden md:block overflow-x-auto">
			<table class="w-full text-left">
				<thead>
					<tr class="border-b border-gray-200 dark:border-warm-border/50">
						<th
							v-for="col in visibleColumns"
							:key="col.key"
							:class="[
								'px-4 py-3 text-overline text-gray-500 dark:text-gray-400 whitespace-nowrap',
								col.align === 'right'
									? 'text-right'
									: col.align === 'center'
									? 'text-center'
									: 'text-left',
								col.sticky ? 'sticky top-0 bg-white dark:bg-warm-card z-10' : '',
							]"
							:style="col.width ? { width: col.width } : {}"
						>
							{{ col.label }}
						</th>
						<th v-if="hasActions" class="px-4 py-3 w-12"></th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="(row, rowIdx) in rows"
						:key="rowKey ? row[rowKey] : rowIdx"
						class="border-b border-gray-100 dark:border-warm-border/30 hover:bg-gray-50/50 dark:hover:bg-warm-dark-700/30 transition-colors"
						:class="rowClass?.(row)"
					>
						<td
							v-for="col in visibleColumns"
							:key="col.key"
							:class="[
								'px-4 py-3 text-body-sm whitespace-nowrap',
								col.align === 'right'
									? 'text-right'
									: col.align === 'center'
									? 'text-center'
									: '',
							]"
						>
							<slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
								{{ col.format ? col.format(row[col.key], row) : row[col.key] }}
							</slot>
						</td>
						<td v-if="hasActions" class="px-4 py-3">
							<slot name="actions" :row="row" :rowIdx="rowIdx" />
						</td>
					</tr>
					<tr v-if="rows.length === 0">
						<td
							:colspan="visibleColumns.length + (hasActions ? 1 : 0)"
							class="px-4 py-12 text-center text-gray-400 dark:text-gray-600"
						>
							<slot name="empty">
								<div class="flex flex-col items-center gap-2">
									<svg
										class="w-10 h-10 opacity-30"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="1.5"
											d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
										/>
									</svg>
									<span class="text-caption">{{ emptyText }}</span>
								</div>
							</slot>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Mobile: stacked cards (< md) -->
		<div v-else class="md:hidden space-y-2">
			<div
				v-for="(row, rowIdx) in rows"
				:key="rowKey ? row[rowKey] : rowIdx"
				class="bg-white dark:bg-warm-card rounded-xl border border-gray-100 dark:border-warm-border/40 p-3"
				:class="rowClass?.(row)"
			>
				<!-- Primary field -->
				<div class="flex items-start justify-between gap-2 mb-2">
					<div class="min-w-0 flex-1">
						<slot
							:name="`mobile-primary-${primaryColumn?.key || 'name'}`"
							:row="row"
							:value="primaryColumn ? row[primaryColumn.key] : ''"
						>
							<div class="text-heading-sm text-gray-900 dark:text-white truncate">
								{{
									primaryColumn
										? primaryColumn.format
											? primaryColumn.format(row[primaryColumn.key], row)
											: row[primaryColumn.key]
										: ''
								}}
							</div>
						</slot>
						<div
							v-if="secondaryColumn"
							class="text-caption text-gray-500 dark:text-gray-400 mt-0.5 truncate"
						>
							{{
								secondaryColumn.format
									? secondaryColumn.format(row[secondaryColumn.key], row)
									: row[secondaryColumn.key]
							}}
						</div>
					</div>
					<div v-if="hasActions" class="shrink-0">
						<slot name="mobile-actions" :row="row" :rowIdx="rowIdx">
							<slot name="actions" :row="row" :rowIdx="rowIdx" />
						</slot>
					</div>
				</div>

				<!-- Secondary fields as key/value grid -->
				<div v-if="mobileFields.length > 0" class="grid grid-cols-2 gap-x-4 gap-y-1">
					<template v-for="col in mobileFields" :key="col.key">
						<div
							v-if="
								col.key !== primaryColumn?.key && col.key !== secondaryColumn?.key
							"
						>
							<slot
								:name="`mobile-cell-${col.key}`"
								:row="row"
								:value="row[col.key]"
							>
								<span class="text-caption text-gray-400 dark:text-gray-500">{{
									col.label
								}}</span>
								<div class="text-body-sm text-gray-700 dark:text-gray-300">
									{{ col.format ? col.format(row[col.key], row) : row[col.key] }}
								</div>
							</slot>
						</div>
					</template>
				</div>
			</div>

			<!-- Empty state -->
			<div
				v-if="rows.length === 0"
				class="flex flex-col items-center gap-2 py-12 text-gray-400 dark:text-gray-600"
			>
				<svg
					class="w-10 h-10 opacity-30"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="1.5"
						d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
					/>
				</svg>
				<span class="text-caption">{{ emptyText }}</span>
			</div>
		</div>

		<!-- Pagination slot -->
		<slot name="pagination" />
	</div>
</template>

<script setup>
import { computed, useSlots } from 'vue'
import { useBreakpoint } from '@/composables/useBreakpoint.js'

const props = defineProps({
	/** @type {Array<{ key: string, label: string, align?: string, width?: string, format?: Function, sticky?: boolean, primary?: boolean, secondary?: boolean, hideMobile?: boolean }>} */
	columns: { type: Array, required: true },
	/** @type {Array<Object>} */
	rows: { type: Array, default: () => [] },
	/** Unique row key field */
	rowKey: { type: String, default: 'name' },
	/** Empty state text */
	emptyText: { type: String, default: 'No records found' },
	/** Dynamic row class function */
	rowClass: { type: Function, default: null },
})

const slots = useSlots()
const bp = {
	isMobile: computed(() => {
		if (typeof window === 'undefined') return false
		return window.innerWidth < 768
	}),
}

// Use actual breakpoint composable in setup context
const { isMobile: mobileRef } = useBreakpoint()
bp.isMobile = mobileRef

const hasActions = computed(() => !!slots.actions || !!slots['mobile-actions'])

const primaryColumn = computed(() => props.columns.find((c) => c.primary) || props.columns[0])
const secondaryColumn = computed(() => props.columns.find((c) => c.secondary) || null)

const visibleColumns = computed(() => props.columns.filter((c) => !c.hidden))

const mobileFields = computed(() => props.columns.filter((c) => !c.hideMobile && !c.hidden))
</script>
