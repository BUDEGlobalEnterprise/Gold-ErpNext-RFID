<template>
	<AppLayout>
		<div
			v-if="!session.currentWarehouse"
			class="min-h-[50vh] flex flex-col items-center justify-center text-center opacity-50"
		>
			<div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4">
				<svg
					class="w-8 h-8 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
					></path>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
					></path>
				</svg>
			</div>
			<h3 class="premium-title !text-xl mb-2">Select Store Location</h3>
			<p class="premium-subtitle">Choose a location from the top menu to view inventory.</p>
		</div>

		<div v-else class="flex flex-col">
			<div class="flex flex-wrap items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">
						{{ viewMode === 'catalog' ? 'Catalogue' : 'Collection' }}
					</h2>

					<div v-if="posSession.hasActiveSession" class="flex items-center gap-2">
						<template v-if="posSession.activeSession?.status === 'Open'">
							<router-link
								to="/closing"
								class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/30 hover:bg-green-500/20 transition"
							>
								<span class="relative flex h-1.5 w-1.5"
									><span
										class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"
									></span
									><span
										class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"
									></span
								></span>
								Session Open
							</router-link>
							<button
								@click="handleSuspend"
								class="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition"
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
										d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
								Suspend
							</button>
							<button
								@click="openRegisterActionsDrawer"
								class="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30 hover:bg-[#D4AF37]/20 transition"
							>
								⚡ Register Controls
							</button>
						</template>
						<template v-else-if="posSession.activeSession?.status === 'Suspended'">
							<span
								class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-500 border border-amber-500/30"
							>
								<span class="relative flex h-1.5 w-1.5">
									<span
										class="relative inline-flex rounded-full h-1.5 w-1.5 bg-amber-500"
									></span>
								</span>
								Session Suspended
							</span>
						</template>
					</div>
					<router-link
						v-else
						to="/opening"
						class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-500/10 text-red-500 border border-red-500/30 hover:bg-red-500/20 transition"
					>
						<span class="relative flex h-1.5 w-1.5"
							><span
								class="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500"
							></span
						></span>
						No Register Session
					</router-link>

					<!-- Online/Offline Indicator -->
					<OfflineIndicator @show-sync-logs="showSyncModal = true" />

					<div
						v-if="ui.activeFilters.pos?.display_case"
						class="flex items-center gap-1.5 px-3 py-1 bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30 rounded-full text-[10px] font-bold animate-in fade-in slide-in-from-left-2"
					>
						<svg
							class="w-3 h-3"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
						</svg>
						Case-Based View
					</div>
				</div>

				<div class="flex items-center gap-2">
					<!-- Cash In/Out - only when session is active -->
					<button
						v-if="posSession.hasActiveSession"
						@click="showCashModal = true"
						class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition"
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
								d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
							></path>
						</svg>
						Cash In/Out
					</button>

					<!-- Held Carts Button -->
					<button
						v-if="posSession.hasActiveSession"
						@click="toggleHeldCarts"
						class="flex items-center gap-1 px-3 py-1.5 text-xs font-bold rounded-lg border transition-all"
						:class="
							heldCarts.length > 0
								? 'text-amber-600 border-amber-300 bg-amber-50 dark:bg-amber-900/20 dark:border-amber-700/50 dark:text-amber-400'
								: 'text-gray-500 border-gray-200 dark:border-warm-border dark:text-gray-400 hover:border-gray-300'
						"
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
								d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						Held
						<span
							v-if="heldCarts.length > 0"
							class="ml-0.5 w-5 h-5 flex items-center justify-center rounded-full bg-amber-500 text-white text-[10px] font-black"
						>
							{{ heldCarts.length }}
						</span>
					</button>
				</div>

				<!-- Held Carts Dropdown -->
				<Teleport to="body">
					<Transition name="fade">
						<div
							v-if="showHeldDrawer"
							class="fixed inset-0 z-[100] flex items-start justify-center pt-20"
						>
							<div
								@click="showHeldDrawer = false"
								class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm"
							></div>
							<div
								class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-md border dark:border-warm-border overflow-hidden"
							>
								<div
									class="p-4 border-b border-gray-100 dark:border-warm-border/50 flex items-center justify-between"
								>
									<h3 class="text-sm font-bold text-gray-900 dark:text-white">
										Held Carts ({{ heldCarts.length }})
									</h3>
									<button
										@click="showHeldDrawer = false"
										class="p-1 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full"
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
												d="M6 18L18 6M6 6l12 12"
											/>
										</svg>
									</button>
								</div>
								<div
									v-if="heldCarts.length === 0"
									class="p-8 text-center text-gray-400 text-sm"
								>
									No held carts
								</div>
								<div v-else class="max-h-80 overflow-y-auto">
									<div
										v-for="hc in heldCarts"
										:key="hc.id"
										class="p-4 border-b border-gray-50 dark:border-warm-border/30 hover:bg-gray-50 dark:hover:bg-white/5 transition"
									>
										<div class="flex items-center justify-between">
											<div class="min-w-0 flex-1">
												<div
													class="font-bold text-sm text-gray-900 dark:text-white truncate"
												>
													{{
														hc.note ||
														hc.customer_name ||
														'Unnamed cart'
													}}
												</div>
												<div class="text-xs text-gray-400 mt-0.5">
													{{ hc.item_count }} item{{
														hc.item_count !== 1 ? 's' : ''
													}}
													· ${{ Number(hc.total || 0).toFixed(2) }}
												</div>
											</div>
											<div class="flex items-center gap-2 ml-3">
												<button
													@click="recallHeldCart(hc.id)"
													class="px-3 py-1.5 text-xs font-bold bg-[#D4AF37] text-black rounded-lg hover:bg-[#b5952f] transition"
												>
													Recall
												</button>
												<button
													@click="discardHeldCart(hc.id)"
													class="px-2 py-1.5 text-xs text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
												>
													Discard
												</button>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</Transition>
				</Teleport>
			</div>

			<!-- Inline Filter Bar - Beautiful, full-width glassmorphic container -->
			<div
				class="w-full mb-6 bg-white/40 dark:bg-warm-dark-900/60 backdrop-blur-xl px-4 py-2.5 rounded-2xl border border-gray-200/50 dark:border-warm-border/30 shadow-sm flex-shrink-0"
			>
				<ItemFilterBar context="pos" />
			</div>

			<!-- Cash In/Out Modal -->
			<CashMovementModal
				v-if="showCashModal"
				:session-name="posSession.sessionName"
				@close="showCashModal = false"
				@recorded="onCashMovementSaved"
			/>

			<!-- Offline Sync Logs Modal -->
			<OfflineSyncModal :show="showSyncModal" @close="showSyncModal = false" />

			<div class="flex-1 overflow-y-auto min-h-0 pr-2 custom-scrollbar">
				<!-- POS View -->
				<div v-if="viewMode === 'pos'">
					<div v-if="items.loading && start === 0" class="py-20 text-center">
						<div
							class="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 dark:border-white border-t-transparent mx-auto mb-4"
						></div>
						<span class="text-gray-400 text-sm font-medium"
							>Curating Collection...</span
						>
					</div>

					<div
						v-else-if="catalog.length === 0"
						class="py-20 text-center premium-card !bg-transparent !border-dashed !border-gray-200 dark:!border-white/10"
					>
						<p class="premium-subtitle">No pieces found matching your criteria.</p>
					</div>

					<div v-else class="smart-grid">
						<div v-for="item in catalog" :key="item.item_code" class="group">
							<ItemCard
								:item="item"
								@quick-add="handleQuickAdd"
								@open-details="openItemDetails"
							/>
						</div>
					</div>

					<div
						v-if="hasMore && catalog.length > 0"
						class="flex justify-center pt-12 pb-12"
					>
						<button
							@click="loadMore"
							:disabled="items.loading"
							class="px-8 py-3 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border text-gray-900 dark:text-white rounded-full shadow-sm hover:shadow-md hover:border-gray-900 dark:hover:border-white transition-all text-sm font-bold uppercase tracking-wider disabled:opacity-50"
						>
							{{ items.loading ? 'Loading...' : 'Load More' }}
						</button>
					</div>
				</div>

				<!-- Catalogue View -->
				<div v-else>
					<div v-if="catalogLoading" class="py-20 text-center">
						<div
							class="animate-spin rounded-full h-8 w-8 border-2 border-gray-900 dark:border-white border-t-transparent mx-auto mb-4"
						></div>
						<span class="text-gray-400 text-sm font-medium">Loading catalogue...</span>
					</div>

					<div v-else-if="categories.length === 0" class="py-20 text-center">
						<p class="text-gray-400 text-sm">No categories found.</p>
					</div>

					<div v-else class="space-y-8">
						<div v-for="cat in categories" :key="cat.name" class="mb-6">
							<div class="flex items-center justify-between mb-4">
								<h3 class="text-lg font-bold text-gray-900 dark:text-white">
									{{ cat.name }}
								</h3>
								<button
									@click="viewCategory(cat)"
									class="text-sm text-[#D4AF37] hover:underline font-medium"
								>
									View All
								</button>
							</div>
							<div class="smart-grid">
								<div v-for="item in cat.items" :key="item.item_code" class="group">
									<ItemCard
										:item="item"
										@quick-add="handleQuickAdd"
										@open-details="openItemDetails(item.item_code)"
									/>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Product Modal - Only on desktop (lg+) -->
		<ProductModal :show="showModal" :itemCode="selectedItemCode" @close="showModal = false" />

		<!-- Suspended Session Screen Lock Overlay -->
		<Teleport to="body">
			<Transition
				enter-active-class="transition-opacity duration-300"
				enter-from-class="opacity-0"
				enter-to-class="opacity-100"
				leave-active-class="transition-opacity duration-200"
				leave-from-class="opacity-100"
				leave-to-class="opacity-0"
			>
				<div
					v-if="
						posSession.hasActiveSession &&
						posSession.activeSession?.status === 'Suspended'
					"
					class="fixed inset-0 bg-black/75 backdrop-blur-md flex items-center justify-center z-[9999]"
				>
					<div
						class="bg-white dark:bg-warm-dark-800 p-10 rounded-2xl text-center max-w-md mx-4 shadow-2xl border border-amber-500/20"
					>
						<div
							class="w-20 h-20 bg-amber-500/10 border border-amber-500/30 rounded-full flex items-center justify-center mx-auto mb-6 text-amber-500 text-4xl animate-pulse"
						>
							🔒
						</div>
						<h2 class="premium-title !text-2xl mb-3">Register Suspended</h2>
						<p class="text-gray-500 dark:text-gray-400 text-sm mb-8 leading-relaxed">
							This cash register session is currently suspended (Floating Till).
							Please click the button below to resume your session and continue
							transactions.
						</p>
						<div class="flex flex-col gap-3">
							<button
								@click="handleResume"
								:disabled="sessionLoading"
								class="w-full px-8 py-3.5 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition shadow-lg active:scale-95 disabled:opacity-50"
							>
								<span v-if="sessionLoading">Resuming Session...</span>
								<span v-else>Resume POS Session</span>
							</button>
							<router-link
								to="/home"
								class="w-full px-8 py-3 bg-gray-100 dark:bg-warm-dark-700 text-gray-700 dark:text-gray-300 font-bold rounded-lg hover:bg-gray-200 dark:hover:bg-warm-dark-600 transition text-sm text-center"
							>
								Exit to Dashboard
							</router-link>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

		<!-- Register Controls & Reports slide-over drawer -->
		<Teleport to="body">
			<Transition
				enter-active-class="transition-opacity duration-300"
				enter-from-class="opacity-0"
				enter-to-class="opacity-100"
				leave-active-class="transition-opacity duration-200"
				leave-from-class="opacity-100"
				leave-to-class="opacity-0"
			>
				<div
					v-if="showRegisterActions"
					class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[999]"
					@click="showRegisterActions = false"
				>
					<div
						class="absolute right-0 top-0 bottom-0 w-full max-w-lg bg-white dark:bg-warm-dark-800 shadow-2xl p-6 overflow-y-auto flex flex-col gap-6"
						@click.stop
					>
						<div
							class="flex items-center justify-between pb-4 border-b dark:border-warm-border/50"
						>
							<div>
								<h2
									class="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wider"
								>
									Register Controls
								</h2>
								<p class="text-xs text-gray-400 mt-0.5 font-mono">
									Session: {{ posSession.activeSession?.name }}
								</p>
							</div>
							<button
								@click="showRegisterActions = false"
								class="text-gray-400 hover:text-gray-600 dark:hover:text-white font-bold text-xl"
							>
								✕
							</button>
						</div>

						<!-- Drawer Status & Threshold Alert -->
						<div class="premium-card p-5 bg-gray-50/50 dark:bg-warm-dark-700/30">
							<div class="flex items-center justify-between mb-4">
								<h3
									class="text-xs font-bold text-gray-500 uppercase tracking-wider"
								>
									Expected Drawer Balance
								</h3>
								<button
									@click="refreshDrawerBalance"
									:disabled="drawerLoading"
									class="text-xs text-[#D4AF37] hover:underline"
								>
									{{ drawerLoading ? 'Syncing...' : '↻ Sync' }}
								</button>
							</div>
							<div v-if="drawerBalance">
								<div class="flex justify-between items-baseline mb-2">
									<span
										class="text-2xl font-bold font-mono text-gray-950 dark:text-white"
									>
										${{
											Number(
												drawerBalance.expected_drawer_balance || 0
											).toFixed(2)
										}}
									</span>
									<span class="text-xs text-gray-400">
										Limit: ${{
											Number(drawerBalance.drawer_threshold || 0).toFixed(2)
										}}
									</span>
								</div>
								<div
									v-if="drawerBalance.exceeds_threshold"
									class="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-500 text-xs mb-3 flex items-start gap-2"
								>
									<span>⚠️</span>
									<div>
										<p class="font-bold">Drawer Cash Limit Exceeded</p>
										<p class="mt-0.5">{{ drawerBalance.alert_message }}</p>
									</div>
								</div>
								<div
									class="grid grid-cols-3 gap-2 text-xs text-gray-400 border-t dark:border-warm-border/50 pt-3 mt-2"
								>
									<div>
										<p class="text-[10px] uppercase font-bold text-gray-500">
											Opening
										</p>
										<p class="font-mono mt-0.5 font-bold">
											${{
												Number(drawerBalance.opening_float || 0).toFixed(2)
											}}
										</p>
									</div>
									<div>
										<p class="text-[10px] uppercase font-bold text-gray-500">
											Sales
										</p>
										<p class="font-mono mt-0.5 font-bold text-green-500">
											+${{
												Number(drawerBalance.cash_sales || 0).toFixed(2)
											}}
										</p>
									</div>
									<div>
										<p class="text-[10px] uppercase font-bold text-gray-500">
											Movements
										</p>
										<p class="font-mono mt-0.5 font-bold text-blue-500">
											{{ drawerBalance.net_movements >= 0 ? '+' : '' }}${{
												Number(drawerBalance.net_movements || 0).toFixed(2)
											}}
										</p>
									</div>
								</div>
							</div>
							<p v-else class="text-xs text-gray-400">Syncing drawer status...</p>
						</div>

						<!-- X Report Section -->
						<div class="border-t dark:border-warm-border/50 pt-4">
							<div class="flex items-center justify-between mb-3">
								<h3
									class="text-xs font-bold text-gray-500 uppercase tracking-wider"
								>
									Mid-Shift Snapshots (X-Report)
								</h3>
								<button
									@click="triggerXReport"
									:disabled="xReportLoading"
									class="px-3.5 py-1.5 bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 border border-[#D4AF37]/30 text-[#D4AF37] text-xs font-bold rounded-lg transition"
								>
									{{ xReportLoading ? 'Generating...' : 'Generate X-Report' }}
								</button>
							</div>

							<!-- Display X Report -->
							<div
								v-if="xReport"
								class="p-4 bg-gray-50 dark:bg-warm-dark-700/20 border border-gray-100 dark:border-warm-border rounded-xl text-xs space-y-4 font-sans max-h-80 overflow-y-auto"
							>
								<div
									class="flex justify-between border-b dark:border-warm-border/50 pb-2"
								>
									<strong class="uppercase text-amber-500"
										>MID-SHIFT X-REPORT</strong
									>
									<span class="text-gray-400"
										>Time: {{ formatDateTime(xReport.generated_at) }}</span
									>
								</div>

								<div class="grid grid-cols-2 gap-4">
									<div>
										<p class="text-gray-400 uppercase text-[9px] font-bold">
											Total Mid-Shift Sales
										</p>
										<p
											class="text-base font-bold font-mono text-gray-900 dark:text-white mt-0.5"
										>
											${{ Number(xReport.total_sales || 0).toFixed(2) }} ({{
												xReport.sales_count
											}}
											sales)
										</p>
									</div>
									<div>
										<p class="text-gray-400 uppercase text-[9px] font-bold">
											Expected Drawer Balance
										</p>
										<p
											class="text-base font-bold font-mono text-green-500 mt-0.5"
										>
											${{
												Number(
													xReport.expected_drawer_balance || 0
												).toFixed(2)
											}}
										</p>
									</div>
								</div>

								<div class="border-t dark:border-warm-border/50 pt-3">
									<h4
										class="font-bold text-gray-800 dark:text-gray-200 uppercase text-[10px] mb-2"
									>
										Payment Breakdown
									</h4>
									<div class="space-y-1.5">
										<div
											v-for="p in xReport.payment_summary"
											:key="p.mode_of_payment"
											class="flex justify-between border-b dark:border-warm-border/20 pb-1"
										>
											<span>{{ p.mode_of_payment }} (x{{ p.count }})</span>
											<span class="font-mono font-bold"
												>${{ Number(p.amount || 0).toFixed(2) }}</span
											>
										</div>
									</div>
								</div>

								<div
									v-if="xReport.cash_movements?.length > 0"
									class="border-t dark:border-warm-border/50 pt-3"
								>
									<h4
										class="font-bold text-gray-800 dark:text-gray-200 uppercase text-[10px] mb-2"
									>
										Cash Movements
									</h4>
									<div class="space-y-1.5">
										<div
											v-for="m in xReport.cash_movements"
											:key="m.name"
											class="flex justify-between text-gray-400"
										>
											<span>{{ m.movement_type }}: {{ m.reason }}</span>
											<span class="font-mono font-bold"
												>{{ m.movement_type === 'Cash In' ? '+' : '-' }}${{
													Number(m.amount || 0).toFixed(2)
												}}</span
											>
										</div>
									</div>
								</div>

								<button
									@click="printXReport"
									class="w-full py-2 bg-gray-100 dark:bg-warm-dark-700 hover:bg-gray-200 text-center font-bold text-xs rounded-lg transition"
								>
									🖨️ Print mid-shift snapshot
								</button>
							</div>
						</div>

						<!-- Manager-Only Variance Analysis -->
						<div v-if="isManager" class="border-t dark:border-warm-border/50 pt-4">
							<div class="flex items-center justify-between mb-3">
								<div>
									<h3
										class="text-xs font-bold text-gray-500 uppercase tracking-wider"
									>
										Variance Audit & History
									</h3>
									<p class="text-[10px] text-gray-400 mt-0.5">
										Dual manager controls & pattern detection
									</p>
								</div>
								<button
									@click="fetchVarianceReport"
									:disabled="varianceLoading"
									class="text-xs text-[#D4AF37] hover:underline"
								>
									{{ varianceLoading ? 'Analyzing...' : 'Analyze Patterns' }}
								</button>
							</div>

							<div
								v-if="varianceReport"
								class="p-4 bg-gray-50 dark:bg-warm-dark-700/20 border border-gray-100 dark:border-warm-border rounded-xl text-xs space-y-4"
							>
								<div class="grid grid-cols-3 gap-2 text-center text-gray-400">
									<div
										class="p-2 bg-emerald-500/5 rounded-lg border border-emerald-500/10"
									>
										<p class="text-[9px] uppercase font-bold text-gray-500">
											Balanced Closes
										</p>
										<p
											class="text-sm font-bold font-mono text-emerald-500 mt-0.5"
										>
											{{ varianceReport.balanced_count }}
										</p>
									</div>
									<div
										class="p-2 bg-red-500/5 rounded-lg border border-red-500/10"
									>
										<p class="text-[9px] uppercase font-bold text-gray-500">
											Shortage Closes
										</p>
										<p class="text-sm font-bold font-mono text-red-500 mt-0.5">
											{{ varianceReport.shortage_count }}
										</p>
									</div>
									<div
										class="p-2 bg-blue-500/5 rounded-lg border border-blue-500/10"
									>
										<p class="text-[9px] uppercase font-bold text-gray-500">
											Excess Closes
										</p>
										<p
											class="text-sm font-bold font-mono text-blue-500 mt-0.5"
										>
											{{ varianceReport.excess_count }}
										</p>
									</div>
								</div>

								<div
									class="flex justify-between items-center text-xs p-3 bg-gray-100/50 dark:bg-warm-dark-700/40 rounded-lg"
								>
									<span>Discrepancy Rate:</span>
									<span
										class="font-bold font-mono"
										:class="
											varianceReport.variance_rate_percent > 30
												? 'text-red-500 font-black'
												: 'text-gray-400'
										"
									>
										{{ varianceReport.variance_rate_percent }}%
									</span>
								</div>

								<div
									v-if="varianceReport.pattern !== 'normal'"
									class="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-500 text-xs flex items-center gap-2"
								>
									<span>🚨</span>
									<div>
										<p class="font-bold">Variance Pattern Alert!</p>
										<p class="mt-0.5">
											Cashier has
											<strong class="underline">{{
												varianceReport.pattern === 'consistent_shortages'
													? 'consistent shortages'
													: 'consistent excess amount'
											}}</strong>
											pattern across past closes.
										</p>
									</div>
								</div>

								<div
									v-if="varianceReport.variance_history?.length > 0"
									class="space-y-2 border-t dark:border-warm-border/30 pt-3"
								>
									<p class="text-[9px] uppercase font-bold text-gray-500 mb-1">
										Recent Closes
									</p>
									<div class="max-h-28 overflow-y-auto space-y-1">
										<div
											v-for="h in varianceReport.variance_history"
											:key="h.closing_entry"
											class="flex justify-between border-b dark:border-warm-border/10 pb-1 text-[11px]"
										>
											<span class="text-gray-400 font-mono">{{
												h.date
											}}</span>
											<span
												class="font-mono font-bold"
												:class="
													h.variance < 0
														? 'text-red-500'
														: h.variance > 0
														? 'text-blue-500'
														: 'text-green-500'
												"
											>
												{{ h.variance >= 0 ? '+' : '' }}${{
													Number(h.variance || 0).toFixed(2)
												}}
											</span>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
	</AppLayout>
