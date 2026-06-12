<template>
	<div class="max-w-7xl mx-auto space-y-12 py-4">
		<!-- Nav Tabs -->
		<div class="flex items-center gap-8 border-b border-gray-150 dark:border-gray-800 px-2 mb-6">
			<button
				@click="activeTab = 'leave_management'"
				class="pb-3 text-xs font-black uppercase tracking-[0.2em] transition-all border-b-2"
				:class="activeTab === 'leave_management' ? 'border-primary text-primary dark:text-emerald-400 font-extrabold' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'"
			>
				Leave Management
			</button>
			<button
				@click="activeTab = 'compensatory_leave'"
				class="pb-3 text-xs font-black uppercase tracking-[0.2em] transition-all border-b-2"
				:class="activeTab === 'compensatory_leave' ? 'border-primary text-primary dark:text-emerald-400 font-extrabold' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'"
			>
				Compensatory Leave
			</button>
		</div>

		<!-- Leave Management Tab Content -->
		<div v-if="activeTab === 'leave_management'" class="space-y-10">
			<!-- Header -->
			<div class="shrink-0 px-2">
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
				<div>
					<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">
						Leave Management
					</h1>
					<p class="text-gray-500 dark:text-gray-500 font-medium font-sans">
						Review your balance, track applications, and request time off.
					</p>
				</div>
				<div class="flex items-center gap-4">
					<button
						@click="showLeaveModal = true; resetForm()"
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
				<!-- Total Allocated -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-primary text-xl"
							>inventory_2</span
						>
						<span
							class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest"
						>{{ leaveTypeCount }}+ Type{{ leaveTypeCount > 1 ? 's' : '' }}</span>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 dark:text-white tracking-tighter leading-none"
						>{{ totalAllocated }}</span>
						<span class="text-sm font-bold text-gray-400 dark:text-gray-500 mb-1">Days</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-4">
						Total Allocated
					</p>
				</div>

				<!-- Annual Leave Balance -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-gray-400 dark:text-gray-500 text-xl"
							>calendar_today</span
						>
						<span
							class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest"
							>Annual</span
						>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 dark:text-white tracking-tighter leading-none"
						>{{ totalBalance }}</span>
						<span class="text-sm font-bold text-gray-400 dark:text-gray-500 mb-1">Days</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-4">
						Balance Available
					</p>
				</div>

				<!-- Pending -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-amber-600 text-xl"
							>pending_actions</span
						>
						<span
							class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest"
							>Pending</span
						>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 dark:text-white tracking-tighter leading-none"
						>{{ pendingCount }}</span>
						<span class="text-sm font-bold text-gray-400 dark:text-gray-500 mb-1">Requests</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-4">
						Awaiting Approval
					</p>
				</div>

				<!-- Utilization -->
				<div class="premium-card !p-8">
					<div class="flex items-center justify-between mb-6">
						<span class="material-symbols-outlined text-gray-400 dark:text-gray-500 text-xl">update</span>
						<span
							class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest"
							>Utilization</span
						>
					</div>
					<div class="flex items-end gap-2 mb-2">
						<span
							class="text-5xl font-black text-gray-900 dark:text-white tracking-tighter leading-none"
						>{{ totalUsed }}</span>
						<span class="text-sm font-bold text-gray-400 dark:text-gray-500 mb-1">Days</span>
					</div>
					<p class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-4">
						Used This Year
					</p>
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
				<!-- Leave Applications List -->
				<div class="lg:col-span-12">
					<div
						class="premium-card !p-0 !overflow-visible border border-gray-100 dark:border-gray-800 shadow-sm"
					>
						<!-- Table Header -->
						<!-- Table Header -->
						<div
							class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-10 py-6 border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 rounded-t-2xl"
						>
							<h3 class="text-sm font-black text-gray-900 dark:text-white tracking-tight">
								Leave Applications
							</h3>
							<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto">
								<select
									v-model="tableFilter.monthYear"
									class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto"
									style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
								>
									<option v-for="opt in monthOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
								</select>
								<select
									v-model="tableFilter.status"
									class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto"
									style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
								>
									<option value="">All Statuses</option>
									<option v-for="opt in leaveStatusOptions" :key="opt" :value="opt">{{ opt }}</option>
								</select>
								<select
									v-if="leaveStore.isApprover"
									v-model="tableFilter.employee"
									class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto"
									style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
								>
									<option value="">All Employees</option>
									<option v-for="emp in leaveStore.approvedEmployeeList" :key="emp.name" :value="emp.name">
										{{ emp.employee_name }} {{ emp.name === currEmployee ? '(Me)' : '' }}
									</option>
								</select>
							</div>
						</div>

						<!-- Table -->
						<div
							ref="tableContainer"
							class="overflow-x-auto cursor-grab"
							:class="{ 'cursor-grabbing select-none': isDragging }"
							@mousedown="handleMouseDown"
							@mouseleave="handleMouseLeave"
							@mouseup="handleMouseUp"
							@mousemove="handleMouseMove"
						>
							<table class="w-full min-w-max text-left">
								<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30">
									<tr>
										<th
											class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]"
										>
											Reference
										</th>
										<th
											class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]"
										>
											Employee Name
										</th>
										<th
											class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]"
										>
											Period
										</th>
										<th
											class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]"
										>
											Type
										</th>
										<th
											class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center"
										>
											Days
										</th>
										<th
											class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center"
										>
											Status
										</th>
										<th
											class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center"
										>
											Actions
										</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-50">
									<tr
										v-for="app in paginatedApplications"
										:key="app.name"
										class="transition-colors"
									>
										<td class="px-10 py-6">
											<button
												@click="showViewModal(app.name)"
												class="text-sm font-bold text-primary hover:text-primary/80 hover:underline focus:outline-none text-left"
											>
												{{ app.name }}
											</button>
										</td>
										<td class="px-10 py-6">
											<p class="text-sm font-bold text-gray-900 dark:text-white">
												{{ app.employee_name }}
											</p>
										</td>
										<td class="px-10 py-6">
											<p class="text-sm font-bold text-gray-900 dark:text-white">
												{{ formatDate(app.from_date) }} -
												{{ formatDate(app.to_date) }}
											</p>
										</td>
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
													<p class="text-sm font-bold text-gray-900 dark:text-white">
														{{ app.leave_type }}
													</p>
												</div>
											</div>
										</td>
										<td class="px-10 py-6 text-center">
											<p class="text-sm font-black text-gray-900 dark:text-white">
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
										<td class="px-10 py-6 text-center relative">
											<button @click.stop="toggleActionMenu(app.name)" class="more_vert px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 mx-auto">
												<span>More</span>
												<span class="material-symbols-outlined text-xs">expand_more</span>
											</button>
											
											<div v-if="activeActionMenu === app.name" class="dropdown-menu absolute right-12 top-14 z-30 w-36 py-1.5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden">
												<button v-if="app.status === 'Open'" @click="handleEdit(app)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
													<span class="material-symbols-outlined text-sm">edit</span>Edit
												</button>
												<button v-if="app.status === 'Open'" @click="handleDelete(app.name)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2">
													<span class="material-symbols-outlined text-sm">delete</span>Delete
												</button>
												<button v-if="app.status === 'Open' && canApproveLeave(app.employee)" @click="handleUpdateStatus(app.name, 'Approved')" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 flex items-center gap-2">
													<span class="material-symbols-outlined text-sm">check_circle</span>Approve
												</button>
												<button v-if="app.status === 'Open' && canApproveLeave(app.employee)" @click="handleUpdateStatus(app.name, 'Rejected')" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2">
													<span class="material-symbols-outlined text-sm">cancel</span>Reject
												</button>
											</div>
										</td>
									</tr>
								</tbody>
							</table>
						</div>

						<!-- Pagination Footer -->
						<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-10 py-5 border-t border-gray-50 dark:border-gray-800 bg-gray-50/10 rounded-b-2xl">
							<!-- Page Size Dropdown -->
							<div class="flex items-center gap-2">
								<label class="text-xs text-gray-500 dark:text-gray-500 font-bold whitespace-nowrap">Rows per page:</label>
								<div class="relative overflow-visible">
									<select v-model.number="pageSize" class="appearance-none w-20 pr-8 pl-3 py-2 text-xs font-bold cursor-pointer border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white outline-none" @change="currentPage = 1" style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;">
										<option :value="10">10</option>
										<option :value="20">20</option>
										<option :value="50">50</option>
									</select>
								</div>
							</div>

							<!-- Showing X-Y of Z and navigation buttons -->
							<div class="flex items-center justify-between sm:justify-end gap-6 flex-1">
								<span class="text-xs text-gray-500 dark:text-gray-500 font-bold tabular-nums">
									Showing {{ Math.min((currentPage - 1) * Number(pageSize) + 1, totalRecords) || 0 }} - {{ Math.min(currentPage * Number(pageSize), totalRecords) || 0 }} of {{ totalRecords }} records
								</span>
								<div class="flex items-center gap-1">
									<button 
										@click="prevPage" 
										:disabled="currentPage === 1"
										class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
									>
										<span class="material-symbols-outlined text-sm font-bold">chevron_left</span>
									</button>
									<button 
										@click="nextPage" 
										:disabled="currentPage === totalPages"
										class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
									>
										<span class="material-symbols-outlined text-sm font-bold">chevron_right</span>
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
		</div>

		<!-- Compensatory Leave Tab Content -->
		<div v-if="activeTab === 'compensatory_leave'" class="space-y-10">
			<!-- Header -->
			<div class="shrink-0 px-2">
				<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
					<div>
						<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">
							Compensatory Leave
						</h1>
						<p class="text-gray-500 dark:text-gray-500 font-medium font-sans">
							Request and manage compensatory leaves for holidays/weekends worked.
						</p>
					</div>
					<div class="flex items-center gap-4">
						<button
							@click="showCompModal = true; resetCompForm()"
							class="px-8 py-3 bg-primary text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-glow-emerald transition-all flex items-center gap-2"
						>
							<span class="material-symbols-outlined text-lg">add</span>
							Compensatory Leave Request
						</button>
					</div>
				</div>
			</div>

			<!-- Filters and Table Card -->
			<div class="space-y-10">
				<div class="premium-card !p-0 !overflow-visible border border-gray-100 dark:border-gray-800 shadow-sm">
					<!-- Table Header with Filters -->
					<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-10 py-6 border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 rounded-t-2xl">
						<h3 class="text-sm font-black text-gray-900 dark:text-white tracking-tight">
							Request History
						</h3>
						<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto">
							<select
								v-model="compFilters.monthYear"
								class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto"
								style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
							>
								<option value="">All Months</option>
								<option v-for="opt in monthOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
							</select>
							<select
								v-if="leaveStore.isApprover"
								v-model="compFilters.employee"
								class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto"
								style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
							>
								<option value="">All Employees</option>
								<option v-for="emp in leaveStore.approvedEmployeeList" :key="emp.name" :value="emp.name">
									{{ emp.employee_name }} {{ emp.name === currEmployee ? '(Me)' : '' }}
								</option>
							</select>
						</div>
					</div>

					<!-- Table -->
					<div class="overflow-x-auto">
						<table class="w-full min-w-max text-left">
							<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30">
								<tr>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Reference</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Employee</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Work Period</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Type</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Reason</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Status</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Actions</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-50">
								<tr v-for="req in compRequests" :key="req.name" class="transition-colors">
									<td class="px-10 py-6">
										<span class="text-sm font-bold text-gray-900 dark:text-white">{{ req.name }}</span>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-bold text-gray-900 dark:text-white">{{ req.employee_name }}</p>
										<p class="text-xs text-gray-400 dark:text-gray-500">{{ req.employee }}</p>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-bold text-gray-900 dark:text-white">
											{{ formatDate(req.work_from_date) }} - {{ formatDate(req.work_end_date) }}
										</p>
										<p v-if="req.half_day" class="text-xs text-amber-600 dark:text-amber-400 font-bold mt-1">
											Half Day: {{ formatDate(req.half_day_date) }}
										</p>
									</td>
									<td class="px-10 py-6">
										<span class="text-sm font-bold text-gray-900 dark:text-white">{{ req.leave_type }}</span>
									</td>
									<td class="px-10 py-6 max-w-xs truncate" :title="req.reason">
										<span class="text-sm text-gray-650 dark:text-gray-300 font-medium">{{ req.reason }}</span>
									</td>
									<td class="px-10 py-6 text-center">
										<span
											class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest"
											:class="getCompStatusStyle(req.docstatus)"
										>
											{{ getCompStatusLabel(req.docstatus) }}
										</span>
									</td>
									<td class="px-10 py-6 text-center relative">
										<button @click.stop="toggleActionMenu(req.name)" class="more_vert px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 mx-auto">
											<span>More</span>
											<span class="material-symbols-outlined text-xs">expand_more</span>
										</button>
										
										<div v-if="activeActionMenu === req.name" class="dropdown-menu absolute right-12 top-14 z-30 w-36 py-1.5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden">
											<button v-if="req.docstatus === 0" @click="handleEditComp(req)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">edit</span>Edit
											</button>
											<button v-if="req.docstatus === 0" @click="handleDeleteComp(req.name)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">delete</span>Delete
											</button>
											<button v-if="req.docstatus === 0 && canApproveComp" @click="handleApproveComp(req.name)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">check_circle</span>Approve
											</button>
											<button v-if="(req.docstatus === 0 || req.docstatus === 1) && canApproveComp" @click="handleRejectComp(req.name)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">cancel</span>Reject
											</button>
										</div>
									</td>
								</tr>
								<tr v-if="compRequests.length === 0">
									<td colspan="7" class="px-10 py-12 text-center text-sm font-bold text-gray-450 dark:text-gray-500">
										No compensatory leave requests found.
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>

		<!-- New Request Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showLeaveModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showLeaveModal = false; submitError = ''"
					></div>
					<div
						class="relative bg-white dark:bg-gray-900 rounded-4xl p-6 sm:p-10 w-full max-w-4xl shadow-2xl border border-gray-50 dark:border-gray-800 max-h-[95vh] overflow-y-auto no-scrollbar"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
									Request Leave
								</h3>
								<p class="text-xs font-bold text-gray-400 dark:text-gray-400 uppercase tracking-widest mt-1">
									Application for absence
								</p>
							</div>
							<button
								@click="showLeaveModal = false; submitError = ''"
								class="w-12 h-12 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div class="space-y-6">
							<!-- Employee -->
							<div>
								<label class="status-label dark:text-gray-300">Employee <span class="text-red-500">*</span></label>
								<select
									v-if="leaveStore.isApprover"
									v-model="newLeave.employee"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select employee...</option>
									<option
										v-for="emp in leaveStore.approvedEmployeeList"
										:key="emp.name"
										:value="emp.name"
									>
										{{ emp.employee_name }}
									</option>
								</select>
								<input
									v-else
									:value="currEmployeeName"
									readonly
									class="w-full bg-gray-100 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-500 dark:text-gray-500 font-bold text-sm cursor-not-allowed"
								/>
							</div>

							<!-- Leave Type -->
							<div>
								<div class="flex justify-between items-baseline mb-2">
									<label class="status-label !mb-0 dark:text-gray-300">Leave Type <span class="text-red-500">*</span></label>
									<span v-if="selectedLeaveTypeBalanceLabel !== null" class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-[0.15em]">
										Available: {{ selectedLeaveTypeBalanceLabel }}
									</span>
								</div>
								<select
									v-model="newLeave.leave_type"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select category...</option>
									<option
										v-for="lt in availableLeaveTypes"
										:key="lt.name"
										:value="lt.leave_type_name"
									>
										{{ lt.leave_type_name }}
									</option>
								</select>
							</div>

							<!-- Leave Approver -->
							<div v-if="newLeave.leave_approver">
								<label class="status-label dark:text-gray-300">Leave Approver</label>
								<input
									type="text"
									:value="newLeave.leave_approver"
									readonly
									class="w-full bg-gray-100 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-500 dark:text-gray-500 font-bold text-sm cursor-not-allowed"
								/>
							</div>

							<!-- From Date + To Date -->
							<div class="grid grid-cols-2 gap-6">
								<div>
									<label class="status-label dark:text-gray-300">From Date <span class="text-red-500">*</span></label>
									<input
										v-model="newLeave.from_date"
										type="date"
										class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
									/>
								</div>
								<div v-if="!newLeave.half_day">
									<label class="status-label dark:text-gray-300">To Date <span class="text-red-500">*</span></label>
									<input
										v-model="newLeave.to_date"
										type="date"
										class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
									/>
								</div>
							</div>

							<!-- Half Day -->
							<div class="flex items-center gap-3">
								<input
									type="checkbox"
									id="half_day"
									v-model="newLeave.half_day"
									@change="onHalfDayToggle"
									class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 dark:bg-gray-800 text-primary focus:ring-primary"
								/>
								<label for="half_day" class="text-sm font-bold text-gray-900 dark:text-white">Half Day</label>
							</div>

							<!-- Status (only for approvers) -->
							<div v-if="showStatus">
								<label class="status-label dark:text-gray-300">Status</label>
								<select
									v-model="newLeave.status"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="">Select status...</option>
									<option
										v-for="opt in leaveStatusOptions"
										:key="opt"
										:value="opt"
									>
										{{ opt }}
									</option>
								</select>
							</div>

							<!-- Reason -->
							<div>
								<label class="status-label dark:text-gray-300">Reason</label>
								<textarea
									v-model="newLeave.description"
									rows="3"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
									placeholder="Brief explanation for the request..."
								></textarea>
							</div>
						</div>

						<div v-if="submitError" class="mt-8 text-center text-red-500 text-sm font-bold bg-red-50 dark:bg-red-900/20 py-3 rounded-xl border border-red-100 dark:border-red-900/30">
							{{ submitError }}
						</div>
						<div class="flex gap-4" :class="submitError ? 'mt-6' : 'mt-12'">
							<button
								@click="showLeaveModal = false; submitError = ''"
								class="flex-1 py-4 text-gray-400 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 font-black text-xs uppercase tracking-widest transition-colors"
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

		<!-- View Detail Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showDetailModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showDetailModal = false"
					></div>
					<div
						class="relative bg-white dark:bg-gray-900 rounded-4xl p-6 sm:p-10 w-full max-w-2xl shadow-2xl border border-gray-50 dark:border-gray-800 max-h-[95vh] overflow-y-auto no-scrollbar"
					>
						<!-- Modal Header -->
						<div class="flex items-center justify-between mb-8 pb-4 border-b border-gray-50 dark:border-gray-850">
							<div>
								<h3 class="text-xl font-black text-gray-900 dark:text-white tracking-tight">
									Leave Application Details
								</h3>
							</div>
							
							<div class="flex items-center gap-2 relative">
								<!-- More Actions Dropdown -->
								<button 
									v-if="currentDetail"
									@click.stop="activeDetailActionMenu = !activeDetailActionMenu" 
									class="more_vert px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
								>
									<span>More</span>
									<span class="material-symbols-outlined text-xs">expand_more</span>
								</button>
								
								<div 
									v-if="activeDetailActionMenu && currentDetail" 
									class="dropdown-menu absolute right-14 top-10 z-30 w-36 py-1.5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden"
								>
									<button 
										v-if="currentDetail.status === 'Open'" 
										@click="showDetailModal = false; handleEdit(currentDetail)" 
										class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2"
									>
										<span class="material-symbols-outlined text-sm">edit</span>Edit
									</button>
									<button 
										v-if="currentDetail.status === 'Open'" 
										@click="handleDelete(currentDetail.name)" 
										class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2"
									>
										<span class="material-symbols-outlined text-sm">delete</span>Delete
									</button>
									<button 
										v-if="currentDetail.status === 'Open' && canApproveLeave(currentDetail.employee)" 
										@click="handleUpdateStatus(currentDetail.name, 'Approved')" 
										class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 flex items-center gap-2"
									>
										<span class="material-symbols-outlined text-sm">check_circle</span>Approve
									</button>
									<button 
										v-if="currentDetail.status === 'Open' && canApproveLeave(currentDetail.employee)" 
										@click="handleUpdateStatus(currentDetail.name, 'Rejected')" 
										class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2"
									>
										<span class="material-symbols-outlined text-sm">cancel</span>Reject
									</button>
								</div>

								<button
									@click="showDetailModal = false"
									class="w-10 h-10 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all ml-2"
								>
									<span class="material-symbols-outlined">close</span>
								</button>
							</div>
						</div>

						<!-- Modal Content -->
						<div v-if="loadingDetail" class="py-12 flex flex-col items-center justify-center gap-4">
							<div class="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
							<p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Loading details...</p>
						</div>

						<div v-else-if="detailError" class="py-6 text-center text-red-500 text-sm font-bold bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-100 dark:border-red-900/30">
							{{ detailError }}
						</div>

						<div v-else-if="currentDetail" class="space-y-6">
							<!-- Reference -->
							<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-gray-100 dark:border-gray-850">
								<div>
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Reference</span>
									<p class="text-lg font-black text-gray-900 dark:text-white mt-1">{{ currentDetail.name }}</p>
								</div>
								<div>
									<span class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest" :class="getStatusStyle(currentDetail.status)">
										{{ currentDetail.status }}
									</span>
								</div>
							</div>

							<!-- Employee and Type Grid -->
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Employee</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.employee_name }}</p>
									<p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ currentDetail.employee }}</p>
								</div>

								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Leave Type</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1 flex items-center gap-2">
										<span class="w-1.5 h-1.5 rounded-full" :class="currentDetail.leave_type?.toLowerCase().includes('sick') ? 'bg-amber-500' : 'bg-emerald-500'"></span>
										{{ currentDetail.leave_type }}
									</p>
								</div>
							</div>

							<!-- Period and Days Grid -->
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Period</span>
									<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">
										{{ formatDate(currentDetail.from_date) }} - {{ formatDate(currentDetail.to_date) }}
									</p>
									<p v-if="currentDetail.half_day" class="text-xs text-amber-600 dark:text-amber-400 font-bold mt-1 flex items-center gap-1">
										<span class="material-symbols-outlined text-sm">info</span> Half Day
									</p>
								</div>

								<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800">
									<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Total Days</span>
									<p class="text-2xl font-black text-gray-900 dark:text-white mt-1">
										{{ currentDetail.total_leave_days || 1 }} <span class="text-sm font-bold text-gray-400 dark:text-gray-500">Days</span>
									</p>
								</div>
							</div>

							<!-- Reason -->
							<div class="bg-gray-50/50 dark:bg-gray-800/30 p-6 rounded-2xl border border-gray-50 dark:border-gray-800">
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Reason / Description</span>
								<p class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2 whitespace-pre-wrap leading-relaxed">
									{{ currentDetail.description || 'No reason provided.' }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

		<!-- New Compensatory Request Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showCompModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showCompModal = false; compSubmitError = ''"
					></div>
					<div
						class="relative bg-white dark:bg-gray-900 rounded-4xl p-6 sm:p-10 w-full max-w-4xl shadow-2xl border border-gray-50 dark:border-gray-800 max-h-[95vh] overflow-y-auto no-scrollbar"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
									{{ isEditingComp ? 'Edit Compensatory Leave Request' : 'Compensatory Leave Request' }}
								</h3>
								<p class="text-xs font-bold text-gray-400 dark:text-gray-400 uppercase tracking-widest mt-1">
									For working on holidays or weekends
								</p>
							</div>
							<button
								@click="showCompModal = false; compSubmitError = ''"
								class="w-12 h-12 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div class="space-y-6">
							<!-- Employee -->
							<div>
								<label class="status-label dark:text-gray-300">Employee <span class="text-red-500">*</span></label>
								<select
									v-if="leaveStore.isApprover"
									v-model="newComp.employee"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select employee...</option>
									<option
										v-for="emp in leaveStore.approvedEmployeeList"
										:key="emp.name"
										:value="emp.name"
									>
										{{ emp.employee_name }}
									</option>
								</select>
								<input
									v-else
									:value="currEmployeeName"
									readonly
									class="w-full bg-gray-100 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-500 dark:text-gray-500 font-bold text-sm cursor-not-allowed"
								/>
							</div>

							<!-- Leave Type -->
							<div>
								<label class="status-label dark:text-gray-300">Leave Type <span class="text-red-500">*</span></label>
								<select
									v-model="newComp.leave_type"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select compensatory leave type...</option>
									<option
										v-for="lt in compLeaveTypes"
										:key="lt"
										:value="lt"
									>
										{{ lt }}
									</option>
								</select>
							</div>

							<!-- Holiday Worked On Dropdown -->
							<div>
								<label class="status-label dark:text-gray-300">Holiday Worked On <span class="text-red-500">*</span></label>
								<select
									v-model="newComp.holiday_date"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
								>
									<option value="" disabled>Select holiday...</option>
									<option
										v-for="h in availableHolidays"
										:key="h.holiday_date"
										:value="h.holiday_date"
									>
										{{ formatDate(h.holiday_date) }} - {{ h.description || 'No Description' }}
									</option>
								</select>
							</div>

							<!-- Half Day -->
							<div class="flex items-center gap-3">
								<input
									type="checkbox"
									id="comp_half_day"
									v-model="newComp.half_day"
									@change="onCompHalfDayToggle"
									class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 dark:bg-gray-800 text-primary focus:ring-primary"
								/>
								<label for="comp_half_day" class="text-sm font-bold text-gray-900 dark:text-white">Half Day</label>
							</div>

							<!-- Half Day Date (Read-only representation) -->
							<div v-if="newComp.half_day && newComp.holiday_date">
								<label class="status-label dark:text-gray-300">Half Day Date</label>
								<input
									:value="formatDate(newComp.holiday_date)"
									readonly
									class="w-full bg-gray-100 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-500 dark:text-gray-500 font-bold text-sm cursor-not-allowed"
								/>
							</div>

							<!-- Reason -->
							<div>
								<label class="status-label dark:text-gray-300">Reason <span class="text-red-500">*</span></label>
								<textarea
									v-model="newComp.reason"
									rows="3"
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
									placeholder="Provide the holiday or weekend work details..."
								></textarea>
							</div>
						</div>

						<div v-if="compSubmitError" class="mt-8 text-center text-red-500 text-sm font-bold bg-red-50 dark:bg-red-900/20 py-3 rounded-xl border border-red-100 dark:border-red-900/30">
							{{ compSubmitError }}
						</div>
						<div class="flex gap-4" :class="compSubmitError ? 'mt-6' : 'mt-12'">
							<button
								@click="showCompModal = false; compSubmitError = ''"
								class="flex-1 py-4 text-gray-400 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 font-black text-xs uppercase tracking-widest transition-colors"
							>
								Dismiss
							</button>
							<button
								@click="submitCompRequest"
								:disabled="!canSubmitComp"
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
import { ref, computed, onMounted, watch } from "vue";
import { createResource } from "frappe-ui";
import { useLeaveStore } from "@/stores/leave";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";
const _now = new Date();
const _currentMonthStr = `${_now.getFullYear()}-${String(_now.getMonth() + 1).padStart(2, '0')}`;

const activeTab = ref("leave_management");
const showCompModal = ref(false);
const compLeaveTypes = ref([]);
const canApproveComp = ref(false);
const compRequests = ref([]);
const compFilters = ref({
	employee: "",
	monthYear: _currentMonthStr,
});
const newComp = ref({
	employee: "",
	leave_type: "",
	holiday_date: "",
	work_from_date: "",
	work_end_date: "",
	half_day: false,
	half_day_date: "",
	reason: "",
});
const isEditingComp = ref(false);

const employeeHolidaysResource = createResource({
	url: "zevar_core.api.leave.get_holidays_for_employee",
	auto: false,
});

const availableHolidays = computed(() => {
	const holidays = [...(employeeHolidaysResource.data || [])];
	const currentDateVal = newComp.value.holiday_date;
	if (currentDateVal && !holidays.some(h => h.holiday_date === currentDateVal)) {
		holidays.push({
			holiday_date: currentDateVal,
			description: "Selected Holiday Date"
		});
	}
	return holidays;
});

watch(
	() => newComp.value.employee,
	(employee_id) => {
		if (employee_id) {
			employeeHolidaysResource.fetch({ employee: employee_id });
		}
	}
);

watch(
	() => newComp.value.holiday_date,
	(selectedDate) => {
		if (selectedDate) {
			newComp.value.work_from_date = selectedDate;
			newComp.value.work_end_date = selectedDate;
			if (newComp.value.half_day) {
				newComp.value.half_day_date = selectedDate;
			}
		} else {
			newComp.value.work_from_date = "";
			newComp.value.work_end_date = "";
			newComp.value.half_day_date = "";
		}
	}
);
const editCompName = ref("");
const compSubmitError = ref("");

const compRequestsResource = createResource({
	url: "zevar_core.api.leave.get_compensatory_leave_requests",
	auto: false,
	onSuccess(data) {
		compRequests.value = data || [];
	}
});

const compLeaveTypesResource = createResource({
	url: "zevar_core.api.leave.get_compensatory_leave_types",
	auto: true,
	onSuccess(data) {
		compLeaveTypes.value = data || [];
		if (data && data.length > 0 && !newComp.value.leave_type) {
			newComp.value.leave_type = data[0];
		}
	}
});

const canApproveCompResource = createResource({
	url: "zevar_core.api.leave.can_approve_compensatory_leaves",
	auto: true,
	onSuccess(data) {
		canApproveComp.value = !!data;
	}
});

const createCompResource = createResource({
	url: "zevar_core.api.leave.create_compensatory_leave_request",
	auto: false,
});

const updateCompResource = createResource({
	url: "zevar_core.api.leave.update_compensatory_leave_request",
	auto: false,
});

const deleteCompResource = createResource({
	url: "zevar_core.api.leave.delete_compensatory_leave_request",
	auto: false,
});

const approveCompResource = createResource({
	url: "zevar_core.api.leave.approve_compensatory_leave_request",
	auto: false,
});

const rejectCompResource = createResource({
	url: "zevar_core.api.leave.reject_compensatory_leave_request",
	auto: false,
});

const canSubmitComp = computed(() => {
	const base = newComp.value.leave_type && newComp.value.holiday_date && newComp.value.reason;
	if (!base) return false;
	if (newComp.value.half_day) return !!newComp.value.half_day_date;
	return true;
});

function getCompStatusStyle(docstatus) {
	if (docstatus === 0) return "bg-amber-100 text-amber-700";
	if (docstatus === 1) return "bg-emerald-100 text-emerald-700";
	if (docstatus === 2) return "bg-red-100 text-red-700";
	return "bg-gray-100 text-gray-500 dark:text-gray-500";
}

function getCompStatusLabel(docstatus) {
	if (docstatus === 0) return "Draft";
	if (docstatus === 1) return "Approved";
	if (docstatus === 2) return "Rejected";
	return "Unknown";
}

function onCompHalfDayToggle() {
	if (newComp.value.half_day) {
		newComp.value.half_day_date = newComp.value.holiday_date;
	} else {
		newComp.value.half_day_date = "";
	}
}

function resetCompForm() {
	compSubmitError.value = "";
	isEditingComp.value = false;
	editCompName.value = "";
	newComp.value = {
		employee: currEmployee.value,
		leave_type: compLeaveTypes.value[0] || "Compensatory Off",
		holiday_date: "",
		work_from_date: "",
		work_end_date: "",
		half_day: false,
		half_day_date: "",
		reason: "",
	};
	if (newComp.value.employee) {
		employeeHolidaysResource.fetch({ employee: newComp.value.employee });
	}
}

function handleEditComp(req) {
	activeActionMenu.value = "";
	isEditingComp.value = true;
	editCompName.value = req.name;
	newComp.value = {
		employee: req.employee,
		leave_type: req.leave_type,
		holiday_date: req.work_from_date,
		work_from_date: req.work_from_date,
		work_end_date: req.work_end_date,
		half_day: req.half_day === 1 || req.half_day === true,
		half_day_date: req.half_day_date || "",
		reason: req.reason || "",
	};
	compSubmitError.value = "";
	showCompModal.value = true;
}

async function submitCompRequest() {
	compSubmitError.value = "";
	const payload = {
		employee: newComp.value.employee || currEmployee.value,
		leave_type: newComp.value.leave_type,
		work_from_date: newComp.value.work_from_date,
		work_end_date: newComp.value.work_end_date,
		half_day: newComp.value.half_day ? 1 : 0,
		half_day_date: newComp.value.half_day ? newComp.value.half_day_date : null,
		reason: newComp.value.reason,
	};
	
	if (isEditingComp.value) {
		payload.name = editCompName.value;
		try {
			const res = await updateCompResource.fetch(payload);
			if (res && res.success === false) {
				compSubmitError.value = res.error || "Failed to update compensatory leave request";
			} else {
				showCompModal.value = false;
				resetCompForm();
				compRequestsResource.fetch({ employee: compFilters.value.employee, month_year: compFilters.value.monthYear });
			}
		} catch (err) {
			compSubmitError.value = err.message || "Failed to update request";
		}
	} else {
		try {
			const res = await createCompResource.fetch(payload);
			if (res && res.success === false) {
				compSubmitError.value = res.error || "Failed to create compensatory leave request";
			} else {
				showCompModal.value = false;
				resetCompForm();
				compRequestsResource.fetch({ employee: compFilters.value.employee, month_year: compFilters.value.monthYear });
			}
		} catch (err) {
			compSubmitError.value = err.message || "Failed to submit request";
		}
	}
}

async function handleDeleteComp(name) {
	activeActionMenu.value = "";
	if (!confirm("Are you sure you want to delete this compensatory leave request?")) return;
	try {
		const res = await deleteCompResource.fetch({ name });
		if (res && res.success === false) {
			alert(res.error || "Failed to delete request");
		} else {
			compRequestsResource.fetch({ employee: compFilters.value.employee, month_year: compFilters.value.monthYear });
		}
	} catch (err) {
		alert(err.message || "Failed to delete request");
	}
}

async function handleApproveComp(name) {
	activeActionMenu.value = "";
	if (!confirm("Are you sure you want to approve this compensatory leave request?")) return;
	try {
		const res = await approveCompResource.fetch({ name });
		if (res && res.success === false) {
			alert(res.error || "Failed to approve request");
		} else {
			compRequestsResource.fetch({ employee: compFilters.value.employee, month_year: compFilters.value.monthYear });
			leaveStore.fetchLeaveBalances();
		}
	} catch (err) {
		alert(err.message || "Failed to approve request");
	}
}

async function handleRejectComp(name) {
	activeActionMenu.value = "";
	if (!confirm("Are you sure you want to reject this compensatory leave request?")) return;
	try {
		const res = await rejectCompResource.fetch({ name });
		if (res && res.success === false) {
			alert(res.error || "Failed to reject request");
		} else {
			compRequestsResource.fetch({ employee: compFilters.value.employee, month_year: compFilters.value.monthYear });
			leaveStore.fetchLeaveBalances();
		}
	} catch (err) {
		alert(err.message || "Failed to reject request");
	}
}

watch(
	() => compFilters.value,
	(newFilters) => {
		compRequestsResource.fetch({ employee: newFilters.employee, month_year: newFilters.monthYear });
	},
	{ deep: true }
);

const today = new Date().toISOString().split("T")[0];

const leaveStore = useLeaveStore();

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
const employeeStore = useEmployeeStore();
const attendanceStore = useAttendanceStore();

// Current employee from store (reactive)
const currEmployee = computed(() => employeeStore.employee?.name || "");
const currEmployeeName = computed(() => employeeStore.employee?.employee_name || employeeStore.employee?.name || "");

// Leave approval details resource — same pattern as hrms Form.vue
const leaveApprovalDetails = createResource({
	url: "zevar_core.api.leave.get_leave_approval_details",
	auto: false,
	onSuccess(data) {
		setLeaveApprovers(data)
	},
});

// Leave details for the request form (includes allocations/balances)
const formLeaveDetails = createResource({
	url: "hrms.hr.doctype.leave_application.leave_application.get_leave_details",
	auto: false,
});

const availableLeaveTypes = computed(() => {
	if (formLeaveDetails.data) {
		const allocation = formLeaveDetails.data.leave_allocation || {};
		const lwps = formLeaveDetails.data.lwps || [];
		
		const allowedAllocated = Object.entries(allocation)
			.filter(([_, details]) => (details.remaining_leaves || 0) > 0)
			.map(([leave_type]) => leave_type);
			
		const allTypes = [...allowedAllocated, ...lwps];
		
		// Ensure currently selected leave_type (especially when editing) is included
		const currentSelected = newLeave.value.leave_type;
		if (currentSelected && !allTypes.includes(currentSelected)) {
			allTypes.push(currentSelected);
		}
		
		return allTypes.map(name => ({
			name: name,
			leave_type_name: name
		}));
	}
	return leaveStore.leaveTypes || [];
});

const selectedLeaveTypeBalanceLabel = computed(() => {
	const leaveType = newLeave.value.leave_type;
	if (!leaveType || !formLeaveDetails.data) return null;
	
	const allocation = formLeaveDetails.data.leave_allocation || {};
	const lwps = formLeaveDetails.data.lwps || [];
	
	if (lwps.includes(leaveType)) {
		return "Unlimited (LWP)";
	}
	
	if (allocation[leaveType]) {
		const bal = allocation[leaveType].remaining_leaves ?? 0;
		return `${bal} Day${bal !== 1 ? 's' : ''}`;
	}
	
	return "0 Days";
});

// Leave validation resource
const leaveValidationResource = createResource({
	url: "zevar_core.api.leave.validate_leave_application",
	auto: false,
	onError(err) {
		submitError.value = err?._error_message || err?.messages?.[0] || "Validation failed";
	},
});

// Leave approver is auto-filled when employee is selected

const showLeaveModal = ref(false);

const tableFilter = ref({
	status: "",
	monthYear: _currentMonthStr,
	employee: "",
});

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

watch(() => tableFilter.value.employee, (newEmp) => {
	if (newEmp) {
		leaveStore.fetchLeaveApplications(newEmp);
	} else {
		if (leaveStore.isApprover && currEmployee.value) {
			leaveStore.fetchLeaveApplicationsForAll();
		} else if (currEmployee.value) {
			leaveStore.fetchLeaveApplications(currEmployee.value);
		}
	}
});
const currentDate = ref(new Date());
const submitError = ref("");

const newLeave = ref({
	employee: "",
	leave_type: "",
	from_date: "",
	to_date: "",
	half_day: false,
	leave_approver: "",
	status: "Approved",
	description: "",
});

const canApprove = computed(() => leaveStore.isApprover);
const showStatus = computed(() => canApprove.value);
const activeActionMenu = ref("");
const activeDetailActionMenu = ref(false);
const showDetailModal = ref(false);
const viewApplicationName = ref("");
const currentDetail = ref(null);
const detailError = ref("");
const loadingDetail = ref(false);

const leaveDetailResource = createResource({
	url: "zevar_core.api.leave.get_leave_application",
	auto: false,
	onSuccess(data) {
		currentDetail.value = data;
		loadingDetail.value = false;
	},
	onError(err) {
		detailError.value = err?.messages?.[0] || "Failed to load leave application details";
		loadingDetail.value = false;
	}
});

function showViewModal(name) {
	viewApplicationName.value = name;
	showDetailModal.value = true;
	loadingDetail.value = true;
	currentDetail.value = null;
	detailError.value = "";
	leaveDetailResource.fetch({ name });
}

const isEditing = ref(false);
const editApplicationName = ref("");

function toggleActionMenu(name) {
	activeActionMenu.value = activeActionMenu.value === name ? "" : name;
}

const leaveStatusOptions = ref([]);

function canApproveLeave(appEmployee) {
	if (!leaveStore.isApprover) return false;
	if (leaveStore.isGlobalApprover) return true;
	if (!leaveStore.approvedEmployeeList.some(e => e.name === appEmployee)) return false;
	if (leaveStore.preventSelfApproval && currEmployee.value === appEmployee) return false;
	return true;
}


const filteredApplications = computed(() => {
	let apps = leaveStore.leaveApplications || [];
	if (tableFilter.value.employee) {
		apps = apps.filter(app => app.employee === tableFilter.value.employee);
	}
	if (tableFilter.value.status) {
		apps = apps.filter(app => app.status === tableFilter.value.status);
	}
	if (tableFilter.value.monthYear) {
		apps = apps.filter(app => {
			const appMonth = app.from_date?.substring(0, 7);
			return appMonth === tableFilter.value.monthYear;
		});
	}
	return apps.sort((a, b) => new Date(b.from_date) - new Date(a.from_date));
});

const currentPage = ref(1);
const pageSize = ref(10);

const totalRecords = computed(() => filteredApplications.value.length);
const totalPages = computed(() => Math.ceil(totalRecords.value / pageSize.value) || 1);

const paginatedApplications = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value;
	return filteredApplications.value.slice(start, start + pageSize.value);
});

