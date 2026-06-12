<template>
	<!-- Greeting Header -->
		<div class="mb-6">
			<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
				Welcome, <span class="text-[#064e3b] dark:text-emerald-400">{{ auth.user?.first_name || auth.user?.full_name?.split(' ')[0] || 'there' }}</span>
			</h1>
		</div>

		<!-- Main Banner Split: Clock + Upcoming Roster -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
			<!-- Clock & Today's Details -->
			<div class="bg-[#f5f5f5] dark:bg-white/5 rounded-xl p-8 flex flex-col items-center justify-center gap-8">
				<!-- Clock Widget -->
				<div class="flex-shrink-0">
					<ClockWidget @punched="refreshDashboard" />
				</div>

				<!-- Clock In Info (bottom, centered) -->
				<div v-if="isClockedIn && !isCompleted" class="w-full max-w-md">
					<p class="text-[10px] font-medium text-gray-500 dark:text-white/50 uppercase tracking-[0.35em] mb-4 text-center">
						Today's Details
					</p>
					<div class="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
						<div>
							<div class="w-10 h-10 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/15 flex items-center justify-center mx-auto mb-2">
								<span class="material-symbols-outlined text-emerald-600 dark:text-emerald-400 text-lg">schedule</span>
							</div>
							<p class="text-[11px] text-gray-500 dark:text-white/50 mb-1">Clock In Time</p>
							<p class="text-lg font-bold text-gray-900 dark:text-white tabular-nums">
								{{ clockInTimeFormatted || '—' }}
							</p>
						</div>
						<div>
							<div class="w-10 h-10 rounded-xl bg-orange-500/10 dark:bg-orange-500/15 flex items-center justify-center mx-auto mb-2">
								<span class="material-symbols-outlined text-orange-600 dark:text-orange-400 text-lg">coffee</span>
							</div>
							<p class="text-[11px] text-gray-500 dark:text-white/50 mb-1">Breaks Today</p>
							<p class="text-lg font-bold text-gray-900 dark:text-white tabular-nums">
								{{ breakCount }} · {{ breakMinutesFormatted }}
							</p>
						</div>
						<div>
							<div class="w-10 h-10 rounded-xl bg-blue-500/10 dark:bg-blue-500/15 flex items-center justify-center mx-auto mb-2">
								<span class="material-symbols-outlined text-blue-600 dark:text-blue-400 text-lg">timer</span>
							</div>
							<p class="text-[11px] text-gray-500 dark:text-white/50 mb-1">Hours Worked</p>
							<p class="text-lg font-bold text-gray-900 dark:text-white tabular-nums">
								{{ hoursWorked }}
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Upcoming Roster (Top Right) -->
			<div class="bg-white dark:bg-white/5 rounded-xl p-8 shadow-sm flex flex-col">
				<p class="text-[11px] font-semibold text-gray-500 dark:text-white/50 uppercase tracking-wider mb-6">
					Upcoming Roster
				</p>
				<div class="space-y-4 flex-1">
					<div v-for="(day, i) in upcomingRoster" :key="i" class="p-5 rounded-2xl transition-all" :class="i === 0 ? 'bg-emerald-50 dark:bg-emerald-500/10 border-l-4 border-l-[#064e3b] dark:border-l-emerald-400' : 'bg-gray-50 dark:bg-white/5'">
						<div class="flex justify-between items-start">
							<div>
								<p class="text-[11px] font-bold text-gray-500 dark:text-white/40 uppercase tracking-tight">
									{{ day.dayLabel }}
								</p>
								<p class="text-lg font-bold text-gray-900 dark:text-white mt-1">
									{{ day.shift_name }}
								</p>
							</div>
							<div class="text-right">
								<p class="text-sm font-semibold text-gray-700 dark:text-emerald-400">
									{{ day.timeLocation }}
								</p>
							</div>
						</div>
					</div>
				</div>
				<button
					@click="openroster()"
					class="w-full mt-8 py-3.5 border-2 border-[#064e3b] dark:border-emerald-400/30 text-[#064e3b] dark:text-emerald-400 text-sm font-bold rounded-xl transition-all hover:bg-[#064e3b] hover:text-white dark:hover:bg-emerald-500 dark:hover:text-white"
				>
					View Full Calendar
				</button>
			</div>
		</div>

		<!-- Leave / Holiday / Count Cards -->
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 mb-6">
			<!-- Available Leaves -->
			<div class="bg-white dark:bg-white/5 rounded-xl p-6 shadow-sm">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/15 flex items-center justify-center">
						<span class="material-symbols-outlined text-emerald-600 dark:text-emerald-400 text-lg">event_busy</span>
					</div>
					<p class="text-[11px] font-semibold text-gray-500 dark:text-white/50 uppercase tracking-wider">Available Leaves</p>
				</div>
				<p class="text-3xl font-bold text-gray-900 dark:text-white tabular-nums">{{ availableLeaves }}</p>
				<p class="text-xs text-gray-500 dark:text-white/50 mt-1">days remaining</p>
			</div>

			<!-- Present This Month -->
			<div class="bg-white dark:bg-white/5 rounded-xl p-6 shadow-sm">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl bg-amber-500/10 dark:bg-amber-500/15 flex items-center justify-center">
						<span class="material-symbols-outlined text-amber-600 dark:text-amber-400 text-lg">event_busy</span>
					</div>
					<p class="text-[11px] font-semibold text-gray-500 dark:text-white/50 uppercase tracking-wider">Present</p>
				</div>
				<p class="text-3xl font-bold text-gray-900 dark:text-white tabular-nums">{{ precentInThisMonth }}</p>
				<p class="text-xs text-gray-500 dark:text-white/50 mt-1">present days</p>
			</div>

			<!-- Absent -->
			<div class="bg-white dark:bg-white/5 rounded-xl p-6 shadow-sm">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl bg-red-500/10 dark:bg-red-500/15 flex items-center justify-center">
						<span class="material-symbols-outlined text-red-600 dark:text-red-400 text-lg">cancel</span>
					</div>
					<p class="text-[11px] font-semibold text-gray-500 dark:text-white/50 uppercase tracking-wider">Absent</p>
				</div>
				<p class="text-3xl font-bold text-gray-900 dark:text-white tabular-nums">{{ absentInThisMonth }}</p>
				<p class="text-xs text-gray-500 dark:text-white/50 mt-1">absent days</p>
			</div>
		</div>

		<!-- 2-Column Bottom Layout -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- LEFT COLUMN: Priority Tasks -->
			<div class="bg-white dark:bg-white/5 rounded-xl p-6 shadow-sm">
				<div class="flex justify-between items-start mb-5">
					<div>
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">Priority Tasks</h3>
						<p class="text-sm text-gray-500 dark:text-white/50 mt-0.5">
							Precision focus items for today
						</p>
					</div>
					<div class="bg-amber-100 dark:bg-amber-500/20 rounded-lg px-3 py-1.5 text-center">
						<p class="text-sm font-bold text-amber-800 dark:text-amber-400 leading-none">
							{{ pendingTasksCount }}
						</p>
						<p class="text-[10px] font-medium text-amber-700 dark:text-amber-300 uppercase tracking-wider">
							Pending
						</p>
					</div>
				</div>
				<div class="space-y-4">
					<div v-for="todo in sortedOpenTodos.slice(0, 5)" :key="todo.id" class="flex items-start gap-3 group border-b border-gray-50 dark:border-white/5 pb-4 last:border-0 last:pb-0">
						<div class="flex-1 min-w-0">
							<div class="flex items-center justify-between gap-2">
								<p class="text-sm font-medium text-gray-900 dark:text-white truncate" :class="todo.status === 'Closed' ? 'line-through text-gray-400 dark:text-white/30' : ''">
									{{ todo.description }}
								</p>
								<span class="text-[9px] font-bold px-2 py-0.5 rounded shrink-0" :class="{
									'text-red-600 bg-red-50 dark:bg-red-500/20 dark:text-red-400': todo.priority === 'High',
									'text-yellow-600 bg-yellow-50 dark:bg-yellow-500/20 dark:text-yellow-400': todo.priority === 'Medium',
									'text-green-600 bg-green-50 dark:bg-green-500/20 dark:text-green-400': todo.priority === 'Low'
								}">
									{{ todo.priority }}
								</span>
							</div>
							<p class="text-xs text-gray-400 dark:text-white/40 mt-1 flex items-center gap-1">
								<span class="material-symbols-outlined text-sm">schedule</span>{{ todo.date }}
							</p>
							<p class="text-xs text-[#064e3b] dark:text-emerald-400 font-medium mt-1">
								{{ todo.status }}
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- RIGHT COLUMN: My Payroll (Bottom Right) -->
			<div class="bg-[#064e3b] rounded-xl p-8 text-white overflow-hidden flex flex-col justify-between shadow-lg">
				<div>
					<div class="flex items-center gap-2 mb-6">
						<span class="material-symbols-outlined text-white/60 text-xl">payments</span>
						<span class="text-[11px] font-semibold text-white/60 uppercase tracking-wider">My Payroll</span>
					</div>
					<p class="text-sm text-white/50 mb-1">Current Period Earnings</p>
					<p class="text-4xl font-bold text-white mb-8">${{ currentPeriodEarnings.toFixed(2) }}</p>
					
					<div class="space-y-4 mb-10">
						<div class="flex justify-between items-center">
							<span class="text-sm text-white/60 font-medium">Tax Deductions</span>
							<span class="text-sm font-bold text-white/80">-${{ taxDeductions.toFixed(2) }}</span>
						</div>
						<div class="w-full h-px bg-white/10"></div>
						<div class="flex justify-between items-center">
							<span class="text-sm text-white/60 font-medium">Bonus Items</span>
							<span class="text-sm font-bold text-white/80">+${{ bonusItems.toFixed(2) }}</span>
						</div>
					</div>
				</div>
				
				<button
					class="w-full py-4 bg-white text-[#064e3b] font-bold rounded-xl text-sm flex items-center justify-center gap-2 transition-all hover:bg-gray-100 active:scale-[0.98] shadow-md"
					@click="downloadStatement()"
				>
					<span class="material-symbols-outlined text-lg">download</span>
					DOWNLOAD STATEMENT
				</button>
			</div>
		</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";
