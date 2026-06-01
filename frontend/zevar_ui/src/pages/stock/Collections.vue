<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Collections</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.collectionsTotal }} Collections</span
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
							:class="{ 'animate-spin': stock.collectionsResource.loading }"
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
						Add Collection
					</button>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.collectionsResource.loading && !stock.collections.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.collections.length"
					class="flex flex-col items-center justify-center py-20 text-gray-400"
				>
					<svg
						class="w-16 h-16 mb-4 opacity-30"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<rect x="3" y="3" width="7" height="7" stroke-width="1" />
						<rect x="14" y="3" width="7" height="7" stroke-width="1" />
						<rect x="14" y="14" width="7" height="7" stroke-width="1" />
						<rect x="3" y="14" width="7" height="7" stroke-width="1" />
					</svg>
					<p class="text-sm font-bold">No collections found</p>
					<p class="text-xs mt-1">Add a collection to showcase curated items</p>
				</div>
				<div
					v-else
					class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3"
				>
					<div
						v-for="col in stock.collections"
						:key="col.name"
						class="premium-card !p-0 overflow-hidden cursor-pointer hover:border-[#D4AF37]/50 group"
						@click="viewCollection(col)"
					>
						<div
							class="aspect-[3/2] bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/10 dark:to-orange-900/10 flex items-center justify-center"
						>
							<img
								v-if="col.image"
								:src="col.image"
								class="w-full h-full object-cover"
							/>
							<svg
								v-else
								class="w-12 h-12 text-amber-200 dark:text-amber-800"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<rect x="3" y="3" width="7" height="7" stroke-width="1" />
								<rect x="14" y="3" width="7" height="7" stroke-width="1" />
								<rect x="14" y="14" width="7" height="7" stroke-width="1" />
								<rect x="3" y="14" width="7" height="7" stroke-width="1" />
							</svg>
						</div>
						<div class="p-3">
							<div class="text-sm font-bold text-gray-900 dark:text-white truncate">
								{{ col.item_group_name || col.name }}
							</div>
							<div class="text-[10px] text-gray-500 mt-0.5">
								{{ col.parent_item_group || 'Root' }} · {{ col.item_count }} items
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Collection Items Modal -->
			<div
				v-if="selectedCollection"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="selectedCollection = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div
						v-if="selectedCollection.image"
						class="h-32 -mx-4 -mt-4 mb-4 bg-cover bg-center rounded-t-2xl"
						:style="{ backgroundImage: `url(${selectedCollection.image})` }"
					></div>
					<div class="flex items-center justify-between mb-4">
						<div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								{{ selectedCollection.item_group_name || selectedCollection.name }}
							</h3>
							<p class="text-xs text-gray-500">
								{{ collectionItems.length || selectedCollection.item_count }} items
							</p>
						</div>
						<button
							@click="selectedCollection = null"
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
					<div v-if="collectionItems.length" class="space-y-1">
						<div
							v-for="item in collectionItems"
							:key="item.item_code"
							class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
						>
							<div class="flex items-center gap-3">
								<div
									class="w-8 h-8 rounded-lg overflow-hidden bg-gray-100 dark:bg-warm-dark-700 flex items-center justify-center shrink-0"
								>
									<img
										v-if="item.image"
										:src="item.image"
										class="w-full h-full object-cover"
									/>
									<span v-else class="text-xs text-gray-400">—</span>
								</div>
								<div>
									<div class="text-xs font-bold text-gray-900 dark:text-white">
										{{ item.item_name }}
									</div>
									<div class="text-[10px] text-gray-500">{{ item.item_code }}</div>
								</div>
							</div>
							<div class="text-right text-xs font-mono text-[#D4AF37]">
								${{ Number(item.standard_rate || 0).toFixed(2) }}
							</div>
						</div>
					</div>
					<div
						v-else-if="!loadingItems"
						class="text-center py-10 text-sm text-gray-400"
					>
						No items in this collection
					</div>
					<div
						v-if="loadingItems"
						class="flex items-center justify-center py-10"
					>
						<div
							class="animate-spin w-6 h-6 border-2 border-[#D4AF37] border-t-transparent rounded-full"
						></div>
					</div>
					<div
						class="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50"
					>
						<button
							@click="openEdit(selectedCollection)"
							class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
						>
							Edit
						</button>
						<button
							@click="confirmDelete(selectedCollection)"
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
							{{ formMode === 'edit' ? 'Edit Collection' : 'Add Collection' }}
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
							<label class="text-[10px] font-bold text-gray-500 uppercase">Collection Name *</label>
							<input
								v-model="form.item_group_name"
								type="text"
								placeholder="e.g. Spring 2026"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Parent Collection</label>
							<input
								v-model="form.parent_item_group"
								type="text"
								placeholder="Leave empty for top-level"
								list="coll-parent-suggestions"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
							<datalist id="coll-parent-suggestions">
								<option
									v-for="c in stock.collections"
									:key="c.name"
									:value="c.name"
								>
									{{ c.item_group_name }}
								</option>
							</datalist>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Cover Image URL</label>
							<div class="flex gap-2 mt-1">
								<input
									v-model="form.image"
									type="text"
									placeholder="https://…"
									class="flex-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								/>
								<label
									class="px-3 py-2 bg-gray-100 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-lg text-xs font-bold cursor-pointer hover:bg-gray-200"
								>
									Upload
									<input
										type="file"
										accept="image/*"
										class="hidden"
										@change="onFileChosen"
									/>
								</label>
							</div>
							<div
								v-if="form.image"
								class="mt-2 h-24 rounded-lg overflow-hidden bg-gray-100"
							>
								<img :src="form.image" class="w-full h-full object-cover" />
							</div>
						</div>
					</div>
					<button
						@click="handleSave"
						:disabled="saving"
						class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50"
					>
						{{ saving ? 'Saving…' : formMode === 'edit' ? 'Save Changes' : 'Create Collection' }}
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
const selectedCollection = ref(null)
const collectionItems = ref([])
const loadingItems = ref(false)
const showForm = ref(false)
const formMode = ref('create')
const saving = ref(false)
const form = reactive({
	item_group_name: '',
	parent_item_group: '',
	image: '',
})

