<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Gemstone Inventory</h2>
				<div class="flex items-center gap-2">
					<select
						v-model="statusFilter"
						@change="loadData"
						class="px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white outline-none"
					>
						<option value="">All Statuses</option>
						<option value="In Stock">In Stock</option>
						<option value="Reserved">Reserved</option>
						<option value="Mounted">Mounted</option>
						<option value="Sold">Sold</option>
					</select>
					<button
						@click="showRegister = true"
						class="flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						Register Stone
					</button>
				</div>
			</div>

			<!-- Gemstone Table -->
			<div class="flex-1 overflow-auto">
				<table v-if="store.gemstones.length" class="w-full text-xs">
					<thead class="sticky top-0 bg-white dark:bg-warm-dark-800">
						<tr
							class="text-left text-gray-500 border-b border-gray-200 dark:border-warm-border"
						>
							<th class="pb-2 pr-3">ID</th>
							<th class="pb-2 pr-3">Type</th>
							<th class="pb-2 pr-3">Shape</th>
							<th class="pb-2 pr-3">Carat</th>
							<th class="pb-2 pr-3">Color</th>
							<th class="pb-2 pr-3">Clarity</th>
							<th class="pb-2 pr-3">Cut</th>
							<th class="pb-2 pr-3">Status</th>
							<th class="pb-2">Actions</th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="gem in store.gemstones"
							:key="gem.name"
							class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50 dark:hover:bg-warm-dark-700/50"
						>
							<td class="py-2 pr-3 text-gray-900 dark:text-white font-mono">
								{{ gem.name }}
							</td>
							<td class="py-2 pr-3">{{ gem.gemstone_type }}</td>
							<td class="py-2 pr-3">{{ gem.shape }}</td>
							<td class="py-2 pr-3 font-semibold">{{ gem.carat_weight }}</td>
							<td class="py-2 pr-3">{{ gem.color || '-' }}</td>
							<td class="py-2 pr-3">{{ gem.clarity || '-' }}</td>
							<td class="py-2 pr-3">{{ gem.cut || '-' }}</td>
							<td class="py-2 pr-3">
								<span
									class="px-1.5 py-0.5 rounded text-[10px] font-bold"
									:class="statusColor(gem.status)"
								>
									{{ gem.status }}
								</span>
							</td>
							<td class="py-2">
								<button
									v-if="gem.status === 'In Stock'"
									@click="openAttach(gem)"
									class="text-[#D4AF37] text-[10px] font-bold hover:underline"
								>
									Attach
								</button>
								<button
									v-if="gem.status === 'Mounted'"
									@click="doDetach(gem)"
									class="text-red-500 text-[10px] font-bold hover:underline ml-2"
								>
									Detach
								</button>
							</td>
						</tr>
					</tbody>
				</table>

				<div
					v-else-if="!store.gemstonesResource.loading"
					class="text-center text-gray-400 text-sm py-12"
				>
					No gemstones found. Register a stone to get started.
				</div>
			</div>

			<!-- Register Modal -->
			<BaseModal v-if="showRegister" @close="showRegister = false" title="Register Gemstone">
				<div class="p-4 space-y-3">
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
								>Gemstone Type</label
							>
							<select
								v-model="form.gemstone_type"
								class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							>
								<option
									v-for="gt in store.gemstoneTypes"
									:key="gt.name"
									:value="gt.gemstone_type_name"
								>
									{{ gt.gemstone_type_name }}
								</option>
							</select>
						</div>
						<div>
							<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
								>Shape</label
							>
							<select
								v-model="form.shape"
								class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							>
								<option>Round</option>
								<option>Oval</option>
								<option>Pear</option>
								<option>Marquise</option>
								<option>Emerald</option>
								<option>Princess</option>
								<option>Cushion</option>
								<option>Radiant</option>
								<option>Asscher</option>
								<option>Heart</option>
								<option>Trillion</option>
								<option>Baguette</option>
								<option>Cabochon</option>
								<option>Briolette</option>
								<option>Fancy</option>
							</select>
						</div>
					</div>
					<div class="grid grid-cols-3 gap-3">
						<div>
							<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
								>Carat Weight</label
							>
							<input
								v-model.number="form.carat_weight"
								type="number"
								step="0.001"
								class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							/>
						</div>
						<div>
							<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
								>Color</label
							>
							<input
								v-model="form.color"
								type="text"
								class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
								placeholder="D, E, F..."
							/>
						</div>
						<div>
							<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
								>Clarity</label
							>
							<input
								v-model="form.clarity"
								type="text"
								class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
								placeholder="IF, VVS1..."
							/>
						</div>
					</div>
					<div>
						<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
							>Cert Lab (optional)</label
						>
						<input
							v-model="form.cert_lab"
							type="text"
							class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							placeholder="GIA, IGI..."
						/>
					</div>
					<div class="flex justify-end gap-2 pt-2">
						<button
							@click="showRegister = false"
							class="px-3 py-2 text-xs text-gray-600"
						>
							Cancel
						</button>
						<button
							@click="doRegister"
							:disabled="store.registerGemstoneResource.loading"
							class="px-4 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold disabled:opacity-50"
						>
							Register
						</button>
					</div>
				</div>
			</BaseModal>

			<!-- Attach Modal -->
			<BaseModal v-if="showAttach" @close="showAttach = false" title="Attach to Serial">
				<div class="p-4 space-y-3">
					<div>
						<label class="text-xs font-semibold text-gray-700 dark:text-gray-300"
							>Serial No</label
						>
						<input
							v-model="attachSerial"
							type="text"
							class="mt-1 w-full px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 rounded-lg text-xs"
							placeholder="Scan or enter serial"
						/>
					</div>
					<div class="flex justify-end gap-2">
						<button
							@click="showAttach = false"
							class="px-3 py-2 text-xs text-gray-600"
						>
							Cancel
						</button>
						<button
							@click="doAttach"
							class="px-4 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold"
						>
							Attach
						</button>
					</div>
				</div>
			</BaseModal>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../../components/AppLayout.vue'
