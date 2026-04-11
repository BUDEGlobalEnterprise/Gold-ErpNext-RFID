<template>
	<div class="h-full flex flex-col gap-10 no-scrollbar overflow-y-auto pb-20">
		<!-- Header -->
		<div class="shrink-0 px-2">
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<h1 class="text-4xl font-black text-gray-900 tracking-tight leading-none mb-3">Expense Claims</h1>
					<p class="text-gray-500 font-medium font-sans">Manage your professional reimbursements and atelier budget.</p>
				</div>
				<div class="flex items-center gap-4">
					<button @click="showClaimModal = true" class="px-8 py-3 bg-primary text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-glow-emerald hover:bg-black transition-all flex items-center gap-2">
						<span class="material-symbols-outlined text-lg">add</span>
						New Claim
					</button>
				</div>
			</div>
		</div>

		<!-- Stats Row -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center">
						<span class="material-symbols-outlined text-emerald-600 text-xl">verified</span>
					</div>
					<span class="text-[9px] font-black text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">+12% vs last month</span>
				</div>
				<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Total Reimbursed</p>
				<p class="text-3xl font-black text-gray-900 tracking-tighter leading-none">{{ formatCurrency(stats.total_reimbursed) }}</p>
			</div>

			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
						<span class="material-symbols-outlined text-amber-600 text-xl">hourglass_top</span>
					</div>
					<span class="text-[9px] font-black text-amber-600 bg-amber-50 px-2 py-1 rounded-full">4 items active</span>
				</div>
				<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Pending Approval</p>
				<p class="text-3xl font-black text-gray-900 tracking-tighter leading-none">{{ formatCurrency(stats.pending_amount) }}</p>
			</div>

			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center">
						<span class="material-symbols-outlined text-gray-600 text-xl">donut_large</span>
					</div>
					<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em]">Budget Used</p>
					<p class="text-sm font-black text-gray-900">65.4%</p>
				</div>
				<div class="h-2 w-full bg-gray-100 rounded-full overflow-hidden mb-3">
					<div class="h-full bg-emerald-600 rounded-full" style="width: 65.4%"></div>
				</div>
				<div class="flex justify-between">
					<span class="text-[9px] font-bold text-gray-400">{{ formatCurrency(stats.total_spent) }} Spent</span>
					<span class="text-[9px] font-bold text-gray-400">{{ formatCurrency(stats.budget_limit) }} Limit</span>
				</div>
			</div>
		</div>

		<!-- Filter Tabs -->
		<div class="flex items-center gap-8 px-2">
			<button
				v-for="filter in ['All Claims', 'Pending', 'Approved', 'Rejected']"
				:key="filter"
				@click="activeFilter = filter"
				class="text-[11px] font-black uppercase tracking-widest pb-2 transition-all"
				:class="activeFilter === filter
					? 'text-gray-900 border-b-2 border-gray-900'
					: 'text-gray-400 hover:text-gray-600'"
			>
				{{ filter }}
			</button>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
			<!-- Claims List -->
			<div class="lg:col-span-8 space-y-4">
				<div v-for="claim in filteredClaims" :key="claim.name" class="premium-card !p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 border-gray-100 group hover:border-primary transition-all shadow-sm">
					<div class="flex items-center gap-6 flex-1">
						<div class="w-12 h-12 rounded-xl bg-gray-50 flex items-center justify-center text-gray-400 group-hover:bg-emerald-50 group-hover:text-primary transition-colors shrink-0">
							<span class="material-symbols-outlined text-xl">{{ getTypeIcon(claim.expense_type) }}</span>
						</div>
						<div class="min-w-0">
							<p class="text-sm font-black text-gray-900 tracking-tight leading-none mb-1 truncate">{{ claim.title || claim.expense_type }}</p>
							<div class="flex items-center gap-3">
								<span class="text-[10px] font-bold text-gray-400">{{ claim.category || 'Travel & Logistics' }}</span>
								<div class="w-1 h-1 rounded-full bg-gray-200"></div>
								<span class="text-[10px] font-bold text-gray-400">{{ formatDate(claim.posting_date) }}</span>
							</div>
						</div>
					</div>
					<div class="flex items-center gap-8">
						<div class="text-right">
							<p class="text-lg font-black text-gray-900 tracking-tighter">{{ formatCurrency(claim.total_claimed_amount) }}</p>
							<p class="text-[9px] font-black uppercase tracking-widest" :class="getStatusColor(claim.status)">{{ claim.status }}</p>
						</div>
						<button class="text-gray-300 hover:text-primary transition-colors">
							<span class="material-symbols-outlined">chevron_right</span>
						</button>
					</div>
				</div>
			</div>

			<!-- Sidebar -->
			<div class="lg:col-span-4 space-y-10">
				<!-- Distribution -->
				<div class="premium-card !p-8">
					<p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mb-6">Distribution</p>
					<div class="space-y-4">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="w-2 h-2 rounded-full bg-gray-900"></div>
								<span class="text-[11px] font-bold text-gray-900">Travel</span>
							</div>
							<span class="text-[11px] font-black text-gray-900">42%</span>
						</div>
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="w-2 h-2 rounded-full bg-emerald-500"></div>
								<span class="text-[11px] font-bold text-gray-900">Dining</span>
							</div>
							<span class="text-[11px] font-black text-gray-900">28%</span>
						</div>
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="w-2 h-2 rounded-full bg-gray-300"></div>
								<span class="text-[11px] font-bold text-gray-900">Other</span>
							</div>
							<span class="text-[11px] font-black text-gray-900">30%</span>
						</div>
					</div>
				</div>

				<!-- Policy Reminder -->
				<div class="premium-card !p-8 bg-amber-50 border-amber-100">
					<div class="flex items-start gap-4">
						<span class="material-symbols-outlined text-amber-600 text-xl shrink-0">info</span>
						<div>
							<p class="text-sm font-black text-gray-900 tracking-tight mb-2">Policy Reminder</p>
							<p class="text-[11px] font-bold text-gray-500 leading-relaxed">All claims over $500 require a digital tax invoice and secondary partner approval.</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- New Claim Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div v-if="showClaimModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
					<div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showClaimModal = false"></div>
					<div class="relative bg-white rounded-4xl p-10 w-full max-w-2xl shadow-2xl border border-gray-50">
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 tracking-tight">Submit Claim</h3>
								<p class="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Personnel Reimbursement Form</p>
							</div>
							<button @click="showClaimModal = false" class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 hover:text-gray-900 transition-all">
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div class="grid grid-cols-2 gap-8">
							<div class="col-span-2">
								<label class="status-label">Expense Category</label>
								<select class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none">
									<option value="" disabled selected>Search or select category...</option>
									<option>Travel & Commute</option>
									<option>Food & Client Dining</option>
									<option>Office & Tooling</option>
									<option>Telecommunications</option>
									<option>Other Expenses</option>
								</select>
							</div>
							<div>
								<label class="status-label">Total Amount ($)</label>
								<input type="number" placeholder="0.00" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all font-mono" />
							</div>
							<div>
								<label class="status-label">Receipt Date</label>
								<input type="date" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all" />
							</div>
							<div class="col-span-2">
								<label class="status-label">Brief Description</label>
								<textarea rows="3" placeholder="Describe the context of this expense..." class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"></textarea>
							</div>
							<div class="col-span-2">
								<label class="status-label">Verification Receipt</label>
								<div class="border-4 border-dashed border-gray-100 rounded-3xl p-10 flex flex-col items-center justify-center hover:bg-emerald-50 hover:border-emerald-100 group transition-all cursor-pointer">
									<div class="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-gray-300 group-hover:text-emerald-500 shadow-sm mb-4 transition-all">
										<span class="material-symbols-outlined text-3xl">upload_file</span>
									</div>
									<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest group-hover:text-emerald-600 transition-all">
										Drag and Drop or <span class="text-primary underline">Choose File</span>
									</p>
								</div>
							</div>
						</div>

						<div class="flex gap-4 mt-12">
							<button @click="showClaimModal = false" class="flex-1 py-4 text-gray-400 font-black text-xs uppercase tracking-widest hover:text-gray-900 transition-all">Dismiss</button>
							<button class="flex-[1.5] py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald">Finalize Submission</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useExpenseStore } from "@/stores/expense";
