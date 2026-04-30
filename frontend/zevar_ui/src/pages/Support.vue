<template>
	<AppLayout>
		<div class="flex flex-col max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
			<!-- Header -->
			<div class="mb-6 flex items-center justify-between">
				<div>
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white">
						Support Center
					</h2>
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
						Create and manage support tickets
					</p>
				</div>
			</div>

			<!-- Content -->
			<div class="flex flex-col md:flex-row gap-6 h-[calc(100vh-200px)]">
				<!-- Left: New Ticket Form -->
				<div
					class="w-full md:w-1/2 bg-white dark:bg-warm-card rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-warm-border/50 overflow-y-auto custom-scrollbar"
				>
					<h3
						class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-6"
					>
						New Ticket
					</h3>

					<form @submit.prevent="submitTicket" class="space-y-5">
						<!-- Category -->
						<div>
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Category</label
							>
							<select
								v-model="form.category"
								required
								:disabled="submitting"
								@change="onCategoryChange"
								class="w-full px-3 py-2.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
							>
								<option value="" disabled>Select category...</option>
								<option
									v-for="cat in categories"
									:key="cat.value"
									:value="cat.value"
								>
									{{ cat.label }}
								</option>
							</select>
						</div>

						<!-- Sub-Category -->
						<div v-if="form.category && subCategories.length > 0">
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Sub-Category</label
							>
							<select
								v-model="form.sub_category"
								:disabled="submitting"
								class="w-full px-3 py-2.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
							>
								<option value="">Select sub-category...</option>
								<option
									v-for="sub in subCategories"
									:key="sub.value"
									:value="sub.value"
								>
									{{ sub.label }}
								</option>
							</select>
						</div>

						<!-- Priority -->
						<div>
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Priority</label
							>
							<div class="grid grid-cols-4 gap-2">
								<button
									v-for="p in priorities"
									:key="p.value"
									type="button"
									@click="form.priority = p.value"
									:disabled="submitting"
									class="px-3 py-2 rounded-lg text-xs font-bold border transition"
									:class="
										form.priority === p.value
											? 'border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]'
											: 'border-gray-200 dark:border-warm-border text-gray-600 dark:text-gray-400 hover:border-gray-300'
									"
								>
									{{ p.label }}
								</button>
							</div>
						</div>

						<!-- Responsible Department -->
						<div>
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
							>
								Responsible Department
								<span class="text-gray-400 font-normal ml-1">(auto-assigned)</span>
							</label>
							<select
								v-model="form.department"
								:disabled="submitting"
								class="w-full px-3 py-2.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
							>
								<option value="">Select department...</option>
								<option
									v-for="dept in departments"
									:key="dept.value"
									:value="dept.value"
								>
									{{ dept.label }}
								</option>
							</select>
						</div>

						<!-- Reference (Customer/Vendor/Employee) - shown based on category -->
						<div v-if="form.category && referenceType">
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
							>
								{{ referenceLabel }}
							</label>
							<div class="relative">
								<input
									v-model="referenceSearch"
									type="text"
									:placeholder="`Search ${referenceLabel.toLowerCase()}...`"
									:disabled="submitting"
									@input="searchReference"
									@focus="showReferenceDropdown = true"
									class="w-full px-3 py-2.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
								/>
								<!-- Dropdown -->
								<div
									v-if="showReferenceDropdown && referenceResults.length > 0"
									class="absolute z-10 w-full mt-1 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg shadow-lg max-h-48 overflow-y-auto"
								>
									<button
										v-for="item in referenceResults"
										:key="item.value"
										type="button"
										@click="selectReference(item)"
										class="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-warm-dark-800 transition"
									>
										<span class="font-medium text-gray-900 dark:text-white">{{
											item.label
										}}</span>
										<span
											v-if="item.detail"
											class="text-gray-500 text-xs ml-2"
											>{{ item.detail }}</span
										>
									</button>
								</div>
							</div>
							<p
								v-if="form.reference_name"
								class="mt-1 text-xs text-green-600 dark:text-green-400"
							>
								Selected: {{ form.reference_name }}
							</p>
						</div>

						<!-- Subject -->
						<div>
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Subject</label
							>
							<input
								v-model="form.subject"
								type="text"
								required
								placeholder="Brief summary of the issue..."
								:disabled="submitting"
								class="w-full px-3 py-2.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
							/>
						</div>

						<!-- Description -->
						<div>
							<label
								class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
								>Description</label
							>
							<textarea
								v-model="form.description"
								required
								rows="4"
								placeholder="Provide detailed description of the issue..."
								:disabled="submitting"
								class="w-full px-3 py-2.5 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400 resize-none"
							></textarea>
						</div>

						<!-- Submit Button -->
						<button
							type="submit"
							:disabled="
								submitting || !form.subject || !form.description || !form.category
							"
							class="w-full py-3 bg-[#D4AF37] text-black rounded-lg font-bold hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
						>
							<svg
								v-if="submitting"
								class="w-4 h-4 animate-spin"
								fill="none"
								viewBox="0 0 24 24"
							>
								<circle
									class="opacity-25"
									cx="12"
									cy="12"
									r="10"
									stroke="currentColor"
									stroke-width="4"
								></circle>
								<path
									class="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
								></path>
							</svg>
							{{ submitting ? 'Submitting...' : 'Submit Ticket' }}
						</button>
					</form>

					<!-- Success Message -->
					<div
						v-if="successMessage"
						class="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/30 rounded-xl"
					>
						<div class="flex items-center gap-3">
							<div
								class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center"
							>
								<svg
									class="w-5 h-5 text-green-600 dark:text-green-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M5 13l4 4L19 7"
									/>
								</svg>
							</div>
							<div>
								<p class="font-bold text-green-800 dark:text-green-300 text-sm">
									Ticket Created!
								</p>
								<p class="text-xs text-green-600 dark:text-green-400">
									{{ successMessage }}
								</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Right: My Tickets -->
				<div
					class="w-full md:w-1/2 bg-gray-50 dark:bg-warm-card/50 rounded-2xl p-6 border border-gray-100 dark:border-warm-border/50 overflow-y-auto custom-scrollbar"
				>
					<div class="flex items-center justify-between mb-6">
						<h3
							class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
						>
							My Tickets
						</h3>
						<button
							@click="fetchTickets"
							:disabled="loadingTickets"
							class="text-xs text-[#D4AF37] hover:underline font-medium"
						>
							{{ loadingTickets ? 'Refreshing...' : 'Refresh' }}
						</button>
					</div>

					<!-- Loading -->
					<div v-if="loadingTickets" class="py-12 text-center">
						<div
							class="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
						></div>
						<span class="text-gray-500 dark:text-gray-400 text-sm"
							>Loading tickets...</span
						>
					</div>

					<!-- Empty State -->
					<div
						v-else-if="tickets.length === 0"
						class="py-12 text-center relative max-w-sm mx-auto"
					>
						<div
							class="w-20 h-20 bg-gray-100 dark:bg-warm-dark-900 rounded-full flex items-center justify-center mx-auto mb-4"
						>
							<svg
								class="w-10 h-10 text-gray-400"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
								/>
							</svg>
						</div>
						<p class="text-gray-900 dark:text-white font-medium mb-1">
							No Support Tickets
						</p>
						<span class="text-gray-500 dark:text-gray-400 text-sm"
							>Your active and past support requests will appear here.</span
						>
					</div>

					<!-- Tickets List -->
					<div v-else class="space-y-4">
						<div
							v-for="ticket in tickets"
							:key="ticket.name"
							class="bg-white dark:bg-warm-dark-900 rounded-xl p-5 border border-gray-100 dark:border-warm-border/50 hover:border-[#D4AF37]/50 hover:shadow-md transition cursor-pointer"
							@click="viewTicket(ticket.name)"
						>
							<div class="flex items-start justify-between mb-3">
								<span class="font-mono text-sm font-semibold text-[#D4AF37]">{{
									ticket.name
								}}</span>
								<span
									class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold"
									:class="getStatusClass(ticket.status)"
								>
									{{ ticket.status }}
								</span>
							</div>
							<p
								class="text-sm font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2"
							>
								{{ ticket.subject }}
							</p>
							<div
								class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 pt-3 border-t border-gray-100 dark:border-warm-border/50"
							>
								<span class="flex items-center gap-1.5 font-medium">
									<svg
										class="w-4 h-4"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="1.5"
											d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
										/>
									</svg>
									{{ ticket.issue_type || ticket.category || 'General' }}
								</span>
								<span class="flex items-center gap-1.5 font-medium">
									<svg
										class="w-4 h-4"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="1.5"
											d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
									{{ formatDate(ticket.creation) }}
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
import { ref, watch, onMounted, computed, onUnmounted } from 'vue'
import { createResource } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
	import { formatDate } from '@/utils/dates.js'

