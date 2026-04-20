<template>
	<div class="h-full flex flex-col gap-10 no-scrollbar overflow-y-auto pb-20">
		<!-- Header -->
		<div class="shrink-0 px-2">
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<p
						class="text-[10px] font-black text-gray-400 uppercase tracking-[0.3em] mb-2"
					>
						Financial Overview
					</p>
					<h1 class="text-4xl font-black text-gray-900 tracking-tight leading-none mb-3">
						Payroll Management
					</h1>
				</div>
				<div class="flex items-center gap-4">
					<div
						class="bg-white border border-gray-100 rounded-xl px-4 py-2.5 flex items-center gap-2"
					>
						<p class="text-[9px] font-black text-gray-400 uppercase tracking-widest">
							Fiscal Year
						</p>
						<select
							v-model="selectedYear"
							@change="changeYear"
							class="bg-transparent text-[13px] font-black text-gray-900 outline-none appearance-none cursor-pointer"
						>
							<option v-for="year in availableYears" :key="year" :value="year">
								{{ year }}
							</option>
						</select>
						<span class="material-symbols-outlined text-gray-400 text-lg"
							>expand_more</span
						>
					</div>
					<button
						class="px-6 py-2.5 bg-primary text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-glow-emerald transition-all flex items-center gap-2"
					>
						<span class="material-symbols-outlined text-lg">add</span>
						Generate Run
					</button>
				</div>
			</div>
		</div>

		<!-- Stats Row -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center">
						<span class="material-symbols-outlined text-gray-600 text-xl"
							>account_balance</span
						>
					</div>
					<span
						class="text-[9px] font-black text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full"
						>+12.4% vs LY</span
					>
				</div>
				<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">
					Net Pay Year to Date
				</p>
				<p class="text-4xl font-black text-gray-900 tracking-tighter leading-none">
					{{ formatCurrency(payrollStore.totalYTD) }}
				</p>
			</div>

			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center">
						<span class="material-symbols-outlined text-emerald-600 text-xl"
							>trending_up</span
						>
					</div>
				</div>
				<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">
					Gross Earnings
				</p>
				<p class="text-4xl font-black text-gray-900 tracking-tighter leading-none">
					{{ formatCurrency(payrollStore.totalEarningsYTD) }}
				</p>
			</div>

			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-12 h-12 rounded-2xl bg-gray-50 flex items-center justify-center">
						<span class="material-symbols-outlined text-amber-600 text-xl"
							>trending_down</span
						>
					</div>
				</div>
				<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">
					Total Deductions
				</p>
				<p class="text-4xl font-black text-gray-900 tracking-tighter leading-none">
					{{ formatCurrency(payrollStore.totalDeductionsYTD) }}
				</p>
				<p class="text-[10px] font-bold text-gray-400 mt-2">{{ taxRatio }}% Tax Ratio</p>
			</div>
		</div>

		<!-- Salary Slips Table -->
		<div class="premium-card !p-0 overflow-hidden border border-gray-100 shadow-sm">
			<div class="flex items-center justify-between px-10 py-6 border-b border-gray-50">
				<h3 class="text-sm font-black text-gray-900 tracking-tight">
					Recent Salary Slips
				</h3>
				<div class="flex items-center gap-6">
					<button
						class="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-gray-400 transition-all"
					>
						<span class="material-symbols-outlined text-lg">filter_list</span>
						Filter
					</button>
					<button
						class="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-gray-400 transition-all"
					>
						<span class="material-symbols-outlined text-lg">download</span>
						Export All
					</button>
				</div>
			</div>

			<table class="w-full text-left">
				<thead class="border-b border-gray-50 bg-gray-50/30">
					<tr>
						<th
							class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em]"
						>
							Pay Period
						</th>
						<th
							class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-right"
						>
							Gross Amount
						</th>
						<th
							class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-right"
						>
							Net Amount
						</th>
						<th
							class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-center"
						>
							Disbursement Status
						</th>
						<th
							class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-center"
						>
							Documents
						</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-50">
					<tr
						v-for="slip in payrollStore.salarySlips"
						:key="slip.id"
						class=" transition-colors"
					>
						<td class="px-10 py-6">
							<div class="flex items-center gap-3">
								<div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
								<p class="text-sm font-bold text-gray-900">
									{{ formatPayPeriod(slip) }}
								</p>
							</div>
						</td>
						<td class="px-10 py-6 text-right">
							<p class="text-sm font-bold text-gray-400">
								{{ formatCurrency(slip.gross_pay) }}
							</p>
						</td>
						<td class="px-10 py-6 text-right">
							<p class="text-sm font-black text-gray-900">
								{{ formatCurrency(slip.net_pay) }}
							</p>
						</td>
						<td class="px-10 py-6 text-center">
							<span
								class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest bg-emerald-100 text-emerald-700"
							>
								Completed
							</span>
						</td>
						<td class="px-10 py-6 text-center">
							<button class="text-gray-400 transition-colors">
								<span class="material-symbols-outlined text-lg">download</span>
							</button>
						</td>
					</tr>
				</tbody>
			</table>

			<!-- Pagination -->
			<div class="flex items-center justify-between px-10 py-5 border-t border-gray-50">
				<p class="text-[10px] font-bold text-gray-400">Showing 1 to 4 of 12 records</p>
				<div class="flex items-center gap-2">
					<button
						class="w-8 h-8 rounded-lg border border-gray-100 flex items-center justify-center text-gray-400 transition-all"
					>
						<span class="material-symbols-outlined text-sm">chevron_left</span>
					</button>
					<button
						class="w-8 h-8 rounded-lg bg-emerald-950 text-white flex items-center justify-center text-[10px] font-black"
					>
						1
					</button>
					<button
						class="w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-bold text-gray-400 transition-all"
					>
						2
					</button>
					<button
						class="w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-bold text-gray-400 transition-all"
					>
						3
					</button>
					<button
						class="w-8 h-8 rounded-lg border border-gray-100 flex items-center justify-center text-gray-400 transition-all"
					>
						<span class="material-symbols-outlined text-sm">chevron_right</span>
					</button>
				</div>
			</div>
		</div>

		<!-- Bottom Section -->
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
			<!-- Tax Compliance -->
			<div class="lg:col-span-8 premium-card !p-10">
				<div class="flex items-center gap-3 mb-6">
					<span class="material-symbols-outlined text-emerald-600 text-xl"
						>verified</span
					>
					<h4 class="text-sm font-black text-gray-900 tracking-tight">
						Tax Compliance Certificate
					</h4>
				</div>
				<p class="text-[11px] font-bold text-gray-500 leading-relaxed mb-8">
					Your payroll runs for the current fiscal year {{ selectedYear }} are fully
					compliant with local tax regulations. The next audit window opens in Q1 2027.
					You can request a digital compliance signature for internal reporting below.
				</p>
				<button
					class="text-[11px] font-black text-emerald-950 uppercase tracking-widest transition-colors"
				>
					Download Compliance Report (PDF)
				</button>
			</div>

			<!-- Assistance -->
			<div class="lg:col-span-4 premium-card !p-10 bg-gray-100 border-gray-100">
				<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-4">
					Assistance
				</p>
				<h4 class="text-sm font-black text-gray-900 tracking-tight mb-2">
					Need help with complex deductions?
				</h4>
				<button
					class="w-full py-3.5 bg-white border border-gray-200 rounded-xl text-[10px] font-black uppercase tracking-widest text-gray-900 transition-all mt-6"
				>
					Connect with Payroll Expert
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { usePayrollStore } from "@/stores/payroll";
import { useEmployeeStore } from "@/stores/employee";

const payrollStore = usePayrollStore();
const employeeStore = useEmployeeStore();

const selectedYear = ref(new Date().getFullYear());
const currentYear = new Date().getFullYear();

const availableYears = computed(() => {
	const years = [];
	for (let i = 0; i < 3; i++) years.push(currentYear - i);
	return years;
});

const taxRatio = computed(() => {
	if (payrollStore.totalEarningsYTD === 0) return "0";
	return ((payrollStore.totalDeductionsYTD / payrollStore.totalEarningsYTD) * 100).toFixed(1);
});

function changeYear() {
	payrollStore.fetchSalarySlips(selectedYear.value);
	payrollStore.fetchPayrollSummary(selectedYear.value);
}

function formatCurrency(amount) {
	if (amount === null || amount === undefined) return "$0";
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "USD",
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	}).format(amount);
}

function formatPayPeriod(slip) {
	if (!slip.start_date) return "Monthly";
	const date = new Date(slip.start_date);
	return `${date.toLocaleDateString("en-US", {
		month: "short",
	})} ${date.getFullYear()} - Monthly`;
}

onMounted(async () => {
	await employeeStore.init();
	payrollStore.init();
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
</style>
