<template>
	<div class="max-w-7xl mx-auto space-y-12 pb-20">
		<!-- Header -->
		<div class="shrink-0 px-2">
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<p
						class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.3em] mb-2"
					>
						Financial Overview
					</p>
					<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">
						Payroll Management
					</h1>
				</div>
			</div>
		</div>

		<!-- Generate Salary Slip Form -->
		<div class="shrink-0 px-2 mt-4">
			<div
				class="premium-card !p-6 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow-sm flex flex-col gap-6"
			>
				<div class="flex flex-col md:flex-row items-end gap-6">
					<div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
						<div class="flex flex-col gap-1.5">
							<label
								class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest"
								>Select Month</label
							>
							<select
								v-model="genMonth"
								@change="statusMessage = ''"
								class="w-full h-11 px-4 bg-gray-50 dark:bg-gray-800 border-none rounded-xl text-sm font-bold text-gray-900 dark:text-white focus:ring-2 focus:ring-emerald-500/20 transition-all outline-none appearance-none cursor-pointer"
							>
								<option
									v-for="(name, index) in monthNames"
									:key="index"
									:value="index + 1"
								>
									{{ name }}
								</option>
							</select>
						</div>
						<div class="flex flex-col gap-1.5">
							<label
								class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest"
								>Select Year</label
							>
							<select
								v-model="genYear"
								@change="statusMessage = ''"
								class="w-full h-11 px-4 bg-gray-50 dark:bg-gray-800 border-none rounded-xl text-sm font-bold text-gray-900 dark:text-white focus:ring-2 focus:ring-emerald-500/20 transition-all outline-none appearance-none cursor-pointer"
							>
								<option v-for="y in genYearOptions" :key="y" :value="y">
									{{ y }}
								</option>
							</select>
						</div>
					</div>
					<button
						@click="generateSlip"
						:disabled="generating"
						class="md:w-auto w-full h-11 px-8 bg-emerald-950 dark:bg-emerald-900 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-emerald-900 dark:hover:bg-emerald-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-3"
					>
						<span v-if="generating" class="material-symbols-outlined animate-spin text-lg"
							>sync</span
						>
						<span v-else class="material-symbols-outlined text-lg">receipt_long</span>
						{{ generating ? "Generating..." : "Generate Salary Slip" }}
					</button>
				</div>

				<!-- Notification Banner -->
				<Transition name="fade">
					<div
						v-if="statusMessage"
						:class="[
							'px-6 py-4 rounded-2xl text-xs font-bold flex items-center justify-between transition-all',
							statusType === 'success'
								? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/50'
								: 'bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 border border-red-100 dark:border-red-900/50',
						]"
					>
						<div class="flex items-center gap-3">
							<span class="material-symbols-outlined text-lg">{{
								statusType === "success" ? "check_circle" : "error"
							}}</span>
							{{ statusMessage }}
						</div>
						<button
							@click="statusMessage = ''"
							class="hover:opacity-70 transition-opacity text-gray-400 dark:text-gray-500"
						>
							<span class="material-symbols-outlined text-lg">close</span>
						</button>
					</div>
				</Transition>
			</div>
		</div>

		<!-- Stats Row -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-12 h-12 rounded-2xl bg-gray-50 dark:bg-gray-800 flex items-center justify-center">
						<span class="material-symbols-outlined text-gray-600 dark:text-gray-400 text-xl"
							>account_balance</span
						>
					</div>
					<span
						class="text-[9px] font-black text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 px-2 py-1 rounded-full"
						>Net Period</span
					>
				</div>
				<p class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.2em] mb-1">
					Net Pay for Selected Period
				</p>
				<p class="text-4xl font-black text-gray-900 dark:text-white tracking-tighter leading-none">
					{{ formatCurrency(payrollStore.myTotalYTD) }}
				</p>
			</div>

			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-12 h-12 rounded-2xl bg-gray-50 dark:bg-gray-800 flex items-center justify-center">
						<span class="material-symbols-outlined text-emerald-600 dark:text-emerald-400 text-xl"
							>trending_up</span
						>
					</div>
				</div>
				<p class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.2em] mb-1">
					Gross Earnings
				</p>
				<p class="text-4xl font-black text-gray-900 dark:text-white tracking-tighter leading-none">
					{{ formatCurrency(payrollStore.myTotalEarningsYTD) }}
				</p>
			</div>

			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-12 h-12 rounded-2xl bg-gray-50 dark:bg-gray-800 flex items-center justify-center">
						<span class="material-symbols-outlined text-amber-600 dark:text-amber-400 text-xl"
							>trending_down</span
						>
					</div>
				</div>
				<p class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.2em] mb-1">
					Total Deductions
				</p>
				<p class="text-4xl font-black text-gray-900 dark:text-white tracking-tighter leading-none">
					{{ formatCurrency(payrollStore.myTotalDeductionsYTD) }}
				</p>
				<p class="text-[10px] font-bold text-gray-400 dark:text-gray-500 mt-2">{{ taxRatio }}% Tax Ratio</p>
			</div>
		</div>

		<!-- Salary Slips Table -->
		<div class="premium-card !p-0 overflow-hidden border border-gray-100 dark:border-gray-800 shadow-sm">
			<div class="flex flex-col md:flex-row md:items-center justify-between px-6 md:px-10 py-6 border-b border-gray-50 dark:border-gray-800 gap-6">
				<h3 class="text-sm font-black text-gray-900 dark:text-white tracking-tight">Recent Salary Slips</h3>
				<div class="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-4 sm:gap-x-8 sm:gap-y-4">
					<div v-if="payrollStore.canViewAll" class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 relative">
						<label class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest shrink-0">Employee:</label>
						<div class="relative w-full">
							<select
								v-model="payrollStore.selectedEmployeeId"
								class="bg-gray-50 dark:bg-gray-800 border-none rounded-xl text-[10px] font-black uppercase tracking-widest text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-emerald-500/20 transition-all outline-none appearance-none cursor-pointer py-1.5 px-4 pr-10 w-full sm:min-w-[160px]"
							>
								<option value="all">All Employees</option>
								<option v-for="emp in payrollStore.employeeList" :key="emp.name" :value="emp.name">
									{{ emp.employee_name }}
								</option>
							</select>
							<span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 text-sm pointer-events-none">expand_more</span>
						</div>
					</div>
					<div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 relative">
						<label class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest shrink-0">Period:</label>
						<div class="relative w-full">
							<select
								v-model="selectedMonthKey"
								class="bg-gray-50 dark:bg-gray-800 border-none rounded-xl text-[10px] font-black uppercase tracking-widest text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-emerald-500/20 transition-all outline-none appearance-none cursor-pointer py-1.5 px-4 pr-10 w-full sm:min-w-[140px]"
							>
								<option value="all">All Months</option>
								<option v-for="opt in monthOptions" :key="opt.value" :value="opt.value">
									{{ opt.label }}
								</option>
							</select>
							<span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 text-sm pointer-events-none">expand_more</span>
						</div>
					</div>
				</div>
			</div>

			<div
				ref="tableContainer"
				class="overflow-x-auto cursor-grab"
				:class="{ 'cursor-grabbing select-none': isDragging }"
				@mousedown="handleMouseDown"
				@mouseleave="handleMouseLeave"
				@mouseup="handleMouseUp"
				@mousemove="handleMouseMove"
			>
				<table class="w-full text-left min-w-[900px]">
					<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-800/50">
						<tr>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Reference</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Employee Name</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Pay Period</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-right">Gross Amount</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Status</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Download</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-50 dark:divide-gray-800">
						<tr v-for="slip in payrollStore.salarySlips" :key="slip.id" class="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
							<td class="px-10 py-6">
								<span 
									@click="viewDetails(slip.id)"
									class="text-sm font-bold text-emerald-600 dark:text-emerald-400 hover:underline cursor-pointer transition-all"
								>
									{{ slip.id }}
								</span>
							</td>
							<td class="px-10 py-6">
								<p class="text-sm font-bold text-gray-900 dark:text-white">{{ slip.employee_name }}</p>
								<p class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest">{{ slip.employee }}</p>
							</td>
							<td class="px-10 py-6">
								<p class="text-sm font-bold text-gray-600 dark:text-gray-400">{{ formatPayPeriod(slip) }}</p>
							</td>
							<td class="px-10 py-6 text-right">
								<p class="text-sm font-black text-gray-900 dark:text-white">{{ formatCurrency(slip.gross_pay) }}</p>
							</td>
							<td class="px-10 py-6 text-center">
								<span 
									class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest"
									:class="slip.status === 'Submitted' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400'"
								>
									{{ slip.status === 'Submitted' ? 'Completed' : slip.status }}
								</span>
							</td>
							<td class="px-10 py-6 text-center">
								<button 
									@click="downloadSlip(slip.id)"
									class="w-10 h-10 rounded-xl flex items-center justify-center text-gray-400 dark:text-gray-500 hover:text-emerald-700 dark:hover:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 transition-all mx-auto"
									title="Download Salary Slip"
								>
									<span class="material-symbols-outlined text-lg">download</span>
								</button>
							</td>
						</tr>
						<tr v-if="payrollStore.salarySlips.length === 0">
							<td colspan="6" class="px-10 py-20 text-center">
								<p class="text-sm font-bold text-gray-400 dark:text-gray-500">No salary slips found for this period.</p>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<!-- Detail Modal -->
		<div v-if="showDetailModal" @click.self="showDetailModal = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
			<div class="bg-white dark:bg-gray-900 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-2xl w-full max-w-2xl mx-4 overflow-hidden flex flex-col max-h-[90vh]">
				<!-- Modal Header -->
				<div class="px-8 py-6 border-b border-gray-50 dark:border-gray-800 flex items-center justify-between bg-gray-50/30 dark:bg-gray-800/50">
					<div>
						<h2 class="text-lg font-black text-gray-900 dark:text-white tracking-tight">Salary Slip Details</h2>
						<p class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mt-1">{{ slipDetail?.id }}</p>
					</div>
					<button @click="showDetailModal = false" class="w-10 h-10 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-all">
						<span class="material-symbols-outlined">close</span>
					</button>
				</div>

				<!-- Modal Content -->
				<div class="p-8 overflow-y-auto no-scrollbar space-y-8">
					<!-- Header Info -->
					<div class="grid grid-cols-2 md:grid-cols-4 gap-6">
						<div>
							<p class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Employee</p>
							<p class="text-sm font-black text-gray-900 dark:text-white">{{ slipDetail?.employee_name }}</p>
						</div>
						<div>
							<p class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Period</p>
							<p class="text-sm font-black text-gray-900 dark:text-white">{{ slipDetail?.month }} {{ slipDetail?.year }}</p>
						</div>
						<div>
							<p class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Working Days</p>
							<p class="text-sm font-black text-gray-900 dark:text-white">{{ slipDetail?.working_days }}</p>
						</div>
						<div>
							<p class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1">Payment Days</p>
							<p class="text-sm font-black text-gray-900 dark:text-white">{{ slipDetail?.payment_days }}</p>
						</div>
					</div>

					<!-- Earnings & Deductions -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-10">
						<!-- Earnings -->
						<div class="space-y-4">
							<h4 class="text-[10px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-widest flex items-center gap-2">
								<span class="w-2 h-2 rounded-full bg-emerald-500"></span>
								Earnings
							</h4>
							<div class="space-y-3">
								<div v-for="e in slipDetail?.earnings" :key="e.component" class="flex items-center justify-between">
									<span class="text-xs font-bold text-gray-600 dark:text-gray-400">{{ e.component }}</span>
									<span class="text-sm font-black text-gray-900 dark:text-white">{{ formatCurrency(e.amount) }}</span>
								</div>
								<div class="pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
									<span class="text-xs font-black text-gray-900 dark:text-white">Gross Pay</span>
									<span class="text-sm font-black text-gray-900 dark:text-white">{{ formatCurrency(slipDetail?.gross_pay) }}</span>
								</div>
							</div>
						</div>

						<!-- Deductions -->
						<div class="space-y-4">
							<h4 class="text-[10px] font-black text-amber-700 dark:text-amber-400 uppercase tracking-widest flex items-center gap-2">
								<span class="w-2 h-2 rounded-full bg-amber-500"></span>
								Deductions
							</h4>
							<div class="space-y-3">
								<div v-for="d in slipDetail?.deductions" :key="d.component" class="flex items-center justify-between">
									<span class="text-xs font-bold text-gray-600 dark:text-gray-400">{{ d.component }}</span>
									<span class="text-sm font-black text-gray-900 dark:text-white text-red-600 dark:text-red-400">-{{ formatCurrency(d.amount) }}</span>
								</div>
								<div class="pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
									<span class="text-xs font-black text-gray-900 dark:text-white">Total Deductions</span>
									<span class="text-sm font-black text-gray-900 dark:text-white">{{ formatCurrency(slipDetail?.total_deduction) }}</span>
								</div>
							</div>
						</div>
					</div>

					<!-- Net Pay -->
					<div class="p-6 bg-emerald-950 dark:bg-emerald-900 rounded-2xl flex items-center justify-between text-white">
						<div>
							<p class="text-[9px] font-black text-emerald-400 uppercase tracking-widest mb-1">Net Payable Amount</p>
							<p class="text-2xl font-black tracking-tight text-white">{{ formatCurrency(slipDetail?.net_pay) }}</p>
						</div>
						<button 
							@click="downloadSlip(slipDetail?.id)"
							class="px-6 py-3 bg-emerald-500 text-emerald-950 text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-emerald-400 transition-all flex items-center gap-2"
						>
							<span class="material-symbols-outlined text-lg">download</span>
							Download PDF
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- PDF Viewer Modal -->
		<div v-if="showPdfModal" @click.self="showPdfModal = false" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-md p-4 md:p-12">
			<div class="bg-white dark:bg-gray-900 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-2xl w-full h-full max-w-5xl flex flex-col overflow-hidden animate-fade-in">
				<!-- Header -->
				<div class="px-8 py-5 border-b border-gray-50 dark:border-gray-800 flex items-center justify-between bg-gray-50/30 dark:bg-gray-800/50">
					<div class="flex items-center gap-4">
						<div class="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600">
							<span class="material-symbols-outlined">description</span>
						</div>
						<div>
							<h2 class="text-base font-black text-gray-900 dark:text-white tracking-tight">Salary Slip Preview</h2>
							<p class="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mt-0.5">{{ currentSlipId }}</p>
						</div>
					</div>
					<div class="flex items-center gap-3">
						<button 
							@click="downloadSlip(currentSlipId, true)"
							class="h-10 px-6 bg-emerald-950 dark:bg-emerald-900 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-emerald-900 transition-all flex items-center gap-2"
						>
							<span class="material-symbols-outlined text-lg">download</span>
							Download
						</button>
						<button @click="showPdfModal = false" class="w-10 h-10 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-all">
							<span class="material-symbols-outlined">close</span>
						</button>
					</div>
				</div>
				<!-- Iframe -->
				<div class="flex-1 bg-gray-100 dark:bg-gray-950 relative">
					<iframe :src="pdfUrl" class="w-full h-full border-none shadow-inner" frameborder="0"></iframe>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { usePayrollStore } from "@/stores/payroll";
