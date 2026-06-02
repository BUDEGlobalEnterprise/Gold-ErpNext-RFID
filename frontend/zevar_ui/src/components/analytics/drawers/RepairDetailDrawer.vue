<template>
	<DetailListDrawer
		title="Repair Detail"
		:items="items"
		:columns="columns"
		:empty="`No repairs delivered today.`"
	/>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import DetailListDrawer from './DetailListDrawer.vue'

const items = ref([])
const columns = [
	{ key: 'name', label: 'Order', mono: true },
	{ key: 'customer', label: 'Customer' },
	{ key: 'grand_total', label: 'Total', mono: true, align: 'right', format: 'currency' },
	{ key: 'workflow_state', label: 'State' },
]

onMounted(async () => {
	try {
		const res = await call('frappe.client.get_list', {
			doctype: 'Repair Order',
			filters: { docstatus: 1, workflow_state: 'Delivered' },
			fields: ['name', 'customer', 'grand_total', 'workflow_state'],
			limit_page_length: 50,
			order_by: 'modified desc',
		})
		items.value = res || []
	} catch (e) {
		console.error('RepairDetailDrawer load:', e)
	}
})
</script>
