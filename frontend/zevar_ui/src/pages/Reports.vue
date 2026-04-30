<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
	router.replace('/reports')
})
</script>

<template>
	<div class="flex items-center justify-center h-full">
		<div
			class="animate-spin rounded-full h-7 w-7 border-2 border-gray-300 border-t-[#D4AF37]"
		></div>
	</div>
</template>