</template>

<script setup>
/**
 * POS Page Component
 *
 * Main Point of Sale page displaying item catalog with filtering and search.
 * Refactored for mobile-first with 1-tap quick add.
 */

import AppLayout from '@/components/AppLayout.vue'
import ItemFilterBar from '@/components/ItemFilterBar.vue'
import ItemCard from '@/components/ItemCard.vue'
import ProductModal from '@/components/POSProductModal.vue'
import CashMovementModal from '@/components/CashMovementModal.vue'
import OfflineIndicator from '@/components/OfflineIndicator.vue'
import OfflineSyncModal from '@/components/OfflineSyncModal.vue'
import { useSessionStore } from '@/stores/session.js'
import { useUIStore } from '@/stores/ui.js'
import { useCartStore } from '@/stores/cart.js'
import { usePosSessionStore } from '@/stores/posSession.js'
import { useOfflineStore } from '@/stores/offline.js'
import { useBreakpoint } from '@/composables/useBreakpoint.js'
import { createResource } from 'frappe-ui'
import { watch, ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const session = useSessionStore()
const ui = useUIStore()
const cart = useCartStore()
const posSession = usePosSessionStore()
const offlineStore = useOfflineStore()
const { isMobile: isMobileBP, productGridCols } = useBreakpoint()

// View mode toggle
const viewMode = ref('pos')
const categories = ref([])
const catalogLoading = ref(false)
const sessionLoading = ref(false)

// Modal State - only used on desktop
const showModal = ref(false)
const selectedItemCode = ref(null)
const showCashModal = ref(false)
const showSyncModal = ref(false)
const showHeldDrawer = ref(false)
const heldCarts = ref([])

// Register Controls & Reports States
const showRegisterActions = ref(false)
const drawerBalance = ref(null)
const drawerLoading = ref(false)
const xReport = ref(null)
const xReportLoading = ref(false)
const varianceReport = ref(null)
const varianceLoading = ref(false)

const isManager = computed(() => {
	const roles = session.userRoles || []
	return (
		roles.includes('Sales Manager') ||
		roles.includes('Store Manager') ||
		roles.includes('System Manager') ||
		roles.includes('Administrator')
	)
})

// Detect mobile/tablet viewport via shared composable
const isMobile = computed(() => isMobileBP.value)

// Data State
const catalog = ref([])
const start = ref(0)
const PAGE_LENGTH = 50
const hasMore = ref(true)
const filteredItems = computed(() => {
	let items = [...(catalog.value || [])]
	const filters = ui.activeFilters.pos || {}
	return items
})

// Fetch Items Resource
const items = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		const f = ui.activeFilters.pos || {}
		const {
			in_stock_only,
			out_of_stock_only,
			price_min,
			price_max,
			custom_jewelry_type,
			custom_metal_type,
			custom_purity,
			custom_gemstone,
			display_case,
			...otherFilters
		} = f

		const params = {
			warehouse: session.currentWarehouse,
			display_case: display_case || undefined,
			page_length: PAGE_LENGTH,
			start: start.value,
			search_term: ui.searchQuery || undefined,
			filters: JSON.stringify({
				custom_jewelry_type: custom_jewelry_type || undefined,
				custom_metal_type: custom_metal_type || undefined,
				custom_purity: custom_purity || undefined,
				custom_gemstone: custom_gemstone || undefined,
				...otherFilters,
			}),
			in_stock_only: in_stock_only || false,
			out_of_stock_only: out_of_stock_only || false,
			min_price: price_min || undefined,
			max_price: price_max || undefined,
			sort_by: ui.sortBy.pos || undefined,
		}

		console.log('🔍 POS Items API Params:', params)
		console.log('🎯 Active Filters:', ui.activeFilters)

		return params
	},
	onSuccess(data) {
		console.log('✅ POS Items API Response:', data.length, 'items')
		if (data.length < PAGE_LENGTH) {
			hasMore.value = false
		}
		if (start.value === 0) {
			catalog.value = data
			// Cache catalog for offline browsing
			offlineStore.updateCatalogCache(data).catch(() => {})
		} else {
			catalog.value.push(...data)
		}
	},
	onError(error) {
		console.error('❌ POS Items API Error:', error)
	},
})

