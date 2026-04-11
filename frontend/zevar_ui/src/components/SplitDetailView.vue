<template>
	<div class="space-y-4">
		<!-- Header -->
		<div class="flex justify-between items-start">
			<div>
				<h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ order.name }}</h3>
				<div class="flex items-center gap-2 mt-1">
					<span
						class="inline-flex px-2 py-0.5 rounded-full text-xs font-bold"
						:class="getStatusBadgeClass(order.status)"
					>
						{{ order.status }}
					</span>
					<span v-if="order.priority === 'Urgent'" class="text-red-500">⚠</span>
				</div>
			</div>
			<div class="flex gap-2">
				<button
					@click="$emit('print-thermal', order)"
					class="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200"
					title="Print Receipt"
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
					@click="$emit('open-qr', order)"
					class="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200"
					title="QR Code"
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
		</div>

		<!-- Estimate Actions -->
		<div
			v-if="order.estimate_status === 'Sent'"
			class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-100"
		>
			<p class="text-sm font-medium text-yellow-800 mb-2">Estimate awaiting approval</p>
			<div class="flex gap-2">
				<button
					@click="approveEstimate"
					class="px-3 py-1.5 bg-green-500 text-white rounded text-sm hover:bg-green-600"
				>
					Approve
				</button>
				<button
					@click="rejectEstimate"
					class="px-3 py-1.5 bg-red-500 text-white rounded text-sm hover:bg-red-600"
				>
					Reject
				</button>
			</div>
		</div>

		<!-- Compliance Badge -->
		<div
			v-if="order.customer_id_type"
			class="flex items-center gap-2 text-xs bg-orange-50 dark:bg-orange-900/20 px-2 py-1 rounded"
		>
			<span class="text-orange-600">ID Verified: {{ order.customer_id_type }}</span>
		</div>

		<!-- Customer -->
		<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
			<p class="text-xs text-gray-500 mb-1">Customer</p>
			<p class="font-medium">{{ order.customer_name }}</p>
			<p v-if="order.customer_phone" class="text-sm text-gray-600">
				{{ order.customer_phone }}
			</p>
		</div>

		<!-- Details -->
		<div class="grid grid-cols-2 gap-3 text-sm">
			<div>
				<span class="text-gray-500">Repair Type:</span>
				<span class="font-medium">{{ order.repair_type_name }}</span>
			</div>
			<div>
				<span class="text-gray-500">Item Type:</span>
				<span class="font-medium">{{ order.item_type || '-' }}</span>
			</div>
			<div v-if="order.item_brand">
				<span class="text-gray-500">Brand:</span>
				<span class="font-medium">{{ order.item_brand }}</span>
			</div>
			<div>
				<span class="text-gray-500">Weight:</span>
				<span class="font-medium">{{ order.item_weight || '-' }}g</span>
			</div>
			<div>
				<span class="text-gray-500">Stones:</span>
				<span class="font-medium">{{ order.stone_weight || '-' }} ct</span>
			</div>
			<div v-if="order.metal_type">
				<span class="text-gray-500">Metal:</span>
				<span class="font-medium">{{ order.metal_type }}</span>
			</div>
		</div>

		<!-- Gemstones -->
		<div
			v-if="order.gemstones && order.gemstones.length > 0"
			class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3"
		>
			<p class="text-xs text-purple-600 font-medium mb-2">Gemstones</p>
			<div class="space-y-1">
				<div
					v-for="(stone, idx) in order.gemstones"
					:key="idx"
					class="text-xs flex justify-between"
				>
					<span>{{ stone.type }} ({{ stone.count }})</span>
					<span class="text-purple-600">{{ stone.carat_weight }}ct</span>
				</div>
			</div>
		</div>

		<!-- Warranty Badge -->
		<div
			v-if="order.is_warranty_repair"
			class="flex items-center gap-2 text-xs bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded"
		>
			<span class="text-green-600">✓ Warranty Repair</span>
			<span v-if="order.original_repair_order" class="text-gray-500"
				>of {{ order.original_repair_order }}</span
			>
		</div>

		<!-- Costs -->
		<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
			<div class="flex justify-between mb-1">
				<span class="text-gray-600">Est. Cost</span>
				<span class="font-medium">${{ formatNum(order.estimated_cost) }}</span>
			</div>
			<div class="flex justify-between">
				<span class="text-gray-600">Total</span>
				<span class="font-bold text-lg">${{ formatNum(order.total_cost) }}</span>
			</div>
		</div>

		<!-- Status Update -->
		<div>
			<label class="block text-sm font-medium mb-2">Update Status</label>
			<select
				v-model="selectedStatus"
				@change="updateStatus"
				class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800"
			>
				<option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
			</select>
		</div>

		<!-- Payment Status & Actions -->
		<div
			v-if="order.payment_status !== 'Paid'"
			class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-100"
		>
			<p class="text-sm font-medium text-blue-800">
				Balance Due: ${{ formatNum(order.balance_due) }}
			</p>
			<button
				@click="$emit('open-payment', order)"
				class="mt-2 px-3 py-1.5 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
			>
				Record Payment
			</button>
		</div>
	</div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { call, toast } from 'frappe-ui'

const props = defineProps({
	order: { type: Object, required: true },
})

const emit = defineEmits(['status-changed', 'print-thermal', 'open-qr', 'open-payment'])

const selectedStatus = ref(props.order.status)
const statusOptions = [
	'Received',
	'Estimated',
	'Approved',
	'In Progress',
	'Waiting for Parts',
	'Quality Check',
	'Ready for Pickup',
	'Delivered',
	'Cancelled',
]

function formatNum(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}

function getStatusBadgeClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-700',
		Estimated: 'bg-yellow-100 text-yellow-700',
		Approved: 'bg-indigo-100 text-indigo-700',
		'In Progress': 'bg-orange-100 text-orange-700',
		'Waiting for Parts': 'bg-purple-100 text-purple-700',
		'Quality Check': 'bg-cyan-100 text-cyan-700',
		'Ready for Pickup': 'bg-green-100 text-green-700',
		Delivered: 'bg-gray-100 text-gray-700',
		Cancelled: 'bg-red-100 text-red-700',
	}
	return classes[status] || 'bg-gray-100 text-gray-600'
}

async function updateStatus() {
	try {
		await call('zevar_core.api.update_repair_status', {
			name: props.order.name,
			status: selectedStatus.value,
		})
		emit('status-changed')
		toast({
			title: 'Updated',
			message: `Status changed to ${selectedStatus.value}`,
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message,
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

async function approveEstimate() {
	try {
		await call('zevar_core.api.approve_estimate', {
			repair_order: props.order.name,
			approved_by: 'Store Staff',
		})
		emit('status-changed')
		toast({
			title: 'Approved',
			message: 'Estimate approved',
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message,
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

async function rejectEstimate() {
	const reason = prompt('Reason for rejection:')
	if (!reason) return
	try {
		await call('zevar_core.api.reject_estimate', { repair_order: props.order.name, reason })
		emit('status-changed')
		toast({
			title: 'Rejected',
			message: 'Estimate rejected',
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message,
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}
</script>
