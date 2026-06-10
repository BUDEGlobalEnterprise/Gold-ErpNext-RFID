<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Vendor Memo Dashboard</h2>
				<div class="flex items-center gap-2">
					<select
						v-model="storeFilter"
						class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs"
					>
						<option value="">All Stores</option>
						<option v-for="s in stores" :key="s" :value="s">{{ s }}</option>
					</select>
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': loading }"
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

			<!-- KPI Strip -->
			<div class="grid grid-cols-5 gap-3 mb-6">
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4"
				>
					<div class="text-xs text-gray-500 mb-1">Open Memos</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ kpi.openCount }}
					</div>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4"
				>
					<div class="text-xs text-gray-500 mb-1">Open Value</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						${{ formatCurrency(kpi.openValue) }}
					</div>
				</div>
				<div class="bg-white dark:bg-warm-dark-800 border border-red-200 rounded-xl p-4">
					<div class="text-xs text-red-500 mb-1">90+ Days</div>
					<div class="text-2xl font-bold text-red-600">{{ kpi.aging90Count }}</div>
				</div>
				<div class="bg-white dark:bg-warm-dark-800 border border-red-200 rounded-xl p-4">
					<div class="text-xs text-red-500 mb-1">90+ Value</div>
					<div class="text-2xl font-bold text-red-600">
						${{ formatCurrency(kpi.aging90Value) }}
					</div>
				</div>
				<div class="bg-white dark:bg-warm-dark-800 border border-green-200 rounded-xl p-4">
					<div class="text-xs text-green-500 mb-1">Sold (MTD)</div>
					<div class="text-2xl font-bold text-green-600">
						${{ formatCurrency(kpi.soldMtd) }}
					</div>
				</div>
			</div>

			<!-- Vendor Aging Grid -->
			<div
				class="flex-1 bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl overflow-auto"
			>
				<table class="w-full text-sm">
					<thead>
						<tr class="bg-gray-50 dark:bg-warm-dark-900 sticky top-0">
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Vendor
							</th>
							<th
								class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase bg-green-50 dark:bg-green-900/20"
							>
								0–30d
							</th>
							<th
								class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase bg-yellow-50 dark:bg-yellow-900/20"
							>
								31–60d
							</th>
							<th
								class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase bg-orange-50 dark:bg-orange-900/20"
							>
								61–90d
							</th>
							<th
								class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase bg-red-50 dark:bg-red-900/20"
							>
								90d+
							</th>
							<th
								class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase"
							>
								Total
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
							v-for="row in vendorRows"
							:key="row.vendor"
							class="border-t border-gray-100 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700"
						>
							<td class="px-4 py-3 font-semibold">{{ row.vendor_name }}</td>
							<td
								class="px-4 py-3 text-center cursor-pointer hover:bg-green-50 dark:hover:bg-green-900/20"
								@click="drillDown(row.vendor, '0-30')"
							>
								<div class="text-sm font-semibold text-green-700">
									{{ row.buckets['0-30'].count }}
								</div>
								<div class="text-xs text-gray-400">
									${{ formatCurrency(row.buckets['0-30'].value) }}
								</div>
							</td>
							<td
								class="px-4 py-3 text-center cursor-pointer hover:bg-yellow-50 dark:hover:bg-yellow-900/20"
								@click="drillDown(row.vendor, '31-60')"
							>
								<div class="text-sm font-semibold text-yellow-700">
									{{ row.buckets['31-60'].count }}
								</div>
								<div class="text-xs text-gray-400">
									${{ formatCurrency(row.buckets['31-60'].value) }}
								</div>
							</td>
							<td
								class="px-4 py-3 text-center cursor-pointer hover:bg-orange-50 dark:hover:bg-orange-900/20"
								@click="drillDown(row.vendor, '61-90')"
							>
								<div class="text-sm font-semibold text-orange-700">
									{{ row.buckets['61-90'].count }}
								</div>
								<div class="text-xs text-gray-400">
									${{ formatCurrency(row.buckets['61-90'].value) }}
								</div>
							</td>
							<td
								class="px-4 py-3 text-center cursor-pointer hover:bg-red-50 dark:hover:bg-red-900/20"
								@click="drillDown(row.vendor, '90+')"
							>
								<div class="text-sm font-semibold text-red-700">
									{{ row.buckets['90+'].count }}
								</div>
								<div class="text-xs text-gray-400">
									${{ formatCurrency(row.buckets['90+'].value) }}
								</div>
							</td>
							<td class="px-4 py-3 text-center font-bold">{{ row.total_count }}</td>
							<td class="px-4 py-3 text-right">
								<button
									class="text-xs text-primary-600 hover:underline mr-2"
									@click="sendAgingEmail(row.vendor)"
								>
									📧 Email
								</button>
								<button
									class="text-xs text-amber-600 hover:underline"
									@click="requestReturn(row.vendor)"
								>
									↩ Return
								</button>
							</td>
						</tr>
						<tr v-if="!vendorRows.length">
							<td colspan="7" class="px-4 py-12 text-center text-gray-400">
								No open vendor memos
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

const loading = ref(false)
const storeFilter = ref('')
const stores = ref([])
const kpi = ref({ openCount: 0, openValue: 0, aging90Count: 0, aging90Value: 0, soldMtd: 0 })
const vendorRows = ref([])

function formatCurrency(v) {
	return new Intl.NumberFormat('en-US', {
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	}).format(v || 0)
}

async function loadData() {
	loading.value = true
	try {
		const res = await frappe.call({
			method: 'zevar_core.api.inventory_v2.get_memo_aging_dashboard',
			args: { memo_class: 'Vendor', store: storeFilter.value || undefined },
		})
		if (res?.message) {
			kpi.value = res.message.kpi || kpi.value
			vendorRows.value = res.message.vendors || []
		}
	} catch (e) {
		console.error('Failed to load vendor memo data:', e)
	} finally {
		loading.value = false
	}
}

function drillDown(vendor, bucket) {
	/* TODO: navigate to MemoItemStatus with vendor + bucket filter */
}
function sendAgingEmail(vendor) {
	/* TODO: call API */
}
function requestReturn(vendor) {
	/* TODO: call API */
}

onMounted(loadData)
</script>
