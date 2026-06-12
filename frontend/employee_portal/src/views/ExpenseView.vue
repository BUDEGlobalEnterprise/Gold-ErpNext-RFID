<template>
	<!-- Header -->
	<div class="shrink-0 px-2">
		<div class="flex flex-col md:flex-row md:items-end justify-between gap-8">
			<div>
				<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">
					Expense Claims
				</h1>
				<p class="text-gray-500 dark:text-white/50 font-medium font-sans">
					Manage your professional reimbursements and atelier budget.
				</p>
			</div>
			<div class="flex items-center gap-4">
				<button
					@click="openNewClaimModal"
					class="px-8 py-3 bg-primary text-white rounded-xl text-[11px] font-black uppercase tracking-[0.2em] shadow-glow-emerald transition-all flex items-center gap-2"
				>
					<span class="material-symbols-outlined text-lg">add</span>
					New Claim
				</button>
			</div>
		</div>
	</div>

	<div class="space-y-10">
		<!-- Stats Row -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-8">
			<!-- Card 1: Expense Claims (This Month) -->
			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div
						class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/30 flex items-center justify-center"
					>
						<span class="material-symbols-outlined text-blue-600 dark:text-blue-400 text-xl"
							>receipt_long</span
						>
					</div>
					<span
						class="text-[9px] font-black text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/30 px-2 py-1 rounded-full"
						>{{ stats.monthly_total_count }} {{ stats.monthly_total_count === 1 ? 'claim' : 'claims' }}</span
					>
				</div>
				<p class="text-[9px] font-black text-gray-400 dark:text-white/40 uppercase tracking-[0.2em] mb-1">
					Expense Claims (This Month)
				</p>
				<p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter leading-none">
					{{ formatCurrency(stats.monthly_total_amount) }}
				</p>
			</div>

			<!-- Card 2: Approved Claims (This Month) -->
			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 flex items-center justify-center">
						<span class="material-symbols-outlined text-emerald-600 dark:text-emerald-400 text-xl"
							>verified</span
						>
					</div>
					<span
						class="text-[9px] font-black text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 px-2 py-1 rounded-full"
						>{{ stats.monthly_approved_count }} approved</span
					>
				</div>
				<p class="text-[9px] font-black text-gray-400 dark:text-white/40 uppercase tracking-[0.2em] mb-1">
					Approved Claims (This Month)
				</p>
				<p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter leading-none">
					{{ formatCurrency(stats.monthly_approved_amount) }}
				</p>
			</div>

			<!-- Card 3: Rejected Claims (This Month) -->
			<div class="premium-card !p-8">
				<div class="flex items-center justify-between mb-6">
					<div class="w-10 h-10 rounded-xl bg-red-50 dark:bg-red-950/30 flex items-center justify-center">
						<span class="material-symbols-outlined text-red-600 dark:text-red-400 text-xl"
							>cancel</span
						>
					</div>
					<span
						class="text-[9px] font-black text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/30 px-2 py-1 rounded-full"
						>{{ stats.monthly_rejected_count }} rejected</span
					>
				</div>
				<p class="text-[9px] font-black text-gray-400 dark:text-white/40 uppercase tracking-[0.2em] mb-1">
					Rejected Claims (This Month)
				</p>
				<p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter leading-none">
					{{ formatCurrency(stats.monthly_rejected_amount) }}
				</p>
			</div>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
			<!-- Claims List Table Card -->
			<div class="lg:col-span-12">
				<div class="premium-card !p-0 !overflow-visible border border-gray-100 dark:border-gray-800 shadow-sm">
					<!-- Table Header -->
					<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-10 py-6 border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-white/[0.02] rounded-t-2xl">
						<h3 class="text-sm font-black text-gray-900 dark:text-white tracking-tight">
							Expense Claims
						</h3>
						<div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 w-full sm:w-auto">
							<select
								v-model="selectedStatus"
								class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto"
								style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
							>
								<option value="" class="dark:bg-gray-900">All Statuses</option>
								<option v-for="opt in expenseStatusOptions" :key="opt" :value="opt" class="dark:bg-gray-900">{{ opt }}</option>
							</select>
							<select
								v-if="expenseStore.isApprover"
								v-model="selectedEmployee"
								class="appearance-none pr-8 text-xs font-bold text-gray-700 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg pl-3 py-1.5 focus:ring-2 focus:ring-primary/20 outline-none w-full sm:w-auto"
								style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;"
							>
								<option value="" class="dark:bg-gray-900">All Employees</option>
								<option v-for="emp in expenseStore.approvedEmployeeList" :key="emp.name" :value="emp.name" class="dark:bg-gray-900">
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
							<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-white/[0.02]">
								<tr>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Reference</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Employee Name</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Posting Date</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Approver</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Amount</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Status</th>
									<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Actions</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-50 dark:divide-gray-800">
								<tr v-for="claim in paginatedClaims" :key="claim.name" class="transition-colors hover:bg-gray-50/50 dark:hover:bg-white/[0.02]">
									<td class="px-10 py-6">
										<span 
											@click="openDetailModal(claim)"
											class="text-sm font-bold text-primary dark:text-emerald-400 hover:underline cursor-pointer transition-all"
										>
											{{ claim.name }}
										</span>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-bold text-gray-900 dark:text-white">{{ claim.employee_name }}</p>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-bold text-gray-900 dark:text-white">{{ formatDate(claim.posting_date) }}</p>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-bold text-gray-900 dark:text-white">{{ claim.expense_approver || '-' }}</p>
									</td>
									<td class="px-10 py-6">
										<p class="text-sm font-black text-gray-900 dark:text-white">{{ formatCurrency(claim.total_claimed_amount) }}</p>
									</td>
									<td class="px-10 py-6 text-center">
										<span
											class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest"
											:class="getStatusTagStyle(claim.status)"
										>
											{{ claim.status }}
										</span>
									</td>
									<td class="px-10 py-6 text-center relative">
										<button @click.stop="toggleActionMenu(claim.name)" class="more_vert px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 border border-gray-200 dark:border-gray-700 hover:bg-gray-55 dark:hover:bg-gray-800 mx-auto">
											<span>More</span>
											<span class="material-symbols-outlined text-xs">expand_more</span>
										</button>
										
										<div v-if="activeActionMenu === claim.name" class="dropdown-menu absolute right-12 top-14 z-30 w-36 py-1.5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden">
											<button v-if="claim.status === 'Draft'" :id="'edit-' + claim.name" @click="handleEdit(claim.name)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">edit</span>Edit
											</button>
											<button v-if="claim.status === 'Draft'" :id="'delete-' + claim.name" @click="handleDelete(claim.name)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-55 dark:hover:bg-red-950/20 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">delete</span>Delete
											</button>
											<button v-if="claim.status === 'Draft' && canApproveClaim(claim)" :id="'approve-' + claim.name" @click="handleUpdateStatus(claim.name, 'Approved')" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-emerald-600 dark:text-emerald-400 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">check_circle</span>Approve
											</button>
											<button v-if="claim.status === 'Draft' && canApproveClaim(claim)" :id="'reject-' + claim.name" @click="handleUpdateStatus(claim.name, 'Rejected')" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-55 dark:hover:bg-red-950/20 flex items-center gap-2">
												<span class="material-symbols-outlined text-sm">cancel</span>Reject
											</button>
										</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>

					<!-- Pagination Footer -->
					<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-10 py-5 border-t border-gray-50 dark:border-gray-800 bg-gray-50/10 dark:bg-white/[0.02] rounded-b-2xl">
						<!-- Page Size Dropdown -->
						<div class="flex items-center gap-2">
							<label class="text-xs text-gray-500 dark:text-gray-400 font-bold whitespace-nowrap">Rows per page:</label>
							<div class="relative overflow-visible">
								<select v-model.number="pageSize" class="appearance-none w-20 pr-8 pl-3 py-2 text-xs font-bold cursor-pointer border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white outline-none" @change="currentPage = 1" style="background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23131313%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E'); background-repeat: no-repeat; background-position: right 0.75rem top 50%; background-size: 0.65rem auto;">
									<option :value="10" class="dark:bg-gray-900">10</option>
									<option :value="20" class="dark:bg-gray-900">20</option>
									<option :value="50" class="dark:bg-gray-900">50</option>
								</select>
							</div>
						</div>

						<!-- Showing X-Y of Z and navigation buttons -->
						<div class="flex items-center justify-between sm:justify-end gap-6 flex-1">
							<span class="text-xs text-gray-500 dark:text-gray-400 font-bold tabular-nums">
								Showing {{ Math.min((currentPage - 1) * Number(pageSize) + 1, totalRecords) || 0 }} - {{ Math.min(currentPage * Number(pageSize), totalRecords) || 0 }} of {{ totalRecords }} records
							</span>
							<div class="flex items-center gap-1">
								<button 
									@click="prevPage" 
									:disabled="currentPage === 1"
									class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 hover:bg-gray-55 dark:hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
								>
									<span class="material-symbols-outlined text-sm font-bold">chevron_left</span>
								</button>
								<button 
									@click="nextPage" 
									:disabled="currentPage === totalPages"
									class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-100 hover:bg-gray-55 dark:hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
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

	<!-- New Claim Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showClaimModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4"
				>
					<div
						class="absolute inset-0 bg-black/40 backdrop-blur-sm"
						@click="showClaimModal = false"
					></div>
					<div
						class="relative bg-white dark:bg-gray-900 rounded-4xl p-6 sm:p-10 w-full max-w-4xl shadow-2xl border border-gray-50 dark:border-gray-800 max-h-[95vh] overflow-y-auto no-scrollbar"
					>
						<div class="flex items-center justify-between mb-10">
							<div>
								<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
									{{ isEditing ? 'Edit Claim' : 'Submit Claim' }}
								</h3>
								<p
									class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mt-1"
								>
									{{ isEditing ? 'Update your professional reimbursement request' : 'Personnel Reimbursement Form' }}
								</p>
							</div>
							<button
								@click="showClaimModal = false"
								class="w-12 h-12 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
							>
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>

						<div class="space-y-8">
							<!-- Header Fields Grid -->
							<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
								<!-- Employee Name -->
								<div>
									<label class="status-label">Employee Name</label>
									<input
										type="text"
										disabled
										:value="employeeStore.employee?.employee_name"
										class="w-full bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-400 dark:text-gray-500 font-bold text-sm cursor-not-allowed"
									/>
								</div>

								<!-- Expense Approver -->
								<div>
									<label class="status-label">Expense Approver</label>
									<select
										v-model="expenseApprover"
										class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
									>
										<option value="" disabled selected class="dark:bg-gray-800">Select Approver...</option>
										<option
											v-for="approver in expenseStore.approversData?.department_approvers"
											:key="approver.name"
											:value="approver.name"
											class="dark:bg-gray-800"
										>
											{{ approver.full_name || approver.name }}
										</option>
									</select>
								</div>

								<!-- Posting Date -->
								<div>
									<label class="status-label">Posting Date</label>
									<input
										type="date"
										v-model="postingDate"
										class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all"
									/>
								</div>

								<!-- Payable Account -->
								<div>
									<label class="status-label">Payable Account</label>
									<select
										v-model="payableAccount"
										class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all appearance-none"
									>
										<option value="" disabled selected class="dark:bg-gray-800">Select Payable Account...</option>
										<option
											v-for="acc in expenseStore.payableAccounts"
											:key="acc.value"
											:value="acc.value"
											class="dark:bg-gray-800"
										>
											{{ acc.label || acc.value }}
										</option>
									</select>
								</div>
							</div>

							<!-- Table Header -->
							<div class="border-t border-gray-100 dark:border-gray-800 pt-8">
								<h4 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-widest mb-6">
									Expense Lines
								</h4>

								<div class="hidden md:grid grid-cols-12 gap-4 px-2 mb-3">
									<span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest col-span-2">Date</span>
									<span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest col-span-3">Type</span>
									<span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest col-span-2">Amount ($)</span>
									<span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest col-span-4">Description</span>
									<span class="text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest col-span-1 text-center">Action</span>
								</div>

								<!-- Expense Lines list -->
								<div class="space-y-3">
									<div v-for="(line, index) in expensesList" :key="index" class="grid grid-cols-12 gap-4 items-center">
										<!-- Date -->
										<div class="col-span-12 md:col-span-2">
											<input
												type="date"
												v-model="line.expense_date"
												class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl px-4 py-3 text-gray-900 dark:text-white font-semibold text-xs focus:outline-none focus:ring-2 focus:ring-primary/10 transition-all"
											/>
										</div>
										<!-- Type -->
										<div class="col-span-12 md:col-span-3">
											<select
												v-model="line.expense_type"
												class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl px-4 py-3 text-gray-900 dark:text-white font-semibold text-xs focus:outline-none focus:ring-2 focus:ring-primary/10 transition-all appearance-none"
											>
												<option value="" disabled selected class="dark:bg-gray-800">Select Type...</option>
												<option v-for="t in expenseStore.expenseTypes" :key="t.name" :value="t.name" class="dark:bg-gray-800">
													{{ t.label || t.name }}
												</option>
											</select>
										</div>
										<!-- Amount -->
										<div class="col-span-12 md:col-span-2">
											<input
												type="number"
												v-model="line.amount"
												placeholder="0.00"
												class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl px-4 py-3 text-gray-900 dark:text-white font-semibold text-xs focus:outline-none focus:ring-2 focus:ring-primary/10 transition-all font-mono"
											/>
										</div>
										<!-- Description -->
										<div class="col-span-12 md:col-span-4">
											<input
												type="text"
												v-model="line.description"
												placeholder="Description..."
												class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl px-4 py-3 text-gray-900 dark:text-white font-semibold text-xs focus:outline-none focus:ring-2 focus:ring-primary/10 transition-all"
											/>
										</div>
										<!-- Action -->
										<div class="col-span-12 md:col-span-1 flex justify-center">
											<button
												type="button"
												@click="removeExpenseLine(index)"
												class="w-10 h-10 rounded-full hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center justify-center text-red-500 transition-all"
											>
												<span class="material-symbols-outlined text-lg">delete</span>
											</button>
										</div>
									</div>
								</div>

								<!-- Add Line Button -->
								<button
									type="button"
									@click="addExpenseLine"
									class="mt-4 px-6 py-2.5 bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/10 hover:bg-gray-100 dark:hover:bg-white/10 text-gray-700 dark:text-white rounded-xl text-[10px] font-black uppercase tracking-wider transition-all flex items-center gap-2"
								>
									<span class="material-symbols-outlined text-sm">add</span>
									Add Row
								</button>
							</div>

							<!-- Remark -->
							<div>
								<label class="status-label">Remark / Notes</label>
								<textarea
									rows="2"
									v-model="remark"
									placeholder="Describe the context of this claim..."
									class="w-full bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl px-6 py-4 text-gray-900 dark:text-white font-bold text-sm focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all resize-none"
								></textarea>
							</div>

							<!-- Total claimed amount display -->
							<div class="flex items-center justify-between border-t border-gray-100 dark:border-gray-800 pt-6">
								<span class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Total Claim Amount</span>
								<span class="text-xl font-black text-gray-900 dark:text-white tracking-tight">{{ formatCurrency(totalClaimedAmount) }}</span>
							</div>
						</div>

						<!-- Error alert box -->
						<div v-if="submitError" class="mt-8 text-center text-red-500 text-sm font-bold bg-red-50 dark:bg-red-900/20 py-3 rounded-xl border border-red-100 dark:border-red-900/30">
							{{ submitError }}
						</div>

						<!-- Form Buttons -->
						<div class="flex gap-4" :class="submitError ? 'mt-6' : 'mt-12'">
							<button
								@click="showClaimModal = false"
								class="flex-1 py-4 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 font-black text-xs uppercase tracking-widest transition-all"
							>
								Dismiss
							</button>
							<button
								@click="handleFinalizeSubmission"
								:disabled="isSubmitting"
								class="flex-[1.5] py-4 bg-primary text-white rounded-2xl text-xs font-black uppercase tracking-widest shadow-glow-emerald disabled:opacity-50 flex items-center justify-center gap-2"
							>
								<span v-if="isSubmitting" class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
								{{ isSubmitting ? (isEditing ? 'Updating...' : 'Submitting...') : (isEditing ? 'Update Claim' : 'Finalize Submission') }}
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

	<!-- Claim Details Modal -->
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
					class="relative bg-white dark:bg-gray-900 rounded-4xl p-6 sm:p-10 w-full max-w-3xl shadow-2xl border border-gray-50 dark:border-gray-800 max-h-[95vh] overflow-y-auto no-scrollbar"
				>
					<div class="flex items-center justify-between mb-8">
						<div>
							<h3 class="text-2xl font-black text-gray-900 dark:text-white tracking-tight">
								Claim Details
							</h3>
							<p class="text-xs font-bold text-gray-400 dark:text-gray-500 uppercase tracking-widest mt-1">
								Expense Claim Record Overview
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
							<div>
								<span
									class="inline-flex px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest"
									:class="getStatusTagStyle(currentDetail.status)"
								>
									{{ currentDetail.status }}
								</span>
							</div>
						</div>

						<!-- Core Fields Grid -->
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
							<!-- Employee Name -->
							<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Employee</span>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.employee_name }}</p>
								<p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ currentDetail.employee }}</p>
							</div>

							<!-- Expense Approver -->
							<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Expense Approver</span>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.expense_approver || '-' }}</p>
							</div>

							<!-- Posting Date -->
							<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Posting Date</span>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ formatDate(currentDetail.posting_date) }}</p>
							</div>

							<!-- Payable Account -->
							<div class="bg-gray-50/50 dark:bg-gray-800/30 p-5 rounded-2xl border border-gray-50 dark:border-gray-800/80">
								<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Payable Account</span>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-1">{{ currentDetail.payable_account || '-' }}</p>
							</div>
						</div>

						<!-- Expense Lines Table -->
						<div class="border border-gray-100 dark:border-gray-800 rounded-2xl overflow-hidden">
							<table class="w-full text-left border-collapse">
								<thead class="bg-gray-50/30 dark:bg-white/[0.02] border-b border-gray-100 dark:border-gray-800">
									<tr>
										<th class="px-5 py-3 text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-wider">Date</th>
										<th class="px-5 py-3 text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-wider">Type</th>
										<th class="px-5 py-3 text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-wider">Amount</th>
										<th class="px-5 py-3 text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-wider">Description</th>
									</tr>
								</thead>
								<tbody class="divide-y divide-gray-100 dark:divide-gray-800">
									<tr v-for="(line, idx) in currentDetail.expenses" :key="idx" class="hover:bg-gray-50/20 dark:hover:bg-white/[0.01]">
										<td class="px-5 py-3 text-xs font-semibold text-gray-900 dark:text-white">{{ formatDate(line.expense_date) }}</td>
										<td class="px-5 py-3 text-xs font-semibold text-gray-900 dark:text-white">{{ line.expense_type }}</td>
										<td class="px-5 py-3 text-xs font-black text-gray-900 dark:text-white">{{ formatCurrency(line.amount) }}</td>
										<td class="px-5 py-3 text-xs text-gray-500 dark:text-gray-400">{{ line.description || '-' }}</td>
									</tr>
									<tr v-if="!currentDetail.expenses || currentDetail.expenses.length === 0">
										<td colspan="4" class="px-5 py-6 text-center text-xs text-gray-400 dark:text-gray-500 font-medium">No expense lines found.</td>
									</tr>
								</tbody>
							</table>
						</div>

						<!-- Remarks / Notes -->
						<div class="bg-gray-50/30 dark:bg-white/[0.01] p-5 rounded-2xl border border-gray-100 dark:border-gray-800">
							<span class="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Remark / Notes</span>
							<p class="text-sm font-medium text-gray-700 dark:text-gray-300 mt-2 whitespace-pre-wrap leading-relaxed">
								{{ currentDetail.remark || 'No remark provided.' }}
							</p>
						</div>

						<!-- Total Amount -->
						<div class="flex items-center justify-between border-t border-gray-100 dark:border-gray-800 pt-6">
							<span class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Total Claim Amount</span>
							<span class="text-xl font-black text-gray-900 dark:text-white tracking-tight">{{ formatCurrency(currentDetail.total_claimed_amount) }}</span>
						</div>
					</div>

					<!-- Form Buttons -->
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
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { createResource } from "frappe-ui";
import { useExpenseStore } from "@/stores/expense";
import { useEmployeeStore } from "@/stores/employee";
import { useAuthStore } from "@/stores/auth";

