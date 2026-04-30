<template>
	<BaseModal :show="true" max-width="max-w-3xl" @close="$emit('close')">
		<template #header>
			<div class="flex items-center justify-between w-full">
				<h3 class="text-lg font-bold text-gray-900 dark:text-white">
					New Repair Order
				</h3>
				<button
						type="button"
						@click="showRepairTypeManager = true"
						class="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
					>
						Manage Repair Types
					</button>
			</div>
		</template>

		<div class="p-6">
			<form @submit.prevent="submit" class="space-y-4">
				<!-- Customer Section -->
				<div class="bg-gray-50 dark:bg-warm-dark-900 rounded-lg p-4">
					<div class="flex items-center justify-between mb-2">
						<label class="block text-sm font-medium">Customer *</label>
						<button
							type="button"
							@click="showNewCustomerModal = true"
							class="text-xs px-2 py-1 bg-[#D4AF37] text-black rounded hover:bg-[#c9a432] flex items-center gap-1"
						>
							<svg
								class="w-3 h-3"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 4v16m8-8H4"
								/>
							</svg>
							New Customer
						</button>
					</div>
					<div class="relative">
						<input
							v-model="customerSearch"
							type="text"
							placeholder="Search customer by name or phone..."
							@input="searchCustomers"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
						<div
							v-if="customerResults.length > 0"
							class="absolute z-10 w-full mt-1 bg-white dark:bg-warm-dark-900 border rounded-lg shadow-lg max-h-48 overflow-y-auto"
						>
							<button
								v-for="c in customerResults"
								:key="c.name"
								type="button"
								@click="selectCustomer(c)"
								class="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-warm-dark-800 border-b last:border-0 flex justify-between"
							>
								<span>{{ c.customer_name }}</span>
								<span class="text-gray-400 text-xs">{{
									c.mobile_no || c.phone || ''
								}}</span>
							</button>
						</div>
					</div>
					<p
						v-if="form.customer"
						class="mt-2 text-xs text-green-600 flex items-center gap-2"
					>
						<span>Selected: {{ form.customer_name }}</span>
						<button
							v-if="customerRepairHistory.length > 0"
							type="button"
							@click="showHistory = !showHistory"
							class="text-blue-600 hover:underline"
						>
							{{ showHistory ? 'Hide' : 'View' }} History ({{
								customerRepairHistory.length
							}})
						</button>
					</p>

					<!-- Customer Repair History -->
					<div
						v-if="showHistory && customerRepairHistory.length > 0"
						class="mt-3 p-2 bg-white dark:bg-warm-dark-900 rounded text-xs"
					>
						<p class="font-medium text-gray-700 mb-2">Previous Repairs</p>
						<div class="space-y-1 max-h-24 overflow-y-auto">
							<div
								v-for="h in customerRepairHistory"
								:key="h.name"
								class="flex justify-between text-gray-600"
							>
								<span>{{ h.repair_type_name }}</span>
								<span>{{ formatDate(h.creation) }} - {{ h.status }}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Customer Phone -->
				<div>
					<label class="block text-sm font-medium mb-1">Customer Phone</label>
					<input
						v-model="form.customer_phone"
						type="tel"
						placeholder="(555) 123-4567"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>

				<!-- Repair Type with Categories -->
				<div>
					<label class="block text-sm font-medium mb-1">Repair Type *</label>
					<div class="flex gap-2 mb-2">
						<select
							v-model="selectedCategory"
							@change="filterRepairTypes"
							class="px-3 py-1 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option value="">All Categories</option>
							<option
								v-for="cat in repairCategories"
								:key="cat"
								:value="cat"
							>
								{{ cat }}
							</option>
						</select>
						<input
							v-model="repairTypeSearch"
							@input="filterRepairTypes"
							type="text"
							placeholder="Search repair types..."
							class="flex-1 px-3 py-1 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<select
						v-model="form.repair_type"
						required
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm max-h-40"
					>
						<option value="">Select...</option>
						<optgroup
							v-for="(types, category) in groupedRepairTypes"
							:key="category"
							:label="category"
						>
							<option v-for="rt in types" :key="rt.name" :value="rt.name">
								{{ rt.repair_name || rt.name }} - ${{ rt.base_price || 0 }}
							</option>
						</optgroup>
					</select>
					<div
						v-if="selectedRepairType"
						class="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs"
					>
						<div class="flex justify-between">
							<span class="text-gray-600">Base Price:</span>
							<span class="font-medium"
								>${{ selectedRepairType.base_price || 0 }}</span
							>
						</div>
						<div
							v-if="selectedRepairType.estimated_days"
							class="flex justify-between"
						>
							<span class="text-gray-600">Est. Days:</span>
							<span class="font-medium"
								>{{ selectedRepairType.estimated_days }} days</span
							>
						</div>
						<p
							v-if="selectedRepairType.description"
							class="mt-1 text-gray-500"
						>
							{{ selectedRepairType.description }}
						</p>
					</div>
				</div>

				<!-- Quick Notes Templates -->
				<div v-if="form.repair_type">
					<label class="block text-sm font-medium mb-1">Quick Notes</label>
					<div class="flex flex-wrap gap-1 mb-2">
						<button
							v-for="(template, idx) in noteTemplates"
							:key="idx"
							type="button"
							@click="addNoteTemplate(template)"
							class="px-2 py-1 text-xs bg-gray-100 dark:bg-warm-dark-900 rounded hover:bg-gray-200"
						>
							{{ template.label }}
						</button>
					</div>
				</div>

				<!-- Item Details Grid -->
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-sm font-medium mb-1">Item Type</label>
						<select
							v-model="form.item_type"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option value="">Select...</option>
							<option>Ring</option>
							<option>Necklace</option>
							<option>Bracelet</option>
							<option>Earring</option>
							<option>Watch</option>
							<option>Chain</option>
							<option>Pendant</option>
							<option>Brooch</option>
							<option>Other</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium mb-1">Priority</label>
						<select
							v-model="form.priority"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option value="Low">Low</option>
							<option value="Medium" selected>Medium</option>
							<option value="High">High</option>
							<option value="Urgent">Urgent</option>
						</select>
					</div>
				</div>

				<!-- Brand & Serial Number -->
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-sm font-medium mb-1">Brand</label>
						<input
							v-model="form.item_brand"
							type="text"
							placeholder="e.g., Rolex, Tiffany"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-sm font-medium mb-1">Serial Number</label>
						<input
							v-model="form.serial_number"
							type="text"
							placeholder="For watches, etc."
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
				</div>

				<!-- Description -->
				<div>
					<label class="block text-sm font-medium mb-1">Item Description</label>
					<textarea
						v-model="form.item_description"
						rows="2"
						placeholder="Describe the item and repair needed..."
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none"
					></textarea>
				</div>

				<!-- Weight & Stones -->
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-sm font-medium mb-1"
							>Item Weight (g)</label
						>
						<input
							v-model.number="form.item_weight"
							type="number"
							step="0.01"
							placeholder="0.00"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
					<div>
						<label class="block text-sm font-medium mb-1"
							>Stone Weight (ct)</label
						>
						<input
							v-model.number="form.stone_weight"
							type="number"
							step="0.01"
							placeholder="0.00"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						/>
					</div>
				</div>

				<!-- Item Condition -->
				<div>
					<label class="block text-sm font-medium mb-1"
						>Item Condition (at intake)</label
					>
					<textarea
						v-model="form.item_condition"
						rows="1"
						placeholder="Scratches, worn prongs, loose stones, etc."
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none"
					></textarea>
				</div>

				<!-- Metal Type & Purity -->
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-sm font-medium mb-1">Metal Type</label>
						<select
							v-model="form.metal_type"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option value="">None</option>
							<option v-for="m in metals" :key="m.name" :value="m.name">
								{{ m.name }}
							</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium mb-1">Purity</label>
						<select
							v-model="form.purity"
							class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
						>
							<option value="">Select...</option>
							<option>10K</option>
							<option>14K</option>
							<option>18K</option>
							<option>22K</option>
							<option>24K</option>
							<option>925</option>
							<option>950</option>
							<option>999</option>
						</select>
					</div>
				</div>

				<!-- Gemstones Section -->
				<div
					class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-100 dark:border-purple-800/30"
				>
					<div class="flex items-center justify-between mb-2">
						<h4 class="text-sm font-bold text-purple-700 dark:text-purple-400">
							Gemstones
						</h4>
						<button
							type="button"
							@click="addGemstone"
							class="text-xs px-2 py-1 bg-purple-500 text-white rounded hover:bg-purple-600"
						>
							+ Add Stone
						</button>
					</div>
					<div
						v-if="form.gemstones.length === 0"
						class="text-xs text-purple-600 dark:text-purple-400 text-center py-2"
					>
						No gemstones added
					</div>
					<div v-else class="space-y-2 max-h-40 overflow-y-auto">
						<div
							v-for="(stone, idx) in form.gemstones"
							:key="idx"
							class="bg-white dark:bg-warm-dark-900 rounded p-2 text-xs"
						>
							<div class="grid grid-cols-3 gap-2">
								<select
									v-model="stone.type"
									class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
								>
									<option value="">Type</option>
									<option>Diamond</option>
									<option>Ruby</option>
									<option>Sapphire</option>
									<option>Emerald</option>
									<option>Pearl</option>
									<option>Other</option>
								</select>
								<input
									v-model.number="stone.count"
									type="number"
									min="1"
									placeholder="Qty"
									class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
								/>
								<input
									v-model.number="stone.carat_weight"
									type="number"
									step="0.01"
									placeholder="Carat"
									class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
								/>
							</div>
							<div class="grid grid-cols-3 gap-2 mt-1">
								<select
									v-model="stone.color"
									class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
								>
									<option value="">Color</option>
									<option>D</option>
									<option>E</option>
									<option>F</option>
									<option>G</option>
									<option>H</option>
									<option>I</option>
									<option>J</option>
									<option>K+</option>
								</select>
								<select
									v-model="stone.clarity"
									class="px-2 py-1 border rounded bg-white dark:bg-warm-dark-900"
								>
									<option value="">Clarity</option>
									<option>FL</option>
									<option>IF</option>
									<option>VVS1</option>
									<option>VVS2</option>
									<option>VS1</option>
									<option>VS2</option>
									<option>SI1</option>
									<option>SI2</option>
								</select>
								<button
									type="button"
									@click="removeGemstone(idx)"
									class="text-red-500 hover:text-red-700"
								>
									Remove
								</button>
							</div>
						</div>
					</div>
				</div>

				<!-- Compliance Section -->
				<div
					class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3 border border-orange-100 dark:border-orange-800/30"
				>
					<h4
						class="text-sm font-bold text-orange-700 dark:text-orange-400 mb-2"
					>
						Customer ID Verification (JVC Compliance)
					</h4>
					<div class="grid grid-cols-2 gap-2">
						<select
							v-model="form.customer_id_type"
							class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
						>
							<option value="">ID Type</option>
							<option>Driver's License</option>
							<option>State ID</option>
							<option>Passport</option>
							<option>Other</option>
						</select>
						<input
							v-model="form.customer_id_number"
							type="text"
							placeholder="ID Number"
							class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
						/>
					</div>
					<input
						v-model="form.customer_id_state"
						type="text"
						placeholder="Issuing State (if applicable)"
						class="mt-2 px-2 py-1 border rounded text-sm w-full bg-white dark:bg-warm-dark-900"
					/>
				</div>

				<!-- Warranty Repair Link -->
				<div
					class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-100 dark:border-green-800/30"
				>
					<label class="flex items-center gap-2">
						<input
							v-model="form.is_warranty_repair"
							type="checkbox"
							class="rounded"
						/>
						<span
							class="text-sm font-medium text-green-800 dark:text-green-400"
							>Warranty Repair</span
						>
					</label>
					<div v-if="form.is_warranty_repair" class="mt-2">
						<input
							v-model="form.original_repair_order"
							type="text"
							placeholder="Original Repair # (e.g., RPR-2026-001)"
							class="w-full px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
						/>
						<select
							v-model="form.warranty_claim_type"
							class="mt-2 w-full px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
						>
							<option value="">Claim Type</option>
							<option>Full Warranty</option>
							<option>Partial</option>
							<option>Not Covered</option>
						</select>
					</div>
				</div>

				<!-- Promised Date -->
				<div>
					<label class="block text-sm font-medium mb-1">Promised Date</label>
					<input
						v-model="form.promised_date"
						type="date"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>

				<!-- Estimated Cost -->
				<div>
					<label class="block text-sm font-medium mb-1"
						>Estimated Cost ($)</label
					>
					<input
						v-model.number="form.estimated_cost"
						type="number"
						step="0.01"
						min="0"
						placeholder="0.00"
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-warm-dark-900 text-sm"
					/>
				</div>

				<!-- Deposit Collection -->
				<div
					class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-100 dark:border-blue-800/30"
				>
					<label class="flex items-center gap-2">
						<input
							v-model="form.collect_deposit"
							type="checkbox"
							class="rounded"
						/>
						<span class="text-sm font-medium text-blue-800 dark:text-blue-400"
							>Collect Deposit Now</span
						>
					</label>
					<div v-if="form.collect_deposit" class="mt-2 grid grid-cols-2 gap-2">
						<input
							v-model.number="form.deposit_amount"
							type="number"
							step="0.01"
							placeholder="Deposit amount"
							class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
						/>
						<select
							v-model="form.deposit_method"
							class="px-2 py-1 border rounded text-sm bg-white dark:bg-warm-dark-900"
						>
							<option value="Cash">Cash</option>
							<option value="Credit Card">Credit Card</option>
							<option value="Check">Check</option>
						</select>
					</div>
				</div>


			</form>
		</div>

		<template #footer>
			<div v-if="errorMsg" class="w-full mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-lg text-sm text-red-700 dark:text-red-400">
				{{ errorMsg }}
			</div>
			<div class="flex gap-3 w-full">
				<button
					type="button"
					@click="$emit('close')"
					class="flex-1 py-2.5 border rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800"
				>
					Cancel
				</button>
				<button
					type="button"
					:disabled="submitting"
					@click="submit"
					class="flex-1 py-2.5 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] disabled:opacity-50 flex items-center justify-center gap-2"
				>
					<svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					{{ submitting ? 'Creating...' : 'Create Repair Order' }}
				</button>
			</div>
		</template>
	</BaseModal>

	<!-- New Customer Modal -->
	<CustomerCreationModal
		v-if="showNewCustomerModal"
		@close="showNewCustomerModal = false"
		@created="onCustomerCreated"
	/>

	<!-- Repair Type Manager Modal -->
	<RepairTypeManager
		v-if="showRepairTypeManager"
		@close="showRepairTypeManager = false"
		@created="onRepairTypeCreated"
	/>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { call, toast, createResource } from 'frappe-ui'
	import { formatDate } from '@/utils/dates.js'
