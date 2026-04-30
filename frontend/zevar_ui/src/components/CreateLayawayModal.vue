<template>
	<component
		:is="inlineMode ? 'div' : 'Transition'"
		name="fade"
		:class="inlineMode ? 'h-full' : ''"
	>
		<div
			v-if="inlineMode || show"
			:class="[
				inlineMode
					? 'h-full flex flex-col bg-white dark:bg-[#1a1c23] w-full rounded-3xl overflow-hidden'
					: 'fixed inset-0 z-[100] flex items-center justify-center p-4',
			]"
		>
			<div
				v-if="!inlineMode"
				class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm"
				@click="close"
			></div>

			<div
				class="relative bg-white dark:bg-[#1a1c23] w-full overflow-hidden flex flex-col"
				:class="[
					inlineMode
						? 'flex-1 h-full rounded-3xl'
						: 'max-w-6xl max-h-[95vh] rounded-3xl shadow-2xl border border-transparent dark:border-warm-border',
				]"
			>
				<!-- Header -->
				<div
					class="flex items-center justify-between p-5 border-b border-gray-100 dark:border-warm-border/50 bg-gradient-to-r from-gray-50 to-white dark:from-gray-900 dark:to-[#1a1c23] rounded-t-3xl flex-shrink-0"
				>
					<div class="flex items-center gap-4">
						<div
							class="w-10 h-10 rounded-xl bg-[#D4AF37]/20 flex items-center justify-center"
						>
							<svg
								class="w-5 h-5 text-[#D4AF37]"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
								/>
							</svg>
						</div>
						<div>
							<h2 class="text-lg font-bold text-gray-900 dark:text-white">
								Create Layaway Contract
							</h2>
							<p class="text-xs text-gray-500 dark:text-gray-400">
								Fill all required fields marked with *
							</p>
						</div>
					</div>
					<div class="flex items-center gap-2">
						<!-- Quick Actions -->
						<div class="hidden md:flex items-center gap-2 mr-4">
							<button
								@click="showIdScanner = !showIdScanner"
								class="px-3 py-1.5 text-xs font-medium text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/10 transition flex items-center gap-1.5"
								title="Scan ID Document"
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
										d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
									/>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
									/>
								</svg>
								Scan ID
							</button>
							<button
								@click="focusBarcodeScanner"
								class="px-3 py-1.5 text-xs font-medium text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/10 transition flex items-center gap-1.5"
								title="Scan Barcode"
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
										d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h2M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
									/>
								</svg>
								Scan Barcode
							</button>
						</div>
						<button
							@click="close"
							class="p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full transition"
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
				</div>

				<!-- Two Column Layout -->
				<div class="flex flex-col lg:flex-row flex-1 overflow-hidden">
					<!-- Left Column - Customer & Details -->
					<div
						class="flex-1 p-5 overflow-y-auto custom-scrollbar rounded-bl-3xl"
						:style="inlineMode ? '' : 'max-height: calc(95vh - 140px)'"
					>
						<IDScannerPanel
							v-model="idScan"
							:show="showIdScanner"
							@close="showIdScanner = false"
							@apply-data="applyIdData"
						/>

						<!-- Customer Selection Section -->
						<div class="mb-5">
							<div class="flex items-center justify-between mb-3">
								<h3
									class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Customer <span class="text-red-500">*</span>
								</h3>
								<button
									@click="isNewCustomerMode = !isNewCustomerMode"
									class="text-xs font-medium text-[#D4AF37] hover:text-[#c9a432] transition flex items-center gap-1"
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
											d="M12 4v16m8-8H4"
										/>
									</svg>
									{{ isNewCustomerMode ? 'Search Existing' : 'New Customer' }}
								</button>
							</div>

							<!-- Search Existing Customer -->
							<div v-if="!isNewCustomerMode" class="relative">
								<div class="relative">
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
										/>
									</svg>
									<input
										v-model="customerSearch"
										type="text"
										placeholder="Search by name, phone, or customer ID..."
										@input="searchCustomers"
										@focus="showCustomerDropdown = true"
										class="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent"
									/>
								</div>
								<div
									v-if="showCustomerDropdown && customerResults.length > 0"
									class="absolute z-20 w-full mt-1 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg shadow-lg max-h-56 overflow-y-auto"
								>
									<button
										v-for="customer in customerResults"
										:key="customer.name"
										type="button"
										@click="selectCustomer(customer)"
										class="w-full px-4 py-3 text-left text-sm hover:bg-gray-50 dark:hover:bg-warm-dark-800 transition border-b border-gray-100 dark:border-warm-border last:border-0"
									>
										<div class="flex items-center justify-between">
											<div>
												<span
													class="font-medium text-gray-900 dark:text-white block"
													>{{ customer.customer_name }}</span
												>
												<span
													v-if="customer.mobile_no"
													class="text-gray-500 text-xs"
												>
													{{ customer.mobile_no }}
												</span>
											</div>
											<span class="text-xs text-[#D4AF37]">{{
												customer.name
											}}</span>
										</div>
									</button>
								</div>
							</div>

							<!-- New Customer Form -->
							<div
								v-else
								class="p-4 bg-gray-50 dark:bg-warm-dark-900 rounded-lg border border-gray-200 dark:border-warm-border"
							>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Full Name *</label
										>
										<input
											v-model="newCustomer.name"
											type="text"
											placeholder="Full legal name"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Phone *</label
										>
										<input
											v-model="newCustomer.phone"
											type="tel"
											placeholder="Phone number"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Email</label
										>
										<input
											v-model="newCustomer.email"
											type="email"
											placeholder="Email address"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Customer Type</label
										>
										<select
											v-model="newCustomer.type"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										>
											<option value="Individual">Individual</option>
											<option value="Company">Company</option>
										</select>
									</div>
								</div>
								<div class="mt-3">
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Address</label
									>
									<textarea
										v-model="newCustomer.address"
										rows="2"
										placeholder="Full street address"
										class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37] resize-none"
									></textarea>
								</div>
								<div class="grid grid-cols-3 gap-3 mt-3">
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>City</label
										>
										<input
											v-model="newCustomer.city"
											type="text"
											placeholder="City"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>State</label
										>
										<input
											v-model="newCustomer.state"
											type="text"
											placeholder="State"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>ZIP</label
										>
										<input
											v-model="newCustomer.zip"
											type="text"
											placeholder="ZIP Code"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
								</div>
							</div>
						</div>

						<!-- Customer Details Card -->
						<div
							v-if="selectedCustomer || isNewCustomerMode"
							class="mb-5 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800/30"
						>
							<h4
								class="text-xs font-bold text-blue-900 dark:text-blue-200 uppercase tracking-wider mb-3"
							>
								Customer Information
							</h4>
							<div class="grid grid-cols-2 gap-3 text-sm">
								<div>
									<span class="text-gray-500 dark:text-gray-400 text-xs"
										>Name</span
									>
									<p class="font-medium text-gray-900 dark:text-white">
										{{
											isNewCustomerMode
												? newCustomer.name
												: selectedCustomer?.customer_name
										}}
									</p>
								</div>
								<div>
									<span class="text-gray-500 dark:text-gray-400 text-xs"
										>Phone</span
									>
									<p class="font-medium text-gray-900 dark:text-white">
										{{
											isNewCustomerMode
												? newCustomer.phone
												: selectedCustomer?.mobile_no || form.phone
										}}
									</p>
								</div>
								<div>
									<span class="text-gray-500 dark:text-gray-400 text-xs"
										>Email</span
									>
									<p class="font-medium text-gray-900 dark:text-white">
										{{
											isNewCustomerMode
												? newCustomer.email
												: selectedCustomer?.email_id || form.email
										}}
									</p>
								</div>
								<div>
									<span class="text-gray-500 dark:text-gray-400 text-xs"
										>Address</span
									>
									<p class="font-medium text-gray-900 dark:text-white truncate">
										{{ form.address || form.city || 'Not provided' }}
									</p>
								</div>
								<div v-if="hasNominee && nominee.name">
									<span class="text-gray-500 dark:text-gray-400 text-xs"
										>Nominee</span
									>
									<p class="font-medium text-[#D4AF37]">
										{{ nominee.name }}
										<span
											v-if="nominee.relationship"
											class="text-xs text-gray-400"
											>({{ nominee.relationship }})</span
										>
									</p>
								</div>
								<div v-if="hasNominee && nominee.phone">
									<span class="text-gray-500 dark:text-gray-400 text-xs"
										>Nominee Phone</span
									>
									<p class="font-medium text-gray-900 dark:text-white">
										{{ nominee.phone }}
									</p>
								</div>
							</div>
						</div>

						<!-- ID Verification Section -->
						<div class="mb-5">
							<h3
								class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
							>
								ID Verification
							</h3>
							<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>ID Type</label
									>
									<select
										v-model="form.idType"
										class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
									>
										<option value="">Select</option>
										<option value="drivers_license">Driver's License</option>
										<option value="passport">Passport</option>
										<option value="national_id">National ID</option>
										<option value="state_id">State ID</option>
										<option value="other">Other</option>
									</select>
								</div>
								<div class="col-span-2 md:col-span-3">
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>ID Number</label
									>
									<input
										v-model="form.idNumber"
										type="text"
										placeholder="Enter ID number"
										class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
									/>
								</div>
							</div>
						</div>

						<!-- Nominee / Secondary Contact -->
						<div class="mb-5">
							<div class="flex items-center justify-between mb-3">
								<h3
									class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
								>
									Nominee / Secondary Contact
								</h3>
								<div class="flex items-center gap-3">
									<span
										v-if="hasNominee && nominee.name"
										class="text-xs text-blue-500 font-medium"
									>
										{{ nominee.name }} ({{ nominee.relationship || 'N/A' }})
									</span>
									<label class="flex items-center gap-2 cursor-pointer">
										<input
											type="checkbox"
											v-model="hasNominee"
											class="w-4 h-4 text-[#D4AF37] rounded focus:ring-[#D4AF37]"
										/>
										<span class="text-xs text-gray-600 dark:text-gray-400">{{
											hasNominee ? 'Remove nominee' : 'Add nominee'
										}}</span>
									</label>
								</div>
							</div>
							<Transition name="slide-down">
								<div v-if="hasNominee" class="grid grid-cols-2 gap-3">
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Full Name</label
										>
										<input
											v-model="nominee.name"
											type="text"
											placeholder="Nominee name"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Relationship</label
										>
										<select
											v-model="nominee.relationship"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										>
											<option value="">Select</option>
											<option value="spouse">Spouse</option>
											<option value="parent">Parent</option>
											<option value="sibling">Sibling</option>
											<option value="child">Child</option>
											<option value="friend">Friend</option>
											<option value="other">Other</option>
										</select>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Phone</label
										>
										<input
											v-model="nominee.phone"
											type="tel"
											placeholder="Contact number"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div>
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Email</label
										>
										<input
											v-model="nominee.email"
											type="email"
											placeholder="Email address"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
								</div>
							</Transition>
						</div>

						<!-- Address Section -->
						<div class="mb-5">
							<h3
								class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
							>
								Address Details
							</h3>
							<div class="space-y-3">
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Street Address</label
									>
									<input
										v-model="form.address"
										type="text"
										placeholder="Street address, apt/suite number"
										class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
									/>
								</div>
								<div class="grid grid-cols-4 gap-3">
									<div class="col-span-1">
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>City</label
										>
										<input
											v-model="form.city"
											type="text"
											placeholder="City"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div class="col-span-1">
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>State</label
										>
										<input
											v-model="form.state"
											type="text"
											placeholder="State"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div class="col-span-1">
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>ZIP</label
										>
										<input
											v-model="form.zip"
											type="text"
											placeholder="ZIP"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
									<div class="col-span-1">
										<label
											class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
											>Country</label
										>
										<input
											v-model="form.country"
											type="text"
											placeholder="Country"
											class="w-full px-3 py-2 text-sm bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Right Column - Items & Summary -->
					<div
						class="flex-1 p-5 border-l border-gray-100 dark:border-warm-border/50 bg-gray-50/50 dark:bg-[#1a1c23]/50 overflow-y-auto rounded-br-3xl"
						:style="inlineMode ? '' : 'max-height: calc(95vh - 140px)'"
					>
						<!-- Layaway Details -->
						<div class="mb-5">
							<h3
								class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
							>
								Layaway Details
							</h3>
							<div class="grid grid-cols-2 gap-3">
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Start Date *</label
									>
									<input
										v-model="form.startDate"
										type="date"
										class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
									/>
								</div>
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Status</label
									>
									<select
										v-model="form.status"
										class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
									>
										<option value="Active">Active</option>
										<option value="Draft">Draft</option>
									</select>
								</div>
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Payment Schedule</label
									>
									<select
										v-model="form.paymentSchedule"
										class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
									>
										<option value="Weekly">Weekly</option>
										<option value="Bi-Weekly">Bi-Weekly</option>
										<option value="Monthly">Monthly</option>
									</select>
								</div>
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Duration ({{
											form.paymentSchedule === 'Monthly'
												? 'Months'
												: 'Weeks'
										}}) *</label
									>
									<select
										v-model.number="form.durationWeeks"
										class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
									>
										<template v-if="form.paymentSchedule === 'Monthly'">
											<option :value="1">1 month</option>
											<option :value="2">2 months</option>
											<option :value="3">3 months</option>
											<option :value="6">6 months</option>
											<option :value="9">9 months</option>
											<option :value="12">12 months</option>
										</template>
										<template v-else>
											<option :value="2">2 weeks</option>
											<option :value="4">4 weeks</option>
											<option :value="6">6 weeks</option>
											<option :value="8">8 weeks</option>
											<option :value="10">10 weeks</option>
											<option :value="12">12 weeks</option>
										</template>
									</select>
								</div>
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Deposit Amount *</label
									>
									<div class="relative">
										<span
											class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm"
											>$</span
										>
										<input
											v-model.number="form.deposit"
											type="number"
											min="0"
											:step="0.01"
											class="w-full pl-7 pr-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37]"
										/>
									</div>
								</div>
								<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
									Deposit payment method is selected from the sidebar.
								</p>
								<div>
									<label
										class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
										>Tax Rate (%)</label
									>
									<div class="relative">
										<input
											v-model.number="form.taxRate"
											type="number"
											min="0"
											max="100"
											:step="0.1"
											class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37] pr-8"
										/>
										<span
											class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm"
											>%</span
										>
									</div>
								</div>
							</div>
							<div class="mt-3">
								<label
									class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1"
									>Notes</label
								>
								<textarea
									v-model="form.notes"
									rows="2"
									placeholder="Additional notes..."
									class="w-full px-3 py-2 text-sm bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-2 focus:ring-[#D4AF37] resize-none"
								></textarea>
							</div>
						</div>

						<!-- Items Section -->
						<div class="mb-5">
							<h3
								class="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3"
							>
								Items
							</h3>

							<!-- Item Search with Barcode Support -->
							<div class="relative mb-3">
								<div class="flex gap-2">
									<div class="relative flex-1">
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
											/>
										</svg>
										<input
											ref="itemSearchInput"
											v-model="itemSearch"
											type="text"
											placeholder="Search by SKU, barcode, or name..."
											@input="searchItems"
											@keydown.enter="handleItemBarcodeScan"
											class="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:ring-2 focus:ring-[#D4AF37]"
										/>
										<div
											v-if="isScanningBarcode"
											class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-green-500 text-xs"
										>
											<span class="animate-pulse">●</span> Scanning...
										</div>
									</div>
									<button
										@click="toggleBarcodeScanner"
										class="px-3 py-2.5 bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/20 transition"
										title="Toggle Barcode Scanner"
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
												d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h2M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
											/>
										</svg>
									</button>
								</div>

								<!-- Search Results Dropdown -->
								<div
									v-if="itemResults.length > 0"
									class="absolute z-20 w-full mt-1 bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg shadow-lg max-h-48 overflow-y-auto"
								>
									<button
										v-for="item in itemResults"
										:key="item.item_code"
										type="button"
										@click="addItem(item)"
										class="w-full px-4 py-2.5 text-left text-sm hover:bg-gray-50 dark:hover:bg-warm-dark-800 transition border-b border-gray-100 dark:border-warm-border last:border-0"
									>
										<div class="flex items-center justify-between">
											<div>
												<span
													class="font-medium text-gray-900 dark:text-white"
													>{{ item.item_name }}</span
												>
												<span class="text-gray-500 text-xs ml-2"
													>SKU: {{ item.item_code }}</span
												>
											</div>
											<span class="text-[#D4AF37] font-bold"
												>${{ formatPrice(item.price) }}</span
											>
										</div>
										<div v-if="item.barcode" class="text-xs text-gray-400">
											Barcode: {{ item.barcode }}
										</div>
									</button>
								</div>
							</div>

							<!-- Items Table -->
							<div
								v-if="selectedItems.length > 0"
								class="overflow-hidden rounded-lg border border-gray-200 dark:border-warm-border"
							>
								<table class="w-full text-sm">
									<thead class="bg-gray-50 dark:bg-warm-dark-900">
										<tr>
											<th
												class="px-3 py-2 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase"
											>
												SKU
											</th>
											<th
												class="px-3 py-2 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase"
											>
												Item
											</th>
											<th
												class="px-2 py-2 text-center text-xs font-bold text-gray-500 dark:text-gray-400 uppercase w-16"
											>
												Qty
											</th>
											<th
												class="px-3 py-2 text-right text-xs font-bold text-gray-500 dark:text-gray-400 uppercase w-20"
											>
												Price
											</th>
											<th
												class="px-3 py-2 text-right text-xs font-bold text-gray-500 dark:text-gray-400 uppercase w-20"
											>
												Amount
											</th>
											<th
												class="px-2 py-2 text-center text-xs font-bold text-gray-500 dark:text-gray-400 uppercase w-10"
											></th>
										</tr>
									</thead>
									<tbody class="divide-y divide-gray-200 dark:divide-gray-700">
										<tr
											v-for="(item, index) in selectedItems"
											:key="item.item_code"
											class="bg-white dark:bg-[#1a1c23] hover:bg-gray-50 dark:hover:bg-warm-dark-800"
										>
											<td
												class="px-3 py-2 text-gray-900 dark:text-white font-mono text-xs"
											>
												{{ item.item_code }}
											</td>
											<td class="px-3 py-2">
												<div
													class="text-gray-900 dark:text-white text-xs truncate max-w-[150px]"
												>
													{{ item.item_name }}
												</div>
												<div
													v-if="item.serial_no"
													class="text-xs text-gray-500"
												>
													SN: {{ item.serial_no }}
												</div>
											</td>
											<td class="px-2 py-2 text-center">
												<input
													v-model.number="item.qty"
													type="number"
													min="1"
													@change="calculateTotals"
													class="w-14 px-2 py-1 text-center bg-gray-50 dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded text-sm text-gray-900 dark:text-gray-100 focus:ring-1 focus:ring-[#D4AF37]"
												/>
											</td>
											<td
												class="px-3 py-2 text-right text-gray-900 dark:text-white text-xs"
											>
												${{ formatPrice(item.price) }}
											</td>
											<td
												class="px-3 py-2 text-right font-medium text-[#D4AF37] text-sm"
											>
												${{ formatPrice(item.price * item.qty) }}
											</td>
											<td class="px-2 py-2 text-center">
												<button
													@click="removeItem(index)"
													class="text-red-500 hover:text-red-600 p-1 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition"
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
															d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
														/>
													</svg>
												</button>
											</td>
										</tr>
									</tbody>
								</table>
							</div>

							<!-- Quick Add Item Buttons -->
							<div v-if="selectedItems.length > 0" class="mt-3 flex gap-2">
								<button
									@click="
										itemSearch = ''
										$refs.itemSearchInput?.focus()
									"
									class="px-3 py-2 text-xs font-medium text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/10 transition flex items-center gap-1"
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
											d="M12 4v16m8-8H4"
										/>
									</svg>
									Add Item
								</button>
								<button
									@click="showSerialInput = !showSerialInput"
									class="px-3 py-2 text-xs font-medium text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-warm-border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition flex items-center gap-1"
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
											d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
										/>
									</svg>
									Serial Numbers
								</button>
							</div>
						</div>

						<!-- Serial Numbers Input Panel -->
						<Transition name="slide-down">
							<div
								v-if="showSerialInput"
								class="mb-5 p-3 bg-gray-100 dark:bg-warm-dark-900 rounded-lg border border-gray-200 dark:border-warm-border"
							>
								<h4
									class="text-xs font-bold text-gray-700 dark:text-gray-300 mb-2"
								>
									Serial Numbers
								</h4>
								<div
									v-for="(item, idx) in selectedItems.filter(
										(i) => i.has_serial
									)"
									:key="item.item_code"
									class="mb-2"
								>
									<label class="text-xs text-gray-500"
										>{{ item.item_name }} (x{{ item.qty }})</label
									>
									<textarea
										v-model="item.serial_numbers"
										rows="2"
										:placeholder="`Enter ${item.qty} serial numbers (one per line)`"
										class="w-full px-3 py-2 text-xs bg-white dark:bg-warm-dark-900 border border-gray-200 dark:border-warm-border rounded-lg focus:ring-1 focus:ring-[#D4AF37] resize-none"
									></textarea>
								</div>
								<p
									v-if="!selectedItems.some((i) => i.has_serial)"
									class="text-xs text-gray-500"
								>
									No items with serial numbers selected.
								</p>
							</div>
						</Transition>

						<!-- Summary Card -->
						<div
							class="p-4 bg-gradient-to-br from-gray-900 to-gray-800 dark:from-black dark:to-gray-900 rounded-2xl text-white"
						>
							<h4 class="text-sm font-bold mb-3 flex items-center gap-2">
								<svg
									class="w-4 h-4 text-[#D4AF37]"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
									/>
								</svg>
								Payment Summary
							</h4>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between items-center">
									<span class="text-gray-400">Subtotal</span>
									<span class="font-medium">${{ formatPrice(subtotal) }}</span>
								</div>
								<!-- Tax Breakdown -->
								<div class="pl-2 border-l-2 border-gray-700">
									<div class="flex justify-between items-center text-xs">
										<span class="text-gray-500">Taxable Amount</span>
										<span class="text-gray-400"
											>${{ formatPrice(subtotal) }}</span
										>
									</div>
									<div class="flex justify-between items-center text-xs">
										<span class="text-gray-500">Tax Rate</span>
										<span class="text-gray-400">{{ form.taxRate }}%</span>
									</div>
									<div class="flex justify-between items-center text-xs">
										<span class="text-gray-500">Tax Amount</span>
										<span class="text-gray-400"
											>${{ formatPrice(taxAmount) }}</span
										>
									</div>
								</div>
								<div
									class="flex justify-between items-center py-2 border-t border-gray-700"
								>
									<span class="text-gray-300">Total</span>
									<span class="font-bold text-lg text-[#D4AF37]"
										>${{ formatPrice(totalAmount) }}</span
									>
								</div>
								<div class="flex justify-between items-center">
									<span class="text-gray-400"
										>Deposit ({{ depositPercent }}%)</span
									>
									<span class="font-medium text-green-400"
										>${{ formatPrice(form.deposit) }}</span
									>
								</div>
								<div
									class="flex justify-between items-center py-2 border-t border-gray-700"
								>
									<span class="text-gray-300">Balance Due</span>
									<span class="font-bold text-lg"
										>${{ formatPrice(remainingBalance) }}</span
									>
								</div>
								<!-- Payment Schedule Preview -->
								<div
									v-if="numberOfPayments > 0"
									class="pt-2 border-t border-gray-700/50"
								>
									<div class="text-xs text-gray-400 mb-2">
										Payment Schedule ({{ paymentFrequencyText }}):
									</div>
									<div
										class="grid grid-cols-2 gap-1 text-xs max-h-24 overflow-y-auto"
									>
										<div
											v-for="n in numberOfPayments"
											:key="n"
											class="flex justify-between bg-gray-800/50 rounded px-2 py-1"
										>
											<span class="text-gray-400">{{
												getPaymentDate(n)
											}}</span>
											<span class="text-gray-300"
												>${{ formatPrice(getPaymentAmount(n)) }}</span
											>
										</div>
									</div>
									<div
										class="flex justify-between items-center mt-2 pt-2 border-t border-gray-700/50 text-xs"
									>
										<span class="text-gray-500"
											>{{ numberOfPayments }} payments</span
										>
										<span class="font-medium text-gray-400"
											>${{ formatPrice(periodicPaymentAmount) }} each</span
										>
									</div>
								</div>
							</div>
						</div>

						<!-- Terms Agreement -->
						<label
							class="flex items-start gap-3 cursor-pointer p-3 mt-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/30 rounded-lg"
						>
							<input
								v-model="form.agreedToTerms"
								type="checkbox"
								class="mt-0.5 w-4 h-4 text-[#D4AF37] border-gray-300 rounded focus:ring-[#D4AF37]"
							/>
							<span class="text-xs text-gray-700 dark:text-gray-300">
								<span class="font-bold">Terms Agreement:</span> I confirm the
								customer has agreed to the layaway terms including the payment
								schedule ({{ paymentFrequencyText }} for {{ form.durationWeeks }}
								{{ form.paymentSchedule === 'Monthly' ? 'months' : 'weeks' }}),
								cancellation policy, and that all items will be reserved until full
								payment is received.
							</span>
						</label>
					</div>
				</div>

				<!-- Footer -->
				<div
					class="flex items-center justify-between px-6 py-4 border-t border-gray-100 dark:border-warm-border/50 bg-gray-50 dark:bg-warm-dark-700 rounded-b-3xl"
				>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						<span v-if="selectedItems.length"
							>{{ selectedItems.length }} items selected</span
						>
					</div>
					<div class="flex items-center gap-3">
						<button
							@click="close"
							class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-warm-border rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition"
						>
							Cancel
						</button>
						<button
							@click="createLayaway"
							:disabled="submitting || !canSubmit"
							class="px-6 py-2 bg-[#D4AF37] text-black rounded-xl text-sm font-bold hover:bg-[#c9a432] disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
						>
							<svg
								v-if="submitting"
								class="w-4 h-4 animate-spin"
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
							{{ submitting ? 'Processing...' : 'Proceed to Payment' }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</component>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch, nextTick } from 'vue'
