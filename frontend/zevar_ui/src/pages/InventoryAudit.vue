<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<!-- Header -->
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<div class="flex items-center gap-3">
					<h2 class="premium-title !text-xl sm:!text-2xl">Inventory Audit</h2>
					<span
						v-if="auditStore.activeSession"
						class="status-label !mb-0 !px-4 !py-1 !rounded-full !border"
						:class="statusClasses"
					>
						{{ auditStore.activeSession.status }}
					</span>
				</div>
				<div class="flex items-center gap-2">
					<button
						v-if="currentView === 'scanning'"
						class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-gray-200 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors"
						@click="currentView = 'history'"
					>
						History
					</button>
					<button
						v-if="currentView !== 'launcher'"
						class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-gray-200 dark:border-warm-border hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors"
						@click="goToLauncher"
					>
						+ New Audit
					</button>
				</div>
			</div>

			<!-- Launcher View -->
			<div v-if="currentView === 'launcher'" class="flex-1 overflow-y-auto min-h-0">
				<div class="max-w-3xl mx-auto space-y-6">
					<!-- Dashboard Cards -->
					<div v-if="auditStore.dashboard" class="grid grid-cols-2 md:grid-cols-4 gap-3">
						<div class="premium-card !p-4 text-center">
							<div
								class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
							>
								Next Audit
							</div>
							<div class="text-sm font-bold text-gray-900 dark:text-white">
								{{
									auditStore.dashboard.next_audit
										? formatDate(auditStore.dashboard.next_audit.scheduled_for)
										: 'None scheduled'
								}}
							</div>
							<div
								v-if="auditStore.dashboard.next_audit"
								class="text-[10px] text-gray-400"
							>
								{{ auditStore.dashboard.next_audit.scope }}
							</div>
						</div>
						<div
							class="premium-card !p-4 text-center"
							:class="
								auditStore.dashboard.overdue_audits > 0
									? '!border-red-300 dark:!border-red-800'
									: ''
							"
						>
							<div
								class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
							>
								Overdue
							</div>
							<div
								class="text-xl font-bold"
								:class="
									auditStore.dashboard.overdue_audits > 0
										? 'text-red-500'
										: 'text-green-600'
								"
							>
								{{ auditStore.dashboard.overdue_audits }}
							</div>
						</div>
						<div class="premium-card !p-4 text-center">
							<div
								class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
							>
								30-Day Shrinkage
							</div>
							<div
								class="text-sm font-bold"
								:class="
									auditStore.dashboard.shrinkage_last_30_days > 0
										? 'text-red-500'
										: 'text-green-600'
								"
							>
								{{ formatCurrency(auditStore.dashboard.shrinkage_last_30_days) }}
							</div>
						</div>
						<div class="premium-card !p-4 text-center">
							<div
								class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
							>
								Audit Hit Rate
							</div>
							<div class="text-xl font-bold text-[#D4AF37]">
								{{ auditStore.dashboard.audit_hit_rate }}%
							</div>
						</div>
					</div>

					<!-- Frozen Store Warning -->
					<div
						v-if="auditStore.dashboard?.frozen_stores?.length"
						class="premium-card !p-4 !border-red-300 bg-red-50 dark:bg-red-900/20"
					>
						<div class="flex items-center gap-3">
							<div class="text-red-500 text-xl font-bold">!</div>
							<div>
								<div class="text-sm font-bold text-red-700 dark:text-red-400">
									Store Frozen
								</div>
								<div class="text-xs text-red-600 dark:text-red-400">
									{{ auditStore.dashboard.frozen_stores[0].reason }} &mdash;
									Reservations and transfers are blocked.
								</div>
							</div>
						</div>
					</div>

					<!-- Start from Audit Plan -->
					<div v-if="auditStore.auditPlans.length" class="premium-card !p-6">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
							Scheduled Audits
						</h3>
						<div class="space-y-2">
							<div
								v-for="plan in auditStore.auditPlans"
								:key="plan.name"
								class="flex items-center justify-between p-3 rounded-lg border border-gray-100 dark:border-warm-border/50 hover:bg-gray-50 dark:hover:bg-warm-dark-700 cursor-pointer transition-colors"
								@click="startFromPlan(plan)"
							>
								<div>
									<div
										class="text-sm font-semibold text-gray-900 dark:text-white"
									>
										{{ plan.scope }}
									</div>
									<div class="text-xs text-gray-500">
										{{ plan.store_location }} &middot;
										{{ formatDate(plan.scheduled_for) }}
									</div>
								</div>
								<button
									class="px-3 py-1.5 text-xs font-bold rounded-lg bg-gradient-to-r from-[#D4AF37] to-[#F2E6A0] text-gray-900"
								>
									Start
								</button>
							</div>
						</div>
					</div>

					<!-- Start New Audit -->
					<div class="premium-card !p-6">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
							Start New Audit
						</h3>
						<div class="space-y-4">
							<div>
								<label
									class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1"
								>
									Audit Scope
								</label>
								<select
									v-model="selectedScope"
									class="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-warm-dark-700 text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
								>
									<option value="Spot">Spot Check (Single Case)</option>
									<option value="Showcase">Showcase Audit (Full Case)</option>
									<option value="Backstock">Backstock / Safe Audit</option>
									<option value="Full Store">Full Store Reconciliation</option>
								</select>
							</div>
							<div>
								<label
									class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1"
								>
									{{
										selectedScope === 'Spot' || selectedScope === 'Showcase'
											? 'Display Case'
											: 'Store / Warehouse'
									}}
								</label>
								<select
									v-model="selectedWarehouse"
									class="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-warm-dark-700 text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
								>
									<option value="">Select...</option>
									<option
										v-for="wh in scopeWarehouses"
										:key="wh.name"
										:value="wh.name"
									>
										{{ wh.name }}
									</option>
								</select>
							</div>
							<div>
								<label
									class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1"
								>
									Notes (optional)
								</label>
								<textarea
									v-model="auditNotes"
									rows="2"
									class="w-full px-4 py-2.5 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-warm-dark-700 text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 resize-none"
									placeholder="e.g. Annual Q2 count, After theft incident..."
								></textarea>
							</div>
							<button
								:disabled="
									!selectedWarehouse || auditStore.startAuditResource.loading
								"
								class="w-full py-3 rounded-lg bg-gradient-to-r from-[#D4AF37] to-[#F2E6A0] text-gray-900 font-bold text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all"
								@click="handleStartAudit"
							>
								{{
									auditStore.startAuditResource.loading
										? 'Starting...'
										: `Start ${selectedScope} Audit`
								}}
							</button>
						</div>
					</div>

					<!-- Resume Draft -->
					<div v-if="draftSessions.length" class="premium-card !p-6">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
							Resume Draft
						</h3>
						<div class="space-y-2">
							<div
								v-for="session in draftSessions"
								:key="session.name"
								class="flex items-center justify-between p-3 rounded-lg border border-gray-100 dark:border-warm-border/50 hover:bg-gray-50 dark:hover:bg-warm-dark-700 cursor-pointer transition-colors"
								@click="handleResume(session.name)"
							>
								<div>
									<div
										class="text-sm font-semibold text-gray-900 dark:text-white"
									>
										{{ session.name }}
									</div>
									<div class="text-xs text-gray-500">
										{{ session.store_location }} &middot;
										{{ formatCount(session.scanned_count) }}/{{
											formatCount(session.expected_count)
										}}
										scanned
									</div>
								</div>
								<span
									class="text-xs font-semibold text-amber-500 bg-amber-50 dark:bg-amber-900/20 px-2 py-0.5 rounded"
								>
									{{ session.status }}
								</span>
							</div>
						</div>
					</div>

					<!-- Recent History -->
					<div class="premium-card !p-6">
						<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">
							Recent Audits
						</h3>
						<button
							class="text-sm text-[#D4AF37] font-semibold hover:underline"
							@click="currentView = 'history'"
						>
							View all audit history &rarr;
						</button>
					</div>
				</div>
			</div>

			<!-- Scanning View -->
			<div v-else-if="currentView === 'scanning'" class="flex-1 min-h-0">
				<div class="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-6">
					<!-- Left Column: Scan Interface -->
					<div class="flex flex-col min-h-0 overflow-y-auto">
						<!-- Scan Mode Toggle -->
						<div class="flex items-center gap-3 mb-4 flex-shrink-0">
							<button
								class="px-4 py-2 text-xs font-bold rounded-lg transition-colors"
								:class="
									auditStore.scanMode === 'barcode'
										? 'bg-[#D4AF37] text-gray-900'
										: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-400'
								"
								@click="auditStore.scanMode = 'barcode'"
							>
								Barcode Scanner
							</button>
							<button
								class="px-4 py-2 text-xs font-bold rounded-lg transition-colors"
								:class="
									auditStore.scanMode === 'rfid'
										? 'bg-[#D4AF37] text-gray-900'
										: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-400'
								"
								@click="auditStore.scanMode = 'rfid'"
							>
								RFID Batch
							</button>
							<div class="flex-1"></div>
							<button
								class="p-2 rounded-lg border border-gray-200 dark:border-warm-border text-xs"
								:class="audioEnabled ? 'text-green-600' : 'text-gray-400'"
								@click="audioEnabled = !audioEnabled"
								title="Toggle scan audio feedback"
							>
								<svg
									class="w-4 h-4"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										v-if="audioEnabled"
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15.536 8.464a5 5 0 010 7.072M17.95 6.05a8 8 0 010 11.9M6.5 8.8l4.2-3.15A1 1 0 0112 6.5v11a1 1 0 01-1.3.95L6.5 15.2H4a1 1 0 01-1-1v-4.4a1 1 0 011-1h2.5z"
									/>
									<path
										v-else
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
									/>
								</svg>
							</button>
						</div>

						<!-- Barcode Input -->
						<div v-if="auditStore.scanMode === 'barcode'" class="mb-4 flex-shrink-0">
							<input
								ref="barcodeInput"
								v-model="barcodeBuffer"
								type="text"
								class="w-full px-4 py-3 rounded-lg border-2 text-sm font-mono focus:outline-none transition-colors"
								:class="lastScanColor"
								placeholder="Scan barcode or tap here to type..."
								autocomplete="off"
								@keydown.enter="handleBarcodeSubmit"
								@blur="refocusInput"
							/>
							<div
								v-if="auditStore.lastScanResult"
								class="mt-2 p-3 rounded-lg text-sm font-semibold"
								:class="scanResultClasses"
							>
								{{ scanResultMessage }}
							</div>
						</div>

						<!-- RFID Batch Input -->
						<div v-else class="mb-4 flex-shrink-0">
							<textarea
								v-model="rfidBatch"
								rows="6"
								class="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-warm-dark-700 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 resize-none"
								placeholder="Paste RFID EPCs here, one per line..."
							></textarea>
							<button
								:disabled="
									!rfidBatch.trim() || auditStore.batchScanResource.loading
								"
								class="mt-2 w-full py-2.5 rounded-lg bg-gradient-to-r from-[#D4AF37] to-[#F2E6A0] text-gray-900 font-bold text-sm disabled:opacity-50"
								@click="handleBatchSubmit"
							>
								{{
									auditStore.batchScanResource.loading
										? 'Processing...'
										: 'Submit Batch (' + rfidLineCount + ' EPCs)'
								}}
							</button>
						</div>

						<!-- Live Scan Feed -->
						<div class="flex-1 overflow-y-auto min-h-0">
							<div class="space-y-2">
								<div
									v-for="(scan, idx) in auditStore.scanFeed"
									:key="idx"
									class="flex items-center gap-3 p-3 rounded-lg border transition-all"
									:class="scanCardClasses(scan.match_status)"
								>
									<div
										class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
										:class="scanIconClass(scan.match_status)"
									>
										{{ scanIcon(scan.match_status) }}
									</div>
									<div class="flex-1 min-w-0">
										<div
											class="text-sm font-semibold text-gray-900 dark:text-white truncate"
										>
											{{
												scan.item_name || scan.barcode_or_epc || 'Unknown'
											}}
										</div>
										<div class="text-xs text-gray-500 truncate">
											{{ scan.item_code || '' }}
											<span v-if="scan.valuation_rate"
												>&middot;
												{{ formatCurrency(scan.valuation_rate) }}</span
											>
										</div>
									</div>
									<span
										class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded"
										:class="scanBadgeClass(scan.match_status)"
									>
										{{ scan.match_status }}
									</span>
								</div>
								<div
									v-if="!auditStore.scanFeed.length"
									class="text-center py-12 text-gray-400 text-sm"
								>
									No scans yet. Start scanning items above.
								</div>
							</div>
						</div>

						<!-- Discrepancy Section -->
						<div
							v-if="
								auditStore.missingItems.length || auditStore.unexpectedItems.length
							"
							class="mt-4 flex-shrink-0"
						>
							<div class="flex gap-2 mb-3">
								<button
									class="px-3 py-1.5 text-xs font-bold rounded-lg"
									:class="
										discrepancyTab === 'missing'
											? 'bg-amber-100 text-amber-700'
											: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-500'
									"
									@click="discrepancyTab = 'missing'"
								>
									Missing ({{ auditStore.missingItems.length }})
								</button>
								<button
									class="px-3 py-1.5 text-xs font-bold rounded-lg"
									:class="
										discrepancyTab === 'unexpected'
											? 'bg-red-100 text-red-700'
											: 'bg-gray-100 dark:bg-warm-dark-700 text-gray-500'
									"
									@click="discrepancyTab = 'unexpected'"
								>
									Unexpected ({{ auditStore.unexpectedItems.length }})
								</button>
							</div>
							<!-- Missing Items Table -->
							<div
								v-if="discrepancyTab === 'missing'"
								class="premium-card !p-0 overflow-hidden"
							>
								<table class="w-full text-xs">
									<thead>
										<tr
											class="bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800/50"
										>
											<th
												class="text-left px-3 py-2 font-bold text-amber-700"
											>
												Item
											</th>
											<th
												class="text-center px-3 py-2 font-bold text-amber-700"
											>
												Expected
											</th>
											<th
												class="text-center px-3 py-2 font-bold text-amber-700"
											>
												Scanned
											</th>
											<th
												class="text-right px-3 py-2 font-bold text-amber-700"
											>
												Value
											</th>
										</tr>
									</thead>
									<tbody>
										<tr
											v-for="item in auditStore.missingItems"
											:key="item.item_code"
											class="border-b border-gray-100 dark:border-warm-border/30"
										>
											<td
												class="px-3 py-2 font-semibold text-gray-900 dark:text-white"
											>
												{{ item.item_name || item.item_code }}
											</td>
											<td class="px-3 py-2 text-center">
												{{ item.expected_qty }}
											</td>
											<td
												class="px-3 py-2 text-center text-amber-600 font-bold"
											>
												{{ item.scanned_qty }}
											</td>
											<td class="px-3 py-2 text-right">
												{{ formatCurrency(item.valuation_rate || 0) }}
											</td>
										</tr>
									</tbody>
								</table>
							</div>
							<!-- Unexpected Items Table -->
							<div
								v-if="discrepancyTab === 'unexpected'"
								class="premium-card !p-0 overflow-hidden"
							>
								<table class="w-full text-xs">
									<thead>
										<tr
											class="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800/50"
										>
											<th class="text-left px-3 py-2 font-bold text-red-700">
												Item
											</th>
											<th class="text-left px-3 py-2 font-bold text-red-700">
												Code
											</th>
											<th class="text-left px-3 py-2 font-bold text-red-700">
												EPC/Barcode
											</th>
										</tr>
									</thead>
									<tbody>
										<tr
											v-for="(item, idx) in auditStore.unexpectedItems"
											:key="idx"
											class="border-b border-gray-100 dark:border-warm-border/30"
										>
											<td
												class="px-3 py-2 font-semibold text-gray-900 dark:text-white"
											>
												{{ item.item_name || 'Unknown' }}
											</td>
											<td class="px-3 py-2 text-gray-500">
												{{ item.item_code || '-' }}
											</td>
											<td
												class="px-3 py-2 text-gray-500 font-mono text-[10px]"
											>
												{{ item.barcode_or_epc }}
											</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>
					</div>

					<!-- Right Column: Progress Dashboard -->
					<div class="flex flex-col min-h-0 overflow-y-auto pr-2 custom-scrollbar">
						<!-- Progress Bar -->
						<div class="premium-card !p-4 mb-4 flex-shrink-0">
							<div class="flex items-center justify-between mb-2">
								<span
									class="text-xs font-bold text-gray-500 uppercase tracking-wider"
									>Progress</span
								>
								<span class="text-sm font-bold text-gray-900 dark:text-white"
									>{{ auditStore.progressPercent }}%</span
								>
							</div>
							<div
								class="w-full h-3 bg-gray-100 dark:bg-warm-dark-700 rounded-full overflow-hidden"
							>
								<div
									class="h-full rounded-full bg-gradient-to-r from-[#D4AF37] to-[#F2E6A0] transition-all duration-500"
									:style="{ width: auditStore.progressPercent + '%' }"
								></div>
							</div>
							<div class="flex justify-between mt-1 text-[10px] text-gray-400">
								<span
									>{{
										auditStore.activeSession?.scanned_count || 0
									}}
									scanned</span
								>
								<span
									>{{
										auditStore.activeSession?.expected_count || 0
									}}
									expected</span
								>
							</div>
						</div>

						<!-- Stat Cards -->
						<div class="grid grid-cols-2 gap-3 mb-4 flex-shrink-0">
							<div class="premium-card !p-3">
								<div
									class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
								>
									Matched
								</div>
								<div class="text-xl font-bold text-green-600">
									{{ auditStore.counts.matched }}
								</div>
							</div>
							<div class="premium-card !p-3">
								<div
									class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
								>
									Unexpected
								</div>
								<div class="text-xl font-bold text-red-500">
									{{ auditStore.counts.unexpected }}
								</div>
							</div>
							<div class="premium-card !p-3">
								<div
									class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
								>
									Missing
								</div>
								<div class="text-xl font-bold text-amber-500">
									{{ auditStore.missingItems.length }}
								</div>
							</div>
							<div class="premium-card !p-3">
								<div
									class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
								>
									Duplicates
								</div>
								<div class="text-xl font-bold text-gray-400">
									{{ auditStore.counts.duplicates }}
								</div>
							</div>
						</div>

						<!-- Value Tracking -->
						<div class="premium-card !p-4 mb-4 flex-shrink-0">
							<div
								class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-3"
							>
								Value Tracking
							</div>
							<div class="space-y-2">
								<div class="flex justify-between text-xs">
									<span class="text-gray-500">Expected Value</span>
									<span class="font-bold text-gray-900 dark:text-white">{{
										formatCurrency(
											auditStore.activeSession?.total_value_expected || 0
										)
									}}</span>
								</div>
								<div class="flex justify-between text-xs">
									<span class="text-gray-500">Scanned Value</span>
									<span class="font-bold text-gray-900 dark:text-white">{{
										formatCurrency(
											auditStore.progress?.session?.total_value_scanned || 0
										)
									}}</span>
								</div>
								<hr class="border-gray-200 dark:border-warm-border/50" />
								<div class="flex justify-between text-xs">
									<span class="text-gray-500">Variance ($)</span>
									<span class="font-bold" :class="valueDiscrepancyColor">{{
										formatCurrency(
											Math.abs(
												auditStore.progress?.session
													?.variance_dollar_total ||
													auditStore.progress?.session
														?.total_value_discrepancy ||
													0
											)
										)
									}}</span>
								</div>
							</div>
						</div>

						<!-- Last Scanned Item Detail -->
						<div v-if="lastScanDetail" class="premium-card !p-4 mb-4 flex-shrink-0">
							<div
								class="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-2"
							>
								Last Scanned
							</div>
							<div class="flex items-center gap-3">
								<div
									v-if="lastScanDetail.item_image"
									class="w-12 h-12 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0"
								>
									<img
										:src="lastScanDetail.item_image"
										class="w-full h-full object-cover"
									/>
								</div>
								<div class="min-w-0">
									<div
										class="text-sm font-bold text-gray-900 dark:text-white truncate"
									>
										{{ lastScanDetail.item_name || 'Unknown' }}
									</div>
									<div class="text-xs text-gray-500">
										{{ lastScanDetail.item_code }}
									</div>
									<div
										v-if="lastScanDetail.valuation_rate"
										class="text-xs font-bold text-[#D4AF37] mt-0.5"
									>
										{{ formatCurrency(lastScanDetail.valuation_rate) }}
									</div>
								</div>
							</div>
						</div>

						<!-- Action Buttons -->
						<div class="space-y-2 mt-auto pt-4 flex-shrink-0">
							<!-- Two-Person Sign-Off -->
							<div v-if="showSignOffField" class="mb-2">
								<label
									class="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1"
									>Manager Sign-Off</label
								>
								<select
									v-model="signOffUser"
									class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-warm-dark-700 text-xs"
								>
									<option value="">Select manager...</option>
									<option
										v-for="u in managerUsers"
										:key="u.name"
										:value="u.name"
									>
										{{ u.full_name || u.name }}
									</option>
								</select>
							</div>

							<button
								:disabled="
									!auditStore.isActive ||
									auditStore.finalizeResource.loading ||
									(showSignOffField && !signOffUser)
								"
								class="w-full py-2.5 rounded-lg bg-gradient-to-r from-[#D4AF37] to-[#F2E6A0] text-gray-900 font-bold text-sm disabled:opacity-50"
								@click="handleFinalize"
							>
								{{
									auditStore.finalizeResource.loading
										? 'Finalizing...'
										: 'Finalize Audit'
								}}
							</button>
							<div class="flex gap-2">
								<button
									:disabled="!auditStore.isActive"
									class="flex-1 py-2 rounded-lg border border-red-200 text-red-600 font-semibold text-xs disabled:opacity-50 hover:bg-red-50 transition-colors"
									@click="handleCancel"
								>
									Cancel
								</button>
								<button
									class="flex-1 py-2 rounded-lg border border-gray-200 dark:border-warm-border text-gray-600 font-semibold text-xs disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors"
									@click="exportPDF"
								>
									PDF Report
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- History View -->
			<div v-else-if="currentView === 'history'" class="flex-1 overflow-y-auto min-h-0">
				<div class="premium-card !p-0 overflow-hidden">
					<table class="w-full text-sm">
						<thead>
							<tr
								class="bg-gray-50 dark:bg-warm-dark-700 border-b border-gray-200 dark:border-warm-border/50"
							>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Session
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Store
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Scope
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Status
								</th>
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Expected
								</th>
								<th
									class="text-center px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Scanned
								</th>
								<th
									class="text-right px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Variance
								</th>
								<th
									class="text-left px-4 py-3 text-[10px] font-bold text-gray-500 uppercase tracking-wider"
								>
									Started
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="session in historySessions"
								:key="session.name"
								class="border-b border-gray-100 dark:border-warm-border/30 hover:bg-gray-50 dark:hover:bg-warm-dark-700 cursor-pointer"
								@click="viewSessionResults(session)"
							>
								<td class="px-4 py-3 font-semibold text-gray-900 dark:text-white">
									{{ session.name }}
								</td>
								<td class="px-4 py-3 text-gray-500">
									{{ session.store_location }}
								</td>
								<td class="px-4 py-3">
									<span
										class="text-xs font-semibold px-2 py-0.5 rounded bg-gray-100 dark:bg-warm-dark-700"
										>{{ session.scope || 'Spot' }}</span
									>
								</td>
								<td class="px-4 py-3">
									<span
										class="text-xs font-bold px-2 py-0.5 rounded"
										:class="historyStatusClass(session.status)"
									>
										{{ session.status }}
									</span>
								</td>
								<td class="px-4 py-3 text-center">{{ session.expected_count }}</td>
								<td class="px-4 py-3 text-center">{{ session.scanned_count }}</td>
								<td
									class="px-4 py-3 text-right font-semibold"
									:class="
										(session.variance_dollar_total ||
											session.total_value_discrepancy ||
											0) > 0
											? 'text-red-500'
											: 'text-green-600'
									"
								>
									{{
										formatCurrency(
											Math.abs(
												session.variance_dollar_total ||
													session.total_value_discrepancy ||
													0
											)
										)
									}}
								</td>
								<td class="px-4 py-3 text-xs text-gray-500">
									{{ formatDate(session.started_at) }}
								</td>
							</tr>
							<tr v-if="!historySessions.length">
								<td
									colspan="8"
									class="px-4 py-12 text-center text-gray-400 text-sm"
								>
									No audit history found.
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Discrepancy View -->
			<div
				v-else-if="currentView === 'discrepancies'"
				class="flex-1 overflow-y-auto min-h-0"
			>
				<div class="max-w-5xl mx-auto">
					<button
						class="flex items-center gap-2 mb-4 text-xs font-bold text-gray-500 hover:text-gray-900 transition-colors"
						@click="currentView = 'history'"
					>
						<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor">
							<path
								d="M19 12H5M12 19l-7-7 7-7"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
						Back to History
					</button>
					<DiscrepancyBoard
						v-if="auditStore.activeSession"
						:audit-session="auditStore.activeSession.name"
						@resolved="onDiscrepancyResolved"
					/>
				</div>
			</div>

			<!-- Approve Variance Dialog -->
			<div
				v-if="showApproveDialog"
				class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			>
				<div
					class="bg-white dark:bg-warm-dark-800 rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl"
				>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
						Approve Variance
					</h3>
					<p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
						This store is frozen due to audit variance exceeding thresholds. Approving
						will unfreeze the store and process shrinkage.
					</p>
					<div class="mb-4">
						<label
							class="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1"
							>Approval Reason</label
						>
						<textarea
							v-model="approveReason"
							rows="3"
							class="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-warm-dark-700 text-sm resize-none"
							placeholder="e.g. Verified missing items are at repair bench..."
						></textarea>
					</div>
					<div class="flex gap-2">
						<button
							@click="showApproveDialog = false"
							class="flex-1 py-2 rounded-lg border border-gray-200 text-gray-600 text-sm font-semibold"
						>
							Cancel
						</button>
						<button
							@click="handleApproveVariance"
							:disabled="!approveReason.trim()"
							class="flex-1 py-2 rounded-lg bg-gradient-to-r from-[#D4AF37] to-[#F2E6A0] text-gray-900 text-sm font-bold disabled:opacity-50"
						>
							Approve & Unfreeze
						</button>
					</div>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import DiscrepancyBoard from '../components/DiscrepancyBoard.vue'
