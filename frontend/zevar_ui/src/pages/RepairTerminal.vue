<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div>
					<h2 class="text-2xl font-serif font-bold text-gray-900 dark:text-white">
						Repair Terminal
					</h2>
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
						Manage repair orders and customer repairs
					</p>
				</div>
				<button
					@click="showNewModal = true"
					class="px-4 py-2.5 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition flex items-center gap-2"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 4v16m8-8H4"
						/>
					</svg>
					New Repair
				</button>
			</div>

			<!-- Status Filter Tabs with Count Badges -->
			<div class="flex gap-2 mb-4 overflow-x-auto pb-2">
				<button
					v-for="statusItem in statusTabs"
					:key="statusItem.value"
					@click="selectStatusTab(statusItem.value)"
					class="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition whitespace-nowrap"
					:class="
						statusFilter === statusItem.value
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30'
							: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border border-transparent hover:bg-gray-200 dark:hover:bg-gray-700'
					"
				>
					<span>{{ statusItem.label }}</span>
					<span
						v-if="statusItem.count > 0"
						class="px-1.5 py-0.5 rounded-full text-xs font-bold"
						:class="
							statusFilter === statusItem.value
								? 'bg-[#D4AF37] text-black'
								: 'bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300'
						"
					>
						{{ statusItem.count }}
					</span>
				</button>
			</div>

			<!-- Search Bar with Quick Search -->
			<div class="flex gap-3 mb-4">
				<div class="flex-1 relative">
					<svg
						class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
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
						v-model="searchTerm"
						@input="debouncedLoad"
						placeholder="Search by repair #, customer name, or phone..."
						class="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
					/>
				</div>
				<button
					@click="showAdvancedSearch = !showAdvancedSearch"
					class="px-4 py-2.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
						/>
					</svg>
				</button>
			</div>

			<!-- Stats Summary -->
			<div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
				<div
					class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-100 dark:border-blue-800/30"
				>
					<span class="text-xs text-blue-600 dark:text-blue-400 font-medium"
						>Received</span
					>
					<p class="text-xl font-bold text-blue-700 dark:text-blue-300">
						{{ stats['Received'] || 0 }}
					</p>
				</div>
				<div
					class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3 border border-orange-100 dark:border-orange-800/30"
				>
					<span class="text-xs text-orange-600 dark:text-orange-400 font-medium"
						>In Progress</span
					>
					<p class="text-xl font-bold text-orange-700 dark:text-orange-300">
						{{ stats['In Progress'] || 0 }}
					</p>
				</div>
				<div
					class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-100 dark:border-purple-800/30"
				>
					<span class="text-xs text-purple-600 dark:text-purple-400 font-medium"
						>Waiting Parts</span
					>
					<p class="text-xl font-bold text-purple-700 dark:text-purple-300">
						{{ stats['Waiting for Parts'] || 0 }}
					</p>
				</div>
				<div
					class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-100 dark:border-green-800/30"
				>
					<span class="text-xs text-green-600 dark:text-green-400 font-medium"
						>Ready</span
					>
					<p class="text-xl font-bold text-green-700 dark:text-green-300">
						{{ stats['Ready for Pickup'] || 0 }}
					</p>
				</div>
			</div>

			<!-- Orders Grid -->
			<div class="flex-1 overflow-y-auto pb-20">
				<div
					v-if="ordersResource.loading && !orders.length"
					class="py-20 text-center bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-200 dark:border-gray-700"
				>
					<div
						class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-4"
					></div>
					<p class="text-gray-500 dark:text-gray-400">Loading repairs...</p>
				</div>

				<div
					v-else-if="!orders.length"
					class="py-20 text-center bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-200 dark:border-gray-700"
				>
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
							d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
						/>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.5"
							d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
						/>
					</svg>
					<p class="text-gray-500 dark:text-gray-400 text-sm">No repair orders found</p>
					<p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
						Create a new repair order to get started
					</p>
				</div>

				<div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					<div
						v-for="order in orders"
						:key="order.name"
						@click="openDetail(order)"
						class="p-4 rounded-xl border bg-white dark:bg-gray-900 hover:border-[#D4AF37] hover:shadow-md cursor-pointer transition-all group"
						:class="getStatusBorderColor(order.status)"
					>
						<!-- Header -->
						<div class="flex justify-between items-start mb-3">
							<div>
								<span class="font-mono text-sm font-bold text-[#D4AF37]">{{
									order.name
								}}</span>
								<span
									class="ml-2 inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold"
									:class="getStatusBadgeClass(order.status)"
								>
									{{ order.status }}
								</span>
							</div>
							<span class="text-xs text-gray-400">{{
								formatDate(order.creation)
							}}</span>
						</div>

						<!-- Repair Type -->
						<p class="font-medium text-gray-900 dark:text-white mb-2 truncate">
							{{ order.repair_type_name || order.repair_type }}
						</p>

						<!-- Customer Info -->
						<div class="space-y-1 mb-3">
							<div
								class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"
							>
								<svg
									class="w-4 h-4 text-gray-400"
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
								<span class="truncate">{{
									order.customer_name || order.customer
								}}</span>
							</div>
							<div
								v-if="order.customer_phone"
								class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-500"
							>
								<svg
									class="w-4 h-4 text-gray-400"
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
								<span>{{ order.customer_phone }}</span>
							</div>
						</div>

						<!-- Footer -->
						<div
							class="flex items-center justify-between pt-2 border-t border-gray-100 dark:border-gray-800"
						>
							<span class="text-xs text-gray-400">
								By: {{ order.handled_by_name || 'Unassigned' }}
							</span>
							<span class="text-sm font-bold text-gray-900 dark:text-white">
								${{ formatNum(order.estimated_cost || order.total_cost) }}
							</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Detail Modal -->
			<Teleport to="body">
				<div
					v-if="detailOrder"
					class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
					@click.self="detailOrder = null"
				>
					<div
						class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto"
					>
						<!-- Modal Header -->
						<div
							class="sticky top-0 bg-white dark:bg-gray-900 p-4 border-b border-gray-100 dark:border-gray-800 flex justify-between items-start"
						>
							<div>
								<h3 class="text-lg font-bold text-gray-900 dark:text-white">
									{{ detailOrder.name }}
								</h3>
								<span
									class="inline-flex px-2 py-0.5 rounded-full text-xs font-bold mt-1"
									:class="getStatusBadgeClass(detailOrder.status)"
								>
									{{ detailOrder.status }}
								</span>
							</div>
							<button
								@click="detailOrder = null"
								class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition"
							>
								<svg
									class="w-5 h-5"
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
						</div>

						<!-- Modal Body -->
						<div class="p-4 space-y-4">
							<!-- Customer Section -->
							<div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
								<h4
									class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-2"
								>
									Customer
								</h4>
								<p class="font-medium text-gray-900 dark:text-white">
									{{ detailOrder.customer_name }}
								</p>
								<p
									v-if="detailOrder.customer_phone"
									class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1 mt-1"
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
											d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
										/>
									</svg>
									{{ detailOrder.customer_phone }}
								</p>
							</div>

							<!-- Repair Details -->
							<div class="space-y-2">
								<div class="flex justify-between">
									<span class="text-gray-500 dark:text-gray-400"
										>Repair Type:</span
									>
									<span class="font-medium text-gray-900 dark:text-white">{{
										detailOrder.repair_type_name
									}}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500 dark:text-gray-400"
										>Handled by:</span
									>
									<span class="font-medium text-gray-900 dark:text-white">{{
										detailOrder.handled_by_name || 'Unassigned'
									}}</span>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500 dark:text-gray-400"
										>Est. Cost:</span
									>
									<span class="font-bold text-[#D4AF37]"
										>${{ formatNum(detailOrder.estimated_cost) }}</span
									>
								</div>
								<div class="flex justify-between">
									<span class="text-gray-500 dark:text-gray-400">Total:</span>
									<span class="font-bold text-gray-900 dark:text-white"
										>${{ formatNum(detailOrder.total_cost) }}</span
									>
								</div>
							</div>

							<!-- Description -->
							<div
								v-if="detailOrder.description"
								class="border-t border-gray-100 dark:border-gray-800 pt-4"
							>
								<h4
									class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-2"
								>
									Description
								</h4>
								<p class="text-sm text-gray-700 dark:text-gray-300">
									{{ detailOrder.description }}
								</p>
							</div>

							<!-- Quick Actions -->
							<div
								class="flex flex-wrap gap-2 pt-4 border-t border-gray-100 dark:border-gray-800"
							>
								<button
									@click="printReceipt(detailOrder.name)"
									class="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition flex items-center gap-1"
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
											d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
										/>
									</svg>
									Print Receipt
								</button>
								<button
									@click="openCustomerHistory(detailOrder.customer)"
									class="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition flex items-center gap-1"
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
											d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
									History
								</button>
							</div>

							<!-- Customer History -->
							<div
								v-if="showHistory.length"
								class="border-t border-gray-100 dark:border-gray-800 pt-4"
							>
								<h4
									class="font-bold text-sm text-gray-700 dark:text-gray-300 mb-2"
								>
									Customer repair history
								</h4>
								<ul class="text-sm space-y-1">
									<li
										v-for="h in showHistory"
										:key="h.name"
										class="flex justify-between items-center py-1 border-b border-gray-100 dark:border-gray-800 last:border-0"
									>
										<span>{{ h.name }} - {{ h.repair_type_name }}</span>
										<span
											class="text-xs px-2 py-0.5 rounded-full"
											:class="getStatusBadgeClass(h.status)"
											>{{ h.status }}</span
										>
									</li>
								</ul>
							</div>

							<!-- Status Update -->
							<div class="pt-4 border-t border-gray-100 dark:border-gray-800">
								<label
									class="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300"
									>Update status</label
								>
								<select
									v-model="detailStatus"
									@change="updateStatus(detailOrder.name)"
									class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
								>
									<option v-for="s in statusOptions" :key="s" :value="s">
										{{ s }}
									</option>
								</select>
							</div>
						</div>
					</div>
				</div>
			</Teleport>

			<!-- New Repair Modal -->
			<Teleport to="body">
				<div
					v-if="showNewModal"
					class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
					@click.self="showNewModal = false"
				>
					<div
						class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl max-w-md w-full mx-4 p-6"
					>
						<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
							New Repair Order
						</h3>
						<form @submit.prevent="submitNewRepair" class="space-y-4">
							<!-- Customer -->
							<div>
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
									>Customer</label
								>
								<div class="relative">
									<input
										v-model="customerSearchText"
										type="text"
										placeholder="Search customer..."
										@input="onCustomerSearchInput"
										@focus="showCustomerDropdown = true"
										class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900 text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
									/>
									<div
										v-if="showCustomerDropdown && customerOptions.length > 0"
										class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-48 overflow-y-auto"
									>
										<button
											v-for="opt in customerOptions"
											:key="opt.value"
											type="button"
											@click="selectCustomerOption(opt)"
											class="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition border-b border-gray-100 dark:border-gray-700 last:border-0"
										>
											<span
												class="font-medium text-gray-900 dark:text-white"
												>{{ opt.label }}</span
											>
										</button>
									</div>
								</div>
								<p
									v-if="newForm.customer"
									class="mt-1 text-xs text-green-600 dark:text-green-400"
								>
									Selected: {{ newForm.customer.label }}
								</p>
							</div>

							<!-- Repair Type -->
							<div>
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
									>Repair Type</label
								>
								<select
									v-model="newForm.repair_type"
									required
									class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
								>
									<option value="">Select...</option>
									<option
										v-for="rt in repairTypes"
										:key="rt.name"
										:value="rt.name"
									>
										{{ rt.description || rt.name }}
									</option>
								</select>
							</div>

							<!-- Customer Phone -->
							<div>
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
									>Customer Phone</label
								>
								<input
									v-model="newForm.customer_phone"
									type="tel"
									placeholder="(555) 123-4567"
									class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
								/>
							</div>

							<!-- Description -->
							<div>
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
									>Item Description</label
								>
								<textarea
									v-model="newForm.item_description"
									rows="3"
									placeholder="Describe the item and repair needed..."
									class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent resize-none"
								></textarea>
							</div>

							<!-- Estimated Cost -->
							<div>
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5"
									>Estimated Cost ($)</label
								>
								<input
									v-model.number="newForm.estimated_cost"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
								/>
							</div>

							<!-- Actions -->
							<div class="flex gap-3 pt-2">
								<button
									type="button"
									@click="showNewModal = false"
									class="flex-1 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
								>
									Cancel
								</button>
								<button
									type="submit"
									class="flex-1 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-bold hover:bg-[#c9a432] transition"
								>
									Create Repair
								</button>
							</div>
						</form>
					</div>
				</div>
			</Teleport>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import { useSessionStore } from '@/stores/session.js'
