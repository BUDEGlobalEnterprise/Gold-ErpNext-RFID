<template>
	<div :class="['repair-timeline', orientation === 'vertical' ? 'vertical' : 'horizontal']">
		<!-- Compact inline mode (for cards) -->
		<div v-if="variant === 'compact'" class="flex items-center gap-0.5 w-full">
			<template v-for="(step, idx) in steps" :key="step.status">
				<div
					class="flex items-center gap-0.5"
					:title="`${step.label}${step.timestamp ? ' — ' + formatTimestamp(step.timestamp) : ''}`"
				>
					<div
						class="w-2 h-2 rounded-full transition-all duration-300 flex-shrink-0"
						:class="getCompactDotClass(step)"
					></div>
				</div>
				<div
					v-if="idx < steps.length - 1"
					class="flex-1 h-[2px] min-w-[8px] transition-all duration-300"
					:class="step.completed ? 'bg-[#D4AF37]' : 'bg-gray-200 dark:bg-gray-700'"
				></div>
			</template>
		</div>

		<!-- Full timeline mode (horizontal) -->
		<div v-else-if="orientation === 'horizontal'" class="flex items-start w-full overflow-x-auto pb-2">
			<template v-for="(step, idx) in steps" :key="step.status">
				<div class="flex flex-col items-center min-w-[80px] flex-1 relative group">
					<!-- Connector line (before dot) -->
					<div class="flex items-center w-full absolute top-[14px]">
						<div
							v-if="idx > 0"
							class="flex-1 h-[2px] transition-all duration-500"
							:class="step.completed || step.active ? 'bg-[#D4AF37]' : 'bg-gray-200 dark:bg-gray-700'"
						></div>
						<div v-else class="flex-1"></div>
						<div
							v-if="idx < steps.length - 1"
							class="flex-1 h-[2px] transition-all duration-500"
							:class="step.completed ? 'bg-[#D4AF37]' : 'bg-gray-200 dark:bg-gray-700'"
						></div>
						<div v-else class="flex-1"></div>
					</div>

					<!-- Step dot -->
					<div
						class="relative z-10 w-7 h-7 rounded-full flex items-center justify-center transition-all duration-300 border-2"
						:class="getStepDotClass(step)"
					>
						<!-- Check icon for completed -->
						<svg v-if="step.completed" class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
						</svg>
						<!-- Pulse animation for active -->
						<span
							v-else-if="step.active"
							class="w-2.5 h-2.5 bg-white rounded-full animate-pulse"
						></span>
						<!-- Empty dot for pending -->
						<span v-else class="w-2 h-2 bg-gray-300 dark:bg-gray-600 rounded-full"></span>
					</div>

					<!-- Label -->
					<p
						class="text-[10px] font-semibold mt-1.5 text-center leading-tight transition-colors"
						:class="
							step.active
								? 'text-[#D4AF37]'
								: step.completed
									? 'text-gray-700 dark:text-gray-300'
									: 'text-gray-400 dark:text-gray-500'
						"
					>
						{{ step.label }}
					</p>

					<!-- Timestamp -->
					<p
						v-if="step.timestamp && (step.completed || step.active)"
						class="text-[9px] text-gray-400 dark:text-gray-500 mt-0.5 text-center"
					>
						{{ formatTimestamp(step.timestamp) }}
					</p>

					<!-- User badge on hover -->
					<div
						v-if="step.user && (step.completed || step.active)"
						class="opacity-0 group-hover:opacity-100 transition-opacity absolute -bottom-5 text-[8px] text-gray-400 whitespace-nowrap"
					>
						{{ step.user }}
					</div>
				</div>
			</template>
		</div>

		<!-- Vertical timeline mode -->
		<div v-else class="flex flex-col">
			<div v-for="(step, idx) in steps" :key="step.status" class="flex gap-3 group">
				<!-- Left column: dot + connector -->
				<div class="flex flex-col items-center">
					<div
						class="w-7 h-7 rounded-full flex items-center justify-center transition-all duration-300 border-2 flex-shrink-0"
						:class="getStepDotClass(step)"
					>
						<svg v-if="step.completed" class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
						</svg>
						<span
							v-else-if="step.active"
							class="w-2.5 h-2.5 bg-white rounded-full animate-pulse"
						></span>
						<span v-else class="w-2 h-2 bg-gray-300 dark:bg-gray-600 rounded-full"></span>
					</div>
					<div
						v-if="idx < steps.length - 1"
						class="w-[2px] flex-1 min-h-[24px] transition-all duration-500"
						:class="step.completed ? 'bg-[#D4AF37]' : 'bg-gray-200 dark:bg-gray-700'"
					></div>
				</div>

				<!-- Right column: content -->
				<div class="pb-4 flex-1 min-w-0">
					<div class="flex items-center gap-2">
						<p
							class="text-sm font-semibold transition-colors"
							:class="
								step.active
									? 'text-[#D4AF37]'
									: step.completed
										? 'text-gray-800 dark:text-gray-200'
										: 'text-gray-400 dark:text-gray-500'
							"
						>
							{{ step.label }}
							<span
								v-if="step.active"
								class="ml-1.5 inline-flex items-center gap-1 px-1.5 py-0.5 bg-[#D4AF37]/10 text-[#D4AF37] text-[10px] font-bold rounded-full"
							>
								<span class="w-1.5 h-1.5 bg-[#D4AF37] rounded-full animate-pulse"></span>
								NOW
							</span>
						</p>
					</div>
					<p
						v-if="step.timestamp && (step.completed || step.active)"
						class="text-xs text-gray-400 dark:text-gray-500 mt-0.5"
					>
						{{ formatTimestamp(step.timestamp) }}
						<span v-if="step.user" class="ml-1">· {{ step.user }}</span>
					</p>
					<p
						v-if="step.active && predictedDate"
						class="text-xs text-blue-500 dark:text-blue-400 mt-1 flex items-center gap-1"
					>
						<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						Est. ready: {{ formatDate(predictedDate) }}
					</p>
					<p
						v-if="step.notes"
						class="text-xs text-gray-500 dark:text-gray-400 mt-1 bg-gray-50 dark:bg-white/5 rounded px-2 py-1"
					>
						{{ step.notes }}
					</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
	/** Current status of the repair */
	currentStatus: { type: String, default: '' },
	/** Array of timeline events from API: [{status, timestamp, user, notes}] */
	events: { type: Array, default: () => [] },
	/** 'horizontal' or 'vertical' */
	orientation: { type: String, default: 'horizontal' },
	/** 'full' or 'compact' */
	variant: { type: String, default: 'full' },
	/** Predicted completion date */
	predictedDate: { type: String, default: '' },
})

