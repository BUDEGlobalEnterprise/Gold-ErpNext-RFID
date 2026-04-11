<template>
	<div class="h-full overflow-y-auto no-scrollbar">
		<div class="max-w-7xl mx-auto space-y-8">
			<!-- Header -->
			<div>
				<h1 class="text-[#064e3b] text-2xl font-bold">My Roster</h1>
				<p class="text-gray-500 text-sm mt-0.5">Your weekly work schedule</p>
			</div>

			<!-- Stats Row -->
			<div class="grid grid-cols-4 gap-5">
				<div class="bg-white rounded-xl p-5 shadow-sm">
					<p class="text-[11px] text-gray-500 font-medium">WORKING DAYS</p>
					<div class="mt-2 flex items-baseline gap-1">
						<span class="text-2xl font-bold text-[#064e3b]">05</span>
						<span class="text-sm text-gray-400">/ 07</span>
					</div>
					<p class="text-xs text-gray-500 mt-2 flex items-center gap-1">
						<span class="material-symbols-outlined text-sm text-[#064e3b]">check_circle</span>
						On track this week
					</p>
				</div>
				<div class="bg-white rounded-xl p-5 shadow-sm">
					<p class="text-[11px] text-gray-500 font-medium">COMPLETED SHIFTS</p>
					<p class="text-2xl font-bold text-[#064e3b] mt-2">03</p>
					<div class="mt-3 w-full bg-gray-100 rounded-full h-1">
						<div class="bg-[#064e3b] h-1 rounded-full" style="width: 60%"></div>
					</div>
				</div>
				<div class="bg-white rounded-xl p-5 shadow-sm">
					<p class="text-[11px] text-gray-500 font-medium">HOURS WORKED</p>
					<div class="mt-2 flex items-baseline gap-1">
						<span class="text-2xl font-bold text-[#064e3b]">24.5</span>
						<span class="text-sm text-gray-400">Hrs</span>
					</div>
					<p class="text-xs text-[#064e3b] font-medium mt-2 flex items-center gap-1">
						<span class="material-symbols-outlined text-sm">trending_up</span>
						+2.4 from last week
					</p>
				</div>
				<div class="bg-[#064e3b] rounded-xl p-5 shadow-sm relative overflow-hidden">
					<p class="text-[11px] text-white/60 font-medium">TARGET HOURS</p>
					<p class="text-2xl font-bold text-white mt-2">40.0</p>
					<p class="text-xs text-white/60 mt-2 flex items-center gap-1">
						<span class="material-symbols-outlined text-sm">info</span>
						15.5 hours remaining
					</p>
					<span class="material-symbols-outlined absolute right-2 bottom-2 text-white/10 text-7xl">star</span>
				</div>
			</div>

			<!-- Navigation Bar -->
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-3">
					<button class="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">Today</button>
					<div class="flex items-center gap-2 bg-white border border-gray-200 rounded-lg">
						<button class="p-1.5 hover:bg-gray-50 rounded-l-lg"><span class="material-symbols-outlined text-gray-500 text-sm">chevron_left</span></button>
						<span class="text-sm font-medium text-gray-700 px-2">{{ weekRangeDisplay }}</span>
						<button class="p-1.5 hover:bg-gray-50 rounded-r-lg"><span class="material-symbols-outlined text-gray-500 text-sm">chevron_right</span></button>
					</div>
				</div>
				<div class="flex items-center gap-3">
					<button class="flex items-center gap-1 px-3 py-2 text-gray-500 hover:text-gray-700 text-sm font-medium">
						<span class="material-symbols-outlined text-sm">filter_list</span>
						Filter
					</button>
					<button class="px-4 py-2 bg-[#064e3b] text-white rounded-lg text-sm font-medium hover:bg-[#043d2e] flex items-center gap-1">
						<span class="material-symbols-outlined text-sm">add</span>
						Request Change
					</button>
				</div>
			</div>

			<!-- Day Cards -->
			<div class="grid grid-cols-6 gap-4">
				<div v-for="day in weeklySchedule" :key="day.date"
					class="bg-white rounded-xl p-5 shadow-sm border-2 transition-all min-h-[200px] flex flex-col"
					:class="[
						day.isToday ? 'border-[#064e3b]' : 'border-transparent hover:border-gray-100',
						day.isOff ? 'bg-gray-50' : ''
					]">
					<!-- Day Header -->
					<div class="flex items-center justify-between mb-4">
						<div>
							<p class="text-[10px] font-medium text-gray-400 uppercase">{{ day.dayShort }}</p>
							<p class="text-2xl font-bold text-gray-900">{{ day.dayNum }}</p>
						</div>
						<span v-if="day.isToday" class="bg-[#064e3b] text-white text-[10px] font-semibold px-2.5 py-1 rounded-full">TODAY</span>
					</div>

					<!-- Off Day -->
					<div v-if="day.isOff" class="flex-1 flex flex-col items-center justify-center text-gray-300">
						<span class="material-symbols-outlined text-3xl">bedtime</span>
						<p class="text-xs font-medium text-gray-400 mt-2">OFF DUTY</p>
					</div>

					<!-- Shift Info -->
					<div v-else class="flex-1 flex flex-col">
						<div class="flex-1 bg-gray-50 rounded-lg p-3 mb-3" :class="day.isToday ? 'bg-[#f0f7f4]' : ''">
							<p class="text-sm font-semibold text-[#064e3b]" v-if="day.isToday">
								<span class="material-symbols-outlined text-sm align-middle mr-1">schedule</span>
								Active Shift
							</p>
							<p class="text-sm font-semibold text-gray-900">{{ day.shiftName }}</p>
							<p class="text-xs text-gray-500 mt-1">{{ day.time }}</p>
							<p v-if="!day.isToday && day.isCompleted" class="text-xs text-[#064e3b] font-medium mt-2 flex items-center gap-1">
								<span class="material-symbols-outlined text-sm">check</span>
								Completed
							</p>
							<p v-if="day.isToday && !day.isCompleted" class="text-xs text-gray-400 mt-2">Ready to start</p>
						</div>
						<button v-if="day.isToday"
							@click="handleClockOut"
							class="w-full py-2 bg-[#064e3b] text-white rounded-lg text-xs font-semibold hover:bg-[#043d2e] transition-all">
							CLOCK OUT
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";

