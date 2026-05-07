<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between mb-6">
				<div>
					<h2 class="premium-title !text-2xl mb-1">Leave Management</h2>
					<p class="text-sm text-gray-500">Plan your time off and track your balances.</p>
				</div>
				<button @click="showApply = true" class="flex items-center gap-2 px-4 py-2 bg-[#D4AF37] text-white rounded-lg font-bold text-sm shadow-lg shadow-[#D4AF37]/20 hover:scale-105 transition-all active:scale-95">
					<span class="material-symbols-outlined text-lg">add_circle</span>
					Request Time Off
				</button>
			</div>

			<!-- Balances Row -->
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
				<div v-for="b in hrStore.leaveBalances" :key="b.leave_type" class="premium-card !p-6 border-l-4" :style="{ borderColor: getLeaveColor(b.leave_type) }">
					<div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">{{ b.leave_type }}</div>
					<div class="flex items-end gap-1">
						<span class="text-3xl font-black text-gray-900 dark:text-white">{{ b.remaining_leaves }}</span>
						<span class="text-xs text-gray-400 mb-1">days left</span>
					</div>
					<div class="mt-4 w-full bg-gray-100 dark:bg-warm-dark-700 rounded-full h-1.5">
						<div class="h-1.5 rounded-full" :style="{ width: getLeaveProgress(b) + '%', backgroundColor: getLeaveColor(b.leave_type) }"></div>
					</div>
				</div>
				<div v-if="!hrStore.leaveBalances.length && !hrStore.balancesResource.loading" class="col-span-full py-10 premium-card text-center text-gray-400 italic text-sm">
					No leave balances found. Contact HR to allocate leaves.
				</div>
			</div>

			<!-- Main Content Grid -->
			<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
				<!-- My Applications -->
				<div class="lg:col-span-8 flex flex-col min-h-0">
					<h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">My Applications</h3>
					<div class="flex-1 overflow-y-auto pr-2">
						<div class="space-y-3">
							<div v-for="app in hrStore.leaveApplications" :key="app.name" class="premium-card !p-4 flex items-center justify-between hover:border-[#D4AF37]/30 transition-colors">
								<div class="flex items-center gap-4">
									<div class="w-10 h-10 rounded-full flex items-center justify-center" :style="{ backgroundColor: getLeaveColor(app.leave_type) + '20', color: getLeaveColor(app.leave_type) }">
										<span class="material-symbols-outlined">{{ getLeaveIcon(app.leave_type) }}</span>
									</div>
									<div>
										<div class="font-bold text-gray-900 dark:text-white text-sm">{{ app.leave_type }}</div>
										<div class="text-[10px] text-gray-500 font-bold uppercase tracking-tighter">
											{{ formatDate(app.from_date) }} — {{ formatDate(app.to_date) }}
										</div>
									</div>
								</div>
								<div class="flex items-center gap-6 text-right">
									<div>
										<div class="text-xs font-black text-gray-900 dark:text-white">{{ app.total_leave_days }} Days</div>
										<div class="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Duration</div>
									</div>
									<div class="w-24 flex justify-center">
										<span class="px-2 py-1 rounded-full text-[9px] font-bold uppercase" :class="getStatusClass(app.status)">
											{{ app.status }}
										</span>
									</div>
									<button v-if="app.status === 'Open'" @click="handleCancel(app.name)" class="p-2 text-gray-400 hover:text-red-500 transition-colors">
										<span class="material-symbols-outlined text-lg">delete</span>
									</button>
								</div>
							</div>
							<div v-if="!hrStore.leaveApplications.length && !hrStore.leavesResource.loading" class="py-20 text-center text-gray-400 flex flex-col items-center">
								<span class="material-symbols-outlined text-4xl mb-2 opacity-20">event_busy</span>
								<p class="text-xs italic font-bold">No leave applications found.</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Calendar / Side Info -->
				<div class="lg:col-span-4 flex flex-col gap-6">
					<div class="premium-card !p-6 bg-gradient-to-br from-warm-dark-800 to-warm-dark-900 border-[#D4AF37]/20">
						<h4 class="text-[10px] font-bold text-[#D4AF37] uppercase tracking-widest mb-4">Quick Tip</h4>
						<p class="text-xs text-gray-400 leading-relaxed">
							Submit your leave requests at least <span class="text-white font-bold">48 hours</span> in advance for faster approval.
						</p>
					</div>

					<div class="premium-card !p-6">
						<h4 class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4">Recent Activity</h4>
						<div class="space-y-4">
							<div v-for="act in recentActivity" :key="act.id" class="flex items-start gap-3">
								<div class="w-1.5 h-1.5 rounded-full mt-1.5" :class="act.dotClass"></div>
								<div>
									<p class="text-xs text-gray-900 dark:text-white font-bold leading-tight">{{ act.text }}</p>
									<span class="text-[9px] text-gray-500 uppercase font-bold">{{ act.time }}</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Apply Modal -->
			<div v-if="showApply" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" @click.self="showApply = false">
				<div class="premium-card !p-8 w-full max-w-lg shadow-2xl animate-in fade-in zoom-in duration-200">
					<div class="flex items-center justify-between mb-8">
						<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tighter">Apply for Leave</h3>
						<button @click="showApply = false" class="p-2 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full transition-colors">
							<span class="material-symbols-outlined">close</span>
						</button>
					</div>

					<div class="space-y-6">
						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block">Leave Type</label>
							<select v-model="form.leave_type" class="w-full bg-gray-50 dark:bg-warm-dark-900 border border-gray-100 dark:border-warm-border rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none appearance-none">
								<option value="" disabled>Select Type</option>
								<option v-for="b in hrStore.leaveBalances" :key="b.leave_type" :value="b.leave_type">{{ b.leave_type }}</option>
							</select>
						</div>

						<div class="grid grid-cols-2 gap-4">
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block">From Date</label>
								<input v-model="form.from_date" type="date" class="w-full bg-gray-50 dark:bg-warm-dark-900 border border-gray-100 dark:border-warm-border rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none" />
							</div>
							<div>
								<label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block">To Date</label>
								<input v-model="form.to_date" type="date" class="w-full bg-gray-50 dark:bg-warm-dark-900 border border-gray-100 dark:border-warm-border rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none" />
							</div>
						</div>

						<div class="flex items-center gap-3 py-2">
							<input v-model="form.half_day" type="checkbox" id="half-day" class="w-4 h-4 text-[#D4AF37] rounded border-gray-300 focus:ring-[#D4AF37]" />
							<label for="half-day" class="text-xs font-bold text-gray-700 dark:text-gray-300">Half Day Request</label>
						</div>

						<div>
							<label class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block">Reason (Optional)</label>
							<textarea v-model="form.reason" rows="3" placeholder="Tell us why..." class="w-full bg-gray-50 dark:bg-warm-dark-900 border border-gray-100 dark:border-warm-border rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-[#D4AF37] outline-none resize-none"></textarea>
						</div>
					</div>

					<div class="flex gap-4 mt-10">
						<button @click="showApply = false" class="flex-1 py-3 bg-gray-100 dark:bg-warm-dark-700 text-gray-700 dark:text-gray-300 rounded-xl font-bold text-sm hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition-colors">Cancel</button>
						<button @click="handleApply" class="flex-[2] py-3 bg-[#D4AF37] text-white rounded-xl font-bold text-sm shadow-xl shadow-[#D4AF37]/20 hover:scale-[1.02] active:scale-95 transition-all">Submit Request</button>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { toast } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import { useHRStore } from '@/stores/hr.js'