import { createResource, call, toast } from 'frappe-ui'
import { ref, watch, onMounted, computed } from 'vue'

const session = useSessionStore()
const statusFilter = ref('')
const searchTerm = ref('')
const orders = ref([])
const stats = ref(null)
const showNewModal = ref(false)
const detailOrder = ref(null)
const detailStatus = ref('')
const showHistory = ref([])
const showAdvancedSearch = ref(false)
const customerQuery = ref('')
const customerSearchText = ref('')
const showCustomerDropdown = ref(false)

const newForm = ref({
	customer: null,
	repair_type: '',
	item_description: '',
	customer_phone: '',
	estimated_cost: null,
})

const repairTypes = ref([])
const statusOptions = [
	'Received',
	'Estimated',
	'Approved',
	'In Progress',
	'Waiting for Parts',
	'Quality Check',
	'Ready for Pickup',
	'Delivered',
	'Cancelled',
]

// Status tabs with counts
const statusTabs = computed(() => {
	const tabs = [
		{ value: '', label: 'All', count: 0 },
		{ value: 'Received', label: 'Received', count: stats.value?.['Received'] || 0 },
		{ value: 'In Progress', label: 'In Progress', count: stats.value?.['In Progress'] || 0 },
		{
			value: 'Waiting for Parts',
			label: 'Parts',
			count: stats.value?.['Waiting for Parts'] || 0,
		},
		{
			value: 'Ready for Pickup',
			label: 'Ready',
			count: stats.value?.['Ready for Pickup'] || 0,
		},
	]
	// Calculate total
	tabs[0].count = Object.values(stats.value || {}).reduce((a, b) => a + b, 0)
	return tabs
})

