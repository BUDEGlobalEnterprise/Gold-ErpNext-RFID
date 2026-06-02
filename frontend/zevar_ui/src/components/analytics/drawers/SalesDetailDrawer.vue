<template>
	<DetailListDrawer
		title="Daily Sales Detail"
		:items="items"
		:columns="columns"
		:empty="`No sales recorded for today.`"
	/>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import DetailListDrawer from './DetailListDrawer.vue'

const props = defineProps({ payload: { type: Object, default: () => ({}) } })

const items = ref([])
const loading = ref(true)

const columns = [
	{ key: 'name', label: 'Invoice', mono: true },
	{ key: 'customer', label: 'Customer' },
	{ key: 'grand_total', label: 'Total', mono: true, align: 'right', format: 'currency' },
	{ key: 'posting_time', label: 'Time', mono: true },
]

onMounted(async () => {
	loading.value = true
	try {
		const res = await call('frappe.client.get_list', {
			doctype: 'Sales Invoice',
			filters: { docstatus: 1, is_pos: 1 },
			fields: ['name', 'customer_name', 'grand_total', 'posting_date'],
			limit_page_length: 50,
			order_by: 'creation desc',
		})
		items.value = res || []
	} catch (e) {
		console.error('SalesDetailDrawer load:', e)
	} finally {
		loading.value = false
	}
})
</script>
