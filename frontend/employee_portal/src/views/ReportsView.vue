<template>
	<div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
		<div class="max-w-7xl mx-auto p-6 space-y-6">
			<!-- Header -->
			<div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
				<div>
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white">Reports</h1>
					<p class="text-gray-600 dark:text-gray-400 mt-1">Generate and view detailed reports</p>
				</div>
				<div class="flex gap-3">
					<button @click="refreshData" class="btn btn-secondary" :disabled="loading">
						<span class="material-symbols-outlined" :class="{ 'animate-spin': loading }">refresh</span>
						Refresh
					</button>
					<button @click="exportData('csv')" class="btn btn-primary">
						<span class="material-symbols-outlined">download</span>
						Export CSV
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
					<span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
				</button>
			</div>

			<!-- Filters -->
			<div class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-slate-700">
				<div class="flex justify-between items-center mb-4">
					<h3 class="font-semibold text-gray-900 dark:text-white">Filters</h3>
					<button @click="clearFilters" class="text-sm text-primary hover:underline">Clear All</button>
				</div>
				<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date From</label>
						<input type="date" v-model="filters.dateFrom" class="form-input">
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date To</label>
						<input type="date" v-model="filters.dateTo" class="form-input">
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
						<select v-model="filters.status" class="form-input">
							<option value="">All Statuses</option>
							<option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Department</label>
						<select v-model="filters.department" class="form-input">
							<option value="">All Departments</option>
							<option v-for="dept in departments" :key="dept" :value="dept">{{ dept }}</option>
						</select>
					</div>
				</div>
				<div class="mt-4">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Search</label>
					<input type="text" v-model="filters.search" placeholder="Search..." class="form-input">
				</div>
			</div>

			<!-- Summary Cards -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<div
					v-for="summary in summaryData"
					:key="summary.id"
					class="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-slate-700"
				>
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm text-gray-600 dark:text-gray-400">{{ summary.label }}</p>
							<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ summary.value }}</p>
						</div>
						<div :class="`summary-icon summary-icon--${summary.variant}`">
							<span class="material-symbols-outlined">{{ summary.icon }}</span>
						</div>
					</div>
					<p class="text-sm mt-2" :class="summary.changeClass">
						{{ summary.change }}
					</p>
				</div>
			</div>

			<!-- Data Table -->
			<div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-700 overflow-hidden">
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead class="bg-gray-50 dark:bg-slate-700">
							<tr>
								<th
									v-for="column in columns"
									:key="column.key"
									class="table-header"
								>
									{{ column.label }}
								</th>
							</tr>
						</thead>
						<tbody>
							<tr v-if="loading">
								<td :colspan="columns.length" class="text-center py-12 text-gray-500">
									Loading...
								</td>
							</tr>
							<tr v-else-if="filteredData.length === 0">
								<td :colspan="columns.length" class="text-center py-12 text-gray-500">
									No data found
								</td>
							</tr>
							<tr
								v-else
								v-for="row in paginatedData"
								:key="row.id"
								class="table-row"
							>
								<td v-for="column in columns" :key="column.key" class="table-cell">
									{{ row[column.key] }}
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Pagination -->
				<div v-if="totalPages > 1" class="flex justify-between items-center p-4 border-t border-gray-200 dark:border-slate-700">
					<p class="text-sm text-gray-600 dark:text-gray-400">
						Showing {{ startIndex + 1 }} to {{ Math.min(endIndex, filteredData.length) }} of {{ filteredData.length }} entries
					</p>
					<div class="flex gap-2">
						<button
							@click="currentPage--"
							:disabled="currentPage === 1"
							class="pagination-btn"
						>
							Previous
						</button>
						<button
							v-for="page in visiblePages"
							:key="page"
							@click="currentPage = page"
							class="pagination-btn"
							:class="{ 'pagination-btn--active': page === currentPage }"
						>
							{{ page }}
						</button>
						<button
							@click="currentPage++"
							:disabled="currentPage === totalPages"
							class="pagination-btn"
						>
							Next
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

// State
const activeTab = ref('attendance')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(25)

const filters = ref({
	dateFrom: '',
	dateTo: '',
	status: '',
	department: '',
	search: ''
})

