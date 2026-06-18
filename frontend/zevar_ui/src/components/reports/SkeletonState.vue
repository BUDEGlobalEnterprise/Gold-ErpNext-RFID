<template>
	<div class="w-full h-full min-h-[150px] bg-gray-50 dark:bg-gray-800/50 rounded-xl animate-pulse flex flex-col justify-end p-4 gap-2">
		<div class="flex items-end justify-between w-full h-full gap-2">
			<div
				v-for="i in lines"
				:key="i"
				class="bg-gray-200 dark:bg-gray-700 rounded w-full"
				:style="{ height: `${20 + ((i * 37) % 60)}%` }"
			></div>
		</div>
	</div>
</template>

<script setup>
defineProps({
	lines: { type: Number, default: 6 },
})
</script>
