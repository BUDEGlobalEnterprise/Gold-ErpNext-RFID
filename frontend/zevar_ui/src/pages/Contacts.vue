<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Contacts</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ pagination.total_count }} Vendors
					</span>
				</div>

				<div class="flex items-center gap-2">
					<ViewToggle v-model="viewMode" storage-key="zevar_contacts_view" />
					<div class="relative">
						<svg
							class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
							/>
						</svg>
						<input
							type="text"
							v-model="searchQuery"
							@input="onSearchInput"
							placeholder="Search by name, phone, email..."
							class="pl-9 pr-4 py-2 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent w-64"
						/>
					</div>
				</div>
			</div>

			<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 flex-shrink-0">
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Vendors
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ pagination.total_count }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Supplier Groups
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ supplierGroups.length }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						With Email
					</div>
					<div class="text-2xl font-bold text-green-600">{{ withEmailCount }}</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						With Phone
					</div>
					<div class="text-2xl font-bold text-blue-500">{{ withPhoneCount }}</div>
				</div>
			</div>

			<div
				v-if="viewMode === 'list'"
				class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar"
			>
				<div
					class="bg-white dark:bg-warm-dark-900/50 rounded-xl border border-gray-100 dark:border-warm-border/50 flex flex-col shadow-sm relative min-h-min"
				>
					<div class="overflow-x-auto">
						<table class="w-full text-sm">
							<thead>
								<tr
									class="bg-gray-50 dark:bg-warm-dark-900/90 border-b border-gray-100 dark:border-warm-border/50 sticky top-0 z-10 backdrop-blur-sm"
								>
									<th
										class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider"
									>
										Supplier
									</th>
									<th
										class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider"
									>
										Contact
									</th>
									<th
										class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider"
									>
										Group
									</th>
									<th
										class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell"
									>
										Type
									</th>
									<th
										class="px-4 py-3 text-left text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell"
									>
										Country
									</th>
									<th
										class="px-4 py-3 text-right text-[10px] font-bold text-gray-500 uppercase tracking-wider"
									>
										Actions
									</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-gray-50 dark:divide-gray-700/30">
								<tr v-if="loading">
									<td
										:colspan="6"
										class="px-4 py-12 text-center text-gray-500 dark:text-gray-400"
									>
										<div
											class="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
										></div>
										Loading contacts...
									</td>
								</tr>
								<tr v-else-if="suppliers.length === 0">
									<td
										:colspan="6"
										class="px-4 py-12 text-center text-gray-500 dark:text-gray-400"
									>
										No contacts found.
									</td>
								</tr>
								<tr
									v-for="supplier in suppliers"
									:key="supplier.name"
									class="hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors cursor-pointer"
								>
									<td class="px-4 py-3">
										<div class="flex items-center gap-3">
											<div
												class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] text-[#0F1115]"
											>
												{{
													getInitials(
														supplier.supplier_name || supplier.name
													)
												}}
											</div>
											<div>
												<div
													class="font-bold text-gray-900 dark:text-white"
												>
													{{ supplier.supplier_name || supplier.name }}
												</div>
												<div
													class="text-[10px] text-gray-500 dark:text-gray-400"
												>
													{{ supplier.name }}
												</div>
											</div>
										</div>
									</td>
									<td class="px-4 py-3">
										<div class="text-xs text-gray-700 dark:text-gray-300">
											{{ supplier.mobile_no || 'No Phone' }}
										</div>
										<div class="text-[10px] text-gray-500">
											{{ supplier.email_id || 'No Email' }}
										</div>
									</td>
									<td class="px-4 py-3">
										<span
											class="px-2 py-1 rounded-full text-[10px] font-bold bg-[#D4AF37]/15 text-[#D4AF37]"
										>
											{{ supplier.supplier_group || 'All Groups' }}
										</span>
									</td>
									<td
										class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
									>
										{{ supplier.supplier_type || '-' }}
									</td>
									<td
										class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell"
									>
										{{ supplier.country || '-' }}
									</td>
									<td class="px-4 py-3 text-right">
										<button
											class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700 text-gray-400 hover:text-gray-600 dark:hover:text-white transition"
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
													d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
												/>
											</svg>
										</button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>

					<div
						class="px-4 py-3 border-t border-gray-100 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-700 flex items-center justify-between mt-auto shrink-0 sticky bottom-0 z-10"
					>
						<div class="flex items-center gap-3">
							<div class="text-xs text-gray-500 dark:text-gray-400">
								Showing {{ (pagination.page - 1) * pagination.page_length + 1 }} to
								{{
									Math.min(
										pagination.page * pagination.page_length,
										pagination.total_count
									)
								}}
								of {{ pagination.total_count }} entries
							</div>
							<div
								class="flex items-center gap-2 border-l border-gray-200 dark:border-warm-border pl-3"
							>
								<label class="text-xs text-gray-500 dark:text-gray-400"
									>Per page:</label
								>
								<select
									v-model="pagination.page_length"
									@change="changePageSize"
									class="text-xs bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded p-1 focus:ring-1 focus:ring-[#D4AF37] outline-none"
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
								class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-200 dark:border-warm-border hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 transition"
							>
								Previous
							</button>
							<span class="text-xs font-medium text-gray-700 dark:text-gray-300 px-2"
								>Page {{ pagination.page }}</span
							>
							<button
								@click="nextPage"
								:disabled="
									pagination.page * pagination.page_length >=
										pagination.total_count || loading
								"
								class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-200 dark:border-warm-border hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 transition"
							>
								Next
							</button>
						</div>
					</div>
				</div>

				<div
					v-if="viewMode === 'grid'"
					class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar"
				>
					<!-- Loading state -->
					<div v-if="loading" class="flex items-center justify-center py-20">
						<div class="text-center">
							<div
								class="animate-spin rounded-full h-10 w-10 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-4"
							></div>
							<div class="text-sm text-gray-500 dark:text-gray-400">
								Loading contacts...
							</div>
						</div>
					</div>

					<!-- Empty state -->
					<div
						v-else-if="suppliers.length === 0"
						class="flex items-center justify-center py-20"
					>
						<div class="text-center">
							<div
								class="w-16 h-16 rounded-full bg-gray-100 dark:bg-warm-dark-800 flex items-center justify-center mx-auto mb-4"
							>
								<svg
									class="w-8 h-8 text-gray-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="1.5"
										d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
									/>
								</svg>
							</div>
							<div class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">
								No contacts found
							</div>
							<div class="text-xs text-gray-500 dark:text-gray-400">
								Try adjusting your search or add a new vendor
							</div>
						</div>
					</div>

					<!-- Grid cards -->
					<div
						v-else
						class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 pb-6"
					>
						<div
							v-for="supplier in suppliers"
							:key="supplier.name"
							class="group bg-white dark:bg-warm-dark-800 rounded-2xl border border-gray-100 dark:border-warm-border/50 overflow-hidden hover:border-[#D4AF37]/40 dark:hover:border-[#D4AF37]/30 transition-all duration-200 cursor-pointer hover:shadow-lg hover:shadow-[#D4AF37]/5 dark:hover:shadow-none hover:-translate-y-0.5"
						>
							<!-- Card accent bar -->
							<div
								class="h-1 bg-gradient-to-r from-[#D4AF37] via-[#F2E6A0] to-[#D4AF37] opacity-0 group-hover:opacity-100 transition-opacity duration-200"
							></div>

							<div class="p-4">
								<!-- Header: avatar + name + group badge -->
								<div class="flex items-start gap-3 mb-3">
									<div
										class="w-11 h-11 rounded-xl flex items-center justify-center text-sm font-bold shrink-0 bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] text-[#0F1115] shadow-sm"
									>
										{{ getInitials(supplier.supplier_name || supplier.name) }}
									</div>
									<div class="min-w-0 flex-1">
										<div
											class="font-bold text-gray-900 dark:text-white text-sm truncate leading-tight"
										>
											{{ supplier.supplier_name || supplier.name }}
										</div>
										<div
											class="text-[10px] text-gray-400 dark:text-gray-500 font-mono mt-0.5"
										>
											{{ supplier.name }}
										</div>
									</div>
								</div>

								<!-- Supplier group badge -->
								<div class="mb-3">
									<span
										class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-[#D4AF37]/10 text-[#B8960C] dark:bg-[#D4AF37]/15 dark:text-[#F2E6A0]"
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
												d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5"
											/>
										</svg>
										{{ supplier.supplier_group || 'All Groups' }}
									</span>
								</div>

								<!-- Divider -->
								<div
									class="border-t border-gray-100 dark:border-warm-border/50 mb-3"
								></div>

								<!-- Contact details -->
								<div class="space-y-2">
									<!-- Phone -->
									<div class="flex items-center gap-2 text-xs">
										<div
											class="w-6 h-6 rounded-md bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center shrink-0"
										>
											<svg
												class="w-3.5 h-3.5 text-blue-500"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
												/>
											</svg>
										</div>
										<span class="text-gray-700 dark:text-gray-300 truncate">{{
											supplier.mobile_no || 'No Phone'
										}}</span>
									</div>

									<!-- Email -->
									<div class="flex items-center gap-2 text-xs">
										<div
											class="w-6 h-6 rounded-md bg-green-50 dark:bg-green-900/30 flex items-center justify-center shrink-0"
										>
											<svg
												class="w-3.5 h-3.5 text-green-500"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
												/>
											</svg>
										</div>
										<span class="text-gray-700 dark:text-gray-300 truncate">{{
											supplier.email_id || 'No Email'
										}}</span>
									</div>

									<!-- Supplier type -->
									<div
										v-if="supplier.supplier_type"
										class="flex items-center gap-2 text-xs"
									>
										<div
											class="w-6 h-6 rounded-md bg-purple-50 dark:bg-purple-900/30 flex items-center justify-center shrink-0"
										>
											<svg
												class="w-3.5 h-3.5 text-purple-500"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
												/>
											</svg>
										</div>
										<span class="text-gray-600 dark:text-gray-400">{{
											supplier.supplier_type
										}}</span>
									</div>

									<!-- Country -->
									<div
										v-if="supplier.country"
										class="flex items-center gap-2 text-xs"
									>
										<div
											class="w-6 h-6 rounded-md bg-orange-50 dark:bg-orange-900/30 flex items-center justify-center shrink-0"
										>
											<svg
												class="w-3.5 h-3.5 text-orange-500"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
												/>
											</svg>
										</div>
										<span class="text-gray-600 dark:text-gray-400">{{
											supplier.country
										}}</span>
									</div>
								</div>

								<!-- Quick action (shown on hover) -->
								<div
									class="mt-3 pt-3 border-t border-gray-50 dark:border-warm-border/30 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
								>
									<button
										class="w-full flex items-center justify-center gap-2 py-1.5 rounded-lg text-xs font-bold text-[#D4AF37] hover:bg-[#D4AF37]/10 transition"
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
												d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
											/>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
											/>
										</svg>
										View Details
									</button>
								</div>
							</div>
						</div>
					</div>

					<!-- Grid Pagination -->
					<div
						class="px-4 py-3 border-t border-gray-100 dark:border-warm-border/50 bg-gray-50/50 dark:bg-warm-dark-700/50 flex items-center justify-between mt-auto shrink-0 sticky bottom-0 z-10 backdrop-blur-sm"
					>
						<div class="flex items-center gap-3">
							<div class="text-xs text-gray-500 dark:text-gray-400">
								Showing {{ (pagination.page - 1) * pagination.page_length + 1 }} to
								{{
									Math.min(
										pagination.page * pagination.page_length,
										pagination.total_count
									)
								}}
								of {{ pagination.total_count }}
							</div>
							<div
								class="flex items-center gap-2 border-l border-gray-200 dark:border-warm-border pl-3"
							>
								<label class="text-xs text-gray-500 dark:text-gray-400"
									>Per page:</label
								>
								<select
									v-model="pagination.page_length"
									@change="changePageSize"
									class="text-xs bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded p-1 focus:ring-1 focus:ring-[#D4AF37] outline-none"
								>
									<option :value="20">20</option>
									<option :value="50">50</option>
									<option :value="100">100</option>
								</select>
							</div>
						</div>
						<div class="flex items-center gap-2">
							<button
								@click="prevPage"
								:disabled="pagination.page === 1 || loading"
								class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-200 dark:border-warm-border hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
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
										d="M15 19l-7-7 7-7"
									/>
								</svg>
							</button>
							<span class="text-xs font-medium text-gray-700 dark:text-gray-300 px-2"
								>Page {{ pagination.page }}</span
							>
							<button
								@click="nextPage"
								:disabled="
									pagination.page * pagination.page_length >=
										pagination.total_count || loading
								"
								class="px-3 py-1.5 text-xs font-bold rounded-lg border border-gray-200 dark:border-warm-border hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
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
										d="M9 5l7 7-7 7"
									/>
								</svg>
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
import ViewToggle from '@/components/ViewToggle.vue'
import { ref, watch, onMounted } from 'vue'
import { createResource } from 'frappe-ui'

const STORAGE_KEY = 'zevar_contacts_view'
const storedView = localStorage.getItem(STORAGE_KEY)
const viewMode = ref(storedView === 'grid' ? 'grid' : 'list')

// Watch for view mode changes and persist to localStorage
watch(viewMode, (mode) => {
	localStorage.setItem(STORAGE_KEY, mode)
})

const suppliers = ref([])
const loading = ref(true)
const searchQuery = ref('')
const activeSearch = ref('')
const supplierGroups = ref([])
const withEmailCount = ref(0)
const withPhoneCount = ref(0)

const pagination = ref({
	page: 1,
	page_length: 20,
	total_count: 0,
})

const getListResource = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		const base = {
			doctype: 'Supplier',
			fields: [
				'name',
				'supplier_name',
				'mobile_no',
				'email_id',
				'supplier_group',
				'supplier_type',
				'country',
			],
			limit_start: (pagination.value.page - 1) * pagination.value.page_length,
			limit_page_length: pagination.value.page_length,
			order_by: 'creation desc',
		}
		if (activeSearch.value) {
			base.or_filters = [
				['name', 'like', `%${activeSearch.value}%`],
				['supplier_name', 'like', `%${activeSearch.value}%`],
				['mobile_no', 'like', `%${activeSearch.value}%`],
				['email_id', 'like', `%${activeSearch.value}%`],
			]
		}
		return base
	},
})

