<template>
	<Teleport to="body">
		<Transition name="slide">
			<div v-if="item" class="fixed inset-0 z-[90] flex justify-end">
				<div
					class="absolute inset-0 bg-black/40 backdrop-blur-sm"
					@click="$emit('close')"
				></div>
				<div
					class="relative w-full max-w-lg bg-white dark:bg-warm-card shadow-2xl overflow-y-auto"
				>
					<div
						class="sticky top-0 bg-white dark:bg-warm-card border-b border-gray-100 dark:border-warm-border/50 p-4 flex items-center justify-between z-10"
					>
						<h3 class="text-lg font-bold text-gray-900 dark:text-white truncate">
							{{ item.name }}
						</h3>
						<button
							@click="$emit('close')"
							class="p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full"
						>
							<svg
								class="w-5 h-5 text-gray-400"
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

					<div v-if="loading" class="flex items-center justify-center py-16">
						<div class="text-sm text-gray-400">Loading details...</div>
					</div>

					<div v-else-if="loadError" class="p-4 space-y-4">
						<div
							class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
						>
							<div class="flex items-start gap-3">
								<svg
									class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								<div>
									<div class="text-sm font-bold text-red-700 dark:text-red-400">
										Failed to load details
									</div>
									<div class="text-xs text-red-600 dark:text-red-300 mt-1">
										{{ loadError }}
									</div>
								</div>
							</div>
							<button
								@click="fetchDetails"
								class="mt-3 w-full py-2 bg-red-600 text-white rounded-lg text-xs font-bold hover:bg-red-700 transition"
							>
								Retry
							</button>
						</div>

						<div class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-4">
							<div class="text-xs text-gray-500 mb-1">{{ item.code }}</div>
							<div class="text-base font-bold text-gray-900 dark:text-white">
								{{ item.name }}
							</div>
							<div
								v-if="item.metal || item.purity"
								class="flex flex-wrap gap-1.5 mt-2"
							>
								<span
									v-if="item.metal"
									class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>{{ item.metal }}</span
								>
								<span
									v-if="item.purity"
									class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-gray-200 dark:bg-warm-dark-700 text-gray-700 dark:text-gray-300"
									>{{ item.purity }}</span
								>
							</div>
							<div v-if="item.weight" class="mt-3 text-xs">
								<span class="text-gray-500">Weight</span>
								<div class="font-bold">{{ item.weight }}g</div>
							</div>
						</div>
					</div>

					<div v-else-if="details" class="p-4 space-y-4">
						<div class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-4">
							<div class="text-xs text-gray-500 mb-1">{{ details.item_code }}</div>
							<div class="text-base font-bold text-gray-900 dark:text-white">
								{{ details.item_name }}
							</div>
							<div class="flex flex-wrap gap-1.5 mt-2">
								<span
									v-if="details.custom_metal_type"
									class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>{{ details.custom_metal_type }}</span
								>
								<span
									v-if="details.custom_purity"
									class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-gray-200 dark:bg-warm-dark-700 text-gray-700 dark:text-gray-300"
									>{{ details.custom_purity }}</span
								>
								<span
									v-if="details.custom_jewelry_type"
									class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
									>{{ details.custom_jewelry_type }}</span
								>
							</div>
							<div class="grid grid-cols-3 gap-3 mt-3 text-xs">
								<div v-if="details.custom_gross_weight_g">
									<span class="text-gray-500">Gross</span>
									<div class="font-bold">
										{{ details.custom_gross_weight_g }}g
									</div>
								</div>
								<div v-if="details.custom_stone_weight_g">
									<span class="text-gray-500">Stone</span>
									<div class="font-bold">
										{{ details.custom_stone_weight_g }}g
									</div>
								</div>
								<div v-if="details.custom_net_weight_g">
									<span class="text-gray-500">Net</span>
									<div class="font-bold">{{ details.custom_net_weight_g }}g</div>
								</div>
							</div>
						</div>

						<div class="grid grid-cols-3 gap-2">
							<div
								class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 text-center"
							>
								<div class="text-[10px] font-bold text-gray-500 uppercase">
									Stock
								</div>
								<div
									class="text-xl font-bold"
									:class="
										details.total_qty <= 0
											? 'text-red-500'
											: details.total_qty < 5
											? 'text-amber-500'
											: 'text-green-600'
									"
								>
									{{ details.total_qty }}
								</div>
							</div>
							<div
								class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 text-center"
							>
								<div class="text-[10px] font-bold text-gray-500 uppercase">
									Value
								</div>
								<div class="text-xl font-bold text-[#D4AF37]">
									{{ fmtCur(details.total_value) }}
								</div>
							</div>
							<div
								class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 text-center"
							>
								<div class="text-[10px] font-bold text-gray-500 uppercase">
									MSRP
								</div>
								<div class="text-xl font-bold text-gray-900 dark:text-white">
									{{ fmtCur(details.custom_msrp || details.standard_rate) }}
								</div>
							</div>
						</div>

						<div
							v-if="
								details.custom_vendor_sku ||
								details.custom_barcode ||
								details.custom_vendor
							"
							class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-3 space-y-1.5"
						>
							<div
								v-if="details.custom_vendor_sku"
								class="flex justify-between text-xs"
							>
								<span class="text-gray-500">Vendor SKU</span>
								<span class="font-mono font-bold">{{
									details.custom_vendor_sku
								}}</span>
							</div>
							<div
								v-if="details.custom_barcode"
								class="flex justify-between text-xs"
							>
								<span class="text-gray-500">Barcode</span>
								<span class="font-mono">{{ details.custom_barcode }}</span>
							</div>
							<div v-if="details.custom_vendor" class="flex justify-between text-xs">
								<span class="text-gray-500">Vendor</span>
								<span>{{ details.custom_vendor }}</span>
							</div>
							<div v-if="details.custom_source" class="flex justify-between text-xs">
								<span class="text-gray-500">Source</span>
								<span>{{ details.custom_source }}</span>
							</div>
							<div
								v-if="details.custom_cost_price"
								class="flex justify-between text-xs"
							>
								<span class="text-gray-500">Cost</span>
								<span class="font-bold">{{
									fmtCur(details.custom_cost_price)
								}}</span>
							</div>
						</div>

						<div v-if="hasStoreBreakdown">
							<div class="text-xs font-bold text-gray-500 uppercase mb-2">
								Store Breakdown
							</div>
							<div class="space-y-1">
								<div
									v-for="(store, code) in details.store_breakdown"
									:key="code"
									class="flex items-center justify-between py-1.5 px-3 bg-gray-50 dark:bg-warm-dark-900 rounded-lg"
								>
									<div>
										<span class="text-xs font-bold">{{ code }}</span>
										<span class="text-xs text-gray-500 ml-1">{{
											store.name
										}}</span>
									</div>
									<span class="text-sm font-bold text-green-600">{{
										store.qty
									}}</span>
								</div>
							</div>
						</div>

						<div v-if="details.serials && details.serials.length > 0">
							<div class="text-xs font-bold text-gray-500 uppercase mb-2">
								Serial Numbers ({{ details.serials.length }})
							</div>
							<div class="space-y-1 max-h-40 overflow-y-auto">
								<div
									v-for="sn in details.serials"
									:key="sn.name"
									class="flex items-center justify-between py-1.5 px-3 bg-gray-50 dark:bg-warm-dark-900 rounded-lg text-xs"
								>
									<div>
										<span class="font-mono font-bold">{{ sn.name }}</span>
									</div>
									<div class="flex items-center gap-2">
										<span class="text-gray-500">{{
											(sn.warehouse || '').split(' - ')[0]
										}}</span>
										<span
											class="text-[9px] px-1.5 py-0.5 rounded-full"
											:class="
												sn.status === 'Active'
													? 'bg-green-100 text-green-700'
													: 'bg-gray-100 text-gray-500'
											"
											>{{ sn.status }}</span
										>
									</div>
								</div>
							</div>
						</div>

						<div v-if="details.reservations && details.reservations.length > 0">
							<div class="text-xs font-bold text-gray-500 uppercase mb-2">
								Active Reservations
							</div>
							<div
								v-for="res in details.reservations"
								:key="res.name"
								class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-2 text-xs mb-1"
							>
								<span class="font-bold">{{ res.customer }}</span> —
								{{ res.serial_no }} — until {{ res.hold_until }}
							</div>
						</div>

						<div
							class="grid grid-cols-2 gap-2 pt-2 border-t border-gray-100 dark:border-warm-border/30"
						>
							<button
								@click="openEdit"
								class="col-span-2 flex items-center justify-center gap-1.5 py-2.5 bg-blue-600 text-white rounded-lg text-xs font-bold hover:bg-blue-700 transition"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
									/>
								</svg>
								Edit Item
							</button>
							<button
								@click="openLifecycle"
								class="flex items-center justify-center gap-1.5 py-2.5 border rounded-lg text-xs font-bold hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								Lifecycle
							</button>
							<button
								@click="openReserve"
								class="flex items-center justify-center gap-1.5 py-2.5 border rounded-lg text-xs font-bold hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								Reserve
							</button>
							<button
								@click="openDamage"
								class="flex items-center justify-center gap-1.5 py-2.5 border rounded-lg text-xs font-bold hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
									/>
								</svg>
								Damage
							</button>
							<button
								@click="openPush"
								class="flex items-center justify-center gap-1.5 py-2.5 border rounded-lg text-xs font-bold hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
									/>
								</svg>
								Push
							</button>
							<button
								@click="openTransfer"
								class="col-span-2 flex items-center justify-center gap-1.5 py-2.5 border rounded-lg text-xs font-bold hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
									/>
								</svg>
								Transfer
							</button>
						</div>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { call } from 'frappe-ui'