const expenseStore = useExpenseStore();
const employeeStore = useEmployeeStore();
const authStore = useAuthStore();

const showClaimModal = ref(false);
const showDetailModal = ref(false);
const currentDetail = ref(null);

function openDetailModal(claim) {
	currentDetail.value = claim;
	showDetailModal.value = true;
}

const selectedStatus = ref("");
const selectedEmployee = ref("");
const expenseStatusOptions = ref([]);

const isEditing = ref(false);
const editClaimName = ref("");
const activeActionMenu = ref("");

// Pagination state
const currentPage = ref(1);
const pageSize = ref(10);

const currEmployee = computed(() => employeeStore.employee?.name || "");

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

const fetchStatusOptions = createResource({
	url: "zevar_core.api.expense.get_expense_status_options",
	auto: true,
	onSuccess(data) {
		expenseStatusOptions.value = data || [];
	},
});

watch([selectedStatus, selectedEmployee], async ([newStatus, newEmp]) => {
	currentPage.value = 1;
	if (newEmp) {
		await expenseStore.fetchClaims(newEmp, newStatus);
	} else {
		if (expenseStore.isApprover) {
			await expenseStore.fetchClaimsForAll(newStatus);
		} else if (employeeStore.employee?.name) {
			await expenseStore.fetchClaims(employeeStore.employee.name, newStatus);
		}
	}
});

