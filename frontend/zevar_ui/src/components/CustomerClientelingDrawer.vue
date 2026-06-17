<template>
	<Teleport to="body">
		<!-- Backdrop -->
		<Transition
			enter-active-class="transition-opacity duration-300"
			enter-from-class="opacity-0"
			enter-to-class="opacity-100"
			leave-active-class="transition-opacity duration-200"
			leave-from-class="opacity-100"
			leave-to-class="opacity-0"
		>
			<div
				v-if="show"
				@click="emit('close')"
				class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[199]"
			></div>
		</Transition>

		<!-- Drawer -->
		<Transition
			enter-active-class="transition-transform duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
			enter-from-class="translate-x-full"
			enter-to-class="translate-x-0"
			leave-active-class="transition-transform duration-200 ease-in"
			leave-from-class="translate-x-0"
			leave-to-class="translate-x-full"
		>
			<div
				v-if="show"
				@keydown.escape="emit('close')"
				class="fixed right-0 top-0 bottom-0 w-full max-w-md z-[200] bg-[#FAF5EE] dark:bg-[#1a1610] border-l border-[#E8E0D4] dark:border-warm-border/50 shadow-[-20px_0_60px_rgba(0,0,0,0.15)] flex flex-col overflow-hidden"
				tabindex="-1"
			>
				<!-- Loading State -->
				<div v-if="loading" class="flex-1 flex items-center justify-center">
					<div class="flex flex-col items-center gap-3">
						<div
							class="animate-spin rounded-full h-8 w-8 border-2 border-gray-200 border-t-[#D4AF37]"
						></div>
						<span class="text-xs text-gray-400">Loading client profile...</span>
					</div>
				</div>

				<!-- Error State -->
				<div v-else-if="error" class="flex-1 flex items-center justify-center p-6">
					<div class="text-center">
						<p class="text-sm text-red-500 mb-2">{{ error }}</p>
						<button
							@click="reload"
							class="text-xs text-[#D4AF37] font-medium hover:underline"
						>
							Try again
						</button>
					</div>
				</div>

				<!-- Content -->
				<template v-else-if="profile">
					<!-- Close Button -->
					<button
						@click="emit('close')"
						class="absolute top-3 right-3 w-7 h-7 rounded-full bg-gray-100 dark:bg-warm-dark-700 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-white transition-colors z-10"
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
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>

					<!-- Header -->
					<div
						class="p-5 pb-4 border-b border-[#E8E0D4] dark:border-warm-border/30 shrink-0"
					>
						<div class="flex items-center gap-3 pr-8">
							<div
								class="w-12 h-12 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] flex items-center justify-center text-black font-black text-sm shrink-0"
							>
								{{ getInitial(profile.customer_name) }}
							</div>
							<div class="min-w-0 flex-1">
								<h2
									class="font-display text-lg font-semibold tracking-tight text-gray-900 dark:text-white truncate"
								>
									{{ profile.customer_name }}
								</h2>
								<div class="text-xs text-gray-500 truncate">
									{{
										[profile.mobile_no, profile.email_id]
											.filter(Boolean)
											.join(' · ') || 'No contact info'
									}}
								</div>
							</div>
						</div>

						<!-- Stats Row -->
						<div class="grid grid-cols-3 gap-2 mt-4">
							<div class="text-center">
								<div
									class="text-[10px] uppercase tracking-widest font-bold text-gray-400"
								>
									Total Spent
								</div>
								<div class="font-mono text-sm font-bold text-[#D4AF37]">
									{{ formatCurrency(profile.total_spent) }}
								</div>
							</div>
							<div class="text-center">
								<div
									class="text-[10px] uppercase tracking-widest font-bold text-gray-400"
								>
									Visits
								</div>
								<div class="font-mono text-sm font-bold text-[#D4AF37]">
									{{ profile.visit_count }}
								</div>
							</div>
							<div class="text-center">
								<div
									class="text-[10px] uppercase tracking-widest font-bold text-gray-400"
								>
									Avg Order
								</div>
								<div class="font-mono text-sm font-bold text-[#D4AF37]">
									{{ formatCurrency(profile.avg_order_value) }}
								</div>
							</div>
						</div>

						<!-- Dormant Badge -->
						<div
							v-if="
								profile.days_since_last_visit && profile.days_since_last_visit > 90
							"
							class="mt-3 px-3 py-1.5 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 text-center"
						>
							<span
								class="text-[10px] font-bold text-red-500 dark:text-red-400 uppercase tracking-wider"
							>
								Haven't visited in {{ profile.days_since_last_visit }} days
							</span>
						</div>
					</div>

					<!-- Occasion Alert -->
					<div
						v-if="upcomingOccasions.length > 0"
						class="mx-4 mt-3 p-3 rounded-xl bg-gradient-to-r from-[#D4AF37]/10 to-[#F2E6A0]/10 border border-[#D4AF37]/30"
					>
						<div
							v-for="occ in upcomingOccasions"
							:key="occ.type"
							class="flex items-center gap-2"
						>
							<span class="text-base">{{
								occ.type === 'birthday' ? '🎂' : '💍'
							}}</span>
							<span class="text-xs font-bold text-[#D4AF37]">{{ occ.label }}</span>
						</div>
					</div>

					<!-- Tab Bar -->
					<div
						class="flex border-b border-[#E8E0D4] dark:border-warm-border/30 px-4 mt-3 shrink-0"
					>
						<button
							v-for="tab in tabs"
							:key="tab.key"
							@click="activeTab = tab.key"
							class="px-4 py-2.5 text-xs transition-colors relative"
							:class="
								activeTab === tab.key
									? 'text-[#D4AF37] font-bold border-b-2 border-[#D4AF37]'
									: 'text-gray-400 font-medium hover:text-gray-600 dark:hover:text-gray-300'
							"
						>
							{{ tab.label }}
						</button>
					</div>

					<!-- Tab Content -->
					<div class="flex-1 overflow-y-auto p-4 space-y-2">
						<!-- History Tab -->
						<div v-if="activeTab === 'history'">
							<div
								v-for="purchase in recentPurchases"
								:key="purchase.invoice"
								class="p-3 rounded-xl bg-white dark:bg-warm-dark-800 border border-[#EFEAE2] dark:border-warm-border/20 mb-2"
							>
								<div class="flex items-center justify-between mb-1.5">
									<span class="text-[10px] text-gray-400 font-mono">{{
										purchase.date
									}}</span>
									<span class="font-mono text-xs font-black text-[#D4AF37]">{{
										formatCurrency(purchase.grand_total)
									}}</span>
								</div>
								<div
									v-for="(item, idx) in purchase.items"
									:key="idx"
									class="text-xs font-semibold text-gray-900 dark:text-white truncate"
								>
									{{ item.qty }}x {{ item.item_name }}
								</div>
							</div>
							<div
								v-if="recentPurchases.length === 0"
								class="text-center py-8 text-gray-300 dark:text-gray-600 italic text-xs"
							>
								No purchase history yet
							</div>
						</div>

						<!-- Sizes Tab -->
						<div v-if="activeTab === 'sizes'">
							<div class="grid grid-cols-2 gap-3">
								<div v-for="field in sizeFields" :key="field.key">
									<div
										class="text-[10px] uppercase tracking-widest font-bold text-gray-400"
									>
										{{ field.label }}
									</div>
									<div
										v-if="profile[field.key]"
										class="text-sm font-bold text-gray-900 dark:text-white mt-0.5"
									>
										{{ profile[field.key] }}
									</div>
									<div
										v-else
										class="text-gray-300 dark:text-gray-600 italic text-xs mt-0.5"
									>
										Not set
									</div>
								</div>
							</div>
						</div>

						<!-- Notes Tab -->
						<div v-if="activeTab === 'notes'">
							<div class="mb-4">
								<textarea
									v-model="newNote"
									rows="3"
									placeholder="Add a note about this customer..."
									class="w-full px-3 py-2 bg-white dark:bg-warm-dark-800 border border-[#E8E0D4] dark:border-warm-border/40 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 resize-none"
								></textarea>
								<button
									@click="submitNote"
									:disabled="savingNote || !newNote.trim()"
									class="mt-2 px-4 py-2 bg-[#D4AF37] text-black font-bold text-xs rounded-lg hover:bg-[#b5952f] disabled:opacity-50 transition"
								>
									{{ savingNote ? 'Saving...' : 'Add Note' }}
								</button>
							</div>
							<div
								v-if="notes"
								class="p-3 rounded-xl bg-white dark:bg-warm-dark-800 border border-[#EFEAE2] dark:border-warm-border/20 whitespace-pre-wrap text-xs text-gray-700 dark:text-gray-300 leading-relaxed"
							>
								{{ notes }}
							</div>
							<div
								v-else
								class="text-center py-6 text-gray-300 dark:text-gray-600 italic text-xs"
							>
								No notes yet
							</div>
						</div>

						<!-- CRM Tab -->
						<div v-if="activeTab === 'crm'">
							<!-- Create Lead Button (when no lead exists) -->
							<div v-if="!hasCRMLead" class="mb-4">
								<button
									@click="handleCreateLead"
									:disabled="creatingLead"
									class="w-full px-4 py-2.5 bg-[#D4AF37] text-black font-bold text-xs rounded-lg hover:bg-[#b5952f] disabled:opacity-50 transition flex items-center justify-center gap-2"
								>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
									{{ creatingLead ? 'Creating...' : 'Create CRM Lead' }}
								</button>
								<p class="text-[10px] text-gray-400 mt-1.5 text-center">Capture this customer in the CRM pipeline</p>
							</div>

							<!-- Lead Card -->
							<div v-if="pipeline?.lead" class="mb-3 p-3 rounded-xl bg-white dark:bg-warm-dark-800 border border-[#EFEAE2] dark:border-warm-border/20">
								<div class="flex items-center justify-between mb-1.5">
									<span class="text-[10px] font-bold uppercase tracking-wider text-gray-400">CRM Lead</span>
									<span
										class="px-2 py-0.5 rounded-full text-[10px] font-bold"
										:class="{
											'bg-blue-100 text-blue-700': pipeline.lead.status === 'Open',
											'bg-amber-100 text-amber-700': pipeline.lead.status === 'Contacted',
											'bg-green-100 text-green-700': pipeline.lead.status === 'Qualified',
											'bg-teal-100 text-teal-700': pipeline.lead.status === 'Converted',
											'bg-gray-100 text-gray-600': !['Open','Contacted','Qualified','Converted'].includes(pipeline.lead.status),
										}"
									>{{ pipeline.lead.status }}</span>
								</div>
								<p class="text-xs text-gray-600 dark:text-gray-300">{{ pipeline.lead.name }}</p>
								<div class="flex gap-3 mt-1.5 text-[10px] text-gray-400">
									<span v-if="pipeline.lead.source">Source: {{ pipeline.lead.source }}</span>
									<span v-if="pipeline.lead.lead_owner">Owner: {{ pipeline.lead.lead_owner }}</span>
								</div>
							</div>

							<!-- Deal Card -->
							<div v-if="pipeline?.deal" class="mb-3 p-3 rounded-xl bg-white dark:bg-warm-dark-800 border border-[#EFEAE2] dark:border-warm-border/20">
								<div class="flex items-center justify-between mb-1.5">
									<span class="text-[10px] font-bold uppercase tracking-wider text-gray-400">CRM Deal</span>
									<span
										class="px-2 py-0.5 rounded-full text-[10px] font-bold"
										:class="{
											'bg-blue-100 text-blue-700': pipeline.deal.status === 'Qualification',
											'bg-amber-100 text-amber-700': pipeline.deal.status === 'Proposal',
											'bg-orange-100 text-orange-700': pipeline.deal.status === 'Negotiation',
											'bg-green-100 text-green-700': pipeline.deal.status === 'Won',
											'bg-red-100 text-red-700': pipeline.deal.status === 'Lost',
											'bg-gray-100 text-gray-600': !['Qualification','Proposal','Negotiation','Won','Lost'].includes(pipeline.deal.status),
										}"
									>{{ pipeline.deal.status }}</span>
								</div>
								<p class="text-xs text-gray-600 dark:text-gray-300">{{ pipeline.deal.name }}</p>
								<div class="grid grid-cols-2 gap-2 mt-2">
									<div class="text-center p-1.5 rounded-lg bg-gray-50 dark:bg-warm-dark-700">
										<p class="text-[10px] text-gray-400">Value</p>
										<p class="text-xs font-bold text-gray-700 dark:text-gray-200">{{ formatCurrency(pipeline.deal.deal_value) }}</p>
									</div>
									<div class="text-center p-1.5 rounded-lg bg-gray-50 dark:bg-warm-dark-700">
										<p class="text-[10px] text-gray-400">Probability</p>
										<p class="text-xs font-bold text-gray-700 dark:text-gray-200">{{ pipeline.deal.probability }}%</p>
									</div>
								</div>
								<div v-if="pipeline.deal.next_step" class="mt-2 text-[10px] text-gray-500">
									Next: {{ pipeline.deal.next_step }}
								</div>
								<div v-if="pipeline.deal.expected_closure_date" class="text-[10px] text-gray-400">
									Expected close: {{ pipeline.deal.expected_closure_date }}
								</div>
							</div>

							<!-- Open Tasks -->
							<div class="mt-3">
								<div class="flex items-center justify-between mb-2">
									<span class="text-[10px] font-bold uppercase tracking-wider text-gray-400">Tasks</span>
									<button
										@click="showTaskForm = !showTaskForm"
										class="text-[10px] text-[#D4AF37] font-medium hover:underline"
									>
										{{ showTaskForm ? 'Cancel' : '+ Add Task' }}
									</button>
								</div>

								<!-- Task Creation Form -->
								<div v-if="showTaskForm" class="mb-3 p-3 rounded-xl bg-white dark:bg-warm-dark-800 border border-[#D4AF37]/30">
									<input
										v-model="newTaskTitle"
										type="text"
										placeholder="Task title..."
										class="w-full px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-700 border border-[#E8E0D4] dark:border-warm-border/40 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-[#D4AF37]/50 mb-2"
									/>
									<input
										v-model="newTaskDueDate"
										type="date"
										class="w-full px-3 py-1.5 bg-gray-50 dark:bg-warm-dark-700 border border-[#E8E0D4] dark:border-warm-border/40 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-[#D4AF37]/50 mb-2"
									/>
									<button
										@click="handleCreateTask"
										:disabled="creatingTask || !newTaskTitle.trim()"
										class="w-full px-3 py-1.5 bg-[#D4AF37] text-black font-bold text-[10px] rounded-lg hover:bg-[#b5952f] disabled:opacity-50 transition"
									>
										{{ creatingTask ? 'Creating...' : 'Create Task' }}
									</button>
								</div>

								<!-- Task List -->
								<div v-if="openTasks.length" class="space-y-2">
									<div
										v-for="task in openTasks"
										:key="task.name"
										class="p-2.5 rounded-lg bg-white dark:bg-warm-dark-800 border border-[#EFEAE2] dark:border-warm-border/20"
									>
										<div class="flex items-center justify-between">
											<span class="text-xs font-medium text-gray-700 dark:text-gray-200">{{ task.title }}</span>
											<span
												class="px-1.5 py-0.5 rounded text-[9px] font-bold"
												:class="{
													'bg-red-100 text-red-700': task.priority === 'High',
													'bg-amber-100 text-amber-700': task.priority === 'Medium',
													'bg-gray-100 text-gray-500': task.priority === 'Low',
												}"
											>{{ task.priority }}</span>
										</div>
										<div class="flex gap-2 mt-1 text-[10px] text-gray-400">
											<span v-if="task.due_date">Due: {{ task.due_date }}</span>
											<span>{{ task.status }}</span>
										</div>
									</div>
								</div>
								<div v-else-if="!showTaskForm" class="text-center py-4 text-gray-300 dark:text-gray-600 italic text-xs">
									No open tasks
								</div>
							</div>
						</div>
					</div>
				</template>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useClienteling } from '@/composables/useClienteling.js'

