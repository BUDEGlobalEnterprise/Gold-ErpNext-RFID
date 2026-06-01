<template>
	<Teleport to="body">
		<Transition name="fade">
			<div
				v-if="show"
				class="fixed inset-0 z-[250] flex items-center justify-center p-4"
			>
				<!-- Backdrop -->
				<div
					@click="handleCancel"
					class="absolute inset-0 bg-gray-900/65 backdrop-blur-sm"
				></div>

				<!-- Dialog Container -->
				<div
					class="relative bg-white dark:bg-[#1a1c23] rounded-2xl shadow-2xl w-full max-w-2xl h-[680px] overflow-hidden flex flex-col border border-transparent dark:border-warm-border transform transition-all duration-300"
				>
					<!-- Header -->
					<div
						class="p-6 pb-4 border-b border-gray-100 dark:border-warm-border flex items-center justify-between flex-shrink-0"
					>
						<div>
							<h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
								<span class="w-2 h-5 bg-[#D4AF37] rounded-sm inline-block"></span>
								{{ isEdit ? 'Edit Customer Profile' : 'Create New Customer' }}
							</h3>
							<p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ isEdit ? 'Update customer details, addresses, and sizes' : 'Add a comprehensive customer profile with custom sizes' }}</p>
						</div>
						<button
							@click="handleCancel"
							class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
						>
							<svg
								class="w-5 h-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
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
						class="flex border-b border-gray-100 dark:border-warm-border px-6 flex-shrink-0 bg-gray-50/50 dark:bg-warm-dark-900/30"
					>
						<button
							v-for="tab in tabs"
							:key="tab.key"
							type="button"
							@click="activeTab = tab.key"
							class="px-4 py-3.5 text-sm font-semibold transition-colors relative"
							:class="
								activeTab === tab.key
									? 'text-[#D4AF37] dark:text-[#D4AF37]'
									: 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
							"
						>
							{{ tab.label }}
							<div
								v-if="activeTab === tab.key"
								class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#D4AF37] rounded-full"
							></div>
						</button>
					</div>

					<!-- Form Content - Scrollable with CONSTANT/FIXED HEIGHT to prevent modal jumping -->
					<div class="flex-1 overflow-y-auto p-6 space-y-5 h-[420px] custom-scrollbar">
												<!-- Tab 1: Contact Details -->
						<!-- Loading State for Edit Mode -->
						<div v-if="loadingEditData" class="flex items-center justify-center py-20">
							<div class="flex flex-col items-center gap-3">
								<div class="animate-spin rounded-full h-8 w-8 border-2 border-gray-200 border-t-[#D4AF37]"></div>
								<span class="text-xs text-gray-400">Loading customer data...</span>
							</div>
						</div>
						<template v-else>
						<div v-if="activeTab === 'contact'" class="space-y-4">
							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
									>
										Contact type <span class="text-red-500">*</span>
									</label>
									<select
										v-model="newCustomer.contact_type"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									>
										<option value="Individual">Individual</option>
										<option value="Company">Company</option>
									</select>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Language</label
									>
									<select
										v-model="newCustomer.language"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
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

							<div class="grid grid-cols-1">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Name <span class="text-red-500">*</span></label
									>
									<input
										v-model="newCustomer.name"
										type="text"
										placeholder="Full name"
										:disabled="isEdit"
										required
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Email</label
									>
									<input
										v-model="newCustomer.email"
										type="email"
										placeholder="email@example.com"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Phone <span class="text-red-500">*</span></label
									>
									<div class="flex">
										<select
											v-model="newCustomer.phone_country"
											class="px-2 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-r-0 border-gray-200 dark:border-warm-border rounded-l-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
										>
											<option
												v-for="c in usPhoneCodes"
												:key="c.flag"
												:value="c.code"
											>
												{{ c.flag }} {{ c.code }}
											</option>
										</select>
										<input
											v-model="newCustomer.phone"
											type="tel"
											placeholder="(555) 123-4567"
											required
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-r-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
										/>
									</div>
								</div>
							</div>

							<div class="grid grid-cols-3 gap-3">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Street number</label
									>
									<input
										v-model="newCustomer.street_number"
										type="text"
										placeholder="123"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Street</label
									>
									<input
										v-model="newCustomer.street"
										type="text"
										placeholder="Main St"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>City</label
									>
									<input
										v-model="newCustomer.city"
										type="text"
										placeholder="New York"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-3 gap-3">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Postcode</label
									>
									<input
										v-model="newCustomer.pincode"
										type="text"
										placeholder="10001"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>State/Region</label
									>
									<select
										v-model="newCustomer.state"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
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
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Country</label
									>
									<select
										v-model="newCustomer.country"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
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
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Bank account number</label
									>
									<input
										v-model="newCustomer.bank_account"
										type="text"
										placeholder="Account number"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>SWIFT/BIC code</label
									>
									<input
										v-model="newCustomer.swift_bic"
										type="text"
										placeholder="SWIFT code"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Bank name</label
									>
									<input
										v-model="newCustomer.bank_name"
										type="text"
										placeholder="Bank name"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Phone 2</label
									>
									<input
										v-model="newCustomer.phone2"
										type="tel"
										placeholder="Secondary phone"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Client number</label
									>
									<input
										v-model="newCustomer.client_number"
										type="text"
										placeholder="Client ID"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Birth date</label
									>
									<input
										v-model="newCustomer.birth_date"
										type="date"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Marriage date</label
									>
									<input
										v-model="newCustomer.marriage_date"
										type="date"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Partner name</label
									>
									<input
										v-model="newCustomer.partner_name"
										type="text"
										placeholder="Partner/spouse name"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Partner phone</label
									>
									<input
										v-model="newCustomer.partner_phone"
										type="tel"
										placeholder="Partner phone"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Partner email</label
									>
									<input
										v-model="newCustomer.partner_email"
										type="email"
										placeholder="Partner email"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Discount (%)</label
									>
									<input
										v-model.number="newCustomer.discount"
										type="number"
										min="0"
										max="100"
										placeholder="0"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Gender</label
									>
									<select
										v-model="newCustomer.gender"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									>
										<option value="">--------</option>
										<option value="Male">Male</option>
										<option value="Female">Female</option>
										<option value="Other">Other</option>
									</select>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Profession</label
									>
									<input
										v-model="newCustomer.profession"
										type="text"
										placeholder="Profession"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Works at</label
									>
									<input
										v-model="newCustomer.works_at"
										type="text"
										placeholder="Company name"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Assigned to</label
									>
									<input
										v-model="newCustomer.assigned_to"
										type="text"
										placeholder="Sales person"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div>
								<label
									class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
									>Tags</label
								>
								<input
									v-model="newCustomer.tags"
									type="text"
									placeholder="VIP, Wholesale, etc."
									class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
								/>
								<p class="text-[10px] text-gray-400 mt-1">
									A comma-separated list of tags.
								</p>
							</div>

							<div>
								<label
									class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
									>Internal notes</label
								>
								<textarea
									v-model="newCustomer.internal_notes"
									rows="3"
									placeholder="Add internal notes about this customer..."
									class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 resize-none transition-shadow"
								></textarea>
							</div>

							<div class="grid grid-cols-2 gap-4 pt-2">
								<label
									class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-[#0F1115] border border-gray-100 dark:border-warm-border/50 rounded-xl cursor-pointer hover:bg-gray-100/50 dark:hover:bg-warm-dark-800/30 transition-colors"
								>
									<input
										v-model="newCustomer.accepts_marketing"
										type="checkbox"
										class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
									/>
									<div class="cursor-pointer">
										<span
											class="text-sm font-semibold text-gray-700 dark:text-gray-300 block"
											>Marketing</span
										>
										<span class="text-[10px] text-gray-400">Accepts email marketing</span>
									</div>
								</label>
								<label
									class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-[#0F1115] border border-gray-100 dark:border-warm-border/50 rounded-xl cursor-pointer hover:bg-gray-100/50 dark:hover:bg-warm-dark-800/30 transition-colors"
								>
									<input
										v-model="newCustomer.tax_exempt"
										type="checkbox"
										class="w-4 h-4 rounded border-gray-300 text-[#D4AF37] focus:ring-[#D4AF37] cursor-pointer"
									/>
									<div class="cursor-pointer">
										<span
											class="text-sm font-semibold text-gray-700 dark:text-gray-300 block"
											>Tax Exempt</span
										>
										<span class="text-[10px] text-gray-400">Exempt from sales tax</span>
									</div>
								</label>
							</div>
						</div>

						<!-- Tab 3: Shipping Address -->
						<div v-if="activeTab === 'shipping'" class="space-y-4">
							<div class="flex items-center gap-3 mb-3 p-3 bg-blue-50/50 dark:bg-blue-900/10 rounded-xl border border-blue-100/30 dark:border-blue-900/20">
								<label class="flex items-center gap-2 cursor-pointer">
									<input
										v-model="newCustomer.same_as_billing"
										type="checkbox"
										class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
									/>
									<span
										class="text-sm font-semibold text-gray-700 dark:text-gray-300"
										>Shipping address is same as billing address</span
									>
								</label>
							</div>

							<div v-if="!newCustomer.same_as_billing" class="space-y-4 transition-all duration-300">
								<div class="grid grid-cols-2 gap-4">
									<div>
										<label
											class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
											>Street number</label
										>
										<input
											v-model="newCustomer.ship_street_number"
											type="text"
											placeholder="123"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
										/>
									</div>
									<div>
										<label
											class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
											>Street</label
										>
										<input
											v-model="newCustomer.ship_street"
											type="text"
											placeholder="Main St"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
										/>
									</div>
								</div>

								<div class="grid grid-cols-3 gap-3">
									<div>
										<label
											class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
											>City</label
										>
										<input
											v-model="newCustomer.ship_city"
											type="text"
											placeholder="City"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
										/>
									</div>
									<div>
										<label
											class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
											>Postcode</label
										>
										<input
											v-model="newCustomer.ship_pincode"
											type="text"
											placeholder="10001"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
										/>
									</div>
									<div>
										<label
											class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
											>State/Region</label
										>
										<select
											v-model="newCustomer.ship_state"
											class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
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
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Country</label
									>
									<select
										v-model="newCustomer.ship_country"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									>
										<option value="United States">United States</option>
										<option value="Canada">Canada</option>
										<option value="Mexico">Mexico</option>
									</select>
								</div>
							</div>
							<div v-else class="flex flex-col items-center justify-center py-12 text-center text-gray-400 space-y-2">
								<svg class="w-12 h-12 text-gray-300 dark:text-warm-dark-700" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<p class="text-sm font-medium">Shipping Address Synchronized</p>
								<p class="text-xs text-gray-500/80 max-w-sm">
									We will automatically copy and use the customer's billing address for all shipments.
								</p>
							</div>
						</div>

						<!-- Tab 4: Sizes -->
						<div v-if="activeTab === 'sizes'" class="space-y-4">
							<div class="p-3 bg-amber-50/50 dark:bg-amber-900/10 border border-amber-100/30 dark:border-amber-900/20 rounded-xl mb-4">
								<p class="text-xs text-amber-800 dark:text-amber-400 font-medium">
									💡 Recording standard jewelry sizes enables personalized shopping recommendations and faster repair creation.
								</p>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Ring left size</label
									>
									<input
										v-model="newCustomer.ring_left_size"
										type="text"
										placeholder="e.g. 7"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Ring right size</label
									>
									<input
										v-model="newCustomer.ring_right_size"
										type="text"
										placeholder="e.g. 7.5"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Middle left size</label
									>
									<input
										v-model="newCustomer.middle_left_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Middle right size</label
									>
									<input
										v-model="newCustomer.middle_right_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Index left size</label
									>
									<input
										v-model="newCustomer.index_left_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Index right size</label
									>
									<input
										v-model="newCustomer.index_right_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Pink left size</label
									>
									<input
										v-model="newCustomer.pink_left_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Pink right size</label
									>
									<input
										v-model="newCustomer.pink_right_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Thumb left size</label
									>
									<input
										v-model="newCustomer.thumb_left_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Thumb right size</label
									>
									<input
										v-model="newCustomer.thumb_right_size"
										type="text"
										placeholder="Size"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>

							<div class="grid grid-cols-2 gap-4">
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Wrist size</label
									>
									<input
										v-model="newCustomer.wrist_size"
										type="text"
										placeholder="e.g. 7 inches"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
								<div>
									<label
										class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 block"
										>Neck size</label
									>
									<input
										v-model="newCustomer.neck_size"
										type="text"
										placeholder="e.g. 18 inches"
										class="w-full px-3 py-2.5 bg-gray-50 dark:bg-[#0F1115] border border-gray-200 dark:border-warm-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]/50 transition-shadow"
									/>
								</div>
							</div>
						</div>

						</template>
						<!-- Error Message -->
						<div
							v-if="createError"
							class="text-sm text-red-500 bg-red-50 dark:bg-red-900/20 px-4 py-3 rounded-lg border border-red-200 dark:border-red-800/30 flex items-center gap-2"
						>
							<svg class="w-4 h-4 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
							</svg>
							<span>{{ createError }}</span>
						</div>
					</div>

					<!-- Footer -->
					<div
						class="p-6 pt-4 border-t border-gray-100 dark:border-warm-border flex gap-3 flex-shrink-0"
					>
						<button
							type="button"
							@click="handleCancel"
							class="flex-1 py-2.5 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 dark:bg-warm-dark-700 dark:text-gray-300 dark:hover:bg-white/10 transition-colors"
						>
							Close
						</button>
						<button
							type="button"
							@click="submit"
							:disabled="!newCustomer.name || (!isEdit && !newCustomer.phone) || creating"
							class="flex-1 py-2.5 rounded-lg font-bold text-white bg-[#D4AF37] hover:bg-[#b5952f] disabled:opacity-50 transition-colors flex items-center justify-center gap-2 shadow-sm"
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
							<span>{{ creating ? (isEdit ? 'Saving...' : 'Creating...') : (isEdit ? 'Save Changes' : 'Add contact →') }}</span>
						</button>
					</div>
				</div>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { call, toast } from 'frappe-ui'

const props = defineProps({
	show: {
		type: Boolean,
		required: true,
	},
	initialName: {
		type: String,
		default: '',
	},
	isEdit: {
		type: Boolean,
		default: false,
	},
	customerName: {
		type: String,
		default: '',
	},
})

const emit = defineEmits(['close', 'created', 'updated'])

const activeTab = ref('contact')

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

function getDefaultForm() {
	return {
		name: props.initialName || '',
		contact_type: 'Individual',
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
const creating = ref(false)
const createError = ref('')

watch(() => props.initialName, (newVal) => {
	if (newVal && !newCustomer.value.name) {
		newCustomer.value.name = newVal
	}
})

const loadingEditData = ref(false)

watch(() => props.show, async (newVal) => {
	if (newVal) {
		createError.value = ''
		activeTab.value = 'contact'
		if (props.isEdit && props.customerName) {
			loadingEditData.value = true
			try {
				const data = await call('zevar_core.api.customer.get_customer_edit_info', {
					customer_name: props.customerName,
				})
				const d = data?.data || data || {}
				newCustomer.value = {
					name: d.customer_name || d.display_name || '',
					contact_type: d.customer_type || 'Individual',
					email: d.email_id || '',
					phone: d.mobile_no || '',
					phone_country: '+1',
					phone2: d.phone2 || '',
					language: 'en',
					street_number: '',
					street: (d.address || '').replace(/^\d+\s*/, ''),
					city: d.city || '',
					state: d.state || '',
					pincode: d.zip || '',
					country: d.country || 'United States',
					bank_account: '',
					swift_bic: '',
					bank_name: '',
					client_number: '',
					internal_notes: d.internal_notes || '',
					birth_date: d.birth_date || '',
					marriage_date: d.marriage_date || '',
					partner_name: d.partner_name || '',
					partner_phone: d.partner_phone || '',
					partner_email: d.partner_email || '',
					discount: null,
					accepts_marketing: d.accepts_marketing == 1,
					gender: d.gender || '',
					profession: d.profession || '',
					tags: '',
					works_at: '',
					assigned_to: '',
					tax_exempt: d.tax_exempt == 1,
					same_as_billing: true,
					ship_street_number: '',
					ship_street: '',
					ship_city: '',
					ship_pincode: '',
					ship_state: '',
					ship_country: 'United States',
					ring_left_size: d.ring_left_size || '',
					ring_right_size: d.ring_right_size || '',
					middle_left_size: d.middle_left_size || '',
					middle_right_size: d.middle_right_size || '',
					index_left_size: d.index_left_size || '',
					index_right_size: d.index_right_size || '',
					pink_left_size: d.pink_left_size || '',
					pink_right_size: d.pink_right_size || '',
					thumb_left_size: d.thumb_left_size || '',
					thumb_right_size: d.thumb_right_size || '',
					wrist_size: d.wrist_size || '',
					neck_size: d.neck_size || '',
				}
			} catch (e) {
				createError.value = e?.message || 'Failed to load customer data'
			} finally {
				loadingEditData.value = false
			}
		} else {
			newCustomer.value = getDefaultForm()
		}
	}
})

function handleCancel() {
	emit('close')
}

async function submit() {
	if (!newCustomer.value.name) {
		toast({
			title: 'Required',
			message: 'Please enter customer name',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}
	if (!newCustomer.value.phone) {
		toast({
			title: 'Required',
			message: 'Please enter phone number',
			icon: 'alert-circle',
			intent: 'error',
		})
		return
	}

	creating.value = true
	createError.value = ''

	try {
		const billingAddress =
			[newCustomer.value.street_number, newCustomer.value.street]
				.filter(Boolean)
				.join(' ') || null

		const apiMethod = props.isEdit
			? 'zevar_core.api.customer.update_customer'
			: 'zevar_core.api.customer.quick_create_customer'

		const response = await call(apiMethod, {
			customer_name: newCustomer.value.name,
			customer_type: newCustomer.value.contact_type,
			mobile_no: newCustomer.value.phone || null,
			email_id: newCustomer.value.email || null,
			gender: newCustomer.value.gender || null,
			birth_date: newCustomer.value.birth_date || null,
			profession: newCustomer.value.profession || null,
			partner_name: newCustomer.value.partner_name || null,
			partner_phone: newCustomer.value.partner_phone || null,
			partner_email: newCustomer.value.partner_email || null,
			marriage_date: newCustomer.value.marriage_date || null,
			tags: newCustomer.value.tags || null,
			internal_notes: newCustomer.value.internal_notes || null,
			phone2: newCustomer.value.phone2 || null,
			accepts_marketing: newCustomer.value.accepts_marketing ? 1 : 0,
			tax_exempt: newCustomer.value.tax_exempt ? 1 : 0,
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
			address_line1: billingAddress,
			address_line2: null,
			city: newCustomer.value.city || null,
			state: newCustomer.value.state || null,
			pincode: newCustomer.value.pincode || null,
			country: newCustomer.value.country || null,
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
		})

		const data = response?.data || response

		if (data && data.success) {
			const customerData = {
				...data,
				name: data.customer_name,
			}
			if (props.isEdit) {
				emit('updated', customerData)
			} else {
				emit('created', customerData)
			}
			toast({
				title: 'Success',
				message: props.isEdit ? 'Customer updated successfully' : 'Customer created successfully',
				icon: 'check',
				intent: 'success',
			})
		} else {
			createError.value = data?.message || 'Failed to create customer'
		}
	} catch (e) {
		const errorMsg = e?.response?.data?.message || e?.message || e?.exception || String(e)
		createError.value = errorMsg
		console.error('Customer creation error:', e)
	} finally {
		creating.value = false
	}
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}

/* Custom scrollbar matching premium design */
.custom-scrollbar::-webkit-scrollbar {
	width: 6px;
	height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
	background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
	background: #cbd5e1;
	border-radius: 3px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
	background: #374151;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
	background: #94a3b8;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
	background: #4b5563;
}
</style>