const stats = computed(() => expenseStore.expenseSummary || {
	monthly_total_count: 0,
	monthly_total_amount: 0.0,
	monthly_approved_count: 0,
	monthly_approved_amount: 0.0,
	monthly_rejected_count: 0,
	monthly_rejected_amount: 0.0,
});

// Form state variables
const expenseApprover = ref("");
const postingDate = ref(new Date().toISOString().substring(0, 10));
const payableAccount = ref("");
const remark = ref("");
const expensesList = ref([
	{ expense_date: new Date().toISOString().substring(0, 10), expense_type: "", amount: 0, description: "" }
]);
const isSubmitting = ref(false);
const submitError = ref("");

const totalClaimedAmount = computed(() => {
	return expensesList.value.reduce((sum, item) => sum + parseFloat(item.amount || 0), 0);
});

// Fetch configuration parameters dynamically
watch(showClaimModal, async (val) => {
	submitError.value = "";
	if (!val) {
		isEditing.value = false;
		editClaimName.value = "";
	} else if (employeeStore.employee) {
		const company = employeeStore.employee.company;
		const employeeId = employeeStore.employee.name;

		if (!isEditing.value) {
			await Promise.all([
				expenseStore.fetchPayableAccounts(company),
				expenseStore.fetchApprovers(employeeId),
				expenseStore.fetchCompanyDefaults(company),
			]);

			expenseApprover.value = expenseStore.approversData?.expense_approver || "";
			payableAccount.value = expenseStore.companyDefaults?.default_expense_claim_payable_account || "";
			postingDate.value = new Date().toISOString().substring(0, 10);
			remark.value = "";
			expensesList.value = [
				{ expense_date: postingDate.value, expense_type: "", amount: 0, description: "" }
			];
		} else {
			await Promise.all([
				expenseStore.fetchPayableAccounts(company),
				expenseStore.fetchApprovers(employeeId),
			]);
		}
	}
});

