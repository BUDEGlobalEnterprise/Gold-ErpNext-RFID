<template>
	<AppLayout>
		<div class="h-full flex flex-col min-h-0">
			<!-- Page Header - consistent with other pages -->
			<!-- Page Header - consistent with other pages -->
			<div class="flex items-center justify-between gap-4 mb-6 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Repair Terminal</h2>
					<span
						class="text-xs font-bold text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-white/5 px-3 py-1 rounded-full border border-gray-200 dark:border-white/10"
					>
						{{ orders.length }} Orders
					</span>
				</div>
				<div class="flex items-center gap-2">
					<!-- View Toggle -->
					<div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
						<button
							@click="viewMode = 'grid'"
							class="px-3 py-1.5 rounded-md text-sm font-medium transition"
							:class="
								viewMode === 'grid'
									? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white'
									: 'text-gray-500 hover:text-gray-700'
							"
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
									d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
								/>
							</svg>
						</button>
						<button
							@click="viewMode = 'kanban'"
							class="px-3 py-1.5 rounded-md text-sm font-medium transition"
							:class="
								viewMode === 'kanban'
									? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white'
									: 'text-gray-500 hover:text-gray-700'
							"
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
									d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
								/>
							</svg>
						</button>
						<button
							v-if="isDesktop"
							@click="viewMode = 'split'"
							class="px-3 py-1.5 rounded-md text-sm font-medium transition"
							:class="
								viewMode === 'split'
									? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white'
									: 'text-gray-500 hover:text-gray-700'
							"
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
									d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 16a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
								/>
							</svg>
						</button>
					</div>
					<button
						@click="showNewModal = true"
						class="px-4 py-2 bg-gray-900 dark:bg-[#D4AF37] text-white dark:text-black rounded-lg text-xs font-bold hover:bg-gray-800 dark:hover:bg-[#c9a432] transition flex items-center gap-2"
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
			</div>

			<!-- Dashboard Stats Widget (compact) -->
			<div
				v-if="dashboardStats"
				class="grid grid-cols-3 md:grid-cols-6 gap-2 mb-3 flex-shrink-0"
			>
				<div
					class="bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2 border border-red-100 dark:border-red-800/30"
				>
					<span class="text-[10px] text-red-600 dark:text-red-400 font-bold uppercase tracking-wide">Overdue</span>
					<p class="text-lg font-bold text-red-700 dark:text-red-300">
						{{ dashboardStats.overdue_count || 0 }}
					</p>
				</div>
				<div
					class="bg-green-50 dark:bg-green-900/20 rounded-lg px-3 py-2 border border-green-100 dark:border-green-800/30"
				>
					<span class="text-[10px] text-green-600 dark:text-green-400 font-bold uppercase tracking-wide">Pickup</span>
					<p class="text-lg font-bold text-green-700 dark:text-green-300">
						{{ dashboardStats.ready_pickup_count || 0 }}
					</p>
				</div>
				<div
					class="bg-blue-50 dark:bg-blue-900/20 rounded-lg px-3 py-2 border border-blue-100 dark:border-blue-800/30"
				>
					<span class="text-[10px] text-blue-600 dark:text-blue-400 font-bold uppercase tracking-wide">Week Rev</span>
					<p class="text-lg font-bold text-blue-700 dark:text-blue-300">
						${{ formatNum(dashboardStats.weekly_revenue || 0) }}
					</p>
				</div>
				<div
					class="bg-purple-50 dark:bg-purple-900/20 rounded-lg px-3 py-2 border border-purple-100 dark:border-purple-800/30"
				>
					<span class="text-[10px] text-purple-600 dark:text-purple-400 font-bold uppercase tracking-wide">Month Rev</span>
					<p class="text-lg font-bold text-purple-700 dark:text-purple-300">
						${{ formatNum(dashboardStats.monthly_revenue || 0) }}
					</p>
				</div>
				<div
					class="bg-orange-50 dark:bg-orange-900/20 rounded-lg px-3 py-2 border border-orange-100 dark:border-orange-800/30"
				>
					<span class="text-[10px] text-orange-600 dark:text-orange-400 font-bold uppercase tracking-wide">Avg Days</span>
					<p class="text-lg font-bold text-orange-700 dark:text-orange-300">
						{{ dashboardStats.avg_turnaround_days || 0 }}d
					</p>
				</div>
				<div
					class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg px-3 py-2 border border-yellow-100 dark:border-yellow-800/30"
				>
					<span class="text-[10px] text-yellow-600 dark:text-yellow-400 font-bold uppercase tracking-wide">Pending</span>
					<p class="text-lg font-bold text-yellow-700 dark:text-yellow-300">
						${{ formatNum(dashboardStats.pending_collections_amount || 0) }}
					</p>
				</div>
			</div>

			<!-- Status Filter Tabs -->
			<div class="flex gap-1.5 mb-3 overflow-x-auto pb-1 flex-shrink-0">
				<button
					v-for="statusItem in statusTabs"
					:key="statusItem.value"
					@click="selectStatusTab(statusItem.value)"
					class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition whitespace-nowrap"
					:class="
						statusFilter === statusItem.value
							? 'bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30'
							: 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-transparent hover:bg-gray-200 dark:hover:bg-gray-700'
					"
				>
					<span>{{ statusItem.label }}</span>
					<span
						v-if="statusItem.count > 0"
						class="px-1.5 py-0.5 rounded-full text-[10px] font-bold"
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

			<!-- Search & Filter Bar -->
			<div class="flex gap-2 mb-3 flex-shrink-0">
				<div class="flex-1 relative">
					<svg
						class="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2"
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
						placeholder="Search repairs..."
						class="w-full pl-9 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
					/>
				</div>
				<button
					@click="showAdvancedSearch = !showAdvancedSearch"
					class="px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition flex items-center gap-1.5"
					:class="{ 'bg-[#D4AF37]/10 border-[#D4AF37]/30': hasActiveFilters }"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
						/>
					</svg>
					<svg
						v-if="hasActiveFilters"
						class="w-3.5 h-3.5 text-[#D4AF37]"
						fill="currentColor"
						viewBox="0 0 20 20"
					>
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
							clip-rule="evenodd"
						/>
					</svg>
				</button>
			</div>

			<!-- Advanced Search Panel -->
			<div
				v-if="showAdvancedSearch"
				class="bg-white dark:bg-gray-800/50 rounded-xl p-4 mb-3 border border-gray-100 dark:border-gray-700/50 flex-shrink-0"
			>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
					<div>
						<label
							class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1"
							>From</label
						>
						<input
							v-model="advancedFilters.from_date"
							type="date"
							class="w-full px-3 py-1.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-sm"
						/>
					</div>
					<div>
						<label
							class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1"
							>To</label
						>
						<input
							v-model="advancedFilters.to_date"
							type="date"
							class="w-full px-3 py-1.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-sm"
						/>
					</div>
					<div>
						<label
							class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1"
							>Priority</label
						>
						<select
							v-model="advancedFilters.priority"
							class="w-full px-3 py-1.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-sm"
						>
							<option value="">All</option>
							<option value="Low">Low</option>
							<option value="Medium">Medium</option>
							<option value="High">High</option>
							<option value="Urgent">Urgent</option>
						</select>
					</div>
					<div>
						<label
							class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1"
							>Technician</label
						>
						<select
							v-model="advancedFilters.assigned_to"
							class="w-full px-3 py-1.5 border border-gray-200 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-sm"
						>
							<option value="">All</option>
							<option
								v-for="tech in technicians"
								:key="tech.value"
								:value="tech.value"
							>
								{{ tech.label }}
							</option>
						</select>
					</div>
				</div>
				<div class="flex justify-end gap-2 mt-3">
					<button
						@click="clearAdvancedFilters"
						class="px-3 py-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-800"
					>
						Clear
					</button>
					<button
						@click="applyAdvancedFilters"
						class="px-4 py-1.5 bg-[#D4AF37] text-black rounded-lg text-sm font-medium hover:bg-[#c9a432]"
					>
						Apply
					</button>
				</div>
			</div>

			<!-- Main Content Area -->
			<div class="flex-1 flex min-h-0 overflow-hidden">
				<!-- Grid View -->
				<div v-if="viewMode === 'grid'" class="flex-1 overflow-y-auto pb-20">
					<div v-if="ordersResource.loading && !orders.length" class="py-20 text-center">
						<div
							class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-4"
						></div>
						<p class="text-gray-500">Loading repairs...</p>
					</div>
					<div
						v-else-if="!orders.length"
						class="py-20 text-center bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-200 dark:border-gray-700"
					>
						<p class="text-gray-500 text-sm">No repair orders found</p>
					</div>
					<div
						v-else
						class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3"
					>
						<RepairCard
							v-for="order in orders"
							:key="order.name"
							:order="order"
							@open-detail="openDetail(order)"
							@quick-status="quickStatusChange"
							@open-qr="showQRCode(order)"
							@print-thermal="printThermalReceipt(order)"
						/>
					</div>
				</div>

				<!-- Kanban View -->
				<div v-else-if="viewMode === 'kanban'" class="flex-1 overflow-x-auto pb-4">
					<div class="flex gap-3 min-w-max h-full">
						<div
							v-for="column in kanbanColumns"
							:key="column.status"
							class="w-72 flex-shrink-0 flex flex-col bg-gray-50 dark:bg-gray-800 rounded-xl"
						>
							<div class="p-3 border-b border-gray-200 dark:border-gray-700">
								<h3
									class="font-bold text-gray-800 dark:text-gray-200 flex items-center justify-between"
								>
									{{ column.label }}
									<span
										class="px-2 py-0.5 rounded-full text-xs font-bold"
										:class="column.badgeClass"
										>{{ column.count }}</span
									>
								</h3>
							</div>
							<div
								class="flex-1 overflow-y-auto p-2 space-y-2"
								@dragover.prevent
								@drop="onDrop($event, column.status)"
							>
								<div
									v-for="order in column.orders"
									:key="order.name"
									draggable="true"
									@dragstart="onDragStart($event, order)"
									class="p-3 bg-white dark:bg-gray-900 rounded-lg shadow-sm cursor-pointer hover:shadow-md transition"
									:class="getStatusBorderColor(order.status)"
								>
									<div class="flex justify-between items-start mb-2">
										<span class="font-mono text-xs font-bold text-[#D4AF37]">{{
											order.name
										}}</span>
										<span
											v-if="order.priority === 'Urgent'"
											class="text-red-500"
										>
											<svg
												class="w-4 h-4"
												fill="currentColor"
												viewBox="0 0 20 20"
											>
												<path
													fill-rule="evenodd"
													d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
													clip-rule="evenodd"
												/>
											</svg>
										</span>
									</div>
									<p
										class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate"
									>
										{{ order.repair_type_name || order.repair_type }}
									</p>
									<p class="text-xs text-gray-500 truncate">
										{{ order.customer_name || order.customer }}
									</p>
									<div
										class="flex justify-between items-center mt-2 pt-2 border-t border-gray-100"
									>
										<span class="text-xs text-gray-400">{{
											formatDate(order.creation)
										}}</span>
										<span class="text-sm font-bold"
											>${{
												formatNum(order.estimated_cost || order.total_cost)
											}}</span
										>
									</div>
									<!-- Quick Actions -->
									<div class="flex gap-1 mt-2">
										<button
											@click.stop="
												quickStatusChange(
													order.name,
													getNextStatus(order.status)
												)
											"
											class="flex-1 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
										>
											→ Next
										</button>
										<button
											@click.stop="openDetail(order)"
											class="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
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
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Split View -->
				<div v-else-if="viewMode === 'split'" class="flex-1 flex gap-4 overflow-hidden">
					<div class="w-1/2 overflow-y-auto">
						<div
							v-if="ordersResource.loading && !orders.length"
							class="py-20 text-center"
						>
							<div
								class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-4"
							></div>
						</div>
						<div v-else class="space-y-2">
							<div
								v-for="order in orders"
								:key="order.name"
								@click="selectedSplitOrder = order"
								class="p-3 rounded-lg border cursor-pointer transition hover:shadow-md"
								:class="
									selectedSplitOrder?.name === order.name
										? 'bg-[#D4AF37]/10 border-[#D4AF37]'
										: 'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700'
								"
							>
								<div class="flex justify-between items-start">
									<div>
										<span class="font-mono text-sm font-bold text-[#D4AF37]">{{
											order.name
										}}</span>
										<span
											class="ml-2 px-2 py-0.5 rounded-full text-[10px] font-bold"
											:class="getStatusBadgeClass(order.status)"
											>{{ order.status }}</span
										>
									</div>
									<span class="text-sm font-bold"
										>${
											formatNum(order.estimated_cost || order.total_cost)
										}</span
									>
								</div>
								<p class="text-sm font-medium mt-1 truncate">
									{{ order.repair_type_name || order.repair_type }}
								</p>
								<p class="text-xs text-gray-500">
									{{ order.customer_name || order.customer }}
								</p>
							</div>
						</div>
					</div>
					<div class="w-1/2 overflow-y-auto">
						<div
							v-if="selectedSplitOrder"
							class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700"
						>
							<SplitDetailView
								:order="selectedSplitOrder"
								@status-changed="onStatusChanged"
								@print-thermal="printThermalReceipt"
								@open-qr="showQRCode"
							/>
						</div>
						<div v-else class="flex items-center justify-center h-full text-gray-400">
							Select a repair to view details
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Detail Modal -->
		<DetailModal
			v-if="detailOrder"
			:order="detailOrder"
			@close="detailOrder = null"
			@status-changed="onStatusChanged"
			@print-thermal="printThermalReceipt"
			@open-qr="showQRCode"
			@open-camera="showCameraModal = true"
		/>

		<!-- New Repair Modal -->
		<NewRepairModal
			v-if="showNewModal"
			@close="showNewModal = false"
			@created="onRepairCreated"
		/>

		<!-- QR Code Modal -->
		<QRCodeModal v-if="qrOrder" :order="qrOrder" @close="qrOrder = null" />

		<!-- Camera Modal for Photo Capture -->
		<CameraModal
			v-if="showCameraModal"
			@close="showCameraModal = false"
			@photo-captured="onPhotoCaptured"
		/>

		<!-- Store Transfer Modal -->
		<StoreTransferModal
			v-if="showTransferModal"
			:order="transferOrder"
			@close="showTransferModal = false"
			@transferred="onRepairCreated"
		/>

		<!-- Payment Modal -->
		<PaymentModal
			v-if="showPaymentModal"
			:order="paymentOrder"
			@close="showPaymentModal = false"
			@payment-recorded="onRepairCreated"
		/>
	</AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { createResource, call, toast } from 'frappe-ui'
