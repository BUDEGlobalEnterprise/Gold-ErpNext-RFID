<template>
	<Teleport to="body">
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
			@click.self="$emit('close')"
		>
			<div
				class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto"
			>
				<!-- Header -->
				<div
					class="sticky top-0 bg-white dark:bg-gray-900 p-4 border-b border-gray-100 dark:border-gray-800 flex justify-between items-start z-10"
				>
					<div>
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">
							{{ order.name }}
						</h3>
						<div class="flex items-center gap-2 mt-1">
							<span
								class="inline-flex px-2 py-0.5 rounded-full text-xs font-bold"
								:class="getStatusBadgeClass(order.status)"
							>
								{{ order.status }}
							</span>
							<span
								v-if="order.priority === 'Urgent'"
								class="px-2 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-700"
								>Urgent</span
							>
							<span
								v-if="order.estimate_status"
								class="px-2 py-0.5 rounded-full text-xs font-bold bg-yellow-100 text-yellow-700"
								>{{ order.estimate_status }}</span
							>
						</div>
					</div>
					<button
						@click="$emit('close')"
						class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<div class="p-4 space-y-4">
					<!-- Quick Actions Toolbar -->
					<div class="flex flex-wrap gap-2">
						<button
							@click="printThermal"
							class="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded text-sm hover:bg-gray-200 flex items-center gap-1"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
								/>
							</svg>
							Thermal Print
						</button>
						<button
							@click="$emit('open-qr', order)"
							class="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded text-sm hover:bg-gray-200 flex items-center gap-1"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
								/>
							</svg>
							QR Code
						</button>
						<button
							@click="$emit('open-camera')"
							class="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded text-sm hover:bg-gray-200 flex items-center gap-1"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
								/>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
								/>
							</svg>
							Add Photo
						</button>
						<button
							@click="initiateTransfer"
							class="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded text-sm hover:bg-gray-200 flex items-center gap-1"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
								/>
							</svg>
							Transfer
						</button>
					</div>

					<!-- Estimate Section -->
					<div
						v-if="order.estimate_status"
						class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-100 dark:border-yellow-800/30"
					>
						<h4
							class="text-xs font-bold text-yellow-600 dark:text-yellow-400 uppercase mb-2"
						>
							Estimate Status
						</h4>
						<div class="flex items-center justify-between mb-2">
							<span class="font-medium">{{ order.estimate_status }}</span>
							<div class="flex gap-2" v-if="order.estimate_status === 'Sent'">
								<button
									@click="approveEstimate"
									class="px-3 py-1 bg-green-500 text-white rounded text-xs hover:bg-green-600"
								>
									Approve
								</button>
								<button
									@click="rejectEstimate"
									class="px-3 py-1 bg-red-500 text-white rounded text-xs hover:bg-red-600"
								>
									Reject
								</button>
							</div>
						</div>
						<div
							v-if="order.estimate_valid_until"
							class="text-xs text-yellow-600 dark:text-yellow-400"
						>
							Valid until: {{ formatDate(order.estimate_valid_until) }}
						</div>
					</div>

					<!-- Compliance Status -->
					<div
						v-if="order.customer_id_type || order.id_verified_by"
						class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3 border border-orange-100 dark:border-orange-800/30"
					>
						<h4
							class="text-xs font-bold text-orange-600 dark:text-orange-400 uppercase mb-2"
						>
							Compliance Status
						</h4>
						<div class="grid grid-cols-2 gap-2 text-xs">
							<div v-if="order.customer_id_type">
								<span class="text-orange-600">ID Type:</span>
								{{ order.customer_id_type }}
							</div>
							<div v-if="order.customer_id_number">
								<span class="text-orange-600">ID Number:</span>
								{{ order.customer_id_number }}
							</div>
							<div v-if="order.id_verified_by">
								<span class="text-orange-600">Verified By:</span>
								{{ order.id_verified_by }}
							</div>
							<div
								v-if="order.intake_checklist_signed"
								class="text-green-600 font-medium"
							>
								✓ Intake Checklist Signed
							</div>
						</div>
					</div>

					<!-- Photos Section -->
					<div
						v-if="order.before_photos?.length || order.after_photos?.length"
						class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3"
					>
						<h4 class="text-xs font-bold text-gray-500 uppercase mb-2">Photos</h4>
						<div class="grid grid-cols-4 gap-2">
							<div v-if="order.before_photos?.length" class="col-span-2">
								<p class="text-xs text-blue-600 font-medium mb-1">Before Repair</p>
								<div class="grid grid-cols-2 gap-1">
									<img
										v-for="(photo, idx) in order.before_photos"
										:key="'before-' + idx"
										:src="photo"
										class="w-full h-20 object-cover rounded border"
									/>
								</div>
							</div>
							<div v-if="order.after_photos?.length" class="col-span-2">
								<p class="text-xs text-green-600 font-medium mb-1">After Repair</p>
								<div class="grid grid-cols-2 gap-1">
									<img
										v-for="(photo, idx) in order.after_photos"
										:key="'after-' + idx"
										:src="photo"
										class="w-full h-20 object-cover rounded border"
									/>
								</div>
							</div>
						</div>
					</div>

					<!-- Customer Section -->
					<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
						<h4 class="text-xs font-bold text-gray-500 uppercase mb-2">Customer</h4>
						<p class="font-medium">{{ order.customer_name }}</p>
						<p
							v-if="order.customer_phone"
							class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1"
						>
							<svg
								class="w-4 h-4"
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
							{{ order.customer_phone }}
						</p>
						<button
							@click="sendNotification"
							class="mt-2 text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
						>
							Send Status Update
						</button>
					</div>

					<!-- Repair Details -->
					<div class="space-y-2">
						<div class="flex justify-between">
							<span class="text-gray-500">Repair Type:</span
							><span class="font-medium">{{ order.repair_type_name }}</span>
						</div>
						<div v-if="order.item_type" class="flex justify-between">
							<span class="text-gray-500">Item Type:</span
							><span class="font-medium">{{ order.item_type }}</span>
						</div>
						<div v-if="order.item_brand" class="flex justify-between">
							<span class="text-gray-500">Brand:</span
							><span class="font-medium">{{ order.item_brand }}</span>
						</div>
						<div v-if="order.serial_number" class="flex justify-between">
							<span class="text-gray-500">Serial #:</span
							><span class="font-medium font-mono">{{ order.serial_number }}</span>
						</div>
						<div v-if="order.item_weight" class="flex justify-between">
							<span class="text-gray-500">Weight:</span
							><span class="font-medium">{{ order.item_weight }}g</span>
						</div>
						<div v-if="order.stone_weight" class="flex justify-between">
							<span class="text-gray-500">Stones:</span
							><span class="font-medium text-purple-600"
								>{{ order.stone_weight }} ct</span
							>
						</div>
						<div v-if="order.metal_type" class="flex justify-between">
							<span class="text-gray-500">Metal:</span
							><span class="font-medium"
								>{{ order.metal_type
								}}{{ order.purity ? ' ' + order.purity : '' }}</span
							>
						</div>
						<div v-if="order.item_condition" class="flex justify-between">
							<span class="text-gray-500">Condition:</span
							><span class="font-medium text-sm">{{ order.item_condition }}</span>
						</div>
						<div v-if="order.promised_date" class="flex justify-between">
							<span class="text-gray-500">Promised:</span
							><span
								class="font-medium"
								:class="{ 'text-red-600': isOverdue(order.promised_date) }"
								>{{ formatDate(order.promised_date) }}</span
							>
						</div>
					</div>

					<!-- Gemstones Section -->
					<div
						v-if="order.gemstones && order.gemstones.length > 0"
						class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-100 dark:border-purple-800/30"
					>
						<h4
							class="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase mb-2"
						>
							Gemstones
						</h4>
						<div class="space-y-2">
							<div
								v-for="(stone, idx) in order.gemstones"
								:key="idx"
								class="bg-white dark:bg-gray-800 rounded p-2 text-xs"
							>
								<div class="flex justify-between">
									<span class="font-medium">{{ stone.type }}</span>
									<span class="text-purple-600"
										>{{ stone.carat_weight }}ct × {{ stone.count }}</span
									>
								</div>
								<div class="flex gap-2 mt-1 text-gray-500">
									<span v-if="stone.color">Color: {{ stone.color }}</span>
									<span v-if="stone.clarity">Clarity: {{ stone.clarity }}</span>
									<span v-if="stone.setting_type"
										>Setting: {{ stone.setting_type }}</span
									>
								</div>
							</div>
						</div>
					</div>

					<!-- Metal Weight Tracking -->
					<div
						v-if="order.metal_weight_in || order.metal_weight_out"
						class="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 border border-amber-100 dark:border-amber-800/30"
					>
						<h4
							class="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase mb-2"
						>
							Metal Weight
						</h4>
						<div class="grid grid-cols-3 gap-2 text-xs text-center">
							<div>
								<span class="text-gray-500">Weight In:</span><br /><span
									class="font-bold"
									>{{ order.metal_weight_in || 0 }}g</span
								>
							</div>
							<div>
								<span class="text-gray-500">Weight Out:</span><br /><span
									class="font-bold"
									>{{ order.metal_weight_out || 0 }}g</span
								>
							</div>
							<div>
								<span class="text-gray-500">Difference:</span><br /><span
									class="font-bold"
									:class="
										(order.metal_weight_difference || 0) < 0
											? 'text-red-600'
											: 'text-green-600'
									"
									>{{ order.metal_weight_difference || 0 }}g</span
								>
							</div>
						</div>
					</div>

					<!-- Payment Section -->
					<div
						class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-100 dark:border-blue-800/30"
					>
						<h4
							class="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase mb-2"
						>
							Payment
						</h4>
						<div class="space-y-1 text-sm">
							<div class="flex justify-between">
								<span>Estimated Cost:</span
								><span>${{ formatNum(order.estimated_cost) }}</span>
							</div>
							<div class="flex justify-between">
								<span>Total Cost:</span
								><span class="font-bold">${{ formatNum(order.total_cost) }}</span>
							</div>
							<div class="flex justify-between">
								<span>Deposit:</span
								><span>${{ formatNum(order.deposit_amount) }}</span>
							</div>
							<div
								class="flex justify-between font-bold border-t border-blue-200 dark:border-blue-800 pt-1"
							>
								<span>Balance Due:</span
								><span>${{ formatNum(order.balance_due) }}</span>
							</div>
						</div>
						<div v-if="order.payment_status !== 'Paid'" class="mt-3">
							<button
								@click="$emit('open-payment', order)"
								class="w-full py-2 bg-blue-500 text-white rounded text-sm font-medium hover:bg-blue-600"
							>
								Record Payment
							</button>
						</div>
					</div>

					<!-- Warranty Section -->
					<div
						v-if="order.warranty_months > 0 || order.is_warranty_repair"
						class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-100 dark:border-purple-800/30"
					>
						<h4
							class="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase mb-2"
						>
							Warranty
						</h4>
						<p v-if="order.warranty_months > 0" class="text-sm">
							{{ order.warranty_months }} months warranty
						</p>
						<p v-if="order.warranty_expiry_date" class="text-xs text-purple-600 mt-1">
							Expires: {{ formatDate(order.warranty_expiry_date) }}
						</p>
						<p
							v-if="order.is_warranty_repair"
							class="text-sm text-green-600 font-medium"
						>
							✓ Warranty Repair
						</p>
						<p v-if="order.original_repair_order" class="text-xs text-gray-500">
							Original: {{ order.original_repair_order }}
						</p>
					</div>

					<!-- Communication Log -->
					<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
						<div class="flex items-center justify-between mb-2">
							<h4 class="text-xs font-bold text-gray-500 uppercase">
								Communication Log
							</h4>
							<button
								@click="showCommunicationForm = !showCommunicationForm"
								class="text-xs px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300"
							>
								+ Add Entry
							</button>
						</div>

						<!-- Add Communication Form -->
						<div
							v-if="showCommunicationForm"
							class="mb-3 p-2 bg-white dark:bg-gray-900 rounded border"
						>
							<div class="grid grid-cols-2 gap-2 mb-2">
								<select
									v-model="newComm.type"
									class="px-2 py-1 border rounded text-xs"
								>
									<option value="Phone Call">Phone Call</option>
									<option value="SMS">SMS</option>
									<option value="Email">Email</option>
									<option value="In-Person">In-Person</option>
								</select>
								<select
									v-model="newComm.direction"
									class="px-2 py-1 border rounded text-xs"
								>
									<option value="Incoming">Incoming</option>
									<option value="Outgoing">Outgoing</option>
								</select>
							</div>
							<textarea
								v-model="newComm.content"
								rows="2"
								placeholder="Communication details..."
								class="w-full px-2 py-1 border rounded text-xs mb-2"
							></textarea>
							<div class="flex gap-2">
								<button
									@click="addCommunication"
									class="text-xs px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600"
								>
									Save
								</button>
								<button
									@click="showCommunicationForm = false"
									class="text-xs px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
								>
									Cancel
								</button>
							</div>
						</div>

						<!-- Communications List -->
						<div
							v-if="communications && communications.length > 0"
							class="space-y-2 max-h-32 overflow-y-auto"
						>
							<div
								v-for="(comm, idx) in communications"
								:key="idx"
								class="bg-white dark:bg-gray-900 rounded p-2 text-xs border"
							>
								<div class="flex justify-between items-start">
									<span
										class="font-medium"
										:class="
											comm.direction === 'Incoming'
												? 'text-blue-600'
												: 'text-green-600'
										"
										>{{ comm.direction }}</span
									>
									<span class="text-gray-400">{{
										formatDateTime(comm.communication_date)
									}}</span>
								</div>
								<p class="text-gray-500">{{ comm.type }}</p>
								<p class="mt-1">{{ comm.content }}</p>
							</div>
						</div>
						<div v-else class="text-xs text-gray-400 text-center py-2">
							No communications logged
						</div>
					</div>

					<!-- Status Update -->
					<div class="pt-2">
						<label class="block text-sm font-medium mb-2">Update Status</label>
						<select
							v-model="selectedStatus"
							@change="updateStatus"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800"
						>
							<option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
						</select>
					</div>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import { call, toast } from 'frappe-ui'