function addExpenseLine() {
	expensesList.value.push({
		expense_date: postingDate.value,
		expense_type: "",
		amount: 0,
		description: "",
	});
}

function removeExpenseLine(idx) {
	expensesList.value.splice(idx, 1);
	if (expensesList.value.length === 0) {
		addExpenseLine();
	}
}

function openNewClaimModal() {
	isEditing.value = false;
	editClaimName.value = "";
	
	// Reset form fields
	expenseApprover.value = "";
	payableAccount.value = "";
	postingDate.value = new Date().toISOString().substring(0, 10);
	remark.value = "";
	expensesList.value = [
		{ expense_date: postingDate.value, expense_type: "", amount: 0, description: "" }
	];
	
	submitError.value = "";
	showClaimModal.value = true;
}

function toggleActionMenu(name) {
	activeActionMenu.value = activeActionMenu.value === name ? "" : name;
}

function handleEdit(claimName) {
	activeActionMenu.value = "";
	isEditing.value = true;
	editClaimName.value = claimName;
	
	const claim = filteredClaims.value.find((c) => c.name === claimName);
	if (!claim) {
		console.error("Claim not found for edit:", claimName);
		return;
	}
	
	expenseApprover.value = claim.expense_approver || "";
	payableAccount.value = claim.payable_account || "";
	postingDate.value = claim.posting_date || new Date().toISOString().substring(0, 10);
	remark.value = claim.remark || "";
	
	expensesList.value = claim.expenses && claim.expenses.length > 0
		? claim.expenses.map((e) => ({
				expense_date: e.expense_date || postingDate.value,
				expense_type: e.expense_type,
				amount: e.amount,
				description: e.description || "",
			}))
		: [{ expense_date: postingDate.value, expense_type: "", amount: 0, description: "" }];
		
	submitError.value = "";
	showClaimModal.value = true;
}