import { useEmployeeStore } from "@/stores/employee";

const payrollStore = usePayrollStore();
const employeeStore = useEmployeeStore();

// Drag scroll state for table
const tableContainer = ref(null);
const isDragging = ref(false);
let startX = 0;
let scrollLeft = 0;

function handleMouseDown(e) {
	if (e.button !== 0) return; // Left click only
	isDragging.value = true;
	startX = e.pageX - tableContainer.value.offsetLeft;
	scrollLeft = tableContainer.value.scrollLeft;
}

function handleMouseLeave() {
	isDragging.value = false;
}

function handleMouseUp() {
	isDragging.value = false;
}

function handleMouseMove(e) {
	if (!isDragging.value) return;
	e.preventDefault();
	const x = e.pageX - tableContainer.value.offsetLeft;
	const walk = (x - startX) * 1.5; // Scroll speed multiplier
	tableContainer.value.scrollLeft = scrollLeft - walk;
}

// Generation Form State
const genMonth = ref(new Date().getMonth());
const genYear = ref(new Date().getFullYear());
if (new Date().getMonth() === 0) {
	genMonth.value = 12;
	genYear.value -= 1;
}

const statusMessage = ref("");
const statusType = ref("success"); // 'success' or 'error'
const generating = ref(false);

const monthNames = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
];