// Fetch Catalogue Resource
const catalogResource = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	makeParams() {
		return { page_length: 100, warehouse: session.currentWarehouse }
	},
	onSuccess(data) {
		const items = data.items || data || []
		const grouped = {}
		items.forEach((item) => {
			const cat = item.item_group || item.category || 'Other'
			if (!grouped[cat]) {
				grouped[cat] = { name: cat, items: [] }
			}
			if (grouped[cat].items.length < 8) {
				grouped[cat].items.push(item)
			}
		})
		categories.value = Object.values(grouped).slice(0, 6)
		catalogLoading.value = false
	},
})

function loadCatalog() {
	catalogLoading.value = true
	catalogResource.fetch()
}

function showCatalogView() {
	viewMode.value = 'catalog'
	loadCatalog()
}

// Actions
function loadMore() {
	if (!hasMore.value || items.loading) return
	start.value += PAGE_LENGTH
	items.fetch()
}

function openItemDetails(itemCode) {
	selectedItemCode.value = itemCode
	showModal.value = true
}

function handleQuickAdd(item) {
	cart.addItem(item)
}

function onCashMovementSaved() {
	showCashModal.value = false
	posSession.fetchStatus()
}

async function handleSuspend() {
	if (!confirm('Are you sure you want to suspend this register session? (Floating Till)')) return
	sessionLoading.value = true
	try {
		const success = await posSession.suspendSession()
		if (success) {
			console.log('Session suspended')
		} else {
			alert(posSession.error || 'Failed to suspend session')
		}
	} catch (e) {
		console.error(e)
	} finally {
		sessionLoading.value = false
	}
}

