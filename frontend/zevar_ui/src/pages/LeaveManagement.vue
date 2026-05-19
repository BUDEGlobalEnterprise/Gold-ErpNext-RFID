<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Leave Management</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ hr.leaveApplicationsTotal }} Applications
					</span>
				</div>
				<div class="flex items-center gap-2">
					<button
						@click="refreshAll"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': hr.leaveBalanceResource.loading }"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15"
							/>
						</svg>
					</button>
					<button
						@click="showApplyModal = true"
						class="flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						Apply Leave
					</button>
				</div>
			</div>

			<div
				v-if="hr.leaveBalances.length"
				class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0"
			>
				<div
					v-for="bal in hr.leaveBalances"
					:key="bal.leave_type"
					class="premium-card !p-4"
				>
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						{{ bal.leave_type }}
					</div>
					<div class="flex items-end gap-1">
						<span
							class="text-2xl font-bold"
							:class="bal.remaining > 0 ? 'text-emerald-500' : 'text-red-500'"
							>{{ bal.remaining }}</span
						>
						<span class="text-gray-400 text-sm mb-1">/ {{ bal.allocated }} days</span>
					</div>
					<div class="text-[10px] text-gray-400 mt-1">
						{{ bal.taken }} taken &middot; {{ bal.pending }} pending
					</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div
					v-if="hr.leaveApplicationsResource.loading && !hr.leaveApplications.length"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>
				<div
					v-else-if="!hr.leaveApplications.length"
					class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500"
				>
					<svg
						class="w-12 h-12 mb-3"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.5"
							d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
						/>
					</svg>
					<p class="text-sm font-medium">No leave applications found</p>
				</div>
				<div v-else class="space-y-2">
					<div
						v-for="app in hr.leaveApplications"
						:key="app.name"
						class="premium-card !p-4 flex items-center justify-between"
					>
						<div class="flex items-center gap-3 min-w-0">
							<div
								class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
								:class="statusBg(app.status)"
							>
								<svg
									class="w-4 h-4"
									:class="statusText(app.status)"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
									/>
								</svg>
							</div>
							<div class="min-w-0">
								<div class="text-sm font-bold text-gray-900 dark:text-white">
									{{ app.leave_type }}
								</div>
								<div class="text-[11px] text-gray-500 dark:text-gray-400">
									{{ app.from_date }} → {{ app.to_date }}
									<span v-if="app.half_day"> (Half Day)</span>
									&middot; {{ app.total_leave_days }} day{{
										app.total_leave_days !== 1 ? 's' : ''
									}}
								</div>
							</div>
						</div>
						<div class="text-right flex-shrink-0 ml-3 flex items-center gap-2">
							<span
								class="px-2 py-0.5 rounded-full text-[9px] font-bold"
								:class="statusBadge(app.status)"
							>
								{{ app.status }}
							</span>
							<button
								v-if="app.status === 'Open' && app.docstatus === 0"
								@click="handleCancel(app.name)"
								class="text-[10px] text-red-500 hover:underline"
							>
								Cancel
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div
			v-if="showApplyModal"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showApplyModal = false"
		>
			<div class="premium-card !p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
				<h3 class="premium-title !text-lg mb-4">Apply for Leave</h3>
				<div class="space-y-3">
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Leave Type</label
						>
						<select v-model="leaveForm.leave_type" class="form-input">
							<option value="">Select type</option>
							<option v-for="lt in hr.leaveTypes" :key="lt.name" :value="lt.name">
								{{ lt.name }}
							</option>
						</select>
					</div>
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label
								class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
								>From</label
							>
							<input v-model="leaveForm.from_date" type="date" class="form-input" />
						</div>
						<div>
							<label
								class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
								>To</label
							>
							<input v-model="leaveForm.to_date" type="date" class="form-input" />
						</div>
					</div>
					<div class="flex items-center gap-2">
						<input
							v-model="leaveForm.half_day"
							type="checkbox"
							class="w-4 h-4 rounded border-gray-300"
						/>
						<label class="text-xs font-bold text-gray-500 dark:text-gray-400"
							>Half Day</label
						>
					</div>
					<div>
						<label
							class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-1 block"
							>Reason</label
						>
						<textarea
							v-model="leaveForm.description"
							class="form-input"
							rows="3"
							placeholder="Optional"
						></textarea>
					</div>
				</div>
				<div class="flex gap-2 mt-5">
					<button
						@click="showApplyModal = false"
						class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300"
					>
						Cancel
					</button>
					<button
						@click="submitLeave"
						class="flex-1 px-4 py-2 rounded-lg text-xs font-bold bg-[#D4AF37] text-white hover:bg-[#C4A030]"
						:disabled="hr.applyLeaveResource.loading"
					>
						{{ hr.applyLeaveResource.loading ? 'Submitting...' : 'Submit' }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useHRStore } from '../stores/hr'

const hr = useHRStore()

const showApplyModal = ref(false)
const leaveForm = ref({
	leave_type: '',
	from_date: '',
	to_date: '',
	half_day: false,
	description: '',
})

function statusBg(s) {
	if (s === 'Approved') return 'bg-emerald-100 dark:bg-emerald-900/30'
	if (s === 'Rejected') return 'bg-red-100 dark:bg-red-900/30'
	if (s === 'Open') return 'bg-amber-100 dark:bg-amber-900/30'
	return 'bg-gray-100 dark:bg-gray-800'
}

function statusText(s) {
	if (s === 'Approved') return 'text-emerald-600'
	if (s === 'Rejected') return 'text-red-600'
	if (s === 'Open') return 'text-amber-600'
	return 'text-gray-400'
}

function statusBadge(s) {
	if (s === 'Approved')
		return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
	if (s === 'Rejected') return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
	if (s === 'Open') return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
	return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
}

function refreshAll() {
	hr.loadLeaveBalance()
	hr.loadLeaveApplications()
}

async function submitLeave() {
	const f = leaveForm.value
	await hr.applyLeave(f.leave_type, f.from_date, f.to_date, f.half_day ? 1 : 0, f.description)
	showApplyModal.value = false
	leaveForm.value = {
		leave_type: '',
		from_date: '',
		to_date: '',
		half_day: false,
		description: '',
	}
	refreshAll()
}

async function handleCancel(name) {
	await hr.cancelLeave(name)
	refreshAll()
}

onMounted(() => {
	refreshAll()
	hr.loadLeaveTypes()
})
</script>
