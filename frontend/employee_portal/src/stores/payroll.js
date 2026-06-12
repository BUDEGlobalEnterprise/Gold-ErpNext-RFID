import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, computed } from "vue";

export const usePayrollStore = defineStore("payroll", () => {
	const salarySlips = ref([]);
	const payrollSummary = ref(null);
	const myPayrollSummary = ref(null);
	const loading = ref(false);
	const selectedEmployeeId = ref(null);
	const employeeList = ref([]);

	// Get salary slips from HRMS via zevar_core API
	const salarySlipsResource = createResource({
		url: "zevar_core.api.payroll.get_salary_slips",
		auto: false,
		onSuccess(data) {
			salarySlips.value = data || [];
		},
	});

	// Get payroll summary
	const payrollSummaryResource = createResource({
		url: "zevar_core.api.payroll.get_payroll_summary",
		auto: false,
		onSuccess(data) {
			payrollSummary.value = data;
		},
	});

	// Get my payroll summary
	const myPayrollSummaryResource = createResource({
		url: "zevar_core.api.payroll.get_payroll_summary",
		auto: false,
		onSuccess(data) {
			myPayrollSummary.value = data;
		},
	});

	// Get salary slip details
	const salarySlipDetailsResource = createResource({
		url: "zevar_core.api.payroll.get_salary_slip_details",
		auto: false,
	});

	// Generate salary slip
	const generateMyPayslipResource = createResource({
		url: "zevar_core.api.payroll.generate_my_payslip",
		auto: false,
	});

	// Permission check
	const canViewAllResource = createResource({
		url: "zevar_core.api.payroll.can_view_all_payroll",
		auto: false,
	});

	// Employee list (secure core method)
	const employeeListResource = createResource({
		url: "zevar_core.api.payroll.get_employee_list",
		auto: false,
		onSuccess(data) {
			employeeList.value = data || [];
		},
	});

	// Computed
	const latestSalarySlip = computed(() => {
		if (!salarySlips.value || salarySlips.value.length === 0) return null;
		return salarySlips.value[0];
	});

	const totalYTD = computed(() => {
		return payrollSummary.value?.total_net_pay || 0;
	});

	const totalEarningsYTD = computed(() => {
		return payrollSummary.value?.total_earnings || 0;
	});

	const totalDeductionsYTD = computed(() => {
		return payrollSummary.value?.total_deductions || 0;
	});

	const myTotalYTD = computed(() => {
		return myPayrollSummary.value?.total_net_pay || 0;
	});

	const myTotalEarningsYTD = computed(() => {
		return myPayrollSummary.value?.total_earnings || 0;
	});

	const myTotalDeductionsYTD = computed(() => {
		return myPayrollSummary.value?.total_deductions || 0;
	});

	const canViewAll = computed(() => {
		return canViewAllResource.data || false;
	});

	// Actions
	async function fetchSalarySlips(params = {}) {
		if (selectedEmployeeId.value) params.employee_id = selectedEmployeeId.value;
		await salarySlipsResource.fetch(params);
	}

	async function fetchPayrollSummary(params = {}) {
		if (selectedEmployeeId.value) params.employee_id = selectedEmployeeId.value;
		await payrollSummaryResource.fetch(params);
	}

	async function fetchMyPayrollSummary(params = {}) {
		await myPayrollSummaryResource.fetch(params);
	}

	async function fetchEmployeeList() {
		await employeeListResource.fetch();
	}

	async function getSlipDetails(slipName) {
		return await salarySlipDetailsResource.fetch({ slip_name: slipName });
	}

	async function generateMyPayslip(month, year) {
		return await generateMyPayslipResource.fetch({ month, year });
	}

	async function checkPermissions() {
		await canViewAllResource.fetch();
	}

	async function init(params = {}) {
		await checkPermissions();
		fetchSalarySlips(params);
		fetchPayrollSummary(params);
	}

	return {
		salarySlips,
		payrollSummary,
		myPayrollSummary,
		loading,
		selectedEmployeeId,
		employeeList,
		latestSalarySlip,
		totalYTD,
		totalEarningsYTD,
		totalDeductionsYTD,
		myTotalYTD,
		myTotalEarningsYTD,
		myTotalDeductionsYTD,
		canViewAll,
		fetchSalarySlips,
		fetchPayrollSummary,
		fetchMyPayrollSummary,
		fetchEmployeeList,
		getSlipDetails,
		generateMyPayslip,
		checkPermissions,
		init,
	};
});
