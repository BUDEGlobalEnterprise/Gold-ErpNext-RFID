<template>
	<!-- Full Page Loading Guard -->
	<div
		v-if="!isReady"
		class="h-[100dvh] w-full flex items-center justify-center bg-gray-50 dark:bg-[#05070a]"
	>
		<div class="flex flex-col items-center gap-4">
			<div
				class="w-12 h-12 rounded-2xl bg-emerald-950 flex items-center justify-center text-white shadow-glow-emerald animate-pulse"
			>
				<span class="material-symbols-outlined text-2xl">diamond</span>
			</div>
			<div class="flex items-center gap-2">
				<div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.3s]"></div>
				<div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:-0.15s]"></div>
				<div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-bounce"></div>
			</div>
		</div>
	</div>

	<div
		v-else
		class="h-[100dvh] w-full flex overflow-hidden bg-gray-50 dark:bg-[#0b0f19] font-display text-gray-900 dark:text-gray-100 selection:bg-emerald-500/30 relative transition-colors duration-500"
	>
		<!-- Mobile Sidebar Overlay -->
		<div
			v-if="mobileMenuOpen"
			class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 hidden sm:block lg:hidden transition-opacity duration-300"
			@click="mobileMenuOpen = false"
		></div>

		<!-- Sidebar -->
		<aside
			class="shrink-0 hidden sm:flex flex-col bg-white dark:bg-[#0a0c1a] border-r border-gray-200 dark:border-white/5 z-50 transition-all duration-300 fixed top-0 left-0 lg:relative h-full"
			:class="[
				sidebarCollapsed ? 'lg:w-20 lg:items-center' : 'lg:w-64',
				mobileMenuOpen ? 'w-64 translate-x-0' : '-translate-x-full lg:translate-x-0',
			]"
		>
			<!-- Branding -->
			<div
				class="h-32 flex items-center px-10 gap-4 shrink-0"
				:class="sidebarCollapsed ? 'lg:px-4 justify-center' : 'justify-between'"
			>
				<div
					v-if="!sidebarCollapsed"
					class="flex items-center gap-5 overflow-hidden group cursor-pointer"
				>
					<div
						class="w-12 h-12 rounded-2xl bg-emerald-950 flex items-center justify-center text-white shadow-glow-emerald shrink-0 transition-transform duration-500"
					>
						<span class="material-symbols-outlined text-2xl icon-loading-guard">diamond</span>
					</div>
					<div class="flex flex-col leading-none">
						<span
							class="font-black text-gray-900 dark:text-white tracking-tighter text-2xl uppercase mb-1"
							>Zevar</span
						>
						<span
							class="text-[9px] text-gray-400 font-black uppercase tracking-[0.4em] whitespace-nowrap"
							>The Curated Atelier</span
						>
					</div>
				</div>
				<div
					v-else
					class="w-12 h-12 rounded-2xl bg-emerald-950 flex items-center justify-center text-white shadow-glow-emerald shrink-0 transition-transform duration-500 cursor-pointer"
				>
					<span class="material-symbols-outlined text-2xl icon-loading-guard">diamond</span>
				</div>
			</div>

			<!-- Nav Items -->
			<nav class="flex-1 px-8 space-y-2.5 overflow-y-auto no-scrollbar pb-10 pt-4">
				<router-link
					v-for="item in navItems"
					:key="item.to"
					:to="item.to"
					custom
					v-slot="{ href, navigate, isActive, isExactActive }"
				>
					<a
						:href="item.isExternal ? item.to : href"
						@click="(e) => { if (item.isExternal) return; navigate(e); mobileMenuOpen = false; }"
						class="flex items-center rounded-2xl transition-all duration-300 group relative"
						:class="[
							(item.to === '/' ? isExactActive : isActive)
								? 'bg-emerald-950 text-white shadow-glow-emerald'
								: 'text-gray-500 dark:text-white/70 hover:bg-gray-100/80 dark:hover:bg-white/5',
							sidebarCollapsed
								? 'lg:justify-center lg:px-0 lg:py-4'
								: 'justify-between px-6 py-4',
						]"
					>
						<div class="flex items-center gap-4 pointer-events-none">
							<span class="material-symbols-outlined text-[22px] shrink-0 pointer-events-none icon-loading-guard">{{
								item.icon
							}}</span>
							<span
								v-show="!sidebarCollapsed"
								class="text-[11px] font-black uppercase tracking-[0.25em] pointer-events-none"
								>{{ renderLabel(item.label) }}</span
							>
						</div>
						<div
							v-if="(item.to === '/' ? isExactActive : isActive) && !sidebarCollapsed"
							class="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgb(52,211,153)] pointer-events-none"
						></div>
					</a>
				</router-link>
			</nav>

			<!-- Bottom Section (Manager Info) -->
			<div
				class="p-4 border-t border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-black/20"
				v-if="!sidebarCollapsed"
			>
				<div
					class="flex items-center gap-3 bg-white dark:bg-white/5 p-3 rounded-xl border border-gray-200 dark:border-white/10 shadow-sm"
				>
					<div
						class="w-9 h-9 rounded-full overflow-hidden border border-gray-100 shrink-0"
					>
						<img
							src="https://i.pravatar.cc/150?u=julian"
							class="w-full h-full object-cover"
						/>
					</div>
					<div class="flex flex-col min-w-0">
						<span
							class="text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mb-1"
							>Manager</span
						>
						<span
							class="text-[11px] font-bold text-gray-900 dark:text-white truncate"
							>{{ managerName }}</span
						>
					</div>
				</div>
			</div>
		</aside>

		<!-- Main Content -->
		<main class="flex-1 flex flex-col h-full min-w-0 overflow-hidden">
			<!-- Header -->
			<header
				class="flex items-center px-4 md:px-10 h-20 bg-white/10 dark:bg-transparent backdrop-blur-md shrink-0"
			>
				<!-- Mobile Logo (Mobile only) -->
				<div class="flex items-center gap-3 sm:hidden cursor-pointer">
					<div class="w-8 h-8 rounded-lg bg-emerald-950 flex items-center justify-center text-white shadow-glow-emerald shrink-0">
						<span class="material-symbols-outlined text-lg icon-loading-guard">diamond</span>
					</div>
					<span class="font-black text-gray-900 dark:text-white tracking-tighter text-sm uppercase">Zevar</span>
				</div>

				<!-- Header Actions (Tablet) -->
				<button
					@click="mobileMenuOpen = !mobileMenuOpen"
					class="hidden sm:flex lg:hidden w-10 h-10 rounded-xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 items-center justify-center text-gray-500 dark:text-white/70 hover:bg-gray-50 dark:hover:bg-white/10 transition-colors"
				>
					<span class="material-symbols-outlined icon-loading-guard">{{
						mobileMenuOpen ? "close" : "menu"
					}}</span>
				</button>

				<!-- Sidebar Toggle (Desktop) -->
				<button
					@click="sidebarCollapsed = !sidebarCollapsed"
					class="hidden lg:flex w-10 h-10 rounded-xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 items-center justify-center text-gray-500 dark:text-white/70 hover:bg-gray-50 dark:hover:bg-white/10 transition-colors ml-4"
				>
					<span class="material-symbols-outlined icon-loading-guard">{{
						sidebarCollapsed ? "menu" : "menu_open"
					}}</span>
				</button>

				<!-- Search Bar -->
				<div class="relative w-full max-w-lg hidden md:block ml-4">
					<span
						class="material-symbols-outlined absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 text-lg icon-loading-guard"
						>search</span
					>
					<input
						type="search"
						placeholder="Search orders, gemstones, or team..."
						class="w-full bg-gray-50/80 dark:bg-white/5 border border-transparent focus:bg-white focus:border-gray-100 dark:focus:border-white/10 rounded-2xl py-3 pl-14 pr-6 text-[13px] focus:outline-none transition-all placeholder-gray-400 font-medium"
					/>
				</div>

				<div class="ml-auto flex items-center gap-6">
					<!-- Notification & Settings Icons -->
					<div class="flex items-center gap-3 text-gray-400">
						<button
							class="w-10 h-10 rounded-full flex items-center justify-center transition-all"
						>
							<span class="material-symbols-outlined text-[22px] icon-loading-guard"
								>notifications</span
							>
						</button>
						<button
							class="w-10 h-10 rounded-full flex items-center justify-center transition-all"
						>
							<span class="material-symbols-outlined text-[22px] icon-loading-guard">settings</span>
						</button>
					</div>

					<div class="h-8 w-px bg-gray-200 dark:bg-white/10"></div>

					<!-- User Profile Section -->
					<div class="flex items-center gap-5">
						<div class="text-right hidden sm:block">
							<p
								class="text-[13px] font-black text-gray-900 dark:text-white tracking-tight leading-none mb-1"
							>
								{{ auth.user?.full_name || "Marcus Sterling" }}
							</p>
							<p
								class="text-[9px] text-gray-400 font-bold uppercase tracking-[0.2em]"
							>
								{{ employeeStore.employee?.designation || "-" }}
							</p>
						</div>
						<button
							class="w-11 h-11 rounded-2xl bg-gray-100 dark:bg-white/5 p-0.5 overflow-hidden group relative border border-gray-100 dark:border-white/10"
							@click="userMenuOpen = !userMenuOpen"
						>
							<img
								:src="
									employeeStore.employee?.image ||
									'https://i.pravatar.cc/150?u=marcus'
								"
								class="w-full h-full object-cover rounded-[14px]"
							/>
						</button>
					</div>

					<Teleport to="body">
						<div
							v-show="userMenuOpen"
							class="fixed right-8 top-20 mt-2 w-64 bg-white dark:bg-[#0a0c1a] border border-gray-200 dark:border-white/10 rounded-3xl shadow-2xl py-3 z-[60] flex flex-col font-medium overflow-hidden"
						>
							<div
								class="px-6 py-4 border-b border-gray-50 dark:border-white/5 mb-1 bg-gray-50/50 dark:bg-white/5"
							>
								<p class="text-gray-900 dark:text-white font-bold text-sm">
									{{ auth.user?.full_name || "User" }}
								</p>
								<p
									class="text-[11px] text-gray-500 mt-1 uppercase tracking-widest font-black"
								>
									{{ employeeStore.employee?.designation || "-" }}
								</p>
							</div>

							<button
								@click="toggleDarkMode"
								class="w-full text-left px-6 py-3 text-gray-600 dark:text-gray-400 transition-colors flex items-center justify-between group"
							>
								<div class="flex items-center gap-4">
									<span class="material-symbols-outlined text-[20px] icon-loading-guard">{{
										isDark ? "light_mode" : "dark_mode"
									}}</span>
									<span class="text-xs font-bold uppercase tracking-widest">{{
										isDark ? "Light Mode" : "Dark Mode"
									}}</span>
								</div>
							</button>

							<button
								@click="auth.logout()"
								class="w-full text-left px-6 py-3 text-red-500 transition-colors flex items-center gap-4 group"
							>
								<span class="material-symbols-outlined text-[20px] icon-loading-guard">logout</span>
								<span class="text-xs font-bold uppercase tracking-widest text-red-500"
									>Log out</span
								>
							</button>
						</div>
					</Teleport>
				</div>
			</header>

			<!-- Page Content Container -->
			<div class="flex-1 overflow-y-auto custom-scrollbar p-6 pb-24 sm:pb-6 md:p-10 relative">
				<slot />
			</div>
		</main>

		<!-- Bottom Scrollable Navigation Bar (Mobile Only) -->
		<div class="sm:hidden fixed bottom-0 left-0 right-0 z-[60] backdrop-blur-md bg-white/80 dark:bg-[#0a0c1a]/85 border-t border-gray-200/80 dark:border-white/5 shadow-[0_-8px_30px_rgb(0,0,0,0.08)] pb-[calc(env(safe-area-inset-bottom,0px)+8px)]">
			<nav class="flex items-center gap-3 overflow-x-auto no-scrollbar px-6 pt-4 pb-2">
				<router-link
					v-for="item in navItems"
					:key="item.to"
					:to="item.to"
					custom
					v-slot="{ href, navigate, isActive, isExactActive }"
				>
					<a
						:href="item.isExternal ? item.to : href"
						@click="(e) => { if (item.isExternal) return; navigate(e); }"
						class="flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all duration-300 whitespace-nowrap shrink-0"
						:class="(item.to === '/' ? isExactActive : isActive)
							? 'bg-emerald-950 text-white shadow-glow-emerald'
							: 'text-gray-500 dark:text-white/70 hover:bg-gray-100/80 dark:hover:bg-white/5'"
					>
						<span class="material-symbols-outlined text-[18px] shrink-0 pointer-events-none icon-loading-guard">{{ item.icon }}</span>
						<span class="text-[10px] font-black uppercase tracking-[0.2em] pointer-events-none">{{ renderLabel(item.label) }}</span>
					</a>
				</router-link>
			</nav>
		</div>
	</div>