import { useTasksStore } from "@/stores/tasks";
import ClockWidget from "@/components/ClockWidget.vue";
import "@/services/api";
import { usePayrollStore } from "../stores/payroll";

const auth = useAuthStore();
const employeeStore = useEmployeeStore();
const attendance = useAttendanceStore();
const tasksStore = useTasksStore();
const loading = ref(true);
const payrollStore = usePayrollStore();
let loadInProgress = false;
let lastLoadTime = 0;

//values for payroll card
const currentPeriodEarnings = ref(0);
const taxDeductions = ref(0);
const bonusItems = ref(0);
const latestSlipId = ref(null);


// Reactive state for banner display
const isClockedIn = computed(() => attendance.todayStatus?.checked_in && !attendance.todayStatus?.is_on_break && !attendance.todayStatus?.last_log_type);
const isCompleted = computed(() => attendance.todayStatus?.last_log_type === "OUT");
const clockInTimeFormatted = computed(() => {
	const firstIn = attendance.todayStatus?.logs?.find((l) => l.log_type === "IN");
	if (!firstIn) return "";
	return new Date(firstIn.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
});
const breakCount = computed(() => attendance.todayStatus?.logs?.filter((l) => l.note === "Break Start").length || 0);
const totalBreakMinutes = computed(() => {
	const logs = attendance.todayStatus?.logs || [];
	const breakStartLogs = logs.filter((l) => l.note === "Break Start");
	const breakEndLogs = logs.filter((l) => l.note === "Break End");
	let totalMs = 0;
	for (let i = 0; i < breakEndLogs.length; i++) {
		totalMs += new Date(breakEndLogs[i].time).getTime() - new Date(breakStartLogs[i].time).getTime();
	}
	return totalMs / 60000;
});

const breakMinutesFormatted = computed(() => {
	const totalMinutes = Math.floor(totalBreakMinutes.value);
	const h = Math.floor(totalMinutes / 60);
	const m = Math.floor(totalMinutes % 60);
	const s = Math.floor((totalBreakMinutes.value * 60) % 60);
	return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
});

const hoursWorked = computed(() => {
	const firstIn = attendance.todayStatus?.logs?.find((l) => l.log_type === "IN");
	const lastOut = attendance.todayStatus?.logs?.find((l) => l.log_type === "OUT");
	if (!firstIn) return "—";
	const start = new Date(firstIn.time).getTime();
	const end = lastOut ? new Date(lastOut.time).getTime() : Date.now();
	const totalHours = (end - start) / (1000 * 60 * 60);
	const breakMinutes = totalBreakMinutes.value;
	const netHours = totalHours - breakMinutes / 60;
	if (netHours < 1) return `${Math.round(netHours * 60)}m`;
	const h = Math.floor(netHours);
	const m = Math.round((netHours - h) * 60);
	return m > 0 ? `${h}h ${m}m` : `${h}h`;
});

// Leave / holiday / working days data
const availableLeaves = ref(0);
const precentInThisMonth = ref(0);
const absentInThisMonth = ref(0);

const clockInTime = ref(null);
async function loadDashboard() {
	const empId = employeeStore.employee?.name;
	if (loadInProgress || !empId) return;
	loadInProgress = true;

	try {
		// 1. Attendance status
		const statusRes = await fetch(`/api/method/zevar_core.api.attendance.get_today_checkin_status?employee_id=${encodeURIComponent(empId)}`);
		const statusData = await statusRes.json();
		if (statusData.message) {
			attendance.todayStatus.value = statusData.message;
			attendance.syncTimerFromStatus();
		}

		// 2. Leave balance — backend returns a plain number
		const leaveRes = await fetch(`/api/method/zevar_core.api.attendance.get_leave_balance?employee=${encodeURIComponent(empId)}`);
		const leaveData = await leaveRes.json();
		if (leaveData.message !== undefined) {
			availableLeaves.value = leaveData.message;
		}

		// Attendance Summary
		const summaryRes = await fetch("/api/method/zevar_core.api.attendance.get_attendance_summary");
		const summaryData = await summaryRes.json();
		if (summaryData.message) {
			precentInThisMonth.value = summaryData.message.present || 0;
			absentInThisMonth.value = summaryData.message.absent || 0;
		}

		// Next 3 days roster
		const rosterRes = await fetch(
			`/api/method/zevar_core.api.roster.get_next_three_days_roster?employee_id=${encodeURIComponent(empId)}`
		);
		const rosterData = await rosterRes.json();
		if (Array.isArray(rosterData.message)) {
			upcomingRosterData.value = rosterData.message;
		}

		// Payroll — current period (latest salary slip)
		const payrollRes = await fetch(`/api/method/zevar_core.api.payroll.get_salary_slips?employee_id=${encodeURIComponent(empId)}`);
		const payrollData = await payrollRes.json();
		if (payrollData.message && payrollData.message.length > 0) {
			const latest = payrollData.message[0];
			latestSlipId.value = latest.id;
			currentPeriodEarnings.value = latest.gross_pay || 0;
			taxDeductions.value = latest.total_deduction || 0;
			// Bonus = earnings not covered by gross_pay (not directly available in latest slip; placeholder)
			bonusItems.value = 0;
		}
	} catch (e) {
		// Handle errors (e.g., show notification)
	} finally {
		loading.value = false;
		loadInProgress = false;
	}
}

const priorityOrder = { High: 1, Medium: 2, Low: 3 };
const sortedOpenTodos = computed(() =>
	[...tasksStore.openTodos].sort(
		(a, b) => (priorityOrder[a.priority] || 99) - (priorityOrder[b.priority] || 99)
	)
);
const pendingTasksCount = computed(() => tasksStore.openTodos.length);

const upcomingRosterData = ref([]);
const upcomingRoster = computed(() =>
	upcomingRosterData.value.map((d) => ({
		dayLabel: d.day_name,
		shift_name: d.shift_name,
		timeLocation: d.is_off
			? "Off"
			: `${formatTime(d.start_time)} - ${formatTime(d.end_time)}`,
	}))
);

function formatTime(t) {
	if (!t) return "";
	if (typeof t === "string") {
		const [h, m] = t.split(":");
		return `${h}:${m}`;
	}
	return t.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function openroster() {
	window.open("/employee-portal#/roster", "_self");
}
async function downloadStatement() {
	if (!latestSlipId.value) return;
	
	// Calling our custom, secure backend method
	const url = `/api/method/zevar_core.api.payroll.download_salary_slip?slip_name=${encodeURIComponent(latestSlipId.value)}`;
	window.open(url, "_blank");
}
async function toggleTodo(todoId, currentStatus) {
	await tasksStore.toggleTodo(todoId, currentStatus);
}
onMounted(async () => {
	await employeeStore.init();
	const empId = employeeStore.employee?.name;
	if (empId) {
		await attendance.init(empId);
		tasksStore.init();
		loadDashboard();
	}
});

// Called from ClockWidget when punch changes
async function refreshDashboard() {
	await employeeStore.init();
	const empId = employeeStore.employee?.name;
	if (empId) {
		// Clear caches and reload
		localStorage.removeItem("cache_today_status");
		await attendance.fetchTodayStatus(empId);
		await loadDashboard();
	}
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
</style>
