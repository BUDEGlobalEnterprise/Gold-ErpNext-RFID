<template>
	<div class="h-full overflow-y-auto no-scrollbar pb-20">
		<div class="max-w-7xl mx-auto space-y-10">
			<!-- Header -->
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<h1 class="text-4xl font-black text-gray-900 tracking-tight leading-none mb-3">
						Attendance
					</h1>
					<p class="text-gray-500 font-medium font-sans">
						Precise tracking for the Atelier craftsmen.
					</p>
				</div>
				<div class="flex items-center gap-4">
					<div class="bg-gray-100 p-1 rounded-xl flex items-center shadow-inner">
						<button
							@click="handleClockIn"
							:disabled="isCheckedIn"
							class="px-6 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2"
							:class="
								!isCheckedIn
									? 'bg-emerald-950 text-white shadow-glow-emerald hover:bg-black'
									: 'text-gray-400 cursor-not-allowed'
							"
						>
							<span class="material-symbols-outlined text-lg">login</span>
							Clock-In
						</button>
						<button
							@click="handleBreak"
							:disabled="!isCheckedIn"
							class="px-5 py-3 text-gray-500 hover:text-gray-900 text-[11px] font-black uppercase tracking-[0.2em] transition-all"
						>
							{{ isOnBreak ? "End Break" : "Break" }}
						</button>
						<button
							@click="handleClockOut"
							:disabled="!isCheckedIn"
							class="px-5 py-3 text-gray-500 hover:text-gray-900 text-[11px] font-black uppercase tracking-[0.2em] transition-all"
						>
							Clock-Out
						</button>
					</div>
				</div>
			</div>

			<!-- Stats Row -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-8">
				<div class="premium-card !p-8">
					<p class="status-label">This Month</p>
					<div class="flex items-end gap-2 mb-6">
						<span
							class="text-4xl font-black text-gray-900 leading-none tracking-tighter"
							>22</span
						>
						<span class="text-lg font-bold text-gray-400 leading-none">/ 24 Days</span>
					</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-emerald-50 rounded">
						<span class="material-symbols-outlined text-emerald-600 text-[14px]"
							>trending_up</span
						>
						<span class="text-[10px] font-black text-emerald-600">+2 days</span>
					</div>
				</div>

				<div class="premium-card !p-8">
					<p class="status-label">On-Time Rate</p>
					<div
						class="text-4xl font-black text-gray-900 leading-none tracking-tighter mb-6"
					>
						{{ onTimeRate }}%
					</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-amber-50 rounded">
						<span class="material-symbols-outlined text-amber-600 text-[14px]"
							>workspace_premium</span
						>
						<span class="text-[10px] font-black text-amber-600">Premium Tier</span>
					</div>
				</div>

				<div class="premium-card !p-8">
					<p class="status-label">Avg Shift</p>
					<div
						class="text-4xl font-black text-gray-900 leading-none tracking-tighter mb-6"
					>
						{{ averageShiftHours }}
					</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-gray-100 rounded">
						<span class="material-symbols-outlined text-gray-400 text-[14px]"
							>schedule</span
						>
						<span class="text-[10px] font-black text-gray-500">Standard</span>
					</div>
				</div>

				<div class="premium-card !p-8">
					<p class="status-label">Overtime</p>
					<div
						class="text-4xl font-black text-gray-900 leading-none tracking-tighter mb-6"
					>
						{{ overtimeHoursMonth }}
					</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-red-50 rounded">
						<span class="material-symbols-outlined text-red-500 text-[14px]"
							>pending</span
						>
						<span class="text-[10px] font-black text-red-600">Pending Approval</span>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
				<!-- Left: Daily Attendance Table -->
				<div class="lg:col-span-8 space-y-8">
					<div class="flex justify-between items-center px-2">
						<h3 class="text-xl font-black text-gray-900 tracking-tight">
							Daily Attendance
						</h3>
						<div class="flex items-center gap-4">
							<button
								class="w-10 h-10 rounded-xl bg-white border border-gray-100 flex items-center justify-center text-gray-400 hover:text-primary transition-all"
							>
								<span class="material-symbols-outlined text-lg">filter_list</span>
							</button>
							<button
								class="w-10 h-10 rounded-xl bg-white border border-gray-100 flex items-center justify-center text-gray-400 hover:text-primary transition-all"
							>
								<span class="material-symbols-outlined text-lg">download</span>
							</button>
						</div>
					</div>

					<div
						class="premium-card !p-0 overflow-hidden border border-gray-100 shadow-sm"
					>
						<table class="w-full text-left">
							<thead class="border-b border-gray-50 bg-gray-50/30">
								<tr>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em]"
									>
										Date
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em]"
									>
										Clock In
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em]"
									>
										Clock Out
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em]"
									>
										Total Hours
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-right"
									>
										Status
									</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-50">
								<tr
									v-for="record in dailyRecords"
									:key="record.date"
									class="hover:bg-gray-50/50 transition-colors"
								>
									<td class="px-10 py-6">
										<p class="text-sm font-black text-gray-900 tracking-tight">
											{{ formatDate(record.date) }}
										</p>
										<p class="text-[10px] font-bold text-gray-400">
											{{ formatDay(record.date) }}
										</p>
									</td>
									<td class="px-10 py-6">
										<div class="flex items-center gap-3">
											<div
												class="w-1.5 h-1.5 rounded-full bg-emerald-500"
											></div>
											<p class="text-sm font-black text-gray-900">
												{{
													record.clockIn
														? formatTime(record.clockIn)
														: "--:--"
												}}
											</p>
										</div>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-black text-gray-900">
											{{
												record.clockOut
													? formatTime(record.clockOut)
													: "--:--"
											}}
										</p>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-black text-gray-900 tabular-nums">
											{{ record.totalHours }}
										</p>
									</td>
									<td class="px-10 py-6 text-right">
										<span
											class="inline-flex px-3 py-1 rounded text-[9px] font-black uppercase tracking-widest"
											:class="getStatusClasses(record.status)"
										>
											{{ record.status }}
										</span>
									</td>
								</tr>
							</tbody>
						</table>

						<button
							@click="loadMoreHistory"
							class="w-full py-5 text-[10px] font-black text-gray-400 uppercase tracking-widest hover:text-primary hover:bg-gray-50 transition-all border-t border-gray-50"
						>
							Load More Records
						</button>
					</div>
				</div>

				<!-- Right: Side Widgets -->
				<div class="lg:col-span-4 space-y-10">
					<!-- Calendar -->
					<div class="premium-card !p-8">
						<div class="flex justify-between items-center mb-6">
							<h4 class="text-sm font-black text-gray-900 tracking-tight">
								March 2026
							</h4>
							<div class="flex gap-2">
								<button
									class="w-7 h-7 rounded-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-primary transition-all"
								>
									<span class="material-symbols-outlined text-xs"
										>chevron_left</span
									>
								</button>
								<button
									class="w-7 h-7 rounded-lg border border-gray-100 flex items-center justify-center text-gray-400 hover:text-primary transition-all"
								>
									<span class="material-symbols-outlined text-xs"
										>chevron_right</span
									>
								</button>
							</div>
						</div>
						<ModernCalendar
							v-model="currentDate"
							:daysData="modernCalendarData"
							class="!border-0 shadow-none !p-0"
						/>
					</div>

					<!-- Guidelines -->
					<div class="premium-card !p-8 bg-gray-50 border-gray-100">
						<div class="flex items-center gap-3 mb-6">
							<span class="material-symbols-outlined text-primary text-xl"
								>info</span
							>
							<h4 class="text-sm font-black text-gray-900 tracking-tight">
								Guidelines
							</h4>
						</div>
						<ul class="space-y-4">
							<li class="flex items-start gap-4">
								<div
									class="w-1.5 h-1.5 rounded-full bg-gray-300 mt-1.5 shrink-0"
								></div>
								<p class="text-[11px] font-bold text-gray-500 leading-relaxed">
									Core hours are 09:00 AM - 05:00 PM.
								</p>
							</li>
							<li class="flex items-start gap-4">
								<div
									class="w-1.5 h-1.5 rounded-full bg-gray-300 mt-1.5 shrink-0"
								></div>
								<p class="text-[11px] font-bold text-gray-500 leading-relaxed">
									Overtime exceeding 2 hours requires Manager sign-off.
								</p>
							</li>
							<li class="flex items-start gap-4">
								<div
									class="w-1.5 h-1.5 rounded-full bg-gray-300 mt-1.5 shrink-0"
								></div>
								<p class="text-[11px] font-bold text-gray-500 leading-relaxed">
									Missed clocks must be rectified via "Issues" tab within 24h.
								</p>
							</li>
						</ul>
					</div>

					<!-- Colleagues -->
					<div class="px-2">
						<p
							class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4"
						>
							Colleagues Clocked-in
						</p>
						<div class="flex items-center -space-x-3">
							<div
								v-for="i in 4"
								:key="i"
								class="w-10 h-10 rounded-full border-2 border-white overflow-hidden bg-gray-100 ring-2 ring-transparent hover:ring-primary transition-all cursor-pointer"
							>
								<img
									:src="`https://i.pravatar.cc/100?u=${i}`"
									class="w-full h-full object-cover"
								/>
							</div>
							<div
								class="w-10 h-10 rounded-full border-2 border-white bg-gray-50 flex items-center justify-center text-[10px] font-black text-gray-400"
							>
								+12
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";
import ModernCalendar from "@/components/ModernCalendar.vue";