import { createResource, createDocumentResource } from 'frappe-ui'
import { useSessionStore } from '@/stores/session.js'
import { useCartStore } from '@/stores/cart.js'
import { useRoute } from 'vue-router'
import IDScannerPanel from './IDScannerPanel.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	inlineMode: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'created', 'proceedToPayment'])
const session = useSessionStore()
const cartStore = useCartStore()
const route = useRoute()

// UI State
const submitting = ref(false)
const isNewCustomerMode = ref(false)
const showIdScanner = ref(false)
const showSerialInput = ref(false)
const isScanningBarcode = ref(false)
const hasNominee = ref(false)
const showCustomerDropdown = ref(false)
const storeTaxDetails = ref(null)

// Search State
const customerSearch = ref('')
const itemSearch = ref('')
const customerResults = ref([])
const itemResults = ref([])

// Selected Data
const selectedCustomer = ref(null)
const selectedItems = ref([])

// Refs
const itemSearchInput = ref(null)

// ID Scanner Data
const idScan = ref({
	type: '',
	number: '',
	name: '',
	address: '',
	dob: '',
})

// New Customer Form
const newCustomer = ref({
	name: '',
	phone: '',
	email: '',
	type: 'Individual',
	address: '',
	city: '',
	state: '',
	zip: '',
})