</template>

<script setup>
import { computed, ref, onMounted, Teleport } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useEmployeeStore } from "@/stores/employee";
import { useRoute } from "vue-router";

const auth = useAuthStore();
const route = useRoute();
const employeeStore = useEmployeeStore();

const sidebarCollapsed = ref(false);
const userMenuOpen = ref(false);
const isDark = ref(false);
const mobileMenuOpen = ref(false);

const showDesk = ref(false);
const isDeskAccessChecked = ref(false);
const fontReady = ref(false);

const isReady = computed(() => {
	// Wait for auth, employee data, desk access check, AND fonts to be ready
	return auth.ready && employeeStore.ready && isDeskAccessChecked.value && fontReady.value;
});

const managerName = computed(() => employeeStore.employee?.reports_to_name || "-");

const checkDeskAccess = async () => {
  try {
    const res = await fetch('/api/method/zevar_core.api.user_info.user_has_desk_access');
    const data = await res.json();
    showDesk.value = !!data.message;
  } catch (e) {
    console.error('Desk access check failed', e);
    showDesk.value = false;
  } finally {
    isDeskAccessChecked.value = true;
  }
};
const managerInitials = computed(() => {
	return managerName.value
		.split(" ")
		.map((n) => n[0])
		.join("")
		.substring(0, 2)
		.toUpperCase();
});

