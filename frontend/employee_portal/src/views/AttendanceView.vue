<template>
	<div class="max-w-7xl mx-auto space-y-12">
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
				@click="activeTab = 'attendance'"
				class="pb-3 text-sm font-black uppercase tracking-[0.2em] transition-all border-b-2"
				:class="activeTab === 'attendance' ? 'border-gray-900 dark:border-white text-gray-900 dark:text-white' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'"
			>
				Attendance
			</button>
			<button
				@click="activeTab = 'checkins'"
				class="pb-3 text-sm font-black uppercase tracking-[0.2em] transition-all border-b-2"
				:class="activeTab === 'checkins' ? 'border-gray-900 dark:border-white text-gray-900 dark:text-white' : 'border-transparent text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'"
			>
				Checkins
			</button>
		</div>

		<!-- Dashboard Tab -->
		<div v-if="activeTab === 'dashboard'">
			<!-- Header + Clock Buttons -->
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8 px-2">
				<div>
					<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">
						Dashboard
					</h1>
				</div>
				<div class="flex items-center gap-4">
					<div class="bg-gray-100 dark:bg-gray-800 p-1 rounded-xl flex items-center shadow-inner">
						<button v-if="isShiftComplete && !isOnBreak" class="px-6 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-gray-700 dark:bg-gray-600 text-gray-300 dark:text-gray-200 cursor-default">
							<span class="material-symbols-outlined text-lg">check_circle</span>Shift Complete
						</button>
						<button v-if="!isCheckedIn && !isOnBreak && !isShiftComplete" @click="handleClockIn" class="px-6 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-emerald-950 text-white shadow-glow-emerald">
							<span class="material-symbols-outlined text-lg">login</span>Clock-In
						</button>
						<button v-else-if="!isCheckedIn && isOnBreak" @click="handleClockIn" class="px-6 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-emerald-950 text-white shadow-glow-emerald">
							<span class="material-symbols-outlined text-lg">login</span>Clock-In
						</button>
						<button v-if="isOnBreak" @click="handleBreak" class="px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-amber-500 text-white">
							<span class="material-symbols-outlined text-lg">restaurant</span>End Break
						</button>
						<button v-if="isCheckedIn && !isOnBreak" @click="handleBreak" class="px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-700">
							<span class="material-symbols-outlined text-lg">restaurant</span>Break
						</button>
						<button v-if="isCheckedIn && !isOnBreak" @click="handleClockOut" class="px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-700">
							<span class="material-symbols-outlined text-lg">logout</span>Clock-Out
						</button>
					</div>
				</div>
			</div>

			<!-- Stats Row -->
			<div class="grid grid-cols-1 md:grid-cols-4 gap-8">
				<div class="premium-card !p-8">
					<p class="status-label">Days Present</p>
					<div class="text-4xl font-black text-gray-900 dark:text-white leading-none tracking-tighter mb-6">{{ statusSummary.Present || 0 }}</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-emerald-50 dark:bg-emerald-500/10 rounded">
						<span class="material-symbols-outlined text-emerald-600 dark:text-emerald-400 text-[14px]">event_busy</span>
						<span class="text-[10px] font-black text-emerald-600 dark:text-emerald-400">this month</span>
					</div>
				</div>
				<div class="premium-card !p-8">
					<p class="status-label">Days Absent</p>
					<div class="text-4xl font-black text-gray-900 dark:text-white leading-none tracking-tighter mb-6">{{ statusSummary.Absent || 0 }}</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-red-50 dark:bg-red-500/10 rounded">
						<span class="material-symbols-outlined text-red-600 dark:text-red-400 text-[14px]">cancel</span>
						<span class="text-[10px] font-black text-red-600 dark:text-red-400">this month</span>
					</div>
				</div>
				<div class="premium-card !p-8">
					<p class="status-label">Scheduled Days</p>
					<div class="text-4xl font-black text-gray-900 dark:text-white leading-none tracking-tighter mb-6">{{ workingDaysInMonth }}</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-blue-50 dark:bg-blue-500/10 rounded">
						<span class="material-symbols-outlined text-blue-600 dark:text-blue-400 text-[14px]">calendar_today</span>
						<span class="text-[10px] font-black text-blue-600 dark:text-blue-400">working days</span>
					</div>
				</div>
				<div class="premium-card !p-8">
					<p class="status-label">Half Days</p>
					<div class="text-4xl font-black text-gray-900 dark:text-white leading-none tracking-tighter mb-6">{{ statusSummary["Half Day"] || 0 }}</div>
					<div class="inline-flex items-center gap-1.5 px-2 py-1 bg-amber-50 dark:bg-amber-500/10 rounded">
						<span class="material-symbols-outlined text-amber-600 dark:text-amber-400 text-[14px]">event_available</span>
						<span class="text-[10px] font-black text-amber-600 dark:text-amber-400">this month</span>
					</div>
				</div>
			</div>

			<!-- Calendar View -->
			<div class="premium-card !p-6 px-2 mt-10">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-lg font-bold text-gray-900 dark:text-white">Calendar</h2>
					<div class="flex items-center gap-2">
						<label class="text-xs text-gray-500 dark:text-gray-400">Month:</label>
						<div class="relative">
							<select v-model="selectedMonthKey" class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[180px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
								<option v-for="opt in monthOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
							</select>
							<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
						</div>
					</div>
				</div>
				<div class="grid grid-cols-7 gap-1 mb-2">
					<div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="text-center text-xs font-bold text-gray-400 dark:text-gray-500 py-2">{{ day }}</div>
				</div>
				<div class="grid grid-cols-7 gap-1">
					<div v-for="day in calendarDays" :key="day.dateStr" class="aspect-square relative">
						<div class="w-full h-full rounded-lg flex flex-col items-center justify-center text-sm cursor-pointer transition-all border"
							:class="[
								day.isToday ? 'bg-emerald-50 text-emerald-700 dark:text-emerald-300 border-emerald-700 dark:border-emerald-900 font-bold' :
								day.isHoliday ? 'bg-blue-100 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800 font-bold' :
								day.isOnLeave ? 'bg-amber-50 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800 font-bold' :
								day.attendanceStatus === 'Present' ? 'bg-emerald-50 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800 font-bold' :
								day.attendanceStatus === 'Absent' ? 'bg-red-50 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800 font-bold' :
								day.attendanceStatus === 'Half Day' ? 'bg-amber-50 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800 font-bold' :
								!day.inCurrentMonth ? 'text-gray-300 dark:text-gray-650 border-gray-100 dark:border-gray-800' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 border-transparent'
							]"
						>
							<span>{{ day.day }}</span>
							<span v-if="day.isToday" class="text-[8px] leading-tight font-black">Today</span>
							<span v-else-if="day.isHoliday && day.holidayName" class="text-[8px] leading-tight font-black truncate max-w-full px-0.5" :title="day.holidayName">{{ day.holidayName }} (Holiday)</span>
							<span v-else-if="day.isOnLeave && day.holidayName" class="text-[8px] leading-tight font-black truncate max-w-full px-0.5" :title="day.holidayName">{{ day.holidayName }}</span>
							<span v-else-if="day.attendanceStatus" class="text-[8px] leading-tight font-black">{{ day.attendanceStatus }}</span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Attendance Tab -->
		<div v-if="activeTab === 'attendance'">
			<!-- Add Attendance Button -->
			<div class="flex justify-end px-2 mb-2" v-if="canMark || showEmployeeFilter">
				<button
					@click="openAddDialog"
					class="px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center gap-2 bg-emerald-950 text-white shadow-glow-emerald"
				>
					<span class="material-symbols-outlined text-lg">add_circle</span>Add Attendance
				</button>
			</div>

			<!-- Filters -->
			<div class="flex flex-col md:flex-row md:items-end justify-between gap-8 px-2">
				<div>
					<h1 class="text-4xl font-black text-gray-900 dark:text-white tracking-tight leading-none mb-3">Attendance</h1>
					<p class="text-gray-500 dark:text-gray-400 font-medium font-sans">Precise tracking for the Atelier craftsmen.</p>
				</div>
				<div class="flex items-center gap-4 flex-wrap">
					<div v-if="showEmployeeFilter" class="flex items-center gap-2">
						<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Employee:</label>
						<div class="relative">
							<select v-model="selectedEmployee" class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[200px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
								<option value="">All Employees</option>
								<option v-for="emp in attendanceStore.employeeList" :key="emp.name" :value="emp.name">{{ emp.employee_name }}</option>
							</select>
							<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
						</div>
					</div>
					<div class="flex items-center gap-2" v-if="!showGridView">
						<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Status:</label>
						<div class="relative">
							<select v-model="filterStatus" class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[140px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
								<option value="">All</option>
								<option value="Present">Present</option>
								<option value="Absent">Absent</option>
								<option value="Half Day">Half Day</option>
								<option value="On Leave">On Leave</option>
							</select>
							<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Month:</label>
						<div class="relative">
							<select v-model="selectedMonthKey" class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[180px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
								<option v-for="opt in monthOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
							</select>
							<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
						</div>
					</div>
					<!-- List / Grid Toggle -->
					<div class="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
						<button @click="showGridView = false" class="px-3 py-1.5 rounded-md text-[10px] font-black uppercase tracking-widest transition-all"
							:class="!showGridView ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'">
							<span class="material-symbols-outlined text-sm">view_list</span>
						</button>
						<button @click="showGridView = true; fetchGridData()" class="px-3 py-1.5 rounded-md text-[10px] font-black uppercase tracking-widest transition-all"
							:class="showGridView ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'">
							<span class="material-symbols-outlined text-sm">grid_view</span>
						</button>
					</div>
				</div>
			</div>

			<!-- Add/Edit Attendance Dialog -->
			<div v-if="showAddAttendanceDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
				<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-xl w-full max-w-md mx-4">
					<div class="p-6">
						<div class="flex items-center justify-between mb-6">
							<h3 class="text-lg font-black text-gray-900 dark:text-white">
								{{ isEditing ? 'Edit Attendance' : 'Add Attendance' }}
							</h3>
							<button @click="showAddAttendanceDialog = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
								<span class="material-symbols-outlined">close</span>
							</button>
						</div>
						<div class="space-y-4">
							<div>
								<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Employee</label>
								<div class="relative" v-if="showEmployeeFilter">
									<select
										v-model="addAttendanceEmployee"
										:disabled="isEditing"
										class="appearance-none pr-8 pl-3 py-3 text-sm w-full cursor-pointer border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 disabled:opacity-60 disabled:cursor-not-allowed"
									>
										<option value="">Select Employee</option>
										<option v-for="emp in attendanceStore.employeeList" :key="emp.name" :value="emp.name">{{ emp.employee_name }}</option>
									</select>
									<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
								</div>
								<div v-else>
									<input
										type="text"
										:value="employeeStore.employee?.employee_name"
										disabled
										class="w-full px-4 py-3 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400 disabled:opacity-60 cursor-not-allowed"
									/>
								</div>
							</div>
							<div>
								<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Date</label>
								<input
									v-model="addAttendanceDate"
									type="date"
									:disabled="isEditing"
									class="w-full px-4 py-3 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 disabled:opacity-60 disabled:cursor-not-allowed"
								/>
							</div>
							<div>
								<label class="block text-xs font-black text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-2">Status</label>
								<select
									v-model="addAttendanceStatus"
									class="w-full px-4 py-3 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
								>
									<option value="Present">Present</option>
									<option value="Absent">Absent</option>
									<option value="Half Day">Half Day</option>
								</select>
							</div>
							<div v-if="addAttendanceError" class="text-sm text-red-600 dark:text-red-400 font-medium">{{ addAttendanceError }}</div>
						</div>
						<div class="flex items-center gap-3 mt-6">
							<button
								@click="handleSaveAttendance"
								:disabled="addingAttendance"
								class="flex-1 px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2 bg-emerald-950 text-white hover:bg-emerald-900 disabled:opacity-50 disabled:cursor-not-allowed"
							>
								<span class="material-symbols-outlined text-base">save</span>Save
							</button>
							<button
								@click="showAddAttendanceDialog = false"
								class="flex-1 px-5 py-3 rounded-lg text-[11px] font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-2 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
							>
								<span class="material-symbols-outlined text-base">close</span>Cancel
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Attendance Grid View -->
			<div v-if="showGridView" class="mt-8 space-y-4">
				<!-- Abbreviations Legend -->
				<div class="flex flex-wrap items-center gap-4 px-4 py-3 bg-gray-50/50 dark:bg-gray-800/30 rounded-xl border border-gray-100 dark:border-gray-800/50">
					<span class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest mr-2">Legend:</span>
					<div class="flex items-center gap-6 flex-wrap">
						<div class="flex items-center gap-2">
							<span class="w-6 h-6 flex items-center justify-center rounded text-[11px] font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400">P</span>
							<span class="text-xs font-bold text-gray-600 dark:text-gray-300">Present / On Time</span>
						</div>
						<div class="flex items-center gap-2">
							<span class="w-6 h-6 flex items-center justify-center rounded text-[11px] font-bold bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400">A</span>
							<span class="text-xs font-bold text-gray-600 dark:text-gray-300">Absent</span>
						</div>
						<div class="flex items-center gap-2">
							<span class="w-6 h-6 flex items-center justify-center rounded text-[11px] font-bold bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400">HD</span>
							<span class="text-xs font-bold text-gray-600 dark:text-gray-300">Half Day</span>
						</div>
						<div class="flex items-center gap-2">
							<span class="w-6 h-6 flex items-center justify-center rounded text-[11px] font-bold bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400">L</span>
							<span class="text-xs font-bold text-gray-600 dark:text-gray-300">On Leave</span>
						</div>
						<div class="flex items-center gap-2">
							<span class="w-6 h-6 flex items-center justify-center rounded text-[11px] font-bold bg-gray-100 text-gray-400 dark:bg-gray-700/30 dark:text-gray-500">H</span>
							<span class="text-xs font-bold text-gray-600 dark:text-gray-300">Holiday / Weekend</span>
						</div>
					</div>
				</div>

				<div class="premium-card !p-0 overflow-hidden border border-gray-100 dark:border-gray-800 shadow-sm">
					<div v-if="gridLoading" class="flex items-center justify-center py-20">
						<span class="text-sm font-bold text-gray-400 dark:text-gray-500">Loading grid…</span>
					</div>
					<div v-else-if="filteredGridData.length === 0" class="flex items-center justify-center py-20">
						<span class="text-sm font-bold text-gray-400 dark:text-gray-500">No attendance data for this period.</span>
					</div>
					<div v-else class="overflow-x-auto">
						<table class="w-full text-center border-collapse">
							<thead>
								<tr>
									<th class="sticky left-0 z-20 px-3 py-3 text-[9px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest bg-gray-50/80 dark:bg-gray-800/80 backdrop-blur border-b border-r border-gray-100 dark:border-gray-800 text-left min-w-[140px]">Employee</th>
									<th v-for="d in gridDayHeaders" :key="d" class="px-0.5 py-3 text-[9px] font-bold text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-800 min-w-[28px] w-[28px]">{{ d }}</th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="row in filteredGridData" :key="row.employee" class="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
									<!-- Employee name sticky column -->
									<td class="sticky left-0 z-10 px-3 py-2 text-[11px] font-bold text-gray-900 dark:text-white text-left bg-white dark:bg-gray-900 border-r border-gray-100 dark:border-gray-800 whitespace-nowrap">{{ row.employee_name }}</td>
									<!-- Day cells -->
									<td v-for="day in row.days" :key="day.date" class="px-0.5 py-1 border border-gray-50 dark:border-gray-800/50">
										<button v-if="day.status"
											@click="openCellDetail(day, row.employee, row.employee_name)"
											class="w-6 h-6 flex items-center justify-center rounded transition-all hover:scale-125"
											:class="getCellClasses(day.status)"
											:title="`${day.date} — ${day.status}`"
										>
											<span class="text-[13px] leading-none font-bold">{{ getStatusIcon(day.status) }}</span>
										</button>
										<span v-else class="w-6 h-6 flex items-center justify-center text-gray-200 dark:text-gray-700 text-[10px]">—</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<!-- Day Detail Popup -->
				<div v-if="showCellDetail" @click.self="showCellDetail = false" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
					<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 shadow-2xl w-full max-w-sm mx-4 overflow-hidden">
						<div class="px-6 py-5 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
							<div class="flex items-center justify-between">
								<div>
									<h3 class="text-base font-black text-gray-900 dark:text-white">{{ detailCell.employeeName }}</h3>
									<p class="text-xs font-bold text-gray-400 dark:text-gray-500 mt-0.5">{{ detailCell.date }}</p>
								</div>
								<button @click="showCellDetail = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
									<span class="material-symbols-outlined">close</span>
								</button>
							</div>
						</div>
						<div class="p-6 space-y-4">
							<div class="flex items-center justify-between">
								<span class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Status</span>
								<span class="inline-flex px-3 py-1 rounded text-[10px] font-black uppercase tracking-widest" :class="getCellClasses(detailCell.status)">{{ detailCell.status }}</span>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Clock In</span>
								<span class="text-sm font-bold text-gray-900 dark:text-white tabular-nums">{{ detailCell.inTime || "—" }}</span>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Clock Out</span>
								<span class="text-sm font-bold text-gray-900 dark:text-white tabular-nums">{{ detailCell.outTime || "—" }}</span>
							</div>
							<div class="flex items-center justify-between">
								<span class="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">Total Hours</span>
								<span class="text-sm font-bold text-gray-900 dark:text-white tabular-nums">{{ detailCell.workingHoursFormatted }}</span>
							</div>
						</div>
						
						<!-- Grid Popup Footer Actions (only if canMark or showEmployeeFilter is true) -->
						<div v-if="canMark || showEmployeeFilter" class="px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-800/20 flex gap-3">
							<button @click="openEditDialog(detailCell)" class="flex-1 px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
								<span class="material-symbols-outlined text-sm">edit</span>Edit
							</button>
							<button v-if="detailCell.name" @click="handleDelete(detailCell)" class="flex-1 px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-red-50 text-red-650 dark:bg-red-950/20 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-950/30">
								<span class="material-symbols-outlined text-sm">delete</span>Delete
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Attendance Table (list view) -->
			<div v-else class="premium-card !p-0 overflow-hidden border border-gray-100 dark:border-gray-800 shadow-sm mt-8">
				<table class="w-full text-left">
					<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-800/50">
						<tr>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">ID</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Date</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Employee</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Clock In</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Clock Out</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Total Hours</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-right">Status</th>
							<th v-if="canMark || showEmployeeFilter" class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em] text-center">Actions</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-50 dark:divide-gray-800">
						<tr v-for="record in paginatedRecords" :key="record.name" class="transition-colors">
							<td class="px-10 py-6">
								<p class="text-sm font-black text-gray-900 dark:text-white tracking-tight">{{ record.name || "-" }}</p>
							</td>
							<td class="px-10 py-6">
								<p class="text-sm font-black text-gray-900 dark:text-white tracking-tight">{{ formatDate(record.date) }}</p>
								<p class="text-[10px] font-bold text-gray-400 dark:text-gray-500">{{ formatDay(record.date) }}</p>
							</td>
							<td class="px-10 py-6">
								<p class="text-sm font-black text-gray-900 dark:text-white tracking-tight">{{ record.employeeName || "-" }}</p>
							</td>
							<td class="px-10 py-6">
								<div class="flex items-center gap-3">
									<div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
									<p class="text-sm font-black text-gray-900 dark:text-white">{{ record.clockIn ? formatTime(record.clockIn) : "--:--" }}</p>
								</div>
							</td>
							<td class="px-10 py-6">
								<p class="text-sm font-black text-gray-900 dark:text-white">{{ record.clockOut ? formatTime(record.clockOut) : "--:--" }}</p>
							</td>
							<td class="px-10 py-6">
								<p class="text-sm font-black text-gray-900 dark:text-white tabular-nums">{{ record.totalHours }}</p>
							</td>
							<td class="px-10 py-6 text-right">
								<span class="inline-flex px-3 py-1 rounded text-[9px] font-black uppercase tracking-widest" :class="getStatusClasses(record.status)">{{ record.status }}</span>
							</td>
							<td v-if="canMark || showEmployeeFilter" class="px-10 py-6 text-center relative">
								<!-- Actions dropdown button -->
								<button @click.stop="toggleActionMenu(record.name)" class="more_vert px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-1.5 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 mx-auto">
									<span>More</span>
									<span class="material-symbols-outlined text-xs">expand_more</span>
								</button>
								
								<!-- Dropdown Menu -->
								<div v-if="activeActionMenu === record.name" class="dropdown-menu absolute right-12 top-14 z-30 w-36 py-1.5 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl shadow-xl overflow-hidden">
									<button @click="openEditDialog(record)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50 flex items-center gap-2">
										<span class="material-symbols-outlined text-sm">edit</span>Edit
									</button>
									<button v-if="record.name" @click="handleDelete(record)" class="w-full px-4 py-2.5 text-[10px] font-black uppercase tracking-widest text-left text-red-650 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center gap-2">
										<span class="material-symbols-outlined text-sm">delete</span>Delete
									</button>
								</div>
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
							<select v-model.number="pageSize" class="appearance-none w-20 pr-8 pl-3 py-1.5 text-xs font-bold cursor-pointer border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100" @change="currentPage = 1">
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
							Showing {{ Math.min((currentPage - 1) * Number(pageSize) + 1, totalRecords) }} - {{ Math.min(currentPage * Number(pageSize), totalRecords) }} of {{ totalRecords }} records
						</span>
						<div class="flex items-center gap-1">
							<button 
								@click="prevPage" 
								:disabled="currentPage === 1"
								class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
							>
								<span class="material-symbols-outlined text-sm font-bold">chevron_left</span>
							</button>
							<button 
								@click="nextPage" 
								:disabled="currentPage === totalPages"
								class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
							>
								<span class="material-symbols-outlined text-sm font-bold">chevron_right</span>
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Checkins Tab -->
		<div v-if="activeTab === 'checkins'">
			<!-- Checkins Filters -->
			<div class="flex items-center gap-4 flex-wrap mb-4">
				<div v-if="showEmployeeFilter" class="flex items-center gap-2">
					<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Employee:</label>
					<div class="relative">
						<select v-model="selectedCheckinsEmployee" class="appearance-none pr-8 pl-3 py-2 text-sm cursor-pointer min-w-[200px] border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
							<option value="">All Employees</option>
							<option v-for="emp in attendanceStore.employeeList" :key="emp.name" :value="emp.name">{{ emp.employee_name }}</option>
						</select>
						<span class="material-symbols-outlined text-xs absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">expand_more</span>
					</div>
				</div>
				<div class="flex items-center gap-2">
					<label class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">Date:</label>
					<input
						v-model="checkinsDate"
						type="date"
						class="px-4 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
					/>
				</div>
			</div>
			<div v-if="checkinsLoading" class="flex items-center justify-center py-20">
				<span class="text-sm font-bold text-gray-400 dark:text-gray-500">Loading checkins…</span>
			</div>
			<div v-else-if="checkinsData.length === 0" class="flex items-center justify-center py-20">
				<span class="text-sm font-bold text-gray-400 dark:text-gray-500">No check-in records found.</span>
			</div>
			<div v-else class="overflow-x-auto">
				<table class="w-full text-left">
					<thead class="border-b border-gray-50 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-800/50">
						<tr>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">ID</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Employee</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Date & Time</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Type</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Device</th>
							<th class="px-10 py-5 text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-[0.25em]">Shift</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-50 dark:divide-gray-800">
						<tr v-for="log in checkinsData" :key="log.name" class="transition-colors">
							<td class="px-10 py-5">
								<p class="text-xs font-bold text-gray-500 dark:text-gray-400 tabular-nums">{{ log.name }}</p>
							</td>
							<td class="px-10 py-5">
								<p class="text-sm font-bold text-gray-900 dark:text-white">{{ log.employee_name || log.employee || "—" }}</p>
							</td>
							<td class="px-10 py-5">
								<p class="text-sm font-bold text-gray-900 dark:text-white tabular-nums">{{ formatDateTime(log.time) }}</p>
								<p class="text-[10px] font-bold text-gray-400 dark:text-gray-500">{{ formatDay(log.time) }}</p>
							</td>
							<td class="px-10 py-5">
								<span class="inline-flex px-3 py-1 rounded text-[9px] font-black uppercase tracking-widest" :class="getCheckinTypeClasses(log.log_type)">
									<span class="material-symbols-outlined text-[11px] mr-1">{{ log.log_type === 'IN' ? 'login' : 'logout' }}</span>
									{{ log.log_type }}
								</span>
							</td>
							<td class="px-10 py-5">
								<p class="text-sm font-bold text-gray-900 dark:text-white truncate max-w-[200px]" :title="log.device_id">{{ log.device_id || "—" }}</p>
							</td>
							<td class="px-10 py-5">
								<p class="text-sm font-bold text-gray-900 dark:text-white">{{ log.shift || "—" }}</p>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { createResource } from "frappe-ui";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";

const employeeStore = useEmployeeStore();
const attendanceStore = useAttendanceStore();

// Resource to fetch current logged-in user's attendance history separately for the dashboard
const currentUserHistoryResource = createResource({
	url: "zevar_core.api.attendance.get_attendance_history",
	auto: false,
});

async function fetchCurrentUserHistory() {
	const empId = employeeStore.employee?.name;
	if (empId) {
		await currentUserHistoryResource.fetch({
			employee_id: empId,
			month: selectedMonth.value,
			year: selectedYear.value,
			override_employee_id: empId,
		});
	}
}

const activeActionMenu = ref("");
const isEditing = ref(false);
const editAttendanceName = ref("");

// Resource to fetch a single attendance record by name/id for editing
const getAttendanceResource = createResource({
	url: "frappe.client.get",
	auto: false,
});

function toggleActionMenu(dateKey) {
	if (activeActionMenu.value === dateKey) {
		activeActionMenu.value = "";
	} else {
		activeActionMenu.value = dateKey;
	}
}

function closeActionMenu() {
	activeActionMenu.value = "";
}

function openAddDialog() {
	isEditing.value = false;
	editAttendanceName.value = "";
	addAttendanceEmployee.value = showEmployeeFilter.value ? "" : (employeeStore.employee?.name || "");
	addAttendanceDate.value = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, "0")}-${String(new Date().getDate()).padStart(2, "0")}`;
	addAttendanceStatus.value = "Present";
	addAttendanceError.value = "";
	showAddAttendanceDialog.value = true;
}

async function openEditDialog(record) {
	activeActionMenu.value = "";
	const attId = record.name || record.attendance_name || "";
	if (!attId) {
		alert("No attendance ID found.");
		return;
	}

	addAttendanceError.value = "";
	addingAttendance.value = true;
	showAddAttendanceDialog.value = true;
	showCellDetail.value = false;
	isEditing.value = true;
	editAttendanceName.value = attId;

	try {
		const res = await getAttendanceResource.fetch({
			doctype: "Attendance",
			name: attId
		});
		if (res && res.name) {
			addAttendanceEmployee.value = res.employee || "";
			addAttendanceDate.value = res.attendance_date || "";
			addAttendanceStatus.value = res.status || "Present";
		} else {
			// fallback
			addAttendanceEmployee.value = record.employee || record.employee_id || "";
			addAttendanceDate.value = record.date || "";
			addAttendanceStatus.value = record.status || "Present";
		}
	} catch (err) {
		console.error("Failed to fetch attendance details:", err);
		// fallback
		addAttendanceEmployee.value = record.employee || record.employee_id || "";
		addAttendanceDate.value = record.date || "";
		addAttendanceStatus.value = record.status || "Present";
	} finally {
		addingAttendance.value = false;
	}
}

async function handleDelete(record) {
	const attName = record.name || record.attendance_name || "";
	if (!attName) {
		alert("No attendance record exists for this day.");
		return;
	}

	if (!confirm("Are you sure you want to delete this attendance record?")) {
		return;
	}

	try {
		const deleteRes = createResource({
			url: "zevar_core.api.attendance.delete_attendance",
			auto: false,
		});
		await deleteRes.fetch({
			attendance_name: attName,
		});

		showCellDetail.value = false;
		activeActionMenu.value = "";

		await fetchMonthlyHistory();
		await fetchCurrentUserHistory();
		await fetchMonthlyStats();
		await fetchMonthlyRoster();
		if (showGridView.value) {
			await fetchGridData();
		}

		// alert("Attendance record deleted successfully.");
	} catch (err) {
		alert(err.message || "Failed to delete attendance record.");
	}
}

const activeTab = ref("dashboard");

const currentDate = ref(new Date());

// Permission to add/edit/delete attendance (create permission)
const canMark = ref(false);

// Permission to view other employees' attendance data (write permission)
const canManage = ref(false);

// Permission to view attendance records (read permission — gate employee filter)
const canView = ref(false);

// Add Attendance dialog state
const showAddAttendanceDialog = ref(false);
const addAttendanceEmployee = ref("");
const addAttendanceDate = ref(
	`${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, "0")}-${String(new Date().getDate()).padStart(2, "0")}`
);
const addAttendanceStatus = ref("Present");
const addAttendanceError = ref("");
const addingAttendance = ref(false);

// Employee filter (for admin/approver — shows dropdown to select employee)
const showEmployeeFilter = computed(() => attendanceStore.employeeList.length > 1);
const selectedEmployee = ref("");

// Grid view
const showGridView = ref(false);
const gridData = ref([]);
const gridDayHeaders = ref([]);
const gridLoading = ref(false);
const showCellDetail = ref(false);
const detailCell = ref({
	employeeName: "",
	date: "",
	status: "",
	inTime: "",
	outTime: "",
	workingHoursFormatted: "",
});

const _today = new Date();
const selectedMonth = ref(_today.getMonth() + 1);
const selectedYear = ref(_today.getFullYear());

// Additional filters
const filterStatus = ref("");

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

const selectedMonthKey = computed({
	get: () => `${selectedYear.value}-${selectedMonth.value}`,
	set: (val) => {
		const [y, m] = val.split("-").map(Number);
		selectedYear.value = y;
		selectedMonth.value = m;
	},
});

const isCheckedIn = computed(() => attendanceStore.isCheckedIn);
const isOnBreak = computed(() => attendanceStore.isOnBreak);
const isShiftComplete = computed(() => attendanceStore.isDayCompleted);
const workingHoursTarget = computed(() => attendanceStore.workingHoursTarget);
const roster = computed(() => attendanceStore.roster);
	const dayInfoMap = computed(() => {
		const map = {};
		const cal = attendanceStore.monthlyRoster?.calendar || [];
		cal.forEach((d) => {
			if (d.status === "holiday" && d.shift?.shift_name) {
				map[d.date] = { type: "holiday", label: d.shift.shift_name };
			} else if (d.status === "on_leave" && d.shift?.shift_name) {
				map[d.date] = { type: "on_leave", label: d.shift.shift_name };
			}
		});

		// Map the current user's actual attendance records onto the calendar days
		const records = currentUserHistoryResource.data?.records || [];
		records.forEach((r) => {
			if (r.date) {
				if (!map[r.date]) map[r.date] = { type: "working", label: "" };
				map[r.date].attendanceStatus = r.status;
			}
		});
		return map;
	});

const workingDaysInMonth = ref(0);

const statusSummary = computed(() => {
	const summary = currentUserHistoryResource.data?.summary || {};
	return {
		Present: summary.Present || 0,
		Absent: summary.Absent || 0,
		"Half Day": summary["Half Day"] || 0,
		"On Leave": summary["On Leave"] || 0,
	};
});

const todayStr = computed(() => {
	const t = new Date();
	return `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`;
});

const calendarDays = computed(() => {
	const days = [];
	const firstOfMonth = new Date(selectedYear.value, selectedMonth.value - 1, 1);
	const lastOfMonth = new Date(selectedYear.value, selectedMonth.value, 0);

	// Sunday-first: getDay() returns 0=Sun, 6=Sat
	const sundayOffset = firstOfMonth.getDay();
	const gridStart = new Date(firstOfMonth);
	gridStart.setDate(gridStart.getDate() - sundayOffset);

	const today = todayStr.value;
	let current = new Date(gridStart);
	const gridEnd = new Date(gridStart);
	gridEnd.setDate(gridEnd.getDate() + 41);

	while (current <= gridEnd) {
		const dateStr = `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, "0")}-${String(current.getDate()).padStart(2, "0")}`;
		const info = dayInfoMap.value[dateStr];
		days.push({
			dateStr,
			day: current.getDate(),
			inCurrentMonth: current.getMonth() === selectedMonth.value - 1,
			isToday: dateStr === today,
			isHoliday: info?.type === "holiday",
			isOnLeave: info?.type === "on_leave",
			holidayName: info?.label || "",
			attendanceStatus: info?.attendanceStatus || "",
		});
		current.setDate(current.getDate() + 1);
	}

	return days;
});

const dailyRecords = computed(() => {
	const records = [];
	const history = (attendanceStore.history || []).filter((r) => !r._summary);
	const targetHours = workingHoursTarget.value;

	history.forEach((record) => {
		const dateStr = record.date;
		if (!dateStr) return;

		const date = new Date(dateStr + "T00:00:00");
		const dayOfWeek = date.getDay();
		const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

		const clockIn = record.in_time || null;
		const clockOut = record.out_time || null;
		const totalHours = record.working_hours || 0;

		let status = record.status || "";

		if (!isWeekend && status === "") {
			if (clockIn) {
				const inTime = new Date(clockIn);
				const lateThreshold = new Date(date);
				const startTime = roster.value?.start_time ? roster.value.start_time.split(":") : [9, 0];
				lateThreshold.setHours(parseInt(startTime[0]), parseInt(startTime[1]), 0);

				if (totalHours >= targetHours) status = "On Time";
				else if (inTime > lateThreshold) status = "Slight Late";
				else status = "On Time";
			} else {
				const todayDate = new Date();
				todayDate.setHours(0, 0, 0, 0);
				if (date < todayDate) status = "Absent";
			}
		}

		if (isWeekend && !status) status = "Weekend";

		const formattedHours = totalHours > 0 ? `${Math.floor(totalHours)}h ${Math.round((totalHours % 1) * 60)}m` : "0h 0m";
		records.push({ name: record.name, employee: record.employee, date: dateStr, clockIn, clockOut, totalHours: formattedHours, status, employeeName: record.employee_name || "" });
	});

	return records.sort((a, b) => new Date(b.date) - new Date(a.date));
});

const currentPage = ref(1);
const pageSize = ref(10);

const totalRecords = computed(() => dailyRecords.value.length);
const totalPages = computed(() => Math.ceil(totalRecords.value / Number(pageSize.value)) || 1);

const paginatedRecords = computed(() => {
	const size = Number(pageSize.value);
	const start = (currentPage.value - 1) * size;
	const end = start + size;
	return dailyRecords.value.slice(start, end);
});

function prevPage() {
	if (currentPage.value > 1) {
		currentPage.value--;
	}
}

// ---- Grid view helpers ----

const filteredGridData = computed(() => {
	if (!filterStatus.value || filterStatus.value === "") return gridData.value;
	// Filter employees who have at least one day matching the selected status,
	// but keep all day columns intact (column alignment is critical).
	return gridData.value.filter((row) =>
		row.days.some((d) => d.status === filterStatus.value)
	);
});

function getStatusIcon(status) {
 	if (status === "Present" || status === "On Time") return "P";
 	if (status === "Absent") return "A";
 	if (status === "Half Day") return "HD";
 	if (status === "On Leave") return "L";
 	if (status === "Holiday" || status === "Weekend") return "H";
 	return "";
 }

function getCellClasses(status) {
	if (status === "Present" || status === "On Time") return "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-500/30";
	if (status === "Absent") return "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-500/30";
	if (status === "Half Day") return "bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400 hover:bg-amber-200 dark:hover:bg-amber-500/30";
	if (status === "On Leave") return "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400 hover:bg-yellow-200 dark:hover:bg-yellow-500/30";
	if (status === "Holiday" || status === "Weekend") return "bg-gray-100 text-gray-300 dark:bg-gray-700/30 dark:text-gray-650";
	return "bg-gray-50 text-gray-300 dark:bg-gray-800 dark:text-gray-650";
}

function getWorkingDayCount(days) {
	return days.filter((d) => d.is_working_day && d.status).length;
 }

function formatGridHours(hours) {
	if (!hours || hours === 0) return "—";
	return `${Math.floor(hours)}h ${Math.round((hours % 1) * 60)}m`;
}

function openCellDetail(day, employeeId, employeeName) {
	detailCell.value = {
		name: day.name || "",
		employee: employeeId || "",
		employeeName,
		date: day.date,
		status: day.status,
		inTime: day.in_time ? new Date(day.in_time).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true }) : "—",
		outTime: day.out_time ? new Date(day.out_time).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true }) : "—",
		workingHoursFormatted: formatGridHours(day.working_hours),
	};
	showCellDetail.value = true;
}

function closeCellDetail() {
	showCellDetail.value = false;
}

async function fetchGridData() {
	const empId = employeeStore.employee?.name;
	if (!empId) return;

	gridLoading.value = true;
	return new Promise((resolve) => {
		const gridRes = createResource({
			url: "zevar_core.api.attendance.get_attendance_grid",
			makeParams: () => {
				const params = { year: selectedYear.value, month: selectedMonth.value };
				if (showEmployeeFilter.value) {
					if (selectedEmployee.value) params.employee_id = selectedEmployee.value;
				} else {
					params.employee_id = empId;
				}
				return params;
			},
			auto: false,
			onSuccess(data) {
				if (data && data.grid) {
					gridData.value = data.grid;
					const m = selectedMonth.value;
					const y = selectedYear.value;
					const daysInMonth = new Date(y, m, 0).getDate();
					gridDayHeaders.value = Array.from({ length: daysInMonth }, (_, i) => String(i + 1));
				} else {
					gridData.value = [];
				}
				gridLoading.value = false;
				resolve();
			},
			onError() {
				console.error("Grid fetch failed");
				gridData.value = [];
				gridLoading.value = false;
				resolve();
			},
		});
		gridRes.fetch();
	});
}

function getStatusClasses(status) {
  const s = status?.toLowerCase();
  if (s === "present" || s === "on time") return "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400";
  if (s === "slight late") return "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400";
  if (s === "absent") return "bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400";
  if (s === "half day") return "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400";
  if (s === "on leave") return "bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400";
  if (s === "weekend") return "bg-gray-50 text-gray-500 dark:bg-gray-700/50 dark:text-gray-400";
  return "bg-gray-50 text-gray-500 dark:bg-gray-700/50 dark:text-gray-400";
}

function formatDate(dateStr) {
	const date = new Date(dateStr);
	return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}
function formatDay(dateStr) {
	return new Date(dateStr).toLocaleDateString("en-US", { weekday: "long" });
}
function formatTime(timeStr) {
	return new Date(timeStr).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true });
}

// ---- Checkins tab ----

const checkinsLoading = ref(false);
const checkinsData = ref([]);
const checkinsDate = ref("");
const selectedCheckinsEmployee = ref("");

const checkinsResource = createResource({
	url: "zevar_core.api.attendance.get_employee_checkins",
	auto: false,
});

async function fetchCheckins() {
	checkinsLoading.value = true;
	try {
		const params = {};
		if (showEmployeeFilter.value) {
			// Admin/Approver mode: use override_employee_id
			params.override_employee_id = selectedCheckinsEmployee.value || "";
		} else {
			// Normal mode: use current user's employee
			const empId = employeeStore.employee?.name;
			if (!empId) {
				checkinsLoading.value = false;
				return;
			}
			params.employee_id = empId;
		}
		if (checkinsDate.value) {
			const [y, m, d] = checkinsDate.value.split("-");
			params.year = y;
			params.month = m;
			params.day = d;
		}
		await checkinsResource.fetch(params);
		checkinsData.value = checkinsResource.data || [];
	} catch (e) {
		console.error("Checkins fetch failed:", e);
		checkinsData.value = [];
	} finally {
		checkinsLoading.value = false;
	}
}

function getCheckinTypeClasses(logType) {
	const t = (logType || "").toUpperCase();
	if (t === "IN") return "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400";
	if (t === "OUT") return "bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400";
	return "bg-gray-50 text-gray-500 dark:bg-gray-700/50 dark:text-gray-400";
}

function formatDateTime(timeStr) {
	if (!timeStr) return "—";
	const d = new Date(timeStr);
	return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) +
		" " +
		d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true });
}

async function handleClockIn() {
	const empId = employeeStore.employee?.name;
	if (empId) await attendanceStore.clockIn(empId);
}
async function handleClockOut() {
	const empId = employeeStore.employee?.name;
	if (empId) await attendanceStore.clockOut(empId);
}
async function handleBreak() {
  if (isOnBreak.value) await attendanceStore.endBreak();
  else await attendanceStore.startBreak();
}

async function handleCheckPermission() {
  try {
    canMark.value = await attendanceStore.checkCanMarkAttendance();
  } catch (e) {
    canMark.value = false;
  }
}

async function handleSaveAttendance() {
  addAttendanceError.value = "";
  const empId = addAttendanceEmployee.value;
  if (!empId) {
    addAttendanceError.value = "Please select an employee.";
    return;
  }
  if (!addAttendanceDate.value) {
    addAttendanceError.value = "Please select a date.";
    return;
  }

  addingAttendance.value = true;
  try {
    if (isEditing.value) {
      if (editAttendanceName.value) {
        const updateRes = createResource({
          url: "zevar_core.api.attendance.update_attendance",
          auto: false,
        });
        await updateRes.fetch({
          attendance_name: editAttendanceName.value,
          status: addAttendanceStatus.value,
        });
        if (updateRes.error) {
          throw new Error(updateRes.error.message || "Failed to update attendance.");
        }
      } else {
        throw new Error("No attendance record ID specified.");
      }
    } else {
      await attendanceStore.markAttendance(empId, addAttendanceDate.value, addAttendanceStatus.value);
    }

    showAddAttendanceDialog.value = false;
    // Reset form
    addAttendanceDate.value = `${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, "0")}-${String(new Date().getDate()).padStart(2, "0")}`;
    addAttendanceEmployee.value = "";
    addAttendanceStatus.value = "Present";
    addAttendanceError.value = "";
    isEditing.value = false;
    editAttendanceName.value = "";

    // Refresh history
    await fetchMonthlyHistory();
    await fetchCurrentUserHistory();
    await fetchMonthlyStats();
    await fetchMonthlyRoster();
    if (showGridView.value) {
      await fetchGridData();
    }
  } catch (err) {
    addAttendanceError.value = err.message || "Failed to save attendance.";
  } finally {
    addingAttendance.value = false;
  }
}

async function fetchAttendanceSummary() {
  // Summary is now derived from history._summary in statusSummary computed
}

async function fetchMonthlyStats() {
  try {
    const m = selectedMonth.value;
    const y = selectedYear.value;
    const res = await fetch(`/api/method/zevar_core.api.attendance.get_monthly_attendance_stats?month=${m}&year=${y}`);
    const data = await res.json();
    if (data.message) workingDaysInMonth.value = data.message.working_days || 0;
  } catch (e) {}
}

async function fetchMonthlyRoster() {
  const empId = employeeStore.employee?.name;
  if (empId) {
    await attendanceStore.fetchMonthlyRoster(empId, selectedYear.value, selectedMonth.value);
  }
}

async function fetchMonthlyHistory() {
  const empId = employeeStore.employee?.name;
  if (empId) {
    const params = {
      month: selectedMonth.value,
      year: selectedYear.value,
      override_employee_id: showEmployeeFilter.value ? (selectedEmployee.value || "") : empId,
    };
    if (filterStatus.value && filterStatus.value !== "All") {
      params.status = filterStatus.value;
    }
    await attendanceStore.fetchHistory(empId, params);
  }
}

// Reload current user's dashboard data when month/year changes
watch([selectedMonth, selectedYear], () => {
	fetchCurrentUserHistory();
	fetchMonthlyStats();
	fetchMonthlyRoster();
});

// Reload list data + grid when any filter changes
watch([selectedEmployee, filterStatus, selectedMonth, selectedYear], () => {
	currentPage.value = 1;
	fetchMonthlyHistory();
	if (showGridView.value) {
		fetchGridData();
	}
});

// Fetch grid data when grid view is toggled on
watch(showGridView, (val) => {
	if (val) {
		fetchGridData();
	}
});

// Fetch checkins when checkins tab is opened
watch(activeTab, (val) => {
	if (val === "checkins") {
		fetchCheckins();
	}
});

// Refetch checkins when date or employee filter changes
watch([checkinsDate, selectedCheckinsEmployee], () => {
	if (activeTab.value === "checkins") {
		fetchCheckins();
	}
});

const handleWindowClick = (e) => {
	if (!e.target.closest(".more_vert") && !e.target.closest(".dropdown-menu")) {
		closeActionMenu();
	}
};

onMounted(async () => {
	window.addEventListener("click", handleWindowClick);
	await employeeStore.init();
	const empId = employeeStore.employee?.name;
	if (empId) {
		await attendanceStore.init(empId);
		await handleCheckPermission();
		try {
			canManage.value = await attendanceStore.checkCanManageAttendance();
		} catch (e) {
			canManage.value = false;
		}
		try {
			canView.value = await attendanceStore.checkCanViewAttendance();
		} catch (e) {
			canView.value = false;
		}
		await fetchCurrentUserHistory();
		await attendanceStore.fetchEmployeeList();
		await fetchMonthlyHistory();
		await fetchMonthlyStats();
		await fetchMonthlyRoster();
		// Fetch grid data if grid view is active on mount
		if (showGridView.value) {
			await fetchGridData();
		}
	}
});

onUnmounted(() => {
	window.removeEventListener("click", handleWindowClick);
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