async function handleDelete(name) {
	activeActionMenu.value = "";
	if (!confirm("Are you sure you want to delete this expense claim?")) return;
	
	try {
		const deleteRes = createResource({
			url: "zevar_core.api.expense.delete_expense_claim",
			onSuccess(data) {
				if (data && data.success === false) {
					alert(data.error || "Failed to delete");
				} else {
					if (selectedEmployee.value) {
						expenseStore.fetchClaims(selectedEmployee.value, selectedStatus.value);
					} else if (expenseStore.isApprover) {
						expenseStore.fetchClaimsForAll(selectedStatus.value);
					} else if (employeeStore.employee?.name) {
						expenseStore.fetchClaims(employeeStore.employee.name, selectedStatus.value);
					}
					if (employeeStore.employee?.name) {
						expenseStore.fetchSummary(employeeStore.employee.name);
					}
				}
			}
		});
		await deleteRes.submit({ name });
	} catch (err) {
		console.error("Delete failed:", err);
		alert("An error occurred while deleting the claim.");
	}
}

function canApproveClaim(claim) {
	if (!expenseStore.isApprover) return false;
	
	// Enforce prevent self-approval check
	const currentEmployeeId = employeeStore.employee?.name;
	if (expenseStore.preventSelfApproval && currentEmployeeId === claim.employee) {
		return false;
	}
	
	// 1. Designated approver check
	if (claim.expense_approver === authStore.user?.user) {
		return true;
	}
	
	// 2. Global approver check
	if (expenseStore.isGlobalApprover) return true;
	
	// 3. Special employee list check
	if (expenseStore.approvedEmployeeList.some((e) => e.name === claim.employee)) {
		return true;
	}
	
	return false;
}

