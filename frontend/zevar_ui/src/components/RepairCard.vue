<template>
	<div
		class="p-3.5 rounded-xl border bg-white dark:bg-warm-dark-800 hover:border-[#D4AF37] hover:shadow-md cursor-pointer transition-all duration-200 group flex flex-col min-w-0"
		:class="getStatusBorderColor(order.status)"
		@click="$emit('open-detail')"
	>
		<!-- Header -->
		<div class="flex justify-between items-start gap-1 mb-2.5 min-w-0">
			<div class="min-w-0 flex items-center gap-1.5 flex-wrap">
				<span class="font-mono text-[10px] font-bold text-[#D4AF37]">{{
					order.name
				}}</span>
				<span
					class="inline-flex px-1.5 py-0.5 rounded-full text-[8px] font-bold shrink-0"
					:class="getStatusBadgeClass(order.status)"
				>
					{{ order.status }}
				</span>
			</div>
			<div class="flex items-center gap-1 shrink-0">
				<span v-if="order.priority === 'Urgent'" class="text-red-500" title="Urgent">
					<svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
							clip-rule="evenodd"
						/>
					</svg>
				</span>
				<span
					v-if="order.is_warranty_repair"
					class="text-green-500"
					title="Warranty Repair"
				>
					<svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
							clip-rule="evenodd"
						/>
					</svg>
				</span>
				<span class="text-[9px] text-gray-400 font-mono">{{
					formatDate(order.creation)
				}}</span>
			</div>
		</div>

		<!-- Repair Type -->
		<p class="font-bold text-gray-900 dark:text-white text-xs mb-2 truncate leading-tight">
			{{ order.repair_type_name || order.repair_type }}
		</p>

		<!-- Item Type Indicators -->
		<div class="flex flex-wrap gap-1 mb-2.5">
			<span
				v-if="order.item_type"
				class="px-1 py-0.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-100 dark:border-warm-border/30 rounded text-[9px] font-bold text-gray-500 dark:text-gray-400"
			>
				{{ order.item_type }}
			</span>
			<span
				v-if="order.stone_weight && order.stone_weight > 0"
				class="px-1 py-0.5 bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-900/30 rounded text-[9px] font-bold text-purple-600 dark:text-purple-400"
			>
				💎 {{ order.stone_weight }}ct
			</span>
			<span
				v-if="order.item_brand"
				class="px-1 py-0.5 bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-900/30 rounded text-[9px] font-bold text-amber-600 dark:text-amber-400"
			>
				{{ order.item_brand }}
			</span>
			<span
				v-if="order.customer_id_type"
				class="px-1 py-0.5 bg-orange-50 dark:bg-orange-900/20 border border-orange-100 dark:border-orange-900/30 rounded text-[9px] font-bold text-orange-600 dark:text-orange-400"
			>
				ID ✓
			</span>
		</div>

		<!-- Customer Info -->
		<div class="space-y-1 mb-3.5 min-w-0">
			<div
				class="flex items-center gap-2 text-[10px] text-gray-600 dark:text-gray-400 min-w-0"
			>
				<svg
					class="w-3.5 h-3.5 text-gray-400 shrink-0"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
					/>
				</svg>
				<span class="truncate">{{ order.customer_name || order.customer }}</span>
			</div>
			<div
				v-if="order.customer_phone"
				class="flex items-center gap-2 text-[10px] text-gray-500 min-w-0"
			>
				<svg
					class="w-3.5 h-3.5 text-gray-400 shrink-0"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
					/>
				</svg>
				<span class="truncate">{{ order.customer_phone }}</span>
			</div>
		</div>

		<!-- Compact Timeline Progress -->
		<div class="mb-2">
			<RepairTimeline :currentStatus="order.status" variant="compact" />
		</div>

		<!-- Footer with Quick Actions -->
		<div
			class="flex items-center justify-between pt-2 border-t border-gray-50 dark:border-warm-border/30 mt-auto min-w-0"
		>
			<span class="text-[10px] text-gray-400 dark:text-gray-500 truncate"
				>By: {{ order.handled_by_name || 'Unassigned' }}</span
			>
			<span
				class="text-xs font-mono font-extrabold text-gray-900 dark:text-white shrink-0 ml-1"
				>${{ formatNum(order.estimated_cost || order.total_cost) }}</span
			>
		</div>

		<!-- Quick Action Buttons (visible on hover) -->
		<div class="mt-2.5 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
			<button
				@click.stop="$emit('quick-status', order.name, getNextStatus(order.status))"
				class="flex-1 py-1 text-[10px] font-bold bg-[#D4AF37] hover:bg-[#c9a432] text-[#0F1115] rounded transition duration-150"
				title="Advance to next status"
			>
				→ Next
			</button>
			<button
				@click.stop="$emit('print-thermal', order)"
				class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-white bg-gray-50 dark:bg-warm-dark-900 hover:bg-gray-100 border border-gray-100 dark:border-warm-border/30 rounded transition"
				title="Print thermal receipt"
			>
				<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
					/>
				</svg>
			</button>
			<button
				@click.stop="$emit('open-qr', order)"
				class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-white bg-gray-50 dark:bg-warm-dark-900 hover:bg-gray-100 border border-gray-100 dark:border-warm-border/30 rounded transition"
				title="Show QR Code"
			>
				<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
					/>
				</svg>
			</button>
		</div>

		<!-- Overdue Warning -->
		<div
			v-if="isOverdue(order.promised_date) && order.status !== 'Delivered'"
			class="mt-2 text-[10px] text-red-500 font-bold flex items-center gap-1 shrink-0"
		>
			<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
				<path
					fill-rule="evenodd"
					d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
					clip-rule="evenodd"
				/>
			</svg>
			Overdue ({{ formatDate(order.promised_date) }})
		</div>
	</div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { formatDate } from '@/utils/dates.js'
import RepairTimeline from './RepairTimeline.vue'

const props = defineProps({
	order: { type: Object, required: true },
})

defineEmits(['open-detail', 'quick-status', 'print-thermal', 'open-qr'])

function formatNum(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}

function isOverdue(dateStr) {
	if (!dateStr) return false
	return new Date(dateStr) < new Date()
}

function getStatusBorderColor(status) {
	const colors = {
		Received: 'border-blue-200 dark:border-blue-900/60',
		'In Progress': 'border-orange-200 dark:border-orange-900/60',
		'Waiting for Parts': 'border-purple-200 dark:border-purple-900/60',
		'Ready for Pickup': 'border-green-200 dark:border-green-900/60',
		Delivered: 'border-gray-200 dark:border-warm-border',
		Cancelled: 'border-red-200 dark:border-red-900/60',
	}
	return colors[status] || 'border-gray-200 dark:border-warm-border'
}

function getStatusBadgeClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
		Estimated: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300',
		Approved: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300',
		'In Progress': 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
		'Waiting for Parts':
			'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
		'Quality Check': 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300',
		'Ready for Pickup': 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
		Delivered: 'bg-gray-100 text-gray-700 dark:bg-warm-dark-700 dark:text-warm-dark-600',
		Cancelled: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
	}
	return (
		classes[status] ||
		'bg-gray-100 text-gray-600 dark:bg-warm-dark-700 dark:text-warm-dark-600'
	)
}

function getNextStatus(currentStatus) {
	const flow = [
		'Received',
		'Estimated',
		'Approved',
		'In Progress',
		'Waiting for Parts',
		'Quality Check',
		'Ready for Pickup',
		'Delivered',
	]
	const idx = flow.indexOf(currentStatus)
	if (idx >= 0 && idx < flow.length - 1) return flow[idx + 1]
	return currentStatus
}
</script>