const props = defineProps({
	show: { type: Boolean, default: false },
	customerName: { type: String, default: '' },
})
const emit = defineEmits(['close'])

const {
	customerData,
	loading,
	error,
	loadIntelligence,
	addNote,
	createTask,
	createLead,
	upcomingOccasions,
	hasUrgentOccasion,
	profile,
	recentPurchases,
	pipeline,
	hasCRMLead,
	hasCRMDeal,
	openTasks,
} = useClienteling()

const activeTab = ref('history')
const newNote = ref('')
const savingNote = ref(false)
const creatingLead = ref(false)
const showTaskForm = ref(false)
const newTaskTitle = ref('')
const newTaskDueDate = ref('')
const creatingTask = ref(false)

const tabs = [
	{ key: 'history', label: 'History' },
	{ key: 'sizes', label: 'Sizes' },
	{ key: 'crm', label: 'CRM' },
	{ key: 'notes', label: 'Notes' },
]

const sizeFields = [
	{ key: 'ring_size', label: 'Ring Size' },
	{ key: 'ring_left_size', label: 'Ring Left' },
	{ key: 'ring_right_size', label: 'Ring Right' },
	{ key: 'wrist_size', label: 'Wrist' },
	{ key: 'neck_size', label: 'Neck' },
	{ key: 'preferred_metal', label: 'Preferred Metal' },
	{ key: 'preferred_purity', label: 'Preferred Purity' },
]

