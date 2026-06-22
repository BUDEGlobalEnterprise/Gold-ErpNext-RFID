<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center justify-between gap-4 mb-4 flex-shrink-0">
				<h2 class="premium-title !text-xl sm:!text-2xl">Settings</h2>
				<button
					@click="refreshAll"
					class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-warm-dark-700"
					title="Refresh"
				>
					<svg
						class="w-4 h-4 text-gray-500"
						:class="{ 'animate-spin': store.loading }"
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
			</div>

			<div class="flex-1 overflow-y-auto">
				<div
					v-if="store.loading && !store.settings"
					class="flex items-center justify-center py-20"
				>
					<div
						class="animate-spin w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full"
					></div>
				</div>

				<div v-else class="space-y-4">
					<div class="flex gap-1 overflow-x-auto pb-2 flex-shrink-0">
						<button
							v-for="tab in tabs"
							:key="tab.key"
							@click="activeTab = tab.key"
							class="px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition"
							:class="
								activeTab === tab.key
									? 'bg-[#D4AF37] text-white'
									: 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-warm-dark-700'
							"
						>
							{{ tab.label }}
						</button>
					</div>

					<div v-if="activeTab === 'pos'">
						<div class="premium-card !p-4 mb-4">
							<div class="flex items-center justify-between mb-3">
								<h3
									class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
								>
									POS Profiles
								</h3>
								<button
									@click="openCreateProfile"
									class="px-3 py-1.5 text-xs font-bold bg-[#D4AF37] text-white rounded-lg hover:bg-[#B8962E] transition"
								>
									+ New Profile
								</button>
							</div>

							<div
								v-if="!store.settings?.pos_profiles?.length"
								class="text-center py-8 text-gray-400 text-sm"
							>
								No POS profiles found
							</div>

							<div v-else class="space-y-2">
								<div
									v-for="profile in store.settings.pos_profiles"
									:key="profile.name"
									class="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-warm-dark-700 hover:border-[#D4AF37]/50 transition cursor-pointer"
									@click="editProfile(profile)"
								>
									<div>
										<div
											class="font-bold text-sm text-gray-900 dark:text-white"
										>
											{{ profile.posa_pos_profile_name || profile.name }}
										</div>
										<div
											class="text-xs text-gray-500 dark:text-gray-400 mt-0.5"
										>
											{{ profile.company }} &middot;
											{{ profile.warehouse || 'No warehouse' }}
										</div>
									</div>
									<div class="flex items-center gap-2">
										<span
											v-if="profile.customer"
											class="text-xs text-gray-400"
											>{{ profile.customer }}</span
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
												d="M9 5l7 7-7 7"
											/>
										</svg>
									</div>
								</div>
							</div>
						</div>
					</div>

					<div v-if="activeTab === 'store'">
						<div class="premium-card !p-4 space-y-4">
							<h3
								class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
							>
								Store Configuration
							</h3>

							<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
								<div>
									<label
										class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
										>Company</label
									>
									<div
										class="px-3 py-2 rounded-lg border border-gray-200 dark:border-warm-dark-700 text-sm bg-gray-50 dark:bg-warm-dark-800 text-gray-700 dark:text-gray-300"
									>
										{{ store.settings?.company || '—' }}
									</div>
								</div>
								<div>
									<label
										class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
										>Default Warehouses</label
									>
									<div class="max-h-40 overflow-y-auto space-y-1">
										<div
											v-for="wh in store.settings?.warehouses?.slice(0, 20)"
											:key="wh.name"
											class="px-3 py-1.5 text-xs rounded border border-gray-100 dark:border-warm-dark-700 text-gray-600 dark:text-gray-400"
										>
											{{ wh.name }}
										</div>
									</div>
								</div>
								<div>
									<label
										class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
										>Price Lists</label
									>
									<div class="space-y-1">
										<div
											v-for="pl in store.settings?.price_lists"
											:key="pl.name"
											class="px-3 py-1.5 text-xs rounded border border-gray-100 dark:border-warm-dark-700 text-gray-600 dark:text-gray-400"
										>
											{{ pl.name }}
											<span v-if="pl.selling" class="text-emerald-500 ml-1"
												>(Selling)</span
											>
											<span v-if="pl.buying" class="text-blue-500 ml-1"
												>(Buying)</span
											>
										</div>
									</div>
								</div>
								<div>
									<label
										class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
										>Cost Centers</label
									>
									<div class="max-h-40 overflow-y-auto space-y-1">
										<div
											v-for="cc in store.settings?.cost_centers?.slice(
												0,
												20
											)"
											:key="cc.name"
											class="px-3 py-1.5 text-xs rounded border border-gray-100 dark:border-warm-dark-700 text-gray-600 dark:text-gray-400"
										>
											{{ cc.name }}
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<div v-if="activeTab === 'payments'">
						<div class="premium-card !p-4 space-y-4">
							<h3
								class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
							>
								Payment Methods
							</h3>
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
								<div
									v-for="mode in store.settings?.modes_of_payment"
									:key="mode.name"
									class="flex items-center justify-between px-3 py-2 rounded-lg border border-gray-200 dark:border-warm-dark-700"
								>
									<span class="text-sm text-gray-800 dark:text-gray-200">{{
										mode.name
									}}</span>
									<span class="text-xs text-gray-400">{{ mode.type }}</span>
								</div>
							</div>
						</div>
					</div>

					<div v-if="activeTab === 'tax'">
						<div class="premium-card !p-4 space-y-4">
							<h3
								class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
							>
								Tax Templates
							</h3>
							<div
								v-if="!store.settings?.tax_templates?.length"
								class="text-center py-6 text-gray-400 text-sm"
							>
								No tax templates configured
							</div>
							<div v-else class="space-y-2">
								<div
									v-for="tax in store.settings.tax_templates"
									:key="tax.name"
									class="px-3 py-2 rounded-lg border border-gray-200 dark:border-warm-dark-700"
								>
									<div
										class="text-sm font-medium text-gray-800 dark:text-gray-200"
									>
										{{ tax.name }}
									</div>
									<div class="text-xs text-gray-400 mt-0.5">
										{{ tax.company }}
									</div>
								</div>
							</div>

							<h3
								class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider pt-4"
							>
								Accounts
							</h3>
							<div class="max-h-60 overflow-y-auto space-y-1">
								<div
									v-for="acc in store.settings?.accounts?.slice(0, 50)"
									:key="acc.name"
									class="flex items-center justify-between px-3 py-1.5 text-xs rounded border border-gray-100 dark:border-warm-dark-700"
								>
									<span class="text-gray-700 dark:text-gray-300">{{
										acc.name
									}}</span>
									<span class="text-gray-400">{{
										acc.account_type || acc.root_type
									}}</span>
								</div>
							</div>
						</div>
					</div>

					<div v-if="activeTab === 'users'">
						<div class="premium-card !p-4 space-y-4">
							<div class="flex items-center justify-between">
								<h3
									class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
								>
									User Management
								</h3>
								<button
									@click="showCreateUser = true"
									class="px-3 py-1.5 text-xs font-bold bg-[#D4AF37] text-white rounded-lg hover:bg-[#B8962E] transition"
								>
									+ New User
								</button>
							</div>

							<div
								v-if="store.usersResource.loading"
								class="flex justify-center py-8"
							>
								<div
									class="animate-spin w-6 h-6 border-2 border-[#D4AF37] border-t-transparent rounded-full"
								></div>
							</div>

							<div v-else class="space-y-2">
								<div
									v-for="user in userList"
									:key="user.name"
									class="flex items-center gap-3 p-3 rounded-lg border border-gray-200 dark:border-warm-dark-700"
								>
									<div
										class="w-8 h-8 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-xs font-bold text-[#D4AF37]"
									>
										{{
											(user.full_name || user.email).charAt(0).toUpperCase()
										}}
									</div>
									<div class="flex-1 min-w-0">
										<div
											class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate"
										>
											{{ user.full_name }}
										</div>
										<div class="text-xs text-gray-400 truncate">
											{{ user.email }}
										</div>
									</div>
									<div class="flex flex-wrap gap-1">
										<span
											v-for="role in user.roles?.slice(0, 3)"
											:key="role"
											class="px-1.5 py-0.5 text-[10px] rounded bg-gray-100 dark:bg-warm-dark-700 text-gray-500 dark:text-gray-400"
										>
											{{ role }}
										</span>
										<span
											v-if="user.roles?.length > 3"
											class="text-[10px] text-gray-400"
											>+{{ user.roles.length - 3 }}</span
										>
									</div>
									<button
										v-if="user.roles?.includes('Sales Manager') || user.roles?.includes('System Manager')"
										@click="openSetPin(user)"
										class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700"
										title="Set Manager PIN"
									>
										<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
										</svg>
									</button>
									<button
										@click="openSetLoginPassword(user)"
										class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700"
										title="Set Login Password"
									>
										<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4v-3.252l7.536-7.536A6 6 0 1121 9z" />
										</svg>
									</button>
									<button
										@click="openEditRoles(user)"
										class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700"
										title="Edit Roles"
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
												d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
											/>
										</svg>
									</button>
								</div>
							</div>
						</div>
					</div>

					<div v-if="activeTab === 'printing'">
						<div class="premium-card !p-4 space-y-4">
							<h3
								class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
							>
								Print Formats
							</h3>
							<div
								v-if="!store.settings?.print_formats?.length"
								class="text-center py-6 text-gray-400 text-sm"
							>
								No print formats found
							</div>
							<div v-else class="space-y-2">
								<div
									v-for="fmt in store.settings.print_formats"
									:key="fmt.name"
									class="flex items-center justify-between px-3 py-2 rounded-lg border border-gray-200 dark:border-warm-dark-700"
								>
									<div>
										<div
											class="text-sm font-medium text-gray-800 dark:text-gray-200"
										>
											{{ fmt.name }}
										</div>
										<div class="text-xs text-gray-400">{{ fmt.doc_type }}</div>
									</div>
									<div class="flex items-center gap-2">
										<span
											v-if="fmt.standard"
											class="px-2 py-0.5 text-[10px] rounded bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400"
											>Standard</span
										>
										<span
											v-else
											class="px-2 py-0.5 text-[10px] rounded bg-[#D4AF37]/10 text-[#D4AF37]"
											>Custom</span
										>
									</div>
								</div>
							</div>
						</div>
					</div>

					<div v-if="activeTab === 'system'">
						<div class="premium-card !p-4 space-y-4">
							<h3
								class="text-sm font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider"
							>
								System Information
							</h3>
							<div v-if="systemInfo" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
								<div
									v-for="(value, key) in systemInfo"
									:key="key"
									class="px-3 py-2 rounded-lg border border-gray-200 dark:border-warm-dark-700"
								>
									<div class="text-xs text-gray-400 mb-0.5">
										{{ formatLabel(key) }}
									</div>
									<div
										class="text-sm font-medium text-gray-800 dark:text-gray-200 break-all"
									>
										{{ Array.isArray(value) ? value.join(', ') : value }}
									</div>
								</div>
							</div>
							<div v-else class="text-center py-6">
								<button
									@click="loadSystem"
									class="px-4 py-2 text-sm bg-[#D4AF37] text-white rounded-lg hover:bg-[#B8962E] transition"
								>
									Load System Info
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div
			v-if="showProfileModal"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showProfileModal = false"
		>
			<div
				class="bg-white dark:bg-warm-dark-800 rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto"
			>
				<div
					class="p-4 border-b border-gray-200 dark:border-warm-dark-700 flex items-center justify-between"
				>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">
						{{ editingProfile ? 'Edit' : 'New' }} POS Profile
					</h3>
					<button
						@click="showProfileModal = false"
						class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700"
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
				<div class="p-4 space-y-3">
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Profile Name</label
						>
						<input
							v-model="profileForm.name"
							type="text"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
							placeholder="Main Terminal"
						/>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Company</label
						>
						<select
							v-model="profileForm.company"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						>
							<option value="">Select company</option>
							<option :value="store.settings?.company">
								{{ store.settings?.company }}
							</option>
						</select>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Warehouse</label
						>
						<select
							v-model="profileForm.warehouse"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						>
							<option value="">Select warehouse</option>
							<option
								v-for="wh in store.settings?.warehouses"
								:key="wh.name"
								:value="wh.name"
							>
								{{ wh.name }}
							</option>
						</select>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Default Customer</label
						>
						<select
							v-model="profileForm.customer"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						>
							<option value="">Select customer</option>
							<option
								v-for="c in store.settings?.customers?.slice(0, 50)"
								:key="c.name"
								:value="c.name"
							>
								{{ c.customer_name }}
							</option>
						</select>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Selling Price List</label
						>
						<select
							v-model="profileForm.selling_price_list"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						>
							<option value="">Select price list</option>
							<option
								v-for="pl in store.settings?.price_lists?.filter((p) => p.selling)"
								:key="pl.name"
								:value="pl.name"
							>
								{{ pl.name }}
							</option>
						</select>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Cost Center</label
						>
						<select
							v-model="profileForm.cost_center"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						>
							<option value="">Select cost center</option>
							<option
								v-for="cc in store.settings?.cost_centers"
								:key="cc.name"
								:value="cc.name"
							>
								{{ cc.name }}
							</option>
						</select>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Payment Methods</label
						>
						<div class="space-y-1 max-h-32 overflow-y-auto">
							<label
								v-for="mode in store.settings?.modes_of_payment"
								:key="mode.name"
								class="flex items-center gap-2 px-2 py-1 text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
							>
								<input
									type="checkbox"
									:value="mode.name"
									v-model="profileForm.payments"
									class="rounded border-gray-300"
								/>
								{{ mode.name }}
							</label>
						</div>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Applicable Users</label
						>
						<div class="space-y-1 max-h-32 overflow-y-auto border border-gray-200 dark:border-warm-dark-700 rounded-lg p-2">
							<div v-if="!store.settings?.users?.length" class="text-xs text-gray-400 p-1">No users found</div>
							<label
								v-for="u in store.settings?.users"
								:key="u.email"
								class="flex items-center gap-2 px-2 py-1 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-50 dark:hover:bg-warm-dark-700 rounded"
							>
								<input
									type="checkbox"
									:value="u.email"
									v-model="profileForm.users"
									class="rounded border-gray-300"
								/>
								{{ u.full_name || u.email }}
							</label>
						</div>
					</div>
				</div>
				<div
					class="p-4 border-t border-gray-200 dark:border-warm-dark-700 flex items-center justify-between"
				>
					<button
						v-if="editingProfile"
						@click="handleDeleteProfile"
						class="px-3 py-2 text-xs font-bold text-red-500 hover:text-red-700 transition"
					>
						Delete
					</button>
					<span v-else></span>
					<div class="flex gap-2">
						<button
							@click="showProfileModal = false"
							class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-700"
						>
							Cancel
						</button>
						<button
							@click="handleSaveProfile"
							:disabled="savingProfile"
							class="px-4 py-2 text-sm font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
						>
							{{ savingProfile ? 'Saving...' : 'Save' }}
						</button>
					</div>
				</div>
			</div>
		</div>

		<div
			v-if="showRoleModal"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showRoleModal = false"
		>
			<div
				class="bg-white dark:bg-warm-dark-800 rounded-xl shadow-2xl w-full max-w-md mx-4 max-h-[80vh] overflow-y-auto"
			>
				<div
					class="p-4 border-b border-gray-200 dark:border-warm-dark-700 flex items-center justify-between"
				>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Edit Roles</h3>
					<button
						@click="showRoleModal = false"
						class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700"
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
				<div class="p-4">
					<div class="mb-3 text-sm text-gray-600 dark:text-gray-400">
						{{ roleEditUser?.full_name }} ({{ roleEditUser?.email }})
					</div>
					<div class="space-y-1 max-h-60 overflow-y-auto">
						<label
							v-for="role in store.settings?.roles"
							:key="role.name"
							class="flex items-center gap-2 px-2 py-1.5 text-sm text-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-50 dark:hover:bg-warm-dark-700 rounded"
						>
							<input
								type="checkbox"
								:value="role.name"
								v-model="roleEditList"
								class="rounded border-gray-300"
							/>
							{{ role.name }}
						</label>
					</div>
				</div>
				<div
					class="p-4 border-t border-gray-200 dark:border-warm-dark-700 flex justify-end gap-2"
				>
					<button
						@click="showRoleModal = false"
						class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 text-gray-700 dark:text-gray-300"
					>
						Cancel
					</button>
					<button
						@click="handleSaveRoles"
						:disabled="savingRoles"
						class="px-4 py-2 text-sm font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
					>
						{{ savingRoles ? 'Saving...' : 'Save Roles' }}
					</button>
				</div>
			</div>
		</div>

		<div
			v-if="showPinModal"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showPinModal = false"
		>
			<div class="bg-white dark:bg-warm-dark-800 rounded-xl shadow-2xl w-full max-w-sm mx-4">
				<div class="p-4 border-b border-gray-200 dark:border-warm-dark-700 flex items-center justify-between">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Set Manager PIN</h3>
					<button
						@click="showPinModal = false"
						class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700"
					>
						<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
				<div class="p-4 space-y-4">
					<div class="text-sm text-gray-600 dark:text-gray-400">
						Setting PIN for: <span class="font-bold text-gray-900 dark:text-gray-100">{{ pinEditUser?.full_name || pinEditUser?.email }}</span>
					</div>
					<div>
						<label class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1">New PIN (min 4 digits)</label>
						<input
							v-model="newPin"
							type="password"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
							placeholder="Enter new PIN"
							maxlength="10"
						/>
					</div>
				</div>
				<div class="p-4 border-t border-gray-200 dark:border-warm-dark-700 flex justify-end gap-2">
					<button
						@click="showPinModal = false"
						class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 text-gray-700 dark:text-gray-300"
					>
						Cancel
					</button>
					<button
						@click="handleSavePin"
						:disabled="savingPin || newPin.length < 4"
						class="px-4 py-2 text-sm font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
					>
						{{ savingPin ? 'Saving...' : 'Set PIN' }}
					</button>
				</div>
			</div>
		</div>
		<div
			v-if="showLoginPasswordModal"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showLoginPasswordModal = false"
		>
			<div class="bg-white dark:bg-warm-dark-800 rounded-xl shadow-2xl w-full max-w-sm mx-4">
				<div class="p-4 border-b border-gray-200 dark:border-warm-dark-700 flex items-center justify-between">
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">Set Login Password</h3>
					<button @click="showLoginPasswordModal = false" class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700">
						<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
				<div class="p-4 space-y-4">
					<div class="text-sm text-gray-600 dark:text-gray-400">
						Setting Login Password for: <span class="font-bold text-gray-900 dark:text-gray-100">{{ pwdEditUser?.full_name || pwdEditUser?.email }}</span>
					</div>
					<div>
						<label class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1">New Password</label>
						<input v-model="newLoginPassword" type="password" class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white" placeholder="Enter new password" />
					</div>
				</div>
				<div class="p-4 border-t border-gray-200 dark:border-warm-dark-700 flex justify-end gap-2">
					<button @click="showLoginPasswordModal = false" class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 text-gray-700 dark:text-gray-300">Cancel</button>
					<button @click="handleSaveLoginPassword" :disabled="savingLoginPassword || !newLoginPassword" class="px-4 py-2 text-sm font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50">
						{{ savingLoginPassword ? 'Saving...' : 'Set Password' }}
					</button>
				</div>
			</div>
		</div>

		<div
			v-if="showCreateUser"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
			@click.self="showCreateUser = false"
		>
			<div class="bg-white dark:bg-warm-dark-800 rounded-xl shadow-2xl w-full max-w-md mx-4">
				<div
					class="p-4 border-b border-gray-200 dark:border-warm-dark-700 flex items-center justify-between"
				>
					<h3 class="text-lg font-bold text-gray-900 dark:text-white">New User</h3>
					<button
						@click="showCreateUser = false"
						class="p-1 rounded hover:bg-gray-100 dark:hover:bg-warm-dark-700"
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
				<div class="p-4 space-y-3">
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Email</label
						>
						<input
							v-model="newUser.email"
							type="email"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						/>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>First Name</label
						>
						<input
							v-model="newUser.first_name"
							type="text"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						/>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Last Name</label
						>
						<input
							v-model="newUser.last_name"
							type="text"
							class="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white"
						/>
					</div>
					<div>
						<label
							class="block text-xs font-bold text-gray-500 dark:text-gray-400 mb-1"
							>Roles</label
						>
						<div class="space-y-1 max-h-32 overflow-y-auto">
							<label
								v-for="role in store.settings?.roles"
								:key="role.name"
								class="flex items-center gap-2 px-2 py-1 text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
							>
								<input
									type="checkbox"
									:value="role.name"
									v-model="newUser.roles"
									class="rounded border-gray-300"
								/>
								{{ role.name }}
							</label>
						</div>
					</div>
				</div>
				<div
					class="p-4 border-t border-gray-200 dark:border-warm-dark-700 flex justify-end gap-2"
				>
					<button
						@click="showCreateUser = false"
						class="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-warm-dark-600 text-gray-700 dark:text-gray-300"
					>
						Cancel
					</button>
					<button
						@click="handleCreateUser"
						:disabled="savingUser"
						class="px-4 py-2 text-sm font-bold rounded-lg bg-[#D4AF37] text-white hover:bg-[#B8962E] transition disabled:opacity-50"
					>
						{{ savingUser ? 'Creating...' : 'Create User' }}
					</button>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import { useSettingsStore } from '../stores/settings'

