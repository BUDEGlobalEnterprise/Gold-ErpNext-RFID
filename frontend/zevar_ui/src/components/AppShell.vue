<template>
	<div class="app-shell-root transition-colors duration-300">
		<!-- ===== DESKTOP SIDEBAR (>= lg) ===== -->
		<aside
			ref="sidebarRef"
			class="hidden lg:flex bg-white/40 dark:bg-warm-dark-900/60 backdrop-blur-xl border-r border-gray-200 dark:border-warm-border/50 flex-col z-30 relative"
			:class="isResizing ? 'transition-none' : 'transition-all duration-300'"
			:style="
				isSidebarCollapsed
					? { width: '80px', minWidth: '80px', maxWidth: '80px' }
					: { width: sidebarWidth + 'px', minWidth: '240px', maxWidth: '400px' }
			"
		>
			<!-- Sidebar Header -->
			<div
				class="h-20 flex items-center border-b border-gray-200 dark:border-warm-border/50 transition-all duration-300"
				:class="isSidebarCollapsed ? 'px-4 justify-center' : 'px-4 justify-between'"
			>
				<div
					v-if="!isSidebarCollapsed"
					class="flex items-center gap-2.5 overflow-hidden min-w-0 pr-2"
				>
					<img
						src="/logo.svg"
						alt="Zevar"
						class="w-8 h-8 rounded-lg shadow-[0_0_15px_rgba(212,175,55,0.3)] shrink-0"
					/>
					<h1
						class="premium-title !text-2xl !tracking-tighter whitespace-nowrap !leading-none truncate"
					>
						ZEVAR
					</h1>
				</div>
				<button
					v-if="!isSidebarCollapsed"
					@click="isSidebarCollapsed = true"
					class="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 border border-gray-200 dark:border-warm-border/50 hover:bg-white/10 transition-all text-gray-400 hover:text-white shrink-0"
					aria-label="Collapse sidebar"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.8"
							d="M20 6H10M20 12h-6M20 18H10M9 8l-4 4 4 4"
						/>
					</svg>
				</button>
				<button
					v-else
					@click="isSidebarCollapsed = false"
					class="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 border border-gray-200 dark:border-warm-border/50 hover:bg-white/10 transition-all text-gray-400 hover:text-white shrink-0"
					aria-label="Expand sidebar"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.8"
							d="M4 6h10M4 12h6M4 18h10M15 8l4 4-4 4"
						/>
					</svg>
				</button>
			</div>

			<div class="flex-1 flex flex-col overflow-hidden">
				<nav class="p-4 space-y-6 flex-1 overflow-y-auto custom-scrollbar">
					<template v-for="(section, groupIdx) in sidebarSections" :key="groupIdx">
						<div class="space-y-1">
							<div v-if="!isSidebarCollapsed" class="px-3 mb-2">
								<span
									class="text-[10px] font-black text-gray-500 uppercase tracking-widest opacity-50"
									>{{ section.label }}</span
								>
							</div>
							<div
								v-else
								class="h-px bg-gray-200 dark:bg-warm-border-subtle mx-2 mb-4 opacity-50"
							></div>
							<router-link
								v-for="item in section.items"
								:key="item.to"
								:to="item.to"
								class="flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden"
								:class="
									isNavActive(item.to)
										? 'bg-gradient-to-r from-[#D4AF37]/20 to-transparent text-[#D4AF37]'
										: 'text-gray-600 dark:text-gray-400 hover:text-[#D4AF37] hover:bg-gradient-to-r hover:from-[#D4AF37]/10 hover:to-transparent'
								"
							>
								<div
									class="relative z-10 flex items-center gap-4 w-full"
									:class="{ 'justify-center': isSidebarCollapsed }"
								>
									<svg
										class="w-5 h-5 transition-colors shrink-0"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											:d="item.icon"
										/>
									</svg>
									<span
										v-if="!isSidebarCollapsed"
										class="font-medium tracking-wide text-sm whitespace-nowrap"
										>{{ item.label }}</span
									>
									<div
										v-if="isSidebarCollapsed"
										class="absolute left-14 px-3 py-1 bg-gray-900 text-white text-[10px] font-bold rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 shadow-xl"
									>
										{{ item.label }}
									</div>
								</div>
							</router-link>
						</div>
					</template>
				</nav>
			</div>

			<!-- Resize Handle -->
			<div
				v-if="!isSidebarCollapsed"
				class="absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-[#D4AF37]/30 transition-colors z-40"
				@mousedown="startResize"
			></div>
		</aside>

		<!-- ===== CONTENT COLUMN ===== -->
		<div class="app-shell-content-col">
			<!-- Header -->
			<header
				class="h-14 md:h-16 lg:h-20 bg-white/70 dark:bg-warm-dark-950/80 backdrop-blur-md border-b border-gray-200 dark:border-warm-border/50 flex items-center justify-between px-3 sm:px-4 lg:px-6 z-20 sticky top-0 shadow-sm transition-colors duration-300 shrink-0"
			>
				<!-- Mobile Left: Hamburger + Logo + Store -->
				<div class="flex lg:hidden items-center gap-2 flex-1 min-w-0">
					<button
						@click="isMobileDrawerOpen = true"
						class="p-1 sm:p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0 touch-target"
						aria-label="Open menu"
					>
						<svg
							class="w-6 h-6 text-gray-600 dark:text-gray-300"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 6h16M4 12h16M4 18h16"
							/>
						</svg>
					</button>
					<img src="/logo.svg" alt="Zevar" class="w-7 h-7 rounded-lg shrink-0" />
					<div class="relative ml-1 min-w-0 flex-1">
						<select
							v-model="session.currentWarehouse"
							@change="session.setWarehouse($event.target.value)"
							class="h-8 w-full bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border/50 pl-2 pr-6 rounded-lg text-xs font-bold text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] cursor-pointer appearance-none truncate"
						>
							<option :value="null" disabled>Store...</option>
							<option v-for="wh in warehouses.data" :key="wh.name" :value="wh.name">
								{{
									wh.name.replace('Zevar US Stores - ', '').replace(' - ZUS', '')
								}}
							</option>
						</select>
					</div>
				</div>

				<!-- Desktop Left: Store + Search -->
				<div class="hidden lg:flex items-center gap-4 flex-1 max-w-3xl">
					<div class="relative group">
						<select
							v-model="session.currentWarehouse"
							@change="session.setWarehouse($event.target.value)"
							class="h-11 bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border/50 pl-4 pr-10 rounded-lg text-sm font-bold text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] cursor-pointer min-w-[200px] shadow-sm outline-none"
						>
							<option :value="null" disabled>Select Store Location</option>
							<option v-for="wh in warehouses.data" :key="wh.name" :value="wh.name">
								{{ wh.name }}
							</option>
						</select>
					</div>
					<div class="relative flex-1">
						<svg
							class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
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
							type="text"
							v-model="ui.searchQuery"
							placeholder="Search collection..."
							class="h-11 w-full bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:ring-2 focus:ring-[#D4AF37] text-sm font-medium pl-11 transition-all"
						/>
					</div>
				</div>

				<!-- Right side: rates + user + cart -->
				<div class="flex items-center gap-2 sm:gap-3 lg:ml-8">
					<!-- Live Rates (desktop only) -->
					<div
						class="hidden xl:flex items-center h-11 bg-gray-50/50 dark:bg-warm-dark-900/50 border border-gray-200 dark:border-warm-border rounded-lg shadow-sm max-w-2xl overflow-x-auto custom-scrollbar-hide"
					>
						<div
							class="flex items-center gap-2 border-r border-gray-200 dark:border-warm-border pr-3 pl-4 bg-gray-100/50 dark:bg-warm-dark-700 h-full sticky left-0 z-10 backdrop-blur-md"
						>
							<span class="relative flex h-2 w-2"
								><span
									class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"
								></span
								><span
									class="relative inline-flex rounded-full h-2 w-2 bg-green-600"
								></span
							></span>
							<span
								class="text-[10px] font-black uppercase tracking-widest text-gray-600 dark:text-gray-400"
								>LIVE</span
							>
						</div>
						<div
							class="flex items-center divide-x divide-gray-200 dark:divide-gray-700 h-full"
						>
							<div
								v-for="[key, rate] in sortedRates"
								:key="key"
								class="flex items-center gap-2 px-4 h-full shrink-0"
							>
								<span
									class="text-[11px] text-gray-500 font-bold uppercase whitespace-nowrap"
									>{{ formatShortLabel(key) }}</span
								>
								<span
									class="text-base font-mono font-black text-[#D4AF37] whitespace-nowrap"
									>${{ rate }}</span
								>
							</div>
						</div>
					</div>

					<!-- User menu -->
					<div class="relative" ref="userMenuRef">
						<button
							@click.stop="isUserMenuOpen = !isUserMenuOpen"
							class="flex items-center gap-2 p-1.5 pr-3 rounded-full hover:bg-gray-100 dark:hover:bg-warm-dark-700 border border-transparent hover:border-gray-200 dark:border-warm-border"
						>
							<div
								class="w-8 h-8 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] flex items-center justify-center text-[#0F1115] font-bold text-xs"
							>
								{{ session.user?.full_name?.[0]?.toUpperCase() || 'U' }}
							</div>
							<span
								class="text-sm font-semibold hidden sm:block text-gray-700 dark:text-white truncate max-w-[80px]"
								>{{ session.user?.full_name?.split(' ')[0] || 'Guest' }}</span
							>
						</button>
						<!-- Dropdown -->
						<Transition
							enter-active-class="transition duration-200 ease-out"
							enter-from-class="transform scale-95 opacity-0"
							enter-to-class="transform scale-100 opacity-100"
							leave-active-class="transition duration-75 ease-in"
							leave-from-class="transform scale-100 opacity-100"
							leave-to-class="transform scale-95 opacity-0"
						>
							<div
								v-if="isUserMenuOpen"
								class="absolute right-0 mt-2 w-56 bg-white/80 dark:bg-warm-card/80 backdrop-blur-xl rounded-xl shadow-xl border border-gray-100 dark:border-warm-border py-2 z-50"
							>
								<div
									class="px-4 py-3 border-b border-gray-100 dark:border-warm-border"
								>
									<p
										class="text-sm font-bold text-gray-900 dark:text-white truncate"
									>
										{{ session.user?.full_name || 'Guest' }}
									</p>
									<p class="text-xs text-gray-500 truncate mt-0.5">
										{{ session.user?.email }}
									</p>
								</div>
								<div
									class="py-1 border-b border-gray-100 dark:border-warm-border/50"
								>
									<button
										@click.stop="ui.toggleTheme()"
										class="w-full flex items-center justify-between px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors group"
									>
										<div class="flex items-center gap-3">
											<svg
												v-if="ui.isDark"
												class="w-4 h-4 text-[#D4AF37]"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
												/>
											</svg>
											<svg
												v-else
												class="w-4 h-4 text-blue-600"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
												/>
											</svg>
											<span>{{
												ui.isDark ? 'Light Mode' : 'Dark Mode'
											}}</span>
										</div>
										<div
											class="w-8 h-4 bg-gray-200 dark:bg-warm-dark-800 rounded-full relative flex items-center px-0.5 transition-colors group-hover:bg-gray-300 dark:group-hover:bg-warm-dark-600"
										>
											<div
												class="w-3 h-3 bg-white dark:bg-[#D4AF37] rounded-full transition-transform duration-200 shadow-sm"
												:class="
													ui.isDark ? 'translate-x-4' : 'translate-x-0'
												"
											></div>
										</div>
									</button>
								</div>
								<div
									class="py-1 border-b border-gray-100 dark:border-warm-border/50"
								>
									<a
										href="/employee-portal"
										class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors"
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
												d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-10V4m0 10V4m-4 10h4"
											/>
										</svg>
										Employee Portal
									</a>
									<a
										href="/update-password"
										class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-warm-dark-700 transition-colors"
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
												d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-3.586l6.828-6.828A6 6 0 1121 9z"
											/>
										</svg>
										Change Password
									</a>
								</div>
								<div class="py-1">
									<button
										@click.stop="session.logoutResource.submit()"
										class="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-500/10"
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
												d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
											/>
										</svg>
										Sign Out
									</button>
								</div>
							</div>
						</Transition>
					</div>

					<!-- Cart -->
					<button
						v-if="!showPersistentCart"
						@click="isCartOpen = true"
						class="relative p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group shrink-0 touch-target"
					>
						<svg
							class="w-5 h-5 sm:w-6 sm:h-6 text-gray-600 dark:text-gray-300"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
							/>
						</svg>
						<span
							v-if="cartStore.totalItems > 0"
							class="absolute top-0 right-0 h-4 w-4 sm:h-5 sm:w-5 flex items-center justify-center bg-[#D4AF37] text-white text-[9px] sm:text-[10px] font-bold rounded-full shadow-md"
							>{{ cartStore.totalItems }}</span
						>
					</button>
				</div>
			</header>

			<!-- Main content area -->
			<div class="app-shell-main-row">
				<main class="app-shell-main p-3 sm:p-4 lg:p-6 transition-colors duration-300">
					<slot></slot>
				</main>

				<!-- Persistent Cart (desktop only) -->
				<Transition
					enter-active-class="transition-all duration-300 ease-out"
					enter-from-class="!w-0 opacity-0"
					enter-to-class="opacity-100"
					leave-active-class="transition-all duration-200 ease-in"
					leave-from-class="opacity-100"
					leave-to-class="!w-0 opacity-0"
				>
					<div
						v-if="showPersistentCart"
						class="flex flex-col shrink-0 bg-white/40 dark:bg-warm-dark-900/60 backdrop-blur-xl border-l border-gray-200 dark:border-warm-border/50 min-h-0 overflow-hidden relative"
						:class="{ 'transition-all duration-300': !isRightResizing }"
						:style="{ width: rightSidebarWidth + 'px' }"
					>
						<div
							class="absolute top-0 left-0 w-1.5 h-full cursor-col-resize hover:bg-[#D4AF37]/30 transition-colors z-40"
							@mousedown="startRightResize"
						></div>
						<CartSidebar :isOpen="true" :persistent="true" />
					</div>
				</Transition>
			</div>
		</div>

		<!-- Mobile Rate Ticker -->
		<div
			v-if="!isLargeDesktop"
			class="app-shell-ticker bg-white/80 dark:bg-warm-dark-900/80 backdrop-blur-md border-t border-gray-200 dark:border-warm-border/50 h-10 flex items-center shrink-0 shadow-[0_-4px_15px_rgba(0,0,0,0.1)] overflow-x-auto no-scrollbar lg:hidden"
		>
			<div
				class="flex items-center gap-1.5 pr-3 pl-3 border-r border-gray-200 dark:border-warm-border/50 shrink-0 bg-gray-100/50 dark:bg-warm-dark-950/50 h-full"
			>
				<span class="relative flex h-1.5 w-1.5"
					><span
						class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"
					></span
					><span
						class="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-600"
					></span
				></span>
				<span class="text-[8px] font-black uppercase tracking-widest text-gray-500"
					>LIVE</span
				>
			</div>
			<div
				class="flex items-center divide-x divide-gray-200 dark:divide-gray-800 min-w-max h-full"
			>
				<div
					v-for="[key, rate] in sortedRates"
					:key="key"
					class="flex items-center gap-2 px-4 h-full shrink-0"
				>
					<span class="text-[9px] text-gray-500 font-bold uppercase">{{
						formatShortLabel(key)
					}}</span>
					<span class="text-xs font-mono font-black text-[#D4AF37]">${{ rate }}</span>
				</div>
			</div>
		</div>

		<!-- ===== MOBILE BOTTOM NAV (< lg) ===== -->
		<nav
			class="app-shell-bottom-nav lg:hidden bg-white/90 dark:bg-warm-dark-950/90 backdrop-blur-lg border-t border-gray-200 dark:border-warm-border/50 flex items-stretch justify-around safe-area-bottom shrink-0"
		>
			<router-link
				v-for="item in bottomNavItems"
				:key="item.to"
				:to="item.to"
				class="flex flex-col items-center justify-center gap-0.5 py-2 px-3 min-w-0 flex-1 transition-colors"
				:class="
					isNavActive(item.to) ? 'text-[#D4AF37]' : 'text-gray-400 dark:text-gray-600'
				"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						:d="item.icon"
					/>
				</svg>
				<span class="text-[10px] font-semibold truncate">{{ item.label }}</span>
			</router-link>
			<button
				@click="isMobileDrawerOpen = true"
				class="flex flex-col items-center justify-center gap-0.5 py-2 px-3 min-w-0 flex-1 text-gray-400 dark:text-gray-600"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
					/>
				</svg>
				<span class="text-[10px] font-semibold">More</span>
			</button>
		</nav>

		<!-- Cart Sidebar -->
		<CartSidebar :isOpen="isCartOpen" :persistent="false" @close="isCartOpen = false" />

		<!-- Global Checkout -->
		<CheckoutModal
			v-if="ui.layawayPayment.show"
			:show="ui.layawayPayment.show"
			mode="layaway"
			:referenceId="ui.layawayPayment.layawayId"
			:balanceAmount="ui.layawayPayment.balance"
			:draftMode="!!ui.layawayPayment.draftPayload"
			@close="ui.closeLayawayPayment"
			@success="handleGlobalPaymentSuccess"
		/>

		<!-- ===== MOBILE DRAWER OVERLAY ===== -->
		<div
			v-if="isMobileDrawerOpen"
			@click="isMobileDrawerOpen = false"
			class="fixed inset-0 bg-black/50 z-40 lg:hidden"
		></div>

		<!-- ===== MOBILE DRAWER ===== -->
		<aside
			class="fixed inset-y-0 left-0 z-50 w-[85vw] max-w-[320px] bg-white/90 dark:bg-warm-dark-900/90 backdrop-blur-xl shadow-2xl transform transition-transform duration-300 lg:hidden flex flex-col"
			:class="isMobileDrawerOpen ? 'translate-x-0' : '-translate-x-full'"
		>
			<div
				class="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-warm-border/50 shrink-0"
			>
				<div class="flex items-center gap-3">
					<img src="/logo.svg" alt="Zevar POS" class="w-8 h-8 rounded-lg" />
					<span
						class="text-gray-900 dark:text-white font-black text-2xl tracking-tighter leading-none"
						>ZEVAR</span
					>
				</div>
				<button
					@click="isMobileDrawerOpen = false"
					class="text-gray-400 p-2 hover:text-white transition-colors touch-target"
					aria-label="Close menu"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
				class="p-4 space-y-3 border-b border-gray-200 dark:border-warm-border/50 shrink-0"
			>
				<div class="relative">
					<svg
						class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
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
						type="text"
						v-model="ui.searchQuery"
						placeholder="Search..."
						class="h-11 w-full bg-gray-800/50 border border-gray-700 text-gray-200 rounded-lg pl-10 pr-4 focus:ring-2 focus:ring-[#D4AF37] text-sm"
					/>
				</div>
				<div class="relative">
					<select
						v-model="session.currentWarehouse"
						@change="session.setWarehouse($event.target.value)"
						class="h-11 w-full bg-gray-800/50 border border-gray-700 text-gray-200 rounded-lg px-3 focus:ring-2 focus:ring-[#D4AF37] text-sm appearance-none"
					>
						<option :value="null" disabled>Store</option>
						<option v-for="wh in warehouses.data" :key="wh.name" :value="wh.name">
							{{ wh.name }}
						</option>
					</select>
				</div>
			</div>
			<nav class="flex-1 overflow-y-auto p-4 space-y-0.5 custom-scrollbar">
				<template v-for="(section, sIdx) in sidebarSections" :key="sIdx">
					<div class="px-3 pt-3 pb-1">
						<span
							class="text-[9px] font-bold text-gray-400 uppercase tracking-widest"
							>{{ section.label }}</span
						>
					</div>
					<router-link
						v-for="item in section.items"
						:key="item.to"
						@click="isMobileDrawerOpen = false"
						:to="item.to"
						class="flex items-center gap-3 px-4 py-2.5 rounded-xl transition-colors"
						:class="
							isNavActive(item.to)
								? 'bg-gradient-to-r from-[#D4AF37]/20 to-transparent text-[#D4AF37]'
								: 'text-gray-600 dark:text-gray-400 hover:text-[#D4AF37]'
						"
					>
						<svg
							class="w-[18px] h-[18px] shrink-0"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								:d="item.icon"
							/>
						</svg>
						<span class="font-medium text-[13px]">{{ item.label }}</span>
					</router-link>
				</template>
				<div class="mt-4 pt-4 border-t border-gray-200 dark:border-warm-border/50">
					<button
						@click="ui.toggleTheme()"
						class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-600 dark:text-gray-400"
					>
						<span class="text-sm font-medium">{{
							ui.isDark ? 'Light Mode' : 'Dark Mode'
						}}</span>
					</button>
					<button
						@click="session.logoutResource.submit()"
						class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10"
					>
						<span class="text-sm font-medium">Sign Out</span>
					</button>
				</div>
			</nav>
		</aside>
	</div>