async function handleUpdateStatus(name, status) {
	activeActionMenu.value = "";
	if (!confirm(`Are you sure you want to mark this expense claim as ${status}?`)) return;
	
	try {
		const updateRes = createResource({
			url: "zevar_core.api.expense.update_expense_claim_status",
			onSuccess(data) {
				if (data && data.success === false) {
					alert(data.error || "Failed to update status");
				} else {
					if (selectedEmployee.value) {
						expenseStore.fetchClaims(selectedEmployee.value, selectedStatus.value);
					} else if (expenseStore.isApprover) {
						expenseStore.fetchClaimsForAll(selectedStatus.value);
					} else if (employeeStore.employee?.name) {
						expenseStore.fetchClaims(employeeStore.employee.name, selectedStatus.value);
					}
					if (employeeStore.employee?.name) {
						expenseStore.fetchSummary(employeeStore.employee.name);
					}
				}
			}
		});
		await updateRes.submit({ name, status });
	} catch (err) {
		console.error("Update status failed:", err);
		alert("An error occurred while updating the status.");
	}
}

async function handleFinalizeSubmission() {
	submitError.value = "";
	if (!expenseApprover.value) {
		submitError.value = "Please select an Expense Approver.";
		return;
	}
	if (!payableAccount.value) {
		submitError.value = "Please select a Payable Account.";
		return;
	}
	if (expensesList.value.length === 0) {
		submitError.value = "Please add at least one expense line.";
		return;
	}
	for (const item of expensesList.value) {
		if (!item.expense_type) {
			submitError.value = "Please select an Expense Type for all lines.";
			return;
		}
		if (parseFloat(item.amount || 0) <= 0) {
			submitError.value = "Amount must be greater than zero for all lines.";
			return;
		}
	}

	isSubmitting.value = true;
	try {
		const payload = {
			employee: employeeStore.employee.name,
			posting_date: postingDate.value,
			payable_account: payableAccount.value,
			expense_approver: expenseApprover.value,
			expenses: expensesList.value,
			remark: remark.value,
		};
		if (isEditing.value) {
			payload.name = editClaimName.value;
		}

		const response = await expenseStore.submitClaimResource.submit(payload);

		if (response && response.success) {
			showClaimModal.value = false;
			isEditing.value = false;
			editClaimName.value = "";
			
			if (selectedEmployee.value) {
				await expenseStore.fetchClaims(selectedEmployee.value, selectedStatus.value);
			} else if (expenseStore.isApprover) {
				await expenseStore.fetchClaimsForAll(selectedStatus.value);
			} else {
				await expenseStore.fetchClaims(employeeStore.employee.name, selectedStatus.value);
			}
			await expenseStore.fetchSummary(employeeStore.employee.name);
		}
	} catch (error) {
		console.error("Submission failed:", error);
		submitError.value = getCleanErrorMessage(error);
	} finally {
		isSubmitting.value = false;
	}
}

