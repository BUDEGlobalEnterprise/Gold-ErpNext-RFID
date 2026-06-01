<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Storages</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.warehousesTotal }} Locations</span
					>
				</div>
				<div class="flex items-center gap-2">
					<button
						@click="loadData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': stock.warehousesResource.loading }"
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
						Add Storage
					</button>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.warehousesResource.loading && !stock.warehouses.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.warehouses.length"
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
							d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
						/>
					</svg>
					<p class="text-sm font-bold">No warehouses found</p>
					<p class="text-xs mt-1">Add a storage location to organize your inventory</p>
				</div>
				<div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
					<div
						v-for="wh in stock.warehouses"
						:key="wh.name"
						class="premium-card cursor-pointer"
						@click="viewWarehouse(wh)"
					>
						<div class="flex items-start gap-3">
							<div
								class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
								:class="
									wh.is_group
										? 'bg-blue-100 dark:bg-blue-900/30'
										: 'bg-gray-100 dark:bg-warm-dark-900'
								"
							>
								<svg
									class="w-5 h-5"
									:class="
										wh.is_group
											? 'text-blue-600 dark:text-blue-400'
											: 'text-gray-500'
									"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
									/>
								</svg>
							</div>
							<div class="flex-1 min-w-0">
								<div
									class="text-sm font-bold text-gray-900 dark:text-white truncate"
								>
									{{ wh.warehouse_name }}
								</div>
								<div class="text-[10px] text-gray-500 truncate">
									{{ wh.parent_warehouse || 'Root' }}
								</div>
								<div class="flex items-center gap-3 mt-2">
									<div>
										<span class="text-[10px] text-gray-500">Items</span>
										<p class="text-sm font-bold text-gray-900 dark:text-white">
											{{ wh.item_count }}
										</p>
									</div>
									<div>
										<span class="text-[10px] text-gray-500">Value</span>
										<p class="text-sm font-bold text-[#D4AF37]">
											${{
												Number(wh.total_value || 0).toLocaleString('en-US', {
													maximumFractionDigits: 0,
												})
											}}
										</p>
									</div>
								</div>
							</div>
							<span
								v-if="wh.is_group"
								class="text-[9px] font-bold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
								>Group</span
							>
						</div>
					</div>
				</div>
			</div>

			<!-- Detail Modal -->
			<div
				v-if="detailWh"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="detailWh = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">
							{{ detailWh.warehouse?.warehouse_name }}
						</h3>
						<button
							@click="detailWh = null"
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
					<div v-if="detailWh.children?.length" class="mb-4">
						<h4 class="text-[10px] font-bold text-gray-500 uppercase mb-2">
							Sub-locations
						</h4>
						<div class="flex flex-wrap gap-2">
							<span
								v-for="c in detailWh.children"
								:key="c.name"
								class="text-[10px] font-bold px-2 py-1 rounded-full bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300"
								>{{ c.warehouse_name }}</span
							>
						</div>
					</div>
					<div v-if="detailWh.items?.length">
						<h4 class="text-[10px] font-bold text-gray-500 uppercase mb-2">
							Items ({{ detailWh.items.length }})
						</h4>
						<div class="max-h-60 overflow-y-auto">
							<div
								v-for="item in detailWh.items"
								:key="item.item_code"
								class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
							>
								<div>
									<div class="text-xs font-bold text-gray-900 dark:text-white">
										{{ item.item_name }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ item.item_code }}
									</div>
								</div>
								<div class="text-right">
									<div class="text-xs font-bold text-gray-900 dark:text-white">
										{{ item.actual_qty }} pcs
									</div>
									<div class="text-[10px] text-[#D4AF37]">
										${{ Number(item.value || 0).toFixed(2) }}
									</div>
								</div>
							</div>
						</div>
					</div>
					<div
						class="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50"
					>
						<button
							v-if="detailWh.warehouse"
							@click="openEdit(detailWh.warehouse)"
							class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
						>
							Edit
						</button>
						<button
							v-if="detailWh.warehouse && !detailWh.warehouse.is_group"
							@click="confirmDelete(detailWh.warehouse)"
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
							{{ formMode === 'edit' ? 'Edit Storage' : 'Add Storage' }}
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
							<label class="text-[10px] font-bold text-gray-500 uppercase">Warehouse Name *</label>
							<input
								v-model="form.warehouse_name"
								type="text"
								placeholder="e.g. Back Stock NYC"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Parent Warehouse</label>
							<input
								v-model="form.parent_warehouse"
								type="text"
								placeholder="Leave empty for root"
								list="wh-parent-suggestions"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
							<datalist id="wh-parent-suggestions">
								<option v-for="w in stock.warehouses" :key="w.name" :value="w.name">
									{{ w.warehouse_name }}
								</option>
							</datalist>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Warehouse Type</label>
								<input
									v-model="form.warehouse_type"
									type="text"
									placeholder="Optional"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								/>
							</div>
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Type</label>
								<select
									v-model="form.is_group"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								>
									<option :value="0">Storage Location</option>
									<option :value="1">Group (Parent)</option>
								</select>
							</div>
						</div>
					</div>
					<button
						@click="handleSave"
						:disabled="saving"
						class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50"
					>
						{{ saving ? 'Saving…' : formMode === 'edit' ? 'Save Changes' : 'Create Storage' }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { toast } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'

const stock = useStockStore()
const detailWh = ref(null)
const showForm = ref(false)
const formMode = ref('create')
const saving = ref(false)
const form = reactive({
	warehouse_name: '',
	parent_warehouse: '',
	warehouse_type: '',
	is_group: 0,
})

function loadData() {
	stock.loadWarehouses()
}

function viewWarehouse(wh) {
	stock.loadWarehouseDetail(wh.name).then(() => {
		detailWh.value = stock.currentWarehouse
	})
}

function openCreate() {
	formMode.value = 'create'
	Object.assign(form, {
		warehouse_name: '',
		parent_warehouse: '',
		warehouse_type: '',
		is_group: 0,
	})
	showForm.value = true
}

function openEdit(wh) {
	formMode.value = 'edit'
	Object.assign(form, {
		warehouse_name: wh.warehouse_name,
		parent_warehouse: wh.parent_warehouse || '',
		warehouse_type: wh.warehouse_type || '',
		is_group: wh.is_group ? 1 : 0,
	})
	detailWh.value = null
	showForm.value = true
}

async function handleSave() {
	if (!form.warehouse_name) {
		toast({ title: 'Warehouse name is required', icon: 'alert-circle', intent: 'warning' })
		return
	}
	saving.value = true
	try {
		if (formMode.value === 'edit' && detailWh.value?.warehouse) {
			await stock.updateWarehouse(detailWh.value.warehouse.name, { ...form })
		} else {
			await stock.createWarehouse({ ...form })
		}
		toast({ title: 'Storage saved', icon: 'check', intent: 'success' })
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

async function confirmDelete(wh) {
	if (!confirm(`Disable storage "${wh.warehouse_name}"? You can't undo this.`)) return
	try {
		await stock.deleteWarehouse(wh.name)
		toast({ title: 'Storage disabled', icon: 'check', intent: 'success' })
		detailWh.value = null
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