import { useAuditStore } from '../stores/audit'
import { useSessionStore } from '../stores/session'
import { useFormatters } from '../composables/useFormatters'

const auditStore = useAuditStore()
const session = useSessionStore()
const { formatCurrency } = useFormatters()

// --- Local State ---
const currentView = ref('launcher') // 'launcher', 'scanning', 'history'
const selectedScope = ref('Spot')
const selectedWarehouse = ref('')
const auditNotes = ref('')
const barcodeBuffer = ref('')
const rfidBatch = ref('')
const audioEnabled = ref(false)
const discrepancyTab = ref('missing')
const barcodeInput = ref(null)
const warehouses = ref([])
const displayCases = ref([])
const draftSessions = ref([])
const historySessions = ref([])
const signOffUser = ref('')
const managerUsers = ref([])
const showApproveDialog = ref(false)
const approveReason = ref('')
const pendingApproveSession = ref(null)

// --- Computed ---
const showSignOffField = computed(() => {
	// Show sign-off when there are discrepancies
	return (
		auditStore.isActive &&
		(auditStore.missingItems.length > 0 || auditStore.unexpectedItems.length > 0)
	)
})

const scopeWarehouses = computed(() => {
	if (selectedScope.value === 'Spot' || selectedScope.value === 'Showcase') {
		return displayCases.value
	}
	return warehouses.value
})

