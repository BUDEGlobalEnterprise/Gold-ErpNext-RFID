<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Reports</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-white/5 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-white/10"
					>
						Dashboard
					</span>
				</div>
				<div class="flex gap-2">
					<select
						v-model="period"
						class="h-9 bg-white dark:bg-[#1C1F26] border border-gray-200 dark:border-white/10 rounded-lg text-xs font-bold text-gray-700 dark:text-gray-300 px-3 pr-8 focus:ring-2 focus:ring-[#D4AF37] outline-none cursor-pointer appearance-none"
					>
						<option value="today">Today</option>
						<option value="week">This Week</option>
						<option value="month">This Month</option>
						<option value="quarter">This Quarter</option>
					</select>
					<button
						class="px-4 py-2 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black text-xs font-bold rounded-lg hover:bg-gray-800 dark:hover:bg-[#b5952f] transition-all shadow-sm flex items-center gap-1.5"
					>
						<svg
							class="w-3.5 h-3.5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							></path>
						</svg>
						Export
					</button>
				</div>
			</div>

			<div class="flex-1 overflow-auto min-h-0">
				<!-- KPI Cards -->
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
					<div class="premium-card !p-4" v-for="kpi in kpis" :key="kpi.label">
						<div class="flex items-center justify-between mb-2">
							<div
								class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
							>
								{{ kpi.label }}
							</div>
							<div
								class="w-8 h-8 rounded-lg flex items-center justify-center"
								:class="kpi.iconBg"
							>
								<svg
									class="w-4 h-4"
									:class="kpi.iconColor"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										:d="kpi.icon"
									></path>
								</svg>
							</div>
						</div>
						<div class="text-2xl font-bold" :class="kpi.valueColor">
							{{ kpi.value }}
						</div>
						<div class="flex items-center gap-1 mt-1">
							<span
								class="text-[10px] font-bold"
								:class="kpi.changePositive ? 'text-green-600' : 'text-red-500'"
							>
								{{ kpi.changePositive ? '↑' : '↓' }} {{ kpi.change }}
							</span>
							<span class="text-[10px] text-gray-500">vs last period</span>
						</div>
					</div>
				</div>

				<!-- Charts Row -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
					<!-- Sales by Category -->
					<div class="premium-card">
						<div class="text-xs font-bold text-gray-900 dark:text-white mb-4">
							Sales by Category
						</div>
						<div class="space-y-3">
							<div v-for="cat in categoryBreakdown" :key="cat.name">
								<div class="flex items-center justify-between text-[11px] mb-1">
									<span class="font-medium text-gray-700 dark:text-gray-300">{{
										cat.name
									}}</span>
									<span class="font-bold text-gray-900 dark:text-white"
										>{{ cat.sales }} pcs ·
										{{ formatCurrency(cat.revenue) }}</span
									>
								</div>
								<div
									class="w-full h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden"
								>
									<div
										class="h-full rounded-full transition-all"
										:style="{ width: cat.pct + '%' }"
										:class="cat.color"
									></div>
								</div>
							</div>
						</div>
					</div>

					<!-- Top Salespersons -->
					<div class="premium-card">
						<div class="text-xs font-bold text-gray-900 dark:text-white mb-4">
							Top Salespersons
						</div>
						<div class="space-y-3">
							<div
								v-for="(sp, idx) in topSalespersons"
								:key="sp.name"
								class="flex items-center gap-3"
							>
								<div
									class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
									:class="
										idx === 0
											? 'bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] text-[#0F1115]'
											: idx === 1
											? 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
											: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400'
									"
								>
									{{ idx + 1 }}
								</div>
								<div class="flex-1 min-w-0">
									<div
										class="text-xs font-bold text-gray-900 dark:text-white truncate"
									>
										{{ sp.name }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ sp.transactions }} transactions
									</div>
								</div>
								<div class="text-right">
									<div class="text-xs font-bold text-[#D4AF37] font-mono">
										{{ formatCurrency(sp.revenue) }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ sp.commission }}% comm
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Metal Performance & Recent High-Value Sales -->
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					<div class="premium-card">
						<div class="text-xs font-bold text-gray-900 dark:text-white mb-4">
							Performance by Metal
						</div>
						<div class="space-y-3">
							<div
								v-for="metal in metalPerformance"
								:key="metal.name"
								class="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-white/[0.02]"
							>
								<div class="flex items-center gap-2">
									<div class="w-3 h-3 rounded-full" :class="metal.dot"></div>
									<span
										class="text-xs font-bold text-gray-900 dark:text-white"
										>{{ metal.name }}</span
									>
								</div>
								<div class="text-right">
									<div class="text-xs font-bold text-[#D4AF37] font-mono">
										{{ formatCurrency(metal.revenue) }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ metal.units }} units
									</div>
								</div>
							</div>
						</div>
					</div>

					<div class="premium-card">
						<div class="text-xs font-bold text-gray-900 dark:text-white mb-4">
							Recent High-Value Sales
						</div>
						<div class="space-y-3">
							<div
								v-for="sale in recentSales"
								:key="sale.id"
								class="flex items-center gap-3 p-2 rounded-lg bg-gray-50 dark:bg-white/[0.02]"
							>
								<div
									class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-400 shrink-0 text-[10px]"
								>
									IMG
								</div>
								<div class="flex-1 min-w-0">
									<div
										class="text-xs font-bold text-gray-900 dark:text-white truncate"
									>
										{{ sale.item }}
									</div>
									<div class="text-[10px] text-gray-500">
										{{ sale.customer }} · {{ sale.date }}
									</div>
								</div>
								<div class="text-sm font-bold text-[#D4AF37] font-mono shrink-0">
									{{ formatCurrency(sale.amount) }}
								</div>
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