function nextPage() {
	if (currentPage.value < totalPages.value) currentPage.value++;
}

function prevPage() {
	if (currentPage.value > 1) currentPage.value--;
}

watch(tableFilter, () => {
	currentPage.value = 1;
}, { deep: true });

// Metric computed values from leaveStore
const totalBalance = computed(() => {
	return leaveStore.totalLeaveBalance ?? 0;
});

const pendingCount = computed(() => {
	return leaveStore.pendingApplications?.length ?? 0;
});

const totalUsed = computed(() => {
	return (leaveStore.leaveBalances ?? []).reduce((sum, lb) => sum + ((lb.allocated_leaves || 0) - (lb.balance_leaves || 0)), 0);
});

const totalAllocated = computed(() => {
	return (leaveStore.leaveBalances ?? []).reduce((sum, lb) => sum + (lb.allocated_leaves || 0), 0);
});

const leaveTypeCount = computed(() => {
	return (leaveStore.leaveBalances ?? []).length;
});

const canSubmitLeave = computed(() => {
	const base = newLeave.value.leave_type && newLeave.value.from_date;
	if (!base) return false;
	if (newLeave.value.half_day) return true;
	return !!newLeave.value.to_date;
});

function getStatusStyle(status) {
	const s = status?.toLowerCase();
	if (s === "approved") return "bg-emerald-100 text-emerald-700";
	if (s === "open" || s === "pending") return "bg-amber-100 text-amber-700";
	if (s === "rejected") return "bg-red-100 text-red-700";
	return "bg-gray-100 text-gray-500 dark:text-gray-500";
}

