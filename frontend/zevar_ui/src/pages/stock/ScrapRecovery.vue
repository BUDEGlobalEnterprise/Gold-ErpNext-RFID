<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Scrap Recovery Queue</h2>
				<div class="flex items-center gap-2">
					<select
						v-model="statusFilter"
						class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs"
					>
						<option value="">All Statuses</option>
						<option value="Pending">Pending Breakdown</option>
						<option value="In Progress">In Progress</option>
						<option value="Sent to Refiner">Sent to Refiner</option>
						<option value="Settled">Settled</option>
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

			<!-- Summary Cards -->
			<div class="grid grid-cols-4 gap-3 mb-6">
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4"
				>
					<div class="text-xs text-gray-500 mb-1">Pending Breakdown</div>
					<div class="text-2xl font-bold text-amber-600">{{ summary.pending }}</div>
					<div class="text-xs text-gray-400 mt-1">
						{{ summary.pendingWeight }}g total
					</div>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4"
				>
					<div class="text-xs text-gray-500 mb-1">At Refiner</div>
					<div class="text-2xl font-bold text-blue-600">{{ summary.atRefiner }}</div>
					<div class="text-xs text-gray-400 mt-1">${{ summary.atRefinerValue }}</div>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4"
				>
					<div class="text-xs text-gray-500 mb-1">Recovered (MTD)</div>
					<div class="text-2xl font-bold text-green-600">
						${{ summary.recoveredMtd }}
					</div>
					<div class="text-xs text-gray-400 mt-1">
						{{ summary.recoveredCount }} pieces
					</div>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4"
				>
					<div class="text-xs text-gray-500 mb-1">Stones Recovered</div>
					<div class="text-2xl font-bold text-purple-600">
						{{ summary.stonesRecovered }}
					</div>
					<div class="text-xs text-gray-400 mt-1">{{ summary.totalCarats }}ct total</div>
				</div>
			</div>

			<!-- Scrap Items List -->
			<div
				class="flex-1 bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl overflow-hidden"
			>
				<table class="w-full text-sm">
					<thead>
						<tr class="bg-gray-50 dark:bg-warm-dark-900">
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Serial #
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Item
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Metal
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Weight (g)
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Source
							</th>
							<th
								class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
							>
								Status
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
							v-for="item in filteredItems"
							:key="item.serial_no"
							class="border-t border-gray-100 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700"
						>
							<td class="px-4 py-3 font-mono text-xs">{{ item.serial_no }}</td>
							<td class="px-4 py-3">{{ item.item_name }}</td>
							<td class="px-4 py-3">
								<span
									class="px-2 py-0.5 rounded text-xs font-semibold"
									:style="{
										background: item.color_hex + '20',
										color: item.color_hex,
									}"
								>
									{{ item.metal }} {{ item.purity }}
								</span>
							</td>
							<td class="px-4 py-3">{{ item.weight_g }}</td>
							<td class="px-4 py-3 text-xs text-gray-500">{{ item.source_type }}</td>
							<td class="px-4 py-3">
								<span
									:class="statusClass(item.status)"
									class="px-2 py-0.5 rounded-full text-xs font-medium"
									>{{ item.status }}</span
								>
							</td>
							<td class="px-4 py-3 text-right">
								<button
									v-if="item.status === 'Pending'"
									@click="disassembleItem(item)"
									class="text-xs text-primary-600 hover:underline mr-2"
								>
									Breakdown
								</button>
								<button
									v-if="item.status === 'In Progress'"
									@click="sendToRefiner(item)"
									class="text-xs text-blue-600 hover:underline mr-2"
								>
									Send to Refiner
								</button>
								<button
									v-if="item.status === 'Sent to Refiner'"
									@click="settleItem(item)"
									class="text-xs text-green-600 hover:underline"
								>
									Settle
								</button>
							</td>
						</tr>
						<tr v-if="!filteredItems.length">
							<td colspan="7" class="px-4 py-12 text-center text-gray-400">
								No scrap items found
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'

const loading = ref(false)
const statusFilter = ref('')
const items = ref([])
const summary = ref({
	pending: 0,
	pendingWeight: 0,
	atRefiner: 0,
	atRefinerValue: 0,
	recoveredMtd: 0,
	recoveredCount: 0,
	stonesRecovered: 0,
	totalCarats: 0,
})

const filteredItems = computed(() =>
	statusFilter.value ? items.value.filter((i) => i.status === statusFilter.value) : items.value
)

function statusClass(status) {
	const map = {
		Pending: 'bg-amber-100 text-amber-700',
		'In Progress': 'bg-blue-100 text-blue-700',
		'Sent to Refiner': 'bg-purple-100 text-purple-700',
		Settled: 'bg-green-100 text-green-700',
	}
	return map[status] || 'bg-gray-100 text-gray-600'
}

async function loadData() {
	loading.value = true
	/* TODO: fetch from API */ loading.value = false
}
function disassembleItem(item) {
	/* TODO: open AssemblyDisassemblyDrawer in disassemble mode */
}
function sendToRefiner(item) {
	/* TODO: call API */
}
function settleItem(item) {
	/* TODO: call API */
}

onMounted(loadData)
</script>