async function handleResume() {
	sessionLoading.value = true
	try {
		const success = await posSession.resumeSession()
		if (success) {
			console.log('Session resumed')
		} else {
			alert(posSession.error || 'Failed to resume session')
		}
	} catch (e) {
		console.error(e)
	} finally {
		sessionLoading.value = false
	}
}

async function openRegisterActionsDrawer() {
	showRegisterActions.value = true
	await refreshDrawerBalance()
}

async function refreshDrawerBalance() {
	if (!posSession.activeSession?.name) return
	drawerLoading.value = true
	try {
		const res = await fetch(
			`/api/method/zevar_core.api.pos_session.get_drawer_balance?session_name=${posSession.activeSession.name}`,
			{
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
			}
		)
		const json = await res.json()
		if (json.message) {
			drawerBalance.value = json.message
		}
	} catch (e) {
		console.error('Failed to sync drawer balance:', e)
	} finally {
		drawerLoading.value = false
	}
}

async function triggerXReport() {
	if (!posSession.activeSession?.name) return
	xReportLoading.value = true
	try {
		const res = await fetch(
			`/api/method/zevar_core.api.pos_session.generate_x_report?session_name=${posSession.activeSession.name}`,
			{
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
			}
		)
		const json = await res.json()
		if (json.message) {
			xReport.value = json.message
		}
	} catch (e) {
		console.error('Failed to generate X report:', e)
	} finally {
		xReportLoading.value = false
	}
}