function handleEdit(app) {
	activeActionMenu.value = "";
	isEditing.value = true;
	editApplicationName.value = app.name;
	
	newLeave.value = {
		employee: app.employee || currEmployee.value,
		leave_type: app.leave_type,
		from_date: app.from_date,
		to_date: app.to_date,
		half_day: app.half_day || false,
		leave_approver: app.leave_approver,
		status: app.status,
		description: app.description || "",
	};
	submitError.value = "";
	showLeaveModal.value = true;
	fetchFormLeaveDetails();
}

async function handleDelete(name) {
	activeActionMenu.value = "";
	if (!confirm("Are you sure you want to delete this leave application?")) return;
	
	const deleteRes = createResource({
		url: "zevar_core.api.leave.delete_leave_application",
		onSuccess(data) {
			if (data && data.success === false) alert(data.error || "Failed to delete");
			else {
				if (tableFilter.value.employee) {
					leaveStore.fetchLeaveApplications(tableFilter.value.employee);
				} else if (leaveStore.isApprover && currEmployee.value) {
					leaveStore.fetchLeaveApplicationsForAll();
				} else {
					leaveStore.fetchLeaveApplications();
				}
				leaveStore.fetchLeaveBalances();
			}
		}
	});
	deleteRes.submit({ name });
}