function loadData() {
	stock.loadCollections()
}

async function viewCollection(col) {
	selectedCollection.value = col
	collectionItems.value = []
	loadingItems.value = true
	try {
		const res = await stock.loadItemsInGroup(col.name)
		collectionItems.value = res?.items || []
	} catch (e) {
		console.warn('Could not load items', e)
	} finally {
		loadingItems.value = false
	}
}

function openCreate() {
	formMode.value = 'create'
	Object.assign(form, {
		item_group_name: '',
		parent_item_group: '',
		image: '',
	})
	showForm.value = true
}

function openEdit(col) {
	formMode.value = 'edit'
	Object.assign(form, {
		item_group_name: col.item_group_name || col.name,
		parent_item_group: col.parent_item_group || '',
		image: col.image || '',
	})
	selectedCollection.value = null
	showForm.value = true
}

function onFileChosen(ev) {
	const file = ev.target.files?.[0]
	if (!file) return
	const reader = new FileReader()
	reader.onload = (e) => {
		form.image = e.target.result
	}
	reader.readAsDataURL(file)
}

async function handleSave() {
	if (!form.item_group_name) {
		toast({
			title: 'Collection name is required',
			icon: 'alert-circle',
			intent: 'warning',
		})
		return
	}
	saving.value = true
	try {
		const values = { ...form, is_group: 0 }
		if (formMode.value === 'edit' && selectedCollection.value?.name) {
			await stock.updateItemGroup(selectedCollection.value.name, values)
		} else {
			await stock.createItemGroup(values)
		}
		toast({ title: 'Collection saved', icon: 'check', intent: 'success' })
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

async function confirmDelete(col) {
	if (
		!confirm(`Delete collection "${col.item_group_name || col.name}"? You can't undo this.`)
	)
		return
	try {
		await stock.deleteItemGroup(col.name)
		toast({ title: 'Collection deleted', icon: 'check', intent: 'success' })
		selectedCollection.value = null
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