import { useSessionStore } from '@/stores/session.js'
import RepairCard from '@/components/RepairCard.vue'
import DetailModal from '@/components/RepairDetailModal.vue'
import SplitDetailView from '@/components/SplitDetailView.vue'
import NewRepairModal from '@/components/NewRepairModal.vue'
import QRCodeModal from '@/components/QRCodeModal.vue'
import CameraModal from '@/components/CameraModal.vue'
import StoreTransferModal from '@/components/StoreTransferModal.vue'
import PaymentModal from '@/components/PaymentModal.vue'

const session = useSessionStore()
const viewMode = ref('grid') // grid, kanban, split
const statusFilter = ref('')
const searchTerm = ref('')
// Use global warehouse from session
const selectedStore = computed(() => session.currentWarehouse || 'all')

// Watch for warehouse changes to reload orders
watch(() => session.currentWarehouse, () => {
	loadOrders()
})
const showAdvancedSearch = ref(false)
const refreshInterval = ref(0) // Auto-refresh off by default
const orders = ref([])
const stats = ref(null)
const dashboardStats = ref(null)
const multiStoreStats = ref([])
const detailOrder = ref(null)
const selectedSplitOrder = ref(null)
const qrOrder = ref(null)
const showCameraModal = ref(false)
const showTransferModal = ref(false)
const transferOrder = ref(null)
const showPaymentModal = ref(false)
const paymentOrder = ref(null)
const showNewModal = ref(false)