const STATUS_FLOW = [
	{ status: 'Received', label: 'Received' },
	{ status: 'Estimated', label: 'Estimated' },
	{ status: 'Approved', label: 'Approved' },
	{ status: 'In Progress', label: 'In Progress' },
	{ status: 'Waiting for Parts', label: 'Parts' },
	{ status: 'Quality Check', label: 'QC' },
	{ status: 'Ready for Pickup', label: 'Ready' },
	{ status: 'Delivered', label: 'Delivered' },
]

const steps = computed(() => {
	const currentIdx = STATUS_FLOW.findIndex((s) => s.status === props.currentStatus)

	// Build an event lookup map: status → {timestamp, user, notes}
	const eventMap = {}
	for (const ev of props.events) {
		if (ev.status) {
			eventMap[ev.status] = {
				timestamp: ev.timestamp || ev.creation,
				user: ev.user_name || ev.user || '',
				notes: ev.notes || '',
			}
		}
	}

	return STATUS_FLOW.map((flowStep, idx) => {
		const event = eventMap[flowStep.status]
		return {
			status: flowStep.status,
			label: flowStep.label,
			completed: idx < currentIdx,
			active: idx === currentIdx,
			pending: idx > currentIdx,
			timestamp: event?.timestamp || '',
			user: event?.user || '',
			notes: event?.notes || '',
		}
	})
})

function getStepDotClass(step) {
	if (step.completed) {
		return 'bg-[#D4AF37] border-[#D4AF37]'
	}
	if (step.active) {
		return 'bg-[#D4AF37] border-[#D4AF37] shadow-lg shadow-[#D4AF37]/30 scale-110'
	}
	return 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600'
}

function getCompactDotClass(step) {
	if (step.completed) return 'bg-[#D4AF37]'
	if (step.active) return 'bg-[#D4AF37] ring-2 ring-[#D4AF37]/30 scale-125'
	return 'bg-gray-200 dark:bg-gray-600'
}

function formatTimestamp(ts) {
	if (!ts) return ''
	try {
		const d = new Date(ts)
		return d.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
		})
	} catch {
		return String(ts)
	}
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	try {
		const d = new Date(dateStr)
		return d.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
		})
	} catch {
		return String(dateStr)
	}
}
</script>
