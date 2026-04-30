<template>
	<div
		class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800"
	>
		<div class="max-w-7xl mx-auto p-6 space-y-6">
			<div
				class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
			>
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white">Reports</h1>
					<p class="text-gray-600 dark:text-gray-400 mt-1">
						Your attendance, leave, payroll, expenses, and tasks
					</p>
				</div>
				<div class="flex gap-3">
					<button @click="refreshData" class="btn btn-secondary" :disabled="loading">
						<span
							class="material-symbols-outlined"
							:class="{ 'animate-spin': loading }"
							>refresh</span
						>
						Refresh
					</button>
				</div>
			</div>

			<!-- Report Type Tabs -->
			<div class="flex flex-wrap gap-2">
				<button
					v-for="tab in reportTabs"
					:key="tab.id"
					@click="activeTab = tab.id"
					class="tab-btn"
					:class="{ 'tab-btn--active': activeTab === tab.id }"
				>
					<span class="material-symbols-outlined">{{ tab.icon }}</span>
					{{ tab.label }}
				</button>
			</div>

			<!-- Loading -->
			<div v-if="loading" class="flex items-center justify-center py-20">
				<div
					class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-emerald-600"
				></div>
			</div>

			<template v-else>
				<!-- Summary Cards -->
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div
						v-for="card in currentSummary"
						:key="card.id"
						class="bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-gray-200 dark:border-slate-700"
					>
						<div class="flex items-center justify-between">
							<div>
								<p class="text-sm text-gray-600 dark:text-gray-400">
									{{ card.label }}
								</p>
								<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
									{{ card.value }}
								</p>
							</div>
							<div :class="`summary-icon summary-icon--${card.variant}`">
								<span class="material-symbols-outlined">{{ card.icon }}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Data Table -->
				<div
					class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-700 overflow-hidden"
				>
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead class="bg-gray-50 dark:bg-slate-700">
								<tr>
									<th
										v-for="column in currentColumns"
										:key="column.key"
										class="table-header"
									>
										{{ column.label }}
									</th>
								</tr>
							</thead>
							<tbody>
								<tr v-if="tableData.length === 0">
									<td
										:colspan="currentColumns.length"
										class="text-center py-12 text-gray-500"
									>
										No data found for this period
									</td>
								</tr>
								<tr
									v-else
									v-for="row in tableData"
									:key="row.id"
									class="table-row"
								>
									<td
										v-for="column in currentColumns"
										:key="column.key"
										class="table-cell"
									>
										<span
											v-if="column.key === 'status'"
											class="px-2 py-0.5 rounded-full text-xs font-bold"
											:class="statusBadgeClass(row[column.key])"
										>
											{{ row[column.key] }}
										</span>
										<span v-else>{{ row[column.key] }}</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</template>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";

const activeTab = ref("attendance");
const loading = ref(false);
const tableData = ref([]);
const attendanceSummary = ref({});
const leaveSummary = ref({});
const expenseSummary = ref({});
const taskSummary = ref({});
const payrollSummary = ref({});

const reportTabs = [
	{ id: "attendance", label: "Attendance", icon: "present_to_all" },
	{ id: "leave", label: "Leave", icon: "event_available" },
	{ id: "payroll", label: "Payroll", icon: "payments" },
	{ id: "expenses", label: "Expenses", icon: "receipt_long" },
	{ id: "tasks", label: "Tasks", icon: "assignment" },
];

async function frappeCall(method, args = {}) {
	const response = await fetch("/api/method/" + method, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-Frappe-CSRF-Token": window.csrf_token || "",
		},
		body: JSON.stringify(args),
	});
	const data = await response.json();
	if (data.exc) throw new Error(data.exc);
	return data.message;
}

const currentColumns = computed(() => {
	const cols = {
		attendance: [
			{ key: "date", label: "Date" },
			{ key: "checkIn", label: "Check In" },
			{ key: "checkOut", label: "Check Out" },
			{ key: "hours", label: "Hours" },
			{ key: "status", label: "Status" },
		],
		leave: [
			{ key: "type", label: "Leave Type" },
			{ key: "fromDate", label: "From" },
			{ key: "toDate", label: "To" },
			{ key: "days", label: "Days" },
			{ key: "status", label: "Status" },
		],
		payroll: [
			{ key: "month", label: "Month" },
			{ key: "grossPay", label: "Gross Pay" },
			{ key: "deductions", label: "Deductions" },
			{ key: "netPay", label: "Net Pay" },
			{ key: "status", label: "Status" },
		],
		expenses: [
			{ key: "type", label: "Expense Type" },
			{ key: "date", label: "Date" },
			{ key: "amount", label: "Amount" },
			{ key: "status", label: "Status" },
		],
		tasks: [
			{ key: "title", label: "Task" },
			{ key: "dueDate", label: "Due Date" },
			{ key: "priority", label: "Priority" },
			{ key: "status", label: "Status" },
		],
	};
	return cols[activeTab.value] || [];
});