function formatDateTime(val) {
	if (!val) return ''
	const d = new Date(val)
	return (
		d.toLocaleDateString() +
		' ' +
		d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
	)
}

function printXReport() {
	if (!xReport.value) return
	const p = xReport.value
	const printWindow = window.open('', '_blank')

	let paymentsHtml = ''
	if (p.payment_summary) {
		p.payment_summary.forEach((pymt) => {
			paymentsHtml += `<tr><td style="padding:6px 0;">${pymt.mode_of_payment} (x${
				pymt.count
			})</td><td style="text-align:right; font-family:monospace;">$${Number(
				pymt.amount || 0
			).toFixed(2)}</td></tr>`
		})
	}

	let movementsHtml = ''
	if (p.cash_movements) {
		p.cash_movements.forEach((m) => {
			movementsHtml += `<tr><td style="padding:6px 0;">${m.movement_type}: ${
				m.reason
			}</td><td style="text-align:right; font-family:monospace;">${
				m.movement_type === 'Cash In' ? '+' : '-'
			}$${Number(m.amount || 0).toFixed(2)}</td></tr>`
		})
	}

	printWindow.document.write(`
		<html>
		<head>
			<title>X-Report - Mid-Shift Snapshot</title>
			<style>
				body { font-family: 'Inter', sans-serif; color: #1e1e1e; margin: 40px; }
				.header { border-bottom: 2px solid #D4AF37; padding-bottom: 15px; margin-bottom: 20px; }
				.title { font-size: 20px; font-weight: bold; letter-spacing: 1px; color: #b5952f; }
				.meta { font-size: 11px; color: #666; margin-top: 5px; }
				.section { margin-bottom: 25px; }
				.section-title { font-size: 12px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 10px; text-transform: uppercase; color: #555; }
				table { width: 100%; border-collapse: collapse; font-size: 13px; }
				.highlight { font-size: 16px; font-weight: bold; color: #111; }
			</style>
		</head>
		<body>
			<div class="header">
				<div class="title">MID-SHIFT X-REPORT</div>
				<div class="meta">
					Session: \${p.session_name}<br>
					User: \${p.user}<br>
					Generated: \${formatDateTime(p.generated_at)}
				</div>
			</div>
			
			<div class="section">
				<table style="font-size:14px; font-weight:bold;">
					<tr>
						<td>Total Mid-Shift Sales (\${p.sales_count} invoices)</td>
						<td style="text-align:right; font-family:monospace;" class="highlight">$\${Number(p.total_sales || 0).toFixed(2)}</td>
					</tr>
					<tr>
						<td>Expected Cash Drawer Balance</td>
						<td style="text-align:right; font-family:monospace; color:green;" class="highlight">$\${Number(p.expected_drawer_balance || 0).toFixed(2)}</td>
					</tr>
				</table>
			</div>

			<div class="section">
				<div class="section-title">Payments Summary</div>
				<table>
					\${paymentsHtml || '<tr><td colspan="2" style="color:#666;">No sales registered yet in this shift.</td></tr>'}
				</table>
			</div>

			<div class="section">
				<div class="section-title">Cash Movements</div>
				<table>
					\${movementsHtml || '<tr><td colspan="2" style="color:#666;">No movements registered.</td></tr>'}
				</table>
			</div>

			<script>
				window.onload = function() { window.print(); window.close(); }
			<\/script>
		<\/body>
		<\/html>
	`)
	printWindow.document.close()
}

