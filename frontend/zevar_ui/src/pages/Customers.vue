<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<!-- Header -->
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Customers</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-white/5 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-white/10"
					>
						{{ filteredCustomers.length }} Clients
					</span>
				</div>
				<button
					class="px-4 py-2 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black text-xs font-bold rounded-lg hover:bg-gray-800 dark:hover:bg-[#b5952f] transition-all shadow-sm"
				>
					+ New Client
				</button>
			</div>

			<!-- Segment Tabs -->
			<div
				class="flex gap-1 bg-gray-100 dark:bg-[#1C1F26] p-1 rounded-xl mb-6 flex-shrink-0 overflow-x-auto"
			>
				<button
					v-for="seg in segments"
					:key="seg.value"
					@click="activeSegment = seg.value"
					class="flex-1 min-w-fit px-4 py-2 text-xs font-bold rounded-lg transition-all whitespace-nowrap"
					:class="
						activeSegment === seg.value
							? 'bg-white dark:bg-[#2a2d37] text-gray-900 dark:text-white shadow-sm'
							: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
					"
				>
					{{ seg.label }}
					<span class="ml-1 text-[10px] font-bold text-gray-400">{{
						getSegmentCount(seg.value)
					}}</span>
				</button>
			</div>

			<!-- Stats Row -->
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6 flex-shrink-0">
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Clients
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ customersData.length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						VIP Members
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ customersData.filter((c) => c.tier === 'VIP').length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Avg Purchase
					</div>
					<div class="text-2xl font-bold text-green-600">
						{{ formatCurrency(avgPurchase) }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Repeat Rate
					</div>
					<div class="text-2xl font-bold text-blue-500">68%</div>
				</div>
			</div>

			<!-- Customer Cards -->
			<div class="flex-1 overflow-auto min-h-0">
				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
					<div
						v-for="customer in filteredCustomers"
						:key="customer.id"
						class="premium-card !p-4 cursor-pointer group"
					>
						<div class="flex items-start gap-3 mb-3">
							<div
								class="w-11 h-11 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
								:class="
									customer.tier === 'VIP'
										? 'bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] text-[#0F1115]'
										: customer.tier === 'Regular'
										? 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
										: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
								"
							>
								{{
									customer.name
										.split(' ')
										.map((n) => n[0])
										.join('')
								}}
							</div>
							<div class="min-w-0 flex-1">
								<div
									class="font-bold text-gray-900 dark:text-white text-sm truncate"
								>
									{{ customer.name }}
								</div>
								<div class="text-[10px] text-gray-500 truncate">
									{{ customer.phone }}
								</div>
							</div>
							<span
								class="text-[9px] font-bold px-2 py-0.5 rounded-full shrink-0"
								:class="
									customer.tier === 'VIP'
										? 'bg-[#D4AF37]/15 text-[#D4AF37]'
										: customer.tier === 'Regular'
										? 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
										: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
								"
							>
								{{ customer.tier }}
							</span>
						</div>
						<div
							class="grid grid-cols-3 gap-2 text-center border-t border-gray-100 dark:border-white/5 pt-3"
						>
							<div>
								<div class="text-[10px] text-gray-500 mb-0.5">Purchases</div>
								<div class="text-xs font-bold text-gray-900 dark:text-white">
									{{ customer.purchases }}
								</div>
							</div>
							<div>
								<div class="text-[10px] text-gray-500 mb-0.5">Lifetime</div>
								<div class="text-xs font-bold text-[#D4AF37]">
									{{ formatCurrency(customer.lifetime) }}
								</div>
							</div>
							<div>
								<div class="text-[10px] text-gray-500 mb-0.5">Last Visit</div>
								<div class="text-xs font-bold text-gray-900 dark:text-white">
									{{ customer.lastVisit }}
								</div>
							</div>
						</div>
						<div
							v-if="customer.preferences.length > 0"
							class="flex flex-wrap gap-1 mt-3"
						>
							<span
								v-for="pref in customer.preferences"
								:key="pref"
								class="text-[9px] font-medium px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"
							>
								{{ pref }}
							</span>
						</div>
					</div>
				</div>

				<div v-if="filteredCustomers.length === 0" class="py-20 text-center">
					<p class="text-gray-400 text-sm">No clients found in this segment.</p>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { useUIStore } from '@/stores/ui.js'
import { ref, computed } from 'vue'

const ui = useUIStore()
const activeSegment = ref('all')

const segments = [
	{ value: 'all', label: 'All' },
	{ value: 'VIP', label: 'VIP' },
	{ value: 'Regular', label: 'Regular' },
	{ value: 'New', label: 'New' },
	{ value: 'Inactive', label: 'Inactive' },
]

const customersData = ref([
	{
		id: 1,
		name: 'Priya Sharma',
		phone: '+1 (555) 234-5678',
		email: 'priya@email.com',
		tier: 'VIP',
		purchases: 24,
		lifetime: 128500,
		lastVisit: '2 days ago',
		preferences: ['Yellow Gold', 'Diamonds', 'Bridal'],
	},
	{
		id: 2,
		name: 'Michael Chen',
		phone: '+1 (555) 345-6789',
		email: 'mchen@email.com',
		tier: 'VIP',
		purchases: 18,
		lifetime: 94200,
		lastVisit: '1 week ago',
		preferences: ['Platinum', 'Sapphires'],
	},
	{
		id: 3,
		name: 'Sarah Williams',
		phone: '+1 (555) 456-7890',
		email: 'swilliams@email.com',
		tier: 'Regular',
		purchases: 8,
		lifetime: 22400,
		lastVisit: '3 days ago',
		preferences: ['Rose Gold', 'Earrings'],
	},
	{
		id: 4,
		name: 'Raj Patel',
		phone: '+1 (555) 567-8901',
		email: 'raj@email.com',
		tier: 'VIP',
		purchases: 32,
		lifetime: 186000,
		lastVisit: 'Yesterday',
		preferences: ['22K Gold', 'Kundan', 'Necklaces'],
	},
	{
		id: 5,
		name: 'Emily Rodriguez',
		phone: '+1 (555) 678-9012',
		email: 'emily.r@email.com',
		tier: 'Regular',
		purchases: 5,
		lifetime: 8500,
		lastVisit: '2 weeks ago',
		preferences: ['Silver', 'Bracelets'],
	},
	{
		id: 6,
		name: 'David Kim',
		phone: '+1 (555) 789-0123',
		email: 'dkim@email.com',
		tier: 'New',
		purchases: 1,
		lifetime: 3200,
		lastVisit: 'Today',
		preferences: ['White Gold'],
	},
	{
		id: 7,
		name: 'Ananya Gupta',
		phone: '+1 (555) 890-1234',
		email: 'ananya@email.com',
		tier: 'VIP',
		purchases: 15,
		lifetime: 72800,
		lastVisit: '4 days ago',
		preferences: ['Polki', 'Bridal Sets', 'Bangles'],
	},
	{
		id: 8,
		name: 'James Thompson',
		phone: '+1 (555) 901-2345',
		email: 'jthompson@email.com',
		tier: 'Regular',
		purchases: 6,
		lifetime: 15600,
		lastVisit: '1 week ago',
		preferences: ['Rings', 'Diamonds'],
	},
	{
		id: 9,
		name: 'Lisa Park',
		phone: '+1 (555) 012-3456',
		email: 'lpark@email.com',
		tier: 'Inactive',
		purchases: 3,
		lifetime: 7200,
		lastVisit: '3 months ago',
		preferences: ['Earrings'],
	},
	{
		id: 10,
		name: 'Ahmed Hassan',
		phone: '+1 (555) 123-4567',
		email: 'ahmed@email.com',
		tier: 'New',
		purchases: 2,
		lifetime: 5800,
		lastVisit: '5 days ago',
		preferences: ['Yellow Gold', 'Chains'],
	},
	{
		id: 11,
		name: 'Jennifer Lee',
		phone: '+1 (555) 234-5670',
		email: 'jlee@email.com',
		tier: 'Regular',
		purchases: 10,
		lifetime: 28900,
		lastVisit: '1 day ago',
		preferences: ['Pendants', 'Emeralds'],
	},
	{
		id: 12,
		name: 'Robert Singh',
		phone: '+1 (555) 345-6780',
		email: 'rsingh@email.com',
		tier: 'Inactive',
		purchases: 2,
		lifetime: 4100,
		lastVisit: '6 months ago',
		preferences: ['Rings'],
	},
])

const avgPurchase = computed(() => {
	const total = customersData.value.reduce((s, c) => s + c.lifetime, 0)
	const purchases = customersData.value.reduce((s, c) => s + c.purchases, 0)
	return purchases > 0 ? total / purchases : 0
})

function getSegmentCount(seg) {
	if (seg === 'all') return customersData.value.length
	return customersData.value.filter((c) => c.tier === seg).length
}

const filteredCustomers = computed(() => {
	let customers = [...customersData.value]

	if (activeSegment.value !== 'all') {
		customers = customers.filter((c) => c.tier === activeSegment.value)
	}

	if (ui.searchQuery) {
		const q = ui.searchQuery.toLowerCase()
		customers = customers.filter(
			(c) =>
				c.name.toLowerCase().includes(q) ||
				c.phone.includes(q) ||
				c.email.toLowerCase().includes(q)
		)
	}

	return customers
})

function formatCurrency(val) {
	if (!val) return '$0'
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		maximumFractionDigits: 0,
	}).format(val)
}
</script>
