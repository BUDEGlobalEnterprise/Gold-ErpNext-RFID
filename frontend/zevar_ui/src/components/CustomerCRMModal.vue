<template>
	<Teleport to="body">
		<Transition name="modal">
			<div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-6"
				@keydown.escape="emit('close')" tabindex="-1">
				<div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="emit('close')"></div>
				<div class="relative w-full max-w-7xl max-h-[96vh] bg-[#FAF5EE] dark:bg-[#1a1610] rounded-2xl shadow-2xl overflow-hidden border border-[#E8E0D4] dark:border-warm-border flex flex-col">
					<!-- Loading -->
					<div v-if="loading" class="flex-1 flex items-center justify-center min-h-[400px]">
						<div class="flex flex-col items-center gap-3">
							<div class="animate-spin rounded-full h-10 w-10 border-2 border-gray-200 border-t-[#D4AF37]"></div>
							<span class="text-sm text-gray-400">Loading customer profile...</span>
						</div>
					</div>
					<!-- Error -->
					<div v-else-if="error" class="flex-1 flex items-center justify-center min-h-[400px] p-6">
						<div class="text-center">
							<p class="text-sm text-red-500 mb-3">{{ error }}</p>
							<button @click="reload" class="px-4 py-2 bg-[#D4AF37] text-white rounded-lg text-sm font-medium hover:bg-[#C4A030] transition">Retry</button>
						</div>
					</div>
					<!-- Loaded -->
					<template v-else-if="profile">
						<!-- Header -->
						<div class="flex items-center justify-between px-5 py-3 bg-white dark:bg-warm-dark-800 border-b border-gray-100 dark:border-warm-border/50">
							<div class="flex items-center gap-4">
								<div class="w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0" :style="{ backgroundColor: statusColor }">{{ initials }}</div>
								<div class="min-w-0">
									<div class="flex items-center gap-2 flex-wrap">
										<h2 class="text-lg font-bold text-gray-900 dark:text-white truncate">{{ profile.customer_name }}</h2>
										<span class="px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide" :class="statusBadgeClass">{{ profile.customer_status || 'Regular' }}</span>
									</div>
									<div class="flex items-center gap-3 mt-0.5 text-xs text-gray-500 dark:text-gray-400">
										<span v-if="profile.mobile_no">{{ profile.mobile_no }}</span>
										<span v-if="profile.email_id">{{ profile.email_id }}</span>
										<span v-if="profile.customer_group" class="px-1.5 py-0.5 bg-gray-100 dark:bg-warm-dark-700 rounded">{{ profile.customer_group }}</span>
										<span v-if="profile.customer_since" class="text-gray-400">Since {{ profile.customer_since }}</span>
									</div>
								</div>
							</div>
							<div class="flex items-center gap-2 flex-shrink-0">
								<a v-if="hasCRMLead" :href="'/app/crm-lead/' + pipeline?.lead?.name" target="_blank" class="px-3 py-1.5 text-xs font-bold bg-[#7c3aed]/10 text-[#7c3aed] rounded-lg hover:bg-[#7c3aed]/20 transition">Open Lead</a>
								<a v-if="hasCRMDeal" :href="'/app/crm-deal/' + pipeline?.deal?.name" target="_blank" class="px-3 py-1.5 text-xs font-bold bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 rounded-lg hover:bg-emerald-100 transition">Open Deal</a>
								<button @click="emit('close')" class="p-1.5 hover:bg-gray-100 dark:hover:bg-warm-dark-700 rounded-full transition">
									<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
								</button>
							</div>
						</div>
						<!-- Tabs -->
						<div class="flex border-b border-gray-100 dark:border-warm-border/50 bg-white dark:bg-warm-dark-800 px-3 gap-0.5 overflow-x-auto">
							<button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
								:class="['px-4 py-2.5 text-xs font-bold uppercase tracking-wider transition-colors border-b-2 -mb-px whitespace-nowrap',
									activeTab === tab.key ? 'border-[#D4AF37] text-[#D4AF37]' : 'border-transparent text-gray-400 hover:text-gray-600']">
								{{ tab.label }}
								<span v-if="tab.badge" class="ml-1 px-1.5 py-0.5 rounded-full text-[10px] bg-[#D4AF37]/10 text-[#D4AF37]">{{ tab.badge }}</span>
							</button>
						</div>
						<!-- Tab Content -->
						<div class="flex-1 overflow-y-auto p-4 min-h-0">

							<!-- ===== OVERVIEW ===== -->
							<div v-if="activeTab === 'overview'" class="space-y-4">
								<div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
									<kpi-card label="Lifetime Value" :value="formatCurrency(profile.lifetime_value || profile.total_spent)" />
									<kpi-card label="YTD Spend" :value="formatCurrency(profile.ytd_spend)" />
									<kpi-card label="Total Visits" :value="String(profile.visit_count)" />
									<kpi-card label="Avg Ticket" :value="formatCurrency(profile.avg_order_value)" />
									<kpi-card label="Loyalty Points" :value="String(loyalty?.points || 0)" accent />
									<kpi-card label="A/R Outstanding" :value="formatCurrency(arBalance?.total_outstanding)" :accent="arBalance?.total_outstanding > 0" />
									<kpi-card label="Active Repairs" :value="String(activeRepairs)" />
									<kpi-card label="Active Layaways" :value="String(activeLayaways)" />
								</div>
								<!-- Dates -->
								<div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
									<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
										<div class="text-xs text-gray-400 uppercase tracking-wider">Last Visit</div>
										<div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ profile.last_purchase_date || 'Never' }}</div>
										<div v-if="profile.days_since_last_visit" class="text-xs text-gray-400">{{ profile.days_since_last_visit }} days ago</div>
									</div>
									<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
										<div class="text-xs text-gray-400 uppercase tracking-wider">Discount Rate</div>
										<div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ profile.discount_rate || 0 }}%</div>
									</div>
									<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
										<div class="text-xs text-gray-400 uppercase tracking-wider">Sales Associate</div>
										<div class="text-sm font-bold text-gray-900 dark:text-white mt-0.5">{{ profile.salesman1 || 'Not assigned' }}</div>
									</div>
								</div>
								<!-- Upcoming Occasions -->
								<div v-if="upcomingOccasions.length" class="bg-[#D4AF37]/5 dark:bg-[#D4AF37]/10 rounded-xl p-3 border border-[#D4AF37]/20">
									<h3 class="text-xs font-bold text-[#D4AF37] uppercase tracking-wider mb-2">Upcoming Occasions</h3>
									<div v-for="occ in upcomingOccasions" :key="occ.type" class="flex items-center justify-between py-1">
										<span class="text-sm capitalize">{{ occ.type === 'birthday' ? '🎂 Birthday' : '💍 Anniversary' }}</span>
										<span class="text-sm font-bold" :class="occ.days_until <= 14 ? 'text-red-500' : 'text-[#D4AF37]'">{{ occ.days_until === 0 ? 'Today!' : occ.days_until + ' days' }}</span>
									</div>
								</div>
							</div>

							<!-- ===== PURCHASES ===== -->
							<div v-else-if="activeTab === 'purchases'">
								<empty-state v-if="!recentPurchases.length" msg="No purchase history." />
								<data-table v-else :headers="['Invoice','Date','Items','Amount','Status']" :rows="purchaseRows">
									<template #cell-0="{row}"><a :href="'/app/sales-invoice/'+row.invoice" target="_blank" class="text-[#D4AF37] hover:underline text-xs font-medium">{{ row.invoice }}</a></template>
									<template #cell-1="{row}"><span class="text-xs text-gray-600 dark:text-gray-300">{{ row.date }}</span></template>
									<template #cell-2="{row}"><span class="text-xs text-gray-500 truncate max-w-[280px] block">{{ (row.items||[]).map(i=>i.item_name).join(', ') || '—' }}</span></template>
									<template #cell-3="{row}"><span class="text-xs font-bold text-gray-900 dark:text-white">{{ formatCurrency(row.grand_total) }}</span></template>
									<template #cell-4="{row}"><span :class="row.status==='Paid'?'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600':'bg-amber-50 dark:bg-amber-900/20 text-amber-600'" class="px-1.5 py-0.5 rounded-full text-[10px] font-bold">{{ row.status }}</span></template>
								</data-table>
							</div>

							<!-- ===== LOYALTY ===== -->
							<div v-else-if="activeTab === 'loyalty'" class="space-y-4">
								<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-4 border border-gray-100 dark:border-warm-border/30 flex items-center gap-4">
									<div class="w-16 h-16 rounded-full bg-[#D4AF37]/10 flex items-center justify-center text-[#D4AF37] text-2xl font-bold">{{ loyalty?.points || 0 }}</div>
									<div>
										<div class="text-base font-bold text-gray-900 dark:text-white">Loyalty Points</div>
										<div class="text-xs text-gray-400">{{ loyalty?.program || 'No program enrolled' }}</div>
									</div>
								</div>
								<empty-state v-if="!loyalty?.history?.length" msg="No loyalty history." />
								<data-table v-else :headers="['Date','Points','Invoice','Program']" :rows="loyaltyHistoryRows">
									<template #cell-0="{row}"><span class="text-xs text-gray-600 dark:text-gray-300">{{ row.date }}</span></template>
									<template #cell-1="{row}"><span class="text-xs font-bold" :class="row.points > 0 ? 'text-emerald-600' : 'text-red-500'">{{ row.points > 0 ? '+' : '' }}{{ row.points }}</span></template>
									<template #cell-2="{row}"><span class="text-xs text-gray-500">{{ row.invoice || '—' }}</span></template>
									<template #cell-3="{row}"><span class="text-xs text-gray-400">{{ row.program || '—' }}</span></template>
								</data-table>
							</div>

							<!-- ===== SERVICES (Repairs + Layaways) ===== -->
							<div v-else-if="activeTab === 'services'" class="space-y-5">
								<!-- Repairs -->
								<div>
									<h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Repairs ({{ repairs.length }})</h3>
									<empty-state v-if="!repairs.length" msg="No repair history." />
									<data-table v-else :headers="['Order','Date','Item','Cost','Status']" :rows="repairs">
										<template #cell-0="{row}"><a :href="'/app/repair-order/'+row.name" target="_blank" class="text-[#D4AF37] hover:underline text-xs font-medium">{{ row.name }}</a></template>
										<template #cell-1="{row}"><span class="text-xs text-gray-600 dark:text-gray-300">{{ row.date }}</span></template>
										<template #cell-2="{row}"><span class="text-xs text-gray-500 truncate max-w-[250px] block">{{ row.item || '—' }}</span></template>
										<template #cell-3="{row}"><span class="text-xs font-bold text-gray-900 dark:text-white">{{ formatCurrency(row.cost) }}</span></template>
										<template #cell-4="{row}"><span :class="repairStatusClass(row.status)" class="px-1.5 py-0.5 rounded-full text-[10px] font-bold">{{ row.status }}</span></template>
									</data-table>
								</div>
								<!-- Layaways -->
								<div>
									<h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Layaways ({{ layaways.length }})</h3>
									<empty-state v-if="!layaways.length" msg="No layaway history." />
									<data-table v-else :headers="['Contract','Date','Total','Paid','Balance','Status']" :rows="layaways">
										<template #cell-0="{row}"><a :href="'/pos/layaway?contract='+row.name" target="_blank" class="text-[#D4AF37] hover:underline text-xs font-medium">{{ row.name }}</a></template>
										<template #cell-1="{row}"><span class="text-xs text-gray-600 dark:text-gray-300">{{ row.date }}</span></template>
										<template #cell-2="{row}"><span class="text-xs font-bold text-gray-900 dark:text-white">{{ formatCurrency(row.total) }}</span></template>
										<template #cell-3="{row}"><span class="text-xs text-emerald-600 font-medium">{{ formatCurrency(row.paid) }}</span></template>
										<template #cell-4="{row}"><span class="text-xs font-bold" :class="row.balance > 0 ? 'text-amber-600' : 'text-emerald-600'">{{ formatCurrency(row.balance) }}</span></template>
										<template #cell-5="{row}"><span :class="layawayStatusClass(row.status)" class="px-1.5 py-0.5 rounded-full text-[10px] font-bold">{{ row.status }}</span></template>
									</data-table>
								</div>
							</div>

							<!-- ===== ACCOUNTS (Trade-Ins + A/R) ===== -->
							<div v-else-if="activeTab === 'accounts'" class="space-y-5">
								<!-- A/R Balance -->
								<div>
									<h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Accounts Receivable — Outstanding: {{ formatCurrency(arBalance?.total_outstanding) }}</h3>
									<empty-state v-if="!arBalance?.entries?.length" msg="No outstanding balances." />
									<data-table v-else :headers="['Invoice','Date','Total','Outstanding']" :rows="arBalance?.entries || []">
										<template #cell-0="{row}"><a :href="'/app/sales-invoice/'+row.invoice" target="_blank" class="text-[#D4AF37] hover:underline text-xs font-medium">{{ row.invoice }}</a></template>
										<template #cell-1="{row}"><span class="text-xs text-gray-600 dark:text-gray-300">{{ row.date }}</span></template>
										<template #cell-2="{row}"><span class="text-xs text-gray-900 dark:text-white">{{ formatCurrency(row.total) }}</span></template>
										<template #cell-3="{row}"><span class="text-xs font-bold text-amber-600">{{ formatCurrency(row.outstanding) }}</span></template>
									</data-table>
								</div>
								<!-- Trade-Ins -->
								<div>
									<h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Trade-Ins ({{ tradeIns.length }})</h3>
									<empty-state v-if="!tradeIns.length" msg="No trade-in history." />
									<data-table v-else :headers="['Record','Date','Description','Value','Status']" :rows="tradeIns">
										<template #cell-0="{row}"><a :href="'/app/trade-in-record/'+row.name" target="_blank" class="text-[#D4AF37] hover:underline text-xs font-medium">{{ row.name }}</a></template>
										<template #cell-1="{row}"><span class="text-xs text-gray-600 dark:text-gray-300">{{ row.date }}</span></template>
										<template #cell-2="{row}"><span class="text-xs text-gray-500 truncate max-w-[250px] block">{{ row.description || '—' }}</span></template>
										<template #cell-3="{row}"><span class="text-xs font-bold text-gray-900 dark:text-white">{{ formatCurrency(row.value) }}</span></template>
										<template #cell-4="{row}"><span class="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 dark:bg-warm-dark-700 text-gray-600 dark:text-gray-300">{{ row.status }}</span></template>
									</data-table>
								</div>
							</div>

							<!-- ===== SIZES ===== -->
							<div v-else-if="activeTab === 'sizes'" class="space-y-4">
								<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-4 border border-gray-100 dark:border-warm-border/30">
									<h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-3">Ring Sizes</h3>
									<div class="grid grid-cols-3 gap-3">
										<size-display label="Ring" :value="profile.ring_size" />
										<size-display label="Left" :value="profile.ring_left_size" />
										<size-display label="Right" :value="profile.ring_right_size" />
									</div>
								</div>
								<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-4 border border-gray-100 dark:border-warm-border/30">
									<h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-3">Measurements</h3>
									<div class="grid grid-cols-2 gap-3">
										<size-display label="Wrist" :value="profile.wrist_size" />
										<size-display label="Neck" :value="profile.neck_size" />
									</div>
								</div>
								<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-4 border border-gray-100 dark:border-warm-border/30">
									<h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-3">Preferences</h3>
									<div class="grid grid-cols-2 gap-3">
										<size-display label="Metal" :value="profile.preferred_metal" />
										<size-display label="Purity" :value="profile.preferred_purity" />
									</div>
									<div v-if="profile.jewelry_preferences" class="mt-3 pt-3 border-t border-gray-100 dark:border-warm-border/20">
										<div class="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Jewelry Preferences</div>
										<div class="text-xs text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ profile.jewelry_preferences }}</div>
									</div>
								</div>
							</div>

							<!-- ===== CRM ===== -->
							<div v-else-if="activeTab === 'crm'" class="space-y-4">
								<div v-if="pipeline?.lead" class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
									<div class="flex items-center justify-between mb-2">
										<h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">CRM Lead</h3>
										<span class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-blue-50 dark:bg-blue-900/20 text-blue-600">{{ pipeline.lead.status }}</span>
									</div>
									<div class="grid grid-cols-2 gap-2 text-[10px]"><div><span class="text-gray-400">Owner:</span> <span class="text-gray-900 dark:text-white font-medium">{{ pipeline.lead.lead_owner || '—' }}</span></div><div><span class="text-gray-400">Source:</span> <span class="text-gray-900 dark:text-white font-medium">{{ pipeline.lead.source || '—' }}</span></div></div>
								</div>
								<div v-else class="bg-gray-50 dark:bg-warm-dark-800/50 rounded-xl p-3 border border-dashed border-gray-200 dark:border-warm-border/30 text-center">
									<p class="text-[10px] text-gray-400 mb-2">No CRM Lead linked</p>
									<button @click="handleCreateLead" :disabled="creatingLead" class="px-3 py-1 text-[10px] font-bold bg-[#D4AF37] text-white rounded-lg hover:bg-[#C4A030] disabled:opacity-50 transition">{{ creatingLead ? 'Creating...' : 'Create CRM Lead' }}</button>
								</div>
								<div v-if="pipeline?.deal" class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
									<div class="flex items-center justify-between mb-2">
										<h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">CRM Deal</h3>
										<span class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600">{{ pipeline.deal.status }}</span>
									</div>
									<div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
										<div><div class="text-[9px] text-gray-400">Value</div><div class="text-xs font-bold text-gray-900 dark:text-white">{{ formatCurrency(pipeline.deal.deal_value) }}</div></div>
										<div><div class="text-[9px] text-gray-400">Probability</div><div class="text-xs font-bold text-gray-900 dark:text-white">{{ pipeline.deal.probability }}%</div></div>
										<div><div class="text-[9px] text-gray-400">Next Step</div><div class="text-[10px] font-medium text-gray-900 dark:text-white truncate">{{ pipeline.deal.next_step || '—' }}</div></div>
										<div><div class="text-[9px] text-gray-400">Owner</div><div class="text-[10px] font-medium text-gray-900 dark:text-white truncate">{{ pipeline.deal.deal_owner || '—' }}</div></div>
									</div>
								</div>
								<!-- Tasks -->
								<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
									<div class="flex items-center justify-between mb-2">
										<h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Open Tasks</h3>
										<button @click="showTaskForm = !showTaskForm" class="text-[10px] text-[#D4AF37] font-bold hover:underline">+ Add</button>
									</div>
									<div v-if="showTaskForm" class="mb-2 p-2 bg-gray-50 dark:bg-warm-dark-900/50 rounded-lg space-y-2">
										<input v-model="newTaskTitle" type="text" placeholder="Task title..." class="w-full px-2 py-1 text-[10px] border border-gray-200 dark:border-warm-border rounded-lg bg-white dark:bg-warm-dark-800 text-gray-900 dark:text-white" />
										<input v-model="newTaskDueDate" type="date" class="w-full px-2 py-1 text-[10px] border border-gray-200 dark:border-warm-border rounded-lg bg-white dark:bg-warm-dark-800 text-gray-900 dark:text-white" />
										<button @click="handleCreateTask" :disabled="creatingTask || !newTaskTitle.trim()" class="px-3 py-1 text-[9px] font-bold bg-[#D4AF37] text-white rounded-lg disabled:opacity-50">{{ creatingTask ? 'Saving...' : 'Save' }}</button>
									</div>
									<empty-state v-if="!openTasks.length && !showTaskForm" msg="No open tasks." />
									<div v-else class="space-y-1">
										<div v-for="t in openTasks" :key="t.name" class="flex items-center justify-between p-1.5 bg-gray-50 dark:bg-warm-dark-900/30 rounded-lg">
											<div class="flex items-center gap-1.5"><div :class="['w-1.5 h-1.5 rounded-full', t.priority==='High'?'bg-red-500':t.priority==='Low'?'bg-gray-300':'bg-amber-400']"></div><span class="text-[10px] font-medium text-gray-900 dark:text-white truncate">{{ t.title }}</span></div>
											<span v-if="t.due_date" class="text-[9px] text-gray-400 ml-2">{{ t.due_date }}</span>
										</div>
									</div>
								</div>
							</div>

							<!-- ===== OCCASIONS ===== -->
							<div v-else-if="activeTab === 'occasions'" class="space-y-4">
								<occasion-card emoji="🎂" label="Birthday" :date="profile.birth_date" :occasion="birthdayOccasion" />
								<occasion-card emoji="💍" label="Anniversary" :date="profile.marriage_date" :occasion="anniversaryOccasion" />
								<div v-if="profile.spouse_name" class="bg-white dark:bg-warm-dark-800 rounded-xl p-4 border border-gray-100 dark:border-warm-border/30">
									<div class="flex items-center gap-3">
										<div class="w-10 h-10 rounded-full bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-lg">👤</div>
										<div><div class="text-xs font-bold text-gray-900 dark:text-white">Spouse</div><div class="text-[10px] text-gray-400">{{ profile.spouse_name }}</div></div>
									</div>
								</div>
							</div>

							<!-- ===== NOTES ===== -->
							<div v-else-if="activeTab === 'notes'" class="space-y-4">
								<div class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
									<h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Add Note</h3>
									<textarea v-model="newNote" rows="2" placeholder="Write a note..." class="w-full px-2 py-1.5 text-[10px] border border-gray-200 dark:border-warm-border rounded-lg bg-gray-50 dark:bg-warm-dark-900 text-gray-900 dark:text-white resize-none" />
									<button @click="submitNote" :disabled="savingNote || !newNote.trim()" class="mt-1.5 px-3 py-1 text-[10px] font-bold bg-[#D4AF37] text-white rounded-lg disabled:opacity-50">{{ savingNote ? 'Saving...' : 'Save Note' }}</button>
								</div>
								<div v-if="notes" class="bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30">
									<div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">History</div>
									<div class="text-[10px] text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">{{ notes }}</div>
								</div>
								<empty-state v-else msg="No notes yet." />
							</div>
						</div>
					</template>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch, computed, defineComponent, h } from 'vue'
