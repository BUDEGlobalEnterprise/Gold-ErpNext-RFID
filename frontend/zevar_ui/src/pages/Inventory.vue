<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Inventory</h2>
					<span
						class="status-label !mb-0 !bg-gray-100 dark:!bg-warm-dark-700 !text-gray-600 dark:!text-white/60 !px-4 !py-1 !rounded-full !border !border-gray-200 dark:!border-warm-border"
					>
						{{ totalItems }} Items
					</span>
				</div>

				<div class="flex items-center gap-2">
					<button
						@click="refreshData"
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						title="Refresh"
					>
						<svg
							class="w-4 h-4 text-gray-500"
							:class="{ 'animate-spin': inventoryResource.loading }"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357 2m15.357 2H15"
							/>
						</svg>
					</button>
					<button
						@click="showStockAdjust = true"
						class="hidden sm:flex items-center gap-1.5 px-3 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold hover:bg-emerald-700 transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
							/>
						</svg>
						Adjust Stock
					</button>
					<button
						@click="showReductions = true"
						class="hidden sm:flex items-center gap-1.5 px-3 py-2 border border-amber-300 bg-amber-50 text-amber-700 rounded-lg text-xs font-bold hover:bg-amber-100 transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"
							/>
						</svg>
						Reductions
					</button>
					<button
						@click="showQuickAdd = true"
						class="hidden sm:flex items-center gap-1.5 px-3 py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold hover:bg-[#C4A030] transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 6v6m0 0v6m0-6h6m-6 0H6"
							/>
						</svg>
						Quick Add
					</button>
					<button
						@click="openPushForSelected"
						class="hidden sm:flex items-center gap-1.5 px-3 py-2 bg-blue-600 text-white rounded-lg text-xs font-bold hover:bg-blue-700 transition"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
							/>
						</svg>
						Push
					</button>
					<button
						@click="showTransferModal = true"
						class="hidden sm:flex items-center gap-1.5 px-3 py-2 border border-gray-300 rounded-lg text-xs font-bold hover:bg-gray-50 transition"
					>
						Transfer
					</button>
					<button
						@click="showConsignment = true"
						class="hidden sm:flex items-center gap-1.5 px-3 py-2 border border-gray-300 rounded-lg text-xs font-bold hover:bg-gray-50 transition"
					>
						Consignment
					</button>

					<div class="md:hidden">
						<button
							@click="mobileMenuOpen = !mobileMenuOpen"
							class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
						>
							<svg
								class="w-5 h-5 text-gray-600 dark:text-gray-300"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
								/>
							</svg>
						</button>
					</div>

					<ViewToggle v-model="viewMode" storage-key="zevar_inventory_view" />
				</div>
			</div>

			<div v-if="mobileMenuOpen" class="md:hidden grid grid-cols-2 gap-2 mb-4">
				<button
					@click="
						showStockAdjust = true;
						mobileMenuOpen = false;
					"
					class="py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold"
				>
					Adjust Stock
				</button>
				<button
					@click="
						showReductions = true;
						mobileMenuOpen = false;
					"
					class="py-2 bg-amber-50 text-amber-700 border border-amber-300 rounded-lg text-xs font-bold"
				>
					Reductions
				</button>
				<button
					@click="
						showQuickAdd = true;
						mobileMenuOpen = false;
					"
					class="py-2 bg-[#D4AF37] text-white rounded-lg text-xs font-bold"
				>
					Quick Add
				</button>
				<button
					@click="
						openPushForSelected();
						mobileMenuOpen = false;
					"
					class="py-2 bg-blue-600 text-white rounded-lg text-xs font-bold"
				>
					Push
				</button>
				<button
					@click="
						showTransferModal = true;
						mobileMenuOpen = false;
					"
					class="py-2 border rounded-lg text-xs font-bold"
				>
					Transfer
				</button>
				<button
					@click="
						showConsignment = true;
						mobileMenuOpen = false;
					"
					class="py-2 border rounded-lg text-xs font-bold"
				>
					Consignment
				</button>
			</div>

			<div class="hidden md:flex justify-center px-4 mb-4">
				<ItemFilterBar context="inventory" />
			</div>

			<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4 flex-shrink-0">
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Items
					</div>
					<div class="text-2xl font-bold text-gray-900 dark:text-white">
						{{ totalItems }}
					</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Total Value
					</div>
					<div class="text-2xl font-bold text-[#D4AF37]">
						{{ formatCurrency(totalValue) }}
					</div>
					<div class="text-[10px] text-gray-500 font-bold mt-1">Retail value</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Low Stock
					</div>
					<div class="text-2xl font-bold text-amber-500">{{ lowStockItems.length }}</div>
					<div class="text-[10px] text-amber-500 font-bold mt-1">Need reorder</div>
				</div>
				<div class="premium-card !p-4">
					<div
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1"
					>
						Out of Stock
					</div>
					<div class="text-2xl font-bold text-red-500">{{ outOfStockItems.length }}</div>
					<div class="text-[10px] text-red-500 font-bold mt-1">Requires action</div>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
				<div v-if="viewMode === 'list'" class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead>
							<tr
								class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50"
							>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Item
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden sm:table-cell"
								>
									Metal
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell"
								>
									Purity
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden md:table-cell"
								>
									Weight
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Stock
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Value
								</th>
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell"
								>
									Status
								</th>
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider hidden lg:table-cell"
								>
									Actions
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="item in filteredItems"
								:key="item.code"
								class="border-b border-gray-100 dark:border-warm-border/50 hover:bg-gray-50/50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
								:class="{
									'bg-emerald-50/50 dark:bg-emerald-900/10':
										selectedItem?.code === item.code,
								}"
								@click="selectedItem = item"
							>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div
											class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-warm-dark-900 overflow-hidden shrink-0"
										>
											<div
												class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600 text-[10px]"
											>
												IMG
											</div>
										</div>
										<div class="min-w-0">
											<div
												class="font-bold text-gray-900 dark:text-white text-xs truncate"
											>
												{{ item.name }}
											</div>
											<div class="text-[10px] text-gray-500 truncate">
												{{ item.code }}
											</div>
										</div>
									</div>
								</td>
								<td class="px-4 py-3 hidden sm:table-cell">
									<span
										class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
										>{{ item.metal }}</span
									>
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell"
								>
									{{ item.purity }}
								</td>
								<td
									class="px-4 py-3 text-xs text-gray-600 dark:text-gray-400 text-right font-mono hidden md:table-cell"
								>
									{{ item.weight }}g
								</td>
								<td class="px-4 py-3 text-right">
									<span
										class="text-xs font-bold"
										:class="
											item.stock <= 0
												? 'text-red-500'
												: item.stock < 5
												? 'text-amber-500'
												: 'text-green-600'
										"
										>{{ item.stock }}</span
									>
								</td>
								<td
									class="px-4 py-3 text-right text-xs font-bold font-mono text-gray-900 dark:text-white"
								>
									{{ formatCurrency(item.price) }}
								</td>
								<td class="px-4 py-3 text-center hidden lg:table-cell">
									<span
										class="text-[9px] font-bold px-2 py-1 rounded-full"
										:class="
											item.stock <= 0
												? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
												: item.stock < 5
												? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
												: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
										"
									>
										{{
											item.stock <= 0
												? 'OUT OF STOCK'
												: item.stock < 5
												? 'LOW STOCK'
												: 'IN STOCK'
										}}
									</span>
								</td>
								<td class="px-4 py-3 text-center hidden lg:table-cell">
									<div class="flex items-center justify-center gap-1">
										<button
											@click.stop="openEdit(item)"
											class="p-1 hover:bg-blue-50 dark:hover:bg-warm-dark-700 rounded"
											title="Edit"
										>
											<svg
												class="w-4 h-4 text-blue-500"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
												/>
											</svg>
										</button>
										<button
											@click.stop="openLifecycle(item)"
											class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded"
											title="Lifecycle"
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
													d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
												/>
											</svg>
										</button>
										<button
											@click.stop="openReserve(item)"
											class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded"
											title="Reserve"
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
													d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
												/>
											</svg>
										</button>
										<button
											@click.stop="openDamage(item)"
											class="p-1 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded"
											title="Damage"
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
													d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
												/>
											</svg>
										</button>
									</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<div
					v-else
					class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3"
				>
					<div
						v-for="item in filteredItems"
						:key="item.code"
						class="premium-card !p-0 overflow-hidden group cursor-pointer"
						@click="selectedItem = item"
					>
						<div class="aspect-square bg-gray-100 dark:bg-warm-dark-900 relative">
							<div
								class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600"
							>
								<svg
									class="w-10 h-10"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="1"
										d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
									/>
								</svg>
							</div>
							<div class="absolute top-2 right-2">
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
									:class="
										item.stock <= 0
											? 'bg-red-100 text-red-700'
											: item.stock < 5
											? 'bg-amber-100 text-amber-700'
											: 'bg-green-100 text-green-700'
									"
									>{{ item.stock }} pcs</span
								>
							</div>
							<div
								class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition flex items-center justify-center opacity-0 group-hover:opacity-100"
							>
								<div class="flex gap-1">
									<button
										@click.stop="openEdit(item)"
										class="p-1.5 bg-white/90 rounded-full hover:bg-white"
										title="Edit"
									>
										<svg
											class="w-3.5 h-3.5 text-blue-600"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
											/>
										</svg>
									</button>
									<button
										@click.stop="openLifecycle(item)"
										class="p-1.5 bg-white/90 rounded-full hover:bg-white"
										title="Lifecycle"
									>
										<svg
											class="w-3.5 h-3.5 text-gray-700"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
											/>
										</svg>
									</button>
									<button
										@click.stop="openReserve(item)"
										class="p-1.5 bg-white/90 rounded-full hover:bg-white"
										title="Reserve"
									>
										<svg
											class="w-3.5 h-3.5 text-gray-700"
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
									</button>
									<button
										@click.stop="openDamage(item)"
										class="p-1.5 bg-white/90 rounded-full hover:bg-white"
										title="Damage"
									>
										<svg
											class="w-3.5 h-3.5 text-gray-700"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
											/>
										</svg>
									</button>
								</div>
							</div>
						</div>
						<div class="p-3">
							<div
								class="text-xs font-bold text-gray-900 dark:text-white truncate mb-1"
							>
								{{ item.name }}
							</div>
							<div class="flex items-center gap-1 mb-2">
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400"
									>{{ item.metal }}</span
								>
								<span
									class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-gray-100 dark:bg-warm-dark-900 text-gray-600 dark:text-gray-400"
									>{{ item.purity }}</span
								>
							</div>
							<div class="flex items-center justify-between">
								<span
									class="text-sm font-bold text-gray-900 dark:text-white font-mono"
									>{{ formatCurrency(item.price) }}</span
								>
								<span class="text-[10px] text-gray-500">{{ item.weight }}g</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<ItemActionDrawer
				v-if="selectedItem"
				:item="selectedItem"
				@close="selectedItem = null"
				@reserve="
					openReserve(selectedItem);
					selectedItem = null;
				"
				@damage="
					openDamage(selectedItem);
					selectedItem = null;
				"
				@lifecycle="
					openLifecycle(selectedItem);
					selectedItem = null;
				"
				@push="
					openPushForItem(selectedItem);
					selectedItem = null;
				"
				@transfer="
					showTransferModal = true;
					selectedItem = null;
				"
				@edit="
					openEdit(selectedItem);
					selectedItem = null;
				"
			/>
		</div>

		<QuickAddItemModal
			v-if="showQuickAdd"
			@close="showQuickAdd = false"
			@created="onDataChanged"
		/>
		<PushToStoresModal
			v-if="showPushToStores"
			:item-code="pushItemCode"
			@close="showPushToStores = false"
			@pushed="onDataChanged"
		/>
		<StoreTransferModal
			v-if="showTransferModal"
			:order="{}"
			mode="dispatch"
			@close="showTransferModal = false"
			@completed="onDataChanged"
		/>
		<ConsignmentModal
			v-if="showConsignment"
			mode="out"
			@close="showConsignment = false"
			@completed="onDataChanged"
		/>
		<ReservePieceModal
			v-if="showReserve && reserveSerialNo"
			:serial-no="reserveSerialNo"
			@close="showReserve = false"
			@reserved="onDataChanged"
		/>
		<DamageReportModal
			v-if="showDamage && damageSerialNo"
			:serial-no="damageSerialNo"
			@close="showDamage = false"
			@completed="onDataChanged"
		/>
		<PieceLifecyclePanel
			v-if="showLifecycle && lifecycleSerialNo"
			:serial-no="lifecycleSerialNo"
			@close="showLifecycle = false"
		/>
		<StockAdjustModal
			v-if="showStockAdjust"
			@close="showStockAdjust = false"
			@completed="onDataChanged"
		/>
		<StockReductionsPanel v-if="showReductions" @close="showReductions = false" />
		<ItemEditModal
			v-if="showEditItem && editItemCode"
			:item-code="editItemCode"
			@close="showEditItem = false"
			@saved="onDataChanged"
		/>
	</AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource, toast } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import ItemFilterBar from '@/components/ItemFilterBar.vue'
