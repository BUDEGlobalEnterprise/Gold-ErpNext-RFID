<template>
	<!-- Kanban board for Shop Floor Control — Zevar-style ──────────────────── -->
	<div
		class="flex flex-col h-full bg-[#F5F0E8] dark:bg-warm-dark-950 transition-colors duration-300"
	>
		<!-- Header ─────────────────────────────────────────────────────── -->
		<div
			class="bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md border-b border-gray-200 dark:border-warm-border/50 px-4 py-3 flex items-center justify-between shrink-0"
		>
			<div>
				<h2
					class="premium-title tracking-tighter text-xl text-gray-900 dark:text-white"
				>
					Shop Floor Control
				</h2>
				<p
					class="text-[10px] font-black uppercase tracking-widest text-gray-500 dark:text-gray-400"
				>
					Job Bag Pipeline
				</p>
			</div>
			<!-- Navigation Buttons -->
			<div class="flex items-center gap-2 bg-gray-50 dark:bg-warm-dark-900 p-1 rounded-lg ml-8">
				<button 
					@click="$router.push('/special-orders')"
					class="px-4 py-1.5 text-sm font-bold rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
				>
					Order Intake
				</button>
				<button 
					@click="$router.push('/special-orders/job-bag')"
					class="px-4 py-1.5 text-sm font-bold rounded-md bg-white dark:bg-warm-dark-800 text-gray-900 dark:text-white shadow-sm"
				>
					Job Bag Dashboard
				</button>
			</div>
			<div class="flex items-center gap-2">
				<!-- Filters -->
				<select
					v-model="filterStatus"
					class="h-8 bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-xs font-bold text-gray-800 dark:text-gray-200 px-3 focus:ring-2 focus:ring-[#D4AF37] outline-none cursor-pointer"
				>
					<option value="all">All Jobs</option>
					<option v-for="s in workflowStatuses" :key="s" :value="s">
						{{ formatStatus(s) }}
					</option>
				</select>
				<Button
					@click="refreshJobs"
					class="h-8 px-3 rounded-lg text-xs font-bold bg-[#D4AF37] text-[#1E2022] hover:bg-[#CBA358] transition-all"
				>
					<svg
						class="w-3.5 h-3.5"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
						/>
					</svg>
				</Button>
			</div>
		</div>

		<!-- Kanban columns ─────────────────────────────────────────────── -->
		<div
			class="flex-1 overflow-x-auto overflow-y-hidden p-4"
		>
			<div class="flex gap-4 h-full min-w-max">
				<!-- Column ─────────────────────────────────────────────────── -->
				<div
					v-for="status in kanbanStatuses"
					:key="status.value"
					class="flex flex-col w-72 shrink-0"
				>
					<!-- Column header ────────────────────────────────────────── -->
					<div
						class="flex items-center gap-2 px-3 py-2.5 rounded-t-xl border-b-2"
						:class="[
							status.headerBg,
							status.headerBorder,
						]"
					>
						<div
							class="w-2.5 h-2.5 rounded-full"
							:class="status.dotColor"
						></div>
						<span
							class="text-[10px] font-black uppercase tracking-widest text-gray-700 dark:text-gray-200"
						>
							{{ status.label }}
						</span>
						<span
							class="ml-auto text-[10px] font-black bg-white/50 dark:bg-warm-dark-800/50 rounded-full px-2 py-0.5 text-gray-500 dark:text-gray-400"
						>
							{{ filteredJobsByStatus(status.value).length }}
						</span>
					</div>

					<!-- Drop zone ────────────────────────────────────────────── -->
					<div
						class="flex-1 overflow-y-auto p-2 space-y-2 rounded-b-xl bg-white/30 dark:bg-warm-dark-900/30"
						:class="
							isDragOverStatus[status.value]
								? 'ring-2 ring-[#D4AF37] ring-dashed bg-[#D4AF37]/5'
								: ''
						"
						@dragover.prevent="isDragOverStatus[status.value] = true"
						@dragleave.prevent="isDragOverStatus[status.value] = false"
						@drop.prevent="handleDrop($event, status.value)"
					>
						<!-- Job card ─────────────────────────────────────────── -->
						<div
							v-for="job in filteredJobsByStatus(status.value)"
							:key="job.name"
							class="rounded-xl border cursor-grab active:cursor-grabbing transition-all"
							:class="[
								darkModeCardBg,
								jobStatusBorder(job.status),
							]"
							draggable="true"
							@dragstart="onDragStart($event, job.name)"
							@dragend="onDragEnd"
						>
							<!-- Card header ────────────────────────────────────── -->
							<div class="px-3 py-2.5">
								<div class="flex items-center justify-between mb-1.5">
									<span
										class="text-[10px] font-black uppercase tracking-widest text-gray-400 dark:text-gray-500"
									>
										{{ job.custom_order_number || job.name }}
									</span>
									<!-- Priority badge ───────────────────────────── -->
									<span
										v-if="job.custom_priority === 'Urgent'"
										class="px-1.5 py-0.5 rounded text-[8px] font-black uppercase bg-red-500/10 text-red-500 border border-red-500/20"
									>
										URGENT
									</span>
									<span
										v-else-if="job.custom_priority === 'High'"
										class="px-1.5 py-0.5 rounded text-[8px] font-black uppercase bg-orange-500/10 text-orange-500 border border-orange-500/20"
									>
										HIGH
									</span>
								</div>

								<!-- Customer name ────────────────────────────── -->
								<p
									class="text-xs font-bold text-gray-800 dark:text-gray-100 truncate"
								>
									{{ job.customer_name || job.customer }}
								</p>

								<!-- Item name ──────────────────────────────── -->
								<p
									class="text-[11px] text-gray-500 dark:text-gray-400 truncate mt-0.5"
								>
									{{ job.custom_item_description || 'Special Order' }}
								</p>
							</div>

							<!-- Card footer ──────────────────────────────────── -->
							<div
								class="flex items-center justify-between px-3 py-2 border-t border-gray-200/50 dark:border-warm-border/30"
							>
								<!-- Assignee ─────────────────────────────── -->
								<div
									v-if="job.custom_assigned_to"
									class="flex items-center gap-1.5"
								>
									<div
										class="w-5 h-5 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] flex items-center justify-center text-[8px] font-bold text-[#1E2022]"
									>
										{{ getInitials(job.custom_assigned_to) }}
									</div>
									<span
										class="text-[9px] font-bold text-gray-500 dark:text-gray-400 truncate max-w-[80px]"
									>
										{{ getInitials(job.custom_assigned_to) }}
									</span>
								</div>

								<!-- Due date ─────────────────────────────── -->
								<span
									v-if="job.custom_due_date"
									class="text-[9px] font-bold"
									:class="
										isOverdue(job.custom_due_date)
											? 'text-red-500'
											: 'text-gray-400 dark:text-gray-500'
									"
								>
									{{ formatDate(job.custom_due_date) }}
								</span>
							</div>
						</div>

						<!-- Empty column ─────────────────────────────────────── -->
						<div
							v-if="filteredJobsByStatus(status.value).length === 0"
							class="flex items-center justify-center h-24 rounded-xl border-2 border-dashed border-gray-200 dark:border-warm-border/30"
						>
							<span
								class="text-[10px] font-bold text-gray-300 dark:text-gray-600 uppercase tracking-wider"
							>
								No jobs
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { createResource } from 'frappe-ui'