import { useClienteling } from '@/composables/useClienteling.js'

// --- Inline helper components ---
const KpiCard = defineComponent({
	props: { label: String, value: String, accent: Boolean },
	setup(props) {
		return () => h('div', { class: 'bg-white dark:bg-warm-dark-800 rounded-xl p-3 border border-gray-100 dark:border-warm-border/30' }, [
			h('div', { class: 'text-[10px] text-gray-400 uppercase tracking-wider font-medium' }, props.label),
			h('div', { class: `text-lg font-bold mt-0.5 ${props.accent ? 'text-[#D4AF37]' : 'text-gray-900 dark:text-white'}` }, props.value || '0'),
		])
	}
})
const EmptyState = defineComponent({
	props: { msg: String },
	setup(props) { return () => h('div', { class: 'text-center py-8 text-gray-400 text-xs' }, props.msg) }
})
const DataTable = defineComponent({
	props: { headers: Array, rows: Array },
	slots: Object,
	setup(props, { slots }) {
		return () => h('div', { class: 'bg-white dark:bg-warm-dark-800 rounded-xl border border-gray-100 dark:border-warm-border/30 overflow-x-auto' }, [
			h('table', { class: 'w-full text-sm' }, [
				h('thead', [h('tr', { class: 'border-b border-gray-100 dark:border-warm-border/30' },
					props.headers.map(hd => h('th', { class: 'text-left px-4 py-2.5 text-[10px] uppercase tracking-wider text-gray-400 font-bold' }, hd))
				)]),
				h('tbody', props.rows.map((row, ri) =>
					h('tr', { class: 'border-b border-gray-50 dark:border-warm-border/10 hover:bg-gray-50/50 dark:hover:bg-white/[0.02]', key: ri },
						props.headers.map((_, ci) => {
							const slotName = `cell-${ci}`
							if (slots[slotName]) {
								return h('td', { class: 'px-4 py-2.5' }, [slots[slotName]({ row })])
							}
							return h('td', { class: 'px-4 py-2.5 text-xs text-gray-600 dark:text-gray-300' }, String(row[Object.keys(row)[ci]] || '—'))
						})
					)
				))
			])
		])
	}
})
const SizeDisplay = defineComponent({
	props: { label: String, value: String },
	setup(props) {
		return () => h('div', [
			h('div', { class: 'text-[10px] text-gray-400 uppercase tracking-wider' }, props.label),
			h('div', { class: 'text-sm font-bold text-gray-900 dark:text-white mt-0.5' }, props.value || '—'),
		])
	}
})
const OccasionCard = defineComponent({
	props: { emoji: String, label: String, date: String, occasion: Object },
	setup(props) {
		return () => h('div', { class: 'bg-white dark:bg-warm-dark-800 rounded-xl p-4 border border-gray-100 dark:border-warm-border/30' }, [
			h('div', { class: 'flex items-center gap-3 mb-2' }, [
				h('div', { class: 'w-10 h-10 rounded-full bg-pink-50 dark:bg-pink-900/20 flex items-center justify-center text-lg' }, props.emoji),
				h('div', [
					h('div', { class: 'text-sm font-bold text-gray-900 dark:text-white' }, props.label),
					h('div', { class: 'text-xs text-gray-400' }, props.date || 'Not recorded'),
				]),
			]),
			props.occasion ? h('div', { class: `mt-2 px-3 py-2 rounded-lg ${props.occasion.days_until <= 14 ? 'bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/20' : 'bg-[#D4AF37]/5 border border-[#D4AF37]/20'}` }, [
				h('span', { class: `text-sm font-bold ${props.occasion.days_until <= 14 ? 'text-red-500' : 'text-[#D4AF37]'}` },
					props.occasion.days_until === 0 ? 'Today!' : props.occasion.days_until + ' days away'),
			]) : null,
		])
	}
})

