<template>
	<div class="premium-card !p-3 sm:!p-5">
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-3">{{ title }}</h3>
		<div v-if="loading" class="space-y-3">
			<div class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
			<div class="h-4 bg-gray-100 dark:bg-gray-800 rounded animate-pulse w-3/4"></div>
		</div>
		<div v-else-if="data.total_customers > 0" class="space-y-4">
			<!-- Visual bars -->
			<div class="flex h-8 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
				<div
					class="h-full bg-emerald-500 transition-all duration-500"
					:style="{ width: data.new_pct + '%' }"
				></div>
				<div
					class="h-full bg-blue-500 transition-all duration-500"
					:style="{ width: data.returning_pct + '%' }"
				></div>
			</div>
			<!-- Labels -->
			<div class="grid grid-cols-2 gap-4">
				<div class="flex items-center gap-2">
					<div class="w-3 h-3 rounded-full bg-emerald-500"></div>
					<div>
						<p class="text-xs font-bold text-gray-900 dark:text-white">New Customers</p>
						<p class="text-lg font-black text-emerald-600 dark:text-emerald-400">
							{{ data.new_customers }}
							<span class="text-xs font-normal text-gray-400 ml-1">({{ data.new_pct }}%)</span>
						</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					<div class="w-3 h-3 rounded-full bg-blue-500"></div>
					<div>
						<p class="text-xs font-bold text-gray-900 dark:text-white">Returning Customers</p>
						<p class="text-lg font-black text-blue-600 dark:text-blue-400">
							{{ data.returning_customers }}
							<span class="text-xs font-normal text-gray-400 ml-1">({{ data.returning_pct }}%)</span>
						</p>
					</div>
				</div>
			</div>
		</div>
		<p v-else class="text-xs text-gray-400 text-center py-8">No customer data</p>
	</div>
</template>

<script setup>
defineProps({
	data: { type: Object, default: () => ({}) },
	title: { type: String, default: 'Customer Mix (New vs Returning)' },
	loading: { type: Boolean, default: false },
})
</script>