async function fetchVarianceReport() {
	varianceLoading.value = true
	try {
		const res = await fetch(
			`/api/method/zevar_core.api.pos_session.get_cashier_variance_report`,
			{
				headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
			}
		)
		const json = await res.json()
		if (json.message) {
			varianceReport.value = json.message
		}
	} catch (e) {
		console.error('Failed to fetch variance report:', e)
	} finally {
		varianceLoading.value = false
	}
}

// ── Held Carts ──
async function fetchHeldCarts() {
	try {
		const res = await fetch('/api/method/zevar_core.api.pos.get_held_carts', {
			method: 'GET',
			headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
		})
		const data = await res.json()
		heldCarts.value = data.message?.carts || []
	} catch (e) {
		heldCarts.value = []
	}
}

function toggleHeldCarts() {
	fetchHeldCarts()
	showHeldDrawer.value = !showHeldDrawer.value
}

async function recallHeldCart(cartId) {
	try {
		const res = await fetch('/api/method/zevar_core.api.pos.recall_cart', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({ cart_id: cartId }),
		})
		const data = await res.json()
		if (data.message?.success) {
			const recalledCart = data.message.cart
			// Clear current cart and restore held items
			cart.clearCart()
			cart.clearCustomer()
			for (const item of recalledCart.items || []) {
				cart.addItem(item)
			}
			if (recalledCart.customer) {
				cart.setCustomer({
					name: recalledCart.customer,
					customer_name: recalledCart.customer_name,
				})
			}
			showHeldDrawer.value = false
			fetchHeldCarts()
		}
	} catch (e) {
		console.error('Recall failed:', e)
	}
}