const genYearOptions = computed(() => {
	const currentYear = new Date().getFullYear();
	return [currentYear, currentYear - 1];
});

// Table Filters State (Adopted from AttendanceView)
const selectedMonth = ref(null);
const selectedYear = ref(null);

const monthOptions = computed(() => {
	const opts = [];
	const start = new Date();
	for (let offset = -24; offset <= 0; offset++) {
		const d = new Date(start.getFullYear(), start.getMonth() + offset, 1);
		const m = d.getMonth() + 1;
		const y = d.getFullYear();
		opts.push({
			value: `${y}-${m}`,
			label: d.toLocaleDateString("en-US", { month: "long", year: "numeric" }),
		});
	}
	return opts;
});

const selectedMonthKey = computed({
	get: () => (selectedMonth.value ? `${selectedYear.value}-${selectedMonth.value}` : "all"),
	set: (val) => {
		if (val === "all") {
			selectedYear.value = null;
			selectedMonth.value = null;
		} else {
			const [y, m] = val.split("-").map(Number);
			selectedYear.value = y;
			selectedMonth.value = m;
		}
	},
});

// Detail Modal State
const showDetailModal = ref(false);
const slipDetail = ref(null);

// PDF Modal State
const showPdfModal = ref(false);
const pdfUrl = ref("");
const currentSlipId = ref("");