async function handleUpdateStatus(name, status) {
	activeActionMenu.value = "";
	if (!confirm(`Are you sure you want to mark this application as ${status}?`)) return;

	const updateRes = createResource({
		url: "zevar_core.api.leave.update_leave_status",
		onSuccess(data) {
			if (data && data.success === false) alert(data.error || "Failed to update status");
			else {
				if (tableFilter.value.employee) {
					leaveStore.fetchLeaveApplications(tableFilter.value.employee);
				} else if (leaveStore.isApprover && currEmployee.value) {
					leaveStore.fetchLeaveApplicationsForAll();
				} else {
					leaveStore.fetchLeaveApplications();
				}
				leaveStore.fetchLeaveBalances();
			}
		}
	});
	updateRes.submit({ name, status });
}

function formatDate(dateStr) {
	return new Date(dateStr).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	});
}

function setLeaveApprovers(data) {
	// Auto-fill leave_approver from selected employee
	if (data?.leave_approver) {
		newLeave.value.leave_approver = data.leave_approver
	}
}

async function submitLeave() {
	submitError.value = "";
	const payload = {
		employee: newLeave.value.employee || currEmployee.value,
		leave_type: newLeave.value.leave_type,
		from_date: newLeave.value.from_date,
		to_date: newLeave.value.half_day ? newLeave.value.from_date : newLeave.value.to_date,
		half_day: newLeave.value.half_day || false,
		leave_approver: newLeave.value.leave_approver,
		description: newLeave.value.description,
		status: newLeave.value.status,
	};

	if (isEditing.value) {
		payload.name = editApplicationName.value;
	}

	// Validate before submitting
	const validation = await leaveValidationResource.fetch({
		leave_type: payload.leave_type,
		from_date: payload.from_date,
		to_date: payload.to_date,
		employee: payload.employee
	});

	if (validation && validation.success === false) {
		submitError.value = validation.error || validation._error_message || "All fields are required: leave_type, from_date, to_date";
		return;
	}

	const submitResource = createResource({
		url: "zevar_core.api.leave.create_leave_application",
		onSuccess(data) {
			if (data && data.success === false) {
				submitError.value = data.error || data._error_message || "All fields are required: leave_type, from_date, to_date";
			} else {
				showLeaveModal.value = false;
				resetForm();
				if (tableFilter.value.employee) {
					leaveStore.fetchLeaveApplications(tableFilter.value.employee);
				} else if (leaveStore.isApprover && currEmployee.value) {
					leaveStore.fetchLeaveApplicationsForAll();
				} else {
					leaveStore.fetchLeaveApplications();
				}
				leaveStore.fetchLeaveBalances();
			}
		},
		onError(err) {
			let errorMsg = "Failed to submit leave request";
			if (err?._error_message) {
				errorMsg = err._error_message;
			} else if (err?.messages?.[0]) {
				errorMsg = err.messages[0];
			} else if (err?.message) {
				errorMsg = err.message;
			}
			submitError.value = errorMsg;
		},
	});

	submitResource.submit(payload);
}