import { useSessionStore } from '@/stores/session.js'
import BaseModal from './BaseModal.vue'
import CustomerCreationModal from './CustomerCreationModal.vue'
import RepairTypeManager from './RepairTypeManager.vue'

const emit = defineEmits(['close', 'created'])
const session = useSessionStore()

const form = ref({
	customer: '',
	customer_name: '',
	customer_phone: '',
	repair_type: '',
	item_type: '',
	item_brand: '',
	serial_number: '',
	item_description: '',
	item_condition: '',
	item_weight: null,
	stone_weight: null,
	metal_type: '',
	purity: '',
	metal_weight_in: null,
	metal_weight_out: null,
	gemstones: [],
	customer_id_type: '',
	customer_id_number: '',
	customer_id_state: '',
	is_warranty_repair: false,
	original_repair_order: '',
	warranty_claim_type: '',
	estimated_cost: null,
	priority: 'Medium',
	promised_date: '',
	collect_deposit: false,
	deposit_amount: null,
	deposit_method: 'Cash',
})

const customerSearch = ref('')
const customerResults = ref([])
const repairTypes = ref([])
const allRepairTypes = ref([])
const metals = ref([])
const submitting = ref(false)
const showNewCustomerModal = ref(false)
const showRepairTypeManager = ref(false)
const showHistory = ref(false)
const customerRepairHistory = ref([])
const selectedCategory = ref('')
const repairTypeSearch = ref('')