const store = useSettingsStore()

const activeTab = ref('pos')
const systemInfo = ref(null)

const showProfileModal = ref(false)
const editingProfile = ref(null)
const savingProfile = ref(false)
const profileForm = ref({
	name: '',
	company: '',
	warehouse: '',
	customer: '',
	selling_price_list: '',
	cost_center: '',
	payments: [],
})

const showRoleModal = ref(false)
const roleEditUser = ref(null)
const roleEditList = ref([])
const savingRoles = ref(false)

const showCreateUser = ref(false)
const savingUser = ref(false)
const newUser = ref({ email: '', first_name: '', last_name: '', password: '', roles: [] })

const showPinModal = ref(false)
const pinEditUser = ref(null)
const newPin = ref('')
const savingPin = ref(false)

const showLoginPasswordModal = ref(false)
const pwdEditUser = ref(null)
const newLoginPassword = ref('')
const savingLoginPassword = ref(false)

const userList = ref([])

const tabs = [
	{ key: 'pos', label: 'POS Profiles' },
	{ key: 'store', label: 'Store' },
	{ key: 'payments', label: 'Payments' },
	{ key: 'tax', label: 'Tax & Accounts' },
	{ key: 'users', label: 'Users' },
	{ key: 'printing', label: 'Printing' },
	{ key: 'system', label: 'System' },
]