const mockClaims = [
	{
		name: "EXP-2024-001",
		title: "Business Trip: Antwerp Diamond Fair",
		expense_type: "Travel",
		category: "Travel & Logistics",
		posting_date: "2023-10-14",
		total_claimed_amount: 1450.0,
		status: "Pending",
	},
	{
		name: "EXP-2024-002",
		title: "Client Dinner: VVIP Stakeholder",
		expense_type: "Dining",
		category: "Food & Dining",
		posting_date: "2023-10-12",
		total_claimed_amount: 420.5,
		status: "Approved",
	},
	{
		name: "EXP-2024-003",
		title: "Specialist Tools: Loupe & Precision Tweezers",
		expense_type: "Tools",
		category: "Atelier Supplies",
		posting_date: "2023-10-09",
		total_claimed_amount: 890.0,
		status: "Approved",
	},
	{
		name: "EXP-2024-004",
		title: "Insured Shipping: GIA Certifications",
		expense_type: "Shipping",
		category: "Logistics",
		posting_date: "2023-10-05",
		total_claimed_amount: 125.0,
		status: "Rejected",
	},
];

const filteredClaims = computed(() => {
	const claims = expenseStore.expenseClaims.length > 0 ? expenseStore.expenseClaims : mockClaims;
	let result = claims;
	if (selectedStatus.value) {
		result = result.filter((c) => c.status === selectedStatus.value);
	}
	if (selectedEmployee.value) {
		result = result.filter((c) => c.employee === selectedEmployee.value);
	}
	return result;
});