const period = ref('week')

const kpis = [
	{
		label: 'Revenue',
		value: '$142,800',
		change: '12.5%',
		changePositive: true,
		valueColor: 'text-[#D4AF37]',
		icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
		iconBg: 'bg-[#D4AF37]/10',
		iconColor: 'text-[#D4AF37]',
	},
	{
		label: 'Transactions',
		value: '47',
		change: '8.2%',
		changePositive: true,
		valueColor: 'text-gray-900 dark:text-white',
		icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
		iconBg: 'bg-blue-500/10',
		iconColor: 'text-blue-500',
	},
	{
		label: 'Avg Ticket',
		value: '$3,038',
		change: '4.1%',
		changePositive: true,
		valueColor: 'text-green-600',
		icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
		iconBg: 'bg-green-500/10',
		iconColor: 'text-green-500',
	},
	{
		label: 'Layaways',
		value: '8',
		change: '2',
		changePositive: false,
		valueColor: 'text-gray-900 dark:text-white',
		icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
		iconBg: 'bg-purple-500/10',
		iconColor: 'text-purple-500',
	},
]

const categoryBreakdown = [
	{ name: 'Rings', sales: 18, revenue: 52400, pct: 85, color: 'bg-[#D4AF37]' },
	{ name: 'Necklaces', sales: 12, revenue: 38200, pct: 68, color: 'bg-amber-400' },
	{ name: 'Earrings', sales: 15, revenue: 22800, pct: 52, color: 'bg-yellow-300' },
	{ name: 'Bracelets', sales: 8, revenue: 18400, pct: 40, color: 'bg-orange-400' },
	{ name: 'Bangles', sales: 5, revenue: 11000, pct: 28, color: 'bg-rose-400' },
]

const topSalespersons = [
	{ name: 'Aisha Patel', transactions: 18, revenue: 52400, commission: 3.5 },
	{ name: 'James Wilson', transactions: 14, revenue: 41200, commission: 3.0 },
	{ name: 'Maria Santos', transactions: 11, revenue: 28800, commission: 3.0 },
	{ name: 'David Chen', transactions: 8, revenue: 20400, commission: 2.5 },
]

const metalPerformance = [
	{ name: 'Yellow Gold', revenue: 68400, units: 28, dot: 'bg-yellow-400' },
	{ name: 'White Gold', revenue: 32200, units: 12, dot: 'bg-gray-300' },
	{ name: 'Platinum', revenue: 24600, units: 5, dot: 'bg-blue-300' },
	{ name: 'Rose Gold', revenue: 12800, units: 8, dot: 'bg-pink-300' },
	{ name: 'Silver', revenue: 4800, units: 15, dot: 'bg-gray-400' },
]

const recentSales = [
	{ id: 1, item: 'Maharani Bridal Set', customer: 'Ananya Gupta', date: 'Today', amount: 58000 },
	{
		id: 2,
		item: 'Heritage Polki Necklace',
		customer: 'Raj Patel',
		date: 'Yesterday',
		amount: 24800,
	},
	{
		id: 3,
		item: 'Diamond Tennis Necklace',
		customer: 'Michael Chen',
		date: '2 days ago',
		amount: 18500,
	},
	{
		id: 4,
		item: 'Diamond Tennis Bracelet',
		customer: 'Sarah Williams',
		date: '3 days ago',
		amount: 14200,
	},
]

function formatCurrency(val) {
	return val
		? new Intl.NumberFormat('en-US', {
				style: 'currency',
				currency: 'USD',
				maximumFractionDigits: 0,
		  }).format(val)
		: '$0'
}
</script>