const noteTemplates = [
	{ label: 'Stone Loose', text: 'Stone is loose, needs tightening' },
	{ label: 'Prong Worn', text: 'Prongs are worn, need retipping' },
	{ label: 'Clasp Broken', text: 'Clasp is broken, needs replacement' },
	{ label: 'Chain Broken', text: 'Chain is broken, needs soldering' },
	{ label: 'Sizing Down', text: 'Ring needs to be sized down' },
	{ label: 'Sizing Up', text: 'Ring needs to be sized up' },
	{ label: 'Cleaning', text: 'Professional cleaning needed' },
	{ label: 'Rhodium Plating', text: 'Rhodium plating for white gold' },
	{ label: 'Stone Missing', text: 'Stone is missing, needs replacement' },
	{ label: 'Engravement', text: 'Engravement needed' },
]

const repairTypesResource = createResource({
	url: 'zevar_core.api.get_repair_types',
	onSuccess: (data) => {
		allRepairTypes.value = data || []
		repairTypes.value = data || []
	},
})

const metalsResource = createResource({
	url: 'frappe.client.get_list',
	makeParams: () => ({
		doctype: 'Zevar Metal',
		fields: ['name'],
		limit_page_length: 100,
	}),
	onSuccess: (data) => {
		metals.value = data || []
	},
})

