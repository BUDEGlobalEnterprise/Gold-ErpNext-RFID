<template>
	<AppLayout>
		<div class="reports-layout flex flex-col gap-4 h-full">
			<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 class="text-2xl font-semibold text-gray-900 dark:text-white">Command Center</h1>
					<p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Unified reporting and analytics</p>
				</div>
				<DateRangeToggle />
			</header>

			<CommandCenterTabs />

			<div class="flex-1 overflow-y-auto min-h-0 pt-2">
				<!-- keep-alive so switching tabs is instantaneous and doesn't refetch -->
				<router-view v-slot="{ Component }">
					<transition name="fade" mode="out-in">
						<keep-alive>
							<component :is="Component" />
						</keep-alive>
					</transition>
				</router-view>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import CommandCenterTabs from '@/components/reports/CommandCenterTabs.vue'
import DateRangeToggle from '@/components/reports/DateRangeToggle.vue'
</script>

<style scoped>
.reports-layout {
	padding-bottom: 24px;
}
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
	transform: translateY(4px);
}
</style>
