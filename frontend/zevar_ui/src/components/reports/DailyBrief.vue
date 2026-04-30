<template>
	<div class="space-y-5">
		<div v-if="loading" class="flex items-center justify-center py-20">
			<div class="text-center text-gray-500 dark:text-gray-400">
				<div
					class="animate-spin rounded-full h-7 w-7 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
				></div>
				Loading daily brief...
			</div>
		</div>

		<template v-else-if="brief">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2">
					<span class="material-symbols-outlined text-[#D4AF37] !text-xl">today</span>
					<h3
						class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide"
					>
						Daily Brief
					</h3>
					<span class="text-[10px] font-bold text-gray-400">{{ brief.date }}</span>
				</div>
				<button
					v-if="roleContext.can_closeout"
					@click="$emit('openReport', 'eod_stream_summary')"
					class="text-xs font-bold text-[#D4AF37] hover:underline flex items-center gap-1"
				>
					Full EOD Report
					<span class="material-symbols-outlined !text-sm">arrow_forward</span>
				</button>
			</div>

			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
				<button
					@click="$emit('drill', 'hourly_sales')"
					class="bg-emerald-50 dark:bg-emerald-900/20 rounded-xl p-4 border border-emerald-100 dark:border-emerald-800/30 hover:border-emerald-300 dark:hover:border-emerald-600 transition-all text-left"
				>
					<div class="flex items-center justify-between">
						<span
							class="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide"
							>Today's Sales</span
						>
						<YoYBadge
							v-if="brief.yoy_deltas?.sales_total"
							:delta="brief.yoy_deltas.sales_total"
						/>
					</div>
					<p class="text-xl font-black text-emerald-700 dark:text-emerald-300 mt-1">
						${{ fmt(brief.sales.total) }}
					</p>
					<p class="text-[10px] text-emerald-500 dark:text-emerald-400 mt-0.5">
						{{ brief.sales.count }} txns
					</p>
				</button>

				<button
					@click="$emit('drill', 'repair_revenue')"
					class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-100 dark:border-blue-800/30 hover:border-blue-300 dark:hover:border-blue-600 transition-all text-left"
				>
					<span
						class="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wide"
						>Repair Revenue</span
					>
					<p class="text-xl font-black text-blue-700 dark:text-blue-300 mt-1">
						${{ fmt(brief.repair_revenue.total) }}
					</p>
					<p class="text-[10px] text-blue-500 dark:text-blue-400 mt-0.5">
						{{ brief.repair_revenue.count }} completed
					</p>
				</button>

				<button
					class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border border-purple-100 dark:border-purple-800/30 hover:border-purple-300 dark:hover:border-purple-600 transition-all text-left"
				>
					<span
						class="text-[10px] font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wide"
						>Layaway Deposits</span
					>
					<p class="text-xl font-black text-purple-700 dark:text-purple-300 mt-1">
						${{ fmt(brief.layaway_deposits.total) }}
					</p>
					<p class="text-[10px] text-purple-500 dark:text-purple-400 mt-0.5">today</p>
				</button>

				<button
					class="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-4 border border-amber-100 dark:border-amber-800/30 hover:border-amber-300 dark:hover:border-amber-600 transition-all text-left"
				>
					<span
						class="text-[10px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wide"
						>Cash Variance</span
					>
					<p class="text-xl font-black text-amber-700 dark:text-amber-300 mt-1">
						${{ fmt(brief.cash_variance_today) }}
					</p>
					<p class="text-[10px] text-amber-500 dark:text-amber-400 mt-0.5">
						today's variance
					</p>
				</button>

				<button
					@click="$emit('drill', 'low_stock_alert')"
					class="rounded-xl p-4 border transition-all text-left"
					:class="
						brief.low_stock_count > 0
							? 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-800/30 hover:border-red-300'
							: 'bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-800/30 hover:border-green-300'
					"
				>
					<span
						class="text-[10px] font-bold uppercase tracking-wide"
						:class="
							brief.low_stock_count > 0
								? 'text-red-600 dark:text-red-400'
								: 'text-green-600 dark:text-green-400'
						"
						>Low Stock</span
					>
					<p
						class="text-xl font-black mt-1"
						:class="
							brief.low_stock_count > 0
								? 'text-red-700 dark:text-red-300'
								: 'text-green-700 dark:text-green-300'
						"
					>
						{{ brief.low_stock_count }} SKUs
					</p>
					<p
						class="text-[10px] mt-0.5"
						:class="
							brief.low_stock_count > 0
								? 'text-red-500 dark:text-red-400'
								: 'text-green-500 dark:text-green-400'
						"
					>
						below threshold
					</p>
				</button>

				<button
					@click="$emit('drill', 'overdue_repairs')"
					class="rounded-xl p-4 border transition-all text-left"
					:class="
						brief.overdue_repairs.count > 0
							? 'bg-orange-50 dark:bg-orange-900/20 border-orange-100 dark:border-orange-800/30 hover:border-orange-300'
							: 'bg-gray-50 dark:bg-gray-800 border-gray-100 dark:border-gray-700 hover:border-gray-300'
					"
				>
					<span
						class="text-[10px] font-bold uppercase tracking-wide"
						:class="
							brief.overdue_repairs.count > 0
								? 'text-orange-600 dark:text-orange-400'
								: 'text-gray-600 dark:text-gray-400'
						"
						>Overdue Repairs</span
					>
					<p
						class="text-xl font-black mt-1"
						:class="
							brief.overdue_repairs.count > 0
								? 'text-orange-700 dark:text-orange-300'
								: 'text-gray-700 dark:text-gray-300'
						"
					>
						{{ brief.overdue_repairs.count }}
					</p>
					<p
						class="text-[10px] mt-0.5"
						:class="
							brief.overdue_repairs.count > 0
								? 'text-orange-500 dark:text-orange-400'
								: 'text-gray-500 dark:text-gray-400'
						"
					>
						{{
							brief.overdue_repairs.max_days_overdue > 0
								? `max ${brief.overdue_repairs.max_days_overdue}d overdue`
								: 'none overdue'
						}}
					</p>
				</button>

				<div
					v-if="brief.financier_ar?.length > 0"
					class="bg-sky-50 dark:bg-sky-900/20 rounded-xl p-4 border border-sky-100 dark:border-sky-800/30 text-left"
				>
					<span
						class="text-[10px] font-bold text-sky-600 dark:text-sky-400 uppercase tracking-wide"
						>Financier A/R</span
					>
					<div class="mt-1 space-y-0.5">
						<div
							v-for="f in brief.financier_ar"
							:key="f.financier"
							class="flex justify-between text-[11px]"
						>
							<span class="text-sky-600 dark:text-sky-400">{{ f.financier }}</span>
							<span class="font-bold text-sky-700 dark:text-sky-300"
								>${{ fmt(f.today_ar) }}</span
							>
						</div>
					</div>
				</div>

				<button
					@click="$emit('drill', 'audit_compliance')"
					class="bg-teal-50 dark:bg-teal-900/20 rounded-xl p-4 border border-teal-100 dark:border-teal-800/30 hover:border-teal-300 dark:hover:border-teal-600 transition-all text-left"
				>
					<span
						class="text-[10px] font-bold text-teal-600 dark:text-teal-400 uppercase tracking-wide"
						>Next Audit Due</span
					>
					<p class="text-xl font-black text-teal-700 dark:text-teal-300 mt-1">
						{{ brief.next_audit?.scope || 'None' }}
					</p>
					<p class="text-[10px] text-teal-500 dark:text-teal-400 mt-0.5">
						{{
							brief.next_audit?.due_in_hours != null
								? `in ${brief.next_audit.due_in_hours}h`
								: 'not scheduled'
						}}
					</p>
				</button>

				<button
					@click="$emit('drill', 'eod_stream_summary')"
					class="bg-rose-50 dark:bg-rose-900/20 rounded-xl p-4 border border-rose-100 dark:border-rose-800/30 hover:border-rose-300 dark:hover:border-rose-600 transition-all text-left"
				>
					<span
						class="text-[10px] font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wide"
						>Pending Approvals</span
					>
					<p class="text-xl font-black text-rose-700 dark:text-rose-300 mt-1">
						{{
							(brief.pending_approvals?.variance_overrides || 0) +
							(brief.pending_approvals?.transfer_receives || 0)
						}}
					</p>
					<p class="text-[10px] text-rose-500 dark:text-rose-400 mt-0.5">
						{{ brief.pending_approvals?.variance_overrides || 0 }} overrides &middot;
						{{ brief.pending_approvals?.transfer_receives || 0 }} transfers
					</p>
				</button>
			</div>

			<div v-if="brief.live_feed?.length > 0" class="premium-card !p-4">
				<div class="flex items-center gap-2 mb-3">
					<span class="material-symbols-outlined text-[#D4AF37] !text-lg"
						>activity_zone</span
					>
					<h3
						class="text-xs font-black text-gray-900 dark:text-white uppercase tracking-wide"
					>
						Today's Feed
					</h3>
				</div>
				<div class="space-y-1.5 max-h-64 overflow-auto">
					<div
						v-for="(entry, i) in brief.live_feed.slice(0, 30)"
						:key="i"
						class="flex items-start gap-3 py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0"
					>
						<span
							class="text-[10px] text-gray-400 dark:text-gray-500 shrink-0 w-12 pt-0.5"
							>{{ formatTime(entry.timestamp) }}</span
						>
						<p class="text-xs text-gray-700 dark:text-gray-300">
							{{ entry.details || entry.event_type }}
						</p>
						<span
							class="text-[10px] text-gray-400 dark:text-gray-500 shrink-0 ml-auto"
							>{{ entry.user }}</span
						>
					</div>
				</div>
			</div>

			<div v-if="roleContext.can_closeout" class="grid grid-cols-2 md:grid-cols-4 gap-3">
				<button
					v-for="action in eodActions"
					:key="action.id"
					@click="$emit('openReport', action.id)"
					class="premium-card !p-4 text-left hover:!border-[#D4AF37] transition-all flex items-center gap-3"
				>
					<div
						class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
						:class="action.bg"
					>
						<span class="material-symbols-outlined !text-lg" :class="action.text">{{
							action.icon
						}}</span>
					</div>
					<div class="min-w-0">
						<p class="text-xs font-bold text-gray-900 dark:text-white truncate">
							{{ action.label }}
						</p>
						<p class="text-[10px] text-gray-500 dark:text-gray-400 truncate">
							{{ action.sub }}
						</p>
					</div>
				</button>
			</div>
		</template>

		<div v-else class="premium-card text-center py-12">
			<span class="material-symbols-outlined text-4xl text-gray-300 dark:text-gray-600 mb-3"
				>cloud_off</span
			>
			<p class="text-sm text-gray-500 dark:text-gray-400">
				Could not load daily brief. Try refreshing.
			</p>
		</div>
	</div>