</template>

<script setup>
import { useSessionStore } from '@/stores/session.js'
import { useGoldStore } from '@/stores/gold.js'
import { useCartStore } from '@/stores/cart.js'
import { useUIStore } from '@/stores/ui.js'
import { createResource } from 'frappe-ui'
import { onMounted, ref, computed, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useBreakpoint } from '@/composables/useBreakpoint.js'
import { canAccessReports } from '@/utils/permissions.js'
import CartSidebar from '@/components/CartSidebar.vue'
import CheckoutModal from '@/components/CheckoutModal.vue'

const session = useSessionStore()
const goldStore = useGoldStore()
const cartStore = useCartStore()
const ui = useUIStore()
const emit = defineEmits(['layaway-payment-success', 'layaway-created'])
const route = useRoute()
const { isMobile, isLargeDesktop } = useBreakpoint()

const isCartOpen = ref(false)
const isUserMenuOpen = ref(false)
const isMobileDrawerOpen = ref(false)
const isSidebarCollapsed = ref(false)
const isResizing = ref(false)
const isRightResizing = ref(false)
const sidebarRef = ref(null)
const userMenuRef = ref(null)

const savedSidebarWidth = localStorage.getItem('zevar_sidebar_width')
const sidebarWidth = ref(savedSidebarWidth ? parseInt(savedSidebarWidth) : 288)
const savedRightSidebarWidth = localStorage.getItem('zevar_right_sidebar_width')
const rightSidebarWidth = ref(savedRightSidebarWidth ? parseInt(savedRightSidebarWidth) : 360)

