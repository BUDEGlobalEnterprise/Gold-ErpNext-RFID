<template>
	<div class="space-y-4">
		<p class="text-xs text-gray-500 dark:text-gray-400">
			Visual dashboards for cross-store analysis. Click to open.
		</p>
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<button
				v-for="dash in dashboards"
				:key="dash.id"
				@click="$emit('openDashboard', dash.id)"
				class="premium-card !p-6 text-left hover:!border-[#D4AF37] transition-all group"
			>
				<div
					class="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
					:class="dash.bg"
				>
					<span class="material-symbols-outlined !text-2xl" :class="dash.text">{{
						dash.icon
					}}</span>
				</div>
				<h3 class="text-base font-bold text-gray-900 dark:text-white mb-1">
					{{ dash.label }}
				</h3>
				<p class="text-[11px] text-gray-500 dark:text-gray-400 leading-4">
					{{ dash.description }}
				</p>
				<div
					class="mt-3 flex items-center gap-1 text-[11px] font-bold text-[#D4AF37] group-hover:underline"
				>
					Open Dashboard
					<span class="material-symbols-outlined !text-sm">arrow_forward</span>
				</div>
			</button>
		</div>
	</div>
</template>

<script setup>
defineEmits(['openDashboard'])

const dashboards = [
	{
		id: 'revenue',
		label: 'Revenue Dashboard',
		icon: 'monitoring',
		bg: 'bg-emerald-500/10',
		text: 'text-emerald-500',
		description:
			'Sales vs last year, category donut, tender stack, hourly heatmap, top salesperson.',
	},
	{
		id: 'inventory',
		label: 'Inventory Dashboard',
		icon: 'inventory_2',
		bg: 'bg-slate-500/10',
		text: 'text-slate-500',
		description: 'Stock value per store, aging buckets, velocity heatmap, shrinkage trend.',
	},
	{
		id: 'customer',
		label: 'Customer Dashboard',
		icon: 'group',
		bg: 'bg-purple-500/10',
		text: 'text-purple-500',
		description: 'New vs returning, avg lifetime value, layaway cohort retention, repair NPS.',
	},
]
</script>
