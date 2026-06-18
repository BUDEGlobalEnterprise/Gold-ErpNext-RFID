<template>
	<div class="text-center py-8 px-4 flex flex-col items-center justify-center h-full">
		<span class="material-symbols-outlined !text-3xl text-red-400 dark:text-red-500 mb-2">error</span>
		<p class="text-xs text-gray-600 dark:text-gray-400 mb-4">{{ message }}</p>
		<button @click="$emit('retry')" class="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs font-medium rounded-lg transition-colors">
			Retry
		</button>
	</div>
</template>

<script setup>
defineProps({
	message: { type: String, default: 'Unable to load data — please refresh' }
})
defineEmits(['retry'])
</script>