import ViewToggle from '@/components/ViewToggle.vue'
import { useUIStore } from '@/stores/ui.js'
import { useSessionStore } from '@/stores/session.js'
import QuickAddItemModal from '@/components/QuickAddItemModal.vue'
import PushToStoresModal from '@/components/PushToStoresModal.vue'
import StoreTransferModal from '@/components/StoreTransferModal.vue'
import ConsignmentModal from '@/components/ConsignmentModal.vue'
import ReservePieceModal from '@/components/ReservePieceModal.vue'
import DamageReportModal from '@/components/DamageReportModal.vue'
import PieceLifecyclePanel from '@/components/PieceLifecyclePanel.vue'
import StockAdjustModal from '@/components/StockAdjustModal.vue'
import StockReductionsPanel from '@/components/StockReductionsPanel.vue'
import ItemActionDrawer from '@/components/ItemActionDrawer.vue'
import ItemEditModal from '@/components/ItemEditModal.vue'
import { useRoute } from 'vue-router'

const ui = useUIStore()
const session = useSessionStore()
const route = useRoute()
const viewMode = ref(localStorage.getItem('zevar_inventory_view') || 'list')

const inventoryData = ref([])
const selectedItem = ref(null)
const mobileMenuOpen = ref(false)

const showQuickAdd = ref(false)
const showPushToStores = ref(false)
const showTransferModal = ref(false)
const showConsignment = ref(false)
const showReserve = ref(false)
const showDamage = ref(false)
const showLifecycle = ref(false)
const showStockAdjust = ref(false)
const showReductions = ref(false)
const showEditItem = ref(false)
const reserveSerialNo = ref('')
const damageSerialNo = ref('')
const lifecycleSerialNo = ref('')
const editItemCode = ref('')
const pushItemCode = ref('')