// --- Main component ---
const props = defineProps({ show: { type: Boolean, default: false }, customerName: { type: String, default: '' } })
const emit = defineEmits(['close'])

const { customerData, loading, error, loadIntelligence, addNote, createTask, createLead,
	upcomingOccasions, profile, recentPurchases, pipeline, hasCRMLead, hasCRMDeal, openTasks } = useClienteling()

const activeTab = ref('overview')
const newNote = ref('')
const savingNote = ref(false)
const creatingLead = ref(false)
const showTaskForm = ref(false)
const newTaskTitle = ref('')
const newTaskDueDate = ref('')
const creatingTask = ref(false)

// Data accessors
const loyalty = computed(() => customerData.value?.loyalty || { points: 0, history: [] })
const repairs = computed(() => customerData.value?.repairs || [])
const layaways = computed(() => customerData.value?.layaways || [])
const tradeIns = computed(() => customerData.value?.trade_ins || [])
const arBalance = computed(() => customerData.value?.ar_balance || { total_outstanding: 0, entries: [] })
const notes = computed(() => customerData.value?.notes || '')

const activeRepairs = computed(() => repairs.value.filter(r => r.status !== 'Completed' && r.status !== 'Delivered').length)
const activeLayaways = computed(() => layaways.value.filter(l => ['Active', 'Draft', 'Overdue'].includes(l.status)).length)