async function discardHeldCart(cartId) {
	try {
		await fetch('/api/method/zevar_core.api.pos.discard_held_cart', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.csrf_token || '',
			},
			body: JSON.stringify({ cart_id: cartId }),
		})
		fetchHeldCarts()
	} catch (e) {
		console.error('Discard failed:', e)
	}
}

function viewCategory(cat) {
	router.push(`/pos-catalogue/${encodeURIComponent(cat.name)}`)
}

// Watchers
let searchTimeout = null

watch(
	() => ({
		search: ui.searchQuery,
		filters: JSON.stringify(ui.activeFilters.pos),
		sort: ui.sortBy.pos,
	}),
	() => {
		if (searchTimeout) clearTimeout(searchTimeout)
		searchTimeout = setTimeout(() => {
			start.value = 0
			hasMore.value = true
			items.fetch()
		}, 400)
	},
	{ deep: true }
)

watch(
	() => session.currentWarehouse,
	(newVal) => {
		if (newVal) {
			start.value = 0
			items.fetch()
		} else {
			catalog.value = []
		}
	},
	{ immediate: true }
)

let sessionPollInterval = null

// Debounced catalog refresh for stock updates from other terminals
let stockRefreshTimeout = null
function handleStockUpdate(data) {
	// Only refresh if the update affects our warehouse or is a broadcast
	if (
		data?.warehouse &&
		session.currentWarehouse &&
		data.warehouse !== session.currentWarehouse
	) {
		return
	}
	// Debounce: wait 2s to batch rapid-fire updates
	if (stockRefreshTimeout) clearTimeout(stockRefreshTimeout)
	stockRefreshTimeout = setTimeout(() => {
		start.value = 0
		hasMore.value = true
		items.fetch()
	}, 2000)
}