const inventoryResource = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		return { warehouse: session.currentWarehouse, page_length: 500 }
	},
	onSuccess(data) {
		inventoryData.value = data.map((i) => ({
			code: i.item_code,
			name: i.item_name,
			metal: i.metal || '-',
			purity: i.purity || '-',
			weight: i.gross_weight || 0,
			stock: i.stock_qty || 0,
			price: i.price || i.msrp || 0,
			category: i.jewelry_type || i.item_group || 'Other',
			serialNo: i.serial_no || '',
		}))
	},
})

inventoryResource.fetch()

const totalItems = computed(() => inventoryData.value.length)
const totalValue = computed(() =>
	inventoryData.value.reduce((sum, i) => sum + i.price * Math.max(i.stock, 0), 0)
)
const lowStockItems = computed(() => inventoryData.value.filter((i) => i.stock > 0 && i.stock < 5))
const outOfStockItems = computed(() => inventoryData.value.filter((i) => i.stock <= 0))

const filteredItems = computed(() => {
	let items = [...inventoryData.value]
	const f = ui.activeFilters.inventory || {}
	const sortBy = ui.sortBy.inventory || ''

	if (f.custom_metal_type) items = items.filter((i) => i.metal === f.custom_metal_type)
	if (f.custom_jewelry_type) items = items.filter((i) => i.category === f.custom_jewelry_type)
	if (f.in_stock_only) items = items.filter((i) => i.stock > 0)
	if (f.out_of_stock_only) items = items.filter((i) => i.stock <= 0)
	if (f.low_stock_only) items = items.filter((i) => i.stock > 0 && i.stock < 5)
	if (f.price_min) items = items.filter((i) => i.price >= f.price_min)
	if (f.price_max) items = items.filter((i) => i.price <= f.price_max)
	if (f.custom_purity) items = items.filter((i) => i.purity === f.custom_purity)

	if (ui.searchQuery) {
		const q = ui.searchQuery.toLowerCase()
		items = items.filter(
			(i) => i.name.toLowerCase().includes(q) || i.code.toLowerCase().includes(q)
		)
	}

	if (sortBy === 'price_asc') items.sort((a, b) => a.price - b.price)
	else if (sortBy === 'price_desc') items.sort((a, b) => b.price - a.price)
	else if (sortBy === 'weight_asc') items.sort((a, b) => a.weight - b.weight)
	else if (sortBy === 'weight_desc') items.sort((a, b) => b.weight - a.weight)
	else if (sortBy === 'name_asc') items.sort((a, b) => a.name.localeCompare(b.name))

	return items
})

