<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0">
				<button @click="$router.push('/reports')" class="w-9 h-9 rounded-lg flex items-center justify-center border border-gray-200 dark:border-warm-border hover:border-[#D4AF37] text-gray-500 dark:text-gray-400 hover:text-[#D4AF37] transition-colors">
					<span class="material-symbols-outlined !text-lg">arrow_back</span>
				</button>
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-slate-500/10">
					<span class="material-symbols-outlined !text-xl text-slate-500">inventory_2</span>
				</div>
				<div>
					<h2 class="premium-title !text-xl">Inventory Dashboard</h2>
					<p class="text-[10px] text-gray-400">Stock value, aging, velocity, shrinkage trend</p>
				</div>
			</div>

			<div class="flex-1 overflow-auto space-y-4 pr-1">
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
					<KPICard label="Total Items" :value="kpi.total_items" icon="category" color="slate" />
					<KPICard label="Total Value" :value="'$' + fmt(kpi.total_value)" icon="account_balance" color="emerald" />
					<KPICard label="Low Stock" :value="kpi.low_stock" icon="warning" color="red" />
					<KPICard label="In Transit" :value="kpi.in_transit" icon="local_shipping" color="amber" />
				</div>

				<div class="premium-card !p-5">
					<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Stock Value by Store</h3>
					<div class="space-y-2">
						<div v-for="store in storeValues" :key="store.name" class="flex items-center gap-3">
							<span class="text-xs font-bold text-gray-900 dark:text-white w-20 truncate">{{ store.name }}</span>
							<div class="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-4 overflow-hidden">
								<div class="h-full rounded-full bg-slate-500/70 dark:bg-slate-400/50" :style="{ width: store.pct + '%' }"></div>
							</div>
							<span class="text-xs font-black text-gray-700 dark:text-gray-200 shrink-0">${{ fmt(store.value) }}</span>
						</div>
					</div>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Aging Buckets</h3>
						<div class="space-y-2">
							<div v-for="bucket in agingBuckets" :key="bucket.label" class="flex items-center justify-between">
								<span class="text-xs text-gray-600 dark:text-gray-400">{{ bucket.label }}</span>
								<span class="text-xs font-bold text-gray-900 dark:text-white">{{ bucket.count }} items</span>
							</div>
						</div>
					</div>

					<div class="premium-card !p-5">
						<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">Shrinkage Trend (6 months)</h3>
						<div class="h-40 flex items-end gap-2">
							<div v-for="(m, i) in shrinkageTrend" :key="i" class="flex-1 flex flex-col items-center gap-1">
								<div class="w-full rounded-t bg-red-500/60 dark:bg-red-400/40 min-h-[2px]" :style="{ height: m.height + '%' }"></div>
								<span class="text-[8px] text-gray-400">{{ m.label }}</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { ref } from 'vue'
import KPICard from '@/components/reports/KPICard.vue'

const kpi = ref({ total_items: 0, total_value: 0, low_stock: 0, in_transit: 0 })

const storeValues = ref([
	{ name: 'NY-01', value: 0, pct: 20 },
	{ name: 'Miami-01', value: 0, pct: 20 },
	{ name: 'LA-01', value: 0, pct: 20 },
	{ name: 'Houston-01', value: 0, pct: 20 },
	{ name: 'Chicago-01', value: 0, pct: 20 },
])

const agingBuckets = ref([
	{ label: '< 30 days', count: 0 },
	{ label: '30–90 days', count: 0 },
	{ label: '90–180 days', count: 0 },
	{ label: '> 180 days', count: 0 },
])

const shrinkageTrend = ref(Array.from({ length: 6 }, (_, i) => ({
	label: ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'][i],
	height: Math.max(5, Math.random() * 60),
})))

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}
</script>
