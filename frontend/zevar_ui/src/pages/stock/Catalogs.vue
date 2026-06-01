<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Catalogs</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
						>{{ stock.catalogVendorsTotal }} Vendors</span
					>
				</div>
				<div class="flex items-center gap-2">
					<div class="relative">
						<input
							v-model="search"
							@input="debouncedSearch"
							type="text"
							placeholder="Search vendors or items…"
							class="pl-8 pr-3 py-1.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-xs text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-[#D4AF37] w-56"
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
							:class="{ 'animate-spin': stock.catalogVendorsResource.loading }"
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

			<!-- Source filter pills -->
			<div class="flex items-center gap-2 mb-4 flex-shrink-0 flex-wrap">
				<button
					v-for="src in sourceOptions"
					:key="src.value || 'all'"
					@click="activeSource = src.value"
					class="px-3 py-1.5 rounded-full text-xs font-bold transition"
					:class="
						activeSource === src.value
							? 'bg-[#D4AF37] text-white'
							: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-white/60 hover:bg-gray-200 dark:hover:bg-warm-dark-600'
					"
				>
					{{ src.label }}
				</button>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="stock.catalogVendorsResource.loading && !stock.catalogVendors.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!stock.catalogVendors.length"
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
							d="M4 19.5A2.5 2.5 0 016.5 17H20"
						/>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1"
							d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"
						/>
					</svg>
					<p class="text-sm font-bold">No vendor catalogs found</p>
					<p class="text-xs mt-1">Items appear here once a vendor is assigned</p>
				</div>
				<div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
					<div
						v-for="v in stock.catalogVendors"
						:key="v.vendor"
						class="premium-card cursor-pointer hover:border-[#D4AF37]/50"
						@click="viewVendor(v)"
					>
						<div class="flex items-start justify-between gap-3 mb-3">
							<div class="min-w-0 flex-1">
								<div class="text-sm font-bold text-gray-900 dark:text-white truncate">
									{{ v.vendor_name || v.vendor }}
								</div>
								<div
									v-if="v.vendor_name && v.vendor_name !== v.vendor"
									class="text-[10px] text-gray-500 truncate font-mono"
								>
									{{ v.vendor }}
								</div>
							</div>
							<div
								class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 bg-amber-50 dark:bg-amber-900/20"
							>
								<svg
									class="w-5 h-5 text-[#D4AF37]"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
									/>
								</svg>
							</div>
						</div>

						<div class="grid grid-cols-2 gap-2 text-center">
							<div
								class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-2"
							>
								<div class="text-[10px] text-gray-500 uppercase">Items</div>
								<div class="text-sm font-bold text-gray-900 dark:text-white">
									{{ v.item_count }}
								</div>
							</div>
							<div
								class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-2"
							>
								<div class="text-[10px] text-gray-500 uppercase">Total</div>
								<div class="text-sm font-bold text-[#D4AF37] font-mono">
									${{ Number(v.total_value || 0).toLocaleString() }}
								</div>
							</div>
						</div>

						<div
							v-if="Object.keys(v.sources || {}).length"
							class="flex flex-wrap gap-1 mt-3"
						>
							<span
								v-for="(count, src) in v.sources"
								:key="src"
								class="inline-flex items-center px-2 py-0.5 text-[10px] font-bold rounded-full bg-blue-50 text-blue-700 border border-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-900/30"
							>
								{{ src }} · {{ count }}
							</span>
						</div>

						<div
							v-if="v.latest_modified"
							class="text-[10px] text-gray-400 mt-3 truncate"
						>
							Updated {{ formatDate(v.latest_modified) }}
						</div>
					</div>
				</div>
			</div>

			<!-- Vendor Items Modal -->
			<div
				v-if="selectedVendor"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
				@click.self="selectedVendor = null"
			>
				<div
					class="premium-card !rounded-2xl w-full max-w-3xl max-h-[80vh] overflow-y-auto m-4"
				>
					<div class="flex items-center justify-between mb-4">
						<div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								{{ selectedVendor.vendor_name || selectedVendor.vendor }}
							</h3>
							<p class="text-xs text-gray-500">
								{{ selectedVendor.item_count }} items · ${{
									Number(selectedVendor.total_value || 0).toLocaleString()
								}} total
							</p>
						</div>
						<button
							@click="selectedVendor = null"
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
					<div v-if="vendorItems.length" class="space-y-1">
						<div
							v-for="item in vendorItems"
							:key="item.name"
							class="flex items-center gap-3 py-2 border-b border-gray-100 dark:border-warm-border/30 last:border-0"
						>
							<div
								class="w-10 h-10 rounded-lg overflow-hidden bg-gray-100 dark:bg-warm-dark-700 flex items-center justify-center shrink-0"
							>
								<img
									v-if="item.image"
									:src="item.image"
									class="w-full h-full object-cover"
								/>
								<span v-else class="text-xs text-gray-400">—</span>
							</div>
							<div class="min-w-0 flex-1">
								<div class="text-xs font-bold text-gray-900 dark:text-white truncate">
									{{ item.item_name }}
								</div>
								<div class="text-[10px] text-gray-500 truncate">
									{{ item.name }} ·
									<span
										v-if="item.item_group"
										class="text-gray-400"
										>{{ item.item_group }} ·</span
									>
									<span v-if="item.custom_metal_type" class="text-gray-400"
										>{{ item.custom_metal_type }}
										<span v-if="item.custom_purity">{{ item.custom_purity }}</span></span
									>
								</div>
							</div>
							<div
								v-if="item.custom_source"
								class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-100 dark:bg-blue-900/20 dark:text-blue-300"
							>
								{{ item.custom_source }}
							</div>
							<div class="text-right text-xs font-mono text-[#D4AF37] w-20">
								${{ Number(item.price || 0).toFixed(2) }}
							</div>
						</div>
					</div>
					<div
						v-else-if="!loadingItems"
						class="text-center py-10 text-sm text-gray-400"
					>
						No items for this vendor
					</div>
					<div
						v-if="loadingItems"
						class="flex items-center justify-center py-10"
					>
						<div
							class="animate-spin w-6 h-6 border-2 border-[#D4AF37] border-t-transparent rounded-full"
						></div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useStockStore } from '@/stores/stock.js'

const stock = useStockStore()
const search = ref('')
const activeSource = ref('')
const selectedVendor = ref(null)
const vendorItems = ref([])
const loadingItems = ref(false)

const sourceOptions = [
	{ label: 'All Sources', value: '' },
	{ label: 'QGold', value: 'QGold' },
	{ label: 'Stuller', value: 'Stuller' },
	{ label: 'Demo', value: 'Demo' },
]

let searchTimer = null
function debouncedSearch() {
	clearTimeout(searchTimer)
	searchTimer = setTimeout(loadData, 300)
}

function loadData() {
	stock.loadCatalogVendors({
		search: search.value || undefined,
		source: activeSource.value || undefined,
	})
}

watch(activeSource, () => loadData())

async function viewVendor(v) {
	selectedVendor.value = v
	vendorItems.value = []
	loadingItems.value = true
	try {
		const res = await stock.loadCatalogItems({
			vendor: v.vendor === '(Unassigned)' ? undefined : v.vendor,
			source: activeSource.value || undefined,
		})
		vendorItems.value = res?.items || []
	} catch (e) {
		console.warn('Could not load items', e)
	} finally {
		loadingItems.value = false
	}
}

function formatDate(s) {
	if (!s) return ''
	try {
		return new Date(s).toLocaleDateString()
	} catch {
		return s
	}
}

onMounted(loadData)
</script>