function resetForm() {
	submitError.value = "";
	isEditing.value = false;
	editApplicationName.value = "";
	newLeave.value = {
		employee: currEmployee.value,
		leave_type: "",
		from_date: "",
		to_date: "",
		half_day: false,
		leave_approver: "",
		status: "Open",
		description: "",
	};
	fetchFormLeaveDetails();
}

function onHalfDayToggle(val) {
	if (!val) {
		// If unchecked and no to_date, set it to from_date
		if (!newLeave.value.to_date && newLeave.value.from_date) {
			newLeave.value.to_date = newLeave.value.from_date;
		}
	} else {
		newLeave.value.to_date = "";
	}
}

// Re-fetch leave approval details when employee changes (same pattern as hrms Form.vue)
function fetchFormLeaveDetails() {
	const employee_id = newLeave.value.employee;
	if (!employee_id) return;
	const date = newLeave.value.from_date || today;
	formLeaveDetails.fetch({ employee: employee_id, date });
}

watch(
	() => newLeave.value.employee,
	(employee_id) => {
		if (employee_id) {
			leaveApprovalDetails.fetch({ employee: employee_id });
			leaveStore.fetchLeaveTypes(employee_id);
			fetchFormLeaveDetails();
		}
	}
);

watch(
	() => newLeave.value.from_date,
	() => {
		fetchFormLeaveDetails();
	}
);

