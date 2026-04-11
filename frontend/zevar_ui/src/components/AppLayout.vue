<template>
	<div
		class="flex h-screen w-screen bg-[#F8F9FA] dark:bg-[#1e1e24] overflow-hidden transition-colors duration-300"
		style="font-family: 'Inter', sans-serif"
	>
		<!-- DESKTOP SIDEBAR -->
		<aside
			ref="sidebarRef"
			class="hidden lg:flex bg-white dark:bg-[#15161a] border-r border-gray-200 dark:border-white/5 flex-col shadow-2xl z-30 relative"
			:class="isResizing ? 'transition-none' : 'transition-all duration-300'"
			:style="
				isSidebarCollapsed
					? { width: '80px', minWidth: '80px', maxWidth: '80px' }
					: { width: sidebarWidth + 'px', minWidth: '240px', maxWidth: '400px' }
			"
		>
			<div
				class="h-20 flex items-center border-b border-gray-200 dark:border-white/5 transition-all duration-300"
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
						class="text-gray-900 dark:text-white font-black text-2xl tracking-tighter whitespace-nowrap leading-none truncate"
					>
						ZEVAR
					</h1>
				</div>
				<button
					v-if="!isSidebarCollapsed"
					@click="isSidebarCollapsed = true"
					class="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 border border-gray-200 dark:border-white/10 hover:bg-white/10 transition-all text-gray-400 hover:text-white shrink-0"
					aria-label="Collapse sidebar"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.8"
							d="M20 6H10M20 12h-6M20 18H10M9 8l-4 4 4 4"
						></path>
					</svg>
				</button>
				<button
					v-else
					@click="isSidebarCollapsed = false"
					class="hidden lg:flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 border border-gray-200 dark:border-white/10 hover:bg-white/10 transition-all text-gray-400 hover:text-white shrink-0"
					aria-label="Expand sidebar"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="1.8"
							d="M4 6h10M4 12h6M4 18h10M15 8l4 4-4 4"
						></path>
					</svg>
				</button>
			</div>

			<div class="flex-1 flex flex-col overflow-hidden">
				<nav class="p-4 space-y-6 flex-1 overflow-y-auto custom-scrollbar">
					<!-- Grouped Navigation -->
					<div
						v-for="(section, groupIdx) in [
							{ label: 'Operations', items: navOperations },
							{ label: 'Sales', items: navSales },
							{ label: 'Services', items: navServices },
							{ label: 'Management', items: navManagement },
						]"
						:key="groupIdx"
						class="space-y-1"
					>
						<div
							v-if="!isSidebarCollapsed"
							class="px-3 mb-2 flex items-center justify-between"
						>
							<span
								class="text-[10px] font-black text-gray-500 uppercase tracking-widest opacity-50"
								>{{ section.label }}</span
							>
						</div>
						<div
							v-else
							class="h-px bg-gray-200 dark:bg-white/5 mx-2 mb-4 opacity-50"
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
									></path>
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
				</nav>
			</div>

			<!-- Resize Handle -->
			<div
				v-if="!isSidebarCollapsed"
				class="absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-[#D4AF37]/30 transition-colors z-40"
				@mousedown="startResize"
			></div>
		</aside>

		<div class="flex-1 flex flex-col relative min-w-0">
			<header
				class="h-16 sm:h-20 bg-white dark:bg-[#15161a] border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-3 sm:px-6 z-[60] sticky top-0 shadow-sm transition-colors duration-300 flex-shrink-0"
			>
				<!-- Mobile Left Header (Hamburger + Logo + Location) -->
				<div class="flex lg:hidden items-center gap-2 sm:gap-3 flex-1 min-w-0">
					<button
						@click="isMobileDrawerOpen = true"
						class="p-1 sm:p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0"
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
							></path>
						</svg>
					</button>
					<img
						src="/logo.svg"
						alt="Zevar"
						class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg shrink-0"
					/>
					<div class="relative ml-1 sm:ml-2 min-w-0 flex-1">
						<select
							v-model="session.currentWarehouse"
							@change="session.setWarehouse($event.target.value)"
							class="h-8 sm:h-9 w-full bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 pl-2 pr-6 rounded-lg text-xs font-bold text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] cursor-pointer appearance-none overflow-hidden text-ellipsis whitespace-nowrap"
						>
							<option :value="null" disabled>Store...</option>
							<option v-for="wh in warehouses.data" :key="wh.name" :value="wh.name">
								{{
									wh.name.replace('Zevar US Stores - ', '').replace(' - ZUS', '')
								}}
							</option>
						</select>
						<svg
							class="w-3 h-3 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500"
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
					</div>
				</div>

				<!-- Desktop Left Header (Store & Search) -->
				<div class="hidden lg:flex items-center gap-4 flex-1 max-w-3xl">
					<div class="relative group">
						<select
							v-model="session.currentWarehouse"
							@change="session.setWarehouse($event.target.value)"
							class="h-11 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 pl-4 pr-10 rounded-lg text-sm font-bold text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-[#D4AF37] focus:border-[#D4AF37] cursor-pointer min-w-[200px] transition-all hover:bg-gray-100 dark:hover:bg-gray-700 shadow-sm outline-none"
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
							></path>
						</svg>
						<input
							type="text"
							v-model="ui.searchQuery"
							placeholder="Search collection..."
							class="h-11 w-full bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-600 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent text-sm font-medium pl-11 transition-all"
						/>
					</div>
				</div>

				<div class="flex items-center gap-2 sm:gap-3 sm:ml-4 lg:ml-8">
					<!-- Live Spot Rates - Desktop Only -->
					<div
						class="hidden xl:flex items-center gap-0 bg-gray-100 dark:bg-[#15161a] text-gray-900 dark:text-white pl-3 pr-1 py-1 lg:pl-4 lg:pr-2 lg:py-1 rounded-xl border border-gray-200 dark:border-gray-800 max-w-lg overflow-hidden transition-colors duration-300"
					>
						<div
							class="flex items-center gap-1.5 lg:gap-2 border-r border-gray-300 dark:border-gray-800 pr-2 mr-2 lg:pr-3 lg:mr-3 flex-shrink-0"
						>
							<span class="relative flex h-1.5 w-1.5 lg:h-2 lg:w-2">
								<span
									class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"
								></span>
								<span
									class="relative inline-flex rounded-full h-1.5 w-1.5 lg:h-2 lg:w-2 bg-green-600"
								></span>
							</span>
							<span
								class="text-[8px] lg:text-[10px] font-bold uppercase tracking-widest text-gray-500 dark:text-gray-400"
								>Live Spot</span
							>
						</div>
						<div
							class="flex items-center gap-3 lg:gap-8 overflow-x-auto pr-1 lg:pr-2 custom-scrollbar-horizontal pb-1 lg:pb-2 pt-0.5 lg:pt-1"
						>
							<div
								v-for="[key, rate] in sortedRates"
								:key="key"
								class="flex flex-col leading-tight flex-shrink-0 px-1 lg:px-3"
							>
								<span
									class="text-[8px] lg:text-[10px] text-gray-500 dark:text-gray-400 uppercase font-bold whitespace-nowrap mb-0"
									>{{ key.replace(/-/g, ' ') }}</span
								>
								<span
									class="text-[11px] lg:text-base font-mono font-bold text-[#D4AF37] tracking-wide"
									>${{ rate
									}}<span
										class="text-[7px] lg:text-[9px] text-gray-500 dark:text-gray-500 ml-0.5 font-normal"
										>/oz</span
									></span
								>
							</div>
						</div>
					</div>

					<!-- User Profile Dropdown -->
					<div class="relative">
						<button
							@click.stop="isUserMenuOpen = !isUserMenuOpen"
							class="flex items-center gap-2 p-1.5 pr-3 rounded-full hover:bg-gray-100 dark:hover:bg-white/5 transition-colors border border-transparent hover:border-gray-200 dark:hover:border-gray-200 dark:border-white/10"
						>
							<div
								class="w-8 h-8 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#F2E6A0] flex items-center justify-center text-[#0F1115] font-bold text-xs shadow-sm"
							>
								{{ session.user?.full_name?.[0]?.toUpperCase() || 'U' }}
							</div>
							<span
								class="text-sm font-semibold hidden sm:block text-gray-700 dark:text-white truncate max-w-[80px]"
								>{{ session.user?.full_name?.split(' ')[0] || 'Guest' }}</span
							>
							<svg
								class="w-4 h-4 text-gray-400 hidden sm:block"
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
							v-if="isUserMenuOpen"
							@click.stop="isUserMenuOpen = false"
							class="fixed inset-0 z-40"
						></div>

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
								class="absolute right-0 mt-2 w-56 bg-white dark:bg-[#1a1c23] rounded-xl shadow-xl border border-gray-100 dark:border-gray-800 py-2 z-50 origin-top-right overflow-hidden"
							>
								<div
									class="px-4 py-3 border-b border-gray-100 dark:border-gray-200 dark:border-white/5 bg-gray-50/50 dark:bg-white/[0.02]"
								>
									<p
										class="text-sm font-bold text-gray-900 dark:text-white truncate"
									>
										{{ session.user?.full_name || 'Guest User' }}
									</p>
									<p
										class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5"
									>
										{{ session.user?.email || 'Not logged in' }}
									</p>
								</div>
								<div
									class="py-1 border-b border-gray-100 dark:border-gray-200 dark:border-white/5"
								>
									<a
										href="#"
										@click.prevent="isUserMenuOpen = false"
										class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
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
												d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
											></path>
										</svg>
										Profile Settings
									</a>
									<a
										href="#"
										@click.prevent="isUserMenuOpen = false"
										class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
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
												d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
											></path>
										</svg>
										Preferences
									</a>
									<a
										href="#"
										@click.prevent="isUserMenuOpen = false"
										class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
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
												d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
											></path>
										</svg>
										Account History
									</a>
								</div>
								<div
									class="py-1 border-b border-gray-100 dark:border-gray-200 dark:border-white/5"
								>
									<button
										@click.stop="ui.toggleTheme()"
										class="w-full flex items-center justify-between px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
									>
										<div class="flex items-center gap-3">
											<svg
												v-if="ui.isDark"
												class="w-4 h-4 text-gray-400"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
												></path>
											</svg>
											<svg
												v-else
												class="w-4 h-4 text-gray-400"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
												></path>
											</svg>
											{{ ui.isDark ? 'Light Mode' : 'Dark Mode' }}
										</div>
										<div
											class="w-8 h-4 bg-gray-200 dark:bg-[#C9A962] rounded-full relative transition-colors duration-300 flex items-center"
										>
											<div
												class="w-3 h-3 bg-white rounded-full absolute transition-transform duration-300 shadow-sm"
												:class="
													ui.isDark
														? 'translate-x-[18px]'
														: 'translate-x-[2px]'
												"
											></div>
										</div>
									</button>
								</div>
								<div class="py-1">
									<button
										@click.stop="session.logoutResource.submit()"
										class="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors font-medium"
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
											></path>
										</svg>
										Sign Out
									</button>
								</div>
							</div>
						</Transition>
					</div>

					<!-- Cart Button (Mobile/Tablet Toggle) -->
					<button
						@click="isCartOpen = true"
						class="lg:hidden relative p-2 sm:p-3 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors group shrink-0"
					>
						<svg
							class="w-5 h-5 sm:w-6 sm:h-6 text-gray-600 dark:text-gray-300 group-hover:text-black dark:group-hover:text-white transition-colors"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
							></path>
						</svg>
						<span
							v-if="cartStore.totalItems > 0"
							class="absolute top-0 right-0 h-4 w-4 sm:h-5 sm:w-5 flex items-center justify-center bg-[#D4AF37] text-white text-[9px] sm:text-[10px] font-bold rounded-full shadow-md transform group-hover:scale-110 transition-transform"
						>
							{{ cartStore.totalItems }}
						</span>
					</button>
				</div>
			</header>

			<div class="flex-1 flex overflow-hidden">
				<main
					class="flex-1 overflow-y-auto overflow-x-hidden p-3 sm:p-4 lg:p-6 pb-16 xl:pb-6 bg-[#F8F9FA] dark:bg-[#1e1e24] transition-colors duration-300"
				>
					<slot></slot>
				</main>

				<!-- Persistent Selection Tray (Right Sidebar) -->
				<div
					class="hidden lg:flex flex-col flex-shrink-0 h-full w-[380px] bg-white dark:bg-[#1a1c23] border-l border-gray-200 dark:border-white/5 overflow-hidden"
				>
					<CartSidebar :isOpen="true" :persistent="true" />
				</div>
			</div>
		</div>

		<CartSidebar :isOpen="isCartOpen" :persistent="false" @close="isCartOpen = false" />

		<!-- Mobile/Tablet Live Rates Bar - Fixed overlay, Hidden on XL+ -->
		<div
			class="xl:hidden fixed bottom-0 left-0 right-0 z-20 bg-white/95 dark:bg-[#15161a]/95 backdrop-blur-sm border-t border-gray-200 dark:border-white/5 py-2 px-3 flex items-center justify-between flex-shrink-0"
		>
			<div
				class="flex items-center gap-1.5 pr-2 border-r border-gray-200 dark:border-white/10 flex-shrink-0"
			>
				<span class="relative flex h-2 w-2">
					<span
						class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"
					></span>
					<span class="relative inline-flex rounded-full h-2 w-2 bg-green-600"></span>
				</span>
				<span class="text-[9px] font-bold uppercase tracking-widest text-gray-400"
					>Spot</span
				>
			</div>
			<div class="flex items-center gap-3 overflow-x-auto hide-scrollbar pl-2 flex-1">
				<div
					v-for="[key, rate] in sortedRates.slice(0, 4)"
					:key="key"
					class="flex flex-col flex-shrink-0 leading-tight"
				>
					<span class="text-[8px] text-gray-500 font-bold uppercase">{{
						key.split('-')[0]
					}}</span>
					<span class="text-xs font-bold text-[#D4AF37]">${{ rate }}</span>
				</div>
			</div>
		</div>

		<!-- MOBILE/TABLET DRAWER OVERLAY -->
		<div
			v-if="isMobileDrawerOpen"
			@click="isMobileDrawerOpen = false"
			class="fixed inset-0 bg-black/50 z-40 lg:hidden transition-opacity"
		></div>

		<!-- MOBILE/TABLET DRAWER -->
		<aside
			class="fixed inset-y-0 left-0 z-50 w-[85vw] max-w-[320px] bg-white dark:bg-[#15161a] shadow-2xl transform transition-transform duration-300 lg:hidden flex flex-col"
			:class="isMobileDrawerOpen ? 'translate-x-0' : '-translate-x-full'"
		>
			<!-- Drawer Header -->
			<div
				class="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-white/5 shrink-0"
			>
				<div class="flex items-center gap-3">
					<img src="/logo.svg" alt="Zevar POS" class="w-8 h-8 rounded-lg" />
					<span
						class="text-gray-900 dark:text-white font-black text-2xl tracking-tighter leading-none mt-0.5"
						>ZEVAR</span
					>
				</div>
				<button
					@click="isMobileDrawerOpen = false"
					class="text-gray-400 p-2 hover:text-white transition-colors"
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						></path>
					</svg>
				</button>
			</div>

			<!-- Search & Store -->
			<div class="p-4 space-y-3 border-b border-gray-200 dark:border-white/5 shrink-0">
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
						></path>
					</svg>
					<input
						type="text"
						v-model="ui.searchQuery"
						placeholder="Search collection..."
						class="h-11 w-full bg-gray-800 border border-gray-700 text-gray-200 rounded-lg pl-10 pr-4 focus:ring-2 focus:ring-[#D4AF37] focus:border-transparent text-sm"
					/>
				</div>
				<div class="relative">
					<select
						v-model="session.currentWarehouse"
						@change="session.setWarehouse($event.target.value)"
						class="h-11 w-full bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 pr-8 focus:ring-2 focus:ring-[#D4AF37] text-sm appearance-none"
					>
						<option :value="null" disabled>Select Store Location</option>
						<option v-for="wh in warehouses.data" :key="wh.name" :value="wh.name">
							{{ wh.name }}
						</option>
					</select>
					<svg
						class="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500"
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
				</div>
			</div>

			<!-- Navigation -->
			<nav class="flex-1 overflow-y-auto p-4 space-y-0.5 custom-scrollbar">
				<template
					v-for="(section, sIdx) in [
						{ label: 'Operations', items: navOperations },
						{ label: 'Sales', items: navSales },
						{ label: 'Services', items: navServices },
						{ label: 'Management', items: navManagement },
					]"
					:key="sIdx"
				>
					<div class="px-3 pt-3 pb-1" :class="{ 'pt-1': sIdx === 0 }">
						<span
							class="text-[9px] font-bold text-gray-400 dark:text-gray-600 uppercase tracking-widest"
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
								: 'text-gray-600 dark:text-gray-400 hover:text-[#D4AF37] hover:bg-gray-50 dark:hover:bg-white/5'
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
							></path>
						</svg>
						<span class="font-medium text-[13px]">{{ item.label }}</span>
					</router-link>
				</template>

				<!-- Live Rates in Mobile Drawer -->
				<div class="mt-6 pt-6 border-t border-gray-200 dark:border-white/5">
					<div class="flex items-center gap-2 mb-3 px-1">
						<span class="relative flex h-2 w-2">
							<span
								class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"
							></span>
							<span
								class="relative inline-flex rounded-full h-2 w-2 bg-green-600"
							></span>
						</span>
						<span class="text-[10px] font-bold uppercase tracking-widest text-gray-500"
							>Live Spot Rates</span
						>
					</div>
					<div class="grid grid-cols-2 gap-2">
						<div
							v-for="[key, rate] in sortedRates.slice(0, 4)"
							:key="key"
							class="bg-gray-800/80 p-2.5 rounded-lg text-center border border-gray-200 dark:border-white/5"
						>
							<div class="text-[9px] text-gray-400 uppercase font-bold mb-0.5">
								{{ key.replace(/-/g, ' ') }}
							</div>
							<div class="text-sm font-bold text-[#D4AF37]">
								${{ rate }}<span class="text-[8px] text-gray-500">/oz</span>
							</div>
						</div>
					</div>
				</div>

				<!-- Theme Toggle in Mobile Drawer -->
				<div class="mt-4 pt-4 border-t border-gray-200 dark:border-white/5">
					<button
						@click="ui.toggleTheme()"
						class="w-full flex items-center justify-between px-4 py-3 rounded-xl text-gray-600 dark:text-gray-400 hover:text-[#D4AF37] hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
					>
						<div class="flex items-center gap-3">
							<svg
								v-if="ui.isDark"
								class="w-5 h-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
								></path>
							</svg>
							<svg
								v-else
								class="w-5 h-5"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
								></path>
							</svg>
							<span class="text-sm font-medium">{{
								ui.isDark ? 'Light Mode' : 'Dark Mode'
							}}</span>
						</div>
						<div
							class="w-10 h-5 bg-gray-600 dark:bg-[#C9A962] rounded-full relative transition-colors duration-300 flex items-center"
						>
							<div
								class="w-4 h-4 bg-white rounded-full absolute transition-transform duration-300 shadow-sm"
								:class="ui.isDark ? 'translate-x-[22px]' : 'translate-x-[2px]'"
							></div>
						</div>
					</button>

					<button
						@click="session.logoutResource.submit()"
						class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-colors mt-1"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
							></path>
						</svg>
						<span class="text-sm font-medium">Sign Out</span>
					</button>
				</div>
			</nav>
		</aside>
	</div>
