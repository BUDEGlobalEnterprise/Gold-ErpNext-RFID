<template>
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
						@click="openNewIssueModal"
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
				<div class="premium-card !p-8 flex flex-col justify-between shadow-sm">
					<p class="status-label">Added This Month</p>
					<p
						class="text-[32px] font-black text-gray-900 dark:text-white tracking-tighter tabular-nums mb-4"
					>
						{{ issuesStore.employeeGrievanceStats.added_this_month }} Cases
					</p>
					<div class="premium-tag tag-emerald">
						<span class="material-symbols-outlined text-[14px]">add_circle</span>
						Employee Issues Added
					</div>
				</div>

				<div class="premium-card !p-8 flex flex-col justify-between shadow-sm">
					<p class="status-label">Resolved This Month</p>
					<p
						class="text-[32px] font-black text-gray-900 dark:text-white tracking-tighter tabular-nums mb-4"
					>
						{{ issuesStore.employeeGrievanceStats.resolved_this_month }} Cases
					</p>
					<div class="premium-tag tag-emerald">
						<span class="material-symbols-outlined text-[14px]">check_circle</span>
						Resolved for this month
					</div>
				</div>

				<div class="premium-card !p-8 flex flex-col justify-between shadow-sm">
					<p class="status-label">Investigated</p>
					<p
						class="text-[32px] font-black text-gray-900 dark:text-white tracking-tighter tabular-nums mb-4"
					>
						{{ issuesStore.employeeGrievanceStats.investigated }} Cases
					</p>
					<div class="premium-tag tag-amber">
						<span class="material-symbols-outlined text-[14px]">search</span>
						Under Investigation
					</div>
				</div>

				<div class="premium-card !p-8 flex flex-col justify-between shadow-sm">
					<p class="status-label">Open Issues</p>
					<p
						class="text-[32px] font-black text-gray-900 dark:text-white tracking-tighter tabular-nums mb-4"
					>
						{{ issuesStore.employeeGrievanceStats.open }} Cases
					</p>
					<div class="premium-tag tag-blue">
						<span class="material-symbols-outlined text-[14px]">schedule</span>
						Awaiting Action
					</div>
				</div>
			</div>

			<div class="premium-card !p-0 !overflow-visible border border-gray-100 dark:border-gray-800 shadow-sm">
				<!-- Table Header -->
				<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 px-10 py-6 border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-white/[0.02] rounded-t-2xl">
					<h3 class="text-sm font-black text-gray-900 dark:text-white tracking-tight">
						Issues
					</h3>
					<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto">
						<!-- Status Filter Dropdown -->
						<select
							v-model="selectedStatus"
							class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto cursor-pointer"
							style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
						>
							<option value="" class="dark:bg-gray-900">All Statuses</option>
							<option v-for="opt in issuesStore.grievanceStatuses" :key="opt.value" :value="opt.value" class="dark:bg-gray-900">
								{{ opt.label }}
							</option>
						</select>

						<!-- Employee Filter Dropdown (HR Manager Only) -->
						<select
							v-if="issuesStore.isHRManager"
							v-model="selectedEmployee"
							class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto cursor-pointer"
							style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
						>
							<option value="" class="dark:bg-gray-900">All Employees</option>
							<option v-for="emp in issuesStore.grievanceEmployees" :key="emp.name" :value="emp.name" class="dark:bg-gray-900">
								{{ emp.employee_name }}
							</option>
						</select>

						<!-- Month/Year Filter Dropdown -->
						<select
							v-model="selectedMonthYear"
							class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto cursor-pointer"
							style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
						>
							<option v-for="opt in monthOptions" :key="opt.value" :value="opt.value" class="dark:bg-gray-900">
								{{ opt.label }}
							</option>
						</select>

						<!-- Reset Filters Button -->
						<button
							v-if="selectedStatus !== '' || selectedEmployee !== (employeeStore.employee?.name || '') || selectedMonthYear !== currentMonthYear"
							@click="resetFilters"
							class="px-3 py-1.5 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 text-[10px] font-black uppercase tracking-widest text-red-500 transition-all flex items-center justify-center gap-1.5 w-full sm:w-auto"
						>
							<span class="material-symbols-outlined text-sm">filter_alt_off</span>
							Clear
						</button>
					</div>
				</div>

				<!-- Table -->
				<div class="overflow-x-auto">
					<table class="w-full min-w-max text-left">
						<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-white/[0.02]">
							<tr>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Reference</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Employee Name</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Date</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Status</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-50 dark:divide-gray-800">
							<tr v-for="ticket in filteredTickets" :key="ticket.name" class="transition-colors hover:bg-gray-50/50 dark:hover:bg-white/[0.02]">
								<td class="px-10 py-6">
									<span 
										@click="openDetailModal(ticket)"
										class="text-sm font-bold text-primary dark:text-emerald-400 hover:underline cursor-pointer transition-all"
									>
										{{ ticket.name }}
									</span>
								</td>
								<td class="px-10 py-6">
									<p class="text-sm font-bold text-gray-900 dark:text-white">{{ ticket.employee_name }}</p>
								</td>
								<td class="px-10 py-6">
									<p class="text-sm font-medium text-gray-650 dark:text-gray-300">{{ formatDate(ticket.date) }}</p>
								</td>
								<td class="px-10 py-6 text-center">
									<span
										class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest"
										:class="getStatusStyle(ticket.status)"
									>
										{{ ticket.status }}
									</span>
								</td>
								<td class="px-10 py-6 text-center relative">
									<button @click.stop="toggleActionMenu(ticket.name)" class="more_vert px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 border border-gray-200 dark:border-gray-700 hover:bg-gray-55 dark:hover:bg-gray-800 mx-auto">
										<span>More</span>
										<span class="material-symbols-outlined text-xs">expand_more</span>
									</button>
									
									<div v-if="activeActionMenu === ticket.name" class="dropdown-menu absolute right-12 top-14 z-30 w-36 py-1.5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden">
										<button v-if="ticket.status === 'Open' && ticket.raised_by === employeeStore.employee?.name" @click="handleEdit(ticket)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">edit</span>Edit
										</button>
										<button v-if="ticket.status === 'Open' && ticket.raised_by !== employeeStore.employee?.name" @click="handleInvestigate(ticket)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">search</span>Investigate
										</button>
										<button v-if="['Open', 'Investigated'].includes(ticket.status) && ticket.raised_by !== employeeStore.employee?.name" @click="handleResolve(ticket)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">verified</span>Resolve
										</button>
										<button @click="handleDelete(ticket.name)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">delete</span>Delete
										</button>
									</div>
								</td>
							</tr>
							<tr v-if="filteredTickets.length === 0">
								<td colspan="5" class="px-10 py-20 text-center">
									<div class="w-16 h-16 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-300 dark:text-gray-600 mx-auto mb-4">
										<span class="material-symbols-outlined text-3xl">support_agent</span>
									</div>
									<p class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">
										No issues found
									</p>
								</td>
							</tr>
						</tbody>
					</table>
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
						@click="closeIssueModal"
					></div>
					<div
						class="relative bg-white dark:bg-[#0a0c1a] rounded-4xl p-10 w-full max-w-xl shadow-2xl border border-gray-50 transform transition-all max-h-[90vh] overflow-y-auto no-scrollbar"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 tracking-tight">
									{{ isEditing ? 'Edit Issue' : 'Report Issue' }}
								</h3>
								<p
									class="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1"
								>
									{{ isEditing ? 'Employee Issue Update' : 'Employee Issue Submission' }}
								</p>
							</div>
							<button
								@click="closeIssueModal"
								class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div class="space-y-6">
							<div>
								<label class="status-label">Employee Name</label>
								<div class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-500 font-bold text-sm">
									{{ employeeStore.employee?.employee_name || 'Loading...' }}
								</div>
							</div>

							<div>
								<label class="status-label">Subject <span class="text-red-500 font-bold">*</span></label>
								<input
									v-model="newIssue.subject"
									type="text"
									placeholder="Brief summary of your concern..."
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
								/>
							</div>

							<div>
								<label class="status-label">Date <span class="text-red-500 font-bold">*</span></label>
								<input
									v-model="newIssue.date"
									type="date"
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
								/>
							</div>

							<div class="grid gap-6" :class="newIssue.grievance_against_party ? 'grid-cols-2' : 'grid-cols-1'">
								<div>
									<label class="status-label">Issue Against Party <span class="text-red-500 font-bold">*</span></label>
									<select
										v-model="newIssue.grievance_against_party"
										@change="onGrievanceAgainstPartyChange"
										class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
									>
										<option value="" disabled>Select party...</option>
										<option
											v-for="party in grievanceParties"
											:key="party"
											:value="party"
										>
											{{ party }}
										</option>
									</select>
								</div>
								<div v-if="newIssue.grievance_against_party">
									<label class="status-label">Issue Against <span class="text-red-500 font-bold">*</span></label>
									<select
										v-model="newIssue.grievance_against"
										class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
									>
										<option value="" disabled>Select target...</option>
										<option
											v-for="opt in grievanceAgainstOptions"
											:key="opt.value"
											:value="opt.value"
										>
											{{ opt.label }}
										</option>
									</select>
								</div>
							</div>

							<div>
								<label class="status-label">Issue Type <span class="text-red-500 font-bold">*</span></label>
								<select
									v-model="newIssue.grievance_type"
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select type...</option>
									<option
										v-for="opt in issuesStore.grievanceTypes"
										:key="opt.value"
										:value="opt.value"
									>
										{{ opt.label }}
									</option>
								</select>
							</div>

							<div>
								<label class="status-label">Detailed Description <span class="text-red-500 font-bold">*</span></label>
								<textarea
									v-model="newIssue.description"
									rows="4"
									placeholder="Provide detailed description of your issue..."
									class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 text-gray-900 font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
								></textarea>
							</div>
						</div>

						<!-- Error Message -->
						<div v-if="submitIssueError" class="mt-6 p-4 rounded-xl bg-red-50 border border-red-100 text-left">
							<p class="text-xs font-semibold text-red-650">
								{{ submitIssueError }}
							</p>
						</div>

						<div class="flex gap-4 mt-8">
							<button
								@click="closeIssueModal"
								class="flex-1 py-4 text-gray-400 font-black text-xs uppercase tracking-widest transition-all"
							>
								Dismiss
							</button>
							<button
								@click="submitIssue"
								:disabled="!canSubmitIssue"
								class="flex-[1.5] py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald disabled:opacity-50"
							>
								{{ isEditing ? 'Update Issue' : 'Finalize Submission' }}
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

		<!-- Issue Details Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showDetailModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showDetailModal = false"
					></div>
					<div
						class="relative bg-white dark:bg-[#0a0c1a] rounded-4xl p-6 sm:p-10 w-full max-w-3xl shadow-2xl border border-gray-50 dark:border-gray-800 max-h-[95vh] overflow-y-auto no-scrollbar"
					>
						<div class="flex items-center justify-between mb-8">
							<div>
								<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
									Issue Details
								</h3>
								<p class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mt-1">
									Grievance Record Overview
								</p>
							</div>
							<button
								@click="showDetailModal = false"
								class="w-12 h-12 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div v-if="currentDetail" class="space-y-8">
							<!-- Reference ID & Status Header -->
							<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-100 dark:border-gray-800">
								<div>
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Reference ID</span>
									<p class="text-lg font-black text-gray-900 dark:text-white mt-1">{{ currentDetail.name }}</p>
								</div>
								<div class="flex items-center gap-4 relative">
									<span
										class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest"
										:class="getStatusStyle(currentDetail.status)"
									>
										{{ currentDetail.status }}
									</span>
									<button @click.stop="toggleActionMenu(currentDetail.name)" class="more_vert px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 border border-gray-200 dark:border-gray-700 hover:bg-gray-55 dark:hover:bg-gray-800 mx-auto">
										<span>More</span>
										<span class="material-symbols-outlined text-xs">expand_more</span>
									</button>
									<div v-if="activeActionMenu === currentDetail.name" class="dropdown-menu absolute right-0 top-12 z-30 w-36 py-1.5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden text-left">
										<button v-if="currentDetail.status === 'Open' && currentDetail.raised_by === employeeStore.employee?.name" @click="handleEdit(currentDetail); showDetailModal = false" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">edit</span>Edit
										</button>
										<button v-if="currentDetail.status === 'Open' && currentDetail.raised_by !== employeeStore.employee?.name" @click="handleInvestigate(currentDetail); showDetailModal = false" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">search</span>Investigate
										</button>
										<button v-if="['Open', 'Investigated'].includes(currentDetail.status) && currentDetail.raised_by !== employeeStore.employee?.name" @click="handleResolve(currentDetail); showDetailModal = false" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">verified</span>Resolve
										</button>
										<button @click="handleDelete(currentDetail.name); showDetailModal = false" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2">
											<span class="material-symbols-outlined text-sm">delete</span>Delete
										</button>
									</div>
								</div>
							</div>

							<!-- Core Fields Grid -->
							<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
								<!-- Employee Name -->
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Employee</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.employee_name }}</p>
									<p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ currentDetail.raised_by }}</p>
								</div>

								<!-- Subject -->
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Subject</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.subject }}</p>
								</div>

								<!-- Date -->
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Date</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ formatDate(currentDetail.date) }}</p>
								</div>

								<!-- Issue Type -->
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Issue Type</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.issue_type }}</p>
								</div>

								<!-- Issue Against Party -->
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Issue Against Party</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.grievance_against_party }}</p>
								</div>

								<!-- Issue Against -->
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Issue Against</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.grievance_against }}</p>
								</div>

								<!-- Designation -->
								<div v-if="currentDetail.designation" class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Designation</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.designation }}</p>
								</div>

								<!-- Reports To -->
								<div v-if="currentDetail.reports_to" class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Reports To</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.reports_to }}</p>
								</div>

								<!-- Associated Document Type -->
								<div v-if="currentDetail.associated_document_type" class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Associated Document Type</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.associated_document_type }}</p>
								</div>

								<!-- Associated Document -->
								<div v-if="currentDetail.associated_document" class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Associated Document</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.associated_document }}</p>
								</div>
							</div>

							<!-- Description -->
							<div class="bg-gray-50/30 dark:bg-white/[0.01] p-5 rounded-2xl border border-gray-100 dark:border-gray-800">
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Detailed Description</span>
								<p class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2 whitespace-pre-wrap leading-relaxed text-left">
									{{ currentDetail.description || 'No description provided.' }}
								</p>
							</div>

							<!-- Investigation Details (Shown for Investigated & Resolved statuses) -->
							<div v-if="['Investigated', 'Resolved'].includes(currentDetail.status) && currentDetail.cause_of_grievance" class="bg-gray-50/30 dark:bg-white/[0.01] p-5 rounded-2xl border border-gray-100 dark:border-gray-800 text-left">
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Cause of Issue (Investigation)</span>
								<p class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2 whitespace-pre-wrap leading-relaxed">
									{{ currentDetail.cause_of_grievance }}
								</p>
							</div>

							<!-- Resolution Details (Shown only for Resolved status) -->
							<div v-if="currentDetail.status === 'Resolved'" class="space-y-6 text-left">
								<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
									<div class="bg-emerald-50/20 dark:bg-emerald-950/10 p-5 rounded-2xl border border-emerald-100/30 dark:border-emerald-950/20">
										<span class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">Resolved By</span>
										<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.resolved_by }}</p>
									</div>
									<div class="bg-emerald-50/20 dark:bg-emerald-950/10 p-5 rounded-2xl border border-emerald-100/30 dark:border-emerald-950/20">
										<span class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">Resolution Date</span>
										<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ formatDate(currentDetail.resolution_date) }}</p>
									</div>
									<!-- Employee Responsible -->
									<div v-if="currentDetail.employee_responsible" class="bg-emerald-50/20 dark:bg-emerald-950/10 p-5 rounded-2xl border border-emerald-100/30 dark:border-emerald-950/20">
										<span class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">Employee Responsible</span>
										<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.employee_responsible }}</p>
									</div>
								</div>
								<div v-if="currentDetail.resolution_detail" class="bg-emerald-50/10 dark:bg-emerald-950/5 p-5 rounded-2xl border border-emerald-100/20 dark:border-emerald-950/10">
									<span class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">Resolution Details</span>
									<p class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2 whitespace-pre-wrap leading-relaxed">
										{{ currentDetail.resolution_detail }}
									</p>
								</div>
							</div>
						</div>

						<div class="flex gap-4 mt-8">
							<button
								@click="showDetailModal = false"
								class="w-full py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald hover:opacity-90 transition-all flex items-center justify-center gap-2"
							>
								Close Details
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

		<!-- Investigate Issue Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showInvestigateModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showInvestigateModal = false"
					></div>
					<div
						class="relative bg-white dark:bg-[#0a0c1a] rounded-4xl p-10 w-full max-w-xl shadow-2xl border border-gray-50 dark:border-gray-800 transform transition-all max-h-[90vh] overflow-y-auto no-scrollbar"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
									Investigate Issue
								</h3>
								<p
									class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mt-1"
								>
									Record Cause of Grievance
								</p>
							</div>
							<button
								@click="showInvestigateModal = false"
								class="w-12 h-12 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div v-if="investigateTicket" class="space-y-6">
							<!-- Hidden/Hidden-like data fields -->
							<div class="grid grid-cols-2 gap-4 pb-4 border-b border-gray-100 dark:border-gray-800">
								<div>
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Issue ID</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ investigateTicket.name }}</p>
								</div>
								<div>
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Employee</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ investigateTicket.employee_name }}</p>
								</div>
							</div>

							<div>
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Subject</span>
								<p class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-1">{{ investigateTicket.subject }}</p>
							</div>

							<!-- Cause of Issue Field -->
							<div>
								<label class="status-label">Cause of Issue <span class="text-red-500 font-bold">*</span></label>
								<textarea
									v-model="causeOfIssue"
									rows="4"
									placeholder="Provide the cause/reason for this issue..."
									class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
								></textarea>
							</div>
						</div>

						<!-- Error Message -->
						<div v-if="investigateError" class="mt-6 p-4 rounded-xl bg-red-50 border border-red-100 text-left">
							<p class="text-xs font-semibold text-red-650">
								{{ investigateError }}
							</p>
						</div>

						<div class="flex gap-4 mt-8">
							<button
								@click="showInvestigateModal = false"
								class="flex-1 py-4 text-gray-400 dark:text-gray-500 font-black text-xs uppercase tracking-widest transition-all"
							>
								Dismiss
							</button>
							<button
								@click="submitInvestigation"
								:disabled="!causeOfIssue.trim()"
								class="flex-[1.5] py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald disabled:opacity-50"
							>
								Save Investigation
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

		<!-- Resolve Issue Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showResolveModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showResolveModal = false"
					></div>
					<div
						class="relative bg-white dark:bg-[#0a0c1a] rounded-4xl p-10 w-full max-w-xl shadow-2xl border border-gray-50 dark:border-gray-800 transform transition-all max-h-[90vh] overflow-y-auto no-scrollbar"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
									Resolve Issue
								</h3>
								<p
									class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mt-1"
								>
									Record Issue Resolution Details
								</p>
							</div>
							<button
								@click="showResolveModal = false"
								class="w-12 h-12 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div v-if="resolveTicket" class="space-y-6">
							<!-- Hidden/Hidden-like data fields -->
							<div class="grid grid-cols-2 gap-4 pb-4 border-b border-gray-100 dark:border-gray-800">
								<div>
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Issue ID</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ resolveTicket.name }}</p>
								</div>
								<div>
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Employee</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ resolveTicket.employee_name }}</p>
								</div>
							</div>

							<div>
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Subject</span>
								<p class="text-sm font-medium text-gray-755 dark:text-gray-300 mt-1">{{ resolveTicket.subject }}</p>
							</div>

							<!-- Resolved By Dropdown (System Users) -->
							<div>
								<label class="status-label">Resolved By <span class="text-red-500 font-bold">*</span></label>
								<select
									v-model="resolvedBy"
									class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select resolver...</option>
									<option
										v-for="user in issuesStore.usersList"
										:key="user.name"
										:value="user.name"
									>
										{{ user.full_name || user.name }}
									</option>
								</select>
							</div>

							<!-- Resolution Date (initially selected as today) -->
							<div>
								<label class="status-label">Resolution Date <span class="text-red-500 font-bold">*</span></label>
								<input
									v-model="resolutionDate"
									type="date"
									class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
								/>
							</div>

							<!-- Resolution Detail Description -->
							<div>
								<label class="status-label">Resolution Details <span class="text-red-500 font-bold">*</span></label>
								<textarea
									v-model="resolutionDetail"
									rows="4"
									placeholder="Provide details on how this issue was resolved..."
									class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
								></textarea>
							</div>
						</div>

						<!-- Error Message -->
						<div v-if="resolveError" class="mt-6 p-4 rounded-xl bg-red-50 border border-red-100 text-left">
							<p class="text-xs font-semibold text-red-650">
								{{ resolveError }}
							</p>
						</div>

						<div class="flex gap-4 mt-8">
							<button
								@click="showResolveModal = false"
								class="flex-1 py-4 text-gray-400 dark:text-gray-500 font-black text-xs uppercase tracking-widest transition-all"
							>
								Dismiss
							</button>
							<button
								@click="submitResolution"
								:disabled="!resolvedBy || !resolutionDate || !resolutionDetail.trim()"
								class="flex-[1.5] py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald disabled:opacity-50"
							>
								Submit Resolution
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useIssuesStore } from "@/stores/issues";
import { useEmployeeStore } from "@/stores/employee";