watch(sidebarWidth, (v) => localStorage.setItem('zevar_sidebar_width', v.toString()))
watch(rightSidebarWidth, (v) => localStorage.setItem('zevar_right_sidebar_width', v.toString()))

// Bottom nav items (mobile only — 5 most used)
const bottomNavItems = [
	{
		to: '/',
		label: 'Home',
		icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
	},
	{
		to: '/terminal',
		label: 'POS',
		icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z',
	},
	{
		to: '/inventory',
		label: 'Inventory',
		icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
	},
	{
		to: '/customers',
		label: 'Customers',
		icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
	},
]

// Sidebar sections (desktop + drawer)
const sidebarSections = computed(() => {
	const sections = [
		{
			label: 'Operations',
			items: [
				{
					to: '/',
					label: 'Dashboard',
					icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
				},
				{
					to: '/terminal',
					label: 'POS Terminal',
					icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z',
				},
				{
					to: '/inventory',
					label: 'Inventory',
					icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
				},
				{
					to: '/inventory-audit',
					label: 'Audit',
					icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
				},
				{
					to: '/customers',
					label: 'Customers',
					icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
				},
			],
		},
		{
			label: 'Sales',
			items: [
				{
					to: '/transactions',
					label: 'Sales History',
					icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
				},
				{
					to: '/pos-catalogue',
					label: 'Catalogues',
					icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
				},
				{
					to: '/layaway',
					label: 'Layaway',
					icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
				},
			],
		},
		{
			label: 'Services',
			items: [
				{
					to: '/repairs',
					label: 'Repairs',
					icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
				},
				{
					to: '/trade-ins',
					label: 'Trade-Ins',
					icon: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4',
				},
				{
					to: '/appraisals',
					label: 'Appraisals',
					icon: 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z',
				},
			],
		},
		{ label: 'Management', items: [] },
	]
	// Add reports conditionally
	if (canAccessReports()) {
		sections[3].items.push({
			to: '/reports',
			label: 'Reports',
			icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
		})
	}
	sections[3].items.push(
		{
			to: '/contacts',
			label: 'Contacts',
			icon: 'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z',
		},
		{
			to: '/support',
			label: 'Support',
			icon: 'M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z',
		}
	)
	return sections
})

