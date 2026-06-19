<template>
	<AppLayout>
		<div class="flex flex-col h-full bg-gray-50 dark:bg-warm-dark-900 overflow-hidden">
			<!-- Navigation Header -->
			<div class="p-6 pb-2">
				<div class="flex items-center justify-between gap-3">
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-[#D4AF37]/10">
							<span class="material-symbols-outlined !text-xl text-[#D4AF37]">dashboard</span>
						</div>
						<div>
							<h2 class="premium-title !text-xl">Job Bag Dashboard</h2>
							<p class="text-[10px] text-gray-400 uppercase tracking-widest font-black">Shop Floor Operations</p>
						</div>
					</div>
					<!-- Navigation Buttons -->
					<div class="flex items-center gap-2 bg-gray-100 dark:bg-warm-dark-800 p-1 rounded-lg">
						<button 
							@click="$router.push('/special-orders')"
							class="px-4 py-1.5 text-sm font-bold rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
						>
							Order Intake
						</button>
						<button 
							@click="$router.push('/special-orders/job-bag')"
							class="px-4 py-1.5 text-sm font-bold rounded-md bg-white dark:bg-warm-dark-700 text-gray-900 dark:text-white shadow-sm"
						>
							Job Bag Dashboard
						</button>
					</div>
				</div>
			</div>

			<!-- We need to ensure JobBagShopFloor takes full height of the remaining space -->
			<JobBagShopFloor class="flex-1" />
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
import JobBagShopFloor from '@/components/special-order/JobBagShopFloor.vue'
</script>