const advancedFilters = ref({
	from_date: '',
	to_date: '',
	priority: '',
	assigned_to: '',
	customer: '',
})

const technicians = ref([])
let refreshTimer = null

// Status tabs
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
	tabs[0].count = Object.values(stats.value || {}).reduce((a, b) => a + b, 0)
	return tabs
})

const isDesktop = computed(() => window.innerWidth >= 1024)

const hasActiveFilters = computed(() => {
	return Object.values(advancedFilters.value).some((v) => v !== '')
})

// Kanban columns
const kanbanColumns = computed(() => {
	const columns = [
		{
			status: 'Received',
			label: 'Received',
			badgeClass: 'bg-blue-100 text-blue-700',
			orders: [],
		},
		{
			status: 'Estimated',
			label: 'Estimated',
			badgeClass: 'bg-yellow-100 text-yellow-700',
			orders: [],
		},
		{
			status: 'Approved',
			label: 'Approved',
			badgeClass: 'bg-indigo-100 text-indigo-700',
			orders: [],
		},
		{
			status: 'In Progress',
			label: 'In Progress',
			badgeClass: 'bg-orange-100 text-orange-700',
			orders: [],
		},
		{
			status: 'Waiting for Parts',
			label: 'Waiting Parts',
			badgeClass: 'bg-purple-100 text-purple-700',
			orders: [],
		},
		{
			status: 'Quality Check',
			label: 'Quality Check',
			badgeClass: 'bg-cyan-100 text-cyan-700',
			orders: [],
		},
		{
			status: 'Ready for Pickup',
			label: 'Ready',
			badgeClass: 'bg-green-100 text-green-700',
			orders: [],
		},
	]
	orders.value.forEach((order) => {
		const col = columns.find((c) => c.status === order.status)
		if (col) col.orders.push(order)
	})
	columns.forEach((c) => (c.count = c.orders.length))
	return columns
})