function isNavActive(path) {
	const current = route.path || ''
	if (path === '/') return current === '/'
	return current === path || current.startsWith(path + '/')
}

// Persistent cart logic
const cartEligibleRoutes = ['/terminal', '/inventory', '/pos-catalogue', '/layaway']
const showPersistentCart = computed(() => {
	if (!isLargeDesktop.value) return false
	const path = route.path || ''
	return (
		cartEligibleRoutes.includes(path) ||
		path.startsWith('/pos-catalogue/') ||
		path.startsWith('/catalogues')
	)
})

// Gold rates
const TROY_OZ_GRAMS = 31.1035
const metalPriority = { 'Yellow Gold': 1, Gold: 1, Silver: 2 }
const purityPriority = {
	'22Kt': 100,
	'18Kt': 90,
	'14Kt': 80,
	'10Kt': 70,
	'999 Fine': 60,
	'925 Sterling': 50,
}

const sortedRates = computed(() => {
	if (!goldStore.rates) return []
	return Object.entries(goldStore.rates)
		.filter(
			([key, rate]) =>
				key &&
				key !== 'null' &&
				rate &&
				!key.includes('Platinum') &&
				!key.toLowerCase().includes('24k')
		)
		.sort((a, b) => {
			const [metalA, purityA] = a[0].split('-')
			const [metalB, purityB] = b[0].split('-')
			const mPA = metalPriority[metalA] || 99
			const mPB = metalPriority[metalB] || 99
			if (mPA !== mPB) return mPA - mPB
			const pPA = purityPriority[purityA] || 0
			const pPB = purityPriority[purityB] || 0
			return pPB - pPA
		})
		.map(([key, ratePerGram]) => {
			const perOz = (ratePerGram * TROY_OZ_GRAMS).toFixed(2)
			return [
				key,
				Number(perOz).toLocaleString('en-US', {
					minimumFractionDigits: 2,
					maximumFractionDigits: 2,
				}),
			]
		})
})