const baseNavItems = [
	{ to: "/", icon: "dashboard", label: "Dashboard" },
	{ to: "/tasks", icon: "task_alt", label: "Tasks" },
	{ to: "/attendance", icon: "calendar_today", label: "Attendance" },
	{ to: "/roster", icon: "schedule", label: "Roster" },
	{ to: "/leave", icon: "beach_access", label: "Leave" },
	{ to: "/expense", icon: "payments", label: "Expense" },
	{ to: "/payroll", icon: "account_balance_wallet", label: "Payroll" },
	{ to: "/team", icon: "groups", label: "Team" },
	{ to: "/issues", icon: "support_agent", label: "Issues" },
];

const navItems = computed(() => {
  const items = [...baseNavItems];
  if (showDesk.value) {
    items.push({ to: "/desk", icon: "terminal", label: "Open Desk", isExternal: true });
  }
  return items;
});

/**
 * Safely render label, supporting i18n if present.
 * Prevents raw keys from flashing before translations load.
 */
const renderLabel = (label) => {
  if (!label) return "";
  
  // Use window.__ for Frappe translations or $t if using vue-i18n
  // Fallback to the label itself if no translation found
  const translated = window.__ ? window.__(label) : label;
  
  // Optional: If we are still "ready" but the label looks like a key (has underscores), 
  // and we have a user-friendly fallback, use it.
  // But usually, window.__ handles this correctly.
  return translated;
};