// Computed: Repair categories
const repairCategories = computed(() => {
	const cats = new Set(allRepairTypes.value.map((rt) => rt.category).filter(Boolean))
	return Array.from(cats).sort()
})

// Computed: Grouped repair types
const groupedRepairTypes = computed(() => {
	const groups = {}
	const filtered =
		selectedCategory.value || repairTypeSearch.value
			? repairTypes.value.filter((rt) => {
					const matchCategory =
						!selectedCategory.value || rt.category === selectedCategory.value
					const matchSearch =
						!repairTypeSearch.value ||
						(rt.repair_name || rt.name || '')
							.toLowerCase()
							.includes(repairTypeSearch.value.toLowerCase()) ||
						(rt.description || '')
							.toLowerCase()
							.includes(repairTypeSearch.value.toLowerCase())
					return matchCategory && matchSearch
			  })
			: repairTypes.value

	filtered.forEach((rt) => {
		const cat = rt.category || 'General'
		if (!groups[cat]) groups[cat] = []
		groups[cat].push(rt)
	})
	return groups
})

// Computed: Selected repair type details
const selectedRepairType = computed(() => {
	if (!form.value.repair_type) return null
	return allRepairTypes.value.find((rt) => rt.name === form.value.repair_type)
})

let searchTimer
function searchCustomers() {
	clearTimeout(searchTimer)
	if (!customerSearch.value || customerSearch.value.length < 2) {
		customerResults.value = []
		return
	}
	searchTimer = setTimeout(async () => {
		try {
			const results = await call('zevar_core.api.customer.search_customers', {
				query: customerSearch.value,
			})
			const list = results || []
			customerResults.value = list.map(c => ({
				...c,
				name: c.name || c.customer_name,
				customer_name: c.display_name || c.customer_name,
			}))
		} catch (e) {
			console.error('Customer search failed:', e)
			customerResults.value = []
		}
	}, 300)
}

