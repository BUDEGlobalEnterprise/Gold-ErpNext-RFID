import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, computed } from "vue";
import { useEmployeeStore } from "./employee";

export const useIssuesStore = defineStore("issues", () => {
	const tickets = ref([]);
	const ticketStats = ref({ total: 0, open: 0, closed: 0, pending: 0 });
	const employeeGrievanceStats = ref({ added_this_month: 0, resolved_this_month: 0, investigated: 0, open: 0, total: 0 });
	const grievanceStatuses = ref([]);
	const grievanceTypes = ref([]);
	const grievanceEmployees = ref([]);
	const isHRManager = ref(false);
	const issueTypes = ref([]);
	const loading = ref(false);
	const usersList = ref([]);

	// Get employee tickets
	const ticketsResource = createResource({
		url: "zevar_core.api.helpdesk.get_employee_tickets",
		auto: false,
		onSuccess(data) {
			tickets.value = data || [];
		},
	});

	// Get ticket stats
	const ticketStatsResource = createResource({
		url: "zevar_core.api.helpdesk.get_ticket_stats",
		auto: false,
		onSuccess(data) {
			if (data) {
				ticketStats.value = data;
			}
		},
	});

	// Get employee grievance stats
	const employeeGrievanceStatsResource = createResource({
		url: "zevar_core.api.helpdesk.get_employee_rievance",
		auto: false,
		onSuccess(data) {
			if (data) {
				employeeGrievanceStats.value = data;
			}
		},
	});

	// Get issue types
	const issueTypesResource = createResource({
		url: "zevar_core.api.helpdesk.get_issue_types",
		auto: false,
		onSuccess(data) {
			issueTypes.value = data || [];
		},
	});

	// Get grievance statuses
	const grievanceStatusesResource = createResource({
		url: "zevar_core.api.helpdesk.get_grievance_statuses",
		auto: false,
		onSuccess(data) {
			grievanceStatuses.value = data || [];
		},
	});

	// Get grievance types
	const grievanceTypesResource = createResource({
		url: "zevar_core.api.helpdesk.get_grievance_types",
		auto: false,
		onSuccess(data) {
			grievanceTypes.value = data || [];
		},
	});

	// Create employee grievance
	const createGrievanceResource = createResource({
		url: "zevar_core.api.helpdesk.create_employee_grievance",
		auto: false,
	});

	// Delete employee grievance
	const deleteGrievanceResource = createResource({
		url: "zevar_core.api.helpdesk.delete_employee_grievance",
		auto: false,
	});

	// Investigate employee grievance
	const investigateGrievanceResource = createResource({
		url: "zevar_core.api.helpdesk.investigate_employee_grievance",
		auto: false,
	});

	// Get users list
	const usersListResource = createResource({
		url: "zevar_core.api.helpdesk.get_users_list",
		auto: false,
		onSuccess(data) {
			usersList.value = data || [];
		},
	});

	// Resolve employee grievance
	const resolveGrievanceResource = createResource({
		url: "zevar_core.api.helpdesk.resolve_employee_grievance",
		auto: false,
	});

	// Get grievance employees
	const grievanceEmployeesResource = createResource({
		url: "zevar_core.api.helpdesk.get_grievance_employees",
		auto: false,
		onSuccess(data) {
			grievanceEmployees.value = data || [];
			isHRManager.value = grievanceEmployees.value.length > 1;
		},
	});

	// Create issue
	const createIssueResource = createResource({
		url: "zevar_core.api.helpdesk.create_attendance_issue",
		auto: false,
	});

	// Computed
	const openTickets = computed(() => {
		return tickets.value.filter((t) => t.status === "Open" || t.status === "Replied");
	});

	const resolvedTickets = computed(() => {
		return tickets.value.filter((t) => t.status === "Resolved" || t.status === "Closed");
	});

	// Actions
	async function fetchTickets(filters = {}) {
		const params = {};
		if (filters.status) params.status = filters.status;
		if (filters.start_date) params.start_date = filters.start_date;
		if (filters.end_date) params.end_date = filters.end_date;
		if (filters.employee_filter) params.employee_filter = filters.employee_filter;
		await ticketsResource.fetch(params);
	}

	async function fetchTicketStats() {
		await ticketStatsResource.fetch();
	}

	async function fetchEmployeeGrievanceStats() {
		await employeeGrievanceStatsResource.fetch();
	}

	async function fetchIssueTypes() {
		await issueTypesResource.fetch();
	}

	async function fetchGrievanceStatuses() {
		await grievanceStatusesResource.fetch();
	}

	async function fetchGrievanceTypes() {
		await grievanceTypesResource.fetch();
	}

	async function fetchGrievanceAgainstOptions(doctype) {
		const employeeStore = useEmployeeStore();
		const raised_by = employeeStore.employee?.name || "";
		const resource = createResource({
			url: "zevar_core.api.helpdesk.search_link_options",
			auto: false,
		});
		return await resource.fetch({
			doctype,
			raised_by,
		});
	}

	async function createGrievance(payload) {
		loading.value = true;
		try {
			const result = await createGrievanceResource.fetch(payload);
			await fetchTickets();
			await fetchEmployeeGrievanceStats();
			return result;
		} finally {
			loading.value = false;
		}
	}

	async function createIssue(subject, description, issueType = "Other", priority = "Medium") {
		loading.value = true;
		try {
			const result = await createIssueResource.fetch({
				subject,
				description,
				issue_type: issueType,
				priority,
			});
			await fetchTickets();
			await fetchTicketStats();
			await fetchEmployeeGrievanceStats();
			return result;
		} finally {
			loading.value = false;
		}
	}

	async function fetchGrievanceEmployees() {
		await grievanceEmployeesResource.fetch();
	}

	async function deleteGrievance(name) {
		loading.value = true;
		try {
			const result = await deleteGrievanceResource.submit({ name });
			await fetchTickets();
			await fetchEmployeeGrievanceStats();
			return result;
		} finally {
			loading.value = false;
		}
	}

	async function investigateGrievance(name, causeOfGrievance) {
		loading.value = true;
		try {
			const result = await investigateGrievanceResource.submit({
				name,
				cause_of_grievance: causeOfGrievance,
			});
			await fetchTickets();
			await fetchEmployeeGrievanceStats();
			return result;
		} finally {
			loading.value = false;
		}
	}

	async function fetchUsersList() {
		await usersListResource.fetch();
	}

	async function resolveGrievance(name, resolvedBy, resolutionDate, resolutionDetail) {
		loading.value = true;
		try {
			const result = await resolveGrievanceResource.submit({
				name,
				resolved_by: resolvedBy,
				resolution_date: resolutionDate,
				resolution_detail: resolutionDetail,
			});
			await fetchTickets();
			await fetchEmployeeGrievanceStats();
			return result;
		} finally {
			loading.value = false;
		}
	}

	function init() {
		fetchTicketStats();
		fetchIssueTypes();
		fetchEmployeeGrievanceStats();
		fetchGrievanceStatuses();
		fetchGrievanceTypes();
		fetchGrievanceEmployees();
		fetchUsersList();
	}

	return {
		tickets,
		ticketStats,
		employeeGrievanceStats,
		grievanceStatuses,
		grievanceTypes,
		grievanceEmployees,
		isHRManager,
		issueTypes,
		loading,
		openTickets,
		resolvedTickets,
		usersList,
		fetchTickets,
		fetchTicketStats,
		fetchEmployeeGrievanceStats,
		fetchGrievanceStatuses,
		fetchGrievanceTypes,
		fetchGrievanceAgainstOptions,
		fetchGrievanceEmployees,
		fetchIssueTypes,
		fetchUsersList,
		createGrievance,
		createIssue,
		deleteGrievance,
		investigateGrievance,
		resolveGrievance,
		init,
	};
});
