<template>
	<div class="space-y-6">
		<p class="text-xs text-gray-500 dark:text-gray-400">
			Visual dashboards for cross-store analysis. Click to open.
		</p>

		<!-- Employee Quick Access — only shown for employee-tier users -->
		<div v-if="accessTier === 'employee'" class="space-y-3">
			<div class="flex items-center gap-2 mb-2">
				<span class="material-symbols-outlined !text-lg text-[#D4AF37]">person</span>
				<h3 class="text-sm font-bold text-gray-900 dark:text-white">My Performance</h3>
			</div>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<button
					v-for="card in employeeCards"
					:key="card.id"
					@click="handleOpen(card)"
					class="premium-card !p-5 text-left hover:!border-[#D4AF37] transition-all group flex items-start gap-4"
				>
					<div
						class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
						:class="card.bg"
					>
						<span class="material-symbols-outlined !text-xl" :class="card.text">{{
							card.icon
						}}</span>
					</div>
					<div class="min-w-0">
						<h4 class="text-sm font-bold text-gray-900 dark:text-white mb-0.5">
							{{ card.label }}
						</h4>
						<p class="text-[11px] text-gray-500 dark:text-gray-400 leading-4">
							{{ card.description }}
						</p>
					</div>
				</button>
			</div>
		</div>

		<!-- Categorized Dashboard Sections -->
		<div v-for="section in visibleSections" :key="section.id" class="space-y-3">
			<div class="flex items-center gap-2 mb-2">
				<span class="material-symbols-outlined !text-lg text-[#D4AF37]">{{
					section.icon
				}}</span>
				<h3 class="text-sm font-bold text-gray-900 dark:text-white">
					{{ section.label }}
				</h3>
				<span
					class="text-[10px] font-medium px-2 py-0.5 rounded-full"
					:class="section.badgeClass"
				>
					{{ section.badge }}
				</span>
			</div>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
				<button
					v-for="dash in section.dashboards"
					:key="dash.id"
					@click="$emit('openDashboard', dash.id)"
					class="premium-card !p-5 text-left hover:!border-[#D4AF37] transition-all group"
				>
					<div class="flex items-start gap-3">
						<div
							class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
							:class="dash.bg"
						>
							<span class="material-symbols-outlined !text-xl" :class="dash.text">{{
								dash.icon
							}}</span>
						</div>
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2 mb-0.5">
								<h4 class="text-sm font-bold text-gray-900 dark:text-white">
									{{ dash.label }}
								</h4>
								<span
									v-if="dash.restricted"
									class="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400"
								>
									{{ dash.restricted }}
								</span>
							</div>
							<p class="text-[11px] text-gray-500 dark:text-gray-400 leading-4">
								{{ dash.description }}
							</p>
						</div>
					</div>
					<div
						class="mt-3 flex items-center gap-1 text-[11px] font-bold text-[#D4AF37] group-hover:underline"
					>
						Open Dashboard
						<span class="material-symbols-outlined !text-sm">arrow_forward</span>
					</div>
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import { getAccessTier } from '@/router.js'

defineEmits(['openDashboard'])

const props = defineProps({
	roleContext: { type: Object, default: () => ({}) },
})

const accessTier = computed(() => {
	const role = props.roleContext?.primary_role
	if (!role) return 'employee'
	if (['System Manager', 'Accounts Manager'].includes(role)) return 'admin'
	if (
		['Store Manager', 'Sales Manager', 'Stock Manager', 'HR Manager', 'HR User'].includes(role)
	)
		return 'manager'
	return 'employee'
})

const employeeCards = [
	{
		id: 'revenue',
		label: 'Sales Dashboard',
		icon: 'monitoring',
		bg: 'bg-emerald-500/10',
		text: 'text-emerald-500',
		description: 'Your sales performance, transaction history, and daily revenue.',
	},
	{
		id: 'my_performance',
		label: 'My Performance',
		icon: 'trending_up',
		bg: 'bg-purple-500/10',
		text: 'text-purple-500',
		description: 'Personal sales targets, commission tracking, and attendance.',
		route: '/transactions',
	},
]

const sections = [
	{
		id: 'sales',
		label: 'Sales & Revenue',
		icon: 'storefront',
		badge: 'All Staff',
		badgeClass: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
		minTier: 'employee',
		dashboards: [
			{
				id: 'revenue',
				label: 'Revenue Dashboard',
				icon: 'monitoring',
				bg: 'bg-emerald-500/10',
				text: 'text-emerald-500',
				description:
					'Sales vs last year, category donut, tender stack, hourly heatmap, top salesperson.',
			},
		],
	},
	{
		id: 'operations',
		label: 'Operations',
		icon: 'inventory_2',
		badge: 'Manager+',
		badgeClass: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
		minTier: 'manager',
		dashboards: [
			{
				id: 'inventory',
				label: 'Inventory Dashboard',
				icon: 'inventory_2',
				bg: 'bg-slate-500/10',
				text: 'text-slate-500',
				description:
					'Stock value per store, aging buckets, velocity heatmap, shrinkage trend.',
			},
			{
				id: 'customer',
				label: 'Customer Dashboard',
				icon: 'group',
				bg: 'bg-purple-500/10',
				text: 'text-purple-500',
				description:
					'New vs returning, avg lifetime value, layaway cohort retention, repair NPS.',
			},
			{
				id: 'repairs',
				label: 'Repair Analytics',
				icon: 'build',
				bg: 'bg-amber-500/10',
				text: 'text-amber-500',
				description:
					'Repair volume, revenue trends, SLA compliance, technician leaderboard, AI insights.',
			},
		],
	},
	{
		id: 'intelligence',
		label: 'Intelligence & AI',
		icon: 'psychology',
		badge: 'Admin Only',
		badgeClass: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
		minTier: 'admin',
		dashboards: [
			{
				id: 'profit',
				label: 'Profit Intelligence',
				icon: 'trending_up',
				bg: 'bg-amber-500/10',
				text: 'text-amber-600',
				description:
					'Cost attribution, margin analysis, overhead allocation, pricing recommendations, AI loss predictions.',
				restricted: 'Admin',
			},
			{
				id: 'admin',
				label: 'Live Monitor',
				icon: 'visibility',
				bg: 'bg-blue-500/10',
				text: 'text-blue-500',
				description:
					'Real-time sales feed, active registers, tax override approvals, employee activity audit log.',
				restricted: 'Admin',
			},
			{
				id: 'command-center',
				label: 'Command Center',
				icon: 'cell_tower',
				bg: 'bg-cyan-500/10',
				text: 'text-cyan-500',
				description:
					'Multi-store repair ops, anomaly alerts, live WebSocket feed, store health monitoring.',
				restricted: 'Admin',
			},
		],
	},
]

const tierLevel = { employee: 1, manager: 2, admin: 3 }

const visibleSections = computed(() => {
	const level = tierLevel[accessTier.value] || 0
	return sections.filter((s) => (tierLevel[s.minTier] || 0) <= level)
})

function handleOpen(card) {
	if (card.route) {
		window.location.href = `/pos${card.route}`
	}
}
</script>
