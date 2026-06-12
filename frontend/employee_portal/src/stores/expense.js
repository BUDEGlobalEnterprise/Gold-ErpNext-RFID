import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, computed } from "vue";

export const useExpenseStore = defineStore("expense", () => {
	const expenseClaims = ref([]);
	const expenseTypes = ref([]);
	const expenseSummary = ref({
		monthly_total_count: 0,
		monthly_total_amount: 0.0,
		monthly_approved_count: 0,
		monthly_approved_amount: 0.0,
		monthly_rejected_count: 0,
		monthly_rejected_amount: 0.0,
	});
	const loading = ref(false);
	const isApprover = ref(false);
	const isGlobalApprover = ref(false);
	const preventSelfApproval = ref(false);
	const approvedEmployeeList = ref([]);

	// Expense Claims
	const claimsResource = createResource({
		url: "zevar_core.api.expense.get_expense_claims",
		auto: false,
		onSuccess(data) {
			expenseClaims.value = data || [];
		},
	});

	// Expense Types
	const typesResource = createResource({
		url: "zevar_core.api.expense.get_expense_types",
		auto: false,
		onSuccess(data) {
			expenseTypes.value = data || [];
		},
	});

	// Expense Summary
	const summaryResource = createResource({
		url: "zevar_core.api.expense.get_expense_summary",
		auto: false,
		onSuccess(data) {
			expenseSummary.value = data || {
				monthly_total_count: 0,
				monthly_total_amount: 0.0,
				monthly_approved_count: 0,
				monthly_approved_amount: 0.0,
				monthly_rejected_count: 0,
				monthly_rejected_amount: 0.0,
			};
		},
	});

	// Payable Accounts
	const payableAccounts = ref([]);
	const payableAccountsResource = createResource({
		url: "zevar_core.api.expense.get_payable_accounts",
		auto: false,
		onSuccess(data) {
			payableAccounts.value = data || [];
		},
	});

	// Approvers details
	const approversData = ref(null);
	const approversResource = createResource({
		url: "zevar_core.api.expense.get_expense_approvers",
		auto: false,
		onSuccess(data) {
			approversData.value = data || null;
		},
	});

	// Company default details
	const companyDefaults = ref(null);
	const defaultsResource = createResource({
		url: "zevar_core.api.expense.get_company_defaults",
		auto: false,
		onSuccess(data) {
			companyDefaults.value = data || null;
		},
	});

	// Submit Claim Resource
	const submitClaimResource = createResource({
		url: "zevar_core.api.expense.submit_new_expense_claim",
		auto: false,
	});

	// Check if current user is an expense approver
	const approverCheckResource = createResource({
		url: "zevar_core.api.expense.is_user_expense_approver",
		auto: false,
		onSuccess(data) {
			if (data && data.is_approver) {
				isApprover.value = true;
				isGlobalApprover.value = !!data.is_global_approver;
				preventSelfApproval.value = !!data.prevent_self_expense_approval;
				approvedEmployeeList.value = data.employees || [];
			} else {
				isApprover.value = false;
				isGlobalApprover.value = false;
				preventSelfApproval.value = false;
				approvedEmployeeList.value = [];
			}
		},
		onError(err) {
			console.error("Expense Approver check failed:", err);
			isApprover.value = false;
			isGlobalApprover.value = false;
			preventSelfApproval.value = false;
			approvedEmployeeList.value = [];
		},
	});

	const claimsForAllResource = createResource({
		url: "zevar_core.api.expense.get_expense_claims_for_all",
		auto: false,
		onSuccess(data) {
			expenseClaims.value = data || [];
		},
	});

	// Actions
	async function fetchClaims(employeeId, status = "") {
		if (!employeeId) return;
		const params = { employee: employeeId };
		if (status) params.status = status;
		await claimsResource.fetch(params);
	}

	async function fetchClaimsForAll(status = "") {
		const params = {};
		if (status) params.status = status;
		await claimsForAllResource.fetch(params);
	}

	async function checkApproverStatus() {
		await approverCheckResource.fetch();
	}

	async function fetchTypes() {
		await typesResource.fetch();
	}

	async function fetchSummary(employeeId) {
		if (!employeeId) return;
		await summaryResource.fetch({ employee_id: employeeId });
	}

	async function fetchPayableAccounts(company) {
		if (!company) return;
		await payableAccountsResource.fetch({ company });
	}

	async function fetchApprovers(employeeId) {
		if (!employeeId) return;
		await approversResource.fetch({ employee: employeeId });
	}

	async function fetchCompanyDefaults(company) {
		if (!company) return;
		await defaultsResource.fetch({ company });
	}

	async function init(employeeId) {
		if (employeeId) {
			await checkApproverStatus();
			if (isApprover.value) {
				await fetchClaimsForAll();
			} else {
				await fetchClaims(employeeId);
			}
			fetchTypes();
			fetchSummary(employeeId);
		}
	}

	return {
		expenseClaims,
		expenseTypes,
		expenseSummary,
		payableAccounts,
		approversData,
		companyDefaults,
		loading,
		isApprover,
		isGlobalApprover,
		preventSelfApproval,
		approvedEmployeeList,
		claimsResource,
		typesResource,
		summaryResource,
		payableAccountsResource,
		approversResource,
		defaultsResource,
		submitClaimResource,
		claimsForAllResource,
		fetchClaims,
		fetchClaimsForAll,
		checkApproverStatus,
		fetchTypes,
		fetchSummary,
		fetchPayableAccounts,
		fetchApprovers,
		fetchCompanyDefaults,
		init,
	};
});