async function selectCustomer(customer) {
	form.value.customer = customer.name
	form.value.customer_name = customer.customer_name
	form.value.customer_phone = customer.mobile_no || customer.phone || customer.mobile || ''
	customerSearch.value = customer.customer_name
	customerResults.value = []
	// Load customer repair history
	loadCustomerHistory(customer.name)
}

async function loadCustomerHistory(customer) {
	try {
		const history = await call('zevar_core.api.get_customer_repair_history', {
			customer,
			limit: 5,
		})
		customerRepairHistory.value = history || []
	} catch (e) {
		console.error('Failed to load customer history:', e)
	}
}

function filterRepairTypes() {
	// Handled by computed property
}

function addNoteTemplate(template) {
	const currentDesc = form.value.item_description || ''
	form.value.item_description = currentDesc ? `${currentDesc}. ${template.text}` : template.text
}

function addGemstone() {
	form.value.gemstones.push({
		type: '',
		count: 1,
		carat_weight: null,
		color: '',
		clarity: '',
		setting_type: '',
		is_treated: false,
	})
}

function removeGemstone(idx) {
	form.value.gemstones.splice(idx, 1)
}

function onCustomerCreated(customer) {
	selectCustomer(customer)
	showNewCustomerModal.value = false
	toast({
		title: 'Customer Selected',
		message: `${customer.customer_name} selected`,
		icon: 'check',
		intent: 'success',
	})
}

