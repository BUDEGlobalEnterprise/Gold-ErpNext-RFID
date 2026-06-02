<template>
	<DetailListDrawer
		title="POS Sessions Today"
		:items="items"
		:columns="columns"
		:empty="`No POS sessions closed today.`"
	>
		<template #row="{ row }">
			<div class="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]">
				<div class="col-span-3 font-mono text-xs">{{ row.name }}</div>
				<div class="col-span-3 text-xs truncate">{{ row.owner }}</div>
				<div class="col-span-2 text-xs font-mono text-right">${{ fmt(row.custom_expected_cash) }}</div>
				<div class="col-span-2 text-xs font-mono text-right">${{ fmt(row.custom_counted_cash) }}</div>
				<div class="col-span-2 text-right">
					<span :class="varianceClass(row.custom_variance)" class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold">
						{{ Number(row.custom_variance || 0) >= 0 ? '+' : '' }}${{ fmt(row.custom_variance) }}
					</span>
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
	{ key: 'name' }, { key: 'owner' },
	{ key: 'custom_expected_cash' }, { key: 'custom_counted_cash' },
	{ key: 'custom_variance' },
]

onMounted(async () => {
	try {
		const res = await call('zevar_core.api.analytics_hub.get_cash_variance_today', {})
		items.value = res?.sessions || []
	} catch (e) {
		console.error('CashVarianceDrawer load:', e)
	}
})

function fmt(n) { if (n == null) return '0.00'; return Number(n).toFixed(2) }
function varianceClass(v) {
	const x = Math.abs(Number(v || 0))
	if (x < 5) return 'bg-emerald-500/15 text-emerald-500'
	if (x < 20) return 'bg-amber-500/15 text-amber-500'
	return 'bg-red-500/15 text-red-500'
}
</script>
