<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Memo Item Status</h2>
				<div class="flex items-center gap-2">
					<select
						v-model="memoClassFilter"
						@change="loadData"
						class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs"
					>
						<option value="">All</option>
						<option value="Vendor">Vendor</option>
						<option value="Customer">Customer</option>
					</select>
					<select
						v-model="lineStatusFilter"
						@change="loadData"
						class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs"
					>
						<option value="">All Statuses</option>
						<option value="Open">Open</option>
						<option value="Sold">Sold</option>
						<option value="Returned">Returned</option>
						<option value="Lost">Lost</option>
						<option value="Damaged">Damaged</option>
					</select>
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15"
							/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Items Table -->
			<div
				class="flex-1 bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl overflow-auto"
			>
				<table class="w-full text-sm">
					<thead>
						<tr class="bg-gray-50 dark:bg-warm-dark-900 sticky top-0">
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Memo #
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Item
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Serial
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Vendor/Customer
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Class
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Line Status
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Received
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Returned
							</th>
							<th
								class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase"
							>
								Actions
							</th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="item in items"
							:key="item.name"
							class="border-t border-gray-100 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700"
						>
							<td class="px-4 py-3">
								<a
									:href="`/app/memo-contract/${item.parent}`"
									class="text-primary-600 hover:underline font-mono text-xs"
									>{{ item.parent }}</a
								>
							</td>
							<td class="px-4 py-3">{{ item.item_name }}</td>
							<td class="px-4 py-3 font-mono text-xs">
								{{ item.serial_no || '—' }}
							</td>
							<td class="px-4 py-3 text-xs">{{ item.counterparty_name }}</td>
							<td class="px-4 py-3">
								<span
									:class="
										item.memo_class === 'Vendor'
											? 'bg-blue-100 text-blue-700'
											: 'bg-purple-100 text-purple-700'
									"
									class="px-2 py-0.5 rounded text-xs font-medium"
								>
									{{ item.memo_class }}
								</span>
							</td>
							<td class="px-4 py-3">
								<span
									:class="lineStatusClass(item.line_status)"
									class="px-2 py-0.5 rounded-full text-xs font-medium"
								>
									{{ item.line_status }}
								</span>
							</td>
							<td class="px-4 py-3 text-xs text-gray-500">
								{{ formatDate(item.date_received) }}
							</td>
							<td class="px-4 py-3 text-xs text-gray-500">
								{{ formatDate(item.returned_at) }}
							</td>
							<td class="px-4 py-3 text-right">
								<button
									v-if="item.line_status === 'Open'"
									@click="returnItem(item)"
									class="text-xs text-blue-600 hover:underline mr-2"
								>
									Return
								</button>
								<button
									v-if="item.line_status === 'Open'"
									@click="markLost(item)"
									class="text-xs text-red-600 hover:underline"
								>
									Lost
								</button>
							</td>
						</tr>
						<tr v-if="!items.length">
							<td colspan="9" class="px-4 py-12 text-center text-gray-400">
								No memo items found
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'

const memoClassFilter = ref('')
const lineStatusFilter = ref('')
const items = ref([])

function lineStatusClass(s) {
	const map = {
		Open: 'bg-blue-100 text-blue-700',
		Sold: 'bg-green-100 text-green-700',
		Returned: 'bg-gray-100 text-gray-600',
		Lost: 'bg-red-100 text-red-700',
		Damaged: 'bg-amber-100 text-amber-700',
	}
	return map[s] || 'bg-gray-100 text-gray-600'
}

function formatDate(d) {
	if (!d) return '—'
	return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

async function loadData() {
	try {
		const res = await frappe.call({
			method: 'zevar_core.api.inventory_v2.list_memo_items',
			args: {
				memo_class: memoClassFilter.value || undefined,
				line_status: lineStatusFilter.value || undefined,
			},
		})
		items.value = res?.message || []
	} catch (e) {
		console.error('Failed to load memo items:', e)
	}
}

function returnItem(item) {
	/* TODO: call record_memo_partial_return */
}
function markLost(item) {
	/* TODO */
}

onMounted(loadData)
</script>
