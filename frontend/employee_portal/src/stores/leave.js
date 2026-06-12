import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, computed } from "vue";

export const useLeaveStore = defineStore("leave", () => {
	const leaveBalances = ref([]);
	const leaveApplications = ref([]);
	const leaveTypes = ref([]);
	const loading = ref(false);
	const employeeId = ref(null);
	const isApprover = ref(false);
	const isGlobalApprover = ref(false);
	const preventSelfApproval = ref(false);
	const approvedEmployeeList = ref([]);

	// Get leave balance map from HRMS
	const leaveBalanceResource = createResource({
		url: "hrms.api.get_leave_balance_map",
		auto: false,
		onSuccess(data) {
			if (data) {
				leaveBalances.value = Object.entries(data).map(([key, value]) => ({
					leave_type: key,
					...value,
				}));
			}
		},
	});

	// Get leave applications from HRMS
	const leaveApplicationsResource = createResource({
		url: "hrms.api.get_leave_applications",
		auto: false,
		onSuccess(data) {
			leaveApplications.value = data || [];
		},
	});

	const leaveApplicationsForAllResource = createResource({
		url: "zevar_core.api.leave.get_leave_applications_for_all",
		auto: false,
		onSuccess(data) {
			leaveApplications.value = data || [];
		},
	});

	// Get leave types from HRMS
	const leaveTypesResource = createResource({
		url: "hrms.api.get_leave_types",
		auto: false,
		onSuccess(data) {
			 if (data && Array.isArray(data)) { 
				 leaveTypes.value = data.map((name) => ({ 
					 name: name,      
					 leave_type_name: name,   
					 }));   
			 } else {  
				leaveTypes.value = [];   
				  } 
		},

	});

	// Check if current user is a leave approver
	const approverCheckResource = createResource({
		url: "zevar_core.api.leave.is_user_leave_approver",
		auto: false,
		onSuccess(data) {
			if (data && data.is_approver) {
				isApprover.value = true;
				isGlobalApprover.value = !!data.is_global_approver;
				preventSelfApproval.value = !!data.prevent_self_leave_approval;
				approvedEmployeeList.value = data.employees || [];
			} else {
				isApprover.value = false;
				isGlobalApprover.value = false;
				preventSelfApproval.value = false;
				approvedEmployeeList.value = [];
			}
		},
		onError(err) {
			console.error("Approver check failed:", err);
			isApprover.value = false;
			isGlobalApprover.value = false;
			preventSelfApproval.value = false;
			approvedEmployeeList.value = [];
		},
	});

	// Computed
	const totalLeaveBalance = computed(() => {
		return leaveBalances.value.reduce((sum, lb) => sum + (lb.balance_leaves || 0), 0);
	});

	const pendingApplications = computed(() => {
		return leaveApplications.value.filter(
			(app) => app.status === "Open" || app.status === "Pending"
		);
	});

	const approvedApplications = computed(() => {
		return leaveApplications.value.filter((app) => app.status === "Approved");
	});

	// Actions
	async function fetchLeaveBalances() {
		await leaveBalanceResource.fetch();
	}

	async function fetchLeaveApplications(emp_id = null, for_approval = false, approver_id = null) {
		const targetEmployee = emp_id === null ? employeeId.value : emp_id;
		const params = {};
		if (targetEmployee) {
			params.employee = targetEmployee;
		}
		if (for_approval) {
			params.for_approval = true;
			if (approver_id) {
				params.approver_id = approver_id;
			}
		}
		await leaveApplicationsResource.fetch(params);
	}

	async function fetchLeaveApplicationsForAll() {
		await leaveApplicationsForAllResource.fetch();
	}

	async function fetchLeaveTypes(emp_id = null) {
		const targetEmployee = emp_id || employeeId.value;
		if (!targetEmployee) return;
		const today = new Date().toISOString().split("T")[0];
		await leaveTypesResource.fetch({ employee: targetEmployee, date: today });
	}

	async function checkApproverStatus() {
		await approverCheckResource.fetch();
	}

	function init(empId) {
		employeeId.value = empId;
		fetchLeaveBalances();
		fetchLeaveApplications();
		fetchLeaveTypes();
		checkApproverStatus();
	}

	return {
		leaveBalances,
		leaveApplications,
		leaveTypes,
		loading,
		isApprover,
		isGlobalApprover,
		preventSelfApproval,
		approvedEmployeeList,
		totalLeaveBalance,
		pendingApplications,
		approvedApplications,
		fetchLeaveBalances,
		fetchLeaveApplications,
		fetchLeaveApplicationsForAll,
		fetchLeaveTypes,
		checkApproverStatus,
		init,
	};
});
