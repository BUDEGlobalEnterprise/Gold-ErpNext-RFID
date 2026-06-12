import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, computed } from "vue";

export const useAttendanceStore = defineStore("attendance", () => {
	const todayStatus = ref(null);
	const roster = ref(null);
	const history = ref([]);
	const loading = ref(false);
	const error = ref(null);
	const workedSecondsToday = ref(0);
	const employeeId = ref(null);
	let timerInterval = null;

	const employeeList = ref([]);
	const monthlyRoster = ref(null);

	// Today's check-in status
	const todayStatusResource = createResource({
		url: "zevar_core.api.attendance.get_today_checkin_status",
		auto: false,
		onSuccess(data) {
			todayStatus.value = data;
		},
	});

	// Employee roster info
	const rosterResource = createResource({
		url: "zevar_core.api.attendance.get_employee_roster",
		auto: false,
		onSuccess(data) {
			roster.value = data;
		},
	});

	// Clock in
	const clockInResource = createResource({
		url: "zevar_core.api.attendance.clock_in",
		auto: false,
	});

	// Clock out
	const clockOutResource = createResource({
		url: "zevar_core.api.attendance.clock_out",
		auto: false,
	});

	// Break start (creates an OUT record with break note)
	const breakStartResource = createResource({
		url: "zevar_core.api.attendance.clock_out",
		auto: false,
	});

	// Break end (creates an IN record with break note)
	const breakEndResource = createResource({
		url: "zevar_core.api.attendance.clock_in",
		auto: false,
	});

	// History
	const historyResource = createResource({
		url: "zevar_core.api.attendance.get_attendance_history",
		auto: false,
		onSuccess(data) {
			history.value = data?.records || data || [];
		},
	});

	// Employee list for marking attendance
	const employeeListResource = createResource({
		url: "zevar_core.api.roster.get_employee_list",
		auto: false,
		onSuccess(data) {
			employeeList.value = data || [];
		},
	});

	// Monthly roster
	const monthlyRosterResource = createResource({
		url: "zevar_core.api.roster.get_monthly_roster",
		auto: false,
		onSuccess(data) {
			monthlyRoster.value = data;
		},
	});

	// Check if user can mark attendance (create permission)
	const canMarkAttendanceResource = createResource({
		url: "zevar_core.api.attendance.can_mark_attendance",
		auto: false,
	});

	// Check if user can manage attendance (write permission — view other employees' data)
	const canManageAttendanceResource = createResource({
		url: "zevar_core.api.attendance.can_manage_attendance",
		auto: false,
	});

	// Check if user can view attendance (read permission — gate employee filter)
	const canViewAttendanceResource = createResource({
		url: "zevar_core.api.attendance.can_view_attendance",
		auto: false,
	});

	// Mark attendance
	const markAttendanceResource = createResource({
		url: "zevar_core.api.attendance.mark_attendance",
		auto: false,
	});

	// Computed
	const isCheckedIn = computed(() => {
		return todayStatus.value?.checked_in || false;
	});

	const isOnBreak = computed(() => {
		return todayStatus.value?.is_on_break || false;
	});

	const totalSecondsToday = computed(() => {
		if (typeof todayStatus.value?.total_seconds_today === "number") {
			return todayStatus.value.total_seconds_today;
		}
		return Math.round((todayStatus.value?.total_hours_today || 0) * 3600);
	});

	const totalHoursToday = computed(() => {
		return Number((workedSecondsToday.value / 3600).toFixed(2));
	});

	const overtimeHours = computed(() => {
		const overtime = workedSecondsToday.value / 3600 - workingHoursTarget.value;
		return Number(Math.max(0, overtime).toFixed(2));
	});

	const workingHoursTarget = computed(() => {
		return roster.value?.working_hours || todayStatus.value?.working_hours_target || 8;
	});

	const shiftComplete = computed(() => {
		return (
			workedSecondsToday.value >= workingHoursTarget.value * 3600 &&
			workedSecondsToday.value > 0
		);
	});

	const canManageBreak = computed(() => {
		return isCheckedIn.value || isOnBreak.value;
	});

	const timerLabel = computed(() => {
		if (isOnBreak.value) return "Break Paused";
		if (isCheckedIn.value) return "Shift Time";
		if (workedSecondsToday.value > 0) return "Today's Total";
		return "Not Clocked In";
	});

	const formattedWorkedTime = computed(() => {
		const totalSeconds = Math.floor(workedSecondsToday.value);
		const hours = Math.floor(totalSeconds / 3600);
		const minutes = Math.floor((totalSeconds % 3600) / 60);
		const seconds = totalSeconds % 60;
		return `${hours.toString().padStart(2, "0")}:${minutes
			.toString()
			.padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
	});

	function getErrorMessage(error) {
		if (!error) return "";
		if (typeof error === "string") return error;
		if (Array.isArray(error.messages)) return error.messages.join(" ");
		if (typeof error.messages === "string") return error.messages;
		return error.message || String(error);
	}

	function clearTimerTicker() {
		if (timerInterval) {
			clearInterval(timerInterval);
			timerInterval = null;
		}
	}

	function startTimerTicker() {
		clearTimerTicker();
		timerInterval = setInterval(() => {
			workedSecondsToday.value += 1;
		}, 1000);
	}

	function syncTimerFromStatus() {
		// Always clear timer first to prevent duplicates
		clearTimerTicker();

		// Sync worked seconds from backend data
		workedSecondsToday.value = totalSecondsToday.value;

		// Start timer only if checked in AND not on break
		if (isCheckedIn.value && !isOnBreak.value) {
			startTimerTicker();
		}
	}

	// Actions
	async function fetchTodayStatus(employeeId) {
		if (!employeeId) return;
		const result = await todayStatusResource.fetch({ employee_id: employeeId });
		syncTimerFromStatus();
		return result;
	}

	async function fetchRoster(employeeId) {
		if (!employeeId) return;
		return rosterResource.fetch({ employee_id: employeeId });
	}

	async function fetchHistory(employeeId, days = 30) {
		if (!employeeId) return;
		if (days && typeof days === "object") {
			await historyResource.fetch({ employee_id: employeeId, ...days });
		} else {
			await historyResource.fetch({ employee_id: employeeId, days });
		}
	}

	async function clockIn(employeeId, latitude = null, longitude = null, notes = null) {
		if (loading.value) return { success: false, status: todayStatus.value };
		loading.value = true;
		error.value = null;
		try {
			const result = await clockInResource.fetch({
				latitude,
				longitude,
				notes,
			});
			if (result && result.status) {
				todayStatus.value = result.status;
				syncTimerFromStatus();
				return result;
			} else if (result && result.success) {
				// Handle case where result has success but status might be named differently
				if (employeeId) {
					await fetchTodayStatus(employeeId);
				}
				return result;
			}
			return result;
		} catch (err) {
			const message = getErrorMessage(err);
			error.value = message;
			if (employeeId && message.includes("Already checked in")) {
				await fetchTodayStatus(employeeId);
				return { success: true, status: todayStatus.value, recovered: true };
			}
			throw err;
		} finally {
			loading.value = false;
		}
	}

	async function clockOut(employeeId, latitude = null, longitude = null, notes = null) {
		if (loading.value) return { success: false, status: todayStatus.value };
		loading.value = true;
		error.value = null;
		try {
			const result = await clockOutResource.fetch({
				latitude,
				longitude,
				notes,
			});
			if (result && result.status) {
				todayStatus.value = result.status;
				syncTimerFromStatus();
				return result;
			} else if (result && result.success) {
				// Handle case where result has success but status might be named differently
				if (employeeId) {
					await fetchTodayStatus(employeeId);
				}
				return result;
			}
			return result;
		} catch (err) {
			const message = getErrorMessage(err);
			error.value = message;
			if (
				employeeId &&
				(message.includes("No active check-in found") ||
					message.includes("Already checked out"))
			) {
				await fetchTodayStatus(employeeId);
				return { success: true, status: todayStatus.value, recovered: true };
			}
			throw err;
		} finally {
			loading.value = false;
		}
	}

	async function init(empId) {
		if (empId) {
			employeeId.value = empId;
			await Promise.all([fetchTodayStatus(empId), fetchRoster(empId)]);
		}
	}

	async function startBreak() {
		if (loading.value) return { success: false, status: todayStatus.value };
		loading.value = true;
		error.value = null;
		try {
			const result = await breakStartResource.fetch({
				notes: "Break Start",
			});
			if (result && result.status) {
				todayStatus.value = result.status;
				syncTimerFromStatus();
			}
			return result;
		} catch (err) {
			error.value = getErrorMessage(err);
			throw err;
		} finally {
			loading.value = false;
		}
	}

	async function endBreak() {
		if (loading.value) return { success: false, status: todayStatus.value };
		loading.value = true;
		error.value = null;
		try {
			const result = await breakEndResource.fetch({
				notes: "Break End",
			});
			if (result && result.status) {
				todayStatus.value = result.status;
				syncTimerFromStatus();
			}
			return result;
		} catch (err) {
			error.value = getErrorMessage(err);
			throw err;
		} finally {
			loading.value = false;
		}
	}

	async function fetchEmployeeList() {
		return employeeListResource.fetch();
	}

	async function fetchMonthlyRoster(employeeId, year, month) {
		if (employeeId) {
			return monthlyRosterResource.fetch({ employee_id: employeeId, year, month });
		}
	}

	async function checkCanMarkAttendance() {
		const result = await canMarkAttendanceResource.fetch();
		return result || false;
	}

	async function checkCanManageAttendance() {
		const result = await canManageAttendanceResource.fetch();
		return result || false;
	}

	async function checkCanViewAttendance() {
		const result = await canViewAttendanceResource.fetch();
		return result || false;
	}

	async function markAttendance(empId, date, status) {
		return markAttendanceResource.fetch({ employee_id: empId, date, status });
	}

	return {
		todayStatus,
		roster,
		history,
		loading,
		error,
		workedSecondsToday,
		employeeId,
		isCheckedIn,
		isOnBreak,
		totalHoursToday,
		totalSecondsToday,
		overtimeHours,
		workingHoursTarget,
		shiftComplete,
		canManageBreak,
		timerLabel,
		formattedWorkedTime,
		employeeList,
		monthlyRoster,
		fetchTodayStatus,
		fetchRoster,
		fetchHistory,
		fetchEmployeeList,
		fetchMonthlyRoster,
		checkCanMarkAttendance,
		checkCanManageAttendance,
		checkCanViewAttendance,
		markAttendance,
		clockIn,
		clockOut,
		startBreak,
		endBreak,
		init,
		syncTimerFromStatus,
	};
});
