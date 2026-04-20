<template>
	<div class="h-full flex flex-col gap-10 no-scrollbar overflow-y-auto pb-20">
		<!-- Header -->
		<div class="shrink-0 px-2">
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<h1 class="text-4xl font-black text-gray-900 tracking-tight leading-none mb-3">
						Leave Management
					</h1>
					<p class="text-gray-500 font-medium font-sans">
						Review your balance, track applications, and request time off.
					</p>
				</div>
				<div class="flex items-center gap-4">
					<button
						@click="showLeaveModal = true"
						class="px-8 py-3 bg-primary text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-glow-emerald transition-all flex items-center gap-2"
					>
						<span class="material-symbols-outlined text-lg">add</span>
						Request Leave
					</button>
				</div>
			</div>
		</div>

		<div class="space-y-10">
			<!-- Metrics Row -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-8">
				<!-- Annual Leave Balance -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-gray-400 text-xl"
							>calendar_today</span
						>
						<span
							class="text-[10px] font-black text-gray-400 uppercase tracking-widest"
							>Annual</span
						>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 tracking-tighter leading-none"
							>14.5</span
						>
						<span class="text-sm font-bold text-gray-400 mb-1">Days</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">
						Balance Available
					</p>
					<div class="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
						<div class="h-full bg-emerald-600 rounded-full" style="width: 69%"></div>
					</div>
				</div>

				<!-- Sick Leave -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-red-500 text-xl"
							>local_hospital</span
						>
						<span
							class="text-[10px] font-black text-gray-400 uppercase tracking-widest"
							>Sick</span
						>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 tracking-tighter leading-none"
							>06</span
						>
						<span class="text-sm font-bold text-gray-400 mb-1">Days</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">
						Yearly Quota
					</p>
					<div class="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
						<div class="h-full bg-red-500 rounded-full" style="width: 40%"></div>
					</div>
				</div>

				<!-- Pending -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-amber-600 text-xl"
							>pending_actions</span
						>
						<span
							class="text-[10px] font-black text-gray-400 uppercase tracking-widest"
							>Pending</span
						>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 tracking-tighter leading-none"
							>02</span
						>
						<span class="text-sm font-bold text-gray-400 mb-1">Requests</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">
						Awaiting Approval
					</p>
					<div class="flex items-center gap-1.5">
						<span class="material-symbols-outlined text-amber-500 text-[14px]"
							>schedule</span
						>
						<span class="text-[10px] font-bold text-amber-600"
							>Last updated 2h ago</span
						>
					</div>
				</div>

				<!-- Utilization -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-gray-400 text-xl">update</span>
						<span
							class="text-[10px] font-black text-gray-400 uppercase tracking-widest"
							>Utilization</span
						>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 tracking-tighter leading-none"
							>18.5</span
						>
						<span class="text-sm font-bold text-gray-400 mb-1">Total</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">
						Days Used This Year
					</p>
					<div class="flex items-center gap-2">
						<span
							class="text-[10px] font-black text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded"
							>+12%</span
						>
						<span class="text-[10px] font-bold text-gray-400"
							>vs. last fiscal year</span
						>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
				<!-- Leave Applications List -->
				<div class="lg:col-span-8">
					<div
						class="premium-card !p-0 overflow-hidden border border-gray-100 shadow-sm"
					>
						<!-- Table Header -->
						<div
							class="flex items-center justify-between px-10 py-6 border-b border-gray-50 bg-gray-50/30"
						>
							<h3 class="text-sm font-black text-gray-900 tracking-tight">
								Leave Applications
							</h3>
							<div class="flex items-center gap-6">
								<button
									v-for="f in ['All', 'Pending', 'Approved']"
									:key="f"
									@click="filterHistory = f.toLowerCase()"
									class="text-[10px] font-black uppercase tracking-widest transition-all pb-1"
									:class="
										filterHistory === f.toLowerCase()
											? 'text-gray-900 border-b-2 border-gray-900'
											: 'text-gray-400 hover:text-gray-600'
									"
								>
									{{ f }}
								</button>
							</div>
						</div>

						<!-- Table -->
						<table class="w-full text-left">
							<thead class="border-b border-gray-50 bg-gray-50/30">
								<tr>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em]"
									>
										Type
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em]"
									>
										Period
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-center"
									>
										Days
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-center"
									>
										Status
									</th>
									<th
										class="px-10 py-5 text-[10px] font-black text-gray-400 uppercase tracking-[0.25em] text-right"
									>
										Actions
									</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-50">
								<tr
									v-for="app in filteredApplications"
									:key="app.name"
									class=" transition-colors"
								>
									<td class="px-10 py-6">
										<div class="flex items-center gap-3">
											<div
												class="w-1.5 h-1.5 rounded-full"
												:class="
													app.leave_type?.toLowerCase().includes('sick')
														? 'bg-amber-500'
														: 'bg-emerald-500'
												"
											></div>
											<div>
												<p class="text-sm font-bold text-gray-900">
													{{ app.leave_type }}
												</p>
												<p class="text-[10px] text-gray-400">
													{{ app.description || "Personal trip" }}
												</p>
											</div>
										</div>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-bold text-gray-900">
											{{ formatDate(app.from_date) }} -
											{{ formatDate(app.to_date) }}
										</p>
									</td>
									<td class="px-10 py-6 text-center">
										<p class="text-sm font-black text-gray-900">
											{{ app.total_leave_days || 1 }}
										</p>
									</td>
									<td class="px-10 py-6 text-center">
										<span
											class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest"
											:class="getStatusStyle(app.status)"
										>
											{{ app.status }}
										</span>
									</td>
									<td class="px-10 py-6 text-right">
										<button
											class="text-gray-400 transition-colors"
										>
											<span class="material-symbols-outlined text-lg"
												>more_horiz</span
											>
										</button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<!-- Sidebar -->
				<div class="lg:col-span-4 space-y-10">
					<!-- Calendar Mini Card -->
					<div class="premium-card !p-8">
						<div class="flex justify-between items-center mb-6">
							<h4 class="text-sm font-black text-gray-900 tracking-tight">
								October 2023
							</h4>
							<div class="flex gap-2">
								<button
									class="w-7 h-7 rounded-lg border border-gray-100 flex items-center justify-center text-gray-400 transition-all"
								>
									<span class="material-symbols-outlined text-xs"
										>chevron_left</span
									>
								</button>
								<button
									class="w-7 h-7 rounded-lg border border-gray-100 flex items-center justify-center text-gray-400 transition-all"
								>
									<span class="material-symbols-outlined text-xs"
										>chevron_right</span
									>
								</button>
							</div>
						</div>
						<StandardCalendar
							v-model="currentDate"
							:events="allEventDates"
							class="!border-0 !shadow-none"
						/>
					</div>

					<!-- Leave Policy Card -->
					<div
						class="premium-card !p-10 bg-emerald-950 text-white relative overflow-hidden"
					>
						<div
							class="absolute -bottom-10 -right-10 w-32 h-32 bg-emerald-500 rounded-full blur-[80px] opacity-20"
						></div>
						<h4
							class="text-xs font-black uppercase tracking-[0.2em] text-white/60 mb-8 relative z-10"
						>
							Leave Policy v4.2
						</h4>
						<div class="space-y-5 relative z-10">
							<div class="flex gap-4">
								<span
									class="material-symbols-outlined text-emerald-400 text-[16px] shrink-0 mt-0.5"
									>check_circle</span
								>
								<p class="text-[11px] font-bold text-white/60 leading-relaxed">
									Submit requests 3 days in advance
								</p>
							</div>
							<div class="flex gap-4">
								<span
									class="material-symbols-outlined text-emerald-400 text-[16px] shrink-0 mt-0.5"
									>check_circle</span
								>
								<p class="text-[11px] font-bold text-white/60 leading-relaxed">
									Annual leave: 21 Days/yr
								</p>
							</div>
							<div class="flex gap-4">
								<span
									class="material-symbols-outlined text-emerald-400 text-[16px] shrink-0 mt-0.5"
									>check_circle</span
								>
								<p class="text-[11px] font-bold text-white/60 leading-relaxed">
									Sick leave: 10 Days/yr
								</p>
							</div>
							<div class="flex gap-4">
								<span
									class="material-symbols-outlined text-emerald-400 text-[16px] shrink-0 mt-0.5"
									>check_circle</span
								>
								<p class="text-[11px] font-bold text-white/60 leading-relaxed">
									Contact HR for emergencies
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- New Request Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showLeaveModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showLeaveModal = false"
					></div>
					<div
						class="relative bg-white rounded-4xl p-10 w-full max-w-xl shadow-2xl border border-gray-50"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 tracking-tight">
									Request Leave
								</h3>
								<p
									class="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1"
								>
									Application for absence
								</p>
							</div>
							<button
								@click="showLeaveModal = false"
								class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div class="space-y-6">
							<div>
								<label class="status-label">Select Leave Type</label>
								<select
									v-model="newLeave.leave_type"
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select category...</option>
									<option
										v-for="lt in leaveStore.leaveTypes"
										:key="lt.name"
										:value="lt.name"
									>
										{{ lt.leave_type_name }}
									</option>
								</select>
							</div>

							<div class="grid grid-cols-2 gap-6">
								<div>
									<label class="status-label">Departure Date</label>
									<input
										v-model="newLeave.from_date"
										type="date"
										class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
									/>
								</div>
								<div>
									<label class="status-label">Return Date</label>
									<input
										v-model="newLeave.to_date"
										type="date"
										class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
									/>
								</div>
							</div>

							<div>
								<label class="status-label">Justification / Reason</label>
								<textarea
									v-model="newLeave.description"
									rows="3"
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
									placeholder="Brief explanation for the request..."
								></textarea>
							</div>
						</div>

						<div class="flex gap-4 mt-12">
							<button
								@click="showLeaveModal = false"
								class="flex-1 py-4 text-gray-400 font-black text-xs uppercase tracking-widest "
							>
								Dismiss
							</button>
							<button
								@click="submitLeave"
								:disabled="!canSubmitLeave"
								class="flex-[1.5] py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald disabled:opacity-50"
							>
								Confirm Request
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useLeaveStore } from "@/stores/leave";
import { useEmployeeStore } from "@/stores/employee";
import StandardCalendar from "@/components/StandardCalendar.vue";