// Report tabs
const reportTabs = [
	{ id: 'attendance', label: 'Attendance', icon: 'present_to_all', count: 156 },
	{ id: 'leave', label: 'Leave', icon: 'event_available', count: 24 },
	{ id: 'payroll', label: 'Payroll', icon: 'payments', count: 12 },
	{ id: 'expenses', label: 'Expenses', icon: 'receipt_long', count: 45 },
	{ id: 'tasks', label: 'Tasks', icon: 'assignment', count: 89 }
]

// Status options based on active tab
const statusOptions = computed(() => {
	const options = {
		attendance: ['Present', 'Absent', 'Late', 'Half Day'],
		leave: ['Approved', 'Pending', 'Rejected'],
		payroll: ['Paid', 'Pending', 'Failed'],
		expenses: ['Approved', 'Pending', 'Rejected'],
		tasks: ['Open', 'In Progress', 'Completed', 'Closed']
	}
	return options[activeTab.value] || []
})

const departments = ['Engineering', 'Sales', 'HR', 'Finance', 'Marketing']

// Summary data
const summaryData = computed(() => {
	const data = {
		attendance: [
			{ id: 'total', label: 'Total Days', value: '22', icon: 'calendar_month', variant: 'primary', change: '+2 days', changeClass: 'text-green-600' },
			{ id: 'present', label: 'Present', value: '20', icon: 'check_circle', variant: 'success', change: '+5%', changeClass: 'text-green-600' },
			{ id: 'absent', label: 'Absent', value: '2', icon: 'cancel', variant: 'danger', change: '-1 day', changeClass: 'text-green-600' },
			{ id: 'rate', label: 'Rate', value: '91%', icon: 'trending_up', variant: 'info', change: '+3%', changeClass: 'text-green-600' }
		],
		leave: [
			{ id: 'total', label: 'Total Requests', value: '24', icon: 'mail', variant: 'primary', change: '+4', changeClass: 'text-amber-600' },
			{ id: 'approved', label: 'Approved', value: '18', icon: 'check_circle', variant: 'success', change: '+2', changeClass: 'text-green-600' },
			{ id: 'pending', label: 'Pending', value: '4', icon: 'schedule', variant: 'warning', change: '+1', changeClass: 'text-red-600' },
			{ id: 'rejected', label: 'Rejected', value: '2', icon: 'cancel', variant: 'danger', change: '0', changeClass: 'text-gray-600' }
		],
		payroll: [
			{ id: 'total', label: 'Total Paid', value: '₹12.5L', icon: 'payments', variant: 'success', change: '+₹1.2L', changeClass: 'text-green-600' },
			{ id: 'pending', label: 'Pending', value: '₹2.1L', icon: 'schedule', variant: 'warning', change: '-₹50K', changeClass: 'text-green-600' },
			{ id: 'avg', label: 'Avg Salary', value: '₹52K', icon: 'account_balance_wallet', variant: 'info', change: '+₹3K', changeClass: 'text-green-600' },
			{ id: 'employees', label: 'Employees', value: '24', icon: 'people', variant: 'primary', change: '+2', changeClass: 'text-green-600' }
		],
		expenses: [
			{ id: 'total', label: 'Total', value: '₹1.8L', icon: 'receipt_long', variant: 'primary', change: '+₹45K', changeClass: 'text-red-600' },
			{ id: 'approved', label: 'Approved', value: '₹1.5L', icon: 'check_circle', variant: 'success', change: '+₹30K', changeClass: 'text-green-600' },
			{ id: 'pending', label: 'Pending', value: '₹25K', icon: 'schedule', variant: 'warning', change: '-₹10K', changeClass: 'text-green-600' },
			{ id: 'rejected', label: 'Rejected', value: '₹5K', icon: 'cancel', variant: 'danger', change: '-₹2K', changeClass: 'text-green-600' }
		],
		tasks: [
			{ id: 'total', label: 'Total Tasks', value: '89', icon: 'assignment', variant: 'primary', change: '+12', changeClass: 'text-green-600' },
			{ id: 'completed', label: 'Completed', value: '65', icon: 'check_circle', variant: 'success', change: '+8', changeClass: 'text-green-600' },
			{ id: 'progress', label: 'In Progress', value: '18', icon: 'pending', variant: 'warning', change: '+3', changeClass: 'text-red-600' },
			{ id: 'overdue', label: 'Overdue', value: '6', icon: 'alarm', variant: 'danger', change: '-2', changeClass: 'text-green-600' }
		]
	}
	return data[activeTab.value] || []
})