const loyaltyHistoryRows = computed(() => loyalty.value?.history || [])
const purchaseRows = computed(() => recentPurchases.value)

const tabs = computed(() => [
	{ key: 'overview', label: 'Overview' },
	{ key: 'purchases', label: 'Purchases', badge: profile.value?.visit_count || null },
	{ key: 'loyalty', label: 'Loyalty', badge: loyalty.value?.points ? String(loyalty.value.points) + 'pts' : null },
	{ key: 'services', label: 'Services', badge: (repairs.value.length + layaways.value.length) || null },
	{ key: 'accounts', label: 'Accounts', badge: arBalance.value?.total_outstanding > 0 ? '!' : null },
	{ key: 'sizes', label: 'Sizes' },
	{ key: 'crm', label: 'CRM' },
	{ key: 'occasions', label: 'Occasions' },
	{ key: 'notes', label: 'Notes' },
])

const statusMap = {
	Regular: { color: '#6b7280', bg: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300' },
	Silver: { color: '#94a3b8', bg: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300' },
	Gold: { color: '#d97706', bg: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600' },
	Platinum: { color: '#7c3aed', bg: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600' },
	VIP: { color: '#059669', bg: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600' },
	Diamond: { color: '#2563eb', bg: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600' },
}
const statusColor = computed(() => statusMap[profile.value?.customer_status]?.color || '#6b7280')
const statusBadgeClass = computed(() => statusMap[profile.value?.customer_status]?.bg || statusMap.Regular.bg)
const initials = computed(() => { if (!profile.value?.customer_name) return '?'; return profile.value.customer_name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase() })
const birthdayOccasion = computed(() => upcomingOccasions.value.find(o => o.type === 'birthday'))
const anniversaryOccasion = computed(() => upcomingOccasions.value.find(o => o.type === 'anniversary'))

function repairStatusClass(s) { return s==='Completed'||s==='Delivered'?'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600':s==='In Progress'?'bg-blue-50 dark:bg-blue-900/20 text-blue-600':'bg-amber-50 dark:bg-amber-900/20 text-amber-600' }
function layawayStatusClass(s) { return s==='Active'?'bg-blue-50 dark:bg-blue-900/20 text-blue-600':s==='Completed'||s==='Paid Off'?'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600':'bg-gray-100 dark:bg-gray-800 text-gray-600' }

watch(() => props.customerName, (n) => { if (n && props.show) loadIntelligence(n) }, { immediate: true })
watch(() => props.show, (o) => { if (o && props.customerName) loadIntelligence(props.customerName); if (!o) { activeTab.value = 'overview'; newNote.value = ''; showTaskForm.value = false } })

function formatCurrency(v) { if (!v) return '$0.00'; return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v) }
function reload() { if (props.customerName) loadIntelligence(props.customerName) }
async function submitNote() { if (!newNote.value.trim()) return; savingNote.value = true; try { await addNote(props.customerName, newNote.value); newNote.value = '' } finally { savingNote.value = false } }
async function handleCreateLead() { if (!props.customerName) return; creatingLead.value = true; try { await createLead(props.customerName) } finally { creatingLead.value = false } }
async function handleCreateTask() { if (!newTaskTitle.value.trim()) return; creatingTask.value = true; try { await createTask(props.customerName, newTaskTitle.value, newTaskDueDate.value || null); newTaskTitle.value = ''; newTaskDueDate.value = ''; showTaskForm.value = false } finally { creatingTask.value = false } }
</script>

<style scoped>
.modal-enter-active,.modal-leave-active{transition:opacity .2s ease}
.modal-enter-from,.modal-leave-to{opacity:0}
.modal-enter-active>div:last-child,.modal-leave-active>div:last-child{transition:transform .2s ease,opacity .2s ease}
.modal-enter-from>div:last-child{transform:scale(.95);opacity:0}
.modal-leave-to>div:last-child{transform:scale(.95);opacity:0}
</style>
