<template>
	<div
		class="p-4 rounded-xl border bg-white dark:bg-gray-900 hover:border-[#D4AF37] hover:shadow-md cursor-pointer transition-all group"
		:class="getStatusBorderColor(order.status)"
		@click="$emit('open-detail')"
	>
		<!-- Header -->
		<div class="flex justify-between items-start mb-3">
			<div>
				<span class="font-mono text-sm font-bold text-[#D4AF37]">{{ order.name }}</span>
				<span
					class="ml-2 inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold"
					:class="getStatusBadgeClass(order.status)"
				>
					{{ order.status }}
				</span>
			</div>
			<div class="flex items-center gap-1">
				<span v-if="order.priority === 'Urgent'" class="text-red-500" title="Urgent">
					<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
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
					<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
							clip-rule="evenodd"
						/>
					</svg>
				</span>
				<span class="text-xs text-gray-400">{{ formatDate(order.creation) }}</span>
			</div>
		</div>

		<!-- Repair Type -->
		<p class="font-medium text-gray-900 dark:text-white mb-2 truncate">
			{{ order.repair_type_name || order.repair_type }}
		</p>

		<!-- Item Type Indicators -->
		<div class="flex flex-wrap gap-1 mb-2">
			<span
				v-if="order.item_type"
				class="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-[10px] text-gray-600"
			>
				{{ order.item_type }}
			</span>
			<span
				v-if="order.stone_weight && order.stone_weight > 0"
				class="px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900/30 rounded text-[10px] text-purple-600"
			>
				💎 {{ order.stone_weight }}ct
			</span>
			<span
				v-if="order.item_brand"
				class="px-1.5 py-0.5 bg-amber-100 dark:bg-amber-900/30 rounded text-[10px] text-amber-600"
			>
				{{ order.item_brand }}
			</span>
			<span
				v-if="order.customer_id_type"
				class="px-1.5 py-0.5 bg-orange-100 dark:bg-orange-900/30 rounded text-[10px] text-orange-600"
			>
				ID ✓
			</span>
		</div>

		<!-- Customer Info -->
		<div class="space-y-1 mb-3">
			<div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
				<svg
					class="w-4 h-4 text-gray-400"
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
			<div v-if="order.customer_phone" class="flex items-center gap-2 text-sm text-gray-500">
				<svg
					class="w-4 h-4 text-gray-400"
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
				<span>{{ order.customer_phone }}</span>
			</div>
		</div>

		<!-- Footer with Quick Actions -->
		<div
			class="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-800"
		>
			<span class="text-xs text-gray-400"
				>By: {{ order.handled_by_name || 'Unassigned' }}</span
			>
			<span class="text-sm font-bold text-gray-900 dark:text-white"
				>${{ formatNum(order.estimated_cost || order.total_cost) }}</span
			>
		</div>

		<!-- Quick Action Buttons (visible on hover) -->
		<div class="mt-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
			<button
				@click.stop="$emit('quick-status', order.name, getNextStatus(order.status))"
				class="flex-1 py-1.5 text-xs font-medium bg-[#D4AF37] text-black rounded hover:bg-[#c9a432]"
				title="Advance to next status"
			>
				→ Next
			</button>
			<button
				@click.stop="$emit('print-thermal', order)"
				class="px-2 py-1.5 text-xs bg-gray-100 dark:bg-gray-800 rounded hover:bg-gray-200"
				title="Print thermal receipt"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
				class="px-2 py-1.5 text-xs bg-gray-100 dark:bg-gray-800 rounded hover:bg-gray-200"
				title="Show QR Code"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
			class="mt-2 text-xs text-red-500 font-medium flex items-center gap-1"
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

const props = defineProps({
	order: { type: Object, required: true },
})

defineEmits(['open-detail', 'quick-status', 'print-thermal', 'open-qr'])

function formatNum(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function isOverdue(dateStr) {
	if (!dateStr) return false
	return new Date(dateStr) < new Date()
}

function getStatusBorderColor(status) {
	const colors = {
		Received: 'border-blue-200 dark:border-blue-800',
		'In Progress': 'border-orange-200 dark:border-orange-800',
		'Waiting for Parts': 'border-purple-200 dark:border-purple-800',
		'Ready for Pickup': 'border-green-200 dark:border-green-800',
		Delivered: 'border-gray-200 dark:border-gray-700',
		Cancelled: 'border-red-200 dark:border-red-800',
	}
	return colors[status] || 'border-gray-200 dark:border-gray-700'
}

function getStatusBadgeClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
		Estimated: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
		Approved: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
		'In Progress': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
		'Waiting for Parts':
			'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
		'Quality Check': 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400',
		'Ready for Pickup': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Delivered: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
		Cancelled: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
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