// State
const submitting = ref(false)
const loadingTickets = ref(false)
const successMessage = ref('')
const tickets = ref([])
const showReferenceDropdown = ref(false)
const referenceSearch = ref('')
const referenceResults = ref([])

// Business-specific categories
const categories = [
	{
		value: 'Customer Issue',
		label: 'Customer Issue',
		department: 'Customer Service',
		referenceType: 'Customer',
	},
	{
		value: 'Jewelry Issue',
		label: 'Jewelry Issue',
		department: 'Quality Control',
		referenceType: 'Item',
	},
	{
		value: 'Vendor Issue',
		label: 'Vendor Issue',
		department: 'Procurement',
		referenceType: 'Supplier',
	},
	{
		value: 'Employee Issue',
		label: 'Employee Issue',
		department: 'Human Resources',
		referenceType: 'Employee',
	},
	{ value: 'Store Issue', label: 'Store Issue', department: 'Operations', referenceType: null },
	{ value: 'Technical', label: 'Technical / IT', department: 'IT Support', referenceType: null },
	{ value: 'Other', label: 'Other', department: 'General', referenceType: null },
]

// Sub-categories based on category
const subCategoryMap = {
	'Customer Issue': [
		{ value: 'Return Request', label: 'Return Request' },
		{ value: 'Exchange Request', label: 'Exchange Request' },
		{ value: 'Complaint', label: 'Complaint' },
		{ value: 'Billing Dispute', label: 'Billing Dispute' },
		{ value: 'Layaway Issue', label: 'Layaway Issue' },
		{ value: 'Gift Card Issue', label: 'Gift Card Issue' },
	],
	'Jewelry Issue': [
		{ value: 'Quality Defect', label: 'Quality Defect' },
		{ value: 'Sizing Issue', label: 'Sizing Issue' },
		{ value: 'Damage', label: 'Damage' },
		{ value: 'Missing Stones', label: 'Missing Stones' },
		{ value: 'Hallmark Issue', label: 'Hallmark Issue' },
	],
	'Vendor Issue': [
		{ value: 'Late Delivery', label: 'Late Delivery' },
		{ value: 'Quality Problem', label: 'Quality Problem' },
		{ value: 'Wrong Item', label: 'Wrong Item' },
		{ value: 'Pricing Dispute', label: 'Pricing Dispute' },
	],
	'Employee Issue': [
		{ value: 'Attendance', label: 'Attendance' },
		{ value: 'Payroll', label: 'Payroll' },
		{ value: 'Leave', label: 'Leave' },
		{ value: 'Manager', label: 'Manager' },
	],
	'Store Issue': [
		{ value: 'Equipment', label: 'Equipment' },
		{ value: 'Security', label: 'Security' },
		{ value: 'Inventory', label: 'Inventory' },
		{ value: 'POS System', label: 'POS System' },
	],
}

