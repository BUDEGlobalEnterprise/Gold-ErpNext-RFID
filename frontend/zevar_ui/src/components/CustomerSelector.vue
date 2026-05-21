<template>
	<div class="customer-selector" data-testid="customer-selector">
		<!-- Selected Customer Display -->
		<div
			v-if="customer && !showSearch"
			class="flex items-center justify-between p-3 bg-gray-50 dark:bg-warm-dark-700 border border-gray-200 dark:border-warm-border rounded-xl"
		>
			<div class="flex items-center gap-3 flex-1 min-w-0">
				<div
					class="w-10 h-10 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37] flex-shrink-0"
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
				<div class="min-w-0 flex-1">
					<div class="font-semibold text-gray-900 dark:text-white text-sm truncate">
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
						class="text-xs text-gray-500 truncate"
					>
						{{ customer.mobile_no || customer.email_id }}
					</div>
				</div>
			</div>
			<div class="flex items-center gap-1 flex-shrink-0">
				<button
					v-if="isAdmin && customer.name"
					@click.prevent="openEditModal(customer)"
					class="p-2 hover:bg-gray-200 dark:hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-[#D4AF37]"
					title="Edit Customer"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
						/>
					</svg>
				</button>
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
		</div>

		<!-- Search / Create UI -->
		<div v-else class="space-y-3">
			<!-- Recent Customers Section (Admin/Manager only) -->
			<div v-if="isAdmin && recentCustomers.length > 0 && !searchQuery" class="space-y-2">
				<div class="flex items-center justify-between">
					<span
						class="text-[10px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
						>Recent Customers</span
					>
					<button
						v-if="recentCustomers.length >= 10"
						@click="loadMoreRecent"
						class="text-[10px] text-[#D4AF37] font-medium hover:underline"
					>
						Load more
					</button>
				</div>
				<div class="flex gap-2 overflow-x-auto pb-1 custom-scrollbar">
					<button
						v-for="rc in recentCustomers"
						:key="rc.name"
						@click="selectCustomer(rc)"
						class="flex-shrink-0 flex items-center gap-2 px-3 py-2 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-xl hover:border-[#D4AF37]/50 hover:bg-[#D4AF37]/5 transition min-w-[140px] max-w-[200px]"
					>
						<div
							class="w-7 h-7 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37] text-xs font-bold flex-shrink-0"
						>
							{{ getInitials(rc.customer_name) }}
						</div>
						<div class="min-w-0 flex-1 text-left">
							<div
								class="text-xs font-medium text-gray-900 dark:text-white truncate"
							>
								{{ rc.customer_name }}
							</div>
							<div class="text-[10px] text-gray-500 truncate">
								{{ rc.mobile_no || rc.email_id || 'No contact' }}
							</div>
						</div>
					</button>
				</div>
			</div>

			<!-- Edit Customer Modal (Admin only) -->
			<Teleport to="body">
				<Transition name="fade">
					<div
						v-if="showEditModal"
						class="fixed inset-0 z-[200] flex items-center justify-center p-4"
					>
						<div
							@click="closeEditModal"
							class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm"
						></div>
						<div
							class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col border border-transparent dark:border-warm-border"
						>
							<!-- Header -->
							<div
								class="p-6 pb-4 border-b border-gray-100 dark:border-warm-border flex items-center justify-between flex-shrink-0"
							>
								<h3 class="text-lg font-bold text-gray-900 dark:text-white">
									Edit Customer
								</h3>
								<button
									@click="closeEditModal"
									class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition"
								>
									<svg
										class="w-5 h-5 text-gray-400"
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

							<!-- Tabs -->
							<div
								class="flex border-b border-gray-100 dark:border-warm-border px-6 flex-shrink-0"
							>
								<button
									v-for="tab in tabs"
									:key="tab.key"
									@click="editTab = tab.key"
									class="px-4 py-3 text-sm font-medium transition-colors relative"
									:class="
										editTab === tab.key
											? 'text-blue-600 dark:text-blue-400'
											: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
									"
								>
									{{ tab.label }}
									<div
										v-if="editTab === tab.key"
										class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400"
									></div>
								</button>
							</div>

							<!-- Loading State -->
							<div
								v-if="editLoading"
								class="flex-1 flex items-center justify-center py-12"
							>
								<div
									class="animate-spin rounded-full h-6 w-6 border-2 border-gray-300 border-t-[#D4AF37]"
								></div>
							</div>

							<!-- Form Content - Scrollable -->
							<div v-else class="flex-1 overflow-y-auto p-6 space-y-5">
								<!-- Tab 1: Contact Details -->
								<div v-if="editTab === 'contact'" class="space-y-4">
									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Contact type</label
											>
											<select
												v-model="editForm.customer_type"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											>
												<option value="Individual">Individual</option>
												<option value="Company">Company</option>
											</select>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Customer group</label
											>
											<input
												v-model="editForm.customer_group"
												type="text"
												placeholder="e.g. VIP, Standard"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Mobile</label
											>
											<input
												v-model="editForm.mobile_no"
												type="tel"
												placeholder="Mobile number"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Email</label
											>
											<input
												v-model="editForm.email_id"
												type="email"
												placeholder="email@example.com"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<div class="grid grid-cols-3 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Gender</label
											>
											<select
												v-model="editForm.gender"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											>
												<option value="">--</option>
												<option value="Male">Male</option>
												<option value="Female">Female</option>
												<option value="Other">Other</option>
											</select>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Birth date</label
											>
											<input
												v-model="editForm.birth_date"
												type="date"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Phone 2</label
											>
											<input
												v-model="editForm.phone2"
												type="tel"
												placeholder="Secondary phone"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Profession</label
										>
										<input
											v-model="editForm.profession"
											type="text"
											placeholder="Profession"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>

								<!-- Tab 2: Extra Details -->
								<div v-if="editTab === 'extra'" class="space-y-4">
									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Partner name</label
											>
											<input
												v-model="editForm.partner_name"
												type="text"
												placeholder="Partner/spouse name"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Partner phone</label
											>
											<input
												v-model="editForm.partner_phone"
												type="tel"
												placeholder="Partner phone"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Partner email</label
											>
											<input
												v-model="editForm.partner_email"
												type="email"
												placeholder="Partner email"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Tags</label
											>
											<input
												v-model="editForm.tags"
												type="text"
												placeholder="VIP, Wholesale, etc."
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Birth date</label
											>
											<input
												v-model="editForm.birth_date"
												type="date"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Marriage date</label
											>
											<input
												v-model="editForm.marriage_date"
												type="date"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<label
										class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-[#0F1115] rounded-lg cursor-pointer"
									>
										<input
											v-model="editForm.accepts_marketing"
											type="checkbox"
											class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
										/>
										<span
											class="text-sm font-medium text-gray-700 dark:text-gray-300"
											>Accepts email marketing</span
										>
									</label>

									<label
										class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-[#0F1115] rounded-lg cursor-pointer"
									>
										<input
											v-model="editForm.tax_exempt"
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

								<!-- Tab 3: Sizes -->
								<div v-if="editTab === 'sizes'" class="space-y-4">
									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Ring left size</label
											>
											<input
												v-model="editForm.ring_left_size"
												type="text"
												placeholder="e.g. 7"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Ring right size</label
											>
											<input
												v-model="editForm.ring_right_size"
												type="text"
												placeholder="e.g. 7.5"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>
									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Wrist size</label
											>
											<input
												v-model="editForm.wrist_size"
												type="text"
												placeholder="e.g. 7 inches"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Neck size</label
											>
											<input
												v-model="editForm.neck_size"
												type="text"
												placeholder="e.g. 18 inches"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Ring size (single hand)</label
											>
											<input
												v-model="editForm.ring_size"
												type="text"
												placeholder="e.g. 7"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Preferred metal</label
											>
											<input
												v-model="editForm.preferred_metal"
												type="text"
												placeholder="Gold, Silver, etc."
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>
								</div>

								<!-- Edit Error Message -->
								<div
									v-if="editError"
									class="text-sm text-red-500 bg-red-50 dark:bg-red-900/20 px-4 py-3 rounded-lg border border-red-200 dark:border-red-800/30"
								>
									{{ editError }}
								</div>

								<!-- Edit Success Message -->
								<div
									v-if="editSuccess"
									class="text-sm text-green-600 bg-green-50 dark:bg-green-900/20 px-4 py-3 rounded-lg border border-green-200 dark:border-green-800/30"
								>
									{{ editSuccess }}
								</div>
							</div>

							<!-- Footer -->
							<div
								v-if="!editLoading"
								class="p-6 pt-4 border-t border-gray-100 dark:border-warm-border flex gap-3 flex-shrink-0"
							>
								<button
									@click="closeEditModal"
									class="flex-1 py-2.5 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-warm-dark-700 dark:text-gray-300 dark:hover:bg-white/10 transition"
								>
									Close
								</button>
								<button
									@click="saveCustomerEdit"
									:disabled="savingEdit"
									class="flex-1 py-2.5 rounded-lg font-bold text-white bg-[#D4AF37] hover:bg-[#b5952f] text-black disabled:opacity-50 transition flex items-center justify-center gap-2"
								>
									<svg
										v-if="savingEdit"
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
									<span>{{ savingEdit ? 'Saving...' : 'Save changes' }}</span>
								</button>
							</div>
						</div>
					</div>
				</Transition>
			</Teleport>
			<!-- Search Input -->
			<div class="relative">
				<input
					ref="searchInput"
					v-model="searchQuery"
					type="text"
					:placeholder="placeholder"
					@input="debouncedSearch"
					@focus="showDropdown = true"
					class="w-full px-4 py-3 pl-10 bg-white dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 focus:border-[#D4AF37]"
					data-testid="customer-search"
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
					class="absolute z-50 w-full mt-1 bg-white dark:bg-[#1a1c23] border border-gray-200 dark:border-warm-border rounded-xl shadow-lg max-h-60 overflow-y-auto"
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
						class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-warm-dark-700 flex items-center gap-3 border-b border-gray-100 dark:border-warm-border/50 last:border-0"
						data-testid="customer-option"
					>
						<div
							class="w-8 h-8 rounded-full bg-gray-100 dark:bg-warm-dark-900 flex items-center justify-center text-gray-500"
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
						class="w-full px-4 py-3 text-left hover:bg-[#D4AF37]/10 flex items-center gap-3 border-t-2 border-gray-100 dark:border-warm-border"
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
				@click="showCreateModalFlag = true"
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

		<!-- Create Customer Modal (Tabbed) -->
		<Teleport to="body">
			<Transition name="fade">
				<div
					v-if="showCreateModalFlag"
					class="fixed inset-0 z-[200] flex items-center justify-center p-4"
				>
					<div
						@click="handleCancelCreate"
						class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm"
					></div>
					<div
						class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col border border-transparent dark:border-warm-border"
					>
						<!-- Header -->
						<div
							class="p-6 pb-4 border-b border-gray-100 dark:border-warm-border flex items-center justify-between flex-shrink-0"
						>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white">
								Create new contact
							</h3>
							<button
								@click="handleCancelCreate"
								class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition"
							>
								<svg
									class="w-5 h-5 text-gray-400"
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

						<!-- Tabs -->
						<div
							class="flex border-b border-gray-100 dark:border-warm-border px-6 flex-shrink-0"
						>
							<button
								v-for="tab in tabs"
								:key="tab.key"
								@click="activeTab = tab.key"
								class="px-4 py-3 text-sm font-medium transition-colors relative"
								:class="
									activeTab === tab.key
										? 'text-blue-600 dark:text-blue-400'
										: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
								"
							>
								{{ tab.label }}
								<div
									v-if="activeTab === tab.key"
									class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400"
								></div>
							</button>
						</div>

						<!-- Form Content - Scrollable -->
						<div class="flex-1 overflow-y-auto p-6 space-y-5">
							<!-- Tab 1: Contact Details -->
							<div v-if="activeTab === 'contact'" class="space-y-4">
								<div>
									<label
										class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
									>
										Contact type <span class="text-red-500">*</span>
									</label>
									<select
										v-model="newCustomer.contact_type"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
									>
										<option value="Individual">Person</option>
										<option value="Company">Company</option>
									</select>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Name</label
										>
										<input
											v-model="newCustomer.name"
											type="text"
											placeholder="Full name"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Internal name</label
										>
										<input
											v-model="newCustomer.internal_name"
											type="text"
											placeholder="Internal calling name"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
										<p class="text-[10px] text-gray-400 mt-1">
											Internal calling name for this client, used in
											dashboards and day-to-day communication.
										</p>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Title</label
										>
										<input
											v-model="newCustomer.title"
											type="text"
											placeholder="e.g. CEO"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Title choices</label
										>
										<select
											v-model="newCustomer.title_choice"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										>
											<option value="">--------</option>
											<option value="Mr">Mr</option>
											<option value="Ms">Ms</option>
											<option value="Mrs">Mrs</option>
											<option value="Dr">Dr</option>
										</select>
									</div>
								</div>

								<div class="grid grid-cols-3 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Email</label
										>
										<input
											v-model="newCustomer.email"
											type="email"
											placeholder="email@example.com"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Phone</label
										>
										<div class="flex">
											<select
												v-model="newCustomer.phone_country"
												class="px-2 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-r-0 border-gray-200 dark:border-warm-border rounded-l-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											>
												<option
													v-for="c in usPhoneCodes"
													:key="c.code"
													:value="c.code"
												>
													{{ c.flag }} {{ c.code }}
												</option>
											</select>
											<input
												v-model="newCustomer.phone"
												type="tel"
												placeholder="(555) 123-4567"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-r-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Language</label
										>
										<select
											v-model="newCustomer.language"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										>
											<option value="en">English</option>
											<option value="es">Spanish</option>
											<option value="fr">French</option>
											<option value="de">German</option>
											<option value="zh">Chinese</option>
											<option value="hi">Hindi</option>
											<option value="ar">Arabic</option>
										</select>
									</div>
								</div>

								<div class="grid grid-cols-3 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Street number</label
										>
										<input
											v-model="newCustomer.street_number"
											type="text"
											placeholder="123"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Street</label
										>
										<input
											v-model="newCustomer.street"
											type="text"
											placeholder="Main St"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>City</label
										>
										<input
											v-model="newCustomer.city"
											type="text"
											placeholder="New York"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>

								<div class="grid grid-cols-3 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Postcode</label
										>
										<input
											v-model="newCustomer.pincode"
											type="text"
											placeholder="10001"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>State/Region</label
										>
										<select
											v-model="newCustomer.state"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										>
											<option value="">Select state</option>
											<option
												v-for="s in usStates"
												:key="s.code"
												:value="s.code"
											>
												{{ s.name }}
											</option>
										</select>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Country</label
										>
										<select
											v-model="newCustomer.country"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										>
											<option value="United States">United States</option>
											<option value="Canada">Canada</option>
											<option value="Mexico">Mexico</option>
											<option value="India">India</option>
											<option value="United Kingdom">United Kingdom</option>
										</select>
									</div>
								</div>
							</div>

							<!-- Tab 2: Extra Details -->
							<div v-if="activeTab === 'extra'" class="space-y-4">
								<div class="grid grid-cols-3 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Bank account number</label
										>
										<input
											v-model="newCustomer.bank_account"
											type="text"
											placeholder="Account number"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>SWIFT/BIC code</label
										>
										<input
											v-model="newCustomer.swift_bic"
											type="text"
											placeholder="SWIFT code"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Bank name</label
										>
										<input
											v-model="newCustomer.bank_name"
											type="text"
											placeholder="Bank name"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Phone 2</label
										>
										<input
											v-model="newCustomer.phone2"
											type="tel"
											placeholder="Secondary phone"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Client number</label
										>
										<input
											v-model="newCustomer.client_number"
											type="text"
											placeholder="Client ID"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Internal notes</label
										>
										<textarea
											v-model="newCustomer.internal_notes"
											rows="3"
											placeholder="Add a note"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 resize-none"
										></textarea>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Birth date</label
										>
										<input
											v-model="newCustomer.birth_date"
											type="date"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Marriage date</label
										>
										<input
											v-model="newCustomer.marriage_date"
											type="date"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Partner name</label
										>
										<input
											v-model="newCustomer.partner_name"
											type="text"
											placeholder="Partner/spouse name"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Partner phone</label
										>
										<input
											v-model="newCustomer.partner_phone"
											type="tel"
											placeholder="Partner phone"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Partner email</label
										>
										<input
											v-model="newCustomer.partner_email"
											type="email"
											placeholder="Partner email"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Discount (%)</label
										>
										<input
											v-model.number="newCustomer.discount"
											type="number"
											min="0"
											max="100"
											placeholder="0"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<label
										class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-[#0F1115] rounded-lg cursor-pointer"
									>
										<input
											v-model="newCustomer.accepts_marketing"
											type="checkbox"
											class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
										/>
										<span
											class="text-sm font-medium text-gray-700 dark:text-gray-300"
											>Accepts email marketing</span
										>
									</label>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Gender</label
										>
										<select
											v-model="newCustomer.gender"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										>
											<option value="">--------</option>
											<option value="Male">Male</option>
											<option value="Female">Female</option>
											<option value="Other">Other</option>
										</select>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Profession</label
										>
										<input
											v-model="newCustomer.profession"
											type="text"
											placeholder="Profession"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Tags</label
										>
										<input
											v-model="newCustomer.tags"
											type="text"
											placeholder="VIP, Wholesale, etc."
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
										<p class="text-[10px] text-gray-400 mt-1">
											A comma-separated list of tags.
										</p>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Works at</label
										>
										<input
											v-model="newCustomer.works_at"
											type="text"
											placeholder="Company name"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Assigned to</label
										>
										<input
											v-model="newCustomer.assigned_to"
											type="text"
											placeholder="Sales person"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
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

							<!-- Tab 3: Shipping Address -->
							<div v-if="activeTab === 'shipping'" class="space-y-4">
								<div class="flex items-center gap-3 mb-3">
									<label class="flex items-center gap-2 cursor-pointer">
										<input
											v-model="newCustomer.same_as_billing"
											type="checkbox"
											class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
										/>
										<span
											class="text-sm font-medium text-gray-700 dark:text-gray-300"
											>Same as billing address</span
										>
									</label>
								</div>

								<template v-if="!newCustomer.same_as_billing">
									<div class="grid grid-cols-2 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Street number</label
											>
											<input
												v-model="newCustomer.ship_street_number"
												type="text"
												placeholder="123"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Street</label
											>
											<input
												v-model="newCustomer.ship_street"
												type="text"
												placeholder="Main St"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
									</div>

									<div class="grid grid-cols-3 gap-3">
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>City</label
											>
											<input
												v-model="newCustomer.ship_city"
												type="text"
												placeholder="City"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>Postcode</label
											>
											<input
												v-model="newCustomer.ship_pincode"
												type="text"
												placeholder="10001"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											/>
										</div>
										<div>
											<label
												class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
												>State/Region</label
											>
											<select
												v-model="newCustomer.ship_state"
												class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
											>
												<option value="">Select state</option>
												<option
													v-for="s in usStates"
													:key="s.code"
													:value="s.code"
												>
													{{ s.name }}
												</option>
											</select>
										</div>
									</div>

									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Country</label
										>
										<select
											v-model="newCustomer.ship_country"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										>
											<option value="United States">United States</option>
											<option value="Canada">Canada</option>
											<option value="Mexico">Mexico</option>
										</select>
									</div>
								</template>
							</div>

							<!-- Tab 4: Sizes -->
							<div v-if="activeTab === 'sizes'" class="space-y-4">
								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Ring left size</label
										>
										<input
											v-model="newCustomer.ring_left_size"
											type="text"
											placeholder="e.g. 7"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Ring right size</label
										>
										<input
											v-model="newCustomer.ring_right_size"
											type="text"
											placeholder="e.g. 7.5"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>
								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Middle left size</label
										>
										<input
											v-model="newCustomer.middle_left_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Middle right size</label
										>
										<input
											v-model="newCustomer.middle_right_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>
								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Index left size</label
										>
										<input
											v-model="newCustomer.index_left_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Index right size</label
										>
										<input
											v-model="newCustomer.index_right_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>
								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Pink left size</label
										>
										<input
											v-model="newCustomer.pink_left_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Pink right size</label
										>
										<input
											v-model="newCustomer.pink_right_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>
								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Thumb left size</label
										>
										<input
											v-model="newCustomer.thumb_left_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Thumb right size</label
										>
										<input
											v-model="newCustomer.thumb_right_size"
											type="text"
											placeholder="Size"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
								</div>
								<div class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Wrist size</label
										>
										<input
											v-model="newCustomer.wrist_size"
											type="text"
											placeholder="e.g. 7 inches"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
									<div>
										<label
											class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1 block"
											>Neck size</label
										>
										<input
											v-model="newCustomer.neck_size"
											type="text"
											placeholder="e.g. 18 inches"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50"
										/>
									</div>
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
							class="p-6 pt-4 border-t border-gray-100 dark:border-warm-border flex gap-3 flex-shrink-0"
						>
							<button
								@click="handleCancelCreate"
								class="flex-1 py-2.5 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-warm-dark-700 dark:text-gray-300 dark:hover:bg-white/10 transition"
							>
								Close
							</button>
							<button
								@click="createCustomer"
								:disabled="!newCustomer.name || creating"
								class="flex-1 py-2.5 rounded-lg font-bold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition flex items-center justify-center gap-2"
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
								<span>{{ creating ? 'Creating...' : 'Add contact →' }}</span>
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>
	</div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useCartStore } from '@/stores/cart.js'
import { useSessionStore } from '@/stores/session.js'

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
const session = useSessionStore()
const isAdmin = computed(() => session.isAdmin || session.isManager)

const tabs = [
	{ key: 'contact', label: 'Contact details' },
	{ key: 'extra', label: 'Extra details' },
	{ key: 'shipping', label: 'Shipping address' },
	{ key: 'sizes', label: 'Sizes' },
]

const usStates = [
	{ code: 'AL', name: 'Alabama' },
	{ code: 'AK', name: 'Alaska' },
	{ code: 'AZ', name: 'Arizona' },
	{ code: 'AR', name: 'Arkansas' },
	{ code: 'CA', name: 'California' },
	{ code: 'CO', name: 'Colorado' },
	{ code: 'CT', name: 'Connecticut' },
	{ code: 'DE', name: 'Delaware' },
	{ code: 'FL', name: 'Florida' },
	{ code: 'GA', name: 'Georgia' },
	{ code: 'HI', name: 'Hawaii' },
	{ code: 'ID', name: 'Idaho' },
	{ code: 'IL', name: 'Illinois' },
	{ code: 'IN', name: 'Indiana' },
	{ code: 'IA', name: 'Iowa' },
	{ code: 'KS', name: 'Kansas' },
	{ code: 'KY', name: 'Kentucky' },
	{ code: 'LA', name: 'Louisiana' },
	{ code: 'ME', name: 'Maine' },
	{ code: 'MD', name: 'Maryland' },
	{ code: 'MA', name: 'Massachusetts' },
	{ code: 'MI', name: 'Michigan' },
	{ code: 'MN', name: 'Minnesota' },
	{ code: 'MS', name: 'Mississippi' },
	{ code: 'MO', name: 'Missouri' },
	{ code: 'MT', name: 'Montana' },
	{ code: 'NE', name: 'Nebraska' },
	{ code: 'NV', name: 'Nevada' },
	{ code: 'NH', name: 'New Hampshire' },
	{ code: 'NJ', name: 'New Jersey' },
	{ code: 'NM', name: 'New Mexico' },
	{ code: 'NY', name: 'New York' },
	{ code: 'NC', name: 'North Carolina' },
	{ code: 'ND', name: 'North Dakota' },
	{ code: 'OH', name: 'Ohio' },
	{ code: 'OK', name: 'Oklahoma' },
	{ code: 'OR', name: 'Oregon' },
	{ code: 'PA', name: 'Pennsylvania' },
	{ code: 'RI', name: 'Rhode Island' },
	{ code: 'SC', name: 'South Carolina' },
	{ code: 'SD', name: 'South Dakota' },
	{ code: 'TN', name: 'Tennessee' },
	{ code: 'TX', name: 'Texas' },
	{ code: 'UT', name: 'Utah' },
	{ code: 'VT', name: 'Vermont' },
	{ code: 'VA', name: 'Virginia' },
	{ code: 'WA', name: 'Washington' },
	{ code: 'WV', name: 'West Virginia' },
	{ code: 'WI', name: 'Wisconsin' },
	{ code: 'WY', name: 'Wyoming' },
	{ code: 'DC', name: 'District of Columbia' },
]

const usPhoneCodes = [
	{ code: '+1', flag: '🇺🇸' },
	{ code: '+1', flag: '🇨🇦' },
	{ code: '+52', flag: '🇲🇽' },
	{ code: '+44', flag: '🇬🇧' },
	{ code: '+91', flag: '🇮🇳' },
]

// State
const showSearch = ref(!cart.customer)
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const showDropdown = ref(false)
const showCreateModalFlag = ref(false)
const creating = ref(false)
const createError = ref('')
const searchInput = ref(null)
const activeTab = ref('contact')

// Recent Customers
const recentCustomers = ref([])
const recentLimit = ref(10)
const recentLoading = ref(false)

// Edit Modal
const showEditModal = ref(false)
const editTab = ref('contact')
const editLoading = ref(false)
const savingEdit = ref(false)
const editError = ref('')
const editSuccess = ref('')
const editCustomerName = ref('')
const editForm = ref({})

const recentCustomersResource = createResource({
	url: 'zevar_core.api.customer.get_recent_customers',
	auto: false,
})

async function loadRecentCustomers() {
	recentLoading.value = true
	try {
		const result = await recentCustomersResource.submit({
			limit: recentLimit.value,
		})
		recentCustomers.value = result || []
	} catch (e) {
		console.error('Failed to load recent customers:', e)
		recentCustomers.value = []
	} finally {
		recentLoading.value = false
	}
}

async function loadMoreRecent() {
	recentLimit.value += 10
	await loadRecentCustomers()
}

const editCustomerInfoResource = createResource({
	url: 'zevar_core.api.customer.get_customer_edit_info',
	auto: false,
})

async function openEditModal(customerData) {
	editCustomerName.value = customerData.name || customerData.customer_name
	showEditModal.value = true
	editError.value = ''
	editSuccess.value = ''
	editTab.value = 'contact'
	editLoading.value = true

	try {
		const r = await editCustomerInfoResource.submit({
			customer_name: editCustomerName.value,
		})
		const data = r?.data || r
		if (data) {
			// Map API response to edit form
			editForm.value = {
				customer_type: data.customer_type || 'Individual',
				mobile_no: data.mobile_no || '',
				email_id: data.email_id || '',
				gender: data.gender || '',
				birth_date: data.birth_date || '',
				profession: data.profession || '',
				partner_name: data.partner_name || '',
				partner_phone: data.partner_phone || '',
				partner_email: data.partner_email || '',
				marriage_date: data.marriage_date || '',
				ring_size: data.ring_size || '',
				preferred_metal: data.preferred_metal || '',
				preferred_purity: data.preferred_purity || '',
				tags: '',
				internal_notes: data.internal_notes || '',
				phone2: data.phone2 || '',
				accepts_marketing: data.accepts_marketing == 1,
				tax_exempt: data.tax_exempt == 1,
				ring_left_size: data.ring_left_size || '',
				ring_right_size: data.ring_right_size || '',
				middle_left_size: data.middle_left_size || '',
				middle_right_size: data.middle_right_size || '',
				index_left_size: data.index_left_size || '',
				index_right_size: data.index_right_size || '',
				pink_left_size: data.pink_left_size || '',
				pink_right_size: data.pink_right_size || '',
				thumb_left_size: data.thumb_left_size || '',
				thumb_right_size: data.thumb_right_size || '',
				wrist_size: data.wrist_size || '',
				neck_size: data.neck_size || '',
				customer_group: data.customer_group || '',
			}
		}
	} catch (e) {
		editError.value = e?.message || 'Failed to load customer details'
	} finally {
		editLoading.value = false
	}
}

async function saveCustomerEdit() {
	savingEdit.value = true
	editError.value = ''
	editSuccess.value = ''

	try {
		const r = await createResource({
			url: 'zevar_core.api.customer.update_customer',
			params: {
				customer_name: editCustomerName.value,
				customer_type: editForm.value.customer_type || null,
				mobile_no: editForm.value.mobile_no || null,
				email_id: editForm.value.email_id || null,
				gender: editForm.value.gender || null,
				birth_date: editForm.value.birth_date || null,
				profession: editForm.value.profession || null,
				partner_name: editForm.value.partner_name || null,
				partner_phone: editForm.value.partner_phone || null,
				partner_email: editForm.value.partner_email || null,
				marriage_date: editForm.value.marriage_date || null,
				ring_size: editForm.value.ring_size || null,
				preferred_metal: editForm.value.preferred_metal || null,
				preferred_purity: editForm.value.preferred_purity || null,
				tags: editForm.value.tags || null,
				internal_notes: editForm.value.internal_notes || null,
				phone2: editForm.value.phone2 || null,
				accepts_marketing: editForm.value.accepts_marketing ? 1 : 0,
				tax_exempt: editForm.value.tax_exempt ? 1 : 0,
				ring_left_size: editForm.value.ring_left_size || null,
				ring_right_size: editForm.value.ring_right_size || null,
				middle_left_size: editForm.value.middle_left_size || null,
				middle_right_size: editForm.value.middle_right_size || null,
				index_left_size: editForm.value.index_left_size || null,
				index_right_size: editForm.value.index_right_size || null,
				pink_left_size: editForm.value.pink_left_size || null,
				pink_right_size: editForm.value.pink_right_size || null,
				thumb_left_size: editForm.value.thumb_left_size || null,
				thumb_right_size: editForm.value.thumb_right_size || null,
				wrist_size: editForm.value.wrist_size || null,
				neck_size: editForm.value.neck_size || null,
			},
		}).fetch()

		const data = r?.data || r
		if (data && data.success) {
			editSuccess.value = data.message || 'Customer updated successfully'

			// Update cart if this is the currently selected customer
			if (
				cart.customer &&
				(cart.customer.name === editCustomerName.value ||
					cart.customer.customer_name === editCustomerName.value)
			) {
				const updated = { ...cart.customer }
				if (editForm.value.mobile_no) updated.mobile_no = editForm.value.mobile_no
				if (editForm.value.email_id) updated.email_id = editForm.value.email_id
				cart.setCustomer(updated)
			}

			// Refresh recent customers list
			await loadRecentCustomers()

			// Close modal after delay
			setTimeout(() => {
				closeEditModal()
			}, 1500)
		} else {
			editError.value = data?.message || 'Failed to update customer'
		}
	} catch (e) {
		editError.value = e?.response?.data?.message || e?.message || 'Failed to update customer'
		console.error('Customer update error:', e)
	} finally {
		savingEdit.value = false
	}
}

function closeEditModal() {
	showEditModal.value = false
	editError.value = ''
	editSuccess.value = ''
	editForm.value = {}
	editCustomerName.value = ''
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
	loadRecentCustomers()
})

function openCreateModal() {
	showCreateModalFlag.value = true
	showDropdown.value = false
}

function handleCancelCreate() {
	showCreateModalFlag.value = false
	resetCreateForm()
}

const customer = computed(() => cart.customer)

const showCreateOption = computed(() => {
	return searchQuery.value.length >= 2 && !searching.value
})

let searchTimeout = null
function debouncedSearch() {
	clearTimeout(searchTimeout)
	searchTimeout = setTimeout(() => {
		performSearch()
	}, 300)
}

const customerSearchResource = createResource({
	url: 'zevar_core.api.customer.search_customers',
	auto: false,
})

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
		searchResults.value = list.map((c) => ({
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

const customerDetailsResource = createResource({
	url: 'zevar_core.api.customer.get_customer_details',
	auto: false,
})

async function selectCustomer(customerData) {
	try {
		const r = await customerDetailsResource.submit({
			customer_name: customerData.customer_name || customerData.name,
		})
		const fullData = r?.data || r
		if (fullData && fullData.customer_name && !fullData.name) {
			fullData.name = fullData.customer_name
		}
		if (fullData) {
			cart.setCustomer(fullData)
		} else {
			cart.setCustomer(customerData)
		}
	} catch (e) {
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

function getDefaultForm() {
	return {
		name: '',
		contact_type: 'Individual',
		internal_name: '',
		title: '',
		title_choice: '',
		email: '',
		phone: '',
		phone_country: '+1',
		phone2: '',
		language: 'en',
		street_number: '',
		street: '',
		city: '',
		state: '',
		pincode: '',
		country: 'United States',
		// Extra details
		bank_account: '',
		swift_bic: '',
		bank_name: '',
		client_number: '',
		internal_notes: '',
		birth_date: '',
		marriage_date: '',
		partner_name: '',
		partner_phone: '',
		partner_email: '',
		discount: null,
		accepts_marketing: false,
		gender: '',
		profession: '',
		tags: '',
		works_at: '',
		assigned_to: '',
		tax_exempt: false,
		// Shipping
		same_as_billing: true,
		ship_street_number: '',
		ship_street: '',
		ship_city: '',
		ship_pincode: '',
		ship_state: '',
		ship_country: 'United States',
		// Sizes
		ring_left_size: '',
		ring_right_size: '',
		middle_left_size: '',
		middle_right_size: '',
		index_left_size: '',
		index_right_size: '',
		pink_left_size: '',
		pink_right_size: '',
		thumb_left_size: '',
		thumb_right_size: '',
		wrist_size: '',
		neck_size: '',
	}
}

const newCustomer = ref(getDefaultForm())

async function createCustomer() {
	if (!newCustomer.value.name) return

	creating.value = true
	createError.value = ''

	try {
		const billingAddress =
			[newCustomer.value.street_number, newCustomer.value.street]
				.filter(Boolean)
				.join(' ') || null

		const r = await createResource({
			url: 'zevar_core.api.customer.quick_create_customer',
			params: {
				customer_name: newCustomer.value.name,
				customer_type: newCustomer.value.contact_type,
				mobile_no: newCustomer.value.phone || null,
				email_id: newCustomer.value.email || null,
				address_line1: billingAddress,
				city: newCustomer.value.city || null,
				state: newCustomer.value.state || null,
				pincode: newCustomer.value.pincode || null,
				country: newCustomer.value.country || null,
				tax_exempt: newCustomer.value.tax_exempt ? 1 : 0,
				gender: newCustomer.value.gender || null,
				birth_date: newCustomer.value.birth_date || null,
				partner_name: newCustomer.value.partner_name || null,
				partner_phone: newCustomer.value.partner_phone || null,
				partner_email: newCustomer.value.partner_email || null,
				marriage_date: newCustomer.value.marriage_date || null,
				profession: newCustomer.value.profession || null,
				tags: newCustomer.value.tags || null,
				internal_notes: newCustomer.value.internal_notes || null,
				phone2: newCustomer.value.phone2 || null,
				accepts_marketing: newCustomer.value.accepts_marketing ? 1 : 0,
				// Sizes
				ring_left_size: newCustomer.value.ring_left_size || null,
				ring_right_size: newCustomer.value.ring_right_size || null,
				middle_left_size: newCustomer.value.middle_left_size || null,
				middle_right_size: newCustomer.value.middle_right_size || null,
				index_left_size: newCustomer.value.index_left_size || null,
				index_right_size: newCustomer.value.index_right_size || null,
				pink_left_size: newCustomer.value.pink_left_size || null,
				pink_right_size: newCustomer.value.pink_right_size || null,
				thumb_left_size: newCustomer.value.thumb_left_size || null,
				thumb_right_size: newCustomer.value.thumb_right_size || null,
				wrist_size: newCustomer.value.wrist_size || null,
				neck_size: newCustomer.value.neck_size || null,
				// Shipping address
				same_as_billing: newCustomer.value.same_as_billing ? 1 : 0,
				ship_address_line1: !newCustomer.value.same_as_billing
					? [newCustomer.value.ship_street_number, newCustomer.value.ship_street]
							.filter(Boolean)
							.join(' ') || null
					: null,
				ship_city: newCustomer.value.ship_city || null,
				ship_state: newCustomer.value.ship_state || null,
				ship_pincode: newCustomer.value.ship_pincode || null,
				ship_country: newCustomer.value.ship_country || null,
			},
		}).fetch()
		const data = r?.data || r

		if (data.success) {
			const customerData = {
				...data,
				name: data.customer_name,
			}
			cart.setCustomer(customerData)
			showCreateModalFlag.value = false
			showSearch.value = false
			searchQuery.value = ''
			resetCreateForm()
			emit('selected', cart.customer)
		} else {
			createError.value = data.message || 'Failed to create customer'
		}
	} catch (e) {
		const errorMsg = e?.response?.data?.message || e?.message || e?.exception || String(e)
		createError.value = errorMsg
		console.error('Customer creation error:', e)
	} finally {
		creating.value = false
	}
}

function clearAndShowSearch() {
	cart.clearCustomer()
	showSearch.value = true
	emit('cleared')
	nextTick(() => {
		searchInput.value?.focus()
	})
}

function clearSearch() {
	searchQuery.value = ''
	searchResults.value = []
	searchInput.value?.focus()
}

function resetCreateForm() {
	newCustomer.value = getDefaultForm()
	createError.value = ''
	activeTab.value = 'contact'
}

watch(
	() => cart.customer,
	(newVal) => {
		if (newVal) {
			showSearch.value = false
		}
	}
)

watch(searchQuery, (val) => {
	if (val && !newCustomer.value.name) {
		newCustomer.value.name = val
	}
})

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
