<template>
<div class="max-w-7xl mx-auto space-y-8">
	<!-- Nav Tabs -->
	<div class="flex items-center gap-8 border-b border-gray-100 dark:border-gray-800">
		<button
			@click="activeTab = 'dashboard'"
			class="pb-3 text-sm font-black uppercase tracking-[0.2em] transition-all border-b-2"
			:class="activeTab === 'dashboard' ? 'border-gray-900 dark:border-white text-gray-900 dark:text-white' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'"
		>
			Dashboard
		</button>
		<button
			@click="activeTab = 'assignment'"
			class="pb-3 text-sm font-black uppercase tracking-[0.2em] transition-all border-b-2"
			:class="activeTab === 'assignment' ? 'border-gray-900 dark:border-white text-gray-900 dark:text-white' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'"
		>
			Shift Assignment
		</button>
	</div>

	<!-- Dashboard Tab -->
	<div v-if="activeTab === 'dashboard'" class="space-y-8">
		<!-- Header -->
		<div class="px-2 flex items-center justify-between">
			<div>
				<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">
				My Roster
			</h1>
			<p class="text-gray-500 font-medium font-sans dark:text-white/50">Your work schedule</p>
		</div>
	</div>

		<!-- Stats Row -->
		<div v-if="rosterStore.loading" class="grid grid-cols-1 md:grid-cols-3 gap-5">
			<div v-for="i in 3" :key="i" class="bg-white dark:bg-white/5 rounded-xl p-5 shadow-sm animate-pulse">
				<div class="h-3 bg-gray-200 dark:bg-white/10 rounded w-20 mb-3"></div>
				<div class="h-8 bg-gray-200 dark:bg-white/10 rounded w-16"></div>
			</div>
		</div>
		<div v-else class="grid grid-cols-1 md:grid-cols-3 gap-5">
			<div class="bg-white dark:bg-white/5 rounded-xl p-5 shadow-sm">
				<p class="text-[11px] text-gray-500 dark:text-white/50 font-medium">WORKING DAYS</p>
				<div class="mt-2 flex items-baseline gap-1">
					<span class="text-2xl font-bold text-[#064e3b] dark:text-emerald-400">{{ rosterStore.workingDays }}</span>
					<span class="text-sm text-gray-400 dark:text-white/40">/ 07</span>
				</div>
				<p class="text-xs text-gray-500 dark:text-white/50 mt-2 flex items-center gap-1">
					<span class="material-symbols-outlined text-sm text-[#064e3b] dark:text-emerald-400"
						>check_circle</span
					>
					On track this week
				</p>
			</div>
			<div class="bg-white dark:bg-white/5 rounded-xl p-5 shadow-sm">
				<p class="text-[11px] text-gray-500 dark:text-white/50 font-medium">HOURS WORKED</p>
				<div class="mt-2 flex items-baseline gap-1">
					<span class="text-2xl font-bold text-[#064e3b] dark:text-emerald-400">{{ rosterStore.hoursWorked.toFixed(1) }}</span>
					<span class="text-sm text-gray-400 dark:text-white/40">Hrs</span>
				</div>
			</div>
			<div class="bg-[#064e3b] dark:bg-emerald-500 rounded-xl p-5 shadow-sm relative overflow-hidden">
				<p class="text-[11px] text-white/60 dark:text-white/50 font-medium">TARGET HOURS</p>
				<p class="text-2xl font-bold text-white dark:text-white mt-2">{{ rosterStore.targetHours.toFixed(1) }}</p>
				<p class="text-xs text-white/60 dark:text-white/40 mt-2 flex items-center gap-1">
					<span class="material-symbols-outlined text-sm">info</span>
					{{ rosterStore.remainingHours.toFixed(1) }} hours remaining
				</p>
				<span
					class="material-symbols-outlined absolute right-2 bottom-2 text-white/10 dark:text-white/20 text-7xl"
					>star</span
				>
			</div>
		</div>

		<!-- Navigation Bar -->
		<div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
			<div class="flex items-center gap-3 flex-wrap">
				<!-- Employee filter for Shift Approvers -->
				<div v-if="isShiftApprover && rosterStore.addRosterEmployees.length > 0" class="flex items-center gap-1 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-1">
					<span class="material-symbols-outlined text-gray-500 dark:text-white/50 text-sm pl-2">person</span>
					<select
						v-model="selectedEmployee"
						class="px-2 py-1.5 bg-transparent border-0 text-sm font-semibold text-gray-700 dark:text-white focus:outline-none focus:ring-0 cursor-pointer max-w-[200px] dark:bg-transparent"
					>
						<option v-for="emp in rosterStore.addRosterEmployees" :key="emp.name" :value="emp.name" class="dark:bg-gray-800">
							{{ emp.employee_name }}
						</option>
					</select>
				</div>

				<button
					@click="goToToday"
					class="px-4 py-2 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg text-sm font-medium text-gray-700 dark:text-white"
				>
					Today
				</button>
				<!-- Weekly/Monthly toggle -->
				<div class="flex items-center gap-1 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg p-1">
					<button
						@click="viewMode = 'weekly'"
						:class="viewMode === 'weekly' ? 'bg-[#064e3b] text-white' : 'text-gray-600 dark:text-white/50 hover:bg-gray-100 dark:hover:bg-white/10'"
						class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors"
					>
						Weekly
					</button>
					<button
						@click="viewMode = 'monthly'"
						:class="viewMode === 'monthly' ? 'bg-[#064e3b] text-white' : 'text-gray-600 dark:text-white/50 hover:bg-gray-100 dark:hover:bg-white/10'"
						class="px-3 py-1.5 text-xs font-semibold rounded-md transition-colors"
					>
						Monthly
					</button>
				</div>
				<div
					class="flex items-center gap-1 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg"
				>
					<button
						@click="goToPrev"
						class="p-2 hover:bg-gray-50 dark:hover:bg-white/5 rounded-l-lg transition-colors"
					>
						<span class="material-symbols-outlined text-gray-500 dark:text-white/50 text-sm"
							>chevron_left</span
						>
					</button>
					<span class="text-sm font-medium text-gray-700 dark:text-white px-3 min-w-[140px] text-center">{{
						rangeDisplay
					}}</span>
					<button
						@click="goToNext"
						class="p-2 hover:bg-gray-50 dark:hover:bg-white/5 rounded-r-lg transition-colors"
					>
						<span class="material-symbols-outlined text-gray-500 dark:text-white/50 text-sm"
							>chevron_right</span
						>
					</button>
				</div>
			</div>
			<div class="flex items-center gap-3 flex-wrap lg:justify-end w-full lg:w-auto">
				<!-- <button
					class="flex items-center gap-1 px-3 py-2 text-gray-500 text-sm font-medium"
				>
					<span class="material-symbols-outlined text-sm">filter_list</span>
					Filter
				</button> -->
				<button
					v-if="canAddRoster"
					@click="openRosterModal"
					class="px-4 py-2 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 text-gray-700 dark:text-white rounded-lg text-sm font-medium flex items-center gap-1 hover:bg-gray-50 dark:hover:bg-white/5"
				>
					<span class="material-symbols-outlined text-sm">assignment_add</span>
					Add Roster
				</button>
				<button
					v-if="employeeStore.employee?.name"
					@click="openRequestModal()"
					class="px-4 py-2 bg-[#064e3b] dark:bg-emerald-500 text-white rounded-lg text-sm font-medium flex items-center gap-1"
				>
					<span class="material-symbols-outlined text-sm">add</span>
					Shift request
				</button>
			</div>
		</div>

		<!-- Day Cards — horizontal scroll -->
		<div v-if="viewMode === 'weekly'"
			ref="scrollContainer"
			class="flex gap-4 overflow-x-auto pb-4 select-none cursor-grab active:cursor-grabbing"
			:class="isMouseDown ? 'snap-none' : 'snap-x snap-mandatory'"
			@mousedown="handleMouseDown"
			@mouseleave="handleMouseLeave"
			@mouseup="handleMouseUp"
			@mousemove="handleMouseMove"
		>
			<div
				v-for="day in rosterStore.weeklySchedule"
				:key="day.date"
				class="bg-white dark:bg-white/5 rounded-xl p-5 shadow-sm border-2 transition-all min-w-[180px] w-[180px] snap-start flex flex-col"
				:data-today="day.is_today"
				:class="[
					day.is_today ? 'border-[#064e3b] dark:border-emerald-400' : 'border-transparent',
					day.status === 'holiday' ? 'bg-blue-50 dark:bg-blue-500/10' : '',
					day.status === 'pending' ? 'bg-orange-50 dark:bg-orange-500/10' : '',
				]"
			>
				<!-- Day Header -->
				<div class="flex items-center justify-between mb-4">
					<div>
						<p class="text-[10px] font-medium text-gray-400 dark:text-white/40 uppercase">
							{{ day.day_short }}
						</p>
						<p class="text-2xl font-bold text-gray-900 dark:text-white">{{ day.day_num }}</p>
					</div>
					<div class="flex items-center gap-1.5">
						<span
							v-if="day.is_today"
							class="bg-[#064e3b] text-white text-[10px] font-semibold px-2.5 py-1 rounded-full"
							>TODAY</span
						>
						<button
							v-if="canAddRoster && (allowMultipleShifts || day.status === 'pending' || day.status === 'holiday')"
							@click.stop="openAddRosterForDate(day.date)"
							class="p-1 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full text-gray-500 dark:text-white/70 hover:text-[#064e3b] dark:hover:text-emerald-400 flex items-center justify-center transition-colors"
							title="Assign Shift"
						>
							<span class="material-symbols-outlined text-lg">add</span>
						</button>
					</div>
				</div>

				<!-- Holiday -->
				<div
					v-if="day.status === 'holiday'"
					class="flex-1 flex flex-col items-center justify-center text-blue-700 dark:text-blue-400"
				>
					<span class="material-symbols-outlined text-3xl">celebration</span>
					<p class="text-sm font-semibold text-blue-600 dark:text-blue-400">{{ day.shift?.shift_name || day.shift?.name }}</p>
					<p class="text-xs text-blue-500 dark:text-blue-400 mt-1">Holiday</p>
				</div>

				<!-- Pending (Yet to assign) -->
				<div
					v-else-if="day.status === 'pending'"
					class="flex-1 flex flex-col items-center justify-center text-orange-700 dark:text-orange-400"
				>
					<span class="material-symbols-outlined text-3xl">schedule</span>
					<p class="text-sm font-semibold text-orange-600 dark:text-orange-400">{{ day.shift?.shift_name || day.shift?.name }}</p>
					<p class="text-xs text-orange-500 dark:text-orange-400 mt-1">Pending</p>
				</div>

				<!-- On Leave -->
				<div
					v-else-if="day.status === 'on_leave'"
					class="flex-1 flex flex-col items-center justify-center text-amber-700 dark:text-amber-400"
				>
					<span class="material-symbols-outlined text-3xl">park</span>
					<p class="text-sm font-semibold text-amber-600 dark:text-amber-400">{{ day.shift?.shift_name || day.shift?.name }}</p>
					<p class="text-xs text-amber-500 dark:text-amber-400 mt-1">Approved Leave</p>
				</div>

				<!-- Shift Info -->
				<div v-else class="flex-1 flex flex-col gap-2">
					<div
						v-for="(sh, idx) in (day.shifts || [day.shift])"
						:key="(sh?.shift_assignment || sh?.name) + idx"
						class="bg-gray-50 dark:bg-white/5 rounded-lg p-3 flex justify-between items-start"
						:class="day.is_today ? 'bg-[#f0f7f4] dark:bg-emerald-500/15 border border-emerald-500/20' : ''"
					>
						<div>
							<p class="text-[10px] font-bold text-[#064e3b] dark:text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1" v-if="day.is_today && idx === 0">
								<span class="material-symbols-outlined text-xs align-middle">schedule</span>
								Active Shift
							</p>
							<p class="text-[10px] font-bold text-[#064e3b] dark:text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1" v-else-if="day.is_today">
								<span class="material-symbols-outlined text-xs align-middle">schedule</span>
								Additional Shift
							</p>
							<p class="text-sm font-semibold text-gray-900 dark:text-white">{{ sh?.shift_name || sh?.name || "—" }}</p>
							<p class="text-xs text-gray-500 dark:text-white/50 mt-1">
								{{ sh?.start_time && sh?.end_time ? `${sh.start_time.slice(0, 5)} – ${sh.end_time.slice(0, 5)}` : "—" }}
							</p>
						</div>
						<button
							v-if="canDeleteRoster && sh?.shift_assignment"
							@click="onDeleteRoster(sh.shift_assignment)"
							class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-1 rounded hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors cursor-pointer shrink-0 ml-2"
							title="Delete Shift Assignment"
						>
							<span class="material-symbols-outlined text-lg">delete</span>
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- Monthly View — 7-column calendar grid -->
		<div v-if="viewMode === 'monthly'" class="bg-white dark:bg-white/5 rounded-xl shadow-sm overflow-hidden">
			<!-- Loading -->
			<div v-if="rosterStore.monthlyLoading" class="p-8 text-center">
				<p class="text-gray-400 dark:text-white/40 text-sm">Loading...</p>
			</div>
			<div v-else>
				<!-- Day-of-week header -->
				<div class="grid grid-cols-7 border-b border-gray-100 dark:border-white/10">
					<div
						v-for="dow in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']"
						:key="dow"
						class="py-3 text-center text-xs font-semibold text-gray-400 dark:text-white/40 uppercase tracking-wider"
					>
						{{ dow }}
					</div>
				</div>

				<!-- Calendar rows — 5 or 6 rows of 7 cells -->
				<template v-for="week in calendarWeeks" :key="week[0].date">
					<div class="grid grid-cols-7 border-b border-gray-50 dark:border-white/5 last:border-b-0">
						<div
							v-for="day in week"
							:key="day.date"
							class="min-h-[72px] p-2 border-r border-gray-50 dark:border-white/5 last:border-r-0 transition-colors"
							:class="[
								day.is_today ? 'bg-emerald-50/50 dark:bg-emerald-500/10' : '',
								!day.is_current_month ? 'bg-gray-50/30 dark:bg-white/[0.02]' : '',
								day.status === 'holiday' && day.is_current_month ? 'bg-blue-50/30 dark:bg-blue-500/5' : '',
								day.status === 'pending' && day.is_current_month ? 'bg-orange-50/30 dark:bg-orange-500/5' : '',
							]"
						>
							<!-- Date + Today badge -->
							<div class="flex items-center justify-between mb-1">
								<span
									class="text-sm font-semibold leading-none"
									:class="!day.is_current_month ? 'text-gray-300 dark:text-white/20' : day.is_today ? 'text-white bg-[#064e3b] dark:bg-emerald-500 rounded-full w-6 h-6 flex items-center justify-center' : 'text-gray-700 dark:text-white'"
								>
									{{ day.day_num }}
								</span>
								<div class="flex items-center gap-1">
									<button
										v-if="canAddRoster && day.is_current_month && (allowMultipleShifts || day.status === 'pending' || day.status === 'holiday')"
										@click.stop="openAddRosterForDate(day.date)"
										class="p-0.5 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full text-gray-400 hover:text-[#064e3b] dark:hover:text-emerald-400 flex items-center justify-center transition-colors"
										title="Assign Shift"
									>
										<span class="material-symbols-outlined text-sm">add</span>
									</button>
									<span v-if="day.is_today && !day.is_current_month" class="bg-[#064e3b] text-white text-[8px] font-semibold px-1.5 py-0.5 rounded-full">
										TODAY
									</span>
								</div>
							</div>

							<!-- Off Day (non-current month fillers) -->
							<div v-if="!day.is_current_month"
								class="flex-1 flex items-center justify-center mt-1"
							>
								<span class="text-[10px] text-gray-300 dark:text-white/10">—</span>
							</div>

							<!-- Holiday -->
							<div v-else-if="day.status === 'holiday'" class="mt-0.5">
								<p class="text-[10px] font-semibold text-blue-600 dark:text-blue-400 leading-tight truncate" :title="day.shift?.shift_name || day.shift?.name">
									{{ day.shift?.shift_name || day.shift?.name }}
								</p>
								<p class="text-[9px] text-blue-500 dark:text-blue-400 mt-0.5 flex items-center gap-0.5">
									<span class="material-symbols-outlined text-[10px]">celebration</span>Holiday
								</p>
							</div>

							<!-- Pending -->
							<div v-else-if="day.status === 'pending'" class="mt-0.5">
								<p class="text-[10px] font-semibold text-orange-600 dark:text-orange-400 leading-tight truncate" :title="day.shift?.shift_name || day.shift?.name">
									{{ day.shift?.shift_name || day.shift?.name }}
								</p>
								<p class="text-[9px] text-orange-500 dark:text-orange-400 mt-0.5 flex items-center gap-0.5">
									<span class="material-symbols-outlined text-[10px]">schedule</span>Pending
								</p>
							</div>

							<!-- On Leave -->
							<div v-else-if="day.status === 'on_leave'" class="mt-0.5">
								<p class="text-[10px] font-semibold text-amber-600 dark:text-amber-400 leading-tight truncate" :title="day.shift?.shift_name || day.shift?.name">
									{{ day.shift?.shift_name || day.shift?.name }}
								</p>
								<p class="text-[9px] text-amber-500 dark:text-amber-400 mt-0.5">Leave</p>
							</div>

							<!-- Working -->
							<div v-else class="mt-0.5 space-y-1">
								<div
									v-for="(sh, idx) in (day.shifts || [day.shift])"
									:key="(sh?.shift_assignment || sh?.name) + idx"
									class="group/shift flex items-center justify-between gap-1"
								>
									<div class="truncate">
										<p class="text-[9px] font-semibold text-[#064e3b] dark:text-emerald-400 leading-tight truncate" :title="sh?.shift_name || sh?.name">
											{{ sh?.shift_name || sh?.name || "—" }}
										</p>
										<p v-if="sh?.start_time" class="text-[8px] text-gray-400 dark:text-white/40 leading-none mt-0.5">
											{{ sh.start_time.slice(0, 5) }} – {{ sh.end_time.slice(0, 5) }}
										</p>
									</div>
									<button
										v-if="canDeleteRoster && sh?.shift_assignment"
										@click.stop="onDeleteRoster(sh.shift_assignment)"
										class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-0.5 rounded opacity-0 group-hover/shift:opacity-100 transition-opacity cursor-pointer shrink-0"
										title="Delete Shift Assignment"
									>
										<span class="material-symbols-outlined text-[10px]">close</span>
									</button>
								</div>
							</div>
						</div>
					</div>
				</template>
			</div>
		</div>

		<!-- Shift Request List -->
		<div class="bg-white dark:bg-white/5 rounded-xl shadow-sm">
			<div class="px-6 py-4 border-b border-gray-100 dark:border-white/10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
				<div>
					<h2 class="text-lg font-bold text-gray-900 dark:text-white">Shift Requests</h2>
					<p class="text-sm text-gray-500 dark:text-white/50 mt-1">Your shift change requests and their status</p>
				</div>
				<!-- Filters -->
				<div class="flex items-center gap-3 flex-wrap">
					<!-- Employee Filter (Shown only for Shift Approvers) -->
					<div v-if="isShiftApprover" class="flex flex-col min-w-[150px]">
						<select
							v-model="filterEmployee"
							class="px-3 py-1.5 border border-gray-200 dark:border-white/10 rounded-lg bg-white dark:bg-gray-800 text-xs font-semibold text-gray-700 dark:text-white/80 focus:outline-none focus:ring-2 focus:ring-[#064e3b]"
						>
							<option value="">All Employees</option>
							<option v-for="emp in rosterStore.addRosterEmployees" :key="emp.name" :value="emp.name">
								{{ emp.employee_name }}
							</option>
						</select>
					</div>

					<!-- Status Filter -->
					<div class="flex flex-col min-w-[120px]">
						<select
							v-model="filterStatus"
							class="px-3 py-1.5 border border-gray-200 dark:border-white/10 rounded-lg bg-white dark:bg-gray-800 text-xs font-semibold text-gray-700 dark:text-white/80 focus:outline-none focus:ring-2 focus:ring-[#064e3b]"
						>
							<option value="">All Statuses</option>
							<option value="Draft">Draft</option>
							<option value="Approved">Approved</option>
							<option value="Rejected">Rejected</option>
						</select>
					</div>
				</div>
			</div>

			<div v-if="rosterStore.shiftRequestLoading" class="px-6 py-8 text-center">
				<p class="text-gray-400 dark:text-white/40 text-sm">Loading requests...</p>
			</div>
			<div v-else-if="rosterStore.shiftRequests.length === 0" class="px-6 py-8 text-center">
				<p class="text-gray-400 dark:text-white/40 text-sm">No shift requests yet</p>
				<button
					@click="openRequestModal()"
					class="mt-3 text-sm text-[#064e3b] dark:text-emerald-400 font-medium hover:underline"
				>
					Create your Shift request →
				</button>
			</div>
			<div v-else-if="filteredShiftRequests.length === 0" class="px-6 py-8 text-center">
				<p class="text-gray-400 dark:text-white/40 text-sm">No matching shift requests</p>
			</div>
			<div v-else class="overflow-x-auto">
				<table class="w-full text-left border-collapse">
					<thead>
						<tr class="border-b border-gray-100 dark:border-white/10 bg-gray-50/50 dark:bg-white/[0.02]">
							<th class="px-6 py-3 text-xs font-bold text-gray-500 dark:text-white/40 uppercase tracking-wider">Reference</th>
							<th class="px-6 py-3 text-xs font-bold text-gray-500 dark:text-white/40 uppercase tracking-wider">Employee Name</th>
							<th class="px-6 py-3 text-xs font-bold text-gray-500 dark:text-white/40 uppercase tracking-wider">Shift Request</th>
							<th class="px-6 py-3 text-xs font-bold text-gray-500 dark:text-white/40 uppercase tracking-wider">Status</th>
							<th class="px-6 py-3 text-xs font-bold text-gray-500 dark:text-white/40 uppercase tracking-wider text-right">Actions</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-100 dark:divide-white/10">
						<tr
							v-for="req in paginatedShiftRequests"
							:key="req.name"
							class="hover:bg-gray-50/50 dark:hover:bg-white/[0.01] transition-colors"
						>
							<!-- Reference -->
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="text-xs font-semibold text-gray-600 dark:text-gray-300 font-mono bg-gray-50 dark:bg-white/5 px-2.5 py-1 rounded-md border border-gray-100 dark:border-white/5">
									{{ req.name }}
								</span>
							</td>

							<!-- Employee Name -->
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="text-sm font-semibold text-gray-900 dark:text-white">
									{{ req.employee_name || req.employee }}
								</span>
							</td>

							<!-- Shift Request -->
							<td class="px-6 py-4 whitespace-nowrap">
								<div>
									<p class="text-sm font-semibold text-gray-900 dark:text-white">
										{{ req.shift_type }}
									</p>
									<p class="text-xs text-gray-500 dark:text-white/50 mt-0.5">
										{{ formatDate(req.from_date) }}
										<span v-if="req.to_date && req.to_date !== req.from_date"> — {{ formatDate(req.to_date) }}</span>
									</p>
								</div>
							</td>

							<!-- Status -->
							<td class="px-6 py-4 whitespace-nowrap">
								<span
									class="text-xs font-medium px-2.5 py-1 rounded-full inline-flex items-center gap-1"
									:class="{
										'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400': req.status === 'Draft',
										'bg-[#064e3b]/10 text-[#064e3b] dark:bg-emerald-500/20 dark:text-emerald-400': req.status === 'Approved',
										'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400': req.status === 'Rejected',
									}"
								>
									<span class="w-1.5 h-1.5 rounded-full" :class="{
										'bg-amber-500': req.status === 'Draft',
										'bg-emerald-500': req.status === 'Approved',
										'bg-red-500': req.status === 'Rejected',
									}"></span>
									{{ req.status }}
								</span>
							</td>

							<!-- Actions -->
							<td class="px-6 py-4 whitespace-nowrap text-right">
								<div v-if="req.status === 'Draft' && (req.employee === employeeStore.employee?.name || req.can_approve)" class="inline-block text-left relative">
									<button
										@click.stop="toggleDropdown(req.name)"
										class="inline-flex items-center gap-1 px-2.5 py-1.5 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-lg text-xs font-semibold text-gray-700 dark:text-white/80 hover:bg-gray-50 dark:hover:bg-white/10 transition-colors"
									>
										<span>More</span>
										<span class="material-symbols-outlined text-xs">expand_more</span>
									</button>

									<!-- Dropdown Menu -->
									<div
										v-if="activeDropdown === req.name"
										class="absolute right-0 mt-1 w-32 bg-white dark:bg-[#1f2937] border border-gray-200 dark:border-white/10 rounded-lg shadow-lg z-20 py-1 text-left"
									>
										<!-- Approve option -->
										<button
											v-if="req.can_approve"
											@click="handleApproveReject(req.name, 'Approved')"
											:disabled="updatingStatusId === req.name"
											class="w-full text-left px-3 py-2 text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 flex items-center gap-2 transition-colors disabled:opacity-50"
										>
											<span v-if="updatingStatusId === req.name && targetStatus === 'Approved'" class="material-symbols-outlined text-sm animate-spin text-emerald-500">refresh</span>
											<span v-else class="material-symbols-outlined text-sm text-emerald-500">check</span>
											<span>Approve</span>
										</button>

										<!-- Reject option -->
										<button
											v-if="req.can_approve"
											@click="handleApproveReject(req.name, 'Rejected')"
											:disabled="updatingStatusId === req.name"
											class="w-full text-left px-3 py-2 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 flex items-center gap-2 transition-colors disabled:opacity-50"
										>
											<span v-if="updatingStatusId === req.name && targetStatus === 'Rejected'" class="material-symbols-outlined text-sm animate-spin text-red-500">refresh</span>
											<span v-else class="material-symbols-outlined text-sm text-red-400">close</span>
											<span>Reject</span>
										</button>

										<!-- Divider if both are present -->
										<div v-if="req.can_approve && req.employee === employeeStore.employee?.name" class="border-t border-gray-100 dark:border-white/10 my-1"></div>

										<!-- Edit option -->
										<button
											v-if="req.employee === employeeStore.employee?.name"
											@click="handleEdit(req.name)"
											class="w-full text-left px-3 py-2 text-xs font-medium text-gray-700 dark:text-white/80 hover:bg-gray-50 dark:hover:bg-white/5 flex items-center gap-2 transition-colors"
										>
											<span class="material-symbols-outlined text-sm text-gray-400">edit</span>
											<span>Edit</span>
										</button>

										<!-- Delete option -->
										<button
											v-if="req.employee === employeeStore.employee?.name"
											@click="handleDelete(req.name)"
											:disabled="rosterStore.cancelingId === req.name"
											class="w-full text-left px-3 py-2 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 flex items-center gap-2 transition-colors disabled:opacity-50"
										>
											<span v-if="rosterStore.cancelingId === req.name" class="material-symbols-outlined text-sm animate-spin text-red-500">refresh</span>
											<span v-else class="material-symbols-outlined text-sm text-red-400">delete</span>
											<span>Delete</span>
										</button>
									</div>
								</div>
							</td>
						</tr>
					</tbody>
				</table>

				<!-- Pagination controls -->
				<div v-if="filteredShiftRequests.length > 0" class="px-6 py-4 border-t border-gray-100 dark:border-white/10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gray-50/50 dark:bg-white/[0.01] rounded-b-xl">
					<div class="flex items-center gap-2">
						<span class="text-xs text-gray-500 dark:text-white/50">Rows per page:</span>
						<select
							v-model="pageSize"
							class="px-3 py-1 border border-gray-200 dark:border-white/10 rounded-lg bg-white dark:bg-gray-800 text-xs font-semibold text-gray-700 dark:text-white/80 focus:outline-none focus:ring-1 focus:ring-[#064e3b] cursor-pointer min-w-[70px]"
						>
							<option :value="10">10</option>
							<option :value="20">20</option>
							<option :value="50">50</option>
						</select>
					</div>

					<div class="flex items-center gap-4">
						<span class="text-xs text-gray-500 dark:text-white/50">
							Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredShiftRequests.length) }} of {{ filteredShiftRequests.length }}
						</span>

						<div class="flex items-center gap-1">
							<button
								@click="prevPage"
								:disabled="currentPage === 1"
								class="p-1 hover:bg-gray-50 dark:hover:bg-white/5 border border-gray-200 dark:border-white/10 rounded transition-colors disabled:opacity-50 flex items-center justify-center"
							>
								<span class="material-symbols-outlined text-gray-500 dark:text-white/50 text-sm align-middle">chevron_left</span>
							</button>
							<button
								@click="nextPage"
								:disabled="currentPage === totalPages"
								class="p-1 hover:bg-gray-50 dark:hover:bg-white/5 border border-gray-200 dark:border-white/10 rounded transition-colors disabled:opacity-50 flex items-center justify-center"
							>
								<span class="material-symbols-outlined text-gray-500 dark:text-white/50 text-sm align-middle">chevron_right</span>
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

		<!-- Shift Assignment Tab -->
		<div v-if="activeTab === 'assignment'" class="space-y-8">
			<!-- Add Shift Assignment Button -->
			<div class="flex justify-end px-2 mb-2" v-if="canAddRoster">
				<button
					@click="openRosterModal"
					class="px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-[#064e3b] dark:bg-emerald-500 text-white shadow-glow-emerald"
				>
					<span class="material-symbols-outlined text-lg">add_circle</span>Add Shift Assignment
				</button>
			</div>

			<!-- Filters -->
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8 px-2">
				<div>
					<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">Shift Assignments</h1>
					<p class="text-gray-500 dark:text-gray-400 font-medium font-sans">Manage shift assignments and scheduling details.</p>
				</div>
				<div class="flex items-center gap-4 flex-wrap">
					<div v-if="isShiftApprover && rosterStore.addRosterEmployees.length > 0" class="flex items-center gap-2">
						<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Employee:</label>
						<div class="relative">
							<select v-model="selectedEmployeeAssignment" class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[200px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
								<option value="">All Employees</option>
								<option v-for="emp in rosterStore.addRosterEmployees" :key="emp.name" :value="emp.name">{{ emp.employee_name }}</option>
							</select>
							<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Month:</label>
						<div class="relative">
							<select v-model="selectedMonthKeyAssignment" class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[180px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
								<option v-for="opt in monthOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
							</select>
							<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Shift Assignment Table -->
			<div class="premium-card !p-0 overflow-hidden border border-gray-100 dark:border-gray-800 shadow-sm mt-8">
				<div v-if="shiftAssignmentsResource.loading" class="flex items-center justify-center py-20">
					<span class="text-sm font-bold text-gray-400 dark:text-gray-500">Loading assignments…</span>
				</div>
				<div v-else-if="!shiftAssignmentsResource.data || shiftAssignmentsResource.data.length === 0" class="flex items-center justify-center py-20">
					<span class="text-sm font-bold text-gray-400 dark:text-gray-500">No shift assignments for this period.</span>
				</div>
				<div v-else class="overflow-x-auto">
					<table class="w-full text-left">
						<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-800/50">
							<tr>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Reference</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Employee</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Shift Type</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Period</th>
								<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Location</th>
								<th v-if="canDeleteRoster" class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-50 dark:divide-gray-800">
							<tr v-for="record in paginatedAssignments" :key="record.name" class="transition-colors hover:bg-gray-50/50 dark:hover:bg-white/[0.01]">
								<!-- Reference ID -->
								<td class="px-10 py-6">
									<span class="text-xs font-semibold text-gray-600 dark:text-gray-300 font-mono bg-gray-50 dark:bg-white/5 px-2.5 py-1 rounded-md border border-gray-100 dark:border-white/5">
										{{ record.name }}
									</span>
								</td>
								<!-- Employee Name -->
								<td class="px-10 py-6">
									<p class="text-sm font-black text-gray-900 dark:text-white tracking-tight">{{ record.employee_name || record.employee }}</p>
								</td>
								<!-- Shift Type -->
								<td class="px-10 py-6">
									<p class="text-sm font-black text-gray-900 dark:text-white tracking-tight">{{ record.shift_type }}</p>
								</td>
								<!-- Period -->
								<td class="px-10 py-6">
									<p class="text-sm font-black text-gray-900 dark:text-white">
										{{ formatDate(record.start_date) }}
										<span v-if="record.end_date"> — {{ formatDate(record.end_date) }}</span>
										<span v-else class="text-xs text-gray-400 dark:text-white/40"> (Ongoing)</span>
									</p>
								</td>
								<!-- Shift Location -->
								<td class="px-10 py-6">
									<p class="text-sm font-medium text-gray-600 dark:text-gray-300">{{ record.location_name || record.shift_location || "—" }}</p>
								</td>
								<!-- Actions -->
								<td v-if="canDeleteRoster" class="px-10 py-6 text-center">
									<button
										@click="onDeleteRoster(record.name)"
										class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors cursor-pointer inline-flex items-center justify-center"
										title="Delete Shift Assignment"
									>
										<span class="material-symbols-outlined text-lg">delete</span>
									</button>
								</td>
							</tr>
						</tbody>
					</table>

					<!-- Pagination Footer -->
					<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-10 py-5 border-t border-gray-50 dark:border-gray-800 bg-gray-50/10 dark:bg-gray-800/10">
						<!-- Page Size Dropdown -->
						<div class="flex items-center gap-2">
							<label class="text-xs text-gray-500 dark:text-gray-400 font-bold whitespace-nowrap">Rows per page:</label>
							<div class="relative">
								<select v-model.number="pageSizeAssignment" class="appearance-none w-20 pr-8 pl-3 py-1.5 text-xs font-bold cursor-pointer border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100" @change="currentPageAssignment = 1">
									<option :value="10">10</option>
									<option :value="20">20</option>
									<option :value="50">50</option>
								</select>
								<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
							</div>
						</div>

						<!-- Showing X-Y of Z and navigation buttons -->
						<div class="flex items-center justify-between sm:justify-end gap-6 flex-1">
							<span class="text-xs text-gray-500 dark:text-gray-400 font-bold tabular-nums">
								Showing {{ Math.min((currentPageAssignment - 1) * Number(pageSizeAssignment) + 1, totalAssignments) }} - {{ Math.min(currentPageAssignment * Number(pageSizeAssignment), totalAssignments) }} of {{ totalAssignments }} records
							</span>
							<div class="flex items-center gap-1">
								<button 
									@click="prevPageAssignment" 
									:disabled="currentPageAssignment === 1"
									class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
								>
									<span class="material-symbols-outlined text-sm font-bold">chevron_left</span>
								</button>
								<button 
									@click="nextPageAssignment" 
									:disabled="currentPageAssignment === totalPagesAssignment"
									class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
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

	<!-- Request Change Modal -->
	<Teleport to="body">
		<div
			v-if="rosterStore.showRequestModal"
			class="fixed inset-0 z-50 flex items-center justify-center p-4"
		>
			<!-- Backdrop -->
			<div
				class="absolute inset-0 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
				@click="rosterStore.closeRequestModal()"
			></div>

			<!-- Modal content -->
			<div class="relative bg-white dark:bg-white/5 rounded-xl shadow-xl w-full max-w-md p-6">
				<!-- Header -->
				<div class="flex items-center justify-between mb-6">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">
						{{ rosterStore.editingRequestId ? 'Edit Shift Request' : 'Request Shift Change' }}
					</h3>
					<button
						@click="rosterStore.closeRequestModal()"
						class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-white/5 rounded-lg"
					>
						<span class="material-symbols-outlined text-sm">close</span>
					</button>
				</div>

				<!-- Approver Info -->
				<p class="text-sm text-gray-500 dark:text-white/50 mb-5">
					Approved by:
					<span class="font-semibold text-gray-900 dark:text-white">
						{{ rosterStore.approverInfo ? rosterStore.approverInfo.name : 'Please set shift request approver' }}
					</span>
				</p>

				<!-- Form -->
				<form @submit.prevent="handleSubmit" class="space-y-4">
					<!-- Shift Type -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							Shift Type <span class="text-red-500">*</span>
						</label>
						<select
							v-model="form.shift_type"
							:disabled="submitting || rosterStore.shiftTypes.length === 0"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<option value="" disabled>{{ rosterStore.shiftTypes.length > 0 ? 'Select shift type' : 'No shift types available' }}</option>
							<option v-for="st in rosterStore.shiftTypes" :key="st.name" :value="st.name">
								{{ st.name }}
							</option>
						</select>
						<p v-if="rosterStore.shiftTypes.length === 0" class="text-xs text-gray-400 dark:text-white/40 mt-1">
							Contact admin to configure shift types
						</p>
					</div>

					<!-- From Date -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							From Date <span class="text-red-500">*</span>
						</label>
						<input
							type="date"
							v-model="form.from_date"
							:disabled="submitting"
							:min="today"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50"
						/>
					</div>

					<!-- To Date -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							To Date
						</label>
						<input
							type="date"
							v-model="form.to_date"
							:disabled="submitting"
							:min="form.from_date || today"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50"
						/>
						<p class="text-xs text-gray-400 dark:text-white/40 mt-1">Leave empty to request for single day</p>
					</div>

					<!-- Submission error -->
					<div v-if="rosterStore.submissionError" class="p-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-lg">
						<p class="text-sm text-red-700 dark:text-red-400">{{ rosterStore.submissionError }}</p>
					</div>

					<!-- Buttons -->
					<div class="flex items-center gap-3 pt-2">
						<button
							type="submit"
							:disabled="!canSubmit || submitting"
							class="flex-1 py-2.5 bg-[#064e3b] text-white rounded-lg text-sm font-semibold disabled:opacity-50 hover:bg-[#043a2d] transition-colors flex items-center justify-center gap-1"
						>
							<span v-if="submitting" class="material-symbols-outlined text-sm animate-spin">refresh</span>
							{{ submitting ? 'Submitting...' : (rosterStore.editingRequestId ? 'Update Request' : 'Submit Request') }}
						</button>
						<button
							type="button"
							@click="rosterStore.closeRequestModal()"
							:disabled="submitting"
							class="px-5 py-2.5 border border-gray-300 dark:border-white/20 text-gray-700 dark:text-white/70 rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
						>
							Cancel
						</button>
					</div>
				</form>
			</div>
		</div>

		<!-- Add Roster Modal -->
		<div
			v-if="rosterStore.showAddRosterModal"
			class="fixed inset-0 z-50 flex items-center justify-center p-4"
		>
			<!-- Backdrop -->
			<div
				class="absolute inset-0 bg-black/40 dark:bg-black/60 backdrop-blur-sm"
				@click="rosterStore.closeAddRosterModal()"
			></div>

			<!-- Modal content -->
			<div class="relative bg-white dark:bg-white/5 rounded-xl shadow-xl w-full max-w-md p-6">
				<!-- Header -->
				<div class="flex items-center justify-between mb-6">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">
						Add Roster
					</h3>
					<button
						@click="rosterStore.closeAddRosterModal()"
						class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-white/5 rounded-lg"
					>
						<span class="material-symbols-outlined text-sm">close</span>
					</button>
				</div>

				<!-- Form -->
				<form @submit.prevent="handleSaveRoster" class="space-y-4">
					<!-- Employee -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							Employee <span class="text-red-500">*</span>
						</label>
						<select
							v-model="rosterStore.addRosterForm.employee"
							:disabled="rosterStore.addRosterSubmitting || rosterStore.addRosterEmployees.length === 0"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<option value="" disabled>{{ rosterStore.addRosterEmployees.length > 0 ? 'Select employee' : 'No employees available' }}</option>
							<option v-for="emp in rosterStore.addRosterEmployees" :key="emp.name" :value="emp.name">
								{{ emp.employee_name }} ({{ emp.name }})
							</option>
						</select>
					</div>

					<!-- Shift Type -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							Shift Type <span class="text-red-500">*</span>
						</label>
						<select
							v-model="rosterStore.addRosterForm.shift_type"
							:disabled="rosterStore.addRosterSubmitting || rosterStore.shiftTypes.length === 0"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
						>
							<option value="" disabled>{{ rosterStore.shiftTypes.length > 0 ? 'Select shift type' : 'No shift types available' }}</option>
							<option v-for="st in rosterStore.shiftTypes" :key="st.name" :value="st.name">
								{{ st.name }}
							</option>
						</select>
					</div>

					<!-- From Date -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							From Date <span class="text-red-500">*</span>
						</label>
						<input
							type="date"
							v-model="rosterStore.addRosterForm.start_date"
							:disabled="rosterStore.addRosterSubmitting"
							:min="today"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50"
						/>
					</div>

					<!-- To Date -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							To Date
						</label>
						<input
							type="date"
							v-model="rosterStore.addRosterForm.end_date"
							:disabled="rosterStore.addRosterSubmitting"
							:min="rosterStore.addRosterForm.start_date || today"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50"
						/>
						<p class="text-xs text-gray-400 dark:text-white/40 mt-1">Leave empty for single day</p>
					</div>

					<!-- Shift Location -->
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-white/70 mb-1.5">
							Shift Location
						</label>
						<select
							v-model="rosterStore.addRosterForm.shift_location"
							:disabled="rosterStore.addRosterSubmitting"
							class="w-full px-3 py-2.5 border border-gray-300 dark:border-white/20 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#064e3b] focus:border-transparent disabled:opacity-50"
						>
							<option value="">Select shift location (Optional)</option>
							<option v-for="loc in rosterStore.shiftLocations" :key="loc.name" :value="loc.name">
								{{ loc.location_name || loc.name }}
							</option>
						</select>
					</div>

					<!-- Submission error -->
					<div v-if="rosterStore.addRosterError" class="p-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-lg">
						<p class="text-sm text-red-700 dark:text-red-400">{{ rosterStore.addRosterError }}</p>
					</div>

					<!-- Buttons -->
					<div class="flex items-center gap-3 pt-2">
						<button
							type="submit"
							:disabled="!rosterStore.addRosterForm.employee || !rosterStore.addRosterForm.shift_type || !rosterStore.addRosterForm.start_date || rosterStore.addRosterSubmitting"
							class="flex-1 py-2.5 bg-[#064e3b] text-white rounded-lg text-sm font-semibold disabled:opacity-50 hover:bg-[#043a2d] transition-colors flex items-center justify-center gap-1"
						>
							<span v-if="rosterStore.addRosterSubmitting" class="material-symbols-outlined text-sm animate-spin">refresh</span>
							{{ rosterStore.addRosterSubmitting ? 'Creating...' : 'Add Roster' }}
						</button>
						<button
							type="button"
							@click="rosterStore.closeAddRosterModal()"
							:disabled="rosterStore.addRosterSubmitting"
							class="px-5 py-2.5 border border-gray-300 dark:border-white/20 text-gray-700 dark:text-white/70 rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
						>
							Cancel
						</button>
					</div>
				</form>
			</div>
		</div>
	</Teleport>
	
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import { createResource } from "frappe-ui";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";
import { useRosterStore } from "@/stores/roster";

const employeeStore = useEmployeeStore();
const attendanceStore = useAttendanceStore();
const rosterStore = useRosterStore();
const scrollContainer = ref(null);

// Tab State
const activeTab = ref("dashboard");

// Shift Assignment Tab State
const selectedEmployeeAssignment = ref("");
const _todayDate = new Date();
const selectedMonthAssignment = ref(_todayDate.getMonth() + 1);
const selectedYearAssignment = ref(_todayDate.getFullYear());

const selectedMonthKeyAssignment = computed({
	get: () => `${selectedYearAssignment.value}-${selectedMonthAssignment.value}`,
	set: (val) => {
		const [y, m] = val.split("-").map(Number);
		selectedYearAssignment.value = y;
		selectedMonthAssignment.value = m;
	},
});

const monthOptions = computed(() => {
	const opts = [];
	const now = new Date();
	for (let offset = -12; offset <= 2; offset++) {
		const d = new Date(now.getFullYear(), now.getMonth() + offset, 1);
		const m = d.getMonth() + 1;
		const y = d.getFullYear();
		opts.push({
			value: `${y}-${m}`,
			label: d.toLocaleDateString("en-US", { month: "long", year: "numeric" }),
			month: m,
			year: y,
		});
	}
	return opts;
});

// Shift Assignments Resource
const shiftAssignmentsResource = createResource({
	url: "zevar_core.api.roster.get_shift_assignments",
	auto: false,
});

async function fetchShiftAssignments() {
	await shiftAssignmentsResource.fetch({
		employee_id: selectedEmployeeAssignment.value || undefined,
		month: selectedMonthAssignment.value,
		year: selectedYearAssignment.value,
	});
}

// Pagination for Shift Assignments
const currentPageAssignment = ref(1);
const pageSizeAssignment = ref(10);

const paginatedAssignments = computed(() => {
	const data = shiftAssignmentsResource.data || [];
	const start = (currentPageAssignment.value - 1) * pageSizeAssignment.value;
	const end = start + pageSizeAssignment.value;
	return data.slice(start, end);
});

const totalAssignments = computed(() => {
	return shiftAssignmentsResource.data?.length || 0;
});

const totalPagesAssignment = computed(() => {
	return Math.ceil(totalAssignments.value / pageSizeAssignment.value) || 1;
});

function prevPageAssignment() {
	if (currentPageAssignment.value > 1) {
		currentPageAssignment.value--;
	}
}

function nextPageAssignment() {
	if (currentPageAssignment.value < totalPagesAssignment.value) {
		currentPageAssignment.value++;
	}
}

watch(totalAssignments, () => {
	currentPageAssignment.value = 1;
});

watch([selectedEmployeeAssignment, selectedMonthAssignment, selectedYearAssignment], async () => {
	await fetchShiftAssignments();
});


const isMouseDown = ref(false);
let startX = 0;
let scrollLeft = 0;

const handleMouseDown = (e) => {
	if (!scrollContainer.value) return;
	isMouseDown.value = true;
	startX = e.pageX - scrollContainer.value.offsetLeft;
	scrollLeft = scrollContainer.value.scrollLeft;
};

const handleMouseLeave = () => {
	isMouseDown.value = false;
};

const handleMouseUp = () => {
	isMouseDown.value = false;
};

const handleMouseMove = (e) => {
	if (!isMouseDown.value || !scrollContainer.value) return;
	e.preventDefault();
	const x = e.pageX - scrollContainer.value.offsetLeft;
	const walk = (x - startX) * 1.5;
	scrollContainer.value.scrollLeft = scrollLeft - walk;
};

const canAddRoster = ref(false);
const canDeleteRoster = ref(false);
const allowMultipleShifts = ref(false);
const filterEmployee = ref("");
const filterStatus = ref("");
const isShiftApprover = ref(false);
const selectedEmployee = ref("");

// Actions Dropdown state for Shift Requests
const activeDropdown = ref(null);

const filteredShiftRequests = computed(() => {
	let requests = rosterStore.shiftRequests;
	if (filterEmployee.value) {
		requests = requests.filter(r => r.employee === filterEmployee.value);
	}
	if (filterStatus.value) {
		requests = requests.filter(r => r.status === filterStatus.value);
	}
	return requests;
});

// Pagination State for Shift Request List
const currentPage = ref(1);
const pageSize = ref(10);

const paginatedShiftRequests = computed(() => {
	const start = (currentPage.value - 1) * pageSize.value;
	const end = start + pageSize.value;
	return filteredShiftRequests.value.slice(start, end);
});

const totalPages = computed(() => {
	return Math.ceil(filteredShiftRequests.value.length / pageSize.value) || 1;
});

function prevPage() {
	if (currentPage.value > 1) {
		currentPage.value--;
	}
}

function nextPage() {
	if (currentPage.value < totalPages.value) {
		currentPage.value++;
	}
}

watch(filteredShiftRequests, () => {
	currentPage.value = 1;
});

function toggleDropdown(name) {
	if (activeDropdown.value === name) {
		activeDropdown.value = null;
	} else {
		activeDropdown.value = name;
	}
}

function handleEdit(name) {
	activeDropdown.value = null;
	openRequestModal(name);
}

async function handleDelete(name) {
	activeDropdown.value = null;
	await rosterStore.handleCancelRequest(name);
}

function closeAllDropdowns() {
	activeDropdown.value = null;
}

const updatingStatusId = ref(null);
const targetStatus = ref(null);

async function handleApproveReject(id, status) {
	updatingStatusId.value = id;
	targetStatus.value = status;
	try {
		await rosterStore.updateRequestStatus(id, status);
		if (status === "Approved") {
			await loadWeek();
		}
	} catch (err) {
		let errorMessage = "Failed to update status";
		if (err && err._server_messages) {
			try {
				const msgs = JSON.parse(err._server_messages);
				if (msgs && msgs.length > 0) {
					errorMessage = msgs[0].replace(/<[^>]*>/g, "").trim();
				}
			} catch {}
		} else if (err && err.exc && typeof err.exc === "string") {
			const lines = err.exc.trim().split('\n');
			const lastLine = lines[lines.length - 1].trim();
			if (lastLine) {
				const parts = lastLine.split(': ');
				errorMessage = parts.length > 1 ? parts[1] : lastLine;
			}
		} else if (err && err.message) {
			errorMessage = err.message;
		}
		alert(errorMessage);
	} finally {
		updatingStatusId.value = null;
		targetStatus.value = null;
	}
}



const weekStart = ref(new Date());
const monthStart = ref(new Date()); // For monthly navigation
const today = new Date().toISOString().split("T")[0];
const submitting = ref(false);
const viewMode = ref("weekly");
const form = ref({
	shift_type: "",
	from_date: "",
	to_date: "",
});

// Computed validation
const canSubmit = computed(() => {
	return form.value.shift_type && form.value.from_date && !submitting.value;
});

// Group flat monthly calendar array into rows of 7 for the grid
const calendarWeeks = computed(() => {
	const days = rosterStore.monthlyCalendar;
	if (!days.length) return [];
	const weeks = [];
	for (let i = 0; i < days.length; i += 7) {
		weeks.push(days.slice(i, i + 7));
	}
	return weeks;
});

// Range display (weekly or monthly)
const rangeDisplay = computed(() => {
	const opts = { month: "short", day: "numeric" };
	if (viewMode.value === "weekly") {
		const start = weekStart.value;
		const end = new Date(start);
		end.setDate(end.getDate() + 6);
		return `${start.toLocaleDateString("en-US", opts)} – ${end.toLocaleDateString("en-US", opts)}, ${end.getFullYear()}`;
	} else {
		const start = monthStart.value;
		return `${start.toLocaleDateString("en-US", { month: "long", year: "numeric" })}`;
	}
});

function getWeekStart(date) {
	const d = new Date(date);
	const day = d.getDay();
	const diff = d.getDate() - day + (day === 0 ? -6 : 1);
	return new Date(d.setDate(diff));
}

function toStr(date) {
	const y = date.getFullYear();
	const m = String(date.getMonth() + 1).padStart(2, "0");
	const d = String(date.getDate()).padStart(2, "0");
	return `${y}-${m}-${d}`;
}

function formatShiftTime(day) {
	if (!day.shift?.start_time) return "";
	const start = String(day.shift.start_time).slice(0, 5);
	const end = String(day.shift.end_time).slice(0, 5);
	return `${start} – ${end}`;
}

// Use attendanceStore.todayStatus — same as ClockWidget
// ClockWidget determines "complete" as: last_log_type === "OUT" && logs?.length >= 2
// This matches the backend get_today_checkin_status response exactly
const isTodayComplete = computed(() => {
	const status = attendanceStore.todayStatus;
	// Must NOT be on break — ClockWidget checks is_on_break BEFORE last_log_type
	if (status?.is_on_break) return false;
	return status?.last_log_type === "OUT" && status.logs?.length >= 2;
});

// Use attendanceStore.todayStatus for clock button
// last_log_type === null → not clocked in yet → show "CLOCK IN"
// last_log_type === "IN"  → clocked in → show "CLOCK OUT"
// last_log_type === "OUT" → shift complete → hide button
function isClockInDay(day) {
	if (!day.is_today) return false;
	if (selectedEmployee.value !== employeeStore.employee?.name) return false;
	const status = attendanceStore.todayStatus;
	if (!status) return true; // No data yet, assume not clocked in
	// Same logic as ClockWidget's else branch: nothing happened today
	return status.last_log_type !== "OUT";
}

function getClockActionLabel(day) {
	if (!day.is_today) return "";
	const logType = attendanceStore.todayStatus?.last_log_type;
	if (logType === "IN") return "CLOCK OUT";
	return "CLOCK IN";
}

function formatDate(dateStr) {
	if (!dateStr) return "";
	const d = new Date(dateStr);
	return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

async function openRequestModal(editId = null) {
	await rosterStore.fetchShiftTypes();
	if (editId) {
		// Find the request and populate form
		const req = rosterStore.shiftRequests.find(r => r.name === editId);
		if (req) {
			form.value = {
				shift_type: req.shift_type,
				from_date: req.from_date,
				to_date: req.to_date || "",
			};
		}
	} else {
		form.value = {
			shift_type: "",
			from_date: "",
			to_date: "",
		};
	}
	await rosterStore.fetchApprover(employeeStore.employee?.name);
	rosterStore.showRequestModal = true;
	rosterStore.editingRequestId = editId;
}

async function checkCanAddRoster() {
	try {
		canAddRoster.value = await rosterStore.checkCanAddRoster();
	} catch (e) {
		canAddRoster.value = false;
	}
}

async function onDeleteRoster(assignmentName) {
	if (!assignmentName) return;
	if (confirm("Are you sure you want to delete this shift assignment?")) {
		const res = await rosterStore.deleteRoster(assignmentName);
		if (!res.success) {
			alert(res.message || "Failed to delete shift assignment.");
		} else {
			if (viewMode.value === "weekly") {
				await loadWeek();
			} else {
				await loadMonth();
			}
			await fetchShiftAssignments();
		}
	}
}

async function handleSaveRoster() {
	await rosterStore.submitAddRoster(rosterStore.addRosterForm);
	if (!rosterStore.addRosterError) {
		await fetchShiftAssignments();
		if (viewMode.value === "weekly") {
			await loadWeek();
		} else {
			await loadMonth();
		}
	}
}

function openRosterModal() {
	rosterStore.openAddRosterModal(employeeStore.employee?.name || "");
}

function openAddRosterForDate(date) {
	const empId = selectedEmployee.value || employeeStore.employee?.name || "";
	rosterStore.openAddRosterModal(empId);
	rosterStore.addRosterForm.start_date = date;
	rosterStore.addRosterForm.end_date = date;
}

async function handleSubmit() {
	if (!canSubmit.value) return;
	submitting.value = true;
	try {
		await rosterStore.submitRequest({
			employee: employeeStore.employee?.name,
			shift_type: form.value.shift_type,
			from_date: form.value.from_date,
			to_date: form.value.to_date || form.value.from_date,
		});
	} finally {
		submitting.value = false;
	}
}

async function goToPrevWeek() {
	const d = new Date(weekStart.value);
	d.setDate(d.getDate() - 7);
	weekStart.value = d;
	await loadWeek();
	snapToToday();
}

async function goToNextWeek() {
	const d = new Date(weekStart.value);
	d.setDate(d.getDate() + 7);
	weekStart.value = d;
	await loadWeek();
	snapToToday();
}

async function goToPrev() {
	if (viewMode.value === "weekly") {
		const d = new Date(weekStart.value);
		d.setDate(d.getDate() - 7);
		weekStart.value = d;
		await loadWeek();
		snapToToday();
	} else {
		const d = new Date(monthStart.value);
		d.setMonth(d.getMonth() - 1);
		monthStart.value = d;
		await loadMonth();
	}
}

async function goToNext() {
	if (viewMode.value === "weekly") {
		const d = new Date(weekStart.value);
		d.setDate(d.getDate() + 7);
		weekStart.value = d;
		await loadWeek();
		snapToToday();
	} else {
		const d = new Date(monthStart.value);
		d.setMonth(d.getMonth() + 1);
		monthStart.value = d;
		await loadMonth();
	}
}

async function goToToday() {
	if (viewMode.value === "weekly") {
		weekStart.value = getWeekStart(new Date());
		await loadWeek();
		snapToToday();
	} else {
		monthStart.value = new Date();
		await loadMonth();
		await snapToToday();
	}
}

async function loadWeek() {
	const empId = selectedEmployee.value || employeeStore.employee?.name;
	if (!empId) return;
	const weekStartStr = toStr(weekStart.value);
	await rosterStore.fetchWeekly(empId, weekStartStr);
}

async function loadMonth() {
	const empId = selectedEmployee.value || employeeStore.employee?.name;
	if (!empId) return;
	const year = monthStart.value.getFullYear();
	const month = monthStart.value.getMonth() + 1; // JS months are 0-indexed, backend expects 1-12
	await rosterStore.fetchMonthly(empId, year, month);
}

async function snapToToday() {
	await nextTick();
	if (!scrollContainer.value) return;
	const todayEl = scrollContainer.value.querySelector("[data-today]");
	if (todayEl) {
		todayEl.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
	}
}

async function handleClockOut(day) {
	const empId = employeeStore.employee?.name;
	if (empId) {
		const shift = attendanceStore.todayStatus?.active_shift_name;
		await attendanceStore.clockOut(empId, null, null, null, shift);
	}
	await loadWeek();
}

async function handleClockInOut(day) {
	const empId = employeeStore.employee?.name;
	if (!empId) return;
	try {
		const shift = attendanceStore.todayStatus?.active_shift_name;
		if (attendanceStore.todayStatus?.last_log_type === "IN") {
			await attendanceStore.clockOut(empId, null, null, null, shift);
		} else {
			await attendanceStore.clockIn(empId, null, null, null, shift);
		}
	} catch (err) {
		console.error("Clock action failed:", err);
		return;
	}
	// Refresh today's status (same as DashboardView's refreshDashboard)
	await attendanceStore.fetchTodayStatus(empId);
	// Force reload the weekly schedule to pick up the new check-in/out
	await loadWeek();
}

// When switching to monthly view, load monthly data and snap to today
watch(viewMode, (newMode) => {
	const empId = selectedEmployee.value || employeeStore.employee?.name;
	if (newMode === "monthly" && empId) {
		monthStart.value = new Date();
		loadMonth();
		snapToToday();
	}
});

watch(selectedEmployee, async (newEmp) => {
	if (newEmp) {
		selectedEmployeeAssignment.value = newEmp;
		if (viewMode.value === "weekly") {
			await loadWeek();
		} else {
			await loadMonth();
		}
	}
});

onMounted(async () => {
	window.addEventListener("click", closeAllDropdowns);
	await employeeStore.init();

	// Set initial week start to current week and month start
	weekStart.value = getWeekStart(new Date());
	monthStart.value = new Date();

	// Check Add Roster permission
	await checkCanAddRoster();
	// Check Delete Roster permission
	try {
		canDeleteRoster.value = await rosterStore.checkCanDeleteRoster();
	} catch (e) {
		canDeleteRoster.value = false;
	}
	// Check Shift Approver permission
	try {
		isShiftApprover.value = await rosterStore.checkIsShiftApprover();
		if (isShiftApprover.value) {
			await rosterStore.fetchAddRosterEmployees();
		}
	} catch (e) {
		isShiftApprover.value = false;
	}

	// Check if multiple shifts are allowed
	try {
		allowMultipleShifts.value = await rosterStore.checkAllowMultipleShifts();
	} catch (e) {
		allowMultipleShifts.value = false;
	}

	if (employeeStore.employee?.name) {
		selectedEmployee.value = employeeStore.employee.name;
	} else if (isShiftApprover.value && rosterStore.addRosterEmployees.length > 0) {
		selectedEmployee.value = rosterStore.addRosterEmployees[0].name;
	}

	if (selectedEmployee.value) {
		selectedEmployeeAssignment.value = selectedEmployee.value;
		await attendanceStore.init(selectedEmployee.value);
		await loadWeek();
		await rosterStore.fetchShiftRequests(selectedEmployee.value);
		await fetchShiftAssignments();
	}
});

onUnmounted(() => {
	window.removeEventListener("click", closeAllDropdowns);
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
