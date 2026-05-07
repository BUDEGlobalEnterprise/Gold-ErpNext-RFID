<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Time Clock</h2>
				<button
					@click="refreshStatus"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
					title="Refresh"
				>
					<svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': hr.checkinStatusResource.loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15" />
					</svg>
				</button>
			</div>

			<div class="flex-1 overflow-y-auto">
				<div v-if="hr.checkinStatusResource.loading && !hr.todayStatus" class="flex items-center justify-center py-20">
					<div class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"></div>
				</div>

				<div v-else class="max-w-md mx-auto space-y-4">
					<div class="premium-card !p-8 text-center">
						<div class="text-5xl font-bold text-gray-900 dark:text-white mb-1">{{ currentTime }}</div>
						<div class="text-sm text-gray-500 dark:text-gray-400">{{ currentDate }}</div>
					</div>

					<div class="premium-card !p-6 text-center">
						<div
							class="w-24 h-24 rounded-full mx-auto mb-4 flex items-center justify-center"
							:class="isCheckedIn ? 'bg-emerald-100 dark:bg-emerald-900/30' : 'bg-gray-100 dark:bg-gray-800'"
						>
							<svg class="w-10 h-10" :class="isCheckedIn ? 'text-emerald-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</div>
						<div class="text-lg font-bold mb-1" :class="isCheckedIn ? 'text-emerald-600' : 'text-gray-500'">
							{{ isCheckedIn ? 'Clocked In' : 'Clocked Out' }}
						</div>
						<div v-if="isCheckedIn && hr.todayStatus?.last_log_time" class="text-xs text-gray-400 mb-4">
							Since {{ formatTime(hr.todayStatus.last_log_time) }}
						</div>
						<div v-if="hr.todayStatus?.total_hours_today" class="text-2xl font-bold text-[#D4AF37] mb-4">
							{{ hr.todayStatus.total_hours_today }}h today
						</div>

						<button
							v-if="!isCheckedIn"
							@click="handleClockIn"
							:disabled="hr.clockInResource.loading"
							class="w-full py-4 rounded-xl text-lg font-bold bg-emerald-500 text-white hover:bg-emerald-600 transition disabled:opacity-50"
						>
							{{ hr.clockInResource.loading ? 'Clocking In...' : 'Clock In' }}
						</button>
						<button
							v-else
							@click="handleClockOut"
							:disabled="hr.clockOutResource.loading"
							class="w-full py-4 rounded-xl text-lg font-bold bg-red-500 text-white hover:bg-red-600 transition disabled:opacity-50"
						>
							{{ hr.clockOutResource.loading ? 'Clocking Out...' : 'Clock Out' }}
						</button>
					</div>

					<div v-if="hr.todayStatus?.logs?.length" class="premium-card !p-4">
						<h4 class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Today's Log</h4>
						<div class="space-y-2">
							<div v-for="(log, i) in hr.todayStatus.logs" :key="i" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-warm-dark-700 last:border-0">
								<div class="flex items-center gap-2">
									<span
										class="w-2 h-2 rounded-full"
										:class="log.log_type === 'IN' ? 'bg-emerald-500' : 'bg-red-500'"
									></span>
									<span class="text-xs font-bold" :class="log.log_type === 'IN' ? 'text-emerald-600' : 'text-red-500'">
										{{ log.log_type === 'IN' ? 'In' : 'Out' }}
									</span>
								</div>
								<span class="text-xs text-gray-500 dark:text-gray-400">{{ formatTime(log.time) }}</span>
							</div>
						</div>
					</div>

					<div v-if="hr.weeklyRoster?.schedule" class="premium-card !p-4">
						<h4 class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">This Week</h4>
						<div class="space-y-1">
							<div
								v-for="day in hr.weeklyRoster.schedule"
								:key="day.date"
								class="flex items-center justify-between py-1.5 text-xs"
								:class="day.is_today ? 'font-bold' : ''"
							>
								<span :class="day.is_today ? 'text-[#D4AF37]' : 'text-gray-500 dark:text-gray-400'">
									{{ day.day_short }} {{ day.day_num }}
								</span>
								<span :class="dayStatusClass(day)">
									{{ dayStatusText(day) }}
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useHRStore } from '../stores/hr'

const hr = useHRStore()

const currentTime = ref('')
const currentDate = ref('')
let timer = null

const isCheckedIn = computed(() => hr.todayStatus?.checked_in === true)

function updateClock() {
	const now = new Date()
	currentTime.value = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
	currentDate.value = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
}

function formatTime(timeStr) {
	if (!timeStr) return ''
	const d = new Date(timeStr)
	return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

function dayStatusClass(day) {
	if (day.is_today) return 'text-[#D4AF37]'
	if (day.status === 'complete') return 'text-emerald-500'
	if (day.status === 'partial') return 'text-amber-500'
	if (day.status === 'off') return 'text-gray-300 dark:text-gray-600'
	return 'text-gray-400'
}

function dayStatusText(day) {
	if (day.total_hours > 0) return `${day.total_hours}h`
	if (day.status === 'off') return 'Off'
	return day.status === 'working' ? 'Scheduled' : '—'
}

function refreshStatus() {
	hr.loadCheckinStatus()
	hr.loadWeeklyRoster()
}

async function handleClockIn() {
	await hr.clockIn()
	refreshStatus()
}

async function handleClockOut() {
	await hr.clockOut()
	refreshStatus()
}

onMounted(() => {
	updateClock()
	timer = setInterval(updateClock, 1000)
	refreshStatus()
})

onUnmounted(() => {
	if (timer) clearInterval(timer)
})
</script>
