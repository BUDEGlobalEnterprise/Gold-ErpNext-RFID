<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useEmployeeStore } from "@/stores/employee";
import { useAttendanceStore } from "@/stores/attendance";

const employeeStore = useEmployeeStore();
const attendance = useAttendanceStore();
const loading = ref(false);
const breakLoading = ref(false);
const error = ref("");
const isClockedIn = ref(false);
const isCompleted = computed(() => attendance.isDayCompleted);
const clockInTime = ref(null);
const elapsed = ref(0);
const onBreak = ref(false);
const totalBreakMinutes = ref(0);
const breakCount = ref(0);
const breakStartTime = ref(null);
const breakElapsed = ref(0);
let timerInterval = null;
let breakTickInterval = null;
let statusSynced = false;
const statusLoading = ref(true);
let timerAnchorTime = 0;    // Date.now() when timer started
let timerAnchorElapsed = 0; // elapsed seconds at anchor point
let lastTotalSeconds = 0;   // last known total_seconds_today from backend

const SHIFT_SECONDS = computed(() => {
  return Math.abs(attendance.workingHoursTarget || 8) * 3600;
});
const RADIUS = 82;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const progress = computed(() => {
  if (elapsed.value === 0) return 0;
  return Math.min(elapsed.value / SHIFT_SECONDS.value, 1);
});