</template>

<script setup>
import YoYBadge from './YoYBadge.vue'

defineProps({
	brief: { type: Object, default: null },
	loading: { type: Boolean, default: false },
	roleContext: { type: Object, default: () => ({}) },
})

defineEmits(['openReport', 'drill'])

const eodActions = [
	{
		id: 'eod_stream_summary',
		label: 'End of Day Summary',
		sub: 'Full closeout totals',
		icon: 'point_of_sale',
		bg: 'bg-blue-500/10',
		text: 'text-blue-500',
	},
	{
		id: 'cash_drawer_reconciliation',
		label: 'Cash Drawer',
		sub: 'Opening/closing balance',
		icon: 'payments',
		bg: 'bg-emerald-500/10',
		text: 'text-emerald-500',
	},
	{
		id: 'payment_method_summary',
		label: 'Payment Methods',
		sub: 'By method breakdown',
		icon: 'credit_card',
		bg: 'bg-purple-500/10',
		text: 'text-purple-500',
	},
	{
		id: 'refunds_voids_discounts',
		label: 'Refunds & Voids',
		sub: 'Audit trail',
		icon: 'receipt_long',
		bg: 'bg-red-500/10',
		text: 'text-red-500',
	},
]

function fmt(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}

function formatTime(ts) {
	if (!ts) return ''
	const d = new Date(ts)
	return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>