const userInitials = computed(() => {
	const name = auth.user?.full_name || "User";
	return name
		.split(" ")
		.map((n) => n[0])
		.join("")
		.substring(0, 2)
		.toUpperCase();
});

const toggleDarkMode = () => {
	isDark.value = !isDark.value;
	if (isDark.value) {
		document.documentElement.classList.add("dark");
		localStorage.setItem("portal_theme", "dark");
	} else {
		document.documentElement.classList.remove("dark");
		localStorage.setItem("portal_theme", "light");
	}
	userMenuOpen.value = false;
};

onMounted(async () => {
	await employeeStore.init();
	await checkDeskAccess();

	// Wait for Material Symbols font to load to prevent icon name flickering
	if (document.fonts) {
		document.fonts.ready.then(() => {
			fontReady.value = true;
		});
		// Fallback if fonts.ready takes too long (e.g. network issue)
		setTimeout(() => { fontReady.value = true; }, 1500);
	} else {
		fontReady.value = true;
	}

	const savedTheme = localStorage.getItem("portal_theme");
	if (savedTheme === "dark") {
		isDark.value = true;
		document.documentElement.classList.add("dark");
	} else {
		isDark.value = false;
		document.documentElement.classList.remove("dark");
	}
});
</script>

<style scoped>
.router-link-active {
	@apply bg-primary text-white shadow-glow-emerald;
}

/* 
  With the Font Loading API guard in isReady, the text will never be visible.
  We keep these styles for standard Material Symbols behavior.
*/
.material-symbols-outlined {
  font-display: block;
  display: inline-block;
  width: 1.5em;
  height: 1.5em;
  line-height: 1;
  text-transform: none;
  letter-spacing: normal;
  word-wrap: normal;
  white-space: nowrap;
  direction: ltr;
}
</style>