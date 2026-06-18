<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0 flex-wrap">
				<button
					@click="$router.push('/reports')"
					class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors"
				>
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-slate-500/10">
					<span class="material-symbols-outlined !text-xl text-slate-500"
						>inventory_2</span
					>
				</div>
				<div>
					<h2 class="premium-title !text-xl">Inventory Dashboard</h2>
					<p class="text-[10px] text-gray-400">
						Stock value, aging, velocity, shrinkage trend
					</p>
				</div>
				<button
					@click="refresh"
					class="ml-auto w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-slate-500 transition-colors"
					:class="{ 'animate-spin': loading }"
				>
					<span class="material-symbols-outlined !text-base">refresh</span>
				</button>
			</div>

			<div class="flex-1 overflow-auto space-y-4 pr-1">
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
					<KPICard
						label="Total Items"
						:value="kpi.total_items"
						icon="category"
						color="slate"
						:loading="loading"
					/>
					<KPICard
						label="Total Value"
						:value="'$' + fmt(kpi.total_value)"
						icon="account_balance"
						color="emerald"
						:loading="loading"
					/>
					<KPICard
						label="Low Stock"
						:value="kpi.low_stock"
						icon="warning"
						color="red"
						:loading="loading"
					/>
					<KPICard
						label="In Transit"
						:value="kpi.in_transit"
						icon="local_shipping"
						color="amber"
						:loading="loading"
					/>
				</div>

				<!-- Stock by Store -->
				<div class="premium-card !p-3 sm:!p-5">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
						Stock Value by Store
					</h3>
					<div v-if="loading" class="space-y-2">
						<div
							v-for="n in 3"
							:key="n"
							class="h-4 bg-gray-100 dark:bg-gray-800 rounded-full animate-pulse"
						></div>
					</div>
					<div v-else-if="storeValues.length" class="space-y-2">
						<div
							v-for="store in storeValues"
							:key="store.warehouse"
							class="flex items-center gap-3"
						>
							<span
								class="text-xs font-bold text-gray-900 dark:text-white w-20 truncate"
								>{{ store.name || store.warehouse }}</span
							>
							<div
								class="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-4 overflow-hidden"
							>
								<div
									class="h-full rounded-full bg-slate-500/70 dark:bg-slate-400/50"
									:style="{ width: store.pct + '%' }"
								></div>
							</div>
							<span
								class="text-xs font-black text-gray-700 dark:text-gray-200 shrink-0"
								>${{ fmt(store.value) }}</span
							>
						</div>
					</div>
					<p v-else class="text-xs text-gray-400 text-center py-4">
						No stock data available
					</p>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<!-- Aging Buckets -->
					<div class="premium-card !p-3 sm:!p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Aging Buckets
						</h3>
						<div v-if="loading" class="space-y-2">
							<div
								v-for="n in 4"
								:key="n"
								class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
							></div>
						</div>
						<div v-else class="space-y-2">
							<div
								v-for="bucket in agingBuckets"
								:key="bucket.label"
								class="flex items-center justify-between"
							>
								<span class="text-xs text-gray-600 dark:text-gray-400">{{
									bucket.label
								}}</span>
								<span class="text-xs font-bold text-gray-900 dark:text-white"
									>{{ bucket.count }} items</span
								>
							</div>
						</div>
					</div>

					<!-- Shrinkage Trend -->
					<div class="premium-card !p-3 sm:!p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">
							Shrinkage Trend (6 months)
						</h3>
						<div v-if="loading" class="h-32 sm:h-40 flex items-center justify-center">
							<span class="material-symbols-outlined animate-spin text-gray-300"
								>progress_activity</span
							>
						</div>
						<div
							v-else-if="shrinkageTrend.length"
							class="h-32 sm:h-40 overflow-x-auto"
						>
							<div class="flex items-end gap-2 min-w-[300px] h-full">
								<div
									v-for="(m, i) in shrinkageTrend"
									:key="i"
									class="flex-1 flex flex-col items-center gap-1 group cursor-default"
								>
									<span
										class="text-[8px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity"
										>${{ fmt(m.value) }}</span
									>
									<div
										class="w-full rounded-t bg-red-500/60 dark:bg-red-400/40 min-h-[2px] hover:bg-red-500 transition-colors"
										:style="{ height: m.height + '%' }"
									></div>
									<span class="text-[8px] text-gray-400">{{ m.label }}</span>
								</div>
							</div>
						</div>
						<p v-else class="text-xs text-gray-400 text-center py-8">
							No shrinkage data
						</p>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { fmt } from '@/utils/format'
import { ref, watch } from 'vue'
import KPICard from '@/components/reports/KPICard.vue'
import { useSessionStore } from '@/stores/session.js'

const session = useSessionStore()
const kpi = ref({ total_items: 0, total_value: 0, low_stock: 0, in_transit: 0 })
const storeValues = ref([])
const agingBuckets = ref([
	{ label: '< 30 days', count: 0 },
	{ label: '30-90 days', count: 0 },
	{ label: '90-180 days', count: 0 },
	{ label: '> 180 days', count: 0 },
])
const shrinkageTrend = ref([])
const loading = ref(true)
const error = ref(null)

async function refresh() {
	loading.value = true
	error.value = null
	try {
		const url = new URL(
			'/api/method/zevar_core.api.inventory_dashboard.get_dashboard_data',
			window.location.origin
		)
		if (session.currentWarehouse) {
			url.searchParams.append('warehouse', session.currentWarehouse)
		}
		const res = await fetch(url.toString(), {
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		if (!res.ok) throw new Error('Failed to load inventory data')
		const json = await res.json()
		const data = json.message || json
		kpi.value = data.kpi || kpi.value
		storeValues.value = data.store_values || []
		agingBuckets.value = data.aging || agingBuckets.value
		shrinkageTrend.value = data.shrinkage || []
	} catch (e) {
		error.value = e.message
		console.error('Inventory dashboard error:', e)
	} finally {
		loading.value = false
	}
}

watch(() => session.currentWarehouse, refresh)

refresh()
</script>
