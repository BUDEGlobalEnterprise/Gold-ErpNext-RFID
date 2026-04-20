<template>
	<div class="h-full overflow-y-auto no-scrollbar pb-20">
		<!-- 3-Column Grid Layout -->
		<div class="grid grid-cols-12 gap-6">
			<!-- LEFT COLUMN (col-span-4) -->
			<div class="col-span-4 space-y-6">
				<!-- Attendance Tracker Card - light gray background -->
				<div class="bg-[#f5f5f5] rounded-xl p-8 flex flex-col items-center">
					<p
						class="text-[10px] font-medium text-gray-500 uppercase tracking-[0.35em] mb-8"
					>
						Attendance Tracker
					</p>

					<!-- Circular Progress -->
					<div class="relative w-48 h-48 flex items-center justify-center mb-8">
						<svg class="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
							<circle
								cx="100"
								cy="100"
								r="86"
								stroke="currentColor"
								stroke-width="5"
								fill="transparent"
								class="text-gray-200"
							/>
							<circle
								cx="100"
								cy="100"
								r="86"
								stroke="currentColor"
								stroke-width="5"
								fill="transparent"
								:stroke-dasharray="circleCircumference"
								:stroke-dashoffset="circleOffset"
								stroke-linecap="round"
								class="text-[#064e3b] transition-all duration-1000"
							/>
						</svg>
						<div class="absolute inset-0 flex flex-col items-center justify-center">
							<p
								class="text-5xl font-bold text-gray-900 leading-none tracking-tight"
							>
								{{ displayTime }}
							</p>
							<p class="text-xs text-gray-500 mt-2">Shift Elapsed</p>
						</div>
					</div>

					<button
						@click="handleClockOut()"
						:disabled="attendance.loading"
						class="w-full py-3 bg-[#064e3b] text-white font-medium rounded-lg text-sm transition-all disabled:opacity-50"
					>
						CLOCK OUT
					</button>
					<button
						@click="handleBreak"
						class="text-sm text-gray-500 mt-3 transition-colors"
					>
						{{ attendance.isOnBreak ? "End Break" : "Request Break Extension" }}
					</button>
				</div>

				<!-- My Profile Card -->
				<div class="bg-white rounded-xl p-6 shadow-sm">
					<div class="flex justify-between items-center mb-5">
						<p
							class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider"
						>
							My Profile
						</p>
						<button class="text-gray-400 ">
							<span class="material-symbols-outlined text-base">edit</span>
						</button>
					</div>
					<div class="flex items-center gap-4 mb-5">
						<div class="w-12 h-12 rounded-full bg-gray-100 overflow-hidden shrink-0">
							<img
								:src="
									employeeStore.employee?.image ||
									'https://i.pravatar.cc/150?u=marcus'
								"
								class="w-full h-full object-cover"
							/>
						</div>
						<div class="min-w-0">
							<p class="text-base font-semibold text-gray-900 truncate">
								{{ auth.user?.full_name || "Marcus Sterling" }}
							</p>
							<p class="text-sm text-gray-500">
								{{ employeeStore.employee?.designation || "Senior Bench Jeweler" }}
							</p>
						</div>
					</div>
					<div class="grid grid-cols-2 gap-3">
						<div class="bg-gray-50 rounded-lg p-3">
							<p class="text-[11px] text-gray-500 mb-0.5">Employee ID</p>
							<p class="text-sm font-semibold text-gray-900">
								{{ employeeStore.employee?.name || "JP-7702" }}
							</p>
						</div>
						<div class="bg-gray-50 rounded-lg p-3">
							<p class="text-[11px] text-gray-500 mb-0.5">Experience</p>
							<p class="text-sm font-semibold text-gray-900">12 Years</p>
						</div>
					</div>
				</div>
			</div>

			<!-- CENTER COLUMN (col-span-5) -->
			<div class="col-span-5 space-y-6">
				<!-- Priority Tasks -->
				<div class="bg-white rounded-xl p-6 shadow-sm">
					<div class="flex justify-between items-start mb-5">
						<div>
							<h3 class="text-lg font-bold text-gray-900">Priority Tasks</h3>
							<p class="text-sm text-gray-500 mt-0.5">
								Precision focus items for today's workshop
							</p>
						</div>
						<div class="bg-amber-100 rounded-lg px-3 py-1.5 text-center">
							<p class="text-sm font-bold text-amber-800 leading-none">
								{{ pendingTasksCount }}
							</p>
							<p
								class="text-[10px] font-medium text-amber-700 uppercase tracking-wider"
							>
								Pending
							</p>
						</div>
					</div>
					<div class="space-y-4">
						<div
							v-for="todo in sortedOpenTodos.slice(0, 3)"
							:key="todo.id"
							class="flex items-start gap-3 group"
						>
							<button
								@click="toggleTodo(todo.id, todo.status)"
								class="w-5 h-5 rounded border-2 border-gray-300 flex items-center justify-center shrink-0 mt-0.5 transition-all group-"
								:class="
									todo.status === 'Closed' ? 'bg-[#064e3b] border-[#064e3b]' : ''
								"
							>
								<span
									v-if="todo.status === 'Closed'"
									class="material-symbols-outlined text-white text-sm"
									>check</span
								>
							</button>
							<div class="flex-1 min-w-0">
								<div class="flex items-center justify-between gap-2">
									<p
										class="text-sm font-medium text-gray-900 truncate"
										:class="
											todo.status === 'Closed'
												? 'line-through text-gray-400'
												: ''
										"
									>
										{{ todo.description }}
									</p>
									<span
										v-if="todo.priority === 'High'"
										class="text-[9px] font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded shrink-0"
										>URGENT</span
									>
								</div>
								<p class="text-xs text-gray-400 mt-1 flex items-center gap-1">
									<span class="material-symbols-outlined text-sm">schedule</span
									>By 14:00 PM
								</p>
								<p
									v-if="todo.status !== 'Closed'"
									class="text-xs text-gray-400 mt-1 flex items-center gap-1"
								>
									<span class="material-symbols-outlined text-sm">work</span
									>Workshop A
								</p>
								<p v-else class="text-xs text-[#064e3b] font-medium mt-1">
									COMPLETED
								</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Activity Stream -->
				<div class="bg-white rounded-xl p-6 shadow-sm">
					<p
						class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-5"
					>
						Activity Stream
					</p>
					<div class="space-y-5">
						<div class="flex gap-4">
							<div
								class="w-9 h-9 rounded-full border-2 border-[#064e3b] flex items-center justify-center shrink-0 mt-0.5"
							>
								<span class="material-symbols-outlined text-[#064e3b] text-lg"
									>verified</span
								>
							</div>
							<div>
								<p class="text-sm font-semibold text-gray-900">Clocked In</p>
								<p class="text-sm text-gray-500 mt-0.5">
									Standard morning shift verified by biometric scan.
								</p>
								<p class="text-xs text-gray-400 mt-1">08:32 AM · TODAY</p>
							</div>
						</div>
						<div class="flex gap-4">
							<div
								class="w-9 h-9 rounded-full border-2 border-gray-200 flex items-center justify-center shrink-0 mt-0.5"
							>
								<span class="material-symbols-outlined text-gray-400 text-lg"
									>receipt_long</span
								>
							</div>
							<div>
								<p class="text-sm font-semibold text-gray-900">
									Expense Claim Approved
								</p>
								<p class="text-sm text-gray-500 mt-0.5">
									Travel reimbursement for Antwerp Trade Show: $450.00
								</p>
								<p class="text-xs text-gray-400 mt-1">YESTERDAY</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- RIGHT COLUMN (col-span-3) -->
			<div class="col-span-3 space-y-6">
				<!-- Upcoming Roster -->
				<div class="bg-white rounded-xl p-6 shadow-sm">
					<p
						class="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-4"
					>
						Upcoming Roster
					</p>
					<div class="space-y-3">
						<div
							v-for="(day, i) in upcomingRoster"
							:key="i"
							class="p-3 rounded-lg"
							:class="
								i === 0
									? 'bg-emerald-50 border-l-4 border-l-[#064e3b]'
									: 'bg-gray-50'
							"
						>
							<p class="text-[10px] font-medium text-gray-500 uppercase">
								{{ day.dayLabel }}
							</p>
							<p class="text-sm font-semibold text-gray-900 mt-0.5">
								{{ day.shift_name }}
							</p>
							<p class="text-xs text-gray-500 mt-0.5">{{ day.timeLocation }}</p>
						</div>
					</div>
					<button
						class="w-full mt-4 py-2 border border-[#064e3b] text-[#064e3b] text-sm font-medium rounded-lg transition-all"
					>
						View Full Calendar
					</button>
				</div>

				<!-- My Payroll - dark green card -->
				<div class="bg-[#064e3b] rounded-xl p-7 text-white overflow-hidden">
					<div class="flex items-center gap-2 mb-5">
						<span class="material-symbols-outlined text-white/60 text-xl"
							>payments</span
						>
						<span
							class="text-[10px] font-medium text-white/60 uppercase tracking-wider"
							>My Payroll</span
						>
					</div>
					<p class="text-sm text-white/50 mb-1">Current Period Earnings</p>
					<p class="text-3xl font-bold text-white/90 mb-8">$4,850.22</p>
					<div class="space-y-3 mb-7">
						<div class="flex justify-between text-xs">
							<span class="text-white/40">Tax Deductions</span
							><span class="text-white/40">-$820.40</span>
						</div>
						<div class="w-full h-px bg-white/10"></div>
						<div class="flex justify-between text-xs">
							<span class="text-white/40">Bonus Items</span
							><span class="text-white/40">+$120.00</span>
						</div>
					</div>
					<button
						class="w-full py-3 bg-white text-[#064e3b] font-semibold rounded-lg text-sm flex items-center justify-center gap-2 transition-all"
					>
						<span class="material-symbols-outlined text-lg">download</span>
						DOWNLOAD STATEMENT
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";
import { useTasksStore } from "@/stores/tasks";

