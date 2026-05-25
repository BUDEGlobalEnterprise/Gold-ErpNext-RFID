<template>
	<AppLayout>
		<div class="flex flex-col h-full">
			<div class="flex items-center gap-3 mb-4 flex-shrink-0 flex-wrap">
				<div class="w-10 h-10 rounded-xl flex items-center justify-center bg-cyan-500/10">
					<span class="material-symbols-outlined !text-xl text-cyan-500">groups</span>
				</div>
				<div>
					<h2 class="premium-title !text-xl">Workforce Intelligence</h2>
					<p class="text-[10px] text-gray-400">Employee performance and scheduling analytics</p>
				</div>
			</div>
			<div class="flex-1 flex items-center justify-center">
				<div class="text-center">
					<span class="material-symbols-outlined !text-4xl text-gray-300 mb-2 block">construction</span>
					<p class="text-sm text-gray-400">Workforce Intelligence coming soon</p>
				</div>
			</div>
		</div>
	</AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
</script>
