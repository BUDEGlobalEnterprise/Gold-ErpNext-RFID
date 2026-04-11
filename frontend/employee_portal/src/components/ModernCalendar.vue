<template>
	<div
		class="glass-card rounded-3xl p-6 border border-white/5 bg-transparent overflow-hidden relative"
	>
		<div
			class="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-[60px] pointer-events-none"
		></div>
		<!-- Calendar Header -->
		<div class="flex items-center justify-between mb-6 relative z-10">
			<h3 class="text-base font-bold text-white tracking-widest uppercase">{{ currentMonthYear }}</h3>
			<div class="flex items-center gap-2">
				<!-- Previous Year -->
				<button
					@click="previousYear"
					class="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-gray-400 dark:text-white/40 hover:text-gray-900 dark:hover:text-white transition-colors"
					title="Previous Year"
				>
					<span class="material-symbols-outlined text-base"
						>keyboard_double_arrow_left</span
					>
				</button>
				<!-- Previous Month -->
				<button
					@click="previousMonth"
					class="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-gray-400 dark:text-white/40 hover:text-gray-900 dark:hover:text-white transition-colors"
					title="Previous Month"
				>
					<span class="material-symbols-outlined text-lg">chevron_left</span>
				</button>
				<!-- Today Button -->
				<button
					@click="goToToday"
					class="px-2 py-0.5 text-[9px] font-bold text-primary hover:text-yellow-600 dark:hover:text-yellow-400 bg-primary/10 hover:bg-primary/20 rounded transition-colors"
					title="Go to Today"
				>
					Today
				</button>
				<!-- Next Month -->
				<button
					@click="nextMonth"
					class="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-gray-400 dark:text-white/40 hover:text-gray-900 dark:hover:text-white transition-colors"
					title="Next Month"
				>
					<span class="material-symbols-outlined text-lg">chevron_right</span>
				</button>
				<!-- Next Year -->
				<button
					@click="nextYear"
					class="p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 text-gray-400 dark:text-white/40 hover:text-gray-900 dark:hover:text-white transition-colors"
					title="Next Year"
				>
					<span class="material-symbols-outlined text-base"
						>keyboard_double_arrow_right</span
					>
				</button>
			</div>
		</div>

		<!-- Day Headers -->
		<div class="grid grid-cols-7 gap-1 mb-2">
			<div
				v-for="day in weekDayHeaders"
				:key="day"
				class="text-[9px] text-center text-gray-400 dark:text-white/30 font-bold uppercase"
			>
				{{ day }}
			</div>
		</div>

		<!-- Calendar Grid -->
		<div class="grid grid-cols-7 gap-1">
			<!-- Empty cells for days before month start -->
			<div v-for="i in firstDayOfMonth" :key="'empty-' + i" class="aspect-square"></div>

			<!-- Days -->
			<button
				v-for="day in calendarDays"
				:key="day.date"
				class="aspect-square rounded-md flex items-center justify-center text-xs relative transition-all"
				:class="getDayClasses(day)"
				@click="handleDayClick(day)"
			>
				{{ day.day }}
				<!-- Status indicator dots -->
				<span
					v-if="day.status === 'present' || day.status === 'complete'"
					class="absolute bottom-0.5 w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-sm"
				></span>
				<span
					v-if="day.status === 'absent'"
					class="absolute bottom-0.5 w-1.5 h-1.5 rounded-full bg-rose-500 shadow-sm"
				></span>
				<span
					v-if="day.status === 'leave'"
					class="absolute bottom-0.5 w-1.5 h-1.5 rounded-full bg-blue-500 shadow-sm"
				></span>
				<span
					v-if="day.status === 'pending' || day.hasPending"
					class="absolute bottom-0.5 w-1.5 h-1.5 rounded-full bg-amber-500 shadow-sm"
				></span>
			</button>
		</div>

		<!-- Legend -->
		<div
			v-if="showDefaultLegend"
			class="mt-4 pt-3 border-t border-black/5 dark:border-white/5 flex flex-wrap gap-x-3 gap-y-2 text-[9px]"
		>
			<div v-if="showLegend.complete" class="flex items-center gap-1.5">
				<span class="w-2 h-2 rounded-full bg-emerald-500"></span>
				<span class="text-gray-500 dark:text-white/40 font-medium">Complete</span>
			</div>
			<div v-if="showLegend.absent" class="flex items-center gap-1.5">
				<span class="w-2 h-2 rounded-full bg-rose-500"></span>
				<span class="text-gray-500 dark:text-white/40 font-medium">Absent</span>
			</div>
			<div v-if="showLegend.pending" class="flex items-center gap-1.5">
				<span class="w-2 h-2 rounded-full bg-amber-500"></span>
				<span class="text-gray-500 dark:text-white/40 font-medium">Pending</span>
			</div>
			<div v-if="showLegend.today" class="flex items-center gap-1.5">
				<span class="w-2 h-2 rounded-full bg-primary/60 border border-primary"></span>
				<span class="text-gray-500 dark:text-white/40 font-medium">Today</span>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps({
	// Initial date to display (defaults to today)
	initialDate: {
		type: Date,
		default: () => new Date(),
	},
	// Array of date objects with status info
	daysData: {
		type: Array,
		default: () => [],
	},
	// Custom day class function
	dayClassFn: {
		type: Function,
		default: null,
	},
	// Show default legend
	showDefaultLegend: {
		type: Boolean,
		default: true,
	},
	// Which legend items to show
	showLegend: {
		type: Object,
		default: () => ({
			complete: true,
			absent: true,
			today: true,
			pending: false,
		}),
	},
	// Weekday headers
	weekdayHeaders: {
		type: Array,
		default: () => ["M", "T", "W", "T", "F", "S", "S"],
	},
	// Start weekday (0 = Sunday, 1 = Monday)
	startWeekday: {
		type: Number,
		default: 1,
	},
});