import BaseModal from '../../components/BaseModal.vue'
import { useInventoryV2Store } from '../../stores/inventoryV2'

const store = useInventoryV2Store()

const statusFilter = ref('')
const showRegister = ref(false)
const showAttach = ref(false)
const attachGem = ref(null)
const attachSerial = ref('')
const form = ref({
	gemstone_type: '',
	shape: 'Round',
	carat_weight: 0,
	color: '',
	clarity: '',
	cert_lab: '',
})

function loadData() {
	store.loadGemstones(statusFilter.value || undefined)
}

function openAttach(gem) {
	attachGem.value = gem
	attachSerial.value = ''
	showAttach.value = true
}

async function doRegister() {
	try {
		await store.registerGemstone(form.value)
		showRegister.value = false
		form.value = {
			gemstone_type: '',
			shape: 'Round',
			carat_weight: 0,
			color: '',
			clarity: '',
			cert_lab: '',
		}
		loadData()
	} catch (e) {
		alert(`Error: ${e.message}`)
	}
}

async function doAttach() {
	if (!attachGem.value || !attachSerial.value) return
	try {
		await store.attachGemstone(attachGem.value.name, attachSerial.value)
		showAttach.value = false
		loadData()
	} catch (e) {
		alert(`Error: ${e.message}`)
	}
}

async function doDetach(gem) {
	if (!confirm(`Detach ${gem.name} from its serial?`)) return
	try {
		await store.detachGemstone(gem.name)
		loadData()
	} catch (e) {
		alert(`Error: ${e.message}`)
	}
}

function statusColor(status) {
	const colors = {
		'In Stock': 'bg-green-100 text-green-700',
		Reserved: 'bg-yellow-100 text-yellow-700',
		Mounted: 'bg-blue-100 text-blue-700',
		Sold: 'bg-gray-100 text-gray-500',
		Lost: 'bg-red-100 text-red-700',
	}
	return colors[status] || 'bg-gray-100 text-gray-700'
}

onMounted(() => {
	store.loadGemstoneTypes()
	loadData()
})
</script>