const lastScanDetail = computed(() => {
	const r = auditStore.lastScanResult
	if (!r || r.match_status === 'Batch') return null
	return r
})

const lastScanColor = computed(() => {
	const r = auditStore.lastScanResult
	if (!r || r.match_status === 'Batch') return 'border-gray-200 dark:border-warm-border'
	if (r.match_status === 'Matched') return 'border-green-400 bg-green-50 dark:bg-green-900/20'
	if (r.match_status === 'Unexpected') return 'border-red-400 bg-red-50 dark:bg-red-900/20'
	if (r.match_status === 'Duplicate') return 'border-amber-400 bg-amber-50 dark:bg-amber-900/20'
	return 'border-gray-200 dark:border-warm-border'
})

const scanResultClasses = computed(() => {
	const r = auditStore.lastScanResult
	if (!r) return ''
	if (r.match_status === 'Matched')
		return 'bg-green-50 dark:bg-green-900/20 text-green-700 border border-green-200'
	if (r.match_status === 'Unexpected')
		return 'bg-red-50 dark:bg-red-900/20 text-red-700 border border-red-200'
	if (r.match_status === 'Duplicate')
		return 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 border border-amber-200'
	if (r.match_status === 'Batch')
		return 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 border border-blue-200'
	return ''
})

const scanResultMessage = computed(() => {
	const r = auditStore.lastScanResult
	if (!r) return ''
	if (r.match_status === 'Matched') return `Matched: ${r.item_name || r.item_code}`
	if (r.match_status === 'Unexpected')
		return `Unexpected: ${r.barcode_or_epc || r.item_code || 'Unknown EPC'}`
	if (r.match_status === 'Duplicate') return `Duplicate scan: ${r.item_name || r.barcode_or_epc}`
	if (r.match_status === 'Batch')
		return `Batch: ${r.total_submitted} new, ${r.duplicates_skipped} duplicates`
	return ''
})