const currentSummary = computed(() => {
	const s = {
		attendance: [
			{
				id: "total",
				label: "Total Days",
				value: attendanceSummary.value.total_days || 0,
				icon: "calendar_month",
				variant: "primary",
			},
			{
				id: "present",
				label: "Present",
				value: attendanceSummary.value.present_days || 0,
				icon: "check_circle",
				variant: "success",
			},
			{
				id: "absent",
				label: "Absent",
				value: attendanceSummary.value.absent_days || 0,
				icon: "cancel",
				variant: "danger",
			},
			{
				id: "rate",
				label: "Attendance Rate",
				value: (attendanceSummary.value.rate || "0") + "%",
				icon: "trending_up",
				variant: "info",
			},
		],
		leave: [
			{
				id: "total",
				label: "Total Requests",
				value: leaveSummary.value.total || 0,
				icon: "mail",
				variant: "primary",
			},
			{
				id: "approved",
				label: "Approved",
				value: leaveSummary.value.approved || 0,
				icon: "check_circle",
				variant: "success",
			},
			{
				id: "pending",
				label: "Pending",
				value: leaveSummary.value.pending || 0,
				icon: "schedule",
				variant: "warning",
			},
			{
				id: "rejected",
				label: "Rejected",
				value: leaveSummary.value.rejected || 0,
				icon: "cancel",
				variant: "danger",
			},
		],
		payroll: [
			{
				id: "total",
				label: "Total Paid",
				value: "$" + (payrollSummary.value.total_paid || "0.00"),
				icon: "payments",
				variant: "success",
			},
			{
				id: "pending",
				label: "Pending",
				value: payrollSummary.value.pending_count || 0,
				icon: "schedule",
				variant: "warning",
			},
			{
				id: "avg",
				label: "Avg Net Pay",
				value: "$" + (payrollSummary.value.avg_net || "0.00"),
				icon: "account_balance_wallet",
				variant: "info",
			},
			{
				id: "slips",
				label: "Total Slips",
				value: payrollSummary.value.total_slips || 0,
				icon: "receipt",
				variant: "primary",
			},
		],
		expenses: [
			{
				id: "total",
				label: "Total Claimed",
				value: "$" + (expenseSummary.value.total || "0.00"),
				icon: "receipt_long",
				variant: "primary",
			},
			{
				id: "approved",
				label: "Approved",
				value: "$" + (expenseSummary.value.approved || "0.00"),
				icon: "check_circle",
				variant: "success",
			},
			{
				id: "pending",
				label: "Pending",
				value: "$" + (expenseSummary.value.pending || "0.00"),
				icon: "schedule",
				variant: "warning",
			},
			{
				id: "rejected",
				label: "Rejected",
				value: "$" + (expenseSummary.value.rejected || "0.00"),
				icon: "cancel",
				variant: "danger",
			},
		],
		tasks: [
			{
				id: "total",
				label: "Total Tasks",
				value: taskSummary.value.total || 0,
				icon: "assignment",
				variant: "primary",
			},
			{
				id: "completed",
				label: "Completed",
				value: taskSummary.value.completed || 0,
				icon: "check_circle",
				variant: "success",
			},
			{
				id: "progress",
				label: "In Progress",
				value: taskSummary.value.in_progress || 0,
				icon: "pending",
				variant: "warning",
			},
			{
				id: "overdue",
				label: "Overdue",
				value: taskSummary.value.overdue || 0,
				icon: "alarm",
				variant: "danger",
			},
		],
	};
	return s[activeTab.value] || [];
});

function statusBadgeClass(status) {
	const map = {
		Present: "bg-green-100 text-green-700",
		Absent: "bg-red-100 text-red-700",
		Late: "bg-yellow-100 text-yellow-700",
		"Half Day": "bg-orange-100 text-orange-700",
		Approved: "bg-green-100 text-green-700",
		Pending: "bg-yellow-100 text-yellow-700",
		Rejected: "bg-red-100 text-red-700",
		Paid: "bg-green-100 text-green-700",
		Open: "bg-blue-100 text-blue-700",
		"In Progress": "bg-yellow-100 text-yellow-700",
		Completed: "bg-green-100 text-green-700",
		Overdue: "bg-red-100 text-red-700",
		Closed: "bg-gray-100 text-gray-700",
		Submitted: "bg-blue-100 text-blue-700",
		Cancelled: "bg-red-100 text-red-700",
		Draft: "bg-gray-100 text-gray-700",
	};
	return map[status] || "bg-gray-100 text-gray-600";
}