const notes = computed(() => customerData.value?.notes || '')

watch(
	() => props.customerName,
	(name) => {
		if (name && props.show) {
			loadIntelligence(name)
		}
	},
	{ immediate: true }
)

watch(
	() => props.show,
	(open) => {
		if (open && props.customerName) {
			loadIntelligence(props.customerName)
		}
		if (!open) {
			activeTab.value = 'history'
			newNote.value = ''
		}
	}
)

async function submitNote() {
	if (!newNote.value.trim() || !props.customerName) return
	savingNote.value = true
	try {
		await addNote(props.customerName, newNote.value)
		newNote.value = ''
	} catch (e) {
		// error is logged in composable
	} finally {
		savingNote.value = false
	}
}

function reload() {
	if (props.customerName) {
		loadIntelligence(props.customerName)
	}
}

function getInitial(name) {
	if (!name) return '?'
	return name
		.split(' ')
		.map((n) => n[0])
		.join('')
		.substring(0, 2)
		.toUpperCase()
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

async function handleCreateLead() {
	if (!props.customerName) return
	creatingLead.value = true
	try {
		await createLead(props.customerName)
	} catch (e) {
		console.error('Create lead failed:', e)
	} finally {
		creatingLead.value = false
	}
}

async function handleCreateTask() {
	if (!props.customerName || !newTaskTitle.value.trim()) return
	creatingTask.value = true
	try {
		await createTask(props.customerName, newTaskTitle.value, newTaskDueDate.value || null)
		newTaskTitle.value = ''
		newTaskDueDate.value = ''
		showTaskForm.value = false
	} catch (e) {
		console.error('Create task failed:', e)
	} finally {
		creatingTask.value = false
	}
}
</script>