const getTodayDate = () => {
	return new Date().toISOString().split("T")[0];
};

function getMonthStartAndEnd(monthYearStr) {
	if (!monthYearStr) return { start: undefined, end: undefined };
	const [year, month] = monthYearStr.split("-").map(Number);
	const start = `${year}-${String(month).padStart(2, "0")}-01`;
	const lastDay = new Date(year, month, 0).getDate();
	const end = `${year}-${String(month).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;
	return { start, end };
}

function formatDate(dateStr) {
	if (!dateStr) return "";
	const date = new Date(dateStr);
	return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

const issuesStore = useIssuesStore();
const employeeStore = useEmployeeStore();

const showIssueModal = ref(false);
const showDetailModal = ref(false);
const currentDetail = ref(null);
const activeActionMenu = ref("");
const submitIssueError = ref("");

const showInvestigateModal = ref(false);
const investigateTicket = ref(null);
const causeOfIssue = ref("");
const investigateError = ref("");

const showResolveModal = ref(false);
const resolveTicket = ref(null);
const resolvedBy = ref("");
const resolutionDate = ref(getTodayDate());
const resolutionDetail = ref("");
const resolveError = ref("");

const isEditing = ref(false);
const editTicketName = ref("");

const selectedStatus = ref("");
const selectedEmployee = ref("");

const _now = new Date();
const currentMonthYear = `${_now.getFullYear()}-${String(_now.getMonth() + 1).padStart(2, '0')}`;
const selectedMonthYear = ref(currentMonthYear);

const monthOptions = computed(() => {
	const opts = [];
	const now = new Date();
	opts.push({ value: "", label: "All Months" });
	for (let offset = -12; offset <= 2; offset++) {
		const d = new Date(now.getFullYear(), now.getMonth() + offset, 1);
		const m = d.getMonth() + 1;
		const y = d.getFullYear();
		const val = `${y}-${String(m).padStart(2, '0')}`;
		opts.push({
			value: val,
			label: d.toLocaleDateString("en-US", { month: "short", year: "numeric" }),
		});
	}
	return opts;
});

const newIssue = ref({
	subject: "",
	date: getTodayDate(),
	status: "Open",
	grievance_against_party: "",
	grievance_against: "",
	grievance_type: "",
	description: "",
});

const grievanceParties = ["Company", "Department", "Employee Group", "Employee Grade", "Employee"];
const grievanceAgainstOptions = ref([]);

async function onGrievanceAgainstPartyChange() {
	newIssue.value.grievance_against = "";
	grievanceAgainstOptions.value = [];
	if (!newIssue.value.grievance_against_party) return;

	try {
		const res = await issuesStore.fetchGrievanceAgainstOptions(
			newIssue.value.grievance_against_party
		);
		grievanceAgainstOptions.value = res || [];
	} catch (e) {
		console.error(e);
	}
}

// Filtered tickets
const filteredTickets = computed(() => {
	return issuesStore.tickets;
});

const canSubmitIssue = computed(() => {
	return (
		newIssue.value.subject &&
		newIssue.value.description &&
		newIssue.value.grievance_against_party &&
		newIssue.value.grievance_against &&
		newIssue.value.grievance_type
	);
});

function resetFilters() {
	selectedStatus.value = "";
	selectedEmployee.value = employeeStore.employee?.name || "";
	selectedMonthYear.value = currentMonthYear;
}

watch(
	[selectedStatus, selectedEmployee, selectedMonthYear],
	async ([status, employee, monthYear]) => {
		const { start, end } = getMonthStartAndEnd(monthYear);
		await issuesStore.fetchTickets({
			status: status || undefined,
			employee_filter: employee || undefined,
			start_date: start,
			end_date: end,
		});
	},
	{ immediate: true }
);

function toggleActionMenu(name) {
	activeActionMenu.value = activeActionMenu.value === name ? "" : name;
}

function openDetailModal(ticket) {
	currentDetail.value = ticket;
	showDetailModal.value = true;
}

function openNewIssueModal() {
	isEditing.value = false;
	editTicketName.value = "";
	submitIssueError.value = "";
	newIssue.value = {
		subject: "",
		date: getTodayDate(),
		status: "Open",
		grievance_against_party: "",
		grievance_against: "",
		grievance_type: "",
		description: "",
	};
	grievanceAgainstOptions.value = [];
	showIssueModal.value = true;
}

function closeIssueModal() {
	showIssueModal.value = false;
	isEditing.value = false;
	editTicketName.value = "";
	submitIssueError.value = "";
	newIssue.value = {
		subject: "",
		date: getTodayDate(),
		status: "Open",
		grievance_against_party: "",
		grievance_against: "",
		grievance_type: "",
		description: "",
	};
	grievanceAgainstOptions.value = [];
}

function handleEdit(ticket) {
	activeActionMenu.value = "";
	isEditing.value = true;
	editTicketName.value = ticket.name;
	submitIssueError.value = "";

	newIssue.value.subject = ticket.subject;
	newIssue.value.description = ticket.description;
	newIssue.value.date = ticket.date || getTodayDate();
	newIssue.value.grievance_against_party = ticket.grievance_against_party;
	newIssue.value.grievance_type = ticket.issue_type;

	onGrievanceAgainstPartyChange().then(() => {
		newIssue.value.grievance_against = ticket.grievance_against;
	});

	showIssueModal.value = true;
}

async function handleDelete(name) {
	activeActionMenu.value = "";
	if (!confirm("Are you sure you want to delete this issue?")) return;

	try {
		const result = await issuesStore.deleteGrievance(name);
		if (result && result.success === false) {
			alert(result.error || "Failed to delete");
		} else {
			const { start, end } = getMonthStartAndEnd(selectedMonthYear.value);
			await issuesStore.fetchTickets({
				status: selectedStatus.value || undefined,
				employee_filter: selectedEmployee.value || undefined,
				start_date: start,
				end_date: end,
			});
		}
	} catch (err) {
		console.error("Delete failed:", err);
		alert("An error occurred while deleting the issue.");
	}
}

function handleInvestigate(ticket) {
	activeActionMenu.value = "";
	investigateTicket.value = ticket;
	causeOfIssue.value = "";
	investigateError.value = "";
	showInvestigateModal.value = true;
}

async function submitInvestigation() {
	if (!causeOfIssue.value.trim() || !investigateTicket.value) {
		investigateError.value = "Please enter the cause of the issue.";
		return;
	}
	investigateError.value = "";

	try {
		const result = await issuesStore.investigateGrievance(
			investigateTicket.value.name,
			causeOfIssue.value
		);
		if (result && result.success === false) {
			investigateError.value = result.error || "Failed to update investigation";
		} else {
			showInvestigateModal.value = false;
			investigateTicket.value = null;
			causeOfIssue.value = "";
			
			// Refetch with current filters
			const { start, end } = getMonthStartAndEnd(selectedMonthYear.value);
			await issuesStore.fetchTickets({
				status: selectedStatus.value || undefined,
				employee_filter: selectedEmployee.value || undefined,
				start_date: start,
				end_date: end,
			});
		}
	} catch (err) {
		console.error("Investigation failed:", err);
		investigateError.value = err.message || err.error || "An error occurred while updating the investigation.";
	}
}

function handleResolve(ticket) {
	activeActionMenu.value = "";
	resolveTicket.value = ticket;
	resolvedBy.value = "";
	resolutionDate.value = getTodayDate();
	resolutionDetail.value = "";
	resolveError.value = "";
	showResolveModal.value = true;
}

async function submitResolution() {
	if (!resolvedBy.value || !resolutionDate.value || !resolutionDetail.value.trim() || !resolveTicket.value) {
		resolveError.value = "Please fill in all mandatory fields.";
		return;
	}
	resolveError.value = "";

	try {
		const result = await issuesStore.resolveGrievance(
			resolveTicket.value.name,
			resolvedBy.value,
			resolutionDate.value,
			resolutionDetail.value
		);
		if (result && result.success === false) {
			resolveError.value = result.error || "Failed to submit resolution";
		} else {
			showResolveModal.value = false;
			resolveTicket.value = null;
			resolvedBy.value = "";
			resolutionDetail.value = "";
			
			// Refetch with current filters
			const { start, end } = getMonthStartAndEnd(selectedMonthYear.value);
			await issuesStore.fetchTickets({
				status: selectedStatus.value || undefined,
				employee_filter: selectedEmployee.value || undefined,
				start_date: start,
				end_date: end,
			});
		}
	} catch (err) {
		console.error("Resolution failed:", err);
		resolveError.value = err.message || err.error || "An error occurred while resolving the issue.";
	}
}

// Actions
async function submitIssue() {
	if (!canSubmitIssue.value) {
		submitIssueError.value = "Please fill in all mandatory fields.";
		return;
	}
	submitIssueError.value = "";

	const payload = {
		subject: newIssue.value.subject,
		description: newIssue.value.description,
		date: newIssue.value.date,
		status: "Open",
		grievance_against_party: newIssue.value.grievance_against_party,
		grievance_against: newIssue.value.grievance_against,
		grievance_type: newIssue.value.grievance_type,
	};
	if (isEditing.value) {
		payload.name = editTicketName.value;
	}

	try {
		const result = await issuesStore.createGrievance(payload);
		if (result && result.success === false) {
			submitIssueError.value = result.error || "Failed to submit issue.";
			return;
		}

		// Refetch with current filters
		const { start, end } = getMonthStartAndEnd(selectedMonthYear.value);
		await issuesStore.fetchTickets({
			status: selectedStatus.value || undefined,
			employee_filter: selectedEmployee.value || undefined,
			start_date: start,
			end_date: end,
		});

		// Reset form
		showIssueModal.value = false;
		isEditing.value = false;
		editTicketName.value = "";
		newIssue.value = {
			subject: "",
			date: getTodayDate(),
			status: "Open",
			grievance_against_party: "",
			grievance_against: "",
			grievance_type: "",
			description: "",
		};
		grievanceAgainstOptions.value = [];
	} catch (err) {
		console.error("Submission failed:", err);
		submitIssueError.value = err.message || err.error || "An error occurred while submitting the issue.";
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
	const s = status?.toLowerCase();
	if (s === "resolved" || s === "closed") {
		return "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400";
	} else if (s === "open" || s === "replied") {
		return "bg-blue-100 text-blue-700 dark:bg-blue-950/30 dark:text-blue-400";
	} else if (s === "investigated") {
		return "bg-amber-100 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400";
	} else if (s === "cancelled" || s === "invalid") {
		return "bg-red-100 text-red-700 dark:bg-red-950/20 dark:text-red-400";
	} else {
		return "bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-gray-400";
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

onMounted(async () => {
	window.addEventListener("click", (e) => {
		if (!e.target.closest(".more_vert") && !e.target.closest(".dropdown-menu")) {
			activeActionMenu.value = "";
		}
	});

	await employeeStore.init();
	if (employeeStore.employee?.name) {
		selectedEmployee.value = employeeStore.employee.name;
	}
	issuesStore.init();
});
</script>