async function loadAttendance() {
	try {
		const data = await frappeCall("zevar_core.api.attendance.get_attendance_history");
		const records = data || [];
		const present = records.filter((r) => r.status === "Present").length;
		const absent = records.filter((r) => r.status === "Absent").length;
		const total = records.length;
		attendanceSummary.value = {
			total_days: total,
			present_days: present,
			absent_days: absent,
			rate: total ? Math.round((present / total) * 100) : 0,
		};
		tableData.value = records.map((r) => ({
			id: r.name,
			date: r.attendance_date || r.date,
			checkIn: r.in_time ? r.in_time.substring(0, 5) : "--",
			checkOut: r.out_time ? r.out_time.substring(0, 5) : "--",
			hours: r.working_hours ? r.working_hours + "h" : "--",
			status: r.status || "Absent",
		}));
	} catch {
		attendanceSummary.value = { total_days: 0, present_days: 0, absent_days: 0, rate: 0 };
		tableData.value = [];
	}
}

async function loadLeave() {
	try {
		const records = await frappeCall("frappe.client.get_list", {
			doctype: "Leave Application",
			fields: ["name", "leave_type", "from_date", "to_date", "total_half_days", "status"],
			limit_page_length: 50,
			order_by: "creation desc",
		});
		const data = records || [];
		leaveSummary.value = {
			total: data.length,
			approved: data.filter((r) => r.status === "Approved").length,
			pending: data.filter((r) => r.status === "Open").length,
			rejected: data.filter((r) => r.status === "Rejected").length,
		};
		tableData.value = data.map((r) => ({
			id: r.name,
			type: r.leave_type,
			fromDate: r.from_date,
			toDate: r.to_date,
			days: r.total_half_days ? (r.total_half_days / 2).toFixed(1) : "--",
			status: r.status === "Open" ? "Pending" : r.status,
		}));
	} catch {
		leaveSummary.value = { total: 0, approved: 0, pending: 0, rejected: 0 };
		tableData.value = [];
	}
}

async function loadPayroll() {
	try {
		const data = await frappeCall("zevar_core.api.payroll.get_salary_slips");
		const records = data || [];
		const paid = records.filter((r) => r.status === "Submitted" || r.docstatus === 1);
		const totalNet = paid.reduce((sum, r) => sum + (parseFloat(r.net_pay) || 0), 0);
		const pendingCount = records.filter((r) => r.docstatus === 0).length;
		payrollSummary.value = {
			total_paid: totalNet.toFixed(2),
			pending_count: pendingCount,
			avg_net: paid.length ? (totalNet / paid.length).toFixed(2) : "0.00",
			total_slips: records.length,
		};
		tableData.value = records.map((r) => ({
			id: r.name,
			month: r.month || r.start_date,
			grossPay: "$" + parseFloat(r.gross_pay || 0).toFixed(2),
			deductions: "$" + parseFloat(r.total_deduction || 0).toFixed(2),
			netPay: "$" + parseFloat(r.net_pay || 0).toFixed(2),
			status: r.docstatus === 0 ? "Draft" : r.docstatus === 1 ? "Paid" : "Cancelled",
		}));
	} catch {
		payrollSummary.value = {
			total_paid: "0.00",
			pending_count: 0,
			avg_net: "0.00",
			total_slips: 0,
		};
		tableData.value = [];
	}
}

async function loadExpenses() {
	try {
		const data = await frappeCall("zevar_core.api.expense.get_expense_claims");
		const records = data || [];
		const total = records.reduce(
			(s, r) => s + parseFloat(r.total_claimed_amount || r.amount || 0),
			0
		);
		const approved = records
			.filter((r) => r.status === "Approved" || r.docstatus === 1)
			.reduce((s, r) => s + parseFloat(r.total_claimed_amount || r.amount || 0), 0);
		const pending = records
			.filter((r) => r.status === "Draft" || r.docstatus === 0)
			.reduce((s, r) => s + parseFloat(r.total_claimed_amount || r.amount || 0), 0);
		const rejected = records
			.filter((r) => r.status === "Rejected")
			.reduce((s, r) => s + parseFloat(r.total_claimed_amount || r.amount || 0), 0);
		expenseSummary.value = {
			total: total.toFixed(2),
			approved: approved.toFixed(2),
			pending: pending.toFixed(2),
			rejected: rejected.toFixed(2),
		};
		tableData.value = records.map((r) => ({
			id: r.name,
			type: r.expense_type || r.remark || "General",
			date: r.posting_date || r.expense_date,
			amount: "$" + parseFloat(r.total_claimed_amount || r.amount || 0).toFixed(2),
			status: r.docstatus === 0 ? "Pending" : r.docstatus === 1 ? "Approved" : "Cancelled",
		}));
	} catch {
		expenseSummary.value = {
			total: "0.00",
			approved: "0.00",
			pending: "0.00",
			rejected: "0.00",
		};
		tableData.value = [];
	}
}