</template>

<script setup>
import { useSessionStore } from '@/stores/session'
import { useGoldStore } from '@/stores/gold.js'
import { useCartStore } from '@/stores/cart.js'
import { useUIStore } from '@/stores/ui'
import { createResource } from 'frappe-ui'
import { onMounted, ref, computed, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import CartSidebar from '@/components/CartSidebar.vue'
import FilterBar from '@/components/FilterBar.vue'
import FilterSidebar from '@/components/FilterSidebar.vue'

const session = useSessionStore()
const goldStore = useGoldStore()
const cartStore = useCartStore()
const ui = useUIStore()

const isCartOpen = ref(false)
const isUserMenuOpen = ref(false)
const isMobileDrawerOpen = ref(false)
const isSidebarCollapsed = ref(false)
const sidebarRef = ref(null)
const sidebarWidth = ref(288)

// Navigation data
const navOperations = [
	{
		to: '/',
		label: 'POS Terminal',
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
		icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
	},
]
const navSales = [
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
	{ to: '/layaway', label: 'Layaway', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
]
const navServices = [
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
]
const navManagement = [
	{
		to: '/reports',
		label: 'Reports',
		icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
	},
	{
		to: '/support',
		label: 'Support',
		icon: 'M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z',
	},
]

// Route active check
const route = useRoute()
function isNavActive(path) {
	const current = route.path || ''
	if (path === '/') return current === '/'
	return current === path || current.startsWith(path + '/')
}

// Show filters on relevant pages
const showFilterSidebar = computed(() => {
	const path = route.path || ''
	return ['/', '/inventory', '/pos-catalogue'].includes(path) || path.startsWith('/catalogues')
})

const TROY_OZ_GRAMS = 31.1035

const sortedRates = computed(() => {
	if (!goldStore.rates) return []
	const priority = [
		'Yellow Gold-24K',
		'Yellow Gold-22K',
		'Yellow Gold-18Kt',
		'Silver-925 Sterling',
	]
	return Object.entries(goldStore.rates)
		.filter(([key]) => !key.includes('Platinum'))
		.map(([key, ratePerGram]) => [key, (ratePerGram * TROY_OZ_GRAMS).toFixed(2)])
		.sort((a, b) => {
			const indexA = priority.indexOf(a[0])
			const indexB = priority.indexOf(b[0])
			if (indexA !== -1 && indexB !== -1) return indexA - indexB
			if (indexA !== -1) return -1
			if (indexB !== -1) return 1
			return a[0].localeCompare(b[0])
		})
})

const warehouses = createResource({
	url: 'frappe.client.get_list',
	params: {
		doctype: 'Warehouse',
		filters: { is_group: 0, parent_warehouse: ['like', '%Zevar US Stores%'] },
		fields: ['name'],
	},
	auto: true,
	onSuccess(data) {
		if (!data || data.length === 0) {
			warehouseFallback.fetch()
		}
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
		if (data && data.length > 0) {
			warehouses.data = data
		}
	},
})

// Sidebar resize
const isResizing = ref(false)
let startX = 0
let startWidth = 0

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
	const diff = e.clientX - startX
	const newWidth = Math.min(Math.max(startWidth + diff, 240), 400)
	sidebarWidth.value = newWidth
}

function stopResize() {
	isResizing.value = false
	document.removeEventListener('mousemove', handleResize)
	document.removeEventListener('mouseup', stopResize)
}

onUnmounted(() => {
	document.removeEventListener('mousemove', handleResize)
	document.removeEventListener('mouseup', stopResize)
})

onMounted(() => {
	goldStore.startPolling()
	if (session.currentWarehouse) {
		cartStore.loadTaxForWarehouse(session.currentWarehouse)
	}
})

watch(
	() => session.currentWarehouse,
	(newWh) => {
		if (newWh) {
			cartStore.loadTaxForWarehouse(newWh)
		}
	}
)
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

.custom-scrollbar-horizontal::-webkit-scrollbar {
	height: 4px;
}
.custom-scrollbar-horizontal::-webkit-scrollbar-track {
	background: transparent;
	margin: 0 10px;
}
.custom-scrollbar-horizontal::-webkit-scrollbar-thumb {
	background: #cbd5e1;
	border-radius: 10px;
}
.dark .custom-scrollbar-horizontal::-webkit-scrollbar-thumb {
	background: #333;
}
.custom-scrollbar-horizontal::-webkit-scrollbar-thumb:hover {
	background: #d4af37;
}

.hide-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
.hide-scrollbar::-webkit-scrollbar {
	display: none;
}
</style>