// Nominee Form
const nominee = ref({
	name: '',
	relationship: '',
	phone: '',
	email: '',
})

// Handle initialization from cart
watch(
	() => props.show,
	(newVal) => {
		if (newVal) {
			if (cartStore.items && cartStore.items.length > 0) {
				selectedItems.value = cartStore.items.map((item) => ({
					item_code: item.item_code,
					item_name: item.item_name,
					qty: item.qty,
					price: item.amount,
					has_serial: item.has_serial || false,
					serial_numbers: '',
				}))
			}

			// Try to set customer from cart if selected
			if (cartStore.customer) {
				selectedCustomer.value = cartStore.customer
				isNewCustomerMode.value = false
				autoFillCustomerFromCart(cartStore.customer)
			}

			// Auto-apply 10% deposit and fetch tax details
			nextTick(() => {
				form.value.deposit = minDeposit.value
				fetchStoreTaxDetails()
			})
		} else {
			// Reset logic... but we already have a close method for reset
		}
	},
	{ immediate: true }
)

// Handle inline mode initialization (Layaway page with ?action=new&customer=...)
watch(
	() => route.query,
	(query) => {
		if (!props.inlineMode) return
		if (query.action === 'new' && cartStore.customer) {
			selectedCustomer.value = cartStore.customer
			isNewCustomerMode.value = false
			autoFillCustomerFromCart(cartStore.customer)
			nextTick(() => {
				form.value.deposit = minDeposit.value
				fetchStoreTaxDetails()
			})
		}
	},
	{ immediate: true }
)

