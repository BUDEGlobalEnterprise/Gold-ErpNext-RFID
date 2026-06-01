<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Metals Inventory</h2>
				<div class="flex items-center gap-2">
					<div class="relative hidden sm:block">
						<input
							v-model="search"
							@input="debouncedSearch"
							type="text"
							placeholder="Search metals..."
							class="pl-8 pr-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37] w-40"
						/>
						<svg
							class="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<circle cx="11" cy="11" r="8" stroke-width="2" />
							<path stroke-linecap="round" stroke-width="2" d="M21 21l-4.35-4.35" />
						</svg>
					</div>
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': stock.metalsResource.loading }"
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
					<button
						@click="openCreate"
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
						Add Metal
					</button>
				</div>
			</div>

			<div
				v-if="ratesList.length"
				class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0"
			>
				<div
					v-for="rate in ratesList.slice(0, 4)"
					:key="rate.label"
					class="premium-card !p-4"
				>
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						{{ rate.label }}
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						${{ Number(rate.price || 0).toFixed(2) }}/g
					</div>
					<div
						v-if="rate.trend"
						class="text-[10px] mt-1"
						:class="
							rate.trend === 'up'
								? 'text-emerald-500'
								: rate.trend === 'down'
								? 'text-red-500'
								: 'text-gray-500'
						"
					>
						{{ rate.trend === 'up' ? '▲' : rate.trend === 'down' ? '▼' : '—' }}
						{{ rate.change_pct || '' }}
					</div>
				</div>
			</div>

			<div
				v-if="metalTypes.length"
				class="flex flex-wrap gap-2 mb-4 flex-shrink-0"
			>
				<button
					v-for="t in ['All', ...metalTypes]"
					:key="t"
					@click="metalTypeFilter = t === 'All' ? '' : t"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						metalTypeFilter === (t === 'All' ? '' : t)
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300'
					"
				>
					{{ t }}
				</button>
			</div>

			<div class="premium-card !p-4 mb-4 flex-shrink-0">
				<div class="flex items-center justify-between">
					<div>
						<div class="text-[10px] font-bold text-gray-500 uppercase">
							Total Metal Items
						</div>
						<div class="text-xl font-bold text-gray-900 dark:text-white">
							{{ stock.metalsTotal }}
						</div>
					</div>
					<div>
						<div class="text-[10px] font-bold text-gray-500 uppercase">
							Total Stock Value
						</div>
						<div class="text-xl font-bold text-[#D4AF37]">
							${{ totalMetalValue.toFixed(2) }}
						</div>
					</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.metalsResource.loading && !stock.metals.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!filteredMetals.length"
					class="flex flex-col items-center justify-center py-20 text-gray-400"
				>
					<svg
						class="w-16 h-16 mb-4 opacity-30"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1"
							d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
						/>
					</svg>
					<p class="text-sm font-bold">No metal items found</p>
					<p class="text-xs mt-1">Add your first metal item to track inventory</p>
				</div>
				<div v-else class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead>
							<tr
								class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50"
							>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Item
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden sm:table-cell"
								>
									Metal
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell"
								>
									Purity
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase hidden md:table-cell"
								>
									Weight
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Stock
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase"
								>
									Value
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="item in filteredMetals"
								:key="item.item_code"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
								@click="viewMetal(item)"
							>
								<td class="px-4 py-3">
									<div class="text-xs font-bold text-gray-900 dark:text-white">
										{{ item.item_name }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ item.item_code }}
									</div>
								</td>
								<td class="px-4 py-3 hidden sm:table-cell">
									<span
										class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
										>{{ item.custom_metal_type || item.item_group }}</span
									>
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ item.custom_purity || '-' }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-mono text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ item.custom_gross_weight_g || '-' }}g
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold"
									:class="
										item.stock_qty > 0 ? 'text-emerald-500' : 'text-red-500'
									"
								>
									{{ item.stock_qty }}
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-[#D4AF37]"
								>
									${{ Number(item.current_value || 0).toFixed(2) }}
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Detail Modal -->
			<div
				v-if="selectedMetal"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="selectedMetal = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								{{ selectedMetal.item_name || selectedMetal.name }}
							</h3>
							<p class="text-xs text-gray-500">
								{{ selectedMetal.item_code || selectedMetal.name }}
							</p>
						</div>
						<button
							@click="selectedMetal = null"
							class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"
						>
							<svg
								class="w-5 h-5 text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
					<div class="grid grid-cols-2 gap-3 mb-4">
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Metal Type</span>
							<p class="text-sm font-bold text-gray-900 dark:text-white">
								{{ selectedMetal.custom_metal_type || '-' }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Purity</span>
							<p class="text-sm font-bold text-gray-900 dark:text-white">
								{{ selectedMetal.custom_purity || '-' }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Gross Weight</span>
							<p class="text-sm font-mono text-gray-700 dark:text-gray-300">
								{{ selectedMetal.custom_gross_weight_g || '-' }}g
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Stock</span>
							<p
								class="text-sm font-bold"
								:class="
									selectedMetal.stock_qty > 0 ? 'text-emerald-500' : 'text-red-500'
								"
							>
								{{ selectedMetal.stock_qty }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Standard Rate</span>
							<p class="text-sm font-mono text-[#D4AF37]">
								${{ Number(selectedMetal.standard_rate || 0).toFixed(2) }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Valuation Rate</span>
							<p class="text-sm font-mono text-[#D4AF37]">
								${{ Number(selectedMetal.valuation_rate || 0).toFixed(2) }}
							</p>
						</div>
					</div>
					<div
						class="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50"
					>
						<button
							@click="openEdit(selectedMetal)"
							class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
						>
							Edit
						</button>
						<button
							@click="confirmDelete(selectedMetal)"
							class="py-2 px-4 bg-red-50 text-red-600 border border-red-200 rounded-lg text-xs font-bold hover:bg-red-100 transition"
						>
							Delete
						</button>
					</div>
				</div>
			</div>

			<!-- Create/Edit Modal -->
			<div
				v-if="showForm"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="showForm = false"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">
							{{ formMode === 'edit' ? 'Edit Metal' : 'Add Metal' }}
						</h3>
						<button
							@click="showForm = false"
							class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-lg"
						>
							<svg
								class="w-5 h-5 text-gray-500"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>
					<div class="space-y-3">
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Item Name *</label>
							<input
								v-model="form.item_name"
								type="text"
								placeholder="e.g. 14K Yellow Gold Bar"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Metal Type</label>
								<select
									v-model="form.custom_metal_type"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								>
									<option value="">Select…</option>
									<option v-for="t in metalTypeOptions" :key="t" :value="t">{{ t }}</option>
								</select>
							</div>
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Purity (Karat)</label>
								<select
									v-model="form.custom_purity"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								>
									<option value="">Select…</option>
									<option v-for="p in purityOptions" :key="p" :value="p">{{ p }}</option>
								</select>
							</div>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Gross Weight (g)</label>
							<input
								v-model.number="form.custom_gross_weight_g"
								type="number"
								step="0.001"
								min="0"
								placeholder="0.000"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Standard Rate ($/g)</label>
								<input
									v-model.number="form.standard_rate"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								/>
							</div>
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Valuation Rate ($/g)</label>
								<input
									v-model.number="form.valuation_rate"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								/>
							</div>
						</div>
					</div>
					<button
						@click="handleSave"
						:disabled="saving"
						class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50"
					>
						{{ saving ? 'Saving…' : formMode === 'edit' ? 'Save Changes' : 'Create Metal' }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { toast } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'
import { useGoldStore } from '@/stores/gold.js'

const stock = useStockStore()
const goldStore = useGoldStore()
const search = ref('')
const metalTypeFilter = ref('')
const selectedMetal = ref(null)
const showForm = ref(false)
const formMode = ref('create')
const saving = ref(false)
const form = reactive({
	item_name: '',
	custom_metal_type: '',
	custom_purity: '',
	custom_gross_weight_g: 0,
	standard_rate: 0,
	valuation_rate: 0,
})

const metalTypeOptions = [
	'Yellow Gold',
	'White Gold',
	'Rose Gold',
	'Green Gold',
	'Platinum',
	'Silver',
	'Palladium',
	'Stainless Steel',
]
const purityOptions = ['9K', '10K', '14K', '18K', '22K', '24K', '925', '950', '999']

const totalMetalValue = computed(() =>
	stock.metals.reduce(
		(s, i) => s + (i.current_value || 0) * Math.max(i.stock_qty, 0),
		0
	)
)
const ratesList = computed(() => {
	const r = goldStore.rates || {}
	return Object.entries(r).map(([key, val]) => ({
		label: key,
		price: typeof val === 'object' ? val.rate_per_gram : val,
		trend: typeof val === 'object' ? val.trend : null,
		change_pct: typeof val === 'object' ? val.change_pct : null,
	}))
})
const metalTypes = computed(() => {
	const set = new Set()
	stock.metals.forEach((m) => {
		if (m.custom_metal_type) set.add(m.custom_metal_type)
	})
	return [...set].sort()
})
const filteredMetals = computed(() => {
	let list = stock.metals
	if (metalTypeFilter.value) {
		list = list.filter((m) => m.custom_metal_type === metalTypeFilter.value)
	}
	if (search.value) {
		const q = search.value.toLowerCase()
		list = list.filter(
			(m) =>
				(m.item_name || '').toLowerCase().includes(q) ||
				(m.item_code || '').toLowerCase().includes(q) ||
				(m.custom_metal_type || '').toLowerCase().includes(q)
		)
	}
	return list
})

let searchTimer = null
function debouncedSearch() {
	clearTimeout(searchTimer)
	searchTimer = setTimeout(loadData, 300)
}

function loadData() {
	stock.loadMetals({ search: search.value || undefined })
	goldStore.startPolling()
}

function viewMetal(m) {
	selectedMetal.value = m
}

function openCreate() {
	formMode.value = 'create'
	Object.assign(form, {
		item_name: '',
		custom_metal_type: '',
		custom_purity: '',
		custom_gross_weight_g: 0,
		standard_rate: 0,
		valuation_rate: 0,
	})
	showForm.value = true
}

function openEdit(m) {
	formMode.value = 'edit'
	Object.assign(form, {
		item_name: m.item_name,
		custom_metal_type: m.custom_metal_type || '',
		custom_purity: m.custom_purity || '',
		custom_gross_weight_g: m.custom_gross_weight_g || 0,
		standard_rate: m.standard_rate || 0,
		valuation_rate: m.valuation_rate || 0,
	})
	selectedMetal.value = null
	showForm.value = true
}

async function handleSave() {
	if (!form.item_name) {
		toast({ title: 'Item name is required', icon: 'alert-circle', intent: 'warning' })
		return
	}
	saving.value = true
	try {
		if (formMode.value === 'edit' && selectedMetal.value?.item_code) {
			// refetch from server to get the actual name (we may have set selectedMetal from list view)
			const detail = await stock.getItem(selectedMetal.value.item_code)
			await stock.updateItem(detail.item.name, { ...form })
		} else {
			// form was opened via 'openCreate' (not 'openEdit'), so create
			await stock.createItem({ ...form }, 'Metals')
		}
		toast({ title: 'Metal saved', icon: 'check', intent: 'success' })
		showForm.value = false
		loadData()
	} catch (e) {
		toast({
			title: 'Save failed',
			text: e?.message || String(e),
			icon: 'alert-circle',
			intent: 'error',
		})
	} finally {
		saving.value = false
	}
}

async function confirmDelete(m) {
	if (!confirm(`Disable metal "${m.item_name}"? You can't undo this.`)) return
	try {
		await stock.deleteItem(m.item_code)
		toast({ title: 'Metal disabled', icon: 'check', intent: 'success' })
		selectedMetal.value = null
		loadData()
	} catch (e) {
		toast({
			title: 'Delete failed',
			text: e?.message || String(e),
			icon: 'alert-circle',
			intent: 'error',
		})
	}
}

onMounted(loadData)
</script>