const auth = useAuthStore();
const employeeStore = useEmployeeStore();
const attendance = useAttendanceStore();
const tasksStore = useTasksStore();

const displayTime = computed(() => attendance.formattedWorkedTime);
const circleCircumference = 2 * Math.PI * 86;
const percentComplete = computed(() => {
	if (!attendance.isCheckedIn && !attendance.workedSecondsToday) return 0;
	const target = (attendance.workingHoursTarget || 8) * 3600;
	const current = Math.min(attendance.workedSecondsToday || 0, target);
	return Math.round((current / target) * 100);
});
const circleOffset = computed(
	() => circleCircumference - (percentComplete.value / 100) * circleCircumference
);

const priorityOrder = { High: 1, Medium: 2, Low: 3 };
const sortedOpenTodos = computed(() =>
	[...tasksStore.openTodos].sort(
		(a, b) => (priorityOrder[a.priority] || 99) - (priorityOrder[b.priority] || 99)
	)
);
const pendingTasksCount = computed(() => tasksStore.openTodos.length);

const upcomingRoster = computed(() => [
	{
		dayLabel: "Tomorrow",
		shift_name: "Morning Shift",
		timeLocation: "08:00 - 16:30 · Atelier 1",
	},
	{
		dayLabel: "Wednesday",
		shift_name: "Quality Control Lead",
		timeLocation: "10:00 - 18:30 · Vault 4",
	},
	{ dayLabel: "Thursday", shift_name: "Rest Day", timeLocation: "Paid Time Off" },
]);

async function handleClockOut() {
	const empId = employeeStore.employee?.name;
	if (empId) await attendance.clockOut(empId);
}
async function handleBreak() {
	if (attendance.isOnBreak) await attendance.endBreak();
	else await attendance.startBreak();
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
	}
});
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
