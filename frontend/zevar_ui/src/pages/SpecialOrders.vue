<template>
	<AppLayout>
		<div class="flex h-full gap-4 relative">
			<!-- Main Content Area: Wizard -->
			<div class="flex-1 min-w-0 pb-20 lg:pb-0">
				<div class="flex items-center justify-between gap-3 mb-6">
					<div class="flex items-center gap-3">
						<div
							class="w-10 h-10 rounded-xl flex items-center justify-center bg-[#D4AF37]/10"
						>
							<span class="material-symbols-outlined !text-xl text-[#D4AF37]">diamond</span>
						</div>
						<div>
							<h2 class="premium-title !text-xl">Special Orders</h2>
							<p class="text-[10px] text-gray-400 uppercase tracking-widest font-black">Custom Manufacturing Workflow</p>
						</div>
					</div>
					<!-- Navigation Buttons -->
					<div class="flex items-center gap-2 bg-gray-100 dark:bg-warm-dark-800 p-1 rounded-lg">
						<button 
							@click="$router.push('/special-orders')"
							class="px-4 py-1.5 text-sm font-bold rounded-md bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white shadow-sm"
						>
							Order Intake
						</button>
						<button 
							@click="$router.push('/special-orders/job-bag')"
							class="px-4 py-1.5 text-sm font-bold rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
						>
							Job Bag Dashboard
						</button>
					</div>
				</div>

				<!-- Wizard Component -->
				<SpecialOrderWizard />
			</div>

			<!-- Right Sidebar: Live Quote & Kanban -->
			<div class="hidden xl:block w-96 flex-shrink-0">
				<div class="sticky top-24 space-y-6">
					<LiveQuoteWidget />
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import SpecialOrderWizard from '@/components/special-order/SpecialOrderWizard.vue'
import LiveQuoteWidget from '@/components/special-order/LiveQuoteWidget.vue'
</script>