onMounted(() => {
	posSession.fetchStatus()
	sessionPollInterval = setInterval(() => posSession.fetchStatus(), 60000)
	fetchHeldCarts() // Load held carts count on mount
	offlineStore.init() // Start online/offline event listeners

	// Listen for real-time stock updates from other POS terminals
	if (window.frappe?.realtime) {
		window.frappe.realtime.on('stock_update', handleStockUpdate)
	} else if (window.frappe?.socketio) {
		window.frappe.socketio.socket?.on('stock_update', handleStockUpdate)
	}

	// Refresh catalog when offline store detects staleness (30-min TTL)
	window.addEventListener('zevar:catalog-stale', () => {
		if (offlineStore.isOnline) {
			catalog.value = []
			start.value = 0
			hasMore.value = true
			items.fetch()
		}
	})

	// Listen for service worker sync completion to refresh pending count
	if ('serviceWorker' in navigator) {
		navigator.serviceWorker.addEventListener('message', (event) => {
			if (event.data?.type === 'SYNC_COMPLETE') {
				offlineStore.refreshPendingCount()
			}
		})
	}
})
onUnmounted(() => {
	if (sessionPollInterval) clearInterval(sessionPollInterval)
	if (stockRefreshTimeout) clearTimeout(stockRefreshTimeout)
	offlineStore.destroy() // Remove online/offline listeners

	// Clean up realtime listener
	if (window.frappe?.realtime) {
		window.frappe.realtime.off('stock_update', handleStockUpdate)
	} else if (window.frappe?.socketio) {
		window.frappe.socketio.socket?.off('stock_update', handleStockUpdate)
	}
})
</script>

<style scoped>
.smart-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
	gap: 0.5rem;
}

@media (min-width: 640px) {
	.smart-grid {
		grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
		gap: 0.75rem;
	}
}

@media (min-width: 1024px) {
	.smart-grid {
		grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
		gap: 0.75rem;
	}
}
</style>
