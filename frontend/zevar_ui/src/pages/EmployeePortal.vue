<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">My Portal</h2>
				<button @click="refreshAll" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700" title="Refresh">
					<svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
					</svg>
				</button>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0">
				<div v-if="!hr.employee" class="flex items-center justify-center py-20 text-gray-400">
					<p class="text-sm">No employee profile found for your account.</p>
				</div>

				<div v-else class="space-y-4">
					<div class="premium-card !p-6">
						<div class="flex items-center gap-4">
							<div class="w-16 h-16 rounded-full bg-[#D4AF37]/20 flex items-center justify-center flex-shrink-0">
								<span class="text-2xl font-bold text-[#D4AF37]">{{ initials }}</span>
							</div>
							<div>
								<div class="text-lg font-bold text-gray-900 dark:text-white">{{ hr.employee.employee_name }}</div>
								<div class="text-sm text-gray-500 dark:text-gray-400">{{ hr.employee.designation || 'No designation' }}</div>
								<div class="text-xs text-gray-400">{{ hr.employee.department || '' }} &middot; {{ hr.employee.employment_type || '' }}</div>
							</div>
						</div>
					</div>

					<div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
						<div class="premium-card !p-4 cursor-pointer hover:ring-1 hover:ring-[#D4AF37]/30" @click="$router.push('/time-clock')">
							<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Time Clock</div>
							<div class="text-xs font-bold" :class="hr.todayStatus?.checked_in ? 'text-emerald-500' : 'text-gray-400'">
								{{ hr.todayStatus?.checked_in ? 'Clocked In' : 'Clocked Out' }}
							</div>
							<div v-if="hr.todayStatus?.total_hours_today" class="text-lg font-bold text-[#D4AF37]">{{ hr.todayStatus.total_hours_today }}h</div>
						</div>
						<div class="premium-card !p-4 cursor-pointer hover:ring-1 hover:ring-[#D4AF37]/30" @click="$router.push('/leave')">
							<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Leave</div>
							<div class="text-xs font-bold text-gray-600 dark:text-gray-300">{{ totalLeaveRemaining }} days remaining</div>
						</div>
						<div class="premium-card !p-4">
							<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Salary Slips</div>
							<div class="text-lg font-bold text-gray-900 dark:text-white">{{ hr.salarySlips.length }}</div>
						</div>
						<div class="premium-card !p-4">
							<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Expenses</div>
							<div class="text-lg font-bold text-gray-900 dark:text-white">{{ hr.expenseClaims.length }}</div>
						</div>
					</div>

					<div class="premium-card !p-4">
						<div class="flex items-center justify-between mb-3">
							<h4 class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Recent Salary Slips</h4>
							<router-link to="/reports" class="text-xs text-[#D4AF37] font-bold hover:underline">View All</router-link>
						</div>
						<div v-if="!hr.salarySlips.length" class="text-sm text-gray-400 py-4 text-center">No salary slips found</div>
						<div v-else class="space-y-2">
							<div v-for="slip in hr.salarySlips.slice(0, 5)" :key="slip.id" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-dark-700 last:border-0">
								<div>
									<div class="text-sm font-bold text-gray-900 dark:text-white">{{ slip.start_date }} → {{ slip.end_date }}</div>
								</div>
								<div class="text-right">
									<div class="text-sm font-bold text-[#D4AF37]">{{ formatCurrency(slip.net_pay) }}</div>
									<div class="text-[10px] text-gray-400">Net Pay</div>
								</div>
							</div>
						</div>
					</div>

					<div class="premium-card !p-4">
						<div class="flex items-center justify-between mb-3">
							<h4 class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Expense Claims</h4>
						</div>
						<div v-if="!hr.expenseClaims.length" class="text-sm text-gray-400 py-4 text-center">No expense claims</div>
						<div v-else class="space-y-2">
							<div v-for="claim in hr.expenseClaims.slice(0, 5)" :key="claim.name" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-dark-700 last:border-0">
								<div>
									<div class="text-sm font-bold text-gray-900 dark:text-white">{{ claim.name }}</div>
									<div class="text-[11px] text-gray-500 dark:text-gray-400">{{ claim.posting_date }}</div>
								</div>
								<div class="text-right">
									<div class="text-sm font-bold text-gray-900 dark:text-white">{{ formatCurrency(claim.total_claimed_amount) }}</div>
									<span class="px-2 py-0.5 rounded-full text-[9px] font-bold" :class="expenseStatusBadge(claim.status)">
										{{ claim.status }}
									</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useHRStore } from '../stores/hr'

const hr = useHRStore()

const initials = computed(() => {
	const name = hr.employee?.employee_name || ''
	return name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()
})

const totalLeaveRemaining = computed(() => hr.leaveBalances.reduce((s, b) => s + (b.remaining || 0), 0))

function formatCurrency(val) {
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0)
}

function expenseStatusBadge(s) {
	if (s === 'Approved' || s === 'Paid') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
	if (s === 'Rejected') return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
	return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
}

function refreshAll() {
	hr.loadProfile()
	hr.loadCheckinStatus()
	hr.loadLeaveBalance()
	hr.loadSalarySlips()
	hr.loadExpenseClaims()
}

onMounted(() => {
	refreshAll()
})
</script>