function formatShortLabel(key) {
	if (!key || key === 'null') return ''
	if (key.startsWith('Silver-')) {
		const purity = key.split('-')[1] || ''
		return `SILVER ${purity.toUpperCase()}`
	}
	const parts = key.split('-')
	if (parts.length >= 2) return `GOLD ${parts[1].toUpperCase().replace('KT', 'K')}`
	return key.toUpperCase()
}

// Warehouses
const warehouses = createResource({
	url: 'frappe.client.get_list',
	params: {
		doctype: 'Warehouse',
		filters: { is_group: 0, parent_warehouse: ['like', '%Zevar US Stores%'] },
		fields: ['name'],
	},
	auto: true,
	onSuccess(data) {
		if (!data || data.length === 0) warehouseFallback.fetch()
	},
})
const warehouseFallback = createResource({
	url: 'frappe.client.get_list',
	params: {
		doctype: 'Warehouse',
		filters: { is_group: 0 },
		fields: ['name'],
		limit_page_length: 50,
	},
	onSuccess(data) {
		if (data?.length > 0) warehouses.data = data
	},
})

// Resize handlers
let startX = 0,
	startWidth = 0
function startResize(e) {
	isResizing.value = true
	startX = e.clientX
	startWidth = sidebarWidth.value
	document.addEventListener('mousemove', handleResize)
	document.addEventListener('mouseup', stopResize)
	e.preventDefault()
}
function handleResize(e) {
	if (!isResizing.value) return
	sidebarWidth.value = Math.min(Math.max(startWidth + (e.clientX - startX), 240), 400)
}
function stopResize() {
	isResizing.value = false
	document.removeEventListener('mousemove', handleResize)
	document.removeEventListener('mouseup', stopResize)
}
function startRightResize(e) {
	isRightResizing.value = true
	startX = e.clientX
	startWidth = rightSidebarWidth.value
	document.addEventListener('mousemove', handleRightResize)
	document.addEventListener('mouseup', stopRightResize)
	e.preventDefault()
}
function handleRightResize(e) {
	if (!isRightResizing.value) return
	rightSidebarWidth.value = Math.min(Math.max(startWidth - (e.clientX - startX), 300), 800)
}
function stopRightResize() {
	isRightResizing.value = false
	document.removeEventListener('mousemove', handleRightResize)
	document.removeEventListener('mouseup', stopRightResize)
}

