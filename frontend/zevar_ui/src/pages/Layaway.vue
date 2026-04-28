<template>
	<AppLayout @layaway-created="onLayawayCreated">
		<div v-if="!showCreateModal" class="h-full flex flex-col">
			<!-- Page Header -->
			<div class="flex items-center justify-between mb-6">
				<div>
					<h1 class="premium-title !text-2xl">Layaway Management</h1>
					<p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
						Manage layaway contracts and payments
					</p>
				</div>
				<div class="flex items-center gap-4">
					<ViewToggle v-model="viewMode" storage-key="zevar_layaway_view" />
					<button
						@click="showCreateModal = true"
						class="px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition flex items-center gap-2"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4v16m8-8H4"
							/>
						</svg>
						New Layaway
					</button>
				</div>
			</div>

			<!-- Filters Bar -->
			<div
				class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 mb-6 border border-gray-100 dark:border-warm-border/50"
			>
				<div class="flex flex-wrap gap-3 items-end">
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>Status</label
						>
						<select
							v-model="filters.status"
							@change="fetchLayaways"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
						>
							<option value="">All</option>
							<option value="Active">Active</option>
							<option value="Completed">Completed</option>
							<option value="Cancelled">Cancelled</option>
							<option value="Defaulted">Defaulted</option>
						</select>
					</div>
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>Customer</label
						>
						<input
							type="text"
							v-model="filters.customer"
							placeholder="Search customer..."
							@keyup.enter="fetchLayaways"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent w-40"
						/>
					</div>
					<div class="flex flex-col gap-1">
						<label class="text-xs font-medium text-gray-500 dark:text-gray-400"
							>Search</label
						>
						<input
							type="text"
							v-model="filters.search"
							placeholder="Contract #..."
							@keyup.enter="fetchLayaways"
							class="px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent w-36"
						/>
					</div>
					<button
						@click="fetchLayaways"
						:disabled="loading"
						class="px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition disabled:opacity-50"
					>
						Search
					</button>
				</div>
			</div>

			<!-- Summary Cards -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6" v-if="summary">
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
				>
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Active</span
					>
					<p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
						{{ summary.active_count }}
					</p>
				</div>
				<div
					class="bg-gradient-to-br from-[#D4AF37]/20 to-[#D4AF37]/5 rounded-xl p-4 border border-[#D4AF37]/30"
				>
					<span class="text-xs text-[#D4AF37] uppercase tracking-wider font-medium"
						>Total Outstanding</span
					>
					<p class="text-2xl font-bold text-[#D4AF37] mt-1">
						{{ formatCurrency(summary.total_outstanding) }}
					</p>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
				>
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Overdue</span
					>
					<p class="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">
						{{ summary.overdue_count }}
					</p>
				</div>
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl p-4 border border-gray-100 dark:border-warm-border/50"
				>
					<span
						class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium"
						>Completed</span
					>
					<p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
						{{ summary.completed_count }}
					</p>
				</div>
			</div>

			<!-- Layaway Cards Grid -->
			<div class="flex-1 overflow-y-auto">
				<div v-if="loading" class="py-20 text-center">
					<div
						class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-4"
					></div>
					<span class="text-gray-500 dark:text-gray-400 text-sm"
						>Loading layaways...</span
					>
				</div>

				<div v-else-if="layaways.length === 0" class="py-20 text-center">
					<svg
						class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4"
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
					<p class="text-gray-500 dark:text-gray-400 text-sm">
						No layaway contracts found
					</p>
				</div>

				<div v-else v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					<div
						v-for="layaway in layaways"
						:key="layaway.name"
						@click="viewDetails(layaway.name)"
						class="bg-white dark:bg-warm-dark-800 rounded-2xl border border-gray-100 dark:border-warm-border/50 p-4 hover:shadow-md hover:border-gray-300 dark:hover:border-warm-border transition cursor-pointer"
					>
						<!-- Header -->
						<div class="flex items-start justify-between mb-3">
							<div>
								<span class="font-mono text-xs text-[#D4AF37]">{{
									layaway.name
								}}</span>
								<p class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">
									{{ layaway.customer_name || layaway.customer || 'Unknown' }}
								</p>
							</div>
							<span
								class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold"
								:class="getStatusClass(layaway.status, layaway.is_overdue)"
							>
								{{ layaway.is_overdue ? 'Overdue' : layaway.status }}
							</span>
						</div>

						<!-- Amounts -->
						<div class="grid grid-cols-2 gap-3 mb-3">
							<div>
								<span class="text-xs text-gray-500 dark:text-gray-400">Total</span>
								<p class="text-sm font-bold text-gray-900 dark:text-white">
									{{ formatCurrency(layaway.total_amount) }}
								</p>
							</div>
							<div>
								<span class="text-xs text-gray-500 dark:text-gray-400"
									>Balance</span
								>
								<p class="text-sm font-bold text-orange-600 dark:text-orange-400">
									{{ formatCurrency(layaway.balance_amount) }}
								</p>
							</div>
						</div>

						<!-- Progress Bar -->
						<div class="mb-3">
							<div
								class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1"
							>
								<span>Paid</span>
								<span
									>{{
										Math.round(
											(layaway.deposit_amount / layaway.total_amount) * 100
										)
									}}%</span
								>
							</div>
							<div
								class="h-2 bg-gray-200 dark:bg-warm-dark-800 rounded-full overflow-hidden"
							>
								<div
									class="h-full bg-[#D4AF37] transition-all duration-300"
									:style="{
										width: `${
											(layaway.deposit_amount / layaway.total_amount) * 100
										}%`,
									}"
								></div>
							</div>
						</div>

						<!-- Footer -->
						<div
							class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400"
						>
							<span>{{ layaway.item_count || 0 }} items</span>
							<span v-if="layaway.next_payment_date">
								Next: {{ formatDate(layaway.next_payment_date) }}
							</span>
							<span v-else> {{ layaway.maximum_duration_months }} months </span>
						</div>
					</div>
				</div>

				<!-- List View -->
				<div v-if="viewMode === 'list'" class="space-y-2">
					<div
						v-for="layaway in layaways"
						:key="layaway.name"
						@click="viewDetails(layaway.name)"
						class="flex items-center justify-between bg-white dark:bg-warm-dark-900/50 rounded-lg px-4 py-3 border border-gray-100 dark:border-warm-border/50 hover:border-[#D4AF37]/30 transition cursor-pointer"
					>
						<div class="flex items-center gap-4 min-w-0">
							<span class="font-mono text-xs text-[#D4AF37] w-32 shrink-0">{{ layaway.name }}</span>
							<span class="text-sm font-bold text-gray-900 dark:text-white truncate">{{ layaway.customer_name || layaway.customer }}</span>
						</div>
						<div class="flex items-center gap-6">
							<div class="text-right">
								<span class="text-xs text-gray-500">Total</span>
								<span class="text-sm font-bold text-gray-900 dark:text-white ml-2">{{ formatCurrency(layaway.total_amount) }}</span>
							</div>
							<div class="text-right">
								<span class="text-xs text-gray-500">Balance</span>
								<span class="text-sm font-bold text-orange-600 dark:text-orange-400 ml-2">{{ formatCurrency(layaway.balance_amount) }}</span>
							</div>
							<span class="inline-flex px-2.5 py-1 rounded-full text-xs font-bold" :class="getStatusClass(layaway.status, layaway.is_overdue)">
								{{ layaway.is_overdue ? 'Overdue' : layaway.status }}
							</span>
						</div>
					</div>
				</div>

				<!-- Pagination -->
				<div
					v-if="pagination.total_pages > 1"
					class="px-4 py-6 flex items-center justify-center gap-2"
				>
					<button
						@click="goToPage(pagination.page - 1)"
						:disabled="pagination.page === 1"
						class="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 dark:border-warm-border text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
					>
						Previous
					</button>
					<span class="text-sm text-gray-500 dark:text-gray-400">
						Page {{ pagination.page }} of {{ pagination.total_pages }}
					</span>
					<button
						@click="goToPage(pagination.page + 1)"
						:disabled="pagination.page === pagination.total_pages"
						class="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-200 dark:border-warm-border text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
					>
						Next
					</button>
				</div>
			</div>
		</div>

		<!-- Create Layaway Inline View -->
		<div v-else class="h-full flex flex-col p-2">
			<div class="mb-4">
				<button @click="closeCreateMode" class="text-sm font-medium text-gray-500 hover:text-gray-900 dark:hover:text-white transition flex items-center gap-1">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
					Back to Layaways
				</button>
			</div>
			<div class="flex-1 overflow-hidden rounded-2xl border border-gray-100 dark:border-warm-border shadow-sm">
				<CreateLayawayModal
				:show="showCreateModal"
				inlineMode
				@close="closeCreateMode"
				@created="onLayawayCreated"
				@proceedToPayment="onProceedToPayment"
			/>
			</div>
		</div>

		<!-- Layaway Detail Modal -->
		<!-- Layaway Detail Modal -->
		<LayawayDetailModal
			:show="showDetailModal"
			:layawayId="selectedLayaway"
			@close="showDetailModal = false"
			@refresh="fetchLayaways"
		/>

		<!-- Layaway Success Confirmation Overlay -->
		<Teleport to="body">
			<Transition name="fade">
				<div v-if="showSuccessConfirmation" class="fixed inset-0 z-[120] flex items-center justify-center p-4">
					<div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="dismissSuccess"></div>
					<div class="relative bg-white dark:bg-warm-card rounded-2xl shadow-2xl max-w-md w-full p-10 flex flex-col items-center text-center border border-transparent dark:border-warm-border animate-bounce-in">
						<div class="w-20 h-20 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-6">
							<svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path>
							</svg>
						</div>
						<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Layaway Created!</h2>
						<p class="text-gray-500 dark:text-gray-400 mb-6">Contract has been created and deposit payment recorded successfully.</p>

						<div class="bg-gray-50 dark:bg-warm-dark-700 rounded-xl p-4 w-full mb-6 border border-gray-100 dark:border-warm-border/50 space-y-2">
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">Contract ID</span>
								<span class="font-mono font-bold text-gray-900 dark:text-white">{{ successData?.layaway_id || '—' }}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">Deposit Paid</span>
								<span class="font-mono font-bold text-[#D4AF37]">{{ formatCurrency(successData?.deposit_amount) }}</span>
							</div>
							<div class="flex justify-between text-sm">
								<span class="text-gray-500 dark:text-gray-400">Status</span>
								<span class="font-bold text-green-600 dark:text-green-400">{{ successData?.status || 'Active' }}</span>
							</div>
						</div>

						<div class="flex gap-3 w-full">
							<button
								@click="viewCreatedLayaway"
								class="flex-1 py-3 rounded-xl font-bold text-sm bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30 hover:bg-[#D4AF37]/20 transition"
							>
								View Details
							</button>
							<button
								@click="dismissSuccess"
								class="flex-1 py-3 rounded-xl font-bold text-sm bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black hover:bg-gray-800 dark:hover:bg-[#b5952f] transition"
							>
								Done
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import { useUIStore } from '@/stores/ui.js'
import { useCartStore } from '@/stores/cart.js'
import AppLayout from '@/components/AppLayout.vue'
import LayawayDetailModal from '@/components/LayawayDetailModal.vue'
import CreateLayawayModal from '@/components/CreateLayawayModal.vue'
import ViewToggle from '@/components/ViewToggle.vue'
	import { formatDate as formatDateUtil } from '@/utils/dates.js'