const countResource = createResource({
	url: 'frappe.client.get_count',
	makeParams() {
		const params = { doctype: 'Supplier' }
		if (activeSearch.value) {
			params.filters = [['Supplier', 'supplier_name', 'like', `%${activeSearch.value}%`]]
		}
		return params
	},
})

const groupsResource = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'Supplier Group',
			fields: ['name'],
			limit_page_length: 0,
		}
	},
})

const emailCountResource = createResource({
	url: 'frappe.client.get_count',
	makeParams() {
		return {
			doctype: 'Supplier',
			filters: [['email_id', '!=', '']],
		}
	},
})

const phoneCountResource = createResource({
	url: 'frappe.client.get_count',
	makeParams() {
		return {
			doctype: 'Supplier',
			filters: [['mobile_no', '!=', '']],
		}
	},
})

async function fetchSuppliers() {
	loading.value = true
	try {
		const [countResult, listResult, groupsResult, emailResult, phoneResult] =
			await Promise.all([
				countResource.submit(),
				getListResource.submit(),
				groupsResource.submit(),
				emailCountResource.submit(),
				phoneCountResource.submit(),
			])

		pagination.value.total_count = countResult?.message || countResult || 0
		suppliers.value = listResult?.message || listResult || []
		supplierGroups.value = groupsResult?.message || groupsResult || []
		withEmailCount.value = emailResult?.message || emailResult || 0
		withPhoneCount.value = phoneResult?.message || phoneResult || 0
	} catch (err) {
		console.error(err)
	} finally {
		loading.value = false
	}
}

function applySearch() {
	activeSearch.value = searchQuery.value
	pagination.value.page = 1
	fetchSuppliers()
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
	fetchSuppliers()
}

function prevPage() {
	if (pagination.value.page > 1) {
		pagination.value.page--
		fetchSuppliers()
	}
}

function nextPage() {
	if (pagination.value.page * pagination.value.page_length < pagination.value.total_count) {
		pagination.value.page++
		fetchSuppliers()
	}
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
	fetchSuppliers()
})
</script>