const darkModeCardBg = 'bg-[#1E2022] dark:bg-[#1E2022]'

// Workflow statuses (columns)
const workflowStatuses = [
	'Quoted',
	'Approved',
	'Procurement',
	'In Production',
	'QC Check',
	'Completed',
	'Delivered',
]

const kanbanStatuses = workflowStatuses.map((s) => {
	const colors = {
		Quoted: { headerBg: 'bg-gray-100/50 dark:bg-gray-800/50', headerBorder: 'border-gray-400 dark:border-gray-500', dotColor: 'bg-gray-400' },
		Approved: { headerBg: 'bg-blue-50/50 dark:bg-blue-900/20', headerBorder: 'border-blue-400', dotColor: 'bg-blue-500' },
		Procurement: { headerBg: 'bg-purple-50/50 dark:bg-purple-900/20', headerBorder: 'border-purple-400', dotColor: 'bg-purple-500' },
		'In Production': { headerBg: 'bg-amber-50/50 dark:bg-amber-900/20', headerBorder: 'border-amber-400', dotColor: 'bg-amber-500' },
		'QC Check': { headerBg: 'bg-orange-50/50 dark:bg-orange-900/20', headerBorder: 'border-orange-400', dotColor: 'bg-orange-500' },
		Completed: { headerBg: 'bg-green-50/50 dark:bg-green-900/20', headerBorder: 'border-green-400', dotColor: 'bg-green-500' },
		Delivered: { headerBg: 'bg-emerald-50/50 dark:bg-emerald-900/20', headerBorder: 'border-emerald-400', dotColor: 'bg-emerald-500' },
	}
	return {
		label: s,
		value: s,
		...colors[s],
	}
})

