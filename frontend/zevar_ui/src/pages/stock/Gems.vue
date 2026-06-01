<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Gems &amp; Stones</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.gemsTotal }} Items</span
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
							:class="{ 'animate-spin': stock.gemsResource.loading }"
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
						Add Gem
					</button>
				</div>
			</div>

			<div class="flex flex-wrap gap-2 mb-4 flex-shrink-0">
				<button
					v-for="t in ['All', ...gemTypeOptions]"
					:key="t"
					@click="activeType = t === 'All' ? '' : t"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						activeType === (t === 'All' ? '' : t)
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300'
					"
				>
					{{ t }}
				</button>
				<button
					@click="certifiedOnly = !certifiedOnly"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						certifiedOnly
							? 'bg-emerald-600 text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300'
					"
				>
					{{ certifiedOnly ? '✓ Certified Only' : 'Certified Only' }}
				</button>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.gemsResource.loading && !stock.gems.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!filteredGems.length"
					class="flex flex-col items-center justify-center py-20 text-gray-400"
				>
					<svg
						class="w-16 h-16 mb-4 opacity-30"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<polygon points="12 2 2 7 12 12 22 7 12 2" stroke-width="1" />
						<polyline points="2 17 12 22 22 17" stroke-width="1" />
						<polyline points="2 12 12 17 22 12" stroke-width="1" />
					</svg>
					<p class="text-sm font-bold">No gems found</p>
					<p class="text-xs mt-1">Add your first gem item to start tracking inventory</p>
				</div>
				<div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
					<div
						v-for="gem in filteredGems"
						:key="gem.item_code"
						class="premium-card !p-0 overflow-hidden group cursor-pointer"
						@click="viewGem(gem)"
					>
						<div
							class="aspect-square bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 flex items-center justify-center relative"
						>
							<img
								v-if="gem.image"
								:src="gem.image"
								class="w-full h-full object-cover"
							/>
							<svg
								v-else
								class="w-12 h-12 text-purple-200 dark:text-purple-800"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<polygon points="12 2 2 7 12 12 22 7 12 2" stroke-width="1" />
								<polyline points="2 17 12 22 22 17" stroke-width="1" />
								<polyline points="2 12 12 17 22 12" stroke-width="1" />
							</svg>
							<div class="absolute top-2 right-2">
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
									:class="
										gem.stock_qty > 0
											? 'bg-green-100 text-green-700'
											: 'bg-red-100 text-red-700'
									"
									>{{ gem.stock_qty }} pcs</span
								>
							</div>
						</div>
						<div class="p-3">
							<div
								class="text-xs font-bold text-gray-900 dark:text-white truncate mb-1"
							>
								{{ gem.item_name }}
							</div>
							<div class="flex flex-wrap gap-1 mb-2">
								<span
									v-if="gem.custom_gem_type"
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400"
									>{{ gem.custom_gem_type }}</span
								>
								<span
									v-if="gem.custom_carat_weight"
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
									>{{ gem.custom_carat_weight }}ct</span
								>
								<span
									v-if="gem.custom_gem_cut"
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400"
									>{{ gem.custom_gem_cut }}</span
								>
							</div>
							<div class="flex items-center justify-between">
								<span
									class="text-sm font-bold text-gray-900 dark:text-white font-mono"
									>${{
										Number(gem.standard_rate || gem.valuation_rate || 0).toFixed(2)
									}}</span
								>
								<span
									v-if="gem.custom_certification_number"
									class="text-[9px] text-emerald-500 font-bold"
									>✓ Cert</span
								>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Detail Modal -->
			<div
				v-if="selectedGem"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="selectedGem = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								{{ selectedGem.item_name }}
							</h3>
							<p class="text-xs text-gray-500">{{ selectedGem.item_code }}</p>
						</div>
						<button
							@click="selectedGem = null"
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
					<div
						v-if="selectedGem.image"
						class="mb-4 aspect-video rounded-lg overflow-hidden bg-gray-100"
					>
						<img :src="selectedGem.image" class="w-full h-full object-cover" />
					</div>
					<div class="grid grid-cols-2 gap-3 mb-4">
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Gem Type</span>
							<p class="text-sm font-bold text-gray-900 dark:text-white">
								{{ selectedGem.custom_gem_type || '-' }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Carat</span>
							<p class="text-sm font-mono text-gray-700 dark:text-gray-300">
								{{ selectedGem.custom_carat_weight || '-' }}ct
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Cut</span>
							<p class="text-sm text-gray-700 dark:text-gray-300">
								{{ selectedGem.custom_gem_cut || '-' }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Color</span>
							<p class="text-sm text-gray-700 dark:text-gray-300">
								{{ selectedGem.custom_gem_color || '-' }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Clarity</span>
							<p class="text-sm text-gray-700 dark:text-gray-300">
								{{ selectedGem.custom_gem_clarity || '-' }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Shape</span>
							<p class="text-sm text-gray-700 dark:text-gray-300">
								{{ selectedGem.custom_gem_shape || '-' }}
							</p>
						</div>
						<div class="col-span-2">
							<span class="text-[10px] text-gray-500 uppercase">Certification</span>
							<p class="text-sm font-mono text-emerald-600">
								{{ selectedGem.custom_certification_number || 'Not certified' }}
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Stock</span>
							<p
								class="text-sm font-bold"
								:class="
									selectedGem.stock_qty > 0 ? 'text-emerald-500' : 'text-red-500'
								"
							>
								{{ selectedGem.stock_qty }} pcs
							</p>
						</div>
						<div>
							<span class="text-[10px] text-gray-500 uppercase">Price</span>
							<p class="text-sm font-mono font-bold text-[#D4AF37]">
								${{
									Number(
										selectedGem.standard_rate || selectedGem.valuation_rate || 0
									).toFixed(2)
								}}
							</p>
						</div>
					</div>
					<div
						class="flex gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50"
					>
						<button
							@click="openEdit(selectedGem)"
							class="flex-1 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
						>
							Edit
						</button>
						<button
							@click="confirmDelete(selectedGem)"
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
							{{ formMode === 'edit' ? 'Edit Gem' : 'Add Gem' }}
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
								placeholder="e.g. 1.5ct Round Diamond F-VVS1"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Gem Type</label>
								<select
									v-model="form.custom_gem_type"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								>
									<option value="">Select…</option>
									<option v-for="t in gemTypeOptions" :key="t" :value="t">{{ t }}</option>
								</select>
							</div>
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Carat</label>
								<input
									v-model.number="form.custom_carat_weight"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								/>
							</div>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Cut</label>
								<select
									v-model="form.custom_gem_cut"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								>
									<option value="">Select…</option>
									<option v-for="c in cutOptions" :key="c" :value="c">{{ c }}</option>
								</select>
							</div>
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Shape</label>
								<select
									v-model="form.custom_gem_shape"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								>
									<option value="">Select…</option>
									<option v-for="s in shapeOptions" :key="s" :value="s">{{ s }}</option>
								</select>
							</div>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Color</label>
								<input
									v-model="form.custom_gem_color"
									type="text"
									placeholder="D, E, F…"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								/>
							</div>
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Clarity</label>
								<input
									v-model="form.custom_gem_clarity"
									type="text"
									placeholder="FL, IF, VVS1…"
									class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
								/>
							</div>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Certification #</label>
							<input
								v-model="form.custom_certification_number"
								type="text"
								placeholder="GIA / IGI / AGS report #"
								class="w-full mt-1 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent outline-none"
							/>
						</div>
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase">Image URL</label>
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
								class="mt-2 h-20 w-20 rounded-lg overflow-hidden bg-gray-100"
							>
								<img :src="form.image" class="w-full h-full object-cover" />
							</div>
						</div>
						<div class="grid grid-cols-2 gap-2">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase">Standard Rate</label>
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
								<label class="text-[10px] font-bold text-gray-500 uppercase">Valuation Rate</label>
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
						{{ saving ? 'Saving…' : formMode === 'edit' ? 'Save Changes' : 'Create Gem' }}
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

const stock = useStockStore()
const activeType = ref('')
const certifiedOnly = ref(false)
const selectedGem = ref(null)
const showForm = ref(false)
const formMode = ref('create')
const saving = ref(false)
const form = reactive({
	item_name: '',
	custom_gem_type: '',
	custom_carat_weight: 0,
	custom_gem_cut: '',
	custom_gem_shape: '',
	custom_gem_color: '',
	custom_gem_clarity: '',
	custom_certification_number: '',
	image: '',
	standard_rate: 0,
	valuation_rate: 0,
})

const gemTypeOptions = [
	'Diamond',
	'Ruby',
	'Sapphire',
	'Emerald',
	'Topaz',
	'Amethyst',
	'Garnet',
	'Pearl',
	'Opal',
	'Turquoise',
	'Onyx',
	'Aquamarine',
	'Peridot',
	'Tanzanite',
	'Citrine',
	'Other',
]
const cutOptions = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
const shapeOptions = [
	'Round',
	'Princess',
	'Cushion',
	'Emerald',
	'Oval',
	'Pear',
	'Marquise',
	'Asscher',
	'Radiant',
	'Heart',
]

const filteredGems = computed(() => {
	let list = stock.gems
	if (activeType.value) list = list.filter((g) => g.custom_gem_type === activeType.value)
	if (certifiedOnly.value)
		list = list.filter((g) => g.custom_certification_number)
	return list
})

function loadData() {
	stock.loadGems({
		gem_type: activeType.value || undefined,
		certified_only: certifiedOnly.value ? 1 : 0,
	})
}

function viewGem(g) {
	selectedGem.value = g
}

function openCreate() {
	formMode.value = 'create'
	Object.assign(form, {
		item_name: '',
		custom_gem_type: '',
		custom_carat_weight: 0,
		custom_gem_cut: '',
		custom_gem_shape: '',
		custom_gem_color: '',
		custom_gem_clarity: '',
		custom_certification_number: '',
		image: '',
		standard_rate: 0,
		valuation_rate: 0,
	})
	showForm.value = true
}

function openEdit(g) {
	formMode.value = 'edit'
	Object.assign(form, {
		item_name: g.item_name,
		custom_gem_type: g.custom_gem_type || '',
		custom_carat_weight: g.custom_carat_weight || 0,
		custom_gem_cut: g.custom_gem_cut || '',
		custom_gem_shape: g.custom_gem_shape || '',
		custom_gem_color: g.custom_gem_color || '',
		custom_gem_clarity: g.custom_gem_clarity || '',
		custom_certification_number: g.custom_certification_number || '',
		image: g.image || '',
		standard_rate: g.standard_rate || 0,
		valuation_rate: g.valuation_rate || 0,
	})
	selectedGem.value = null
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
	if (!form.item_name) {
		toast({ title: 'Item name is required', icon: 'alert-circle', intent: 'warning' })
		return
	}
	saving.value = true
	try {
		// pick the right Item Group based on the gem type
		const isStone = ['Pearl', 'Opal', 'Turquoise', 'Onyx'].includes(form.custom_gem_type)
		const itemGroup = isStone ? 'Stones' : 'Gems'
		if (formMode.value === 'edit' && selectedGem.value?.item_code) {
			const detail = await stock.getItem(selectedGem.value.item_code)
			await stock.updateItem(detail.item.name, { ...form })
		} else {
			await stock.createItem({ ...form }, itemGroup)
		}
		toast({ title: 'Gem saved', icon: 'check', intent: 'success' })
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

async function confirmDelete(g) {
	if (!confirm(`Disable gem "${g.item_name}"? You can't undo this.`)) return
	try {
		await stock.deleteItem(g.item_code)
		toast({ title: 'Gem disabled', icon: 'check', intent: 'success' })
		selectedGem.value = null
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
