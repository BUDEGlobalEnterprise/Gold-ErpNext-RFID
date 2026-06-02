<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">External Bench Tracker</h2>
				<div class="flex items-center gap-2">
					<select v-model="selectedVendor" @change="loadBenchData" class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white">
						<option value="">Select Vendor</option>
						<option v-for="v in vendors" :key="v" :value="v">{{ v }}</option>
					</select>
					<button @click="loadBenchData" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700" title="Refresh">
						<svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': store.benchStatusResource.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
						</svg>
					</button>
				</div>
			</div>

			<!-- Active Repairs at Bench -->
			<div v-if="benchRepairs.length" class="space-y-2 mb-6">
				<div v-for="repair in benchRepairs" :key="repair.name"
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4">
					<div class="flex items-center justify-between">
						<div>
							<div class="text-sm font-semibold text-gray-900 dark:text-white">{{ repair.name }}</div>
							<div class="text-xs text-gray-500">
								Customer: {{ repair.customer }} &middot; Status: {{ repair.status }}
							</div>
							<div class="text-xs text-gray-400 mt-1">
								Dispatched: {{ repair.external_bench_dispatched_at }}
							</div>
						</div>
						<button @click="openReceive(repair)" class="px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-bold hover:bg-green-700">
							Receive
						</button>
					</div>
				</div>
			</div>

			<div v-else-if="selectedVendor && !store.benchStatusResource.loading" class="text-center text-gray-400 text-sm py-12">
				No active repairs at this bench.
			</div>

			<div v-else-if="!selectedVendor" class="text-center text-gray-400 text-sm py-12">
				Select a vendor to view bench status.
			</div>

			<!-- Receive Modal -->
			<BaseModal v-if="showReceive" @close="showReceive = false" title="Receive from Bench">
				<div class="p-4 space-y-3">
					<div class="text-xs text-gray-500">Repair: {{ activeRepair?.name }}</div>
					<div>
						<label class="text-xs font-semibold text-gray-700 dark:text-gray-300">Invoice Reference</label>
						<input v-model="receiveInvoiceRef" type="text" class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs" />
					</div>
					<div>
						<label class="text-xs font-semibold text-gray-700 dark:text-gray-300">Bench Cost</label>
						<input v-model.number="receiveCost" type="number" step="0.01" class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs" />
					</div>
					<div class="flex justify-end gap-2">
						<button @click="showReceive = false" class="px-3 py-2 text-xs text-gray-600">Cancel</button>
						<button @click="doReceive" :disabled="store.receiveBenchResource.loading" class="px-4 py-2 bg-green-600 text-white rounded-lg text-xs font-bold disabled:opacity-50">
							Confirm Received
						</button>
					</div>
				</div>
			</BaseModal>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import BaseModal from '../../components/BaseModal.vue'
import { useInventoryV2Store } from '../../stores/inventoryV2'

const store = useInventoryV2Store()

const selectedVendor = ref('')
const vendors = ref([])
const showReceive = ref(false)
const activeRepair = ref(null)
const receiveInvoiceRef = ref('')
const receiveCost = ref(0)

const benchRepairs = computed(() => store.benchStatus?.active_repairs || [])

function loadBenchData() {
	if (!selectedVendor.value) return
	store.loadBenchStatus(selectedVendor.value)
}

function openReceive(repair) {
	activeRepair.value = repair
	receiveInvoiceRef.value = ''
	receiveCost.value = 0
	showReceive.value = true
}

async function doReceive() {
	if (!activeRepair.value) return
	try {
		await store.receiveFromBench(
			activeRepair.value.name,
			receiveInvoiceRef.value || undefined,
			receiveCost.value || undefined,
		)
		showReceive.value = false
		loadBenchData()
	} catch (e) { alert(`Error: ${e.message}`) }
}

onMounted(async () => {
	// Load vendor list from external bench vendors
	try {
		const { createResource } = await import('frappe-ui')
		const res = createResource({ url: 'zevar_core.api.inventory_v2.list_external_bench_vendors' })
		// Fallback: use stock store's vendor list
		vendors.value = []
	} catch (e) {
		// Will populate from store data
	}
})
</script>