const statusClasses = computed(() => {
	const s = auditStore.activeSession?.status
	if (s === 'Reconciled') return '!bg-green-50 !text-green-700 !border-green-200'
	if (s === 'Reconciled with Shrinkage') return '!bg-amber-50 !text-amber-700 !border-amber-200'
	if (s === 'Discrepancy') return '!bg-red-50 !text-red-700 !border-red-200'
	if (s === 'Pending Manager Review') return '!bg-red-100 !text-red-800 !border-red-300'
	if (s === 'In Progress') return '!bg-blue-50 !text-blue-700 !border-blue-200'
	if (s === 'Draft') return '!bg-gray-50 !text-gray-600 !border-gray-200'
	if (s === 'Cancelled') return '!bg-gray-100 !text-gray-400 !border-gray-200'
	return '!bg-amber-50 !text-amber-700 !border-amber-200'
})

const valueDiscrepancyColor = computed(() => {
	const d =
		auditStore.progress?.session?.variance_dollar_total ||
		auditStore.progress?.session?.total_value_discrepancy ||
		0
	if (d > 0) return 'text-red-500'
	if (d < 0) return 'text-green-600'
	return 'text-gray-500'
})

const rfidLineCount = computed(() => {
	return rfidBatch.value.split('\n').filter((l) => l.trim()).length
})

