<template>
	<div class="glass-card !rounded-2xl p-4 border border-white/5 bg-white dark:bg-[#111420]">
		<!-- Calendar Header -->
		<div class="flex items-center justify-between mb-4">
			<h3 class="text-sm font-bold text-gray-900 dark:text-white capitalize">
				{{ monthName }} {{ currentYear }}
			</h3>
			<div class="flex gap-1">
					<button
						@click="prevMonth"
						class="p-1.5 rounded-lg text-gray-400 dark:text-white/40 transition-all border border-transparent hover:bg-gray-100 dark:hover:bg-white/5"
					>
					<span class="material-symbols-outlined text-lg">chevron_left</span>
				</button>
					<button
						@click="nextMonth"
						class="p-1.5 rounded-lg text-gray-400 dark:text-white/40 transition-all border border-transparent hover:bg-gray-100 dark:hover:bg-white/5"
					>
					<span class="material-symbols-outlined text-lg">chevron_right</span>
				</button>
			</div>
		</div>

		<!-- Day Labels -->
		<div class="grid grid-cols-7 gap-1 mb-2">
			<div
				v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']"
				:key="day"
				class="text-[10px] text-center text-gray-400 dark:text-white/30 font-bold uppercase tracking-wider"
			>
				{{ day[0] }}
			</div>
		</div>

		<!-- Days Grid -->
		<div class="grid grid-cols-7 gap-1">
			<!-- Padding for start of month -->
			<div v-for="n in firstDayOffset" :key="'pad-' + n" class="aspect-square"></div>

			<!-- Month Days -->
			<button
				v-for="d in daysInMonth"
				:key="d"
				@click="selectDate(d)"
				class="aspect-square rounded-full flex items-center justify-center text-xs relative transition-all group"
					:class="[
						isSelected(d)
							? 'bg-primary text-black font-bold shadow-lg shadow-primary/20 scale-110 z-10'
							: isToday(d)
							? 'bg-primary/10 text-primary font-bold'
							: 'text-gray-600 dark:text-white/60 hover:bg-gray-100 dark:hover:bg-white/5',
					]"
				>
				{{ d }}
				<!-- Event Dots or indicators can go here -->
				<span
					v-if="hasEvent(d) && !isSelected(d)"
					class="absolute bottom-1 w-1 h-1 rounded-full bg-primary/50"
				></span>
			</button>
		</div>

		<!-- Today/Selected Info -->
		<div class="mt-4 pt-3 border-t border-gray-100 dark:border-white/5">
			<p class="text-[10px] text-gray-400 dark:text-white/40 font-medium">
				{{ selectedFormatted }}
			</p>
		</div>
	</div>
</template>

<script setup>
import { computed, ref } from "vue";

const props = defineProps({
	modelValue: {
		type: [Date, String, null],
		default: null,
	},
	events: {
		type: Array, // Array of date strings 'YYYY-MM-DD'
		default: () => [],
	},
});

const emit = defineEmits(["update:modelValue", "change"]);

const now = new Date();
const currentMonth = ref(now.getMonth());
const currentYear = ref(now.getFullYear());

const monthName = computed(() => {
	return new Intl.DateTimeFormat("en-US", { month: "long" }).format(
		new Date(currentYear.value, currentMonth.value)
	);
});

const daysInMonth = computed(() => {
	return new Date(currentYear.value, currentMonth.value + 1, 0).getDate();
});

const firstDayOffset = computed(() => {
	return new Date(currentYear.value, currentMonth.value, 1).getDay();
});

const prevMonth = () => {
	if (currentMonth.value === 0) {
		currentMonth.value = 11;
		currentYear.value--;
	} else {
		currentMonth.value--;
	}
};

const nextMonth = () => {
	if (currentMonth.value === 11) {
		currentMonth.value = 0;
		currentYear.value++;
	} else {
		currentMonth.value++;
	}
};

const isToday = (day) => {
	return (
		day === now.getDate() &&
		currentMonth.value === now.getMonth() &&
		currentYear.value === now.getFullYear()
	);
};

const isSelected = (day) => {
	if (!props.modelValue) return false;
	const d = new Date(props.modelValue);
	return (
		day === d.getDate() &&
		currentMonth.value === d.getMonth() &&
		currentYear.value === d.getFullYear()
	);
};

const hasEvent = (day) => {
	const dateStr = `${currentYear.value}-${String(currentMonth.value + 1).padStart(
		2,
		"0"
	)}-${String(day).padStart(2, "0")}`;
	return props.events.includes(dateStr);
};

const selectDate = (day) => {
	const date = new Date(currentYear.value, currentMonth.value, day);
	emit("update:modelValue", date);
	emit("change", date);
};

const selectedFormatted = computed(() => {
	if (!props.modelValue) return "No date selected";
	return new Intl.DateTimeFormat("en-US", {
		weekday: "long",
		year: "numeric",
		month: "long",
		day: "numeric",
	}).format(new Date(props.modelValue));
});
</script>