const shiftTargetDisplay = computed(() => {
  const targetHours = Math.abs(attendance.workingHoursTarget || 8);
  const h = Math.floor(targetHours);
  const m = Math.round((targetHours - h) * 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")} Target`;
});

const shiftComplete = computed(() => progress.value >= 1);

const dashOffset = computed(() => CIRCUMFERENCE * (1 - progress.value));

const timerDisplay = computed(() => {
  const h = Math.floor(elapsed.value / 3600);
  const m = Math.floor((elapsed.value % 3600) / 60);
  const s = elapsed.value % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
});

const breakTimerDisplay = computed(() => {
  const total = breakElapsed.value;
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
});

const clockInTimeFormatted = computed(() => {
  if (!clockInTime.value) return "";
  return clockInTime.value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
});

const breakMinutesFormatted = computed(() => {
  const totalMinutes = Math.floor(totalBreakMinutes.value);
  const h = Math.floor(totalMinutes / 60);
  const m = Math.floor(totalMinutes % 60);
  const s = Math.floor((totalBreakMinutes.value * 60) % 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
});

const ringColor = computed(() => {
  if (onBreak.value) return "#f59e0b";
  if (isCompleted.value) return "#22c55e";
  if (shiftComplete.value) return "#22c55e";
  return "#ef4444";
});

const glowColor = computed(() => {
  if (onBreak.value) return "rgba(245, 158, 11, 0.3)";
  if (isCompleted.value) return "rgba(34, 197, 94, 0.35)";
  if (shiftComplete.value) return "rgba(34, 197, 94, 0.35)";
  return "rgba(239, 68, 68, 0.25)";
});

function startTimer() {
  stopTimer();
  stopBreakTick();
  // Tick elapsed locally from the anchor point
  timerInterval = setInterval(() => {
    elapsed.value = timerAnchorElapsed + Math.floor((Date.now() - timerAnchorTime) / 1000);
  }, 1000);
}

function startBreakTick() {
  stopBreakTick();
  // Tick breakElapsed while on break so the display updates
  breakTickInterval = setInterval(() => {
    if (onBreak.value && breakStartTime.value) {
      breakElapsed.value = Math.floor((Date.now() - breakStartTime.value.getTime()) / 1000);
    }
  }, 1000);
}

function stopBreakTick() {
  if (breakTickInterval) {
    clearInterval(breakTickInterval);
    breakTickInterval = null;
  }
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

async function fetchStatus() {
  try {
    const empId = attendance.employeeId;
    if (!empId) return;
    await attendance.fetchTodayStatus(empId);

    const data = attendance.todayStatus;
    if (!data) return;

    statusSynced = true;
    const firstInLog = data.logs?.find((l) => l.log_type === "IN");

    const newTotal = data.total_seconds_today || 0;

    // Compute elapsed from backend anchor — ticks forward using Date.now() drift
    if (lastTotalSeconds > 0 && data.checked_in) {
      // Resuming: elapsed = last known total + time since last fetch
      const drift = Math.floor((Date.now() - timerAnchorTime) / 1000);
      elapsed.value = lastTotalSeconds + drift;
    } else {
      // First fetch or not checked in
      elapsed.value = newTotal;
    }

    // Build clockInTime from logs (first IN log) for display
    if (firstInLog) {
      clockInTime.value = new Date(firstInLog.time);
    } else if (data.is_still_checked_in && data.last_in_from_prev_day) {
      clockInTime.value = new Date(data.last_in_from_prev_day);
    }

    // Derive break info from check-in logs (backend returns logs, not a breaks object)
    const entries = data.logs || [];
    breakCount.value = entries.filter((l) => l.note === "Break Start").length;
    const breakStartLogs = entries.filter((l) => l.note === "Break Start");
    const breakEndLogs = entries.filter((l) => l.note === "Break End");
    let totalMs = 0;
    for (let i = 0; i < breakEndLogs.length; i++) {
      totalMs += new Date(breakEndLogs[i].time).getTime() - new Date(breakStartLogs[i].time).getTime();
    }
    totalBreakMinutes.value = totalMs / 60000;

    // Find the most recent break start log without a matching break-end log
    let breakStartIndex = -1;
    for (let i = entries.length - 1; i >= 0; i--) {
      if (entries[i].note === "Break Start") {
        breakStartIndex = i;
        break;
      }
    }
    if (breakStartIndex >= 0) {
      const logTypeAfter = entries[breakStartIndex + 1]?.log_type;
      const isStillOnBreak =
        !logTypeAfter || logTypeAfter === "OUT" || logTypeAfter === "Break Start";
      if (isStillOnBreak) {
        breakStartTime.value = new Date(entries[breakStartIndex].time);
      } else {
        // Break was already ended — don't set breakStartTime
        breakStartTime.value = null;
      }
    } else {
      breakStartTime.value = null;
    }

    // Determine state from backend data
    if (data.is_on_break) {
      // Currently on break — stop work timer, start break tick
      isClockedIn.value = true;
      onBreak.value = true;
      lastTotalSeconds = 0;
      stopTimer();
      startBreakTick();
    } else if ((data.checked_in || data.is_still_checked_in) && data.last_log_type !== "OUT") {
      // Clocked in and actively working
      isClockedIn.value = true;
      onBreak.value = false;
      timerAnchorTime = Date.now();
      timerAnchorElapsed = elapsed.value;
      lastTotalSeconds = newTotal;
      stopBreakTick();
      startTimer();
    } else if (data.last_log_type === "OUT" && data.logs?.length >= 2 && isCompleted.value) {
      // Both IN and OUT done for today — day complete
      isClockedIn.value = false;
      onBreak.value = false;
      elapsed.value = data.total_seconds_today || 0;
      stopTimer();
    } else {
      // Nothing happened today OR completed state has vanished
      isClockedIn.value = false;
      clockInTime.value = null;
      elapsed.value = 0;
      onBreak.value = false;
      stopTimer();
    }
  } catch {
    // Silently fail
  } finally {
    statusLoading.value = false;
  }
}

async function handleClockIn() {
  const empId = employeeStore.employee?.name;
  if (!empId) {
    error.value = "No employee ID found";
    return;
  }
  if (isCompleted.value || onBreak.value) return;
  loading.value = true;
  error.value = "";
  try {
    const shift = attendance.todayStatus?.active_shift_name;
    const result = await attendance.clockIn(empId, null, null, null, shift);
    if (result && (result.success || result.checked_in)) {
      // Refresh status from backend to get accurate state
      await fetchStatus();
      emit("punched");
    } else {
      error.value = result?.message || result?.error || "Clock in failed";
    }
  } catch (e) {
    error.value = attendance.error || e.message || "Something went wrong";
  } finally {
    loading.value = false;
  }
}

async function handleClockOut() {
  const empId = employeeStore.employee?.name;
  if (!empId) {
    error.value = "No employee ID found";
    return;
  }
  if (!isClockedIn.value || isCompleted.value) return;
  loading.value = true;
  error.value = "";
  try {
    const shift = attendance.todayStatus?.active_shift_name;
    const result = await attendance.clockOut(empId, null, null, null, shift);
    if (result && (result.success || result.checked_out)) {
      // Refresh status from backend to get accurate elapsed time and state
      await fetchStatus();
      emit("punched");
    } else {
      error.value = result?.message || result?.error || "Clock out failed";
    }
  } catch (e) {
    error.value = attendance.error || e.message || "Something went wrong";
  } finally {
    loading.value = false;
  }
}

async function handleBreak() {
  breakLoading.value = true;
  error.value = "";
  try {
    if (onBreak.value) {
      // End break — refresh status from backend to get accurate state
      await attendance.endBreak();
      await fetchStatus();
    } else {
      // Start break
      await attendance.startBreak();
      // Refresh status from backend to get accurate state
      await fetchStatus();
    }
  } catch (e) {
    error.value = attendance.error || e.message || "Something went wrong";
  } finally {
    breakLoading.value = false;
  }
}

onMounted(async () => {
  await employeeStore.init();
  // attendance.employeeId may already be set by Dashboard init
  // Wait briefly for it to be ready if not
  if (!attendance.employeeId) {
    await new Promise((resolve) => {
      const check = () => {
        if (attendance.employeeId) resolve();
        else setTimeout(check, 50);
      };
      setTimeout(resolve, 3000); // fallback timeout
      check();
    });
  }
  await fetchStatus();
});

watch(isCompleted, () => {
  fetchStatus();
});

onUnmounted(() => {
  stopTimer();
  stopBreakTick();
});

const emit = defineEmits(["punched"]);
</script>

<template>
  <div class="flex flex-col items-center">
    <!-- SVG Clock Ring -->
    <div class="relative mb-6">
      <svg width="200" height="200" class="transform -rotate-90">
        <!-- Background ring (filled track, tinted by theme color) -->
        <circle
          :cx="100"
          :cy="100"
          :r="RADIUS"
          :fill="ringColor"
          fill-opacity="0.12"
          stroke-width="0"
        />
        <!-- Progress ring -->
        <circle
          :cx="100"
          :cy="100"
          :r="RADIUS"
          fill="none"
          :stroke="ringColor"
          stroke-width="6"
          stroke-linecap="round"
          :stroke-dasharray="CIRCUMFERENCE"
          :stroke-dashoffset="dashOffset"
          class="transition-all duration-1000"
        />
      </svg>

      <!-- Center content (non-clickable, just display) -->
      <div
        class="absolute inset-0 m-auto w-[140px] h-[140px] rounded-full flex flex-col items-center justify-center gap-1 bg-white/5 dark:bg-white/[0.03]"
      >
        <div
          v-if="statusLoading || loading"
          class="w-6 h-6 border-2 border-current border-t-transparent rounded-full animate-spin"
        />
        <template v-else>
          <span
            v-if="onBreak"
            class="text-2xl font-bold tabular-nums tracking-tight text-orange-500"
          >
            {{ breakTimerDisplay }}
          </span>
          <span
            v-else-if="isCompleted"
            class="text-2xl font-bold tabular-nums tracking-tight text-emerald-400"
          >
            {{ timerDisplay }}
          </span>
          <span
            v-else-if="isClockedIn"
            class="text-2xl font-bold tabular-nums tracking-tight"
            :class="shiftComplete ? 'text-emerald-400' : 'text-red-400'"
          >
            {{ timerDisplay }}
          </span>
          <span v-else class="text-[11px] font-semibold uppercase tracking-wider opacity-70 text-gray-500 dark:text-white/70">
            Shift Elapsed
          </span>
          
          <span
            v-if="onBreak"
            class="text-[11px] font-medium text-orange-500"
          >
            On Break
          </span>
          <span
            v-else-if="isClockedIn || isCompleted"
            class="text-[11px] font-medium"
            :class="isCompleted ? 'text-emerald-400' : shiftComplete ? 'text-emerald-400' : 'text-red-400'"
          >
            {{ isCompleted ? 'Day Complete' : shiftComplete ? 'Shift Complete' : shiftTargetDisplay }}
          </span>
        </template>
      </div>
    </div>

    <!-- Clock In/Out Button -->
    <div class="mb-3 w-full">
      <button
        v-if="!isClockedIn && !isCompleted"
        @click="handleClockIn"
        :disabled="loading"
        class="w-full py-3 bg-green-500/15 text-green-400 border border-green-500/30 font-medium rounded-lg text-sm transition-all hover:bg-green-500/25 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-green-500/20 dark:text-green-300 dark:border-green-500/40"
      >
        <div
          v-if="loading"
          class="w-5 h-5 border-2 border-green-400 border-t-transparent rounded-full animate-spin mx-auto dark:border-green-300"
        />
        <template v-else>CLOCK IN</template>
      </button>

      <button
        v-else-if="isClockedIn && !isCompleted"
        @click="handleClockOut"
        :disabled="loading"
        class="w-full py-3 bg-[#064e3b]/15 text-[#064e3b] border border-[#064e3b]/30 font-medium rounded-lg text-sm transition-all hover:bg-[#064e3b]/25 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-green-500/20 dark:text-green-300 dark:border-green-500/40"
      >
        <div
          v-if="loading"
          class="w-5 h-5 border-2 border-[#064e3b] border-t-transparent rounded-full animate-spin mx-auto dark:border-green-300"
        />
        <template v-else>CLOCK OUT</template>
      </button>

      <div
        v-else-if="isCompleted"
        class="w-full py-3 bg-emerald-500/15 text-emerald-400 font-medium rounded-lg text-sm text-center border border-emerald-500/30"
      >
        Day Complete
      </div>
    </div>

    <!-- Break Button (only enabled when clocked in) -->
    <div class="mb-4 w-full">
      <button
        v-if="isClockedIn && !isCompleted"
        @click="handleBreak"
        :disabled="breakLoading"
        class="w-full flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200"
        :class="[
          'bg-[#FFA500]/15 text-[#FFA500] border border-[#FFA500]/30 hover:bg-[#FFA500]/25 dark:bg-orange-500/20 dark:text-orange-300 dark:border-orange-500/40 dark:hover:bg-orange-500/30'
          
        ]"
      >
        <div
          v-if="breakLoading && !onBreak"
          class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
        />
        <span v-if="onBreak">End Break · {{ breakTimerDisplay }}</span>
        <span v-else>Take Break</span>
      </button>
    </div>

    <!-- Break Info -->
    <div
      v-if="(isClockedIn || isCompleted) && breakCount > 0 && !onBreak"
      class="mb-3 px-3 py-1.5 bg-white/[0.03] dark:bg-white/5 rounded-lg text-xs text-gray-500 dark:text-white/50 text-center"
    >
      {{ breakCount }} break{{ breakCount !== 1 ? "s" : "" }} ·
      {{ breakMinutesFormatted }}
    </div>

    <!-- Status text -->
    <div class="text-center space-y-1.5">
      <div v-if="isCompleted" class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mb-2">
        Day Complete
      </div>
      <div v-else-if="onBreak" class="text-xs font-semibold text-amber-600 dark:text-amber-400 mb-2">
        On Break
      </div>
      <div v-else-if="shiftComplete && isClockedIn" class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mb-2">
        Shift Complete
      </div>

      <p v-if="isCompleted" class="text-sm text-gray-500 dark:text-white/50">
        Worked <span class="text-gray-900 dark:text-white font-medium">{{ timerDisplay }}</span> today
      </p>
      <p v-else-if="onBreak" class="text-sm text-amber-400/80">Break started · Timer paused</p>
      <p v-else-if="isClockedIn && clockInTimeFormatted" class="text-sm text-gray-500 dark:text-white/50">
        Clocked in at <span class="text-gray-900 dark:text-white font-medium">{{ clockInTimeFormatted }}</span>
      </p>
      <p v-else class="text-sm text-gray-400 dark:text-white/40">Tap CLOCK IN to start your shift</p>
    </div>

    <p v-if="error" class="mt-3 text-xs text-red-650 dark:text-red-400 text-center font-semibold max-w-[220px]">{{ error }}</p>
  </div>
</template>