// --- Helpers ---
function formatCount(n) {
	return n || 0
}

function formatDate(d) {
	if (!d) return '-'
	try {
		return new Date(d).toLocaleDateString()
	} catch {
		return d
	}
}

function scanCardClasses(status) {
	if (status === 'Matched')
		return 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800/30'
	if (status === 'Unexpected')
		return 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800/30'
	if (status === 'Duplicate')
		return 'bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-800/30'
	return 'bg-gray-50 dark:bg-warm-dark-700 border-gray-200 dark:border-warm-border/50'
}

function scanIconClass(status) {
	if (status === 'Matched') return 'bg-green-500'
	if (status === 'Unexpected') return 'bg-red-500'
	if (status === 'Duplicate') return 'bg-amber-500'
	return 'bg-gray-400'
}

function scanIcon(status) {
	if (status === 'Matched') return '\u2713'
	if (status === 'Unexpected') return '!'
	if (status === 'Duplicate') return '\u229E'
	return '?'
}

function scanBadgeClass(status) {
	if (status === 'Matched') return 'bg-green-100 dark:bg-green-900/30 text-green-700'
	if (status === 'Unexpected') return 'bg-red-100 dark:bg-red-900/30 text-red-700'
	if (status === 'Duplicate') return 'bg-amber-100 dark:bg-amber-900/30 text-amber-700'
	return 'bg-gray-100 text-gray-500'
}

