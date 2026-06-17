<template>
	<DetailListDrawer
		title="Layaway Detail"
		:items="items"
		:columns="columns"
		:empty="`No active layaways.`"
	>
		<template #row="{ row }">
			<div
				class="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded hover:bg-gray-50 dark:hover:bg-[#1C1F26]"
			>
				<div class="col-span-4 font-mono text-xs">{{ row.name }}</div>
				<div class="col-span-4 text-xs truncate">{{ row.customer }}</div>
				<div class="col-span-2 text-xs font-mono text-right">
					${{ fmt(row.outstanding_amount) }}
				</div>
				<div class="col-span-2 text-[10px] text-right">
					<span
						v-if="isOverdue(row)"
						class="px-1.5 py-0.5 rounded bg-red-500/15 text-red-500 font-bold"
						>overdue</span
					>
					<span
						v-else
						class="px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-500 font-bold"
						>active</span
					>
				</div>
			</div>
		</template>
	</DetailListDrawer>
</template>

<script setup>
import { fmt } from '@/utils/format'
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'
import DetailListDrawer from './DetailListDrawer.vue'

const items = ref([])
const columns = [
	{ key: 'name' },
	{ key: 'customer' },
	{ key: 'outstanding_amount' },
	{ key: 'status' },
]

onMounted(async () => {
	try {
		const res = await call('frappe.client.get_list', {
			doctype: 'Layaway Contract',
			filters: { docstatus: 1, status: 'Active' },
			fields: ['name', 'customer', 'outstanding_amount', 'next_payment_due', 'status'],
			limit_page_length: 50,
			order_by: 'next_payment_due asc',
		})
		items.value = res || []
	} catch (e) {
		console.error('LayawayDetailDrawer load:', e)
	}
})
function isOverdue(r) {
	if (!r.next_payment_due) return false
	return new Date(r.next_payment_due) < new Date()
}
</script>
