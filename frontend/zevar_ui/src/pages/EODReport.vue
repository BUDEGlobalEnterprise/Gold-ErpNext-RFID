<template>
	<AppLayout>
		<div class="reports-layout flex flex-col gap-4 h-full">
			<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 class="text-2xl font-semibold text-gray-900 dark:text-white">Command Center</h1>
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Unified reporting and analytics</p>
				</div>
				<div class="flex flex-col sm:flex-row gap-2 sm:items-center">
					<input
						v-model="selectedDate"
						type="date"
						:max="todayStr"
						class="h-9 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs text-gray-900 dark:text-white focus:ring-2 focus:ring-[#D4AF37] outline-none"
					/>
					<select
						v-model="selectedStore"
						class="h-9 px-3 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs text-gray-700 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] outline-none"
					>
						<option value="">All Stores</option>
						<option v-for="(label, code) in storeLocations" :key="code" :value="code">
							{{ label }}
						</option>
					</select>
					<button
						@click="loadReport"
						:disabled="eodResource.loading"
						class="h-9 px-4 rounded-lg border border-gray-200 dark:border-warm-border bg-white dark:bg-[#1C1F26] text-xs font-bold text-gray-700 dark:text-gray-200 hover:border-[#D4AF37] disabled:opacity-50 flex items-center gap-2"
					>
						<span
							class="material-symbols-outlined !text-base"
							:class="{ 'animate-spin': eodResource.loading }"
							>refresh</span
						>
						Refresh
					</button>
				</div>
			</header>

			<CommandCenterTabs />

			<div class="flex-1 overflow-auto min-h-0 pt-2 flex flex-col">
				<!-- ============ Header ============ -->
				<div
					class="flex items-center gap-3 mb-4 flex-shrink-0 no-print"
				>
					<span class="material-symbols-outlined text-[#D4AF37] !text-2xl">point_of_sale</span>
					<div>
						<h2 class="premium-title !text-xl sm:!text-2xl leading-tight">End of Day Report</h2>
						<p class="text-[11px] text-gray-500 dark:text-gray-400">
							Z-Report &middot; {{ report?.meta?.primary_role || '' }}
							<span v-if="isToday" class="text-[#D4AF37]">&middot; Live</span>
						</p>
					</div>
				</div>

			<!-- ============ Loading ============ -->
			<div v-if="eodResource.loading && !report" class="flex-1 flex items-center justify-center">
				<div class="text-center text-gray-500 dark:text-gray-400">
					<div
						class="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-[#D4AF37] mx-auto mb-3"
					></div>
					Building end-of-day report...
				</div>
			</div>

			<!-- ============ Error ============ -->
			<div v-else-if="loadError && !report" class="flex-1 flex items-center justify-center">
				<div class="premium-card max-w-md text-center">
					<span class="material-symbols-outlined text-4xl text-red-400 mb-3">error</span>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
						Could not load report
					</h3>
					<p class="text-sm text-gray-500 dark:text-gray-400">{{ loadError }}</p>
					<button
						@click="loadReport"
						class="mt-4 px-4 py-2 bg-[#D4AF37] text-black text-xs font-bold rounded-lg"
					>
						Try Again
					</button>
				</div>
			</div>

			<!-- ============ Report body ============ -->
			<div v-else-if="report" class="flex-1 overflow-auto min-h-0 pr-1 pb-4 eod-body">
				<!-- Print-only header -->
				<div class="print-only mb-4">
					<h1 class="!text-2xl font-black text-center text-black">Z-REPORT — END OF DAY</h1>
					<p class="text-center text-sm text-gray-600">
						{{ fmtDateLong(report.date) }}
						<span v-if="selectedStore">&middot; {{ storeLocations[selectedStore] }}</span>
					</p>
				</div>

				<!-- ===== Quick KPI Bar ===== -->
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
					<div class="premium-card !p-4 flex flex-col gap-1">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-bold uppercase tracking-wide text-emerald-600 dark:text-emerald-400">Net Sales</span>
							<span class="material-symbols-outlined !text-base text-emerald-600 dark:text-emerald-400">payments</span>
						</div>
						<YoYBadge v-if="revenue.yoy && (revenue.yoy.pct || revenue.yoy.this)" :delta="revenue.yoy" />
						<p class="text-xl font-black font-mono text-gray-900 dark:text-white">{{ fmtMoney(revenue.net_sales) }}</p>
					</div>
					<div class="premium-card !p-4 flex flex-col gap-1">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-bold uppercase tracking-wide text-blue-600 dark:text-blue-400">Transactions</span>
							<span class="material-symbols-outlined !text-base text-blue-600 dark:text-blue-400">receipt_long</span>
						</div>
						<p class="text-xl font-black font-mono text-gray-900 dark:text-white">{{ fmtNum(revenue.transaction_count) }}</p>
						<p class="text-[10px] text-gray-500 dark:text-gray-400">avg {{ fmtMoney(revenue.avg_ticket) }}</p>
					</div>
					<div class="premium-card !p-4 flex flex-col gap-1">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-bold uppercase tracking-wide text-purple-600 dark:text-purple-400">Tax Collected</span>
							<span class="material-symbols-outlined !text-base text-purple-600 dark:text-purple-400">percent</span>
						</div>
						<p class="text-xl font-black font-mono text-gray-900 dark:text-white">{{ fmtMoney(revenue.tax_collected) }}</p>
					</div>
					<div class="premium-card !p-4 flex flex-col gap-1">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-bold uppercase tracking-wide text-amber-600 dark:text-amber-400">Cash Variance</span>
							<span class="material-symbols-outlined !text-base text-amber-600 dark:text-amber-400">account_balance_wallet</span>
						</div>
						<p
							class="text-xl font-black font-mono"
							:class="{
								'text-green-500': varianceTone === 'green',
								'text-red-500': varianceTone === 'red',
								'text-amber-500': varianceTone === 'amber',
								'text-gray-400': varianceTone === 'neutral',
							}"
						>{{ fmtVariance(cash.variance) }}</p>
						<p class="text-[10px] text-gray-500 dark:text-gray-400">{{ varianceLabel }}</p>
					</div>
				</div>

				<!-- ===== Section 1: Revenue Dashboard ===== -->
				<section class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('revenue')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">monitoring</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Revenue Dashboard</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.revenue ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.revenue" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Gross Sales</p>
								<p class="text-lg font-black font-mono text-emerald-600 dark:text-emerald-400">{{ fmtMoney(revenue.gross_sales) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Refunds</p>
								<p class="text-lg font-black font-mono text-red-600 dark:text-red-400">{{ fmtMoney(revenue.refunds) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Net Sales</p>
								<p class="text-lg font-black font-mono text-emerald-600 dark:text-emerald-400">{{ fmtMoney(revenue.net_sales) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Avg Ticket</p>
								<p class="text-lg font-black font-mono text-blue-600 dark:text-blue-400">{{ fmtMoney(revenue.avg_ticket) }}</p>
							</div>
						</div>
						<div class="flex flex-wrap gap-4 text-xs mb-4">
							<span class="inline-flex items-center gap-1">
								<span class="text-gray-500 dark:text-gray-400">vs Last Year</span>
								<span class="font-bold" :class="yoyUp(revenue.yoy) ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">{{ fmtPct(revenue.yoy) }}</span>
							</span>
							<span class="inline-flex items-center gap-1">
								<span class="text-gray-500 dark:text-gray-400">vs Last Week</span>
								<span class="font-bold" :class="yoyUp(revenue.wow) ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">{{ fmtPct(revenue.wow) }}</span>
							</span>
							<span v-if="revenue.peak_hour" class="inline-flex items-center gap-1 text-gray-500 dark:text-gray-400">
								<span class="material-symbols-outlined !text-sm">schedule</span>
								Peak hour: <b class="text-gray-900 dark:text-white ml-1">{{ formatHour(revenue.peak_hour.hour) }}</b> ({{ revenue.peak_hour.count }} txns)
							</span>
						</div>
						<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-4">
							<div class="flex items-end gap-1 h-32">
								<template v-if="revenue.hourly_breakdown && revenue.hourly_breakdown.length">
									<div v-for="h in hourlyChart" :key="h.hour" class="flex-1 flex flex-col items-center justify-end group">
										<div class="w-full rounded-t bg-gradient-to-t from-[#D4AF37]/40 to-[#D4AF37] min-h-[2px]" :style="{ height: h.barPct + '%' }"></div>
										<span class="text-[8px] text-gray-400 mt-1">{{ h.hour }}</span>
									</div>
								</template>
								<p v-else class="text-xs text-gray-400 m-auto">No hourly sales data</p>
							</div>
						</div>
					</div>
				</section>

				<!-- ===== Section 2: Transaction Streams ===== -->
				<section class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('streams')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">category</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Transaction Streams</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.streams ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.streams" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
							<div v-for="s in streamCards" :key="s.label" class="premium-card !p-4 flex flex-col gap-1">
								<div class="flex items-center justify-between">
									<span class="text-[10px] font-bold uppercase tracking-wide" :class="toneClass(s.tone)">{{ s.label }}</span>
									<span class="material-symbols-outlined !text-base" :class="toneClass(s.tone)">{{ s.icon }}</span>
								</div>
								<p class="text-lg font-black font-mono text-gray-900 dark:text-white">{{ fmtMoney(s.total) }}</p>
								<p class="text-[10px] text-gray-500 dark:text-gray-400">{{ s.count }} txns</p>
								<p v-if="s.sub" class="text-[9px] text-gray-400">{{ s.sub }}</p>
							</div>
						</div>
					</div>
				</section>

				<!-- ===== Section 3: Payment Breakdown ===== -->
				<section v-if="report.meta.can_see_financials" class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('payments')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">credit_card</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Payment Breakdown</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.payments ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.payments" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2 mb-4">
							<div v-for="(g, key) in paymentGroups" :key="key" class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-lg p-2 text-center">
								<p class="text-[9px] uppercase tracking-wider text-gray-500 capitalize">{{ groupLabel(key) }}</p>
								<p class="text-sm font-bold font-mono text-gray-900 dark:text-white">{{ fmtMoney(g.total) }}</p>
								<p class="text-[9px] text-gray-400">{{ paymentMethods.total ? Math.round((g.total / paymentMethods.total) * 100) || 0 : 0 }}%</p>
							</div>
						</div>
						<div v-if="paymentMethods.methods && paymentMethods.methods.length" class="overflow-x-auto">
							<table class="w-full text-xs">
								<thead>
									<tr class="text-left text-[10px] uppercase tracking-wider text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-warm-border">
										<th class="py-2 pr-3 font-bold">Method</th>
										<th class="py-2 px-3 font-bold text-right">Count</th>
										<th class="py-2 px-3 font-bold text-right">Total</th>
										<th class="py-2 pl-3 font-bold text-right">Share</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="m in paymentMethods.methods" :key="m.method" class="border-b border-gray-100 dark:border-gray-800">
										<td class="py-2 pr-3 font-medium text-gray-900 dark:text-white">{{ m.method }}</td>
										<td class="py-2 px-3 text-right text-gray-600 dark:text-gray-300">{{ m.count }}</td>
										<td class="py-2 px-3 text-right font-mono text-gray-900 dark:text-white">{{ fmtMoney(m.total) }}</td>
										<td class="py-2 pl-3 text-right">
											<span class="inline-block h-1.5 rounded-full bg-[#D4AF37] align-middle" :style="{ width: Math.min(100, m.pct) * 1.2 + 'px' }"></span>
											<span class="ml-1 text-gray-500">{{ m.pct }}%</span>
										</td>
									</tr>
								</tbody>
								<tfoot>
									<tr class="font-bold">
										<td class="py-2 pr-3 text-gray-900 dark:text-white">Total Collected</td>
										<td class="py-2 px-3"></td>
										<td class="py-2 px-3 text-right font-mono text-[#D4AF37]">{{ fmtMoney(paymentMethods.total) }}</td>
										<td class="py-2 pl-3"></td>
									</tr>
								</tfoot>
							</table>
						</div>
						<p v-else class="text-xs text-gray-400 py-4 text-center">No payment data for this day</p>
						<div v-if="paymentMethods.financing && paymentMethods.financing.length" class="mt-4">
							<h4 class="text-[10px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">Financing Approvals</h4>
							<div class="flex flex-wrap gap-2">
								<span v-for="f in paymentMethods.financing" :key="f.provider" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-300 border border-sky-100 dark:border-sky-800/30">
									{{ f.provider }}: {{ f.approved_count }} &middot; {{ fmtMoney(f.total_financed) }}
								</span>
							</div>
						</div>
					</div>
				</section>

				<!-- ===== Section 4: Cash Drawer Reconciliation ===== -->
				<section v-if="report.meta.can_see_financials" class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('cash')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">account_balance_wallet</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Cash Drawer Reconciliation</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.cash ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.cash" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Opening Float</p>
								<p class="text-lg font-black font-mono text-gray-600 dark:text-gray-300">{{ fmtMoney(cash.opening_float) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Cash Sales</p>
								<p class="text-lg font-black font-mono text-emerald-600 dark:text-emerald-400">{{ fmtMoney(cash.cash_sales) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Cash Refunds</p>
								<p class="text-lg font-black font-mono text-red-600 dark:text-red-400">-{{ fmtMoney(cash.cash_refunds) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Payouts/Drops</p>
								<p class="text-lg font-black font-mono text-gray-600 dark:text-gray-300">{{ fmtMoney(cash.cash_drops_payouts) }}</p>
							</div>
						</div>
						<div class="rounded-xl p-5 border" :class="varianceBoxClass">
							<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
								<div>
									<p class="text-[10px] uppercase tracking-wider text-gray-500">Expected</p>
									<p class="text-lg font-black font-mono text-gray-900 dark:text-white">{{ fmtMoney(cash.expected_closing) }}</p>
								</div>
								<div>
									<p class="text-[10px] uppercase tracking-wider text-gray-500">Counted</p>
									<p class="text-lg font-black font-mono text-gray-900 dark:text-white">{{ cash.session_closed ? fmtMoney(cash.counted_closing) : '—' }}</p>
									<p v-if="!cash.session_closed" class="text-[9px] text-gray-400">session open</p>
								</div>
								<div>
									<p class="text-[10px] uppercase tracking-wider text-gray-500">Variance</p>
									<p class="text-lg font-black font-mono" :class="varianceTextClass">{{ fmtVariance(cash.variance) }}</p>
								</div>
								<div>
									<p class="text-[10px] uppercase tracking-wider text-gray-500">Status</p>
									<p class="text-xs font-bold uppercase mt-1" :class="varianceTextClass">{{ varianceLabel }}</p>
									<p v-if="cash.override_required" class="text-[9px] text-red-400 mt-1">override required (&gt;${{ cash.threshold }})</p>
								</div>
							</div>
							<table v-if="cash.denominations && cash.denominations.length" class="w-full text-xs mt-4 border-t border-gray-200 dark:border-gray-700 pt-3">
								<thead>
									<tr class="text-left text-[10px] uppercase text-gray-500">
										<th class="py-1">Mode</th>
										<th class="py-1 text-right">Opening</th>
										<th class="py-1 text-right">Expected</th>
										<th class="py-1 text-right">Counted</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="(d, i) in cash.denominations" :key="i" class="text-gray-700 dark:text-gray-300">
										<td class="py-1">{{ d.mode_of_payment }}</td>
										<td class="py-1 text-right font-mono">{{ fmtMoney(d.opening) }}</td>
										<td class="py-1 text-right font-mono">{{ fmtMoney(d.expected) }}</td>
										<td class="py-1 text-right font-mono">{{ fmtMoney(d.counted) }}</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>
				</section>

				<!-- ===== Section 5: Audit Trail ===== -->
				<section v-if="report.meta.can_see_store" class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('audit')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">shield_person</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Audit Trail</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.audit ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.audit" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-2 md:grid-cols-5 gap-3">
							<div v-for="a in auditCards" :key="a.label" class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<div class="flex items-center gap-1.5">
									<span class="material-symbols-outlined !text-base" :class="toneClass(a.tone)">{{ a.icon }}</span>
									<span class="text-[10px] font-bold uppercase tracking-wide" :class="toneClass(a.tone)">{{ a.label }}</span>
								</div>
								<p class="text-xl font-black font-mono text-gray-900 dark:text-white mt-1">{{ a.count }}</p>
								<p v-if="a.total != null" class="text-[10px] text-gray-500">{{ fmtMoney(a.total) }}</p>
								<p v-if="a.extra" class="text-[9px] text-gray-400">{{ a.extra }}</p>
								<div v-if="a.reasons && a.reasons.length" class="mt-1 space-y-0.5">
									<p v-for="(r, i) in a.reasons.slice(0, 3)" :key="i" class="text-[9px] text-gray-400 truncate">{{ r.count }}× {{ r.reason }}</p>
								</div>
							</div>
						</div>
					</div>
				</section>

				<!-- ===== Section 6: Team Performance ===== -->
				<section v-if="report.meta.can_see_store" class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('team')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">groups</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Team Performance</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.team ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.team" class="px-4 pb-4 pt-1">
						<div class="overflow-x-auto">
							<table v-if="team.salespeople && team.salespeople.length" class="w-full text-xs">
								<thead>
									<tr class="text-left text-[10px] uppercase tracking-wider text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-warm-border">
										<th class="py-2 pr-3 font-bold">#</th>
										<th class="py-2 px-3 font-bold">Salesperson</th>
										<th class="py-2 px-3 font-bold text-right">Txns</th>
										<th class="py-2 px-3 font-bold text-right">Sales</th>
										<th class="py-2 px-3 font-bold text-right">Avg Ticket</th>
										<th class="py-2 pl-3 font-bold text-right">Commission</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="(s, i) in team.salespeople" :key="s.user" class="border-b border-gray-100 dark:border-gray-800">
										<td class="py-2 pr-3 text-gray-400">
											<span v-if="i === 0" class="material-symbols-outlined !text-base text-[#D4AF37]">emoji_events</span>
											<span v-else>{{ i + 1 }}</span>
										</td>
										<td class="py-2 px-3 font-medium text-gray-900 dark:text-white">{{ s.name }}</td>
										<td class="py-2 px-3 text-right text-gray-600 dark:text-gray-300">{{ s.transaction_count }}</td>
										<td class="py-2 px-3 text-right font-mono text-gray-900 dark:text-white">{{ fmtMoney(s.total_sales) }}</td>
										<td class="py-2 px-3 text-right text-gray-600 dark:text-gray-300">{{ fmtMoney(s.avg_ticket) }}</td>
										<td class="py-2 pl-3 text-right font-mono text-emerald-600 dark:text-emerald-400">{{ fmtMoney(s.commission_earned) }}</td>
									</tr>
								</tbody>
							</table>
							<p v-else class="text-xs text-gray-400 py-6 text-center">No salesperson activity for this day</p>
						</div>
						<p v-if="team.salespeople && team.salespeople.length" class="text-xs text-gray-500 dark:text-gray-400 mt-3 text-right">
							Total commission: <b class="text-emerald-600 dark:text-emerald-400">{{ fmtMoney(team.total_commission) }}</b>
						</p>
					</div>
				</section>

				<!-- ===== Section 7: Repairs & Services ===== -->
				<section class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('repairs')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">build</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Repairs &amp; Services</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.repairs ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.repairs" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-2 md:grid-cols-5 gap-3">
							<div v-for="m in repairCards" :key="m.label" class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3 text-center">
								<span class="material-symbols-outlined !text-xl" :class="toneClass(m.tone)">{{ m.icon }}</span>
								<p class="text-xl font-black font-mono" :class="toneClass(m.tone)">{{ m.value }}</p>
								<p class="text-[10px] text-gray-500 dark:text-gray-400">{{ m.label }}</p>
								<p v-if="m.sub" class="text-[9px] text-gray-400">{{ m.sub }}</p>
							</div>
						</div>
					</div>
				</section>

				<!-- ===== Section 8: Inventory Impact ===== -->
				<section class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('inventory')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">inventory_2</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Inventory Impact</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.inventory ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.inventory" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Items Sold</p>
								<p class="text-lg font-black font-mono text-emerald-600 dark:text-emerald-400">{{ fmtNum(inventory.items_sold) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Items Returned</p>
								<p class="text-lg font-black font-mono text-red-600 dark:text-red-400">{{ fmtNum(inventory.items_returned) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Net Change</p>
								<p class="text-lg font-black font-mono text-blue-600 dark:text-blue-400">{{ fmtNum(inventory.net_change) }}</p>
							</div>
							<div class="bg-gray-50 dark:bg-warm-dark-700/40 rounded-xl p-3">
								<p class="text-[10px] uppercase tracking-wider text-gray-500">Low Stock SKUs</p>
								<p class="text-lg font-black font-mono" :class="inventory.low_stock_count > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-gray-600 dark:text-gray-300'">{{ fmtNum(inventory.low_stock_count) }}</p>
							</div>
						</div>
						<div v-if="inventory.low_stock && inventory.low_stock.length" class="overflow-x-auto">
							<h4 class="text-[10px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">Low Stock Items</h4>
							<table class="w-full text-xs">
								<thead>
									<tr class="text-left text-[10px] uppercase text-gray-500 border-b border-gray-200 dark:border-warm-border">
										<th class="py-1.5 pr-3">Item</th>
										<th class="py-1.5 px-3">Warehouse</th>
										<th class="py-1.5 pl-3 text-right">Qty</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="(it, i) in inventory.low_stock.slice(0, 10)" :key="i" class="border-b border-gray-100 dark:border-gray-800">
										<td class="py-1.5 pr-3 text-gray-900 dark:text-white">{{ it.item_code }}</td>
										<td class="py-1.5 px-3 text-gray-500">{{ it.warehouse }}</td>
										<td class="py-1.5 pl-3 text-right font-mono text-red-500">{{ it.actual_qty }}</td>
									</tr>
								</tbody>
							</table>
						</div>
						<div v-if="inventory.high_value_items && inventory.high_value_items.length" class="mt-4">
							<h4 class="text-[10px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">High-Value Sales (&ge; {{ fmtMoney(inventory.high_value_threshold, 0) }})</h4>
							<div class="flex flex-wrap gap-2">
								<span v-for="(h, i) in inventory.high_value_items.slice(0, 12)" :key="i" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 border border-amber-100 dark:border-amber-800/30">
									{{ h.item_name || h.item_code }} &middot; <b>{{ fmtMoney(h.amount) }}</b>
								</span>
							</div>
						</div>
					</div>
				</section>

				<!-- ===== Session & Notes ===== -->
				<section class="premium-card !p-0 mb-4 overflow-hidden">
					<button @click="toggle('session')" class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700/40 transition no-print">
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined !text-lg text-[#D4AF37]">notes</span>
							<h3 class="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wide">Session &amp; Operational Notes</h3>
						</div>
						<span class="material-symbols-outlined !text-lg text-gray-400 transition-transform" :style="collapsed.session ? '' : 'transform: rotate(180deg)'">expand_more</span>
					</button>
					<div v-show="!collapsed.session" class="px-4 pb-4 pt-1">
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<h4 class="text-[10px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">POS Session</h4>
								<div v-if="session.has_session" class="space-y-1 text-xs text-gray-700 dark:text-gray-300">
									<div class="flex justify-between"><span class="text-gray-500">Sessions</span><span>{{ session.session_count }} ({{ session.open_sessions }} open)</span></div>
									<div class="flex justify-between"><span class="text-gray-500">Opening Float</span><span class="font-mono">{{ fmtMoney(session.opening_balance) }}</span></div>
									<div class="flex justify-between"><span class="text-gray-500">Duration</span><span>{{ session.duration_hours }}h</span></div>
									<div class="flex justify-between"><span class="text-gray-500">Cashiers</span><span>{{ cashierNames }}</span></div>
								</div>
								<p v-else class="text-xs text-gray-400">No POS session for this day</p>
							</div>
							<div>
								<h4 class="text-[10px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">Manager Notes &amp; Incidents</h4>
								<div v-if="notes.manager_notes && notes.manager_notes.length" class="space-y-1 mb-2">
									<p v-for="(n, i) in notes.manager_notes" :key="i" class="text-xs text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-warm-dark-700/40 rounded p-2">{{ n }}</p>
								</div>
								<div v-if="notes.flagged_incidents && notes.flagged_incidents.length">
									<p v-for="(inc, i) in notes.flagged_incidents" :key="i" class="text-xs text-red-600 dark:text-red-400 flex items-start gap-1.5 mb-1">
										<span class="material-symbols-outlined !text-sm mt-0.5">warning</span>
										<span>{{ inc.details || inc.event_type }} <span class="text-gray-400">— {{ inc.user }}</span></span>
									</p>
								</div>
								<p v-if="!notes.manager_notes?.length && !notes.flagged_incidents?.length" class="text-xs text-gray-400">No notes or incidents</p>
							</div>
						</div>
					</div>
				</section>

				<!-- ===== Footer Actions ===== -->
				<div class="flex flex-wrap gap-3 justify-center mt-6 pt-4 border-t border-gray-200 dark:border-warm-border no-print">
					<button @click="printReport" class="px-5 py-2.5 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#b5952f] transition text-sm flex items-center gap-2">
						<span class="material-symbols-outlined !text-base">print</span>Print Z-Report
					</button>
					<button @click="exportPdf" :disabled="exporting" class="px-5 py-2.5 border border-gray-200 dark:border-warm-border rounded-lg font-bold text-sm text-gray-700 dark:text-gray-200 hover:border-[#D4AF37] flex items-center gap-2 disabled:opacity-50">
						<span class="material-symbols-outlined !text-base">{{ exporting ? 'downloading' : 'picture_as_pdf' }}</span>
						{{ exporting ? 'Generating...' : 'Export PDF' }}
					</button>
					<button @click="emailManager" :disabled="emailing" class="px-5 py-2.5 border border-gray-200 dark:border-warm-border rounded-lg font-bold text-sm text-gray-700 dark:text-gray-200 hover:border-[#D4AF37] flex items-center gap-2 disabled:opacity-50">
						<span class="material-symbols-outlined !text-base">{{ emailing ? 'progress_activity' : 'mail' }}</span>
						{{ emailing ? 'Preparing...' : 'Email to Manager' }}
					</button>
				</div>
				<p class="text-center text-[10px] text-gray-400 mt-3">Generated {{ formatDateTime(report.meta.generated_at) }}</p>
			</div>
		</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'
import AppLayout from '@/components/AppLayout.vue'
import YoYBadge from '@/components/reports/YoYBadge.vue'
import CommandCenterTabs from '@/components/reports/CommandCenterTabs.vue'

const route = useRoute()

const storeLocations = {
	'NY-01': 'New York',
	'Miami-01': 'Miami',
	'LA-01': 'Los Angeles',
	'Houston-01': 'Houston',
	'Chicago-01': 'Chicago',
}

const todayStr = new Date().toISOString().split('T')[0]
const initialDate =
	route.query.date && String(route.query.date).toLowerCase() !== 'today'
		? String(route.query.date)
		: todayStr

const selectedDate = ref(initialDate)
const selectedStore = ref(route.query.store ? String(route.query.store) : '')
const report = ref(null)
const loadError = ref('')
const exporting = ref(false)
const emailing = ref(false)
const collapsed = ref({})

const eodResource = createResource({
	url: 'zevar_core.api.reports.get_eod_closeout_report',
	onSuccess(data) {
		report.value = data
		loadError.value = ''
	},
	onError(error) {
		loadError.value =
			error?.messages?.[0] || error?.message || 'Unable to load the EOD report.'
		report.value = null
	},
})

const pdfResource = createResource({
	url: 'zevar_core.api.reports.generate_eod_pdf',
	auto: false,
})

function loadReport() {
	eodResource.fetch({ date: selectedDate.value, store: selectedStore.value || undefined })
}

let refreshTimer = null
onMounted(() => {
	loadReport()
	// Auto-refresh every 60s when viewing today
	refreshTimer = setInterval(() => {
		if (selectedDate.value === todayStr) loadReport()
	}, 60000)
})
onUnmounted(() => clearInterval(refreshTimer))

// ---- section accessors (null-safe) ----
const revenue = computed(() => report.value?.revenue || {})
const streams = computed(() => report.value?.transaction_streams || {})
const paymentMethods = computed(() => report.value?.payment_methods || { methods: [], groups: {}, financing: [], total: 0 })
const paymentGroups = computed(() => paymentMethods.value.groups || {})
const cash = computed(() => report.value?.cash_reconciliation || {})
const audit = computed(() => report.value?.audit_trail || {})
const team = computed(() => report.value?.salesperson_performance || { salespeople: [], total_commission: 0 })
const repair = computed(() => report.value?.repair_status || {})
const inventory = computed(() => report.value?.inventory_impact || { low_stock: [], high_value_items: [] })
const session = computed(() => report.value?.session_info || { cashiers: [] })
const notes = computed(() => report.value?.operational_notes || { manager_notes: [], flagged_incidents: [] })

const isToday = computed(() => selectedDate.value === todayStr)

const streamCards = computed(() => {
	const s = streams.value
	return [
		{ label: 'Jewelry Sales', icon: 'diamond', tone: 'amber', count: s.jewelry_sales?.count || 0, total: s.jewelry_sales?.total || 0, sub: `avg ${fmtMoney(s.jewelry_sales?.avg_ticket || 0)}` },
		{ label: 'Repairs', icon: 'build', tone: 'blue', count: s.repairs?.count || 0, total: s.repairs?.total_revenue || 0, sub: `${s.repairs?.completed_today || 0} done · ${s.repairs?.active || 0} active` },
		{ label: 'Layaway', icon: 'event_repeat', tone: 'purple', count: s.layaway?.new_contracts || 0, total: s.layaway?.deposits_collected || 0, sub: `${s.layaway?.matured_today || 0} matured · ${s.layaway?.active || 0} active` },
		{ label: 'Trade-Ins', icon: 'swap_horiz', tone: 'teal', count: s.trade_ins?.count || 0, total: s.trade_ins?.total_value || 0 },
		{ label: 'Gold Purchases', icon: 'savings', tone: 'amber', count: s.gold_purchases?.count || 0, total: s.gold_purchases?.total_value || 0, sub: `${fmtNum(s.gold_purchases?.total_weight_g || 0, 1)} g` },
		{ label: 'Gift Cards Sold', icon: 'card_giftcard', tone: 'rose', count: s.gift_cards?.sold?.count || 0, total: s.gift_cards?.sold?.amount || 0, sub: `${s.gift_cards?.redeemed?.count || 0} redeemed` },
		{ label: 'Custom Orders', icon: 'design_services', tone: 'indigo', count: s.custom_orders?.count || 0, total: s.custom_orders?.total_deposits || 0 },
	]
})

const auditCards = computed(() => {
	const a = audit.value
	return [
		{ label: 'Voids', icon: 'block', tone: 'red', count: a.voids?.count || 0, total: a.voids?.total, reasons: a.voids?.reasons || [] },
		{ label: 'Refunds', icon: 'undo', tone: 'orange', count: a.refunds?.count || 0, total: a.refunds?.total, reasons: a.refunds?.reasons || [], extra: `${a.refunds?.items_returned || 0} items` },
		{ label: 'Discounts', icon: 'sell', tone: 'purple', count: a.discounts?.count || 0, total: a.discounts?.total, reasons: a.discounts?.top_reasons || [] },
		{ label: 'Mgr Overrides', icon: 'manage_accounts', tone: 'blue', count: a.manager_overrides?.count || 0, extra: `${(a.manager_overrides?.by_approver || []).length} approvers` },
		{ label: 'Price Overrides', icon: 'price_change', tone: 'teal', count: a.price_overrides?.count || 0 },
	]
})

const repairCards = computed(() => {
	const r = repair.value
	return [
		{ label: 'New Today', icon: 'add_circle', tone: 'emerald', value: r.new_today || 0 },
		{ label: 'Completed', icon: 'task_alt', tone: 'blue', value: r.completed_today || 0 },
		{ label: 'Delivered', icon: 'local_shipping', tone: 'purple', value: r.delivered_today || 0 },
		{ label: 'Active In Shop', icon: 'handyman', tone: 'amber', value: r.active || 0 },
		{ label: 'Overdue', icon: 'warning', tone: r.overdue > 0 ? 'red' : 'gray', value: r.overdue || 0, sub: r.oldest_overdue ? `oldest ${r.oldest_overdue}` : '' },
	]
})

const cashierNames = computed(() => (session.value.cashiers || []).map((c) => c.full_name).join(', ') || '—')

// ---- variance colour mapping (plan: green=balanced, red=short, amber=over) ----
const varianceTone = computed(() => {
	const s = cash.value.variance_status
	if (!cash.value.session_closed && !cash.value.counted_closing) return 'neutral'
	if (s === 'balanced') return 'green'
	if (s === 'short') return 'red'
	if (s === 'excess') return 'amber'
	return 'neutral'
})
const varianceLabel = computed(() => {
	const map = { green: 'Balanced', red: 'Short', amber: 'Over', neutral: 'Pending' }
	return map[varianceTone.value] || '—'
})
const varianceTextClass = computed(() => ({
	green: 'text-green-500',
	red: 'text-red-500',
	amber: 'text-amber-500',
	neutral: 'text-gray-400',
}[varianceTone.value]))
const varianceBoxClass = computed(() => ({
	green: 'bg-green-500/10 border-green-500/30',
	red: 'bg-red-500/10 border-red-500/30',
	amber: 'bg-amber-500/10 border-amber-500/30',
	neutral: 'bg-gray-50 dark:bg-warm-dark-700/40 border-gray-200 dark:border-warm-border',
}[varianceTone.value]))

// hourly chart bars (height % based on max txn count)
const hourlyChart = computed(() => {
	const rows = revenue.value.hourly_breakdown || []
	const max = Math.max(1, ...rows.map((r) => r.count))
	return rows.map((r) => ({ ...r, barPct: Math.round((r.count / max) * 100) }))
})

// ---- tone + formatters ----
function toneClass(tone) {
	return (
		{
			emerald: 'text-emerald-600 dark:text-emerald-400',
			blue: 'text-blue-600 dark:text-blue-400',
			purple: 'text-purple-600 dark:text-purple-400',
			amber: 'text-amber-600 dark:text-amber-400',
			red: 'text-red-600 dark:text-red-400',
			orange: 'text-orange-600 dark:text-orange-400',
			teal: 'text-teal-600 dark:text-teal-400',
			rose: 'text-rose-600 dark:text-rose-400',
			indigo: 'text-indigo-600 dark:text-indigo-400',
			gray: 'text-gray-600 dark:text-gray-300',
		}[tone] || ''
	)
}
function groupLabel(key) {
	return String(key).replace('_', ' ')
}
function yoyUp(delta) {
	return (delta?.pct ?? 0) >= 0
}
function fmtPct(delta) {
	const pct = delta?.pct ?? 0
	return `${pct >= 0 ? '+' : ''}${pct}%`
}
function fmtMoney(v, dp = 2) {
	if (v == null || isNaN(v)) return (0).toFixed(dp)
	return '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}
function fmtNum(v, dp = 0) {
	if (v == null || isNaN(v)) return (0).toFixed(dp)
	return Number(v).toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}
function fmtVariance(v) {
	if (v == null) return '$0.00'
	const sign = Number(v) > 0 ? '+' : ''
	return sign + fmtMoney(v)
}
function formatHour(h) {
	if (h == null) return ''
	const ampm = h < 12 ? 'AM' : 'PM'
	const hr = h % 12 === 0 ? 12 : h % 12
	return `${hr}${ampm}`
}
function fmtDateLong(d) {
	if (!d) return ''
	try {
		return new Date(d + 'T00:00:00').toLocaleDateString('en-US', {
			weekday: 'short', year: 'numeric', month: 'long', day: 'numeric',
		})
	} catch {
		return d
	}
}
function formatDateTime(iso) {
	if (!iso) return ''
	try {
		return new Date(iso).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })
	} catch {
		return iso
	}
}

// ---- actions ----
function toggle(id) {
	collapsed.value[id] = !collapsed.value[id]
}
function printReport() {
	window.print()
}
async function exportPdf() {
	exporting.value = true
	try {
		const res = await pdfResource.submit({ date: selectedDate.value, store: selectedStore.value || undefined })
		if (res?.file_url) window.open(res.file_url, '_blank')
	} catch (e) {
		loadError.value = e?.messages?.[0] || e?.message || 'PDF export failed'
	} finally {
		exporting.value = false
	}
}
async function emailManager() {
	emailing.value = true
	try {
		const res = await pdfResource.submit({ date: selectedDate.value, store: selectedStore.value || undefined })
		const subject = encodeURIComponent(`EOD Z-Report — ${selectedDate.value}`)
		const body = encodeURIComponent(
			`End of Day report for ${selectedDate.value}.\n\n` +
				`Net Sales: ${fmtMoney(revenue.value.net_sales)}\n` +
				`Transactions: ${revenue.value.transaction_count}\n` +
				`Cash Variance: ${fmtVariance(cash.value.variance)} (${varianceLabel.value})\n\n` +
				(res?.file_url ? `Z-Report PDF: ${window.location.origin}${res.file_url}` : '')
		)
		window.location.href = `mailto:?subject=${subject}&body=${body}`
	} catch (e) {
		loadError.value = e?.messages?.[0] || e?.message || 'Email preparation failed'
	} finally {
		emailing.value = false
	}
}
</script>

<style scoped>
.eod-report {
	scroll-behavior: smooth;
}

/* Print styles — produce a clean Z-Report layout */
@media print {
	.eod-report :deep(.no-print) {
		display: none !important;
	}
	.eod-report :deep(.eod-section),
	.eod-report section {
		break-inside: avoid;
	}
	.eod-report :deep(.premium-card) {
		box-shadow: none !important;
		border: 1px solid #ddd !important;
	}
	.print-only {
		display: block !important;
	}
	body {
		background: #fff !important;
	}
}

.print-only {
	display: none;
}
</style>