const emit = defineEmits(["day-click", "month-change", "year-change", "today"]);

const currentDate = ref(new Date(props.initialDate));

// Watch for external initialDate changes
watch(
	() => props.initialDate,
	(newDate) => {
		if (newDate) {
			currentDate.value = new Date(newDate);
		}
	}
);

// Week day headers
const weekDayHeaders = computed(() => props.weekdayHeaders);

// Current month display
const currentMonthYear = computed(() => {
	return currentDate.value.toLocaleDateString("en-US", { month: "short", year: "numeric" });
});

// Get first day of month (adjusted for start weekday)
const firstDayOfMonth = computed(() => {
	const firstDay = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1);
	const day = firstDay.getDay();
	// Adjust based on start weekday (1 = Monday start)
	if (props.startWeekday === 1) {
		return day === 0 ? 6 : day - 1;
	}
	return day;
});

// Get days in month
const daysInMonth = computed(() => {
	return new Date(
		currentDate.value.getFullYear(),
		currentDate.value.getMonth() + 1,
		0
	).getDate();
});

// Build a map of date strings to day data for quick lookup
const daysDataMap = computed(() => {
	const map = new Map();
	props.daysData.forEach((day) => {
		if (day.date) {
			map.set(day.date, day);
		}
	});
	return map;
});

// Calendar days
const calendarDays = computed(() => {
	const today = new Date();
	const days = [];

	for (let i = 1; i <= daysInMonth.value; i++) {
		const dayDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), i);
		const dateStr = dayDate.toISOString().split("T")[0];
		const isToday =
			dayDate.getDate() === today.getDate() &&
			dayDate.getMonth() === today.getMonth() &&
			dayDate.getFullYear() === today.getFullYear();

		const dayOfWeek = dayDate.getDay();
		const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

		// Get data from props if available
		const dayData = daysDataMap.value.get(dateStr) || {};

		days.push({
			day: i,
			date: dateStr,
			isToday,
			isWeekend,
			status: dayData.status || "",
			hasLeave: dayData.hasLeave || false,
			hasPending: dayData.hasPending || false,
			...dayData,
		});
	}

	return days;
});

// Get CSS classes for a day
function getDayClasses(day) {
	if (props.dayClassFn) {
		return props.dayClassFn(day);
	}

	// Default class logic
	const classes = [];

	if (day.isToday) {
		classes.push(
			"bg-primary/20 text-primary font-bold border border-primary/20 shadow-[0_0_10px_rgba(244,192,37,0.1)]"
		);
	} else if (day.status === "leave" || day.hasLeave) {
		classes.push("bg-blue-500/10 text-blue-600 dark:text-blue-400");
	} else if (day.status === "pending" || day.hasPending) {
		classes.push("bg-amber-500/10 text-amber-600 dark:text-amber-400");
	} else if (day.status === "complete" || day.status === "present") {
		classes.push("text-emerald-600 dark:text-emerald-400");
	} else if (day.status === "absent") {
		classes.push("text-rose-600 dark:text-rose-400");
	} else if (day.status === "weekend" || day.isWeekend) {
		classes.push("text-gray-300 dark:text-white/10");
	} else {
		classes.push("text-gray-600 dark:text-white/50 hover:bg-black/5 dark:hover:bg-white/5");
	}

	return classes;
}

// Handle day click
function handleDayClick(day) {
	emit("day-click", day);
}

// Navigation methods
function previousMonth() {
	currentDate.value = new Date(
		currentDate.value.getFullYear(),
		currentDate.value.getMonth() - 1,
		1
	);
	emit("month-change", { date: currentDate.value, direction: "prev" });
}

function nextMonth() {
	currentDate.value = new Date(
		currentDate.value.getFullYear(),
		currentDate.value.getMonth() + 1,
		1
	);
	emit("month-change", { date: currentDate.value, direction: "next" });
}

function previousYear() {
	currentDate.value = new Date(
		currentDate.value.getFullYear() - 1,
		currentDate.value.getMonth(),
		1
	);
	emit("year-change", { date: currentDate.value, direction: "prev" });
}

function nextYear() {
	currentDate.value = new Date(
		currentDate.value.getFullYear() + 1,
		currentDate.value.getMonth(),
		1
	);
	emit("year-change", { date: currentDate.value, direction: "next" });
}

function goToToday() {
	currentDate.value = new Date();
	emit("today", { date: currentDate.value });
}

// Expose methods for parent components
defineExpose({
	previousMonth,
	nextMonth,
	previousYear,
	nextYear,
	goToToday,
	currentDate,
});
</script>