const repairTypesResource = createResource({
	url: 'zevar_core.api.get_repair_types',
	onSuccess: (data) => {
		repairTypes.value = data || []
	},
})

const customersResource = createResource({
	url: 'frappe.client.get_list',
	makeParams: () => ({
		doctype: 'Customer',
		filters: {
			customer_name: ['like', `%${customerQuery.value}%`],
		},
		fields: ['name', 'customer_name', 'mobile_no'],
		limit_page_length: 10,
	}),
	auto: false,
})

const customerOptions = computed(() => {
	return (customersResource.data || []).map((c) => ({
		label: c.customer_name + (c.mobile_no ? ` (${c.mobile_no})` : ''),
		value: c.name,
	}))
})

let customerSearchTimer
function onCustomerSearchInput() {
	showCustomerDropdown.value = true
	const q = customerSearchText.value
	if (!q || q.length < 2) {
		return
	}
	customerQuery.value = q
	clearTimeout(customerSearchTimer)
	customerSearchTimer = setTimeout(() => {
		customersResource.fetch()
	}, 300)
}

function selectCustomerOption(opt) {
	newForm.value.customer = opt
	customerSearchText.value = opt.label
	showCustomerDropdown.value = false
}

const ordersResource = createResource({
	url: 'zevar_core.api.get_repair_orders',
	makeParams: () => ({
		status: statusFilter.value || undefined,
		warehouse: session.currentWarehouse || undefined,
		search_term: searchTerm.value || undefined,
		page_length: 50,
	}),
	onSuccess: (data) => {
		orders.value = data || []
	},
})