function historyStatusClass(status) {
	if (status === 'Reconciled') return 'bg-green-100 text-green-700'
	if (status === 'Reconciled with Shrinkage') return 'bg-amber-100 text-amber-700'
	if (status === 'Discrepancy') return 'bg-red-100 text-red-700'
	if (status === 'Pending Manager Review') return 'bg-red-200 text-red-800'
	if (status === 'Cancelled') return 'bg-gray-100 text-gray-500'
	return 'bg-amber-100 text-amber-700'
}

function playBeep(type) {
	if (!audioEnabled.value) return
	try {
		const freq = type === 'matched' ? 880 : type === 'unexpected' ? 330 : 660
		const ctx = new (window.AudioContext || window.webkitAudioContext)()
		const osc = ctx.createOscillator()
		const gain = ctx.createGain()
		osc.connect(gain)
		gain.connect(ctx.destination)
		osc.frequency.value = freq
		gain.gain.value = 0.1
		osc.start()
		setTimeout(() => {
			osc.stop()
			ctx.close()
		}, 150)
	} catch {
		/* audio not available */
	}
}

// --- Actions ---
async function handleStartAudit() {
	if (!selectedWarehouse.value) return
	await auditStore.startAudit(
		selectedWarehouse.value,
		auditNotes.value || undefined,
		selectedScope.value
	)
	currentView.value = 'scanning'
	auditStore.startPolling()
	await nextTick()
	refocusInput()
}