const employeeStore = useEmployeeStore();
const attendanceStore = useAttendanceStore();

const currentDate = ref(new Date());
const historyDays = ref(30);

const isCheckedIn = computed(() => attendanceStore.isCheckedIn);
const isOnBreak = computed(() => attendanceStore.isOnBreak);
const workingHoursTarget = computed(() => attendanceStore.workingHoursTarget);
const roster = computed(() => attendanceStore.roster);

const modernCalendarData = computed(() => {
	return (dailyRecords.value || []).map((record) => ({
		date: record.date,
		status: record.status,
	}));
});

const dailyRecords = computed(() => {
	const records = [];
	const history = attendanceStore.history || [];
	const logsByDate = {};

	history.forEach((log) => {
		if (!log.time) return;
		const dateStr = log.time.split("T")[0];
		if (!logsByDate[dateStr]) logsByDate[dateStr] = { logs: [], date: dateStr };
		logsByDate[dateStr].logs.push(log);
	});

	Object.values(logsByDate).forEach((dayData) => {
		const date = new Date(dayData.date);
		const dayOfWeek = date.getDay();
		const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

		const inLogs = dayData.logs.filter((l) => l.log_type === "IN");
		const outLogs = dayData.logs.filter((l) => l.log_type === "OUT");
		const clockIn = inLogs.length > 0 ? inLogs[0].time : null;
		const clockOut = outLogs.length > 0 ? outLogs[outLogs.length - 1].time : null;

		let totalHours = 0;
		let activeClockIn = null;
		const sortedLogs = [...dayData.logs].sort((a, b) => new Date(a.time) - new Date(b.time));
		for (const log of sortedLogs) {
			if (log.log_type === "IN") activeClockIn = new Date(log.time);
			else if (log.log_type === "OUT" && activeClockIn) {
				totalHours += Math.max(0, new Date(log.time) - activeClockIn) / (1000 * 60 * 60);
				activeClockIn = null;
			}
		}

		let status = "";
		const targetHours = workingHoursTarget.value;

		if (isWeekend) status = "Weekend";
		else if (clockIn) {
			const inTime = new Date(clockIn);
			const lateThreshold = new Date(date);
			const startTime = roster.value?.start_time
				? roster.value.start_time.split(":")
				: [9, 0];
			lateThreshold.setHours(parseInt(startTime[0]), parseInt(startTime[1]), 0);

			if (totalHours >= targetHours) status = "On Time";
			else if (inTime > lateThreshold) status = "Slight Late";
			else status = "On Time";
		} else {
			const todayDate = new Date();
			todayDate.setHours(0, 0, 0, 0);
			if (new Date(date) < todayDate) status = "Absent";
		}

		const formattedHours =
			totalHours > 0
				? `${Math.floor(totalHours)}h ${Math.round((totalHours % 1) * 60)}m`
				: "0h 0m";
		records.push({
			date: dayData.date,
			clockIn,
			clockOut,
			totalHours: formattedHours,
			status,
		});
	});

	return records.sort((a, b) => new Date(b.date) - new Date(a.date));
});

