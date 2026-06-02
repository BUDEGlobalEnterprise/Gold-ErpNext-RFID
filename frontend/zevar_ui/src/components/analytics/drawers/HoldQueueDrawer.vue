<template>
	<DetailListDrawer
		title="Active Hold Queue"
		:items="items"
		:columns="[{ key: 'reservation' }, { key: 'customer' }, { key: 'item' }, { key: 'hold_until' }]"
		:empty="`No active holds.`"
	>
		<template #row="{ row }">
			<div class="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]">
				<div class="col-span-3 font-mono text-xs">{{ row.reservation || row.name }}</div>
				<div class="col-span-3 text-xs truncate">{{ row.customer }}</div>
				<div class="col-span-3 text-xs truncate font-mono">{{ row.item || row.item_code }}</div>
				<div class="col-span-3 text-[10px] font-mono text-right text-gray-500">{{ row.hold_until }}</div>
			</div>
		</template>
	</DetailListDrawer>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import DetailListDrawer from './DetailListDrawer.vue'

const items = ref([])
onMounted(async () => {
	try {
		const res = await call('zevar_core.api.analytics_hub.get_hold_queue', {})
		items.value = res?.active_holds || []
	} catch (e) {
		console.error('HoldQueueDrawer load:', e)
	}
})
</script>