// Resources
const ordersResource = createResource({
	url: 'zevar_core.api.get_repair_orders',
	makeParams: () => ({
		status: statusFilter.value || undefined,
		warehouse: selectedStore.value !== 'all' ? selectedStore.value : undefined,
		search_term: searchTerm.value || undefined,
		from_date: advancedFilters.value.from_date || undefined,
		to_date: advancedFilters.value.to_date || undefined,
		priority: advancedFilters.value.priority || undefined,
		assigned_to: advancedFilters.value.assigned_to || undefined,
		customer: advancedFilters.value.customer || undefined,
		page_length: 100,
	}),
	onSuccess: (data) => {
		orders.value = data || []
	},
})

const statsResource = createResource({
	url: 'zevar_core.api.get_repair_stats',
	makeParams: () => ({
		warehouse: selectedStore.value !== 'all' ? selectedStore.value : undefined,
	}),
	onSuccess: (data) => {
		stats.value = data
	},
})

const dashboardStatsResource = createResource({
	url: 'zevar_core.api.get_dashboard_stats',
	makeParams: () => ({
		warehouse: selectedStore.value !== 'all' ? selectedStore.value : undefined,
	}),
	onSuccess: (data) => {
		dashboardStats.value = data
	},
})

const multiStoreStatsResource = createResource({
	url: 'zevar_core.api.get_multi_store_stats',
	onSuccess: (data) => {
		multiStoreStats.value = data || []
	},
})