const employeeStore = useEmployeeStore();
const attendanceStore = useAttendanceStore();

const weekStart = ref(getWeekStart(new Date()));

function getWeekStart(date) {
	const d = new Date(date);
	const day = d.getDay();
	const diff = d.getDate() - day + (day === 0 ? -6 : 1);
	return new Date(d.setDate(diff));
}

const weekRangeDisplay = computed(() => {
	const start = weekStart.value;
	const end = new Date(start);
	end.setDate(end.getDate() + 6);
	const opts = { month: "short", day: "numeric" };
	return `${start.toLocaleDateString("en-US", opts)} – ${end.toLocaleDateString("en-US", { ...opts, year: "numeric" })}`;
});

const weeklySchedule = computed(() => {
	const days = [];
	const today = new Date();
	today.setHours(0, 0, 0, 0);
	const shiftNames = ["Morning Shift", "Morning Shift", "Morning Shift", "Full Day", "Morning Shift"];
	const times = ["08:00 – 16:30", "08:00 – 16:30", "08:00 – 16:30", "09:00 – 17:30", "08:00 – 16:30"];

	for (let i = 0; i < 6; i++) {
		const d = new Date(weekStart.value);
		d.setDate(d.getDate() + i);
		const isToday = d.toDateString() === today.toDateString();
		const isPast = d < today;
		const isOff = i === 5;
		days.push({
			date: d.toISOString().split("T")[0],
			dayShort: d.toLocaleDateString("en-US", { weekday: "short" }).toUpperCase(),
			dayNum: d.getDate(),
			isToday,
			isOff,
			isCompleted: isPast && !isToday && !isOff,
			shiftName: isOff ? "" : shiftNames[i] || "Morning Shift",
			time: isOff ? "" : times[i] || "08:00 – 16:30",
		});
	}
	return days;
});

async function handleClockOut() {
	const empId = employeeStore.employee?.name;
	if (empId) await attendanceStore.clockOut(empId);
}

onMounted(async () => {
	await employeeStore.init();
	if (employeeStore.employee?.name) await attendanceStore.init(employeeStore.employee.name);
});
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