const departments = [
	{ value: 'Customer Service', label: 'Customer Service' },
	{ value: 'Quality Control', label: 'Quality Control' },
	{ value: 'Procurement', label: 'Procurement' },
	{ value: 'Human Resources', label: 'Human Resources' },
	{ value: 'Operations', label: 'Operations' },
	{ value: 'IT Support', label: 'IT Support' },
	{ value: 'Sales', label: 'Sales' },
	{ value: 'Finance', label: 'Finance' },
	{ value: 'General', label: 'General' },
]

const priorities = [
	{ value: 'Low', label: 'Low' },
	{ value: 'Medium', label: 'Medium' },
	{ value: 'High', label: 'High' },
	{ value: 'Urgent', label: 'Urgent' },
]

const form = ref({
	category: '',
	sub_category: '',
	priority: 'Medium',
	department: '',
	subject: '',
	description: '',
	reference_type: '',
	reference_name: '',
})

// Computed
const subCategories = computed(() => {
	return subCategoryMap[form.value.category] || []
})

const referenceType = computed(() => {
	const cat = categories.find((c) => c.value === form.value.category)
	return cat?.referenceType || null
})

const referenceLabel = computed(() => {
	const labels = {
		Customer: 'Customer',
		Supplier: 'Vendor',
		Employee: 'Employee',
		Item: 'Item',
	}
	return labels[referenceType.value] || 'Reference'
})