// Table columns
const columns = computed(() => {
	const cols = {
		attendance: [
			{ key: 'employee', label: 'Employee' },
			{ key: 'date', label: 'Date' },
			{ key: 'checkIn', label: 'Check In' },
			{ key: 'checkOut', label: 'Check Out' },
			{ key: 'hours', label: 'Hours' },
			{ key: 'status', label: 'Status' }
		],
		leave: [
			{ key: 'employee', label: 'Employee' },
			{ key: 'type', label: 'Leave Type' },
			{ key: 'fromDate', label: 'From' },
			{ key: 'toDate', label: 'To' },
			{ key: 'days', label: 'Days' },
			{ key: 'status', label: 'Status' }
		],
		payroll: [
			{ key: 'employee', label: 'Employee' },
			{ key: 'month', label: 'Month' },
			{ key: 'basic', label: 'Basic' },
			{ key: 'allowances', label: 'Allowances' },
			{ key: 'deductions', label: 'Deductions' },
			{ key: 'netSalary', label: 'Net Salary' },
			{ key: 'status', label: 'Status' }
		],
		expenses: [
			{ key: 'employee', label: 'Employee' },
			{ key: 'type', label: 'Expense Type' },
			{ key: 'date', label: 'Date' },
			{ key: 'amount', label: 'Amount' },
			{ key: 'status', label: 'Status' }
		],
		tasks: [
			{ key: 'title', label: 'Task' },
			{ key: 'assignedTo', label: 'Assigned To' },
			{ key: 'dueDate', label: 'Due Date' },
			{ key: 'priority', label: 'Priority' },
			{ key: 'status', label: 'Status' }
		]
	}
	return cols[activeTab.value] || []
})

// Mock data
const tableData = ref([])

// Filtered and paginated data
const filteredData = computed(() => {
	let data = [...tableData.value]

	if (filters.value.search) {
		const search = filters.value.search.toLowerCase()
		data = data.filter(row =>
			Object.values(row).some(val =>
				String(val).toLowerCase().includes(search)
			)
		)
	}

	if (filters.value.status) {
		data = data.filter(row => row.status === filters.value.status)
	}

	if (filters.value.department) {
		data = data.filter(row => row.department === filters.value.department)
	}

	return data
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value))
const startIndex = computed(() => (currentPage.value - 1) * pageSize.value)
const endIndex = computed(() => startIndex.value + pageSize.value)

const paginatedData = computed(() => {
	return filteredData.value.slice(startIndex.value, endIndex.value)
})

const visiblePages = computed(() => {
	const pages = []
	let start = Math.max(1, currentPage.value - 2)
	let end = Math.min(totalPages.value, start + 4)
	if (end - start < 4) start = Math.max(1, end - 4)
	for (let i = start; i <= end; i++) {
		pages.push(i)
	}
	return pages
})

// Methods
function clearFilters() {
	filters.value = {
		dateFrom: '',
		dateTo: '',
		status: '',
		department: '',
		search: ''
	}
	currentPage.value = 1
}

async function refreshData() {
	loading.value = true
	// Simulate API call
	setTimeout(() => {
		loadMockData()
		loading.value = false
	}, 1000)
}

