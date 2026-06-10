<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">BOM Builder</h2>
				<div class="flex items-center gap-2">
					<input
						v-model="itemSearch"
						@input="debouncedSearch"
						type="text"
						placeholder="Search by item code..."
						class="pl-3 pr-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37] w-48"
					/>
					<button
						@click="loadBoms"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': store.bomListResource.loading }"
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

			<!-- BOM List -->
			<div v-if="store.bomList.length" class="grid gap-3 mb-6">
				<div
					v-for="bom in filteredBoms"
					:key="bom.name"
					class="bg-white dark:bg-warm-dark-800 border border-gray-200 dark:border-warm-border rounded-xl p-4 cursor-pointer hover:border-[#D4AF37] transition"
					@click="selectBom(bom)"
				>
					<div class="flex items-center justify-between">
						<div>
							<span class="text-sm font-semibold text-gray-900 dark:text-white">{{
								bom.bom_name || bom.name
							}}</span>
							<span class="ml-2 text-xs text-gray-500">{{
								bom.parent_item_code
							}}</span>
							<span
								v-if="bom.is_default"
								class="ml-2 px-1.5 py-0.5 bg-[#D4AF37]/20 text-[#D4AF37] text-[10px] font-bold rounded"
								>DEFAULT</span
							>
						</div>
						<span class="text-xs text-gray-400">Yield: {{ bom.yield_qty || 1 }}</span>
					</div>
				</div>
			</div>

			<div
				v-else-if="!store.bomListResource.loading"
				class="text-center text-gray-400 text-sm py-8"
			>
				No BOMs found. Select an item to view its BOM.
			</div>

			<!-- Selected BOM Detail -->
			<div v-if="selectedBom" class="border-t border-gray-200 dark:border-warm-border pt-4">
				<div class="flex items-center justify-between mb-3">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white">Components</h3>
					<div class="flex gap-2">
						<button
							@click="showAssemble = true"
							class="px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-bold hover:bg-green-700 transition"
						>
							Assemble
						</button>
						<button
							@click="showDisassemble = true"
							class="px-3 py-1.5 bg-red-600 text-white rounded-lg text-xs font-bold hover:bg-red-700 transition"
						>
							Disassemble
						</button>
					</div>
				</div>

				<!-- Cost Rollup -->
				<div v-if="store.bomCostRollup" class="grid grid-cols-4 gap-3 mb-4">
					<div class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 text-center">
						<div class="text-[10px] text-gray-500 uppercase">Material</div>
						<div class="text-sm font-bold text-gray-900 dark:text-white">
							${{ store.bomCostRollup.material_total }}
						</div>
					</div>
					<div class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 text-center">
						<div class="text-[10px] text-gray-500 uppercase">Labor</div>
						<div class="text-sm font-bold text-gray-900 dark:text-white">
							${{ store.bomCostRollup.labor_cost }}
						</div>
					</div>
					<div class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 text-center">
						<div class="text-[10px] text-gray-500 uppercase">Overhead</div>
						<div class="text-sm font-bold text-gray-900 dark:text-white">
							${{ store.bomCostRollup.overhead }}
						</div>
					</div>
					<div class="bg-[#D4AF37]/10 rounded-lg p-3 text-center">
						<div class="text-[10px] text-[#D4AF37] uppercase font-bold">Total</div>
						<div class="text-sm font-bold text-[#D4AF37]">
							${{ store.bomCostRollup.grand_total }}
						</div>
					</div>
				</div>

				<!-- Components table -->
				<div v-if="selectedBomComponents.length" class="overflow-x-auto">
					<table class="w-full text-xs">
						<thead>
							<tr
								class="text-left text-gray-500 border-b border-gray-200 dark:border-warm-border"
							>
								<th class="pb-2 pr-3">Type</th>
								<th class="pb-2 pr-3">Item</th>
								<th class="pb-2 pr-3">Qty</th>
								<th class="pb-2 pr-3">UOM</th>
								<th class="pb-2">Cost %</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="(c, i) in selectedBomComponents"
								:key="i"
								class="border-b border-gray-100 dark:border-warm-border/50"
							>
								<td class="py-2 pr-3">
									<span
										class="px-1.5 py-0.5 rounded text-[10px] font-bold"
										:class="componentTypeColor(c.component_type)"
									>
										{{ c.component_type }}
									</span>
								</td>
								<td class="py-2 pr-3 text-gray-900 dark:text-white">
									{{ c.component_item }}
								</td>
								<td class="py-2 pr-3">{{ c.qty_per_build }}</td>
								<td class="py-2 pr-3 text-gray-500">{{ c.uom }}</td>
								<td class="py-2 text-gray-500">{{ c.cost_share_pct }}%</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Assemble Modal -->
			<BaseModal v-if="showAssemble" @close="showAssemble = false" title="Assemble from BOM">
				<div class="p-4 space-y-3">
					<div>
						<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
							>Parent Serial No (optional)</label
						>
						<input
							v-model="assembleSerial"
							type="text"
							class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							placeholder="Scan or enter serial"
						/>
					</div>
					<div class="flex justify-end gap-2">
						<button
							@click="showAssemble = false"
							class="px-3 py-2 text-xs text-gray-600 hover:text-gray-800"
						>
							Cancel
						</button>
						<button
							@click="doAssemble"
							:disabled="store.assembleResource.loading"
							class="px-4 py-2 bg-green-600 text-white rounded-lg text-xs font-bold hover:bg-green-700 disabled:opacity-50"
						>
							{{ store.assembleResource.loading ? 'Assembling...' : 'Assemble' }}
						</button>
					</div>
				</div>
			</BaseModal>

			<!-- Disassemble Modal -->
			<BaseModal
				v-if="showDisassemble"
				@close="showDisassemble = false"
				title="Disassemble to Components"
			>
				<div class="p-4 space-y-3">
					<div>
						<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
							>Serial No to Disassemble</label
						>
						<input
							v-model="disassembleSerial"
							type="text"
							class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							placeholder="Scan or enter serial"
						/>
					</div>
					<div>
						<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
							>Reason</label
						>
						<input
							v-model="disassembleReason"
							type="text"
							class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							placeholder="Optional reason"
						/>
					</div>
					<div class="flex justify-end gap-2">
						<button
							@click="showDisassemble = false"
							class="px-3 py-2 text-xs text-gray-600 hover:text-gray-800"
						>
							Cancel
						</button>
						<button
							@click="doDisassemble"
							:disabled="store.disassembleResource.loading"
							class="px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-bold hover:bg-red-700 disabled:opacity-50"
						>
							{{
								store.disassembleResource.loading
									? 'Disassembling...'
									: 'Disassemble'
							}}
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

