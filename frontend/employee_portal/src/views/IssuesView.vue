<template>
	<div class="h-full flex flex-col gap-10 no-scrollbar overflow-y-auto pb-20">
		<!-- Header Redesigned -->
		<div class="shrink-0 px-2">
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<h1
						class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3"
					>
						Support & Helpdesk
					</h1>
					<p class="text-gray-500 font-medium font-sans">
						Get assistance from HR or report workspace issues with precision.
					</p>
				</div>
				<div class="flex items-center gap-4">
					<button
						class="px-6 py-3 bg-white border border-gray-100 rounded-xl text-[10px] font-black uppercase tracking-widest text-gray-400 transition-all flex items-center gap-3 shadow-sm"
					>
						<span class="material-symbols-outlined text-lg">contact_support</span>
						Documentation
					</button>
					<button
						@click="showIssueModal = true"
						class="px-8 py-3 bg-primary text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-glow-emerald transition-all"
					>
						Report New Issue
					</button>
				</div>
			</div>
		</div>

		<div class="space-y-10">
			<!-- Metrics Row Redesigned -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-8">
				<!-- Large Resolved Card -->
				<div
					class="md:col-span-1 premium-card !p-8 bg-emerald-950 text-white shadow-glow-emerald flex flex-col justify-between min-h-[220px] group transition-transform"
				>
					<div class="flex items-center gap-3">
						<span
							class="text-[10px] font-black uppercase tracking-[0.25em] text-white/40"
							>Resolved Tickets</span
						>
					</div>
					<div>
						<p
							class="text-[48px] font-black tracking-tighter leading-none mb-2 tabular-nums"
						>
							{{ issuesStore.ticketStats.closed }}
						</p>
						<p class="text-[9px] font-black uppercase tracking-[0.2em] text-white/30">
							Successfully Closed Cases
						</p>
					</div>
				</div>

				<div class="premium-card !p-8 flex flex-col justify-between shadow-sm">
					<p class="status-label">Open Tickets</p>
					<p
						class="text-[32px] font-black text-gray-900 tracking-tighter tabular-nums mb-4"
					>
						{{ issuesStore.ticketStats.open }} Cases
					</p>
					<div class="premium-tag tag-amber">
						<span class="material-symbols-outlined text-[14px]">schedule</span>
						Awaiting Response
					</div>
				</div>

				<div class="premium-card !p-8 flex flex-col justify-between shadow-sm">
					<p class="status-label">Total Submissions</p>
					<p
						class="text-[32px] font-black text-gray-900 tracking-tighter tabular-nums mb-4"
					>
						{{ issuesStore.ticketStats.total }} Total
					</p>
					<div class="premium-tag tag-gray">
						<span class="material-symbols-outlined text-[14px]">history</span>
						Lifetime Data
					</div>
				</div>

				<div class="premium-card !p-8 flex flex-col justify-between shadow-sm">
					<p class="status-label">Avg. Resolution</p>
					<p
						class="text-[32px] font-black text-gray-900 tracking-tighter tabular-nums mb-4"
					>
						24 Hours
					</p>
					<div class="premium-tag tag-emerald">
						<span class="material-symbols-outlined text-[14px]">speed</span>
						SLA Target Met
					</div>
				</div>
			</div>

			<!-- Secondary Bar Redesigned -->
			<div
				class="flex items-center justify-between px-2 bg-gray-50 p-4 rounded-2xl shrink-0"
			>
				<div class="flex items-center gap-3">
					<button
						v-for="f in ['all', 'open', 'resolved']"
						:key="f"
						@click="filterTickets = f"
						class="px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
						:class="
							filterTickets === f
								? 'bg-white text-gray-900 shadow-sm'
								: 'text-gray-400 hover:text-gray-600'
						"
					>
						{{ f }}
					</button>
				</div>
				<div class="flex items-center gap-4">
					<button
						class="w-10 h-10 rounded-xl bg-white border border-gray-100 flex items-center justify-center text-gray-400 transition-all"
					>
						<span class="material-symbols-outlined text-lg">filter_list</span>
					</button>
				</div>
			</div>

			<div class="space-y-4">
				<div
					v-if="filteredTickets.length === 0"
					class="premium-card !p-20 text-center border-gray-100 shadow-sm"
				>
					<div
						class="w-16 h-16 rounded-full bg-gray-50 flex items-center justify-center text-gray-300 mx-auto mb-4"
					>
						<span class="material-symbols-outlined text-3xl">support_agent</span>
					</div>
					<p class="text-xs font-black text-gray-400 uppercase tracking-widest">
						No tickets found
					</p>
				</div>

				<div
					v-for="ticket in filteredTickets"
					:key="ticket.name"
					class="premium-card !p-8 flex flex-col md:flex-row md:items-center justify-between gap-8 border-gray-100 group transition-all shadow-sm cursor-pointer"
					@click="viewTicket(ticket)"
				>
					<div class="flex items-center gap-6">
						<div
							class="w-14 h-14 rounded-2xl bg-gray-50 flex flex-col items-center justify-center text-gray-400 transition-colors"
						>
							<span
								class="text-[9px] font-black uppercase tracking-widest leading-none mb-1"
								>{{ formatDate(ticket.creation).split(" ")[0] }}</span
							>
							<span class="text-lg font-black leading-none text-gray-900">{{
								formatDate(ticket.creation).split(" ")[1]
							}}</span>
						</div>
						<div>
							<p
								class="text-sm font-black text-gray-900 tracking-tight leading-none mb-2"
							>
								{{ ticket.subject }}
							</p>
							<div class="flex items-center gap-3">
								<span
									class="text-[10px] font-black text-gray-400 uppercase tracking-widest"
									>{{ ticket.ticket_type || "General" }}</span
								>
								<div class="w-1 h-1 rounded-full bg-gray-200"></div>
								<span
									class="text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded shadow-sm border"
									:class="getStatusStyle(ticket.status)"
									>{{ ticket.status }}</span
								>
								<div class="w-1 h-1 rounded-full bg-gray-200"></div>
								<span
									class="text-[10px] font-black uppercase tracking-widest text-red-500"
									v-if="
										ticket.priority === 'High' || ticket.priority === 'Urgent'
									"
									>{{ ticket.priority }}</span
								>
							</div>
						</div>
					</div>
					<div class="flex items-center gap-12">
						<div class="text-right">
							<p
								class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-1"
							>
								Ticket ID
							</p>
							<p class="text-lg font-black text-gray-900 tracking-tighter">
								{{ ticket.name }}
							</p>
						</div>
						<button
							class="w-12 h-12 rounded-xl bg-gray-50 flex items-center justify-center text-gray-400 transition-all"
						>
							<span class="material-symbols-outlined">chevron_right</span>
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Report Issue Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showIssueModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showIssueModal = false"
					></div>
					<div
						class="relative bg-white dark:bg-[#0a0c1a] rounded-4xl p-10 w-full max-w-xl shadow-2xl border border-gray-50 transform transition-all"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 tracking-tight">
									Report Issue
								</h3>
								<p
									class="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1"
								>
									Personnel Helpdesk Submission
								</p>
							</div>
							<button
								@click="showIssueModal = false"
								class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div class="space-y-6">
							<div>
								<label class="status-label">Issue Subject</label>
								<input
									v-model="newIssue.subject"
									type="text"
									placeholder="Brief summary of your concern..."
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
								/>
							</div>

							<div class="grid grid-cols-2 gap-6">
								<div>
									<label class="status-label">Category</label>
									<select
										v-model="newIssue.issue_type"
										class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
									>
										<option value="" disabled>Select type...</option>
										<option
											v-for="type in issuesStore.issueTypes"
											:key="type.name"
											:value="type.name"
										>
											{{ type.name }}
										</option>
										<option value="Attendance">Attendance</option>
										<option value="Payroll">Payroll</option>
										<option value="Leave">Leave</option>
										<option value="Other">Other</option>
									</select>
								</div>
								<div>
									<label class="status-label">Priority</label>
									<select
										v-model="newIssue.priority"
										class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
									>
										<option value="Low">Low</option>
										<option value="Medium">Medium</option>
										<option value="High">High</option>
										<option value="Urgent">Urgent</option>
									</select>
								</div>
							</div>

							<div>
								<label class="status-label">Detailed Description</label>
								<textarea
									v-model="newIssue.description"
									rows="4"
									placeholder="Provide enough context for our artisans to assist you..."
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
								></textarea>
							</div>
						</div>

						<div class="flex gap-4 mt-12">
							<button
								@click="showIssueModal = false"
								class="flex-1 py-4 text-gray-400 font-black text-xs uppercase tracking-widest transition-all"
							>
								Dismiss
							</button>
							<button
								@click="submitIssue"
								:disabled="!canSubmitIssue"
								class="flex-[1.5] py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald disabled:opacity-50"
							>
								Finalize Submission
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
import { useIssuesStore } from "@/stores/issues";