function refreshAll() {
	store.loadSettings()
	if (activeTab.value === 'users') loadUsers()
}

function formatLabel(key) {
	return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function openCreateProfile() {
	editingProfile.value = null
	profileForm.value = {
		name: '',
		company: store.settings?.company || '',
		warehouse: '',
		customer: '',
		selling_price_list: '',
		cost_center: '',
		payments: [],
		users: [],
	}
	showProfileModal.value = true
}

function editProfile(profile) {
	editingProfile.value = profile
	profileForm.value = {
		name: profile.posa_pos_profile_name || '',
		company: profile.company || '',
		warehouse: profile.warehouse || '',
		customer: profile.customer || '',
		selling_price_list: profile.selling_price_list || '',
		cost_center: profile.cost_center || '',
		payments: [],
		users: [],
	}
	store.loadPosProfile(profile.name).then((data) => {
		if (data?.profile?.payment_methods) {
			profileForm.value.payments = data.profile.payment_methods
				.filter((p) => p.default)
				.map((p) => p.mode_of_payment)
		}
		if (data?.profile?.users) {
			profileForm.value.users = data.profile.users
		}
	})
	showProfileModal.value = true
}

async function handleSaveProfile() {
	savingProfile.value = true
	try {
		const paymentsJson = JSON.stringify(
			profileForm.value.payments.map((mode) => ({ mode_of_payment: mode, default: 1 }))
		)
		const usersJson = JSON.stringify(profileForm.value.users)
		
		if (editingProfile.value) {
			await store.updatePosProfile(editingProfile.value.name, {
				warehouse: profileForm.value.warehouse,
				customer: profileForm.value.customer,
				selling_price_list: profileForm.value.selling_price_list,
				cost_center: profileForm.value.cost_center,
				posa_pos_profile_name: profileForm.value.name,
				payments_json: paymentsJson,
				users_json: usersJson,
			})
		} else {
			await store.createPosProfile({
				company: profileForm.value.company,
				warehouse: profileForm.value.warehouse,
				customer: profileForm.value.customer || undefined,
				selling_price_list: profileForm.value.selling_price_list || undefined,
				cost_center: profileForm.value.cost_center || undefined,
				name_override: profileForm.value.name || undefined,
				payments_json: paymentsJson,
				users_json: usersJson,
			})
		}
		showProfileModal.value = false
		await store.loadSettings()
	} finally {
		savingProfile.value = false
	}
}

async function handleDeleteProfile() {
	if (!editingProfile.value) return
	if (!confirm('Delete this POS profile?')) return
	savingProfile.value = true
	try {
		await store.deletePosProfile(editingProfile.value.name)
		showProfileModal.value = false
		await store.loadSettings()
	} finally {
		savingProfile.value = false
	}
}

async function loadUsers() {
	const data = await store.loadUsers()
	if (data?.users) userList.value = data.users
}

function openEditRoles(user) {
	roleEditUser.value = user
	roleEditList.value = [...(user.roles || [])]
	showRoleModal.value = true
}

async function handleSaveRoles() {
	savingRoles.value = true
	try {
		await store.updateUserRoles(roleEditUser.value.email, roleEditList.value)
		showRoleModal.value = false
		await loadUsers()
	} finally {
		savingRoles.value = false
	}
}

function openSetPin(user) {
	pinEditUser.value = user
	newPin.value = ''
	showPinModal.value = true
}

async function handleSavePin() {
	if (newPin.value.length < 4) return
	savingPin.value = true
	try {
		await store.setManagerPin(newPin.value, pinEditUser.value.name || pinEditUser.value.email)
		showPinModal.value = false
		newPin.value = ''
	} finally {
		savingPin.value = false
	}
}

function openSetLoginPassword(user) {
	pwdEditUser.value = user
	newLoginPassword.value = ''
	showLoginPasswordModal.value = true
}

async function handleSaveLoginPassword() {
	if (!newLoginPassword.value) return
	savingLoginPassword.value = true
	try {
		await store.setUserPassword(pwdEditUser.value.email, newLoginPassword.value)
		showLoginPasswordModal.value = false
		newLoginPassword.value = ''
	} finally {
		savingLoginPassword.value = false
	}
}

async function handleCreateUser() {
	savingUser.value = true
	try {
		await store.createUser({
			email: newUser.value.email,
			first_name: newUser.value.first_name,
			last_name: newUser.value.last_name || undefined,
			password: newUser.value.password || undefined,
			roles_json: JSON.stringify(newUser.value.roles),
		})
		showCreateUser.value = false
		newUser.value = { email: '', first_name: '', last_name: '', password: '', roles: [] }
		await loadUsers()
	} finally {
		savingUser.value = false
	}
}

async function loadSystem() {
	const data = await store.loadSystemInfo()
	if (data?.system_info) systemInfo.value = data.system_info
}

onMounted(() => {
	store.loadSettings()
	loadUsers()
})
</script>