async function autoFillCustomerFromCart(cust) {
	if (!cust) return

	selectedCustomer.value = cust
	customerSearch.value = cust.display_name || cust.customer_name || cust.name
	isNewCustomerMode.value = false

	form.value.phone = cust.mobile_no || ''
	form.value.email = cust.email_id || ''

	try {
		const customerName = cust.name || cust.customer_name
		const result = await customerDetailsResource.submit({ customer_name: customerName })
		const details = result?.message ?? result
		if (details) {
			form.value.phone = details.mobile_no || form.value.phone
			form.value.email = details.email_id || form.value.email
			form.value.address = details.address || ''
			form.value.city = details.city || ''
			form.value.state = details.state || ''
			form.value.zip = details.zip || ''
			form.value.country = details.country || ''

			if (details.nominee_name) {
				hasNominee.value = true
				nominee.value.name = details.nominee_name || ''
				nominee.value.relationship = details.nominee_relationship || ''
				nominee.value.phone = details.nominee_phone || ''
				nominee.value.email = ''
			}
		}
	} catch (e) {
		if ('address' in cust && cust.address) form.value.address = cust.address
		if ('city' in cust && cust.city) form.value.city = cust.city
		if ('state' in cust && cust.state) form.value.state = cust.state
		if ('zip' in cust && cust.zip) form.value.zip = cust.zip
		else if ('pincode' in cust && cust.pincode) form.value.zip = cust.pincode
		if ('country' in cust && cust.country) form.value.country = cust.country
	}
}

