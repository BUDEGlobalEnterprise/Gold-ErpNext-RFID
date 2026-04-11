<template>
	<div
		class="h-[100dvh] w-full flex overflow-hidden bg-gray-50 dark:bg-[#05070a] font-display text-gray-900 dark:text-gray-100 selection:bg-emerald-500/30 relative transition-colors duration-500"
	>
		<!-- Mobile Sidebar Overlay -->
		<div
			v-if="mobileMenuOpen"
			class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
			@click="mobileMenuOpen = false"
		></div>

		<!-- Sidebar -->
		<aside
			class="shrink-0 flex flex-col bg-white dark:bg-[#0a0c1a] border-r border-gray-200 dark:border-white/5 z-50 transition-all duration-300 fixed lg:relative h-full"
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
						class="w-12 h-12 rounded-2xl bg-emerald-950 flex items-center justify-center text-white shadow-glow-emerald shrink-0 group-hover:scale-105 transition-transform duration-500"
					>
                        <span class="material-symbols-outlined text-2xl">diamond</span>
					</div>
					<div class="flex flex-col leading-none">
						<span
							class="font-black text-gray-900 dark:text-white tracking-tighter text-2xl uppercase mb-1"
							>Zevar</span
						>
						<span class="text-[9px] text-gray-400 font-black uppercase tracking-[0.4em] whitespace-nowrap">The Curated Atelier</span>
					</div>
				</div>
                <div v-else class="w-12 h-12 rounded-2xl bg-emerald-950 flex items-center justify-center text-white shadow-glow-emerald shrink-0 hover:scale-105 transition-transform duration-500 cursor-pointer">
                    <span class="material-symbols-outlined text-2xl">diamond</span>
                </div>
			</div>

			<!-- Nav Items -->
			<nav class="flex-1 px-8 space-y-2.5 overflow-y-auto no-scrollbar pb-10 pt-4">
				<router-link
					v-for="item in navItems"
					:key="item.to"
					:to="item.to"
					@click="mobileMenuOpen = false"
					class="flex items-center rounded-2xl transition-all duration-300 group relative"
					:class="[
						route.path === item.to
							? 'bg-emerald-950 text-white shadow-glow-emerald'
							: 'text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50/80 dark:hover:bg-white/5',
						sidebarCollapsed
							? 'lg:justify-center lg:px-0 lg:py-4'
							: 'justify-between px-6 py-4',
					]"
				>
					<div class="flex items-center gap-4">
						<span
							class="material-symbols-outlined text-[22px] shrink-0"
							>{{ item.icon }}</span
						>
						<span
							v-show="!sidebarCollapsed"
							class="text-[11px] font-black uppercase tracking-[0.25em]"
							>{{ item.label }}</span
						>
					</div>
                    <div v-if="route.path === item.to && !sidebarCollapsed" class="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgb(52,211,153)]"></div>
				</router-link>
			</nav>

            <!-- Bottom Section (Manager Info) -->
            <div class="p-4 border-t border-gray-100 dark:border-white/5 bg-gray-50/50 dark:bg-black/20" v-if="!sidebarCollapsed">
                <div class="flex items-center gap-3 bg-white dark:bg-white/5 p-3 rounded-xl border border-gray-200 dark:border-white/10 shadow-sm">
                    <div class="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center text-blue-600 dark:text-blue-400 font-black text-xs">
                        {{ managerInitials }}
                    </div>
                    <div class="flex flex-col min-w-0">
                        <span class="text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mb-1">Manager</span>
                        <span class="text-[11px] font-bold text-gray-900 dark:text-white truncate">{{ managerName }}</span>
                    </div>
                </div>
            </div>
		</aside>

		<!-- Main Content -->
		<main
			class="flex-1 flex flex-col h-full min-w-0 overflow-hidden"
		>
			<!-- Header -->
			<header
				class="flex items-center px-4 md:px-10 h-20 bg-white/10 dark:bg-transparent backdrop-blur-md shrink-0"
			>
                <!-- Search Bar -->
                <div class="relative w-full max-w-lg hidden md:block">
                    <span class="material-symbols-outlined absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 text-lg">search</span>
                    <input 
                        type="search" 
                        placeholder="Search orders, gemstones, or team..." 
                        class="w-full bg-gray-50/80 dark:bg-white/5 border border-transparent focus:bg-white focus:border-gray-100 dark:focus:border-white/10 rounded-2xl py-3 pl-14 pr-6 text-[13px] focus:outline-none transition-all placeholder-gray-400 font-medium"
                    />
                </div>

				<!-- Header Actions (Mobile) -->
                <button
                    @click="mobileMenuOpen = !mobileMenuOpen"
                    class="lg:hidden w-10 h-10 rounded-xl bg-white border border-gray-200 flex items-center justify-center text-gray-500"
                >
                    <span class="material-symbols-outlined">{{ mobileMenuOpen ? 'close' : 'menu' }}</span>
                </button>

				<div class="ml-auto flex items-center gap-6">
                    <!-- Notification & Settings Icons -->
                    <div class="flex items-center gap-3 text-gray-400">
                        <button class="w-10 h-10 rounded-full hover:bg-gray-100 hover:text-gray-900 flex items-center justify-center transition-all">
                            <span class="material-symbols-outlined text-[22px]">notifications</span>
                        </button>
                        <button class="w-10 h-10 rounded-full hover:bg-gray-100 hover:text-gray-900 flex items-center justify-center transition-all">
                            <span class="material-symbols-outlined text-[22px]">settings</span>
                        </button>
                    </div>

                    <div class="h-8 w-px bg-gray-200 dark:bg-white/10"></div>

                    <!-- User Profile Section -->
                    <div class="flex items-center gap-5">
                        <div class="text-right hidden sm:block">
                            <p class="text-[13px] font-black text-gray-900 dark:text-white tracking-tight leading-none mb-1">{{ auth.user?.full_name || 'Marcus Sterling' }}</p>
                            <p class="text-[9px] text-gray-400 font-bold uppercase tracking-[0.2em]">Master Setter</p>
                        </div>
                        <button 
                            class="w-11 h-11 rounded-2xl bg-gray-100 dark:bg-white/5 p-0.5 overflow-hidden group relative border border-gray-100 dark:border-white/10"
                            @click="userMenuOpen = !userMenuOpen"
                        >
                            <img :src="employeeStore.employee?.image || 'https://i.pravatar.cc/150?u=marcus'" class="w-full h-full object-cover rounded-[14px]" />
                        </button>
                    </div>

                    <!-- User Menu Dropdown -->
                    <div
						v-show="userMenuOpen"
                        class="absolute right-8 top-20 mt-2 w-64 bg-white dark:bg-[#0a0c1a] border border-gray-200 dark:border-white/10 rounded-3xl shadow-2xl py-3 z-[60] flex flex-col font-medium overflow-hidden"
                    >
                        <div class="px-6 py-4 border-b border-gray-50 dark:border-white/5 mb-1 bg-gray-50/50 dark:bg-white/5">
							<p class="text-gray-900 dark:text-white font-bold text-sm">
								{{ auth.user?.full_name || "User" }}
							</p>
							<p class="text-[11px] text-gray-500 mt-1 uppercase tracking-widest font-black">
								Master Setter
							</p>
						</div>

						<button
							@click="toggleDarkMode"
							class="w-full text-left px-6 py-3 text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-white hover:bg-emerald-50 dark:hover:bg-white/5 transition-colors flex items-center justify-between group"
						>
							<div class="flex items-center gap-4">
								<span class="material-symbols-outlined text-[20px]">{{ isDark ? "light_mode" : "dark_mode" }}</span>
								<span class="text-xs font-bold uppercase tracking-widest">{{ isDark ? "Light Mode" : "Dark Mode" }}</span>
							</div>
						</button>

						<button
							@click="auth.logout()"
							class="w-full text-left px-6 py-3 text-red-500 hover:bg-red-50 transition-colors flex items-center gap-4 group"
						>
							<span class="material-symbols-outlined text-[20px]">logout</span>
							<span class="text-xs font-bold uppercase tracking-widest text-red-500">Log out</span>
						</button>
                    </div>
				</div>
			</header>

			<!-- Page Content Container -->
			<div
				class="flex-1 overflow-y-auto no-scrollbar p-6 md:p-10 relative"
			>
				<slot />
			</div>
		</main>
	</div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRoute } from "vue-router";
import { useEmployeeStore } from "@/stores/employee";

const auth = useAuthStore();
const route = useRoute();
const employeeStore = useEmployeeStore();

const sidebarCollapsed = ref(false);
const mobileMenuOpen = ref(false);
const userMenuOpen = ref(false);
const isDark = ref(false);

const managerName = computed(() => employeeStore.employee?.reports_to_name || "Julian Voss");
const managerInitials = computed(() => {
    return managerName.value.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
});

const navItems = [
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

const userInitials = computed(() => {
	const name = auth.user?.full_name || "User";
	return name.split(" ").map((n) => n[0]).join("").substring(0, 2).toUpperCase();
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
</style>
