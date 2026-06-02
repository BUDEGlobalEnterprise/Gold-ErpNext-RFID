<template>
	<div class="space-y-4">
		<div>
			<h4 class="text-[10px] font-black uppercase tracking-wider text-gray-500 mb-2">Repairs ({{ repairList.length }})</h4>
			<DetailListDrawer
				title="Overdue Repairs"
				:items="repairList"
				:columns="[{ key: 'name' }, { key: 'customer' }, { key: 'balance_due' }, { key: 'ready_for_pickup_date' }]"
				:empty="`No overdue repairs.`"
				inline
			/>
		</div>
		<div>
			<h4 class="text-[10px] font-black uppercase tracking-wider text-gray-500 mb-2">Layaways ({{ layawayList.length }})</h4>
			<DetailListDrawer
				title="Overdue Layaways"
				:items="layawayList"
				:columns="[{ key: 'name' }, { key: 'customer' }, { key: 'outstanding_amount' }, { key: 'next_payment_due' }]"
				:empty="`No overdue layaways.`"
				inline
			/>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import DetailListDrawer from './DetailListDrawer.vue'

const repairList = ref([])
const layawayList = ref([])

onMounted(async () => {
	try {
		const res = await call('zevar_core.api.analytics_hub.get_overdue_payments', { type: 'all' })
		repairList.value = res?.repairs || []
		layawayList.value = res?.layaways || []
	} catch (e) {
		console.error('OverdueDrawer load:', e)
	}
})
</script>