const techniciansResource = createResource({
	url: 'frappe.client.get_list',
	makeParams: () => ({
		doctype: 'User',
		filters: { enabled: 1 },
		fields: ['name', 'full_name', 'first_name', 'last_name'],
		limit_page_length: 100,
	}),
	onSuccess: (data) => {
		technicians.value = (data || []).map((t) => ({
			value: t.name,
			label: t.full_name || `${t.first_name || ''} ${t.last_name || ''}`.trim() || t.name,
		}))
	},
})

function loadOrders() {
	ordersResource.fetch()
	statsResource.fetch()
	dashboardStatsResource.fetch()
	if (selectedStore.value === 'all') multiStoreStatsResource.fetch()
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

function applyAdvancedFilters() {
	showAdvancedSearch.value = false
	loadOrders()
}

function clearAdvancedFilters() {
	advancedFilters.value = {
		from_date: '',
		to_date: '',
		priority: '',
		assigned_to: '',
		customer: '',
	}
	loadOrders()
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
		Received: 'border-blue-200',
		'In Progress': 'border-orange-200',
		'Waiting for Parts': 'border-purple-200',
		'Ready for Pickup': 'border-green-200',
		Delivered: 'border-gray-200',
		Cancelled: 'border-red-200',
	}
	return colors[status] || 'border-gray-200'
}

