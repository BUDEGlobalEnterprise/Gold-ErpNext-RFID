import { defineStore } from "pinia";
import { createResource } from "frappe-ui";
import { ref, computed } from "vue";

export const useRosterStore = defineStore("roster", () => {
	const weeklySchedule = ref([]);
	const weeklySummary = ref(null);
	const loading = ref(false);
	const error = ref(null);
	const currentWeekStart = ref(null); // "YYYY-MM-DD"

	// Monthly view state
	const monthlyCalendar = ref([]);
	const monthlyLoading = ref(false);
	const monthlyYear = ref(new Date().getFullYear());
	const monthlyMonth = ref(new Date().getMonth()); // 0-indexed

	const weeklyRosterResource = createResource({
		url: "zevar_core.api.roster.get_weekly_roster",
		auto: false,
		onSuccess(data) {
			weeklySchedule.value = data?.schedule ?? [];
			weeklySummary.value = data?.summary || null;
		},
		onError(err) {
			console.error("Weekly roster fetch error:", err);
			error.value = err;
		},
	});

	const monthlyRosterResource = createResource({
		url: "zevar_core.api.roster.get_monthly_roster",
		auto: false,
		onSuccess(data) {
			monthlyCalendar.value = data?.calendar ?? [];
		},
		onError(err) {
			console.error("Monthly roster fetch error:", err);
		},
	});

	// Shift Request state
	const shiftRequests = ref([]);
	const shiftRequestLoading = ref(false);
	const approverInfo = ref(null); // { name, message }
	const showRequestModal = ref(false);
	const editingRequestId = ref(null);
	const shiftTypes = ref([]);
	const submissionError = ref(null);
	const submitting = ref(false);
	const cancelingId = ref(null);

	// Add Roster state
	const showAddRosterModal = ref(false);
	const addRosterSubmitting = ref(false);
	const addRosterError = ref(null);
	const currentEmployeeId = ref(null);
	const addRosterForm = ref({
		employee: "",
		shift_type: "",
		start_date: "",
		end_date: "",
		shift_location: "",
	});

	// Employee and shift location dropdowns for Add Roster
	const addRosterEmployees = ref([]);
	const shiftLocations = ref([]);

	const shiftRequestsResource = createResource({
		url: "zevar_core.api.roster.get_shift_requests",
		auto: false,
		onSuccess(data) {
			shiftRequests.value = data ?? [];
		},
		onError(err) {
			console.error("Shift requests fetch error:", err);
		},
	});

	const createRequestResource = createResource({
		url: "zevar_core.api.roster.create_shift_request",
		onSuccess() {
			shiftRequestsResource.fetch();
		},
	});

	const updateRequestResource = createResource({
		url: "zevar_core.api.roster.update_shift_request",
		onSuccess() {
			shiftRequestsResource.fetch();
		},
	});

	const cancelRequestResource = createResource({
		url: "zevar_core.api.roster.cancel_shift_request",
		onSuccess() {
			shiftRequestsResource.fetch();
		},
	});

	const updateRequestStatusResource = createResource({
		url: "zevar_core.api.roster.update_shift_request_status",
		onSuccess() {
			shiftRequestsResource.fetch();
		},
	});

	const approverResource = createResource({
		url: "hrms.api.get_shift_request_approvers",
		auto: false,
		onSuccess(data) {
			if (data && data.length > 0) {
				approverInfo.value = { name: data[0].full_name, user: data[0].name };
			} else {
				approverInfo.value = null;
			}
		},
	});

	const shiftTypesResource = createResource({
		url: "zevar_core.api.roster.get_shift_types",
		auto: false,
		onSuccess(data) {
			shiftTypes.value = data ?? [];
		},
		onError(err) {
			console.error("Shift types fetch error:", err);
		},
	});

	// Add Roster permission check
	const canAddRosterResource = createResource({
		url: "zevar_core.api.roster.can_add_roster",
		auto: false,
	});

	// Delete Roster permission check
	const canDeleteRosterResource = createResource({
		url: "zevar_core.api.roster.can_delete_roster",
		auto: false,
	});


	const isShiftApproverResource = createResource({
		url: "zevar_core.api.roster.is_shift_approver",
		auto: false,
	});

	const allowMultipleShiftsResource = createResource({
		url: "zevar_core.api.roster.allow_multiple_shifts",
		auto: false,
	});

	// Shift locations resource for Add Roster dropdown
	const shiftLocationsResource = createResource({
		url: "zevar_core.api.roster.get_shift_locations",
		auto: false,
		onSuccess(data) {
			shiftLocations.value = data ?? [];
		},
		onError(err) {
			console.error("Shift locations fetch error:", err);
		},
	});

	// Employee list resource for Add Roster dropdown
	const employeeListResource = createResource({
		url: "zevar_core.api.roster.get_employee_list",
		auto: false,
		onSuccess(data) {
			addRosterEmployees.value = data ?? [];
		},
		onError(err) {
			console.error("Employee list fetch error:", err);
		},
	});

	const addRosterResource = createResource({
		url: "zevar_core.api.roster.add_roster",
		onSuccess() {
			// Refresh shift requests and weekly roster after adding
			if (currentEmployeeId.value) {
				fetchShiftRequests(currentEmployeeId.value);
				if (currentWeekStart.value) {
					fetchWeekly(currentEmployeeId.value, currentWeekStart.value);
				}
			}
		},
	});

	const deleteRosterResource = createResource({
		url: "zevar_core.api.roster.delete_roster",
		onSuccess() {
			// Refresh shift requests and weekly roster after deleting
			if (currentEmployeeId.value) {
				fetchShiftRequests(currentEmployeeId.value);
				if (currentWeekStart.value) {
					fetchWeekly(currentEmployeeId.value, currentWeekStart.value);
				}
				fetchMonthly(currentEmployeeId.value, monthlyYear.value, monthlyMonth.value);
			}
		},
	});


	// Computed stats
	const workingDays = computed(() => weeklySummary.value?.total_working_days ?? 0);
	const hoursWorked = computed(() => Number(weeklySummary.value?.total_hours ?? 0));
	const targetHours = computed(() => Number(weeklySummary.value?.target_hours ?? 0));
	const remainingHours = computed(
		() => Math.max(0, Number((targetHours.value - hoursWorked.value).toFixed(1)))
	);

	// Actions
	async function fetchWeekly(employeeId, weekStartStr) {
		if (!employeeId) return;
		loading.value = true;
		error.value = null;
		try {
			await weeklyRosterResource.fetch({
				employee_id: employeeId,
				start_date: weekStartStr,
			});
			currentWeekStart.value = weekStartStr;
		} finally {
			loading.value = false;
		}
	}

	async function fetchMonthly(employeeId, year, month) {
		if (!employeeId) return;
		monthlyLoading.value = true;
		try {
			await monthlyRosterResource.fetch({
				employee_id: employeeId,
				year: year,
				month: month,
			});
			monthlyYear.value = year;
			monthlyMonth.value = month;
		} finally {
			monthlyLoading.value = false;
		}
	}

	async function fetchShiftRequests(employeeId) {
		if (!employeeId) return;
		shiftRequestLoading.value = true;
		try {
			await shiftRequestsResource.fetch({ employee_id: employeeId });
		} finally {
			shiftRequestLoading.value = false;
		}
	}

	async function fetchApprover(employeeId) {
		if (!employeeId) {
			approverInfo.value = null;
			return;
		}
		try {
			await approverResource.fetch({ employee: employeeId });
		} catch {
			approverInfo.value = null;
		}
	}

	async function fetchShiftTypes() {
		try {
			await shiftTypesResource.fetch();
		} catch {
			shiftTypes.value = [];
		}
	}

	async function fetchShiftLocations() {
		try {
			await shiftLocationsResource.fetch();
		} catch {
			shiftLocations.value = [];
		}
	}

	async function fetchAddRosterEmployees() {
		try {
			await employeeListResource.fetch();
		} catch {
			addRosterEmployees.value = [];
		}
	}

	async function checkCanAddRoster() {
		await canAddRosterResource.fetch();
		return canAddRosterResource.data;
	}

	async function checkCanDeleteRoster() {
		await canDeleteRosterResource.fetch();
		return canDeleteRosterResource.data;
	}


	async function checkIsShiftApprover() {
		await isShiftApproverResource.fetch();
		return isShiftApproverResource.data;
	}

	async function checkAllowMultipleShifts() {
		await allowMultipleShiftsResource.fetch();
		return allowMultipleShiftsResource.data;
	}

	async function openRequestModal(editId = null) {
		editingRequestId.value = editId;
		showRequestModal.value = true;
		submissionError.value = null;
	}

	async function closeRequestModal() {
		showRequestModal.value = false;
		editingRequestId.value = null;
		submissionError.value = null;
	}

	// Add Roster actions
	async function openAddRosterModal(employeeId) {
		currentEmployeeId.value = employeeId;
		addRosterForm.value = {
			employee: employeeId,
			shift_type: "",
			start_date: "",
			end_date: "",
			shift_location: "",
		};
		showAddRosterModal.value = true;
		addRosterError.value = null;
		// Fetch dropdown data
		if (shiftTypes.value.length === 0) {
			await fetchShiftTypes();
		}
		if (shiftLocations.value.length === 0) {
			await fetchShiftLocations();
		}
		if (addRosterEmployees.value.length === 0) {
			await fetchAddRosterEmployees();
		}
	}

	function closeAddRosterModal() {
		showAddRosterModal.value = false;
		addRosterForm.value = { employee: "", shift_type: "", start_date: "", end_date: "", shift_location: "" };
		addRosterError.value = null;
	}

	async function submitAddRoster(formData) {
		addRosterError.value = null;
		addRosterSubmitting.value = true;
		try {
			let result = await addRosterResource.submit({
				employee: formData.employee,
				shift_type: formData.shift_type,
				start_date: formData.start_date,
				end_date: formData.end_date || null,
				shift_location: formData.shift_location || null,
			});
			if (result && result.success === false) {
				addRosterError.value = result.message;
				return;
			}
			closeAddRosterModal();
		} catch (err) {
			if (err && err._server_messages) {
				try {
					const msgs = JSON.parse(err._server_messages);
					if (msgs && msgs.length > 0) {
						addRosterError.value = msgs[0].replace(/<[^>]*>/g, "").trim();
						return;
					}
				} catch {}
			}
			if (err && err.exc && typeof err.exc === "string") {
				const lines = err.exc.trim().split('\n');
				const lastLine = lines[lines.length - 1].trim();
				if (lastLine) {
					const parts = lastLine.split(': ');
					addRosterError.value = parts.length > 1 ? parts[1] : lastLine;
				} else {
					addRosterError.value = "Failed to create shift assignment";
				}
			} else if (err && err.message) {
				addRosterError.value = err.message;
			} else {
				addRosterError.value = "Failed to create shift assignment";
			}
		} finally {
			addRosterSubmitting.value = false;
		}
	}

	async function deleteRoster(assignmentName) {
		try {
			let result = await deleteRosterResource.submit({ assignment_name: assignmentName });
			if (result && result.success === false) {
				return { success: false, message: result.message };
			}
			return { success: true };
		} catch (err) {
			console.error("Delete roster assignment error:", err);
			let errMsg = "Failed to delete roster assignment";
			if (err && err._server_messages) {
				try {
					const msgs = JSON.parse(err._server_messages);
					if (msgs && msgs.length > 0) {
						errMsg = msgs[0].replace(/<[^>]*>/g, "").trim();
					}
				} catch {}
			} else if (err && err.message) {
				errMsg = err.message;
			}
			return { success: false, message: errMsg };
		}
	}


	async function submitRequest(data) {
		submissionError.value = null;
		submitting.value = true;
		try {
			let result;
			if (editingRequestId.value) {
				result = await updateRequestResource.submit({
					name: editingRequestId.value,
					shift_type: data.shift_type,
					from_date: data.from_date,
					to_date: data.to_date || null,
				});
			} else {
				result = await createRequestResource.submit(data);
			}
			// Backend may return {success: false, message: ...} for validation errors
			if (result && result.success === false) {
				submissionError.value = result.message;
				return;
			}
			closeRequestModal();
		} catch (err) {
			// Backend _server_messages (clean messages from frappe.throw / DocType validation)
			if (err && err._server_messages) {
				try {
					const msgs = JSON.parse(err._server_messages);
					if (msgs && msgs.length > 0) {
						// Strip HTML tags from server message
						submissionError.value = msgs[0].replace(/<[^>]*>/g, "").trim();
						return;
					}
				} catch {}
			}
			// frappe 500 errors: err.exc has the raw traceback, clean message is the last line
			if (err && err.exc && typeof err.exc === "string") {
				const lines = err.exc.trim().split('\n');
				const lastLine = lines[lines.length - 1].trim();
				// "OverlappingShiftRequestError: ..." or "msgprint: ..." — extract the message
				if (lastLine) {
					const parts = lastLine.split(': ');
					submissionError.value = parts.length > 1 ? parts[1] : lastLine;
				} else {
					submissionError.value = "Failed to submit request";
				}
			} else if (err && err.message) {
				submissionError.value = err.message;
			} else if (err && typeof err === "string") {
				submissionError.value = err;
			} else {
				submissionError.value = "Failed to submit request";
			}
		} finally {
			submitting.value = false;
		}
	}

	async function handleCancelRequest(name) {
		if (confirm("Cancel this shift request?")) {
			cancelingId.value = name;
			try {
				await cancelRequestResource.submit({ name });
			} finally {
				cancelingId.value = null;
			}
		}
	}

	async function updateRequestStatus(name, status) {
		try {
			await updateRequestStatusResource.submit({ name, status });
		} catch (err) {
			console.error("Failed to update request status:", err);
			throw err;
		}
	}

	return {
		weeklySchedule,
		weeklySummary,
		loading,
		error,
		currentWeekStart,
		workingDays,
		hoursWorked,
		targetHours,
		remainingHours,
		fetchWeekly,

		// Monthly view
		monthlyCalendar,
		monthlyLoading,
		monthlyYear,
		monthlyMonth,
		fetchMonthly,

		// Shift request state
		shiftRequests,
		shiftRequestLoading,
		approverInfo,
		showRequestModal,
		editingRequestId,
		shiftTypes,
		submissionError,
		submitting,
		cancelingId,
		fetchShiftRequests,
		fetchApprover,
		fetchShiftTypes,
		checkCanAddRoster,
		checkIsShiftApprover,
		checkAllowMultipleShifts,
		openRequestModal,
		closeRequestModal,
		submitRequest,
		handleCancelRequest,
		updateRequestStatus,

		// Add Roster state
		showAddRosterModal,
		addRosterSubmitting,
		addRosterError,
		addRosterForm,
		addRosterEmployees,
		shiftLocations,
		openAddRosterModal,
		closeAddRosterModal,
		submitAddRoster,
		deleteRoster,
		fetchShiftLocations,
		fetchAddRosterEmployees,
		checkCanDeleteRoster,
	};
});
