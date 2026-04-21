<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<!-- Header -->
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Customers</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-white/5 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-white/10"
					>
						{{ pagination.total_count }} Clients
					</span>
				</div>
				
				<div class="flex items-center gap-2">
					<div class="relative">
						<svg class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
						<input
							type="text"
							v-model="searchQuery"
							@input="onSearchInput"
							placeholder="Search by name, phone, email..."
							class="pl-9 pr-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent w-64"
						/>
					</div>
					<button
						class="px-4 py-2 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black text-xs font-bold rounded-lg hover:bg-gray-800 dark:hover:bg-[#b5952f] transition-all shadow-sm"
					>
						+ New Client
					</button>
				</div>
			</div>

			<!-- Stats Row -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 flex-shrink-0">
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Clients</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">{{ pagination.total_count }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Recent (30 Days)</div>
					<div class="text-2xl font-bold text-[#D4AF37]">{{ recentCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">VIP Members</div>
					<div class="text-2xl font-bold text-green-600">{{ vipCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Repeat Rate</div>
					<div class="text-2xl font-bold text-blue-500">68%</div>
				</div>
			</div>

			<!-- Table View Wrapper with Outside Scrollbar -->
			<div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
				<div class="bg-white dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-700/50 flex flex-col shadow-sm relative min-h-min">
					<div class="overflow-x-auto">
						<table class="w-full text-sm">
							<thead>
								<tr class="bg-gray-50 dark:bg-gray-900/90 border-b border-gray-100 dark:border-gray-700/50 sticky top-0 z-10 backdrop-blur-sm">
								<th class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider">Name</th>
								<th class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider">Contact</th>
								<th class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider">Group</th>
								<th class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell">Joined</th>
								<th class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell">Territory</th>
								<th class="px-4 py-3 text-right text-[10px] font-bold text-gray-500 uppercase tracking-wider">Actions</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-50 dark:divide-gray-700/30">
							<tr v-if="loading">
								<td colspan="6" class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
									<div class="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"></div>
									Loading customers...
								</td>
							</tr>
							<tr v-else-if="customers.length === 0">
								<td colspan="6" class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
									No customers found.
								</td>
							</tr>
							<tr
								v-for="customer in customers"
								:key="customer.name"
								class="hover:bg-gray-50 dark:hover:bg-white/5 transition-colors cursor-pointer"
							>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
											:class="customer.customer_group === 'VIP' ? 'bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] text-[#0F1115]' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300'">
											{{ getInitials(customer.customer_name || customer.name) }}
										</div>
										<div class="font-bold text-gray-900 dark:text-white">
											{{ customer.customer_name || customer.name }}
										</div>
									</div>
								</td>
								<td class="px-4 py-3">
									<div class="text-xs text-gray-700 dark:text-gray-300">{{ customer.mobile_no || 'No Phone' }}</div>
									<div class="text-[10px] text-gray-500">{{ customer.email_id || 'No Email' }}</div>
								</td>
								<td class="px-4 py-3">
									<span class="px-2 py-1 rounded-full text-[10px] font-bold"
										:class="customer.customer_group === 'VIP' ? 'bg-[#D4AF37]/15 text-[#D4AF37]' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'">
										{{ customer.customer_group || 'Standard' }}
									</span>
								</td>
								<td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell">
									{{ formatDate(customer.creation) }}
								</td>
								<td class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell">
									{{ customer.territory || '-' }}
								</td>
								<td class="px-4 py-3 text-right">
									<button class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 text-gray-400 hover:text-gray-600 dark:hover:text-white transition">
										<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
									</button>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Pagination Controls -->
				<div class="px-4 py-3 border-t border-gray-100 dark:border-gray-700/50 bg-gray-50 dark:bg-gray-900/30 flex items-center justify-between mt-auto shrink-0 sticky bottom-0 z-10">
					<div class="flex items-center gap-3">
						<div class="text-xs text-gray-500 dark:text-gray-400">
							Showing {{ (pagination.page - 1) * pagination.page_length + 1 }} to {{ Math.min(pagination.page * pagination.page_length, pagination.total_count) }} of {{ pagination.total_count }} entries
						</div>
						<div class="flex items-center gap-2 border-l border-gray-200 dark:border-gray-700 pl-3">
							<label class="text-xs text-gray-500 dark:text-gray-400">Per page:</label>
							<select 
								v-model="pagination.page_length" 
								@change="changePageSize"
								class="text-xs bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded p-1 focus:ring-1 focus:ring-[#D4AF37] outline-none"
							>
								<option :value="20">20</option>
								<option :value="50">50</option>
								<option :value="100">100</option>
								<option :value="250">250</option>
								<option :value="500">500</option>
							</select>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<button 
							@click="prevPage" 
							:disabled="pagination.page === 1 || loading"
							class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 transition"
						>
							Previous
						</button>
						<span class="text-xs font-medium text-gray-700 dark:text-gray-300 px-2">Page {{ pagination.page }}</span>
						<button 
							@click="nextPage" 
							:disabled="(pagination.page * pagination.page_length) >= pagination.total_count || loading"
							class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 transition"
						>
							Next
						</button>
					</div>
				</div>
			</div>
		</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'

const customers = ref([])
const loading = ref(true)
const searchQuery = ref('')
const activeSearch = ref('')
const recentCount = ref(0)
const vipCount = ref(0)

const pagination = ref({
	page: 1,
	page_length: 20,
	total_count: 0
})

const getListResource = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		const filters = {}
		if (activeSearch.value) {
			return {
				doctype: 'Customer',
				fields: ['name', 'customer_name', 'mobile_no', 'email_id', 'customer_group', 'territory', 'creation'],
				or_filters: [
					['name', 'like', `%${activeSearch.value}%`],
					['customer_name', 'like', `%${activeSearch.value}%`],
					['mobile_no', 'like', `%${activeSearch.value}%`],
					['email_id', 'like', `%${activeSearch.value}%`]
				],
				limit_start: (pagination.value.page - 1) * pagination.value.page_length,
				limit_page_length: pagination.value.page_length,
				order_by: 'creation desc'
			}
		}
		return {
			doctype: 'Customer',
			fields: ['name', 'customer_name', 'mobile_no', 'email_id', 'customer_group', 'territory', 'creation'],
			limit_start: (pagination.value.page - 1) * pagination.value.page_length,
			limit_page_length: pagination.value.page_length,
			order_by: 'creation desc'
		}
	}
})

const countResource = createResource({
	url: 'frappe.client.get_count',
	makeParams() {
		if (activeSearch.value) {
			return {
				doctype: 'Customer',
				filters: [
					['name', 'like', `%${activeSearch.value}%`]
				]
			}
		}
		return {
			doctype: 'Customer'
		}
	}
})

const vipCountResource = createResource({
	url: 'frappe.client.get_count',
	makeParams() {
		return {
			doctype: 'Customer',
			filters: [
				['customer_group', '=', 'VIP']
			]
		}
	}
})

async function fetchCustomers() {
	loading.value = true
	try {
		const [countResult, listResult, vipResult] = await Promise.all([
			countResource.submit(),
			getListResource.submit(),
			vipCountResource.submit()
		])
		
		pagination.value.total_count = countResult?.message || countResult || 0
		customers.value = listResult?.message || listResult || []
		vipCount.value = vipResult?.message || vipResult || 0
	} catch (err) {
		console.error(err)
	} finally {
		loading.value = false
	}
}

function applySearch() {
	activeSearch.value = searchQuery.value
	pagination.value.page = 1
	fetchCustomers()
}

let searchTimeout
function onSearchInput() {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(() => {
		applySearch()
	}, 300)
}

function changePageSize() {
	pagination.value.page = 1
	fetchCustomers()
}

function prevPage() {
	if (pagination.value.page > 1) {
		pagination.value.page--
		fetchCustomers()
	}
}

function nextPage() {
	if ((pagination.value.page * pagination.value.page_length) < pagination.value.total_count) {
		pagination.value.page++
		fetchCustomers()
	}
}

function getInitials(name) {
	if (!name) return '?'
	return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}

function formatDate(dateStr) {
	if (!dateStr) return 'Unknown'
	return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

onMounted(() => {
	fetchCustomers()
})
</script>
