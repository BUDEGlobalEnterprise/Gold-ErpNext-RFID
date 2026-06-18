<template>
	<div class="customer-selector" data-testid="customer-selector">
		<!-- Selected Customer Display -->
		<div
			v-if="customer && !showSearch"
			class="flex items-center justify-between p-2.5 bg-gray-50/50 dark:bg-warm-dark-700/30 border border-gray-100 dark:border-warm-border/20 rounded-xl"
		>
			<div class="flex items-center gap-2.5 flex-1 min-w-0">
				<div
					class="w-8 h-8 rounded-full bg-[#D4AF37]/15 flex items-center justify-center text-[#D4AF37] flex-shrink-0"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
						></path>
					</svg>
				</div>
				<div class="min-w-0 flex-1 cursor-pointer" @click="$emit('open-profile')">
					<div class="font-bold text-gray-900 dark:text-white text-xs truncate">
						{{ customer.display_name || customer.customer_name || customer.name }}
						<span
							v-if="
								customer.name &&
								customer.name !== (customer.display_name || customer.customer_name)
							"
							class="text-[10px] text-gray-400 font-normal ml-1"
							>({{ customer.name }})</span
						>
					</div>
					<div
						v-if="customer.mobile_no || customer.email_id"
						class="text-[10px] text-gray-400 truncate mt-0.5"
					>
						{{ customer.mobile_no || customer.email_id }}
					</div>
				</div>
			</div>
			<div class="flex items-center gap-0.5 flex-shrink-0">
				<button
					v-if="isAdmin && customer.name"
					@click.prevent="openEditCustomer(customer)"
					class="p-1.5 hover:bg-gray-200/50 dark:hover:bg-white/5 rounded-full transition-colors text-gray-400 hover:text-[#D4AF37]"
					title="Edit Customer"
				>
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
				</button>
				<button
					@click.prevent="$emit('open-clienteling')"
					class="p-1.5 hover:bg-[#D4AF37]/10 rounded-full transition-colors text-gray-400 hover:text-[#D4AF37]"
					title="View Client Profile"
				>
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
						/>
					</svg>
				</button>
				<button
					@click="clearAndShowSearch"
					class="p-1.5 hover:bg-gray-200/50 dark:hover:bg-white/5 rounded-full transition-colors text-gray-400 hover:text-red-500"
					title="Change Customer"
				>
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						></path>
					</svg>
				</button>
			</div>
		</div>

		<!-- Search / Create UI -->
		<div v-else class="space-y-3">
			<!-- Search Input -->
			<div class="relative">
				<input
					ref="searchInput"
					v-model="searchQuery"
					type="text"
					:placeholder="placeholder"
					@input="debouncedSearch"
					@focus="showDropdown = true"
					class="w-full px-4 py-3 pl-10 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 focus:border-[#D4AF37]"
					data-testid="customer-search"
				/>
				<svg
					class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
					></path>
				</svg>
				<button
					v-if="searchQuery"
					@click="clearSearch"
					class="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full"
				>
					<svg
						class="w-3 h-3 text-gray-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						></path>
					</svg>
				</button>

				<!-- Search Results Dropdown -->
				<div
					v-if="
						showDropdown && (searchResults.length > 0 || searching || showCreateOption)
					"
					class="absolute z-50 w-full mt-1 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-warm-border rounded-xl shadow-lg max-h-60 overflow-y-auto"
				>
					<!-- Searching indicator -->
					<div
						v-if="searching"
						class="px-4 py-3 text-sm text-gray-500 flex items-center gap-2"
					>
						<svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
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
						Searching...
					</div>

					<!-- Search Results -->
					<button
						v-for="result in searchResults"
						:key="result.customer_name"
						@click="selectCustomer(result)"
						class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700 flex items-center gap-3 border-b border-gray-100 dark:border-warm-border/50 last:border-0"
						data-testid="customer-option"
					>
						<div
							class="w-8 h-8 rounded-full bg-gray-100 dark:bg-warm-dark-900 flex items-center justify-center text-gray-500"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
								></path>
							</svg>
						</div>
						<div class="min-w-0 flex-1">
							<div
								class="font-medium text-gray-900 dark:text-white text-sm truncate"
							>
								{{ result.display_name || result.customer_name }}
								<span
									v-if="result.customer_name !== result.display_name"
									class="text-xs text-gray-500 font-normal ml-1"
									>({{ result.customer_name }})</span
								>
							</div>
							<div class="text-xs text-gray-500 truncate">
								{{
									[result.mobile_no, result.email_id]
										.filter(Boolean)
										.join(' · ') || 'No contact info'
								}}
							</div>
						</div>
					</button>

					<!-- Create New Customer Option -->
					<button
						v-if="showCreateOption"
						@click="openCreateModal"
						class="w-full px-4 py-3 text-left hover:bg-[#D4AF37]/10 flex items-center gap-3 border-t-2 border-gray-100 dark:border-warm-border"
					>
						<div
							class="w-8 h-8 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37]"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 6v6m0 0v6m0-6h6m-6 0H6"
								></path>
							</svg>
						</div>
						<div class="text-sm">
							<span class="font-medium text-[#D4AF37]">Create new customer</span>
							<span v-if="searchQuery" class="text-gray-500"
								>: "{{ searchQuery }}"</span
							>
						</div>
					</button>
				</div>
			</div>

			<!-- Click outside to close dropdown -->
			<div
				v-if="showDropdown"
				@click="showDropdown = false"
				class="fixed inset-0 z-40"
			></div>

			<!-- Quick Add Button (when no search query) -->
			<button
				v-if="!searchQuery && showQuickAdd"
				@click="showCreateModalFlag = true"
				class="w-full py-2 text-sm font-medium text-[#D4AF37] border border-dashed border-[#D4AF37]/40 rounded-lg hover:bg-[#D4AF37]/10 transition flex items-center justify-center gap-2"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6v6m0 0v6m0-6h6m-6 0H6"
					></path>
				</svg>
				Add New Customer
			</button>
		</div>

		<!-- Create Customer Modal (Standardized) -->
		<CustomerCreationModal
			v-if="showCreateModalFlag"
			:show="showCreateModalFlag"
			:initial-name="isEditMode ? '' : searchQuery"
			:is-edit="isEditMode"
			:customer-name="editCustomerNameRef"
			@close="handleCancelCreate"
			@created="onCustomerCreatedInSelector"
			@updated="onCustomerUpdatedInSelector"
		/>
	</div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useCartStore } from '@/stores/cart.js'