// Helper to get today's date
const getTodayDate = () => {
	const today = new Date()
	return today.toISOString().split('T')[0]
}

// Main Form
const form = ref({
	phone: '',
	email: '',
	startDate: getTodayDate(),
	status: 'Active',
	paymentSchedule: 'Monthly',
	durationWeeks: 3,
	deposit: 0,
	taxRate: 0,
	notes: '',
	agreedToTerms: false,
	address: '',
	city: '',
	state: '',
	zip: '',
	country: '',
	idType: '',
	idNumber: '',
})

// Computed Properties
const paymentFrequencyText = computed(() => {
	const schedule = form.value.paymentSchedule
	switch (schedule) {
		case 'Weekly':
			return 'Weekly'
		case 'Bi-Weekly':
			return 'Bi-Weekly'
		case 'Monthly':
			return 'Monthly'
		default:
			return 'Weekly'
	}
})

const subtotal = computed(() => {
	return selectedItems.value.reduce((sum, item) => sum + (item.price * item.qty || 0), 0)
})

const taxAmount = computed(() => {
	return subtotal.value * (form.value.taxRate / 100)
})

const totalAmount = computed(() => {
	return subtotal.value + taxAmount.value
})

const remainingBalance = computed(() => {
	return Math.max(0, totalAmount.value - (form.value.deposit || 0))
})