const itemSearch = ref('')
const selectedBom = ref(null)
const selectedBomComponents = ref([])
const showAssemble = ref(false)
const showDisassemble = ref(false)
const assembleSerial = ref('')
const disassembleSerial = ref('')
const disassembleReason = ref('')

let searchTimeout = null
function debouncedSearch() {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(() => loadBoms(), 300)
}

const filteredBoms = computed(() => {
	if (!itemSearch.value) return store.bomList
	const q = itemSearch.value.toLowerCase()
	return store.bomList.filter(
		(b) =>
			(b.parent_item_code || '').toLowerCase().includes(q) ||
			(b.bom_name || '').toLowerCase().includes(q)
	)
})

function loadBoms() {
	store.loadBomList(itemSearch.value || undefined)
}

async function selectBom(bom) {
	selectedBom.value = bom
	const result = await store.loadBomDetail(bom.parent_item_code)
	if (result?.found) {
		selectedBomComponents.value = result.components || []
	}
	await store.loadBomCost(bom.name)
}

async function doAssemble() {
	if (!selectedBom.value) return
	try {
		const result = await store.assemble(selectedBom.value.name, assembleSerial.value || null)
		alert(`Assembled! Stock Entry: ${result.stock_entry}`)
		showAssemble.value = false
		assembleSerial.value = ''
	} catch (e) {
		alert(`Error: ${e.message}`)
	}
}

async function doDisassemble() {
	if (!selectedBom.value || !disassembleSerial.value) {
		alert('Serial number is required')
		return
	}
	try {
		const result = await store.disassemble(
			disassembleSerial.value,
			selectedBom.value.name,
			disassembleReason.value
		)
		alert(`Disassembled! Recovered ${result.recovered_components?.length || 0} components`)
		showDisassemble.value = false
		disassembleSerial.value = ''
		disassembleReason.value = ''
	} catch (e) {
		alert(`Error: ${e.message}`)
	}
}

function componentTypeColor(type) {
	const colors = {
		Setting: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
		'Center Stone': 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
		Melee: 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300',
		Finding: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300',
		Labor: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
	}
	return colors[type] || 'bg-gray-100 text-gray-700'
}

onMounted(() => loadBoms())
</script>
