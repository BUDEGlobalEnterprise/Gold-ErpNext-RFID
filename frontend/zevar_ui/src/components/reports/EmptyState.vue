<template>
	<div class="text-center py-12 px-4">
		<div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
			<span class="material-symbols-outlined !text-3xl text-gray-300 dark:text-gray-600">bar_chart</span>
		</div>
		<h3 class="text-sm font-bold text-gray-900 dark:text-white mb-1">{{ title }}</h3>
		<p class="text-xs text-gray-400">{{ message }}</p>
	</div>
</template>

<script setup>
defineProps({
	title: { type: String, default: 'No data available' },
	message: { type: String, default: 'Try selecting a different date range' },
})
</script>
