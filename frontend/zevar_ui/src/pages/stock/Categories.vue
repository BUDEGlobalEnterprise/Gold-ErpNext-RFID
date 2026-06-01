<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Categories</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.categoriesTotal }} Groups</span
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
							:class="{ 'animate-spin': stock.categoriesResource.loading }"
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
						Add Category
					</button>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.categoriesResource.loading && !stock.categories.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.categories.length"
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
							d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
						/>
					</svg>
					<p class="text-sm font-bold">No categories found</p>
					<p class="text-xs mt-1">Add a category to organize your items</p>
				</div>
				<div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
					<div
						v-for="cat in stock.categories"
						:key="cat.name"
						class="premium-card cursor-pointer hover:border-[#D4AF37]/50"
						@click="viewCategory(cat)"
					>
						<div class="flex items-center gap-3">
							<div
								class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 overflow-hidden bg-amber-50 dark:bg-amber-900/20"
							>
								<img
									v-if="cat.image"
									:src="cat.image"
									class="w-full h-full object-cover"
								/>
								<svg
									v-else
									class="w-5 h-5"
									:class="cat.is_group ? 'text-amber-600' : 'text-gray-500'"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
									/>
								</svg>
							</div>
							<div class="min-w-0 flex-1">
								<div
									class="text-xs font-bold text-gray-900 dark:text-white truncate"
								>
									{{ cat.item_group_name || cat.name }}
								</div>
								<div class="text-[10px] text-gray-500 truncate">
									{{ cat.parent_item_group || 'Root' }}
								</div>
								<div class="text-[10px] text-gray-500 mt-1">
									{{ cat.item_count }} items
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Items in Category Modal -->
			<div
				v-if="selectedCategory"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="selectedCategory = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								{{ selectedCategory.item_group_name || selectedCategory.name }}
							</h3>
							<p class="text-xs text-gray-500">
								{{ selectedCategory.item_count || categoryItems.length }} items
							</p>
						</div>
						<button
							@click="selectedCategory = null"
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
					<div v-if="categoryItems.length" class="space-y-1">
						<div
							v-for="item in categoryItems"
							:key="item.item_code"
							class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
						>
							<div>
								<div class="text-xs font-bold text-gray-900 dark:text-white">
									{{ item.item_name }}
								</div>
								<div class="text-[10px] text-gray-500">{{ item.item_code }}</div>
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
						No items in this category
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
							v-if="selectedCategory"
							@click="openEdit(selectedCategory)"
							class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
						>
							Edit
						</button>
						<button
							v-if="selectedCategory"
							@click="confirmDelete(selectedCategory)"
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
							{{ formMode === 'edit' ? 'Edit Category' : 'Add Category' }}
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
							<label class="text-[10px] font-bold text-gray-500 uppercase">Category Name *</label>
							<input
								v-model="form.item_group_name"
								type="text"
								placeholder="e.g. Engagement Rings"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Parent Category</label>
							<input
								v-model="form.parent_item_group"
								type="text"
								placeholder="Leave empty for top-level"
								list="cat-parent-suggestions"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
							<datalist id="cat-parent-suggestions">
								<option v-for="c in stock.categories" :key="c.name" :value="c.name">
									{{ c.item_group_name }}
								</option>
							</datalist>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Is Group?</label>
							<select
								v-model="form.is_group"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							>
								<option :value="0">No (leaf category)</option>
								<option :value="1">Yes (contains sub-categories)</option>
							</select>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Image URL</label>
							<input
								v-model="form.image"
								type="text"
								placeholder="https://…"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
					</div>
					<button
						@click="handleSave"
						:disabled="saving"
						class="w-full mt-4 py-2.5 bg-[#D4AF37] text-white rounded-lg text-sm font-bold hover:bg-[#C4A030] transition disabled:opacity-50"
					>
						{{ saving ? 'Saving…' : formMode === 'edit' ? 'Save Changes' : 'Create Category' }}
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
const selectedCategory = ref(null)
const categoryItems = ref([])
const loadingItems = ref(false)
const showForm = ref(false)
const formMode = ref('create')
const saving = ref(false)
const form = reactive({
	item_group_name: '',
	parent_item_group: '',
	is_group: 0,
	image: '',
})

function loadData() {
	stock.loadCategories()
}

async function viewCategory(cat) {
	selectedCategory.value = cat
	categoryItems.value = []
	loadingItems.value = true
	try {
		const res = await stock.loadItemsInGroup(cat.name)
		categoryItems.value = res?.items || []
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
		is_group: 0,
		image: '',
	})
	showForm.value = true
}

function openEdit(cat) {
	formMode.value = 'edit'
	Object.assign(form, {
		item_group_name: cat.item_group_name,
		parent_item_group: cat.parent_item_group || '',
		is_group: cat.is_group ? 1 : 0,
		image: cat.image || '',
	})
	selectedCategory.value = null
	showForm.value = true
}

async function handleSave() {
	if (!form.item_group_name) {
		toast({ title: 'Category name is required', icon: 'alert-circle', intent: 'warning' })
		return
	}
	saving.value = true
	try {
		if (formMode.value === 'edit' && selectedCategory.value?.name) {
			await stock.updateItemGroup(selectedCategory.value.name, { ...form })
		} else {
			await stock.createItemGroup({ ...form })
		}
		toast({ title: 'Category saved', icon: 'check', intent: 'success' })
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

async function confirmDelete(cat) {
	if (!confirm(`Delete category "${cat.item_group_name || cat.name}"? You can't undo this.`))
		return
	try {
		await stock.deleteItemGroup(cat.name)
		toast({ title: 'Category deleted', icon: 'check', intent: 'success' })
		selectedCategory.value = null
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