const hrStore = useHRStore()
const showApply = ref(false)
const form = ref({
	leave_type: '',
	from_date: '',
	to_date: '',
	reason: '',
	half_day: false
})

const recentActivity = [
	{ id: 1, text: 'Sick Leave request approved by HR', time: '2 DAYS AGO', dotClass: 'bg-emerald-500' },
	{ id: 2, text: 'You submitted a Vacation request', time: '5 DAYS AGO', dotClass: 'bg-blue-500' },
	{ id: 3, text: 'Holiday: Spring Festival', time: '1 WEEK AGO', dotClass: 'bg-amber-500' }
]

function getLeaveColor(type) {
	const map = {
		'Vacation': '#3b82f6',
		'Sick Leave': '#ef4444',
		'Casual Leave': '#f59e0b',
		'Compensatory Off': '#10b981',
		'Maternity Leave': '#ec4899',
		'Paternity Leave': '#8b5cf6'
	}
	return map[type] || '#64748b'
}

function getLeaveIcon(type) {
	const map = {
		'Vacation': 'flight',
		'Sick Leave': 'medical_services',
		'Casual Leave': 'event_available',
		'Compensatory Off': 'history'
	}
	return map[type] || 'calendar_today'
}

function getLeaveProgress(b) {
	if (!b.total_leaves) return 0
	return (b.leaves_taken / b.total_leaves) * 100
}

function formatDate(d) {
	if (!d) return '-'
	return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function getStatusClass(status) {
	const map = {
		'Approved': 'bg-emerald-100 text-emerald-700',
		'Pending': 'bg-amber-100 text-amber-700',
		'Open': 'bg-blue-100 text-blue-700',
		'Rejected': 'bg-red-100 text-red-700',
		'Cancelled': 'bg-gray-100 text-gray-500'
	}
	return map[status] || 'bg-gray-100 text-gray-500'
}

async function handleApply() {
	if (!form.value.leave_type || !form.value.from_date || !form.value.to_date) {
		toast({ title: 'Missing Information', message: 'Please fill all required fields', icon: 'alert-circle', intent: 'warning' })
		return
	}

	try {
		const res = await hrStore.applyLeave(
			form.value.leave_type,
			form.value.from_date,
			form.value.to_date,
			form.value.reason,
			form.value.half_day ? 1 : 0
		)
		if (res.success) {
			toast({ title: 'Success', message: 'Leave request submitted successfully', icon: 'check', intent: 'success' })
			showApply.value = false
			form.value = { leave_type: '', from_date: '', to_date: '', reason: '', half_day: false }
			hrStore.loadAll()
		}
	} catch (e) {
		toast({ title: 'Error', message: e.message || 'Failed to submit request', icon: 'alert-circle', intent: 'danger' })
	}
}

async function handleCancel(name) {
	if (!confirm('Are you sure you want to cancel this leave application?')) return
	
	try {
		const res = await hrStore.cancelLeave(name)
		if (res.success) {
			toast({ title: 'Cancelled', message: 'Leave application removed', icon: 'check', intent: 'success' })
			hrStore.loadAll()
		}
	} catch (e) {
		toast({ title: 'Error', message: e.message || 'Failed to cancel', icon: 'alert-circle', intent: 'danger' })
	}
}

onMounted(() => {
	hrStore.loadAll()
})
</script>

<style scoped>
.font-black { font-family: 'Inter', sans-serif; font-weight: 900; }
.font-800 { font-family: 'Inter', sans-serif; font-weight: 800; }
</style>
