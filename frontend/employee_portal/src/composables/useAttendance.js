/**
 * useAttendance Composable
 *
 * Extracts attendance clock-in/out logic from AttendanceView.vue
 * into a reusable composable for dashboard and attendance views.
 */
import { ref, computed, onMounted } from "vue";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";

export function useAttendance() {
	const employeeStore = useEmployeeStore();
	const attendanceStore = useAttendanceStore();

	const historyDays = ref(30);

	const isCheckedIn = computed(() => attendanceStore.isCheckedIn);
	const isOnBreak = computed(() => attendanceStore.isOnBreak);
	const totalHoursToday = computed(() => attendanceStore.totalHoursToday);
	const overtimeHours = computed(() => attendanceStore.overtimeHours);
	const workingHoursTarget = computed(() => attendanceStore.workingHoursTarget);
	const roster = computed(() => attendanceStore.roster);
	const canManageBreak = computed(() => attendanceStore.canManageBreak);
	const formattedTimer = computed(() => attendanceStore.formattedWorkedTime);
	const timerLabel = computed(() => attendanceStore.timerLabel);
	const hasWorkedToday = computed(() => attendanceStore.workedSecondsToday > 0);
	const shiftComplete = computed(() => attendanceStore.shiftComplete);

	const timerCircleClass = computed(() => {
		if (!hasWorkedToday.value && !isCheckedIn.value && !isOnBreak.value) return "bg-white/5";
		if (isOnBreak.value && !shiftComplete.value) return "bg-sky-500/10";
		return shiftComplete.value ? "bg-emerald-500/10" : "bg-amber-500/10";
	});

	const timerTextClass = computed(() => {
		if (!hasWorkedToday.value && !isCheckedIn.value && !isOnBreak.value)
			return "text-white/40";
		if (isOnBreak.value && !shiftComplete.value) return "text-sky-400";
		return shiftComplete.value ? "text-emerald-400" : "text-amber-400";
	});

	const attendanceEvents = computed(() => {
		return (attendanceStore.history || [])
			.filter((log) => log.log_type === "IN")
			.map((log) => log.time.split("T")[0]);
	});

	const dailyRecords = computed(() => {
		const records = [];
		const history = attendanceStore.history || [];
		const logsByDate = {};

		history.forEach((log) => {
			if (!log.time) return;
			const dateStr = log.time.split("T")[0];
			if (!logsByDate[dateStr]) {
				logsByDate[dateStr] = { logs: [], date: dateStr };
			}
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
			const sortedLogs = [...dayData.logs].sort(
				(a, b) => new Date(a.time) - new Date(b.time)
			);
			for (const log of sortedLogs) {
				if (log.log_type === "IN") {
					activeClockIn = new Date(log.time);
				} else if (log.log_type === "OUT" && activeClockIn) {
					totalHours +=
						Math.max(0, new Date(log.time) - activeClockIn) / (1000 * 60 * 60);
					activeClockIn = null;
				}
			}

			let status = "";
			const targetHours = workingHoursTarget.value;

			if (isWeekend) {
				status = "weekend";
			} else if (clockIn) {
				const inTime = new Date(clockIn);
				const lateThreshold = new Date(date);
				const startTime = roster.value?.start_time
					? roster.value.start_time.split(":")
					: [9, 0];
				lateThreshold.setHours(parseInt(startTime[0]), parseInt(startTime[1]), 0);

				if (totalHours >= targetHours) {
					status = "complete";
				} else if (inTime > lateThreshold) {
					status = "late";
				} else {
					status = "present";
				}
			} else {
				const todayDate = new Date();
				todayDate.setHours(0, 0, 0, 0);
				const compareDate = new Date(date);
				compareDate.setHours(0, 0, 0, 0);
				if (compareDate < todayDate) {
					status = "absent";
				}
			}

			records.push({ date: dayData.date, clockIn, clockOut, totalHours, status });
		});

		records.sort((a, b) => new Date(b.date) - new Date(a.date));
		return records;
	});

	const totalHours = computed(() => {
		return dailyRecords.value.reduce((sum, r) => sum + (r.totalHours || 0), 0);
	});

	const onTimeRate = computed(() => {
		const present = dailyRecords.value.filter((r) =>
			["present", "late", "complete"].includes(r.status)
		);
		const onTime = present.filter((r) => r.status !== "late");
		return present.length > 0 ? Math.round((onTime.length / present.length) * 100) : 100;
	});

	const averageShiftHours = computed(() => {
		const withHours = dailyRecords.value.filter((r) => r.totalHours > 0);
		if (withHours.length === 0) return 0;
		const total = withHours.reduce((sum, r) => sum + r.totalHours, 0);
		return (total / withHours.length).toFixed(1);
	});

	function formatDate(dateStr) {
		if (!dateStr) return "";
		const date = new Date(dateStr);
		return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
	}

	function formatDay(dateStr) {
		if (!dateStr) return "";
		const date = new Date(dateStr);
		return date.toLocaleDateString("en-US", { weekday: "short" });
	}

	function formatTime(timeStr) {
		if (!timeStr) return "";
		const date = new Date(timeStr);
		return date.toLocaleTimeString("en-US", {
			hour: "2-digit",
			minute: "2-digit",
			hour12: true,
		});
	}

	async function loadMoreHistory() {
		historyDays.value += 30;
		const employeeId = employeeStore.employee?.name;
		if (employeeId) {
			await attendanceStore.fetchHistory(employeeId, historyDays.value);
		}
	}

	async function handleBreak() {
		try {
			if (isOnBreak.value) {
				await attendanceStore.endBreak();
			} else {
				await attendanceStore.startBreak();
			}
			const employeeId = employeeStore.employee?.name;
			if (employeeId) {
				attendanceStore.fetchHistory(employeeId, historyDays.value);
			}
		} catch (error) {
			// Error handled by store
		}
	}

	async function handleClockIn() {
		const employeeId = employeeStore.employee?.name;
		if (!employeeId) return;
		try {
			await attendanceStore.clockIn(employeeId, null, null);
			attendanceStore.fetchHistory(employeeId, historyDays.value);
		} catch (error) {
			// Error handled by store
		}
	}

	async function handleClockOut() {
		const employeeId = employeeStore.employee?.name;
		if (!employeeId) return;
		try {
			await attendanceStore.clockOut(employeeId, null, null);
			attendanceStore.fetchHistory(employeeId, historyDays.value);
		} catch (error) {
			// Error handled by store
		}
	}

	async function initAttendance() {
		await employeeStore.init();
		const employeeId = employeeStore.employee?.name;
		if (employeeId) {
			await attendanceStore.init(employeeId);
			await attendanceStore.fetchHistory(employeeId, historyDays.value);
		}
	}

	return {
		isCheckedIn,
		isOnBreak,
		totalHoursToday,
		overtimeHours,
		workingHoursTarget,
		roster,
		canManageBreak,
		formattedTimer,
		timerLabel,
		hasWorkedToday,
		shiftComplete,
		timerCircleClass,
		timerTextClass,
		attendanceEvents,
		dailyRecords,
		totalHours,
		onTimeRate,
		averageShiftHours,
		formatDate,
		formatDay,
		formatTime,
		loadMoreHistory,
		handleBreak,
		handleClockIn,
		handleClockOut,
		initAttendance,
	};
}