// Routing
const route = useRoute()
const router = useRouter()
const ui = useUIStore()
const cart = useCartStore()

// State
const loading = ref(false)
const layaways = ref([])
const showDetailModal = ref(false)
const showSuccessConfirmation = ref(false)
const selectedLayaway = ref(null)
const showCreateModal = ref(false)
const successData = ref(null)
const pagination = ref({ page: 1, total_pages: 1, total_count: 0 })

const viewMode = ref(localStorage.getItem('zevar_layaway_view') || 'grid')

const filters = ref({
	status: '',
	customer: '',
	search: '',
})

// Computed summary
const summary = computed(() => {
	if (!layaways.value.length) return null

	const active = layaways.value.filter((l) => l.status === 'Active')
	const overdue = layaways.value.filter((l) => l.is_overdue)
	const completed = layaways.value.filter((l) => l.status === 'Completed')

	return {
		active_count: active.length,
		overdue_count: overdue.length,
		completed_count: completed.length,
		total_outstanding: active.reduce((sum, l) => sum + (l.balance_amount || 0), 0),
	}
})

// Resources
const layawaysResource = createResource({
	url: 'zevar_core.api.layaway.get_all_layaways',
	auto: false,
})

function unwrapResponse(result) {
	return result?.message ?? result
}

// Methods
function formatCurrency(amount) {
	if (!amount) return '$0.00'
	return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

function formatDate(dateStr) {
	return formatDateUtil(dateStr)
}

function getStatusClass(status, isOverdue) {
	if (isOverdue) {
		return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
	}
	const classes = {
		Active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Completed: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
		Cancelled: 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400',
		Defaulted: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-warm-dark-900 dark:text-gray-400'
}

async function fetchLayaways() {
	loading.value = true
	try {
		const result = unwrapResponse(
			await layawaysResource.submit({
				...filters.value,
				page: pagination.value.page,
				page_size: 20,
			})
		)

		layaways.value = result?.layaways || []
		pagination.value = result?.pagination || pagination.value
	} catch (error) {
		console.error('Failed to fetch layaways:', error)
	} finally {
		loading.value = false
	}
}

function viewDetails(layawayId) {
	selectedLayaway.value = layawayId
	showDetailModal.value = true
}

function goToPage(page) {
	pagination.value.page = page
	fetchLayaways()
}

// Step 1: CreateLayawayModal emits proceedToPayment with the payload
async function onProceedToPayment(payload) {
	// Trigger global payment sidebar with draft payload
	ui.openLayawayPayment(null, payload.deposit_amount || 0, payload)
}

// Step 2: AppLayout emits layaway-created after sidebar payment success
function onLayawayCreated(result) {
	successData.value = result
	selectedLayaway.value = result.layaway_id
	cart.clearCart()
	closeCreateMode()
	fetchLayaways()
	showSuccessConfirmation.value = true
}

function viewCreatedLayaway() {
	showSuccessConfirmation.value = false
	if (successData.value?.layaway_id) {
		selectedLayaway.value = successData.value.layaway_id
		showDetailModal.value = true
	}
	successData.value = null
}

function dismissSuccess() {
	showSuccessConfirmation.value = false
	successData.value = null
}

function closeCreateMode() {
	showCreateModal.value = false
	if (route.query.action === 'new') {
		router.replace({ name: 'Layaway' })
	}
}

// Lifecycle
onMounted(() => {
	fetchLayaways()
	if (route.query.action === 'new') {
		showCreateModal.value = true
	}
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
@keyframes bounce-in {
	0% { transform: scale(0.9); opacity: 0; }
	50% { transform: scale(1.02); }
	100% { transform: scale(1); opacity: 1; }
}
.animate-bounce-in {
	animation: bounce-in 0.4s ease-out;
}
</style>