const statsResource = createResource({
	url: 'zevar_core.api.get_repair_stats',
	makeParams: () => ({ warehouse: session.currentWarehouse || undefined }),
	onSuccess: (data) => {
		stats.value = data
	},
})

function loadOrders() {
	ordersResource.fetch()
	statsResource.fetch()
}

function selectStatusTab(value) {
	statusFilter.value = value
	loadOrders()
}

let debounceTimer
function debouncedLoad() {
	clearTimeout(debounceTimer)
	debounceTimer = setTimeout(loadOrders, 300)
}

function formatNum(n) {
	if (n == null) return '0.00'
	return Number(n).toFixed(2)
}

function formatDate(dateStr) {
	if (!dateStr) return ''
	const date = new Date(dateStr)
	return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function getStatusBorderColor(status) {
	const colors = {
		Received: 'border-blue-200 dark:border-blue-800',
		'In Progress': 'border-orange-200 dark:border-orange-800',
		'Waiting for Parts': 'border-purple-200 dark:border-purple-800',
		'Ready for Pickup': 'border-green-200 dark:border-green-800',
		Delivered: 'border-gray-200 dark:border-gray-700',
		Cancelled: 'border-red-200 dark:border-red-800',
	}
	return colors[status] || 'border-gray-200 dark:border-gray-700'
}

function getStatusBadgeClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
		Estimated: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
		Approved: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
		'In Progress': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
		'Waiting for Parts':
			'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
		'Quality Check': 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400',
		'Ready for Pickup': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
		Delivered: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400',
		Cancelled: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
	}
	return classes[status] || 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
}