async function startFromPlan(plan) {
	selectedScope.value =
		plan.scope === 'Daily Spot'
			? 'Spot'
			: plan.scope === 'Weekly Showcase'
			? 'Showcase'
			: plan.scope === 'Monthly Backstock'
			? 'Backstock'
			: 'Full Store'
	selectedWarehouse.value = plan.store_location
	await auditStore.startAudit(plan.store_location, undefined, selectedScope.value, plan.name)
	currentView.value = 'scanning'
	auditStore.startPolling()
	await nextTick()
	refocusInput()
}

async function handleResume(sessionName) {
	await auditStore.resumeAudit(sessionName)
	currentView.value = 'scanning'
	await nextTick()
	refocusInput()
}

function goToLauncher() {
	auditStore.clearSession()
	currentView.value = 'launcher'
	loadDrafts()
	auditStore.loadDashboard()
	auditStore.loadAuditPlans()
}

function handleBarcodeSubmit() {
	const code = barcodeBuffer.value.trim()
	if (!code) return
	barcodeBuffer.value = ''
	auditStore.scanBarcode(code).then((result) => {
		if (result?.match_status === 'Matched') playBeep('matched')
		else if (result?.match_status === 'Unexpected') playBeep('unexpected')
		else if (result?.match_status === 'Duplicate') playBeep('duplicate')
	})
}

