import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { ref } from 'vue'

export const useHRStore = defineStore('hr', () => {
	const employee = ref(null)
	const leaveApplications = ref([])
	const leaveApplicationsTotal = ref(0)
	const leaveBalances = ref([])
	const leaveTypes = ref([])
	const attendanceCalendar = ref([])
	const calendarMonth = ref(null)
	const calendarYear = ref(null)

	const todayStatus = ref(null)
	const weeklyRoster = ref(null)
	const attendanceHistory = ref([])

	const salarySlips = ref([])
	const expenseClaims = ref([])

	const employeeProfileResource = createResource({
		url: 'zevar_core.api.hr.get_employee_profile',
		onSuccess(data) {
			employee.value = data.employee || null
		},
	})

	const leaveApplicationsResource = createResource({
		url: 'zevar_core.api.hr.get_leave_applications',
		onSuccess(data) {
			leaveApplications.value = data.applications || []
			leaveApplicationsTotal.value = data.total || 0
		},
	})

	const leaveBalanceResource = createResource({
		url: 'zevar_core.api.hr.get_leave_balance',
		onSuccess(data) {
			leaveBalances.value = data.balances || []
		},
	})

	const applyLeaveResource = createResource({
		url: 'zevar_core.api.hr.apply_leave',
	})

	const cancelLeaveResource = createResource({
		url: 'zevar_core.api.hr.cancel_leave',
	})

	const leaveTypesResource = createResource({
		url: 'zevar_core.api.hr.get_leave_types',
		onSuccess(data) {
			leaveTypes.value = data.leave_types || []
		},
	})

	const attendanceCalendarResource = createResource({
		url: 'zevar_core.api.hr.get_attendance_calendar',
		onSuccess(data) {
			attendanceCalendar.value = data.days || []
			calendarMonth.value = data.month
			calendarYear.value = data.year
		},
	})

	const checkinStatusResource = createResource({
		url: 'zevar_core.api.attendance.get_today_checkin_status',
		onSuccess(data) {
			todayStatus.value = data
		},
	})

	const clockInResource = createResource({
		url: 'zevar_core.api.attendance.clock_in',
	})

	const clockOutResource = createResource({
		url: 'zevar_core.api.attendance.clock_out',
	})

	const weeklyRosterResource = createResource({
		url: 'zevar_core.api.attendance.get_weekly_roster',
		onSuccess(data) {
			weeklyRoster.value = data
		},
	})

	const attendanceHistoryResource = createResource({
		url: 'zevar_core.api.attendance.get_attendance_history',
		onSuccess(data) {
			attendanceHistory.value = data || []
		},
	})

	const salarySlipsResource = createResource({
		url: 'zevar_core.api.payroll.get_salary_slips',
		onSuccess(data) {
			salarySlips.value = data || []
		},
	})

	const expenseClaimsResource = createResource({
		url: 'zevar_core.api.expense.get_expense_claims',
		onSuccess(data) {
			expenseClaims.value = data || []
		},
	})

	function loadProfile() {
		return employeeProfileResource.submit()
	}

	function loadLeaveApplications(params = {}) {
		return leaveApplicationsResource.submit(params)
	}

	function loadLeaveBalance() {
		return leaveBalanceResource.submit()
	}

	function applyLeave(leave_type, from_date, to_date, half_day, description) {
		return applyLeaveResource.submit({ leave_type, from_date, to_date, half_day, description })
	}

	function cancelLeave(name) {
		return cancelLeaveResource.submit({ name })
	}

	function loadLeaveTypes() {
		return leaveTypesResource.submit()
	}

	function loadAttendanceCalendar(month, year) {
		return attendanceCalendarResource.submit({ month, year })
	}

	function loadCheckinStatus() {
		return checkinStatusResource.submit({})
	}

	async function clockIn() {
		const result = await clockInResource.submit({})
		if (result?.status) todayStatus.value = result.status
		return result
	}

	async function clockOut() {
		const result = await clockOutResource.submit({})
		if (result?.status) todayStatus.value = result.status
		return result
	}

	function loadWeeklyRoster(startDate) {
		return weeklyRosterResource.submit({ start_date: startDate })
	}

	function loadAttendanceHistory(days) {
		return attendanceHistoryResource.submit({ days: days || 30 })
	}

	function loadSalarySlips(year) {
		return salarySlipsResource.submit({ year })
	}

	function loadExpenseClaims(status) {
		return expenseClaimsResource.submit({ status })
	}

	return {
		employee,
		leaveApplications,
		leaveApplicationsTotal,
		leaveBalances,
		leaveTypes,
		attendanceCalendar,
		calendarMonth,
		calendarYear,
		todayStatus,
		weeklyRoster,
		attendanceHistory,
		salarySlips,
		expenseClaims,

		employeeProfileResource,
		leaveApplicationsResource,
		leaveBalanceResource,
		applyLeaveResource,
		cancelLeaveResource,
		leaveTypesResource,
		attendanceCalendarResource,
		checkinStatusResource,
		clockInResource,
		clockOutResource,
		weeklyRosterResource,
		attendanceHistoryResource,
		salarySlipsResource,
		expenseClaimsResource,

		loadProfile,
		loadLeaveApplications,
		loadLeaveBalance,
		applyLeave,
		cancelLeave,
		loadLeaveTypes,
		loadAttendanceCalendar,
		loadCheckinStatus,
		clockIn,
		clockOut,
		loadWeeklyRoster,
		loadAttendanceHistory,
		loadSalarySlips,
		loadExpenseClaims,
	}
})