function handleDocumentClick(e) {
	if (isUserMenuOpen.value && userMenuRef.value && !userMenuRef.value.contains(e.target))
		isUserMenuOpen.value = false
}

async function handleGlobalPaymentSuccess(result) {
	const draftPayload = ui.layawayPayment.draftPayload
	if (draftPayload) {
		try {
			const res = await fetch('/api/method/zevar_core.api.layaway.create_layaway', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-Frappe-CSRF-Token': window.csrf_token,
				},
				body: JSON.stringify({
					...draftPayload,
					payments: JSON.stringify(result.payments || []),
				}),
			})
			const data = await res.json()
			if (!res.ok || data.exc_type) {
				alert('Layaway creation failed')
				return
			}
			const r = data.message ?? data
			if (r?.success || r?.layaway_id) {
				ui.closeLayawayPayment()
				emit('layaway-created', r)
			}
		} catch (err) {
			alert('Network error')
			ui.closeLayawayPayment()
		}
	} else {
		ui.closeLayawayPayment()
		emit('layaway-payment-success', result)
	}
}

watch(
	() => session.currentWarehouse,
	(wh) => {
		if (wh) cartStore.loadTaxForWarehouse(wh)
	}
)
onMounted(() => {
	goldStore.startPolling()
	if (session.currentWarehouse) cartStore.loadTaxForWarehouse(session.currentWarehouse)
	document.addEventListener('click', handleDocumentClick)
})
onUnmounted(() => {
	document.removeEventListener('mousemove', handleResize)
	document.removeEventListener('mouseup', stopResize)
	document.removeEventListener('mousemove', handleRightResize)
	document.removeEventListener('mouseup', stopRightResize)
	document.removeEventListener('click', handleDocumentClick)
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
	width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
	background: rgba(255, 255, 255, 0.05);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
	background: rgba(255, 255, 255, 0.2);
	border-radius: 10px;
}

.custom-scrollbar-hide::-webkit-scrollbar {
	height: 3px;
}
.custom-scrollbar-hide::-webkit-scrollbar-track {
	background: transparent;
}
.custom-scrollbar-hide::-webkit-scrollbar-thumb {
	background: transparent;
	border-radius: 10px;
}
.custom-scrollbar-hide:hover::-webkit-scrollbar-thumb {
	background: rgba(212, 175, 55, 0.3);
}

/* ===== CSS Grid App Shell ===== */
.app-shell-root {
	display: grid;
	min-height: 100dvh;
	width: 100%;
	/* Mobile: header + content + ticker + bottom nav */
	grid-template-columns: 1fr;
	grid-template-rows: auto 1fr auto auto;
	grid-template-areas:
		'content'
		'content'
		'ticker'
		'bottomnav';
}

/* lg+: sidebar + content, no bottom nav */
@media (min-width: 1024px) {
	.app-shell-root {
		grid-template-columns: auto 1fr;
		grid-template-rows: minmax(0, 1fr) auto;
		grid-template-areas:
			'sidebar content'
			'sidebar ticker';
		height: 100dvh;
		overflow: hidden;
	}
}

/* xl+: no ticker */
@media (min-width: 1280px) {
	.app-shell-root {
		grid-template-rows: 1fr;
		grid-template-areas: 'sidebar content';
	}
}

.app-shell-root > aside:first-child {
	grid-area: sidebar;
}

.app-shell-content-col {
	grid-area: content;
	display: flex;
	flex-direction: column;
	min-width: 0;
	min-height: 0;
}

@media (max-width: 1023px) {
	.app-shell-content-col {
		overflow: visible;
	}
}

@media (min-width: 1024px) {
	.app-shell-content-col {
		overflow: hidden;
	}
}

.app-shell-main-row {
	flex: 1 1 0%;
	display: flex;
	min-height: 0;
	min-width: 0;
}

.app-shell-main {
	flex: 1 1 0%;
	min-width: 0;
	min-height: 0;
	overflow-y: auto;
	overflow-x: hidden;
}

.app-shell-ticker {
	grid-area: ticker;
}

.app-shell-bottom-nav {
	grid-area: bottomnav;
}
</style>