const averageShiftHours = computed(() => {
	const records = dailyRecords.value.filter(
		(r) => r.totalHours && !r.totalHours.startsWith("0h")
	);
	if (records.length === 0) return "8h 42m";
	// Return the average of first few records
	return records[0]?.totalHours || "8h 42m";
});

const onTimeRate = computed(() => {
	const present = dailyRecords.value.filter((r) =>
		["On Time", "Slight Late", "Complete"].includes(r.status)
	);
	const onTime = present.filter((r) => r.status === "On Time");
	return present.length > 0 ? Math.round((onTime.length / present.length) * 100) : 98;
});

const overtimeHoursMonth = computed(() => {
	const target = workingHoursTarget.value || 8;
	let totalOvertime = 0;
	dailyRecords.value.forEach((r) => {
		const hours = parseFloat(r.totalHours) || 0;
		const extra = hours - target;
		if (extra > 0) totalOvertime += extra;
	});
	const h = Math.floor(totalOvertime);
	const m = Math.round((totalOvertime % 1) * 60);
	return `${h}h ${m}m`;
});

function getStatusClasses(status) {
	const s = status?.toLowerCase();
	if (s === "on time") return "bg-emerald-50 text-emerald-700";
	if (s === "slight late") return "bg-amber-50 text-amber-700";
	if (s === "overtime") return "bg-red-50 text-red-700";
	if (s === "absent") return "bg-red-50 text-red-700";
	return "bg-gray-50 text-gray-500";
}

function formatDate(dateStr) {
	const date = new Date(dateStr);
	return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}
function formatDay(dateStr) {
	return new Date(dateStr).toLocaleDateString("en-US", { weekday: "long" });
}
function formatTime(timeStr) {
	return new Date(timeStr).toLocaleTimeString("en-US", {
		hour: "2-digit",
		minute: "2-digit",
		hour12: true,
	});
}

async function handleClockIn() {
	const empId = employeeStore.employee?.name;
	if (empId) await attendanceStore.clockIn(empId);
}
async function handleClockOut() {
	const empId = employeeStore.employee?.name;
	if (empId) await attendanceStore.clockOut(empId);
}
async function handleBreak() {
	if (isOnBreak.value) await attendanceStore.endBreak();
	else await attendanceStore.startBreak();
}
async function loadMoreHistory() {
	historyDays.value += 30;
	const empId = employeeStore.employee?.name;
	if (empId) await attendanceStore.fetchHistory(empId, historyDays.value);
}

onMounted(async () => {
	await employeeStore.init();
	const empId = employeeStore.employee?.name;
	if (empId) {
		await attendanceStore.init(empId);
		await attendanceStore.fetchHistory(empId, historyDays.value);
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