async function submitNewRepair() {
	if (!newForm.value.customer || !newForm.value.customer.value) {
		toast({
			title: 'Missing Information',
			message: 'Please select a customer.',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	if (!newForm.value.repair_type) {
		toast({
			title: 'Missing Information',
			message: 'Please select a repair type.',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}

	try {
		await call('zevar_core.api.create_repair_order', {
			customer: newForm.value.customer.value,
			repair_type: newForm.value.repair_type,
			item_description: newForm.value.item_description || undefined,
			customer_phone: newForm.value.customer_phone || undefined,
			estimated_cost: newForm.value.estimated_cost || undefined,
			warehouse: session.currentWarehouse || undefined,
			handled_by: session.user?.email || undefined,
		})
		showNewModal.value = false
		customerSearchText.value = ''
		newForm.value = {
			customer: null,
			repair_type: '',
			item_description: '',
			customer_phone: '',
			estimated_cost: null,
		}
		loadOrders()
		toast({
			title: 'Success',
			message: 'Repair order created successfully.',
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		console.error(e)
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message || 'Failed to create repair order.',
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

async function openDetail(order) {
	const d = await call('zevar_core.api.get_repair_order_details', { name: order.name })
	detailOrder.value = d
	detailStatus.value = d.status
}

async function updateStatus(name) {
	try {
		await call('zevar_core.api.update_repair_status', { name, status: detailStatus.value })
		loadOrders()
		toast({
			title: 'Updated',
			message: `Status changed to ${detailStatus.value}`,
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		console.error(e)
		toast({
			title: 'Error',
			message: e.messages?.[0] || e.message || 'Failed to update status',
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

async function printReceipt(name) {
	try {
		const html = await call('zevar_core.api.get_repair_receipt_html', { name })
		const w = window.open('', '_blank')
		w.document.write(html)
		w.document.close()
		w.print()
	} catch (e) {
		console.error(e)
		toast({
			title: 'Error',
			message: 'Failed to generate receipt',
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

async function openCustomerHistory(customer) {
	try {
		const list = await call('zevar_core.api.get_customer_repair_history', {
			customer,
			limit: 10,
		})
		showHistory.value = list || []
	} catch (e) {
		console.error(e)
		toast({
			title: 'Error',
			message: 'Failed to load history',
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

onMounted(() => {
	loadOrders()
	repairTypesResource.fetch()
})
</script>