import { useSessionStore } from '@/stores/session.js'
import CustomerCreationModal from './CustomerCreationModal.vue'

const props = defineProps({
	placeholder: {
		type: String,
		default: 'Search customers by name, phone, or email...',
	},
	showQuickAdd: {
		type: Boolean,
		default: true,
	},
	compact: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(['selected', 'cleared', 'open-clienteling', 'open-profile'])

const cart = useCartStore()
const session = useSessionStore()
const isAdmin = computed(() => session.isAdmin || session.isManager)

// State
const showSearch = ref(!cart.customer)
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const showDropdown = ref(false)
const showCreateModalFlag = ref(false)
const isEditMode = ref(false)
const editCustomerNameRef = ref('')
const searchInput = ref(null)

// Recent Customers
const recentCustomers = ref([])
const recentLimit = ref(10)
const recentLoading = ref(false)

const recentCustomersResource = createResource({
	url: 'zevar_core.api.customer.get_recent_customers',
	auto: false,
})

async function loadRecentCustomers() {
	recentLoading.value = true
	try {
		const result = await recentCustomersResource.submit({
			limit: recentLimit.value,
		})
		recentCustomers.value = result || []
	} catch (e) {
		console.error('Failed to load recent customers:', e)
		recentCustomers.value = []
	} finally {
		recentLoading.value = false
	}
}

async function loadMoreRecent() {
	recentLimit.value += 10
	await loadRecentCustomers()
}

function getInitials(name) {
	if (!name) return '?'
	return name
		.split(' ')
		.map((n) => n[0])
		.join('')
		.substring(0, 2)
		.toUpperCase()
}

onMounted(() => {
	loadRecentCustomers()
})

function openCreateModal() {
	isEditMode.value = false
	editCustomerNameRef.value = ''
	showCreateModalFlag.value = true
	showDropdown.value = false
}

function openEditCustomer(customerData) {
	isEditMode.value = true
	editCustomerNameRef.value = customerData.name || customerData.customer_name
	showCreateModalFlag.value = true
}

function handleCancelCreate() {
	showCreateModalFlag.value = false
	isEditMode.value = false
	editCustomerNameRef.value = ''
}

function onCustomerCreatedInSelector(customerData) {
	cart.setCustomer(customerData)
	showCreateModalFlag.value = false
	isEditMode.value = false
	editCustomerNameRef.value = ''
	showSearch.value = false
	searchQuery.value = ''
	emit('selected', cart.customer)
}

function onCustomerUpdatedInSelector(customerData) {
	showCreateModalFlag.value = false
	isEditMode.value = false
	editCustomerNameRef.value = ''
	if (customerData) {
		const updatedId = customerData.name || customerData.customer_name
		if (
			cart.customer &&
			updatedId &&
			(cart.customer.name === updatedId || cart.customer.customer_name === updatedId)
		) {
			cart.setCustomer({ ...cart.customer, ...customerData })
		}
		if (updatedId) {
			const idx = recentCustomers.value.findIndex(
				(c) => c.name === updatedId || c.customer_name === updatedId
			)
			if (idx !== -1) {
				recentCustomers.value[idx] = { ...recentCustomers.value[idx], ...customerData }
			}
		}
	}
	loadRecentCustomers()
}

const customer = computed(() => cart.customer)

const showCreateOption = computed(() => {
	return searchQuery.value.length >= 2 && !searching.value
})

let searchTimeout = null
function debouncedSearch() {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(() => {
		performSearch()
	}, 300)
}

const customerSearchResource = createResource({
	url: 'zevar_core.api.customer.search_customers',
	auto: false,
})

async function performSearch() {
	if (!searchQuery.value || searchQuery.value.length < 2) {
		searchResults.value = []
		return
	}

	searching.value = true
	showDropdown.value = true

	try {
		const results = await customerSearchResource.submit({
			query: searchQuery.value,
		})
		const list = results || []
		searchResults.value = list.map((c) => ({
			...c,
			name: c.name || c.customer_name,
			customer_name: c.display_name || c.customer_name,
		}))
	} catch (e) {
		console.error('Customer search failed:', e)
		searchResults.value = []
	} finally {
		searching.value = false
	}
}

const customerDetailsResource = createResource({
	url: 'zevar_core.api.customer.get_customer_details',
	auto: false,
})

async function selectCustomer(customerData) {
	try {
		const r = await customerDetailsResource.submit({
			customer_name: customerData.customer_name || customerData.name,
		})
		const fullData = r?.data || r
		if (fullData && fullData.customer_name && !fullData.name) {
			fullData.name = fullData.customer_name
		}
		if (fullData) {
			cart.setCustomer(fullData)
		} else {
			cart.setCustomer(customerData)
		}
	} catch (e) {
		const basicData = { ...customerData }
		if (basicData.customer_name && !basicData.name) {
			basicData.name = basicData.customer_name
		}
		cart.setCustomer(basicData)
	}

	showSearch.value = false
	showDropdown.value = false
	searchQuery.value = ''
	searchResults.value = []
	emit('selected', cart.customer)
}

function clearAndShowSearch() {
	cart.clearCustomer()
	showSearch.value = true
	emit('cleared')
	nextTick(() => {
		searchInput.value?.focus()
	})
}

function clearSearch() {
	searchQuery.value = ''
	searchResults.value = []
	searchInput.value?.focus()
}

watch(
	() => cart.customer,
	(newVal) => {
		if (newVal) {
			showSearch.value = false
		}
	}
)

defineExpose({
	showSearch,
	focusSearch: () => searchInput.value?.focus(),
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