import { useEmployeeStore } from "@/stores/employee";

const expenseStore = useExpenseStore();
const employeeStore = useEmployeeStore();

const showClaimModal = ref(false);
const activeFilter = ref("All Claims");

const stats = ref({
	total_reimbursed: 14290.50,
	pending_amount: 2840.00,
	total_spent: 13080,
	budget_limit: 20000,
});

const mockClaims = [
	{
		name: "EXP-2024-001",
		title: "Business Trip: Antwerp Diamond Fair",
		expense_type: "Travel",
		category: "Travel & Logistics",
		posting_date: "2023-10-14",
		total_claimed_amount: 1450.00,
		status: "Pending",
	},
	{
		name: "EXP-2024-002",
		title: "Client Dinner: VVIP Stakeholder",
		expense_type: "Dining",
		category: "Food & Dining",
		posting_date: "2023-10-12",
		total_claimed_amount: 420.50,
		status: "Approved",
	},
	{
		name: "EXP-2024-003",
		title: "Specialist Tools: Loupe & Precision Tweezers",
		expense_type: "Tools",
		category: "Atelier Supplies",
		posting_date: "2023-10-09",
		total_claimed_amount: 890.00,
		status: "Approved",
	},
	{
		name: "EXP-2024-004",
		title: "Insured Shipping: GIA Certifications",
		expense_type: "Shipping",
		category: "Logistics",
		posting_date: "2023-10-05",
		total_claimed_amount: 125.00,
		status: "Rejected",
	},
];

const filteredClaims = computed(() => {
	const claims = expenseStore.expenseClaims.length > 0 ? expenseStore.expenseClaims : mockClaims;
	if (activeFilter.value === "All Claims") return claims;
	return claims.filter((c) => c.status === activeFilter.value);
});

function getTypeIcon(type) {
	const icons = {
		Travel: "flight",
		Dining: "restaurant",
		Tools: "inventory_2",
		Shipping: "local_shipping",
	};
	return icons[type] || "receipt_long";
}

function getStatusColor(status) {
	const colors = {
		Approved: "text-emerald-600",
		Pending: "text-amber-600",
		Rejected: "text-red-600",
	};
	return colors[status] || "text-gray-400";
}

function formatCurrency(amount) {
	if (amount === null || amount === undefined) return "$0";
	return new Intl.NumberFormat("en-US", {
		style: "currency",
		currency: "USD",
		minimumFractionDigits: 2,
	}).format(amount);
}

function formatDate(dateStr) {
	if (!dateStr) return "";
	return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

onMounted(async () => {
	await employeeStore.init();
	if (employeeStore.employee?.name) {
		expenseStore.init(employeeStore.employee.name);
	}
});
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: scale(0.95); }

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