async function loadTasks() {
	try {
		const data = await frappeCall("zevar_core.api.tasks.get_employee_tasks");
		const records = (data && data.tasks) || data || [];
		const total = records.length;
		const completed = records.filter(
			(r) => r.status === "Completed" || r.status === "Closed"
		).length;
		const inProgress = records.filter(
			(r) => r.status === "In Progress" || r.status === "Open"
		).length;
		const overdue = records.filter((r) => r.status === "Overdue" || r.is_overdue).length;
		taskSummary.value = { total, completed, in_progress: inProgress, overdue };
		tableData.value = records.map((r) => ({
			id: r.name,
			title: r.subject || r.description || r.title || r.name,
			dueDate: r.due_date || r.date || "--",
			priority: r.priority || r.type || "Normal",
			status:
				r.status === "Completed"
					? "Completed"
					: r.status === "Open"
					? "Open"
					: r.status || "Open",
		}));
	} catch {
		taskSummary.value = { total: 0, completed: 0, in_progress: 0, overdue: 0 };
		tableData.value = [];
	}
}

async function loadTab() {
	loading.value = true;
	tableData.value = [];
	try {
		switch (activeTab.value) {
			case "attendance":
				await loadAttendance();
				break;
			case "leave":
				await loadLeave();
				break;
			case "payroll":
				await loadPayroll();
				break;
			case "expenses":
				await loadExpenses();
				break;
			case "tasks":
				await loadTasks();
				break;
		}
	} catch (e) {
		console.error("Failed to load report:", e);
	} finally {
		loading.value = false;
	}
}

async function refreshData() {
	await loadTab();
}

watch(activeTab, () => {
	loadTab();
});

onMounted(() => {
	loadTab();
});
</script>

<style scoped>
.tab-btn {
	display: inline-flex;
	align-items: center;
	gap: 0.5rem;
	padding: 0.75rem 1.25rem;
	border-radius: 0.75rem;
	font-weight: 600;
	font-size: 0.875rem;
	transition: all 0.2s;
	background: white;
	color: #6b7280;
	border: 1px solid #e5e7eb;
}
.tab-btn:hover {
	background: #f9fafb;
}
.tab-btn--active {
	background: linear-gradient(135deg, #04403a 0%, #065f46 100%);
	color: white;
	border-color: transparent;
}
.summary-icon {
	width: 48px;
	height: 48px;
	border-radius: 0.75rem;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24px;
}
.summary-icon--primary {
	background: rgba(4, 64, 58, 0.1);
	color: #04403a;
}
.summary-icon--success {
	background: rgba(16, 185, 129, 0.1);
	color: #10b981;
}
.summary-icon--danger {
	background: rgba(239, 68, 68, 0.1);
	color: #ef4444;
}
.summary-icon--warning {
	background: rgba(245, 158, 11, 0.1);
	color: #f59e0b;
}
.summary-icon--info {
	background: rgba(59, 130, 246, 0.1);
	color: #3b82f6;
}
.table-header {
	padding: 0.75rem 1.5rem;
	text-align: left;
	font-size: 0.75rem;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.05em;
	color: #6b7280;
}
.table-row {
	border-bottom: 1px solid #f3f4f6;
	transition: background 0.15s;
}
.table-row:hover {
	background: #f9fafb;
}
.table-cell {
	padding: 0.75rem 1.5rem;
	font-size: 0.875rem;
	color: #374151;
}
.btn {
	display: inline-flex;
	align-items: center;
	gap: 0.5rem;
	padding: 0.625rem 1.25rem;
	border-radius: 0.5rem;
	font-size: 0.875rem;
	font-weight: 600;
	transition: all 0.2s;
}
.btn-secondary {
	background: white;
	color: #374151;
	border: 1px solid #e5e7eb;
}
.btn-secondary:hover {
	background: #f9fafb;
}
.animate-spin {
	animation: spin 1s linear infinite;
}
@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}
</style>