function loadMockData() {
	const mockData = {
		attendance: [
			{ id: 1, employee: 'John Doe', date: '2026-04-11', checkIn: '09:00', checkOut: '18:00', hours: '9h', status: 'Present', department: 'Engineering' },
			{ id: 2, employee: 'Jane Smith', date: '2026-04-11', checkIn: '09:15', checkOut: '18:00', hours: '8.75h', status: 'Late', department: 'Sales' },
			{ id: 3, employee: 'Bob Johnson', date: '2026-04-11', checkIn: '--', checkOut: '--', hours: '0h', status: 'Absent', department: 'Engineering' },
			{ id: 4, employee: 'Alice Williams', date: '2026-04-11', checkIn: '09:00', checkOut: '14:00', hours: '5h', status: 'Half Day', department: 'HR' }
		],
		leave: [
			{ id: 1, employee: 'John Doe', type: 'Annual Leave', fromDate: '2026-04-15', toDate: '2026-04-17', days: 3, status: 'Approved', department: 'Engineering' },
			{ id: 2, employee: 'Jane Smith', type: 'Sick Leave', fromDate: '2026-04-12', toDate: '2026-04-12', days: 1, status: 'Pending', department: 'Sales' },
			{ id: 3, employee: 'Bob Johnson', type: 'Casual Leave', fromDate: '2026-04-10', toDate: '2026-04-11', days: 2, status: 'Approved', department: 'Engineering' }
		],
		payroll: [
			{ id: 1, employee: 'John Doe', month: 'March 2026', basic: '₹45,000', allowances: '₹15,000', deductions: '₹8,000', netSalary: '₹52,000', status: 'Paid', department: 'Engineering' },
			{ id: 2, employee: 'Jane Smith', month: 'March 2026', basic: '₹42,000', allowances: '₹12,000', deductions: '₹6,500', netSalary: '₹47,500', status: 'Paid', department: 'Sales' },
			{ id: 3, employee: 'Bob Johnson', month: 'March 2026', basic: '₹48,000', allowances: '₹18,000', deductions: '₹9,500', netSalary: '₹56,500', status: 'Pending', department: 'Engineering' }
		],
		expenses: [
			{ id: 1, employee: 'John Doe', type: 'Travel', date: '2026-04-10', amount: '₹3,500', status: 'Approved', department: 'Engineering' },
			{ id: 2, employee: 'Jane Smith', type: 'Meals', date: '2026-04-09', amount: '₹850', status: 'Pending', department: 'Sales' },
			{ id: 3, employee: 'Bob Johnson', type: 'Office Supplies', date: '2026-04-08', amount: '₹2,300', status: 'Approved', department: 'Engineering' }
		],
		tasks: [
			{ id: 1, title: 'Complete project report', assignedTo: 'John Doe', dueDate: '2026-04-15', priority: 'High', status: 'In Progress', department: 'Engineering' },
			{ id: 2, title: 'Review documentation', assignedTo: 'Jane Smith', dueDate: '2026-04-14', priority: 'Medium', status: 'Open', department: 'Sales' },
			{ id: 3, title: 'Update presentation', assignedTo: 'Bob Johnson', dueDate: '2026-04-13', priority: 'High', status: 'Completed', department: 'Engineering' },
			{ id: 4, title: 'Fix bug in module', assignedTo: 'Alice Williams', dueDate: '2026-04-12', priority: 'High', status: 'Overdue', department: 'HR' }
		]
	}
	tableData.value = mockData[activeTab.value] || []
}

function exportData(format) {
	console.log('Exporting as', format)
	// Implement export logic
}

// Watch for tab changes
watch(activeTab, () => {
	currentPage.value = 1
	loadMockData()
})

// Lifecycle
onMounted(() => {
	loadMockData()
})
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
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	border-color: transparent;
}

.tab-count {
	background: rgba(0, 0, 0, 0.2);
	padding: 0.125rem 0.5rem;
	border-radius: 99px;
	font-size: 0.75rem;
}

.form-input {
	width: 100%;
	padding: 0.625rem 0.875rem;
	border: 1px solid #e5e7eb;
	border-radius: 0.5rem;
	font-size: 0.875rem;
	transition: all 0.2s;
}

.form-input:focus {
	outline: none;
	border-color: #667eea;
	box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
	background: rgba(102, 126, 234, 0.1);
	color: #667eea;
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

.pagination-btn {
	padding: 0.5rem 0.75rem;
	border: 1px solid #e5e7eb;
	border-radius: 0.5rem;
	font-size: 0.875rem;
	font-weight: 500;
	transition: all 0.2s;
	background: white;
}

.pagination-btn:hover:not(:disabled) {
	background: #f9fafb;
}

.pagination-btn:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.pagination-btn--active {
	background: #667eea;
	color: white;
	border-color: #667eea;
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

.btn-primary {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	border: none;
}

.btn-primary:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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