function onRepairTypeCreated() {
	showRepairTypeManager.value = false
	repairTypesResource.fetch()
}

async function submit() {
	if (!form.value.customer) {
		toast({
			title: 'Missing Information',
			message: 'Please select a customer',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	if (!form.value.repair_type) {
		toast({
			title: 'Missing Information',
			message: 'Please select a repair type',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}

	submitting.value = true
	try {
		const payload = {
			customer: form.value.customer,
			repair_type: form.value.repair_type,
			item_description: form.value.item_description || undefined,
			customer_phone: form.value.customer_phone || undefined,
			estimated_cost: form.value.estimated_cost || undefined,
			priority: form.value.priority,
			item_type: form.value.item_type || undefined,
			item_brand: form.value.item_brand || undefined,
			serial_number: form.value.serial_number || undefined,
			item_condition: form.value.item_condition || undefined,
			item_weight: form.value.item_weight || undefined,
			stone_weight: form.value.stone_weight || undefined,
			metal_type: form.value.metal_type || undefined,
			purity: form.value.purity || undefined,
			metal_weight_in: form.value.metal_weight_in || undefined,
			metal_weight_out: form.value.metal_weight_out || undefined,
			gemstones_json: form.value.gemstones.length > 0 ? JSON.stringify(form.value.gemstones) : undefined,
			customer_id_type: form.value.customer_id_type || undefined,
			customer_id_number: form.value.customer_id_number || undefined,
			customer_id_state: form.value.customer_id_state || undefined,
			is_warranty_repair: form.value.is_warranty_repair ? 1 : undefined,
			original_repair_order: form.value.original_repair_order || undefined,
			warranty_claim_type: form.value.warranty_claim_type || undefined,
			promised_date: form.value.promised_date || undefined,
			warehouse: session.currentWarehouse || undefined,
			handled_by: session.user?.email || undefined,
		}

		// Remove undefined values to avoid sending them as 'undefined' strings
		Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key])

		await call('zevar_core.api.create_repair_order', payload)

		// If deposit was collected, record payment
		if (form.value.collect_deposit && form.value.deposit_amount) {
			// Payment would be recorded separately after order creation
		}

		emit('created')
		toast({
			title: 'Success',
			message: 'Repair order created successfully',
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message,
			icon: 'alert-triangle',
			intent: 'error',
		})
	} finally {
		submitting.value = false
	}
}

onMounted(() => {
	repairTypesResource.fetch()
	metalsResource.fetch()
})
</script>