// Resources
const createTicketResource = createResource({
	url: 'zevar_core.api.helpdesk.create_support_ticket',
	auto: false,
})

const getTicketsResource = createResource({
	url: 'zevar_core.api.helpdesk.get_employee_tickets',
	auto: false,
})

const searchResource = createResource({
	url: 'frappe.client.get_list',
	auto: false,
})

// Methods
function onCategoryChange() {
	form.value.sub_category = ''
	form.value.reference_name = ''
	referenceSearch.value = ''

	const cat = categories.find((c) => c.value === form.value.category)
	if (cat) {
		form.value.department = cat.department
		form.value.reference_type = cat.referenceType || ''
	}
}

async function searchReference() {
	if (!referenceType.value || !referenceSearch.value || referenceSearch.value.length < 2) {
		referenceResults.value = []
		return
	}

	const doctypeMap = {
		Customer: { doctype: 'Customer', labelField: 'customer_name', detailField: 'mobile_no' },
		Supplier: { doctype: 'Supplier', labelField: 'supplier_name', detailField: null },
		Employee: { doctype: 'Employee', labelField: 'employee_name', detailField: 'designation' },
		Item: { doctype: 'Item', labelField: 'item_name', detailField: 'item_code' },
	}

	const config = doctypeMap[referenceType.value]
	if (!config) return

	try {
		const result = await searchResource.submit({
			doctype: config.doctype,
			fields: ['name', config.labelField, config.detailField].filter(Boolean),
			filters: {
				[config.labelField]: ['like', `%${referenceSearch.value}%`],
			},
			limit_page_length: 10,
		})

		referenceResults.value = (result || []).map((item) => ({
			value: item.name,
			label: item[config.labelField],
			detail: config.detailField ? item[config.detailField] : null,
		}))
	} catch (error) {
		console.error('Search failed:', error)
		referenceResults.value = []
	}
}

function selectReference(item) {
	form.value.reference_name = item.value
	referenceSearch.value = item.label
	showReferenceDropdown.value = false
}

async function submitTicket() {
	submitting.value = true
	successMessage.value = ''

	try {
		const result = await createTicketResource.submit({
			category: form.value.category,
			sub_category: form.value.sub_category,
			subject: form.value.subject,
			description: form.value.description,
			priority: form.value.priority,
			department: form.value.department,
			reference_type: form.value.reference_type,
			reference_name: form.value.reference_name,
		})

		if (result?.ticket_id) {
			successMessage.value = `Ticket ${result.ticket_id} created successfully`
			form.value = {
				category: '',
				sub_category: '',
				priority: 'Medium',
				department: '',
				subject: '',
				description: '',
				reference_type: '',
				reference_name: '',
			}
			referenceSearch.value = ''
			fetchTickets()
		}
	} catch (error) {
		console.error('Failed to create ticket:', error)
	} finally {
		submitting.value = false
	}
}

async function fetchTickets() {
	loadingTickets.value = true
	try {
		const result = await getTicketsResource.submit({ limit: 50 })
		tickets.value = result.tickets || result || []
	} catch (error) {
		console.error('Failed to fetch tickets:', error)
	} finally {
		loadingTickets.value = false
	}
}

function viewTicket(ticketId) {
	const ticket = tickets.value.find((t) => t.name === ticketId)
	const route =
		ticket?.source === 'helpdesk'
			? '/app/hd-ticket/' + ticketId
			: '/app/support-ticket/' + ticketId
	window.open(route, '_blank')
}

function getStatusClass(status) {
	const classes = {
		Open: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
		'In Progress': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
		Resolved: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Closed: 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400',
		Replied: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400'
}

let clickListener = null

onMounted(() => {
	fetchTickets()

	clickListener = (e) => {
		if (!e.target.closest('.relative')) {
			showReferenceDropdown.value = false
		}
	}
	document.addEventListener('click', clickListener)
})

onUnmounted(() => {
	if (clickListener) {
		document.removeEventListener('click', clickListener)
	}
})
</script>