onMounted(async () => {
	window.addEventListener('click', (e) => {
		if (!e.target.closest('.more_vert') && !e.target.closest('.dropdown-menu')) {
			activeActionMenu.value = "";
			activeDetailActionMenu.value = false;
		}
	});

	await employeeStore.init();
	const employeeId = employeeStore.employee?.name;
	if (employeeId) {
		leaveStore.init(employeeId);
		// Fetch leave approval details for the current employee
		leaveApprovalDetails.fetch({ employee: employeeId });
		newLeave.value.employee = employeeId;
	}

	// Fetch Leave Application status options from backend
	const statusOptionsResource = createResource({
		url: "zevar_core.api.leave.get_leave_status_options",
		auto: true,
		onSuccess(data) {
			leaveStatusOptions.value = data || [];
		},
	});

	// Fetch approver status from store
	await leaveStore.checkApproverStatus();
	
	if (employeeId) {
		if (leaveStore.isApprover) {
			const hasSelf = leaveStore.approvedEmployeeList.some(e => e.name === employeeId);
			if (!hasSelf) {
				leaveStore.approvedEmployeeList.unshift({
					name: employeeId,
					employee_name: currEmployeeName.value
				});
			}
		} else {
			tableFilter.value.employee = employeeId;
			compFilters.value.employee = employeeId;
		}
	}

	if (!tableFilter.value.employee && leaveStore.isApprover && currEmployee.value) {
		leaveStore.fetchLeaveApplicationsForAll();
	}
	
	compRequestsResource.fetch({ employee: compFilters.value.employee, month_year: compFilters.value.monthYear });
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