const issuesStore = useIssuesStore();

const showIssueModal = ref(false);
const filterTickets = ref("all");

const newIssue = ref({
	subject: "",
	description: "",
	issue_type: "",
	priority: "Medium",
});

// Filtered tickets
const filteredTickets = computed(() => {
	if (filterTickets.value === "open") {
		return issuesStore.openTickets;
	} else if (filterTickets.value === "resolved") {
		return issuesStore.resolvedTickets;
	}
	return issuesStore.tickets;
});

const canSubmitIssue = computed(() => {
	return newIssue.value.subject && newIssue.value.description;
});

// Actions
async function submitIssue() {
	if (!canSubmitIssue.value) return;

	await issuesStore.createIssue(
		newIssue.value.subject,
		newIssue.value.description,
		newIssue.value.issue_type || "Other",
		newIssue.value.priority
	);

	// Reset form
	showIssueModal.value = false;
	newIssue.value = {
		subject: "",
		description: "",
		issue_type: "",
		priority: "Medium",
	};
}

function viewTicket(ticket) {
	// Open ticket in desk or show details
	if (ticket.url) {
		window.open(ticket.url, "_blank");
	} else {
		window.open(`/app/hd-ticket/${ticket.name}`, "_blank");
	}
}

// Helpers
function getStatusDotColor(status) {
	switch (status) {
		case "Resolved":
		case "Closed":
			return "bg-emerald-glow";
		case "Open":
		case "Replied":
			return "bg-blue-400";
		default:
			return "bg-white/40";
	}
}

function getStatusStyle(status) {
	switch (status) {
		case "Resolved":
		case "Closed":
			return "bg-emerald-glow/20 text-emerald-glow";
		case "Open":
		case "Replied":
			return "bg-blue-400/20 text-blue-400";
		default:
			return "bg-white/10 text-white/40";
	}
}

function getPriorityClass(priority) {
	switch (priority) {
		case "High":
		case "Urgent":
			return "bg-red-500/15 text-red-400";
		case "Medium":
			return "bg-amber-500/15 text-amber-400";
		case "Low":
			return "bg-blue-500/15 text-blue-400";
		default:
			return "bg-white/10 text-white/50";
	}
}

function formatDate(dateStr) {
	if (!dateStr) return "";
	const date = new Date(dateStr);
	return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

onMounted(() => {
	issuesStore.init();
});
</script>