const props = defineProps({
	item: { type: Object, default: null },
})

const emit = defineEmits(['close', 'reserve', 'damage', 'lifecycle', 'push', 'transfer', 'edit'])

const loading = ref(false)
const details = ref(null)
const loadError = ref('')

const hasStoreBreakdown = ref(false)

async function fetchDetails() {
	if (!props.item) {
		details.value = null
		loadError.value = ''
		return
	}
	loading.value = true
	loadError.value = ''
	try {
		const res = await call('zevar_core.services.stock_reduction.ui_get_item_inventory', {
			item_code: props.item.code,
		})
		details.value = res
		hasStoreBreakdown.value =
			res.store_breakdown && Object.keys(res.store_breakdown).length > 0
	} catch (err) {
		details.value = null
		loadError.value = err?.message || 'Unable to load item details. Please try again.'
	} finally {
		loading.value = false
	}
}

watch(() => props.item, fetchDetails, { immediate: true })

function getFirstSerial() {
	if (details.value?.serials?.length > 0) return details.value.serials[0].name
	return props.item?.serialNo || props.item?.code || ''
}

function openLifecycle() {
	emit('lifecycle')
}
function openReserve() {
	emit('reserve')
}
function openDamage() {
	emit('damage')
}
function openPush() {
	emit('push')
}
function openTransfer() {
	emit('transfer')
}
function openEdit() {
	emit('edit')
}

function fmtCur(val) {
	if (!val) return '$0'
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		maximumFractionDigits: 0,
	}).format(val)
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
	transition: transform 0.25s ease, opacity 0.2s ease;
}
.slide-enter-from,
.slide-leave-to {
	transform: translateX(100%);
	opacity: 0;
}
</style>