const taxRatio = computed(() => {
	if (!payrollStore.myTotalEarningsYTD || payrollStore.myTotalEarningsYTD === 0) return "0";
	return ((payrollStore.myTotalDeductionsYTD / payrollStore.myTotalEarningsYTD) * 100).toFixed(1);
});

// Watchers for filters
watch([selectedMonth, selectedYear, () => payrollStore.selectedEmployeeId], () => {
	refreshData();
});

async function refreshData() {
	const params = {
		year: selectedYear.value,
		month: selectedMonth.value,
	};
	await payrollStore.fetchSalarySlips(params);
	await payrollStore.fetchPayrollSummary(params);

	// Always fetch current user summary for the cards
	if (employeeStore.employee?.name) {
		await payrollStore.fetchMyPayrollSummary({
			...params,
			employee_id: employeeStore.employee?.name,
		});
	}
}

async function generateSlip() {
	generating.value = true;
	statusMessage.value = "";
	try {
		const result = await payrollStore.generateMyPayslip(genMonth.value, genYear.value);
		if (result.success) {
			statusType.value = "success";
			statusMessage.value = result.message || "Salary slip generated successfully";
			refreshData();
		} else {
			statusType.value = "error";
			statusMessage.value = result.error || "Failed to generate salary slip";
		}
	} catch (e) {
		console.error(e);
		statusType.value = "error";
		statusMessage.value = "An error occurred while generating the salary slip.";
	} finally {
		generating.value = false;
	}
}