const totalRecords = computed(() => filteredClaims.value.length);
const totalPages = computed(() => Math.ceil(totalRecords.value / pageSize.value) || 1);
const paginatedClaims = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value;
	return filteredClaims.value.slice(start, start + pageSize.value);
});

function nextPage() {
	if (currentPage.value < totalPages.value) {
		currentPage.value++;
	}
}

function prevPage() {
	if (currentPage.value > 1) {
		currentPage.value--;
	}
}

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

function getStatusTagStyle(status) {
	const e = status?.toLowerCase();
	if (e === "approved" || e === "paid") {
		return "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400";
	} else if (e === "pending" || e === "submitted" || e === "unpaid") {
		return "bg-amber-100 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400";
	} else if (e === "rejected" || e === "cancelled") {
		return "bg-red-100 text-red-700 dark:bg-red-950/20 dark:text-red-400";
	} else {
		return "bg-gray-100 text-gray-500 dark:bg-white/5 dark:text-gray-400";
	}
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
	return new Date(dateStr).toLocaleDateString("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	});
}

function getCleanErrorMessage(error) {
	let msg = error?._error_message || (error?.messages && error.messages[0]) || error?.message || "";
	if (typeof msg === "string") {
		// Strip HTML tags if any
		msg = msg.replace(/<[^>]*>/g, "");
		// Remove common python/frappe exception prefixes
		msg = msg.replace(/^(frappe\.exceptions\.)?[a-zA-Z]+Error:\s*/, "");
		// Clean up "Failed to submit expense claim:" if present
		msg = msg.replace(/^Failed to submit expense claim:\s*/i, "");
		msg = msg.trim();
	}
	return msg || "Failed to submit expense claim. Please try again.";
}

onMounted(async () => {
	window.addEventListener("click", (e) => {
		if (!e.target.closest(".more_vert") && !e.target.closest(".dropdown-menu")) {
			activeActionMenu.value = "";
		}
	});

	await employeeStore.init();
	const employeeId = employeeStore.employee?.name;
	
	// Check if the current user is an approver unconditionally
	await expenseStore.checkApproverStatus();

	if (employeeId) {
		if (expenseStore.isApprover) {
			const hasSelf = expenseStore.approvedEmployeeList.some((e) => e.name === employeeId);
			if (!hasSelf) {
				expenseStore.approvedEmployeeList.unshift({
					name: employeeId,
					employee_name: employeeStore.employee?.employee_name || employeeId,
				});
			}
			await expenseStore.fetchClaimsForAll();
		} else {
			await expenseStore.fetchClaims(employeeId);
		}
		selectedEmployee.value = employeeId;
		await expenseStore.fetchSummary(employeeId);
	} else {
		// Users without an employee record (like Administrator) who are approvers
		if (expenseStore.isApprover) {
			await expenseStore.fetchClaimsForAll();
		}
	}
	await expenseStore.fetchTypes();
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
	transform: scale(0.95);
}

.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}

.dark select {
	background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E") !important;
}
</style>