function handleBatchSubmit() {
	const codes = rfidBatch.value
		.split('\n')
		.map((l) => l.trim())
		.filter(Boolean)
	if (!codes.length) return
	auditStore.scanBatch(codes).then(() => {
		rfidBatch.value = ''
	})
}

function refocusInput() {
	if (auditStore.scanMode === 'barcode' && barcodeInput.value) {
		nextTick(() => barcodeInput.value?.focus())
	}
}

function handleFinalize() {
	if (
		!confirm(
			'Finalize this audit? Missing items will trigger shrinkage entries or store freeze.'
		)
	)
		return
	auditStore.finalize(signOffUser.value || undefined)
}

function handleCancel() {
	if (!confirm('Cancel this audit? The session will be marked as cancelled.')) return
	auditStore.cancel()
}

function handleApproveVariance() {
	if (!approveReason.value.trim() || !pendingApproveSession.value) return
	auditStore.approveVariance(pendingApproveSession.value, approveReason.value).then(() => {
		showApproveDialog.value = false
		approveReason.value = ''
		pendingApproveSession.value = null
		goToLauncher()
	})
}

function viewSessionResults(session) {
	if (session.status === 'Pending Manager Review' || session.status === 'Discrepancy') {
		auditStore.activeSession = session
		currentView.value = 'discrepancies'
		return
	}
	if (['Draft', 'In Progress'].includes(session.status)) {
		handleResume(session.name)
	} else {
		auditStore.activeSession = session
		auditStore.refreshProgress()
		currentView.value = 'scanning'
	}
}

function onDiscrepancyResolved() {
	loadHistory()
}

function exportPDF() {
	const sessionName = auditStore.activeSession?.name
	if (!sessionName) return
	window.open(
		`/api/method/frappe.utils.print_format.download_pdf?doctype=Case+Audit+Session&name=${sessionName}&format=Audit+Report`,
		'_blank'
	)
}

async function loadWarehouses() {
	try {
		const res = await fetch('/api/method/frappe.client.get_list', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': window.csrf_token || '',
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				doctype: 'Warehouse',
				fields: ['name'],
				filters: { is_group: 0 },
				limit_page_length: 200,
			}),
		})
		const data = await res.json()
		warehouses.value = data.message || []
	} catch {
		warehouses.value = []
	}
}

async function loadDisplayCases() {
	try {
		const res = await fetch('/api/method/frappe.client.get_list', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': window.csrf_token || '',
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				doctype: 'Display Case',
				fields: ['name', 'case_name', 'warehouse'],
				limit_page_length: 100,
			}),
		})
		const data = await res.json()
		displayCases.value = (data.message || []).map((dc) => ({
			name: dc.warehouse || dc.name,
			label: dc.case_name || dc.name,
		}))
	} catch {
		displayCases.value = []
	}
}

async function loadManagers() {
	try {
		const res = await fetch('/api/method/frappe.client.get_list', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': window.csrf_token || '',
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				doctype: 'User',
				fields: ['name', 'full_name'],
				filters: { user_type: 'System User', enabled: 1 },
				limit_page_length: 100,
			}),
		})
		const data = await res.json()
		managerUsers.value = (data.message || []).filter(
			(u) => u.name !== 'Administrator' && u.name !== 'Guest'
		)
	} catch {
		managerUsers.value = []
	}
}

async function loadDrafts() {
	try {
		const res = await fetch('/api/method/zevar_core.api.inventory_audit.get_audit_history', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': window.csrf_token || '',
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ status: 'Draft', page_size: 10 }),
		})
		const data = await res.json()
		draftSessions.value = data.message?.sessions || []
	} catch {
		draftSessions.value = []
	}
}

async function loadHistory() {
	await auditStore.loadHistory({ page_size: 50 })
	historySessions.value = auditStore.historyResource.data?.sessions || []
}

// Watch scope change to reset warehouse selection
watch(selectedScope, () => {
	selectedWarehouse.value = ''
})

// Watch view changes
watch(currentView, (v) => {
	if (v === 'history') loadHistory()
	if (v === 'launcher') {
		loadDrafts()
		loadWarehouses()
		loadDisplayCases()
		auditStore.loadDashboard()
		auditStore.loadAuditPlans()
	}
})

// --- Lifecycle ---
onMounted(() => {
	selectedWarehouse.value = session.currentWarehouse || ''
	loadWarehouses()
	loadDisplayCases()
	loadManagers()
	loadDrafts()
	auditStore.loadDashboard()
	auditStore.loadAuditPlans()
})

onBeforeUnmount(() => {
	auditStore.stopPolling()
})
</script>
