<template>
	<DetailListDrawer
		title="Low Stock Items"
		:items="items"
		:columns="columns"
		:empty="`No items below reorder level.`"
	>
		<template #row="{ row }">
			<div
				class="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]"
			>
				<div class="col-span-4 font-mono text-xs truncate">{{ row.item_code }}</div>
				<div class="col-span-4 text-xs truncate">{{ row.item_name }}</div>
				<div class="col-span-2 text-xs font-mono text-right">{{ row.actual_qty }}</div>
				<div class="col-span-2 text-right">
					<span
						:class="sevClass(row.severity)"
						class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase"
						>{{ row.severity }}</span
					>
				</div>
			</div>
		</template>
	</DetailListDrawer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import DetailListDrawer from './DetailListDrawer.vue'

const items = ref([])
const columns = [
	{ key: 'item_code' },
	{ key: 'item_name' },
	{ key: 'actual_qty' },
	{ key: 'severity' },
]

onMounted(async () => {
	try {
		const res = await call('zevar_core.api.analytics_hub.get_low_stock_detail', {
			severity: 'all',
			limit: 100,
		})
		items.value = res?.items || []
	} catch (e) {
		console.error('LowStockDrawer load:', e)
	}
})

function sevClass(s) {
	return s === 'stockout' ? 'bg-red-500/15 text-red-500' : 'bg-amber-500/15 text-amber-500'
}
</script>
