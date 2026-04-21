<template>
	<div class="customer-selector">
		<!-- Selected Customer Display -->
		<div
			v-if="customer && !showSearch"
			class="flex items-center justify-between p-3 bg-gray-50 dark:bg-[#15171e] border border-gray-200 dark:border-white/10 rounded-xl"
		>
			<div class="flex items-center gap-3">
				<div
					class="w-10 h-10 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37]"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
						></path>
					</svg>
				</div>
				<div>
					<div class="font-semibold text-gray-900 dark:text-white text-sm">
						{{ customer.display_name || customer.customer_name || customer.name }}
						<span
							v-if="
								customer.name &&
								customer.name !== (customer.display_name || customer.customer_name)
							"
							class="text-xs text-gray-500 font-normal ml-1"
							>({{ customer.name }})</span
						>
					</div>
					<div
						v-if="customer.mobile_no || customer.email_id"
						class="text-xs text-gray-500"
					>
						{{ customer.mobile_no || customer.email_id }}
					</div>
				</div>
			</div>
			<button
				@click="clearAndShowSearch"
				class="p-2 hover:bg-gray-200 dark:hover:bg-white/10 rounded-full transition-colors text-gray-400"
				title="Change Customer"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					></path>
				</svg>
			</button>
		</div>

		<!-- Search / Create UI -->
		<div v-else class="space-y-3">
			<!-- Search Input -->
			<div class="relative">
				<input
					ref="searchInput"
					v-model="searchQuery"
					type="text"
					:placeholder="placeholder"
					@input="debouncedSearch"
					@focus="showDropdown = true"
					class="w-full px-4 py-3 pl-10 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 focus:border-[#D4AF37]"
				/>
				<svg
					class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
					></path>
				</svg>
				<button
					v-if="searchQuery"
					@click="clearSearch"
					class="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full"
				>
					<svg
						class="w-3 h-3 text-gray-400"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						></path>
					</svg>
				</button>

				<!-- Search Results Dropdown -->
				<div
					v-if="
						showDropdown && (searchResults.length > 0 || searching || showCreateOption)
					"
					class="absolute z-50 w-full mt-1 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-white/10 rounded-xl shadow-lg max-h-60 overflow-y-auto"
				>
					<!-- Searching indicator -->
					<div
						v-if="searching"
						class="px-4 py-3 text-sm text-gray-500 flex items-center gap-2"
					>
						<svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						Searching...
					</div>

					<!-- Search Results -->
					<button
						v-for="result in searchResults"
						:key="result.customer_name"
						@click="selectCustomer(result)"
						class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-white/5 flex items-center gap-3 border-b border-gray-100 dark:border-white/5 last:border-0"
					>
						<div
							class="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500"
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
									d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
								></path>
							</svg>
						</div>
						<div class="min-w-0 flex-1">
							<div
								class="font-medium text-gray-900 dark:text-white text-sm truncate"
							>
								{{ result.display_name || result.customer_name }}
								<span
									v-if="result.customer_name !== result.display_name"
									class="text-xs text-gray-500 font-normal ml-1"
									>({{ result.customer_name }})</span
								>
							</div>
							<div class="text-xs text-gray-500 truncate">
								{{
									[result.mobile_no, result.email_id]
										.filter(Boolean)
										.join(' · ') || 'No contact info'
								}}
							</div>
						</div>
					</button>

					<!-- Create New Customer Option -->
					<button
						v-if="showCreateOption"
						@click="openCreateModal"
						class="w-full px-4 py-3 text-left hover:bg-[#D4AF37]/10 flex items-center gap-3 border-t-2 border-gray-100 dark:border-white/10"
					>
						<div
							class="w-8 h-8 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37]"
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
									d="M12 6v6m0 0v6m0-6h6m-6 0H6"
								></path>
							</svg>
						</div>
						<div class="text-sm">
							<span class="font-medium text-[#D4AF37]">Create new customer</span>
							<span v-if="searchQuery" class="text-gray-500"
								>: "{{ searchQuery }}"</span
							>
						</div>
					</button>
				</div>
			</div>

			<!-- Click outside to close dropdown -->
			<div
				v-if="showDropdown"
				@click="showDropdown = false"
				class="fixed inset-0 z-40"
			></div>

			<!-- Quick Add Button (when no search query) -->
			<button
				v-if="!searchQuery && showQuickAdd"
				@click="showCreateModal = true"
				class="w-full py-2 text-sm font-medium text-[#D4AF37] border border-dashed border-[#D4AF37]/40 rounded-lg hover:bg-[#D4AF37]/10 transition flex items-center justify-center gap-2"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6v6m0 0v6m0-6h6m-6 0H6"
					></path>
				</svg>
				Add New Customer
			</button>
		</div>

		<!-- Create Customer Modal -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showCreateModal"
					class="fixed inset-0 z-[200] flex items-center justify-center p-4"
				>
					<div
						@click="showCreateModal = false"
						class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm"
					></div>
					<div
						class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col border border-transparent dark:border-white/10"
					>
						<!-- Header -->
						<div
							class="p-6 pb-4 border-b border-gray-100 dark:border-white/10 flex-shrink-0"
						>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								Add New Customer
							</h3>
							<p class="text-sm text-gray-500 mt-1">
								Fill in customer details below
							</p>
						</div>

						<!-- Form Content - Scrollable -->
						<div class="flex-1 overflow-y-auto p-6 space-y-5">
							<!-- Basic Information -->
							<div class="space-y-4">
								<h4
									class="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2"
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
											d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
										></path>
									</svg>
									Basic Information
								</h4>
								<div class="grid grid-cols-2 gap-3">
									<div class="col-span-2">
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
										>
											{{
												cart.customerType === 'Company'
													? 'Company Name'
													: 'Full Name'
											}}
											<span class="text-red-500">*</span>
										</label>
										<input
											v-model="newCustomer.name"
											type="text"
											placeholder="John Doe"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
										>
											Phone Number
										</label>
										<input
											v-model="newCustomer.phone"
											type="tel"
											placeholder="(555) 123-4567"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
										>
											Email
										</label>
										<input
											v-model="newCustomer.email"
											type="email"
											placeholder="john@example.com"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>
							</div>

							<!-- Address Section (Collapsible) -->
							<div
								class="border border-gray-200 dark:border-white/10 rounded-xl overflow-hidden"
							>
								<button
									@click="showAddressFields = !showAddressFields"
									class="w-full px-4 py-3 flex items-center justify-between bg-gray-50 dark:bg-[#15171e] hover:bg-gray-100 dark:hover:bg-white/5 transition"
								>
									<span
										class="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2"
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
												d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
											></path>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
											></path>
										</svg>
										Address
									</span>
									<svg
										class="w-4 h-4 text-gray-400 transition-transform"
										:class="showAddressFields ? 'rotate-180' : ''"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 9l-7 7-7-7"
										></path>
									</svg>
								</button>
								<div
									v-if="showAddressFields"
									class="p-4 space-y-3 bg-white dark:bg-[#1a1c23]"
								>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Street Address</label
										>
										<input
											v-model="newCustomer.address_line1"
											type="text"
											placeholder="123 Main St"
											class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Apt / Suite</label
										>
										<input
											v-model="newCustomer.address_line2"
											type="text"
											placeholder="Apt 4B"
											class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div class="grid grid-cols-3 gap-3">
										<div class="col-span-2">
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>City</label
											>
											<input
												v-model="newCustomer.city"
												type="text"
												placeholder="New York"
												class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>State</label
											>
											<input
												v-model="newCustomer.state"
												type="text"
												placeholder="NY"
												class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>ZIP Code</label
										>
										<input
											v-model="newCustomer.pincode"
											type="text"
											placeholder="10001"
											class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>
							</div>

							<!-- Jewelry Preferences (Collapsible) -->
							<div
								class="border border-gray-200 dark:border-white/10 rounded-xl overflow-hidden"
							>
								<button
									@click="showPreferenceFields = !showPreferenceFields"
									class="w-full px-4 py-3 flex items-center justify-between bg-gray-50 dark:bg-[#15171e] hover:bg-gray-100 dark:hover:bg-white/5 transition"
								>
									<span
										class="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2"
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
												d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
											></path>
										</svg>
										Jewelry Preferences
									</span>
									<svg
										class="w-4 h-4 text-gray-400 transition-transform"
										:class="showPreferenceFields ? 'rotate-180' : ''"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 9l-7 7-7-7"
										></path>
									</svg>
								</button>
								<div
									v-if="showPreferenceFields"
									class="p-4 space-y-3 bg-white dark:bg-[#1a1c23]"
								>
									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Ring Size</label
											>
											<select
												v-model="newCustomer.ring_size"
												class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											>
												<option value="">Select...</option>
												<option
													v-for="size in ringSizes"
													:key="size"
													:value="size"
												>
													{{ size }}
												</option>
											</select>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Preferred Metal</label
											>
											<select
												v-model="newCustomer.preferred_metal"
												class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											>
												<option value="">Select...</option>
												<option value="Yellow Gold">Yellow Gold</option>
												<option value="White Gold">White Gold</option>
												<option value="Rose Gold">Rose Gold</option>
												<option value="Platinum">Platinum</option>
												<option value="Silver">Silver</option>
											</select>
										</div>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Preferred Gold Purity</label
										>
										<select
											v-model="newCustomer.preferred_purity"
											class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										>
											<option value="">Select...</option>
											<option value="24K">24K (99.9%)</option>
											<option value="22K">22K (91.6%)</option>
											<option value="18K">18K (75%)</option>
											<option value="14K">14K (58.3%)</option>
											<option value="10K">10K (41.7%)</option>
										</select>
									</div>
								</div>
							</div>

							<!-- Additional Info (Collapsible) -->
							<div
								v-if="cart.customerType !== 'Company'"
								class="border border-gray-200 dark:border-white/10 rounded-xl overflow-hidden"
							>
								<button
									@click="showAdditionalFields = !showAdditionalFields"
									class="w-full px-4 py-3 flex items-center justify-between bg-gray-50 dark:bg-[#15171e] hover:bg-gray-100 dark:hover:bg-white/5 transition"
								>
									<span
										class="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2"
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
												d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
											></path>
										</svg>
										Additional Info
									</span>
									<svg
										class="w-4 h-4 text-gray-400 transition-transform"
										:class="showAdditionalFields ? 'rotate-180' : ''"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 9l-7 7-7-7"
										></path>
									</svg>
								</button>
								<div
									v-if="showAdditionalFields"
									class="p-4 space-y-3 bg-white dark:bg-[#1a1c23]"
								>
									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Spouse Name</label
											>
											<input
												v-model="newCustomer.spouse_name"
												type="text"
												placeholder="Jane Doe"
												class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Anniversary</label
											>
											<input
												v-model="newCustomer.anniversary"
												type="date"
												class="w-full px-3 py-2 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-white/10 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>
									<label
										class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-[#0F1115] rounded-lg cursor-pointer"
									>
										<input
											v-model="newCustomer.tax_exempt"
											type="checkbox"
											class="w-4 h-4 rounded border-gray-300 text-[#D4AF37] focus:ring-[#D4AF37]"
										/>
										<div>
											<span
												class="text-sm font-medium text-gray-700 dark:text-gray-300"
												>Tax Exempt</span
											>
											<p class="text-xs text-gray-500">
												Customer is exempt from sales tax
											</p>
										</div>
									</label>
								</div>
							</div>

							<!-- Error Message -->
							<div
								v-if="createError"
								class="text-sm text-red-500 bg-red-50 dark:bg-red-900/20 px-4 py-3 rounded-lg border border-red-200 dark:border-red-800/30"
							>
								{{ createError }}
							</div>
						</div>

						<!-- Footer -->
						<div
							class="p-6 pt-4 border-t border-gray-100 dark:border-white/10 flex gap-3 flex-shrink-0"
						>
							<button
								@click="handleCancelCreate"
								class="flex-1 py-2.5 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-white/5 dark:text-gray-300 dark:hover:bg-white/10 transition"
							>
								Cancel
							</button>
							<button
								@click="createCustomer"
								:disabled="!newCustomer.name || creating"
								class="flex-1 py-2.5 rounded-lg font-bold text-white bg-[#D4AF37] hover:bg-[#b5952f] disabled:opacity-50 transition flex items-center justify-center gap-2"
							>
								<svg
									v-if="creating"
									class="animate-spin w-4 h-4"
									fill="none"
									viewBox="0 0 24 24"
								>
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
									></path>
								</svg>
								<span>{{ creating ? 'Creating...' : 'Create Customer' }}</span>
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
	</div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { createResource } from 'frappe-ui'
import { useCartStore } from '@/stores/cart.js'

const props = defineProps({
	placeholder: {
		type: String,
		default: 'Search customers by name, phone, or email...',
	},
	showQuickAdd: {
		type: Boolean,
		default: true,
	},
	compact: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(['selected', 'cleared'])

const cart = useCartStore()

// Ring sizes for dropdown
const ringSizes = [
	'3',
	'3.5',
	'4',
	'4.5',
	'5',
	'5.5',
	'6',
	'6.5',
	'7',
	'7.5',
	'8',
	'8.5',
	'9',
	'9.5',
	'10',
	'10.5',
	'11',
	'11.5',
	'12',
	'12.5',
	'13',
	'13.5',
	'14',
]

// State
const showSearch = ref(!cart.customer)
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const showDropdown = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const searchInput = ref(null)

// Collapsible sections
const showAddressFields = ref(false)
const showPreferenceFields = ref(false)
const showAdditionalFields = ref(false)

// New customer form
const newCustomer = ref({
	name: '',
	phone: '',
	email: '',
	// Address
	address_line1: '',
	address_line2: '',
	city: '',
	state: '',
	pincode: '',
	// Preferences
	ring_size: '',
	preferred_metal: '',
	preferred_purity: '',
	// Additional
	spouse_name: '',
	anniversary: '',
	tax_exempt: false,
})

function openCreateModal() {
	showCreateModal.value = true
	showDropdown.value = false
}

function handleCancelCreate() {
	showCreateModal.value = false
	resetCreateForm()
}

// Computed
const customer = computed(() => cart.customer)

const showCreateOption = computed(() => {
	return searchQuery.value.length >= 2 && !searching.value
})

// Debounce helper
let searchTimeout = null
function debouncedSearch() {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(() => {
		performSearch()
	}, 300)
}

// Search customers resource (persistent)
const customerSearchResource = createResource({
	url: 'zevar_core.api.customer.search_customers',
	auto: false,
})

// Search customers
// Search customers
async function performSearch() {
	if (!searchQuery.value || searchQuery.value.length < 2) {
		searchResults.value = []
		return
	}

	searching.value = true
	showDropdown.value = true

	try {
		const results = await customerSearchResource.submit({
			query: searchQuery.value,
		})
		const list = results || []
		searchResults.value = list.map(c => ({
			...c,
			name: c.name || c.customer_name,
			customer_name: c.display_name || c.customer_name,
		}))
	} catch (e) {
		console.error('Customer search failed:', e)
		searchResults.value = []
	} finally {
		searching.value = false
	}
}
// Customer details resource (persistent)
const customerDetailsResource = createResource({
	url: 'zevar_core.api.customer.get_customer_details',
	auto: false,
})

// Select an existing customer
async function selectCustomer(customerData) {
	// Fetch full details
	try {
		const r = await customerDetailsResource.submit({ customer_name: customerData.customer_name || customerData.name })
		const fullData = r?.data || r
		// Ensure name field is set for compatibility
		if (fullData && fullData.customer_name && !fullData.name) {
			fullData.name = fullData.customer_name
		}
		if (fullData) {
			cart.setCustomer(fullData)
		} else {
			cart.setCustomer(customerData)
		}
	} catch (e) {
		// Fallback to basic data, ensure name field is set
		const basicData = { ...customerData }
		if (basicData.customer_name && !basicData.name) {
			basicData.name = basicData.customer_name
		}
		cart.setCustomer(basicData)
	}

	showSearch.value = false
	showDropdown.value = false
	searchQuery.value = ''
	searchResults.value = []
	emit('selected', cart.customer)
}

// Create new customer
async function createCustomer() {
	if (!newCustomer.value.name) return

	creating.value = true
	createError.value = ''

	try {
		const r = await createResource({
			url: 'zevar_core.api.customer.quick_create_customer',
			params: {
				customer_name: newCustomer.value.name,
				customer_type: cart.customerType !== 'Walkin' ? cart.customerType : 'Individual',
				mobile_no: newCustomer.value.phone || null,
				email_id: newCustomer.value.email || null,
				// Address
				address_line1: newCustomer.value.address_line1 || null,
				address_line2: newCustomer.value.address_line2 || null,
				city: newCustomer.value.city || null,
				state: newCustomer.value.state || null,
				pincode: newCustomer.value.pincode || null,
				// Preferences
				ring_size: newCustomer.value.ring_size || null,
				preferred_metal: newCustomer.value.preferred_metal || null,
				preferred_purity: newCustomer.value.preferred_purity || null,
				// Additional
				spouse_name: newCustomer.value.spouse_name || null,
				anniversary: newCustomer.value.anniversary || null,
				tax_exempt: newCustomer.value.tax_exempt ? 1 : 0,
			},
		}).fetch()
		const data = r?.data || r

		if (data.success) {
			// Ensure customer_name is set for compatibility
			const customerData = {
				...data,
				name: data.customer_name, // Add name field for compatibility
			}
			cart.setCustomer(customerData)
			showCreateModal.value = false
			showSearch.value = false
			searchQuery.value = ''
			resetCreateForm()
			emit('selected', cart.customer)
		} else {
			createError.value = data.message || 'Failed to create customer'
		}
	} catch (e) {
		// Handle Frappe error responses
		const errorMsg = e?.response?.data?.message || e?.message || e?.exception || String(e)
		createError.value = errorMsg
		console.error('Customer creation error:', e)
	} finally {
		creating.value = false
	}
}

// Clear and show search
function clearAndShowSearch() {
	cart.clearCustomer()
	showSearch.value = true
	emit('cleared')
	nextTick(() => {
		searchInput.value?.focus()
	})
}

// Clear search
function clearSearch() {
	searchQuery.value = ''
	searchResults.value = []
	searchInput.value?.focus()
}

// Reset create form
function resetCreateForm() {
	newCustomer.value = {
		name: '',
		phone: '',
		email: '',
		address_line1: '',
		address_line2: '',
		city: '',
		state: '',
		pincode: '',
		ring_size: '',
		preferred_metal: '',
		preferred_purity: '',
		spouse_name: '',
		anniversary: '',
		tax_exempt: false,
	}
	createError.value = ''
	showAddressFields.value = false
	showPreferenceFields.value = false
	showAdditionalFields.value = false
}

// Watch for external customer changes
watch(
	() => cart.customer,
	(newVal) => {
		if (newVal) {
			showSearch.value = false
		}
	}
)

// Initialize with prefill from search query for create form
watch(searchQuery, (val) => {
	if (val && !newCustomer.value.name) {
		newCustomer.value.name = val
	}
})

// Expose methods for parent components
defineExpose({
	showSearch,
	focusSearch: () => searchInput.value?.focus(),
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