const minDeposit = computed(() => {
	return Math.ceil(totalAmount.value * 0.1)
})

const numberOfPayments = computed(() => {
	const val = form.value.durationWeeks
	const schedule = form.value.paymentSchedule
	switch (schedule) {
		case 'Weekly':
			return val
		case 'Bi-Weekly':
			return Math.ceil(val / 2)
		case 'Monthly':
			return val // In monthly mode, durationWeeks is used as durationMonths
		default:
			return val
	}
})

const periodicPaymentAmount = computed(() => {
	if (numberOfPayments.value <= 0) return 0
	return remainingBalance.value / numberOfPayments.value
})

// Deposit percentage
const depositPercent = computed(() => {
	if (totalAmount.value <= 0) return 0
	return ((form.value.deposit / totalAmount.value) * 100).toFixed(1)
})

// Helper functions for payment schedule
function getPaymentDate(paymentNumber) {
	const startDate = new Date(form.value.startDate)
	const schedule = form.value.paymentSchedule
	switch (schedule) {
		case 'Weekly':
			startDate.setDate(startDate.getDate() + paymentNumber * 7)
			break
		case 'Bi-Weekly':
			startDate.setDate(startDate.getDate() + paymentNumber * 14)
			break
		case 'Monthly':
			startDate.setMonth(startDate.getMonth() + paymentNumber)
			break
	}
	return startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function getPaymentAmount(paymentNumber) {
	const amount = periodicPaymentAmount.value
	const remaining = remainingBalance.value - (paymentNumber - 1) * amount
	return Math.min(amount, Math.max(0, remaining))
}

const canSubmit = computed(() => {
	const hasCustomer = isNewCustomerMode.value
		? newCustomer.value.name && newCustomer.value.phone
		: selectedCustomer.value

	// Validate duration is a valid option for the selected schedule
	const validMonthlyDurations = [1, 2, 3, 6, 9, 12]
	const validWeeklyDurations = [2, 4, 6, 8, 10, 12]
	const duration = form.value.durationWeeks
	const validDuration =
		form.value.paymentSchedule === 'Monthly'
			? validMonthlyDurations.includes(duration)
			: validWeeklyDurations.includes(duration)

	return (
		hasCustomer &&
		selectedItems.value.length > 0 &&
		form.value.deposit >= minDeposit.value &&
		form.value.deposit < totalAmount.value &&
		validDuration &&
		form.value.startDate &&
		form.value.agreedToTerms
	)
})

watch(
	() => form.value.paymentSchedule,
	(newVal) => {
		if (newVal === 'Monthly') {
			form.value.durationWeeks = 3 // 3 months default
		} else {
			form.value.durationWeeks = 4 // 4 weeks default
		}
	},
	{ immediate: true }
)

// Watchers
// Resources
const searchCustomersResource = createResource({
	url: 'zevar_core.api.customer.search_customers',
	auto: false,
})

const searchItemsResource = createResource({
	url: 'zevar_core.api.catalog.get_pos_items',
	auto: false,
})

const createCustomerResource = createResource({
	url: 'frappe.client.insert',
	auto: false,
})

const customerDetailsResource = createResource({
	url: 'zevar_core.api.customer.get_customer_details',
	auto: false,
})

const createLayawayResource = createResource({
	url: 'zevar_core.api.layaway.create_layaway',
	auto: false,
})

const storeTaxResource = createResource({
	url: 'zevar_core.api.tax.get_tax_details_by_warehouse',
	auto: false,
})

// Functions
function formatPrice(price) {
	if (price == null) return '0.00'
	return Number(price).toLocaleString('en-US', {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	})
}

async function fetchStoreTaxDetails() {
	if (!session.currentWarehouse) return
	try {
		const result = await storeTaxResource.submit({
			warehouse: session.currentWarehouse,
		})
		const details = result?.message ?? result
		if (details && details.county_tax_rate) {
			storeTaxDetails.value = details
			form.value.taxRate = details.county_tax_rate
		}
	} catch (error) {
		console.error('Failed to fetch store tax details:', error)
	}
}

function unwrapResponse(result) {
	return result?.message ?? result
}

let customerSearchTimer
async function searchCustomers() {
	if (!customerSearch.value || customerSearch.value.length < 2) {
		customerResults.value = []
		return
	}
	clearTimeout(customerSearchTimer)
	customerSearchTimer = setTimeout(async () => {
		try {
			const customers = await searchCustomersResource.submit({
				query: customerSearch.value,
			})
			const list = customers || []
			customerResults.value = list.map((c) => ({
				...c,
				name: c.name || c.customer_name,
				customer_name: c.display_name || c.customer_name,
			}))
		} catch (error) {
			console.error('Customer search failed:', error)
		}
	}, 300)
}

async function selectCustomer(customer) {
	await autoFillCustomerFromCart(customer)
	showCustomerDropdown.value = false
}

let itemSearchTimer
async function searchItems() {
	if (!itemSearch.value || itemSearch.value.length < 2) {
		itemResults.value = []
		return
	}
	clearTimeout(itemSearchTimer)
	itemSearchTimer = setTimeout(async () => {
		try {
			const result = unwrapResponse(
				await searchItemsResource.submit({
					search_term: itemSearch.value,
					page_length: 20,
					warehouse: session.currentWarehouse || undefined,
				})
			)
			itemResults.value = (Array.isArray(result) ? result : []).map((item) => ({
				item_code: item.item_code,
				item_name: item.item_name,
				price: item.price || item.standard_rate || 0,
				barcode: item.barcode || null,
				has_serial: item.has_serial_no || item.serial_no || false,
				qty: 1,
				serial_numbers: '',
			}))
		} catch (error) {
			console.error('Item search failed:', error)
		}
	}, 300)
}

function addItem(item) {
	const existing = selectedItems.value.find((i) => i.item_code === item.item_code)
	if (existing) {
		existing.qty += 1
	} else {
		selectedItems.value.push({
			...item,
			qty: 1,
			serial_numbers: '',
		})
	}
	form.value.deposit = Math.ceil(totalAmount.value * 0.1)
	itemSearch.value = ''
	itemResults.value = []
}

function removeItem(index) {
	selectedItems.value.splice(index, 1)
	if (selectedItems.value.length > 0) {
		form.value.deposit = Math.ceil(totalAmount.value * 0.1)
	} else {
		form.value.deposit = 0
	}
}

// Watch duration to update deposit if changed significantly?
// Actually 10% should be dynamic but let user override.
watch([subtotal, () => form.value.taxRate], () => {
	if (form.value.deposit === 0 || form.value.deposit < minDeposit.value) {
		form.value.deposit = minDeposit.value
	}
})

function calculateTotals() {
	// Triggered by qty change - computed properties auto-update
}

// Barcode Scanner Functions
function toggleBarcodeScanner() {
	isScanningBarcode.value = !isScanningBarcode.value
	if (isScanningBarcode.value) {
		focusBarcodeScanner()
	}
}

function focusBarcodeScanner() {
	nextTick(() => {
		itemSearchInput.value?.focus()
	})
}

function handleItemBarcodeScan(event) {
	if (isScanningBarcode.value) {
		const barcode = event.target.value
		if (barcode.length >= 8) {
			searchItems()
		}
	}
}

// ID Scanner Functions
function applyIdData() {
	if (isNewCustomerMode.value) {
		newCustomer.value.name = idScan.value.name
		newCustomer.value.address = idScan.value.address
	} else {
		form.value.address = idScan.value.address
	}
	form.value.idNumber = idScan.value.number
	form.value.idType = idScan.value.type
	showIdScanner.value = false
}

// Create Customer
async function createNewCustomer() {
	try {
		const result = await createCustomerResource.submit({
			doc: {
				doctype: 'Customer',
				customer_name: newCustomer.value.name,
				customer_type: newCustomer.value.type,
				mobile_no: newCustomer.value.phone,
				email_id: newCustomer.value.email,
				address_line1: newCustomer.value.address,
				city: newCustomer.value.city,
				state: newCustomer.value.state,
				country: newCustomer.value.country || 'United States',
				pincode: newCustomer.value.zip,
			},
		})
		return result?.name || result?.message?.name
	} catch (error) {
		console.error('Failed to create customer:', error)
		throw error
	}
}

async function createLayaway() {
	if (!canSubmit.value) return

	submitting.value = true

	try {
		let customerName = selectedCustomer.value?.name

		// Create new customer if in new customer mode
		if (isNewCustomerMode.value) {
			customerName = await createNewCustomer()
		}

		// Duration months logic
		const durationMonths =
			form.value.paymentSchedule === 'Monthly'
				? form.value.durationWeeks // Actually months in this mode
				: Math.max(1, Math.round(form.value.durationWeeks / 4))

		// Prepare items
		const items = selectedItems.value.map((item) => ({
			item_code: item.item_code,
			item_name: item.item_name,
			qty: item.qty,
			rate: item.price,
		}))

		// Prepare notes with additional info
		let notes = form.value.notes || ''
		if (form.value.address) {
			notes += `\n\nAddress: ${form.value.address}`
			if (form.value.city) notes += `, ${form.value.city}`
			if (form.value.state) notes += `, ${form.value.state}`
			if (form.value.zip) notes += ` ${form.value.zip}`
		}
		if (form.value.idType && form.value.idNumber) {
			notes += `\n\nID: ${form.value.idType} - ${form.value.idNumber}`
		}
		if (hasNominee.value && nominee.value.name) {
			notes += `\n\nNominee: ${nominee.value.name} (${nominee.value.relationship || 'N/A'})`
			if (nominee.value.phone) notes += ` - ${nominee.value.phone}`
		}
		const payload = {
			customer: customerName,
			items: JSON.stringify(items),
			deposit_amount: form.value.deposit,
			duration_months: durationMonths,
			warehouse: session.currentWarehouse || undefined,
			store_location: session.currentStoreLocation || undefined,
			notes: notes.trim(),
			terms_accepted: form.value.agreedToTerms ? 1 : 0,
			customer_contact: isNewCustomerMode.value
				? newCustomer.value.phone
				: form.value.phone || selectedCustomer.value?.mobile_no,
			customer_email: isNewCustomerMode.value
				? newCustomer.value.email
				: form.value.email || selectedCustomer.value?.email_id,
		}

		emit('proceedToPayment', payload)
		// Do not clear cart or close yet, Layaway.vue will handle it
	} catch (error) {
		console.error('Failed to prepare layaway payload:', error)
	} finally {
		submitting.value = false
	}
}

function close() {
	customerSearch.value = ''
	itemSearch.value = ''
	selectedCustomer.value = null
	selectedItems.value = []
	customerResults.value = []
	itemResults.value = []
	isNewCustomerMode.value = false
	showIdScanner.value = false
	showSerialInput.value = false
	hasNominee.value = false
	isScanningBarcode.value = false

	newCustomer.value = {
		name: '',
		phone: '',
		email: '',
		type: 'Individual',
		address: '',
		city: '',
		state: '',
		zip: '',
	}

	nominee.value = {
		name: '',
		relationship: '',
		phone: '',
		email: '',
	}

	idScan.value = {
		type: '',
		number: '',
		name: '',
		address: '',
		dob: '',
	}

	form.value = {
		phone: '',
		email: '',
		startDate: getTodayDate(),
		status: 'Active',
		paymentSchedule: 'Weekly',
		durationWeeks: 3,
		deposit: 0,
		taxRate: 0,
		notes: '',
		agreedToTerms: false,
		address: '',
		city: '',
		state: '',
		zip: '',
		country: '',
		idType: '',
		idNumber: '',
	}

	emit('close')
}

// Barcode scanner keyboard listener
onMounted(() => {
	document.addEventListener('keydown', handleBarcodeKeyPress)
})

onBeforeUnmount(() => {
	document.removeEventListener('keydown', handleBarcodeKeyPress)
})

let barcodeBuffer = ''
let barcodeTimeout = null

function handleBarcodeKeyPress(e) {
	if (!props.show || !isScanningBarcode.value) return

	// Barcode scanners send keystrokes rapidly followed by Enter
	if (e.key === 'Enter') {
		if (barcodeBuffer.length > 0) {
			itemSearch.value = barcodeBuffer
			searchItems()
			barcodeBuffer = ''
		}
		return
	}

	// Collect characters
	if (e.key.length === 1) {
		barcodeBuffer += e.key

		// Clear buffer after 100ms of no input (not a barcode scanner)
		clearTimeout(barcodeTimeout)
		barcodeTimeout = setTimeout(() => {
			barcodeBuffer = ''
		}, 100)
	}
}

watch(
	() => props.show,
	(isOpen) => {
		if (isOpen) {
			showCustomerDropdown.value = false
		}
	}
)
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

.slide-down-enter-active,
.slide-down-leave-active {
	transition: all 0.3s ease;
	overflow: hidden;
}
.slide-down-enter-from,
.slide-down-leave-to {
	max-height: 0;
	opacity: 0;
}
.slide-down-enter-to,
.slide-down-leave-from {
	max-height: 500px;
	opacity: 1;
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
	width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-track {
	background: transparent;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
	background: #d1d5db;
	border-radius: 3px;
}
.dark .overflow-y-auto::-webkit-scrollbar-thumb {
	background: #4b5563;
}
</style>