const props = defineProps({
	order: { type: Object, required: true },
})

const emit = defineEmits([
	'close',
	'status-changed',
	'print-thermal',
	'open-qr',
	'open-camera',
	'open-payment',
])

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
const communications = ref([])
const showCommunicationForm = ref(false)
const newComm = ref({ type: 'Phone Call', direction: 'Outgoing', content: '' })

function formatNum(n) {
	return n ? Number(n).toFixed(2) : '0.00'
}
function formatDate(d) {
	return d ? new Date(d).toLocaleDateString() : ''
}
function formatDateTime(d) {
	return d ? new Date(d).toLocaleString() : ''
}

function isOverdue(dateStr) {
	if (!dateStr) return false
	return new Date(dateStr) < new Date()
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

function printThermal() {
	emit('print-thermal', props.order)
}

function initiateTransfer() {
	window.location.href = `#transfer=${props.order.name}`
}

async function sendNotification() {
	try {
		await call('zevar_core.api.send_manual_notification', {
			repair_order: props.order.name,
			notification_type: props.order.status,
			message: `Status update for ${props.order.name}`,
		})
		toast({
			title: 'Sent',
			message: 'Notification sent successfully',
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

async function addCommunication() {
	if (!newComm.value.content) {
		toast({
			title: 'Required',
			message: 'Please enter communication details',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	try {
		await call('zevar_core.api.log_manual_communication', {
			repair_order: props.order.name,
			comm_type: newComm.value.type,
			direction: newComm.value.direction,
			content: newComm.value.content,
		})
		await loadCommunications()
		showCommunicationForm.value = false
		newComm.value = { type: 'Phone Call', direction: 'Outgoing', content: '' }
		toast({
			title: 'Logged',
			message: 'Communication logged',
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

async function loadCommunications() {
	try {
		const data = await call('zevar_core.api.get_communications', {
			repair_order: props.order.name,
		})
		communications.value = data || []
	} catch (e) {
		console.error('Failed to load communications:', e)
	}
}

onMounted(() => {
	loadCommunications()
})
</script>