function getStatusBadgeClass(status) {
	const classes = {
		Received: 'bg-blue-100 text-blue-700',
		Estimated: 'bg-yellow-100 text-yellow-700',
		Approved: 'bg-indigo-100 text-indigo-700',
		'In Progress': 'bg-orange-100 text-orange-700',
		'Waiting for Parts': 'bg-purple-100 text-purple-700',
		'Quality Check': 'bg-cyan-100 text-cyan-700',
		'Ready for Pickup': 'bg-green-100 text-green-700',
		Delivered: 'bg-gray-100 text-gray-700',
		Cancelled: 'bg-red-100 text-red-700',
	}
	return classes[status] || 'bg-gray-100 text-gray-600'
}

async function openDetail(order) {
	const d = await call('zevar_core.api.get_repair_order_details', { name: order.name })
	detailOrder.value = d
}

async function quickStatusChange(name, newStatus) {
	try {
		await call('zevar_core.api.update_repair_status', { name, status: newStatus })
		loadOrders()
		toast({
			title: 'Updated',
			message: `Status changed to ${newStatus}`,
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
	}
}

function getNextStatus(currentStatus) {
	const flow = [
		'Received',
		'Estimated',
		'Approved',
		'In Progress',
		'Waiting for Parts',
		'Quality Check',
		'Ready for Pickup',
		'Delivered',
	]
	const idx = flow.indexOf(currentStatus)
	if (idx >= 0 && idx < flow.length - 1) return flow[idx + 1]
	return currentStatus
}

function onStatusChanged() {
	loadOrders()
	detailOrder.value = null
}

function onRepairCreated() {
	showNewModal.value = false
	showTransferModal.value = false
	showPaymentModal.value = false
	loadOrders()
}

function showQRCode(order) {
	qrOrder.value = order
}

async function printThermalReceipt(order) {
	try {
		const html = await call('zevar_core.api.get_thermal_receipt_html', { name: order.name })
		const w = window.open('', '_blank')
		w.document.write(html)
		w.document.close()
		w.print()
	} catch (e) {
		toast({
			title: 'Error',
			message: 'Failed to generate receipt',
			icon: 'alert-triangle',
			intent: 'error',
		})
	}
}

function onPhotoCaptured(photoData) {
	// Handle captured photo
	if (detailOrder.value) {
		// Attach photo to repair order
		call('zevar_core.api.attach_repair_photo', {
			repair_order: detailOrder.value.name,
			photo_data: photoData,
			photo_type: 'before',
		}).then(() => {
			toast({
				title: 'Success',
				message: 'Photo attached',
				icon: 'check',
				intent: 'success',
			})
			openDetail(detailOrder.value)
		})
	}
	showCameraModal.value = false
}

// Drag and drop for Kanban
let draggedOrder = null

function onDragStart(event, order) {
	draggedOrder = order
	event.dataTransfer.effectAllowed = 'move'
}

function onDrop(event, newStatus) {
	event.preventDefault()
	if (draggedOrder && draggedOrder.status !== newStatus) {
		quickStatusChange(draggedOrder.name, newStatus)
	}
	draggedOrder = null
}

// Auto-refresh
function setupAutoRefresh() {
	if (refreshTimer) clearInterval(refreshTimer)
	if (refreshInterval.value > 0) {
		refreshTimer = setInterval(loadOrders, refreshInterval.value)
	}
}

onMounted(() => {
	loadOrders()
	techniciansResource.fetch()
	setupAutoRefresh()
})

onUnmounted(() => {
	if (refreshTimer) clearInterval(refreshTimer)
})
</script>