const leaveStore = useLeaveStore();
const employeeStore = useEmployeeStore();

const showLeaveModal = ref(false);
const filterHistory = ref("all");
const currentDate = ref(new Date());

const newLeave = ref({
	leave_type: "",
	from_date: "",
	to_date: "",
	description: "",
});

const allEventDates = computed(() => {
	const dates = [];
	leaveStore.leaveApplications.forEach((app) => {
		const start = new Date(app.from_date);
		const end = new Date(app.to_date || app.from_date);
		for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
			dates.push(new Date(d));
		}
	});
	return dates;
});

const filteredApplications = computed(() => {
	let apps = leaveStore.leaveApplications;
	if (filterHistory.value === "pending") {
		apps = apps.filter((app) => app.status === "Open" || app.status === "Pending");
	} else if (filterHistory.value === "approved") {
		apps = apps.filter((app) => app.status === "Approved");
	}
	return apps.sort((a, b) => new Date(b.from_date) - new Date(a.from_date));
});

const canSubmitLeave = computed(() => {
	return newLeave.value.leave_type && newLeave.value.from_date && newLeave.value.to_date;
});

function getStatusStyle(status) {
	const s = status?.toLowerCase();
	if (s === "approved") return "bg-emerald-100 text-emerald-700";
	if (s === "open" || s === "pending") return "bg-amber-100 text-amber-700";
	if (s === "rejected") return "bg-red-100 text-red-700";
	return "bg-gray-100 text-gray-500";
}

function formatDate(dateStr) {
	return new Date(dateStr).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	});
}

async function submitLeave() {
	showLeaveModal.value = false;
	newLeave.value = { leave_type: "", from_date: "", to_date: "", description: "" };
}

onMounted(async () => {
	await employeeStore.init();
	const employeeId = employeeStore.employee?.name;
	if (employeeId) leaveStore.init(employeeId);
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
	transform: scale(0.98);
}

.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
</style>
