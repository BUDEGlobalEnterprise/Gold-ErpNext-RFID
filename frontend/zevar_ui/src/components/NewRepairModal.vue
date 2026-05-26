<template>
	<BaseModal :show="true" max-width="max-w-4xl" @close="$emit('close')">
		<template #header>
			<div class="flex items-center justify-between w-full">
				<div class="flex items-center gap-3">
					<div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
						<svg class="w-6 h-6 text-[#D4AF37]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
						</svg>
					</div>
					<div>
						<h3 class="text-lg font-bold text-gray-900 dark:text-white">New Repair Intake</h3>
						<p class="text-xs text-gray-500 dark:text-gray-400">Create a secure, comprehensive jewelry repair order</p>
					</div>
				</div>
				<button
					type="button"
					@click="showRepairTypeManager = true"
					class="px-3 py-1.5 text-xs bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-800/30 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/40 transition font-medium"
				>
					Manage Repair Types
				</button>
			</div>
		</template>

		<!-- Stepper Tabs -->
		<div class="border-b border-gray-100 dark:border-warm-border/50 bg-gray-50/50 dark:bg-warm-dark-900/30 px-6 py-3 flex-shrink-0 flex items-center justify-between">
			<div class="flex gap-4 w-full justify-around sm:justify-start sm:gap-8">
				<button
					v-for="tab in tabs"
					:key="tab.id"
					type="button"
					@click="activeTab = tab.id"
					class="flex items-center gap-2 pb-2 text-sm font-semibold transition relative whitespace-nowrap"
					:class="activeTab === tab.id ? 'text-[#D4AF37]' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200'"
				>
					<span class="w-5 h-5 flex items-center justify-center rounded-full text-xs font-bold"
						:class="activeTab === tab.id ? 'bg-[#D4AF37] text-black' : 'bg-gray-200 dark:bg-warm-dark-800 text-gray-500'"
					>
						{{ tab.num }}
					</span>
					<span>{{ tab.label }}</span>
					<span
						v-if="activeTab === tab.id"
						class="absolute bottom-0 left-0 w-full h-0.5 bg-[#D4AF37]"
					></span>
				</button>
			</div>
		</div>

		<div class="p-6 overflow-y-auto max-h-[60vh] custom-scrollbar">
			<div v-if="errorMsg" class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30 rounded-lg text-sm text-red-700 dark:text-red-400">
				{{ errorMsg }}
			</div>

			<!-- TAB 1: Customer & Logistics -->
			<div v-if="activeTab === 'logistics'" class="space-y-6">
				<!-- Customer Section -->
				<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-5 border border-gray-100 dark:border-warm-border/30">
					<div class="flex items-center justify-between mb-3">
						<label class="block text-sm font-bold text-gray-700 dark:text-gray-300">Customer Selection *</label>
						<button
							type="button"
							@click="showNewCustomerModal = true"
							class="text-xs px-2.5 py-1 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-[#c9a432] transition flex items-center gap-1"
						>
							<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							New Customer
						</button>
					</div>

					<div class="relative">
						<input
							v-model="customerSearch"
							type="text"
							placeholder="Search customer by name or phone..."
							@input="searchCustomers"
							class="w-full px-3 py-2.5 pl-10 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
						/>
						<svg class="w-4 h-4 text-gray-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>

						<div
							v-if="customerResults.length > 0"
							class="absolute z-50 w-full mt-1 bg-white dark:bg-warm-dark-900 border border-gray-100 dark:border-gray-800 rounded-lg shadow-xl max-h-48 overflow-y-auto"
						>
							<button
								v-for="c in customerResults"
								:key="c.name"
								type="button"
								@click="selectCustomer(c)"
								class="w-full px-4 py-2.5 text-left text-sm hover:bg-gray-50 dark:hover:bg-warm-dark-800 border-b border-gray-50 dark:border-gray-800 last:border-0 flex justify-between items-center"
							>
								<div>
									<span class="font-bold text-gray-800 dark:text-gray-200">{{ c.customer_name }}</span>
									<span v-if="c.is_repeat" class="ml-2 text-[10px] bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 px-2 py-0.5 rounded-full font-bold">✨ Repeat Client</span>
								</div>
								<span class="text-gray-400 text-xs font-mono">{{ c.mobile_no || c.phone || '' }}</span>
							</button>
						</div>
					</div>

					<!-- Selected Customer Badge -->
					<div v-if="form.customer" class="mt-3 p-3 bg-white dark:bg-warm-dark-900/80 rounded-lg border border-gray-100 dark:border-gray-800/80 flex items-center justify-between">
						<div class="flex items-center gap-2">
							<div class="w-2 h-2 rounded-full bg-green-500"></div>
							<span class="text-sm font-bold text-gray-800 dark:text-gray-200">{{ form.customer_name }}</span>
							<span v-if="customerRepairHistory.length > 0" class="text-xs text-amber-500 font-bold bg-amber-50 dark:bg-amber-900/10 px-2 py-0.5 rounded">
								{{ customerRepairHistory.length }} past repairs
							</span>
						</div>
						<button
							v-if="customerRepairHistory.length > 0"
							type="button"
							@click="showHistory = !showHistory"
							class="text-xs text-blue-600 hover:text-blue-700 font-bold hover:underline"
						>
							{{ showHistory ? 'Hide history' : 'View history timeline' }}
						</button>
					</div>

					<!-- Customer History Timeline -->
					<div v-if="showHistory && customerRepairHistory.length > 0" class="mt-3 p-3 bg-white dark:bg-warm-dark-900 rounded-lg border border-gray-100 dark:border-gray-800 text-xs">
						<p class="font-bold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-1.5">
							<svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							Previous Repairs History
						</p>
						<div class="space-y-3 relative border-l border-gray-100 dark:border-gray-800 ml-2 pl-4">
							<div v-for="h in customerRepairHistory" :key="h.name" class="relative">
								<div class="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-gray-300 dark:bg-gray-700"></div>
								<div class="flex justify-between items-start">
									<div>
										<span class="font-bold text-gray-800 dark:text-gray-200">{{ h.repair_type_name }}</span>
										<p class="text-gray-400 mt-0.5 text-[10px]">{{ h.item_description || 'No description' }}</p>
									</div>
									<div class="text-right">
										<span class="px-2 py-0.5 rounded text-[10px] font-bold"
											:class="h.status === 'Delivered' ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400' : 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'"
										>
											{{ h.status }}
										</span>
										<p class="text-[9px] text-gray-400 font-mono mt-1">{{ formatDate(h.creation) }}</p>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Logistics Details Grid -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-5 border border-gray-100 dark:border-warm-border/30">
					<!-- Store Location / Warehouse -->
					<div>
						<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Receiving Store *</label>
						<select
							v-model="form.warehouse"
							required
							class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37]"
						>
							<option v-for="loc in storeLocations" :key="loc.name" :value="loc.name">
								{{ loc.warehouse_name || loc.name }}
							</option>
						</select>
					</div>

					<!-- Handled By -->
					<div>
						<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Intake Employee</label>
						<select
							v-model="form.handled_by"
							class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37]"
						>
							<option v-for="t in technicians" :key="t.value" :value="t.value">
								{{ t.label }}
							</option>
						</select>
					</div>

					<!-- Promised Date & Presets -->
					<div>
						<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Expected Date *</label>
						<input
							v-model="form.promised_date"
							type="date"
							required
							class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent mb-2"
						/>
						<div class="flex gap-1.5">
							<button
								v-for="p in datePresets"
								:key="p.days"
								type="button"
								@click="setPromisedDatePreset(p.days)"
								class="flex-1 py-1 text-[10px] bg-white dark:bg-warm-dark-900 border border-gray-100 dark:border-gray-800 hover:border-[#D4AF37] rounded font-bold text-gray-600 dark:text-gray-300 hover:text-[#D4AF37] dark:hover:text-[#D4AF37] transition"
							>
								{{ p.label }}
							</button>
						</div>
					</div>

					<!-- Priority Group -->
					<div>
						<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">Priority Level</label>
						<div class="grid grid-cols-4 gap-1.5">
							<button
								v-for="p in priorityOptions"
								:key="p.value"
								type="button"
								@click="form.priority = p.value"
								class="py-2.5 text-xs font-bold rounded-lg border transition flex flex-col items-center gap-1"
								:class="form.priority === p.value ? p.activeClass : 'bg-white dark:bg-warm-dark-900 border-gray-100 dark:border-gray-800 text-gray-600 dark:text-gray-400 hover:border-gray-200'"
							>
								<span class="w-2 h-2 rounded-full" :class="p.bulletClass"></span>
								{{ p.value }}
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- TAB 2: Jewelry Specs & Gemstones -->
			<div v-if="activeTab === 'jewelry'" class="space-y-6">
				<!-- Item Type & Metal details -->
				<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-5 border border-gray-100 dark:border-warm-border/30">
					<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">Item Type Selector *</label>
					
					<!-- Interactive Item Grid -->
					<div class="grid grid-cols-3 sm:grid-cols-5 gap-2 mb-4">
						<button
							v-for="type in itemTypes"
							:key="type.name"
							type="button"
							@click="form.item_type = type.name"
							class="p-3 border rounded-xl flex flex-col items-center gap-2 hover:border-[#D4AF37] transition text-center focus:outline-none"
							:class="form.item_type === type.name ? 'border-[#D4AF37] bg-[#D4AF37]/5 text-[#D4AF37] font-bold shadow-sm' : 'border-gray-100 dark:border-gray-800/80 bg-white dark:bg-warm-dark-900 text-gray-600 dark:text-gray-300 hover:bg-gray-50/50 dark:hover:bg-warm-dark-800/30'"
						>
							<span v-html="type.icon" class="w-6 h-6 flex items-center justify-center text-gray-400 dark:text-gray-500" :class="{ 'text-[#D4AF37] dark:text-[#D4AF37]': form.item_type === type.name }"></span>
							<span class="text-[10px] uppercase tracking-wider font-bold">{{ type.name }}</span>
						</button>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
						<!-- Metal Type Link -->
						<div>
							<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Metal Type</label>
							<select
								v-model="form.metal_type"
								class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37]"
							>
								<option value="">None / Not Applicable</option>
								<option v-for="m in metals" :key="m.name" :value="m.name">
									{{ m.name }}
								</option>
							</select>
						</div>

						<!-- Purity -->
						<div>
							<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Purity</label>
							<select
								v-model="form.purity"
								class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37]"
							>
								<option value="">Select Purity...</option>
								<option>10K</option>
								<option>14K</option>
								<option>18K</option>
								<option>22K</option>
								<option>24K</option>
								<option>925 Silver</option>
								<option>950 Platinum</option>
								<option>999 Fine</option>
							</select>
						</div>

						<!-- Brand / Designer -->
						<div>
							<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Brand / Designer</label>
							<input
								v-model="form.item_brand"
								type="text"
								placeholder="e.g., Rolex, Tiffany, Cartier"
								class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37]"
							/>
						</div>
					</div>
				</div>

				<!-- Physical State & Weights -->
				<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-5 border border-gray-100 dark:border-warm-border/30 space-y-4">
					<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
						<!-- Item Weight -->
						<div>
							<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Gross Item Weight (g) *</label>
							<div class="relative">
								<input
									v-model.number="form.item_weight"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									class="w-full px-3 py-2 pr-8 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 font-mono text-sm focus:ring-2 focus:ring-[#D4AF37]"
								/>
								<span class="text-xs text-gray-400 absolute right-3 top-2.5">g</span>
							</div>
						</div>

						<!-- Stone Weight -->
						<div>
							<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Total Stone Weight (ct)</label>
							<div class="relative">
								<input
									v-model.number="form.stone_weight"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									class="w-full px-3 py-2 pr-10 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 font-mono text-sm focus:ring-2 focus:ring-[#D4AF37]"
								/>
								<span class="text-xs text-gray-400 absolute right-3 top-2.5">ct</span>
							</div>
						</div>

						<!-- Serial Number -->
						<div>
							<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Serial Number</label>
							<input
								v-model="form.serial_number"
								type="text"
								placeholder="For luxury watches / designer items"
								class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm focus:ring-2 focus:ring-[#D4AF37]"
							/>
						</div>
					</div>

					<!-- Gold weight alert validation warning banner -->
					<div v-if="showWeightWarning" class="p-3.5 bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-900/20 rounded-lg flex items-start gap-3">
						<svg class="w-5 h-5 text-amber-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
						<div>
							<span class="text-xs font-bold text-amber-800 dark:text-amber-400">Precision Intake Alert</span>
							<p class="text-[11px] text-amber-700 dark:text-amber-500 mt-0.5">Metal type is selected but gross weight is missing. Documenting exact gram weight protects your store against weight-swap claims at pickup.</p>
						</div>
					</div>

					<!-- Intake Condition Quick-Select Checklist -->
					<div>
						<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">Quick Intake Condition Checklist</label>
						<div class="flex flex-wrap gap-1.5">
							<button
								v-for="cond in conditionPresets"
								:key="cond"
								type="button"
								@click="toggleCondition(cond)"
								class="px-3 py-1.5 text-xs font-semibold rounded-full border transition-all"
								:class="isConditionSelected(cond)
									? 'bg-[#D4AF37] border-[#D4AF37] text-black shadow-sm font-bold'
									: 'bg-white dark:bg-warm-dark-900 border-gray-100 dark:border-gray-800 text-gray-600 dark:text-gray-400 hover:border-gray-200'"
							>
								{{ cond }}
							</button>
						</div>
					</div>

					<!-- Condition Textarea -->
					<div>
						<label class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Detailed Item Condition Description</label>
						<textarea
							v-model="form.item_condition"
							rows="2"
							placeholder="Describe scratches, worn prongs, chipped stones, etc. in detail..."
							class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none focus:ring-2 focus:ring-[#D4AF37]"
						></textarea>
					</div>
				</div>

				<!-- Gemstones Section -->
				<div class="bg-purple-50/50 dark:bg-purple-900/10 rounded-xl p-5 border border-purple-100 dark:border-purple-900/20">
					<div class="flex items-center justify-between mb-3">
						<div class="flex items-center gap-2">
							<span class="text-xl">💎</span>
							<h4 class="text-sm font-bold text-purple-800 dark:text-purple-400">Gemstone Breakdown Checklist</h4>
						</div>
						<button
							type="button"
							@click="addGemstone"
							class="text-xs px-2.5 py-1.5 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-700 transition flex items-center gap-1"
						>
							<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
							</svg>
							Add Stone
						</button>
					</div>

					<p v-if="form.gemstones.length === 0" class="text-xs text-purple-500/80 dark:text-purple-400/60 text-center py-6 bg-white dark:bg-warm-dark-900 rounded-lg border border-purple-50 dark:border-purple-950/20">
						No gemstones registered. Click "Add Stone" to record diamonds, rubies, etc.
					</p>

					<div v-else class="space-y-3 max-h-60 overflow-y-auto custom-scrollbar pr-1">
						<div
							v-for="(stone, idx) in form.gemstones"
							:key="idx"
							class="bg-white dark:bg-warm-dark-900 rounded-xl p-3 border border-purple-50 dark:border-purple-950/30 text-xs shadow-sm"
						>
							<div class="flex items-center justify-between border-b border-gray-50 dark:border-gray-800 pb-2 mb-2.5">
								<span class="font-bold text-purple-700 dark:text-purple-400">Stone #{{ idx + 1 }}</span>
								<button
									type="button"
									@click="removeGemstone(idx)"
									class="text-[10px] text-red-500 hover:text-red-700 hover:underline font-bold"
								>
									Remove Stone
								</button>
							</div>

							<div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
								<!-- Stone Type -->
								<div>
									<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">Type *</label>
									<select
										v-model="stone.gemstone_type"
										class="w-full px-1.5 py-1.5 border rounded bg-white dark:bg-warm-dark-900 text-xs focus:ring-1 focus:ring-purple-500"
									>
										<option value="">-- Type --</option>
										<option>Diamond</option>
										<option>Ruby</option>
										<option>Sapphire</option>
										<option>Emerald</option>
										<option>Alexandrite</option>
										<option>Pearl</option>
										<option>Opal</option>
										<option>Garnet</option>
										<option>Topaz</option>
										<option>Amethyst</option>
										<option>Citrine</option>
										<option>Aquamarine</option>
										<option>Tourmaline</option>
										<option>Peridot</option>
										<option>Tanzanite</option>
										<option>Zircon</option>
										<option>Jade</option>
										<option>Moonstone</option>
										<option>Other</option>
									</select>
								</div>

								<!-- Qty -->
								<div>
									<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">Quantity</label>
									<input
										v-model.number="stone.quantity"
										type="number"
										min="1"
										placeholder="Qty"
										class="w-full px-1.5 py-1.5 border rounded bg-white dark:bg-warm-dark-900 text-xs text-right font-mono"
									/>
								</div>

								<!-- Carats -->
								<div>
									<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">Carat Wt</label>
									<input
										v-model.number="stone.carat_weight"
										type="number"
										step="0.01"
										placeholder="ct"
										class="w-full px-1.5 py-1.5 border rounded bg-white dark:bg-warm-dark-900 text-xs text-right font-mono"
									/>
								</div>

								<!-- Color -->
								<div>
									<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">Color</label>
									<select
										v-model="stone.color"
										class="w-full px-1.5 py-1.5 border rounded bg-white dark:bg-warm-dark-900 text-xs"
									>
										<option value="">--</option>
										<option>D</option>
										<option>E</option>
										<option>F</option>
										<option>G</option>
										<option>H</option>
										<option>I</option>
										<option>J</option>
										<option>K</option>
										<option>L</option>
										<option>M</option>
										<option>N-Z</option>
										<option>Fancy Yellow</option>
										<option>Fancy Pink</option>
										<option>Fancy Blue</option>
										<option>Fancy Green</option>
										<option>Other</option>
									</select>
								</div>

								<!-- Clarity -->
								<div>
									<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">Clarity</label>
									<select
										v-model="stone.clarity"
										class="w-full px-1.5 py-1.5 border rounded bg-white dark:bg-warm-dark-900 text-xs"
									>
										<option value="">--</option>
										<option>FL</option>
										<option>IF</option>
										<option>VVS1</option>
										<option>VVS2</option>
										<option>VS1</option>
										<option>VS2</option>
										<option>SI1</option>
										<option>SI2</option>
										<option>I1</option>
										<option>I2</option>
										<option>I3</option>
									</select>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- TAB 3: Estimate, Compliance & Waivers -->
			<div v-if="activeTab === 'pricing'" class="space-y-6">
				<!-- Service details -->
				<div class="bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-5 border border-gray-100 dark:border-warm-border/30 space-y-4">
					<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
						<!-- Repair Category Grouped Selector (POS Dual-Panel Design) -->
						<div class="flex flex-col h-full space-y-3">
							<div class="flex items-center justify-between">
								<label class="block text-sm font-bold text-gray-700 dark:text-gray-300">Select Service Type *</label>
								<span 
									v-if="recommendedRepairTypes.length > 0" 
									class="text-[10px] bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 px-2 py-0.5 rounded-full font-bold flex items-center gap-1 shrink-0 animate-pulse"
								>
									⚡ Smart Suggestions Loaded
								</span>
							</div>
							
							<!-- Search Input -->
							<div class="relative">
								<input
									v-model="repairTypeSearch"
									type="text"
									placeholder="Search services instantly (e.g., soldering, sizing)..."
									class="w-full pl-9 pr-8 py-2 border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-warm-dark-900 text-xs focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent placeholder-gray-400"
								/>
								<span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
									<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round"/></svg>
								</span>
								<button 
									v-if="repairTypeSearch || selectedCategory" 
									type="button"
									@click="clearFilters"
									class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 font-extrabold text-sm"
								>
									✕
								</button>
							</div>

							<!-- Category Sidebar + Service Grid -->
							<div class="grid grid-cols-12 gap-3 h-52">
								<!-- Left Category Sidebar Tabs -->
								<div class="col-span-4 overflow-y-auto pr-1 border-r border-gray-100 dark:border-gray-800 space-y-1 scrollbar-thin">
									<button
										type="button"
										@click="selectedCategory = ''"
										class="w-full text-left px-2 py-1.5 rounded-lg text-[10px] font-bold transition-all truncate"
										:class="!selectedCategory 
											? 'bg-[#D4AF37]/10 text-[#D4AF37] border-l-2 border-[#D4AF37]' 
											: 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-warm-dark-800'"
									>
										All Services
									</button>
									<button
										v-for="cat in repairCategories"
										:key="cat"
										type="button"
										@click="selectedCategory = cat"
										class="w-full text-left px-2 py-1.5 rounded-lg text-[10px] font-semibold transition-all truncate"
										:class="selectedCategory === cat 
											? 'bg-[#D4AF37]/10 text-[#D4AF37] border-l-2 border-[#D4AF37]' 
											: 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-warm-dark-800'"
										:title="cat"
									>
										{{ cat }}
									</button>
								</div>

								<!-- Right Service Grid Panel -->
								<div class="col-span-8 overflow-y-auto p-1 bg-white dark:bg-warm-dark-900/20 border border-gray-200 dark:border-gray-700/60 rounded-xl space-y-1">
									<!-- Smart Recommendations Section -->
									<div v-if="recommendedRepairTypes.length > 0" class="mb-3 pb-3 border-b border-gray-100 dark:border-warm-border/30">
										<div class="flex items-center gap-1.5 px-2 py-1.5 mb-1 bg-amber-50/40 dark:bg-amber-950/5 rounded-lg border border-amber-200/20 dark:border-amber-900/10">
											<span class="text-xs">✨</span>
											<span class="text-[10px] font-extrabold uppercase tracking-wider text-amber-500">Smart Suggestions</span>
											<span class="text-[8px] bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 px-1.5 py-0.5 rounded-full font-bold">Based on Intake Checklist</span>
										</div>
										<div class="space-y-1">
											<button
												v-for="rt in recommendedRepairTypes"
												:key="'rec-' + rt.name"
												type="button"
												@click="form.repair_type = rt.name"
												class="w-full flex justify-between items-center p-2 rounded-lg text-left transition-all border outline-none group"
												:class="form.repair_type === rt.name 
													? 'bg-amber-50/50 dark:bg-amber-950/15 border-[#D4AF37] text-amber-900 dark:text-amber-300 font-extrabold shadow-sm'
													: 'bg-amber-500/[0.03] dark:bg-amber-500/[0.01] border-dashed border-amber-200 dark:border-amber-900/30 hover:border-amber-400 dark:hover:border-amber-800 text-gray-700 dark:text-gray-300 hover:bg-amber-500/[0.08] dark:hover:bg-amber-500/[0.03]'"
											>
												<div class="pr-2 truncate">
													<div class="flex items-center gap-1.5 truncate">
														<span v-if="form.repair_type === rt.name" class="text-amber-500 font-extrabold flex-shrink-0">✓</span>
														<span class="font-bold text-[11px] group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">{{ rt.repair_name || rt.name }}</span>
													</div>
													<div class="text-[9px] text-gray-400 font-normal uppercase tracking-wider mt-0.5">{{ rt.category || 'General' }}</div>
												</div>
												<div class="text-right flex-shrink-0">
													<span class="font-bold font-mono text-[11px] text-gray-900 dark:text-gray-100 bg-white dark:bg-warm-dark-900 px-1.5 py-0.5 border border-gray-100 dark:border-gray-800 rounded-md">${{ rt.base_price || 0 }}</span>
													<div v-if="rt.estimated_days" class="text-[8px] text-gray-400 font-normal mt-0.5">{{ rt.estimated_days }}d turnaround</div>
												</div>
											</button>
										</div>
									</div>

									<!-- Empty State -->
									<div v-if="filteredRepairTypes.length === 0" class="text-center py-8 text-gray-400 text-xs">
										<p class="mb-1.5">No matching services.</p>
										<button 
											type="button"
											@click="clearFilters"
											class="text-amber-500 hover:underline font-bold text-xs"
										>
											Clear Filters
										</button>
									</div>

									<!-- Touch Cards -->
									<button
										v-for="rt in filteredRepairTypes"
										:key="rt.name"
										type="button"
										@click="form.repair_type = rt.name"
										class="w-full flex justify-between items-center p-2 rounded-lg text-left transition-all border outline-none group"
										:class="form.repair_type === rt.name 
											? 'bg-amber-50/50 dark:bg-amber-950/15 border-[#D4AF37] text-amber-900 dark:text-amber-300 font-extrabold shadow-sm'
											: 'bg-gray-50/60 dark:bg-warm-dark-800/20 border-transparent hover:border-gray-200 dark:hover:border-warm-border text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-warm-dark-800'"
									>
										<div class="pr-2 truncate">
											<div class="flex items-center gap-1.5 truncate">
												<span v-if="form.repair_type === rt.name" class="text-amber-500 font-extrabold flex-shrink-0">✓</span>
												<span class="font-bold text-[11px] group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">{{ rt.repair_name || rt.name }}</span>
											</div>
											<div class="text-[9px] text-gray-400 font-normal uppercase tracking-wider mt-0.5">{{ rt.category || 'General' }}</div>
										</div>
										<div class="text-right flex-shrink-0">
											<span class="font-bold font-mono text-[11px] text-gray-900 dark:text-gray-100 bg-white dark:bg-warm-dark-900 px-1.5 py-0.5 border border-gray-100 dark:border-gray-800 rounded-md">${{ rt.base_price || 0 }}</span>
											<div v-if="rt.estimated_days" class="text-[8px] text-gray-400 font-normal mt-0.5">{{ rt.estimated_days }}d turnaround</div>
										</div>
									</button>
								</div>
							</div>

							<!-- Hidden Input for HTML5 Validation -->
							<input type="text" class="sr-only" v-model="form.repair_type" required />

							<!-- Active Service Details & Turnaround Preview -->
							<div
								v-if="selectedRepairType"
								class="p-2.5 bg-amber-500/5 dark:bg-amber-500/[0.02] border border-[#D4AF37]/20 rounded-xl space-y-1 text-xs"
							>
								<div class="flex justify-between items-center">
									<span class="text-gray-400">Selected Service:</span>
									<span class="font-bold text-[#D4AF37]">{{ selectedRepairType.repair_name || selectedRepairType.name }}</span>
								</div>
								<div class="grid grid-cols-2 gap-2 pt-1 border-t border-gray-100 dark:border-gray-800/80">
									<div class="flex justify-between items-center">
										<span class="text-gray-400">Standard Price:</span>
										<span class="font-bold text-gray-900 dark:text-gray-100 font-mono">${{ selectedRepairType.base_price || 0 }}</span>
									</div>
									<div class="flex justify-between items-center">
										<span class="text-gray-400">Turnaround:</span>
										<span class="font-bold text-gray-900 dark:text-gray-100">{{ selectedRepairType.estimated_days || 3 }} days</span>
									</div>
								</div>
								<p v-if="selectedRepairType.description" class="text-[10px] text-gray-400 pt-1 border-t border-gray-100 dark:border-gray-800/80 italic">
									{{ selectedRepairType.description }}
								</p>
							</div>
						</div>

						<!-- Repair Description & Notes Presets -->
						<div>
							<label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Detailed Description of Work</label>
							<div class="flex flex-wrap gap-1 mb-2">
								<button
									v-for="(template, idx) in noteTemplates"
									:key="idx"
									type="button"
									@click="addNoteTemplate(template)"
									class="px-2 py-1 text-[10px] bg-white dark:bg-warm-dark-900 border border-gray-100 dark:border-gray-800 hover:border-gray-200 rounded font-semibold text-gray-500 hover:text-gray-800 transition"
								>
									+ {{ template.label }}
								</button>
							</div>
							<textarea
								v-model="form.item_description"
								rows="3"
								placeholder="Enter full jeweler instructions and customer request details..."
								class="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 text-sm resize-none focus:ring-2 focus:ring-[#D4AF37]"
							></textarea>
						</div>
					</div>
				</div>

				<!-- Financial Breakdown & Deposit -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 dark:bg-warm-dark-900/50 rounded-xl p-5 border border-gray-100 dark:border-warm-border/30">
					<!-- Detailed Cost Estimator -->
					<div>
						<h4 class="text-sm font-bold text-gray-800 dark:text-gray-200 mb-3">Cost Breakdown</h4>
						<div class="space-y-3">
							<div class="flex items-center justify-between">
								<label class="text-xs font-semibold text-gray-500">Labor Cost ($)</label>
								<input
									v-model.number="form.labor_cost"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									@input="updateTotalCost"
									class="w-32 px-2.5 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 font-mono text-sm text-right focus:ring-2 focus:ring-[#D4AF37]"
								/>
							</div>
							<div class="flex items-center justify-between">
								<label class="text-xs font-semibold text-gray-500">Materials Cost ($)</label>
								<input
									v-model.number="form.material_cost"
									type="number"
									step="0.01"
									min="0"
									placeholder="0.00"
									@input="updateTotalCost"
									class="w-32 px-2.5 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-warm-dark-900 font-mono text-sm text-right focus:ring-2 focus:ring-[#D4AF37]"
								/>
							</div>
							<div class="flex items-center justify-between border-t border-gray-200/50 pt-2">
								<label class="text-sm font-bold text-gray-700 dark:text-gray-300">Total Estimate ($) *</label>
								<input
									v-model.number="form.estimated_cost"
									type="number"
									step="0.01"
									min="0"
									required
									placeholder="0.00"
									class="w-32 px-2.5 py-1.5 border border-[#D4AF37] rounded-lg bg-amber-50/20 dark:bg-warm-dark-900 font-mono font-extrabold text-sm text-right text-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]"
								/>
							</div>
						</div>
					</div>

					<!-- Deposit Intake (50% Standard Check) -->
					<div class="border-l border-gray-200/40 pl-0 md:pl-5 space-y-3.5">
						<h4 class="text-sm font-bold text-gray-800 dark:text-gray-200">Deposit / Advance Payment</h4>
						<label class="flex items-center gap-2 cursor-pointer">
							<input v-model="form.collect_deposit" type="checkbox" class="rounded border-gray-300 dark:border-gray-700 text-[#D4AF37] focus:ring-[#D4AF37]" />
							<span class="text-xs font-bold text-gray-700 dark:text-gray-300">Collect Intake Deposit (Standard 50%)</span>
						</label>

						<div v-if="form.collect_deposit" class="p-3 bg-white dark:bg-warm-dark-900 rounded-xl border border-gray-100 dark:border-gray-800 space-y-2">
							<div class="flex justify-between items-center">
								<label class="text-xs text-gray-500 font-medium">Recommended (50%):</label>
								<span class="text-xs font-bold font-mono text-gray-800 dark:text-gray-200">${{ recommendedDeposit }}</span>
							</div>

							<div class="grid grid-cols-2 gap-2">
								<div class="relative">
									<input
										v-model.number="form.deposit_amount"
										type="number"
										step="0.01"
										min="0"
										placeholder="Deposit"
										class="w-full px-2 py-1.5 border rounded text-xs bg-white dark:bg-warm-dark-900 text-right font-mono"
									/>
									<span class="text-[10px] text-gray-400 absolute left-2 top-2">$</span>
								</div>
								<select
									v-model="form.deposit_payment_method"
									class="px-2 py-1.5 border rounded text-xs bg-white dark:bg-warm-dark-900"
								>
									<option>Cash</option>
									<option>Credit Card</option>
									<option>Check</option>
									<option>Other</option>
								</select>
							</div>
							<div v-if="remainingBalance > 0" class="text-[10px] text-gray-400 text-right font-mono">
								Balance Due at Pickup: ${{ remainingBalance.toFixed(2) }}
							</div>
						</div>
					</div>
				</div>

				<!-- JVC Compliance & ID Verification -->
				<div class="bg-orange-50/50 dark:bg-orange-950/10 rounded-xl p-5 border border-orange-100 dark:border-orange-950/20 space-y-3">
					<div class="flex items-center gap-2">
						<span class="text-lg">🔒</span>
						<h4 class="text-sm font-bold text-orange-800 dark:text-orange-400">Customer ID Verification (JVC Compliance)</h4>
					</div>
					<p class="text-[10px] text-orange-600 dark:text-orange-500">AML and Patriot Act guidelines require valid identification verification for high-value custom work or precious metal custody.</p>
					
					<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
						<div>
							<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">ID Type</label>
							<select
								v-model="form.customer_id_type"
								class="w-full px-2.5 py-1.5 border border-gray-200 dark:border-gray-800 rounded text-xs bg-white dark:bg-warm-dark-900"
							>
								<option value="">-- No ID Verified --</option>
								<option>Driver's License</option>
								<option>State ID</option>
								<option>Passport</option>
								<option>Military ID</option>
								<option>Other</option>
							</select>
						</div>
						<div>
							<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">ID Number</label>
							<input
								v-model="form.customer_id_number"
								type="text"
								placeholder="ID / License Number"
								class="w-full px-2.5 py-1.5 border border-gray-200 dark:border-gray-800 rounded text-xs bg-white dark:bg-warm-dark-900"
							/>
						</div>
						<div>
							<label class="block text-[10px] font-bold text-gray-400 uppercase mb-0.5">Issuing State</label>
							<input
								v-model="form.customer_id_state"
								type="text"
								placeholder="State e.g. CA"
								class="w-full px-2.5 py-1.5 border border-gray-200 dark:border-gray-800 rounded text-xs bg-white dark:bg-warm-dark-900"
							/>
						</div>
					</div>
				</div>

				<!-- Legal Waiver & Liability Sign-off -->
				<div class="bg-gray-100 dark:bg-warm-dark-900/80 rounded-xl p-4 border border-gray-200/50 dark:border-gray-800 text-xs text-gray-500 space-y-3">
					<p class="font-bold text-gray-700 dark:text-gray-300">Liability Waiver & Custom Repair Disclaimers</p>
					<div class="max-h-20 overflow-y-auto custom-scrollbar border-l-2 border-[#D4AF37] pl-3 leading-relaxed text-[10px] dark:text-gray-400">
						Zevar Jewelers makes every reasonable effort to safely clean and service your precious items. Clients agree that precious gemstones and prongs can become naturally brittle or fracture during stone resetting or sizing processes. Zevar Jewelers is not liable for structural stone fracturing inherent to stones during bench work. Leftover metal scrap remains bench property unless scrap pickup is explicitly requested in writing. Items unclaimed for more than 90 days from the date of promised completion are subject to private sale or salvage to cover estimated service costs.
					</div>
					<label class="flex items-center gap-2.5 cursor-pointer pt-1">
						<input v-model="form.intake_checklist_signed" type="checkbox" class="rounded border-gray-300 dark:border-gray-700 text-[#D4AF37] focus:ring-[#D4AF37]" />
						<span class="font-bold text-gray-700 dark:text-gray-300">Customer has read and signs off on the estimate, disclosures, and waivers</span>
					</label>
				</div>
			</div>
		</div>

		<template #footer>
			<div class="flex justify-between items-center w-full">
				<!-- Step Info / Progress -->
				<span class="text-xs text-gray-400 font-semibold font-mono">
					Step {{ currentStepNum }} of 3
				</span>

				<!-- Action Buttons -->
				<div class="flex gap-3">
					<button
						v-if="activeTab !== 'logistics'"
						type="button"
						@click="prevTab"
						class="px-5 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-50 dark:hover:bg-warm-dark-700 text-gray-700 dark:text-gray-300 transition"
					>
						Back
					</button>
					<button
						type="button"
						@click="$emit('close')"
						class="px-5 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-50 dark:hover:bg-warm-dark-700 text-gray-700 dark:text-gray-300 transition"
					>
						Cancel
					</button>
					<button
						v-if="activeTab !== 'pricing'"
						type="button"
						@click="nextTab"
						class="px-6 py-2.5 bg-[#D4AF37] text-black font-extrabold rounded-lg text-sm hover:bg-[#c9a432] transition"
					>
						Next Step
					</button>
					<button
						v-else
						type="button"
						:disabled="submitting || !form.intake_checklist_signed"
						@click="submit"
						class="px-8 py-2.5 bg-[#D4AF37] text-black font-extrabold rounded-lg text-sm hover:bg-[#c9a432] disabled:opacity-50 transition flex items-center justify-center gap-2"
					>
						<svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						{{ submitting ? 'Submitting Intake...' : 'Finalize & Create Order' }}
					</button>
				</div>
			</div>
		</template>
	</BaseModal>

	<!-- New Customer Modal -->
	<CustomerCreationModal
		v-if="showNewCustomerModal"
		:show="showNewCustomerModal"
		@close="showNewCustomerModal = false"
		@created="onCustomerCreated"
	/>

	<!-- Repair Type Manager Modal -->
	<RepairTypeManager
		v-if="showRepairTypeManager"
		@close="showRepairTypeManager = false"
		@created="onRepairTypeCreated"
	/>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { call, toast, createResource } from 'frappe-ui'
import { formatDate } from '@/utils/dates.js'
import { useSessionStore } from '@/stores/session.js'
import BaseModal from './BaseModal.vue'
import CustomerCreationModal from './CustomerCreationModal.vue'
import RepairTypeManager from './RepairTypeManager.vue'

const emit = defineEmits(['close', 'created'])
const session = useSessionStore()

const activeTab = ref('logistics')

const tabs = [
	{ id: 'logistics', num: 1, label: 'Customer & Store' },
	{ id: 'jewelry', num: 2, label: 'Jewelry & Gemstones' },
	{ id: 'pricing', num: 3, label: 'Pricing & Compliance' },
]

const currentStepNum = computed(() => {
	if (activeTab.value === 'logistics') return 1
	if (activeTab.value === 'jewelry') return 2
	return 3
})

function prevTab() {
	if (activeTab.value === 'pricing') activeTab.value = 'jewelry'
	else if (activeTab.value === 'jewelry') activeTab.value = 'logistics'
}

function nextTab() {
	if (activeTab.value === 'logistics') {
		activeTab.value = 'jewelry'
	} else if (activeTab.value === 'jewelry') {
		activeTab.value = 'pricing'
		
		// Smart Auto-selection logic:
		if (!form.value.repair_type && recommendedRepairTypes.value.length > 0) {
			// If there is exactly 1 recommendation, auto-select it!
			if (recommendedRepairTypes.value.length === 1) {
				form.value.repair_type = recommendedRepairTypes.value[0].name
				toast({
					title: 'Auto-Selected Service',
					message: `Selected "${recommendedRepairTypes.value[0].repair_name || recommendedRepairTypes.value[0].name}" based on Quick Intake checklist`,
					icon: 'check',
					intent: 'info',
				})
			}
		}
	}
}

const form = ref({
	customer: '',
	customer_name: '',
	customer_phone: '',
	repair_type: '',
	item_type: 'Ring',
	item_brand: '',
	serial_number: '',
	item_description: '',
	item_condition: '',
	item_weight: null,
	stone_weight: null,
	metal_type: '',
	purity: '',
	metal_weight_in: null,
	metal_weight_out: null,
	gemstones: [],
	customer_id_type: '',
	customer_id_number: '',
	customer_id_state: '',
	is_warranty_repair: false,
	original_repair_order: '',
	warranty_claim_type: '',
	estimated_cost: null,
	material_cost: null,
	labor_cost: null,
	priority: 'Medium',
	promised_date: '',
	collect_deposit: false,
	deposit_amount: null,
	deposit_payment_method: 'Cash',
	intake_checklist_signed: false,
	warehouse: '',
})

const customerSearch = ref('')
const customerResults = ref([])
const repairTypes = ref([])
const allRepairTypes = ref([])
const metals = ref([])
const storeLocations = ref([])
const technicians = ref([])
const submitting = ref(false)
const showNewCustomerModal = ref(false)
const showRepairTypeManager = ref(false)
const showHistory = ref(false)
const customerRepairHistory = ref([])
const selectedCategory = ref('')
const repairTypeSearch = ref('')
const errorMsg = ref('')

const datePresets = [
	{ label: '+7 Days', days: 7 },
	{ label: '+14 Days', days: 14 },
	{ label: '+30 Days', days: 30 },
]

const priorityOptions = [
	{ value: 'Low', bulletClass: 'bg-gray-400', activeClass: 'border-gray-400 bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-300 font-extrabold shadow-sm' },
	{ value: 'Medium', bulletClass: 'bg-yellow-400', activeClass: 'border-yellow-400 bg-yellow-50 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 font-extrabold shadow-sm' },
	{ value: 'High', bulletClass: 'bg-orange-400', activeClass: 'border-orange-400 bg-orange-50 dark:bg-orange-900 text-orange-700 dark:text-orange-300 font-extrabold shadow-sm' },
	{ value: 'Urgent', bulletClass: 'bg-red-400', activeClass: 'border-red-500 bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-300 font-extrabold shadow-sm' },
]

const itemTypes = [
	{ name: 'Ring', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="14" r="6" /><path d="M12 8l-2-3h4z" stroke-linecap="round" stroke-linejoin="round" /></svg>` },
	{ name: 'Necklace', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 4c0 6 3 10 6 10s6-4 6-10" stroke-linecap="round" /><circle cx="12" cy="15" r="1.5" fill="currentColor" /></svg>` },
	{ name: 'Bracelet', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><ellipse cx="12" cy="12" rx="8" ry="4" /><path d="M6 12a2 2 0 0 1 4 0m4 0a2 2 0 0 1 4 0" stroke-linecap="round" /></svg>` },
	{ name: 'Earring', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 4v4m0 0l-3 3.5 3 3.5 3-3.5-3-3.5z" stroke-linecap="round" stroke-linejoin="round" /></svg>` },
	{ name: 'Watch', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="5" /><path d="M12 7V3h-2h4M12 17v4h-2h4" stroke-linecap="round" stroke-linejoin="round" /></svg>` },
	{ name: 'Chain', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 15l6-6M8 10a3 3 0 0 1 4 4M12 10a3 3 0 0 1 4 4" stroke-linecap="round" stroke-linejoin="round" /></svg>` },
	{ name: 'Pendant', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 5l6 7 6-7" stroke-linecap="round" /><path d="M12 12c-1.5 2-1.5 4 0 5.5s3 1.5 3 0-1.5-3.5-3-5.5z" fill="currentColor" /></svg>` },
	{ name: 'Brooch', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="4" /><path d="M12 2v6M12 16v6M2 12h6M16 12h6" stroke-linecap="round" /></svg>` },
	{ name: 'Other', icon: `<svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z" stroke-linecap="round" stroke-linejoin="round" /></svg>` },
]

const conditionPresets = [
	'Light Scratches',
	'Deep Scratches',
	'Loose Stones',
	'Missing Stones',
	'Worn Prongs',
	'Broken Clasp',
	'Bent Band',
	'Polishing Needed'
]

const noteTemplates = [
	{ label: 'Stone Loose', text: 'Stone is loose, needs tightening' },
	{ label: 'Prong Worn', text: 'Prongs are worn, need retipping' },
	{ label: 'Clasp Broken', text: 'Clasp is broken, needs replacement' },
	{ label: 'Chain Broken', text: 'Chain is broken, needs soldering' },
	{ label: 'Sizing Down', text: 'Ring needs to be sized down' },
	{ label: 'Sizing Up', text: 'Ring needs to be sized up' },
	{ label: 'Cleaning', text: 'Professional cleaning needed' },
	{ label: 'Rhodium Plating', text: 'Rhodium plating for white gold' },
	{ label: 'Stone Missing', text: 'Stone is missing, needs replacement' },
	{ label: 'Engravement', text: 'Engravement needed' },
]

const repairTypesResource = createResource({
	url: 'zevar_core.api.get_repair_types',
	onSuccess: (data) => {
		allRepairTypes.value = data || []
		repairTypes.value = data || []
	},
})

const metalsResource = createResource({
	url: 'frappe.client.get_list',
	makeParams: () => ({
		doctype: 'Zevar Metal',
		fields: ['name'],
		limit_page_length: 100,
	}),
	onSuccess: (data) => {
		metals.value = data || []
	},
})

// Computed: Recommended deposit (50%)
const recommendedDeposit = computed(() => {
	const total = form.value.estimated_cost || 0
	return (total / 2).toFixed(2)
})

// Computed: Remaining balance due
const remainingBalance = computed(() => {
	const total = form.value.estimated_cost || 0
	const deposit = form.value.deposit_amount || 0
	return Math.max(0, total - deposit)
})

// Watch collect deposit, auto fill 50%
watch(() => form.value.collect_deposit, (val) => {
	if (val) {
		const total = form.value.estimated_cost || 0
		form.value.deposit_amount = parseFloat((total / 2).toFixed(2))
	} else {
		form.value.deposit_amount = null
	}
})

// Auto-fill est cost when selecting repair type
watch(() => form.value.repair_type, (newType) => {
	if (newType && selectedRepairType.value) {
		const basePrice = selectedRepairType.value.base_price || 0
		form.value.labor_cost = basePrice
		form.value.material_cost = 0
		form.value.estimated_cost = basePrice
	}
})

function setPromisedDatePreset(days) {
	const date = new Date()
	date.setDate(date.getDate() + days)
	const yyyy = date.getFullYear()
	const mm = String(date.getMonth() + 1).padStart(2, '0')
	const dd = String(date.getDate()).padStart(2, '0')
	form.value.promised_date = `${yyyy}-${mm}-${dd}`
}

function toggleCondition(cond) {
	const current = form.value.item_condition || ''
	const parts = current.split(',').map(s => s.trim()).filter(Boolean)
	
	if (parts.includes(cond)) {
		const filtered = parts.filter(p => p !== cond)
		form.value.item_condition = filtered.join(', ')
	} else {
		parts.push(cond)
		form.value.item_condition = parts.join(', ')
	}
}

function isConditionSelected(cond) {
	const current = form.value.item_condition || ''
	return current.split(',').map(s => s.trim()).includes(cond)
}

function updateTotalCost() {
	const labor = parseFloat(form.value.labor_cost) || 0
	const material = parseFloat(form.value.material_cost) || 0
	form.value.estimated_cost = parseFloat((labor + material).toFixed(2))
	
	if (form.value.collect_deposit) {
		form.value.deposit_amount = parseFloat((form.value.estimated_cost / 2).toFixed(2))
	}
}

const showWeightWarning = computed(() => {
	return form.value.metal_type && !form.value.item_weight
})

// Mappings from quick intake checklist conditions to service keywords
const conditionToKeywordsMap = {
	'Light Scratches': ['polish', 'clean', 'buff', 'refinish'],
	'Deep Scratches': ['polish', 'refinish', 'laser', 'repair'],
	'Loose Stones': ['tighten', 'stone', 'set', 'prong'],
	'Missing Stones': ['replace', 'set', 'stone', 'gemstone'],
	'Worn Prongs': ['prong', 'tipping', 'retip', 'head'],
	'Broken Clasp': ['clasp', 'lock', 'spring', 'solder'],
	'Bent Band': ['bend', 'shape', 'size', 'band', 'shank'],
	'Polishing Needed': ['polish', 'clean', 'buff']
}

const selectedConditions = computed(() => {
	const current = form.value.item_condition || ''
	return current.split(',').map(s => s.trim()).filter(Boolean)
})

const recommendedRepairTypes = computed(() => {
	const activeConditions = selectedConditions.value
	if (activeConditions.length === 0) return []

	// Gather all keywords for active conditions
	const keywords = new Set()
	activeConditions.forEach(cond => {
		const kws = conditionToKeywordsMap[cond] || []
		kws.forEach(kw => keywords.add(kw.toLowerCase()))
	})

	if (keywords.size === 0) return []

	// Filter allRepairTypes to find matches
	return allRepairTypes.value.filter(rt => {
		const name = (rt.repair_name || rt.name || '').toLowerCase()
		const desc = (rt.description || '').toLowerCase()
		const cat = (rt.category || '').toLowerCase()

		// Check if any keyword matches name, description, or category
		return Array.from(keywords).some(kw => 
			name.includes(kw) || desc.includes(kw) || cat.includes(kw)
		)
	})
})

// Computed: Repair categories
const repairCategories = computed(() => {
	const cats = new Set(allRepairTypes.value.map((rt) => rt.category).filter(Boolean))
	return Array.from(cats).sort()
})

// Computed: Grouped repair types
const groupedRepairTypes = computed(() => {
	const groups = {}
	const filtered =
		selectedCategory.value || repairTypeSearch.value
			? repairTypes.value.filter((rt) => {
					const matchCategory =
						!selectedCategory.value || rt.category === selectedCategory.value
					const matchSearch =
						!repairTypeSearch.value ||
						(rt.repair_name || rt.name || '')
							.toLowerCase()
							.includes(repairTypeSearch.value.toLowerCase()) ||
						(rt.description || '')
							.toLowerCase()
							.includes(repairTypeSearch.value.toLowerCase())
					return matchCategory && matchSearch
			  })
			: repairTypes.value

	filtered.forEach((rt) => {
		const cat = rt.category || 'General'
		if (!groups[cat]) groups[cat] = []
		groups[cat].push(rt)
	})
	return groups
})

// Computed: Filtered repair types flat list
const filteredRepairTypes = computed(() => {
	return repairTypes.value.filter((rt) => {
		const matchCategory =
			!selectedCategory.value || rt.category === selectedCategory.value
		const matchSearch =
			!repairTypeSearch.value ||
			(rt.repair_name || rt.name || '')
				.toLowerCase()
				.includes(repairTypeSearch.value.toLowerCase()) ||
			(rt.description || '')
				.toLowerCase()
				.includes(repairTypeSearch.value.toLowerCase())
		return matchCategory && matchSearch
	})
})

function clearFilters() {
	repairTypeSearch.value = ''
	selectedCategory.value = ''
}

// Computed: Selected repair type details
const selectedRepairType = computed(() => {
	if (!form.value.repair_type) return null
	return allRepairTypes.value.find((rt) => rt.name === form.value.repair_type)
})

let searchTimer
function searchCustomers() {
	clearTimeout(searchTimer)
	if (!customerSearch.value || customerSearch.value.length < 2) {
		customerResults.value = []
		return
	}
	searchTimer = setTimeout(async () => {
		try {
			const results = await call('zevar_core.api.customer.search_customers', {
				query: customerSearch.value,
			})
			const list = results || []
			customerResults.value = list.map((c) => ({
				...c,
				name: c.name || c.customer_name,
				customer_name: c.display_name || c.customer_name,
				is_repeat: true,
			}))
		} catch (e) {
			console.error('Customer search failed:', e)
			customerResults.value = []
		}
	}, 300)
}

async function selectCustomer(customer) {
	form.value.customer = customer.name
	form.value.customer_name = customer.customer_name
	form.value.customer_phone = customer.mobile_no || customer.phone || customer.mobile || ''
	customerSearch.value = customer.customer_name
	customerResults.value = []
	loadCustomerHistory(customer.name)
}

async function loadCustomerHistory(customer) {
	try {
		const history = await call('zevar_core.api.get_customer_repair_history', {
			customer,
			limit: 5,
		})
		customerRepairHistory.value = history || []
	} catch (e) {
		console.error('Failed to load customer history:', e)
	}
}

function addNoteTemplate(template) {
	const currentDesc = form.value.item_description || ''
	form.value.item_description = currentDesc ? `${currentDesc}. ${template.text}` : template.text
}

function addGemstone() {
	form.value.gemstones.push({
		gemstone_type: 'Diamond',
		quantity: 1,
		carat_weight: null,
		color: '',
		clarity: '',
		setting_type: 'Prong',
		is_treated: 0,
		notes: '',
	})
}

function removeGemstone(idx) {
	form.value.gemstones.splice(idx, 1)
}

function onCustomerCreated(customer) {
	selectCustomer(customer)
	showNewCustomerModal.value = false
	toast({
		title: 'Customer Selected',
		message: `${customer.customer_name} selected`,
		icon: 'check',
		intent: 'success',
	})
}

function onRepairTypeCreated() {
	showRepairTypeManager.value = false
	repairTypesResource.fetch()
}

async function submit() {
	if (!form.value.customer) {
		activeTab.value = 'logistics'
		toast({
			title: 'Required Field Missing',
			message: 'Please select or create a customer',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	if (!form.value.repair_type) {
		activeTab.value = 'pricing'
		toast({
			title: 'Required Field Missing',
			message: 'Please select a service repair type',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	if (!form.value.promised_date) {
		activeTab.value = 'logistics'
		toast({
			title: 'Required Field Missing',
			message: 'Please select a promised completion date',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	if (!form.value.intake_checklist_signed) {
		activeTab.value = 'pricing'
		toast({
			title: 'Signature Required',
			message: 'Customer must read and check the liability waiver to submit order',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}

	submitting.value = true
	errorMsg.value = ''
	try {
		// Calculate final stone weight before payload
		if (form.value.gemstones.length > 0) {
			form.value.stone_weight = form.value.gemstones.reduce((sum, item) => sum + (parseFloat(item.carat_weight) || 0), 0)
		}

		// Standard USA jewelry POS security & access control
		const payload = {
			customer: form.value.customer,
			repair_type: form.value.repair_type,
			item_description: form.value.item_description || undefined,
			customer_phone: form.value.customer_phone || undefined,
			estimated_cost: form.value.estimated_cost || undefined,
			labor_cost: form.value.labor_cost || undefined,
			material_cost: form.value.material_cost || undefined,
			priority: form.value.priority,
			item_type: form.value.item_type || undefined,
			item_brand: form.value.item_brand || undefined,
			serial_number: form.value.serial_number || undefined,
			item_condition: form.value.item_condition || undefined,
			item_weight: form.value.item_weight || undefined,
			metal_weight_in: form.value.item_weight || undefined, // Metal Weight In equals gross weight at intake
			stone_weight: form.value.stone_weight || undefined,
			metal_type: form.value.metal_type || undefined,
			purity: form.value.purity || undefined,
			customer_id_type: form.value.customer_id_type || undefined,
			customer_id_number: form.value.customer_id_number || undefined,
			customer_id_state: form.value.customer_id_state || undefined,
			is_warranty_repair: form.value.is_warranty_repair ? 1 : 0,
			original_repair_order: form.value.original_repair_order || undefined,
			warranty_claim_type: form.value.warranty_claim_type || undefined,
			promised_date: form.value.promised_date || undefined,
			warehouse: form.value.warehouse || undefined,
			receiving_store: form.value.warehouse || undefined,
			handled_by: form.value.handled_by || undefined,
			intake_checklist_signed: form.value.intake_checklist_signed ? 1 : 0,
			collect_deposit: form.value.collect_deposit ? 1 : 0,
			deposit_amount: form.value.collect_deposit ? form.value.deposit_amount : undefined,
			deposit_payment_method: form.value.collect_deposit ? form.value.deposit_payment_method : undefined,
		}

		// Embed gemstones if present for a single atomic transaction
		if (form.value.gemstones.length > 0) {
			payload.gemstones = form.value.gemstones.map((stone) => ({
				doctype: 'Repair Gemstone',
				gemstone_type: stone.gemstone_type,
				quantity: parseInt(stone.quantity) || 1,
				carat_weight: stone.carat_weight ? parseFloat(stone.carat_weight) : undefined,
				color: stone.color || undefined,
				clarity: stone.clarity || undefined,
				setting_type: stone.setting_type || undefined,
				is_treated: stone.is_treated ? 1 : 0,
				notes: stone.notes || undefined,
			}))
		}

		// Embed payment if deposit is collected for atomic execution
		if (form.value.collect_deposit && form.value.deposit_amount > 0) {
			payload.payments = [{
				doctype: 'Repair Payment',
				amount: parseFloat(form.value.deposit_amount),
				payment_method: form.value.deposit_payment_method,
				payment_date: new Date().toISOString().split('T')[0],
				notes: 'Intake deposit payment',
			}]
		}

		// Remove undefined values to avoid sending them as 'undefined' strings
		Object.keys(payload).forEach((key) => payload[key] === undefined && delete payload[key])

		await call('zevar_core.api.create_repair_order', payload)

		emit('created')
		toast({
			title: 'Success',
			message: 'Repair intake order completed successfully',
			icon: 'check',
			intent: 'success',
		})
	} catch (e) {
		console.error('Failed to create repair order:', e)
		let errorDetails = ''
		if (e && typeof e === 'object') {
			if (e.messages && e.messages.length > 0) {
				errorDetails = e.messages.join('\n')
			} else if (e.message) {
				errorDetails = e.message
			} else if (e.exc) {
				try {
					const parsed = JSON.parse(e.exc)
					errorDetails = parsed[0] || e.exc
				} catch {
					errorDetails = e.exc
				}
			} else {
				errorDetails = JSON.stringify(e)
			}
		} else {
			errorDetails = String(e)
		}
		errorMsg.value = errorDetails
		toast({
			title: 'Intake Failed',
			message: errorMsg.value,
			icon: 'alert-triangle',
			intent: 'error',
		})
	} finally {
		submitting.value = false
	}
}

onMounted(async () => {
	repairTypesResource.fetch()
	metalsResource.fetch()

	// Default warehouse from session
	if (session.currentWarehouse) {
		form.value.warehouse = session.currentWarehouse
	}

	// Default handled by from session user email
	if (session.user?.email) {
		form.value.handled_by = session.user.email
	}

	// Fetch store locations
	try {
		const locations = await call('frappe.client.get_list', {
			doctype: 'Warehouse',
			fields: ['name', 'warehouse_name'],
			filters: {
				is_group: 0,
				disabled: 0,
				name: ['in', [
					'Store 1 - New York - ZJ',
					'Store 2 - Los Angeles - ZJ',
					'Store 3 - Chicago - ZJ',
					'Store 4 - Houston - ZJ',
					'Store 5 - Miami - ZJ'
				]]
			},
			limit_page_length: 10,
		})
		storeLocations.value = locations || []
	} catch (e) {
		console.error('Failed to fetch warehouses:', e)
	}

	// Fetch technicians/users
	try {
		const users = await call('frappe.client.get_list', {
			doctype: 'User',
			filters: { enabled: 1 },
			fields: ['name', 'full_name', 'first_name', 'last_name'],
			limit_page_length: 100,
		})
		technicians.value = (users || []).map((t) => ({
			value: t.name,
			label: t.full_name || `${t.first_name || ''} ${t.last_name || ''}`.trim() || t.name,
		}))
	} catch (e) {
		console.error('Failed to fetch users:', e)
	}

	// Initialize default promised date (+7 days preset)
	setPromisedDatePreset(7)
})
</script>