// Jobs data
const jobs = ref([])
const filterStatus = ref('all')
const draggedJobId = ref(null)
const isDragOverStatus = ref({})

// Dark mode toggle (from existing UI store pattern)
const darkModeCardBgClass = 'bg-[#1E2022] dark:bg-[#1E2022]'

const filteredJobs = computed(() => {
	if (filterStatus.value === 'all') return jobs.value
	return jobs.value.filter((j) => j.status === filterStatus.value)
})

function filteredJobsByStatus(status) {
	if (filterStatus.value !== 'all' && filterStatus.value !== status) return []
	return filteredJobs.value.filter((j) => j.status === status)
}

function jobStatusBorder(status) {
	const borderMap = {
		Quoted: 'border-gray-300/50 dark:border-gray-600/50',
		Approved: 'border-blue-300/50 dark:border-blue-600/50',
		Procurement: 'border-purple-300/50 dark:border-purple-600/50',
		'In Production': 'border-amber-300/50 dark:border-amber-600/50',
		'QC Check': 'border-orange-300/50 dark:border-orange-600/50',
		Completed: 'border-green-300/50 dark:border-green-600/50',
		Delivered: 'border-emerald-300/50 dark:border-emerald-600/50',
	}
	return borderMap[status] || 'border-gray-300/50 dark:border-gray-600/50'
}

// Fetch jobs from backend
const jobsResource = createResource({
	url: 'zevar_core.api.special_order.get_job_bag_list',
	auto: true,
})

watch(() => jobsResource.data, (newData) => {
	if (newData) {
		jobs.value = newData
	}
}, { immediate: true })

onMounted(() => {
	if (jobsResource.data) {
		jobs.value = jobsResource.data
	}
})

function refreshJobs() {
	jobsResource.fetch()
}

// Drag and drop
function onDragStart(event, jobId) {
	draggedJobId.value = jobId
	event.dataTransfer.effectAllowed = 'move'
	// Set a minimal transparent drag image
	const img = new Image()
	img.src = 'data:image/gif,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='
	event.dataTransfer.setDragImage(img, 0, 0)
}

function onDragEnd() {
	draggedJobId.value = null
	isDragOverStatus.value = {}
}

async function handleDrop(event, newStatus) {
	isDragOverStatus.value = {}
	const jobId = draggedJobId.value
	if (!jobId) return

	try {
		await createResource({
			url: 'zevar_core.api.special_order.update_job_status',
			makeParams() {
				return { job_name: jobId, new_status: newStatus }
			},
		}).fetch()
		// Refresh the list
		jobsResource.fetch()
	} catch (e) {
		console.error('[ShopFloor] update status error:', e)
	}

	draggedJobId.value = null
}

function getInitials(name) {
	if (!name) return '?'
	return name
		.split(' ')
		.map((w) => w[0])
		.join('')
		.toUpperCase()
		.slice(0, 2)
}

function isOverdue(dateStr) {
	if (!dateStr) return false
	return new Date(dateStr) < new Date()
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	const d = new Date(dateStr)
	return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatStatus(s) {
	return s
}
</script>