function refreshData() {
	inventoryResource.fetch()
}

function openEdit(item) {
	editItemCode.value = item.code
	showEditItem.value = true
}

function openLifecycle(item) {
	lifecycleSerialNo.value = item.serialNo || item.code
	showLifecycle.value = true
}
function openReserve(item) {
	reserveSerialNo.value = item.serialNo || item.code
	showReserve.value = true
}
function openDamage(item) {
	damageSerialNo.value = item.serialNo || item.code
	showDamage.value = true
}
function openPushForItem(item) {
	if (!item) {
		toast({ title: 'Select an item first', icon: 'info', intent: 'warning' })
		return
	}
	pushItemCode.value = item.code
	showPushToStores.value = true
}
function openPushForSelected() {
	if (selectedItem.value) {
		openPushForItem(selectedItem.value)
	} else {
		pushItemCode.value = ''
		showPushToStores.value = true
	}
}
function onDataChanged() {
	inventoryResource.fetch()
	showQuickAdd.value = false
	showPushToStores.value = false
	showTransferModal.value = false
	showConsignment.value = false
	showReserve.value = false
	showDamage.value = false
	showEditItem.value = false
	selectedItem.value = null
}

function formatCurrency(val) {
	if (!val) return '$0.00'
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		maximumFractionDigits: 0,
	}).format(val)
}

if (route.name === 'InventoryAdd') {
	showQuickAdd.value = true
}
</script>