async function viewDetails(slipId) {
	try {
		const res = await payrollStore.getSlipDetails(slipId);
		if (res) {
			slipDetail.value = res;
			showDetailModal.value = true;
		}
	} catch (e) {
		console.error(e);
	}
}

function downloadSlip(slipId, actualDownload = false) {
	if (!slipId) return;
	const url = `/api/method/zevar_core.api.payroll.download_salary_slip?slip_name=${slipId}`;
	
	if (actualDownload) {
		window.open(url, "_blank");
	} else {
		currentSlipId.value = slipId;
		pdfUrl.value = url;
		showPdfModal.value = true;
	}
}

function formatCurrency(amount) {
	if (amount === null || amount === undefined) return "₹0.00";
	return new Intl.NumberFormat("en-IN", {
		style: "currency",
		currency: "INR",
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	}).format(amount);
}

function formatPayPeriod(slip) {
	if (!slip.start_date) return "Monthly";
    const parts = slip.start_date.split("-");
    if (parts.length < 2) return "Monthly";
    const year = parts[0];
    const month = parseInt(parts[1]);
    const monthName = monthNames[month - 1].substring(0, 3);
    return `${monthName} ${year} - Monthly`;
}

onMounted(async () => {
	await employeeStore.init();
	await payrollStore.checkPermissions();
	
	if (payrollStore.canViewAll) {
		await payrollStore.fetchEmployeeList();
		payrollStore.selectedEmployeeId = employeeStore.employee?.name || "all";
	} else {
		payrollStore.selectedEmployeeId = employeeStore.employee?.name;
	}
	
    refreshData();
});
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
